"""
Phase 2 Integration Tests Runner
Comprehensive test execution runner for RFU Phase 2 Core Integration Tests

Features:
- Executes both Week 5-6 Component Tests and Week 7-8 Cross-Component Tests
- Generates detailed reports and metrics
- Provides performance benchmarking
- Supports selective test execution
- Creates comprehensive summaries
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# Test categories and their corresponding files
WEEK_5_6_TESTS = {
    "database_integration": "week5_6_component_tests/test_database_integration.py",
    "file_operations_integration": "week5_6_component_tests/test_file_operations_integration.py",
    "gui_integration": "week5_6_component_tests/test_gui_integration.py",
    "external_service_integration": "week5_6_component_tests/test_external_service_integration.py",
}

WEEK_7_8_TESTS = {
    "data_flow_validation": "week7_8_cross_component_tests/test_data_flow_validation.py",
    "event_propagation": "week7_8_cross_component_tests/test_event_propagation.py",
    "shared_resource_access": "week7_8_cross_component_tests/test_shared_resource_access.py",
    "error_propagation": "week7_8_cross_component_tests/test_error_propagation.py",
}

ALL_TESTS = {**WEEK_5_6_TESTS, **WEEK_7_8_TESTS}


class Phase2TestRunner:
    """Comprehensive test runner for Phase 2 integration tests"""

    def __init__(self, base_path=None):
        self.base_path = base_path or Path(__file__).parent
        self.results = {
            "execution_summary": {
                "start_time": None,
                "end_time": None,
                "total_duration": 0,
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0,
                "skipped_tests": 0,
                "error_tests": 0,
            },
            "test_categories": {},
            "performance_metrics": {},
            "detailed_results": {},
            "recommendations": [],
        }

    def run_tests(
        self, test_categories=None, verbose=False, generate_html=True
    ):
        """Run specified test categories or all tests"""
        print("=" * 70)
        print("RFU Phase 2 Core Integration Tests")
        print("=" * 70)

        # Determine which tests to run
        if test_categories:
            tests_to_run = {
                k: v for k, v in ALL_TESTS.items() if k in test_categories
            }
        else:
            tests_to_run = ALL_TESTS

        print(f"Running {len(tests_to_run)} test categories...")
        print()

        self.results["execution_summary"][
            "start_time"
        ] = datetime.now().isoformat()
        start_time = time.time()

        # Execute each test category
        for category, test_file in tests_to_run.items():
            print(f"Executing {category}...")
            test_result = self._run_single_test(category, test_file, verbose)
            self.results["test_categories"][category] = test_result

            # Update summary statistics
            self._update_summary_stats(test_result)

            print(f"  Result: {test_result['status']}")
            if test_result["status"] == "FAILED":
                print(f"  Failures: {test_result['failures']}")
            print()

        # Calculate final metrics
        end_time = time.time()
        self.results["execution_summary"][
            "end_time"
        ] = datetime.now().isoformat()
        self.results["execution_summary"]["total_duration"] = (
            end_time - start_time
        )

        # Generate reports
        self._generate_performance_metrics()
        self._generate_recommendations()

        # Output results
        self._print_summary()

        if generate_html:
            self._generate_html_report()

        return self.results

    def _run_single_test(self, category, test_file, verbose):
        """Run a single test file and collect results"""
        test_path = self.base_path / test_file

        if not test_path.exists():
            return {
                "status": "ERROR",
                "message": f"Test file not found: {test_file}",
                "duration": 0,
                "tests_run": 0,
                "failures": 0,
                "errors": 0,
                "skipped": 0,
            }

        # Prepare pytest command
        cmd = [
            sys.executable,
            "-m",
            "pytest",
            str(test_path),
            "--tb=short",
            "--json-report",
            "--json-report-file="
            + str(self.base_path / f"{category}_results.json"),
            "--verbose" if verbose else "--quiet",
        ]

        start_time = time.time()

        try:
            # Execute pytest
            result = subprocess.run(
                cmd, capture_output=True, text=True, cwd=str(self.base_path)
            )

            duration = time.time() - start_time

            # Parse JSON results if available
            json_file = self.base_path / f"{category}_results.json"
            test_details = self._parse_json_results(json_file)

            # Clean up JSON file
            if json_file.exists():
                os.unlink(json_file)

            # Determine status
            status = "PASSED" if result.returncode == 0 else "FAILED"

            return {
                "status": status,
                "duration": duration,
                "tests_run": test_details.get("total", 0),
                "failures": test_details.get("failed", 0),
                "errors": test_details.get("error", 0),
                "skipped": test_details.get("skipped", 0),
                "stdout": result.stdout,
                "stderr": result.stderr,
                "details": test_details,
            }

        except Exception as e:
            return {
                "status": "ERROR",
                "message": str(e),
                "duration": time.time() - start_time,
                "tests_run": 0,
                "failures": 0,
                "errors": 1,
                "skipped": 0,
            }

    def _parse_json_results(self, json_file):
        """Parse pytest JSON results if available"""
        try:
            if json_file.exists():
                with open(json_file, "r") as f:
                    data = json.load(f)

                summary = data.get("summary", {})
                return {
                    "total": summary.get("total", 0),
                    "passed": summary.get("passed", 0),
                    "failed": summary.get("failed", 0),
                    "error": summary.get("error", 0),
                    "skipped": summary.get("skipped", 0),
                    "tests": data.get("tests", []),
                }
        except Exception:
            pass

        return {"total": 0, "passed": 0, "failed": 0, "error": 0, "skipped": 0}

    def _update_summary_stats(self, test_result):
        """Update summary statistics"""
        summary = self.results["execution_summary"]

        summary["total_tests"] += test_result.get("tests_run", 0)
        summary["failed_tests"] += test_result.get("failures", 0)
        summary["error_tests"] += test_result.get("errors", 0)
        summary["skipped_tests"] += test_result.get("skipped", 0)

        # Calculate passed tests
        tests_run = test_result.get("tests_run", 0)
        failures = test_result.get("failures", 0)
        errors = test_result.get("errors", 0)
        skipped = test_result.get("skipped", 0)

        summary["passed_tests"] += max(
            0, tests_run - failures - errors - skipped
        )

    def _generate_performance_metrics(self):
        """Generate performance metrics from test results"""
        metrics = {
            "total_execution_time": self.results["execution_summary"][
                "total_duration"
            ],
            "average_test_time": 0,
            "slowest_categories": [],
            "fastest_categories": [],
            "category_performance": {},
        }

        # Calculate category performance
        category_times = []
        for category, result in self.results["test_categories"].items():
            duration = result.get("duration", 0)
            tests_count = result.get("tests_run", 0)

            metrics["category_performance"][category] = {
                "duration": duration,
                "tests_count": tests_count,
                "avg_test_time": duration / max(1, tests_count),
            }

            category_times.append((category, duration))

        # Sort by duration
        category_times.sort(key=lambda x: x[1])

        if category_times:
            metrics["fastest_categories"] = category_times[:2]
            metrics["slowest_categories"] = category_times[-2:]

            total_tests = sum(
                r.get("tests_run", 0)
                for r in self.results["test_categories"].values()
            )
            if total_tests > 0:
                metrics["average_test_time"] = (
                    metrics["total_execution_time"] / total_tests
                )

        self.results["performance_metrics"] = metrics

    def _generate_recommendations(self):
        """Generate recommendations based on test results"""
        recommendations = []

        # Check for failures
        failed_categories = [
            cat
            for cat, result in self.results["test_categories"].items()
            if result.get("status") == "FAILED"
        ]

        if failed_categories:
            recommendations.append(
                {
                    "type": "CRITICAL",
                    "message": f"Address failing test categories: {', '.join(failed_categories)}",
                }
            )

        # Check for slow tests
        slow_threshold = 60  # seconds
        slow_categories = [
            cat
            for cat, result in self.results["test_categories"].items()
            if result.get("duration", 0) > slow_threshold
        ]

        if slow_categories:
            recommendations.append(
                {
                    "type": "PERFORMANCE",
                    "message": f"Optimize slow test categories: {', '.join(slow_categories)}",
                }
            )

        # Check coverage
        total_tests = self.results["execution_summary"]["total_tests"]
        if total_tests < 50:  # Arbitrary threshold
            recommendations.append(
                {
                    "type": "COVERAGE",
                    "message": "Consider adding more comprehensive test cases",
                }
            )

        # Success recommendations
        if not failed_categories:
            recommendations.append(
                {
                    "type": "SUCCESS",
                    "message": "All integration tests passed - system integration is healthy",
                }
            )

            recommendations.append(
                {
                    "type": "MAINTENANCE",
                    "message": "Schedule regular integration test execution",
                }
            )

        self.results["recommendations"] = recommendations

    def _print_summary(self):
        """Print test execution summary"""
        print("=" * 70)
        print("TEST EXECUTION SUMMARY")
        print("=" * 70)

        summary = self.results["execution_summary"]

        print(f"Total Duration: {summary['total_duration']:.2f} seconds")
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed_tests']}")
        print(f"Failed: {summary['failed_tests']}")
        print(f"Errors: {summary['error_tests']}")
        print(f"Skipped: {summary['skipped_tests']}")

        # Calculate success rate
        if summary["total_tests"] > 0:
            success_rate = (
                summary["passed_tests"] / summary["total_tests"]
            ) * 100
            print(f"Success Rate: {success_rate:.1f}%")

        print()
        print("Category Results:")
        print("-" * 50)

        for category, result in self.results["test_categories"].items():
            status = result.get("status", "UNKNOWN")
            duration = result.get("duration", 0)
            tests_run = result.get("tests_run", 0)

            print(
                f"{category:30} {status:8} ({tests_run:2d} tests, {duration:5.2f}s)"
            )

        print()
        print("Recommendations:")
        print("-" * 50)

        for rec in self.results["recommendations"]:
            rec_type = rec["type"]
            message = rec["message"]
            print(f"[{rec_type}] {message}")

        print()

    def _generate_html_report(self):
        """Generate HTML report"""
        report_file = self.base_path / "phase2_test_report.html"

        html_content = self._create_html_report()

        with open(report_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"HTML report generated: {report_file}")

    def _create_html_report(self):
        """Create HTML report content"""
        summary = self.results["execution_summary"]

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>RFU Phase 2 Integration Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ background-color: #f8f9fa; padding: 20px; border-radius: 5px; }}
        .summary {{ display: flex; justify-content: space-around; margin: 20px 0; }}
        .metric {{ text-align: center; padding: 15px; background-color: #e9ecef; border-radius: 5px; }}
        .metric h3 {{ margin: 0; color: #495057; }}
        .metric .number {{ font-size: 2em; font-weight: bold; color: #007bff; }}
        .passed {{ color: #28a745; }}
        .failed {{ color: #dc3545; }}
        .category {{ margin: 15px 0; padding: 15px; border: 1px solid #dee2e6; border-radius: 5px; }}
        .category h3 {{ margin-top: 0; }}
        .status-passed {{ background-color: #d4edda; color: #155724; }}
        .status-failed {{ background-color: #f8d7da; color: #721c24; }}
        .status-error {{ background-color: #fff3cd; color: #856404; }}
        .recommendations {{ margin-top: 30px; }}
        .recommendation {{ padding: 10px; margin: 5px 0; border-radius: 5px; }}
        .critical {{ background-color: #f8d7da; border-left: 4px solid #dc3545; }}
        .performance {{ background-color: #fff3cd; border-left: 4px solid #ffc107; }}
        .success {{ background-color: #d4edda; border-left: 4px solid #28a745; }}
        .maintenance {{ background-color: #d1ecf1; border-left: 4px solid #17a2b8; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>RFU Phase 2 Core Integration Test Report</h1>
        <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Duration:</strong> {summary['total_duration']:.2f} seconds</p>
    </div>

    <div class="summary">
        <div class="metric">
            <h3>Total Tests</h3>
            <div class="number">{summary['total_tests']}</div>
        </div>
        <div class="metric">
            <h3>Passed</h3>
            <div class="number passed">{summary['passed_tests']}</div>
        </div>
        <div class="metric">
            <h3>Failed</h3>
            <div class="number failed">{summary['failed_tests']}</div>
        </div>
        <div class="metric">
            <h3>Success Rate</h3>
            <div class="number">
                {(summary['passed_tests'] / max(1, summary['total_tests']) * 100):.1f}%
            </div>
        </div>
    </div>

    <h2>Test Categories</h2>
"""

        # Add category details
        for category, result in self.results["test_categories"].items():
            status = result.get("status", "UNKNOWN")
            status_class = f"status-{status.lower()}"

            html += f"""
    <div class="category {status_class}">
        <h3>{category.replace('_', ' ').title()}</h3>
        <p><strong>Status:</strong> {status}</p>
        <p><strong>Duration:</strong> {result.get('duration', 0):.2f} seconds</p>
        <p><strong>Tests Run:</strong> {result.get('tests_run', 0)}</p>
        <p><strong>Failures:</strong> {result.get('failures', 0)}</p>
    </div>
"""

        # Add recommendations
        html += """
    <div class="recommendations">
        <h2>Recommendations</h2>
"""

        for rec in self.results["recommendations"]:
            rec_type = rec["type"].lower()
            html += f"""
        <div class="recommendation {rec_type}">
            <strong>[{rec['type']}]</strong> {rec['message']}
        </div>
"""

        html += """
    </div>
</body>
</html>
"""

        return html

    def save_results(self, filename=None):
        """Save results to JSON file"""
        if filename is None:
            filename = f"phase2_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        results_file = self.base_path / filename

        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, default=str)

        print(f"Results saved to: {results_file}")

        return results_file


def main():
    """Main entry point for the test runner"""
    parser = argparse.ArgumentParser(
        description="RFU Phase 2 Integration Test Runner"
    )

    parser.add_argument(
        "--categories",
        nargs="*",
        choices=list(ALL_TESTS.keys()) + ["week5-6", "week7-8"],
        help="Specific test categories to run (default: all)",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    parser.add_argument(
        "--no-html", action="store_true", help="Skip HTML report generation"
    )

    parser.add_argument(
        "--save-results", help="Save results to specified JSON file"
    )

    args = parser.parse_args()

    # Handle special category groups
    test_categories = None
    if args.categories:
        if "week5-6" in args.categories:
            test_categories = list(WEEK_5_6_TESTS.keys())
        elif "week7-8" in args.categories:
            test_categories = list(WEEK_7_8_TESTS.keys())
        else:
            test_categories = args.categories

    # Create and run test runner
    runner = Phase2TestRunner()

    try:
        results = runner.run_tests(
            test_categories=test_categories,
            verbose=args.verbose,
            generate_html=not args.no_html,
        )

        # Save results if requested
        if args.save_results:
            runner.save_results(args.save_results)

        # Exit with appropriate code
        failed_tests = results["execution_summary"]["failed_tests"]
        error_tests = results["execution_summary"]["error_tests"]

        if failed_tests > 0 or error_tests > 0:
            sys.exit(1)
        else:
            sys.exit(0)

    except KeyboardInterrupt:
        print("\nTest execution interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"Error running tests: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
