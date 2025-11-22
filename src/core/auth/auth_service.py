"""High-level authentication orchestration for RFU."""

from __future__ import annotations

import os
import secrets
import string
from typing import Optional

from src.core.auth.exceptions import AccountBlockedError, AuthenticationError
from src.core.auth.models import (
    AccountStatus,
    AuthSession,
    UserAccount,
    UserRole,
)
from src.core.auth.policies import InputValidator, LockoutPolicy
from src.core.auth.security import PasswordHasher
from src.core.auth.user_store import UserStore
from src.log_manager import get_log_manager

_DEFAULT_BOOTSTRAP_PASSWORD = "ChangeMeNow!2025"


class AuthService:
    """Authenticate RFU users with account lockout and auditing."""

    MAX_LOGIN_ATTEMPTS = 5

    def __init__(
        self,
        *,
        store: Optional[UserStore] = None,
        password_hasher: Optional[PasswordHasher] = None,
        input_validator: Optional[InputValidator] = None,
        lockout_policy: Optional[LockoutPolicy] = None,
    ) -> None:
        self.store = store or UserStore()
        self.password_hasher = password_hasher or PasswordHasher()
        self._validator = input_validator or InputValidator()
        self._lockout_policy = lockout_policy or LockoutPolicy(
            max_attempts=self.MAX_LOGIN_ATTEMPTS,
        )
        self.logger = get_log_manager().get_logger("AuthService")
        self._ensure_bootstrap_admin()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def authenticate(
        self,
        username: str,
        password: str,
        *,
        surface: str = "gui",
    ) -> AuthSession:
        if not isinstance(username, str) or not isinstance(password, str):
            raise AuthenticationError("Username and password are required")

        (
            sanitized_username,
            normalized_password,
        ) = self._validator.validate_credentials(
            username,
            password,
        )

        account = self.store.get_user(sanitized_username)
        if not account:
            self.logger.warning(
                "Login failed: unknown user '%s'",
                sanitized_username,
            )
            raise AuthenticationError("Invalid username or password")

        if account.is_blocked:
            self.logger.warning(
                "Login rejected: blocked account '%s'",
                sanitized_username,
            )
            raise AccountBlockedError(
                "Account is blocked; contact an administrator",
            )

        status_value = self._status_value(account.account_status)

        if status_value in {"pending", AccountStatus.PENDING.value}:
            self.logger.warning(
                "Login rejected: pending account '%s'",
                sanitized_username,
            )
            raise AuthenticationError(
                "Account pending administrator approval",
            )

        if status_value == AccountStatus.DISABLED.value:
            self.logger.warning(
                "Login rejected: disabled account '%s'",
                sanitized_username,
            )
            raise AuthenticationError(
                "Account disabled; contact an administrator",
            )

        if not self.password_hasher.verify(
            account.password_hash,
            normalized_password,
        ):
            decision = self._lockout_policy.register_failure(account)
            blocked = self.store.record_login_failure(
                sanitized_username,
                max_attempts=self.MAX_LOGIN_ATTEMPTS,
                origin_surface=surface,
            )
            blocked = blocked or decision.blocked
            if decision.should_alert and not blocked:
                self.logger.warning(
                    "Multiple failed logins for %s (%s/%s)",
                    sanitized_username,
                    decision.attempts,
                    decision.max_attempts,
                )
            if blocked:
                self.logger.error(
                    "Account '%s' blocked after %s failures",
                    sanitized_username,
                    decision.max_attempts,
                )
                self._lockout_policy.reset_history(account.username)
                raise AccountBlockedError(
                    "Account blocked after too many failed attempts",
                )
            raise AuthenticationError("Invalid username or password")

        self.store.record_login_success(
            sanitized_username,
            origin_surface=surface,
        )
        self._lockout_policy.register_success(account)
        account.reset_required = False
        self.logger.info("User '%s' authenticated", sanitized_username)
        return AuthSession(
            username=sanitized_username,
            role=self._role_value(account.role),
            preferences_user_id=account.preferences_user_id,
            reset_required=account.reset_required,
        )

    def create_user(
        self,
        *,
        username: str,
        password: str,
        role: str = "user",
        preferences_user_id: Optional[str] = None,
        actor: str = "system",
        require_reset: bool = False,
    ) -> None:
        password_hash = self.password_hasher.hash(password)
        self.store.create_user(
            username=username,
            password_hash=password_hash,
            role=role,
            preferences_user_id=preferences_user_id,
            reset_required=require_reset,
        )
        self.logger.info("User '%s' created by %s", username, actor)

    def reset_password(
        self,
        *,
        username: str,
        actor: str,
        temporary_password: Optional[str] = None,
    ) -> str:
        self._require_account(username)
        temp_password = temporary_password or self._generate_temporary_password()
        password_hash = self.password_hasher.hash(temp_password)
        self.store.update_password(
            username=username,
            password_hash=password_hash,
            reset_required=False,
            actor=actor,
        )
        self.logger.warning(
            "User '%s' password reset by %s; reset_required=False",
            username,
            actor,
        )
        return temp_password

    def unblock_account(self, *, username: str, actor: str) -> None:
        self._require_account(username)
        self.store.unblock(username, actor=actor)
        self.logger.info("Account '%s' unblocked by %s", username, actor)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _generate_temporary_password(self, length: int = 16) -> str:
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*()_-+="
        return "".join(secrets.choice(alphabet) for _ in range(length))

    def _require_account(self, username: str) -> UserAccount:
        account = self.store.get_user(username)
        if not account:
            raise AuthenticationError(f"Unknown user '{username}'")
        return account

    @staticmethod
    def _status_value(status: str | AccountStatus) -> str:
        return status.value if isinstance(status, AccountStatus) else str(status)

    @staticmethod
    def _role_value(role: str | UserRole) -> str:
        return role.value if isinstance(role, UserRole) else str(role)

    def _ensure_bootstrap_admin(self) -> None:
        if self.store.has_any_user():
            return
        bootstrap_password = os.getenv(
            "RFU_BOOTSTRAP_ADMIN_PASSWORD",
            _DEFAULT_BOOTSTRAP_PASSWORD,
        )
        password_hash = self.password_hasher.hash(bootstrap_password)
        self.store.create_user(
            username="rfu-admin",
            password_hash=password_hash,
            role="admin",
            preferences_user_id="rfu-admin",
            reset_required=True,
        )
        self.logger.warning(
            "Bootstrap admin user 'rfu-admin' created. "
            "Change the password immediately.",
        )


__all__ = ["AuthService"]
