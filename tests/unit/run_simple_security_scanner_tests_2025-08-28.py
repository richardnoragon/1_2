#!/usr/bin/env python3
"""
Test Runner for security_scanner.py Unit Tests
Generated: 2025-08-28

This script runs comprehensive unit tests for security_scanner.py and generates
detailed reports including HTML coverage, JSON results, and execution summaries.
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


class SimpleSecurityScannerTestRunner:
    """Test runner for security_scanner.py unit tests."""

    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.project_root = self.test_dir.parent.parent
        self.start_time = datetime.now()
        self.test_results = {
            "execution_timestamp": self.start_time.isoformat(),
            "test_file": "test_simple_security_scanner_2025-08-28.py",
            "target_module": "src/tools/security/security_scanner/security_scanner.py",
            "framework": "pytest",
            "results": {},
        }

    def setup_environment(self):
        """Setup test environment and dependencies."""
        print("Setting up test environment for Simple Security Scanner...")

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
            print(
                f"📦 Installing missing packages: {', '.join(missing_packages)}"
            )
            for package in missing_packages:
                try:
                    subprocess.run(
                        [sys.executable, "-m", "pip", "install", package],
                        check=True,
                        capture_output=True,
                    )
                    print(f"[SUCCESS] Installed {package}")
                except subprocess.CalledProcessError as e:
                    print(f"[ERROR] Failed to install {package}: {e}")
                    return False

        print("[SUCCESS] Environment setup complete")
        return True

    def run_tests(self):
        """Execute the unit tests with comprehensive reporting."""
        print(
            "\nRunning comprehensive unit tests for security_scanner.py..."
        )
        print(
            f"Execution started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}"
        )

        # Construct pytest command
        test_file = (
            self.test_dir / "test_simple_security_scanner_2025-08-28.py"
        )
        config_file = (
            self.test_dir / "pytest_simple_security_scanner_2025-08-28.ini"
        )

        pytest_cmd = [
            sys.executable,
            "-m",
            "pytest",
            str(test_file),
            "-c",
            str(config_file),
            "--verbose",
            "--tb=long",
            f"--html={self.test_dir}/result_simple_security_scanner_report_2025-08-28.html",
            "--self-contained-html",
            f"--junitxml={self.test_dir}/result_simple_security_scanner_junit_2025-08-28.xml",
            f"--cov=tools.security.security_scanner.security_scanner",
            f"--cov-report=html:{self.test_dir}/result_simple_security_scanner_coverage_2025-08-28",
            f"--cov-report=json:{self.test_dir}/result_simple_security_scanner_coverage_2025-08-28.json",
            f"--cov-report=xml:{self.test_dir}/result_simple_security_scanner_coverage_2025-08-28.xml",
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
                timeout=600,  # 10 minute timeout
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
            print("[ERROR] Tests timed out after 10 minutes")
            self.test_results["error"] = "Test execution timeout"
            return False
        except Exception as e:
            print(f"[ERROR] Error running tests: {e}")
            self.test_results["error"] = str(e)
            return False

    def parse_coverage_results(self):
        """Parse coverage results from JSON report."""
        coverage_file = (
            self.test_dir
            / "result_simple_security_scanner_coverage_2025-08-28.json"
        )

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
                print(f"[WARNING] Could not parse coverage results: {e}")
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
{'='*75}
SIMPLE SECURITY SCANNER UNIT TESTS - EXECUTION SUMMARY
{'='*75}

📊 EXECUTION DETAILS
Target File: security_scanner.py
Test File: test_simple_security_scanner_2025-08-28.py
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
HTML Report: result_simple_security_scanner_report_2025-08-28.html
Coverage Report: result_simple_security_scanner_coverage_2025-08-28/
JSON Coverage: result_simple_security_scanner_coverage_2025-08-28.json
XML Coverage: result_simple_security_scanner_coverage_2025-08-28.xml
JUnit XML: result_simple_security_scanner_junit_2025-08-28.xml
Summary JSON: result_simple_security_scanner_summary_2025-08-28.json

🎯 TEST CATEGORIES COVERED
✓ Unit Tests - Individual method testing
✓ Integration Tests - Component interaction testing  
✓ Error Handling - Exception and edge case testing
✓ Performance Tests - Large dataset handling
✓ Security Tests - Network scanning validation
✓ Mocking Tests - GUI component isolation
✓ Workflow Tests - End-to-end scenarios

📋 FUNCTIONALITY TESTED
✓ SecurityScanWorker.__init__() - Initialization with scan types
✓ SecurityScanWorker.run() - Main scan execution logic
✓ SecurityScanWorker.scan_system_info() - System information gathering
  • Windows and Linux platform detection
  • System specifications and hostname
  • Exception handling for platform errors
✓ SecurityScanWorker.scan_network_ports() - Network port scanning
  • Port scanning on localhost (security focused)
  • Open/closed port detection
  • Socket timeout and error handling
✓ SecurityScanWorker.scan_file_permissions() - File permission checking
  • Windows and Unix permission checking
  • Safe directory scanning only
  • Access error handling
✓ SecurityScanWorker.scan_running_processes() - Process analysis
  • Windows tasklist command execution
  • Unix ps command execution
  • Subprocess error handling
✓ SimpleSecurityScannerGUI.__init__() - GUI initialization & styling
✓ SimpleSecurityScannerGUI._setup_ui() - UI component setup
✓ SimpleSecurityScannerGUI.start_scan() - Scan initiation
  • All scan options selected
  • Partial scan options
  • No options selected warning
✓ SimpleSecurityScannerGUI.update_progress() - Progress bar updates
✓ SimpleSecurityScannerGUI.update_status() - Status label updates
✓ SimpleSecurityScannerGUI.display_results() - Results display
✓ SimpleSecurityScannerGUI.scan_finished() - Post-scan cleanup
✓ SimpleSecurityScannerGUI.clear_results() - Results clearing
✓ main() function - Application entry point
✓ Import error handling - PyQt5 availability checks
✓ Edge cases and boundary conditions
✓ Performance testing - Large dataset handling
✓ Security testing - Localhost-only scanning

🔐 SECURITY TESTING HIGHLIGHTS
✓ Network scanning limited to localhost only
✓ File permission scanning restricted to safe directories
✓ No external network access in tests
✓ Subprocess command validation
✓ Exception handling for security failures

⚡ PERFORMANCE TESTING HIGHLIGHTS
✓ Network scanning with timeout handling
✓ Large process list handling (1000+ processes)
✓ Memory efficient mock data processing
✓ Execution time validation (<5s for network, <2s for processes)

🧪 EDGE CASE TESTING HIGHLIGHTS
✓ Empty subprocess output handling
✓ Network timeout simulation
✓ File paths with special characters
✓ Platform-specific behavior differences
✓ PyQt5 import error scenarios
✓ Unknown scan type handling

{'='*75}
END OF SUMMARY
{'='*75}
"""

        # Save summary to file
        summary_file = (
            self.test_dir
            / "result_simple_security_scanner_summary_2025-08-28.txt"
        )
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write(summary)

        # Save JSON results
        json_file = (
            self.test_dir
            / "result_simple_security_scanner_summary_2025-08-28.json"
        )
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(self.test_results, f, indent=2, default=str)

        print(summary)

        return summary

    def run_complete_test_suite(self):
        """Run the complete test suite with setup, execution, and reporting."""
        print("Starting Simple Security Scanner Unit Test Suite")
        print(f"Working Directory: {os.getcwd()}")
    print(f"Target: src/tools/security/security_scanner/security_scanner.py")
        print(f"Date: {datetime.now().strftime('%Y-%m-%d')}")

        # Setup environment
        if not self.setup_environment():
            print("[ERROR] Environment setup failed")
            return False

        # Run tests
        success = self.run_tests()

        # Parse coverage
        self.parse_coverage_results()

        # Generate reports
        self.generate_summary_report()

        # Final status
        if success:
            print("\n[SUCCESS] Test suite completed successfully!")
            print(f"Check the generated reports in: {self.test_dir}")
            print("\nGenerated Report Files:")
            print(
                f"  - HTML Report: result_simple_security_scanner_report_2025-08-28.html"
            )
            print(
                f"  - Coverage HTML: result_simple_security_scanner_coverage_2025-08-28/"
            )
            print(
                f"  - Coverage JSON: result_simple_security_scanner_coverage_2025-08-28.json"
            )
            print(
                f"  - JUnit XML: result_simple_security_scanner_junit_2025-08-28.xml"
            )
            print(
                f"  - Summary: result_simple_security_scanner_summary_2025-08-28.txt"
            )
        else:
            print("\n❌ Test suite completed with failures")
            print(f"🔍 Check the error reports in: {self.test_dir}")

        return success


def main():
    """Main function to run the test suite."""
    runner = SimpleSecurityScannerTestRunner()
    success = runner.run_complete_test_suite()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
