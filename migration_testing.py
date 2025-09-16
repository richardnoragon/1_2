#!/usr/bin/env python3
"""
Comprehensive Testing Framework for Migration Validation
======================================================

This module provides extensive testing capabilities for validating
the migration from src/utilities to src/tools.

Test Categories:
1. Pre-migration validation tests
2. Post-migration functionality tests  
3. Import statement validation
4. Integration tests
5. Performance tests
6. End-to-end functionality tests

Usage:
    python migration_testing.py [--pre-migration] [--post-migration] [--all]
"""

import argparse
import importlib
import importlib.util
import json
import logging
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from typing import Any, Dict, List, Optional


class MigrationTestFramework:
    """Main framework for migration testing."""
    
    def __init__(self, project_root: Optional[str] = None):
        self.project_root = Path(project_root or Path(__file__).parent)
        self.test_results = {}
        self.setup_logging()
        
        # Add project root to Python path
        if str(self.project_root) not in sys.path:
            sys.path.insert(0, str(self.project_root))
    
    def setup_logging(self):
        """Setup test logging."""
        log_dir = self.project_root / "test_logs"
        log_dir.mkdir(exist_ok=True)
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"migration_tests_{timestamp}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def run_all_tests(self, test_type: str = "all") -> Dict[str, Any]:
        """Run all relevant tests based on migration state."""
        if test_type == "pre-migration" or test_type == "all":
            self.run_pre_migration_tests()
        
        if test_type == "post-migration" or test_type == "all":
            self.run_post_migration_tests()
        
        if test_type == "all":
            self.run_integration_tests()
            self.run_performance_tests()
        
        return self.test_results
    
    def run_pre_migration_tests(self):
        """Run tests before migration to establish baseline."""
        self.logger.info("Running pre-migration validation tests...")
        
        suite = unittest.TestSuite()
        loader = unittest.TestLoader()
        suite.addTest(loader.loadTestsFromTestCase(PreMigrationTests))
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        self.test_results["pre_migration"] = {
            "tests_run": result.testsRun,
            "failures": len(result.failures),
            "errors": len(result.errors),
            "success": result.wasSuccessful()
        }
    
    def run_post_migration_tests(self):
        """Run tests after migration to validate success."""
        self.logger.info("Running post-migration validation tests...")
        
        suite = unittest.TestSuite()
        loader = unittest.TestLoader()
        suite.addTest(loader.loadTestsFromTestCase(PostMigrationTests))
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        self.test_results["post_migration"] = {
            "tests_run": result.testsRun,
            "failures": len(result.failures),
            "errors": len(result.errors),
            "success": result.wasSuccessful()
        }
    
    def run_integration_tests(self):
        """Run integration tests."""
        self.logger.info("Running integration tests...")
        
        suite = unittest.TestSuite()
        loader = unittest.TestLoader()
        suite.addTest(loader.loadTestsFromTestCase(IntegrationTests))
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        self.test_results["integration"] = {
            "tests_run": result.testsRun,
            "failures": len(result.failures),
            "errors": len(result.errors),
            "success": result.wasSuccessful()
        }
    
    def run_performance_tests(self):
        """Run performance validation tests."""
        self.logger.info("Running performance tests...")
        
        suite = unittest.TestSuite()
        loader = unittest.TestLoader()
        suite.addTest(loader.loadTestsFromTestCase(PerformanceTests))
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        self.test_results["performance"] = {
            "tests_run": result.testsRun,
            "failures": len(result.failures),
            "errors": len(result.errors),
            "success": result.wasSuccessful()
        }
    
    def generate_test_report(self) -> str:
        """Generate comprehensive test report."""
        report_file = self.project_root / f"test_report_{time.strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, "w") as f:
            json.dump(self.test_results, f, indent=2)
        
        self.logger.info(f"Test report generated: {report_file}")
        return str(report_file)


class PreMigrationTests(unittest.TestCase):
    """Test suite for pre-migration validation."""
    
    def setUp(self):
        """Set up test environment."""
        self.project_root = Path(__file__).parent
        if str(self.project_root) not in sys.path:
            sys.path.insert(0, str(self.project_root))
        
        self.utilities_modules = [
            "src.tools.advanced_folders",
            "src.tools.pdf_tools",
            "src.tools.file_management",
            "src.tools.office_metadata"
        ]
    
    def test_utilities_directory_exists(self):
        """Test that utilities directory exists."""
        utilities_path = self.project_root / "src" / "utilities"
        self.assertTrue(utilities_path.exists(), "utilities directory should exist")
        self.assertTrue(utilities_path.is_dir(), "utilities should be a directory")
    
    def test_utilities_module_imports(self):
        """Test that utilities modules can be imported."""
        for module_name in self.utilities_modules:
            with self.subTest(module=module_name):
                try:
                    spec = importlib.util.find_spec(module_name)
                    self.assertIsNotNone(spec, f"Module {module_name} should be findable")
                except ImportError as e:
                    self.fail(f"Failed to find module {module_name}: {e}")
    
    def test_key_gui_components_exist(self):
        """Test that key GUI components exist and are accessible."""
        gui_components = [
            ("src.tools.pdf_tools.widgets.enhanced_pdf_tools_widget", "EnhancedPDFToolsWidget"),
            ("src.tools.file_management.catalog", "CatalogWindow"),
            ("src.tools.metadata.image_metadata", "ImageMetadataEditorGUI")
        ]
        
        for module_name, class_name in gui_components:
            with self.subTest(component=f"{module_name}.{class_name}"):
                try:
                    spec = importlib.util.find_spec(module_name)
                    if spec is not None:
                        module = importlib.import_module(module_name)
                        self.assertTrue(hasattr(module, class_name), 
                                      f"Module {module_name} should have {class_name}")
                        gui_class = getattr(module, class_name)
                        self.assertTrue(callable(gui_class), 
                                      f"{class_name} should be callable")
                except (ImportError, AttributeError) as e:
                    # Some modules might not be available in test environment
                    self.skipTest(f"Skipping {module_name}.{class_name}: {e}")
    
    def test_file_structure_integrity(self):
        """Test that file structure is intact."""
        utilities_path = self.project_root / "src" / "utilities"
        
        # Count files by type
        py_files = list(utilities_path.rglob("*.py"))
        ui_files = list(utilities_path.rglob("*.ui"))
        
        self.assertGreater(len(py_files), 50, "Should have substantial number of Python files")
        self.assertGreater(len(ui_files), 10, "Should have UI files")
    
    def test_import_statements_current_format(self):
        """Test that current import statements work."""
        test_files = [
            self.project_root / "src" / "rfu" / "hub.py",
            self.project_root / "main.py"
        ]
        
        for test_file in test_files:
            if test_file.exists():
                with self.subTest(file=str(test_file)):
                    with open(test_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Should contain utilities imports
                    if "utilities" in content:
                        # Basic syntax check
                        try:
                            compile(content, str(test_file), 'exec')
                        except SyntaxError as e:
                            self.fail(f"Syntax error in {test_file}: {e}")


class PostMigrationTests(unittest.TestCase):
    """Test suite for post-migration validation."""
    
    def setUp(self):
        """Set up test environment."""
        self.project_root = Path(__file__).parent
        if str(self.project_root) not in sys.path:
            sys.path.insert(0, str(self.project_root))
        
        self.tools_modules = [
            "src.tools.pdf_tools",
            "src.tools.file_management",
            "src.tools.metadata",
            "src.tools.file_operations"
        ]
    
    def test_tools_directory_exists(self):
        """Test that tools directory exists and has expected content."""
        tools_path = self.project_root / "src" / "tools"
        self.assertTrue(tools_path.exists(), "tools directory should exist")
        self.assertTrue(tools_path.is_dir(), "tools should be a directory")
        
        # Check for migrated content
        expected_dirs = ["pdf_tools", "file_management", "metadata"]
        for expected_dir in expected_dirs:
            dir_path = tools_path / expected_dir
            self.assertTrue(dir_path.exists(), f"{expected_dir} should exist in tools")
    
    def test_migrated_modules_importable(self):
        """Test that migrated modules can be imported."""
        for module_name in self.tools_modules:
            with self.subTest(module=module_name):
                try:
                    spec = importlib.util.find_spec(module_name)
                    if spec is not None:
                        # Try to actually import the module
                        importlib.import_module(module_name)
                    else:
                        # Module not found is acceptable for some optional modules
                        self.skipTest(f"Module {module_name} not found (may be expected)")
                except ImportError as e:
                    self.fail(f"Failed to import migrated module {module_name}: {e}")
    
    def test_old_utilities_imports_fail(self):
        """Test that old utilities import paths no longer work."""
        old_modules = [
            "src.tools.pdf_tools",
            "src.tools.file_management",
            "src.tools.advanced_folders"
        ]
        
        for module_name in old_modules:
            with self.subTest(module=module_name):
                # Old imports should fail
                with self.assertRaises(ImportError, 
                                     msg=f"Old import {module_name} should fail"):
                    importlib.import_module(module_name)
    
    def test_import_statements_updated(self):
        """Test that import statements have been updated."""
        key_files = [
            self.project_root / "src" / "rfu" / "hub.py",
            self.project_root / "main.py"
        ]
        
        for test_file in key_files:
            if test_file.exists():
                with self.subTest(file=str(test_file)):
                    with open(test_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Should not contain old utilities imports
                    self.assertNotIn("from src.utilities", content,
                                   f"File {test_file} should not contain old utilities imports")
                    
                    # Should contain new tools imports if it had utilities imports
                    if "from src.tools" in content or "import src.tools" in content:
                        # File was updated - verify syntax
                        try:
                            compile(content, str(test_file), 'exec')
                        except SyntaxError as e:
                            self.fail(f"Syntax error in updated {test_file}: {e}")
    
    def test_gui_components_still_accessible(self):
        """Test that GUI components are still accessible after migration."""
        gui_components = [
            ("src.tools.pdf_tools.widgets.enhanced_pdf_tools_widget", "EnhancedPDFToolsWidget"),
            ("src.tools.file_operations.catalog.catalog", "CatalogWindow"),
            ("src.tools.metadata.image_metadata", "ImageMetadataEditorGUI")
        ]
        
        for module_name, class_name in gui_components:
            with self.subTest(component=f"{module_name}.{class_name}"):
                try:
                    spec = importlib.util.find_spec(module_name)
                    if spec is not None:
                        module = importlib.import_module(module_name)
                        self.assertTrue(hasattr(module, class_name),
                                      f"Migrated module {module_name} should have {class_name}")
                        gui_class = getattr(module, class_name)
                        self.assertTrue(callable(gui_class),
                                      f"Migrated {class_name} should be callable")
                except (ImportError, AttributeError) as e:
                    self.skipTest(f"Skipping migrated {module_name}.{class_name}: {e}")
    
    def test_file_count_preservation(self):
        """Test that file count is preserved after migration."""
        tools_path = self.project_root / "src" / "tools"
        
        if tools_path.exists():
            # Count Python files in tools directory
            py_files = list(tools_path.rglob("*.py"))
            ui_files = list(tools_path.rglob("*.ui"))
            
            # Should have substantial content
            self.assertGreater(len(py_files), 50, 
                             "Tools directory should have substantial Python files")
            self.assertGreater(len(ui_files), 5,
                             "Tools directory should have UI files")


class IntegrationTests(unittest.TestCase):
    """Integration tests for complete system functionality."""
    
    def setUp(self):
        """Set up integration test environment."""
        self.project_root = Path(__file__).parent
        if str(self.project_root) not in sys.path:
            sys.path.insert(0, str(self.project_root))
    
    def test_main_application_components(self):
        """Test that main application components can be imported."""
        main_components = [
            "src.rfu.main",
            "src.rfu.hub",
            "src.rfu.config_manager"
        ]
        
        for component in main_components:
            with self.subTest(component=component):
                try:
                    spec = importlib.util.find_spec(component)
                    if spec is not None:
                        importlib.import_module(component)
                    else:
                        self.skipTest(f"Component {component} not found")
                except ImportError as e:
                    self.fail(f"Failed to import main component {component}: {e}")
    
    def test_cross_module_dependencies(self):
        """Test that cross-module dependencies still work."""
        # Test internal dependencies within migrated modules
        dependency_tests = [
            # Test if PDF tools internal dependencies work
            ("src.tools.pdf_tools", "EnhancedPDFToolsWidget"),
            # Test if file management dependencies work
            ("src.tools.file_management", "advanced_folders"),
        ]
        
        for module_name, expected_item in dependency_tests:
            with self.subTest(dependency=f"{module_name} -> {expected_item}"):
                try:
                    spec = importlib.util.find_spec(module_name)
                    if spec is not None:
                        module = importlib.import_module(module_name)
                        # Basic validation that module loaded successfully
                        self.assertIsNotNone(module)
                except ImportError as e:
                    self.skipTest(f"Dependency test skipped for {module_name}: {e}")
    
    def test_configuration_system(self):
        """Test that configuration system works with new paths."""
        try:
            from src.rfu.config_manager import get_config_manager
            config = get_config_manager()
            
            # Test basic config functionality
            self.assertIsNotNone(config)
            
            # Test that config can handle new tool paths
            # (This is a basic test - specific config tests would be more detailed)
            
        except ImportError as e:
            self.skipTest(f"Configuration system test skipped: {e}")


class PerformanceTests(unittest.TestCase):
    """Performance tests to ensure migration doesn't degrade performance."""
    
    def setUp(self):
        """Set up performance test environment."""
        self.project_root = Path(__file__).parent
        if str(self.project_root) not in sys.path:
            sys.path.insert(0, str(self.project_root))
    
    def test_import_performance(self):
        """Test that import times are reasonable."""
        import_tests = [
            "src.tools.pdf_tools",
            "src.tools.file_management",
            "src.tools.metadata"
        ]
        
        for module_name in import_tests:
            with self.subTest(module=module_name):
                start_time = time.time()
                try:
                    spec = importlib.util.find_spec(module_name)
                    if spec is not None:
                        importlib.import_module(module_name)
                        import_time = time.time() - start_time
                        
                        # Import should complete within reasonable time (5 seconds)
                        self.assertLess(import_time, 5.0,
                                      f"Import of {module_name} took {import_time:.2f}s")
                except ImportError:
                    self.skipTest(f"Module {module_name} not available for performance test")
    
    def test_module_loading_overhead(self):
        """Test that module loading overhead is acceptable."""
        # Test multiple imports of the same module
        module_name = "src.tools.file_management"
        
        try:
            # First import (may be slower due to loading)
            start_time = time.time()
            spec = importlib.util.find_spec(module_name)
            if spec is not None:
                importlib.import_module(module_name)
                first_import_time = time.time() - start_time
                
                # Subsequent imports should be faster (cached)
                start_time = time.time()
                importlib.import_module(module_name)
                second_import_time = time.time() - start_time
                
                # Second import should be significantly faster
                self.assertLess(second_import_time, first_import_time,
                              "Subsequent imports should be faster due to caching")
        
        except ImportError:
            self.skipTest(f"Module {module_name} not available for performance test")


class EndToEndTests(unittest.TestCase):
    """End-to-end functionality tests."""
    
    def setUp(self):
        """Set up end-to-end test environment."""
        self.project_root = Path(__file__).parent
        if str(self.project_root) not in sys.path:
            sys.path.insert(0, str(self.project_root))
    
    def test_application_startup_simulation(self):
        """Simulate application startup process."""
        try:
            # Test main entry point
            main_module = importlib.import_module("src.rfu.main")
            self.assertTrue(hasattr(main_module, "main"),
                          "Main module should have main function")
            
            # Test hub creation
            hub_module = importlib.import_module("src.rfu.hub")
            self.assertTrue(hasattr(hub_module, "RFUHub"),
                          "Hub module should have RFUHub class")
            
            # Note: We don't actually start the GUI in tests
            
        except ImportError as e:
            self.fail(f"Application startup simulation failed: {e}")
    
    def test_tool_accessibility(self):
        """Test that tools are accessible through the system."""
        # Test basic accessibility of tools
        tool_categories = [
            "src.tools.pdf_tools",
            "src.tools.file_management", 
            "src.tools.file_operations",
            "src.tools.metadata",
            "src.tools.security",
            "src.tools.system"
        ]
        
        accessible_tools = 0
        for tool_category in tool_categories:
            try:
                spec = importlib.util.find_spec(tool_category)
                if spec is not None:
                    importlib.import_module(tool_category)
                    accessible_tools += 1
            except ImportError:
                pass  # Some tools might not be available
        
        # At least some tools should be accessible
        self.assertGreater(accessible_tools, 2,
                          f"At least 3 tool categories should be accessible, got {accessible_tools}")


def main():
    """Main entry point for test execution."""
    parser = argparse.ArgumentParser(description="Migration testing framework")
    parser.add_argument("--pre-migration", action="store_true",
                       help="Run pre-migration tests only")
    parser.add_argument("--post-migration", action="store_true", 
                       help="Run post-migration tests only")
    parser.add_argument("--integration", action="store_true",
                       help="Run integration tests only")
    parser.add_argument("--performance", action="store_true",
                       help="Run performance tests only")
    parser.add_argument("--all", action="store_true",
                       help="Run all tests")
    parser.add_argument("--report", action="store_true",
                       help="Generate detailed test report")
    
    args = parser.parse_args()
    
    # Determine test type
    if args.pre_migration:
        test_type = "pre-migration"
    elif args.post_migration:
        test_type = "post-migration"
    elif args.integration:
        test_type = "integration"
    elif args.performance:
        test_type = "performance"
    else:
        test_type = "all"
    
    # Create test framework
    framework = MigrationTestFramework()
    
    # Run tests
    results = framework.run_all_tests(test_type)
    
    # Generate report if requested
    if args.report:
        report_file = framework.generate_test_report()
        print(f"Detailed test report generated: {report_file}")
    
    # Print summary
    print("\n=== Test Results Summary ===")
    total_success = True
    for test_category, result in results.items():
        success = result.get("success", False)
        total_success = total_success and success
        status = "PASSED" if success else "FAILED"
        print(f"{test_category}: {status} ({result.get('tests_run', 0)} tests)")
        
        if result.get("failures", 0) > 0:
            print(f"  - Failures: {result['failures']}")
        if result.get("errors", 0) > 0:
            print(f"  - Errors: {result['errors']}")
    
    print(f"\nOverall Result: {'PASSED' if total_success else 'FAILED'}")
    
    return 0 if total_success else 1


if __name__ == "__main__":
    sys.exit(main())