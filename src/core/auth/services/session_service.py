"""Session management helpers (logout, revocation, idle refresh)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Callable, Iterable, List, Optional

from src.core.auth.models import SessionToken
from src.core.auth.repositories.session_store import SessionStore
from src.log_manager import get_log_manager

if TYPE_CHECKING:
    from src.core.auth.services.admin_notification_service import (
        AdminNotificationService,
    )
    from src.core.auth.services.break_glass_service import BreakGlassService

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
        break_glass_service: Optional["BreakGlassService"] = None,
        notification_service: Optional["AdminNotificationService"] = None,
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
        self._break_glass_service = break_glass_service
        self._notification_service = notification_service

    # ------------------------------------------------------------------
    def logout(
        self,
        session_handle_hash: str,
        *,
        actor: str | None = None,
    ) -> bool:
        """Revoke a single session handle hash.

        For break-glass sessions, this also deactivates the break-glass
        session and triggers credential rotation requirements.
        """
        # Get session to check if it's break-glass
        token = self._store.get(session_handle_hash)

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

            # Handle break-glass session deactivation
            if token and token.is_break_glass:
                self._handle_break_glass_logout(token, actor)
        else:
            self._logger.debug(
                "Session %s not found during logout request",
                session_handle_hash,
            )
        return revoked

    def _handle_break_glass_logout(
        self,
        token: SessionToken,
        actor: str | None = None,
    ) -> None:
        """Handle break-glass session logout with rotation trigger.

        Args:
            token: The break-glass session token being logged out
            actor: The actor performing the logout
        """
        username = token.user_id
        bg_session_id = token.break_glass_session_id

        self._logger.warning(
            "Break-glass session ended: user=%s, session_id=%s",
            username,
            bg_session_id,
        )

        # Deactivate the break-glass session
        if self._break_glass_service and bg_session_id:
            deactivated = self._break_glass_service.deactivate(
                username,
                now=self._clock(),
            )
            if deactivated:
                self._logger.info(
                    "Break-glass session deactivated: %s",
                    bg_session_id,
                )
            else:
                self._logger.warning(
                    "Failed to deactivate break-glass session: %s",
                    bg_session_id,
                )

        # Calculate session duration
        duration_minutes = 0
        if token.issued_at:
            duration = self._clock() - token.issued_at
            duration_minutes = int(duration.total_seconds() / 60)

        # Send notification about session end
        if self._notification_service and bg_session_id:
            # Get action count from break-glass service if available
            action_count = 0
            if self._break_glass_service:
                status = self._break_glass_service.get_session_status(username)
                if status:
                    action_count = status.action_count

            self._notification_service.notify_break_glass_session_ended(
                username=username,
                session_id=bg_session_id,
                duration_minutes=duration_minutes,
                action_count=action_count,
            )

            # Notify that rotation is required
            reason_text = f"Break-glass session ended after {duration_minutes} minutes"
            self._notification_service.notify_rotation_required(
                username=username,
                reason=reason_text,
                urgency="high",
            )

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
