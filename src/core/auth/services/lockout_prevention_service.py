"""Lockout prevention service for always-available accounts."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:  # pragma: no cover
    from src.core.auth.repositories.user_account_repository import (
        UserAccountRepository,
    )

_COOLDOWN_MINUTES = 15


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------
@dataclass
class CheckResult:
    """Result from ``check_auto_unblock``."""

    account_username: str
    should_unblock: bool
    reason: str
    time_remaining: Optional[timedelta] = None


@dataclass
class AccessiblePath:
    """Describes one always-available/break-glass access path."""

    account_username: str
    role: str
    account_type: str
    is_accessible: bool
    will_auto_unblock_at: Optional[str] = None


@dataclass
class HealthStatus:
    """Result from ``get_health_status``."""

    healthy: bool
    reason: str = ""
    has_dev_access: bool = False
    has_admin_access: bool = False
    blocked_count: int = 0
    accessible_paths: List[AccessiblePath] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------
class LockoutPreventionService:
    """Manage cooldown-based auto-unblocking of always-available accounts."""

    COOLDOWN_MINUTES: int = _COOLDOWN_MINUTES

    def __init__(self, *, user_repository: "UserAccountRepository") -> None:
        self._repo = user_repository

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def check_auto_unblock(self, *, username: str) -> CheckResult:
        """Check whether *username* should be auto-unblocked.

        The account must be ``is_always_available=True``.  If it is
        currently blocked and ``auto_unblock_at`` is in the past (or
        unset), the caller should perform the unblock.
        """
        account = self._repo.get(username)
        if account is None:
            return CheckResult(
                account_username=username,
                should_unblock=False,
                reason="Account not found.",
            )

        if not account.is_always_available:
            return CheckResult(
                account_username=username,
                should_unblock=False,
                reason="Account is not always-available.",
            )

        if not account.is_blocked:
            return CheckResult(
                account_username=username,
                should_unblock=False,
                reason="Account is not blocked; no action needed.",
            )

        now = datetime.now(timezone.utc)

        if account.auto_unblock_at is None:
            # Blocked but no cooldown set — unblock immediately.
            return CheckResult(
                account_username=username,
                should_unblock=True,
                reason="Account is blocked with no cooldown scheduled.",
            )

        unblock_at = account.auto_unblock_at
        # Ensure timezone-aware comparison.
        if unblock_at.tzinfo is None:
            unblock_at = unblock_at.replace(tzinfo=timezone.utc)

        if now >= unblock_at:
            return CheckResult(
                account_username=username,
                should_unblock=True,
                reason="Cooldown period has elapsed; ready to unblock.",
            )

        time_remaining = unblock_at - now
        minutes_left = int(time_remaining.total_seconds() // 60) + 1
        return CheckResult(
            account_username=username,
            should_unblock=False,
            reason=f"Cooldown active — approximately {minutes_left} minute(s) remaining.",
            time_remaining=time_remaining,
        )

    def perform_auto_unblock(self, *, username: str) -> None:
        """Unblock an always-available account and clear its cooldown."""
        account = self._repo.get(username)
        if account is None or not account.is_always_available:
            return

        from src.core.auth.models.user_account import AccountStatus

        account.is_blocked = False
        account.account_status = AccountStatus.ACTIVE
        account.auto_unblock_at = None
        account.login_attempts = 0
        account.updated_at = datetime.now(timezone.utc)
        self._repo.upsert(account)

    def trigger_cooldown(self, *, username: str) -> datetime:
        """Block an always-available account for ``COOLDOWN_MINUTES``.

        Returns the ``auto_unblock_at`` datetime so callers can store it.
        """
        now = datetime.now(timezone.utc)
        unblock_at = now + timedelta(minutes=self.COOLDOWN_MINUTES)

        account = self._repo.get(username)
        if account is None or not account.is_always_available:
            return unblock_at  # Nothing we can do; return the computed time.

        from src.core.auth.models.user_account import AccountStatus

        account.is_blocked = True
        account.account_status = AccountStatus.BLOCKED
        account.auto_unblock_at = unblock_at
        account.blocked_at = now
        account.updated_at = now
        self._repo.upsert(account)
        return unblock_at

    def get_health_status(self) -> HealthStatus:
        """Return a summary of lockout-prevention health.

        Evaluates all always-available and break-glass accounts to
        determine whether at least one dev path and one admin path are
        currently accessible.
        """
        try:
            always_available = self._repo.get_always_available_accounts()
            break_glass = self._repo.get_break_glass_accounts()
        except Exception:  # pylint: disable=broad-except
            return HealthStatus(
                healthy=False,
                reason="Failed to query protected accounts from repository.",
            )

        now = datetime.now(timezone.utc)
        paths: List[AccessiblePath] = []
        has_dev = False
        has_admin = False
        blocked = 0

        for account in list(always_available) + list(break_glass):
            role_val = (
                account.role.value
                if hasattr(account.role, "value")
                else str(account.role)
            )
            acc_type = "break_glass" if account.is_break_glass else "always_available"

            accessible = not account.is_blocked

            # Always-available accounts may auto-unblock.
            will_unblock: Optional[str] = None
            if (
                account.is_blocked
                and account.is_always_available
                and account.auto_unblock_at
            ):
                unblock_at = account.auto_unblock_at
                if unblock_at.tzinfo is None:
                    unblock_at = unblock_at.replace(tzinfo=timezone.utc)
                if now >= unblock_at:
                    accessible = True  # cooldown has elapsed
                else:
                    will_unblock = unblock_at.isoformat()

            if account.is_blocked:
                blocked += 1

            if accessible:
                if role_val == "dev":
                    has_dev = True
                if role_val in ("admin", "dev"):
                    has_admin = True  # dev >= admin

            paths.append(
                AccessiblePath(
                    account_username=account.username,
                    role=role_val,
                    account_type=acc_type,
                    is_accessible=accessible,
                    will_auto_unblock_at=will_unblock,
                )
            )

        healthy = has_dev or has_admin
        reason = "" if healthy else "No accessible admin/dev path found."

        return HealthStatus(
            healthy=healthy,
            reason=reason,
            has_dev_access=has_dev,
            has_admin_access=has_admin,
            blocked_count=blocked,
            accessible_paths=paths,
        )


__all__ = [
    "AccessiblePath",
    "CheckResult",
    "HealthStatus",
    "LockoutPreventionService",
]
