#!/usr/bin/env python3
"""Test runner script for organize.py unit tests.

This script executes comprehensive unit tests for organize.py with detailed
reporting including execution timestamp, coverage, and results.

Usage:
    python run_organize_tests_2025-08-24.py

Outputs:
    - HTML test report
    - JSON test results
    - Coverage reports (HTML and JSON)
    - JUnit XML for CI integration
    - Console output with summary
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def setup_environment():
    """Setup the test environment and paths."""
    # Get script directory and project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent

    # Add project root to Python path
    sys.path.insert(0, str(project_root))

    # Ensure test output directory exists
    test_output_dir = script_dir
    test_output_dir.mkdir(parents=True, exist_ok=True)

    return project_root, test_output_dir


def install_dependencies(requirements_file):
    """Install test dependencies if needed."""
    try:
        print("Installing test dependencies...")
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
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install dependencies: {e}")
        print(f"Error output: {e.stderr}")
        return False


def run_tests(project_root, test_output_dir):
    """Run the pytest test suite with comprehensive reporting."""
    test_file = test_output_dir / "test_organize_2025-08-24.py"

    if not test_file.exists():
        print(f"✗ Test file not found: {test_file}")
        return False

    # Build pytest command with all reporting options
    pytest_cmd = [
        sys.executable,
        "-m",
        "pytest",
        str(test_file),
        "--verbose",
        "--tb=short",
        "--color=yes",
        "--durations=10",
        f"--html={test_output_dir}/result_organize_2025-08-24.html",
        "--self-contained-html",
        f"--json-report-file={test_output_dir}/result_organize_2025-08-24.json",
        f"--cov=src.utilities.file_operations.organize.organize",
        f"--cov-report=html:{test_output_dir}/result_organize_coverage_2025-08-24",
        f"--cov-report=json:{test_output_dir}/result_organize_coverage_2025-08-24.json",
        "--cov-report=term-missing",
        f"--junit-xml={test_output_dir}/result_organize_2025-08-24_junit.xml",
    ]

    print("Running tests...")
    print(f"Command: {' '.join(pytest_cmd)}")

    try:
        # Run tests
        result = subprocess.run(
            pytest_cmd,
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
        )

        # Print test output
        print("\n" + "=" * 60)
        print("TEST OUTPUT")
        print("=" * 60)
        print(result.stdout)

        if result.stderr:
            print("\n" + "=" * 60)
            print("ERROR OUTPUT")
            print("=" * 60)
            print(result.stderr)

        return result.returncode == 0

    except subprocess.TimeoutExpired:
        print("✗ Tests timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"✗ Error running tests: {e}")
        return False


def generate_summary_report(test_output_dir):
    """Generate a comprehensive summary report."""
    summary_file = test_output_dir / f"result_organize_2025-08-24_summary.json"

    # Get current timestamp
    timestamp = datetime.now().isoformat()

    # Initialize summary data
    summary = {
        "test_execution": {
            "timestamp": timestamp,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M:%S"),
            "target_module": "organize.py",
            "test_file": "test_organize_2025-08-24.py",
            "framework": "pytest",
            "python_version": sys.version,
            "platform": sys.platform,
        },
        "reports_generated": [],
        "coverage": {},
        "test_results": {},
    }

    # Check for generated reports
    report_files = [
        ("HTML Report", "result_organize_2025-08-24.html"),
        ("JSON Report", "result_organize_2025-08-24.json"),
        ("JUnit XML", "result_organize_2025-08-24_junit.xml"),
        ("Coverage HTML", "result_organize_coverage_2025-08-24/index.html"),
        ("Coverage JSON", "result_organize_coverage_2025-08-24.json"),
    ]

    for report_name, report_file in report_files:
        report_path = test_output_dir / report_file
        if report_path.exists():
            summary["reports_generated"].append(
                {
                    "name": report_name,
                    "file": report_file,
                    "exists": True,
                    "size_bytes": (
                        report_path.stat().st_size
                        if report_path.is_file()
                        else 0
                    ),
                }
            )
        else:
            summary["reports_generated"].append(
                {
                    "name": report_name,
                    "file": report_file,
                    "exists": False,
                    "size_bytes": 0,
                }
            )

    # Try to read test results from JSON report
    json_report_path = test_output_dir / "result_organize_2025-08-24.json"
    if json_report_path.exists():
        try:
            with open(json_report_path, "r") as f:
                test_data = json.load(f)
                summary["test_results"] = {
                    "total_tests": test_data.get("summary", {}).get(
                        "total", 0
                    ),
                    "passed": test_data.get("summary", {}).get("passed", 0),
                    "failed": test_data.get("summary", {}).get("failed", 0),
                    "skipped": test_data.get("summary", {}).get("skipped", 0),
                    "duration": test_data.get("duration", 0),
                }
        except Exception as e:
            summary["test_results"][
                "error"
            ] = f"Could not parse test results: {e}"

    # Try to read coverage data
    coverage_json_path = (
        test_output_dir / "result_organize_coverage_2025-08-24.json"
    )
    if coverage_json_path.exists():
        try:
            with open(coverage_json_path, "r") as f:
                coverage_data = json.load(f)
                if "totals" in coverage_data:
                    summary["coverage"] = {
                        "lines_covered": coverage_data["totals"].get(
                            "covered_lines", 0
                        ),
                        "lines_total": coverage_data["totals"].get(
                            "num_statements", 0
                        ),
                        "coverage_percent": coverage_data["totals"].get(
                            "percent_covered", 0
                        ),
                        "missing_lines": coverage_data["totals"].get(
                            "missing_lines", 0
                        ),
                        "branches_covered": coverage_data["totals"].get(
                            "covered_branches", 0
                        ),
                        "branches_total": coverage_data["totals"].get(
                            "num_branches", 0
                        ),
                    }
        except Exception as e:
            summary["coverage"][
                "error"
            ] = f"Could not parse coverage data: {e}"

    # Write summary report
    try:
        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2)
        print(f"✓ Summary report written to: {summary_file}")
        return True
    except Exception as e:
        print(f"✗ Could not write summary report: {e}")
        return False


def print_final_summary(test_output_dir):
    """Print final test execution summary to console."""
    print("\n" + "=" * 60)
    print("TEST EXECUTION SUMMARY")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target Module: organize.py")
    print(f"Test File: test_organize_2025-08-24.py")
    print(f"Output Directory: {test_output_dir}")

    # List generated files
    print("\nGenerated Reports:")
    report_files = [
        "result_organize_2025-08-24.html",
        "result_organize_2025-08-24.json",
        "result_organize_2025-08-24_junit.xml",
        "result_organize_coverage_2025-08-24.json",
        "result_organize_2025-08-24_summary.json",
    ]

    for report_file in report_files:
        report_path = test_output_dir / report_file
        if report_path.exists():
            size = report_path.stat().st_size if report_path.is_file() else 0
            print(f"  ✓ {report_file} ({size} bytes)")
        else:
            print(f"  ✗ {report_file} (missing)")

    # Check for coverage HTML directory
    coverage_html_dir = test_output_dir / "result_organize_coverage_2025-08-24"
    if coverage_html_dir.exists():
        print(f"  ✓ Coverage HTML directory: {coverage_html_dir}")
    else:
        print(f"  ✗ Coverage HTML directory: {coverage_html_dir} (missing)")


def main():
    """Main test runner function."""
    print("=" * 60)
    print("ORGANIZE.PY UNIT TEST RUNNER")
    print("=" * 60)
    print(f"Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python Version: {sys.version}")
    print(f"Platform: {sys.platform}")

    # Setup environment
    project_root, test_output_dir = setup_environment()
    print(f"Project Root: {project_root}")
    print(f"Test Output: {test_output_dir}")

    # Check for requirements file and install dependencies
    requirements_file = (
        test_output_dir / "test_requirements_organize_2025-08-24.txt"
    )
    if requirements_file.exists():
        if not install_dependencies(requirements_file):
            print("✗ Failed to install dependencies. Continuing anyway...")
    else:
        print("ℹ No requirements file found, skipping dependency installation")

    # Run tests
    success = run_tests(project_root, test_output_dir)

    # Generate summary report
    generate_summary_report(test_output_dir)

    # Print final summary
    print_final_summary(test_output_dir)

    if success:
        print("\n✓ Test execution completed successfully!")
        return 0
    else:
        print("\n✗ Test execution completed with errors!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
