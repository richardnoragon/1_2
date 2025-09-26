#!/usr/bin/env python3
"""
Size Analyzer Configuration Test Script

This script validates the configuration management and resource path updates
for Phase 5 of the size analyzer migration.
"""

import os
import sys
import json
import traceback
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from core.config_manager import ConfigManager
    from file_utilities_2.core.size_analyzer_config import SizeAnalyzerConfig
    from file_utilities_2.core.size_analyzer_logging import (
        get_size_analyzer_logger, cleanup_logging
    )
    from file_utilities_2.core.size_analyzer_logic import SizeAnalyzer
    from file_utilities_2.gui.size_analyzer_gui import SizeAnalyzerGUI
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure all modules are properly installed and accessible.")
    sys.exit(1)


class ConfigurationValidator:
    """Validates Size Analyzer configuration and resource management."""
    
    def __init__(self):
        """Initialize the configuration validator."""
        self.results = {
            'passed': 0,
            'failed': 0,
            'warnings': 0,
            'tests': []
        }
        self.config_manager = None
        self.size_analyzer_config = None
        self.logger = None
    
    def log_test(self, test_name: str, status: str, message: str, 
                 details: str = None):
        """Log a test result."""
        test_result = {
            'test': test_name,
            'status': status,
            'message': message,
            'details': details
        }
        
        self.results['tests'].append(test_result)
        
        if status == 'PASS':
            self.results['passed'] += 1
            print(f"✓ {test_name}: {message}")
        elif status == 'FAIL':
            self.results['failed'] += 1
            print(f"✗ {test_name}: {message}")
            if details:
                print(f"  Details: {details}")
        elif status == 'WARN':
            self.results['warnings'] += 1
            print(f"⚠ {test_name}: {message}")
    
    def test_main_configuration_loading(self):
        """Test main configuration loading."""
        try:
            self.config_manager = ConfigManager()
            config = self.config_manager.get_config()
            
            if config:
                self.log_test(
                    "Main Configuration Loading",
                    "PASS",
                    "Main configuration loaded successfully"
                )
                return True
            else:
                self.log_test(
                    "Main Configuration Loading",
                    "FAIL",
                    "Main configuration is empty or None"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Main Configuration Loading",
                "FAIL",
                "Failed to load main configuration",
                str(e)
            )
            return False
    
    def test_size_analyzer_configuration_section(self):
        """Test size analyzer configuration section."""
        try:
            config = self.config_manager.config
            
            if 'size_analyzer' in config:
                size_analyzer_config = config['size_analyzer']
                
                # Check required subsections
                required_sections = [
                    'general', 'analysis', 'export', 'ui', 
                    'performance', 'resources', 'hub_integration', 'logging'
                ]
                
                missing_sections = []
                for section in required_sections:
                    if section not in size_analyzer_config:
                        missing_sections.append(section)
                
                if missing_sections:
                    self.log_test(
                        "Size Analyzer Configuration Section",
                        "FAIL",
                        "Missing required subsections",
                        f"Missing: {', '.join(missing_sections)}"
                    )
                    return False
                else:
                    self.log_test(
                        "Size Analyzer Configuration Section",
                        "PASS",
                        "All required subsections present"
                    )
                    return True
            else:
                self.log_test(
                    "Size Analyzer Configuration Section",
                    "FAIL",
                    "Size analyzer section not found in configuration"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Size Analyzer Configuration Section",
                "FAIL",
                "Error checking size analyzer configuration section",
                str(e)
            )
            return False
    
    def test_size_analyzer_config_manager(self):
        """Test Size Analyzer configuration manager."""
        try:
            self.size_analyzer_config = SizeAnalyzerConfig(self.config_manager)
            
            # Test getting settings
            module_path = self.size_analyzer_config.get_setting(
                'general', 'module_path'
            )
            
            if module_path == 'file_utilities_2.gui.size_analyzer_gui':
                self.log_test(
                    "Size Analyzer Config Manager",
                    "PASS",
                    "Configuration manager working correctly"
                )
                return True
            else:
                self.log_test(
                    "Size Analyzer Config Manager",
                    "FAIL",
                    f"Unexpected module path: {module_path}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Size Analyzer Config Manager",
                "FAIL",
                "Error initializing Size Analyzer configuration manager",
                str(e)
            )
            return False
    
    def test_resource_paths(self):
        """Test resource path resolution."""
        try:
            resources_to_check = [
                ('icon_path', 'file_utilities_2/gui/icons/size_analyzer.png'),
                ('ui_file', 'file_utilities_2/gui/size_analyzer.ui'),
                ('help_file', 'file_utilities_2/docs/size_analyzer_help.html')
            ]
            
            all_passed = True
            
            for resource_name, expected_path in resources_to_check:
                resource_path = self.size_analyzer_config.get_resource_path(
                    resource_name
                )
                
                if os.path.exists(resource_path):
                    self.log_test(
                        f"Resource Path - {resource_name}",
                        "PASS",
                        f"Resource found at {resource_path}"
                    )
                else:
                    self.log_test(
                        f"Resource Path - {resource_name}",
                        "FAIL",
                        f"Resource not found at {resource_path}"
                    )
                    all_passed = False
            
            return all_passed
            
        except Exception as e:
            self.log_test(
                "Resource Paths",
                "FAIL",
                "Error checking resource paths",
                str(e)
            )
            return False
    
    def test_directory_creation(self):
        """Test directory creation for cache, temp, and logs."""
        try:
            directories_to_check = [
                'cache_directory',
                'temp_directory', 
                'log_directory'
            ]
            
            all_passed = True
            
            for dir_name in directories_to_check:
                dir_path = self.size_analyzer_config.get_resource_path(dir_name)
                
                if os.path.exists(dir_path) and os.path.isdir(dir_path):
                    self.log_test(
                        f"Directory - {dir_name}",
                        "PASS",
                        f"Directory exists at {dir_path}"
                    )
                else:
                    self.log_test(
                        f"Directory - {dir_name}",
                        "FAIL",
                        f"Directory not found at {dir_path}"
                    )
                    all_passed = False
            
            return all_passed
            
        except Exception as e:
            self.log_test(
                "Directory Creation",
                "FAIL",
                "Error checking directories",
                str(e)
            )
            return False
    
    def test_logging_configuration(self):
        """Test logging configuration."""
        try:
            self.logger = get_size_analyzer_logger(self.size_analyzer_config)
            
            if self.logger:
                # Test basic logging
                self.logger.log_core_logic('info', 'Test log message')
                
                self.log_test(
                    "Logging Configuration",
                    "PASS",
                    "Logging system initialized successfully"
                )
                return True
            else:
                self.log_test(
                    "Logging Configuration",
                    "FAIL",
                    "Failed to initialize logging system"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Logging Configuration",
                "FAIL",
                "Error initializing logging configuration",
                str(e)
            )
            return False
    
    def test_settings_persistence(self):
        """Test settings persistence."""
        try:
            # Test setting and getting a value
            test_value = "test_directory_123"
            
            success = self.size_analyzer_config.set_setting(
                'general', 'last_opened_directory', test_value
            )
            
            if not success:
                self.log_test(
                    "Settings Persistence",
                    "FAIL",
                    "Failed to set test setting"
                )
                return False
            
            # Retrieve the value
            retrieved_value = self.size_analyzer_config.get_setting(
                'general', 'last_opened_directory'
            )
            
            if retrieved_value == test_value:
                self.log_test(
                    "Settings Persistence",
                    "PASS",
                    "Settings persistence working correctly"
                )
                
                # Clean up test value
                self.size_analyzer_config.set_setting(
                    'general', 'last_opened_directory', ''
                )
                return True
            else:
                self.log_test(
                    "Settings Persistence",
                    "FAIL",
                    f"Retrieved value mismatch: {retrieved_value} != {test_value}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Settings Persistence",
                "FAIL",
                "Error testing settings persistence",
                str(e)
            )
            return False
    
    def test_configuration_validation(self):
        """Test configuration validation."""
        try:
            validation_results = self.size_analyzer_config.validate_configuration()
            
            if isinstance(validation_results, dict):
                errors = validation_results.get('errors', [])
                warnings = validation_results.get('warnings', [])
                
                if errors:
                    self.log_test(
                        "Configuration Validation",
                        "FAIL",
                        f"Configuration validation found {len(errors)} errors",
                        '; '.join(errors)
                    )
                    return False
                elif warnings:
                    self.log_test(
                        "Configuration Validation",
                        "WARN",
                        f"Configuration validation found {len(warnings)} warnings",
                        '; '.join(warnings)
                    )
                    return True
                else:
                    self.log_test(
                        "Configuration Validation",
                        "PASS",
                        "Configuration validation passed without issues"
                    )
                    return True
            else:
                self.log_test(
                    "Configuration Validation",
                    "FAIL",
                    "Configuration validation returned unexpected format"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Configuration Validation",
                "FAIL",
                "Error during configuration validation",
                str(e)
            )
            return False
    
    def test_size_analyzer_instantiation(self):
        """Test Size Analyzer instantiation with configuration."""
        try:
            analyzer = SizeAnalyzer()
            
            if analyzer:
                self.log_test(
                    "Size Analyzer Instantiation",
                    "PASS",
                    "Size Analyzer instantiated successfully"
                )
                return True
            else:
                self.log_test(
                    "Size Analyzer Instantiation",
                    "FAIL",
                    "Failed to instantiate Size Analyzer"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Size Analyzer Instantiation",
                "FAIL",
                "Error instantiating Size Analyzer",
                str(e)
            )
            return False
    
    def run_all_tests(self):
        """Run all configuration tests."""
        print("=" * 60)
        print("Size Analyzer Configuration Validation Tests")
        print("=" * 60)
        
        tests = [
            self.test_main_configuration_loading,
            self.test_size_analyzer_configuration_section,
            self.test_size_analyzer_config_manager,
            self.test_resource_paths,
            self.test_directory_creation,
            self.test_logging_configuration,
            self.test_settings_persistence,
            self.test_configuration_validation,
            self.test_size_analyzer_instantiation
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                self.log_test(
                    test.__name__,
                    "FAIL",
                    "Unexpected error during test execution",
                    str(e)
                )
        
        # Cleanup
        try:
            if self.logger:
                cleanup_logging()
        except Exception as e:
            print(f"Warning: Error during cleanup: {e}")
        
        # Print summary
        print("\n" + "=" * 60)
        print("Test Summary")
        print("=" * 60)
        print(f"Passed: {self.results['passed']}")
        print(f"Failed: {self.results['failed']}")
        print(f"Warnings: {self.results['warnings']}")
        print(f"Total: {len(self.results['tests'])}")
        
        if self.results['failed'] == 0:
            print("\n✓ All tests passed! Configuration is working correctly.")
            return True
        else:
            print(f"\n✗ {self.results['failed']} test(s) failed. Please review the issues above.")
            return False
    
    def generate_report(self, output_file: str = None):
        """Generate a detailed test report."""
        if output_file is None:
            output_file = "size_analyzer_configuration_test_report.json"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            
            print(f"\nDetailed test report saved to: {output_file}")
            
        except Exception as e:
            print(f"Error saving test report: {e}")


def main():
    """Main test execution function."""
    validator = ConfigurationValidator()
    
    try:
        success = validator.run_all_tests()
        validator.generate_report()
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\nTest execution interrupted by user.")
        return 1
    except Exception as e:
        print(f"\nUnexpected error during test execution: {e}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())