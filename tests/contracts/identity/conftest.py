"""Shared fixtures for identity contract tests.

The contract suite spins up a temporary SQLite database using migration
`006_baseline_login_password.sql`, seeds representative identity rows, and then
loads the future controllers under test via dynamic imports. This keeps the
contract expectations close to the OpenAPI definition in
`specs/006-baseline-login-password/contracts/authentication.yaml`.
"""

from __future__ import annotations

import importlib
import shutil
import sqlite3
from pathlib import Path
from typing import Any, Dict

import pytest

from tests.fixtures.identity_fixtures import (
    IDENTITY_LOCKED_PASSWORD,
    IDENTITY_PENDING_PASSWORD,
    IDENTITY_SAMPLE_PASSWORD,
    UserSeed,
    assert_mfa_schema_ready,
    attach_preferences,
    preference_record,
)

MIGRATION_FILE = Path("scripts/migrations/006_baseline_login_password.sql")

CONTRACT_ACCOUNTS: Dict[str, Dict[str, Any]] = {
    "demo_active": {
        "username": "demo_active",
        "password": IDENTITY_SAMPLE_PASSWORD,
        "preferences_id": "pref_demo_active",
    },
    "lockout_user": {
        "username": "lockout_candidate",
        "password": IDENTITY_LOCKED_PASSWORD,
        "preferences_id": "pref_lockout",
    },
    "pending_user": {
        "username": "pending_demo",
        "password": IDENTITY_PENDING_PASSWORD,
        "preferences_id": None,
    },
    "reset_user": {
        "username": "reset_target",
        "password": "ResetM3Now!42",
        "preferences_id": "pref_reset_target",
    },
    "share_guard": {
        "username": "share_guard",
        "password": "CantShare123!",
        "preferences_id": "pref_share_guard",
    },
}

_USER_INSERT_SQL = """
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
    enforced_password_change
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

_PREFERENCE_INSERT_SQL = """
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
"""


def _ensure_schema_version_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS rfu_schema_version (
            version INTEGER PRIMARY KEY,
            applied_at TEXT NOT NULL,
            description TEXT
        )
        """
    )


def _seed_user(conn: sqlite3.Connection, user_row: Dict[str, Any]) -> None:
    conn.execute(
        _USER_INSERT_SQL,
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
        ),
    )


def _seed_preferences(conn: sqlite3.Connection, pref_row: Dict[str, Any]) -> None:
    conn.execute(
        _PREFERENCE_INSERT_SQL,
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


def _build_user(
    *,
    username: str,
    plaintext: str,
    role: str = "standard",
    account_status: str = "active",
    share_preferences: bool = False,
    login_attempts: int = 0,
    preferences_id: str | None = None,
) -> Dict[str, Any]:
    seed = UserSeed(
        username=username,
        plaintext_password=plaintext,
        role=role,
        account_status=account_status,
        share_preferences=share_preferences,
        login_attempts=login_attempts,
        preferences_id=preferences_id,
    )
    return seed.to_row()


def _seed_contract_data(conn: sqlite3.Connection) -> None:
    # Active user for login success + logout tests
    active_user = _build_user(
        username=CONTRACT_ACCOUNTS["demo_active"]["username"],
        plaintext=CONTRACT_ACCOUNTS["demo_active"]["password"],
        preferences_id=CONTRACT_ACCOUNTS["demo_active"]["preferences_id"],
    )
    active_user, active_pref = attach_preferences(
        active_user,
        preference_record(
            active_user["username"],
            preferences_id=CONTRACT_ACCOUNTS["demo_active"]["preferences_id"],
            share_enabled=False,
        ),
    )
    _seed_user(conn, active_user)
    _seed_preferences(conn, active_pref)

    # Lockout scenario user starts with 4 attempts already recorded.
    lockout_user = _build_user(
        username=CONTRACT_ACCOUNTS["lockout_user"]["username"],
        plaintext=CONTRACT_ACCOUNTS["lockout_user"]["password"],
        login_attempts=4,
        preferences_id=CONTRACT_ACCOUNTS["lockout_user"]["preferences_id"],
    )
    lockout_user, lockout_pref = attach_preferences(
        lockout_user,
        preference_record(
            lockout_user["username"],
            preferences_id=CONTRACT_ACCOUNTS["lockout_user"]["preferences_id"],
        ),
    )
    _seed_user(conn, lockout_user)
    _seed_preferences(conn, lockout_pref)

    # Pending user waiting for admin approval (no preferences yet).
    pending_user = _build_user(
        username=CONTRACT_ACCOUNTS["pending_user"]["username"],
        plaintext=CONTRACT_ACCOUNTS["pending_user"]["password"],
        account_status="pending",
        preferences_id=None,
    )
    _seed_user(conn, pending_user)

    # Reset target user for admin reset flow.
    reset_user = _build_user(
        username=CONTRACT_ACCOUNTS["reset_user"]["username"],
        plaintext=CONTRACT_ACCOUNTS["reset_user"]["password"],
        preferences_id=CONTRACT_ACCOUNTS["reset_user"]["preferences_id"],
    )
    reset_user, reset_pref = attach_preferences(
        reset_user,
        preference_record(
            reset_user["username"],
            preferences_id=CONTRACT_ACCOUNTS["reset_user"]["preferences_id"],
        ),
    )
    _seed_user(conn, reset_user)
    _seed_preferences(conn, reset_pref)

    # Share guard user with sharing disabled flag.
    share_guard = _build_user(
        username=CONTRACT_ACCOUNTS["share_guard"]["username"],
        plaintext=CONTRACT_ACCOUNTS["share_guard"]["password"],
        share_preferences=False,
        preferences_id=CONTRACT_ACCOUNTS["share_guard"]["preferences_id"],
    )
    share_guard, share_pref = attach_preferences(
        share_guard,
        preference_record(
            share_guard["username"],
            preferences_id=CONTRACT_ACCOUNTS["share_guard"]["preferences_id"],
            share_enabled=False,
        ),
    )
    _seed_user(conn, share_guard)
    _seed_preferences(conn, share_pref)


def _prepare_template_db(template_path: Path) -> None:
    template_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(template_path)
    conn.execute("PRAGMA foreign_keys=ON;")
    _ensure_schema_version_table(conn)
    script = MIGRATION_FILE.read_text(encoding="utf-8")
    conn.executescript(script)
    assert_mfa_schema_ready(conn)
    _seed_contract_data(conn)
    conn.commit()
    conn.close()


@pytest.fixture(scope="session")
def identity_contract_template(tmp_path_factory: pytest.TempPathFactory) -> Path:
    template_dir = tmp_path_factory.mktemp("identity_contract_template")
    template_path = template_dir / "rfu_identity_contract.sqlite"
    if not MIGRATION_FILE.exists():
        raise FileNotFoundError(
            "Expected migration file at scripts/migrations/006_baseline_login_password.sql"
        )
    _prepare_template_db(template_path)
    return template_path


@pytest.fixture
def contract_db_path(identity_contract_template: Path, tmp_path: Path) -> Path:
    db_path = tmp_path / "identity_contract.sqlite"
    shutil.copy(identity_contract_template, db_path)
    return db_path


@pytest.fixture
def contract_db_conn(contract_db_path: Path):
    conn = sqlite3.connect(contract_db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


@pytest.fixture(scope="session")
def identity_accounts() -> Dict[str, Dict[str, Any]]:
    return CONTRACT_ACCOUNTS


def _load_controller(module_path: str, class_name: str):
    module = importlib.import_module(module_path)
    try:
        return getattr(module, class_name)
    except AttributeError as exc:
        raise AssertionError(
            f"{module_path}.{class_name} must exist for identity contract tests"
        ) from exc


def _instantiate_controller(module_path: str, class_name: str, *, db_path: Path):
    controller_cls = _load_controller(module_path, class_name)
    try:
        return controller_cls(db_path=db_path)
    except (
        TypeError
    ) as exc:  # pragma: no cover - exercised when controller missing kwargs
        raise AssertionError(
            f"{class_name} must accept a 'db_path' keyword argument for contract tests"
        ) from exc


@pytest.fixture
def auth_controller(contract_db_path: Path):
    return _instantiate_controller(
        "src.core.auth.endpoints.auth_controller",
        "AuthController",
        db_path=contract_db_path,
    )


@pytest.fixture
def admin_users_controller(contract_db_path: Path):
    return _instantiate_controller(
        "src.core.auth.endpoints.admin_users_controller",
        "AdminUsersController",
        db_path=contract_db_path,
    )


@pytest.fixture
def preferences_share_controller(contract_db_path: Path):
    return _instantiate_controller(
        "src.core.preferences.endpoints.preferences_share_controller",
        "PreferencesShareController",
        db_path=contract_db_path,
    )
