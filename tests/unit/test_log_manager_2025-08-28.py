"""
Comprehensive unit tests for log_manager.py

Test file following naming convention: test_log_manager_2025-08-28.py
Generated on: 2025-08-28

This module provides comprehensive testing for the LogManager class and its methods.
"""

import json
import logging
import os
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

# Add the src directory to the path to import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.log_manager import (LogManager, get_log_manager,
                             get_log_manager_instance)


class TestLogManager:
    """Test class for LogManager functionality."""
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Setup and teardown for each test."""
        # Setup: Create temporary directory for testing
        self.temp_dir = Path(tempfile.mkdtemp())
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        # Reset singleton instance before each test
        LogManager._instance = None
        
        yield
        
        # Teardown: Clean up temporary directory and reset working directory
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
        # Reset singleton instance after each test
        LogManager._instance = None
    
    def test_singleton_pattern(self):
        """Test that LogManager implements singleton pattern correctly."""
        # Create two instances
        manager1 = LogManager()
        manager2 = LogManager()
        
        # Assert they are the same instance
        assert manager1 is manager2
        assert id(manager1) == id(manager2)
    
    def test_initialization(self):
        """Test LogManager initialization."""
        manager = LogManager()
        
        # Check that log directory is created
        assert manager.log_dir.exists()
        assert manager.log_dir.name == 'logs'
        
        # Check main log file path
        assert manager.main_log_file == manager.log_dir / 'rfu.log'
        
        # Check root logger configuration
        assert manager.root_logger.name == 'RFU'
        assert manager.root_logger.level == logging.DEBUG
        
        # Check formatters
        assert manager.detailed_formatter is not None
        assert manager.simple_formatter is not None
        
        # Check handlers are set up
        assert len(manager.root_logger.handlers) >= 1
        
        # Check initialization flag
        assert manager._initialized is True
    
    def test_setup_file_handler_success(self):
        """Test successful file handler setup."""
        manager = LogManager()
        
        # Check file handler exists
        assert hasattr(manager, 'file_handler')
        
        # Check log file is created
        assert manager.main_log_file.parent.exists()
        
        # Check handler configuration
        file_handlers = [h for h in manager.root_logger.handlers 
                        if isinstance(h, logging.handlers.RotatingFileHandler)]
        assert len(file_handlers) >= 1
        
        file_handler = file_handlers[0]
        assert file_handler.level == logging.DEBUG
        assert file_handler.maxBytes == 10*1024*1024  # 10MB
        assert file_handler.backupCount == 5
    
    @patch('logging.handlers.RotatingFileHandler')
    def test_setup_file_handler_failure(self, mock_handler):
        """Test file handler setup failure handling."""
        # Mock handler to raise exception
        mock_handler.side_effect = Exception("File access denied")
        
        manager = LogManager()
        
        # Should handle exception gracefully
        assert manager.file_handler is None
    
    def test_setup_console_handler_success(self):
        """Test successful console handler setup."""
        manager = LogManager()
        
        # Check console handler exists
        assert hasattr(manager, 'console_handler')
        
        # Check handler configuration
        console_handlers = [h for h in manager.root_logger.handlers 
                           if isinstance(h, logging.StreamHandler)]
        assert len(console_handlers) >= 1
        
        console_handler = console_handlers[0]
        assert console_handler.level == logging.INFO
        assert console_handler.stream == sys.stdout
    
    @patch('logging.StreamHandler')
    def test_setup_console_handler_failure(self, mock_handler):
        """Test console handler setup failure handling."""
        # Mock handler to raise exception
        mock_handler.side_effect = Exception("Console access denied")
        
        manager = LogManager()
        
        # Should handle exception gracefully
        assert manager.console_handler is None
    
    def test_get_logger_new(self):
        """Test getting a new logger instance."""
        manager = LogManager()
        
        logger = manager.get_logger('test_component')
        
        # Check logger properties
        assert logger.name == 'RFU.test_component'
        assert logger.level == logging.DEBUG
        assert 'RFU.test_component' in manager._loggers
        assert manager._loggers['RFU.test_component'] is logger
    
    def test_get_logger_existing(self):
        """Test getting an existing logger instance."""
        manager = LogManager()
        
        # Create logger first time
        logger1 = manager.get_logger('test_component')
        
        # Get same logger second time
        logger2 = manager.get_logger('test_component')
        
        # Should return same instance
        assert logger1 is logger2
    
    def test_get_logger_with_rfu_prefix(self):
        """Test getting logger with RFU prefix already included."""
        manager = LogManager()
        
        logger = manager.get_logger('RFU.test_component')
        
        # Should not double-prefix
        assert logger.name == 'RFU.test_component'
    
    def test_set_level_valid(self):
        """Test setting valid logging level."""
        manager = LogManager()
        
        # Test different valid levels
        test_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        
        for level_name in test_levels:
            manager.set_level(level_name)
            expected_level = getattr(logging, level_name)
            
            # Check root logger level
            assert manager.root_logger.level == expected_level
            
            # Check console handler level (if exists)
            if manager.console_handler:
                assert manager.console_handler.level == expected_level
    
    def test_set_level_invalid(self):
        """Test setting invalid logging level."""
        manager = LogManager()
        original_level = manager.root_logger.level
        
        # Try to set invalid level
        manager.set_level('INVALID_LEVEL')
        
        # Level should remain unchanged
        assert manager.root_logger.level == original_level
    
    def test_set_level_case_insensitive(self):
        """Test setting logging level with different cases."""
        manager = LogManager()
        
        # Test lowercase
        manager.set_level('info')
        assert manager.root_logger.level == logging.INFO
        
        # Test mixed case
        manager.set_level('Warning')
        assert manager.root_logger.level == logging.WARNING
    
    def test_set_console_level_valid(self):
        """Test setting valid console logging level."""
        manager = LogManager()
        
        if manager.console_handler:
            manager.set_console_level('ERROR')
            assert manager.console_handler.level == logging.ERROR
    
    def test_set_console_level_invalid(self):
        """Test setting invalid console logging level."""
        manager = LogManager()
        
        if manager.console_handler:
            original_level = manager.console_handler.level
            manager.set_console_level('INVALID_LEVEL')
            assert manager.console_handler.level == original_level
    
    def test_set_console_level_no_handler(self):
        """Test setting console level when no console handler exists."""
        manager = LogManager()
        manager.console_handler = None
        
        # Should not raise exception
        manager.set_console_level('ERROR')
    
    def test_add_file_handler_success(self):
        """Test successful addition of file handler."""
        manager = LogManager()
        
        result = manager.add_file_handler(
            name='test_handler',
            filename='test.log',
            level='WARNING'
        )
        
        # Check return value
        assert result is True
        
        # Check file is created
        test_log_file = manager.log_dir / 'test.log'
        assert test_log_file.parent.exists()
        
        # Check handler is added
        rotating_handlers = [h for h in manager.root_logger.handlers 
                            if isinstance(h, logging.handlers.RotatingFileHandler)]
        assert len(rotating_handlers) >= 2  # Original + new handler
    
    @patch('logging.handlers.RotatingFileHandler')
    def test_add_file_handler_failure(self, mock_handler):
        """Test file handler addition failure."""
        manager = LogManager()
        
        # Mock handler to raise exception
        mock_handler.side_effect = Exception("Cannot create file")
        
        result = manager.add_file_handler(
            name='test_handler',
            filename='test.log'
        )
        
        # Should return False on failure
        assert result is False
    
    def test_add_file_handler_default_level(self):
        """Test adding file handler with default level."""
        manager = LogManager()
        
        result = manager.add_file_handler(
            name='test_handler',
            filename='test.log'
        )
        
        assert result is True
    
    def test_log_structured_basic(self):
        """Test structured logging with basic parameters."""
        manager = LogManager()
        
        with patch.object(manager.root_logger, 'info') as mock_log:
            manager.log_structured(
                level='INFO',
                component='test_component',
                message='Test message'
            )
            
            # Should create logger and log message
            assert 'RFU.test_component' in manager._loggers
    
    def test_log_structured_with_kwargs(self):
        """Test structured logging with additional context."""
        manager = LogManager()
        
        # Create a mock logger to capture the log call
        mock_logger = Mock()
        manager._loggers['RFU.test_component'] = mock_logger
        
        with patch.object(manager, 'get_logger', return_value=mock_logger):
            manager.log_structured(
                level='INFO',
                component='test_component',
                message='Test message',
                user_id=123,
                action='test_action'
            )
            
            # Check that log was called with structured message
            mock_logger.log.assert_called_once()
            args, kwargs = mock_logger.log.call_args
            level, message = args
            
            assert level == logging.INFO
            assert 'Test message' in message
            assert 'user_id=123' in message
            assert 'action=test_action' in message
    
    def test_log_structured_invalid_level(self):
        """Test structured logging with invalid level."""
        manager = LogManager()
        
        mock_logger = Mock()
        with patch.object(manager, 'get_logger', return_value=mock_logger):
            manager.log_structured(
                level='INVALID_LEVEL',
                component='test_component',
                message='Test message'
            )
            
            # Should default to INFO level
            mock_logger.log.assert_called_once()
            args, kwargs = mock_logger.log.call_args
            level = args[0]
            assert level == logging.INFO
    
    def test_get_log_stats(self):
        """Test getting logging statistics."""
        manager = LogManager()
        
        # Create some loggers
        manager.get_logger('component1')
        manager.get_logger('component2')
        
        stats = manager.get_log_stats()
        
        # Check required fields
        assert 'log_directory' in stats
        assert 'main_log_file' in stats
        assert 'active_loggers' in stats
        assert 'logger_names' in stats
        assert 'root_level' in stats
        assert 'handlers' in stats
        
        # Check values
        assert stats['log_directory'] == str(manager.log_dir)
        assert stats['main_log_file'] == str(manager.main_log_file)
        assert stats['active_loggers'] == 2
        assert 'RFU.component1' in stats['logger_names']
        assert 'RFU.component2' in stats['logger_names']
        assert stats['root_level'] == 'DEBUG'
        assert stats['handlers'] >= 1
    
    def test_get_log_stats_with_existing_file(self):
        """Test getting statistics when log file exists."""
        manager = LogManager()
        
        # Create log file with some content
        manager.main_log_file.write_text('Test log content')
        
        stats = manager.get_log_stats()
        
        # Should include file size
        assert 'main_log_size_bytes' in stats
        assert stats['main_log_size_bytes'] > 0
    
    def test_cleanup_success(self):
        """Test successful cleanup of logging resources."""
        manager = LogManager()
        
        # Create some loggers and handlers
        logger1 = manager.get_logger('component1')
        logger2 = manager.get_logger('component2')
        
        # Get initial handler count
        initial_handlers = len(manager.root_logger.handlers)
        
        # Perform cleanup
        manager.cleanup()
        
        # Check handlers are removed
        assert len(manager.root_logger.handlers) == 0
        
        # Check loggers are cleared
        assert len(manager._loggers) == 0
    
    @patch('logging.Handler.close')
    def test_cleanup_with_handler_error(self, mock_close):
        """Test cleanup when handler close fails."""
        manager = LogManager()
        
        # Mock close to raise exception
        mock_close.side_effect = Exception("Close failed")
        
        # Should handle exception gracefully
        manager.cleanup()
        
        # Loggers should still be cleared
        assert len(manager._loggers) == 0


class TestGlobalFunctions:
    """Test class for global utility functions."""
    
    def setup_method(self):
        """Setup for each test method."""
        # Reset global instance
        import src.log_manager
        rfu.log_manager._log_manager = None
        LogManager._instance = None
    
    def teardown_method(self):
        """Teardown for each test method."""
        # Reset global instance
        import src.log_manager
        rfu.log_manager._log_manager = None
        LogManager._instance = None
    
    def test_get_log_manager_first_call(self):
        """Test first call to get_log_manager creates instance."""
        manager = get_log_manager()
        
        assert manager is not None
        assert isinstance(manager, LogManager)
    
    def test_get_log_manager_subsequent_calls(self):
        """Test subsequent calls return same instance."""
        manager1 = get_log_manager()
        manager2 = get_log_manager()
        
        assert manager1 is manager2
    
    def test_get_log_manager_instance_backward_compatibility(self):
        """Test backward compatibility function."""
        manager1 = get_log_manager()
        manager2 = get_log_manager_instance()
        
        assert manager1 is manager2


class TestLogManagerIntegration:
    """Integration tests for LogManager."""
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Setup and teardown for integration tests."""
        # Setup: Create temporary directory
        self.temp_dir = Path(tempfile.mkdtemp())
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        # Reset singleton
        LogManager._instance = None
        
        yield
        
        # Teardown
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        LogManager._instance = None
    
    def test_end_to_end_logging_workflow(self):
        """Test complete logging workflow."""
        # Initialize manager
        manager = LogManager()
        
        # Get logger and log messages
        logger = manager.get_logger('integration_test')
        logger.info('Test info message')
        logger.warning('Test warning message')
        logger.error('Test error message')
        
        # Add custom file handler
        success = manager.add_file_handler(
            name='custom_handler',
            filename='custom.log',
            level='WARNING'
        )
        assert success
        
        # Log structured message
        manager.log_structured(
            level='INFO',
            component='integration_test',
            message='Structured test message',
            test_id=1,
            operation='end_to_end_test'
        )
        
        # Change logging levels
        manager.set_level('WARNING')
        manager.set_console_level('ERROR')
        
        # Get statistics
        stats = manager.get_log_stats()
        assert stats['active_loggers'] >= 1
        assert 'RFU.integration_test' in stats['logger_names']
        
        # Cleanup
        manager.cleanup()
        assert len(manager._loggers) == 0
    
    def test_concurrent_logger_access(self):
        """Test concurrent access to loggers (simulated)."""
        manager = LogManager()
        
        # Simulate multiple components getting loggers
        loggers = []
        for i in range(10):
            logger = manager.get_logger(f'component_{i}')
            loggers.append(logger)
            logger.info(f'Message from component {i}')
        
        # Check all loggers are created
        assert len(manager._loggers) == 10
        
        # Check all loggers are unique
        logger_names = [logger.name for logger in loggers]
        assert len(set(logger_names)) == 10
    
    def test_logging_with_file_rotation(self):
        """Test logging behavior with file rotation scenario."""
        manager = LogManager()
        logger = manager.get_logger('rotation_test')
        
        # Generate multiple log messages
        for i in range(100):
            logger.info(f'Log message {i} - This is a test message to generate log content')
        
        # Check log file exists
        assert manager.main_log_file.exists()
        
        # Check stats include file size
        stats = manager.get_log_stats()
        assert 'main_log_size_bytes' in stats
        assert stats['main_log_size_bytes'] > 0


class TestLogManagerErrorHandling:
    """Test class for error handling scenarios."""
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Setup and teardown for error handling tests."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        LogManager._instance = None
        
        yield
        
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        LogManager._instance = None
    
    @patch('pathlib.Path.mkdir')
    def test_log_directory_creation_failure(self, mock_mkdir):
        """Test handling of log directory creation failure."""
        # Mock mkdir to raise exception
        mock_mkdir.side_effect = PermissionError("Permission denied")
        
        # Should handle gracefully
        manager = LogManager()
        assert manager is not None
    
    def test_invalid_log_level_handling(self):
        """Test handling of various invalid log levels."""
        manager = LogManager()
        original_level = manager.root_logger.level
        
        invalid_levels = ['', None, 123, 'INVALID', 'debug_invalid']
        
        for invalid_level in invalid_levels:
            try:
                manager.set_level(str(invalid_level))
                # Level should remain unchanged
                assert manager.root_logger.level == original_level
            except Exception:
                # Should not raise exceptions for invalid levels
                pytest.fail(f"Unexpected exception for level: {invalid_level}")
    
    def test_structured_logging_with_complex_kwargs(self):
        """Test structured logging with complex keyword arguments."""
        manager = LogManager()
        
        complex_kwargs = {
            'nested_dict': {'key': 'value', 'number': 42},
            'list_data': [1, 2, 3],
            'none_value': None,
            'boolean': True,
            'unicode': 'Testing unicode: üñíçødé'
        }
        
        # Should handle complex data without errors
        try:
            manager.log_structured(
                level='INFO',
                component='error_test',
                message='Complex data test',
                **complex_kwargs
            )
        except Exception as e:
            pytest.fail(f"Structured logging failed with complex kwargs: {e}")


# Test execution metadata
TEST_EXECUTION_TIMESTAMP = datetime.now().isoformat()
TEST_MODULE_NAME = "test_log_manager_2025-08-28"
TEST_TARGET_MODULE = "log_manager"

if __name__ == "__main__":
    print(f"Test execution started at: {TEST_EXECUTION_TIMESTAMP}")
    print(f"Testing module: {TEST_TARGET_MODULE}")
    print(f"Test file: {TEST_MODULE_NAME}")