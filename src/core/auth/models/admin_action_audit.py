"""Structured representation of admin action audit records."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Dict, Mapping

from .utils import datetime_to_iso, dict_to_json, json_to_dict, parse_datetime


class AdminActionType(StrEnum):
    APPROVE_USER = "approve_user"
    RESET_PASSWORD = "reset_password"
    UNBLOCK_USER = "unblock_user"
    EXPORT_PREFERENCES = "export_preferences"
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOCKOUT = "lockout"
    SHARE_PREFERENCES = "share_preferences"
    UNAUTHORIZED_ADMIN_ACTION = "unauthorized_admin_action"
    SELF_REGISTRATION = "self_registration"
    PREFERENCE_RECOVERY = "preference_recovery"
    PENDING_REGISTRATION_ALERT = "pending_registration_alert"

    @classmethod
    def coerce(cls, value: object | None) -> "AdminActionType":
        if isinstance(value, cls):
            return value
        candidate = cls.APPROVE_USER.value if value is None else str(value)
        try:
            return cls(candidate)
        except ValueError:
            return cls.UNAUTHORIZED_ADMIN_ACTION


class AdminActionSurface(StrEnum):
    GUI = "gui"
    CLI = "cli"
    SERVICE = "service"

    @classmethod
    def coerce(cls, value: object | None) -> "AdminActionSurface":
        if isinstance(value, cls):
            return value
        candidate = cls.GUI.value if value is None else str(value)
        try:
            return cls(candidate)
        except ValueError:
            return cls.GUI


@dataclass(slots=True)
class AdminActionAudit:
    audit_id: str
    actor_username: str
    action_type: AdminActionType
    details: str
    target_username: str | None = None
    origin_surface: AdminActionSurface = AdminActionSurface.GUI
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: str | None = None
    metadata: Dict[str, Any] | None = None

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> "AdminActionAudit":
        return cls(
            audit_id=row["audit_id"],
            actor_username=row["actor_username"],
            action_type=AdminActionType.coerce(row.get("action_type")),
            details=row.get("details", ""),
            target_username=row.get("target_username"),
            origin_surface=AdminActionSurface.coerce(row.get("origin_surface")),
            created_at=parse_datetime(row.get("created_at"))
            or datetime.now(timezone.utc),
            correlation_id=row.get("correlation_id"),
            metadata=json_to_dict(row.get("metadata")),
        )

    def to_record(self) -> Dict[str, Any]:
        return {
            "audit_id": self.audit_id,
            "actor_username": self.actor_username,
            "action_type": self.action_type.value,
            "target_username": self.target_username,
            "origin_surface": self.origin_surface.value,
            "details": self.details,
            "created_at": datetime_to_iso(self.created_at),
            "correlation_id": self.correlation_id,
            "metadata": dict_to_json(self.metadata),
        }

    def attach_metadata(
        self, extra: Dict[str, Any] | None = None, /, **kwargs: Any
    ) -> None:
        if extra is None and not kwargs:
            return
        payload: Dict[str, Any] = dict(self.metadata or {})
        payload.update(extra or {})
        payload.update(kwargs)
        self.metadata = payload

    def set_details(self, details: str) -> None:
        self.details = details

    def stamp_correlation(self, correlation_id: str) -> None:
        self.correlation_id = correlation_id


__all__ = [
    "AdminActionAudit",
    "AdminActionSurface",
    "AdminActionType",
]
