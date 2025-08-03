"""Custom test runner for network connectivity tests."""

import sys
import os
import time
import subprocess
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional
import json


class NetworkConnectivityTestRunner:
    """Custom test runner for network connectivity tests."""
    
    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.project_root = self.test_dir.parent
        self.results = {}
        
    def run_unit_tests(self, verbose: bool = False) -> Dict[str, Any]:
        """Run unit tests."""
        print("Running unit tests...")
        cmd = [
            sys.executable, "-m", "pytest",
            str(self.test_dir / "unit"),
            "-v" if verbose else "-q",
            "--tb=short",
            "--markers=unit"
        ]
        
        result = self._run_pytest_command(cmd, "unit_tests")
        return result
    
    def run_integration_tests(self, verbose: bool = False) -> Dict[str, Any]:
        """Run integration tests."""
        print("Running integration tests...")
        cmd = [
            sys.executable, "-m", "pytest",
            str(self.test_dir / "integration"),
            "-v" if verbose else "-q",
            "--tb=short",
            "--markers=integration"
        ]
        
        result = self._run_pytest_command(cmd, "integration_tests")
        return result
    
    def run_gui_tests(self, verbose: bool = False) -> Dict[str, Any]:
        """Run GUI tests."""
        print("Running GUI tests...")
        cmd = [
            sys.executable, "-m", "pytest",
            str(self.test_dir / "gui"),
            "-v" if verbose else "-q",
            "--tb=short",
            "--markers=gui"
        ]
        
        result = self._run_pytest_command(cmd, "gui_tests")
        return result
    
    def run_performance_tests(self, verbose: bool = False) -> Dict[str, Any]:
        """Run performance tests."""
        print("Running performance tests...")
        cmd = [
            sys.executable, "-m", "pytest",
            str(self.test_dir / "performance"),
            "-v" if verbose else "-q",
            "--tb=short",
            "--markers=performance"
        ]
        
        result = self._run_pytest_command(cmd, "performance_tests")
        return result
    
    def run_stress_tests(self, verbose: bool = False) -> Dict[str, Any]:
        """Run stress tests."""
        print("Running stress tests...")
        cmd = [
            sys.executable, "-m", "pytest",
            str(self.test_dir / "performance"),
            "-v" if verbose else "-q",
            "--tb=short",
            "--markers=stress"
        ]
        
        result = self._run_pytest_command(cmd, "stress_tests")
        return result
    
    def run_all_tests(self, verbose: bool = False, 
                     include_stress: bool = False) -> Dict[str, Any]:
        """Run all tests."""
        print("Running all network connectivity tests...")
        
        results = {}
        
        # Run test suites in order
        results["unit"] = self.run_unit_tests(verbose)
        results["integration"] = self.run_integration_tests(verbose)
        results["gui"] = self.run_gui_tests(verbose)
        results["performance"] = self.run_performance_tests(verbose)
        
        if include_stress:
            results["stress"] = self.run_stress_tests(verbose)
        
        # Generate summary
        results["summary"] = self._generate_summary(results)
        
        return results
    
    def run_coverage_analysis(self) -> Dict[str, Any]:
        """Run tests with coverage analysis."""
        print("Running coverage analysis...")
        
        cmd = [
            sys.executable, "-m", "pytest",
            str(self.test_dir),
            "--cov=" + str(self.project_root),
            "--cov-report=html",
            "--cov-report=term",
            "--cov-report=json",
            "--cov-config=" + str(self.test_dir / ".coveragerc")
        ]
        
        result = self._run_pytest_command(cmd, "coverage")
        
        # Parse coverage results
        coverage_file = self.project_root / "coverage.json"
        if coverage_file.exists():
            with open(coverage_file) as f:
                coverage_data = json.load(f)
                result["coverage_data"] = coverage_data
        
        return result
    
    def run_specific_test(self, test_path: str, 
                         verbose: bool = False) -> Dict[str, Any]:
        """Run a specific test file or test function."""
        print(f"Running specific test: {test_path}")
        
        cmd = [
            sys.executable, "-m", "pytest",
            test_path,
            "-v" if verbose else "-q",
            "--tb=short"
        ]
        
        result = self._run_pytest_command(cmd, "specific_test")
        return result
    
    def _run_pytest_command(self, cmd: List[str], 
                           test_type: str) -> Dict[str, Any]:
        """Run a pytest command and capture results."""
        start_time = time.time()
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(self.project_root)
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            return {
                "test_type": test_type,
                "success": result.returncode == 0,
                "return_code": result.returncode,
                "duration": duration,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "command": " ".join(cmd)
            }
            
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            
            return {
                "test_type": test_type,
                "success": False,
                "return_code": -1,
                "duration": duration,
                "stdout": "",
                "stderr": str(e),
                "command": " ".join(cmd),
                "error": str(e)
            }
    
    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate test summary."""
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        total_duration = 0
        
        for test_type, result in results.items():
            if test_type == "summary":
                continue
                
            if isinstance(result, dict) and "success" in result:
                total_duration += result.get("duration", 0)
                
                # Parse stdout for test counts (basic parsing)
                stdout = result.get("stdout", "")
                if "passed" in stdout or "failed" in stdout:
                    # This is a simplified parser - in practice you'd want
                    # more robust parsing of pytest output
                    if result["success"]:
                        passed_tests += 1
                    else:
                        failed_tests += 1
                    total_tests += 1
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "total_duration": total_duration,
            "overall_success": failed_tests == 0
        }
    
    def generate_report(self, results: Dict[str, Any], 
                       output_file: Optional[str] = None) -> str:
        """Generate a test report."""
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("NETWORK CONNECTIVITY TEST REPORT")
        report_lines.append("=" * 60)
        report_lines.append("")
        
        # Summary
        if "summary" in results:
            summary = results["summary"]
            report_lines.append("SUMMARY:")
            report_lines.append(f"  Total Tests: {summary['total_tests']}")
            report_lines.append(f"  Passed: {summary['passed_tests']}")
            report_lines.append(f"  Failed: {summary['failed_tests']}")
            report_lines.append(f"  Success Rate: {summary['success_rate']:.1f}%")
            report_lines.append(f"  Total Duration: {summary['total_duration']:.2f}s")
            report_lines.append(f"  Overall Success: {summary['overall_success']}")
            report_lines.append("")
        
        # Individual test results
        for test_type, result in results.items():
            if test_type == "summary":
                continue
                
            report_lines.append(f"{test_type.upper()} TESTS:")
            report_lines.append(f"  Success: {result.get('success', False)}")
            report_lines.append(f"  Duration: {result.get('duration', 0):.2f}s")
            report_lines.append(f"  Return Code: {result.get('return_code', 'N/A')}")
            
            if not result.get('success', False):
                stderr = result.get('stderr', '')
                if stderr:
                    report_lines.append(f"  Error Output:")
                    for line in stderr.split('\n')[:10]:  # First 10 lines
                        report_lines.append(f"    {line}")
            
            report_lines.append("")
        
        report_lines.append("=" * 60)
        
        report_text = "\n".join(report_lines)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report_text)
            print(f"Report saved to: {output_file}")
        
        return report_text


def main():
    """Main entry point for test runner."""
    parser = argparse.ArgumentParser(
        description="Network Connectivity Test Runner"
    )
    
    parser.add_argument(
        "--test-type",
        choices=["unit", "integration", "gui", "performance", "stress", "all"],
        default="all",
        help="Type of tests to run"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Run with coverage analysis"
    )
    
    parser.add_argument(
        "--include-stress",
        action="store_true",
        help="Include stress tests (when running all tests)"
    )
    
    parser.add_argument(
        "--specific-test",
        help="Run a specific test file or function"
    )
    
    parser.add_argument(
        "--report-file",
        help="Save test report to file"
    )
    
    args = parser.parse_args()
    
    runner = NetworkConnectivityTestRunner()
    
    # Run tests based on arguments
    if args.coverage:
        results = runner.run_coverage_analysis()
    elif args.specific_test:
        results = runner.run_specific_test(args.specific_test, args.verbose)
    elif args.test_type == "unit":
        results = runner.run_unit_tests(args.verbose)
    elif args.test_type == "integration":
        results = runner.run_integration_tests(args.verbose)
    elif args.test_type == "gui":
        results = runner.run_gui_tests(args.verbose)
    elif args.test_type == "performance":
        results = runner.run_performance_tests(args.verbose)
    elif args.test_type == "stress":
        results = runner.run_stress_tests(args.verbose)
    elif args.test_type == "all":
        results = runner.run_all_tests(args.verbose, args.include_stress)
    
    # Generate and display report
    report = runner.generate_report(results, args.report_file)
    print(report)
    
    # Exit with appropriate code
    if isinstance(results, dict):
        if "summary" in results:
            sys.exit(0 if results["summary"]["overall_success"] else 1)
        else:
            sys.exit(0 if results.get("success", False) else 1)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()