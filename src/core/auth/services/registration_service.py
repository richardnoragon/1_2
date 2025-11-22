"""Self-registration service for RFU identity flows."""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Mapping

from src.core.auth.models.admin_action_audit import AdminActionType
from src.core.auth.policies import InputValidator
from src.core.auth.security import PasswordHasher
from src.core.auth.services.audit_logger import AuditLogger
from src.log_manager import get_log_manager

LOGGER = get_log_manager().get_logger("Auth.RegistrationService")

_ALLOWED_CHANNELS = frozenset({"gui", "cli", "hub", "bootstrap"})
_RESPONSE_MESSAGE = (
    "Registration received. Your account will remain pending until an "
    "administrator approves it."
)


NotificationHook = Callable[[Dict[str, Any]], None]


class RegistrationService:
    """Handle FR-009 self-registration workflow."""

    def __init__(
        self,
        *,
        database_path: str | Path,
        validator: InputValidator | None = None,
        origin_surface: str = "service",
        notification_hooks: Iterable[NotificationHook] | None = None,
        audit_logger: AuditLogger | None = None,
    ) -> None:
        self.database_path = Path(database_path)
        self.validator = validator or InputValidator()
        self.password_hasher = PasswordHasher()
        self.origin_surface = (
            origin_surface if origin_surface in {"gui", "cli", "service"} else "service"
        )
        self.notification_hooks: tuple[NotificationHook, ...] = tuple(
            notification_hooks or ()
        )
        self._audit_logger = audit_logger or AuditLogger(
            database_path=self.database_path,
            default_surface=self.origin_surface,
        )

    # ------------------------------------------------------------------
    def register_user(
        self,
        *,
        username: str,
        password: str,
        channel: str = "gui",
        metadata: Mapping[str, Any] | None = None,
    ) -> Dict[str, Any]:
        sanitized_username = self.validator.validate_username(username)
        normalized_password = self.validator.validate_password(password)
        normalized_channel = self._normalize_channel(channel)
        metadata_payload = self._prepare_metadata(metadata, normalized_channel)
        password_hash, password_salt = self.password_hasher.hash_with_salt(
            normalized_password
        )
        submitted_at = self._utc_now_iso()

        with self._connect() as conn:
            if self._user_exists(conn, sanitized_username):
                raise ValueError(
                    "Username already exists. If you previously registered, "
                    "please wait for administrator approval."
                )
            self._insert_user(
                conn,
                username=sanitized_username,
                password_hash=password_hash,
                password_salt=password_salt,
                channel=normalized_channel,
                metadata_json=json.dumps(metadata_payload, sort_keys=True),
                submitted_at=submitted_at,
            )
            conn.commit()
        self._record_audit_entry(
            username=sanitized_username,
            channel=normalized_channel,
            metadata=metadata_payload,
            submitted_at=submitted_at,
        )

        result = {
            "username": sanitized_username,
            "status": "pending",
            "requires_approval": True,
            "channel": normalized_channel,
            "message": _RESPONSE_MESSAGE,
            "submitted_at": submitted_at,
        }
        LOGGER.info(
            "Self-registration queued for %s via %s channel",
            sanitized_username,
            normalized_channel,
        )
        self._notify_hooks(
            {
                **result,
                "metadata": metadata_payload,
                "database_path": str(self.database_path),
                "origin_surface": self.origin_surface,
            }
        )
        return result

    # ------------------------------------------------------------------
    def _connect(self) -> sqlite3.Connection:
        if not self.database_path.exists():
            raise FileNotFoundError(
                f"Identity database not found at {self.database_path}"
            )
        conn = sqlite3.connect(self.database_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON;")
        return conn

    @staticmethod
    def _utc_now_iso() -> str:
        timestamp = datetime.now(timezone.utc).replace(
            microsecond=0,
            tzinfo=None,
        )
        return timestamp.isoformat()

    @staticmethod
    def _normalize_channel(raw_channel: str | None) -> str:
        candidate = (raw_channel or "gui").strip().lower()
        if candidate not in _ALLOWED_CHANNELS:
            raise ValueError("surface/channel must be one of gui, cli, hub, bootstrap")
        return candidate

    @staticmethod
    def _prepare_metadata(
        metadata: Mapping[str, Any] | None,
        channel: str,
    ) -> Dict[str, Any]:
        if metadata is None:
            payload: Dict[str, Any] = {}
        elif isinstance(metadata, Mapping):
            payload = dict(metadata)
        else:
            raise ValueError("registration metadata must be a mapping when provided")
        payload.setdefault("surface", channel)
        return payload

    @staticmethod
    def _user_exists(conn: sqlite3.Connection, username: str) -> bool:
        row = conn.execute(
            "SELECT 1 FROM user_accounts WHERE username = ? LIMIT 1",
            (username,),
        ).fetchone()
        return bool(row)

    def _insert_user(
        self,
        conn: sqlite3.Connection,
        *,
        username: str,
        password_hash: str,
        password_salt: bytes,
        channel: str,
        metadata_json: str,
        submitted_at: str,
    ) -> None:
        conn.execute(
            """
            INSERT INTO user_accounts (
                username,
                password_hash,
                password_salt,
                role,
                account_status,
                is_blocked,
                login_attempts,
                last_login,
                last_failed_login,
                preferences_id,
                share_preferences,
                registration_channel,
                registration_metadata,
                created_at,
                activated_at,
                blocked_at,
                updated_at,
                enforced_password_change
            ) VALUES (
                ?, ?, ?, 'standard', 'pending', 0, 0,
                NULL, NULL, NULL, 0, ?, ?, ?, NULL, NULL, ?, 0
            )
            """,
            (
                username,
                password_hash,
                sqlite3.Binary(password_salt),
                channel,
                metadata_json,
                submitted_at,
                submitted_at,
            ),
        )

    def _record_audit_entry(
        self,
        *,
        username: str,
        channel: str,
        metadata: Mapping[str, Any],
        submitted_at: str,
    ) -> None:
        audit_details: Dict[str, Any] = {
            "event": "self_registration",
            "status": "pending",
            "channel": channel,
            "metadata": metadata,
            "submitted_at": submitted_at,
        }
        metadata_payload = {"requires_approval": True}
        correlation_id = self._build_correlation_id(
            username=username,
            submitted_at=submitted_at,
        )
        self._audit_logger.record_action(
            action_type=AdminActionType.SELF_REGISTRATION,
            actor_username=username,
            target_username=username,
            details=audit_details,
            origin_surface=self.origin_surface,
            metadata=metadata_payload,
            occurred_at=submitted_at,
            correlation_id=correlation_id,
        )

    def _notify_hooks(self, payload: Mapping[str, Any]) -> None:
        if not self.notification_hooks:
            return
        for hook in self.notification_hooks:
            try:
                hook(dict(payload))
            except Exception as exc:  # pragma: no cover - defensive
                LOGGER.warning(
                    "Registration notification hook failed: %s",
                    exc,
                )

    @staticmethod
    def _build_correlation_id(
        *,
        username: str,
        submitted_at: str,
    ) -> str:
        token = uuid.uuid4().hex[:10]
        safe_user = username.replace(" ", "-")
        compact_time = submitted_at.replace(":", "").replace("-", "")
        return f"registration-{safe_user}-{compact_time}-{token}"


__all__ = ["RegistrationService"]
