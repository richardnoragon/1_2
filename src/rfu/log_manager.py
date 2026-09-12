"""Compatibility wrapper for the legacy `rfu.log_manager` import contract."""

from __future__ import annotations

from src.log_manager import (
    CustomRotatingFileHandler,
    LogManager,
    get_log_manager,
    get_log_manager_instance,
)

__all__ = [
    "LogManager",
    "get_log_manager",
    "get_log_manager_instance",
    "CustomRotatingFileHandler",
]
