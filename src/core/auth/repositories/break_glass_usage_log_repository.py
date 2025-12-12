"""Repository for break-glass usage logs.

Provides persistence for BreakGlassUsageLog records.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, List, Optional

from src.core.auth.models.break_glass_usage_log import (
    ActionEntry,
    BreakGlassUsageLog,
)


class BreakGlassUsageLogRepository:
    """Repository for break-glass usage logs.

    Manages persistence of BreakGlassUsageLog instances
    to the SQLite database.
    """

    TABLE_NAME = "break_glass_usage_log"

    def __init__(self, db_connection: Any = None):
        """Initialize repository.

        Args:
            db_connection: SQLite database connection
        """
        self._conn = db_connection

    def save(self, log: BreakGlassUsageLog) -> bool:
        """Save or update a usage log.

        Args:
            log: The usage log to save

        Returns:
            True if save was successful
        """
        if self._conn is None:
            return False

        try:
            # Serialize actions to JSON
            actions_json = json.dumps(
                [
                    {
                        "action_type": a.action_type,
                        "description": a.description,
                        "timestamp": a.timestamp.isoformat(),
                    }
                    for a in log.actions
                ]
            )

            cursor = self._conn.cursor()
            cursor.execute(
                f"""
                INSERT INTO {self.TABLE_NAME}
                    (session_id, username, justification, started_at,
                     ended_at, actions, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(session_id) DO UPDATE SET
                    ended_at = excluded.ended_at,
                    actions = excluded.actions,
                    is_active = excluded.is_active
                """,
                (
                    log.session_id,
                    log.username,
                    log.justification,
                    log.started_at.isoformat() if log.started_at else None,
                    log.ended_at.isoformat() if log.ended_at else None,
                    actions_json,
                    int(log.is_active),
                ),
            )
            self._conn.commit()
            return True
        except Exception:
            return False

    def get_by_session_id(self, session_id: str) -> Optional[BreakGlassUsageLog]:
        """Get a usage log by session ID.

        Args:
            session_id: The session ID

        Returns:
            BreakGlassUsageLog or None if not found
        """
        if self._conn is None:
            return None

        try:
            cursor = self._conn.cursor()
            cursor.execute(
                f"""
                SELECT session_id, username, justification, started_at,
                       ended_at, actions, is_active
                FROM {self.TABLE_NAME}
                WHERE session_id = ?
                """,
                (session_id,),
            )
            row = cursor.fetchone()
            if row is None:
                return None

            return self._row_to_log(row)
        except Exception:
            return None

    def get_active_session(self, username: str) -> Optional[BreakGlassUsageLog]:
        """Get active session for a username.

        Args:
            username: The account username

        Returns:
            BreakGlassUsageLog or None if no active session
        """
        if self._conn is None:
            return None

        try:
            cursor = self._conn.cursor()
            cursor.execute(
                f"""
                SELECT session_id, username, justification, started_at,
                       ended_at, actions, is_active
                FROM {self.TABLE_NAME}
                WHERE username = ? AND is_active = 1
                ORDER BY started_at DESC
                LIMIT 1
                """,
                (username,),
            )
            row = cursor.fetchone()
            if row is None:
                return None

            return self._row_to_log(row)
        except Exception:
            return None

    def get_sessions(
        self,
        username: str | None = None,
        session_id: str | None = None,
        since: datetime | None = None,
        limit: int = 100,
    ) -> List[BreakGlassUsageLog]:
        """Get sessions matching filters.

        Args:
            username: Filter by username
            session_id: Filter by session ID
            since: Only sessions after this time
            limit: Maximum number of results

        Returns:
            List of matching logs
        """
        if self._conn is None:
            return []

        try:
            conditions = []
            params = []

            if username:
                conditions.append("username = ?")
                params.append(username)

            if session_id:
                conditions.append("session_id = ?")
                params.append(session_id)

            if since:
                conditions.append("started_at >= ?")
                params.append(since.isoformat())

            where_clause = ""
            if conditions:
                where_clause = "WHERE " + " AND ".join(conditions)

            cursor = self._conn.cursor()
            cursor.execute(
                f"""
                SELECT session_id, username, justification, started_at,
                       ended_at, actions, is_active
                FROM {self.TABLE_NAME}
                {where_clause}
                ORDER BY started_at DESC
                LIMIT ?
                """,
                (*params, limit),
            )
            rows = cursor.fetchall()
            return [self._row_to_log(row) for row in rows]
        except Exception:
            return []

    def get_sessions_for_user(
        self,
        username: str,
        limit: int = 50,
    ) -> List[BreakGlassUsageLog]:
        """Get all sessions for a user.

        Args:
            username: The account username
            limit: Maximum number of results

        Returns:
            List of logs for the user
        """
        return self.get_sessions(username=username, limit=limit)

    def get_recent_sessions(
        self,
        hours: int = 24,
        limit: int = 100,
    ) -> List[BreakGlassUsageLog]:
        """Get recent sessions within time window.

        Args:
            hours: Number of hours to look back
            limit: Maximum number of results

        Returns:
            List of recent logs
        """
        if self._conn is None:
            return []

        try:
            cursor = self._conn.cursor()
            cursor.execute(
                f"""
                SELECT session_id, username, justification, started_at,
                       ended_at, actions, is_active
                FROM {self.TABLE_NAME}
                WHERE started_at >= datetime('now', '-{hours} hours')
                ORDER BY started_at DESC
                LIMIT ?
                """,
                (limit,),
            )
            rows = cursor.fetchall()
            return [self._row_to_log(row) for row in rows]
        except Exception:
            return []

    def delete(self, session_id: str) -> bool:
        """Delete a usage log by session ID.

        Args:
            session_id: The session ID to delete

        Returns:
            True if deletion was successful
        """
        if self._conn is None:
            return False

        try:
            cursor = self._conn.cursor()
            cursor.execute(
                f"DELETE FROM {self.TABLE_NAME} WHERE session_id = ?",
                (session_id,),
            )
            self._conn.commit()
            return cursor.rowcount > 0
        except Exception:
            return False

    def count_sessions(
        self,
        username: str | None = None,
        active_only: bool = False,
    ) -> int:
        """Count sessions matching criteria.

        Args:
            username: Filter by username
            active_only: Only count active sessions

        Returns:
            Number of matching sessions
        """
        if self._conn is None:
            return 0

        try:
            conditions = []
            params = []

            if username:
                conditions.append("username = ?")
                params.append(username)

            if active_only:
                conditions.append("is_active = 1")

            where_clause = ""
            if conditions:
                where_clause = "WHERE " + " AND ".join(conditions)

            cursor = self._conn.cursor()
            cursor.execute(
                f"SELECT COUNT(*) FROM {self.TABLE_NAME} {where_clause}",
                params,
            )
            row = cursor.fetchone()
            return row[0] if row else 0
        except Exception:
            return 0

    def _row_to_log(self, row: tuple) -> BreakGlassUsageLog:
        """Convert database row to BreakGlassUsageLog.

        Args:
            row: Database row tuple

        Returns:
            BreakGlassUsageLog instance
        """
        # Parse actions from JSON
        actions = []
        if row[5]:
            try:
                actions_data = json.loads(row[5])
                actions = [
                    ActionEntry(
                        action_type=a["action_type"],
                        description=a["description"],
                        timestamp=datetime.fromisoformat(a["timestamp"]),
                    )
                    for a in actions_data
                ]
            except (json.JSONDecodeError, KeyError):
                pass

        return BreakGlassUsageLog(
            session_id=row[0],
            username=row[1],
            justification=row[2],
            started_at=datetime.fromisoformat(row[3]) if row[3] else None,
            ended_at=datetime.fromisoformat(row[4]) if row[4] else None,
            actions=actions,
        )


__all__ = ["BreakGlassUsageLogRepository"]
