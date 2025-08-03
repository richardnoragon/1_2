"""
Integration Tests for File Splitter

This module provides comprehensive integration testing for the file splitter
with file_utilities_2 components, including hub integration, cross-tool
compatibility, and end-to-end functionality testing.
"""

import unittest
import os
import tempfile
import shutil
from unittest.mock import Mock, patch
from PyQt5.QtCore import QCoreApplication

from file_utilities_2.integration.file_splitter_connector import (
    FileSplitterHubConnector, create_file_splitter_hub_connector,
    register_file_splitter_with_hub
)
from file_utilities_2.core.file_splitter_logic import FileSplitterLogic
from file_utilities_2.core.file_splitter_config import FileSplitterConfig
from file_utilities_2.core.file_splitter_logging import get_file_splitter_logger


class TestFileSplitterHubIntegration(unittest.TestCase):
    """Test suite for file splitter hub integration."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_dir = tempfile.mkdtemp()
        
        # Create test file
        self.test_file = os.path.join(self.test_dir, "integration_test.dat")
        with open(self.test_file, 'wb') as f:
            f.write(os.urandom(2048))  # 2KB test file
        
        # Mock hub instance
        self.mock_hub = Mock()
        
        # Create hub connector with mocked hub
        with patch('file_utilities_2.integration.file_splitter_connector.HubIntegratedTool.__init__'):
            self.hub_connector = FileSplitterHubConnector()
            self.hub_connector.hub_connector = Mock()
    
    def tearDown(self):
        """Clean up test fixtures after each test method."""
        shutil.rmtree(self.test_dir)
    
    def test_hub_connector_initialization(self):
        """Test hub connector initialization."""
        self.assertEqual(self.hub_connector.tool_name, "file_splitter")
        self.assertIsNotNone(self.hub_connector.config)
        self.assertIsNotNone(self.hub_connector.logger)
        self.assertIsNotNone(self.hub_connector.splitter_logic)
    
    def test_split_operation_via_hub(self):
        """Test starting split operation via hub connector."""
        output_dir = os.path.join(self.test_dir, "hub_split")
        os.makedirs(output_dir)
        
        # Mock the split_file method
        with patch.object(self.hub_connector.splitter_logic, 'split_file') as mock_split:
            result = self.hub_connector.start_split_operation(
                self.test_file, output_dir, 'size', 1024, 1
            )
            
            self.assertTrue(result)
            mock_split.assert_called_once_with(
                self.test_file, output_dir, 'size', 1024, 1
            )
    
    def test_join_operation_via_hub(self):
        """Test starting join operation via hub connector."""
        chunk_file = os.path.join(self.test_dir, "test.part001")
        output_file = os.path.join(self.test_dir, "joined.dat")
        
        # Create dummy chunk file
        with open(chunk_file, 'wb') as f:
            f.write(b"test data")
        
        # Mock the join_files method
        with patch.object(self.hub_connector.splitter_logic, 'join_files') as mock_join:
            result = self.hub_connector.start_join_operation(chunk_file, output_file)
            
            self.assertTrue(result)
            mock_join.assert_called_once_with(chunk_file, output_file)
    
    def test_operation_status_reporting(self):
        """Test operation status reporting."""
        status = self.hub_connector.get_operation_status()
        
        self.assertIsInstance(status, dict)
        self.assertIn('tool_name', status)
        self.assertIn('is_running', status)
        self.assertIn('operation_stats', status)
        self.assertIn('config_summary', status)
        self.assertIn('hub_connected', status)
        
        self.assertEqual(status['tool_name'], 'file_splitter')
    
    def test_configuration_update_via_hub(self):
        """Test configuration updates via hub."""
        config_updates = {
            'default_chunk_size': 2048,
            'verify_integrity': False
        }
        
        result = self.hub_connector.update_configuration(config_updates)
        
        self.assertTrue(result)
        self.assertEqual(
            self.hub_connector.config.get('default_chunk_size'), 2048
        )
        self.assertFalse(
            self.hub_connector.config.get('verify_integrity')
        )
    
    def test_hub_command_handling(self):
        """Test handling commands from hub."""
        # Test split_file command
        with patch.object(self.hub_connector, 'start_split_operation', return_value=True):
            result = self.hub_connector.handle_hub_command(
                'split_file',
                {
                    'input_filepath': self.test_file,
                    'output_dir': self.test_dir,
                    'split_mode': 'size',
                    'value': 1024
                }
            )
            
            self.assertTrue(result['success'])
            self.assertEqual(result['command'], 'split_file')
        
        # Test get_status command
        result = self.hub_connector.handle_hub_command('get_status', {})
        
        self.assertTrue(result['success'])
        self.assertEqual(result['command'], 'get_status')
        self.assertIn('status', result)
        
        # Test unknown command
        result = self.hub_connector.handle_hub_command('unknown_command', {})
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)


class TestCrossToolCompatibility(unittest.TestCase):
    """Test suite for cross-tool compatibility and integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        
        # Create components
        self.config = FileSplitterConfig()
        self.logger = get_file_splitter_logger()
        self.logic = FileSplitterLogic(self.config, self.logger)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)
    
    def test_shared_configuration_compatibility(self):
        """Test compatibility with shared configuration system."""
        # Test configuration can be shared across tools
        shared_config = {
            'log_level': 'DEBUG',
            'enable_hub_reporting': True,
            'memory_limit_mb': 256
        }
        
        self.config.update(shared_config)
        
        # Verify configuration is applied
        self.assertEqual(self.config.get('log_level'), 'DEBUG')
        self.assertTrue(self.config.get('enable_hub_reporting'))
        self.assertEqual(self.config.get('memory_limit_mb'), 256)
    
    def test_shared_logging_compatibility(self):
        """Test compatibility with shared logging system."""
        # Test logger can be used by other tools
        logger = get_file_splitter_logger("shared_test")
        
        # Test logging functionality
        with patch.object(logger, 'info') as mock_info:
            logger.info("Test shared logging")
            mock_info.assert_called_once_with("Test shared logging")


if __name__ == '__main__':
    # Initialize QApplication for Qt signal testing
    app = QCoreApplication([])
    unittest.main()