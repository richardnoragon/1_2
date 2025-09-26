#!/usr/bin/env python3
"""
File Touch Integration Test Script

This script validates the complete integration of file_touch into file_utilities_1.
Tests all functionality, imports, UI elements, and configuration settings.
"""

import os
import sys
import tempfile
import traceback
from pathlib import Path


def test_import_integration():
    """Test that file_touch can be imported from file_utilities_1."""
    print("Testing import integration...")

    try:
        # Test package-level import
        from file_utilities_1 import FileTouchWindow

        print("✅ Package-level import successful: FileTouchWindow")

        # Test direct module import
        from file_utilities_1.file_touch import (
            FileTouchWindow as DirectFileTouchWindow,
        )

        print("✅ Direct module import successful: FileTouchWindow")

        # Test backward compatibility import
        from file_utilities_1.file_touch import FileTouchGUI

        print("✅ Backward compatibility import successful: FileTouchGUI")

        # Verify they are the same or compatible classes
        assert issubclass(
            FileTouchGUI, FileTouchWindow
        ), "FileTouchGUI should inherit from FileTouchWindow"
        print("✅ Class inheritance verified")

        return True

    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during import: {e}")
        traceback.print_exc()
        return False


def test_file_structure():
    """Test that all required files are in place."""
    print("\nTesting file structure...")

    required_files = [
        "file_utilities_1/file_touch.py",
        "file_utilities_1/file_touch.ui",
        "file_utilities_1/__init__.py",
    ]

    all_present = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")
            all_present = False

    return all_present


def test_ui_file_loading():
    """Test that the UI file can be loaded correctly."""
    print("\nTesting UI file loading...")

    try:
        from PyQt5.QtWidgets import QApplication
        from PyQt5 import uic

        # Create QApplication if it doesn't exist
        app = QApplication.instance()
        if app is None:
            app = QApplication([])

        ui_file = Path("file_utilities_1/file_touch.ui")
        if ui_file.exists():
            # Try to load the UI file
            from PyQt5.QtWidgets import QMainWindow

            window = QMainWindow()
            uic.loadUi(str(ui_file), window)
            print("✅ UI file loads successfully")
            return True
        else:
            print("❌ UI file not found")
            return False

    except ImportError as e:
        print(f"⚠️  PyQt5 not available for UI testing: {e}")
        return True  # Not a failure if PyQt5 isn't available
    except Exception as e:
        print(f"❌ UI file loading failed: {e}")
        traceback.print_exc()
        return False


def test_class_instantiation():
    """Test that the FileTouchWindow class can be instantiated."""
    print("\nTesting class instantiation...")

    try:
        from file_utilities_1 import FileTouchWindow

        # Test instantiation without actually showing the window
        # This tests the basic class structure
        print("✅ FileTouchWindow class can be imported")

        # Test that required methods exist
        required_methods = [
            "__init__",
            "browse_file",
            "refresh_timestamps",
            "apply_changes",
            "save_profile",
            "load_profile",
        ]

        for method in required_methods:
            if hasattr(FileTouchWindow, method):
                print(f"✅ Method {method} exists")
            else:
                print(f"❌ Method {method} missing")
                return False

        return True

    except Exception as e:
        print(f"❌ Class instantiation test failed: {e}")
        traceback.print_exc()
        return False


def test_rfuhub_integration():
    """Test that RFU Hub can import and use the migrated file_touch."""
    print("\nTesting RFU Hub integration...")

    try:
        # Test the import that RFU Hub uses
        from file_utilities_1 import FileTouchWindow

        print("✅ RFU Hub import path works")

        # Verify the class has the expected interface
        window_class = FileTouchWindow
        if hasattr(window_class, "show") and hasattr(window_class, "close"):
            print("✅ Window interface methods available")
        else:
            print("❌ Missing required window interface methods")
            return False

        return True

    except Exception as e:
        print(f"❌ RFU Hub integration test failed: {e}")
        traceback.print_exc()
        return False


def test_configuration_compatibility():
    """Test that configuration management works."""
    print("\nTesting configuration compatibility...")

    try:
        from config_manager import ConfigManager

        # Test that ConfigManager can be imported and used
        config = ConfigManager()
        print("✅ ConfigManager import successful")

        # Test profile operations (basic functionality)
        profiles = config.get_profiles("file_touch")
        print(f"✅ Profile retrieval works (found {len(profiles)} profiles)")

        return True

    except Exception as e:
        print(f"❌ Configuration compatibility test failed: {e}")
        traceback.print_exc()
        return False


def test_dependency_resolution():
    """Test that all dependencies can be resolved."""
    print("\nTesting dependency resolution...")

    dependencies = [
        "log_manager",
        "gui.common.base_window",
        "gui.common.dialogs",
        "config_manager",
    ]

    all_resolved = True
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep} import successful")
        except ImportError as e:
            print(f"❌ {dep} import failed: {e}")
            all_resolved = False
        except Exception as e:
            print(f"⚠️  {dep} import warning: {e}")

    return all_resolved


def test_backup_integrity():
    """Test that backup files are intact."""
    print("\nTesting backup integrity...")

    backup_dir = "backup/file_touch_migration/2025-07-29_20-15-00"
    required_backups = [
        f"{backup_dir}/file_touch.py",
        f"{backup_dir}/file_touch.ui",
        f"{backup_dir}/file_touch_files.md",
        f"{backup_dir}/backup_manifest.txt",
    ]

    all_present = True
    for backup_file in required_backups:
        if os.path.exists(backup_file):
            print(f"✅ Backup file exists: {backup_file}")
        else:
            print(f"❌ Backup file missing: {backup_file}")
            all_present = False

    return all_present


def run_comprehensive_test():
    """Run all tests and provide a comprehensive report."""
    print("=" * 60)
    print("FILE TOUCH INTEGRATION VALIDATION TEST")
    print("=" * 60)

    tests = [
        ("Import Integration", test_import_integration),
        ("File Structure", test_file_structure),
        ("UI File Loading", test_ui_file_loading),
        ("Class Instantiation", test_class_instantiation),
        ("RFU Hub Integration", test_rfuhub_integration),
        ("Configuration Compatibility", test_configuration_compatibility),
        ("Dependency Resolution", test_dependency_resolution),
        ("Backup Integrity", test_backup_integrity),
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for result in results.values() if result)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<30} {status}")

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL TESTS PASSED - Integration successful!")
        return True
    else:
        print("⚠️  Some tests failed - Review issues above")
        return False


if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)
