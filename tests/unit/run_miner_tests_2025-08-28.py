#!/usr/bin/env python3
"""
Test Runner for miner.py Unit Tests
Created: 2025-08-28
Executes comprehensive tests with detailed reporting and coverage analysis
"""

import os
import sys
import time
import json
import subprocess
import platform
from datetime import datetime
from pathlib import Path


class MinerTestRunner:
    """Test runner for miner.py unit tests"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.test_dir = Path(__file__).parent
        self.project_root = self.test_dir.parent.parent
        self.results_dir = self.test_dir
        
        # Test configuration
        self.test_file = "test_miner_2025-08-28.py"
        self.config_file = "pytest_miner_2025-08-28.ini"
        self.conftest_file = "conftest_miner_2025-08-28.py"
        
        # Output files
        self.html_report = "result_miner_2025-08-28.html"
        self.json_report = "result_miner_2025-08-28.json"
        self.junit_xml = "result_miner_2025-08-28.xml"
        self.coverage_html = "coverage_miner_2025-08-28/"
        self.coverage_json = "result_miner_coverage_2025-08-28.json"
        self.execution_log = "result_miner_execution_2025-08-28.log"
        self.summary_file = "result_miner_summary_2025-08-28.txt"
        
    def setup_environment(self):
        """Setup test environment and dependencies"""
        print("Setting up test environment...")
        
        # Ensure logs directory exists
        logs_dir = self.test_dir / "logs"
        logs_dir.mkdir(exist_ok=True)
        
        # Add project src to Python path
        src_path = str(self.project_root / "src")
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        
        # Set environment variables
        os.environ['PYTHONPATH'] = str(self.project_root / "src")
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'  # For headless GUI testing
        
        print(f"Python path: {sys.path[0]}")
        print(f"Working directory: {os.getcwd()}")
        print(f"Test directory: {self.test_dir}")
        
    def check_dependencies(self):
        """Check if all required dependencies are available"""
        print("Checking dependencies...")
        
        required_packages = [
            'pytest',
            'pytest-html',
            'pytest-json-report',
            'pytest-cov',
            'PyQt5',
            'PyMuPDF'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            print(f"Missing packages: {missing_packages}")
            print("Installing missing packages...")
            for package in missing_packages:
                subprocess.run([sys.executable, '-m', 'pip', 'install', package], 
                             check=True)
        
        print("All dependencies satisfied.")
    
    def run_tests(self):
        """Execute the test suite"""
        print(f"Running tests for {self.test_file}...")
        
        # Change to test directory
        os.chdir(self.test_dir)
        
        # Build pytest command
        pytest_cmd = [
            sys.executable, '-m', 'pytest',
            self.test_file,
            f'-c={self.config_file}',
            f'--html={self.html_report}',
            '--self-contained-html',
            f'--json-report-file={self.json_report}',
            f'--junit-xml={self.junit_xml}',
            f'--cov=src.utilities.pdf_tools.pdf_view_analysis.miner',
            f'--cov-report=html:{self.coverage_html}',
            f'--cov-report=json:{self.coverage_json}',
            '--cov-report=term-missing',
            '--cov-fail-under=80',
            '-v',
            '--tb=short',
            '--durations=10',
            '--maxfail=10'
        ]
        
        print(f"Executing: {' '.join(pytest_cmd)}")
        
        # Execute tests
        with open(self.execution_log, 'w') as log_file:
            result = subprocess.run(
                pytest_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=self.test_dir
            )
            
            # Write output to log file
            log_file.write(result.stdout)
            
            # Also print to console
            print(result.stdout)
        
        return result.returncode == 0
    
    def generate_summary(self, test_success):
        """Generate test execution summary"""
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        summary = {
            "test_execution_summary": {
                "timestamp": self.start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_seconds": duration.total_seconds(),
                "test_file": self.test_file,
                "test_success": test_success,
                "platform": {
                    "system": platform.system(),
                    "release": platform.release(),
                    "python_version": platform.python_version(),
                    "architecture": platform.architecture()[0]
                },
                "output_files": {
                    "html_report": self.html_report,
                    "json_report": self.json_report,
                    "junit_xml": self.junit_xml,
                    "coverage_html": self.coverage_html,
                    "coverage_json": self.coverage_json,
                    "execution_log": self.execution_log,
                    "summary_file": self.summary_file
                }
            }
        }
        
        # Load test results if available
        try:
            if os.path.exists(self.json_report):
                with open(self.json_report, 'r') as f:
                    test_results = json.load(f)
                    summary["test_results"] = {
                        "total_tests": test_results.get("summary", {}).get("total", 0),
                        "passed": test_results.get("summary", {}).get("passed", 0),
                        "failed": test_results.get("summary", {}).get("failed", 0),
                        "errors": test_results.get("summary", {}).get("error", 0),
                        "skipped": test_results.get("summary", {}).get("skipped", 0),
                        "duration": test_results.get("duration", 0)
                    }
        except Exception as e:
            print(f"Could not load test results: {e}")
        
        # Load coverage results if available
        try:
            if os.path.exists(self.coverage_json):
                with open(self.coverage_json, 'r') as f:
                    coverage_data = json.load(f)
                    summary["coverage"] = {
                        "total_coverage": coverage_data.get("totals", {}).get("percent_covered", 0),
                        "lines_covered": coverage_data.get("totals", {}).get("covered_lines", 0),
                        "lines_missing": coverage_data.get("totals", {}).get("missing_lines", 0),
                        "total_lines": coverage_data.get("totals", {}).get("num_statements", 0)
                    }
        except Exception as e:
            print(f"Could not load coverage results: {e}")
        
        # Write summary to JSON file
        summary_json_file = f"result_miner_summary_2025-08-28.json"
        with open(summary_json_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Write human-readable summary
        with open(self.summary_file, 'w') as f:
            f.write("MINER.PY UNIT TEST EXECUTION SUMMARY\\n")
            f.write("=" * 50 + "\\n\\n")
            f.write(f"Execution Date: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\\n")
            f.write(f"Duration: {duration.total_seconds():.2f} seconds\\n")
            f.write(f"Test File: {self.test_file}\\n")
            f.write(f"Test Success: {'PASSED' if test_success else 'FAILED'}\\n\\n")
            
            if "test_results" in summary:
                results = summary["test_results"]
                f.write("TEST RESULTS:\\n")
                f.write("-" * 20 + "\\n")
                f.write(f"Total Tests: {results['total_tests']}\\n")
                f.write(f"Passed: {results['passed']}\\n")
                f.write(f"Failed: {results['failed']}\\n")
                f.write(f"Errors: {results['errors']}\\n")
                f.write(f"Skipped: {results['skipped']}\\n")
                f.write(f"Test Duration: {results['duration']:.2f} seconds\\n\\n")
            
            if "coverage" in summary:
                coverage = summary["coverage"]
                f.write("COVERAGE RESULTS:\\n")
                f.write("-" * 20 + "\\n")
                f.write(f"Total Coverage: {coverage['total_coverage']:.1f}%\\n")
                f.write(f"Lines Covered: {coverage['lines_covered']}\\n")
                f.write(f"Lines Missing: {coverage['lines_missing']}\\n")
                f.write(f"Total Lines: {coverage['total_lines']}\\n\\n")
            
            f.write("OUTPUT FILES:\\n")
            f.write("-" * 20 + "\\n")
            for file_type, filename in summary["test_execution_summary"]["output_files"].items():
                f.write(f"{file_type.replace('_', ' ').title()}: {filename}\\n")
        
        print(f"\\nTest execution summary written to: {self.summary_file}")
        print(f"Test execution summary JSON written to: {summary_json_file}")
        
        return summary
    
    def run(self):
        """Main execution method"""
        print("Miner.py Unit Test Runner")
        print("=" * 50)
        print(f"Started at: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        try:
            # Setup environment
            self.setup_environment()
            
            # Check dependencies
            self.check_dependencies()
            
            # Run tests
            test_success = self.run_tests()
            
            # Generate summary
            summary = self.generate_summary(test_success)
            
            print("\\n" + "=" * 50)
            if test_success:
                print("✅ ALL TESTS COMPLETED SUCCESSFULLY")
            else:
                print("❌ SOME TESTS FAILED")
            
            print(f"Duration: {(datetime.now() - self.start_time).total_seconds():.2f} seconds")
            print(f"Reports generated in: {self.test_dir}")
            print("=" * 50)
            
            return test_success
            
        except Exception as e:
            print(f"\\n❌ Test execution failed with error: {e}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    runner = MinerTestRunner()
    success = runner.run()
    sys.exit(0 if success else 1)