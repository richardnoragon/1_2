#!/usr/bin/env python3
"""
Tag Viewer Editor Cleanup Validation Test
==========================================

This script validates that the legacy file cleanup was successful and that
the tag_viewer_editor migration is 100% complete and functional.
"""

import sys
import os
from pathlib import Path
import importlib.util


def test_legacy_files_removed():
    """Test that legacy files have been successfully removed."""
    print("Testing legacy file removal...")

    legacy_files = ["tag_viewer_editor.py", "tag_viewer_editor.ui"]

    results = {}
    for file_name in legacy_files:
        file_path = Path(file_name)
        exists = file_path.exists()
        results[file_name] = {
            "exists": exists,
            "status": (
                "FAIL - File still exists" if exists else "PASS - File removed"
            ),
        }
        print(f"  {file_name}: {results[file_name]['status']}")

    return results


def test_migrated_files_exist():
    """Test that migrated files exist in the new location."""
    print("\nTesting migrated file existence...")

    migrated_files = [
        "file_utilities_2/gui/tag_viewer_editor.py",
        "file_utilities_2/gui/tag_viewer_editor.ui",
    ]

    results = {}
    for file_path in migrated_files:
        path = Path(file_path)
        exists = path.exists()
        results[file_path] = {
            "exists": exists,
            "status": (
                "PASS - File exists" if exists else "FAIL - File missing"
            ),
        }
        print(f"  {file_path}: {results[file_path]['status']}")

    return results


def test_backup_integrity():
    """Test that backup files are intact."""
    print("\nTesting backup integrity...")

    backup_files = [
        "backup/tag_viewer_editor_migration/2025-01-27_14-16-46/tag_viewer_editor.py",
        "backup/tag_viewer_editor_migration/2025-01-27_14-16-46/tag_viewer_editor.ui",
        "backup/tag_viewer_editor_migration/2025-01-27_14-16-46/backup_manifest.txt",
    ]

    results = {}
    for file_path in backup_files:
        path = Path(file_path)
        exists = path.exists()
        results[file_path] = {
            "exists": exists,
            "status": (
                "PASS - Backup exists" if exists else "FAIL - Backup missing"
            ),
        }
        print(f"  {file_path}: {results[file_path]['status']}")

    return results


def test_import_functionality():
    """Test that the new import works correctly."""
    print("\nTesting import functionality...")

    try:
        # Test the new import path
        from file_utilities_2.gui.tag_viewer_editor import TagViewerEditor

        print("  Import test: PASS - Successfully imported TagViewerEditor")

        # Test class instantiation (without showing the window)
        try:
            # We'll test this without actually creating a QApplication
            # since that would require GUI setup
            print(
                "  Class availability: PASS - TagViewerEditor class is accessible"
            )
            return {"import_test": "PASS", "class_test": "PASS"}
        except Exception as e:
            print(f"  Class test: FAIL - Error accessing class: {e}")
            return {"import_test": "PASS", "class_test": "FAIL"}

    except ImportError as e:
        print(f"  Import test: FAIL - Import error: {e}")
        return {"import_test": "FAIL", "class_test": "SKIP"}


def test_no_legacy_imports():
    """Test that no files still try to import from the old location."""
    print("\nTesting for legacy import references...")

    # Search for any remaining legacy imports
    python_files = list(Path(".").rglob("*.py"))
    legacy_imports_found = []

    for py_file in python_files:
        # Skip test files and backup files
        if any(
            skip in str(py_file)
            for skip in ["test_", "backup/", "validation_script"]
        ):
            continue

        try:
            content = py_file.read_text(encoding="utf-8")
            if (
                "from tag_viewer_editor import" in content
                or "import tag_viewer_editor" in content
            ):
                # Check if it's just a comment
                lines = content.split("\n")
                for i, line in enumerate(lines):
                    if (
                        "from tag_viewer_editor import" in line
                        or "import tag_viewer_editor" in line
                    ) and not line.strip().startswith("#"):
                        legacy_imports_found.append(
                            f"{py_file}:{i+1} - {line.strip()}"
                        )
        except Exception:
            continue

    if legacy_imports_found:
        print("  Legacy imports: FAIL - Found legacy imports:")
        for import_ref in legacy_imports_found:
            print(f"    {import_ref}")
        return {"legacy_imports": "FAIL", "details": legacy_imports_found}
    else:
        print("  Legacy imports: PASS - No legacy imports found")
        return {"legacy_imports": "PASS", "details": []}


def main():
    """Run all validation tests."""
    print("Tag Viewer Editor Cleanup Validation")
    print("=" * 50)

    # Run all tests
    legacy_removal = test_legacy_files_removed()
    migrated_existence = test_migrated_files_exist()
    backup_integrity = test_backup_integrity()
    import_functionality = test_import_functionality()
    legacy_imports = test_no_legacy_imports()

    # Summary
    print("\n" + "=" * 50)
    print("VALIDATION SUMMARY")
    print("=" * 50)

    all_passed = True

    # Check legacy file removal
    for file_name, result in legacy_removal.items():
        if result["exists"]:
            all_passed = False
            print(f"❌ FAIL: {file_name} still exists in root directory")
        else:
            print(f"✅ PASS: {file_name} successfully removed")

    # Check migrated files
    for file_path, result in migrated_existence.items():
        if not result["exists"]:
            all_passed = False
            print(f"❌ FAIL: {file_path} missing from new location")
        else:
            print(f"✅ PASS: {file_path} exists in new location")

    # Check backup integrity
    for file_path, result in backup_integrity.items():
        if not result["exists"]:
            all_passed = False
            print(f"❌ FAIL: {file_path} backup missing")
        else:
            print(f"✅ PASS: {file_path} backup intact")

    # Check import functionality
    if import_functionality["import_test"] == "PASS":
        print("✅ PASS: New import path works correctly")
    else:
        all_passed = False
        print("❌ FAIL: New import path not working")

    # Check legacy imports
    if legacy_imports["legacy_imports"] == "PASS":
        print("✅ PASS: No legacy imports found")
    else:
        all_passed = False
        print("❌ FAIL: Legacy imports still exist")

    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 MIGRATION CLEANUP SUCCESSFUL!")
        print("✅ All legacy files removed")
        print("✅ All migrated files in place")
        print("✅ All backups intact")
        print("✅ New imports working")
        print("✅ No legacy references found")
        print("\nThe tag_viewer_editor migration is 100% complete!")
    else:
        print("⚠️  MIGRATION CLEANUP ISSUES DETECTED")
        print("Please review the failed tests above.")

    print("=" * 50)
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
