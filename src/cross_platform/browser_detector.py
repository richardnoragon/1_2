#!/usr/bin/env python3
"""Cross-Platform Browser Detection Utilities.

This module provides comprehensive browser detection across Windows, Linux,
and macOS platforms with support for major browsers and security compliance.
"""

import json
import logging
import platform
import re
import subprocess
import sys
import tempfile
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


@dataclass
class BrowserInfo:
    """Information about a detected browser."""

    name: str
    version: Optional[str] = None
    executable_path: Optional[str] = None
    profile_paths: List[str] = None
    is_default: bool = False
    architecture: Optional[str] = None
    last_modified: Optional[str] = None

    def __post_init__(self):
        if self.profile_paths is None:
            self.profile_paths = []


@dataclass
class BrowserProfile:
    """Information about a browser profile."""

    browser_name: str
    profile_name: str
    profile_path: str
    user_data_dir: str
    is_default: bool = False
    last_used: Optional[str] = None


class BrowserDetector(ABC):
    """Abstract base class for platform-specific browser detectors."""

    def __init__(self, platform_name: str):
        self.platform_name = platform_name
        self.logger = logging.getLogger(f"BrowserDetector.{platform_name}")

    @abstractmethod
    def detect_browsers(self) -> List[BrowserInfo]:
        """Detect all installed browsers on this platform."""
        pass

    @abstractmethod
    def get_browser_profiles(self, browser_name: str) -> List[BrowserProfile]:
        """Get profiles for a specific browser."""
        pass

    @abstractmethod
    def get_default_browser(self) -> Optional[BrowserInfo]:
        """Get the default browser on this platform."""
        pass


class WindowsBrowserDetector(BrowserDetector):
    """Browser detector for Windows platforms."""

    def __init__(self):
        super().__init__("Windows")
        self.registry_paths = {
            "chrome": [
                r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe",
                r"HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe",
            ],
            "firefox": [
                r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\firefox.exe",
                r"HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths\firefox.exe",
            ],
            "edge": [
                r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\msedge.exe"
            ],
            "opera": [
                r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\opera.exe"
            ],
            "brave": [
                r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\brave.exe"
            ],
        }

    def detect_browsers(self) -> List[BrowserInfo]:
        """Detect browsers using Windows registry and file system."""
        browsers = []

        # Registry-based detection
        for browser_name, reg_paths in self.registry_paths.items():
            browser_info = self._detect_browser_from_registry(
                browser_name, reg_paths
            )
            if browser_info:
                browsers.append(browser_info)

        # File system-based detection for additional locations
        browsers.extend(self._detect_browsers_from_filesystem())

        # Remove duplicates
        unique_browsers = self._remove_duplicate_browsers(browsers)

        # Get versions for detected browsers
        for browser in unique_browsers:
            if browser.executable_path:
                browser.version = self._get_browser_version(browser)

        return unique_browsers

    def _detect_browser_from_registry(
        self, browser_name: str, registry_paths: List[str]
    ) -> Optional[BrowserInfo]:
        """Detect browser from Windows registry."""
        try:
            import winreg

            for reg_path in registry_paths:
                try:
                    # Parse registry path
                    parts = reg_path.split("\\", 1)
                    hive_name = parts[0]
                    key_path = parts[1].rsplit("\\", 1)[0]

                    # Map hive names to constants
                    hive_map = {
                        "HKEY_LOCAL_MACHINE": winreg.HKEY_LOCAL_MACHINE,
                        "HKEY_CURRENT_USER": winreg.HKEY_CURRENT_USER,
                    }

                    hive = hive_map.get(hive_name)
                    if not hive:
                        continue

                    # Open registry key
                    with winreg.OpenKey(hive, key_path) as key:
                        executable_path = winreg.QueryValue(key, "")

                        if executable_path and Path(executable_path).exists():
                            return BrowserInfo(
                                name=browser_name,
                                executable_path=executable_path,
                            )

                except (OSError, FileNotFoundError):
                    continue

            return None

        except ImportError:
            self.logger.warning(
                "winreg module not available, skipping registry detection"
            )
            return None

    def _detect_browsers_from_filesystem(self) -> List[BrowserInfo]:
        """Detect browsers from common installation paths."""
        browsers = []

        # Common installation paths
        common_paths = {
            "chrome": [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                Path.home()
                / "AppData"
                / "Local"
                / "Google"
                / "Chrome"
                / "Application"
                / "chrome.exe",
            ],
            "firefox": [
                r"C:\Program Files\Mozilla Firefox\firefox.exe",
                r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
            ],
            "edge": [
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            ],
            "opera": [
                Path.home()
                / "AppData"
                / "Local"
                / "Programs"
                / "Opera"
                / "opera.exe"
            ],
            "brave": [
                r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
                r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
                Path.home()
                / "AppData"
                / "Local"
                / "BraveSoftware"
                / "Brave-Browser"
                / "Application"
                / "brave.exe",
            ],
        }

        for browser_name, paths in common_paths.items():
            for path in paths:
                if isinstance(path, str):
                    path = Path(path)

                if path.exists():
                    browsers.append(
                        BrowserInfo(
                            name=browser_name, executable_path=str(path)
                        )
                    )
                    break  # Found one, move to next browser

        return browsers

    def _remove_duplicate_browsers(
        self, browsers: List[BrowserInfo]
    ) -> List[BrowserInfo]:
        """Remove duplicate browser entries."""
        seen_browsers = {}
        unique_browsers = []

        for browser in browsers:
            key = (browser.name, browser.executable_path)
            if key not in seen_browsers:
                seen_browsers[key] = browser
                unique_browsers.append(browser)

        return unique_browsers

    def _get_browser_version(self, browser: BrowserInfo) -> Optional[str]:
        """Get browser version from executable."""
        try:
            if (
                not browser.executable_path
                or not Path(browser.executable_path).exists()
            ):
                return None

            # Try to get version info from executable
            result = subprocess.run(
                [
                    "powershell",
                    "-Command",
                    f"(Get-ItemProperty '{browser.executable_path}').VersionInfo.FileVersion",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()

            # Alternative method: run browser with version flag
            version_flags = {
                "chrome": "--version",
                "firefox": "--version",
                "edge": "--version",
                "opera": "--version",
                "brave": "--version",
            }

            flag = version_flags.get(browser.name)
            if flag:
                result = subprocess.run(
                    [browser.executable_path, flag],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                if result.returncode == 0:
                    # Extract version number from output
                    version_match = re.search(
                        r"(\d+\.\d+\.\d+)", result.stdout
                    )
                    if version_match:
                        return version_match.group(1)

            return None

        except Exception as e:
            self.logger.debug(f"Failed to get version for {browser.name}: {e}")
            return None

    def get_browser_profiles(self, browser_name: str) -> List[BrowserProfile]:
        """Get browser profiles for Windows."""
        profiles = []

        profile_paths = {
            "chrome": Path.home()
            / "AppData"
            / "Local"
            / "Google"
            / "Chrome"
            / "User Data",
            "firefox": Path.home()
            / "AppData"
            / "Roaming"
            / "Mozilla"
            / "Firefox"
            / "Profiles",
            "edge": Path.home()
            / "AppData"
            / "Local"
            / "Microsoft"
            / "Edge"
            / "User Data",
            "opera": Path.home()
            / "AppData"
            / "Roaming"
            / "Opera Software"
            / "Opera Stable",
            "brave": Path.home()
            / "AppData"
            / "Local"
            / "BraveSoftware"
            / "Brave-Browser"
            / "User Data",
        }

        base_path = profile_paths.get(browser_name.lower())
        if not base_path or not base_path.exists():
            return profiles

        try:
            if browser_name.lower() == "firefox":
                # Firefox uses profiles.ini
                profiles_ini = base_path.parent / "profiles.ini"
                if profiles_ini.exists():
                    profiles.extend(self._parse_firefox_profiles(profiles_ini))
            else:
                # Chromium-based browsers use User Data directories
                for item in base_path.iterdir():
                    if item.is_dir() and (
                        item.name.startswith("Profile")
                        or item.name == "Default"
                    ):
                        profiles.append(
                            BrowserProfile(
                                browser_name=browser_name,
                                profile_name=item.name,
                                profile_path=str(item),
                                user_data_dir=str(base_path),
                                is_default=(item.name == "Default"),
                            )
                        )

        except Exception as e:
            self.logger.error(
                f"Error getting profiles for {browser_name}: {e}"
            )

        return profiles

    def _parse_firefox_profiles(
        self, profiles_ini: Path
    ) -> List[BrowserProfile]:
        """Parse Firefox profiles.ini file."""
        profiles = []

        try:
            import configparser

            config = configparser.ConfigParser()
            config.read(profiles_ini)

            for section_name in config.sections():
                if section_name.startswith("Profile"):
                    section = config[section_name]
                    name = section.get("Name", "Unknown")
                    path = section.get("Path", "")
                    is_relative = section.getboolean("IsRelative", True)
                    is_default = section.getboolean("Default", False)

                    if path:
                        if is_relative:
                            profile_path = profiles_ini.parent / path
                        else:
                            profile_path = Path(path)

                        if profile_path.exists():
                            profiles.append(
                                BrowserProfile(
                                    browser_name="firefox",
                                    profile_name=name,
                                    profile_path=str(profile_path),
                                    user_data_dir=str(profiles_ini.parent),
                                    is_default=is_default,
                                )
                            )

        except Exception as e:
            self.logger.error(f"Error parsing Firefox profiles: {e}")

        return profiles

    def get_default_browser(self) -> Optional[BrowserInfo]:
        """Get the default browser on Windows."""
        try:
            import winreg

            # Get default browser from registry
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"SOFTWARE\Microsoft\Windows\Shell\Associations\UrlAssociations\http\UserChoice",
            ) as key:
                prog_id = winreg.QueryValueEx(key, "ProgId")[0]

            # Map ProgId to browser name
            prog_id_map = {
                "ChromeHTML": "chrome",
                "FirefoxURL": "firefox",
                "MSEdgeHTM": "edge",
                "OperaStable": "opera",
                "BraveHTML": "brave",
            }

            browser_name = prog_id_map.get(prog_id)
            if browser_name:
                # Find the browser in detected browsers
                detected_browsers = self.detect_browsers()
                for browser in detected_browsers:
                    if browser.name == browser_name:
                        browser.is_default = True
                        return browser

            return None

        except Exception as e:
            self.logger.error(f"Error getting default browser: {e}")
            return None


class LinuxBrowserDetector(BrowserDetector):
    """Browser detector for Linux platforms."""

    def __init__(self):
        super().__init__("Linux")
        self.common_paths = {
            "chrome": [
                "/usr/bin/google-chrome",
                "/usr/bin/google-chrome-stable",
                "/opt/google/chrome/google-chrome",
            ],
            "chromium": [
                "/usr/bin/chromium",
                "/usr/bin/chromium-browser",
                "/snap/bin/chromium",
            ],
            "firefox": [
                "/usr/bin/firefox",
                "/usr/bin/firefox-esr",
                "/snap/bin/firefox",
            ],
            "opera": ["/usr/bin/opera", "/usr/bin/opera-stable"],
            "brave": [
                "/usr/bin/brave-browser",
                "/opt/brave.com/brave/brave-browser",
            ],
        }

    def detect_browsers(self) -> List[BrowserInfo]:
        """Detect browsers on Linux using various methods."""
        browsers = []

        # Method 1: Check common installation paths
        browsers.extend(self._detect_from_paths())

        # Method 2: Use 'which' command
        browsers.extend(self._detect_with_which())

        # Method 3: Use package manager queries
        browsers.extend(self._detect_with_package_managers())

        # Method 4: Desktop entries
        browsers.extend(self._detect_from_desktop_entries())

        # Remove duplicates and get versions
        unique_browsers = self._remove_duplicate_browsers(browsers)

        for browser in unique_browsers:
            if browser.executable_path:
                browser.version = self._get_browser_version(browser)

        return unique_browsers

    def _detect_from_paths(self) -> List[BrowserInfo]:
        """Detect browsers from common installation paths."""
        browsers = []

        for browser_name, paths in self.common_paths.items():
            for path in paths:
                if Path(path).exists():
                    browsers.append(
                        BrowserInfo(name=browser_name, executable_path=path)
                    )
                    break

        return browsers

    def _detect_with_which(self) -> List[BrowserInfo]:
        """Detect browsers using the 'which' command."""
        browsers = []

        browser_commands = [
            "google-chrome",
            "google-chrome-stable",
            "chromium",
            "chromium-browser",
            "firefox",
            "firefox-esr",
            "opera",
            "opera-stable",
            "brave-browser",
        ]

        for command in browser_commands:
            try:
                result = subprocess.run(
                    ["which", command], capture_output=True, text=True
                )
                if result.returncode == 0:
                    executable_path = result.stdout.strip()
                    if executable_path:
                        # Determine browser name from command
                        browser_name = self._command_to_browser_name(command)
                        browsers.append(
                            BrowserInfo(
                                name=browser_name,
                                executable_path=executable_path,
                            )
                        )
            except Exception:
                continue

        return browsers

    def _detect_with_package_managers(self) -> List[BrowserInfo]:
        """Detect browsers using package manager queries."""
        browsers = []

        # APT (Debian/Ubuntu)
        if self._command_exists("dpkg"):
            browsers.extend(self._detect_with_dpkg())

        # RPM (RedHat/CentOS/Fedora)
        if self._command_exists("rpm"):
            browsers.extend(self._detect_with_rpm())

        # Snap packages
        if self._command_exists("snap"):
            browsers.extend(self._detect_with_snap())

        # Flatpak
        if self._command_exists("flatpak"):
            browsers.extend(self._detect_with_flatpak())

        return browsers

    def _detect_with_dpkg(self) -> List[BrowserInfo]:
        """Detect browsers using dpkg."""
        browsers = []

        package_map = {
            "google-chrome-stable": "chrome",
            "chromium-browser": "chromium",
            "firefox": "firefox",
            "firefox-esr": "firefox",
            "opera-stable": "opera",
        }

        for package, browser_name in package_map.items():
            try:
                result = subprocess.run(
                    ["dpkg", "-l", package], capture_output=True, text=True
                )
                if result.returncode == 0 and "ii" in result.stdout:
                    # Package is installed, try to find executable
                    executable = self._find_executable_for_package(package)
                    if executable:
                        browsers.append(
                            BrowserInfo(
                                name=browser_name, executable_path=executable
                            )
                        )
            except Exception:
                continue

        return browsers

    def _detect_with_rpm(self) -> List[BrowserInfo]:
        """Detect browsers using rpm."""
        browsers = []

        package_map = {
            "google-chrome-stable": "chrome",
            "chromium": "chromium",
            "firefox": "firefox",
            "opera-stable": "opera",
        }

        for package, browser_name in package_map.items():
            try:
                result = subprocess.run(
                    ["rpm", "-q", package], capture_output=True, text=True
                )
                if result.returncode == 0:
                    # Package is installed, try to find executable
                    executable = self._find_executable_for_package(package)
                    if executable:
                        browsers.append(
                            BrowserInfo(
                                name=browser_name, executable_path=executable
                            )
                        )
            except Exception:
                continue

        return browsers

    def _detect_with_snap(self) -> List[BrowserInfo]:
        """Detect browsers installed via Snap."""
        browsers = []

        try:
            result = subprocess.run(
                ["snap", "list"], capture_output=True, text=True
            )
            if result.returncode == 0:
                for line in result.stdout.split("\n"):
                    if "chromium" in line.lower():
                        browsers.append(
                            BrowserInfo(
                                name="chromium",
                                executable_path="/snap/bin/chromium",
                            )
                        )
                    elif "firefox" in line.lower():
                        browsers.append(
                            BrowserInfo(
                                name="firefox",
                                executable_path="/snap/bin/firefox",
                            )
                        )
        except Exception:
            pass

        return browsers

    def _detect_with_flatpak(self) -> List[BrowserInfo]:
        """Detect browsers installed via Flatpak."""
        browsers = []

        try:
            result = subprocess.run(
                ["flatpak", "list", "--app"], capture_output=True, text=True
            )
            if result.returncode == 0:
                for line in result.stdout.split("\n"):
                    if "firefox" in line.lower():
                        browsers.append(
                            BrowserInfo(
                                name="firefox",
                                executable_path="flatpak run org.mozilla.firefox",
                            )
                        )
                    elif "chromium" in line.lower():
                        browsers.append(
                            BrowserInfo(
                                name="chromium",
                                executable_path="flatpak run org.chromium.Chromium",
                            )
                        )
        except Exception:
            pass

        return browsers

    def _detect_from_desktop_entries(self) -> List[BrowserInfo]:
        """Detect browsers from desktop entry files."""
        browsers = []

        desktop_dirs = [
            "/usr/share/applications",
            "/usr/local/share/applications",
            Path.home() / ".local" / "share" / "applications",
        ]

        for desktop_dir in desktop_dirs:
            if not Path(desktop_dir).exists():
                continue

            try:
                for desktop_file in Path(desktop_dir).glob("*.desktop"):
                    browser_info = self._parse_desktop_file(desktop_file)
                    if browser_info:
                        browsers.append(browser_info)
            except Exception:
                continue

        return browsers

    def _parse_desktop_file(self, desktop_file: Path) -> Optional[BrowserInfo]:
        """Parse a desktop entry file for browser information."""
        try:
            with open(desktop_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Look for browser-related desktop files
            browser_keywords = [
                "chrome",
                "firefox",
                "chromium",
                "opera",
                "brave",
            ]

            name_match = re.search(r"^Name=(.+)$", content, re.MULTILINE)
            exec_match = re.search(r"^Exec=([^\s]+)", content, re.MULTILINE)

            if name_match and exec_match:
                name = name_match.group(1).lower()
                executable = exec_match.group(1)

                for keyword in browser_keywords:
                    if keyword in name or keyword in executable.lower():
                        # Resolve executable path
                        if not executable.startswith("/"):
                            # Try to find full path
                            try:
                                result = subprocess.run(
                                    ["which", executable],
                                    capture_output=True,
                                    text=True,
                                )
                                if result.returncode == 0:
                                    executable = result.stdout.strip()
                            except Exception:
                                continue

                        if Path(executable).exists():
                            browser_name = self._command_to_browser_name(
                                executable
                            )
                            return BrowserInfo(
                                name=browser_name, executable_path=executable
                            )

            return None

        except Exception:
            return None

    def _command_to_browser_name(self, command: str) -> str:
        """Convert command name to standardized browser name."""
        command = command.lower()

        if "chrome" in command and "chromium" not in command:
            return "chrome"
        elif "chromium" in command:
            return "chromium"
        elif "firefox" in command:
            return "firefox"
        elif "opera" in command:
            return "opera"
        elif "brave" in command:
            return "brave"
        else:
            return Path(command).stem

    def _command_exists(self, command: str) -> bool:
        """Check if a command exists in the system."""
        try:
            result = subprocess.run(["which", command], capture_output=True)
            return result.returncode == 0
        except Exception:
            return False

    def _find_executable_for_package(self, package_name: str) -> Optional[str]:
        """Find executable path for an installed package."""
        # Try common executable names
        executable_map = {
            "google-chrome-stable": "google-chrome",
            "chromium-browser": "chromium-browser",
            "firefox": "firefox",
            "firefox-esr": "firefox-esr",
            "opera-stable": "opera",
        }

        executable_name = executable_map.get(package_name, package_name)

        try:
            result = subprocess.run(
                ["which", executable_name], capture_output=True, text=True
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass

        return None

    def _remove_duplicate_browsers(
        self, browsers: List[BrowserInfo]
    ) -> List[BrowserInfo]:
        """Remove duplicate browser entries."""
        seen_browsers = {}
        unique_browsers = []

        for browser in browsers:
            # Use normalized executable path as key
            key = (browser.name, Path(browser.executable_path or "").resolve())
            if key not in seen_browsers:
                seen_browsers[key] = browser
                unique_browsers.append(browser)

        return unique_browsers

    def _get_browser_version(self, browser: BrowserInfo) -> Optional[str]:
        """Get browser version on Linux."""
        try:
            if not browser.executable_path:
                return None

            # Try version flag
            result = subprocess.run(
                [browser.executable_path, "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                # Extract version number
                version_match = re.search(r"(\d+\.\d+\.\d+)", result.stdout)
                if version_match:
                    return version_match.group(1)

            return None

        except Exception as e:
            self.logger.debug(f"Failed to get version for {browser.name}: {e}")
            return None

    def get_browser_profiles(self, browser_name: str) -> List[BrowserProfile]:
        """Get browser profiles on Linux."""
        profiles = []

        profile_paths = {
            "chrome": Path.home() / ".config" / "google-chrome",
            "chromium": Path.home() / ".config" / "chromium",
            "firefox": Path.home() / ".mozilla" / "firefox",
            "opera": Path.home() / ".config" / "opera",
            "brave": Path.home()
            / ".config"
            / "BraveSoftware"
            / "Brave-Browser",
        }

        base_path = profile_paths.get(browser_name.lower())
        if not base_path or not base_path.exists():
            return profiles

        try:
            if browser_name.lower() == "firefox":
                # Firefox profiles
                profiles_ini = base_path / "profiles.ini"
                if profiles_ini.exists():
                    profiles.extend(self._parse_firefox_profiles(profiles_ini))
            else:
                # Chromium-based browsers
                for item in base_path.iterdir():
                    if item.is_dir() and (
                        item.name.startswith("Profile")
                        or item.name == "Default"
                    ):
                        profiles.append(
                            BrowserProfile(
                                browser_name=browser_name,
                                profile_name=item.name,
                                profile_path=str(item),
                                user_data_dir=str(base_path),
                                is_default=(item.name == "Default"),
                            )
                        )

        except Exception as e:
            self.logger.error(
                f"Error getting profiles for {browser_name}: {e}"
            )

        return profiles

    def _parse_firefox_profiles(
        self, profiles_ini: Path
    ) -> List[BrowserProfile]:
        """Parse Firefox profiles.ini file on Linux."""
        profiles = []

        try:
            import configparser

            config = configparser.ConfigParser()
            config.read(profiles_ini)

            for section_name in config.sections():
                if section_name.startswith("Profile"):
                    section = config[section_name]
                    name = section.get("Name", "Unknown")
                    path = section.get("Path", "")
                    is_relative = section.getboolean("IsRelative", True)
                    is_default = section.getboolean("Default", False)

                    if path:
                        if is_relative:
                            profile_path = profiles_ini.parent / path
                        else:
                            profile_path = Path(path)

                        if profile_path.exists():
                            profiles.append(
                                BrowserProfile(
                                    browser_name="firefox",
                                    profile_name=name,
                                    profile_path=str(profile_path),
                                    user_data_dir=str(profiles_ini.parent),
                                    is_default=is_default,
                                )
                            )

        except Exception as e:
            self.logger.error(f"Error parsing Firefox profiles: {e}")

        return profiles

    def get_default_browser(self) -> Optional[BrowserInfo]:
        """Get the default browser on Linux."""
        try:
            # Try xdg-settings
            result = subprocess.run(
                ["xdg-settings", "get", "default-web-browser"],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                default_app = result.stdout.strip()

                # Map desktop file to browser name
                browser_map = {
                    "google-chrome.desktop": "chrome",
                    "chromium.desktop": "chromium",
                    "firefox.desktop": "firefox",
                    "opera.desktop": "opera",
                    "brave-browser.desktop": "brave",
                }

                browser_name = browser_map.get(default_app)
                if browser_name:
                    # Find the browser in detected browsers
                    detected_browsers = self.detect_browsers()
                    for browser in detected_browsers:
                        if browser.name == browser_name:
                            browser.is_default = True
                            return browser

            return None

        except Exception as e:
            self.logger.error(f"Error getting default browser: {e}")
            return None


class MacOSBrowserDetector(BrowserDetector):
    """Browser detector for macOS platforms with SIP compliance."""

    def __init__(self):
        super().__init__("macOS")
        self.app_paths = {
            "chrome": "/Applications/Google Chrome.app",
            "firefox": "/Applications/Firefox.app",
            "safari": "/Applications/Safari.app",
            "opera": "/Applications/Opera.app",
            "brave": "/Applications/Brave Browser.app",
            "edge": "/Applications/Microsoft Edge.app",
        }

        # SIP-compliant detection methods
        self.user_consent_granted = False
        self.sandbox_mode = True
        self.detection_methods = [
            "applications_folder",
            "launch_services",
            "system_profiler",
            "mdfind_spotlight",
            "user_applications",
            "defaults_read",
        ]

    def detect_browsers(self) -> List[BrowserInfo]:
        """Detect browsers on macOS with SIP compliance."""
        browsers = []

        try:
            # Request user consent for enhanced detection
            if self._request_user_consent():
                self.user_consent_granted = True
                self.sandbox_mode = False
                self.logger.info(
                    "User consent granted for enhanced browser detection"
                )
            else:
                self.logger.warning(
                    "User consent not granted, using sandbox mode"
                )

            # Method 1: Check Applications folder (SIP-safe)
            browsers.extend(self._detect_from_applications())

            # Method 2: Use Launch Services (SIP-safe)
            browsers.extend(self._detect_with_launch_services())

            # Method 3: Use system_profiler (SIP-safe)
            browsers.extend(self._detect_with_system_profiler())

            # Method 4: Use mdfind (Spotlight) (SIP-safe)
            browsers.extend(self._detect_with_mdfind())

            # Method 5: User Applications folder (SIP-safe)
            browsers.extend(self._detect_from_user_applications())

            # Method 6: defaults read (requires consent)
            if self.user_consent_granted:
                browsers.extend(self._detect_with_defaults_read())

            # Remove duplicates and get versions
            unique_browsers = self._remove_duplicate_browsers(browsers)

            for browser in unique_browsers:
                browser.version = self._get_browser_version(browser)

            return unique_browsers

        except Exception as e:
            self.logger.error(f"Error during macOS browser detection: {e}")
            # Fallback to basic detection
            return self._fallback_detection()

    def _detect_from_applications(self) -> List[BrowserInfo]:
        """Detect browsers from /Applications folder."""
        browsers = []

        for browser_name, app_path in self.app_paths.items():
            if Path(app_path).exists():
                executable = self._get_executable_from_app(app_path)
                browsers.append(
                    BrowserInfo(name=browser_name, executable_path=executable)
                )

        return browsers

    def _detect_with_mdfind(self) -> List[BrowserInfo]:
        """Detect browsers using Spotlight search."""
        browsers = []

        browser_queries = [
            'kMDItemCFBundleIdentifier = "com.google.Chrome"',
            'kMDItemCFBundleIdentifier = "org.mozilla.firefox"',
            'kMDItemCFBundleIdentifier = "com.apple.Safari"',
            'kMDItemCFBundleIdentifier = "com.operasoftware.Opera"',
            'kMDItemCFBundleIdentifier = "com.brave.Browser"',
            'kMDItemCFBundleIdentifier = "com.microsoft.edgemac"',
        ]

        browser_map = {
            "com.google.Chrome": "chrome",
            "org.mozilla.firefox": "firefox",
            "com.apple.Safari": "safari",
            "com.operasoftware.Opera": "opera",
            "com.brave.Browser": "brave",
            "com.microsoft.edgemac": "edge",
        }

        for query in browser_queries:
            try:
                result = subprocess.run(
                    ["mdfind", query],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                if result.returncode == 0 and result.stdout.strip():
                    app_path = result.stdout.strip().split("\n")[0]

                    # Extract bundle identifier from query
                    bundle_id = query.split('"')[1]
                    browser_name = browser_map.get(bundle_id)

                    if browser_name and Path(app_path).exists():
                        executable = self._get_executable_from_app(app_path)
                        browsers.append(
                            BrowserInfo(
                                name=browser_name, executable_path=executable
                            )
                        )

            except Exception:
                continue

        return browsers

    def _request_user_consent(self) -> bool:
        """Request user consent for enhanced browser detection."""
        try:
            # Use osascript to display user consent dialog
            script = """
            tell application "System Events"
                display dialog "This application would like to access browser information for enhanced detection. This may include reading browser preferences and profile data." ¬
                    buttons {"Don't Allow", "Allow"} ¬
                    default button "Allow" ¬
                    with title "Browser Detection Permission" ¬
                    with icon caution
                set button_pressed to button returned of result
                return button_pressed
            end tell
            """

            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                response = result.stdout.strip()
                return response == "Allow"

            return False

        except Exception as e:
            self.logger.debug(f"User consent dialog failed: {e}")
            # Fallback: assume no consent in automated environments
            return False

    def _detect_with_launch_services(self) -> List[BrowserInfo]:
        """Detect browsers using Launch Services API (SIP-safe)."""
        browsers = []

        try:
            # Use system_profiler to get application information
            result = subprocess.run(
                ["system_profiler", "SPApplicationsDataType", "-xml"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                # Parse the XML output to find browser applications
                import xml.etree.ElementTree as ET

                try:
                    root = ET.fromstring(result.stdout)
                    # Look for browser-related applications
                    for item in root.iter():
                        if item.tag == "string" and item.text:
                            text = item.text.lower()
                            if any(
                                browser in text
                                for browser in [
                                    "chrome",
                                    "firefox",
                                    "safari",
                                    "opera",
                                    "brave",
                                    "edge",
                                ]
                            ):
                                # Extract browser information
                                self._extract_browser_info_from_xml(
                                    item, browsers
                                )
                except ET.ParseError:
                    self.logger.debug(
                        "Failed to parse system_profiler XML output"
                    )

        except Exception as e:
            self.logger.debug(f"Launch Services detection failed: {e}")

        return browsers

    def _detect_with_system_profiler(self) -> List[BrowserInfo]:
        """Detect browsers using system_profiler (SIP-safe)."""
        browsers = []

        try:
            # Query for installed applications
            result = subprocess.run(
                ["system_profiler", "SPApplicationsDataType", "-json"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                try:
                    data = json.loads(result.stdout)
                    applications = data.get("SPApplicationsDataType", [])

                    for app in applications:
                        app_name = app.get("_name", "").lower()
                        app_path = app.get("path", "")

                        # Check if this is a browser
                        browser_name = self._identify_browser_from_name(
                            app_name
                        )
                        if browser_name and app_path:
                            executable = self._get_executable_from_app(
                                app_path
                            )
                            if executable:
                                browsers.append(
                                    BrowserInfo(
                                        name=browser_name,
                                        executable_path=executable,
                                    )
                                )

                except json.JSONDecodeError:
                    self.logger.debug(
                        "Failed to parse system_profiler JSON output"
                    )

        except Exception as e:
            self.logger.debug(f"system_profiler detection failed: {e}")

        return browsers

    def _detect_with_defaults_read(self) -> List[BrowserInfo]:
        """Detect browsers using defaults read (requires user consent)."""
        browsers = []

        if not self.user_consent_granted:
            return browsers

        try:
            # Read browser-related preferences
            browser_domains = [
                "com.google.Chrome",
                "org.mozilla.firefox",
                "com.apple.Safari",
                "com.operasoftware.Opera",
                "com.brave.Browser",
                "com.microsoft.edgemac",
            ]

            for domain in browser_domains:
                try:
                    result = subprocess.run(
                        ["defaults", "read", domain, "NSNavLastRootDirectory"],
                        capture_output=True,
                        text=True,
                        timeout=10,
                    )

                    if result.returncode == 0:
                        # Browser is installed and has preferences
                        browser_name = self._domain_to_browser_name(domain)
                        if browser_name:
                            app_path = self.app_paths.get(browser_name)
                            if app_path and Path(app_path).exists():
                                executable = self._get_executable_from_app(
                                    app_path
                                )
                                if executable:
                                    browsers.append(
                                        BrowserInfo(
                                            name=browser_name,
                                            executable_path=executable,
                                        )
                                    )

                except Exception:
                    continue

        except Exception as e:
            self.logger.debug(f"defaults read detection failed: {e}")

        return browsers

    def _fallback_detection(self) -> List[BrowserInfo]:
        """Fallback detection method when all else fails."""
        browsers = []

        try:
            # Basic detection using just file system checks
            for browser_name, app_path in self.app_paths.items():
                try:
                    if Path(app_path).exists():
                        browsers.append(
                            BrowserInfo(
                                name=browser_name, executable_path=app_path
                            )
                        )
                except Exception:
                    continue

        except Exception as e:
            self.logger.error(f"Fallback detection failed: {e}")

        return browsers

    def _extract_browser_info_from_xml(
        self, item, browsers: List[BrowserInfo]
    ) -> None:
        """Extract browser information from XML elements."""
        try:
            # This is a simplified implementation - would need full XML parsing
            # for production use
            pass
        except Exception:
            pass

    def _identify_browser_from_name(self, app_name: str) -> Optional[str]:
        """Identify browser name from application name."""
        app_name_lower = app_name.lower()

        if "chrome" in app_name_lower and "chromium" not in app_name_lower:
            return "chrome"
        elif "firefox" in app_name_lower:
            return "firefox"
        elif "safari" in app_name_lower:
            return "safari"
        elif "opera" in app_name_lower:
            return "opera"
        elif "brave" in app_name_lower:
            return "brave"
        elif "edge" in app_name_lower:
            return "edge"

        return None

    def _domain_to_browser_name(self, domain: str) -> Optional[str]:
        """Convert bundle domain to browser name."""
        domain_map = {
            "com.google.Chrome": "chrome",
            "org.mozilla.firefox": "firefox",
            "com.apple.Safari": "safari",
            "com.operasoftware.Opera": "opera",
            "com.brave.Browser": "brave",
            "com.microsoft.edgemac": "edge",
        }
        return domain_map.get(domain)

    def _detect_from_user_applications(self) -> List[BrowserInfo]:
        """Detect browsers from user Applications folder."""
        browsers = []
        user_apps = Path.home() / "Applications"

        if user_apps.exists():
            for browser_name, app_name in self.app_paths.items():
                app_path = user_apps / Path(app_name).name
                if app_path.exists():
                    executable = self._get_executable_from_app(str(app_path))
                    browsers.append(
                        BrowserInfo(
                            name=browser_name, executable_path=executable
                        )
                    )

        return browsers

    def _get_executable_from_app(self, app_path: str) -> str:
        """Get executable path from macOS .app bundle."""
        try:
            # Get Info.plist to find executable name
            info_plist = Path(app_path) / "Contents" / "Info.plist"

            if info_plist.exists():
                result = subprocess.run(
                    ["plutil", "-p", str(info_plist)],
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0:
                    # Extract CFBundleExecutable
                    for line in result.stdout.split("\n"):
                        if "CFBundleExecutable" in line:
                            executable_name = line.split('"')[3]
                            return str(
                                Path(app_path)
                                / "Contents"
                                / "MacOS"
                                / executable_name
                            )

            # Fallback: assume executable name matches app name
            app_name = Path(app_path).stem
            return str(Path(app_path) / "Contents" / "MacOS" / app_name)

        except Exception:
            return app_path

    def _remove_duplicate_browsers(
        self, browsers: List[BrowserInfo]
    ) -> List[BrowserInfo]:
        """Remove duplicate browser entries."""
        seen_browsers = {}
        unique_browsers = []

        for browser in browsers:
            key = (browser.name, browser.executable_path)
            if key not in seen_browsers:
                seen_browsers[key] = browser
                unique_browsers.append(browser)

        return unique_browsers

    def _get_browser_version(self, browser: BrowserInfo) -> Optional[str]:
        """Get browser version on macOS."""
        try:
            if not browser.executable_path:
                return None

            # Try to get version from Info.plist
            app_path = browser.executable_path
            if "/Contents/MacOS/" in app_path:
                app_bundle = app_path.split("/Contents/MacOS/")[0]
                info_plist = Path(app_bundle) / "Contents" / "Info.plist"

                if info_plist.exists():
                    result = subprocess.run(
                        ["plutil", "-p", str(info_plist)],
                        capture_output=True,
                        text=True,
                    )

                    if result.returncode == 0:
                        for line in result.stdout.split("\n"):
                            if "CFBundleShortVersionString" in line:
                                version = line.split('"')[3]
                                return version

            # Fallback: try version flag
            result = subprocess.run(
                [browser.executable_path, "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                version_match = re.search(r"(\d+\.\d+\.\d+)", result.stdout)
                if version_match:
                    return version_match.group(1)

            return None

        except Exception as e:
            self.logger.debug(f"Failed to get version for {browser.name}: {e}")
            return None

    def get_browser_profiles(self, browser_name: str) -> List[BrowserProfile]:
        """Get browser profiles on macOS."""
        profiles = []

        profile_paths = {
            "chrome": Path.home()
            / "Library"
            / "Application Support"
            / "Google"
            / "Chrome",
            "firefox": Path.home()
            / "Library"
            / "Application Support"
            / "Firefox"
            / "Profiles",
            "safari": Path.home() / "Library" / "Safari",
            "opera": Path.home()
            / "Library"
            / "Application Support"
            / "com.operasoftware.Opera",
            "brave": Path.home()
            / "Library"
            / "Application Support"
            / "BraveSoftware"
            / "Brave-Browser",
            "edge": Path.home()
            / "Library"
            / "Application Support"
            / "Microsoft Edge",
        }

        base_path = profile_paths.get(browser_name.lower())
        if not base_path or not base_path.exists():
            return profiles

        try:
            if browser_name.lower() == "firefox":
                # Firefox profiles
                profiles_ini = base_path.parent / "profiles.ini"
                if profiles_ini.exists():
                    profiles.extend(self._parse_firefox_profiles(profiles_ini))
            elif browser_name.lower() == "safari":
                # Safari doesn't use traditional profiles
                profiles.append(
                    BrowserProfile(
                        browser_name="safari",
                        profile_name="Default",
                        profile_path=str(base_path),
                        user_data_dir=str(base_path),
                        is_default=True,
                    )
                )
            else:
                # Chromium-based browsers
                for item in base_path.iterdir():
                    if item.is_dir() and (
                        item.name.startswith("Profile")
                        or item.name == "Default"
                    ):
                        profiles.append(
                            BrowserProfile(
                                browser_name=browser_name,
                                profile_name=item.name,
                                profile_path=str(item),
                                user_data_dir=str(base_path),
                                is_default=(item.name == "Default"),
                            )
                        )

        except Exception as e:
            self.logger.error(
                f"Error getting profiles for {browser_name}: {e}"
            )

        return profiles

    def _parse_firefox_profiles(
        self, profiles_ini: Path
    ) -> List[BrowserProfile]:
        """Parse Firefox profiles.ini file on macOS."""
        profiles = []

        try:
            import configparser

            config = configparser.ConfigParser()
            config.read(profiles_ini)

            for section_name in config.sections():
                if section_name.startswith("Profile"):
                    section = config[section_name]
                    name = section.get("Name", "Unknown")
                    path = section.get("Path", "")
                    is_relative = section.getboolean("IsRelative", True)
                    is_default = section.getboolean("Default", False)

                    if path:
                        if is_relative:
                            profile_path = profiles_ini.parent / path
                        else:
                            profile_path = Path(path)

                        if profile_path.exists():
                            profiles.append(
                                BrowserProfile(
                                    browser_name="firefox",
                                    profile_name=name,
                                    profile_path=str(profile_path),
                                    user_data_dir=str(profiles_ini.parent),
                                    is_default=is_default,
                                )
                            )

        except Exception as e:
            self.logger.error(f"Error parsing Firefox profiles: {e}")

        return profiles

    def get_default_browser(self) -> Optional[BrowserInfo]:
        """Get the default browser on macOS."""
        try:
            # Use defaults command to get default browser
            result = subprocess.run(
                [
                    "defaults",
                    "read",
                    "com.apple.LaunchServices/com.apple.launchservices.secure",
                    "LSHandlers",
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                # Parse output to find http handler
                output = result.stdout

                # Look for http URL scheme handler
                # This is a simplified approach - full parsing would be more complex
                bundle_id_map = {
                    "com.google.chrome": "chrome",
                    "org.mozilla.firefox": "firefox",
                    "com.apple.safari": "safari",
                    "com.operasoftware.opera": "opera",
                    "com.brave.browser": "brave",
                    "com.microsoft.edgemac": "edge",
                }

                for bundle_id, browser_name in bundle_id_map.items():
                    if bundle_id in output:
                        # Find the browser in detected browsers
                        detected_browsers = self.detect_browsers()
                        for browser in detected_browsers:
                            if browser.name == browser_name:
                                browser.is_default = True
                                return browser

            return None

        except Exception as e:
            self.logger.error(f"Error getting default browser: {e}")
            return None


class CrossPlatformBrowserDetector:
    """Cross-platform browser detection manager."""

    def __init__(self, verbose: bool = False):
        """Initialize cross-platform browser detector.

        Args:
            verbose: Enable verbose logging
        """
        self.verbose = verbose
        self.setup_logging()

        # Detect platform and create appropriate detector
        self.platform = platform.system().lower()
        self.detector = self._create_platform_detector()

        self.logger.info(
            f"CrossPlatformBrowserDetector initialized for {self.platform}"
        )

    def setup_logging(self):
        """Setup logging configuration."""
        log_level = logging.DEBUG if self.verbose else logging.INFO
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(
                    f'browser_detection_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
                ),
            ],
        )
        self.logger = logging.getLogger(__name__)

    def _create_platform_detector(self) -> BrowserDetector:
        """Create platform-specific browser detector."""
        if self.platform == "windows":
            return WindowsBrowserDetector()
        elif self.platform == "linux":
            return LinuxBrowserDetector()
        elif self.platform == "darwin":  # macOS
            return MacOSBrowserDetector()
        else:
            # Fallback to Linux detector for other Unix-like systems
            self.logger.warning(
                f"Unknown platform {self.platform}, using Linux detector"
            )
            return LinuxBrowserDetector()

    def detect_all_browsers(self) -> List[BrowserInfo]:
        """Detect all installed browsers."""
        self.logger.info("Starting browser detection...")

        try:
            browsers = self.detector.detect_browsers()
            self.logger.info(f"Found {len(browsers)} browsers")

            for browser in browsers:
                self.logger.info(
                    f"  - {browser.name} v{browser.version or 'unknown'}"
                )

            return browsers

        except Exception as e:
            self.logger.error(f"Error during browser detection: {e}")
            return []

    def get_browser_profiles(self, browser_name: str) -> List[BrowserProfile]:
        """Get profiles for a specific browser."""
        try:
            profiles = self.detector.get_browser_profiles(browser_name)
            self.logger.info(
                f"Found {len(profiles)} profiles for {browser_name}"
            )
            return profiles
        except Exception as e:
            self.logger.error(
                f"Error getting profiles for {browser_name}: {e}"
            )
            return []

    def get_default_browser(self) -> Optional[BrowserInfo]:
        """Get the system default browser."""
        try:
            default_browser = self.detector.get_default_browser()
            if default_browser:
                self.logger.info(f"Default browser: {default_browser.name}")
            else:
                self.logger.warning("Could not determine default browser")
            return default_browser
        except Exception as e:
            self.logger.error(f"Error getting default browser: {e}")
            return None

    def generate_detection_report(self) -> str:
        """Generate a comprehensive browser detection report."""
        report_lines = [
            "=" * 60,
            "CROSS-PLATFORM BROWSER DETECTION REPORT",
            "=" * 60,
            "",
            f"Detection Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Platform: {self.platform}",
            f"Detector: {self.detector.__class__.__name__}",
            "",
            "Detected Browsers:",
            "-" * 20,
        ]

        browsers = self.detect_all_browsers()
        default_browser = self.get_default_browser()

        for browser in browsers:
            status = (
                " [DEFAULT]"
                if (default_browser and browser.name == default_browser.name)
                else ""
            )
            report_lines.append(
                f"  • {browser.name} v{browser.version or 'unknown'}{status}"
            )
            if browser.executable_path:
                report_lines.append(f"    Path: {browser.executable_path}")

            # Get profiles
            profiles = self.get_browser_profiles(browser.name)
            if profiles:
                report_lines.append(f"    Profiles: {len(profiles)}")
                for profile in profiles[:3]:  # Show first 3 profiles
                    default_indicator = (
                        " [DEFAULT]" if profile.is_default else ""
                    )
                    report_lines.append(
                        f"      - {profile.profile_name}{default_indicator}"
                    )
                if len(profiles) > 3:
                    report_lines.append(
                        f"      ... and {len(profiles) - 3} more"
                    )

            report_lines.append("")

        if not browsers:
            report_lines.append("  No browsers detected.")

        report_lines.extend(
            ["", f"Total Browsers Found: {len(browsers)}", "", "=" * 60]
        )

        return "\n".join(report_lines)

    def export_detection_results(self, export_format: str = "json") -> str:
        """Export detection results to specified format."""
        browsers = self.detect_all_browsers()
        default_browser = self.get_default_browser()

        # Prepare data structure
        data = {
            "detection_date": datetime.now().isoformat(),
            "platform": self.platform,
            "detector": self.detector.__class__.__name__,
            "default_browser": (
                asdict(default_browser) if default_browser else None
            ),
            "browsers": [],
        }

        for browser in browsers:
            browser_data = asdict(browser)
            browser_data["profiles"] = [
                asdict(profile)
                for profile in self.get_browser_profiles(browser.name)
            ]
            data["browsers"].append(browser_data)

        if export_format.lower() == "json":
            filename = f"browser_detection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, "w") as f:
                json.dump(data, f, indent=2, default=str)
        else:
            raise ValueError(f"Unsupported export format: {export_format}")

        return filename

    def validate_browser_accessibility(self) -> Dict[str, bool]:
        """Validate that detected browsers are accessible and functional."""
        validation_results = {}
        browsers = self.detect_all_browsers()

        for browser in browsers:
            try:
                if not browser.executable_path:
                    validation_results[browser.name] = False
                    continue

                # Try to get version (indicates browser is accessible)
                result = subprocess.run(
                    [browser.executable_path, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                validation_results[browser.name] = result.returncode == 0

            except Exception:
                validation_results[browser.name] = False

        return validation_results


def main():
    """Main entry point for browser detection script."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Cross-Platform Browser Detection Utilities"
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    parser.add_argument(
        "--export", choices=["json"], help="Export results to specified format"
    )

    parser.add_argument(
        "--profiles",
        metavar="BROWSER",
        help="Show profiles for specific browser",
    )

    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate browser accessibility",
    )

    args = parser.parse_args()

    # Create detector
    detector = CrossPlatformBrowserDetector(verbose=args.verbose)

    # Generate and display report
    report = detector.generate_detection_report()
    print(report)

    # Export if requested
    if args.export:
        filename = detector.export_detection_results(args.export)
        print(f"\nResults exported to: {filename}")

    # Show profiles for specific browser
    if args.profiles:
        profiles = detector.get_browser_profiles(args.profiles)
        if profiles:
            print(f"\nProfiles for {args.profiles}:")
            print("-" * 30)
            for profile in profiles:
                default_indicator = " [DEFAULT]" if profile.is_default else ""
                print(f"  • {profile.profile_name}{default_indicator}")
                print(f"    Path: {profile.profile_path}")
        else:
            print(f"\nNo profiles found for {args.profiles}")

    # Validate if requested
    if args.validate:
        print("\nValidating browser accessibility...")
        validation_results = detector.validate_browser_accessibility()

        print("\nValidation Results:")
        print("-" * 30)
        for browser, accessible in validation_results.items():
            status = "✓" if accessible else "✗"
            print(f"{status} {browser}")


if __name__ == "__main__":
    main()
