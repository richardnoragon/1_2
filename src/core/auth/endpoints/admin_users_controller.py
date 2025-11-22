"""Controller for `/admin/users` contract coverage."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from src.core.auth.workflows.admin_actions import (
    DEFAULT_RESET_DELIVERY_CHANNELS,
    AdminIdentityActions,
)
from src.log_manager import get_log_manager

LOGGER = get_log_manager().get_logger("AdminUsersController")


class AdminUsersController:
    """Expose POST/PATCH helpers with explicit role guards."""

    def __init__(self, *, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.workflow = AdminIdentityActions(
            database_path=self.db_path,
            origin_surface="gui",
        )

    # ------------------------------------------------------------------
    def post_user(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        self._require_admin_role(payload, attempted_action="approve_user")
        username = payload.get("username")
        approve_flag = payload.get("approve")
        role = payload.get("role", "standard")
        template = payload.get("preferences_template", "default")
        actor_username = payload.get("token_username")
        if not approve_flag:
            raise ValueError("approve flag is required for POST /admin/users")
        if not isinstance(username, str) or not username:
            raise ValueError("username is required")

        LOGGER.info(
            "Admin approval requested for %s (role=%s)",
            username,
            role,
        )
        return self.workflow.approve_user(
            username=username,
            role=role,
            preferences_template=template,
            actor_username=actor_username,
        )

    def patch_user(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        self._require_admin_role(payload, attempted_action="patch_user")
        action = (payload.get("action") or "").lower()
        username = payload.get("username")
        if not isinstance(username, str) or not username:
            raise ValueError("username is required")

        actor_username = payload.get("token_username")
        justification = payload.get("reason")

        if action == "reset_password":
            delivery = payload.get("dispatcher_channel", "console")
            if delivery not in DEFAULT_RESET_DELIVERY_CHANNELS:
                raise ValueError(
                    "dispatcher_channel must be one of "
                    f"{sorted(DEFAULT_RESET_DELIVERY_CHANNELS)}"
                )
            LOGGER.warning(
                "Admin reset requested for %s via %s",
                username,
                delivery,
            )
            return self.workflow.reset_password(
                username=username,
                delivery=delivery,
                justification=justification or "",
                actor_username=actor_username,
            )

        if action == "unblock":
            LOGGER.info("Admin unblock requested for %s", username)
            return self.workflow.unblock_user(
                username=username,
                justification=justification or "",
                actor_username=actor_username,
            )

        raise ValueError("Unsupported admin action")

    # ------------------------------------------------------------------
    def _require_admin_role(
        self,
        payload: Dict[str, Any],
        *,
        attempted_action: str,
    ) -> None:
        token_role = payload.get("token_role")
        if token_role is None:
            return
        role = str(token_role).lower()
        if role == "admin":
            return
        actor_username = payload.get("token_username")
        self.workflow.log_unauthorized_attempt(
            actor_username=actor_username,
            target_username=payload.get("username"),
            attempted_action=attempted_action,
        )
        raise PermissionError("Administrator role required for this action")


__all__ = ["AdminUsersController"]
