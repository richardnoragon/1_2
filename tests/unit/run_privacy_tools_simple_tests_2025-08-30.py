#!/usr/bin/env python3
"""
Test Runner for privacy_tools_simple.py Unit Tests

This script runs comprehensive unit tests for privacy_tools_simple.py
and generates detailed reports with timestamps.

Usage: python run_privacy_tools_simple_tests_2025-08-30.py
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# Test configuration
TEST_DATE = "2025-08-30"
TEST_DIR = Path(__file__).parent
PROJECT_ROOT = TEST_DIR.parent.parent
TEST_FILE = TEST_DIR / f"test_privacy_tools_simple_{TEST_DATE}.py"
PYTEST_CONFIG = TEST_DIR / f"pytest_privacy_tools_simple_{TEST_DATE}.ini"

# Result files
RESULTS = {
    "html_report": TEST_DIR
    / f"result_privacy_tools_simple_report_{TEST_DATE}.html",
    "json_report": TEST_DIR
    / f"result_privacy_tools_simple_json_{TEST_DATE}.json",
    "junit_xml": TEST_DIR
    / f"result_privacy_tools_simple_junit_{TEST_DATE}.xml",
    "coverage_html": TEST_DIR
    / f"result_privacy_tools_simple_coverage_{TEST_DATE}.html",
    "coverage_json": TEST_DIR
    / f"result_privacy_tools_simple_coverage_{TEST_DATE}.json",
    "pytest_log": TEST_DIR
    / f"result_privacy_tools_simple_pytest_{TEST_DATE}.log",
    "execution_summary": TEST_DIR
    / f"result_privacy_tools_simple_execution_summary_{TEST_DATE}.json",
}


def check_dependencies():
    """Check if required test dependencies are installed."""
    required_packages = [
        "pytest",
        "pytest-cov",
        "pytest-html",
        "pytest-json-report",
        "pytest-timeout",
        "pytest-mock",
        "pytest-qt",
        "PyQt5",
    ]

    missing_packages = []

    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print(
            f"Install with: pip install -r {TEST_DIR / f'requirements_test_privacy_tools_simple_{TEST_DATE}.txt'}"
        )
        return False

    print("✅ All required test dependencies are installed")
    return True


def run_tests():
    """Run the test suite with comprehensive reporting."""
    print(f"\n🧪 Starting Privacy Tools Simple Tests - {TEST_DATE}")
    print(f"📁 Test Directory: {TEST_DIR}")
    print(f"📄 Test File: {TEST_FILE}")
    print(f"⚙️ Config File: {PYTEST_CONFIG}")

    # Build pytest command
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        str(TEST_FILE),
        "-c",
        str(PYTEST_CONFIG),
        "--verbose",
        "--tb=short",
        f"--cov=src.utilities.privacy.privacy_tools_simple",
        f'--cov-report=html:{RESULTS["coverage_html"]}',
        f'--cov-report=json:{RESULTS["coverage_json"]}',
        "--cov-report=term-missing",
        f'--html={RESULTS["html_report"]}',
        "--self-contained-html",
        f'--junitxml={RESULTS["junit_xml"]}',
        "--json-report",
        f'--json-report-file={RESULTS["json_report"]}',
        "--timeout=300",
    ]

    # Add environment variables
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT)

    print(f"\n🚀 Executing command: {' '.join(cmd)}")

    # Record start time
    start_time = time.time()
    start_datetime = datetime.now()

    try:
        # Run tests
        result = subprocess.run(
            cmd,
            cwd=PROJECT_ROOT,
            env=env,
            capture_output=True,
            text=True,
            timeout=600,  # 10 minute timeout
        )

        end_time = time.time()
        end_datetime = datetime.now()
        execution_time = end_time - start_time

        # Generate execution summary
        summary = {
            "test_session": {
                "date": TEST_DATE,
                "start_time": start_datetime.isoformat(),
                "end_time": end_datetime.isoformat(),
                "execution_time_seconds": round(execution_time, 2),
                "execution_time_formatted": f"{execution_time:.2f} seconds",
            },
            "test_execution": {
                "return_code": result.returncode,
                "success": result.returncode == 0,
                "command": " ".join(cmd),
                "working_directory": str(PROJECT_ROOT),
            },
            "output": {"stdout": result.stdout, "stderr": result.stderr},
            "files_generated": {
                name: str(path) for name, path in RESULTS.items()
            },
        }

        # Save execution summary
        with open(RESULTS["execution_summary"], "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        # Print results
        print(f"\n📊 Test Execution Summary")
        print(f"⏱️  Execution Time: {execution_time:.2f} seconds")
        print(f"🎯 Return Code: {result.returncode}")
        print(f"✅ Success: {'Yes' if result.returncode == 0 else 'No'}")

        if result.stdout:
            print(f"\n📤 STDOUT:\n{result.stdout}")

        if result.stderr:
            print(f"\n❌ STDERR:\n{result.stderr}")

        # Print generated files
        print(f"\n📁 Generated Files:")
        for name, path in RESULTS.items():
            if path.exists():
                size = path.stat().st_size
                print(f"   ✅ {name}: {path} ({size:,} bytes)")
            else:
                print(f"   ❌ {name}: {path} (not generated)")

        return result.returncode == 0

    except subprocess.TimeoutExpired:
        print("❌ Tests timed out after 10 minutes")
        return False
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False


def validate_results():
    """Validate that expected result files were generated."""
    print(f"\n🔍 Validating Test Results")

    required_files = [
        "html_report",
        "json_report",
        "junit_xml",
        "execution_summary",
    ]
    all_valid = True

    for file_key in required_files:
        file_path = RESULTS[file_key]
        if file_path.exists() and file_path.stat().st_size > 0:
            print(f"   ✅ {file_key}: {file_path}")
        else:
            print(f"   ❌ {file_key}: {file_path} (missing or empty)")
            all_valid = False

    return all_valid


def main():
    """Main test execution function."""
    print("=" * 80)
    print(f"🧪 Privacy Tools Simple - Comprehensive Unit Test Suite")
    print(f"📅 Test Date: {TEST_DATE}")
    print(f"🕒 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    # Check dependencies
    if not check_dependencies():
        sys.exit(1)

    # Ensure test directory exists
    TEST_DIR.mkdir(parents=True, exist_ok=True)

    # Run tests
    success = run_tests()

    # Validate results
    results_valid = validate_results()

    # Final summary
    print("\n" + "=" * 80)
    if success and results_valid:
        print("🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
        print(f"📋 View detailed results in: {RESULTS['html_report']}")
        print(f"📊 View coverage report in: {RESULTS['coverage_html']}")
        exit_code = 0
    else:
        print("❌ TESTS FAILED OR RESULTS INCOMPLETE")
        exit_code = 1

    print(f"🕒 Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
