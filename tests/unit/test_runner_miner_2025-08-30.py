"""
Enhanced Test Runner for miner.py with Comprehensive Reporting
Created: 2025-08-30
Target: src/utilities/pdf_tools/pdf_view_analysis/miner.py

This script provides an enhanced test execution environment with:
- Detailed HTML and JSON reporting
- Test coverage analysis
- Performance metrics
- Execution timestamps
- Standardized output formatting
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


class MinerTestRunner:
    """Enhanced test runner for miner.py with comprehensive reporting"""
    
    def __init__(self):
        self.test_start_time = None
        self.test_end_time = None
        self.test_directory = Path(__file__).parent
        self.date_stamp = datetime.now().strftime("%Y-%m-%d")
        self.timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # Output file names following the specified convention
        self.test_file = f"test_miner_{self.date_stamp}.py"
        self.result_prefix = f"result_miner_{self.date_stamp}"
        
        # Report file paths
        self.reports = {
            'html': self.test_directory / f"{self.result_prefix}_report.html",
            'json': self.test_directory / f"{self.result_prefix}_results.json",
            'junit': self.test_directory / f"{self.result_prefix}_junit.xml",
            'coverage_html': self.test_directory / f"coverage_miner_html_{self.date_stamp}",
            'coverage_json': self.test_directory / f"{self.result_prefix}_coverage.json",
            'coverage_xml': self.test_directory / f"{self.result_prefix}_coverage.xml",
            'execution_log': self.test_directory / f"{self.result_prefix}_execution.log"
        }
    
    def setup_environment(self):
        """Setup test environment and dependencies"""
        print(f"Setting up test environment at {self.timestamp}")
        
        # Ensure required packages are available
        required_packages = [
            'pytest>=7.0.0',
            'pytest-html>=3.1.0',
            'pytest-cov>=4.0.0',
            'pytest-json-report>=1.5.0',
            'pytest-timeout>=2.1.0',
            'PyQt5>=5.15.0',
            'PyMuPDF>=1.20.0'
        ]
        
        print("Checking required packages...")
        for package in required_packages:
            try:
                __import__(package.split('>=')[0].replace('-', '_'))
                print(f"✓ {package.split('>=')[0]} is available")
            except ImportError:
                print(f"✗ {package.split('>=')[0]} is missing")
                print(f"  Install with: pip install {package}")
        
        # Create output directories
        for report_type, path in self.reports.items():
            if 'html' in report_type and path.suffix == '':
                path.mkdir(exist_ok=True)
            elif path.suffix:
                path.parent.mkdir(exist_ok=True)
    
    def generate_test_command(self, test_markers=None, verbose=True):
        """Generate pytest command with all reporting options"""
        cmd = [
            sys.executable, '-m', 'pytest',
            str(self.test_directory / self.test_file)
        ]
        
        # Basic options
        if verbose:
            cmd.extend(['-v', '--tb=short'])
        
        # Reporting options
        cmd.extend([
            f'--html={self.reports["html"]}',
            '--self-contained-html',
            f'--junit-xml={self.reports["junit"]}',
            '--json-report',
            f'--json-report-file={self.reports["json"]}'
        ])
        
        # Coverage options
        cmd.extend([
            '--cov=miner',
            f'--cov-report=html:{self.reports["coverage_html"]}',
            f'--cov-report=json:{self.reports["coverage_json"]}',
            f'--cov-report=xml:{self.reports["coverage_xml"]}',
            '--cov-report=term-missing',
            '--cov-fail-under=70'
        ])
        
        # Performance and debugging options
        cmd.extend([
            '--durations=10',
            '--timeout=300',
            '--maxfail=5'
        ])
        
        # Test markers
        if test_markers:
            for marker in test_markers:
                cmd.extend(['-m', marker])
        
        return cmd
    
    def run_tests(self, test_markers=None, capture_output=True):
        """Execute tests with comprehensive reporting"""
        self.test_start_time = datetime.now()
        print(f"Starting test execution at {self.test_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Generate test command
        cmd = self.generate_test_command(test_markers)
        
        print(f"Executing command: {' '.join(cmd)}")
        print("-" * 80)
        
        # Execute tests
        try:
            if capture_output:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    cwd=self.test_directory
                )
                
                # Log output
                with open(self.reports['execution_log'], 'w') as log_file:
                    log_file.write(f"Test Execution Log - {self.timestamp}\\n")
                    log_file.write("=" * 80 + "\\n")
                    log_file.write(f"Command: {' '.join(cmd)}\\n")
                    log_file.write(f"Start Time: {self.test_start_time}\\n")
                    log_file.write("\\nSTDOUT:\\n")
                    log_file.write(result.stdout)
                    log_file.write("\\nSTDERR:\\n")
                    log_file.write(result.stderr)
                
                print(result.stdout)
                if result.stderr:
                    print("STDERR:", result.stderr)
                
                return_code = result.returncode
            else:
                return_code = subprocess.call(cmd, cwd=self.test_directory)
        
        except Exception as e:
            print(f"Error executing tests: {e}")
            return_code = 1
        
        self.test_end_time = datetime.now()
        
        # Generate summary
        self.generate_execution_summary(return_code)
        
        return return_code
    
    def generate_execution_summary(self, return_code):
        """Generate comprehensive execution summary"""
        execution_time = self.test_end_time - self.test_start_time
        
        summary = {
            'execution_info': {
                'start_time': self.test_start_time.isoformat(),
                'end_time': self.test_end_time.isoformat(),
                'execution_time_seconds': execution_time.total_seconds(),
                'execution_time_formatted': str(execution_time),
                'date_stamp': self.date_stamp,
                'timestamp': self.timestamp,
                'return_code': return_code,
                'success': return_code == 0
            },
            'test_files': {
                'target_module': 'miner.py',
                'test_file': self.test_file,
                'test_directory': str(self.test_directory)
            },
            'report_files': {
                name: str(path) for name, path in self.reports.items()
            },
            'environment_info': {
                'python_version': sys.version,
                'platform': sys.platform,
                'working_directory': os.getcwd()
            }
        }
        
        # Save summary
        summary_file = self.test_directory / f"{self.result_prefix}_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Print summary
        print("\\n" + "=" * 80)
        print("TEST EXECUTION SUMMARY")
        print("=" * 80)
        print(f"Start Time: {self.test_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"End Time: {self.test_end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Duration: {execution_time}")
        print(f"Result: {'SUCCESS' if return_code == 0 else 'FAILURE'}")
        print(f"Return Code: {return_code}")
        print()
        print("Generated Reports:")
        for name, path in self.reports.items():
            if path.exists() or (path.suffix == '' and path.is_dir()):
                status = "✓"
            else:
                status = "✗"
            print(f"  {status} {name}: {path}")
        print(f"  ✓ summary: {summary_file}")
        print("=" * 80)
    
    def run_specific_tests(self, test_categories):
        """Run specific test categories"""
        category_markers = {
            'unit': ['unit'],
            'integration': ['integration'],
            'gui': ['gui'],
            'performance': ['performance'],
            'error_handling': ['error_handling'],
            'all': None,
            'fast': ['fast', 'unit'],
            'slow': ['slow', 'performance', 'integration']
        }
        
        markers = []
        for category in test_categories:
            if category in category_markers:
                if category_markers[category]:
                    markers.extend(category_markers[category])
            else:
                print(f"Warning: Unknown test category '{category}'")
        
        if 'all' in test_categories:
            markers = None
        
        return self.run_tests(test_markers=markers)
    
    def cleanup_old_reports(self, keep_days=7):
        """Clean up old test reports"""
        print(f"Cleaning up reports older than {keep_days} days...")
        
        current_time = time.time()
        cutoff_time = current_time - (keep_days * 24 * 60 * 60)
        
        for file_path in self.test_directory.glob("result_miner_*"):
            if file_path.stat().st_mtime < cutoff_time:
                try:
                    if file_path.is_dir():
                        import shutil
                        shutil.rmtree(file_path)
                    else:
                        file_path.unlink()
                    print(f"  Removed: {file_path}")
                except Exception as e:
                    print(f"  Failed to remove {file_path}: {e}")


def main():
    """Main entry point for the test runner"""
    parser = argparse.ArgumentParser(
        description="Enhanced Test Runner for miner.py",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_runner_miner_2025-08-30.py
  python test_runner_miner_2025-08-30.py --categories unit integration
  python test_runner_miner_2025-08-30.py --categories fast --no-capture
  python test_runner_miner_2025-08-30.py --cleanup --keep-days 3
        """
    )
    
    parser.add_argument(
        '--categories',
        nargs='+',
        choices=['unit', 'integration', 'gui', 'performance', 'error_handling', 'all', 'fast', 'slow'],
        default=['all'],
        help='Test categories to run (default: all)'
    )
    
    parser.add_argument(
        '--no-capture',
        action='store_true',
        help='Disable output capture for interactive debugging'
    )
    
    parser.add_argument(
        '--cleanup',
        action='store_true',
        help='Clean up old test reports'
    )
    
    parser.add_argument(
        '--keep-days',
        type=int,
        default=7,
        help='Number of days to keep old reports (default: 7)'
    )
    
    args = parser.parse_args()
    
    # Create test runner
    runner = MinerTestRunner()
    
    # Setup environment
    runner.setup_environment()
    
    # Clean up old reports if requested
    if args.cleanup:
        runner.cleanup_old_reports(args.keep_days)
    
    # Run tests
    return_code = runner.run_specific_tests(
        args.categories,
    )
    
    sys.exit(return_code)


if __name__ == "__main__":
    main()