"""Repository for admin_notification table operations."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

from src.core.auth.models.admin_notification import (
    AdminNotification,
    NotificationType,
)


class AdminNotificationRepository:
    """CRUD operations for admin_notification table."""

    def __init__(
        self,
        *,
        database_path: str | Path | None = None,
    ) -> None:
        self._database_path = Path(database_path) if database_path else None

    def _connect(self) -> sqlite3.Connection:
        if not self._database_path or not self._database_path.exists():
            raise FileNotFoundError(f"Database not found: {self._database_path}")
        conn = sqlite3.connect(self._database_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON;")
        return conn

    def create(self, notification: AdminNotification) -> AdminNotification:
        """Insert a new notification and return with ID."""
        with self._connect() as conn:
            row = notification.to_row()
            cursor = conn.execute(
                """
                INSERT INTO admin_notification (
                    notification_type,
                    subject,
                    body,
                    metadata,
                    acknowledged,
                    acknowledged_by,
                    acknowledged_at,
                    created_at,
                    expires_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row["notification_type"],
                    row["subject"],
                    row["body"],
                    row["metadata"],
                    row["acknowledged"],
                    row["acknowledged_by"],
                    row["acknowledged_at"],
                    row["created_at"],
                    row["expires_at"],
                ),
            )
            notification.notification_id = cursor.lastrowid
            conn.commit()
        return notification

    def get(self, notification_id: int) -> AdminNotification | None:
        """Get a notification by ID."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM admin_notification WHERE id = ?",
                (notification_id,),
            ).fetchone()
            if row is None:
                return None
            return AdminNotification.from_row(dict(row))

    def list_unacknowledged(
        self,
        *,
        notification_type: NotificationType | None = None,
        limit: int = 50,
    ) -> Sequence[AdminNotification]:
        """List unacknowledged notifications, optionally filtered by type."""
        query = "SELECT * FROM admin_notification WHERE acknowledged = 0"
        params: list = []
        if notification_type:
            query += " AND notification_type = ?"
            params.append(notification_type.value)
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
            return [AdminNotification.from_row(dict(r)) for r in rows]

    def list_recent(
        self,
        *,
        days: int = 7,
        limit: int = 100,
    ) -> Sequence[AdminNotification]:
        """List recent notifications within the given number of days."""
        query = """
            SELECT * FROM admin_notification
            WHERE created_at >= datetime('now', ?)
            ORDER BY created_at DESC
            LIMIT ?
        """
        with self._connect() as conn:
            rows = conn.execute(query, (f"-{days} days", limit)).fetchall()
            return [AdminNotification.from_row(dict(r)) for r in rows]

    def acknowledge(
        self,
        notification_id: int,
        admin_username: str,
    ) -> bool:
        """Acknowledge a notification. Returns True if updated."""
        now_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        with self._connect() as conn:
            cursor = conn.execute(
                """
                UPDATE admin_notification
                SET acknowledged = 1,
                    acknowledged_by = ?,
                    acknowledged_at = ?
                WHERE id = ? AND acknowledged = 0
                """,
                (admin_username, now_iso, notification_id),
            )
            conn.commit()
            return cursor.rowcount > 0

    def count_unacknowledged(
        self,
        notification_type: NotificationType | None = None,
    ) -> int:
        """Count unacknowledged notifications."""
        query = "SELECT COUNT(*) FROM admin_notification WHERE acknowledged = 0"
        params: list = []
        if notification_type:
            query += " AND notification_type = ?"
            params.append(notification_type.value)
        with self._connect() as conn:
            result = conn.execute(query, params).fetchone()
            return result[0] if result else 0

    def delete_expired(self) -> int:
        """Delete expired notifications. Returns count deleted."""
        with self._connect() as conn:
            cursor = conn.execute(
                """
                DELETE FROM admin_notification
                WHERE expires_at IS NOT NULL
                  AND expires_at < datetime('now')
                """
            )
            conn.commit()
            return cursor.rowcount


__all__ = ["AdminNotificationRepository"]
