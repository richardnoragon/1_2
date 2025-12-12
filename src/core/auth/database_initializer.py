"""Database initializer for identity and authentication.

Handles database schema migrations and protected account bootstrapping
during application startup. Ensures lockout prevention features are
properly initialized.

Task: T064 - Wire AccountBootstrapService into database initialization
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Protocol

from src.log_manager import get_log_manager

LOGGER = get_log_manager().get_logger("AuthDatabaseInitializer")

# Migration file paths
MIGRATION_006 = Path("scripts/migrations/006_baseline_login_password.sql")
MIGRATION_007 = Path("scripts/migrations/007_lockout_prevention.sql")


class UserAccountRepositoryProtocol(Protocol):
    """Minimal interface for user account persistence."""

    def get(self, username: str) -> Any: ...

    def upsert(self, account: Any) -> None: ...


class IdentityDatabaseInitializer:
    """Initialize identity database with schema and protected accounts.

    Coordinates:
    - Schema version tracking
    - Migration application
    - Protected account bootstrapping
    - First-run vs existing database detection
    """

    SCHEMA_VERSION_TABLE = "rfu_schema_version"
    CURRENT_SCHEMA_VERSION = 7  # 007_lockout_prevention

    def __init__(
        self,
        database_path: str | Path,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        """Initialize the database initializer.

        Args:
            database_path: Path to the identity database
            clock: Optional clock function for testing
        """
        self.db_path = Path(database_path)
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def initialize(
        self,
        *,
        bootstrap_accounts: bool = True,
        show_console: bool = False,
        export_credentials: bool = True,
    ) -> Dict[str, Any]:
        """Initialize the identity database.

        Applies pending migrations and bootstraps protected accounts
        if needed.

        Args:
            bootstrap_accounts: Whether to create protected accounts
            show_console: Whether to display credentials on console
            export_credentials: Whether to export credentials to file

        Returns:
            Dict with initialization results
        """
        result = {
            "success": False,
            "is_first_run": False,
            "migrations_applied": [],
            "current_version": 0,
            "accounts_created": [],
            "accounts_existing": [],
            "error": None,
        }

        try:
            # Ensure database directory exists
            self.db_path.parent.mkdir(parents=True, exist_ok=True)

            # Check if this is a first run
            result["is_first_run"] = not self.db_path.exists()

            with self._connect() as conn:
                # Ensure schema version table exists
                self._ensure_version_table(conn)

                # Get current schema version
                current_version = self._get_schema_version(conn)
                result["current_version"] = current_version

                # Apply pending migrations
                migrations_applied = self._apply_pending_migrations(
                    conn, current_version
                )
                result["migrations_applied"] = migrations_applied

                # Update current version after migrations
                if migrations_applied:
                    result["current_version"] = self._get_schema_version(conn)

            # Bootstrap protected accounts if requested
            if bootstrap_accounts:
                bootstrap_result = self._bootstrap_protected_accounts(
                    show_console=show_console,
                    export_credentials=export_credentials,
                )
                result["accounts_created"] = bootstrap_result.get(
                    "accounts_created", []
                )
                result["accounts_existing"] = bootstrap_result.get(
                    "accounts_existing", []
                )
                if bootstrap_result.get("credentials_file"):
                    result["credentials_file"] = bootstrap_result["credentials_file"]

            result["success"] = True
            LOGGER.info(
                "Database initialization complete. Version: %s, "
                "Migrations: %d, Accounts created: %d",
                result["current_version"],
                len(result["migrations_applied"]),
                len(result["accounts_created"]),
            )

        except Exception as e:
            result["error"] = str(e)
            LOGGER.error("Database initialization failed: %s", e)

        return result

    def needs_migration(self) -> bool:
        """Check if the database needs migration.

        Returns:
            True if migrations are pending
        """
        if not self.db_path.exists():
            return True

        try:
            with self._connect() as conn:
                self._ensure_version_table(conn)
                current = self._get_schema_version(conn)
                return current < self.CURRENT_SCHEMA_VERSION
        except Exception:
            return True

    def get_schema_version(self) -> int:
        """Get the current schema version.

        Returns:
            Current schema version number, or 0 if not initialized
        """
        if not self.db_path.exists():
            return 0

        try:
            with self._connect() as conn:
                self._ensure_version_table(conn)
                return self._get_schema_version(conn)
        except Exception:
            return 0

    def _connect(self) -> sqlite3.Connection:
        """Create database connection with proper settings."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON;")
        return conn

    def _ensure_version_table(self, conn: sqlite3.Connection) -> None:
        """Ensure schema version tracking table exists."""
        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {self.SCHEMA_VERSION_TABLE} (
                version INTEGER PRIMARY KEY,
                applied_at TEXT NOT NULL,
                description TEXT
            )
            """
        )

    def _get_schema_version(self, conn: sqlite3.Connection) -> int:
        """Get the current schema version from the database."""
        cursor = conn.execute(
            f"SELECT MAX(version) as ver FROM {self.SCHEMA_VERSION_TABLE}"
        )
        row = cursor.fetchone()
        if row is None or row["ver"] is None:
            return 0
        return int(row["ver"])

    def _record_migration(
        self,
        conn: sqlite3.Connection,
        version: int,
        description: str,
    ) -> None:
        """Record a migration as applied."""
        now = self._clock().isoformat()
        conn.execute(
            f"""
            INSERT OR REPLACE INTO {self.SCHEMA_VERSION_TABLE}
                (version, applied_at, description)
            VALUES (?, ?, ?)
            """,
            (version, now, description),
        )

    def _apply_pending_migrations(
        self,
        conn: sqlite3.Connection,
        current_version: int,
    ) -> list[str]:
        """Apply any pending migrations.

        Args:
            conn: Database connection
            current_version: Current schema version

        Returns:
            List of migration names that were applied
        """
        applied = []

        # Migration 6: Baseline login/password (006_baseline_login_password.sql)
        if current_version < 6 and MIGRATION_006.exists():
            LOGGER.info("Applying migration 006: baseline_login_password")
            script = MIGRATION_006.read_text(encoding="utf-8")
            conn.executescript(script)
            self._record_migration(
                conn, 6, "006_baseline_login_password - Initial identity schema"
            )
            applied.append("006_baseline_login_password")
            conn.commit()

        # Migration 7: Lockout prevention (007_lockout_prevention.sql)
        if current_version < 7 and MIGRATION_007.exists():
            LOGGER.info("Applying migration 007: lockout_prevention")
            script = MIGRATION_007.read_text(encoding="utf-8")
            conn.executescript(script)
            self._record_migration(
                conn, 7, "007_lockout_prevention - Four-role system and auto-unblock"
            )
            applied.append("007_lockout_prevention")
            conn.commit()

        return applied

    def _bootstrap_protected_accounts(
        self,
        *,
        show_console: bool = False,
        export_credentials: bool = True,
    ) -> Dict[str, Any]:
        """Bootstrap protected accounts using AccountBootstrapService.

        Args:
            show_console: Whether to display credentials on console
            export_credentials: Whether to export credentials to file

        Returns:
            Dict with bootstrap results
        """
        try:
            from src.core.auth.repositories.user_account_repository import (
                UserAccountRepository,
            )
            from src.core.auth.services.account_bootstrap_service import (
                AccountBootstrapService,
            )

            # Create repository
            user_repo = UserAccountRepository(database_path=self.db_path)

            # Create bootstrap service
            bootstrap_service = AccountBootstrapService(
                user_repository=user_repo,
            )

            # Run bootstrap
            result = bootstrap_service.bootstrap_protected_accounts(
                show_console=show_console,
                export_credentials=export_credentials,
            )

            # Convert result to dictionary
            accounts_created = [
                {
                    "username": acc.username,
                    "role": acc.role.value if hasattr(acc.role, "value") else acc.role,
                    "account_type": acc.account_type,
                }
                for acc in result.accounts_created
            ]

            return {
                "success": result.success,
                "accounts_created": accounts_created,
                "accounts_existing": result.accounts_existing,
                "credentials_file": result.credentials_file,
                "error": result.error,
            }

        except ImportError as e:
            LOGGER.warning("Could not import bootstrap components: %s", e)
            return {
                "success": False,
                "error": f"Import error: {e}",
                "accounts_created": [],
                "accounts_existing": [],
            }
        except Exception as e:
            LOGGER.error("Protected account bootstrap failed: %s", e)
            return {
                "success": False,
                "error": str(e),
                "accounts_created": [],
                "accounts_existing": [],
            }


def ensure_identity_database(
    database_path: str | Path,
    *,
    bootstrap_accounts: bool = True,
    show_console: bool = False,
    export_credentials: bool = True,
) -> Dict[str, Any]:
    """Convenience function to ensure identity database is initialized.

    Can be called from application startup to ensure database is ready.

    Args:
        database_path: Path to the identity database
        bootstrap_accounts: Whether to create protected accounts
        show_console: Whether to display credentials on console
        export_credentials: Whether to export credentials to file

    Returns:
        Dict with initialization results
    """
    initializer = IdentityDatabaseInitializer(database_path)
    return initializer.initialize(
        bootstrap_accounts=bootstrap_accounts,
        show_console=show_console,
        export_credentials=export_credentials,
    )


__all__ = [
    "IdentityDatabaseInitializer",
    "ensure_identity_database",
]
