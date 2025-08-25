"""
Simplified unit tests for extract_tables_camelot.py (Core Functions Only)
Created: 2025-08-24
Test Coverage: Configuration and extraction functions without GUI components
"""

import json
import os
import sys
import tempfile
from unittest.mock import Mock, mock_open, patch

import pytest

# Add the source directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'utilities', 'pdf_tools', 'pdf_content_extraction'))

# Import the module under test
try:
    import extract_tables_camelot as etc
except ImportError as e:
    pytest.skip(f"Could not import extract_tables_camelot: {e}", allow_module_level=True)


class TestConfigManagement:
    """Test configuration loading and saving functions."""
    
    def test_load_config_success(self):
        """Test successful configuration loading."""
        config_data = {
            "extract_tables": {
                "flavor": "lattice",
                "line_scale": 15,
                "process_background": False
            }
        }
        
        with patch('builtins.open', mock_open(read_data=json.dumps(config_data))):
            with patch('extract_tables_camelot.logger') as mock_logger:
                result = etc.load_config()
                
                assert result == config_data
                mock_logger.error.assert_not_called()
    
    def test_load_config_file_not_found(self):
        """Test configuration loading when file doesn't exist."""
        with patch('builtins.open', side_effect=FileNotFoundError("File not found")):
            with patch('extract_tables_camelot.logger') as mock_logger:
                result = etc.load_config()
                
                assert result is None
                mock_logger.error.assert_called_once()
    
    def test_load_config_invalid_json(self):
        """Test configuration loading with invalid JSON."""
        with patch('builtins.open', mock_open(read_data="invalid json")):
            with patch('extract_tables_camelot.logger') as mock_logger:
                result = etc.load_config()
                
                assert result is None
                mock_logger.error.assert_called_once()
    
    def test_save_config_success(self):
        """Test successful configuration saving."""
        config_data = {"test": "data"}
        
        with patch('builtins.open', mock_open()) as mock_file:
            with patch('json.dump') as mock_json_dump:
                with patch('extract_tables_camelot.logger') as mock_logger:
                    result = etc.save_config(config_data)
                    
                    assert result is True
                    mock_file.assert_called_once_with('config.json', 'w')
                    mock_json_dump.assert_called_once()
                    mock_logger.error.assert_not_called()
    
    def test_save_config_error(self):
        """Test configuration saving with error."""
        config_data = {"test": "data"}
        
        with patch('builtins.open', side_effect=OSError("Write error")):
            with patch('extract_tables_camelot.logger') as mock_logger:
                result = etc.save_config(config_data)
                
                assert result is False
                mock_logger.error.assert_called_once()


class TestExtractTables:
    """Test the main table extraction function."""
    
    def test_extract_tables_success(self):
        """Test successful table extraction."""
        # Mock camelot.read_pdf to return mock tables
        mock_table1 = Mock()
        mock_table1.to_csv = Mock()
        mock_table2 = Mock()
        mock_table2.to_csv = Mock()
        
        mock_tables = [mock_table1, mock_table2]
        
        with patch('camelot.read_pdf', return_value=mock_tables) as mock_read_pdf:
            with patch('extract_tables_camelot.logger') as mock_logger:
                with patch('os.path.exists', return_value=True):
                    result = etc.extract_tables('test.pdf', 'output', flavor='lattice')
                    
                    assert result is True
                    mock_read_pdf.assert_called_once()
                    mock_logger.info.assert_called()
                    assert mock_table1.to_csv.call_count == 1
                    assert mock_table2.to_csv.call_count == 1
    
    def test_extract_tables_no_tables_found(self):
        """Test table extraction when no tables are found."""
        mock_tables = []
        
        with patch('camelot.read_pdf', return_value=mock_tables):
            with patch('extract_tables_camelot.logger') as mock_logger:
                with patch('os.path.exists', return_value=True):
                    result = etc.extract_tables('test.pdf', 'output')
                    
                    assert result is False
                    mock_logger.warning.assert_called()
    
    def test_extract_tables_camelot_error(self):
        """Test table extraction with camelot error."""
        with patch('camelot.read_pdf', side_effect=Exception("Camelot error")):
            with patch('extract_tables_camelot.logger') as mock_logger:
                with patch('PyQt5.QtWidgets.QMessageBox.critical'):
                    result = etc.extract_tables('test.pdf', 'output')
                    
                    assert result is False
                    mock_logger.error.assert_called()
    
    def test_extract_tables_with_parameters(self):
        """Test table extraction with various parameters."""
        mock_table = Mock()
        mock_table.to_csv = Mock()
        mock_tables = [mock_table]
        
        params = {
            'flavor': 'stream',
            'line_scale': 20,
            'process_background': True,
            'pages': '1-3'
        }
        
        with patch('camelot.read_pdf', return_value=mock_tables) as mock_read_pdf:
            with patch('extract_tables_camelot.logger'):
                with patch('os.path.exists', return_value=True):
                    result = etc.extract_tables('test.pdf', 'output', **params)
                    
                    assert result is True
                    mock_read_pdf.assert_called_once_with('test.pdf', **params)
    
    def test_extract_tables_auto_output_folder(self):
        """Test table extraction with automatic output folder creation."""
        mock_table = Mock()
        mock_table.to_csv = Mock()
        mock_tables = [mock_table]
        
        with patch('camelot.read_pdf', return_value=mock_tables):
            with patch('os.path.exists', return_value=False):
                with patch('os.makedirs') as mock_makedirs:
                    with patch('extract_tables_camelot.logger'):
                        result = etc.extract_tables('test.pdf')
                        
                        assert result is True
                        mock_makedirs.assert_called()


class TestParameterValidation:
    """Test parameter validation and edge cases."""
    
    def test_save_config_none_config(self):
        """Test save_config with None configuration."""
        with patch('builtins.open', mock_open()):
            with patch('json.dump'):
                result = etc.save_config(None)
                assert isinstance(result, bool)
    
    def test_save_config_empty_config(self):
        """Test save_config with empty configuration."""
        with patch('builtins.open', mock_open()):
            with patch('json.dump'):
                result = etc.save_config({})
                assert result is True


class TestIntegration:
    """Integration tests combining multiple components."""
    
    def test_config_roundtrip(self):
        """Test saving and loading configuration."""
        test_config = {
            "extract_tables": {
                "flavor": "stream",
                "line_scale": 25,
                "process_background": True
            }
        }
        
        # Save config
        with patch('builtins.open', mock_open()):
            with patch('json.dump'):
                save_result = etc.save_config(test_config)
                assert save_result is True
        
        # Load config
        with patch('builtins.open', mock_open(read_data=json.dumps(test_config))):
            loaded_config = etc.load_config()
            assert loaded_config == test_config
    
    def test_extract_tables_full_workflow(self):
        """Test complete table extraction workflow."""
        # Mock the entire camelot workflow
        mock_table = Mock()
        mock_table.to_csv = Mock()
        mock_tables = [mock_table]
        
        with patch('camelot.read_pdf', return_value=mock_tables):
            with patch('os.path.exists', return_value=True):
                with patch('extract_tables_camelot.logger'):
                    params = {
                        'flavor': 'lattice',
                        'line_scale': 15,
                        'process_background': False
                    }
                    
                    result = etc.extract_tables('test.pdf', 'output', **params)
                    
                    assert result is True
                    mock_table.to_csv.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])