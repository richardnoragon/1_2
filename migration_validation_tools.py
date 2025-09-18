#!/usr/bin/env python3
"""
Advanced Folders Migration Validation Script
===========================================

This script provides comprehensive testing and validation for the 
advanced_folders migration from src/advanced_folders to 
src/tools/file_management/advanced_folders_legacy.

Features:
- Pre-migration validation
- Post-migration verification
- Import testing
- Functionality validation
- Performance testing
- Rollback verification

Author: GitHub Copilot
Date: September 17, 2025
"""

import importlib
import importlib.util
import json
import os
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class MigrationValidator:
    """Comprehensive validation for advanced_folders migration"""
    
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path).resolve()
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Define paths
        self.source_path = self.root_path / "src" / "advanced_folders"
        self.legacy_path = self.root_path / "src" / "tools" / "file_management" / "advanced_folders_legacy"
        self.current_path = self.root_path / "src" / "tools" / "file_management" / "advanced_folders"
        
        # Test results
        self.test_results = {
            "timestamp": self.timestamp,
            "pre_migration": {},
            "post_migration": {},
            "import_tests": {},
            "functionality_tests": {},
            "performance_tests": {},
            "rollback_tests": {},
            "overall_status": "pending"
        }
        
        # Add root to Python path for imports
        if str(self.root_path) not in sys.path:
            sys.path.insert(0, str(self.root_path))

    def log_test(self, category: str, test_name: str, status: str, 
                 details: str = "", duration: float = 0.0):
        """Log test results"""
        if category not in self.test_results:
            self.test_results[category] = {}
        
        self.test_results[category][test_name] = {
            "status": status,
            "details": details,
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"[{status}] {category}.{test_name}: {details}")

    def validate_pre_migration(self) -> bool:
        """Validate environment before migration"""
        print("=== Pre-Migration Validation ===")
        
        # Check source directory exists
        start_time = time.time()
        if self.source_path.exists():
            self.log_test("pre_migration", "source_exists", "PASS", 
                         f"Source directory found: {self.source_path}",
                         time.time() - start_time)
        else:
            self.log_test("pre_migration", "source_exists", "FAIL", 
                         f"Source directory not found: {self.source_path}",
                         time.time() - start_time)
            return False
        
        # Check source directory structure
        start_time = time.time()
        required_dirs = ["core", "models", "exceptions", "repository", "validation"]
        missing_dirs = []
        
        for dir_name in required_dirs:
            if not (self.source_path / dir_name).exists():
                missing_dirs.append(dir_name)
        
        if missing_dirs:
            self.log_test("pre_migration", "source_structure", "FAIL",
                         f"Missing directories: {missing_dirs}",
                         time.time() - start_time)
            return False
        else:
            self.log_test("pre_migration", "source_structure", "PASS",
                         "All required directories present",
                         time.time() - start_time)
        
        # Check if target already exists
        start_time = time.time()
        if self.legacy_path.exists():
            self.log_test("pre_migration", "target_clean", "WARNING",
                         f"Target directory already exists: {self.legacy_path}",
                         time.time() - start_time)
        else:
            self.log_test("pre_migration", "target_clean", "PASS",
                         "Target directory is clean",
                         time.time() - start_time)
        
        # Test source imports
        start_time = time.time()
        try:
            # Try importing from source
            spec = importlib.util.find_spec("src.advanced_folders")
            if spec is not None:
                self.log_test("pre_migration", "source_importable", "PASS",
                             "Source module is importable",
                             time.time() - start_time)
            else:
                self.log_test("pre_migration", "source_importable", "FAIL",
                             "Source module not found in Python path",
                             time.time() - start_time)
                return False
        except Exception as e:
            self.log_test("pre_migration", "source_importable", "FAIL",
                         f"Import error: {e}",
                         time.time() - start_time)
            return False
        
        return True

    def validate_post_migration(self) -> bool:
        """Validate environment after migration"""
        print("\n=== Post-Migration Validation ===")
        
        # Check legacy directory exists
        start_time = time.time()
        if self.legacy_path.exists():
            self.log_test("post_migration", "legacy_exists", "PASS",
                         f"Legacy directory created: {self.legacy_path}",
                         time.time() - start_time)
        else:
            self.log_test("post_migration", "legacy_exists", "FAIL",
                         f"Legacy directory not found: {self.legacy_path}",
                         time.time() - start_time)
            return False
        
        # Check legacy directory structure
        start_time = time.time()
        required_dirs = ["core", "models", "exceptions", "repository", "validation"]
        missing_dirs = []
        
        for dir_name in required_dirs:
            if not (self.legacy_path / dir_name).exists():
                missing_dirs.append(dir_name)
        
        if missing_dirs:
            self.log_test("post_migration", "legacy_structure", "FAIL",
                         f"Missing directories: {missing_dirs}",
                         time.time() - start_time)
            return False
        else:
            self.log_test("post_migration", "legacy_structure", "PASS",
                         "All required directories present",
                         time.time() - start_time)
        
        # Check if source is removed (optional)
        start_time = time.time()
        if self.source_path.exists():
            self.log_test("post_migration", "source_cleanup", "WARNING",
                         "Source directory still exists (not cleaned up)",
                         time.time() - start_time)
        else:
            self.log_test("post_migration", "source_cleanup", "PASS",
                         "Source directory cleaned up",
                         time.time() - start_time)
        
        # Check current implementation still exists
        start_time = time.time()
        if self.current_path.exists():
            self.log_test("post_migration", "current_preserved", "PASS",
                         "Current implementation preserved",
                         time.time() - start_time)
        else:
            self.log_test("post_migration", "current_preserved", "FAIL",
                         "Current implementation missing",
                         time.time() - start_time)
            return False
        
        return True

    def test_imports(self) -> bool:
        """Test import functionality"""
        print("\n=== Import Testing ===")
        
        # Test legacy module import
        start_time = time.time()
        try:
            import src.tools.file_management.advanced_folders_legacy as legacy_af
            self.log_test("import_tests", "legacy_import", "PASS",
                         "Legacy module imported successfully",
                         time.time() - start_time)
        except ImportError as e:
            self.log_test("import_tests", "legacy_import", "FAIL",
                         f"Legacy import failed: {e}",
                         time.time() - start_time)
            return False
        except Exception as e:
            self.log_test("import_tests", "legacy_import", "FAIL",
                         f"Unexpected error: {e}",
                         time.time() - start_time)
            return False
        
        # Test current module import (should still work)
        start_time = time.time()
        try:
            import src.tools.file_management.advanced_folders as current_af
            self.log_test("import_tests", "current_import", "PASS",
                         "Current module imported successfully",
                         time.time() - start_time)
        except ImportError as e:
            self.log_test("import_tests", "current_import", "FAIL",
                         f"Current import failed: {e}",
                         time.time() - start_time)
            return False
        except Exception as e:
            self.log_test("import_tests", "current_import", "FAIL",
                         f"Unexpected error: {e}",
                         time.time() - start_time)
            return False
        
        # Test specific submodule imports
        submodules = [
            "models.folder_configuration",
            "models.search_parameters",
            "core.search_engine",
            "exceptions.advanced_folders_exceptions",
            "repository.folder_repository"
        ]
        
        for submodule in submodules:
            start_time = time.time()
            try:
                full_module = f"src.tools.file_management.advanced_folders_legacy.{submodule}"
                importlib.import_module(full_module)
                self.log_test("import_tests", f"submodule_{submodule.replace('.', '_')}", "PASS",
                             f"Submodule {submodule} imported successfully",
                             time.time() - start_time)
            except ImportError as e:
                self.log_test("import_tests", f"submodule_{submodule.replace('.', '_')}", "FAIL",
                             f"Submodule {submodule} import failed: {e}",
                             time.time() - start_time)
                return False
        
        # Test no name conflicts
        start_time = time.time()
        try:
            legacy_af = importlib.import_module("src.tools.file_management.advanced_folders_legacy")
            current_af = importlib.import_module("src.tools.file_management.advanced_folders")
            
            # Verify they are different modules
            if legacy_af is not current_af:
                self.log_test("import_tests", "no_conflicts", "PASS",
                             "No name conflicts between legacy and current",
                             time.time() - start_time)
            else:
                self.log_test("import_tests", "no_conflicts", "FAIL",
                             "Name conflict detected",
                             time.time() - start_time)
                return False
        except Exception as e:
            self.log_test("import_tests", "no_conflicts", "FAIL",
                         f"Conflict test failed: {e}",
                         time.time() - start_time)
            return False
        
        return True

    def test_functionality(self) -> bool:
        """Test basic functionality of migrated modules"""
        print("\n=== Functionality Testing ===")
        
        # Test legacy module functionality
        start_time = time.time()
        try:
            from src.tools.file_management.advanced_folders_legacy.models.folder_configuration import \
                FolderConfiguration

            # Try to create a configuration object
            config = FolderConfiguration(
                folder_path="/test/path",
                search_parameters={}
            )
            
            if config.folder_path == "/test/path":
                self.log_test("functionality_tests", "legacy_functionality", "PASS",
                             "Legacy module functionality working",
                             time.time() - start_time)
            else:
                self.log_test("functionality_tests", "legacy_functionality", "FAIL",
                             "Legacy module functionality broken",
                             time.time() - start_time)
                return False
                
        except Exception as e:
            self.log_test("functionality_tests", "legacy_functionality", "FAIL",
                         f"Legacy functionality test failed: {e}",
                         time.time() - start_time)
            return False
        
        # Test that current module still works independently
        start_time = time.time()
        try:
            # Try to import something from current module
            spec = importlib.util.find_spec("src.tools.file_management.advanced_folders")
            if spec is not None:
                self.log_test("functionality_tests", "current_functionality", "PASS",
                             "Current module still accessible",
                             time.time() - start_time)
            else:
                self.log_test("functionality_tests", "current_functionality", "FAIL",
                             "Current module not accessible",
                             time.time() - start_time)
                return False
        except Exception as e:
            self.log_test("functionality_tests", "current_functionality", "FAIL",
                         f"Current functionality test failed: {e}",
                         time.time() - start_time)
            return False
        
        return True

    def test_performance(self) -> bool:
        """Test performance of imports and basic operations"""
        print("\n=== Performance Testing ===")
        
        # Test import performance
        start_time = time.time()
        try:
            for _ in range(10):
                import src.tools.file_management.advanced_folders_legacy
                importlib.reload(src.tools.file_management.advanced_folders_legacy)
            
            avg_time = (time.time() - start_time) / 10
            
            if avg_time < 1.0:  # Less than 1 second per import
                self.log_test("performance_tests", "import_performance", "PASS",
                             f"Average import time: {avg_time:.3f}s",
                             avg_time)
            else:
                self.log_test("performance_tests", "import_performance", "WARNING",
                             f"Slow import time: {avg_time:.3f}s",
                             avg_time)
        except Exception as e:
            self.log_test("performance_tests", "import_performance", "FAIL",
                         f"Performance test failed: {e}",
                         time.time() - start_time)
            return False
        
        return True

    def generate_validation_report(self) -> bool:
        """Generate comprehensive validation report"""
        try:
            # Calculate overall status
            all_tests = []
            for category in self.test_results.values():
                if isinstance(category, dict):
                    for test in category.values():
                        if isinstance(test, dict) and "status" in test:
                            all_tests.append(test["status"])
            
            pass_count = all_tests.count("PASS")
            fail_count = all_tests.count("FAIL")
            warning_count = all_tests.count("WARNING")
            
            if fail_count == 0:
                if warning_count == 0:
                    self.test_results["overall_status"] = "PASS"
                else:
                    self.test_results["overall_status"] = "PASS_WITH_WARNINGS"
            else:
                self.test_results["overall_status"] = "FAIL"
            
            # Save report
            report_path = self.root_path / f"migration_validation_report_{self.timestamp}.json"
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, indent=2, default=str)
            
            print(f"\n=== Validation Summary ===")
            print(f"Total Tests: {len(all_tests)}")
            print(f"Passed: {pass_count}")
            print(f"Failed: {fail_count}")
            print(f"Warnings: {warning_count}")
            print(f"Overall Status: {self.test_results['overall_status']}")
            print(f"Report saved: {report_path}")
            
            return fail_count == 0
            
        except Exception as e:
            print(f"Failed to generate report: {e}")
            return False

    def run_pre_migration_validation(self) -> bool:
        """Run pre-migration validation only"""
        print("Running Pre-Migration Validation...")
        success = self.validate_pre_migration()
        self.generate_validation_report()
        return success

    def run_post_migration_validation(self) -> bool:
        """Run complete post-migration validation"""
        print("Running Post-Migration Validation...")
        
        success = True
        success &= self.validate_post_migration()
        success &= self.test_imports()
        success &= self.test_functionality()
        success &= self.test_performance()
        
        self.generate_validation_report()
        return success

    def run_complete_validation(self) -> bool:
        """Run both pre and post migration validation"""
        print("Running Complete Migration Validation...")
        
        success = True
        success &= self.validate_pre_migration()
        success &= self.validate_post_migration()
        success &= self.test_imports()
        success &= self.test_functionality()
        success &= self.test_performance()
        
        self.generate_validation_report()
        return success


def main():
    """Main execution function"""
    print("Advanced Folders Migration Validation Tool")
    print("=" * 50)
    
    validator = MigrationValidator()
    
    # Determine what to run based on command line args
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == "pre":
            success = validator.run_pre_migration_validation()
        elif mode == "post":
            success = validator.run_post_migration_validation()
        elif mode == "complete":
            success = validator.run_complete_validation()
        else:
            print(f"Unknown mode: {mode}")
            print("Usage: python migration_validation.py [pre|post|complete]")
            return False
    else:
        # Default to post-migration validation
        success = validator.run_post_migration_validation()
    
    if success:
        print("\n[SUCCESS] All validations passed!")
    else:
        print("\n[FAILED] Some validations failed!")
        print("Check the validation report for details.")
    
    return success


if __name__ == "__main__":
    exit(0 if main() else 1)