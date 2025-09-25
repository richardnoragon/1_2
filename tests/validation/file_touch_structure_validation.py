#!/usr/bin/env python3
"""
File Touch Structure Validation Script

This script validates the file structure and basic integration without requiring PyQt5.
"""

import os
import ast
import sys


def validate_file_structure():
    """Validate that all required files are in place."""
    print("Validating file structure...")

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


def validate_init_file():
    """Validate that __init__.py has been updated correctly."""
    print("\nValidating __init__.py updates...")

    init_file = "file_utilities_1/__init__.py"
    if not os.path.exists(init_file):
        print("❌ __init__.py not found")
        return False

    with open(init_file, "r") as f:
        content = f.read()

    # Check for FileTouchWindow import
    if "from .file_touch import FileTouchWindow" in content:
        print("✅ FileTouchWindow import found")
    else:
        print("❌ FileTouchWindow import missing")
        return False

    # Check for FileTouchWindow in __all__
    if "'FileTouchWindow'" in content:
        print("✅ FileTouchWindow in __all__ list")
    else:
        print("❌ FileTouchWindow missing from __all__ list")
        return False

    return True


def validate_python_syntax():
    """Validate that the migrated Python file has valid syntax."""
    print("\nValidating Python syntax...")

    file_path = "file_utilities_1/file_touch.py"
    if not os.path.exists(file_path):
        print("❌ file_touch.py not found")
        return False

    try:
        with open(file_path, "r") as f:
            content = f.read()

        # Parse the file to check syntax
        ast.parse(content)
        print("✅ Python syntax is valid")

        # Check for key classes
        if "class FileTouchWindow" in content:
            print("✅ FileTouchWindow class found")
        else:
            print("❌ FileTouchWindow class missing")
            return False

        if "class FileTouchLogic" in content:
            print("✅ FileTouchLogic class found")
        else:
            print("❌ FileTouchLogic class missing")
            return False

        # Check for backward compatibility
        if "class FileTouchGUI" in content:
            print("✅ FileTouchGUI compatibility class found")
        else:
            print("❌ FileTouchGUI compatibility class missing")
            return False

        return True

    except SyntaxError as e:
        print(f"❌ Syntax error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False


def validate_backup_integrity():
    """Validate that backup files are intact."""
    print("\nValidating backup integrity...")

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
            print(f"✅ Backup exists: {os.path.basename(backup_file)}")
        else:
            print(f"❌ Backup missing: {backup_file}")
            all_present = False

    return all_present


def validate_rfuhub_update():
    """Validate that rfuhub.py has been updated."""
    print("\nValidating RFU Hub updates...")

    rfuhub_file = "rfuhub.py"
    if not os.path.exists(rfuhub_file):
        print("❌ rfuhub.py not found")
        return False

    with open(rfuhub_file, "r") as f:
        content = f.read()

    # Check for updated import
    if "from file_utilities_1 import FileTouchWindow" in content:
        print("✅ Updated import found in rfuhub.py")
    else:
        print("❌ Updated import missing in rfuhub.py")
        return False

    # Check for updated instantiation
    if "FileTouchWindow()" in content:
        print("✅ Updated class instantiation found")
    else:
        print("❌ Updated class instantiation missing")
        return False

    return True


def check_original_files_status():
    """Check if original files still exist (should be removed after validation)."""
    print("\nChecking original file status...")

    original_files = ["file_touch.py", "file_touch.ui"]

    files_exist = []
    for file_path in original_files:
        if os.path.exists(file_path):
            files_exist.append(file_path)
            print(f"⚠️  Original file still exists: {file_path}")
        else:
            print(f"✅ Original file removed: {file_path}")

    return files_exist


def run_validation():
    """Run all validation tests."""
    print("=" * 60)
    print("FILE TOUCH STRUCTURE VALIDATION")
    print("=" * 60)

    tests = [
        ("File Structure", validate_file_structure),
        ("__init__.py Updates", validate_init_file),
        ("Python Syntax", validate_python_syntax),
        ("Backup Integrity", validate_backup_integrity),
        ("RFU Hub Updates", validate_rfuhub_update),
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False

    # Check original files
    original_files = check_original_files_status()

    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)

    passed = sum(1 for result in results.values() if result)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<25} {status}")

    print(f"\nStructural validation: {passed}/{total} tests passed")

    if original_files:
        print(
            f"\n⚠️  {len(original_files)} original files still exist and should be removed:"
        )
        for file_path in original_files:
            print(f"   - {file_path}")
        print("\nReady for cleanup phase.")
    else:
        print("\n✅ All original files have been removed.")

    return passed == total, original_files


if __name__ == "__main__":
    success, remaining_files = run_validation()
    if success:
        print("\n🎉 STRUCTURE VALIDATION SUCCESSFUL!")
        if remaining_files:
            print("Ready to proceed with cleanup.")
        else:
            print("Migration complete!")
    else:
        print("\n⚠️  Some validation tests failed.")

    sys.exit(0 if success else 1)
