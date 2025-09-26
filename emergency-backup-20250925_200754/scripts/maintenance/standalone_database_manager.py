"""
Standalone Database Manager for direct import testing.

This version can be imported without relative import issues.
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
                section TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                value_type TEXT NOT NULL DEFAULT 'string',
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
            "CREATE INDEX IF NOT EXISTS idx_file_history_path ON file_history(file_path)",
            "CREATE INDEX IF NOT EXISTS idx_file_history_accessed ON file_history(last_accessed DESC)",
            "CREATE INDEX IF NOT EXISTS idx_app_logs_timestamp ON app_logs(timestamp DESC)",
            "CREATE INDEX IF NOT EXISTS idx_app_logs_level ON app_logs(level)",
            "CREATE INDEX IF NOT EXISTS idx_app_settings_section ON app_settings(section)",
        ]
        
        for index_sql in indexes:
            conn.execute(index_sql)
    
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
        """Execute a SELECT query and return results."""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(query, params)
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            self.logger.error(f"Query execution failed: {e}")
            return []
    
    def execute_update(self, query: str, params: Tuple = ()) -> int:
        """Execute an UPDATE/INSERT/DELETE query and return affected rows."""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(query, params)
                conn.commit()
                return cursor.rowcount
        except Exception as e:
            self.logger.error(f"Update execution failed: {e}")
            return 0
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get database information and statistics."""
        try:
            with self.get_connection() as conn:
                # Get database size
                db_size = self.db_file.stat().st_size if self.db_file.exists() else 0
                
                # Get table counts
                tables = ['app_settings', 'file_history', 'app_logs']
                
                table_counts = {}
                for table in tables:
                    cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
                    table_counts[table] = cursor.fetchone()[0]
                
                # Get metadata
                cursor = conn.execute("SELECT * FROM db_metadata")
                metadata = {row['key']: row['value'] for row in cursor.fetchall()}
                
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


# Global instance
_database_manager = None


def get_database_manager() -> DatabaseManager:
    """Get the global DatabaseManager instance."""
    global _database_manager
    if _database_manager is None:
        _database_manager = DatabaseManager()
    return _database_manager
