#!/usr/bin/env python3
"""
Test runner script for browser_detector.py comprehensive unit tests

This script executes the enhanced test suite for browser_detector.py with
comprehensive reporting and coverage analysis.

Created: 2025-08-30
Target: browser_detector.py
"""

import datetime
import json
import os
import subprocess
import sys
from pathlib import Path


def setup_environment():
    """Set up the testing environment."""
    # Add source directory to Python path
    project_root = Path(__file__).parent.parent.parent
    src_path = project_root / "src"

    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

    # Set environment variables
    os.environ["PYTHONPATH"] = str(src_path)
    os.environ["PYTEST_CURRENT_TEST"] = "browser_detector_enhanced_2025-08-30"

    return project_root


def create_results_directory():
    """Create the results directory if it doesn't exist."""
    results_dir = Path("C:/Users/richardi/1_2/tests/unit/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    return results_dir


def run_tests():
    """Execute the test suite with comprehensive reporting."""
    print("=" * 80)
    print("BROWSER DETECTOR ENHANCED UNIT TEST EXECUTION")
    print("=" * 80)
    print(f"Execution Time: {datetime.datetime.now()}")
    print(f"Target Module: browser_detector.py")
    print(f"Test File: test_browser_detector_enhanced_2025-08-30.py")
    print("=" * 80)

    # Setup environment
    project_root = setup_environment()
    results_dir = create_results_directory()

    # Define test file and config
    test_file = (
        Path(__file__).parent / "test_browser_detector_enhanced_2025-08-30.py"
    )
    config_file = (
        Path(__file__).parent
        / "pytest_browser_detector_enhanced_2025-08-30.ini"
    )

    # Build pytest command
    pytest_cmd = [
        sys.executable,
        "-m",
        "pytest",
        str(test_file),
        f"-c",
        str(config_file),
        "-v",
        "--tb=short",
        "--strict-markers",
        f"--html={results_dir}/result_browser_detector_enhanced_2025-08-30.html",
        "--self-contained-html",
        "--json-report",
        f"--json-report-file={results_dir}/result_browser_detector_enhanced_2025-08-30.json",
        "--cov=utilities.privacy.privacy_tools.core.browser_detector",
        f"--cov-report=html:{results_dir}/coverage_browser_detector_enhanced_2025-08-30",
        f"--cov-report=json:{results_dir}/coverage_browser_detector_enhanced_2025-08-30.json",
        "--cov-report=term-missing",
        "--cov-fail-under=70",
        f"--junit-xml={results_dir}/result_browser_detector_enhanced_2025-08-30_junit.xml",
    ]

    print("Executing pytest command...")
    print(" ".join(pytest_cmd))
    print("-" * 80)

    try:
        # Run the tests
        result = subprocess.run(
            pytest_cmd,
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=600,  # 10 minute timeout
        )

        print("STDOUT:")
        print(result.stdout)

        if result.stderr:
            print("STDERR:")
            print(result.stderr)

        print("-" * 80)
        print(f"Return code: {result.returncode}")

        # Generate summary report
        generate_summary_report(results_dir, result)

        return result.returncode

    except subprocess.TimeoutExpired:
        print("ERROR: Test execution timed out after 10 minutes")
        return 1
    except Exception as e:
        print(f"ERROR: Failed to execute tests: {e}")
        return 1


def generate_summary_report(results_dir, test_result):
    """Generate a summary report of the test execution."""
    summary_file = (
        results_dir / "result_browser_detector_enhanced_2025-08-30_summary.md"
    )

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    summary_content = f"""# Browser Detector Enhanced Unit Test Summary

## Test Execution Details
- **Execution Date**: {timestamp}
- **Test Target**: browser_detector.py
- **Test File**: test_browser_detector_enhanced_2025-08-30.py
- **Return Code**: {test_result.returncode}
- **Status**: {'PASSED' if test_result.returncode == 0 else 'FAILED'}

## Test Output
### STDOUT
```
{test_result.stdout}
```

### STDERR
```
{test_result.stderr}
```

## Generated Reports
- **HTML Report**: result_browser_detector_enhanced_2025-08-30.html
- **JSON Report**: result_browser_detector_enhanced_2025-08-30.json
- **JUnit XML**: result_browser_detector_enhanced_2025-08-30_junit.xml
- **Coverage HTML**: coverage_browser_detector_enhanced_2025-08-30/
- **Coverage JSON**: coverage_browser_detector_enhanced_2025-08-30.json

## Test Configuration
- Minimum Coverage Threshold: 70%
- Test Discovery Pattern: test_*
- Reporting Format: HTML, JSON, JUnit XML
- Coverage Analysis: Enabled with detailed reporting

## Notes
This comprehensive test suite validates all functionality of the BrowserDetector class
including platform-specific browser detection, process management, and data access validation.
"""

    try:
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write(summary_content)
        print(f"Summary report generated: {summary_file}")
    except Exception as e:
        print(f"Warning: Could not generate summary report: {e}")


if __name__ == "__main__":
    exit_code = run_tests()

    print("\n" + "=" * 80)
    print(f"TEST EXECUTION COMPLETED - Exit Code: {exit_code}")
    print("=" * 80)

    if exit_code == 0:
        print("✅ All tests passed successfully!")
    else:
        print("❌ Some tests failed or encountered errors.")

    print(f"\nResults available in: C:/Users/richardi/1_2/tests/unit/results/")
    print(
        "Check the HTML report for detailed test results and coverage information."
    )

    sys.exit(exit_code)
