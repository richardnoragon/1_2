"""
Richard's File Utilities - Utilities Package

This package contains all the file utility tools organized by category:
- analysis: File analysis tools (checksum, duplicates, size analysis)
- file_management: File management tools (finder, catalog, rename, organize)
- file_operations: File manipulation tools
- metadata: Metadata editing tools
- network: Network connectivity tools
- pdf_tools: PDF manipulation tools
- privacy: Privacy and data cleaning tools
- security: Security and encryption tools
- system: System administration tools
"""

import sys
from pathlib import Path

__version__ = "3.0.0"
__author__ = "Richard's File Utilities"

# Ensure proper path resolution for submodules
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))


def safe_import(module_name, package_name=None):
    """Safely import a module with error handling."""
    try:
        if package_name:
            module_path = f".{module_name}"
            args = (module_path, globals(), locals(), [module_name], 1)
            return __import__(*args)
        else:
            return __import__(module_name)
    except ImportError as e:
        print(f"Warning: Could not import {module_name}: {e}")
        return None


# Import utility categories
analysis = safe_import("analysis", __name__)
file_management = safe_import("file_management", __name__)
file_operations = safe_import("file_operations", __name__)
metadata = safe_import("metadata", __name__)
network = safe_import("network", __name__)
pdf_tools = safe_import("pdf_tools", __name__)
privacy = safe_import("privacy", __name__)
security = safe_import("security", __name__)
system = safe_import("system", __name__)

__all__ = [
    "analysis",
    "file_management",
    "file_operations",
    "metadata",
    "network",
    "pdf_tools",
    "privacy",
    "security",
    "system"
]


def get_available_utilities():
    """Return information about available utility categories."""
    utilities = {}
    for util_name in __all__:
        util_module = globals().get(util_name)
        utilities[util_name] = {
            'available': util_module is not None,
            'module': util_module
        }
    return utilities


def validate_utilities():
    """Validate that all utility categories are properly loaded."""
    available = get_available_utilities()
    missing = [name for name, info in available.items()
               if not info['available']]
    
    if missing:
        print(f"Missing utility categories: {missing}")
        return False
    return True
