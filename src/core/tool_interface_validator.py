"""Utilities for validating tool window classes.

This module centralizes interface validation logic for RFU tools to ensure
consistent behavior across the application. Validation occurs both at
application runtime and within automated tests to prevent regressions.
"""

import importlib
import inspect
import logging
import pkgutil
from dataclasses import dataclass
from types import ModuleType
from typing import Iterable, List, Optional, Sequence, Tuple, Type

from PyQt5.QtWidgets import QMainWindow

logger = logging.getLogger(__name__)

REQUIRED_TOOL_ATTRIBUTES: Tuple[str, ...] = ("ensure_exit_action_reference",)


class ToolInterfaceError(RuntimeError):
    """Raised when a tool class fails interface validation."""

    def __init__(self, class_name: str, missing: Sequence[str]):
        message = (
            f"Tool class '{class_name}' is missing required attribute(s): "
            f"{', '.join(missing)}"
        )
        super().__init__(message)
        self.class_name = class_name
        self.missing = tuple(missing)


@dataclass
class ToolAuditIssue:
    """Represents a problem discovered during tool validation."""

    severity: str
    module_name: str
    class_name: Optional[str]
    message: str


def _issubclass_safe(candidate: Type[object], target: Type[object]) -> bool:
    """Safely determine subclass relationships."""

    try:
        return issubclass(candidate, target)
    except TypeError:
        return False


def _iter_tool_modules() -> Iterable[ModuleType]:
    """Yield tool modules discovered under ``src.tools``."""

    try:
        tools_pkg = importlib.import_module("src.tools")
    except ImportError as exc:  # pragma: no cover - configuration error
        logger.error("Failed to import tools package: %s", exc)
        raise

    namespace = getattr(tools_pkg, "__path__", None)
    if namespace is None:
        logger.warning("Tools package has no __path__; no modules to audit")
        return []

    for finder, name, ispkg in pkgutil.walk_packages(
        namespace, tools_pkg.__name__ + "."
    ):
        try:
            yield importlib.import_module(name)
        except Exception as exc:  # pragma: no cover - import errors reported
            logger.warning("Failed to import tool module %s: %s", name, exc)
            yield ToolImportErrorModule(name, exc)  # type: ignore[misc]


class ToolImportErrorModule(ModuleType):
    """Sentinel module representing an import failure."""

    def __init__(self, module_name: str, error: Exception):
        super().__init__(module_name)
        self.__import_error__ = error


def _iter_tool_classes(module: ModuleType) -> Iterable[Type[QMainWindow]]:
    """Yield concrete QMainWindow subclasses defined in *module*."""

    if hasattr(module, "__import_error__"):
        return []

    for _, cls in inspect.getmembers(module, inspect.isclass):
        if cls.__module__ != module.__name__:
            continue
        if not _issubclass_safe(cls, QMainWindow):
            continue
        if inspect.isabstract(cls):
            continue
        yield cls


def validate_tool_class(
    tool_class: Type[QMainWindow],
    required_attributes: Sequence[str] = REQUIRED_TOOL_ATTRIBUTES,
) -> None:
    """Validate a single tool class.

    Raises:
        ToolInterfaceError: If *tool_class* lacks required attributes.
    """

    missing = [attr for attr in required_attributes if not hasattr(tool_class, attr)]
    if missing:
        raise ToolInterfaceError(tool_class.__name__, missing)


def audit_tool_classes(
    required_attributes: Sequence[str] = REQUIRED_TOOL_ATTRIBUTES,
) -> List[ToolAuditIssue]:
    """Perform an audit of all tool classes.

    Returns a list of issues that should be investigated.
    An empty list indicates the audit succeeded.
    """

    issues: List[ToolAuditIssue] = []

    try:
        modules = list(_iter_tool_modules())
    except ImportError as exc:  # pragma: no cover - configuration error
        issues.append(
            ToolAuditIssue(
                severity="error",
                module_name="src.tools",
                class_name=None,
                message=f"Failed to import tools package: {exc}",
            )
        )
        return issues

    for module in modules:
        if hasattr(module, "__import_error__"):
            error: Exception = getattr(module, "__import_error__")
            issues.append(
                ToolAuditIssue(
                    severity="error",
                    module_name=module.__name__,
                    class_name=None,
                    message=f"Module import failed: {error}",
                )
            )
            continue

        for cls in _iter_tool_classes(module):
            missing = [attr for attr in required_attributes if not hasattr(cls, attr)]
            if missing:
                issues.append(
                    ToolAuditIssue(
                        severity="error",
                        module_name=module.__name__,
                        class_name=cls.__name__,
                        message="Missing attribute(s): " + ", ".join(missing),
                    )
                )

    return issues


__all__ = [
    "ToolInterfaceError",
    "ToolAuditIssue",
    "REQUIRED_TOOL_ATTRIBUTES",
    "audit_tool_classes",
    "validate_tool_class",
]
