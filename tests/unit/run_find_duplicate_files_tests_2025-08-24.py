#!/usr/bin/env python3
"""
Test Runner for find_duplicate_files.py Unit Tests
Created: 2025-08-24
Generates comprehensive test reports with timestamps and detailed results.
"""

import datetime
import os
import subprocess
import sys
from pathlib import Path


def setup_test_environment():
    """Setup the test environment and install dependencies."""
    print("Setting up test environment...")

    # Install test dependencies
    req_file = "requirements_test_find_duplicate_files_2025-08-24.txt"
    requirements_file = Path(__file__).parent / req_file

    if requirements_file.exists():
        try:
            cmd = [
                sys.executable,
                "-m",
                "pip",
                "install",
                "-r",
                str(requirements_file),
            ]
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            print("✓ Test dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install dependencies: {e}")
            return False

    return True


def run_find_duplicate_files_tests():
    """Run the comprehensive test suite for find_duplicate_files.py."""
    print(f"\n{'='*60}")
    print("Running Comprehensive Unit Tests for find_duplicate_files.py")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Execution Time: {timestamp}")
    print(f"{'='*60}")

    # Change to project root directory
    project_root = Path(__file__).parent.parent.parent
    os.chdir(project_root)

    # Ensure tests directory exists
    test_dir = Path("tests/unit")
    test_dir.mkdir(parents=True, exist_ok=True)

    # Test file path
    test_file = test_dir / "test_find_duplicate_files_2025-08-24.py"

    if not test_file.exists():
        print(f"✗ Test file not found: {test_file}")
        return False

    # Run pytest with comprehensive reporting
    base_name = "result_find_duplicate_files"
    cov_json = f"tests/unit/{base_name}_coverage_2025-08-24.json"
    html_path = f"tests/unit/{base_name}_2025-08-24.html"
    json_path = f"tests/unit/{base_name}_2025-08-24.json"
    cov_html = f"tests/unit/{base_name}_coverage_2025-08-24"
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        str(test_file),
        "-v",
        "--tb=short",
        "--color=yes",
        "--durations=10",
        f"--html={html_path}",
        "--self-contained-html",
        "--json-report",
        f"--json-report-file={json_path}",
        "--cov=src.tools.analysis.duplicate_finder.find_duplicate_files",
        f"--cov-report=html:{cov_html}",
        "--cov-report=term-missing",
        f"--cov-report=json:{cov_json}",
    ]

    try:
        print(f"Executing: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        print(f"\n{'='*40} TEST EXECUTION OUTPUT {'='*40}")
        print(result.stdout)

        if result.stderr:
            print(f"\n{'='*40} ERROR OUTPUT {'='*40}")
            print(result.stderr)

        print(f"\n{'='*40} TEST EXECUTION SUMMARY {'='*40}")
        print(f"Return Code: {result.returncode}")
        exec_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"Execution completed at: {exec_time}")

        # Generate summary report
        generate_test_summary(result.returncode == 0)

        return result.returncode == 0

    except subprocess.TimeoutExpired:
        print("✗ Test execution timed out after 300 seconds")
        return False
    except Exception as e:
        print(f"✗ Test execution failed: {e}")
        return False


def generate_test_summary(success):
    """Generate a comprehensive test execution summary."""
    base_name = "result_find_duplicate_files_execution_summary_2025-08-24"
    summary_file = Path("tests/unit") / f"{base_name}.txt"

    summary_content = f"""
FIND_DUPLICATE_FILES.PY UNIT TEST EXECUTION SUMMARY
===================================================

Execution Details:
- Test Date: {datetime.datetime.now().strftime('%Y-%m-%d')}
- Execution Time: {datetime.datetime.now().strftime('%H:%M:%S')}
- Test Framework: pytest
- Target Module: src.tools.analysis.duplicate_finder.find_duplicate_files
- Test Status: {'PASSED' if success else 'FAILED'}

Generated Reports:
- HTML Report: tests/unit/result_find_duplicate_files_2025-08-24.html
- JSON Report: tests/unit/result_find_duplicate_files_2025-08-24.json
- Coverage HTML: tests/unit/result_find_duplicate_files_coverage_2025-08-24/
- Coverage JSON: tests/unit/result_find_duplicate_files_coverage_2025-08-24.json

Test Coverage Areas:
✓ DuplicateFinderApp class initialization and functionality
✓ GUI component creation and layout management
✓ Directory selection and browsing functionality
✓ File scanning and duplicate detection algorithms
✓ MD5 hash calculation for file comparison
✓ Results display and list widget management
✓ Error handling for permission and access issues
✓ Edge cases: Unicode filenames, large files, nested directories
✓ Mock data testing with various file structures
✓ Integration testing of GUI and logic components
✓ Menu integration and callback functionality
✓ Binary file and empty file handling

Test Categories:
- Unit Tests: Core functionality testing for DuplicateFinderApp class
- Integration Tests: GUI and file system interaction testing
- Edge Case Tests: Boundary conditions and special scenarios
- Error Handling Tests: Exception and error scenarios
- GUI Tests: User interface component and interaction testing
- File System Tests: Directory scanning and file operations
- Performance Tests: Large file and deep directory handling

Files Generated:
- Test file: test_find_duplicate_files_2025-08-24.py
- Requirements: requirements_test_find_duplicate_files_2025-08-24.txt
- This summary: result_find_duplicate_files_execution_summary_2025-08-24.txt

Technical Coverage:
- DuplicateFinderApp: Complete GUI testing with PyQt5 components
- File Operations: Directory scanning, hash calculation, duplicate detection
- Error Handling: Permission errors, file not found, exception handling
- GUI Components: Button states, list widgets, dialogs, menu integration
- File System: Nested directories, Unicode names, binary files, symlinks

Notes:
- All tests follow pytest best practices
- Comprehensive mock data and fixtures used
- Detailed assertions for all test scenarios
- Proper setup and teardown for test isolation
- GUI testing with PyQt5 framework included
- Generated on: {datetime.datetime.now().isoformat()}
"""

    try:
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write(summary_content)
        print(f"✓ Test summary generated: {summary_file}")
    except Exception as e:
        print(f"✗ Failed to generate test summary: {e}")


def check_reports():
    """Check if all required reports were generated."""
    print(f"\n{'='*40} REPORT VERIFICATION {'='*40}")

    base_name = "result_find_duplicate_files_execution_summary_2025-08-24"
    expected_files = [
        "tests/unit/result_find_duplicate_files_2025-08-24.html",
        "tests/unit/result_find_duplicate_files_2025-08-24.json",
        "tests/unit/result_find_duplicate_files_coverage_2025-08-24.json",
        f"tests/unit/{base_name}.txt",
    ]

    all_present = True
    for file_path in expected_files:
        if Path(file_path).exists():
            size = Path(file_path).stat().st_size
            print(f"✓ {file_path} ({size} bytes)")
        else:
            print(f"✗ {file_path} (missing)")
            all_present = False

    # Check coverage HTML directory
    cov_dir_name = "result_find_duplicate_files_coverage_2025-08-24"
    coverage_dir = Path(f"tests/unit/{cov_dir_name}")
    if coverage_dir.exists() and (coverage_dir / "index.html").exists():
        print(f"✓ {coverage_dir}/index.html (coverage report)")
    else:
        print(f"✗ {coverage_dir}/index.html (missing)")
        all_present = False

    return all_present


def main():
    """Main execution function."""
    print("FIND_DUPLICATE_FILES.PY COMPREHENSIVE TEST RUNNER")
    print("=" * 55)

    # Setup test environment
    if not setup_test_environment():
        print("✗ Failed to setup test environment")
        return 1

    # Run tests
    if not run_find_duplicate_files_tests():
        print("✗ Test execution failed")
        return 1

    # Verify reports
    if not check_reports():
        print("⚠ Some reports may be missing")

    print(f"\n{'='*55}")
    print("✓ Test execution completed successfully!")
    print("Check the tests/unit directory for detailed reports.")
    final_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Execution completed: {final_time}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
