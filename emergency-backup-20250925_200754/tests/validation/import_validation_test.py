#!/usr/bin/env python3
"""
Import validation test for TagViewerEditor migration.

This script validates that the TagViewerEditor can be successfully imported
from its new location in file_utilities_2.gui.tag_viewer_editor.
"""


def test_tag_viewer_editor_import():
    """Test importing TagViewerEditor from new location."""
    try:
        from file_utilities_2.gui.tag_viewer_editor import TagViewerEditor

        print(
            "✓ SUCCESS: TagViewerEditor imported successfully from file_utilities_2.gui.tag_viewer_editor"
        )
        return True
    except ImportError as e:
        print(f"✗ FAILED: Could not import TagViewerEditor: {e}")
        return False
    except Exception as e:
        print(f"✗ ERROR: Unexpected error during import: {e}")
        return False


def test_gui_module_import():
    """Test importing TagViewerEditor from gui module."""
    try:
        from file_utilities_2.gui import TagViewerEditor

        print(
            "✓ SUCCESS: TagViewerEditor imported successfully from file_utilities_2.gui"
        )
        return True
    except ImportError as e:
        print(
            f"✗ FAILED: Could not import TagViewerEditor from gui module: {e}"
        )
        return False
    except Exception as e:
        print(f"✗ ERROR: Unexpected error during gui module import: {e}")
        return False


def validate_class_attributes():
    """Validate that TagViewerEditor has expected attributes."""
    try:
        from file_utilities_2.gui.tag_viewer_editor import TagViewerEditor

        # Check if it's a class
        if not isinstance(TagViewerEditor, type):
            print("✗ FAILED: TagViewerEditor is not a class")
            return False

        print("✓ SUCCESS: TagViewerEditor is a valid class")
        return True
    except Exception as e:
        print(f"✗ ERROR: Could not validate class attributes: {e}")
        return False


def main():
    """Run all import validation tests."""
    print("TagViewerEditor Import Validation Test")
    print("=" * 50)

    tests = [
        test_tag_viewer_editor_import,
        test_gui_module_import,
        validate_class_attributes,
    ]

    results = []
    for test in tests:
        print(f"\nRunning {test.__name__}...")
        results.append(test())

    print("\n" + "=" * 50)
    print("VALIDATION SUMMARY:")
    print(f"Tests passed: {sum(results)}/{len(results)}")

    if all(results):
        print("✓ ALL TESTS PASSED: Import migration successful!")
        return 0
    else:
        print("✗ SOME TESTS FAILED: Import migration needs attention!")
        return 1


if __name__ == "__main__":
    exit(main())
