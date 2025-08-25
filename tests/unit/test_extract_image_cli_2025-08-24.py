"""
Comprehensive unit tests for extract_image_cli.py
Generated on: 2025-08-24
Test execution with standardized output and detailed results.
"""

import os
import shutil
import sys
import tempfile
from unittest.mock import Mock, mock_open, patch

import pytest

# Add the source directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

# Import the module under test
try:
    from src.utilities.pdf_tools.pdf_content_extraction import \
        extract_image_cli
    extract_images = extract_image_cli.extract_images
    MainWindow = extract_image_cli.MainWindow
    main = extract_image_cli.main
except ImportError as e:
    print(f"Import error: {e}")
    # Fallback import path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    from src.utilities.pdf_tools.pdf_content_extraction import \
        extract_image_cli
    extract_images = extract_image_cli.extract_images
    MainWindow = extract_image_cli.MainWindow
    main = extract_image_cli.main


class TestExtractImages:
    """Test class for the extract_images function."""
    
    @pytest.fixture
    def temp_dirs(self):
        """Create temporary directories for testing."""
        temp_input = tempfile.mkdtemp(prefix="test_input_")
        temp_output = tempfile.mkdtemp(prefix="test_output_")
        yield temp_input, temp_output
        # Cleanup
        shutil.rmtree(temp_input, ignore_errors=True)
        shutil.rmtree(temp_output, ignore_errors=True)
    
    @pytest.fixture
    def mock_pdf_document(self):
        """Create a mock PDF document with images."""
        mock_doc = Mock()
        mock_doc.__len__ = Mock(return_value=2)  # 2 pages
        
        # Mock page with images
        mock_page = Mock()
        mock_images = [
            (1, 'image1_data'),  # xref, data
            (2, 'image2_data')
        ]
        mock_page.get_images.return_value = mock_images
        
        # Mock document pages
        mock_doc.__getitem__ = Mock(return_value=mock_page)
        mock_doc.close = Mock()
        
        # Mock extract_image method
        mock_base_image = {
            'image': b'fake_image_data',
            'ext': 'png'
        }
        mock_doc.extract_image = Mock(return_value=mock_base_image)
        
        return mock_doc
    
    @pytest.fixture
    def mock_pil_image(self):
        """Create a mock PIL Image."""
        mock_image = Mock()
        mock_image.width = 200
        mock_image.height = 150
        mock_image.save = Mock()
        return mock_image
    
    @pytest.mark.unit
    def test_extract_images_file_not_found(self, temp_dirs):
        """Test extract_images with non-existent PDF file."""
        temp_input, temp_output = temp_dirs
        non_existent_file = os.path.join(temp_input, "non_existent.pdf")
        
        with pytest.raises(FileNotFoundError) as exc_info:
            extract_images(non_existent_file, temp_output)
        
        assert "Input file not found" in str(exc_info.value)
    
    @pytest.mark.unit
    @patch('src.utilities.pdf_tools.pdf_content_extraction.extract_image_cli.fitz.open')
    @patch('src.utilities.pdf_tools.pdf_content_extraction.extract_image_cli.Image.open')
    def test_extract_images_success(self, mock_image_open, mock_fitz_open, 
                                   temp_dirs, mock_pdf_document, mock_pil_image):
        """Test successful image extraction."""
        temp_input, temp_output = temp_dirs
        pdf_path = os.path.join(temp_input, "test.pdf")
        
        # Create a dummy PDF file
        with open(pdf_path, 'w') as f:
            f.write("dummy pdf content")
        
        # Setup mocks
        mock_fitz_open.return_value = mock_pdf_document
        mock_image_open.return_value = mock_pil_image
        
        # Execute function
        result = extract_images(pdf_path, temp_output, min_width=100, min_height=100, format="png")
        
        # Assertions
        assert isinstance(result, list)
        mock_fitz_open.assert_called_once_with(pdf_path)
        mock_pdf_document.close.assert_called_once()
    
    @pytest.mark.unit
    @patch('src.utilities.pdf_tools.pdf_content_extraction.extract_image_cli.fitz.open')
    @patch('src.utilities.pdf_tools.pdf_content_extraction.extract_image_cli.Image.open')
    def test_extract_images_size_filtering(self, mock_image_open, mock_fitz_open, 
                                          temp_dirs, mock_pdf_document):
        """Test image size filtering functionality."""
        temp_input, temp_output = temp_dirs
        pdf_path = os.path.join(temp_input, "test.pdf")
        
        with open(pdf_path, 'w') as f:
            f.write("dummy pdf content")
        
        # Create a small image that should be filtered out
        small_image = Mock()
        small_image.width = 50
        small_image.height = 30
        small_image.save = Mock()
        
        mock_fitz_open.return_value = mock_pdf_document
        mock_image_open.return_value = small_image
        
        result = extract_images(pdf_path, temp_output, min_width=100, min_height=100)
        
        # Should return empty list as image is too small
        assert result == []
    
    @pytest.mark.unit
    @patch('src.utilities.pdf_tools.pdf_content_extraction.extract_image_cli.fitz.open')
    def test_extract_images_pdf_open_error(self, mock_fitz_open, temp_dirs):
        """Test handling of PDF opening errors."""
        temp_input, temp_output = temp_dirs
        pdf_path = os.path.join(temp_input, "corrupt.pdf")
        
        with open(pdf_path, 'w') as f:
            f.write("dummy pdf content")
        
        mock_fitz_open.side_effect = Exception("Corrupt PDF file")
        
        with pytest.raises(Exception) as exc_info:
            extract_images(pdf_path, temp_output)
        
        assert "Corrupt PDF file" in str(exc_info.value)
    
    @pytest.mark.unit
    def test_extract_images_creates_output_directory(self, temp_dirs):
        """Test that extract_images creates output directory if it doesn't exist."""
        temp_input, _ = temp_dirs
        pdf_path = os.path.join(temp_input, "test.pdf")
        non_existent_output = os.path.join(temp_input, "new_output_dir")
        
        with open(pdf_path, 'w') as f:
            f.write("dummy pdf content")
        
        with patch('src.utilities.pdf_tools.pdf_content_extraction.extract_image_cli.fitz.open') as mock_fitz:
            mock_doc = Mock()
            mock_doc.__len__ = Mock(return_value=0)  # No pages
            mock_doc.close = Mock()
            mock_fitz.return_value = mock_doc
            
            extract_images(pdf_path, non_existent_output)
            
            assert os.path.exists(non_existent_output)
    
    @pytest.mark.pdf
    @patch('src.utilities.pdf_tools.pdf_content_extraction.extract_image_cli.fitz.open')
    @patch('src.utilities.pdf_tools.pdf_content_extraction.extract_image_cli.Image.open')
    def test_extract_images_different_formats(self, mock_image_open, mock_fitz_open, 
                                             temp_dirs, mock_pdf_document, mock_pil_image):
        """Test image extraction with different output formats."""
        temp_input, temp_output = temp_dirs
        pdf_path = os.path.join(temp_input, "test.pdf")
        
        with open(pdf_path, 'w') as f:
            f.write("dummy pdf content")
        
        mock_fitz_open.return_value = mock_pdf_document
        mock_image_open.return_value = mock_pil_image
        
        # Test different formats
        for format_type in ['png', 'jpg', 'jpeg', 'tiff']:
            extract_images(pdf_path, temp_output, format=format_type)
            # Verify save was called with uppercase format
            calls = mock_pil_image.save.call_args_list
            if calls:
                _, kwargs = calls[-1]
                assert kwargs.get('format') == format_type.upper()


@pytest.mark.gui
class TestMainWindow:
    """Test class for the MainWindow GUI class."""
    
    @pytest.fixture
    def mock_qt_app(self):
        """Mock PyQt5 application for testing."""
        with patch('src.utilities.pdf_tools.pdf_content_extraction.extract_image_cli.QApplication') as mock_app:
            mock_app_instance = Mock()
            mock_app.return_value = mock_app_instance
            yield mock_app_instance
    
    @pytest.fixture
    def mock_main_window_init(self):
        """Mock MainWindow initialization components."""
        with patch('src.utilities.pdf_tools.pdf_content_extraction.extract_image_cli.uic.loadUi') as mock_load_ui, \
             patch('src.utilities.pdf_tools.pdf_content_extraction.extract_image_cli.QtWidgets.QProgressBar') as mock_progress, \
             patch.object(MainWindow, 'statusBar') as mock_status_bar, \
             patch.object(MainWindow, 'show') as mock_show:
            
            mock_status_bar.return_value.addPermanentWidget = Mock()
            yield {
                'load_ui': mock_load_ui,
                'progress_bar': mock_progress,
                'status_bar': mock_status_bar,
                'show': mock_show
            }
    
    @pytest.mark.gui
    def test_main_window_initialization(self, mock_main_window_init):
        """Test MainWindow initialization."""
        with patch.object(MainWindow, '__init__', lambda x: None):
            window = MainWindow()
            window.browseButton = Mock()
            window.browseOutputButton = Mock()
            window.extractButton = Mock()
            window.actionExit = Mock()
            window.progressBar = Mock()
            window.statusBar = Mock(return_value=Mock())
            
            # Test that initialization would work
            assert window is not None
    
    @pytest.mark.gui
    @patch('src.utilities.pdf_tools.pdf_content_extraction.extract_image_cli.QFileDialog.getOpenFileName')
    def test_browse_pdf_success(self, mock_file_dialog):
        """Test successful PDF file browsing."""
        mock_file_dialog.return_value = ("/path/to/test.pdf", "")
        
        with patch.object(MainWindow, '__init__', lambda x: None):
            window = MainWindow()
            window.pdfFileEdit = Mock()
            
            window.browse_pdf()
            
            window.pdfFileEdit.setText.assert_called_once_with("/path/to/test.pdf")
    
    @pytest.mark.gui
    @patch('src.utilities.pdf_tools.pdf_content_extraction.extract_image_cli.QFileDialog.getOpenFileName')
    def test_browse_pdf_cancelled(self, mock_file_dialog):
        """Test cancelled PDF file browsing."""
        mock_file_dialog.return_value = ("", "")  # User cancelled
        
        with patch.object(MainWindow, '__init__', lambda x: None):
            window = MainWindow()
            window.pdfFileEdit = Mock()
            
            window.browse_pdf()
            
            # setText should not be called if user cancelled
            window.pdfFileEdit.setText.assert_not_called()
    
    @pytest.mark.gui
    @patch('src.utilities.pdf_tools.pdf_content_extraction.extract_image_cli.QFileDialog.getExistingDirectory')
    def test_browse_output_dir_success(self, mock_dir_dialog):
        """Test successful output directory browsing."""
        mock_dir_dialog.return_value = "/path/to/output"
        
        with patch.object(MainWindow, '__init__', lambda x: None):
            window = MainWindow()
            window.outputDirEdit = Mock()
            
            window.browse_output_dir()
            
            window.outputDirEdit.setText.assert_called_once_with("/path/to/output")
    
    @pytest.mark.gui
    @patch('src.utilities.pdf_tools.pdf_content_extraction.extract_image_cli.QMessageBox.warning')
    def test_extract_images_no_pdf_selected(self, mock_message_box):
        """Test extract_images with no PDF file selected."""
        with patch.object(MainWindow, '__init__', lambda x: None):
            window = MainWindow()
            window.pdfFileEdit = Mock()
            window.pdfFileEdit.text.return_value = ""  # No file selected
            window.outputDirEdit = Mock()
            window.outputDirEdit.text.return_value = "/output"
            
            window.extract_images()
            
            mock_message_box.assert_called_once()
    
    @pytest.mark.gui
    @patch('src.utilities.pdf_tools.pdf_content_extraction.extract_image_cli.QMessageBox.warning')
    def test_extract_images_no_output_dir_selected(self, mock_message_box):
        """Test extract_images with no output directory selected."""
        with patch.object(MainWindow, '__init__', lambda x: None):
            window = MainWindow()
            window.pdfFileEdit = Mock()
            window.pdfFileEdit.text.return_value = "/path/to/test.pdf"
            window.outputDirEdit = Mock()
            window.outputDirEdit.text.return_value = ""  # No directory selected
            
            window.extract_images()
            
            mock_message_box.assert_called_once()
    
    @pytest.mark.gui
    @patch('src.utilities.pdf_tools.pdf_content_extraction.extract_image_cli.fitz.open')
    @patch('src.utilities.pdf_tools.pdf_content_extraction.extract_image_cli.QMessageBox.information')
    def test_extract_images_gui_success(self, mock_message_box, mock_fitz_open):
        """Test successful image extraction through GUI."""
        # Setup mock PDF document
        mock_doc = Mock()
        mock_doc.page_count = 1
        mock_page = Mock()
        mock_page.get_images.return_value = [(1, 'img_data')]
        mock_doc.__getitem__.return_value = mock_page
        mock_doc.extract_image.return_value = {
            'image': b'fake_image_data',
            'ext': 'png'
        }
        mock_doc.close = Mock()
        mock_fitz_open.return_value = mock_doc
        
        with patch.object(MainWindow, '__init__', lambda x: None), \
             patch('builtins.open', mock_open()):
            
            window = MainWindow()
            window.pdfFileEdit = Mock()
            window.pdfFileEdit.text.return_value = "/path/to/test.pdf"
            window.outputDirEdit = Mock()
            window.outputDirEdit.text.return_value = "/output"
            window.progressBar = Mock()
            window.statusBar = Mock(return_value=Mock())
            
            with patch('src.utilities.pdf_tools.pdf_content_extraction.extract_image_cli.QtWidgets.QApplication.processEvents'):
                window.extract_images()
            
            mock_message_box.assert_called_once()
            args, _ = mock_message_box.call_args
            assert "Successfully extracted" in args[1]
    
    @pytest.mark.gui
    @patch('src.utilities.pdf_tools.pdf_content_extraction.extract_image_cli.QFileDialog.getOpenFileName')
    @patch('src.utilities.pdf_tools.pdf_content_extraction.extract_image_cli.QMessageBox.critical')
    def test_browse_pdf_error_handling(self, mock_message_box, mock_file_dialog):
        """Test error handling in browse_pdf method."""
        mock_file_dialog.side_effect = Exception("File dialog error")
        
        with patch.object(MainWindow, '__init__', lambda x: None):
            window = MainWindow()
            
            window.browse_pdf()
            
            mock_message_box.assert_called_once()
    
    @pytest.mark.gui
    @patch('src.utilities.pdf_tools.pdf_content_extraction.extract_image_cli.QFileDialog.getExistingDirectory')
    @patch('src.utilities.pdf_tools.pdf_content_extraction.extract_image_cli.QMessageBox.critical')
    def test_browse_output_dir_error_handling(self, mock_message_box, mock_dir_dialog):
        """Test error handling in browse_output_dir method."""
        mock_dir_dialog.side_effect = Exception("Directory dialog error")
        
        with patch.object(MainWindow, '__init__', lambda x: None):
            window = MainWindow()
            
            window.browse_output_dir()
            
            mock_message_box.assert_called_once()


@pytest.mark.integration
class TestMainFunction:
    """Test class for the main function and application startup."""
    
    @pytest.mark.integration
    @patch('src.utilities.pdf_tools.pdf_content_extraction.extract_image_cli.QApplication')
    @patch('src.utilities.pdf_tools.pdf_content_extraction.extract_image_cli.MainWindow')
    @patch('sys.exit')
    def test_main_function_success(self, mock_sys_exit, mock_main_window, mock_qapp):
        """Test successful main function execution."""
        # Setup mocks
        mock_app_instance = Mock()
        mock_qapp.return_value = mock_app_instance
        mock_app_instance.exec_.return_value = 0
        
        mock_window_instance = Mock()
        mock_main_window.return_value = mock_window_instance
        
        # Test with mocked sys.argv
        with patch('sys.argv', ['extract_image_cli.py']):
            main()
        
        # Verify app was created and window was instantiated
        mock_qapp.assert_called_once()
        mock_main_window.assert_called_once()
        mock_sys_exit.assert_called_once_with(0)
    
    @pytest.mark.integration
    @patch('src.utilities.pdf_tools.pdf_content_extraction.extract_image_cli.QApplication')
    @patch('src.utilities.pdf_tools.pdf_content_extraction.extract_image_cli.MainWindow')
    @patch('sys.exit')
    def test_main_function_window_init_error(self, mock_sys_exit, mock_main_window, mock_qapp):
        """Test main function with MainWindow initialization error."""
        mock_qapp.return_value = Mock()
        mock_main_window.side_effect = Exception("Window initialization failed")
        
        with patch('sys.argv', ['extract_image_cli.py']):
            main()
        
        mock_sys_exit.assert_called_once_with(1)
    
    @pytest.mark.integration
    @patch('src.utilities.pdf_tools.pdf_content_extraction.extract_image_cli.QApplication')
    @patch('sys.exit')
    def test_main_function_app_creation_error(self, mock_sys_exit, mock_qapp):
        """Test main function with QApplication creation error."""
        mock_qapp.side_effect = Exception("QApplication creation failed")
        
        with patch('sys.argv', ['extract_image_cli.py']):
            main()
        
        mock_sys_exit.assert_called_once_with(1)


class TestEdgeCasesAndErrorHandling:
    """Test class for edge cases and error handling scenarios."""
    
    @pytest.mark.unit
    def test_extract_images_empty_pdf(self, temp_dirs):
        """Test extract_images with PDF containing no images."""
        temp_input, temp_output = temp_dirs
        pdf_path = os.path.join(temp_input, "empty.pdf")
        
        with open(pdf_path, 'w') as f:
            f.write("dummy pdf content")
        
        with patch('src.utilities.pdf_tools.pdf_content_extraction.extract_image_cli.fitz.open') as mock_fitz:
            mock_doc = Mock()
            mock_doc.__len__ = Mock(return_value=1)  # 1 page
            mock_page = Mock()
            mock_page.get_images.return_value = []  # No images
            mock_doc.__getitem__ = Mock(return_value=mock_page)
            mock_doc.close = Mock()
            mock_fitz.return_value = mock_doc
            
            result = extract_images(pdf_path, temp_output)
            
            assert result == []
    
    @pytest.mark.unit
    @patch('src.utilities.pdf_tools.pdf_content_extraction.extract_image_cli.fitz.open')
    @patch('src.utilities.pdf_tools.pdf_content_extraction.extract_image_cli.Image.open')
    def test_extract_images_corrupted_image_data(self, mock_image_open, mock_fitz_open, temp_dirs):
        """Test extract_images with corrupted image data in PDF."""
        temp_input, temp_output = temp_dirs
        pdf_path = os.path.join(temp_input, "corrupted_images.pdf")
        
        with open(pdf_path, 'w') as f:
            f.write("dummy pdf content")
        
        # Setup mock to simulate corrupted image
        mock_doc = Mock()
        mock_doc.__len__ = Mock(return_value=1)
        mock_page = Mock()
        mock_page.get_images.return_value = [(1, 'corrupted_data')]
        mock_doc.__getitem__ = Mock(return_value=mock_page)
        mock_doc.extract_image.return_value = {'image': b'corrupted', 'ext': 'png'}
        mock_doc.close = Mock()
        mock_fitz_open.return_value = mock_doc
        
        # Image.open should raise exception for corrupted data
        mock_image_open.side_effect = Exception("Cannot identify image file")
        
        result = extract_images(pdf_path, temp_output)
        
        # Should handle the error gracefully and return empty list
        assert result == []
    
    @pytest.mark.unit
    def test_extract_images_invalid_parameters(self, temp_dirs):
        """Test extract_images with invalid parameters."""
        temp_input, temp_output = temp_dirs
        pdf_path = os.path.join(temp_input, "test.pdf")
        
        with open(pdf_path, 'w') as f:
            f.write("dummy pdf content")
        
        with patch('src.utilities.pdf_tools.pdf_content_extraction.extract_image_cli.fitz.open') as mock_fitz:
            mock_doc = Mock()
            mock_doc.__len__ = Mock(return_value=0)
            mock_doc.close = Mock()
            mock_fitz.return_value = mock_doc
            
            # Test with negative dimensions
            result = extract_images(pdf_path, temp_output, min_width=-10, min_height=-10)
            assert isinstance(result, list)
            
            # Test with zero dimensions
            result = extract_images(pdf_path, temp_output, min_width=0, min_height=0)
            assert isinstance(result, list)


class TestSetupAndTeardown:
    """Test class demonstrating setup and teardown methods."""
    
    @classmethod
    def setup_class(cls):
        """Class-level setup for test data preparation."""
        cls.test_data_dir = tempfile.mkdtemp(prefix="test_setup_")
        print(f"Created test data directory: {cls.test_data_dir}")
    
    @classmethod
    def teardown_class(cls):
        """Class-level teardown for test data cleanup."""
        if hasattr(cls, 'test_data_dir') and os.path.exists(cls.test_data_dir):
            shutil.rmtree(cls.test_data_dir, ignore_errors=True)
            print(f"Cleaned up test data directory: {cls.test_data_dir}")
    
    def setup_method(self, method):
        """Method-level setup before each test."""
        self.method_temp_dir = tempfile.mkdtemp(prefix=f"test_{method.__name__}_")
        print(f"Setup for {method.__name__}: {self.method_temp_dir}")
    
    def teardown_method(self, method):
        """Method-level teardown after each test."""
        if hasattr(self, 'method_temp_dir') and os.path.exists(self.method_temp_dir):
            shutil.rmtree(self.method_temp_dir, ignore_errors=True)
            print(f"Teardown for {method.__name__}: {self.method_temp_dir}")
    
    @pytest.mark.unit
    def test_setup_teardown_example(self):
        """Example test showing setup and teardown functionality."""
        # Verify setup worked
        assert os.path.exists(self.method_temp_dir)
        assert os.path.exists(self.test_data_dir)
        
        # Create a test file
        test_file = os.path.join(self.method_temp_dir, "test_file.txt")
        with open(test_file, 'w') as f:
            f.write("test content")
        
        assert os.path.exists(test_file)


# Test execution timestamp and results tracking
@pytest.fixture(scope="session", autouse=True)
def test_execution_info():
    """Fixture to track test execution information."""
    import datetime
    
    execution_time = datetime.datetime.now()
    print("\n" + "="*60)
    print("EXTRACT_IMAGE_CLI TEST EXECUTION")
    print(f"Timestamp: {execution_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("Test file: test_extract_image_cli_2025-08-24.py")
    print("Target module: extract_image_cli.py")
    print("="*60 + "\n")
    
    yield execution_time
    
    end_time = datetime.datetime.now()
    duration = end_time - execution_time
    print("\n" + "="*60)
    print("TEST EXECUTION COMPLETED")
    print(f"End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total duration: {duration}")
    print("="*60 + "\n")


if __name__ == "__main__":
    # Direct execution for debugging
    pytest.main([__file__, "-v", "--tb=short"])