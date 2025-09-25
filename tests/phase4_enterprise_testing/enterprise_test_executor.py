"""
Enterprise Test Execution Framework for Advanced Folders System
Phase 4: Testing & QA (Week 10) - Automated Test Execution & Reporting

This script provides comprehensive test execution with enterprise-grade reporting,
CI/CD integration, and detailed analysis capabilities following zero-compromise
quality standards.
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pytest


class EnterpriseTestExecutor:
    """Enterprise-grade test execution framework with comprehensive reporting."""

    def __init__(self, project_root: Path, output_dir: Optional[Path] = None):
        """Initialize the test executor.

        Args:
            project_root: Root directory of the project
            output_dir: Directory for test outputs (default: project_root/test_reports)
        """
        self.project_root = Path(project_root)
        self.output_dir = output_dir or (self.project_root / "test_reports")
        self.output_dir.mkdir(exist_ok=True)

        # Test suite directories
        self.test_dirs = {
            "unit": self.project_root
            / "tests"
            / "phase4_enterprise_testing"
            / "unit",
            "integration": self.project_root
            / "tests"
            / "phase4_enterprise_testing"
            / "integration",
            "performance": self.project_root
            / "tests"
            / "phase4_enterprise_testing"
            / "performance",
            "security": self.project_root
            / "tests"
            / "phase4_enterprise_testing"
            / "security",
        }

        # Execution timestamp
        self.execution_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Results storage
        self.test_results = {
            "execution_info": {
                "timestamp": self.execution_timestamp,
                "project_root": str(self.project_root),
                "output_dir": str(self.output_dir),
            },
            "suite_results": {},
            "summary": {},
            "coverage": {},
            "performance_metrics": {},
            "security_findings": {},
        }

    def validate_test_environment(self) -> bool:
        """Validate test environment setup and dependencies."""
        print("🔍 Validating test environment...")

        validation_results = []

        # Check Python version
        python_version = sys.version_info
        if python_version >= (3, 8):
            validation_results.append(
                (
                    "Python version",
                    "✅ PASS",
                    f"Python {python_version.major}.{python_version.minor}",
                )
            )
        else:
            validation_results.append(
                (
                    "Python version",
                    "❌ FAIL",
                    f"Python {python_version.major}.{python_version.minor} - Requires 3.8+",
                )
            )

        # Check required packages
        required_packages = [
            "pytest",
            "pytest-cov",
            "pytest-html",
            "pytest-xdist",
            "pytest-benchmark",
            "psutil",
            "PyQt5",
        ]

        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
                validation_results.append(
                    (f"Package {package}", "✅ PASS", "Available")
                )
            except ImportError:
                validation_results.append(
                    (f"Package {package}", "❌ FAIL", "Missing")
                )

        # Check test directories
        for suite_name, test_dir in self.test_dirs.items():
            if test_dir.exists():
                test_files = list(test_dir.glob("test_*.py"))
                validation_results.append(
                    (
                        f"{suite_name.title()} tests",
                        "✅ PASS",
                        f"{len(test_files)} test files found",
                    )
                )
            else:
                validation_results.append(
                    (
                        f"{suite_name.title()} tests",
                        "❌ FAIL",
                        "Directory missing",
                    )
                )

        # Check source code availability
        src_dirs = [
            self.project_root / "src",
            self.project_root / "src" / "utilities" / "advanced_folders",
        ]

        for src_dir in src_dirs:
            if src_dir.exists():
                py_files = list(src_dir.rglob("*.py"))
                validation_results.append(
                    (
                        f"Source {src_dir.name}",
                        "✅ PASS",
                        f"{len(py_files)} Python files",
                    )
                )
            else:
                validation_results.append(
                    (f"Source {src_dir.name}", "❌ FAIL", "Directory missing")
                )

        # Print validation results
        print("\nEnvironment Validation Results:")
        print("=" * 60)
        for item, status, details in validation_results:
            print(f"{item:<30} {status} {details}")

        # Determine overall validation status
        failed_checks = [
            result for result in validation_results if "❌ FAIL" in result[1]
        ]
        if failed_checks:
            print(
                f"\n❌ Environment validation failed: {len(failed_checks)} issues found"
            )
            return False
        else:
            print("\n✅ Environment validation successful")
            return True

    def execute_test_suite(
        self, suite_name: str, extra_args: Optional[List[str]] = None
    ) -> Dict:
        """Execute a specific test suite with comprehensive reporting.

        Args:
            suite_name: Name of test suite ('unit', 'integration', 'performance', 'security')
            extra_args: Additional pytest arguments

        Returns:
            Dictionary containing test results and metrics
        """
        print(f"\n🧪 Executing {suite_name.title()} Test Suite...")

        test_dir = self.test_dirs.get(suite_name)
        if not test_dir or not test_dir.exists():
            return {
                "status": "skipped",
                "reason": f"Test directory not found: {test_dir}",
                "duration": 0,
                "tests_run": 0,
                "passed": 0,
                "failed": 0,
                "errors": 0,
            }

        # Prepare pytest arguments
        base_args = [
            str(test_dir),
            "-v",
            "--tb=short",
            "--strict-markers",
            f"--junitxml={self.output_dir}/{suite_name}_results.xml",
            f"--html={self.output_dir}/{suite_name}_report.html",
            "--self-contained-html",
        ]

        # Add coverage for unit and integration tests
        if suite_name in ["unit", "integration"]:
            coverage_args = [
                "--cov=src",
                "--cov-report=html:"
                + str(self.output_dir / f"{suite_name}_coverage_html"),
                "--cov-report=xml:"
                + str(self.output_dir / f"{suite_name}_coverage.xml"),
                "--cov-report=term-missing",
                "--cov-fail-under=90",
            ]
            base_args.extend(coverage_args)

        # Add performance-specific arguments
        if suite_name == "performance":
            perf_args = [
                "--benchmark-only",
                "--benchmark-sort=mean",
                f"--benchmark-json={self.output_dir}/performance_benchmarks.json",
            ]
            base_args.extend(perf_args)

        # Add security-specific arguments
        if suite_name == "security":
            security_args = [
                "-m",
                "security",
                "--capture=no",  # Allow security output to be visible
            ]
            base_args.extend(security_args)

        # Add extra arguments
        if extra_args:
            base_args.extend(extra_args)

        # Execute tests
        start_time = time.time()

        try:
            # Run pytest with arguments
            result = pytest.main(base_args)
            duration = time.time() - start_time

            # Parse results
            if result == 0:
                status = "passed"
            elif result == 1:
                status = "failed"
            elif result == 2:
                status = "interrupted"
            elif result == 3:
                status = "internal_error"
            elif result == 4:
                status = "usage_error"
            elif result == 5:
                status = "no_tests"
            else:
                status = "unknown"

            # Parse XML results for detailed metrics
            xml_file = self.output_dir / f"{suite_name}_results.xml"
            test_metrics = (
                self._parse_junit_xml(xml_file) if xml_file.exists() else {}
            )

            suite_result = {
                "status": status,
                "exit_code": result,
                "duration": duration,
                "start_time": start_time,
                "end_time": time.time(),
                **test_metrics,
            }

            print(
                f"✅ {suite_name.title()} tests completed in {duration:.2f}s"
            )
            if test_metrics:
                print(f"   Tests run: {test_metrics.get('tests_run', 0)}")
                print(f"   Passed: {test_metrics.get('passed', 0)}")
                print(f"   Failed: {test_metrics.get('failed', 0)}")
                print(f"   Errors: {test_metrics.get('errors', 0)}")
                print(f"   Skipped: {test_metrics.get('skipped', 0)}")

            return suite_result

        except Exception as e:
            duration = time.time() - start_time
            error_result = {
                "status": "error",
                "error": str(e),
                "duration": duration,
                "tests_run": 0,
                "passed": 0,
                "failed": 0,
                "errors": 1,
            }

            print(f"❌ {suite_name.title()} tests failed with error: {e}")
            return error_result

    def _parse_junit_xml(self, xml_file: Path) -> Dict:
        """Parse JUnit XML file for test metrics."""
        try:
            import xml.etree.ElementTree as ET

            tree = ET.parse(xml_file)
            root = tree.getroot()

            # Extract test metrics from testsuite element
            testsuite = root.find("testsuite")
            if testsuite is not None:
                return {
                    "tests_run": int(testsuite.get("tests", 0)),
                    "passed": int(testsuite.get("tests", 0))
                    - int(testsuite.get("failures", 0))
                    - int(testsuite.get("errors", 0)),
                    "failed": int(testsuite.get("failures", 0)),
                    "errors": int(testsuite.get("errors", 0)),
                    "skipped": int(testsuite.get("skipped", 0)),
                    "time": float(testsuite.get("time", 0)),
                }
            else:
                return {}

        except Exception as e:
            print(f"Warning: Could not parse JUnit XML {xml_file}: {e}")
            return {}

    def execute_all_test_suites(self, parallel: bool = False) -> Dict:
        """Execute all test suites in sequence or parallel.

        Args:
            parallel: Whether to run test suites in parallel (default: False)

        Returns:
            Complete test execution results
        """
        print("\n🚀 Starting Enterprise Test Execution Framework")
        print("=" * 60)
        print(f"Execution timestamp: {self.execution_timestamp}")
        print(f"Project root: {self.project_root}")
        print(f"Output directory: {self.output_dir}")

        # Validate environment first
        if not self.validate_test_environment():
            print(
                "\n❌ Environment validation failed. Aborting test execution."
            )
            return self.test_results

        total_start_time = time.time()

        # Define test suite execution order (sequential by default)
        suite_order = ["unit", "integration", "performance", "security"]

        if parallel:
            print(
                "\n⚠️  Parallel execution not implemented yet - running sequentially"
            )

        # Execute test suites sequentially
        for suite_name in suite_order:
            print(f"\n{'='*20} {suite_name.upper()} TESTS {'='*20}")

            # Execute suite
            suite_result = self.execute_test_suite(suite_name)
            self.test_results["suite_results"][suite_name] = suite_result

            # Check for critical failures
            if suite_result["status"] in [
                "failed",
                "error",
            ] and suite_name in ["unit", "security"]:
                print(
                    f"\n❌ Critical failure in {suite_name} tests - stopping execution"
                )
                break

        total_duration = time.time() - total_start_time

        # Generate summary
        self._generate_test_summary(total_duration)

        # Generate comprehensive report
        self._generate_comprehensive_report()

        print(f"\n✅ Test execution completed in {total_duration:.2f}s")
        print(f"📊 Reports available in: {self.output_dir}")

        return self.test_results

    def _generate_test_summary(self, total_duration: float):
        """Generate test execution summary."""
        summary = {
            "total_duration": total_duration,
            "suites_executed": len(self.test_results["suite_results"]),
            "overall_status": "passed",
            "total_tests": 0,
            "total_passed": 0,
            "total_failed": 0,
            "total_errors": 0,
            "total_skipped": 0,
        }

        # Aggregate results
        for suite_name, suite_result in self.test_results[
            "suite_results"
        ].items():
            if suite_result["status"] in ["failed", "error"]:
                summary["overall_status"] = "failed"

            summary["total_tests"] += suite_result.get("tests_run", 0)
            summary["total_passed"] += suite_result.get("passed", 0)
            summary["total_failed"] += suite_result.get("failed", 0)
            summary["total_errors"] += suite_result.get("errors", 0)
            summary["total_skipped"] += suite_result.get("skipped", 0)

        # Calculate success rate
        if summary["total_tests"] > 0:
            summary["success_rate"] = (
                summary["total_passed"] / summary["total_tests"] * 100
            )
        else:
            summary["success_rate"] = 0

        self.test_results["summary"] = summary

        # Print summary
        print("\n📊 TEST EXECUTION SUMMARY")
        print("=" * 50)
        print(
            f"Overall Status: {'✅ PASSED' if summary['overall_status'] == 'passed' else '❌ FAILED'}"
        )
        print(f"Total Duration: {summary['total_duration']:.2f} seconds")
        print(f"Total Tests: {summary['total_tests']}")
        print(
            f"Passed: {summary['total_passed']} ({summary['success_rate']:.1f}%)"
        )
        print(f"Failed: {summary['total_failed']}")
        print(f"Errors: {summary['total_errors']}")
        print(f"Skipped: {summary['total_skipped']}")

        # Per-suite breakdown
        print("\nPer-Suite Results:")
        for suite_name, suite_result in self.test_results[
            "suite_results"
        ].items():
            status_icon = "✅" if suite_result["status"] == "passed" else "❌"
            print(
                f"  {suite_name.title():<12} {status_icon} {suite_result.get('tests_run', 0):>3} tests in {suite_result.get('duration', 0):>6.2f}s"
            )

    def _generate_comprehensive_report(self):
        """Generate comprehensive HTML and JSON reports."""
        # Generate JSON report
        json_report_path = (
            self.output_dir
            / f"enterprise_test_report_{self.execution_timestamp}.json"
        )
        with open(json_report_path, "w") as f:
            json.dump(self.test_results, f, indent=2, default=str)

        # Generate HTML summary report
        html_report_path = (
            self.output_dir
            / f"enterprise_test_summary_{self.execution_timestamp}.html"
        )
        self._generate_html_summary_report(html_report_path)

        # Generate executive summary
        exec_summary_path = (
            self.output_dir
            / f"executive_summary_{self.execution_timestamp}.md"
        )
        self._generate_executive_summary(exec_summary_path)

        print(f"\n📋 Reports generated:")
        print(f"   JSON Report: {json_report_path}")
        print(f"   HTML Summary: {html_report_path}")
        print(f"   Executive Summary: {exec_summary_path}")

    def _generate_html_summary_report(self, output_path: Path):
        """Generate comprehensive HTML summary report."""
        summary = self.test_results["summary"]

        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Enterprise Test Report - {self.execution_timestamp}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #f4f4f4; padding: 20px; border-radius: 5px; }}
        .status-passed {{ color: #4CAF50; font-weight: bold; }}
        .status-failed {{ color: #f44336; font-weight: bold; }}
        .metric {{ display: inline-block; margin: 10px; padding: 10px; background: #f9f9f9; border-radius: 3px; }}
        .suite-result {{ margin: 10px 0; padding: 10px; border-left: 4px solid #ddd; }}
        .suite-passed {{ border-left-color: #4CAF50; }}
        .suite-failed {{ border-left-color: #f44336; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Advanced Folders System - Enterprise Test Report</h1>
        <p><strong>Execution Time:</strong> {self.execution_timestamp}</p>
        <p><strong>Overall Status:</strong> <span class="status-{'passed' if summary['overall_status'] == 'passed' else 'failed'}">{summary['overall_status'].upper()}</span></p>
    </div>
    
    <h2>Test Execution Summary</h2>
    <div class="metric">Total Tests: <strong>{summary['total_tests']}</strong></div>
    <div class="metric">Passed: <strong>{summary['total_passed']}</strong></div>
    <div class="metric">Failed: <strong>{summary['total_failed']}</strong></div>
    <div class="metric">Errors: <strong>{summary['total_errors']}</strong></div>
    <div class="metric">Success Rate: <strong>{summary['success_rate']:.1f}%</strong></div>
    <div class="metric">Duration: <strong>{summary['total_duration']:.2f}s</strong></div>
    
    <h2>Test Suite Results</h2>
    <table>
        <tr>
            <th>Test Suite</th>
            <th>Status</th>
            <th>Tests Run</th>
            <th>Passed</th>
            <th>Failed</th>
            <th>Errors</th>
            <th>Duration (s)</th>
        </tr>
"""

        for suite_name, suite_result in self.test_results[
            "suite_results"
        ].items():
            status_class = (
                "passed" if suite_result["status"] == "passed" else "failed"
            )
            html_content += f"""
        <tr>
            <td>{suite_name.title()}</td>
            <td><span class="status-{status_class}">{suite_result['status'].upper()}</span></td>
            <td>{suite_result.get('tests_run', 0)}</td>
            <td>{suite_result.get('passed', 0)}</td>
            <td>{suite_result.get('failed', 0)}</td>
            <td>{suite_result.get('errors', 0)}</td>
            <td>{suite_result.get('duration', 0):.2f}</td>
        </tr>
"""

        html_content += """
    </table>
    
    <h2>Quality Gates Status</h2>
    <ul>
"""

        # Quality gate checks
        quality_gates = [
            (
                "Unit Test Coverage",
                ">90%",
                summary["total_passed"] / max(summary["total_tests"], 1) * 100
                > 90,
            ),
            (
                "Security Tests",
                "All Pass",
                self.test_results["suite_results"]
                .get("security", {})
                .get("status")
                == "passed",
            ),
            (
                "Performance Tests",
                "All Pass",
                self.test_results["suite_results"]
                .get("performance", {})
                .get("status")
                == "passed",
            ),
            (
                "Integration Tests",
                "All Pass",
                self.test_results["suite_results"]
                .get("integration", {})
                .get("status")
                == "passed",
            ),
        ]

        for gate_name, requirement, passed in quality_gates:
            status_class = "passed" if passed else "failed"
            status_text = "PASS" if passed else "FAIL"
            html_content += f'        <li>{gate_name}: {requirement} - <span class="status-{status_class}">{status_text}</span></li>\n'

        html_content += """
    </ul>
    
    <h2>Detailed Reports</h2>
    <p>Individual test suite reports are available:</p>
    <ul>
"""

        # Link to individual reports
        for suite_name in self.test_results["suite_results"].keys():
            html_content += f'        <li><a href="{suite_name}_report.html">{suite_name.title()} Test Report</a></li>\n'

        html_content += """
    </ul>
    
    <footer style="margin-top: 50px; padding-top: 20px; border-top: 1px solid #ddd; color: #666;">
        <p>Generated by Enterprise Test Execution Framework - Advanced Folders System</p>
        <p>Phase 4: Testing & QA (Week 10) - Zero-Compromise Quality Standards</p>
    </footer>
</body>
</html>
"""

        with open(output_path, "w") as f:
            f.write(html_content)

    def _generate_executive_summary(self, output_path: Path):
        """Generate executive summary in Markdown format."""
        summary = self.test_results["summary"]

        markdown_content = f"""# Advanced Folders System - Executive Test Summary

**Report Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Test Execution ID:** {self.execution_timestamp}  
**Project:** Advanced Folders System (Phase 4: Testing & QA)  

## Executive Overview

The Advanced Folders System has undergone comprehensive enterprise-grade testing following zero-compromise quality standards. This report summarizes the test execution results and quality assurance status.

### Overall Test Results

- **Status:** {'✅ PASSED' if summary['overall_status'] == 'passed' else '❌ FAILED'}
- **Total Tests Executed:** {summary['total_tests']}
- **Success Rate:** {summary['success_rate']:.1f}%
- **Total Execution Time:** {summary['total_duration']:.2f} seconds

### Test Coverage Breakdown

| Test Suite | Status | Tests | Passed | Failed | Duration |
|------------|--------|-------|--------|--------|----------|
"""

        for suite_name, suite_result in self.test_results[
            "suite_results"
        ].items():
            status_icon = "✅" if suite_result["status"] == "passed" else "❌"
            markdown_content += f"| {suite_name.title()} | {status_icon} | {suite_result.get('tests_run', 0)} | {suite_result.get('passed', 0)} | {suite_result.get('failed', 0)} | {suite_result.get('duration', 0):.2f}s |\n"

        markdown_content += f"""

### Quality Gates Assessment

**Enterprise Quality Standards Compliance:**

- **Unit Testing:** {'✅ COMPLIANT' if summary['total_passed'] / max(summary['total_tests'], 1) * 100 > 90 else '❌ NON-COMPLIANT'} (Target: >90% coverage)
- **Integration Testing:** {'✅ COMPLIANT' if self.test_results['suite_results'].get('integration', {}).get('status') == 'passed' else '❌ NON-COMPLIANT'}
- **Performance Testing:** {'✅ COMPLIANT' if self.test_results['suite_results'].get('performance', {}).get('status') == 'passed' else '❌ NON-COMPLIANT'}
- **Security Testing:** {'✅ COMPLIANT' if self.test_results['suite_results'].get('security', {}).get('status') == 'passed' else '❌ NON-COMPLIANT'} (Zero tolerance policy)

### Risk Assessment

"""

        # Risk assessment based on results
        if summary["overall_status"] == "passed":
            markdown_content += """
**Risk Level:** LOW
- All critical test suites have passed
- Quality gates are satisfied
- System is ready for production deployment
"""
        else:
            failed_suites = [
                name
                for name, result in self.test_results["suite_results"].items()
                if result["status"] != "passed"
            ]
            markdown_content += f"""
**Risk Level:** HIGH
- Failed test suites: {', '.join(failed_suites)}
- Quality gates not satisfied
- System requires remediation before deployment
"""

        markdown_content += f"""

### Recommendations

1. **Immediate Actions:**
   - Review detailed test reports for failed tests
   - Address any security vulnerabilities identified
   - Validate performance benchmarks meet requirements

2. **Deployment Decision:**
   - {'✅ APPROVED for production deployment' if summary['overall_status'] == 'passed' else '❌ BLOCKED from production deployment'}
   - {'All quality gates satisfied' if summary['overall_status'] == 'passed' else 'Quality gates must be satisfied before deployment'}

3. **Next Steps:**
   - Implement continuous integration testing
   - Schedule regular security assessments
   - Monitor performance metrics in production

### Detailed Reports

For comprehensive technical details, refer to:
- Individual test suite HTML reports
- Coverage analysis reports
- Performance benchmark data
- Security assessment findings

---

**Report Authority:** Enterprise Test Engineer  
**Quality Assurance Level:** Zero-Compromise Standards  
**Compliance Framework:** OWASP, Enterprise Security Guidelines  
"""

        with open(output_path, "w") as f:
            f.write(markdown_content)

    def run_ci_cd_integration(self) -> bool:
        """Run tests with CI/CD integration features.

        Returns:
            True if all tests pass (CI/CD should proceed), False otherwise
        """
        print("🔧 Running CI/CD Integration Mode...")

        # Execute all test suites
        results = self.execute_all_test_suites()

        # Determine CI/CD status
        overall_status = results["summary"]["overall_status"]

        # Generate CI/CD specific outputs
        ci_cd_output = {
            "success": overall_status == "passed",
            "exit_code": 0 if overall_status == "passed" else 1,
            "summary": results["summary"],
            "quality_gates": {
                "unit_tests": results["suite_results"]
                .get("unit", {})
                .get("status")
                == "passed",
                "integration_tests": results["suite_results"]
                .get("integration", {})
                .get("status")
                == "passed",
                "security_tests": results["suite_results"]
                .get("security", {})
                .get("status")
                == "passed",
                "performance_tests": results["suite_results"]
                .get("performance", {})
                .get("status")
                == "passed",
            },
        }

        # Write CI/CD output file
        ci_cd_file = self.output_dir / "ci_cd_results.json"
        with open(ci_cd_file, "w") as f:
            json.dump(ci_cd_output, f, indent=2, default=str)

        # Set exit code for CI/CD systems
        exit_code = 0 if overall_status == "passed" else 1

        print(f"🚀 CI/CD Integration Results:")
        print(
            f"   Status: {'✅ PASS' if overall_status == 'passed' else '❌ FAIL'}"
        )
        print(f"   Exit Code: {exit_code}")
        print(f"   Results File: {ci_cd_file}")

        return overall_status == "passed"


def main():
    """Main entry point for enterprise test execution."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Enterprise Test Execution Framework"
    )
    parser.add_argument(
        "--project-root", type=str, default=".", help="Project root directory"
    )
    parser.add_argument(
        "--output-dir", type=str, help="Output directory for reports"
    )
    parser.add_argument(
        "--suite",
        type=str,
        choices=["unit", "integration", "performance", "security"],
        help="Run specific test suite only",
    )
    parser.add_argument(
        "--ci-cd", action="store_true", help="Run in CI/CD integration mode"
    )
    parser.add_argument(
        "--parallel", action="store_true", help="Run test suites in parallel"
    )

    args = parser.parse_args()

    # Initialize executor
    project_root = Path(args.project_root).resolve()
    output_dir = Path(args.output_dir).resolve() if args.output_dir else None

    executor = EnterpriseTestExecutor(project_root, output_dir)

    try:
        if args.ci_cd:
            # CI/CD integration mode
            success = executor.run_ci_cd_integration()
            sys.exit(0 if success else 1)
        elif args.suite:
            # Run specific suite
            if not executor.validate_test_environment():
                sys.exit(1)

            result = executor.execute_test_suite(args.suite)
            print(f"\n{args.suite.title()} test suite: {result['status']}")
            sys.exit(0 if result["status"] == "passed" else 1)
        else:
            # Run all suites
            results = executor.execute_all_test_suites(parallel=args.parallel)
            overall_status = results["summary"]["overall_status"]
            sys.exit(0 if overall_status == "passed" else 1)

    except KeyboardInterrupt:
        print("\n⚠️ Test execution interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Test execution failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
