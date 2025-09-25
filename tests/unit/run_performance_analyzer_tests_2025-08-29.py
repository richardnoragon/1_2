#!/usr/bin/env python3
"""
Test execution script for performance_analyzer tests.
Created: 2025-08-29

This script executes the performance_analyzer test suite with proper
configuration and generates comprehensive reports.
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def main():
    """Execute performance analyzer tests with comprehensive reporting."""
    print("=" * 80)
    print("PERFORMANCE ANALYZER UNIT TESTS")
    print("=" * 80)
    print(f"Execution Time: {datetime.now().isoformat()}")
    print(f"Target Module: performance_analyzer.py")
    print(f"Test Framework: pytest")
    print("=" * 80)

    # Set up test environment
    test_dir = Path(__file__).parent
    project_root = test_dir.parent.parent

    # Change to project root for correct imports
    os.chdir(project_root)

    # Add project root to Python path
    sys.path.insert(0, str(project_root))

    # Pytest command with configuration
    pytest_cmd = [
        sys.executable,
        "-m",
        "pytest",
        "-c",
        "tests/unit/pytest_performance_analyzer_2025-08-29.ini",
        "tests/unit/test_performance_analyzer_2025-08-29.py",
        "-v",
        "--tb=short",
    ]

    print("Executing pytest command:")
    print(" ".join(pytest_cmd))
    print("-" * 80)

    try:
        # Execute tests
        result = subprocess.run(
            pytest_cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
        )

        print("STDOUT:")
        print(result.stdout)

        if result.stderr:
            print("STDERR:")
            print(result.stderr)

        print("-" * 80)
        print(f"Test execution completed with exit code: {result.returncode}")

        # Generate execution summary
        generate_execution_summary(
            result.returncode, result.stdout, result.stderr
        )

        return result.returncode

    except subprocess.TimeoutExpired:
        print("ERROR: Test execution timed out after 5 minutes")
        generate_execution_summary(1, "", "Test execution timed out")
        return 1
    except Exception as e:
        print(f"ERROR: Test execution failed: {e}")
        generate_execution_summary(1, "", str(e))
        return 1


def generate_execution_summary(exit_code, stdout="", stderr=""):
    """Generate standardized execution summary."""
    timestamp = datetime.now().isoformat()

    summary = {
        "execution_metadata": {
            "timestamp": timestamp,
            "target_module": "performance_analyzer.py",
            "test_file": "test_performance_analyzer_2025-08-29.py",
            "framework": "pytest",
            "exit_code": exit_code,
            "status": "PASSED" if exit_code == 0 else "FAILED",
        },
        "output_files": {
            "html_report": "tests/unit/result_performance_analyzer_2025-08-29.html",
            "json_report": "tests/unit/result_performance_analyzer_2025-08-29.json",
            "xml_report": "tests/unit/result_performance_analyzer_2025-08-29.xml",
            "coverage_html": "tests/unit/result_performance_analyzer_coverage_2025-08-29",
            "coverage_json": "tests/unit/result_performance_analyzer_coverage_2025-08-29.json",
        },
        "execution_details": {
            "stdout_length": len(stdout),
            "stderr_length": len(stderr),
            "has_output": len(stdout) > 0,
            "has_errors": len(stderr) > 0,
        },
    }

    # Parse test results from stdout if available
    if stdout:
        summary["test_summary"] = parse_test_output(stdout)

    # Save execution summary
    summary_file = f"tests/unit/result_performance_analyzer_execution_summary_{timestamp[:10]}.json"
    try:
        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2)
        print(f"Execution summary saved to: {summary_file}")
    except Exception as e:
        print(f"Failed to save execution summary: {e}")

    # Print summary to console
    print("\n" + "=" * 50)
    print("EXECUTION SUMMARY")
    print("=" * 50)
    print(f"Status: {summary['execution_metadata']['status']}")
    print(f"Exit Code: {exit_code}")
    print(f"Timestamp: {timestamp}")

    if "test_summary" in summary:
        test_summary = summary["test_summary"]
        print(f"Tests Passed: {test_summary.get('passed', 'N/A')}")
        print(f"Tests Failed: {test_summary.get('failed', 'N/A')}")
        print(f"Total Tests: {test_summary.get('total', 'N/A')}")

    print("Expected Output Files:")
    for file_type, file_path in summary["output_files"].items():
        file_exists = os.path.exists(file_path)
        status = "[OK]" if file_exists else "[MISSING]"
        print(f"  {status} {file_type}: {file_path}")


def parse_test_output(stdout):
    """Parse pytest output to extract test summary."""
    lines = stdout.split("\n")
    summary = {"total": 0, "passed": 0, "failed": 0, "skipped": 0, "errors": 0}

    # Look for pytest summary line
    for line in lines:
        if "passed" in line and "failed" in line:
            # Try to parse summary line like "5 passed, 2 failed in 1.23s"
            try:
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == "passed" and i > 0:
                        summary["passed"] = int(parts[i - 1])
                    elif part == "failed" and i > 0:
                        summary["failed"] = int(parts[i - 1])
                    elif part == "skipped" and i > 0:
                        summary["skipped"] = int(parts[i - 1])
                    elif part == "error" and i > 0:
                        summary["errors"] = int(parts[i - 1])

                summary["total"] = (
                    summary["passed"]
                    + summary["failed"]
                    + summary["skipped"]
                    + summary["errors"]
                )
                break
            except (ValueError, IndexError):
                continue

    # Alternative parsing - count individual test results
    if summary["total"] == 0:
        for line in lines:
            if "::test_" in line:
                if "PASSED" in line:
                    summary["passed"] += 1
                elif "FAILED" in line:
                    summary["failed"] += 1
                elif "SKIPPED" in line:
                    summary["skipped"] += 1
                elif "ERROR" in line:
                    summary["errors"] += 1

        summary["total"] = (
            summary["passed"]
            + summary["failed"]
            + summary["skipped"]
            + summary["errors"]
        )

    return summary


def install_dependencies():
    """Install required test dependencies."""
    dependencies = [
        "pytest>=7.0.0",
        "pytest-html>=3.1.0",
        "pytest-json-report>=1.5.0",
        "pytest-cov>=4.0.0",
        "coverage>=7.0.0",
    ]

    print("Installing test dependencies...")
    for dep in dependencies:
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", dep],
                check=True,
                capture_output=True,
            )
            print(f"✓ Installed {dep}")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install {dep}: {e}")
            return False

    return True


if __name__ == "__main__":
    print("Performance Analyzer Test Suite")
    print("Setting up test environment...")

    # Optionally install dependencies
    if "--install-deps" in sys.argv:
        if not install_dependencies():
            print("Failed to install dependencies")
            sys.exit(1)

    # Run tests
    exit_code = main()

    print(f"\nTest execution completed with exit code: {exit_code}")
    if exit_code == 0:
        print("🎉 All tests passed!")
    else:
        print("❌ Some tests failed. Check the reports for details.")

    sys.exit(exit_code)
