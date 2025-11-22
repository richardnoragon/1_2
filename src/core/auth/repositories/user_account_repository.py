"""Repository helpers for the ``user_accounts`` table."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from typing import Mapping

from src.core.auth.models import AccountStatus, UserAccount, UserRole
from src.core.auth.models.utils import datetime_to_iso, dict_to_json
from src.core.database.repository_base import SQLiteRepository


def _blob(value: bytes | memoryview | None) -> sqlite3.Binary | None:
    if value is None:
        return None
    if isinstance(value, memoryview):
        value = value.tobytes()
    return sqlite3.Binary(bytes(value))


def _iso(value: datetime | None) -> str | None:
    return datetime_to_iso(value)


class UserAccountRepository(SQLiteRepository):
    """CRUD + lifecycle helpers for ``user_accounts`` rows."""

    def get(self, username: str) -> UserAccount | None:
        with self._connection() as conn:
            row = conn.execute(
                "SELECT * FROM user_accounts WHERE username = ? LIMIT 1",
                (username,),
            ).fetchone()
        return self._row_to_account(row)

    def list_by_status(
        self,
        *,
        status: AccountStatus,
        limit: int | None = None,
    ) -> list[UserAccount]:
        sql = "SELECT * FROM user_accounts WHERE account_status = ? ORDER BY created_at"
        params: list[object] = [status.value]
        if limit and limit > 0:
            sql += " LIMIT ?"
            params.append(limit)
        with self._connection() as conn:
            rows = conn.execute(sql, tuple(params)).fetchall()
        return [self._row_to_account(row) for row in rows if row]

    def has_any_user(self) -> bool:
        with self._connection() as conn:
            row = conn.execute("SELECT COUNT(1) AS total FROM user_accounts").fetchone()
        return bool(row and row["total"])  # type: ignore[index]

    def upsert(self, account: UserAccount) -> None:
        record = account.to_record()
        with self._connection() as conn:
            conn.execute(
                """
                INSERT INTO user_accounts (
                    username,
                    password_hash,
                    password_salt,
                    role,
                    account_status,
                    login_attempts,
                    is_blocked,
                    preferences_id,
                    share_preferences,
                    registration_channel,
                    registration_metadata,
                    created_at,
                    activated_at,
                    blocked_at,
                    updated_at,
                    last_login,
                    last_failed_login,
                    enforced_password_change,
                    mfa_enabled,
                    mfa_secret_encrypted,
                    mfa_recovery_codes,
                    mfa_enforced_at
                ) VALUES (
                    :username,
                    :password_hash,
                    :password_salt,
                    :role,
                    :account_status,
                    :login_attempts,
                    :is_blocked,
                    :preferences_id,
                    :share_preferences,
                    :registration_channel,
                    :registration_metadata,
                    :created_at,
                    :activated_at,
                    :blocked_at,
                    :updated_at,
                    :last_login,
                    :last_failed_login,
                    :enforced_password_change,
                    :mfa_enabled,
                    :mfa_secret_encrypted,
                    :mfa_recovery_codes,
                    :mfa_enforced_at
                )
                ON CONFLICT(username) DO UPDATE SET
                    password_hash = excluded.password_hash,
                    password_salt = excluded.password_salt,
                    role = excluded.role,
                    account_status = excluded.account_status,
                    login_attempts = excluded.login_attempts,
                    is_blocked = excluded.is_blocked,
                    preferences_id = excluded.preferences_id,
                    share_preferences = excluded.share_preferences,
                    registration_channel = excluded.registration_channel,
                    registration_metadata = excluded.registration_metadata,
                    activated_at = excluded.activated_at,
                    blocked_at = excluded.blocked_at,
                    updated_at = excluded.updated_at,
                    last_login = excluded.last_login,
                    last_failed_login = excluded.last_failed_login,
                    enforced_password_change = excluded.enforced_password_change,
                    mfa_enabled = excluded.mfa_enabled,
                    mfa_secret_encrypted = excluded.mfa_secret_encrypted,
                    mfa_recovery_codes = excluded.mfa_recovery_codes,
                    mfa_enforced_at = excluded.mfa_enforced_at
                """,
                {
                    "username": record["username"],
                    "password_hash": record["password_hash"],
                    "password_salt": _blob(record.get("password_salt")),
                    "role": record["role"],
                    "account_status": record["account_status"],
                    "login_attempts": record["login_attempts"],
                    "is_blocked": record["is_blocked"],
                    "preferences_id": record.get("preferences_id"),
                    "share_preferences": record["share_preferences"],
                    "registration_channel": record["registration_channel"],
                    "registration_metadata": record.get("registration_metadata"),
                    "created_at": _iso(record.get("created_at")),
                    "activated_at": _iso(record.get("activated_at")),
                    "blocked_at": _iso(record.get("blocked_at")),
                    "updated_at": _iso(record.get("updated_at"))
                    or _iso(datetime.now(timezone.utc)),
                    "last_login": _iso(record.get("last_login")),
                    "last_failed_login": _iso(record.get("last_failed_login")),
                    "enforced_password_change": record["enforced_password_change"],
                    "mfa_enabled": record["mfa_enabled"],
                    "mfa_secret_encrypted": _blob(record.get("mfa_secret_encrypted")),
                    "mfa_recovery_codes": record.get("mfa_recovery_codes"),
                    "mfa_enforced_at": _iso(record.get("mfa_enforced_at")),
                },
            )
            conn.commit()

    def delete(self, username: str) -> int:
        with self._connection() as conn:
            cursor = conn.execute(
                "DELETE FROM user_accounts WHERE username = ?",
                (username,),
            )
            conn.commit()
            return cursor.rowcount

    def set_role(self, username: str, role: UserRole) -> bool:
        with self._connection() as conn:
            cursor = conn.execute(
                "UPDATE user_accounts SET role = ?, updated_at = CURRENT_TIMESTAMP WHERE username = ?",
                (role.value, username),
            )
            conn.commit()
            return bool(cursor.rowcount)

    def activate_pending_account(
        self,
        *,
        username: str,
        preferences_id: str,
        actor_username: str,
        activated_at: datetime | None = None,
    ) -> UserAccount:
        timestamp = _iso(activated_at or datetime.now(timezone.utc))
        with self._connection() as conn:
            conn.execute("BEGIN")
            row = conn.execute(
                "SELECT * FROM user_accounts WHERE username = ? LIMIT 1",
                (username,),
            ).fetchone()
            account = self._row_to_account(row)
            if account is None:
                raise ValueError(f"Unknown user '{username}'")
            if account.account_status != AccountStatus.PENDING:
                raise ValueError("Account is not pending approval")
            metadata = dict(account.registration_metadata or {})
            metadata.update(
                {
                    "approved_by": actor_username,
                    "approved_at": timestamp,
                }
            )
            payload = dict_to_json(metadata)
            conn.execute(
                """
                UPDATE user_accounts
                SET account_status = ?,
                    is_blocked = 0,
                    login_attempts = 0,
                    preferences_id = ?,
                    activated_at = ?,
                    updated_at = ?,
                    registration_metadata = ?
                WHERE username = ?
                """,
                (
                    AccountStatus.ACTIVE.value,
                    preferences_id,
                    timestamp,
                    timestamp,
                    payload,
                    username,
                ),
            )
            conn.commit()
        account.account_status = AccountStatus.ACTIVE
        account.preferences_id = preferences_id
        account.activated_at = datetime.fromisoformat(timestamp)
        account.updated_at = account.activated_at
        account.registration_metadata = metadata
        return account

    def update_status(
        self,
        *,
        username: str,
        status: AccountStatus,
        blocked_at: datetime | None = None,
    ) -> bool:
        block_flag = 1 if status == AccountStatus.BLOCKED else 0
        with self._connection() as conn:
            cursor = conn.execute(
                """
                UPDATE user_accounts
                SET account_status = ?,
                    blocked_at = ?,
                    updated_at = CURRENT_TIMESTAMP,
                    is_blocked = ?
                WHERE username = ?
                """,
                (
                    status.value,
                    _iso(blocked_at),
                    block_flag,
                    username,
                ),
            )
            conn.commit()
            return bool(cursor.rowcount)

    def record_login_success(self, username: str) -> None:
        with self._connection() as conn:
            conn.execute(
                """
                UPDATE user_accounts
                SET login_attempts = 0,
                    is_blocked = 0,
                    last_login = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP,
                    account_status = ?
                WHERE username = ?
                """,
                (AccountStatus.ACTIVE.value, username),
            )
            conn.commit()

    def record_login_failure(
        self,
        username: str,
        *,
        max_attempts: int,
    ) -> tuple[int, bool]:
        if max_attempts <= 0:
            raise ValueError("max_attempts must be positive")
        with self._connection() as conn:
            conn.execute("BEGIN")
            row = conn.execute(
                "SELECT login_attempts FROM user_accounts WHERE username = ?",
                (username,),
            ).fetchone()
            if row is None:
                raise ValueError(f"Unknown user '{username}'")
            attempts = int(row["login_attempts"] or 0)
            attempts += 1
            blocked = attempts >= max_attempts
            conn.execute(
                """
                UPDATE user_accounts
                SET login_attempts = ?,
                    is_blocked = CASE WHEN ? THEN 1 ELSE 0 END,
                    account_status = CASE WHEN ? THEN ? ELSE account_status END,
                    blocked_at = CASE WHEN ? THEN CURRENT_TIMESTAMP ELSE blocked_at END,
                    last_failed_login = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE username = ?
                """,
                (
                    attempts,
                    blocked,
                    blocked,
                    AccountStatus.BLOCKED.value,
                    blocked,
                    username,
                ),
            )
            conn.commit()
        return attempts, blocked

    def update_preferences_link(
        self,
        *,
        username: str,
        preferences_id: str,
    ) -> bool:
        with self._connection() as conn:
            cursor = conn.execute(
                """
                UPDATE user_accounts
                SET preferences_id = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE username = ?
                """,
                (preferences_id, username),
            )
            conn.commit()
            return bool(cursor.rowcount)

    def ensure_metadata(
        self,
        *,
        username: str,
        metadata: Mapping[str, object] | None,
    ) -> None:
        payload = dict_to_json(metadata)
        with self._connection() as conn:
            conn.execute(
                "UPDATE user_accounts SET registration_metadata = ? WHERE username = ?",
                (payload, username),
            )
            conn.commit()

    def users_with_role(self, role: UserRole) -> list[str]:
        with self._connection() as conn:
            rows = conn.execute(
                "SELECT username FROM user_accounts WHERE role = ?",
                (role.value,),
            ).fetchall()
        return [row["username"] for row in rows]

    @staticmethod
    def _row_to_account(
        row: sqlite3.Row | Mapping[str, object] | None,
    ) -> UserAccount | None:
        if row is None:
            return None
        data = dict(row)
        return UserAccount.from_row(data)


__all__ = ["UserAccountRepository"]
