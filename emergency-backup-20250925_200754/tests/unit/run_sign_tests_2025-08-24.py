#!/usr/bin/env python3
"""
Automated Test Runner for PDF Sign Module
Created: 2025-08-24
Target: sign.py comprehensive testing

This script executes comprehensive unit tests for the PDF signing module
and generates detailed reports with timestamps and execution summaries.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


class SignTestRunner:
    """Test runner for PDF sign module with comprehensive reporting"""

    def __init__(self):
        self.start_time = datetime.now()
        self.test_date = self.start_time.strftime("%Y-%m-%d")
        self.test_timestamp = self.start_time.strftime("%Y-%m-%d_%H-%M-%S")

        # Define paths
        self.project_root = Path(__file__).parent.parent.parent
        self.test_dir = Path(__file__).parent
        self.reports_dir = self.test_dir

        # Test configuration
        self.config_file = self.test_dir / f"pytest_sign_{self.test_date}.ini"
        self.test_file = self.test_dir / f"test_sign_{self.test_date}.py"
        self.requirements_file = (
            self.test_dir / f"requirements_test_sign_{self.test_date}.txt"
        )

        # Output files
        self.html_report = (
            self.reports_dir / f"result_sign_{self.test_date}.html"
        )
        self.json_report = (
            self.reports_dir / f"result_sign_{self.test_date}.json"
        )
        self.junit_report = (
            self.reports_dir / f"result_sign_{self.test_date}_junit.xml"
        )
        self.coverage_html = (
            self.reports_dir / f"result_sign_coverage_{self.test_date}"
        )
        self.coverage_json = (
            self.reports_dir / f"result_sign_coverage_{self.test_date}.json"
        )
        self.execution_summary = (
            self.reports_dir
            / f"result_sign_execution_summary_{self.test_date}.txt"
        )

    def check_dependencies(self):
        """Check if required dependencies are installed"""
        print("Checking test dependencies...")

        try:
            # Check if requirements file exists
            if not self.requirements_file.exists():
                print(
                    f"Warning: Requirements file not found: {self.requirements_file}"
                )
                return False

            # Try to import key dependencies
            dependencies = [
                "pytest",
                "pytest_html",
                "pytest_cov",
                "pikepdf",
                "fitz",
                "PIL",
                "OpenSSL",
            ]

            missing_deps = []
            for dep in dependencies:
                try:
                    if dep == "fitz":
                        import fitz
                    elif dep == "PIL":
                        import PIL
                    elif dep == "OpenSSL":
                        import OpenSSL
                    else:
                        __import__(dep)
                    print(f"✓ {dep}")
                except ImportError:
                    missing_deps.append(dep)
                    print(f"✗ {dep}")

            if missing_deps:
                print(f"\nMissing dependencies: {', '.join(missing_deps)}")
                print(f"Install with: pip install -r {self.requirements_file}")
                return False

            print("All dependencies available!")
            return True

        except Exception as e:
            print(f"Error checking dependencies: {e}")
            return False

    def install_dependencies(self):
        """Install test dependencies"""
        print("Installing test dependencies...")

        if not self.requirements_file.exists():
            print(f"Requirements file not found: {self.requirements_file}")
            return False

        try:
            cmd = [
                sys.executable,
                "-m",
                "pip",
                "install",
                "-r",
                str(self.requirements_file),
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                print("Dependencies installed successfully!")
                return True
            else:
                print(f"Error installing dependencies: {result.stderr}")
                return False

        except Exception as e:
            print(f"Error installing dependencies: {e}")
            return False

    def run_tests(self, install_deps=False, verbose=True):
        """Execute the test suite"""
        print(f"\n{'='*60}")
        print(f"PDF Sign Module Test Execution")
        print(f"Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")

        # Check dependencies
        if not self.check_dependencies():
            if install_deps:
                if not self.install_dependencies():
                    print("Failed to install dependencies. Aborting test run.")
                    return False
            else:
                print(
                    "Dependencies missing. Use --install-deps to install them."
                )
                return False

        # Verify test files exist
        if not self.test_file.exists():
            print(f"Test file not found: {self.test_file}")
            return False

        if not self.config_file.exists():
            print(f"Config file not found: {self.config_file}")
            return False

        # Prepare pytest command
        pytest_cmd = [
            sys.executable,
            "-m",
            "pytest",
            str(self.test_file),
            f"--config-file={self.config_file}",
            f"--html={self.html_report}",
            "--self-contained-html",
            f"--json-report",
            f"--json-report-file={self.json_report}",
            f"--junit-xml={self.junit_report}",
            f"--cov=src.tools.pdf_tools.pdf_basic_operations.sign",
            f"--cov-report=html:{self.coverage_html}",
            f"--cov-report=json:{self.coverage_json}",
            "--cov-report=term-missing",
            "--tb=short",
        ]

        if verbose:
            pytest_cmd.append("-v")

        print(f"\nExecuting: {' '.join(pytest_cmd)}")
        print(f"Working directory: {os.getcwd()}")

        # Execute tests
        start_exec_time = time.time()
        try:
            result = subprocess.run(
                pytest_cmd,
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=600,  # 10 minute timeout
            )

            exec_duration = time.time() - start_exec_time

            # Display results
            print(f"\n{'-'*50}")
            print("TEST EXECUTION RESULTS")
            print(f"{'-'*50}")
            print(f"Exit code: {result.returncode}")
            print(f"Duration: {exec_duration:.2f} seconds")
            print(f"\nSTDOUT:\n{result.stdout}")

            if result.stderr:
                print(f"\nSTDERR:\n{result.stderr}")

            # Generate execution summary
            self.generate_execution_summary(result, exec_duration)

            # Display report locations
            self.display_report_locations()

            return result.returncode == 0

        except subprocess.TimeoutExpired:
            print("Test execution timed out after 10 minutes")
            return False
        except Exception as e:
            print(f"Error executing tests: {e}")
            return False

    def generate_execution_summary(self, result, duration):
        """Generate detailed execution summary"""
        summary_data = {
            "execution_info": {
                "timestamp": self.start_time.isoformat(),
                "date": self.test_date,
                "duration_seconds": round(duration, 2),
                "exit_code": result.returncode,
                "success": result.returncode == 0,
            },
            "test_files": {
                "test_file": str(self.test_file),
                "config_file": str(self.config_file),
                "requirements_file": str(self.requirements_file),
            },
            "output_files": {
                "html_report": str(self.html_report),
                "json_report": str(self.json_report),
                "junit_report": str(self.junit_report),
                "coverage_html": str(self.coverage_html),
                "coverage_json": str(self.coverage_json),
            },
            "command_output": {
                "stdout": result.stdout,
                "stderr": result.stderr,
            },
        }

        # Parse JSON report if available
        if self.json_report.exists():
            try:
                with open(self.json_report, "r") as f:
                    json_data = json.load(f)
                    summary_data["test_results"] = {
                        "total_tests": json_data.get("summary", {}).get(
                            "total", 0
                        ),
                        "passed": json_data.get("summary", {}).get(
                            "passed", 0
                        ),
                        "failed": json_data.get("summary", {}).get(
                            "failed", 0
                        ),
                        "skipped": json_data.get("summary", {}).get(
                            "skipped", 0
                        ),
                        "errors": json_data.get("summary", {}).get("error", 0),
                    }
            except Exception as e:
                summary_data["json_parse_error"] = str(e)

        # Write text summary
        with open(self.execution_summary, "w") as f:
            f.write(f"PDF Sign Module Test Execution Summary\n")
            f.write(f"{'='*50}\n\n")
            f.write(
                f"Execution Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            )
            f.write(f"Duration: {duration:.2f} seconds\n")
            f.write(f"Exit Code: {result.returncode}\n")
            f.write(
                f"Success: {'Yes' if result.returncode == 0 else 'No'}\n\n"
            )

            if "test_results" in summary_data:
                tr = summary_data["test_results"]
                f.write(f"Test Results:\n")
                f.write(f"  Total: {tr['total_tests']}\n")
                f.write(f"  Passed: {tr['passed']}\n")
                f.write(f"  Failed: {tr['failed']}\n")
                f.write(f"  Skipped: {tr['skipped']}\n")
                f.write(f"  Errors: {tr['errors']}\n\n")

            f.write(f"Output Files:\n")
            f.write(f"  HTML Report: {self.html_report}\n")
            f.write(f"  JSON Report: {self.json_report}\n")
            f.write(f"  JUnit XML: {self.junit_report}\n")
            f.write(f"  Coverage HTML: {self.coverage_html}\n")
            f.write(f"  Coverage JSON: {self.coverage_json}\n\n")

            f.write(f"Command Output:\n")
            f.write(f"{'-'*20}\n")
            f.write(f"{result.stdout}\n")

            if result.stderr:
                f.write(f"\nError Output:\n")
                f.write(f"{'-'*20}\n")
                f.write(f"{result.stderr}\n")

        # Write JSON summary
        json_summary_file = (
            self.reports_dir / f"result_sign_summary_{self.test_date}.json"
        )
        with open(json_summary_file, "w") as f:
            json.dump(summary_data, f, indent=2)

        print(f"\nExecution summary written to: {self.execution_summary}")
        print(f"JSON summary written to: {json_summary_file}")

    def display_report_locations(self):
        """Display locations of generated reports"""
        print(f"\n{'='*60}")
        print("GENERATED REPORTS")
        print(f"{'='*60}")

        reports = [
            ("HTML Test Report", self.html_report),
            ("JSON Test Report", self.json_report),
            ("JUnit XML Report", self.junit_report),
            ("Coverage HTML Report", self.coverage_html / "index.html"),
            ("Coverage JSON Report", self.coverage_json),
            ("Execution Summary", self.execution_summary),
        ]

        for name, path in reports:
            if isinstance(path, Path) and path.exists():
                print(f"✓ {name}: {path}")
            elif isinstance(path, Path):
                print(f"✗ {name}: {path} (not found)")
            else:
                print(f"? {name}: {path}")

        print(f"\nTo view HTML reports, open them in a web browser:")
        print(f"  {self.html_report}")
        if (self.coverage_html / "index.html").exists():
            print(f"  {self.coverage_html / 'index.html'}")

    def clean_previous_reports(self):
        """Clean up previous test reports"""
        print("Cleaning previous reports...")

        patterns = [
            f"result_sign_{self.test_date}.*",
            f"result_sign_coverage_{self.test_date}*",
        ]

        cleaned = 0
        for pattern in patterns:
            for file_path in self.reports_dir.glob(pattern):
                try:
                    if file_path.is_dir():
                        shutil.rmtree(file_path)
                    else:
                        file_path.unlink()
                    cleaned += 1
                    print(f"Removed: {file_path}")
                except Exception as e:
                    print(f"Failed to remove {file_path}: {e}")

        print(f"Cleaned {cleaned} previous report files/directories")


def main():
    """Main function to run the test suite"""
    parser = argparse.ArgumentParser(description="Run PDF Sign module tests")
    parser.add_argument(
        "--install-deps",
        action="store_true",
        help="Install test dependencies if missing",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean previous reports before running",
    )
    parser.add_argument(
        "--quiet", action="store_true", help="Run tests in quiet mode"
    )

    args = parser.parse_args()

    # Create test runner
    runner = SignTestRunner()

    # Clean previous reports if requested
    if args.clean:
        runner.clean_previous_reports()

    # Run tests
    success = runner.run_tests(
        install_deps=args.install_deps, verbose=not args.quiet
    )

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
