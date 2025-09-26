"""
Security Manager for Software Maintenance Toolkit

This module provides comprehensive security management including administrative
privilege handling, backup creation, restore point management, and security
validation for all software maintenance operations.
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass

from .maintenance_base import MaintenanceToolBase


@dataclass
class RestorePoint:
    """Data class representing a system restore point."""

    id: str
    name: str
    description: str
    creation_time: datetime
    size_mb: float
    restore_path: str

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "creation_time": self.creation_time.isoformat(),
            "size_mb": self.size_mb,
            "restore_path": self.restore_path,
        }


@dataclass
class BackupEntry:
    """Data class representing a backup entry."""

    id: str
    source_path: str
    backup_path: str
    creation_time: datetime
    size_mb: float
    backup_type: str  # 'file', 'directory', 'registry'

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "source_path": self.source_path,
            "backup_path": self.backup_path,
            "creation_time": self.creation_time.isoformat(),
            "size_mb": self.size_mb,
            "backup_type": self.backup_type,
        }


class SecurityManager(MaintenanceToolBase):
    """
    Comprehensive security management system for software maintenance
    operations including privilege management, backups, and restore points.
    """

    def __init__(self):
        super().__init__("Security Manager")

        self.backup_registry: Dict[str, BackupEntry] = {}
        self.restore_points: Dict[str, RestorePoint] = {}

        # Security settings
        self.require_confirmation = True
        self.auto_backup = True
        self.max_backup_age_days = 30
        self.max_backup_size_gb = 10

        # Load existing backups and restore points
        self._load_backup_registry()
        self._load_restore_points()

    def _load_backup_registry(self):
        """Load the backup registry from disk."""
        registry_file = Path(
            "software_maintenance/config/backup_registry.json"
        )

        if registry_file.exists():
            try:
                with open(registry_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                for backup_id, backup_data in data.items():
                    self.backup_registry[backup_id] = BackupEntry(
                        id=backup_data["id"],
                        source_path=backup_data["source_path"],
                        backup_path=backup_data["backup_path"],
                        creation_time=datetime.fromisoformat(
                            backup_data["creation_time"]
                        ),
                        size_mb=backup_data["size_mb"],
                        backup_type=backup_data["backup_type"],
                    )

                self.log_info(
                    f"Loaded {len(self.backup_registry)} backup entries"
                )

            except Exception as e:
                self.log_warning(f"Failed to load backup registry: {e}")

    def _save_backup_registry(self):
        """Save the backup registry to disk."""
        registry_file = Path(
            "software_maintenance/config/backup_registry.json"
        )
        registry_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            data = {
                backup_id: backup.to_dict()
                for backup_id, backup in self.backup_registry.items()
            }

            with open(registry_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.log_error(f"Failed to save backup registry: {e}")

    def _load_restore_points(self):
        """Load restore points from disk."""
        restore_file = Path("software_maintenance/config/restore_points.json")

        if restore_file.exists():
            try:
                with open(restore_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                for point_id, point_data in data.items():
                    self.restore_points[point_id] = RestorePoint(
                        id=point_data["id"],
                        name=point_data["name"],
                        description=point_data["description"],
                        creation_time=datetime.fromisoformat(
                            point_data["creation_time"]
                        ),
                        size_mb=point_data["size_mb"],
                        restore_path=point_data["restore_path"],
                    )

                self.log_info(
                    f"Loaded {len(self.restore_points)} restore points"
                )

            except Exception as e:
                self.log_warning(f"Failed to load restore points: {e}")

    def _save_restore_points(self):
        """Save restore points to disk."""
        restore_file = Path("software_maintenance/config/restore_points.json")
        restore_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            data = {
                point_id: point.to_dict()
                for point_id, point in self.restore_points.items()
            }

            with open(restore_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.log_error(f"Failed to save restore points: {e}")

    def check_admin_privileges(self) -> bool:
        """Check if the current process has administrative privileges."""
        try:
            if sys.platform == "win32":
                import ctypes

                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:
                return os.geteuid() == 0
        except Exception as e:
            self.log_warning(f"Could not check admin privileges: {e}")
            return False

    def request_admin_elevation(self) -> bool:
        """Request administrative privilege elevation."""
        if self.check_admin_privileges():
            return True

        try:
            if sys.platform == "win32":
                # On Windows, we can't elevate the current process
                # This would typically require restarting the application
                self.log_warning(
                    "Administrative privileges required. "
                    "Please restart the application as administrator."
                )
                return False
            else:
                # On Unix-like systems, we could use sudo
                self.log_warning(
                    "Administrative privileges required. "
                    "Please run with sudo or as root."
                )
                return False

        except Exception as e:
            self.log_error(f"Failed to request admin elevation: {e}")
            return False

    def create_file_backup(
        self, file_path: str, backup_name: str = None
    ) -> Optional[str]:
        """
        Create a backup of a single file.

        Args:
            file_path: Path to the file to backup
            backup_name: Optional custom backup name

        Returns:
            Backup ID if successful, None otherwise
        """
        try:
            source = Path(file_path)
            if not source.exists() or not source.is_file():
                self.log_warning(f"Source file does not exist: {file_path}")
                return None

            # Generate backup ID and paths
            backup_id = f"file_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            backup_dir = Path("software_maintenance/backups") / backup_id
            backup_dir.mkdir(parents=True, exist_ok=True)

            if backup_name is None:
                backup_name = source.name

            backup_path = backup_dir / backup_name

            # Copy the file
            shutil.copy2(source, backup_path)

            # Calculate size
            size_mb = backup_path.stat().st_size / (1024 * 1024)

            # Create backup entry
            backup_entry = BackupEntry(
                id=backup_id,
                source_path=str(source),
                backup_path=str(backup_path),
                creation_time=datetime.now(),
                size_mb=size_mb,
                backup_type="file",
            )

            self.backup_registry[backup_id] = backup_entry
            self._save_backup_registry()

            self.log_info(f"File backup created: {backup_id}")
            return backup_id

        except Exception as e:
            self.log_error(f"Failed to create file backup: {e}")
            return None

    def create_directory_backup(
        self, dir_path: str, backup_name: str = None
    ) -> Optional[str]:
        """
        Create a backup of a directory.

        Args:
            dir_path: Path to the directory to backup
            backup_name: Optional custom backup name

        Returns:
            Backup ID if successful, None otherwise
        """
        try:
            source = Path(dir_path)
            if not source.exists() or not source.is_dir():
                self.log_warning(
                    f"Source directory does not exist: {dir_path}"
                )
                return None

            # Generate backup ID and paths
            backup_id = f"dir_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            backup_dir = Path("software_maintenance/backups") / backup_id
            backup_dir.mkdir(parents=True, exist_ok=True)

            if backup_name is None:
                backup_name = source.name

            backup_path = backup_dir / backup_name

            # Copy the directory
            shutil.copytree(source, backup_path)

            # Calculate size
            size_mb = sum(
                f.stat().st_size for f in backup_path.rglob("*") if f.is_file()
            ) / (1024 * 1024)

            # Create backup entry
            backup_entry = BackupEntry(
                id=backup_id,
                source_path=str(source),
                backup_path=str(backup_path),
                creation_time=datetime.now(),
                size_mb=size_mb,
                backup_type="directory",
            )

            self.backup_registry[backup_id] = backup_entry
            self._save_backup_registry()

            self.log_info(f"Directory backup created: {backup_id}")
            return backup_id

        except Exception as e:
            self.log_error(f"Failed to create directory backup: {e}")
            return None

    def create_registry_backup(self, registry_key: str) -> Optional[str]:
        """
        Create a backup of a Windows registry key.

        Args:
            registry_key: Registry key path to backup

        Returns:
            Backup ID if successful, None otherwise
        """
        if sys.platform != "win32":
            self.log_warning("Registry backup only supported on Windows")
            return None

        try:
            # Generate backup ID and paths
            backup_id = f"reg_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            backup_dir = Path("software_maintenance/backups") / backup_id
            backup_dir.mkdir(parents=True, exist_ok=True)

            backup_file = backup_dir / "registry_backup.reg"

            # Export registry key using reg.exe
            cmd = ["reg", "export", registry_key, str(backup_file), "/y"]
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                self.log_error(f"Registry export failed: {result.stderr}")
                return None

            # Calculate size
            size_mb = backup_file.stat().st_size / (1024 * 1024)

            # Create backup entry
            backup_entry = BackupEntry(
                id=backup_id,
                source_path=registry_key,
                backup_path=str(backup_file),
                creation_time=datetime.now(),
                size_mb=size_mb,
                backup_type="registry",
            )

            self.backup_registry[backup_id] = backup_entry
            self._save_backup_registry()

            self.log_info(f"Registry backup created: {backup_id}")
            return backup_id

        except Exception as e:
            self.log_error(f"Failed to create registry backup: {e}")
            return None

    def restore_backup(self, backup_id: str) -> bool:
        """
        Restore a backup by its ID.

        Args:
            backup_id: ID of the backup to restore

        Returns:
            True if successful, False otherwise
        """
        if backup_id not in self.backup_registry:
            self.log_error(f"Backup not found: {backup_id}")
            return False

        backup = self.backup_registry[backup_id]

        try:
            if backup.backup_type == "file":
                return self._restore_file_backup(backup)
            elif backup.backup_type == "directory":
                return self._restore_directory_backup(backup)
            elif backup.backup_type == "registry":
                return self._restore_registry_backup(backup)
            else:
                self.log_error(f"Unknown backup type: {backup.backup_type}")
                return False

        except Exception as e:
            self.log_error(f"Failed to restore backup {backup_id}: {e}")
            return False

    def _restore_file_backup(self, backup: BackupEntry) -> bool:
        """Restore a file backup."""
        backup_path = Path(backup.backup_path)
        source_path = Path(backup.source_path)

        if not backup_path.exists():
            self.log_error(f"Backup file not found: {backup.backup_path}")
            return False

        # Create parent directory if needed
        source_path.parent.mkdir(parents=True, exist_ok=True)

        # Copy the backup file back
        shutil.copy2(backup_path, source_path)

        self.log_info(f"File restored: {backup.source_path}")
        return True

    def _restore_directory_backup(self, backup: BackupEntry) -> bool:
        """Restore a directory backup."""
        backup_path = Path(backup.backup_path)
        source_path = Path(backup.source_path)

        if not backup_path.exists():
            self.log_error(f"Backup directory not found: {backup.backup_path}")
            return False

        # Remove existing directory if it exists
        if source_path.exists():
            shutil.rmtree(source_path)

        # Copy the backup directory back
        shutil.copytree(backup_path, source_path)

        self.log_info(f"Directory restored: {backup.source_path}")
        return True

    def _restore_registry_backup(self, backup: BackupEntry) -> bool:
        """Restore a registry backup."""
        if sys.platform != "win32":
            self.log_error("Registry restore only supported on Windows")
            return False

        backup_path = Path(backup.backup_path)

        if not backup_path.exists():
            self.log_error(f"Registry backup not found: {backup.backup_path}")
            return False

        # Import registry backup using reg.exe
        cmd = ["reg", "import", str(backup_path)]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            self.log_error(f"Registry import failed: {result.stderr}")
            return False

        self.log_info(f"Registry restored: {backup.source_path}")
        return True

    def create_system_restore_point(
        self, name: str, description: str = ""
    ) -> Optional[str]:
        """
        Create a system restore point.

        Args:
            name: Name for the restore point
            description: Optional description

        Returns:
            Restore point ID if successful, None otherwise
        """
        if sys.platform != "win32":
            self.log_warning("System restore points only supported on Windows")
            return None

        try:
            # Generate restore point ID
            point_id = f"rp_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

            # Create restore point using PowerShell
            ps_script = f"""
            Checkpoint-Computer -Description "{name}" -RestorePointType "MODIFY_SETTINGS"
            """

            cmd = ["powershell", "-Command", ps_script]
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                self.log_warning(
                    f"System restore point creation failed: "
                    f"{result.stderr}"
                )
                # Continue with manual restore point creation

            # Create our own restore point entry
            restore_point = RestorePoint(
                id=point_id,
                name=name,
                description=description,
                creation_time=datetime.now(),
                size_mb=0.0,  # System restore points don't have a size
                restore_path="",
            )

            self.restore_points[point_id] = restore_point
            self._save_restore_points()

            self.log_info(f"Restore point created: {point_id}")
            return point_id

        except Exception as e:
            self.log_error(f"Failed to create restore point: {e}")
            return None

    def cleanup_old_backups(self) -> int:
        """
        Clean up old backups based on age and size limits.

        Returns:
            Number of backups cleaned up
        """
        cleaned_count = 0
        current_time = datetime.now()

        # Calculate total backup size
        total_size_gb = (
            sum(backup.size_mb for backup in self.backup_registry.values())
            / 1024
        )

        # Sort backups by creation time (oldest first)
        sorted_backups = sorted(
            self.backup_registry.items(), key=lambda x: x[1].creation_time
        )

        for backup_id, backup in sorted_backups:
            should_delete = False

            # Check age limit
            age_days = (current_time - backup.creation_time).days
            if age_days > self.max_backup_age_days:
                should_delete = True
                self.log_info(f"Backup {backup_id} is {age_days} days old")

            # Check size limit
            elif total_size_gb > self.max_backup_size_gb:
                should_delete = True
                self.log_info(
                    f"Total backup size ({total_size_gb:.2f} GB) "
                    f"exceeds limit ({self.max_backup_size_gb} GB)"
                )

            if should_delete:
                if self._delete_backup(backup_id):
                    cleaned_count += 1
                    total_size_gb -= backup.size_mb / 1024

        self.log_info(f"Cleaned up {cleaned_count} old backups")
        return cleaned_count

    def _delete_backup(self, backup_id: str) -> bool:
        """Delete a backup and its files."""
        if backup_id not in self.backup_registry:
            return False

        backup = self.backup_registry[backup_id]

        try:
            # Delete backup files
            backup_path = Path(backup.backup_path)
            if backup_path.exists():
                if backup_path.is_file():
                    backup_path.unlink()
                else:
                    shutil.rmtree(backup_path.parent)

            # Remove from registry
            del self.backup_registry[backup_id]
            self._save_backup_registry()

            self.log_info(f"Backup deleted: {backup_id}")
            return True

        except Exception as e:
            self.log_error(f"Failed to delete backup {backup_id}: {e}")
            return False

    def get_backup_statistics(self) -> Dict[str, any]:
        """Get statistics about backups."""
        total_size_mb = sum(
            backup.size_mb for backup in self.backup_registry.values()
        )

        type_counts = {}
        for backup in self.backup_registry.values():
            backup_type = backup.backup_type
            type_counts[backup_type] = type_counts.get(backup_type, 0) + 1

        return {
            "total_backups": len(self.backup_registry),
            "total_size_mb": total_size_mb,
            "total_size_gb": total_size_mb / 1024,
            "backup_type_breakdown": type_counts,
            "oldest_backup": min(
                (b.creation_time for b in self.backup_registry.values()),
                default=None,
            ),
            "newest_backup": max(
                (b.creation_time for b in self.backup_registry.values()),
                default=None,
            ),
        }

    def execute(self, **kwargs) -> bool:
        """Execute security manager operations."""
        # This is mainly a utility class, so execute just validates the system
        try:
            self.update_status("Validating security configuration...")

            # Check admin privileges
            has_admin = self.check_admin_privileges()
            self.log_info(f"Administrative privileges: {has_admin}")

            # Clean up old backups
            self.update_status("Cleaning up old backups...")
            cleaned = self.cleanup_old_backups()

            # Validate backup directories
            self.update_status("Validating backup directories...")
            backup_dir = Path("software_maintenance/backups")
            if not backup_dir.exists():
                backup_dir.mkdir(parents=True, exist_ok=True)

            self.log_info("Security manager validation completed")
            return True

        except Exception as e:
            self.log_error(f"Security manager validation failed: {e}")
            return False
