"""
Enhanced Core Logic Tests for File Splitter

This module provides comprehensive testing for the migrated file splitter
core logic with file_utilities_2 integration, including hub connectivity,
configuration management, and enhanced error handling.
"""

import unittest
import os
import json
import hashlib
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
from PyQt5.QtCore import QCoreApplication

from file_utilities_2.core.file_splitter_logic import (
    FileSplitterLogic, FileSplitterWorkerThread,
    FileSplitterError, FileSplitterValidationError, FileSplitterIOError
)
from file_utilities_2.core.file_splitter_config import FileSplitterConfig
from file_utilities_2.core.file_splitter_logging import get_file_splitter_logger


class TestFileSplitterLogic(unittest.TestCase):
    """Enhanced test suite for FileSplitterLogic with file_utilities_2 integration."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_dir = tempfile.mkdtemp()
        
        # Create test configuration
        self.config = FileSplitterConfig()
        self.logger = get_file_splitter_logger()
        self.logic = FileSplitterLogic(self.config, self.logger)
        
        # Create test files
        self.test_file = os.path.join(self.test_dir, "test_file.dat")
        self.file_size = 1024 * 1024 * 2  # 2MB test file
        with open(self.test_file, 'wb') as f:
            f.write(os.urandom(self.file_size))
        
        # Calculate original file hash for integrity verification
        with open(self.test_file, 'rb') as f:
            self.original_hash = hashlib.sha256(f.read()).hexdigest()
        
        # Mock hub connector
        self.hub_connector_mock = Mock()
        self.logic.set_hub_connector(self.hub_connector_mock)
    
    def tearDown(self):
        """Clean up test fixtures after each test method."""
        shutil.rmtree(self.test_dir)
    
    def test_initialization_with_config_and_logger(self):
        """Test initialization with custom config and logger."""
        custom_config = FileSplitterConfig()
        custom_logger = get_file_splitter_logger("test_logger")
        
        logic = FileSplitterLogic(custom_config, custom_logger)
        
        self.assertEqual(logic.config, custom_config)
        self.assertEqual(logic.logger, custom_logger)
        self.assertIsNotNone(logic.operation_stats)
        self.assertFalse(logic._is_running)
    
    def test_hub_connector_integration(self):
        """Test hub connector integration."""
        # Test setting hub connector
        mock_connector = Mock()
        self.logic.set_hub_connector(mock_connector)
        
        self.assertEqual(self.logic.hub_connector, mock_connector)
    
    def test_calculate_split_params_by_size(self):
        """Test _calculate_split_params with split by size mode."""
        # Test normal case
        chunk_size, num_chunks = self.logic._calculate_split_params(
            1000, 'size', 100, 1
        )
        self.assertEqual(chunk_size, 100)
        self.assertEqual(num_chunks, 10)
        
        # Test edge case - chunk size larger than file
        chunk_size, num_chunks = self.logic._calculate_split_params(
            1000, 'size', 2000, 1
        )
        self.assertEqual(chunk_size, 1000)
        self.assertEqual(num_chunks, 1)
        
        # Test zero file size
        chunk_size, num_chunks = self.logic._calculate_split_params(
            0, 'size', 100, 1
        )
        self.assertEqual(chunk_size, 0)
        self.assertEqual(num_chunks, 0)
    
    def test_calculate_split_params_by_parts(self):
        """Test _calculate_split_params with split by parts mode."""
        # Test normal case
        chunk_size, num_chunks = self.logic._calculate_split_params(
            1000, 'parts', 5, 1
        )
        self.assertEqual(chunk_size, 200)
        self.assertEqual(num_chunks, 5)
        
        # Test edge case - single part
        chunk_size, num_chunks = self.logic._calculate_split_params(
            1000, 'parts', 1, 1
        )
        self.assertEqual(chunk_size, 1000)
        self.assertEqual(num_chunks, 1)
    
    def test_calculate_split_params_invalid_inputs(self):
        """Test _calculate_split_params with invalid inputs."""
        # Test invalid split mode
        with self.assertRaises(FileSplitterValidationError):
            self.logic._calculate_split_params(1000, 'invalid', 10, 1)
        
        # Test negative chunk size
        with self.assertRaises(FileSplitterValidationError):
            self.logic._calculate_split_params(1000, 'size', -100, 1)
        
        # Test zero parts
        with self.assertRaises(FileSplitterValidationError):
            self.logic._calculate_split_params(1000, 'parts', 0, 1)
        
        # Test too many chunks
        with self.assertRaises(FileSplitterValidationError):
            self.logic._calculate_split_params(1000, 'parts', 10000, 1)
    
    def test_split_file_by_size_with_hub_reporting(self):
        """Test splitting a file by fixed chunk size with hub reporting."""
        output_dir = os.path.join(self.test_dir, "split_output")
        os.makedirs(output_dir)
        
        # Set up signal capture
        complete_messages = []
        error_messages = []
        progress_updates = []
        
        def capture_complete(message):
            complete_messages.append(message)
        
        def capture_error(message):
            error_messages.append(message)
        
        def capture_progress(current, total, message):
            progress_updates.append((current, total, message))
        
        self.logic.operation_complete.connect(capture_complete)
        self.logic.error_occurred.connect(capture_error)
        self.logic.progress_updated.connect(capture_progress)
        
        # Split file into 500KB chunks
        chunk_size = 500 * 1024  # 500KB
        self.logic.split_file(
            self.test_file, output_dir, 'size', chunk_size, 1
        )
        
        # Verify operation completed successfully
        self.assertEqual(len(complete_messages), 1)
        self.assertEqual(len(error_messages), 0)
        self.assertGreater(len(progress_updates), 0)
        
        # Verify hub reporting was called
        self.hub_connector_mock.report_status_to_hub.assert_called()
        
        # Verify chunks were created
        chunk_files = [f for f in os.listdir(output_dir)
                       if f.startswith('test_file.dat.part')]
        self.assertGreaterEqual(len(chunk_files), 4)
        self.assertLessEqual(len(chunk_files), 5)
        
        # Verify metadata file was created
        metadata_file = os.path.join(output_dir, '_metadata.json')
        self.assertTrue(os.path.exists(metadata_file))
        
        # Verify enhanced metadata content
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        self.assertEqual(metadata['original_filename'], 'test_file.dat')
        self.assertEqual(metadata['total_size'], self.file_size)
        self.assertEqual(metadata['num_chunks'], len(chunk_files))
        self.assertIn('created_timestamp', metadata)
        self.assertIn('splitter_version', metadata)
    
    def test_split_file_by_parts_with_config(self):
        """Test splitting a file into specified number of parts with config."""
        output_dir = os.path.join(self.test_dir, "split_parts")
        os.makedirs(output_dir)
        
        # Update config for testing
        self.config.set('verify_integrity', True)
        self.config.set('create_metadata_file', True)
        
        complete_messages = []
        
        def capture_complete(message):
            complete_messages.append(message)
        
        self.logic.operation_complete.connect(capture_complete)
        
        # Split into 3 parts
        self.logic.split_file(self.test_file, output_dir, 'parts', 3, 1)
        
        # Verify operation completed
        self.assertEqual(len(complete_messages), 1)
        
        # Verify 3 chunks were created
        chunk_files = [f for f in os.listdir(output_dir)
                       if f.startswith('test_file.dat.part')]
        self.assertEqual(len(chunk_files), 3)
    
    def test_join_files_with_metadata_and_hub_reporting(self):
        """Test joining files using metadata file with hub reporting."""
        # First split a file
        split_dir = os.path.join(self.test_dir, "join_test")
        os.makedirs(split_dir)
        
        self.logic.split_file(self.test_file, split_dir, 'size', 500*1024, 1)
        
        # Now join the files
        first_chunk = os.path.join(split_dir, 'test_file.dat.part001')
        output_file = os.path.join(self.test_dir, "joined_file.dat")
        
        complete_messages = []
        
        def capture_complete(message):
            complete_messages.append(message)
        
        self.logic.operation_complete.connect(capture_complete)
        
        # Reset hub connector mock for join operation
        self.hub_connector_mock.reset_mock()
        
        self.logic.join_files(first_chunk, output_file)
        
        # Verify operation completed
        self.assertEqual(len(complete_messages), 1)
        self.assertTrue(os.path.exists(output_file))
        
        # Verify hub reporting was called for join operation
        self.hub_connector_mock.report_status_to_hub.assert_called()
        
        # Verify file integrity
        with open(output_file, 'rb') as f:
            joined_hash = hashlib.sha256(f.read()).hexdigest()
        self.assertEqual(joined_hash, self.original_hash)
    
    def test_error_handling_with_hub_reporting(self):
        """Test error handling with hub reporting."""
        error_messages = []
        
        def capture_error(message):
            error_messages.append(message)
        
        self.logic.error_occurred.connect(capture_error)
        
        # Try to split non-existent file
        self.logic.split_file("nonexistent.dat", self.test_dir, 'size', 1024, 1)
        
        # Should emit error
        self.assertGreater(len(error_messages), 0)
        self.assertIn("not found", error_messages[0].lower())
        
        # Verify hub error reporting was called
        self.hub_connector_mock.report_error_to_hub.assert_called()
    
    def test_stop_operation_with_hub_reporting(self):
        """Test stopping an operation with hub reporting."""
        self.assertFalse(self.logic._is_running)
        
        # Start operation state
        self.logic._is_running = True
        
        # Stop operation
        self.logic.stop()
        
        self.assertFalse(self.logic._is_running)
        
        # Verify hub reporting was called
        self.hub_connector_mock.report_status_to_hub.assert_called_with(
            "stopped", {"stop_time": unittest.mock.ANY}
        )
    
    def test_operation_stats_tracking(self):
        """Test operation statistics tracking."""
        # Initial stats
        self.assertIsInstance(self.logic.operation_stats, dict)
        self.assertEqual(self.logic.operation_stats['bytes_processed'], 0)
        self.assertEqual(self.logic.operation_stats['chunks_processed'], 0)
        self.assertEqual(self.logic.operation_stats['errors_count'], 0)
        
        # Perform operation and check stats update
        output_dir = os.path.join(self.test_dir, "stats_test")
        os.makedirs(output_dir)
        
        self.logic.split_file(self.test_file, output_dir, 'parts', 2, 1)
        
        # Stats should be updated
        self.assertGreater(self.logic.operation_stats['bytes_processed'], 0)
        self.assertGreater(self.logic.operation_stats['chunks_processed'], 0)
        self.assertIsNotNone(self.logic.operation_stats['start_time'])
        self.assertIsNotNone(self.logic.operation_stats['end_time'])


class TestFileSplitterWorkerThread(unittest.TestCase):
    """Test suite for FileSplitterWorkerThread."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.config = FileSplitterConfig()
        self.logger = get_file_splitter_logger()
        self.logic = FileSplitterLogic(self.config, self.logger)
        
        # Create test file
        self.test_file = os.path.join(self.test_dir, "thread_test.dat")
        with open(self.test_file, 'wb') as f:
            f.write(os.urandom(1024))  # 1KB test file
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)
    
    def test_worker_thread_initialization(self):
        """Test worker thread initialization."""
        thread = FileSplitterWorkerThread(
            self.logic, 'split', 
            self.test_file, self.test_dir, 'size', 512, 1
        )
        
        self.assertEqual(thread.operation_logic, self.logic)
        self.assertEqual(thread.operation_type, 'split')
        self.assertEqual(len(thread.args), 5)
    
    def test_worker_thread_split_operation(self):
        """Test worker thread split operation."""
        output_dir = os.path.join(self.test_dir, "thread_split")
        os.makedirs(output_dir)
        
        thread = FileSplitterWorkerThread(
            self.logic, 'split',
            self.test_file, output_dir, 'size', 512, 1
        )
        
        # Mock the split_file method to avoid actual operation
        with patch.object(self.logic, 'split_file') as mock_split:
            thread.run()
            mock_split.assert_called_once_with(
                self.test_file, output_dir, 'size', 512, 1
            )


class TestFileSplitterIntegration(unittest.TestCase):
    """Integration tests for file splitter with file_utilities_2 components."""
    
    def setUp(self):
        """Set up integration test environment."""
        self.test_dir = tempfile.mkdtemp()
        
        # Create test file with known content
        test_string = b"This is a test file for integration testing."
        self.test_content = test_string * 1000
        self.test_file = os.path.join(self.test_dir, "integration_test.txt")
        with open(self.test_file, 'wb') as f:
            f.write(self.test_content)
    
    def tearDown(self):
        """Clean up integration test environment."""
        shutil.rmtree(self.test_dir)
    
    def test_full_split_join_cycle_with_file_utilities_2(self):
        """Test complete split and join cycle with file_utilities_2 integration."""
        # Initialize with file_utilities_2 components
        config = FileSplitterConfig()
        logger = get_file_splitter_logger()
        logic = FileSplitterLogic(config, logger)
        
        # Mock hub connector
        hub_connector = Mock()
        logic.set_hub_connector(hub_connector)
        
        # Split the file
        split_dir = os.path.join(self.test_dir, "integration_split")
        os.makedirs(split_dir)
        
        complete_messages = []
        
        def capture_complete(message):
            complete_messages.append(message)
        
        logic.operation_complete.connect(capture_complete)
        
        # Split into 5 parts
        logic.split_file(self.test_file, split_dir, 'parts', 5, 1)
        
        # Verify split completed
        self.assertEqual(len(complete_messages), 1)
        self.assertIn("successfully split", complete_messages[0].lower())
        
        # Verify hub integration was used
        hub_connector.report_status_to_hub.assert_called()
        
        # Join the files
        first_chunk = os.path.join(split_dir, 'integration_test.txt.part001')
        joined_file = os.path.join(self.test_dir, "integration_joined.txt")
        
        complete_messages.clear()
        hub_connector.reset_mock()
        
        logic.join_files(first_chunk, joined_file)
        
        # Verify join completed
        self.assertEqual(len(complete_messages), 1)
        self.assertIn("successfully joined", complete_messages[0].lower())
        
        # Verify hub integration was used for join
        hub_connector.report_status_to_hub.assert_called()
        
        # Verify content integrity
        with open(joined_file, 'rb') as f:
            joined_content = f.read()
        
        self.assertEqual(joined_content, self.test_content)
        self.assertEqual(len(joined_content), len(self.test_content))
    
    def test_configuration_integration(self):
        """Test configuration integration with file splitter logic."""
        config = FileSplitterConfig()
        
        # Test configuration settings
        config.set('default_chunk_size', 2048)
        config.set('verify_integrity', True)
        config.set('enable_hub_reporting', True)
        
        logic = FileSplitterLogic(config)
        
        # Verify configuration is used
        self.assertEqual(logic.config.get('default_chunk_size'), 2048)
        self.assertTrue(logic.config.is_integrity_verification_enabled())
        self.assertTrue(logic.config.is_hub_reporting_enabled())
    
    def test_logging_integration(self):
        """Test logging integration with file splitter logic."""
        logger = get_file_splitter_logger("integration_test")
        config = FileSplitterConfig()
        logic = FileSplitterLogic(config, logger)
        
        # Verify logger is set
        self.assertEqual(logic.logger, logger)
        
        # Test logging functionality
        with patch.object(logger, 'info') as mock_info:
            logic.logger.info("Test log message")
            mock_info.assert_called_once_with("Test log message")


if __name__ == '__main__':
    # Initialize QApplication for Qt signal testing
    app = QCoreApplication([])
    unittest.main()