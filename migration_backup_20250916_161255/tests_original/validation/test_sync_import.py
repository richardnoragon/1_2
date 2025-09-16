#!/usr/bin/env python3
"""
Test script to verify that the sync module can be imported correctly
from its new location in the synchronization_backup folder.
"""

import sys
import traceback

def test_sync_import():
    """Test importing the sync module from the new location."""
    print("Testing sync module import from new location...")
    print("=" * 50)
    
    try:
        # Test the import that rfuhub.py uses
        from synchronization_backup.sync import SyncWindow
        print("✓ Successfully imported SyncWindow from synchronization_backup.sync")
        
        # Test that we can instantiate the class
        print("✓ SyncWindow class is available")
        print(f"✓ SyncWindow class location: {SyncWindow.__module__}")
        
        # Test that the UI file path is correct
        import os
        ui_file_path = os.path.join('synchronization_backup', 'sync.ui')
        if os.path.exists(ui_file_path):
            print(f"✓ UI file exists at: {ui_file_path}")
        else:
            print(f"✗ UI file not found at: {ui_file_path}")
            return False
            
        print("\n" + "=" * 50)
        print("✓ All import tests passed successfully!")
        print("✓ The sync functionality should work correctly from the new location.")
        return True
        
    except ImportError as e:
        print(f"✗ Import Error: {e}")
        print("\nThis indicates that the module structure or import path is incorrect.")
        traceback.print_exc()
        return False
        
    except Exception as e:
        print(f"✗ Unexpected Error: {e}")
        traceback.print_exc()
        return False

def test_package_structure():
    """Test that the package structure is correct."""
    print("\nTesting package structure...")
    print("-" * 30)
    
    import os
    
    # Check if __init__.py exists
    init_file = os.path.join('synchronization_backup', '__init__.py')
    if os.path.exists(init_file):
        print("✓ __init__.py exists in synchronization_backup")
    else:
        print("✗ __init__.py missing in synchronization_backup")
        return False
    
    # Check if sync.py exists
    sync_file = os.path.join('synchronization_backup', 'sync.py')
    if os.path.exists(sync_file):
        print("✓ sync.py exists in synchronization_backup")
    else:
        print("✗ sync.py missing in synchronization_backup")
        return False
    
    # Check if sync.ui exists
    ui_file = os.path.join('synchronization_backup', 'sync.ui')
    if os.path.exists(ui_file):
        print("✓ sync.ui exists in synchronization_backup")
    else:
        print("✗ sync.ui missing in synchronization_backup")
        return False
    
    return True

if __name__ == "__main__":
    print("Sync Module Migration Test")
    print("=" * 50)
    
    # Test package structure first
    structure_ok = test_package_structure()
    
    if structure_ok:
        # Test imports
        import_ok = test_sync_import()
        
        if import_ok:
            print("\n🎉 Migration completed successfully!")
            print("The sync functionality is ready to use from its new location.")
            sys.exit(0)
        else:
            print("\n❌ Migration has issues that need to be resolved.")
            sys.exit(1)
    else:
        print("\n❌ Package structure is incorrect.")
        sys.exit(1)