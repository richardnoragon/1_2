"""
System Cleanup Module for Richard's File Utilities

This module provides comprehensive Windows system optimization and cleanup
capabilities, including registry cleaning, temporary file removal, cache
clearing, and system performance optimization.

Features:
- Registry Cleaner
- Delete Windows Log Data
- Clear Program Cache
- Delete Temp Files
- Delete Old Restore Points
- Delete Memory Access Logs
- Delete Program Downloads
- Clear Windows Cache
- Clear Windows History
- Delete Backup Files
- Remove Start Menu Shortcuts
- Remove "Last Used" Shortcuts
"""

__version__ = "1.0.0"
__author__ = "Richard's File Utilities"

from .core.cleanup_base import CleanupToolBase
from .core.windows_utils import WindowsUtils
from .core.safety_manager import SafetyManager

__all__ = [
    'CleanupToolBase',
    'WindowsUtils',
    'SafetyManager'
]