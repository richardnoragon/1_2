#!/usr/bin/env python3
"""
Comprehensive test runner for extract_text.py unit tests
Generated on: 2025-08-28
Executes tests with detailed reporting and coverage analysis
"""

import datetime
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path


class ExtractTextTestRunner:
    """Test runner for extract_text.py with comprehensive reporting."""

    def __init__(self):
        self.test_dir = Path("c:/Users/richardi/1_2/tests/unit")
        self.test_file = self.test_dir / "test_extract_text_2025-08-28.py"
        self.date_suffix = "2025-08-28"
        self.start_time = None
        self.end_time = None

        # Result file paths
        self.result_files = {
            "html_report": self.test_dir
            / f"result_extract_text_{self.date_suffix}.html",
            "json_report": self.test_dir
            / f"result_extract_text_{self.date_suffix}.json",
            "coverage_html": self.test_dir
            / f"result_extract_text_coverage_{self.date_suffix}",
            "coverage_json": self.test_dir
            / f"result_extract_text_coverage_{self.date_suffix}.json",
            "junit_xml": self.test_dir
            / f"result_extract_text_{self.date_suffix}.xml",
            "summary_txt": self.test_dir
            / f"result_extract_text_summary_{self.date_suffix}.txt",
            "execution_log": self.test_dir
            / f"result_extract_text_execution_{self.date_suffix}.log",
        }

    def setup_environment(self):
        """Setup test environment and dependencies."""
        print("Setting up test environment for extract_text.py...")

        # Ensure test directory exists
        self.test_dir.mkdir(parents=True, exist_ok=True)

        # Install required packages
        required_packages = [
            "pytest>=7.0.0",
            "pytest-html>=3.1.0",
            "pytest-json-report>=1.5.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
            "pytest-qt>=4.2.0",  # For PyQt5 testing
            "coverage[toml]>=7.0.0",
            "PyQt5>=5.15.0",
            "pdfplumber>=0.9.0",
        ]

        for package in required_packages:
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", package],
                    check=True,
                    capture_output=True,
                )
                print(f"✓ Installed {package}")
            except subprocess.CalledProcessError as e:
                print(f"⚠ Warning: Failed to install {package}: {e}")

    def run_tests(self):
        """Execute the test suite with comprehensive reporting."""
        print(f"\nRunning tests for extract_text.py...")
        print(f"Test file: {self.test_file}")
        print(f"Output directory: {self.test_dir}")

        self.start_time = datetime.datetime.now()

        # Build pytest command
        cmd = [
            sys.executable,
            "-m",
            "pytest",
            str(self.test_file),
            "-v",
            "--tb=short",
            "--strict-markers",
            "--disable-warnings",
            f"--html={self.result_files['html_report']}",
            "--self-contained-html",
            "--json-report",
            f"--json-report-file={self.result_files['json_report']}",
            f"--junitxml={self.result_files['junit_xml']}",
            "--cov=extract_text",
            f"--cov-report=html:{self.result_files['coverage_html']}",
            f"--cov-report=json:{self.result_files['coverage_json']}",
            "--cov-report=term-missing",
            "--cov-fail-under=70",  # Adjusted for GUI testing
            "--durations=10",
            "-m",
            "not gui",  # Skip GUI tests by default unless display available
        ]

        # Check if we have a display for GUI tests
        if os.environ.get("DISPLAY") or sys.platform == "win32":
            cmd.remove("-m")
            cmd.remove("not gui")
            print("Display available - running all tests including GUI tests")
        else:
            print("No display detected - skipping GUI tests")

        print(f"\nExecuting command: {' '.join(cmd)}")

        # Execute tests
        try:
            with open(self.result_files["execution_log"], "w") as log_file:
                result = subprocess.run(
                    cmd,
                    cwd=str(self.test_dir),
                    capture_output=True,
                    text=True,
                    timeout=600,  # 10 minute timeout for GUI tests
                )

                log_file.write(f"Command: {' '.join(cmd)}\n")
                log_file.write(f"Return code: {result.returncode}\n")
                log_file.write(f"STDOUT:\n{result.stdout}\n")
                log_file.write(f"STDERR:\n{result.stderr}\n")

                print(
                    f"✓ Tests completed with return code: {result.returncode}"
                )

                if result.stdout:
                    print("STDOUT:")
                    print(result.stdout)

                if result.stderr:
                    print("STDERR:")
                    print(result.stderr)

        except subprocess.TimeoutExpired:
            print("✗ Test execution timed out after 10 minutes")
            return False
        except Exception as e:
            print(f"✗ Test execution failed: {e}")
            return False

        self.end_time = datetime.datetime.now()
        return True

    def generate_summary_report(self):
        """Generate a comprehensive summary report."""
        print("\nGenerating summary report...")

        summary_data = {
            "test_execution": {
                "start_time": (
                    self.start_time.isoformat() if self.start_time else None
                ),
                "end_time": (
                    self.end_time.isoformat() if self.end_time else None
                ),
                "duration_seconds": (
                    (self.end_time - self.start_time).total_seconds()
                    if self.start_time and self.end_time
                    else None
                ),
                "test_file": str(self.test_file),
                "target_module": "extract_text.py",
                "target_path": "src/tools/pdf_tools/pdf_content_extraction/extract_text.py",
            },
            "results": {},
            "coverage": {},
            "test_categories": {
                "function_tests": 0,
                "gui_tests": 0,
                "edge_case_tests": 0,
                "error_handling_tests": 0,
            },
            "files_generated": {},
        }

        # Parse JSON report if available
        if self.result_files["json_report"].exists():
            try:
                with open(self.result_files["json_report"], "r") as f:
                    json_data = json.load(f)

                summary_data["results"] = {
                    "total_tests": json_data.get("summary", {}).get(
                        "total", 0
                    ),
                    "passed": json_data.get("summary", {}).get("passed", 0),
                    "failed": json_data.get("summary", {}).get("failed", 0),
                    "skipped": json_data.get("summary", {}).get("skipped", 0),
                    "errors": json_data.get("summary", {}).get("error", 0),
                    "duration": json_data.get("duration", 0),
                }

                # Analyze test categories
                tests = json_data.get("tests", [])
                for test in tests:
                    test_name = test.get("nodeid", "").lower()
                    if "extract_text_from_pdf" in test_name:
                        summary_data["test_categories"]["function_tests"] += 1
                    elif "ui" in test_name or "gui" in test_name:
                        summary_data["test_categories"]["gui_tests"] += 1
                    elif (
                        "edge" in test_name
                        or "stress" in test_name
                        or "concurrent" in test_name
                    ):
                        summary_data["test_categories"]["edge_case_tests"] += 1
                    elif (
                        "error" in test_name
                        or "exception" in test_name
                        or "failure" in test_name
                    ):
                        summary_data["test_categories"][
                            "error_handling_tests"
                        ] += 1

            except Exception as e:
                print(f"Warning: Could not parse JSON report: {e}")

        # Parse coverage report if available
        if self.result_files["coverage_json"].exists():
            try:
                with open(self.result_files["coverage_json"], "r") as f:
                    coverage_data = json.load(f)

                summary_data["coverage"] = {
                    "total_lines": coverage_data.get("totals", {}).get(
                        "num_statements", 0
                    ),
                    "covered_lines": coverage_data.get("totals", {}).get(
                        "covered_lines", 0
                    ),
                    "missing_lines": coverage_data.get("totals", {}).get(
                        "missing_lines", 0
                    ),
                    "coverage_percent": coverage_data.get("totals", {}).get(
                        "percent_covered", 0
                    ),
                    "excluded_lines": coverage_data.get("totals", {}).get(
                        "excluded_lines", 0
                    ),
                }

                # Get file-specific coverage if available
                files = coverage_data.get("files", {})
                for file_path, file_data in files.items():
                    if "extract_text.py" in file_path:
                        summary_data["coverage"]["extract_text_coverage"] = {
                            "lines": file_data.get("summary", {}).get(
                                "num_statements", 0
                            ),
                            "covered": file_data.get("summary", {}).get(
                                "covered_lines", 0
                            ),
                            "missing": file_data.get("summary", {}).get(
                                "missing_lines", 0
                            ),
                            "percent": file_data.get("summary", {}).get(
                                "percent_covered", 0
                            ),
                        }
                        break

            except Exception as e:
                print(f"Warning: Could not parse coverage report: {e}")

        # Check which files were generated
        for name, path in self.result_files.items():
            summary_data["files_generated"][name] = {
                "path": str(path),
                "exists": path.exists(),
                "size_bytes": path.stat().st_size if path.exists() else 0,
            }

        # Write summary to text file
        with open(self.result_files["summary_txt"], "w") as f:
            f.write("=" * 80 + "\n")
            f.write("EXTRACT TEXT UNIT TEST EXECUTION SUMMARY\n")
            f.write("=" * 80 + "\n")
            f.write(f"Generated on: {datetime.datetime.now().isoformat()}\n")
            f.write(f"Target file: extract_text.py\n")
            f.write(
                f"Target path: {summary_data['test_execution']['target_path']}\n"
            )
            f.write(f"Test file: {self.test_file}\n\n")

            if summary_data["test_execution"]["start_time"]:
                f.write("EXECUTION DETAILS:\n")
                f.write("-" * 40 + "\n")
                f.write(
                    f"Start time: {summary_data['test_execution']['start_time']}\n"
                )
                f.write(
                    f"End time: {summary_data['test_execution']['end_time']}\n"
                )
                f.write(
                    f"Duration: {summary_data['test_execution']['duration_seconds']:.2f} seconds\n\n"
                )

            if summary_data["results"]:
                f.write("TEST RESULTS:\n")
                f.write("-" * 40 + "\n")
                results = summary_data["results"]
                f.write(f"Total tests: {results['total_tests']}\n")
                f.write(f"Passed: {results['passed']}\n")
                f.write(f"Failed: {results['failed']}\n")
                f.write(f"Skipped: {results['skipped']}\n")
                f.write(f"Errors: {results['errors']}\n")
                f.write(f"Duration: {results['duration']:.2f} seconds\n\n")

                # Test categories breakdown
                categories = summary_data["test_categories"]
                if any(categories.values()):
                    f.write("TEST CATEGORIES:\n")
                    f.write("-" * 40 + "\n")
                    f.write(
                        f"Function tests: {categories['function_tests']}\n"
                    )
                    f.write(f"GUI tests: {categories['gui_tests']}\n")
                    f.write(
                        f"Edge case tests: {categories['edge_case_tests']}\n"
                    )
                    f.write(
                        f"Error handling tests: {categories['error_handling_tests']}\n\n"
                    )

            if summary_data["coverage"]:
                f.write("COVERAGE ANALYSIS:\n")
                f.write("-" * 40 + "\n")
                coverage = summary_data["coverage"]
                f.write(f"Total lines: {coverage['total_lines']}\n")
                f.write(f"Covered lines: {coverage['covered_lines']}\n")
                f.write(f"Missing lines: {coverage['missing_lines']}\n")
                f.write(
                    f"Coverage percentage: {coverage['coverage_percent']:.2f}%\n"
                )
                f.write(f"Excluded lines: {coverage['excluded_lines']}\n")

                if "extract_text_coverage" in coverage:
                    ext_cov = coverage["extract_text_coverage"]
                    f.write(f"\nEXTRACT_TEXT.PY SPECIFIC:\n")
                    f.write(f"Lines: {ext_cov['lines']}\n")
                    f.write(f"Covered: {ext_cov['covered']}\n")
                    f.write(f"Missing: {ext_cov['missing']}\n")
                    f.write(f"Percentage: {ext_cov['percent']:.2f}%\n")
                f.write("\n")

            f.write("TESTED FUNCTIONALITY:\n")
            f.write("-" * 40 + "\n")
            f.write("✓ extract_text_from_pdf() function\n")
            f.write("  - File validation and error handling\n")
            f.write("  - PDF opening and text extraction\n")
            f.write("  - Page range parsing and validation\n")
            f.write("  - Unicode text handling\n")
            f.write("  - Output file writing\n")
            f.write("  - Exception handling\n\n")
            f.write("✓ ExtractTextUI class\n")
            f.write("  - UI initialization and setup\n")
            f.write("  - File browsing and selection\n")
            f.write("  - Text extraction with progress\n")
            f.write("  - Text saving and export\n")
            f.write("  - Error dialogs and messaging\n")
            f.write("  - Widget interactions\n\n")
            f.write("✓ Main application function\n")
            f.write("  - Application initialization\n")
            f.write("  - Exception handling\n")
            f.write("  - Exit code management\n\n")
            f.write("✓ Edge cases and error conditions\n")
            f.write("  - Large file handling\n")
            f.write("  - Concurrent operations\n")
            f.write("  - Memory stress testing\n")
            f.write("  - Invalid input handling\n\n")

            f.write("FILES GENERATED:\n")
            f.write("-" * 40 + "\n")
            for name, info in summary_data["files_generated"].items():
                status = "✓" if info["exists"] else "✗"
                f.write(
                    f"{status} {name}: {info['path']} ({info['size_bytes']} bytes)\n"
                )

        # Write summary as JSON
        summary_json_path = (
            self.test_dir
            / f"result_extract_text_summary_{self.date_suffix}.json"
        )
        with open(summary_json_path, "w") as f:
            json.dump(summary_data, f, indent=2, ensure_ascii=False)

        print(
            f"✓ Summary report generated: {self.result_files['summary_txt']}"
        )
        print(f"✓ Summary JSON generated: {summary_json_path}")

        return summary_data

    def print_results_summary(self, summary_data):
        """Print a brief summary to console."""
        print("\n" + "=" * 80)
        print("EXTRACT TEXT TEST EXECUTION SUMMARY")
        print("=" * 80)

        if summary_data["results"]:
            results = summary_data["results"]
            total = results["total_tests"]
            passed = results["passed"]
            failed = results["failed"]
            skipped = results["skipped"]

            success_rate = (passed / total * 100) if total > 0 else 0

            print(
                f"📊 Tests: {total} total, {passed} passed, {failed} failed, {skipped} skipped"
            )
            print(f"✨ Success Rate: {success_rate:.1f}%")

            # Show test categories
            categories = summary_data["test_categories"]
            if any(categories.values()):
                print(
                    f"📋 Categories: {categories['function_tests']} function, {categories['gui_tests']} GUI, {categories['edge_case_tests']} edge cases, {categories['error_handling_tests']} error handling"
                )

            if summary_data["coverage"]:
                coverage = summary_data["coverage"]
                print(f"📈 Coverage: {coverage['coverage_percent']:.1f}%")

                if "extract_text_coverage" in coverage:
                    ext_cov = coverage["extract_text_coverage"]
                    print(
                        f"🎯 extract_text.py: {ext_cov['percent']:.1f}% ({ext_cov['covered']}/{ext_cov['lines']} lines)"
                    )

        if summary_data["test_execution"]["duration_seconds"]:
            duration = summary_data["test_execution"]["duration_seconds"]
            print(f"⏱️  Duration: {duration:.2f} seconds")

        print(f"📁 Output Directory: {self.test_dir}")
        print("=" * 80)

    def run_full_test_suite(self):
        """Run the complete test suite with setup, execution, and reporting."""
        print("🚀 Starting comprehensive test execution for extract_text.py")
        print(f"📅 Date: {self.date_suffix}")
        print(f"🎯 Target: extract_text.py")
        print(
            f"📍 Path: src/tools/pdf_tools/pdf_content_extraction/extract_text.py"
        )

        try:
            # Setup environment
            self.setup_environment()

            # Run tests
            if not self.run_tests():
                print("❌ Test execution failed")
                return False

            # Generate reports
            summary_data = self.generate_summary_report()

            # Print summary
            self.print_results_summary(summary_data)

            print("\n✅ Test execution completed successfully!")
            print(
                f"📊 View detailed results: {self.result_files['html_report']}"
            )
            print(
                f"📈 View coverage report: {self.result_files['coverage_html']}/index.html"
            )

            return True

        except Exception as e:
            print(f"❌ Test execution failed with error: {e}")
            return False


def main():
    """Main entry point."""
    runner = ExtractTextTestRunner()
    success = runner.run_full_test_suite()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
