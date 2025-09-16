#!/usr/bin/env python3
"""
Test Runner for merg.py Unit Tests
Generated on: August 24, 2025
Target: src.utilities.pdf_tools.pdf_basic_operations.merg

This script executes comprehensive unit tests for merg.py with detailed reporting.
Generates HTML, JSON, and coverage reports with execution timestamps.
"""

import json
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime


class MergTestRunner:
    """Test runner for merg.py unit tests with comprehensive reporting"""
    
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.date_stamp = datetime.now().strftime("%Y-%m-%d")
        self.test_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_root = os.path.abspath(os.path.join(self.test_dir, '..', '..'))
        
        # Output files
        self.output_files = {
            'html_report': f'result_merg_{self.date_stamp}.html',
            'json_report': f'result_merg_{self.date_stamp}.json',
            'coverage_html': f'result_merg_coverage_{self.date_stamp}',
            'coverage_json': f'result_merg_coverage_{self.date_stamp}.json',
            'junit_xml': f'result_merg_{self.date_stamp}_junit.xml',
            'execution_summary': f'result_merg_execution_summary_{self.date_stamp}.txt'
        }
        
    def setup_environment(self):
        """Setup test environment and dependencies"""
        print(f"Setting up test environment at {self.timestamp}")
        
        # Add project paths to Python path
        sys.path.insert(0, self.project_root)
        sys.path.insert(0, os.path.join(self.project_root, 'src'))
        
        # Verify required packages
        required_packages = [
            'pytest', 'pytest-html', 'pytest-json-report', 
            'pytest-cov', 'PyQt5', 'pikepdf'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            print(f"Warning: Missing packages: {missing_packages}")
            return False
        
        print("All required packages available")
        return True
    
    def generate_pre_test_summary(self):
        """Generate pre-test execution summary"""
        summary = {
            "test_execution_info": {
                "timestamp": self.timestamp,
                "date": self.date_stamp,
                "target_module": "src.utilities.pdf_tools.pdf_basic_operations.merg",
                "test_file": f"test_merg_{self.date_stamp}.py",
                "config_file": f"pytest_merg_{self.date_stamp}.ini",
                "python_version": platform.python_version(),
                "platform": platform.platform(),
                "working_directory": self.test_dir
            },
            "output_files": self.output_files,
            "test_categories": [
                "merge_pdfs function tests",
                "MergeUI class tests",
                "Main function tests", 
                "Edge case tests"
            ],
            "coverage_targets": [
                "merge_pdfs function",
                "MergeUI.__init__",
                "MergeUI.update_button_states",
                "MergeUI.add_files",
                "MergeUI.remove_file",
                "MergeUI.clear_files",
                "MergeUI.move_up",
                "MergeUI.move_down", 
                "MergeUI.merge_files",
                "main function"
            ]
        }
        
        return summary
    
    def run_tests(self):
        """Execute the test suite with comprehensive reporting"""
        print(f"\\nStarting test execution at {self.timestamp}")
        print("=" * 60)
        
        # Change to test directory
        os.chdir(self.test_dir)
        
        # Build pytest command
        pytest_cmd = [
            sys.executable, '-m', 'pytest',
            '-c', f'pytest_merg_{self.date_stamp}.ini',
            f'test_merg_{self.date_stamp}.py',
            '--verbose',
            '--tb=short',
            '--html=' + self.output_files['html_report'],
            '--self-contained-html',
            '--json-report',
            '--json-report-file=' + self.output_files['json_report'],
            '--cov=src.utilities.pdf_tools.pdf_basic_operations.merg',
            '--cov-report=html:' + self.output_files['coverage_html'],
            '--cov-report=json:' + self.output_files['coverage_json'],
            '--cov-report=term-missing',
            '--junit-xml=' + self.output_files['junit_xml'],
            '--durations=10'
        ]
        
        print(f"Running command: {' '.join(pytest_cmd)}")
        print("-" * 60)
        
        # Execute tests
        try:
            result = subprocess.run(
                pytest_cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            
            print("STDOUT:")
            print(result.stdout)
            
            if result.stderr:
                print("\\nSTDERR:")
                print(result.stderr)
            
            return result.returncode, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            print("Test execution timed out after 10 minutes")
            return -1, "", "Test execution timeout"
        except Exception as e:
            print(f"Error executing tests: {e}")
            return -1, "", str(e)
    
    def generate_execution_summary(self, return_code, stdout, stderr):
        """Generate comprehensive execution summary"""
        end_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # Parse test results from output
        test_results = self.parse_test_output(stdout)
        
        summary = {
            "test_execution_summary": {
                "start_time": self.timestamp,
                "end_time": end_timestamp,
                "target_module": "src.utilities.pdf_tools.pdf_basic_operations.merg",
                "test_file": f"test_merg_{self.date_stamp}.py",
                "exit_code": return_code,
                "success": return_code == 0,
                "test_results": test_results,
                "output_files_generated": self.verify_output_files(),
                "errors": stderr if stderr else None
            }
        }
        
        # Write summary to file
        summary_file = self.output_files['execution_summary']
        with open(summary_file, 'w') as f:
            f.write("MERG.PY UNIT TEST EXECUTION SUMMARY\\n")
            f.write("=" * 50 + "\\n")
            f.write(f"Generated: {end_timestamp}\\n")
            f.write(f"Target: src.utilities.pdf_tools.pdf_basic_operations.merg\\n")
            f.write(f"Test File: test_merg_{self.date_stamp}.py\\n\\n")
            
            f.write("EXECUTION DETAILS:\\n")
            f.write("-" * 20 + "\\n")
            f.write(f"Start Time: {self.timestamp}\\n")
            f.write(f"End Time: {end_timestamp}\\n")
            f.write(f"Exit Code: {return_code}\\n")
            f.write(f"Success: {'Yes' if return_code == 0 else 'No'}\\n\\n")
            
            f.write("TEST RESULTS:\\n")
            f.write("-" * 15 + "\\n")
            for key, value in test_results.items():
                f.write(f"{key}: {value}\\n")
            
            f.write("\\nOUTPUT FILES:\\n")
            f.write("-" * 15 + "\\n")
            for file_type, filename in self.output_files.items():
                exists = "✓" if os.path.exists(filename) else "✗"
                f.write(f"{exists} {filename}\\n")
            
            if stderr:
                f.write(f"\\nERRORS:\\n")
                f.write("-" * 10 + "\\n")
                f.write(stderr)
            
            f.write("\\n" + "=" * 50 + "\\n")
            f.write(json.dumps(summary, indent=2))
        
        return summary
    
    def parse_test_output(self, output):
        """Parse pytest output for test statistics"""
        results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": 0
        }
        
        if not output:
            return results
        
        lines = output.split('\\n')
        for line in lines:
            if 'passed' in line and 'failed' in line:
                # Parse summary line like "5 passed, 2 failed in 1.23s"
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == 'passed' and i > 0:
                        results['passed'] = int(parts[i-1])
                    elif part == 'failed' and i > 0:
                        results['failed'] = int(parts[i-1])
                    elif part == 'skipped' and i > 0:
                        results['skipped'] = int(parts[i-1])
                    elif part == 'error' and i > 0:
                        results['errors'] = int(parts[i-1])
                
                results['total_tests'] = (results['passed'] + results['failed'] + 
                                        results['skipped'] + results['errors'])
                break
        
        return results
    
    def verify_output_files(self):
        """Verify which output files were successfully generated"""
        generated_files = {}
        for file_type, filename in self.output_files.items():
            generated_files[file_type] = {
                'filename': filename,
                'exists': os.path.exists(filename),
                'size': os.path.getsize(filename) if os.path.exists(filename) else 0
            }
        return generated_files
    
    def cleanup_old_results(self):
        """Clean up old test result files"""
        patterns = [
            'result_merg_*.html',
            'result_merg_*.json', 
            'result_merg_*.xml',
            'result_merg_*.txt'
        ]
        
        for pattern in patterns:
            for file in os.listdir(self.test_dir):
                if file.startswith('result_merg_') and not file.endswith(self.date_stamp):
                    try:
                        file_path = os.path.join(self.test_dir, file)
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                    except Exception as e:
                        print(f"Warning: Could not remove {file}: {e}")
    
    def run(self):
        """Main execution method"""
        print("MERG.PY UNIT TEST RUNNER")
        print("=" * 40)
        print(f"Timestamp: {self.timestamp}")
        print(f"Target: src.utilities.pdf_tools.pdf_basic_operations.merg")
        print(f"Test Directory: {self.test_dir}")
        
        # Setup environment
        if not self.setup_environment():
            print("Environment setup failed")
            return False
        
        # Generate pre-test summary
        pre_summary = self.generate_pre_test_summary()
        print("\\nPre-test summary generated")
        
        # Clean up old results
        self.cleanup_old_results()
        print("Old result files cleaned up")
        
        # Run tests
        return_code, stdout, stderr = self.run_tests()
        
        # Generate execution summary
        final_summary = self.generate_execution_summary(return_code, stdout, stderr)
        
        print("\\n" + "=" * 60)
        print("TEST EXECUTION COMPLETE")
        print(f"Exit Code: {return_code}")
        print(f"Success: {'Yes' if return_code == 0 else 'No'}")
        
        # Print output files
        print("\\nGenerated Files:")
        for file_type, filename in self.output_files.items():
            exists = "✓" if os.path.exists(filename) else "✗"
            print(f"  {exists} {filename}")
        
        return return_code == 0

def main():
    """Main entry point"""
    runner = MergTestRunner()
    success = runner.run()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()