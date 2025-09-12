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

# Import the SystemCleanupGUI from the parent module
try:
    import sys
    import os
    import importlib.util
    
    # Get the path to the parent system_cleanup.py file
    current_dir = os.path.dirname(__file__)
    parent_file = os.path.join(os.path.dirname(current_dir), 'system_cleanup.py')
    
    if os.path.exists(parent_file):
        # Load the module directly from file
        spec = importlib.util.spec_from_file_location("system_cleanup_module", parent_file)
        system_cleanup_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(system_cleanup_module)
        
        # Get the SystemCleanupGUI class
        SystemCleanupGUI = getattr(system_cleanup_module, 'SystemCleanupGUI', None)
        SYSTEM_CLEANUP_GUI_AVAILABLE = SystemCleanupGUI is not None
    else:
        SystemCleanupGUI = None
        SYSTEM_CLEANUP_GUI_AVAILABLE = False
        
except Exception as e:
    SystemCleanupGUI = None
    SYSTEM_CLEANUP_GUI_AVAILABLE = False
    print(f"Warning: Could not import SystemCleanupGUI: {e}")

__all__ = [
    'CleanupToolBase',
    'WindowsUtils',
    'SafetyManager',
    'SystemCleanupGUI'
]