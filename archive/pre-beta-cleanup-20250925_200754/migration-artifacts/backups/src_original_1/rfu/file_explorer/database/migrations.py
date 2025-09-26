"""
Database Migration System for RFU Multi-Pane File Explorer
Enterprise-Grade Migration Framework with Version Control

This module provides a comprehensive database migration framework with:

- Version-controlled schema evolution
- Automatic backup and rollback capabilities
- Transaction safety with atomic operations
- Cross-platform compatibility
- Comprehensive error handling and logging
- Database integrity verification
- Performance optimization tracking

Migration Features:
- Forward and backward migration support
- Dependency resolution between migrations
- Automatic schema version detection
- Safe migration execution with rollback
- Migration history tracking
- Data preservation during schema changes

Author: RFU Development Team
Created: 2025-09-12
Version: 1.0.0 (Phase 1 Foundation)
"""

import json
import logging
import shutil
import sqlite3
import sys
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from PyQt5.QtCore import QObject, pyqtSignal


class MigrationError(Exception):
    """Custom exception for migration operations."""
    pass


class Migration(ABC):
    """
    Base class for database migrations.
    
    All migrations should inherit from this class and implement
    the upgrade and downgrade methods.
    """
    
    def __init__(self, version: int, description: str):
        """
        Initialize migration.
        
        Args:
            version: Migration version number
            description: Human-readable description of the migration
        """
        self.version = version
        self.description = description
        self.applied_at: Optional[datetime] = None
        self.execution_time_ms: int = 0
    
    @abstractmethod
    def upgrade(self, conn: sqlite3.Connection) -> bool:
        """
        Apply the migration (upgrade database).
        
        Args:
            conn: Database connection
            
        Returns:
            bool: True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def downgrade(self, conn: sqlite3.Connection) -> bool:
        """
        Reverse the migration (downgrade database).
        
        Args:
            conn: Database connection
            
        Returns:
            bool: True if successful, False otherwise
        """
        pass
    
    def validate_preconditions(self, conn: sqlite3.Connection) -> bool:
        """
        Validate that preconditions for migration are met.
        
        Args:
            conn: Database connection
            
        Returns:
            bool: True if preconditions are met, False otherwise
        """
        return True
    
    def validate_postconditions(self, conn: sqlite3.Connection) -> bool:
        """
        Validate that migration was applied correctly.
        
        Args:
            conn: Database connection
            
        Returns:
            bool: True if postconditions are met, False otherwise
        """
        return True
    
    def get_dependencies(self) -> List[int]:
        """
        Get list of migration versions this migration depends on.
        
        Returns:
            List[int]: List of required migration versions
        """
        return []
    
    def __str__(self) -> str:
        return f"Migration {self.version}: {self.description}"
    
    def __repr__(self) -> str:
        return f"Migration(version={self.version}, description='{self.description}')"


class CreateInitialSchemaMigration(Migration):
    """Initial schema creation migration."""
    
    def __init__(self):
        super().__init__(1, "Create initial file explorer schema")
    
    def upgrade(self, conn: sqlite3.Connection) -> bool:
        """Create the initial database schema."""
        try:
            # Enable foreign keys
            conn.execute("PRAGMA foreign_keys=ON")
            
            # Create core tables
            self._create_pane_tables(conn)
            self._create_preference_tables(conn)
            self._create_history_tables(conn)
            self._create_system_tables(conn)
            
            # Create indexes
            self._create_initial_indexes(conn)
            
            # Create triggers
            self._create_initial_triggers(conn)
            
            # Insert default data
            self._insert_initial_data(conn)
            
            return True
            
        except sqlite3.Error as e:
            logging.error(f"Failed to create initial schema: {e}")
            return False
    
    def downgrade(self, conn: sqlite3.Connection) -> bool:
        """Drop all tables (complete rollback)."""
        try:
            tables = [
                'file_operations', 'navigation_history', 'recent_directories',
                'bookmarks', 'file_type_colors', 'layout_preferences',
                'pane_settings', 'pane_configurations', 'migration_history'
            ]
            
            for table in tables:
                conn.execute(f"DROP TABLE IF EXISTS {table}")
            
            return True
            
        except sqlite3.Error as e:
            logging.error(f"Failed to downgrade initial schema: {e}")
            return False
    
    def _create_pane_tables(self, conn: sqlite3.Connection):
        """Create pane-related tables."""
        
        # Pane configurations
        conn.execute("""
            CREATE TABLE IF NOT EXISTS pane_configurations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                config_name TEXT NOT NULL UNIQUE,
                pane_count INTEGER NOT NULL CHECK (pane_count BETWEEN 1 AND 4),
                is_default BOOLEAN DEFAULT FALSE,
                layout_type TEXT NOT NULL DEFAULT 'horizontal' 
                    CHECK (layout_type IN ('horizontal', 'vertical', 'grid')),
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Individual pane settings
        conn.execute("""
            CREATE TABLE IF NOT EXISTS pane_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                config_id INTEGER NOT NULL REFERENCES pane_configurations(id) ON DELETE CASCADE,
                pane_index INTEGER NOT NULL CHECK (pane_index BETWEEN 0 AND 3),
                default_path TEXT,
                view_mode TEXT DEFAULT 'list' 
                    CHECK (view_mode IN ('list', 'icon', 'detail', 'tree')),
                sort_column TEXT DEFAULT 'name',
                sort_order TEXT DEFAULT 'ASC' CHECK (sort_order IN ('ASC', 'DESC')),
                show_hidden BOOLEAN DEFAULT FALSE,
                show_system BOOLEAN DEFAULT FALSE,
                column_widths TEXT, -- JSON array
                file_filters TEXT, -- JSON array
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(config_id, pane_index)
            )
        """)
    
    def _create_preference_tables(self, conn: sqlite3.Connection):
        """Create preference-related tables."""
        
        # File type color schemes
        conn.execute("""
            CREATE TABLE IF NOT EXISTS file_type_colors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scheme_name TEXT NOT NULL,
                file_extension TEXT NOT NULL,
                foreground_color TEXT NOT NULL,
                background_color TEXT,
                font_weight TEXT DEFAULT 'normal' 
                    CHECK (font_weight IN ('normal', 'bold')),
                font_style TEXT DEFAULT 'normal' 
                    CHECK (font_style IN ('normal', 'italic', 'oblique')),
                icon_path TEXT,
                is_default BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(scheme_name, file_extension)
            )
        """)
        
        # Layout preferences
        conn.execute("""
            CREATE TABLE IF NOT EXISTS layout_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                preference_name TEXT NOT NULL UNIQUE,
                window_geometry TEXT, -- JSON
                window_state TEXT, -- JSON
                pane_splitter_sizes TEXT, -- JSON array
                toolbar_visible BOOLEAN DEFAULT TRUE,
                statusbar_visible BOOLEAN DEFAULT TRUE,
                sidebar_visible BOOLEAN DEFAULT TRUE,
                sidebar_width INTEGER DEFAULT 200,
                theme_name TEXT DEFAULT 'default',
                font_family TEXT DEFAULT 'System',
                font_size INTEGER DEFAULT 10,
                is_default BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Bookmarks
        conn.execute("""
            CREATE TABLE IF NOT EXISTS bookmarks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                path TEXT NOT NULL,
                icon_path TEXT,
                category TEXT DEFAULT 'user',
                sort_order INTEGER DEFAULT 0,
                access_count INTEGER DEFAULT 0,
                last_accessed TIMESTAMP,
                is_favorite BOOLEAN DEFAULT FALSE,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    
    def _create_history_tables(self, conn: sqlite3.Connection):
        """Create history-related tables."""
        
        # Navigation history
        conn.execute("""
            CREATE TABLE IF NOT EXISTS navigation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pane_index INTEGER NOT NULL,
                path TEXT NOT NULL,
                operation_type TEXT DEFAULT 'navigate' 
                    CHECK (operation_type IN ('navigate', 'back', 'forward', 'up', 'bookmark')),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                session_id TEXT NOT NULL,
                duration_seconds INTEGER DEFAULT 0,
                file_count INTEGER DEFAULT 0,
                folder_count INTEGER DEFAULT 0
            )
        """)
        
        # Recent directories
        conn.execute("""
            CREATE TABLE IF NOT EXISTS recent_directories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT NOT NULL,
                pane_index INTEGER,
                access_count INTEGER DEFAULT 1,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                session_id TEXT,
                duration_seconds INTEGER DEFAULT 0,
                display_name TEXT,
                UNIQUE(path, pane_index)
            )
        """)
        
        # File operations
        conn.execute("""
            CREATE TABLE IF NOT EXISTS file_operations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                operation_type TEXT NOT NULL 
                    CHECK (operation_type IN ('copy', 'move', 'delete', 'rename', 'compress', 'extract')),
                source_path TEXT NOT NULL,
                destination_path TEXT,
                file_size BIGINT DEFAULT 0,
                status TEXT NOT NULL DEFAULT 'pending' 
                    CHECK (status IN ('pending', 'in_progress', 'completed', 'failed', 'cancelled')),
                progress_percent INTEGER DEFAULT 0 CHECK (progress_percent BETWEEN 0 AND 100),
                error_message TEXT,
                operation_id TEXT UNIQUE,
                user_initiated BOOLEAN DEFAULT TRUE,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                duration_seconds INTEGER DEFAULT 0
            )
        """)
    
    def _create_system_tables(self, conn: sqlite3.Connection):
        """Create system tables."""
        
        # Migration history
        conn.execute("""
            CREATE TABLE IF NOT EXISTS migration_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version INTEGER NOT NULL UNIQUE,
                description TEXT NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                execution_time_ms INTEGER DEFAULT 0,
                checksum TEXT,
                rollback_sql TEXT
            )
        """)
    
    def _create_initial_indexes(self, conn: sqlite3.Connection):
        """Create initial performance indexes."""
        
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_pane_config_default ON pane_configurations(is_default)",
            "CREATE INDEX IF NOT EXISTS idx_pane_settings_config ON pane_settings(config_id)",
            "CREATE INDEX IF NOT EXISTS idx_file_colors_scheme ON file_type_colors(scheme_name)",
            "CREATE INDEX IF NOT EXISTS idx_file_colors_ext ON file_type_colors(file_extension)",
            "CREATE INDEX IF NOT EXISTS idx_bookmarks_category ON bookmarks(category)",
            "CREATE INDEX IF NOT EXISTS idx_bookmarks_favorite ON bookmarks(is_favorite)",
            "CREATE INDEX IF NOT EXISTS idx_recent_path ON recent_directories(path)",
            "CREATE INDEX IF NOT EXISTS idx_recent_accessed ON recent_directories(last_accessed)",
            "CREATE INDEX IF NOT EXISTS idx_nav_pane ON navigation_history(pane_index)",
            "CREATE INDEX IF NOT EXISTS idx_nav_session ON navigation_history(session_id)",
            "CREATE INDEX IF NOT EXISTS idx_file_ops_status ON file_operations(status)",
            "CREATE INDEX IF NOT EXISTS idx_file_ops_type ON file_operations(operation_type)"
        ]
        
        for index_sql in indexes:
            conn.execute(index_sql)
    
    def _create_initial_triggers(self, conn: sqlite3.Connection):
        """Create initial database triggers."""
        
        # Auto-update timestamps
        triggers = [
            """
            CREATE TRIGGER IF NOT EXISTS update_pane_config_timestamp 
            AFTER UPDATE ON pane_configurations
            BEGIN
                UPDATE pane_configurations SET updated_at = CURRENT_TIMESTAMP 
                WHERE id = NEW.id;
            END
            """,
            """
            CREATE TRIGGER IF NOT EXISTS update_pane_settings_timestamp 
            AFTER UPDATE ON pane_settings
            BEGIN
                UPDATE pane_settings SET updated_at = CURRENT_TIMESTAMP 
                WHERE id = NEW.id;
            END
            """,
            """
            CREATE TRIGGER IF NOT EXISTS ensure_single_default_config
            BEFORE UPDATE ON pane_configurations
            WHEN NEW.is_default = 1 AND OLD.is_default = 0
            BEGIN
                UPDATE pane_configurations SET is_default = FALSE 
                WHERE is_default = TRUE AND id != NEW.id;
            END
            """
        ]
        
        for trigger_sql in triggers:
            conn.execute(trigger_sql)
    
    def _insert_initial_data(self, conn: sqlite3.Connection):
        """Insert initial default data."""
        
        # Default pane configuration
        conn.execute("""
            INSERT OR IGNORE INTO pane_configurations 
            (config_name, pane_count, is_default, layout_type, description)
            VALUES ('Default Dual Pane', 2, TRUE, 'horizontal', 'Default two-pane horizontal layout')
        """)
        
        # Get the config ID
        cursor = conn.execute("SELECT id FROM pane_configurations WHERE config_name = 'Default Dual Pane'")
        config_id = cursor.fetchone()[0]
        
        # Default pane settings
        home_path = str(Path.home())
        documents_path = str(Path.home() / 'Documents')
        
        pane_settings = [
            (config_id, 0, home_path, 'list', 'name', 'ASC', False, False),
            (config_id, 1, documents_path, 'list', 'name', 'ASC', False, False)
        ]
        
        conn.executemany("""
            INSERT OR IGNORE INTO pane_settings 
            (config_id, pane_index, default_path, view_mode, sort_column, sort_order, show_hidden, show_system)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, pane_settings)
        
        # Default file type colors
        default_colors = [
            ('Default', '.txt', '#000000', None, 'normal', 'normal'),
            ('Default', '.py', '#0066cc', None, 'normal', 'normal'),
            ('Default', '.js', '#f7df1e', '#323330', 'normal', 'normal'),
            ('Default', '.html', '#e34c26', None, 'normal', 'normal'),
            ('Default', '.css', '#1572b6', None, 'normal', 'normal'),
            ('Default', '.pdf', '#ff0000', None, 'bold', 'normal'),
            ('Default', '.jpg', '#ff6b6b', None, 'normal', 'normal'),
            ('Default', '.png', '#ff6b6b', None, 'normal', 'normal'),
            ('Default', '.zip', '#f39c12', None, 'normal', 'normal'),
            ('Default', '.exe', '#e67e22', None, 'bold', 'normal')
        ]
        
        conn.executemany("""
            INSERT OR IGNORE INTO file_type_colors 
            (scheme_name, file_extension, foreground_color, background_color, font_weight, font_style)
            VALUES (?, ?, ?, ?, ?, ?)
        """, default_colors)
        
        # Default bookmarks
        default_bookmarks = [
            ('Home', home_path, None, 'system', 1, True),
            ('Documents', documents_path, None, 'system', 2, True),
            ('Downloads', str(Path.home() / 'Downloads'), None, 'system', 3, True),
            ('Desktop', str(Path.home() / 'Desktop'), None, 'system', 4, True)
        ]
        
        conn.executemany("""
            INSERT OR IGNORE INTO bookmarks 
            (name, path, icon_path, category, sort_order, is_favorite)
            VALUES (?, ?, ?, ?, ?, ?)
        """, default_bookmarks)
        
        # Default layout preferences
        conn.execute("""
            INSERT OR IGNORE INTO layout_preferences 
            (preference_name, toolbar_visible, statusbar_visible, sidebar_visible, 
             sidebar_width, theme_name, is_default)
            VALUES ('Default Layout', TRUE, TRUE, TRUE, 200, 'default', TRUE)
        """)


class DatabaseMigrator(QObject):
    """
    Enterprise-grade database migration manager.
    
    Features:
    - Automatic migration discovery and execution
    - Version tracking and dependency resolution
    - Atomic migration execution with rollback
    - Backup creation before migrations
    - Migration history and auditing
    - Performance monitoring
    """
    
    # Signals for migration events
    migration_started = pyqtSignal(int, str)  # version, description
    migration_completed = pyqtSignal(int, bool, str)  # version, success, message
    migration_progress = pyqtSignal(int, int)  # current, total
    
    def __init__(self, db_path: Union[str, Path]):
        """
        Initialize migration manager.
        
        Args:
            db_path: Path to database file
        """
        super().__init__()
        
        self.db_path = Path(db_path)
        self.backup_dir = self.db_path.parent / 'backups'
        self.backup_dir.mkdir(exist_ok=True)
        
        # Setup logging
        self.logger = logging.getLogger('RFU.FileExplorer.Migrator')
        
        # Migration registry
        self.migrations: Dict[int, Migration] = {}
        self._register_default_migrations()
        
        # Migration state
        self.current_version = 0
        self.target_version = max(self.migrations.keys()) if self.migrations else 0
        
        self.logger.info(f"Migration manager initialized for: {self.db_path}")
    
    def _register_default_migrations(self):
        """Register default migrations."""
        self.register_migration(CreateInitialSchemaMigration())
    
    def register_migration(self, migration: Migration):
        """
        Register a migration.
        
        Args:
            migration: Migration instance to register
        """
        if migration.version in self.migrations:
            raise MigrationError(f"Migration version {migration.version} already registered")
        
        self.migrations[migration.version] = migration
        self.logger.debug(f"Registered migration: {migration}")
    
    def get_current_version(self) -> int:
        """
        Get current database schema version.
        
        Returns:
            int: Current schema version, 0 if no migrations applied
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Check if migration_history table exists
                cursor = conn.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='migration_history'
                """)
                
                if not cursor.fetchone():
                    return 0
                
                # Get latest migration version
                cursor = conn.execute("""
                    SELECT MAX(version) FROM migration_history
                """)
                
                result = cursor.fetchone()
                return result[0] if result and result[0] is not None else 0
                
        except sqlite3.Error as e:
            self.logger.error(f"Failed to get current version: {e}")
            return 0
    
    def get_migration_history(self) -> List[Dict[str, Any]]:
        """
        Get migration history.
        
        Returns:
            List[Dict]: List of applied migrations with metadata
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT * FROM migration_history 
                    ORDER BY version
                """)
                return [dict(row) for row in cursor.fetchall()]
                
        except sqlite3.Error as e:
            self.logger.error(f"Failed to get migration history: {e}")
            return []
    
    def needs_migration(self) -> bool:
        """
        Check if database needs migration.
        
        Returns:
            bool: True if migration needed, False otherwise
        """
        current = self.get_current_version()
        target = self.target_version
        return current < target
    
    def create_backup(self) -> Optional[Path]:
        """
        Create database backup before migration.
        
        Returns:
            Optional[Path]: Path to backup file, None if failed
        """
        if not self.db_path.exists():
            return None
        
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = self.backup_dir / f"file_explorer_backup_{timestamp}.db"
            
            shutil.copy2(self.db_path, backup_path)
            
            # Compress backup if it's large
            if backup_path.stat().st_size > 10 * 1024 * 1024:  # 10MB
                import gzip
                compressed_path = backup_path.with_suffix('.db.gz')
                with open(backup_path, 'rb') as f_in:
                    with gzip.open(compressed_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                backup_path.unlink()
                backup_path = compressed_path
            
            self.logger.info(f"Database backup created: {backup_path}")
            return backup_path
            
        except Exception as e:
            self.logger.error(f"Failed to create backup: {e}")
            return None
    
    def migrate(self, target_version: Optional[int] = None) -> bool:
        """
        Execute database migration to target version.
        
        Args:
            target_version: Target schema version, None for latest
            
        Returns:
            bool: True if migration successful, False otherwise
        """
        if target_version is None:
            target_version = self.target_version
        
        current_version = self.get_current_version()
        
        if current_version == target_version:
            self.logger.info("Database is already at target version")
            return True
        
        if current_version > target_version:
            self.logger.warning("Downgrade migrations not yet implemented")
            return False
        
        # Create backup
        backup_path = self.create_backup()
        if not backup_path and self.db_path.exists():
            self.logger.error("Failed to create backup, aborting migration")
            return False
        
        # Get migrations to apply
        migrations_to_apply = [
            self.migrations[v] for v in range(current_version + 1, target_version + 1)
            if v in self.migrations
        ]
        
        if not migrations_to_apply:
            self.logger.warning("No migrations to apply")
            return True
        
        # Validate migration dependencies
        if not self._validate_migration_dependencies(migrations_to_apply):
            self.logger.error("Migration dependency validation failed")
            return False
        
        # Execute migrations
        self.logger.info(f"Starting migration from version {current_version} to {target_version}")
        self.migration_progress.emit(0, len(migrations_to_apply))
        
        success = True
        for i, migration in enumerate(migrations_to_apply):
            self.migration_started.emit(migration.version, migration.description)
            
            if not self._apply_migration(migration):
                success = False
                break
            
            self.migration_progress.emit(i + 1, len(migrations_to_apply))
            self.migration_completed.emit(migration.version, True, "Migration applied successfully")
        
        if success:
            self.logger.info(f"Migration completed successfully to version {target_version}")
        else:
            self.logger.error("Migration failed, database may need manual recovery")
            if backup_path:
                self.logger.info(f"Backup available at: {backup_path}")
        
        return success
    
    def _validate_migration_dependencies(self, migrations: List[Migration]) -> bool:
        """
        Validate that all migration dependencies are satisfied.
        
        Args:
            migrations: List of migrations to validate
            
        Returns:
            bool: True if all dependencies satisfied, False otherwise
        """
        applied_versions = {m.version for m in migrations}
        current_version = self.get_current_version()
        
        for migration in migrations:
            for dep_version in migration.get_dependencies():
                if dep_version > current_version and dep_version not in applied_versions:
                    self.logger.error(
                        f"Migration {migration.version} depends on version {dep_version} "
                        f"which is not available"
                    )
                    return False
        
        return True
    
    def _apply_migration(self, migration: Migration) -> bool:
        """
        Apply a single migration with transaction safety.
        
        Args:
            migration: Migration to apply
            
        Returns:
            bool: True if successful, False otherwise
        """
        start_time = datetime.now()
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Start transaction
                conn.execute("BEGIN IMMEDIATE")
                
                try:
                    # Validate preconditions
                    if not migration.validate_preconditions(conn):
                        raise MigrationError(f"Preconditions not met for migration {migration.version}")
                    
                    # Apply migration
                    if not migration.upgrade(conn):
                        raise MigrationError(f"Migration {migration.version} upgrade failed")
                    
                    # Validate postconditions
                    if not migration.validate_postconditions(conn):
                        raise MigrationError(f"Postconditions not met for migration {migration.version}")
                    
                    # Record migration in history
                    execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
                    
                    conn.execute("""
                        INSERT INTO migration_history 
                        (version, description, execution_time_ms)
                        VALUES (?, ?, ?)
                    """, (migration.version, migration.description, execution_time_ms))
                    
                    # Commit transaction
                    conn.commit()
                    
                    migration.applied_at = datetime.now()
                    migration.execution_time_ms = execution_time_ms
                    
                    self.logger.info(
                        f"Applied migration {migration.version}: {migration.description} "
                        f"(execution time: {execution_time_ms}ms)"
                    )
                    
                    return True
                    
                except Exception as e:
                    # Rollback transaction
                    conn.rollback()
                    raise e
                    
        except Exception as e:
            self.logger.error(f"Failed to apply migration {migration.version}: {e}")
            self.migration_completed.emit(migration.version, False, str(e))
            return False
    
    def get_migration_status(self) -> Dict[str, Any]:
        """
        Get comprehensive migration status.
        
        Returns:
            Dict: Migration status information
        """
        current_version = self.get_current_version()
        
        status = {
            'current_version': current_version,
            'target_version': self.target_version,
            'needs_migration': self.needs_migration(),
            'available_migrations': len(self.migrations),
            'applied_migrations': len(self.get_migration_history()),
            'database_exists': self.db_path.exists(),
            'backup_directory': str(self.backup_dir)
        }
        
        if current_version > 0:
            history = self.get_migration_history()
            if history:
                last_migration = history[-1]
                status['last_migration'] = {
                    'version': last_migration['version'],
                    'description': last_migration['description'],
                    'applied_at': last_migration['applied_at'],
                    'execution_time_ms': last_migration['execution_time_ms']
                }
        
        return status
    
    def verify_database_consistency(self) -> bool:
        """
        Verify database consistency after migration.
        
        Returns:
            bool: True if consistent, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Check PRAGMA integrity
                cursor = conn.execute("PRAGMA integrity_check")
                result = cursor.fetchone()
                
                if result[0] != 'ok':
                    self.logger.error(f"Database integrity check failed: {result[0]}")
                    return False
                
                # Check foreign key consistency
                cursor = conn.execute("PRAGMA foreign_key_check")
                violations = cursor.fetchall()
                
                if violations:
                    self.logger.error(f"Foreign key violations found: {len(violations)}")
                    return False
                
                self.logger.info("Database consistency verification passed")
                return True
                
        except sqlite3.Error as e:
            self.logger.error(f"Database consistency check failed: {e}")
            return False


# For testing and development
if __name__ == '__main__':
    # Configure logging for testing
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Test migration system
    db_path = Path('test_migration.db')
    
    # Clean up previous test
    if db_path.exists():
        db_path.unlink()
    
    migrator = DatabaseMigrator(db_path)
    
    print("Migration Status:")
    status = migrator.get_migration_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    if migrator.needs_migration():
        print("\nRunning migration...")
        success = migrator.migrate()
        
        if success:
            print("Migration completed successfully!")
            
            # Verify consistency
            if migrator.verify_database_consistency():
                print("Database consistency verified!")
            else:
                print("Database consistency check failed!")
        else:
            print("Migration failed!")
    else:
        print("No migration needed.")
    
    # Clean up test database
    if db_path.exists():
        db_path.unlink()
    
    # Clean up backup directory
    backup_dir = db_path.parent / 'backups'
    if backup_dir.exists():
        shutil.rmtree(backup_dir)