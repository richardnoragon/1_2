"""
Migration 001: Initial Schema Setup with Security Enhancements

This migration creates the initial database schema with security tables
for theme data protection, directory security, and audit logging.
"""

import sqlite3
from ..migration_base import MigrationBase, MigrationMetadata, ValidationResult


class Migration001InitialSchema(MigrationBase):
    """Initial database schema setup with security enhancements."""

    @property
    def metadata(self) -> MigrationMetadata:
        return MigrationMetadata(
            version="001",
            description="Initial schema setup with security tables",
            dependencies=[],
            estimated_duration_ms=5000,
            breaking_changes=False,
            rollback_supported=True,
        )

    def up(self, connection: sqlite3.Connection) -> None:
        """Create initial schema with security enhancements."""

        # Create enhanced user preferences table with encryption support
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS user_preferences_secure (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL DEFAULT 'default',
                preference_category TEXT NOT NULL,
                preference_key TEXT NOT NULL,
                encrypted_value BLOB,
                value_type TEXT NOT NULL DEFAULT 'string',
                encryption_version INTEGER DEFAULT 1,
                integrity_hash TEXT NOT NULL,
                is_pii_sensitive BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, preference_category, preference_key)
            )
        """
        )

        # Create audit log table for preference changes
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS preference_audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                preference_category TEXT NOT NULL,
                preference_key TEXT NOT NULL,
                operation TEXT NOT NULL 
                    CHECK (operation IN ('create', 'read', 'update', 'delete')),
                old_value_hash TEXT,
                new_value_hash TEXT,
                ip_address TEXT,
                user_agent TEXT,
                session_id TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                success BOOLEAN DEFAULT TRUE,
                error_message TEXT
            )
        """
        )

        # Create indexes for performance
        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_user_preferences_secure_user 
            ON user_preferences_secure(user_id)
        """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_user_preferences_secure_category 
            ON user_preferences_secure(preference_category)
        """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_preference_audit_log_timestamp 
            ON preference_audit_log(timestamp DESC)
        """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_preference_audit_log_user 
            ON preference_audit_log(user_id)
        """
        )

        connection.commit()

    def down(self, connection: sqlite3.Connection) -> None:
        """Rollback initial schema."""
        # Drop indexes first
        connection.execute(
            "DROP INDEX IF EXISTS idx_preference_audit_log_user"
        )
        connection.execute(
            "DROP INDEX IF EXISTS idx_preference_audit_log_timestamp"
        )
        connection.execute(
            "DROP INDEX IF EXISTS idx_user_preferences_secure_category"
        )
        connection.execute(
            "DROP INDEX IF EXISTS idx_user_preferences_secure_user"
        )

        # Drop tables
        connection.execute("DROP TABLE IF EXISTS preference_audit_log")
        connection.execute("DROP TABLE IF EXISTS user_preferences_secure")

        connection.commit()

    def validate_preconditions(
        self, connection: sqlite3.Connection
    ) -> ValidationResult:
        """Validate that migration can be safely executed."""
        # Check if tables already exist
        cursor = connection.execute(
            """
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name IN ('user_preferences_secure', 'preference_audit_log')
        """
        )
        existing_tables = [row[0] for row in cursor.fetchall()]

        if existing_tables:
            return ValidationResult(
                success=False,
                message=f"Tables already exist: {existing_tables}",
            )

        return ValidationResult(
            success=True, message="Preconditions satisfied"
        )

    def validate_postconditions(
        self, connection: sqlite3.Connection
    ) -> ValidationResult:
        """Validate that migration was executed successfully."""
        # Verify tables were created
        cursor = connection.execute(
            """
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name IN ('user_preferences_secure', 'preference_audit_log')
        """
        )
        created_tables = [row[0] for row in cursor.fetchall()]

        expected_tables = ["user_preferences_secure", "preference_audit_log"]
        if set(created_tables) != set(expected_tables):
            return ValidationResult(
                success=False,
                message=f"Expected tables {expected_tables}, found {created_tables}",
            )

        # Verify indexes were created
        cursor = connection.execute(
            """
            SELECT name FROM sqlite_master 
            WHERE type='index' AND name LIKE 'idx_user_preferences%'
        """
        )
        indexes = [row[0] for row in cursor.fetchall()]

        if (
            len(indexes) < 2
        ):  # Should have at least 2 indexes for user_preferences_secure
            return ValidationResult(
                success=False,
                message=f"Expected at least 2 indexes, found {len(indexes)}",
            )

        return ValidationResult(
            success=True, message="Migration completed successfully"
        )
