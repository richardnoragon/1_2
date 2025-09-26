#!/usr/bin/env python3
"""
File Splitter Migration Backup Script

Creates comprehensive backup of all file splitter related files before
migration.
"""

import os
import shutil
import json
import hashlib
from datetime import datetime


def create_migration_backup():
    """Create comprehensive backup before migration."""
    
    # Create backup directory with timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    backup_dir = f"backup/file_splitter_migration/{timestamp}"
    os.makedirs(backup_dir, exist_ok=True)
    
    # Files to backup
    files_to_backup = [
        'file_splitter_joiner.py',
        'file_splitter_joiner.ui',
        'tests/test_file_splitter_joiner.py'
    ]
    
    # Create backup manifest
    manifest = {
        'backup_timestamp': timestamp,
        'backup_directory': backup_dir,
        'files_backed_up': [],
        'migration_phase': 'pre_migration',
        'backup_size_bytes': 0,
        'migration_plan_version': '1.0',
        'original_file_hashes': {}
    }
    
    # Backup each file
    total_size = 0
    for file_path in files_to_backup:
        if os.path.exists(file_path):
            # Calculate file size
            file_size = os.path.getsize(file_path)
            total_size += file_size
            
            # Calculate file hash for integrity verification
            with open(file_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            
            # Copy file to backup
            backup_file_path = os.path.join(
                backup_dir, os.path.basename(file_path)
            )
            shutil.copy2(file_path, backup_file_path)
            
            # Add to manifest
            manifest['files_backed_up'].append({
                'original_path': file_path,
                'backup_path': backup_file_path,
                'size_bytes': file_size,
                'backup_timestamp': timestamp,
                'file_hash': file_hash
            })
            
            manifest['original_file_hashes'][file_path] = file_hash
            
            print(f"✅ Backed up: {file_path} -> {backup_file_path}")
        else:
            print(f"⚠️  Warning: File not found: {file_path}")
    
    manifest['backup_size_bytes'] = total_size
    
    # Save manifest
    manifest_path = os.path.join(backup_dir, 'backup_manifest.json')
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"\n🎉 Backup completed successfully!")
    print(f"📁 Backup directory: {backup_dir}")
    print(f"📊 Total files backed up: {len(manifest['files_backed_up'])}")
    print(f"💾 Total backup size: {total_size:,} bytes")
    print(f"📋 Manifest file: {manifest_path}")
    
    return backup_dir, manifest

if __name__ == "__main__":
    create_migration_backup()