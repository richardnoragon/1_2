"""Richard's File Utilities - Source Code Package."""

import importlib
import sys
from pathlib import Path
from typing import Any, Callable, Dict

# Ensure the src directory is discoverable
src_dir = Path(__file__).parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# Provide backward-compatible alias so `src.core` resolves to `core_rfu`
try:
    core_pkg = importlib.import_module("src.core_rfu")
    sys.modules.setdefault("src.core", core_pkg)
except Exception as exc:  # pragma: no cover - defensive fallback
    print(f"Warning: core consolidation alias failed: {exc}")

from src.core_rfu.constants import APP_NAME, APP_ORGANIZATION, APP_VERSION
from src.core_rfu.error_handler import (
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


# Import main packages
utilities = safe_import_package("utilities")
rfu = safe_import_package("rfu")
legacy = safe_import_package("legacy")

__all__ = [
    "utilities",
    "rfu",
    "legacy",
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
        "utilities": utilities is not None,
        "rfu": rfu is not None,
        "legacy": legacy is not None,
        "version": __version__,
        "description": __description__,
    }
