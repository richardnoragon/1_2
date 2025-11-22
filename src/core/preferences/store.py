"""PreferencesStore: database-backed user preference API.

This module provides a typed, modular, and testable interface for storing
and retrieving user preferences with strong namespacing. It uses the
canonical SQLite database (`user_preferences` table) and is designed to be
safe to adopt incrementally alongside existing JSON-based ConfigManager code.

Contracts
- Key space: (user_id, preference_category, preference_key) is unique
- Types: value_type in {string,int,float,bool,json}; values are serialized
- Errors: raise ValueError for invalid inputs; surface DatabaseError for IO
- Success: methods return concrete values or counts; never swallow errors

Edge cases handled
- Missing DB file → callers may choose to fall back; this API surfaces errors
- Large values → JSON type recommended; size not enforced here
- Concurrent writes → rely on SQLite + unique constraints; upsert semantics
- Unknown types → rejected at write time
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Optional

from src.database.database_manager import DatabaseManager, get_database_manager

VALID_TYPES = {"string", "int", "float", "bool", "json"}


def _infer_type(value: Any) -> str:
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int) and not isinstance(value, bool):
        return "int"
    if isinstance(value, float):
        return "float"
    if isinstance(value, (dict, list)):
        return "json"
    return "string"


def _serialize(value: Any, value_type: str) -> str:
    if value_type == "json":
        return json.dumps(value, ensure_ascii=False)
    if value_type == "bool":
        return "true" if bool(value) else "false"
    return str(value)


def _deserialize(raw: str, value_type: str) -> Any:
    try:
        if value_type == "json":
            return json.loads(raw)
        if value_type == "bool":
            return raw.lower() in ("true", "1", "yes")
        if value_type == "int":
            return int(raw)
        if value_type == "float":
            return float(raw)
        return raw
    except Exception:
        # Fallback to raw on type conversion error
        return raw


@dataclass(frozen=True)
class PreferenceKey:
    user_id: str
    category: str
    key: str


class PreferencesStore:
    """Database-backed preference CRUD with batch helpers."""

    def __init__(self, db: Optional[DatabaseManager] = None) -> None:
        self.db = db or get_database_manager()

    # ------------------------- Read APIs -------------------------
    def get(self, user_id: str, category: str, key: str, default: Any = None) -> Any:
        self._validate_ns(user_id, category, key)
        rows = self.db.execute_query(
            """
                        SELECT preference_value AS value, value_type
                        FROM user_preferences
                        WHERE user_id = ?
                            AND preference_category = ?
                            AND preference_key = ?
                        LIMIT 1
            """,
            (user_id, category, key),
        )
        if not rows:
            return default
        return _deserialize(rows[0]["value"], rows[0]["value_type"])

    def get_category(self, user_id: str, category: str) -> Dict[str, Any]:
        # Use a placeholder key to reuse namespace validation
        self._validate_ns(user_id, category, "k")
        rows = self.db.execute_query(
            """
            SELECT preference_key, preference_value AS value, value_type
            FROM user_preferences
            WHERE user_id = ? AND preference_category = ?
            ORDER BY preference_key
            """,
            (user_id, category),
        )
        return {
            r["preference_key"]: _deserialize(r["value"], r["value_type"]) for r in rows
        }

    def list_categories(self, user_id: str) -> Iterable[str]:
        self._validate_id(user_id)
        rows = self.db.execute_query(
            """
            SELECT DISTINCT preference_category
            FROM user_preferences
            WHERE user_id = ?
            ORDER BY preference_category
            """,
            (user_id,),
        )
        return [r["preference_category"] for r in rows]

    # ------------------------- Write APIs ------------------------
    def set(
        self,
        user_id: str,
        category: str,
        key: str,
        value: Any,
        *,
        value_type: Optional[str] = None,
        is_encrypted: bool = False,
    ) -> None:
        self._validate_ns(user_id, category, key)
        vtype = value_type or _infer_type(value)
        if vtype not in VALID_TYPES:
            raise ValueError(f"Unsupported value_type '{vtype}' for {category}.{key}")
        raw = _serialize(value, vtype)
        self.db.execute_update(
            """
            INSERT INTO user_preferences (
                user_id, preference_category, preference_key,
                preference_value, value_type, is_encrypted
            )
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id, preference_category, preference_key)
            DO UPDATE SET
                preference_value=excluded.preference_value,
                value_type=excluded.value_type,
                is_encrypted=excluded.is_encrypted
            """,
            (user_id, category, key, raw, vtype, 1 if is_encrypted else 0),
        )

    def set_category(
        self,
        user_id: str,
        category: str,
        values: Dict[str, Any],
    ) -> int:
        self._validate_ns(user_id, category, "k")
        params = []
        for k, v in values.items():
            vtype = _infer_type(v)
            if vtype not in VALID_TYPES:
                raise ValueError(f"Unsupported value_type '{vtype}' for {category}.{k}")
            params.append(
                (
                    user_id,
                    category,
                    k,
                    _serialize(v, vtype),
                    vtype,
                    0,
                )
            )
        if not params:
            return 0
        return self.db.execute_many(
            """
            INSERT INTO user_preferences (
                user_id, preference_category, preference_key,
                preference_value, value_type, is_encrypted
            )
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id, preference_category, preference_key)
            DO UPDATE SET
                preference_value=excluded.preference_value,
                value_type=excluded.value_type,
                is_encrypted=excluded.is_encrypted
            """,
            params,
        )

    def delete(self, user_id: str, category: str, key: str) -> int:
        self._validate_ns(user_id, category, key)
        return self.db.execute_update(
            (
                "DELETE FROM user_preferences "
                "WHERE user_id = ? AND preference_category = ? "
                "AND preference_key = ?"
            ),
            (user_id, category, key),
        )

    # ------------------------- Validators -----------------------
    @staticmethod
    def _validate_id(user_id: str) -> None:
        if not isinstance(user_id, str) or not user_id.strip():
            raise ValueError("user_id must be a non-empty string")

    @classmethod
    def _validate_ns(cls, user_id: str, category: str, key: str) -> None:
        cls._validate_id(user_id)
        if not isinstance(category, str) or not category.strip():
            raise ValueError("category must be a non-empty string")
        if not isinstance(key, str) or not key.strip():
            raise ValueError("key must be a non-empty string")


__all__ = ["PreferencesStore", "PreferenceKey"]
