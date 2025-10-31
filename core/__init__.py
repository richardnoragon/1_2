"""Compatibility package mapping legacy ``core`` imports to ``src.core``.

This module keeps legacy import paths working after the core modules were
consolidated under ``src.core``. It mirrors the canonical package so existing
code can continue using ``import core`` style imports without modification.
"""

from __future__ import annotations

import importlib
import sys
from types import ModuleType
from typing import Any

_core_pkg = importlib.import_module("src.core")

# Share the submodule search locations so ``core.*`` resolves to the
# consolidated implementation under ``src.core``.
__path__ = list(getattr(_core_pkg, "__path__", []))

# Expose public attributes from the consolidated package.
if hasattr(_core_pkg, "__all__"):
    for _name in _core_pkg.__all__:
        globals()[_name] = getattr(_core_pkg, _name)


def __getattr__(name: str) -> Any:
    """Delegate attribute access to ``src.core``."""
    return getattr(_core_pkg, name)


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(dir(_core_pkg)))


def _ensure_submodule(name: str) -> ModuleType:
    """Load and cache a core submodule from the consolidated package."""
    full_name = f"{__name__}.{name}"
    if full_name in sys.modules:
        return sys.modules[full_name]  # pragma: no cover

    target = importlib.import_module(f"src.core.{name}")
    sys.modules[full_name] = target
    return target


def __getattr_submodule(name: str) -> ModuleType:
    return _ensure_submodule(name)


# Register a finder so ``import core.foo`` transparently resolves to
# ``src.core.foo``. Python automatically handles this via ``__path__``
# for actual files, but we also eagerly cache known modules used by the suite.
for _submodule in [
    "config_manager",
    "constants",
    "database_logging",
    "database_manager",
    "database_models",
    "logging_manager",
    "log_manager",
    "error_handler",
]:
    try:
        _ensure_submodule(_submodule)
    except ModuleNotFoundError:
        continue
