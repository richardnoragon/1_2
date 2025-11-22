"""Preference portability helpers for export and import flows."""

from __future__ import annotations

import json
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Tuple,
)

try:  # pragma: no cover - optional dependency
    import pyAesCrypt  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - optional dependency
    pyAesCrypt = None  # type: ignore[assignment]

if TYPE_CHECKING:  # pragma: no cover
    import pyAesCrypt  # type: ignore  # noqa: F401

from src.core.preferences.store import VALID_TYPES, PreferencesStore
from src.log_manager import get_log_manager

_BUFFER_SIZE = 64 * 1024
_EXPORT_VERSION = "2025.11-beta"
_EXPORT_ROOT = Path("backups/preferences")
_IMPORT_SOURCE = "pref-import"
AES_AVAILABLE = pyAesCrypt is not None


_LOGGER = get_log_manager().get_logger("PreferencePortability")


class PreferencePortabilityError(RuntimeError):
    """Base exception for preference portability operations."""


class InvalidExportError(PreferencePortabilityError):
    """Raised when an export payload is malformed or unsupported."""


class DecryptionRequiredError(PreferencePortabilityError):
    """Raised when attempting to load an encrypted file without a key."""


@dataclass
class PreferenceEntry:
    """Serialisable representation of a single preference entry."""

    category: str
    key: str
    value: Any
    value_type: str
    is_encrypted: bool
    source: Optional[str]
    schema_version: Optional[int]


def export_preferences(
    user_id: str,
    *,
    destination: Optional[Path] = None,
    categories: Optional[Iterable[str]] = None,
    include_encrypted: bool = True,
    passphrase: Optional[str] = None,
    store: Optional[PreferencesStore] = None,
) -> Path:
    """Export preferences for a user into a JSON (optionally AES) payload."""

    if not user_id or not isinstance(user_id, str):
        raise ValueError("user_id must be a non-empty string")

    prefs_store = store or PreferencesStore()
    entries = _collect_entries(
        prefs_store,
        user_id,
        categories,
        include_encrypted=include_encrypted,
    )

    snapshot = {
        "version": _EXPORT_VERSION,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "user_id": user_id,
        "entry_count": len(entries),
        "entries": [entry.__dict__ for entry in entries],
    }

    categories_logged = sorted({entry.category for entry in entries}) if entries else []
    encrypted = bool(passphrase)
    base_dir = destination or (_EXPORT_ROOT / user_id)
    base_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    json_path = base_dir / f"preferences_{timestamp}.json"
    json_path.write_text(
        json.dumps(snapshot, indent=2, ensure_ascii=True),
        encoding="utf-8",
    )

    output_path: Path
    if passphrase:
        _ensure_aes_support()
        encrypted_path = json_path.with_suffix(json_path.suffix + ".aes")
        pyAesCrypt.encryptFile(
            str(json_path),
            str(encrypted_path),
            passphrase,
            _BUFFER_SIZE,
        )
        json_path.unlink(missing_ok=True)
        output_path = encrypted_path
    else:
        output_path = json_path

    _LOGGER.info(
        "preferences_export_completed user_id=%s entry_count=%d "
        "categories=%s encrypted=%s destination=%s",
        user_id,
        len(entries),
        categories_logged,
        encrypted,
        str(output_path),
    )

    return output_path


def import_preferences(
    source: Path,
    *,
    passphrase: Optional[str] = None,
    target_user_id: Optional[str] = None,
    allow_overwrite: bool = False,
    store: Optional[PreferencesStore] = None,
) -> Dict[str, Any]:
    """Import preferences from an export payload."""

    payload = _load_payload(Path(source), passphrase)
    if not isinstance(payload, dict):
        raise InvalidExportError("Export payload must be a JSON object")

    entries = payload.get("entries", [])
    if not isinstance(entries, list):
        raise InvalidExportError("Export entries must be a list")

    source_user = payload.get("user_id")
    target_user = target_user_id or source_user
    if not target_user or not isinstance(target_user, str):
        raise InvalidExportError("Export missing valid user identifier")

    prefs_store = store or PreferencesStore()
    applied = 0
    skipped = 0
    categories_seen: set[str] = set()
    for entry in entries:
        (
            category,
            key,
            value_type,
            value,
            is_encrypted,
            schema_version,
        ) = _prepare_entry(entry)

        if not allow_overwrite and _exists(
            prefs_store,
            target_user,
            category,
            key,
        ):
            skipped += 1
            continue

        categories_seen.add(category)
        prefs_store.set(
            target_user,
            category,
            key,
            value,
            value_type=value_type,
            is_encrypted=is_encrypted,
        )
        prefs_store.db.execute_update(
            """
            UPDATE user_preferences
               SET source = ?,
                   schema_version = COALESCE(?, schema_version)
             WHERE user_id = ?
               AND preference_category = ?
               AND preference_key = ?
            """,
            (
                _IMPORT_SOURCE,
                schema_version,
                target_user,
                category,
                key,
            ),
        )
        applied += 1

    _LOGGER.info(
        "preferences_import_completed source=%s target_user=%s "
        "entry_count=%d applied=%d skipped=%d categories=%s "
        "encrypted=%s allow_overwrite=%s",
        str(source),
        target_user,
        len(entries),
        applied,
        skipped,
        sorted(categories_seen) if categories_seen else [],
        bool(passphrase),
        allow_overwrite,
    )

    return {
        "user_id": target_user,
        "applied": applied,
        "skipped": skipped,
        "version": payload.get("version"),
    }


def _collect_entries(
    store: PreferencesStore,
    user_id: str,
    categories: Optional[Iterable[str]],
    *,
    include_encrypted: bool,
) -> List[PreferenceEntry]:
    if categories is None:
        category_list = list(store.list_categories(user_id))
    else:
        category_list = sorted({str(cat) for cat in categories})

    entries: List[PreferenceEntry] = []
    for category in category_list:
        rows = store.db.execute_query(
            """
            SELECT preference_key, preference_value, value_type,
                   is_encrypted, source, schema_version
            FROM user_preferences
            WHERE user_id = ? AND preference_category = ?
            ORDER BY preference_key
            """,
            (user_id, category),
        )
        for row in rows:
            encrypted = bool(row["is_encrypted"])
            if encrypted and not include_encrypted:
                continue
            value = _deserialize(row["preference_value"], row["value_type"])
            row_keys = row.keys()
            source = row["source"] if "source" in row_keys else None
            schema_version = (
                row["schema_version"] if "schema_version" in row_keys else None
            )
            entries.append(
                PreferenceEntry(
                    category=category,
                    key=row["preference_key"],
                    value=value,
                    value_type=row["value_type"],
                    is_encrypted=encrypted,
                    source=source,
                    schema_version=schema_version,
                )
            )
    return entries


def _deserialize(value: str, value_type: str) -> Any:
    try:
        if value_type == "json":
            return json.loads(value)
        if value_type == "bool":
            return value.lower() in ("true", "1", "yes")
        if value_type == "int":
            return int(value)
        if value_type == "float":
            return float(value)
        return value
    except Exception as exc:  # noqa: BLE001
        raise InvalidExportError(
            "Unable to deserialize preference value",
        ) from exc


def _coerce_value(value: Any, value_type: str) -> Any:
    if value_type == "json":
        if not isinstance(value, (dict, list)):
            raise InvalidExportError("JSON preference must be dict or list")
        return value
    if value_type == "bool":
        return _coerce_bool(value)
    if value_type == "int":
        return _coerce_numeric(int, "int", value)
    if value_type == "float":
        return _coerce_numeric(float, "float", value)
    if not isinstance(value, str):
        return str(value)
    return value


def _coerce_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ("true", "1", "yes")
    if isinstance(value, (int, float)):
        return bool(value)
    raise InvalidExportError("Cannot coerce value to bool")


def _coerce_numeric(
    caster: Callable[[Any], Any],
    label: str,
    value: Any,
) -> Any:
    try:
        return caster(value)
    except (TypeError, ValueError) as exc:  # noqa: BLE001
        raise InvalidExportError(f"Cannot coerce value to {label}") from exc


def _exists(
    store: PreferencesStore,
    user_id: str,
    category: str,
    key: str,
) -> bool:
    rows = store.db.execute_query(
        """
        SELECT 1
        FROM user_preferences
        WHERE user_id = ? AND preference_category = ? AND preference_key = ?
        LIMIT 1
        """,
        (user_id, category, key),
    )
    return bool(rows)


def _load_payload(source: Path, passphrase: Optional[str]) -> Dict[str, Any]:
    if not source.exists():
        raise FileNotFoundError(source)

    if source.suffix == ".aes":
        if not passphrase:
            raise DecryptionRequiredError(
                "Encrypted export requires a passphrase",
            )
        _ensure_aes_support()
        with tempfile.NamedTemporaryFile(delete=False) as handle:
            tmp_path = Path(handle.name)
        try:
            try:
                pyAesCrypt.decryptFile(
                    str(source),
                    str(tmp_path),
                    passphrase,
                    _BUFFER_SIZE,
                )
            except ValueError as exc:
                raise InvalidExportError(
                    "Unable to decrypt export; validate passphrase",
                ) from exc
            data = tmp_path.read_text(encoding="utf-8")
        finally:
            tmp_path.unlink(missing_ok=True)
    else:
        if passphrase:
            raise InvalidExportError(
                "Passphrase provided for unencrypted export",
            )
        data = source.read_text(encoding="utf-8")

    try:
        return json.loads(data)
    except json.JSONDecodeError as exc:  # noqa: BLE001
        raise InvalidExportError("Export payload is not valid JSON") from exc


def _prepare_entry(
    entry: Any,
) -> Tuple[str, str, str, Any, bool, Optional[int]]:
    if not isinstance(entry, dict):
        raise InvalidExportError("Preference entry must be a JSON object")

    category = entry.get("category")
    key = entry.get("key")
    value_type = entry.get("value_type")
    value = entry.get("value")
    is_encrypted = bool(entry.get("is_encrypted", False))
    schema_version = entry.get("schema_version")

    if not category or not key:
        raise InvalidExportError("Preference entry missing category/key")
    if value_type not in VALID_TYPES:
        raise InvalidExportError(f"Unsupported value_type '{value_type}'")

    coerced = _coerce_value(value, value_type)
    return category, key, value_type, coerced, is_encrypted, schema_version


def _ensure_aes_support() -> None:
    if not AES_AVAILABLE:
        raise PreferencePortabilityError(
            "pyAesCrypt is required for AES export/import support",
        )


__all__ = [
    "PreferencePortabilityError",
    "InvalidExportError",
    "DecryptionRequiredError",
    "PreferenceEntry",
    "AES_AVAILABLE",
    "export_preferences",
    "import_preferences",
]
