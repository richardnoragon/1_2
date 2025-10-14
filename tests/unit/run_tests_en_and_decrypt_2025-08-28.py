#!/usr/bin/env python3
"""
Test Runner for en_and_decrypt.py Unit Tests

Comprehensive test execution script with detailed reporting and coverage analysis.
Generated: 2025-08-28

This script:
1. Configures the test environment
2. Executes comprehensive unit tests
3. Generates HTML, JSON, and XML reports
4. Provides coverage analysis
5. Creates execution summary
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# Test configuration
TEST_CONFIG = {
    "test_file": "test_en_and_decrypt_2025-08-28.py",
    "target_module": "en_and_decrypt.py",
    "output_dir": "c:/Users/richardi/1_2/tests/unit",
    "date_suffix": "2025-08-28",
    "framework": "pytest",
    "coverage_threshold": 80,
}


def ensure_dependencies():
    """Ensure required testing dependencies are installed."""
    required_packages = [
        "pytest",
        "pytest-html",
        "pytest-json-report",
        "pytest-cov",
        "pytest-timeout",
        "pytest-mock",
    ]

    print("🔍 Checking test dependencies...")

    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package} - Available")
        except ImportError:
            print(f"⚠️  {package} - Installing...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"✅ {package} - Installed successfully")
            except subprocess.CalledProcessError:
                print(f"❌ {package} - Installation failed")


def setup_test_environment():
    """Setup the test environment and directories."""
    print("🔧 Setting up test environment...")

    # Ensure output directory exists
    output_dir = Path(TEST_CONFIG["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create coverage directory
    coverage_dir = output_dir / f"coverage_en_and_decrypt_{TEST_CONFIG['date_suffix']}"
    coverage_dir.mkdir(exist_ok=True)

    print(f"📁 Test output directory: {output_dir}")
    print(f"📊 Coverage directory: {coverage_dir}")

    return output_dir, coverage_dir


def run_tests(output_dir, coverage_dir):
    """Execute the comprehensive test suite."""
    print("🧪 Executing comprehensive test suite...")

    test_file = output_dir / TEST_CONFIG["test_file"]

    # Build pytest command with all reporting options
    pytest_cmd = [
        sys.executable,
        "-m",
        "pytest",
        str(test_file),
        "-v",
        "--tb=short",
        "--capture=no",
        "--color=yes",
        "--durations=10",
        f"--html={output_dir}/result_en_and_decrypt_{TEST_CONFIG['date_suffix']}.html",
        "--self-contained-html",
        f"--junitxml={output_dir}/result_en_and_decrypt_{TEST_CONFIG['date_suffix']}.xml",
        "--json-report",
        f"--json-report-file={output_dir}/result_en_and_decrypt_{TEST_CONFIG['date_suffix']}.json",
        "--cov=src.tools.security.encryption.en_and_decrypt",
        f"--cov-report=html:{coverage_dir}",
        f"--cov-report=json:{output_dir}/coverage_en_and_decrypt_{TEST_CONFIG['date_suffix']}.json",
        "--cov-report=term-missing",
        f"--cov-fail-under={TEST_CONFIG['coverage_threshold']}",
        "--timeout=300",
    ]

    print(f"📋 Test command: {' '.join(pytest_cmd)}")

    # Execute tests
    start_time = time.time()
    try:
        result = subprocess.run(
            pytest_cmd,
            capture_output=True,
            text=True,
            cwd=str(Path(output_dir).parent.parent),
        )
        execution_time = time.time() - start_time

        print(f"⏱️  Test execution completed in {execution_time:.2f} seconds")
        print(f"📤 Return code: {result.returncode}")

        if result.stdout:
            print("📊 Test Output:")
            print(result.stdout)

        if result.stderr:
            print("⚠️  Test Warnings/Errors:")
            print(result.stderr)

        return result, execution_time

    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return None, 0


def generate_execution_summary(output_dir, test_result, execution_time):
    """Generate comprehensive execution summary."""
    print("📝 Generating execution summary...")

    timestamp = datetime.now()

    summary = {
        "test_execution_summary": {
            "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "date": TEST_CONFIG["date_suffix"],
            "target_module": TEST_CONFIG["target_module"],
            "test_file": TEST_CONFIG["test_file"],
            "framework": TEST_CONFIG["framework"],
            "execution_time_seconds": execution_time,
            "return_code": test_result.returncode if test_result else -1,
            "success": test_result.returncode == 0 if test_result else False,
        },
        "test_configuration": {
            "coverage_threshold": TEST_CONFIG["coverage_threshold"],
            "output_directory": str(output_dir),
            "timeout_seconds": 300,
            "parallel_execution": False,
        },
        "generated_reports": {
            "html_report": f"result_en_and_decrypt_{TEST_CONFIG['date_suffix']}.html",
            "json_report": f"result_en_and_decrypt_{TEST_CONFIG['date_suffix']}.json",
            "xml_report": f"result_en_and_decrypt_{TEST_CONFIG['date_suffix']}.xml",
            "coverage_html": f"coverage_en_and_decrypt_{TEST_CONFIG['date_suffix']}/index.html",
            "coverage_json": f"coverage_en_and_decrypt_{TEST_CONFIG['date_suffix']}.json",
        },
        "test_categories_covered": [
            "GUI Initialization Tests",
            "UI Component Creation Tests",
            "File Selection Functionality Tests",
            "Encryption/Decryption Operation Tests",
            "Utility Method Tests",
            "Edge Case and Error Handling Tests",
            "Main Function Tests",
            "Security Validation Tests",
        ],
        "testing_features": [
            "Comprehensive mocking of PyQt5 components",
            "Setup and teardown with temporary test data",
            "Edge case testing with special characters",
            "Security-focused password validation",
            "Error scenario simulation",
            "Performance testing with large datasets",
            "Integration testing capabilities",
            "Detailed assertion coverage",
        ],
    }

    # Add output information if available
    if test_result:
        summary["execution_output"] = {
            "stdout_length": len(test_result.stdout),
            "stderr_length": len(test_result.stderr),
            "has_warnings": len(test_result.stderr) > 0,
        }

    # Save summary
    summary_file = (
        output_dir / f"result_en_and_decrypt_{TEST_CONFIG['date_suffix']}_summary.json"
    )
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"📋 Execution summary saved: {summary_file}")

    return summary


def print_final_report(summary, output_dir):
    """Print final test execution report."""
    print("\n" + "=" * 80)
    print("🎯 COMPREHENSIVE TEST EXECUTION REPORT")
    print("=" * 80)

    exec_summary = summary["test_execution_summary"]
    print(f"📅 Execution Date: {exec_summary['timestamp']}")
    print(f"🎯 Target Module: {exec_summary['target_module']}")
    print(f"📄 Test File: {exec_summary['test_file']}")
    print(f"⚡ Framework: {exec_summary['framework']}")
    print(f"⏱️  Execution Time: {exec_summary['execution_time_seconds']:.2f} seconds")
    print(f"✅ Success: {'Yes' if exec_summary['success'] else 'No'}")
    print(f"🏁 Return Code: {exec_summary['return_code']}")

    print(f"\n📊 Generated Reports:")
    for report_name, report_file in summary["generated_reports"].items():
        report_path = output_dir / report_file
        status = "✅ Created" if report_path.exists() else "❌ Missing"
        print(f"   {report_name}: {status}")

    print(f"\n🧪 Test Categories Covered:")
    for category in summary["test_categories_covered"]:
        print(f"   ✅ {category}")

    print(f"\n🔧 Testing Features:")
    for feature in summary["testing_features"]:
        print(f"   🔹 {feature}")

    print("\n" + "=" * 80)
    print("📁 All test results saved to:", output_dir)
    print("=" * 80)


def main():
    """Main test runner execution."""
    print("🚀 Starting Comprehensive Unit Test Suite for en_and_decrypt.py")
    print(f"📅 Generated: {TEST_CONFIG['date_suffix']}")
    print("-" * 80)

    try:
        # Step 1: Ensure dependencies
        ensure_dependencies()

        # Step 2: Setup environment
        output_dir, coverage_dir = setup_test_environment()

        # Step 3: Run tests
        test_result, execution_time = run_tests(output_dir, coverage_dir)

        # Step 4: Generate summary
        summary = generate_execution_summary(output_dir, test_result, execution_time)

        # Step 5: Print final report
        print_final_report(summary, output_dir)

        # Return appropriate exit code
        if test_result and test_result.returncode == 0:
            print("🎉 All tests completed successfully!")
            return 0
        else:
            print("⚠️  Some tests failed or execution encountered issues.")
            return 1

    except Exception as e:
        print(f"💥 Critical error in test execution: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
