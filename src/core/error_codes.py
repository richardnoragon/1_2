"""Stable error codes and actionable messages shared by tools and the hub."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ErrorDefinition:
    code: str
    message: str
    retryable: bool = True


ERRORS = {
    "RFU-INPUT": ErrorDefinition("RFU-INPUT", "Check the input and try again."),
    "RFU-NOT-FOUND": ErrorDefinition("RFU-NOT-FOUND", "The item is no longer available. Choose another item and try again."),
    "RFU-PERMISSION": ErrorDefinition("RFU-PERMISSION", "Access was denied. Choose an accessible location or check your permissions."),
    "RFU-IO": ErrorDefinition("RFU-IO", "The operation could not access its files. Check the location and available space."),
    "RFU-UNAVAILABLE": ErrorDefinition("RFU-UNAVAILABLE", "This tool is unavailable. Check its installation or return to the hub."),
    "RFU-CANCELLED": ErrorDefinition("RFU-CANCELLED", "The operation was cancelled.", False),
    "RFU-INTERNAL": ErrorDefinition("RFU-INTERNAL", "The operation could not be completed. Try again or return to the hub."),
}
ALIASES = {
    "ValueError": "RFU-INPUT", "FileNotFoundError": "RFU-NOT-FOUND",
    "PermissionError": "RFU-PERMISSION", "OSError": "RFU-IO",
    "ImportError": "RFU-UNAVAILABLE", "ModuleNotFoundError": "RFU-UNAVAILABLE",
    "WorkflowCancelled": "RFU-CANCELLED",
}


def resolve_error(code_or_exception) -> ErrorDefinition:
    if isinstance(code_or_exception, BaseException):
        for cls in type(code_or_exception).__mro__:
            if cls.__name__ in ALIASES:
                return ERRORS[ALIASES[cls.__name__]]
        return ERRORS["RFU-INTERNAL"]
    code = ALIASES.get(code_or_exception, code_or_exception)
    return ERRORS.get(code, ERRORS["RFU-INTERNAL"])
