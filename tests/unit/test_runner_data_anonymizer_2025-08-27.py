#!/usr/bin/env python3
"""
Test Runner for data_anonymizer.py Unit Tests

Script: test_runner_data_anonymizer_2025-08-27.py
Created: 2025-08-27
Purpose: Execute comprehensive unit tests with detailed reporting

This script runs the data_anonymizer unit tests and generates:
- HTML test report
- JSON test report  
- Coverage reports (HTML and JSON)
- Execution timestamp and detailed results
"""

import datetime
import json
import os
import subprocess
import sys
from pathlib import Path


class DataAnonymizerTestRunner:
    """Test runner for data_anonymizer.py unit tests."""
    
    def __init__(self):
        """Initialize the test runner."""
        self.test_dir = Path(__file__).parent
        self.project_root = self.test_dir.parent.parent
        self.date_str = "2025-08-27"
        self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # Output file paths
        self.html_report = self.test_dir / f"result_data_anonymizer_report_{self.date_str}.html"
        self.json_report = self.test_dir / f"result_data_anonymizer_report_{self.date_str}.json"
        self.coverage_html = self.test_dir / f"result_data_anonymizer_coverage_{self.date_str}"
        self.coverage_json = self.test_dir / f"result_data_anonymizer_coverage_{self.date_str}.json"
        self.execution_log = self.test_dir / f"result_data_anonymizer_execution_{self.date_str}.log"
        
    def ensure_dependencies(self):
        """Ensure required testing dependencies are installed."""
        required_packages = [
            'pytest',
            'pytest-html',
            'pytest-json-report',
            'pytest-cov',
            'pytest-mock',
            'coverage'
        ]
        
        print(f"[{self.timestamp}] Checking required dependencies...")
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            print(f"Installing missing packages: {', '.join(missing_packages)}")
            for package in missing_packages:
                subprocess.run([
                    sys.executable, '-m', 'pip', 'install', package
                ], check=True)
        
        print("All dependencies are available.")
    
    def prepare_environment(self):
        """Prepare the test environment."""
        print(f"[{self.timestamp}] Preparing test environment...")
        
        # Add project root to Python path
        if str(self.project_root) not in sys.path:
            sys.path.insert(0, str(self.project_root))
        
        # Create output directory if it doesn't exist
        self.test_dir.mkdir(parents=True, exist_ok=True)
        
        # Set environment variables
        os.environ['PYTHONPATH'] = str(self.project_root)
        os.environ['PYTEST_CURRENT_TEST'] = f"data_anonymizer_tests_{self.date_str}"
    
    def run_tests(self):
        """Execute the unit tests with comprehensive reporting."""
        print(f"[{self.timestamp}] Starting data_anonymizer unit tests...")
        
        # Construct pytest command
        test_file = self.test_dir / f"test_data_anonymizer_{self.date_str}.py"
        
        pytest_args = [
            sys.executable, '-m', 'pytest',
            str(test_file),
            '-v',  # Verbose output
            '--tb=short',  # Short traceback format
            '--strict-markers',
            '--strict-config',
            f'--html={self.html_report}',
            '--self-contained-html',
            '--json-report',
            f'--json-report-file={self.json_report}',
            f'--cov=src.tools.privacy.anonymizer.data_anonymizer',
            f'--cov-report=html:{self.coverage_html}',
            f'--cov-report=json:{self.coverage_json}',
            '--cov-report=term-missing',
            '--cov-fail-under=80',  # 80% coverage threshold
            '--capture=no',  # Don't capture output
        ]
        
        # Execute tests
        try:
            result = subprocess.run(
                pytest_args,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300  # 5-minute timeout
            )
            
            # Log execution details
            self._log_execution_details(result)
            
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            print("Test execution timed out after 5 minutes.")
            return False
        except Exception as e:
            print(f"Error executing tests: {e}")
            return False
    
    def _log_execution_details(self, result):
        """Log detailed execution results."""
        with open(self.execution_log, 'w', encoding='utf-8') as f:
            f.write(f"Data Anonymizer Test Execution Log\n")
            f.write(f"{'=' * 50}\n")
            f.write(f"Execution Date: {self.timestamp}\n")
            f.write(f"Target File: data_anonymizer.py\n")
            f.write(f"Test File: test_data_anonymizer_{self.date_str}.py\n")
            f.write(f"Return Code: {result.returncode}\n")
            f.write(f"\nSTDOUT:\n{'-' * 20}\n")
            f.write(result.stdout)
            f.write(f"\nSTDERR:\n{'-' * 20}\n")
            f.write(result.stderr)
            f.write(f"\nTest Reports Generated:\n{'-' * 25}\n")
            f.write(f"HTML Report: {self.html_report}\n")
            f.write(f"JSON Report: {self.json_report}\n")
            f.write(f"Coverage HTML: {self.coverage_html}\n")
            f.write(f"Coverage JSON: {self.coverage_json}\n")
        
        # Print summary to console
        print(f"\n{'=' * 60}")
        print(f"TEST EXECUTION SUMMARY - {self.timestamp}")
        print(f"{'=' * 60}")
        print(f"Return Code: {result.returncode}")
        print(f"Success: {'YES' if result.returncode == 0 else 'NO'}")
        
        if result.stdout:
            print(f"\nTest Output:\n{result.stdout}")
        
        if result.stderr:
            print(f"\nErrors/Warnings:\n{result.stderr}")
    
    def generate_summary_report(self):
        """Generate a comprehensive summary report."""
        summary_file = self.test_dir / f"result_data_anonymizer_summary_{self.date_str}.md"
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"# Data Anonymizer Unit Test Summary\n\n")
            f.write(f"**Execution Date:** {self.timestamp}\n")
            f.write(f"**Target Module:** data_anonymizer.py\n")
            f.write(f"**Test Framework:** pytest\n\n")
            
            f.write("## Test Files Generated\n\n")
            f.write(f"- **Test File:** `test_data_anonymizer_{self.date_str}.py`\n")
            f.write(f"- **HTML Report:** `result_data_anonymizer_report_{self.date_str}.html`\n")
            f.write(f"- **JSON Report:** `result_data_anonymizer_report_{self.date_str}.json`\n")
            f.write(f"- **Coverage HTML:** `result_data_anonymizer_coverage_{self.date_str}/`\n")
            f.write(f"- **Coverage JSON:** `result_data_anonymizer_coverage_{self.date_str}.json`\n")
            f.write(f"- **Execution Log:** `result_data_anonymizer_execution_{self.date_str}.log`\n\n")
            
            f.write("## Test Coverage Areas\n\n")
            f.write("The comprehensive test suite covers:\n\n")
            f.write("1. **Import Mechanism Testing**\n")
            f.write("   - Successful PrivacyCleanerGUI import\n")
            f.write("   - Fallback to SimplePrivacyHub\n")
            f.write("   - Error dialog creation\n")
            f.write("   - PyQt5 availability checks\n\n")
            
            f.write("2. **DataAnonymizerGUI Class Testing**\n")
            f.write("   - Error dialog initialization\n")
            f.write("   - Show method functionality\n")
            f.write("   - Message content validation\n")
            f.write("   - No-Qt fallback behavior\n\n")
            
            f.write("3. **Main Function Testing**\n")
            f.write("   - Successful execution path\n")
            f.write("   - Window title setting\n")
            f.write("   - PyQt5 import error handling\n")
            f.write("   - General exception handling\n")
            f.write("   - Application exit codes\n\n")
            
            f.write("4. **Edge Cases and Error Conditions**\n")
            f.write("   - Module attribute existence\n")
            f.write("   - sys.argv handling\n")
            f.write("   - Keyboard interrupt handling\n")
            f.write("   - Integration scenarios\n\n")
            
            f.write("## Test Configuration\n\n")
            f.write("- **Coverage Threshold:** 80%\n")
            f.write("- **Timeout:** 300 seconds\n")
            f.write("- **Mock Framework:** unittest.mock\n")
            f.write("- **Assertion Framework:** pytest\n\n")
            
            # Try to include JSON report data if available
            if self.json_report.exists():
                try:
                    with open(self.json_report, 'r') as json_file:
                        report_data = json.load(json_file)
                        
                    f.write("## Test Results\n\n")
                    f.write(f"- **Total Tests:** {report_data.get('summary', {}).get('total', 'N/A')}\n")
                    f.write(f"- **Passed:** {report_data.get('summary', {}).get('passed', 'N/A')}\n")
                    f.write(f"- **Failed:** {report_data.get('summary', {}).get('failed', 'N/A')}\n")
                    f.write(f"- **Skipped:** {report_data.get('summary', {}).get('skipped', 'N/A')}\n")
                    f.write(f"- **Duration:** {report_data.get('duration', 'N/A')} seconds\n\n")
                    
                except Exception:
                    f.write("## Test Results\n\n")
                    f.write("Test results will be available after execution.\n\n")
            
            f.write("## Files Location\n\n")
            f.write(f"All test files are located in: `{self.test_dir}`\n\n")
            f.write("## Usage\n\n")
            f.write("To run the tests manually:\n\n")
            f.write("```bash\n")
            f.write(f"cd {self.project_root}\n")
            f.write(f"python -m pytest {test_file} -v --html={self.html_report} --json-report\n")
            f.write("```\n")
        
        print(f"Summary report generated: {summary_file}")
    
    def run_complete_test_suite(self):
        """Run the complete test suite with all reporting."""
        print(f"Starting Data Anonymizer Test Suite - {self.timestamp}")
        print("=" * 60)
        
        try:
            # Step 1: Ensure dependencies
            self.ensure_dependencies()
            
            # Step 2: Prepare environment
            self.prepare_environment()
            
            # Step 3: Run tests
            success = self.run_tests()
            
            # Step 4: Generate summary
            self.generate_summary_report()
            
            # Final status
            status = "COMPLETED SUCCESSFULLY" if success else "COMPLETED WITH ISSUES"
            print(f"\nTest Suite {status}")
            print(f"Check {self.execution_log} for detailed logs")
            print(f"Check {self.html_report} for HTML report")
            
            return success
            
        except Exception as e:
            print(f"Test suite execution failed: {e}")
            return False


def main():
    """Main entry point for the test runner."""
    runner = DataAnonymizerTestRunner()
    success = runner.run_complete_test_suite()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()