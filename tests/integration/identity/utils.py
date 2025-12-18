"""Shared helpers for identity integration tests derived from quickstart flows."""

from __future__ import annotations

import importlib
import sqlite3
from pathlib import Path
from typing import Any, Callable, Dict, Protocol

from tests.fixtures.identity_fixtures import (
    UserSeed,
    attach_preferences,
    preference_record,
    session_record,
)

MIGRATION_FILE = Path("scripts/migrations/006_baseline_login_password.sql")


class CommandResultProtocol(Protocol):
    exit_code: int
    payload: Any | None


def ensure_schema_version_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS rfu_schema_version (
            version INTEGER PRIMARY KEY,
            applied_at TEXT NOT NULL,
            description TEXT
        )
        """
    )


def apply_identity_schema(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys=ON;")
    ensure_schema_version_table(conn)
    if not MIGRATION_FILE.exists():
        raise FileNotFoundError(
            "Expected migration file at "
            "scripts/migrations/006_baseline_login_password.sql"
        )
    script = MIGRATION_FILE.read_text(encoding="utf-8")
    conn.executescript(script)
    conn.commit()
    conn.close()


def insert_user(conn: sqlite3.Connection, user_row: Dict[str, Any]) -> None:
    conn.execute(
        """
        INSERT INTO user_accounts (
            username,
            password_hash,
            password_salt,
            role,
            account_status,
            is_blocked,
            login_attempts,
            last_login,
            last_failed_login,
            preferences_id,
            share_preferences,
            registration_channel,
            registration_metadata,
            created_at,
            activated_at,
            blocked_at,
            updated_at,
            enforced_password_change,
            is_always_available,
            is_break_glass,
            break_glass_justification,
            auto_unblock_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_row["username"],
            user_row["password_hash"],
            sqlite3.Binary(user_row["password_salt"]),
            user_row["role"],
            user_row["account_status"],
            user_row["is_blocked"],
            user_row["login_attempts"],
            user_row["last_login"],
            user_row["last_failed_login"],
            user_row["preferences_id"],
            user_row["share_preferences"],
            user_row["registration_channel"],
            user_row["registration_metadata"],
            user_row["created_at"],
            user_row["activated_at"],
            user_row["blocked_at"],
            user_row["updated_at"],
            user_row["enforced_password_change"],
            user_row.get("is_always_available", 0),
            user_row.get("is_break_glass", 0),
            user_row.get("break_glass_justification"),
            user_row.get("auto_unblock_at"),
        ),
    )


def insert_preference(
    conn: sqlite3.Connection,
    pref_row: Dict[str, Any],
) -> None:
    conn.execute(
        """
        INSERT INTO user_preferences (
            preferences_id,
            user_id,
            schema_version,
            payload,
            is_encrypted,
            metadata,
            shared_metadata,
            created_at,
            updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            pref_row["preferences_id"],
            pref_row["user_id"],
            pref_row["schema_version"],
            pref_row["payload"],
            pref_row["is_encrypted"],
            pref_row["metadata"],
            pref_row["shared_metadata"],
            pref_row["created_at"],
            pref_row["updated_at"],
        ),
    )


def insert_session(
    conn: sqlite3.Connection,
    session_row: Dict[str, Any],
) -> None:
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
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            session_row["session_handle_hash"],
            session_row["user_id"],
            session_row["issued_at"],
            session_row["last_activity_at"],
            session_row["expires_at"],
            session_row["surface"],
            session_row["origin_host"],
            session_row["revoked"],
            session_row["revoked_at"],
            session_row["preferences_id"],
            session_row["idle_timeout_deadline"],
        ),
    )


def build_user(
    *,
    username: str,
    plaintext: str,
    role: str = "standard",
    status: str = "active",
    login_attempts: int = 0,
    share_preferences: bool = False,
    preferences_id: str | None = None,
    is_always_available: bool = False,
    is_break_glass: bool = False,
) -> Dict[str, Any]:
    seed = UserSeed(
        username=username,
        plaintext_password=plaintext,
        role=role,
        account_status=status,
        login_attempts=login_attempts,
        share_preferences=share_preferences,
        preferences_id=preferences_id,
        is_always_available=is_always_available,
        is_break_glass=is_break_glass,
    )
    return seed.to_row()


def attach_default_preferences(
    user_row: Dict[str, Any],
    *,
    preferences_id: str | None = None,
    share_enabled: bool = False,
) -> tuple[Dict[str, Any], Dict[str, Any]]:
    pref_id = preferences_id or f"pref_{user_row['username']}"
    return attach_preferences(
        user_row,
        preference_record(
            user_row["username"],
            preferences_id=pref_id,
            share_enabled=share_enabled,
        ),
    )


def build_session_token(
    user_id: str,
    *,
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
    return session_record(
        user_id,
        surface=surface,
        revoked=revoked,
        preferences_id=preferences_id,
        issued_at=issued_at,
        last_activity_at=last_activity_at,
        expires_at=expires_at,
        idle_timeout_deadline=idle_timeout_deadline,
        origin_host=origin_host,
        revoked_at=revoked_at,
    )


def load_symbol(module_path: str, attribute: str, guidance: str = "") -> Any:
    try:
        module = importlib.import_module(module_path)
    except ModuleNotFoundError as exc:
        raise AssertionError(
            f"Module {module_path} must exist for identity integration tests"
        ) from exc
    try:
        return getattr(module, attribute)
    except AttributeError as exc:
        hint = f" ({guidance})" if guidance else ""
        raise AssertionError(
            f"{module_path}.{attribute} is required for identity "
            f"integration tests{hint}"
        ) from exc


def load_callable(
    module_path: str,
    attribute: str,
    guidance: str = "",
) -> Callable[..., Any]:
    symbol = load_symbol(module_path, attribute, guidance)
    if not callable(symbol):
        raise AssertionError(
            f"{module_path}.{attribute} must be callable for integration tests"
        )
    return symbol


def expect_command_success(result: CommandResultProtocol | Any) -> Any:
    exit_code = getattr(result, "exit_code", None)
    assert exit_code == 0, "RFU admin CLI must return exit_code=0 on success"
    return getattr(result, "payload", None)
