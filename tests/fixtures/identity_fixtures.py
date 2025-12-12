"""Identity fixture helpers for contract/integration tests.

These helpers centralize the sample rows referenced throughout
`specs/006-baseline-login-password`, giving future contract and integration
tests an easy way to seed pending users, blocked users, or default
preference bundles
without duplicating Argon2 hashing or metadata wiring logic.
"""

from __future__ import annotations

import json
import secrets
import sqlite3
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, MutableMapping, Tuple

from argon2.low_level import Type, hash_secret

DEFAULT_ARGON2_SETTINGS: Dict[str, int] = {
    "time_cost": 3,
    "memory_cost": 64 * 1024,
    "parallelism": 4,
    "hash_len": 32,
    "salt_len": 16,
}

PREFERENCE_SCHEMA_VERSION = 1
IDENTITY_SAMPLE_PASSWORD = "Dem0Acc3ss!42"
IDENTITY_PENDING_PASSWORD = "Pend1ngPass!"  # Already satisfies min length
# Used for blocked user fixture defaults
IDENTITY_LOCKED_PASSWORD = "L0ckedOut!!99"

_MFA_ACCOUNT_COLUMNS = {
    "mfa_enabled",
    "mfa_secret_encrypted",
    "mfa_recovery_codes",
    "mfa_enforced_at",
}

_MFA_RECOVERY_CODE_COLUMNS = {
    "code_id",
    "user_id",
    "code_hash",
    "issued_at",
    "redeemed_at",
    "revoked_at",
    "metadata",
}


def _utc_now() -> str:
    """Return an ISO-8601 timestamp in UTC without microseconds."""
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _json_or_null(value: Any | None) -> str | None:
    return None if value is None else json.dumps(value, sort_keys=True)


def hash_password(
    plaintext: str,
    *,
    salt: bytes | None = None,
) -> Tuple[str, bytes]:
    """Hash `plaintext` using the Argon2id parameters from research notes."""
    if not plaintext:
        raise ValueError("plaintext password must be non-empty")

    salt_bytes = salt or secrets.token_bytes(DEFAULT_ARGON2_SETTINGS["salt_len"])
    hashed = hash_secret(
        plaintext.encode("utf-8"),
        salt_bytes,
        time_cost=DEFAULT_ARGON2_SETTINGS["time_cost"],
        memory_cost=DEFAULT_ARGON2_SETTINGS["memory_cost"],
        parallelism=DEFAULT_ARGON2_SETTINGS["parallelism"],
        hash_len=DEFAULT_ARGON2_SETTINGS["hash_len"],
        type=Type.ID,
    )
    return hashed.decode("utf-8"), salt_bytes


@dataclass(slots=True)
class UserSeed:
    """Convenience wrapper for generating user_account style rows."""

    username: str
    plaintext_password: str = IDENTITY_SAMPLE_PASSWORD
    role: str = "standard"
    account_status: str = "active"
    share_preferences: bool = False
    login_attempts: int = 0
    registration_channel: str = "hub"
    preferences_id: str | None = None
    registration_metadata: Dict[str, Any] = field(default_factory=dict)
    mfa_enabled: bool = False
    mfa_secret_encrypted: bytes | None = None
    mfa_recovery_codes: list[str] | None = None
    mfa_enforced_at: str | None = None
    # Lockout prevention fields (Phase 3.8)
    is_always_available: bool = False
    is_break_glass: bool = False
    break_glass_justification: str | None = None
    auto_unblock_at: str | None = None

    def to_row(self) -> Dict[str, Any]:
        password_hash, salt = hash_password(self.plaintext_password)
        now = _utc_now()
        is_blocked = 1 if self.account_status == "blocked" else 0
        row = {
            "username": self.username,
            "password_hash": password_hash,
            "password_salt": salt,
            "role": self.role,
            "account_status": self.account_status,
            "is_blocked": is_blocked,
            "login_attempts": self.login_attempts,
            "last_login": None,
            "last_failed_login": None,
            "preferences_id": self.preferences_id,
            "share_preferences": 1 if self.share_preferences else 0,
            "registration_channel": self.registration_channel,
            "registration_metadata": _json_or_null(
                self.registration_metadata or {"source": self.registration_channel}
            ),
            "created_at": now,
            "activated_at": None,
            "blocked_at": now if is_blocked else None,
            "updated_at": now,
            "enforced_password_change": 0,
            "mfa_enabled": 1 if self.mfa_enabled else 0,
            "mfa_secret_encrypted": self.mfa_secret_encrypted,
            "mfa_recovery_codes": _json_or_null(self.mfa_recovery_codes),
            "mfa_enforced_at": self.mfa_enforced_at,
            # Lockout prevention fields
            "is_always_available": 1 if self.is_always_available else 0,
            "is_break_glass": 1 if self.is_break_glass else 0,
            "break_glass_justification": self.break_glass_justification,
            "auto_unblock_at": self.auto_unblock_at,
        }
        return row


def seed_active_user(
    username: str = "demo",
    *,
    role: str = "standard",
    preferences_id: str | None = None,
) -> Dict[str, Any]:
    """Return an active user row ready for insertion/mocking."""
    return UserSeed(
        username=username, role=role, preferences_id=preferences_id
    ).to_row()


def seed_pending_user(username: str = "pending_user") -> Dict[str, Any]:
    """Return a pending registration row using the shared Argon2 defaults."""
    return UserSeed(
        username=username,
        plaintext_password=IDENTITY_PENDING_PASSWORD,
        account_status="pending",
        login_attempts=0,
    ).to_row()


def seed_blocked_user(
    username: str = "blocked_user",
    *,
    attempts: int = 5,
) -> Dict[str, Any]:
    """Return a blocked user row capped at the lockout attempt ceiling."""
    return UserSeed(
        username=username,
        plaintext_password=IDENTITY_LOCKED_PASSWORD,
        account_status="blocked",
        login_attempts=max(attempts, 5),
    ).to_row()


def seed_mfa_enabled_user(
    username: str = "mfa_demo",
    *,
    preferences_id: str | None = None,
    recovery_codes: list[str] | None = None,
    secret_bytes: bytes | None = None,
    enforced_at: str | None = None,
    plaintext_password: str = IDENTITY_SAMPLE_PASSWORD,
) -> Dict[str, Any]:
    """Return a user row with MFA columns populated."""

    codes = recovery_codes or [f"RC-{secrets.token_hex(3)}" for _ in range(5)]
    secret = secret_bytes or secrets.token_bytes(32)
    enforced_ts = enforced_at or _utc_now()
    return UserSeed(
        username=username,
        plaintext_password=plaintext_password,
        preferences_id=preferences_id,
        mfa_enabled=True,
        mfa_secret_encrypted=secret,
        mfa_recovery_codes=codes,
        mfa_enforced_at=enforced_ts,
    ).to_row()


def preference_payload(
    user_id: str,
    *,
    share_enabled: bool = False,
    overrides: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """Generate a baseline preference payload (JSON-ready dict)."""
    payload: Dict[str, Any] = {
        "layout": "default",
        "favorite_tools": ["file_finder", "size_analyzer"],
        "share_preferences": share_enabled,
        "metadata": {
            "purpose": "team sync" if share_enabled else "personal",
            "shared_by": user_id if share_enabled else None,
            "timestamp": _utc_now(),
        },
    }
    if overrides:
        payload.update(overrides)
    return payload


def preference_record(
    user_id: str,
    *,
    preferences_id: str | None = None,
    share_enabled: bool = False,
    schema_version: int = PREFERENCE_SCHEMA_VERSION,
    overrides: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """Build a `user_preferences` row aligned with the migration schema."""
    pref_id = preferences_id or f"pref_{user_id}_{secrets.token_hex(3)}"
    payload_dict = preference_payload(
        user_id, share_enabled=share_enabled, overrides=overrides
    )
    timestamp = _utc_now()
    return {
        "preferences_id": pref_id,
        "user_id": user_id,
        "schema_version": schema_version,
        "payload": json.dumps(payload_dict, sort_keys=True),
        "is_encrypted": 0,
        "metadata": _json_or_null({"generated_at": timestamp}),
        "shared_metadata": _json_or_null(payload_dict.get("metadata")),
        "created_at": timestamp,
        "updated_at": timestamp,
    }


def attach_preferences(
    user_row: MutableMapping[str, Any],
    preference_row: MutableMapping[str, Any],
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Link a user + preference bundle and return tuple copies."""
    combined_user = dict(user_row)
    combined_pref = dict(preference_row)
    combined_user["preferences_id"] = combined_pref["preferences_id"]
    return combined_user, combined_pref


def session_record(
    user_id: str,
    *,
    session_handle: str | None = None,
    surface: str = "gui",
    revoked: bool = False,
    preferences_id: str | None = None,
    issued_at: str | None = None,
    last_activity_at: str | None = None,
    expires_at: str | None = None,
    idle_timeout_deadline: str | None = None,
    origin_host: str = "localhost",
    revoked_at: str | None = None,
) -> Dict[str, Any]:
    """Generate a `session_tokens` compatible row for integration tests."""

    now = _utc_now()
    handle = session_handle or f"session_{uuid.uuid4().hex}"
    issued_ts = issued_at or now
    last_activity_ts = last_activity_at or now
    expires_ts = expires_at or now
    idle_deadline_ts = idle_timeout_deadline or now
    revoked_ts = revoked_at or (now if revoked else None)
    return {
        "session_handle_hash": handle,
        "user_id": user_id,
        "issued_at": issued_ts,
        "last_activity_at": last_activity_ts,
        "expires_at": expires_ts,
        "surface": surface,
        "origin_host": origin_host,
        "revoked": 1 if revoked else 0,
        "revoked_at": revoked_ts,
        "preferences_id": preferences_id,
        "idle_timeout_deadline": idle_deadline_ts,
    }


def mfa_recovery_code_record(
    user_id: str,
    *,
    code_id: str | None = None,
    recovery_code: str | None = None,
    issued_at: str | None = None,
    redeemed_at: str | None = None,
    revoked_at: str | None = None,
    metadata: Dict[str, Any] | None = None,
) -> Tuple[Dict[str, Any], str]:
    """Build a user_mfa_recovery_codes row and return it with the raw code."""

    code_value = recovery_code or secrets.token_urlsafe(10)
    hashed_value, _ = hash_password(code_value)
    issued_ts = issued_at or _utc_now()
    record = {
        "code_id": code_id or f"code_{uuid.uuid4().hex}",
        "user_id": user_id,
        "code_hash": hashed_value,
        "issued_at": issued_ts,
        "redeemed_at": redeemed_at,
        "revoked_at": revoked_at,
        "metadata": _json_or_null(metadata),
    }
    return record, code_value


def _table_columns(conn: sqlite3.Connection, table_name: str) -> set[str]:
    cursor = conn.execute(f"PRAGMA table_info({table_name});")
    return {row[1] for row in cursor.fetchall()}


def _table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    cursor = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,),
    )
    return cursor.fetchone() is not None


def assert_mfa_schema_ready(conn: sqlite3.Connection) -> None:
    """Ensure MFA columns/tables exist before seeding fixtures.

    Tests call this helper once migrations run to catch drift early instead of
    waiting for repository failures when MFA readiness toggles resume.
    """

    account_columns = _table_columns(conn, "user_accounts")
    missing_account = _MFA_ACCOUNT_COLUMNS - account_columns
    if missing_account:
        formatted = ", ".join(sorted(missing_account))
        raise AssertionError(
            "user_accounts missing MFA columns: {columns}".format(columns=formatted)
        )

    if not _table_exists(conn, "user_mfa_recovery_codes"):
        raise AssertionError("user_mfa_recovery_codes table must exist for MFA")

    recovery_columns = _table_columns(conn, "user_mfa_recovery_codes")
    missing_recovery = _MFA_RECOVERY_CODE_COLUMNS - recovery_columns
    if missing_recovery:
        formatted = ", ".join(sorted(missing_recovery))
        raise AssertionError(
            "user_mfa_recovery_codes missing columns: {columns}".format(
                columns=formatted
            )
        )


__all__ = [
    "DEFAULT_ARGON2_SETTINGS",
    "IDENTITY_SAMPLE_PASSWORD",
    "IDENTITY_PENDING_PASSWORD",
    "IDENTITY_LOCKED_PASSWORD",
    "UserSeed",
    "hash_password",
    "seed_active_user",
    "seed_pending_user",
    "seed_blocked_user",
    "seed_mfa_enabled_user",
    "preference_payload",
    "preference_record",
    "attach_preferences",
    "session_record",
    "mfa_recovery_code_record",
    "assert_mfa_schema_ready",
]
