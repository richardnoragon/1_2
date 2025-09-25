#!/usr/bin/env python3
"""
Network Scanner Test Runner
Executes comprehensive unit tests with detailed reporting.
Created on 2025-08-24
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def run_network_scanner_tests():
    """Run comprehensive tests for network_scanner.py with detailed reporting."""

    # Ensure we're in the correct directory
    project_root = Path(__file__).parent.parent.parent
    os.chdir(project_root)

    # Test configuration
    test_file = "tests/unit/test_network_scanner_2025-08-24.py"
    timestamp = datetime.now().isoformat()

    # Output file paths
    html_report = "tests/unit/result_network_scanner_2025-08-24.html"
    json_report = "tests/unit/result_network_scanner_2025-08-24.json"
    coverage_html = "tests/unit/result_network_scanner_coverage_2025-08-24"
    coverage_json = (
        "tests/unit/result_network_scanner_coverage_2025-08-24.json"
    )
    text_report = "tests/unit/result_network_scanner_2025-08-24.txt"

    print(f"=== Network Scanner Test Execution ===")
    print(f"Timestamp: {timestamp}")
    print(f"Test File: {test_file}")
    print(f"Output Directory: tests/unit/")
    print("=" * 50)

    # Pytest command with comprehensive reporting
    pytest_cmd = [
        sys.executable,
        "-m",
        "pytest",
        test_file,
        "-v",
        "--tb=short",
        f"--html={html_report}",
        "--self-contained-html",
        "--json-report",
        f"--json-report-file={json_report}",
        "--cov=src.utilities.network.network_scanner",
        f"--cov-report=html:{coverage_html}",
        "--cov-report=term-missing",
        f"--cov-report=json:{coverage_json}",
        "--cov-fail-under=80",
        "--durations=10",
        "--strict-markers",
        "-x",  # Stop on first failure for detailed debugging
    ]

    try:
        # Run tests and capture output
        print("Running pytest with comprehensive reporting...")
        result = subprocess.run(
            pytest_cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
        )

        # Write detailed text report
        with open(text_report, "w", encoding="utf-8") as f:
            f.write(f"Network Scanner Test Execution Report\n")
            f.write(f"Generated: {timestamp}\n")
            f.write("=" * 60 + "\n\n")

            f.write("COMMAND EXECUTED:\n")
            f.write(" ".join(pytest_cmd) + "\n\n")

            f.write("RETURN CODE:\n")
            f.write(f"{result.returncode}\n\n")

            f.write("STDOUT OUTPUT:\n")
            f.write(result.stdout + "\n\n")

            if result.stderr:
                f.write("STDERR OUTPUT:\n")
                f.write(result.stderr + "\n\n")

            # Test summary
            f.write("TEST EXECUTION SUMMARY:\n")
            f.write(f"Exit Code: {result.returncode}\n")
            if result.returncode == 0:
                f.write("Status: ALL TESTS PASSED ✓\n")
            else:
                f.write("Status: TESTS FAILED ✗\n")

            f.write(f"Execution Time: {datetime.now().isoformat()}\n")

        # Display results
        print("\n" + "=" * 50)
        print("TEST EXECUTION RESULTS:")
        print("=" * 50)
        print(result.stdout)

        if result.stderr:
            print("\nERRORS/WARNINGS:")
            print(result.stderr)

        # Process JSON report if available
        if os.path.exists(json_report):
            try:
                with open(json_report, "r") as f:
                    json_data = json.load(f)

                print(f"\nTEST SUMMARY:")
                print(
                    f"Total Tests: {json_data.get('summary', {}).get('total', 'N/A')}"
                )
                print(
                    f"Passed: {json_data.get('summary', {}).get('passed', 'N/A')}"
                )
                print(
                    f"Failed: {json_data.get('summary', {}).get('failed', 'N/A')}"
                )
                print(f"Duration: {json_data.get('duration', 'N/A')} seconds")

            except json.JSONDecodeError:
                print("Warning: Could not parse JSON report")

        # Report file locations
        print(f"\nREPORT FILES GENERATED:")
        print(f"HTML Report: {html_report}")
        print(f"JSON Report: {json_report}")
        print(f"Text Report: {text_report}")
        print(f"Coverage HTML: {coverage_html}/index.html")
        print(f"Coverage JSON: {coverage_json}")

        return result.returncode == 0

    except subprocess.TimeoutExpired:
        print("ERROR: Test execution timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"ERROR: Test execution failed: {e}")
        return False


def install_test_dependencies():
    """Install required test dependencies."""
    print("Installing test dependencies...")

    requirements_file = "tests/unit/test_requirements_2025-08-24.txt"

    if not os.path.exists(requirements_file):
        print(f"Warning: Requirements file not found: {requirements_file}")
        return False

    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", requirements_file],
            check=True,
        )
        print("Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies: {e}")
        return False


def main():
    """Main execution function."""
    print("Network Scanner Test Suite - 2025-08-24")
    print("Comprehensive Unit Testing with Detailed Reporting")
    print("=" * 60)

    # Check if dependencies should be installed
    if len(sys.argv) > 1 and sys.argv[1] == "--install-deps":
        if not install_test_dependencies():
            sys.exit(1)
        print()

    # Run tests
    success = run_network_scanner_tests()

    if success:
        print("\n✓ All tests completed successfully!")
        sys.exit(0)
    else:
        print("\n✗ Test execution failed or tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
