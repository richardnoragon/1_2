#!/usr/bin/env python3#!/usr/bin/env python3#!/usr/bin/env python3

"""

Enhanced Editor Test Runner Script""""""



Executes comprehensive unit tests for enhanced_editor.py with standardized output.Enhanced Editor Test Runner ScriptEnhanced Editor Test Runner

Generates detailed HTML and JSON reports with execution timestamp and coverage.

==========================

Created: 2025-08-31

Target: enhanced_editor.pyExecutes comprehensive unit tests for enhanced_editor.py with standardized output generation.

"""

Generates detailed HTML and JSON reports with execution timestamp and coverage analysis.Comprehensive test execution script for enhanced_editor.py

import os

import sysGenerates detailed HTML and JSON reports with coverage analysis.

import subprocess

import jsonCreated: 2025-08-31

import time

from datetime import datetimeTarget: enhanced_editor.pyExecution Date: 2025-08-31

from pathlib import Path

"""Target File: enhanced_editor.py



def setup_environment():Framework: pytest

    """Setup test environment and paths."""

    current_dir = Path(__file__).parentimport os

    src_dir = current_dir / "src"

import sysFeatures:

    if str(src_dir) not in sys.path:

        sys.path.insert(0, str(src_dir))import subprocess- Detailed HTML test reports



    os.environ["PYTHONPATH"] = str(current_dir)import json- JSON test result exports

    os.environ["TEST_MODE"] = "1"

    os.environ["QT_QPA_PLATFORM"] = "offscreen"import time- Coverage analysis with multiple formats



from datetime import datetime- JUnit XML for CI/CD integration

def get_python_executable():

    """Get the correct Python executable path."""from pathlib import Path- Execution timing and performance metrics

    venv_python = Path("venv/Scripts/python.exe")

    if venv_python.exists():- Standardized output formatting

        return str(venv_python)

    return sys.executable"""



def setup_environment():

def run_tests():

    """Run the comprehensive test suite."""    """Setup test environment and paths."""import datetime

    setup_environment()

    # Add current directory to Python pathimport json

    test_file = "tests/unit/test_enhanced_editor_2025-08-31.py"

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")    current_dir = Path(__file__).parentimport os



    print("=" * 80)    src_dir = current_dir / "src"import subprocess

    print("Enhanced Editor Test Suite Execution")

    print(f"Execution Timestamp: {timestamp}")    import sys

    print("Target Module: enhanced_editor.py")

    print(f"Test File: {test_file}")    if str(src_dir) not in sys.path:from pathlib import Path

    print("=" * 80)

    print()        sys.path.insert(0, str(src_dir))from typing import Any, Dict, List



    os.makedirs("tests/unit", exist_ok=True)    



    python_exe = get_python_executable()    # Set environment variables



    pytest_cmd = [    os.environ["PYTHONPATH"] = str(current_dir)class EnhancedEditorTestRunner:

        python_exe, "-m", "pytest",

        test_file,    os.environ["TEST_MODE"] = "1"    """Test runner for enhanced_editor.py with comprehensive reporting."""

        "-v",

        "--tb=short",    os.environ["QT_QPA_PLATFORM"] = "offscreen"  # For headless Qt testing    

        "--html=tests/unit/result_enhanced_editor_2025-08-31.html",

        "--self-contained-html",    def __init__(self):

        "--json-report",

        "--json-report-file=tests/unit/result_enhanced_editor_2025-08-31.json",        self.test_date = "2025-08-31"

        "--cov=src.utilities.file_operations.enhanced_editor",

        "--cov-report=html:tests/unit/result_enhanced_editor_coverage_2025-08-31",def get_python_executable():        self.target_file = "enhanced_editor"

        "--cov-report=term-missing",

        "--cov-report=json:tests/unit/result_enhanced_editor_coverage_2025-08-31.json",    """Get the correct Python executable path."""        self.test_file = f"test_{self.target_file}_{self.test_date}.py"

        "--cov-branch",

        "--maxfail=5"    venv_python = Path("venv/Scripts/python.exe")        self.config_file = f"pytest_{self.target_file}_{self.test_date}.ini"

    ]

    if venv_python.exists():        

    print("Executing test command:")

    print(" ".join(pytest_cmd))        return str(venv_python)        # Result file names

    print()

    return sys.executable        self.html_report = f"result_{self.target_file}_{self.test_date}.html"

    start_time = time.time()

        self.json_report = f"result_{self.target_file}_{self.test_date}.json"

    try:

        result = subprocess.run(        self.coverage_html = f"result_{self.target_file}_coverage_{self.test_date}"

            pytest_cmd,

            capture_output=True,def run_tests():        self.coverage_json = f"result_{self.target_file}_coverage_{self.test_date}.json"

            text=True,

            cwd=os.getcwd(),    """Run the comprehensive test suite."""        self.coverage_xml = f"result_{self.target_file}_coverage_{self.test_date}.xml"

            check=False

        )    setup_environment()        self.junit_xml = f"result_{self.target_file}_junit_{self.test_date}.xml"



        end_time = time.time()            self.summary_json = f"result_{self.target_file}_summary_{self.test_date}.json"

        execution_time = end_time - start_time

    test_file = "tests/unit/test_enhanced_editor_2025-08-31.py"        

        print("STDOUT:")

        print(result.stdout)    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")        # Execution tracking

        print("\nSTDERR:")

        print(result.stderr)            self.start_time = None



        generate_summary_report(result, execution_time, timestamp)    print(f"=" * 80)        self.end_time = None



        return result.returncode    print(f"Enhanced Editor Test Suite Execution")        self.execution_log = []



    except OSError as e:    print(f"Execution Timestamp: {timestamp}")        

        print(f"Error running tests: {e}")

        return 1    print(f"Target Module: enhanced_editor.py")    def log_message(self, message: str, level: str = "INFO"):



    print(f"Test File: {test_file}")        """Log a message with timestamp."""

def generate_summary_report(result, execution_time, timestamp):

    """Generate standardized test summary report."""    print(f"=" * 80)        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")



    json_report_path = "tests/unit/result_enhanced_editor_2025-08-31.json"    print()        log_entry = f"[{timestamp}] {level}: {message}"

    test_stats = {

        "total": 0,            print(log_entry)

        "passed": 0,

        "failed": 0,    # Ensure test directory exists        self.execution_log.append(log_entry)

        "skipped": 0,

        "errors": 0,    os.makedirs("tests/unit", exist_ok=True)    

        "duration": execution_time

    }        def check_dependencies(self) -> bool:



    if os.path.exists(json_report_path):    # Get Python executable        """Check if required dependencies are installed."""

        try:

            with open(json_report_path, 'r', encoding='utf-8') as f:    python_exe = get_python_executable()        self.log_message("Checking test dependencies...")

                json_data = json.load(f)

                summary = json_data.get('summary', {})            

                test_stats.update({

                    "total": summary.get('total', 0),    # Prepare pytest command        required_packages = [

                    "passed": summary.get('passed', 0),

                    "failed": summary.get('failed', 0),    pytest_cmd = [            'pytest',

                    "skipped": summary.get('skipped', 0),

                    "errors": summary.get('error', 0)        python_exe, "-m", "pytest",            'pytest-html',

                })

        except (IOError, json.JSONDecodeError) as e:        test_file,            'pytest-json-report',

            print(f"Warning: Could not parse JSON report: {e}")

        "-v",            'pytest-cov',

    total_tests = test_stats['total']

    passed_tests = test_stats['passed']        "--tb=short",            'coverage'

    success_rate = (passed_tests / max(total_tests, 1)) * 100 if total_tests > 0 else 0

        "--html=tests/unit/result_enhanced_editor_2025-08-31.html",        ]

    summary_report = {

        "test_execution_summary": {        "--self-contained-html",        

            "execution_timestamp": timestamp,

            "test_file": "test_enhanced_editor_2025-08-31.py",        "--json-report",        missing_packages = []

            "target_module": "enhanced_editor.py",

            "test_framework": "pytest",        "--json-report-file=tests/unit/result_enhanced_editor_2025-08-31.json",        for package in required_packages:

            "python_version": sys.version,

            "execution_environment": "automated_test_suite"        "--cov=src.utilities.file_operations.enhanced_editor",            try:

        },

        "test_results": {        "--cov-report=html:tests/unit/result_enhanced_editor_coverage_2025-08-31",                __import__(package.replace('-', '_'))

            "total_tests": test_stats['total'],

            "passed": test_stats['passed'],        "--cov-report=term-missing",            except ImportError:

            "failed": test_stats['failed'],

            "skipped": test_stats['skipped'],        "--cov-report=json:tests/unit/result_enhanced_editor_coverage_2025-08-31.json",                missing_packages.append(package)

            "errors": test_stats['errors'],

            "success_rate_percentage": f"{success_rate:.2f}%",        "--cov-branch",        

            "execution_time_seconds": f"{execution_time:.2f}"

        },        "--maxfail=5"        if missing_packages:

        "test_categories_covered": [

            "DocumentType enumeration validation",    ]            self.log_message(f"Missing required packages: {missing_packages}", "ERROR")

            "SearchOptions dataclass functionality",

            "EditorSettings configuration management",                self.log_message("Install with: pip install " + " ".join(missing_packages), "INFO")

            "SyntaxHighlighter language processing",

            "DocumentManager document lifecycle",    print("Executing test command:")            return False

            "SearchDialog user interface components",

            "TextEditor widget functionality",    print(" ".join(pytest_cmd))        

            "LineNumberArea display components",

            "EnhancedEditor main application logic",    print()        self.log_message("All dependencies are available", "SUCCESS")

            "PreferencesDialog settings management",

            "Error handling and edge cases",            return True

            "Integration workflows and end-to-end testing"

        ],    # Record start time    

        "coverage_analysis": {

            "html_report": "result_enhanced_editor_coverage_2025-08-31/index.html",    start_time = time.time()    def setup_test_environment(self):

            "json_report": "result_enhanced_editor_coverage_2025-08-31.json",

            "coverage_requirement": "80% minimum"            """Setup the test environment."""

        },

        "output_files": {    try:        self.log_message("Setting up test environment...")

            "html_test_report": "result_enhanced_editor_2025-08-31.html",

            "json_test_report": "result_enhanced_editor_2025-08-31.json",        # Run tests        

            "coverage_html": "result_enhanced_editor_coverage_2025-08-31/",

            "coverage_json": "result_enhanced_editor_coverage_2025-08-31.json",        result = subprocess.run(        # Ensure we're in the correct directory

            "summary_report": "result_enhanced_editor_summary_2025-08-31.json"

        },            pytest_cmd,        current_dir = Path.cwd()

        "test_status": "PASSED" if result.returncode == 0 else "FAILED",

        "return_code": result.returncode            capture_output=True,        if not (current_dir / "tests" / "unit").exists():

    }

            text=True,            self.log_message("Creating tests/unit directory structure...", "INFO")

    summary_path = "tests/unit/result_enhanced_editor_summary_2025-08-31.json"

    try:            cwd=os.getcwd()            (current_dir / "tests" / "unit").mkdir(parents=True, exist_ok=True)

        with open(summary_path, 'w', encoding='utf-8') as f:

            json.dump(summary_report, f, indent=2)        )        

        print(f"\nSummary report saved to: {summary_path}")

    except IOError as e:                # Check if test files exist

        print(f"Warning: Could not save summary report: {e}")

        # Record end time        test_file_path = Path("tests/unit") / self.test_file

    print("\n" + "=" * 80)

    print("TEST EXECUTION SUMMARY")        end_time = time.time()        config_file_path = Path("tests/unit") / self.config_file

    print("=" * 80)

    print(f"Timestamp: {timestamp}")        execution_time = end_time - start_time        

    print(f"Total Tests: {test_stats['total']}")

    print(f"Passed: {test_stats['passed']}")                if not test_file_path.exists():

    print(f"Failed: {test_stats['failed']}")

    print(f"Skipped: {test_stats['skipped']}")        # Print test output            self.log_message(f"Test file not found: {test_file_path}", "ERROR")

    print(f"Errors: {test_stats['errors']}")

    print(f"Success Rate: {success_rate:.2f}%")        print("STDOUT:")            return False

    print(f"Execution Time: {execution_time:.2f} seconds")

    status = 'PASSED' if result.returncode == 0 else 'FAILED'        print(result.stdout)        

    print(f"Status: {status}")

    print("=" * 80)        print("\nSTDERR:")        if not config_file_path.exists():



    print("\nGenerated Test Output Files:")        print(result.stderr)            self.log_message(f"Config file not found: {config_file_path}", "WARNING")

    output_files = [

        "tests/unit/result_enhanced_editor_2025-08-31.html",                

        "tests/unit/result_enhanced_editor_2025-08-31.json",

        "tests/unit/result_enhanced_editor_coverage_2025-08-31/index.html",        # Generate summary report        # Setup Python path

        "tests/unit/result_enhanced_editor_coverage_2025-08-31.json",

        "tests/unit/result_enhanced_editor_summary_2025-08-31.json"        generate_summary_report(result, execution_time, timestamp)        src_path = current_dir / "src"

    ]

                if src_path.exists() and str(src_path) not in sys.path:

    for file_path in output_files:

        if os.path.exists(file_path):        return result.returncode            sys.path.insert(0, str(src_path))

            print(f"✓ {file_path}")

        else:                    self.log_message(f"Added to Python path: {src_path}", "INFO")

            print(f"✗ {file_path} (not generated)")

    except Exception as e:        

    print("\n" + "=" * 80)

        print(f"Error running tests: {e}")        self.log_message("Test environment setup complete", "SUCCESS")



def main():        return 1        return True

    """Main execution function."""

    print("Enhanced Editor Comprehensive Test Suite")    

    print("========================================")

    def run_tests(self) -> Dict[str, Any]:

    test_file = "tests/unit/test_enhanced_editor_2025-08-31.py"

    if not os.path.exists(test_file):def generate_summary_report(result, execution_time, timestamp):        """Execute the test suite."""

        print(f"Error: Test file {test_file} not found!")

        return 1    """Generate standardized test summary report."""        self.log_message("Starting test execution...")



    return run_tests()            self.start_time = datetime.datetime.now()



    # Parse JSON report if available        

if __name__ == "__main__":

    sys.exit(main())    json_report_path = "tests/unit/result_enhanced_editor_2025-08-31.json"        # Change to project root directory

    test_stats = {        os.chdir(Path(__file__).parent.parent.parent)

        "total": 0,        

        "passed": 0,        # Build pytest command

        "failed": 0,        cmd = [

        "skipped": 0,            sys.executable, "-m", "pytest",

        "errors": 0,            f"tests/unit/{self.test_file}",

        "duration": execution_time            "-c", f"tests/unit/{self.config_file}",

    }            "--verbose",

                "--tb=short",

    if os.path.exists(json_report_path):            f"--html=tests/unit/{self.html_report}",

        try:            "--self-contained-html",

            with open(json_report_path, 'r') as f:            "--json-report",

                json_data = json.load(f)            f"--json-report-file=tests/unit/{self.json_report}",

                summary = json_data.get('summary', {})            f"--cov=src.utilities.file_operations.enhanced_editor.enhanced_editor",

                test_stats.update({            f"--cov-report=html:tests/unit/{self.coverage_html}",

                    "total": summary.get('total', 0),            f"--cov-report=json:tests/unit/{self.coverage_json}",

                    "passed": summary.get('passed', 0),            f"--cov-report=xml:tests/unit/{self.coverage_xml}",

                    "failed": summary.get('failed', 0),            "--cov-report=term-missing",

                    "skipped": summary.get('skipped', 0),            f"--junit-xml=tests/unit/{self.junit_xml}",

                    "errors": summary.get('error', 0)            "--durations=10"

                })        ]

        except Exception as e:        

            print(f"Warning: Could not parse JSON report: {e}")        self.log_message(f"Executing command: {' '.join(cmd)}")

            

    # Calculate success rate        # Execute tests

    total_tests = test_stats['total']        try:

    passed_tests = test_stats['passed']            result = subprocess.run(

    success_rate = (passed_tests / max(total_tests, 1)) * 100 if total_tests > 0 else 0                cmd,

                    capture_output=True,

    # Create comprehensive summary                text=True,

    summary_report = {                timeout=300  # 5 minute timeout

        "test_execution_summary": {            )

            "execution_timestamp": timestamp,            

            "test_file": "test_enhanced_editor_2025-08-31.py",            self.end_time = datetime.datetime.now()

            "target_module": "enhanced_editor.py",            execution_time = (self.end_time - self.start_time).total_seconds()

            "test_framework": "pytest",            

            "python_version": sys.version,            self.log_message(f"Test execution completed in {execution_time:.2f} seconds")

            "execution_environment": "automated_test_suite"            self.log_message(f"Return code: {result.returncode}")

        },            

        "test_results": {            if result.stdout:

            "total_tests": test_stats['total'],                self.log_message("STDOUT:", "DEBUG")

            "passed": test_stats['passed'],                print(result.stdout)

            "failed": test_stats['failed'],            

            "skipped": test_stats['skipped'],            if result.stderr:

            "errors": test_stats['errors'],                self.log_message("STDERR:", "DEBUG")

            "success_rate_percentage": f"{success_rate:.2f}%",                print(result.stderr)

            "execution_time_seconds": f"{execution_time:.2f}"            

        },            return {

        "test_categories_covered": [                'return_code': result.returncode,

            "DocumentType enumeration validation",                'stdout': result.stdout,

            "SearchOptions dataclass functionality",                'stderr': result.stderr,

            "EditorSettings configuration management",                'execution_time': execution_time,

            "SyntaxHighlighter language processing",                'success': result.returncode == 0

            "DocumentManager document lifecycle",            }

            "SearchDialog user interface components",            

            "TextEditor widget functionality",        except subprocess.TimeoutExpired:

            "LineNumberArea display components",            self.log_message("Test execution timed out", "ERROR")

            "EnhancedEditor main application logic",            return {

            "PreferencesDialog settings management",                'return_code': -1,

            "Error handling and edge cases",                'stdout': '',

            "Integration workflows and end-to-end testing"                'stderr': 'Test execution timed out',

        ],                'execution_time': 300,

        "coverage_analysis": {                'success': False

            "html_report": "result_enhanced_editor_coverage_2025-08-31/index.html",            }

            "json_report": "result_enhanced_editor_coverage_2025-08-31.json",        except Exception as e:

            "coverage_requirement": "80% minimum"            self.log_message(f"Error during test execution: {e}", "ERROR")

        },            return {

        "output_files": {                'return_code': -2,

            "html_test_report": "result_enhanced_editor_2025-08-31.html",                'stdout': '',

            "json_test_report": "result_enhanced_editor_2025-08-31.json",                'stderr': str(e),

            "coverage_html": "result_enhanced_editor_coverage_2025-08-31/",                'execution_time': 0,

            "coverage_json": "result_enhanced_editor_coverage_2025-08-31.json",                'success': False

            "summary_report": "result_enhanced_editor_summary_2025-08-31.json"            }

        },    

        "test_status": "PASSED" if result.returncode == 0 else "FAILED",    def parse_test_results(self) -> Dict[str, Any]:

        "return_code": result.returncode        """Parse and analyze test results."""

    }        self.log_message("Parsing test results...")

            

    # Save summary report        results = {

    summary_path = "tests/unit/result_enhanced_editor_summary_2025-08-31.json"            'timestamp': datetime.datetime.now().isoformat(),

    try:            'test_date': self.test_date,

        with open(summary_path, 'w') as f:            'target_file': self.target_file,

            json.dump(summary_report, f, indent=2)            'html_report_available': False,

        print(f"\nSummary report saved to: {summary_path}")            'json_report_available': False,

    except Exception as e:            'coverage_report_available': False,

        print(f"Warning: Could not save summary report: {e}")            'junit_report_available': False,

                'test_summary': {},

    # Print summary to console            'coverage_summary': {},

    print("\n" + "=" * 80)            'errors': []

    print("TEST EXECUTION SUMMARY")        }

    print("=" * 80)        

    print(f"Timestamp: {timestamp}")        # Check for HTML report

    print(f"Total Tests: {test_stats['total']}")        html_path = Path(f"tests/unit/{self.html_report}")

    print(f"Passed: {test_stats['passed']}")        if html_path.exists():

    print(f"Failed: {test_stats['failed']}")            results['html_report_available'] = True

    print(f"Skipped: {test_stats['skipped']}")            results['html_report_path'] = str(html_path)

    print(f"Errors: {test_stats['errors']}")            self.log_message(f"HTML report generated: {html_path}")

    print(f"Success Rate: {success_rate:.2f}%")        else:

    print(f"Execution Time: {execution_time:.2f} seconds")            results['errors'].append(f"HTML report not found: {html_path}")

    print(f"Status: {'PASSED' if result.returncode == 0 else 'FAILED'}")        

    print("=" * 80)        # Parse JSON report

            json_path = Path(f"tests/unit/{self.json_report}")

    # List generated files        if json_path.exists():

    print("\nGenerated Test Output Files:")            try:

    output_files = [                with open(json_path, 'r') as f:

        "tests/unit/result_enhanced_editor_2025-08-31.html",                    json_data = json.load(f)

        "tests/unit/result_enhanced_editor_2025-08-31.json",                

        "tests/unit/result_enhanced_editor_coverage_2025-08-31/index.html",                results['json_report_available'] = True

        "tests/unit/result_enhanced_editor_coverage_2025-08-31.json",                results['json_report_path'] = str(json_path)

        "tests/unit/result_enhanced_editor_summary_2025-08-31.json"                

    ]                # Extract test summary

                    summary = json_data.get('summary', {})

    for file_path in output_files:                results['test_summary'] = {

        if os.path.exists(file_path):                    'total': summary.get('total', 0),

            print(f"✓ {file_path}")                    'passed': summary.get('passed', 0),

        else:                    'failed': summary.get('failed', 0),

            print(f"✗ {file_path} (not generated)")                    'skipped': summary.get('skipped', 0),

                        'error': summary.get('error', 0),

    print("\n" + "=" * 80)                    'duration': summary.get('duration', 0)

                }

                

def main():                self.log_message(f"Test summary: {results['test_summary']}")

    """Main execution function."""                

    print("Enhanced Editor Comprehensive Test Suite")            except Exception as e:

    print("========================================")                results['errors'].append(f"Error parsing JSON report: {e}")

            else:

    # Check if test file exists            results['errors'].append(f"JSON report not found: {json_path}")

    test_file = "tests/unit/test_enhanced_editor_2025-08-31.py"        

    if not os.path.exists(test_file):        # Parse coverage report

        print(f"Error: Test file {test_file} not found!")        coverage_json_path = Path(f"tests/unit/{self.coverage_json}")

        return 1        if coverage_json_path.exists():

                try:

    # Run tests                with open(coverage_json_path, 'r') as f:

    return run_tests()                    coverage_data = json.load(f)

                

                results['coverage_report_available'] = True

if __name__ == "__main__":                results['coverage_json_path'] = str(coverage_json_path)

    sys.exit(main())                
                # Extract coverage summary
                totals = coverage_data.get('totals', {})
                results['coverage_summary'] = {
                    'covered_lines': totals.get('covered_lines', 0),
                    'num_statements': totals.get('num_statements', 0),
                    'percent_covered': totals.get('percent_covered', 0),
                    'missing_lines': totals.get('missing_lines', 0),
                    'excluded_lines': totals.get('excluded_lines', 0)
                }
                
                self.log_message(f"Coverage summary: {results['coverage_summary']}")
                
            except Exception as e:
                results['errors'].append(f"Error parsing coverage report: {e}")
        else:
            results['errors'].append(f"Coverage JSON report not found: {coverage_json_path}")
        
        # Check for JUnit XML
        junit_path = Path(f"tests/unit/{self.junit_xml}")
        if junit_path.exists():
            results['junit_report_available'] = True
            results['junit_report_path'] = str(junit_path)
            self.log_message(f"JUnit XML report generated: {junit_path}")
        else:
            results['errors'].append(f"JUnit XML report not found: {junit_path}")
        
        return results
    
    def generate_summary_report(self, test_results: Dict[str, Any], 
                               parsed_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a comprehensive summary report."""
        self.log_message("Generating summary report...")
        
        summary = {
            'metadata': {
                'test_execution_timestamp': datetime.datetime.now().isoformat(),
                'test_date': self.test_date,
                'target_file': f"{self.target_file}.py",
                'test_framework': 'pytest',
                'execution_duration': test_results.get('execution_time', 0),
                'success': test_results.get('success', False)
            },
            'test_results': {
                'return_code': test_results.get('return_code', -1),
                'summary': parsed_results.get('test_summary', {}),
                'reports_generated': {
                    'html_report': parsed_results.get('html_report_available', False),
                    'json_report': parsed_results.get('json_report_available', False),
                    'coverage_report': parsed_results.get('coverage_report_available', False),
                    'junit_report': parsed_results.get('junit_report_available', False)
                },
                'file_paths': {
                    'html_report': parsed_results.get('html_report_path', ''),
                    'json_report': parsed_results.get('json_report_path', ''),
                    'coverage_json': parsed_results.get('coverage_json_path', ''),
                    'junit_xml': parsed_results.get('junit_report_path', '')
                }
            },
            'coverage_analysis': parsed_results.get('coverage_summary', {}),
            'execution_log': self.execution_log,
            'errors': parsed_results.get('errors', []),
            'recommendations': self._generate_recommendations(parsed_results)
        }
        
        # Save summary to file
        summary_path = Path(f"tests/unit/{self.summary_json}")
        try:
            with open(summary_path, 'w') as f:
                json.dump(summary, f, indent=2)
            
            self.log_message(f"Summary report saved: {summary_path}")
            summary['summary_report_path'] = str(summary_path)
            
        except Exception as e:
            self.log_message(f"Error saving summary report: {e}", "ERROR")
            summary['errors'].append(f"Could not save summary report: {e}")
        
        return summary
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on test results."""
        recommendations = []
        
        # Test coverage recommendations
        coverage = results.get('coverage_summary', {})
        percent_covered = coverage.get('percent_covered', 0)
        
        if percent_covered < 80:
            recommendations.append(
                f"Test coverage is {percent_covered:.1f}%. Consider adding more tests to reach 80%+ coverage."
            )
        elif percent_covered >= 95:
            recommendations.append(
                f"Excellent test coverage: {percent_covered:.1f}%!"
            )
        
        # Test result recommendations
        test_summary = results.get('test_summary', {})
        failed_tests = test_summary.get('failed', 0)
        error_tests = test_summary.get('error', 0)
        
        if failed_tests > 0:
            recommendations.append(
                f"{failed_tests} test(s) failed. Review the HTML report for details."
            )
        
        if error_tests > 0:
            recommendations.append(
                f"{error_tests} test(s) had errors. Check test setup and imports."
            )
        
        # Missing reports recommendations
        if not results.get('html_report_available', False):
            recommendations.append("HTML report not generated. Check pytest-html installation.")
        
        if not results.get('coverage_report_available', False):
            recommendations.append("Coverage report not generated. Check pytest-cov installation.")
        
        # General recommendations
        if not recommendations:
            recommendations.append("All tests passed successfully with good coverage!")
        
        return recommendations
    
    def print_final_summary(self, summary: Dict[str, Any]):
        """Print a formatted final summary."""
        print("\n" + "="*80)
        print("ENHANCED EDITOR TEST EXECUTION SUMMARY")
        print("="*80)
        
        metadata = summary.get('metadata', {})
        print(f"Execution Timestamp: {metadata.get('test_execution_timestamp', 'N/A')}")
        print(f"Target File: {metadata.get('target_file', 'N/A')}")
        print(f"Test Framework: {metadata.get('test_framework', 'N/A')}")
        print(f"Execution Duration: {metadata.get('execution_duration', 0):.2f} seconds")
        print(f"Overall Success: {'✓' if metadata.get('success', False) else '✗'}")
        
        print("\nTEST RESULTS:")
        test_summary = summary.get('test_results', {}).get('summary', {})
        print(f"  Total Tests: {test_summary.get('total', 0)}")
        print(f"  Passed: {test_summary.get('passed', 0)}")
        print(f"  Failed: {test_summary.get('failed', 0)}")
        print(f"  Skipped: {test_summary.get('skipped', 0)}")
        print(f"  Errors: {test_summary.get('error', 0)}")
        
        print("\nCOVERAGE ANALYSIS:")
        coverage = summary.get('coverage_analysis', {})
        print(f"  Coverage Percentage: {coverage.get('percent_covered', 0):.1f}%")
        print(f"  Covered Lines: {coverage.get('covered_lines', 0)}")
        print(f"  Total Statements: {coverage.get('num_statements', 0)}")
        print(f"  Missing Lines: {coverage.get('missing_lines', 0)}")
        
        print("\nGENERATED REPORTS:")
        reports = summary.get('test_results', {}).get('reports_generated', {})
        file_paths = summary.get('test_results', {}).get('file_paths', {})
        
        for report_type, generated in reports.items():
            status = "✓" if generated else "✗"
            print(f"  {report_type.replace('_', ' ').title()}: {status}")
            if generated and report_type in file_paths:
                print(f"    Path: {file_paths[report_type]}")
        
        print("\nRECOMMENDATIONS:")
        for recommendation in summary.get('recommendations', []):
            print(f"  • {recommendation}")
        
        errors = summary.get('errors', [])
        if errors:
            print("\nERRORS:")
            for error in errors:
                print(f"  • {error}")
        
        print("\n" + "="*80)
    
    def run(self) -> Dict[str, Any]:
        """Execute the complete test suite with reporting."""
        self.log_message("Starting Enhanced Editor Test Suite")
        
        # Check dependencies
        if not self.check_dependencies():
            return {'success': False, 'error': 'Missing dependencies'}
        
        # Setup environment
        if not self.setup_test_environment():
            return {'success': False, 'error': 'Environment setup failed'}
        
        # Run tests
        test_results = self.run_tests()
        
        # Parse results
        parsed_results = self.parse_test_results()
        
        # Generate summary
        summary = self.generate_summary_report(test_results, parsed_results)
        
        # Print final summary
        self.print_final_summary(summary)
        
        return summary


def main():
    """Main function to run the test suite."""
    runner = EnhancedEditorTestRunner()
    
    try:
        summary = runner.run()
        
        # Exit with appropriate code
        if summary.get('metadata', {}).get('success', False):
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nTest execution interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()