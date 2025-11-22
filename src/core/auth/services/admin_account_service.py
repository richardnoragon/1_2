"""Admin account maintenance workflows (reset + unblock)."""

from __future__ import annotations

import secrets
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict

from src.core.auth.models import AccountStatus, UserAccount, UserRole
from src.core.auth.models.admin_action_audit import AdminActionType
from src.core.auth.models.reset_request import (
    ResetChannel,
    ResetOriginSurface,
    ResetRequest,
    ResetStatus,
)
from src.core.auth.policies import InputValidator
from src.core.auth.repositories.admin_action_audit_repository import (
    AdminActionAuditRepository,
)
from src.core.auth.repositories.reset_request_repository import (
    ResetRequestRepository,
)
from src.core.auth.repositories.session_store import SessionStore
from src.core.auth.repositories.user_account_repository import (
    UserAccountRepository,
)
from src.core.auth.security import PasswordHasher
from src.core.auth.services.audit_logger import AuditLogger
from src.log_manager import get_log_manager

LOGGER = get_log_manager().get_logger("Auth.AdminAccountService")
DEFAULT_RESET_DELIVERY_CHANNELS = frozenset({"console", "secure_note", "cli"})
_RESET_EXPIRATION_MINUTES = 30


@dataclass(slots=True)
class ResetResult:
    username: str
    delivery: str
    enforced_password_change: bool
    reset_request_id: str
    temporary_password: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "username": self.username,
            "delivery": self.delivery,
            "enforced_password_change": self.enforced_password_change,
            "reset_request_id": self.reset_request_id,
            "temporary_password": self.temporary_password,
        }


@dataclass(slots=True)
class UnblockResult:
    username: str
    account_status: str
    justification: str
    login_attempts: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "username": self.username,
            "account_status": self.account_status,
            "justification": self.justification,
            "login_attempts": self.login_attempts,
        }


class AdminAccountService:
    """Reset passwords and unblock accounts with role enforcement."""

    def __init__(
        self,
        *,
        database_path: str | Path | None = None,
        user_repo: UserAccountRepository | None = None,
        session_store: SessionStore | None = None,
        reset_repo: ResetRequestRepository | None = None,
        audit_repo: AdminActionAuditRepository | None = None,
        audit_logger: AuditLogger | None = None,
        validator: InputValidator | None = None,
        password_hasher: PasswordHasher | None = None,
        origin_surface: str = "cli",
        default_actor: str = "rfu-admin",
    ) -> None:
        db_path = Path(database_path) if database_path else None
        self._user_repo = user_repo or UserAccountRepository(
            database_path=db_path,
        )
        self._session_store = session_store or SessionStore(
            database_path=db_path,
        )
        self._reset_repo = reset_repo or ResetRequestRepository(
            database_path=db_path,
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
        self._hasher = password_hasher or PasswordHasher()
        self._origin_surface = origin_surface
        self._default_actor = default_actor

    # ------------------------------------------------------------------
    def reset_password(
        self,
        *,
        username: str,
        delivery: str,
        justification: str,
        actor_username: str | None = None,
    ) -> Dict[str, Any]:
        justification_value = self._require_justification(justification)
        normalized_delivery = self._normalize_delivery(delivery)
        sanitized_username = self._validator.validate_username(username)
        actor = self._resolve_actor(actor_username)
        self._assert_actor_is_admin(actor)

        account = self._require_account(sanitized_username)
        temp_password = PasswordHasher.generate_temporary_password(length=14)
        password_hash, password_salt = self._hasher.hash_with_salt(
            temp_password,
        )
        now = datetime.now(timezone.utc)
        self._update_account_password(
            account,
            password_hash=password_hash,
            password_salt=password_salt,
            timestamp=now,
        )
        self._session_store.revoke_for_user(sanitized_username, timestamp=now)
        request_id = self._record_reset_request(
            username=sanitized_username,
            actor_username=actor,
            delivery=normalized_delivery,
            justification=justification_value,
            temporary_secret=temp_password,
            issued_at=now,
        )
        self._log_action(
            action_type=AdminActionType.RESET_PASSWORD,
            actor_username=actor,
            target_username=sanitized_username,
            details={
                "delivery": normalized_delivery,
                "justification": justification_value,
                "reset_request_id": request_id,
            },
            correlation_id=request_id,
        )
        self._reset_repo.mark_delivered(request_id, delivered_at=now)
        LOGGER.warning(
            "Password for %s reset via %s (actor=%s, request=%s)",
            sanitized_username,
            normalized_delivery,
            actor,
            request_id,
        )
        result = ResetResult(
            username=sanitized_username,
            delivery=normalized_delivery,
            enforced_password_change=True,
            reset_request_id=request_id,
            temporary_password=temp_password,
        )
        return result.to_dict()

    def unblock_user(
        self,
        *,
        username: str,
        justification: str,
        actor_username: str | None = None,
    ) -> Dict[str, Any]:
        justification_value = self._require_justification(justification)
        sanitized_username = self._validator.validate_username(username)
        actor = self._resolve_actor(actor_username)
        self._assert_actor_is_admin(actor)
        account = self._require_account(sanitized_username)
        previous_status = account.account_status
        previous_attempts = account.login_attempts
        was_blocked = account.is_blocked
        now = datetime.now(timezone.utc)
        self._reset_block_state(account, timestamp=now)
        self._session_store.revoke_for_user(sanitized_username, timestamp=now)
        correlation_id = self._generate_correlation_id(
            "unblock", identifier=sanitized_username
        )
        self._log_action(
            action_type=AdminActionType.UNBLOCK_USER,
            actor_username=actor,
            target_username=sanitized_username,
            details={
                "justification": justification_value,
                "previous_status": previous_status.value,
                "previous_attempts": previous_attempts,
                "was_blocked": was_blocked,
            },
            correlation_id=correlation_id,
        )
        LOGGER.info(
            "User %s unblocked via admin workflow (actor=%s)",
            sanitized_username,
            actor,
        )
        result = UnblockResult(
            username=sanitized_username,
            account_status=account.account_status.value,
            justification=justification_value,
            login_attempts=account.login_attempts,
        )
        return result.to_dict()

    # ------------------------------------------------------------------
    def _require_account(self, username: str) -> UserAccount:
        account = self._user_repo.get(username)
        if account is None:
            raise ValueError(f"User '{username}' not found")
        return account

    def _require_justification(self, justification: str | None) -> str:
        value = (justification or "").strip()
        if not value:
            raise ValueError("justification is required")
        return value

    def _normalize_delivery(self, delivery: str | None) -> str:
        candidate = (delivery or "console").strip().lower()
        if candidate not in DEFAULT_RESET_DELIVERY_CHANNELS:
            allowed = ", ".join(sorted(DEFAULT_RESET_DELIVERY_CHANNELS))
            raise ValueError(f"delivery must be one of {allowed}")
        return candidate

    def _resolve_actor(self, actor_username: str | None) -> str:
        return actor_username or self._default_actor

    def _assert_actor_is_admin(self, actor_username: str) -> None:
        actor_account = self._user_repo.get(actor_username)
        if not actor_account or actor_account.role != UserRole.ADMIN:
            raise PermissionError(
                "Administrator role required for this action",
            )

    def _update_account_password(
        self,
        account: UserAccount,
        *,
        password_hash: str,
        password_salt: bytes,
        timestamp: datetime,
    ) -> None:
        account.password_hash = password_hash
        account.password_salt = password_salt
        account.reset_required = True
        account.is_blocked = False
        account.login_attempts = 0
        account.blocked_at = None
        if account.account_status in {
            AccountStatus.PENDING,
            AccountStatus.BLOCKED,
        }:
            account.account_status = AccountStatus.ACTIVE
        account.updated_at = timestamp
        self._user_repo.upsert(account)

    def _reset_block_state(
        self,
        account: UserAccount,
        *,
        timestamp: datetime,
    ) -> None:
        account.login_attempts = 0
        account.is_blocked = False
        account.blocked_at = None
        if account.account_status != AccountStatus.DISABLED:
            account.account_status = AccountStatus.ACTIVE
        account.updated_at = timestamp
        self._user_repo.upsert(account)

    def _record_reset_request(
        self,
        *,
        username: str,
        actor_username: str,
        delivery: str,
        justification: str,
        temporary_secret: str,
        issued_at: datetime,
    ) -> str:
        expires_at = issued_at + timedelta(minutes=_RESET_EXPIRATION_MINUTES)
        request = ResetRequest(
            request_id=uuid.uuid4().hex,
            user_id=username,
            initiated_by=actor_username,
            dispatcher_channel=ResetChannel(delivery),
            expires_at=expires_at,
            status=ResetStatus.PENDING,
            reason=justification,
            origin_surface=ResetOriginSurface(self._origin_surface),
            temporary_secret=temporary_secret.encode("utf-8"),
            secret_nonce=secrets.token_bytes(16),
            created_at=issued_at,
            justification=justification,
        )
        self._reset_repo.create(request)
        return request.request_id

    @staticmethod
    def _generate_correlation_id(
        prefix: str,
        *,
        identifier: str | None = None,
    ) -> str:
        token = uuid.uuid4().hex[:12]
        if identifier:
            return f"{prefix}-{identifier}-{token}"
        return f"{prefix}-{token}"

    def _log_action(
        self,
        *,
        action_type: AdminActionType,
        actor_username: str,
        target_username: str,
        details: Dict[str, Any],
        correlation_id: str,
    ) -> None:
        self._audit_logger.record_action(
            action_type=action_type,
            actor_username=actor_username,
            target_username=target_username,
            details=details,
            origin_surface=self._origin_surface,
            correlation_id=correlation_id,
        )


__all__ = [
    "AdminAccountService",
    "DEFAULT_RESET_DELIVERY_CHANNELS",
    "ResetResult",
    "UnblockResult",
]
