"""Always-available account configuration model.

Tracks cooldown state and auto-unblock settings for protected accounts
that should never be permanently locked out.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Mapping

from src.core.auth.models.utils import parse_datetime


@dataclass(slots=True)
class AlwaysAvailableAccountConfig:
    """Configuration for an always-available protected account."""

    username: str
    last_cooldown_start: datetime | None = None
    cooldown_duration_minutes: int = 5
    auto_unblock_enabled: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> "AlwaysAvailableAccountConfig":
        """Create from database row."""
        return cls(
            username=row["username"],
            last_cooldown_start=parse_datetime(row.get("last_cooldown_start")),
            cooldown_duration_minutes=int(row.get("cooldown_duration_minutes") or 5),
            auto_unblock_enabled=bool(row.get("auto_unblock_enabled", 1)),
            created_at=parse_datetime(row.get("created_at")),
            updated_at=parse_datetime(row.get("updated_at")),
        )

    def to_record(self) -> dict[str, Any]:
        """Convert to database record."""
        return {
            "username": self.username,
            "last_cooldown_start": (
                self.last_cooldown_start.isoformat()
                if self.last_cooldown_start
                else None
            ),
            "cooldown_duration_minutes": self.cooldown_duration_minutes,
            "auto_unblock_enabled": int(self.auto_unblock_enabled),
            "created_at": (self.created_at.isoformat() if self.created_at else None),
            "updated_at": (self.updated_at.isoformat() if self.updated_at else None),
        }

    @property
    def cooldown_expires_at(self) -> datetime | None:
        """Calculate when the cooldown period expires."""
        if self.last_cooldown_start is None:
            return None
        return self.last_cooldown_start + timedelta(
            minutes=self.cooldown_duration_minutes
        )

    def should_auto_unblock(self, now: datetime | None = None) -> bool:
        """Check if the account should be automatically unblocked.

        Returns True if:
        - Auto-unblock is enabled
        - Cooldown has started
        - Cooldown period has expired
        """
        if not self.auto_unblock_enabled:
            return False
        if self.last_cooldown_start is None:
            return False

        check_time = now or datetime.now()
        expires_at = self.cooldown_expires_at
        return expires_at is not None and check_time >= expires_at

    def time_until_unblock(self, now: datetime | None = None) -> timedelta | None:
        """Return time remaining until auto-unblock, or None if not in cooldown."""
        if self.last_cooldown_start is None:
            return None

        check_time = now or datetime.now()
        expires_at = self.cooldown_expires_at
        if expires_at is None:
            return None

        remaining = expires_at - check_time
        return remaining if remaining.total_seconds() > 0 else timedelta(0)

    def start_cooldown(self, now: datetime | None = None) -> None:
        """Start the cooldown timer."""
        self.last_cooldown_start = now or datetime.now()
        self.updated_at = datetime.now()

    def reset_cooldown(self) -> None:
        """Clear the cooldown state after successful unblock."""
        self.last_cooldown_start = None
        self.updated_at = datetime.now()


__all__ = ["AlwaysAvailableAccountConfig"]
