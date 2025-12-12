"""Data model for administrator notifications.

AdminNotification represents a notification queued for delivery to
administrators, typically for security-sensitive events such as
break-glass login usage, lockout alerts, and rotation requirements.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping


class NotificationType(Enum):
    """Types of administrator notifications."""

    BREAK_GLASS_USAGE = "break_glass_usage"
    SECURITY_INCIDENT = "security_incident"
    LOCKOUT_ALERT = "lockout_alert"
    ROTATION_REQUIRED = "rotation_required"
    SYSTEM_ALERT = "system_alert"

    @classmethod
    def coerce(cls, value: str | "NotificationType") -> "NotificationType":
        """Convert string to NotificationType with fallback."""
        if isinstance(value, cls):
            return value
        try:
            return cls(value.lower())
        except ValueError:
            return cls.SYSTEM_ALERT


@dataclass(slots=True)
class AdminNotification:
    """A notification queued for administrator attention.

    Attributes:
        notification_id: Unique identifier for this notification.
        notification_type: Category of the notification.
        subject: Brief subject line for the notification.
        body: Detailed notification body text.
        metadata: Additional structured data as JSON.
        acknowledged: Whether an admin has acknowledged this.
        acknowledged_by: Username of the acknowledging admin.
        acknowledged_at: When the notification was acknowledged.
        created_at: When the notification was created.
        expires_at: When the notification should be auto-archived.
    """

    notification_id: int | None = None
    notification_type: NotificationType = NotificationType.SYSTEM_ALERT
    subject: str = ""
    body: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    acknowledged: bool = False
    acknowledged_by: str | None = None
    acknowledged_at: datetime | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime | None = None

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> "AdminNotification":
        """Construct from database row."""
        metadata_raw = row.get("metadata") or "{}"
        try:
            metadata = json.loads(metadata_raw)
        except (json.JSONDecodeError, TypeError):
            metadata = {}

        created_at_raw = row.get("created_at")
        if isinstance(created_at_raw, datetime):
            created_at = created_at_raw
        elif isinstance(created_at_raw, str):
            try:
                created_at = datetime.fromisoformat(
                    created_at_raw.replace("Z", "+00:00")
                )
            except ValueError:
                created_at = datetime.now(timezone.utc)
        else:
            created_at = datetime.now(timezone.utc)

        expires_at_raw = row.get("expires_at")
        expires_at = None
        if isinstance(expires_at_raw, datetime):
            expires_at = expires_at_raw
        elif isinstance(expires_at_raw, str):
            try:
                expires_at = datetime.fromisoformat(
                    expires_at_raw.replace("Z", "+00:00")
                )
            except ValueError:
                pass

        acked_at_raw = row.get("acknowledged_at")
        acked_at = None
        if isinstance(acked_at_raw, datetime):
            acked_at = acked_at_raw
        elif isinstance(acked_at_raw, str):
            try:
                acked_at = datetime.fromisoformat(acked_at_raw.replace("Z", "+00:00"))
            except ValueError:
                pass

        return cls(
            notification_id=row.get("id"),
            notification_type=NotificationType.coerce(
                row.get("notification_type", "system_alert")
            ),
            subject=row.get("subject") or "",
            body=row.get("body") or "",
            metadata=metadata,
            acknowledged=bool(row.get("acknowledged")),
            acknowledged_by=row.get("acknowledged_by"),
            acknowledged_at=acked_at,
            created_at=created_at,
            expires_at=expires_at,
        )

    def to_row(self) -> dict[str, Any]:
        """Convert to database row dict."""
        created_iso = self.created_at.isoformat().replace("+00:00", "Z")
        expires_iso = (
            self.expires_at.isoformat().replace("+00:00", "Z")
            if self.expires_at
            else None
        )
        acked_iso = (
            self.acknowledged_at.isoformat().replace("+00:00", "Z")
            if self.acknowledged_at
            else None
        )
        return {
            "id": self.notification_id,
            "notification_type": self.notification_type.value,
            "subject": self.subject,
            "body": self.body,
            "metadata": json.dumps(self.metadata, sort_keys=True),
            "acknowledged": 1 if self.acknowledged else 0,
            "acknowledged_by": self.acknowledged_by,
            "acknowledged_at": acked_iso,
            "created_at": created_iso,
            "expires_at": expires_iso,
        }

    @property
    def is_break_glass_alert(self) -> bool:
        """True if this is a break-glass usage notification."""
        return self.notification_type == NotificationType.BREAK_GLASS_USAGE

    @property
    def is_security_alert(self) -> bool:
        """True if this is a security-related notification."""
        return self.notification_type in (
            NotificationType.BREAK_GLASS_USAGE,
            NotificationType.SECURITY_INCIDENT,
            NotificationType.LOCKOUT_ALERT,
        )

    @property
    def requires_acknowledgment(self) -> bool:
        """True if this notification requires manual acknowledgment."""
        return self.is_security_alert and not self.acknowledged

    def acknowledge(self, admin_username: str) -> None:
        """Mark this notification as acknowledged."""
        self.acknowledged = True
        self.acknowledged_by = admin_username
        self.acknowledged_at = datetime.now(timezone.utc)


__all__ = ["AdminNotification", "NotificationType"]
