#!/usr/bin/env python3
"""
Test runner script for log_manager unit tests
Generated on: 2025-08-28

This script runs the comprehensive unit tests for log_manager.py and generates
standardized test output with execution timestamp and detailed results.
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def run_log_manager_tests():
    """Run the log_manager unit tests with comprehensive reporting."""
    
    # Get current timestamp
    timestamp = datetime.now()
    print(f"=== LOG MANAGER UNIT TEST EXECUTION ===")
    print(f"Execution started at: {timestamp.isoformat()}")
    print(f"Target module: log_manager.py")
    print(f"Test file: test_log_manager_2025-08-28.py")
    print("=" * 50)
    
    # Set up paths
    test_dir = Path(__file__).parent
    project_root = test_dir.parent.parent
    
    # Change to project root for test execution
    original_dir = os.getcwd()
    os.chdir(project_root)
    
    try:
        # Install test dependencies
        print("Installing test dependencies...")
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", 
            str(test_dir / "test_requirements_log_manager_2025-08-28.txt")
        ], check=False, capture_output=True)
        
        # Run the tests with detailed reporting
        print("Running unit tests...")
        
        cmd = [
            sys.executable, "-m", "pytest",
            str(test_dir / "test_log_manager_2025-08-28.py"),
            "-v",
            "--tb=long",
            "--html=" + str(test_dir / "result_log_manager_2025-08-28.html"),
            "--self-contained-html",
            "--json-report",
            "--json-report-file=" + str(test_dir / "result_log_manager_2025-08-28.json"),
            "--cov=src.log_manager",
            "--cov-report=html:" + str(test_dir / "result_log_manager_coverage_2025-08-28"),
            "--cov-report=json:" + str(test_dir / "result_log_manager_coverage_2025-08-28.json"),
            "--cov-report=term-missing",
            "--durations=10"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Print test execution results
        print("\n=== TEST EXECUTION OUTPUT ===")
        print(result.stdout)
        
        if result.stderr:
            print("\n=== ERRORS/WARNINGS ===")
            print(result.stderr)
        
        # Generate summary report
        generate_summary_report(test_dir, result, timestamp)
        
        print(f"\n=== EXECUTION COMPLETED ===")
        print(f"Execution finished at: {datetime.now().isoformat()}")
        print(f"Exit code: {result.returncode}")
        
        return result.returncode
        
    except Exception as e:
        print(f"Error during test execution: {e}")
        return 1
        
    finally:
        os.chdir(original_dir)


def generate_summary_report(test_dir, result, timestamp):
    """Generate a comprehensive summary report."""
    
    summary_file = test_dir / f"result_log_manager_summary_2025-08-28.txt"
    
    try:
        # Load JSON report if available
        json_report_file = test_dir / "result_log_manager_2025-08-28.json"
        test_data = {}
        
        if json_report_file.exists():
            with open(json_report_file, 'r') as f:
                test_data = json.load(f)
        
        # Generate summary
        with open(summary_file, 'w') as f:
            f.write("LOG MANAGER UNIT TEST EXECUTION SUMMARY\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"Execution Timestamp: {timestamp.isoformat()}\n")
            f.write(f"Target Module: log_manager.py\n")
            f.write(f"Test File: test_log_manager_2025-08-28.py\n")
            f.write(f"Exit Code: {result.returncode}\n\n")
            
            if test_data:
                f.write("TEST RESULTS SUMMARY:\n")
                f.write("-" * 25 + "\n")
                f.write(f"Total Tests: {test_data.get('summary', {}).get('total', 'N/A')}\n")
                f.write(f"Passed: {test_data.get('summary', {}).get('passed', 'N/A')}\n")
                f.write(f"Failed: {test_data.get('summary', {}).get('failed', 'N/A')}\n")
                f.write(f"Skipped: {test_data.get('summary', {}).get('skipped', 'N/A')}\n")
                f.write(f"Duration: {test_data.get('duration', 'N/A')} seconds\n\n")
            
            f.write("GENERATED FILES:\n")
            f.write("-" * 15 + "\n")
            
            generated_files = [
                "result_log_manager_2025-08-28.html",
                "result_log_manager_2025-08-28.json", 
                "result_log_manager_coverage_2025-08-28.json",
                "result_log_manager_summary_2025-08-28.txt"
            ]
            
            for filename in generated_files:
                filepath = test_dir / filename
                if filepath.exists():
                    f.write(f"✓ {filename}\n")
                else:
                    f.write(f"✗ {filename} (not generated)\n")
            
            # Coverage directory
            coverage_dir = test_dir / "result_log_manager_coverage_2025-08-28"
            if coverage_dir.exists():
                f.write(f"✓ {coverage_dir.name}/ (coverage HTML report)\n")
            else:
                f.write(f"✗ {coverage_dir.name}/ (coverage HTML not generated)\n")
            
            f.write("\nSTDOUT:\n")
            f.write("-" * 7 + "\n")
            f.write(result.stdout)
            
            if result.stderr:
                f.write("\nSTDERR:\n")
                f.write("-" * 7 + "\n")
                f.write(result.stderr)
        
        print(f"Summary report generated: {summary_file}")
        
    except Exception as e:
        print(f"Error generating summary report: {e}")


if __name__ == "__main__":
    exit_code = run_log_manager_tests()
    sys.exit(exit_code)