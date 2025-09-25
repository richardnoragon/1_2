#!/usr/bin/env python3
"""
Simple Test Runner for main.py Unit Tests
Richard's File Utilities - Main Module Testing Suite

This script executes the main.py unit tests and generates the required outputs.

Created: 2025-08-28
Target: main.py
Framework: pytest

Execution: python simple_run_main_tests_2025-08-28.py
"""

import datetime
import os
import subprocess
import sys
from pathlib import Path


def main():
    """Execute the test suite with basic reporting."""
    print("🚀 Main.py Unit Test Runner - Simple Execution")

    # Set up paths
    test_dir = Path(__file__).parent
    project_root = test_dir.parent.parent
    date_suffix = datetime.datetime.now().strftime("%Y-%m-%d")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Test file
    test_file = test_dir / f"test_main_{date_suffix}.py"

    # Output files
    html_report = test_dir / f"result_main_{date_suffix}.html"
    json_report = test_dir / f"result_main_{date_suffix}.json"
    xml_report = test_dir / f"result_main_{date_suffix}.xml"
    coverage_dir = test_dir / f"result_main_{date_suffix}_coverage"

    print(f"📅 Date: {date_suffix}")
    print(f"⏰ Timestamp: {timestamp}")
    print(f"📁 Test file: {test_file}")
    print("=" * 80)

    if not test_file.exists():
        print(f"❌ Test file not found: {test_file}")
        return 1

    # Change to project root for imports
    os.chdir(str(project_root))

    # Set environment variables
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    os.environ["PYTEST_RUNNING"] = "1"

    # Build pytest command
    pytest_cmd = [
        sys.executable,
        "-m",
        "pytest",
        str(test_file),
        "--verbose",
        "--tb=short",
        "--disable-warnings",
        "--durations=10",
        f"--html={html_report}",
        "--self-contained-html",
        "--json-report",
        f"--json-report-file={json_report}",
        f"--junitxml={xml_report}",
        "--cov=main",
        f"--cov-report=html:{coverage_dir}",
        "--cov-report=term-missing",
        "--timeout=300",
    ]

    print("🔧 Running pytest with coverage...")
    print(f"Command: {' '.join(pytest_cmd)}")
    print()

    # Execute tests
    start_time = datetime.datetime.now()

    try:
        result = subprocess.run(
            pytest_cmd,
            capture_output=True,
            text=True,
            timeout=600,  # 10 minutes
        )

        end_time = datetime.datetime.now()
        duration = (end_time - start_time).total_seconds()

        print("=" * 80)
        print("📊 TEST EXECUTION RESULTS")
        print("=" * 80)
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print(f"🔢 Exit Code: {result.returncode}")
        print(
            f"📋 Status: {'✅ SUCCESS' if result.returncode == 0 else '❌ FAILED'}"
        )

        # Show stdout
        if result.stdout:
            print("\n📝 Test Output:")
            print(result.stdout)

        # Show stderr if there are errors
        if result.stderr and result.returncode != 0:
            print("\n⚠️  Error Output:")
            print(result.stderr)

        # Check generated files
        print("\n📁 Generated Files:")
        report_files = [
            ("HTML Report", html_report),
            ("JSON Report", json_report),
            ("XML Report", xml_report),
            ("Coverage HTML", coverage_dir / "index.html"),
        ]

        for file_type, file_path in report_files:
            if file_path.exists():
                size = (
                    file_path.stat().st_size
                    if file_path.is_file()
                    else "directory"
                )
                print(f"✅ {file_type}: {file_path.name} ({size} bytes)")
            else:
                print(f"❌ {file_type}: Not generated")

        # Create simple summary
        summary_file = test_dir / f"result_main_{date_suffix}_summary.txt"
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write(f"Main.py Unit Tests Summary\n")
            f.write(f"Date: {date_suffix}\n")
            f.write(f"Timestamp: {timestamp}\n")
            f.write(f"Duration: {duration:.2f} seconds\n")
            f.write(f"Exit Code: {result.returncode}\n")
            f.write(
                f"Status: {'SUCCESS' if result.returncode == 0 else 'FAILED'}\n"
            )
            f.write(f"\nGenerated Files:\n")
            for file_type, file_path in report_files:
                status = "✅" if file_path.exists() else "❌"
                f.write(f"{status} {file_type}: {file_path.name}\n")

        print(f"✅ Summary saved: {summary_file.name}")

        return result.returncode

    except subprocess.TimeoutExpired:
        print("⏰ Test execution timed out!")
        return 1
    except Exception as e:
        print(f"💥 Error running tests: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
