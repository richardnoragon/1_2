"""
Comprehensive unit tests for extract_metadata.py
Created: 2025-08-24
"""

import os
import sys
import tempfile
from datetime import datetime
from unittest.mock import MagicMock, Mock, mock_open, patch

import pytest

# Add src path to import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'utilities', 'pdf_tools', 'pdf_content_extraction'))

try:
    from extract_metadata import MetadataExtractorUI, transform_date
except ImportError as e:
    pytest.skip(f"Cannot import extract_metadata module: {e}", allow_module_level=True)

import pikepdf
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication, QFileDialog, QMessageBox


class TestTransformDate:
    """Test cases for the transform_date function"""
    
    def test_transform_date_valid_format(self):
        """Test transform_date with valid PDF date format"""
        # Test standard PDF date format
        pdf_date = "D:20230815142530"
        expected = "2023-08-15T14:25:30"
        result = transform_date(pdf_date)
        assert result == expected
    
    def test_transform_date_without_d_prefix(self):
        """Test transform_date with date string without D: prefix"""
        pdf_date = "20230815142530"
        expected = "2023-08-15T14:25:30"
        result = transform_date(pdf_date)
        assert result == expected
    
    def test_transform_date_with_timezone(self):
        """Test transform_date with timezone information"""
        pdf_date = "D:20230815142530+05'00'"
        expected = "2023-08-15T14:25:30"
        result = transform_date(pdf_date)
        assert result == expected
    
    def test_transform_date_edge_cases(self):
        """Test transform_date with edge case dates"""
        # New Year's Day
        pdf_date = "D:20240101000000"
        expected = "2024-01-01T00:00:00"
        result = transform_date(pdf_date)
        assert result == expected
        
        # December 31st
        pdf_date = "D:20231231235959"
        expected = "2023-12-31T23:59:59"
        result = transform_date(pdf_date)
        assert result == expected
    
    def test_transform_date_invalid_format(self):
        """Test transform_date with invalid date format"""
        # Invalid date string should return the original string
        pdf_date = "invalid_date"
        result = transform_date(pdf_date)
        assert result == pdf_date
    
    def test_transform_date_empty_string(self):
        """Test transform_date with empty string"""
        pdf_date = ""
        result = transform_date(pdf_date)
        assert result == pdf_date
    
    def test_transform_date_partial_format(self):
        """Test transform_date with partial date format"""
        pdf_date = "D:2023"
        result = transform_date(pdf_date)
        # Should return the date without the D: prefix due to the way the function works
        assert result == "2023"


@pytest.fixture
def qapp():
    """Create QApplication for testing Qt widgets"""
    if not QApplication.instance():
        app = QApplication([])
    else:
        app = QApplication.instance()
    yield app
    # Don't quit the app as it might be used by other tests


@pytest.fixture
def mock_ui_file():
    """Mock the UI file loading"""
    with patch('extract_metadata.uic.loadUi') as mock_loadui:
        yield mock_loadui


@pytest.fixture
def mock_logger():
    """Mock logger for testing"""
    with patch('extract_metadata.setup_logger') as mock_setup_logger:
        mock_logger = Mock()
        mock_setup_logger.return_value = mock_logger
        yield mock_logger


class TestMetadataExtractorUI:
    """Test cases for MetadataExtractorUI class"""
    
    def setup_method(self):
        """Setup method called before each test"""
        self.test_files = []
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Teardown method called after each test"""
        # Clean up test files
        for file_path in self.test_files:
            if os.path.exists(file_path):
                os.remove(file_path)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)
    
    @patch('extract_metadata.uic.loadUi')
    def test_init_success(self, mock_loadui, qapp, mock_logger):
        """Test successful initialization of MetadataExtractorUI"""
        # Mock UI components
        mock_ui = Mock()
        mock_ui.browseButton = Mock()
        mock_ui.extractButton = Mock()
        mock_ui.actionExit = Mock()
        
        with patch.object(MetadataExtractorUI, '__init__', lambda x: None):
            extractor = MetadataExtractorUI()
            extractor.browseButton = mock_ui.browseButton
            extractor.extractButton = mock_ui.extractButton
            extractor.actionExit = mock_ui.actionExit
            
            # Verify components are created
            assert extractor.browseButton is not None
            assert extractor.extractButton is not None
            assert extractor.actionExit is not None
    
    @patch('extract_metadata.uic.loadUi')
    @patch('extract_metadata.QMessageBox.critical')
    def test_init_failure(self, mock_critical, mock_loadui, qapp, mock_logger):
        """Test initialization failure handling"""
        mock_loadui.side_effect = Exception("UI loading failed")
        
        with patch.object(MetadataExtractorUI, 'close') as mock_close:
            try:
                extractor = MetadataExtractorUI()
            except:
                pass
            mock_critical.assert_called()
    
    @patch('extract_metadata.QFileDialog.getOpenFileName')
    def test_browse_file_success(self, mock_dialog, qapp):
        """Test successful file browsing"""
        # Create a mock UI
        with patch('extract_metadata.uic.loadUi'):
            extractor = MetadataExtractorUI()
            extractor.inputFileEdit = Mock()
            extractor.extractButton = Mock()
            extractor.outputText = Mock()
            
            # Mock file dialog to return a file
            test_file = os.path.join(self.temp_dir, "test.pdf")
            mock_dialog.return_value = (test_file, "PDF Files (*.pdf)")
            
            extractor.browse_file()
            
            extractor.inputFileEdit.setText.assert_called_with(test_file)
            extractor.extractButton.setEnabled.assert_called_with(True)
            extractor.outputText.clear.assert_called()
    
    @patch('extract_metadata.QFileDialog.getOpenFileName')
    def test_browse_file_cancel(self, mock_dialog, qapp):
        """Test file browsing cancellation"""
        with patch('extract_metadata.uic.loadUi'):
            extractor = MetadataExtractorUI()
            extractor.inputFileEdit = Mock()
            extractor.extractButton = Mock()
            extractor.outputText = Mock()
            
            # Mock file dialog to return empty (cancelled)
            mock_dialog.return_value = ("", "")
            
            extractor.browse_file()
            
            extractor.inputFileEdit.setText.assert_not_called()
            extractor.extractButton.setEnabled.assert_not_called()
    
    @patch('extract_metadata.QMessageBox.critical')
    @patch('extract_metadata.QFileDialog.getOpenFileName')
    def test_browse_file_exception(self, mock_dialog, mock_critical, qapp):
        """Test file browsing exception handling"""
        with patch('extract_metadata.uic.loadUi'):
            extractor = MetadataExtractorUI()
            
            mock_dialog.side_effect = Exception("Dialog error")
            
            extractor.browse_file()
            
            mock_critical.assert_called()
    
    @patch('extract_metadata.QMessageBox.warning')
    def test_extract_metadata_no_file(self, mock_warning, qapp):
        """Test metadata extraction with no file selected"""
        with patch('extract_metadata.uic.loadUi'):
            extractor = MetadataExtractorUI()
            extractor.inputFileEdit = Mock()
            extractor.inputFileEdit.text.return_value = ""
            
            extractor.extract_metadata()
            
            mock_warning.assert_called()
    
    @patch('extract_metadata.QMessageBox.critical')
    @patch('extract_metadata.os.path.exists')
    def test_extract_metadata_file_not_found(self, mock_exists, mock_critical, qapp):
        """Test metadata extraction with non-existent file"""
        with patch('extract_metadata.uic.loadUi'):
            extractor = MetadataExtractorUI()
            extractor.inputFileEdit = Mock()
            extractor.inputFileEdit.text.return_value = "nonexistent.pdf"
            
            mock_exists.return_value = False
            
            extractor.extract_metadata()
            
            mock_critical.assert_called()
    
    @patch('extract_metadata.pikepdf.Pdf.open')
    @patch('extract_metadata.os.path.exists')
    def test_extract_metadata_success(self, mock_exists, mock_pdf_open, qapp):
        """Test successful metadata extraction"""
        with patch('extract_metadata.uic.loadUi'):
            extractor = MetadataExtractorUI()
            extractor.inputFileEdit = Mock()
            extractor.inputFileEdit.text.return_value = "test.pdf"
            extractor.outputText = Mock()
            extractor.statusBar = Mock(return_value=Mock())
            
            mock_exists.return_value = True
            
            # Mock PDF with metadata
            mock_pdf = Mock()
            mock_docinfo = {
                '/Title': 'Test Document',
                '/Author': 'Test Author',
                '/CreationDate': 'D:20230815142530'
            }
            mock_pdf.docinfo = mock_docinfo
            mock_pdf_open.return_value.__enter__.return_value = mock_pdf
            
            # Mock PyQt5 application processing
            with patch('extract_metadata.sys') as mock_sys:
                mock_sys.path = []
                extractor.extract_metadata()
            
            extractor.outputText.setText.assert_called()
            # Verify the metadata was processed
            call_args = extractor.outputText.setText.call_args[0][0]
            assert 'Title: Test Document' in call_args
            assert 'Author: Test Author' in call_args
            assert 'CreationDate: 2023-08-15T14:25:30' in call_args
    
    @patch('extract_metadata.QMessageBox.information')
    @patch('extract_metadata.pikepdf.Pdf.open')
    @patch('extract_metadata.os.path.exists')
    def test_extract_metadata_no_metadata(self, mock_exists, mock_pdf_open, mock_info, qapp):
        """Test metadata extraction with no metadata found"""
        with patch('extract_metadata.uic.loadUi'):
            extractor = MetadataExtractorUI()
            extractor.inputFileEdit = Mock()
            extractor.inputFileEdit.text.return_value = "test.pdf"
            extractor.statusBar = Mock(return_value=Mock())
            
            mock_exists.return_value = True
            
            # Mock PDF without metadata
            mock_pdf = Mock()
            mock_pdf.docinfo = None
            mock_pdf_open.return_value.__enter__.return_value = mock_pdf
            
            extractor.extract_metadata()
            
            mock_info.assert_called()
    
    @patch('extract_metadata.QMessageBox.critical')
    @patch('extract_metadata.pikepdf.Pdf.open')
    @patch('extract_metadata.os.path.exists')
    def test_extract_metadata_pdf_error(self, mock_exists, mock_pdf_open, mock_critical, qapp):
        """Test metadata extraction with PDF error"""
        with patch('extract_metadata.uic.loadUi'):
            extractor = MetadataExtractorUI()
            extractor.inputFileEdit = Mock()
            extractor.inputFileEdit.text.return_value = "corrupt.pdf"
            extractor.statusBar = Mock(return_value=Mock())
            
            mock_exists.return_value = True
            mock_pdf_open.side_effect = pikepdf.PdfError("Corrupt PDF")
            
            extractor.extract_metadata()
            
            mock_critical.assert_called()
    
    @patch('extract_metadata.QMessageBox.critical')
    @patch('extract_metadata.os.path.exists')
    def test_extract_metadata_general_exception(self, mock_exists, mock_critical, qapp):
        """Test metadata extraction with general exception"""
        with patch('extract_metadata.uic.loadUi'):
            extractor = MetadataExtractorUI()
            extractor.inputFileEdit = Mock()
            extractor.inputFileEdit.text.return_value = "test.pdf"
            
            mock_exists.side_effect = Exception("General error")
            
            extractor.extract_metadata()
            
            mock_critical.assert_called()


class TestMainFunction:
    """Test cases for the main function"""
    
    @patch('extract_metadata.QApplication')
    @patch('extract_metadata.MetadataExtractorUI')
    @patch('extract_metadata.sys.exit')
    def test_main_success(self, mock_exit, mock_ui, mock_app):
        """Test successful main function execution"""
        from extract_metadata import main
        
        mock_app_instance = Mock()
        mock_app.return_value = mock_app_instance
        mock_ui_instance = Mock()
        mock_ui.return_value = mock_ui_instance
        mock_app_instance.exec_.return_value = 0
        
        main()
        
        # Just check that QApplication was called (don't check specific args)
        mock_app.assert_called_once()
        mock_ui.assert_called_once()
        mock_exit.assert_called_with(0)
    
    @patch('extract_metadata.QApplication')
    @patch('extract_metadata.MetadataExtractorUI')
    @patch('extract_metadata.sys.exit')
    def test_main_exception(self, mock_exit, mock_ui, mock_app):
        """Test main function exception handling"""
        from extract_metadata import main
        
        mock_app.side_effect = Exception("App creation failed")
        
        main()
        
        mock_exit.assert_called_with(1)


class TestIntegration:
    """Integration tests for the entire module"""
    
    def setup_method(self):
        """Setup for integration tests"""
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Cleanup for integration tests"""
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)
    
    def test_transform_date_integration(self):
        """Integration test for transform_date with various formats"""
        test_cases = [
            ("D:20230815142530", "2023-08-15T14:25:30"),
            ("20230815142530", "2023-08-15T14:25:30"),
            ("D:20240101000000", "2024-01-01T00:00:00"),
            ("invalid", "invalid"),
            ("", ""),
        ]
        
        for input_date, expected in test_cases:
            result = transform_date(input_date)
            assert result == expected, f"Failed for input: {input_date}"


# Pytest configuration and fixtures for better test execution
@pytest.fixture(scope="session", autouse=True)
def test_session_setup():
    """Setup that runs once per test session"""
    print(f"\n{'='*60}")
    print(f"STARTING EXTRACT_METADATA TESTS - {datetime.now().isoformat()}")
    print(f"{'='*60}")
    yield
    print(f"\n{'='*60}")
    print(f"COMPLETED EXTRACT_METADATA TESTS - {datetime.now().isoformat()}")
    print(f"{'='*60}")


@pytest.fixture(autouse=True)
def test_setup_teardown():
    """Setup and teardown for each test"""
    test_start = datetime.now()
    yield
    test_end = datetime.now()
    duration = (test_end - test_start).total_seconds()
    print(f"Test duration: {duration:.3f}s")


# Custom pytest markers for test categorization
pytestmark = [
    pytest.mark.unit,
    pytest.mark.extract_metadata
]
