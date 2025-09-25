"""
Browser detection utilities for privacy tools.

This module provides functionality to detect installed browsers,
check if they're running, and manage browser-specific operations.
"""

import os
from pathlib import Path
from typing import List, Dict, Set
from .platform_utils import PlatformUtils
from .data_locations import DataLocations


class BrowserDetector:
    """Utility class for detecting and managing browsers."""

    def __init__(self):
        """Initialize the browser detector."""
        self.platform = PlatformUtils.get_platform()
        self._detected_browsers = None
        self._browser_paths = {}

    def detect_installed_browsers(self) -> List[str]:
        """Detect all installed browsers on the system."""
        if self._detected_browsers is not None:
            return self._detected_browsers

        detected = []

        for browser in DataLocations.get_all_supported_browsers():
            if self._is_browser_installed(browser):
                detected.append(browser)

        self._detected_browsers = detected
        return detected

    def _is_browser_installed(self, browser: str) -> bool:
        """Check if a specific browser is installed."""
        if self.platform == PlatformUtils.WINDOWS:
            return self._check_windows_browser(browser)
        elif self.platform == PlatformUtils.MACOS:
            return self._check_macos_browser(browser)
        elif self.platform == PlatformUtils.LINUX:
            return self._check_linux_browser(browser)
        return False

    def _check_windows_browser(self, browser: str) -> bool:
        """Check if browser is installed on Windows."""
        home = PlatformUtils.get_home_directory()
        local_appdata = PlatformUtils.get_local_appdata_directory()
        appdata = PlatformUtils.get_appdata_directory()

        if not local_appdata or not appdata:
            return False

        if browser == DataLocations.CHROME:
            chrome_path = local_appdata / "Google" / "Chrome"
            return chrome_path.exists()

        elif browser == DataLocations.FIREFOX:
            firefox_path = appdata / "Mozilla" / "Firefox"
            return firefox_path.exists()

        elif browser == DataLocations.EDGE:
            edge_path = local_appdata / "Microsoft" / "Edge"
            return edge_path.exists()

        return False

    def _check_macos_browser(self, browser: str) -> bool:
        """Check if browser is installed on macOS."""
        home = PlatformUtils.get_home_directory()
        app_support = home / "Library" / "Application Support"
        applications = Path("/Applications")

        if browser == DataLocations.CHROME:
            return (applications / "Google Chrome.app").exists() or (
                app_support / "Google" / "Chrome"
            ).exists()

        elif browser == DataLocations.FIREFOX:
            return (applications / "Firefox.app").exists() or (
                app_support / "Firefox"
            ).exists()

        elif browser == DataLocations.SAFARI:
            return (applications / "Safari.app").exists() or (
                home / "Library" / "Safari"
            ).exists()

        elif browser == DataLocations.EDGE:
            return (applications / "Microsoft Edge.app").exists() or (
                app_support / "Microsoft Edge"
            ).exists()

        return False

    def _check_linux_browser(self, browser: str) -> bool:
        """Check if browser is installed on Linux."""
        home = PlatformUtils.get_home_directory()
        config_dir = home / ".config"

        if browser == DataLocations.CHROME:
            return (
                config_dir / "google-chrome"
            ).exists() or self._check_command_exists("google-chrome")

        elif browser == DataLocations.FIREFOX:
            return (
                home / ".mozilla" / "firefox"
            ).exists() or self._check_command_exists("firefox")

        elif browser == DataLocations.EDGE:
            return (
                config_dir / "microsoft-edge"
            ).exists() or self._check_command_exists("microsoft-edge")

        return False

    def _check_command_exists(self, command: str) -> bool:
        """Check if a command exists in PATH."""
        import shutil

        return shutil.which(command) is not None

    def get_running_browsers(self) -> List[str]:
        """Get list of currently running browsers."""
        running = []
        executable_names = DataLocations.get_browser_executable_names()

        for browser in self.detect_installed_browsers():
            if browser in executable_names:
                for exe_name in executable_names[browser]:
                    if PlatformUtils.is_process_running(exe_name):
                        running.append(browser)
                        break

        return running

    def is_browser_running(self, browser: str) -> bool:
        """Check if a specific browser is currently running."""
        return browser in self.get_running_browsers()

    def close_browser(self, browser: str) -> bool:
        """Attempt to close a running browser."""
        if not self.is_browser_running(browser):
            return True

        executable_names = DataLocations.get_browser_executable_names()
        if browser not in executable_names:
            return False

        success = True
        for exe_name in executable_names[browser]:
            if PlatformUtils.is_process_running(exe_name):
                if not PlatformUtils.kill_process(exe_name):
                    success = False

        return success

    def get_browser_data_paths(self, browser: str) -> Dict[str, List[Path]]:
        """Get data paths for a specific browser."""
        if browser not in self._browser_paths:
            self._browser_paths[browser] = (
                DataLocations.get_browser_data_paths(browser)
            )
        return self._browser_paths[browser]

    def get_browser_profile_paths(self, browser: str) -> List[Path]:
        """Get profile paths for a specific browser."""
        data_paths = self.get_browser_data_paths(browser)
        return data_paths.get("profiles", [])

    def validate_browser_access(self, browser: str) -> Dict[str, bool]:
        """Validate access to browser data files."""
        results = {}
        data_paths = self.get_browser_data_paths(browser)

        for data_type, paths in data_paths.items():
            accessible = True
            for path in paths:
                if path.exists():
                    try:
                        # Try to access the file/directory
                        if path.is_file():
                            with open(path, "rb") as f:
                                f.read(1)
                        elif path.is_dir():
                            list(path.iterdir())
                    except (PermissionError, OSError):
                        accessible = False
                        break
            results[data_type] = accessible

        return results

    def get_browser_info(self, browser: str) -> Dict[str, any]:
        """Get comprehensive information about a browser."""
        return {
            "name": browser,
            "installed": browser in self.detect_installed_browsers(),
            "running": self.is_browser_running(browser),
            "data_paths": self.get_browser_data_paths(browser),
            "access_status": self.validate_browser_access(browser),
        }

    def get_all_browser_info(self) -> Dict[str, Dict[str, any]]:
        """Get information about all detected browsers."""
        info = {}
        for browser in self.detect_installed_browsers():
            info[browser] = self.get_browser_info(browser)
        return info

    def refresh_detection(self) -> None:
        """Refresh browser detection cache."""
        self._detected_browsers = None
        self._browser_paths.clear()
