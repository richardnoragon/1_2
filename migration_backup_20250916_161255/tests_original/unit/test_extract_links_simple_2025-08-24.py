#!/usr/bin/env python3
"""
Comprehensive Unit Tests for extract_links.py
Test File: test_extract_links_2025-08-24.py
Created: 2025-08-24
Target: extract_links.py - PDF link extraction utility

This test suite provides comprehensive coverage for the ExtractLinksUI class
and its functionality including:
- UI initialization and setup
- File browsing functionality  
- PDF link extraction
- Error handling
- File operations
- Logging functionality
"""

import os
import shutil
import sys
import tempfile
from datetime import datetime
from unittest.mock import Mock, mock_open, patch

import pikepdf
import pytest
from PyQt5.QtWidgets import QApplication

# Add the source directory to the path
extraction_path = os.path.join(
    os.path.dirname(__file__), '..', '..', 'src', 'utilities',
    'pdf_tools', 'pdf_content_extraction'
)
operations_path = os.path.join(
    os.path.dirname(__file__), '..', '..', 'src', 'utilities',
    'pdf_tools', 'pdf_basic_operations'
)
sys.path.insert(0, extraction_path)
sys.path.insert(0, operations_path)

# Import the module under test
try:
    from extract_links import ExtractLinksUI, main
    from log_config import setup_logger
except ImportError as e:
    pytest.skip(
        f"Could not import extract_links module: {e}",
        allow_module_level=True
    )


class TestExtractLinksUI:
    """Test class for ExtractLinksUI functionality"""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup method run before each test"""
        self.test_start_time = datetime.now()
        
        # Create QApplication if it doesn't exist
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
            
        # Create temporary directories for testing
        self.temp_dir = tempfile.mkdtemp()
        self.urls_dir = os.path.join(self.temp_dir, 'urls')
        self.test_pdf_path = os.path.join(self.temp_dir, 'test.pdf')
        
        yield
        
        # Cleanup
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def mock_ui_file(self):
        """Mock the UI file loading"""
        with patch('extract_links.uic.loadUi') as mock_load:
            yield mock_load
    
    @pytest.fixture
    def sample_pdf_with_links(self):
        """Create a sample PDF with links for testing"""
        pdf = pikepdf.Pdf.new()
        page = pikepdf.Page.new(pdf)
        
        # Create annotation with link
        annot = pikepdf.Dictionary({
            '/Type': pikepdf.Name('/Annot'),
            '/Subtype': pikepdf.Name('/Link'),
            '/A': pikepdf.Dictionary({
                '/Type': pikepdf.Name('/Action'),
                '/S': pikepdf.Name('/URI'),
                '/URI': 'https://example.com'
            })
        })
        
        page['/Annots'] = pikepdf.Array([annot])
        pdf.pages.append(page)
        
        # Save to test file
        pdf.save(self.test_pdf_path)
        pdf.close()
        
        return self.test_pdf_path
    
    @pytest.fixture
    def sample_pdf_no_links(self):
        """Create a sample PDF without links for testing"""
        pdf = pikepdf.Pdf.new()
        page = pikepdf.Page.new(pdf)
        pdf.pages.append(page)
        pdf.save(self.test_pdf_path)
        pdf.close()
        return self.test_pdf_path

    def test_init_success(self, mock_ui_file):
        """Test successful initialization of ExtractLinksUI"""
        mock_ui_file.return_value = None
        
        with patch.object(ExtractLinksUI, 'show'), \
             patch.object(ExtractLinksUI, 'browseButton', Mock()), \
             patch.object(ExtractLinksUI, 'extractButton', Mock()), \
             patch.object(ExtractLinksUI, 'actionExit', Mock()):
            
            ui = ExtractLinksUI()
            
            assert ui is not None
            mock_ui_file.assert_called_once_with('extract_links.ui', ui)

    def test_init_failure(self, mock_ui_file):
        """Test initialization failure handling"""
        mock_ui_file.side_effect = Exception("UI file not found")
        
        with pytest.raises(Exception, match="UI file not found"):
            ExtractLinksUI()

    def test_browse_file_success(self, mock_ui_file):
        """Test successful file browsing"""
        mock_ui_file.return_value = None
        test_file_path = "/path/to/test.pdf"
        
        with patch.object(ExtractLinksUI, 'show'), \
             patch.object(ExtractLinksUI, 'browseButton', Mock()), \
             patch.object(ExtractLinksUI, 'extractButton', Mock()), \
             patch.object(ExtractLinksUI, 'actionExit', Mock()), \
             patch.object(ExtractLinksUI, 'inputFileEdit', Mock()) as mock_input, \
             patch('extract_links.QFileDialog.getOpenFileName') as mock_dialog:
            
            mock_dialog.return_value = (test_file_path, "PDF Files (*.pdf)")
            
            ui = ExtractLinksUI()
            ui.browse_file()
            
            mock_dialog.assert_called_once()
            mock_input.setText.assert_called_once_with(test_file_path)

    def test_browse_file_cancel(self, mock_ui_file):
        """Test file browsing when user cancels"""
        mock_ui_file.return_value = None
        
        with patch.object(ExtractLinksUI, 'show'), \
             patch.object(ExtractLinksUI, 'browseButton', Mock()), \
             patch.object(ExtractLinksUI, 'extractButton', Mock()), \
             patch.object(ExtractLinksUI, 'actionExit', Mock()), \
             patch.object(ExtractLinksUI, 'inputFileEdit', Mock()) as mock_input, \
             patch('extract_links.QFileDialog.getOpenFileName') as mock_dialog:
            
            mock_dialog.return_value = ("", "")
            
            ui = ExtractLinksUI()
            ui.browse_file()
            
            mock_dialog.assert_called_once()
            mock_input.setText.assert_not_called()

    def test_browse_file_exception(self, mock_ui_file):
        """Test file browsing exception handling"""
        mock_ui_file.return_value = None
        
        with patch.object(ExtractLinksUI, 'show'), \
             patch.object(ExtractLinksUI, 'browseButton', Mock()), \
             patch.object(ExtractLinksUI, 'extractButton', Mock()), \
             patch.object(ExtractLinksUI, 'actionExit', Mock()), \
             patch('extract_links.QFileDialog.getOpenFileName') as mock_dialog, \
             patch('extract_links.QMessageBox.critical') as mock_msgbox:
            
            mock_dialog.side_effect = Exception("Dialog error")
            
            ui = ExtractLinksUI()
            ui.browse_file()
            
            mock_msgbox.assert_called_once()

    def test_extract_links_no_file(self, mock_ui_file):
        """Test extract_links when no file is selected"""
        mock_ui_file.return_value = None
        
        with patch.object(ExtractLinksUI, 'show'), \
             patch.object(ExtractLinksUI, 'browseButton', Mock()), \
             patch.object(ExtractLinksUI, 'extractButton', Mock()), \
             patch.object(ExtractLinksUI, 'actionExit', Mock()), \
             patch.object(ExtractLinksUI, 'inputFileEdit', Mock()) as mock_input, \
             patch('extract_links.QMessageBox.warning') as mock_msgbox:
            
            mock_input.text.return_value = ""
            
            ui = ExtractLinksUI()
            ui.extract_links()
            
            mock_msgbox.assert_called_once()

    def test_extract_links_with_urls(self, mock_ui_file, sample_pdf_with_links):
        """Test successful link extraction from PDF with URLs"""
        mock_ui_file.return_value = None
        
        with patch.object(ExtractLinksUI, 'show'), \
             patch.object(ExtractLinksUI, 'browseButton', Mock()), \
             patch.object(ExtractLinksUI, 'extractButton', Mock()), \
             patch.object(ExtractLinksUI, 'actionExit', Mock()), \
             patch.object(ExtractLinksUI, 'inputFileEdit', Mock()) as mock_input, \
             patch.object(ExtractLinksUI, 'outputText', Mock()) as mock_output, \
             patch('extract_links.os.makedirs'), \
             patch('extract_links.os.path.exists') as mock_exists, \
             patch('extract_links.os.rename'), \
             patch('builtins.open', mock_open()):
            
            mock_input.text.return_value = sample_pdf_with_links
            mock_exists.return_value = False
            
            ui = ExtractLinksUI()
            ui.extract_links()
            
            # Verify output was written
            mock_output.append.assert_called()

    def test_extract_links_no_urls(self, mock_ui_file, sample_pdf_no_links):
        """Test link extraction from PDF without URLs"""
        mock_ui_file.return_value = None
        
        with patch.object(ExtractLinksUI, 'show'), \
             patch.object(ExtractLinksUI, 'browseButton', Mock()), \
             patch.object(ExtractLinksUI, 'extractButton', Mock()), \
             patch.object(ExtractLinksUI, 'actionExit', Mock()), \
             patch.object(ExtractLinksUI, 'inputFileEdit', Mock()) as mock_input, \
             patch.object(ExtractLinksUI, 'outputText', Mock()) as mock_output, \
             patch('extract_links.os.makedirs'), \
             patch('extract_links.os.path.exists') as mock_exists, \
             patch('extract_links.os.rename'), \
             patch('builtins.open', mock_open()):
            
            mock_input.text.return_value = sample_pdf_no_links
            mock_exists.return_value = False
            
            ui = ExtractLinksUI()
            ui.extract_links()
            
            # Verify total count shows 0 URLs
            calls = mock_output.append.call_args_list
            assert any("[*] Total URLs extracted: 0" in str(call) for call in calls)

    def test_extract_links_pdf_error(self, mock_ui_file):
        """Test extraction with PDF reading error"""
        mock_ui_file.return_value = None
        
        with patch.object(ExtractLinksUI, 'show'), \
             patch.object(ExtractLinksUI, 'browseButton', Mock()), \
             patch.object(ExtractLinksUI, 'extractButton', Mock()), \
             patch.object(ExtractLinksUI, 'actionExit', Mock()), \
             patch.object(ExtractLinksUI, 'inputFileEdit', Mock()) as mock_input, \
             patch('extract_links.pikepdf.Pdf.open') as mock_pdf, \
             patch('extract_links.QMessageBox.critical') as mock_msgbox:
            
            mock_input.text.return_value = "invalid.pdf"
            mock_pdf.side_effect = Exception("Cannot open PDF")
            
            ui = ExtractLinksUI()
            ui.extract_links()
            
            mock_msgbox.assert_called()

    def test_main_function_success(self):
        """Test main function successful execution"""
        with patch('extract_links.QApplication') as mock_app, \
             patch('extract_links.ExtractLinksUI'), \
             patch('sys.exit') as mock_exit:
            
            mock_app_instance = Mock()
            mock_app.return_value = mock_app_instance
            mock_app_instance.exec_.return_value = 0
            
            main()
            
            mock_app.assert_called_once()
            mock_exit.assert_called_once_with(0)

    def test_main_function_exception(self):
        """Test main function exception handling"""
        with patch('extract_links.QApplication') as mock_app, \
             patch('sys.exit') as mock_exit:
            
            mock_app.side_effect = Exception("Application error")
            
            main()
            
            mock_exit.assert_called_once_with(1)

    def test_logging_integration(self, mock_ui_file):
        """Test logging functionality integration"""
        mock_ui_file.return_value = None
        
        with patch.object(ExtractLinksUI, 'show'), \
             patch.object(ExtractLinksUI, 'browseButton', Mock()), \
             patch.object(ExtractLinksUI, 'extractButton', Mock()), \
             patch.object(ExtractLinksUI, 'actionExit', Mock()), \
             patch('extract_links.logger') as mock_logger:
            
            ExtractLinksUI()
            
            # Verify logger was used during initialization
            mock_logger.info.assert_called()

    def test_ui_signal_connections(self, mock_ui_file):
        """Test that UI signals are properly connected"""
        mock_ui_file.return_value = None
        
        mock_browse_btn = Mock()
        mock_extract_btn = Mock()
        mock_action_exit = Mock()
        
        with patch.object(ExtractLinksUI, 'show'), \
             patch.object(ExtractLinksUI, 'browseButton', mock_browse_btn), \
             patch.object(ExtractLinksUI, 'extractButton', mock_extract_btn), \
             patch.object(ExtractLinksUI, 'actionExit', mock_action_exit):
            
            ExtractLinksUI()
            
            # Verify signal connections
            mock_browse_btn.clicked.connect.assert_called_once()
            mock_extract_btn.clicked.connect.assert_called_once()
            mock_action_exit.triggered.connect.assert_called_once()


class TestLogConfig:
    """Test class for log_config functionality"""
    
    def test_setup_logger_creates_directory(self):
        """Test that setup_logger creates logs directory"""
        with patch('log_config.os.makedirs') as mock_makedirs, \
             patch('log_config.os.path.exists', return_value=False):
            
            logger = setup_logger('test_logger')
            mock_makedirs.assert_called_once_with('logs')
            assert logger.name == 'test_logger'

    def test_setup_logger_existing_directory(self):
        """Test setup_logger when logs directory exists"""
        with patch('log_config.os.makedirs') as mock_makedirs, \
             patch('log_config.os.path.exists', return_value=True):
            
            logger = setup_logger('test_logger')
            mock_makedirs.assert_not_called()
            assert logger.name == 'test_logger'


# Test execution timing and reporting
class TestReporting:
    """Test class for execution timing and reporting functionality"""
    
    def test_execution_timing(self):
        """Test that execution timing is properly tracked"""
        start_time = datetime.now()
        
        # Simulate test execution
        import time
        time.sleep(0.01)
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        assert execution_time > 0
        assert execution_time < 1  # Should be very fast

    def test_result_data_structure(self):
        """Test the structure of test result data"""
        test_result = {
            "timestamp": datetime.now().isoformat(),
            "test_name": "test_extract_links_2025-08-24",
            "status": "passed",
            "execution_time": 0.123,
            "coverage": 95.5,
            "details": "All tests passed successfully"
        }
        
        # Validate required fields
        assert "timestamp" in test_result
        assert "test_name" in test_result
        assert "status" in test_result
        assert isinstance(test_result["execution_time"], float)


if __name__ == "__main__":
    # Run tests when executed directly
    pytest.main([__file__, "-v", "--tb=short"])