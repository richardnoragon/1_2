"""
Simple test execution script for encrypt.py
Executes tests and generates reports
Created: 2025-08-24
"""

import os
import subprocess
import sys
from datetime import datetime


def main():
    """Execute the comprehensive test suite"""
    print("ENCRYPT.PY COMPREHENSIVE UNIT TESTS")
    print("=" * 40)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    current_dir = os.path.dirname(os.path.abspath(__file__))

    print(f"Execution timestamp: {timestamp}")
    print(f"Test directory: {current_dir}")
    print("-" * 40)

    # Define output files
    test_file = os.path.join(current_dir, "test_encrypt_2025-08-24.py")
    html_output = os.path.join(
        current_dir, f"result_encrypt_report_{timestamp}.html"
    )
    json_output = os.path.join(
        current_dir, f"result_encrypt_results_{timestamp}.json"
    )

    # Pytest command
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        test_file,
        "-v",
        "--tb=short",
        f"--html={html_output}",
        "--self-contained-html",
        f"--json-report={json_output}",
        "--capture=no",
    ]

    print("Executing tests...")
    try:
        result = subprocess.run(cmd, cwd=current_dir)
        print(
            f"\nTest execution completed with exit code: {result.returncode}"
        )
        print(f"HTML Report: {html_output}")
        print(f"JSON Results: {json_output}")
        return result.returncode
    except Exception as e:
        print(f"Error executing tests: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
