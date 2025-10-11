"""
File Operations Utilities

This package contains utilities for file operations including:
- File management (catalog, finder, organize, rename)
- File operations (copy, move, sync, delete, compress, split/join)
- File touch utilities
- Synchronization and backup tools
"""

# Import warnings for optional imports
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
    from .file_touch import *
except ImportError as e:
    warnings.warn(f"Could not import file_touch: {e}")

try:
    from .cmsd import *
except ImportError as e:
    warnings.warn(f"Could not import cmsd: {e}")

try:
    from .compression import *
except ImportError as e:
    warnings.warn(f"Could not import compression: {e}")

try:
    from .file_splitter import *
except ImportError as e:
    warnings.warn(f"Could not import file_splitter: {e}")

try:
    from .synchronization_backup import *
except ImportError as e:
    warnings.warn(f"Could not import synchronization_backup: {e}")

try:
    from .enhanced_editor import EnhancedEditor  # noqa: F401

    __all__.append("EnhancedEditor")
except ImportError as e:
    warnings.warn(f"Could not import enhanced_editor: {e}")
