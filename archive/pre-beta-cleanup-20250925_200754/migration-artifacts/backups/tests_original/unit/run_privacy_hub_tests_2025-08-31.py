#!/usr/bin/env python3
"""
Test Execution Script for Privacy Hub Unit Tests

This script executes comprehensive unit tests for privacy_hub.py
and generates detailed reports with timestamps.

Generated: 2025-08-31
Target: src/utilities/privacy/privacy_tools/gui/privacy_hub.py
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


def setup_environment():
    """Setup test environment and dependencies."""
    print("Setting up test environment...")
    
    # Ensure we're in the correct directory
    test_dir = Path(__file__).parent
    os.chdir(test_dir)
    
    # Create results directory if it doesn't exist
    results_dir = test_dir / "results"
    results_dir.mkdir(exist_ok=True)
    
    # Install test requirements if needed
    try:
        import pytest
        import pytest_cov
        import pytest_html
        print("✓ Required packages already installed")
    except ImportError:
        print("Installing test requirements...")
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", 
            "requirements_test_privacy_hub_2025-08-31.txt"
        ], check=True)
    
    return results_dir


def run_tests(results_dir):
    """Execute the test suite with comprehensive reporting."""
    print("\n" + "="*60)
    print("EXECUTING PRIVACY HUB UNIT TESTS")
    print("="*60)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    # Test execution command
    cmd = [
        sys.executable, "-m", "pytest",
        "-c", "pytest_privacy_hub_2025-08-31.ini",
        "test_privacy_hub_2025-08-31.py",
        "-v",
        "--tb=short",
        f"--html={results_dir}/result_privacy_hub_2025-08-31_report.html",
        "--self-contained-html",
        f"--json-report-file={results_dir}/result_privacy_hub_2025-08-31_results.json",
        f"--junit-xml={results_dir}/result_privacy_hub_2025-08-31_junit.xml",
        "--cov=src.utilities.privacy.privacy_tools.gui.privacy_hub",
        f"--cov-report=html:{results_dir}/result_privacy_hub_2025-08-31_coverage",
        f"--cov-report=json:{results_dir}/result_privacy_hub_2025-08-31_coverage.json",
        "--cov-report=term-missing",
        "--durations=10"
    ]
    
    print(f"Test command: {' '.join(cmd)}")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    start_time = time.time()
    
    try:
        # Execute tests
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Print results
        print("\n" + "-"*40)
        print("TEST EXECUTION COMPLETE")
        print("-"*40)
        print(f"Exit code: {result.returncode}")
        print(f"Execution time: {execution_time:.2f} seconds")
        print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if result.stdout:
            print("\nSTDOUT:")
            print(result.stdout)
        
        if result.stderr:
            print("\nSTDERR:")
            print(result.stderr)
        
        # Generate execution summary
        generate_execution_summary(results_dir, result, execution_time, timestamp)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("ERROR: Test execution timed out after 300 seconds")
        return False
    except Exception as e:
        print(f"ERROR: Test execution failed: {e}")
        return False


def generate_execution_summary(results_dir, result, execution_time, timestamp):
    """Generate comprehensive execution summary."""
    summary = {
        "test_execution_summary": {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "execution_id": timestamp,
            "target_file": "src/utilities/privacy/privacy_tools/gui/privacy_hub.py",
            "test_file": "test_privacy_hub_2025-08-31.py",
            "execution_time_seconds": round(execution_time, 2),
            "exit_code": result.returncode,
            "success": result.returncode == 0,
            "test_framework": "pytest",
            "python_version": sys.version,
            "platform": sys.platform,
            "working_directory": str(Path.cwd()),
            "output_files": {
                "html_report": f"result_privacy_hub_2025-08-31_report.html",
                "json_results": f"result_privacy_hub_2025-08-31_results.json",
                "junit_xml": f"result_privacy_hub_2025-08-31_junit.xml",
                "coverage_html": f"result_privacy_hub_2025-08-31_coverage/index.html",
                "coverage_json": f"result_privacy_hub_2025-08-31_coverage.json",
                "execution_summary": f"result_privacy_hub_2025-08-31_summary.json"
            },
            "test_configuration": {
                "config_file": "pytest_privacy_hub_2025-08-31.ini",
                "requirements_file": "requirements_test_privacy_hub_2025-08-31.txt",
                "coverage_threshold": 80,
                "timeout_seconds": 300
            },
            "stdout_lines": len(result.stdout.splitlines()) if result.stdout else 0,
            "stderr_lines": len(result.stderr.splitlines()) if result.stderr else 0
        }
    }
    
    # Save summary
    summary_file = results_dir / "result_privacy_hub_2025-08-31_summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Execution summary saved to: {summary_file}")


def parse_test_results(results_dir):
    """Parse and display test results summary."""
    json_results_file = results_dir / "result_privacy_hub_2025-08-31_results.json"
    
    if not json_results_file.exists():
        print("Warning: JSON results file not found")
        return
    
    try:
        with open(json_results_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        summary = data.get('summary', {})
        
        print("\n" + "="*60)
        print("TEST RESULTS SUMMARY")
        print("="*60)
        print(f"Total tests: {summary.get('total', 'N/A')}")
        print(f"Passed: {summary.get('passed', 'N/A')}")
        print(f"Failed: {summary.get('failed', 'N/A')}")
        print(f"Skipped: {summary.get('skipped', 'N/A')}")
        print(f"Errors: {summary.get('error', 'N/A')}")
        
        # Parse test details
        if 'tests' in data:
            print(f"\nTest Details:")
            for test in data['tests']:
                status = "✓" if test['outcome'] == 'passed' else "✗"
                duration = test.get('duration', 0)
                print(f"  {status} {test['nodeid']} ({duration:.3f}s)")
        
    except Exception as e:
        print(f"Error parsing test results: {e}")


def main():
    """Main execution function."""
    print("Privacy Hub Unit Test Executor")
    print("Generated: 2025-08-31")
    print("Target: src/utilities/privacy/privacy_tools/gui/privacy_hub.py")
    
    try:
        # Setup environment
        results_dir = setup_environment()
        
        # Run tests
        success = run_tests(results_dir)
        
        # Parse and display results
        parse_test_results(results_dir)
        
        # Final status
        print("\n" + "="*60)
        if success:
            print("✓ ALL TESTS COMPLETED SUCCESSFULLY")
        else:
            print("✗ SOME TESTS FAILED OR ENCOUNTERED ERRORS")
        print("="*60)
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n\nTest execution interrupted by user")
        return 2
    except Exception as e:
        print(f"\nFatal error: {e}")
        return 3


if __name__ == "__main__":
    sys.exit(main())