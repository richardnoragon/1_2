"""Append-only repository for admin action audit rows."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable

from src.core.auth.models.admin_action_audit import (
    AdminActionAudit,
    AdminActionSurface,
    AdminActionType,
)
from src.core.auth.models.utils import datetime_to_iso
from src.core.database.repository_base import SQLiteRepository


class AdminActionAuditRepository(SQLiteRepository):
    """Persist :class:`AdminActionAudit` entries and export windows."""

    def append(self, audit: AdminActionAudit) -> AdminActionAudit:
        record = audit.to_record()
        created_at = record.get("created_at") or datetime_to_iso(
            audit.created_at or datetime.now(timezone.utc)
        )
        with self._connection() as conn:
            conn.execute(
                """
                INSERT INTO admin_action_audit (
                    audit_id,
                    actor_username,
                    target_username,
                    action_type,
                    origin_surface,
                    details,
                    created_at,
                    correlation_id,
                    metadata
                ) VALUES (
                    :audit_id,
                    :actor_username,
                    :target_username,
                    :action_type,
                    :origin_surface,
                    :details,
                    :created_at,
                    :correlation_id,
                    :metadata
                )
                ON CONFLICT(audit_id) DO UPDATE SET
                    actor_username = excluded.actor_username,
                    target_username = excluded.target_username,
                    action_type = excluded.action_type,
                    origin_surface = excluded.origin_surface,
                    details = excluded.details,
                    created_at = excluded.created_at,
                    correlation_id = excluded.correlation_id,
                    metadata = excluded.metadata
                """,
                {
                    "audit_id": record["audit_id"],
                    "actor_username": record["actor_username"],
                    "target_username": record.get("target_username"),
                    "action_type": record["action_type"],
                    "origin_surface": record["origin_surface"],
                    "details": record["details"],
                    "created_at": created_at,
                    "correlation_id": record.get("correlation_id"),
                    "metadata": record.get("metadata"),
                },
            )
            conn.commit()
        audit.created_at = audit.created_at or datetime.fromisoformat(created_at)
        return audit

    def fetch_recent(self, *, limit: int = 50) -> list[AdminActionAudit]:
        limit = max(1, min(limit, 500))
        with self._connection() as conn:
            rows = conn.execute(
                """
                SELECT * FROM admin_action_audit
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [AdminActionAudit.from_row(dict(row)) for row in rows or []]

    def for_target(
        self, target_username: str, *, limit: int = 100
    ) -> list[AdminActionAudit]:
        limit = max(1, min(limit, 500))
        with self._connection() as conn:
            rows = conn.execute(
                """
                SELECT * FROM admin_action_audit
                WHERE target_username = ?
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (target_username, limit),
            ).fetchall()
        return [AdminActionAudit.from_row(dict(row)) for row in rows or []]

    def export_window(
        self,
        *,
        start: datetime,
        end: datetime,
        action_types: Iterable[AdminActionType] | None = None,
        origin_surfaces: Iterable[AdminActionSurface] | None = None,
    ) -> list[AdminActionAudit]:
        clauses = ["created_at BETWEEN :start AND :end"]
        params: dict[str, object] = {
            "start": datetime_to_iso(start),
            "end": datetime_to_iso(end),
        }
        if action_types:
            type_list = [
                atype.value if isinstance(atype, AdminActionType) else str(atype)
                for atype in action_types
            ]
            placeholders = ",".join(f":type_{i}" for i in range(len(type_list)))
            clauses.append(f"action_type IN ({placeholders})")
            params.update({f"type_{i}": value for i, value in enumerate(type_list)})
        if origin_surfaces:
            surface_list = [
                (
                    surface.value
                    if isinstance(surface, AdminActionSurface)
                    else str(surface)
                )
                for surface in origin_surfaces
            ]
            placeholders = ",".join(f":surface_{i}" for i in range(len(surface_list)))
            clauses.append(f"origin_surface IN ({placeholders})")
            params.update(
                {f"surface_{i}": value for i, value in enumerate(surface_list)}
            )
        where_clause = " AND ".join(clauses)
        sql = (
            f"SELECT * FROM admin_action_audit WHERE {where_clause} ORDER BY created_at"
        )
        with self._connection() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [AdminActionAudit.from_row(dict(row)) for row in rows or []]

    def delete_before(self, *, cutoff: datetime) -> int:
        cutoff_iso = datetime_to_iso(cutoff)
        with self._connection() as conn:
            cursor = conn.execute(
                "DELETE FROM admin_action_audit WHERE created_at < ?",
                (cutoff_iso,),
            )
            conn.commit()
            return cursor.rowcount


__all__ = ["AdminActionAuditRepository"]
