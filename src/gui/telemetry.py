"""UI telemetry infrastructure for RFU (spec §9.3, DEV-001).

All UI tools emit structured telemetry events via :func:`emit_telemetry`.

Required fields (TEL-5b)::

    event_type   – one of the VALID_EVENT_TYPES below
    tool_id      – logical identifier of the emitting tool
    actor_username – resolved from env / OS account / "anonymous"
    session_id   – linked to the active DatabaseManager session
    timestamp    – UTC ISO-8601, always auto-generated

Prohibited fields (DEV-001)::

    device_id        – stripped silently
    app_instance_id  – stripped silently

The function is intentionally side-effect-free to callers: any internal
exception is suppressed so a telemetry failure can never break the GUI.
"""

from __future__ import annotations

import getpass
import json
import logging
import os
from datetime import datetime, timezone
from typing import Any

_LOGGER = logging.getLogger("rfu.ui_telemetry")

# Lazy module-level import so tests can patch src.gui.telemetry.get_database_manager
try:
    from src.database.database_manager import (  # noqa: E402
        get_database_manager,
    )
except ImportError:
    get_database_manager = None  # type: ignore[assignment, misc]

# DEV-001: these fields must never appear in a UI telemetry event
_PROHIBITED_FIELDS: frozenset[str] = frozenset({"device_id", "app_instance_id"})

# spec §9.3: accepted event_type values
VALID_EVENT_TYPES: frozenset[str] = frozenset(
    {
        "ui_view_load",
        "ui_user_action",
        "ui_error_event",
        "ui_performance_metric",
    }
)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _resolve_actor_username() -> str:
    """Resolve the current user identifier for telemetry payloads.

    Resolution order:
    1. ``RFU_USER_ID`` environment variable (trimmed, non-empty)
    2. OS account name via :func:`getpass.getuser`
    3. Static fallback ``"anonymous"``
    """
    override = os.getenv("RFU_USER_ID")
    if override and override.strip():
        return override.strip()
    try:
        uid = getpass.getuser().strip()
        if uid:
            return uid
    except Exception:  # noqa: BLE001
        pass
    return "anonymous"


def _resolve_session_id() -> str:
    """Return the active DatabaseManager session UUID, or empty string."""
    try:
        from src.database.database_manager import (
            DatabaseManager,  # lazy import
        )

        return DatabaseManager().session_id
    except Exception:  # noqa: BLE001
        return ""


def _route_to_audit_log(payload: dict[str, Any]) -> None:
    """Insert a telemetry payload row into the SQLite ``app_logs`` table.

    This is the TEL-7a audit-log routing path.  Failures are silently
    suppressed so that database unavailability never propagates to the UI.
    """
    try:
        if get_database_manager is None:
            return

        db = get_database_manager()
        # Extra metadata = all fields beyond the five canonical ones
        metadata_fields = {
            k: v
            for k, v in payload.items()
            if k
            not in (
                "event_type",
                "tool_id",
                "session_id",
                "timestamp",
                "actor_username",
            )
        }
        db.execute_update(
            """
            INSERT INTO app_logs
                (level, logger_name, message, tool_name, session_id, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                "INFO",
                "ui_telemetry",
                payload["event_type"],
                payload["tool_id"],
                payload.get("session_id", ""),
                json.dumps(metadata_fields),
            ),
        )
    except Exception:  # noqa: BLE001 — graceful fallback (TEL-7a)
        pass


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def emit_telemetry(
    event_type: str,
    *,
    tool_id: str,
    actor_username: str | None = None,
    session_id: str | None = None,
    **kwargs: Any,
) -> None:
    """Emit a structured UI telemetry event (spec §9.3).

    Parameters
    ----------
    event_type:
        One of the four spec §9.3 types: ``ui_view_load``,
        ``ui_user_action``, ``ui_error_event``, ``ui_performance_metric``.
    tool_id:
        Logical identifier of the tool emitting the event.
    actor_username:
        Who triggered the event.  Resolved automatically if *None*.
    session_id:
        Active session UUID.  Resolved from DatabaseManager if *None*.
    **kwargs:
        Additional event-specific fields.  ``device_id`` and
        ``app_instance_id`` are silently stripped (DEV-001).
    """
    try:
        # TEL-6: strip prohibited fields (DEV-001)
        for field in _PROHIBITED_FIELDS:
            kwargs.pop(field, None)

        # Build the canonical payload (TEL-5b: five required fields)
        payload: dict[str, Any] = {
            "event_type": event_type,
            "tool_id": tool_id,
            "actor_username": (
                actor_username
                if actor_username is not None
                else _resolve_actor_username()
            ),
            "session_id": (
                session_id if session_id is not None else _resolve_session_id()
            ),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **kwargs,
        }

        # Structured log (human-readable + captured by LogManager handlers)
        _LOGGER.info(
            "ui_telemetry.%s tool=%s",
            event_type,
            tool_id,
            extra={"telemetry": payload},
        )

        # SQLite audit-log routing (TEL-7a)
        _route_to_audit_log(payload)

    except Exception:  # noqa: BLE001 — telemetry must never crash the UI
        pass
