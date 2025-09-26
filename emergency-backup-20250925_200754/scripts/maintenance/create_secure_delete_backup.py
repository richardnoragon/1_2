#!/usr/bin/env python3
"""
Secure Delete Migration Backup Script
Creates comprehensive backup of secure_delete files before migration.
"""

import os
import shutil
import hashlib
import json
from datetime import datetime
from pathlib import Path

def calculate_file_hash(file_path):
    """Calculate SHA256 hash of a file."""
    hash_sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    except Exception as e:
        return f"Error: {str(e)}"

def create_backup():
    """Create comprehensive backup of secure_delete files."""
    # Create backup directory with timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    backup_dir = Path(f'backup/secure_delete_migration/{timestamp}')
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"🔄 Creating backup in: {backup_dir}")
    
    # Files to backup
    files_to_backup = [
        'secure_delete.py',
        'secure_delete.ui'
    ]
    
    backup_manifest = {
        'backup_timestamp': timestamp,
        'backup_date': datetime.now().isoformat(),
        'migration_purpose': 'Secure Delete Migration to file_utilities_2',
        'files': {}
    }
    
    # Backup each file
    for file_name in files_to_backup:
        source_path = Path(file_name)
        if source_path.exists():
            # Copy file to backup directory
            dest_path = backup_dir / file_name
            shutil.copy2(source_path, dest_path)
            
            # Calculate checksums
            source_hash = calculate_file_hash(source_path)
            backup_hash = calculate_file_hash(dest_path)
            
            # Get file stats
            stat = source_path.stat()
            
            backup_manifest['files'][file_name] = {
                'source_path': str(source_path),
                'backup_path': str(dest_path),
                'source_hash': source_hash,
                'backup_hash': backup_hash,
                'file_size': stat.st_size,
                'modified_time': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'backup_verified': source_hash == backup_hash
            }
            
            print(f"✅ Backed up: {file_name} ({stat.st_size} bytes)")
            if source_hash == backup_hash:
                print(f"   ✅ Checksum verified: {source_hash[:16]}...")
            else:
                print(f"   ❌ Checksum mismatch!")
        else:
            print(f"❌ File not found: {file_name}")
            backup_manifest['files'][file_name] = {
                'status': 'not_found',
                'error': f"File {file_name} does not exist"
            }
    
    # Save backup manifest
    manifest_path = backup_dir / 'backup_manifest.json'
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(backup_manifest, f, indent=2, ensure_ascii=False)
    
    print(f"📋 Backup manifest saved: {manifest_path}")
    
    # Create backup summary
    summary_path = backup_dir / 'backup_summary.md'
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(f"""# Secure Delete Migration Backup Summary

**Backup Date**: {backup_manifest['backup_date']}  
**Backup Directory**: `{backup_dir}`  
**Purpose**: {backup_manifest['migration_purpose']}

## Backed Up Files

""")
        for file_name, info in backup_manifest['files'].items():
            if 'source_hash' in info:
                f.write(f"### {file_name}\n")
                f.write(f"- **Size**: {info['file_size']:,} bytes\n")
                f.write(f"- **Modified**: {info['modified_time']}\n")
                f.write(f"- **Checksum**: `{info['source_hash']}`\n")
                f.write(f"- **Verified**: {'✅ Yes' if info['backup_verified'] else '❌ No'}\n\n")
            else:
                f.write(f"### {file_name}\n")
                f.write(f"- **Status**: ❌ {info.get('error', 'Unknown error')}\n\n")
        
        f.write(f"""## Backup Verification

All files have been backed up with SHA256 checksums for integrity verification.
The backup can be restored by copying files back to the main directory.

## Rollback Procedure

If migration needs to be rolled back:

1. Stop any running secure_delete processes
2. Copy files from `{backup_dir}` back to main directory
3. Verify checksums match the manifest
4. Test functionality

---
*Backup created by Secure Delete Migration Script*
""")
    
    print(f"📄 Backup summary saved: {summary_path}")
    print(f"🎯 Backup completed successfully!")
    
    return backup_dir, backup_manifest

if __name__ == "__main__":
    backup_dir, manifest = create_backup()
    print(f"\n📁 Backup location: {backup_dir}")
    print(f"📋 Files backed up: {len([f for f in manifest['files'].values() if 'source_hash' in f])}")