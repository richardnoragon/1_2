"""Preference sharing service implementation."""

from __future__ import annotations

import json
import sqlite3
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

try:  # pragma: no cover - fallback when running outside package context
    from src.log_manager import get_log_manager
except ImportError:  # pragma: no cover - fallback for direct execution
    from log_manager import get_log_manager  # type: ignore

from src.core.auth.models.admin_action_audit import AdminActionType
from src.core.auth.services.audit_logger import AuditLogger

LOGGER = get_log_manager().get_logger("Preferences.ShareService")


@dataclass(slots=True)
class ShareService:
    """Reusable preference sharing policies for all surfaces."""

    database_path: Path
    origin_surface: str = "cli"
    _audit_logger: AuditLogger = field(init=False, repr=False)

    def __init__(
        self,
        *,
        database_path: str | Path,
        origin_surface: str = "cli",
        audit_logger: AuditLogger | None = None,
    ) -> None:
        self.database_path = Path(database_path)
        self.origin_surface = origin_surface
        self._audit_logger = audit_logger or AuditLogger(
            database_path=self.database_path,
            default_surface=self.origin_surface,
        )

    # ------------------------------------------------------------------
    def export_preferences(
        self,
        *,
        username: str,
        purpose: str,
        actor_username: Optional[str] = None,
        additional_actor_candidates: Optional[Iterable[Optional[str]]] = None,
    ) -> Dict[str, Any]:
        purpose_value = (purpose or "").strip()
        if not purpose_value:
            raise ValueError("purpose is required")

        with self._connect() as conn:
            user_row = self._fetch_user(conn, username)
            if not user_row["share_preferences"]:
                raise PermissionError(
                    "share_preferences flag is disabled for this user"
                )
            preferences_id = user_row["preferences_id"]
            if not preferences_id:
                raise ValueError(
                    (
                        "User {username!r} does not have an assigned " "preferences_id"
                    ).format(username=username)
                )

            pref_row = self._fetch_preferences(conn, preferences_id)
            payload = self._load_payload(pref_row["payload"])
            metadata = self._build_metadata(
                username=username,
                purpose=purpose_value,
                schema_version=pref_row["schema_version"],
            )
            actor_candidates: list[Optional[str]] = []
            if actor_username:
                actor_candidates.append(actor_username)
            if additional_actor_candidates:
                actor_candidates.extend(additional_actor_candidates)
            actor = self._resolve_actor(
                conn,
                candidates=actor_candidates,
                default=username,
            )

            conn.execute(
                """
                UPDATE user_preferences
                SET shared_metadata = ?,
                    updated_at = ?
                WHERE preferences_id = ?
                """,
                (
                    json.dumps(metadata, sort_keys=True),
                    metadata["shared_at"],
                    preferences_id,
                ),
            )

            self._insert_audit_entry(
                actor_username=actor,
                target_username=username,
                preferences_id=preferences_id,
                purpose=purpose_value,
                schema_version=pref_row["schema_version"],
                shared_metadata=metadata,
            )
            conn.commit()

            result = {
                "username": username,
                "preferences_id": preferences_id,
                "purpose": purpose_value,
                "export": {
                    "preferences": payload,
                    "metadata": metadata,
                },
            }
            LOGGER.info(
                "Preference export prepared for %s (purpose=%s, actor=%s)",
                username,
                purpose_value,
                actor,
            )
            return result

    # ------------------------------------------------------------------
    def _connect(self) -> sqlite3.Connection:
        if not self.database_path:
            raise FileNotFoundError("Identity database path is not configured")
        conn = sqlite3.connect(self.database_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON;")
        return conn

    def _fetch_user(
        self,
        conn: sqlite3.Connection,
        username: str,
    ) -> sqlite3.Row:
        row = conn.execute(
            """
            SELECT username,
                   share_preferences,
                   preferences_id
            FROM user_accounts
            WHERE username = ?
            LIMIT 1
            """,
            (username,),
        ).fetchone()
        if row is None:
            raise ValueError(f"User {username!r} does not exist in user_accounts")
        return row

    def _fetch_preferences(
        self,
        conn: sqlite3.Connection,
        preferences_id: str,
    ) -> sqlite3.Row:
        row = conn.execute(
            """
            SELECT preferences_id,
                   schema_version,
                   payload
            FROM user_preferences
            WHERE preferences_id = ?
            LIMIT 1
            """,
            (preferences_id,),
        ).fetchone()
        if row is None:
            raise ValueError(
                f"Preference profile {preferences_id!r} not found for export"
            )
        return row

    def _load_payload(self, payload_text: str) -> Dict[str, Any]:
        try:
            payload = json.loads(payload_text or "{}")
        except json.JSONDecodeError as exc:  # pragma: no cover - defensive
            raise ValueError("Stored preference payload is not valid JSON") from exc
        if not isinstance(payload, dict):
            raise ValueError("Preference payload must be a JSON object")
        return payload

    def _build_metadata(
        self,
        *,
        username: str,
        purpose: str,
        schema_version: int,
    ) -> Dict[str, Any]:
        from datetime import datetime, timezone

        shared_at = (
            datetime.now(timezone.utc)
            .replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z")
        )
        return {
            "shared_by": username,
            "purpose": purpose,
            "shared_at": shared_at,
            "origin_surface": self.origin_surface,
            "schema_version": schema_version,
        }

    def _insert_audit_entry(
        self,
        *,
        actor_username: str,
        target_username: str,
        preferences_id: str,
        purpose: str,
        schema_version: int,
        shared_metadata: Dict[str, Any],
    ) -> None:
        correlation_id = self._build_correlation_id(preferences_id)
        self._audit_logger.record_action(
            action_type=AdminActionType.SHARE_PREFERENCES,
            actor_username=actor_username,
            target_username=target_username,
            details={
                "preferences_id": preferences_id,
                "purpose": purpose,
                "schema_version": schema_version,
            },
            origin_surface=self.origin_surface,
            metadata={"shared_metadata": shared_metadata},
            correlation_id=correlation_id,
        )

    def _resolve_actor(
        self,
        conn: sqlite3.Connection,
        *,
        candidates: Iterable[Optional[str]],
        default: str,
    ) -> str:
        for candidate in candidates:
            if not candidate:
                continue
            row = conn.execute(
                "SELECT 1 FROM user_accounts WHERE username = ? LIMIT 1",
                (candidate,),
            ).fetchone()
            if row:
                return candidate
        return default

    @staticmethod
    def _build_correlation_id(preferences_id: str) -> str:
        token = uuid.uuid4().hex[:8]
        return f"share-{preferences_id}-{token}"


__all__ = ["ShareService"]
