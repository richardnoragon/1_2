"""
Synchronization and Backup Utilities Package

This package contains utilities for file synchronization and backup operations.
"""

# Package metadata
__version__ = "1.0.0"
__author__ = "Richard's File Utilities"
__description__ = "File synchronization and backup utilities"

# Import main classes for easy access
try:
    from .sync import SyncWindow, SyncWorker
    __all__ = ['SyncWindow', 'SyncWorker']
except ImportError:
    # Handle case where sync module is not yet available
    __all__ = []