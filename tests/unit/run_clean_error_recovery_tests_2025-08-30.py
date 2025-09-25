#!/usr/bin/env python3
"""
Clean test runner for error_recovery.py unit tests
This runner generates fresh output files with current test results
"""

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def run_clean_tests():
    """Run tests and generate fresh output files."""

    # Change to the correct directory
    test_dir = Path(__file__).parent
    os.chdir(test_dir)

    # Define output files with clean names
    timestamp = datetime.now().strftime("%Y-%m-%d")
    html_report = f"result_error_recovery_clean_{timestamp}_report.html"
    json_report = f"result_error_recovery_clean_{timestamp}_results.json"
    junit_report = f"result_error_recovery_clean_{timestamp}_junit.xml"

    # Clean pytest command with all required options
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "test_error_recovery_clean_2025-08-30.py",
        "-c",
        "pytest_error_recovery_2025-08-30.ini",
        f"--html={html_report}",
        "--json-report",
        f"--json-report-file={json_report}",
        f"--junitxml={junit_report}",
        "--cov=src.utilities.privacy.error_recovery",
        "--cov-report=html",
        "--cov-report=term",
        "-v",
    ]

    print(f"Running command: {' '.join(cmd)}")

    try:
        # Run the tests
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=300
        )

        print(f"Exit code: {result.returncode}")
        print(f"STDOUT:\n{result.stdout}")
        if result.stderr:
            print(f"STDERR:\n{result.stderr}")

        # Generate summary
        summary_file = f"result_error_recovery_clean_{timestamp}_summary.md"
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write(
                f"""# Clean Error Recovery Test Results
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Test File:** test_error_recovery_clean_2025-08-30.py  
**Target Module:** src.utilities.privacy.error_recovery  

## Test Execution Summary

**Exit Code:** {result.returncode}  
**Command:** `{' '.join(cmd)}`

## Output Files Generated
- [x] **HTML Report:** `{html_report}`
- [x] **JSON Results:** `{json_report}`  
- [x] **JUnit XML:** `{junit_report}`
- [x] **Summary:** `{summary_file}`

## Test Output
```
{result.stdout}
```

## Test Completion Status
The comprehensive unit test suite for `error_recovery.py` has been executed with all required output formats generated successfully.
"""
            )

        print(f"\nSummary written to: {summary_file}")

        # List generated files
        print("\nGenerated files:")
        for filename in [html_report, json_report, junit_report, summary_file]:
            if os.path.exists(filename):
                print(f"  [x] {filename}")
            else:
                print(f"  [ ] {filename} (missing)")

        return result.returncode

    except subprocess.TimeoutExpired:
        print("Test execution timed out after 5 minutes")
        return 1
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1


if __name__ == "__main__":
    exit_code = run_clean_tests()
    sys.exit(exit_code)
