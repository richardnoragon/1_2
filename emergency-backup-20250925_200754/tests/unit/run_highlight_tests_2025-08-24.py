#!/usr/bin/env python3
"""
Test runner script for highlight.py comprehensive unit tests
Generated on August 24, 2025

This script executes the complete test suite for highlight.py and generates
standardized HTML and JSON reports with detailed coverage information.
"""

import datetime
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


def setup_test_environment():
    """Setup the test environment and directories"""
    print("Setting up test environment...")

    # Get the current directory
    current_dir = Path(__file__).parent

    # Create necessary directories
    directories = ["logs", "output", "result_highlight_coverage_2025-08-24"]

    for directory in directories:
        dir_path = current_dir / directory
        dir_path.mkdir(exist_ok=True)
        print(f"Created directory: {dir_path}")

    # Set environment variables
    os.environ["PYTHONPATH"] = str(current_dir.parent.parent / "src")

    return current_dir


def run_tests(test_dir):
    """Execute the pytest test suite"""
    print("Starting test execution...")

    # Change to test directory
    os.chdir(test_dir)

    # Define pytest command with all required options
    pytest_cmd = [
        sys.executable,
        "-m",
        "pytest",
        "-c",
        "pytest_highlight_2025-08-24.ini",
        "test_highlight_2025-08-24.py",
        "--verbose",
        "--tb=short",
        "--html=result_highlight_2025-08-24.html",
        "--self-contained-html",
        "--json-report",
        "--json-report-file=result_highlight_2025-08-24.json",
        "--cov=highlight",
        "--cov-report=html:result_highlight_coverage_2025-08-24",
        "--cov-report=json:result_highlight_coverage_2025-08-24.json",
        "--cov-report=term-missing",
        "--cov-branch",
        "--junit-xml=result_highlight_2025-08-24_junit.xml",
        "--disable-warnings",
    ]

    print(f"Executing command: {' '.join(pytest_cmd)}")

    # Execute pytest
    try:
        result = subprocess.run(
            pytest_cmd,
            capture_output=True,
            text=True,
            timeout=600,  # 10 minute timeout
        )

        return result
    except subprocess.TimeoutExpired:
        print("ERROR: Test execution timed out after 10 minutes")
        return None
    except Exception as e:
        print(f"ERROR: Test execution failed: {e}")
        return None


def generate_execution_summary(test_dir, test_result):
    """Generate a comprehensive execution summary"""
    print("Generating execution summary...")

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    summary_lines = [
        "=" * 80,
        "HIGHLIGHT.PY COMPREHENSIVE UNIT TEST EXECUTION SUMMARY",
        "=" * 80,
        f"Execution Date: {timestamp}",
        f"Test Suite: highlight.py unit tests",
        f"Configuration: pytest_highlight_2025-08-24.ini",
        f"Test File: test_highlight_2025-08-24.py",
        "",
        "EXECUTION DETAILS:",
        "-" * 40,
    ]

    if test_result:
        summary_lines.extend(
            [
                f"Return Code: {test_result.returncode}",
                f"Execution Status: {'PASSED' if test_result.returncode == 0 else 'FAILED'}",
                "",
                "STDOUT OUTPUT:",
                "-" * 40,
                test_result.stdout,
                "",
                "STDERR OUTPUT:",
                "-" * 40,
                (
                    test_result.stderr
                    if test_result.stderr
                    else "No errors reported"
                ),
                "",
            ]
        )
    else:
        summary_lines.extend(
            [
                "Return Code: ERROR",
                "Execution Status: TIMEOUT/ERROR",
                "Details: Test execution failed or timed out",
                "",
            ]
        )

    # Add coverage information if available
    coverage_json_path = test_dir / "result_highlight_coverage_2025-08-24.json"
    if coverage_json_path.exists():
        try:
            with open(coverage_json_path, "r") as f:
                coverage_data = json.load(f)

            summary_lines.extend(
                [
                    "COVERAGE INFORMATION:",
                    "-" * 40,
                    f"Total Coverage: {coverage_data.get('totals', {}).get('percent_covered', 'N/A')}%",
                    f"Lines Covered: {coverage_data.get('totals', {}).get('covered_lines', 'N/A')}",
                    f"Lines Missing: {coverage_data.get('totals', {}).get('missing_lines', 'N/A')}",
                    f"Total Lines: {coverage_data.get('totals', {}).get('num_statements', 'N/A')}",
                    "",
                ]
            )
        except Exception as e:
            summary_lines.extend(
                [
                    "COVERAGE INFORMATION:",
                    "-" * 40,
                    f"Error reading coverage data: {e}",
                    "",
                ]
            )

    # Add test results if JSON report is available
    json_report_path = test_dir / "result_highlight_2025-08-24.json"
    if json_report_path.exists():
        try:
            with open(json_report_path, "r") as f:
                test_data = json.load(f)

            summary_lines.extend(
                [
                    "TEST RESULTS SUMMARY:",
                    "-" * 40,
                    f"Total Tests: {test_data.get('summary', {}).get('total', 'N/A')}",
                    f"Passed: {test_data.get('summary', {}).get('passed', 'N/A')}",
                    f"Failed: {test_data.get('summary', {}).get('failed', 'N/A')}",
                    f"Skipped: {test_data.get('summary', {}).get('skipped', 'N/A')}",
                    f"Duration: {test_data.get('duration', 'N/A')} seconds",
                    "",
                ]
            )

            # Add failed test details if any
            if test_data.get("summary", {}).get("failed", 0) > 0:
                summary_lines.extend(["FAILED TESTS:", "-" * 40])

                for test in test_data.get("tests", []):
                    if test.get("outcome") == "failed":
                        summary_lines.append(
                            f"- {test.get('nodeid', 'Unknown test')}"
                        )
                        if test.get("call", {}).get("longrepr"):
                            summary_lines.append(
                                f"  Error: {test['call']['longrepr'][:100]}..."
                            )

                summary_lines.append("")

        except Exception as e:
            summary_lines.extend(
                [
                    "TEST RESULTS SUMMARY:",
                    "-" * 40,
                    f"Error reading test results: {e}",
                    "",
                ]
            )

    # Add file locations
    summary_lines.extend(
        [
            "GENERATED FILES:",
            "-" * 40,
            f"HTML Report: {test_dir}/result_highlight_2025-08-24.html",
            f"JSON Report: {test_dir}/result_highlight_2025-08-24.json",
            f"JUnit XML: {test_dir}/result_highlight_2025-08-24_junit.xml",
            f"Coverage HTML: {test_dir}/result_highlight_coverage_2025-08-24/index.html",
            f"Coverage JSON: {test_dir}/result_highlight_coverage_2025-08-24.json",
            f"Execution Summary: {test_dir}/result_highlight_execution_summary_2025-08-24.txt",
            "",
            "=" * 80,
            "END OF EXECUTION SUMMARY",
            "=" * 80,
        ]
    )

    # Write summary to file
    summary_path = (
        test_dir / "result_highlight_execution_summary_2025-08-24.txt"
    )
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(summary_lines))

    print(f"Execution summary written to: {summary_path}")

    # Also print key information to console
    print("\nKEY RESULTS:")
    print("-" * 40)
    if test_result:
        print(
            f"Overall Status: {'PASSED' if test_result.returncode == 0 else 'FAILED'}"
        )
    else:
        print("Overall Status: ERROR/TIMEOUT")

    if coverage_json_path.exists():
        try:
            with open(coverage_json_path, "r") as f:
                coverage_data = json.load(f)
            print(
                f"Coverage: {coverage_data.get('totals', {}).get('percent_covered', 'N/A')}%"
            )
        except:
            print("Coverage: Unable to read")

    return summary_path


def check_dependencies():
    """Check if required dependencies are available"""
    print("Checking dependencies...")

    required_packages = [
        ("pytest", "pytest"),
        ("pytest-html", "pytest_html"),
        ("pytest-json-report", "pytest_jsonreport"),
        ("pytest-cov", "pytest_cov"),
        ("PyQt5", "PyQt5"),
    ]

    missing_packages = []

    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
            print(f"✓ {package_name} is available")
        except ImportError:
            missing_packages.append(package_name)
            print(f"✗ {package_name} is missing")

    if missing_packages:
        print(
            f"\nERROR: Missing required packages: {', '.join(missing_packages)}"
        )
        print(
            "Please install them using: pip install "
            + " ".join(missing_packages)
        )
        return False

    return True


def main():
    """Main execution function"""
    print("Highlight.py Unit Test Runner")
    print("=" * 50)
    print(
        f"Started at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    print()

    # Check dependencies
    if not check_dependencies():
        sys.exit(1)

    # Setup environment
    test_dir = setup_test_environment()

    # Run tests
    test_result = run_tests(test_dir)

    # Generate summary
    summary_path = generate_execution_summary(test_dir, test_result)

    print("\n" + "=" * 50)
    print("Test execution completed!")
    print(f"Summary available at: {summary_path}")

    if test_result:
        if test_result.returncode == 0:
            print("Status: ALL TESTS PASSED ✓")
            sys.exit(0)
        else:
            print("Status: SOME TESTS FAILED ✗")
            sys.exit(1)
    else:
        print("Status: EXECUTION ERROR ✗")
        sys.exit(1)


if __name__ == "__main__":
    main()
