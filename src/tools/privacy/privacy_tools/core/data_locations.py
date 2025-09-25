"""
Browser and system data location mappings for all supported platforms.

This module contains the paths and patterns for locating browser data
across Windows, macOS, and Linux systems.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional
from .platform_utils import PlatformUtils


class DataLocations:
    """Centralized data location mappings for browsers and system data."""

    # Browser identifiers
    CHROME = "chrome"
    FIREFOX = "firefox"
    EDGE = "edge"
    SAFARI = "safari"
    OPERA = "opera"
    BRAVE = "brave"

    @classmethod
    def get_browser_data_paths(cls, browser: str) -> Dict[str, List[Path]]:
        """Get data paths for a specific browser on current platform."""
        platform = PlatformUtils.get_platform()

        if platform == PlatformUtils.WINDOWS:
            return cls._get_windows_browser_paths(browser)
        elif platform == PlatformUtils.MACOS:
            return cls._get_macos_browser_paths(browser)
        elif platform == PlatformUtils.LINUX:
            return cls._get_linux_browser_paths(browser)

        return {}

    @classmethod
    def _get_windows_browser_paths(cls, browser: str) -> Dict[str, List[Path]]:
        """Get Windows browser data paths."""
        home = PlatformUtils.get_home_directory()
        local_appdata = PlatformUtils.get_local_appdata_directory()
        appdata = PlatformUtils.get_appdata_directory()

        paths = {}

        if browser == cls.CHROME:
            base_path = local_appdata / "Google" / "Chrome" / "User Data"
            paths = {
                "profiles": [base_path / "Default", base_path / "Profile 1"],
                "cookies": [base_path / "Default" / "Cookies"],
                "history": [base_path / "Default" / "History"],
                "downloads": [base_path / "Default" / "History"],
                "cache": [base_path / "Default" / "Cache"],
                "sessions": [base_path / "Default" / "Sessions"],
            }

        elif browser == cls.FIREFOX:
            base_path = appdata / "Mozilla" / "Firefox" / "Profiles"
            # Firefox uses profile directories with random names
            if base_path.exists():
                profile_dirs = [d for d in base_path.iterdir() if d.is_dir()]
                paths = {
                    "profiles": profile_dirs,
                    "cookies": [p / "cookies.sqlite" for p in profile_dirs],
                    "history": [p / "places.sqlite" for p in profile_dirs],
                    "downloads": [p / "places.sqlite" for p in profile_dirs],
                    "cache": [p / "cache2" for p in profile_dirs],
                    "sessions": [
                        p / "sessionstore-backups" for p in profile_dirs
                    ],
                }

        elif browser == cls.EDGE:
            base_path = local_appdata / "Microsoft" / "Edge" / "User Data"
            paths = {
                "profiles": [base_path / "Default"],
                "cookies": [base_path / "Default" / "Cookies"],
                "history": [base_path / "Default" / "History"],
                "downloads": [base_path / "Default" / "History"],
                "cache": [base_path / "Default" / "Cache"],
                "sessions": [base_path / "Default" / "Sessions"],
            }

        return paths

    @classmethod
    def _get_macos_browser_paths(cls, browser: str) -> Dict[str, List[Path]]:
        """Get macOS browser data paths."""
        home = PlatformUtils.get_home_directory()
        app_support = home / "Library" / "Application Support"

        paths = {}

        if browser == cls.CHROME:
            base_path = app_support / "Google" / "Chrome"
            paths = {
                "profiles": [base_path / "Default", base_path / "Profile 1"],
                "cookies": [base_path / "Default" / "Cookies"],
                "history": [base_path / "Default" / "History"],
                "downloads": [base_path / "Default" / "History"],
                "cache": [base_path / "Default" / "Cache"],
                "sessions": [base_path / "Default" / "Sessions"],
            }

        elif browser == cls.FIREFOX:
            base_path = app_support / "Firefox" / "Profiles"
            if base_path.exists():
                profile_dirs = [d for d in base_path.iterdir() if d.is_dir()]
                paths = {
                    "profiles": profile_dirs,
                    "cookies": [p / "cookies.sqlite" for p in profile_dirs],
                    "history": [p / "places.sqlite" for p in profile_dirs],
                    "downloads": [p / "places.sqlite" for p in profile_dirs],
                    "cache": [p / "cache2" for p in profile_dirs],
                    "sessions": [
                        p / "sessionstore-backups" for p in profile_dirs
                    ],
                }

        elif browser == cls.SAFARI:
            base_path = home / "Library" / "Safari"
            paths = {
                "profiles": [base_path],
                "cookies": [base_path / "Cookies" / "Cookies.binarycookies"],
                "history": [base_path / "History.db"],
                "downloads": [base_path / "Downloads.plist"],
                "cache": [home / "Library" / "Caches" / "com.apple.Safari"],
                "sessions": [base_path / "LastSession.plist"],
            }

        elif browser == cls.EDGE:
            base_path = app_support / "Microsoft Edge"
            paths = {
                "profiles": [base_path / "Default"],
                "cookies": [base_path / "Default" / "Cookies"],
                "history": [base_path / "Default" / "History"],
                "downloads": [base_path / "Default" / "History"],
                "cache": [base_path / "Default" / "Cache"],
                "sessions": [base_path / "Default" / "Sessions"],
            }

        return paths

    @classmethod
    def _get_linux_browser_paths(cls, browser: str) -> Dict[str, List[Path]]:
        """Get Linux browser data paths."""
        home = PlatformUtils.get_home_directory()
        config_dir = home / ".config"

        paths = {}

        if browser == cls.CHROME:
            base_path = config_dir / "google-chrome"
            paths = {
                "profiles": [base_path / "Default", base_path / "Profile 1"],
                "cookies": [base_path / "Default" / "Cookies"],
                "history": [base_path / "Default" / "History"],
                "downloads": [base_path / "Default" / "History"],
                "cache": [base_path / "Default" / "Cache"],
                "sessions": [base_path / "Default" / "Sessions"],
            }

        elif browser == cls.FIREFOX:
            base_path = home / ".mozilla" / "firefox"
            if base_path.exists():
                profile_dirs = [
                    d
                    for d in base_path.iterdir()
                    if d.is_dir() and not d.name.startswith(".")
                ]
                paths = {
                    "profiles": profile_dirs,
                    "cookies": [p / "cookies.sqlite" for p in profile_dirs],
                    "history": [p / "places.sqlite" for p in profile_dirs],
                    "downloads": [p / "places.sqlite" for p in profile_dirs],
                    "cache": [p / "cache2" for p in profile_dirs],
                    "sessions": [
                        p / "sessionstore-backups" for p in profile_dirs
                    ],
                }

        elif browser == cls.EDGE:
            base_path = config_dir / "microsoft-edge"
            paths = {
                "profiles": [base_path / "Default"],
                "cookies": [base_path / "Default" / "Cookies"],
                "history": [base_path / "Default" / "History"],
                "downloads": [base_path / "Default" / "History"],
                "cache": [base_path / "Default" / "Cache"],
                "sessions": [base_path / "Default" / "Sessions"],
            }

        return paths

    @classmethod
    def get_system_data_paths(cls) -> Dict[str, List[Path]]:
        """Get system-specific data paths for cleaning."""
        platform = PlatformUtils.get_platform()
        home = PlatformUtils.get_home_directory()

        paths = {}

        if platform == PlatformUtils.WINDOWS:
            appdata = PlatformUtils.get_appdata_directory()
            local_appdata = PlatformUtils.get_local_appdata_directory()

            paths = {
                "recent_files": [
                    appdata / "Microsoft" / "Windows" / "Recent",
                    appdata / "Microsoft" / "Office" / "Recent",
                ],
                "jump_lists": [
                    appdata
                    / "Microsoft"
                    / "Windows"
                    / "Recent"
                    / "AutomaticDestinations",
                    appdata
                    / "Microsoft"
                    / "Windows"
                    / "Recent"
                    / "CustomDestinations",
                ],
                "thumbnail_cache": [
                    local_appdata / "Microsoft" / "Windows" / "Explorer"
                ],
                "temp_files": [
                    Path(os.environ.get("TEMP", "")),
                    local_appdata / "Temp",
                ],
            }

        elif platform == PlatformUtils.MACOS:
            paths = {
                "recent_files": [
                    home
                    / "Library"
                    / "Application Support"
                    / "com.apple.sharedfilelist"
                ],
                "spotlight_cache": [
                    home / "Library" / "Metadata" / "CoreSpotlight"
                ],
                "quicklook_cache": [
                    home
                    / "Library"
                    / "Caches"
                    / "com.apple.QuickLook.thumbnailcache"
                ],
                "temp_files": [Path("/tmp"), home / "Library" / "Caches"],
            }

        elif platform == PlatformUtils.LINUX:
            paths = {
                "recent_files": [
                    home / ".local" / "share" / "recently-used.xbel",
                    home / ".recently-used",
                ],
                "thumbnail_cache": [
                    home / ".cache" / "thumbnails",
                    home / ".thumbnails",
                ],
                "temp_files": [Path("/tmp"), home / ".cache"],
            }

        return paths

    @classmethod
    def get_all_supported_browsers(cls) -> List[str]:
        """Get list of all supported browsers."""
        return [
            cls.CHROME,
            cls.FIREFOX,
            cls.EDGE,
            cls.SAFARI,
            cls.OPERA,
            cls.BRAVE,
        ]

    @classmethod
    def get_browser_executable_names(cls) -> Dict[str, List[str]]:
        """Get executable names for browsers to check if they're running."""
        return {
            cls.CHROME: ["chrome.exe", "google-chrome", "Google Chrome"],
            cls.FIREFOX: ["firefox.exe", "firefox", "Firefox"],
            cls.EDGE: ["msedge.exe", "microsoft-edge", "Microsoft Edge"],
            cls.SAFARI: ["Safari"],
            cls.OPERA: ["opera.exe", "opera", "Opera"],
            cls.BRAVE: ["brave.exe", "brave-browser", "Brave Browser"],
        }
