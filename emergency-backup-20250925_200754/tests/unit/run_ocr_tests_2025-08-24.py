#!/usr/bin/env python3
"""
OCR Unit Test Runner
Executes comprehensive unit tests for ocr.py module
Created: 2025-08-24
"""

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def main():
    """Main test execution function"""
    # Generate execution timestamp
    execution_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    print("=" * 80)
    print(f"OCR Unit Test Execution - Timestamp: {execution_timestamp}")
    print("=" * 80)

    # Set up paths
    project_root = Path(__file__).parent.parent.parent
    test_file = project_root / "tests" / "unit" / "test_ocr_2025-08-24.py"

    # Add source directory to Python path
    src_path = project_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

    # Set environment variables
    os.environ["PYTHONPATH"] = str(project_root)
    os.environ["TEST_MODE"] = "1"

    # Define test command with all options
    python_exe = sys.executable
    cmd = [
        python_exe,
        "-m",
        "pytest",
        str(test_file),
        "-v",
        "--tb=short",
        f"--html=tests/unit/result_ocr_2025-08-24_{execution_timestamp}.html",
        "--self-contained-html",
        f"--json-report-file=tests/unit/result_ocr_2025-08-24_{execution_timestamp}.json",
        "--cov=src.tools.pdf_tools.pdf_enhancements.ocr",
        f"--cov-report=html:tests/unit/htmlcov_ocr_2025-08-24_{execution_timestamp}",
        "--cov-report=term-missing",
        f"--cov-report=json:tests/unit/coverage_ocr_2025-08-24_{execution_timestamp}.json",
        "--maxfail=10",
        "--durations=10",
    ]

    print(f"Executing command: {' '.join(cmd)}")
    print("-" * 80)

    try:
        # Change to project root directory
        os.chdir(project_root)

        # Execute pytest
        result = subprocess.run(cmd, capture_output=False, text=True)

        print("-" * 80)
        print(f"Test execution completed with exit code: {result.returncode}")

        # Generate summary file
        summary_file = (
            project_root
            / "tests"
            / "unit"
            / f"result_ocr_execution_summary_2025-08-24_{execution_timestamp}.txt"
        )

        with open(summary_file, "w") as f:
            f.write(f"OCR Unit Test Execution Summary\n")
            f.write(f"Execution Timestamp: {execution_timestamp}\n")
            f.write(f"Exit Code: {result.returncode}\n")
            f.write(f"Test File: {test_file}\n")
            f.write(f"Command: {' '.join(cmd)}\n")
            f.write("\nReports Generated:\n")
            f.write(
                f"- HTML Report: result_ocr_2025-08-24_{execution_timestamp}.html\n"
            )
            f.write(
                f"- JSON Report: result_ocr_2025-08-24_{execution_timestamp}.json\n"
            )
            f.write(
                f"- Coverage HTML: htmlcov_ocr_2025-08-24_{execution_timestamp}/\n"
            )
            f.write(
                f"- Coverage JSON: coverage_ocr_2025-08-24_{execution_timestamp}.json\n"
            )

        print(f"Summary written to: {summary_file}")

        return result.returncode

    except Exception as e:
        print(f"Error executing tests: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
