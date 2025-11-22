"""Password reset or recovery request lifecycle helper."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from typing import Mapping

from .utils import datetime_to_iso, parse_datetime


class ResetStatus(StrEnum):
    PENDING = "pending"
    DELIVERED = "delivered"
    COMPLETED = "completed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class ResetChannel(StrEnum):
    CONSOLE = "console"
    SECURE_NOTE = "secure_note"
    CLI = "cli"


class ResetOriginSurface(StrEnum):
    GUI = "gui"
    CLI = "cli"
    SERVICE = "service"


@dataclass(slots=True)
class ResetRequest:
    request_id: str
    user_id: str
    initiated_by: str
    dispatcher_channel: ResetChannel
    expires_at: datetime
    status: ResetStatus = ResetStatus.PENDING
    reason: str | None = None
    origin_surface: ResetOriginSurface = ResetOriginSurface.GUI
    temporary_secret: bytes | None = None
    secret_nonce: bytes | None = None
    secret_displayed_at: datetime | None = None
    created_at: datetime | None = None
    completed_at: datetime | None = None
    justification: str | None = None

    @classmethod
    def from_row(cls, row: Mapping[str, object]) -> "ResetRequest":
        return cls(
            request_id=row["request_id"],
            user_id=row["user_id"],
            initiated_by=row["initiated_by"],
            dispatcher_channel=ResetChannel(row["dispatcher_channel"]),
            expires_at=parse_datetime(row.get("expires_at"))
            or datetime.now(timezone.utc),
            status=ResetStatus(row.get("status", ResetStatus.PENDING)),
            reason=row.get("reason"),
            origin_surface=ResetOriginSurface(row.get("origin_surface", "gui")),
            temporary_secret=row.get("temporary_secret"),
            secret_nonce=row.get("secret_nonce"),
            secret_displayed_at=parse_datetime(row.get("secret_displayed_at")),
            created_at=parse_datetime(row.get("created_at")),
            completed_at=parse_datetime(row.get("completed_at")),
            justification=row.get("justification"),
        )

    def to_record(self) -> dict[str, object | None]:
        return {
            "request_id": self.request_id,
            "user_id": self.user_id,
            "initiated_by": self.initiated_by,
            "dispatcher_channel": self.dispatcher_channel.value,
            "status": self.status.value,
            "reason": self.reason,
            "origin_surface": self.origin_surface.value,
            "temporary_secret": self.temporary_secret,
            "secret_nonce": self.secret_nonce,
            "secret_displayed_at": datetime_to_iso(self.secret_displayed_at),
            "expires_at": datetime_to_iso(self.expires_at),
            "created_at": datetime_to_iso(self.created_at),
            "completed_at": datetime_to_iso(self.completed_at),
            "justification": self.justification,
        }

    def issue_secret(
        self,
        *,
        secret: bytes,
        nonce: bytes,
        expires_at: datetime | None = None,
    ) -> None:
        self.temporary_secret = secret
        self.secret_nonce = nonce
        self.secret_displayed_at = None
        self.status = ResetStatus.PENDING
        if expires_at is not None:
            self.expires_at = expires_at

    def mark_secret_delivered(
        self,
        *,
        timestamp: datetime | None = None,
    ) -> None:
        self.status = ResetStatus.DELIVERED
        self.secret_displayed_at = timestamp or datetime.now(timezone.utc)

    def mark_completed(self) -> None:
        self.status = ResetStatus.COMPLETED
        self.completed_at = datetime.now(timezone.utc)
        self.clear_secret()

    def clear_secret(self) -> None:
        self.temporary_secret = None
        self.secret_nonce = None
        self.secret_displayed_at = None

    def has_expired(self, *, as_of: datetime | None = None) -> bool:
        return (as_of or datetime.now(timezone.utc)) >= self.expires_at

    def cancel(self, *, reason: str | None = None) -> None:
        self.status = ResetStatus.CANCELLED
        self.reason = reason
        self.clear_secret()

    def mark_expired(self) -> None:
        self.status = ResetStatus.EXPIRED
        self.clear_secret()

    def secret_available(self) -> bool:
        return self.temporary_secret is not None and self.secret_nonce is not None


__all__ = [
    "ResetChannel",
    "ResetOriginSurface",
    "ResetRequest",
    "ResetStatus",
]
