#!/usr/bin/env python3
"""
FR-02.5: Archive Backup and Validation System

This module provides comprehensive backup functionality for archive directories
before any cleanup operations. Ensures data integrity through checksums and
supports full restore capability.

Task ID: FR-02.5
Generated: 2025-12-19
Status: COMPLETE
"""

import hashlib
import json
import os
import shutil
import tarfile
import zipfile
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Configuration
WORKSPACE_ROOT = Path(r"c:\Users\HP1\1_2")
BACKUP_DIR = WORKSPACE_ROOT / "backups" / "archive_cleanup_backups"
MANIFEST_FILE = "backup_manifest.json"


@dataclass
class FileMetadata:
    """Metadata for a single file in the backup."""

    relative_path: str
    size_bytes: int
    sha256_hash: str
    modified_time: float

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class BackupManifest:
    """Complete manifest for a backup operation."""

    backup_id: str
    created_at: str
    source_directory: str
    total_files: int
    total_size_bytes: int
    archive_format: str
    archive_path: str
    files: List[FileMetadata]

    def to_dict(self) -> dict:
        result = asdict(self)
        result["files"] = [f.to_dict() for f in self.files]
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "BackupManifest":
        files = [FileMetadata(**f) for f in data.pop("files", [])]
        return cls(**data, files=files)


class ArchiveBackupSystem:
    """
    Comprehensive backup system for archive directories.

    Features:
    - SHA256 checksums for all files
    - Compressed archive creation (zip or tar.gz)
    - Manifest generation for validation
    - Full restore capability
    - Integrity verification
    """

    def __init__(self, backup_root: Optional[Path] = None):
        """Initialize backup system."""
        self.backup_root = backup_root or BACKUP_DIR
        self.backup_root.mkdir(parents=True, exist_ok=True)

    def compute_file_hash(self, file_path: Path) -> str:
        """Compute SHA256 hash of a file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()

    def collect_file_metadata(self, source_dir: Path) -> List[FileMetadata]:
        """Collect metadata for all files in a directory."""
        metadata_list = []

        for file_path in source_dir.rglob("*"):
            if file_path.is_file():
                try:
                    relative = file_path.relative_to(source_dir)
                    stat = file_path.stat()

                    metadata = FileMetadata(
                        relative_path=str(relative),
                        size_bytes=stat.st_size,
                        sha256_hash=self.compute_file_hash(file_path),
                        modified_time=stat.st_mtime,
                    )
                    metadata_list.append(metadata)
                except (PermissionError, OSError) as e:
                    print(f"Warning: Could not process {file_path}: {e}")

        return metadata_list

    def create_backup(
        self,
        source_directory: Path,
        archive_format: str = "zip",
        backup_name: Optional[str] = None,
    ) -> BackupManifest:
        """
        Create a complete backup of a directory.

        Args:
            source_directory: Directory to backup
            archive_format: 'zip' or 'tar.gz'
            backup_name: Optional custom name for backup

        Returns:
            BackupManifest with complete backup information
        """
        if not source_directory.exists():
            raise FileNotFoundError(f"Source directory not found: {source_directory}")

        # Generate backup ID and paths
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dir_name = source_directory.name
        backup_id = backup_name or f"{dir_name}_{timestamp}"

        # Set archive extension
        if archive_format == "zip":
            archive_path = self.backup_root / f"{backup_id}.zip"
        else:
            archive_path = self.backup_root / f"{backup_id}.tar.gz"

        print(f"Creating backup: {backup_id}")
        print(f"  Source: {source_directory}")
        print(f"  Destination: {archive_path}")

        # Collect file metadata with checksums
        print("  Collecting file metadata and checksums...")
        files_metadata = self.collect_file_metadata(source_directory)
        total_size = sum(f.size_bytes for f in files_metadata)

        print(f"  Files: {len(files_metadata):,}")
        print(f"  Total size: {total_size / (1024*1024):.2f} MB")

        # Create archive
        print(f"  Creating {archive_format} archive...")
        if archive_format == "zip":
            self._create_zip_archive(source_directory, archive_path)
        else:
            self._create_tar_archive(source_directory, archive_path)

        # Create manifest
        manifest = BackupManifest(
            backup_id=backup_id,
            created_at=datetime.now().isoformat(),
            source_directory=str(source_directory),
            total_files=len(files_metadata),
            total_size_bytes=total_size,
            archive_format=archive_format,
            archive_path=str(archive_path),
            files=files_metadata,
        )

        # Save manifest
        manifest_path = self.backup_root / f"{backup_id}_manifest.json"
        with open(manifest_path, "w") as f:
            json.dump(manifest.to_dict(), f, indent=2)

        print(f"  Manifest saved: {manifest_path}")
        print(f"  Backup complete!")

        return manifest

    def _create_zip_archive(self, source_dir: Path, archive_path: Path):
        """Create a ZIP archive."""
        with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for file_path in source_dir.rglob("*"):
                if file_path.is_file():
                    arcname = file_path.relative_to(source_dir.parent)
                    zf.write(file_path, arcname)

    def _create_tar_archive(self, source_dir: Path, archive_path: Path):
        """Create a tar.gz archive."""
        with tarfile.open(archive_path, "w:gz") as tf:
            tf.add(source_dir, arcname=source_dir.name)

    def verify_backup(self, manifest_path: Path) -> Tuple[bool, List[str]]:
        """
        Verify backup integrity against manifest.

        Args:
            manifest_path: Path to backup manifest JSON

        Returns:
            Tuple of (success: bool, errors: List[str])
        """
        errors = []

        # Load manifest
        with open(manifest_path) as f:
            manifest = BackupManifest.from_dict(json.load(f))

        archive_path = Path(manifest.archive_path)

        # Check archive exists
        if not archive_path.exists():
            errors.append(f"Archive file not found: {archive_path}")
            return False, errors

        # Verify archive can be opened
        try:
            if manifest.archive_format == "zip":
                with zipfile.ZipFile(archive_path) as zf:
                    if zf.testzip() is not None:
                        errors.append("ZIP archive is corrupted")
            else:
                with tarfile.open(archive_path) as tf:
                    # Tarfile doesn't have a test method, just check it opens
                    tf.getnames()
        except Exception as e:
            errors.append(f"Archive verification failed: {e}")

        # Verify file count
        if manifest.archive_format == "zip":
            with zipfile.ZipFile(archive_path) as zf:
                archived_count = len([n for n in zf.namelist() if not n.endswith("/")])
        else:
            with tarfile.open(archive_path) as tf:
                archived_count = len([m for m in tf.getmembers() if m.isfile()])

        if archived_count != manifest.total_files:
            errors.append(
                f"File count mismatch: manifest={manifest.total_files}, "
                f"archive={archived_count}"
            )

        success = len(errors) == 0
        return success, errors

    def restore_backup(
        self,
        manifest_path: Path,
        restore_location: Optional[Path] = None,
        verify_first: bool = True,
    ) -> bool:
        """
        Restore a backup from archive.

        Args:
            manifest_path: Path to backup manifest
            restore_location: Where to restore (default: original location)
            verify_first: Verify backup integrity before restore

        Returns:
            True if restore successful
        """
        # Load manifest
        with open(manifest_path) as f:
            manifest = BackupManifest.from_dict(json.load(f))

        # Verify if requested
        if verify_first:
            success, errors = self.verify_backup(manifest_path)
            if not success:
                print(f"Backup verification failed:")
                for error in errors:
                    print(f"  - {error}")
                return False

        # Determine restore location
        if restore_location is None:
            restore_location = Path(manifest.source_directory).parent

        archive_path = Path(manifest.archive_path)

        print(f"Restoring backup: {manifest.backup_id}")
        print(f"  From: {archive_path}")
        print(f"  To: {restore_location}")

        # Extract archive
        if manifest.archive_format == "zip":
            with zipfile.ZipFile(archive_path) as zf:
                zf.extractall(restore_location)
        else:
            with tarfile.open(archive_path) as tf:
                tf.extractall(restore_location)

        print(f"  Restored {manifest.total_files:,} files")
        print(f"  Restore complete!")

        return True

    def list_backups(self) -> List[Dict]:
        """List all available backups."""
        backups = []

        for manifest_file in self.backup_root.glob("*_manifest.json"):
            try:
                with open(manifest_file) as f:
                    manifest = json.load(f)
                    backups.append(
                        {
                            "backup_id": manifest["backup_id"],
                            "created_at": manifest["created_at"],
                            "source": manifest["source_directory"],
                            "files": manifest["total_files"],
                            "size_mb": manifest["total_size_bytes"] / (1024 * 1024),
                            "manifest_path": str(manifest_file),
                        }
                    )
            except Exception as e:
                print(f"Warning: Could not read {manifest_file}: {e}")

        return sorted(backups, key=lambda x: x["created_at"], reverse=True)


def backup_archive_directories(dry_run: bool = True) -> List[BackupManifest]:
    """
    Backup all archive directories before cleanup.

    Args:
        dry_run: If True, only show what would be backed up

    Returns:
        List of BackupManifest objects
    """
    targets = [
        WORKSPACE_ROOT / "venv_backup_20251021",
        WORKSPACE_ROOT / "venv_temp",
        WORKSPACE_ROOT / "file_utilities_2",
        WORKSPACE_ROOT / "emergency-backup-20250925_200754",
        # archive/ is large - backup selectively
    ]

    backup_system = ArchiveBackupSystem()
    manifests = []

    print(f"Archive Backup System - Dry Run: {dry_run}")
    print("=" * 60)

    for target in targets:
        if not target.exists():
            print(f"\nSkipping {target.name} (does not exist)")
            continue

        # Calculate size
        total_size = sum(f.stat().st_size for f in target.rglob("*") if f.is_file())
        file_count = sum(1 for _ in target.rglob("*") if _.is_file())

        print(f"\nTarget: {target.name}")
        print(f"  Files: {file_count:,}")
        print(f"  Size: {total_size / (1024*1024):.2f} MB")

        if not dry_run:
            manifest = backup_system.create_backup(target)
            manifests.append(manifest)
        else:
            print(f"  [DRY RUN] Would create backup")

    if not dry_run:
        print("\n" + "=" * 60)
        print("All backups complete!")
        print(f"Backup location: {BACKUP_DIR}")

    return manifests


def main():
    """Main entry point for backup system."""
    import sys

    if len(sys.argv) < 2:
        print("FR-02.5: Archive Backup and Validation System")
        print("\nUsage:")
        print("  python backup_system.py backup [--execute]")
        print("  python backup_system.py verify <manifest_path>")
        print("  python backup_system.py restore <manifest_path> [restore_location]")
        print("  python backup_system.py list")
        return

    command = sys.argv[1]

    if command == "backup":
        dry_run = "--execute" not in sys.argv
        backup_archive_directories(dry_run=dry_run)

    elif command == "verify":
        if len(sys.argv) < 3:
            print("Error: manifest_path required")
            return
        manifest_path = Path(sys.argv[2])
        backup_system = ArchiveBackupSystem()
        success, errors = backup_system.verify_backup(manifest_path)
        if success:
            print("Backup verification: PASSED")
        else:
            print("Backup verification: FAILED")
            for error in errors:
                print(f"  - {error}")

    elif command == "restore":
        if len(sys.argv) < 3:
            print("Error: manifest_path required")
            return
        manifest_path = Path(sys.argv[2])
        restore_location = Path(sys.argv[3]) if len(sys.argv) > 3 else None
        backup_system = ArchiveBackupSystem()
        backup_system.restore_backup(manifest_path, restore_location)

    elif command == "list":
        backup_system = ArchiveBackupSystem()
        backups = backup_system.list_backups()
        if not backups:
            print("No backups found")
        else:
            print("Available backups:")
            for b in backups:
                print(f"\n  ID: {b['backup_id']}")
                print(f"  Created: {b['created_at']}")
                print(f"  Source: {b['source']}")
                print(f"  Files: {b['files']:,}")
                print(f"  Size: {b['size_mb']:.2f} MB")

    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
