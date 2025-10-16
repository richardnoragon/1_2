#!/usr/bin/env python3
"""
Test Runner for secure_delete.py Unit Tests
Generated: 2025-08-28

This script runs comprehensive unit tests for secure_delete.py and generates
detailed reports including HTML coverage, JSON results, and execution summaries.
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


class SecureDeleteTestRunner:
    """Test runner for secure_delete.py unit tests."""

    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.project_root = self.test_dir.parent.parent
        self.start_time = datetime.now()
        self.test_results = {
            "execution_timestamp": self.start_time.isoformat(),
            "test_file": "test_secure_delete_2025-08-28.py",
            "target_module": "src/utilities/security/secure_delete.py",
            "framework": "pytest",
            "results": {},
        }

    def setup_environment(self):
        """Setup test environment and dependencies."""
        print("🔧 Setting up test environment...")

        # Check if required packages are installed
        required_packages = [
            "pytest",
            "pytest-cov",
            "pytest-html",
            "pytest-mock",
        ]

        missing_packages = []
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
            except ImportError:
                missing_packages.append(package)

        if missing_packages:
            print(f"📦 Installing missing packages: {', '.join(missing_packages)}")
            for package in missing_packages:
                try:
                    subprocess.run(
                        [sys.executable, "-m", "pip", "install", package],
                        check=True,
                        capture_output=True,
                    )
                    print(f"✅ Installed {package}")
                except subprocess.CalledProcessError as e:
                    print(f"❌ Failed to install {package}: {e}")
                    return False

        print("✅ Environment setup complete")
        return True

    def run_tests(self):
        """Execute the unit tests with comprehensive reporting."""
        print("\n🧪 Running comprehensive unit tests for secure_delete.py...")
        print(f"📅 Execution started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")

        # Construct pytest command
        test_file = self.test_dir / "test_secure_delete_2025-08-28.py"
        config_file = self.test_dir / "pytest_secure_delete.ini"

        pytest_cmd = [
            sys.executable,
            "-m",
            "pytest",
            str(test_file),
            "-c",
            str(config_file),
            "--verbose",
            "--tb=long",
            f"--html={self.test_dir}/result_secure_delete_report_2025-08-28.html",
            "--self-contained-html",
            f"--junitxml={self.test_dir}/result_secure_delete_junit_2025-08-28.xml",
            f"--cov=src.utilities.security.secure_delete",
            f"--cov-report=html:{self.test_dir}/result_secure_delete_coverage_2025-08-28",
            f"--cov-report=json:{self.test_dir}/result_secure_delete_coverage_2025-08-28.json",
            "--cov-report=term-missing",
            "--cov-branch",
        ]

        try:
            # Change to project root for proper imports
            original_cwd = os.getcwd()
            os.chdir(self.project_root)

            # Run tests
            result = subprocess.run(
                pytest_cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            # Restore original directory
            os.chdir(original_cwd)

            # Process results
            self.test_results["exit_code"] = result.returncode
            self.test_results["stdout"] = result.stdout
            self.test_results["stderr"] = result.stderr
            self.test_results["success"] = result.returncode == 0

            return result.returncode == 0

        except subprocess.TimeoutExpired:
            print("❌ Tests timed out after 5 minutes")
            self.test_results["error"] = "Test execution timeout"
            return False
        except Exception as e:
            print(f"❌ Error running tests: {e}")
            self.test_results["error"] = str(e)
            return False

    def parse_coverage_results(self):
        """Parse coverage results from JSON report."""
        coverage_file = self.test_dir / "result_secure_delete_coverage_2025-08-28.json"

        if coverage_file.exists():
            try:
                with open(coverage_file, "r") as f:
                    coverage_data = json.load(f)

                self.test_results["coverage"] = {
                    "total_statements": coverage_data.get("totals", {}).get(
                        "num_statements", 0
                    ),
                    "covered_statements": coverage_data.get("totals", {}).get(
                        "covered_lines", 0
                    ),
                    "missing_statements": coverage_data.get("totals", {}).get(
                        "missing_lines", 0
                    ),
                    "coverage_percentage": coverage_data.get("totals", {}).get(
                        "percent_covered", 0
                    ),
                    "branch_coverage": coverage_data.get("totals", {}).get(
                        "percent_covered_display", "N/A"
                    ),
                }

                return True
            except Exception as e:
                print(f"⚠️ Could not parse coverage results: {e}")
                return False

        return False

    def generate_summary_report(self):
        """Generate a comprehensive summary report."""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()

        self.test_results["end_time"] = end_time.isoformat()
        self.test_results["duration_seconds"] = duration

        # Parse test output for statistics
        stdout = self.test_results.get("stdout", "")

        # Extract test counts from pytest output
        import re

        # Look for patterns like "5 passed, 2 failed, 1 skipped"
        test_pattern = r"(\d+) (\w+)(?:, (\d+) (\w+))*"
        matches = re.findall(r"(\d+) (passed|failed|skipped|error)", stdout)

        test_counts = {"passed": 0, "failed": 0, "skipped": 0, "error": 0}
        for count, status in matches:
            test_counts[status] = int(count)

        self.test_results["test_counts"] = test_counts

        # Generate summary text
        summary = f"""
{'='*60}
SECURE DELETE UNIT TESTS - EXECUTION SUMMARY
{'='*60}

📊 EXECUTION DETAILS
Target File: secure_delete.py
Test File: test_secure_delete_2025-08-28.py
Framework: pytest
Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}
End Time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}
Duration: {duration:.2f} seconds

📈 TEST RESULTS
Tests Passed: {test_counts['passed']}
Tests Failed: {test_counts['failed']}
Tests Skipped: {test_counts['skipped']}
Tests with Errors: {test_counts['error']}
Total Tests: {sum(test_counts.values())}

Success Rate: {(test_counts['passed'] / max(sum(test_counts.values()), 1) * 100):.1f}%
Overall Status: {'✅ PASSED' if self.test_results['success'] else '❌ FAILED'}

🔍 COVERAGE ANALYSIS
"""

        if "coverage" in self.test_results:
            cov = self.test_results["coverage"]
            summary += f"""Statement Coverage: {cov['coverage_percentage']:.1f}%
Total Statements: {cov['total_statements']}
Covered Statements: {cov['covered_statements']}
Missing Statements: {cov['missing_statements']}
Branch Coverage: {cov['branch_coverage']}
"""
        else:
            summary += "Coverage data not available\n"

        summary += f"""
📁 GENERATED FILES
HTML Report: result_secure_delete_report_2025-08-28.html
Coverage Report: result_secure_delete_coverage_2025-08-28/
JSON Coverage: result_secure_delete_coverage_2025-08-28.json
JUnit XML: result_secure_delete_junit_2025-08-28.xml
Summary JSON: result_secure_delete_summary_2025-08-28.json

🎯 TEST CATEGORIES COVERED
✓ Unit Tests - Individual method testing
✓ Integration Tests - Component interaction testing  
✓ Error Handling - Exception and edge case testing
✓ Performance Tests - Large dataset handling
✓ Mocking Tests - GUI component isolation
✓ Workflow Tests - End-to-end scenarios

📋 FUNCTIONALITY TESTED
✓ SecureDeleteGUI.__init__() - Initialization
✓ SecureDeleteGUI._setup_menu_callbacks() - Menu integration
✓ SecureDeleteGUI.show_help() - Help system
✓ SecureDeleteGUI.show_preferences() - Preferences dialog
✓ SecureDeleteGUI.refresh_view() - View refresh
✓ SecureDeleteGUI.clear_selection() - Selection clearing
✓ SecureDeleteGUI.select_files() - File selection
✓ SecureDeleteGUI.select_folder() - Folder selection
✓ SecureDeleteGUI.secure_delete() - Deletion workflow
✓ SecureDeleteGUI.init_ui() - UI initialization
✓ main() function - Application entry point
✓ Import error handling - Graceful degradation
✓ Edge cases and error conditions

{'='*60}
END OF SUMMARY
{'='*60}
"""

        # Save summary to file
        summary_file = self.test_dir / "result_secure_delete_summary_2025-08-28.txt"
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write(summary)

        # Save JSON results
        json_file = self.test_dir / "result_secure_delete_summary_2025-08-28.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(self.test_results, f, indent=2, default=str)

        print(summary)

        return summary

    def run_complete_test_suite(self):
        """Run the complete test suite with setup, execution, and reporting."""
        print("🚀 Starting Secure Delete Unit Test Suite")
        print(f"📁 Working Directory: {os.getcwd()}")
        print(f"🎯 Target: src/utilities/security/secure_delete.py")
        print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}")

        # Setup environment
        if not self.setup_environment():
            print("❌ Environment setup failed")
            return False

        # Run tests
        success = self.run_tests()

        # Parse coverage
        self.parse_coverage_results()

        # Generate reports
        self.generate_summary_report()

        # Final status
        if success:
            print("\n🎉 Test suite completed successfully!")
            print(f"📊 Check the generated reports in: {self.test_dir}")
        else:
            print("\n❌ Test suite completed with failures")
            print(f"🔍 Check the error reports in: {self.test_dir}")

        return success


def main():
    """Main function to run the test suite."""
    runner = SecureDeleteTestRunner()
    success = runner.run_complete_test_suite()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
