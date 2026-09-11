"""Core functionality for Richard's File Utilities."""

import importlib
import sys

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
    "ApplicationState",
    "build_application_state",
    "AuditTrailService",
    "get_audit_trail",
    "LogManager",
    "ObservabilityService",
    "ToolLaunchRequest",
    "ToolRuntimeRecord",
    "ToolRuntimeTracker",
    "resolve_tool_class",
    "resolve_tool_launch_request",
]

_LAZY_EXPORTS = {
    "APP_NAME": (".constants", "APP_NAME"),
    "APP_ORGANIZATION": (".constants", "APP_ORGANIZATION"),
    "APP_TITLE": (".constants", "APP_TITLE"),
    "APP_VERSION": (".constants", "APP_VERSION"),
    "JSON_FILES_FILTER": (".constants", "JSON_FILES_FILTER"),
    "JSON_FILES_FILTER_SIMPLE": (".constants", "JSON_FILES_FILTER_SIMPLE"),
    "SUGGESTED_SOLUTIONS_HEADER": (".constants", "SUGGESTED_SOLUTIONS_HEADER"),
    "SUGGESTED_SOLUTIONS_HEADER_PLAIN": (
        ".constants",
        "SUGGESTED_SOLUTIONS_HEADER_PLAIN",
    ),
    "ErrorHandler": (".error_handler", "ErrorHandler"),
    "error_handler": (".error_handler", "error_handler"),
    "get_error_handler": (".error_handler", "get_error_handler"),
    "handle_gui_error": (".error_handler", "handle_gui_error"),
    "safe_execute": (".error_handler", "safe_execute"),
    "ApplicationState": (".application_state", "ApplicationState"),
    "build_application_state": (".application_state", "build_application_state"),
    "AuditTrailService": (".audit_trail", "AuditTrailService"),
    "get_audit_trail": (".audit_trail", "get_audit_trail"),
    "LogManager": (".logging_manager", "LogManager"),
    "ObservabilityService": (".observability", "ObservabilityService"),
    "ToolLaunchRequest": (".tool_lifecycle", "ToolLaunchRequest"),
    "ToolRuntimeRecord": (".tool_lifecycle", "ToolRuntimeRecord"),
    "ToolRuntimeTracker": (".tool_lifecycle", "ToolRuntimeTracker"),
    "resolve_tool_class": (".tool_lifecycle", "resolve_tool_class"),
    "resolve_tool_launch_request": (
        ".tool_lifecycle",
        "resolve_tool_launch_request",
    ),
}


def __getattr__(name: str):
    target = _LAZY_EXPORTS.get(name)
    if target is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    module_name, attribute_name = target
    module = importlib.import_module(module_name, package=__name__)
    value = getattr(module, attribute_name)
    globals()[name] = value
    return value


# Maintain module registration for fully qualified imports
module_ref = sys.modules[__name__]
sys.modules.setdefault("src.core", module_ref)
