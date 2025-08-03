"""
Richard's File Utilities - Source Code Package

Main package for Richard's File Utilities containing all source code modules.
This package provides a comprehensive suite of file management and
analysis tools.
"""

import sys
from pathlib import Path

# Ensure the src directory is in the Python path
src_dir = Path(__file__).parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# Package metadata
__version__ = "3.0.0"
__author__ = "Richard's File Utilities"
__description__ = "Comprehensive file management and analysis utilities"


def safe_import_package(package_name):
    """Safely import a package with error handling."""
    try:
        return __import__(package_name, fromlist=[package_name])
    except ImportError as e:
        print(f"Warning: Could not import package {package_name}: {e}")
        return None


# Import main packages
utilities = safe_import_package("utilities")
rfu = safe_import_package("rfu")
legacy = safe_import_package("legacy")

__all__ = ["utilities", "rfu", "legacy"]


def get_package_info():
    """Return information about available packages."""
    return {
        'utilities': utilities is not None,
        'rfu': rfu is not None,
        'legacy': legacy is not None,
        'version': __version__,
        'description': __description__
    }