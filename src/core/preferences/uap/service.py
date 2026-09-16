"""T018-T026 — UAPService: core appearance management service.

Responsibilities:
  - Load / persist UAPSettings from/to PreferencesStore
  - Seed factory-default AppearanceProfile on first run (T018-B)
  - Apply UAP to a window: geometry, font, browse root (T021)
  - Cascade / centre window placement (T023)
  - Profile CRUD (T024)
  - Signal-based live propagation via ThemeManager (T025)

Governance constraints:
  P3-M02 — apply() is the final geometry step; nothing resizes after it
  A2     — save_last_used() only from closeEvent; set_font() -> set_font_preferences()
  N5     — set_font_preferences() writes ONLY font keys
  INV-002 — factory_default profile is non-deletable
  P3-H04 — "factory_default" is a sentinel, never a UUID
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Union

try:
    from PyQt5.QtGui import QFont, QFontDatabase
    from PyQt5.QtWidgets import QApplication, QMessageBox, QWidget

    _QT_AVAILABLE = True
except ImportError:
    _QT_AVAILABLE = False
    QApplication = None  # type: ignore
    QWidget = None  # type: ignore
    QFont = None  # type: ignore

# Deferred import to avoid circular dependency at module load time.
# Patched in tests as 'src.core.preferences.uap.service.ThemeManager'.
try:
    from src.gui.themes import ThemeManager
except ImportError:
    ThemeManager = None  # type: ignore

from .defaults import FACTORY_DEFAULTS, get_platform_font_family
from .models import AppearanceProfile, UAPSettings

log = logging.getLogger(__name__)

_USER_ID = "richard"
_CATEGORY = "uap"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class UAPService:
    """Unified Appearance Profile service.

    Parameters
    ----------
    store : optional PreferencesStore
        Injected for testing. Production code uses the default PreferencesStore.
    user_id : str
        User identifier for preference key scoping.
    """

    def __init__(self, store=None, user_id: str = _USER_ID) -> None:
        if store is None:
            from src.core.preferences.store import PreferencesStore

            store = PreferencesStore()
        self.store = store
        self.user_id = user_id
        self._settings: UAPSettings = UAPSettings()
        self._profiles: dict = {}
        self.load()

    # ------------------------------------------------------------------
    # T018 — load
    # ------------------------------------------------------------------

    def load(self) -> UAPSettings:
        """Load UAPSettings from store; seed factory default on first run."""
        data: dict = self.store.get_category(self.user_id, _CATEGORY) or {}

        self._settings = UAPSettings(
            mode=str(data.get("mode", FACTORY_DEFAULTS["mode"])),
            active_profile_id=str(data.get("active_profile_id", "")),
            last_used_width=int(data.get("last_used_width", FACTORY_DEFAULTS["width"])),
            last_used_height=int(
                data.get("last_used_height", FACTORY_DEFAULTS["height"])
            ),
            last_used_x=int(data.get("last_used_x", FACTORY_DEFAULTS["window_x"])),
            last_used_y=int(data.get("last_used_y", FACTORY_DEFAULTS["window_y"])),
            last_used_font_family=str(
                data.get("last_used_font_family", get_platform_font_family())
            ),
            last_used_font_size=int(
                data.get("last_used_font_size", FACTORY_DEFAULTS["font_size"])
            ),
            last_used_directory=str(data.get("last_used_directory", "")),
        )

        # Load persisted profiles
        self._profiles = {}
        for key, value in data.items():
            if key.startswith("profile:") and value:
                try:
                    profile = AppearanceProfile.from_json(str(value))
                    self._profiles[profile.profile_id] = profile
                except (json.JSONDecodeError, KeyError, ValueError) as exc:
                    log.warning("Failed to load profile '%s': %s", key, exc)

        # T018-B — seed factory default profile on first load
        if "factory_default" not in self._profiles:
            self._seed_factory_default()

        return self._settings

    def _seed_factory_default(self) -> None:
        """Seed the non-deletable factory-default AppearanceProfile (T018-B)."""
        profile = AppearanceProfile(
            profile_id="factory_default",
            profile_name="Default",
            window_width=FACTORY_DEFAULTS["width"],
            window_height=FACTORY_DEFAULTS["height"],
            window_x=FACTORY_DEFAULTS["window_x"],
            window_y=FACTORY_DEFAULTS["window_y"],
            font_family=get_platform_font_family(),
            font_size=FACTORY_DEFAULTS["font_size"],
            directory="",
            is_default=True,
            is_user_created=False,
            profile_schema_version=FACTORY_DEFAULTS["profile_schema_version"],
        )
        self._profiles["factory_default"] = profile
        self._persist_profile(profile)

    def _persist_profile(self, profile: AppearanceProfile) -> None:
        self.store.set(
            self.user_id,
            _CATEGORY,
            f"profile:{profile.profile_id}",
            profile.to_json(),
        )

    # ------------------------------------------------------------------
    # T019 — save_last_used (full-state write; only from closeEvent — A2)
    # ------------------------------------------------------------------

    def save_last_used(
        self,
        width: int,
        height: int,
        x: int,
        y: int,
        font_family: str,
        font_size: int,
        directory: str,
    ) -> None:
        """Persist all seven last_used_* keys unconditionally (BC-006, C4)."""
        self._settings.last_used_width = width
        self._settings.last_used_height = height
        self._settings.last_used_x = x
        self._settings.last_used_y = y
        self._settings.last_used_font_family = font_family
        self._settings.last_used_font_size = font_size
        self._settings.last_used_directory = directory

        self.store.set(self.user_id, _CATEGORY, "last_used_width", width)
        self.store.set(self.user_id, _CATEGORY, "last_used_height", height)
        self.store.set(self.user_id, _CATEGORY, "last_used_x", x)
        self.store.set(self.user_id, _CATEGORY, "last_used_y", y)
        self.store.set(self.user_id, _CATEGORY, "last_used_font_family", font_family)
        self.store.set(self.user_id, _CATEGORY, "last_used_font_size", font_size)
        self.store.set(self.user_id, _CATEGORY, "last_used_directory", directory)

    # ------------------------------------------------------------------
    # T020 — get_active_settings
    # ------------------------------------------------------------------

    def get_active_settings(self) -> Union[UAPSettings, AppearanceProfile]:
        """Return active settings object based on current mode."""
        if self._settings.mode == "predefined":
            profile_id = self._settings.active_profile_id
            if profile_id and profile_id in self._profiles:
                return self._profiles[profile_id]
            # Fallback to factory default
            if "factory_default" in self._profiles:
                return self._profiles["factory_default"]
        return self._settings

    # ------------------------------------------------------------------
    # T021 — apply
    # ------------------------------------------------------------------

    def apply(self, window, manifest_entry=None) -> None:
        """Apply UAP geometry, font, and browse root to a window.

        P3-M02: This is the FINAL geometry step. Nothing resizes after apply().
        U1: Font propagation uses findChildren(QWidget).
        """
        settings = self.get_active_settings()

        if isinstance(settings, AppearanceProfile):
            width = settings.window_width
            height = settings.window_height
            font_family = settings.font_family
            font_size = settings.font_size
            directory = settings.directory
        else:
            width = settings.last_used_width
            height = settings.last_used_height
            font_family = settings.last_used_font_family
            font_size = settings.last_used_font_size
            directory = settings.last_used_directory

        # Clamp to manifest minimums
        min_w = (
            getattr(manifest_entry, "min_window_width", 400) if manifest_entry else 400
        )
        min_h = (
            getattr(manifest_entry, "min_window_height", 300) if manifest_entry else 300
        )
        width = max(width, min_w)
        height = max(height, min_h)

        window.resize(width, height)

        if _QT_AVAILABLE:
            from src.rfu.font_tokens import apply_profile
            apply_profile(window, font_family, font_size)
        else:
            # Non-Qt environment (tests): pass font info directly
            window.setFont(font_family)
            for widget in window.findChildren(QWidget):
                widget.setFont(font_family)

        # Set browse root via attribute or method
        resolved = self.resolve_directory(directory)
        if hasattr(window, "set_browse_root"):
            window.set_browse_root(str(resolved))
        else:
            window._uap_browse_root = resolved

    # ------------------------------------------------------------------
    # T022 — resolve_directory
    # ------------------------------------------------------------------

    def resolve_directory(self, path: str) -> Path:
        """Resolve stored path; fall back to home if it doesn't exist (BC-002)."""
        if path:
            p = Path(path)
            if p.exists() and p.is_dir():
                return p
        log.warning("stored directory '%s' not found - using home directory", path)
        return Path.home()

    # ------------------------------------------------------------------
    # T023 — place_window
    # ------------------------------------------------------------------

    def place_window(self, window, open_windows: Optional[list] = None) -> None:
        """Place window using stored coords, cascade, or centre (FR-023)."""
        if open_windows is None:
            open_windows = []

        x = self._settings.last_used_x
        y = self._settings.last_used_y

        # Explicit stored position
        if x != -1 and y != -1:
            window.move(x, y)
            return

        # Cascade: offset from the last open window
        if open_windows:
            last = open_windows[-1]
            pos = last.pos()
            window.move(pos.x() + 20, pos.y() + 20)
            return

        # Centre on primary screen
        if _QT_AVAILABLE and QApplication is not None:
            screen = QApplication.primaryScreen()
            if screen is not None:
                geom = screen.availableGeometry()
                center = geom.center()
                try:
                    w = window.width()
                    h = window.height()
                except Exception:
                    w = self._settings.last_used_width
                    h = self._settings.last_used_height
                window.move(center.x() - w // 2, center.y() - h // 2)
                return

        # Fallback: no-op
        window.move(0, 0)

    # ------------------------------------------------------------------
    # T024 — Profile CRUD
    # ------------------------------------------------------------------

    def create_profile(self, name: str) -> AppearanceProfile:
        """Create a new user profile inheriting current last-used values."""
        profile_id = str(uuid.uuid4())
        profile = AppearanceProfile(
            profile_id=profile_id,
            profile_name=name,
            window_width=self._settings.last_used_width,
            window_height=self._settings.last_used_height,
            window_x=self._settings.last_used_x,
            window_y=self._settings.last_used_y,
            font_family=self._settings.last_used_font_family,
            font_size=self._settings.last_used_font_size,
            directory=self._settings.last_used_directory,
            is_default=False,
            is_user_created=True,
        )
        self._profiles[profile_id] = profile
        self._persist_profile(profile)
        return profile

    def get_profile(self, profile_id: str) -> AppearanceProfile:
        return self._profiles[profile_id]

    def list_profiles(self) -> List[AppearanceProfile]:
        return list(self._profiles.values())

    def rename_profile(self, profile_id: str, new_name: str) -> None:
        profile = self._profiles[profile_id]
        profile.profile_name = new_name
        profile.updated_at = _now_iso()
        self._persist_profile(profile)

    def duplicate_profile(self, profile_id: str, new_name: str) -> AppearanceProfile:
        original = self._profiles[profile_id]
        new_id = str(uuid.uuid4())
        dup = AppearanceProfile(
            profile_id=new_id,
            profile_name=new_name,
            window_width=original.window_width,
            window_height=original.window_height,
            window_x=original.window_x,
            window_y=original.window_y,
            font_family=original.font_family,
            font_size=original.font_size,
            directory=original.directory,
            is_default=False,
            is_user_created=True,
        )
        self._profiles[new_id] = dup
        self._persist_profile(dup)
        return dup

    def delete_profile(self, profile_id: str) -> None:
        """Delete a profile. Raises ValueError for factory_default or last profile (INV-002)."""
        if profile_id == "factory_default":
            raise ValueError(
                "The factory-default profile cannot be deleted (INV-002). "
                "Deletion guard checks profile_id sentinel, not profile_name."
            )
        if len(self._profiles) <= 1:
            raise ValueError("Cannot delete the last remaining profile (INV-002).")
        del self._profiles[profile_id]
        # Nullify the persisted key
        self.store.set(self.user_id, _CATEGORY, f"profile:{profile_id}", None)

    def set_active_profile(self, profile_id: str) -> None:
        """Set active profile and switch mode to predefined."""
        self._settings.active_profile_id = profile_id
        self._settings.mode = "predefined"
        self.store.set(self.user_id, _CATEGORY, "active_profile_id", profile_id)
        self.store.set(self.user_id, _CATEGORY, "mode", "predefined")

    # ------------------------------------------------------------------
    # T025 — signal methods
    # ------------------------------------------------------------------

    def set_font(self, family: str, size: int) -> None:
        """Clamp size to [6,32]; persist font fields only; emit signal (BC-004, A2).

        MUST NOT call save_last_used() — that is a closeEvent-only operation.
        """
        size = max(6, min(32, size))
        self.set_font_preferences(family, size)
        if ThemeManager is not None:
            try:
                ThemeManager.instance().uap_font_changed.emit(family, size)
            except AttributeError:
                # ThemeManager not yet a QObject — T042 pending
                pass

    def set_font_preferences(self, font_family: str, font_size: int) -> None:
        """Persist ONLY last_used_font_family and last_used_font_size (N5, A2).

        MUST NOT touch geometry, directory, or any other appearance field.
        """
        self._settings.last_used_font_family = font_family
        self._settings.last_used_font_size = font_size
        self.store.set(self.user_id, _CATEGORY, "last_used_font_family", font_family)
        self.store.set(self.user_id, _CATEGORY, "last_used_font_size", font_size)

    def set_geometry(self, width: int, height: int, x: int, y: int) -> None:
        """Persist geometry fields only; emit signal (BC-006c, I4)."""
        self._settings.last_used_width = width
        self._settings.last_used_height = height
        self._settings.last_used_x = x
        self._settings.last_used_y = y
        self.store.set(self.user_id, _CATEGORY, "last_used_width", width)
        self.store.set(self.user_id, _CATEGORY, "last_used_height", height)
        self.store.set(self.user_id, _CATEGORY, "last_used_x", x)
        self.store.set(self.user_id, _CATEGORY, "last_used_y", y)
        if ThemeManager is not None:
            try:
                ThemeManager.instance().uap_geometry_changed.emit(width, height, x, y)
            except AttributeError:
                pass

    def set_directory(self, path: str) -> None:
        """Persist last-used directory only; MUST NOT touch geometry (BC-006b, I4)."""
        self._settings.last_used_directory = path
        self.store.set(self.user_id, _CATEGORY, "last_used_directory", path)

    # ------------------------------------------------------------------
    # T026 — import_profile
    # ------------------------------------------------------------------

    def import_profile(self, data: str) -> AppearanceProfile:
        """Parse and import an AppearanceProfile from JSON (FR-026).

        Geometry normalization is NOT performed here (G3): undersized values
        are only clamped at apply-time (T021).
        """
        profile = AppearanceProfile.from_json(data)

        resets = []

        # Check directory exists
        if profile.directory and not Path(profile.directory).exists():
            resets.append(
                f"working_directory '{profile.directory}' not found — reset to empty"
            )
            profile.directory = ""

        # Check font available
        if _QT_AVAILABLE:
            db = QFontDatabase()
            available = db.families()
            if profile.font_family not in available:
                resets.append(
                    f"font_family '{profile.font_family}' not available — reset to platform default"
                )
                profile.font_family = get_platform_font_family()

        # Warn user about resets
        if resets and _QT_AVAILABLE:
            msg = "The following incompatible fields were reset during import:\n\n"
            msg += "\n".join(f"• {r}" for r in resets)
            QMessageBox.warning(None, "Profile Import — Fields Reset", msg)

        # Assign new ID for user-created imported profile
        if not profile.is_user_created:
            profile.is_user_created = True

        # Don't overwrite factory_default sentinel
        if profile.profile_id == "factory_default":
            profile.profile_id = str(uuid.uuid4())

        profile.updated_at = _now_iso()
        self._profiles[profile.profile_id] = profile
        self._persist_profile(profile)
        return profile


__all__ = ["UAPService"]
