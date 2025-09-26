#!/usr/bin/env python3
"""
Enhanced Test Execution Script for Security Validator Tests
===========================================================

Script: execute_security_validator_tests_enhanced_2025-08-30.py
Target: test_security_validator_2025-08-30.py
Generated: 2025-08-30T09:40:00Z
Framework: pytest with comprehensive reporting and benchmarking

Features:
- Standardized timestamp generation
- Enhanced result file naming
- Memory profiling integration
- Performance benchmarking
- Comprehensive reporting
- Error handling and cleanup
- Test result analysis
"""

import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import psutil
except ImportError:
    psutil = None


class SecurityValidatorTestRunner:
    """Enhanced test runner for SecurityValidator tests."""
    
    def __init__(self):
        """Initialize the test runner."""
        self.start_time = datetime.now(timezone.utc)
        self.test_dir = Path(__file__).parent
        self.base_name = "security_validator_2025-08-30"
        
        # Setup logging
        self.setup_logging()
        
        # Test configuration
        self.config = {
            'pytest_config': f'pytest_{self.base_name}_enhanced.ini',
            'test_file': f'test_{self.base_name}.py',
            'conftest_file': f'conftest_{self.base_name}.py',
            'requirements_file': f'requirements_test_{self.base_name}_enhanced.txt'
        }
        
        # Result files
        self.results = {
            'html_report': f'result_{self.base_name}.html',
            'json_report': f'result_{self.base_name}.json',
            'coverage_html': f'result_{self.base_name}_coverage',
            'coverage_json': f'result_{self.base_name}_coverage.json',
            'coverage_xml': f'result_{self.base_name}_coverage.xml',
            'junit_xml': f'result_{self.base_name}_junit.xml',
            'log_file': f'result_{self.base_name}_test.log',
            'execution_summary': f'result_{self.base_name}_execution_summary.json',
            'performance_report': f'result_{self.base_name}_performance.json',
            'memory_report': f'result_{self.base_name}_memory.json'
        }
        
    def setup_logging(self):
        """Setup logging configuration."""
        log_format = '%(asctime)s [%(levelname)8s] %(name)s: %(message)s'
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.logger = logging.getLogger('SecurityValidatorTestRunner')
    
    def check_dependencies(self) -> bool:
        """Check if all required dependencies are installed."""
        self.logger.info("Checking test dependencies...")
        
        requirements_file = self.test_dir / self.config['requirements_file']
        if not requirements_file.exists():
            self.logger.warning(f"Requirements file not found: {requirements_file}")
            return True  # Continue anyway
        
        try:
            # Check if pytest is available
            import pytest
            self.logger.info(f"pytest version: {pytest.__version__}")
            
            # Check other critical packages
            packages_to_check = [
                ('coverage', 'coverage'),
                ('pytest_html', 'pytest-html'),
                ('pytest_json_report', 'pytest-json-report')
            ]
            
            for package_import, package_name in packages_to_check:
                try:
                    __import__(package_import)
                    self.logger.info(f"✓ {package_name} is available")
                except ImportError:
                    self.logger.warning(f"⚠ {package_name} not found - some features may be limited")
            
            return True
            
        except ImportError as e:
            self.logger.error(f"Critical dependency missing: {e}")
            return False
    
    def prepare_test_environment(self):
        """Prepare the test environment."""
        self.logger.info("Preparing test environment...")
        
        # Ensure test files exist
        test_file = self.test_dir / self.config['test_file']
        if not test_file.exists():
            self.logger.error(f"Test file not found: {test_file}")
            return False
        
        # Clean up previous results
        self.cleanup_previous_results()
        
        # Create necessary directories
        for result_path in self.results.values():
            if result_path.endswith('_coverage') or '/' in result_path:
                result_dir = self.test_dir / result_path
                result_dir.mkdir(exist_ok=True)
        
        return True
    
    def cleanup_previous_results(self):
        """Clean up previous test results."""
        self.logger.info("Cleaning up previous test results...")
        
        patterns_to_clean = [
            f'result_{self.base_name}*',
            f'.pytest_cache',
            f'__pycache__'
        ]
        
        for pattern in patterns_to_clean:
            for path in self.test_dir.glob(pattern):
                if path.is_file():
                    try:
                        path.unlink()
                    except Exception as e:
                        self.logger.warning(f"Could not remove {path}: {e}")
                elif path.is_dir():
                    try:
                        import shutil
                        shutil.rmtree(path, ignore_errors=True)
                    except Exception as e:
                        self.logger.warning(f"Could not remove directory {path}: {e}")
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information for the test report."""
        info = {
            'timestamp': self.start_time.isoformat(),
            'python_version': sys.version,
            'platform': sys.platform,
            'current_directory': str(self.test_dir),
            'environment_variables': {
                'PYTHONPATH': os.environ.get('PYTHONPATH', ''),
                'PATH': os.environ.get('PATH', '')[:200] + '...' if len(os.environ.get('PATH', '')) > 200 else os.environ.get('PATH', '')
            }
        }
        
        if psutil:
            info.update({
                'cpu_count': psutil.cpu_count(),
                'memory_total': psutil.virtual_memory().total,
                'memory_available': psutil.virtual_memory().available
            })
        
        return info
    
    def monitor_memory_usage(self) -> Dict[str, Any]:
        """Monitor memory usage during test execution."""
        if not psutil:
            return {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'error': 'psutil not available'
            }
        
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            
            return {
                'rss': memory_info.rss,
                'vms': memory_info.vms,
                'percent': process.memory_percent(),
                'available': psutil.virtual_memory().available,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            return {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'error': str(e)
            }
    
    def run_tests(self) -> Dict[str, Any]:
        """Execute the test suite with enhanced reporting."""
        self.logger.info("Starting test execution...")
        
        # Build pytest command
        pytest_cmd = [
            sys.executable, '-m', 'pytest',
            str(self.test_dir / self.config['test_file']),
            f'--html={self.results["html_report"]}',
            '--self-contained-html',
            '--json-report',
            f'--json-report-file={self.results["json_report"]}',
            '--json-report-summary',
            f'--cov=utilities.network.network_connectivity_complex.core.security_validator',
            f'--cov-report=html:{self.results["coverage_html"]}',
            f'--cov-report=json:{self.results["coverage_json"]}',
            f'--cov-report=xml:{self.results["coverage_xml"]}',
            '--cov-report=term-missing:skip-covered',
            '--cov-fail-under=80',
            f'--junit-xml={self.results["junit_xml"]}',
            '--durations=10',
            '--durations-min=1.0',
            '-v',
            '--tb=short',
            '--strict-markers',
            '--strict-config',
            '--disable-warnings'
        ]
        
        # Add configuration file if it exists
        config_file = self.test_dir / self.config['pytest_config']
        if config_file.exists():
            pytest_cmd.extend(['-c', str(config_file)])
        
        # Execute tests
        start_time = time.time()
        memory_before = self.monitor_memory_usage()
        
        try:
            self.logger.info(f"Executing command: {' '.join(pytest_cmd)}")
            result = subprocess.run(
                pytest_cmd,
                cwd=self.test_dir,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            
            end_time = time.time()
            memory_after = self.monitor_memory_usage()
            
            execution_info = {
                'command': ' '.join(pytest_cmd),
                'return_code': result.returncode,
                'execution_time': end_time - start_time,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'memory_before': memory_before,
                'memory_after': memory_after,
                'memory_peak': max(
                    memory_before.get('rss', 0), 
                    memory_after.get('rss', 0)
                ) if 'error' not in memory_before and 'error' not in memory_after else 0
            }
            
            self.logger.info(f"Test execution completed in {execution_info['execution_time']:.2f} seconds")
            self.logger.info(f"Return code: {result.returncode}")
            
            if result.returncode == 0:
                self.logger.info("✓ All tests passed!")
            else:
                self.logger.warning(f"⚠ Tests completed with return code: {result.returncode}")
            
            return execution_info
            
        except subprocess.TimeoutExpired:
            self.logger.error("Test execution timed out after 10 minutes")
            return {
                'command': ' '.join(pytest_cmd),
                'return_code': -1,
                'execution_time': 600,
                'stdout': '',
                'stderr': 'Test execution timed out',
                'memory_before': memory_before,
                'memory_after': self.monitor_memory_usage(),
                'error': 'timeout'
            }
        
        except Exception as e:
            self.logger.error(f"Error executing tests: {e}")
            return {
                'command': ' '.join(pytest_cmd),
                'return_code': -1,
                'execution_time': time.time() - start_time,
                'stdout': '',
                'stderr': str(e),
                'memory_before': memory_before,
                'memory_after': self.monitor_memory_usage(),
                'error': str(e)
            }
    
    def analyze_results(self, execution_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze test results and generate summary."""
        self.logger.info("Analyzing test results...")
        
        analysis = {
            'execution_summary': execution_info,
            'system_info': self.get_system_info(),
            'file_results': {},
            'performance_metrics': {},
            'coverage_analysis': {},
            'recommendations': []
        }
        
        # Analyze JSON report if available
        json_report_path = self.test_dir / self.results['json_report']
        if json_report_path.exists():
            try:
                with open(json_report_path, 'r') as f:
                    json_data = json.load(f)
                    
                analysis['test_results'] = {
                    'summary': json_data.get('summary', {}),
                    'total_duration': json_data.get('duration', 0),
                    'test_count': len(json_data.get('tests', [])),
                    'passed': len([t for t in json_data.get('tests', []) if t.get('outcome') == 'passed']),
                    'failed': len([t for t in json_data.get('tests', []) if t.get('outcome') == 'failed']),
                    'skipped': len([t for t in json_data.get('tests', []) if t.get('outcome') == 'skipped'])
                }
                
                # Analyze slow tests
                slow_tests = [
                    t for t in json_data.get('tests', [])
                    if t.get('duration', 0) > 1.0
                ]
                if slow_tests:
                    analysis['performance_metrics']['slow_tests'] = [
                        {
                            'name': t.get('nodeid', ''),
                            'duration': t.get('duration', 0)
                        }
                        for t in sorted(slow_tests, key=lambda x: x.get('duration', 0), reverse=True)
                    ]
                
            except Exception as e:
                self.logger.warning(f"Could not analyze JSON report: {e}")
        
        # Analyze coverage if available
        coverage_json_path = self.test_dir / self.results['coverage_json']
        if coverage_json_path.exists():
            try:
                with open(coverage_json_path, 'r') as f:
                    coverage_data = json.load(f)
                    
                analysis['coverage_analysis'] = {
                    'line_coverage': coverage_data.get('totals', {}).get('percent_covered', 0),
                    'branch_coverage': coverage_data.get('totals', {}).get('percent_covered_display', '0%'),
                    'missing_lines': coverage_data.get('totals', {}).get('missing_lines', 0),
                    'files_analyzed': len(coverage_data.get('files', {}))
                }
                
            except Exception as e:
                self.logger.warning(f"Could not analyze coverage report: {e}")
        
        # Generate recommendations
        if analysis.get('coverage_analysis', {}).get('line_coverage', 0) < 90:
            analysis['recommendations'].append("Consider increasing test coverage to above 90%")
        
        if execution_info.get('execution_time', 0) > 120:
            analysis['recommendations'].append("Test execution time is high - consider optimizing slow tests")
        
        if execution_info.get('memory_peak', 0) > 100 * 1024 * 1024:  # 100MB
            analysis['recommendations'].append("High memory usage detected - review memory-intensive tests")
        
        return analysis
    
    def generate_summary_report(self, analysis: Dict[str, Any]):
        """Generate a comprehensive summary report."""
        self.logger.info("Generating summary report...")
        
        # Save detailed analysis
        summary_path = self.test_dir / self.results['execution_summary']
        with open(summary_path, 'w') as f:
            json.dump(analysis, f, indent=2, default=str)
        
        # Generate human-readable summary
        execution_time = analysis['execution_summary'].get('execution_time', 0)
        test_results = analysis.get('test_results', {})
        coverage = analysis.get('coverage_analysis', {})
        
        summary_text = f"""
Security Validator Test Execution Summary
==========================================
Generated: {datetime.now(timezone.utc).isoformat()}

EXECUTION DETAILS:
- Start Time: {analysis['system_info']['timestamp']}
- Execution Time: {execution_time:.2f} seconds
- Return Code: {analysis['execution_summary'].get('return_code', 'Unknown')}
- Python Version: {analysis['system_info']['python_version']}

TEST RESULTS:
- Total Tests: {test_results.get('test_count', 0)}
- Passed: {test_results.get('passed', 0)}
- Failed: {test_results.get('failed', 0)}
- Skipped: {test_results.get('skipped', 0)}

COVERAGE ANALYSIS:
- Line Coverage: {coverage.get('line_coverage', 0):.2f}%
- Files Analyzed: {coverage.get('files_analyzed', 0)}

PERFORMANCE METRICS:
- Average Test Duration: {execution_time / max(test_results.get('test_count', 1), 1):.3f}s
- Memory Peak: {analysis['execution_summary'].get('memory_peak', 0) / (1024*1024):.2f} MB

RECOMMENDATIONS:
"""
        
        for rec in analysis.get('recommendations', []):
            summary_text += f"- {rec}\n"
        
        if not analysis.get('recommendations'):
            summary_text += "- No specific recommendations - tests executed successfully\n"
        
        summary_text += f"""
RESULT FILES GENERATED:
- HTML Report: {self.results['html_report']}
- JSON Report: {self.results['json_report']}
- Coverage HTML: {self.results['coverage_html']}/
- Coverage JSON: {self.results['coverage_json']}
- JUnit XML: {self.results['junit_xml']}
- Execution Summary: {self.results['execution_summary']}

For detailed results, open the HTML report: {self.results['html_report']}
"""
        
        # Save text summary
        text_summary_path = self.test_dir / f'result_{self.base_name}_summary.txt'
        with open(text_summary_path, 'w') as f:
            f.write(summary_text)
        
        print(summary_text)
        self.logger.info(f"Summary report saved to: {text_summary_path}")
    
    def run(self):
        """Execute the complete test workflow."""
        try:
            self.logger.info("=" * 60)
            self.logger.info("Security Validator Enhanced Test Runner")
            self.logger.info("=" * 60)
            
            # Check dependencies
            if not self.check_dependencies():
                return 1
            
            # Prepare environment
            if not self.prepare_test_environment():
                return 1
            
            # Run tests
            execution_info = self.run_tests()
            
            # Analyze results
            analysis = self.analyze_results(execution_info)
            
            # Generate reports
            self.generate_summary_report(analysis)
            
            # Return appropriate exit code
            return execution_info.get('return_code', 0)
            
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            return 1
        
        finally:
            end_time = datetime.now(timezone.utc)
            total_time = (end_time - self.start_time).total_seconds()
            self.logger.info(f"Total workflow execution time: {total_time:.2f} seconds")


def main():
    """Main entry point."""
    runner = SecurityValidatorTestRunner()
    exit_code = runner.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()