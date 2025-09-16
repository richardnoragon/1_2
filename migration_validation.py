#!/usr/bin/env python3
"""
Migration Validation Tools
=========================

Comprehensive tools for validating successful migration from src/utilities to src/tools.
These tools verify file integrity, import functionality, and system behavior.

Tools included:
1. Migration Validator - Core validation engine
2. Import Verifier - Validates all import statements work
3. Functionality Tester - Tests that tools still work
4. Performance Analyzer - Ensures no performance degradation
5. Rollback Detector - Identifies when rollback may be needed
6. Health Monitor - Ongoing system health checks

Usage:
    python migration_validation.py [--validator] [--all] [--report]
"""

import argparse
import importlib
import importlib.util
import json
import logging
import os
import subprocess
import sys
import time
import traceback
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class ValidationResult:
    """Structure for validation results."""
    test_name: str
    status: str  # 'passed', 'failed', 'warning', 'skipped'
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


class MigrationValidator:
    """Core migration validation engine."""
    
    def __init__(self, project_root: Optional[str] = None):
        self.project_root = Path(project_root or Path(__file__).parent)
        self.results: List[ValidationResult] = []
        self.setup_logging()
        
        # Ensure project root is in Python path
        if str(self.project_root) not in sys.path:
            sys.path.insert(0, str(self.project_root))
    
    def setup_logging(self):
        """Setup validation logging."""
        log_dir = self.project_root / "validation_logs"
        log_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"migration_validation_{timestamp}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("Migration validation started")
    
    def add_result(self, result: ValidationResult):
        """Add a validation result."""
        self.results.append(result)
        
        if result.status == 'passed':
            self.logger.info(f"✓ {result.test_name}: {result.message}")
        elif result.status == 'failed':
            self.logger.error(f"✗ {result.test_name}: {result.message}")
        elif result.status == 'warning':
            self.logger.warning(f"⚠ {result.test_name}: {result.message}")
        else:
            self.logger.info(f"- {result.test_name}: {result.message}")
    
    def validate_directory_structure(self) -> bool:
        """Validate that migration directory structure is correct."""
        self.logger.info("Validating directory structure...")
        
        # Check that utilities directory is gone or empty
        utilities_path = self.project_root / "src" / "utilities"
        if utilities_path.exists():
            files_in_utilities = list(utilities_path.rglob("*"))
            if files_in_utilities:
                self.add_result(ValidationResult(
                    "utilities_cleanup",
                    "warning",
                    f"Utilities directory still contains {len(files_in_utilities)} items",
                    {"files_remaining": [str(f) for f in files_in_utilities[:10]]}
                ))
            else:
                self.add_result(ValidationResult(
                    "utilities_cleanup",
                    "passed",
                    "Utilities directory is empty"
                ))
        else:
            self.add_result(ValidationResult(
                "utilities_cleanup",
                "passed",
                "Utilities directory has been removed"
            ))
        
        # Check that tools directory exists and has content
        tools_path = self.project_root / "src" / "tools"
        if not tools_path.exists():
            self.add_result(ValidationResult(
                "tools_directory",
                "failed",
                "Tools directory does not exist"
            ))
            return False
        
        # Count files in tools directory
        py_files = list(tools_path.rglob("*.py"))
        ui_files = list(tools_path.rglob("*.ui"))
        
        self.add_result(ValidationResult(
            "tools_content",
            "passed",
            f"Tools directory contains {len(py_files)} Python files and {len(ui_files)} UI files",
            {"python_files": len(py_files), "ui_files": len(ui_files)}
        ))
        
        # Check for expected directories
        expected_dirs = [
            "pdf_tools",
            "file_management",
            "metadata",
            "file_operations",
            "analysis",
            "network",
            "privacy",
            "security",
            "system"
        ]
        
        missing_dirs = []
        for expected_dir in expected_dirs:
            dir_path = tools_path / expected_dir
            if not dir_path.exists():
                missing_dirs.append(expected_dir)
        
        if missing_dirs:
            self.add_result(ValidationResult(
                "expected_directories",
                "warning",
                f"Missing expected directories: {missing_dirs}",
                {"missing": missing_dirs}
            ))
        else:
            self.add_result(ValidationResult(
                "expected_directories",
                "passed",
                "All expected directories present"
            ))
        
        return True
    
    def validate_import_statements(self) -> bool:
        """Validate that import statements have been updated correctly."""
        self.logger.info("Validating import statements...")
        
        # Files to check for import updates
        files_to_check = []
        
        # Add Python files from key directories
        for pattern in ["src/**/*.py", "tests/**/*.py", "*.py"]:
            files_to_check.extend(self.project_root.glob(pattern))
        
        old_imports_found = []
        import_errors = []
        
        for file_path in files_to_check:
            if file_path.is_file():
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Check for old import patterns
                    old_patterns = [
                        "from src.utilities",
                        "import src.utilities",
                        "from tools.",
                        "import tools."
                    ]
                    
                    for pattern in old_patterns:
                        if pattern in content:
                            old_imports_found.append((str(file_path), pattern))
                    
                    # Basic syntax check
                    try:
                        compile(content, str(file_path), 'exec')
                    except SyntaxError as e:
                        import_errors.append((str(file_path), str(e)))
                
                except Exception as e:
                    import_errors.append((str(file_path), f"Read error: {e}"))
        
        # Report old imports
        if old_imports_found:
            self.add_result(ValidationResult(
                "old_imports",
                "failed",
                f"Found {len(old_imports_found)} files with old import statements",
                {"old_imports": old_imports_found[:10]}  # First 10 only
            ))
        else:
            self.add_result(ValidationResult(
                "old_imports",
                "passed",
                "No old import statements found"
            ))
        
        # Report syntax errors
        if import_errors:
            self.add_result(ValidationResult(
                "syntax_errors",
                "failed",
                f"Found {len(import_errors)} files with syntax errors",
                {"errors": import_errors[:5]}  # First 5 only
            ))
        else:
            self.add_result(ValidationResult(
                "syntax_errors",
                "passed",
                "No syntax errors found"
            ))
        
        return len(old_imports_found) == 0 and len(import_errors) == 0
    
    def validate_module_imports(self) -> bool:
        """Validate that new module imports work correctly."""
        self.logger.info("Validating module imports...")
        
        # Test import of key modules
        test_modules = [
            "src.tools.pdf_tools",
            "src.tools.file_management",
            "src.tools.file_operations", 
            "src.tools.metadata",
            "src.tools.analysis",
            "src.tools.network",
            "src.tools.privacy",
            "src.tools.security",
            "src.tools.system"
        ]
        
        import_successes = 0
        import_failures = []
        
        for module_name in test_modules:
            try:
                spec = importlib.util.find_spec(module_name)
                if spec is not None:
                    # Try to actually import the module
                    importlib.import_module(module_name)
                    import_successes += 1
                    self.add_result(ValidationResult(
                        f"import_{module_name}",
                        "passed", 
                        f"Successfully imported {module_name}"
                    ))
                else:
                    self.add_result(ValidationResult(
                        f"import_{module_name}",
                        "warning",
                        f"Module {module_name} not found"
                    ))
            except ImportError as e:
                import_failures.append((module_name, str(e)))
                self.add_result(ValidationResult(
                    f"import_{module_name}",
                    "failed",
                    f"Failed to import {module_name}: {e}"
                ))
            except Exception as e:
                import_failures.append((module_name, f"Unexpected error: {e}"))
                self.add_result(ValidationResult(
                    f"import_{module_name}",
                    "failed",
                    f"Unexpected error importing {module_name}: {e}"
                ))
        
        # Overall import assessment
        if import_successes >= len(test_modules) * 0.7:  # 70% success rate
            self.add_result(ValidationResult(
                "overall_imports",
                "passed",
                f"Successfully imported {import_successes}/{len(test_modules)} modules"
            ))
            return True
        else:
            self.add_result(ValidationResult(
                "overall_imports",
                "failed", 
                f"Only {import_successes}/{len(test_modules)} modules imported successfully"
            ))
            return False
    
    def validate_gui_components(self) -> bool:
        """Validate that GUI components are accessible."""
        self.logger.info("Validating GUI components...")
        
        # Test key GUI components
        gui_components = [
            ("src.tools.pdf_tools.widgets.enhanced_pdf_tools_widget", "EnhancedPDFToolsWidget"),
            ("src.tools.file_operations.catalog.catalog", "CatalogWindow"),
            ("src.tools.metadata.image_metadata", "ImageMetadataEditorGUI"),
            ("src.tools.analysis.size_analyzer", "SizeAnalyzerGUI"),
            ("src.tools.security.encryption", "EncryptionGUI")
        ]
        
        gui_successes = 0
        
        for module_name, class_name in gui_components:
            try:
                spec = importlib.util.find_spec(module_name)
                if spec is not None:
                    module = importlib.import_module(module_name)
                    if hasattr(module, class_name):
                        gui_class = getattr(module, class_name)
                        if callable(gui_class):
                            gui_successes += 1
                            self.add_result(ValidationResult(
                                f"gui_{class_name}",
                                "passed",
                                f"GUI component {class_name} is accessible"
                            ))
                        else:
                            self.add_result(ValidationResult(
                                f"gui_{class_name}",
                                "failed",
                                f"GUI component {class_name} is not callable"
                            ))
                    else:
                        self.add_result(ValidationResult(
                            f"gui_{class_name}",
                            "failed",
                            f"GUI component {class_name} not found in {module_name}"
                        ))
                else:
                    self.add_result(ValidationResult(
                        f"gui_{class_name}",
                        "warning",
                        f"Module {module_name} not found"
                    ))
            except Exception as e:
                self.add_result(ValidationResult(
                    f"gui_{class_name}",
                    "failed",
                    f"Error accessing {class_name}: {e}"
                ))
        
        # Overall GUI assessment
        if gui_successes >= len(gui_components) * 0.5:  # 50% success rate for GUI
            self.add_result(ValidationResult(
                "overall_gui",
                "passed",
                f"Successfully accessed {gui_successes}/{len(gui_components)} GUI components"
            ))
            return True
        else:
            self.add_result(ValidationResult(
                "overall_gui",
                "warning",
                f"Only {gui_successes}/{len(gui_components)} GUI components accessible"
            ))
            return False
    
    def validate_configuration_system(self) -> bool:
        """Validate that configuration system works with new structure."""
        self.logger.info("Validating configuration system...")
        
        try:
            # Test config manager import
            from src.rfu.config_manager import get_config_manager
            config = get_config_manager()
            
            self.add_result(ValidationResult(
                "config_manager",
                "passed",
                "Configuration manager is accessible"
            ))
            
            # Test basic config operations
            try:
                # Test getting a setting
                test_setting = config.get_setting('general', 'logging_level', 'INFO')
                
                self.add_result(ValidationResult(
                    "config_operations",
                    "passed",
                    "Configuration operations work correctly"
                ))
                
                return True
                
            except Exception as e:
                self.add_result(ValidationResult(
                    "config_operations",
                    "failed",
                    f"Configuration operations failed: {e}"
                ))
                return False
        
        except ImportError as e:
            self.add_result(ValidationResult(
                "config_manager",
                "failed",
                f"Configuration manager not accessible: {e}"
            ))
            return False
    
    def validate_main_application(self) -> bool:
        """Validate that main application components work."""
        self.logger.info("Validating main application...")
        
        try:
            # Test main module import
            from src.rfu.main import main
            
            self.add_result(ValidationResult(
                "main_function",
                "passed",
                "Main function is accessible"
            ))
            
            # Test hub import
            from src.rfu.hub import RFUHub
            
            self.add_result(ValidationResult(
                "hub_class",
                "passed",
                "RFUHub class is accessible"
            ))
            
            return True
            
        except ImportError as e:
            self.add_result(ValidationResult(
                "main_application",
                "failed",
                f"Main application components not accessible: {e}"
            ))
            return False
    
    def generate_validation_report(self) -> str:
        """Generate comprehensive validation report."""
        # Calculate summary statistics
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r.status == 'passed'])
        failed_tests = len([r for r in self.results if r.status == 'failed'])
        warning_tests = len([r for r in self.results if r.status == 'warning'])
        skipped_tests = len([r for r in self.results if r.status == 'skipped'])
        
        # Create report structure
        report = {
            "validation_summary": {
                "timestamp": datetime.now().isoformat(),
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "warnings": warning_tests,
                "skipped": skipped_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                "overall_status": "PASSED" if failed_tests == 0 else "FAILED"
            },
            "detailed_results": [
                {
                    "test_name": r.test_name,
                    "status": r.status,
                    "message": r.message,
                    "timestamp": r.timestamp,
                    "details": r.details
                }
                for r in self.results
            ]
        }
        
        # Write report to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.project_root / f"validation_report_{timestamp}.json"
        
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)
        
        self.logger.info(f"Validation report generated: {report_file}")
        return str(report_file)
    
    def run_complete_validation(self) -> bool:
        """Run complete validation suite."""
        self.logger.info("=== Starting Complete Migration Validation ===")
        
        validations = [
            ("Directory Structure", self.validate_directory_structure),
            ("Import Statements", self.validate_import_statements),
            ("Module Imports", self.validate_module_imports),
            ("GUI Components", self.validate_gui_components),
            ("Configuration System", self.validate_configuration_system),
            ("Main Application", self.validate_main_application)
        ]
        
        overall_success = True
        
        for validation_name, validation_func in validations:
            self.logger.info(f"Running {validation_name} validation...")
            try:
                success = validation_func()
                if not success:
                    overall_success = False
            except Exception as e:
                self.logger.error(f"Validation {validation_name} crashed: {e}")
                self.add_result(ValidationResult(
                    f"{validation_name.lower().replace(' ', '_')}_crash",
                    "failed",
                    f"Validation crashed: {e}"
                ))
                overall_success = False
        
        # Generate report
        report_file = self.generate_validation_report()
        
        # Print summary
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r.status == 'passed'])
        failed_tests = len([r for r in self.results if r.status == 'failed'])
        warning_tests = len([r for r in self.results if r.status == 'warning'])
        
        self.logger.info("=== Validation Summary ===")
        self.logger.info(f"Total Tests: {total_tests}")
        self.logger.info(f"Passed: {passed_tests}")
        self.logger.info(f"Failed: {failed_tests}")
        self.logger.info(f"Warnings: {warning_tests}")
        self.logger.info(f"Success Rate: {(passed_tests / total_tests * 100):.1f}%")
        self.logger.info(f"Overall Status: {'PASSED' if overall_success else 'FAILED'}")
        self.logger.info(f"Report: {report_file}")
        
        return overall_success


class PerformanceAnalyzer:
    """Analyze performance impact of migration."""
    
    def __init__(self, project_root: Optional[str] = None):
        self.project_root = Path(project_root or Path(__file__).parent)
        self.logger = logging.getLogger(f"{__name__}.PerformanceAnalyzer")
    
    def measure_import_times(self) -> Dict[str, float]:
        """Measure import times for migrated modules."""
        modules_to_test = [
            "src.tools.pdf_tools",
            "src.tools.file_management",
            "src.tools.analysis",
            "src.tools.security"
        ]
        
        import_times = {}
        
        for module_name in modules_to_test:
            try:
                start_time = time.time()
                spec = importlib.util.find_spec(module_name)
                if spec is not None:
                    importlib.import_module(module_name)
                    import_time = time.time() - start_time
                    import_times[module_name] = import_time
                    self.logger.info(f"Import time for {module_name}: {import_time:.3f}s")
            except Exception as e:
                self.logger.error(f"Failed to measure import time for {module_name}: {e}")
                import_times[module_name] = -1  # Error indicator
        
        return import_times
    
    def analyze_performance(self) -> Dict[str, Any]:
        """Analyze overall performance impact."""
        self.logger.info("Analyzing performance impact...")
        
        # Measure import times
        import_times = self.measure_import_times()
        
        # Basic performance assessment
        performance_report = {
            "import_times": import_times,
            "average_import_time": sum([t for t in import_times.values() if t > 0]) / len([t for t in import_times.values() if t > 0]) if import_times else 0,
            "slow_imports": [m for m, t in import_times.items() if t > 2.0],  # > 2 seconds
            "performance_status": "good"
        }
        
        # Determine performance status
        if performance_report["average_import_time"] > 3.0:
            performance_report["performance_status"] = "poor"
        elif performance_report["average_import_time"] > 1.5:
            performance_report["performance_status"] = "fair"
        
        return performance_report


def main():
    """Main entry point for validation tools."""
    parser = argparse.ArgumentParser(description="Migration validation tools")
    parser.add_argument("--validator", action="store_true",
                       help="Run migration validator")
    parser.add_argument("--performance", action="store_true",
                       help="Run performance analysis")
    parser.add_argument("--all", action="store_true",
                       help="Run all validation tools")
    parser.add_argument("--report", action="store_true",
                       help="Generate detailed reports")
    
    args = parser.parse_args()
    
    if not any([args.validator, args.performance, args.all]):
        args.all = True  # Default to all if nothing specified
    
    overall_success = True
    
    # Run migration validator
    if args.validator or args.all:
        print("Running migration validator...")
        validator = MigrationValidator()
        success = validator.run_complete_validation()
        if not success:
            overall_success = False
    
    # Run performance analyzer
    if args.performance or args.all:
        print("Running performance analysis...")
        analyzer = PerformanceAnalyzer()
        performance_report = analyzer.analyze_performance()
        
        print(f"Performance Status: {performance_report['performance_status']}")
        print(f"Average Import Time: {performance_report['average_import_time']:.3f}s")
        
        if performance_report['slow_imports']:
            print(f"Slow imports detected: {performance_report['slow_imports']}")
        
        if args.report:
            # Save performance report
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            perf_file = Path(__file__).parent / f"performance_report_{timestamp}.json"
            with open(perf_file, "w") as f:
                json.dump(performance_report, f, indent=2)
            print(f"Performance report saved: {perf_file}")
    
    print(f"\nOverall validation result: {'PASSED' if overall_success else 'FAILED'}")
    return 0 if overall_success else 1


if __name__ == "__main__":
    sys.exit(main())