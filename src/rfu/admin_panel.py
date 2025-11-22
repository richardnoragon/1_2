"""Admin panel guard helpers shared between GUI flows and tests."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

from src.core.auth.endpoints.admin_users_controller import AdminUsersController
from src.core.auth.policies import InputValidator
from src.log_manager import get_log_manager

LOGGER = get_log_manager().get_logger("RFU.AdminPanel")


def _extract_session_mapping(
    session: Mapping[str, Any] | Dict[str, Any],
) -> Mapping[str, Any]:
    if isinstance(session, dict):
        return session
    return dict(session)


def _extract_role(session: Mapping[str, Any]) -> str | None:
    role = session.get("role")
    if not role and isinstance(session.get("session"), Mapping):
        nested = session["session"]
        role = nested.get("role")  # type: ignore[index]
    return str(role).lower() if role else None


def _extract_username(session: Mapping[str, Any]) -> str | None:
    username = session.get("username")
    if not username and isinstance(session.get("session"), Mapping):
        nested = session["session"]
        username = nested.get("username")  # type: ignore[index]
    return str(username) if username else None


def guard_admin_panel_access(*, session: Mapping[str, Any] | Dict[str, Any]) -> None:
    """Raise when the provided session does not represent an admin user."""

    mapping = _extract_session_mapping(session)
    role = _extract_role(mapping)
    if role == "admin":
        return
    username = _extract_username(mapping) or "unknown"
    LOGGER.warning(
        "Admin panel access denied for user %s with role=%s",
        username,
        role or "missing",
    )
    raise PermissionError("Administrator role required to open the admin panel")


@dataclass(frozen=True)
class ResetSecretEnvelope:
    """Container describing the outcome of a reset request."""

    temporary_password: Optional[str]
    delivery: str
    justification: str
    revealed: bool


@dataclass
class AdminPanelActions:
    """High-level helpers that back the GUI admin management panel."""

    controller: AdminUsersController
    database_path: Path
    session_username: str | None = None
    validator: InputValidator = field(default_factory=InputValidator)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.database_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON;")
        return conn

    def list_pending_users(self, limit: int = 25) -> list[Dict[str, Any]]:
        return self.controller.workflow.list_pending_users(limit=limit)

    def recent_audit_entries(self, limit: int = 50) -> list[Dict[str, Any]]:
        return self.controller.workflow.export_audit_entries(limit=limit)

    def approve_pending_user(
        self,
        *,
        username: str,
        role: str = "standard",
        template: str = "default",
    ) -> Dict[str, Any]:
        sanitized = self.validator.validate_username(username)
        payload = {
            "username": sanitized,
            "approve": True,
            "role": role,
            "preferences_template": template,
            "token_role": "admin",
            "token_username": self.session_username,
        }
        result = self.controller.post_user(payload)
        LOGGER.info("Admin panel approved %s (role=%s)", sanitized, role)
        return result

    def reset_user_password(
        self,
        *,
        username: str,
        delivery: str = "console",
        justification: str,
        reveal_secret: bool = False,
    ) -> ResetSecretEnvelope:
        sanitized = self.validator.validate_username(username)
        justification_value = (justification or "").strip()
        if not justification_value:
            raise ValueError("justification is required")

        payload = self.controller.patch_user(
            {
                "action": "reset_password",
                "username": sanitized,
                "dispatcher_channel": delivery,
                "reason": justification_value,
                "token_role": "admin",
                "token_username": self.session_username,
            }
        )
        temporary_password = payload.get("temporary_password")
        return ResetSecretEnvelope(
            temporary_password=temporary_password if reveal_secret else None,
            delivery=delivery,
            justification=justification_value,
            revealed=reveal_secret,
        )

    def unblock_user(
        self,
        *,
        username: str,
        justification: str,
    ) -> Dict[str, Any]:
        sanitized = self.validator.validate_username(username)
        justification_value = (justification or "").strip()
        if not justification_value:
            raise ValueError("justification is required")
        payload = self.controller.patch_user(
            {
                "action": "unblock",
                "username": sanitized,
                "reason": justification_value,
                "token_role": "admin",
                "token_username": self.session_username,
            }
        )
        LOGGER.info("Admin panel unblocked %s", sanitized)
        return payload

    def share_preferences_state(self, username: str) -> Dict[str, Any]:
        sanitized = self.validator.validate_username(username)
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT username,
                       share_preferences,
                       preferences_id
                FROM user_accounts
                WHERE username = ?
                LIMIT 1
                """,
                (sanitized,),
            ).fetchone()
            if row is None:
                raise ValueError(
                    f"User {sanitized!r} does not exist for preference view"
                )
            return {
                "username": row["username"],
                "share_preferences": bool(row["share_preferences"]),
                "preferences_id": row["preferences_id"],
            }


@dataclass(frozen=True)
class AdminPanelContext:
    session_username: str | None
    deeplink_target: str | None
    controller: AdminUsersController
    actions: AdminPanelActions


def open_admin_panel(
    *,
    session: Mapping[str, Any] | Dict[str, Any],
    database_path: str | Path,
    deeplink_target: str | None = None,
) -> AdminPanelContext:
    """Return a launch context with helpers after enforcing admin gate."""

    guard_admin_panel_access(session=session)
    controller = AdminUsersController(db_path=database_path)
    username = _extract_username(_extract_session_mapping(session))
    LOGGER.info(
        "Admin panel opened by %s (deeplink=%s)",
        username or "unknown",
        deeplink_target,
    )
    actions = AdminPanelActions(
        controller=controller,
        database_path=Path(database_path),
        session_username=username,
    )
    return AdminPanelContext(
        session_username=username,
        deeplink_target=deeplink_target,
        controller=controller,
        actions=actions,
    )


__all__ = [
    "AdminPanelActions",
    "AdminPanelContext",
    "ResetSecretEnvelope",
    "guard_admin_panel_access",
    "open_admin_panel",
]
