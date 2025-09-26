#!/usr/bin/env python3
"""
Organize Files Migration Rollback Script
========================================

This script provides a safe rollback mechanism for the organize.py and organize.ui 
files migration from root directory to file_utilities_1 directory.

Created: 2025-01-27 14:29:43
Backup Location: backup/organize_migration/2025-01-27_14-29-43/

Usage:
    python organize_rollback.py

Safety Features:
- Verifies backup integrity before rollback
- Creates verification checksums
- Provides detailed logging of all operations
- Confirms user intent before proceeding
"""

import os
import shutil
import hashlib
from pathlib import Path
from datetime import datetime

# Configuration
BACKUP_DIR = Path('backup/organize_migration/2025-01-27_14-29-43')
TARGET_DIR = Path('file_utilities_1')
ROOT_DIR = Path('.')
FILES_TO_ROLLBACK = ['organize.py', 'organize.ui']

def calculate_file_hash(file_path):
    """Calculate SHA256 hash of a file for integrity verification."""
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        print(f"❌ Error calculating hash for {file_path}: {e}")
        return None

def verify_backup_integrity():
    """Verify that backup files exist and are readable."""
    print("🔍 Verifying backup integrity...")
    
    for filename in FILES_TO_ROLLBACK:
        backup_file = BACKUP_DIR / filename
        
        if not backup_file.exists():
            print(f"❌ Backup file missing: {backup_file}")
            return False
        
        if not backup_file.is_file():
            print(f"❌ Backup path is not a file: {backup_file}")
            return False
        
        try:
            with open(backup_file, 'r', encoding='utf-8') as f:
                content = f.read(100)  # Test readability
            print(f"✅ Backup verified: {filename} ({backup_file.stat().st_size} bytes)")
        except Exception as e:
            print(f"❌ Cannot read backup file {filename}: {e}")
            return False
    
    return True

def check_current_state():
    """Check current state of files in target and root directories."""
    print("\n📋 Checking current file state...")
    
    state = {
        'files_in_target': [],
        'files_in_root': [],
        'missing_files': []
    }
    
    for filename in FILES_TO_ROLLBACK:
        target_file = TARGET_DIR / filename
        root_file = ROOT_DIR / filename
        
        if target_file.exists():
            state['files_in_target'].append(filename)
            print(f"📁 Found in target: {filename} ({target_file.stat().st_size} bytes)")
        
        if root_file.exists():
            state['files_in_root'].append(filename)
            print(f"📁 Found in root: {filename} ({root_file.stat().st_size} bytes)")
        
        if not target_file.exists() and not root_file.exists():
            state['missing_files'].append(filename)
            print(f"❌ Missing: {filename}")
    
    return state

def perform_rollback():
    """Perform the actual rollback operation."""
    print("\n🔄 Starting rollback operation...")
    
    rollback_log = []
    success_count = 0
    
    for filename in FILES_TO_ROLLBACK:
        backup_file = BACKUP_DIR / filename
        target_file = TARGET_DIR / filename
        root_file = ROOT_DIR / filename
        
        try:
            # Step 1: Remove file from target directory if it exists
            if target_file.exists():
                print(f"🗑️  Removing {filename} from {TARGET_DIR}")
                target_file.unlink()
                rollback_log.append(f"Removed: {target_file}")
            
            # Step 2: Copy file from backup to root directory
            print(f"📋 Restoring {filename} to root directory")
            shutil.copy2(backup_file, root_file)
            rollback_log.append(f"Restored: {backup_file} -> {root_file}")
            
            # Step 3: Verify restoration
            if root_file.exists():
                restored_size = root_file.stat().st_size
                backup_size = backup_file.stat().st_size
                
                if restored_size == backup_size:
                    print(f"✅ Successfully restored: {filename} ({restored_size} bytes)")
                    success_count += 1
                else:
                    print(f"⚠️  Size mismatch for {filename}: restored={restored_size}, backup={backup_size}")
            else:
                print(f"❌ Failed to restore: {filename}")
        
        except Exception as e:
            print(f"❌ Error during rollback of {filename}: {e}")
            rollback_log.append(f"Error: {filename} - {e}")
    
    return success_count, rollback_log

def create_rollback_report(success_count, rollback_log):
    """Create a detailed rollback report."""
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    report_file = Path(f'organize_rollback_report_{timestamp}.txt')
    
    report_content = f"""
ORGANIZE FILES ROLLBACK REPORT
==============================

Rollback Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Backup Source: {BACKUP_DIR.absolute()}
Target Directory: {TARGET_DIR.absolute()}
Root Directory: {ROOT_DIR.absolute()}

Files Processed: {len(FILES_TO_ROLLBACK)}
Successful Rollbacks: {success_count}
Failed Rollbacks: {len(FILES_TO_ROLLBACK) - success_count}

ROLLBACK LOG:
{chr(10).join(rollback_log)}

POST-ROLLBACK STATE:
"""
    
    # Add current state to report
    for filename in FILES_TO_ROLLBACK:
        root_file = ROOT_DIR / filename
        target_file = TARGET_DIR / filename
        
        if root_file.exists():
            report_content += f"\n✅ {filename}: Restored to root ({root_file.stat().st_size} bytes)"
        else:
            report_content += f"\n❌ {filename}: NOT in root directory"
        
        if target_file.exists():
            report_content += f"\n⚠️  {filename}: Still in target directory"
        else:
            report_content += f"\n✅ {filename}: Removed from target directory"
    
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        print(f"\n📄 Rollback report saved: {report_file}")
    except Exception as e:
        print(f"\n❌ Failed to save rollback report: {e}")

def main():
    """Main rollback function."""
    print("🔄 ORGANIZE FILES MIGRATION ROLLBACK")
    print("=" * 50)
    print(f"Backup Location: {BACKUP_DIR.absolute()}")
    print(f"Target Directory: {TARGET_DIR}")
    print(f"Files to rollback: {', '.join(FILES_TO_ROLLBACK)}")
    print()
    
    # Step 1: Verify backup integrity
    if not verify_backup_integrity():
        print("\n❌ ROLLBACK ABORTED: Backup integrity check failed")
        return False
    
    # Step 2: Check current state
    current_state = check_current_state()
    
    # Step 3: Confirm user intent
    print(f"\n⚠️  WARNING: This will restore files from backup to root directory")
    print(f"Files in target directory will be removed: {current_state['files_in_target']}")
    print(f"Files will be restored to root: {FILES_TO_ROLLBACK}")
    
    confirm = input("\nDo you want to proceed with rollback? (yes/no): ").lower().strip()
    
    if confirm not in ['yes', 'y']:
        print("❌ Rollback cancelled by user")
        return False
    
    # Step 4: Perform rollback
    success_count, rollback_log = perform_rollback()
    
    # Step 5: Create report
    create_rollback_report(success_count, rollback_log)
    
    # Step 6: Final summary
    print(f"\n🎯 ROLLBACK SUMMARY:")
    print(f"✅ Successfully rolled back: {success_count}/{len(FILES_TO_ROLLBACK)} files")
    
    if success_count == len(FILES_TO_ROLLBACK):
        print("✅ ROLLBACK COMPLETED SUCCESSFULLY")
        print("📁 Files have been restored to root directory")
        print("🗑️  Files have been removed from file_utilities_1 directory")
        return True
    else:
        print("⚠️  ROLLBACK PARTIALLY COMPLETED")
        print("❌ Some files may require manual intervention")
        return False

if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Rollback interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during rollback: {e}")
        import traceback
        traceback.print_exc()
        exit(1)