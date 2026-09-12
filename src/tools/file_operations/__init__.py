"""
File Operations Utilities

This package contains utilities for file operations including:
- File management (catalog, finder, organize, rename)
- File operations (copy, move, sync, delete, compress, split/join)
- Synchronization and backup tools
"""

# Import warnings for optional imports
import os
import warnings

__all__ = []

# Core file operations
try:
    from .catalog import *
except ImportError as e:
    warnings.warn(f"Could not import catalog: {e}")

try:
    from .file_finder import *
except ImportError as e:
    warnings.warn(f"Could not import file_finder: {e}")

try:
    from .organize import *
except ImportError as e:
    warnings.warn(f"Could not import organize: {e}")

try:
    from .rename import *
except ImportError as e:
    warnings.warn(f"Could not import rename: {e}")

try:
    from .compression import *
except ImportError as e:
    warnings.warn(f"Could not import compression: {e}")

try:
    from .file_splitter import *
except ImportError as e:
    warnings.warn(f"Could not import file_splitter: {e}")

try:
    from . import file_splitter_logic  # noqa: F401
    __all__.append("file_splitter_logic")
except ImportError as e:
    warnings.warn(f"Could not import file_splitter_logic: {e}")

if os.environ.get("RFU_SKIP_ENHANCED_EDITOR_IMPORT", "0") != "1":
    try:
        from .enhanced_editor import EnhancedEditor  # noqa: F401

        __all__.append("EnhancedEditor")
    except ImportError as e:
        warnings.warn(f"Could not import enhanced_editor: {e}")
