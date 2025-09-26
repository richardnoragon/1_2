#!/usr/bin/env python3
"""
File Finder Migration Verification Script

This script verifies that the migrated file_finder.py can be imported
and instantiated correctly from the file_utilities_1 package.
"""

import sys
import os
from pathlib import Path

def test_import():
    """Test that FileFinderWindow can be imported from file_utilities_1."""
    print("Testing import of FileFinderWindow...")
    try:
        from file_utilities_1.file_finder import FileFinderWindow
        print("✅ Successfully imported FileFinderWindow from file_utilities_1.file_finder")
        return True, FileFinderWindow
    except ImportError as e:
        print(f"❌ Failed to import FileFinderWindow: {e}")
        return False, None
    except Exception as e:
        print(f"❌ Unexpected error during import: {e}")
        return False, None

def test_package_import():
    """Test that FileFinderWindow can be imported from package __init__."""
    print("Testing package-level import...")
    try:
        from file_utilities_1 import FileFinderWindow
        print("✅ Successfully imported FileFinderWindow from file_utilities_1 package")
        return True
    except ImportError as e:
        print(f"❌ Failed to import from package: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during package import: {e}")
        return False

def test_class_instantiation(FileFinderWindow):
    """Test that FileFinderWindow can be instantiated."""
    print("Testing class instantiation...")
    try:
        # Note: We won't actually show the window to avoid GUI issues
        # Just test that the class can be instantiated
        window = FileFinderWindow()
        print("✅ Successfully instantiated FileFinderWindow")
        
        # Test that it has expected attributes
        expected_attrs = ['directory', 'filetype', 'model', 'meta_model']
        missing_attrs = []
        for attr in expected_attrs:
            if not hasattr(window, attr):
                missing_attrs.append(attr)
        
        if missing_attrs:
            print(f"⚠️  Missing expected attributes: {missing_attrs}")
        else:
            print("✅ All expected attributes present")
            
        # Close the window to clean up
        window.close()
        return True
    except Exception as e:
        print(f"❌ Failed to instantiate FileFinderWindow: {e}")
        return False

def test_ui_file_exists():
    """Test that the UI file exists in the correct location."""
    print("Testing UI file existence...")
    ui_file = Path("file_utilities_1/file_finder.ui")
    if ui_file.exists():
        print(f"✅ UI file exists at {ui_file}")
        return True
    else:
        print(f"❌ UI file not found at {ui_file}")
        return False

def test_icon_files_exist():
    """Test that required icon files exist."""
    print("Testing icon files existence...")
    icon_files = [
        "file_utilities_1/icons/folder.png",
        "file_utilities_1/icons/search.png"
    ]
    
    all_exist = True
    for icon_file in icon_files:
        icon_path = Path(icon_file)
        if icon_path.exists():
            print(f"✅ Icon file exists: {icon_file}")
        else:
            print(f"❌ Icon file missing: {icon_file}")
            all_exist = False
    
    return all_exist

def test_backup_files_exist():
    """Test that backup files were created."""
    print("Testing backup files existence...")
    backup_files = [
        "backup/file_finder.py.backup",
        "backup/file_finder.ui.backup"
    ]
    
    all_exist = True
    for backup_file in backup_files:
        backup_path = Path(backup_file)
        if backup_path.exists():
            print(f"✅ Backup file exists: {backup_file}")
        else:
            print(f"❌ Backup file missing: {backup_file}")
            all_exist = False
    
    return all_exist

def main():
    """Run all verification tests."""
    print("=" * 60)
    print("FILE FINDER MIGRATION VERIFICATION")
    print("=" * 60)
    
    # Track test results
    tests_passed = 0
    total_tests = 6
    
    # Test 1: Import from module
    success, FileFinderWindow = test_import()
    if success:
        tests_passed += 1
    
    print()
    
    # Test 2: Import from package
    if test_package_import():
        tests_passed += 1
    
    print()
    
    # Test 3: Class instantiation (only if import succeeded)
    if success and FileFinderWindow:
        if test_class_instantiation(FileFinderWindow):
            tests_passed += 1
    else:
        print("Skipping instantiation test due to import failure")
    
    print()
    
    # Test 4: UI file exists
    if test_ui_file_exists():
        tests_passed += 1
    
    print()
    
    # Test 5: Icon files exist
    if test_icon_files_exist():
        tests_passed += 1
    
    print()
    
    # Test 6: Backup files exist
    if test_backup_files_exist():
        tests_passed += 1
    
    print()
    print("=" * 60)
    print(f"VERIFICATION RESULTS: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 ALL TESTS PASSED - Migration verification successful!")
        return True
    else:
        print(f"⚠️  {total_tests - tests_passed} test(s) failed - Review migration")
        return False

if __name__ == "__main__":
    # Ensure we're in the right directory
    if not Path("file_utilities_1").exists():
        print("❌ Error: file_utilities_1 directory not found. Run from project root.")
        sys.exit(1)
    
    success = main()
    sys.exit(0 if success else 1)