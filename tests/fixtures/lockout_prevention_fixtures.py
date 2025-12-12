"""Fixtures for lockout prevention testing.

Provides helpers to seed:
- Always-available accounts (dev + admin)
- Break-glass accounts (dev + admin)
- Standard accounts with each of the four roles
- Blocked accounts in cooldown state
"""

from __future__ import annotations

import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, List

# Protected account usernames (canonical names from spec)
ALWAYS_AVAILABLE_DEV = "rfu_dev_always"
ALWAYS_AVAILABLE_ADMIN = "rfu_admin_always"
BREAK_GLASS_DEV = "rfu_dev_breakglass"
BREAK_GLASS_ADMIN = "rfu_admin_breakglass"

# Default test password (only for fixtures, never in production)
DEFAULT_TEST_PASSWORD_HASH = (
    "$argon2id$v=19$m=65536,t=3,p=4$" "dGVzdHNhbHQxMjM0NTY$testhashabcdef1234567890"
)


def generate_session_id() -> str:
    """Generate a unique session ID for testing."""
    return f"test_session_{secrets.token_hex(8)}"


def seed_always_available_dev(
    database_path: str | None = None,
    active: bool = True,
) -> Dict[str, Any]:
    """Create an always-available dev account record.

    Args:
        database_path: If provided, insert into database
        active: Whether account should be active (vs blocked in cooldown)

    Returns:
        Account record dictionary
    """
    now = datetime.now()
    record = {
        "username": ALWAYS_AVAILABLE_DEV,
        "password_hash": DEFAULT_TEST_PASSWORD_HASH,
        "password_salt": None,
        "role": "dev",
        "account_status": "active" if active else "blocked",
        "login_attempts": 0 if active else 5,
        "is_blocked": 0 if active else 1,
        "preferences_id": f"pref_{ALWAYS_AVAILABLE_DEV}",
        "share_preferences": 0,
        "registration_channel": "bootstrap",
        "registration_metadata": None,
        "created_at": now.isoformat(),
        "activated_at": now.isoformat() if active else None,
        "blocked_at": None if active else now.isoformat(),
        "is_always_available": 1,
        "is_break_glass": 0,
        "break_glass_justification": None,
        "auto_unblock_at": (
            None if active else (now + timedelta(minutes=5)).isoformat()
        ),
    }

    if database_path:
        _insert_user_record(database_path, record)

    return record


def seed_always_available_admin(
    database_path: str | None = None,
    active: bool = True,
) -> Dict[str, Any]:
    """Create an always-available admin account record."""
    now = datetime.now()
    record = {
        "username": ALWAYS_AVAILABLE_ADMIN,
        "password_hash": DEFAULT_TEST_PASSWORD_HASH,
        "password_salt": None,
        "role": "admin",
        "account_status": "active" if active else "blocked",
        "login_attempts": 0 if active else 5,
        "is_blocked": 0 if active else 1,
        "preferences_id": f"pref_{ALWAYS_AVAILABLE_ADMIN}",
        "share_preferences": 0,
        "registration_channel": "bootstrap",
        "registration_metadata": None,
        "created_at": now.isoformat(),
        "activated_at": now.isoformat() if active else None,
        "blocked_at": None if active else now.isoformat(),
        "is_always_available": 1,
        "is_break_glass": 0,
        "break_glass_justification": None,
        "auto_unblock_at": (
            None if active else (now + timedelta(minutes=5)).isoformat()
        ),
    }

    if database_path:
        _insert_user_record(database_path, record)

    return record


def seed_break_glass_dev(
    database_path: str | None = None,
    active: bool = True,
) -> Dict[str, Any]:
    """Create a break-glass dev account record."""
    now = datetime.now()
    record = {
        "username": BREAK_GLASS_DEV,
        "password_hash": DEFAULT_TEST_PASSWORD_HASH,
        "password_salt": None,
        "role": "dev",
        "account_status": "active" if active else "disabled",
        "login_attempts": 0,
        "is_blocked": 0,
        "preferences_id": f"pref_{BREAK_GLASS_DEV}",
        "share_preferences": 0,
        "registration_channel": "bootstrap",
        "registration_metadata": None,
        "created_at": now.isoformat(),
        "activated_at": now.isoformat() if active else None,
        "is_always_available": 0,
        "is_break_glass": 1,
        "break_glass_justification": None,
        "auto_unblock_at": None,
    }

    if database_path:
        _insert_user_record(database_path, record)

    return record


def seed_break_glass_admin(
    database_path: str | None = None,
    active: bool = True,
) -> Dict[str, Any]:
    """Create a break-glass admin account record."""
    now = datetime.now()
    record = {
        "username": BREAK_GLASS_ADMIN,
        "password_hash": DEFAULT_TEST_PASSWORD_HASH,
        "password_salt": None,
        "role": "admin",
        "account_status": "active" if active else "disabled",
        "login_attempts": 0,
        "is_blocked": 0,
        "preferences_id": f"pref_{BREAK_GLASS_ADMIN}",
        "share_preferences": 0,
        "registration_channel": "bootstrap",
        "registration_metadata": None,
        "created_at": now.isoformat(),
        "activated_at": now.isoformat() if active else None,
        "is_always_available": 0,
        "is_break_glass": 1,
        "break_glass_justification": None,
        "auto_unblock_at": None,
    }

    if database_path:
        _insert_user_record(database_path, record)

    return record


def seed_standard_user(
    username: str,
    role: str = "user",
    database_path: str | None = None,
    active: bool = True,
    blocked: bool = False,
) -> Dict[str, Any]:
    """Create a standard (non-protected) user account record.

    Args:
        username: Account username
        role: One of dev, admin, user, readonly
        database_path: If provided, insert into database
        active: Whether account is active
        blocked: Whether account is blocked

    Returns:
        Account record dictionary
    """
    now = datetime.now()
    status = (
        "active" if active and not blocked else ("blocked" if blocked else "pending")
    )

    record = {
        "username": username,
        "password_hash": DEFAULT_TEST_PASSWORD_HASH,
        "password_salt": None,
        "role": role,
        "account_status": status,
        "login_attempts": 5 if blocked else 0,
        "is_blocked": 1 if blocked else 0,
        "preferences_id": f"pref_{username}",
        "share_preferences": 0,
        "registration_channel": "cli",
        "registration_metadata": None,
        "created_at": now.isoformat(),
        "activated_at": now.isoformat() if active else None,
        "blocked_at": now.isoformat() if blocked else None,
        "is_always_available": 0,
        "is_break_glass": 0,
        "break_glass_justification": None,
        "auto_unblock_at": None,
    }

    if database_path:
        _insert_user_record(database_path, record)

    return record


def seed_blocked_in_cooldown(
    username: str = ALWAYS_AVAILABLE_ADMIN,
    cooldown_minutes: int = 5,
    elapsed_minutes: int = 2,
    database_path: str | None = None,
) -> Dict[str, Any]:
    """Create an always-available account in cooldown state.

    Args:
        username: Account username
        cooldown_minutes: Total cooldown duration
        elapsed_minutes: How much time has passed since block
        database_path: If provided, insert into database

    Returns:
        Account record dictionary with cooldown timestamps
    """
    now = datetime.now()
    blocked_at = now - timedelta(minutes=elapsed_minutes)
    auto_unblock_at = blocked_at + timedelta(minutes=cooldown_minutes)

    record = {
        "username": username,
        "password_hash": DEFAULT_TEST_PASSWORD_HASH,
        "password_salt": None,
        "role": "admin",
        "account_status": "blocked",
        "login_attempts": 5,
        "is_blocked": 1,
        "preferences_id": f"pref_{username}",
        "share_preferences": 0,
        "registration_channel": "bootstrap",
        "registration_metadata": None,
        "created_at": (now - timedelta(days=30)).isoformat(),
        "activated_at": (now - timedelta(days=30)).isoformat(),
        "blocked_at": blocked_at.isoformat(),
        "is_always_available": 1,
        "is_break_glass": 0,
        "break_glass_justification": None,
        "auto_unblock_at": auto_unblock_at.isoformat(),
    }

    if database_path:
        _insert_user_record(database_path, record)

    return record


def seed_all_protected_accounts(
    database_path: str | None = None,
) -> List[Dict[str, Any]]:
    """Seed all four protected accounts.

    Returns:
        List of account records
    """
    accounts = [
        seed_always_available_dev(database_path),
        seed_always_available_admin(database_path),
        seed_break_glass_dev(database_path),
        seed_break_glass_admin(database_path),
    ]
    return accounts


def seed_role_test_accounts(
    database_path: str | None = None,
) -> Dict[str, Dict[str, Any]]:
    """Seed one account for each role.

    Returns:
        Dictionary mapping role name to account record
    """
    roles = ["dev", "admin", "user", "readonly"]
    accounts = {}
    for role in roles:
        username = f"test_{role}_user"
        accounts[role] = seed_standard_user(
            username=username,
            role=role,
            database_path=database_path,
        )
    return accounts


def break_glass_usage_log_record(
    session_id: str | None = None,
    username: str = BREAK_GLASS_ADMIN,
    justification: str = "Emergency recovery testing",
    actions: List[Dict[str, Any]] | None = None,
    logout: bool = False,
) -> Dict[str, Any]:
    """Create a break-glass usage log record.

    Args:
        session_id: Session identifier (auto-generated if None)
        username: Break-glass account username
        justification: Reason for break-glass access
        actions: List of action entries
        logout: Whether to include logout timestamp

    Returns:
        Usage log record dictionary
    """
    now = datetime.now()
    sid = session_id or generate_session_id()

    record = {
        "session_id": sid,
        "account_username": username,
        "login_timestamp": now.isoformat(),
        "logout_timestamp": now.isoformat() if logout else None,
        "justification": justification,
        "actions_performed": actions or [],
        "post_usage_rotation_status": "pending" if logout else "not_required",
        "client_ip": "127.0.0.1",
        "client_hostname": "localhost",
        "created_at": now.isoformat(),
    }

    return record


def always_available_config_record(
    username: str = ALWAYS_AVAILABLE_ADMIN,
    cooldown_minutes: int = 5,
    in_cooldown: bool = False,
) -> Dict[str, Any]:
    """Create an always-available account config record.

    Args:
        username: Account username
        cooldown_minutes: Cooldown duration in minutes
        in_cooldown: Whether currently in cooldown state

    Returns:
        Config record dictionary
    """
    now = datetime.now()

    record = {
        "username": username,
        "last_cooldown_start": (
            (now - timedelta(minutes=2)).isoformat() if in_cooldown else None
        ),
        "cooldown_duration_minutes": cooldown_minutes,
        "auto_unblock_enabled": 1,
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
    }

    return record


def _insert_user_record(database_path: str, record: Dict[str, Any]) -> None:
    """Insert a user record into the database.

    Note: This is a simple helper for fixture setup. Production code
    should use the repository pattern.
    """
    import sqlite3

    conn = sqlite3.connect(database_path)
    try:
        cursor = conn.cursor()

        # Build INSERT statement dynamically
        columns = list(record.keys())
        placeholders = ["?" for _ in columns]

        sql = f"""
            INSERT OR REPLACE INTO user_accounts ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
        """

        values = [record[col] for col in columns]
        cursor.execute(sql, values)
        conn.commit()
    finally:
        conn.close()


__all__ = [
    "ALWAYS_AVAILABLE_ADMIN",
    "ALWAYS_AVAILABLE_DEV",
    "BREAK_GLASS_ADMIN",
    "BREAK_GLASS_DEV",
    "always_available_config_record",
    "break_glass_usage_log_record",
    "generate_session_id",
    "seed_all_protected_accounts",
    "seed_always_available_admin",
    "seed_always_available_dev",
    "seed_blocked_in_cooldown",
    "seed_break_glass_admin",
    "seed_break_glass_dev",
    "seed_role_test_accounts",
    "seed_standard_user",
]
