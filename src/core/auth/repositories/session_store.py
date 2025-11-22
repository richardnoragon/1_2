"""Session token persistence helpers."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable

from src.core.auth.models.session_token import SessionToken
from src.core.auth.models.utils import datetime_to_iso
from src.core.database.repository_base import SQLiteRepository


class SessionStore(SQLiteRepository):
    """Create, revoke, and enumerate ``session_tokens`` rows."""

    def get(self, session_handle_hash: str) -> SessionToken | None:
        with self._connection() as conn:
            row = conn.execute(
                "SELECT * FROM session_tokens WHERE session_handle_hash = ?",
                (session_handle_hash,),
            ).fetchone()
        if not row:
            return None
        return SessionToken.from_row(dict(row))

    def issue(self, token: SessionToken) -> SessionToken:
        record = token.to_record()
        with self._connection() as conn:
            conn.execute(
                """
                INSERT INTO session_tokens (
                    session_handle_hash,
                    user_id,
                    issued_at,
                    last_activity_at,
                    expires_at,
                    surface,
                    origin_host,
                    revoked,
                    revoked_at,
                    preferences_id,
                    idle_timeout_deadline
                ) VALUES (
                    :session_handle_hash,
                    :user_id,
                    :issued_at,
                    :last_activity_at,
                    :expires_at,
                    :surface,
                    :origin_host,
                    :revoked,
                    :revoked_at,
                    :preferences_id,
                    :idle_timeout_deadline
                )
                ON CONFLICT(session_handle_hash) DO UPDATE SET
                    user_id = excluded.user_id,
                    last_activity_at = excluded.last_activity_at,
                    expires_at = excluded.expires_at,
                    surface = excluded.surface,
                    origin_host = excluded.origin_host,
                    revoked = excluded.revoked,
                    revoked_at = excluded.revoked_at,
                    preferences_id = excluded.preferences_id,
                    idle_timeout_deadline = excluded.idle_timeout_deadline
                """,
                record,
            )
            conn.commit()
        return token

    def list_active(
        self,
        *,
        user_id: str | None = None,
        include_revoked: bool = False,
    ) -> list[SessionToken]:
        clauses: list[str] = []
        params: list[object] = []
        if not include_revoked:
            clauses.append("revoked = 0")
        if user_id:
            clauses.append("user_id = ?")
            params.append(user_id)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        query = (
            "SELECT * FROM session_tokens " f"{where} ORDER BY last_activity_at DESC"
        )
        with self._connection() as conn:
            rows = conn.execute(query, tuple(params)).fetchall()
        return [SessionToken.from_row(dict(row)) for row in rows or []]

    def revoke(
        self,
        session_handle_hash: str,
        *,
        timestamp: datetime | None = None,
    ) -> bool:
        revoked_at = datetime_to_iso(timestamp or datetime.now(timezone.utc))
        with self._connection() as conn:
            cursor = conn.execute(
                """
                UPDATE session_tokens
                SET revoked = 1,
                    revoked_at = :revoked_at
                WHERE session_handle_hash = :hash
                """,
                {"revoked_at": revoked_at, "hash": session_handle_hash},
            )
            conn.commit()
            return bool(cursor.rowcount)

    def revoke_for_user(
        self,
        user_id: str,
        *,
        timestamp: datetime | None = None,
        include_revoked: bool = False,
    ) -> int:
        revoked_at = datetime_to_iso(timestamp or datetime.now(timezone.utc))
        clauses = ["user_id = :user_id"]
        if not include_revoked:
            clauses.append("revoked = 0")
        sql = (
            "UPDATE session_tokens SET revoked = 1, revoked_at = :revoked_at "
            f"WHERE {' AND '.join(clauses)}"
        )
        with self._connection() as conn:
            cursor = conn.execute(
                sql,
                {
                    "user_id": user_id,
                    "revoked_at": revoked_at,
                },
            )
            conn.commit()
            return cursor.rowcount

    def update_activity(
        self,
        session_handle_hash: str,
        *,
        activity_time: datetime | None = None,
        idle_deadline: datetime | None = None,
    ) -> bool:
        updates: list[str] = []
        params: dict[str, object | None] = {"hash": session_handle_hash}
        if activity_time is not None:
            updates.append("last_activity_at = :activity")
            params["activity"] = datetime_to_iso(activity_time)
        if idle_deadline is not None:
            updates.append("idle_timeout_deadline = :idle")
            params["idle"] = datetime_to_iso(idle_deadline)
        if not updates:
            return False
        sql = (
            "UPDATE session_tokens SET "
            + ", ".join(updates)
            + " WHERE session_handle_hash = :hash"
        )
        with self._connection() as conn:
            cursor = conn.execute(sql, params)
            conn.commit()
            return bool(cursor.rowcount)

    def list_idle(
        self,
        *,
        as_of: datetime | None = None,
    ) -> list[SessionToken]:
        moment = datetime_to_iso(as_of or datetime.now(timezone.utc))
        sql = (
            "SELECT * FROM session_tokens "
            "WHERE idle_timeout_deadline IS NOT NULL "
            "AND idle_timeout_deadline < ? "
            "AND revoked = 0"
        )
        with self._connection() as conn:
            rows = conn.execute(sql, (moment,)).fetchall()
        return [SessionToken.from_row(dict(row)) for row in rows or []]

    def purge_expired(
        self,
        *,
        as_of: datetime | None = None,
    ) -> int:
        cutoff = datetime_to_iso(as_of or datetime.now(timezone.utc))
        sql = (
            "DELETE FROM session_tokens "
            "WHERE (revoked = 1 AND revoked_at IS NOT NULL AND revoked_at < ?) "
            "OR expires_at < ?"
        )
        with self._connection() as conn:
            cursor = conn.execute(sql, (cutoff, cutoff))
            conn.commit()
            return cursor.rowcount

    def hydrate_many(self, hashes: Iterable[str]) -> list[SessionToken]:
        tokens: list[SessionToken] = []
        hash_list = list(hashes)
        if not hash_list:
            return tokens
        placeholders = ",".join("?" for _ in hash_list)
        sql = f"SELECT * FROM session_tokens WHERE session_handle_hash IN ({placeholders})"
        with self._connection() as conn:
            rows = conn.execute(sql, tuple(hash_list)).fetchall()
        for row in rows or []:
            tokens.append(SessionToken.from_row(dict(row)))
        return tokens


__all__ = ["SessionStore"]
