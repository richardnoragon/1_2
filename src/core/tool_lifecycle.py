"""Shared tool lifecycle helpers for hub launch and registration flows."""

from __future__ import annotations

import importlib
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional, Type

from .audit_trail import AuditTrailService, get_audit_trail
from .tool_manifest import ToolManifestEntry, ToolManifestRegistry


@dataclass(frozen=True)
class ToolLaunchRequest:
    """Resolved request for launching a tool."""

    tool_name: str
    module_name: str
    class_name: str
    manifest: Optional[ToolManifestEntry] = None


@dataclass
class ToolRuntimeRecord:
    """Lifecycle snapshot for a registered tool instance."""

    tool_name: str
    tool_instance: Any
    status: str = "registered"
    last_activity: datetime = field(default_factory=datetime.now)
    progress: int = 0
    current_operation: Optional[str] = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "tool_class_name": type(self.tool_instance).__name__,
            "status": self.status,
            "last_activity": self.last_activity.isoformat(),
            "progress": self.progress,
            "current_operation": self.current_operation,
        }


def resolve_tool_launch_request(
    tool_name: str,
    module_name: Optional[str] = None,
    class_name: Optional[str] = None,
) -> Optional[ToolLaunchRequest]:
    """Resolve a launch request using explicit args or the manifest registry."""

    manifest = ToolManifestRegistry.lookup(tool_name)
    if manifest:
        return ToolLaunchRequest(
            tool_name=tool_name,
            module_name=manifest.module_path,
            class_name=manifest.class_name,
            manifest=manifest,
        )

    if module_name and class_name:
        return ToolLaunchRequest(
            tool_name=tool_name,
            module_name=module_name,
            class_name=class_name,
        )

    return None


def resolve_tool_class(
    module_name: str,
    class_name: str,
) -> Optional[Type[Any]]:
    """Import a tool class using the standard RFU import path strategy."""

    import_strategies = [
        lambda: _import_direct(module_name, class_name),
        lambda: _import_direct(
            module_name if module_name.startswith("src.") else f"src.{module_name}",
            class_name,
        ),
        lambda: _import_absolute(module_name, class_name),
    ]

    for strategy in import_strategies:
        try:
            tool_class = strategy()
            if tool_class:
                return tool_class
        except Exception:
            continue

    return None


def _import_direct(module_name: str, class_name: str) -> Optional[Type[Any]]:
    try:
        module = __import__(module_name, fromlist=[class_name])
        if hasattr(module, class_name):
            return getattr(module, class_name)
        return None
    except (ImportError, AttributeError):
        return None


def _import_absolute(module_name: str, class_name: str) -> Optional[Type[Any]]:
    try:
        module = importlib.import_module(module_name)
        if hasattr(module, class_name):
            return getattr(module, class_name)
        return None
    except (ImportError, AttributeError):
        return None


class ToolRuntimeTracker:
    """Instance-scoped lifecycle tracker for registered tool windows."""

    def __init__(
        self,
        logger: Optional[logging.Logger] = None,
        audit_trail: Optional[AuditTrailService] = None,
    ) -> None:
        self._logger = logger or logging.getLogger(__name__)
        self._audit_trail = audit_trail or get_audit_trail()
        self._records: dict[str, ToolRuntimeRecord] = {}

    def register(
        self,
        tool_name: str,
        tool_instance: Any,
        *,
        actor: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> ToolRuntimeRecord:
        record = self._records.get(tool_name)
        if record is None:
            record = ToolRuntimeRecord(tool_name=tool_name, tool_instance=tool_instance)
            self._records[tool_name] = record
        else:
            record.tool_instance = tool_instance
            record.status = "registered"
            record.last_activity = datetime.now()

        self._emit_audit_event(
            tool_name,
            operation="tool_registered",
            status="success",
            actor=actor,
            session_id=session_id,
            metadata={
                "class_name": type(tool_instance).__name__,
                **(metadata or {}),
            },
        )
        return record

    def unregister(
        self,
        tool_name: str,
        *,
        actor: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> Optional[ToolRuntimeRecord]:
        removed = self._records.pop(tool_name, None)
        if removed is not None:
            self._emit_audit_event(
                tool_name,
                operation="tool_unregistered",
                status="success",
                actor=actor,
                session_id=session_id,
                metadata=metadata,
            )
        return removed

    def update_progress(
        self,
        tool_name: str,
        percentage: int,
        message: str = "",
        *,
        actor: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> Optional[ToolRuntimeRecord]:
        record = self._records.get(tool_name)
        if record is None:
            return None

        record.progress = percentage
        record.current_operation = message
        record.last_activity = datetime.now()
        record.status = "complete" if percentage >= 100 else "in_progress"
        self._emit_audit_event(
            tool_name,
            operation="tool_progress_updated",
            status=record.status,
            actor=actor,
            session_id=session_id,
            metadata={
                "progress": percentage,
                "current_operation": message,
                **(metadata or {}),
            },
        )
        return record

    def snapshot(self, tool_name: str) -> Optional[dict[str, Any]]:
        record = self._records.get(tool_name)
        if record is None:
            return None
        return record.as_dict()

    def clear(self) -> None:
        self._records.clear()

    def _emit_audit_event(
        self,
        tool_name: str,
        *,
        operation: str,
        status: str,
        actor: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        manifest = ToolManifestRegistry.lookup(tool_name)
        category = manifest.category if manifest else "unknown"
        normalized_status = "success" if status in {"registered", "in_progress", "complete"} else status

        payload = {
            "category": category,
            "tool_id": manifest.tool_id if manifest else None,
        }
        if metadata:
            payload.update(metadata)

        if category in {"file_management", "file_operations", "metadata", "pdf"}:
            self._audit_trail.log_file_operation(
                operation,
                status=normalized_status,
                actor=actor,
                session_id=session_id,
                tool_name=tool_name,
                metadata=payload,
            )
            return

        if category in {"security", "privacy"}:
            self._audit_trail.log_security_operation(
                operation,
                status=normalized_status,
                actor=actor,
                session_id=session_id,
                tool_name=tool_name,
                metadata=payload,
            )
            return

        self._audit_trail.log_event(
            event_type="tool_operation",
            operation=operation,
            status=normalized_status,
            component=category,
            actor=actor,
            session_id=session_id,
            tool_name=tool_name,
            metadata=payload,
        )
