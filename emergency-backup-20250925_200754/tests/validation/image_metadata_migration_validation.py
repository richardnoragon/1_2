#!/usr/bin/env python3
"""
Image Metadata Editor Migration Validation Script

This script validates the successful migration of the Image Metadata Editor
from the root directory into the file_utilities_2 module structure.
"""

import sys
import os
import traceback
import tempfile
from pathlib import Path
from PIL import Image
import piexif


def create_test_image():
    """Create a test image with EXIF data for testing."""
    # Create a simple test image
    img = Image.new("RGB", (100, 100), color="red")

    # Create EXIF data
    exif_dict = {
        "0th": {
            piexif.ImageIFD.Artist: "Test Artist",
            piexif.ImageIFD.Software: "Test Software",
            piexif.ImageIFD.ImageDescription: "Test Description",
        },
        "Exif": {
            piexif.ExifIFD.DateTimeOriginal: "2025:01:01 12:00:00",
            piexif.ExifIFD.ExposureTime: (1, 100),
            piexif.ExifIFD.FNumber: (28, 10),
        },
        "GPS": {},
        "1st": {},
        "thumbnail": None,
    }

    exif_bytes = piexif.dump(exif_dict)

    # Save test image with EXIF data
    test_image_path = os.path.join(
        tempfile.gettempdir(), "test_image_metadata.jpg"
    )
    img.save(test_image_path, "JPEG", exif=exif_bytes)

    return test_image_path


def test_imports():
    """Test that all migrated components can be imported successfully."""
    print("Testing imports...")

    try:
        # Test core logic import
        from file_utilities_2.core.image_metadata_logic import (
            ImageMetadataLogic,
        )

        print("✓ Core logic import successful")

        # Test GUI import
        from file_utilities_2.gui.image_metadata_gui import ImageMetadataEditor

        print("✓ GUI import successful")

        # Test package-level import
        from file_utilities_2 import ImageMetadataLogic as PackageLogic
        from file_utilities_2 import ImageMetadataEditor as PackageEditor

        print("✓ Package-level imports successful")

        return True

    except ImportError as e:
        print(f"✗ Import failed: {e}")
        traceback.print_exc()
        return False


def test_core_functionality():
    """Test the core image metadata functionality."""
    print("\nTesting core functionality...")

    try:
        from file_utilities_2.core.image_metadata_logic import (
            ImageMetadataLogic,
        )

        # Create test image
        test_image_path = create_test_image()

        # Initialize logic
        logic = ImageMetadataLogic()

        # Test metadata loading
        metadata = logic.load_metadata(test_image_path)
        if metadata:
            print("✓ Metadata loading successful")
        else:
            print("✗ Metadata loading failed")
            return False

        # Test metadata validation
        if logic.validate_metadata(metadata):
            print("✓ Metadata validation successful")
        else:
            print("✗ Metadata validation failed")
            return False

        # Test metadata modification
        if "0th" in metadata:
            metadata["0th"][piexif.ImageIFD.Artist] = "Modified Artist"

        # Test metadata saving
        backup_path = test_image_path + ".backup"
        if logic.save_metadata(test_image_path, metadata, backup_path):
            print("✓ Metadata saving successful")
        else:
            print("✗ Metadata saving failed")
            return False

        # Cleanup
        try:
            os.remove(test_image_path)
            if os.path.exists(backup_path):
                os.remove(backup_path)
        except:
            pass

        return True

    except Exception as e:
        print(f"✗ Core functionality test failed: {e}")
        traceback.print_exc()
        return False


def test_gui_initialization():
    """Test GUI component initialization."""
    print("\nTesting GUI initialization...")

    try:
        from PyQt5.QtWidgets import QApplication
        from file_utilities_2.gui.image_metadata_gui import ImageMetadataEditor

        # Create QApplication if it doesn't exist
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        # Initialize GUI
        editor = ImageMetadataEditor()
        print("✓ GUI initialization successful")

        # Test basic properties
        if hasattr(editor, "logic"):
            print("✓ Logic component attached")
        else:
            print("✗ Logic component missing")
            return False

        if hasattr(editor, "hub_connector"):
            print("✓ Hub connector attached")
        else:
            print("✗ Hub connector missing")
            return False

        # Test UI components
        if hasattr(editor, "metadata_tree"):
            print("✓ Metadata tree widget present")
        else:
            print("✗ Metadata tree widget missing")
            return False

        return True

    except Exception as e:
        print(f"✗ GUI initialization test failed: {e}")
        traceback.print_exc()
        return False


def test_integration_components():
    """Test integration with file_utilities_2 components."""
    print("\nTesting integration components...")

    try:
        from file_utilities_2.gui.image_metadata_gui import ImageMetadataEditor
        from PyQt5.QtWidgets import QApplication

        # Create QApplication if it doesn't exist
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        editor = ImageMetadataEditor()

        # Test StandardWindow inheritance
        if hasattr(editor, "theme_manager"):
            print("✓ ThemeManager integration present")
        else:
            print("✗ ThemeManager integration missing")
            return False

        # Test HubConnector
        if hasattr(editor, "hub_connector") and editor.hub_connector:
            print("✓ HubConnector integration present")
            if hasattr(editor.hub_connector, "tool_name"):
                print(f"✓ Tool name: {editor.hub_connector.tool_name}")
            else:
                print("✗ HubConnector tool_name missing")
                return False
        else:
            print("✗ HubConnector integration missing")
            return False

        # Test progress tracking signals
        if hasattr(editor.logic, "progress_percentage"):
            print("✓ Progress tracking signals present")
        else:
            print("✗ Progress tracking signals missing")
            return False

        return True

    except Exception as e:
        print(f"✗ Integration components test failed: {e}")
        traceback.print_exc()
        return False


def test_file_structure():
    """Test that all required files are in place."""
    print("\nTesting file structure...")

    required_files = [
        "file_utilities_2/core/image_metadata_logic.py",
        "file_utilities_2/gui/image_metadata_gui.py",
        "file_utilities_2/gui/image_metadata.ui",
        "file_utilities_2/tests/test_image_metadata.py",
    ]

    all_present = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path} present")
        else:
            print(f"✗ {file_path} missing")
            all_present = False

    return all_present


def test_original_files_cleanup():
    """Test that original files are ready for cleanup."""
    print("\nTesting original files status...")

    original_files = ["edit_image_metadata.py", "edit_image_metadata.ui"]

    files_exist = []
    for file_path in original_files:
        if os.path.exists(file_path):
            files_exist.append(file_path)
            print(f"! {file_path} still present (ready for cleanup)")
        else:
            print(f"✓ {file_path} already removed")

    return files_exist


def run_comprehensive_validation():
    """Run all validation tests."""
    print("=" * 60)
    print("IMAGE METADATA EDITOR MIGRATION VALIDATION")
    print("=" * 60)

    tests = [
        ("Import Tests", test_imports),
        ("Core Functionality Tests", test_core_functionality),
        ("GUI Initialization Tests", test_gui_initialization),
        ("Integration Component Tests", test_integration_components),
        ("File Structure Tests", test_file_structure),
    ]

    results = {}

    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 40)
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            results[test_name] = False

    # Check original files
    print(f"\nOriginal Files Cleanup Check:")
    print("-" * 40)
    original_files = test_original_files_cleanup()

    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)

    passed = sum(1 for result in results.values() if result)
    total = len(results)

    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")

    print(f"\nOverall: {passed}/{total} tests passed")

    if original_files:
        print(f"\nOriginal files ready for cleanup: {len(original_files)}")
        for file_path in original_files:
            print(f"  - {file_path}")
    else:
        print("\nNo original files found (already cleaned up)")

    # Migration status
    if passed == total:
        print("\n🎉 MIGRATION VALIDATION: SUCCESS")
        print("All components migrated successfully!")
        if original_files:
            print("Ready to remove original files.")
        return True
    else:
        print("\n❌ MIGRATION VALIDATION: ISSUES DETECTED")
        print("Some components need attention before cleanup.")
        return False


if __name__ == "__main__":
    success = run_comprehensive_validation()
    sys.exit(0 if success else 1)
