"""
Comprehensive Test Runner for size_analyzer_config.py

This script executes the comprehensive unit tests for size_analyzer_config.py
with detailed reporting, coverage analysis, and result generation.

Created: 2025-08-29
Author: GitHub Copilot
Framework: pytest
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


class TestRunner:
    """Comprehensive test runner with detailed reporting."""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.test_dir = Path(__file__).parent
        self.results_dir = self.test_dir / 'results'
        self.timestamp = self.start_time.strftime('%Y-%m-%d')
        
        # Ensure results directory exists
        self.results_dir.mkdir(exist_ok=True)
        
        # File paths
        self.test_file = self.test_dir / f'test_size_analyzer_config_comprehensive_{self.timestamp}.py'
        self.config_file = self.test_dir / f'pytest_size_analyzer_config_comprehensive_{self.timestamp}.ini'
        
        # Result files
        self.html_report = self.results_dir / f'result_size_analyzer_config_{self.timestamp}_report.html'
        self.json_report = self.results_dir / f'result_size_analyzer_config_{self.timestamp}.json'
        self.junit_report = self.results_dir / f'result_size_analyzer_config_{self.timestamp}_junit.xml'
        self.coverage_json = self.results_dir / f'result_size_analyzer_config_coverage_{self.timestamp}.json'
        self.coverage_html_dir = self.results_dir / f'result_size_analyzer_config_coverage_{self.timestamp}'
        self.execution_summary = self.results_dir / f'result_size_analyzer_config_execution_summary_{self.timestamp}.md'
        
    def install_dependencies(self):
        """Install required test dependencies."""
        print("Installing test dependencies...")
        
        dependencies = [
            'pytest>=7.0.0',
            'pytest-html>=3.1.0',
            'pytest-json-report>=1.5.0',
            'pytest-cov>=4.0.0',
            'pytest-mock>=3.10.0',
            'coverage>=7.0.0'
        ]
        
        for dep in dependencies:
            try:
                result = subprocess.run([sys.executable, '-m', 'pip', 'install', dep], 
                                      capture_output=True, text=True, timeout=120)
                if result.returncode == 0:
                    print(f"✓ Installed {dep}")
                else:
                    print(f"✗ Failed to install {dep}: {result.stderr}")
                    return False
            except subprocess.TimeoutExpired:
                print(f"✗ Timeout installing {dep}")
                return False
            except Exception as e:
                print(f"✗ Failed to install {dep}: {e}")
                return False
        
        print("Dependencies installed successfully!")
        return True
    
    def run_tests(self):
        """Execute the comprehensive test suite."""
        print(f"\nRunning comprehensive tests for size_analyzer_config.py...")
        print(f"Test file: {self.test_file}")
        print(f"Config file: {self.config_file}")
        print(f"Results directory: {self.results_dir}")
        
        # Build pytest command
        cmd = [
            sys.executable, '-m', 'pytest',
            str(self.test_file),
            f'-c={self.config_file}',
            '-v',
            '--tb=short',
            '--strict-markers',
            '--strict-config',
            f'--html={self.html_report}',
            '--self-contained-html',
            '--json-report',
            f'--json-report-file={self.json_report}',
            f'--junitxml={self.junit_report}',
            '--cov=src.utilities.analysis.config.size_analyzer_config',
            f'--cov-report=html:{self.coverage_html_dir}',
            f'--cov-report=json:{self.coverage_json}',
            '--cov-report=term-missing',
            '--cov-fail-under=75',
            '--durations=10',
            '--maxfail=10'
        ]
        
        print(f"\nExecuting command: {' '.join(cmd)}")
        
        try:
            # Run tests
            process = subprocess.run(cmd, 
                                   capture_output=True, 
                                   text=True, 
                                   cwd=self.test_dir,
                                   timeout=300)  # 5 minute timeout
            
            return process
            
        except subprocess.TimeoutExpired:
            print("✗ Test execution timed out after 5 minutes")
            return None
        except Exception as e:
            print(f"✗ Error running tests: {e}")
            return None
    
    def generate_execution_summary(self, process_result):
        """Generate comprehensive execution summary."""
        end_time = datetime.now()
        total_duration = (end_time - self.start_time).total_seconds()
        
        # Parse JSON report if available
        test_stats = {}
        if self.json_report.exists():
            try:
                with open(self.json_report, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                    summary = json_data.get('summary', {})
                    test_stats = {
                        'total': summary.get('total', 0),
                        'passed': summary.get('passed', 0),
                        'failed': summary.get('failed', 0),
                        'skipped': summary.get('skipped', 0),
                        'errors': summary.get('error', 0),
                        'duration': json_data.get('duration', 0)
                    }
            except Exception as e:
                print(f"Warning: Could not parse JSON report: {e}")
        
        # Parse coverage report if available
        coverage_stats = {}
        if self.coverage_json.exists():
            try:
                with open(self.coverage_json, 'r', encoding='utf-8') as f:
                    coverage_data = json.load(f)
                    totals = coverage_data.get('totals', {})
                    coverage_stats = {
                        'statements': totals.get('num_statements', 0),
                        'missing': totals.get('missing_lines', 0),
                        'excluded': totals.get('excluded_lines', 0),
                        'coverage_percent': totals.get('percent_covered', 0)
                    }
            except Exception as e:
                print(f"Warning: Could not parse coverage report: {e}")
        
        # Generate markdown summary
        summary_content = f"""# Size Analyzer Config Test Execution Summary
        
## Test Run Information
- **Execution Date**: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}
- **Completion Date**: {end_time.strftime('%Y-%m-%d %H:%M:%S')}
- **Total Duration**: {total_duration:.2f} seconds
- **Test File**: `{self.test_file.name}`
- **Python Version**: {sys.version}
- **Platform**: {sys.platform}

## Test Results
- **Total Tests**: {test_stats.get('total', 'N/A')}
- **Passed**: {test_stats.get('passed', 'N/A')}
- **Failed**: {test_stats.get('failed', 'N/A')}
- **Skipped**: {test_stats.get('skipped', 'N/A')}
- **Errors**: {test_stats.get('errors', 'N/A')}
- **Success Rate**: {(test_stats.get('passed', 0) / test_stats.get('total', 1) * 100):.1f}%

## Coverage Analysis
- **Total Statements**: {coverage_stats.get('statements', 'N/A')}
- **Missing Lines**: {coverage_stats.get('missing', 'N/A')}
- **Coverage Percentage**: {coverage_stats.get('coverage_percent', 'N/A'):.1f}%

## Generated Reports
- **HTML Report**: `{self.html_report.name}`
- **JSON Report**: `{self.json_report.name}`
- **JUnit XML**: `{self.junit_report.name}`
- **Coverage HTML**: `{self.coverage_html_dir.name}/`
- **Coverage JSON**: `{self.coverage_json.name}`

## Test Categories Covered
- ✓ Helper Functions (`get_config_manager`, `get_log_manager`)
- ✓ SizeAnalyzerConfig Initialization
- ✓ Core Configuration Management
- ✓ Settings Management (get/set operations)
- ✓ Recent Directories Management
- ✓ Window Geometry Management
- ✓ Resource Path Management
- ✓ Configuration Validation
- ✓ Import/Export Functionality
- ✓ Edge Cases and Error Handling
- ✓ Integration Scenarios

## Exit Code
**{process_result.returncode if process_result else 'N/A'}** ({('PASSED' if process_result and process_result.returncode == 0 else 'FAILED') if process_result else 'TIMEOUT'})

## Standard Output
```
{process_result.stdout if process_result else 'No output available'}
```

## Standard Error
```
{process_result.stderr if process_result else 'No error output available'}
```

---
*Generated by comprehensive test runner on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        # Write summary to file
        with open(self.execution_summary, 'w', encoding='utf-8') as f:
            f.write(summary_content)
        
        return summary_content
    
    def print_results_summary(self, process_result):
        """Print a summary of test results to console."""
        print("\n" + "="*80)
        print("TEST EXECUTION SUMMARY")
        print("="*80)
        
        if process_result:
            print(f"Exit Code: {process_result.returncode}")
            print(f"Status: {'PASSED' if process_result.returncode == 0 else 'FAILED'}")
        else:
            print("Status: TIMEOUT or ERROR")
        
        print(f"Duration: {(datetime.now() - self.start_time).total_seconds():.2f} seconds")
        
        # Print file locations
        print(f"\nGenerated Files:")
        print(f"  - HTML Report: {self.html_report}")
        print(f"  - JSON Report: {self.json_report}")
        print(f"  - JUnit XML: {self.junit_report}")
        print(f"  - Coverage HTML: {self.coverage_html_dir}/")
        print(f"  - Coverage JSON: {self.coverage_json}")
        print(f"  - Execution Summary: {self.execution_summary}")
        
        # Quick stats if JSON report exists
        if self.json_report.exists():
            try:
                with open(self.json_report, 'r') as f:
                    data = json.load(f)
                    summary = data.get('summary', {})
                    print(f"\nQuick Stats:")
                    print(f"  - Total Tests: {summary.get('total', 0)}")
                    print(f"  - Passed: {summary.get('passed', 0)}")
                    print(f"  - Failed: {summary.get('failed', 0)}")
                    if summary.get('total', 0) > 0:
                        success_rate = summary.get('passed', 0) / summary.get('total', 1) * 100
                        print(f"  - Success Rate: {success_rate:.1f}%")
            except Exception:
                pass
        
        print("="*80)
    
    def run(self):
        """Run the complete test suite with reporting."""
        print("Starting comprehensive test execution for size_analyzer_config.py")
        print(f"Timestamp: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check if test file exists
        if not self.test_file.exists():
            print(f"✗ Test file not found: {self.test_file}")
            return False
        
        # Install dependencies
        if not self.install_dependencies():
            print("✗ Failed to install dependencies")
            return False
        
        # Run tests
        process_result = self.run_tests()
        
        # Generate summary
        summary = self.generate_execution_summary(process_result)
        
        # Print results
        self.print_results_summary(process_result)
        
        return process_result and process_result.returncode == 0


if __name__ == '__main__':
    runner = TestRunner()
    success = runner.run()
    
    if success:
        print("\n✓ Test execution completed successfully!")
        sys.exit(0)
    else:
        print("\n✗ Test execution failed!")
        sys.exit(1)