#!/usr/bin/env python3
"""
Test runner for convert_to_image.py comprehensive unit tests
Created on: 2025-08-24

This script runs the comprehensive test suite for convert_to_image.py
and generates detailed reports with timestamps.
"""

import datetime
import json
import os
import subprocess
import sys
from pathlib import Path


def setup_environment():
    """Setup the test environment"""
    # Add source path to Python path
    current_dir = Path(__file__).parent
    src_path = (
        current_dir
        / ".."
        / ".."
        / "src"
        / "utilities"
        / "pdf_tools"
        / "pdf_conversion"
    )
    sys.path.insert(0, str(src_path.resolve()))

    # Change to test directory
    os.chdir(current_dir)

    print("Test environment setup completed")
    print(f"Current directory: {os.getcwd()}")
    print(f"Source path added: {src_path.resolve()}")


def install_dependencies():
    """Install test dependencies"""
    print("Installing test dependencies...")
    try:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "-r",
                "requirements_test_convert_to_image_2025-08-24.txt",
            ],
            check=True,
        )
        print("Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies: {e}")
        return False
    return True


def run_tests():
    """Run the comprehensive test suite"""
    print(
        f"\nStarting comprehensive test execution at {datetime.datetime.now()}"
    )
    print("=" * 70)

    # Test command with all reporting options
    test_command = [
        sys.executable,
        "-m",
        "pytest",
        "test_convert_to_image_2025-08-24.py",
        "-v",
        "--tb=short",
        "--html=result_convert_to_image_2025-08-24.html",
        "--self-contained-html",
        "--json-report",
        "--json-report-file=result_convert_to_image_2025-08-24.json",
        "--cov=convert_to_image",
        "--cov-report=html:result_convert_to_image_coverage_2025-08-24",
        "--cov-report=json:result_convert_to_image_coverage_2025-08-24.json",
        "--cov-report=term-missing",
        "--cov-branch",
    ]

    try:
        result = subprocess.run(test_command, capture_output=True, text=True)
        print("STDOUT:")
        print(result.stdout)

        if result.stderr:
            print("\nSTDERR:")
            print(result.stderr)

        print(
            f"\nTest execution completed with return code: {result.returncode}"
        )
        return result.returncode == 0

    except subprocess.CalledProcessError as e:
        print(f"Test execution failed: {e}")
        return False


def generate_summary_report():
    """Generate a summary report of test results"""
    print("\nGenerating summary report...")

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Try to read JSON test report
    json_report_path = "result_convert_to_image_2025-08-24.json"
    coverage_json_path = "result_convert_to_image_coverage_2025-08-24.json"

    summary = {
        "test_execution_timestamp": timestamp,
        "test_file": "convert_to_image.py",
        "test_date": "2025-08-24",
        "reports_generated": [],
    }

    # Check for generated reports
    report_files = [
        "result_convert_to_image_2025-08-24.html",
        "result_convert_to_image_2025-08-24.json",
        "result_convert_to_image_coverage_2025-08-24.json",
    ]

    for report_file in report_files:
        if os.path.exists(report_file):
            summary["reports_generated"].append(
                {
                    "file": report_file,
                    "size": os.path.getsize(report_file),
                    "created": datetime.datetime.fromtimestamp(
                        os.path.getctime(report_file)
                    ).strftime("%Y-%m-%d %H:%M:%S"),
                }
            )

    # Try to extract test results from JSON report
    if os.path.exists(json_report_path):
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
            print(f"Could not parse test results: {e}")

    # Try to extract coverage data
    if os.path.exists(coverage_json_path):
        try:
            with open(coverage_json_path, "r") as f:
                coverage_data = json.load(f)
                summary["coverage"] = {
                    "total_coverage": coverage_data.get("totals", {}).get(
                        "percent_covered", 0
                    ),
                    "lines_covered": coverage_data.get("totals", {}).get(
                        "covered_lines", 0
                    ),
                    "total_lines": coverage_data.get("totals", {}).get(
                        "num_statements", 0
                    ),
                    "missing_lines": coverage_data.get("totals", {}).get(
                        "missing_lines", 0
                    ),
                }
        except Exception as e:
            print(f"Could not parse coverage data: {e}")

    # Write summary report
    summary_file = f"result_convert_to_image_summary_2025-08-24.json"
    with open(summary_file, "w") as f:
        json.dump(summary, f, indent=2)

    # Create human-readable summary
    summary_text_file = f"result_convert_to_image_summary_2025-08-24.txt"
    with open(summary_text_file, "w") as f:
        f.write("COMPREHENSIVE TEST RESULTS SUMMARY\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Test Execution Date: {summary['test_date']}\n")
        f.write(
            f"Execution Timestamp: {summary['test_execution_timestamp']}\n"
        )
        f.write(f"Target Module: {summary['test_file']}\n\n")

        if "test_results" in summary:
            results = summary["test_results"]
            f.write("TEST RESULTS:\n")
            f.write(f"  Total Tests: {results['total_tests']}\n")
            f.write(f"  Passed: {results['passed']}\n")
            f.write(f"  Failed: {results['failed']}\n")
            f.write(f"  Skipped: {results['skipped']}\n")
            f.write(f"  Duration: {results['duration']:.2f} seconds\n\n")

        if "coverage" in summary:
            coverage = summary["coverage"]
            f.write("CODE COVERAGE:\n")
            f.write(f"  Total Coverage: {coverage['total_coverage']:.1f}%\n")
            f.write(f"  Lines Covered: {coverage['lines_covered']}\n")
            f.write(f"  Total Lines: {coverage['total_lines']}\n")
            f.write(f"  Missing Lines: {coverage['missing_lines']}\n\n")

        f.write("GENERATED REPORTS:\n")
        for report in summary["reports_generated"]:
            f.write(
                f"  - {report['file']} ({report['size']} bytes, created {report['created']})\n"
            )

    print(f"Summary reports generated:")
    print(f"  - {summary_file}")
    print(f"  - {summary_text_file}")


def main():
    """Main test execution function"""
    print("COMPREHENSIVE UNIT TEST SUITE FOR convert_to_image.py")
    print("=" * 60)
    print(f"Execution started at: {datetime.datetime.now()}")
    print(f"Test date: 2025-08-24")
    print()

    # Setup environment
    setup_environment()

    # Install dependencies
    if not install_dependencies():
        print("Failed to install dependencies. Exiting.")
        sys.exit(1)

    # Run tests
    test_success = run_tests()

    # Generate summary
    generate_summary_report()

    print("\n" + "=" * 60)
    if test_success:
        print("TEST EXECUTION COMPLETED SUCCESSFULLY!")
    else:
        print("TEST EXECUTION COMPLETED WITH ISSUES!")

    print(f"Execution finished at: {datetime.datetime.now()}")
    print("\nGenerated files:")
    print("  - result_convert_to_image_2025-08-24.html (HTML test report)")
    print("  - result_convert_to_image_2025-08-24.json (JSON test report)")
    print("  - result_convert_to_image_coverage_2025-08-24/ (Coverage HTML)")
    print(
        "  - result_convert_to_image_coverage_2025-08-24.json (Coverage JSON)"
    )
    print("  - result_convert_to_image_summary_2025-08-24.json (Summary JSON)")
    print("  - result_convert_to_image_summary_2025-08-24.txt (Summary text)")

    return 0 if test_success else 1


if __name__ == "__main__":
    sys.exit(main())
