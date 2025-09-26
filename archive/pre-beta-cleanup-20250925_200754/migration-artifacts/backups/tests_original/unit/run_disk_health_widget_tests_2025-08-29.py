"""
Automated test runner for disk_health_widget.py

Runner file: run_disk_health_widget_tests_2025-08-29.py
Target test files: test_disk_health_widget_*.py files
Created: 2025-08-29
Framework: pytest with automated reporting

This script runs all disk health widget tests and generates comprehensive reports.
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


class DiskHealthWidgetTestRunner:
    """Comprehensive test runner for disk health widget tests."""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.test_directory = Path("c:/Users/richardi/1_2/tests/unit")
        self.results_directory = self.test_directory
        self.timestamp = "2025-08-29"
        
        # Test file patterns
        self.test_files = [
            f"test_disk_health_widget_{self.timestamp}.py",
            f"test_disk_health_widget_clean_{self.timestamp}.py", 
            f"test_disk_health_widget_mock_{self.timestamp}.py"
        ]
        
        # Result files
        self.result_files = {
            'html_report': f"result_disk_health_widget_test_report_{self.timestamp}.html",
            'xml_report': f"result_disk_health_widget_junit_{self.timestamp}.xml",
            'json_report': f"result_disk_health_widget_json_{self.timestamp}.json",
            'coverage_report': f"result_disk_health_widget_coverage_{self.timestamp}.html",
            'execution_log': f"result_disk_health_widget_execution_log_{self.timestamp}.txt",
            'summary_report': f"result_disk_health_widget_summary_{self.timestamp}.json"
        }
        
        # Test execution results
        self.test_results = {}
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.skipped_tests = 0
        self.execution_times = {}
    
    def setup_environment(self):
        """Setup test environment and verify dependencies."""
        print("Setting up test environment...")
        
        # Ensure test directory exists
        self.test_directory.mkdir(parents=True, exist_ok=True)
        
        # Check Python version
        python_version = sys.version_info
        print(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        # Verify pytest installation
        try:
            import pytest
            print(f"pytest version: {pytest.__version__}")
        except ImportError:
            print("ERROR: pytest not installed. Installing...")
            subprocess.run([sys.executable, "-m", "pip", "install", "pytest"], check=True)
        
        # Verify additional testing packages
        required_packages = ["pytest-html", "pytest-cov", "pytest-json-report"]
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
                print(f"{package}: Available")
            except ImportError:
                print(f"{package}: Not found, installing...")
                subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)
        
        print("Environment setup complete.\n")
    
    def verify_test_files(self):
        """Verify all test files exist."""
        print("Verifying test files...")
        
        missing_files = []
        for test_file in self.test_files:
            file_path = self.test_directory / test_file
            if file_path.exists():
                print(f"✓ Found: {test_file}")
            else:
                print(f"✗ Missing: {test_file}")
                missing_files.append(test_file)
        
        if missing_files:
            print(f"\nERROR: Missing test files: {missing_files}")
            return False
        
        print("All test files verified.\n")
        return True
    
    def run_individual_test_file(self, test_file):
        """Run individual test file with detailed reporting."""
        print(f"Running {test_file}...")
        
        file_path = self.test_directory / test_file
        base_name = test_file.replace(".py", "")
        
        # Create individual result file names
        html_file = self.results_directory / f"result_{base_name}_report.html"
        xml_file = self.results_directory / f"result_{base_name}_junit.xml"
        json_file = self.results_directory / f"result_{base_name}_json.json"
        
        # Pytest command with comprehensive reporting
        cmd = [
            sys.executable, "-m", "pytest",
            str(file_path),
            "-v", "--tb=short",
            f"--html={html_file}",
            f"--junitxml={xml_file}",
            f"--json-report", f"--json-report-file={json_file}",
            "--json-report-summary"
        ]
        
        # Run test with timing
        start_time = time.time()
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(self.test_directory)
            )
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Store results
            self.execution_times[test_file] = execution_time
            self.test_results[test_file] = {
                'return_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'execution_time': execution_time,
                'html_report': str(html_file),
                'xml_report': str(xml_file),
                'json_report': str(json_file)
            }
            
            # Parse test counts from output
            self._parse_test_results(result.stdout, test_file)
            
            if result.returncode == 0:
                print(f"✓ {test_file} completed successfully ({execution_time:.2f}s)")
            else:
                print(f"✗ {test_file} failed (return code: {result.returncode})")
                print(f"Error output: {result.stderr}")
            
        except Exception as e:
            print(f"✗ Error running {test_file}: {e}")
            self.test_results[test_file] = {
                'error': str(e),
                'execution_time': 0
            }
        
        print()
    
    def _parse_test_results(self, output, test_file):
        """Parse test results from pytest output."""
        lines = output.split('\n')
        
        for line in lines:
            if "passed" in line or "failed" in line or "error" in line:
                # Extract test counts (simplified parsing)
                if " passed" in line:
                    try:
                        parts = line.split()
                        for i, part in enumerate(parts):
                            if "passed" in part and i > 0:
                                passed = int(parts[i-1])
                                self.passed_tests += passed
                                break
                    except (ValueError, IndexError):
                        pass
                
                if " failed" in line:
                    try:
                        parts = line.split()
                        for i, part in enumerate(parts):
                            if "failed" in part and i > 0:
                                failed = int(parts[i-1])
                                self.failed_tests += failed
                                break
                    except (ValueError, IndexError):
                        pass
    
    def run_all_tests(self):
        """Run all test files."""
        print("Starting comprehensive test execution...\n")
        
        for test_file in self.test_files:
            self.run_individual_test_file(test_file)
        
        # Calculate totals
        self.total_tests = self.passed_tests + self.failed_tests + self.skipped_tests
    
    def run_combined_tests(self):
        """Run all tests together for combined reporting."""
        print("Running combined test suite...")
        
        # Combined test command
        test_patterns = [str(self.test_directory / pattern) for pattern in self.test_files]
        
        html_file = self.results_directory / self.result_files['html_report']
        xml_file = self.results_directory / self.result_files['xml_report']
        json_file = self.results_directory / self.result_files['json_report']
        
        cmd = [
            sys.executable, "-m", "pytest"
        ] + test_patterns + [
            "-v", "--tb=short",
            f"--html={html_file}",
            f"--junitxml={xml_file}",
            f"--json-report", f"--json-report-file={json_file}",
            "--json-report-summary"
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(self.test_directory)
            )
            
            print(f"Combined tests completed (return code: {result.returncode})")
            
            if result.returncode == 0:
                print("✓ All combined tests passed")
            else:
                print("✗ Some combined tests failed")
                print(f"Error output: {result.stderr}")
            
        except Exception as e:
            print(f"Error running combined tests: {e}")
    
    def generate_execution_log(self):
        """Generate detailed execution log."""
        log_file = self.results_directory / self.result_files['execution_log']
        
        with open(log_file, 'w') as f:
            f.write(f"Disk Health Widget Test Execution Log\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write(f"Start Time: {self.start_time.isoformat()}\n")
            f.write("=" * 50 + "\n\n")
            
            f.write("Test Files Executed:\n")
            for test_file in self.test_files:
                f.write(f"- {test_file}\n")
            f.write("\n")
            
            f.write("Execution Results:\n")
            for test_file, results in self.test_results.items():
                f.write(f"\n{test_file}:\n")
                f.write(f"  Return Code: {results.get('return_code', 'N/A')}\n")
                f.write(f"  Execution Time: {results.get('execution_time', 0):.2f}s\n")
                
                if 'error' in results:
                    f.write(f"  Error: {results['error']}\n")
                
                if 'stdout' in results:
                    f.write(f"  Output:\n")
                    for line in results['stdout'].split('\n')[:10]:  # First 10 lines
                        f.write(f"    {line}\n")
                    if len(results['stdout'].split('\n')) > 10:
                        f.write("    ... (truncated)\n")
        
        print(f"Execution log written to: {log_file}")
    
    def generate_summary_report(self):
        """Generate comprehensive summary report."""
        end_time = datetime.now()
        total_execution_time = end_time - self.start_time
        
        summary = {
            'disk_health_widget_test_summary': {
                'execution_metadata': {
                    'start_time': self.start_time.isoformat(),
                    'end_time': end_time.isoformat(),
                    'total_execution_time': str(total_execution_time),
                    'timestamp': self.timestamp,
                    'runner_script': 'run_disk_health_widget_tests_2025-08-29.py'
                },
                'test_files': {
                    'total_files': len(self.test_files),
                    'files_executed': list(self.test_files),
                    'individual_execution_times': self.execution_times
                },
                'test_results': {
                    'total_tests': self.total_tests,
                    'passed_tests': self.passed_tests,
                    'failed_tests': self.failed_tests,
                    'skipped_tests': self.skipped_tests,
                    'success_rate': f"{(self.passed_tests / max(self.total_tests, 1)) * 100:.1f}%"
                },
                'output_files': {
                    'html_reports': [
                        self.result_files['html_report'],
                        f"result_test_disk_health_widget_{self.timestamp}_report.html",
                        f"result_test_disk_health_widget_clean_{self.timestamp}_report.html",
                        f"result_test_disk_health_widget_mock_{self.timestamp}_report.html"
                    ],
                    'xml_reports': [
                        self.result_files['xml_report'],
                        f"result_test_disk_health_widget_{self.timestamp}_junit.xml",
                        f"result_test_disk_health_widget_clean_{self.timestamp}_junit.xml",
                        f"result_test_disk_health_widget_mock_{self.timestamp}_junit.xml"
                    ],
                    'json_reports': [
                        self.result_files['json_report'],
                        f"result_test_disk_health_widget_{self.timestamp}_json.json",
                        f"result_test_disk_health_widget_clean_{self.timestamp}_json.json",
                        f"result_test_disk_health_widget_mock_{self.timestamp}_json.json"
                    ],
                    'execution_log': self.result_files['execution_log'],
                    'summary_report': self.result_files['summary_report']
                },
                'individual_test_results': self.test_results
            }
        }
        
        # Write summary report
        summary_file = self.results_directory / self.result_files['summary_report']
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        print(f"Summary report written to: {summary_file}")
        return summary
    
    def print_final_summary(self):
        """Print final execution summary."""
        end_time = datetime.now()
        total_time = end_time - self.start_time
        
        print("\n" + "=" * 60)
        print("DISK HEALTH WIDGET TEST EXECUTION SUMMARY")
        print("=" * 60)
        print(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"End Time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total Execution Time: {total_time}")
        print()
        print(f"Test Files: {len(self.test_files)}")
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.failed_tests}")
        print(f"Skipped: {self.skipped_tests}")
        
        if self.total_tests > 0:
            success_rate = (self.passed_tests / self.total_tests) * 100
            print(f"Success Rate: {success_rate:.1f}%")
        
        print()
        print("Individual Test Execution Times:")
        for test_file, exec_time in self.execution_times.items():
            print(f"  {test_file}: {exec_time:.2f}s")
        
        print()
        print("Generated Reports:")
        for report_type, filename in self.result_files.items():
            report_path = self.results_directory / filename
            if report_path.exists():
                print(f"  ✓ {filename}")
            else:
                print(f"  ✗ {filename} (not generated)")
        
        print("=" * 60)
    
    def run(self):
        """Execute complete test suite."""
        print("Disk Health Widget Comprehensive Test Runner")
        print(f"Timestamp: {self.timestamp}")
        print("=" * 50)
        
        try:
            # Setup and verification
            self.setup_environment()
            
            if not self.verify_test_files():
                return False
            
            # Run tests
            self.run_individual_tests()
            self.run_combined_tests()
            
            # Generate reports
            self.generate_execution_log()
            self.generate_summary_report()
            
            # Final summary
            self.print_final_summary()
            
            return True
            
        except Exception as e:
            print(f"CRITICAL ERROR in test runner: {e}")
            return False
    
    def run_individual_tests(self):
        """Run individual test files."""
        self.run_all_tests()


def main():
    """Main execution function."""
    runner = DiskHealthWidgetTestRunner()
    success = runner.run()
    
    if success:
        print("\nTest execution completed successfully!")
        return 0
    else:
        print("\nTest execution completed with errors!")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)