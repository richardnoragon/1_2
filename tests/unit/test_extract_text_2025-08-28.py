"""
Comprehensive unit tests for extract_text.py
Generated on: 2025-08-28
Target: src/utilities/pdf_tools/pdf_content_extraction/extract_text.py
"""

import json
import os
import sys
import tempfile
import threading
import time
from datetime import datetime
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, Mock, call, mock_open, patch

import pytest
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QTimer
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication, QMessageBox

# Add the source directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'utilities', 'pdf_tools', 'pdf_content_extraction'))

try:
    from extract_text import ExtractTextUI, extract_text_from_pdf, main
except ImportError as e:
    pytest.skip(f"Cannot import extract_text module: {e}", allow_module_level=True)


class TestExtractTextFromPdf:
    """Test extract_text_from_pdf function."""
    
    @pytest.fixture
    def sample_pdf_path(self):
        """Create a temporary PDF file path."""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            yield f.name
        # Cleanup
        try:
            os.unlink(f.name)
        except FileNotFoundError:
            pass
    
    @pytest.fixture
    def mock_logger(self):
        """Mock logger for testing."""
        with patch('extract_text.logger') as mock_log:
            yield mock_log
    
    def test_extract_text_file_not_found(self, mock_logger):
        """Test extraction with non-existent file."""
        with patch('extract_text.QMessageBox') as mock_msg:
            result = extract_text_from_pdf("/non/existent/file.pdf")
            
            assert result is False
            mock_logger.error.assert_called()
            mock_msg.critical.assert_called()
    
    def test_extract_text_invalid_input_path(self, mock_logger):
        """Test extraction with invalid input path."""
        with patch('extract_text.QMessageBox') as mock_msg:
            result = extract_text_from_pdf("")
            
            assert result is False
            mock_logger.error.assert_called()
    
    @patch('extract_text.os.path.exists')
    @patch('extract_text.pdfplumber.open')
    def test_extract_text_success_no_output_file(self, mock_pdf_open, mock_exists, mock_logger):
        """Test successful text extraction without output file."""
        mock_exists.return_value = True
        
        # Mock PDF structure
        mock_page = Mock()
        mock_page.extract_text.return_value = "Sample text from page 1"
        
        mock_pdf = Mock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__.return_value = mock_pdf
        mock_pdf.__exit__.return_value = None
        
        mock_pdf_open.return_value = mock_pdf
        
        result = extract_text_from_pdf("test.pdf")
        
        assert isinstance(result, str)
        assert "Sample text from page 1" in result
        assert "=== Page 1 ===" in result
        mock_logger.info.assert_called()
        mock_logger.debug.assert_called()
    
    @patch('extract_text.os.path.exists')
    @patch('extract_text.pdfplumber.open')
    @patch('builtins.open', new_callable=mock_open)
    def test_extract_text_success_with_output_file(self, mock_file_open, mock_pdf_open, mock_exists, mock_logger):
        """Test successful text extraction with output file."""
        mock_exists.return_value = True
        
        # Mock PDF structure
        mock_page = Mock()
        mock_page.extract_text.return_value = "Sample text"
        
        mock_pdf = Mock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__.return_value = mock_pdf
        mock_pdf.__exit__.return_value = None
        
        mock_pdf_open.return_value = mock_pdf
        
        result = extract_text_from_pdf("test.pdf", "output.txt")
        
        assert result is True
        mock_file_open.assert_called_once_with("output.txt", 'w', encoding='utf-8')
        mock_logger.info.assert_called()
    
    @patch('extract_text.os.path.exists')
    @patch('extract_text.pdfplumber.open')
    def test_extract_text_multiple_pages(self, mock_pdf_open, mock_exists, mock_logger):
        """Test text extraction from multiple pages."""
        mock_exists.return_value = True
        
        # Mock multiple pages
        mock_page1 = Mock()
        mock_page1.extract_text.return_value = "Page 1 text"
        
        mock_page2 = Mock()
        mock_page2.extract_text.return_value = "Page 2 text"
        
        mock_page3 = Mock()
        mock_page3.extract_text.return_value = "Page 3 text"
        
        mock_pdf = Mock()
        mock_pdf.pages = [mock_page1, mock_page2, mock_page3]
        mock_pdf.__enter__.return_value = mock_pdf
        mock_pdf.__exit__.return_value = None
        
        mock_pdf_open.return_value = mock_pdf
        
        result = extract_text_from_pdf("test.pdf")
        
        assert isinstance(result, str)
        assert "Page 1 text" in result
        assert "Page 2 text" in result
        assert "Page 3 text" in result
        assert "=== Page 1 ===" in result
        assert "=== Page 2 ===" in result
        assert "=== Page 3 ===" in result
    
    @patch('extract_text.os.path.exists')
    @patch('extract_text.pdfplumber.open')
    def test_extract_text_specific_pages(self, mock_pdf_open, mock_exists, mock_logger):
        """Test text extraction from specific pages."""
        mock_exists.return_value = True
        
        # Mock multiple pages
        pages = []
        for i in range(5):
            mock_page = Mock()
            mock_page.extract_text.return_value = f"Page {i+1} text"
            pages.append(mock_page)
        
        mock_pdf = Mock()
        mock_pdf.pages = pages
        mock_pdf.__enter__.return_value = mock_pdf
        mock_pdf.__exit__.return_value = None
        
        mock_pdf_open.return_value = mock_pdf
        
        # Test extracting pages 2-4
        result = extract_text_from_pdf("test.pdf", pages="2-4")
        
        assert isinstance(result, str)
        assert "Page 2 text" in result
        assert "Page 3 text" in result
        assert "Page 4 text" in result
        assert "Page 1 text" not in result
        assert "Page 5 text" not in result
    
    @patch('extract_text.os.path.exists')
    @patch('extract_text.pdfplumber.open')
    def test_extract_text_specific_pages_comma_separated(self, mock_pdf_open, mock_exists, mock_logger):
        """Test text extraction from comma-separated specific pages."""
        mock_exists.return_value = True
        
        # Mock multiple pages
        pages = []
        for i in range(5):
            mock_page = Mock()
            mock_page.extract_text.return_value = f"Page {i+1} text"
            pages.append(mock_page)
        
        mock_pdf = Mock()
        mock_pdf.pages = pages
        mock_pdf.__enter__.return_value = mock_pdf
        mock_pdf.__exit__.return_value = None
        
        mock_pdf_open.return_value = mock_pdf
        
        # Test extracting pages 1, 3, 5
        result = extract_text_from_pdf("test.pdf", pages="1,3,5")
        
        assert isinstance(result, str)
        assert "Page 1 text" in result
        assert "Page 3 text" in result
        assert "Page 5 text" in result
        assert "Page 2 text" not in result
        assert "Page 4 text" not in result
    
    @patch('extract_text.os.path.exists')
    def test_extract_text_invalid_page_range(self, mock_exists, mock_logger):
        """Test extraction with invalid page range."""
        mock_exists.return_value = True
        
        with patch('extract_text.QMessageBox') as mock_msg:
            result = extract_text_from_pdf("test.pdf", pages="invalid-range")
            
            assert result is False
            mock_logger.error.assert_called()
            mock_msg.critical.assert_called()
    
    @patch('extract_text.os.path.exists')
    @patch('extract_text.pdfplumber.open')
    def test_extract_text_page_out_of_range(self, mock_pdf_open, mock_exists, mock_logger):
        """Test extraction with page numbers out of range."""
        mock_exists.return_value = True
        
        # Mock single page PDF
        mock_page = Mock()
        mock_page.extract_text.return_value = "Page 1 text"
        
        mock_pdf = Mock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__.return_value = mock_pdf
        mock_pdf.__exit__.return_value = None
        
        mock_pdf_open.return_value = mock_pdf
        
        result = extract_text_from_pdf("test.pdf", pages="1,5")  # Page 5 doesn't exist
        
        assert isinstance(result, str)
        assert "Page 1 text" in result
        mock_logger.warning.assert_called()
    
    @patch('extract_text.os.path.exists')
    @patch('extract_text.pdfplumber.open')
    def test_extract_text_page_extraction_error(self, mock_pdf_open, mock_exists, mock_logger):
        """Test handling of page extraction errors."""
        mock_exists.return_value = True
        
        # Mock page that raises exception
        mock_page = Mock()
        mock_page.extract_text.side_effect = Exception("Page extraction error")
        
        mock_pdf = Mock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__.return_value = mock_pdf
        mock_pdf.__exit__.return_value = None
        
        mock_pdf_open.return_value = mock_pdf
        
        with patch('extract_text.QMessageBox') as mock_msg:
            result = extract_text_from_pdf("test.pdf")
            
            # Should return empty string but not fail completely
            assert isinstance(result, str)
            mock_logger.error.assert_called()
            mock_msg.warning.assert_called()
    
    @patch('extract_text.os.path.exists')
    @patch('extract_text.pdfplumber.open')
    def test_extract_text_empty_pages(self, mock_pdf_open, mock_exists, mock_logger):
        """Test extraction from pages with no text."""
        mock_exists.return_value = True
        
        # Mock page with no text
        mock_page1 = Mock()
        mock_page1.extract_text.return_value = None
        
        mock_page2 = Mock()
        mock_page2.extract_text.return_value = ""
        
        mock_page3 = Mock()
        mock_page3.extract_text.return_value = "Some text"
        
        mock_pdf = Mock()
        mock_pdf.pages = [mock_page1, mock_page2, mock_page3]
        mock_pdf.__enter__.return_value = mock_pdf
        mock_pdf.__exit__.return_value = None
        
        mock_pdf_open.return_value = mock_pdf
        
        result = extract_text_from_pdf("test.pdf")
        
        assert isinstance(result, str)
        assert "Some text" in result
        assert "=== Page 3 ===" in result
        # Pages 1 and 2 should not have content sections
        assert result.count("===") == 2  # Only opening and closing for page 3
    
    @patch('extract_text.os.path.exists')
    @patch('extract_text.pdfplumber.open')
    def test_extract_text_pdf_open_error(self, mock_pdf_open, mock_exists, mock_logger):
        """Test handling of PDF opening errors."""
        mock_exists.return_value = True
        mock_pdf_open.side_effect = Exception("Cannot open PDF")
        
        with patch('extract_text.QMessageBox') as mock_msg:
            result = extract_text_from_pdf("test.pdf")
            
            assert result is False
            mock_logger.error.assert_called()
            mock_msg.critical.assert_called()
    
    @patch('extract_text.os.path.exists')
    @patch('extract_text.pdfplumber.open')
    @patch('builtins.open', new_callable=mock_open)
    def test_extract_text_file_save_error(self, mock_file_open, mock_pdf_open, mock_exists, mock_logger):
        """Test handling of file save errors."""
        mock_exists.return_value = True
        
        # Mock PDF structure
        mock_page = Mock()
        mock_page.extract_text.return_value = "Sample text"
        
        mock_pdf = Mock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__.return_value = mock_pdf
        mock_pdf.__exit__.return_value = None
        
        mock_pdf_open.return_value = mock_pdf
        mock_file_open.side_effect = PermissionError("Cannot write file")
        
        with patch('extract_text.QMessageBox') as mock_msg:
            result = extract_text_from_pdf("test.pdf", "output.txt")
            
            assert result is False
            mock_logger.error.assert_called()
            mock_msg.critical.assert_called()
    
    @patch('extract_text.os.path.exists')
    def test_extract_text_unexpected_error(self, mock_exists, mock_logger):
        """Test handling of unexpected errors."""
        mock_exists.side_effect = Exception("Unexpected error")
        
        with patch('extract_text.QMessageBox') as mock_msg:
            result = extract_text_from_pdf("test.pdf")
            
            assert result is False
            mock_logger.error.assert_called()
            mock_msg.critical.assert_called()


@pytest.fixture(scope="module")
def qapp():
    """Create QApplication instance for testing."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    # Don't quit the app as it might be used by other tests


class TestExtractTextUI:
    """Test ExtractTextUI class."""
    
    @pytest.fixture
    def mock_ui_file(self):
        """Mock the UI file loading."""
        with patch('extract_text.uic.loadUi') as mock_load:
            yield mock_load
    
    @pytest.fixture
    def mock_widgets(self):
        """Mock Qt widgets."""
        with patch.multiple(
            'extract_text.QtWidgets',
            QProgressBar=Mock,
            QMainWindow=Mock
        ) as mocks:
            yield mocks
    
    @pytest.fixture
    def mock_logger(self):
        """Mock logger for UI testing."""
        with patch('extract_text.logger') as mock_log:
            yield mock_log
    
    def test_init_success(self, qapp, mock_ui_file, mock_logger):
        """Test successful UI initialization."""
        with patch.object(ExtractTextUI, 'show'):
            # Mock all required attributes
            mock_ui = Mock()
            mock_ui.browseButton = Mock()
            mock_ui.extractButton = Mock()
            mock_ui.saveButton = Mock()
            mock_ui.actionExit = Mock()
            mock_ui.statusBar.return_value.addPermanentWidget = Mock()
            
            with patch('extract_text.QtWidgets.QProgressBar'):
                with patch.multiple(
                    ExtractTextUI,
                    browseButton=Mock(),
                    extractButton=Mock(),
                    saveButton=Mock(),
                    actionExit=Mock(),
                    statusBar=Mock(),
                    inputFileEdit=Mock(),
                    outputText=Mock(),
                    pagesEdit=Mock()
                ):
                    ui = ExtractTextUI()
                    
                    assert ui.current_file is None
                    mock_logger.info.assert_called()
                    mock_logger.debug.assert_called()
    
    def test_init_ui_load_failure(self, qapp, mock_logger):
        """Test UI initialization with UI loading failure."""
        with patch('extract_text.uic.loadUi', side_effect=Exception("UI load error")):
            with patch('extract_text.QMessageBox') as mock_msg:
                with patch.object(ExtractTextUI, 'close'):
                    ui = ExtractTextUI()
                    
                    mock_logger.error.assert_called()
                    mock_msg.critical.assert_called()
    
    def test_browse_file_success(self, qapp, mock_ui_file, mock_logger):
        """Test successful file browsing."""
        with patch('extract_text.QFileDialog.getOpenFileName') as mock_dialog:
            mock_dialog.return_value = ("/path/to/test.pdf", "PDF Files (*.pdf)")
            
            with patch.object(ExtractTextUI, 'show'):
                with patch.multiple(
                    ExtractTextUI,
                    browseButton=Mock(),
                    extractButton=Mock(),
                    saveButton=Mock(),
                    actionExit=Mock(),
                    statusBar=Mock(),
                    inputFileEdit=Mock(),
                    outputText=Mock(),
                    pagesEdit=Mock()
                ):
                    ui = ExtractTextUI()
                    ui.browse_file()
                    
                    assert ui.current_file == "/path/to/test.pdf"
                    ui.inputFileEdit.setText.assert_called_with("/path/to/test.pdf")
                    ui.extractButton.setEnabled.assert_called_with(True)
                    ui.outputText.clear.assert_called()
                    mock_logger.info.assert_called()
    
    def test_browse_file_cancelled(self, qapp, mock_ui_file, mock_logger):
        """Test file browsing when user cancels."""
        with patch('extract_text.QFileDialog.getOpenFileName') as mock_dialog:
            mock_dialog.return_value = ("", "")
            
            with patch.object(ExtractTextUI, 'show'):
                with patch.multiple(
                    ExtractTextUI,
                    browseButton=Mock(),
                    extractButton=Mock(),
                    saveButton=Mock(),
                    actionExit=Mock(),
                    statusBar=Mock(),
                    inputFileEdit=Mock(),
                    outputText=Mock(),
                    pagesEdit=Mock()
                ):
                    ui = ExtractTextUI()
                    original_file = ui.current_file
                    ui.browse_file()
                    
                    # File should remain unchanged
                    assert ui.current_file == original_file
    
    def test_browse_file_error(self, qapp, mock_ui_file, mock_logger):
        """Test file browsing with error."""
        with patch('extract_text.QFileDialog.getOpenFileName', side_effect=Exception("Dialog error")):
            with patch('extract_text.QMessageBox') as mock_msg:
                with patch.object(ExtractTextUI, 'show'):
                    with patch.multiple(
                        ExtractTextUI,
                        browseButton=Mock(),
                        extractButton=Mock(),
                        saveButton=Mock(),
                        actionExit=Mock(),
                        statusBar=Mock(),
                        inputFileEdit=Mock(),
                        outputText=Mock(),
                        pagesEdit=Mock()
                    ):
                        ui = ExtractTextUI()
                        ui.browse_file()
                        
                        mock_logger.error.assert_called()
                        mock_msg.critical.assert_called()
    
    def test_extract_text_no_file(self, qapp, mock_ui_file, mock_logger):
        """Test text extraction without selected file."""
        with patch('extract_text.QMessageBox') as mock_msg:
            with patch.object(ExtractTextUI, 'show'):
                with patch.multiple(
                    ExtractTextUI,
                    browseButton=Mock(),
                    extractButton=Mock(),
                    saveButton=Mock(),
                    actionExit=Mock(),
                    statusBar=Mock(),
                    inputFileEdit=Mock(),
                    outputText=Mock(),
                    pagesEdit=Mock()
                ):
                    ui = ExtractTextUI()
                    ui.current_file = None
                    ui.extract_text()
                    
                    mock_logger.warning.assert_called()
                    mock_msg.warning.assert_called()
    
    def test_extract_text_invalid_pages(self, qapp, mock_ui_file, mock_logger):
        """Test text extraction with invalid page format."""
        with patch('extract_text.QMessageBox') as mock_msg:
            with patch.object(ExtractTextUI, 'show'):
                with patch.multiple(
                    ExtractTextUI,
                    browseButton=Mock(),
                    extractButton=Mock(),
                    saveButton=Mock(),
                    actionExit=Mock(),
                    statusBar=Mock(),
                    inputFileEdit=Mock(),
                    outputText=Mock(),
                    pagesEdit=Mock()
                ):
                    ui = ExtractTextUI()
                    ui.current_file = "/path/to/test.pdf"
                    ui.pagesEdit.text.return_value = "invalid,pages"
                    ui.extract_text()
                    
                    mock_logger.error.assert_called()
                    mock_msg.warning.assert_called()
    
    @patch('extract_text.extract_text_from_pdf')
    def test_extract_text_success(self, mock_extract, qapp, mock_ui_file, mock_logger):
        """Test successful text extraction."""
        mock_extract.return_value = "Extracted text content"
        
        with patch.object(ExtractTextUI, 'show'):
            with patch('extract_text.QtWidgets.QApplication.processEvents'):
                with patch.multiple(
                    ExtractTextUI,
                    browseButton=Mock(),
                    extractButton=Mock(),
                    saveButton=Mock(),
                    actionExit=Mock(),
                    statusBar=Mock(),
                    inputFileEdit=Mock(),
                    outputText=Mock(),
                    pagesEdit=Mock(),
                    progressBar=Mock()
                ):
                    ui = ExtractTextUI()
                    ui.current_file = "/path/to/test.pdf"
                    ui.pagesEdit.text.return_value = ""
                    ui.extract_text()
                    
                    ui.outputText.setPlainText.assert_called_with("Extracted text content")
                    ui.saveButton.setEnabled.assert_called_with(True)
                    mock_logger.info.assert_called()
    
    @patch('extract_text.extract_text_from_pdf')
    def test_extract_text_failure(self, mock_extract, qapp, mock_ui_file, mock_logger):
        """Test text extraction failure."""
        mock_extract.return_value = False
        
        with patch('extract_text.QMessageBox') as mock_msg:
            with patch.object(ExtractTextUI, 'show'):
                with patch('extract_text.QtWidgets.QApplication.processEvents'):
                    with patch.multiple(
                        ExtractTextUI,
                        browseButton=Mock(),
                        extractButton=Mock(),
                        saveButton=Mock(),
                        actionExit=Mock(),
                        statusBar=Mock(),
                        inputFileEdit=Mock(),
                        outputText=Mock(),
                        pagesEdit=Mock(),
                        progressBar=Mock()
                    ):
                        ui = ExtractTextUI()
                        ui.current_file = "/path/to/test.pdf"
                        ui.pagesEdit.text.return_value = ""
                        ui.extract_text()
                        
                        mock_logger.warning.assert_called()
                        mock_msg.warning.assert_called()
    
    @patch('extract_text.extract_text_from_pdf')
    def test_extract_text_with_pages(self, mock_extract, qapp, mock_ui_file, mock_logger):
        """Test text extraction with specific pages."""
        mock_extract.return_value = "Page specific content"
        
        with patch.object(ExtractTextUI, 'show'):
            with patch('extract_text.QtWidgets.QApplication.processEvents'):
                with patch.multiple(
                    ExtractTextUI,
                    browseButton=Mock(),
                    extractButton=Mock(),
                    saveButton=Mock(),
                    actionExit=Mock(),
                    statusBar=Mock(),
                    inputFileEdit=Mock(),
                    outputText=Mock(),
                    pagesEdit=Mock(),
                    progressBar=Mock()
                ):
                    ui = ExtractTextUI()
                    ui.current_file = "/path/to/test.pdf"
                    ui.pagesEdit.text.return_value = "1,3,5"
                    ui.extract_text()
                    
                    # Check that pages parameter was passed correctly
                    mock_extract.assert_called_with("/path/to/test.pdf", pages=(0, 2, 4))
                    mock_logger.info.assert_called()
    
    @patch('extract_text.extract_text_from_pdf')
    def test_extract_text_exception(self, mock_extract, qapp, mock_ui_file, mock_logger):
        """Test text extraction with exception."""
        mock_extract.side_effect = Exception("Extraction error")
        
        with patch('extract_text.QMessageBox') as mock_msg:
            with patch.object(ExtractTextUI, 'show'):
                with patch('extract_text.QtWidgets.QApplication.processEvents'):
                    with patch.multiple(
                        ExtractTextUI,
                        browseButton=Mock(),
                        extractButton=Mock(),
                        saveButton=Mock(),
                        actionExit=Mock(),
                        statusBar=Mock(),
                        inputFileEdit=Mock(),
                        outputText=Mock(),
                        pagesEdit=Mock(),
                        progressBar=Mock()
                    ):
                        ui = ExtractTextUI()
                        ui.current_file = "/path/to/test.pdf"
                        ui.pagesEdit.text.return_value = ""
                        ui.extract_text()
                        
                        mock_logger.error.assert_called()
                        mock_msg.critical.assert_called()
    
    def test_save_text_no_content(self, qapp, mock_ui_file, mock_logger):
        """Test saving text without content."""
        with patch('extract_text.QMessageBox') as mock_msg:
            with patch.object(ExtractTextUI, 'show'):
                with patch.multiple(
                    ExtractTextUI,
                    browseButton=Mock(),
                    extractButton=Mock(),
                    saveButton=Mock(),
                    actionExit=Mock(),
                    statusBar=Mock(),
                    inputFileEdit=Mock(),
                    outputText=Mock(),
                    pagesEdit=Mock()
                ):
                    ui = ExtractTextUI()
                    ui.outputText.toPlainText.return_value = ""
                    ui.save_text()
                    
                    mock_logger.warning.assert_called()
                    mock_msg.warning.assert_called()
    
    def test_save_text_success(self, qapp, mock_ui_file, mock_logger):
        """Test successful text saving."""
        with patch('extract_text.QFileDialog.getSaveFileName') as mock_dialog:
            mock_dialog.return_value = ("/path/to/output.txt", "Text Files (*.txt)")
            
            with patch('builtins.open', mock_open()) as mock_file:
                with patch('extract_text.QMessageBox') as mock_msg:
                    with patch.object(ExtractTextUI, 'show'):
                        with patch('extract_text.QtWidgets.QApplication.processEvents'):
                            with patch.multiple(
                                ExtractTextUI,
                                browseButton=Mock(),
                                extractButton=Mock(),
                                saveButton=Mock(),
                                actionExit=Mock(),
                                statusBar=Mock(),
                                inputFileEdit=Mock(),
                                outputText=Mock(),
                                pagesEdit=Mock(),
                                progressBar=Mock()
                            ):
                                ui = ExtractTextUI()
                                ui.outputText.toPlainText.return_value = "Sample text to save"
                                ui.save_text()
                                
                                mock_file.assert_called_with("/path/to/output.txt", 'w', encoding='utf-8')
                                mock_logger.info.assert_called()
                                mock_msg.information.assert_called()
    
    def test_save_text_cancelled(self, qapp, mock_ui_file, mock_logger):
        """Test text saving when user cancels."""
        with patch('extract_text.QFileDialog.getSaveFileName') as mock_dialog:
            mock_dialog.return_value = ("", "")
            
            with patch.object(ExtractTextUI, 'show'):
                with patch.multiple(
                    ExtractTextUI,
                    browseButton=Mock(),
                    extractButton=Mock(),
                    saveButton=Mock(),
                    actionExit=Mock(),
                    statusBar=Mock(),
                    inputFileEdit=Mock(),
                    outputText=Mock(),
                    pagesEdit=Mock()
                ):
                    ui = ExtractTextUI()
                    ui.outputText.toPlainText.return_value = "Sample text"
                    ui.save_text()
                    
                    # Should not attempt to write file
                    mock_logger.warning.assert_not_called()
    
    def test_save_text_write_error(self, qapp, mock_ui_file, mock_logger):
        """Test text saving with write error."""
        with patch('extract_text.QFileDialog.getSaveFileName') as mock_dialog:
            mock_dialog.return_value = ("/path/to/output.txt", "Text Files (*.txt)")
            
            with patch('builtins.open', side_effect=PermissionError("Cannot write")):
                with patch('extract_text.QMessageBox') as mock_msg:
                    with patch.object(ExtractTextUI, 'show'):
                        with patch('extract_text.QtWidgets.QApplication.processEvents'):
                            with patch.multiple(
                                ExtractTextUI,
                                browseButton=Mock(),
                                extractButton=Mock(),
                                saveButton=Mock(),
                                actionExit=Mock(),
                                statusBar=Mock(),
                                inputFileEdit=Mock(),
                                outputText=Mock(),
                                pagesEdit=Mock(),
                                progressBar=Mock()
                            ):
                                ui = ExtractTextUI()
                                ui.outputText.toPlainText.return_value = "Sample text"
                                ui.save_text()
                                
                                mock_logger.error.assert_called()
                                mock_msg.critical.assert_called()
    
    def test_save_text_exception(self, qapp, mock_ui_file, mock_logger):
        """Test text saving with unexpected exception."""
        with patch('extract_text.QFileDialog.getSaveFileName', side_effect=Exception("Dialog error")):
            with patch('extract_text.QMessageBox') as mock_msg:
                with patch.object(ExtractTextUI, 'show'):
                    with patch.multiple(
                        ExtractTextUI,
                        browseButton=Mock(),
                        extractButton=Mock(),
                        saveButton=Mock(),
                        actionExit=Mock(),
                        statusBar=Mock(),
                        inputFileEdit=Mock(),
                        outputText=Mock(),
                        pagesEdit=Mock()
                    ):
                        ui = ExtractTextUI()
                        ui.outputText.toPlainText.return_value = "Sample text"
                        ui.save_text()
                        
                        mock_logger.error.assert_called()
                        mock_msg.critical.assert_called()


class TestMainFunction:
    """Test main function."""
    
    @patch('extract_text.QtWidgets.QApplication')
    @patch('extract_text.ExtractTextUI')
    def test_main_success(self, mock_ui, mock_app_class, mock_logger):
        """Test successful main function execution."""
        mock_app = Mock()
        mock_app.exec_.return_value = 0
        mock_app_class.return_value = mock_app
        
        mock_ui_instance = Mock()
        mock_ui.return_value = mock_ui_instance
        
        with patch('sys.exit') as mock_exit:
            main()
            
            mock_app_class.assert_called_once()
            mock_ui.assert_called_once()
            mock_app.exec_.assert_called_once()
            mock_exit.assert_called_with(0)
            mock_logger.info.assert_called()
    
    @patch('extract_text.QtWidgets.QApplication')
    def test_main_ui_init_failure(self, mock_app_class, mock_logger):
        """Test main function with UI initialization failure."""
        mock_app = Mock()
        mock_app_class.return_value = mock_app
        
        with patch('extract_text.ExtractTextUI', side_effect=Exception("UI init error")):
            with patch('extract_text.QMessageBox') as mock_msg:
                with patch('sys.exit') as mock_exit:
                    main()
                    
                    mock_logger.critical.assert_called()
                    mock_msg.critical.assert_called()
                    mock_exit.assert_called_with(1)
    
    @patch('extract_text.QtWidgets.QApplication')
    @patch('extract_text.ExtractTextUI')
    def test_main_app_execution_failure(self, mock_ui, mock_app_class, mock_logger):
        """Test main function with application execution failure."""
        mock_app = Mock()
        mock_app.exec_.side_effect = Exception("App execution error")
        mock_app_class.return_value = mock_app
        
        with patch('extract_text.QMessageBox') as mock_msg:
            with patch('sys.exit') as mock_exit:
                main()
                
                mock_logger.critical.assert_called()
                mock_msg.critical.assert_called()
                mock_exit.assert_called_with(1)


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_extract_text_unicode_content(self):
        """Test extraction with Unicode content."""
        with patch('extract_text.os.path.exists', return_value=True):
            with patch('extract_text.pdfplumber.open') as mock_pdf_open:
                # Mock page with Unicode content
                mock_page = Mock()
                mock_page.extract_text.return_value = "文字 テスト Тест 🚀"
                
                mock_pdf = Mock()
                mock_pdf.pages = [mock_page]
                mock_pdf.__enter__.return_value = mock_pdf
                mock_pdf.__exit__.return_value = None
                
                mock_pdf_open.return_value = mock_pdf
                
                result = extract_text_from_pdf("test.pdf")
                
                assert isinstance(result, str)
                assert "文字 テスト Тест 🚀" in result
    
    def test_extract_text_very_large_page_range(self):
        """Test extraction with very large page range."""
        with patch('extract_text.os.path.exists', return_value=True):
            with patch('extract_text.pdfplumber.open') as mock_pdf_open:
                # Mock PDF with only 2 pages
                pages = [Mock(), Mock()]
                for i, page in enumerate(pages):
                    page.extract_text.return_value = f"Page {i+1}"
                
                mock_pdf = Mock()
                mock_pdf.pages = pages
                mock_pdf.__enter__.return_value = mock_pdf
                mock_pdf.__exit__.return_value = None
                
                mock_pdf_open.return_value = mock_pdf
                
                # Request pages 1-100
                result = extract_text_from_pdf("test.pdf", pages="1-100")
                
                assert isinstance(result, str)
                assert "Page 1" in result
                assert "Page 2" in result
    
    def test_extract_text_negative_page_numbers(self):
        """Test extraction with negative page numbers."""
        with patch('extract_text.os.path.exists', return_value=True):
            with patch('extract_text.QMessageBox') as mock_msg:
                result = extract_text_from_pdf("test.pdf", pages="-1,0,1")
                
                assert result is False
                mock_msg.critical.assert_called()
    
    def test_extract_text_empty_page_range(self):
        """Test extraction with empty page range."""
        with patch('extract_text.os.path.exists', return_value=True):
            with patch('extract_text.pdfplumber.open') as mock_pdf_open:
                mock_page = Mock()
                mock_page.extract_text.return_value = "Sample text"
                
                mock_pdf = Mock()
                mock_pdf.pages = [mock_page]
                mock_pdf.__enter__.return_value = mock_pdf
                mock_pdf.__exit__.return_value = None
                
                mock_pdf_open.return_value = mock_pdf
                
                # Empty pages string should extract all pages
                result = extract_text_from_pdf("test.pdf", pages="")
                
                assert isinstance(result, str)
                assert "Sample text" in result
    
    def test_concurrent_extractions(self):
        """Test concurrent text extractions."""
        results = []
        
        def extract_worker(file_id):
            with patch('extract_text.os.path.exists', return_value=True):
                with patch('extract_text.pdfplumber.open') as mock_pdf_open:
                    mock_page = Mock()
                    mock_page.extract_text.return_value = f"Content from file {file_id}"
                    
                    mock_pdf = Mock()
                    mock_pdf.pages = [mock_page]
                    mock_pdf.__enter__.return_value = mock_pdf
                    mock_pdf.__exit__.return_value = None
                    
                    mock_pdf_open.return_value = mock_pdf
                    
                    result = extract_text_from_pdf(f"test{file_id}.pdf")
                    results.append((file_id, result))
        
        # Start multiple extraction threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=extract_worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all extractions completed
        assert len(results) == 3
        for file_id, result in results:
            assert isinstance(result, str)
            assert f"Content from file {file_id}" in result
    
    def test_memory_stress_large_text(self):
        """Test extraction with very large text content."""
        with patch('extract_text.os.path.exists', return_value=True):
            with patch('extract_text.pdfplumber.open') as mock_pdf_open:
                # Mock page with large content (1MB of text)
                large_content = "A" * (1024 * 1024)
                mock_page = Mock()
                mock_page.extract_text.return_value = large_content
                
                mock_pdf = Mock()
                mock_pdf.pages = [mock_page]
                mock_pdf.__enter__.return_value = mock_pdf
                mock_pdf.__exit__.return_value = None
                
                mock_pdf_open.return_value = mock_pdf
                
                result = extract_text_from_pdf("large_test.pdf")
                
                assert isinstance(result, str)
                assert len(result) > 1024 * 1024  # Should include headers and content


# Test configuration and fixtures for pytest
@pytest.fixture(scope="session")
def test_session_info():
    """Provide test session information."""
    return {
        "start_time": datetime.now(),
        "test_file": "test_extract_text_2025-08-28.py",
        "target_module": "extract_text.py"
    }


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "gui: mark test as GUI test requiring display"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names."""
    for item in items:
        # Mark integration tests
        if "integration" in item.name.lower():
            item.add_marker(pytest.mark.integration)
        
        # Mark slow tests
        if any(keyword in item.name.lower() for keyword in ["concurrent", "thread", "stress", "large"]):
            item.add_marker(pytest.mark.slow)
        
        # Mark GUI tests
        if any(keyword in item.name.lower() for keyword in ["ui", "gui", "widget", "dialog"]):
            item.add_marker(pytest.mark.gui)


if __name__ == "__main__":
    # Run tests when script is executed directly
    pytest.main([__file__, "-v", "--tb=short"])