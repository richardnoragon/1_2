"""Centralized audit trail service for security-sensitive operations.

The audit trail emits structured records through the RFU logging stack with a
consistent event schema and conservative metadata redaction.
"""

from __future__ import annotations

import logging
import os
import re
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

SENSITIVE_KEY_PATTERN = re.compile(
    r"password|passphrase|secret|token|api[_-]?key|private[_-]?key|credential|cookie|authorization|auth",
    re.IGNORECASE,
)


@dataclass
class AuditEvent:
    """Canonical audit event payload."""

    event_id: str
    event_type: str
    status: str
    occurred_at: str
    component: str
    operation: str
    actor: Optional[str] = None
    resource: Optional[str] = None
    tool_name: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AuditTrailService:
    """Centralized audit logger with best-effort redaction."""

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger("RFU.AuditTrail")
        self.session_id = os.getenv("RFU_AUDIT_SESSION_ID") or str(uuid.uuid4())
        self._default_actor: Optional[str] = None
        self._default_session_id: Optional[str] = None

    def set_context(
        self,
        *,
        actor: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> None:
        """Set default actor/session values for subsequent audit events."""

        if actor is not None:
            self._default_actor = actor
        if session_id is not None:
            self._default_session_id = session_id

    def clear_context(self) -> None:
        """Clear default actor/session values."""

        self._default_actor = None
        self._default_session_id = None

    def log_event(
        self,
        *,
        event_type: str,
        operation: str,
        status: str,
        component: str,
        actor: Optional[str] = None,
        session_id: Optional[str] = None,
        resource: Optional[str] = None,
        tool_name: Optional[str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> AuditEvent:
        metadata_dict = dict(metadata or {})
        resolved_actor = actor or self._default_actor or self._resolve_actor(
            metadata_dict
        )
        resolved_session_id = (
            session_id
            or self._default_session_id
            or self._resolve_session_id(metadata_dict)
            or self.session_id
        )
        event = AuditEvent(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            status=status,
            occurred_at=datetime.now(timezone.utc).isoformat(),
            component=component,
            operation=operation,
            actor=resolved_actor,
            resource=resource,
            tool_name=tool_name,
            session_id=resolved_session_id,
            metadata=self._sanitize_metadata(metadata_dict),
        )

        self._emit(event)
        return event

    def log_file_operation(
        self,
        operation: str,
        *,
        status: str = "success",
        actor: Optional[str] = None,
        session_id: Optional[str] = None,
        resource: Optional[str] = None,
        tool_name: Optional[str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> AuditEvent:
        return self.log_event(
            event_type="file_operation",
            operation=operation,
            status=status,
            component="file",
            actor=actor,
            session_id=session_id,
            resource=resource,
            tool_name=tool_name,
            metadata=metadata,
        )

    def log_config_operation(
        self,
        operation: str,
        *,
        status: str = "success",
        actor: Optional[str] = None,
        session_id: Optional[str] = None,
        resource: Optional[str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> AuditEvent:
        return self.log_event(
            event_type="config_operation",
            operation=operation,
            status=status,
            component="config",
            actor=actor,
            session_id=session_id,
            resource=resource,
            metadata=metadata,
        )

    def log_security_operation(
        self,
        operation: str,
        *,
        status: str = "success",
        actor: Optional[str] = None,
        session_id: Optional[str] = None,
        resource: Optional[str] = None,
        tool_name: Optional[str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> AuditEvent:
        return self.log_event(
            event_type="security_operation",
            operation=operation,
            status=status,
            component="security",
            actor=actor,
            session_id=session_id,
            resource=resource,
            tool_name=tool_name,
            metadata=metadata,
        )

    def _emit(self, event: AuditEvent) -> None:
        payload = event.to_dict()
        level = self._level_for_status(event.status)
        self.logger.log(
            level,
            "AUDIT %s",
            payload,
            extra={
                "tool_name": event.tool_name,
                "audit_event_id": event.event_id,
                "audit_event_type": event.event_type,
            },
        )

    @staticmethod
    def _level_for_status(status: str) -> int:
        lowered = status.lower()
        if lowered in {"error", "failed", "failure", "denied"}:
            return logging.ERROR
        if lowered in {"warning", "partial"}:
            return logging.WARNING
        return logging.INFO

    def _sanitize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        sanitized: Dict[str, Any] = {}
        for key, value in metadata.items():
            if SENSITIVE_KEY_PATTERN.search(key):
                sanitized[key] = "***redacted***"
                continue

            sanitized[key] = self._sanitize_value(value)
        return sanitized

    @staticmethod
    def _resolve_actor(metadata: Mapping[str, Any]) -> Optional[str]:
        """Resolve actor identity from explicit metadata or environment."""

        metadata_actor = metadata.get("actor")
        if metadata_actor is not None:
            return str(metadata_actor)

        for env_key in ("RFU_ACTOR", "USER", "USERNAME"):
            env_value = os.getenv(env_key)
            if env_value:
                return env_value

        return None

    @staticmethod
    def _resolve_session_id(metadata: Mapping[str, Any]) -> Optional[str]:
        """Resolve session identifier from metadata when present."""

        session_id = metadata.get("session_id")
        if session_id is not None:
            return str(session_id)
        return None

    def _sanitize_value(self, value: Any) -> Any:
        if isinstance(value, Mapping):
            nested: Dict[str, Any] = {}
            for sub_key, sub_value in value.items():
                sub_key_str = str(sub_key)
                if SENSITIVE_KEY_PATTERN.search(sub_key_str):
                    nested[sub_key_str] = "***redacted***"
                else:
                    nested[sub_key_str] = self._sanitize_value(sub_value)
            return nested

        if isinstance(value, (list, tuple, set)):
            return [self._sanitize_value(item) for item in value]

        if isinstance(value, Path):
            return str(value)

        if isinstance(value, Exception):
            return str(value)

        if isinstance(value, str) and len(value) > 4096:
            return value[:4093] + "..."

        return value


_shared_audit_trail: Optional[AuditTrailService] = None


def get_audit_trail() -> AuditTrailService:
    """Return a process-wide shared audit trail instance."""

    global _shared_audit_trail
    if _shared_audit_trail is None:
        _shared_audit_trail = AuditTrailService()
    return _shared_audit_trail
