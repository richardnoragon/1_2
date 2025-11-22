"""Idle timeout enforcement helpers for RFU sessions.

The integration tests expect an ``enforce_idle_timeouts`` callable that inspects
``session_tokens`` rows, revokes any sessions exceeding the configured idle
window, and returns a metadata summary used by orchestration layers (hub/CLI).
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict

from src.log_manager import get_log_manager

LOGGER = get_log_manager().get_logger("IdleTimeoutWatcher")


def _utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def _isoformat(ts: datetime) -> str:
    return ts.isoformat().replace("+00:00", "Z")


def _connect(database_path: Path) -> sqlite3.Connection:
    if not database_path.exists():
        raise FileNotFoundError(f"Database not found at {database_path}")
    conn = sqlite3.connect(database_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


def _build_revocation_clause(placeholders: int) -> str:
    joined = ",".join(["?"] * placeholders)
    return f"session_handle_hash IN ({joined})"


def _collect_stale_handles(
    conn: sqlite3.Connection,
    *,
    now_iso: str,
    cutoff_iso: str,
) -> list[str]:
    rows = conn.execute(
        """
        SELECT session_handle_hash
        FROM session_tokens
        WHERE revoked = 0
          AND (
                (last_activity_at IS NOT NULL AND last_activity_at <= ?)
             OR (
                    last_activity_at IS NULL
                AND idle_timeout_deadline IS NOT NULL
                AND idle_timeout_deadline <= ?
             )
          )
        """,
        (cutoff_iso, now_iso),
    ).fetchall()
    return [row[0] for row in rows]


def _count_active_sessions(conn: sqlite3.Connection) -> int:
    row = conn.execute(
        "SELECT COUNT(*) FROM session_tokens WHERE revoked = 0"
    ).fetchone()
    return int(row[0]) if row else 0


def enforce_idle_timeouts(
    *,
    database_path: str | Path,
    idle_minutes: int = 10,
) -> Dict[str, Any]:
    """Revoke sessions that exceeded the idle window.

    Args:
        database_path: Path to the SQLite identity database.
        idle_minutes: Idle timeout window in minutes.

    Returns:
        Metadata describing the enforcement pass (counts and thresholds).
    """

    if idle_minutes <= 0:
        raise ValueError("idle_minutes must be a positive integer")

    db_path = Path(database_path)
    now = _utc_now()
    cutoff = now - timedelta(minutes=idle_minutes)
    now_iso = _isoformat(now)
    cutoff_iso = _isoformat(cutoff)

    with _connect(db_path) as conn:
        stale_handles = _collect_stale_handles(
            conn,
            now_iso=now_iso,
            cutoff_iso=cutoff_iso,
        )
        revoked_count = 0
        if stale_handles:
            clause = _build_revocation_clause(len(stale_handles))
            params: list[Any] = [now_iso, *stale_handles]
            conn.execute(
                f"""
                UPDATE session_tokens
                SET revoked = 1,
                    revoked_at = ?
                WHERE {clause}
                """,
                params,
            )
            conn.commit()
            revoked_count = len(stale_handles)

        summary: Dict[str, Any] = {
            "timestamp": now_iso,
            "threshold": cutoff_iso,
            "idle_minutes": idle_minutes,
            "revoked_sessions": revoked_count,
            "checked_sessions": _count_active_sessions(conn),
            "database_path": str(db_path),
        }
        if revoked_count:
            LOGGER.warning(
                "Revoked %s stale session(s) exceeding idle timeout (threshold=%s)",
                revoked_count,
                cutoff_iso,
            )
        else:
            LOGGER.debug(
                "Idle timeout enforcement ran with no revocations (threshold=%s)",
                cutoff_iso,
            )
        return summary


__all__ = ["enforce_idle_timeouts"]
