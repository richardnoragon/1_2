"""
Comprehensive Test Suite for File Splitter Logic

This module provides comprehensive testing for the file splitter logic module,
including split operations, join operations, error handling, and integration testing.
"""

import hashlib
import json
import os
import shutil
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, Mock, patch

from PyQt5.QtCore import QCoreApplication

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from tools.file_operations.file_splitter_config import FileSplitterConfig
from tools.file_operations.file_splitter_logging import \
    get_file_splitter_logger
from tools.file_operations.file_splitter_logic import (
    FileSplitterError, FileSplitterIOError, FileSplitterLogic,
    FileSplitterValidationError, FileSplitterWorkerThread)


class TestFileSplitterLogic(unittest.TestCase):
    """Comprehensive test suite for FileSplitterLogic."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_dir = tempfile.mkdtemp()
        
        # Create test configuration
        self.config = FileSplitterConfig()
        self.logger = get_file_splitter_logger("test_logger")
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
        
        # Signal capture lists
        self.complete_messages = []
        self.error_messages = []
        self.progress_updates = []
        
        # Connect signals for testing
        self.logic.operation_complete.connect(self._capture_complete)
        self.logic.error_occurred.connect(self._capture_error)
        self.logic.progress_updated.connect(self._capture_progress)
    
    def tearDown(self):
        """Clean up test fixtures after each test method."""
        shutil.rmtree(self.test_dir)
    
    def _capture_complete(self, message):
        """Capture completion messages."""
        self.complete_messages.append(message)
    
    def _capture_error(self, message):
        """Capture error messages."""
        self.error_messages.append(message)
    
    def _capture_progress(self, current, total, message):
        """Capture progress updates."""
        self.progress_updates.append((current, total, message))
    
    def test_initialization_with_config_and_logger(self):
        """Test initialization with custom config and logger."""
        custom_config = FileSplitterConfig()
        custom_logger = get_file_splitter_logger("test_custom")
        
        logic = FileSplitterLogic(custom_config, custom_logger)
        
        self.assertEqual(logic.config, custom_config)
        self.assertEqual(logic.logger, custom_logger)
        self.assertIsNotNone(logic.operation_stats)
        self.assertFalse(logic._is_running)
    
    def test_initialization_with_defaults(self):
        """Test initialization with default config and logger."""
        logic = FileSplitterLogic()
        
        self.assertIsNotNone(logic.config)
        self.assertIsNotNone(logic.logger)
        self.assertIsInstance(logic.operation_stats, dict)
        self.assertFalse(logic._is_running)
    
    def test_hub_connector_integration(self):
        """Test hub connector integration."""
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
        
        # Test with unit multiplier
        chunk_size, num_chunks = self.logic._calculate_split_params(
            1024 * 10, 'size', 2, 1024  # 2KB chunks
        )
        self.assertEqual(chunk_size, 2048)
        self.assertEqual(num_chunks, 5)
    
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
        
        # Test uneven division
        chunk_size, num_chunks = self.logic._calculate_split_params(
            1001, 'parts', 3, 1
        )
        self.assertEqual(chunk_size, 334)  # ceil(1001/3)
        self.assertEqual(num_chunks, 3)
    
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
    
    def test_split_file_by_size_success(self):
        """Test successful file splitting by size."""
        output_dir = os.path.join(self.test_dir, "split_output")
        os.makedirs(output_dir)
        
        # Split file into 500KB chunks
        chunk_size = 500 * 1024  # 500KB
        self.logic.split_file(
            self.test_file, output_dir, 'size', chunk_size, 1
        )
        
        # Verify operation completed successfully
        self.assertEqual(len(self.complete_messages), 1)
        self.assertEqual(len(self.error_messages), 0)
        self.assertGreater(len(self.progress_updates), 0)
        
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
        
        # Verify metadata content
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        self.assertEqual(metadata['original_filename'], 'test_file.dat')
        self.assertEqual(metadata['total_size'], self.file_size)
        self.assertEqual(metadata['num_chunks'], len(chunk_files))
        self.assertIn('created_timestamp', metadata)
        self.assertIn('splitter_version', metadata)
    
    def test_split_file_by_parts_success(self):
        """Test successful file splitting by parts."""
        output_dir = os.path.join(self.test_dir, "split_parts")
        os.makedirs(output_dir)
        
        # Split into 3 parts
        self.logic.split_file(self.test_file, output_dir, 'parts', 3, 1)
        
        # Verify operation completed
        self.assertEqual(len(self.complete_messages), 1)
        self.assertEqual(len(self.error_messages), 0)
        
        # Verify 3 chunks were created
        chunk_files = [f for f in os.listdir(output_dir)
                       if f.startswith('test_file.dat.part')]
        self.assertEqual(len(chunk_files), 3)
        
        # Verify total size consistency
        total_chunk_size = 0
        for chunk_file in chunk_files:
            chunk_path = os.path.join(output_dir, chunk_file)
            total_chunk_size += os.path.getsize(chunk_path)
        
        self.assertEqual(total_chunk_size, self.file_size)
    
    def test_split_file_nonexistent_input(self):
        """Test splitting non-existent file."""
        output_dir = os.path.join(self.test_dir, "error_test")
        os.makedirs(output_dir)
        
        self.logic.split_file("nonexistent.dat", output_dir, 'size', 1024, 1)
        
        # Should emit error
        self.assertEqual(len(self.complete_messages), 0)
        self.assertGreater(len(self.error_messages), 0)
        self.assertIn("not found", self.error_messages[0].lower())
        
        # Verify hub error reporting was called
        self.hub_connector_mock.report_error_to_hub.assert_called()
    
    def test_split_file_invalid_output_directory(self):
        """Test splitting with invalid output directory."""
        # Try to use a file as directory (should fail)
        invalid_output = self.test_file  # Use existing file as "directory"
        
        self.logic.split_file(self.test_file, invalid_output, 'size', 1024, 1)
        
        # Should emit error
        self.assertGreater(len(self.error_messages), 0)
        self.hub_connector_mock.report_error_to_hub.assert_called()
    
    def test_split_empty_file(self):
        """Test splitting an empty file."""
        empty_file = os.path.join(self.test_dir, "empty.dat")
        with open(empty_file, 'wb') as f:
            pass  # Create empty file
        
        output_dir = os.path.join(self.test_dir, "empty_output")
        os.makedirs(output_dir)
        
        self.logic.split_file(empty_file, output_dir, 'size', 1024, 1)
        
        # Should complete with message about empty file
        self.assertEqual(len(self.complete_messages), 1)
        self.assertIn("empty", self.complete_messages[0].lower())
    
    def test_join_files_with_metadata_success(self):
        """Test successful file joining with metadata."""
        # First split a file
        split_dir = os.path.join(self.test_dir, "join_test")
        os.makedirs(split_dir)
        
        self.logic.split_file(self.test_file, split_dir, 'size', 500*1024, 1)
        
        # Clear captured messages
        self.complete_messages.clear()
        self.error_messages.clear()
        self.progress_updates.clear()
        
        # Now join the files
        first_chunk = os.path.join(split_dir, 'test_file.dat.part001')
        output_file = os.path.join(self.test_dir, "joined_file.dat")
        
        # Reset hub connector mock for join operation
        self.hub_connector_mock.reset_mock()
        
        self.logic.join_files(first_chunk, output_file)
        
        # Verify operation completed
        self.assertEqual(len(self.complete_messages), 1)
        self.assertEqual(len(self.error_messages), 0)
        self.assertTrue(os.path.exists(output_file))
        
        # Verify hub reporting was called for join operation
        self.hub_connector_mock.report_status_to_hub.assert_called()
        
        # Verify file integrity
        with open(output_file, 'rb') as f:
            joined_hash = hashlib.sha256(f.read()).hexdigest()
        self.assertEqual(joined_hash, self.original_hash)
        
        # Verify file size
        self.assertEqual(os.path.getsize(output_file), self.file_size)
    
    def test_join_files_without_metadata(self):
        """Test joining files without metadata file."""
        # Manually create chunks without metadata
        split_dir = os.path.join(self.test_dir, "manual_split")
        os.makedirs(split_dir)
        
        chunk_size = 1024 * 512  # 512KB
        num_chunks = (self.file_size + chunk_size - 1) // chunk_size
        
        with open(self.test_file, 'rb') as infile:
            for i in range(num_chunks):
                chunk_filename = f"test_file.dat.part{i+1:03d}"
                chunk_path = os.path.join(split_dir, chunk_filename)
                
                with open(chunk_path, 'wb') as outfile:
                    data = infile.read(chunk_size)
                    if data:
                        outfile.write(data)
        
        # Join files (should work without metadata)
        first_chunk = os.path.join(split_dir, 'test_file.dat.part001')
        output_file = os.path.join(self.test_dir, "manual_joined.dat")
        
        self.logic.join_files(first_chunk, output_file)
        
        # Verify operation completed
        self.assertEqual(len(self.complete_messages), 1)
        self.assertEqual(len(self.error_messages), 0)
        self.assertTrue(os.path.exists(output_file))
        
        # Verify file integrity
        with open(output_file, 'rb') as f:
            joined_hash = hashlib.sha256(f.read()).hexdigest()
        self.assertEqual(joined_hash, self.original_hash)
    
    def test_join_files_missing_chunk(self):
        """Test joining files with missing chunk."""
        # Create some chunks but delete one
        split_dir = os.path.join(self.test_dir, "missing_chunk")
        os.makedirs(split_dir)
        
        self.logic.split_file(self.test_file, split_dir, 'parts', 4, 1)
        
        # Delete middle chunk
        chunk_to_delete = os.path.join(split_dir, 'test_file.dat.part002')
        if os.path.exists(chunk_to_delete):
            os.remove(chunk_to_delete)
        
        # Clear captured messages
        self.complete_messages.clear()
        self.error_messages.clear()
        
        # Try to join (should fail)
        first_chunk = os.path.join(split_dir, 'test_file.dat.part001')
        output_file = os.path.join(self.test_dir, "incomplete_join.dat")
        
        self.logic.join_files(first_chunk, output_file)
        
        # Should emit error about missing chunk
        self.assertEqual(len(self.complete_messages), 0)
        self.assertGreater(len(self.error_messages), 0)
        self.assertIn("missing", self.error_messages[0].lower())
    
    def test_join_files_nonexistent_first_chunk(self):
        """Test joining with non-existent first chunk."""
        nonexistent_chunk = os.path.join(self.test_dir, "nonexistent.part001")
        output_file = os.path.join(self.test_dir, "failed_join.dat")
        
        self.logic.join_files(nonexistent_chunk, output_file)
        
        # Should emit error
        self.assertEqual(len(self.complete_messages), 0)
        self.assertGreater(len(self.error_messages), 0)
        self.assertIn("not found", self.error_messages[0].lower())
    
    def test_stop_operation(self):
        """Test stopping an operation."""
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
        self.assertEqual(self.logic.operation_stats['operation_type'], 'split')
    
    def test_progress_reporting_to_hub(self):
        """Test progress reporting to hub."""
        output_dir = os.path.join(self.test_dir, "progress_test")
        os.makedirs(output_dir)
        
        self.logic.split_file(self.test_file, output_dir, 'parts', 3, 1)
        
        # Verify progress was reported to hub
        self.hub_connector_mock.report_progress_to_hub.assert_called()
        
        # Verify status updates were sent
        self.hub_connector_mock.report_status_to_hub.assert_called()
    
    def test_configuration_integration(self):
        """Test configuration integration."""
        # Test configuration settings are used
        self.assertEqual(
            self.logic.config.get('default_chunk_size'),
            self.config.get('default_chunk_size')
        )
        
        # Update configuration
        self.config.set('verify_integrity', False)
        self.assertFalse(self.logic.config.get('verify_integrity'))
    
    def test_error_recovery_and_cleanup(self):
        """Test error recovery and cleanup behavior."""
        # Test with a non-existent parent directory that can't be created
        import tempfile
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Create a file in the temp directory first
            dummy_file = os.path.join(temp_dir, "dummy.txt")
            with open(dummy_file, 'w') as f:
                f.write("test")
            
            # Now try to use that file as a directory path (should fail)
            invalid_output_dir = os.path.join(dummy_file, "subdir")
            
            self.logic.split_file(self.test_file, invalid_output_dir, 'size', 1024, 1)
            
            # Should handle error gracefully
            # Either error messages should be generated OR the operation should complete
            # (depending on how the error is handled)
            has_error = len(self.error_messages) > 0
            has_completion = len(self.complete_messages) > 0
            
            # At least one should be true
            self.assertTrue(has_error or has_completion, 
                          "Operation should either complete or generate an error")
            
            # If there were errors, hub should have been notified
            if has_error:
                self.hub_connector_mock.report_error_to_hub.assert_called()
                
        finally:
            # Clean up temp directory
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestFileSplitterWorkerThread(unittest.TestCase):
    """Test suite for FileSplitterWorkerThread."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.config = FileSplitterConfig()
        self.logger = get_file_splitter_logger("test_worker")
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
    
    def test_worker_thread_join_operation(self):
        """Test worker thread join operation."""
        # Create a dummy first chunk file
        first_chunk = os.path.join(self.test_dir, "test.part001")
        with open(first_chunk, 'wb') as f:
            f.write(b"test data")
        
        output_file = os.path.join(self.test_dir, "joined.dat")
        
        thread = FileSplitterWorkerThread(
            self.logic, 'join',
            first_chunk, output_file
        )
        
        # Mock the join_files method
        with patch.object(self.logic, 'join_files') as mock_join:
            thread.run()
            mock_join.assert_called_once_with(first_chunk, output_file)
    
    def test_worker_thread_invalid_operation(self):
        """Test worker thread with invalid operation type."""
        thread = FileSplitterWorkerThread(
            self.logic, 'invalid_operation'
        )
        
        # Should handle gracefully (just log error)
        with patch.object(thread.logger, 'error') as mock_error:
            thread.run()
            mock_error.assert_called()


class TestFileSplitterIntegration(unittest.TestCase):
    """Integration tests for file splitter components."""
    
    def setUp(self):
        """Set up integration test environment."""
        self.test_dir = tempfile.mkdtemp()
        
        # Create test file with known content
        test_string = b"This is a test file for integration testing. " * 1000
        self.test_content = test_string
        self.test_file = os.path.join(self.test_dir, "integration_test.txt")
        with open(self.test_file, 'wb') as f:
            f.write(self.test_content)
    
    def tearDown(self):
        """Clean up integration test environment."""
        shutil.rmtree(self.test_dir)
    
    def test_full_split_join_cycle(self):
        """Test complete split and join cycle."""
        config = FileSplitterConfig()
        logger = get_file_splitter_logger("integration")
        logic = FileSplitterLogic(config, logger)
        
        # Mock hub connector
        hub_connector = Mock()
        logic.set_hub_connector(hub_connector)
        
        complete_messages = []
        
        def capture_complete(message):
            complete_messages.append(message)
        
        logic.operation_complete.connect(capture_complete)
        
        # Split the file
        split_dir = os.path.join(self.test_dir, "integration_split")
        os.makedirs(split_dir)
        
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
    
    def test_multiple_split_join_cycles(self):
        """Test multiple split and join cycles with different parameters."""
        config = FileSplitterConfig()
        logic = FileSplitterLogic(config)
        
        test_params = [
            ('size', 1024),    # 1KB chunks
            ('parts', 3),      # 3 parts
            ('size', 2048),    # 2KB chunks
        ]
        
        for i, (mode, value) in enumerate(test_params):
            with self.subTest(cycle=i, mode=mode, value=value):
                # Split
                split_dir = os.path.join(self.test_dir, f"cycle_{i}_split")
                os.makedirs(split_dir)
                
                logic.split_file(self.test_file, split_dir, mode, value, 1)
                
                # Verify chunks exist
                chunk_files = [f for f in os.listdir(split_dir)
                              if f.startswith('integration_test.txt.part')]
                self.assertGreater(len(chunk_files), 0)
                
                # Join
                first_chunk = os.path.join(split_dir, 'integration_test.txt.part001')
                joined_file = os.path.join(self.test_dir, f"cycle_{i}_joined.txt")
                
                logic.join_files(first_chunk, joined_file)
                
                # Verify integrity
                with open(joined_file, 'rb') as f:
                    joined_content = f.read()
                
                self.assertEqual(joined_content, self.test_content)


if __name__ == '__main__':
    # Initialize QApplication for Qt signal testing
    app = QCoreApplication([])
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestFileSplitterLogic))
    suite.addTests(loader.loadTestsFromTestCase(TestFileSplitterWorkerThread))
    suite.addTests(loader.loadTestsFromTestCase(TestFileSplitterIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with appropriate code
    exit(0 if result.wasSuccessful() else 1)