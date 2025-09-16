#!/usr/bin/env python3
"""
Test Runner for Error Recovery Unit Tests

Script: test_runner_error_recovery_2025-08-30.py
Target: error_recovery.py comprehensive unit tests
Generated: 2025-08-30
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


class ErrorRecoveryTestRunner:
    """Test runner for error recovery unit tests with comprehensive reporting."""
    
    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.project_root = self.test_dir.parent.parent
        self.timestamp = datetime.now()
        self.test_file = self.test_dir / "test_error_recovery_2025-08-30.py"
        
    def setup_environment(self):
        """Setup the testing environment."""
        print(f"=== Error Recovery Test Setup - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')} ===")
        print(f"Test Directory: {self.test_dir}")
        print(f"Project Root: {self.project_root}")
        print(f"Test File: {self.test_file}")
        
        # Add project root to Python path
        sys.path.insert(0, str(self.project_root))
        
        # Change to project root directory
        os.chdir(self.project_root)
        
        print("Environment setup complete.\n")
    
    def install_dependencies(self):
        """Install required test dependencies."""
        print("=== Installing Test Dependencies ===")
        requirements_file = self.test_dir / "test_requirements_error_recovery_2025-08-30.txt"
        
        if requirements_file.exists():
            try:
                subprocess.run([
                    sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
                ], check=True, capture_output=True, text=True)
                print("Dependencies installed successfully.")
            except subprocess.CalledProcessError as e:
                print(f"Warning: Failed to install some dependencies: {e}")
                print("Continuing with existing packages...")
        else:
            print("No requirements file found, using existing packages.")
        
        print()
    
    def run_tests(self):
        """Execute the unit tests with comprehensive reporting."""
        print("=== Running Error Recovery Unit Tests ===")
        
        start_time = time.time()
        
        # Construct pytest command
        cmd = [
            sys.executable, "-m", "pytest",
            str(self.test_file),
            "-v",
            "--tb=short",
            f"--html={self.test_dir}/result_error_recovery_2025-08-30.html",
            "--self-contained-html",
            "--json-report",
            f"--json-report-file={self.test_dir}/result_error_recovery_2025-08-30.json",
            f"--cov=src.utilities.privacy.error_recovery",
            f"--cov-report=html:{self.test_dir}/result_error_recovery_coverage_2025-08-30",
            f"--cov-report=json:{self.test_dir}/result_error_recovery_coverage_2025-08-30.json",
            "--cov-report=term-missing",
            "--cov-branch",
            "--durations=0"
        ]
        
        print(f"Executing: {' '.join(cmd)}")
        print()
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Display results
            print("STDOUT:")
            print(result.stdout)
            print("\nSTDERR:")
            print(result.stderr)
            
            # Generate summary
            self.generate_test_summary(result, execution_time)
            
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            print("ERROR: Tests timed out after 5 minutes")
            return False
        except Exception as e:
            print(f"ERROR: Failed to run tests: {e}")
            return False
    
    def generate_test_summary(self, result, execution_time):
        """Generate a comprehensive test summary."""
        summary_file = self.test_dir / f"result_error_recovery_summary_2025-08-30.txt"
        
        # Parse JSON report if available
        json_report_file = self.test_dir / "result_error_recovery_2025-08-30.json"
        test_stats = self.parse_json_report(json_report_file)
        
        summary_content = f"""
===============================================================================
ERROR RECOVERY UNIT TESTS - EXECUTION SUMMARY
===============================================================================

Test Execution Details:
- Timestamp: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
- Target Module: src.utilities.privacy.error_recovery
- Test File: test_error_recovery_2025-08-30.py
- Execution Time: {execution_time:.2f} seconds
- Exit Code: {result.returncode}

Test Results:
{test_stats}

Output Files Generated:
- HTML Report: result_error_recovery_2025-08-30.html
- JSON Report: result_error_recovery_2025-08-30.json
- Coverage HTML: result_error_recovery_coverage_2025-08-30/
- Coverage JSON: result_error_recovery_coverage_2025-08-30.json
- Summary: result_error_recovery_summary_2025-08-30.txt

Test Status: {'PASSED' if result.returncode == 0 else 'FAILED'}

===============================================================================
DETAILED OUTPUT
===============================================================================

STDOUT:
{result.stdout}

STDERR:
{result.stderr}

===============================================================================
"""
        
        # Write summary to file
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary_content)
        
        print(f"\n=== Test Summary Generated: {summary_file} ===")
        print(summary_content)
    
    def parse_json_report(self, json_file):
        """Parse JSON test report and extract key statistics."""
        if not json_file.exists():
            return "JSON report not available"
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            summary = data.get('summary', {})
            tests = data.get('tests', [])
            
            stats = f"""
- Total Tests: {summary.get('total', 0)}
- Passed: {summary.get('passed', 0)}
- Failed: {summary.get('failed', 0)}
- Skipped: {summary.get('skipped', 0)}
- Errors: {summary.get('error', 0)}
- Duration: {summary.get('duration', 0):.2f} seconds"""
            
            if summary.get('failed', 0) > 0:
                failed_tests = [test['nodeid'] for test in tests if test['outcome'] == 'failed']
                stats += f"\n\nFailed Tests:\n" + "\n".join(f"  - {test}" for test in failed_tests)
            
            return stats
            
        except Exception as e:
            return f"Error parsing JSON report: {e}"
    
    def validate_test_coverage(self):
        """Validate that test coverage meets requirements."""
        coverage_json = self.test_dir / "result_error_recovery_coverage_2025-08-30.json"
        
        if not coverage_json.exists():
            print("Warning: Coverage report not found")
            return False
        
        try:
            with open(coverage_json, 'r', encoding='utf-8') as f:
                coverage_data = json.load(f)
            
            total_coverage = coverage_data.get('totals', {}).get('percent_covered', 0)
            print(f"Total Coverage: {total_coverage:.1f}%")
            
            if total_coverage >= 80:
                print("✓ Coverage requirement met (≥80%)")
                return True
            else:
                print("✗ Coverage requirement not met (<80%)")
                return False
                
        except Exception as e:
            print(f"Error reading coverage report: {e}")
            return False
    
    def run_complete_test_suite(self):
        """Run the complete test suite with setup and reporting."""
        print("="*80)
        print("ERROR RECOVERY COMPREHENSIVE UNIT TEST SUITE")
        print("="*80)
        
        self.setup_environment()
        self.install_dependencies()
        
        success = self.run_tests()
        coverage_ok = self.validate_test_coverage()
        
        print("\n" + "="*80)
        print("FINAL RESULTS")
        print("="*80)
        print(f"Tests: {'PASSED' if success else 'FAILED'}")
        print(f"Coverage: {'ACCEPTABLE' if coverage_ok else 'BELOW THRESHOLD'}")
        print(f"Overall: {'SUCCESS' if success and coverage_ok else 'NEEDS ATTENTION'}")
        print("="*80)
        
        return success and coverage_ok


if __name__ == "__main__":
    runner = ErrorRecoveryTestRunner()
    success = runner.run_complete_test_suite()
    sys.exit(0 if success else 1)