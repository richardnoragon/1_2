#!/usr/bin/env python3
"""
Test Runner for size_analyzer_config.py
Created: 2025-08-29
Author: GitHub Copilot

This script runs comprehensive unit tests for size_analyzer_config.py
and generates detailed HTML and JSON reports with coverage information.
"""

import datetime
import json
import os
import subprocess
import sys
import time
from pathlib import Path


def setup_environment():
    """Setup the test environment and install dependencies."""
    print("Setting up test environment...")

    # Get the test directory
    test_dir = Path(__file__).parent
    requirements_file = (
        test_dir / "test_requirements_size_analyzer_config_2025-08-29.txt"
    )

    # Install test requirements
    if requirements_file.exists():
        print(f"Installing test requirements from {requirements_file}")
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
            print("✓ Test requirements installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"⚠ Warning: Failed to install some requirements: {e}")
            print("Continuing with existing packages...")

    # Add the project root to Python path
    project_root = test_dir.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    return test_dir


def run_tests(test_dir):
    """Run the comprehensive test suite."""
    print("\n" + "=" * 60)
    print("RUNNING COMPREHENSIVE UNIT TESTS")
    print("=" * 60)

    start_time = time.time()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"Test execution started at: {timestamp}")
    print(f"Test directory: {test_dir}")
    print(f"Python version: {sys.version}")

    # Test file to run
    test_file = test_dir / "test_size_analyzer_config_2025-08-29.py"

    if not test_file.exists():
        print(f"❌ Error: Test file not found: {test_file}")
        return False

    # Pytest command with comprehensive reporting
    pytest_cmd = [
        sys.executable,
        "-m",
        "pytest",
        str(test_file),
        "--verbose",
        "--tb=short",
        "--strict-markers",
        "--strict-config",
        f"--html={test_dir}/result_size_analyzer_config_2025-08-29.html",
        "--self-contained-html",
        "--json-report",
        f"--json-report-file={test_dir}/result_size_analyzer_config_2025-08-29.json",
        "--cov=src.utilities.analysis.config.size_analyzer_config",
        f"--cov-report=html:{test_dir}/result_size_analyzer_config_coverage_2025-08-29",
        f"--cov-report=json:{test_dir}/result_size_analyzer_config_coverage_2025-08-29.json",
        "--cov-report=term-missing",
        "--cov-branch",
        "--timeout=300",
    ]

    print(f"\nExecuting command: {' '.join(pytest_cmd)}")
    print("-" * 60)

    try:
        # Run pytest
        result = subprocess.run(
            pytest_cmd,
            cwd=test_dir,
            capture_output=True,
            text=True,
            timeout=600,  # 10 minute timeout
        )

        end_time = time.time()
        execution_time = end_time - start_time

        print(f"\nTest execution completed in {execution_time:.2f} seconds")

        # Print stdout and stderr
        if result.stdout:
            print("\n" + "=" * 60)
            print("TEST OUTPUT")
            print("=" * 60)
            print(result.stdout)

        if result.stderr:
            print("\n" + "=" * 60)
            print("ERROR OUTPUT")
            print("=" * 60)
            print(result.stderr)

        # Check return code
        if result.returncode == 0:
            print("\n✓ All tests passed successfully!")
        else:
            print(f"\n⚠ Tests completed with return code: {result.returncode}")
            if result.returncode == 1:
                print("Some tests failed - check the reports for details")
            elif result.returncode == 2:
                print("Test execution was interrupted")
            elif result.returncode == 3:
                print("Internal error occurred")

        return result.returncode == 0

    except subprocess.TimeoutExpired:
        print("\n❌ Error: Test execution timed out after 10 minutes")
        return False
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error: Test execution failed: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False


def generate_summary_report(test_dir):
    """Generate a comprehensive summary report."""
    print("\n" + "=" * 60)
    print("GENERATING SUMMARY REPORT")
    print("=" * 60)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Read JSON report if available
    json_report_file = test_dir / "result_size_analyzer_config_2025-08-29.json"
    coverage_json_file = (
        test_dir / "result_size_analyzer_config_coverage_2025-08-29.json"
    )

    summary_data = {
        "execution_timestamp": timestamp,
        "test_target": "size_analyzer_config.py",
        "test_file": "test_size_analyzer_config_2025-08-29.py",
        "reports_generated": [],
        "test_results": {},
        "coverage_results": {},
        "file_locations": {},
    }

    # Check for generated reports
    reports = [
        ("HTML Report", "result_size_analyzer_config_2025-08-29.html"),
        ("JSON Report", "result_size_analyzer_config_2025-08-29.json"),
        (
            "Coverage HTML",
            "result_size_analyzer_config_coverage_2025-08-29/index.html",
        ),
        (
            "Coverage JSON",
            "result_size_analyzer_config_coverage_2025-08-29.json",
        ),
    ]

    for report_name, file_path in reports:
        full_path = test_dir / file_path
        if full_path.exists():
            summary_data["reports_generated"].append(report_name)
            summary_data["file_locations"][report_name] = str(full_path)
            print(f"✓ {report_name}: {full_path}")
        else:
            print(f"⚠ {report_name}: Not found at {full_path}")

    # Parse JSON report if available
    if json_report_file.exists():
        try:
            with open(json_report_file, "r", encoding="utf-8") as f:
                json_data = json.load(f)

            summary_data["test_results"] = {
                "total_tests": json_data.get("summary", {}).get("total", 0),
                "passed": json_data.get("summary", {}).get("passed", 0),
                "failed": json_data.get("summary", {}).get("failed", 0),
                "skipped": json_data.get("summary", {}).get("skipped", 0),
                "errors": json_data.get("summary", {}).get("error", 0),
                "duration": json_data.get("duration", 0),
                "exit_code": json_data.get("exitcode", -1),
            }

            print(f"\\n📊 Test Results Summary:")
            print(
                f"   Total Tests: {summary_data['test_results']['total_tests']}"
            )
            print(f"   Passed: {summary_data['test_results']['passed']}")
            print(f"   Failed: {summary_data['test_results']['failed']}")
            print(f"   Skipped: {summary_data['test_results']['skipped']}")
            print(f"   Errors: {summary_data['test_results']['errors']}")
            print(
                f"   Duration: {summary_data['test_results']['duration']:.2f}s"
            )

        except Exception as e:
            print(f"⚠ Could not parse JSON report: {e}")

    # Parse coverage report if available
    if coverage_json_file.exists():
        try:
            with open(coverage_json_file, "r", encoding="utf-8") as f:
                coverage_data = json.load(f)

            totals = coverage_data.get("totals", {})
            summary_data["coverage_results"] = {
                "statements": totals.get("num_statements", 0),
                "missing": totals.get("missing_lines", 0),
                "excluded": totals.get("excluded_lines", 0),
                "branches": totals.get("num_branches", 0),
                "partial_branches": totals.get("num_partial_branches", 0),
                "coverage_percent": totals.get("percent_covered", 0.0),
                "branch_coverage_percent": totals.get(
                    "percent_covered_display", "0%"
                ),
            }

            print(f"\\n📈 Coverage Results:")
            print(
                f"   Line Coverage: {summary_data['coverage_results']['coverage_percent']:.1f}%"
            )
            print(
                f"   Statements: {summary_data['coverage_results']['statements']}"
            )
            print(
                f"   Missing Lines: {summary_data['coverage_results']['missing']}"
            )
            print(
                f"   Branches: {summary_data['coverage_results']['branches']}"
            )

        except Exception as e:
            print(f"⚠ Could not parse coverage report: {e}")

    # Save summary report
    summary_file = (
        test_dir / "result_size_analyzer_config_summary_2025-08-29.json"
    )
    try:
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(summary_data, f, indent=2, ensure_ascii=False)
        print(f"\\n✓ Summary report saved: {summary_file}")
    except Exception as e:
        print(f"⚠ Could not save summary report: {e}")

    return summary_data


def main():
    """Main execution function."""
    print("🧪 Size Analyzer Config - Comprehensive Unit Test Runner")
    print("=" * 60)
    print(
        f"Execution Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    print(f"Target Module: size_analyzer_config.py")
    print(f"Python Version: {sys.version}")

    try:
        # Setup environment
        test_dir = setup_environment()

        # Run tests
        success = run_tests(test_dir)

        # Generate summary
        summary_data = generate_summary_report(test_dir)

        # Final status
        print("\\n" + "=" * 60)
        print("EXECUTION COMPLETE")
        print("=" * 60)

        if success:
            print("🎉 All tests completed successfully!")
            print("📋 Reports have been generated in the test directory.")
        else:
            print(
                "⚠ Tests completed with issues - check the reports for details."
            )

        print(f"\\n📁 Test Directory: {test_dir}")
        print("\\n📊 Generated Reports:")
        for report_name in summary_data.get("reports_generated", []):
            file_path = summary_data["file_locations"].get(
                report_name, "Unknown"
            )
            print(f"   • {report_name}: {file_path}")

        return 0 if success else 1

    except KeyboardInterrupt:
        print("\\n❌ Test execution interrupted by user")
        return 130
    except Exception as e:
        print(f"\\n❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
