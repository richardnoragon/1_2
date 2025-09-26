#!/usr/bin/env python3
"""
Test execution script for launch_main.py unit tests

This script executes comprehensive unit tests for launch_main.py with
detailed reporting and coverage analysis.

Created: 2025-08-28
Target: src/rfu/launch_main.py
Framework: pytest
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


def setup_test_environment():
    """Set up the test environment and paths."""
    # Get the current directory
    current_dir = Path(__file__).parent
    
    # Add necessary paths to Python path
    workspace_root = current_dir.parent.parent
    sys.path.insert(0, str(workspace_root))
    sys.path.insert(0, str(workspace_root / "src"))
    
    # Ensure we're in the correct directory
    os.chdir(current_dir)
    
    print(f"Test environment setup complete")
    print(f"Working directory: {os.getcwd()}")
    print(f"Workspace root: {workspace_root}")
    
    return workspace_root

def install_requirements():
    """Install required testing packages."""
    requirements = [
        'pytest>=7.0.0',
        'pytest-html>=3.0.0',
        'pytest-json-report>=1.5.0',
        'pytest-cov>=4.0.0',
        'coverage>=6.0.0'
    ]
    
    print("Installing test requirements...")
    for requirement in requirements:
        try:
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', requirement
            ], check=True, capture_output=True, text=True)
            print(f"✓ Installed {requirement}")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install {requirement}: {e}")
            return False
    
    return True

def run_tests():
    """Execute the comprehensive test suite."""
    print("\n" + "="*60)
    print("LAUNCH_MAIN.PY COMPREHENSIVE UNIT TESTS")
    print("="*60)
    print(f"Execution started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Test execution command
    test_command = [
        sys.executable, '-m', 'pytest',
        'test_launch_main_2025-08-28.py',
        '-c', 'pytest_launch_main_2025-08-28.ini',
        '-v',
        '--tb=short',
        '--strict-markers',
        '--html=result_launch_main_2025-08-28.html',
        '--self-contained-html',
        '--json-report=result_launch_main_2025-08-28.json',
        '--json-report-file=result_launch_main_2025-08-28.json',
        '--cov=launch_main',
        '--cov-report=html:coverage_launch_main_2025-08-28',
        '--cov-report=json:coverage_launch_main_2025-08-28.json',
        '--cov-report=term-missing',
        '--cov-branch',
        '--cov-fail-under=80'
    ]
    
    start_time = time.time()
    
    try:
        # Execute tests
        result = subprocess.run(
            test_command,
            capture_output=True,
            text=True,
            timeout=300  # 5-minute timeout
        )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"\nTest execution completed in {execution_time:.2f} seconds")
        print(f"Exit code: {result.returncode}")
        
        # Display test output
        if result.stdout:
            print("\nSTDOUT:")
            print("-" * 40)
            print(result.stdout)
        
        if result.stderr:
            print("\nSTDERR:")
            print("-" * 40)
            print(result.stderr)
        
        return result.returncode == 0, result, execution_time
        
    except subprocess.TimeoutExpired:
        print("ERROR: Test execution timed out after 5 minutes")
        return False, None, 0
    except Exception as e:
        print(f"ERROR: Test execution failed: {e}")
        return False, None, 0

def generate_summary_report(success, result, execution_time):
    """Generate a comprehensive summary report."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    summary = {
        "test_execution_summary": {
            "target_file": "src/rfu/launch_main.py",
            "test_file": "test_launch_main_2025-08-28.py",
            "execution_timestamp": timestamp,
            "execution_time_seconds": round(execution_time, 2),
            "success": success,
            "exit_code": result.returncode if result else -1
        },
        "test_results": {
            "html_report": "result_launch_main_2025-08-28.html",
            "json_report": "result_launch_main_2025-08-28.json",
            "coverage_html": "coverage_launch_main_2025-08-28/index.html",
            "coverage_json": "coverage_launch_main_2025-08-28.json"
        },
        "test_categories": {
            "unit_tests": "TestLaunchMainModule",
            "integration_tests": "TestLaunchMainIntegration", 
            "edge_case_tests": "TestLaunchMainEdgeCases",
            "performance_tests": "TestLaunchMainPerformance"
        }
    }
    
    # Parse JSON report if available
    json_report_path = Path("result_launch_main_2025-08-28.json")
    if json_report_path.exists():
        try:
            with open(json_report_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            summary["pytest_summary"] = {
                "total_tests": json_data.get("summary", {}).get("total", 0),
                "passed": json_data.get("summary", {}).get("passed", 0),
                "failed": json_data.get("summary", {}).get("failed", 0),
                "skipped": json_data.get("summary", {}).get("skipped", 0),
                "errors": json_data.get("summary", {}).get("error", 0),
                "duration": json_data.get("duration", 0)
            }
        except Exception as e:
            summary["pytest_summary"] = {"error": f"Failed to parse JSON report: {e}"}
    
    # Parse coverage report if available
    coverage_json_path = Path("coverage_launch_main_2025-08-28.json")
    if coverage_json_path.exists():
        try:
            with open(coverage_json_path, 'r', encoding='utf-8') as f:
                coverage_data = json.load(f)
            
            summary["coverage_summary"] = {
                "total_coverage": coverage_data.get("totals", {}).get("percent_covered", 0),
                "lines_covered": coverage_data.get("totals", {}).get("covered_lines", 0),
                "lines_total": coverage_data.get("totals", {}).get("num_statements", 0),
                "branches_covered": coverage_data.get("totals", {}).get("covered_branches", 0),
                "branches_total": coverage_data.get("totals", {}).get("num_branches", 0)
            }
        except Exception as e:
            summary["coverage_summary"] = {"error": f"Failed to parse coverage report: {e}"}
    
    # Write summary report
    summary_file = f"result_launch_main_summary_2025-08-28.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    # Write text summary
    text_summary_file = f"result_launch_main_summary_2025-08-28.txt"
    with open(text_summary_file, 'w', encoding='utf-8') as f:
        f.write("LAUNCH_MAIN.PY UNIT TESTING COMPLETION SUMMARY\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Execution Date: {timestamp}\n")
        f.write(f"Target File: src/rfu/launch_main.py\n")
        f.write(f"Test File: test_launch_main_2025-08-28.py\n")
        f.write(f"Execution Time: {execution_time:.2f} seconds\n")
        f.write(f"Overall Success: {'✓ PASSED' if success else '✗ FAILED'}\n\n")
        
        if "pytest_summary" in summary:
            pytest_sum = summary["pytest_summary"]
            if "total_tests" in pytest_sum:
                f.write("TEST RESULTS:\n")
                f.write("-" * 20 + "\n")
                f.write(f"Total Tests: {pytest_sum['total_tests']}\n")
                f.write(f"Passed: {pytest_sum['passed']}\n")
                f.write(f"Failed: {pytest_sum['failed']}\n")
                f.write(f"Skipped: {pytest_sum['skipped']}\n")
                f.write(f"Errors: {pytest_sum['errors']}\n")
                f.write(f"Duration: {pytest_sum['duration']:.2f}s\n\n")
        
        if "coverage_summary" in summary:
            cov_sum = summary["coverage_summary"]
            if "total_coverage" in cov_sum:
                f.write("COVERAGE RESULTS:\n")
                f.write("-" * 20 + "\n")
                f.write(f"Total Coverage: {cov_sum['total_coverage']:.2f}%\n")
                f.write(f"Lines Covered: {cov_sum['lines_covered']}/{cov_sum['lines_total']}\n")
                f.write(f"Branches Covered: {cov_sum['branches_covered']}/{cov_sum['branches_total']}\n\n")
        
        f.write("GENERATED FILES:\n")
        f.write("-" * 20 + "\n")
        f.write("• result_launch_main_2025-08-28.html (Test Report)\n")
        f.write("• result_launch_main_2025-08-28.json (Test Data)\n")
        f.write("• coverage_launch_main_2025-08-28/ (Coverage HTML)\n")
        f.write("• coverage_launch_main_2025-08-28.json (Coverage Data)\n")
        f.write("• result_launch_main_summary_2025-08-28.json (Summary JSON)\n")
        f.write("• result_launch_main_summary_2025-08-28.txt (This Summary)\n")
    
    print(f"\nSummary reports generated:")
    print(f"• {summary_file}")
    print(f"• {text_summary_file}")
    
    return summary

def main():
    """Main execution function."""
    print("Launch Main Unit Testing - Comprehensive Test Suite")
    print("=" * 60)
    
    # Setup environment
    workspace_root = setup_test_environment()
    
    # Install requirements
    if not install_requirements():
        print("Failed to install requirements. Attempting to continue...")
    
    # Run tests
    success, result, execution_time = run_tests()
    
    # Generate summary
    summary = generate_summary_report(success, result, execution_time)
    
    # Final status
    print("\n" + "="*60)
    if success:
        print("✓ ALL TESTS COMPLETED SUCCESSFULLY")
        print("✓ Comprehensive test coverage achieved")
        print("✓ All test artifacts generated")
    else:
        print("✗ TESTS FAILED OR INCOMPLETE")
        print("✗ Check error logs and reports for details")
    
    print("="*60)
    print(f"Test execution completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())