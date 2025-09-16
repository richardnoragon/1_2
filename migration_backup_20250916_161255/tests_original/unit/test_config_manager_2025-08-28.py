"""
Comprehensive unit tests for config_manager.py

This module contains comprehensive unit tests for the ConfigManager class
using pytest framework with detailed test coverage, edge cases, and mock data.

Test File: test_config_manager_2025-08-28.py
Target: config_manager.py
Date: 2025-08-28
Framework: pytest
"""

import datetime
import json
import logging
import shutil
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

# Add the parent directory to the path to import config_manager
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config_manager import ConfigManager, get_config_manager


class TestConfigManager:
    """Comprehensive test suite for ConfigManager class."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Setup and teardown for each test method."""
        # Setup: Create temporary directory for testing
        self.test_dir = Path(tempfile.mkdtemp())
        self.original_config_dir = None
        self.original_config_file = None
        
        # Store original singleton instance
        self.original_instance = ConfigManager._instance
        
        # Reset singleton for testing
        ConfigManager._instance = None
        
        # Create test data
        self.sample_config = {
            'general': {
                'logging_level': 'DEBUG',
                'enable_debug_logging': True,
                'auto_save_config': False,
                'theme': 'dark',
                'language': 'en',
                'check_for_updates': False
            },
            'gui': {
                'window_width': 1200,
                'window_height': 800,
                'remember_window_position': False,
                'show_status_bar': False,
                'show_toolbar': False,
                'font_size': 14,
                'font_family': 'Arial'
            },
            'test_section': {
                'test_key1': 'test_value1',
                'test_key2': 42,
                'test_key3': True,
                'test_key4': [1, 2, 3],
                'test_key5': {'nested': 'value'}
            }
        }
        
        yield
        
        # Teardown: Clean up test directory and restore singleton
        try:
            if self.test_dir.exists():
                shutil.rmtree(self.test_dir)
        except Exception:
            pass
        
        # Restore original singleton instance
        ConfigManager._instance = self.original_instance

    @pytest.fixture
    def config_manager(self):
        """Create a ConfigManager instance for testing."""
        with patch.object(ConfigManager, '_setup_config'):
            manager = ConfigManager()
            manager.config_dir = self.test_dir / 'config'
            manager.config_dir.mkdir(exist_ok=True)
            manager.config_file = manager.config_dir / 'rfu_config.json'
            manager.config = {}
            manager.logger = logging.getLogger('TestConfigManager')
            manager._initialized = True
            return manager

    @pytest.fixture
    def config_manager_with_data(self):
        """Create a ConfigManager instance with sample data."""
        with patch.object(ConfigManager, '_setup_config'):
            manager = ConfigManager()
            manager.config_dir = self.test_dir / 'config'
            manager.config_dir.mkdir(exist_ok=True)
            manager.config_file = manager.config_dir / 'rfu_config.json'
            manager.config = self.sample_config.copy()
            manager.logger = logging.getLogger('TestConfigManager')
            manager._initialized = True
            
            # Write sample config to file
            with open(manager.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.sample_config, f, indent=2)
            
            return manager

    def test_singleton_pattern(self):
        """Test that ConfigManager follows singleton pattern."""
        # Create first instance
        instance1 = ConfigManager()
        instance2 = ConfigManager()
        
        # Both should be the same instance
        assert instance1 is instance2
        assert id(instance1) == id(instance2)

    def test_initialization(self, config_manager):
        """Test ConfigManager initialization."""
        assert config_manager._initialized is True
        assert isinstance(config_manager.config, dict)
        assert config_manager.config_dir.exists()
        assert isinstance(config_manager.logger, logging.Logger)

    def test_ensure_default_sections(self, config_manager):
        """Test that default sections are created correctly."""
        config_manager._ensure_default_sections()
        
        expected_sections = [
            'general', 'gui', 'logging', 'tools',
            'network_connectivity', 'pdf_tools',
            'privacy_tools', 'software_maintenance'
        ]
        
        for section in expected_sections:
            assert section in config_manager.config
            assert isinstance(config_manager.config[section], dict)
        
        # Test specific default values
        assert config_manager.config['general']['logging_level'] == 'INFO'
        assert config_manager.config['gui']['window_width'] == 900
        assert config_manager.config['logging']['enable_file_logging'] is True

    def test_get_setting_valid_section_and_key(self, config_manager_with_data):
        """Test getting a valid setting."""
        result = config_manager_with_data.get_setting('general', 'logging_level')
        assert result == 'DEBUG'
        
        result = config_manager_with_data.get_setting('gui', 'window_width')
        assert result == 1200
        
        result = config_manager_with_data.get_setting('test_section', 'test_key2')
        assert result == 42

    def test_get_setting_entire_section(self, config_manager_with_data):
        """Test getting an entire section."""
        result = config_manager_with_data.get_setting('general')
        expected = self.sample_config['general']
        assert result == expected

    def test_get_setting_nonexistent_section(self, config_manager_with_data):
        """Test getting setting from nonexistent section."""
        result = config_manager_with_data.get_setting('nonexistent', 'key', 'default')
        assert result == 'default'

    def test_get_setting_nonexistent_key(self, config_manager_with_data):
        """Test getting nonexistent key from valid section."""
        result = config_manager_with_data.get_setting('general', 'nonexistent', 'default')
        assert result == 'default'

    def test_get_setting_with_none_default(self, config_manager_with_data):
        """Test getting setting with None as default."""
        result = config_manager_with_data.get_setting('nonexistent', 'key')
        assert result is None

    def test_set_setting_new_section(self, config_manager):
        """Test setting a value in a new section."""
        result = config_manager.set_setting('new_section', 'new_key', 'new_value')
        assert result is True
        assert 'new_section' in config_manager.config
        assert config_manager.config['new_section']['new_key'] == 'new_value'

    def test_set_setting_existing_section(self, config_manager_with_data):
        """Test setting a value in an existing section."""
        result = config_manager_with_data.set_setting('general', 'new_setting', 'test_value')
        assert result is True
        assert config_manager_with_data.config['general']['new_setting'] == 'test_value'

    def test_set_setting_overwrite_existing(self, config_manager_with_data):
        """Test overwriting an existing setting."""
        original_value = config_manager_with_data.config['general']['logging_level']
        result = config_manager_with_data.set_setting('general', 'logging_level', 'ERROR')
        assert result is True
        assert config_manager_with_data.config['general']['logging_level'] == 'ERROR'
        assert config_manager_with_data.config['general']['logging_level'] != original_value

    def test_set_setting_various_data_types(self, config_manager):
        """Test setting various data types."""
        test_cases = [
            ('string_val', 'test_string'),
            ('int_val', 123),
            ('float_val', 45.67),
            ('bool_val', True),
            ('list_val', [1, 2, 3, 'test']),
            ('dict_val', {'nested': {'deep': 'value'}}),
            ('none_val', None)
        ]
        
        for key, value in test_cases:
            result = config_manager.set_setting('test_types', key, value)
            assert result is True
            assert config_manager.config['test_types'][key] == value

    def test_get_section_existing(self, config_manager_with_data):
        """Test getting an existing section."""
        result = config_manager_with_data.get_section('general')
        expected = self.sample_config['general']
        assert result == expected
        assert isinstance(result, dict)

    def test_get_section_nonexistent(self, config_manager_with_data):
        """Test getting a nonexistent section."""
        result = config_manager_with_data.get_section('nonexistent')
        assert result == {}
        assert isinstance(result, dict)

    def test_set_section_new(self, config_manager):
        """Test setting a new section."""
        new_section = {'key1': 'value1', 'key2': 42}
        result = config_manager.set_section('new_section', new_section)
        assert result is True
        assert config_manager.config['new_section'] == new_section

    def test_set_section_overwrite(self, config_manager_with_data):
        """Test overwriting an existing section."""
        new_section = {'completely': 'different', 'data': True}
        result = config_manager_with_data.set_section('general', new_section)
        assert result is True
        assert config_manager_with_data.config['general'] == new_section

    def test_set_section_independence(self, config_manager):
        """Test that set_section creates independent copy."""
        original_dict = {'key1': 'value1', 'key2': {'nested': 'value'}}
        config_manager.set_section('test_section', original_dict)
        
        # Modify original dict
        original_dict['key1'] = 'modified'
        original_dict['key2']['nested'] = 'modified'
        
        # Config should remain unchanged
        assert config_manager.config['test_section']['key1'] == 'value1'
        assert config_manager.config['test_section']['key2']['nested'] == 'value'

    def test_remove_setting_existing(self, config_manager_with_data):
        """Test removing an existing setting."""
        # Verify setting exists
        assert 'logging_level' in config_manager_with_data.config['general']
        
        result = config_manager_with_data.remove_setting('general', 'logging_level')
        assert result is True
        assert 'logging_level' not in config_manager_with_data.config['general']

    def test_remove_setting_nonexistent_key(self, config_manager_with_data):
        """Test removing a nonexistent key."""
        result = config_manager_with_data.remove_setting('general', 'nonexistent')
        assert result is False

    def test_remove_setting_nonexistent_section(self, config_manager_with_data):
        """Test removing from nonexistent section."""
        result = config_manager_with_data.remove_setting('nonexistent', 'key')
        assert result is False

    def test_save_config_success(self, config_manager_with_data):
        """Test successful config saving."""
        config_manager_with_data.config_dir.mkdir(exist_ok=True)
        result = config_manager_with_data.save_config()
        assert result is True
        assert config_manager_with_data.config_file.exists()
        
        # Verify file content
        with open(config_manager_with_data.config_file, 'r', encoding='utf-8') as f:
            saved_config = json.load(f)
        assert saved_config == config_manager_with_data.config

    def test_save_config_directory_creation(self, config_manager):
        """Test that save_config creates directory if it doesn't exist."""
        # Remove config directory
        if config_manager.config_dir.exists():
            shutil.rmtree(config_manager.config_dir)
        
        result = config_manager.save_config()
        assert result is True
        assert config_manager.config_dir.exists()
        assert config_manager.config_file.exists()

    def test_save_config_permission_error(self, config_manager):
        """Test save_config with permission error."""
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            result = config_manager.save_config()
            assert result is False

    def test_load_config_existing_file(self, config_manager):
        """Test loading config from existing file."""
        # Create config file with data
        config_manager.config_dir.mkdir(exist_ok=True)
        with open(config_manager.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.sample_config, f)
        
        result = config_manager.load_config()
        assert result is True
        assert config_manager.config == self.sample_config

    def test_load_config_nonexistent_file(self, config_manager):
        """Test loading config when file doesn't exist."""
        result = config_manager.load_config()
        assert result is True
        # Should have default sections
        assert 'general' in config_manager.config

    def test_load_config_invalid_json(self, config_manager):
        """Test loading config with invalid JSON."""
        config_manager.config_file.touch()  # Create empty file
        with patch('builtins.open', side_effect=json.JSONDecodeError("Invalid JSON", "", 0)):
            result = config_manager.load_config()
            assert result is False

    def test_reset_to_defaults(self, config_manager_with_data):
        """Test resetting configuration to defaults."""
        # Verify we have custom data
        assert config_manager_with_data.config['general']['logging_level'] == 'DEBUG'
        
        result = config_manager_with_data.reset_to_defaults()
        assert result is True
        
        # Should have default values
        assert config_manager_with_data.config['general']['logging_level'] == 'INFO'
        assert 'test_section' not in config_manager_with_data.config

    def test_get_all_settings(self, config_manager_with_data):
        """Test getting all settings."""
        result = config_manager_with_data.get_all_settings()
        assert result == config_manager_with_data.config
        assert isinstance(result, dict)
        
        # Verify it's a copy (independence)
        result['new_key'] = 'new_value'
        assert 'new_key' not in config_manager_with_data.config

    def test_export_config_success(self, config_manager_with_data):
        """Test successful config export."""
        export_path = self.test_dir / 'exported_config.json'
        result = config_manager_with_data.export_config(export_path)
        assert result is True
        assert export_path.exists()
        
        # Verify exported content
        with open(export_path, 'r', encoding='utf-8') as f:
            exported_config = json.load(f)
        assert exported_config == config_manager_with_data.config

    def test_export_config_nested_directory(self, config_manager_with_data):
        """Test exporting to nested directory that doesn't exist."""
        export_path = self.test_dir / 'nested' / 'dir' / 'config.json'
        result = config_manager_with_data.export_config(export_path)
        assert result is True
        assert export_path.exists()
        assert export_path.parent.exists()

    def test_export_config_permission_error(self, config_manager_with_data):
        """Test export config with permission error."""
        export_path = self.test_dir / 'export.json'
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            result = config_manager_with_data.export_config(export_path)
            assert result is False

    def test_import_config_success(self, config_manager):
        """Test successful config import."""
        # Create import file
        import_path = self.test_dir / 'import_config.json'
        with open(import_path, 'w', encoding='utf-8') as f:
            json.dump(self.sample_config, f)
        
        result = config_manager.import_config(import_path)
        assert result is True
        
        # Verify imported data is present
        assert config_manager.config['general']['logging_level'] == 'DEBUG'
        assert config_manager.config['test_section']['test_key1'] == 'test_value1'

    def test_import_config_nonexistent_file(self, config_manager):
        """Test importing from nonexistent file."""
        import_path = self.test_dir / 'nonexistent.json'
        result = config_manager.import_config(import_path)
        assert result is False

    def test_import_config_invalid_json(self, config_manager):
        """Test importing invalid JSON."""
        import_path = self.test_dir / 'invalid.json'
        with open(import_path, 'w') as f:
            f.write("invalid json content")
        
        result = config_manager.import_config(import_path)
        assert result is False

    def test_import_config_invalid_format(self, config_manager):
        """Test importing non-dict JSON."""
        import_path = self.test_dir / 'invalid_format.json'
        with open(import_path, 'w') as f:
            json.dump(["not", "a", "dict"], f)
        
        result = config_manager.import_config(import_path)
        assert result is False

    def test_import_config_merge_behavior(self, config_manager_with_data):
        """Test that import merges with existing config."""
        # Create import file with additional data
        import_config = {
            'general': {'new_setting': 'new_value'},
            'brand_new_section': {'key': 'value'}
        }
        import_path = self.test_dir / 'merge_test.json'
        with open(import_path, 'w', encoding='utf-8') as f:
            json.dump(import_config, f)
        
        # Store original value
        original_theme = config_manager_with_data.config['general']['theme']
        
        result = config_manager_with_data.import_config(import_path)
        assert result is True
        
        # New setting should be added
        assert config_manager_with_data.config['general']['new_setting'] == 'new_value'
        # Original setting should remain
        assert config_manager_with_data.config['general']['theme'] == original_theme
        # New section should be added
        assert config_manager_with_data.config['brand_new_section']['key'] == 'value'

    def test_get_config_info(self, config_manager_with_data):
        """Test getting configuration information."""
        result = config_manager_with_data.get_config_info()
        
        assert isinstance(result, dict)
        assert 'config_file' in result
        assert 'config_dir' in result
        assert 'sections' in result
        assert 'total_settings' in result
        assert 'file_exists' in result
        assert 'file_size_bytes' in result
        
        # Verify content
        assert str(config_manager_with_data.config_file) in result['config_file']
        assert str(config_manager_with_data.config_dir) in result['config_dir']
        assert isinstance(result['sections'], list)
        assert isinstance(result['total_settings'], int)
        assert isinstance(result['file_exists'], bool)
        assert isinstance(result['file_size_bytes'], int)
        
        # Verify sections list
        expected_sections = list(config_manager_with_data.config.keys())
        assert set(result['sections']) == set(expected_sections)

    def test_auto_save_enabled(self, config_manager):
        """Test auto-save functionality when enabled."""
        config_manager.config = {'general': {'auto_save_config': True}}
        config_manager.config_dir.mkdir(exist_ok=True)
        
        with patch.object(config_manager, 'save_config') as mock_save:
            config_manager.set_setting('test', 'key', 'value')
            mock_save.assert_called_once()

    def test_auto_save_disabled(self, config_manager):
        """Test auto-save functionality when disabled."""
        config_manager.config = {'general': {'auto_save_config': False}}
        
        with patch.object(config_manager, 'save_config') as mock_save:
            config_manager.set_setting('test', 'key', 'value')
            mock_save.assert_not_called()

    def test_thread_safety_singleton(self):
        """Test thread safety of singleton pattern."""
        import threading
        import time
        
        instances = []
        
        def create_instance():
            time.sleep(0.01)  # Small delay to increase chance of race condition
            instance = ConfigManager()
            instances.append(instance)
        
        # Create multiple threads
        threads = [threading.Thread(target=create_instance) for _ in range(10)]
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All instances should be the same
        assert len(instances) == 10
        for instance in instances:
            assert instance is instances[0]

    def test_error_handling_in_methods(self, config_manager):
        """Test error handling in various methods."""
        # Test with mock that raises exception
        with patch.object(config_manager, 'config', side_effect=Exception("Test error")):
            result = config_manager.get_setting('test', 'key', 'default')
            assert result == 'default'

    @pytest.mark.parametrize("section,key,value", [
        ('test', 'string', 'test_value'),
        ('test', 'integer', 42),
        ('test', 'float', 3.14159),
        ('test', 'boolean', True),
        ('test', 'list', [1, 2, 3]),
        ('test', 'dict', {'nested': 'value'}),
        ('test', 'none', None),
    ])
    def test_data_type_preservation(self, config_manager, section, key, value):
        """Test that various data types are preserved correctly."""
        config_manager.set_setting(section, key, value)
        retrieved = config_manager.get_setting(section, key)
        assert retrieved == value
        assert type(retrieved) == type(value)

    def test_path_object_handling(self, config_manager_with_data):
        """Test handling of Path objects in export/import methods."""
        from pathlib import Path

        # Test export with Path object
        export_path = Path(self.test_dir) / 'path_test.json'
        result = config_manager_with_data.export_config(export_path)
        assert result is True
        
        # Test import with Path object
        new_manager = config_manager_with_data
        new_manager.config = {}
        result = new_manager.import_config(export_path)
        assert result is True


class TestConfigManagerGlobalFunction:
    """Test the global get_config_manager function."""

    def setup_method(self):
        """Setup for each test method."""
        # Reset global instance
        import config_manager
        config_manager._config_manager = None

    def test_get_config_manager_singleton(self):
        """Test that get_config_manager returns singleton instance."""
        manager1 = get_config_manager()
        manager2 = get_config_manager()
        
        assert manager1 is manager2
        assert isinstance(manager1, ConfigManager)

    def test_get_config_manager_creates_instance(self):
        """Test that get_config_manager creates instance when needed."""
        import config_manager
        assert config_manager._config_manager is None
        
        manager = get_config_manager()
        assert config_manager._config_manager is not None
        assert config_manager._config_manager is manager


class TestConfigManagerEdgeCases:
    """Test edge cases and boundary conditions."""

    @pytest.fixture
    def config_manager(self):
        """Create a ConfigManager instance for testing."""
        test_dir = Path(tempfile.mkdtemp())
        with patch.object(ConfigManager, '_setup_config'):
            manager = ConfigManager()
            manager.config_dir = test_dir / 'config'
            manager.config_file = manager.config_dir / 'rfu_config.json'
            manager.config = {}
            manager.logger = logging.getLogger('TestConfigManager')
            manager._initialized = True
            yield manager
        
        # Cleanup
        if test_dir.exists():
            shutil.rmtree(test_dir)

    def test_empty_string_values(self, config_manager):
        """Test handling of empty string values."""
        config_manager.set_setting('test', 'empty_string', '')
        result = config_manager.get_setting('test', 'empty_string')
        assert result == ''

    def test_unicode_values(self, config_manager):
        """Test handling of unicode values."""
        unicode_value = 'Test with émojis 🚀 and spécial characters'
        config_manager.set_setting('test', 'unicode', unicode_value)
        result = config_manager.get_setting('test', 'unicode')
        assert result == unicode_value

    def test_very_long_values(self, config_manager):
        """Test handling of very long values."""
        long_value = 'x' * 10000
        config_manager.set_setting('test', 'long_value', long_value)
        result = config_manager.get_setting('test', 'long_value')
        assert result == long_value

    def test_deep_nested_structures(self, config_manager):
        """Test handling of deeply nested data structures."""
        deep_structure = {
            'level1': {
                'level2': {
                    'level3': {
                        'level4': {
                            'deep_value': 'found_it'
                        }
                    }
                }
            }
        }
        config_manager.set_setting('test', 'deep', deep_structure)
        result = config_manager.get_setting('test', 'deep')
        assert result == deep_structure

    def test_special_characters_in_keys(self, config_manager):
        """Test handling of special characters in section and key names."""
        special_section = 'test-section_with.special@chars'
        special_key = 'key-with_special.chars@123'
        
        config_manager.set_setting(special_section, special_key, 'special_value')
        result = config_manager.get_setting(special_section, special_key)
        assert result == 'special_value'


if __name__ == '__main__':
    # Generate timestamp for test execution
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"Starting comprehensive ConfigManager tests at {timestamp}")
    
    # Run tests with detailed output
    pytest.main([
        __file__,
        '-v',
        '--tb=short',
        '--capture=no'
    ])