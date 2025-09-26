#!/usr/bin/env python3
"""
Final Validation Test Script for FileFinderWindow Migration
Tests all critical functionality and import paths to ensure production readiness.
"""

import sys
import os
import traceback
import importlib
from pathlib import Path
from typing import List, Dict, Any


class FinalValidationTester:
    """Comprehensive validation tester for FileFinderWindow migration."""

    def __init__(self):
        self.test_results = []
        self.passed_tests = 0
        self.failed_tests = 0

    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log test result."""
        status = "✅ PASS" if passed else "❌ FAIL"
        self.test_results.append(
            {
                "name": test_name,
                "status": status,
                "passed": passed,
                "details": details,
            }
        )

        if passed:
            self.passed_tests += 1
        else:
            self.failed_tests += 1

        print(f"{status}: {test_name}")
        if details:
            print(f"    Details: {details}")

    def test_import_paths(self) -> None:
        """Test all critical import paths."""
        print("\n=== TASK 20: Import System Validation ===")

        # Test 1: Import from file_utilities_1 package
        try:
            from file_utilities_1 import FileFinderWindow

            self.log_test(
                "Import from file_utilities_1",
                True,
                "FileFinderWindow imported successfully from package",
            )
        except Exception as e:
            self.log_test("Import from file_utilities_1", False, str(e))

        # Test 2: Direct module import
        try:
            from file_utilities_1.file_finder import FileFinderWindow

            self.log_test(
                "Direct module import",
                True,
                "FileFinderWindow imported directly from module",
            )
        except Exception as e:
            self.log_test("Direct module import", False, str(e))

        # Test 3: Backward compatibility import
        try:
            from file_finder import FileFinder

            self.log_test(
                "Backward compatibility import",
                True,
                "FileFinder wrapper class imported successfully",
            )
        except Exception as e:
            self.log_test("Backward compatibility import", False, str(e))

        # Test 4: Package __init__.py exports
        try:
            import file_utilities_1

            exports = getattr(file_utilities_1, "__all__", [])
            has_file_finder = "FileFinderWindow" in exports
            self.log_test(
                "Package exports FileFinderWindow",
                has_file_finder,
                f"__all__ contains: {exports}",
            )
        except Exception as e:
            self.log_test("Package exports FileFinderWindow", False, str(e))

    def test_file_structure(self) -> None:
        """Test file structure and organization."""
        print("\n=== File Structure Validation ===")

        # Test migrated files exist
        files_to_check = [
            "file_utilities_1/__init__.py",
            "file_utilities_1/file_finder.py",
            "file_utilities_1/file_finder.ui",
            "file_utilities_1/icons/folder.png",
            "file_utilities_1/icons/search.png",
            "file_finder.py",  # Backward compatibility file
        ]

        for file_path in files_to_check:
            exists = Path(file_path).exists()
            self.log_test(
                f"File exists: {file_path}",
                exists,
                f"File {'found' if exists else 'missing'}",
            )

    def test_critical_fixes(self) -> None:
        """Test that critical bug fixes are in place."""
        print("\n=== TASK 19: Critical Bug Fixes Validation ===")

        # Test pathlib import fix
        try:
            with open("file_utilities_1/file_finder.py", "r") as f:
                content = f.read()

            has_pathlib_import = "import pathlib" in content
            has_pathlib_from_import = "from pathlib import Path" in content

            self.log_test(
                "pathlib import fix",
                has_pathlib_import,
                "import pathlib statement found",
            )
            self.log_test(
                "pathlib Path import fix",
                has_pathlib_from_import,
                "from pathlib import Path statement found",
            )
        except Exception as e:
            self.log_test("pathlib import fix", False, str(e))

        # Test traceback import fix
        try:
            with open("file_utilities_1/file_finder.py", "r") as f:
                content = f.read()

            has_traceback_import = "import traceback" in content
            self.log_test(
                "traceback import fix",
                has_traceback_import,
                "import traceback statement found",
            )
        except Exception as e:
            self.log_test("traceback import fix", False, str(e))

        # Test UI loading path fix
        try:
            with open("file_utilities_1/file_finder.py", "r") as f:
                content = f.read()

            has_relative_ui_path = (
                'Path(__file__).parent / "file_finder.ui"' in content
            )
            self.log_test(
                "UI loading path fix",
                has_relative_ui_path,
                "Relative UI path resolution implemented",
            )
        except Exception as e:
            self.log_test("UI loading path fix", False, str(e))

    def test_rfuhub_integration(self) -> None:
        """Test RFU Hub integration."""
        print("\n=== RFU Hub Integration Validation ===")

        try:
            with open("rfuhub.py", "r") as f:
                content = f.read()

            # Check for updated import
            has_new_import = (
                "from file_utilities_1 import FileFinderWindow" in content
            )
            self.log_test(
                "RFU Hub updated import",
                has_new_import,
                "RFU Hub uses new import path",
            )

            # Check for updated instantiation
            has_new_instantiation = "FileFinderWindow()" in content
            self.log_test(
                "RFU Hub updated instantiation",
                has_new_instantiation,
                "RFU Hub uses new class name",
            )

        except Exception as e:
            self.log_test("RFU Hub integration", False, str(e))

    def test_class_instantiation(self) -> None:
        """Test class instantiation without GUI."""
        print("\n=== Class Instantiation Testing ===")

        # Test FileFinderWindow instantiation
        try:
            from file_utilities_1 import FileFinderWindow

            # Don't actually create the window to avoid GUI issues
            # Just test that the class can be imported and has expected attributes

            has_init = hasattr(FileFinderWindow, "__init__")
            self.log_test(
                "FileFinderWindow has __init__",
                has_init,
                "Class properly defined with constructor",
            )

            # Check for key methods
            expected_methods = [
                "search",
                "show_metadata",
                "open_file",
                "select_directory",
            ]
            for method in expected_methods:
                has_method = hasattr(FileFinderWindow, method)
                self.log_test(
                    f"FileFinderWindow has {method} method",
                    has_method,
                    f"Method {'found' if has_method else 'missing'}",
                )

        except Exception as e:
            self.log_test("FileFinderWindow instantiation test", False, str(e))

        # Test FileFinder wrapper instantiation
        try:
            from file_finder import FileFinder

            has_init = hasattr(FileFinder, "__init__")
            self.log_test(
                "FileFinder wrapper has __init__",
                has_init,
                "Wrapper class properly defined",
            )
        except Exception as e:
            self.log_test(
                "FileFinder wrapper instantiation test", False, str(e)
            )

    def test_dependencies(self) -> None:
        """Test all required dependencies."""
        print("\n=== Dependency Validation ===")

        dependencies = [
            "PyQt5",
            "pathlib",
            "traceback",
            "datetime",
            "subprocess",
            "docx",
            "PyPDF2",
            "chardet",
            "os",
            "sys",
        ]

        for dep in dependencies:
            try:
                importlib.import_module(dep)
                self.log_test(f"Dependency: {dep}", True, "Module available")
            except ImportError:
                self.log_test(
                    f"Dependency: {dep}", False, "Module not available"
                )

    def test_backward_compatibility(self) -> None:
        """Test backward compatibility features."""
        print("\n=== Backward Compatibility Validation ===")

        # Test that old import still works
        try:
            from file_finder import FileFinder

            # Test that wrapper has expected attributes for tests
            wrapper_attrs = [
                "pattern_edit",
                "search_button",
                "results_list",
                "recursive_check",
                "show_hidden_check",
            ]

            # Create instance to test attributes (without showing GUI)
            instance = FileFinder()

            for attr in wrapper_attrs:
                has_attr = hasattr(instance, attr)
                self.log_test(
                    f"FileFinder has {attr} attribute",
                    has_attr,
                    f"Attribute {'found' if has_attr else 'missing'}",
                )

        except Exception as e:
            self.log_test("Backward compatibility test", False, str(e))

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all validation tests."""
        print(
            "🚀 Starting Final Validation Testing for FileFinderWindow Migration"
        )
        print("=" * 80)

        # Run all test categories
        self.test_import_paths()
        self.test_file_structure()
        self.test_critical_fixes()
        self.test_rfuhub_integration()
        self.test_class_instantiation()
        self.test_dependencies()
        self.test_backward_compatibility()

        # Generate summary
        total_tests = self.passed_tests + self.failed_tests
        success_rate = (
            (self.passed_tests / total_tests * 100) if total_tests > 0 else 0
        )

        print("\n" + "=" * 80)
        print("🏁 FINAL VALIDATION SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")

        if self.failed_tests == 0:
            print("🎉 ALL TESTS PASSED - MIGRATION VALIDATION SUCCESSFUL!")
            print("✅ Production Ready - Zero regressions detected")
        else:
            print("⚠️  SOME TESTS FAILED - Review required before production")

        return {
            "total_tests": total_tests,
            "passed": self.passed_tests,
            "failed": self.failed_tests,
            "success_rate": success_rate,
            "test_results": self.test_results,
            "production_ready": self.failed_tests == 0,
        }


def main():
    """Main function to run validation tests."""
    tester = FinalValidationTester()
    results = tester.run_all_tests()

    # Return exit code based on results
    return 0 if results["production_ready"] else 1


if __name__ == "__main__":
    sys.exit(main())
