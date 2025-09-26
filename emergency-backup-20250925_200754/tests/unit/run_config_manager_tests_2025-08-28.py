"""
Test runner script for config_manager comprehensive testing
File: run_config_manager_tests_2025-08-28.py
Date: 2025-08-28
"""

import datetime
import os
import subprocess
import sys
from pathlib import Path


def install_requirements():
    """Install required testing packages."""
    print("Installing testing requirements...")
    requirements_file = (
        Path(__file__).parent / "test_requirements_2025-08-28.txt"
    )

    try:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "-r",
                str(requirements_file),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        print("✓ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install requirements: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False


def run_tests():
    """Run the comprehensive tests with detailed reporting."""
    print(
        f"\nStarting ConfigManager comprehensive tests at {datetime.datetime.now()}"
    )
    print("=" * 70)

    # Change to the test directory
    test_dir = Path(__file__).parent
    os.chdir(test_dir)

    # Test command with comprehensive reporting
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "test_config_manager_2025-08-28.py",
        "-v",
        "--tb=short",
        "--color=yes",
        "--durations=10",
        "--html=result_config_manager_2025-08-28.html",
        "--self-contained-html",
        "--json-report",
        "--json-report-file=result_config_manager_2025-08-28.json",
        f"--cov={Path(__file__).parent.parent.parent / 'config_manager.py'}",
        "--cov-report=html:result_config_manager_coverage_2025-08-28",
        "--cov-report=json:result_config_manager_coverage_2025-08-28.json",
        "--cov-report=term-missing",
        "--cov-branch",
        "--cov-fail-under=85",
        "--capture=no",
    ]

    try:
        result = subprocess.run(cmd, capture_output=False, text=True)

        print("\n" + "=" * 70)
        print("Test execution completed!")
        print(f"Exit code: {result.returncode}")

        # List generated files
        print("\nGenerated test result files:")
        result_files = [
            "result_config_manager_2025-08-28.html",
            "result_config_manager_2025-08-28.json",
            "result_config_manager_coverage_2025-08-28.json",
        ]

        for file in result_files:
            if Path(file).exists():
                print(f"✓ {file}")
            else:
                print(f"✗ {file} (not found)")

        # Check for coverage HTML directory
        coverage_dir = Path("result_config_manager_coverage_2025-08-28")
        if coverage_dir.exists():
            print(f"✓ {coverage_dir}/ (HTML coverage report)")
        else:
            print(f"✗ {coverage_dir}/ (not found)")

        return result.returncode == 0

    except Exception as e:
        print(f"✗ Test execution failed: {e}")
        return False


def generate_summary_report():
    """Generate a summary report of the test execution."""
    summary_file = Path("result_config_manager_summary_2025-08-28.txt")

    with open(summary_file, "w", encoding="utf-8") as f:
        f.write("ConfigManager Comprehensive Test Summary\n")
        f.write("=" * 50 + "\n")
        f.write(f"Execution Date: {datetime.datetime.now()}\n")
        f.write(f"Test File: test_config_manager_2025-08-28.py\n")
        f.write(f"Target Module: config_manager.py\n\n")

        f.write("Generated Reports:\n")
        f.write("- HTML Test Report: result_config_manager_2025-08-28.html\n")
        f.write("- JSON Test Report: result_config_manager_2025-08-28.json\n")
        f.write(
            "- HTML Coverage Report: result_config_manager_coverage_2025-08-28/\n"
        )
        f.write(
            "- JSON Coverage Report: result_config_manager_coverage_2025-08-28.json\n\n"
        )

        f.write("Test Categories Covered:\n")
        f.write("- Singleton pattern implementation\n")
        f.write("- Configuration management (get/set/remove)\n")
        f.write("- Section management\n")
        f.write("- File I/O operations (save/load/export/import)\n")
        f.write("- Error handling and edge cases\n")
        f.write("- Thread safety\n")
        f.write("- Data type preservation\n")
        f.write("- Default value handling\n")
        f.write("- Auto-save functionality\n")
        f.write("- Configuration reset and defaults\n")

    print(f"✓ Summary report generated: {summary_file}")


def main():
    """Main test execution function."""
    print("ConfigManager Comprehensive Test Suite")
    print("Date: 2025-08-28")
    print("=" * 50)

    # Step 1: Install requirements
    if not install_requirements():
        print("Failed to install requirements. Exiting.")
        return False

    # Step 2: Run tests
    success = run_tests()

    # Step 3: Generate summary
    generate_summary_report()

    if success:
        print("\n🎉 All tests completed successfully!")
    else:
        print("\n⚠️  Some tests failed. Check the reports for details.")

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
