"""Utility that simulates repeated login failures to trigger lockout guards."""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from .cli_types import CommandResult

LOCKOUT_THRESHOLD = 5
ACTOR_USERNAME = "rfu-admin"
ORIGIN_SURFACE = "cli"


def _utc_now() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _connect(database_path: Path) -> sqlite3.Connection:
    if not database_path.exists():
        raise FileNotFoundError(f"Database not found at {database_path}")
    conn = sqlite3.connect(database_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


def _fetch_user(conn: sqlite3.Connection, username: str) -> sqlite3.Row:
    row = conn.execute(
        """
        SELECT username, login_attempts, account_status, is_blocked, blocked_at
        FROM user_accounts
        WHERE username = ?
        LIMIT 1
        """,
        (username,),
    ).fetchone()
    if row is None:
        raise ValueError(f"User {username!r} does not exist in user_accounts")
    return row


def _resolve_actor_username(
    conn: sqlite3.Connection,
    fallback: str,
) -> str:
    row = conn.execute(
        "SELECT 1 FROM user_accounts WHERE username = ? LIMIT 1",
        (ACTOR_USERNAME,),
    ).fetchone()
    return ACTOR_USERNAME if row else fallback


def _insert_audit_row(
    conn: sqlite3.Connection,
    *,
    target_username: str,
    attempts: int,
    blocked: bool,
    action_type: str,
) -> None:
    actor_username = _resolve_actor_username(conn, fallback=target_username)
    conn.execute(
        """
        INSERT INTO admin_action_audit (
            audit_id,
            actor_username,
            target_username,
            action_type,
            origin_surface,
            details,
            created_at,
            correlation_id,
            metadata
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            str(uuid.uuid4()),
            actor_username,
            target_username,
            action_type,
            ORIGIN_SURFACE,
            json.dumps({"attempts": attempts, "blocked": blocked}),
            _utc_now(),
            None,
            None,
        ),
    )


def simulate_failed_logins(
    *,
    database_path: str | Path,
    username: str,
    attempts: int = LOCKOUT_THRESHOLD,
) -> CommandResult:
    """Trigger repeated failures so tests can assert the lockout workflow."""

    db_path = Path(database_path)
    if attempts <= 0:
        return CommandResult(
            exit_code=1,
            error="attempts must be a positive integer",
        )

    try:
        with _connect(db_path) as conn:
            user_row = _fetch_user(conn, username)
            base_attempts = int(user_row["login_attempts"] or 0)
            new_attempts = base_attempts + attempts
            blocked = new_attempts >= LOCKOUT_THRESHOLD
            action_type = "lockout" if blocked else "login_failure"

            blocked_at = user_row["blocked_at"]
            now_ts = _utc_now()
            if blocked and not blocked_at:
                blocked_at = now_ts

            conn.execute(
                """
                UPDATE user_accounts
                SET login_attempts = ?,
                    is_blocked = ?,
                    account_status = CASE WHEN ? THEN 'blocked'
                                           ELSE account_status END,
                    last_failed_login = ?,
                    blocked_at = CASE WHEN ? THEN ? ELSE blocked_at END,
                    updated_at = ?
                WHERE username = ?
                """,
                (
                    new_attempts,
                    1 if blocked else user_row["is_blocked"],
                    1 if blocked else 0,
                    now_ts,
                    1 if blocked else 0,
                    blocked_at,
                    now_ts,
                    username,
                ),
            )

            _insert_audit_row(
                conn,
                target_username=username,
                attempts=new_attempts,
                blocked=blocked,
                action_type=action_type,
            )

            conn.commit()

            payload = {
                "username": username,
                "attempts": new_attempts,
                "blocked": blocked,
                "account_status": (
                    "blocked" if blocked else user_row["account_status"]
                ),
            }
            return CommandResult(exit_code=0, payload=payload)
    except Exception as exc:  # pragma: no cover - surfaced to CLI caller
        return CommandResult(exit_code=1, error=str(exc))


def _parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database-path", required=True)
    parser.add_argument("--username", required=True)
    parser.add_argument("--attempts", type=int, default=LOCKOUT_THRESHOLD)
    return parser.parse_args(list(argv) if argv is not None else None)


def main(argv: Iterable[str] | None = None) -> int:
    args = _parse_args(argv)
    result = simulate_failed_logins(
        database_path=args.database_path,
        username=args.username,
        attempts=args.attempts,
    )

    if result.payload is not None:
        print(json.dumps(result.payload, indent=2))
    if result.error:
        print(result.error, file=sys.stderr)
    return result.exit_code


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main(sys.argv[1:]))
