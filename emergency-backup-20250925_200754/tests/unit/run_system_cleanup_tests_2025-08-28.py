#!/usr/bin/env python3
"""
Test Runner for System Cleanup Unit Tests
Created: 2025-08-28
Target: system_cleanup.py

This script runs comprehensive unit tests for system_cleanup.py with
standardized output and detailed reporting.
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def create_test_summary():
    """Create a comprehensive test execution summary."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    summary = {
        "test_execution": {
            "timestamp": timestamp,
            "date": "2025-08-28",
            "target_module": "system_cleanup.py",
            "test_file": "test_system_cleanup_2025-08-28.py",
            "test_framework": "pytest",
            "python_version": sys.version,
            "working_directory": os.getcwd(),
        },
        "test_configuration": {
            "coverage_enabled": True,
            "html_report": True,
            "json_report": True,
            "timeout": 600,
            "verbose_output": True,
            "strict_mode": True,
        },
    }

    return summary


def run_system_cleanup_tests():
    """Execute the system cleanup unit tests with comprehensive reporting."""
    print("=" * 80)
    print("SYSTEM CLEANUP UNIT TESTS EXECUTION")
    print("=" * 80)
    print(f"Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Target Module: system_cleanup.py")
    print("Test File: test_system_cleanup_2025-08-28.py")
    print("=" * 80)

    # Create test summary
    summary = create_test_summary()

    # Save initial summary
    summary_file = "result_system_cleanup_execution_summary_2025-08-28.json"
    with open(summary_file, "w") as f:
        json.dump(summary, f, indent=2)

    # Construct pytest command with all options
    pytest_cmd = [
        sys.executable,
        "-m",
        "pytest",
        "test_system_cleanup_2025-08-28.py",
        "-c",
        "system_cleanup_pytest.ini",
        "--verbose",
        "--tb=long",
        "--color=yes",
        "--durations=10",
        "--html=result_system_cleanup_report_2025-08-28.html",
        "--self-contained-html",
        "--json-report",
        "--json-report-file=result_system_cleanup_json_2025-08-28.json",
        "--cov=../../src/utilities/system/system_cleanup",
        "--cov-report=html:result_system_cleanup_coverage_2025-08-28",
        "--cov-report=json:result_system_cleanup_coverage_2025-08-28.json",
        "--cov-report=term-missing",
        "--cov-branch",
    ]

    print("\nExecuting pytest command:")
    print(" ".join(pytest_cmd))
    print("\n" + "=" * 80)

    # Execute tests
    try:
        result = subprocess.run(
            pytest_cmd, capture_output=False, text=True, cwd=os.getcwd()
        )

        # Update summary with results
        summary["test_results"] = {
            "exit_code": result.returncode,
            "execution_completed": True,
            "completion_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        # Determine test status
        if result.returncode == 0:
            status = "PASSED"
            print(f"\n{'='*80}")
            print("✅ ALL TESTS PASSED SUCCESSFULLY!")
        elif result.returncode == 1:
            status = "FAILED"
            print(f"\n{'='*80}")
            print("❌ SOME TESTS FAILED")
        else:
            status = "ERROR"
            print(f"\n{'='*80}")
            print(f"⚠️  TEST EXECUTION ERROR (Exit Code: {result.returncode})")

        summary["test_results"]["status"] = status

        # Save final summary
        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2)

        print(f"Test execution completed with status: {status}")
        print(f"Detailed results saved to: {summary_file}")
        print("=" * 80)

        return result.returncode

    except Exception as e:
        print(f"\n❌ Error executing tests: {e}")
        summary["test_results"] = {
            "exit_code": -1,
            "execution_completed": False,
            "error": str(e),
            "completion_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2)

        return -1


def display_test_files():
    """Display information about generated test files."""
    print("\n" + "=" * 80)
    print("GENERATED TEST FILES AND REPORTS")
    print("=" * 80)

    expected_files = [
        "test_system_cleanup_2025-08-28.py",
        "system_cleanup_pytest.ini",
        "result_system_cleanup_report_2025-08-28.html",
        "result_system_cleanup_json_2025-08-28.json",
        "result_system_cleanup_coverage_2025-08-28.json",
        "result_system_cleanup_execution_summary_2025-08-28.json",
    ]

    for filename in expected_files:
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print(f"✅ {filename} ({size} bytes)")
        else:
            print(f"❌ {filename} (not found)")

    # Check for coverage HTML directory
    coverage_dir = "result_system_cleanup_coverage_2025-08-28"
    if os.path.exists(coverage_dir):
        print(f"✅ {coverage_dir}/ (coverage HTML directory)")
    else:
        print(f"❌ {coverage_dir}/ (not found)")

    print("=" * 80)


def main():
    """Main execution function."""
    # Ensure we're in the correct directory
    os.chdir(Path(__file__).parent)

    print("Starting System Cleanup Unit Tests...")
    print(f"Working Directory: {os.getcwd()}")

    # Run the tests
    exit_code = run_system_cleanup_tests()

    # Display file information
    display_test_files()

    # Final status
    print(f"\nTest execution finished with exit code: {exit_code}")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
