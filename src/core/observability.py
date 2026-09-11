"""Shared observability contract for errors, tool events, and operational telemetry."""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Mapping, Optional


@dataclass
class ObservabilityRecord:
    """Structured observability payload."""

    record_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: str = "event"
    component: str = "unknown"
    operation: str = "unknown"
    status: str = "info"
    message: str = ""
    tool_name: Optional[str] = None
    file_path: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    occurred_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "record_id": self.record_id,
            "type": self.type,
            "component": self.component,
            "operation": self.operation,
            "status": self.status,
            "message": self.message,
            "tool_name": self.tool_name,
            "file_path": self.file_path,
            "metadata": self.metadata,
            "occurred_at": self.occurred_at,
        }


class ObservabilityService:
    """Consolidated event emitter for GUI, service, and background diagnostics."""

    def __init__(self, logger: Optional[logging.Logger] = None, audit_trail: Optional[Any] = None):
        self.logger = logger or logging.getLogger("RFU.Observability")
        self.audit_trail = audit_trail

    def _emit(self, record: ObservabilityRecord) -> Dict[str, Any]:
        payload = record.to_dict()
        self.logger.log(self._level_for_status(record.status), "%s", payload)
        if self.audit_trail is not None and hasattr(self.audit_trail, "log_event"):
            self.audit_trail.log_event(
                event_type=record.type,
                operation=record.operation,
                status=record.status,
                component=record.component,
                resource=record.file_path,
                tool_name=record.tool_name,
                metadata=record.metadata,
            )
        return payload

    @staticmethod
    def _level_for_status(status: str) -> int:
        status_key = (status or "info").lower()
        if status_key in {"error", "failed", "failure", "denied"}:
            return logging.ERROR
        if status_key in {"warning", "warn", "partial"}:
            return logging.WARNING
        return logging.INFO

    def record_error(
        self,
        *,
        component: str,
        operation: str,
        message: str,
        exception: Optional[Exception] = None,
        metadata: Optional[Mapping[str, Any]] = None,
        tool_name: Optional[str] = None,
        file_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload = dict(metadata or {})
        if exception is not None:
            payload.setdefault("exception_type", type(exception).__name__)
            payload.setdefault("exception_message", str(exception))
        record = ObservabilityRecord(
            type="error",
            component=component,
            operation=operation,
            status="error",
            message=message,
            tool_name=tool_name,
            file_path=file_path,
            metadata=payload,
        )
        return self._emit(record)

    def record_warning(
        self,
        *,
        component: str,
        operation: str,
        message: str,
        metadata: Optional[Mapping[str, Any]] = None,
        tool_name: Optional[str] = None,
        file_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        record = ObservabilityRecord(
            type="warning",
            component=component,
            operation=operation,
            status="warning",
            message=message,
            tool_name=tool_name,
            file_path=file_path,
            metadata=dict(metadata or {}),
        )
        return self._emit(record)

    def record_info(
        self,
        *,
        component: str,
        operation: str,
        message: str,
        metadata: Optional[Mapping[str, Any]] = None,
        tool_name: Optional[str] = None,
        file_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        record = ObservabilityRecord(
            type="info",
            component=component,
            operation=operation,
            status="info",
            message=message,
            tool_name=tool_name,
            file_path=file_path,
            metadata=dict(metadata or {}),
        )
        return self._emit(record)

    def log_tool_event(
        self,
        tool_name: str,
        *,
        status: str,
        operation: str,
        details: str,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, Any]:
        record = ObservabilityRecord(
            type="tool_event",
            component="tool",
            operation=operation,
            status=status,
            message=details,
            tool_name=tool_name,
            metadata=dict(metadata or {}),
        )
        return self._emit(record)
