"""
Test Runner for Performance Analyzer Tests
Generated: 2025-08-28

This script runs comprehensive unit tests for performance_analyzer.py with detailed reporting.
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def run_tests():
    """Execute the performance analyzer tests with comprehensive reporting."""

    # Test execution timestamp
    start_time = datetime.now()
    print(
        f"Starting Performance Analyzer Test Suite - {start_time.strftime('%Y-%m-%d %H:%M:%S')}"
    )
    print("=" * 80)

    # Define paths
    current_dir = Path(__file__).parent
    test_file = current_dir / "test_performance_analyzer_2025-08-28.py"
    config_file = current_dir / "pytest_performance_analyzer_2025-08-28.ini"

    # Test command with all reporting options
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        str(test_file),
        f"-c={config_file}",
        "-v",
        "--tb=short",
        "--html=result_performance_analyzer_html_report_2025-08-28.html",
        "--self-contained-html",
        "--json-report",
        "--json-report-file=result_performance_analyzer_json_report_2025-08-28.json",
        "--cov=performance_analyzer",
        "--cov-report=html:result_performance_analyzer_coverage_2025-08-28",
        "--cov-report=json:result_performance_analyzer_coverage_2025-08-28.json",
        "--cov-report=term-missing",
        "--durations=10",
    ]

    try:
        # Execute tests
        print("Executing test command:")
        print(" ".join(cmd))
        print("-" * 80)

        result = subprocess.run(
            cmd, capture_output=True, text=True, cwd=current_dir
        )

        # Print test output
        print("STDOUT:")
        print(result.stdout)

        if result.stderr:
            print("STDERR:")
            print(result.stderr)

        end_time = datetime.now()
        duration = end_time - start_time

        # Generate execution summary
        summary = {
            "test_suite": "Performance Analyzer Unit Tests",
            "target_file": "performance_analyzer.py",
            "test_file": "test_performance_analyzer_2025-08-28.py",
            "execution_start": start_time.isoformat(),
            "execution_end": end_time.isoformat(),
            "duration_seconds": duration.total_seconds(),
            "return_code": result.returncode,
            "command_executed": " ".join(cmd),
            "success": result.returncode == 0,
        }

        # Load and include test results if available
        json_report_file = (
            current_dir
            / "result_performance_analyzer_json_report_2025-08-28.json"
        )
        if json_report_file.exists():
            try:
                with open(json_report_file, "r") as f:
                    test_results = json.load(f)
                    summary["test_results"] = {
                        "total_tests": test_results.get("summary", {}).get(
                            "total", 0
                        ),
                        "passed": test_results.get("summary", {}).get(
                            "passed", 0
                        ),
                        "failed": test_results.get("summary", {}).get(
                            "failed", 0
                        ),
                        "skipped": test_results.get("summary", {}).get(
                            "skipped", 0
                        ),
                        "errors": test_results.get("summary", {}).get(
                            "error", 0
                        ),
                        "test_duration": test_results.get("duration", 0),
                    }
            except Exception as e:
                summary["json_report_error"] = str(e)

        # Load coverage data if available
        coverage_file = (
            current_dir
            / "result_performance_analyzer_coverage_2025-08-28.json"
        )
        if coverage_file.exists():
            try:
                with open(coverage_file, "r") as f:
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
                summary["coverage_report_error"] = str(e)

        # Write execution summary
        summary_file = (
            current_dir
            / "result_performance_analyzer_execution_summary_2025-08-28.json"
        )
        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2)

        print("=" * 80)
        print(
            f"Test execution completed - {end_time.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        print(f"Duration: {duration.total_seconds():.2f} seconds")
        print(f"Return code: {result.returncode}")
        print(f"Success: {summary['success']}")

        if summary.get("test_results"):
            tr = summary["test_results"]
            print(
                f"Tests: {tr['total_tests']} total, {tr['passed']} passed, {tr['failed']} failed"
            )

        if summary.get("coverage"):
            cov = summary["coverage"]
            print(
                f"Coverage: {cov['total_coverage']:.1f}% ({cov['lines_covered']}/{cov['total_lines']} lines)"
            )

        print("\nGenerated Reports:")
        print(
            f"- HTML Report: result_performance_analyzer_html_report_2025-08-28.html"
        )
        print(
            f"- JSON Report: result_performance_analyzer_json_report_2025-08-28.json"
        )
        print(
            f"- Coverage HTML: result_performance_analyzer_coverage_2025-08-28/"
        )
        print(
            f"- Coverage JSON: result_performance_analyzer_coverage_2025-08-28.json"
        )
        print(
            f"- Execution Summary: result_performance_analyzer_execution_summary_2025-08-28.json"
        )

        return result.returncode == 0

    except Exception as e:
        print(f"Error executing tests: {e}")
        return False


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
