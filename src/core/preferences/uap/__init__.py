"""T013 — UAP package public API.

Exposes the core UAP types and service for import by the rest of the codebase.
"""

from .defaults import FACTORY_DEFAULTS, get_platform_font_family
from .models import AppearanceProfile, UAPSettings
from .service import UAPService

__all__ = [
    "UAPService",
    "AppearanceProfile",
    "UAPSettings",
    "FACTORY_DEFAULTS",
    "get_platform_font_family",
]
