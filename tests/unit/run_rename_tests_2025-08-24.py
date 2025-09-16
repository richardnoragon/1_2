#!/usr/bin/env python3
"""
Test runner script for rename.py module tests.

This script provides comprehensive test execution with detailed reporting,
coverage analysis, and results summary for the rename.py module.

Test Results:
- HTML Coverage Report: htmlcov_rename_2025-08-24/index.html
- JSON Coverage Report: coverage_rename_2025-08-24.json
- JUnit XML Report: junit_rename_2025-08-24.xml
- Test Summary: result_rename_2025-08-24.json
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def run_tests():
    """Execute the test suite with comprehensive reporting."""
    print("=" * 80)
    print("RENAME.PY MODULE - COMPREHENSIVE TEST EXECUTION")
    print("=" * 80)
    print(f"Test execution started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target module: src.utilities.file_management.rename")
    print(f"Test file: test_rename_2025-08-24.py")
    print("-" * 80)
    
    # Change to the project root directory
    test_dir = Path(__file__).parent
    os.chdir(test_dir.parent.parent)
    
    # Define test command with all reporting options
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/unit/test_rename_2025-08-24.py",
        "-v",
        "--tb=short",
        f"--cov=src.utilities.file_management.rename",
        f"--cov-report=html:tests/unit/htmlcov_rename_2025-08-24",
        f"--cov-report=json:tests/unit/coverage_rename_2025-08-24.json",
        "--cov-report=term-missing",
        f"--junitxml=tests/unit/junit_rename_2025-08-24.xml",
        "-c", "tests/unit/pytest_rename_2025-08-24.ini"
    ]
    
    try:
        # Execute the tests
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        print("TEST EXECUTION OUTPUT:")
        print("-" * 40)
        print(result.stdout)
        
        if result.stderr:
            print("STDERR OUTPUT:")
            print("-" * 40)
            print(result.stderr)
        
        # Parse coverage results if available
        coverage_file = test_dir / "coverage_rename_2025-08-24.json"
        coverage_summary = {}
        
        if coverage_file.exists():
            try:
                with open(coverage_file, 'r') as f:
                    coverage_data = json.load(f)
                    totals = coverage_data.get('totals', {})
                    coverage_summary = {
                        'covered_lines': totals.get('covered_lines', 0),
                        'num_statements': totals.get('num_statements', 0),
                        'percent_covered': totals.get('percent_covered', 0.0),
                        'missing_lines': totals.get('missing_lines', 0)
                    }
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Warning: Could not parse coverage data: {e}")
        
        # Create comprehensive test summary
        summary = {
            "test_execution": {
                "timestamp": datetime.now().isoformat(),
                "exit_code": result.returncode,
                "test_file": "test_rename_2025-08-24.py",
                "target_module": "src.tools.file_management.rename",
                "framework": "pytest",
                "success": result.returncode == 0
            },
            "coverage": coverage_summary,
            "reports": {
                "html_coverage": "htmlcov_rename_2025-08-24/index.html",
                "json_coverage": "coverage_rename_2025-08-24.json",
                "junit_xml": "junit_rename_2025-08-24.xml",
                "summary": "result_rename_2025-08-24.json"
            },
            "command": " ".join(cmd)
        }
        
        # Save test summary
        summary_file = test_dir / "result_rename_2025-08-24.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print("=" * 80)
        print("TEST EXECUTION SUMMARY")
        print("=" * 80)
        print(f"Exit Code: {result.returncode}")
        print(f"Success: {'✓' if result.returncode == 0 else '✗'}")
        
        if coverage_summary:
            print(f"Coverage: {coverage_summary.get('percent_covered', 0):.1f}%")
            print(f"Statements: {coverage_summary.get('num_statements', 0)}")
            print(f"Covered Lines: {coverage_summary.get('covered_lines', 0)}")
            print(f"Missing Lines: {coverage_summary.get('missing_lines', 0)}")
        
        print("\nGenerated Reports:")
        print(f"- HTML Coverage: {test_dir}/htmlcov_rename_2025-08-24/index.html")
        print(f"- JSON Coverage: {test_dir}/coverage_rename_2025-08-24.json")
        print(f"- JUnit XML: {test_dir}/junit_rename_2025-08-24.xml")
        print(f"- Summary: {test_dir}/result_rename_2025-08-24.json")
        print("=" * 80)
        
        return result.returncode
        
    except subprocess.TimeoutExpired:
        print("ERROR: Test execution timed out after 5 minutes")
        return 1
    except Exception as e:
        print(f"ERROR: Test execution failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)