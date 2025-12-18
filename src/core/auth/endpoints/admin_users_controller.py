"""Controller for `/admin/users` contract coverage.

Task T066: Extended to support:
- Role change endpoint with escalation rules (dev-only for admin promotion)
- Protected account guards (block modification/deletion of protected accounts)
- 403 responses for protected account violations
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Set

from src.core.auth.workflows.admin_actions import (
    DEFAULT_RESET_DELIVERY_CHANNELS,
    AdminIdentityActions,
)
from src.log_manager import get_log_manager

LOGGER = get_log_manager().get_logger("AdminUsersController")

# Protected account usernames that cannot be modified or deleted
PROTECTED_USERNAMES: Set[str] = {
    "rfu_dev_always",
    "rfu_admin_always",
    "rfu_dev_breakglass",
    "rfu_admin_breakglass",
}

# Role hierarchy for escalation checks
ROLE_HIERARCHY: Dict[str, int] = {
    "readonly": 1,
    "user": 2,
    "standard": 2,
    "admin": 3,
    "dev": 4,
}


class AdminUsersController:
    """Expose POST/PATCH helpers with explicit role guards.

    Extended (T066) with:
    - Protected account guards for modification/deletion
    - Role change escalation rules (dev-only for admin promotion)
    - 403 responses for protected account violations
    """

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

        # T066: Check if this is a protected account
        self._check_protected_account(username, action)

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

        if action == "change_role":
            return self._handle_role_change(payload)

        raise ValueError("Unsupported admin action")

    def delete_user(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a user account.

        T066: Protected accounts cannot be deleted.
        Note: This endpoint is prepared for future implementation.
        Currently returns an error as delete_user workflow is not yet
        implemented in AdminIdentityActions.
        """
        self._require_dev_role(payload, attempted_action="delete_user")
        username = payload.get("username")
        if not isinstance(username, str) or not username:
            raise ValueError("username is required")

        # T066: Block deletion of protected accounts
        if username in PROTECTED_USERNAMES:
            LOGGER.warning(
                "Attempted deletion of protected account: %s",
                username,
            )
            raise PermissionError(f"Cannot delete protected account: {username}")

        # TODO: Implement delete_user in AdminIdentityActions workflow
        # For now, this endpoint validates guards but does not delete
        raise NotImplementedError("User deletion not yet implemented in workflow")

    # ------------------------------------------------------------------
    def _handle_role_change(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle role change with escalation rules.

        T066: Dev-only for admin promotion, admin-only for user demotion.
        Note: Role change workflow pending implementation.
        """
        username = payload.get("username")
        new_role = payload.get("new_role", "").lower()
        actor_username = payload.get("token_username")
        actor_role = (payload.get("token_role") or "").lower()
        _ = payload.get("reason", "")  # justification for future use

        if not new_role:
            raise ValueError("new_role is required for role changes")

        if new_role not in ROLE_HIERARCHY:
            raise ValueError(f"Invalid role: {new_role}")

        # T066: Block role changes to protected accounts
        if username in PROTECTED_USERNAMES:
            LOGGER.warning(
                "Attempted role change on protected account: %s",
                username,
            )
            raise PermissionError(
                f"Cannot modify role of protected account: {username}"
            )

        # T066: Check escalation rules
        new_role_level = ROLE_HIERARCHY.get(new_role, 0)
        actor_level = ROLE_HIERARCHY.get(actor_role, 0)

        # Only dev can promote to admin or dev
        if new_role_level >= ROLE_HIERARCHY["admin"]:
            if actor_role != "dev":
                self.workflow.log_unauthorized_attempt(
                    actor_username=actor_username,
                    target_username=username,
                    attempted_action=f"promote_to_{new_role}",
                )
                raise PermissionError(f"Only dev role can promote to {new_role}")

        # Cannot promote above your own level
        if new_role_level > actor_level:
            self.workflow.log_unauthorized_attempt(
                actor_username=actor_username,
                target_username=username,
                attempted_action=f"promote_to_{new_role}",
            )
            raise PermissionError("Cannot promote user above your own role level")

        LOGGER.info(
            "Role change: %s -> %s by %s",
            username,
            new_role,
            actor_username,
        )
        # Role change workflow pending implementation in AdminIdentityActions
        raise NotImplementedError("Role change not yet implemented in workflow")

    def _check_protected_account(
        self,
        username: str,
        action: str,
    ) -> None:
        """Check if action is allowed on protected accounts.

        T066: Protected accounts have restricted modification options.
        """
        if username not in PROTECTED_USERNAMES:
            return

        # These actions are always blocked on protected accounts
        blocked_actions = {"delete", "change_role", "disable"}
        if action in blocked_actions:
            LOGGER.warning(
                "Blocked %s on protected account: %s",
                action,
                username,
            )
            raise PermissionError(
                f"Cannot perform {action} on protected account: {username}"
            )

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
        if role in {"admin", "dev"}:
            return
        actor_username = payload.get("token_username")
        self.workflow.log_unauthorized_attempt(
            actor_username=actor_username,
            target_username=payload.get("username"),
            attempted_action=attempted_action,
        )
        raise PermissionError("Administrator role required for this action")

    def _require_dev_role(
        self,
        payload: Dict[str, Any],
        *,
        attempted_action: str,
    ) -> None:
        """Require dev role for sensitive operations.

        T066: Used for user deletion and other high-privilege operations.
        """
        token_role = payload.get("token_role")
        if token_role is None:
            return
        role = str(token_role).lower()
        if role == "dev":
            return
        actor_username = payload.get("token_username")
        self.workflow.log_unauthorized_attempt(
            actor_username=actor_username,
            target_username=payload.get("username"),
            attempted_action=attempted_action,
        )
        raise PermissionError("Developer role required for this action")


__all__ = ["AdminUsersController"]
