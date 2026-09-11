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

_LAZY_EXPORTS = {
    "APP_NAME": ("src.core.constants", "APP_NAME"),
    "APP_ORGANIZATION": ("src.core.constants", "APP_ORGANIZATION"),
    "APP_VERSION": ("src.core.constants", "APP_VERSION"),
    "ErrorHandler": ("src.core.error_handler", "ErrorHandler"),
    "error_handler": ("src.core.error_handler", "error_handler"),
    "get_error_handler": ("src.core.error_handler", "get_error_handler"),
    "handle_gui_error": ("src.core.error_handler", "handle_gui_error"),
    "safe_execute": ("src.core.error_handler", "safe_execute"),
    "ObservabilityService": ("src.core.observability", "ObservabilityService"),
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
