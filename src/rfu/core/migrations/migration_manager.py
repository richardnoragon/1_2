"""
Database Migration Manager - Central orchestrator for database migrations.

This module handles the execution of database migrations with comprehensive
error handling, rollback capabilities, and validation.
"""

import sqlite3
import logging
import threading
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path

from .migration_base import (
    MigrationBase, MigrationResult, MigrationStatus, ValidationResult,
    MigrationError, MigrationLockError, MigrationValidationError
)
from .rollback_manager import RollbackManager
from .schema_validator import SchemaValidator


class MigrationLockManager:
    """Manages migration locks to prevent concurrent migrations."""
    
    def __init__(self, database_manager):
        self.db_manager = database_manager
        self.logger = logging.getLogger('RFU.MigrationLockManager')
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
            rows_affected = self.db_manager.execute_update("""
                INSERT OR IGNORE INTO migration_locks 
                (id, locked_by, migration_version, process_id, expires_at)
                VALUES (1, ?, ?, ?, ?)
            """, (
                'migration_manager',
                migration_version,
                process_id,
                datetime.fromtimestamp(expires_at).isoformat()
            ))
            
            if rows_affected > 0:
                self.logger.info(f"Acquired migration lock for {migration_version}")
                return True
            
            # Check if existing lock has expired
            existing_lock = self.db_manager.execute_query("""
                SELECT expires_at FROM migration_locks WHERE id = 1
            """)
            
            if existing_lock:
                lock_expires = datetime.fromisoformat(existing_lock[0]['expires_at'])
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
            self.db_manager.execute_update("DELETE FROM migration_locks WHERE id = 1")
            self.logger.info("Released migration lock")
            return True
        except Exception as e:
            self.logger.error(f"Failed to release migration lock: {e}")
            return False
    
    def force_release_lock(self) -> bool:
        """Force release migration lock (for expired locks)."""
        try:
            self.db_manager.execute_update("DELETE FROM migration_locks WHERE id = 1")
            self.logger.warning("Force released migration lock")
            return True
        except Exception as e:
            self.logger.error(f"Failed to force release migration lock: {e}")
            return False
    
    def is_locked(self) -> bool:
        """Check if migration system is currently locked."""
        try:
            result = self.db_manager.execute_query("""
                SELECT expires_at FROM migration_locks WHERE id = 1
            """)
            
            if not result:
                return False
            
            lock_expires = datetime.fromisoformat(result[0]['expires_at'])
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
        self.logger = logging.getLogger('RFU.MigrationManager')
        self.rollback_manager = RollbackManager(database_manager)
        self.validator = SchemaValidator(database_manager)
        self.lock_manager = MigrationLockManager(database_manager)
        self._initialize_migration_tables()
    
    def _initialize_migration_tables(self):
        """Initialize migration tracking tables if they don't exist."""
        try:
            with self.db_manager.get_connection() as conn:
                # Migration history table
                conn.execute("""
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
                """)
                
                # Migration locks table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS migration_locks (
                        id INTEGER PRIMARY KEY CHECK (id = 1),
                        locked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        locked_by TEXT NOT NULL,
                        migration_version TEXT,
                        process_id TEXT,
                        expires_at TIMESTAMP
                    )
                """)
                
                # Migration backups table
                conn.execute("""
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
                """)
                
                # Schema checksums table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS schema_checksums (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        migration_version TEXT NOT NULL,
                        table_name TEXT NOT NULL,
                        schema_checksum TEXT NOT NULL,
                        data_checksum TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(migration_version, table_name)
                    )
                """)
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to initialize migration tables: {e}")
            raise
    
    def execute_migrations(self, target_version: Optional[str] = None) -> MigrationResult:
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
                raise MigrationLockError("Migration system is currently locked")
            
            # Acquire migration lock
            if not self.lock_manager.acquire_lock(target_version or "latest"):
                raise MigrationLockError("Could not acquire migration lock")
            
            try:
                # Get pending migrations
                pending_migrations = self._get_pending_migrations(target_version)
                
                if not pending_migrations:
                    return MigrationResult(
                        success=True,
                        version="no_migrations",
                        execution_time_ms=0
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
                
                execution_time = (datetime.now() - start_time).total_seconds() * 1000
                
                return MigrationResult(
                    success=True,
                    version=pending_migrations[-1] if pending_migrations else "none",
                    execution_time_ms=int(execution_time)
                )
                
            finally:
                # Always release lock
                self.lock_manager.release_lock()
                
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            self.logger.error(f"Migration execution failed: {e}")
            
            return MigrationResult(
                success=False,
                version="failed",
                execution_time_ms=int(execution_time),
                error=str(e)
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
                raise MigrationLockError("Migration system is currently locked")
            
            # Acquire migration lock
            if not self.lock_manager.acquire_lock(f"rollback_to_{target_version}"):
                raise MigrationLockError("Could not acquire migration lock for rollback")
            
            try:
                # Execute rollback
                rollback_result = self.rollback_manager.execute_rollback(target_version)
                
                execution_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if rollback_result.success:
                    return MigrationResult(
                        success=True,
                        version=target_version,
                        execution_time_ms=int(execution_time),
                        rollback_executed=True
                    )
                else:
                    return MigrationResult(
                        success=False,
                        version=target_version,
                        execution_time_ms=int(execution_time),
                        error=rollback_result.error,
                        rollback_executed=True
                    )
                
            finally:
                # Always release lock
                self.lock_manager.release_lock()
                
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            self.logger.error(f"Rollback execution failed: {e}")
            
            return MigrationResult(
                success=False,
                version=target_version,
                execution_time_ms=int(execution_time),
                error=str(e),
                rollback_executed=False
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
            applied_migrations = self.db_manager.execute_query("""
                SELECT version FROM migration_history 
                WHERE status = 'applied' 
                ORDER BY applied_at
            """)
            applied_versions = [m['version'] for m in applied_migrations]
            
            # Get pending migrations (would need migration discovery mechanism)
            pending_migrations = self._get_pending_migrations()
            
            # Get last migration date
            last_migration = self.db_manager.execute_query("""
                SELECT applied_at FROM migration_history 
                WHERE status = 'applied' 
                ORDER BY applied_at DESC 
                LIMIT 1
            """)
            last_migration_date = (
                last_migration[0]['applied_at'] if last_migration else None
            )
            
            # Check if system is locked
            database_locked = self.lock_manager.is_locked()
            
            return MigrationStatus(
                current_version=current_version,
                pending_migrations=pending_migrations,
                applied_migrations=applied_versions,
                last_migration_date=last_migration_date,
                database_locked=database_locked
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get migration status: {e}")
            return MigrationStatus(
                current_version="error",
                pending_migrations=[],
                applied_migrations=[],
                last_migration_date=None,
                database_locked=True
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
                success=True,
                message="All migration integrity checks passed"
            )
            
        except Exception as e:
            self.logger.error(f"Migration integrity validation failed: {e}")
            return ValidationResult(
                success=False,
                message=f"Integrity validation error: {e}"
            )
    
    def _get_current_version(self) -> str:
        """Get the current database migration version."""
        try:
            result = self.db_manager.execute_query("""
                SELECT version FROM migration_history 
                WHERE status = 'applied' 
                ORDER BY applied_at DESC 
                LIMIT 1
            """)
            
            if result:
                return result[0]['version']
            else:
                return "000"  # No migrations applied
        except Exception:
            return "000"
    
    def _get_pending_migrations(self, target_version: Optional[str] = None) -> List[str]:
        """
        Get list of pending migrations to execute.
        
        Args:
            target_version: Target version to migrate to
            
        Returns:
            List of migration versions to execute
        """
        # For now, return empty list - this would be populated by migration discovery
        # In a full implementation, this would scan for migration files
        return []
    
    def _execute_single_migration(self, migration_version: str):
        """
        Execute a single migration.
        
        Args:
            migration_version: Version of migration to execute
        """
        try:
            # This would load and execute the specific migration
            # For now, we'll just record it in the migration history
            self.db_manager.execute_update("""
                INSERT INTO migration_history 
                (version, description, execution_time_ms, checksum, dependencies)
                VALUES (?, ?, ?, ?, ?)
            """, (
                migration_version,
                f"Migration {migration_version}",
                1000,  # Placeholder execution time
                "checksum_placeholder",
                "[]"  # Empty dependencies
            ))
            
            # Record schema checksum
            self.validator.record_schema_checksum(migration_version)
            
            self.logger.info(f"Successfully executed migration: {migration_version}")
            
        except Exception as e:
            self.logger.error(f"Failed to execute migration {migration_version}: {e}")
            
            # Record failed migration
            self.db_manager.execute_update("""
                INSERT INTO migration_history 
                (version, description, execution_time_ms, checksum, status, error_message)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                migration_version,
                f"Migration {migration_version} (failed)",
                0,
                "checksum_placeholder",
                "failed",
                str(e)
            ))
            
            raise
