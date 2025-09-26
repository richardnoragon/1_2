#!/usr/bin/env python3
"""
Test Runner for platform_utils.py comprehensive testing
Generated on: 2025-08-30

This script runs comprehensive unit tests for platform_utils.py using pytest framework
with detailed HTML and JSON reporting, coverage analysis, and standardized output.
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


class PlatformUtilsTestRunner:
    """Test runner for platform_utils.py with comprehensive reporting."""
    
    def __init__(self):
        self.test_date = "2025-08-30"
        self.base_dir = Path("C:/Users/richardi/1_2/tests/unit")
        self.test_file = self.base_dir / f"test_platform_utils_{self.test_date}.py"
        self.config_file = self.base_dir / f"pytest_platform_utils_{self.test_date}.ini"
        self.results_prefix = f"result_platform_utils_{self.test_date}"
        
        # Ensure base directory exists
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Result file paths
        self.html_report = self.base_dir / f"{self.results_prefix}.html"
        self.json_report = self.base_dir / f"{self.results_prefix}.json"
        self.coverage_html_dir = self.base_dir / f"{self.results_prefix}_coverage"
        self.coverage_json = self.base_dir / f"{self.results_prefix}_coverage.json"
        self.summary_report = self.base_dir / f"{self.results_prefix}_summary.json"
    
    def check_dependencies(self) -> bool:
        """Check if all required dependencies are installed."""
        required_packages = [
            'pytest',
            'pytest-html',
            'pytest-json-report',
            'pytest-cov',
            'pytest-timeout'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            print(f"Missing required packages: {', '.join(missing_packages)}")
            print("Installing missing packages...")
            
            for package in missing_packages:
                try:
                    subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                    print(f"✓ Installed {package}")
                except subprocess.CalledProcessError as e:
                    print(f"✗ Failed to install {package}: {e}")
                    return False
        
        return True
    
    def run_tests(self) -> Dict[str, Any]:
        """Run the comprehensive test suite."""
        print(f"Starting comprehensive test execution at {datetime.now()}")
        print(f"Test file: {self.test_file}")
        print(f"Configuration: {self.config_file}")
        print("-" * 80)
        
        start_time = time.time()
        
        # Build pytest command
        cmd = [
            sys.executable, '-m', 'pytest',
            str(self.test_file),
            '-c', str(self.config_file),
            '--verbose',
            '--tb=short',
            '--html', str(self.html_report),
            '--self-contained-html',
            '--json-report',
            '--json-report-file', str(self.json_report),
            '--cov=src.utilities.privacy.privacy_tools.core.platform_utils',
            '--cov-report=html:' + str(self.coverage_html_dir),
            '--cov-report=term-missing',
            '--cov-report=json:' + str(self.coverage_json),
            '--durations=10'
        ]
        
        # Execute tests
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=Path("C:/Users/richardi/1_2"),
                timeout=300
            )
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Prepare results summary
            test_results = {
                'execution_info': {
                    'timestamp': datetime.now().isoformat(),
                    'test_date': self.test_date,
                    'execution_time_seconds': round(execution_time, 2),
                    'exit_code': result.returncode,
                    'success': result.returncode == 0
                },
                'command': ' '.join(cmd),
                'stdout': result.stdout,
                'stderr': result.stderr,
                'files_generated': {
                    'html_report': str(self.html_report),
                    'json_report': str(self.json_report),
                    'coverage_html': str(self.coverage_html_dir),
                    'coverage_json': str(self.coverage_json),
                    'summary_report': str(self.summary_report)
                }
            }
            
            # Parse JSON report if available
            if self.json_report.exists():
                try:
                    with open(self.json_report, 'r') as f:
                        json_data = json.load(f)
                        test_results['test_summary'] = {
                            'total_tests': json_data.get('summary', {}).get('total', 0),
                            'passed': json_data.get('summary', {}).get('passed', 0),
                            'failed': json_data.get('summary', {}).get('failed', 0),
                            'errors': json_data.get('summary', {}).get('error', 0),
                            'skipped': json_data.get('summary', {}).get('skipped', 0),
                            'duration': json_data.get('duration', 0)
                        }
                except Exception as e:
                    test_results['json_parse_error'] = str(e)
            
            # Parse coverage report if available
            if self.coverage_json.exists():
                try:
                    with open(self.coverage_json, 'r') as f:
                        coverage_data = json.load(f)
                        test_results['coverage_summary'] = {
                            'total_statements': coverage_data.get('totals', {}).get('num_statements', 0),
                            'missing_statements': coverage_data.get('totals', {}).get('missing_lines', 0),
                            'coverage_percent': coverage_data.get('totals', {}).get('percent_covered', 0),
                            'covered_lines': coverage_data.get('totals', {}).get('covered_lines', 0)
                        }
                except Exception as e:
                    test_results['coverage_parse_error'] = str(e)
            
            return test_results
            
        except subprocess.TimeoutExpired:
            return {
                'execution_info': {
                    'timestamp': datetime.now().isoformat(),
                    'test_date': self.test_date,
                    'execution_time_seconds': 300,
                    'exit_code': -1,
                    'success': False
                },
                'error': 'Test execution timed out after 300 seconds'
            }
        except Exception as e:
            return {
                'execution_info': {
                    'timestamp': datetime.now().isoformat(),
                    'test_date': self.test_date,
                    'execution_time_seconds': 0,
                    'exit_code': -1,
                    'success': False
                },
                'error': f'Test execution failed: {str(e)}'
            }
    
    def generate_summary_report(self, test_results: Dict[str, Any]) -> None:
        """Generate a comprehensive summary report."""
        summary = {
            'test_execution_summary': {
                'platform_utils_test_date': self.test_date,
                'execution_timestamp': test_results['execution_info']['timestamp'],
                'total_execution_time': f"{test_results['execution_info']['execution_time_seconds']} seconds",
                'overall_success': test_results['execution_info']['success'],
                'exit_code': test_results['execution_info']['exit_code']
            }
        }
        
        # Add test results if available
        if 'test_summary' in test_results:
            summary['test_results'] = test_results['test_summary']
            summary['test_results']['pass_rate'] = (
                test_results['test_summary']['passed'] / 
                max(test_results['test_summary']['total_tests'], 1) * 100
            )
        
        # Add coverage results if available
        if 'coverage_summary' in test_results:
            summary['coverage_analysis'] = test_results['coverage_summary']
        
        # Add file locations
        summary['generated_files'] = test_results.get('files_generated', {})
        
        # Add any errors
        if 'error' in test_results:
            summary['execution_error'] = test_results['error']
        
        if 'json_parse_error' in test_results:
            summary['json_parse_error'] = test_results['json_parse_error']
        
        if 'coverage_parse_error' in test_results:
            summary['coverage_parse_error'] = test_results['coverage_parse_error']
        
        # Save summary report
        with open(self.summary_report, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        print(f"\n{'='*80}")
        print("TEST EXECUTION SUMMARY")
        print(f"{'='*80}")
        print(f"Date: {self.test_date}")
        print(f"Timestamp: {summary['test_execution_summary']['execution_timestamp']}")
        print(f"Execution Time: {summary['test_execution_summary']['total_execution_time']}")
        print(f"Overall Success: {summary['test_execution_summary']['overall_success']}")
        
        if 'test_results' in summary:
            print(f"\nTest Results:")
            print(f"  Total Tests: {summary['test_results']['total_tests']}")
            print(f"  Passed: {summary['test_results']['passed']}")
            print(f"  Failed: {summary['test_results']['failed']}")
            print(f"  Errors: {summary['test_results']['errors']}")
            print(f"  Skipped: {summary['test_results']['skipped']}")
            print(f"  Pass Rate: {summary['test_results']['pass_rate']:.1f}%")
        
        if 'coverage_analysis' in summary:
            print(f"\nCoverage Analysis:")
            print(f"  Coverage: {summary['coverage_analysis']['coverage_percent']:.1f}%")
            print(f"  Total Statements: {summary['coverage_analysis']['total_statements']}")
            print(f"  Covered Lines: {summary['coverage_analysis']['covered_lines']}")
            print(f"  Missing Statements: {summary['coverage_analysis']['missing_statements']}")
        
        print(f"\nGenerated Reports:")
        for report_type, file_path in summary['generated_files'].items():
            exists = "✓" if Path(file_path).exists() else "✗"
            print(f"  {exists} {report_type}: {file_path}")
        
        print(f"\n{'='*80}")
    
    def run(self) -> bool:
        """Run the complete test suite with reporting."""
        print("Platform Utils Comprehensive Test Runner")
        print(f"Generated on: {self.test_date}")
        print(f"Target: platform_utils.py")
        print("="*80)
        
        # Check dependencies
        if not self.check_dependencies():
            print("❌ Dependency check failed. Cannot proceed with testing.")
            return False
        
        print("✓ All dependencies are available")
        
        # Verify test files exist
        if not self.test_file.exists():
            print(f"❌ Test file not found: {self.test_file}")
            return False
        
        if not self.config_file.exists():
            print(f"❌ Configuration file not found: {self.config_file}")
            return False
        
        print("✓ Test files are ready")
        
        # Run tests
        test_results = self.run_tests()
        
        # Generate summary
        self.generate_summary_report(test_results)
        
        return test_results['execution_info']['success']


def main():
    """Main entry point for the test runner."""
    runner = PlatformUtilsTestRunner()
    success = runner.run()
    
    if success:
        print("\n🎉 All tests completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed or there were errors.")
        sys.exit(1)


if __name__ == "__main__":
    main()