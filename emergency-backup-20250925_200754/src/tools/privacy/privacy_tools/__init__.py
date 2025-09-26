"""
Privacy Tools Module for Richard's File Utilities

This module provides comprehensive privacy cleaning tools that work across
Windows, macOS, and Linux platforms with support for all major browsers.

Features:
- Secure Empty Trash
- Delete Browser Cookies
- Delete Internet History
- Delete File History
- Delete Browser Downloads
"""

__version__ = "1.0.0"
__author__ = "Richard's File Utilities"

from .core.privacy_base import PrivacyToolBase
from .core.browser_detector import BrowserDetector
from .core.platform_utils import PlatformUtils

__all__ = ["PrivacyToolBase", "BrowserDetector", "PlatformUtils"]
