#!/usr/bin/env python3
"""
Test runner for battery_health_widget comprehensive testing.

This script runs the complete test suite for battery_health_widget.py
and generates detailed reports with timestamps and coverage information.

Usage:
    python run_battery_health_widget_tests_2025-08-29.py

Output Files:
    - result_battery_health_widget_2025-08-29_report.html
    - result_battery_health_widget_2025-08-29_junit.xml
    - result_battery_health_widget_2025-08-29_summary.json
    - result_battery_health_widget_2025-08-29_coverage.html (if coverage available)
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# Configuration
TEST_DIR = Path(__file__).parent
TEST_FILE = "test_battery_health_widget_clean_2025-08-29.py"
CONFIG_FILE = "pytest_battery_health_widget_2025-08-29.ini"
OUTPUT_PREFIX = "result_battery_health_widget_2025-08-29"

def run_tests():
    """Run the complete test suite with comprehensive reporting."""
    print("=" * 80)
    print("BATTERY HEALTH WIDGET COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    print(f"Test execution started at: {datetime.now().isoformat()}")
    print(f"Test file: {TEST_FILE}")
    print(f"Target module: battery_health_widget.py")
    print(f"Framework: pytest")
    print("-" * 80)
    
    start_time = time.time()
    
    # Ensure we're in the correct directory
    os.chdir(TEST_DIR)
    
    # Build pytest command
    pytest_cmd = [
        sys.executable, "-m", "pytest",
        TEST_FILE,
        "-c", CONFIG_FILE,
        "-v",
        "--tb=short",
        f"--html={OUTPUT_PREFIX}_report.html",
        "--self-contained-html",
        f"--junitxml={OUTPUT_PREFIX}_junit.xml",
        "--disable-warnings"
    ]
    
    # Add coverage if pytest-cov is available
    try:
        import pytest_cov
        pytest_cmd.extend([
            "--cov=src.utilities.system.diagnostics_monitoring.gui.battery_health_widget",
            f"--cov-report=html:{OUTPUT_PREFIX}_coverage.html",
            f"--cov-report=json:{OUTPUT_PREFIX}_coverage.json",
            "--cov-report=term-missing"
        ])
        print("Coverage reporting enabled")
    except ImportError:
        print("Coverage reporting not available (pytest-cov not installed)")
    
    # Add JSON reporting if available
    try:
        import pytest_json_report
        pytest_cmd.extend([
            "--json-report",
            f"--json-report-file={OUTPUT_PREFIX}_detailed.json"
        ])
        print("JSON reporting enabled")
    except ImportError:
        print("JSON reporting not available (pytest-json-report not installed)")
    
    print(f"Running command: {' '.join(pytest_cmd)}")
    print("-" * 80)
    
    # Execute tests
    try:
        result = subprocess.run(
            pytest_cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5-minute timeout
        )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Print test output
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        # Generate summary report
        generate_summary_report(
            start_time=datetime.fromtimestamp(start_time),
            end_time=datetime.fromtimestamp(end_time),
            execution_time=execution_time,
            return_code=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr
        )
        
        print("-" * 80)
        print(f"Test execution completed at: {datetime.now().isoformat()}")
        print(f"Total execution time: {execution_time:.2f} seconds")
        print(f"Exit code: {result.returncode}")
        
        if result.returncode == 0:
            print("✅ All tests passed successfully!")
        else:
            print("❌ Some tests failed or encountered errors.")
        
        print("-" * 80)
        print("Generated output files:")
        list_output_files()
        
        return result.returncode
        
    except subprocess.TimeoutExpired:
        print("❌ Test execution timed out after 5 minutes")
        return 1
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 1


def generate_summary_report(start_time, end_time, execution_time, 
                          return_code, stdout, stderr):
    """Generate a comprehensive summary report."""
    summary = {
        "test_execution_summary": {
            "test_file": TEST_FILE,
            "target_module": "battery_health_widget.py",
            "framework": "pytest",
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "execution_time_seconds": round(execution_time, 2),
            "exit_code": return_code,
            "success": return_code == 0,
            "python_version": sys.version,
            "platform": sys.platform,
            "working_directory": str(TEST_DIR),
            "command_output": {
                "stdout": stdout,
                "stderr": stderr
            }
        },
        "test_configuration": {
            "config_file": CONFIG_FILE,
            "test_patterns": ["test_*.py"],
            "markers": ["unit", "integration", "performance"],
            "reports_generated": []
        },
        "output_files": {
            "html_report": f"{OUTPUT_PREFIX}_report.html",
            "junit_xml": f"{OUTPUT_PREFIX}_junit.xml",
            "summary_json": f"{OUTPUT_PREFIX}_summary.json"
        }
    }
    
    # Check for additional output files
    for file_pattern in [
        f"{OUTPUT_PREFIX}_coverage.html",
        f"{OUTPUT_PREFIX}_coverage.json", 
        f"{OUTPUT_PREFIX}_detailed.json"
    ]:
        if Path(file_pattern).exists():
            summary["test_configuration"]["reports_generated"].append(file_pattern)
    
    # Parse test results from stdout if available
    if stdout:
        summary["test_results"] = parse_test_results(stdout)
    
    # Write summary report
    summary_file = f"{OUTPUT_PREFIX}_summary.json"
    try:
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"Summary report written to: {summary_file}")
    except Exception as e:
        print(f"Warning: Could not write summary report: {e}")


def parse_test_results(stdout):
    """Parse test results from pytest output."""
    results = {
        "total_tests": 0,
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "errors": 0,
        "test_details": []
    }
    
    lines = stdout.split('\n')
    for line in lines:
        if '::' in line and ('PASSED' in line or 'FAILED' in line or 
                           'SKIPPED' in line or 'ERROR' in line):
            results["test_details"].append(line.strip())
            
            if 'PASSED' in line:
                results["passed"] += 1
            elif 'FAILED' in line:
                results["failed"] += 1
            elif 'SKIPPED' in line:
                results["skipped"] += 1
            elif 'ERROR' in line:
                results["errors"] += 1
    
    results["total_tests"] = (results["passed"] + results["failed"] + 
                            results["skipped"] + results["errors"])
    
    return results


def list_output_files():
    """List all generated output files."""
    output_files = []
    for pattern in [
        f"{OUTPUT_PREFIX}_*.html",
        f"{OUTPUT_PREFIX}_*.xml", 
        f"{OUTPUT_PREFIX}_*.json"
    ]:
        files = list(Path('.').glob(pattern.replace('*', '*')))
        output_files.extend(files)
    
    for file_path in sorted(output_files):
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"  📄 {file_path.name} ({size:,} bytes)")


def check_dependencies():
    """Check if required dependencies are available."""
    print("Checking dependencies...")
    
    required = ['pytest']
    optional = ['pytest-html', 'pytest-cov', 'pytest-json-report']
    
    for package in required:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} - available")
        except ImportError:
            print(f"❌ {package} - REQUIRED but not available")
            return False
    
    for package in optional:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} - available")
        except ImportError:
            print(f"⚠️  {package} - optional, not available")
    
    return True


def main():
    """Main entry point."""
    print("Battery Health Widget Test Suite Runner")
    print("=" * 50)
    
    # Check if test file exists
    if not Path(TEST_FILE).exists():
        print(f"❌ Test file not found: {TEST_FILE}")
        return 1
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Required dependencies not available")
        return 1
    
    print()
    
    # Run tests
    return run_tests()


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)