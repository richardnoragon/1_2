#!/usr/bin/env python3
"""
Security Validator Test Runner
=============================

Test Runner: run_security_validator_tests_2025-08-30.py
Target: test_security_validator_2025-08-30.py
Generated: 2025-08-30

This script executes comprehensive unit tests for the SecurityValidator module
and generates standardized test output with execution timestamps and detailed results.

Usage:
    python run_security_validator_tests_2025-08-30.py [options]

Options:
    --verbose       Enable verbose output
    --coverage      Generate coverage reports
    --html          Generate HTML reports
    --json          Generate JSON reports
    --junit         Generate JUnit XML reports
    --benchmark     Run performance benchmarks
    --markers       Filter tests by markers (e.g., --markers security)
    --parallel      Run tests in parallel
    --timeout       Set test timeout (default: 300 seconds)

Output Files:
    - result_security_validator_2025-08-30.html
    - result_security_validator_2025-08-30.json
    - result_security_validator_2025-08-30_junit.xml
    - result_security_validator_coverage_2025-08-30/ (directory)
    - result_security_validator_coverage_2025-08-30.json
"""

import argparse
import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('result_security_validator_test_execution_2025-08-30.log')
    ]
)
logger = logging.getLogger(__name__)

class SecurityValidatorTestRunner:
    """Test runner for SecurityValidator unit tests."""
    
    def __init__(self):
        """Initialize the test runner."""
        self.start_time = datetime.now()
        self.test_dir = Path(__file__).parent
        self.test_file = "test_security_validator_2025-08-30.py"
        self.config_file = "pytest_security_validator_2025-08-30.ini"
        self.requirements_file = "requirements_test_security_validator_2025-08-30.txt"
        
        # Output files
        self.html_report = "result_security_validator_2025-08-30.html"
        self.json_report = "result_security_validator_2025-08-30.json"
        self.junit_report = "result_security_validator_2025-08-30_junit.xml"
        self.coverage_dir = "result_security_validator_coverage_2025-08-30"
        self.coverage_json = "result_security_validator_coverage_2025-08-30.json"
        self.summary_file = "result_security_validator_summary_2025-08-30.json"
        
        logger.info(f"SecurityValidator Test Runner initialized at {self.start_time}")
        logger.info(f"Working directory: {self.test_dir}")
    
    def check_dependencies(self):
        """Check if required dependencies are installed."""
        logger.info("Checking test dependencies...")
        
        required_packages = [
            'pytest', 'pytest-html', 'pytest-json-report', 
            'pytest-cov', 'pytest-mock', 'pytest-timeout'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            logger.warning(f"Missing packages: {missing_packages}")
            logger.info("Installing missing packages...")
            self.install_dependencies()
        else:
            logger.info("All dependencies are available")
    
    def install_dependencies(self):
        """Install required test dependencies."""
        try:
            requirements_path = self.test_dir / self.requirements_file
            if requirements_path.exists():
                cmd = [sys.executable, "-m", "pip", "install", "-r", str(requirements_path)]
                logger.info(f"Installing dependencies: {' '.join(cmd)}")
                
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    timeout=300
                )
                
                if result.returncode == 0:
                    logger.info("Dependencies installed successfully")
                else:
                    logger.error(f"Failed to install dependencies: {result.stderr}")
            else:
                logger.warning(f"Requirements file not found: {requirements_path}")
        except Exception as e:
            logger.error(f"Error installing dependencies: {e}")
    
    def validate_test_environment(self):
        """Validate the test environment setup."""
        logger.info("Validating test environment...")
        
        # Check if test file exists
        test_path = self.test_dir / self.test_file
        if not test_path.exists():
            logger.error(f"Test file not found: {test_path}")
            return False
        
        # Check if config file exists
        config_path = self.test_dir / self.config_file
        if not config_path.exists():
            logger.warning(f"Config file not found: {config_path}")
        
        # Check if target module can be imported
        try:
            sys.path.insert(0, str(self.test_dir.parent.parent / "src"))
            from utilities.network.network_connectivity_complex.core.security_validator import \
                SecurityValidator
            logger.info("Target module imported successfully")
            return True
        except ImportError as e:
            logger.error(f"Cannot import target module: {e}")
            return False
    
    def build_pytest_command(self, args):
        """Build the pytest command with all options."""
        cmd = [sys.executable, "-m", "pytest"]
        
        # Add config file if it exists
        config_path = self.test_dir / self.config_file
        if config_path.exists():
            cmd.extend(["-c", str(config_path)])
        
        # Add test file
        cmd.append(str(self.test_dir / self.test_file))
        
        # Basic options
        cmd.extend(["-v", "--tb=short"])
        
        # Output reports
        if args.html:
            cmd.extend([
                "--html", self.html_report,
                "--self-contained-html"
            ])
        
        if args.json:
            cmd.extend([
                "--json-report",
                "--json-report-file", self.json_report
            ])
        
        if args.junit:
            cmd.extend([
                "--junit-xml", self.junit_report
            ])
        
        # Coverage options
        if args.coverage:
            cmd.extend([
                "--cov=utilities.network.network_connectivity_complex.core.security_validator",
                f"--cov-report=html:{self.coverage_dir}",
                f"--cov-report=json:{self.coverage_json}",
                "--cov-report=term-missing"
            ])
        
        # Test filtering
        if args.markers:
            cmd.extend(["-m", args.markers])
        
        # Parallel execution
        if args.parallel:
            cmd.extend(["-n", "auto"])
        
        # Timeout
        if args.timeout:
            cmd.extend(["--timeout", str(args.timeout)])
        
        # Benchmark
        if args.benchmark:
            cmd.append("--benchmark-only")
        
        return cmd
    
    def run_tests(self, args):
        """Execute the test suite."""
        logger.info("Starting test execution...")
        
        cmd = self.build_pytest_command(args)
        logger.info(f"Executing command: {' '.join(cmd)}")
        
        start_time = time.time()
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.test_dir,
                capture_output=True,
                text=True,
                timeout=args.timeout
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            logger.info(f"Test execution completed in {duration:.2f} seconds")
            logger.info(f"Return code: {result.returncode}")
            
            # Log stdout and stderr
            if result.stdout:
                logger.info("Test output:")
                print(result.stdout)
            
            if result.stderr:
                logger.warning("Test errors/warnings:")
                print(result.stderr)
            
            return {
                'returncode': result.returncode,
                'duration': duration,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'success': result.returncode == 0
            }
            
        except subprocess.TimeoutExpired:
            logger.error(f"Test execution timed out after {args.timeout} seconds")
            return {
                'returncode': -1,
                'duration': args.timeout,
                'stdout': '',
                'stderr': 'Test execution timed out',
                'success': False
            }
        except Exception as e:
            logger.error(f"Error executing tests: {e}")
            return {
                'returncode': -1,
                'duration': 0,
                'stdout': '',
                'stderr': str(e),
                'success': False
            }
    
    def generate_summary_report(self, test_result):
        """Generate a comprehensive summary report."""
        logger.info("Generating summary report...")
        
        summary = {
            'test_execution': {
                'timestamp': self.start_time.isoformat(),
                'duration_seconds': test_result['duration'],
                'success': test_result['success'],
                'return_code': test_result['returncode']
            },
            'test_files': {
                'test_file': self.test_file,
                'config_file': self.config_file,
                'requirements_file': self.requirements_file
            },
            'output_files': {
                'html_report': self.html_report,
                'json_report': self.json_report,
                'junit_report': self.junit_report,
                'coverage_directory': self.coverage_dir,
                'coverage_json': self.coverage_json,
                'summary_file': self.summary_file
            },
            'environment': {
                'python_version': sys.version,
                'working_directory': str(self.test_dir),
                'platform': sys.platform
            }
        }
        
        # Add test results if JSON report exists
        json_report_path = self.test_dir / self.json_report
        if json_report_path.exists():
            try:
                with open(json_report_path, 'r') as f:
                    test_data = json.load(f)
                summary['test_results'] = {
                    'total_tests': test_data.get('summary', {}).get('total', 0),
                    'passed': test_data.get('summary', {}).get('passed', 0),
                    'failed': test_data.get('summary', {}).get('failed', 0),
                    'skipped': test_data.get('summary', {}).get('skipped', 0),
                    'errors': test_data.get('summary', {}).get('error', 0)
                }
            except Exception as e:
                logger.warning(f"Could not parse JSON report: {e}")
        
        # Add coverage information if available
        coverage_json_path = self.test_dir / self.coverage_json
        if coverage_json_path.exists():
            try:
                with open(coverage_json_path, 'r') as f:
                    coverage_data = json.load(f)
                summary['coverage'] = {
                    'line_coverage': coverage_data.get('totals', {}).get('percent_covered', 0),
                    'lines_covered': coverage_data.get('totals', {}).get('covered_lines', 0),
                    'total_lines': coverage_data.get('totals', {}).get('num_statements', 0),
                    'missing_lines': coverage_data.get('totals', {}).get('missing_lines', 0)
                }
            except Exception as e:
                logger.warning(f"Could not parse coverage report: {e}")
        
        # Write summary to file
        summary_path = self.test_dir / self.summary_file
        try:
            with open(summary_path, 'w') as f:
                json.dump(summary, f, indent=2, default=str)
            logger.info(f"Summary report written to: {summary_path}")
        except Exception as e:
            logger.error(f"Error writing summary report: {e}")
        
        return summary
    
    def cleanup_old_results(self):
        """Clean up old test result files."""
        logger.info("Cleaning up old test results...")
        
        patterns = [
            "result_security_validator_*.html",
            "result_security_validator_*.json",
            "result_security_validator_*.xml",
            "result_security_validator_*.log"
        ]
        
        for pattern in patterns:
            for file_path in self.test_dir.glob(pattern):
                if file_path.name != self.html_report and \
                   file_path.name != self.json_report and \
                   file_path.name != self.junit_report:
                    try:
                        file_path.unlink()
                        logger.debug(f"Removed old file: {file_path}")
                    except Exception as e:
                        logger.warning(f"Could not remove {file_path}: {e}")
    
    def validate_output_files(self):
        """Validate that expected output files were generated."""
        logger.info("Validating output files...")
        
        expected_files = [
            self.html_report,
            self.json_report,
            self.junit_report,
            self.summary_file
        ]
        
        missing_files = []
        for filename in expected_files:
            file_path = self.test_dir / filename
            if not file_path.exists():
                missing_files.append(filename)
            else:
                file_size = file_path.stat().st_size
                logger.info(f"Generated: {filename} ({file_size} bytes)")
        
        if missing_files:
            logger.warning(f"Missing output files: {missing_files}")
        else:
            logger.info("All expected output files generated successfully")
        
        return len(missing_files) == 0


def main():
    """Main entry point for the test runner."""
    parser = argparse.ArgumentParser(
        description="Run comprehensive unit tests for SecurityValidator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        '--verbose', action='store_true',
        help='Enable verbose output'
    )
    parser.add_argument(
        '--coverage', action='store_true', default=True,
        help='Generate coverage reports (default: True)'
    )
    parser.add_argument(
        '--html', action='store_true', default=True,
        help='Generate HTML reports (default: True)'
    )
    parser.add_argument(
        '--json', action='store_true', default=True,
        help='Generate JSON reports (default: True)'
    )
    parser.add_argument(
        '--junit', action='store_true', default=True,
        help='Generate JUnit XML reports (default: True)'
    )
    parser.add_argument(
        '--benchmark', action='store_true',
        help='Run performance benchmarks'
    )
    parser.add_argument(
        '--markers', type=str,
        help='Filter tests by markers (e.g., security, performance)'
    )
    parser.add_argument(
        '--parallel', action='store_true',
        help='Run tests in parallel'
    )
    parser.add_argument(
        '--timeout', type=int, default=300,
        help='Set test timeout in seconds (default: 300)'
    )
    parser.add_argument(
        '--cleanup', action='store_true', default=True,
        help='Clean up old result files (default: True)'
    )
    
    args = parser.parse_args()
    
    # Initialize test runner
    runner = SecurityValidatorTestRunner()
    
    try:
        # Setup phase
        if args.cleanup:
            runner.cleanup_old_results()
        
        runner.check_dependencies()
        
        if not runner.validate_test_environment():
            logger.error("Test environment validation failed")
            sys.exit(1)
        
        # Execution phase
        test_result = runner.run_tests(args)
        
        # Reporting phase
        summary = runner.generate_summary_report(test_result)
        output_validation = runner.validate_output_files()
        
        # Final status
        end_time = datetime.now()
        total_duration = (end_time - runner.start_time).total_seconds()
        
        logger.info(f"Test execution completed in {total_duration:.2f} seconds")
        logger.info(f"Test success: {test_result['success']}")
        logger.info(f"Output validation: {output_validation}")
        
        if test_result['success'] and output_validation:
            logger.info("✅ All tests completed successfully!")
            print("\n" + "="*60)
            print("🎉 SECURITY VALIDATOR TESTS COMPLETED SUCCESSFULLY! 🎉")
            print("="*60)
            print(f"📊 Test Results: {runner.html_report}")
            print(f"📈 Coverage Report: {runner.coverage_dir}/index.html")
            print(f"📋 Summary: {runner.summary_file}")
            print("="*60)
            sys.exit(0)
        else:
            logger.error("❌ Test execution failed or output validation failed")
            sys.exit(1)
    
    except KeyboardInterrupt:
        logger.warning("Test execution interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()