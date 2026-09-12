"""Richard's File Utilities - Source Code Package."""

import sys
from pathlib import Path
from typing import Any, Dict

# Ensure the src directory is discoverable
src_dir = Path(__file__).parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

__version__ = "3.0.0"
__author__ = "Richard's File Utilities"
__description__ = "Comprehensive file management and analysis utilities"


def safe_import_package(package_name: str):
    """Safely import a package with error handling."""
    try:
        return __import__(package_name, fromlist=[package_name])
    except ImportError as exc:  # pragma: no cover - optional packages
        print(f"Warning: Could not import package {package_name}: {exc}")
        return None


# Import main packages (only import existing packages)
rfu = safe_import_package("rfu")

_CORE_CONSTANTS_MODULE = "src.core.constants"
_CORE_ERROR_HANDLER_MODULE = "src.core.error_handler"
_CORE_OBSERVABILITY_MODULE = "src.core.observability"

_LAZY_EXPORTS = {
    "APP_NAME": (_CORE_CONSTANTS_MODULE, "APP_NAME"),
    "APP_ORGANIZATION": (_CORE_CONSTANTS_MODULE, "APP_ORGANIZATION"),
    "APP_VERSION": (_CORE_CONSTANTS_MODULE, "APP_VERSION"),
    "ErrorHandler": (_CORE_ERROR_HANDLER_MODULE, "ErrorHandler"),
    "error_handler": (_CORE_ERROR_HANDLER_MODULE, "error_handler"),
    "get_error_handler": (_CORE_ERROR_HANDLER_MODULE, "get_error_handler"),
    "handle_gui_error": (_CORE_ERROR_HANDLER_MODULE, "handle_gui_error"),
    "safe_execute": (_CORE_ERROR_HANDLER_MODULE, "safe_execute"),
    "ObservabilityService": (_CORE_OBSERVABILITY_MODULE, "ObservabilityService"),
}

__all__ = [
    "rfu",
    "APP_NAME",
    "APP_ORGANIZATION",
    "APP_VERSION",
    "ErrorHandler",
    "error_handler",
    "get_error_handler",
    "handle_gui_error",
    "safe_execute",
    "ObservabilityService",
]


def get_package_info() -> Dict[str, Any]:
    """Return information about available packages."""
    return {
        "rfu": rfu is not None,
        "version": __version__,
        "description": __description__,
    }


def __getattr__(name: str):
    """Resolve compatibility exports lazily to avoid heavy import side effects."""

    target = _LAZY_EXPORTS.get(name)
    if target is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    module_name, attribute_name = target
    module = __import__(module_name, fromlist=[attribute_name])
    value = getattr(module, attribute_name)
    globals()[name] = value
    return value
