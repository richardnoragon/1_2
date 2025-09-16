"""
Comprehensive unit tests for convert_to_image.py
Created on: 2025-08-24
Test framework: pytest

Tests cover:
- convert_pdf2img function
- ConvertToImageUI class methods
- Error handling and edge cases
- File operations and validation
"""

import os
import shutil
import sys
import tempfile
from datetime import datetime
from unittest.mock import Mock, patch

import pytest

# Add the source directory to Python path
src_path = os.path.join(
    os.path.dirname(__file__), '..', '..', 'src', 'utilities',
    'pdf_tools', 'pdf_conversion'
)
sys.path.insert(0, src_path)

# Import the module under test
try:
    import convert_to_image
    from convert_to_image import ConvertToImageUI, convert_pdf2img
except ImportError as e:
    pytest.skip(f"Could not import convert_to_image module: {e}", allow_module_level=True)


class TestConvertPdf2Img:
    """Test class for convert_pdf2img function"""

    def setup_method(self):
        """Setup test environment before each test"""
        self.test_dir = tempfile.mkdtemp()
        self.test_pdf_path = os.path.join(self.test_dir, "test.pdf")
        self.mock_pdf_content = b"Mock PDF content"
        
        # Create a mock PDF file
        with open(self.test_pdf_path, "wb") as f:
            f.write(self.mock_pdf_content)

    def teardown_method(self):
        """Cleanup test environment after each test"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        
        # Clean up converted_images directory if it exists
        if os.path.exists("converted_images"):
            shutil.rmtree("converted_images")

    @patch('convert_to_image.fitz')
    @patch('convert_to_image.Image')
    @patch('convert_to_image.os.makedirs')
    def test_convert_pdf2img_success_all_pages(self, mock_makedirs,
                                               mock_image, mock_fitz):
        """Test successful conversion of all pages"""
        # Setup mocks
        mock_pdf = Mock()
        mock_fitz.open.return_value = mock_pdf
        
        # Configure mock PDF properly
        mock_pdf.__len__ = Mock(return_value=3)
        mock_pdf.close = Mock()
        
        mock_page = Mock()
        mock_pdf.__getitem__ = Mock(return_value=mock_page)
        
        mock_pixmap = Mock()
        mock_pixmap.width = 800
        mock_pixmap.height = 600
        mock_pixmap.samples = b"mock_image_data"
        mock_page.get_pixmap.return_value = mock_pixmap
        
        mock_pil_image = Mock()
        mock_image.frombytes.return_value = mock_pil_image
        
        # Execute test
        result = convert_pdf2img(self.test_pdf_path)
        
        # Assertions
        assert isinstance(result, list)
        assert len(result) == 3
        mock_fitz.open.assert_called_once_with(self.test_pdf_path)
        mock_pdf.close.assert_called_once()
        assert mock_pil_image.save.call_count == 3

    @patch('convert_to_image.fitz')
    @patch('convert_to_image.Image')
    def test_convert_pdf2img_specific_pages(self, mock_image, mock_fitz):
        """Test conversion of specific pages"""
        # Setup mocks
        mock_pdf = Mock()
        mock_fitz.open.return_value = mock_pdf
        mock_pdf.__len__ = Mock(return_value=5)
        mock_pdf.close = Mock()
        
        mock_page = Mock()
        mock_pdf.__getitem__ = Mock(return_value=mock_page)
        
        mock_pixmap = Mock()
        mock_pixmap.width = 800
        mock_pixmap.height = 600
        mock_pixmap.samples = b"mock_image_data"
        mock_page.get_pixmap.return_value = mock_pixmap
        
        mock_pil_image = Mock()
        mock_image.frombytes.return_value = mock_pil_image
        
        # Execute test with specific pages
        pages_to_convert = (0, 2, 4)  # Pages 1, 3, 5
        result = convert_pdf2img(self.test_pdf_path, pages_to_convert)
        
        # Assertions
        assert isinstance(result, list)
        assert len(result) == 3
        mock_fitz.open.assert_called_once_with(self.test_pdf_path)

    def test_convert_pdf2img_file_not_found(self):
        """Test behavior when input file doesn't exist"""
        non_existent_file = os.path.join(self.test_dir, "nonexistent.pdf")
        
        with pytest.raises(FileNotFoundError) as exc_info:
            convert_pdf2img(non_existent_file)
        
        assert "Input file not found" in str(exc_info.value)

    @patch('convert_to_image.fitz')
    def test_convert_pdf2img_pages_out_of_range(self, mock_fitz):
        """Test handling of page numbers out of range"""
        # Setup mocks
        mock_pdf = Mock()
        mock_fitz.open.return_value = mock_pdf
        mock_pdf.__len__.return_value = 2  # Only 2 pages
        
        mock_page = Mock()
        mock_pdf.__getitem__.return_value = mock_page
        
        mock_pixmap = Mock()
        mock_pixmap.width = 800
        mock_pixmap.height = 600
        mock_pixmap.samples = b"mock_image_data"
        mock_page.get_pixmap.return_value = mock_pixmap
        
        # Execute test with out-of-range pages
        pages_to_convert = (0, 1, 5)  # Page 6 is out of range
        result = convert_pdf2img(self.test_pdf_path, pages_to_convert)
        
        # Should skip out-of-range pages and continue
        assert isinstance(result, list)
        mock_fitz.open.assert_called_once_with(self.test_pdf_path)

    @patch('convert_to_image.fitz')
    def test_convert_pdf2img_fitz_exception(self, mock_fitz):
        """Test handling of PyMuPDF exceptions"""
        mock_fitz.open.side_effect = Exception("PDF parsing error")
        
        with pytest.raises(Exception) as exc_info:
            convert_pdf2img(self.test_pdf_path)
        
        assert "PDF parsing error" in str(exc_info.value)

    @patch('convert_to_image.fitz')
    @patch('convert_to_image.Image')
    def test_convert_pdf2img_page_conversion_error(self, mock_image,
                                                   mock_fitz):
        """Test handling of individual page conversion errors"""
        # Setup mocks
        mock_pdf = Mock()
        mock_fitz.open.return_value = mock_pdf
        mock_pdf.__len__.return_value = 2
        
        mock_page = Mock()
        mock_pdf.__getitem__.return_value = mock_page
        mock_page.get_pixmap.side_effect = Exception("Page conversion error")
        
        # Execute test - should continue despite page errors
        result = convert_pdf2img(self.test_pdf_path)
        
        # Should return empty list since all pages failed
        assert isinstance(result, list)
        assert len(result) == 0

    @patch('convert_to_image.os.path.exists')
    @patch('convert_to_image.os.makedirs')
    def test_convert_pdf2img_creates_output_directory(self, mock_makedirs,
                                                      mock_exists):
        """Test that output directory is created if it doesn't exist"""
        mock_exists.side_effect = lambda path: path != "converted_images"
        
        with patch('convert_to_image.fitz') as mock_fitz:
            mock_pdf = Mock()
            mock_fitz.open.return_value = mock_pdf
            # No pages to avoid further mocking
            mock_pdf.__len__.return_value = 0
            
            convert_pdf2img(self.test_pdf_path)
            
            mock_makedirs.assert_called_once_with("converted_images")


class TestConvertToImageUI:
    """Test class for ConvertToImageUI class"""

    def setup_method(self):
        """Setup test environment before each test"""
        self.test_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Cleanup test environment after each test"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    @patch('convert_to_image.QtWidgets.QApplication')
    @patch('convert_to_image.uic.loadUi')
    def test_init_success(self, mock_loadui, mock_qapp):
        """Test successful initialization of UI"""
        with patch.object(ConvertToImageUI, 'show'):
            # Mock UI elements
            mock_ui = Mock()
            mock_ui.browseButton = Mock()
            mock_ui.convertButton = Mock()
            mock_ui.actionExit = Mock()
            
            with patch.multiple(
                    ConvertToImageUI,
                    browseButton=mock_ui.browseButton,
                    convertButton=mock_ui.convertButton,
                    actionExit=mock_ui.actionExit):
                
                ui = ConvertToImageUI()
                
                # Verify signal connections were attempted
                mock_loadui.assert_called_once_with('convert_to_image.ui', ui)

    @patch('convert_to_image.QtWidgets.QApplication')
    @patch('convert_to_image.uic.loadUi')
    def test_init_failure(self, mock_loadui, mock_qapp):
        """Test initialization failure handling"""
        mock_loadui.side_effect = Exception("UI loading error")
        
        with pytest.raises(Exception) as exc_info:
            ConvertToImageUI()
        
        assert "UI loading error" in str(exc_info.value)

    @patch('convert_to_image.QFileDialog.getOpenFileName')
    def test_browse_file_success(self, mock_dialog):
        """Test successful file browsing"""
        mock_dialog.return_value = ("/path/to/test.pdf", "PDF Files (*.pdf)")
        
        with patch.object(ConvertToImageUI, '__init__', lambda x: None):
            ui = ConvertToImageUI()
            ui.inputFileEdit = Mock()
            
            ui.browse_file()
            
            expected_path = "/path/to/test.pdf"
            ui.inputFileEdit.setText.assert_called_once_with(expected_path)
            mock_dialog.assert_called_once()

    @patch('convert_to_image.QFileDialog.getOpenFileName')
    def test_browse_file_cancel(self, mock_dialog):
        """Test file browsing when user cancels"""
        mock_dialog.return_value = ("", "")
        
        with patch.object(ConvertToImageUI, '__init__', lambda x: None):
            ui = ConvertToImageUI()
            ui.inputFileEdit = Mock()
            
            ui.browse_file()
            
            # setText should not be called when no file is selected
            ui.inputFileEdit.setText.assert_not_called()

    @patch('convert_to_image.QFileDialog.getOpenFileName')
    @patch('convert_to_image.QMessageBox.critical')
    def test_browse_file_exception(self, mock_msgbox, mock_dialog):
        """Test file browsing exception handling"""
        mock_dialog.side_effect = Exception("Dialog error")
        
        with patch.object(ConvertToImageUI, '__init__', lambda x: None):
            ui = ConvertToImageUI()
            ui.inputFileEdit = Mock()
            
            ui.browse_file()
            
            mock_msgbox.assert_called_once()

    @patch('convert_to_image.convert_pdf2img')
    def test_convert_file_success(self, mock_convert):
        """Test successful file conversion"""
        mock_convert.return_value = ["image1.png", "image2.png"]
        
        with patch.object(ConvertToImageUI, '__init__', lambda x: None):
            ui = ConvertToImageUI()
            ui.inputFileEdit = Mock()
            ui.inputFileEdit.text.return_value = "/path/to/test.pdf"
            ui.pagesEdit = Mock()
            ui.pagesEdit.text.return_value = ""
            ui.outputText = Mock()
            
            ui.convert_file()
            
            ui.outputText.setText.assert_called_once()
            output_text = ui.outputText.setText.call_args[0][0]
            assert "Conversion completed successfully!" in output_text

    @patch('convert_to_image.QMessageBox.warning')
    def test_convert_file_no_input(self, mock_warning):
        """Test conversion when no input file is selected"""
        with patch.object(ConvertToImageUI, '__init__', lambda x: None):
            ui = ConvertToImageUI()
            ui.inputFileEdit = Mock()
            ui.inputFileEdit.text.return_value = ""
            
            ui.convert_file()
            
            mock_warning.assert_called_once()
            args = mock_warning.call_args[0]
            assert "Please select a PDF file first!" in args[2]

    @patch('convert_to_image.QMessageBox.warning')
    def test_convert_file_invalid_pages(self, mock_warning):
        """Test conversion with invalid page numbers"""
        with patch.object(ConvertToImageUI, '__init__', lambda x: None):
            ui = ConvertToImageUI()
            ui.inputFileEdit = Mock()
            ui.inputFileEdit.text.return_value = "/path/to/test.pdf"
            ui.pagesEdit = Mock()
            ui.pagesEdit.text.return_value = "invalid,pages"
            
            ui.convert_file()
            
            mock_warning.assert_called_once()
            args = mock_warning.call_args[0]
            assert "Invalid page numbers!" in args[2]

    @patch('convert_to_image.convert_pdf2img')
    @patch('convert_to_image.QMessageBox.critical')
    def test_convert_file_conversion_error(self, mock_critical, mock_convert):
        """Test conversion error handling"""
        mock_convert.side_effect = Exception("Conversion failed")
        
        with patch.object(ConvertToImageUI, '__init__', lambda x: None):
            ui = ConvertToImageUI()
            ui.inputFileEdit = Mock()
            ui.inputFileEdit.text.return_value = "/path/to/test.pdf"
            ui.pagesEdit = Mock()
            ui.pagesEdit.text.return_value = ""
            ui.outputText = Mock()
            
            ui.convert_file()
            
            mock_critical.assert_called_once()

    @patch('convert_to_image.convert_pdf2img')
    def test_convert_file_with_specific_pages(self, mock_convert):
        """Test conversion with specific page numbers"""
        mock_convert.return_value = ["image1.png"]
        
        with patch.object(ConvertToImageUI, '__init__', lambda x: None):
            ui = ConvertToImageUI()
            ui.inputFileEdit = Mock()
            ui.inputFileEdit.text.return_value = "/path/to/test.pdf"
            ui.pagesEdit = Mock()
            ui.pagesEdit.text.return_value = "1, 3, 5"
            ui.outputText = Mock()
            
            ui.convert_file()
            
            # Verify convert_pdf2img was called with correct page numbers
            # (0-indexed)
            mock_convert.assert_called_once_with("/path/to/test.pdf",
                                                 (0, 2, 4))


class TestMainFunction:
    """Test class for main function"""

    @patch('convert_to_image.QtWidgets.QApplication')
    @patch('convert_to_image.ConvertToImageUI')
    @patch('convert_to_image.sys.exit')
    def test_main_success(self, mock_exit, mock_ui, mock_qapp):
        """Test successful main function execution"""
        mock_app = Mock()
        mock_qapp.return_value = mock_app
        mock_app.exec_.return_value = 0
        
        convert_to_image.main()
        
        mock_qapp.assert_called_once_with(sys.argv)
        mock_ui.assert_called_once()
        mock_exit.assert_called_once_with(0)

    @patch('convert_to_image.QtWidgets.QApplication')
    @patch('convert_to_image.sys.exit')
    def test_main_exception(self, mock_exit, mock_qapp):
        """Test main function exception handling"""
        mock_qapp.side_effect = Exception("Application error")
        
        convert_to_image.main()
        
        mock_exit.assert_called_once_with(1)


class TestIntegration:
    """Integration tests for the complete workflow"""

    def setup_method(self):
        """Setup test environment"""
        self.test_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Cleanup test environment"""
        if hasattr(self, 'test_dir') and self.test_dir:
            if os.path.exists(self.test_dir):
                shutil.rmtree(self.test_dir)
        if os.path.exists("converted_images"):
            shutil.rmtree("converted_images")

    @patch('convert_to_image.fitz')
    @patch('convert_to_image.Image')
    def test_full_conversion_workflow(self, mock_image, mock_fitz):
        """Test complete PDF to image conversion workflow"""
        # Setup comprehensive mocks
        mock_pdf = Mock()
        mock_fitz.open.return_value = mock_pdf
        mock_pdf.__len__.return_value = 2
        
        mock_page = Mock()
        mock_pdf.__getitem__.return_value = mock_page
        
        mock_pixmap = Mock()
        mock_pixmap.width = 800
        mock_pixmap.height = 600
        mock_pixmap.samples = b"mock_image_data" * 1000  # Realistic size
        mock_page.get_pixmap.return_value = mock_pixmap
        
        mock_pil_image = Mock()
        mock_image.frombytes.return_value = mock_pil_image
        
        # Create test PDF file
        test_pdf = os.path.join(self.test_dir, "test.pdf")
        with open(test_pdf, "wb") as f:
            f.write(b"Mock PDF content")
        
        # Execute conversion
        result = convert_pdf2img(test_pdf)
        
        # Verify results
        assert isinstance(result, list)
        assert len(result) == 2
        assert all("page_" in path for path in result)
        assert all(path.endswith(".png") for path in result)
        
        # Verify PyMuPDF interactions
        mock_fitz.open.assert_called_once_with(test_pdf)
        mock_pdf.close.assert_called_once()
        
        # Verify PIL interactions
        assert mock_image.frombytes.call_count == 2
        assert mock_pil_image.save.call_count == 2


# Test configuration and fixtures
@pytest.fixture(scope="session")
def test_session_info():
    """Provide test session information"""
    return {
        "start_time": datetime.now(),
        "test_file": "convert_to_image.py",
        "test_date": "2025-08-24"
    }


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Automatically setup test environment for all tests"""
    # Ensure clean state before each test
    if os.path.exists("converted_images"):
        shutil.rmtree("converted_images")
    
    yield
    
    # Cleanup after each test
    if os.path.exists("converted_images"):
        shutil.rmtree("converted_images")


# Custom pytest markers
pytestmark = [
    pytest.mark.unit,
    pytest.mark.pdf_tools
]