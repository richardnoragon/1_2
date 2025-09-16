"""
Test runner script for encrypt.py comprehensive unit tests
Generates standardized test output with timestamp and detailed results
Created: 2025-08-24
"""

import datetime
import json
import os
import subprocess
import sys
from pathlib import Path


def setup_test_environment():
    """Setup the test environment and install dependencies"""
    test_dir = Path(__file__).parent
    requirements_file = test_dir / "test_requirements_encrypt_2025-08-24.txt"
    
    print("Setting up test environment...")
    print(f"Installing dependencies from {requirements_file}")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ])
        print("✓ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install dependencies: {e}")
        return False
    
    return True

def run_tests():
    """Run the comprehensive test suite"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    test_dir = Path(__file__).parent
    test_file = test_dir / "test_encrypt_2025-08-24.py"
    
    # Output file paths with timestamp
    html_report = test_dir / f"result_encrypt_test_report_2025-08-24_{timestamp}.html"
    json_report = test_dir / f"result_encrypt_test_results_2025-08-24_{timestamp}.json"
    coverage_html = test_dir / f"result_encrypt_coverage_2025-08-24_{timestamp}"
    coverage_json = test_dir / f"result_encrypt_coverage_2025-08-24_{timestamp}.json"
    
    print(f"Starting comprehensive tests for encrypt.py at {timestamp}")
    print(f"Test file: {test_file}")
    print(f"Output directory: {test_dir}")
    print("-" * 60)
    
    # Pytest command with all options
    cmd = [
        sys.executable, "-m", "pytest",
        str(test_file),
        "-v",
        "--tb=short",
        "--capture=no",
        f"--html={html_report}",
        "--self-contained-html",
        f"--json-report={json_report}",
        "--cov=encrypt",
        f"--cov-report=html:{coverage_html}",
        f"--cov-report=json:{coverage_json}",
        "--cov-report=term-missing",
        "--cov-fail-under=70"
    ]
    
    try:
        result = subprocess.run(cmd, cwd=test_dir.parent.parent, capture_output=False)
        
        print("-" * 60)
        print(f"Test execution completed with exit code: {result.returncode}")
        
        # Generate summary report
        generate_summary_report(html_report, json_report, coverage_json, timestamp)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"✗ Error running tests: {e}")
        return False

def generate_summary_report(html_report, json_report, coverage_json, timestamp):
    """Generate a summary report of test results"""
    summary_file = Path(__file__).parent / f"result_encrypt_test_summary_2025-08-24_{timestamp}.txt"
    
    try:
        with open(summary_file, 'w') as f:
            f.write("COMPREHENSIVE UNIT TEST SUMMARY FOR ENCRYPT.PY\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Test Execution Timestamp: {timestamp}\n")
            f.write(f"Test Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Read JSON test results if available
            if json_report.exists():
                try:
                    with open(json_report, 'r') as json_file:
                        test_data = json.load(json_file)
                        
                    f.write("TEST RESULTS SUMMARY:\n")
                    f.write("-" * 25 + "\n")
                    f.write(f"Total Tests: {test_data.get('summary', {}).get('total', 'N/A')}\n")
                    f.write(f"Passed: {test_data.get('summary', {}).get('passed', 'N/A')}\n")
                    f.write(f"Failed: {test_data.get('summary', {}).get('failed', 'N/A')}\n")
                    f.write(f"Skipped: {test_data.get('summary', {}).get('skipped', 'N/A')}\n")
                    f.write(f"Duration: {test_data.get('duration', 'N/A')} seconds\n\n")
                    
                except Exception as e:
                    f.write(f"Error reading test results: {e}\n\n")
            
            # Read coverage results if available
            if coverage_json.exists():
                try:
                    with open(coverage_json, 'r') as cov_file:
                        coverage_data = json.load(cov_file)
                        
                    f.write("CODE COVERAGE SUMMARY:\n")
                    f.write("-" * 25 + "\n")
                    total_coverage = coverage_data.get('totals', {}).get('percent_covered', 'N/A')
                    f.write(f"Overall Coverage: {total_coverage}%\n")
                    
                    files = coverage_data.get('files', {})
                    for file_path, file_data in files.items():
                        if 'encrypt.py' in file_path:
                            f.write(f"encrypt.py Coverage: {file_data.get('summary', {}).get('percent_covered', 'N/A')}%\n")
                    
                    f.write("\n")
                    
                except Exception as e:
                    f.write(f"Error reading coverage results: {e}\n\n")
            
            f.write("OUTPUT FILES GENERATED:\n")
            f.write("-" * 25 + "\n")
            f.write(f"• HTML Test Report: {html_report.name}\n")
            f.write(f"• JSON Test Results: {json_report.name}\n")
            f.write(f"• HTML Coverage Report: {coverage_json.with_suffix('').name}/\n")
            f.write(f"• JSON Coverage Data: {coverage_json.name}\n")
            f.write(f"• Test Summary: {summary_file.name}\n\n")
            
            f.write("TEST CATEGORIES COVERED:\n")
            f.write("-" * 25 + "\n")
            f.write("• PDF Encryption Functions\n")
            f.write("• PDF Decryption Functions\n")
            f.write("• Stream Cipher Operations\n")
            f.write("• File Validation\n")
            f.write("• Error Handling\n")
            f.write("• UI Components\n")
            f.write("• Edge Cases and Boundary Conditions\n")
            f.write("• Exception Scenarios\n")
            f.write("• Mock and Patch Testing\n")
            
        print(f"✓ Summary report generated: {summary_file}")
        
    except Exception as e:
        print(f"✗ Error generating summary report: {e}")

def main():
    """Main execution function"""
    print("ENCRYPT.PY COMPREHENSIVE UNIT TEST SUITE")
    print("=" * 50)
    print("Setting up test environment and running comprehensive tests...")
    print()
    
    # Setup test environment
    if not setup_test_environment():
        print("✗ Test environment setup failed")
        sys.exit(1)
    
    # Run tests
    if run_tests():
        print("✓ All tests completed successfully")
        sys.exit(0)
    else:
        print("✗ Some tests failed or encountered errors")
        sys.exit(1)

if __name__ == "__main__":
    main()