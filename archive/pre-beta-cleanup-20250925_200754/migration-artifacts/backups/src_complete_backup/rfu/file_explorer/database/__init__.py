"""
Database Package for RFU Multi-Pane File Explorer
Enterprise-Grade Database Schema and Migration System

This package provides comprehensive database support for the RFU File Explorer
with SQLite as the primary backend, featuring:

- Complete schema definitions for all explorer components
- Robust migration system with version control
- Transaction safety and rollback capabilities
- Performance optimization with proper indexing
- Cross-platform compatibility

Created: 2025-09-12
Version: 1.0.0 (Phase 1 Foundation)
"""

__version__ = "1.0.0"

from .migrations import DatabaseMigrator
from .schema import FileExplorerDatabase

__all__ = ['FileExplorerDatabase', 'DatabaseMigrator']
