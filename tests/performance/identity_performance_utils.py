"""Shared helpers for identity performance tests."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

from src.core.auth.models.admin_action_audit import AdminActionType
from src.core.auth.services.audit_logger import AuditLogger
from tests.fixtures.identity_fixtures import (
    IDENTITY_SAMPLE_PASSWORD,
    preference_record,
)
from tests.integration.identity.utils import (
    apply_identity_schema,
    attach_default_preferences,
    build_user,
    insert_preference,
    insert_user,
)


def bootstrap_identity_db(root: Path, *, username: str = "demo") -> Path:
    """Create a fresh identity database containing a single active user."""

    root.mkdir(parents=True, exist_ok=True)
    db_path = root / "identity_perf.sqlite3"
    apply_identity_schema(db_path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        user_row = build_user(
            username=username,
            plaintext=IDENTITY_SAMPLE_PASSWORD,
        )
        user_row, pref_row = attach_default_preferences(
            user_row,
            preferences_id=f"pref_{username}_workspace",
        )
        insert_user(conn, user_row)
        insert_preference(conn, pref_row)
        conn.commit()
    finally:
        conn.close()
    return db_path


def seed_preference_records(db_path: Path, *, count: int = 120) -> None:
    """Insert a batch of additional preference profiles to simulate load."""

    conn = sqlite3.connect(db_path)
    try:
        for index in range(count):
            record = preference_record(
                user_id=f"perf_seed_{index}",
                preferences_id=f"pref_seed_{index}",
                overrides={"layout": f"team-{index % 5}"},
            )
            insert_preference(conn, record)
        conn.commit()
    finally:
        conn.close()


def seed_audit_entries(
    db_path: Path,
    *,
    days: int = 30,
    entries_per_day: int = 12,
) -> None:
    """Populate the admin_action_audit table with a rolling history."""

    _ensure_required_accounts(db_path)
    logger = AuditLogger(database_path=db_path, default_surface="cli")
    now = datetime.now(timezone.utc)
    total_entries = max(1, days * entries_per_day)
    for index in range(total_entries):
        timestamp = now - timedelta(minutes=30 * index)
        logger.record_action(
            action_type=AdminActionType.RESET_PASSWORD,
            actor_username=f"admin_{index % 3}",
            target_username=f"user_{index % 10}",
            details={"iteration": index},
            origin_surface="cli",
            occurred_at=timestamp,
        )


def _ensure_required_accounts(db_path: Path) -> None:
    """Seed actor/target accounts referenced by audit fixtures if absent."""

    conn = sqlite3.connect(db_path)
    try:
        actors = {f"admin_{suffix}" for suffix in range(3)}
        actors.add("rfu-admin")
        targets = {f"user_{suffix}" for suffix in range(10)}
        for username in sorted(actors):
            _ensure_identity_account(conn, username=username, role="admin")
        for username in sorted(targets):
            _ensure_identity_account(conn, username=username, role="standard")
        conn.commit()
    finally:
        conn.close()


def _ensure_identity_account(
    conn: sqlite3.Connection,
    *,
    username: str,
    role: str,
) -> None:
    """Insert an identity user + preference row unless it already exists."""

    exists = conn.execute(
        "SELECT 1 FROM user_accounts WHERE username = ?",
        (username,),
    ).fetchone()
    if exists:
        return
    user_row = build_user(
        username=username,
        plaintext=IDENTITY_SAMPLE_PASSWORD,
        role=role,
        preferences_id=f"perf_{username}",
    )
    user_row, pref_row = attach_default_preferences(
        user_row,
        preferences_id=f"perf_{username}",
    )
    insert_user(conn, user_row)
    insert_preference(conn, pref_row)


__all__ = [
    "bootstrap_identity_db",
    "seed_preference_records",
    "seed_audit_entries",
]
