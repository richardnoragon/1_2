#!/usr/bin/env python3
"""
Rollback script for Advanced Folders Migration
Generated: 2025-09-17T17:21:29.774807
"""

import os
import shutil
from pathlib import Path

def rollback_migration():
    """Rollback the advanced folders migration"""
    root_path = Path(".")
    backup_path = Path("C:\Users\HP1\1_2\migration_backup_20250917_172120")
    
    print("Starting rollback...")
    
    # Restore source directory
    source_backup = backup_path / "src_advanced_folders"
    target_source = root_path / "src" / "advanced_folders"
    
    if source_backup.exists():
        if target_source.exists():
            shutil.rmtree(target_source)
        shutil.copytree(source_backup, target_source)
        print("Restored src/advanced_folders")
    
    # Remove migrated directory
    migrated_path = root_path / "src" / "tools" / "file_management" / "advanced_folders_legacy"
    if migrated_path.exists():
        shutil.rmtree(migrated_path)
        print("Removed migrated directory")
    
    # Restore test directory
    test_backup = backup_path / "advanced_folders"
    target_test = root_path / "tests" / "advanced_folders"
    
    if test_backup.exists():
        if target_test.exists():
            shutil.rmtree(target_test)
        shutil.copytree(test_backup, target_test)
        print("Restored test directory")
    
    # Remove migrated test directory
    migrated_test = root_path / "tests" / "advanced_folders_legacy"
    if migrated_test.exists():
        shutil.rmtree(migrated_test)
        print("Removed migrated test directory")
    
    print("Rollback completed!")
    print("Note: You will need to manually revert import statement changes in files.")
    print("Check the migration log for files that were updated.")

if __name__ == "__main__":
    rollback_migration()
