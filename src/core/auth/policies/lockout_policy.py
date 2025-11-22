"""Lockout policy engine enforcing FR-011 attempt thresholds."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Callable, Deque, Dict

from src.core.auth.models import AccountStatus, UserAccount


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


class LockoutPolicy:
    """Track login attempts and determine when to block or alert."""

    def __init__(
        self,
        *,
        max_attempts: int = 5,
        alert_threshold: int = 3,
        alert_window: timedelta | None = timedelta(minutes=5),
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        if max_attempts <= 0:
            raise ValueError("max_attempts must be positive")
        if alert_threshold <= 0:
            raise ValueError("alert_threshold must be positive")
        self._max_attempts = max_attempts
        self._alert_threshold = min(alert_threshold, max_attempts)
        self._alert_window = alert_window
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._history: Dict[str, Deque[datetime]] = {}

    # ------------------------------------------------------------------
    def register_failure(
        self,
        account: UserAccount,
        *,
        occurred_at: datetime | None = None,
    ) -> LockoutDecision:
        moment = occurred_at or self._clock()
        attempts = account.login_attempts + 1
        blocked = attempts >= self._max_attempts
        blocked_at = moment if blocked else None
        status = AccountStatus.BLOCKED if blocked else account.account_status
        history = self._history.setdefault(account.username, deque())
        history.append(moment)
        self._prune_history(history, moment)
        should_alert = len(history) >= self._alert_threshold
        reason = "max_attempts" if blocked else "increment"
        return LockoutDecision(
            attempts=attempts,
            max_attempts=self._max_attempts,
            blocked=blocked,
            blocked_at=blocked_at,
            status=status,
            should_alert=should_alert,
            reason=reason,
        )

    def register_success(self, account: UserAccount) -> LockoutDecision:
        self._history.pop(account.username, None)
        return LockoutDecision(
            attempts=0,
            max_attempts=self._max_attempts,
            blocked=False,
            blocked_at=None,
            status=AccountStatus.ACTIVE,
            should_alert=False,
            reason="reset",
        )

    def reset_history(self, username: str) -> None:
        self._history.pop(username, None)

    # ------------------------------------------------------------------
    def _prune_history(self, history: Deque[datetime], moment: datetime) -> None:
        if not self._alert_window:
            return
        cutoff = moment - self._alert_window
        while history and history[0] < cutoff:
            history.popleft()


__all__ = ["LockoutDecision", "LockoutPolicy"]
