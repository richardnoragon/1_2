"""
Standardized Test Environment Configuration
Generated: 2025-09-08
Purpose: Provide consistent Python path and dependency configuration for all tests

This configuration addresses import system issues by standardizing:
- Python path configuration
- Module resolution
- Dependency management
"""

import os
import sys
from pathlib import Path

# Workspace configuration
WORKSPACE_ROOT = Path(r"C:\Users\HP1\1_2")

# Python paths (in order of priority)
PYTHON_PATHS = [
    r"C:\Users\HP1\1_2\src",
    r"C:\Users\HP1\1_2",
    r"C:\Users\HP1\1_2\tests\unit",
]

# Available modules
AVAILABLE_MODULES = [
    "PIL",
    "PyQt5",
    "PyQt5.QtCore",
    "PyQt5.QtWidgets",
    "camelot",
    "cv2",
    "fitz",
    "logging",
    "pathlib",
    "psutil",
    "pytesseract",
    "pytest",
    "socket",
    "tempfile",
    "tkinter",
    "unittest.mock",
    "urllib",
]

# Missing modules
MISSING_MODULES = [
    "pytest-cov",
    "pytest-html",
    "pytest-json-report",
    "requests",
]


def setup_test_environment():
    """Setup standardized test environment."""
    # Add Python paths
    for path in PYTHON_PATHS:
        abs_path = str(Path(path).resolve())
        if abs_path not in sys.path:
            sys.path.insert(0, abs_path)
    
    # Set environment variables
    os.environ['PYTHONPATH'] = os.pathsep.join(PYTHON_PATHS)
    os.environ['TEST_WORKSPACE_ROOT'] = str(WORKSPACE_ROOT)
    
    return {
        'workspace_root': WORKSPACE_ROOT,
        'python_paths': PYTHON_PATHS,
        'available_modules': AVAILABLE_MODULES,
        'missing_modules': MISSING_MODULES
    }


def get_module_import_path(module_name: str) -> str:
    """Get the correct import path for a module.
    
    Args:
        module_name: Name of the module to import
        
    Returns:
        Corrected import path or original name if not found
    """
    # Module path corrections for common import issues
    path_corrections = {
        'rfu.dev_hub': 'dev_hub',
        'utilities.system.system_cleanup': 'system_cleanup',
        'utilities.network.network_connectivity': 'network_connectivity',
        'utilities.privacy.error_recovery': 'error_recovery',
        'rfu.log_manager': 'log_manager',
        'utilities.core.config_manager': 'config_manager'
    }
    
    return path_corrections.get(module_name, module_name)


if __name__ == '__main__':
    # Auto-setup when imported or run directly
    setup_test_environment()
