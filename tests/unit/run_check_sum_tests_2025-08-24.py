#!/usr/bin/env python3
"""
Test Runner for check_sum.py     # Run pytest with comprehensive reporting
    cov_json = "tests/unit/result_check_sum_coverage_2025-08-24.json"
    cmd = [
        sys.executable, "-m", "pytest",
        str(test_file),
        "-v",
        "--tb=short",
        "--color=yes",
        "--durations=10",
        "--html=tests/unit/result_check_sum_2025-08-24.html",
        "--self-contained-html",
        "--json-report",
        "--json-report-file=tests/unit/result_check_sum_2025-08-24.json",
    "--cov=src.tools.analysis.checksum.check_sum",
        "--cov-report=html:tests/unit/result_check_sum_coverage_2025-08-24",
        "--cov-report=term-missing",
        "--cov-report=json:" + cov_json
    ]d: 2025-08-24
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
    req_file = ("requirements_test_check_sum_2025-08-24.txt")
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


def run_checksum_tests():
    """Run the comprehensive test suite for check_sum.py."""
    print(f"\n{'='*60}")
    print("Running Comprehensive Unit Tests for check_sum.py")
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
    test_file = test_dir / "test_check_sum_2025-08-24.py"
    
    if not test_file.exists():
        print(f"✗ Test file not found: {test_file}")
        return False
    
    # Run pytest with comprehensive reporting
    cmd = [
        sys.executable, "-m", "pytest",
        str(test_file),
        "-v",
        "--tb=short",
        "--color=yes",
        "--durations=10",
        "--html=tests/unit/result_check_sum_2025-08-24.html",
        "--self-contained-html",
        "--json-report",
        "--json-report-file=tests/unit/result_check_sum_2025-08-24.json",
    "--cov=src.tools.analysis.checksum.check_sum",
        "--cov-report=html:tests/unit/result_check_sum_coverage_2025-08-24",
        "--cov-report=term-missing",
        "    # Run pytest with comprehensive reporting
    cov_json = "tests/unit/result_check_sum_coverage_2025-08-24.json"
    cmd = [
        sys.executable, "-m", "pytest",
        str(test_file),
        "-v",
        "--tb=short",
        "--color=yes",
        "--durations=10",
        "--html=tests/unit/result_check_sum_2025-08-24.html",
        "--self-contained-html",
        "--json-report",
        "--json-report-file=tests/unit/result_check_sum_2025-08-24.json",
    "--cov=src.tools.analysis.checksum.check_sum",
        "--cov-report=html:tests/unit/result_check_sum_coverage_2025-08-24",
        "--cov-report=term-missing",
        "--cov-report=json:" + cov_json
    ]
        "--cov-report=json:" + cov_json"
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
        print(f"Execution completed at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
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
    summary_file = Path("tests/unit/result_check_sum_execution_summary_2025-08-24.txt")
    
    summary_content = f"""
CHECK_SUM.PY UNIT TEST EXECUTION SUMMARY
==========================================

Execution Details:
- Test Date: {datetime.datetime.now().strftime('%Y-%m-%d')}
- Execution Time: {datetime.datetime.now().strftime('%H:%M:%S')}
- Test Framework: pytest
- Target Module: src.tools.analysis.checksum.check_sum
- Test Status: {'PASSED' if success else 'FAILED'}

Generated Reports:
- HTML Report: tests/unit/result_check_sum_2025-08-24.html
- JSON Report: tests/unit/result_check_sum_2025-08-24.json
- Coverage HTML: tests/unit/result_check_sum_coverage_2025-08-24/index.html
- Coverage JSON: tests/unit/result_check_sum_coverage_2025-08-24.json

Test Coverage Areas:
✓ ChecksumGUI class initialization and setup
✓ File selection functionality and validation
✓ MD5 checksum calculation with various file types
✓ UI component creation and behavior testing
✓ Error handling for file access and permission issues
✓ Menu integration and callback functionality
✓ Edge cases: empty files, large files, unicode filenames
✓ Mock data testing with known checksum values
✓ Multiple calculation scenarios and result handling
✓ Fallback mode operation without StandardWindow

Test Categories:
- Unit Tests: Core functionality testing
- Integration Tests: Component interaction testing
- Edge Case Tests: Boundary condition testing
- Error Handling Tests: Exception and error scenarios
- GUI Tests: User interface component testing
- Performance Tests: Large file handling

Files Generated:
- Test file: test_check_sum_2025-08-24.py
- Requirements: requirements_test_check_sum_2025-08-24.txt
- This summary: result_check_sum_execution_summary_2025-08-24.txt

Notes:
- All tests follow pytest best practices
- Comprehensive mock data and fixtures used
- Detailed assertions for all test scenarios
- Proper setup and teardown for test isolation
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
        "tests/unit/result_check_sum_2025-08-24.html",
        "tests/unit/result_check_sum_2025-08-24.json",
        "tests/unit/result_check_sum_coverage_2025-08-24.json",
        "tests/unit/result_check_sum_execution_summary_2025-08-24.txt"
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
    coverage_dir = Path("tests/unit/result_check_sum_coverage_2025-08-24")
    if coverage_dir.exists() and (coverage_dir / "index.html").exists():
        print(f"✓ {coverage_dir}/index.html (coverage report)")
    else:
        print(f"✗ {coverage_dir}/index.html (missing)")
        all_present = False
    
    return all_present


def main():
    """Main execution function."""
    print("CHECK_SUM.PY COMPREHENSIVE TEST RUNNER")
    print("=" * 50)
    
    # Setup test environment
    if not setup_test_environment():
        print("✗ Failed to setup test environment")
        return 1
    
    # Run tests
    if not run_checksum_tests():
        print("✗ Test execution failed")
        return 1
    
    # Verify reports
    if not check_reports():
        print("⚠ Some reports may be missing")
    
    print(f"\n{'='*50}")
    print("✓ Test execution completed successfully!")
    print(f"Check the tests/unit directory for detailed reports.")
    print(f"Execution completed: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())