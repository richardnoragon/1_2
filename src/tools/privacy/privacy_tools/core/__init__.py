"""
Core utilities for Privacy Tools module.

This package contains the foundational classes and utilities used by all privacy tools.
"""

from .privacy_base import PrivacyToolBase
from .browser_detector import BrowserDetector
from .platform_utils import PlatformUtils
from .data_locations import DataLocations

__all__ = [
    "PrivacyToolBase",
    "BrowserDetector",
    "PlatformUtils",
    "DataLocations",
]
