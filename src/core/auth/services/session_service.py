"""Session management helpers (logout, revocation, idle refresh)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable, Iterable, List

from src.core.auth.models import SessionToken
from src.core.auth.repositories.session_store import SessionStore
from src.log_manager import get_log_manager

Clock = Callable[[], datetime]


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class SessionService:
    """Coordinate session revocation + idle timeout bookkeeping."""

    def __init__(
        self,
        *,
        session_store: SessionStore | None = None,
        database_path: str | Path | None = None,
        idle_timeout: timedelta = timedelta(minutes=10),
        clock: Clock | None = None,
    ) -> None:
        if session_store is not None:
            self._store = session_store
        elif database_path is not None:
            self._store = SessionStore(database_path=database_path)
        else:
            # Fall back to global DatabaseManager wiring.
            self._store = SessionStore()
        self._idle_timeout = idle_timeout
        self._clock = clock or _utcnow
        self._logger = get_log_manager().get_logger("Auth.SessionService")

    # ------------------------------------------------------------------
    def logout(
        self,
        session_handle_hash: str,
        *,
        actor: str | None = None,
    ) -> bool:
        """Revoke a single session handle hash."""

        revoked = self._store.revoke(
            session_handle_hash,
            timestamp=self._clock(),
        )
        if revoked:
            self._logger.info(
                "Session %s revoked (actor=%s)",
                session_handle_hash,
                actor or "system",
            )
        else:
            self._logger.debug(
                "Session %s not found during logout request",
                session_handle_hash,
            )
        return revoked

    def logout_many(
        self,
        session_hashes: Iterable[str],
        *,
        actor: str | None = None,
    ) -> int:
        total = 0
        for handle in session_hashes:
            if self.logout(handle, actor=actor):
                total += 1
        return total

    def logout_user(
        self,
        username: str,
        *,
        include_revoked: bool = False,
        actor: str | None = None,
    ) -> int:
        revoked = self._store.revoke_for_user(
            username,
            timestamp=self._clock(),
            include_revoked=include_revoked,
        )
        if revoked:
            self._logger.info(
                "Revoked %s session(s) for user %s (actor=%s)",
                revoked,
                username,
                actor or "system",
            )
        return revoked

    def refresh_activity(
        self,
        session_handle_hash: str,
        *,
        idle_timeout: timedelta | None = None,
        activity_time: datetime | None = None,
    ) -> bool:
        moment = activity_time or self._clock()
        timeout = idle_timeout or self._idle_timeout
        idle_deadline = moment + timeout if timeout else None
        updated = self._store.update_activity(
            session_handle_hash,
            activity_time=moment,
            idle_deadline=idle_deadline,
        )
        if updated:
            self._logger.debug(
                "Session %s activity refreshed (idle deadline %s)",
                session_handle_hash,
                idle_deadline,
            )
        return updated

    def list_active(
        self,
        *,
        user_id: str | None = None,
        include_revoked: bool = False,
    ) -> List[SessionToken]:
        return self._store.list_active(
            user_id=user_id,
            include_revoked=include_revoked,
        )

    def purge_expired(self, *, as_of: datetime | None = None) -> int:
        removed = self._store.purge_expired(as_of=as_of or self._clock())
        if removed:
            self._logger.info("Purged %s expired session(s)", removed)
        return removed

    def ensure_idle_deadline(
        self,
        token: SessionToken,
        *,
        idle_timeout: timedelta | None = None,
    ) -> SessionToken:
        timeout = idle_timeout or self._idle_timeout
        if timeout.total_seconds() <= 0:
            return token
        if token.idle_timeout_deadline is None:
            token.set_idle_timeout(duration=timeout, reference=self._clock())
            self._store.update_activity(
                token.session_handle_hash,
                idle_deadline=token.idle_timeout_deadline,
            )
        return token


__all__ = ["SessionService"]
