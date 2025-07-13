import unittest
import os
import json
from tests.test_utils import TestUtils
from config_manager import ConfigManager

from core.error_handler import error_handler


class TestConfigManager(unittest.TestCase):
    """A class that handles test config manager."""
    def setUp(self):
        """setup."""
        self.test_dir = TestUtils.create_temp_dir()
        self.config_file = os.path.join(self.test_dir, "config.json")
        self.config_manager = ConfigManager()
        # Store original config path and replace it
        self.original_config_path = self.config_manager.config_path
        self.config_manager.config_path = self.config_file

    def tearDown(self):
        """teardown."""
        TestUtils.cleanup_temp_dir(self.test_dir)

    def test_default_config(self):
        """Test loading default configuration"""
        config = self.config_manager.get_config()
        
        # Verify default values
        self.assertIsInstance(config, dict)
        self.assertIn('theme', config)
        self.assertIn('language', config)
        self.assertEqual(config['theme'], 'light')
        self.assertEqual(config['language'], 'en')

    def test_save_load_config(self):
        """Test saving and loading configuration"""
        test_config = {
            'theme': 'dark',
            'language': 'de',
            'show_hidden': True
        }
        
        # Save config
        self.config_manager.save_config(test_config)
        
        # Verify file exists
        self.assertTrue(os.path.exists(self.config_file))
        
        # Load config
        loaded_config = self.config_manager.get_config()
        
        # Verify loaded values match saved values
        for key, value in test_config.items():
            self.assertEqual(loaded_config[key], value)

    def test_update_config(self):
        """Test updating configuration values"""
        # Set initial config
        self.config_manager.save_config({
            'theme': 'light',
            'language': 'en'
        })
        
        # Update single value
        self.config_manager.update_config('theme', 'dark')
        
        # Verify update
        config = self.config_manager.get_config()
        self.assertEqual(config['theme'], 'dark')
        self.assertEqual(config['language'], 'en')

    def test_update_multiple(self):
        """Test updating multiple configuration values"""
        # Set initial config
        self.config_manager.save_config({
            'theme': 'light',
            'language': 'en',
            'show_hidden': False
        })
        
        # Update multiple values
        updates = {
            'theme': 'dark',
            'show_hidden': True
        }
        self.config_manager.update_multiple(updates)
        
        # Verify updates
        config = self.config_manager.get_config()
        self.assertEqual(config['theme'], 'dark')
        self.assertEqual(config['show_hidden'], True)
        self.assertEqual(config['language'], 'en')

    def test_invalid_config_file(self):
        """Test handling of invalid configuration file"""
        # Write invalid JSON
        with open(self.config_file, 'w') as f:
            f.write('invalid json')
        
        # Should load default config
        config = self.config_manager.get_config()
        self.assertIsInstance(config, dict)
        self.assertIn('theme', config)

    def test_missing_config_file(self):
        """Test handling of missing configuration file"""
        # Don't create config file
        config = self.config_manager.get_config()
        
        # Should return default config
        self.assertIsInstance(config, dict)
        self.assertIn('theme', config)

    def test_type_validation(self):
        """Test configuration value type validation"""
        # Test invalid types
        invalid_configs = [
            {'theme': 123},  # theme should be string
            {'show_hidden': 'true'},  # show_hidden should be bool
            {'language': True}  # language should be string
        ]
        
        for invalid_config in invalid_configs:
            with self.assertRaises(ValueError):
                self.config_manager.save_config(invalid_config)

    def test_required_fields(self):
        """Test handling of required configuration fields"""
        # Try to save config missing required fields
        incomplete_config = {'theme': 'dark'}  # missing language
        
        with self.assertRaises(ValueError):
            self.config_manager.save_config(incomplete_config, validate_required=True)

    def test_config_reset(self):
        """Test resetting configuration to defaults"""
        # Set custom config
        test_config = {
            'theme': 'dark',
            'language': 'de',
            'show_hidden': True
        }
        self.config_manager.save_config(test_config)
        
        # Reset config
        self.config_manager.reset_to_defaults()
        
        # Verify defaults are restored
        config = self.config_manager.get_config()
        self.assertEqual(config['theme'], 'light')
        self.assertEqual(config['language'], 'en')
        self.assertFalse(config['show_hidden'])

    def test_config_backup(self):
        """Test configuration backup functionality"""
        # Set initial config
        test_config = {
            'theme': 'dark',
            'language': 'de'
        }
        self.config_manager.save_config(test_config)
        
        # Create backup
        backup_file = self.config_manager.create_backup()
        
        # Verify backup file exists
        self.assertTrue(os.path.exists(backup_file))
        
        # Verify backup content
        with open(backup_file, 'r') as f:
            backup_config = json.load(f)
            self.assertEqual(backup_config, test_config)

    def test_config_restore(self):
        """Test configuration restore functionality"""
        # Set initial config
        original_config = {
            'theme': 'dark',
            'language': 'de'
        }
        self.config_manager.save_config(original_config)
        
        # Create backup
        backup_file = self.config_manager.create_backup()
        
        # Change config
        self.config_manager.update_config('theme', 'light')
        
        # Restore from backup
        self.config_manager.restore_from_backup(backup_file)
        
        # Verify restored config matches original
        restored_config = self.config_manager.get_config()
        self.assertEqual(restored_config, original_config)

if __name__ == '__main__':
    unittest.main()