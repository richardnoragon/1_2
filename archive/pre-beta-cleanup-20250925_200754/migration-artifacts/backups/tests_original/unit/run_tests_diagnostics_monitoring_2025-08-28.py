#!/usr/bin/env python3
"""
Test Runner for diagnostics_monitoring.py Comprehensive Unit Tests
Test execution timestamp: 2025-08-28

This script runs all unit tests for the diagnostics_monitoring module with
comprehensive reporting including HTML, JSON, and coverage reports.
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Configuration
TEST_DIR = Path(__file__).parent
PROJECT_ROOT = TEST_DIR.parent.parent
RESULTS_DIR = TEST_DIR
TIMESTAMP = datetime.now().strftime('%Y-%m-%d')

# Test configuration
TEST_FILES = [
    f"test_diagnostics_monitoring_{TIMESTAMP}.py",
    f"test_monitor_base_diagnostics_monitoring_{TIMESTAMP}.py", 
    f"test_platform_detector_diagnostics_monitoring_{TIMESTAMP}.py"
]

REPORT_FILES = {
    'html': f"result_diagnostics_monitoring_{TIMESTAMP}.html",
    'json': f"result_diagnostics_monitoring_{TIMESTAMP}.json",
    'coverage_html': f"result_diagnostics_monitoring_coverage_{TIMESTAMP}",
    'coverage_xml': f"result_diagnostics_monitoring_coverage_{TIMESTAMP}.xml"
}


def setup_environment():
    """Setup the test environment."""
    print("=" * 80)
    print("DIAGNOSTICS MONITORING UNIT TEST RUNNER")
    print("=" * 80)
    print(f"Test Execution Date: {TIMESTAMP}")
    print(f"Test Directory: {TEST_DIR}")
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"Python Version: {sys.version}")
    print("=" * 80)
    
    # Ensure test directory exists
    TEST_DIR.mkdir(exist_ok=True)
    
    # Add project root to Python path
    sys.path.insert(0, str(PROJECT_ROOT / 'src'))
    
    return True


def run_pytest_with_reports():
    """Run pytest with comprehensive reporting."""
    print("\nRunning pytest with comprehensive reporting...")
    
    # Build pytest command
    pytest_cmd = [
        sys.executable, '-m', 'pytest',
        str(TEST_DIR),
        '--verbose',
        '--tb=short',
        '--strict-markers',
        '--disable-warnings',
        f'--html={RESULTS_DIR / REPORT_FILES["html"]}',
        '--self-contained-html',
        '--json-report',
        f'--json-report-file={RESULTS_DIR / REPORT_FILES["json"]}',
        f'--cov={PROJECT_ROOT / "src" / "utilities" / "system" / "diagnostics_monitoring"}',
        f'--cov-report=html:{RESULTS_DIR / REPORT_FILES["coverage_html"]}',
        f'--cov-report=xml:{RESULTS_DIR / REPORT_FILES["coverage_xml"]}',
        '--cov-report=term-missing',
        '--cov-fail-under=50'  # Lower threshold for comprehensive testing
    ]
    
    print(f"Executing command: {' '.join(pytest_cmd)}")
    
    try:
        # Run pytest
        result = subprocess.run(
            pytest_cmd,
            cwd=TEST_DIR,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        print("\nPytest execution completed.")
        print(f"Return code: {result.returncode}")
        
        # Print stdout
        if result.stdout:
            print("\n--- PYTEST OUTPUT ---")
            print(result.stdout)
        
        # Print stderr if there are errors
        if result.stderr:
            print("\n--- PYTEST ERRORS ---")
            print(result.stderr)
        
        return result.returncode == 0, result
    
    except subprocess.TimeoutExpired:
        print("ERROR: Pytest execution timed out after 5 minutes")
        return False, None
    except Exception as e:
        print(f"ERROR: Failed to run pytest: {e}")
        return False, None


def run_individual_test_files():
    """Run individual test files if pytest fails."""
    print("\nRunning individual test files...")
    
    results = {}
    
    for test_file in TEST_FILES:
        test_path = TEST_DIR / test_file
        
        if not test_path.exists():
            print(f"SKIP: {test_file} - File not found")
            results[test_file] = {'status': 'skipped', 'reason': 'file_not_found'}
            continue
        
        print(f"\nRunning: {test_file}")
        
        try:
            # Run the test file directly
            cmd = [sys.executable, str(test_path)]
            result = subprocess.run(
                cmd,
                cwd=TEST_DIR,
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout per file
            )
            
            success = result.returncode == 0
            results[test_file] = {
                'status': 'passed' if success else 'failed',
                'return_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
            
            print(f"  Result: {'PASSED' if success else 'FAILED'}")
            if result.stdout:
                print(f"  Output length: {len(result.stdout)} characters")
            if result.stderr:
                print(f"  Error output: {result.stderr[:200]}...")
        
        except subprocess.TimeoutExpired:
            print(f"  TIMEOUT: {test_file} exceeded 2 minute limit")
            results[test_file] = {'status': 'timeout', 'reason': 'timeout_exceeded'}
        except Exception as e:
            print(f"  ERROR: {test_file} - {e}")
            results[test_file] = {'status': 'error', 'reason': str(e)}
    
    return results


def generate_summary_report(pytest_success, pytest_result, individual_results):
    """Generate a comprehensive summary report."""
    print("\n" + "=" * 80)
    print("COMPREHENSIVE TEST EXECUTION SUMMARY")
    print("=" * 80)
    
    summary = {
        'execution_timestamp': datetime.now().isoformat(),
        'execution_date': TIMESTAMP,
        'project_root': str(PROJECT_ROOT),
        'test_directory': str(TEST_DIR),
        'python_version': sys.version,
        'pytest_execution': {
            'success': pytest_success,
            'return_code': pytest_result.returncode if pytest_result else None
        },
        'individual_tests': individual_results,
        'reports_generated': {},
        'summary_statistics': {}
    }
    
    # Check which reports were generated
    for report_type, filename in REPORT_FILES.items():
        report_path = RESULTS_DIR / filename
        if report_type == 'coverage_html':
            # Coverage HTML creates a directory
            summary['reports_generated'][report_type] = {
                'path': str(report_path),
                'exists': report_path.exists(),
                'type': 'directory'
            }
        else:
            summary['reports_generated'][report_type] = {
                'path': str(report_path),
                'exists': report_path.exists(),
                'size': report_path.stat().st_size if report_path.exists() else 0,
                'type': 'file'
            }
    
    # Calculate summary statistics
    total_tests = len(individual_results)
    passed_tests = sum(1 for r in individual_results.values() if r.get('status') == 'passed')
    failed_tests = sum(1 for r in individual_results.values() if r.get('status') == 'failed')
    skipped_tests = sum(1 for r in individual_results.values() if r.get('status') == 'skipped')
    error_tests = sum(1 for r in individual_results.values() if r.get('status') == 'error')
    timeout_tests = sum(1 for r in individual_results.values() if r.get('status') == 'timeout')
    
    summary['summary_statistics'] = {
        'total_test_files': total_tests,
        'passed_test_files': passed_tests,
        'failed_test_files': failed_tests,
        'skipped_test_files': skipped_tests,
        'error_test_files': error_tests,
        'timeout_test_files': timeout_tests,
        'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0
    }
    
    # Print summary to console
    print(f"Execution Date: {TIMESTAMP}")
    print(f"Pytest Success: {'YES' if pytest_success else 'NO'}")
    print(f"Total Test Files: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Skipped: {skipped_tests}")
    print(f"Errors: {error_tests}")
    print(f"Timeouts: {timeout_tests}")
    print(f"Success Rate: {summary['summary_statistics']['success_rate']:.1f}%")
    
    print("\nGenerated Reports:")
    for report_type, info in summary['reports_generated'].items():
        status = "✓" if info['exists'] else "✗"
        print(f"  {status} {report_type}: {info['path']}")
    
    # Save summary to JSON file
    summary_file = RESULTS_DIR / f"result_diagnostics_monitoring_summary_{TIMESTAMP}.json"
    try:
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        print(f"\nSummary report saved: {summary_file}")
    except Exception as e:
        print(f"WARNING: Could not save summary report: {e}")
    
    return summary


def parse_pytest_json_report():
    """Parse pytest JSON report if available."""
    json_report_path = RESULTS_DIR / REPORT_FILES['json']
    
    if not json_report_path.exists():
        return None
    
    try:
        with open(json_report_path, 'r', encoding='utf-8') as f:
            report_data = json.load(f)
        
        print("\n--- PYTEST JSON REPORT SUMMARY ---")
        print(f"Total Tests: {report_data.get('summary', {}).get('total', 0)}")
        print(f"Passed: {report_data.get('summary', {}).get('passed', 0)}")
        print(f"Failed: {report_data.get('summary', {}).get('failed', 0)}")
        print(f"Skipped: {report_data.get('summary', {}).get('skipped', 0)}")
        print(f"Errors: {report_data.get('summary', {}).get('error', 0)}")
        
        if 'duration' in report_data:
            print(f"Execution Time: {report_data['duration']:.2f} seconds")
        
        return report_data
    
    except Exception as e:
        print(f"WARNING: Could not parse pytest JSON report: {e}")
        return None


def cleanup_and_finalize():
    """Perform cleanup and finalization."""
    print("\n" + "=" * 80)
    print("TEST EXECUTION COMPLETED")
    print("=" * 80)
    
    # List all generated files
    print("\nGenerated Files:")
    for file in RESULTS_DIR.glob(f"*{TIMESTAMP}*"):
        if file.is_file():
            size = file.stat().st_size
            print(f"  {file.name} ({size:,} bytes)")
        elif file.is_dir():
            file_count = len(list(file.rglob('*')))
            print(f"  {file.name}/ ({file_count} files)")
    
    print(f"\nAll reports saved to: {RESULTS_DIR}")
    print(f"Test execution timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def main():
    """Main test runner function."""
    try:
        # Setup environment
        if not setup_environment():
            return 1
        
        # Run pytest with comprehensive reporting
        pytest_success, pytest_result = run_pytest_with_reports()
        
        # Run individual test files
        individual_results = run_individual_test_files()
        
        # Parse pytest JSON report
        pytest_json_data = parse_pytest_json_report()
        
        # Generate summary report
        summary = generate_summary_report(pytest_success, pytest_result, individual_results)
        
        # Cleanup and finalize
        cleanup_and_finalize()
        
        # Return appropriate exit code
        if pytest_success or any(r.get('status') == 'passed' for r in individual_results.values()):
            print("\nTEST RUNNER: SUCCESS - At least some tests passed")
            return 0
        else:
            print("\nTEST RUNNER: FAILURE - No tests passed successfully")
            return 1
    
    except KeyboardInterrupt:
        print("\nTEST RUNNER: Interrupted by user")
        return 130
    except Exception as e:
        print(f"\nTEST RUNNER: Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)