"""
CMSD GUI Module

This module provides a GUI wrapper for the CMSD (Copy/Move/Sync/Delete) logic,
maintaining compatibility with the tools interface while using
the enhanced utilities logic.
"""

from .gui import CopyMoveSyncDeleteWindow

__all__ = ["CopyMoveSyncDeleteWindow"]
