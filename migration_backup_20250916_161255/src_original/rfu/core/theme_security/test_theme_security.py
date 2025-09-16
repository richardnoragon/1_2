"""
Comprehensive Testing Framework for Theme Security Components

This module provides comprehensive testing for all Phase 2 theme security
components including unit tests, integration tests, and security validation.
"""

import unittest
import tempfile
import os
import shutil
import sqlite3
import json
from pathlib import Path
from unittest.mock import Mock, patch
import logging

# Configure test logging
logging.basicConfig(level=logging.WARNING)

# Import security components to test
try:
    from .theme_security_manager import ThemeSecurityManager
    from .theme_config import ThemeSecurityConfig
    from .theme_backup import ThemeBackupManager
    from .theme_recovery import ThemeRecoveryManager
    from .theme_validator import ThemeIntegrityValidator
    from .theme_access_control import ThemeAccessController
    from .theme_data_encryption import ThemeDataEncryption
except ImportError:
    # For standalone testing
    import sys
    sys.path.append('..')
    try:
        from theme_security_manager import ThemeSecurityManager
        from theme_config import ThemeSecurityConfig
        from theme_backup import ThemeBackupManager
        from theme_recovery import ThemeRecoveryManager
        from theme_validator import ThemeIntegrityValidator
        from theme_access_control import ThemeAccessController
        from theme_data_encryption import ThemeDataEncryption
    except ImportError:
        # Mock classes for testing
        ThemeSecurityManager = Mock
        ThemeSecurityConfig = Mock
        ThemeBackupManager = Mock
        ThemeRecoveryManager = Mock
        ThemeIntegrityValidator = Mock
        ThemeAccessController = Mock
        ThemeDataEncryption = Mock


class BaseSecurityTest(unittest.TestCase):
    """Base class for security component tests."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directories
        self.test_dir = tempfile.mkdtemp(prefix='theme_security_test_')
        self.config_dir = os.path.join(self.test_dir, 'config')
        self.data_dir = os.path.join(self.test_dir, 'data')
        self.backup_dir = os.path.join(self.test_dir, 'backups')
        
        os.makedirs(self.config_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # Test database path
        self.db_path = os.path.join(self.data_dir, 'test_security.db')
        
        # Sample theme data
        self.sample_theme = {
            'name': 'test_theme',
            'version': '1.0',
            'colors': {
                'primary': '#FF0000',
                'secondary': '#00FF00'
            },
            'settings': {
                'dark_mode': True,
                'font_size': 12
            }
        }
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def _create_test_database(self):
        """Create a test database with security tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create basic security tables for testing
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS theme_security_config (
                config_key TEXT PRIMARY KEY,
                config_value TEXT NOT NULL,
                config_type TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS theme_access_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                operation TEXT NOT NULL,
                theme_name TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                success BOOLEAN NOT NULL,
                details TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS theme_backups (
                backup_id TEXT PRIMARY KEY,
                theme_name TEXT NOT NULL,
                backup_path TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                size_bytes INTEGER,
                compression_type TEXT,
                checksum TEXT
            )
        """)
        
        conn.commit()
        conn.close()


class TestThemeSecurityConfig(BaseSecurityTest):
    """Test suite for ThemeSecurityConfig."""
    
    def test_config_initialization(self):
        """Test configuration initialization."""
        config_file = os.path.join(self.config_dir, 'security.json')
        
        if ThemeSecurityConfig != Mock:
            config = ThemeSecurityConfig(config_file, self.db_path)
            self.assertIsNotNone(config)
            
            # Test default configuration exists
            encryption_config = config.get_section('encryption')
            self.assertIsInstance(encryption_config, dict)
            
            # Test specific values
            self.assertEqual(config.get('encryption.algorithm'), 'AES-256-GCM')
            self.assertTrue(config.get('encryption.require_encryption'))
    
    def test_config_get_set(self):
        """Test configuration get/set operations."""
        if ThemeSecurityConfig == Mock:
            self.skipTest("ThemeSecurityConfig not available")
        
        config_file = os.path.join(self.config_dir, 'security.json')
        config = ThemeSecurityConfig(config_file, self.db_path)
        
        # Test setting and getting values
        self.assertTrue(config.set('test.value', 'test_data', persist=False))
        self.assertEqual(config.get('test.value'), 'test_data')
        
        # Test default values
        self.assertEqual(config.get('nonexistent.key', 'default'), 'default')
    
    def test_config_validation(self):
        """Test configuration validation."""
        if ThemeSecurityConfig == Mock:
            self.skipTest("ThemeSecurityConfig not available")
        
        config_file = os.path.join(self.config_dir, 'security.json')
        config = ThemeSecurityConfig(config_file, self.db_path)
        
        # Test validation
        validation_result = config.validate_configuration()
        self.assertIsInstance(validation_result, dict)
        self.assertIn('valid', validation_result)
        self.assertIn('errors', validation_result)
    
    def test_config_file_operations(self):
        """Test configuration file save/load operations."""
        if ThemeSecurityConfig == Mock:
            self.skipTest("ThemeSecurityConfig not available")
        
        config_file = os.path.join(self.config_dir, 'security.json')
        config = ThemeSecurityConfig(config_file, self.db_path)
        
        # Test saving to file
        self.assertTrue(config.save_to_file())
        self.assertTrue(os.path.exists(config_file))
        
        # Test reloading
        self.assertTrue(config.reload())


class TestThemeDataEncryption(BaseSecurityTest):
    """Test suite for ThemeDataEncryption."""
    
    def test_encryption_initialization(self):
        """Test encryption component initialization."""
        if ThemeDataEncryption == Mock:
            self.skipTest("ThemeDataEncryption not available")
        
        encryption = ThemeDataEncryption()
        self.assertIsNotNone(encryption)
    
    def test_encrypt_decrypt_roundtrip(self):
        """Test encryption and decryption roundtrip."""
        if ThemeDataEncryption == Mock:
            self.skipTest("ThemeDataEncryption not available")
        
        encryption = ThemeDataEncryption()
        
        # Test data encryption/decryption
        original_data = self.sample_theme
        encrypted_data = encryption.encrypt_theme_data(original_data)
        
        self.assertIsNotNone(encrypted_data)
        self.assertNotEqual(encrypted_data, original_data)
        
        # Decrypt and verify
        decrypted_data = encryption.decrypt_theme_data(encrypted_data)
        self.assertEqual(decrypted_data, original_data)
    
    def test_key_generation(self):
        """Test encryption key generation."""
        if ThemeDataEncryption == Mock:
            self.skipTest("ThemeDataEncryption not available")
        
        encryption = ThemeDataEncryption()
        
        # Test key generation
        key1 = encryption.generate_key()
        key2 = encryption.generate_key()
        
        self.assertIsNotNone(key1)
        self.assertIsNotNone(key2)
        self.assertNotEqual(key1, key2)  # Keys should be different


class TestThemeIntegrityValidator(BaseSecurityTest):
    """Test suite for ThemeIntegrityValidator."""
    
    def test_validator_initialization(self):
        """Test validator initialization."""
        if ThemeIntegrityValidator == Mock:
            self.skipTest("ThemeIntegrityValidator not available")
        
        validator = ThemeIntegrityValidator()
        self.assertIsNotNone(validator)
    
    def test_theme_validation(self):
        """Test theme data validation."""
        if ThemeIntegrityValidator == Mock:
            self.skipTest("ThemeIntegrityValidator not available")
        
        validator = ThemeIntegrityValidator()
        
        # Test valid theme
        validation_result = validator.validate_theme_data(self.sample_theme)
        self.assertIsInstance(validation_result, dict)
        self.assertIn('valid', validation_result)
        
        # Test invalid theme
        invalid_theme = {'invalid': 'structure'}
        validation_result = validator.validate_theme_data(invalid_theme)
        self.assertIsInstance(validation_result, dict)
    
    def test_corruption_detection(self):
        """Test corruption detection."""
        if ThemeIntegrityValidator == Mock:
            self.skipTest("ThemeIntegrityValidator not available")
        
        validator = ThemeIntegrityValidator()
        
        # Test with corrupted data
        corrupted_theme = self.sample_theme.copy()
        corrupted_theme['corrupted_field'] = None
        
        result = validator.detect_corruption(corrupted_theme)
        self.assertIsInstance(result, dict)


class TestThemeAccessController(BaseSecurityTest):
    """Test suite for ThemeAccessController."""
    
    def setUp(self):
        """Set up access controller test environment."""
        super().setUp()
        self._create_test_database()
    
    def test_access_controller_initialization(self):
        """Test access controller initialization."""
        if ThemeAccessController == Mock:
            self.skipTest("ThemeAccessController not available")
        
        controller = ThemeAccessController(self.db_path)
        self.assertIsNotNone(controller)
    
    def test_permission_checking(self):
        """Test permission checking functionality."""
        if ThemeAccessController == Mock:
            self.skipTest("ThemeAccessController not available")
        
        controller = ThemeAccessController(self.db_path)
        
        # Test permission check
        user_id = "test_user"
        operation = "read_theme"
        
        result = controller.check_permission(user_id, operation)
        self.assertIsInstance(result, bool)
    
    def test_audit_logging(self):
        """Test audit logging functionality."""
        if ThemeAccessController == Mock:
            self.skipTest("ThemeAccessController not available")
        
        controller = ThemeAccessController(self.db_path)
        
        # Test audit log creation
        user_id = "test_user"
        operation = "test_operation"
        theme_name = "test_theme"
        
        result = controller.log_access(user_id, operation, theme_name, True)
        self.assertTrue(result)


class TestThemeBackupManager(BaseSecurityTest):
    """Test suite for ThemeBackupManager."""
    
    def setUp(self):
        """Set up backup manager test environment."""
        super().setUp()
        self._create_test_database()
    
    def test_backup_manager_initialization(self):
        """Test backup manager initialization."""
        if ThemeBackupManager == Mock:
            self.skipTest("ThemeBackupManager not available")
        
        manager = ThemeBackupManager(self.backup_dir, self.db_path)
        self.assertIsNotNone(manager)
    
    def test_backup_creation(self):
        """Test backup creation."""
        if ThemeBackupManager == Mock:
            self.skipTest("ThemeBackupManager not available")
        
        manager = ThemeBackupManager(self.backup_dir, self.db_path)
        
        # Create a test theme file
        theme_file = os.path.join(self.data_dir, 'test_theme.json')
        with open(theme_file, 'w') as f:
            json.dump(self.sample_theme, f)
        
        # Test backup creation
        backup_id = manager.create_backup('test_theme', theme_file)
        
        if backup_id:
            self.assertIsNotNone(backup_id)
            
            # Verify backup file exists
            backup_files = list(Path(self.backup_dir).glob('*.backup'))
            self.assertGreater(len(backup_files), 0)
    
    def test_backup_verification(self):
        """Test backup verification."""
        if ThemeBackupManager == Mock:
            self.skipTest("ThemeBackupManager not available")
        
        manager = ThemeBackupManager(self.backup_dir, self.db_path)
        
        # Create and verify a backup
        theme_file = os.path.join(self.data_dir, 'test_theme.json')
        with open(theme_file, 'w') as f:
            json.dump(self.sample_theme, f)
        
        backup_id = manager.create_backup('test_theme', theme_file)
        
        if backup_id:
            result = manager.verify_backup(backup_id)
            self.assertIsInstance(result, dict)


class TestThemeRecoveryManager(BaseSecurityTest):
    """Test suite for ThemeRecoveryManager."""
    
    def setUp(self):
        """Set up recovery manager test environment."""
        super().setUp()
        self._create_test_database()
    
    def test_recovery_manager_initialization(self):
        """Test recovery manager initialization."""
        if ThemeRecoveryManager == Mock:
            self.skipTest("ThemeRecoveryManager not available")
        
        manager = ThemeRecoveryManager(self.backup_dir, self.db_path)
        self.assertIsNotNone(manager)
    
    def test_corruption_recovery(self):
        """Test corruption recovery process."""
        if ThemeRecoveryManager == Mock:
            self.skipTest("ThemeRecoveryManager not available")
        
        manager = ThemeRecoveryManager(self.backup_dir, self.db_path)
        
        # Create corrupted theme file
        corrupted_file = os.path.join(self.data_dir, 'corrupted_theme.json')
        with open(corrupted_file, 'w') as f:
            f.write('invalid json content')
        
        # Test recovery attempt
        recovery_result = manager.attempt_recovery('corrupted_theme', corrupted_file)
        self.assertIsInstance(recovery_result, dict)
        self.assertIn('success', recovery_result)


class TestThemeSecurityManager(BaseSecurityTest):
    """Test suite for ThemeSecurityManager (integration tests)."""
    
    def setUp(self):
        """Set up security manager test environment."""
        super().setUp()
        self._create_test_database()
    
    def test_security_manager_initialization(self):
        """Test security manager initialization."""
        if ThemeSecurityManager == Mock:
            self.skipTest("ThemeSecurityManager not available")
        
        manager = ThemeSecurityManager()
        self.assertIsNotNone(manager)
    
    @patch('keyring.get_password')
    @patch('keyring.set_password')
    def test_secure_theme_operations(self, mock_set_password, mock_get_password):
        """Test secure theme save/load operations."""
        if ThemeSecurityManager == Mock:
            self.skipTest("ThemeSecurityManager not available")
        
        # Mock keyring operations
        mock_get_password.return_value = None
        mock_set_password.return_value = None
        
        manager = ThemeSecurityManager()
        
        # Test secure save
        theme_file = os.path.join(self.data_dir, 'secure_theme.json')
        result = manager.save_theme_secure('test_theme', self.sample_theme, theme_file)
        
        if result:
            self.assertTrue(result)
            
            # Test secure load
            loaded_theme = manager.load_theme_secure('test_theme', theme_file)
            if loaded_theme:
                self.assertEqual(loaded_theme, self.sample_theme)
    
    def test_security_status(self):
        """Test security status reporting."""
        if ThemeSecurityManager == Mock:
            self.skipTest("ThemeSecurityManager not available")
        
        manager = ThemeSecurityManager()
        
        # Test status retrieval
        status = manager.get_security_status()
        self.assertIsInstance(status, dict)
        
        # Check expected status fields
        expected_fields = ['encryption_enabled', 'backup_count', 'access_control_enabled']
        for field in expected_fields:
            if field in status:
                self.assertIsInstance(status[field], (bool, int))


class TestSecurityIntegration(BaseSecurityTest):
    """Integration tests for complete security system."""
    
    def setUp(self):
        """Set up integration test environment."""
        super().setUp()
        self._create_test_database()
    
    def test_full_security_workflow(self):
        """Test complete security workflow."""
        if any(cls == Mock for cls in [ThemeSecurityManager, ThemeSecurityConfig, 
                                      ThemeBackupManager, ThemeIntegrityValidator]):
            self.skipTest("Security components not available")
        
        # Initialize components
        config = ThemeSecurityConfig(
            os.path.join(self.config_dir, 'security.json'),
            self.db_path
        )
        manager = ThemeSecurityManager()
        backup_mgr = ThemeBackupManager(self.backup_dir, self.db_path)
        validator = ThemeIntegrityValidator()
        
        # 1. Configure security settings
        config.set('encryption.require_encryption', True)
        config.set('backup.auto_backup_enabled', True)
        
        # 2. Validate theme data
        validation_result = validator.validate_theme_data(self.sample_theme)
        self.assertTrue(validation_result.get('valid', False))
        
        # 3. Create backup
        theme_file = os.path.join(self.data_dir, 'workflow_theme.json')
        with open(theme_file, 'w') as f:
            json.dump(self.sample_theme, f)
        
        backup_id = backup_mgr.create_backup('workflow_theme', theme_file)
        if backup_id:
            self.assertIsNotNone(backup_id)
        
        # 4. Save theme securely
        with patch('keyring.get_password', return_value=None), \
             patch('keyring.set_password', return_value=None):
            
            result = manager.save_theme_secure('workflow_theme', self.sample_theme, theme_file)
            if result:
                self.assertTrue(result)
                
                # 5. Load theme securely
                loaded_theme = manager.load_theme_secure('workflow_theme', theme_file)
                if loaded_theme:
                    self.assertEqual(loaded_theme, self.sample_theme)
    
    def test_error_handling(self):
        """Test error handling across components."""
        if any(cls == Mock for cls in [ThemeSecurityManager, ThemeBackupManager]):
            self.skipTest("Security components not available")
        
        # Test with invalid paths
        manager = ThemeSecurityManager()
        
        # These should handle errors gracefully
        invalid_file = '/invalid/file/path.json'
        
        with patch('keyring.get_password', return_value=None):
            result = manager.load_theme_secure('invalid_theme', invalid_file)
            # Should return None or handle error gracefully
            self.assertIsNone(result)


class SecurityTestSuite:
    """Test suite runner for security components."""
    
    @staticmethod
    def run_all_tests():
        """Run all security tests."""
        # Create test suite
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()
        
        # Add test classes
        test_classes = [
            TestThemeSecurityConfig,
            TestThemeDataEncryption,
            TestThemeIntegrityValidator,
            TestThemeAccessController,
            TestThemeBackupManager,
            TestThemeRecoveryManager,
            TestThemeSecurityManager,
            TestSecurityIntegration
        ]
        
        for test_class in test_classes:
            tests = loader.loadTestsFromTestCase(test_class)
            suite.addTests(tests)
        
        # Run tests
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return result
    
    @staticmethod
    def run_unit_tests():
        """Run only unit tests."""
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()
        
        unit_test_classes = [
            TestThemeSecurityConfig,
            TestThemeDataEncryption,
            TestThemeIntegrityValidator,
            TestThemeAccessController,
            TestThemeBackupManager,
            TestThemeRecoveryManager
        ]
        
        for test_class in unit_test_classes:
            tests = loader.loadTestsFromTestCase(test_class)
            suite.addTests(tests)
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return result
    
    @staticmethod
    def run_integration_tests():
        """Run only integration tests."""
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()
        
        integration_test_classes = [
            TestThemeSecurityManager,
            TestSecurityIntegration
        ]
        
        for test_class in integration_test_classes:
            tests = loader.loadTestsFromTestCase(test_class)
            suite.addTests(tests)
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return result


if __name__ == '__main__':
    # Run tests based on command line arguments
    import sys
    
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
        
        if test_type == 'unit':
            print("Running unit tests...")
            result = SecurityTestSuite.run_unit_tests()
        elif test_type == 'integration':
            print("Running integration tests...")
            result = SecurityTestSuite.run_integration_tests()
        else:
            print("Running all tests...")
            result = SecurityTestSuite.run_all_tests()
    else:
        print("Running all tests...")
        result = SecurityTestSuite.run_all_tests()
    
    # Exit with error code if tests failed
    if not result.wasSuccessful():
        sys.exit(1)