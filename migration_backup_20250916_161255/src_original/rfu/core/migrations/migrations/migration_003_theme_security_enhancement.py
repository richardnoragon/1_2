"""
Migration 003: Theme Security Enhancement

This migration enhances the theme security system with additional tables
for comprehensive access control, backup management, and recovery tracking.
Extends the existing theme security framework from migration 002.
"""

import sqlite3
from ..migration_base import MigrationBase, MigrationMetadata, ValidationResult


class Migration003ThemeSecurityEnhancement(MigrationBase):
    """Enhance theme security system with additional security features."""
    
    @property
    def metadata(self) -> MigrationMetadata:
        return MigrationMetadata(
            version="003",
            description="Enhance theme security with advanced access control, backup management, and recovery tracking",
            dependencies=["002"],
            estimated_duration_ms=15000,
            breaking_changes=False,
            rollback_supported=True
        )
    
    def up(self, connection: sqlite3.Connection) -> None:
        """Add enhanced theme security tables."""
        
        # Create user sessions for theme access control
        connection.execute("""
            CREATE TABLE IF NOT EXISTS theme_user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                session_id TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                active BOOLEAN DEFAULT 1,
                ip_address TEXT,
                user_agent TEXT,
                security_level TEXT DEFAULT 'normal' CHECK (security_level IN 
                    ('low', 'normal', 'high', 'critical'))
            )
        """)
        
        # Create failed authentication attempts tracking
        connection.execute("""
            CREATE TABLE IF NOT EXISTS theme_failed_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                operation TEXT NOT NULL,
                ip_address TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                attempt_details TEXT,
                lockout_until TIMESTAMP
            )
        """)
        
        # Create backup verification log
        connection.execute("""
            CREATE TABLE IF NOT EXISTS theme_backup_verification (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                backup_id TEXT NOT NULL,
                verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                verification_success BOOLEAN NOT NULL,
                error_message TEXT,
                verification_method TEXT DEFAULT 'checksum',
                verification_duration_ms INTEGER,
                FOREIGN KEY (backup_id) REFERENCES theme_backups (backup_id) ON DELETE CASCADE
            )
        """)
        
        # Create recovery operations log
        connection.execute("""
            CREATE TABLE IF NOT EXISTS theme_recovery_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                theme_name TEXT NOT NULL,
                user_id TEXT NOT NULL,
                corruption_type TEXT,
                recovery_strategy TEXT NOT NULL CHECK (recovery_strategy IN 
                    ('backup_restore', 'default_theme', 'safe_mode', 'repair_attempt', 'user_intervention')),
                success BOOLEAN NOT NULL,
                error_message TEXT,
                backup_id_used TEXT,
                recovery_duration_ms INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_recovered BOOLEAN DEFAULT FALSE,
                recovery_quality TEXT CHECK (recovery_quality IN 
                    ('full', 'partial', 'minimal', 'failed'))
            )
        """)
        
        # Create security configuration settings
        connection.execute("""
            CREATE TABLE IF NOT EXISTS theme_security_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                config_key TEXT UNIQUE NOT NULL,
                config_value TEXT NOT NULL,
                config_type TEXT DEFAULT 'string' CHECK (config_type IN 
                    ('string', 'integer', 'boolean', 'json')),
                description TEXT,
                is_encrypted BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_by TEXT
            )
        """)
        
        # Create audit trail for security events
        connection.execute("""
            CREATE TABLE IF NOT EXISTS theme_security_audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL CHECK (event_type IN 
                    ('permission_granted', 'permission_revoked', 'key_rotation', 
                     'config_change', 'security_violation', 'backup_created', 
                     'recovery_initiated', 'encryption_change')),
                user_id TEXT NOT NULL,
                affected_resource TEXT,
                event_details TEXT,
                security_impact TEXT CHECK (security_impact IN 
                    ('none', 'low', 'medium', 'high', 'critical')),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                source_ip TEXT,
                source_component TEXT,
                remediation_required BOOLEAN DEFAULT FALSE
            )
        """)
        
        # Create theme integrity checksums table
        connection.execute("""
            CREATE TABLE IF NOT EXISTS theme_integrity_checksums (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                theme_name TEXT NOT NULL,
                user_id TEXT NOT NULL,
                file_path TEXT NOT NULL,
                checksum_type TEXT DEFAULT 'sha256',
                checksum_value TEXT NOT NULL,
                last_verified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                verification_count INTEGER DEFAULT 1,
                integrity_status TEXT DEFAULT 'valid' CHECK (integrity_status IN 
                    ('valid', 'corrupted', 'missing', 'unknown')),
                UNIQUE(theme_name, user_id, file_path)
            )
        """)
        
        # Add new columns to existing tables for enhanced functionality
        
        # Enhance theme_access_log with additional security fields
        try:
            connection.execute("""
                ALTER TABLE theme_access_log ADD COLUMN 
                authentication_method TEXT DEFAULT 'default'
            """)
        except sqlite3.OperationalError:
            pass  # Column might already exist
        
        try:
            connection.execute("""
                ALTER TABLE theme_access_log ADD COLUMN 
                risk_score INTEGER DEFAULT 0
            """)
        except sqlite3.OperationalError:
            pass
        
        try:
            connection.execute("""
                ALTER TABLE theme_access_log ADD COLUMN 
                geo_location TEXT
            """)
        except sqlite3.OperationalError:
            pass
        
        # Enhance theme_permissions with role-based access
        try:
            connection.execute("""
                ALTER TABLE theme_permissions ADD COLUMN 
                role_name TEXT
            """)
        except sqlite3.OperationalError:
            pass
        
        try:
            connection.execute("""
                ALTER TABLE theme_permissions ADD COLUMN 
                permission_source TEXT DEFAULT 'manual' CHECK (permission_source IN 
                    ('manual', 'role', 'inherited', 'system'))
            """)
        except sqlite3.OperationalError:
            pass
        
        # Enhance theme_backups with metadata
        try:
            connection.execute("""
                ALTER TABLE theme_backups ADD COLUMN 
                metadata TEXT
            """)
        except sqlite3.OperationalError:
            pass
        
        try:
            connection.execute("""
                ALTER TABLE theme_backups ADD COLUMN 
                compressed BOOLEAN DEFAULT 0
            """)
        except sqlite3.OperationalError:
            pass
        
        try:
            connection.execute("""
                ALTER TABLE theme_backups ADD COLUMN 
                verified BOOLEAN DEFAULT 0
            """)
        except sqlite3.OperationalError:
            pass
        
        # Create comprehensive indexes for performance
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_theme_sessions_user ON theme_user_sessions(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_theme_sessions_active ON theme_user_sessions(active, expires_at)",
            "CREATE INDEX IF NOT EXISTS idx_theme_failed_attempts_user ON theme_failed_attempts(user_id, timestamp DESC)",
            "CREATE INDEX IF NOT EXISTS idx_theme_backup_verification_backup ON theme_backup_verification(backup_id)",
            "CREATE INDEX IF NOT EXISTS idx_theme_recovery_theme ON theme_recovery_log(theme_name, user_id)",
            "CREATE INDEX IF NOT EXISTS idx_theme_recovery_strategy ON theme_recovery_log(recovery_strategy, success)",
            "CREATE INDEX IF NOT EXISTS idx_theme_security_config_key ON theme_security_config(config_key)",
            "CREATE INDEX IF NOT EXISTS idx_theme_security_audit_event ON theme_security_audit(event_type, timestamp DESC)",
            "CREATE INDEX IF NOT EXISTS idx_theme_security_audit_user ON theme_security_audit(user_id, timestamp DESC)",
            "CREATE INDEX IF NOT EXISTS idx_theme_integrity_theme ON theme_integrity_checksums(theme_name, user_id)",
            "CREATE INDEX IF NOT EXISTS idx_theme_integrity_status ON theme_integrity_checksums(integrity_status, last_verified)",
            "CREATE INDEX IF NOT EXISTS idx_theme_access_log_risk ON theme_access_log(risk_score DESC)",
            "CREATE INDEX IF NOT EXISTS idx_theme_permissions_role ON theme_permissions(role_name)",
            "CREATE INDEX IF NOT EXISTS idx_theme_backups_verified ON theme_backups(verified, created_at DESC)"
        ]
        
        for index_sql in indexes:
            try:
                connection.execute(index_sql)
            except sqlite3.OperationalError as e:
                # Index might already exist, continue
                if "already exists" not in str(e):
                    raise
        
        # Insert default security configuration
        default_configs = [
            ('max_failed_attempts', '3', 'integer', 'Maximum failed authentication attempts before lockout'),
            ('lockout_duration_seconds', '300', 'integer', 'Duration of account lockout in seconds'),
            ('session_timeout_seconds', '3600', 'integer', 'Session timeout in seconds'),
            ('backup_retention_days', '30', 'integer', 'Number of days to retain backups'),
            ('max_backups_per_theme', '10', 'integer', 'Maximum number of backups per theme'),
            ('auto_backup_enabled', 'true', 'boolean', 'Enable automatic backup creation'),
            ('encryption_algorithm', 'AES-256-GCM', 'string', 'Encryption algorithm for theme data'),
            ('integrity_check_interval', '24', 'integer', 'Hours between integrity checks'),
            ('corruption_threshold', '0.1', 'string', 'Corruption threshold for auto-recovery'),
            ('audit_log_retention_days', '365', 'integer', 'Number of days to retain audit logs')
        ]
        
        for config_key, config_value, config_type, description in default_configs:
            connection.execute("""
                INSERT OR IGNORE INTO theme_security_config 
                (config_key, config_value, config_type, description)
                VALUES (?, ?, ?, ?)
            """, (config_key, config_value, config_type, description))
        
        connection.commit()
    
    def down(self, connection: sqlite3.Connection) -> None:
        """Rollback theme security enhancements."""
        
        # Drop indexes first
        indexes_to_drop = [
            "idx_theme_backups_verified",
            "idx_theme_permissions_role",
            "idx_theme_access_log_risk",
            "idx_theme_integrity_status",
            "idx_theme_integrity_theme",
            "idx_theme_security_audit_user",
            "idx_theme_security_audit_event",
            "idx_theme_security_config_key",
            "idx_theme_recovery_strategy",
            "idx_theme_recovery_theme",
            "idx_theme_backup_verification_backup",
            "idx_theme_failed_attempts_user",
            "idx_theme_sessions_active",
            "idx_theme_sessions_user"
        ]
        
        for index_name in indexes_to_drop:
            try:
                connection.execute(f"DROP INDEX IF EXISTS {index_name}")
            except sqlite3.OperationalError:
                pass  # Index might not exist
        
        # Drop new tables
        tables_to_drop = [
            "theme_integrity_checksums",
            "theme_security_audit",
            "theme_security_config",
            "theme_recovery_log",
            "theme_backup_verification",
            "theme_failed_attempts",
            "theme_user_sessions"
        ]
        
        for table_name in tables_to_drop:
            connection.execute(f"DROP TABLE IF EXISTS {table_name}")
        
        # Remove added columns (SQLite doesn't support DROP COLUMN easily)
        # We'll leave the columns as they don't break existing functionality
        
        connection.commit()
    
    def validate_preconditions(self, connection: sqlite3.Connection) -> ValidationResult:
        """Validate dependencies and prerequisites."""
        
        # Check that migration 002 was applied
        cursor = connection.execute("""
            SELECT version FROM migration_history 
            WHERE version = '002' AND status = 'applied'
        """)
        if not cursor.fetchone():
            return ValidationResult(
                success=False,
                message="Migration 002 must be applied before migration 003"
            )
        
        # Check that required tables from migration 002 exist
        required_tables = [
            'theme_access_log', 'theme_permissions', 'theme_backups', 
            'theme_corruption_log', 'secure_themes'
        ]
        
        cursor = connection.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name IN (?, ?, ?, ?, ?)
        """, required_tables)
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        if len(existing_tables) < len(required_tables):
            missing_tables = set(required_tables) - set(existing_tables)
            return ValidationResult(
                success=False,
                message=f"Required tables from migration 002 are missing: {missing_tables}"
            )
        
        return ValidationResult(success=True, message="Dependencies satisfied")
    
    def validate_postconditions(self, connection: sqlite3.Connection) -> ValidationResult:
        """Validate enhanced security tables were created."""
        
        expected_tables = [
            'theme_user_sessions', 'theme_failed_attempts', 'theme_backup_verification',
            'theme_recovery_log', 'theme_security_config', 'theme_security_audit',
            'theme_integrity_checksums'
        ]
        
        cursor = connection.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name IN (?, ?, ?, ?, ?, ?, ?)
        """, expected_tables)
        created_tables = [row[0] for row in cursor.fetchall()]
        
        if set(created_tables) != set(expected_tables):
            missing_tables = set(expected_tables) - set(created_tables)
            return ValidationResult(
                success=False,
                message=f"Expected tables {expected_tables}, missing {missing_tables}"
            )
        
        # Verify security configuration was inserted
        cursor = connection.execute("""
            SELECT COUNT(*) FROM theme_security_config
        """)
        config_count = cursor.fetchone()[0]
        
        if config_count < 5:  # Should have at least 5 default configurations
            return ValidationResult(
                success=False,
                message=f"Expected at least 5 security configurations, found {config_count}"
            )
        
        # Verify key indexes were created
        cursor = connection.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND name LIKE 'idx_theme_%'
        """)
        indexes = [row[0] for row in cursor.fetchall()]
        
        if len(indexes) < 10:  # Should have many indexes for performance
            return ValidationResult(
                success=False,
                message=f"Expected at least 10 theme indexes, found {len(indexes)}"
            )
        
        return ValidationResult(
            success=True, 
            message="Theme security enhancements added successfully"
        )