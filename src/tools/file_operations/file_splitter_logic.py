"""Compatibility wrapper for the file splitter logic module.

This keeps the historical import contract
``src.tools.file_operations.file_splitter_logic`` working while the package
implementation lives under ``src/tools/file_operations/file_splitter/``.
"""

from .file_splitter.file_splitter_logic import *  # noqa: F401,F403

# Re-export the package's canonical module path for compatibility imports.
from .file_splitter import file_splitter_logic as _canonical_module

__all__ = getattr(_canonical_module, "__all__", []) or [
    "FileSplitterError",
    "FileSplitterValidationError",
    "FileSplitterIOError",
    "FileSplitterSecurityError",
    "FileSplitterLogic",
    "_validate_and_sanitize_path",
    "_is_safe_path",
    "_create_secure_temp_dir",
]
