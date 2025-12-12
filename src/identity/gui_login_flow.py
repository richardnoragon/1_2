"""GUI-focused login helpers that reuse the shared AuthService pipeline."""

from __future__ import annotations

import json
import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from src.core.auth.policies import InputValidator
from src.core.auth.services import (
    build_auth_service,
    build_registration_service,
)

_INPUT_VALIDATOR = InputValidator()
_LOGGER = logging.getLogger("RFU.Identity.GuiLogin")


def _validate_credentials(username: str, password: str) -> Tuple[str, str]:
    return _INPUT_VALIDATOR.validate_credentials(username, password)


def _safe_json_loads(raw_payload: str | None) -> Dict[str, Any]:
    if not raw_payload:
        return {}
    try:
        value = json.loads(raw_payload)
    except json.JSONDecodeError:  # pragma: no cover - defensive fallback
        _LOGGER.warning("Preference payload invalid JSON; using empty dict")
        return {}
    return value if isinstance(value, dict) else {}


def _load_preference_snapshot(
    database_path: Path,
    *,
    username: str,
    preference_identifier: Optional[str],
) -> Optional[Dict[str, Any]]:
    if not database_path or not database_path.exists():
        _LOGGER.debug(
            "Identity database %s not found; skipping snapshot",
            database_path,
        )
        return None

    conn = sqlite3.connect(database_path)
    conn.row_factory = sqlite3.Row
    try:
        row = None
        if preference_identifier:
            row = conn.execute(
                """
                SELECT preferences_id,
                       schema_version,
                       payload,
                       user_id,
                       updated_at
                FROM user_preferences
                WHERE preferences_id = ?
                LIMIT 1
                """,
                (preference_identifier,),
            ).fetchone()

        if row is None:
            row = conn.execute(
                """
                SELECT preferences_id,
                       schema_version,
                       payload,
                       user_id,
                       updated_at
                FROM user_preferences
                WHERE user_id = ?
                ORDER BY updated_at DESC
                LIMIT 1
                """,
                (username,),
            ).fetchone()

        if row is None:
            return None

        payload = _safe_json_loads(row["payload"])
        snapshot = {
            "preferences_id": row["preferences_id"],
            "schema_version": row["schema_version"],
            "payload": payload,
            "user_id": row["user_id"],
            "updated_at": row["updated_at"],
            "fetched_at": datetime.now(timezone.utc)
            .replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z"),
        }
        return snapshot
    except sqlite3.OperationalError as exc:  # pragma: no cover - schema guard
        _LOGGER.warning("Preference snapshot query failed: %s", exc)
        return None
    finally:
        conn.close()


def _fallback_snapshot(
    *,
    username: str,
    preference_identifier: Optional[str],
) -> Dict[str, Any]:
    pref_id = preference_identifier or f"pref_{username}"
    return {
        "preferences_id": pref_id,
        "schema_version": 1,
        "payload": {"layout": "default", "favorite_tools": []},
        "user_id": username,
        "updated_at": None,
        "fetched_at": datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
        "source": "fallback",
    }


def _build_preference_badge(
    *,
    username: str,
    snapshot: Dict[str, Any],
) -> Dict[str, Any]:
    payload = snapshot.get("payload") or {}
    layout_label = str(payload.get("layout") or "default").strip()
    preferences_id = snapshot.get("preferences_id")
    parts = [username]
    if preferences_id:
        parts.append(str(preferences_id))
    if layout_label:
        parts.append(layout_label)
        label = " | ".join(parts)
    badge = {
        "text": label,
        "label": label,
        "user": username,
        "preferences_id": preferences_id,
        "layout": layout_label,
    }
    favorite_tools = payload.get("favorite_tools")
    if isinstance(favorite_tools, list):
        badge["favorite_tools"] = favorite_tools
    return badge


def login_with_preferences(
    *,
    database_path: str | Path,
    username: str,
    password: str,
    justification: Optional[str] = None,
) -> Dict[str, object]:
    """Authenticate a user and return hub-friendly session context.

    Args:
        database_path: Path to the identity database.
        username: The username to authenticate.
        password: The password to verify.
        justification: Required for break-glass accounts; reason for
            emergency access (minimum 10 characters).

    Returns:
        Dictionary with session context including status, username, role,
        preference snapshot, and session details.

    Raises:
        BreakGlassJustificationRequired: When a break-glass account logs
            in without providing justification.
        AuthenticationError: For invalid credentials or account state.
    """

    sanitized_username, normalized_password = _validate_credentials(
        username,
        password,
    )
    auth_service = build_auth_service(
        database_path=database_path,
        validator=_INPUT_VALIDATOR,
    )
    session = auth_service.authenticate(
        sanitized_username,
        normalized_password,
        surface="gui",
        justification=justification,
    )
    db_path = Path(database_path)
    snapshot = _load_preference_snapshot(
        db_path,
        username=session.username,
        preference_identifier=session.preferences_user_id,
    )
    workspace_ready = snapshot is not None
    if snapshot is None:
        snapshot = _fallback_snapshot(
            username=session.username,
            preference_identifier=session.preferences_user_id,
        )

    badge = _build_preference_badge(
        username=session.username,
        snapshot=snapshot,
    )

    return {
        "status": "authenticated",
        "username": session.username,
        "role": session.role,
        "workspace_ready": workspace_ready,
        "preference_snapshot": snapshot,
        "preference_badge": badge,
        "session": {
            "username": session.username,
            "role": session.role,
            "preferences_user_id": session.preferences_user_id,
            "reset_required": session.reset_required,
        },
    }


def submit_registration_request(
    *,
    database_path: str | Path,
    username: str,
    password: str,
    metadata: Dict[str, Any] | None = None,
    channel: str = "gui",
) -> Dict[str, Any]:
    """Submit a registration request using shared validator rules."""

    service = build_registration_service(
        database_path=database_path,
        origin_surface="gui",
        validator=_INPUT_VALIDATOR,
    )
    return service.register_user(
        username=username,
        password=password,
        channel=channel,
        metadata=metadata,
    )


__all__ = ["login_with_preferences", "submit_registration_request"]
