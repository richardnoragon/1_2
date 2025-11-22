"""Service layer for pending account approvals."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from src.core.auth.models import AccountStatus, UserAccount, UserRole
from src.core.auth.models.admin_action_audit import (
    AdminActionAudit,
    AdminActionSurface,
    AdminActionType,
)
from src.core.auth.policies import InputValidator
from src.core.auth.repositories.admin_action_audit_repository import (
    AdminActionAuditRepository,
)
from src.core.auth.repositories.user_account_repository import UserAccountRepository
from src.core.auth.services.audit_logger import AuditLogger
from src.core.preferences.models import PreferenceProfile, PreferenceSchemaVersion
from src.core.preferences.repositories.preference_profile_repository import (
    PreferenceProfileRepository,
)
from src.log_manager import get_log_manager

LOGGER = get_log_manager().get_logger("Auth.AdminApprovalService")

_DEFAULT_TEMPLATE_PAYLOAD = {
    "layout": "default",
    "favorite_tools": ["file_finder", "size_analyzer"],
    "shortcuts": ["Ctrl+Shift+F"],
}


@dataclass(slots=True)
class ApprovalResult:
    username: str
    role: str
    preferences_id: str
    account_status: str
    template: str
    activated_at: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "username": self.username,
            "role": self.role,
            "preferences_id": self.preferences_id,
            "account_status": self.account_status,
            "preferences_template": self.template,
            "activated_at": self.activated_at,
        }


class AdminApprovalService:
    """Approve pending users while enforcing administrator role requirements."""

    def __init__(
        self,
        *,
        database_path: str | Path | None = None,
        user_repo: UserAccountRepository | None = None,
        preference_repo: PreferenceProfileRepository | None = None,
        audit_repo: AdminActionAuditRepository | None = None,
        audit_logger: AuditLogger | None = None,
        validator: InputValidator | None = None,
        origin_surface: str = "cli",
        default_actor: str = "rfu-admin",
    ) -> None:
        db_path = Path(database_path) if database_path else None
        self._user_repo = user_repo or UserAccountRepository(database_path=db_path)
        self._pref_repo = preference_repo or PreferenceProfileRepository(
            database_path=db_path
        )
        self._audit_repo = audit_repo or AdminActionAuditRepository(
            database_path=db_path
        )
        self._audit_logger = audit_logger or AuditLogger(
            database_path=db_path,
            repository=self._audit_repo,
            default_surface=origin_surface,
        )
        self._validator = validator or InputValidator()
        self._origin_surface = origin_surface
        self._default_actor = default_actor

    # ------------------------------------------------------------------
    def approve_user(
        self,
        *,
        username: str,
        role: str = "standard",
        preferences_template: str = "default",
        actor_username: str | None = None,
    ) -> Dict[str, Any]:
        sanitized_username = self._validator.validate_username(username)
        actor = self._resolve_actor(actor_username, sanitized_username)
        self._assert_actor_is_admin(actor)

        account = self._user_repo.get(sanitized_username)
        if account is None:
            raise ValueError(f"Unknown user '{sanitized_username}'")
        if account.account_status != AccountStatus.PENDING:
            raise ValueError("Only pending accounts can be approved")

        target_role = self._normalize_role(role)
        preferences_id = self._ensure_preferences(
            account,
            template_name=preferences_template,
        )
        activated_at = datetime.now(timezone.utc)
        updated_account = self._user_repo.activate_pending_account(
            username=sanitized_username,
            preferences_id=preferences_id,
            actor_username=actor,
            activated_at=activated_at,
        )
        if updated_account.role != target_role:
            self._user_repo.set_role(sanitized_username, target_role)
        updated_account.role = target_role
        updated_account.account_status = AccountStatus.ACTIVE
        activated_iso = (
            activated_at.replace(microsecond=0).isoformat().replace("+00:00", "Z")
        )
        result = ApprovalResult(
            username=sanitized_username,
            role=target_role.value,
            preferences_id=preferences_id,
            account_status=updated_account.account_status.value,
            template=preferences_template,
            activated_at=activated_iso,
        )
        self._log_approval(
            actor_username=actor,
            target_username=sanitized_username,
            role=target_role.value,
            preferences_id=preferences_id,
            template=preferences_template,
        )
        LOGGER.info(
            "User %s approved (role=%s, actor=%s)",
            sanitized_username,
            target_role.value,
            actor,
        )
        return result.to_dict()

    def list_pending(self, *, limit: int = 25) -> list[UserAccount]:
        return self._user_repo.list_by_status(
            status=AccountStatus.PENDING,
            limit=limit,
        )

    # ------------------------------------------------------------------
    def _resolve_actor(self, actor_username: str | None, target: str) -> str:
        if actor_username:
            return actor_username
        if target == self._default_actor:
            return target
        return self._default_actor

    def _assert_actor_is_admin(self, actor_username: str) -> None:
        account = self._user_repo.get(actor_username)
        if not account or account.role != UserRole.ADMIN:
            raise PermissionError("Administrator role required for this action")

    def _normalize_role(self, role: str | UserRole) -> UserRole:
        try:
            return UserRole(str(role).lower())
        except ValueError:
            raise ValueError("role must be admin, standard, or readonly") from None

    def _ensure_preferences(
        self,
        account: UserAccount,
        *,
        template_name: str,
    ) -> str:
        preferences_id = account.preferences_id or self._generate_preferences_id()
        payload = self._template_payload(template_name)
        profile = PreferenceProfile(
            preferences_id=preferences_id,
            user_id=account.username,
            schema_version=PreferenceSchemaVersion.V1,
            payload=payload,
        )
        self._pref_repo.save(profile)
        return preferences_id

    def _template_payload(self, template_name: str) -> Dict[str, Any]:
        key = (template_name or "default").strip().lower()
        if key == "minimal":
            return {
                "layout": "minimal",
                "favorite_tools": ["file_finder"],
            }
        return dict(_DEFAULT_TEMPLATE_PAYLOAD)

    @staticmethod
    def _generate_preferences_id() -> str:
        return f"pref_{uuid.uuid4().hex[:12]}"

    def _log_approval(
        self,
        *,
        actor_username: str,
        target_username: str,
        role: str,
        preferences_id: str,
        template: str,
    ) -> None:
        details = {
            "role": role,
            "preferences_id": preferences_id,
            "preferences_template": template,
        }
        correlation_id = self._build_correlation_id(
            username=target_username,
            preferences_id=preferences_id,
        )
        self._audit_logger.record_action(
            action_type=AdminActionType.APPROVE_USER,
            actor_username=actor_username,
            target_username=target_username,
            details=details,
            origin_surface=self._origin_surface,
            correlation_id=correlation_id,
        )

    @staticmethod
    def _build_correlation_id(
        *,
        username: str,
        preferences_id: str,
    ) -> str:
        token = uuid.uuid4().hex[:10]
        safe_user = username.replace(" ", "-")
        return f"approval-{safe_user}-{preferences_id}-{token}"


__all__ = ["AdminApprovalService", "ApprovalResult"]
