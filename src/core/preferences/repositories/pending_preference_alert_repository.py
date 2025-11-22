"""Repository for ``pending_preference_alerts`` lifecycle management."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable

from src.core.auth.models.utils import datetime_to_iso
from src.core.database.repository_base import SQLiteRepository
from src.core.preferences.models.pending_preference_alert import (
    AlertResolutionState,
    AlertSeverity,
    PendingPreferenceAlert,
)


class PendingPreferenceAlertRepository(SQLiteRepository):
    """Create, query, and resolve preference corruption alerts."""

    def get(self, alert_id: str) -> PendingPreferenceAlert | None:
        with self._connection() as conn:
            row = conn.execute(
                "SELECT * FROM pending_preference_alerts WHERE alert_id = ?",
                (alert_id,),
            ).fetchone()
        if not row:
            return None
        return PendingPreferenceAlert.from_row(dict(row))

    def create(self, alert: PendingPreferenceAlert) -> PendingPreferenceAlert:
        record = alert.to_record()
        detected_at = record.get("detected_at") or datetime_to_iso(
            alert.detected_at or datetime.now(timezone.utc)
        )
        with self._connection() as conn:
            conn.execute(
                """
                INSERT INTO pending_preference_alerts (
                    alert_id,
                    user_id,
                    detected_at,
                    severity,
                    resolution_state,
                    notes,
                    resolved_at,
                    resolved_by,
                    preference_snapshot_version,
                    metadata
                ) VALUES (
                    :alert_id,
                    :user_id,
                    :detected_at,
                    :severity,
                    :resolution_state,
                    :notes,
                    :resolved_at,
                    :resolved_by,
                    :preference_snapshot_version,
                    :metadata
                )
                ON CONFLICT(alert_id) DO UPDATE SET
                    severity = excluded.severity,
                    resolution_state = excluded.resolution_state,
                    notes = excluded.notes,
                    resolved_at = excluded.resolved_at,
                    resolved_by = excluded.resolved_by,
                    preference_snapshot_version = excluded.preference_snapshot_version,
                    metadata = excluded.metadata
                """,
                {
                    "alert_id": record["alert_id"],
                    "user_id": record["user_id"],
                    "detected_at": detected_at,
                    "severity": record["severity"],
                    "resolution_state": record["resolution_state"],
                    "notes": record.get("notes"),
                    "resolved_at": record.get("resolved_at"),
                    "resolved_by": record.get("resolved_by"),
                    "preference_snapshot_version": record.get(
                        "preference_snapshot_version"
                    ),
                    "metadata": record.get("metadata"),
                },
            )
            conn.commit()
        alert.detected_at = alert.detected_at or datetime.fromisoformat(detected_at)
        return alert

    def list_open(
        self,
        *,
        user_id: str | None = None,
        severities: Iterable[AlertSeverity] | None = None,
    ) -> list[PendingPreferenceAlert]:
        clauses = ["resolution_state IN ('open', 'investigating')"]
        params: list[object] = []
        if user_id:
            clauses.append("user_id = ?")
            params.append(user_id)
        if severities:
            severity_values = [
                severity.value if isinstance(severity, AlertSeverity) else str(severity)
                for severity in severities
            ]
            placeholders = ",".join("?" for _ in severity_values)
            clauses.append(f"severity IN ({placeholders})")
            params.extend(severity_values)
        sql = (
            "SELECT * FROM pending_preference_alerts WHERE "
            + " AND ".join(clauses)
            + " ORDER BY detected_at DESC"
        )
        with self._connection() as conn:
            rows = conn.execute(sql, tuple(params)).fetchall()
        return [PendingPreferenceAlert.from_row(dict(row)) for row in rows or []]

    def resolve(
        self,
        alert_id: str,
        *,
        resolved_by: str,
        notes: str | None = None,
        timestamp: datetime | None = None,
    ) -> bool:
        resolved_at = datetime_to_iso(timestamp or datetime.now(timezone.utc))
        with self._connection() as conn:
            cursor = conn.execute(
                """
                UPDATE pending_preference_alerts
                SET resolution_state = :state,
                    resolved_by = :resolved_by,
                    resolved_at = :resolved_at,
                    notes = COALESCE(:notes, notes)
                WHERE alert_id = :alert_id
                """,
                {
                    "state": AlertResolutionState.RESOLVED.value,
                    "resolved_by": resolved_by,
                    "resolved_at": resolved_at,
                    "notes": notes,
                    "alert_id": alert_id,
                },
            )
            conn.commit()
            return bool(cursor.rowcount)

    def dismiss(
        self,
        alert_id: str,
        *,
        resolved_by: str,
        notes: str | None = None,
        timestamp: datetime | None = None,
    ) -> bool:
        resolved_at = datetime_to_iso(timestamp or datetime.now(timezone.utc))
        with self._connection() as conn:
            cursor = conn.execute(
                """
                UPDATE pending_preference_alerts
                SET resolution_state = :state,
                    resolved_by = :resolved_by,
                    resolved_at = :resolved_at,
                    notes = COALESCE(:notes, notes)
                WHERE alert_id = :alert_id
                """,
                {
                    "state": AlertResolutionState.DISMISSED.value,
                    "resolved_by": resolved_by,
                    "resolved_at": resolved_at,
                    "notes": notes,
                    "alert_id": alert_id,
                },
            )
            conn.commit()
            return bool(cursor.rowcount)

    def reopen(self, alert_id: str, *, notes: str | None = None) -> bool:
        with self._connection() as conn:
            cursor = conn.execute(
                """
                UPDATE pending_preference_alerts
                SET resolution_state = :state,
                    resolved_at = NULL,
                    resolved_by = NULL,
                    notes = COALESCE(:notes, notes)
                WHERE alert_id = :alert_id
                """,
                {
                    "state": AlertResolutionState.OPEN.value,
                    "notes": notes,
                    "alert_id": alert_id,
                },
            )
            conn.commit()
            return bool(cursor.rowcount)

    def delete(self, alert_id: str) -> bool:
        with self._connection() as conn:
            cursor = conn.execute(
                "DELETE FROM pending_preference_alerts WHERE alert_id = ?",
                (alert_id,),
            )
            conn.commit()
            return bool(cursor.rowcount)


__all__ = ["PendingPreferenceAlertRepository"]
