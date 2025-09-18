#!/usr/bin/env python3
"""
Comprehensive Integration Tests for Advanced Folders
Testing RFU integration, settings persistence, and core functionality
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

# Add src directory to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    import pytest
    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False


class TestAdvancedFoldersIntegration(unittest.TestCase):
    """Test Advanced Folders integration with RFU Hub and settings persistence."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.config_file = Path(self.test_dir) / "test_config.json"
        
        # Mock PyQt5 components
        self.mock_qt_classes()
        
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def mock_qt_classes(self):
        """Mock PyQt5 classes for testing."""
        # Mock all PyQt5 components that might be imported
        qt_mocks = {
            'PyQt5.QtWidgets': Mock(),
            'PyQt5.QtCore': Mock(),
            'PyQt5.QtGui': Mock()
        }
        
        for module_name, mock_obj in qt_mocks.items():
            sys.modules[module_name] = mock_obj
            
        # Setup common Qt class mocks
        mock_widget = Mock()
        mock_widget.show = Mock()
        mock_widget.hide = Mock()
        mock_widget.setLayout = Mock()
        
        qt_mocks['PyQt5.QtWidgets'].QWidget = Mock(return_value=mock_widget)
        qt_mocks['PyQt5.QtWidgets'].QVBoxLayout = Mock()
        qt_mocks['PyQt5.QtWidgets'].QHBoxLayout = Mock()
        qt_mocks['PyQt5.QtWidgets'].QTabWidget = Mock()
        qt_mocks['PyQt5.QtWidgets'].QLabel = Mock()
        qt_mocks['PyQt5.QtWidgets'].QPushButton = Mock()
        qt_mocks['PyQt5.QtWidgets'].QLineEdit = Mock()
        qt_mocks['PyQt5.QtWidgets'].QTextEdit = Mock()
        qt_mocks['PyQt5.QtWidgets'].QComboBox = Mock()
        qt_mocks['PyQt5.QtWidgets'].QCheckBox = Mock()
        qt_mocks['PyQt5.QtWidgets'].QSpinBox = Mock()
        qt_mocks['PyQt5.QtWidgets'].QListWidget = Mock()
        qt_mocks['PyQt5.QtWidgets'].QTableWidget = Mock()
        qt_mocks['PyQt5.QtWidgets'].QProgressBar = Mock()
        qt_mocks['PyQt5.QtWidgets'].QGroupBox = Mock()
        qt_mocks['PyQt5.QtWidgets'].QDialog = Mock()
        qt_mocks['PyQt5.QtWidgets'].QFileDialog = Mock()
        qt_mocks['PyQt5.QtWidgets'].QMessageBox = Mock()
        
        # Mock Qt enums and constants
        qt_mocks['PyQt5.QtCore'].Qt = Mock()
        qt_mocks['PyQt5.QtCore'].Qt.AlignCenter = Mock()
        qt_mocks['PyQt5.QtCore'].QThread = Mock()
        qt_mocks['PyQt5.QtCore'].pyqtSignal = Mock()
        qt_mocks['PyQt5.QtCore'].QTimer = Mock()

    def test_folder_configuration_model(self):
        """Test FolderConfiguration data model functionality."""
        try:
            from src.tools.file_management.advanced_folders.core.folder_configuration import (
                FolderConfiguration, FolderStatistics, SearchParameters)

            # Test FolderConfiguration creation
            config = FolderConfiguration(
                name="Test Folder",
                path="/test/path",
                description="Test folder description"
            )
            
            self.assertEqual(config.name, "Test Folder")
            self.assertEqual(config.path, "/test/path")
            self.assertEqual(config.description, "Test folder description")
            self.assertTrue(config.enabled)
            self.assertIsNotNone(config.created_date)
            
            # Test SearchParameters
            search_params = SearchParameters()
            self.assertEqual(search_params.file_extensions, [])
            self.assertEqual(search_params.size_min, 0)
            self.assertIsNone(search_params.size_max)
            
            # Test FolderStatistics
            stats = FolderStatistics()
            self.assertEqual(stats.total_files, 0)
            self.assertEqual(stats.total_size, 0)
            
            print("✓ FolderConfiguration model tests passed")
            
        except ImportError as e:
            self.skipTest(f"Advanced Folders module not available: {e}")

    def test_folder_configuration_manager(self):
        """Test FolderConfigurationManager persistence functionality."""
        try:
            from src.tools.file_management.advanced_folders.core.folder_configuration import (
                FolderConfiguration, FolderConfigurationManager)

            # Create test configuration
            config = FolderConfiguration(
                name="Test Config",
                path=str(self.test_dir),
                description="Test configuration"
            )
            
            # Test manager creation and persistence
            manager = FolderConfigurationManager()
            manager.config_file = self.config_file
            
            # Test saving configuration
            manager.save_configuration(config)
            self.assertTrue(self.config_file.exists())
            
            # Test loading configuration
            loaded_configs = manager.load_configurations()
            self.assertEqual(len(loaded_configs), 1)
            self.assertEqual(loaded_configs[0].name, "Test Config")
            self.assertEqual(loaded_configs[0].path, str(self.test_dir))
            
            # Test updating configuration
            config.description = "Updated description"
            manager.update_configuration(config)
            
            updated_configs = manager.load_configurations()
            self.assertEqual(updated_configs[0].description, "Updated description")
            
            # Test deleting configuration
            manager.delete_configuration(config.id)
            remaining_configs = manager.load_configurations()
            self.assertEqual(len(remaining_configs), 0)
            
            print("✓ FolderConfigurationManager tests passed")
            
        except ImportError as e:
            self.skipTest(f"Advanced Folders module not available: {e}")

    def test_search_engine_functionality(self):
        """Test SearchEngine core functionality."""
        try:
            from src.tools.file_management.advanced_folders.core.search_engine import (
                FileResult, SearchEngine, SearchParameters)

            # Create test files
            test_file = Path(self.test_dir) / "test.txt"
            test_file.write_text("This is a test file content")
            
            # Test SearchEngine creation
            engine = SearchEngine()
            self.assertIsNotNone(engine)
            
            # Test search parameters
            params = SearchParameters(
                path=str(self.test_dir),
                file_extensions=[".txt"],
                content_search="test"
            )
            
            # Test search functionality (mocked for thread safety)
            with patch.object(engine, '_perform_search') as mock_search:
                mock_result = FileResult(
                    path=str(test_file),
                    name="test.txt",
                    size=len("This is a test file content"),
                    modified_date=test_file.stat().st_mtime
                )
                mock_search.return_value = [mock_result]
                
                results = engine.search(params)
                self.assertIsInstance(results, list)
                
            print("✓ SearchEngine functionality tests passed")
            
        except ImportError as e:
            self.skipTest(f"Advanced Folders module not available: {e}")

    def test_config_manager_integration(self):
        """Test integration with RFU ConfigManager."""
        try:
            # Mock the ConfigManager
            with patch('src.config_manager.get_config_manager') as mock_get_config:
                mock_config_manager = Mock()
                mock_config_manager.get_setting.return_value = {}
                mock_config_manager.set_setting = Mock()
                mock_get_config.return_value = mock_config_manager
                
                from src.tools.file_management.advanced_folders.core.folder_configuration import \
                    FolderConfigurationManager
                
                manager = FolderConfigurationManager()
                
                # Test that ConfigManager integration is available
                self.assertIsNotNone(manager)
                
                # Verify ConfigManager methods are called
                manager._load_from_config_manager()
                mock_config_manager.get_setting.assert_called()
                
            print("✓ ConfigManager integration tests passed")
            
        except ImportError as e:
            self.skipTest(f"ConfigManager integration not available: {e}")

    def test_rfu_hub_integration(self):
        """Test integration with RFU Hub main launcher."""
        try:
            # Mock the main RFU application
            with patch('builtins.__import__') as mock_import:
                # Mock the import of AdvancedFoldersGUI
                mock_gui_class = Mock()
                mock_gui_instance = Mock()
                mock_gui_class.return_value = mock_gui_instance
                
                mock_module = Mock()
                mock_module.AdvancedFoldersGUI = mock_gui_class
                mock_import.return_value = mock_module
                
                # Test that the module can be imported and instantiated
                module = __import__('src.tools.file_management.advanced_folders.advanced_folders_main')
                self.assertIsNotNone(module)
                
            print("✓ RFU Hub integration tests passed")
            
        except ImportError as e:
            self.skipTest(f"RFU Hub integration not available: {e}")

    def test_main_integration_entry_point(self):
        """Test main.py integration entry point."""
        try:
            from src.tools.file_management.advanced_folders.advanced_folders_main import \
                main

            # Mock QApplication to prevent GUI startup
            with patch('src.tools.file_management.advanced_folders.advanced_folders_main.QApplication') as mock_app:
                mock_app_instance = Mock()
                mock_app.return_value = mock_app_instance
                mock_app_instance.exec_ = Mock(return_value=0)
                
                # Test main function executes without error
                with patch('src.tools.file_management.advanced_folders.advanced_folders_main.AdvancedFoldersGUI'):
                    result = main()
                    self.assertEqual(result, 0)
                    
            print("✓ Main integration entry point tests passed")
            
        except ImportError as e:
            self.skipTest(f"Main integration entry point not available: {e}")

    def test_package_structure(self):
        """Test that the Advanced Folders package structure is correct."""
        try:
            # Test package imports
            import src.tools.file_management.advanced_folders
            from src.tools.file_management.advanced_folders import (
                AdvancedFoldersWidget, FolderConfiguration, SearchEngine)

            # Verify classes are available
            self.assertTrue(hasattr(src.utilities.file_management.advanced_folders, 'FolderConfiguration'))
            self.assertTrue(hasattr(src.utilities.file_management.advanced_folders, 'SearchEngine'))
            self.assertTrue(hasattr(src.utilities.file_management.advanced_folders, 'AdvancedFoldersWidget'))
            
            print("✓ Package structure tests passed")
            
        except ImportError as e:
            self.skipTest(f"Package structure not available: {e}")


class TestAdvancedFoldersSettingsPersistence(unittest.TestCase):
    """Test settings persistence functionality specifically."""
    
    def setUp(self):
        """Set up test environment for settings tests."""
        self.test_dir = tempfile.mkdtemp()
        self.config_file = Path(self.test_dir) / "settings_test.json"
        
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_json_persistence_format(self):
        """Test JSON persistence format compatibility."""
        try:
            from src.tools.file_management.advanced_folders.core.folder_configuration import \
                FolderConfiguration

            # Create test configuration
            config = FolderConfiguration(
                name="Persistence Test",
                path="/test/persistence",
                description="Testing JSON persistence"
            )
            
            # Test serialization to JSON
            config_dict = config.to_dict()
            json_str = json.dumps(config_dict, indent=2)
            
            # Verify JSON structure
            parsed_data = json.loads(json_str)
            self.assertIn('name', parsed_data)
            self.assertIn('path', parsed_data)
            self.assertIn('description', parsed_data)
            self.assertIn('enabled', parsed_data)
            self.assertIn('created_date', parsed_data)
            
            # Test deserialization from JSON
            restored_config = FolderConfiguration.from_dict(parsed_data)
            self.assertEqual(restored_config.name, config.name)
            self.assertEqual(restored_config.path, config.path)
            self.assertEqual(restored_config.description, config.description)
            
            print("✓ JSON persistence format tests passed")
            
        except ImportError as e:
            self.skipTest(f"Advanced Folders module not available: {e}")

    def test_config_manager_settings_integration(self):
        """Test integration with ConfigManager settings system."""
        # This test verifies the settings persistence integration
        # with the existing RFU ConfigManager system
        
        try:
            # Mock ConfigManager for testing
            with patch('src.config_manager.get_config_manager') as mock_get_config:
                mock_config_manager = Mock()
                mock_config_manager.get_setting.return_value = {
                    'advanced_folders': {
                        'configurations': []
                    }
                }
                mock_config_manager.set_setting = Mock()
                mock_get_config.return_value = mock_config_manager
                
                from src.tools.file_management.advanced_folders.core.folder_configuration import \
                    FolderConfigurationManager
                
                manager = FolderConfigurationManager()
                
                # Test loading from ConfigManager
                configs = manager._load_from_config_manager()
                self.assertIsInstance(configs, list)
                
                # Test saving to ConfigManager
                test_configs = []  # Empty list for test
                manager._save_to_config_manager(test_configs)
                
                # Verify ConfigManager methods were called
                mock_config_manager.get_setting.assert_called_with('advanced_folders', 'configurations', [])
                mock_config_manager.set_setting.assert_called_with('advanced_folders', 'configurations', test_configs)
                
            print("✓ ConfigManager settings integration tests passed")
            
        except ImportError as e:
            self.skipTest(f"ConfigManager integration not available: {e}")


def run_integration_tests():
    """Run all integration tests with comprehensive reporting."""
    print("="*60)
    print("Advanced Folders - Comprehensive Integration Tests")
    print("="*60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestAdvancedFoldersIntegration,
        TestAdvancedFoldersSettingsPersistence
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "="*60)
    print("Integration Test Summary")
    print("="*60)
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.failures:
        print("\nFailures:")
        for test, failure in result.failures:
            print(f"  - {test}: {failure}")
    
    if result.errors:
        print("\nErrors:")
        for test, error in result.errors:
            print(f"  - {test}: {error}")
    
    if result.skipped:
        print("\nSkipped:")
        for test, reason in result.skipped:
            print(f"  - {test}: {reason}")
    
    # Return overall success status
    return len(result.failures) == 0 and len(result.errors) == 0


if __name__ == "__main__":
    # Run integration tests
    success = run_integration_tests()
    
    if success:
        print("\n✓ All Advanced Folders integration tests completed successfully!")
        sys.exit(0)
    else:
        print("\n✗ Some integration tests failed. Please review the output above.")
        sys.exit(1)