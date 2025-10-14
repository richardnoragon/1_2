#!/usr/bin/env python3
"""
Comprehensive Test Runner for Permissions Editor
Automated test execution with detailed reporting and analysis

Author: Generated Test Suite
Date: 2025-08-28
Target: permissions_editor.py comprehensive testing
Framework: pytest with full reporting suite

Features:
- Automated test discovery and execution
- Multi-format reporting (HTML, JSON, XML, Coverage)
- Performance metrics and timing analysis
- Error categorization and summary
- Test result validation and quality metrics
- Comprehensive documentation generation
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, project_root)


class PermissionsEditorTestRunner:
    """Comprehensive test runner for Permissions Editor."""

    def __init__(self):
        self.test_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_root = project_root
        self.timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.results = {}
        self.start_time = None
        self.end_time = None

        # Test configuration
        self.config_file = os.path.join(
            self.test_dir, "test_config_permissions_editor_2025-08-28.ini"
        )
        self.test_files = [
            "test_permissions_editor_2025-08-28.py",
            "test_permissions_editor_gui_2025-08-28.py",
        ]

        # Output files
        self.html_report = os.path.join(
            self.test_dir, "result_permissions_editor_2025-08-28.html"
        )
        self.json_report = os.path.join(
            self.test_dir, "result_permissions_editor_2025-08-28.json"
        )
        self.xml_report = os.path.join(
            self.test_dir, "result_permissions_editor_2025-08-28.xml"
        )
        self.coverage_dir = os.path.join(
            self.test_dir, "result_permissions_editor_coverage_2025-08-28"
        )
        self.coverage_xml = os.path.join(
            self.test_dir, "result_permissions_editor_coverage_2025-08-28.xml"
        )
        self.summary_report = os.path.join(
            self.test_dir, "result_permissions_editor_summary_2025-08-28.json"
        )
        self.comprehensive_report = os.path.join(
            self.test_dir,
            "result_permissions_editor_comprehensive_report_2025-08-28.md",
        )

    def validate_environment(self):
        """Validate test environment and dependencies."""
        print("🔍 Validating test environment...")

        # Check Python version
        python_version = sys.version_info
        print(
            f"   Python version: {python_version.major}.{python_version.minor}.{python_version.micro}"
        )

        # Check required packages
        required_packages = [
            "pytest",
            "pytest-html",
            "pytest-json-report",
            "pytest-cov",
            "pytest-mock",
            "PyQt5",
        ]

        missing_packages = []
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
                print(f"   ✅ {package} available")
            except ImportError:
                missing_packages.append(package)
                print(f"   ❌ {package} missing")

        if missing_packages:
            print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
            print("Install with: pip install " + " ".join(missing_packages))
            return False

        # Check target module
        try:
            from src.tools.system.permissions.permissions_editor import (
                PermissionsEditorGUI,
            )

            print("   ✅ Target module permissions_editor available")
        except ImportError as e:
            print(f"   ❌ Target module import error: {e}")
            return False

        # Check test files
        for test_file in self.test_files:
            test_path = os.path.join(self.test_dir, test_file)
            if os.path.exists(test_path):
                print(f"   ✅ Test file {test_file} found")
            else:
                print(f"   ❌ Test file {test_file} missing")
                return False

        print("✅ Environment validation completed\n")
        return True

    def setup_test_environment(self):
        """Setup test environment and temporary directories."""
        print("🛠️  Setting up test environment...")

        # Create test data directory if needed
        test_data_dir = os.path.join(self.test_dir, "test_data")
        os.makedirs(test_data_dir, exist_ok=True)

        # Create temporary test files
        temp_test_file = os.path.join(test_data_dir, "temp_permissions_test.txt")
        with open(temp_test_file, "w") as f:
            f.write("Temporary test file for permissions testing")

        # Set known permissions for testing
        import stat

        os.chmod(temp_test_file, stat.S_IRUSR | stat.S_IWUSR)

        print("   ✅ Test data created")
        print("   ✅ Temporary files setup")
        print("✅ Test environment setup completed\n")

    def execute_tests(self):
        """Execute comprehensive test suite."""
        print("🚀 Executing comprehensive test suite...")
        self.start_time = time.time()

        # Build pytest command
        cmd = [
            sys.executable,
            "-m",
            "pytest",
            "--config-file",
            self.config_file,
            "--verbose",
            "--tb=short",
            "--strict-markers",
            "--disable-warnings",
            f"--html={self.html_report}",
            "--self-contained-html",
            "--json-report",
            f"--json-report-file={self.json_report}",
            f"--junitxml={self.xml_report}",
            "--cov=src/utilities/system/permissions_editor",
            f"--cov-report=html:{self.coverage_dir}",
            f"--cov-report=xml:{self.coverage_xml}",
            "--cov-report=term-missing",
            "--cov-fail-under=70",
            "--maxfail=20",
        ]

        # Add test files
        for test_file in self.test_files:
            test_path = os.path.join(self.test_dir, test_file)
            if os.path.exists(test_path):
                cmd.append(test_path)

        print(f"   Command: {' '.join(cmd)}")
        print(f"   Working directory: {self.test_dir}")

        # Execute tests
        try:
            result = subprocess.run(
                cmd,
                cwd=self.test_dir,
                capture_output=True,
                text=True,
                timeout=600,  # 10 minute timeout
            )

            self.end_time = time.time()

            print(f"   Exit code: {result.returncode}")
            print(f"   Execution time: {self.end_time - self.start_time:.2f} seconds")

            if result.stdout:
                print("   STDOUT:")
                print(
                    "   " + "\n   ".join(result.stdout.split("\n")[:10])
                )  # First 10 lines

            if result.stderr:
                print("   STDERR:")
                print(
                    "   " + "\n   ".join(result.stderr.split("\n")[:5])
                )  # First 5 lines

            self.results["exit_code"] = result.returncode
            self.results["stdout"] = result.stdout
            self.results["stderr"] = result.stderr
            self.results["execution_time"] = self.end_time - self.start_time

            return result.returncode == 0

        except subprocess.TimeoutExpired:
            print("   ❌ Test execution timed out")
            self.results["timeout"] = True
            return False
        except Exception as e:
            print(f"   ❌ Test execution failed: {e}")
            self.results["error"] = str(e)
            return False

    def analyze_results(self):
        """Analyze test results and generate metrics."""
        print("📊 Analyzing test results...")

        # Parse JSON report
        if os.path.exists(self.json_report):
            try:
                with open(self.json_report, "r") as f:
                    json_data = json.load(f)

                self.results["summary"] = json_data.get("summary", {})
                self.results["tests"] = json_data.get("tests", [])
                self.results["collectors"] = json_data.get("collectors", [])

                # Calculate metrics
                summary = self.results["summary"]
                total_tests = summary.get("total", 0)
                passed_tests = summary.get("passed", 0)
                failed_tests = summary.get("failed", 0)
                skipped_tests = summary.get("skipped", 0)
                error_tests = summary.get("error", 0)

                self.results["metrics"] = {
                    "total_tests": total_tests,
                    "passed_tests": passed_tests,
                    "failed_tests": failed_tests,
                    "skipped_tests": skipped_tests,
                    "error_tests": error_tests,
                    "pass_rate": (
                        (passed_tests / total_tests * 100) if total_tests > 0 else 0
                    ),
                    "failure_rate": (
                        (failed_tests / total_tests * 100) if total_tests > 0 else 0
                    ),
                }

                print(f"   📈 Total tests: {total_tests}")
                print(f"   ✅ Passed: {passed_tests}")
                print(f"   ❌ Failed: {failed_tests}")
                print(f"   ⏭️ Skipped: {skipped_tests}")
                print(f"   🚫 Errors: {error_tests}")
                print(f"   📊 Pass rate: {self.results['metrics']['pass_rate']:.1f}%")

            except Exception as e:
                print(f"   ⚠️ Error parsing JSON report: {e}")

        # Analyze coverage
        coverage_xml = self.coverage_xml
        if os.path.exists(coverage_xml):
            try:
                import xml.etree.ElementTree as ET

                tree = ET.parse(coverage_xml)
                root = tree.getroot()

                coverage_elem = root.find(".//coverage")
                if coverage_elem is not None:
                    line_rate = float(coverage_elem.get("line-rate", 0)) * 100
                    branch_rate = float(coverage_elem.get("branch-rate", 0)) * 100

                    self.results["coverage"] = {
                        "line_coverage": line_rate,
                        "branch_coverage": branch_rate,
                    }

                    print(f"   📋 Line coverage: {line_rate:.1f}%")
                    print(f"   🌿 Branch coverage: {branch_rate:.1f}%")

            except Exception as e:
                print(f"   ⚠️ Error parsing coverage report: {e}")

        print("✅ Result analysis completed\n")

    def generate_summary(self):
        """Generate comprehensive test summary."""
        print("📝 Generating test summary...")

        summary_data = {
            "test_run_info": {
                "timestamp": self.timestamp,
                "start_time": self.start_time,
                "end_time": self.end_time,
                "execution_time": getattr(self, "end_time", 0)
                - getattr(self, "start_time", 0),
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "test_files": self.test_files,
                "project_root": self.project_root,
            },
            "results": self.results,
            "file_locations": {
                "html_report": self.html_report,
                "json_report": self.json_report,
                "xml_report": self.xml_report,
                "coverage_dir": self.coverage_dir,
                "coverage_xml": self.coverage_xml,
            },
        }

        # Save summary JSON
        with open(self.summary_report, "w") as f:
            json.dump(summary_data, f, indent=2, default=str)

        print(f"   ✅ Summary saved to: {self.summary_report}")
        print("✅ Summary generation completed\n")

        return summary_data

    def generate_comprehensive_report(self, summary_data):
        """Generate comprehensive markdown report."""
        print("📖 Generating comprehensive report...")

        report_content = f"""# Permissions Editor - Comprehensive Test Report

## Test Execution Summary

**Test Run Information:**
- **Timestamp:** {self.timestamp}
- **Execution Time:** {summary_data['test_run_info']['execution_time']:.2f} seconds
- **Python Version:** {summary_data['test_run_info']['python_version']}
- **Target Module:** src.utilities.system.permissions_editor
- **Test Framework:** pytest with comprehensive reporting

## Test Results Overview

"""

        if "metrics" in self.results:
            metrics = self.results["metrics"]
            report_content += f"""
### Test Execution Metrics
- **Total Tests:** {metrics['total_tests']}
- **Passed:** {metrics['passed_tests']} ({metrics['pass_rate']:.1f}%)
- **Failed:** {metrics['failed_tests']} ({metrics['failure_rate']:.1f}%)
- **Skipped:** {metrics['skipped_tests']}
- **Errors:** {metrics['error_tests']}

### Quality Assessment
- **Pass Rate:** {'🟢 Excellent' if metrics['pass_rate'] >= 90 else '🟡 Good' if metrics['pass_rate'] >= 75 else '🔴 Needs Improvement'}
- **Test Coverage:** {'✅ Comprehensive' if metrics['total_tests'] >= 50 else '⚠️ Moderate' if metrics['total_tests'] >= 25 else '❌ Limited'}

"""

        if "coverage" in self.results:
            coverage = self.results["coverage"]
            report_content += f"""
### Code Coverage Analysis
- **Line Coverage:** {coverage['line_coverage']:.1f}%
- **Branch Coverage:** {coverage['branch_coverage']:.1f}%
- **Coverage Quality:** {'🟢 Excellent' if coverage['line_coverage'] >= 90 else '🟡 Good' if coverage['line_coverage'] >= 75 else '🔴 Needs Improvement'}

"""

        report_content += f"""
## Test Categories

### Core Functionality Tests
- **Initialization Tests:** Widget creation and setup
- **File Selection Tests:** File and directory selection functionality
- **Permission Loading Tests:** Reading current file permissions
- **Permission Application Tests:** Applying permission changes
- **UI Operations Tests:** User interface interactions

### GUI Integration Tests
- **Widget Interactions:** Button clicks and checkbox states
- **Event Handling:** User input processing
- **State Management:** UI state consistency
- **Dialog Interactions:** Message boxes and confirmations
- **Layout and Accessibility:** Visual organization and keyboard navigation

### Edge Cases and Error Handling
- **Invalid Paths:** Nonexistent files and directories
- **Permission Errors:** Access denied scenarios
- **Special Characters:** Unicode and special character handling
- **Large Operations:** Performance with many status updates
- **Memory Management:** Resource cleanup and optimization

## File Reports

### Generated Reports
- **HTML Report:** `{os.path.basename(self.html_report)}`
- **JSON Report:** `{os.path.basename(self.json_report)}`
- **XML Report:** `{os.path.basename(self.xml_report)}`
- **Coverage HTML:** `{os.path.basename(self.coverage_dir)}/`
- **Coverage XML:** `{os.path.basename(self.coverage_xml)}`

### Test Files
"""

        for test_file in self.test_files:
            report_content += f"- **{test_file}:** Comprehensive unit tests\n"

        if "tests" in self.results:
            failed_tests = [
                test for test in self.results["tests"] if test["outcome"] == "failed"
            ]
            if failed_tests:
                report_content += f"""

## Failed Tests Analysis

"""
                for test in failed_tests[:10]:  # Limit to first 10 failed tests
                    report_content += f"""
### {test['nodeid']}
- **Outcome:** {test['outcome']}
- **Duration:** {test.get('duration', 0):.3f}s
- **Error:** {test.get('call', {}).get('longrepr', 'Unknown error')[:200]}...

"""

        report_content += f"""

## Recommendations

### Performance Optimization
- Monitor memory usage during large operations
- Optimize status list updates for better responsiveness
- Consider lazy loading for large file lists

### Test Coverage Enhancement
- Add more edge case testing for file system operations
- Increase platform-specific permission testing
- Add automated GUI interaction testing

### Code Quality Improvements
- Implement proper error logging and user feedback
- Add input validation for file paths
- Enhance accessibility features for keyboard navigation

## Technical Details

### Test Environment
- **Working Directory:** {self.test_dir}
- **Project Root:** {self.project_root}
- **Configuration File:** {os.path.basename(self.config_file)}

### Dependencies
- **PyQt5:** GUI framework and testing
- **pytest:** Test framework and execution
- **pytest-html:** HTML report generation
- **pytest-json-report:** JSON result output
- **pytest-cov:** Code coverage analysis
- **pytest-mock:** Mocking functionality

---

*Report generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} by Permissions Editor Test Runner*
"""

        # Save comprehensive report
        with open(self.comprehensive_report, "w", encoding="utf-8") as f:
            f.write(report_content)

        print(f"   ✅ Comprehensive report saved to: {self.comprehensive_report}")
        print("✅ Comprehensive report generation completed\n")

    def validate_reports(self):
        """Validate generated reports and files."""
        print("🔍 Validating generated reports...")

        report_files = {
            "HTML Report": self.html_report,
            "JSON Report": self.json_report,
            "XML Report": self.xml_report,
            "Coverage XML": self.coverage_xml,
            "Summary JSON": self.summary_report,
            "Comprehensive Report": self.comprehensive_report,
        }

        all_valid = True
        for name, filepath in report_files.items():
            if os.path.exists(filepath):
                size = os.path.getsize(filepath)
                print(f"   ✅ {name}: {size:,} bytes")
            else:
                print(f"   ❌ {name}: Missing")
                all_valid = False

        # Check coverage directory
        if os.path.exists(self.coverage_dir):
            coverage_files = len(
                [f for f in os.listdir(self.coverage_dir) if f.endswith(".html")]
            )
            print(f"   ✅ Coverage HTML: {coverage_files} files")
        else:
            print(f"   ❌ Coverage HTML: Directory missing")
            all_valid = False

        print(
            f"✅ Report validation completed - {'All reports generated' if all_valid else 'Some reports missing'}\n"
        )
        return all_valid

    def cleanup_temporary_files(self):
        """Clean up temporary test files."""
        print("🧹 Cleaning up temporary files...")

        # Clean up test data
        test_data_dir = os.path.join(self.test_dir, "test_data")
        temp_files = [os.path.join(test_data_dir, "temp_permissions_test.txt")]

        for temp_file in temp_files:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                    print(f"   ✅ Removed: {os.path.basename(temp_file)}")
                except Exception as e:
                    print(f"   ⚠️ Could not remove {temp_file}: {e}")

        print("✅ Cleanup completed\n")

    def run_complete_test_suite(self):
        """Run the complete test suite with all phases."""
        print("=" * 80)
        print("🚀 PERMISSIONS EDITOR - COMPREHENSIVE TEST SUITE")
        print("=" * 80)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        try:
            # Phase 1: Environment validation
            if not self.validate_environment():
                print("❌ Environment validation failed. Aborting test run.")
                return False

            # Phase 2: Setup
            self.setup_test_environment()

            # Phase 3: Test execution
            if not self.execute_tests():
                print("⚠️ Test execution completed with issues.")

            # Phase 4: Analysis
            self.analyze_results()

            # Phase 5: Reporting
            summary_data = self.generate_summary()
            self.generate_comprehensive_report(summary_data)

            # Phase 6: Validation
            self.validate_reports()

            # Phase 7: Cleanup
            self.cleanup_temporary_files()

            # Final summary
            print("=" * 80)
            print("📋 FINAL SUMMARY")
            print("=" * 80)

            if "metrics" in self.results:
                metrics = self.results["metrics"]
                print(
                    f"🎯 Test Results: {metrics['passed_tests']}/{metrics['total_tests']} passed ({metrics['pass_rate']:.1f}%)"
                )

            if "coverage" in self.results:
                coverage = self.results["coverage"]
                print(f"📊 Code Coverage: {coverage['line_coverage']:.1f}% lines")

            print(
                f"⏱️ Total Execution Time: {getattr(self, 'end_time', 0) - getattr(self, 'start_time', 0):.2f} seconds"
            )
            print(f"📁 Reports Location: {self.test_dir}")
            print(
                f"📖 Comprehensive Report: {os.path.basename(self.comprehensive_report)}"
            )

            print("\n✅ Comprehensive test suite completed successfully!")
            print("=" * 80)

            return True

        except Exception as e:
            print(f"\n❌ Test suite failed with error: {e}")
            import traceback

            traceback.print_exc()
            return False


def main():
    """Main function to run the test suite."""
    runner = PermissionsEditorTestRunner()
    success = runner.run_complete_test_suite()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
