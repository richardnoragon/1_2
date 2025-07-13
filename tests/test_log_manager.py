import unittest
import os
import logging
from tests.test_utils import TestUtils
from log_manager import LogManager

from core.error_handler import error_handler


class TestLogManager(unittest.TestCase):
    """A class that handles test log manager."""
    def setUp(self):
        """setup."""
        self.test_dir = TestUtils.create_temp_dir()
        self.log_file = os.path.join(self.test_dir, "test.log")
        self.log_manager = LogManager(self.log_file)

    def tearDown(self):
        """teardown."""
        TestUtils.cleanup_temp_dir(self.test_dir)
        # Reset logging configuration
        logging.getLogger().handlers = []

    def test_log_initialization(self):
        """Test log manager initialization"""
        # Verify log file creation
        self.assertTrue(os.path.exists(self.log_file))
        
        # Verify logger configuration
        logger = logging.getLogger('RFU')
        self.assertTrue(logger.handlers)
        self.assertEqual(logger.level, logging.INFO)

    def test_log_levels(self):
        """Test different logging levels"""
        test_messages = {
            'debug': "Debug message",
            'info': "Info message",
            'warning': "Warning message",
            'error': "Error message",
            'critical': "Critical message"
        }
        
        # Log messages at different levels
        for level, message in test_messages.items():
            getattr(self.log_manager, level)(message)
        
        # Read log file
        with open(self.log_file, 'r') as f:
            log_content = f.read()
        
        # Verify all messages were logged
        for message in test_messages.values():
            self.assertIn(message, log_content)

    def test_log_rotation(self):
        """Test log file rotation"""
        # Configure small max size to trigger rotation
        self.log_manager.configure(max_size=100, backup_count=3)
        
        # Write enough logs to trigger rotation
        for i in range(10):
            self.log_manager.info(f"Test message {i}" * 5)
        
        # Verify rotation files exist
        base_name = os.path.splitext(self.log_file)[0]
        for i in range(1, 4):
            rotation_file = f"{base_name}.{i}.log"
            self.assertTrue(
                os.path.exists(rotation_file),
                f"Rotation file {rotation_file} not found"
            )

    def test_log_formatting(self):
        """Test log message formatting"""
        test_message = "Test log message"
        self.log_manager.info(test_message)
        
        with open(self.log_file, 'r') as f:
            log_line = f.read().strip()
        
        # Verify log format includes timestamp, level, and message
        self.assertRegex(
            log_line,
            r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} - INFO - Test log message'
        )

    def test_context_capture(self):
        """Test capturing of context information"""
        # Set up context
        self.log_manager.set_context(module='test_module', function='test_func')
        
        # Log with context
        test_message = "Test with context"
        self.log_manager.info(test_message)
        
        with open(self.log_file, 'r') as f:
            log_line = f.read().strip()
        
        # Verify context is included
        self.assertIn('test_module', log_line)
        self.assertIn('test_func', log_line)

    def test_error_logging_with_exception(self):
        """Test logging errors with exception information"""
        try:
            raise ValueError("Test exception")
        except ValueError as e:
            self.log_manager.error("An error occurred", exc_info=e)
        
        with open(self.log_file, 'r') as f:
            log_content = f.read()
        
        # Verify exception details are logged
        self.assertIn("Test exception", log_content)
        self.assertIn("Traceback", log_content)
        self.assertIn("ValueError", log_content)

    def test_log_filtering(self):
        """Test log message filtering"""
        # Set minimum level to WARNING
        self.log_manager.set_level(logging.WARNING)
        
        # Log messages at different levels
        self.log_manager.debug("Debug message")
        self.log_manager.info("Info message")
        self.log_manager.warning("Warning message")
        self.log_manager.error("Error message")
        
        with open(self.log_file, 'r') as f:
            log_content = f.read()
        
        # Verify only WARNING and above are logged
        self.assertNotIn("Debug message", log_content)
        self.assertNotIn("Info message", log_content)
        self.assertIn("Warning message", log_content)
        self.assertIn("Error message", log_content)

    def test_log_handlers(self):
        """Test adding custom log handlers"""
        # Create a memory handler for testing
        from io import StringIO
        string_io = StringIO()
        memory_handler = logging.StreamHandler(string_io)
        
        # Add handler
        self.log_manager.add_handler(memory_handler)
        
        # Log a message
        test_message = "Test memory handler"
        self.log_manager.info(test_message)
        
        # Verify message in both handlers
        self.assertIn(test_message, string_io.getvalue())
        with open(self.log_file, 'r') as f:
            self.assertIn(test_message, f.read())

    def test_log_cleanup(self):
        """Test log file cleanup functionality"""
        # Create some old log files
        base_name = os.path.splitext(self.log_file)[0]
        old_logs = []
        for i in range(5):
            old_log = f"{base_name}.old{i}.log"
            with open(old_log, 'w') as f:
                f.write(f"Old log {i}")
            old_logs.append(old_log)
        
        # Clean up logs older than 0 days (all of them)
        self.log_manager.cleanup_old_logs(max_age_days=0)
        
        # Verify old logs are removed
        for old_log in old_logs:
            self.assertFalse(
                os.path.exists(old_log),
                f"Old log {old_log} was not cleaned up"
            )

if __name__ == '__main__':
    unittest.main()