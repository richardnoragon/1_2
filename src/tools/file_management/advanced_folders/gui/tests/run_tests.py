"""
Test Execution Runner for Advanced Folders GUI Test Suite

Comprehensive test runner that executes all test categories with proper
reporting, coverage analysis, and result documentation. Provides
enterprise-level test execution with detailed reporting.

Author: RFU Development Team
Version: 1.0.0
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import pytest


class TestExecutionRunner:
    """Main test execution runner with comprehensive reporting."""

    def __init__(self, test_directory=None):
        """Initialize the test runner."""
        self.test_directory = test_directory or Path(__file__).parent
        self.results = {}
        self.start_time = None
        self.end_time = None

    def run_all_tests(self, generate_reports=True):
        """Run all test categories and generate reports."""
        print("=" * 80)
        print("ADVANCED FOLDERS GUI TEST SUITE")
        print("=" * 80)
        print(f"Test Directory: {self.test_directory}")
        print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        self.start_time = datetime.now()

        # Define test categories
        test_categories = [
            {
                "name": "Unit Tests",
                "marker": "unit",
                "file": "test_gui_components.py",
                "description": "Individual component unit tests",
            },
            {
                "name": "Integration Tests",
                "marker": "integration",
                "file": "test_integration.py",
                "description": "Component integration and workflow tests",
            },
            {
                "name": "Performance Tests",
                "marker": "performance",
                "file": "test_performance.py",
                "description": "Performance and stress testing",
            },
            {
                "name": "Accessibility Tests",
                "marker": "accessibility",
                "file": "test_accessibility.py",
                "description": "WCAG compliance and accessibility testing",
            },
        ]

        # Execute each test category
        for category in test_categories:
            self._run_test_category(category)

        self.end_time = datetime.now()

        # Generate reports
        if generate_reports:
            self._generate_summary_report()
            self._generate_detailed_report()
            self._generate_coverage_report()

        return self.results

    def _run_test_category(self, category):
        """Run a specific test category."""
        print(f"Running {category['name']}...")
        print(f"Description: {category['description']}")
        print(f"File: {category['file']}")
        print("-" * 60)

        # Prepare pytest arguments
        test_file = self.test_directory / category["file"]
        pytest_args = [
            str(test_file),
            f"-m",
            category["marker"],
            "-v",
            "--tb=short",
            "--durations=10",
            f"--junit-xml={self.test_directory}/results_{category['marker']}.xml",
            f"--html={self.test_directory}/report_{category['marker']}.html",
            "--self-contained-html",
        ]

        # Add coverage for unit and integration tests
        if category["marker"] in ["unit", "integration"]:
            pytest_args.extend(
                [
                    "--cov=../",
                    f"--cov-report=html:{self.test_directory}/coverage_{category['marker']}",
                    "--cov-report=term-missing",
                ]
            )

        start_time = time.time()

        try:
            # Run pytest
            result = pytest.main(pytest_args)
            status = "PASSED" if result == 0 else "FAILED"

        except Exception as e:
            print(f"Error running {category['name']}: {e}")
            result = -1
            status = "ERROR"

        end_time = time.time()
        execution_time = end_time - start_time

        # Store results
        self.results[category["marker"]] = {
            "name": category["name"],
            "status": status,
            "execution_time": execution_time,
            "return_code": result,
            "file": category["file"],
        }

        print(f"Status: {status}")
        print(f"Execution Time: {execution_time:.2f} seconds")
        print(f"Return Code: {result}")
        print()

    def _generate_summary_report(self):
        """Generate a summary report of all test results."""
        report_file = self.test_directory / "test_summary_report.txt"

        with open(report_file, "w") as f:
            f.write("ADVANCED FOLDERS GUI TEST SUITE - SUMMARY REPORT\n")
            f.write("=" * 60 + "\n\n")

            f.write(
                f"Execution Start: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            )
            f.write(
                f"Execution End: {self.end_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            )

            total_time = (self.end_time - self.start_time).total_seconds()
            f.write(f"Total Execution Time: {total_time:.2f} seconds\n\n")

            # Test category results
            f.write("TEST CATEGORY RESULTS:\n")
            f.write("-" * 30 + "\n")

            total_passed = 0
            total_failed = 0

            for category, result in self.results.items():
                status_symbol = "✓" if result["status"] == "PASSED" else "✗"
                f.write(
                    f"{status_symbol} {result['name']:<20} {result['status']:<8} ({result['execution_time']:.2f}s)\n"
                )

                if result["status"] == "PASSED":
                    total_passed += 1
                else:
                    total_failed += 1

            f.write(f"\nOVERALL RESULTS:\n")
            f.write(f"Passed: {total_passed}\n")
            f.write(f"Failed: {total_failed}\n")
            f.write(
                f"Success Rate: {(total_passed / len(self.results) * 100):.1f}%\n"
            )

            # Recommendations
            f.write(f"\nRECOMMENDATIONS:\n")
            f.write("-" * 20 + "\n")

            if total_failed == 0:
                f.write("✓ All test categories passed successfully\n")
                f.write("✓ GUI components meet enterprise quality standards\n")
                f.write("✓ Ready for production deployment\n")
            else:
                f.write(
                    "⚠ Some test categories failed - review detailed reports\n"
                )
                f.write("⚠ Address failing tests before deployment\n")

                for category, result in self.results.items():
                    if result["status"] != "PASSED":
                        f.write(f"  - Review {result['name']} results\n")

        print(f"Summary report generated: {report_file}")

    def _generate_detailed_report(self):
        """Generate detailed JSON report for programmatic access."""
        report_file = self.test_directory / "test_detailed_report.json"

        detailed_results = {
            "execution_info": {
                "start_time": self.start_time.isoformat(),
                "end_time": self.end_time.isoformat(),
                "total_duration": (
                    self.end_time - self.start_time
                ).total_seconds(),
                "test_directory": str(self.test_directory),
            },
            "test_categories": self.results,
            "summary": {
                "total_categories": len(self.results),
                "passed_categories": sum(
                    1 for r in self.results.values() if r["status"] == "PASSED"
                ),
                "failed_categories": sum(
                    1 for r in self.results.values() if r["status"] != "PASSED"
                ),
                "success_rate": sum(
                    1 for r in self.results.values() if r["status"] == "PASSED"
                )
                / len(self.results)
                * 100,
            },
            "file_locations": {
                "unit_tests": "test_gui_components.py",
                "integration_tests": "test_integration.py",
                "performance_tests": "test_performance.py",
                "accessibility_tests": "test_accessibility.py",
                "configuration": "conftest.py",
            },
        }

        with open(report_file, "w") as f:
            json.dump(detailed_results, f, indent=2, default=str)

        print(f"Detailed report generated: {report_file}")

    def _generate_coverage_report(self):
        """Generate coverage summary report."""
        coverage_file = self.test_directory / "coverage_summary.txt"

        try:
            # Run coverage report
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "coverage",
                    "report",
                    "--include=../*",
                    "--omit=test_*",
                ],
                capture_output=True,
                text=True,
                cwd=self.test_directory,
            )

            with open(coverage_file, "w") as f:
                f.write("CODE COVERAGE SUMMARY\n")
                f.write("=" * 30 + "\n\n")
                f.write(result.stdout)

                if result.stderr:
                    f.write("\nERRORS:\n")
                    f.write(result.stderr)

            print(f"Coverage report generated: {coverage_file}")

        except Exception as e:
            print(f"Could not generate coverage report: {e}")

    def run_specific_category(self, category_name):
        """Run a specific test category only."""
        category_map = {
            "unit": ("test_gui_components.py", "unit"),
            "integration": ("test_integration.py", "integration"),
            "performance": ("test_performance.py", "performance"),
            "accessibility": ("test_accessibility.py", "accessibility"),
        }

        if category_name not in category_map:
            print(f"Unknown category: {category_name}")
            print(f"Available categories: {list(category_map.keys())}")
            return

        file_name, marker = category_map[category_name]
        category = {
            "name": category_name.title() + " Tests",
            "marker": marker,
            "file": file_name,
            "description": f"{category_name.title()} testing category",
        }

        self.start_time = datetime.now()
        self._run_test_category(category)
        self.end_time = datetime.now()

        print(f"\n{category_name.title()} tests completed.")
        return self.results.get(marker)


def main():
    """Main entry point for test execution."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Advanced Folders GUI Test Runner"
    )
    parser.add_argument(
        "--category",
        choices=["unit", "integration", "performance", "accessibility", "all"],
        default="all",
        help="Test category to run (default: all)",
    )
    parser.add_argument(
        "--no-reports", action="store_true", help="Skip report generation"
    )
    parser.add_argument("--test-dir", help="Custom test directory path")

    args = parser.parse_args()

    # Initialize runner
    test_dir = Path(args.test_dir) if args.test_dir else None
    runner = TestExecutionRunner(test_dir)

    try:
        if args.category == "all":
            results = runner.run_all_tests(
                generate_reports=not args.no_reports
            )

            # Print final summary
            print("=" * 80)
            print("FINAL SUMMARY")
            print("=" * 80)

            for category, result in results.items():
                status_symbol = "✓" if result["status"] == "PASSED" else "✗"
                print(f"{status_symbol} {result['name']}: {result['status']}")

            success_rate = (
                sum(1 for r in results.values() if r["status"] == "PASSED")
                / len(results)
                * 100
            )
            print(f"\nOverall Success Rate: {success_rate:.1f}%")

            if success_rate == 100:
                print(
                    "🎉 All tests passed! GUI components ready for deployment."
                )
                sys.exit(0)
            else:
                print("⚠️  Some tests failed. Review reports for details.")
                sys.exit(1)
        else:
            result = runner.run_specific_category(args.category)
            if result and result["status"] == "PASSED":
                print(f"✓ {args.category.title()} tests passed!")
                sys.exit(0)
            else:
                print(f"✗ {args.category.title()} tests failed!")
                sys.exit(1)

    except KeyboardInterrupt:
        print("\nTest execution interrupted by user.")
        sys.exit(130)
    except Exception as e:
        print(f"Error during test execution: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
