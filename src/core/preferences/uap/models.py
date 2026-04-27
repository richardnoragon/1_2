"""T015-T017 — AppearanceProfile and UAPSettings data models.

Invariants enforced here:
    INV-006 — window_x and window_y must both be -1 OR both be >= 0
    Field validation — width >= 400, height >= 300, font_size in [6, 32],
                       window_x >= -1, window_y >= -1
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from .defaults import FACTORY_DEFAULTS, get_platform_font_family


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# T015-T016 — AppearanceProfile
# ---------------------------------------------------------------------------


@dataclass
class AppearanceProfile:
    profile_id: str
    profile_name: str
    window_width: int
    window_height: int
    font_family: str
    font_size: int
    is_default: bool
    window_x: int = -1
    window_y: int = -1
    # directory maps to 'working_directory' in the JSON schema (INV-003)
    directory: str = ""
    created_at: str = field(default_factory=_now_iso)
    updated_at: str = field(default_factory=_now_iso)
    profile_schema_version: int = 2
    is_user_created: bool = False

    def __post_init__(self) -> None:
        if self.window_width < 400:
            raise ValueError(f"window_width must be >= 400, got {self.window_width}")
        if self.window_height < 300:
            raise ValueError(f"window_height must be >= 300, got {self.window_height}")
        if not (6 <= self.font_size <= 32):
            raise ValueError(f"font_size must be in [6, 32], got {self.font_size}")
        if self.window_x < -1:
            raise ValueError(f"window_x must be >= -1, got {self.window_x}")
        if self.window_y < -1:
            raise ValueError(f"window_y must be >= -1, got {self.window_y}")
        # INV-006 — mixed sentinel: both must be -1 OR both must be >= 0
        if (self.window_x == -1) != (self.window_y == -1):
            raise ValueError(
                "mixed sentinel: window_x and window_y must both be -1 "
                "or both be non-negative"
            )

    # T016 — serialisation
    def to_json(self) -> str:
        data = {
            "profile_id": self.profile_id,
            "profile_name": self.profile_name,
            "is_default": self.is_default,
            "window_width": self.window_width,
            "window_height": self.window_height,
            "window_x": self.window_x,
            "window_y": self.window_y,
            "font_family": self.font_family,
            "font_size": self.font_size,
            "working_directory": self.directory,
            "created_at": self.created_at,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "profile_schema_version": self.profile_schema_version,
            "is_user_created": self.is_user_created,
        }
        return json.dumps(data)

    @classmethod
    def from_json(cls, s: str) -> "AppearanceProfile":
        data = json.loads(s)

        # G2 — schema migration
        schema_version = data.get("profile_schema_version", 1)
        if schema_version < 2:
            # v1 → v2: profile_schema_version field was not persisted in v1
            data["profile_schema_version"] = 2

        # Resolve working_directory → directory (backward compat for both key names)
        directory = data.get("working_directory", data.get("directory", ""))

        return cls(
            profile_id=data["profile_id"],
            profile_name=data["profile_name"],
            window_width=int(data["window_width"]),
            window_height=int(data["window_height"]),
            window_x=int(data.get("window_x", -1)),
            window_y=int(data.get("window_y", -1)),
            font_family=data["font_family"],
            font_size=int(data["font_size"]),
            directory=directory,
            is_default=bool(data["is_default"]),
            is_user_created=bool(data.get("is_user_created", False)),
            created_at=data.get("created_at", _now_iso()),
            updated_at=data.get("updated_at", _now_iso()),
            profile_schema_version=int(data["profile_schema_version"]),
        )


# ---------------------------------------------------------------------------
# T017 — UAPSettings
# ---------------------------------------------------------------------------


@dataclass
class UAPSettings:
    """Runtime-readable aggregate of the user's current UAP state.

    Note (C4): last_used_* values are always kept current regardless of mode.
    In predefined mode the hub applies the active profile on open but continues
    to silently record the user's actual usage in last_used_*.
    """

    mode: str = FACTORY_DEFAULTS["mode"]
    active_profile_id: str = ""
    last_used_width: int = FACTORY_DEFAULTS["width"]
    last_used_height: int = FACTORY_DEFAULTS["height"]
    last_used_x: int = FACTORY_DEFAULTS["window_x"]
    last_used_y: int = FACTORY_DEFAULTS["window_y"]
    last_used_font_family: str = field(default_factory=get_platform_font_family)
    last_used_font_size: int = FACTORY_DEFAULTS["font_size"]
    last_used_directory: str = ""

    def __post_init__(self) -> None:
        if self.mode not in ("last_used", "predefined"):
            raise ValueError(
                f"mode must be 'last_used' or 'predefined', got {self.mode!r}"
            )


__all__ = ["AppearanceProfile", "UAPSettings"]
