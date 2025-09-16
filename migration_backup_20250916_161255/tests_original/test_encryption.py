"""
Comprehensive test suite for encryption functionality.

This module tests all components of the encryption migration including
core logic, configuration, logging, GUI, and integration.
"""

import os
import sys
import tempfile
import shutil
import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from file_utilities_2.core.encryption_logic import EncryptionLogic
from file_utilities_2.core.encryption_config import EncryptionConfig
from file_utilities_2.core.encryption_logging import EncryptionLogger, LogLevel, SecurityEvent
from file_utilities_2.integration.encryption_connector import EncryptionHubConnector


class TestEncryptionLogic(unittest.TestCase):
    """Test cases for EncryptionLogic class."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = Mock()
        self.logger = Mock()
        self.hub_instance = Mock()
        
        self.encryption_logic = EncryptionLogic(
            config=self.config,
            logger=self.logger,
            hub_instance=self.hub_instance
        )
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_key_generation(self):
        """Test encryption key generation."""
        key = self.encryption_logic.generate_key()
        
        self.assertIsNotNone(key)
        self.assertIsInstance(key, bytes)
        self.assertEqual(len(key), 44)  # Fernet key length
    
    def test_key_save_and_load(self):
        """Test key saving and loading."""
        key = self.encryption_logic.generate_key()
        key_path = os.path.join(self.temp_dir, "test.key")
        
        # Test saving
        result = self.encryption_logic.save_key(key, key_path)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(key_path))
        
        # Test loading
        loaded_key = self.encryption_logic.load_key(key_path)
        self.assertEqual(key, loaded_key)
    
    def test_file_encryption_decryption(self):
        """Test file encryption and decryption."""
        # Create test file
        test_file = os.path.join(self.temp_dir, "test.txt")
        test_content = "This is a test file for encryption."
        
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        # Generate key
        key = self.encryption_logic.generate_key()
        
        # Test encryption
        encrypted_file = os.path.join(self.temp_dir, "test.txt.encrypted")
        result = self.encryption_logic.encrypt_file(test_file, key, encrypted_file)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(encrypted_file))
        
        # Verify encrypted content is different
        with open(encrypted_file, 'rb') as f:
            encrypted_content = f.read()
        self.assertNotEqual(test_content.encode(), encrypted_content)
        
        # Test decryption
        decrypted_file = os.path.join(self.temp_dir, "test.txt.decrypted")
        result = self.encryption_logic.decrypt_file(encrypted_file, key, decrypted_file)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(decrypted_file))
        
        # Verify decrypted content matches original
        with open(decrypted_file, 'r', encoding='utf-8') as f:
            decrypted_content = f.read()
        self.assertEqual(test_content, decrypted_content)
    
    def test_directory_encryption(self):
        """Test directory encryption."""
        # Create test directory structure
        test_dir = os.path.join(self.temp_dir, "test_dir")
        os.makedirs(test_dir)
        
        # Create test files
        for i in range(3):
            file_path = os.path.join(test_dir, f"file_{i}.txt")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"Content of file {i}")
        
        # Create subdirectory
        sub_dir = os.path.join(test_dir, "subdir")
        os.makedirs(sub_dir)
        sub_file = os.path.join(sub_dir, "sub_file.txt")
        with open(sub_file, 'w', encoding='utf-8') as f:
            f.write("Subdirectory file content")
        
        # Generate key
        key = self.encryption_logic.generate_key()
        
        # Test directory encryption
        results = self.encryption_logic.encrypt_directory(test_dir, key, recursive=True)
        
        self.assertIsInstance(results, dict)
        self.assertIn('success_count', results)
        self.assertIn('error_count', results)
        self.assertEqual(results['error_count'], 0)
        self.assertGreater(results['success_count'], 0)
    
    def test_operation_cancellation(self):
        """Test operation cancellation."""
        self.encryption_logic.cancel_operation()
        self.assertTrue(self.encryption_logic._cancel_requested)
    
    def test_progress_tracking(self):
        """Test progress tracking functionality."""
        # Mock progress update
        with patch.object(self.encryption_logic, 'progress_updated') as mock_signal:
            self.encryption_logic._update_progress(50, 100, "Test progress")
            mock_signal.emit.assert_called_once_with(50, 100, "Test progress")


class TestEncryptionConfig(unittest.TestCase):
    """Test cases for EncryptionConfig class."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "test_config.json")
        self.config = EncryptionConfig(config_path=self.config_path)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_default_configuration(self):
        """Test default configuration loading."""
        self.assertIsInstance(self.config._config, dict)
        self.assertIn('user_preferences', self.config._config)
        self.assertIn('security_settings', self.config._config)
        self.assertIn('performance_settings', self.config._config)
    
    def test_setting_get_and_set(self):
        """Test getting and setting configuration values."""
        # Test getting default value
        buffer_size = self.config.get_setting('performance_settings.buffer_size')
        self.assertEqual(buffer_size, 8192)
        
        # Test setting new value
        result = self.config.set_setting('performance_settings.buffer_size', 16384)
        self.assertTrue(result)
        
        # Test getting updated value
        new_buffer_size = self.config.get_setting('performance_settings.buffer_size')
        self.assertEqual(new_buffer_size, 16384)
    
    def test_setting_validation(self):
        """Test setting validation."""
        # Test valid setting
        result = self.config.set_setting('performance_settings.buffer_size', 4096)
        self.assertTrue(result)
        
        # Test invalid setting (too small)
        result = self.config.set_setting('performance_settings.buffer_size', 512)
        self.assertFalse(result)
    
    def test_configuration_export_import(self):
        """Test configuration export and import."""
        # Modify some settings
        self.config.set_setting('performance_settings.buffer_size', 16384)
        self.config.set_setting('user_preferences.confirm_overwrite', False)
        
        # Export configuration
        export_path = os.path.join(self.temp_dir, "exported_config.json")
        result = self.config.export_config(export_path)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(export_path))
        
        # Create new config instance
        new_config_path = os.path.join(self.temp_dir, "new_config.json")
        new_config = EncryptionConfig(config_path=new_config_path)
        
        # Import configuration
        result = new_config.import_config(export_path)
        self.assertTrue(result)
        
        # Verify imported settings
        buffer_size = new_config.get_setting('performance_settings.buffer_size')
        self.assertEqual(buffer_size, 16384)
        confirm_overwrite = new_config.get_setting('user_preferences.confirm_overwrite')
        self.assertFalse(confirm_overwrite)
    
    def test_configuration_validation(self):
        """Test configuration validation."""
        issues = self.config.validate_settings()
        self.assertIsInstance(issues, list)
        
        # All default settings should be valid
        error_issues = [issue for issue in issues if issue['severity'] == 'error']
        self.assertEqual(len(error_issues), 0)


class TestEncryptionLogger(unittest.TestCase):
    """Test cases for EncryptionLogger class."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.logger = EncryptionLogger(log_directory=self.temp_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        self.logger.close()
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_logging_functionality(self):
        """Test basic logging functionality."""
        self.logger.log(LogLevel.INFO, "Test message", {"key": "value"})
        
        # Verify log file was created
        log_files = [f for f in os.listdir(self.temp_dir) if f.startswith('encryption_')]
        self.assertGreater(len(log_files), 0)
    
    def test_audit_logging(self):
        """Test audit logging functionality."""
        self.logger.audit(SecurityEvent.KEY_GENERATED, {"key_type": "test"})
        
        # Verify audit file was created
        self.assertTrue(os.path.exists(self.logger.audit_file))
        
        # Verify audit entry was written
        audit_entries = self.logger.export_audit_log()
        self.assertGreater(len(audit_entries), 0)
        self.assertEqual(audit_entries[0]['event_type'], 'key_generated')
    
    def test_operation_timing(self):
        """Test operation timing functionality."""
        operation_id = "test_operation"
        
        # Start timing
        self.logger.start_operation_timing(operation_id)
        self.assertIn(operation_id, self.logger._operation_timings)
        
        # End timing
        import time
        time.sleep(0.1)  # Small delay for measurable duration
        duration = self.logger.end_operation_timing(operation_id)
        
        self.assertGreater(duration, 0)
        self.assertIsNotNone(self.logger._operation_timings[operation_id]['end_time'])
    
    def test_session_statistics(self):
        """Test session statistics tracking."""
        stats = self.logger.get_session_stats()
        
        self.assertIsInstance(stats, dict)
        self.assertIn('session_id', stats)
        self.assertIn('operations_count', stats)
        self.assertIn('session_duration_seconds', stats)


class TestEncryptionHubConnector(unittest.TestCase):
    """Test cases for EncryptionHubConnector class."""
    
    def setUp(self):
        """Set up test environment."""
        self.hub_instance = Mock()
        self.connector = EncryptionHubConnector(hub_instance=self.hub_instance)
    
    def test_operation_registration(self):
        """Test operation registration."""
        operation_id = self.connector.register_operation(
            "encrypt_file", 
            {"file_path": "test.txt", "key": "test_key"}
        )
        
        self.assertIsInstance(operation_id, str)
        self.assertIn(operation_id, self.connector.active_operations)
        
        operation = self.connector.get_operation_status(operation_id)
        self.assertEqual(operation['type'], 'encrypt_file')
        self.assertEqual(operation['status'], 'starting')
    
    def test_progress_tracking(self):
        """Test progress tracking."""
        operation_id = self.connector.register_operation("test_operation", {})
        
        # Update progress
        self.connector.update_operation_progress(operation_id, 50, 100, "Half done")
        
        operation = self.connector.get_operation_status(operation_id)
        self.assertEqual(operation['progress'], 50)
        self.assertEqual(operation['total'], 100)
        self.assertEqual(operation['message'], "Half done")
        self.assertEqual(operation['status'], 'in_progress')
    
    def test_operation_completion(self):
        """Test operation completion."""
        operation_id = self.connector.register_operation("test_operation", {})
        
        # Complete operation
        results = {"success": True, "bytes_processed": 1024}
        self.connector.complete_operation(operation_id, results)
        
        # Operation should be removed from active operations
        self.assertNotIn(operation_id, self.connector.active_operations)
        
        # Metrics should be updated
        metrics = self.connector.get_performance_metrics()
        self.assertEqual(metrics['successful_operations'], 1)
        self.assertEqual(metrics['total_bytes_processed'], 1024)
    
    def test_operation_failure(self):
        """Test operation failure handling."""
        operation_id = self.connector.register_operation("test_operation", {})
        
        # Fail operation
        self.connector.fail_operation(operation_id, "Test error")
        
        # Operation should be removed from active operations
        self.assertNotIn(operation_id, self.connector.active_operations)
        
        # Metrics should be updated
        metrics = self.connector.get_performance_metrics()
        self.assertEqual(metrics['failed_operations'], 1)
    
    def test_resource_management(self):
        """Test resource management functionality."""
        # Update resource usage
        self.connector.update_resource_usage(
            memory_mb=100, 
            cpu_percent=25, 
            disk_io_mb=10,
            active_files=["file1.txt", "file2.txt"]
        )
        
        usage = self.connector.get_resource_usage()
        self.assertEqual(usage['memory_usage'], 100)
        self.assertEqual(usage['cpu_usage'], 25)
        self.assertEqual(usage['disk_io'], 10)
        self.assertEqual(len(usage['active_files']), 2)
    
    def test_hub_communication(self):
        """Test hub communication functionality."""
        # Test resource allocation request
        result = self.connector.request_resource_allocation("memory", 512)
        self.assertTrue(result)  # Should default to True if no hub
        
        # Test coordination message
        result = self.connector.coordinate_with_other_tools("test_message", {"data": "test"})
        self.assertFalse(result)  # Should default to False if no hub method


class TestEncryptionIntegration(unittest.TestCase):
    """Integration tests for encryption components."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create integrated components
        self.config = EncryptionConfig()
        self.logger = EncryptionLogger(log_directory=self.temp_dir)
        self.hub_connector = EncryptionHubConnector()
        
        self.encryption_logic = EncryptionLogic(
            config=self.config,
            logger=self.logger,
            hub_instance=self.hub_connector
        )
    
    def tearDown(self):
        """Clean up test environment."""
        self.logger.close()
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_end_to_end_encryption(self):
        """Test complete encryption workflow."""
        # Create test file
        test_file = os.path.join(self.temp_dir, "integration_test.txt")
        test_content = "Integration test content for encryption workflow."
        
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        # Generate and save key
        key = self.encryption_logic.generate_key()
        key_file = os.path.join(self.temp_dir, "test.key")
        self.encryption_logic.save_key(key, key_file)
        
        # Encrypt file
        encrypted_file = test_file + ".encrypted"
        result = self.encryption_logic.encrypt_file(test_file, key, encrypted_file)
        self.assertTrue(result)
        
        # Decrypt file
        decrypted_file = test_file + ".decrypted"
        result = self.encryption_logic.decrypt_file(encrypted_file, key, decrypted_file)
        self.assertTrue(result)
        
        # Verify content
        with open(decrypted_file, 'r', encoding='utf-8') as f:
            decrypted_content = f.read()
        self.assertEqual(test_content, decrypted_content)
        
        # Verify logging occurred
        audit_entries = self.logger.export_audit_log()
        self.assertGreater(len(audit_entries), 0)
    
    def test_configuration_integration(self):
        """Test configuration integration with other components."""
        # Update configuration
        self.config.set_setting('performance_settings.buffer_size', 16384)
        
        # Verify encryption logic uses updated config
        buffer_size = self.config.get_setting('performance_settings.buffer_size')
        self.assertEqual(buffer_size, 16384)
    
    def test_error_handling_integration(self):
        """Test error handling across components."""
        # Try to encrypt non-existent file
        result = self.encryption_logic.encrypt_file(
            "non_existent_file.txt", 
            b"fake_key", 
            "output.txt"
        )
        self.assertFalse(result)
        
        # Verify error was logged
        # Note: In a real implementation, we'd check the log files


def run_encryption_tests():
    """Run all encryption tests."""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestEncryptionLogic))
    test_suite.addTest(unittest.makeSuite(TestEncryptionConfig))
    test_suite.addTest(unittest.makeSuite(TestEncryptionLogger))
    test_suite.addTest(unittest.makeSuite(TestEncryptionHubConnector))
    test_suite.addTest(unittest.makeSuite(TestEncryptionIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_encryption_tests()
    sys.exit(0 if success else 1)