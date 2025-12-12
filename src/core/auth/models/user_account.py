"""User account dataclass matching the baseline auth tables."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any, Dict, Mapping, Sequence

from .utils import (
    bool_from_db,
    dict_to_json,
    json_to_dict,
    json_to_list,
    list_to_json,
    parse_datetime,
)


class UserRole(StrEnum):
    """Four-role system: dev > admin > user > readonly."""

    DEV = "dev"
    ADMIN = "admin"
    USER = "user"
    READONLY = "readonly"

    # Legacy alias for backward compatibility during migration
    STANDARD = "user"

    @classmethod
    def from_db(cls, value: str | None) -> "UserRole":
        normalized = (value or cls.USER.value).strip().lower()
        alias_map = {
            "dev": cls.DEV,
            "developer": cls.DEV,
            "admin": cls.ADMIN,
            "administrator": cls.ADMIN,
            "user": cls.USER,
            "standard": cls.USER,  # Migration: standard → user
            "readonly": cls.READONLY,
            "read_only": cls.READONLY,
        }
        return alias_map.get(normalized, cls.USER)

    @property
    def privilege_level(self) -> int:
        """Return privilege level for hierarchy comparisons."""
        levels = {
            UserRole.DEV: 4,
            UserRole.ADMIN: 3,
            UserRole.USER: 2,
            UserRole.READONLY: 1,
        }
        return levels.get(self, 2)

    def has_at_least(self, required: "UserRole") -> bool:
        """Check if this role meets or exceeds required level."""
        return self.privilege_level >= required.privilege_level


class AccountStatus(StrEnum):
    ACTIVE = "active"
    PENDING = "pending"
    BLOCKED = "blocked"
    DISABLED = "disabled"

    @classmethod
    def from_db(cls, value: str | None) -> "AccountStatus":
        normalized = (value or cls.PENDING.value).strip().lower()
        alias_map = {
            "active": cls.ACTIVE,
            "pending": cls.PENDING,
            "pending_activation": cls.PENDING,
            "locked": cls.BLOCKED,
            "blocked": cls.BLOCKED,
            "disabled": cls.DISABLED,
        }
        return alias_map.get(normalized, cls.PENDING)


class RegistrationChannel(StrEnum):
    HUB = "hub"
    GUI = "gui"
    CLI = "cli"
    BOOTSTRAP = "bootstrap"

    @classmethod
    def from_db(cls, value: str | None) -> "RegistrationChannel":
        normalized = (value or cls.HUB.value).strip().lower()
        alias_map = {
            "hub": cls.HUB,
            "gui": cls.GUI,
            "cli": cls.CLI,
            "bootstrap": cls.BOOTSTRAP,
            "service": cls.HUB,
            "portal": cls.GUI,
        }
        return alias_map.get(normalized, cls.HUB)


def _coerce_bytes(value: Any) -> bytes | None:
    if value is None:
        return None
    if isinstance(value, memoryview):
        return value.tobytes()
    if isinstance(value, (bytes, bytearray)):
        return bytes(value)
    return str(value).encode("utf-8")


@dataclass(slots=True)
class UserAccount:
    username: str
    password_hash: str
    password_salt: bytes | None = None
    role: UserRole = UserRole.USER
    account_status: AccountStatus = AccountStatus.PENDING
    login_attempts: int = 0
    is_blocked: bool = False
    preferences_id: str | None = None
    share_preferences: bool = False
    registration_channel: RegistrationChannel = RegistrationChannel.HUB
    registration_metadata: Dict[str, Any] | None = None
    created_at: datetime | None = None
    activated_at: datetime | None = None
    blocked_at: datetime | None = None
    updated_at: datetime | None = None
    last_login: datetime | None = None
    last_failed_login: datetime | None = None
    reset_required: bool = False
    mfa_enabled: bool = False
    mfa_secret_encrypted: bytes | None = None
    mfa_recovery_codes: Sequence[str] = field(default_factory=tuple)
    mfa_enforced_at: datetime | None = None
    # Lockout prevention fields (007-upgrade-to-login)
    is_always_available: bool = False
    is_break_glass: bool = False
    break_glass_justification: str | None = None
    auto_unblock_at: datetime | None = None

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> "UserAccount":
        metadata = json_to_dict(row.get("registration_metadata"))
        recovery_codes = json_to_list(row.get("mfa_recovery_codes")) or ()
        reset_flag = row.get(
            "reset_required",
            row.get("enforced_password_change"),
        )
        return cls(
            username=row["username"],
            password_hash=row["password_hash"],
            password_salt=_coerce_bytes(row.get("password_salt")),
            role=UserRole.from_db(row.get("role")),
            account_status=AccountStatus.from_db(row.get("account_status")),
            login_attempts=int(row.get("login_attempts") or 0),
            is_blocked=bool_from_db(row.get("is_blocked")),
            preferences_id=row.get("preferences_id"),
            share_preferences=bool_from_db(row.get("share_preferences")),
            registration_channel=RegistrationChannel.from_db(
                row.get("registration_channel")
            ),
            registration_metadata=metadata,
            created_at=parse_datetime(row.get("created_at")),
            activated_at=parse_datetime(row.get("activated_at")),
            blocked_at=parse_datetime(row.get("blocked_at")),
            updated_at=parse_datetime(row.get("updated_at")),
            last_login=parse_datetime(row.get("last_login")),
            last_failed_login=parse_datetime(row.get("last_failed_login")),
            reset_required=bool_from_db(reset_flag),
            mfa_enabled=bool_from_db(row.get("mfa_enabled")),
            mfa_secret_encrypted=_coerce_bytes(row.get("mfa_secret_encrypted")),
            mfa_recovery_codes=recovery_codes,
            mfa_enforced_at=parse_datetime(row.get("mfa_enforced_at")),
            is_always_available=bool_from_db(row.get("is_always_available")),
            is_break_glass=bool_from_db(row.get("is_break_glass")),
            break_glass_justification=row.get("break_glass_justification"),
            auto_unblock_at=parse_datetime(row.get("auto_unblock_at")),
        )

    def to_record(self) -> Dict[str, Any]:
        return {
            "username": self.username,
            "password_hash": self.password_hash,
            "password_salt": self.password_salt,
            "role": self.role.value,
            "account_status": self.account_status.value,
            "login_attempts": self.login_attempts,
            "is_blocked": int(self.is_blocked),
            "preferences_id": self.preferences_id,
            "share_preferences": int(self.share_preferences),
            "registration_channel": self.registration_channel.value,
            "registration_metadata": dict_to_json(self.registration_metadata),
            "created_at": self.created_at,
            "activated_at": self.activated_at,
            "blocked_at": self.blocked_at,
            "updated_at": self.updated_at,
            "last_login": self.last_login,
            "last_failed_login": self.last_failed_login,
            "enforced_password_change": int(self.reset_required),
            "mfa_enabled": int(self.mfa_enabled),
            "mfa_secret_encrypted": self.mfa_secret_encrypted,
            "mfa_recovery_codes": list_to_json(self.mfa_recovery_codes),
            "mfa_enforced_at": self.mfa_enforced_at,
            "is_always_available": int(self.is_always_available),
            "is_break_glass": int(self.is_break_glass),
            "break_glass_justification": self.break_glass_justification,
            "auto_unblock_at": self.auto_unblock_at,
        }

    @property
    def is_pending(self) -> bool:
        return self.account_status == AccountStatus.PENDING

    @property
    def is_active(self) -> bool:
        return self.account_status == AccountStatus.ACTIVE

    @property
    def is_disabled(self) -> bool:
        return self.account_status == AccountStatus.DISABLED

    @property
    def is_protected(self) -> bool:
        """True if always-available or break-glass account."""
        return self.is_always_available or self.is_break_glass

    @property
    def can_be_deleted(self) -> bool:
        """Return False if account is protected from deletion."""
        return not self.is_protected

    @property
    def can_be_permanently_blocked(self) -> bool:
        """Return False if account is always-available (uses cooldown)."""
        return not self.is_always_available

    @property
    def preferences_user_id(self) -> str | None:
        return self.preferences_id

    @preferences_user_id.setter
    def preferences_user_id(self, value: str | None) -> None:
        self.preferences_id = value


__all__ = [
    "AccountStatus",
    "RegistrationChannel",
    "UserAccount",
    "UserRole",
]
