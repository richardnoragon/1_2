"""
src/core/guardian — ComponentGuardian package (spec §7.2 / P1-C03).

Public API re-exported here so callers can use shorter import paths:

    from src.core.guardian import ComponentGuardian, ComponentState
    from src.core.guardian import register_gui_component
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
