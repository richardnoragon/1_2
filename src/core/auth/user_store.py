"""Low-level database operations for user accounts."""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from src.core.auth.models import UserAccount
from src.database.database_manager import DatabaseManager, get_database_manager


class _DirectDatabaseAdapter:
    """Minimal adapter that mirrors DatabaseManager's query helpers."""

    def __init__(self, database_path: str | Path) -> None:
        self._path = Path(database_path)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def execute_query(
        self,
        query: str,
        params: tuple = (),
    ) -> list[dict[str, Any]]:
        conn = self._connect()
        try:
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def execute_update(self, query: str, params: tuple = ()) -> int:
        conn = self._connect()
        try:
            cursor = conn.execute(query, params)
            conn.commit()
            return int(cursor.rowcount)
        finally:
            conn.close()


class UserStore:
    """Typed helper around ``user_accounts`` and related audit tables."""

    def __init__(
        self,
        db: Optional[DatabaseManager] = None,
        *,
        database_path: str | Path | None = None,
    ) -> None:
        if db is None and database_path is not None:
            self.db = _DirectDatabaseAdapter(database_path)
        else:
            self.db = db or get_database_manager()
        self._preference_column: Optional[str] = None
        self._reset_column: Optional[str] = None
        self._audit_schema_variant: Optional[str] = None
        self._table_columns_cache: Dict[str, set[str]] = {}

    def _columns_for_table(self, table: str) -> set[str]:
        if table in self._table_columns_cache:
            return self._table_columns_cache[table]
        try:
            columns = self.db.execute_query(f"PRAGMA table_info({table})")
        except (RuntimeError, sqlite3.Error):
            # pragma: no cover - defensive fallback
            names: set[str] = set()
        else:
            names = {
                row.get("name")
                for row in columns
                if isinstance(row, dict) and row.get("name")
            }
        self._table_columns_cache[table] = names
        return names

    def _preferences_column_name(self) -> str:
        if self._preference_column:
            return self._preference_column

        names = self._columns_for_table("user_accounts")
        for candidate in ("preferences_user_id", "preferences_id"):
            if candidate in names:
                self._preference_column = candidate
                break
        else:
            self._preference_column = "preferences_user_id"

        return self._preference_column

    def _reset_column_name(self) -> str:
        if self._reset_column:
            return self._reset_column

        names = self._columns_for_table("user_accounts")
        if "reset_required" in names:
            self._reset_column = "reset_required"
        elif "enforced_password_change" in names:
            self._reset_column = "enforced_password_change"
        else:
            self._reset_column = "reset_required"
        return self._reset_column

    def _audit_schema(self) -> str:
        if self._audit_schema_variant is not None:
            return self._audit_schema_variant

        names = self._columns_for_table("admin_action_audit")
        if not names:
            self._audit_schema_variant = "none"
            return self._audit_schema_variant

        extended_fields = {
            "actor_username",
            "target_username",
            "action_type",
            "origin_surface",
        }
        if extended_fields.issubset(names):
            self._audit_schema_variant = "extended"
        elif {"username", "action", "actor", "metadata"}.issubset(names):
            self._audit_schema_variant = "legacy"
        else:
            self._audit_schema_variant = "none"
        return self._audit_schema_variant

    def _user_exists(self, username: str) -> bool:
        rows = self.db.execute_query(
            "SELECT 1 FROM user_accounts WHERE username = ? LIMIT 1",
            (username,),
        )
        return bool(rows)

    # ------------------------------------------------------------------
    # Query helpers
    # ------------------------------------------------------------------
    def has_any_user(self) -> bool:
        rows = self.db.execute_query(
            "SELECT COUNT(1) AS total FROM user_accounts",
        )
        return bool(rows and rows[0]["total"])

    def get_user(self, username: str) -> Optional[UserAccount]:
        pref_column = self._preferences_column_name()
        reset_column = self._reset_column_name()
        rows = self.db.execute_query(
            "SELECT * FROM user_accounts WHERE username = ? LIMIT 1",
            (username,),
        )
        if not rows:
            return None
        row = dict(rows[0])
        row["preferences_id"] = row.get(pref_column)
        row["enforced_password_change"] = row.get(reset_column)
        return UserAccount.from_row(row)

    # Alias for compatibility with BreakGlassService
    def get_by_username(self, username: str) -> Optional[UserAccount]:
        """Alias for get_user() - compatibility with BreakGlassService."""
        return self.get_user(username)

    @staticmethod
    def _utc_timestamp() -> str:
        return datetime.now(timezone.utc).isoformat(timespec="microseconds")

    # ------------------------------------------------------------------
    # Mutation helpers
    # ------------------------------------------------------------------
    def create_user(
        self,
        *,
        username: str,
        password_hash: str,
        role: str = "user",
        preferences_user_id: Optional[str] = None,
        reset_required: bool = False,
    ) -> None:
        prefs_id = preferences_user_id or username
        pref_column = self._preferences_column_name()
        reset_column = self._reset_column_name()
        self.db.execute_update(
            f"""
            INSERT INTO user_accounts (
                username,
                password_hash,
                role,
                {pref_column},
                {reset_column}
            ) VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(username) DO NOTHING
            """,
            (
                username,
                password_hash,
                role,
                prefs_id,
                1 if reset_required else 0,
            ),
        )
        self.record_audit(
            username=username,
            action="create",
            actor="system",
            details={"role": role},
        )

    def update_password(
        self,
        *,
        username: str,
        password_hash: str,
        reset_required: bool = False,
        actor: str = "system",
    ) -> None:
        reset_column = self._reset_column_name()
        self.db.execute_update(
            f"""
            UPDATE user_accounts
            SET password_hash = ?,
                {reset_column} = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE username = ?
            """,
            (password_hash, 1 if reset_required else 0, username),
        )
        self.record_audit(
            username=username,
            action="password_reset",
            actor=actor,
            details={"reset_required": reset_required},
        )

    def record_login_success(
        self,
        username: str,
        *,
        origin_surface: str = "service",
    ) -> None:
        reset_column = self._reset_column_name()
        self.db.execute_update(
            f"""
            UPDATE user_accounts
            SET login_attempts = 0,
                is_blocked = 0,
                account_status = 'active',
                {reset_column} = 0,
                last_login = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE username = ?
            """,
            (username,),
        )
        self.record_audit(
            username=username,
            action="login_success",
            actor=username,
            origin_surface=origin_surface,
        )

    def record_login_failure(
        self,
        username: str,
        *,
        max_attempts: int,
        origin_surface: str = "service",
    ) -> bool:
        rows = self.db.execute_query(
            "SELECT login_attempts FROM user_accounts WHERE username = ?",
            (username,),
        )
        current_attempts = int(rows[0]["login_attempts"] or 0) if rows else 0
        new_attempts = current_attempts + 1
        is_blocked = 1 if new_attempts >= max_attempts else 0
        self.db.execute_update(
            """
            UPDATE user_accounts
            SET login_attempts = ?,
                is_blocked = ?,
                account_status = CASE
                    WHEN ? = 1 THEN 'blocked'
                    ELSE account_status
                END,
                last_failed_login = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE username = ?
            """,
            (new_attempts, is_blocked, is_blocked, username),
        )
        self.record_audit(
            username=username,
            action="login_failure",
            actor=username,
            origin_surface=origin_surface,
            details={"attempts": new_attempts, "blocked": bool(is_blocked)},
        )
        if is_blocked:
            self.record_audit(
                username=username,
                action="lockout",
                actor=username,
                origin_surface=origin_surface,
                details={"attempts": new_attempts},
            )
        return bool(is_blocked)

    def unblock(self, username: str, *, actor: str) -> None:
        self.db.execute_update(
            """
            UPDATE user_accounts
            SET login_attempts = 0,
                is_blocked = 0,
                account_status = 'active',
                updated_at = CURRENT_TIMESTAMP
            WHERE username = ?
            """,
            (username,),
        )
        self.record_audit(
            username=username,
            action="unblock",
            actor=actor,
        )

    def record_audit(
        self,
        *,
        username: str,
        action: str,
        actor: Optional[str] = None,
        origin_surface: str = "service",
        details: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        schema = self._audit_schema()
        if schema == "none":
            return

        payload = json.dumps(details or {}, ensure_ascii=False)
        actor_username = actor or username
        if schema == "legacy":
            self.db.execute_update(
                """
                INSERT INTO admin_action_audit (
                    username,
                    action,
                    actor,
                    metadata
                ) VALUES (?, ?, ?, ?)
                """,
                (username, action, actor_username, payload),
            )
            return

        if not self._user_exists(actor_username):
            actor_username = username
        audit_id = uuid.uuid4().hex
        metadata_payload = json.dumps(metadata or {}, ensure_ascii=False)
        created_at = self._utc_timestamp()
        self.db.execute_update(
            """
            INSERT INTO admin_action_audit (
                audit_id,
                actor_username,
                target_username,
                action_type,
                origin_surface,
                details,
                created_at,
                metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                audit_id,
                actor_username,
                username,
                action,
                origin_surface,
                payload,
                created_at,
                metadata_payload,
            ),
        )


__all__ = ["UserStore"]
