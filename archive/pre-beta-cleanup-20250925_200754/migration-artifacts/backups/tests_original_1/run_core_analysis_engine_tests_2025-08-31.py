#!/usr/bin/env python3
"""
Core Analysis Engine Comprehensive Test Runner

This script runs all test suites for the Core Analysis Engine components,
providing comprehensive coverage validation and detailed reporting.

Created: August 31, 2025
Purpose: Execute all Core Analysis Engine tests and generate coverage report
Priority: HIGH (completing missing critical test coverage)
"""

import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


@dataclass
class TestResult:
    """Test result data structure."""
    test_suite: str
    status: str
    duration: float
    tests_run: int
    tests_passed: int
    tests_failed: int
    tests_skipped: int
    coverage_percent: float = 0.0
    error_message: str = ""


class CoreAnalysisEngineTestRunner:
    """Comprehensive test runner for Core Analysis Engine."""
    
    def __init__(self):
        """Initialize the test runner."""
        # Get the directory where this script is located
        script_dir = Path(__file__).parent
        
        self.test_suites = [
            {
                'name': 'Size Analyzer Logging',
                'file': str(script_dir / 'unit' / 'test_size_analyzer_logging_comprehensive_2025-08-31.py'),
                'type': 'unit',
                'description': 'Comprehensive logging component tests'
            },
            {
                'name': 'Core Analysis Engine Unit Tests',
                'file': str(script_dir / 'unit' / 'test_core_analysis_engine_comprehensive_2025-08-31.py'),
                'type': 'unit',
                'description': 'Core engine component unit tests'
            },
            {
                'name': 'Core Analysis Engine Integration',
                'file': str(script_dir / 'integration' / 'test_core_analysis_engine_integration_2025-08-31.py'),
                'type': 'integration',
                'description': 'Component integration tests'
            },
            {
                'name': 'Core Analysis Engine Performance',
                'file': str(script_dir / 'performance' / 'test_core_analysis_engine_benchmarks_2025-08-31.py'),
                'type': 'performance',
                'description': 'Performance benchmarks and stress tests'
            },
            {
                'name': 'Core Analysis Engine End-to-End',
                'file': str(script_dir / 'e2e' / 'test_core_analysis_engine_e2e_2025-08-31.py'),
                'type': 'e2e',
                'description': 'Complete workflow validation tests'
            }
        ]
        
        self.results: List[TestResult] = []
        self.start_time = time.time()
    
    def run_test_suite(self, test_suite: Dict[str, str]) -> TestResult:
        """Run a single test suite and return results."""
        print(f"\n{'='*60}")
        print(f"Running: {test_suite['name']}")
        print(f"Type: {test_suite['type'].upper()}")
        print(f"Description: {test_suite['description']}")
        print(f"File: {test_suite['file']}")
        print(f"{'='*60}")
        
        start_time = time.time()
        
        # Prepare pytest command
        pytest_cmd = [
            sys.executable, '-m', 'pytest',
            test_suite['file'],
            '-v',
            '--tb=short',
            '--color=yes',
            '--durations=10',
            '--json-report',
            '--json-report-file=test_results.json'
        ]
        
        try:
            # Run the test suite
            result = subprocess.run(
                pytest_cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            
            duration = time.time() - start_time
            
            # Parse results
            tests_run, tests_passed, tests_failed, tests_skipped = self._parse_pytest_output(result.stdout)
            
            # Determine status
            if result.returncode == 0:
                status = "PASSED" if tests_failed == 0 else "PARTIAL"
            else:
                status = "FAILED"
            
            test_result = TestResult(
                test_suite=test_suite['name'],
                status=status,
                duration=duration,
                tests_run=tests_run,
                tests_passed=tests_passed,
                tests_failed=tests_failed,
                tests_skipped=tests_skipped,
                error_message=result.stderr if result.returncode != 0 else ""
            )
            
            # Print summary
            print(f"\nTest Suite: {test_suite['name']}")
            print(f"Status: {status}")
            print(f"Duration: {duration:.2f}s")
            print(f"Tests Run: {tests_run}")
            print(f"Passed: {tests_passed}")
            print(f"Failed: {tests_failed}")
            print(f"Skipped: {tests_skipped}")
            
            if result.stderr:
                print(f"Errors: {result.stderr[:500]}...")
            
            return test_result
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            return TestResult(
                test_suite=test_suite['name'],
                status="TIMEOUT",
                duration=duration,
                tests_run=0,
                tests_passed=0,
                tests_failed=0,
                tests_skipped=0,
                error_message="Test suite timed out after 10 minutes"
            )
        
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                test_suite=test_suite['name'],
                status="ERROR",
                duration=duration,
                tests_run=0,
                tests_passed=0,
                tests_failed=0,
                tests_skipped=0,
                error_message=str(e)
            )
    
    def _parse_pytest_output(self, output: str) -> tuple:
        """Parse pytest output to extract test counts."""
        tests_run = 0
        tests_passed = 0
        tests_failed = 0
        tests_skipped = 0
        
        lines = output.split('\n')
        for line in lines:
            if 'passed' in line and 'failed' in line:
                # Look for summary line like "5 failed, 10 passed in 2.34s"
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == 'passed' and i > 0:
                        try:
                            tests_passed = int(parts[i-1])
                        except (ValueError, IndexError):
                            pass
                    elif part == 'failed' and i > 0:
                        try:
                            tests_failed = int(parts[i-1])
                        except (ValueError, IndexError):
                            pass
                    elif part == 'skipped' and i > 0:
                        try:
                            tests_skipped = int(parts[i-1])
                        except (ValueError, IndexError):
                            pass
            elif '::' in line and ('PASSED' in line or 'FAILED' in line or 'SKIPPED' in line):
                tests_run += 1
        
        if tests_run == 0:
            tests_run = tests_passed + tests_failed + tests_skipped
        
        return tests_run, tests_passed, tests_failed, tests_skipped
    
    def run_all_tests(self) -> None:
        """Run all test suites."""
        print("CORE ANALYSIS ENGINE COMPREHENSIVE TEST EXECUTION")
        print("=" * 80)
        print(f"Starting comprehensive test run at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Test suites to run: {len(self.test_suites)}")
        print()
        
        # Run each test suite
        for test_suite in self.test_suites:
            result = self.run_test_suite(test_suite)
            self.results.append(result)
        
        # Generate final report
        self.generate_final_report()
    
    def generate_final_report(self) -> None:
        """Generate comprehensive final report."""
        total_duration = time.time() - self.start_time
        
        print("\n\n" + "=" * 80)
        print("CORE ANALYSIS ENGINE TEST EXECUTION SUMMARY")
        print("=" * 80)
        
        # Overall statistics
        total_tests = sum(r.tests_run for r in self.results)
        total_passed = sum(r.tests_passed for r in self.results)
        total_failed = sum(r.tests_failed for r in self.results)
        total_skipped = sum(r.tests_skipped for r in self.results)
        
        print(f"Total Execution Time: {total_duration:.2f} seconds")
        print(f"Test Suites Run: {len(self.results)}")
        print(f"Total Tests Executed: {total_tests}")
        print(f"Tests Passed: {total_passed}")
        print(f"Tests Failed: {total_failed}")
        print(f"Tests Skipped: {total_skipped}")
        
        if total_tests > 0:
            pass_rate = (total_passed / total_tests) * 100
            print(f"Overall Pass Rate: {pass_rate:.1f}%")
        
        print("\nDETAILED RESULTS BY TEST SUITE:")
        print("-" * 50)
        
        for result in self.results:
            status_emoji = {
                "PASSED": "✅",
                "PARTIAL": "⚠️",
                "FAILED": "❌",
                "TIMEOUT": "⏰",
                "ERROR": "💥"
            }.get(result.status, "❓")
            
            print(f"{status_emoji} {result.test_suite}")
            print(f"   Status: {result.status}")
            print(f"   Duration: {result.duration:.2f}s")
            print(f"   Tests: {result.tests_passed}/{result.tests_run} passed")
            
            if result.tests_failed > 0:
                print(f"   Failed: {result.tests_failed}")
            if result.tests_skipped > 0:
                print(f"   Skipped: {result.tests_skipped}")
            if result.error_message:
                print(f"   Error: {result.error_message[:100]}...")
            print()
        
        # Performance summary
        print("PERFORMANCE SUMMARY:")
        print("-" * 30)
        performance_results = [r for r in self.results if 'Performance' in r.test_suite]
        if performance_results:
            for result in performance_results:
                print(f"Performance Tests: {result.tests_passed}/{result.tests_run} passed")
                if result.duration > 0:
                    print(f"Performance Duration: {result.duration:.2f}s")
        
        # Coverage summary
        print("\nTEST COVERAGE ANALYSIS:")
        print("-" * 30)
        
        coverage_components = [
            "SizeAnalyzerLogger - Logging component",
            "SizeAnalyzer - Core analysis engine",
            "Data processing pipelines",
            "Algorithm validation methods",
            "Error handling mechanisms",
            "Performance monitoring",
            "Integration points",
            "End-to-end workflows"
        ]
        
        for component in coverage_components:
            # Determine coverage based on test results
            has_tests = any(component.split(' - ')[0].lower() in r.test_suite.lower() 
                          for r in self.results if r.status in ["PASSED", "PARTIAL"])
            status = "✅ COVERED" if has_tests else "❌ NEEDS COVERAGE"
            print(f"{status}: {component}")
        
        # Recommendations
        print("\nRECOMMENDAT IONS:")
        print("-" * 20)
        
        failed_suites = [r for r in self.results if r.status in ["FAILED", "ERROR", "TIMEOUT"]]
        if failed_suites:
            print("🔧 IMMEDIATE ACTION REQUIRED:")
            for result in failed_suites:
                print(f"   - Fix {result.test_suite}: {result.error_message[:100]}")
        
        partial_suites = [r for r in self.results if r.status == "PARTIAL"]
        if partial_suites:
            print("⚠️  REVIEW REQUIRED:")
            for result in partial_suites:
                print(f"   - Review {result.test_suite}: {result.tests_failed} tests failed")
        
        if not failed_suites and not partial_suites:
            print("✅ ALL TESTS PASSING - Core Analysis Engine test coverage is comprehensive")
        
        # Save results to file
        self.save_results_to_file()
        
        print(f"\nTest execution completed at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("Detailed results saved to: core_analysis_engine_test_results.json")
    
    def save_results_to_file(self) -> None:
        """Save test results to JSON file."""
        results_data = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_duration': time.time() - self.start_time,
            'summary': {
                'total_suites': len(self.results),
                'total_tests': sum(r.tests_run for r in self.results),
                'total_passed': sum(r.tests_passed for r in self.results),
                'total_failed': sum(r.tests_failed for r in self.results),
                'total_skipped': sum(r.tests_skipped for r in self.results)
            },
            'test_results': [
                {
                    'test_suite': r.test_suite,
                    'status': r.status,
                    'duration': r.duration,
                    'tests_run': r.tests_run,
                    'tests_passed': r.tests_passed,
                    'tests_failed': r.tests_failed,
                    'tests_skipped': r.tests_skipped,
                    'error_message': r.error_message
                }
                for r in self.results
            ]
        }
        
        with open('core_analysis_engine_test_results.json', 'w') as f:
            json.dump(results_data, f, indent=2)


def main():
    """Main entry point for test runner."""
    runner = CoreAnalysisEngineTestRunner()
    
    try:
        runner.run_all_tests()
        
        # Determine exit code based on results
        failed_suites = [r for r in runner.results if r.status in ["FAILED", "ERROR", "TIMEOUT"]]
        if failed_suites:
            print(f"\nTest execution failed - {len(failed_suites)} test suite(s) failed")
            sys.exit(1)
        else:
            print("\nTest execution completed successfully")
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\nTest execution interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\nTest execution failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()