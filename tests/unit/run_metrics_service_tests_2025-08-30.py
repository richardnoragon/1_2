"""
Test runner script for metrics_service tests
Generated on: 2025-08-30
"""

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def setup_environment():
    """Setup the testing environment."""
    # Get the project root directory
    current_dir = Path(__file__).parent
    project_root = current_dir.parent.parent

    # Add source paths to PYTHONPATH
    src_path = project_root / "src"
    metrics_path = (
        project_root
        / "src"
        / "utilities"
        / "network"
        / "network_connectivity_complex"
        / "core"
    )

    env_path = os.environ.get("PYTHONPATH", "")
    new_paths = [str(src_path), str(metrics_path)]

    if env_path:
        env_path = os.pathsep.join(new_paths + [env_path])
    else:
        env_path = os.pathsep.join(new_paths)

    os.environ["PYTHONPATH"] = env_path

    return project_root


def run_tests():
    """Run the metrics service tests."""
    print("=" * 60)
    print("METRICS SERVICE COMPREHENSIVE UNIT TESTS")
    print("=" * 60)
    print(f"Execution Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Test Framework: pytest")
    print(f"Python Version: {sys.version}")
    print("=" * 60)

    project_root = setup_environment()

    # Change to project root directory
    os.chdir(project_root)

    # Get the test file path
    test_file = (
        project_root / "tests" / "unit" / "test_metrics_service_2025-08-30.py"
    )

    if not test_file.exists():
        print(f"ERROR: Test file not found: {test_file}")
        return 1

    # Prepare pytest command
    pytest_cmd = [
        sys.executable,
        "-m",
        "pytest",
        str(test_file),
        "-v",
        "--tb=short",
        f"--html=tests/unit/result_metrics_service_2025-08-30.html",
        "--self-contained-html",
        "--json-report",
        f"--json-report-file=tests/unit/result_metrics_service_2025-08-30.json",
        "--cov=metrics_service",
        f"--cov-report=html:tests/unit/result_metrics_service_coverage_2025-08-30",
        "--cov-report=term-missing",
        f"--cov-report=json:tests/unit/result_metrics_service_coverage_2025-08-30.json",
    ]

    print("Running command:")
    print(" ".join(pytest_cmd))
    print("-" * 60)

    try:
        # Run the tests
        result = subprocess.run(pytest_cmd, capture_output=False, text=True)

        print("-" * 60)
        print(f"Test execution completed with exit code: {result.returncode}")

        # Generate execution summary
        generate_execution_summary(project_root, result.returncode)

        return result.returncode

    except Exception as e:
        print(f"ERROR: Failed to run tests: {e}")
        return 1


def generate_execution_summary(project_root, exit_code):
    """Generate a test execution summary."""
    summary = {
        "execution_info": {
            "timestamp": datetime.now().isoformat(),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M:%S"),
            "exit_code": exit_code,
            "status": "PASSED" if exit_code == 0 else "FAILED",
            "python_version": sys.version,
            "working_directory": str(project_root),
        },
        "test_files": {
            "test_file": "test_metrics_service_2025-08-30.py",
            "target_module": "metrics_service.py",
            "html_report": "result_metrics_service_2025-08-30.html",
            "json_report": "result_metrics_service_2025-08-30.json",
            "coverage_html": "result_metrics_service_coverage_2025-08-30/",
            "coverage_json": "result_metrics_service_coverage_2025-08-30.json",
        },
        "framework_info": {
            "framework": "pytest",
            "features": [
                "HTML reporting",
                "JSON reporting",
                "Code coverage",
                "Detailed assertions",
                "Mock testing",
                "Edge case testing",
            ],
        },
    }

    # Write summary to file
    summary_file = (
        project_root
        / "tests"
        / "unit"
        / "result_metrics_service_execution_summary_2025-08-30.json"
    )

    try:
        with open(summary_file, "w", encoding="utf-8") as f:
            import json

            json.dump(summary, f, indent=2, ensure_ascii=False)

        print(f"Execution summary saved to: {summary_file}")

    except Exception as e:
        print(f"WARNING: Could not save execution summary: {e}")


if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)
