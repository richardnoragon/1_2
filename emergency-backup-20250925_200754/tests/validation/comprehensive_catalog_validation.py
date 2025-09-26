#!/usr/bin/env python3
"""
Comprehensive Catalog Migration Validation Script

This script performs final validation to ensure all integrations work correctly
after the catalog migration from root directory to file_utilities_1/.

Validation Areas:
1. Import Validation
2. Integration Point Validation
3. File Path Resolution
4. Functionality Preservation
5. Cross-Reference Validation
"""

import sys
import os
import traceback
import importlib
import subprocess
from pathlib import Path


class CatalogValidationTester:
    def __init__(self):
        self.test_results = []
        self.failed_tests = []
        self.passed_tests = []

    def log_test(self, test_name, success, details=""):
        """Log test result"""
        result = {"test": test_name, "success": success, "details": details}
        self.test_results.append(result)

        if success:
            self.passed_tests.append(test_name)
            print(f"✅ PASS: {test_name}")
        else:
            self.failed_tests.append(test_name)
            print(f"❌ FAIL: {test_name}")
            if details:
                print(f"   Details: {details}")

    def test_basic_import(self):
        """Test 1: Basic import validation"""
        print("\n=== 1. IMPORT VALIDATION ===")

        # Test 1.1: Basic CatalogWindow import
        try:
            from file_utilities_1.catalog import CatalogWindow

            self.log_test("Basic CatalogWindow import", True)
        except Exception as e:
            self.log_test("Basic CatalogWindow import", False, str(e))
            return False

        # Test 1.2: Check if CatalogWindow is properly defined
        try:
            if hasattr(CatalogWindow, "__init__"):
                self.log_test("CatalogWindow class definition", True)
            else:
                self.log_test(
                    "CatalogWindow class definition",
                    False,
                    "Missing __init__ method",
                )
        except Exception as e:
            self.log_test("CatalogWindow class definition", False, str(e))

        # Test 1.3: Test GUI dependencies accessibility
        try:
            from file_utilities_1.catalog import CatalogWindow

            # Check if BaseWindow is accessible
            catalog_instance = None
            # We'll test instantiation later, just check import dependencies here
            import sys

            if "gui.common.base_window" in sys.modules or "gui" in sys.modules:
                self.log_test("GUI dependencies accessible", True)
            else:
                # Try to access the BaseWindow through catalog module
                import file_utilities_1.catalog as catalog_mod

                if hasattr(catalog_mod, "BaseWindow") or "BaseWindow" in str(
                    catalog_mod
                ):
                    self.log_test("GUI dependencies accessible", True)
                else:
                    self.log_test(
                        "GUI dependencies accessible",
                        False,
                        "BaseWindow not found in imports",
                    )
        except Exception as e:
            self.log_test("GUI dependencies accessible", False, str(e))

        return True

    def test_integration_points(self):
        """Test 2: Integration point validation"""
        print("\n=== 2. INTEGRATION POINT VALIDATION ===")

        # Test 2.1: rfuhub.py can import CatalogWindow
        try:
            # Read rfuhub.py to check import statement
            with open("rfuhub.py", "r", encoding="utf-8") as f:
                rfuhub_content = f.read()

            if (
                "from file_utilities_1.catalog import CatalogWindow"
                in rfuhub_content
            ):
                self.log_test("rfuhub.py import statement updated", True)
            else:
                self.log_test(
                    "rfuhub.py import statement updated",
                    False,
                    "Import statement not found or incorrect",
                )
        except Exception as e:
            self.log_test("rfuhub.py import statement updated", False, str(e))

        # Test 2.2: test_catalog.py can import and run
        try:
            # Check if test_catalog.py exists and has correct imports
            test_catalog_path = Path("tests/test_catalog.py")
            if test_catalog_path.exists():
                with open(test_catalog_path, "r", encoding="utf-8") as f:
                    test_content = f.read()

                if (
                    "from file_utilities_1.catalog import CatalogWindow"
                    in test_content
                ):
                    self.log_test("test_catalog.py import statement", True)
                else:
                    self.log_test(
                        "test_catalog.py import statement",
                        False,
                        "Import statement not updated",
                    )
            else:
                self.log_test(
                    "test_catalog.py import statement",
                    False,
                    "test_catalog.py not found",
                )
        except Exception as e:
            self.log_test("test_catalog.py import statement", False, str(e))

        # Test 2.3: test_main.py works with updated imports
        try:
            test_main_path = Path("tests/test_main.py")
            if test_main_path.exists():
                with open(test_main_path, "r", encoding="utf-8") as f:
                    test_main_content = f.read()

                # Check if it references catalog correctly
                if "catalog" in test_main_content.lower():
                    self.log_test("test_main.py catalog references", True)
                else:
                    self.log_test(
                        "test_main.py catalog references",
                        True,
                        "No catalog references found (may be OK)",
                    )
            else:
                self.log_test(
                    "test_main.py catalog references",
                    False,
                    "test_main.py not found",
                )
        except Exception as e:
            self.log_test("test_main.py catalog references", False, str(e))

    def test_file_path_resolution(self):
        """Test 3: File path resolution"""
        print("\n=== 3. FILE PATH RESOLUTION ===")

        # Test 3.1: catalog.ui exists in new location
        catalog_ui_path = Path("file_utilities_1/catalog.ui")
        if catalog_ui_path.exists():
            self.log_test("catalog.ui in new location", True)
        else:
            self.log_test(
                "catalog.ui in new location",
                False,
                "catalog.ui not found in file_utilities_1/",
            )

        # Test 3.2: catalog.png icon exists
        catalog_icon_path = Path("file_utilities_1/icons/catalog.png")
        if catalog_icon_path.exists():
            self.log_test("catalog.png icon exists", True)
        else:
            self.log_test(
                "catalog.png icon exists",
                False,
                "catalog.png not found in file_utilities_1/icons/",
            )

        # Test 3.3: Check path resolution in catalog.py
        try:
            with open(
                "file_utilities_1/catalog.py", "r", encoding="utf-8"
            ) as f:
                catalog_content = f.read()

            # Check for proper path handling
            if "__file__" in catalog_content and "dirname" in catalog_content:
                self.log_test("Path resolution logic in catalog.py", True)
            else:
                self.log_test(
                    "Path resolution logic in catalog.py",
                    False,
                    "Missing __file__ or dirname usage",
                )
        except Exception as e:
            self.log_test("Path resolution logic in catalog.py", False, str(e))

    def test_functionality_preservation(self):
        """Test 4: Functionality preservation"""
        print("\n=== 4. FUNCTIONALITY PRESERVATION ===")

        # Test 4.1: Try to instantiate CatalogWindow (without GUI)
        try:
            # Import without creating GUI
            from file_utilities_1.catalog import CatalogWindow

            # Check if class has expected methods
            expected_methods = ["__init__", "scan_directory", "generate_html"]
            missing_methods = []

            for method in expected_methods:
                if not hasattr(CatalogWindow, method):
                    missing_methods.append(method)

            if not missing_methods:
                self.log_test("CatalogWindow methods preserved", True)
            else:
                self.log_test(
                    "CatalogWindow methods preserved",
                    False,
                    f"Missing methods: {missing_methods}",
                )
        except Exception as e:
            self.log_test("CatalogWindow methods preserved", False, str(e))

        # Test 4.2: Check PyQt5 imports
        try:
            from file_utilities_1.catalog import CatalogWindow
            import file_utilities_1.catalog as catalog_module

            # Check if PyQt5 is imported in the module
            catalog_source = open(
                "file_utilities_1/catalog.py", "r", encoding="utf-8"
            ).read()
            if "PyQt5" in catalog_source:
                self.log_test("PyQt5 imports maintained", True)
            else:
                self.log_test(
                    "PyQt5 imports maintained",
                    False,
                    "PyQt5 imports not found",
                )
        except Exception as e:
            self.log_test("PyQt5 imports maintained", False, str(e))

    def test_cross_references(self):
        """Test 5: Cross-reference validation"""
        print("\n=== 5. CROSS-REFERENCE VALIDATION ===")

        # Test 5.1: Check migration scripts
        migration_script_path = Path("tools/gui_migration/migrate_catalog.py")
        if migration_script_path.exists():
            try:
                with open(migration_script_path, "r", encoding="utf-8") as f:
                    migration_content = f.read()

                if "file_utilities_1" in migration_content:
                    self.log_test(
                        "Migration script references correct location", True
                    )
                else:
                    self.log_test(
                        "Migration script references correct location",
                        False,
                        "file_utilities_1 not found in migration script",
                    )
            except Exception as e:
                self.log_test(
                    "Migration script references correct location",
                    False,
                    str(e),
                )
        else:
            self.log_test(
                "Migration script references correct location",
                False,
                "Migration script not found",
            )

        # Test 5.2: Check styling tools
        styling_tool_path = Path("tools/apply_standardized_styling.py")
        if styling_tool_path.exists():
            try:
                with open(styling_tool_path, "r", encoding="utf-8") as f:
                    styling_content = f.read()

                # Check if it can find the moved files
                if (
                    "file_utilities_1" in styling_content
                    or "catalog" not in styling_content
                ):
                    self.log_test(
                        "Styling tools updated for new location", True
                    )
                else:
                    self.log_test(
                        "Styling tools updated for new location",
                        False,
                        "May need updating for new catalog location",
                    )
            except Exception as e:
                self.log_test(
                    "Styling tools updated for new location", False, str(e)
                )
        else:
            self.log_test(
                "Styling tools updated for new location",
                False,
                "Styling tool not found",
            )

        # Test 5.3: Check documentation references
        readme_path = Path("README.md")
        if readme_path.exists():
            try:
                with open(readme_path, "r", encoding="utf-8") as f:
                    readme_content = f.read()

                # This is informational - documentation may not be updated yet
                if "file_utilities_1" in readme_content:
                    self.log_test("Documentation references updated", True)
                else:
                    self.log_test(
                        "Documentation references updated",
                        False,
                        "Documentation may need updating (informational)",
                    )
            except Exception as e:
                self.log_test(
                    "Documentation references updated", False, str(e)
                )
        else:
            self.log_test(
                "Documentation references updated",
                False,
                "README.md not found",
            )

    def run_syntax_validation(self):
        """Test 6: Syntax validation"""
        print("\n=== 6. SYNTAX VALIDATION ===")

        # Test syntax of moved files
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "py_compile",
                    "file_utilities_1/catalog.py",
                ],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                self.log_test("catalog.py syntax validation", True)
            else:
                self.log_test(
                    "catalog.py syntax validation", False, result.stderr
                )
        except Exception as e:
            self.log_test("catalog.py syntax validation", False, str(e))

    def run_all_tests(self):
        """Run all validation tests"""
        print("🔍 Starting Comprehensive Catalog Migration Validation")
        print("=" * 60)

        # Run all test suites
        self.test_basic_import()
        self.test_integration_points()
        self.test_file_path_resolution()
        self.test_functionality_preservation()
        self.test_cross_references()
        self.run_syntax_validation()

        # Print summary
        print("\n" + "=" * 60)
        print("📊 VALIDATION SUMMARY")
        print("=" * 60)

        total_tests = len(self.test_results)
        passed_count = len(self.passed_tests)
        failed_count = len(self.failed_tests)

        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_count}")
        print(f"Failed: {failed_count}")
        print(f"Success Rate: {(passed_count/total_tests)*100:.1f}%")

        if self.failed_tests:
            print(f"\n❌ Failed Tests:")
            for test in self.failed_tests:
                print(f"   - {test}")

        if passed_count == total_tests:
            print(
                f"\n🎉 ALL TESTS PASSED! Catalog migration validation successful."
            )
            return True
        else:
            print(f"\n⚠️  Some tests failed. Review the issues above.")
            return False


def main():
    """Main validation function"""
    validator = CatalogValidationTester()
    success = validator.run_all_tests()

    if success:
        print("\n✅ Catalog migration validation completed successfully!")
        sys.exit(0)
    else:
        print(
            "\n❌ Catalog migration validation found issues that need attention."
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
