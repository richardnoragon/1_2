"""Utility helpers shared across auth model dataclasses."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, Mapping, Sequence


def parse_datetime(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, (bytes, bytearray)):
        try:
            value = value.decode("utf-8")
        except Exception:
            return None
    text = str(value).strip()
    if not text:
        return None
    normalized = text.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None


def datetime_to_iso(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.replace(microsecond=0).isoformat()


def bool_from_db(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    if isinstance(value, (int, float)):
        return value != 0
    text = str(value).strip().lower()
    return text in {"1", "true", "t", "yes", "y"}


def json_to_dict(value: Any) -> Dict[str, Any] | None:
    if value in (None, ""):
        return None
    if isinstance(value, Mapping):
        return dict(value)
    if isinstance(value, (bytes, bytearray)):
        try:
            value = value.decode("utf-8")
        except Exception:
            return None
    try:
        payload = json.loads(value)
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None


def json_to_list(value: Any) -> Sequence[str] | None:
    if value in (None, ""):
        return None
    if isinstance(value, (list, tuple)):
        return tuple(str(item) for item in value)
    if isinstance(value, (bytes, bytearray)):
        try:
            value = value.decode("utf-8")
        except Exception:
            return None
    try:
        payload = json.loads(value)
    except Exception:
        return None
    if isinstance(payload, list):
        return tuple(str(item) for item in payload)
    return None


def dict_to_json(value: Mapping[str, Any] | None) -> str | None:
    if not value:
        return None
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def list_to_json(values: Sequence[str] | None) -> str | None:
    if not values:
        return None
    return json.dumps(list(values), ensure_ascii=False)
