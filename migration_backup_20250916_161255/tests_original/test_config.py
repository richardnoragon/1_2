import unittest
import os
import json
from tests.test_utils import TestUtils
from config_manager import ConfigManager

class TestConfigManager(unittest.TestCase):
    """A class that handles test config manager."""
    def setUp(self):
        """setup."""
        self.test_dir = TestUtils.create_temp_dir()
        self.config_file = os.path.join(self.test_dir, "test_config.json")
        self.config_manager = ConfigManager(self.config_file)
        
        # Default test configuration
        self.test_config = {
            'last_directory': '/test/path',
            'file_types': ['.txt', '.doc', '.pdf'],
            'theme': 'light',
            'language': 'en',
            'auto_backup': True,
            'max_recent_files': 10
        }

    def tearDown(self):
        """teardown."""
        TestUtils.cleanup_temp_dir(self.test_dir)

    def test_save_load_config(self):
        """Test saving and loading configuration"""
        # Save configuration
        self.config_manager.save_config(self.test_config)
        
        # Verify file was created
        self.assertTrue(os.path.exists(self.config_file))
        
        # Load and verify configuration
        loaded_config = self.config_manager.load_config()
        self.assertEqual(loaded_config, self.test_config)

    def test_get_set_value(self):
        """Test getting and setting individual config values"""
        # Set initial config
        self.config_manager.save_config(self.test_config)
        
        # Test getting value
        self.assertEqual(
            self.config_manager.get_value('theme'),
            'light'
        )
        
        # Test setting value
        self.config_manager.set_value('theme', 'dark')
        self.assertEqual(
            self.config_manager.get_value('theme'),
            'dark'
        )
        
        # Verify persistence
        loaded_config = self.config_manager.load_config()
        self.assertEqual(loaded_config['theme'], 'dark')

    def test_default_config(self):
        """Test loading default configuration when file doesn't exist"""
        # Don't create config file
        config = self.config_manager.load_config()
        
        # Verify default values are set
        self.assertIsNotNone(config)
        self.assertTrue(isinstance(config, dict))
        self.assertIn('last_directory', config)
        self.assertIn('theme', config)

    def test_invalid_config(self):
        """Test handling of invalid configuration file"""
        # Write invalid JSON
        with open(self.config_file, 'w') as f:
            f.write('invalid json content')
        
        # Should load default config when file is invalid
        config = self.config_manager.load_config()
        self.assertIsNotNone(config)
        self.assertTrue(isinstance(config, dict))

    def test_merge_config(self):
        """Test merging new configuration with existing"""
        # Set initial config
        self.config_manager.save_config(self.test_config)
        
        # Merge new settings
        new_settings = {
            'theme': 'dark',
            'new_setting': 'value'
        }
        self.config_manager.merge_config(new_settings)
        
        # Verify merge
        config = self.config_manager.load_config()
        self.assertEqual(config['theme'], 'dark')
        self.assertEqual(config['new_setting'], 'value')
        self.assertEqual(config['language'], 'en')  # Original value preserved

    def test_config_validation(self):
        """Test configuration validation"""
        invalid_config = {
            'max_recent_files': 'not a number',  # Should be int
            'auto_backup': 'not a boolean'       # Should be bool
        }
        
        # Should raise ValueError for invalid types
        with self.assertRaises(ValueError):
            self.config_manager.save_config(invalid_config)

if __name__ == '__main__':
    unittest.main()

import os
import sys
import json

from core.error_handler import error_handler


class TestConfig:
    """Configuration management for test suite"""
    
    _default_config = {
        'temp_dir': None,  # Will be set at runtime
        'gui': {
            'enabled': True,
            'screenshot_dir': 'test-reports/screenshots',
            'wait_time': 0.5  # seconds to wait for GUI operations
        },
        'file_sizes': {
            'small': 1024,        # 1 KB
            'medium': 1024*1024,  # 1 MB
            'large': 1024*1024*10 # 10 MB
        },
        'timeouts': {
            'short': 5,   # 5 seconds
            'medium': 30, # 30 seconds
            'long': 120   # 2 minutes
        },
        'parallel': {
            'enabled': True,
            'max_workers': None  # Will use CPU count if None
        }
    }
    
    @classmethod
    def load(cls):
        """Load test configuration, combining defaults with custom settings"""
        # Start with default config
        config = cls._default_config.copy()
        
        # Look for custom config file
        config_file = os.getenv('RFU_TEST_CONFIG', 'test_config.json')
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                custom_config = json.load(f)
                cls._update_recursive(config, custom_config)
        
        # Apply environment variables
        cls._apply_env_vars(config)
        
        # Set runtime values
        config['temp_dir'] = os.getenv('RFU_TEST_TEMP_DIR') or os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'test-tmp'
        )
        
        # Create required directories
        os.makedirs(config['temp_dir'], exist_ok=True)
        os.makedirs(config['gui']['screenshot_dir'], exist_ok=True)
        
        return config
    
    @staticmethod
    def _update_recursive(base, update):
        """Recursively update a dictionary"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict):
                if isinstance(value, dict):
                    TestConfig._update_recursive(base[key], value)
                else:
                    base[key] = value
            else:
                base[key] = value
    
    @staticmethod
    def _apply_env_vars(config):
        """Apply environment variables to configuration"""
        # GUI settings
        if os.getenv('RFU_TEST_NO_GUI'):
            config['gui']['enabled'] = False
        
        # Parallel execution
        if os.getenv('RFU_TEST_NO_PARALLEL'):
            config['parallel']['enabled'] = False
        if os.getenv('RFU_TEST_MAX_WORKERS'):
            config['parallel']['max_workers'] = int(os.getenv('RFU_TEST_MAX_WORKERS'))
        
        # Timeouts
        for timeout in config['timeouts']:
            env_var = f'RFU_TEST_TIMEOUT_{timeout.upper()}'
            if os.getenv(env_var):
                config['timeouts'][timeout] = int(os.getenv(env_var))
    
    @staticmethod
    def save_current():
        """Save current configuration to file"""
        config = TestConfig.load()
        with open('test_config.json', 'w') as f:
            json.dump(config, f, indent=4)