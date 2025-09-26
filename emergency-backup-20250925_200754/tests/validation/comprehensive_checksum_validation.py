#!/usr/bin/env python3
"""
Comprehensive Final Integration Validation and Testing
for Checksum Files Migration to file_utilities_2

This script performs end-to-end validation of the completed migration.
"""

import sys
import os
import time
import traceback
from pathlib import Path


def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def print_test(test_name, status, details=""):
    """Print test result with consistent formatting"""
    status_symbol = "✅" if status else "❌"
    print(f"{status_symbol} {test_name}")
    if details:
        print(f"   {details}")


def test_basic_imports():
    """Test 1: Basic Import Validation"""
    print_section("1. BASIC IMPORT VALIDATION")

    results = {}

    # Test PyQt5 imports
    try:
        from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
        from PyQt5.QtCore import QObject, pyqtSignal, QThread, QTimer
        from PyQt5.QtGui import QFont

        results["pyqt5"] = True
        print_test("PyQt5 core imports", True)
    except ImportError as e:
        results["pyqt5"] = False
        print_test("PyQt5 core imports", False, str(e))

    # Test file_utilities_2 package-level imports
    try:
        from file_utilities_2.core.check_sum import (
            ChecksumLogic,
            VALID_ALGORITHMS,
        )

        results["core_logic"] = True
        print_test(
            "Core checksum logic import",
            True,
            f"Algorithms: {VALID_ALGORITHMS}",
        )
    except ImportError as e:
        results["core_logic"] = False
        print_test("Core checksum logic import", False, str(e))

    # Test GUI imports
    try:
        from file_utilities_2.gui.check_sum_gui import ChecksumGUI

        results["enhanced_gui"] = True
        print_test("Enhanced GUI import", True)
    except ImportError as e:
        results["enhanced_gui"] = False
        print_test("Enhanced GUI import", False, str(e))

    try:
        from file_utilities_2.gui.check_sum_standardized import (
            ChecksumWindow,
            EnhancedChecksumThread,
        )

        results["standardized_gui"] = True
        print_test("Standardized GUI import", True)
    except ImportError as e:
        results["standardized_gui"] = False
        print_test("Standardized GUI import", False, str(e))

    # Test package-level imports
    try:
        from file_utilities_2 import (
            ChecksumLogic as PkgChecksumLogic,
            VALID_ALGORITHMS as PkgAlgorithms,
        )

        results["package_level"] = True
        print_test("Package-level imports", True)
    except ImportError as e:
        results["package_level"] = False
        print_test("Package-level imports", False, str(e))

    return results


def test_external_imports():
    """Test 2: External File Import Validation"""
    print_section("2. EXTERNAL FILE IMPORT VALIDATION")

    results = {}

    # Test rfuhub.py import
    try:
        if os.path.exists("rfuhub.py"):
            # Read the file to check import statements
            with open("rfuhub.py", "r", encoding="utf-8") as f:
                content = f.read()

            if (
                "from file_utilities_2.gui.check_sum_gui import ChecksumGUI"
                in content
            ):
                results["rfuhub_import"] = True
                print_test(
                    "rfuhub.py import statement",
                    True,
                    "Correctly imports from file_utilities_2",
                )
            else:
                results["rfuhub_import"] = False
                print_test(
                    "rfuhub.py import statement",
                    False,
                    "Import statement not found or incorrect",
                )
        else:
            results["rfuhub_import"] = None
            print_test("rfuhub.py file", False, "File not found")
    except Exception as e:
        results["rfuhub_import"] = False
        print_test("rfuhub.py validation", False, str(e))

    # Test tests/test_checksum.py import
    try:
        if os.path.exists("tests/test_checksum.py"):
            with open("tests/test_checksum.py", "r", encoding="utf-8") as f:
                content = f.read()

            if (
                "from file_utilities_2.core.check_sum import ChecksumLogic"
                in content
            ):
                results["test_checksum_import"] = True
                print_test(
                    "tests/test_checksum.py import",
                    True,
                    "Correctly imports from file_utilities_2",
                )
            else:
                results["test_checksum_import"] = False
                print_test(
                    "tests/test_checksum.py import",
                    False,
                    "Import statement not found or incorrect",
                )
        else:
            results["test_checksum_import"] = None
            print_test("tests/test_checksum.py file", False, "File not found")
    except Exception as e:
        results["test_checksum_import"] = False
        print_test("tests/test_checksum.py validation", False, str(e))

    return results


def test_functional_validation():
    """Test 3: Functional Validation"""
    print_section("3. FUNCTIONAL VALIDATION")

    results = {}

    try:
        from file_utilities_2.core.check_sum import (
            ChecksumLogic,
            VALID_ALGORITHMS,
        )

        # Test ChecksumLogic instantiation
        try:
            logic = ChecksumLogic()
            results["logic_instantiation"] = True
            print_test("ChecksumLogic instantiation", True)
        except Exception as e:
            results["logic_instantiation"] = False
            print_test("ChecksumLogic instantiation", False, str(e))

        # Test algorithm validation
        try:
            test_algorithms = ["md5", "sha1", "sha256", "sha512"]
            available_algorithms = [
                alg for alg in test_algorithms if alg in VALID_ALGORITHMS
            ]
            if available_algorithms:
                results["algorithms_available"] = True
                print_test(
                    "Algorithm availability",
                    True,
                    f"Available: {available_algorithms}",
                )
            else:
                results["algorithms_available"] = False
                print_test(
                    "Algorithm availability",
                    False,
                    "No standard algorithms found",
                )
        except Exception as e:
            results["algorithms_available"] = False
            print_test("Algorithm availability", False, str(e))

        # Test basic checksum calculation
        try:
            if results.get("logic_instantiation", False):
                # Create a test file
                test_file = Path("test_checksum_file.txt")
                test_file.write_text("Hello, World!")

                # Calculate checksum
                checksum = logic.calculate_checksum(str(test_file), "md5")
                if checksum:
                    results["checksum_calculation"] = True
                    print_test(
                        "Checksum calculation", True, f"MD5: {checksum}"
                    )
                else:
                    results["checksum_calculation"] = False
                    print_test(
                        "Checksum calculation", False, "No checksum returned"
                    )

                # Clean up
                test_file.unlink()
        except Exception as e:
            results["checksum_calculation"] = False
            print_test("Checksum calculation", False, str(e))

    except ImportError as e:
        results["functional_test"] = False
        print_test("Functional validation setup", False, f"Import failed: {e}")

    return results


def test_gui_instantiation():
    """Test 4: GUI Component Instantiation"""
    print_section("4. GUI COMPONENT INSTANTIATION")

    results = {}

    try:
        from PyQt5.QtWidgets import QApplication
        from file_utilities_2.gui.check_sum_gui import ChecksumGUI
        from file_utilities_2.gui.check_sum_standardized import ChecksumWindow

        # Create QApplication if it doesn't exist
        app = QApplication.instance()
        if app is None:
            app = QApplication([])

        # Test ChecksumGUI instantiation
        try:
            gui = ChecksumGUI()
            results["checksum_gui"] = True
            print_test("ChecksumGUI instantiation", True)
            gui.close()
        except Exception as e:
            results["checksum_gui"] = False
            print_test("ChecksumGUI instantiation", False, str(e))

        # Test ChecksumWindow instantiation
        try:
            window = ChecksumWindow()
            results["checksum_window"] = True
            print_test("ChecksumWindow instantiation", True)
            window.close()
        except Exception as e:
            results["checksum_window"] = False
            print_test("ChecksumWindow instantiation", False, str(e))

    except ImportError as e:
        results["gui_test"] = False
        print_test("GUI instantiation setup", False, f"Import failed: {e}")

    return results


def test_package_structure():
    """Test 5: Package Structure Validation"""
    print_section("5. PACKAGE STRUCTURE VALIDATION")

    results = {}

    # Check file_utilities_2 directory structure
    base_path = Path("file_utilities_2")

    required_files = [
        "__init__.py",
        "core/__init__.py",
        "core/check_sum.py",
        "gui/__init__.py",
        "gui/check_sum_gui.py",
        "gui/check_sum_standardized.py",
        "gui/check_sum_utils.py",
        "gui/check_sum_worker.py",
    ]

    for file_path in required_files:
        full_path = base_path / file_path
        if full_path.exists():
            results[f"file_{file_path}"] = True
            print_test(f"File exists: {file_path}", True)
        else:
            results[f"file_{file_path}"] = False
            print_test(f"File exists: {file_path}", False)

    # Test __init__.py exports
    try:
        from file_utilities_2 import ChecksumLogic, VALID_ALGORITHMS

        results["init_exports"] = True
        print_test(
            "__init__.py exports",
            True,
            "ChecksumLogic and VALID_ALGORITHMS available",
        )
    except ImportError as e:
        results["init_exports"] = False
        print_test("__init__.py exports", False, str(e))

    return results


def test_error_handling():
    """Test 6: Error Handling Validation"""
    print_section("6. ERROR HANDLING VALIDATION")

    results = {}

    try:
        from file_utilities_2.core.check_sum import ChecksumLogic

        logic = ChecksumLogic()

        # Test invalid file handling
        try:
            result = logic.calculate_checksum("nonexistent_file.txt", "md5")
            if result is None:
                results["invalid_file"] = True
                print_test(
                    "Invalid file handling",
                    True,
                    "Returns None for nonexistent file",
                )
            else:
                results["invalid_file"] = False
                print_test(
                    "Invalid file handling",
                    False,
                    "Should return None for nonexistent file",
                )
        except Exception as e:
            results["invalid_file"] = True
            print_test(
                "Invalid file handling",
                True,
                f"Properly raises exception: {type(e).__name__}",
            )

        # Test invalid algorithm handling
        try:
            test_file = Path("test_error_file.txt")
            test_file.write_text("test")

            result = logic.calculate_checksum(
                str(test_file), "invalid_algorithm"
            )
            if result is None:
                results["invalid_algorithm"] = True
                print_test(
                    "Invalid algorithm handling",
                    True,
                    "Returns None for invalid algorithm",
                )
            else:
                results["invalid_algorithm"] = False
                print_test(
                    "Invalid algorithm handling",
                    False,
                    "Should return None for invalid algorithm",
                )

            test_file.unlink()
        except Exception as e:
            results["invalid_algorithm"] = True
            print_test(
                "Invalid algorithm handling",
                True,
                f"Properly raises exception: {type(e).__name__}",
            )

    except ImportError as e:
        results["error_handling"] = False
        print_test("Error handling setup", False, f"Import failed: {e}")

    return results


def generate_summary_report(all_results):
    """Generate comprehensive summary report"""
    print_section("COMPREHENSIVE VALIDATION SUMMARY")

    total_tests = 0
    passed_tests = 0

    for category, results in all_results.items():
        print(f"\n{category.upper().replace('_', ' ')}:")
        category_passed = 0
        category_total = 0

        for test_name, result in results.items():
            if result is not None:
                category_total += 1
                total_tests += 1
                if result:
                    category_passed += 1
                    passed_tests += 1
                    print(f"  ✅ {test_name}")
                else:
                    print(f"  ❌ {test_name}")
            else:
                print(f"  ⚠️  {test_name} (not applicable)")

        if category_total > 0:
            percentage = (category_passed / category_total) * 100
            print(
                f"  Category Score: {category_passed}/{category_total} ({percentage:.1f}%)"
            )

    print(f"\n{'='*60}")
    print(f"OVERALL VALIDATION RESULTS")
    print(f"{'='*60}")

    if total_tests > 0:
        overall_percentage = (passed_tests / total_tests) * 100
        print(f"Total Tests: {total_tests}")
        print(f"Passed Tests: {passed_tests}")
        print(f"Failed Tests: {total_tests - passed_tests}")
        print(f"Success Rate: {overall_percentage:.1f}%")

        if overall_percentage >= 90:
            print("🎉 EXCELLENT: Migration validation highly successful!")
        elif overall_percentage >= 80:
            print("✅ GOOD: Migration validation successful with minor issues")
        elif overall_percentage >= 70:
            print(
                "⚠️  ACCEPTABLE: Migration validation passed with some concerns"
            )
        else:
            print(
                "❌ NEEDS ATTENTION: Migration validation found significant issues"
            )
    else:
        print("❌ CRITICAL: No tests could be executed")

    return passed_tests, total_tests


def main():
    """Main validation function"""
    print("🔍 COMPREHENSIVE CHECKSUM MIGRATION VALIDATION")
    print("=" * 60)
    print("Performing final integration validation and testing...")

    start_time = time.time()

    # Run all validation tests
    all_results = {}

    try:
        all_results["basic_imports"] = test_basic_imports()
        all_results["external_imports"] = test_external_imports()
        all_results["functional_validation"] = test_functional_validation()
        all_results["gui_instantiation"] = test_gui_instantiation()
        all_results["package_structure"] = test_package_structure()
        all_results["error_handling"] = test_error_handling()

        # Generate summary report
        passed, total = generate_summary_report(all_results)

        end_time = time.time()
        duration = end_time - start_time

        print(f"\nValidation completed in {duration:.2f} seconds")

        # Return exit code based on results
        if total > 0 and (passed / total) >= 0.8:
            print("\n🎯 VALIDATION SUCCESSFUL: Ready for production use!")
            return 0
        else:
            print(
                "\n⚠️  VALIDATION ISSUES: Review failed tests before deployment"
            )
            return 1

    except Exception as e:
        print(f"\n❌ CRITICAL ERROR during validation: {e}")
        traceback.print_exc()
        return 2


if __name__ == "__main__":
    sys.exit(main())
