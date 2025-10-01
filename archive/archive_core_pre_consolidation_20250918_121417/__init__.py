"""
Core constants and configuration for Richard's File Utilities.
"""

from .constants import (
    APP_NAME,
    JSON_FILES_FILTER,
    IMPORT_ERROR,
    SECURITY_TEST,
    SUGGESTED_SOLUTIONS_HEADER,
)

# Import error handler now available in src/core
from .error_handler import error_handler

__all__ = [
    "APP_NAME",
    "JSON_FILES_FILTER",
    "IMPORT_ERROR",
    "SECURITY_TEST",
    "SUGGESTED_SOLUTIONS_HEADER",
    "error_handler",
]
