"""
Rollback Management System for Database Migrations.

This module handles database rollback operations with data preservation
and integrity verification, providing comprehensive recovery capabilities.
"""

import sqlite3
import logging
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from .migration_base import (
    RollbackResult, ValidationResult, MigrationError, RollbackError
)


class RollbackPoint:
    """Represents a rollback point in the migration history."""
    
    def __init__(self, version: str, backup_id: str, timestamp: datetime):
        self.version = version
        self.backup_id = backup_id
        self.timestamp = timestamp
        self.data_checksum = None
        self.schema_checksum = None


class RollbackPlan:
    """Execution plan for a rollback operation."""
    
    def __init__(self, target_version: str, current_version: str):
        self.target_version = target_version
        self.current_version = current_version
        self.migrations_to_rollback: List[str] = []
        self.estimated_duration_ms = 0
        self.data_loss_risk = False
        self.requires_backup = True


class MigrationBackupManager:
    """Manages migration backups with compression and integrity verification."""
    
    def __init__(self, database_manager):
        self.db_manager = database_manager
        self.logger = logging.getLogger('RFU.MigrationBackupManager')
        self.backup_dir = Path('data/migration_backups')
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def create_pre_migration_backup(self, migration_version: str) -> str:
        """
        Create backup before migration execution.
        
        Args:
            migration_version: Version of migration being executed
            
        Returns:
            Backup ID for the created backup
            
        Raises:
            Exception: If backup creation fails
        """
        try:
            backup_id = str(uuid.uuid4())
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"pre_migration_{migration_version}_{timestamp}_{backup_id[:8]}.db"
            backup_path = self.backup_dir / backup_filename
            
            # Create the backup by copying the database file
            import shutil
            db_file = Path(self.db_manager.db_file)
            if not db_file.exists():
                raise Exception("Database file does not exist")
            
            shutil.copy2(db_file, backup_path)
            
            if not backup_path.exists():
                raise Exception("Backup file was not created successfully")
            
            # Calculate checksum
            checksum = self._calculate_file_checksum(backup_path)
            file_size = backup_path.stat().st_size
            
            # Record backup in database
            self.db_manager.execute_update("""
                INSERT INTO migration_backups 
                (id, migration_version, backup_type, file_path, file_size_bytes, 
                 checksum, created_at, compression_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                backup_id,
                migration_version,
                'pre_migration',
                str(backup_path),
                file_size,
                checksum,
                datetime.now().isoformat(),
                'none'
            ))
            
            self.logger.info(f"Created pre-migration backup: {backup_id}")
            return backup_id
            
        except Exception as e:
            self.logger.error(f"Failed to create pre-migration backup: {e}")
            raise
    
    def create_rollback_backup(self, rollback_version: str) -> str:
        """
        Create backup before rollback execution.
        
        Args:
            rollback_version: Target version for rollback
            
        Returns:
            Backup ID for the created backup
        """
        try:
            backup_id = str(uuid.uuid4())
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"pre_rollback_{rollback_version}_{timestamp}_{backup_id[:8]}.db"
            backup_path = self.backup_dir / backup_filename
            
            # Create the backup
            if not self.db_manager.backup_database(str(backup_path)):
                raise Exception("Database backup failed")
            
            # Calculate checksum and file size
            checksum = self._calculate_file_checksum(backup_path)
            file_size = backup_path.stat().st_size
            
            # Record backup in database
            self.db_manager.execute_update("""
                INSERT INTO migration_backups 
                (id, migration_version, backup_type, file_path, file_size_bytes, 
                 checksum, created_at, compression_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                backup_id,
                rollback_version,
                'pre_rollback',
                str(backup_path),
                file_size,
                checksum,
                datetime.now().isoformat(),
                'none'
            ))
            
            self.logger.info(f"Created pre-rollback backup: {backup_id}")
            return backup_id
            
        except Exception as e:
            self.logger.error(f"Failed to create pre-rollback backup: {e}")
            raise
    
    def restore_from_backup(self, backup_id: str) -> bool:
        """
        Restore database from backup.
        
        Args:
            backup_id: ID of backup to restore
            
        Returns:
            True if restore was successful
        """
        try:
            # Get backup information
            backup_info = self.db_manager.execute_query("""
                SELECT file_path, checksum, file_size_bytes
                FROM migration_backups 
                WHERE id = ?
            """, (backup_id,))
            
            if not backup_info:
                raise Exception(f"Backup {backup_id} not found")
            
            backup_path = Path(backup_info[0]['file_path'])
            expected_checksum = backup_info[0]['checksum']
            
            # Verify backup file exists and integrity
            if not backup_path.exists():
                raise Exception(f"Backup file not found: {backup_path}")
            
            actual_checksum = self._calculate_file_checksum(backup_path)
            if actual_checksum != expected_checksum:
                raise Exception(f"Backup file integrity check failed")
            
            # Restore the database
            if not self.db_manager.restore_database(backup_path):
                raise Exception("Database restore failed")
            
            self.logger.info(f"Successfully restored from backup: {backup_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to restore from backup {backup_id}: {e}")
            return False
    
    def _calculate_file_checksum(self, file_path: Path) -> str:
        """Calculate SHA-256 checksum of a file."""
        import hashlib
        
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()


class RollbackManager:
    """
    Manages database rollback operations with data preservation
    and integrity verification.
    """
    
    def __init__(self, database_manager):
        self.db_manager = database_manager
        self.backup_manager = MigrationBackupManager(database_manager)
        self.logger = logging.getLogger('RFU.RollbackManager')
    
    def create_rollback_point(self, version: str) -> RollbackPoint:
        """
        Create a rollback point before migration execution.
        
        Args:
            version: Migration version
            
        Returns:
            RollbackPoint object
        """
        try:
            # Create backup
            backup_id = self.backup_manager.create_pre_migration_backup(version)
            
            # Create rollback point
            rollback_point = RollbackPoint(
                version=version,
                backup_id=backup_id,
                timestamp=datetime.now()
            )
            
            self.logger.info(f"Created rollback point for version {version}")
            return rollback_point
            
        except Exception as e:
            self.logger.error(f"Failed to create rollback point: {e}")
            raise
    
    def execute_rollback(self, target_version: str) -> RollbackResult:
        """
        Execute rollback to target version.
        
        Args:
            target_version: Target migration version
            
        Returns:
            RollbackResult with rollback outcome
        """
        start_time = datetime.now()
        rolled_back_migrations = []
        
        try:
            # Validate rollback safety
            validation_result = self.validate_rollback_safety(target_version)
            if not validation_result.success:
                raise RollbackError(
                    f"Rollback validation failed: {validation_result.message}",
                    target_version
                )
            
            # Get rollback plan
            rollback_plan = self.get_rollback_plan(target_version)
            
            # Create backup before rollback
            backup_id = self.backup_manager.create_rollback_backup(target_version)
            
            # Execute rollback for each migration
            current_version = self._get_current_version()
            
            # Get migrations to rollback in reverse order
            migrations_to_rollback = self._get_migrations_to_rollback(
                current_version, target_version
            )
            
            for migration_version in reversed(migrations_to_rollback):
                try:
                    self._rollback_single_migration(migration_version)
                    rolled_back_migrations.append(migration_version)
                    self.logger.info(f"Rolled back migration: {migration_version}")
                except Exception as e:
                    self.logger.error(f"Failed to rollback migration {migration_version}: {e}")
                    # Attempt emergency restore
                    if self.backup_manager.restore_from_backup(backup_id):
                        raise RollbackError(
                            f"Rollback failed at {migration_version}, restored from backup",
                            target_version, e
                        )
                    else:
                        raise RollbackError(
                            f"Rollback failed at {migration_version}, backup restore also failed",
                            target_version, e
                        )
            
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return RollbackResult(
                success=True,
                target_version=target_version,
                migrations_rolled_back=rolled_back_migrations,
                execution_time_ms=int(execution_time),
                backup_restored=False
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return RollbackResult(
                success=False,
                target_version=target_version,
                migrations_rolled_back=rolled_back_migrations,
                execution_time_ms=int(execution_time),
                error=str(e)
            )
    
    def validate_rollback_safety(self, target_version: str) -> ValidationResult:
        """
        Validate that rollback can be safely performed.
        
        Args:
            target_version: Target migration version
            
        Returns:
            ValidationResult indicating if rollback is safe
        """
        try:
            # Check if target version exists in migration history
            applied_migrations = self.db_manager.execute_query("""
                SELECT version FROM migration_history 
                WHERE status = 'applied' 
                ORDER BY applied_at
            """)
            
            applied_versions = [m['version'] for m in applied_migrations]
            
            if target_version not in applied_versions:
                return ValidationResult(
                    success=False,
                    message=f"Target version {target_version} was never applied"
                )
            
            # Check if any migrations have rollback_supported = False
            current_version = self._get_current_version()
            migrations_to_check = self._get_migrations_to_rollback(
                current_version, target_version
            )
            
            for version in migrations_to_check:
                # Check if migration supports rollback
                migration_info = self.db_manager.execute_query("""
                    SELECT breaking_changes FROM migration_history 
                    WHERE version = ?
                """, (version,))
                
                if migration_info and migration_info[0].get('breaking_changes'):
                    return ValidationResult(
                        success=False,
                        message=f"Migration {version} has breaking changes and may not support safe rollback"
                    )
            
            return ValidationResult(
                success=True,
                message="Rollback can be safely performed"
            )
            
        except Exception as e:
            return ValidationResult(
                success=False,
                message=f"Rollback safety validation failed: {e}"
            )
    
    def get_rollback_plan(self, target_version: str) -> RollbackPlan:
        """
        Generate rollback execution plan.
        
        Args:
            target_version: Target migration version
            
        Returns:
            RollbackPlan with execution details
        """
        current_version = self._get_current_version()
        plan = RollbackPlan(target_version, current_version)
        
        # Get migrations to rollback
        plan.migrations_to_rollback = self._get_migrations_to_rollback(
            current_version, target_version
        )
        
        # Estimate duration based on migration complexities
        plan.estimated_duration_ms = len(plan.migrations_to_rollback) * 5000  # 5 seconds per migration
        
        # Check for data loss risk
        plan.data_loss_risk = any(
            self._migration_has_data_loss_risk(version) 
            for version in plan.migrations_to_rollback
        )
        
        return plan
    
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
    
    def _get_migrations_to_rollback(self, current_version: str, 
                                   target_version: str) -> List[str]:
        """Get list of migrations that need to be rolled back."""
        try:
            # Get all applied migrations between target and current
            result = self.db_manager.execute_query("""
                SELECT version FROM migration_history 
                WHERE status = 'applied' 
                AND version > ? 
                AND version <= ?
                ORDER BY applied_at ASC
            """, (target_version, current_version))
            
            return [m['version'] for m in result]
        except Exception:
            return []
    
    def _rollback_single_migration(self, migration_version: str):
        """Rollback a single migration."""
        # This would load and execute the specific migration's down() method
        # For now, we'll update the migration history
        self.db_manager.execute_update("""
            UPDATE migration_history 
            SET status = 'rolled_back' 
            WHERE version = ?
        """, (migration_version,))
    
    def _migration_has_data_loss_risk(self, version: str) -> bool:
        """Check if a migration rollback has data loss risk."""
        try:
            result = self.db_manager.execute_query("""
                SELECT breaking_changes FROM migration_history 
                WHERE version = ?
            """, (version,))
            
            return result and result[0].get('breaking_changes', False)
        except Exception:
            return True  # Assume risk if we can't determine
