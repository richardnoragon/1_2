"""
Test runner script for convert_to_docx.py comprehensive testing
Generated on: 2025-08-24
Execution timestamp: {timestamp}

This script runs comprehensive unit tests for convert_to_docx.py with:
- Detailed HTML and JSON reporting
- Code coverage analysis
- Test execution timing
- Standardized output formatting
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def generate_execution_summary(test_results_file, coverage_file, output_file):
    """Generate a comprehensive test execution summary."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    summary = {
        "execution_timestamp": timestamp,
        "test_file": "test_convert_to_docx_2025-08-24.py",
        "target_module": "convert_to_docx.py",
        "test_framework": "pytest",
        "reports_generated": []
    }
    
    # Try to read test results
    if os.path.exists(test_results_file):
        try:
            with open(test_results_file, 'r', encoding='utf-8') as f:
                test_data = json.load(f)
                summary["test_results"] = {
                    "total_tests": test_data.get("summary", {}).get("total", 0),
                    "passed": test_data.get("summary", {}).get("passed", 0),
                    "failed": test_data.get("summary", {}).get("failed", 0),
                    "skipped": test_data.get("summary", {}).get("skipped", 0),
                    "duration": test_data.get("duration", 0)
                }
                summary["reports_generated"].append("JSON test report")
        except Exception as e:
            summary["test_results"] = {"error": f"Could not read test results: {e}"}
    
    # Try to read coverage results
    if os.path.exists(coverage_file):
        try:
            with open(coverage_file, 'r', encoding='utf-8') as f:
                coverage_data = json.load(f)
                summary["coverage_results"] = {
                    "total_coverage": coverage_data.get("totals", {}).get("percent_covered", 0),
                    "lines_covered": coverage_data.get("totals", {}).get("covered_lines", 0),
                    "lines_missing": coverage_data.get("totals", {}).get("missing_lines", 0),
                    "total_lines": coverage_data.get("totals", {}).get("num_statements", 0)
                }
                summary["reports_generated"].append("JSON coverage report")
        except Exception as e:
            summary["coverage_results"] = {"error": f"Could not read coverage results: {e}"}
    
    # Check for HTML reports
    html_report = "result_convert_to_docx_2025-08-24.html"
    if os.path.exists(html_report):
        summary["reports_generated"].append("HTML test report")
    
    coverage_html_dir = "result_convert_to_docx_coverage_2025-08-24"
    if os.path.exists(coverage_html_dir):
        summary["reports_generated"].append("HTML coverage report")
    
    junit_report = "result_convert_to_docx_2025-08-24_junit.xml"
    if os.path.exists(junit_report):
        summary["reports_generated"].append("JUnit XML report")
    
    # Write summary
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"CONVERT_TO_DOCX TEST EXECUTION SUMMARY\\n")
        f.write(f"{'='*50}\\n\\n")
        f.write(f"Execution Timestamp: {summary['execution_timestamp']}\\n")
        f.write(f"Test File: {summary['test_file']}\\n")
        f.write(f"Target Module: {summary['target_module']}\\n")
        f.write(f"Test Framework: {summary['test_framework']}\\n\\n")
        
        if "test_results" in summary and "error" not in summary["test_results"]:
            results = summary["test_results"]
            f.write(f"TEST RESULTS:\\n")
            f.write(f"Total Tests: {results['total_tests']}\\n")
            f.write(f"Passed: {results['passed']}\\n")
            f.write(f"Failed: {results['failed']}\\n")
            f.write(f"Skipped: {results['skipped']}\\n")
            f.write(f"Duration: {results['duration']:.2f} seconds\\n\\n")
        
        if "coverage_results" in summary and "error" not in summary["coverage_results"]:
            coverage = summary["coverage_results"]
            f.write(f"COVERAGE RESULTS:\\n")
            f.write(f"Total Coverage: {coverage['total_coverage']:.1f}%\\n")
            f.write(f"Lines Covered: {coverage['lines_covered']}\\n")
            f.write(f"Lines Missing: {coverage['lines_missing']}\\n")
            f.write(f"Total Lines: {coverage['total_lines']}\\n\\n")
        
        f.write(f"REPORTS GENERATED:\\n")
        for report in summary["reports_generated"]:
            f.write(f"- {report}\\n")
        
        if not summary["reports_generated"]:
            f.write("- No reports were successfully generated\\n")
    
    return summary


def main():
    """Main test execution function."""
    print("="*60)
    print("CONVERT_TO_DOCX COMPREHENSIVE TEST EXECUTION")
    print("="*60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Set up test environment
    test_dir = Path(__file__).parent
    os.chdir(test_dir)
    
    # Install required packages
    print("Installing required test packages...")
    required_packages = [
        "pytest",
        "pytest-html",
        "pytest-json-report",
        "pytest-cov",
        "pytest-timeout",
        "PyQt5",
        "pdf2docx"
    ]
    
    for package in required_packages:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", package], 
                         check=True, capture_output=True)
            print(f"✓ {package} installed/verified")
        except subprocess.CalledProcessError:
            print(f"✗ Failed to install {package}")
    
    print()
    
    # Run tests
    print("Running comprehensive tests...")
    test_command = [
        sys.executable, "-m", "pytest",
        "-c", "pytest_convert_to_docx_2025-08-24.ini",
        "test_convert_to_docx_2025-08-24.py",
        "-v"
    ]
    
    try:
        result = subprocess.run(test_command, capture_output=True, text=True)
        print("Test execution completed!")
        print()
        print("STDOUT:")
        print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        # Generate execution summary
        print("Generating execution summary...")
        summary = generate_execution_summary(
            "result_convert_to_docx_2025-08-24.json",
            "result_convert_to_docx_coverage_2025-08-24.json",
            "result_convert_to_docx_execution_summary_2025-08-24.txt"
        )
        
        print("✓ Execution summary generated")
        print()
        
        # Display summary
        if "test_results" in summary and "error" not in summary["test_results"]:
            results = summary["test_results"]
            print(f"Test Summary: {results['passed']} passed, {results['failed']} failed, {results['skipped']} skipped")
        
        if "coverage_results" in summary and "error" not in summary["coverage_results"]:
            coverage = summary["coverage_results"]
            print(f"Coverage: {coverage['total_coverage']:.1f}%")
        
        print(f"Reports: {len(summary['reports_generated'])} generated")
        
        return result.returncode
        
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    print("="*60)
    print(f"Test execution completed with exit code: {exit_code}")
    print("="*60)
    sys.exit(exit_code)