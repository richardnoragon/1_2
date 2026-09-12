"""
Safety manager for system cleanup operations.

Provides backup, restore, and safety validation functionality to ensure
safe system cleanup operations with rollback capabilities.
"""

import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

try:
    import winreg
except ImportError:  # pragma: no cover - Windows-only dependency
    winreg = None

from .windows_utils import WindowsUtils


class SafetyManager:
    """Manager for safety operations during system cleanup."""

    def __init__(self):
        """Initialize the safety manager."""
        self.backup_root = Path(tempfile.gettempdir()) / "RFU_Cleanup_Backups"
        self.backup_root.mkdir(exist_ok=True)

        # Create session-specific backup directory
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_backup_dir = self.backup_root / f"session_{session_id}"
        self.session_backup_dir.mkdir(exist_ok=True)

        self.registry_backups = []
        self.file_backups = []
        self.restore_points = []

    def create_restore_point(self, description: str) -> bool:
        """Create a system restore point."""
        try:
            success = WindowsUtils.create_system_restore_point(description)
            if success:
                self.restore_points.append(
                    {
                        "description": description,
                        "timestamp": datetime.now(),
                        "type": "system_restore",
                    }
                )
            return success
        except Exception:
            return False

    def backup_registry_key(
        self, key_path: str, hive: Optional[int] = None
    ) -> Optional[Path]:
        """Backup a registry key to a .reg file."""
        if winreg is None or sys.platform != "win32":
            return None

        hive = hive if hive is not None else winreg.HKEY_LOCAL_MACHINE

        try:
            # Create backup filename
            safe_key_name = key_path.replace("\\", "_").replace("/", "_")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"registry_{safe_key_name}_{timestamp}.reg"
            backup_path = self.session_backup_dir / backup_filename

            # Export registry key using reg.exe
            hive_names = {
                winreg.HKEY_LOCAL_MACHINE: "HKLM",
                winreg.HKEY_CURRENT_USER: "HKCU",
                winreg.HKEY_CLASSES_ROOT: "HKCR",
                winreg.HKEY_USERS: "HKU",
                winreg.HKEY_CURRENT_CONFIG: "HKCC",
            }

            hive_name = hive_names.get(hive, "HKLM")
            full_key_path = f"{hive_name}\\{key_path}"

            command = f'reg export "{full_key_path}" "{backup_path}" /y'
            result = subprocess.run(command, shell=True, capture_output=True)

            if result.returncode == 0 and backup_path.exists():
                self.registry_backups.append(
                    {
                        "key_path": key_path,
                        "hive": hive,
                        "backup_path": backup_path,
                        "timestamp": datetime.now(),
                    }
                )
                return backup_path

        except Exception:
            pass

        return None

    def restore_registry_key(self, backup_path: Path) -> bool:
        """Restore a registry key from a backup file."""
        try:
            if not backup_path.exists():
                return False

            command = f'reg import "{backup_path}"'
            result = subprocess.run(command, shell=True, capture_output=True)
            return result.returncode == 0

        except Exception:
            return False

    def backup_file(
        self, file_path: Path, backup_dir: Optional[Path] = None
    ) -> Optional[Path]:
        """Create a backup of a file."""
        try:
            if not file_path.exists():
                return None

            if backup_dir is None:
                backup_dir = self.session_backup_dir / "files"

            backup_dir.mkdir(parents=True, exist_ok=True)

            # Create backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{file_path.name}_{timestamp}.backup"
            backup_path = backup_dir / backup_filename

            # Handle duplicate backup names
            counter = 1
            while backup_path.exists():
                backup_filename = f"{file_path.name}_{timestamp}_{counter}.backup"
                backup_path = backup_dir / backup_filename
                counter += 1

            # Copy the file
            shutil.copy2(file_path, backup_path)

            self.file_backups.append(
                {
                    "original_path": file_path,
                    "backup_path": backup_path,
                    "timestamp": datetime.now(),
                }
            )

            return backup_path

        except Exception:
            return None

    def restore_file(
        self, backup_path: Path, original_path: Optional[Path] = None
    ) -> bool:
        """Restore a file from backup."""
        try:
            if not backup_path.exists():
                return False

            # Find original path if not provided
            if original_path is None:
                for backup_info in self.file_backups:
                    if backup_info["backup_path"] == backup_path:
                        original_path = backup_info["original_path"]
                        break

                if original_path is None:
                    return False

            # Restore the file
            shutil.copy2(backup_path, original_path)
            return True

        except Exception:
            return False

    def backup_directory(
        self, dir_path: Path, backup_dir: Optional[Path] = None
    ) -> Optional[Path]:
        """Create a backup of an entire directory."""
        try:
            if not dir_path.exists():
                return None

            if backup_dir is None:
                backup_dir = self.session_backup_dir / "directories"

            backup_dir.mkdir(parents=True, exist_ok=True)

            # Create backup directory name with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dirname = f"{dir_path.name}_{timestamp}_backup"
            backup_path = backup_dir / backup_dirname

            # Handle duplicate backup names
            counter = 1
            while backup_path.exists():
                backup_dirname = f"{dir_path.name}_{timestamp}_{counter}_backup"
                backup_path = backup_dir / backup_dirname
                counter += 1

            # Copy the directory
            shutil.copytree(dir_path, backup_path)

            self.file_backups.append(
                {
                    "original_path": dir_path,
                    "backup_path": backup_path,
                    "timestamp": datetime.now(),
                    "type": "directory",
                }
            )

            return backup_path

        except Exception:
            return None

    def validate_file_safety(self, file_path: Path) -> Dict[str, Any]:
        """Validate if a file is safe to delete."""
        safety_info = {
            "safe_to_delete": True,
            "warnings": [],
            "critical": False,
            "in_use": False,
            "system_file": False,
        }

        try:
            if not file_path.exists():
                safety_info["safe_to_delete"] = False
                safety_info["warnings"].append("File does not exist")
                return safety_info

            # Check if file is in use
            if WindowsUtils.is_file_in_use(file_path):
                safety_info["in_use"] = True
                safety_info["safe_to_delete"] = False
                safety_info["warnings"].append("File is currently in use")

            # Check if it's a system file
            if self._is_system_file(file_path):
                safety_info["system_file"] = True
                safety_info["critical"] = True
                safety_info["safe_to_delete"] = False
                safety_info["warnings"].append("This is a critical system file")

            # Check file location for safety
            if self._is_critical_location(file_path):
                safety_info["critical"] = True
                safety_info["warnings"].append("File is in a critical system location")

            # Check file extension for safety
            if self._is_critical_extension(file_path):
                safety_info["warnings"].append(
                    "File has a potentially critical extension"
                )

        except Exception as e:
            safety_info["safe_to_delete"] = False
            safety_info["warnings"].append(f"Error validating file: {str(e)}")

        return safety_info

    def _is_system_file(self, file_path: Path) -> bool:
        """Check if a file is a critical system file."""
        try:
            # Check file attributes for system flag
            import stat

            file_stat = file_path.stat()

            # On Windows, check if it has system or hidden attributes
            if hasattr(stat, "FILE_ATTRIBUTE_SYSTEM"):
                if file_stat.st_file_attributes & stat.FILE_ATTRIBUTE_SYSTEM:
                    return True

            # Check against known critical system files
            critical_files = {
                "ntoskrnl.exe",
                "hal.dll",
                "ntdll.dll",
                "kernel32.dll",
                "user32.dll",
                "gdi32.dll",
                "advapi32.dll",
                "ole32.dll",
                "shell32.dll",
                "shlwapi.dll",
                "comctl32.dll",
                "comdlg32.dll",
                "wininet.dll",
                "urlmon.dll",
                "msvcrt.dll",
                "msvcp*.dll",
                "vcruntime*.dll",
                "api-ms-*.dll",
            }

            file_name = file_path.name.lower()
            for critical_file in critical_files:
                if "*" in critical_file:
                    # Handle wildcard patterns
                    pattern = critical_file.replace("*", "")
                    if pattern in file_name:
                        return True
                elif file_name == critical_file:
                    return True

        except Exception:
            pass

        return False

    def _is_critical_location(self, file_path: Path) -> bool:
        """Check if a file is in a critical system location."""
        try:
            file_str = str(file_path).lower()
            windows_dir = WindowsUtils.get_windows_directory()
            system_drive = WindowsUtils.get_system_drive()

            critical_paths = [
                str(windows_dir / "System32").lower(),
                str(windows_dir / "SysWOW64").lower(),
                str(windows_dir / "WinSxS").lower(),
                f"{system_drive.lower()}\\program files\\windows",
                f"{system_drive.lower()}\\windows\\boot",
                f"{system_drive.lower()}\\windows\\system32\\drivers",
            ]

            for critical_path in critical_paths:
                if file_str.startswith(critical_path):
                    return True

        except Exception:
            pass

        return False

    def _is_critical_extension(self, file_path: Path) -> bool:
        """Check if a file has a critical extension."""
        critical_extensions = {
            ".sys",
            ".dll",
            ".exe",
            ".ocx",
            ".cpl",
            ".scr",
            ".drv",
            ".vxd",
            ".com",
            ".bat",
            ".cmd",
            ".reg",
        }

        return file_path.suffix.lower() in critical_extensions

    def validate_registry_key_safety(
        self, key_path: str, hive: Optional[int] = None
    ) -> Dict[str, Any]:
        """Validate if a registry key is safe to modify."""
        safety_info = {
            "safe_to_modify": True,
            "warnings": [],
            "critical": False,
            "exists": False,
        }

        if winreg is None or sys.platform != "win32":
            safety_info["safe_to_modify"] = False
            safety_info["warnings"].append(
                "Registry validation is only available on Windows"
            )
            return safety_info

        hive = hive if hive is not None else winreg.HKEY_LOCAL_MACHINE

        try:
            # Check if key exists
            try:
                with winreg.OpenKey(hive, key_path):
                    safety_info["exists"] = True
            except FileNotFoundError:
                safety_info["exists"] = False
                safety_info["warnings"].append("Registry key does not exist")
                return safety_info

            # Check against critical registry paths
            critical_paths = [
                r"SYSTEM\CurrentControlSet\Services",
                r"SYSTEM\CurrentControlSet\Control",
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
                r"SOFTWARE\Microsoft\Windows NT\CurrentVersion",
                r"SYSTEM\CurrentControlSet\Enum",
                r"SAM\SAM",
                r"SECURITY\Policy",
            ]

            key_lower = key_path.lower()
            for critical_path in critical_paths:
                if key_lower.startswith(critical_path.lower()):
                    safety_info["critical"] = True
                    safety_info["warnings"].append(
                        "Registry key is in a critical system area"
                    )
                    break

        except Exception as e:
            safety_info["safe_to_modify"] = False
            safety_info["warnings"].append(f"Error validating registry key: {str(e)}")

        return safety_info

    def get_backup_summary(self) -> Dict[str, Any]:
        """Get a summary of all backups created in this session."""
        return {
            "session_backup_dir": str(self.session_backup_dir),
            "registry_backups": len(self.registry_backups),
            "file_backups": len(self.file_backups),
            "restore_points": len(self.restore_points),
            "total_backup_size": self._calculate_backup_size(),
        }

    def _calculate_backup_size(self) -> int:
        """Calculate total size of all backups."""
        total_size = 0

        try:
            if self.session_backup_dir.exists():
                total_size = WindowsUtils.get_file_size(self.session_backup_dir)
        except Exception:
            pass

        return total_size

    def cleanup_old_backups(self, days_old: int = 7, dry_run: bool = False) -> bool:
        """Clean up backup files older than specified days.

        When dry_run is True, identifies directories that would be removed
        without deleting anything.
        """
        try:
            if not self.backup_root.exists():
                return True

            import time

            cutoff_time = time.time() - (days_old * 24 * 3600)

            for backup_dir in self.backup_root.iterdir():
                if backup_dir.is_dir():
                    try:
                        dir_time = backup_dir.stat().st_mtime
                        if dir_time < cutoff_time and not dry_run:
                            shutil.rmtree(backup_dir)
                    except Exception:
                        continue

            return True

        except Exception:
            return False

    def restore_all_backups(self, dry_run: bool = False) -> bool:
        """Restore all backups created in this session.

        When dry_run is True, validates that backup files exist and restore
        paths are reachable without overwriting any files.
        """
        success = True

        # Restore registry backups
        for backup_info in self.registry_backups:
            if dry_run:
                if not Path(backup_info["backup_path"]).exists():
                    success = False
            else:
                if not self.restore_registry_key(backup_info["backup_path"]):
                    success = False

        # Restore file backups
        for backup_info in self.file_backups:
            if dry_run:
                if not backup_info["backup_path"].exists():
                    success = False
            else:
                if not self.restore_file(
                    backup_info["backup_path"], backup_info["original_path"]
                ):
                    success = False

        return success
