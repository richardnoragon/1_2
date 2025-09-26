"""
Advanced Folders Backup and Restore System

This module provides automated backup and manual restore capabilities
for Advanced Folders configurations with versioning and integrity checks.
"""

import hashlib
import json
import logging
import shutil
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .folder_configuration import FolderConfigurationManager
from .import_export import ImportExportManager


class BackupError(Exception):
    """Base exception for backup operations."""
    pass


class RestoreError(Exception):
    """Base exception for restore operations."""
    pass


class BackupMetadata:
    """Metadata for backup files."""
    
    def __init__(self, backup_path: Path):
        self.backup_path = backup_path
        self.created_date: Optional[datetime] = None
        self.configuration_count: int = 0
        self.file_size: int = 0
        self.checksum: str = ""
        self.version: str = "1.0"
        self.description: str = ""
        
    def calculate_checksum(self) -> str:
        """Calculate SHA-256 checksum of backup file."""
        if not self.backup_path.exists():
            return ""
        
        sha256_hash = hashlib.sha256()
        with open(self.backup_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        
        self.checksum = sha256_hash.hexdigest()
        return self.checksum
    
    def update_metadata(self):
        """Update metadata from backup file."""
        if self.backup_path.exists():
            stat = self.backup_path.stat()
            self.file_size = stat.st_size
            self.created_date = datetime.fromtimestamp(stat.st_mtime)
            self.calculate_checksum()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'backup_path': str(self.backup_path),
            'created_date': self.created_date.isoformat() if self.created_date else None,
            'configuration_count': self.configuration_count,
            'file_size': self.file_size,
            'checksum': self.checksum,
            'version': self.version,
            'description': self.description
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BackupMetadata':
        """Create instance from dictionary."""
        backup = cls(Path(data['backup_path']))
        backup.configuration_count = data.get('configuration_count', 0)
        backup.file_size = data.get('file_size', 0)
        backup.checksum = data.get('checksum', '')
        backup.version = data.get('version', '1.0')
        backup.description = data.get('description', '')
        
        if data.get('created_date'):
            backup.created_date = datetime.fromisoformat(data['created_date'])
        
        return backup


class AutomaticBackupScheduler:
    """Handles automated backup scheduling."""
    
    def __init__(self, backup_manager: 'BackupManager'):
        self.backup_manager = backup_manager
        self.logger = logging.getLogger('AdvancedFolders.AutoBackup')
        self._last_backup: Optional[datetime] = None
        self._backup_interval: timedelta = timedelta(hours=24)  # Daily by default
        self._enabled = True
        
    def set_backup_interval(self, hours: int):
        """Set backup interval in hours."""
        self._backup_interval = timedelta(hours=hours)
    
    def enable_automatic_backup(self, enabled: bool):
        """Enable or disable automatic backups."""
        self._enabled = enabled
        self.logger.info(f"Automatic backup {'enabled' if enabled else 'disabled'}")
    
    def is_backup_due(self) -> bool:
        """Check if a backup is due."""
        if not self._enabled:
            return False
        
        if self._last_backup is None:
            return True
        
        return datetime.now() - self._last_backup >= self._backup_interval
    
    def perform_automatic_backup(self) -> bool:
        """Perform automatic backup if due."""
        if not self.is_backup_due():
            return True
        
        try:
            backup_path = self.backup_manager.create_automatic_backup()
            if backup_path:
                self._last_backup = datetime.now()
                self.logger.info(f"Automatic backup completed: {backup_path}")
                return True
            else:
                self.logger.error("Automatic backup failed")
                return False
        
        except Exception as e:
            self.logger.error(f"Automatic backup error: {e}")
            return False
    
    def get_next_backup_time(self) -> Optional[datetime]:
        """Get the next scheduled backup time."""
        if not self._enabled or self._last_backup is None:
            return None
        
        return self._last_backup + self._backup_interval


class BackupManager:
    """Manages backup and restore operations for Advanced Folders configurations."""
    
    def __init__(self, config_manager: FolderConfigurationManager, 
                 backup_directory: Optional[Path] = None):
        """Initialize backup manager.
        
        Args:
            config_manager: Configuration manager instance
            backup_directory: Directory for storing backups (default: config/backups)
        """
        self.config_manager = config_manager
        self.import_export_manager = ImportExportManager(config_manager)
        self.logger = logging.getLogger('AdvancedFolders.BackupManager')
        
        # Set backup directory
        if backup_directory:
            self.backup_directory = backup_directory
        else:
            self.backup_directory = Path("config/backups/advanced_folders")
        
        # Ensure backup directory exists
        self.backup_directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize automatic backup scheduler
        self.auto_scheduler = AutomaticBackupScheduler(self)
        
        # Metadata file for tracking backups
        self.metadata_file = self.backup_directory / "backup_metadata.json"
        self._backup_metadata: Dict[str, BackupMetadata] = {}
        self._load_backup_metadata()
    
    def create_backup(self, description: str = "", 
                     automatic: bool = False,
                     **options) -> Optional[Path]:
        """Create a backup of all configurations.
        
        Args:
            description: Optional description for the backup
            automatic: Whether this is an automatic backup
            
        Returns:
            Path to created backup file or None if failed
        """
        try:
            # Generate backup filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_type = "auto" if automatic else "manual"
            backup_filename = f"advanced_folders_{backup_type}_{timestamp}.zip"
            backup_path = self.backup_directory / backup_filename
            
            # Create backup using import/export manager
            success = self.import_export_manager.export_configurations(
                backup_path,
                include_statistics=True,
                compress=True,
                **options
            )
            
            if success:
                # Create and store metadata
                metadata = BackupMetadata(backup_path)
                metadata.update_metadata()
                metadata.configuration_count = len(self.config_manager.list_folders())
                metadata.description = description
                
                self._backup_metadata[str(backup_path)] = metadata
                self._save_backup_metadata()
                
                # Clean up old backups if needed
                if automatic:
                    self._cleanup_old_automatic_backups()
                
                self.logger.info(f"Backup created successfully: {backup_path}")
                return backup_path
            else:
                self.logger.error("Failed to create backup")
                return None
        
        except Exception as e:
            self.logger.error(f"Backup creation failed: {e}")
            return None
    
    def create_automatic_backup(self, **options) -> Optional[Path]:
        """Create an automatic backup."""
        return self.create_backup(
            description="Automatic backup",
            automatic=True,
            **options
        )
    
    def restore_backup(self, backup_path: Path, 
                      conflict_resolution: str = 'prompt',
                      verify_integrity: bool = True,
                      create_restore_point: bool = True,
                      **options) -> Tuple[bool, List[str]]:
        """Restore configurations from backup.
        
        Args:
            backup_path: Path to backup file
            conflict_resolution: How to handle conflicts
            verify_integrity: Whether to verify backup integrity
            
        Returns:
            Tuple of (success, messages)
        """
        try:
            # Verify backup file exists
            if not backup_path.exists():
                return False, [f"Backup file not found: {backup_path}"]
            
            # Verify integrity if requested
            if verify_integrity:
                integrity_ok, integrity_msg = self.verify_backup_integrity(backup_path)
                if not integrity_ok:
                    return False, [f"Integrity check failed: {integrity_msg}"]
            
            # Create restore point before proceeding (optional)
            if create_restore_point:
                restore_point = self.create_restore_point(**options)
                if not restore_point:
                    # Log warning but don't fail the restore
                    self.logger.warning("Failed to create restore point, continuing with restore")
                    restore_point_msg = "Warning: Could not create restore point"
                else:
                    restore_point_msg = f"Restore point created: {restore_point}"
            else:
                restore_point_msg = "Restore point creation skipped"
            
            # Perform import
            success, messages = self.import_export_manager.import_configurations(
                backup_path,
                conflict_resolution=conflict_resolution,
                **options
            )
            
            if success:
                messages.append(f"Restore completed from: {backup_path}")
                messages.append(restore_point_msg)
                self.logger.info(f"Restore completed from: {backup_path}")
            else:
                self.logger.error(f"Restore failed from: {backup_path}")
            
            return success, messages
        
        except Exception as e:
            self.logger.error(f"Restore operation failed: {e}")
            return False, [f"Restore failed: {e}"]
    
    def create_restore_point(self, **options) -> Optional[Path]:
        """Create a restore point before making changes."""
        return self.create_backup(
            description="Restore point - created before restore operation",
            **options
        )
    
    def list_backups(self, backup_type: Optional[str] = None) -> List[BackupMetadata]:
        """List available backups.
        
        Args:
            backup_type: Filter by backup type ('auto', 'manual', or None for all)
            
        Returns:
            List of backup metadata, sorted by creation date (newest first)
        """
        backups = []
        
        for metadata in self._backup_metadata.values():
            if backup_type:
                if backup_type == 'auto' and 'auto' not in metadata.backup_path.name:
                    continue
                elif backup_type == 'manual' and 'manual' not in metadata.backup_path.name:
                    continue
            
            # Update metadata if file still exists
            if metadata.backup_path.exists():
                metadata.update_metadata()
                backups.append(metadata)
            else:
                # Remove metadata for missing files
                self._backup_metadata.pop(str(metadata.backup_path), None)
        
        # Sort by creation date (newest first)
        backups.sort(key=lambda x: x.created_date or datetime.min, reverse=True)
        
        # Save updated metadata
        self._save_backup_metadata()
        
        return backups
    
    def delete_backup(self, backup_path: Path) -> bool:
        """Delete a backup file and its metadata.
        
        Args:
            backup_path: Path to backup file to delete
            
        Returns:
            True if deleted successfully
        """
        try:
            if backup_path.exists():
                backup_path.unlink()
            
            # Remove from metadata
            self._backup_metadata.pop(str(backup_path), None)
            self._save_backup_metadata()
            
            self.logger.info(f"Backup deleted: {backup_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to delete backup {backup_path}: {e}")
            return False
    
    def verify_backup_integrity(self, backup_path: Path) -> Tuple[bool, str]:
        """Verify backup file integrity.
        
        Args:
            backup_path: Path to backup file
            
        Returns:
            Tuple of (is_valid, message)
        """
        try:
            # Check if file exists
            if not backup_path.exists():
                return False, "Backup file does not exist"
            
            # Get stored metadata
            metadata = self._backup_metadata.get(str(backup_path))
            if not metadata:
                return False, "No metadata found for backup"
            
            # Calculate current checksum
            current_checksum = metadata.calculate_checksum()
            
            # Compare with stored checksum
            if current_checksum != metadata.checksum:
                return False, "Checksum mismatch - file may be corrupted"
            
            # Try to read and validate the backup file without importing
            # Create a temporary manager for validation
            temp_manager = FolderConfigurationManager()
            temp_ie_manager = ImportExportManager(temp_manager)
            
            # Use a non-existent config file to avoid loading existing configs
            import tempfile
            with tempfile.NamedTemporaryFile() as tmp:
                temp_manager._config_file = Path(tmp.name + "_validation.json")
                
                success, messages = temp_ie_manager.import_configurations(
                    backup_path,
                    conflict_resolution='rename',  # Allow import for validation
                    validate_paths=False  # Skip path validation during integrity check
                )
            
            if not success:
                return False, f"Backup file is corrupted: {messages}"
            
            return True, "Backup integrity verified"
        
        except Exception as e:
            return False, f"Integrity verification failed: {e}"
    
    def _cleanup_old_automatic_backups(self, keep_count: int = 7):
        """Clean up old automatic backups, keeping only the most recent ones.
        
        Args:
            keep_count: Number of automatic backups to keep
        """
        try:
            auto_backups = [b for b in self.list_backups('auto')]
            
            if len(auto_backups) > keep_count:
                # Delete oldest backups
                backups_to_delete = auto_backups[keep_count:]
                
                for backup in backups_to_delete:
                    self.delete_backup(backup.backup_path)
                
                self.logger.info(f"Cleaned up {len(backups_to_delete)} old automatic backups")
        
        except Exception as e:
            self.logger.error(f"Failed to cleanup old backups: {e}")
    
    def _load_backup_metadata(self):
        """Load backup metadata from file."""
        try:
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for path_str, metadata_dict in data.items():
                    metadata = BackupMetadata.from_dict(metadata_dict)
                    self._backup_metadata[path_str] = metadata
        
        except Exception as e:
            self.logger.error(f"Failed to load backup metadata: {e}")
    
    def _save_backup_metadata(self):
        """Save backup metadata to file."""
        try:
            data = {}
            for path_str, metadata in self._backup_metadata.items():
                data[path_str] = metadata.to_dict()
            
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        
        except Exception as e:
            self.logger.error(f"Failed to save backup metadata: {e}")
    
    def get_backup_statistics(self) -> Dict[str, Any]:
        """Get backup system statistics.
        
        Returns:
            Dictionary with backup statistics
        """
        backups = self.list_backups()
        auto_backups = self.list_backups('auto')
        manual_backups = self.list_backups('manual')
        
        total_size = sum(b.file_size for b in backups)
        
        stats = {
            'total_backups': len(backups),
            'automatic_backups': len(auto_backups),
            'manual_backups': len(manual_backups),
            'total_size_bytes': total_size,
            'total_size_mb': total_size / (1024 * 1024),
            'oldest_backup': backups[-1].created_date if backups else None,
            'newest_backup': backups[0].created_date if backups else None,
            'backup_directory': str(self.backup_directory),
            'automatic_backup_enabled': self.auto_scheduler._enabled,
            'next_automatic_backup': self.auto_scheduler.get_next_backup_time()
        }
        
        return stats
    
    def configure_automatic_backup(self, enabled: bool, interval_hours: int = 24):
        """Configure automatic backup settings.
        
        Args:
            enabled: Whether to enable automatic backups
            interval_hours: Backup interval in hours
        """
        self.auto_scheduler.enable_automatic_backup(enabled)
        self.auto_scheduler.set_backup_interval(interval_hours)
        
        self.logger.info(f"Automatic backup configured: enabled={enabled}, interval={interval_hours}h")
    
    def perform_maintenance(self):
        """Perform maintenance tasks for the backup system."""
        try:
            # Check for automatic backup
            self.auto_scheduler.perform_automatic_backup()
            
            # Clean up orphaned metadata
            orphaned_paths = []
            for path_str in self._backup_metadata:
                if not Path(path_str).exists():
                    orphaned_paths.append(path_str)
            
            for path_str in orphaned_paths:
                self._backup_metadata.pop(path_str, None)
            
            if orphaned_paths:
                self._save_backup_metadata()
                self.logger.info(f"Cleaned up {len(orphaned_paths)} orphaned metadata entries")
        
        except Exception as e:
            self.logger.error(f"Backup maintenance failed: {e}")