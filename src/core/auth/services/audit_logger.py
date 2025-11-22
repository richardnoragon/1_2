"""Structured audit logging helper for admin/security events."""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from src.core.auth.models.admin_action_audit import (
    AdminActionAudit,
    AdminActionSurface,
    AdminActionType,
)
from src.core.auth.models.utils import parse_datetime
from src.core.auth.repositories.admin_action_audit_repository import (
    AdminActionAuditRepository,
)
from src.log_manager import get_log_manager

LOGGER = get_log_manager().get_logger("Auth.AuditLogger")


@dataclass(slots=True)
class AuditLogContext:
    origin_surface: str = "service"
    correlation_id: str | None = None


class AuditLogger:
    """Persist admin_action_audit rows with structured metadata."""

    def __init__(
        self,
        *,
        database_path: str | Path | None = None,
        repository: AdminActionAuditRepository | None = None,
        default_surface: str = "service",
    ) -> None:
        db_path = Path(database_path) if database_path else None
        self._repository = repository or AdminActionAuditRepository(
            database_path=db_path
        )
        self._default_surface = default_surface

    # ------------------------------------------------------------------
    def record_action(
        self,
        *,
        action_type: str | AdminActionType,
        actor_username: str,
        target_username: str | None = None,
        details: Mapping[str, Any],
        origin_surface: str | None = None,
        correlation_id: str,
        metadata: Mapping[str, Any] | None = None,
        occurred_at: datetime | str | None = None,
    ) -> AdminActionAudit:
        audit_type = (
            action_type
            if isinstance(action_type, AdminActionType)
            else AdminActionType.coerce(action_type)
        )
        surface = AdminActionSurface.coerce(origin_surface or self._default_surface)
        if not details:
            raise ValueError("details payload is required for audit logging")
        payload = json.dumps(details, sort_keys=True)
        timestamp = parse_datetime(occurred_at) if occurred_at else None
        created_at = timestamp or datetime.now(timezone.utc)
        if not correlation_id:
            raise ValueError("correlation_id is required for audit logging")
        correlation = correlation_id
        entry = AdminActionAudit(
            audit_id=uuid.uuid4().hex,
            actor_username=actor_username,
            target_username=target_username,
            action_type=audit_type,
            origin_surface=surface,
            details=payload,
            created_at=created_at,
        )
        entry.correlation_id = correlation
        if metadata:
            entry.metadata = dict(metadata)
        persisted = self._repository.append(entry)
        LOGGER.info(
            "Audit %s -> %s (%s)",
            actor_username,
            target_username or "<system>",
            audit_type.value,
        )
        return persisted


__all__ = ["AuditLogContext", "AuditLogger"]
