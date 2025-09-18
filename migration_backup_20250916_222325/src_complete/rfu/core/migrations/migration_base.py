"""
Base classes and interfaces for database migrations.

This module defines the abstract base class and data structures
for implementing database migrations with validation and rollback support.
"""

import sqlite3
import hashlib
import inspect
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum


class CorruptionType(Enum):
    """Types of data corruption that can be detected."""
    TRUNCATED = "truncated"
    INVALID_CHARACTERS = "invalid_characters"
    MISSING_FIELDS = "missing_fields"
    INVALID_TYPES = "invalid_types"
    CHECKSUM_MISMATCH = "checksum_mismatch"
    UNKNOWN = "unknown"


class RecoveryStrategy(Enum):
    """Recovery strategies for different corruption scenarios."""
    BACKUP_RESTORE = "backup_restore"
    DATA_SANITIZATION = "data_sanitization"
    FIELD_RECONSTRUCTION = "field_reconstruction"
    TYPE_CORRECTION = "type_correction"
    FULL_BACKUP_RESTORE = "full_backup_restore"
    DEFAULT_FALLBACK = "default_fallback"


@dataclass
class MigrationMetadata:
    """Metadata for a database migration."""
    version: str
    description: str
    dependencies: List[str]
    estimated_duration_ms: int
    breaking_changes: bool
    rollback_supported: bool


@dataclass
class ValidationResult:
    """Result of a migration validation operation."""
    success: bool
    message: str
    corruption_type: Optional[CorruptionType] = None
    details: Optional[Dict[str, Any]] = None


@dataclass
class MigrationResult:
    """Result of a migration execution."""
    success: bool
    version: str
    execution_time_ms: int
    backup_id: Optional[str] = None
    error: Optional[str] = None
    rollback_executed: bool = False


@dataclass
class RollbackResult:
    """Result of a rollback operation."""
    success: bool
    target_version: str
    migrations_rolled_back: List[str]
    execution_time_ms: int
    backup_restored: bool = False
    error: Optional[str] = None


@dataclass
class MigrationStatus:
    """Current migration status information."""
    current_version: str
    pending_migrations: List[str]
    applied_migrations: List[str]
    last_migration_date: Optional[str]
    database_locked: bool


class MigrationBase(ABC):
    """
    Abstract base class for all database migrations.
    
    Provides structure and validation for migration scripts with
    comprehensive error handling and rollback support.
    """
    
    @property
    @abstractmethod
    def metadata(self) -> MigrationMetadata:
        """Migration metadata including version, dependencies, etc."""
        pass
    
    @abstractmethod
    def up(self, connection: sqlite3.Connection) -> None:
        """
        Execute forward migration.
        
        Args:
            connection: SQLite database connection
            
        Raises:
            Exception: If migration fails
        """
        pass
    
    @abstractmethod
    def down(self, connection: sqlite3.Connection) -> None:
        """
        Execute rollback migration.
        
        Args:
            connection: SQLite database connection
            
        Raises:
            Exception: If rollback fails
        """
        pass
    
    @abstractmethod
    def validate_preconditions(self, connection: sqlite3.Connection) -> ValidationResult:
        """
        Validate that migration can be safely executed.
        
        Args:
            connection: SQLite database connection
            
        Returns:
            ValidationResult indicating if migration can proceed
        """
        pass
    
    @abstractmethod
    def validate_postconditions(self, connection: sqlite3.Connection) -> ValidationResult:
        """
        Validate that migration was executed successfully.
        
        Args:
            connection: SQLite database connection
            
        Returns:
            ValidationResult indicating if migration succeeded
        """
        pass
    
    def get_checksum(self) -> str:
        """
        Generate cryptographically secure checksum for migration integrity.
        
        Uses SHA-256 with proper content normalization and salt for security.
        
        Returns:
            SHA-256 checksum of migration content with salt
        """
        try:
            # Get the source code of the migration methods with normalization
            up_source = inspect.getsource(self.up).strip()
            down_source = inspect.getsource(self.down).strip()
            
            # Normalize metadata for consistent hashing
            metadata_dict = {
                'version': self.metadata.version,
                'description': self.metadata.description,
                'dependencies': sorted(
                    self.metadata.dependencies
                ),  # Sort for consistency
                'estimated_duration_ms': self.metadata.estimated_duration_ms,
                'breaking_changes': self.metadata.breaking_changes,
                'rollback_supported': self.metadata.rollback_supported
            }
            
            # Convert to normalized JSON string
            import json
            metadata_str = json.dumps(
                metadata_dict, sort_keys=True, separators=(',', ':')
            )
            
            # Create deterministic salt from class name and version
            class_identifier = (
                f"{self.__class__.__module__}.{self.__class__.__name__}"
            )
            salt_input = f"{class_identifier}:{self.metadata.version}"
            salt = hashlib.sha256(salt_input.encode('utf-8')).digest()
            
            # Combine all content with proper separation
            content_parts = [
                b"UP_METHOD:",
                up_source.encode('utf-8'),
                b"DOWN_METHOD:",
                down_source.encode('utf-8'),
                b"METADATA:",
                metadata_str.encode('utf-8'),
                b"SALT:",
                salt
            ]
            
            # Generate cryptographically secure checksum
            hasher = hashlib.sha256()
            for part in content_parts:
                hasher.update(part)
            
            return hasher.hexdigest()
            
        except Exception:
            # Fallback to basic checksum if inspection fails
            class_name = self.__class__.__name__
            version = self.metadata.version
            fallback_content = f"{class_name}:{version}"
            return hashlib.sha256(fallback_content.encode('utf-8')).hexdigest()
    
    def get_migration_info(self) -> Dict[str, Any]:
        """
        Get comprehensive migration information.
        
        Returns:
            Dictionary with migration details
        """
        return {
            'version': self.metadata.version,
            'description': self.metadata.description,
            'dependencies': self.metadata.dependencies,
            'estimated_duration_ms': self.metadata.estimated_duration_ms,
            'breaking_changes': self.metadata.breaking_changes,
            'rollback_supported': self.metadata.rollback_supported,
            'checksum': self.get_checksum(),
            'class_name': self.__class__.__name__
        }
    
    def validate_dependencies(
        self, applied_migrations: List[str]
    ) -> ValidationResult:
        """
        Validate that all dependencies are satisfied.
        
        Args:
            applied_migrations: List of already applied migration versions
            
        Returns:
            ValidationResult indicating if dependencies are satisfied
        """
        missing_deps = []
        
        for dependency in self.metadata.dependencies:
            if dependency not in applied_migrations:
                missing_deps.append(dependency)
        
        if missing_deps:
            return ValidationResult(
                success=False,
                message=f"Missing dependencies: {missing_deps}",
                details={'missing_dependencies': missing_deps}
            )
        
        return ValidationResult(
            success=True,
            message="All dependencies satisfied"
        )


class MigrationError(Exception):
    """Base exception for migration errors."""
    
    def __init__(self, message: str, migration_version: Optional[str] = None,
                 original_error: Optional[Exception] = None):
        super().__init__(message)
        self.migration_version = migration_version
        self.original_error = original_error


class MigrationValidationError(MigrationError):
    """Raised when migration validation fails."""
    pass


class RollbackError(MigrationError):
    """Raised when rollback operation fails."""
    pass


class MigrationLockError(MigrationError):
    """Raised when migration lock cannot be acquired."""
    pass


class MigrationDependencyError(MigrationError):
    """Raised when migration dependencies are not satisfied."""
    pass
