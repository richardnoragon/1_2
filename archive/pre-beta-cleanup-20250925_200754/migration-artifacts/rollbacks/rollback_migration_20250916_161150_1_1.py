#!/usr/bin/env python3
"""
Rollback Script for Migration: C:\Users\HP1\1_2\migration_backup_20250916_161150
"""

import shutil
import os
from pathlib import Path

def rollback_migration():
    """Rollback the migration to previous state."""
    backup_path = Path("C:\Users\HP1\1_2\migration_backup_20250916_161150")
    project_root = Path(__file__).parent
    
    if not backup_path.exists():
        print(f"ERROR: Backup directory not found: {backup_path}")
        return False
    
    print("Rolling back migration...")
    
    # Remove current tools directory
    tools_path = project_root / "src" / "tools"
    if tools_path.exists():
        shutil.rmtree(tools_path)
        print("Removed current tools directory")
    
    # Restore original directories
    restore_items = [
        ("src_original", "src"),
        ("tests_original", "tests"), 
        ("config_original", "config"),
        ("main_backup.py", "main.py"),
        ("requirements_backup.txt", "requirements.txt")
    ]
    
    for backup_item, target_item in restore_items:
        backup_item_path = backup_path / backup_item
        target_item_path = project_root / target_item
        
        if backup_item_path.exists():
            if target_item_path.exists():
                if target_item_path.is_dir():
                    shutil.rmtree(target_item_path)
                else:
                    target_item_path.unlink()
            
            if backup_item_path.is_dir():
                shutil.copytree(backup_item_path, target_item_path)
            else:
                shutil.copy2(backup_item_path, target_item_path)
            
            print(f"Restored {backup_item} to {target_item}")
    
    print("Rollback completed successfully")
    return True

if __name__ == "__main__":
    rollback_migration()
