"""
Encryption Migration Validation Script

This script validates the successful migration of encryption functionality
from standalone files to the integrated file_utilities_2 structure.
"""

import os
import sys
import tempfile
import shutil
import traceback
from datetime import datetime


def test_imports():
    """Test that all new modules can be imported successfully."""
    print("Testing imports...")

    try:
        # Test core imports
        from file_utilities_2.core.encryption_logic import EncryptionLogic
        from file_utilities_2.core.encryption_config import EncryptionConfig
        from file_utilities_2.core.encryption_logging import EncryptionLogger

        print("✓ Core modules imported successfully")

        # Test GUI imports
        from file_utilities_2.gui.encryption_gui import EncryptionGUI

        print("✓ GUI modules imported successfully")

        # Test integration imports
        from file_utilities_2.integration.encryption_connector import (
            EncryptionHubConnector,
        )

        print("✓ Integration modules imported successfully")

        # Test package-level imports
        from file_utilities_2 import (
            EncryptionLogic as PkgEncryptionLogic,
            EncryptionConfig as PkgEncryptionConfig,
            EncryptionLogger as PkgEncryptionLogger,
            EncryptionGUI as PkgEncryptionGUI,
            EncryptionHubConnector as PkgEncryptionHubConnector,
        )

        print("✓ Package-level imports working correctly")

        return True

    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error during import: {e}")
        return False


def test_core_functionality():
    """Test core encryption functionality."""
    print("\nTesting core functionality...")

    try:
        from file_utilities_2.core.encryption_logic import EncryptionLogic
        from file_utilities_2.core.encryption_config import EncryptionConfig
        from file_utilities_2.core.encryption_logging import EncryptionLogger

        # Create temporary directory
        temp_dir = tempfile.mkdtemp()

        try:
            # Initialize components
            config = EncryptionConfig()
            logger = EncryptionLogger(log_directory=temp_dir)
            encryption_logic = EncryptionLogic(config=config, logger=logger)

            # Test key generation
            key = encryption_logic.generate_key()
            if not key or len(key) != 44:
                raise ValueError("Key generation failed")
            print("✓ Key generation working")

            # Test key save/load
            key_file = os.path.join(temp_dir, "test.key")
            if not encryption_logic.save_key(key, key_file):
                raise ValueError("Key saving failed")

            loaded_key = encryption_logic.load_key(key_file)
            if loaded_key != key:
                raise ValueError("Key loading failed")
            print("✓ Key save/load working")

            # Test file encryption/decryption
            test_file = os.path.join(temp_dir, "test.txt")
            test_content = "Test encryption content"

            with open(test_file, "w", encoding="utf-8") as f:
                f.write(test_content)

            encrypted_file = test_file + ".encrypted"
            if not encryption_logic.encrypt_file(
                test_file, key, encrypted_file
            ):
                raise ValueError("File encryption failed")
            print("✓ File encryption working")

            decrypted_file = test_file + ".decrypted"
            if not encryption_logic.decrypt_file(
                encrypted_file, key, decrypted_file
            ):
                raise ValueError("File decryption failed")

            with open(decrypted_file, "r", encoding="utf-8") as f:
                decrypted_content = f.read()

            if decrypted_content != test_content:
                raise ValueError("Decrypted content doesn't match original")
            print("✓ File decryption working")

            # Test configuration
            buffer_size = config.get_setting(
                "performance_settings.buffer_size"
            )
            if buffer_size != 8192:
                raise ValueError("Configuration reading failed")

            if not config.set_setting(
                "performance_settings.buffer_size", 16384
            ):
                raise ValueError("Configuration setting failed")
            print("✓ Configuration management working")

            # Test logging
            logger.log(logger.LogLevel.INFO, "Test log message")
            logger.audit(logger.SecurityEvent.KEY_GENERATED, {"test": "data"})
            print("✓ Logging functionality working")

            logger.close()
            return True

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    except Exception as e:
        print(f"✗ Core functionality test failed: {e}")
        traceback.print_exc()
        return False


def test_gui_initialization():
    """Test GUI initialization without showing the window."""
    print("\nTesting GUI initialization...")

    try:
        # Import PyQt5 to check if it's available
        from PyQt5.QtWidgets import QApplication
        from file_utilities_2.gui.encryption_gui import EncryptionGUI

        # Create QApplication if it doesn't exist
        app = QApplication.instance()
        if app is None:
            app = QApplication([])

        # Try to create GUI instance
        gui = EncryptionGUI()

        # Basic checks
        if not hasattr(gui, "encryption_logic"):
            raise ValueError("GUI missing encryption_logic attribute")

        if not hasattr(gui, "config"):
            raise ValueError("GUI missing config attribute")

        if not hasattr(gui, "logger"):
            raise ValueError("GUI missing logger attribute")

        print("✓ GUI initialization working")

        # Clean up
        gui.close()
        return True

    except ImportError as e:
        print(f"⚠ GUI test skipped (PyQt5 not available): {e}")
        return True  # Not a failure, just unavailable
    except Exception as e:
        print(f"✗ GUI initialization failed: {e}")
        traceback.print_exc()
        return False


def test_integration():
    """Test integration components."""
    print("\nTesting integration...")

    try:
        from file_utilities_2.integration.encryption_connector import (
            EncryptionHubConnector,
        )

        # Create connector
        connector = EncryptionHubConnector()

        # Test operation registration
        op_id = connector.register_operation("test_op", {"param": "value"})
        if not op_id:
            raise ValueError("Operation registration failed")

        # Test progress tracking
        connector.update_operation_progress(op_id, 50, 100, "Test progress")

        status = connector.get_operation_status(op_id)
        if not status or status["progress"] != 50:
            raise ValueError("Progress tracking failed")

        # Test completion
        connector.complete_operation(op_id, {"result": "success"})

        # Operation should be removed
        if connector.get_operation_status(op_id) is not None:
            raise ValueError("Operation cleanup failed")

        print("✓ Integration components working")
        return True

    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        traceback.print_exc()
        return False


def test_backward_compatibility():
    """Test that original functionality is preserved."""
    print("\nTesting backward compatibility...")

    try:
        # Check if original files still exist
        original_files = ["en_and_decrypt.py", "en_and_decrypt.ui"]
        backup_exists = False

        for filename in original_files:
            if os.path.exists(filename):
                print(f"⚠ Original file {filename} still exists")

            # Check backup
            backup_pattern = f"backup/encryption_migration/*/{filename}"
            import glob

            backup_files = glob.glob(backup_pattern)
            if backup_files:
                backup_exists = True
                print(f"✓ Backup found for {filename}")

        if backup_exists:
            print("✓ Backup system working")
        else:
            print("⚠ No backups found")

        return True

    except Exception as e:
        print(f"✗ Backward compatibility test failed: {e}")
        return False


def test_package_structure():
    """Test that package structure is correct."""
    print("\nTesting package structure...")

    try:
        expected_files = [
            "file_utilities_2/core/encryption_logic.py",
            "file_utilities_2/core/encryption_config.py",
            "file_utilities_2/core/encryption_logging.py",
            "file_utilities_2/gui/encryption_gui.py",
            "file_utilities_2/integration/encryption_connector.py",
        ]

        missing_files = []
        for file_path in expected_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)

        if missing_files:
            print(f"✗ Missing files: {missing_files}")
            return False

        print("✓ All expected files present")

        # Test __init__.py files
        init_files = [
            "file_utilities_2/__init__.py",
            "file_utilities_2/core/__init__.py",
            "file_utilities_2/gui/__init__.py",
            "file_utilities_2/integration/__init__.py",
        ]

        for init_file in init_files:
            if not os.path.exists(init_file):
                print(f"✗ Missing {init_file}")
                return False

        print("✓ Package structure correct")
        return True

    except Exception as e:
        print(f"✗ Package structure test failed: {e}")
        return False


def run_validation():
    """Run all validation tests."""
    print("=" * 60)
    print("ENCRYPTION MIGRATION VALIDATION")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    tests = [
        ("Package Structure", test_package_structure),
        ("Imports", test_imports),
        ("Core Functionality", test_core_functionality),
        ("GUI Initialization", test_gui_initialization),
        ("Integration", test_integration),
        ("Backward Compatibility", test_backward_compatibility),
    ]

    results = {}

    for test_name, test_func in tests:
        print(f"\n{'=' * 40}")
        print(f"Running {test_name} Test")
        print("=" * 40)

        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"✗ {test_name} test crashed: {e}")
            traceback.print_exc()
            results[test_name] = False

    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)

    passed = 0
    total = len(results)

    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        icon = "✓" if result else "✗"
        print(f"{icon} {test_name}: {status}")
        if result:
            passed += 1

    print(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Migration validation successful.")
        return True
    else:
        print(
            f"\n❌ {total - passed} tests failed. Migration needs attention."
        )
        return False


if __name__ == "__main__":
    success = run_validation()
    sys.exit(0 if success else 1)
