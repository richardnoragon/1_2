#!/usr/bin/env python3
"""
Test Runner for Office Metadata Editor Unit Tests
File: run_office_meta_data_editor_tests_2025-08-24.py
Created: 2025-08-24

This script executes comprehensive unit tests for office_meta_data_editor.py
with detailed reporting, coverage analysis, and error handling.

Features:
- Automated test discovery and execution
- Coverage reporting with HTML and JSON output
- Error logging and debugging information
- Performance benchmarking
- Test result validation
- Dependency verification
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
    'test_file': 'test_office_meta_data_editor_2025-08-24.py',
    'target_module': 'src.tools.metadata.office_meta_data_editor',
    'output_dir': 'tests/unit',
    'coverage_threshold': 85,
    'timeout': 300,  # 5 minutes
    'reports': {
        'html': 'result_office_meta_data_editor_2025-08-24.html',
        'json': 'result_office_meta_data_editor_2025-08-24.json',
        'coverage_html': 'result_office_meta_data_editor_coverage_2025-08-24',
        'coverage_json': 'result_office_meta_data_editor_coverage_2025-08-24.json',
        'summary': 'result_office_meta_data_editor_execution_summary_2025-08-24.txt'
    }
}


def check_dependencies():
    """Check if required dependencies are available."""
    print("Checking dependencies...")
    
    required_packages = [
        'pytest', 'pytest-cov', 'pytest-html', 'pytest-json-report',
        'PyQt5', 'coverage'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✓ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"  ✗ {package} (missing)")
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Installing missing packages...")
        
        for package in missing_packages:
            try:
                subprocess.run([
                    sys.executable, '-m', 'pip', 'install', package
                ], check=True, capture_output=True)
                print(f"  ✓ Installed {package}")
            except subprocess.CalledProcessError as e:
                print(f"  ✗ Failed to install {package}: {e}")
                return False
    
    return True


def setup_test_environment():
    """Setup test environment and directories."""
    print("Setting up test environment...")
    
    # Ensure output directory exists
    output_dir = Path(TEST_CONFIG['output_dir'])
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Set environment variables for testing
    os.environ['PYTEST_CURRENT_TEST'] = 'office_meta_data_editor_tests'
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'  # For headless PyQt5 testing
    
    print("  ✓ Test environment configured")
    return True


def run_tests():
    """Execute the test suite with comprehensive reporting."""
    print("Executing test suite...")
    
    start_time = time.time()
    
    # Construct pytest command
    test_file = os.path.join(TEST_CONFIG['output_dir'], TEST_CONFIG['test_file'])
    
    pytest_args = [
        sys.executable, '-m', 'pytest',
        test_file,
        '-v',
        '--tb=short',
        '--strict-markers',
        '--disable-warnings',
        f'--cov={TEST_CONFIG["target_module"]}',
        '--cov-report=term-missing',
        f'--cov-report=html:{TEST_CONFIG["output_dir"]}/{TEST_CONFIG["reports"]["coverage_html"]}',
        f'--cov-report=json:{TEST_CONFIG["output_dir"]}/{TEST_CONFIG["reports"]["coverage_json"]}',
        '--cov-branch',
        f'--cov-fail-under={TEST_CONFIG["coverage_threshold"]}',
        f'--html={TEST_CONFIG["output_dir"]}/{TEST_CONFIG["reports"]["html"]}',
        '--self-contained-html',
        '--json-report',
        f'--json-report-file={TEST_CONFIG["output_dir"]}/{TEST_CONFIG["reports"]["json"]}',
        '--json-report-summary',
        f'--timeout={TEST_CONFIG["timeout"]}',
        '--capture=no'
    ]
    
    print(f"Running command: {' '.join(pytest_args)}")
    
    try:
        result = subprocess.run(
            pytest_args,
            capture_output=True,
            text=True,
            timeout=TEST_CONFIG['timeout']
        )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Parse results
        test_results = {
            'execution_time': execution_time,
            'return_code': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"  ✓ Tests completed in {execution_time:.2f} seconds")
        print(f"  ✓ Return code: {result.returncode}")
        
        return test_results
        
    except subprocess.TimeoutExpired:
        print(f"  ✗ Tests timed out after {TEST_CONFIG['timeout']} seconds")
        return None
    except Exception as e:
        print(f"  ✗ Error running tests: {e}")
        return None


def parse_test_results():
    """Parse and analyze test results."""
    print("Parsing test results...")
    
    results_summary = {
        'test_file': TEST_CONFIG['test_file'],
        'target_module': TEST_CONFIG['target_module'],
        'timestamp': datetime.now().isoformat(),
        'tests': {},
        'coverage': {},
        'errors': []
    }
    
    # Parse JSON report if available
    json_report_path = os.path.join(
        TEST_CONFIG['output_dir'], 
        TEST_CONFIG['reports']['json']
    )
    
    if os.path.exists(json_report_path):
        try:
            with open(json_report_path, 'r') as f:
                json_data = json.load(f)
            
            results_summary['tests'] = {
                'total': json_data.get('summary', {}).get('total', 0),
                'passed': json_data.get('summary', {}).get('passed', 0),
                'failed': json_data.get('summary', {}).get('failed', 0),
                'skipped': json_data.get('summary', {}).get('skipped', 0),
                'duration': json_data.get('duration', 0)
            }
            
            print(f"  ✓ Parsed JSON report: {results_summary['tests']}")
            
        except Exception as e:
            results_summary['errors'].append(f"Failed to parse JSON report: {e}")
            print(f"  ✗ JSON report parsing error: {e}")
    
    # Parse coverage report if available
    coverage_json_path = os.path.join(
        TEST_CONFIG['output_dir'], 
        TEST_CONFIG['reports']['coverage_json']
    )
    
    if os.path.exists(coverage_json_path):
        try:
            with open(coverage_json_path, 'r') as f:
                coverage_data = json.load(f)
            
            # Extract coverage summary
            totals = coverage_data.get('totals', {})
            results_summary['coverage'] = {
                'lines_covered': totals.get('covered_lines', 0),
                'lines_total': totals.get('num_statements', 0),
                'coverage_percent': totals.get('percent_covered', 0),
                'branches_covered': totals.get('covered_branches', 0),
                'branches_total': totals.get('num_branches', 0),
                'branch_coverage_percent': totals.get('percent_covered_branches', 0)
            }
            
            print(f"  ✓ Parsed coverage report: {results_summary['coverage']['coverage_percent']:.1f}%")
            
        except Exception as e:
            results_summary['errors'].append(f"Failed to parse coverage report: {e}")
            print(f"  ✗ Coverage report parsing error: {e}")
    
    return results_summary


def generate_summary_report(test_results, results_summary):
    """Generate comprehensive summary report."""
    print("Generating summary report...")
    
    summary_path = os.path.join(
        TEST_CONFIG['output_dir'], 
        TEST_CONFIG['reports']['summary']
    )
    
    try:
        with open(summary_path, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("OFFICE METADATA EDITOR UNIT TEST EXECUTION SUMMARY\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"Test Execution Timestamp: {results_summary['timestamp']}\n")
            f.write(f"Test File: {TEST_CONFIG['test_file']}\n")
            f.write(f"Target Module: {TEST_CONFIG['target_module']}\n")
            f.write(f"Test Framework: pytest with comprehensive reporting\n\n")
            
            # Test Results Section
            f.write("TEST EXECUTION RESULTS\n")
            f.write("-" * 50 + "\n")
            
            if test_results:
                f.write(f"Execution Time: {test_results['execution_time']:.2f} seconds\n")
                f.write(f"Return Code: {test_results['return_code']}\n")
                
                if test_results['return_code'] == 0:
                    f.write("Status: ✅ SUCCESS\n")
                else:
                    f.write("Status: ❌ FAILED\n")
            else:
                f.write("Status: ❌ EXECUTION FAILED\n")
            
            f.write("\n")
            
            # Test Statistics
            if results_summary['tests']:
                tests = results_summary['tests']
                f.write("TEST STATISTICS\n")
                f.write("-" * 50 + "\n")
                f.write(f"Total Tests: {tests['total']}\n")
                f.write(f"Passed: {tests['passed']}\n")
                f.write(f"Failed: {tests['failed']}\n")
                f.write(f"Skipped: {tests['skipped']}\n")
                f.write(f"Duration: {tests['duration']:.2f} seconds\n")
                
                if tests['total'] > 0:
                    success_rate = (tests['passed'] / tests['total']) * 100
                    f.write(f"Success Rate: {success_rate:.1f}%\n")
                
                f.write("\n")
            
            # Coverage Statistics
            if results_summary['coverage']:
                coverage = results_summary['coverage']
                f.write("CODE COVERAGE ANALYSIS\n")
                f.write("-" * 50 + "\n")
                f.write(f"Lines Covered: {coverage['lines_covered']}\n")
                f.write(f"Total Lines: {coverage['lines_total']}\n")
                f.write(f"Line Coverage: {coverage['coverage_percent']:.1f}%\n")
                f.write(f"Branches Covered: {coverage['branches_covered']}\n")
                f.write(f"Total Branches: {coverage['branches_total']}\n")
                f.write(f"Branch Coverage: {coverage['branch_coverage_percent']:.1f}%\n")
                
                if coverage['coverage_percent'] >= TEST_CONFIG['coverage_threshold']:
                    f.write("Coverage Status: ✅ MEETS THRESHOLD\n")
                else:
                    f.write("Coverage Status: ⚠️ BELOW THRESHOLD\n")
                
                f.write("\n")
            
            # Generated Files
            f.write("GENERATED FILES\n")
            f.write("-" * 50 + "\n")
            
            for report_type, filename in TEST_CONFIG['reports'].items():
                file_path = os.path.join(TEST_CONFIG['output_dir'], filename)
                if os.path.exists(file_path):
                    size = os.path.getsize(file_path)
                    f.write(f"✅ {filename} ({size:,} bytes)\n")
                else:
                    f.write(f"❌ {filename} (not generated)\n")
            
            f.write("\n")
            
            # Errors and Warnings
            if results_summary['errors']:
                f.write("ERRORS AND WARNINGS\n")
                f.write("-" * 50 + "\n")
                for error in results_summary['errors']:
                    f.write(f"• {error}\n")
                f.write("\n")
            
            # Output sections
            if test_results and test_results['stdout']:
                f.write("STANDARD OUTPUT\n")
                f.write("-" * 50 + "\n")
                f.write(test_results['stdout'])
                f.write("\n\n")
            
            if test_results and test_results['stderr']:
                f.write("ERROR OUTPUT\n")
                f.write("-" * 50 + "\n")
                f.write(test_results['stderr'])
                f.write("\n\n")
            
            f.write("=" * 80 + "\n")
            f.write("END OF REPORT\n")
            f.write("=" * 80 + "\n")
        
        print(f"  ✓ Summary report generated: {summary_path}")
        return True
        
    except Exception as e:
        print(f"  ✗ Failed to generate summary report: {e}")
        return False


def main():
    """Main execution function."""
    print("Office Metadata Editor Test Runner")
    print("=" * 50)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Dependency check failed")
        return 1
    
    # Setup environment
    if not setup_test_environment():
        print("❌ Environment setup failed")
        return 1
    
    # Run tests
    test_results = run_tests()
    if test_results is None:
        print("❌ Test execution failed")
        return 1
    
    # Parse results
    results_summary = parse_test_results()
    
    # Generate summary
    if not generate_summary_report(test_results, results_summary):
        print("❌ Summary generation failed")
        return 1
    
    # Final status
    print("\n" + "=" * 50)
    print("Test execution completed!")
    
    if test_results['return_code'] == 0:
        print("✅ All tests passed successfully")
        return 0
    else:
        print("❌ Some tests failed")
        return test_results['return_code']


if __name__ == "__main__":
    sys.exit(main())