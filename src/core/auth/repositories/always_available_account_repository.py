"""Repository for always-available account configuration.

Provides CRUD operations for AlwaysAvailableAccountConfig records.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, List, Optional

from src.core.auth.models.always_available_account_config import (
    AlwaysAvailableAccountConfig,
)


class AlwaysAvailableAccountRepository:
    """Repository for always-available account configuration.

    Manages persistence of AlwaysAvailableAccountConfig instances
    to the SQLite database.
    """

    TABLE_NAME = "always_available_account_config"

    def __init__(self, db_connection: Any = None):
        """Initialize repository.

        Args:
            db_connection: SQLite database connection
        """
        self._conn = db_connection

    def get_config(self, username: str) -> Optional[AlwaysAvailableAccountConfig]:
        """Get configuration for a username.

        Args:
            username: The account username

        Returns:
            AlwaysAvailableAccountConfig or None if not found
        """
        if self._conn is None:
            return None

        try:
            cursor = self._conn.cursor()
            cursor.execute(
                f"""
                SELECT username, cooldown_duration_minutes, auto_unblock_enabled,
                       last_cooldown_started_at, cooldown_count
                FROM {self.TABLE_NAME}
                WHERE username = ?
                """,
                (username,),
            )
            row = cursor.fetchone()
            if row is None:
                return None

            return AlwaysAvailableAccountConfig(
                username=row[0],
                cooldown_duration_minutes=row[1],
                auto_unblock_enabled=bool(row[2]),
                last_cooldown_started_at=(
                    datetime.fromisoformat(row[3]) if row[3] else None
                ),
                cooldown_count=row[4] or 0,
            )
        except Exception:
            return None

    def save(self, config: AlwaysAvailableAccountConfig) -> bool:
        """Save or update configuration.

        Args:
            config: The configuration to save

        Returns:
            True if save was successful
        """
        if self._conn is None:
            return False

        try:
            cursor = self._conn.cursor()
            cursor.execute(
                f"""
                INSERT INTO {self.TABLE_NAME}
                    (username, cooldown_duration_minutes, auto_unblock_enabled,
                     last_cooldown_started_at, cooldown_count)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(username) DO UPDATE SET
                    cooldown_duration_minutes = excluded.cooldown_duration_minutes,
                    auto_unblock_enabled = excluded.auto_unblock_enabled,
                    last_cooldown_started_at = excluded.last_cooldown_started_at,
                    cooldown_count = excluded.cooldown_count
                """,
                (
                    config.username,
                    config.cooldown_duration_minutes,
                    int(config.auto_unblock_enabled),
                    (
                        config.last_cooldown_started_at.isoformat()
                        if config.last_cooldown_started_at
                        else None
                    ),
                    config.cooldown_count,
                ),
            )
            self._conn.commit()
            return True
        except Exception:
            return False

    def delete(self, username: str) -> bool:
        """Delete configuration for a username.

        Args:
            username: The account username

        Returns:
            True if deletion was successful
        """
        if self._conn is None:
            return False

        try:
            cursor = self._conn.cursor()
            cursor.execute(
                f"DELETE FROM {self.TABLE_NAME} WHERE username = ?",
                (username,),
            )
            self._conn.commit()
            return cursor.rowcount > 0
        except Exception:
            return False

    def get_all(self) -> List[AlwaysAvailableAccountConfig]:
        """Get all configurations.

        Returns:
            List of all configurations
        """
        if self._conn is None:
            return []

        try:
            cursor = self._conn.cursor()
            cursor.execute(
                f"""
                SELECT username, cooldown_duration_minutes, auto_unblock_enabled,
                       last_cooldown_started_at, cooldown_count
                FROM {self.TABLE_NAME}
                """
            )
            rows = cursor.fetchall()
            return [
                AlwaysAvailableAccountConfig(
                    username=row[0],
                    cooldown_duration_minutes=row[1],
                    auto_unblock_enabled=bool(row[2]),
                    last_cooldown_started_at=(
                        datetime.fromisoformat(row[3]) if row[3] else None
                    ),
                    cooldown_count=row[4] or 0,
                )
                for row in rows
            ]
        except Exception:
            return []

    def get_accounts_in_cooldown(self) -> List[AlwaysAvailableAccountConfig]:
        """Get accounts currently in cooldown.

        Returns:
            List of configs where cooldown is active
        """
        if self._conn is None:
            return []

        try:
            cursor = self._conn.cursor()
            cursor.execute(
                f"""
                SELECT username, cooldown_duration_minutes, auto_unblock_enabled,
                       last_cooldown_started_at, cooldown_count
                FROM {self.TABLE_NAME}
                WHERE last_cooldown_started_at IS NOT NULL
                """
            )
            rows = cursor.fetchall()
            configs = []
            now = datetime.now()
            for row in rows:
                config = AlwaysAvailableAccountConfig(
                    username=row[0],
                    cooldown_duration_minutes=row[1],
                    auto_unblock_enabled=bool(row[2]),
                    last_cooldown_started_at=(
                        datetime.fromisoformat(row[3]) if row[3] else None
                    ),
                    cooldown_count=row[4] or 0,
                )
                # Only include if cooldown hasn't expired
                if not config.should_auto_unblock(now):
                    configs.append(config)
            return configs
        except Exception:
            return []

    def increment_cooldown_count(self, username: str) -> bool:
        """Increment the cooldown count for an account.

        Args:
            username: The account username

        Returns:
            True if update was successful
        """
        if self._conn is None:
            return False

        try:
            cursor = self._conn.cursor()
            cursor.execute(
                f"""
                UPDATE {self.TABLE_NAME}
                SET cooldown_count = cooldown_count + 1
                WHERE username = ?
                """,
                (username,),
            )
            self._conn.commit()
            return cursor.rowcount > 0
        except Exception:
            return False


__all__ = ["AlwaysAvailableAccountRepository"]
