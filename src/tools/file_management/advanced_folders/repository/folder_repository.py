"""
Repository pattern implementation for Advanced Folders feature.

This module provides a comprehensive data access layer with CRUD operations,
transaction management, and database abstraction following enterprise patterns.
"""

import json
import sqlite3
import threading
from abc import ABC, abstractmethod
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

from ..exceptions import RepositoryException, ValidationException
from ..models.folder_configuration import FolderConfiguration
from ..models.search_parameters import SearchParameters
from ..validation.validator_framework import ValidationFramework


class DatabaseConnectionManager:
    """
    Thread-safe database connection manager with connection pooling.

    Manages SQLite connections with proper resource cleanup and
    concurrent access handling.
    """

    def __init__(self, db_path: Union[str, Path], pool_size: int = 5):
        """
        Initialize connection manager.

        Args:
            db_path: Path to SQLite database file
            pool_size: Maximum number of connections in pool
        """
        self.db_path = Path(db_path)
        self.pool_size = pool_size
        self._connections = []
        self._lock = threading.Lock()
        self._local = threading.local()

        # Ensure database directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def get_connection(self) -> sqlite3.Connection:
        """
        Get a database connection for current thread.

        Returns:
            SQLite connection instance
        """
        # Check if current thread already has a connection
        if hasattr(self._local, "connection"):
            return self._local.connection

        with self._lock:
            # Try to reuse connection from pool
            if self._connections:
                conn = self._connections.pop()
            else:
                # Create new connection
                conn = sqlite3.connect(
                    str(self.db_path), check_same_thread=False, timeout=30.0
                )

                # Configure connection
                conn.row_factory = sqlite3.Row
                conn.execute("PRAGMA foreign_keys = ON")
                conn.execute("PRAGMA journal_mode = WAL")
                conn.execute("PRAGMA synchronous = NORMAL")
                conn.execute("PRAGMA cache_size = -64000")  # 64MB cache

            # Store connection for current thread
            self._local.connection = conn

        return conn

    def return_connection(self, conn: sqlite3.Connection) -> None:
        """
        Return connection to pool.

        Args:
            conn: Connection to return
        """
        if hasattr(self._local, "connection"):
            delattr(self._local, "connection")

        with self._lock:
            if len(self._connections) < self.pool_size:
                self._connections.append(conn)
            else:
                conn.close()

    @contextmanager
    def get_transaction(self):
        """
        Context manager for database transactions.

        Yields:
            Database connection with transaction
        """
        conn = self.get_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            self.return_connection(conn)

    def close_all(self) -> None:
        """Close all connections in pool."""
        with self._lock:
            for conn in self._connections:
                conn.close()
            self._connections.clear()

            if hasattr(self._local, "connection"):
                self._local.connection.close()
                delattr(self._local, "connection")


class BaseRepository(ABC):
    """
    Abstract base repository with common functionality.

    Provides foundation for all repository implementations with
    standard CRUD operations and transaction management.
    """

    def __init__(self, connection_manager: DatabaseConnectionManager):
        """
        Initialize base repository.

        Args:
            connection_manager: Database connection manager
        """
        self.connection_manager = connection_manager
        self.validator = ValidationFramework()
        self._initialized = False

    @abstractmethod
    def create_tables(self) -> None:
        """Create required database tables."""
        pass

    @abstractmethod
    def get_table_name(self) -> str:
        """Get primary table name for this repository."""
        pass

    def ensure_initialized(self) -> None:
        """Ensure repository is initialized."""
        if not self._initialized:
            self.create_tables()
            self._initialized = True

    def execute_query(
        self,
        query: str,
        params: Optional[tuple] = None,
        fetch_one: bool = False,
        fetch_all: bool = True,
    ) -> Any:
        """
        Execute a database query.

        Args:
            query: SQL query to execute
            params: Query parameters
            fetch_one: Whether to fetch only one result
            fetch_all: Whether to fetch all results

        Returns:
            Query results or None
        """
        try:
            with self.connection_manager.get_transaction() as conn:
                cursor = conn.execute(query, params or ())

                if fetch_one:
                    return cursor.fetchone()
                elif fetch_all:
                    return cursor.fetchall()
                else:
                    return cursor.rowcount

        except sqlite3.Error as e:
            raise RepositoryException(
                f"Database query failed: {str(e)}",
                operation="SELECT" if "SELECT" in query.upper() else "UNKNOWN",
                table_name=self.get_table_name(),
                query=query,
                cause=e,
            )
        except Exception as e:
            raise RepositoryException(
                f"Unexpected error during query execution: {str(e)}",
                query=query,
                cause=e,
            )

    def execute_update(
        self, query: str, params: Optional[tuple] = None
    ) -> int:
        """
        Execute an update/insert/delete query.

        Args:
            query: SQL query to execute
            params: Query parameters

        Returns:
            Number of affected rows
        """
        operation = "UPDATE"
        if "INSERT" in query.upper():
            operation = "INSERT"
        elif "DELETE" in query.upper():
            operation = "DELETE"

        try:
            with self.connection_manager.get_transaction() as conn:
                cursor = conn.execute(query, params or ())
                return cursor.rowcount

        except sqlite3.IntegrityError as e:
            raise RepositoryException(
                f"Data integrity violation: {str(e)}",
                operation=operation,
                table_name=self.get_table_name(),
                query=query,
                cause=e,
            )
        except sqlite3.Error as e:
            raise RepositoryException(
                f"Database {operation.lower()} failed: {str(e)}",
                operation=operation,
                table_name=self.get_table_name(),
                query=query,
                cause=e,
            )
        except Exception as e:
            raise RepositoryException(
                f"Unexpected error during {operation.lower()}: {str(e)}",
                operation=operation,
                query=query,
                cause=e,
            )

    def table_exists(self, table_name: str) -> bool:
        """
        Check if table exists in database.

        Args:
            table_name: Name of table to check

        Returns:
            True if table exists
        """
        query = """
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name=?
        """
        result = self.execute_query(query, (table_name,), fetch_one=True)
        return result is not None


class FolderRepository(BaseRepository):
    """
    Repository for folder configuration persistence.

    Provides CRUD operations for FolderConfiguration objects with
    relationship management and data integrity.
    """

    TABLE_NAME = "folder_configurations"
    TARGET_DIRS_TABLE = "folder_target_directories"

    def __init__(self, connection_manager: DatabaseConnectionManager):
        """
        Initialize folder repository.

        Args:
            connection_manager: Database connection manager
        """
        super().__init__(connection_manager)
        self.ensure_initialized()

    def get_table_name(self) -> str:
        """Get primary table name."""
        return self.TABLE_NAME

    def create_tables(self) -> None:
        """Create folder configuration tables."""
        # Main folder configurations table
        main_table_sql = f"""
            CREATE TABLE IF NOT EXISTS {self.TABLE_NAME} (
                folder_id TEXT PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                folder_type TEXT NOT NULL,
                created_at TEXT NOT NULL,
                modified_at TEXT NOT NULL,
                last_accessed_at TEXT NOT NULL,
                performance_settings TEXT NOT NULL,
                security_settings TEXT NOT NULL,
                monitoring_mode TEXT NOT NULL,
                indexing_strategy TEXT NOT NULL,
                auto_refresh_enabled INTEGER NOT NULL DEFAULT 1,
                auto_refresh_interval_minutes INTEGER NOT NULL DEFAULT 15,
                metadata TEXT,
                tags TEXT,
                last_scan_count INTEGER DEFAULT 0,
                last_scan_time TEXT,
                total_size_bytes INTEGER DEFAULT 0,
                is_active INTEGER NOT NULL DEFAULT 1,
                is_persistent INTEGER NOT NULL DEFAULT 1,
                version INTEGER NOT NULL DEFAULT 1,
                CONSTRAINT valid_folder_type CHECK (
                    folder_type IN ('smart_folder', 'search_folder', 'virtual_folder', 'dynamic_folder')
                ),
                CONSTRAINT valid_monitoring_mode CHECK (
                    monitoring_mode IN ('none', 'basic', 'full', 'real_time')
                ),
                CONSTRAINT valid_indexing_strategy CHECK (
                    indexing_strategy IN ('none', 'metadata_only', 'content_basic', 'content_full')
                )
            )
        """

        # Target directories table
        target_dirs_sql = f"""
            CREATE TABLE IF NOT EXISTS {self.TARGET_DIRS_TABLE} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                folder_id TEXT NOT NULL,
                path TEXT NOT NULL,
                include_subdirectories INTEGER NOT NULL DEFAULT 1,
                follow_symlinks INTEGER NOT NULL DEFAULT 0,
                max_depth INTEGER,
                exclude_patterns TEXT,
                FOREIGN KEY (folder_id) REFERENCES {self.TABLE_NAME} (folder_id) ON DELETE CASCADE,
                UNIQUE (folder_id, path)
            )
        """

        # Create indexes
        indexes_sql = [
            f"CREATE INDEX IF NOT EXISTS idx_folder_name ON {self.TABLE_NAME} (name)",
            f"CREATE INDEX IF NOT EXISTS idx_folder_type ON {self.TABLE_NAME} (folder_type)",
            f"CREATE INDEX IF NOT EXISTS idx_folder_active ON {self.TABLE_NAME} (is_active)",
            f"CREATE INDEX IF NOT EXISTS idx_folder_modified ON {self.TABLE_NAME} (modified_at)",
            f"CREATE INDEX IF NOT EXISTS idx_target_folder_id ON {self.TARGET_DIRS_TABLE} (folder_id)",
            f"CREATE INDEX IF NOT EXISTS idx_target_path ON {self.TARGET_DIRS_TABLE} (path)",
        ]

        try:
            # Execute table creation
            self.execute_update(main_table_sql)
            self.execute_update(target_dirs_sql)

            # Create indexes
            for index_sql in indexes_sql:
                self.execute_update(index_sql)

        except Exception as e:
            raise RepositoryException(
                f"Failed to create folder configuration tables: {str(e)}",
                operation="CREATE",
                cause=e,
            )

    def create(
        self, folder_config: FolderConfiguration
    ) -> FolderConfiguration:
        """
        Create a new folder configuration.

        Args:
            folder_config: Configuration to create

        Returns:
            Created configuration with any updates

        Raises:
            RepositoryException: If creation fails
            ValidationException: If validation fails
        """
        # Validate configuration
        folder_config.validate_integrity()

        try:
            with self.connection_manager.get_transaction() as conn:
                # Insert main configuration
                main_insert_sql = f"""
                    INSERT INTO {self.TABLE_NAME} (
                        folder_id, name, description, folder_type,
                        created_at, modified_at, last_accessed_at,
                        performance_settings, security_settings,
                        monitoring_mode, indexing_strategy,
                        auto_refresh_enabled, auto_refresh_interval_minutes,
                        metadata, tags, last_scan_count, last_scan_time,
                        total_size_bytes, is_active, is_persistent, version
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """

                main_params = (
                    folder_config.folder_id,
                    folder_config.name,
                    folder_config.description,
                    folder_config.folder_type.value,
                    folder_config.created_at.isoformat(),
                    folder_config.modified_at.isoformat(),
                    folder_config.last_accessed_at.isoformat(),
                    json.dumps(folder_config.performance_settings.__dict__),
                    json.dumps(folder_config.security_settings.to_dict()),
                    folder_config.monitoring_mode.value,
                    folder_config.indexing_strategy.value,
                    folder_config.auto_refresh_enabled,
                    folder_config.auto_refresh_interval_minutes,
                    json.dumps(folder_config.metadata),
                    json.dumps(list(folder_config.tags)),
                    folder_config.last_scan_count,
                    (
                        folder_config.last_scan_time.isoformat()
                        if folder_config.last_scan_time
                        else None
                    ),
                    folder_config.total_size_bytes,
                    folder_config.is_active,
                    folder_config.is_persistent,
                    folder_config.version,
                )

                conn.execute(main_insert_sql, main_params)

                # Insert target directories
                if folder_config.target_directories:
                    target_insert_sql = f"""
                        INSERT INTO {self.TARGET_DIRS_TABLE} (
                            folder_id, path, include_subdirectories,
                            follow_symlinks, max_depth, exclude_patterns
                        ) VALUES (?, ?, ?, ?, ?, ?)
                    """

                    for target in folder_config.target_directories:
                        target_params = (
                            folder_config.folder_id,
                            target.path,
                            target.include_subdirectories,
                            target.follow_symlinks,
                            target.max_depth,
                            json.dumps(target.exclude_patterns),
                        )
                        conn.execute(target_insert_sql, target_params)

                conn.commit()

            return folder_config

        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e) and "name" in str(e):
                raise ValidationException(
                    f"Folder name '{folder_config.name}' already exists",
                    field_name="name",
                    field_value=folder_config.name,
                    validation_rule="unique",
                )
            else:
                raise RepositoryException(
                    f"Data integrity violation while creating folder: {str(e)}",
                    operation="INSERT",
                    table_name=self.TABLE_NAME,
                    cause=e,
                )
        except Exception as e:
            raise RepositoryException(
                f"Failed to create folder configuration: {str(e)}",
                operation="INSERT",
                table_name=self.TABLE_NAME,
                cause=e,
            )

    def get_by_id(self, folder_id: str) -> Optional[FolderConfiguration]:
        """
        Get folder configuration by ID.

        Args:
            folder_id: Folder ID to search for

        Returns:
            FolderConfiguration if found, None otherwise
        """
        query = f"SELECT * FROM {self.TABLE_NAME} WHERE folder_id = ?"
        row = self.execute_query(query, (folder_id,), fetch_one=True)

        if row:
            return self._row_to_folder_config(row)
        return None

    def get_by_name(self, name: str) -> Optional[FolderConfiguration]:
        """
        Get folder configuration by name.

        Args:
            name: Folder name to search for

        Returns:
            FolderConfiguration if found, None otherwise
        """
        query = f"SELECT * FROM {self.TABLE_NAME} WHERE name = ?"
        row = self.execute_query(query, (name,), fetch_one=True)

        if row:
            return self._row_to_folder_config(row)
        return None

    def get_all(self, active_only: bool = True) -> List[FolderConfiguration]:
        """
        Get all folder configurations.

        Args:
            active_only: Whether to return only active configurations

        Returns:
            List of folder configurations
        """
        if active_only:
            query = f"SELECT * FROM {self.TABLE_NAME} WHERE is_active = 1 ORDER BY name"
        else:
            query = f"SELECT * FROM {self.TABLE_NAME} ORDER BY name"

        rows = self.execute_query(query)
        return [self._row_to_folder_config(row) for row in rows]

    def get_by_type(self, folder_type: str) -> List[FolderConfiguration]:
        """
        Get folder configurations by type.

        Args:
            folder_type: Type of folder to filter by

        Returns:
            List of matching folder configurations
        """
        query = f"SELECT * FROM {self.TABLE_NAME} WHERE folder_type = ? AND is_active = 1 ORDER BY name"
        rows = self.execute_query(query, (folder_type,))
        return [self._row_to_folder_config(row) for row in rows]

    def update(
        self, folder_config: FolderConfiguration
    ) -> FolderConfiguration:
        """
        Update existing folder configuration.

        Args:
            folder_config: Configuration to update

        Returns:
            Updated configuration

        Raises:
            RepositoryException: If update fails
            ValidationException: If validation fails
        """
        # Validate configuration
        folder_config.validate_integrity()

        # Update modified time and version
        folder_config.modified_at = datetime.now(timezone.utc)
        folder_config.version += 1

        try:
            with self.connection_manager.get_transaction() as conn:
                # Update main configuration
                main_update_sql = f"""
                    UPDATE {self.TABLE_NAME} SET
                        name = ?, description = ?, folder_type = ?,
                        modified_at = ?, last_accessed_at = ?,
                        performance_settings = ?, security_settings = ?,
                        monitoring_mode = ?, indexing_strategy = ?,
                        auto_refresh_enabled = ?, auto_refresh_interval_minutes = ?,
                        metadata = ?, tags = ?, last_scan_count = ?,
                        last_scan_time = ?, total_size_bytes = ?,
                        is_active = ?, is_persistent = ?, version = ?
                    WHERE folder_id = ?
                """

                main_params = (
                    folder_config.name,
                    folder_config.description,
                    folder_config.folder_type.value,
                    folder_config.modified_at.isoformat(),
                    folder_config.last_accessed_at.isoformat(),
                    json.dumps(folder_config.performance_settings.__dict__),
                    json.dumps(folder_config.security_settings.to_dict()),
                    folder_config.monitoring_mode.value,
                    folder_config.indexing_strategy.value,
                    folder_config.auto_refresh_enabled,
                    folder_config.auto_refresh_interval_minutes,
                    json.dumps(folder_config.metadata),
                    json.dumps(list(folder_config.tags)),
                    folder_config.last_scan_count,
                    (
                        folder_config.last_scan_time.isoformat()
                        if folder_config.last_scan_time
                        else None
                    ),
                    folder_config.total_size_bytes,
                    folder_config.is_active,
                    folder_config.is_persistent,
                    folder_config.version,
                    folder_config.folder_id,
                )

                rows_affected = conn.execute(
                    main_update_sql, main_params
                ).rowcount

                if rows_affected == 0:
                    raise RepositoryException(
                        f"Folder configuration not found: {folder_config.folder_id}",
                        operation="UPDATE",
                        table_name=self.TABLE_NAME,
                    )

                # Update target directories (delete and recreate)
                delete_targets_sql = (
                    f"DELETE FROM {self.TARGET_DIRS_TABLE} WHERE folder_id = ?"
                )
                conn.execute(delete_targets_sql, (folder_config.folder_id,))

                if folder_config.target_directories:
                    target_insert_sql = f"""
                        INSERT INTO {self.TARGET_DIRS_TABLE} (
                            folder_id, path, include_subdirectories,
                            follow_symlinks, max_depth, exclude_patterns
                        ) VALUES (?, ?, ?, ?, ?, ?)
                    """

                    for target in folder_config.target_directories:
                        target_params = (
                            folder_config.folder_id,
                            target.path,
                            target.include_subdirectories,
                            target.follow_symlinks,
                            target.max_depth,
                            json.dumps(target.exclude_patterns),
                        )
                        conn.execute(target_insert_sql, target_params)

                conn.commit()

            return folder_config

        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e) and "name" in str(e):
                raise ValidationException(
                    f"Folder name '{folder_config.name}' already exists",
                    field_name="name",
                    field_value=folder_config.name,
                    validation_rule="unique",
                )
            else:
                raise RepositoryException(
                    f"Data integrity violation while updating folder: {str(e)}",
                    operation="UPDATE",
                    table_name=self.TABLE_NAME,
                    cause=e,
                )
        except Exception as e:
            raise RepositoryException(
                f"Failed to update folder configuration: {str(e)}",
                operation="UPDATE",
                table_name=self.TABLE_NAME,
                cause=e,
            )

    def delete(self, folder_id: str) -> bool:
        """
        Delete folder configuration.

        Args:
            folder_id: ID of folder to delete

        Returns:
            True if deleted, False if not found
        """
        try:
            with self.connection_manager.get_transaction() as conn:
                # Delete target directories first (foreign key constraint)
                delete_targets_sql = (
                    f"DELETE FROM {self.TARGET_DIRS_TABLE} WHERE folder_id = ?"
                )
                conn.execute(delete_targets_sql, (folder_id,))

                # Delete main configuration
                delete_main_sql = (
                    f"DELETE FROM {self.TABLE_NAME} WHERE folder_id = ?"
                )
                cursor = conn.execute(delete_main_sql, (folder_id,))

                conn.commit()

                return cursor.rowcount > 0

        except Exception as e:
            raise RepositoryException(
                f"Failed to delete folder configuration: {str(e)}",
                operation="DELETE",
                table_name=self.TABLE_NAME,
                cause=e,
            )

    def exists(self, folder_id: str) -> bool:
        """
        Check if folder configuration exists.

        Args:
            folder_id: Folder ID to check

        Returns:
            True if exists
        """
        query = f"SELECT 1 FROM {self.TABLE_NAME} WHERE folder_id = ?"
        result = self.execute_query(query, (folder_id,), fetch_one=True)
        return result is not None

    def name_exists(self, name: str, exclude_id: Optional[str] = None) -> bool:
        """
        Check if folder name exists.

        Args:
            name: Folder name to check
            exclude_id: Folder ID to exclude from check

        Returns:
            True if name exists
        """
        if exclude_id:
            query = f"SELECT 1 FROM {self.TABLE_NAME} WHERE name = ? AND folder_id != ?"
            result = self.execute_query(
                query, (name, exclude_id), fetch_one=True
            )
        else:
            query = f"SELECT 1 FROM {self.TABLE_NAME} WHERE name = ?"
            result = self.execute_query(query, (name,), fetch_one=True)

        return result is not None

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get repository statistics.

        Returns:
            Dictionary with statistics
        """
        stats_query = f"""
            SELECT 
                COUNT(*) as total_folders,
                COUNT(CASE WHEN is_active = 1 THEN 1 END) as active_folders,
                COUNT(CASE WHEN folder_type = 'smart_folder' THEN 1 END) as smart_folders,
                COUNT(CASE WHEN folder_type = 'search_folder' THEN 1 END) as search_folders,
                AVG(last_scan_count) as avg_scan_count,
                SUM(total_size_bytes) as total_size_bytes
            FROM {self.TABLE_NAME}
        """

        targets_query = (
            f"SELECT COUNT(*) as total_targets FROM {self.TARGET_DIRS_TABLE}"
        )

        stats_row = self.execute_query(stats_query, fetch_one=True)
        targets_row = self.execute_query(targets_query, fetch_one=True)

        return {
            "total_folders": stats_row["total_folders"],
            "active_folders": stats_row["active_folders"],
            "smart_folders": stats_row["smart_folders"],
            "search_folders": stats_row["search_folders"],
            "total_targets": targets_row["total_targets"],
            "avg_scan_count": stats_row["avg_scan_count"] or 0,
            "total_size_bytes": stats_row["total_size_bytes"] or 0,
        }

    def _row_to_folder_config(self, row: sqlite3.Row) -> FolderConfiguration:
        """
        Convert database row to FolderConfiguration object.

        Args:
            row: Database row

        Returns:
            FolderConfiguration instance
        """
        try:
            # Load target directories
            targets_query = (
                f"SELECT * FROM {self.TARGET_DIRS_TABLE} WHERE folder_id = ?"
            )
            target_rows = self.execute_query(
                targets_query, (row["folder_id"],)
            )

            # Convert row to dictionary
            config_data = {
                "folder_id": row["folder_id"],
                "name": row["name"],
                "description": row["description"],
                "folder_type": row["folder_type"],
                "created_at": row["created_at"],
                "modified_at": row["modified_at"],
                "last_accessed_at": row["last_accessed_at"],
                "performance_settings": json.loads(
                    row["performance_settings"]
                ),
                "security_settings": json.loads(row["security_settings"]),
                "monitoring_mode": row["monitoring_mode"],
                "indexing_strategy": row["indexing_strategy"],
                "auto_refresh_enabled": bool(row["auto_refresh_enabled"]),
                "auto_refresh_interval_minutes": row[
                    "auto_refresh_interval_minutes"
                ],
                "metadata": json.loads(row["metadata"]),
                "tags": json.loads(row["tags"]),
                "last_scan_count": row["last_scan_count"],
                "last_scan_time": row["last_scan_time"],
                "total_size_bytes": row["total_size_bytes"],
                "is_active": bool(row["is_active"]),
                "is_persistent": bool(row["is_persistent"]),
                "version": row["version"],
                "target_directories": [],
            }

            # Add target directories
            for target_row in target_rows:
                target_data = {
                    "path": target_row["path"],
                    "include_subdirectories": bool(
                        target_row["include_subdirectories"]
                    ),
                    "follow_symlinks": bool(target_row["follow_symlinks"]),
                    "max_depth": target_row["max_depth"],
                    "exclude_patterns": json.loads(
                        target_row["exclude_patterns"]
                    ),
                }
                config_data["target_directories"].append(target_data)

            return FolderConfiguration.from_dict(config_data)

        except Exception as e:
            raise RepositoryException(
                f"Failed to convert database row to folder configuration: {str(e)}",
                operation="SELECT",
                table_name=self.TABLE_NAME,
                cause=e,
            )
