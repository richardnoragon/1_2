"""Lockout policy engine enforcing FR-011 attempt thresholds.

Supports always-available accounts with cooldown-based auto-unblock
instead of permanent blocking (per 007-upgrade-to-login spec).

T052: Enhanced to optionally integrate with LockoutPreventionService
for coordinated cooldown triggering.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Callable, Deque, Dict, Optional, Protocol

from src.core.auth.models import AccountStatus, UserAccount

if TYPE_CHECKING:
    from src.core.auth.services.lockout_prevention_service import (
        LockoutPreventionService,
    )


class LockoutPreventionServiceProtocol(Protocol):
    """Protocol for lockout prevention service integration."""

    def trigger_cooldown(
        self, username: str, now: Optional[datetime] = None
    ) -> datetime:
        """Trigger cooldown for an always-available account."""
        ...


@dataclass(slots=True)
class LockoutDecision:
    """Outcome of evaluating a login attempt against the policy."""

    attempts: int
    max_attempts: int
    blocked: bool
    blocked_at: datetime | None
    status: AccountStatus
    should_alert: bool
    reason: str
    auto_unblock_at: datetime | None = None
    is_cooldown: bool = False
    cooldown_triggered: bool = False  # T052: Track if service was called


class LockoutPolicy:
    """Track login attempts and determine when to block or alert.

    For always-available accounts, uses cooldown-based temporary blocking
    instead of permanent lockout.

    T052: Optionally integrates with LockoutPreventionService to persist
    cooldown state when an always-available account is blocked.
    """

    # Default cooldown for always-available accounts (5 minutes)
    DEFAULT_COOLDOWN_MINUTES = 5

    def __init__(
        self,
        *,
        max_attempts: int = 5,
        alert_threshold: int = 3,
        alert_window: timedelta | None = timedelta(minutes=5),
        cooldown_minutes: int = DEFAULT_COOLDOWN_MINUTES,
        clock: Callable[[], datetime] | None = None,
        lockout_prevention_service: Optional[
            "LockoutPreventionService | LockoutPreventionServiceProtocol"
        ] = None,
    ) -> None:
        if max_attempts <= 0:
            raise ValueError("max_attempts must be positive")
        if alert_threshold <= 0:
            raise ValueError("alert_threshold must be positive")
        self._max_attempts = max_attempts
        self._alert_threshold = min(alert_threshold, max_attempts)
        self._alert_window = alert_window
        self._cooldown_minutes = cooldown_minutes
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._history: Dict[str, Deque[datetime]] = {}
        # T052: Optional service integration for persisting cooldown state
        self._lockout_prevention_service = lockout_prevention_service

    # ------------------------------------------------------------------
    def register_failure(
        self,
        account: UserAccount,
        *,
        occurred_at: datetime | None = None,
    ) -> LockoutDecision:
        """Register a failed login attempt and determine lockout status.

        For always-available accounts, triggers cooldown instead of
        permanent block (T052).

        Args:
            account: The user account that failed login
            occurred_at: Time of failure (defaults to now)

        Returns:
            LockoutDecision with updated status and cooldown info
        """
        moment = occurred_at or self._clock()
        attempts = account.login_attempts + 1
        blocked = attempts >= self._max_attempts
        blocked_at = moment if blocked else None
        status = AccountStatus.BLOCKED if blocked else account.account_status

        # Handle always-available accounts with cooldown (T052)
        auto_unblock_at = None
        is_cooldown = False
        cooldown_triggered = False

        if blocked and account.is_always_available:
            is_cooldown = True
            # Calculate auto_unblock_at
            cooldown_delta = timedelta(minutes=self._cooldown_minutes)
            auto_unblock_at = moment + cooldown_delta

            # T052: Call LockoutPreventionService.trigger_cooldown() if available
            if self._lockout_prevention_service is not None:
                try:
                    # Service may return a different unblock time based on config
                    service_unblock_at = (
                        self._lockout_prevention_service.trigger_cooldown(
                            account.username, now=moment
                        )
                    )
                    if service_unblock_at is not None:
                        auto_unblock_at = service_unblock_at
                    cooldown_triggered = True
                except Exception:
                    # Log error but continue - policy can still return decision
                    # Caller should handle service persistence separately
                    pass

        history = self._history.setdefault(account.username, deque())
        history.append(moment)
        self._prune_history(history, moment)
        should_alert = len(history) >= self._alert_threshold

        # Set appropriate reason
        if blocked:
            reason = "cooldown" if is_cooldown else "max_attempts"
        else:
            reason = "increment"

        return LockoutDecision(
            attempts=attempts,
            max_attempts=self._max_attempts,
            blocked=blocked,
            blocked_at=blocked_at,
            status=status,
            should_alert=should_alert,
            reason=reason,
            auto_unblock_at=auto_unblock_at,
            is_cooldown=is_cooldown,
            cooldown_triggered=cooldown_triggered,
        )

    def register_success(self, account: UserAccount) -> LockoutDecision:
        """Register a successful login, resetting lockout state."""
        self._history.pop(account.username, None)
        return LockoutDecision(
            attempts=0,
            max_attempts=self._max_attempts,
            blocked=False,
            blocked_at=None,
            status=AccountStatus.ACTIVE,
            should_alert=False,
            reason="reset",
            cooldown_triggered=False,
        )

    def check_auto_unblock(
        self,
        account: UserAccount,
        *,
        check_time: datetime | None = None,
    ) -> LockoutDecision | None:
        """Check if an always-available account should auto-unblock.

        Args:
            account: The user account to check
            check_time: Time to check against (defaults to now)

        Returns:
            LockoutDecision with unblock info, or None if not applicable
        """
        if not account.is_always_available:
            return None
        if account.account_status != AccountStatus.BLOCKED:
            return None
        if account.auto_unblock_at is None:
            return None

        moment = check_time or self._clock()

        if moment >= account.auto_unblock_at:
            # Cooldown expired - should unblock
            self._history.pop(account.username, None)
            return LockoutDecision(
                attempts=0,
                max_attempts=self._max_attempts,
                blocked=False,
                blocked_at=None,
                status=AccountStatus.ACTIVE,
                should_alert=False,
                reason="auto_unblock",
                auto_unblock_at=None,
                is_cooldown=False,
                cooldown_triggered=False,
            )
        else:
            # Still in cooldown
            return LockoutDecision(
                attempts=account.login_attempts,
                max_attempts=self._max_attempts,
                blocked=True,
                blocked_at=account.blocked_at,
                status=AccountStatus.BLOCKED,
                should_alert=False,
                reason="cooldown_active",
                auto_unblock_at=account.auto_unblock_at,
                is_cooldown=True,
                cooldown_triggered=False,
            )

    def reset_history(self, username: str) -> None:
        self._history.pop(username, None)

    @property
    def cooldown_minutes(self) -> int:
        """Return the configured cooldown duration in minutes."""
        return self._cooldown_minutes

    # ------------------------------------------------------------------
    def _prune_history(
        self,
        history: Deque[datetime],
        moment: datetime,
    ) -> None:
        if not self._alert_window:
            return
        cutoff = moment - self._alert_window
        while history and history[0] < cutoff:
            history.popleft()


__all__ = ["LockoutDecision", "LockoutPolicy"]
