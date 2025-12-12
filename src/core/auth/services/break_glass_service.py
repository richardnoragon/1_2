"""Break-glass emergency access service.

Provides emergency administrative access when normal access paths fail.
Break-glass access requires justification and logs all actions for audit.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, List, Optional

from src.core.auth.models.break_glass_usage_log import BreakGlassUsageLog
from src.core.auth.models.user_account import AccountStatus, UserAccount, UserRole


@dataclass(frozen=True, slots=True)
class BreakGlassActivationResult:
    """Result of break-glass activation attempt."""

    success: bool
    session_id: str | None = None
    account_username: str | None = None
    expires_at: datetime | None = None
    error: str | None = None

    @classmethod
    def activated(
        cls,
        session_id: str,
        username: str,
        expires_at: datetime,
    ) -> "BreakGlassActivationResult":
        """Successful activation."""
        return cls(
            success=True,
            session_id=session_id,
            account_username=username,
            expires_at=expires_at,
        )

    @classmethod
    def failed(cls, error: str) -> "BreakGlassActivationResult":
        """Failed activation."""
        return cls(success=False, error=error)


@dataclass(frozen=True, slots=True)
class BreakGlassSessionStatus:
    """Status of an active break-glass session."""

    session_id: str
    account_username: str
    started_at: datetime
    expires_at: datetime | None
    action_count: int
    is_active: bool
    justification: str


@dataclass(frozen=True, slots=True)
class BreakGlassAuditEntry:
    """Single audit entry for break-glass activity."""

    session_id: str
    account_username: str
    action_type: str
    action_detail: str
    timestamp: datetime
    justification: str


class BreakGlassService:
    """Service for managing break-glass emergency access.

    Coordinates:
    - Activation with justification validation
    - Session lifecycle management
    - Action logging and audit trail
    - Deactivation and rotation requirements
    """

    # Session duration limits
    DEFAULT_SESSION_DURATION_MINUTES = 60
    MAX_SESSION_DURATION_MINUTES = 240
    MIN_JUSTIFICATION_LENGTH = 10

    def __init__(
        self,
        user_repository: Any = None,
        usage_log_repository: Any = None,
        audit_logger: Any = None,
        notification_service: Any = None,
        session_duration_minutes: int = DEFAULT_SESSION_DURATION_MINUTES,
    ):
        """Initialize the service.

        Args:
            user_repository: Repository for user accounts
            usage_log_repository: Repository for break-glass logs
            audit_logger: General audit logger
            notification_service: Service for admin notifications
            session_duration_minutes: Session duration in minutes
        """
        self._user_repo = user_repository
        self._log_repo = usage_log_repository
        self._audit_logger = audit_logger
        self._notification_service = notification_service
        self._session_duration = min(
            session_duration_minutes,
            self.MAX_SESSION_DURATION_MINUTES,
        )
        self._active_sessions: dict[str, BreakGlassUsageLog] = {}

    def activate(
        self,
        username: str,
        justification: str,
        now: datetime | None = None,
    ) -> BreakGlassActivationResult:
        """Activate break-glass access for an account.

        Args:
            username: The break-glass account username
            justification: Reason for emergency access (required)
            now: Current time (for testing)

        Returns:
            BreakGlassActivationResult with session details or error
        """
        activation_time = now or datetime.now()

        # Validate justification
        validation_error = self._validate_justification(justification)
        if validation_error:
            return BreakGlassActivationResult.failed(validation_error)

        # Get and validate account
        user = self._get_user(username)
        if user is None:
            return BreakGlassActivationResult.failed("account not found")

        if not user.is_break_glass:
            return BreakGlassActivationResult.failed("not a break-glass account")

        if user.account_status != AccountStatus.ACTIVE:
            return BreakGlassActivationResult.failed(
                f"account is {user.account_status.value}"
            )

        # Check for existing active session
        if username in self._active_sessions:
            existing = self._active_sessions[username]
            if existing.is_active:
                return BreakGlassActivationResult.failed("session already active")

        # Create session
        session = BreakGlassUsageLog.create_session(
            username=username,
            justification=justification,
            start_time=activation_time,
        )
        self._active_sessions[username] = session

        # Calculate expiration
        expires_at = activation_time + timedelta(minutes=self._session_duration)

        # Persist if repository available
        if self._log_repo:
            self._log_repo.save(session)

        # Send notification
        if self._notification_service:
            self._notification_service.notify_break_glass_activation(
                username=username,
                justification=justification,
                session_id=session.session_id,
            )

        # Log to audit
        if self._audit_logger:
            self._audit_logger.record_action(
                action_type="break_glass_activated",
                actor=username,
                target=username,
                details={
                    "session_id": session.session_id,
                    "justification": justification,
                    "expires_at": expires_at.isoformat(),
                },
            )

        return BreakGlassActivationResult.activated(
            session_id=session.session_id,
            username=username,
            expires_at=expires_at,
        )

    def deactivate(
        self,
        username: str,
        now: datetime | None = None,
    ) -> bool:
        """Deactivate an active break-glass session.

        Args:
            username: The break-glass account username
            now: Current time (for testing)

        Returns:
            True if session was deactivated
        """
        end_time = now or datetime.now()

        if username not in self._active_sessions:
            return False

        session = self._active_sessions[username]
        if not session.is_active:
            return False

        # End the session
        session.end_session(end_time)

        # Persist if repository available
        if self._log_repo:
            self._log_repo.save(session)

        # Check rotation requirement
        if session.needs_rotation:
            if self._notification_service:
                self._notification_service.notify_rotation_required(
                    username=username,
                    session_id=session.session_id,
                    action_count=session.action_count,
                )

        # Log to audit
        if self._audit_logger:
            self._audit_logger.record_action(
                action_type="break_glass_deactivated",
                actor=username,
                target=username,
                details={
                    "session_id": session.session_id,
                    "action_count": session.action_count,
                    "needs_rotation": session.needs_rotation,
                },
            )

        return True

    def log_action(
        self,
        username: str,
        action_type: str,
        action_detail: str,
        now: datetime | None = None,
    ) -> bool:
        """Log an action taken during a break-glass session.

        Args:
            username: The break-glass account username
            action_type: Type of action performed
            action_detail: Details of the action
            now: Current time (for testing)

        Returns:
            True if action was logged
        """
        action_time = now or datetime.now()

        if username not in self._active_sessions:
            return False

        session = self._active_sessions[username]
        if not session.is_active:
            return False

        session.add_action(
            action_type=action_type,
            description=action_detail,
            timestamp=action_time,
        )

        # Persist if repository available
        if self._log_repo:
            self._log_repo.save(session)

        # Log to audit
        if self._audit_logger:
            self._audit_logger.record_action(
                action_type="break_glass_action",
                actor=username,
                target=action_detail,
                details={
                    "session_id": session.session_id,
                    "action_type": action_type,
                    "action_count": session.action_count,
                },
            )

        return True

    def get_session_status(
        self,
        username: str,
    ) -> Optional[BreakGlassSessionStatus]:
        """Get the status of a break-glass session.

        Args:
            username: The break-glass account username

        Returns:
            BreakGlassSessionStatus or None if no session
        """
        if username not in self._active_sessions:
            # Try to load from repository
            if self._log_repo:
                session = self._log_repo.get_active_session(username)
                if session:
                    self._active_sessions[username] = session
                else:
                    return None
            else:
                return None

        session = self._active_sessions[username]
        expires_at = None
        if session.started_at:
            expires_at = session.started_at + timedelta(minutes=self._session_duration)

        return BreakGlassSessionStatus(
            session_id=session.session_id,
            account_username=session.username,
            started_at=session.started_at,
            expires_at=expires_at,
            action_count=session.action_count,
            is_active=session.is_active,
            justification=session.justification,
        )

    def get_audit_trail(
        self,
        username: str | None = None,
        session_id: str | None = None,
        since: datetime | None = None,
    ) -> List[BreakGlassAuditEntry]:
        """Get audit trail for break-glass usage.

        Args:
            username: Filter by account username
            session_id: Filter by session ID
            since: Only entries after this time

        Returns:
            List of audit entries
        """
        entries: List[BreakGlassAuditEntry] = []

        sessions = self._get_sessions_for_audit(username, session_id, since)
        for session in sessions:
            for action in session.actions:
                if since and action.timestamp < since:
                    continue

                entries.append(
                    BreakGlassAuditEntry(
                        session_id=session.session_id,
                        account_username=session.username,
                        action_type=action.action_type,
                        action_detail=action.description,
                        timestamp=action.timestamp,
                        justification=session.justification,
                    )
                )

        # Sort by timestamp
        entries.sort(key=lambda e: e.timestamp)
        return entries

    def get_available_break_glass_accounts(self) -> List[dict]:
        """Get list of available break-glass accounts.

        Returns:
            List of account info dictionaries
        """
        accounts = []

        if self._user_repo:
            try:
                users = self._user_repo.get_break_glass_accounts()
                for user in users:
                    is_available = user.account_status == AccountStatus.ACTIVE
                    has_active_session = (
                        user.username in self._active_sessions
                        and self._active_sessions[user.username].is_active
                    )

                    accounts.append(
                        {
                            "username": user.username,
                            "role": (
                                user.role.value
                                if hasattr(user.role, "value")
                                else str(user.role)
                            ),
                            "is_available": is_available and not has_active_session,
                            "has_active_session": has_active_session,
                            "status": user.account_status.value,
                        }
                    )
            except Exception:
                pass

        return accounts

    def _validate_justification(self, justification: str) -> Optional[str]:
        """Validate justification text.

        Returns error message or None if valid.
        """
        if not justification:
            return "justification is required"

        if not isinstance(justification, str):
            return "justification must be a string"

        justification = justification.strip()
        if len(justification) < self.MIN_JUSTIFICATION_LENGTH:
            return (
                f"justification must be at least "
                f"{self.MIN_JUSTIFICATION_LENGTH} characters"
            )

        return None

    def _get_user(self, username: str) -> Optional[UserAccount]:
        """Get a user account by username."""
        if self._user_repo is None:
            return None
        try:
            return self._user_repo.get_by_username(username)
        except Exception:
            return None

    def _get_sessions_for_audit(
        self,
        username: str | None,
        session_id: str | None,
        since: datetime | None,
    ) -> List[BreakGlassUsageLog]:
        """Get sessions for audit trail."""
        sessions: List[BreakGlassUsageLog] = []

        # Get from memory
        for session in self._active_sessions.values():
            if username and session.username != username:
                continue
            if session_id and session.session_id != session_id:
                continue
            if since and session.started_at and session.started_at < since:
                continue
            sessions.append(session)

        # Get from repository
        if self._log_repo:
            try:
                repo_sessions = self._log_repo.get_sessions(
                    username=username,
                    session_id=session_id,
                    since=since,
                )
                for session in repo_sessions:
                    if session.session_id not in [s.session_id for s in sessions]:
                        sessions.append(session)
            except Exception:
                pass

        return sessions


__all__ = [
    "BreakGlassActivationResult",
    "BreakGlassAuditEntry",
    "BreakGlassService",
    "BreakGlassSessionStatus",
]
