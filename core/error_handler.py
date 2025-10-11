"""Compatibility layer forwarding legacy ``core.error_handler`` imports."""

from src.core_rfu.error_handler import (  # noqa: F401
    ErrorHandler,
    error_handler,
    get_error_handler,
    handle_gui_error,
    safe_execute,
)

__all__ = [
    "ErrorHandler",
    "error_handler",
    "get_error_handler",
    "handle_gui_error",
    "safe_execute",
]
