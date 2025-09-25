"""
Test runner script for extract_metadata.py comprehensive unit tests
Created: 2025-08-24
Execution timestamp: {timestamp}
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def run_extract_metadata_tests():
    """Run comprehensive unit tests for extract_metadata.py"""

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{'='*70}")
    print(f"EXTRACT METADATA COMPREHENSIVE UNIT TEST EXECUTION")
    print(f"Execution Time: {timestamp}")
    print(f"{'='*70}")

    # Set up paths
    test_dir = Path(__file__).parent
    project_root = test_dir.parent.parent

    # Change to project directory
    os.chdir(str(project_root))

    # Test command with comprehensive reporting
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/unit/test_extract_metadata_2025-08-24.py",
        "-v",
        "--tb=short",
        f"--cov=src/tools/pdf_tools/pdf_content_extraction/extract_metadata",
        f"--cov-report=html:tests/unit/result_extract_metadata_2025-08-24_coverage_html",
        f"--cov-report=json:tests/unit/result_extract_metadata_2025-08-24_coverage.json",
        f"--cov-report=term-missing",
        f"--html=tests/unit/result_extract_metadata_2025-08-24_report.html",
        f"--self-contained-html",
        f"--json-report",
        f"--json-report-file=tests/unit/result_extract_metadata_2025-08-24_results.json",
        "--capture=no",
        "--durations=10",
    ]

    print(f"Running command: {' '.join(cmd)}")
    print(f"{'='*70}")

    try:
        # Run the tests
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=300
        )

        print("STDOUT:")
        print(result.stdout)

        if result.stderr:
            print("STDERR:")
            print(result.stderr)

        print(f"{'='*70}")
        print(
            f"Test execution completed with return code: {result.returncode}"
        )

        # Generate summary report
        generate_summary_report(result, timestamp)

        return result.returncode

    except subprocess.TimeoutExpired:
        print("ERROR: Test execution timed out after 5 minutes")
        return 1
    except Exception as e:
        print(f"ERROR: Failed to run tests: {e}")
        return 1


def generate_summary_report(result, timestamp):
    """Generate a summary report of test execution"""

    summary_file = "tests/unit/result_extract_metadata_2025-08-24_summary.txt"

    with open(summary_file, "w") as f:
        f.write(f"EXTRACT METADATA TEST EXECUTION SUMMARY\\n")
        f.write(f"{'='*50}\\n")
        f.write(f"Execution Timestamp: {timestamp}\\n")
        f.write(f"Return Code: {result.returncode}\\n")
        f.write(f"Success: {'YES' if result.returncode == 0 else 'NO'}\\n")
        f.write(f"\\n")

        f.write(f"STDOUT OUTPUT:\\n")
        f.write(f"{'-'*30}\\n")
        f.write(result.stdout)
        f.write(f"\\n")

        if result.stderr:
            f.write(f"STDERR OUTPUT:\\n")
            f.write(f"{'-'*30}\\n")
            f.write(result.stderr)
            f.write(f"\\n")

        # Try to parse JSON results if available
        try:
            json_file = (
                "tests/unit/result_extract_metadata_2025-08-24_results.json"
            )
            if os.path.exists(json_file):
                with open(json_file, "r") as jf:
                    test_data = json.load(jf)

                f.write(f"DETAILED TEST RESULTS:\\n")
                f.write(f"{'-'*30}\\n")
                f.write(
                    f"Total Tests: {test_data.get('summary', {}).get('total', 'N/A')}\\n"
                )
                f.write(
                    f"Passed: {test_data.get('summary', {}).get('passed', 'N/A')}\\n"
                )
                f.write(
                    f"Failed: {test_data.get('summary', {}).get('failed', 'N/A')}\\n"
                )
                f.write(
                    f"Skipped: {test_data.get('summary', {}).get('skipped', 'N/A')}\\n"
                )
                f.write(
                    f"Duration: {test_data.get('duration', 'N/A')} seconds\\n"
                )

        except Exception as e:
            f.write(f"Could not parse JSON results: {e}\\n")

    print(f"Summary report written to: {summary_file}")


if __name__ == "__main__":
    sys.exit(run_extract_metadata_tests())
