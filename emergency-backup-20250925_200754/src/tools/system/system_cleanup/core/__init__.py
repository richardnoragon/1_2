"""
Core utilities for System Cleanup module.

This package contains the foundational classes and utilities used by all
system cleanup tools.
"""

from .cleanup_base import CleanupToolBase
from .windows_utils import WindowsUtils
from .safety_manager import SafetyManager
from .system_locations import SystemLocations

__all__ = [
    "CleanupToolBase",
    "WindowsUtils",
    "SafetyManager",
    "SystemLocations",
]
