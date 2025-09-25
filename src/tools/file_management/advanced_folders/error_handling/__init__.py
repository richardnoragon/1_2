"""
Error handling infrastructure for Advanced Folders feature.

This module provides centralized error handling, logging integration,
and graceful degradation capabilities.
"""

from .error_handler import (
    ErrorHandler,
    GracefulDegradation,
    get_degradation_manager,
    get_error_handler,
    handle_errors,
    safe_execute,
    with_fallback,
)

__all__ = [
    "ErrorHandler",
    "GracefulDegradation",
    "get_error_handler",
    "get_degradation_manager",
    "handle_errors",
    "safe_execute",
    "with_fallback",
]
