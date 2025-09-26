"""
Migration 002: Add Encryption Support for Theme Data

This migration adds comprehensive encryption support for theme data storage,
including secure themes table, access logging, and key management.
"""

import sqlite3
from ..migration_base import MigrationBase, MigrationMetadata, ValidationResult


class Migration002AddEncryptionSupport(MigrationBase):
    """Add encryption support for theme data."""
    
    @property
    def metadata(self) -> MigrationMetadata:
        return MigrationMetadata(
            version="002",
            description="Add encryption support for theme data storage",
            dependencies=["001"],
            estimated_duration_ms=10000,
            breaking_changes=False,
            rollback_supported=True
        )
    
    def up(self, connection: sqlite3.Connection) -> None:
        """Add encryption support tables."""
        
        # Create secure themes table with encryption
        connection.execute("""
            CREATE TABLE IF NOT EXISTS secure_themes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL DEFAULT 'default',
                theme_name TEXT NOT NULL,
                encrypted_data BLOB NOT NULL,
                integrity_hash TEXT NOT NULL,
                encryption_version INTEGER DEFAULT 1,
                theme_version TEXT DEFAULT '1.0',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                access_count INTEGER DEFAULT 0,
                last_accessed TIMESTAMP,
                UNIQUE(user_id, theme_name)
            )
        """)
        
        # Create theme access audit log
        connection.execute("""
            CREATE TABLE IF NOT EXISTS theme_access_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                theme_name TEXT NOT NULL,
                operation TEXT NOT NULL CHECK (operation IN 
                    ('read', 'write', 'delete', 'export', 'import', 'validate')),
                ip_address TEXT,
                user_agent TEXT,
                session_id TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                success BOOLEAN DEFAULT TRUE,
                error_message TEXT,
                data_size_bytes INTEGER,
                execution_time_ms INTEGER,
                security_level TEXT DEFAULT 'normal' CHECK (security_level IN 
                    ('low', 'normal', 'high', 'critical'))
            )
        """)
        
        # Create theme permissions management
        connection.execute("""
            CREATE TABLE IF NOT EXISTS theme_permissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                theme_name TEXT NOT NULL,
                permission_type TEXT NOT NULL CHECK (permission_type IN 
                    ('read', 'write', 'delete', 'export', 'admin')),
                granted_by TEXT NOT NULL,
                granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                conditions TEXT,
                UNIQUE(user_id, theme_name, permission_type)
            )
        """)
        
        # Create theme backups tracking
        connection.execute("""
            CREATE TABLE IF NOT EXISTS theme_backups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                backup_id TEXT NOT NULL UNIQUE,
                user_id TEXT NOT NULL,
                theme_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_size_bytes INTEGER NOT NULL,
                checksum TEXT NOT NULL,
                encryption_version INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                backup_type TEXT DEFAULT 'automatic' CHECK (backup_type IN 
                    ('automatic', 'manual', 'corruption_recovery')),
                compression_type TEXT DEFAULT 'gzip'
            )
        """)
        
        # Create theme corruption incidents log
        connection.execute("""
            CREATE TABLE IF NOT EXISTS theme_corruption_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                theme_name TEXT NOT NULL,
                corruption_type TEXT NOT NULL,
                detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                corruption_details TEXT,
                recovery_attempted BOOLEAN DEFAULT FALSE,
                recovery_successful BOOLEAN DEFAULT FALSE,
                recovery_method TEXT,
                data_loss_occurred BOOLEAN DEFAULT FALSE,
                backup_used TEXT
            )
        """)
        
        # Create encryption keys management
        connection.execute("""
            CREATE TABLE IF NOT EXISTS theme_encryption_keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key_id TEXT NOT NULL UNIQUE,
                key_type TEXT NOT NULL CHECK (key_type IN 
                    ('master', 'user', 'backup')),
                encrypted_key BLOB NOT NULL,
                salt BLOB NOT NULL,
                key_version INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                rotation_count INTEGER DEFAULT 0,
                last_used TIMESTAMP
            )
        """)
        
        # Create performance indexes
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_secure_themes_user ON secure_themes(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_secure_themes_name ON secure_themes(theme_name)",
            "CREATE INDEX IF NOT EXISTS idx_secure_themes_accessed ON secure_themes(last_accessed DESC)",
            "CREATE INDEX IF NOT EXISTS idx_theme_access_log_timestamp ON theme_access_log(timestamp DESC)",
            "CREATE INDEX IF NOT EXISTS idx_theme_access_log_user ON theme_access_log(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_theme_permissions_user ON theme_permissions(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_theme_backups_user ON theme_backups(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_theme_corruption_detected ON theme_corruption_log(detected_at DESC)",
            "CREATE INDEX IF NOT EXISTS idx_theme_encryption_keys_type ON theme_encryption_keys(key_type)"
        ]
        
        for index_sql in indexes:
            connection.execute(index_sql)
        
        connection.commit()
    
    def down(self, connection: sqlite3.Connection) -> None:
        """Rollback encryption support."""
        # Drop indexes first
        indexes_to_drop = [
            "idx_theme_encryption_keys_type",
            "idx_theme_corruption_detected", 
            "idx_theme_backups_user",
            "idx_theme_permissions_user",
            "idx_theme_access_log_user",
            "idx_theme_access_log_timestamp",
            "idx_secure_themes_accessed",
            "idx_secure_themes_name",
            "idx_secure_themes_user"
        ]
        
        for index_name in indexes_to_drop:
            connection.execute(f"DROP INDEX IF EXISTS {index_name}")
        
        # Drop tables
        tables_to_drop = [
            "theme_encryption_keys",
            "theme_corruption_log", 
            "theme_backups",
            "theme_permissions",
            "theme_access_log",
            "secure_themes"
        ]
        
        for table_name in tables_to_drop:
            connection.execute(f"DROP TABLE IF EXISTS {table_name}")
        
        connection.commit()
    
    def validate_preconditions(self, connection: sqlite3.Connection) -> ValidationResult:
        """Validate dependencies and prerequisites."""
        # Check that migration 001 was applied
        cursor = connection.execute("""
            SELECT version FROM migration_history 
            WHERE version = '001' AND status = 'applied'
        """)
        if not cursor.fetchone():
            return ValidationResult(
                success=False,
                message="Migration 001 must be applied before migration 002"
            )
        
        # Check that required tables from migration 001 exist
        cursor = connection.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name IN ('user_preferences_secure', 'preference_audit_log')
        """)
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        if len(existing_tables) < 2:
            return ValidationResult(
                success=False,
                message="Required tables from migration 001 are missing"
            )
        
        return ValidationResult(success=True, message="Dependencies satisfied")
    
    def validate_postconditions(self, connection: sqlite3.Connection) -> ValidationResult:
        """Validate encryption tables were created."""
        expected_tables = [
            'secure_themes', 'theme_access_log', 'theme_permissions',
            'theme_backups', 'theme_corruption_log', 'theme_encryption_keys'
        ]
        
        cursor = connection.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name IN (?, ?, ?, ?, ?, ?)
        """, expected_tables)
        created_tables = [row[0] for row in cursor.fetchall()]
        
        if set(created_tables) != set(expected_tables):
            return ValidationResult(
                success=False,
                message=f"Expected tables {expected_tables}, found {created_tables}"
            )
        
        # Verify indexes were created
        cursor = connection.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND name LIKE 'idx_secure_themes%'
        """)
        theme_indexes = [row[0] for row in cursor.fetchall()]
        
        if len(theme_indexes) < 3:  # Should have at least 3 indexes for secure_themes
            return ValidationResult(
                success=False,
                message=f"Expected at least 3 theme indexes, found {len(theme_indexes)}"
            )
        
        return ValidationResult(success=True, message="Encryption support added successfully")
