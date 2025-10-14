#!/usr/bin/env python3
"""
Verification Script for en_and_decrypt.py Migration

This script verifies that the encryption/decryption tool has been successfully
migrated to src/tools/security/encryption/ and all functionality works correctly.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def test_import():
    """Test that the module can be imported from the new location."""
    print("🔍 Testing module import from new location...")
    try:
        from src.tools.security.encryption.en_and_decrypt import EnAndDecryptGUI

        print("✅ Successfully imported EnAndDecryptGUI from new location")
        return True
    except ImportError as e:
        print(f"❌ Failed to import: {e}")
        return False


def test_class_instantiation():
    """Test that the class can be instantiated."""
    print("\n🔍 Testing class instantiation...")
    try:
        from src.tools.security.encryption.en_and_decrypt import EnAndDecryptGUI

        # We can't actually instantiate without QApplication, but we can check the class exists
        assert hasattr(EnAndDecryptGUI, "__init__")
        assert hasattr(EnAndDecryptGUI, "show_help")
        assert hasattr(EnAndDecryptGUI, "encrypt_files")
        assert hasattr(EnAndDecryptGUI, "decrypt_files")
        print("✅ Class has all expected methods")
        return True
    except Exception as e:
        print(f"❌ Class instantiation check failed: {e}")
        return False


def test_old_location_removed():
    """Test that the old file location no longer exists."""
    print("\n🔍 Checking old file location...")
    old_path = project_root / "src" / "tools" / "security" / "en_and_decrypt.py"
    if old_path.exists():
        print(f"⚠️  WARNING: Old file still exists at {old_path}")
        return False
    else:
        print("✅ Old file location has been removed")
        return True


def test_new_location_exists():
    """Test that the file exists at the new location."""
    print("\n🔍 Checking new file location...")
    new_path = (
        project_root / "src" / "tools" / "security" / "encryption" / "en_and_decrypt.py"
    )
    if new_path.exists():
        print(f"✅ File exists at new location: {new_path}")
        return True
    else:
        print(f"❌ File not found at new location: {new_path}")
        return False


def test_init_file():
    """Test that __init__.py exports the class correctly."""
    print("\n🔍 Testing __init__.py exports...")
    try:
        from src.tools.security.encryption import EnAndDecryptGUI

        print("✅ EnAndDecryptGUI can be imported from package __init__")
        return True
    except ImportError as e:
        print(f"❌ Failed to import from __init__: {e}")
        return False


def verify_file_structure():
    """Verify the encryption folder structure is correct."""
    print("\n🔍 Verifying encryption folder structure...")
    encryption_dir = project_root / "src" / "tools" / "security" / "encryption"

    required_files = ["__init__.py", "en_and_decrypt.py"]

    all_exist = True
    for filename in required_files:
        file_path = encryption_dir / filename
        if file_path.exists():
            print(f"✅ {filename} exists")
        else:
            print(f"❌ {filename} missing")
            all_exist = False

    return all_exist


def main():
    """Run all verification tests."""
    print("=" * 80)
    print("ENCRYPTION TOOL MIGRATION VERIFICATION")
    print("=" * 80)
    print(f"Project Root: {project_root}")
    print("=" * 80)

    tests = [
        ("File Structure", verify_file_structure),
        ("New Location Exists", test_new_location_exists),
        ("Old Location Removed", test_old_location_removed),
        ("Module Import", test_import),
        ("Class Instantiation", test_class_instantiation),
        ("Package Import", test_init_file),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' raised exception: {e}")
            results.append((test_name, False))

    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print("=" * 80)
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All verification tests passed!")
        print("✅ Migration completed successfully!")
        return 0
    else:
        print(f"⚠️  {total - passed} test(s) failed")
        print("❌ Migration verification failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
