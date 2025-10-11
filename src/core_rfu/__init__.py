"""Core functionality for Richard's File Utilities."""

import importlib
import sys

from .constants import (
    APP_NAME,
    APP_ORGANIZATION,
    APP_TITLE,
    APP_VERSION,
    JSON_FILES_FILTER,
    JSON_FILES_FILTER_SIMPLE,
    SUGGESTED_SOLUTIONS_HEADER,
    SUGGESTED_SOLUTIONS_HEADER_PLAIN,
)
from .error_handler import (
    ErrorHandler,
    error_handler,
    get_error_handler,
    handle_gui_error,
    safe_execute,
)
from .logging_manager import LogManager

__all__ = [
    "APP_NAME",
    "APP_ORGANIZATION",
    "APP_TITLE",
    "APP_VERSION",
    "JSON_FILES_FILTER",
    "JSON_FILES_FILTER_SIMPLE",
    "SUGGESTED_SOLUTIONS_HEADER",
    "SUGGESTED_SOLUTIONS_HEADER_PLAIN",
    "ErrorHandler",
    "error_handler",
    "get_error_handler",
    "handle_gui_error",
    "safe_execute",
    "LogManager",
]

# Maintain backward compatibility so existing code can still import from src.core
if "src.core" not in sys.modules:
    sys.modules["src.core"] = importlib.import_module("src.core_rfu")
