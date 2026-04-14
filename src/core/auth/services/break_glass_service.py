"""Break-glass service: activate/deactivate emergency sessions."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:  # pragma: no cover
    from src.core.auth.repositories.user_account_repository import (
        UserAccountRepository,
    )
    from src.core.auth.services.audit_logger import AuditLogger

_DEFAULT_SESSION_DURATION_HOURS = 4


@dataclass
class ActivationResult:
    """Result of a break-glass activation attempt."""

    success: bool
    session_id: Optional[str] = None
    account_username: Optional[str] = None
    expires_at: Optional[datetime] = None
    error: Optional[str] = None

    @classmethod
    def ok(
        cls,
        *,
        session_id: str,
        account_username: str,
        expires_at: datetime,
    ) -> "ActivationResult":
        return cls(
            success=True,
            session_id=session_id,
            account_username=account_username,
            expires_at=expires_at,
        )

    @classmethod
    def failed(cls, error: str) -> "ActivationResult":
        return cls(success=False, error=error)


class BreakGlassService:
    """Manage break-glass emergency sessions.

    A break-glass session is created when an authorised account with
    ``is_break_glass=True`` authenticates.  Every activation is
    recorded via the audit logger; all actions taken during the session
    are expected to be logged by the caller.
    """

    def __init__(
        self,
        *,
        user_repository: "UserAccountRepository",
        audit_logger: Optional["AuditLogger"] = None,
        session_duration_hours: int = _DEFAULT_SESSION_DURATION_HOURS,
    ) -> None:
        self._repo = user_repository
        self._audit_logger = audit_logger
        self._session_duration = timedelta(hours=session_duration_hours)
        # In-process store of active sessions: username -> session_id
        self._active_sessions: dict[str, str] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def activate(
        self,
        *,
        username: str,
        justification: str,
    ) -> ActivationResult:
        """Open a break-glass session for *username*.

        The account must exist, be a break-glass account, and not be
        disabled.  The *justification* is stored for audit purposes.
        """
        account = self._repo.get(username)
        if account is None:
            return ActivationResult.failed(f"Account '{username}' not found.")

        if not account.is_break_glass:
            return ActivationResult.failed(
                f"Account '{username}' is not a break-glass account."
            )

        from src.core.auth.models.user_account import AccountStatus

        if account.account_status == AccountStatus.DISABLED:
            return ActivationResult.failed(f"Account '{username}' is disabled.")

        # Persist the justification text on the account record.
        account.break_glass_justification = justification
        self._repo.upsert(account)

        session_id = str(uuid.uuid4())
        expires_at = datetime.now(timezone.utc) + self._session_duration
        self._active_sessions[username] = session_id

        self._log(
            action_type="break_glass_login",
            actor_username=username,
            target_username=username,
            details={
                "session_id": session_id,
                "justification": justification,
                "expires_at": expires_at.isoformat(),
            },
        )

        return ActivationResult.ok(
            session_id=session_id,
            account_username=username,
            expires_at=expires_at,
        )

    def deactivate(self, *, username: str) -> bool:
        """End the active break-glass session for *username*.

        Returns ``True`` if a session was found and closed,
        ``False`` otherwise.
        """
        session_id = self._active_sessions.pop(username, None)
        if session_id is None:
            # Nothing in the in-process store; attempt a best-effort
            # deactivation by logging the attempt.
            self._log(
                action_type="break_glass_logout",
                actor_username=username,
                target_username=username,
                details={"note": "No active in-process session found"},
            )
            return False

        self._log(
            action_type="break_glass_logout",
            actor_username=username,
            target_username=username,
            details={"session_id": session_id},
        )
        return True

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _log(
        self,
        *,
        action_type: str,
        actor_username: str,
        target_username: str,
        details: Any = None,
    ) -> None:
        if self._audit_logger is None:
            return
        try:
            self._audit_logger.record_action(
                action_type=action_type,
                actor_username=actor_username,
                target_username=target_username,
                details=details or {},
            )
        except Exception:  # pylint: disable=broad-except
            pass  # Logging failures must never break the auth flow


__all__ = ["ActivationResult", "BreakGlassService"]
