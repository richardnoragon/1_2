#!/usr/bin/env python3
"""
Comprehensive backup script for tag_viewer_editor files before migration.

This script creates a timestamped backup with integrity verification,
checksums, and a detailed manifest for rollback procedures.
"""

import os
import shutil
import hashlib
import datetime
from pathlib import Path
from typing import Dict, Tuple, List


class TagViewerEditorBackup:
    """Handles comprehensive backup of tag_viewer_editor files."""
    
    def __init__(self):
        self.source_files = [
            'tag_viewer_editor.py',
            'tag_viewer_editor.ui'
        ]
        self.backup_base_dir = Path('backup/tag_viewer_editor_migration')
        self.timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        self.backup_dir = self.backup_base_dir / self.timestamp
        self.checksums = {}
        
    def calculate_checksum(self, file_path: str, algorithm: str = 'sha256') -> str:
        """Calculate checksum for a file."""
        hash_obj = hashlib.new(algorithm)
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_obj.update(chunk)
            return hash_obj.hexdigest()
        except Exception as e:
            print(f"❌ Error calculating checksum for {file_path}: {e}")
            return ""
    
    def verify_source_files(self) -> bool:
        """Verify that all source files exist and are readable."""
        print("🔍 Verifying source files...")
        
        for file_path in self.source_files:
            if not os.path.exists(file_path):
                print(f"❌ Source file not found: {file_path}")
                return False
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    f.read(100)  # Test readability
                
                size = os.path.getsize(file_path)
                print(f"✅ {file_path}: EXISTS ({size} bytes)")
                
            except Exception as e:
                print(f"❌ Cannot read source file {file_path}: {e}")
                return False
        
        return True
    
    def create_backup_directory(self) -> bool:
        """Create the timestamped backup directory structure."""
        print(f"📁 Creating backup directory: {self.backup_dir}")
        
        try:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            print(f"✅ Backup directory created: {self.backup_dir}")
            return True
        except Exception as e:
            print(f"❌ Failed to create backup directory: {e}")
            return False
    
    def backup_files(self) -> bool:
        """Copy source files to backup location."""
        print("📋 Copying files to backup location...")
        
        for file_path in self.source_files:
            try:
                source = Path(file_path)
                destination = self.backup_dir / source.name
                
                # Copy file
                shutil.copy2(source, destination)
                
                # Verify copy
                if destination.exists():
                    source_size = source.stat().st_size
                    dest_size = destination.stat().st_size
                    
                    if source_size == dest_size:
                        print(f"✅ {file_path} → {destination} ({dest_size} bytes)")
                    else:
                        print(f"❌ Size mismatch for {file_path}: {source_size} vs {dest_size}")
                        return False
                else:
                    print(f"❌ Backup file not created: {destination}")
                    return False
                    
            except Exception as e:
                print(f"❌ Failed to backup {file_path}: {e}")
                return False
        
        return True
    
    def generate_checksums(self) -> bool:
        """Generate checksums for both original and backup files."""
        print("🔐 Generating checksums...")
        
        for file_path in self.source_files:
            try:
                # Original file checksum
                original_checksum = self.calculate_checksum(file_path)
                if not original_checksum:
                    return False
                
                # Backup file checksum
                backup_file = self.backup_dir / Path(file_path).name
                backup_checksum = self.calculate_checksum(str(backup_file))
                if not backup_checksum:
                    return False
                
                # Store checksums
                self.checksums[file_path] = {
                    'original': original_checksum,
                    'backup': backup_checksum,
                    'match': original_checksum == backup_checksum
                }
                
                status = "✅" if original_checksum == backup_checksum else "❌"
                print(f"{status} {file_path}: {original_checksum[:16]}...")
                
            except Exception as e:
                print(f"❌ Checksum generation failed for {file_path}: {e}")
                return False
        
        return True
    
    def create_manifest(self) -> bool:
        """Create backup manifest with metadata."""
        print("📄 Creating backup manifest...")
        
        manifest_path = self.backup_dir / 'backup_manifest.txt'
        
        try:
            with open(manifest_path, 'w', encoding='utf-8') as f:
                f.write("TAG VIEWER EDITOR BACKUP MANIFEST\n")
                f.write("=" * 50 + "\n\n")
                
                f.write(f"Backup Timestamp: {self.timestamp}\n")
                f.write(f"Backup Location: {self.backup_dir.absolute()}\n")
                f.write(f"Migration Context: Pre-migration safety backup\n")
                f.write(f"Created By: create_tag_viewer_editor_backup.py\n\n")
                
                f.write("BACKED UP FILES:\n")
                f.write("-" * 20 + "\n")
                
                for file_path in self.source_files:
                    original_path = Path(file_path).absolute()
                    backup_path = self.backup_dir / Path(file_path).name
                    original_size = original_path.stat().st_size
                    backup_size = backup_path.stat().st_size
                    
                    f.write(f"\nFile: {file_path}\n")
                    f.write(f"  Original Path: {original_path}\n")
                    f.write(f"  Original Size: {original_size} bytes\n")
                    f.write(f"  Backup Path: {backup_path}\n")
                    f.write(f"  Backup Size: {backup_size} bytes\n")
                    f.write(f"  SHA256 (Original): {self.checksums[file_path]['original']}\n")
                    f.write(f"  SHA256 (Backup): {self.checksums[file_path]['backup']}\n")
                    f.write(f"  Integrity Check: {'PASS' if self.checksums[file_path]['match'] else 'FAIL'}\n")
                
                f.write(f"\nBACKUP SUMMARY:\n")
                f.write("-" * 15 + "\n")
                f.write(f"Total Files: {len(self.source_files)}\n")
                f.write(f"All Checksums Match: {'YES' if all(c['match'] for c in self.checksums.values()) else 'NO'}\n")
                f.write(f"Backup Status: {'SUCCESSFUL' if all(c['match'] for c in self.checksums.values()) else 'FAILED'}\n")
                
                f.write(f"\nROLLBACK INSTRUCTIONS:\n")
                f.write("-" * 22 + "\n")
                f.write(f"To restore files from this backup:\n")
                f.write(f"1. Run: python backup_restore.py\n")
                f.write(f"2. Select backup: {self.timestamp}\n")
                f.write(f"3. Confirm restoration\n\n")
                f.write(f"Manual restoration:\n")
                for file_path in self.source_files:
                    backup_file = self.backup_dir / Path(file_path).name
                    f.write(f"  copy \"{backup_file}\" \"{file_path}\"\n")
            
            print(f"✅ Manifest created: {manifest_path}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create manifest: {e}")
            return False
    
    def verify_backup_integrity(self) -> bool:
        """Verify backup integrity by comparing checksums."""
        print("🔍 Verifying backup integrity...")
        
        all_match = True
        for file_path, checksums in self.checksums.items():
            if checksums['match']:
                print(f"✅ {file_path}: Integrity verified")
            else:
                print(f"❌ {file_path}: Checksum mismatch!")
                all_match = False
        
        return all_match
    
    def test_backup_readability(self) -> bool:
        """Test that backup files are readable."""
        print("📖 Testing backup file readability...")
        
        for file_path in self.source_files:
            backup_file = self.backup_dir / Path(file_path).name
            try:
                with open(backup_file, 'r', encoding='utf-8') as f:
                    content = f.read(100)  # Read first 100 chars
                print(f"✅ {backup_file.name}: Readable")
            except Exception as e:
                print(f"❌ {backup_file.name}: Read error - {e}")
                return False
        
        return True
    
    def run_backup(self) -> bool:
        """Execute the complete backup process."""
        print("🚀 Starting TagViewerEditor backup process...")
        print("=" * 60)
        
        # Step 1: Verify source files
        if not self.verify_source_files():
            print("❌ Source file verification failed!")
            return False
        
        # Step 2: Create backup directory
        if not self.create_backup_directory():
            print("❌ Backup directory creation failed!")
            return False
        
        # Step 3: Copy files
        if not self.backup_files():
            print("❌ File backup failed!")
            return False
        
        # Step 4: Generate checksums
        if not self.generate_checksums():
            print("❌ Checksum generation failed!")
            return False
        
        # Step 5: Create manifest
        if not self.create_manifest():
            print("❌ Manifest creation failed!")
            return False
        
        # Step 6: Verify integrity
        if not self.verify_backup_integrity():
            print("❌ Backup integrity verification failed!")
            return False
        
        # Step 7: Test readability
        if not self.test_backup_readability():
            print("❌ Backup readability test failed!")
            return False
        
        print("\n" + "=" * 60)
        print("🎯 BACKUP COMPLETED SUCCESSFULLY!")
        print(f"📁 Backup Location: {self.backup_dir.absolute()}")
        print(f"📄 Manifest: {self.backup_dir / 'backup_manifest.txt'}")
        print(f"🔐 All checksums verified")
        print(f"📋 Files backed up: {len(self.source_files)}")
        
        return True


def main():
    """Main execution function."""
    backup = TagViewerEditorBackup()
    success = backup.run_backup()
    
    if success:
        print("\n✅ Backup process completed successfully!")
        print("🔒 Files are safely backed up and ready for migration.")
    else:
        print("\n❌ Backup process failed!")
        print("⚠️  Do not proceed with migration until backup is successful.")
    
    return success


if __name__ == "__main__":
    main()