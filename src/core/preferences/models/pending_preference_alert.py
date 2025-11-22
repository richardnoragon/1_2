"""Dataclass for pending preference alerts awaiting review."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Dict, Mapping

from src.core.auth.models.utils import (
    datetime_to_iso,
    dict_to_json,
    json_to_dict,
    parse_datetime,
)


class AlertSeverity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertResolutionState(StrEnum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


@dataclass(slots=True)
class PendingPreferenceAlert:
    alert_id: str
    user_id: str
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    severity: AlertSeverity = AlertSeverity.LOW
    resolution_state: AlertResolutionState = AlertResolutionState.OPEN
    notes: str | None = None
    resolved_at: datetime | None = None
    resolved_by: str | None = None
    preference_snapshot_version: int | None = None
    metadata: Dict[str, Any] | None = None

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> "PendingPreferenceAlert":
        return cls(
            alert_id=row["alert_id"],
            user_id=row["user_id"],
            detected_at=parse_datetime(row.get("detected_at"))
            or datetime.now(timezone.utc),
            severity=AlertSeverity(row.get("severity", AlertSeverity.LOW)),
            resolution_state=AlertResolutionState(
                row.get("resolution_state", AlertResolutionState.OPEN)
            ),
            notes=row.get("notes"),
            resolved_at=parse_datetime(row.get("resolved_at")),
            resolved_by=row.get("resolved_by"),
            preference_snapshot_version=row.get("preference_snapshot_version"),
            metadata=json_to_dict(row.get("metadata")),
        )

    def to_record(self) -> Dict[str, Any]:
        return {
            "alert_id": self.alert_id,
            "user_id": self.user_id,
            "detected_at": datetime_to_iso(self.detected_at),
            "severity": self.severity.value,
            "resolution_state": self.resolution_state.value,
            "notes": self.notes,
            "resolved_at": datetime_to_iso(self.resolved_at),
            "resolved_by": self.resolved_by,
            "preference_snapshot_version": self.preference_snapshot_version,
            "metadata": dict_to_json(self.metadata),
        }

    def mark_investigating(self, *, notes: str | None = None) -> None:
        self.resolution_state = AlertResolutionState.INVESTIGATING
        if notes:
            self.notes = notes

    def mark_resolved(
        self,
        *,
        resolved_by: str,
        notes: str | None = None,
        timestamp: datetime | None = None,
    ) -> None:
        self.resolution_state = AlertResolutionState.RESOLVED
        self.resolved_by = resolved_by
        self.resolved_at = timestamp or datetime.now(timezone.utc)
        if notes:
            self.notes = notes

    def dismiss(
        self,
        *,
        resolved_by: str,
        notes: str | None = None,
        timestamp: datetime | None = None,
    ) -> None:
        self.resolution_state = AlertResolutionState.DISMISSED
        self.resolved_by = resolved_by
        self.resolved_at = timestamp or datetime.now(timezone.utc)
        if notes:
            self.notes = notes

    def reopen(self, *, notes: str | None = None) -> None:
        self.resolution_state = AlertResolutionState.OPEN
        self.resolved_at = None
        self.resolved_by = None
        if notes:
            self.notes = notes

    def escalate_severity(self) -> None:
        order = [
            AlertSeverity.LOW,
            AlertSeverity.MEDIUM,
            AlertSeverity.HIGH,
            AlertSeverity.CRITICAL,
        ]
        try:
            idx = order.index(self.severity)
        except ValueError:
            self.severity = AlertSeverity.LOW
            idx = 0
        if idx < len(order) - 1:
            self.severity = order[idx + 1]

    def update_metadata(self, data: Dict[str, Any]) -> None:
        merged = dict(self.metadata or {})
        merged.update(data)
        self.metadata = merged


__all__ = [
    "AlertResolutionState",
    "AlertSeverity",
    "PendingPreferenceAlert",
]
