#!/usr/bin/env python3
"""
Rollback script for restoring tag_viewer_editor files from backup.

This script provides safe restoration of files from timestamped backups
with integrity verification and safety checks.
"""

import os
import shutil
import hashlib
from pathlib import Path
from typing import List, Optional


class BackupRestorer:
    """Handles safe restoration of tag_viewer_editor files from backup."""
    
    def __init__(self):
        self.backup_base_dir = Path('backup/tag_viewer_editor_migration')
        self.target_files = [
            'tag_viewer_editor.py',
            'tag_viewer_editor.ui'
        ]
    
    def calculate_checksum(self, file_path: str) -> str:
        """Calculate SHA256 checksum for a file."""
        hash_obj = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_obj.update(chunk)
            return hash_obj.hexdigest()
        except Exception as e:
            print(f"❌ Error calculating checksum for {file_path}: {e}")
            return ""
    
    def list_available_backups(self) -> List[str]:
        """List all available backup timestamps."""
        if not self.backup_base_dir.exists():
            return []
        
        backups = []
        for item in self.backup_base_dir.iterdir():
            if item.is_dir() and self.is_valid_backup(item):
                backups.append(item.name)
        
        return sorted(backups, reverse=True)  # Most recent first
    
    def is_valid_backup(self, backup_dir: Path) -> bool:
        """Check if a backup directory contains valid backup files."""
        manifest_file = backup_dir / 'backup_manifest.txt'
        if not manifest_file.exists():
            return False
        
        # Check if all target files exist in backup
        for file_name in self.target_files:
            backup_file = backup_dir / file_name
            if not backup_file.exists():
                return False
        
        return True
    
    def read_manifest(self, backup_dir: Path) -> dict:
        """Read backup manifest and extract metadata."""
        manifest_file = backup_dir / 'backup_manifest.txt'
        manifest_data = {}
        
        try:
            with open(manifest_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Extract basic info (simple parsing)
            lines = content.split('\n')
            for line in lines:
                if line.startswith('Backup Timestamp:'):
                    manifest_data['timestamp'] = line.split(':', 1)[1].strip()
                elif line.startswith('Backup Location:'):
                    manifest_data['location'] = line.split(':', 1)[1].strip()
                elif 'Backup Status:' in line:
                    status = line.split(':', 1)[1].strip()
                    manifest_data['status'] = status
            
            return manifest_data
            
        except Exception as e:
            print(f"❌ Error reading manifest: {e}")
            return {}
    
    def backup_current_files(self) -> bool:
        """Create backup of current files before restoration."""
        print("🔄 Creating safety backup of current files...")
        
        safety_backup_dir = Path('backup/pre_restore_safety')
        safety_backup_dir.mkdir(parents=True, exist_ok=True)
        
        for file_name in self.target_files:
            if os.path.exists(file_name):
                try:
                    source = Path(file_name)
                    destination = safety_backup_dir / f"{file_name}.pre_restore"
                    shutil.copy2(source, destination)
                    print(f"✅ Safety backup: {file_name}")
                except Exception as e:
                    print(f"❌ Failed to create safety backup for {file_name}: {e}")
                    return False
        
        return True
    
    def restore_files(self, backup_timestamp: str) -> bool:
        """Restore files from specified backup."""
        backup_dir = self.backup_base_dir / backup_timestamp
        
        if not self.is_valid_backup(backup_dir):
            print(f"❌ Invalid backup: {backup_timestamp}")
            return False
        
        print(f"📋 Restoring files from backup: {backup_timestamp}")
        
        # Create safety backup first
        if not self.backup_current_files():
            print("❌ Failed to create safety backup!")
            return False
        
        # Restore each file
        for file_name in self.target_files:
            backup_file = backup_dir / file_name
            target_file = Path(file_name)
            
            try:
                # Copy file
                shutil.copy2(backup_file, target_file)
                
                # Verify restoration
                if target_file.exists():
                    backup_size = backup_file.stat().st_size
                    restored_size = target_file.stat().st_size
                    
                    if backup_size == restored_size:
                        print(f"✅ Restored: {file_name} ({restored_size} bytes)")
                    else:
                        print(f"❌ Size mismatch after restore: {file_name}")
                        return False
                else:
                    print(f"❌ File not restored: {file_name}")
                    return False
                    
            except Exception as e:
                print(f"❌ Failed to restore {file_name}: {e}")
                return False
        
        return True
    
    def verify_restoration(self, backup_timestamp: str) -> bool:
        """Verify that restored files match backup checksums."""
        print("🔍 Verifying restoration integrity...")
        
        backup_dir = self.backup_base_dir / backup_timestamp
        
        for file_name in self.target_files:
            backup_file = backup_dir / file_name
            restored_file = Path(file_name)
            
            if not restored_file.exists():
                print(f"❌ Restored file missing: {file_name}")
                return False
            
            # Calculate checksums
            backup_checksum = self.calculate_checksum(str(backup_file))
            restored_checksum = self.calculate_checksum(str(restored_file))
            
            if backup_checksum == restored_checksum:
                print(f"✅ {file_name}: Integrity verified")
            else:
                print(f"❌ {file_name}: Checksum mismatch!")
                return False
        
        return True
    
    def interactive_restore(self):
        """Interactive restoration process."""
        print("🔄 TagViewerEditor Backup Restoration Tool")
        print("=" * 50)
        
        # List available backups
        backups = self.list_available_backups()
        
        if not backups:
            print("❌ No backups found!")
            print(f"Expected location: {self.backup_base_dir}")
            return False
        
        print(f"📋 Available backups ({len(backups)} found):")
        for i, backup in enumerate(backups, 1):
            backup_dir = self.backup_base_dir / backup
            manifest = self.read_manifest(backup_dir)
            status = manifest.get('status', 'UNKNOWN')
            print(f"  {i}. {backup} - Status: {status}")
        
        # Get user selection
        while True:
            try:
                choice = input(f"\nSelect backup (1-{len(backups)}) or 'q' to quit: ")
                if choice.lower() == 'q':
                    print("Restoration cancelled.")
                    return False
                
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(backups):
                    selected_backup = backups[choice_idx]
                    break
                else:
                    print(f"Invalid choice. Enter 1-{len(backups)}")
            except ValueError:
                print("Invalid input. Enter a number or 'q'")
        
        # Show backup details
        backup_dir = self.backup_base_dir / selected_backup
        manifest = self.read_manifest(backup_dir)
        
        print(f"\n📄 Backup Details:")
        print(f"  Timestamp: {manifest.get('timestamp', 'Unknown')}")
        print(f"  Status: {manifest.get('status', 'Unknown')}")
        print(f"  Location: {backup_dir}")
        
        # Confirm restoration
        confirm = input(f"\n⚠️  This will overwrite current files. Continue? (y/N): ")
        if confirm.lower() != 'y':
            print("Restoration cancelled.")
            return False
        
        # Perform restoration
        if self.restore_files(selected_backup):
            if self.verify_restoration(selected_backup):
                print("\n✅ Restoration completed successfully!")
                print("🔍 All files verified and restored.")
                return True
            else:
                print("\n❌ Restoration verification failed!")
                return False
        else:
            print("\n❌ Restoration failed!")
            return False


def main():
    """Main execution function."""
    restorer = BackupRestorer()
    success = restorer.interactive_restore()
    
    if success:
        print("\n🎯 Files successfully restored from backup!")
    else:
        print("\n⚠️  Restoration process failed or was cancelled.")
    
    return success


if __name__ == "__main__":
    main()