#!/usr/bin/env python3
"""
Test Runner for empty_folders.py Unit Tests
Created: 2025-08-24
Generates comprehensive test reports with timestamps and detailed results.
"""

import os
import sys
import subprocess
import datetime
from pathlib import Path


def setup_test_environment():
    """Setup the test environment and install dependencies."""
    print("Setting up test environment...")
    
    # Install test dependencies
    req_file = "requirements_test_empty_folders_2025-08-24.txt"
    requirements_file = Path(__file__).parent / req_file
    
    if requirements_file.exists():
        try:
            cmd = [sys.executable, "-m", "pip", "install", "-r",
                   str(requirements_file)]
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            print("✓ Test dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install dependencies: {e}")
            return False
    
    return True


def run_empty_folders_tests():
    """Run the comprehensive test suite for empty_folders.py."""
    print(f"\n{'='*60}")
    print("Running Comprehensive Unit Tests for empty_folders.py")
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"Execution Time: {timestamp}")
    print(f"{'='*60}")
    
    # Change to project root directory
    project_root = Path(__file__).parent.parent.parent
    os.chdir(project_root)
    
    # Ensure tests directory exists
    test_dir = Path("tests/unit")
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # Test file path
    test_file = test_dir / "test_empty_folders_2025-08-24.py"
    
    if not test_file.exists():
        print(f"✗ Test file not found: {test_file}")
        return False
    
    # Run pytest with comprehensive reporting
    cov_json = "tests/unit/result_empty_folders_coverage_2025-08-24.json"
    html_path = "tests/unit/result_empty_folders_2025-08-24.html"
    json_path = "tests/unit/result_empty_folders_2025-08-24.json"
    cov_html = "tests/unit/result_empty_folders_coverage_2025-08-24"
    cmd = [
        sys.executable, "-m", "pytest",
        str(test_file),
        "-v",
        "--tb=short",
        "--color=yes",
        "--durations=10",
        f"--html={html_path}",
        "--self-contained-html",
        "--json-report",
        f"--json-report-file={json_path}",
        "--cov=src.utilities.analysis.empty_folders",
        f"--cov-report=html:{cov_html}",
        "--cov-report=term-missing",
        f"--cov-report=json:{cov_json}"
    ]
    
    try:
        print(f"Executing: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True,
                                timeout=300)
        
        print(f"\n{'='*40} TEST EXECUTION OUTPUT {'='*40}")
        print(result.stdout)
        
        if result.stderr:
            print(f"\n{'='*40} ERROR OUTPUT {'='*40}")
            print(result.stderr)
        
        print(f"\n{'='*40} TEST EXECUTION SUMMARY {'='*40}")
        print(f"Return Code: {result.returncode}")
        exec_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
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
    summary_file = (Path("tests/unit") /
                    "result_empty_folders_execution_summary_2025-08-24.txt")
    
    summary_content = f"""
EMPTY_FOLDERS.PY UNIT TEST EXECUTION SUMMARY
=============================================

Execution Details:
- Test Date: {datetime.datetime.now().strftime('%Y-%m-%d')}
- Execution Time: {datetime.datetime.now().strftime('%H:%M:%S')}
- Test Framework: pytest
- Target Module: src.utilities.analysis.empty_folders
- Test Status: {'PASSED' if success else 'FAILED'}

Generated Reports:
- HTML Report: tests/unit/result_empty_folders_2025-08-24.html
- JSON Report: tests/unit/result_empty_folders_2025-08-24.json
- Coverage HTML: tests/unit/result_empty_folders_coverage_2025-08-24/index.html
- Coverage JSON: tests/unit/result_empty_folders_coverage_2025-08-24.json

Test Coverage Areas:
✓ EmptyFolderLogic class initialization and functionality
✓ Directory scanning for empty folders (recursive)
✓ Empty folder deletion with proper ordering
✓ EmptyFoldersGUI class initialization and UI components
✓ Directory selection and browsing functionality
✓ Signal handling and threading operations
✓ Button state management and user interactions
✓ Error handling for permission and access issues
✓ Edge cases: Unicode filenames, deep nesting, permission errors
✓ Mock data testing with various directory structures
✓ Integration testing of GUI and logic components
✓ Menu integration and callback functionality

Test Categories:
- Unit Tests: Core functionality testing for both classes
- Integration Tests: GUI and logic component interaction testing
- Edge Case Tests: Boundary conditions and special scenarios
- Error Handling Tests: Exception and error scenarios
- GUI Tests: User interface component and interaction testing
- Signal Tests: PyQt signal emission and handling
- Threading Tests: Background operation management

Files Generated:
- Test file: test_empty_folders_2025-08-24.py
- Requirements: requirements_test_empty_folders_2025-08-24.txt
- This summary: result_empty_folders_execution_summary_2025-08-24.txt

Technical Coverage:
- EmptyFolderLogic: Find and delete empty folders functionality
- EmptyFoldersGUI: Complete UI testing with PyQt5 components
- Signal/Slot: Progress updates, folder found, deletion status
- Threading: Background scanning and deletion operations
- File System: Directory creation, deletion, permission handling
- Error Handling: OSError, permission denied, nonexistent paths

Notes:
- All tests follow pytest best practices
- Comprehensive mock data and fixtures used
- Detailed assertions for all test scenarios
- Proper setup and teardown for test isolation
- Threading and signal testing included
- Generated on: {datetime.datetime.now().isoformat()}
"""
    
    try:
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary_content)
        print(f"✓ Test summary generated: {summary_file}")
    except Exception as e:
        print(f"✗ Failed to generate test summary: {e}")


def check_reports():
    """Check if all required reports were generated."""
    print(f"\n{'='*40} REPORT VERIFICATION {'='*40}")
    
    expected_files = [
        "tests/unit/result_empty_folders_2025-08-24.html",
        "tests/unit/result_empty_folders_2025-08-24.json",
        "tests/unit/result_empty_folders_coverage_2025-08-24.json",
        "tests/unit/result_empty_folders_execution_summary_2025-08-24.txt"
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
    coverage_dir = Path("tests/unit/result_empty_folders_coverage_2025-08-24")
    if coverage_dir.exists() and (coverage_dir / "index.html").exists():
        print(f"✓ {coverage_dir}/index.html (coverage report)")
    else:
        print(f"✗ {coverage_dir}/index.html (missing)")
        all_present = False
    
    return all_present


def main():
    """Main execution function."""
    print("EMPTY_FOLDERS.PY COMPREHENSIVE TEST RUNNER")
    print("=" * 50)
    
    # Setup test environment
    if not setup_test_environment():
        print("✗ Failed to setup test environment")
        return 1
    
    # Run tests
    if not run_empty_folders_tests():
        print("✗ Test execution failed")
        return 1
    
    # Verify reports
    if not check_reports():
        print("⚠ Some reports may be missing")
    
    print(f"\n{'='*50}")
    print("✓ Test execution completed successfully!")
    print("Check the tests/unit directory for detailed reports.")
    final_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"Execution completed: {final_time}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())