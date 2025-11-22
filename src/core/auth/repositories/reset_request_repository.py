"""Reset request persistence helpers."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from typing import Iterable

from src.core.auth.models.reset_request import ResetRequest, ResetStatus
from src.core.auth.models.utils import datetime_to_iso
from src.core.database.repository_base import SQLiteRepository


def _blob(value: bytes | memoryview | None) -> sqlite3.Binary | None:
    if value is None:
        return None
    if isinstance(value, memoryview):
        value = value.tobytes()
    return sqlite3.Binary(bytes(value))


class ResetRequestRepository(SQLiteRepository):
    """Create, encrypt, and expire ``reset_requests`` rows."""

    def get(self, request_id: str) -> ResetRequest | None:
        with self._connection() as conn:
            row = conn.execute(
                "SELECT * FROM reset_requests WHERE request_id = ?",
                (request_id,),
            ).fetchone()
        if not row:
            return None
        return ResetRequest.from_row(dict(row))

    def create(self, request: ResetRequest) -> ResetRequest:
        record = request.to_record()
        now = datetime.now(timezone.utc)
        created_at = datetime_to_iso(request.created_at or now)
        expires_at = record.get("expires_at") or datetime_to_iso(request.expires_at)
        with self._connection() as conn:
            conn.execute(
                """
                INSERT INTO reset_requests (
                    request_id,
                    user_id,
                    initiated_by,
                    reason,
                    origin_surface,
                    dispatcher_channel,
                    status,
                    temporary_secret,
                    secret_nonce,
                    secret_displayed_at,
                    expires_at,
                    created_at,
                    completed_at,
                    justification
                ) VALUES (
                    :request_id,
                    :user_id,
                    :initiated_by,
                    :reason,
                    :origin_surface,
                    :dispatcher_channel,
                    :status,
                    :temporary_secret,
                    :secret_nonce,
                    :secret_displayed_at,
                    :expires_at,
                    :created_at,
                    :completed_at,
                    :justification
                )
                ON CONFLICT(request_id) DO UPDATE SET
                    status = excluded.status,
                    reason = excluded.reason,
                    temporary_secret = excluded.temporary_secret,
                    secret_nonce = excluded.secret_nonce,
                    secret_displayed_at = excluded.secret_displayed_at,
                    expires_at = excluded.expires_at,
                    completed_at = excluded.completed_at,
                    justification = excluded.justification
                """,
                {
                    "request_id": record["request_id"],
                    "user_id": record["user_id"],
                    "initiated_by": record["initiated_by"],
                    "reason": record.get("reason"),
                    "origin_surface": record["origin_surface"],
                    "dispatcher_channel": record["dispatcher_channel"],
                    "status": record["status"],
                    "temporary_secret": _blob(record.get("temporary_secret")),
                    "secret_nonce": _blob(record.get("secret_nonce")),
                    "secret_displayed_at": record.get("secret_displayed_at"),
                    "expires_at": expires_at,
                    "created_at": created_at,
                    "completed_at": record.get("completed_at"),
                    "justification": record.get("justification"),
                },
            )
            conn.commit()
        request.created_at = request.created_at or datetime.fromisoformat(created_at)
        return request

    def list_active(
        self,
        *,
        user_id: str | None = None,
    ) -> list[ResetRequest]:
        clauses = ["status IN ('pending', 'delivered')"]
        params: list[object] = []
        if user_id:
            clauses.append("user_id = ?")
            params.append(user_id)
        sql = (
            "SELECT * FROM reset_requests WHERE "
            + " AND ".join(clauses)
            + " ORDER BY created_at DESC"
        )
        with self._connection() as conn:
            rows = conn.execute(sql, tuple(params)).fetchall()
        return [ResetRequest.from_row(dict(row)) for row in rows or []]

    def mark_delivered(
        self,
        request_id: str,
        *,
        delivered_at: datetime | None = None,
    ) -> bool:
        timestamp = datetime_to_iso(delivered_at or datetime.now(timezone.utc))
        with self._connection() as conn:
            cursor = conn.execute(
                """
                UPDATE reset_requests
                SET status = :status,
                    secret_displayed_at = :delivered_at
                WHERE request_id = :request_id
                """,
                {
                    "status": ResetStatus.DELIVERED.value,
                    "delivered_at": timestamp,
                    "request_id": request_id,
                },
            )
            conn.commit()
            return bool(cursor.rowcount)

    def mark_completed(self, request_id: str) -> bool:
        timestamp = datetime_to_iso(datetime.now(timezone.utc))
        with self._connection() as conn:
            cursor = conn.execute(
                """
                UPDATE reset_requests
                SET status = :status,
                    completed_at = :completed_at,
                    temporary_secret = NULL,
                    secret_nonce = NULL,
                    secret_displayed_at = NULL
                WHERE request_id = :request_id
                """,
                {
                    "status": ResetStatus.COMPLETED.value,
                    "completed_at": timestamp,
                    "request_id": request_id,
                },
            )
            conn.commit()
            return bool(cursor.rowcount)

    def cancel(self, request_id: str, *, reason: str | None = None) -> bool:
        with self._connection() as conn:
            cursor = conn.execute(
                """
                UPDATE reset_requests
                SET status = :status,
                    reason = :reason,
                    temporary_secret = NULL,
                    secret_nonce = NULL
                WHERE request_id = :request_id
                """,
                {
                    "status": ResetStatus.CANCELLED.value,
                    "reason": reason,
                    "request_id": request_id,
                },
            )
            conn.commit()
            return bool(cursor.rowcount)

    def expire_outstanding(
        self,
        *,
        as_of: datetime | None = None,
    ) -> int:
        timestamp = datetime_to_iso(as_of or datetime.now(timezone.utc))
        with self._connection() as conn:
            cursor = conn.execute(
                """
                UPDATE reset_requests
                SET status = :status,
                    temporary_secret = NULL,
                    secret_nonce = NULL
                WHERE status IN ('pending', 'delivered')
                  AND expires_at <= :cutoff
                """,
                {
                    "status": ResetStatus.EXPIRED.value,
                    "cutoff": timestamp,
                },
            )
            conn.commit()
            return cursor.rowcount

    def purge_completed(
        self,
        *,
        older_than: datetime | None = None,
    ) -> int:
        cutoff = datetime_to_iso(older_than or datetime.now(timezone.utc))
        with self._connection() as conn:
            cursor = conn.execute(
                "DELETE FROM reset_requests WHERE status = ? AND completed_at <= ?",
                (ResetStatus.COMPLETED.value, cutoff),
            )
            conn.commit()
            return cursor.rowcount

    def hydrate_many(self, request_ids: Iterable[str]) -> list[ResetRequest]:
        identifiers = list(request_ids)
        if not identifiers:
            return []
        placeholders = ",".join("?" for _ in identifiers)
        sql = f"SELECT * FROM reset_requests WHERE request_id IN ({placeholders})"
        with self._connection() as conn:
            rows = conn.execute(sql, tuple(identifiers)).fetchall()
        return [ResetRequest.from_row(dict(row)) for row in rows or []]


__all__ = ["ResetRequestRepository"]
