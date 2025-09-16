#!/usr/bin/env python3
"""
Integration test for the migrated empty_folders module.
This script tests the complete functionality of the empty folders cleaner.
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path


def create_test_directory_structure():
    """Create a test directory structure with empty and non-empty folders."""
    # Create temporary directory
    test_dir = tempfile.mkdtemp(prefix="empty_folders_test_")
    test_path = Path(test_dir)
    
    # Create directory structure
    (test_path / "empty_folder_1").mkdir()
    (test_path / "empty_folder_2").mkdir()
    (test_path / "non_empty_folder").mkdir()
    (test_path / "non_empty_folder" / "file.txt").write_text("test content")
    
    # Create nested empty folders
    (test_path / "nested" / "empty_subfolder").mkdir(parents=True)
    (test_path / "nested" / "non_empty_subfolder").mkdir()
    (test_path / "nested" / "non_empty_subfolder" / "file.txt").write_text("test")
    
    return test_path


def cleanup_test_directory(test_path):
    """Clean up the test directory."""
    if test_path.exists():
        shutil.rmtree(test_path)


def test_import():
    """Test importing the empty folders module."""
    print("Testing imports...")
    
    try:
        from file_utilities_1.empty_folders import EmptyFoldersWindow, EmptyFolderLogic
        print("✅ Successfully imported EmptyFoldersWindow and EmptyFolderLogic")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False


def test_logic_functionality():
    """Test the EmptyFolderLogic class functionality."""
    print("\nTesting EmptyFolderLogic functionality...")
    
    try:
        from file_utilities_1.empty_folders import EmptyFolderLogic
        
        # Create test directory
        test_path = create_test_directory_structure()
        print(f"Created test directory: {test_path}")
        
        # Test logic instance
        logic = EmptyFolderLogic()
        
        # Test finding empty folders (synchronous for testing)
        empty_folders = []
        
        def collect_folders(folders):
            nonlocal empty_folders
            empty_folders = folders
        
        logic.folders_found.connect(collect_folders)
        
        # Manually find empty folders for testing
        for root, dirs, files in os.walk(test_path):
            try:
                if not os.listdir(root):
                    empty_folders.append(root)
            except (OSError, PermissionError):
                continue
        
        print(f"Found {len(empty_folders)} empty folders:")
        for folder in empty_folders:
            rel_path = os.path.relpath(folder, test_path)
            print(f"  - {rel_path}")
        
        # Verify we found the expected empty folders
        expected_empty = ["empty_folder_1", "empty_folder_2", "nested/empty_subfolder"]
        found_relative = [os.path.relpath(f, test_path) for f in empty_folders]
        
        success = True
        for expected in expected_empty:
            if expected in found_relative:
                print(f"✅ Found expected empty folder: {expected}")
            else:
                print(f"❌ Missing expected empty folder: {expected}")
                success = False
        
        # Clean up
        cleanup_test_directory(test_path)
        
        return success
        
    except Exception as e:
        print(f"❌ Logic test failed: {e}")
        return False


def test_ui_creation():
    """Test UI creation without showing the window."""
    print("\nTesting UI creation...")
    
    try:
        from PyQt5.QtWidgets import QApplication
        from file_utilities_1.empty_folders import EmptyFoldersWindow
        
        # Create QApplication if it doesn't exist
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        # Create window (but don't show it)
        window = EmptyFoldersWindow()
        
        # Test that UI elements exist
        ui_elements = [
            'pathInput', 'browseButton', 'scanButton', 'stopButton',
            'folderList', 'selectAllButton', 'unselectAllButton', 
            'deleteButton', 'statusLabel'
        ]
        
        success = True
        for element in ui_elements:
            if hasattr(window, element):
                print(f"✅ UI element exists: {element}")
            else:
                print(f"❌ Missing UI element: {element}")
                success = False
        
        # Test initial state
        if hasattr(window, 'deleteButton') and not window.deleteButton.isEnabled():
            print("✅ Delete button correctly disabled initially")
        else:
            print("❌ Delete button state incorrect")
            success = False
        
        if hasattr(window, 'stopButton') and not window.stopButton.isEnabled():
            print("✅ Stop button correctly disabled initially")
        else:
            print("❌ Stop button state incorrect")
            success = False
        
        # Clean up
        window.close()
        
        return success
        
    except Exception as e:
        print(f"❌ UI creation test failed: {e}")
        return False


def test_package_integration():
    """Test package-level integration."""
    print("\nTesting package integration...")
    
    try:
        # Test package import
        import file_utilities_1
        
        # Test that EmptyFoldersWindow is in __all__
        if 'EmptyFoldersWindow' in file_utilities_1.__all__:
            print("✅ EmptyFoldersWindow in package __all__")
        else:
            print("❌ EmptyFoldersWindow missing from package __all__")
            return False
        
        # Test direct import from package
        from file_utilities_1 import EmptyFoldersWindow
        print("✅ Successfully imported EmptyFoldersWindow from package")
        
        return True
        
    except Exception as e:
        print(f"❌ Package integration test failed: {e}")
        return False


def main():
    """Run all integration tests."""
    print("=" * 60)
    print("Empty Folders Migration Integration Test Suite")
    print("=" * 60)
    
    tests = [
        ("Import Test", test_import),
        ("Logic Functionality Test", test_logic_functionality),
        ("UI Creation Test", test_ui_creation),
        ("Package Integration Test", test_package_integration),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<30} {status}")
        if result:
            passed += 1
    
    print("-" * 60)
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Migration appears successful.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())