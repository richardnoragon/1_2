import unittest
import os
import logging
from tests.test_utils import TestUtils
from log_manager import LogManager

from core.error_handler import error_handler


class TestLogging(unittest.TestCase):
    def setUp(self):
        self.test_dir = TestUtils.create_temp_dir()
        self.log_file = os.path.join(self.test_dir, "test.log")
        self.log_manager = LogManager(self.log_file)

    def tearDown(self):
        TestUtils.cleanup_temp_dir(self.test_dir)
        # Reset logging configuration
        logging.getLogger().handlers = []

    def test_log_file_creation(self):
        """Test log file is created and writable"""
        self.log_manager.info("Test message")
        self.assertTrue(os.path.exists(self.log_file))
        
        with open(self.log_file, 'r') as f:
            content = f.read()
            self.assertIn("Test message", content)

    def test_log_levels(self):
        """Test different logging levels"""
        test_messages = {
            'debug': 'Debug message',
            'info': 'Info message',
            'warning': 'Warning message',
            'error': 'Error message',
            'critical': 'Critical message'
        }
        
        # Log messages at different levels
        self.log_manager.debug(test_messages['debug'])
        self.log_manager.info(test_messages['info'])
        self.log_manager.warning(test_messages['warning'])
        self.log_manager.error(test_messages['error'])
        self.log_manager.critical(test_messages['critical'])
        
        # Read log file and verify
        with open(self.log_file, 'r') as f:
            content = f.read()
            for message in test_messages.values():
                self.assertIn(message, content)

    def test_log_rotation(self):
        """Test log file rotation"""
        # Write enough logs to trigger rotation
        for i in range(1000):
            self.log_manager.info(f"Test message {i}")
        
        # Check if backup log exists
        backup_exists = any(
            f.startswith(os.path.basename(self.log_file))
            and f.endswith('.1')
            for f in os.listdir(self.test_dir)
        )
        self.assertTrue(backup_exists)

    def test_log_formatting(self):
        """Test log message formatting"""
        test_message = "Test format message"
        self.log_manager.info(test_message)
        
        with open(self.log_file, 'r') as f:
            content = f.read()
            # Verify timestamp format
            self.assertRegex(content, r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}')
            # Verify log level
            self.assertIn("INFO", content)
            # Verify message
            self.assertIn(test_message, content)

    def test_exception_logging(self):
        """Test exception logging"""
        try:
            raise ValueError("Test exception")
        except ValueError as e:
            self.log_manager.exception("An error occurred")
        
        with open(self.log_file, 'r') as f:
            content = f.read()
            self.assertIn("An error occurred", content)
            self.assertIn("ValueError: Test exception", content)
            self.assertIn("Traceback", content)

    def test_log_filters(self):
        """Test log filtering"""
        # Set up filter for specific module
        self.log_manager.add_filter("test_module")
        
        # Log messages from different modules
        self.log_manager.info("General message")
        self.log_manager._log("test_module", "Filtered message")
        
        with open(self.log_file, 'r') as f:
            content = f.read()
            self.assertNotIn("General message", content)
            self.assertIn("Filtered message", content)

if __name__ == '__main__':
    unittest.main()