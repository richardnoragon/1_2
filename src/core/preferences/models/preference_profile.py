"""Dataclass helpers for user preference profiles and metadata."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import IntEnum
from typing import Any, Dict, Mapping, MutableMapping

from src.core.auth.models.utils import (
    bool_from_db,
    dict_to_json,
    json_to_dict,
    parse_datetime,
)


class PreferenceSchemaVersion(IntEnum):
    """Supported schema versions for serialized preference payloads."""

    V1 = 1
    V2 = 2

    @classmethod
    def coerce(cls, value: Any) -> "PreferenceSchemaVersion":
        try:
            if isinstance(value, PreferenceSchemaVersion):
                return value
            return cls(int(value))
        except (TypeError, ValueError):
            # pragma: no cover - defensive fallback
            return cls.V1


def _coerce_payload(value: Any) -> Dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    data = json_to_dict(value)
    return data or {}


def _serialize_payload(value: Mapping[str, Any] | None) -> str:
    if not value:
        return "{}"
    serialized = dict_to_json(value)
    return serialized or "{}"


@dataclass(slots=True)
class PreferenceProfile:
    preferences_id: str
    user_id: str
    schema_version: PreferenceSchemaVersion = PreferenceSchemaVersion.V1
    payload: Dict[str, Any] = field(default_factory=dict)
    is_encrypted: bool = False
    metadata: Dict[str, Any] | None = None
    shared_metadata: Dict[str, Any] | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> "PreferenceProfile":
        return cls(
            preferences_id=row["preferences_id"],
            user_id=row["user_id"],
            schema_version=PreferenceSchemaVersion.coerce(
                row.get("schema_version", PreferenceSchemaVersion.V1)
            ),
            payload=_coerce_payload(row.get("payload")),
            is_encrypted=bool_from_db(row.get("is_encrypted")),
            metadata=json_to_dict(row.get("metadata")),
            shared_metadata=json_to_dict(row.get("shared_metadata")),
            created_at=parse_datetime(row.get("created_at")),
            updated_at=parse_datetime(row.get("updated_at")),
        )

    def to_record(self) -> Dict[str, Any]:
        return {
            "preferences_id": self.preferences_id,
            "user_id": self.user_id,
            "schema_version": int(self.schema_version),
            "payload": _serialize_payload(self.payload),
            "is_encrypted": int(self.is_encrypted),
            "metadata": dict_to_json(self.metadata),
            "shared_metadata": dict_to_json(self.shared_metadata),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def mark_encrypted(
        self,
        *,
        context: Mapping[str, Any] | None = None,
    ) -> None:
        self.is_encrypted = True
        if context:
            merged: Dict[str, Any] = dict(self.metadata or {})
            merged["encryption"] = dict(context)
            self.metadata = merged
        self.touch()

    def mark_decrypted(self) -> None:
        self.is_encrypted = False
        if self.metadata and "encryption" in self.metadata:
            self.metadata.pop("encryption")
            if not self.metadata:
                self.metadata = None
        self.touch()

    def bump_schema_version(self, new_version: PreferenceSchemaVersion | int) -> None:
        self.schema_version = PreferenceSchemaVersion.coerce(new_version)
        self.touch()

    def update_payload(
        self,
        *,
        updates: Mapping[str, Any],
        replace: bool = False,
    ) -> None:
        if replace:
            self.payload = dict(updates)
        else:
            mutable: MutableMapping[str, Any] = dict(self.payload)
            mutable.update(dict(updates))
            self.payload = dict(mutable)
        self.touch()

    def record_share_event(
        self,
        *,
        shared_by: str,
        purpose: str,
        origin_surface: str | None = None,
        timestamp: datetime | None = None,
    ) -> None:
        event_time = timestamp or datetime.now(timezone.utc)
        iso_timestamp = (
            event_time.replace(microsecond=0).isoformat().replace("+00:00", "Z")
        )
        self.shared_metadata = {
            "shared_by": shared_by,
            "purpose": purpose,
            "timestamp": iso_timestamp,
        }
        if origin_surface:
            self.shared_metadata["origin_surface"] = origin_surface
        self.touch(event_time)

    def clear_share_event(self) -> None:
        self.shared_metadata = None
        self.touch()

    def touch(self, timestamp: datetime | None = None) -> None:
        self.updated_at = timestamp or datetime.now(timezone.utc)


__all__ = [
    "PreferenceProfile",
    "PreferenceSchemaVersion",
]
