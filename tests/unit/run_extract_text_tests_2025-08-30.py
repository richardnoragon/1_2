"""
Comprehensive Test Runner for extract_text.py
Execution Date: 2025-08-30
Framework: pytest with detailed reporting

This script provides:
1. Automated test execution with pytest
2. Comprehensive HTML and JSON reporting
3. Code coverage analysis
4. Detailed execution metrics
5. Error handling and logging
"""

import datetime
import json
import os
import subprocess
import sys
import time
from pathlib import Path


class TestExecutionManager:
    """Manages comprehensive test execution and reporting"""

    def __init__(self):
        self.execution_timestamp = datetime.datetime.now()
        self.test_dir = Path(__file__).parent
        self.project_root = self.test_dir.parent.parent
        self.date_suffix = "2025-08-30"

        # Setup paths
        self.test_file = (
            self.test_dir / f"test_extract_text_{self.date_suffix}.py"
        )
        self.results_dir = self.test_dir

        # Report file paths
        self.html_report = (
            self.results_dir
            / f"result_extract_text_report_{self.date_suffix}.html"
        )
        self.json_report = (
            self.results_dir
            / f"result_extract_text_json_{self.date_suffix}.json"
        )
        self.coverage_html = (
            self.results_dir
            / f"result_extract_text_coverage_{self.date_suffix}"
        )
        self.coverage_json = (
            self.results_dir
            / f"result_extract_text_coverage_{self.date_suffix}.json"
        )
        self.execution_log = (
            self.results_dir
            / f"result_extract_text_execution_log_{self.date_suffix}.txt"
        )

        print(
            f"Test Execution Manager initialized at {self.execution_timestamp}"
        )
        print(f"Test directory: {self.test_dir}")
        print(f"Project root: {self.project_root}")

    def setup_environment(self):
        """Setup test environment and dependencies"""
        print("\n" + "=" * 80)
        print("SETTING UP TEST ENVIRONMENT")
        print("=" * 80)

        # Add project root to Python path
        sys.path.insert(0, str(self.project_root))

        # Ensure test directory exists
        self.test_dir.mkdir(parents=True, exist_ok=True)

        # Install required packages if not available
        required_packages = [
            "pytest",
            "pytest-html",
            "pytest-json-report",
            "pytest-cov",
            "PyQt5",
        ]

        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
                print(f"✓ {package} is available")
            except ImportError:
                print(f"⚠ {package} not found - attempting to install...")
                try:
                    subprocess.check_call(
                        [sys.executable, "-m", "pip", "install", package]
                    )
                    print(f"✓ {package} installed successfully")
                except subprocess.CalledProcessError:
                    print(f"✗ Failed to install {package}")

        print("Environment setup completed")

    def execute_tests(self):
        """Execute comprehensive tests with detailed reporting"""
        print("\n" + "=" * 80)
        print("EXECUTING COMPREHENSIVE TESTS")
        print("=" * 80)

        start_time = time.time()

        # Build pytest command with comprehensive reporting
        pytest_cmd = [
            sys.executable,
            "-m",
            "pytest",
            str(self.test_file),
            "-v",  # Verbose output
            "--tb=long",  # Detailed traceback
            "--capture=no",  # Don't capture output
            "--durations=10",  # Show 10 slowest tests
            "--html=" + str(self.html_report),  # HTML report
            "--self-contained-html",  # Self-contained HTML
            "--json-report",  # Enable JSON reporting
            "--json-report-file=" + str(self.json_report),  # JSON report file
            "--cov=extract_text",  # Coverage for extract_text module
            "--cov-report=html:" + str(self.coverage_html),  # HTML coverage
            "--cov-report=json:" + str(self.coverage_json),  # JSON coverage
            "--cov-report=term-missing",  # Terminal coverage with missing lines
            "--maxfail=10",  # Stop after 10 failures
            "--strict-markers",  # Strict marker checking
        ]

        print(f"Executing command: {' '.join(pytest_cmd)}")
        print(f"Start time: {datetime.datetime.now().isoformat()}")

        # Execute tests and capture output
        try:
            with open(self.execution_log, "w", encoding="utf-8") as log_file:
                log_file.write(
                    f"Test Execution Log - {self.execution_timestamp.isoformat()}\n"
                )
                log_file.write("=" * 80 + "\n")
                log_file.write(f"Command: {' '.join(pytest_cmd)}\n")
                log_file.write("=" * 80 + "\n\n")

                result = subprocess.run(
                    pytest_cmd,
                    cwd=str(self.project_root),
                    capture_output=True,
                    text=True,
                    timeout=300,  # 5 minute timeout
                )

                # Write output to log
                log_file.write("STDOUT:\n")
                log_file.write(result.stdout)
                log_file.write("\n\nSTDERR:\n")
                log_file.write(result.stderr)
                log_file.write(f"\n\nReturn Code: {result.returncode}\n")

                # Also print to console
                print("STDOUT:")
                print(result.stdout)
                if result.stderr:
                    print("\nSTDERR:")
                    print(result.stderr)

                end_time = time.time()
                execution_duration = end_time - start_time

                print(
                    f"\nTest execution completed in {execution_duration:.2f} seconds"
                )
                print(f"End time: {datetime.datetime.now().isoformat()}")
                print(f"Return code: {result.returncode}")

                log_file.write(
                    f"\nExecution Duration: {execution_duration:.2f} seconds\n"
                )
                log_file.write(
                    f"End Time: {datetime.datetime.now().isoformat()}\n"
                )

                return result.returncode == 0, result

        except subprocess.TimeoutExpired:
            print("⚠ Test execution timed out after 5 minutes")
            return False, None
        except Exception as e:
            print(f"✗ Test execution failed with error: {str(e)}")
            return False, None

    def generate_summary_report(self, test_success, test_result):
        """Generate a comprehensive summary report"""
        print("\n" + "=" * 80)
        print("GENERATING SUMMARY REPORT")
        print("=" * 80)

        summary_file = (
            self.results_dir
            / f"result_extract_text_summary_{self.date_suffix}.json"
        )

        summary = {
            "execution_metadata": {
                "timestamp": self.execution_timestamp.isoformat(),
                "date": self.date_suffix,
                "target_module": "extract_text.py",
                "test_framework": "pytest",
                "python_version": sys.version,
                "platform": sys.platform,
            },
            "execution_results": {
                "success": test_success,
                "return_code": test_result.returncode if test_result else -1,
                "execution_duration": None,  # Will be calculated from logs
            },
            "generated_files": {
                "test_file": str(self.test_file),
                "html_report": str(self.html_report),
                "json_report": str(self.json_report),
                "coverage_html": str(self.coverage_html),
                "coverage_json": str(self.coverage_json),
                "execution_log": str(self.execution_log),
                "summary_report": str(summary_file),
            },
            "file_status": {},
        }

        # Check which files were actually generated
        for file_type, file_path in summary["generated_files"].items():
            if file_type == "summary_report":
                continue
            path_obj = Path(file_path)
            summary["file_status"][file_type] = {
                "exists": path_obj.exists(),
                "size": path_obj.stat().st_size if path_obj.exists() else 0,
                "modified": (
                    path_obj.stat().st_mtime if path_obj.exists() else None
                ),
            }

        # Try to read JSON test report for additional details
        if self.json_report.exists():
            try:
                with open(self.json_report, "r", encoding="utf-8") as f:
                    test_data = json.load(f)
                    summary["test_statistics"] = {
                        "total_tests": test_data.get("summary", {}).get(
                            "total", 0
                        ),
                        "passed": test_data.get("summary", {}).get(
                            "passed", 0
                        ),
                        "failed": test_data.get("summary", {}).get(
                            "failed", 0
                        ),
                        "skipped": test_data.get("summary", {}).get(
                            "skipped", 0
                        ),
                        "errors": test_data.get("summary", {}).get("error", 0),
                        "duration": test_data.get("duration", 0),
                    }
                    summary["execution_results"]["execution_duration"] = (
                        test_data.get("duration", 0)
                    )
            except Exception as e:
                summary["test_statistics"] = {
                    "error": f"Failed to parse JSON report: {str(e)}"
                }

        # Try to read coverage report
        if self.coverage_json.exists():
            try:
                with open(self.coverage_json, "r", encoding="utf-8") as f:
                    coverage_data = json.load(f)
                    summary["coverage_statistics"] = {
                        "total_statements": coverage_data.get(
                            "totals", {}
                        ).get("num_statements", 0),
                        "covered_statements": coverage_data.get(
                            "totals", {}
                        ).get("covered_lines", 0),
                        "coverage_percentage": coverage_data.get(
                            "totals", {}
                        ).get("percent_covered", 0),
                        "missing_lines": coverage_data.get("totals", {}).get(
                            "missing_lines", 0
                        ),
                    }
            except Exception as e:
                summary["coverage_statistics"] = {
                    "error": f"Failed to parse coverage report: {str(e)}"
                }

        # Write summary report
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, default=str)

        print(f"Summary report generated: {summary_file}")

        # Print summary to console
        print("\nEXECUTION SUMMARY:")
        print(f"✓ Test file created: {self.test_file.name}")
        print(f"✓ Execution log: {self.execution_log.name}")

        if summary["file_status"].get("html_report", {}).get("exists"):
            print(f"✓ HTML report: {self.html_report.name}")
        else:
            print(f"⚠ HTML report not generated")

        if summary["file_status"].get("json_report", {}).get("exists"):
            print(f"✓ JSON report: {self.json_report.name}")
        else:
            print(f"⚠ JSON report not generated")

        if summary["file_status"].get("coverage_html", {}).get("exists"):
            print(f"✓ Coverage HTML: {self.coverage_html.name}")
        else:
            print(f"⚠ Coverage HTML not generated")

        if "test_statistics" in summary:
            stats = summary["test_statistics"]
            if "error" not in stats:
                print(f"\nTEST STATISTICS:")
                print(f"  Total tests: {stats.get('total_tests', 'N/A')}")
                print(f"  Passed: {stats.get('passed', 'N/A')}")
                print(f"  Failed: {stats.get('failed', 'N/A')}")
                print(f"  Skipped: {stats.get('skipped', 'N/A')}")
                print(f"  Duration: {stats.get('duration', 'N/A')} seconds")

        if "coverage_statistics" in summary:
            cov = summary["coverage_statistics"]
            if "error" not in cov:
                print(f"\nCOVERAGE STATISTICS:")
                print(f"  Coverage: {cov.get('coverage_percentage', 'N/A')}%")
                print(
                    f"  Total statements: {cov.get('total_statements', 'N/A')}"
                )
                print(
                    f"  Covered statements: {cov.get('covered_statements', 'N/A')}"
                )

        return summary

    def run_complete_test_suite(self):
        """Run the complete test suite with all reporting"""
        print("COMPREHENSIVE TEST EXECUTION FOR extract_text.py")
        print("Date: 2025-08-30")
        print("Framework: pytest")
        print("=" * 80)

        try:
            # Setup environment
            self.setup_environment()

            # Execute tests
            success, result = self.execute_tests()

            # Generate summary
            summary = self.generate_summary_report(success, result)

            print("\n" + "=" * 80)
            print("TEST EXECUTION COMPLETED")
            print("=" * 80)

            if success:
                print("✓ All tests completed successfully!")
            else:
                print("⚠ Some tests failed or execution encountered issues")

            print(f"\nAll output files are located in: {self.results_dir}")
            print(
                "Check the HTML report for detailed test results and coverage information."
            )

            return success

        except Exception as e:
            print(f"✗ Fatal error during test execution: {str(e)}")
            return False


def main():
    """Main entry point for test execution"""
    manager = TestExecutionManager()
    success = manager.run_complete_test_suite()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
