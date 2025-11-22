"""
Database Manager for Richard's File Utilities.

Provides centralized SQLite management with connection pooling, schema
migrations, and backup support.
"""

import json
import logging
import shutil
import sqlite3
import threading
import uuid
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

PREFERENCE_SCHEMA_VERSION = "1.1.0"
PREFERENCE_BOOTSTRAP_KEY = "pref/2025-11-11/config-bootstrap"
_PREFERENCE_TABLE = "user_preferences"
_QUERY_LABEL = "Query: %s"
_PARAMS_LABEL = "Params: %s"


# Custom Database Exception Classes
class DatabaseError(Exception):
    """Base exception for database operations."""


class DatabaseQueryError(DatabaseError):
    """Exception for database query failures."""


class DatabaseUpdateError(DatabaseError):
    """Exception for database update/insert/delete failures."""


class DatabaseConnectionError(DatabaseError):
    """Exception for database connection failures."""


class DatabaseManager:
    """Centralized SQLite database manager with singleton pattern."""

    _instance = None
    _lock = threading.Lock()
    _db_path_override: Optional[Path]

    def __new__(cls, db_path: Optional[Union[str, Path]] = None):
        """Ensure singleton pattern; capture optional db_path override."""

        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(DatabaseManager, cls).__new__(cls)
                    cls._instance._initialized = False
                    cls._instance._db_path_override = None
        if db_path is not None:
            cls._instance._db_path_override = Path(db_path)
        return cls._instance

    def __init__(self, db_path: Optional[Union[str, Path]] = None):
        """Initialize the database manager."""

        if not getattr(self, "_initialized", False):
            override = getattr(self, "_db_path_override", None)
            if db_path is not None:
                override = Path(db_path)
                self._db_path_override = override
            self._setup_database(override)
            self._initialized = True

    def _setup_database(self, db_path: Optional[Union[str, Path]] = None):
        """Setup database management system."""

        if db_path is not None:
            self.db_file = Path(db_path)
            self.db_dir = self.db_file.parent
            self.db_dir.mkdir(parents=True, exist_ok=True)
        else:
            self.db_dir = Path("data")
            self.db_dir.mkdir(exist_ok=True)
            self.db_file = self.db_dir / "rfu_database.db"

        self.backup_dir = self.db_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)

        # Connection pool settings
        self.max_connections = 10
        self.connection_pool: List[sqlite3.Connection] = []
        self.pool_lock = threading.Lock()

        # Setup logging
        self.logger = logging.getLogger("RFU.DatabaseManager")

        # Preference schema mode (canonical vs identity-managed)
        self._preference_schema = "canonical"

        # Session tracking
        self.session_id = str(uuid.uuid4())

        # Initialize database
        self._initialize_database()

        self.logger.info("DatabaseManager initialized successfully")

    def _initialize_database(self):
        """Initialize database schema and configuration."""
        try:
            # Create initial connection to set up database
            with self.get_connection() as conn:
                # Enable WAL mode for better concurrency
                conn.execute("PRAGMA journal_mode=WAL")
                # Enable foreign key constraints
                conn.execute("PRAGMA foreign_keys=ON")
                # Set reasonable timeout
                conn.execute("PRAGMA busy_timeout=30000")

                # Create schema
                self._create_schema(conn)

                # Create indexes
                self._create_indexes(conn)

                # Create triggers
                self._create_triggers(conn)

                # Insert initial data
                self._insert_initial_data(conn)

                conn.commit()

            self.logger.info("Database schema initialized successfully")

        except Exception as error:
            self.logger.error("Failed to initialize database: %s", error)
            raise

        self._bootstrap_preferences_once()

    def _create_schema(self, conn: sqlite3.Connection):
        """Create database schema."""

        # Application Settings Table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS app_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                section TEXT NOT NULL CHECK(length(section) > 0),
                key TEXT NOT NULL CHECK(length(key) > 0),
                value TEXT NOT NULL,
                value_type TEXT NOT NULL DEFAULT 'string'
                    CHECK (
                        value_type IN (
                            'string',
                            'int',
                            'float',
                            'bool',
                            'json'
                        )
                    ),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(section, key)
            )
        """
        )

        # File History Table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS file_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL,
                file_name TEXT NOT NULL,
                file_size INTEGER,
                file_type TEXT,
                directory_path TEXT NOT NULL,
                access_count INTEGER DEFAULT 1,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                first_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                tool_name TEXT,
                operation_type TEXT,
                metadata TEXT,
                UNIQUE(file_path)
            )
        """
        )

        # Directory History Table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS directory_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                directory_path TEXT NOT NULL UNIQUE,
                access_count INTEGER DEFAULT 1,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                first_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_favorite BOOLEAN DEFAULT FALSE,
                tool_name TEXT,
                metadata TEXT
            )
        """
        )

        # Application Logs Table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS app_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                level TEXT NOT NULL,
                logger_name TEXT NOT NULL,
                message TEXT NOT NULL,
                module TEXT,
                function TEXT,
                line_number INTEGER,
                tool_name TEXT,
                session_id TEXT,
                metadata TEXT
            )
        """
        )

        # Tool Usage Statistics Table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tool_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tool_name TEXT NOT NULL,
                operation_type TEXT,
                usage_count INTEGER DEFAULT 1,
                last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                first_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                success_count INTEGER DEFAULT 0,
                error_count INTEGER DEFAULT 0,
                total_execution_time_ms INTEGER DEFAULT 0,
                metadata TEXT,
                UNIQUE(tool_name, operation_type)
            )
        """
        )

        # User preference core tables and companions
        self._ensure_user_preferences_schema(conn)
        self._ensure_preference_support_tables(conn)

        # Identity tables
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS user_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                login_attempts INTEGER NOT NULL DEFAULT 0,
                is_blocked BOOLEAN NOT NULL DEFAULT 0,
                preferences_user_id TEXT NOT NULL,
                reset_required BOOLEAN NOT NULL DEFAULT 0,
                last_login TIMESTAMP,
                last_failed_login TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        self._migrate_admin_action_audit_table(conn)

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS admin_action_audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                action TEXT NOT NULL,
                actor TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # Database Metadata Table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS db_metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

    def _ensure_user_preferences_schema(
        self,
        conn: sqlite3.Connection,
    ) -> None:
        """Create or migrate user preferences to the canonical schema."""

        columns = self._get_table_columns(conn, _PREFERENCE_TABLE)
        if not columns:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL DEFAULT 'default',
                    preference_category TEXT NOT NULL,
                    preference_key TEXT NOT NULL,
                    preference_value TEXT NOT NULL,
                    value_type TEXT NOT NULL CHECK (
                        value_type IN ('string','int','float','bool','json')
                    ),
                    is_encrypted BOOLEAN NOT NULL DEFAULT 0,
                    source TEXT NOT NULL DEFAULT 'rfu-core',
                    schema_version INTEGER NOT NULL DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, preference_category, preference_key)
                )
                """
            )
            self._preference_schema = "canonical"
            return

        if self._is_identity_preference_schema(columns):
            self._preference_schema = "identity"
            self.logger.info(
                "Detected identity-managed preference schema; canonical "
                "migrations disabled",
            )
            return

        desired = {
            "id",
            "user_id",
            "preference_category",
            "preference_key",
            "preference_value",
            "value_type",
            "is_encrypted",
            "source",
            "schema_version",
            "created_at",
            "updated_at",
        }

        legacy_signature = "setting_name" in columns or "category" in columns
        missing = desired.difference(columns)
        if legacy_signature or missing:
            self.logger.info(
                "Upgrading %s table to Preference schema v%s",
                _PREFERENCE_TABLE,
                PREFERENCE_SCHEMA_VERSION,
            )
            self._rebuild_user_preferences_table(conn, columns)
            self._preference_schema = "canonical"

    def _ensure_preference_support_tables(
        self,
        conn: sqlite3.Connection,
    ) -> None:
        """Ensure audit and migration tracking tables exist."""

        if self._preference_schema == "identity":
            self.logger.debug(
                "Skipping preference support tables for identity-managed " "database",
            )
            return

        self._create_preference_audit_log_table(conn)
        self._migrate_preference_audit_log(conn)

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS preference_migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                migration_key TEXT NOT NULL UNIQUE,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                applied_by TEXT,
                notes TEXT
            )
            """
        )

        self._ensure_initial_preference_audit(conn)

    def _migrate_admin_action_audit_table(
        self,
        conn: sqlite3.Connection,
    ) -> None:
        """Rename legacy user_account_audit table if present."""

        legacy_columns = self._get_table_columns(conn, "user_account_audit")
        new_columns = self._get_table_columns(conn, "admin_action_audit")

        if legacy_columns and not new_columns:
            self.logger.info(
                "Renaming user_account_audit table to admin_action_audit for"
                " consistency",
            )
            conn.execute("ALTER TABLE user_account_audit RENAME TO admin_action_audit")
            conn.execute("DROP INDEX IF EXISTS idx_user_account_audit_user")

    @staticmethod
    def _create_preference_audit_log_table(
        conn: sqlite3.Connection,
    ) -> None:
        """Create the preference_audit_log table if it does not exist."""

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS preference_audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                preference_category TEXT NOT NULL,
                preference_key TEXT NOT NULL,
                change_type TEXT NOT NULL CHECK (
                    change_type IN ('insert','update','delete')
                ),
                value_type TEXT,
                old_value TEXT,
                new_value TEXT,
                changed_by TEXT,
                change_reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

    def _migrate_preference_audit_log(
        self,
        conn: sqlite3.Connection,
    ) -> None:
        """Ensure preference_audit_log matches the expected schema."""

        columns = self._get_table_columns(conn, "preference_audit_log")
        if not columns:
            return

        expected_columns = {
            "id",
            "user_id",
            "preference_category",
            "preference_key",
            "change_type",
            "value_type",
            "old_value",
            "new_value",
            "changed_by",
            "change_reason",
            "created_at",
        }

        missing_columns = expected_columns.difference(columns)
        legacy_signature = "operation" in columns or "action" in columns

        if missing_columns or legacy_signature:
            self._rebuild_preference_audit_log(conn, columns)

    @staticmethod
    def _choose_column_expr(
        available: Set[str],
        preferred: Tuple[str, ...],
        default: str,
    ) -> str:
        """Return first matching column expression or default."""

        for name in preferred:
            if name in available:
                return name
        return default

    def _rebuild_preference_audit_log(
        self,
        conn: sqlite3.Connection,
        columns: Set[str],
    ) -> None:
        """Rebuild preference_audit_log to the canonical schema."""

        legacy_table = "preference_audit_log_legacy"

        self.logger.info(
            "Rebuilding preference_audit_log table to canonical schema",
        )

        conn.execute(f"ALTER TABLE preference_audit_log RENAME TO {legacy_table}")

        self._create_preference_audit_log_table(conn)

        user_expr = self._choose_column_expr(
            columns,
            ("user_id",),
            "'default'",
        )
        category_expr = self._choose_column_expr(
            columns,
            ("preference_category", "category"),
            "'general'",
        )
        key_expr = self._choose_column_expr(
            columns,
            ("preference_key", "setting_name"),
            "'unknown'",
        )
        change_expr = self._choose_column_expr(
            columns,
            ("change_type", "operation"),
            "'insert'",
        )
        value_type_expr = self._choose_column_expr(
            columns,
            ("value_type",),
            "'string'",
        )
        old_value_expr = self._choose_column_expr(
            columns,
            ("old_value",),
            "NULL",
        )
        new_value_expr = self._choose_column_expr(
            columns,
            ("new_value",),
            "NULL",
        )
        changed_by_expr = self._choose_column_expr(
            columns,
            ("changed_by", "actor"),
            "'legacy'",
        )
        change_reason_expr = self._choose_column_expr(
            columns,
            ("change_reason",),
            "'legacy-import'",
        )
        created_at_expr = self._choose_column_expr(
            columns,
            ("created_at",),
            "CURRENT_TIMESTAMP",
        )

        conn.execute(
            f"""
            INSERT INTO preference_audit_log (
                user_id,
                preference_category,
                preference_key,
                change_type,
                value_type,
                old_value,
                new_value,
                changed_by,
                change_reason,
                created_at
            )
            SELECT
                {user_expr},
                {category_expr},
                {key_expr},
                {change_expr},
                {value_type_expr},
                {old_value_expr},
                {new_value_expr},
                {changed_by_expr},
                {change_reason_expr},
                {created_at_expr}
            FROM {legacy_table}
            """
        )

        conn.execute(f"DROP TABLE {legacy_table}")

    def _ensure_initial_preference_audit(
        self,
        conn: sqlite3.Connection,
    ) -> None:
        """Seed audit log for existing preference rows."""

        if self._preference_schema == "identity":
            return

        if not self._table_exists(conn, _PREFERENCE_TABLE):
            return

        cursor = conn.execute("SELECT COUNT(1) FROM preference_audit_log")
        if cursor.fetchone()[0]:
            return

        cursor = conn.execute(f"SELECT COUNT(1) FROM {_PREFERENCE_TABLE}")
        if not cursor.fetchone()[0]:
            return

        conn.execute(
            """
            INSERT INTO preference_audit_log (
                user_id,
                preference_category,
                preference_key,
                change_type,
                value_type,
                old_value,
                new_value,
                changed_by,
                change_reason
            )
            SELECT
                user_id,
                preference_category,
                preference_key,
                'insert' AS change_type,
                value_type,
                NULL AS old_value,
                preference_value AS new_value,
                source AS changed_by,
                'initial-import' AS change_reason
            FROM user_preferences
            """
        )

    def _rebuild_user_preferences_table(
        self,
        conn: sqlite3.Connection,
        columns: Set[str],
    ) -> None:
        """Recreate user preferences table and migrate legacy data."""

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        legacy_table = f"{_PREFERENCE_TABLE}_legacy_{timestamp}"
        conn.execute(f"ALTER TABLE {_PREFERENCE_TABLE} RENAME TO {legacy_table}")

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL DEFAULT 'default',
                preference_category TEXT NOT NULL,
                preference_key TEXT NOT NULL,
                preference_value TEXT NOT NULL,
                value_type TEXT NOT NULL CHECK (
                    value_type IN ('string','int','float','bool','json')
                ),
                is_encrypted BOOLEAN NOT NULL DEFAULT 0,
                source TEXT NOT NULL DEFAULT 'legacy-bootstrap',
                schema_version INTEGER NOT NULL DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, preference_category, preference_key)
            )
            """
        )

        user_expr = "user_id" if "user_id" in columns else "'default'"
        category_expr = (
            "preference_category" if "preference_category" in columns else "category"
        )
        key_expr = "preference_key" if "preference_key" in columns else "setting_name"
        value_expr = (
            "preference_value" if "preference_value" in columns else "setting_value"
        )
        value_type_expr = "value_type" if "value_type" in columns else "'string'"
        encrypted_expr = "is_encrypted" if "is_encrypted" in columns else "0"
        created_expr = "created_at" if "created_at" in columns else "CURRENT_TIMESTAMP"
        updated_expr = "updated_at" if "updated_at" in columns else "CURRENT_TIMESTAMP"

        conn.execute(
            f"""
            INSERT INTO user_preferences (
                user_id,
                preference_category,
                preference_key,
                preference_value,
                value_type,
                is_encrypted,
                source,
                schema_version,
                created_at,
                updated_at
            )
            SELECT
                {user_expr} AS user_id,
                {category_expr} AS preference_category,
                {key_expr} AS preference_key,
                {value_expr} AS preference_value,
                CASE
                    WHEN {value_type_expr} IN (
                        'string',
                        'int',
                        'float',
                        'bool',
                        'json'
                    )
                        THEN {value_type_expr}
                    ELSE 'string'
                END AS value_type,
                CASE
                    WHEN {encrypted_expr} IN (1, '1', 'true', 'TRUE')
                        THEN 1
                    ELSE 0
                END AS is_encrypted,
                'legacy-bootstrap' AS source,
                1 AS schema_version,
                {created_expr} AS created_at,
                {updated_expr} AS updated_at
            FROM {legacy_table}
            """
        )

    @staticmethod
    def _is_identity_preference_schema(columns: Set[str]) -> bool:
        """Return True when the preference table matches identity schema."""

        identity_markers = {"preferences_id", "payload"}
        canonical_markers = {"preference_key", "preference_category"}
        return identity_markers.issubset(columns) and not (canonical_markers & columns)

    @staticmethod
    def _get_table_columns(conn: sqlite3.Connection, table: str) -> Set[str]:
        """Return the set of column names for a table."""

        try:
            cursor = conn.execute(f"PRAGMA table_info({table})")
        except sqlite3.OperationalError:
            return set()
        return {row[1] for row in cursor.fetchall()}

    @staticmethod
    def _table_exists(conn: sqlite3.Connection, table: str) -> bool:
        """Return True when the table exists in the database."""

        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table,),
        )
        return cursor.fetchone() is not None

    def _create_indexes(self, conn: sqlite3.Connection):
        """Create database indexes for performance."""

        indexes = [
            # File history indexes
            (
                "CREATE INDEX IF NOT EXISTS idx_file_history_path "
                "ON file_history(file_path)"
            ),
            (
                "CREATE INDEX IF NOT EXISTS idx_file_history_accessed "
                "ON file_history(last_accessed DESC)"
            ),
            (
                "CREATE INDEX IF NOT EXISTS idx_file_history_tool "
                "ON file_history(tool_name)"
            ),
            # Directory history indexes
            (
                "CREATE INDEX IF NOT EXISTS idx_directory_history_path "
                "ON directory_history(directory_path)"
            ),
            (
                "CREATE INDEX IF NOT EXISTS idx_directory_history_accessed "
                "ON directory_history(last_accessed DESC)"
            ),
            (
                "CREATE INDEX IF NOT EXISTS idx_directory_history_favorite "
                "ON directory_history(is_favorite)"
            ),
            # Application logs indexes
            (
                "CREATE INDEX IF NOT EXISTS idx_app_logs_timestamp "
                "ON app_logs(timestamp DESC)"
            ),
            ("CREATE INDEX IF NOT EXISTS idx_app_logs_level " "ON app_logs(level)"),
            (
                "CREATE INDEX IF NOT EXISTS idx_app_logs_logger "
                "ON app_logs(logger_name)"
            ),
            (
                "CREATE INDEX IF NOT EXISTS idx_app_logs_session "
                "ON app_logs(session_id)"
            ),
            # Tool usage indexes
            (
                "CREATE INDEX IF NOT EXISTS idx_tool_usage_name "
                "ON tool_usage(tool_name)"
            ),
            (
                "CREATE INDEX IF NOT EXISTS idx_tool_usage_last_used "
                "ON tool_usage(last_used DESC)"
            ),
            # Settings indexes
            (
                "CREATE INDEX IF NOT EXISTS idx_app_settings_section "
                "ON app_settings(section)"
            ),
            (
                "CREATE INDEX IF NOT EXISTS idx_app_settings_key "
                "ON app_settings(section, key)"
            ),
            (
                "CREATE INDEX IF NOT EXISTS idx_user_accounts_role "
                "ON user_accounts(role)"
            ),
        ]

        if self._preference_schema != "identity":
            indexes.extend(
                [
                    (
                        "CREATE INDEX IF NOT EXISTS "
                        "idx_user_pref_user_category "
                        "ON user_preferences(user_id, preference_category)"
                    ),
                    (
                        "CREATE INDEX IF NOT EXISTS "
                        "idx_user_pref_category_key "
                        "ON user_preferences(preference_category, "
                        "preference_key)"
                    ),
                    (
                        "CREATE INDEX IF NOT EXISTS idx_user_pref_updated_at "
                        "ON user_preferences(updated_at DESC)"
                    ),
                    (
                        "CREATE INDEX IF NOT EXISTS idx_pref_audit_user_time "
                        "ON preference_audit_log(user_id, created_at DESC)"
                    ),
                ]
            )

        admin_columns = self._get_table_columns(conn, "admin_action_audit")
        if "username" in admin_columns:
            indexes.append(
                (
                    "CREATE INDEX IF NOT EXISTS idx_admin_action_audit_user "
                    "ON admin_action_audit(username, created_at DESC)"
                )
            )
        elif {"actor_username", "created_at"}.issubset(admin_columns):
            indexes.append(
                (
                    "CREATE INDEX IF NOT EXISTS idx_admin_action_actor_time "
                    "ON admin_action_audit(actor_username, created_at DESC)"
                )
            )

        for index_sql in indexes:
            conn.execute(index_sql)

    def _create_triggers(self, conn: sqlite3.Connection):
        """Create database triggers for automation."""

        # Update timestamp trigger for app_settings
        conn.execute(
            """
            CREATE TRIGGER IF NOT EXISTS update_app_settings_timestamp
            AFTER UPDATE ON app_settings
            BEGIN
                UPDATE app_settings
                SET updated_at = CURRENT_TIMESTAMP
                WHERE id = NEW.id;
            END
        """
        )

        if self._preference_schema != "identity":
            # Update timestamp trigger for user_preferences
            conn.execute(
                """
                CREATE TRIGGER IF NOT EXISTS update_user_preferences_timestamp
                AFTER UPDATE ON user_preferences
                BEGIN
                    UPDATE user_preferences
                    SET updated_at = CURRENT_TIMESTAMP
                    WHERE id = NEW.id;
                END
            """
            )

            # Audit triggers for user_preferences changes
            conn.execute(
                """
                CREATE TRIGGER IF NOT EXISTS audit_user_preferences_insert
                AFTER INSERT ON user_preferences
                BEGIN
                    INSERT INTO preference_audit_log (
                        user_id,
                        preference_category,
                        preference_key,
                        change_type,
                        value_type,
                        old_value,
                        new_value,
                        changed_by,
                        change_reason
                    ) VALUES (
                        NEW.user_id,
                        NEW.preference_category,
                        NEW.preference_key,
                        'insert',
                        NEW.value_type,
                        NULL,
                        NEW.preference_value,
                        NEW.source,
                        'bootstrap'
                    );
                END
            """
            )

            conn.execute(
                """
                CREATE TRIGGER IF NOT EXISTS audit_user_preferences_update
                AFTER UPDATE ON user_preferences
                BEGIN
                    INSERT INTO preference_audit_log (
                        user_id,
                        preference_category,
                        preference_key,
                        change_type,
                        value_type,
                        old_value,
                        new_value,
                        changed_by,
                        change_reason
                    ) VALUES (
                        NEW.user_id,
                        NEW.preference_category,
                        NEW.preference_key,
                        'update',
                        NEW.value_type,
                        OLD.preference_value,
                        NEW.preference_value,
                        COALESCE(NEW.source, 'rfu-core'),
                        'update'
                    );
                END
            """
            )

            conn.execute(
                """
                CREATE TRIGGER IF NOT EXISTS audit_user_preferences_delete
                AFTER DELETE ON user_preferences
                BEGIN
                    INSERT INTO preference_audit_log (
                        user_id,
                        preference_category,
                        preference_key,
                        change_type,
                        value_type,
                        old_value,
                        new_value,
                        changed_by,
                        change_reason
                    ) VALUES (
                        OLD.user_id,
                        OLD.preference_category,
                        OLD.preference_key,
                        'delete',
                        OLD.value_type,
                        OLD.preference_value,
                        NULL,
                        COALESCE(OLD.source, 'rfu-core'),
                        'delete'
                    );
                END
            """
            )

        # Increment access count for file_history
        conn.execute(
            """
            CREATE TRIGGER IF NOT EXISTS increment_file_access
            AFTER UPDATE ON file_history
            WHEN NEW.last_accessed > OLD.last_accessed
            BEGIN
                UPDATE file_history
                SET access_count = access_count + 1
                WHERE id = NEW.id;
            END
        """
        )

        # Increment access count for directory_history
        conn.execute(
            """
            CREATE TRIGGER IF NOT EXISTS increment_directory_access
            AFTER UPDATE ON directory_history
            WHEN NEW.last_accessed > OLD.last_accessed
            BEGIN
                UPDATE directory_history
                SET access_count = access_count + 1
                WHERE id = NEW.id;
            END
        """
        )

        user_account_columns = self._get_table_columns(conn, "user_accounts")
        if "id" in user_account_columns:
            conn.execute(
                """
                CREATE TRIGGER IF NOT EXISTS update_user_accounts_timestamp
                AFTER UPDATE ON user_accounts
                BEGIN
                    UPDATE user_accounts
                    SET updated_at = CURRENT_TIMESTAMP
                    WHERE id = NEW.id;
                END
                """
            )
        elif "username" in user_account_columns:
            conn.execute(
                """
                CREATE TRIGGER IF NOT EXISTS update_user_accounts_timestamp
                AFTER UPDATE ON user_accounts
                BEGIN
                    UPDATE user_accounts
                    SET updated_at = CURRENT_TIMESTAMP
                    WHERE username = NEW.username;
                END
                """
            )

    def _insert_initial_data(self, conn: sqlite3.Connection):
        """Insert initial metadata and configuration."""

        # Database version and metadata
        metadata = [
            ("schema_version", "1.0.0"),
            ("created_at", datetime.now().isoformat()),
            ("session_id", self.session_id),
            ("application_version", "1.0.0"),
            ("preference_schema_version", PREFERENCE_SCHEMA_VERSION),
        ]

        conn.executemany(
            "INSERT OR REPLACE INTO db_metadata (key, value) VALUES (?, ?)",
            metadata,
        )

        # Default application settings
        default_settings = [
            ("database", "auto_vacuum", "true", "boolean"),
            ("database", "backup_retention_days", "30", "integer"),
            ("database", "log_retention_days", "90", "integer"),
            ("database", "max_file_history_entries", "1000", "integer"),
            ("database", "enable_analytics", "true", "boolean"),
        ]

        conn.executemany(
            """
            INSERT OR IGNORE INTO app_settings
                (section, key, value, value_type)
            VALUES (?, ?, ?, ?)
            """,
            default_settings,
        )

    @contextmanager
    def get_connection(self):
        """Get a database connection from the pool."""
        conn = None
        try:
            with self.pool_lock:
                if self.connection_pool:
                    conn = self.connection_pool.pop()
                else:
                    conn = sqlite3.connect(
                        str(self.db_file),
                        timeout=30.0,
                        check_same_thread=False,
                    )
                    conn.row_factory = sqlite3.Row
                    conn.execute("PRAGMA foreign_keys=ON")

            yield conn

        except sqlite3.Error as error:
            if conn:
                conn.rollback()
            self.logger.error("Database error: %s", error)
            raise
        finally:
            if conn:
                with self.pool_lock:
                    if len(self.connection_pool) < self.max_connections:
                        self.connection_pool.append(conn)
                    else:
                        conn.close()

    def execute_query(self, query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        """Run a SELECT query with consistent error handling."""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(query, params)
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except sqlite3.DatabaseError as error:
            self.logger.error("Database error in query execution: %s", error)
            self.logger.error(_QUERY_LABEL, query)
            self.logger.error(_PARAMS_LABEL, params)
            msg = f"Database query failed: {error}"
            raise DatabaseQueryError(msg) from error
        except (TypeError, ValueError) as error:
            self.logger.error(_QUERY_LABEL, query)
            self.logger.error(_PARAMS_LABEL, params)
            msg = f"Query execution failed: {error}"
            raise DatabaseError(msg) from error

    def execute_update(self, query: str, params: Tuple = ()) -> int:
        """Run a mutating query and report affected rows."""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(query, params)
                conn.commit()
                return int(cursor.rowcount)
        except sqlite3.DatabaseError as error:
            self.logger.error("Database error in update execution: %s", error)
            self.logger.error(_QUERY_LABEL, query)
            self.logger.error(_PARAMS_LABEL, params)
            msg = f"Database update failed: {error}"
            raise DatabaseUpdateError(msg) from error
        except (TypeError, ValueError) as error:
            self.logger.error(_QUERY_LABEL, query)
            self.logger.error(_PARAMS_LABEL, params)
            msg = f"Update execution failed: {error}"
            raise DatabaseError(msg) from error

    def execute_many(self, query: str, params_list: List[Tuple]) -> int:
        """Execute multiple queries with different parameters."""
        try:
            with self.get_connection() as conn:
                cursor = conn.executemany(query, params_list)
                conn.commit()
                return int(cursor.rowcount)
        except sqlite3.DatabaseError as error:
            self.logger.error("Batch execution failed: %s", error)
            return 0

    def backup_database(self, backup_name: Optional[str] = None) -> bool:
        """Create a backup of the database."""
        try:
            # Validation: Check if database file exists
            if not self.db_file.exists():
                self.logger.error("Database file does not exist, cannot backup")
                return False

            # Validation: Check if backup directory exists and is writable
            if not self.backup_dir.exists():
                try:
                    self.backup_dir.mkdir(parents=True, exist_ok=True)
                except OSError as os_error:
                    self.logger.error(
                        "Cannot create backup directory: %s",
                        os_error,
                    )
                    return False

            if backup_name is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"rfu_database_backup_{timestamp}.db"

            # Validation: Sanitize backup name
            backup_name = backup_name.replace("/", "_").replace("\\", "_")
            backup_name = backup_name.strip()
            if not backup_name or backup_name == ".":
                self.logger.error("Invalid backup name")
                return False

            backup_path = self.backup_dir / backup_name
            shutil.copy2(self.db_file, backup_path)

            self.logger.info("Database backed up to: %s", backup_path)
            return True
        except OSError as error:
            self.logger.error("Database backup failed: %s", error)
            return False

    def restore_database(self, backup_path: Union[str, Path]) -> bool:
        """Restore database from a backup with safety measures."""
        try:
            backup_file = Path(backup_path)

            # Validation checks
            if not backup_file.exists():
                self.logger.error("Backup file not found: %s", backup_file)
                return False

            if not backup_file.is_file():
                self.logger.error("Backup path is not a file: %s", backup_file)
                return False

            # Safety: Create a backup of current database before restore
            if self.db_file.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safety_backup_name = f"safety_backup_before_restore_{timestamp}.db"
                self.logger.info(
                    "Creating safety backup: %s",
                    safety_backup_name,
                )
                if not self.backup_database(safety_backup_name):
                    self.logger.warning(
                        "Could not create safety backup, proceeding anyway"
                    )

            # Close all connections
            self.close_all_connections()

            # Restore the database
            shutil.copy2(backup_file, self.db_file)

            # Validate restored database
            try:
                # Quick validation: open and query the restored database
                test_conn = sqlite3.connect(self.db_file)
                test_conn.execute("SELECT 1").fetchone()
                test_conn.close()
            except sqlite3.Error as error:
                self.logger.error(
                    "Restored database validation failed: %s",
                    error,
                )
                return False

            # Reinitialize
            self._initialize_database()

            self.logger.info("Database restored from: %s", backup_file)
            return True
        except (OSError, DatabaseError) as error:
            self.logger.error("Database restore failed: %s", error)
            return False

    def cleanup_old_data(self):
        """Clean up old data based on retention policies."""
        try:
            with self.get_connection() as conn:
                # Get retention settings
                log_retention = self.get_setting(
                    "database",
                    "log_retention_days",
                    90,
                )
                backup_retention = self.get_setting(
                    "database", "backup_retention_days", 30
                )

                # Clean old logs
                cutoff_date = datetime.now() - timedelta(days=log_retention)
                conn.execute(
                    "DELETE FROM app_logs WHERE timestamp < ?",
                    (cutoff_date.isoformat(),),
                )

                # Clean old backups
                backup_cutoff = datetime.now() - timedelta(days=backup_retention)
                for backup_file in self.backup_dir.glob("rfu_database_backup_*.db"):
                    if backup_file.stat().st_mtime < backup_cutoff.timestamp():
                        backup_file.unlink()
                        self.logger.info(
                            "Removed old backup: %s",
                            backup_file,
                        )

                conn.commit()
                self.logger.info("Database cleanup completed")
        except (sqlite3.DatabaseError, OSError) as error:
            self.logger.error("Database cleanup failed: %s", error)

    def vacuum_database(self) -> bool:
        """Perform database vacuum operation."""
        try:
            with self.get_connection() as conn:
                conn.execute("VACUUM")
                self.logger.info("Database vacuum completed")
                return True
        except sqlite3.DatabaseError as error:
            self.logger.error("Database vacuum failed: %s", error)
            return False

    def get_database_info(self) -> Dict[str, Any]:
        """Get database information and statistics."""
        try:
            with self.get_connection() as conn:
                # Get database size
                db_size = self.db_file.stat().st_size if self.db_file.exists() else 0

                # Get table counts
                tables = [
                    "app_settings",
                    "file_history",
                    "directory_history",
                    "app_logs",
                    "tool_usage",
                    "user_preferences",
                ]

                table_counts = {}
                for table in tables:
                    try:
                        cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cursor.fetchone()[0]
                        table_counts[table] = count
                        cursor.close()  # Properly close cursor
                    except sqlite3.Error as error:
                        self.logger.warning(
                            "Could not count table %s: %s", table, error
                        )
                        table_counts[table] = 0

                # Get metadata with proper resource management
                try:
                    cursor = conn.execute("SELECT * FROM db_metadata")
                    metadata = {row["key"]: row["value"] for row in cursor.fetchall()}
                    cursor.close()  # Properly close cursor
                except sqlite3.Error as error:
                    self.logger.warning("Could not fetch metadata: %s", error)
                    metadata = {}

                return {
                    "database_file": str(self.db_file),
                    "database_size_bytes": db_size,
                    "database_size_mb": round(db_size / (1024 * 1024), 2),
                    "table_counts": table_counts,
                    "metadata": metadata,
                    "session_id": self.session_id,
                    "connection_pool_size": len(self.connection_pool),
                }
        except (sqlite3.DatabaseError, OSError) as error:
            self.logger.error("Failed to get database info: %s", error)
            return {}

    def _bootstrap_preferences_once(self) -> None:
        """Backfill preference data one time per installation."""

        if self._preference_schema == "identity":
            self.logger.debug(
                "Preference bootstrap skipped: identity-managed database",
            )
            return

        try:
            if self.preference_migration_applied(PREFERENCE_BOOTSTRAP_KEY):
                return
        except DatabaseError:
            self.logger.exception(
                "Unable to query preference migration state; " "skipping bootstrap",
            )
            return

        try:
            from src.database.migrations.json_to_preferences import (
                migrate_preferences_from_config,
            )
        except ImportError as exc:
            self.logger.debug(
                "Preference bootstrap skipped: migration helper unavailable " "(%s)",
                exc,
            )
            return

        try:
            migrated = migrate_preferences_from_config(db=self)
        except DatabaseError:
            self.logger.exception("Preference bootstrap failed")
            return

        if not migrated:
            return

        try:
            self.record_preference_migration(
                PREFERENCE_BOOTSTRAP_KEY,
                applied_by="config-bootstrap",
                notes="JSON config import and legacy preference migration",
            )
        except DatabaseError:
            self.logger.exception(
                "Preference bootstrap succeeded but recording migration key " "failed",
            )

    def preference_migration_applied(self, migration_key: str) -> bool:
        """Return True when a preference migration key has been recorded."""

        if self._preference_schema == "identity":
            self.logger.debug(
                "Preference migrations not tracked for identity schema",
            )
            return False

        rows = self.execute_query(
            ("SELECT 1 FROM preference_migrations WHERE migration_key = ? " "LIMIT 1"),
            (migration_key,),
        )
        return bool(rows)

    def record_preference_migration(
        self,
        migration_key: str,
        *,
        applied_by: str = "rfu-core",
        notes: Optional[str] = None,
    ) -> None:
        """Persist a preference migration record."""

        if self._preference_schema == "identity":
            self.logger.debug(
                "Skipping preference migration record for identity schema",
            )
            return

        self.execute_update(
            """
            INSERT OR IGNORE INTO preference_migrations (
                migration_key,
                applied_at,
                applied_by,
                notes
            ) VALUES (
                ?,
                CURRENT_TIMESTAMP,
                ?,
                ?
            )
            """,
            (migration_key, applied_by, notes),
        )

    def close_all_connections(self):
        """Close all database connections."""
        with self.pool_lock:
            for conn in self.connection_pool:
                try:
                    conn.close()
                except sqlite3.Error:
                    self.logger.debug(
                        "Error closing database connection", exc_info=True
                    )
            self.connection_pool.clear()

    def get_setting(self, section: str, key: str, default: Any = None) -> Any:
        """Get a setting value from database."""
        try:
            query = (
                "SELECT value, value_type FROM app_settings "
                "WHERE section = ? AND key = ?"
            )
            result = self.execute_query(query, (section, key))

            if result:
                value = result[0]["value"]
                value_type = result[0]["value_type"]

                # Convert value based on type
                if value_type == "integer":
                    return int(value)
                elif value_type == "float":
                    return float(value)
                elif value_type == "boolean":
                    return value.lower() in ("true", "1", "yes")
                elif value_type == "json":
                    return json.loads(value)
                else:
                    return value

            return default
        except (DatabaseError, ValueError) as error:
            self.logger.error(
                "Failed to get setting %s.%s: %s",
                section,
                key,
                error,
            )
            return default

    def __del__(self):
        """Cleanup when object is destroyed."""
        try:
            self.close_all_connections()
        except (DatabaseError, sqlite3.Error):
            self.logger.debug("Cleanup encountered an error", exc_info=True)


def get_database_manager() -> DatabaseManager:
    """Get the global DatabaseManager instance."""
    return DatabaseManager()


__all__ = [
    "DatabaseManager",
    "DatabaseError",
    "DatabaseQueryError",
    "DatabaseUpdateError",
    "DatabaseConnectionError",
    "get_database_manager",
]
