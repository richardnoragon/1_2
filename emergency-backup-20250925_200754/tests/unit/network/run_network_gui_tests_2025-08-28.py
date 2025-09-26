"""
Network GUI Test Execution Script
Test execution timestamp: 2025-08-28
Target: src/utilities/network/gui.py

This script executes comprehensive unit tests for network\gui.py with detailed reporting.
"""

import os
import sys
import subprocess
import json
import time
from datetime import datetime
from pathlib import Path

# Test configuration
TEST_FILE = "test_network_gui_2025-08-28.py"
CONFIG_FILE = "pytest_network_gui_2025-08-28.ini"
RESULTS_DIR = Path(".")
TIMESTAMP = "2025-08-28"


def setup_environment():
    """Set up the testing environment."""
    print("Setting up testing environment...")

    # Ensure we're in the correct directory
    test_dir = Path(__file__).parent
    os.chdir(test_dir)

    # Add project root to Python path
    project_root = test_dir.parent.parent.parent
    sys.path.insert(0, str(project_root))

    print(f"Working directory: {os.getcwd()}")
    print(f"Project root: {project_root}")


def install_test_dependencies():
    """Install test dependencies if needed."""
    print("Checking test dependencies...")

    required_packages = [
        "pytest>=8.0.0",
        "pytest-cov>=4.0.0",
        "pytest-html>=3.0.0",
        "pytest-json-report>=1.5.0",
        "pytest-timeout>=2.1.0",
        "pytest-qt>=4.0.0",
        "PyQt5>=5.15.0",
    ]

    for package in required_packages:
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "show", package.split(">=")[0]],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                print(f"Installing {package}...")
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", package],
                    check=True,
                )
        except subprocess.CalledProcessError as e:
            print(f"Warning: Could not install {package}: {e}")


def run_tests():
    """Execute the test suite."""
    print(f"\n{'='*60}")
    print(f"EXECUTING NETWORK GUI TESTS - {TIMESTAMP}")
    print(f"{'='*60}")

    start_time = datetime.now()

    # Build pytest command
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "-c",
        CONFIG_FILE,
        TEST_FILE,
        "--verbose",
        "--tb=short",
        f"--html=result_network_gui_{TIMESTAMP}.html",
        "--self-contained-html",
        f"--junitxml=result_network_gui_{TIMESTAMP}.xml",
        "--json-report",
        f"--json-report-file=result_network_gui_{TIMESTAMP}.json",
        f"--cov=src.utilities.network.gui",
        f"--cov-report=html:coverage_network_gui_{TIMESTAMP}/",
        f"--cov-report=json:result_network_gui_coverage_{TIMESTAMP}.json",
        "--cov-report=term-missing",
        "--cov-branch",
        "--durations=10",
    ]

    print(f"Executing command: {' '.join(cmd)}")
    print(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        # Run tests
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=600
        )

        end_time = datetime.now()
        duration = end_time - start_time

        print(f"\nTest execution completed!")
        print(f"End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Duration: {duration}")
        print(f"Return code: {result.returncode}")

        # Print output
        if result.stdout:
            print(f"\n{'='*60}")
            print("STDOUT:")
            print(f"{'='*60}")
            print(result.stdout)

        if result.stderr:
            print(f"\n{'='*60}")
            print("STDERR:")
            print(f"{'='*60}")
            print(result.stderr)

        return result.returncode == 0, result.stdout, result.stderr, duration

    except subprocess.TimeoutExpired:
        print("Test execution timed out!")
        return False, "", "Test execution timed out", None
    except Exception as e:
        print(f"Error executing tests: {e}")
        return False, "", str(e), None


def generate_summary_report(success, stdout, stderr, duration):
    """Generate a comprehensive test summary report."""
    print(f"\n{'='*60}")
    print("GENERATING SUMMARY REPORT")
    print(f"{'='*60}")

    timestamp = datetime.now()

    # Parse test results from JSON if available
    test_stats = {}
    json_report_file = f"result_network_gui_{TIMESTAMP}.json"

    if os.path.exists(json_report_file):
        try:
            with open(json_report_file, "r") as f:
                json_data = json.load(f)
                test_stats = {
                    "total_tests": json_data.get("summary", {}).get(
                        "total", 0
                    ),
                    "passed": json_data.get("summary", {}).get("passed", 0),
                    "failed": json_data.get("summary", {}).get("failed", 0),
                    "skipped": json_data.get("summary", {}).get("skipped", 0),
                    "errors": json_data.get("summary", {}).get("error", 0),
                    "duration": json_data.get("duration", 0),
                    "outcome": json_data.get("exitcode", 1) == 0,
                }
        except Exception as e:
            print(f"Warning: Could not parse JSON report: {e}")

    # Generate summary
    summary = {
        "test_execution_info": {
            "timestamp": timestamp.isoformat(),
            "target_module": "src/utilities/network/gui.py",
            "test_file": TEST_FILE,
            "execution_successful": success,
            "duration_seconds": duration.total_seconds() if duration else 0,
        },
        "test_statistics": test_stats,
        "generated_files": {
            "html_report": f"result_network_gui_{TIMESTAMP}.html",
            "json_report": f"result_network_gui_{TIMESTAMP}.json",
            "xml_report": f"result_network_gui_{TIMESTAMP}.xml",
            "coverage_html": f"coverage_network_gui_{TIMESTAMP}/",
            "coverage_json": f"result_network_gui_coverage_{TIMESTAMP}.json",
        },
        "test_environment": {
            "python_version": sys.version,
            "working_directory": os.getcwd(),
            "platform": sys.platform,
        },
    }

    # Save summary as JSON
    summary_file = f"result_network_gui_summary_{TIMESTAMP}.json"
    with open(summary_file, "w") as f:
        json.dump(summary, f, indent=2, default=str)

    # Save summary as text
    summary_text_file = f"result_network_gui_summary_{TIMESTAMP}.txt"
    with open(summary_text_file, "w") as f:
        f.write(f"NETWORK GUI UNIT TESTS EXECUTION SUMMARY\n")
        f.write(f"{'='*50}\n\n")
        f.write(
            f"Execution Timestamp: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
        )
        f.write(f"Target Module: src/utilities/network/gui.py\n")
        f.write(f"Test File: {TEST_FILE}\n")
        f.write(f"Execution Successful: {success}\n")

        if duration:
            f.write(f"Duration: {duration}\n")

        f.write(f"\nTest Statistics:\n")
        f.write(f"  Total Tests: {test_stats.get('total_tests', 'N/A')}\n")
        f.write(f"  Passed: {test_stats.get('passed', 'N/A')}\n")
        f.write(f"  Failed: {test_stats.get('failed', 'N/A')}\n")
        f.write(f"  Skipped: {test_stats.get('skipped', 'N/A')}\n")
        f.write(f"  Errors: {test_stats.get('errors', 'N/A')}\n")

        f.write(f"\nGenerated Files:\n")
        for name, file in summary["generated_files"].items():
            f.write(f"  {name}: {file}\n")

        if stdout:
            f.write(f"\n\nStdout Output:\n{'-'*30}\n{stdout}\n")

        if stderr:
            f.write(f"\n\nStderr Output:\n{'-'*30}\n{stderr}\n")

    print(f"Summary reports generated:")
    print(f"  JSON: {summary_file}")
    print(f"  Text: {summary_text_file}")

    return summary


def validate_results():
    """Validate test results and check for required files."""
    print(f"\n{'='*60}")
    print("VALIDATING RESULTS")
    print(f"{'='*60}")

    expected_files = [
        f"result_network_gui_{TIMESTAMP}.html",
        f"result_network_gui_{TIMESTAMP}.json",
        f"result_network_gui_{TIMESTAMP}.xml",
        f"result_network_gui_coverage_{TIMESTAMP}.json",
    ]

    missing_files = []
    existing_files = []

    for file in expected_files:
        if os.path.exists(file):
            existing_files.append(file)
            size = os.path.getsize(file)
            print(f"✓ {file} ({size} bytes)")
        else:
            missing_files.append(file)
            print(f"✗ {file} (missing)")

    # Check coverage directory
    coverage_dir = f"coverage_network_gui_{TIMESTAMP}"
    if os.path.exists(coverage_dir):
        print(f"✓ {coverage_dir}/ (coverage HTML directory)")
    else:
        print(f"✗ {coverage_dir}/ (missing)")
        missing_files.append(coverage_dir)

    if missing_files:
        print(f"\nWarning: {len(missing_files)} expected files are missing")
        return False
    else:
        print(f"\nAll expected files generated successfully!")
        return True


def main():
    """Main execution function."""
    print("Network GUI Unit Tests Execution Script")
    print(f"Timestamp: {TIMESTAMP}")
    print(f"Target: src/utilities/network/gui.py")

    # Setup
    setup_environment()
    install_test_dependencies()

    # Execute tests
    success, stdout, stderr, duration = run_tests()

    # Generate reports
    summary = generate_summary_report(success, stdout, stderr, duration)

    # Validate results
    validation_success = validate_results()

    # Final status
    print(f"\n{'='*60}")
    print("FINAL STATUS")
    print(f"{'='*60}")

    overall_success = success and validation_success

    if overall_success:
        print("✓ Test execution completed successfully!")
        print("✓ All reports generated successfully!")
        return 0
    else:
        print("✗ Test execution completed with issues")
        if not success:
            print("  - Test execution failed")
        if not validation_success:
            print("  - Report validation failed")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
