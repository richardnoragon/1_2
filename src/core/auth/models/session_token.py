"""Session token helper for active authentication sessions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import StrEnum
from typing import Any, Dict, Mapping

from .utils import bool_from_db, datetime_to_iso, parse_datetime


class SessionSurface(StrEnum):
    GUI = "gui"
    CLI = "cli"

    @classmethod
    def coerce(cls, value: Any) -> "SessionSurface":
        try:
            if isinstance(value, SessionSurface):
                return value
            return cls(str(value))
        except (ValueError, TypeError):
            return cls.GUI


@dataclass(slots=True)
class SessionToken:
    session_handle_hash: str
    user_id: str
    issued_at: datetime
    last_activity_at: datetime
    expires_at: datetime
    surface: SessionSurface = SessionSurface.GUI
    origin_host: str | None = None
    revoked: bool = False
    revoked_at: datetime | None = None
    preferences_id: str | None = None
    idle_timeout_deadline: datetime | None = None
    session_type: str = "normal"  # 'normal', 'break_glass'
    usage_log_id: int | None = None  # FK to break_glass_usage_log.id

    @property
    def is_break_glass(self) -> bool:
        """True if this is a break-glass emergency session."""
        return self.session_type == "break_glass"

    @property
    def break_glass_session_id(self) -> str | None:
        """Alias for usage_log_id as string for API compatibility."""
        return str(self.usage_log_id) if self.usage_log_id else None

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> "SessionToken":
        issued = parse_datetime(row.get("issued_at")) or datetime.now(timezone.utc)
        last_activity = parse_datetime(row.get("last_activity_at")) or issued
        expires = parse_datetime(row.get("expires_at")) or issued
        return cls(
            session_handle_hash=row["session_handle_hash"],
            user_id=row["user_id"],
            issued_at=issued,
            last_activity_at=last_activity,
            expires_at=expires,
            surface=SessionSurface.coerce(row.get("surface")),
            origin_host=row.get("origin_host"),
            revoked=bool_from_db(row.get("revoked")),
            revoked_at=parse_datetime(row.get("revoked_at")),
            preferences_id=row.get("preferences_id"),
            idle_timeout_deadline=parse_datetime(row.get("idle_timeout_deadline")),
            session_type=row.get("session_type", "normal"),
            usage_log_id=row.get("usage_log_id"),
        )

    def is_active(self, *, as_of: datetime | None = None) -> bool:
        moment = as_of or datetime.now(timezone.utc)
        if self.revoked or moment > self.expires_at:
            return False
        if self.idle_timeout_deadline and moment > self.idle_timeout_deadline:
            return False
        return True

    def is_idle(self, *, as_of: datetime | None = None) -> bool:
        """Return True when the session exceeded its idle deadline."""

        if not self.idle_timeout_deadline:
            return False
        moment = as_of or datetime.now(timezone.utc)
        return moment > self.idle_timeout_deadline

    def mark_revoked(
        self,
        *,
        timestamp: datetime | None = None,
    ) -> None:
        self.revoked = True
        self.revoked_at = timestamp or datetime.now(timezone.utc)

    def touch(
        self,
        *,
        activity_time: datetime | None = None,
        idle_deadline: datetime | None = None,
    ) -> None:
        self.last_activity_at = activity_time or datetime.now(timezone.utc)
        if idle_deadline is not None:
            self.idle_timeout_deadline = idle_deadline

    def set_idle_timeout(
        self,
        *,
        duration: timedelta,
        reference: datetime | None = None,
    ) -> None:
        """Advance the idle timeout deadline from the supplied reference."""

        base = reference or datetime.now(timezone.utc)
        self.idle_timeout_deadline = base + duration

    def extend_expiration(
        self,
        *,
        new_expires_at: datetime | None = None,
        delta: timedelta | None = None,
    ) -> None:
        """Extend the expiration time either to a new value or by a delta."""

        if new_expires_at is not None:
            self.expires_at = new_expires_at
            return
        if delta is not None:
            self.expires_at = self.expires_at + delta

    def seconds_until_expiration(
        self,
        *,
        as_of: datetime | None = None,
    ) -> int:
        moment = as_of or datetime.now(timezone.utc)
        remaining = (self.expires_at - moment).total_seconds()
        return int(remaining) if remaining > 0 else 0

    def to_record(self) -> Dict[str, Any]:
        return {
            "session_handle_hash": self.session_handle_hash,
            "user_id": self.user_id,
            "issued_at": datetime_to_iso(self.issued_at),
            "last_activity_at": datetime_to_iso(self.last_activity_at),
            "expires_at": datetime_to_iso(self.expires_at),
            "surface": self.surface.value,
            "origin_host": self.origin_host,
            "revoked": int(self.revoked),
            "revoked_at": datetime_to_iso(self.revoked_at),
            "preferences_id": self.preferences_id,
            "idle_timeout_deadline": datetime_to_iso(self.idle_timeout_deadline),
            "session_type": self.session_type,
            "usage_log_id": self.usage_log_id,
        }


__all__ = ["SessionToken", "SessionSurface"]
