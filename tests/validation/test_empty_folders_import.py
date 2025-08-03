#!/usr/bin/env python3
"""
Test script to verify empty_folders.py imports and basic functionality
"""

import sys
import os

def test_empty_folders_import():
    """Test importing the empty folders module."""
    print("Testing empty_folders.py import...")
    
    try:
        # Test importing the module
        from file_utilities_1.empty_folders import EmptyFoldersWindow, EmptyFolderLogic
        print("✓ Successfully imported EmptyFoldersWindow and EmptyFolderLogic")
        
        # Test creating the logic class
        logic = EmptyFolderLogic()
        print("✓ Successfully created EmptyFolderLogic instance")
        
        # Test that the logic has the expected methods
        expected_methods = ['find_empty_folders', 'delete_folders', 'stop']
        for method in expected_methods:
            if hasattr(logic, method):
                print(f"✓ Logic has method: {method}")
            else:
                print(f"✗ Logic missing method: {method}")
                return False
        
        # Test that the logic has the expected signals
        expected_signals = ['progress_updated', 'folders_found', 'deletion_update', 'error_occurred', 'finished']
        for signal in expected_signals:
            if hasattr(logic, signal):
                print(f"✓ Logic has signal: {signal}")
            else:
                print(f"✗ Logic missing signal: {signal}")
                return False
        
        print("✓ All import tests passed!")
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

def test_ui_file_exists():
    """Test that the UI file exists and is accessible."""
    print("\nTesting UI file accessibility...")
    
    ui_file_path = os.path.join("file_utilities_1", "empty_folders.ui")
    
    if os.path.exists(ui_file_path):
        print(f"✓ UI file exists: {ui_file_path}")
        
        # Check if file is readable
        try:
            with open(ui_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if content.strip():
                    print("✓ UI file is readable and not empty")
                    
                    # Check for key UI elements
                    ui_elements = ['pathInput', 'browseButton', 'scanButton', 'folderList', 'deleteButton']
                    for element in ui_elements:
                        if element in content:
                            print(f"✓ UI file contains element: {element}")
                        else:
                            print(f"✗ UI file missing element: {element}")
                            return False
                    
                    return True
                else:
                    print("✗ UI file is empty")
                    return False
        except Exception as e:
            print(f"✗ Error reading UI file: {e}")
            return False
    else:
        print(f"✗ UI file not found: {ui_file_path}")
        return False

def main():
    """Run all tests."""
    print("=" * 50)
    print("Empty Folders Migration Test Suite")
    print("=" * 50)
    
    all_passed = True
    
    # Test imports
    if not test_empty_folders_import():
        all_passed = False
    
    # Test UI file
    if not test_ui_file_exists():
        all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✓ ALL TESTS PASSED!")
        print("The empty folders migration appears to be successful.")
    else:
        print("✗ SOME TESTS FAILED!")
        print("There are issues that need to be addressed.")
    print("=" * 50)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())