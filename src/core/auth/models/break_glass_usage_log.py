"""Break-glass usage log model.

Tracks emergency access sessions for audit and compliance purposes.
Every break-glass login creates a log entry that persists through
the session lifecycle.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, List, Mapping

from src.core.auth.models.utils import parse_datetime


@dataclass(slots=True)
class ActionEntry:
    """A single action performed during a break-glass session."""

    action_type: str
    description: str = ""
    target: str | None = None
    timestamp: datetime | None = None
    details: dict[str, Any] | None = None

    # Compatibility alias
    @property
    def action(self) -> str:
        """Alias for action_type for compatibility."""
        return self.action_type

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        ts_iso = self.timestamp.isoformat() if self.timestamp else None
        return {
            "action_type": self.action_type,
            "description": self.description,
            "target": self.target,
            "timestamp": ts_iso,
            "details": self.details,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ActionEntry":
        """Create from dictionary."""
        # Support both 'action' and 'action_type' keys
        action_type = data.get("action_type") or data.get("action", "unknown")
        return cls(
            action_type=action_type,
            description=data.get("description", ""),
            target=data.get("target"),
            timestamp=parse_datetime(data.get("timestamp")),
            details=data.get("details"),
        )


@dataclass(slots=True)
class BreakGlassUsageLog:
    """Log entry for a break-glass emergency access session."""

    id: int | None = None
    session_id: str = ""
    account_username: str = ""
    login_timestamp: datetime | None = None
    logout_timestamp: datetime | None = None
    justification: str = ""
    actions_performed: List[ActionEntry] = field(default_factory=list)
    post_usage_rotation_status: str = "not_required"
    client_ip: str | None = None
    client_hostname: str | None = None
    created_at: datetime | None = None

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> "BreakGlassUsageLog":
        """Create from database row."""
        actions_json = row.get("actions_performed", "[]")
        if isinstance(actions_json, str):
            try:
                actions_data = json.loads(actions_json)
            except json.JSONDecodeError:
                actions_data = []
        else:
            actions_data = actions_json or []

        actions = [ActionEntry.from_dict(a) for a in actions_data]

        return cls(
            id=row.get("id"),
            session_id=row.get("session_id", ""),
            account_username=row.get("account_username", ""),
            login_timestamp=parse_datetime(row.get("login_timestamp")),
            logout_timestamp=parse_datetime(row.get("logout_timestamp")),
            justification=row.get("justification", ""),
            actions_performed=actions,
            post_usage_rotation_status=row.get(
                "post_usage_rotation_status", "not_required"
            ),
            client_ip=row.get("client_ip"),
            client_hostname=row.get("client_hostname"),
            created_at=parse_datetime(row.get("created_at")),
        )

    def to_record(self) -> dict[str, Any]:
        """Convert to database record."""
        login_ts = None
        if self.login_timestamp:
            login_ts = self.login_timestamp.isoformat()
        logout_ts = None
        if self.logout_timestamp:
            logout_ts = self.logout_timestamp.isoformat()
        return {
            "session_id": self.session_id,
            "account_username": self.account_username,
            "login_timestamp": login_ts,
            "logout_timestamp": logout_ts,
            "justification": self.justification,
            "actions_performed": json.dumps(
                [a.to_dict() for a in self.actions_performed]
            ),
            "post_usage_rotation_status": self.post_usage_rotation_status,
            "client_ip": self.client_ip,
            "client_hostname": self.client_hostname,
        }

    def add_action(
        self,
        action_type: str,
        description: str = "",
        target: str | None = None,
        timestamp: datetime | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Append an action to the session log."""
        entry = ActionEntry(
            action_type=action_type,
            description=description,
            target=target,
            timestamp=timestamp or datetime.now(),
            details=details,
        )
        self.actions_performed.append(entry)

    @property
    def is_active(self) -> bool:
        """Return True if the session is still active (no logout)."""
        return self.logout_timestamp is None

    @property
    def rotation_pending(self) -> bool:
        """Return True if credential rotation is pending."""
        return self.post_usage_rotation_status == "pending"

    @property
    def rotation_complete(self) -> bool:
        """Return True if credential rotation is complete."""
        return self.post_usage_rotation_status == "complete"

    def mark_rotation_pending(self) -> None:
        """Mark that credential rotation is required after logout."""
        self.post_usage_rotation_status = "pending"

    def mark_rotation_complete(self) -> None:
        """Mark that credential rotation has been completed."""
        self.post_usage_rotation_status = "complete"

    def end_session(self, logout_time: datetime | None = None) -> None:
        """End the break-glass session and mark rotation pending."""
        self.logout_timestamp = logout_time or datetime.now()
        self.mark_rotation_pending()

    @classmethod
    def create_session(
        cls,
        username: str,
        justification: str,
        start_time: datetime | None = None,
        session_id: str | None = None,
        client_ip: str | None = None,
        client_hostname: str | None = None,
    ) -> "BreakGlassUsageLog":
        """Create a new break-glass session.

        Args:
            username: The break-glass account username
            justification: Reason for emergency access
            start_time: Session start time (defaults to now)
            session_id: Optional session ID (generates UUID if not provided)
            client_ip: Optional client IP address
            client_hostname: Optional client hostname

        Returns:
            New BreakGlassUsageLog instance
        """
        import uuid

        return cls(
            session_id=session_id or str(uuid.uuid4()),
            account_username=username,
            login_timestamp=start_time or datetime.now(),
            justification=justification,
            client_ip=client_ip,
            client_hostname=client_hostname,
            created_at=datetime.now(),
        )

    @property
    def username(self) -> str:
        """Alias for account_username for compatibility."""
        return self.account_username

    @property
    def started_at(self) -> datetime | None:
        """Alias for login_timestamp for compatibility."""
        return self.login_timestamp

    @property
    def ended_at(self) -> datetime | None:
        """Alias for logout_timestamp for compatibility."""
        return self.logout_timestamp

    @property
    def actions(self) -> List[ActionEntry]:
        """Alias for actions_performed for compatibility."""
        return self.actions_performed

    @property
    def action_count(self) -> int:
        """Return the number of actions performed in this session."""
        return len(self.actions_performed)

    @property
    def needs_rotation(self) -> bool:
        """Return True if rotation is needed based on action count."""
        # Rotation needed if any actions were performed
        return len(self.actions_performed) > 0


__all__ = ["ActionEntry", "BreakGlassUsageLog"]
