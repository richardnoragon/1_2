#!/usr/bin/env python3
"""
Test runner script for data_locations.py unit tests.

This script executes comprehensive unit tests for the DataLocations class
and generates detailed HTML and JSON reports with coverage information.

Usage:
    python run_test_data_locations_2025-08-30.py
"""

import json
import os
import platform
import subprocess
import sys
from datetime import datetime
from pathlib import Path


class TestRunner:
    """Test runner for data_locations.py unit tests."""
    
    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.test_file = "test_data_locations_2025-08-30.py"
        self.timestamp = datetime.now()
        self.results = {}
    
    def setup_environment(self):
        """Setup the test environment."""
        print(f"Setting up test environment for {self.test_file}")
        print(f"Test directory: {self.test_dir}")
        print(f"Timestamp: {self.timestamp.isoformat()}")
        
        # Ensure we're in the correct directory
        os.chdir(self.test_dir)
        
        # Add project root to Python path
        project_root = self.test_dir.parent.parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        
        print(f"Project root added to path: {project_root}")
    
    def install_dependencies(self):
        """Install test dependencies."""
        requirements_file = f"test_requirements_data_locations_2025-08-30.txt"
        
        if Path(requirements_file).exists():
            print(f"Installing test dependencies from {requirements_file}")
            try:
                subprocess.run([
                    sys.executable, "-m", "pip", "install", "-r", requirements_file
                ], check=True, capture_output=True, text=True)
                print("Dependencies installed successfully")
                return True
            except subprocess.CalledProcessError as e:
                print(f"Warning: Failed to install some dependencies: {e}")
                print("Continuing with available packages...")
                return False
        else:
            print(f"No requirements file found: {requirements_file}")
            return False
    
    def run_tests(self):
        """Execute the unit tests with comprehensive reporting."""
        print(f"\\nRunning tests for {self.test_file}")
        print("=" * 60)
        
        # Build pytest command with all reporting options
        cmd = [
            sys.executable, "-m", "pytest",
            self.test_file,
            "-v",
            "--tb=short",
            "--html=result_data_locations_2025-08-30.html",
            "--self-contained-html",
            "--json-report",
            "--json-report-file=result_data_locations_2025-08-30.json",
            "--cov=utilities.privacy.privacy_tools.core.data_locations",
            "--cov-report=html:result_data_locations_2025-08-30_coverage",
            "--cov-report=json:result_data_locations_2025-08-30_coverage.json",
            "--cov-report=term-missing",
            "--maxfail=10",
            "-p", "no:warnings"
        ]
        
        print(f"Executing command: {' '.join(cmd)}")
        
        try:
            # Run tests and capture output
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            # Store results
            self.results = {
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "command": " ".join(cmd),
                "execution_time": datetime.now() - self.timestamp
            }
            
            # Print output
            print("\\nTest Output:")
            print("-" * 40)
            print(result.stdout)
            
            if result.stderr:
                print("\\nTest Errors/Warnings:")
                print("-" * 40)
                print(result.stderr)
            
            # Determine success
            success = result.returncode == 0
            print(f"\\nTest execution {'PASSED' if success else 'FAILED'}")
            print(f"Return code: {result.returncode}")
            
            return success
            
        except subprocess.TimeoutExpired:
            print("ERROR: Test execution timed out after 5 minutes")
            return False
        except Exception as e:
            print(f"ERROR: Failed to execute tests: {e}")
            return False
    
    def generate_summary_report(self):
        """Generate a comprehensive summary report."""
        summary_file = "result_data_locations_2025-08-30_summary.json"
        
        summary = {
            "test_execution": {
                "timestamp": self.timestamp.isoformat(),
                "completion_time": datetime.now().isoformat(),
                "duration_seconds": self.results.get("execution_time", {}).total_seconds() if "execution_time" in self.results else 0,
                "success": self.results.get("return_code", -1) == 0
            },
            "test_details": {
                "test_file": self.test_file,
                "target_module": "data_locations.py",
                "test_directory": str(self.test_dir),
                "command_executed": self.results.get("command", "")
            },
            "environment": {
                "platform": platform.system(),
                "platform_version": platform.version(),
                "python_version": sys.version,
                "python_executable": sys.executable,
                "working_directory": os.getcwd()
            },
            "generated_files": [
                "result_data_locations_2025-08-30.html",
                "result_data_locations_2025-08-30.json",
                "result_data_locations_2025-08-30_coverage/",
                "result_data_locations_2025-08-30_coverage.json",
                summary_file
            ]
        }
        
        # Add test results if available
        if "stdout" in self.results:
            summary["test_output"] = {
                "stdout_preview": self.results["stdout"][:1000] + "..." if len(self.results["stdout"]) > 1000 else self.results["stdout"],
                "stderr_preview": self.results["stderr"][:500] + "..." if len(self.results["stderr"]) > 500 else self.results["stderr"]
            }
        
        # Write summary report
        try:
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2, default=str)
            print(f"\\nSummary report generated: {summary_file}")
            return True
        except Exception as e:
            print(f"Warning: Failed to generate summary report: {e}")
            return False
    
    def verify_generated_files(self):
        """Verify that all expected output files were generated."""
        expected_files = [
            "result_data_locations_2025-08-30.html",
            "result_data_locations_2025-08-30.json",
            "result_data_locations_2025-08-30_coverage.json"
        ]
        
        expected_dirs = [
            "result_data_locations_2025-08-30_coverage"
        ]
        
        print("\\nVerifying generated files:")
        print("-" * 30)
        
        all_present = True
        
        for file_path in expected_files:
            if Path(file_path).exists():
                size = Path(file_path).stat().st_size
                print(f"✓ {file_path} ({size} bytes)")
            else:
                print(f"✗ {file_path} (missing)")
                all_present = False
        
        for dir_path in expected_dirs:
            if Path(dir_path).exists() and Path(dir_path).is_dir():
                file_count = len(list(Path(dir_path).rglob("*")))
                print(f"✓ {dir_path}/ ({file_count} files)")
            else:
                print(f"✗ {dir_path}/ (missing)")
                all_present = False
        
        return all_present
    
    def run(self):
        """Execute the complete test workflow."""
        print("DataLocations Unit Test Runner")
        print("=" * 50)
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Platform: {platform.system()} {platform.release()}")
        print(f"Python: {sys.version}")
        
        try:
            # Setup environment
            self.setup_environment()
            
            # Install dependencies (optional, continue if fails)
            self.install_dependencies()
            
            # Run tests
            test_success = self.run_tests()
            
            # Generate summary
            summary_success = self.generate_summary_report()
            
            # Verify files
            files_present = self.verify_generated_files()
            
            # Final status
            print("\\n" + "=" * 50)
            print("TEST EXECUTION SUMMARY")
            print("=" * 50)
            print(f"Tests executed: {'SUCCESS' if test_success else 'FAILED'}")
            print(f"Summary generated: {'SUCCESS' if summary_success else 'FAILED'}")
            print(f"Output files: {'ALL PRESENT' if files_present else 'SOME MISSING'}")
            
            overall_success = test_success and summary_success and files_present
            print(f"\\nOverall result: {'SUCCESS' if overall_success else 'PARTIAL SUCCESS'}")
            
            if overall_success:
                print("\\nAll test outputs are available in the following files:")
                print("- result_data_locations_2025-08-30.html (HTML report)")
                print("- result_data_locations_2025-08-30.json (JSON report)")
                print("- result_data_locations_2025-08-30_coverage/ (Coverage HTML)")
                print("- result_data_locations_2025-08-30_coverage.json (Coverage JSON)")
                print("- result_data_locations_2025-08-30_summary.json (Execution summary)")
            
            return overall_success
            
        except Exception as e:
            print(f"\\nFATAL ERROR: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Main entry point."""
    runner = TestRunner()
    success = runner.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()