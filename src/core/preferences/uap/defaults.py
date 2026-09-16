"""T014 — Platform-aware font defaults and FACTORY_DEFAULTS.

profile_schema_version is a per-profile field (N1). It is NOT a top-level uap.* key.
"""

import sys


def get_platform_font_family() -> str:
    """Return the canonical system UI font for the current platform."""
    if sys.platform == "win32":
        return "Segoe UI"
    elif sys.platform == "darwin":
        return "Helvetica Neue"
    else:
        return "DejaVu Sans"


FACTORY_DEFAULTS: dict = {
    "width": 1000,
    "height": 700,
    "font_size": 14,
    "mode": "last_used",
    "window_x": -1,
    "window_y": -1,
    # profile_schema_version is per-profile, but stored here for reference by T018-B
    "profile_schema_version": 2,
}


__all__ = ["get_platform_font_family", "FACTORY_DEFAULTS"]
