"""Persistence helpers for the ``user_preferences`` table."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Mapping

from src.core.auth.models.utils import datetime_to_iso
from src.core.database.repository_base import SQLiteRepository
from src.core.preferences.models import PreferenceProfile, PreferenceSchemaVersion


class PreferenceProfileRepository(SQLiteRepository):
    """Load and store :class:`PreferenceProfile` rows."""

    def get(self, preferences_id: str) -> PreferenceProfile | None:
        query = "SELECT * FROM user_preferences WHERE preferences_id = ? LIMIT 1"
        with self._connection() as conn:
            row = conn.execute(query, (preferences_id,)).fetchone()
        if not row:
            return None
        return PreferenceProfile.from_row(dict(row))

    def get_by_user(self, user_id: str) -> PreferenceProfile | None:
        query = "SELECT * FROM user_preferences WHERE user_id = ? LIMIT 1"
        with self._connection() as conn:
            row = conn.execute(query, (user_id,)).fetchone()
        if not row:
            return None
        return PreferenceProfile.from_row(dict(row))

    def save(self, profile: PreferenceProfile) -> PreferenceProfile:
        record = profile.to_record()
        now = datetime.now(timezone.utc)
        created_at = datetime_to_iso(record.get("created_at") or now)
        updated_at = datetime_to_iso(record.get("updated_at") or now)
        payload = record.get("payload") or "{}"
        with self._connection() as conn:
            conn.execute(
                """
                INSERT INTO user_preferences (
                    preferences_id,
                    user_id,
                    schema_version,
                    payload,
                    is_encrypted,
                    metadata,
                    shared_metadata,
                    created_at,
                    updated_at
                ) VALUES (
                    :preferences_id,
                    :user_id,
                    :schema_version,
                    :payload,
                    :is_encrypted,
                    :metadata,
                    :shared_metadata,
                    :created_at,
                    :updated_at
                )
                ON CONFLICT(preferences_id) DO UPDATE SET
                    user_id = excluded.user_id,
                    schema_version = excluded.schema_version,
                    payload = excluded.payload,
                    is_encrypted = excluded.is_encrypted,
                    metadata = excluded.metadata,
                    shared_metadata = excluded.shared_metadata,
                    updated_at = excluded.updated_at
                """,
                {
                    "preferences_id": record["preferences_id"],
                    "user_id": record["user_id"],
                    "schema_version": int(
                        record.get("schema_version") or PreferenceSchemaVersion.V1
                    ),
                    "payload": payload,
                    "is_encrypted": int(record.get("is_encrypted") or 0),
                    "metadata": record.get("metadata"),
                    "shared_metadata": record.get("shared_metadata"),
                    "created_at": created_at,
                    "updated_at": updated_at,
                },
            )
            conn.commit()
        profile.created_at = profile.created_at or datetime.fromisoformat(created_at)
        profile.updated_at = datetime.fromisoformat(updated_at)
        return profile

    def delete(self, preferences_id: str) -> bool:
        with self._connection() as conn:
            cursor = conn.execute(
                "DELETE FROM user_preferences WHERE preferences_id = ?",
                (preferences_id,),
            )
            conn.commit()
            return bool(cursor.rowcount)

    def ensure_for_user(
        self,
        *,
        user_id: str,
        preferences_id: str,
        template_payload: Mapping[str, object] | None = None,
        schema_version: PreferenceSchemaVersion = PreferenceSchemaVersion.V1,
    ) -> PreferenceProfile:
        existing = self.get(preferences_id)
        if existing:
            return existing
        payload = dict(template_payload or {})
        profile = PreferenceProfile(
            preferences_id=preferences_id,
            user_id=user_id,
            schema_version=schema_version,
            payload=payload,
            created_at=datetime.now(timezone.utc),
        )
        return self.save(profile)

    def mark_encrypted(
        self,
        *,
        preferences_id: str,
        context: Mapping[str, object] | None = None,
    ) -> PreferenceProfile:
        profile = self._require(preferences_id)
        profile.mark_encrypted(context=context)
        return self.save(profile)

    def mark_decrypted(self, *, preferences_id: str) -> PreferenceProfile:
        profile = self._require(preferences_id)
        profile.mark_decrypted()
        return self.save(profile)

    def record_share_event(
        self,
        *,
        preferences_id: str,
        shared_by: str,
        purpose: str,
        origin_surface: str | None = None,
    ) -> PreferenceProfile:
        profile = self._require(preferences_id)
        profile.record_share_event(
            shared_by=shared_by,
            purpose=purpose,
            origin_surface=origin_surface,
        )
        return self.save(profile)

    def _require(self, preferences_id: str) -> PreferenceProfile:
        profile = self.get(preferences_id)
        if profile is None:
            raise ValueError(f"Preference profile '{preferences_id}' not found")
        return profile


__all__ = ["PreferenceProfileRepository"]
