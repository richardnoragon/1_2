"""Convenience exports for the Empty Folders analysis tool."""

from importlib import import_module

_import_error = None

try:
    _module = import_module(".empty_folders", package=__name__)
    EmptyFoldersGUI = getattr(_module, "EmptyFoldersGUI")
except Exception as exc:  # pragma: no cover - defensive guard
    _import_error = exc
    EmptyFoldersGUI = None


if EmptyFoldersGUI is None:  # pragma: no cover - only used when imports fail

    class EmptyFoldersGUI:
        """Placeholder that surfaces the original import error when instantiated."""

        def __init__(self, *args, **kwargs):
            raise ImportError(
                "The Empty Folders GUI could not be imported."
            ) from _import_error


__all__ = ["EmptyFoldersGUI"]
