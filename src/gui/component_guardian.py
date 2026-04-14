"""
src/gui/component_guardian.py — backward-compatibility shim (P1-C05).

The canonical implementation lives at src/core/guardian/component_guardian.py.
This file re-exports all public names so that any existing code importing
from this path continues to work without modification.

DO NOT add new code here.  Update callers to import from
``src.core.guardian.component_guardian`` or ``src.core.guardian`` directly.
"""

from src.core.guardian.component_guardian import (  # noqa: F401
    ComponentDegradationError,
    ComponentError,
    ComponentGuardian,
    ComponentInfo,
    ComponentRecoveryError,
    ComponentState,
    get_component_guardian,
    protected_gui_operation,
    register_gui_component,
)

__all__ = [
    "ComponentDegradationError",
    "ComponentError",
    "ComponentGuardian",
    "ComponentInfo",
    "ComponentRecoveryError",
    "ComponentState",
    "get_component_guardian",
    "protected_gui_operation",
    "register_gui_component",
]
