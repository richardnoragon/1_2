#!/usr/bin/env python3
"""
Size Analyzer Migration Test Script

This script validates that the Size Analyzer migration was successful
by testing the core functionality and imports.
"""

import os
import sys
import tempfile
import traceback
from typing import Dict, Any


def test_imports():
    """Test that all new components can be imported."""
    print("Testing imports...")

    try:
        # Test core logic import
        from file_utilities_2.core.size_analyzer_logic import (
            SizeAnalyzer,
            SizeAnalyzerWorker,
        )

        print("✓ Core logic imports successful")

        # Test GUI import
        from file_utilities_2.gui.size_analyzer_gui import SizeAnalyzerGUI

        print("✓ GUI imports successful")

        # Test package-level imports
        from file_utilities_2 import (
            SizeAnalyzer,
            SizeAnalyzerWorker,
            SizeAnalyzerGUI,
        )

        print("✓ Package-level imports successful")

        return True

    except Exception as e:
        print(f"✗ Import failed: {e}")
        traceback.print_exc()
        return False


def test_size_analyzer_class():
    """Test the SizeAnalyzer class functionality."""
    print("\nTesting SizeAnalyzer class...")

    try:
        from file_utilities_2.core.size_analyzer_logic import SizeAnalyzer

        # Create analyzer instance
        analyzer = SizeAnalyzer()
        print("✓ SizeAnalyzer instance created")

        # Test format_size method
        test_sizes = [
            (1024, "1.0 KB"),
            (1024 * 1024, "1.0 MB"),
            (1024 * 1024 * 1024, "1.0 GB"),
            (123, "123.0 B"),
        ]

        for size, expected in test_sizes:
            result = analyzer.format_size(size)
            if result == expected:
                print(f"✓ format_size({size}) = {result}")
            else:
                print(f"✗ format_size({size}) = {result}, expected {expected}")
                return False

        return True

    except Exception as e:
        print(f"✗ SizeAnalyzer test failed: {e}")
        traceback.print_exc()
        return False


def test_directory_analysis():
    """Test directory analysis functionality."""
    print("\nTesting directory analysis...")

    try:
        from file_utilities_2.core.size_analyzer_logic import SizeAnalyzer

        # Create temporary test directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            test_files = {
                "test1.txt": b"Hello World" * 100,  # ~1KB
                "test2.py": b'print("test")' * 50,  # ~650B
                "test3.md": b"# Test\nContent" * 20,  # ~280B
            }

            for filename, content in test_files.items():
                file_path = os.path.join(temp_dir, filename)
                with open(file_path, "wb") as f:
                    f.write(content)

            # Create subdirectory
            sub_dir = os.path.join(temp_dir, "subdir")
            os.makedirs(sub_dir)
            with open(os.path.join(sub_dir, "sub_test.txt"), "wb") as f:
                f.write(b"Subdirectory file" * 10)

            # Test analysis
            analyzer = SizeAnalyzer()
            analysis = analyzer.analyze_directory(temp_dir)

            # Validate results
            assert isinstance(
                analysis, dict
            ), "Analysis should return a dictionary"
            assert (
                "total_size" in analysis
            ), "Analysis should include total_size"
            assert (
                "file_count" in analysis
            ), "Analysis should include file_count"
            assert (
                "directory_count" in analysis
            ), "Analysis should include directory_count"
            assert "files" in analysis, "Analysis should include files list"
            assert (
                "file_types" in analysis
            ), "Analysis should include file_types"

            print(f"✓ Analysis completed for {temp_dir}")
            print(f"  - Files: {analysis['file_count']}")
            print(f"  - Directories: {analysis['directory_count']}")
            print(
                f"  - Total Size: {analyzer.format_size(analysis['total_size'])}"
            )
            print(f"  - File Types: {len(analysis['file_types'])}")

            # Test export functionality
            export_path = os.path.join(temp_dir, "analysis_export.json")
            analyzer.export_analysis(analysis, export_path)

            if os.path.exists(export_path):
                print("✓ Export functionality working")
            else:
                print("✗ Export functionality failed")
                return False

        return True

    except Exception as e:
        print(f"✗ Directory analysis test failed: {e}")
        traceback.print_exc()
        return False


def test_gui_creation():
    """Test GUI creation (without showing)."""
    print("\nTesting GUI creation...")

    try:
        # Import Qt components
        from PyQt5.QtWidgets import QApplication
        from file_utilities_2.gui.size_analyzer_gui import SizeAnalyzerGUI

        # Create QApplication if it doesn't exist
        app = QApplication.instance()
        if app is None:
            app = QApplication([])

        # Create GUI instance
        gui = SizeAnalyzerGUI()
        print("✓ SizeAnalyzerGUI instance created")

        # Test that required components exist
        assert hasattr(gui, "analyzer"), "GUI should have analyzer attribute"
        assert hasattr(
            gui, "selected_directory"
        ), "GUI should have selected_directory attribute"

        print("✓ GUI components validated")

        return True

    except Exception as e:
        print(f"✗ GUI creation test failed: {e}")
        traceback.print_exc()
        return False


def test_backward_compatibility():
    """Test that the migration maintains backward compatibility."""
    print("\nTesting backward compatibility...")

    try:
        # Test that the old import still works for the window class
        from size_analyzer import SizeAnalyzerWindow

        print("✓ Original SizeAnalyzerWindow still importable")

        # Test that the new SizeAnalyzer class is available
        from file_utilities_2.core.size_analyzer_logic import SizeAnalyzer

        print("✓ New SizeAnalyzer class available")

        return True

    except Exception as e:
        print(f"✗ Backward compatibility test failed: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all migration tests."""
    print("Size Analyzer Migration Validation")
    print("=" * 50)

    tests = [
        ("Import Tests", test_imports),
        ("SizeAnalyzer Class Tests", test_size_analyzer_class),
        ("Directory Analysis Tests", test_directory_analysis),
        ("GUI Creation Tests", test_gui_creation),
        ("Backward Compatibility Tests", test_backward_compatibility),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n{test_name}")
        print("-" * len(test_name))

        try:
            if test_func():
                passed += 1
                print(f"✓ {test_name} PASSED")
            else:
                print(f"✗ {test_name} FAILED")
        except Exception as e:
            print(f"✗ {test_name} FAILED with exception: {e}")

    print(f"\n{'='*50}")
    print(f"Migration Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Migration successful!")
        return 0
    else:
        print("❌ Some tests failed. Please review the migration.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
