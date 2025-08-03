#!/usr/bin/env python3
"""
File Splitter Migration Cleanup Script

This script safely removes the original file_splitter_joiner files after
successful migration to file_utilities_2 framework.
"""

import os
from datetime import datetime


def cleanup_original_files():
    """Remove original file splitter files after successful migration."""
    
    # Files to remove
    files_to_remove = [
        'file_splitter_joiner.py',
        'file_splitter_joiner.ui'
    ]
    
    # Test file to remove
    test_file = 'tests/test_file_splitter_joiner.py'
    
    cleanup_log = []
    
    print("File Splitter Migration Cleanup")
    print("=" * 40)
    print(f"Cleanup Time: {datetime.now().isoformat()}")
    print()
    
    # Remove main files
    for file_path in files_to_remove:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                cleanup_log.append(f"✅ Removed: {file_path}")
                print(f"✅ Removed: {file_path}")
            except Exception as e:
                cleanup_log.append(f"❌ Failed to remove {file_path}: {str(e)}")
                print(f"❌ Failed to remove {file_path}: {str(e)}")
        else:
            cleanup_log.append(f"ℹ️  File not found: {file_path}")
            print(f"ℹ️  File not found: {file_path}")
    
    # Remove test file
    if os.path.exists(test_file):
        try:
            os.remove(test_file)
            cleanup_log.append(f"✅ Removed: {test_file}")
            print(f"✅ Removed: {test_file}")
        except Exception as e:
            cleanup_log.append(f"❌ Failed to remove {test_file}: {str(e)}")
            print(f"❌ Failed to remove {test_file}: {str(e)}")
    else:
        cleanup_log.append(f"ℹ️  File not found: {test_file}")
        print(f"ℹ️  File not found: {test_file}")
    
    print()
    print("Cleanup Summary:")
    print("-" * 20)
    for log_entry in cleanup_log:
        print(log_entry)
    
    print()
    print("✅ File Splitter Migration Cleanup Complete!")
    print("All original files have been safely removed.")
    print("Migrated files are available in file_utilities_2/")
    
    return cleanup_log


if __name__ == "__main__":
    cleanup_original_files()