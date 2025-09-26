"""
Database Migration System for RFU Hub

This module provides a comprehensive database migration system with:
- Version tracking and dependency management
- Rollback capabilities with data preservation
- Migration validation and integrity checking
- Automated backup creation before migrations
- Comprehensive error handling and recovery
"""

from .migration_manager import DatabaseMigrationManager
from .migration_base import MigrationBase, MigrationMetadata
from .rollback_manager import RollbackManager
from .schema_validator import SchemaValidator

__all__ = [
    "DatabaseMigrationManager",
    "MigrationBase",
    "MigrationMetadata",
    "RollbackManager",
    "SchemaValidator",
]
