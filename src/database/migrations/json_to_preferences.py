"""Backfill user preferences from legacy configuration sources."""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterable, List, Optional, Sequence

from src.config.schema_map import map_config_to_preferences
from src.config.config_manager import get_config_manager
from src.core.preferences.store import PreferencesStore
from src.database.database_manager import DatabaseError, get_database_manager

logger = logging.getLogger("RFU.PreferenceMigration")

_VALID_TYPES = {"string", "int", "float", "bool", "json"}
_MIGRATION_KEY = "pref/2025-11-11/config-bootstrap"
_MIGRATION_SOURCE = "config-bootstrap"
_MIGRATION_NOTES = "JSON ConfigManager bootstrap"
_SOURCE_TAG = "config-migration"


def migrate_preferences_from_config(
    user_id: str = "default",
    db=None,
) -> bool:
    """Migrate legacy preferences into the unified preference store."""

    manager = db or get_database_manager()
    if manager.preference_migration_applied(_MIGRATION_KEY):
        logger.debug(
            "Preference migration %s already recorded",
            _MIGRATION_KEY,
        )
        return False
    config_manager = get_config_manager()
    backup_path = _create_config_backup(config_manager)
    config = getattr(config_manager, "config", {})
    mapped = map_config_to_preferences(config)

    store = PreferencesStore(db=manager)

    migrated = _apply_mapped_preferences(manager, store, user_id, mapped)

    if migrated:
        notes = _compose_migration_notes(backup_path)
        try:
            manager.record_preference_migration(
                _MIGRATION_KEY,
                applied_by=_MIGRATION_SOURCE,
                notes=notes,
            )
        except DatabaseError:
            logger.exception("Failed to record preference migration key")

    return migrated


def _apply_mapped_preferences(
    db,
    store: PreferencesStore,
    user_id: str,
    mapped: Dict[str, Dict[str, Any]],
) -> bool:
    """Write mapped legacy configuration values into the preference store."""

    migrated = False

    for category, values in mapped.items():
        if not values:
            continue

        existing = store.get_category(user_id, category)
        to_write: Dict[str, Any] = {}
        for key, value in values.items():
            current = existing.get(key)
            if key not in existing or _should_backfill(current):
                to_write[key] = value

        if not to_write:
            continue

        affected = store.set_category(user_id, category, to_write)
        if not affected:
            continue

        _mark_preference_sources(
            db,
            user_id,
            category,
            tuple(to_write.keys()),
        )
        logger.info(
            "Migrated %d legacy %s preference keys",
            affected,
            category,
        )
        migrated = True

    return migrated


def _should_backfill(current: Any) -> bool:
    """Return True when a stored value should be replaced by migration data."""

    if current is None:
        return True
    if isinstance(current, str):
        return current.strip() == ""
    if isinstance(current, (list, tuple, set, dict)):
        return len(current) == 0
    return False


def _mark_preference_sources(
    db,
    user_id: str,
    category: str,
    keys: Sequence[str],
) -> None:
    """Annotate migrated rows with the config migration source tag."""

    if not keys:
        return

    placeholders = ", ".join("?" for _ in keys)
    params = (_SOURCE_TAG, user_id, category, *keys)
    db.execute_update(
        f"""
        UPDATE user_preferences
           SET source = ?
         WHERE user_id = ?
           AND preference_category = ?
           AND preference_key IN ({placeholders})
        """,
        params,
    )


def _create_config_backup(config_manager) -> Optional[str]:
    """Attempt to create a timestamped backup of the config file."""

    create_backup = getattr(config_manager, "create_backup", None)
    if not callable(create_backup):
        return None

    try:
        backup_path = create_backup()
        logger.info("Config backup stored at %s", backup_path)
        return backup_path
    except Exception:  # noqa: BLE001
        logger.warning(
            "Unable to create config backup prior to migration",
            exc_info=True,
        )
        return None


def _compose_migration_notes(backup_path: Optional[str]) -> Optional[str]:
    """Create a descriptive notes payload for the migration record."""

    if not backup_path:
        return _MIGRATION_NOTES
    return f"{_MIGRATION_NOTES} (backup={backup_path})"


def export_preference_snapshot(
    categories: Iterable[str],
    user_id: str = "default",
) -> List[Dict[str, Any]]:
    """Utility helper used in tests to validate migration results."""

    store = PreferencesStore()
    snapshot: List[Dict[str, Any]] = []
    for category in categories:
        data = store.get_category(user_id, category)
        if data:
            snapshot.append({"category": category, "values": data})
    return snapshot
