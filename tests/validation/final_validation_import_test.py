#!/usr/bin/env python3
"""
Final Validation - Import Testing for Empty Folders Migration
Tests all import patterns and package exports
"""

import sys
import os
import traceback
from pathlib import Path


def test_direct_imports():
    """Test direct imports from file_utilities_1.empty_folders"""
    print("=" * 60)
    print("TESTING DIRECT IMPORTS")
    print("=" * 60)

    try:
        from file_utilities_1.empty_folders import (
            EmptyFoldersWindow,
            EmptyFolderLogic,
        )

        print(
            "✅ SUCCESS: Direct import of EmptyFoldersWindow and EmptyFolderLogic"
        )

        # Test class instantiation
        logic = EmptyFolderLogic()
        print("✅ SUCCESS: EmptyFolderLogic instantiation")

        # Test window class (without showing)
        window_class = EmptyFoldersWindow
        print("✅ SUCCESS: EmptyFoldersWindow class accessible")

        return True

    except Exception as e:
        print(f"❌ FAILED: Direct import failed - {e}")
        traceback.print_exc()
        return False


def test_package_imports():
    """Test package-level imports"""
    print("\n" + "=" * 60)
    print("TESTING PACKAGE IMPORTS")
    print("=" * 60)

    try:
        from file_utilities_1 import EmptyFoldersWindow

        print("✅ SUCCESS: Package-level import of EmptyFoldersWindow")

        # Test __all__ export
        import file_utilities_1

        if hasattr(file_utilities_1, "__all__"):
            if "EmptyFoldersWindow" in file_utilities_1.__all__:
                print("✅ SUCCESS: EmptyFoldersWindow in __all__ exports")
            else:
                print("❌ WARNING: EmptyFoldersWindow not in __all__ exports")
                print(f"   Current __all__: {file_utilities_1.__all__}")
        else:
            print("❌ WARNING: No __all__ defined in package")

        return True

    except Exception as e:
        print(f"❌ FAILED: Package import failed - {e}")
        traceback.print_exc()
        return False


def test_ui_file_access():
    """Test UI file accessibility"""
    print("\n" + "=" * 60)
    print("TESTING UI FILE ACCESS")
    print("=" * 60)

    try:
        ui_file_path = Path("file_utilities_1/empty_folders.ui")

        if ui_file_path.exists():
            print("✅ SUCCESS: UI file exists at expected location")

            # Check file size
            file_size = ui_file_path.stat().st_size
            print(f"✅ INFO: UI file size: {file_size} bytes")

            # Check if it's readable
            with open(ui_file_path, "r", encoding="utf-8") as f:
                content = f.read(100)  # Read first 100 chars
                if content.startswith("<?xml"):
                    print("✅ SUCCESS: UI file is valid XML format")
                else:
                    print("❌ WARNING: UI file doesn't appear to be XML")

        else:
            print(f"❌ FAILED: UI file not found at {ui_file_path}")
            return False

        return True

    except Exception as e:
        print(f"❌ FAILED: UI file access failed - {e}")
        traceback.print_exc()
        return False


def test_dependency_imports():
    """Test that all dependencies can be imported"""
    print("\n" + "=" * 60)
    print("TESTING DEPENDENCY IMPORTS")
    print("=" * 60)

    dependencies = [
        (
            "PyQt5.QtWidgets",
            ["QApplication", "QListWidgetItem", "QMessageBox"],
        ),
        ("PyQt5.QtCore", ["Qt", "QObject", "pyqtSignal", "QThread"]),
        ("pathlib", ["Path"]),
        ("typing", ["List", "Optional"]),
    ]

    all_success = True

    for module_name, items in dependencies:
        try:
            module = __import__(module_name, fromlist=items)
            for item in items:
                if hasattr(module, item):
                    print(f"✅ SUCCESS: {module_name}.{item}")
                else:
                    print(f"❌ FAILED: {module_name}.{item} not found")
                    all_success = False
        except ImportError as e:
            print(f"❌ FAILED: Cannot import {module_name} - {e}")
            all_success = False

    return all_success


def test_project_dependencies():
    """Test project-specific dependencies"""
    print("\n" + "=" * 60)
    print("TESTING PROJECT DEPENDENCIES")
    print("=" * 60)

    try:
        # Test if gui.common modules are accessible
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))

        try:
            from gui.common.base_window import BaseWindow

            print("✅ SUCCESS: BaseWindow import")
        except ImportError as e:
            print(f"❌ FAILED: BaseWindow import - {e}")
            return False

        try:
            from gui.common.dialogs import (
                get_existing_directory,
                show_error_dialog,
            )

            print("✅ SUCCESS: Dialog functions import")
        except ImportError as e:
            print(f"❌ FAILED: Dialog functions import - {e}")
            return False

        return True

    except Exception as e:
        print(f"❌ FAILED: Project dependencies test failed - {e}")
        traceback.print_exc()
        return False


def main():
    """Run all import tests"""
    print("EMPTY FOLDERS MIGRATION - FINAL VALIDATION IMPORT TESTING")
    print("=" * 80)
    print(f"Python Version: {sys.version}")
    print(f"Working Directory: {os.getcwd()}")
    print(f"Python Path: {sys.path[:3]}...")  # Show first 3 entries
    print("=" * 80)

    tests = [
        ("Direct Imports", test_direct_imports),
        ("Package Imports", test_package_imports),
        ("UI File Access", test_ui_file_access),
        ("Dependency Imports", test_dependency_imports),
        ("Project Dependencies", test_project_dependencies),
    ]

    results = {}

    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ CRITICAL ERROR in {test_name}: {e}")
            traceback.print_exc()
            results[test_name] = False

    # Summary
    print("\n" + "=" * 80)
    print("IMPORT TESTING SUMMARY")
    print("=" * 80)

    passed = 0
    total = len(tests)

    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1

    print("-" * 80)
    print(f"TOTAL: {passed}/{total} tests passed")

    if passed == total:
        print(
            "\n🎉 ALL IMPORT TESTS PASSED! Migration imports are working correctly."
        )
        return True
    else:
        print(
            f"\n⚠️  {total - passed} import tests failed. Review issues above."
        )
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
