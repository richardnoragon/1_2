"""Compatibility namespace for legacy src.tools.advanced_folders imports.

The Advanced Folders implementation was moved under
`src.tools.file_management.advanced_folders`. This namespace preserves legacy
imports used by older tests and modules.
"""

from importlib import import_module
from pathlib import Path

_TARGET = (
    Path(__file__).resolve().parent.parent / "file_management" / "advanced_folders"
).resolve()
__path__ = [str(_TARGET)]


def __getattr__(name: str):
    """Lazily resolve legacy package attributes to real submodules."""
    if name in {"core", "database", "gui", "integration", "models", "repository", "validation"}:
        module = import_module(f"{__name__}.{name}")
        globals()[name] = module
        return module
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


__all__ = ["core", "database", "gui", "integration", "models", "repository", "validation"]
