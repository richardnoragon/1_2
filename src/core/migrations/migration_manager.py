"""
Database Migration Manager - Central orchestrator for database migrations.

This module handles the execution of database migrations with comprehensive
error handling, rollback capabilities, and validation.
"""

import sqlite3
import logging
import threading
import uuid
import importlib
import pkgutil
from datetime import datetime
from typing import Optional, List, Dict, Any, Set
from pathlib import Path

from .migration_base import (
    MigrationBase,
    MigrationResult,
    MigrationStatus,
    ValidationResult,
    MigrationError,
    MigrationLockError,
    MigrationValidationError,
)
from .rollback_manager import RollbackManager
from .schema_validator import SchemaValidator


class MigrationLockManager:
    """Manages migration locks to prevent concurrent migrations."""

    def __init__(self, database_manager):
        self.db_manager = database_manager
        self.logger = logging.getLogger("RFU.MigrationLockManager")
        self.lock_timeout_seconds = 300  # 5 minutes

    def acquire_lock(self, migration_version: str) -> bool:
        """
        Acquire migration lock.

        Args:
            migration_version: Version of migration requesting lock

        Returns:
            True if lock was acquired successfully
        """
        try:
            process_id = str(uuid.uuid4())
            expires_at = datetime.now().timestamp() + self.lock_timeout_seconds

            # Try to acquire lock
            rows_affected = self.db_manager.execute_update(
                """
                INSERT OR IGNORE INTO migration_locks 
                (id, locked_by, migration_version, process_id, expires_at)
                VALUES (1, ?, ?, ?, ?)
            """,
                (
                    "migration_manager",
                    migration_version,
                    process_id,
                    datetime.fromtimestamp(expires_at).isoformat(),
                ),
            )

            if rows_affected > 0:
                self.logger.info(
                    f"Acquired migration lock for {migration_version}"
                )
                return True

            # Check if existing lock has expired
            existing_lock = self.db_manager.execute_query(
                """
                SELECT expires_at FROM migration_locks WHERE id = 1
            """
            )

            if existing_lock:
                lock_expires = datetime.fromisoformat(
                    existing_lock[0]["expires_at"]
                )
                if lock_expires < datetime.now():
                    # Force release expired lock
                    self.force_release_lock()
                    # Try to acquire again
                    return self.acquire_lock(migration_version)

            return False

        except Exception as e:
            self.logger.error(f"Failed to acquire migration lock: {e}")
            return False

    def release_lock(self) -> bool:
        """Release migration lock."""
        try:
            self.db_manager.execute_update(
                "DELETE FROM migration_locks WHERE id = 1"
            )
            self.logger.info("Released migration lock")
            return True
        except Exception as e:
            self.logger.error(f"Failed to release migration lock: {e}")
            return False

    def force_release_lock(self) -> bool:
        """Force release migration lock (for expired locks)."""
        try:
            self.db_manager.execute_update(
                "DELETE FROM migration_locks WHERE id = 1"
            )
            self.logger.warning("Force released migration lock")
            return True
        except Exception as e:
            self.logger.error(f"Failed to force release migration lock: {e}")
            return False

    def is_locked(self) -> bool:
        """Check if migration system is currently locked."""
        try:
            result = self.db_manager.execute_query(
                """
                SELECT expires_at FROM migration_locks WHERE id = 1
            """
            )

            if not result:
                return False

            lock_expires = datetime.fromisoformat(result[0]["expires_at"])
            return lock_expires > datetime.now()

        except Exception:
            return False


class DatabaseMigrationManager:
    """
    Central migration orchestrator that handles the execution of database
    migrations with comprehensive error handling and rollback capabilities.
    """

    def __init__(self, database_manager):
        self.db_manager = database_manager
        self.logger = logging.getLogger("RFU.MigrationManager")
        self.rollback_manager = RollbackManager(database_manager)
        self.validator = SchemaValidator(database_manager)
        self.lock_manager = MigrationLockManager(database_manager)
        self._initialize_migration_tables()

    def _initialize_migration_tables(self):
        """Initialize migration tracking tables if they don't exist."""
        try:
            with self.db_manager.get_connection() as conn:
                # Migration history table
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS migration_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        version TEXT NOT NULL UNIQUE,
                        description TEXT NOT NULL,
                        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        applied_by TEXT DEFAULT 'system',
                        execution_time_ms INTEGER NOT NULL,
                        checksum TEXT NOT NULL,
                        rollback_script_checksum TEXT,
                        dependencies TEXT,
                        breaking_changes BOOLEAN DEFAULT FALSE,
                        status TEXT DEFAULT 'applied' 
                            CHECK (status IN ('applied', 'rolled_back', 'failed')),
                        error_message TEXT,
                        backup_id TEXT
                    )
                """
                )

                # Migration locks table
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS migration_locks (
                        id INTEGER PRIMARY KEY CHECK (id = 1),
                        locked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        locked_by TEXT NOT NULL,
                        migration_version TEXT,
                        process_id TEXT,
                        expires_at TIMESTAMP
                    )
                """
                )

                # Migration backups table
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS migration_backups (
                        id TEXT PRIMARY KEY,
                        migration_version TEXT NOT NULL,
                        backup_type TEXT NOT NULL 
                            CHECK (backup_type IN ('pre_migration', 'pre_rollback', 'emergency')),
                        file_path TEXT NOT NULL,
                        file_size_bytes INTEGER NOT NULL,
                        checksum TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP,
                        compression_type TEXT DEFAULT 'gzip'
                    )
                """
                )

                # Schema checksums table
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS schema_checksums (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        migration_version TEXT NOT NULL,
                        table_name TEXT NOT NULL,
                        schema_checksum TEXT NOT NULL,
                        data_checksum TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(migration_version, table_name)
                    )
                """
                )

                conn.commit()

        except Exception as e:
            self.logger.error(f"Failed to initialize migration tables: {e}")
            raise

    def execute_migrations(
        self, target_version: Optional[str] = None
    ) -> MigrationResult:
        """
        Execute pending migrations up to target version.

        Args:
            target_version: Target migration version (None for latest)

        Returns:
            MigrationResult with execution outcome and details
        """
        start_time = datetime.now()

        try:
            # Check if system is locked
            if self.lock_manager.is_locked():
                raise MigrationLockError(
                    "Migration system is currently locked"
                )

            # Acquire migration lock
            if not self.lock_manager.acquire_lock(target_version or "latest"):
                raise MigrationLockError("Could not acquire migration lock")

            try:
                # Get pending migrations
                pending_migrations = self._get_pending_migrations(
                    target_version
                )

                if not pending_migrations:
                    return MigrationResult(
                        success=True,
                        version="no_migrations",
                        execution_time_ms=0,
                    )

                # Validate system state before migration
                validation_result = self.validator.validate_schema_integrity()
                if not validation_result.success:
                    raise MigrationValidationError(
                        f"Pre-migration validation failed: {validation_result.message}"
                    )

                # Execute each pending migration
                for migration_version in pending_migrations:
                    self._execute_single_migration(migration_version)

                execution_time = (
                    datetime.now() - start_time
                ).total_seconds() * 1000

                return MigrationResult(
                    success=True,
                    version=(
                        pending_migrations[-1]
                        if pending_migrations
                        else "none"
                    ),
                    execution_time_ms=int(execution_time),
                )

            finally:
                # Always release lock
                self.lock_manager.release_lock()

        except Exception as e:
            execution_time = (
                datetime.now() - start_time
            ).total_seconds() * 1000
            self.logger.error(f"Migration execution failed: {e}")

            return MigrationResult(
                success=False,
                version="failed",
                execution_time_ms=int(execution_time),
                error=str(e),
            )

    def rollback_to_version(self, target_version: str) -> MigrationResult:
        """
        Rollback database to specific version.

        Args:
            target_version: Target version to rollback to

        Returns:
            MigrationResult with rollback outcome
        """
        start_time = datetime.now()

        try:
            # Check if system is locked
            if self.lock_manager.is_locked():
                raise MigrationLockError(
                    "Migration system is currently locked"
                )

            # Acquire migration lock
            if not self.lock_manager.acquire_lock(
                f"rollback_to_{target_version}"
            ):
                raise MigrationLockError(
                    "Could not acquire migration lock for rollback"
                )

            try:
                # Execute rollback
                rollback_result = self.rollback_manager.execute_rollback(
                    target_version
                )

                execution_time = (
                    datetime.now() - start_time
                ).total_seconds() * 1000

                if rollback_result.success:
                    return MigrationResult(
                        success=True,
                        version=target_version,
                        execution_time_ms=int(execution_time),
                        rollback_executed=True,
                    )
                else:
                    return MigrationResult(
                        success=False,
                        version=target_version,
                        execution_time_ms=int(execution_time),
                        error=rollback_result.error,
                        rollback_executed=True,
                    )

            finally:
                # Always release lock
                self.lock_manager.release_lock()

        except Exception as e:
            execution_time = (
                datetime.now() - start_time
            ).total_seconds() * 1000
            self.logger.error(f"Rollback execution failed: {e}")

            return MigrationResult(
                success=False,
                version=target_version,
                execution_time_ms=int(execution_time),
                error=str(e),
                rollback_executed=False,
            )

    def get_migration_status(self) -> MigrationStatus:
        """
        Get current migration status and pending migrations.

        Returns:
            MigrationStatus with current state information
        """
        try:
            # Get current version
            current_version = self._get_current_version()

            # Get applied migrations
            applied_migrations = self.db_manager.execute_query(
                """
                SELECT version FROM migration_history 
                WHERE status = 'applied' 
                ORDER BY applied_at
            """
            )
            applied_versions = [m["version"] for m in applied_migrations]

            # Get pending migrations (would need migration discovery mechanism)
            pending_migrations = self._get_pending_migrations()

            # Get last migration date
            last_migration = self.db_manager.execute_query(
                """
                SELECT applied_at FROM migration_history 
                WHERE status = 'applied' 
                ORDER BY applied_at DESC 
                LIMIT 1
            """
            )
            last_migration_date = (
                last_migration[0]["applied_at"] if last_migration else None
            )

            # Check if system is locked
            database_locked = self.lock_manager.is_locked()

            return MigrationStatus(
                current_version=current_version,
                pending_migrations=pending_migrations,
                applied_migrations=applied_versions,
                last_migration_date=last_migration_date,
                database_locked=database_locked,
            )

        except Exception as e:
            self.logger.error(f"Failed to get migration status: {e}")
            return MigrationStatus(
                current_version="error",
                pending_migrations=[],
                applied_migrations=[],
                last_migration_date=None,
                database_locked=True,
            )

    def validate_migration_integrity(self) -> ValidationResult:
        """
        Validate migration history and database integrity.

        Returns:
            ValidationResult with validation outcome
        """
        try:
            # Validate schema integrity
            schema_result = self.validator.validate_schema_integrity()
            if not schema_result.success:
                return schema_result

            # Validate migration consistency
            migration_result = self.validator.validate_migration_consistency()
            if not migration_result.success:
                return migration_result

            # Validate data integrity
            data_result = self.validator.validate_data_integrity()
            if not data_result.success:
                return data_result

            return ValidationResult(
                success=True, message="All migration integrity checks passed"
            )

        except Exception as e:
            self.logger.error(f"Migration integrity validation failed: {e}")
            return ValidationResult(
                success=False, message=f"Integrity validation error: {e}"
            )

    def _get_current_version(self) -> str:
        """Get the current database migration version."""
        try:
            result = self.db_manager.execute_query(
                """
                SELECT version FROM migration_history 
                WHERE status = 'applied' 
                ORDER BY applied_at DESC 
                LIMIT 1
            """
            )

            if result:
                return result[0]["version"]
            else:
                return "000"  # No migrations applied
        except Exception:
            return "000"

    def _validate_target_version(
        self, target_version: Optional[str]
    ) -> Optional[str]:
        """Validate and clean target version parameter."""
        if target_version is not None:
            if (
                not isinstance(target_version, str)
                or not target_version.strip()
            ):
                raise MigrationValidationError(
                    "Target version must be a non-empty string"
                )
            return target_version.strip()
        return None

    def _get_applied_migrations_set(self) -> Set[str]:
        """Get set of applied migration versions."""
        try:
            applied_migrations = self.db_manager.execute_query(
                """
                SELECT version FROM migration_history 
                WHERE status = 'applied' 
                ORDER BY version
            """
            )
            applied_versions = {m["version"] for m in applied_migrations}
            self.logger.debug(
                f"Found {len(applied_versions)} applied migrations"
            )
            return applied_versions
        except Exception as e:
            self.logger.error(f"Failed to query applied migrations: {e}")
            raise MigrationError(f"Unable to retrieve migration history: {e}")

    def _get_available_migrations_dict(self) -> Dict[str, type]:
        """Get available migration classes."""
        try:
            available_migrations = self._discover_migrations()
            if not available_migrations:
                self.logger.warning("No available migrations found")
                return {}
            self.logger.debug(
                f"Found {len(available_migrations)} available migrations"
            )
            return available_migrations
        except Exception as e:
            self.logger.error(f"Failed to discover migrations: {e}")
            raise MigrationError(
                f"Unable to discover available migrations: {e}"
            )

    def _filter_pending_migrations_list(
        self,
        available: Dict[str, type],
        applied: Set[str],
        target: Optional[str],
    ) -> List[str]:
        """Filter available migrations to get pending ones."""
        # Validate target version exists if specified
        if target and target not in available:
            available_versions = sorted(available.keys())
            raise MigrationValidationError(
                f"Target version '{target}' not found. "
                f"Available versions: {available_versions}"
            )

        # Get current version for validation
        try:
            current_version = self._get_current_version()
            self.logger.debug(f"Current database version: {current_version}")
        except Exception as e:
            self.logger.warning(f"Failed to get current version: {e}")
            current_version = "000"

        # Find pending migrations
        pending = []
        all_versions = sorted(available.keys())

        for version in all_versions:
            # Skip if already applied
            if version in applied:
                self.logger.debug(f"Skipping applied migration: {version}")
                continue

            # Skip if version is older than current
            if version < current_version:
                self.logger.warning(
                    f"Migration {version} is older than current version {current_version}, skipping"
                )
                continue

            # Add to pending list
            pending.append(version)
            self.logger.debug(f"Added pending migration: {version}")

            # Stop if we've reached the target version
            if target and version == target:
                self.logger.debug(f"Reached target version {target}, stopping")
                break

        return pending

    def _validate_pending_chain_integrity(
        self, pending: List[str], available: Dict[str, type]
    ) -> None:
        """Validate migration chain integrity."""
        if pending:
            try:
                self._validate_migration_chain(pending, available)
            except Exception as e:
                raise MigrationValidationError(
                    f"Migration chain validation failed: {e}"
                )

    def _log_pending_migration_results(self, pending: List[str]) -> None:
        """Log results of pending migration discovery."""
        if pending:
            self.logger.info(
                f"Found {len(pending)} pending migrations: {pending}"
            )
        else:
            self.logger.info("No pending migrations found")

    def _get_pending_migrations(
        self, target_version: Optional[str] = None
    ) -> List[str]:
        """
        Get list of pending migrations to execute.

        Args:
            target_version: Target version to migrate to (None for all pending)

        Returns:
            List of migration versions to execute in order
        """
        try:
            self.logger.debug(
                f"Getting pending migrations (target: {target_version})"
            )

            # Validate and clean target version
            target_version = self._validate_target_version(target_version)

            # Get applied and available migrations
            applied_versions = self._get_applied_migrations_set()
            available_migrations = self._get_available_migrations_dict()

            # Filter pending migrations
            pending = self._filter_pending_migrations_list(
                available_migrations, applied_versions, target_version
            )

            # Validate migration chain
            if pending:
                self._validate_pending_chain_integrity(
                    pending, available_migrations
                )

            # Log results and return
            self._log_pending_migration_results(pending)
            return pending

        except (MigrationError, MigrationValidationError):
            # Re-raise our custom exceptions
            raise
        except sqlite3.Error as e:
            self.logger.error(
                f"Database error while getting pending migrations: {e}"
            )
            raise MigrationError(f"Database error: {e}")
        except Exception as e:
            self.logger.error(
                f"Unexpected error while getting pending migrations: {e}"
            )
            raise MigrationError(f"Unexpected error: {e}")

    def _discover_migrations(self) -> Dict[str, type]:
        """
        Discover available migration classes.

        Returns:
            Dictionary mapping version strings to migration classes
        """
        migrations = {}

        try:
            # Import the migrations package
            from .migrations import (
                Migration001InitialSchema,
                Migration002AddEncryptionSupport,
            )

            # Register known migrations
            migration_classes = [
                Migration001InitialSchema,
                Migration002AddEncryptionSupport,
            ]

            for migration_class in migration_classes:
                try:
                    # Create instance to get metadata
                    instance = migration_class()
                    version = instance.metadata.version
                    migrations[version] = migration_class
                    self.logger.debug(
                        f"Discovered migration {version}: {migration_class.__name__}"
                    )
                except Exception as e:
                    self.logger.warning(
                        f"Failed to register migration {migration_class.__name__}: {e}"
                    )

            self.logger.info(f"Discovered {len(migrations)} migrations")
            return migrations

        except Exception as e:
            self.logger.error(f"Failed to discover migrations: {e}")
            return {}

    def _validate_migration_chain(
        self,
        pending_migrations: List[str],
        available_migrations: Dict[str, type],
    ) -> None:
        """
        Validate that the migration chain is complete and dependencies are met.

        Args:
            pending_migrations: List of pending migration versions
            available_migrations: Dictionary of available migrations

        Raises:
            MigrationValidationError: If validation fails
        """
        if not pending_migrations:
            return

        self.logger.debug(f"Validating migration chain: {pending_migrations}")

        try:
            self._check_migrations_exist(
                pending_migrations, available_migrations
            )
            self._validate_migration_metadata(
                pending_migrations, available_migrations
            )
            self._validate_version_ordering(pending_migrations)
            self.logger.debug(
                "Migration chain validation completed successfully"
            )

        except MigrationValidationError:
            raise
        except Exception as e:
            raise MigrationValidationError(
                f"Unexpected error during chain validation: {e}"
            )

    def _check_migrations_exist(
        self,
        pending_migrations: List[str],
        available_migrations: Dict[str, type],
    ) -> None:
        """Check that all migrations in chain exist."""
        for version in pending_migrations:
            if version not in available_migrations:
                raise MigrationValidationError(
                    f"Migration {version} not found in available migrations"
                )

    def _validate_migration_metadata(
        self,
        pending_migrations: List[str],
        available_migrations: Dict[str, type],
    ) -> None:
        """Validate migration metadata and dependencies."""
        for version in pending_migrations:
            try:
                migration_class = available_migrations[version]
                migration_instance = migration_class()
                metadata = migration_instance.metadata

                self._validate_metadata_format(version, metadata)
                self._validate_dependencies(
                    version, metadata, available_migrations
                )

                self.logger.debug(
                    f"Validated migration {version}: {metadata.description}"
                )

            except Exception as e:
                raise MigrationValidationError(
                    f"Failed to validate migration {version}: {e}"
                )

    def _validate_metadata_format(self, version: str, metadata) -> None:
        """Validate the format of migration metadata."""
        if not metadata.version or not isinstance(metadata.version, str):
            raise MigrationValidationError(
                f"Migration {version} has invalid version metadata"
            )

    def _validate_dependencies(
        self, version: str, metadata, available_migrations: Dict[str, type]
    ) -> None:
        """Validate migration dependencies."""
        if hasattr(metadata, "dependencies") and metadata.dependencies:
            for dep_version in metadata.dependencies:
                if dep_version not in available_migrations:
                    raise MigrationValidationError(
                        f"Migration {version} depends on unavailable "
                        f"migration {dep_version}"
                    )

    def _validate_version_ordering(
        self, pending_migrations: List[str]
    ) -> None:
        """Check for version conflicts or gaps."""
        sorted_versions = sorted(pending_migrations)
        for i, version in enumerate(sorted_versions):
            if i > 0:
                prev_version = sorted_versions[i - 1]
                if version <= prev_version:
                    raise MigrationValidationError(
                        f"Migration version ordering error: "
                        f"{prev_version} -> {version}"
                    )

    def _execute_single_migration(self, migration_version: str):
        """
        Execute a single migration.

        Args:
            migration_version: Version of migration to execute
        """
        start_time = datetime.now()

        try:
            # Get available migrations
            available_migrations = self._discover_migrations()

            if migration_version not in available_migrations:
                raise MigrationError(
                    f"Migration {migration_version} not found"
                )

            # Get migration class and create instance
            migration_class = available_migrations[migration_version]
            migration = migration_class()

            # Validate preconditions
            with self.db_manager.get_connection() as conn:
                precondition_result = migration.validate_preconditions(conn)
                if not precondition_result.success:
                    raise MigrationValidationError(
                        f"Preconditions failed for migration "
                        f"{migration_version}: {precondition_result.message}"
                    )

                # Create backup point
                backup_point = self.rollback_manager.create_rollback_point(
                    migration_version
                )

                # Execute the migration
                self.logger.info(f"Executing migration {migration_version}")
                migration.up(conn)

                # Validate postconditions
                postcondition_result = migration.validate_postconditions(conn)
                if not postcondition_result.success:
                    raise MigrationValidationError(
                        f"Postconditions failed for migration "
                        f"{migration_version}: {postcondition_result.message}"
                    )

                # Calculate execution time
                execution_time = (
                    datetime.now() - start_time
                ).total_seconds() * 1000

                # Record migration in history
                dependencies_json = str(migration.metadata.dependencies)
                checksum = migration.get_checksum()

                conn.execute(
                    """
                    INSERT INTO migration_history
                    (version, description, execution_time_ms, checksum,
                     dependencies, breaking_changes, backup_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        migration_version,
                        migration.metadata.description,
                        int(execution_time),
                        checksum,
                        dependencies_json,
                        migration.metadata.breaking_changes,
                        backup_point.backup_id if backup_point else None,
                    ),
                )

                # Record schema checksum
                self.validator.record_schema_checksum(migration_version)

                conn.commit()

                self.logger.info(
                    f"Successfully executed migration: {migration_version} "
                    f"({int(execution_time)}ms)"
                )

        except Exception as e:
            self.logger.error(
                f"Failed to execute migration {migration_version}: {e}"
            )
            # Attempt rollback on failure
            try:
                self.rollback_manager.execute_rollback(migration_version)
            except Exception as rollback_error:
                self.logger.error(
                    f"Rollback failed for migration {migration_version}: "
                    f"{rollback_error}"
                )
            raise
