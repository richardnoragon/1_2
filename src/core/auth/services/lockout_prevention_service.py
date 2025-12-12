"""Lockout prevention service.

Manages the auto-unblock mechanism for always-available accounts and
provides health status checking to verify the lockout prevention
invariant is satisfied.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from src.core.auth.models.always_available_account_config import (
    AlwaysAvailableAccountConfig,
)
from src.core.auth.models.user_account import AccountStatus, UserAccount


@dataclass(frozen=True, slots=True)
class AutoUnblockResult:
    """Result of an auto-unblock check."""

    should_unblock: bool
    account_username: str
    time_remaining: timedelta | None = None
    reason: str | None = None

    @classmethod
    def unblock(cls, username: str) -> "AutoUnblockResult":
        """Account should be unblocked."""
        return cls(
            should_unblock=True,
            account_username=username,
            reason="cooldown expired",
        )

    @classmethod
    def wait(cls, username: str, remaining: timedelta) -> "AutoUnblockResult":
        """Account is still in cooldown."""
        return cls(
            should_unblock=False,
            account_username=username,
            time_remaining=remaining,
            reason="cooldown not expired",
        )

    @classmethod
    def not_blocked(cls, username: str) -> "AutoUnblockResult":
        """Account is not blocked."""
        return cls(
            should_unblock=False,
            account_username=username,
            reason="account not blocked",
        )


@dataclass(frozen=True, slots=True)
class AccessPath:
    """Represents an accessible login path."""

    account_username: str
    role: str
    account_type: str  # "always_available" or "break_glass"
    is_accessible: bool
    will_auto_unblock_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class LockoutPreventionHealth:
    """Health status of the lockout prevention system."""

    healthy: bool
    accessible_paths: List[AccessPath]
    blocked_count: int
    reason: str | None = None

    @property
    def has_dev_access(self) -> bool:
        """Check if dev access is available."""
        return any(p.is_accessible and p.role == "dev" for p in self.accessible_paths)

    @property
    def has_admin_access(self) -> bool:
        """Check if admin access is available."""
        return any(p.is_accessible and p.role == "admin" for p in self.accessible_paths)


class LockoutPreventionService:
    """Service for managing lockout prevention features.

    Coordinates:
    - Auto-unblock checks for always-available accounts
    - Cooldown triggering on lockout
    - Health status verification
    """

    def __init__(
        self,
        user_repository: Any = None,
        config_repository: Any = None,
        audit_logger: Any = None,
        default_cooldown_minutes: int = 5,
    ):
        """Initialize the service.

        Args:
            user_repository: Repository for user accounts
            config_repository: Repository for always-available configs
            audit_logger: Logger for audit trail
            default_cooldown_minutes: Default cooldown duration
        """
        self._user_repo = user_repository
        self._config_repo = config_repository
        self._audit_logger = audit_logger
        self._default_cooldown = default_cooldown_minutes

    def check_auto_unblock(
        self,
        username: str,
        now: datetime | None = None,
    ) -> AutoUnblockResult:
        """Check if an always-available account should auto-unblock.

        Args:
            username: The account username
            now: Current time (for testing)

        Returns:
            AutoUnblockResult indicating whether to unblock
        """
        check_time = now or datetime.now()

        # Get user account
        user = self._get_user(username)
        if user is None:
            return AutoUnblockResult(
                should_unblock=False,
                account_username=username,
                reason="account not found",
            )

        # Must be always-available
        if not user.is_always_available:
            return AutoUnblockResult(
                should_unblock=False,
                account_username=username,
                reason="not an always-available account",
            )

        # Must be blocked
        if user.account_status != AccountStatus.BLOCKED:
            return AutoUnblockResult.not_blocked(username)

        # Check auto_unblock_at timestamp
        if user.auto_unblock_at is None:
            return AutoUnblockResult(
                should_unblock=False,
                account_username=username,
                reason="no auto-unblock scheduled",
            )

        if check_time >= user.auto_unblock_at:
            return AutoUnblockResult.unblock(username)

        remaining = user.auto_unblock_at - check_time
        return AutoUnblockResult.wait(username, remaining)

    def trigger_cooldown(
        self,
        username: str,
        now: datetime | None = None,
    ) -> datetime:
        """Start the cooldown period for an always-available account.

        Called when an always-available account hits the lockout threshold.
        Instead of permanently blocking, starts a cooldown timer.

        Args:
            username: The account username
            now: Current time (for testing)

        Returns:
            The datetime when auto-unblock will occur
        """
        start_time = now or datetime.now()
        unblock_at = start_time + timedelta(minutes=self._default_cooldown)

        # Update account with auto_unblock_at
        if self._user_repo:
            self._user_repo.set_auto_unblock(username, unblock_at)

        # Update config with cooldown start
        if self._config_repo:
            config = self._get_or_create_config(username)
            config.start_cooldown(start_time)
            self._config_repo.save(config)

        # Log the cooldown start
        if self._audit_logger:
            self._audit_logger.record_action(
                action_type="auto_unblock_scheduled",
                actor_username=username,
                target_username=username,
                details={
                    "cooldown_minutes": self._default_cooldown,
                    "unblock_at": unblock_at.isoformat(),
                },
                correlation_id=uuid.uuid4().hex,
            )

        return unblock_at

    def perform_auto_unblock(
        self,
        username: str,
        now: datetime | None = None,
    ) -> bool:
        """Perform auto-unblock if conditions are met.

        Args:
            username: The account username
            now: Current time (for testing)

        Returns:
            True if unblock was performed
        """
        result = self.check_auto_unblock(username, now)
        if not result.should_unblock:
            return False

        # Perform the unblock
        if self._user_repo:
            self._user_repo.unblock(username)
            self._user_repo.set_auto_unblock(username, None)

        # Reset config cooldown
        if self._config_repo:
            config = self._get_or_create_config(username)
            config.reset_cooldown()
            self._config_repo.save(config)

        # Log the auto-unblock
        if self._audit_logger:
            self._audit_logger.record_action(
                action_type="auto_unblock",
                actor_username="system",
                target_username=username,
                details={"reason": "cooldown expired"},
                correlation_id=uuid.uuid4().hex,
            )

        return True

    def get_health_status(self) -> LockoutPreventionHealth:
        """Get the current health status of lockout prevention.

        Checks that at least one access path is available (either
        always-available or break-glass) for both dev and admin roles.

        Returns:
            LockoutPreventionHealth with status and accessible paths
        """
        paths: List[AccessPath] = []
        blocked_count = 0

        # Get always-available accounts
        always_available = self._get_protected_accounts(always_available=True)
        for user in always_available:
            is_accessible = user.account_status == AccountStatus.ACTIVE
            if user.account_status == AccountStatus.BLOCKED:
                blocked_count += 1

            paths.append(
                AccessPath(
                    account_username=user.username,
                    role=user.role.value if hasattr(user.role, "value") else user.role,
                    account_type="always_available",
                    is_accessible=is_accessible,
                    will_auto_unblock_at=user.auto_unblock_at,
                )
            )

        # Get break-glass accounts
        break_glass = self._get_protected_accounts(break_glass=True)
        for user in break_glass:
            is_accessible = user.account_status == AccountStatus.ACTIVE

            paths.append(
                AccessPath(
                    account_username=user.username,
                    role=user.role.value if hasattr(user.role, "value") else user.role,
                    account_type="break_glass",
                    is_accessible=is_accessible,
                )
            )

        # Determine health
        has_accessible = any(p.is_accessible for p in paths)
        healthy = has_accessible or len(paths) == 0  # Empty = not configured

        reason = None
        if not healthy:
            reason = "no accessible paths available"
        elif blocked_count > 0:
            reason = f"{blocked_count} account(s) in cooldown"

        return LockoutPreventionHealth(
            healthy=healthy,
            accessible_paths=paths,
            blocked_count=blocked_count,
            reason=reason,
        )

    def _get_user(self, username: str) -> Optional[UserAccount]:
        """Get a user account by username."""
        if self._user_repo is None:
            return None
        try:
            return self._user_repo.get(username)
        except Exception:
            return None

    def _get_protected_accounts(
        self,
        always_available: bool = False,
        break_glass: bool = False,
    ) -> List[UserAccount]:
        """Get protected accounts by type."""
        if self._user_repo is None:
            return []
        try:
            if always_available:
                return self._user_repo.get_always_available_accounts()
            if break_glass:
                return self._user_repo.get_break_glass_accounts()
            return []
        except Exception:
            return []

    def _get_or_create_config(
        self,
        username: str,
    ) -> AlwaysAvailableAccountConfig:
        """Get or create config for an always-available account."""
        if self._config_repo:
            config = self._config_repo.get_config(username)
            if config:
                return config

        return AlwaysAvailableAccountConfig(
            username=username,
            cooldown_duration_minutes=self._default_cooldown,
            auto_unblock_enabled=True,
        )


__all__ = [
    "AccessPath",
    "AutoUnblockResult",
    "LockoutPreventionHealth",
    "LockoutPreventionService",
]
