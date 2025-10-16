"""Process monitor tool package."""

from importlib import import_module
from typing import TYPE_CHECKING, Any

__all__ = ["ProcessMonitorGUI", "ProcessMonitorWorker", "main"]


def __getattr__(name: str) -> Any:
    if name in __all__:
        module = import_module(".process_monitor", __name__)
        return getattr(module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


if TYPE_CHECKING:  # pragma: no cover - help static analyzers
    from .process_monitor import (
        ProcessMonitorGUI,
        ProcessMonitorWorker,
        main,
    )
