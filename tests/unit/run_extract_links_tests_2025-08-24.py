#!/usr/bin/env python3
"""
Test Runner for extract_links.py
Runner file: run_extract_links_tests_2025-08-24.py
Created: 2025-08-24
Target: Execute comprehensive tests for extract_links.py with detailed reporting

This script executes the test suite for extract_links.py and generates:
- HTML test reports
- JSON test results
- Coverage reports (HTML and JSON)
- JUnit XML reports
- Execution summary with timestamp
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# Constants
TEST_DATE = "2025-08-24"
TARGET_MODULE = "extract_links"
TEST_FILE = f"test_{TARGET_MODULE}_{TEST_DATE}.py"
CONFIG_FILE = f"pytest_{TARGET_MODULE}_{TEST_DATE}.ini"
RESULTS_PREFIX = f"result_{TARGET_MODULE}"


class TestRunner:
    """Test runner class for extract_links.py testing"""

    def __init__(self):
        self.start_time = datetime.now()
        self.test_dir = Path(__file__).parent
        self.results = {
            "timestamp": self.start_time.isoformat(),
            "test_date": TEST_DATE,
            "target_module": TARGET_MODULE,
            "status": "not_started",
            "execution_time": 0,
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "coverage_percentage": 0,
            "reports_generated": [],
            "errors": [],
        }

    def setup_environment(self):
        """Setup test environment and directories"""
        print(f"Setting up test environment for {TARGET_MODULE}...")

        # Create logs directory if it doesn't exist
        logs_dir = self.test_dir / "logs"
        logs_dir.mkdir(exist_ok=True)

        # Verify test files exist
        test_file_path = self.test_dir / TEST_FILE
        config_file_path = self.test_dir / CONFIG_FILE

        if not test_file_path.exists():
            raise FileNotFoundError(f"Test file not found: {TEST_FILE}")

        if not config_file_path.exists():
            raise FileNotFoundError(f"Config file not found: {CONFIG_FILE}")

        print("✓ Environment setup completed")

    def install_dependencies(self):
        """Install required test dependencies"""
        print("Installing test dependencies...")

        dependencies = [
            "pytest>=6.2.0",
            "pytest-html>=3.1.0",
            "pytest-json-report>=1.5.0",
            "pytest-cov>=3.0.0",
            "pytest-timeout>=2.1.0",
            "PyQt5>=5.15.0",
            "pikepdf>=5.0.0",
        ]

        for dep in dependencies:
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", dep],
                    capture_output=True,
                    text=True,
                    timeout=60,
                )

                if result.returncode != 0:
                    print(f"Warning: Failed to install {dep}")
                    self.results["errors"].append(
                        f"Dependency installation failed: {dep}"
                    )

            except subprocess.TimeoutExpired:
                print(f"Warning: Timeout installing {dep}")
                self.results["errors"].append(
                    f"Dependency installation timeout: {dep}"
                )

        print("✓ Dependencies installation completed")

    def run_tests(self):
        """Execute the test suite"""
        print(f"Running tests for {TARGET_MODULE}...")

        # Build pytest command
        pytest_cmd = [
            sys.executable,
            "-m",
            "pytest",
            "-c",
            CONFIG_FILE,
            TEST_FILE,
            "--tb=short",
            "-v",
        ]

        try:
            # Execute tests
            result = subprocess.run(
                pytest_cmd,
                cwd=self.test_dir,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutes timeout
            )

            self.results["return_code"] = result.returncode
            self.results["stdout"] = result.stdout
            self.results["stderr"] = result.stderr

            if result.returncode == 0:
                self.results["status"] = "passed"
                print("✓ All tests passed!")
            else:
                self.results["status"] = "failed"
                print(f"✗ Tests failed with return code: {result.returncode}")

        except subprocess.TimeoutExpired:
            self.results["status"] = "timeout"
            self.results["errors"].append("Test execution timeout")
            print("✗ Test execution timed out")

        except Exception as e:
            self.results["status"] = "error"
            self.results["errors"].append(f"Test execution error: {str(e)}")
            print(f"✗ Test execution error: {e}")

    def parse_results(self):
        """Parse test results from generated reports"""
        print("Parsing test results...")

        # Parse JSON report if available
        json_report_path = self.test_dir / f"{RESULTS_PREFIX}_{TEST_DATE}.json"
        if json_report_path.exists():
            try:
                with open(json_report_path, "r") as f:
                    json_data = json.load(f)

                summary = json_data.get("summary", {})
                self.results["tests_run"] = summary.get("total", 0)
                self.results["tests_passed"] = summary.get("passed", 0)
                self.results["tests_failed"] = summary.get("failed", 0)
                self.results["test_duration"] = json_data.get("duration", 0)

                self.results["reports_generated"].append("JSON report")

            except Exception as e:
                self.results["errors"].append(
                    f"Failed to parse JSON report: {str(e)}"
                )

        # Parse coverage JSON if available
        coverage_json_path = (
            self.test_dir / f"{RESULTS_PREFIX}_coverage_{TEST_DATE}.json"
        )
        if coverage_json_path.exists():
            try:
                with open(coverage_json_path, "r") as f:
                    coverage_data = json.load(f)

                totals = coverage_data.get("totals", {})
                if "percent_covered" in totals:
                    self.results["coverage_percentage"] = totals[
                        "percent_covered"
                    ]

                self.results["reports_generated"].append("Coverage JSON")

            except Exception as e:
                self.results["errors"].append(
                    f"Failed to parse coverage JSON: {str(e)}"
                )

        # Check for other generated reports
        report_files = [
            f"{RESULTS_PREFIX}_{TEST_DATE}.html",
            f"{RESULTS_PREFIX}_{TEST_DATE}_junit.xml",
            f"{RESULTS_PREFIX}_coverage_{TEST_DATE}/index.html",
        ]

        for report_file in report_files:
            if (self.test_dir / report_file).exists():
                self.results["reports_generated"].append(report_file)

        print(
            f"✓ Found {len(self.results['reports_generated'])} generated reports"
        )

    def generate_summary(self):
        """Generate execution summary"""
        print("Generating execution summary...")

        end_time = datetime.now()
        self.results["execution_time"] = (
            end_time - self.start_time
        ).total_seconds()
        self.results["end_timestamp"] = end_time.isoformat()

        # Create summary text
        summary_lines = [
            f"Extract Links Testing Execution Summary - {TEST_DATE}",
            "=" * 60,
            f"Execution Start: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Execution End: {end_time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Total Duration: {self.results['execution_time']:.2f} seconds",
            "",
            f"Target Module: {TARGET_MODULE}",
            f"Test Status: {self.results['status'].upper()}",
            f"Tests Run: {self.results['tests_run']}",
            f"Tests Passed: {self.results['tests_passed']}",
            f"Tests Failed: {self.results['tests_failed']}",
            f"Coverage: {self.results['coverage_percentage']:.1f}%",
            "",
            "Generated Reports:",
        ]

        for report in self.results["reports_generated"]:
            summary_lines.append(f"  - {report}")

        if self.results["errors"]:
            summary_lines.extend(
                [
                    "",
                    "Errors Encountered:",
                ]
            )
            for error in self.results["errors"]:
                summary_lines.append(f"  - {error}")

        summary_text = "\n".join(summary_lines)

        # Write summary to file
        summary_file = (
            self.test_dir
            / f"{RESULTS_PREFIX}_execution_summary_{TEST_DATE}.txt"
        )
        with open(summary_file, "w") as f:
            f.write(summary_text)

        # Write detailed results to JSON
        results_file = (
            self.test_dir
            / f"{RESULTS_PREFIX}_detailed_results_{TEST_DATE}.json"
        )
        with open(results_file, "w") as f:
            json.dump(self.results, f, indent=2)

        print(f"✓ Summary written to: {summary_file}")
        print(f"✓ Detailed results written to: {results_file}")

        return summary_text

    def print_summary(self):
        """Print summary to console"""
        summary = self.generate_summary()
        print("\n" + summary)

    def run_complete_test_suite(self):
        """Run the complete test suite with all steps"""
        print(f"Starting comprehensive test execution for {TARGET_MODULE}")
        print(f"Timestamp: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 60)

        try:
            self.setup_environment()
            self.install_dependencies()
            self.run_tests()
            self.parse_results()
            self.print_summary()

            return self.results["status"] in [
                "passed",
                "failed",
            ]  # True if tests ran

        except Exception as e:
            self.results["status"] = "setup_error"
            self.results["errors"].append(f"Setup error: {str(e)}")
            print(f"✗ Setup failed: {e}")
            self.print_summary()
            return False


def main():
    """Main execution function"""
    runner = TestRunner()

    try:
        success = runner.run_complete_test_suite()
        exit_code = 0 if success else 1

    except KeyboardInterrupt:
        print("\n✗ Test execution interrupted by user")
        runner.results["status"] = "interrupted"
        runner.print_summary()
        exit_code = 2

    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        runner.results["status"] = "unexpected_error"
        runner.results["errors"].append(f"Unexpected error: {str(e)}")
        runner.print_summary()
        exit_code = 3

    print(f"\nTest runner completed with exit code: {exit_code}")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
