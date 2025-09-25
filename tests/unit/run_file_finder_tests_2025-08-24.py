#!/usr/bin/env python3
"""
Test Runner for file_finder.py Unit Tests
Generated: 2025-08-24

This script runs comprehensive unit tests for the file_finder module
and generates detailed HTML and JSON reports.
"""

import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path


def main():
    """Run the test suite with comprehensive reporting."""
    # Test configuration
    test_dir = Path(__file__).parent
    project_root = test_dir.parent.parent
    test_file = test_dir / "test_file_finder_2025-08-24.py"
    requirements_file = test_dir / "requirements_file_finder_2025-08-24.txt"

    # Timestamp for report naming
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Report file names
    html_report = test_dir / f"result_file_finder_html_report_{timestamp}.html"
    json_report = test_dir / f"result_file_finder_json_report_{timestamp}.json"
    coverage_report = (
        test_dir / f"result_file_finder_coverage_report_{timestamp}.html"
    )
    text_output = test_dir / f"result_file_finder_test_output_{timestamp}.txt"

    print(
        f"File Finder Test Runner - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    print("=" * 60)

    # Add project root to Python path
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    # Check if test file exists
    if not test_file.exists():
        print(f"ERROR: Test file not found: {test_file}")
        return 1

    # Install requirements if file exists
    if requirements_file.exists():
        print("Installing test requirements...")
        try:
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "-r",
                    str(requirements_file),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            print("✓ Requirements installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"WARNING: Failed to install requirements: {e}")
            print("Continuing with existing packages...")

    # Build pytest command
    pytest_cmd = [
        sys.executable,
        "-m",
        "pytest",
        str(test_file),
        "-v",
        "--tb=short",
        f"--html={html_report}",
        "--self-contained-html",
        f"--json-report={json_report}",
        f"--cov=src.utilities.file_management.file_finder",
        f"--cov-report=html:{coverage_report}",
        "--cov-report=term-missing",
        "-x",  # Stop on first failure for faster debugging
    ]

    print(f"\nRunning tests on: {test_file.name}")
    print(f"Test command: {' '.join(pytest_cmd[2:])}")
    print("-" * 60)

    # Run the tests and capture output
    try:
        result = subprocess.run(
            pytest_cmd,
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
        )

        # Save output to file
        with open(text_output, "w", encoding="utf-8") as f:
            f.write(f"File Finder Test Execution Report\n")
            f.write(
                f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            )
            f.write(f"Test File: {test_file.name}\n")
            f.write("=" * 60 + "\n\n")
            f.write("STDOUT:\n")
            f.write(result.stdout)
            f.write("\n\nSTDERR:\n")
            f.write(result.stderr)
            f.write(f"\n\nReturn Code: {result.returncode}\n")

        # Display results
        print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)

        # Print summary
        print("\n" + "=" * 60)
        print("TEST EXECUTION SUMMARY")
        print("=" * 60)
        print(f"Return Code: {result.returncode}")
        print(f"Text Output: {text_output}")

        if html_report.exists():
            print(f"HTML Report: {html_report}")
        if json_report.exists():
            print(f"JSON Report: {json_report}")
        if coverage_report.exists():
            print(f"Coverage Report: {coverage_report}")

        # Parse basic results from output
        lines = result.stdout.split("\n")
        for line in lines:
            if "passed" in line and "failed" in line:
                print(f"Result Summary: {line.strip()}")
                break
            elif line.startswith("=") and (
                "passed" in line or "failed" in line
            ):
                print(f"Result Summary: {line.strip()}")
                break

        return result.returncode

    except subprocess.TimeoutExpired:
        print("ERROR: Test execution timed out after 5 minutes")
        return 1
    except Exception as e:
        print(f"ERROR: Failed to execute tests: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
