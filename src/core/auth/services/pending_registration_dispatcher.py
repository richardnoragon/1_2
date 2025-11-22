"""Telemetry dispatcher for pending self-registration events."""

from __future__ import annotations

import json
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from src.core.auth.models.admin_action_audit import AdminActionType
from src.core.auth.services.audit_logger import AuditLogger
from src.log_manager import get_log_manager

LOGGER = get_log_manager().get_logger("Auth.PendingRegistrationDispatcher")


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(tzinfo=None).isoformat()


@dataclass(slots=True)
class PendingRegistrationEvent:
    username: str | None
    channel: str | None
    submitted_at: str | None
    pending_count: int
    pending_preview: list[str]
    origin_surface: str | None
    database_path: str
    metadata: Mapping[str, Any]
    captured_at: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "username": self.username,
            "channel": self.channel,
            "submitted_at": self.submitted_at,
            "pending_count": self.pending_count,
            "pending_preview": self.pending_preview,
            "origin_surface": self.origin_surface,
            "database_path": self.database_path,
            "metadata": dict(self.metadata),
            "captured_at": self.captured_at,
        }


class PendingRegistrationDispatcher:
    """Persist telemetry for pending registration alerts."""

    def __init__(
        self,
        *,
        database_path: str | Path,
        telemetry_dir: str | Path | None = None,
        max_preview: int = 5,
        audit_logger: AuditLogger | None = None,
    ) -> None:
        self._database_path = Path(database_path)
        base_dir = (
            Path(telemetry_dir) if telemetry_dir else Path("reports") / "telemetry"
        )
        base_dir.mkdir(parents=True, exist_ok=True)
        self._history_file = base_dir / "pending_registration_alerts.jsonl"
        self._latest_file = base_dir / "pending_registration_alert_latest.json"
        self._max_preview = max(1, int(max_preview))
        self._audit_logger = audit_logger

    # ------------------------------------------------------------------
    def __call__(self, payload: Mapping[str, Any]) -> None:
        event = self._build_event(payload)
        try:
            self._append_history(event)
            self._write_latest(event)
            self._emit_audit_alert(event)
            LOGGER.info(
                "Pending registration alert for %s (pending_count=%s)",
                event.username,
                event.pending_count,
            )
        except Exception as exc:  # pragma: no cover - defensive logging
            LOGGER.warning(
                "Failed to write pending registration telemetry: %s",
                exc,
            )

    # ------------------------------------------------------------------
    def _build_event(
        self,
        payload: Mapping[str, Any],
    ) -> PendingRegistrationEvent:
        pending_count, preview = self._pending_snapshot()
        metadata = payload.get("metadata") or {}
        if not isinstance(metadata, Mapping):
            metadata = {"raw": metadata}
        submitted_at = payload.get("submitted_at")
        username = payload.get("username")
        channel = payload.get("channel")
        origin = payload.get("origin_surface")
        return PendingRegistrationEvent(
            username=str(username) if username is not None else None,
            channel=str(channel) if channel is not None else None,
            submitted_at=(str(submitted_at) if submitted_at is not None else None),
            pending_count=pending_count,
            pending_preview=preview,
            origin_surface=str(origin) if origin is not None else None,
            database_path=str(self._database_path),
            metadata=dict(metadata),
            captured_at=_utc_now(),
        )

    def _pending_snapshot(self) -> tuple[int, list[str]]:
        if not self._database_path.exists():
            return 0, []
        try:
            with sqlite3.connect(self._database_path) as conn:
                conn.row_factory = sqlite3.Row
                count_row = conn.execute(
                    "SELECT COUNT(*) AS total "
                    "FROM user_accounts WHERE account_status='pending'"
                ).fetchone()
                total_pending = int(count_row[0]) if count_row else 0
                rows = conn.execute(
                    """
                    SELECT username
                    FROM user_accounts
                    WHERE account_status = 'pending'
                    ORDER BY created_at ASC
                    LIMIT ?
                    """,
                    (self._max_preview,),
                ).fetchall()
        except sqlite3.Error as exc:  # pragma: no cover - defensive fallback
            LOGGER.warning("Pending registration snapshot failed: %s", exc)
            return 0, []
        preview = [str(row["username"]) for row in rows if row["username"]]
        return total_pending, preview

    def _append_history(self, event: PendingRegistrationEvent) -> None:
        line = json.dumps(event.to_dict(), sort_keys=True)
        with self._history_file.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")

    def _write_latest(self, event: PendingRegistrationEvent) -> None:
        with self._latest_file.open("w", encoding="utf-8") as handle:
            json.dump(event.to_dict(), handle, indent=2, sort_keys=True)

    def _emit_audit_alert(self, event: PendingRegistrationEvent) -> None:
        if not self._audit_logger:
            return
        details = {
            "pending_count": event.pending_count,
            "pending_preview": event.pending_preview,
            "submitted_at": event.submitted_at,
            "channel": event.channel,
            "captured_at": event.captured_at,
        }
        metadata = dict(event.metadata)
        if event.origin_surface:
            metadata.setdefault("origin_surface", event.origin_surface)
        actor = event.username or "pending_registration"
        correlation_id = self._build_correlation_id(event)
        try:
            self._audit_logger.record_action(
                action_type=AdminActionType.PENDING_REGISTRATION_ALERT,
                actor_username=actor,
                target_username=event.username,
                details=details,
                origin_surface=event.origin_surface,
                metadata=metadata,
                correlation_id=correlation_id,
            )
        except Exception as exc:  # pragma: no cover - defensive logging
            LOGGER.warning(
                "Failed to emit pending registration audit alert: %s",
                exc,
            )

    @staticmethod
    def _build_correlation_id(event: PendingRegistrationEvent) -> str:
        username = (event.username or "pending").strip().lower() or "pending"
        username = username.replace(" ", "-")
        token = uuid.uuid4().hex[:12]
        return f"pending-registration-{username}-{token}"


__all__ = ["PendingRegistrationDispatcher", "PendingRegistrationEvent"]
