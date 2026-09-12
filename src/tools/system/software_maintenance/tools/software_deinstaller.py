"""
Powerful Software De-Installer for Software Maintenance Toolkit

This module provides comprehensive software uninstallation capabilities including
deep system scanning, complete removal with leftover cleanup, batch uninstallation,
restore points, disk space analysis, and uninstallation history tracking.
"""

import os
import json
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime
from dataclasses import dataclass

try:
    import winreg
except ImportError:  # pragma: no cover - Windows-only dependency
    winreg = None

from ..core.maintenance_base import MaintenanceToolBase
from ..core.software_detector import SoftwareDetector, SoftwareInfo
from ..core.security_manager import SecurityManager
from ..core.platform_support import PlatformSupport


@dataclass
class UninstallSession:
    """Data class representing an uninstallation session."""

    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_software: int = 0
    successful_removals: int = 0
    failed_removals: int = 0
    space_recovered_mb: float = 0.0
    software_removed: List[str] = None

    def __post_init__(self):
        if self.software_removed is None:
            self.software_removed = []

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "session_id": self.session_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "total_software": self.total_software,
            "successful_removals": self.successful_removals,
            "failed_removals": self.failed_removals,
            "space_recovered_mb": self.space_recovered_mb,
            "software_removed": self.software_removed,
        }


@dataclass
class LeftoverItem:
    """Data class representing leftover files or registry entries."""

    item_type: str  # 'file', 'directory', 'registry'
    path: str
    size_mb: float = 0.0
    last_modified: Optional[datetime] = None
    is_safe_to_remove: bool = False

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "item_type": self.item_type,
            "path": self.path,
            "size_mb": self.size_mb,
            "last_modified": (
                self.last_modified.isoformat() if self.last_modified else None
            ),
            "is_safe_to_remove": self.is_safe_to_remove,
        }


@dataclass
class UninstallAnalysis:
    """Data class representing uninstallation analysis results."""

    software_name: str
    estimated_size_mb: float
    install_location: str
    registry_entries: List[str]
    leftover_files: List[LeftoverItem]
    dependencies: List[str]
    is_system_component: bool
    uninstall_complexity: str  # 'simple', 'moderate', 'complex'

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "software_name": self.software_name,
            "estimated_size_mb": self.estimated_size_mb,
            "install_location": self.install_location,
            "registry_entries": self.registry_entries,
            "leftover_files": [item.to_dict() for item in self.leftover_files],
            "dependencies": self.dependencies,
            "is_system_component": self.is_system_component,
            "uninstall_complexity": self.uninstall_complexity,
        }


class SoftwareDeinstaller(MaintenanceToolBase):
    """
    Powerful Software De-Installer providing comprehensive uninstallation
    capabilities with deep scanning and advanced cleanup features.
    """

    def __init__(self):
        super().__init__("Software De-Installer")

        # Initialize core components
        self.software_detector = SoftwareDetector()
        self.security_manager = SecurityManager()
        self.platform_support = PlatformSupport()

        # Uninstallation management
        self.detected_software: Dict[str, SoftwareInfo] = {}
        self.uninstall_history: List[UninstallSession] = []
        self.leftover_cache: Dict[str, List[LeftoverItem]] = {}

        # Settings
        self.create_restore_points = True
        self.backup_before_removal = True
        self.deep_scan_enabled = True
        self.auto_cleanup_leftovers = False

        # Common leftover locations
        self.common_leftover_paths = self._get_common_leftover_paths()

        # Load configuration and history
        self._load_configuration()
        self._load_uninstall_history()

        self.require_admin = True

    def _get_common_leftover_paths(self) -> List[str]:
        """Get common paths where software leftovers are found."""
        paths = []

        if self.platform_support.platform_type.value == "windows":
            system_paths = self.platform_support.system_paths
            paths.extend(
                [
                    system_paths.get("appdata", ""),
                    system_paths.get("localappdata", ""),
                    system_paths.get("programdata", ""),
                    os.path.join(
                        system_paths.get("userprofile", ""), "Documents"
                    ),
                    "C:\\ProgramData",
                    "C:\\Users\\Public",
                ]
            )
        elif self.platform_support.platform_type.value == "macos":
            paths.extend(
                [
                    os.path.expanduser("~/Library/Application Support"),
                    os.path.expanduser("~/Library/Preferences"),
                    os.path.expanduser("~/Library/Caches"),
                    "/Library/Application Support",
                    "/Library/Preferences",
                ]
            )
        elif self.platform_support.platform_type.value == "linux":
            paths.extend(
                [
                    os.path.expanduser("~/.config"),
                    os.path.expanduser("~/.local/share"),
                    os.path.expanduser("~/.cache"),
                    "/etc",
                    "/usr/share",
                ]
            )

        # Filter out empty paths and verify they exist
        return [path for path in paths if path and os.path.exists(path)]

    def _load_configuration(self):
        """Load de-installer configuration from file."""
        config_file = Path(
            "software_maintenance/config/deinstaller_config.json"
        )

        if config_file.exists():
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)

                self.create_restore_points = config.get(
                    "create_restore_points", True
                )
                self.backup_before_removal = config.get(
                    "backup_before_removal", True
                )
                self.deep_scan_enabled = config.get("deep_scan_enabled", True)
                self.auto_cleanup_leftovers = config.get(
                    "auto_cleanup_leftovers", False
                )

                self.log_info("De-installer configuration loaded successfully")

            except Exception as e:
                self.log_warning(
                    f"Failed to load de-installer configuration: {e}"
                )

    def _save_configuration(self):
        """Save de-installer configuration to file."""
        config_file = Path(
            "software_maintenance/config/deinstaller_config.json"
        )
        config_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            config = {
                "create_restore_points": self.create_restore_points,
                "backup_before_removal": self.backup_before_removal,
                "deep_scan_enabled": self.deep_scan_enabled,
                "auto_cleanup_leftovers": self.auto_cleanup_leftovers,
            }

            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.log_error(f"Failed to save de-installer configuration: {e}")

    def _load_uninstall_history(self):
        """Load uninstallation history from file."""
        history_file = Path(
            "software_maintenance/config/uninstall_history.json"
        )

        if history_file.exists():
            try:
                with open(history_file, "r", encoding="utf-8") as f:
                    history_data = json.load(f)

                self.uninstall_history = []
                for session_data in history_data:
                    session = UninstallSession(
                        session_id=session_data["session_id"],
                        start_time=datetime.fromisoformat(
                            session_data["start_time"]
                        ),
                        end_time=(
                            datetime.fromisoformat(session_data["end_time"])
                            if session_data.get("end_time")
                            else None
                        ),
                        total_software=session_data["total_software"],
                        successful_removals=session_data[
                            "successful_removals"
                        ],
                        failed_removals=session_data["failed_removals"],
                        space_recovered_mb=session_data["space_recovered_mb"],
                        software_removed=session_data["software_removed"],
                    )
                    self.uninstall_history.append(session)

                self.log_info(
                    f"Loaded {len(self.uninstall_history)} uninstall sessions"
                )

            except Exception as e:
                self.log_warning(f"Failed to load uninstall history: {e}")

    def _save_uninstall_history(self):
        """Save uninstallation history to file."""
        history_file = Path(
            "software_maintenance/config/uninstall_history.json"
        )
        history_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            history_data = [
                session.to_dict() for session in self.uninstall_history
            ]

            with open(history_file, "w", encoding="utf-8") as f:
                json.dump(history_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.log_error(f"Failed to save uninstall history: {e}")

    def scan_installed_software(
        self, include_system: bool = False
    ) -> Dict[str, SoftwareInfo]:
        """
        Scan for installed software using the software detector.

        Args:
            include_system: Include system components in scan

        Returns:
            Dictionary of detected software
        """
        self.update_status("Scanning installed software...")

        try:
            success = self.software_detector.run(
                include_system=include_system, save_results=True
            )

            if success:
                self.detected_software = (
                    self.software_detector.detected_software
                )
                self.log_info(
                    f"Found {len(self.detected_software)} installed applications"
                )
                return self.detected_software
            else:
                self.log_error("Software scan failed")
                return {}

        except Exception as e:
            self.log_error(f"Error scanning software: {e}")
            return {}

    def analyze_software_for_removal(
        self, software_name: str
    ) -> Optional[UninstallAnalysis]:
        """
        Perform deep analysis of software for uninstallation.

        Args:
            software_name: Name of the software to analyze

        Returns:
            UninstallAnalysis object or None if not found
        """
        if software_name not in self.detected_software:
            self.log_error(f"Software not found: {software_name}")
            return None

        software_info = self.detected_software[software_name]

        try:
            self.update_status(f"Analyzing {software_name} for removal...")

            # Estimate size
            estimated_size = software_info.size_mb or 0.0
            if estimated_size == 0.0 and software_info.install_location:
                estimated_size = self._calculate_directory_size(
                    software_info.install_location
                )

            # Find registry entries
            registry_entries = self._find_registry_entries(software_name)

            # Find leftover files
            leftover_files = self._find_potential_leftovers(software_name)

            # Check dependencies
            dependencies = self._find_dependencies(software_name)

            # Determine complexity
            complexity = self._determine_uninstall_complexity(
                software_info, registry_entries, leftover_files, dependencies
            )

            analysis = UninstallAnalysis(
                software_name=software_name,
                estimated_size_mb=estimated_size,
                install_location=software_info.install_location,
                registry_entries=registry_entries,
                leftover_files=leftover_files,
                dependencies=dependencies,
                is_system_component=software_info.is_system_component,
                uninstall_complexity=complexity,
            )

            self.log_info(
                f"Analysis completed for {software_name}: {complexity} complexity"
            )
            return analysis

        except Exception as e:
            self.log_error(f"Error analyzing {software_name}: {e}")
            return None

    def _calculate_directory_size(self, directory_path: str) -> float:
        """Calculate the total size of a directory in MB."""
        try:
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(directory_path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(filepath)
                    except (OSError, FileNotFoundError):
                        continue

            return total_size / (1024 * 1024)  # Convert to MB

        except Exception as e:
            self.log_warning(
                f"Could not calculate directory size for {directory_path}: {e}"
            )
            return 0.0

    def _find_registry_entries(self, software_name: str) -> List[str]:
        """Find registry entries related to the software."""
        registry_entries = []

        if self.platform_support.platform_type.value != "windows":
            return registry_entries

        try:
            # Search common registry locations
            search_paths = [
                (
                    winreg.HKEY_LOCAL_MACHINE,
                    r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
                ),
                (
                    winreg.HKEY_LOCAL_MACHINE,
                    r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
                ),
                (
                    winreg.HKEY_CURRENT_USER,
                    r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
                ),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE"),
                (winreg.HKEY_CURRENT_USER, r"SOFTWARE"),
            ]

            for hive, base_path in search_paths:
                try:
                    with winreg.OpenKey(hive, base_path) as key:
                        self._search_registry_recursive(
                            key,
                            base_path,
                            software_name,
                            registry_entries,
                            hive,
                        )
                except FileNotFoundError:
                    continue

        except Exception as e:
            self.log_warning(
                f"Error searching registry for {software_name}: {e}"
            )

        return registry_entries

    def _search_registry_recursive(
        self,
        key,
        path: str,
        software_name: str,
        results: List[str],
        hive,
        max_depth: int = 3,
    ):
        """Recursively search registry for software-related entries."""
        if max_depth <= 0:
            return

        try:
            i = 0
            while True:
                try:
                    subkey_name = winreg.EnumKey(key, i)

                    # Check if subkey name contains software name
                    if software_name.lower() in subkey_name.lower():
                        full_path = f"{path}\\{subkey_name}"
                        if full_path not in results:
                            results.append(full_path)

                    # Recursively search subkey
                    try:
                        with winreg.OpenKey(key, subkey_name) as subkey:
                            subpath = f"{path}\\{subkey_name}"
                            self._search_registry_recursive(
                                subkey,
                                subpath,
                                software_name,
                                results,
                                hive,
                                max_depth - 1,
                            )
                    except (FileNotFoundError, PermissionError):
                        pass

                    i += 1

                except OSError:
                    break

        except Exception as e:
            self.log_warning(f"Error in recursive registry search: {e}")

    def _find_potential_leftovers(
        self, software_name: str
    ) -> List[LeftoverItem]:
        """Find potential leftover files and directories."""
        leftovers = []

        try:
            # Search common leftover locations
            for search_path in self.common_leftover_paths:
                if not os.path.exists(search_path):
                    continue

                try:
                    for item in os.listdir(search_path):
                        item_path = os.path.join(search_path, item)

                        # Check if item name contains software name
                        if software_name.lower() in item.lower():
                            leftover = self._create_leftover_item(item_path)
                            if leftover:
                                leftovers.append(leftover)

                except (PermissionError, FileNotFoundError):
                    continue

        except Exception as e:
            self.log_warning(
                f"Error finding leftovers for {software_name}: {e}"
            )

        return leftovers

    def _create_leftover_item(self, item_path: str) -> Optional[LeftoverItem]:
        """Create a LeftoverItem from a file or directory path."""
        try:
            path_obj = Path(item_path)

            if not path_obj.exists():
                return None

            # Determine item type and size
            if path_obj.is_file():
                item_type = "file"
                size_mb = path_obj.stat().st_size / (1024 * 1024)
            elif path_obj.is_dir():
                item_type = "directory"
                size_mb = self._calculate_directory_size(str(path_obj))
            else:
                return None

            # Get last modified time
            last_modified = datetime.fromtimestamp(path_obj.stat().st_mtime)

            # Determine if safe to remove (basic heuristics)
            is_safe = self._is_safe_to_remove(str(path_obj))

            return LeftoverItem(
                item_type=item_type,
                path=str(path_obj),
                size_mb=size_mb,
                last_modified=last_modified,
                is_safe_to_remove=is_safe,
            )

        except Exception as e:
            self.log_warning(
                f"Error creating leftover item for {item_path}: {e}"
            )
            return None

    def _is_safe_to_remove(self, item_path: str) -> bool:
        """Determine if an item is safe to remove using basic heuristics."""
        try:
            path_obj = Path(item_path)

            # Never remove system directories
            system_dirs = ["Windows", "System32", "Program Files", "Users"]
            if any(sys_dir in str(path_obj) for sys_dir in system_dirs):
                return False

            # Check if it's in a user-specific location
            user_dirs = [
                "AppData",
                "Documents",
                "Desktop",
                ".config",
                ".local",
            ]
            if any(user_dir in str(path_obj) for user_dir in user_dirs):
                return True

            # Check file extensions that are typically safe to remove
            if path_obj.is_file():
                safe_extensions = [".log", ".tmp", ".cache", ".bak", ".old"]
                if path_obj.suffix.lower() in safe_extensions:
                    return True

            return False

        except Exception:
            return False

    def _find_dependencies(self, software_name: str) -> List[str]:
        """Find software dependencies (simplified implementation)."""
        dependencies = []

        try:
            # This is a simplified implementation
            # In a real-world scenario, you would check:
            # - Shared libraries
            # - Registry dependencies
            # - File associations
            # - Service dependencies

            # For now, just check if other software has similar names
            for other_software in self.detected_software.keys():
                if (
                    other_software != software_name
                    and software_name.lower() in other_software.lower()
                ):
                    dependencies.append(other_software)

        except Exception as e:
            self.log_warning(
                f"Error finding dependencies for {software_name}: {e}"
            )

        return dependencies

    def _determine_uninstall_complexity(
        self,
        software_info: SoftwareInfo,
        registry_entries: List[str],
        leftover_files: List[LeftoverItem],
        dependencies: List[str],
    ) -> str:
        """Determine the complexity of uninstalling the software."""
        complexity_score = 0

        # System component adds complexity
        if software_info.is_system_component:
            complexity_score += 3

        # Registry entries add complexity
        complexity_score += min(len(registry_entries) // 5, 2)

        # Leftover files add complexity
        complexity_score += min(len(leftover_files) // 10, 2)

        # Dependencies add complexity
        complexity_score += min(len(dependencies), 2)

        # No uninstall string adds complexity
        if not software_info.uninstall_string:
            complexity_score += 2

        if complexity_score <= 2:
            return "simple"
        elif complexity_score <= 5:
            return "moderate"
        else:
            return "complex"

    def create_pre_removal_backup(self, software_name: str) -> Optional[str]:
        """
        Create backup before removing software.

        Args:
            software_name: Name of the software to backup

        Returns:
            Backup ID if successful, None otherwise
        """
        if not self.backup_before_removal:
            return None

        try:
            if software_name in self.detected_software:
                software_info = self.detected_software[software_name]

                # Create directory backup if install location exists
                if (
                    software_info.install_location
                    and Path(software_info.install_location).exists()
                ):
                    backup_id = self.security_manager.create_directory_backup(
                        software_info.install_location,
                        f"{software_name}_pre_removal",
                    )

                    if backup_id:
                        self.log_info(
                            f"Created backup for {software_name}: {backup_id}"
                        )
                        return backup_id

                # Create registry backup if available
                if software_info.registry_key:
                    backup_id = self.security_manager.create_registry_backup(
                        software_info.registry_key
                    )

                    if backup_id:
                        self.log_info(
                            f"Created registry backup for {software_name}: {backup_id}"
                        )
                        return backup_id

            self.log_warning(f"Could not create backup for {software_name}")
            return None

        except Exception as e:
            self.log_error(f"Error creating backup for {software_name}: {e}")
            return None

    def uninstall_software(
        self, software_name: str, remove_leftovers: bool = None
    ) -> bool:
        """
        Uninstall a specific software package.

        Args:
            software_name: Name of the software to uninstall
            remove_leftovers: Whether to remove leftover files

        Returns:
            True if successful, False otherwise
        """
        if software_name not in self.detected_software:
            self.log_error(f"Software not found: {software_name}")
            return False

        software_info = self.detected_software[software_name]

        try:
            self.update_status(f"Uninstalling {software_name}...")

            # Create restore point if enabled
            if self.create_restore_points:
                restore_point_id = self.security_manager.create_system_restore_point(
                    f"Before uninstalling {software_name}",
                    "Automatic restore point created by Software De-Installer",
                )

            # Create backup if enabled
            backup_id = self.create_pre_removal_backup(software_name)

            # Perform the uninstallation
            success = self._execute_uninstall(software_info)

            if success:
                self.log_info(f"Successfully uninstalled {software_name}")

                # Remove leftovers if requested
                if remove_leftovers or (
                    remove_leftovers is None and self.auto_cleanup_leftovers
                ):
                    self._cleanup_leftovers(software_name)

                # Remove from detected software
                del self.detected_software[software_name]

                return True
            else:
                self.log_error(f"Failed to uninstall {software_name}")

                # Offer to restore backup if uninstall failed
                if backup_id:
                    self.log_info(
                        f"Backup available for restoration: {backup_id}"
                    )

                return False

        except Exception as e:
            self.log_error(f"Error uninstalling {software_name}: {e}")
            return False

    def _execute_uninstall(self, software_info: SoftwareInfo) -> bool:
        """Execute the actual uninstallation process."""
        try:
            # Try using the uninstall string first
            if software_info.uninstall_string:
                return self._run_uninstall_command(
                    software_info.uninstall_string
                )

            # Try package manager uninstall
            if software_info.package_manager != "registry":
                return self._uninstall_via_package_manager(
                    software_info.name, software_info.package_manager
                )

            # Manual removal as last resort
            self.log_warning(
                f"No uninstall method found for {software_info.name}, attempting manual removal"
            )
            return self._manual_removal(software_info)

        except Exception as e:
            self.log_error(
                f"Error executing uninstall for {software_info.name}: {e}"
            )
            return False

    def _run_uninstall_command(self, uninstall_string: str) -> bool:
        """Run the software's uninstall command."""
        try:
            # Parse the uninstall string
            if uninstall_string.startswith('"'):
                # Handle quoted paths
                end_quote = uninstall_string.find('"', 1)
                if end_quote != -1:
                    command = uninstall_string[1:end_quote]
                    args = uninstall_string[end_quote + 1 :].strip()
                else:
                    command = uninstall_string
                    args = ""
            else:
                # Handle unquoted paths
                parts = uninstall_string.split(" ", 1)
                command = parts[0]
                args = parts[1] if len(parts) > 1 else ""

            # Add silent uninstall flags if not present
            if (
                "/S" not in args
                and "/SILENT" not in args
                and "/quiet" not in args
            ):
                args += " /S"

            # Execute the uninstall command
            full_command = f'"{command}" {args}'.strip()
            result = subprocess.run(
                full_command, shell=True, capture_output=True, timeout=300
            )

            return result.returncode == 0

        except Exception as e:
            self.log_error(f"Error running uninstall command: {e}")
            return False

    def _uninstall_via_package_manager(
        self, software_name: str, package_manager: str
    ) -> bool:
        """Uninstall software via package manager."""
        try:
            if package_manager == "chocolatey":
                result = subprocess.run(
                    ["choco", "uninstall", software_name, "-y"],
                    capture_output=True,
                    timeout=300,
                )
                return result.returncode == 0

            elif package_manager == "winget":
                result = subprocess.run(
                    ["winget", "uninstall", software_name, "--silent"],
                    capture_output=True,
                    timeout=300,
                )
                return result.returncode == 0

            elif package_manager == "homebrew":
                result = subprocess.run(
                    ["brew", "uninstall", software_name],
                    capture_output=True,
                    timeout=300,
                )
                return result.returncode == 0

            elif package_manager == "apt":
                result = subprocess.run(
                    ["sudo", "apt", "remove", software_name, "-y"],
                    capture_output=True,
                    timeout=300,
                )
                return result.returncode == 0

            else:
                self.log_warning(
                    f"Unsupported package manager: {package_manager}"
                )
                return False

        except Exception as e:
            self.log_error(f"Error uninstalling via {package_manager}: {e}")
            return False

    def _manual_removal(self, software_info: SoftwareInfo) -> bool:
        """Perform manual removal of software files and registry entries."""
        try:
            success = True

            # Remove installation directory
            if (
                software_info.install_location
                and Path(software_info.install_location).exists()
            ):
                try:
                    shutil.rmtree(software_info.install_location)
                    self.log_info(
                        f"Removed installation directory: {software_info.install_location}"
                    )
                except Exception as e:
                    self.log_error(
                        f"Failed to remove installation directory: {e}"
                    )
                    success = False

            # Remove registry entries
            if (
                software_info.registry_key
                and self.platform_support.platform_type.value == "windows"
            ):
                try:
                    self._remove_registry_key(software_info.registry_key)
                    self.log_info(
                        f"Removed registry key: {software_info.registry_key}"
                    )
                except Exception as e:
                    self.log_error(f"Failed to remove registry key: {e}")
                    success = False

            return success

        except Exception as e:
            self.log_error(f"Error in manual removal: {e}")
            return False

    def _remove_registry_key(self, registry_key: str):
        """Remove a registry key."""
        try:
            # Parse registry key path
            if registry_key.startswith("HKEY_LOCAL_MACHINE"):
                hive = winreg.HKEY_LOCAL_MACHINE
                subkey = registry_key.replace("HKEY_LOCAL_MACHINE\\", "")
            elif registry_key.startswith("HKEY_CURRENT_USER"):
                hive = winreg.HKEY_CURRENT_USER
                subkey = registry_key.replace("HKEY_CURRENT_USER\\", "")
            else:
                raise ValueError(
                    f"Unsupported registry hive in: {registry_key}"
                )

            # Delete the registry key
            winreg.DeleteKey(hive, subkey)

        except Exception as e:
            self.log_error(f"Error removing registry key {registry_key}: {e}")
            raise

    def _cleanup_leftovers(self, software_name: str):
        """Clean up leftover files and registry entries."""
        try:
            if software_name not in self.leftover_cache:
                # Find leftovers if not cached
                leftovers = self._find_potential_leftovers(software_name)
                self.leftover_cache[software_name] = leftovers
            else:
                leftovers = self.leftover_cache[software_name]

            removed_count = 0
            for leftover in leftovers:
                if leftover.is_safe_to_remove:
                    try:
                        if leftover.item_type == "file":
                            os.remove(leftover.path)
                        elif leftover.item_type == "directory":
                            shutil.rmtree(leftover.path)

                        removed_count += 1
                        self.log_info(f"Removed leftover: {leftover.path}")

                    except Exception as e:
                        self.log_warning(
                            f"Failed to remove leftover {leftover.path}: {e}"
                        )

            self.log_info(
                f"Cleaned up {removed_count} leftover items for {software_name}"
            )

        except Exception as e:
            self.log_error(
                f"Error cleaning up leftovers for {software_name}: {e}"
            )

    def uninstall_multiple_software(
        self, software_list: List[str], remove_leftovers: bool = None
    ) -> Dict[str, bool]:
        """
        Uninstall multiple software packages.

        Args:
            software_list: List of software names to uninstall
            remove_leftovers: Whether to remove leftover files

        Returns:
            Dictionary mapping software names to success status
        """
        results = {}
        total_removals = len(software_list)
        total_space_recovered = 0.0

        # Create uninstall session
        session = UninstallSession(
            session_id=f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            start_time=datetime.now(),
            total_software=total_removals,
        )

        try:
            for i, software_name in enumerate(software_list):
                if self.is_cancelled:
                    break

                progress = int(((i + 1) / total_removals) * 100)
                self.update_progress(percentage=progress)

                # Calculate space before removal
                space_before = 0.0
                if software_name in self.detected_software:
                    software_info = self.detected_software[software_name]
                    space_before = software_info.size_mb or 0.0
                    if space_before == 0.0 and software_info.install_location:
                        space_before = self._calculate_directory_size(
                            software_info.install_location
                        )

                success = self.uninstall_software(
                    software_name, remove_leftovers
                )
                results[software_name] = success

                if success:
                    session.successful_removals += 1
                    session.software_removed.append(software_name)
                    total_space_recovered += space_before
                else:
                    session.failed_removals += 1

            # Complete session
            session.end_time = datetime.now()
            session.space_recovered_mb = total_space_recovered
            self.uninstall_history.append(session)
            self._save_uninstall_history()

            self.log_info(
                f"Batch uninstall completed: {session.successful_removals}/{total_removals} successful"
            )
            self.log_info(f"Space recovered: {total_space_recovered:.2f} MB")

        except Exception as e:
            self.log_error(f"Error in batch uninstall: {e}")
            session.end_time = datetime.now()
            session.space_recovered_mb = total_space_recovered
            self.uninstall_history.append(session)
            self._save_uninstall_history()

        return results

    def rollback_removal(self, software_name: str, backup_id: str) -> bool:
        """
        Rollback a software removal using a backup.

        Args:
            software_name: Name of the software to restore
            backup_id: ID of the backup to restore

        Returns:
            True if successful, False otherwise
        """
        try:
            self.update_status(f"Rolling back removal of {software_name}...")

            success = self.security_manager.restore_backup(backup_id)

            if success:
                self.log_info(
                    f"Successfully rolled back removal of {software_name}"
                )
                return True
            else:
                self.log_error(
                    f"Failed to rollback removal of {software_name}"
                )
                return False

        except Exception as e:
            self.log_error(
                f"Error rolling back removal of {software_name}: {e}"
            )
            return False

    def analyze_disk_space_recovery(
        self, software_list: List[str]
    ) -> Dict[str, float]:
        """
        Analyze potential disk space recovery from removing software.

        Args:
            software_list: List of software names to analyze

        Returns:
            Dictionary mapping software names to estimated space recovery in MB
        """
        space_analysis = {}

        try:
            for software_name in software_list:
                if software_name in self.detected_software:
                    software_info = self.detected_software[software_name]

                    # Get size from software info
                    estimated_space = software_info.size_mb or 0.0

                    # If no size info, calculate from install location
                    if (
                        estimated_space == 0.0
                        and software_info.install_location
                    ):
                        estimated_space = self._calculate_directory_size(
                            software_info.install_location
                        )

                    # Add potential leftover space
                    leftovers = self._find_potential_leftovers(software_name)
                    leftover_space = sum(item.size_mb for item in leftovers)

                    total_space = estimated_space + leftover_space
                    space_analysis[software_name] = total_space

                else:
                    space_analysis[software_name] = 0.0

            self.log_info(
                f"Disk space analysis completed for {len(software_list)} applications"
            )

        except Exception as e:
            self.log_error(f"Error analyzing disk space recovery: {e}")

        return space_analysis

    def get_uninstall_statistics(self) -> Dict[str, any]:
        """Get comprehensive uninstallation statistics."""
        total_sessions = len(self.uninstall_history)
        total_removals = sum(
            session.successful_removals for session in self.uninstall_history
        )
        total_failures = sum(
            session.failed_removals for session in self.uninstall_history
        )
        total_space_recovered = sum(
            session.space_recovered_mb for session in self.uninstall_history
        )

        # Recent activity (last 30 days)
        from datetime import timedelta

        recent_cutoff = datetime.now() - timedelta(days=30)
        recent_sessions = [
            s for s in self.uninstall_history if s.start_time >= recent_cutoff
        ]
        recent_removals = sum(
            session.successful_removals for session in recent_sessions
        )
        recent_space_recovered = sum(
            session.space_recovered_mb for session in recent_sessions
        )

        return {
            "total_sessions": total_sessions,
            "total_successful_removals": total_removals,
            "total_failed_removals": total_failures,
            "total_space_recovered_mb": total_space_recovered,
            "total_space_recovered_gb": total_space_recovered / 1024,
            "recent_removals_30_days": recent_removals,
            "recent_space_recovered_30_days": recent_space_recovered,
            "detected_software": len(self.detected_software),
            "cached_leftovers": len(self.leftover_cache),
        }

    def save_uninstall_report(self, filename: str = None) -> str:
        """Save uninstallation analysis to a report file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"uninstall_report_{timestamp}.json"

        filepath = Path("software_maintenance/reports") / filename

        try:
            # Analyze all detected software
            analyses = {}
            for software_name in self.detected_software.keys():
                analysis = self.analyze_software_for_removal(software_name)
                if analysis:
                    analyses[software_name] = analysis.to_dict()

            report_data = {
                "scan_date": datetime.now().isoformat(),
                "total_software": len(self.detected_software),
                "uninstall_analyses": analyses,
                "statistics": self.get_uninstall_statistics(),
            }

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)

            self.log_info(f"Uninstall report saved to: {filepath}")
            return str(filepath)

        except Exception as e:
            self.log_error(f"Failed to save uninstall report: {e}")
            return ""

    def execute(
        self,
        scan_software: bool = True,
        analyze_all: bool = False,
        include_system: bool = False,
        save_report: bool = True,
    ) -> bool:
        """
        Execute comprehensive software uninstallation analysis.

        Args:
            scan_software: Perform software scanning
            analyze_all: Analyze all software for removal
            include_system: Include system components
            save_report: Save analysis report

        Returns:
            True if successful, False otherwise
        """
        try:
            steps = []
            if scan_software:
                steps.append("Software Scan")
            if analyze_all:
                steps.append("Analyze Software")
            if save_report:
                steps.append("Save Report")

            self.set_progress_steps(steps)

            # Scan installed software
            if scan_software:
                self.next_step("Scanning installed software")
                self.scan_installed_software(include_system)

            # Analyze all software if requested
            if analyze_all:
                self.next_step("Analyzing software for removal")
                for software_name in self.detected_software.keys():
                    if self.is_cancelled:
                        break
                    self.analyze_software_for_removal(software_name)

            # Save report
            if save_report:
                self.next_step("Saving analysis report")
                self.save_uninstall_report()

            self.log_info(
                "Software uninstallation analysis completed successfully"
            )
            return True

        except Exception as e:
            self.log_error(f"Software uninstallation analysis failed: {e}")
            return False
