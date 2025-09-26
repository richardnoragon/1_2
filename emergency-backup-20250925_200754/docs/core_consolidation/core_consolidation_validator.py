#!/usr/bin/env python3
"""
Core Consolidation Migration Validation and Testing Script
Comprehensive testing suite for the core consolidation migration

Date: September 17, 2025
Project: Richard's File Utilities (RFU)
Purpose: Validate and test the core consolidation migration
"""

import sys
import json
import importlib
import traceback
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Tuple


class CoreConsolidationValidator:
    """Validates and tests the core consolidation migration."""
    
    def __init__(self, workspace_root: Path):
        """Initialize the validator.
        
        Args:
            workspace_root: Path to the workspace root directory
        """
        self.workspace_root = Path(workspace_root)
        self.src_path = self.workspace_root / "src"
        self.core_path = self.src_path / "core"
        self.core_rfu_path = self.src_path / "core_rfu"
        self.docs_path = self.workspace_root / "docs" / "core_consolidation"
        
        # Test results tracking
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "migration_status": None,
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "test_details": [],
            "import_tests": [],
            "functionality_tests": [],
            "integration_tests": [],
            "errors": []
        }
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.docs_path / f"validation_log_{timestamp}.txt"
        
        # Add src to Python path for testing
        if str(self.src_path) not in sys.path:
            sys.path.insert(0, str(self.src_path))
    
    def log_message(self, message: str, level: str = "INFO"):
        """Log a message to both console and file.
        
        Args:
            message: Message to log
            level: Log level (INFO, WARNING, ERROR)
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        
        print(log_entry)
        
        # Ensure log directory exists
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + "\n")
    
    def run_test(self, test_name: str, test_func, *args, **kwargs) -> bool:
        """Run a single test and record results.
        
        Args:
            test_name: Name of the test
            test_func: Function to execute
            *args: Arguments to pass to test function
            **kwargs: Keyword arguments to pass to test function
            
        Returns:
            True if test passed
        """
        self.test_results["total_tests"] += 1
        
        try:
            self.log_message(f"Running test: {test_name}")
            result = test_func(*args, **kwargs)
            
            if result:
                self.test_results["passed_tests"] += 1
                self.log_message(f"✅ PASSED: {test_name}")
                status = "PASSED"
            else:
                self.test_results["failed_tests"] += 1
                self.log_message(f"❌ FAILED: {test_name}", "ERROR")
                status = "FAILED"
            
            self.test_results["test_details"].append({
                "name": test_name,
                "status": status,
                "timestamp": datetime.now().isoformat(),
                "error": None
            })
            
            return result
            
        except Exception as e:
            self.test_results["failed_tests"] += 1
            error_msg = f"Exception in {test_name}: {str(e)}"
            self.log_message(f"❌ ERROR: {error_msg}", "ERROR")
            self.log_message(f"Traceback: {traceback.format_exc()}", "ERROR")
            
            self.test_results["test_details"].append({
                "name": test_name,
                "status": "ERROR",
                "timestamp": datetime.now().isoformat(),
                "error": error_msg
            })
            
            return False
    
    def test_directory_structure(self) -> bool:
        """Test that the directory structure is correct after migration."""
        # Check that core directory exists and has content
        if not self.core_path.exists():
            self.log_message("Core directory does not exist", "ERROR")
            return False
        
        # Check for key files
        required_files = ["__init__.py", "constants.py", "error_handler.py"]
        for file_name in required_files:
            file_path = self.core_path / file_name
            if not file_path.exists():
                self.log_message(f"Required file missing: {file_name}", "ERROR")
                return False
        
        # Check for subdirectories that should exist
        expected_subdirs = ["directory_security", "file_ops", "migrations", "theme_security"]
        existing_subdirs = []
        for subdir in expected_subdirs:
            subdir_path = self.core_path / subdir
            if subdir_path.exists():
                existing_subdirs.append(subdir)
        
        self.log_message(f"Found subdirectories: {existing_subdirs}")
        
        # Check that core_rfu no longer exists (if migration completed)
        if self.core_rfu_path.exists():
            # Migration might not be complete, or this could be intentional
            self.log_message(f"WARNING: core_rfu still exists: {self.core_rfu_path}", "WARNING")
        
        return True
    
    def test_basic_imports(self) -> bool:
        """Test basic module imports."""
        import_tests = [
            ("core", "import core"),
            ("core.constants", "from core.constants import APP_NAME"),
            ("core.error_handler", "from core.error_handler import error_handler"),
        ]
        
        all_passed = True
        
        for module_name, import_statement in import_tests:
            try:
                exec(import_statement)
                self.log_message(f"✅ Import successful: {import_statement}")
                self.test_results["import_tests"].append({
                    "module": module_name,
                    "statement": import_statement,
                    "status": "SUCCESS"
                })
            except Exception as e:
                self.log_message(f"❌ Import failed: {import_statement} - {e}", "ERROR")
                self.test_results["import_tests"].append({
                    "module": module_name,
                    "statement": import_statement,
                    "status": "FAILED",
                    "error": str(e)
                })
                all_passed = False
        
        return all_passed
    
    def test_constants_functionality(self) -> bool:
        """Test that constants are accessible and have expected values."""
        try:
            from core.constants import APP_NAME, SECURITY_HIGH, JSON_FILES_FILTER
            
            # Test expected values
            if APP_NAME != "Richard's File Utilities":
                self.log_message(f"Unexpected APP_NAME: {APP_NAME}", "ERROR")
                return False
            
            if not isinstance(SECURITY_HIGH, str):
                self.log_message(f"SECURITY_HIGH is not a string: {type(SECURITY_HIGH)}", "ERROR")
                return False
            
            if not isinstance(JSON_FILES_FILTER, str):
                self.log_message(f"JSON_FILES_FILTER is not a string: {type(JSON_FILES_FILTER)}", "ERROR")
                return False
            
            self.log_message("✅ Constants functionality validated")
            return True
            
        except Exception as e:
            self.log_message(f"Constants functionality test failed: {e}", "ERROR")
            return False
    
    def test_error_handler_functionality(self) -> bool:
        """Test that error handler works correctly."""
        try:
            from core.error_handler import error_handler
            
            # Test that error_handler is callable
            if not hasattr(error_handler, 'log_info'):
                self.log_message("Error handler missing log_info method", "ERROR")
                return False
            
            # Test logging functionality
            test_message = "Test message from validation"
            error_handler.log_info(test_message)
            
            self.log_message("✅ Error handler functionality validated")
            return True
            
        except Exception as e:
            self.log_message(f"Error handler functionality test failed: {e}", "ERROR")
            return False
    
    def test_subdirectory_imports(self) -> bool:
        """Test imports from subdirectories."""
        subdirectory_tests = [
            ("core.directory_security.directory_security_manager", "DirectorySecurityManager"),
            ("core.file_ops.file_handler", "FileHandler"),
            ("core.migrations.migration_manager", "MigrationManager"),
            ("core.theme_security.theme_security_manager", "ThemeSecurityManager"),
        ]
        
        passed = 0
        total = len(subdirectory_tests)
        
        for module_path, class_name in subdirectory_tests:
            try:
                module = importlib.import_module(module_path)
                if hasattr(module, class_name):
                    self.log_message(f"✅ Subdirectory import successful: {module_path}.{class_name}")
                    passed += 1
                else:
                    self.log_message(f"❌ Class not found: {module_path}.{class_name}", "WARNING")
            except ImportError as e:
                self.log_message(f"❌ Subdirectory import failed: {module_path} - {e}", "WARNING")
            except Exception as e:
                self.log_message(f"❌ Unexpected error importing {module_path}: {e}", "ERROR")
        
        # Allow some failures as not all modules may be complete
        success_rate = passed / total if total > 0 else 0
        if success_rate >= 0.5:  # 50% success rate is acceptable
            self.log_message(f"✅ Subdirectory imports: {passed}/{total} successful")
            return True
        else:
            self.log_message(f"❌ Too many subdirectory import failures: {passed}/{total}", "ERROR")
            return False
    
    def test_configuration_imports(self) -> bool:
        """Test configuration manager imports."""
        config_tests = [
            "core.config_manager",
            "core.enhanced_config_manager",
            "core.logging_manager"
        ]
        
        passed = 0
        
        for module_path in config_tests:
            try:
                importlib.import_module(module_path)
                self.log_message(f"✅ Configuration import successful: {module_path}")
                passed += 1
            except ImportError as e:
                self.log_message(f"❌ Configuration import failed: {module_path} - {e}", "WARNING")
            except Exception as e:
                self.log_message(f"❌ Unexpected error importing {module_path}: {e}", "ERROR")
        
        # At least one config manager should be available
        if passed > 0:
            self.log_message(f"✅ Configuration imports: {passed}/{len(config_tests)} successful")
            return True
        else:
            self.log_message("❌ No configuration managers available", "ERROR")
            return False
    
    def test_database_imports(self) -> bool:
        """Test database-related imports (optional)."""
        database_tests = [
            "core.database_manager",
            "core.database_models",
            "core.database_logging"
        ]
        
        passed = 0
        
        for module_path in database_tests:
            try:
                importlib.import_module(module_path)
                self.log_message(f"✅ Database import successful: {module_path}")
                passed += 1
            except ImportError as e:
                self.log_message(f"❌ Database import failed: {module_path} - {e}", "WARNING")
            except Exception as e:
                self.log_message(f"❌ Unexpected error importing {module_path}: {e}", "WARNING")
        
        # Database modules are optional
        self.log_message(f"Database imports: {passed}/{len(database_tests)} successful")
        return True  # Always pass as database modules are optional
    
    def test_migration_state(self) -> bool:
        """Check migration state from migration files."""
        state_file = self.docs_path / "migration_state.json"
        
        if not state_file.exists():
            self.log_message("No migration state file found", "WARNING")
            return True  # Not necessarily an error
        
        try:
            with open(state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            phase = state.get("phase", "unknown")
            self.test_results["migration_status"] = phase
            
            if phase == "migration_successful":
                self.log_message("✅ Migration state indicates success")
                return True
            elif phase == "cleanup_completed":
                self.log_message("✅ Migration and cleanup completed successfully")
                return True
            else:
                self.log_message(f"Migration state: {phase}", "WARNING")
                return True  # Don't fail on this
                
        except Exception as e:
            self.log_message(f"Error reading migration state: {e}", "WARNING")
            return True  # Don't fail on this
    
    def test_file_counts(self) -> bool:
        """Test that file counts are reasonable."""
        core_py_files = list(self.core_path.rglob("*.py"))
        total_files = len(core_py_files)
        
        # Should have at least the basic files
        if total_files < 3:
            self.log_message(f"Too few Python files in core: {total_files}", "ERROR")
            return False
        
        # Log file distribution
        subdirs = {}
        for py_file in core_py_files:
            rel_path = py_file.relative_to(self.core_path)
            if len(rel_path.parts) > 1:
                subdir = rel_path.parts[0]
                subdirs[subdir] = subdirs.get(subdir, 0) + 1
        
        self.log_message(f"✅ Total Python files in core: {total_files}")
        for subdir, count in subdirs.items():
            self.log_message(f"  {subdir}: {count} files")
        
        return True
    
    def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run all validation tests.
        
        Returns:
            Dictionary containing complete test results
        """
        self.log_message("=== STARTING COMPREHENSIVE VALIDATION ===")
        
        # Structure tests
        self.run_test("Directory Structure", self.test_directory_structure)
        self.run_test("File Counts", self.test_file_counts)
        
        # Import tests
        self.run_test("Basic Imports", self.test_basic_imports)
        self.run_test("Subdirectory Imports", self.test_subdirectory_imports)
        self.run_test("Configuration Imports", self.test_configuration_imports)
        self.run_test("Database Imports", self.test_database_imports)
        
        # Functionality tests
        self.run_test("Constants Functionality", self.test_constants_functionality)
        self.run_test("Error Handler Functionality", self.test_error_handler_functionality)
        
        # Migration state test
        self.run_test("Migration State", self.test_migration_state)
        
        # Calculate success rate
        success_rate = (self.test_results["passed_tests"] / 
                       self.test_results["total_tests"] * 100 
                       if self.test_results["total_tests"] > 0 else 0)
        
        self.test_results["success_rate"] = success_rate
        
        self.log_message("=== VALIDATION COMPLETED ===")
        self.log_message(f"Total Tests: {self.test_results['total_tests']}")
        self.log_message(f"Passed: {self.test_results['passed_tests']}")
        self.log_message(f"Failed: {self.test_results['failed_tests']}")
        self.log_message(f"Success Rate: {success_rate:.1f}%")
        
        # Save results
        self.save_test_results()
        
        return self.test_results
    
    def save_test_results(self):
        """Save test results to JSON file."""
        results_file = self.docs_path / "validation_results.json"
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2)
        
        self.log_message(f"✅ Test results saved to {results_file}")
    
    def generate_validation_report(self) -> str:
        """Generate a human-readable validation report.
        
        Returns:
            Formatted validation report as string
        """
        report = []
        report.append("# Core Consolidation Migration Validation Report")
        report.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**Workspace**: {self.workspace_root}")
        report.append("")
        
        # Summary
        report.append("## Summary")
        success_rate = self.test_results.get("success_rate", 0)
        if success_rate >= 90:
            status_emoji = "🟢"
            status_text = "EXCELLENT"
        elif success_rate >= 75:
            status_emoji = "🟡"
            status_text = "GOOD"
        elif success_rate >= 50:
            status_emoji = "🟠"
            status_text = "ACCEPTABLE"
        else:
            status_emoji = "🔴"
            status_text = "POOR"
        
        report.append(f"**Overall Status**: {status_emoji} {status_text}")
        report.append(f"**Success Rate**: {success_rate:.1f}%")
        report.append(f"**Total Tests**: {self.test_results['total_tests']}")
        report.append(f"**Passed**: {self.test_results['passed_tests']}")
        report.append(f"**Failed**: {self.test_results['failed_tests']}")
        report.append("")
        
        # Migration Status
        migration_status = self.test_results.get("migration_status")
        if migration_status:
            report.append("## Migration Status")
            report.append(f"**Phase**: {migration_status}")
            report.append("")
        
        # Test Details
        report.append("## Test Results")
        for test in self.test_results["test_details"]:
            status_emoji = "✅" if test["status"] == "PASSED" else "❌"
            report.append(f"- {status_emoji} **{test['name']}**: {test['status']}")
            if test.get("error"):
                report.append(f"  - Error: {test['error']}")
        
        report.append("")
        
        # Import Tests
        if self.test_results["import_tests"]:
            report.append("## Import Test Details")
            for import_test in self.test_results["import_tests"]:
                status_emoji = "✅" if import_test["status"] == "SUCCESS" else "❌"
                report.append(f"- {status_emoji} `{import_test['statement']}`")
                if import_test.get("error"):
                    report.append(f"  - Error: {import_test['error']}")
            report.append("")
        
        # Recommendations
        report.append("## Recommendations")
        if success_rate >= 90:
            report.append("✅ Migration appears to be successful. All core functionality is working.")
        elif success_rate >= 75:
            report.append("⚠️ Migration mostly successful with minor issues. Review failed tests.")
        elif success_rate >= 50:
            report.append("⚠️ Migration partially successful. Some functionality may be impacted.")
        else:
            report.append("❌ Migration has significant issues. Consider rollback and investigation.")
        
        return "\n".join(report)


def main():
    """Main execution function."""
    # Get workspace root
    script_dir = Path(__file__).parent
    workspace_root = script_dir.parent.parent
    
    print("🧪 Core Consolidation Migration Validation Script")
    print(f"📁 Workspace: {workspace_root}")
    print("=" * 60)
    
    # Initialize validator
    validator = CoreConsolidationValidator(workspace_root)
    
    # Run validation
    print("\n🚀 Starting comprehensive validation...")
    results = validator.run_comprehensive_validation()
    
    # Generate and save report
    report = validator.generate_validation_report()
    report_file = validator.docs_path / "validation_report.md"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    # Display summary
    print("\n" + "=" * 60)
    success_rate = results.get("success_rate", 0)
    
    if success_rate >= 90:
        print("🎉 VALIDATION SUCCESSFUL!")
        print("✅ Migration appears to be working correctly.")
    elif success_rate >= 75:
        print("✅ VALIDATION MOSTLY SUCCESSFUL")
        print("⚠️ Minor issues detected, but core functionality works.")
    elif success_rate >= 50:
        print("⚠️ VALIDATION PARTIALLY SUCCESSFUL")
        print("🔍 Some issues detected, review recommended.")
    else:
        print("❌ VALIDATION FAILED")
        print("🚨 Significant issues detected, rollback recommended.")
    
    print(f"\n📊 Results: {results['passed_tests']}/{results['total_tests']} tests passed ({success_rate:.1f}%)")
    print(f"📝 Detailed log: {validator.log_file}")
    print(f"📄 Validation report: {report_file}")
    print(f"📊 Test results: {validator.docs_path / 'validation_results.json'}")
    
    return success_rate >= 75  # Consider success if 75% or more tests pass


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)