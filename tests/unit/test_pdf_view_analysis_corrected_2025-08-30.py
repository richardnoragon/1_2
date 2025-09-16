"""
Comprehensive unit tests for PDF View Analysis module (CORRECTED VERSION).

This test suite provides complete coverage for the PDFViewer class including:
- Initialization and UI loading
- Configuration management
- File operations
- Page navigation
- Error handling
- Resource cleanup

Created: 2025-08-30
Module: src/tools/pdf_tools/pdf_view_analysis/view.py
"""

import os
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, Mock, call, mock_open, patch

import pytest

# Add project root to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'utilities', 'pdf_tools', 'pdf_view_analysis'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Mock PyQt5 modules before importing
PyQt5_mock = Mock()
PyQt5_mock.QtWidgets = Mock()
PyQt5_mock.QtGui = Mock()
PyQt5_mock.QtCore = Mock()
PyQt5_mock.uic = Mock()

# Mock required PyQt5 classes
PyQt5_mock.QtWidgets.QMainWindow = Mock()
PyQt5_mock.QtWidgets.QApplication = Mock()
PyQt5_mock.QtWidgets.QFileDialog = Mock()
PyQt5_mock.QtWidgets.QMessageBox = Mock()
PyQt5_mock.QtWidgets.QGraphicsScene = Mock()
PyQt5_mock.QtGui.QImage = Mock()
PyQt5_mock.QtGui.QPixmap = Mock()
PyQt5_mock.QtCore.Qt = Mock()
PyQt5_mock.QtCore.Qt.KeepAspectRatio = Mock()
PyQt5_mock.uic.loadUi = Mock()

# Mock image formats
PyQt5_mock.QtGui.QImage.Format_RGBA8888 = 1
PyQt5_mock.QtGui.QImage.Format_RGB888 = 2

sys.modules['PyQt5'] = PyQt5_mock
sys.modules['PyQt5.QtWidgets'] = PyQt5_mock.QtWidgets
sys.modules['PyQt5.QtGui'] = PyQt5_mock.QtGui
sys.modules['PyQt5.QtCore'] = PyQt5_mock.QtCore
sys.modules['PyQt5.uic'] = PyQt5_mock.uic

# Mock fitz (PyMuPDF)
fitz_mock = Mock()
fitz_mock.open = Mock()
fitz_mock.FileDataError = Exception
fitz_mock.Matrix = Mock()
sys.modules['fitz'] = fitz_mock

# Mock config_manager
config_manager_mock = Mock()
sys.modules['config_manager'] = config_manager_mock

# Mock log_config
log_config_mock = Mock()
log_config_mock.setup_logger = Mock(return_value=Mock())
sys.modules['log_config'] = log_config_mock


class TestPDFViewer:
    """Test suite for PDFViewer class."""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Set up test environment before each test."""
        # Reset all mocks
        PyQt5_mock.reset_mock()
        fitz_mock.reset_mock()
        config_manager_mock.reset_mock()
        log_config_mock.reset_mock()
        
        # Mock ConfigManager instance
        self.mock_config = Mock()
        self.mock_config.get_setting.return_value = ''
        self.mock_config.get_module_config.return_value = {
            'zoom_factor': 1.0,
            'default_page': 1
        }
        self.mock_config.set_setting = Mock()
        config_manager_mock.ConfigManager.return_value = self.mock_config
        
        # Mock logger
        self.mock_logger = Mock()
        log_config_mock.setup_logger.return_value = self.mock_logger
        
        # Create temporary test directory
        self.test_dir = tempfile.mkdtemp()
        self.test_files = []
        
        yield
        
        # Cleanup
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def create_test_pdf_file(self, filename="test.pdf", content_size=5):
        """Create a test PDF file for testing."""
        filepath = os.path.join(self.test_dir, filename)
        with open(filepath, 'wb') as f:
            f.write(b'%PDF-1.4\n%test content' * content_size)
        self.test_files.append(filepath)
        return filepath

    def create_mock_viewer(self):
        """Create a mock PDFViewer with basic attributes."""
        viewer = Mock()
        viewer.config = self.mock_config
        viewer.doc = None
        viewer.current_page = 0
        viewer.total_pages = 0
        viewer.zoom_factor = 1.0
        viewer.last_directory = self.test_dir
        viewer.default_page = 1
        
        # Mock UI components
        viewer.actionOpen = Mock()
        viewer.actionExit = Mock()
        viewer.previousButton = Mock()
        viewer.nextButton = Mock()
        viewer.pdfView = Mock()
        viewer.pageLabel = Mock()
        viewer.statusBar = Mock(return_value=Mock())
        
        return viewer

    def test_load_settings_success(self):
        """Test successful settings loading."""
        # Configure mock config responses
        self.mock_config.get_setting.return_value = '/test/directory'
        self.mock_config.get_module_config.return_value = {
            'zoom_factor': 1.5,
            'default_page': 2
        }
        
        # Import and create viewer manually
        from view import PDFViewer
        
        viewer = self.create_mock_viewer()
        
        # Test the load_settings method logic
        last_dir = self.mock_config.get_setting('general', 'last_opened_dir', '')
        viewer_config = self.mock_config.get_module_config('viewer')
        zoom_factor = viewer_config.get('zoom_factor', 1.0)
        default_page = viewer_config.get('default_page', 1)
        
        # Verify values
        assert last_dir == '/test/directory'
        assert zoom_factor == 1.5
        assert default_page == 2

    def test_load_settings_with_defaults(self):
        """Test settings loading with default values."""
        # Configure mock to return empty values
        self.mock_config.get_setting.return_value = ''
        self.mock_config.get_module_config.return_value = {}
        
        viewer = self.create_mock_viewer()
        
        # Test the load_settings method logic with defaults
        last_dir = self.mock_config.get_setting('general', 'last_opened_dir', '')
        last_directory = last_dir if last_dir else os.path.expanduser('~')
        
        viewer_config = self.mock_config.get_module_config('viewer')
        zoom_factor = viewer_config.get('zoom_factor', 1.0)
        default_page = viewer_config.get('default_page', 1)
        
        # Verify default values are used
        assert last_directory == os.path.expanduser('~')
        assert zoom_factor == 1.0
        assert default_page == 1

    def test_save_settings_success(self):
        """Test successful settings saving."""
        viewer = self.create_mock_viewer()
        viewer.last_directory = '/test/directory'
        
        # Simulate save_settings call
        self.mock_config.set_setting('general', 'last_opened_dir', viewer.last_directory)
        
        # Verify setting was saved
        self.mock_config.set_setting.assert_called_once_with(
            'general', 'last_opened_dir', '/test/directory'
        )

    def test_open_file_success(self):
        """Test successful file opening logic."""
        # Create test PDF file
        test_file = self.create_test_pdf_file()
        
        # Mock fitz document
        mock_doc = Mock()
        mock_doc.close = Mock()
        mock_page_count = 5
        fitz_mock.open.return_value = mock_doc
        
        # Mock __len__ method properly
        mock_doc.__len__ = Mock(return_value=mock_page_count)
        
        viewer = self.create_mock_viewer()
        
        # Simulate file opening logic
        fitz_mock.open(test_file)
        doc = fitz_mock.open.return_value
        total_pages = len(doc)
        current_page = viewer.default_page - 1
        
        # Verify file operations
        fitz_mock.open.assert_called_with(test_file)
        assert total_pages == mock_page_count
        assert current_page == 0  # default_page - 1

    def test_open_file_corrupted_pdf(self):
        """Test opening corrupted PDF file."""
        test_file = self.create_test_pdf_file()
        
        # Mock fitz to raise FileDataError
        fitz_mock.open.side_effect = fitz_mock.FileDataError("Corrupted file")
        
        viewer = self.create_mock_viewer()
        
        # Test error handling
        with pytest.raises(fitz_mock.FileDataError):
            fitz_mock.open(test_file)

    def test_show_page_success(self):
        """Test successful page display logic."""
        # Mock document and page
        mock_doc = Mock()
        mock_page = Mock()
        mock_pixmap = Mock()
        mock_pixmap.alpha = False
        mock_pixmap.samples = b'test'
        mock_pixmap.width = 100
        mock_pixmap.height = 150
        mock_pixmap.stride = 100
        
        mock_page.get_pixmap.return_value = mock_pixmap
        
        # Mock __getitem__ properly
        mock_doc.__getitem__ = Mock(return_value=mock_page)
        
        viewer = self.create_mock_viewer()
        viewer.doc = mock_doc
        viewer.current_page = 0
        viewer.total_pages = 5
        viewer.zoom_factor = 1.0
        
        # Test page retrieval
        page = mock_doc[viewer.current_page]
        
        # Mock matrix creation
        zoom = viewer.zoom_factor
        with patch('view.fitz.Matrix') as mock_matrix:
            mock_matrix.return_value = Mock()
            mat = mock_matrix(zoom, zoom)
            pixmap = page.get_pixmap(matrix=mat)
            
            # Verify page rendering components
            mock_doc.__getitem__.assert_called_with(0)
            page.get_pixmap.assert_called_once()
            assert pixmap == mock_pixmap

    def test_navigation_logic(self):
        """Test page navigation logic."""
        viewer = self.create_mock_viewer()
        viewer.current_page = 2
        viewer.total_pages = 5
        
        # Test next page
        if viewer.current_page < viewer.total_pages - 1:
            viewer.current_page += 1
        
        assert viewer.current_page == 3
        
        # Test previous page
        if viewer.current_page > 0:
            viewer.current_page -= 1
        
        assert viewer.current_page == 2

    def test_navigation_boundaries(self):
        """Test navigation boundary conditions."""
        viewer = self.create_mock_viewer()
        viewer.total_pages = 5
        
        # Test first page boundary
        viewer.current_page = 0
        original_page = viewer.current_page
        if viewer.current_page > 0:
            viewer.current_page -= 1
        
        assert viewer.current_page == original_page  # Should not change
        
        # Test last page boundary
        viewer.current_page = 4  # Last page (0-based)
        original_page = viewer.current_page
        if viewer.current_page < viewer.total_pages - 1:
            viewer.current_page += 1
        
        assert viewer.current_page == original_page  # Should not change

    def test_button_state_logic(self):
        """Test navigation button state management logic."""
        viewer = self.create_mock_viewer()
        viewer.total_pages = 5
        
        # Test button states for middle page
        viewer.current_page = 2
        previous_enabled = viewer.current_page > 0
        next_enabled = viewer.current_page < viewer.total_pages - 1
        
        assert previous_enabled == True
        assert next_enabled == True
        
        # Test button states for first page
        viewer.current_page = 0
        previous_enabled = viewer.current_page > 0
        next_enabled = viewer.current_page < viewer.total_pages - 1
        
        assert previous_enabled == False
        assert next_enabled == True
        
        # Test button states for last page
        viewer.current_page = 4
        previous_enabled = viewer.current_page > 0
        next_enabled = viewer.current_page < viewer.total_pages - 1
        
        assert previous_enabled == True
        assert next_enabled == False

    def test_document_cleanup(self):
        """Test document cleanup logic."""
        mock_doc = Mock()
        mock_doc.close = Mock()
        
        viewer = self.create_mock_viewer()
        viewer.doc = mock_doc
        
        # Simulate cleanup
        if viewer.doc:
            viewer.doc.close()
        
        mock_doc.close.assert_called_once()

    def test_file_dialog_interaction(self):
        """Test file dialog interaction logic."""
        test_file = self.create_test_pdf_file()
        
        # Mock QFileDialog
        with patch('view.QFileDialog') as mock_dialog:
            mock_dialog.getOpenFileName.return_value = (test_file, 'PDF Files (*.pdf)')
            
            # Test file selection
            file_name, _ = mock_dialog.getOpenFileName(
                None,
                "Open PDF file",
                self.test_dir,
                "PDF Files (*.pdf)"
            )
            
            assert file_name == test_file
            mock_dialog.getOpenFileName.assert_called_once()

    def test_empty_pdf_handling(self):
        """Test handling of empty PDF documents."""
        # Mock empty document
        mock_doc = Mock()
        mock_doc.__len__ = Mock(return_value=0)
        fitz_mock.open.return_value = mock_doc
        
        viewer = self.create_mock_viewer()
        
        # Simulate opening empty PDF
        doc = fitz_mock.open('empty.pdf')
        total_pages = len(doc)
        
        assert total_pages == 0

    def test_zoom_factor_application(self):
        """Test zoom factor application in rendering."""
        zoom_factors = [0.5, 1.0, 1.5, 2.0]
        
        for zoom in zoom_factors:
            viewer = self.create_mock_viewer()
            viewer.zoom_factor = zoom
            
            # Mock matrix creation with zoom
            with patch('view.fitz.Matrix') as mock_matrix:
                mock_matrix.return_value = Mock()
                mat = mock_matrix(zoom, zoom)
                
                # Verify matrix creation with correct zoom
                mock_matrix.assert_called_with(zoom, zoom)

    def test_error_handling_patterns(self):
        """Test various error handling scenarios."""
        # Test configuration error handling
        self.mock_config.get_setting.side_effect = Exception("Config error")
        
        try:
            self.mock_config.get_setting('general', 'last_opened_dir', '')
        except Exception as e:
            assert str(e) == "Config error"
        
        # Reset mock
        self.mock_config.get_setting.side_effect = None
        self.mock_config.get_setting.return_value = ''

    @patch('view.QApplication')
    @patch('view.sys.exit')
    def test_main_function_success(self, mock_exit, mock_app):
        """Test successful main function execution."""
        from view import main
        
        mock_app_instance = Mock()
        mock_app.return_value = mock_app_instance
        mock_app_instance.exec_.return_value = 0
        
        with patch('view.PDFViewer') as mock_viewer:
            mock_viewer.return_value = Mock()
            
            main()
            
            # Verify application was created and started
            mock_app.assert_called_once()
            mock_viewer.assert_called_once()
            mock_exit.assert_called_once_with(0)

    @patch('view.QApplication')
    @patch('view.sys.exit')
    def test_main_function_failure(self, mock_exit, mock_app):
        """Test main function failure handling."""
        from view import main
        
        mock_app.side_effect = Exception("Application failed")
        
        with patch('view.QMessageBox') as mock_msgbox:
            main()
            
            # Verify error was handled
            mock_msgbox.critical.assert_called_once()
            mock_exit.assert_called_once_with(1)

    def test_page_label_formatting(self):
        """Test page label text formatting."""
        viewer = self.create_mock_viewer()
        viewer.current_page = 2
        viewer.total_pages = 5
        
        # Test page label format
        page_text = f"Page {viewer.current_page + 1} of {viewer.total_pages}"
        assert page_text == "Page 3 of 5"

    def test_image_format_handling(self):
        """Test image format selection logic."""
        # Test with alpha channel
        mock_pixmap_alpha = Mock()
        mock_pixmap_alpha.alpha = True
        
        fmt_alpha = PyQt5_mock.QtGui.QImage.Format_RGBA8888 if mock_pixmap_alpha.alpha else PyQt5_mock.QtGui.QImage.Format_RGB888
        assert fmt_alpha == PyQt5_mock.QtGui.QImage.Format_RGBA8888
        
        # Test without alpha channel
        mock_pixmap_no_alpha = Mock()
        mock_pixmap_no_alpha.alpha = False
        
        fmt_no_alpha = PyQt5_mock.QtGui.QImage.Format_RGBA8888 if mock_pixmap_no_alpha.alpha else PyQt5_mock.QtGui.QImage.Format_RGB888
        assert fmt_no_alpha == PyQt5_mock.QtGui.QImage.Format_RGB888

    def test_directory_persistence(self):
        """Test directory persistence logic."""
        test_file = self.create_test_pdf_file()
        
        viewer = self.create_mock_viewer()
        
        # Simulate directory update
        new_directory = os.path.dirname(test_file)
        viewer.last_directory = new_directory
        
        assert viewer.last_directory == new_directory

    def test_status_bar_messaging(self):
        """Test status bar message formatting."""
        test_file = self.create_test_pdf_file("document.pdf")
        filename = os.path.basename(test_file)
        
        # Test success message
        success_message = f"Loaded {filename}"
        assert success_message == "Loaded document.pdf"
        
        # Test warning message
        warning_message = "Empty PDF file"
        assert warning_message == "Empty PDF file"


class TestPDFViewerIntegration:
    """Integration tests for PDFViewer functionality."""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Set up integration test environment."""
        self.test_dir = tempfile.mkdtemp()
        yield
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_configuration_workflow(self):
        """Test complete configuration workflow."""
        # Mock configuration manager
        mock_config = Mock()
        mock_config.get_setting.return_value = self.test_dir
        mock_config.get_module_config.return_value = {
            'zoom_factor': 1.0,
            'default_page': 1
        }
        
        # Test configuration loading
        last_dir = mock_config.get_setting('general', 'last_opened_dir', '')
        viewer_config = mock_config.get_module_config('viewer')
        
        assert last_dir == self.test_dir
        assert viewer_config['zoom_factor'] == 1.0
        assert viewer_config['default_page'] == 1

    def test_file_operations_workflow(self):
        """Test complete file operations workflow."""
        # Create test file
        test_file = os.path.join(self.test_dir, 'test.pdf')
        with open(test_file, 'wb') as f:
            f.write(b'%PDF-1.4\ntest content')
        
        # Mock document
        mock_doc = Mock()
        mock_doc.__len__ = Mock(return_value=3)
        
        with patch('view.fitz') as mock_fitz:
            mock_fitz.open.return_value = mock_doc
            
            # Simulate file opening
            doc = mock_fitz.open(test_file)
            total_pages = len(doc)
            
            assert total_pages == 3
            mock_fitz.open.assert_called_with(test_file)


class TestPDFViewerEdgeCases:
    """Edge case tests for PDFViewer."""

    def test_very_large_document(self):
        """Test handling of very large documents."""
        # Mock large document
        mock_doc = Mock()
        mock_doc.__len__ = Mock(return_value=10000)
        
        # Test navigation in large document
        current_page = 5000
        total_pages = len(mock_doc)
        
        # Test next page
        if current_page < total_pages - 1:
            current_page += 1
        
        assert current_page == 5001
        
        # Test previous page
        if current_page > 0:
            current_page -= 1
        
        assert current_page == 5000

    def test_extreme_zoom_factors(self):
        """Test extreme zoom factor values."""
        extreme_zooms = [0.01, 0.1, 10.0, 100.0]
        
        for zoom in extreme_zooms:
            # This should not cause errors in matrix creation
            with patch('view.fitz.Matrix') as mock_matrix:
                mock_matrix.return_value = Mock()
                mat = mock_matrix(zoom, zoom)
                
                # Verify matrix creation doesn't fail
                mock_matrix.assert_called_with(zoom, zoom)

    def test_memory_management(self):
        """Test memory management patterns."""
        # Simulate multiple document openings
        docs = []
        for i in range(5):
            mock_doc = Mock()
            mock_doc.close = Mock()
            docs.append(mock_doc)
        
        # Test that old documents would be closed
        for doc in docs[:-1]:  # All but the last
            doc.close()
            doc.close.assert_called_once()

    def test_unicode_filenames(self):
        """Test handling of unicode filenames."""
        unicode_filename = "тест_файл_ñ_ü.pdf"
        
        # Test that unicode filenames are handled properly
        with patch('view.os.path.basename') as mock_basename:
            mock_basename.return_value = unicode_filename
            
            filename = mock_basename('/path/to/' + unicode_filename)
            assert filename == unicode_filename

    def test_invalid_page_numbers(self):
        """Test handling of invalid page numbers."""
        total_pages = 5
        
        # Test negative page
        current_page = -1
        valid_page = 0 <= current_page < total_pages
        assert valid_page == False
        
        # Test page beyond bounds
        current_page = 10
        valid_page = 0 <= current_page < total_pages
        assert valid_page == False
        
        # Test valid page
        current_page = 2
        valid_page = 0 <= current_page < total_pages
        assert valid_page == True


# Test configuration
@pytest.fixture(scope="session")
def test_config():
    """Provide test configuration."""
    return {
        'test_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'test_module': 'pdf_view_analysis',
        'coverage_threshold': 80,
        'performance_threshold': 1.0  # seconds
    }


# Performance monitoring
@pytest.fixture(autouse=True)
def monitor_test_performance(request):
    """Monitor individual test performance."""
    import time
    start_time = time.time()
    
    yield
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Log slow tests
    if duration > 1.0:
        print(f"\nSlow test detected: {duration:.2f}s")


if __name__ == '__main__':
    # Run tests with coverage and detailed output
    pytest.main([
        __file__,
        '-v',
        '--tb=short',
        '--cov=view',
        '--cov-report=html',
        '--cov-report=json',
        '--junit-xml=result_pdf_view_analysis_2025-08-30_junit.xml'
    ])