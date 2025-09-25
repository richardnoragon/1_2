#!/usr/bin/env python3
"""
Test Runner for Network Transfer Module

Script: run_network_transfer_tests_2025-08-24.py
Target: test_network_transfer_2025-08-24.py
Created: 2025-08-24

This script executes comprehensive unit tests for the Network Transfer module
with proper pytest configuration, coverage reporting, and result generation.

Features:
- Configures test environment
- Executes tests with coverage
- Generates HTML and JSON reports
- Creates execution summary
- Handles dependencies and imports
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# Test configuration
TEST_TARGET = "network_transfer"
TEST_DATE = "2025-08-24"
TEST_FILE = f"test_{TEST_TARGET}_{TEST_DATE}.py"
COVERAGE_TARGET = "src.tools.network.network_transfer"

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
UNIT_TESTS_DIR = SCRIPT_DIR
RESULTS_DIR = UNIT_TESTS_DIR


def setup_environment():
    """Set up the test environment."""
    print("Setting up test environment...")

    # Add project root to Python path
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))

    # Change to project root directory
    os.chdir(PROJECT_ROOT)

    print(f"✓ Working directory: {os.getcwd()}")
    print(f"✓ Python path includes: {PROJECT_ROOT}")


def check_dependencies():
    """Check if required dependencies are available."""
    print("Checking dependencies...")

    required_packages = [
        "pytest",
        "pytest-cov",
        "pytest-html",
        "pytest-json-report",
        "PyQt5",
        "cryptography",
    ]

    missing_packages = []

    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✓ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"✗ {package} (missing)")

    if missing_packages:
        print(f"\nWarning: Missing packages: {', '.join(missing_packages)}")
        print("Some tests may be skipped.")
    else:
        print("✓ All dependencies available")

    return len(missing_packages) == 0


def run_tests():
    """Execute the test suite with comprehensive coverage and reporting."""
    print(f"\nExecuting tests for {TEST_TARGET}...")

    # Test execution timestamp
    start_time = datetime.now()

    # Define output files
    html_report = RESULTS_DIR / f"result_{TEST_TARGET}_{TEST_DATE}.html"
    json_report = RESULTS_DIR / f"result_{TEST_TARGET}_{TEST_DATE}.json"
    coverage_html = RESULTS_DIR / f"result_{TEST_TARGET}_coverage_{TEST_DATE}"
    coverage_json = (
        RESULTS_DIR / f"result_{TEST_TARGET}_coverage_{TEST_DATE}.json"
    )
    junit_xml = RESULTS_DIR / f"result_{TEST_TARGET}_{TEST_DATE}_junit.xml"
    summary_file = (
        RESULTS_DIR / f"result_{TEST_TARGET}_execution_summary_{TEST_DATE}.txt"
    )

    # Pytest command with comprehensive reporting
    pytest_cmd = [
        sys.executable,
        "-m",
        "pytest",
        str(UNIT_TESTS_DIR / TEST_FILE),
        "-v",
        "--tb=short",
        "--strict-markers",
        "--disable-warnings",
        f"--cov={COVERAGE_TARGET}",
        "--cov-report=html:" + str(coverage_html),
        "--cov-report=json:" + str(coverage_json),
        "--cov-report=term-missing",
        "--cov-fail-under=80",
        "--html=" + str(html_report),
        "--self-contained-html",
        "--json-report",
        "--json-report-file=" + str(json_report),
        "--junit-xml=" + str(junit_xml),
        "--maxfail=5",
        "--durations=10",
    ]

    print(f"Running command: {' '.join(pytest_cmd)}")
    print(f"Test file: {UNIT_TESTS_DIR / TEST_FILE}")

    try:
        # Run pytest
        result = subprocess.run(
            pytest_cmd, capture_output=True, text=True, cwd=PROJECT_ROOT
        )

        end_time = datetime.now()
        duration = end_time - start_time

        # Create execution summary
        create_execution_summary(
            result,
            start_time,
            end_time,
            duration,
            summary_file,
            html_report,
            json_report,
            coverage_html,
        )

        print(f"\n{'='*60}")
        print("TEST EXECUTION COMPLETED")
        print(f"{'='*60}")
        print(f"Duration: {duration}")
        print(f"Exit code: {result.returncode}")
        print(f"Summary: {summary_file}")
        print(f"HTML Report: {html_report}")
        print(f"JSON Report: {json_report}")
        print(f"Coverage Report: {coverage_html}/index.html")

        return result.returncode == 0

    except Exception as e:
        print(f"Error running tests: {e}")
        return False


def create_execution_summary(
    result,
    start_time,
    end_time,
    duration,
    summary_file,
    html_report,
    json_report,
    coverage_html,
):
    """Create detailed execution summary."""

    # Parse JSON report for detailed statistics
    test_stats = parse_json_report(json_report)

    summary_content = f"""
NETWORK TRANSFER MODULE - UNIT TEST EXECUTION SUMMARY
=====================================================

Test Execution Details:
----------------------
Target Module: {COVERAGE_TARGET}
Test File: {TEST_FILE}
Execution Date: {TEST_DATE}
Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}
End Time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}
Duration: {duration}
Exit Code: {result.returncode}

Test Results:
------------
{format_test_results(test_stats, result)}

Coverage Information:
-------------------
{format_coverage_info(coverage_html)}

Output Files Generated:
----------------------
- HTML Report: {html_report.name}
- JSON Report: {json_report.name}
- Coverage HTML: {coverage_html.name}/index.html
- Coverage JSON: {coverage_html.name}.json
- JUnit XML: result_{TEST_TARGET}_{TEST_DATE}_junit.xml
- Execution Summary: {summary_file.name}

Standard Output:
---------------
{result.stdout}

Standard Error:
--------------
{result.stderr}

Test Categories Covered:
----------------------
✓ SecurityManager Class Tests
  - Key generation and management
  - Encryption/decryption (AES-GCM and fallback)
  - Authentication token verification
  - Error handling and edge cases

✓ TransferProtocol Class Tests
  - Message creation and parsing
  - Size validation and limits
  - Protocol constants verification
  - Unicode support and edge cases

✓ PathSecurity Class Tests
  - Path sanitization and validation
  - Security checks against traversal attacks
  - File validation and size limits
  - Extension filtering and permissions

✓ TransferServer Class Tests
  - Server initialization and configuration
  - Client connection handling
  - Message processing for all types
  - Signal emission and error handling

✓ TransferClient Class Tests
  - Connection establishment
  - File transfer operations
  - Configuration transfer
  - Collection transfer and progress tracking

✓ NetworkTransferGUI Class Tests
  - GUI initialization and components
  - File selection and validation
  - Security checks and validation
  - Transfer management and history

✓ Integration Tests
  - End-to-end transfer scenarios
  - Security validation workflows
  - Protocol message handling
  - Error recovery and edge cases

Security Focus Areas:
-------------------
✓ Path traversal prevention
✓ Input validation and sanitization
✓ Encryption security (AES-GCM preferred)
✓ Network security (localhost binding)
✓ File system security and permissions
✓ Configuration data sanitization

Summary:
--------
{get_test_summary(result.returncode, test_stats)}

Next Steps:
----------
1. Review any failed tests in HTML report
2. Check coverage gaps in coverage report
3. Address any security vulnerabilities found
4. Update documentation if needed
5. Integrate tests into CI/CD pipeline

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

    try:
        summary_file.write_text(summary_content, encoding="utf-8")
        print(f"✓ Execution summary created: {summary_file}")
    except Exception as e:
        print(f"✗ Failed to create execution summary: {e}")


def parse_json_report(json_report_path):
    """Parse JSON test report for statistics."""
    try:
        if json_report_path.exists():
            with open(json_report_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("summary", {})
    except Exception as e:
        print(f"Warning: Could not parse JSON report: {e}")

    return {}


def format_test_results(test_stats, result):
    """Format test results section."""
    if not test_stats:
        return f"Exit Code: {result.returncode}\nDetailed statistics not available."

    total = test_stats.get("total", 0)
    passed = test_stats.get("passed", 0)
    failed = test_stats.get("failed", 0)
    skipped = test_stats.get("skipped", 0)
    errors = test_stats.get("error", 0)

    success_rate = (passed / total * 100) if total > 0 else 0

    return f"""Total Tests: {total}
Passed: {passed}
Failed: {failed}
Skipped: {skipped}
Errors: {errors}
Success Rate: {success_rate:.1f}%"""


def format_coverage_info(coverage_html_dir):
    """Format coverage information."""
    coverage_json = Path(str(coverage_html_dir) + ".json")

    if coverage_json.exists():
        try:
            with open(coverage_json, "r") as f:
                coverage_data = json.load(f)
                total_coverage = coverage_data.get("totals", {}).get(
                    "percent_covered", 0
                )
                return f"Total Coverage: {total_coverage:.1f}%"
        except Exception:
            pass

    return "Coverage information will be available in HTML report"


def get_test_summary(exit_code, test_stats):
    """Get overall test summary."""
    if exit_code == 0:
        return "✓ All tests completed successfully"
    else:
        failed = test_stats.get("failed", 0)
        errors = test_stats.get("error", 0)
        if failed > 0 or errors > 0:
            return f"✗ Tests failed: {failed} failures, {errors} errors"
        else:
            return f"✗ Test execution failed with exit code {exit_code}"


def main():
    """Main execution function."""
    print("=" * 60)
    print(f"NETWORK TRANSFER MODULE UNIT TESTS - {TEST_DATE}")
    print("=" * 60)

    # Setup
    setup_environment()

    # Check dependencies
    deps_ok = check_dependencies()

    # Run tests
    success = run_tests()

    # Final status
    print(f"\n{'='*60}")
    if success:
        print("✓ TEST EXECUTION SUCCESSFUL")
    else:
        print("✗ TEST EXECUTION FAILED")

    if not deps_ok:
        print("⚠ Some dependencies were missing")

    print("=" * 60)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
