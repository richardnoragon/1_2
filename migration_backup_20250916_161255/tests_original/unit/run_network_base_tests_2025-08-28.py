"""
Test runner for network_base.py comprehensive unit tests.
Created: 2025-08-28
Target: src/utilities/network/network_connectivity_complex/core/network_base.py

This script executes the comprehensive test suite for network_base.py,
generates detailed reports, and provides execution summary.
"""

import os
import sys
import subprocess
import json
import time
from datetime import datetime
from pathlib import Path


class NetworkBaseTestRunner:
    """Test runner for network_base.py unit tests."""
    
    def __init__(self):
        """Initialize the test runner."""
        self.start_time = datetime.now()
        self.test_file = "test_network_base_2025-08-28.py"
        self.config_file = "pytest_network_base_2025-08-28.ini"
        self.base_dir = Path(__file__).parent
        self.logs_dir = self.base_dir / "logs"
        self.results_dir = self.base_dir
        
        # Ensure directories exist
        self.logs_dir.mkdir(exist_ok=True)
        
        # Result files
        self.html_report = "result_network_base_2025-08-28.html"
        self.json_report = "result_network_base_2025-08-28.json"
        self.coverage_html = "coverage_network_base_2025-08-28"
        self.coverage_json = "result_network_base_coverage_2025-08-28.json"
        self.junit_xml = "result_network_base_2025-08-28.xml"
        self.summary_file = "result_network_base_summary_2025-08-28.txt"
        self.execution_log = self.logs_dir / "test_execution_network_base_2025-08-28.log"
    
    def check_dependencies(self):
        """Check if required dependencies are available."""
        print("Checking test dependencies...")
        
        required_packages = [
            'pytest', 'pytest-html', 'pytest-json-report', 
            'pytest-cov', 'pytest-mock', 'coverage'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            print(f"Missing required packages: {missing_packages}")
            print("Installing missing packages...")
            try:
                subprocess.run([
                    sys.executable, "-m", "pip", "install", 
                    "-r", "requirements_test_network_base_2025-08-28.txt"
                ], check=True, cwd=self.base_dir)
                print("Dependencies installed successfully.")
            except subprocess.CalledProcessError as e:
                print(f"Failed to install dependencies: {e}")
                return False
        
        return True
    
    def setup_environment(self):
        """Set up the test environment."""
        print("Setting up test environment...")
        
        # Add source paths to Python path
        src_paths = [
            self.base_dir.parent.parent / "src",
            self.base_dir.parent.parent / "src" / "utilities",
            self.base_dir.parent.parent / "src" / "utilities" / "network",
            self.base_dir.parent.parent / "src" / "core"
        ]
        
        for path in src_paths:
            if path.exists() and str(path) not in sys.path:
                sys.path.insert(0, str(path))
        
        # Set environment variables
        os.environ['PYTHONPATH'] = os.pathsep.join([str(p) for p in src_paths])
        os.environ['PYTEST_CURRENT_TEST'] = self.test_file
        
        print("Environment setup complete.")
    
    def run_tests(self):
        """Execute the test suite."""
        print(f"Running tests for network_base.py...")
        print(f"Test file: {self.test_file}")
        print(f"Start time: {self.start_time}")
        
        # Build pytest command
        cmd = [
            sys.executable, "-m", "pytest",
            self.test_file,
            f"-c={self.config_file}",
            "--verbose",
            "--tb=short",
            f"--html={self.html_report}",
            "--self-contained-html",
            f"--json-report-file={self.json_report}",
            "--json-report",
            f"--junitxml={self.junit_xml}",
            "--cov=utilities.network.network_connectivity_complex.core.network_base",
            f"--cov-report=html:{self.coverage_html}",
            f"--cov-report=json:{self.coverage_json}",
            "--cov-report=term-missing",
            "--durations=10",
            "--capture=no",
            "-x"  # Stop on first failure for debugging
        ]
        
        print(f"Executing command: {' '.join(cmd)}")
        
        try:
            # Execute tests with output capture
            with open(self.execution_log, 'w') as log_file:
                log_file.write(f"Test execution started: {self.start_time}\n")
                log_file.write(f"Command: {' '.join(cmd)}\n")
                log_file.write("-" * 80 + "\n")
                log_file.flush()
                
                result = subprocess.run(
                    cmd,
                    cwd=self.base_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    timeout=1800  # 30 minutes timeout
                )
                
                # Write output to log
                log_file.write(result.stdout)
                log_file.write(f"\nReturn code: {result.returncode}\n")
                log_file.write(f"Test execution completed: {datetime.now()}\n")
            
            # Print output to console
            print(result.stdout)
            
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            print("Test execution timed out after 30 minutes.")
            return False
        except Exception as e:
            print(f"Error executing tests: {e}")
            return False
    
    def generate_summary(self, test_success):
        """Generate test execution summary."""
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        print("Generating test summary...")
        
        summary_data = {
            "test_execution_summary": {
                "test_file": self.test_file,
                "target_module": "network_base.py",
                "execution_date": "2025-08-28",
                "start_time": self.start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_seconds": duration.total_seconds(),
                "duration_formatted": str(duration),
                "success": test_success,
                "test_framework": "pytest"
            },
            "output_files": {
                "html_report": self.html_report,
                "json_report": self.json_report,
                "junit_xml": self.junit_xml,
                "coverage_html": self.coverage_html,
                "coverage_json": self.coverage_json,
                "execution_log": str(self.execution_log),
                "summary_file": self.summary_file
            },
            "test_configuration": {
                "config_file": self.config_file,
                "coverage_config": ".coveragerc_network_base_2025-08-28",
                "requirements_file": "requirements_test_network_base_2025-08-28.txt"
            }
        }
        
        # Add test results if JSON report exists
        json_report_path = self.results_dir / self.json_report
        if json_report_path.exists():
            try:
                with open(json_report_path, 'r') as f:
                    test_results = json.load(f)
                
                summary_data["test_results"] = {
                    "total_tests": test_results.get("summary", {}).get("total", 0),
                    "passed": test_results.get("summary", {}).get("passed", 0),
                    "failed": test_results.get("summary", {}).get("failed", 0),
                    "skipped": test_results.get("summary", {}).get("skipped", 0),
                    "errors": test_results.get("summary", {}).get("error", 0),
                    "duration": test_results.get("duration", 0)
                }
            except Exception as e:
                print(f"Could not parse test results: {e}")
        
        # Add coverage information if available
        coverage_json_path = self.results_dir / self.coverage_json
        if coverage_json_path.exists():
            try:
                with open(coverage_json_path, 'r') as f:
                    coverage_data = json.load(f)
                
                summary_data["coverage"] = {
                    "line_coverage": coverage_data.get("totals", {}).get("percent_covered", 0),
                    "branch_coverage": coverage_data.get("totals", {}).get("percent_covered_display", "N/A"),
                    "lines_covered": coverage_data.get("totals", {}).get("covered_lines", 0),
                    "lines_missing": coverage_data.get("totals", {}).get("missing_lines", 0),
                    "total_lines": coverage_data.get("totals", {}).get("num_statements", 0)
                }
            except Exception as e:
                print(f"Could not parse coverage data: {e}")
        
        # Write summary to file
        summary_path = self.results_dir / self.summary_file
        with open(summary_path, 'w') as f:
            f.write("NETWORK_BASE.PY UNIT TEST EXECUTION SUMMARY\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated: {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("EXECUTION DETAILS:\n")
            f.write(f"  Test File: {self.test_file}\n")
            f.write(f"  Target Module: network_base.py\n")
            f.write(f"  Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"  End Time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"  Duration: {duration}\n")
            f.write(f"  Success: {test_success}\n\n")
            
            if "test_results" in summary_data:
                results = summary_data["test_results"]
                f.write("TEST RESULTS:\n")
                f.write(f"  Total Tests: {results['total_tests']}\n")
                f.write(f"  Passed: {results['passed']}\n")
                f.write(f"  Failed: {results['failed']}\n")
                f.write(f"  Skipped: {results['skipped']}\n")
                f.write(f"  Errors: {results['errors']}\n")
                f.write(f"  Test Duration: {results['duration']:.2f}s\n\n")
            
            if "coverage" in summary_data:
                coverage = summary_data["coverage"]
                f.write("COVERAGE ANALYSIS:\n")
                f.write(f"  Line Coverage: {coverage['line_coverage']:.2f}%\n")
                f.write(f"  Lines Covered: {coverage['lines_covered']}\n")
                f.write(f"  Lines Missing: {coverage['lines_missing']}\n")
                f.write(f"  Total Lines: {coverage['total_lines']}\n\n")
            
            f.write("OUTPUT FILES:\n")
            for file_type, filename in summary_data["output_files"].items():
                f.write(f"  {file_type.replace('_', ' ').title()}: {filename}\n")
        
        # Save JSON summary
        json_summary_path = self.results_dir / f"result_network_base_summary_2025-08-28.json"
        with open(json_summary_path, 'w') as f:
            json.dump(summary_data, f, indent=2, default=str)
        
        print(f"Summary saved to: {summary_path}")
        print(f"JSON summary saved to: {json_summary_path}")
        
        return summary_data
    
    def print_final_report(self, summary_data):
        """Print final execution report."""
        print("\n" + "=" * 60)
        print("NETWORK_BASE.PY UNIT TEST EXECUTION COMPLETE")
        print("=" * 60)
        
        execution = summary_data["test_execution_summary"]
        print(f"Execution Time: {execution['duration_formatted']}")
        print(f"Overall Success: {execution['success']}")
        
        if "test_results" in summary_data:
            results = summary_data["test_results"]
            print(f"Tests Run: {results['total_tests']}")
            print(f"Passed: {results['passed']}")
            print(f"Failed: {results['failed']}")
            if results['failed'] > 0:
                print("❌ Some tests failed!")
            else:
                print("✅ All tests passed!")
        
        if "coverage" in summary_data:
            coverage = summary_data["coverage"]
            print(f"Code Coverage: {coverage['line_coverage']:.2f}%")
        
        print("\nGenerated Reports:")
        for file_type, filename in summary_data["output_files"].items():
            if Path(self.results_dir / filename).exists():
                print(f"  ✅ {file_type.replace('_', ' ').title()}: {filename}")
            else:
                print(f"  ❌ {file_type.replace('_', ' ').title()}: {filename} (not found)")
        
        print("\n" + "=" * 60)
    
    def run(self):
        """Execute the complete test process."""
        print("NETWORK_BASE.PY COMPREHENSIVE UNIT TEST EXECUTION")
        print("=" * 60)
        print(f"Date: 2025-08-28")
        print(f"Target: network_base.py")
        print(f"Framework: pytest")
        print("=" * 60)
        
        try:
            # Check dependencies
            if not self.check_dependencies():
                print("❌ Dependency check failed!")
                return False
            
            # Setup environment
            self.setup_environment()
            
            # Run tests
            test_success = self.run_tests()
            
            # Generate summary
            summary_data = self.generate_summary(test_success)
            
            # Print final report
            self.print_final_report(summary_data)
            
            return test_success
            
        except KeyboardInterrupt:
            print("\n❌ Test execution interrupted by user.")
            return False
        except Exception as e:
            print(f"\n❌ Test execution failed with error: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Main entry point."""
    runner = NetworkBaseTestRunner()
    success = runner.run()
    
    if success:
        print("\n🎉 Test execution completed successfully!")
        return 0
    else:
        print("\n💥 Test execution failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())