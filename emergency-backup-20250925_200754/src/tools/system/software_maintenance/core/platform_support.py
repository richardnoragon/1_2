"""
Platform Support for Software Maintenance Toolkit

This module provides cross-platform compatibility utilities for Windows,
macOS, and Linux systems, handling platform-specific operations and
providing unified interfaces for software maintenance tasks.
"""

import os
import sys
import platform
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from enum import Enum

from .maintenance_base import MaintenanceToolBase


class PlatformType(Enum):
    """Enumeration of supported platforms."""

    WINDOWS = "windows"
    MACOS = "macos"
    LINUX = "linux"
    UNKNOWN = "unknown"


class PlatformSupport(MaintenanceToolBase):
    """
    Cross-platform support utilities providing unified interfaces
    for platform-specific operations.
    """

    def __init__(self):
        super().__init__("Platform Support")

        self.platform_type = self._detect_platform()
        self.platform_info = self._get_platform_info()

        # Platform-specific paths
        self.system_paths = self._get_system_paths()
        self.temp_paths = self._get_temp_paths()
        self.config_paths = self._get_config_paths()

        self.log_info(f"Platform detected: {self.platform_type.value}")

    def _detect_platform(self) -> PlatformType:
        """Detect the current platform."""
        system = platform.system().lower()

        if system == "windows":
            return PlatformType.WINDOWS
        elif system == "darwin":
            return PlatformType.MACOS
        elif system == "linux":
            return PlatformType.LINUX
        else:
            return PlatformType.UNKNOWN

    def _get_platform_info(self) -> Dict[str, str]:
        """Get detailed platform information."""
        info = {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "architecture": platform.architecture()[0],
            "python_version": platform.python_version(),
        }

        if self.platform_type == PlatformType.WINDOWS:
            info["windows_edition"] = platform.win32_edition()
            info["windows_version"] = platform.win32_ver()[0]
        elif self.platform_type == PlatformType.MACOS:
            info["mac_version"] = platform.mac_ver()[0]
        elif self.platform_type == PlatformType.LINUX:
            try:
                info["linux_distribution"] = platform.freedesktop_os_release()
            except AttributeError:
                info["linux_distribution"] = {}

        return info

    def _get_system_paths(self) -> Dict[str, str]:
        """Get platform-specific system paths."""
        paths = {}

        if self.platform_type == PlatformType.WINDOWS:
            paths.update(
                {
                    "program_files": os.environ.get(
                        "PROGRAMFILES", "C:\\Program Files"
                    ),
                    "program_files_x86": os.environ.get(
                        "PROGRAMFILES(X86)", "C:\\Program Files (x86)"
                    ),
                    "system32": os.path.join(
                        os.environ.get("WINDIR", "C:\\Windows"), "System32"
                    ),
                    "appdata": os.environ.get("APPDATA", ""),
                    "localappdata": os.environ.get("LOCALAPPDATA", ""),
                    "programdata": os.environ.get("PROGRAMDATA", ""),
                    "userprofile": os.environ.get("USERPROFILE", ""),
                    "windows": os.environ.get("WINDIR", "C:\\Windows"),
                }
            )

        elif self.platform_type == PlatformType.MACOS:
            home = os.path.expanduser("~")
            paths.update(
                {
                    "applications": "/Applications",
                    "library": "/Library",
                    "user_library": os.path.join(home, "Library"),
                    "user_applications": os.path.join(home, "Applications"),
                    "system": "/System",
                    "usr": "/usr",
                    "opt": "/opt",
                    "home": home,
                }
            )

        elif self.platform_type == PlatformType.LINUX:
            home = os.path.expanduser("~")
            paths.update(
                {
                    "usr": "/usr",
                    "usr_local": "/usr/local",
                    "opt": "/opt",
                    "etc": "/etc",
                    "var": "/var",
                    "home": home,
                    "user_local": os.path.join(home, ".local"),
                    "user_config": os.path.join(home, ".config"),
                    "user_cache": os.path.join(home, ".cache"),
                }
            )

        return paths

    def _get_temp_paths(self) -> List[str]:
        """Get platform-specific temporary directories."""
        temp_paths = []

        if self.platform_type == PlatformType.WINDOWS:
            temp_paths.extend(
                [
                    os.environ.get("TEMP", ""),
                    os.environ.get("TMP", ""),
                    "C:\\Windows\\Temp",
                    os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp"),
                ]
            )

        elif self.platform_type == PlatformType.MACOS:
            temp_paths.extend(
                [
                    "/tmp",
                    "/var/tmp",
                    os.path.expanduser("~/Library/Caches"),
                    "/private/tmp",
                ]
            )

        elif self.platform_type == PlatformType.LINUX:
            temp_paths.extend(
                [
                    "/tmp",
                    "/var/tmp",
                    os.path.expanduser("~/.cache"),
                    (
                        "/run/user/" + str(os.getuid())
                        if hasattr(os, "getuid")
                        else ""
                    ),
                ]
            )

        # Filter out empty paths
        return [path for path in temp_paths if path]

    def _get_config_paths(self) -> List[str]:
        """Get platform-specific configuration directories."""
        config_paths = []

        if self.platform_type == PlatformType.WINDOWS:
            config_paths.extend(
                [
                    os.environ.get("APPDATA", ""),
                    os.environ.get("LOCALAPPDATA", ""),
                    os.environ.get("PROGRAMDATA", ""),
                ]
            )

        elif self.platform_type == PlatformType.MACOS:
            home = os.path.expanduser("~")
            config_paths.extend(
                [
                    os.path.join(home, "Library", "Preferences"),
                    os.path.join(home, "Library", "Application Support"),
                    "/Library/Preferences",
                    "/Library/Application Support",
                ]
            )

        elif self.platform_type == PlatformType.LINUX:
            home = os.path.expanduser("~")
            config_paths.extend(
                [
                    os.path.join(home, ".config"),
                    os.path.join(home, ".local", "share"),
                    "/etc",
                    "/usr/share",
                ]
            )

        # Filter out empty paths
        return [path for path in config_paths if path]

    def get_installed_software_locations(self) -> List[str]:
        """Get common software installation locations for the platform."""
        locations = []

        if self.platform_type == PlatformType.WINDOWS:
            locations.extend(
                [
                    self.system_paths.get("program_files", ""),
                    self.system_paths.get("program_files_x86", ""),
                    os.path.join(
                        self.system_paths.get("localappdata", ""), "Programs"
                    ),
                    os.path.join(
                        self.system_paths.get("userprofile", ""),
                        "AppData",
                        "Local",
                        "Programs",
                    ),
                ]
            )

        elif self.platform_type == PlatformType.MACOS:
            locations.extend(
                [
                    "/Applications",
                    os.path.expanduser("~/Applications"),
                    "/usr/local/bin",
                    "/opt",
                ]
            )

        elif self.platform_type == PlatformType.LINUX:
            locations.extend(
                [
                    "/usr/bin",
                    "/usr/local/bin",
                    "/opt",
                    "/snap",
                    "/var/lib/flatpak/app",
                    os.path.expanduser("~/.local/bin"),
                    os.path.expanduser("~/.local/share/applications"),
                ]
            )

        # Filter out empty paths and verify they exist
        return [path for path in locations if path and os.path.exists(path)]

    def get_package_manager_commands(self) -> Dict[str, List[str]]:
        """Get available package manager commands for the platform."""
        commands = {}

        if self.platform_type == PlatformType.WINDOWS:
            # Windows package managers
            if self._command_exists("choco"):
                commands["chocolatey"] = ["choco"]
            if self._command_exists("winget"):
                commands["winget"] = ["winget"]
            if self._command_exists("scoop"):
                commands["scoop"] = ["scoop"]

        elif self.platform_type == PlatformType.MACOS:
            # macOS package managers
            if self._command_exists("brew"):
                commands["homebrew"] = ["brew"]
            if self._command_exists("port"):
                commands["macports"] = ["port"]

        elif self.platform_type == PlatformType.LINUX:
            # Linux package managers
            if self._command_exists("apt"):
                commands["apt"] = ["apt", "apt-get"]
            if self._command_exists("yum"):
                commands["yum"] = ["yum"]
            if self._command_exists("dnf"):
                commands["dnf"] = ["dnf"]
            if self._command_exists("pacman"):
                commands["pacman"] = ["pacman"]
            if self._command_exists("zypper"):
                commands["zypper"] = ["zypper"]
            if self._command_exists("snap"):
                commands["snap"] = ["snap"]
            if self._command_exists("flatpak"):
                commands["flatpak"] = ["flatpak"]

        return commands

    def _command_exists(self, command: str) -> bool:
        """Check if a command exists in the system PATH."""
        try:
            subprocess.run(
                [command, "--version"],
                capture_output=True,
                check=False,
                timeout=5,
            )
            return True
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return False

    def get_admin_command_prefix(self) -> List[str]:
        """Get the command prefix needed for administrative operations."""
        if self.platform_type == PlatformType.WINDOWS:
            # Windows doesn't have a direct equivalent to sudo
            # Administrative operations require UAC elevation
            return []
        else:
            # Unix-like systems use sudo
            return ["sudo"]

    def is_admin(self) -> bool:
        """Check if the current process has administrative privileges."""
        try:
            if self.platform_type == PlatformType.WINDOWS:
                import ctypes

                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:
                return os.geteuid() == 0
        except Exception as e:
            self.log_warning(f"Could not check admin privileges: {e}")
            return False

    def get_file_permissions(self, file_path: str) -> Dict[str, bool]:
        """Get file permissions in a cross-platform way."""
        permissions = {
            "readable": False,
            "writable": False,
            "executable": False,
        }

        try:
            path = Path(file_path)
            if path.exists():
                permissions["readable"] = os.access(path, os.R_OK)
                permissions["writable"] = os.access(path, os.W_OK)
                permissions["executable"] = os.access(path, os.X_OK)
        except Exception as e:
            self.log_warning(
                f"Could not check permissions for {file_path}: {e}"
            )

        return permissions

    def get_disk_usage(self, path: str) -> Dict[str, int]:
        """Get disk usage information for a path."""
        usage = {"total": 0, "used": 0, "free": 0}

        try:
            if self.platform_type == PlatformType.WINDOWS:
                import shutil

                total, used, free = shutil.disk_usage(path)
                usage = {"total": total, "used": used, "free": free}
            else:
                # Unix-like systems
                statvfs = os.statvfs(path)
                usage = {
                    "total": statvfs.f_frsize * statvfs.f_blocks,
                    "used": statvfs.f_frsize
                    * (statvfs.f_blocks - statvfs.f_available),
                    "free": statvfs.f_frsize * statvfs.f_available,
                }
        except Exception as e:
            self.log_warning(f"Could not get disk usage for {path}: {e}")

        return usage

    def get_process_list(self) -> List[Dict[str, str]]:
        """Get a list of running processes."""
        processes = []

        try:
            if self.platform_type == PlatformType.WINDOWS:
                # Use tasklist on Windows
                result = subprocess.run(
                    ["tasklist", "/fo", "csv"], capture_output=True, text=True
                )
                if result.returncode == 0:
                    lines = result.stdout.strip().split("\n")[
                        1:
                    ]  # Skip header
                    for line in lines:
                        parts = line.split('","')
                        if len(parts) >= 2:
                            name = parts[0].strip('"')
                            pid = parts[1].strip('"')
                            processes.append({"name": name, "pid": pid})
            else:
                # Use ps on Unix-like systems
                result = subprocess.run(
                    ["ps", "aux"], capture_output=True, text=True
                )
                if result.returncode == 0:
                    lines = result.stdout.strip().split("\n")[
                        1:
                    ]  # Skip header
                    for line in lines:
                        parts = line.split()
                        if len(parts) >= 11:
                            pid = parts[1]
                            name = parts[10]
                            processes.append({"name": name, "pid": pid})

        except Exception as e:
            self.log_warning(f"Could not get process list: {e}")

        return processes

    def kill_process(self, pid: str) -> bool:
        """Kill a process by PID."""
        try:
            if self.platform_type == PlatformType.WINDOWS:
                result = subprocess.run(
                    ["taskkill", "/F", "/PID", pid], capture_output=True
                )
                return result.returncode == 0
            else:
                result = subprocess.run(
                    ["kill", "-9", pid], capture_output=True
                )
                return result.returncode == 0

        except Exception as e:
            self.log_error(f"Could not kill process {pid}: {e}")
            return False

    def get_environment_variables(self) -> Dict[str, str]:
        """Get relevant environment variables for the platform."""
        relevant_vars = []

        if self.platform_type == PlatformType.WINDOWS:
            relevant_vars = [
                "PATH",
                "PROGRAMFILES",
                "PROGRAMFILES(X86)",
                "WINDIR",
                "APPDATA",
                "LOCALAPPDATA",
                "PROGRAMDATA",
                "USERPROFILE",
                "TEMP",
                "TMP",
                "COMPUTERNAME",
                "USERNAME",
            ]
        else:
            relevant_vars = [
                "PATH",
                "HOME",
                "USER",
                "SHELL",
                "TERM",
                "LANG",
                "XDG_CONFIG_HOME",
                "XDG_DATA_HOME",
                "XDG_CACHE_HOME",
            ]

        return {var: os.environ.get(var, "") for var in relevant_vars}

    def create_desktop_shortcut(
        self, name: str, target: str, icon: str = None
    ) -> bool:
        """Create a desktop shortcut."""
        try:
            if self.platform_type == PlatformType.WINDOWS:
                return self._create_windows_shortcut(name, target, icon)
            elif self.platform_type == PlatformType.LINUX:
                return self._create_linux_desktop_entry(name, target, icon)
            else:
                self.log_warning(
                    "Desktop shortcuts not supported on this platform"
                )
                return False

        except Exception as e:
            self.log_error(f"Could not create desktop shortcut: {e}")
            return False

    def _create_windows_shortcut(
        self, name: str, target: str, icon: str = None
    ) -> bool:
        """Create a Windows shortcut (.lnk file)."""
        try:
            import win32com.client

            desktop = os.path.join(os.environ["USERPROFILE"], "Desktop")
            shortcut_path = os.path.join(desktop, f"{name}.lnk")

            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = target
            if icon:
                shortcut.IconLocation = icon
            shortcut.save()

            return True

        except ImportError:
            self.log_warning("pywin32 not available for shortcut creation")
            return False

    def _create_linux_desktop_entry(
        self, name: str, target: str, icon: str = None
    ) -> bool:
        """Create a Linux desktop entry (.desktop file)."""
        desktop_dir = os.path.expanduser("~/Desktop")
        if not os.path.exists(desktop_dir):
            desktop_dir = os.path.expanduser("~/.local/share/applications")

        desktop_file = os.path.join(desktop_dir, f"{name}.desktop")

        content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name={name}
Exec={target}
Terminal=false
"""

        if icon:
            content += f"Icon={icon}\n"

        try:
            with open(desktop_file, "w") as f:
                f.write(content)

            # Make executable
            os.chmod(desktop_file, 0o755)
            return True

        except Exception:
            return False

    def execute(self, **kwargs) -> bool:
        """Execute platform support validation."""
        try:
            self.update_status("Validating platform support...")

            # Log platform information
            self.log_info(f"Platform: {self.platform_info}")
            self.log_info(f"System paths: {len(self.system_paths)} configured")
            self.log_info(f"Temp paths: {len(self.temp_paths)} available")
            self.log_info(f"Config paths: {len(self.config_paths)} available")

            # Check package managers
            package_managers = self.get_package_manager_commands()
            self.log_info(f"Package managers: {list(package_managers.keys())}")

            # Check admin privileges
            admin_status = self.is_admin()
            self.log_info(f"Administrative privileges: {admin_status}")

            self.update_status("Platform support validation completed")
            return True

        except Exception as e:
            self.log_error(f"Platform support validation failed: {e}")
            return False
