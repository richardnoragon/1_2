"""Authentication data model exports."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .admin_action_audit import (
    AdminActionAudit,
    AdminActionSurface,
    AdminActionType,
)
from .reset_request import (
    ResetChannel,
    ResetOriginSurface,
    ResetRequest,
    ResetStatus,
)
from .session_token import SessionSurface, SessionToken
from .user_account import (
    AccountStatus,
    RegistrationChannel,
    UserAccount,
    UserRole,
)


@dataclass(slots=True)
class AuthSession:
    """Result of a successful authentication."""

    username: str
    role: str
    preferences_user_id: str | None
    reset_required: bool = False
    session_id: str | None = None
    issued_at: datetime | None = None
    expires_at: datetime | None = None
    session_type: str = "standard"  # 'standard', 'break_glass'

    @property
    def is_break_glass(self) -> bool:
        """True if this is a break-glass emergency session."""
        return self.session_type == "break_glass"

    @classmethod
    def from_account(
        cls,
        account: UserAccount,
        *,
        session_id: str | None = None,
        issued_at: datetime | None = None,
        expires_at: datetime | None = None,
        session_type: str = "standard",
    ) -> "AuthSession":
        return cls(
            username=account.username,
            role=account.role.value,
            preferences_user_id=account.preferences_user_id,
            reset_required=account.reset_required,
            session_id=session_id,
            issued_at=issued_at,
            expires_at=expires_at,
            session_type=session_type,
        )


__all__ = [
    "AccountStatus",
    "AdminActionAudit",
    "AdminActionSurface",
    "AdminActionType",
    "AuthSession",
    "RegistrationChannel",
    "ResetChannel",
    "ResetOriginSurface",
    "ResetRequest",
    "ResetStatus",
    "SessionSurface",
    "SessionToken",
    "UserAccount",
    "UserRole",
]
