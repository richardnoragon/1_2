"""
Database Manager for Richard's File Utilities

This module provides centralized SQLite database management with connection pooling,
schema management, migrations, and backup functionality.
"""

import sqlite3
import threading
import logging
import json
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from datetime import datetime, timedelta
from contextlib import contextmanager
import uuid


# Custom Database Exception Classes
class DatabaseError(Exception):
    """Base exception for database operations."""
    pass


class DatabaseQueryError(DatabaseError):
    """Exception for database query failures."""
    pass


class DatabaseUpdateError(DatabaseError):
    """Exception for database update/insert/delete failures."""
    pass


class DatabaseConnectionError(DatabaseError):
    """Exception for database connection failures."""
    pass


class DatabaseManager:
    """Centralized SQLite database manager with singleton pattern."""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Ensure singleton pattern."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(DatabaseManager, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the database manager."""
        if not self._initialized:
            self._setup_database()
            self._initialized = True
    
    def _setup_database(self):
        """Setup database management system."""
        # Database configuration
        self.db_dir = Path('data')
        self.db_dir.mkdir(exist_ok=True)
        self.db_file = self.db_dir / 'rfu_database.db'
        self.backup_dir = self.db_dir / 'backups'
        self.backup_dir.mkdir(exist_ok=True)
        
        # Connection pool settings
        self.max_connections = 10
        self.connection_pool: List[sqlite3.Connection] = []
        self.pool_lock = threading.Lock()
        
        # Setup logging
        self.logger = logging.getLogger('RFU.DatabaseManager')
        
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
            
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise
    
    def _create_schema(self, conn: sqlite3.Connection):
        """Create database schema."""
        
        # Application Settings Table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS app_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                section TEXT NOT NULL CHECK(length(section) > 0),
                key TEXT NOT NULL CHECK(length(key) > 0),
                value TEXT NOT NULL,
                value_type TEXT NOT NULL DEFAULT 'string'
                    CHECK(value_type IN ('string', 'int', 'float', 
                                        'bool', 'json')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(section, key)
            )
        """)
        
        # File History Table
        conn.execute("""
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
        """)
        
        # Directory History Table
        conn.execute("""
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
        """)
        
        # Application Logs Table
        conn.execute("""
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
        """)
        
        # Tool Usage Statistics Table
        conn.execute("""
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
        """)
        
        # User Preferences Table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT DEFAULT 'default',
                preference_category TEXT NOT NULL,
                preference_key TEXT NOT NULL,
                preference_value TEXT NOT NULL,
                value_type TEXT NOT NULL DEFAULT 'string',
                is_encrypted BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, preference_category, preference_key)
            )
        """)
        
        # Database Metadata Table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS db_metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    
    def _create_indexes(self, conn: sqlite3.Connection):
        """Create database indexes for performance."""
        
        indexes = [
            # File history indexes
            "CREATE INDEX IF NOT EXISTS idx_file_history_path ON file_history(file_path)",
            "CREATE INDEX IF NOT EXISTS idx_file_history_accessed ON file_history(last_accessed DESC)",
            "CREATE INDEX IF NOT EXISTS idx_file_history_tool ON file_history(tool_name)",
            
            # Directory history indexes
            "CREATE INDEX IF NOT EXISTS idx_directory_history_path ON directory_history(directory_path)",
            "CREATE INDEX IF NOT EXISTS idx_directory_history_accessed ON directory_history(last_accessed DESC)",
            "CREATE INDEX IF NOT EXISTS idx_directory_history_favorite ON directory_history(is_favorite)",
            
            # Application logs indexes
            "CREATE INDEX IF NOT EXISTS idx_app_logs_timestamp ON app_logs(timestamp DESC)",
            "CREATE INDEX IF NOT EXISTS idx_app_logs_level ON app_logs(level)",
            "CREATE INDEX IF NOT EXISTS idx_app_logs_logger ON app_logs(logger_name)",
            "CREATE INDEX IF NOT EXISTS idx_app_logs_session ON app_logs(session_id)",
            
            # Tool usage indexes
            "CREATE INDEX IF NOT EXISTS idx_tool_usage_name ON tool_usage(tool_name)",
            "CREATE INDEX IF NOT EXISTS idx_tool_usage_last_used ON tool_usage(last_used DESC)",
            
            # Settings indexes
            "CREATE INDEX IF NOT EXISTS idx_app_settings_section ON app_settings(section)",
            "CREATE INDEX IF NOT EXISTS idx_app_settings_key ON app_settings(section, key)",
            
            # User preferences indexes
            "CREATE INDEX IF NOT EXISTS idx_user_preferences_category ON user_preferences(preference_category)",
            "CREATE INDEX IF NOT EXISTS idx_user_preferences_user ON user_preferences(user_id)",
        ]
        
        for index_sql in indexes:
            conn.execute(index_sql)
    
    def _create_triggers(self, conn: sqlite3.Connection):
        """Create database triggers for automation."""
        
        # Update timestamp trigger for app_settings
        conn.execute("""
            CREATE TRIGGER IF NOT EXISTS update_app_settings_timestamp
            AFTER UPDATE ON app_settings
            BEGIN
                UPDATE app_settings 
                SET updated_at = CURRENT_TIMESTAMP 
                WHERE id = NEW.id;
            END
        """)
        
        # Update timestamp trigger for user_preferences
        conn.execute("""
            CREATE TRIGGER IF NOT EXISTS update_user_preferences_timestamp
            AFTER UPDATE ON user_preferences
            BEGIN
                UPDATE user_preferences 
                SET updated_at = CURRENT_TIMESTAMP 
                WHERE id = NEW.id;
            END
        """)
        
        # Increment access count for file_history
        conn.execute("""
            CREATE TRIGGER IF NOT EXISTS increment_file_access
            AFTER UPDATE ON file_history
            WHEN NEW.last_accessed > OLD.last_accessed
            BEGIN
                UPDATE file_history 
                SET access_count = access_count + 1
                WHERE id = NEW.id;
            END
        """)
        
        # Increment access count for directory_history
        conn.execute("""
            CREATE TRIGGER IF NOT EXISTS increment_directory_access
            AFTER UPDATE ON directory_history
            WHEN NEW.last_accessed > OLD.last_accessed
            BEGIN
                UPDATE directory_history 
                SET access_count = access_count + 1
                WHERE id = NEW.id;
            END
        """)
    
    def _insert_initial_data(self, conn: sqlite3.Connection):
        """Insert initial metadata and configuration."""
        
        # Database version and metadata
        metadata = [
            ('schema_version', '1.0.0'),
            ('created_at', datetime.now().isoformat()),
            ('session_id', self.session_id),
            ('application_version', '1.0.0'),
        ]
        
        conn.executemany(
            "INSERT OR REPLACE INTO db_metadata (key, value) VALUES (?, ?)",
            metadata
        )
        
        # Default application settings
        default_settings = [
            ('database', 'auto_vacuum', 'true', 'boolean'),
            ('database', 'backup_retention_days', '30', 'integer'),
            ('database', 'log_retention_days', '90', 'integer'),
            ('database', 'max_file_history_entries', '1000', 'integer'),
            ('database', 'enable_analytics', 'true', 'boolean'),
        ]
        
        conn.executemany(
            """INSERT OR IGNORE INTO app_settings 
               (section, key, value, value_type) VALUES (?, ?, ?, ?)""",
            default_settings
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
                        check_same_thread=False
                    )
                    conn.row_factory = sqlite3.Row
                    conn.execute("PRAGMA foreign_keys=ON")
            
            yield conn
            
        except Exception as e:
            if conn:
                conn.rollback()
            self.logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                with self.pool_lock:
                    if len(self.connection_pool) < self.max_connections:
                        self.connection_pool.append(conn)
                    else:
                        conn.close()
    
    def execute_query(self, query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results with proper error handling."""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(query, params)
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except sqlite3.DatabaseError as e:
            self.logger.error(f"Database error in query execution: {e}")
            self.logger.error(f"Query: {query}")
            self.logger.error(f"Params: {params}")
            raise DatabaseQueryError(f"Database query failed: {e}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error in query execution: {e}")
            self.logger.error(f"Query: {query}")
            self.logger.error(f"Params: {params}")
            raise DatabaseError(f"Query execution failed: {e}") from e
    
    def execute_update(self, query: str, params: Tuple = ()) -> int:
        """Execute an UPDATE/INSERT/DELETE query and return affected rows with proper error handling."""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(query, params)
                conn.commit()
                return cursor.rowcount
        except sqlite3.DatabaseError as e:
            self.logger.error(f"Database error in update execution: {e}")
            self.logger.error(f"Query: {query}")
            self.logger.error(f"Params: {params}")
            raise DatabaseUpdateError(f"Database update failed: {e}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error in update execution: {e}")
            self.logger.error(f"Query: {query}")
            self.logger.error(f"Params: {params}")
            raise DatabaseError(f"Update execution failed: {e}") from e
    
    def execute_many(self, query: str, params_list: List[Tuple]) -> int:
        """Execute multiple queries with different parameters."""
        try:
            with self.get_connection() as conn:
                cursor = conn.executemany(query, params_list)
                conn.commit()
                return cursor.rowcount
        except Exception as e:
            self.logger.error(f"Batch execution failed: {e}")
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
                except OSError as e:
                    self.logger.error(f"Cannot create backup directory: {e}")
                    return False
            
            if backup_name is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"rfu_database_backup_{timestamp}.db"
            
            # Validation: Sanitize backup name
            backup_name = backup_name.replace('/', '_').replace('\\', '_')
            backup_name = backup_name.strip()
            if not backup_name or backup_name == '.':
                self.logger.error("Invalid backup name")
                return False
            
            backup_path = self.backup_dir / backup_name
            shutil.copy2(self.db_file, backup_path)
            
            self.logger.info(f"Database backed up to: {backup_path}")
            return True
        except Exception as e:
            self.logger.error(f"Database backup failed: {e}")
            return False
    
    def restore_database(self, backup_path: Union[str, Path]) -> bool:
        """Restore database from a backup with safety measures."""
        try:
            backup_file = Path(backup_path)
            
            # Validation checks
            if not backup_file.exists():
                self.logger.error(f"Backup file not found: {backup_file}")
                return False
                
            if not backup_file.is_file():
                self.logger.error(f"Backup path is not a file: {backup_file}")
                return False
                
            # Safety: Create a backup of current database before restore
            if self.db_file.exists():
                safety_backup_name = f"safety_backup_before_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                self.logger.info(f"Creating safety backup: {safety_backup_name}")
                if not self.backup_database(safety_backup_name):
                    self.logger.warning("Could not create safety backup, proceeding anyway")
            
            # Close all connections
            self.close_all_connections()
            
            # Restore the database
            shutil.copy2(backup_file, self.db_file)
            
            # Validate restored database
            try:
                # Quick validation - try to open and query the restored database
                test_conn = sqlite3.connect(self.db_file)
                test_conn.execute("SELECT 1").fetchone()
                test_conn.close()
            except sqlite3.Error as e:
                self.logger.error(f"Restored database validation failed: {e}")
                return False
            
            # Reinitialize
            self._initialize_database()
            
            self.logger.info(f"Database restored from: {backup_file}")
            return True
        except Exception as e:
            self.logger.error(f"Database restore failed: {e}")
            return False
    
    def cleanup_old_data(self):
        """Clean up old data based on retention policies."""
        try:
            with self.get_connection() as conn:
                # Get retention settings
                log_retention = self.get_setting('database', 'log_retention_days', 90)
                backup_retention = self.get_setting('database', 'backup_retention_days', 30)
                
                # Clean old logs
                cutoff_date = datetime.now() - timedelta(days=log_retention)
                conn.execute(
                    "DELETE FROM app_logs WHERE timestamp < ?",
                    (cutoff_date.isoformat(),)
                )
                
                # Clean old backups
                backup_cutoff = datetime.now() - timedelta(days=backup_retention)
                for backup_file in self.backup_dir.glob("rfu_database_backup_*.db"):
                    if backup_file.stat().st_mtime < backup_cutoff.timestamp():
                        backup_file.unlink()
                        self.logger.info(f"Removed old backup: {backup_file}")
                
                conn.commit()
                self.logger.info("Database cleanup completed")
                
        except Exception as e:
            self.logger.error(f"Database cleanup failed: {e}")
    
    def vacuum_database(self) -> bool:
        """Perform database vacuum operation."""
        try:
            with self.get_connection() as conn:
                conn.execute("VACUUM")
                self.logger.info("Database vacuum completed")
                return True
        except Exception as e:
            self.logger.error(f"Database vacuum failed: {e}")
            return False
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get database information and statistics."""
        try:
            with self.get_connection() as conn:
                # Get database size
                db_size = self.db_file.stat().st_size if self.db_file.exists() else 0
                
                # Get table counts
                tables = [
                    'app_settings', 'file_history', 'directory_history',
                    'app_logs', 'tool_usage', 'user_preferences'
                ]
                
                table_counts = {}
                for table in tables:
                    try:
                        cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cursor.fetchone()[0]
                        table_counts[table] = count
                        cursor.close()  # Properly close cursor
                    except sqlite3.Error as e:
                        self.logger.warning(f"Could not count table {table}: {e}")
                        table_counts[table] = 0
                
                # Get metadata with proper resource management
                try:
                    cursor = conn.execute("SELECT * FROM db_metadata")
                    metadata = {row['key']: row['value'] for row in cursor.fetchall()}
                    cursor.close()  # Properly close cursor
                except sqlite3.Error as e:
                    self.logger.warning(f"Could not fetch metadata: {e}")
                    metadata = {}
                
                return {
                    'database_file': str(self.db_file),
                    'database_size_bytes': db_size,
                    'database_size_mb': round(db_size / (1024 * 1024), 2),
                    'table_counts': table_counts,
                    'metadata': metadata,
                    'session_id': self.session_id,
                    'connection_pool_size': len(self.connection_pool)
                }
        except Exception as e:
            self.logger.error(f"Failed to get database info: {e}")
            return {}
    
    def close_all_connections(self):
        """Close all database connections."""
        with self.pool_lock:
            for conn in self.connection_pool:
                try:
                    conn.close()
                except Exception:
                    pass
            self.connection_pool.clear()
    
    def get_setting(self, section: str, key: str, default: Any = None) -> Any:
        """Get a setting value from database."""
        try:
            query = "SELECT value, value_type FROM app_settings WHERE section = ? AND key = ?"
            result = self.execute_query(query, (section, key))
            
            if result:
                value = result[0]['value']
                value_type = result[0]['value_type']
                
                # Convert value based on type
                if value_type == 'integer':
                    return int(value)
                elif value_type == 'float':
                    return float(value)
                elif value_type == 'boolean':
                    return value.lower() in ('true', '1', 'yes')
                elif value_type == 'json':
                    return json.loads(value)
                else:
                    return value
            
            return default
        except Exception as e:
            self.logger.error(f"Failed to get setting {section}.{key}: {e}")
            return default
    
    def __del__(self):
        """Cleanup when object is destroyed."""
        try:
            self.close_all_connections()
        except Exception:
            pass


# Global instance
_database_manager = None


def get_database_manager() -> DatabaseManager:
    """Get the global DatabaseManager instance."""
    global _database_manager
    if _database_manager is None:
        _database_manager = DatabaseManager()
    return _database_manager
