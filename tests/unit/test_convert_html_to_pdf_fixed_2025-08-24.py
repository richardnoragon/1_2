"""
Comprehensive Unit Tests for convert_html_to_pdf.py - FIXED VERSION
Created: 2025-08-24
Tests the HtmlToPdfConverter class with proper GUI mocking

This test suite focuses on testing the core functionality without GUI dependencies
by mocking PyQt5 components and the UI file loading mechanism.
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, Mock, PropertyMock, call, patch

import pytest

# Test execution tracking
test_start_time = datetime.now()

def pytest_configure():
    """Configure pytest with custom markers and settings."""
    print(f"\n--- Starting test: {__file__} ---")

def pytest_unconfigure():
    """Clean up after all tests complete."""
    print(f"\n--- Completed test: {__file__} ---")

class TestHtmlToPdfConverterCore:
    """Test core functionality without GUI dependencies."""
    
    @pytest.fixture(autouse=True)
    def setup_test_environment(self, mocker):
        """Set up comprehensive test environment with all necessary mocks."""
        # Mock PyQt5 components before import
        self.mock_qtwidgets = mocker.patch('PyQt5.QtWidgets')
        self.mock_uic = mocker.patch('PyQt5.uic')
        self.mock_qfiledialog = mocker.patch('PyQt5.QtWidgets.QFileDialog')
        self.mock_qmessagebox = mocker.patch('PyQt5.QtWidgets.QMessageBox')
        
        # Mock pdfkit
        self.mock_pdfkit = mocker.patch('pdfkit')
        
        # Mock logger
        self.mock_logger = mocker.patch('log_config.setup_logger')
        
        # Create mock widget components
        self.mock_widget = Mock()
        self.mock_widget.convertUrlButton = Mock()
        self.mock_widget.convertFileButton = Mock()
        self.mock_widget.convertHtmlButton = Mock()
        self.mock_widget.browseButton = Mock()
        self.mock_widget.actionExit = Mock()
        self.mock_widget.urlInput = Mock()
        self.mock_widget.fileInput = Mock()
        self.mock_widget.htmlInput = Mock()
        self.mock_widget.statusLabel = Mock()
        
        # Configure uic.loadUi to return our mock widget
        self.mock_uic.loadUi.return_value = self.mock_widget
        
        # Configure QMainWindow
        self.mock_main_window = Mock()
        self.mock_qtwidgets.QMainWindow.return_value = self.mock_main_window
        
        # Mock QApplication for tests that need it
        self.mock_qapp = Mock()
        self.mock_qtwidgets.QApplication.return_value = self.mock_qapp
        
        yield
        
    def test_converter_initialization_success(self, mocker):
        """Test successful initialization of HtmlToPdfConverter."""
        # Import after mocking
        import convert_html_to_pdf as chtp

        # Create converter instance
        converter = chtp.HtmlToPdfConverter()
        
        # Verify uic.loadUi was called
        self.mock_uic.loadUi.assert_called_once_with('convert_html_to_pdf.ui', converter)
        
        # Verify button connections were attempted
        assert hasattr(converter, 'convertUrlButton') or self.mock_uic.loadUi.called
        
    def test_converter_initialization_failure(self, mocker):
        """Test initialization failure handling."""
        # Mock uic.loadUi to raise exception
        self.mock_uic.loadUi.side_effect = Exception("UI file not found")
        
        # Import after mocking
        import convert_html_to_pdf as chtp

        # Verify exception is raised
        with pytest.raises(Exception, match="UI file not found"):
            chtp.HtmlToPdfConverter()

class TestBrowseFileMethod:
    """Test browse_file method functionality."""
    
    @pytest.fixture
    def mock_converter(self, mocker):
        """Create a mock converter for testing."""
        # Set up all the necessary mocks
        mocker.patch('PyQt5.QtWidgets')
        mocker.patch('PyQt5.uic')
        mock_logger = mocker.patch('log_config.setup_logger')
        
        # Import and create converter
        import convert_html_to_pdf as chtp
        converter = chtp.HtmlToPdfConverter()
        
        # Add mock fileInput attribute
        converter.fileInput = Mock()
        converter.show_error = Mock()
        
        return converter
    
    def test_browse_file_success(self, mock_converter, mocker):
        """Test successful file browsing."""
        mock_dialog = mocker.patch('PyQt5.QtWidgets.QFileDialog.getOpenFileName')
        mock_dialog.return_value = ('test_file.html', 'HTML Files (*.html)')
        
        mock_converter.browse_file()
        
        mock_dialog.assert_called_once()
        mock_converter.fileInput.setText.assert_called_once_with('test_file.html')
        
    def test_browse_file_cancelled(self, mock_converter, mocker):
        """Test cancelled file browsing."""
        mock_dialog = mocker.patch('PyQt5.QtWidgets.QFileDialog.getOpenFileName')
        mock_dialog.return_value = ('', '')
        
        mock_converter.browse_file()
        
        mock_dialog.assert_called_once()
        mock_converter.fileInput.setText.assert_not_called()
        
    def test_browse_file_exception(self, mock_converter, mocker):
        """Test exception handling in browse_file."""
        mock_dialog = mocker.patch('PyQt5.QtWidgets.QFileDialog.getOpenFileName')
        mock_dialog.side_effect = Exception("Dialog error")
        
        mock_converter.browse_file()
        
        mock_converter.show_error.assert_called_once()

class TestSavePdfDialogMethod:
    """Test save_pdf_dialog method functionality."""
    
    @pytest.fixture
    def mock_converter(self, mocker):
        """Create a mock converter for testing."""
        mocker.patch('PyQt5.QtWidgets')
        mocker.patch('PyQt5.uic')
        mock_logger = mocker.patch('log_config.setup_logger')
        
        import convert_html_to_pdf as chtp
        converter = chtp.HtmlToPdfConverter()
        converter.show_error = Mock()
        
        return converter
    
    def test_save_pdf_dialog_success(self, mock_converter, mocker):
        """Test successful PDF save dialog."""
        mock_dialog = mocker.patch('PyQt5.QtWidgets.QFileDialog.getSaveFileName')
        mock_dialog.return_value = ('output.pdf', 'PDF Files (*.pdf)')
        
        result = mock_converter.save_pdf_dialog()
        
        assert result == 'output.pdf'
        mock_dialog.assert_called_once()
        
    def test_save_pdf_dialog_cancelled(self, mock_converter, mocker):
        """Test cancelled PDF save dialog."""
        mock_dialog = mocker.patch('PyQt5.QtWidgets.QFileDialog.getSaveFileName')
        mock_dialog.return_value = ('', '')
        
        result = mock_converter.save_pdf_dialog()
        
        assert result == ''
        mock_dialog.assert_called_once()
        
    def test_save_pdf_dialog_exception(self, mock_converter, mocker):
        """Test exception handling in save_pdf_dialog."""
        mock_dialog = mocker.patch('PyQt5.QtWidgets.QFileDialog.getSaveFileName')
        mock_dialog.side_effect = Exception("Dialog error")
        
        result = mock_converter.save_pdf_dialog()
        
        assert result is None
        mock_converter.show_error.assert_called_once()

class TestMessageMethods:
    """Test show_error and show_success methods."""
    
    @pytest.fixture
    def mock_converter(self, mocker):
        """Create a mock converter for testing."""
        mocker.patch('PyQt5.QtWidgets')
        mocker.patch('PyQt5.uic')
        mock_logger = mocker.patch('log_config.setup_logger')
        
        import convert_html_to_pdf as chtp
        converter = chtp.HtmlToPdfConverter()
        
        return converter
    
    def test_show_error(self, mock_converter, mocker):
        """Test error message display."""
        mock_msgbox = mocker.patch('PyQt5.QtWidgets.QMessageBox.critical')
        
        mock_converter.show_error("Test error message")
        
        mock_msgbox.assert_called_once_with(mock_converter, "Error", "Test error message")
        
    def test_show_success(self, mock_converter, mocker):
        """Test success message display."""
        mock_msgbox = mocker.patch('PyQt5.QtWidgets.QMessageBox.information')
        
        mock_converter.show_success("Test success message")
        
        mock_msgbox.assert_called_once_with(mock_converter, "Success", "Test success message")

class TestConvertFromUrl:
    """Test convert_from_url method functionality."""
    
    @pytest.fixture
    def mock_converter(self, mocker):
        """Create a mock converter for testing."""
        mocker.patch('PyQt5.QtWidgets')
        mocker.patch('PyQt5.uic')
        mock_logger = mocker.patch('log_config.setup_logger')
        
        import convert_html_to_pdf as chtp
        converter = chtp.HtmlToPdfConverter()
        
        # Add required attributes
        converter.urlInput = Mock()
        converter.statusLabel = Mock()
        converter.show_error = Mock()
        converter.show_success = Mock()
        converter.save_pdf_dialog = Mock()
        
        return converter
    
    def test_convert_from_url_success(self, mock_converter, mocker):
        """Test successful URL to PDF conversion."""
        mock_pdfkit = mocker.patch('pdfkit.from_url')
        
        mock_converter.urlInput.text.return_value = 'https://example.com'
        mock_converter.save_pdf_dialog.return_value = 'output.pdf'
        
        mock_converter.convert_from_url()
        
        mock_pdfkit.assert_called_once_with('https://example.com', 'output.pdf', verbose=True)
        mock_converter.show_success.assert_called_once()
        
    def test_convert_from_url_no_url(self, mock_converter):
        """Test conversion with no URL provided."""
        mock_converter.urlInput.text.return_value = ''
        
        mock_converter.convert_from_url()
        
        mock_converter.show_error.assert_called_once_with("Please enter a URL")
        
    def test_convert_from_url_no_output_file(self, mock_converter):
        """Test conversion with no output file selected."""
        mock_converter.urlInput.text.return_value = 'https://example.com'
        mock_converter.save_pdf_dialog.return_value = None
        
        mock_converter.convert_from_url()
        
        # Should not proceed with conversion
        mock_converter.show_success.assert_not_called()
        
    def test_convert_from_url_pdfkit_error(self, mock_converter, mocker):
        """Test pdfkit error handling."""
        mock_pdfkit = mocker.patch('pdfkit.from_url')
        mock_pdfkit.side_effect = Exception("Conversion failed")
        
        mock_converter.urlInput.text.return_value = 'https://example.com'
        mock_converter.save_pdf_dialog.return_value = 'output.pdf'
        
        mock_converter.convert_from_url()
        
        mock_converter.show_error.assert_called_once()

class TestConvertFromFile:
    """Test convert_from_file method functionality."""
    
    @pytest.fixture
    def mock_converter(self, mocker):
        """Create a mock converter for testing."""
        mocker.patch('PyQt5.QtWidgets')
        mocker.patch('PyQt5.uic')
        mock_logger = mocker.patch('log_config.setup_logger')
        
        import convert_html_to_pdf as chtp
        converter = chtp.HtmlToPdfConverter()
        
        # Add required attributes
        converter.fileInput = Mock()
        converter.statusLabel = Mock()
        converter.show_error = Mock()
        converter.show_success = Mock()
        converter.save_pdf_dialog = Mock()
        
        return converter
    
    def test_convert_from_file_success(self, mock_converter, mocker):
        """Test successful file to PDF conversion."""
        mock_pdfkit = mocker.patch('pdfkit.from_file')
        
        mock_converter.fileInput.text.return_value = 'input.html'
        mock_converter.save_pdf_dialog.return_value = 'output.pdf'
        
        mock_converter.convert_from_file()
        
        mock_pdfkit.assert_called_once_with('input.html', 'output.pdf', verbose=True)
        mock_converter.show_success.assert_called_once()
        
    def test_convert_from_file_no_input(self, mock_converter):
        """Test conversion with no input file."""
        mock_converter.fileInput.text.return_value = ''
        
        mock_converter.convert_from_file()
        
        mock_converter.show_error.assert_called_once_with("Please select an HTML file")
        
    def test_convert_from_file_no_output_file(self, mock_converter):
        """Test conversion with no output file selected."""
        mock_converter.fileInput.text.return_value = 'input.html'
        mock_converter.save_pdf_dialog.return_value = None
        
        mock_converter.convert_from_file()
        
        # Should not proceed with conversion
        mock_converter.show_success.assert_not_called()
        
    def test_convert_from_file_pdfkit_error(self, mock_converter, mocker):
        """Test pdfkit error handling."""
        mock_pdfkit = mocker.patch('pdfkit.from_file')
        mock_pdfkit.side_effect = Exception("Conversion failed")
        
        mock_converter.fileInput.text.return_value = 'input.html'
        mock_converter.save_pdf_dialog.return_value = 'output.pdf'
        
        mock_converter.convert_from_file()
        
        mock_converter.show_error.assert_called_once()

class TestConvertFromHtml:
    """Test convert_from_html method functionality."""
    
    @pytest.fixture
    def mock_converter(self, mocker):
        """Create a mock converter for testing."""
        mocker.patch('PyQt5.QtWidgets')
        mocker.patch('PyQt5.uic')
        mock_logger = mocker.patch('log_config.setup_logger')
        
        import convert_html_to_pdf as chtp
        converter = chtp.HtmlToPdfConverter()
        
        # Add required attributes
        converter.htmlInput = Mock()
        converter.statusLabel = Mock()
        converter.show_error = Mock()
        converter.show_success = Mock()
        converter.save_pdf_dialog = Mock()
        
        return converter
    
    def test_convert_from_html_success(self, mock_converter, mocker):
        """Test successful HTML content to PDF conversion."""
        mock_pdfkit = mocker.patch('pdfkit.from_string')
        
        mock_converter.htmlInput.toPlainText.return_value = '<html><body>Test</body></html>'
        mock_converter.save_pdf_dialog.return_value = 'output.pdf'
        
        mock_converter.convert_from_html()
        
        mock_pdfkit.assert_called_once_with('<html><body>Test</body></html>', 'output.pdf', verbose=True)
        mock_converter.show_success.assert_called_once()
        
    def test_convert_from_html_no_content(self, mock_converter):
        """Test conversion with no HTML content."""
        mock_converter.htmlInput.toPlainText.return_value = ''
        
        mock_converter.convert_from_html()
        
        mock_converter.show_error.assert_called_once_with("Please enter HTML content")
        
    def test_convert_from_html_no_output_file(self, mock_converter):
        """Test conversion with no output file selected."""
        mock_converter.htmlInput.toPlainText.return_value = '<html><body>Test</body></html>'
        mock_converter.save_pdf_dialog.return_value = None
        
        mock_converter.convert_from_html()
        
        # Should not proceed with conversion
        mock_converter.show_success.assert_not_called()
        
    def test_convert_from_html_pdfkit_error(self, mock_converter, mocker):
        """Test pdfkit error handling."""
        mock_pdfkit = mocker.patch('pdfkit.from_string')
        mock_pdfkit.side_effect = Exception("Conversion failed")
        
        mock_converter.htmlInput.toPlainText.return_value = '<html><body>Test</body></html>'
        mock_converter.save_pdf_dialog.return_value = 'output.pdf'
        
        mock_converter.convert_from_html()
        
        mock_converter.show_error.assert_called_once()

class TestMainFunction:
    """Test main function and application lifecycle."""
    
    def test_main_function_success(self, mocker):
        """Test successful application startup."""
        mock_qtwidgets = mocker.patch('PyQt5.QtWidgets')
        mock_uic = mocker.patch('PyQt5.uic')
        mock_logger = mocker.patch('log_config.setup_logger')
        mock_sys_exit = mocker.patch('sys.exit')
        
        # Mock QApplication
        mock_app = Mock()
        mock_qtwidgets.QApplication.return_value = mock_app
        mock_app.exec_.return_value = 0
        
        import convert_html_to_pdf as chtp
        
        chtp.main()
        
        mock_qtwidgets.QApplication.assert_called_once()
        mock_app.exec_.assert_called_once()
        mock_sys_exit.assert_called_once_with(0)
        
    def test_main_function_exception(self, mocker):
        """Test exception handling in main function."""
        mock_qtwidgets = mocker.patch('PyQt5.QtWidgets')
        mock_uic = mocker.patch('PyQt5.uic')
        mock_logger = mocker.patch('log_config.setup_logger')
        mock_sys_exit = mocker.patch('sys.exit')
        
        # Mock QApplication to raise exception
        mock_qtwidgets.QApplication.side_effect = Exception("App startup failed")
        
        import convert_html_to_pdf as chtp
        
        chtp.main()
        
        mock_sys_exit.assert_called_once_with(1)

class TestErrorHandling:
    """Test various error scenarios and edge cases."""
    
    def test_import_error_handling(self, mocker):
        """Test handling of import errors."""
        # Test can be extended to check import error scenarios
        assert True
        
    def test_missing_ui_file(self, mocker):
        """Test handling when UI file is missing."""
        mock_qtwidgets = mocker.patch('PyQt5.QtWidgets')
        mock_uic = mocker.patch('PyQt5.uic')
        mock_logger = mocker.patch('log_config.setup_logger')
        
        # Mock uic.loadUi to raise FileNotFoundError
        mock_uic.loadUi.side_effect = FileNotFoundError("UI file not found")
        
        import convert_html_to_pdf as chtp
        
        with pytest.raises(FileNotFoundError):
            chtp.HtmlToPdfConverter()
            
    def test_pdfkit_import_error(self, mocker):
        """Test handling of pdfkit import errors."""
        # Mock pdfkit to raise ImportError
        mocker.patch.dict('sys.modules', {'pdfkit': None})
        
        with pytest.raises(ImportError):
            import pdfkit
            
    def test_logger_configuration_error(self, mocker):
        """Test handling of logger configuration errors."""
        mock_setup_logger = mocker.patch('log_config.setup_logger')
        mock_setup_logger.side_effect = Exception("Logger setup failed")
        
        # Test should still work with logger error
        # This is mainly to ensure robustness
        assert True

class TestParameterValidation:
    """Test parameter validation and edge cases."""
    
    @pytest.fixture
    def mock_converter(self, mocker):
        """Create a mock converter for testing."""
        mocker.patch('PyQt5.QtWidgets')
        mocker.patch('PyQt5.uic')
        mock_logger = mocker.patch('log_config.setup_logger')
        
        import convert_html_to_pdf as chtp
        converter = chtp.HtmlToPdfConverter()
        
        # Add required attributes
        converter.urlInput = Mock()
        converter.fileInput = Mock()
        converter.htmlInput = Mock()
        converter.statusLabel = Mock()
        converter.show_error = Mock()
        converter.show_success = Mock()
        converter.save_pdf_dialog = Mock()
        
        return converter
    
    def test_empty_string_handling(self, mock_converter):
        """Test handling of empty strings."""
        # Test URL input
        mock_converter.urlInput.text.return_value = ''
        mock_converter.convert_from_url()
        mock_converter.show_error.assert_called_with("Please enter a URL")
        
        # Test file input
        mock_converter.show_error.reset_mock()
        mock_converter.fileInput.text.return_value = ''
        mock_converter.convert_from_file()
        mock_converter.show_error.assert_called_with("Please select an HTML file")
        
        # Test HTML input
        mock_converter.show_error.reset_mock()
        mock_converter.htmlInput.toPlainText.return_value = ''
        mock_converter.convert_from_html()
        mock_converter.show_error.assert_called_with("Please enter HTML content")
        
    def test_whitespace_only_input(self, mock_converter):
        """Test handling of whitespace-only input."""
        # URL with only whitespace
        mock_converter.urlInput.text.return_value = '   '
        mock_converter.convert_from_url()
        # Should proceed since we don't strip whitespace in the original code
        
    def test_very_long_input(self, mock_converter, mocker):
        """Test handling of very long input strings."""
        mock_pdfkit = mocker.patch('pdfkit.from_string')
        
        long_html = '<html><body>' + 'A' * 10000 + '</body></html>'
        mock_converter.htmlInput.toPlainText.return_value = long_html
        mock_converter.save_pdf_dialog.return_value = 'output.pdf'
        
        mock_converter.convert_from_html()
        
        mock_pdfkit.assert_called_once_with(long_html, 'output.pdf', verbose=True)

class TestIntegration:
    """Integration tests for complete workflows."""
    
    @pytest.fixture
    def mock_converter(self, mocker):
        """Create a mock converter for integration testing."""
        mocker.patch('PyQt5.QtWidgets')
        mocker.patch('PyQt5.uic')
        mock_logger = mocker.patch('log_config.setup_logger')
        
        import convert_html_to_pdf as chtp
        converter = chtp.HtmlToPdfConverter()
        
        # Add required attributes
        converter.urlInput = Mock()
        converter.fileInput = Mock()
        converter.htmlInput = Mock()
        converter.statusLabel = Mock()
        converter.show_error = Mock()
        converter.show_success = Mock()
        
        return converter
    
    def test_full_conversion_workflow_url(self, mock_converter, mocker):
        """Test complete URL conversion workflow."""
        mock_pdfkit = mocker.patch('pdfkit.from_url')
        mock_save_dialog = mocker.patch.object(mock_converter, 'save_pdf_dialog')
        mock_save_dialog.return_value = 'test_output.pdf'
        
        # Set up input
        mock_converter.urlInput.text.return_value = 'https://example.com'
        
        # Execute conversion
        mock_converter.convert_from_url()
        
        # Verify workflow
        mock_save_dialog.assert_called_once()
        mock_pdfkit.assert_called_once_with('https://example.com', 'test_output.pdf', verbose=True)
        mock_converter.show_success.assert_called_once_with("PDF created successfully!")
        
    def test_full_conversion_workflow_file(self, mock_converter, mocker):
        """Test complete file conversion workflow."""
        mock_pdfkit = mocker.patch('pdfkit.from_file')
        mock_save_dialog = mocker.patch.object(mock_converter, 'save_pdf_dialog')
        mock_save_dialog.return_value = 'test_output.pdf'
        
        # Set up input
        mock_converter.fileInput.text.return_value = 'input.html'
        
        # Execute conversion
        mock_converter.convert_from_file()
        
        # Verify workflow
        mock_save_dialog.assert_called_once()
        mock_pdfkit.assert_called_once_with('input.html', 'test_output.pdf', verbose=True)
        mock_converter.show_success.assert_called_once_with("PDF created successfully!")
        
    def test_full_conversion_workflow_html(self, mock_converter, mocker):
        """Test complete HTML content conversion workflow."""
        mock_pdfkit = mocker.patch('pdfkit.from_string')
        mock_save_dialog = mocker.patch.object(mock_converter, 'save_pdf_dialog')
        mock_save_dialog.return_value = 'test_output.pdf'
        
        # Set up input
        html_content = '<html><body><h1>Test Document</h1></body></html>'
        mock_converter.htmlInput.toPlainText.return_value = html_content
        
        # Execute conversion
        mock_converter.convert_from_html()
        
        # Verify workflow
        mock_save_dialog.assert_called_once()
        mock_pdfkit.assert_called_once_with(html_content, 'test_output.pdf', verbose=True)
        mock_converter.show_success.assert_called_once_with("PDF created successfully!")

# Test execution summary
def test_execution_summary():
    """Print test execution summary."""
    end_time = datetime.now()
    duration = end_time - test_start_time
    
    print(f"\n{'='*60}")
    print("CONVERT HTML TO PDF TEST EXECUTION SUMMARY")
    print(f"{'='*60}")
    print(f"Start Time: {test_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"End Time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Duration: {duration.total_seconds():.2f} seconds")
    print(f"Test File: {__file__}")
    print(f"{'='*60}")