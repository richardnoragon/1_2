"""High-level PreferenceManager built on PreferencesStore.

This module provides a convenient, typed wrapper around the low-level
PreferencesStore for common RFU user personalization use cases:

- Universal theming: get/set active theme and theme profiles
- Favorites: add/list/remove favorites (paths, tools)
- Directory preferences: default roots, recents, visibility flags
- Generic get/set with automatic user_id and namespacing

Design goals
- Separation of concerns: consumer modules depend on this API, not DB
- Backward compatibility: safe to adopt incrementally alongside JSON config
- Extensibility: new categories/keys do not affect existing modules

Security
- No secrets are stored here; callers may pass is_encrypted=True for
  sensitive values (envelope encryption handled upstream when added)

"""

from __future__ import annotations

import getpass
import hashlib
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .store import PreferencesStore

DEFAULT_USER_ID = "default"


def _current_user_id() -> str:
    """Resolve the active preference user identifier.

    Resolution order:
    1. `RFU_USER_ID` environment variable (trimmed, must be non-empty)
    2. Operating system account via ``getpass.getuser()``
    3. Static fallback ``"default"`` to guarantee a stable namespace
    """

    override = os.getenv("RFU_USER_ID")
    if override and override.strip():
        return override.strip()

    try:
        uid = getpass.getuser().strip()
        if uid:
            return uid
    except Exception:  # noqa: BLE001 - best-effort resolution only
        pass

    return DEFAULT_USER_ID


class PreferenceManager:
    """High-level, user-scoped preference operations.

    Category conventions (kebab-case):
    - theming: keys [theme, profile, overrides]
    - favorites: keys prefixed with kind (tool:, path:)
    - directories: keys [default_root, recent, show_hidden]
    - module_settings/<module>: arbitrary module-owned settings (json)
    """

    def __init__(
        self,
        store: Optional[PreferencesStore] = None,
        *,
        user_id: Optional[str] = None,
    ) -> None:
        self.store = store or PreferencesStore()
        self.user_id = user_id or _current_user_id()

    # ---------------------- Generic accessors ----------------------
    def get(self, category: str, key: str, default: Any = None) -> Any:
        return self.store.get(self.user_id, category, key, default)

    def set(
        self,
        category: str,
        key: str,
        value: Any,
        *,
        is_encrypted: bool = False,
    ) -> None:
        self.store.set(
            self.user_id,
            category,
            key,
            value,
            is_encrypted=is_encrypted,
        )

    def get_category(self, category: str) -> Dict[str, Any]:
        return self.store.get_category(self.user_id, category)

    # ---------------------- Theming ----------------------
    def get_theme(self, default: str = "light") -> str:
        value = self.get("theming", "theme", default)
        return str(value or default)

    def set_theme(self, theme: str) -> None:
        theme = str(theme).strip().lower()
        if theme not in {"light", "dark"}:
            # Allow arbitrary names for future theme packs, but keep a guard
            # for typos
            if len(theme) == 0:
                theme = "light"
        self.set("theming", "theme", theme)

    # Theme profile management (named presets)
    def save_theme_profile(self, name: str, data: Dict[str, Any]) -> None:
        self.set("theming", f"profile:{name}", data)

    def load_theme_profile(
        self,
        name: str,
        default: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        value = self.get("theming", f"profile:{name}", default)
        return value if isinstance(value, dict) else default

    def list_theme_profiles(self) -> List[str]:
        items = self.get_category("theming")
        return sorted(
            [k.split(":", 1)[1] for k in items.keys() if k.startswith("profile:")]
        )

    # ---------------------- Favorites ----------------------
    @staticmethod
    def _path_key(path: str) -> str:
        # Normalize and hash for stable key
        p = str(Path(path))
        digest = hashlib.sha256(p.encode("utf-8")).hexdigest()[:16]
        return f"path:{digest}"

    def add_favorite_path(
        self,
        path: str,
        *,
        label: Optional[str] = None,
    ) -> None:
        self.set(
            "favorites",
            self._path_key(path),
            {"path": str(Path(path)), "label": label or Path(path).name},
        )

    def remove_favorite_path(self, path: str) -> int:
        key = self._path_key(path)
        return self.store.delete(self.user_id, "favorites", key)

    def list_favorite_paths(self) -> List[Dict[str, Any]]:
        cat = self.get_category("favorites")
        results = []
        for key, value in cat.items():
            if (
                key.startswith("path:")
                and isinstance(value, dict)
                and value.get("path")
            ):
                results.append(value)
        return results

    def add_favorite_tool(
        self, tool_name: str, *, module: Optional[str] = None
    ) -> None:
        self.set(
            "favorites",
            f"tool:{tool_name}",
            {"tool": tool_name, "module": module},
        )

    def remove_favorite_tool(self, tool_name: str) -> int:
        key = f"tool:{tool_name}"
        return self.store.delete(self.user_id, "favorites", key)

    def list_favorite_tools(self) -> List[Dict[str, Any]]:
        cat = self.get_category("favorites")
        results = []
        for key, value in cat.items():
            if (
                key.startswith("tool:")
                and isinstance(value, dict)
                and value.get("tool")
            ):
                results.append(value)
        return results

    # ---------------------- Directories ----------------------
    def get_directory_prefs(self) -> Dict[str, Any]:
        # keys: default_root (str), recent (list[str]), show_hidden (bool)
        cat = self.get_category("directories")
        return {
            "default_root": str(cat.get("default_root") or ""),
            "recent": list(cat.get("recent") or []),
            "show_hidden": bool(cat.get("show_hidden") or False),
        }

    def set_directory_prefs(
        self,
        *,
        default_root: Optional[str] = None,
        recent: Optional[Iterable[str]] = None,
        show_hidden: Optional[bool] = None,
    ) -> None:
        updates: Dict[str, Any] = {}
        if default_root is not None:
            updates["default_root"] = str(default_root)
        if recent is not None:
            updates["recent"] = list(map(str, recent))
        if show_hidden is not None:
            updates["show_hidden"] = bool(show_hidden)
        if updates:
            self.store.set_category(self.user_id, "directories", updates)

    # ---------------------- UAP (Unified Appearance Profile) ----------------------
    def get_uap_settings(self) -> "UAPSettings":
        from src.core.preferences.uap.service import UAPService

        svc = UAPService(store=self.store, user_id=self.user_id)
        return svc.load()

    def save_uap_settings(self, settings: "UAPSettings") -> None:
        from src.core.preferences.uap.service import UAPService

        svc = UAPService(store=self.store, user_id=self.user_id)
        svc.save_last_used(
            width=settings.last_used_width,
            height=settings.last_used_height,
            x=settings.last_used_x,
            y=settings.last_used_y,
            font_family=settings.last_used_font_family,
            font_size=settings.last_used_font_size,
            directory=settings.last_used_directory,
        )


__all__ = ["PreferenceManager"]
