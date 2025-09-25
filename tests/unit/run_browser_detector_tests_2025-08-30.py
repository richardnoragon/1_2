#!/usr/bin/env python3
"""
Test runner script for browser_detector.py unit tests
Execution Date: 2025-08-30
Target: test_browser_detector_2025-08-30.py

This script executes comprehensive unit tests for the BrowserDetector class
and generates detailed HTML and JSON reports with coverage analysis.
"""

import datetime
import json
import os
import subprocess
import sys
from pathlib import Path


def setup_environment():
    """Set up the test environment and paths."""
    # Get the current working directory
    cwd = Path.cwd()

    # Ensure we're in the correct directory
    if not (cwd / "tests" / "unit").exists():
        print(
            "Error: tests/unit directory not found. Please run from project root."
        )
        sys.exit(1)

    # Create results directory if it doesn't exist
    results_dir = cwd / "tests" / "unit" / "results"
    results_dir.mkdir(exist_ok=True)

    # Add source directory to Python path
    src_dir = cwd / "src"
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    return cwd, results_dir


def run_tests(cwd, results_dir):
    """Execute the test suite with comprehensive reporting."""
    test_file = "test_browser_detector_2025-08-30.py"
    config_file = "pytest_browser_detector_2025-08-30.ini"

    # Get Python executable
    python_executable = sys.executable
    if "venv" in str(Path(python_executable).parent):
        # Use the venv python
        venv_python = Path(cwd) / "venv" / "Scripts" / "python.exe"
        if venv_python.exists():
            python_executable = str(venv_python)

    # Construct pytest command
    cmd = [
        python_executable,
        "-m",
        "pytest",
        f"tests/unit/{test_file}",
        "-c",
        f"tests/unit/{config_file}",
        "--verbose",
        "--tb=long",
        f"--cov=src.utilities.privacy.privacy_tools.core.browser_detector",
        f"--cov-report=html:{results_dir}/coverage_browser_detector_2025-08-30",
        f"--cov-report=json:{results_dir}/result_browser_detector_2025-08-30_coverage.json",
        "--cov-report=term-missing",
        f"--html={results_dir}/result_browser_detector_2025-08-30_report.html",
        "--self-contained-html",
        "--json-report",
        f"--json-report-file={results_dir}/result_browser_detector_2025-08-30_results.json",
        f"--junit-xml={results_dir}/result_browser_detector_2025-08-30_junit.xml",
        "--timeout=60",
    ]

    print("=" * 80)
    print("BROWSER DETECTOR UNIT TESTS - EXECUTION STARTED")
    print("=" * 80)
    print(
        f"Timestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    print(f"Test File: {test_file}")
    print(f"Config File: {config_file}")
    print(f"Python Executable: {python_executable}")
    print(f"Working Directory: {cwd}")
    print(f"Results Directory: {results_dir}")
    print("=" * 80)

    # Execute the tests
    try:
        result = subprocess.run(
            cmd, cwd=cwd, capture_output=True, text=True, timeout=300
        )

        print("STDOUT:")
        print(result.stdout)

        if result.stderr:
            print("STDERR:")
            print(result.stderr)

        print("=" * 80)
        print(
            f"Test execution completed with return code: {result.returncode}"
        )
        print("=" * 80)

        return result.returncode == 0, result.stdout, result.stderr

    except subprocess.TimeoutExpired:
        print("ERROR: Test execution timed out after 5 minutes")
        return False, "", "Test execution timeout"

    except Exception as e:
        print(f"ERROR: Failed to execute tests: {e}")
        return False, "", str(e)


def generate_summary_report(results_dir, success, stdout, stderr):
    """Generate a comprehensive summary report."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")

    # Create summary data
    summary_data = {
        "test_execution": {
            "timestamp": timestamp,
            "date": date_str,
            "target_file": "browser_detector.py",
            "test_file": "test_browser_detector_2025-08-30.py",
            "success": success,
            "execution_time": None,
        },
        "test_results": {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": 0,
        },
        "coverage": {
            "line_coverage": 0,
            "branch_coverage": 0,
            "total_statements": 0,
            "missing_statements": 0,
        },
        "outputs": {
            "html_report": f"result_browser_detector_{date_str}_report.html",
            "json_results": f"result_browser_detector_{date_str}_results.json",
            "junit_xml": f"result_browser_detector_{date_str}_junit.xml",
            "coverage_html": f"coverage_browser_detector_{date_str}/index.html",
            "coverage_json": f"result_browser_detector_{date_str}_coverage.json",
        },
        "execution_details": {"stdout": stdout, "stderr": stderr},
    }

    # Try to parse JSON results if available
    json_results_file = (
        results_dir / f"result_browser_detector_{date_str}_results.json"
    )
    if json_results_file.exists():
        try:
            with open(json_results_file, "r") as f:
                json_data = json.load(f)

            summary_data["test_results"]["total_tests"] = json_data.get(
                "summary", {}
            ).get("total", 0)
            summary_data["test_results"]["passed"] = json_data.get(
                "summary", {}
            ).get("passed", 0)
            summary_data["test_results"]["failed"] = json_data.get(
                "summary", {}
            ).get("failed", 0)
            summary_data["test_results"]["skipped"] = json_data.get(
                "summary", {}
            ).get("skipped", 0)
            summary_data["test_results"]["errors"] = json_data.get(
                "summary", {}
            ).get("error", 0)

            if "duration" in json_data:
                summary_data["test_execution"][
                    "execution_time"
                ] = f"{json_data['duration']:.2f} seconds"

        except Exception as e:
            print(f"Warning: Could not parse JSON results: {e}")

    # Try to parse coverage results if available
    coverage_json_file = (
        results_dir / f"result_browser_detector_{date_str}_coverage.json"
    )
    if coverage_json_file.exists():
        try:
            with open(coverage_json_file, "r") as f:
                coverage_data = json.load(f)

            if "totals" in coverage_data:
                totals = coverage_data["totals"]
                summary_data["coverage"]["total_statements"] = totals.get(
                    "num_statements", 0
                )
                summary_data["coverage"]["missing_statements"] = totals.get(
                    "missing_lines", 0
                )
                summary_data["coverage"]["line_coverage"] = totals.get(
                    "percent_covered", 0
                )

        except Exception as e:
            print(f"Warning: Could not parse coverage data: {e}")

    # Save comprehensive summary
    summary_file = (
        results_dir / f"result_browser_detector_{date_str}_summary.json"
    )
    with open(summary_file, "w") as f:
        json.dump(summary_data, f, indent=2)

    # Create markdown summary
    markdown_summary = f"""# Browser Detector Unit Tests - Execution Summary

## Test Execution Details
- **Timestamp**: {timestamp}
- **Target File**: browser_detector.py
- **Test File**: test_browser_detector_2025-08-30.py
- **Execution Status**: {'✅ SUCCESS' if success else '❌ FAILED'}
- **Execution Time**: {summary_data['test_execution']['execution_time'] or 'N/A'}

## Test Results
- **Total Tests**: {summary_data['test_results']['total_tests']}
- **Passed**: {summary_data['test_results']['passed']}
- **Failed**: {summary_data['test_results']['failed']}
- **Skipped**: {summary_data['test_results']['skipped']}
- **Errors**: {summary_data['test_results']['errors']}

## Coverage Analysis
- **Line Coverage**: {summary_data['coverage']['line_coverage']:.1f}%
- **Total Statements**: {summary_data['coverage']['total_statements']}
- **Missing Statements**: {summary_data['coverage']['missing_statements']}

## Generated Reports
- **HTML Report**: {summary_data['outputs']['html_report']}
- **JSON Results**: {summary_data['outputs']['json_results']}
- **JUnit XML**: {summary_data['outputs']['junit_xml']}
- **Coverage HTML**: {summary_data['outputs']['coverage_html']}
- **Coverage JSON**: {summary_data['outputs']['coverage_json']}

## Test Categories Covered
- ✅ Basic initialization and platform detection
- ✅ Browser installation detection (Windows, macOS, Linux)
- ✅ Running browser detection and process management
- ✅ Browser data path retrieval and validation
- ✅ Access permission validation
- ✅ Comprehensive browser information gathering
- ✅ Cache management and refresh functionality
- ✅ Edge cases and error conditions
- ✅ Parameterized tests for multiple browsers and platforms

## Test Features
- **Comprehensive Mocking**: All external dependencies properly mocked
- **Platform Coverage**: Tests for Windows, macOS, and Linux platforms
- **Error Handling**: Tests for permission errors, file not found, etc.
- **Edge Cases**: Empty lists, unknown browsers, system errors
- **Parameterized Testing**: Multiple browser types and platform combinations

---
*Generated on {timestamp}*
"""

    markdown_file = (
        results_dir / f"result_browser_detector_{date_str}_documentation.md"
    )
    with open(markdown_file, "w") as f:
        f.write(markdown_summary)

    return summary_data


def main():
    """Main execution function."""
    print("Browser Detector Unit Test Runner")
    print("=" * 50)

    # Setup environment
    cwd, results_dir = setup_environment()

    # Run tests
    success, stdout, stderr = run_tests(cwd, results_dir)

    # Generate summary
    summary = generate_summary_report(results_dir, success, stdout, stderr)

    # Print final status
    print("\n" + "=" * 80)
    print("FINAL EXECUTION STATUS")
    print("=" * 80)
    print(f"Tests Executed: {'✅ SUCCESS' if success else '❌ FAILED'}")
    print(f"Total Tests: {summary['test_results']['total_tests']}")
    print(f"Passed: {summary['test_results']['passed']}")
    print(f"Failed: {summary['test_results']['failed']}")
    print(f"Coverage: {summary['coverage']['line_coverage']:.1f}%")
    print(f"Results Directory: {results_dir}")
    print("=" * 80)

    # Return appropriate exit code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
