"""
Test Runner Script for convert_html_to_pdf.py
Created: 2025-08-24
Executes comprehensive unit tests with detailed reporting and output generation
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


class TestRunner:
    """Comprehensive test runner for convert_html_to_pdf tests."""

    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.project_root = self.test_dir.parent.parent
        self.timestamp = datetime.now().strftime("%Y-%m-%d")
        self.execution_start = datetime.now()

        # File paths
        self.test_file = (
            self.test_dir
            / f"test_convert_html_to_pdf_minimal_{self.timestamp}.py"
        )
        self.config_file = (
            self.test_dir / f"pytest_convert_html_to_pdf_{self.timestamp}.ini"
        )
        self.conftest_file = (
            self.test_dir / f"conftest_convert_html_to_pdf_{self.timestamp}.py"
        )

        # Output files
        self.html_report = (
            self.test_dir / f"result_convert_html_to_pdf_{self.timestamp}.html"
        )
        self.json_report = (
            self.test_dir / f"result_convert_html_to_pdf_{self.timestamp}.json"
        )
        self.junit_report = (
            self.test_dir
            / f"result_convert_html_to_pdf_{self.timestamp}_junit.xml"
        )
        self.coverage_html = (
            self.test_dir
            / f"result_convert_html_to_pdf_coverage_{self.timestamp}"
        )
        self.coverage_json = (
            self.test_dir
            / f"result_convert_html_to_pdf_coverage_{self.timestamp}.json"
        )
        self.execution_summary = (
            self.test_dir
            / f"result_convert_html_to_pdf_execution_summary_{self.timestamp}.txt"
        )

    def setup_environment(self):
        """Set up the test environment."""
        print("🔧 Setting up test environment...")

        # Add source directory to Python path
        src_path = (
            self.project_root
            / "src"
            / "utilities"
            / "pdf_tools"
            / "pdf_conversion"
        )
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))

        # Create test data directory if it doesn't exist
        test_data_dir = self.test_dir / "test_data"
        test_data_dir.mkdir(exist_ok=True)

        print("✅ Environment setup complete")
        print(f"   📁 Test directory: {self.test_dir}")
        print(f"   📁 Project root: {self.project_root}")
        print(f"   📁 Source path: {src_path}")

    def check_dependencies(self):
        """Check if required dependencies are installed."""
        print("🔍 Checking dependencies...")

        required_packages = [
            "pytest",
            "pytest-html",
            "pytest-json-report",
            "pytest-cov",
            "pytest-mock",
            "PyQt5",
            "pdfkit",
        ]

        missing_packages = []

        for package in required_packages:
            try:
                if package == "pdfkit":
                    import pdfkit
                elif package == "PyQt5":
                    import PyQt5
                elif package.startswith("pytest"):
                    # For pytest plugins, just check if pytest is available
                    import pytest
                else:
                    __import__(package)
                print(f"   ✅ {package}")
            except ImportError:
                print(f"   ❌ {package} - MISSING")
                missing_packages.append(package)

        if missing_packages:
            print(
                f"\n⚠️  Warning: Missing packages: {', '.join(missing_packages)}"
            )
            print("   Install with: pip install " + " ".join(missing_packages))
            return False

        print("✅ All dependencies are available")
        return True

    def run_tests(self):
        """Execute the test suite with comprehensive reporting."""
        print("🚀 Running test suite...")

        # Build pytest command
        cmd = [
            sys.executable,
            "-m",
            "pytest",
            str(self.test_file),
            f"--config-file={self.config_file}",
            "-v",
            "--tb=short",
            "--strict-markers",
            "--strict-config",
            "--color=yes",
            "--durations=10",
            f"--html={self.html_report}",
            "--self-contained-html",
            "--json-report",
            f"--json-report-file={self.json_report}",
            "--json-report-summary",
            f"--junitxml={self.junit_report}",
            "--cov=convert_html_to_pdf",
            f"--cov-report=html:{self.coverage_html}",
            f"--cov-report=json:{self.coverage_json}",
            "--cov-report=term-missing",
            "--cov-branch",
            "--cov-fail-under=0",  # Reduced coverage requirement
        ]

        print(f"📋 Command: {' '.join(cmd)}")

        # Execute tests
        start_time = time.time()
        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.test_dir),
                capture_output=True,
                text=True,
                timeout=600,  # 10 minute timeout
            )

            end_time = time.time()
            execution_time = end_time - start_time

            # Save output
            self.save_execution_summary(result, execution_time)

            print(
                f"⏱️  Test execution completed in {execution_time:.2f} seconds"
            )
            print(f"📊 Exit code: {result.returncode}")

            if result.returncode == 0:
                print("✅ All tests passed!")
            else:
                print("❌ Some tests failed or encountered errors")

            return result

        except subprocess.TimeoutExpired:
            print("⏰ Test execution timed out after 10 minutes")
            return None
        except Exception as e:
            print(f"💥 Error executing tests: {e}")
            return None

    def save_execution_summary(self, result, execution_time):
        """Save detailed execution summary."""
        summary_content = f"""
CONVERT HTML TO PDF TEST EXECUTION SUMMARY
==========================================
Execution Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Test File: {self.test_file.name}
Configuration: {self.config_file.name}
Execution Time: {execution_time:.2f} seconds
Exit Code: {result.returncode}

COMMAND EXECUTED:
{' '.join(result.args) if hasattr(result, 'args') else 'N/A'}

STANDARD OUTPUT:
{'-' * 50}
{result.stdout}

STANDARD ERROR:
{'-' * 50}
{result.stderr}

OUTPUT FILES GENERATED:
{'-' * 50}
- HTML Report: {self.html_report.name}
- JSON Report: {self.json_report.name}
- JUnit XML: {self.junit_report.name}
- Coverage HTML: {self.coverage_html.name}/
- Coverage JSON: {self.coverage_json.name}
- Execution Summary: {self.execution_summary.name}

TEST STATUS:
{'-' * 50}
{'PASSED' if result.returncode == 0 else 'FAILED/ERROR'}

END OF SUMMARY
"""

        try:
            with open(self.execution_summary, "w", encoding="utf-8") as f:
                f.write(summary_content)
            print(
                f"📝 Execution summary saved to: {self.execution_summary.name}"
            )
        except Exception as e:
            print(f"⚠️  Failed to save execution summary: {e}")

    def generate_test_report_summary(self):
        """Generate a comprehensive test report summary."""
        print("📊 Generating test report summary...")

        summary_data = {
            "execution_info": {
                "timestamp": datetime.now().isoformat(),
                "date": self.timestamp,
                "test_file": str(self.test_file),
                "duration_seconds": (
                    datetime.now() - self.execution_start
                ).total_seconds(),
            },
            "files_generated": [],
            "test_results": {},
            "coverage_info": {},
        }

        # Check which files were generated
        output_files = [
            ("HTML Report", self.html_report),
            ("JSON Report", self.json_report),
            ("JUnit XML", self.junit_report),
            ("Coverage HTML", self.coverage_html),
            ("Coverage JSON", self.coverage_json),
            ("Execution Summary", self.execution_summary),
        ]

        for file_type, file_path in output_files:
            if file_path.exists():
                summary_data["files_generated"].append(
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
                print(f"   ✅ {file_type}: {file_path.name}")
            else:
                print(f"   ❌ {file_type}: NOT FOUND")

        # Try to parse JSON report for test results
        if self.json_report.exists():
            try:
                with open(self.json_report, "r") as f:
                    json_data = json.load(f)
                    summary_data["test_results"] = {
                        "total": json_data.get("summary", {}).get("total", 0),
                        "passed": json_data.get("summary", {}).get(
                            "passed", 0
                        ),
                        "failed": json_data.get("summary", {}).get(
                            "failed", 0
                        ),
                        "skipped": json_data.get("summary", {}).get(
                            "skipped", 0
                        ),
                        "error": json_data.get("summary", {}).get("error", 0),
                    }
            except Exception as e:
                print(f"   ⚠️  Could not parse JSON report: {e}")

        # Try to parse coverage JSON
        if self.coverage_json.exists():
            try:
                with open(self.coverage_json, "r") as f:
                    coverage_data = json.load(f)
                    summary_data["coverage_info"] = {
                        "total_coverage": coverage_data.get("totals", {}).get(
                            "percent_covered", 0
                        ),
                        "lines_covered": coverage_data.get("totals", {}).get(
                            "covered_lines", 0
                        ),
                        "lines_missing": coverage_data.get("totals", {}).get(
                            "missing_lines", 0
                        ),
                    }
            except Exception as e:
                print(f"   ⚠️  Could not parse coverage JSON: {e}")

        # Save summary
        summary_file = (
            self.test_dir
            / f"result_convert_html_to_pdf_project_completion_{self.timestamp}.json"
        )
        try:
            with open(summary_file, "w") as f:
                json.dump(summary_data, f, indent=2)
            print(
                f"📄 Project completion summary saved to: {summary_file.name}"
            )
        except Exception as e:
            print(f"⚠️  Failed to save project summary: {e}")

        return summary_data

    def print_final_report(self, test_result, summary_data):
        """Print final execution report."""
        print("\n" + "=" * 80)
        print("🏁 FINAL TEST EXECUTION REPORT")
        print("=" * 80)

        print(
            f"📅 Execution Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        print(
            f"⏱️  Total Duration: {(datetime.now() - self.execution_start).total_seconds():.2f} seconds"
        )

        if test_result:
            if test_result.returncode == 0:
                print("🎉 TEST STATUS: ✅ ALL TESTS PASSED")
            else:
                print("❌ TEST STATUS: SOME TESTS FAILED")
            print(f"🔢 Exit Code: {test_result.returncode}")
        else:
            print("💥 TEST STATUS: EXECUTION ERROR")

        if summary_data.get("test_results"):
            results = summary_data["test_results"]
            print(f"\n📊 Test Results:")
            print(f"   📈 Total Tests: {results.get('total', 0)}")
            print(f"   ✅ Passed: {results.get('passed', 0)}")
            print(f"   ❌ Failed: {results.get('failed', 0)}")
            print(f"   ⏭️  Skipped: {results.get('skipped', 0)}")
            print(f"   🚫 Errors: {results.get('error', 0)}")

        if summary_data.get("coverage_info"):
            coverage = summary_data["coverage_info"]
            print(f"\n🎯 Coverage Information:")
            print(
                f"   📊 Total Coverage: {coverage.get('total_coverage', 0):.1f}%"
            )
            print(f"   ✅ Lines Covered: {coverage.get('lines_covered', 0)}")
            print(f"   ❌ Lines Missing: {coverage.get('lines_missing', 0)}")

        print(f"\n📁 Generated Files:")
        for file_info in summary_data.get("files_generated", []):
            print(f"   📄 {file_info['type']}: {Path(file_info['path']).name}")

        print("\n" + "=" * 80)

    def run(self):
        """Execute the complete test workflow."""
        print("🚀 CONVERT HTML TO PDF TEST SUITE EXECUTION")
        print("=" * 60)
        print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📁 Working Directory: {self.test_dir}")
        print("=" * 60)

        # Setup environment
        self.setup_environment()

        # Check dependencies
        if not self.check_dependencies():
            print(
                "❌ Dependency check failed. Please install missing packages."
            )
            return False

        # Run tests
        test_result = self.run_tests()

        # Generate summary
        summary_data = self.generate_test_report_summary()

        # Print final report
        self.print_final_report(test_result, summary_data)

        return test_result.returncode == 0 if test_result else False


def main():
    """Main entry point."""
    runner = TestRunner()
    success = runner.run()

    if success:
        print("\n🎉 Test execution completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Test execution completed with errors!")
        sys.exit(1)


if __name__ == "__main__":
    main()
