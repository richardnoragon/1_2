"""Richard's File Utilities - Source Code Package."""

import sys
from pathlib import Path
from typing import Any, Dict

# Ensure the src directory is discoverable
src_dir = Path(__file__).parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from src.core.constants import (  # noqa: E402
    APP_NAME,
    APP_ORGANIZATION,
    APP_VERSION,
)
from src.core.error_handler import (  # noqa: E402
    ErrorHandler,
    error_handler,
    get_error_handler,
    handle_gui_error,
    safe_execute,
)

__version__ = APP_VERSION
__author__ = APP_ORGANIZATION
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
]


def get_package_info() -> Dict[str, Any]:
    """Return information about available packages."""
    return {
        "rfu": rfu is not None,
        "version": __version__,
        "description": __description__,
    }
