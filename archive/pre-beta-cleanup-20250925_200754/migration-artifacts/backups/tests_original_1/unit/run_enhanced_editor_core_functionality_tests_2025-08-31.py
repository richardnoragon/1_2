#!/usr/bin/env python3
"""
Enhanced Editor Core Functionality Test Runner
Created: 2025-08-31
Target: enhanced_editor.py core functionality

This script runs comprehensive unit tests for the Enhanced Editor core functionality
with detailed reporting, coverage analysis, and standardized output.
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


class EnhancedEditorCoreFunctionalityTestRunner:
    """Test runner for Enhanced Editor core functionality."""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.test_dir = Path(__file__).parent
        self.results_dir = self.test_dir / "results"
        self.timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.date_stamp = "2025-08-31"
        
        # Ensure results directory exists
        self.results_dir.mkdir(exist_ok=True)
        
        # Test configuration
        self.test_file = "test_enhanced_editor_core_functionality_2025-08-31.py"
        self.config_file = "pytest_enhanced_editor_core_functionality_2025-08-31.ini"
        self.requirements_file = "requirements_test_enhanced_editor_core_functionality_2025-08-31.txt"
        
        # Output files
        self.html_report = f"result_enhanced_editor_core_functionality_{self.date_stamp}_report.html"
        self.json_report = f"result_enhanced_editor_core_functionality_{self.date_stamp}_results.json"
        self.junit_report = f"result_enhanced_editor_core_functionality_{self.date_stamp}_junit.xml"
        self.coverage_html = f"result_enhanced_editor_core_functionality_{self.date_stamp}_coverage/"
        self.coverage_json = f"result_enhanced_editor_core_functionality_{self.date_stamp}_coverage.json"
        self.summary_file = f"result_enhanced_editor_core_functionality_{self.date_stamp}_summary.json"
        self.execution_log = f"result_enhanced_editor_core_functionality_{self.date_stamp}_execution.log"
    
    def log_message(self, message, level="INFO"):
        """Log message with timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        print(log_entry)
        
        # Also write to execution log
        log_file = self.results_dir / self.execution_log
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")
    
    def check_requirements(self):
        """Check if all required packages are installed."""
        self.log_message("Checking test requirements...")
        
        requirements_path = self.test_dir / self.requirements_file
        if not requirements_path.exists():
            self.log_message(f"Requirements file not found: {requirements_path}", "ERROR")
            return False
        
        try:
            # Try to import key testing packages
            import pytest
            import pytest_cov
            import pytest_html
            import pytest_mock
            
            self.log_message("Core test packages are available")
            return True
            
        except ImportError as e:
            self.log_message(f"Missing required package: {e}", "ERROR")
            self.log_message("Please install requirements: pip install -r " + 
                           str(requirements_path), "ERROR")
            return False
    
    def setup_environment(self):
        """Setup test environment."""
        self.log_message("Setting up test environment...")
        
        # Set environment variables for Qt testing
        os.environ["QT_QPA_PLATFORM"] = "offscreen"
        os.environ["QT_LOGGING_RULES"] = "qt.qpa.xcb=false"
        os.environ["PYTEST_CURRENT_TEST"] = "enhanced_editor_core_functionality"
        
        # Add source path to PYTHONPATH
        src_path = self.test_dir.parent.parent / "src" / "utilities" / "file_operations" / "enhanced_editor"
        if src_path.exists():
            sys.path.insert(0, str(src_path))
            os.environ["PYTHONPATH"] = str(src_path) + os.pathsep + os.environ.get("PYTHONPATH", "")
        
        self.log_message("Environment configured for core functionality testing")
    
    def run_tests(self):
        """Run the core functionality test suite."""
        self.log_message("Starting core functionality test execution...")
        self.start_time = time.time()
        
        # Construct pytest command
        cmd = [
            sys.executable, "-m", "pytest",
            self.test_file,
            "-c", self.config_file,
            "--verbose",
            "--tb=short",
            "--color=yes",
            "--durations=10",
            f"--html={self.results_dir / self.html_report}",
            "--self-contained-html",
            f"--junitxml={self.results_dir / self.junit_report}",
            "--json-report",
            f"--json-report-file={self.results_dir / self.json_report}",
            f"--cov=enhanced_editor",
            f"--cov-report=html:{self.results_dir / self.coverage_html}",
            f"--cov-report=json:{self.results_dir / self.coverage_json}",
            "--cov-report=term-missing",
            "--cov-fail-under=70",  # Lower threshold for core functionality
            "--cov-branch",
            "-m", "not slow",  # Skip slow tests by default
        ]
        
        self.log_message(f"Executing command: {' '.join(cmd)}")
        
        # Run tests
        try:
            result = subprocess.run(
                cmd,
                cwd=self.test_dir,
                capture_output=True,
                text=True,
                timeout=1200  # 20 minute timeout for core tests
            )
            
            self.end_time = time.time()
            
            # Log output
            if result.stdout:
                self.log_message("STDOUT:")
                for line in result.stdout.split('\n'):
                    if line.strip():
                        self.log_message(f"  {line}")
            
            if result.stderr:
                self.log_message("STDERR:")
                for line in result.stderr.split('\n'):
                    if line.strip():
                        self.log_message(f"  {line}", "WARN")
            
            return result.returncode == 0, result
            
        except subprocess.TimeoutExpired:
            self.log_message("Test execution timed out after 20 minutes", "ERROR")
            return False, None
        
        except Exception as e:
            self.log_message(f"Error running tests: {e}", "ERROR")
            return False, None
    
    def generate_summary_report(self, test_success, result):
        """Generate comprehensive summary report."""
        self.log_message("Generating summary report...")
        
        execution_time = self.end_time - self.start_time if self.end_time and self.start_time else 0
        
        # Load JSON results if available
        json_results = {}
        json_file = self.results_dir / self.json_report
        if json_file.exists():
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    json_results = json.load(f)
            except Exception as e:
                self.log_message(f"Error reading JSON results: {e}", "WARN")
        
        # Load coverage results if available
        coverage_data = {}
        coverage_file = self.results_dir / self.coverage_json
        if coverage_file.exists():
            try:
                with open(coverage_file, 'r', encoding='utf-8') as f:
                    coverage_data = json.load(f)
            except Exception as e:
                self.log_message(f"Error reading coverage data: {e}", "WARN")
        
        # Create comprehensive summary
        summary = {
            "test_execution_summary": {
                "execution_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "test_file": self.test_file,
                "target_module": "enhanced_editor.py",
                "test_focus": "Core Functionality",
                "config_file": self.config_file,
                "requirements_file": self.requirements_file,
                "execution_time_seconds": round(execution_time, 2),
                "execution_time_formatted": f"{int(execution_time // 60)}m {int(execution_time % 60)}s",
                "test_success": test_success,
                "return_code": result.returncode if result else -1
            },
            
            "test_results": {
                "total_tests": json_results.get("summary", {}).get("total", 0),
                "passed": json_results.get("summary", {}).get("passed", 0),
                "failed": json_results.get("summary", {}).get("failed", 0),
                "skipped": json_results.get("summary", {}).get("skipped", 0),
                "errors": json_results.get("summary", {}).get("error", 0),
                "warnings": json_results.get("summary", {}).get("warnings", 0),
                "success_rate": "0.00%"
            },
            
            "coverage_analysis": {
                "total_coverage": coverage_data.get("totals", {}).get("percent_covered", 0),
                "lines_covered": coverage_data.get("totals", {}).get("covered_lines", 0),
                "lines_missing": coverage_data.get("totals", {}).get("missing_lines", 0),
                "total_lines": coverage_data.get("totals", {}).get("num_statements", 0),
                "branch_coverage": coverage_data.get("totals", {}).get("percent_covered_display", "N/A"),
                "coverage_files": list(coverage_data.get("files", {}).keys()) if coverage_data.get("files") else []
            },
            
            "test_categories_core": {
                "core_data_structures": "Tests for DocumentType, SearchOptions, EditorSettings",
                "document_manager": "Tests for document management core functionality",
                "file_operations": "Tests for file I/O, encoding detection, basic file ops",
                "search_replace": "Tests for search and replace core algorithms",
                "syntax_highlighting": "Tests for basic syntax highlighting functionality",
                "text_editor_core": "Tests for core text editing operations",
                "error_handling": "Tests for error scenarios and edge cases",
                "integration": "Tests for core component integration",
                "performance": "Tests for core performance characteristics",
                "configuration": "Tests for settings and configuration management"
            },
            
            "test_class_breakdown_core": {
                "TestDocumentType": "Document type enumeration tests",
                "TestSearchOptions": "Search options dataclass tests",
                "TestEditorSettings": "Editor settings configuration tests",
                "TestDocumentManager": "Document management core tests",
                "TestSyntaxHighlighterCore": "Basic syntax highlighting tests",
                "TestFileOperationsCore": "Core file operation tests",
                "TestSearchReplaceCore": "Search and replace algorithm tests",
                "TestTextEditorCore": "Text editor core functionality tests",
                "TestErrorHandlingCore": "Error handling and edge case tests",
                "TestCoreIntegration": "Integration between core components",
                "TestCorePerformance": "Core performance and stress tests",
                "TestConfigurationCore": "Configuration and settings tests"
            },
            
            "core_functionality_focus": {
                "data_structures": "Fundamental data types and enumerations",
                "document_management": "Document lifecycle and properties management",
                "file_operations": "Basic file reading, writing, encoding detection",
                "text_processing": "Core text manipulation and processing",
                "search_algorithms": "Search and replace algorithm implementation",
                "settings_management": "Configuration and preferences handling",
                "error_recovery": "Error handling and graceful degradation",
                "component_integration": "Basic component interaction patterns"
            },
            
            "output_files": {
                "html_report": str(self.results_dir / self.html_report),
                "json_results": str(self.results_dir / self.json_report),
                "junit_xml": str(self.results_dir / self.junit_report),
                "coverage_html": str(self.results_dir / self.coverage_html),
                "coverage_json": str(self.results_dir / self.coverage_json),
                "execution_log": str(self.results_dir / self.execution_log),
                "summary_report": str(self.results_dir / self.summary_file)
            },
            
            "environment_info": {
                "python_version": sys.version,
                "platform": sys.platform,
                "working_directory": str(self.test_dir),
                "pytest_version": self.get_package_version("pytest"),
                "coverage_version": self.get_package_version("coverage"),
                "pyqt5_available": self.check_pyqt5_availability()
            },
            
            "next_steps": {
                "view_html_report": f"Open {self.html_report} in a web browser",
                "view_coverage": f"Open {self.coverage_html}index.html for detailed coverage",
                "check_failures": "Review failed tests in the HTML report",
                "improve_coverage": "Add tests for uncovered core functionality",
                "run_full_suite": "Execute the comprehensive test suite for complete coverage"
            }
        }
        
        # Calculate success rate
        total = summary["test_results"]["total_tests"]
        passed = summary["test_results"]["passed"]
        if total > 0:
            success_rate = (passed / total) * 100
            summary["test_results"]["success_rate"] = f"{success_rate:.2f}%"
        
        # Save summary to file
        summary_path = self.results_dir / self.summary_file
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        self.log_message(f"Summary report saved to: {summary_path}")
        return summary
    
    def get_package_version(self, package_name):
        """Get version of installed package."""
        try:
            import importlib.metadata
            return importlib.metadata.version(package_name)
        except:
            try:
                import pkg_resources
                return pkg_resources.get_distribution(package_name).version
            except:
                return "Unknown"
    
    def check_pyqt5_availability(self):
        """Check if PyQt5 is available."""
        try:
            import PyQt5
            return True
        except ImportError:
            return False
    
    def display_summary(self, summary):
        """Display test execution summary."""
        print("\n" + "="*80)
        print(" ENHANCED EDITOR CORE FUNCTIONALITY TEST SUMMARY")
        print("="*80)
        
        exec_info = summary["test_execution_summary"]
        print(f"Execution Time: {exec_info['execution_timestamp']}")
        print(f"Target Module: {exec_info['target_module']}")
        print(f"Test Focus: {exec_info['test_focus']}")
        print(f"Test File: {exec_info['test_file']}")
        print(f"Duration: {exec_info['execution_time_formatted']}")
        print(f"Success: {'✓ PASSED' if exec_info['test_success'] else '✗ FAILED'}")
        
        print("\nTEST RESULTS:")
        results = summary["test_results"]
        print(f"  Total Tests: {results['total_tests']}")
        print(f"  Passed: {results['passed']}")
        print(f"  Failed: {results['failed']}")
        print(f"  Skipped: {results['skipped']}")
        print(f"  Errors: {results['errors']}")
        print(f"  Success Rate: {results['success_rate']}")
        
        print("\nCOVERAGE ANALYSIS:")
        coverage = summary["coverage_analysis"]
        print(f"  Total Coverage: {coverage['total_coverage']:.2f}%")
        print(f"  Lines Covered: {coverage['lines_covered']}")
        print(f"  Lines Missing: {coverage['lines_missing']}")
        print(f"  Total Lines: {coverage['total_lines']}")
        
        print("\nCORE FUNCTIONALITY AREAS TESTED:")
        focus_areas = summary["core_functionality_focus"]
        for area, description in focus_areas.items():
            print(f"  • {area.replace('_', ' ').title()}: {description}")
        
        print("\nOUTPUT FILES:")
        files = summary["output_files"]
        for file_type, file_path in files.items():
            if os.path.exists(file_path):
                print(f"  ✓ {file_type}: {file_path}")
            else:
                print(f"  ✗ {file_type}: {file_path} (not found)")
        
        print("\nNEXT STEPS:")
        for step, description in summary["next_steps"].items():
            print(f"  • {description}")
        
        print("="*80)
    
    def run(self):
        """Main execution method."""
        self.log_message("Starting Enhanced Editor Core Functionality Test Suite")
        self.log_message(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check requirements
        if not self.check_requirements():
            self.log_message("Requirements check failed", "ERROR")
            return False
        
        # Setup environment
        self.setup_environment()
        
        # Check if test file exists
        test_file_path = self.test_dir / self.test_file
        if not test_file_path.exists():
            self.log_message(f"Test file not found: {test_file_path}", "ERROR")
            return False
        
        # Run tests
        success, result = self.run_tests()
        
        # Generate summary
        summary = self.generate_summary_report(success, result)
        
        # Display results
        self.display_summary(summary)
        
        # Final status
        if success:
            self.log_message("Core functionality test execution completed successfully ✓")
        else:
            self.log_message("Core functionality test execution completed with failures ✗", "ERROR")
        
        return success


def main():
    """Main entry point."""
    runner = EnhancedEditorCoreFunctionalityTestRunner()
    success = runner.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()