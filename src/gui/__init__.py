"""GUI components for Richard's File Utilities."""

try:
    from ..core.error_handler import error_handler
except ImportError:  # pragma: no cover - optional GUI runtime not installed
    error_handler = None
