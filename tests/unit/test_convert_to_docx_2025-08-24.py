"""
Comprehensive unit tests for convert_to_docx.py
Generated on: 2025-08-24
Test execution timestamp: {execution_timestamp}

This test suite provides comprehensive testing coverage for:
- convert_pdf2docx function
- create_folder function
- move_files function
- ConvertWindow class and its methods

Tests include:
- Unit tests for individual functions
- Integration tests for component interaction
- GUI tests for window components
- Edge cases and error handling
- Mock data scenarios
"""

import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from PyQt5.QtWidgets import QApplication

# Add source directory to path for imports
source_path = str(Path(__file__).parent.parent.parent / "src" /
                  "utilities" / "pdf_tools" / "pdf_conversion")
sys.path.insert(0, source_path)

# Import the module under test
try:
    from convert_to_docx import (ConvertWindow, convert_pdf2docx,
                                 create_folder, move_files)
except ImportError as e:
    pytest.skip(f"Could not import convert_to_docx module: {e}",
                allow_module_level=True)


class TestConvertPdf2Docx:
    """Test cases for convert_pdf2docx function."""
    
    def test_convert_pdf2docx_success(self, temp_dir, mock_pdf2docx_parse):
        """Test successful PDF to DOCX conversion."""
        # Arrange
        input_file = os.path.join(temp_dir, "test.pdf")
        output_file = os.path.join(temp_dir, "test.docx")
        
        # Create mock PDF file
        with open(input_file, 'w') as f:
            f.write("Mock PDF content")
        
        mock_pdf2docx_parse.return_value = True
        
        with patch('convert_to_docx.logger') as mock_logger:
            # Act
            result = convert_pdf2docx(input_file, output_file)
            
            # Assert
            assert result is True
            mock_pdf2docx_parse.assert_called_once_with(
                pdf_file=input_file, 
                docx_with_path=output_file, 
                pages=None
            )
            mock_logger.info.assert_called()
    
    def test_convert_pdf2docx_with_pages(self, temp_dir, mock_pdf2docx_parse):
        """Test PDF to DOCX conversion with specific pages."""
        # Arrange
        input_file = os.path.join(temp_dir, "test.pdf")
        output_file = os.path.join(temp_dir, "test.docx")
        pages = ("1", "3", "5")
        
        with open(input_file, 'w') as f:
            f.write("Mock PDF content")
        
        mock_pdf2docx_parse.return_value = True
        
        with patch('convert_to_docx.logger') as mock_logger:
            # Act
            result = convert_pdf2docx(input_file, output_file, pages)
            
            # Assert
            assert result is True
            mock_pdf2docx_parse.assert_called_once_with(
                pdf_file=input_file, 
                docx_with_path=output_file, 
                pages=[1, 3, 5]
            )
    
    def test_convert_pdf2docx_with_invalid_pages(self, temp_dir, mock_pdf2docx_parse):
        """Test PDF to DOCX conversion with invalid page numbers."""
        # Arrange
        input_file = os.path.join(temp_dir, "test.pdf")
        output_file = os.path.join(temp_dir, "test.docx")
        pages = ("1", "abc", "3", "xyz")
        
        with open(input_file, 'w') as f:
            f.write("Mock PDF content")
        
        mock_pdf2docx_parse.return_value = True
        
        with patch('convert_to_docx.logger') as mock_logger:
            # Act
            result = convert_pdf2docx(input_file, output_file, pages)
            
            # Assert
            assert result is True
            mock_pdf2docx_parse.assert_called_once_with(
                pdf_file=input_file, 
                docx_with_path=output_file, 
                pages=[1, 3]  # Only numeric pages should be included
            )
    
    def test_convert_pdf2docx_file_not_found(self, temp_dir):
        """Test PDF to DOCX conversion with non-existent input file."""
        # Arrange
        input_file = os.path.join(temp_dir, "nonexistent.pdf")
        output_file = os.path.join(temp_dir, "test.docx")
        
        with patch('convert_to_docx.logger') as mock_logger:
            # Act & Assert
            with pytest.raises(SystemExit):
                convert_pdf2docx(input_file, output_file)
            
            mock_logger.error.assert_called()
    
    def test_convert_pdf2docx_parse_exception(self, temp_dir, mock_pdf2docx_parse):
        """Test PDF to DOCX conversion when parse raises exception."""
        # Arrange
        input_file = os.path.join(temp_dir, "test.pdf")
        output_file = os.path.join(temp_dir, "test.docx")
        
        with open(input_file, 'w') as f:
            f.write("Mock PDF content")
        
        mock_pdf2docx_parse.side_effect = Exception("Parse error")
        
        with patch('convert_to_docx.logger') as mock_logger:
            # Act & Assert
            with pytest.raises(SystemExit):
                convert_pdf2docx(input_file, output_file)
            
            mock_logger.error.assert_called()


class TestCreateFolder:
    """Test cases for create_folder function."""
    
    def test_create_folder_success(self, temp_dir):
        """Test successful folder creation."""
        # Arrange
        folder_path = os.path.join(temp_dir, "new_folder")
        
        with patch('convert_to_docx.logger') as mock_logger:
            # Act
            result = create_folder(folder_path)
            
            # Assert
            assert result is True
            assert os.path.exists(folder_path)
            mock_logger.info.assert_called_with("Creating folder: %s", folder_path)
    
    def test_create_folder_already_exists(self, temp_dir):
        """Test folder creation when folder already exists."""
        # Arrange
        folder_path = os.path.join(temp_dir, "existing_folder")
        os.makedirs(folder_path)
        
        with patch('convert_to_docx.logger') as mock_logger:
            # Act
            result = create_folder(folder_path)
            
            # Assert
            assert result is True
            assert os.path.exists(folder_path)
            # Should not log creation message since folder exists
            mock_logger.info.assert_not_called()
    
    def test_create_folder_nested_path(self, temp_dir):
        """Test creation of nested folder structure."""
        # Arrange
        folder_path = os.path.join(temp_dir, "parent", "child", "grandchild")
        
        with patch('convert_to_docx.logger') as mock_logger:
            # Act
            result = create_folder(folder_path)
            
            # Assert
            assert result is True
            assert os.path.exists(folder_path)
            mock_logger.info.assert_called()
    
    def test_create_folder_permission_error(self, temp_dir):
        """Test folder creation with permission error."""
        # Arrange
        folder_path = os.path.join(temp_dir, "protected_folder")
        
        with patch('convert_to_docx.os.makedirs') as mock_makedirs, \
             patch('convert_to_docx.logger') as mock_logger:
            mock_makedirs.side_effect = PermissionError("Permission denied")
            
            # Act
            result = create_folder(folder_path)
            
            # Assert
            assert result is False
            mock_logger.error.assert_called()


class TestMoveFiles:
    """Test cases for move_files function."""
    
    def test_move_files_success(self, temp_dir):
        """Test successful file moving."""
        # Arrange
        input_file = os.path.join(temp_dir, "input.pdf")
        output_file = os.path.join(temp_dir, "output.docx")
        folder_name = os.path.join(temp_dir, "destination")
        
        # Create test files and destination folder
        with open(input_file, 'w') as f:
            f.write("Input content")
        with open(output_file, 'w') as f:
            f.write("Output content")
        os.makedirs(folder_name)
        
        with patch('convert_to_docx.logger') as mock_logger:
            # Act
            result = move_files(input_file, output_file, folder_name)
            
            # Assert
            assert result is True
            assert not os.path.exists(input_file)  # Original files should be moved
            assert not os.path.exists(output_file)
            assert os.path.exists(os.path.join(folder_name, "input.pdf"))
            assert os.path.exists(os.path.join(folder_name, "output.docx"))
            mock_logger.info.assert_called()
    
    def test_move_files_destination_not_exists(self, temp_dir):
        """Test file moving when destination folder doesn't exist."""
        # Arrange
        input_file = os.path.join(temp_dir, "input.pdf")
        output_file = os.path.join(temp_dir, "output.docx")
        folder_name = os.path.join(temp_dir, "nonexistent")
        
        with open(input_file, 'w') as f:
            f.write("Input content")
        with open(output_file, 'w') as f:
            f.write("Output content")
        
        with patch('convert_to_docx.logger') as mock_logger:
            # Act
            result = move_files(input_file, output_file, folder_name)
            
            # Assert
            assert result is False
            mock_logger.warning.assert_called()
    
    def test_move_files_shutil_error(self, temp_dir):
        """Test file moving with shutil error."""
        # Arrange
        input_file = os.path.join(temp_dir, "input.pdf")
        output_file = os.path.join(temp_dir, "output.docx")
        folder_name = os.path.join(temp_dir, "destination")
        
        with open(input_file, 'w') as f:
            f.write("Input content")
        with open(output_file, 'w') as f:
            f.write("Output content")
        os.makedirs(folder_name)
        
        with patch('convert_to_docx.shutil.move') as mock_move, \
             patch('convert_to_docx.logger') as mock_logger:
            mock_move.side_effect = Exception("Move error")
            
            # Act
            result = move_files(input_file, output_file, folder_name)
            
            # Assert
            assert result is False
            mock_logger.error.assert_called()


class TestConvertWindow:
    """Test cases for ConvertWindow class."""
    
    @pytest.fixture(autouse=True)
    def setup_qapp(self, qapp):
        """Ensure QApplication is available for GUI tests."""
        self.app = qapp
    
    def test_convert_window_initialization(self):
        """Test ConvertWindow initialization."""
        with patch('convert_to_docx.logger') as mock_logger:
            # Act
            window = ConvertWindow()
            
            # Assert
            assert window.windowTitle() == 'PDF to DOCX Converter'
            assert window.geometry().width() == 600
            assert window.geometry().height() == 400
            mock_logger.info.assert_called_with("PDF to DOCX converter initialized")
    
    def test_convert_window_initialization_error(self):
        """Test ConvertWindow initialization with error."""
        with patch('convert_to_docx.ConvertWindow.initUI') as mock_init, \
             patch('convert_to_docx.logger') as mock_logger:
            mock_init.side_effect = Exception("Init error")
            
            # Act & Assert
            with pytest.raises(Exception):
                ConvertWindow()
            
            mock_logger.error.assert_called()
    
    def test_init_ui_components(self):
        """Test UI components initialization."""
        with patch('convert_to_docx.logger'):
            # Act
            window = ConvertWindow()
            
            # Assert - Check menu bar exists
            menubar = window.menuBar()
            assert menubar is not None
            
            # Check menu actions
            file_menu = menubar.actions()[0].menu()
            assert file_menu.title() == 'File'
            
            # Check central widget and layout
            central_widget = window.centralWidget()
            assert central_widget is not None
            
            # Check that status label exists
            assert hasattr(window, 'status_label')
            assert hasattr(window, 'progress_label')
    
    def test_select_pdf_success(self, temp_dir):
        """Test successful PDF selection and conversion."""
        # Arrange
        input_file = os.path.join(temp_dir, "test.pdf")
        with open(input_file, 'w') as f:
            f.write("Mock PDF content")
        
        with patch('convert_to_docx.logger'), \
             patch('convert_to_docx.QFileDialog.getOpenFileName') as mock_dialog, \
             patch('convert_to_docx.convert_pdf2docx') as mock_convert, \
             patch('convert_to_docx.QMessageBox') as mock_msgbox:
            
            mock_dialog.return_value = (input_file, "")
            mock_convert.return_value = True
            
            window = ConvertWindow()
            
            # Act
            window.select_pdf()
            
            # Assert
            mock_convert.assert_called_once()
            mock_msgbox.information.assert_called_once()
            assert "Select a PDF file to convert" in window.status_label.text()
    
    def test_select_pdf_no_file_selected(self):
        """Test PDF selection when no file is selected."""
        with patch('convert_to_docx.logger'), \
             patch('convert_to_docx.QFileDialog.getOpenFileName') as mock_dialog:
            
            mock_dialog.return_value = ("", "")  # No file selected
            
            window = ConvertWindow()
            original_text = window.status_label.text()
            
            # Act
            window.select_pdf()
            
            # Assert
            # Status should remain unchanged
            assert window.status_label.text() == original_text
    
    def test_select_pdf_conversion_error(self, temp_dir):
        """Test PDF selection with conversion error."""
        # Arrange
        input_file = os.path.join(temp_dir, "test.pdf")
        with open(input_file, 'w') as f:
            f.write("Mock PDF content")
        
        with patch('convert_to_docx.logger') as mock_logger, \
             patch('convert_to_docx.QFileDialog.getOpenFileName') as mock_dialog, \
             patch('convert_to_docx.convert_pdf2docx') as mock_convert, \
             patch('convert_to_docx.QMessageBox') as mock_msgbox:
            
            mock_dialog.return_value = (input_file, "")
            mock_convert.side_effect = Exception("Conversion failed")
            
            window = ConvertWindow()
            
            # Act
            window.select_pdf()
            
            # Assert
            mock_logger.error.assert_called()
            mock_msgbox.critical.assert_called_once()
            assert "Error occurred during conversion" in window.status_label.text()
    
    def test_select_pdf_dialog_error(self):
        """Test PDF selection with dialog error."""
        with patch('convert_to_docx.logger') as mock_logger, \
             patch('convert_to_docx.QFileDialog.getOpenFileName') as mock_dialog, \
             patch('convert_to_docx.QMessageBox') as mock_msgbox:
            
            mock_dialog.side_effect = Exception("Dialog error")
            
            window = ConvertWindow()
            
            # Act
            window.select_pdf()
            
            # Assert
            mock_logger.error.assert_called()
            mock_msgbox.critical.assert_called_once()


class TestIntegration:
    """Integration tests for convert_to_docx module."""
    
    def test_full_conversion_workflow(self, temp_dir):
        """Test complete conversion workflow."""
        # Arrange
        input_file = os.path.join(temp_dir, "test.pdf")
        output_file = os.path.join(temp_dir, "test.docx")
        destination_folder = os.path.join(temp_dir, "converted")
        
        with open(input_file, 'w') as f:
            f.write("Mock PDF content")
        
        with patch('convert_to_docx.parse') as mock_parse, \
             patch('convert_to_docx.logger'):
            
            mock_parse.return_value = True
            
            # Act - Convert PDF
            convert_result = convert_pdf2docx(input_file, output_file)
            
            # Create destination folder
            folder_result = create_folder(destination_folder)
            
            # Create mock output file for moving
            with open(output_file, 'w') as f:
                f.write("Mock DOCX content")
            
            # Move files
            move_result = move_files(input_file, output_file, destination_folder)
            
            # Assert
            assert convert_result is True
            assert folder_result is True
            assert move_result is True
    
    def test_gui_integration_workflow(self, temp_dir):
        """Test GUI integration workflow."""
        # Arrange
        input_file = os.path.join(temp_dir, "test.pdf")
        with open(input_file, 'w') as f:
            f.write("Mock PDF content")
        
        with patch('convert_to_docx.logger'), \
             patch('convert_to_docx.parse') as mock_parse, \
             patch('convert_to_docx.QFileDialog.getOpenFileName') as mock_dialog:
            
            mock_parse.return_value = True
            mock_dialog.return_value = (input_file, "")
            
            # Act
            window = ConvertWindow()
            window.select_pdf()
            
            # Assert
            assert window.windowTitle() == 'PDF to DOCX Converter'
            mock_parse.assert_called_once()


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_empty_string_inputs(self):
        """Test functions with empty string inputs."""
        with patch('convert_to_docx.logger'):
            # Test create_folder with empty string
            result = create_folder("")
            # Empty string creates current directory, which should exist
            assert result is True
            
            # Test move_files with empty strings
            result = move_files("", "", "")
            assert result is False
    
    def test_unicode_file_paths(self, temp_dir):
        """Test functions with unicode file paths."""
        # Arrange
        unicode_file = os.path.join(temp_dir, "测试文件.pdf")
        unicode_output = os.path.join(temp_dir, "测试文件.docx")
        unicode_folder = os.path.join(temp_dir, "测试文件夹")
        
        with open(unicode_file, 'w', encoding='utf-8') as f:
            f.write("Unicode test content")
        
        with patch('convert_to_docx.parse') as mock_parse, \
             patch('convert_to_docx.logger'):
            
            mock_parse.return_value = True
            
            # Act
            convert_result = convert_pdf2docx(unicode_file, unicode_output)
            folder_result = create_folder(unicode_folder)
            
            # Assert
            assert convert_result is True
            assert folder_result is True
            assert os.path.exists(unicode_folder)
    
    def test_very_long_file_paths(self, temp_dir):
        """Test functions with very long file paths."""
        # Arrange - Create a very long path
        long_path_components = ["very_long_folder_name_" + str(i) for i in range(10)]
        long_folder = os.path.join(temp_dir, *long_path_components)
        
        with patch('convert_to_docx.logger'):
            # Act
            try:
                result = create_folder(long_folder)
                # If the system supports it, should succeed
                if result:
                    assert os.path.exists(long_folder)
            except OSError:
                # If path is too long for the system, that's expected
                pass


# Fixtures for test setup and teardown
@pytest.fixture
def temp_dir():
    """Create a temporary directory for each test."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield tmp_dir


@pytest.fixture
def mock_pdf2docx_parse():
    """Mock the pdf2docx.parse function."""
    with patch('convert_to_docx.parse') as mock_parse:
        yield mock_parse


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance for GUI tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    # Don't quit the app as it might be used by other tests


@pytest.fixture(scope="session")
def execution_timestamp():
    """Fixture providing the test execution timestamp."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# Test data setup and teardown
def setup_module(module):
    """Setup module-level test data."""
    print(f"\n=== Setting up test module: {module.__name__} ===")
    print(f"Test execution timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def teardown_module(module):
    """Teardown module-level test data."""
    print(f"\n=== Tearing down test module: {module.__name__} ===")
    print(f"Test completion timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def setup_function(function):
    """Setup function-level test data."""
    print(f"\n--- Setting up test function: {function.__name__} ---")


def teardown_function(function):
    """Teardown function-level test data."""
    print(f"--- Completed test function: {function.__name__} ---")


if __name__ == "__main__":
    pytest.main([__file__])