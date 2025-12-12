"""Repository helpers for the ``user_accounts`` table."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Mapping

from src.core.auth.models import AccountStatus, UserAccount, UserRole
from src.core.auth.models.utils import datetime_to_iso, dict_to_json
from src.core.database.repository_base import SQLiteRepository

if TYPE_CHECKING:
    from src.core.auth.services.audit_logger import AuditLogger


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
                    mfa_enforced_at,
                    is_always_available,
                    is_break_glass,
                    break_glass_justification,
                    auto_unblock_at
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
                    :mfa_enforced_at,
                    :is_always_available,
                    :is_break_glass,
                    :break_glass_justification,
                    :auto_unblock_at
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
                    mfa_enforced_at = excluded.mfa_enforced_at,
                    is_always_available = excluded.is_always_available,
                    is_break_glass = excluded.is_break_glass,
                    break_glass_justification = excluded.break_glass_justification,
                    auto_unblock_at = excluded.auto_unblock_at
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
                    "is_always_available": record.get("is_always_available", 0),
                    "is_break_glass": record.get("is_break_glass", 0),
                    "break_glass_justification": record.get(
                        "break_glass_justification"
                    ),
                    "auto_unblock_at": _iso(record.get("auto_unblock_at")),
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

    def unblock(self, username: str) -> bool:
        """Unblock an account by resetting status to active.

        Also resets login_attempts and is_blocked flag.

        Args:
            username: The account username to unblock

        Returns:
            True if account was updated, False otherwise
        """
        with self._connection() as conn:
            cursor = conn.execute(
                """
                UPDATE user_accounts
                SET account_status = ?,
                    is_blocked = 0,
                    login_attempts = 0,
                    blocked_at = NULL,
                    updated_at = CURRENT_TIMESTAMP
                WHERE username = ?
                """,
                (AccountStatus.ACTIVE.value, username),
            )
            conn.commit()
            return bool(cursor.rowcount)

    def set_auto_unblock(
        self,
        username: str,
        auto_unblock_at: datetime | None,
    ) -> bool:
        """Set or clear the auto-unblock timestamp for an account.

        Args:
            username: The account username
            auto_unblock_at: When to auto-unblock, or None to clear

        Returns:
            True if account was updated, False otherwise
        """
        with self._connection() as conn:
            cursor = conn.execute(
                """
                UPDATE user_accounts
                SET auto_unblock_at = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE username = ?
                """,
                (_iso(auto_unblock_at), username),
            )
            conn.commit()
            return bool(cursor.rowcount)

    # ------------------------------------------------------------------
    # T044: Protected account queries
    # ------------------------------------------------------------------

    def get_always_available_accounts(self) -> list[UserAccount]:
        """Get all accounts marked as always-available.

        Returns:
            List of UserAccount objects with is_always_available=True
        """
        with self._connection() as conn:
            rows = conn.execute(
                """
                SELECT * FROM user_accounts
                WHERE is_always_available = 1
                ORDER BY username
                """
            ).fetchall()
        return [self._row_to_account(row) for row in rows if row]

    def get_break_glass_accounts(self) -> list[UserAccount]:
        """Get all accounts marked as break-glass.

        Returns:
            List of UserAccount objects with is_break_glass=True
        """
        with self._connection() as conn:
            rows = conn.execute(
                """
                SELECT * FROM user_accounts
                WHERE is_break_glass = 1
                ORDER BY username
                """
            ).fetchall()
        return [self._row_to_account(row) for row in rows if row]

    def get_protected_accounts(self) -> list[UserAccount]:
        """Get all protected accounts (always-available or break-glass).

        Returns:
            List of UserAccount objects that are protected
        """
        with self._connection() as conn:
            rows = conn.execute(
                """
                SELECT * FROM user_accounts
                WHERE is_always_available = 1 OR is_break_glass = 1
                ORDER BY username
                """
            ).fetchall()
        return [self._row_to_account(row) for row in rows if row]

    def is_protected(self, username: str) -> bool:
        """Check if an account is protected (always-available or break-glass).

        Args:
            username: The account username to check

        Returns:
            True if the account is protected, False otherwise
        """
        with self._connection() as conn:
            row = conn.execute(
                """
                SELECT (is_always_available = 1 OR is_break_glass = 1)
                    AS protected
                FROM user_accounts
                WHERE username = ?
                """,
                (username,),
            ).fetchone()
        if row is None:
            return False
        return bool(row["protected"])

    def is_always_available(self, username: str) -> bool:
        """Check if an account is always-available.

        Args:
            username: The account username to check

        Returns:
            True if the account is always-available, False otherwise
        """
        with self._connection() as conn:
            row = conn.execute(
                """
                SELECT is_always_available
                FROM user_accounts
                WHERE username = ?
                """,
                (username,),
            ).fetchone()
        if row is None:
            return False
        return bool(row["is_always_available"])

    def is_break_glass(self, username: str) -> bool:
        """Check if an account is a break-glass account.

        Args:
            username: The account username to check

        Returns:
            True if the account is break-glass, False otherwise
        """
        with self._connection() as conn:
            row = conn.execute(
                """
                SELECT is_break_glass
                FROM user_accounts
                WHERE username = ?
                """,
                (username,),
            ).fetchone()
        if row is None:
            return False
        return bool(row["is_break_glass"])

    def update_role(
        self,
        username: str,
        new_role: UserRole,
        *,
        actor_username: str | None = None,
        audit_logger: "AuditLogger | None" = None,
        correlation_id: str | None = None,
    ) -> bool:
        """Update an account's role with optional audit logging.

        Protected accounts (always-available or break-glass) cannot have
        their roles changed.

        Args:
            username: The account username to update
            new_role: The new role to assign
            actor_username: Who is making the change (for audit)
            audit_logger: Optional audit logger for recording the change
            correlation_id: Optional correlation ID for audit trail

        Returns:
            True if role was updated, False otherwise

        Raises:
            PermissionError: If account is protected
        """
        # Check if account is protected
        if self.is_protected(username):
            if audit_logger and actor_username and correlation_id:
                audit_logger.record_action(
                    action_type="role_change_blocked",
                    actor_username=actor_username,
                    target_username=username,
                    details={
                        "reason": "protected_account",
                        "attempted_role": new_role.value,
                    },
                    correlation_id=correlation_id,
                )
            raise PermissionError(
                f"Cannot change role for protected account '{username}'"
            )

        # Get current role for audit
        current_account = self.get(username)
        if current_account is None:
            return False

        old_role = current_account.role

        with self._connection() as conn:
            cursor = conn.execute(
                """
                UPDATE user_accounts
                SET role = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE username = ?
                """,
                (new_role.value, username),
            )
            conn.commit()
            updated = bool(cursor.rowcount)

        # Log the role change if audit logger provided
        if updated and audit_logger and actor_username and correlation_id:
            audit_logger.record_action(
                action_type="role_changed",
                actor_username=actor_username,
                target_username=username,
                details={
                    "old_role": old_role.value,
                    "new_role": new_role.value,
                },
                correlation_id=correlation_id,
            )

        return updated

    @staticmethod
    def _row_to_account(
        row: sqlite3.Row | Mapping[str, object] | None,
    ) -> UserAccount | None:
        if row is None:
            return None
        data = dict(row)
        return UserAccount.from_row(data)


__all__ = ["UserAccountRepository"]
