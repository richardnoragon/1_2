#!/usr/bin/env python3
"""
Office Metadata GUI Test Runner
Comprehensive test execution script for office_metadata_gui.py
Created: 2025-08-29
Target: src/tools/metadata/office_metadata/office_metadata_gui.py

This script executes comprehensive unit tests for the Office Metadata GUI
with standardized reporting, coverage analysis, and result documentation.
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


class OfficeMetadataGUITestRunner:
    """Enhanced test runner for Office Metadata GUI tests."""

    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y-%m-%d")
        self.execution_time = datetime.now().isoformat()
        self.test_dir = Path(__file__).parent
        self.results_dir = self.test_dir / "results"
        self.results_dir.mkdir(exist_ok=True)

        # Test configuration
        self.test_file = f"test_office_metadata_gui_{self.timestamp}.py"
        self.config_file = f"pytest_office_metadata_gui_{self.timestamp}.ini"

        # Result files
        self.html_report = f"result_office_metadata_gui_{self.timestamp}.html"
        self.json_report = f"result_office_metadata_gui_{self.timestamp}.json"
        self.coverage_html = (
            f"result_office_metadata_gui_coverage_{self.timestamp}"
        )
        self.coverage_json = (
            f"result_office_metadata_gui_coverage_{self.timestamp}.json"
        )
        self.coverage_xml = (
            f"result_office_metadata_gui_coverage_{self.timestamp}.xml"
        )
        self.execution_log = (
            f"result_office_metadata_gui_execution_{self.timestamp}.log"
        )
        self.summary_report = (
            f"result_office_metadata_gui_summary_{self.timestamp}.json"
        )

        # Pytest command configuration
        self.pytest_args = [
            sys.executable,
            "-m",
            "pytest",
            self.test_file,
            f"-c={self.config_file}",
            "--verbose",
            "--tb=short",
            "--strict-markers",
            "--disable-warnings",
            f"--html={self.html_report}",
            "--self-contained-html",
            "--json-report",
            f"--json-report-file={self.json_report}",
            "--cov=src.tools.metadata.office_metadata.office_metadata_gui",
            f"--cov-report=html:{self.coverage_html}",
            f"--cov-report=json:{self.coverage_json}",
            f"--cov-report=xml:{self.coverage_xml}",
            "--cov-report=term-missing",
            "--cov-fail-under=75",
            "--maxfail=10",
            "--durations=20",
        ]

    def check_dependencies(self):
        """Check if required dependencies are available."""
        print("🔍 Checking test dependencies...")

        required_packages = [
            "pytest",
            "pytest-html",
            "pytest-json-report",
            "pytest-cov",
            "pytest-timeout",
        ]

        missing_packages = []

        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
                print(f"  ✅ {package} - Available")
            except ImportError:
                missing_packages.append(package)
                print(f"  ❌ {package} - Missing")

        if missing_packages:
            print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
            print("Install with: pip install " + " ".join(missing_packages))
            return False

        # Check PyQt5 availability
        try:
            import PyQt5

            print("  ✅ PyQt5 - Available")
        except ImportError:
            print("  ⚠️  PyQt5 - Not available (GUI tests will be skipped)")

        return True

    def check_target_module(self):
        """Check if target module is available."""
        print("\n🎯 Checking target module...")

        target_path = Path(
            "src/tools/metadata/office_metadata/office_metadata_gui.py"
        )

        if target_path.exists():
            print(f"  ✅ Target module found: {target_path}")
            return True
        else:
            # Try alternative paths
            alternative_paths = [
                Path(
                    "../../../src/tools/metadata/office_metadata/office_metadata_gui.py"
                ),
                Path(
                    "../../src/tools/metadata/office_metadata/office_metadata_gui.py"
                ),
                Path("src/utilities/office_metadata/office_metadata_gui.py"),
            ]

            for alt_path in alternative_paths:
                if alt_path.exists():
                    print(f"  ✅ Target module found: {alt_path}")
                    return True

            print(f"  ❌ Target module not found")
            print(f"     Expected: {target_path}")
            return False

    def setup_environment(self):
        """Setup test environment."""
        print("\n🛠️  Setting up test environment...")

        # Add src to Python path
        src_paths = ["src", "../src", "../../src", "../../../src"]

        for src_path in src_paths:
            if os.path.exists(src_path):
                abs_src_path = os.path.abspath(src_path)
                if abs_src_path not in sys.path:
                    sys.path.insert(0, abs_src_path)
                    print(f"  ✅ Added to Python path: {abs_src_path}")
                break

        # Set environment variables
        os.environ["PYTHONPATH"] = os.pathsep.join(sys.path)
        os.environ["QT_QPA_PLATFORM"] = "offscreen"  # For headless GUI testing

        print("  ✅ Environment variables configured")

    def run_tests(self):
        """Execute the test suite."""
        print(f"\n🚀 Running Office Metadata GUI tests...")
        print(f"   Test file: {self.test_file}")
        print(f"   Config: {self.config_file}")
        print(f"   Timestamp: {self.execution_time}")

        start_time = time.time()

        # Execute pytest
        try:
            with open(self.execution_log, "w", encoding="utf-8") as log_file:
                # Write execution header
                log_file.write(f"Office Metadata GUI Test Execution Log\n")
                log_file.write(f"Started: {self.execution_time}\n")
                log_file.write(f"Command: {' '.join(self.pytest_args)}\n")
                log_file.write("=" * 80 + "\n\n")

                # Run pytest
                result = subprocess.run(
                    self.pytest_args,
                    cwd=self.test_dir,
                    capture_output=True,
                    text=True,
                    timeout=600,  # 10 minute timeout
                )

                # Write results to log
                log_file.write("STDOUT:\n")
                log_file.write(result.stdout)
                log_file.write("\n\nSTDERR:\n")
                log_file.write(result.stderr)
                log_file.write(f"\n\nReturn Code: {result.returncode}\n")

                execution_time = time.time() - start_time
                log_file.write(
                    f"Execution Time: {execution_time:.2f} seconds\n"
                )

                print(f"   Return code: {result.returncode}")
                print(f"   Execution time: {execution_time:.2f} seconds")

                if result.returncode == 0:
                    print("   ✅ Tests completed successfully")
                else:
                    print("   ⚠️  Tests completed with issues")

                return (
                    result.returncode,
                    execution_time,
                    result.stdout,
                    result.stderr,
                )

        except subprocess.TimeoutExpired:
            print("   ❌ Test execution timed out")
            return -1, time.time() - start_time, "", "Test execution timed out"
        except Exception as e:
            print(f"   ❌ Test execution failed: {e}")
            return -1, time.time() - start_time, "", str(e)

    def process_results(self, return_code, execution_time, stdout, stderr):
        """Process and analyze test results."""
        print("\n📊 Processing test results...")

        summary = {
            "execution_info": {
                "timestamp": self.execution_time,
                "date": self.timestamp,
                "target_module": "src/utilities/office_metadata/office_metadata_gui.py",
                "test_file": self.test_file,
                "config_file": self.config_file,
                "execution_time_seconds": execution_time,
                "return_code": return_code,
                "status": "SUCCESS" if return_code == 0 else "FAILED",
            },
            "test_framework": {
                "runner": "pytest",
                "version": self._get_pytest_version(),
                "plugins": [
                    "pytest-html",
                    "pytest-json-report",
                    "pytest-cov",
                    "pytest-timeout",
                ],
            },
            "coverage_reports": {
                "html_report": self.coverage_html,
                "json_report": self.coverage_json,
                "xml_report": self.coverage_xml,
            },
            "output_files": {
                "html_report": self.html_report,
                "json_report": self.json_report,
                "execution_log": self.execution_log,
                "summary_report": self.summary_report,
            },
        }

        # Parse JSON report if available
        json_report_path = self.test_dir / self.json_report
        if json_report_path.exists():
            try:
                with open(json_report_path, "r", encoding="utf-8") as f:
                    json_data = json.load(f)

                summary["test_results"] = {
                    "total_tests": json_data.get("summary", {}).get(
                        "total", 0
                    ),
                    "passed": json_data.get("summary", {}).get("passed", 0),
                    "failed": json_data.get("summary", {}).get("failed", 0),
                    "skipped": json_data.get("summary", {}).get("skipped", 0),
                    "errors": json_data.get("summary", {}).get("error", 0),
                    "duration": json_data.get("duration", execution_time),
                }

                print(f"   ✅ Tests: {summary['test_results']['total_tests']}")
                print(f"   ✅ Passed: {summary['test_results']['passed']}")
                print(f"   ❌ Failed: {summary['test_results']['failed']}")
                print(f"   ⏭️  Skipped: {summary['test_results']['skipped']}")

            except Exception as e:
                print(f"   ⚠️  Could not parse JSON report: {e}")

        # Parse coverage report if available
        coverage_json_path = self.test_dir / self.coverage_json
        if coverage_json_path.exists():
            try:
                with open(coverage_json_path, "r", encoding="utf-8") as f:
                    coverage_data = json.load(f)

                totals = coverage_data.get("totals", {})
                summary["coverage"] = {
                    "percent_covered": totals.get("percent_covered", 0),
                    "num_statements": totals.get("num_statements", 0),
                    "missing_lines": totals.get("missing_lines", 0),
                    "covered_lines": totals.get("covered_lines", 0),
                }

                print(
                    f"   📈 Coverage: {summary['coverage']['percent_covered']:.1f}%"
                )

            except Exception as e:
                print(f"   ⚠️  Could not parse coverage report: {e}")

        # Save summary
        summary_path = self.test_dir / self.summary_report
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        print(f"   ✅ Summary saved: {summary_path}")

        return summary

    def _get_pytest_version(self):
        """Get pytest version."""
        try:
            import pytest

            return pytest.__version__
        except:
            return "unknown"

    def generate_report(self, summary):
        """Generate final test report."""
        print("\n📋 Generating final report...")

        report_content = f"""
# Office Metadata GUI Test Report
**Generated:** {self.execution_time}  
**Target Module:** src/utilities/office_metadata/office_metadata_gui.py  
**Test Date:** {self.timestamp}  

## Execution Summary
- **Status:** {summary['execution_info']['status']}
- **Return Code:** {summary['execution_info']['return_code']}
- **Execution Time:** {summary['execution_info']['execution_time_seconds']:.2f} seconds

## Test Results
"""

        if "test_results" in summary:
            results = summary["test_results"]
            report_content += f"""
- **Total Tests:** {results['total_tests']}
- **Passed:** {results['passed']}
- **Failed:** {results['failed']} 
- **Skipped:** {results['skipped']}
- **Errors:** {results['errors']}
"""

        if "coverage" in summary:
            coverage = summary["coverage"]
            report_content += f"""
## Coverage Analysis
- **Coverage Percentage:** {coverage['percent_covered']:.1f}%
- **Total Statements:** {coverage['num_statements']}
- **Covered Lines:** {coverage['covered_lines']}
- **Missing Lines:** {coverage['missing_lines']}
"""

        report_content += f"""
## Output Files
- **HTML Report:** {self.html_report}
- **JSON Report:** {self.json_report}
- **Coverage HTML:** {self.coverage_html}/index.html
- **Coverage JSON:** {self.coverage_json}
- **Coverage XML:** {self.coverage_xml}
- **Execution Log:** {self.execution_log}
- **Summary Report:** {self.summary_report}

## Test Categories Covered
1. **OfficeMetadataLogic Tests:** Core metadata extraction logic
2. **MetadataWorker Tests:** Worker thread functionality (requires PyQt5)
3. **OfficeMetadataGUI Tests:** GUI component testing (requires PyQt5)
4. **Integration Tests:** End-to-end workflow testing
5. **Edge Case Tests:** Error handling and boundary conditions

## Test Data
- **Mock DOCX Files:** Complete Office document structure
- **XML Metadata:** Core, app, and custom properties
- **Security Testing:** Privacy and sensitive data detection
- **Unicode Support:** Multi-language content validation
- **Error Scenarios:** Invalid files and corrupted data

---
*Generated by Office Metadata GUI Test Runner*
"""

        report_file = (
            self.test_dir
            / f"result_office_metadata_gui_report_{self.timestamp}.md"
        )
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report_content)

        print(f"   ✅ Final report: {report_file}")

        return report_file

    def run(self):
        """Execute complete test workflow."""
        print("🧪 Office Metadata GUI Test Suite")
        print("=" * 50)

        # Pre-flight checks
        if not self.check_dependencies():
            print("\n❌ Dependency check failed")
            return 1

        if not self.check_target_module():
            print("\n❌ Target module check failed")
            return 1

        self.setup_environment()

        # Execute tests
        return_code, execution_time, stdout, stderr = self.run_tests()

        # Process results
        summary = self.process_results(
            return_code, execution_time, stdout, stderr
        )

        # Generate final report
        report_file = self.generate_report(summary)

        print("\n✅ Test execution completed!")
        print(f"   View results: {self.html_report}")
        print(f"   Coverage report: {self.coverage_html}/index.html")
        print(f"   Summary: {self.summary_report}")

        return return_code


if __name__ == "__main__":
    runner = OfficeMetadataGUITestRunner()
    exit_code = runner.run()
    sys.exit(exit_code)
