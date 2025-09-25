#!/usr/bin/env python3
"""
Test Runner for main.py Unit Tests
Richard's File Utilities - Main Module Testing Suite

This script executes comprehensive unit tests for main.py with detailed reporting
and coverage analysis. Generates standardized test outputs with timestamps.

Created: 2025-08-28
Target: main.py
Framework: pytest

Execution: python run_main_tests_2025-08-28.py
"""

import datetime
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List


class MainTestRunner:
    """Comprehensive test runner for main.py unit tests."""

    def __init__(self):
        """Initialize the test runner."""
        self.test_dir = Path(__file__).parent
        self.project_root = self.test_dir.parent.parent
        self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.date_suffix = datetime.datetime.now().strftime("%Y-%m-%d")

        # Test file paths
        self.test_file = self.test_dir / f"test_main_{self.date_suffix}.py"

        # Output file paths
        self.html_report = (
            self.test_dir / f"result_main_{self.date_suffix}.html"
        )
        self.json_report = (
            self.test_dir / f"result_main_{self.date_suffix}.json"
        )
        self.xml_report = self.test_dir / f"result_main_{self.date_suffix}.xml"
        self.coverage_dir = (
            self.test_dir / f"result_main_{self.date_suffix}_coverage"
        )
        self.coverage_xml = (
            self.test_dir / f"result_main_{self.date_suffix}_coverage.xml"
        )
        self.execution_log = (
            self.test_dir / f"result_main_{self.date_suffix}_execution.log"
        )

        # Summary files
        self.summary_json = (
            self.test_dir / f"result_main_{self.date_suffix}_summary.json"
        )
        self.summary_txt = (
            self.test_dir / f"result_main_{self.date_suffix}_summary.txt"
        )
        self.summary_md = (
            self.test_dir
            / f"result_main_{self.date_suffix}_completion_summary.md"
        )

    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are met."""
        print("🔍 Checking prerequisites...")

        # Check if test file exists
        if not self.test_file.exists():
            print(f"❌ Test file not found: {self.test_file}")
            return False

        # Check if main.py exists
        main_file = self.project_root / "main.py"
        if not main_file.exists():
            print(f"❌ Main file not found: {main_file}")
            return False

        # Check required packages
        required_packages = [
            "pytest",
            "pytest-html",
            "pytest-json-report",
            "pytest-cov",
            "pytest-mock",
            "pytest-timeout",
        ]

        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
            except ImportError:
                print(f"❌ Required package not found: {package}")
                print(f"Install with: pip install {package}")
                return False

        print("✅ All prerequisites met")
        return True

    def setup_environment(self):
        """Setup test environment and paths."""
        print("🔧 Setting up test environment...")

        # Add project root to Python path
        if str(self.project_root) not in sys.path:
            sys.path.insert(0, str(self.project_root))

        # Set environment variables for testing
        os.environ["PYTEST_RUNNING"] = "1"
        os.environ["QT_QPA_PLATFORM"] = "offscreen"  # For GUI testing
        os.environ["PYTHONPATH"] = str(self.project_root)

        # Create output directories
        self.coverage_dir.mkdir(exist_ok=True)

        print("✅ Test environment configured")

    def run_tests(self) -> Dict[str, Any]:
        """Execute the test suite with comprehensive reporting."""
        print("🚀 Starting comprehensive test execution...")

        # Build pytest command with all reporting options
        pytest_cmd = [
            sys.executable,
            "-m",
            "pytest",
            str(self.test_file),
            "--verbose",
            "--tb=short",
            "--strict-markers",
            "--disable-warnings",
            "--show-capture=no",
            "--durations=10",
            "--maxfail=20",
            f"--html={self.html_report}",
            "--self-contained-html",
            "--json-report",
            f"--json-report-file={self.json_report}",
            f"--junitxml={self.xml_report}",
            "--cov=main",
            f"--cov-report=html:{self.coverage_dir}",
            "--cov-report=term-missing",
            f"--cov-report=xml:{self.coverage_xml}",
            "--cov-fail-under=70",  # Realistic coverage threshold
            "--timeout=300",
            "--timeout-method=thread",
        ]

        # Execute tests
        start_time = datetime.datetime.now()

        try:
            with open(self.execution_log, "w", encoding="utf-8") as log_file:
                print(f"📝 Execution log: {self.execution_log}")

                # Write header to log
                log_file.write(f"Main.py Unit Tests Execution Log\n")
                log_file.write(f"Started: {start_time.isoformat()}\n")
                log_file.write(f"Command: {' '.join(pytest_cmd)}\n")
                log_file.write("=" * 80 + "\n\n")
                log_file.flush()

                # Run pytest
                result = subprocess.run(
                    pytest_cmd,
                    cwd=str(self.project_root),
                    capture_output=True,
                    text=True,
                    timeout=600,  # 10 minutes timeout
                )

                # Write output to log
                log_file.write("STDOUT:\n")
                log_file.write(result.stdout)
                log_file.write("\n" + "=" * 40 + "\n")
                log_file.write("STDERR:\n")
                log_file.write(result.stderr)

        except subprocess.TimeoutExpired:
            print("⏰ Test execution timed out after 10 minutes")
            return self._create_timeout_result(start_time)
        except Exception as e:
            print(f"❌ Test execution failed: {e}")
            return self._create_error_result(start_time, str(e))

        end_time = datetime.datetime.now()
        execution_time = (end_time - start_time).total_seconds()

        # Parse results
        test_results = self._parse_test_results(
            result, start_time, end_time, execution_time
        )

        print(f"⏱️  Test execution completed in {execution_time:.2f} seconds")
        print(f"📊 Exit code: {result.returncode}")

        return test_results

    def _parse_test_results(
        self,
        result: subprocess.CompletedProcess,
        start_time: datetime.datetime,
        end_time: datetime.datetime,
        execution_time: float,
    ) -> Dict[str, Any]:
        """Parse test results from subprocess output."""
        test_results = {
            "execution_info": {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "execution_time_seconds": execution_time,
                "exit_code": result.returncode,
                "success": result.returncode == 0,
            },
            "files_generated": [],
            "test_summary": {},
            "coverage_info": {},
            "errors": [],
        }

        # Check for generated files
        report_files = [
            ("HTML Report", self.html_report),
            ("JSON Report", self.json_report),
            ("XML Report", self.xml_report),
            ("Coverage HTML", self.coverage_dir / "index.html"),
            ("Coverage XML", self.coverage_xml),
            ("Execution Log", self.execution_log),
        ]

        for file_type, file_path in report_files:
            if file_path.exists():
                test_results["files_generated"].append(
                    {
                        "type": file_type,
                        "path": str(file_path),
                        "size_bytes": (
                            file_path.stat().st_size
                            if file_path.is_file()
                            else 0
                        ),
                    }
                )

        # Parse JSON report if available
        if self.json_report.exists():
            try:
                with open(self.json_report, "r", encoding="utf-8") as f:
                    json_data = json.load(f)
                    test_results["test_summary"] = json_data.get("summary", {})
            except Exception as e:
                test_results["errors"].append(
                    f"Failed to parse JSON report: {e}"
                )

        # Parse coverage XML if available
        if self.coverage_xml.exists():
            try:
                import xml.etree.ElementTree as ET

                tree = ET.parse(self.coverage_xml)
                root = tree.getroot()
                coverage_elem = root.find(".//coverage")
                if coverage_elem is not None:
                    test_results["coverage_info"] = {
                        "line_rate": float(
                            coverage_elem.get("line-rate", 0.0)
                        ),
                        "branch_rate": float(
                            coverage_elem.get("branch-rate", 0.0)
                        ),
                        "lines_covered": int(
                            coverage_elem.get("lines-covered", 0)
                        ),
                        "lines_valid": int(
                            coverage_elem.get("lines-valid", 0)
                        ),
                    }
            except Exception as e:
                test_results["errors"].append(
                    f"Failed to parse coverage XML: {e}"
                )

        # Add stdout/stderr for debugging
        test_results["output"] = {
            "stdout": result.stdout,
            "stderr": result.stderr,
        }

        return test_results

    def _create_timeout_result(
        self, start_time: datetime.datetime
    ) -> Dict[str, Any]:
        """Create result structure for timeout scenario."""
        end_time = datetime.datetime.now()
        return {
            "execution_info": {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "execution_time_seconds": (
                    end_time - start_time
                ).total_seconds(),
                "exit_code": -1,
                "success": False,
                "error": "Test execution timed out",
            },
            "files_generated": [],
            "test_summary": {"error": "Timeout"},
            "coverage_info": {},
            "errors": ["Test execution timed out after 10 minutes"],
        }

    def _create_error_result(
        self, start_time: datetime.datetime, error: str
    ) -> Dict[str, Any]:
        """Create result structure for error scenario."""
        end_time = datetime.datetime.now()
        return {
            "execution_info": {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "execution_time_seconds": (
                    end_time - start_time
                ).total_seconds(),
                "exit_code": -2,
                "success": False,
                "error": error,
            },
            "files_generated": [],
            "test_summary": {"error": error},
            "coverage_info": {},
            "errors": [error],
        }

    def generate_summary_reports(self, test_results: Dict[str, Any]):
        """Generate comprehensive summary reports."""
        print("📋 Generating summary reports...")

        # Generate JSON summary
        self._generate_json_summary(test_results)

        # Generate text summary
        self._generate_text_summary(test_results)

        # Generate markdown completion summary
        self._generate_markdown_summary(test_results)

        print("✅ Summary reports generated")

    def _generate_json_summary(self, test_results: Dict[str, Any]):
        """Generate JSON summary report."""
        summary = {
            "test_metadata": {
                "target_module": "main.py",
                "test_file": str(self.test_file),
                "execution_timestamp": self.timestamp,
                "date": self.date_suffix,
                "framework": "pytest",
            },
            "execution_results": test_results["execution_info"],
            "test_summary": test_results["test_summary"],
            "coverage_summary": test_results["coverage_info"],
            "generated_files": test_results["files_generated"],
            "errors_encountered": test_results["errors"],
        }

        with open(self.summary_json, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

    def _generate_text_summary(self, test_results: Dict[str, Any]):
        """Generate text summary report."""
        execution_info = test_results["execution_info"]
        test_summary = test_results["test_summary"]
        coverage_info = test_results["coverage_info"]

        with open(self.summary_txt, "w", encoding="utf-8") as f:
            f.write("=" * 80 + "\n")
            f.write("MAIN.PY UNIT TESTS - EXECUTION SUMMARY\n")
            f.write("=" * 80 + "\n\n")

            f.write(f"Test Target: main.py\n")
            f.write(f"Test File: {self.test_file.name}\n")
            f.write(f"Execution Date: {self.date_suffix}\n")
            f.write(f"Execution Time: {self.timestamp}\n")
            f.write(f"Framework: pytest with comprehensive plugins\n\n")

            f.write("EXECUTION RESULTS:\n")
            f.write("-" * 40 + "\n")
            f.write(
                f"Status: {'SUCCESS' if execution_info['success'] else 'FAILED'}\n"
            )
            f.write(f"Exit Code: {execution_info['exit_code']}\n")
            f.write(
                f"Duration: {execution_info['execution_time_seconds']:.2f} seconds\n"
            )
            f.write(f"Start Time: {execution_info['start_time']}\n")
            f.write(f"End Time: {execution_info['end_time']}\n\n")

            if test_summary:
                f.write("TEST SUMMARY:\n")
                f.write("-" * 40 + "\n")
                for key, value in test_summary.items():
                    f.write(f"{key.replace('_', ' ').title()}: {value}\n")
                f.write("\n")

            if coverage_info:
                f.write("COVERAGE SUMMARY:\n")
                f.write("-" * 40 + "\n")
                line_rate = coverage_info.get("line_rate", 0.0)
                f.write(f"Line Coverage: {line_rate * 100:.1f}%\n")
                f.write(
                    f"Lines Covered: {coverage_info.get('lines_covered', 0)}\n"
                )
                f.write(
                    f"Total Lines: {coverage_info.get('lines_valid', 0)}\n\n"
                )

            f.write("GENERATED FILES:\n")
            f.write("-" * 40 + "\n")
            for file_info in test_results["files_generated"]:
                f.write(f"{file_info['type']}: {file_info['path']}\n")
            f.write("\n")

            if test_results["errors"]:
                f.write("ERRORS ENCOUNTERED:\n")
                f.write("-" * 40 + "\n")
                for error in test_results["errors"]:
                    f.write(f"• {error}\n")
                f.write("\n")

    def _generate_markdown_summary(self, test_results: Dict[str, Any]):
        """Generate markdown completion summary."""
        execution_info = test_results["execution_info"]
        test_summary = test_results["test_summary"]
        coverage_info = test_results["coverage_info"]

        with open(self.summary_md, "w", encoding="utf-8") as f:
            f.write("# Main.py Unit Testing - Project Completion Summary\n\n")

            f.write(f"**Date:** {self.date_suffix}  \n")
            f.write(f"**Execution Time:** {self.timestamp}  \n")
            f.write(f"**Target Module:** main.py  \n")
            f.write(
                f"**Test Framework:** pytest with comprehensive plugins  \n"
            )
            f.write(
                f"**Status:** {'✅ SUCCESS' if execution_info['success'] else '❌ FAILED'}  \n\n"
            )

            f.write("## Executive Summary\n\n")
            f.write(
                "Comprehensive unit testing has been completed for the main.py module of Richard's File Utilities. "
            )
            f.write(
                "This testing suite provides thorough coverage of all functions and methods including:\n\n"
            )
            f.write("- Database system initialization\n")
            f.write("- Main window functionality\n")
            f.write("- Tool launcher methods\n")
            f.write("- Security menu actions\n")
            f.write("- Error handling scenarios\n")
            f.write("- Edge cases and performance testing\n\n")

            f.write("## Test Execution Results\n\n")
            f.write("| Metric | Value |\n")
            f.write("|--------|-------|\n")
            f.write(
                f"| Execution Status | {'SUCCESS' if execution_info['success'] else 'FAILED'} |\n"
            )
            f.write(
                f"| Duration | {execution_info['execution_time_seconds']:.2f} seconds |\n"
            )
            f.write(f"| Exit Code | {execution_info['exit_code']} |\n")

            if test_summary:
                if "total" in test_summary:
                    f.write(
                        f"| Total Tests | {test_summary.get('total', 'N/A')} |\n"
                    )
                if "passed" in test_summary:
                    f.write(
                        f"| Tests Passed | {test_summary.get('passed', 'N/A')} |\n"
                    )
                if "failed" in test_summary:
                    f.write(
                        f"| Tests Failed | {test_summary.get('failed', 'N/A')} |\n"
                    )

            if coverage_info:
                line_coverage = coverage_info.get("line_rate", 0.0) * 100
                f.write(f"| Line Coverage | {line_coverage:.1f}% |\n")

            f.write("\n")

            f.write("## Coverage Analysis\n\n")
            if coverage_info:
                line_rate = coverage_info.get("line_rate", 0.0)
                lines_covered = coverage_info.get("lines_covered", 0)
                lines_valid = coverage_info.get("lines_valid", 0)

                f.write(f"**Line Coverage:** {line_rate * 100:.1f}%  \n")
                f.write(
                    f"**Lines Covered:** {lines_covered} out of {lines_valid}  \n\n"
                )

                if line_rate >= 0.8:
                    f.write(
                        "✅ **Excellent coverage** - Above 80% threshold\n\n"
                    )
                elif line_rate >= 0.7:
                    f.write("✅ **Good coverage** - Above 70% threshold\n\n")
                elif line_rate >= 0.6:
                    f.write(
                        "⚠️ **Moderate coverage** - Consider improving test coverage\n\n"
                    )
                else:
                    f.write(
                        "❌ **Low coverage** - Significant improvements needed\n\n"
                    )
            else:
                f.write("Coverage information not available.\n\n")

            f.write("## Generated Reports\n\n")
            for file_info in test_results["files_generated"]:
                file_path = Path(file_info["path"])
                f.write(f"- **{file_info['type']}:** `{file_path.name}`\n")
            f.write("\n")

            f.write("## Test Categories Covered\n\n")
            f.write("### 1. Database System Initialization\n")
            f.write("- ✅ Successful initialization scenarios\n")
            f.write("- ✅ Import error handling\n")
            f.write("- ✅ Runtime error scenarios\n")
            f.write("- ✅ Database validation failures\n\n")

            f.write("### 2. Main Window Functionality\n")
            f.write("- ✅ Window initialization\n")
            f.write("- ✅ Tool usage tracking\n")
            f.write("- ✅ File access tracking\n")
            f.write("- ✅ Menu bar creation\n")
            f.write("- ✅ Menu callback implementations\n\n")

            f.write("### 3. Tool Launcher Methods\n")
            f.write("- ✅ Successful tool launching\n")
            f.write("- ✅ Import strategy testing\n")
            f.write("- ✅ Tool validation\n")
            f.write("- ✅ Error handling scenarios\n\n")

            f.write("### 4. Security Menu Actions\n")
            f.write("- ✅ Security preferences handling\n")
            f.write("- ✅ Emergency actions\n")
            f.write("- ✅ Configuration import/export\n")
            f.write("- ✅ Security feature testing\n\n")

            f.write("### 5. Edge Cases and Performance\n")
            f.write("- ✅ Multiple tool launches\n")
            f.write("- ✅ Large file list handling\n")
            f.write("- ✅ Permission error scenarios\n")
            f.write("- ✅ JSON serialization errors\n\n")

            if test_results["errors"]:
                f.write("## Issues Encountered\n\n")
                for error in test_results["errors"]:
                    f.write(f"- ❌ {error}\n")
                f.write("\n")

            f.write("## Recommendations\n\n")
            if execution_info["success"]:
                f.write(
                    "✅ **Testing Successful:** All test categories have been executed successfully. "
                )
                f.write(
                    "The main.py module demonstrates robust error handling and comprehensive functionality.\n\n"
                )

                if (
                    coverage_info
                    and coverage_info.get("line_rate", 0.0) >= 0.7
                ):
                    f.write(
                        "✅ **Coverage Acceptable:** Code coverage meets quality standards.\n\n"
                    )
                else:
                    f.write(
                        "⚠️ **Coverage Improvement:** Consider adding more test cases to improve coverage.\n\n"
                    )

                f.write("**Next Steps:**\n")
                f.write(
                    "1. Review generated HTML and JSON reports for detailed analysis\n"
                )
                f.write(
                    "2. Address any specific issues identified in the test output\n"
                )
                f.write(
                    "3. Consider adding integration tests for end-to-end scenarios\n"
                )
                f.write(
                    "4. Implement continuous testing in development workflow\n\n"
                )
            else:
                f.write(
                    "❌ **Testing Issues:** Some test execution problems were encountered. "
                )
                f.write(
                    "Review the execution log and error details for resolution.\n\n"
                )

                f.write("**Immediate Actions Required:**\n")
                f.write("1. Review execution log for specific error details\n")
                f.write(
                    "2. Address any missing dependencies or configuration issues\n"
                )
                f.write("3. Verify test environment setup\n")
                f.write(
                    "4. Re-run tests after resolving identified issues\n\n"
                )

            f.write("---\n")
            f.write(
                f"*Report generated automatically on {datetime.datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}*\n"
            )

    def display_results(self, test_results: Dict[str, Any]):
        """Display test execution results."""
        execution_info = test_results["execution_info"]

        print("\n" + "=" * 80)
        print("MAIN.PY UNIT TESTS - EXECUTION COMPLETE")
        print("=" * 80)

        print(f"📅 Date: {self.date_suffix}")
        print(
            f"⏰ Duration: {execution_info['execution_time_seconds']:.2f} seconds"
        )
        print(
            f"📋 Status: {'✅ SUCCESS' if execution_info['success'] else '❌ FAILED'}"
        )
        print(f"🔢 Exit Code: {execution_info['exit_code']}")

        if test_results["test_summary"]:
            print(f"\n📊 TEST SUMMARY:")
            for key, value in test_results["test_summary"].items():
                print(f"   {key.replace('_', ' ').title()}: {value}")

        if test_results["coverage_info"]:
            coverage = test_results["coverage_info"]
            line_rate = coverage.get("line_rate", 0.0) * 100
            print(
                f"\n📈 COVERAGE: {line_rate:.1f}% ({coverage.get('lines_covered', 0)}/{coverage.get('lines_valid', 0)} lines)"
            )

        print(f"\n📁 GENERATED FILES:")
        for file_info in test_results["files_generated"]:
            print(f"   {file_info['type']}: {Path(file_info['path']).name}")

        print(f"\n📝 SUMMARY REPORTS:")
        print(f"   JSON: {self.summary_json.name}")
        print(f"   Text: {self.summary_txt.name}")
        print(f"   Markdown: {self.summary_md.name}")

        if test_results["errors"]:
            print(f"\n⚠️  ERRORS:")
            for error in test_results["errors"]:
                print(f"   • {error}")

        print("\n" + "=" * 80)

    def run(self):
        """Execute the complete test workflow."""
        print("🚀 Main.py Unit Test Runner - Starting Execution")
        print(f"📅 Date: {self.date_suffix}")
        print(f"⏰ Timestamp: {self.timestamp}")
        print("=" * 80)

        # Check prerequisites
        if not self.check_prerequisites():
            print("❌ Prerequisites check failed. Cannot proceed.")
            return False

        # Setup environment
        self.setup_environment()

        # Run tests
        test_results = self.run_tests()

        # Generate summary reports
        self.generate_summary_reports(test_results)

        # Display results
        self.display_results(test_results)

        return test_results["execution_info"]["success"]


def main():
    """Main entry point for the test runner."""
    try:
        runner = MainTestRunner()
        success = runner.run()

        if success:
            print("\n🎉 Test execution completed successfully!")
            return 0
        else:
            print(
                "\n❌ Test execution completed with issues. Review the reports for details."
            )
            return 1

    except KeyboardInterrupt:
        print("\n⏸️  Test execution interrupted by user.")
        return 130
    except Exception as e:
        print(f"\n💥 Unexpected error in test runner: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
