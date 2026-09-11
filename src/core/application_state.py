"""Shared application-state façade for hub-style entry points."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Optional

from .audit_trail import get_audit_trail


def _build_logger(logger_name: str) -> logging.Logger:
    try:
        from ..log_manager import get_log_manager

        log_manager = get_log_manager()
        if hasattr(log_manager, "get_logger"):
            return log_manager.get_logger(logger_name)
    except Exception:
        pass

    return logging.getLogger(logger_name)


def _build_config_manager() -> Any:
    try:
        from ..config_manager import get_config_manager

        return get_config_manager()
    except Exception:
        return None


def _build_preference_manager() -> Any:
    try:
        from .preferences.manager import PreferenceManager

        return PreferenceManager()
    except Exception:
        return None


@dataclass(frozen=True)
class ApplicationState:
    """Resolved services used by hub and launcher entry points."""

    logger: logging.Logger
    config_manager: Any = None
    preference_manager: Any = None
    audit_trail: Any = None
    database_available: bool = False


def build_application_state(
    logger_name: str,
    *,
    include_config: bool = True,
    include_preferences: bool = True,
    database_available: bool = False,
) -> ApplicationState:
    """Build a best-effort service bundle for a UI entry point."""

    return ApplicationState(
        logger=_build_logger(logger_name),
        config_manager=_build_config_manager() if include_config else None,
        preference_manager=(
            _build_preference_manager() if include_preferences else None
        ),
        audit_trail=get_audit_trail(),
        database_available=database_available,
    )