#!/usr/bin/env python3
"""
Enhanced Editor Test Runner
Created: 2025-08-29

This script runs comprehensive unit tests for the Enhanced Editor module
and generates detailed reports with timestamps and coverage information.
"""

import datetime
import json
import os
import subprocess
import sys
from pathlib import Path

# Test configuration
TEST_DIR = Path(__file__).parent
PROJECT_ROOT = TEST_DIR.parent.parent
RESULTS_DIR = TEST_DIR / "unit"
DATE_SUFFIX = "2025-08-29"

# Test files and output files
TEST_FILE = RESULTS_DIR / f"test_enhanced_editor_{DATE_SUFFIX}.py"
CONFIG_FILE = RESULTS_DIR / f"pytest_enhanced_editor_{DATE_SUFFIX}.ini"
CONFTEST_FILE = RESULTS_DIR / f"conftest_enhanced_editor_{DATE_SUFFIX}.py"

# Output files
HTML_REPORT = RESULTS_DIR / f"result_enhanced_editor_report_{DATE_SUFFIX}.html"
JSON_REPORT = (
    RESULTS_DIR / f"result_enhanced_editor_results_{DATE_SUFFIX}.json"
)
COVERAGE_HTML = RESULTS_DIR / f"result_enhanced_editor_coverage_{DATE_SUFFIX}"
COVERAGE_JSON = (
    RESULTS_DIR / f"result_enhanced_editor_coverage_{DATE_SUFFIX}.json"
)
EXECUTION_LOG = (
    RESULTS_DIR / f"result_enhanced_editor_execution_{DATE_SUFFIX}.log"
)


def ensure_dependencies():
    """Ensure required dependencies are installed."""
    required_packages = [
        "pytest",
        "pytest-html",
        "pytest-json-report",
        "pytest-cov",
        "coverage",
        "PyQt5",
    ]

    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print(f"Installing missing packages: {missing_packages}")
        subprocess.run(
            [sys.executable, "-m", "pip", "install"] + missing_packages,
            check=True,
        )


def create_execution_summary():
    """Create execution summary with timestamp."""
    timestamp = datetime.datetime.now()

    summary = {
        "execution_info": {
            "timestamp": timestamp.isoformat(),
            "date": timestamp.strftime("%Y-%m-%d"),
            "time": timestamp.strftime("%H:%M:%S"),
            "test_file": str(TEST_FILE),
            "config_file": str(CONFIG_FILE),
            "python_version": sys.version,
            "platform": sys.platform,
        },
        "test_configuration": {
            "test_framework": "pytest",
            "coverage_enabled": True,
            "html_report": True,
            "json_report": True,
            "target_module": "src.tools.file_operations.enhanced_editor.enhanced_editor",
        },
        "output_files": {
            "html_report": str(HTML_REPORT),
            "json_report": str(JSON_REPORT),
            "coverage_html": str(COVERAGE_HTML),
            "coverage_json": str(COVERAGE_JSON),
            "execution_log": str(EXECUTION_LOG),
        },
    }

    return summary


def run_tests():
    """Run the test suite with comprehensive reporting."""
    print("Enhanced Editor Test Suite")
    print("=" * 50)
    print(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Test file: {TEST_FILE}")
    print(f"Results directory: {RESULTS_DIR}")
    print()

    # Ensure output directory exists
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Check if test file exists
    if not TEST_FILE.exists():
        print(f"ERROR: Test file not found: {TEST_FILE}")
        return False

    # Build pytest command
    pytest_cmd = [
        sys.executable,
        "-m",
        "pytest",
        str(TEST_FILE),
        f"--html={HTML_REPORT}",
        "--self-contained-html",
        f"--json-report-file={JSON_REPORT}",
        "--json-report",
        f"--cov=src.utilities.file_operations.enhanced_editor.enhanced_editor",
        f"--cov-report=html:{COVERAGE_HTML}",
        f"--cov-report=json:{COVERAGE_JSON}",
        "--cov-report=term-missing",
        "--verbose",
        "--tb=short",
        "--showlocals",
        "--durations=10",
        "-x",  # Stop on first failure for debugging
    ]

    # Add config file if it exists
    if CONFIG_FILE.exists():
        pytest_cmd.extend(["-c", str(CONFIG_FILE)])

    print("Running pytest with command:")
    print(" ".join(pytest_cmd))
    print()

    # Create execution summary
    summary = create_execution_summary()

    try:
        # Run tests and capture output
        with open(EXECUTION_LOG, "w") as log_file:
            log_file.write(
                f"Test execution started: {summary['execution_info']['timestamp']}\n"
            )
            log_file.write(f"Command: {' '.join(pytest_cmd)}\n\n")

            result = subprocess.run(
                pytest_cmd,
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            # Write output to log
            log_file.write("STDOUT:\n")
            log_file.write(result.stdout)
            log_file.write("\n\nSTDERR:\n")
            log_file.write(result.stderr)
            log_file.write(f"\n\nReturn code: {result.returncode}\n")

        # Update summary with results
        summary["execution_results"] = {
            "return_code": result.returncode,
            "success": result.returncode == 0,
            "stdout_lines": len(result.stdout.splitlines()),
            "stderr_lines": len(result.stderr.splitlines()),
        }

        # Print results
        print("Test execution completed!")
        print(f"Return code: {result.returncode}")
        if result.returncode == 0:
            print("✓ All tests passed!")
        else:
            print("✗ Some tests failed or encountered errors")

        print(f"\nExecution log saved to: {EXECUTION_LOG}")

        # Parse and include test results if JSON report was created
        if JSON_REPORT.exists():
            try:
                with open(JSON_REPORT, "r") as f:
                    test_results = json.load(f)
                    summary["test_results"] = {
                        "total": test_results.get("summary", {}).get(
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
                        "duration": test_results.get("duration", 0),
                    }
                    print(
                        f"Tests: {summary['test_results']['total']} total, "
                        f"{summary['test_results']['passed']} passed, "
                        f"{summary['test_results']['failed']} failed, "
                        f"{summary['test_results']['skipped']} skipped"
                    )
                    print(
                        f"Duration: {summary['test_results']['duration']:.2f} seconds"
                    )
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Warning: Could not parse test results: {e}")

        # Parse and include coverage results if JSON coverage was created
        if COVERAGE_JSON.exists():
            try:
                with open(COVERAGE_JSON, "r") as f:
                    coverage_data = json.load(f)
                    summary["coverage_results"] = {
                        "line_coverage": coverage_data.get("totals", {}).get(
                            "percent_covered", 0
                        ),
                        "lines_covered": coverage_data.get("totals", {}).get(
                            "covered_lines", 0
                        ),
                        "lines_total": coverage_data.get("totals", {}).get(
                            "num_statements", 0
                        ),
                        "missing_lines": coverage_data.get("totals", {}).get(
                            "missing_lines", 0
                        ),
                    }
                    print(
                        f"Coverage: {summary['coverage_results']['line_coverage']:.1f}% "
                        f"({summary['coverage_results']['lines_covered']}/{summary['coverage_results']['lines_total']} lines)"
                    )
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Warning: Could not parse coverage results: {e}")

        # Print output file locations
        print(f"\nGenerated reports:")
        if HTML_REPORT.exists():
            print(f"  HTML Report: {HTML_REPORT}")
        if JSON_REPORT.exists():
            print(f"  JSON Report: {JSON_REPORT}")
        if COVERAGE_HTML.exists():
            print(f"  Coverage HTML: {COVERAGE_HTML}")
        if COVERAGE_JSON.exists():
            print(f"  Coverage JSON: {COVERAGE_JSON}")

        return result.returncode == 0

    except subprocess.TimeoutExpired:
        summary["execution_results"] = {
            "return_code": -1,
            "success": False,
            "error": "Test execution timed out",
        }
        print("ERROR: Test execution timed out")
        return False

    except Exception as e:
        summary["execution_results"] = {
            "return_code": -1,
            "success": False,
            "error": str(e),
        }
        print(f"ERROR: Test execution failed: {e}")
        return False

    finally:
        # Save execution summary
        summary_file = (
            RESULTS_DIR / f"result_enhanced_editor_summary_{DATE_SUFFIX}.json"
        )
        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2)
        print(f"Execution summary saved to: {summary_file}")


def main():
    """Main execution function."""
    try:
        # Ensure dependencies
        ensure_dependencies()

        # Run tests
        success = run_tests()

        if success:
            print("\n🎉 Test suite completed successfully!")
            return 0
        else:
            print("\n❌ Test suite completed with failures")
            return 1

    except KeyboardInterrupt:
        print("\n⏹️  Test execution interrupted by user")
        return 130
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
