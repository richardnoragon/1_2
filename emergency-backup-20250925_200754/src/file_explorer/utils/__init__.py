"""
Utils package for RFU Multi-Pane File Explorer
Enterprise-Grade Utility Modules

This package provides comprehensive utility modules for:

- Directory watching and filesystem monitoring
- File operations and management
- Search and indexing capabilities
- Thumbnail generation and caching
- Cross-platform compatibility helpers
- Performance monitoring and optimization

Author: RFU Development Team
Created: 2025-09-12
Version: 1.0.0 (Phase 1 Foundation)
"""

# Import main utility classes
try:
    from .directory_watcher import (
        DirectoryWatcher,
        EventDebouncer,
        EventFilter,
        EventPriority,
        FileSystemEventType,
        WatchEvent,
        create_directory_watcher,
    )
except ImportError:
    # Handle missing dependencies gracefully
    pass

try:
    from .file_operations import FileOperations
    from .search_engine import SearchEngine
    from .thumbnail_generator import ThumbnailGenerator
except ImportError:
    # Handle missing dependencies gracefully
    pass

__version__ = "1.0.0"
__author__ = "RFU Development Team"

# Module exports
__all__ = [
    "DirectoryWatcher",
    "create_directory_watcher",
    "EventFilter",
    "EventDebouncer",
    "WatchEvent",
    "FileSystemEventType",
    "EventPriority",
    "FileOperations",
    "ThumbnailGenerator",
    "SearchEngine",
]
