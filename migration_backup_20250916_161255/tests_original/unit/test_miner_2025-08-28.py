"""
Comprehensive unit tests for miner.py
Created: 2025-08-28
Test Coverage: MainWindow and PDFMiner classes with all methods and edge cases
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock, call
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt
import fitz  # PyMuPDF

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

# Import the modules under test
from src.utilities.pdf_tools.pdf_view_analysis.miner import MainWindow, PDFMiner


class TestPDFMiner:
    """Test suite for PDFMiner class"""
    
    def setup_method(self):
        """Setup test data and mocks before each test"""
        self.test_pdf_path = "test_document.pdf"
        self.mock_pdf_doc = Mock()
        self.mock_first_page = Mock()
        
        # Setup mock first page with rect
        self.mock_first_page.rect.width = 800
        self.mock_first_page.rect.height = 600
        
        # Setup mock pdf document
        self.mock_pdf_doc.load_page.return_value = self.mock_first_page
        self.mock_pdf_doc.metadata = {
            'title': 'Test Document',
            'author': 'Test Author',
            'subject': 'Test Subject',
            'creator': 'Test Creator'
        }
        self.mock_pdf_doc.page_count = 5
        
    def teardown_method(self):
        """Cleanup after each test"""
        pass
    
    @patch('src.utilities.pdf_tools.pdf_view_analysis.miner.fitz.open')
    def test_pdf_miner_initialization_success(self, mock_fitz_open):
        """Test successful PDFMiner initialization"""
        mock_fitz_open.return_value = self.mock_pdf_doc
        
        miner = PDFMiner(self.test_pdf_path)
        
        assert miner.filepath == self.test_pdf_path
        assert miner.pdf == self.mock_pdf_doc
        assert miner.first_page == self.mock_first_page
        assert miner.width == 800
        assert miner.height == 600
        assert miner.zoom == 0.8  # Based on 800px width
        mock_fitz_open.assert_called_once_with(self.test_pdf_path)
    
    @patch('src.utilities.pdf_tools.pdf_view_analysis.miner.fitz.open')
    def test_pdf_miner_initialization_different_widths(self, mock_fitz_open):
        """Test PDFMiner initialization with different page widths"""
        test_cases = [
            (700, 0.6),
            (600, 1.0), 
            (500, 1.0),
            (900, 0.8)  # Default case for widths not in dict
        ]
        
        for width, expected_zoom in test_cases:
            self.mock_first_page.rect.width = width
            mock_fitz_open.return_value = self.mock_pdf_doc
            
            miner = PDFMiner(self.test_pdf_path)
            
            assert miner.zoom == expected_zoom
            assert miner.width == width
    
    @patch('src.utilities.pdf_tools.pdf_view_analysis.miner.fitz.open')
    def test_pdf_miner_initialization_file_not_found(self, mock_fitz_open):
        """Test PDFMiner initialization with non-existent file"""
        mock_fitz_open.side_effect = FileNotFoundError("File not found")
        
        with pytest.raises(FileNotFoundError):
            PDFMiner("nonexistent.pdf")
    
    @patch('src.utilities.pdf_tools.pdf_view_analysis.miner.fitz.open')
    def test_pdf_miner_initialization_invalid_pdf(self, mock_fitz_open):
        """Test PDFMiner initialization with invalid PDF"""
        mock_fitz_open.side_effect = RuntimeError("Invalid PDF")
        
        with pytest.raises(RuntimeError):
            PDFMiner("invalid.pdf")
    
    @patch('src.utilities.pdf_tools.pdf_view_analysis.miner.fitz.open')
    def test_get_metadata_success(self, mock_fitz_open):
        """Test successful metadata retrieval"""
        mock_fitz_open.return_value = self.mock_pdf_doc
        miner = PDFMiner(self.test_pdf_path)
        
        metadata, num_pages = miner.get_metadata()
        
        assert metadata == self.mock_pdf_doc.metadata
        assert num_pages == 5
    
    @patch('src.utilities.pdf_tools.pdf_view_analysis.miner.fitz.open')
    def test_get_metadata_empty_metadata(self, mock_fitz_open):
        """Test metadata retrieval with empty metadata"""
        self.mock_pdf_doc.metadata = {}
        self.mock_pdf_doc.page_count = 0
        mock_fitz_open.return_value = self.mock_pdf_doc
        miner = PDFMiner(self.test_pdf_path)
        
        metadata, num_pages = miner.get_metadata()
        
        assert metadata == {}
        assert num_pages == 0
    
    @patch('src.utilities.pdf_tools.pdf_view_analysis.miner.fitz.open')
    def test_get_page_with_zoom(self, mock_fitz_open):
        """Test page retrieval with zoom applied"""
        mock_fitz_open.return_value = self.mock_pdf_doc
        mock_page = Mock()
        mock_pixmap = Mock()
        mock_pixmap.samples = b'\x00' * 1000  # Mock image data
        mock_pixmap.width = 400
        mock_pixmap.height = 300
        mock_pixmap.stride = 1200
        mock_page.get_pixmap.return_value = mock_pixmap
        self.mock_pdf_doc.load_page.return_value = mock_page
        
        miner = PDFMiner(self.test_pdf_path)
        
        with patch('src.utilities.pdf_tools.pdf_view_analysis.miner.QImage') as mock_qimage:
            mock_qimage_instance = Mock()
            mock_qimage.return_value = mock_qimage_instance
            
            result = miner.get_page(0)
            
            # Verify page loading and pixmap generation
            self.mock_pdf_doc.load_page.assert_called_with(0)
            mock_page.get_pixmap.assert_called_once()
            
            # Verify QImage creation
            mock_qimage.assert_called_once_with(
                mock_pixmap.samples,
                mock_pixmap.width,
                mock_pixmap.height,
                mock_pixmap.stride,
                QImage.Format_RGB888
            )
            assert result == mock_qimage_instance
    
    @patch('src.utilities.pdf_tools.pdf_view_analysis.miner.fitz.open')
    def test_get_page_without_zoom(self, mock_fitz_open):
        """Test page retrieval without zoom"""
        # Set zoom to None/False
        self.mock_first_page.rect.width = 1000  # Will result in default zoom
        mock_fitz_open.return_value = self.mock_pdf_doc
        mock_page = Mock()
        mock_pixmap = Mock()
        mock_pixmap.samples = b'\x00' * 1000
        mock_pixmap.width = 400
        mock_pixmap.height = 300
        mock_pixmap.stride = 1200
        mock_page.get_pixmap.return_value = mock_pixmap
        self.mock_pdf_doc.load_page.return_value = mock_page
        
        miner = PDFMiner(self.test_pdf_path)
        miner.zoom = None  # Force no zoom
        
        with patch('src.utilities.pdf_tools.pdf_view_analysis.miner.QImage') as mock_qimage:
            mock_qimage_instance = Mock()
            mock_qimage.return_value = mock_qimage_instance
            
            result = miner.get_page(0)
            
            # Verify pixmap generation without matrix
            mock_page.get_pixmap.assert_called_once_with()
            assert result == mock_qimage_instance
    
    @patch('src.utilities.pdf_tools.pdf_view_analysis.miner.fitz.open')
    def test_get_page_invalid_page_number(self, mock_fitz_open):
        """Test page retrieval with invalid page number"""
        mock_fitz_open.return_value = self.mock_pdf_doc
        self.mock_pdf_doc.load_page.side_effect = IndexError("Page index out of range")
        
        miner = PDFMiner(self.test_pdf_path)
        
        with pytest.raises(IndexError):
            miner.get_page(10)  # Page doesn't exist
    
    @patch('src.utilities.pdf_tools.pdf_view_analysis.miner.fitz.open')
    def test_get_text_success(self, mock_fitz_open):
        """Test successful text extraction"""
        mock_fitz_open.return_value = self.mock_pdf_doc
        mock_page = Mock()
        expected_text = "This is sample text from the PDF"
        mock_page.getText.return_value = expected_text
        self.mock_pdf_doc.load_page.return_value = mock_page
        
        miner = PDFMiner(self.test_pdf_path)
        result = miner.get_text(0)
        
        assert result == expected_text
        self.mock_pdf_doc.load_page.assert_called_with(0)
        mock_page.getText.assert_called_with('text')
    
    @patch('src.utilities.pdf_tools.pdf_view_analysis.miner.fitz.open')
    def test_get_text_empty_page(self, mock_fitz_open):
        """Test text extraction from empty page"""
        mock_fitz_open.return_value = self.mock_pdf_doc
        mock_page = Mock()
        mock_page.getText.return_value = ""
        self.mock_pdf_doc.load_page.return_value = mock_page
        
        miner = PDFMiner(self.test_pdf_path)
        result = miner.get_text(0)
        
        assert result == ""
    
    @patch('src.utilities.pdf_tools.pdf_view_analysis.miner.fitz.open')
    def test_get_text_invalid_page_number(self, mock_fitz_open):
        """Test text extraction with invalid page number"""
        mock_fitz_open.return_value = self.mock_pdf_doc
        self.mock_pdf_doc.load_page.side_effect = IndexError("Page index out of range")
        
        miner = PDFMiner(self.test_pdf_path)
        
        with pytest.raises(IndexError):
            miner.get_text(-1)  # Invalid page number


class TestMainWindow:
    """Test suite for MainWindow class"""
    
    @pytest.fixture(autouse=True)
    def setup_qapp(self):
        """Setup QApplication for GUI tests"""
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
        yield
        # Cleanup is handled by pytest automatically
    
    def setup_method(self):
        """Setup test data before each test"""
        self.mock_ui_file = "miner.ui"
    
    @patch('src.utilities.pdf_tools.pdf_view_analysis.miner.uic.loadUi')
    def test_main_window_initialization(self, mock_load_ui):
        """Test MainWindow initialization"""
        with patch.object(MainWindow, 'actionExit') as mock_exit, \
             patch.object(MainWindow, 'actionOpen') as mock_open:
            
            mock_exit.triggered = Mock()
            mock_open.triggered = Mock()
            
            window = MainWindow()
            
            assert window.pdf_miner is None
            assert window.current_page == 0
            mock_load_ui.assert_called_once_with('miner.ui', window)
            mock_exit.triggered.connect.assert_called_once()
            mock_open.triggered.connect.assert_called_once()
    
    @patch('src.utilities.pdf_tools.pdf_view_analysis.miner.uic.loadUi')
    @patch('src.utilities.pdf_tools.pdf_view_analysis.miner.QFileDialog.getOpenFileName')
    @patch('src.utilities.pdf_tools.pdf_view_analysis.miner.PDFMiner')
    def test_open_pdf_success(self, mock_pdf_miner_class, mock_file_dialog, mock_load_ui):
        """Test successful PDF opening"""
        # Setup mocks
        test_filepath = "/path/to/test.pdf"
        mock_file_dialog.return_value = (test_filepath, "PDF files (*.pdf)")
        mock_pdf_miner_instance = Mock()
        mock_pdf_miner_class.return_value = mock_pdf_miner_instance
        
        with patch.object(MainWindow, 'actionExit') as mock_exit, \
             patch.object(MainWindow, 'actionOpen') as mock_open, \
             patch.object(MainWindow, 'show_page') as mock_show_page:
            
            mock_exit.triggered = Mock()
            mock_open.triggered = Mock()
            
            window = MainWindow()
            window.open_pdf()
            
            # Verify file dialog was called
            mock_file_dialog.assert_called_once_with(
                window, "Open PDF", "", "PDF files (*.pdf)"
            )
            
            # Verify PDFMiner was created
            mock_pdf_miner_class.assert_called_once_with(test_filepath)
            assert window.pdf_miner == mock_pdf_miner_instance
            
            # Verify show_page was called
            mock_show_page.assert_called_once_with(0)
    
    @patch('src.utilities.pdf_tools.pdf_view_analysis.miner.uic.loadUi')
    @patch('src.utilities.pdf_tools.pdf_view_analysis.miner.QFileDialog.getOpenFileName')
    def test_open_pdf_cancelled(self, mock_file_dialog, mock_load_ui):
        """Test PDF opening when user cancels dialog"""
        # User cancels dialog
        mock_file_dialog.return_value = ("", "")
        
        with patch.object(MainWindow, 'actionExit') as mock_exit, \
             patch.object(MainWindow, 'actionOpen') as mock_open:
            
            mock_exit.triggered = Mock()
            mock_open.triggered = Mock()
            
            window = MainWindow()
            initial_pdf_miner = window.pdf_miner
            window.open_pdf()
            
            # Verify PDFMiner was not created
            assert window.pdf_miner == initial_pdf_miner  # Should remain None
    
    @patch('src.utilities.pdf_tools.pdf_view_analysis.miner.uic.loadUi')
    @patch('src.utilities.pdf_tools.pdf_view_analysis.miner.QFileDialog.getOpenFileName')
    @patch('src.utilities.pdf_tools.pdf_view_analysis.miner.PDFMiner')
    def test_open_pdf_invalid_file(self, mock_pdf_miner_class, mock_file_dialog, mock_load_ui):
        """Test PDF opening with invalid file"""
        test_filepath = "/path/to/invalid.pdf"
        mock_file_dialog.return_value = (test_filepath, "PDF files (*.pdf)")
        mock_pdf_miner_class.side_effect = RuntimeError("Invalid PDF")
        
        with patch.object(MainWindow, 'actionExit') as mock_exit, \
             patch.object(MainWindow, 'actionOpen') as mock_open:
            
            mock_exit.triggered = Mock()
            mock_open.triggered = Mock()
            
            window = MainWindow()
            
            with pytest.raises(RuntimeError):
                window.open_pdf()
    
    @patch('src.utilities.pdf_tools.pdf_view_analysis.miner.uic.loadUi')
    def test_show_page_with_pdf_miner(self, mock_load_ui):
        """Test show_page with valid PDF miner"""
        with patch.object(MainWindow, 'actionExit') as mock_exit, \
             patch.object(MainWindow, 'actionOpen') as mock_open, \
             patch.object(MainWindow, 'pdfView') as mock_pdf_view:
            
            mock_exit.triggered = Mock()
            mock_open.triggered = Mock()
            mock_pdf_view.setPixmap = Mock()
            
            # Create mock PDFMiner and QImage
            mock_pdf_miner = Mock()
            mock_qimage = Mock()
            mock_pdf_miner.get_page.return_value = mock_qimage
            
            window = MainWindow()
            window.pdf_miner = mock_pdf_miner
            
            with patch('src.utilities.pdf_tools.pdf_view_analysis.miner.QPixmap.fromImage') as mock_from_image:
                mock_pixmap = Mock()
                mock_from_image.return_value = mock_pixmap
                
                window.show_page(2)
                
                # Verify get_page was called with correct page number
                mock_pdf_miner.get_page.assert_called_once_with(2)
                
                # Verify QPixmap creation and setting
                mock_from_image.assert_called_once_with(mock_qimage)
                mock_pdf_view.setPixmap.assert_called_once_with(mock_pixmap)
    
    @patch('src.utilities.pdf_tools.pdf_view_analysis.miner.uic.loadUi')
    def test_show_page_without_pdf_miner(self, mock_load_ui):
        """Test show_page without PDF miner"""
        with patch.object(MainWindow, 'actionExit') as mock_exit, \
             patch.object(MainWindow, 'actionOpen') as mock_open, \
             patch.object(MainWindow, 'pdfView') as mock_pdf_view:
            
            mock_exit.triggered = Mock()
            mock_open.triggered = Mock()
            mock_pdf_view.setPixmap = Mock()
            
            window = MainWindow()
            # pdf_miner remains None
            
            window.show_page(2)
            
            # Verify setPixmap was not called
            mock_pdf_view.setPixmap.assert_not_called()
    
    @patch('src.utilities.pdf_tools.pdf_view_analysis.miner.uic.loadUi')
    def test_close_action(self, mock_load_ui):
        """Test window close action"""
        with patch.object(MainWindow, 'actionExit') as mock_exit, \
             patch.object(MainWindow, 'actionOpen') as mock_open, \
             patch.object(MainWindow, 'close') as mock_close:
            
            mock_exit.triggered = Mock()
            mock_open.triggered = Mock()
            
            window = MainWindow()
            
            # Simulate exit action trigger
            connected_method = mock_exit.triggered.connect.call_args[0][0]
            assert connected_method == window.close


class TestMainWindowEdgeCases:
    """Additional edge case tests for MainWindow"""
    
    @pytest.fixture(autouse=True)
    def setup_qapp(self):
        """Setup QApplication for GUI tests"""
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
        yield
    
    @patch('src.utilities.pdf_tools.pdf_view_analysis.miner.uic.loadUi')
    def test_ui_file_not_found(self, mock_load_ui):
        """Test handling when UI file is not found"""
        mock_load_ui.side_effect = FileNotFoundError("UI file not found")
        
        with patch.object(MainWindow, 'actionExit', create=True) as mock_exit, \
             patch.object(MainWindow, 'actionOpen', create=True) as mock_open:
            
            mock_exit.triggered = Mock()
            mock_open.triggered = Mock()
            
            with pytest.raises(FileNotFoundError):
                MainWindow()
    
    @patch('src.utilities.pdf_tools.pdf_view_analysis.miner.uic.loadUi')
    @patch('src.utilities.pdf_tools.pdf_view_analysis.miner.QFileDialog.getOpenFileName')
    def test_multiple_pdf_opens(self, mock_file_dialog, mock_load_ui):
        """Test opening multiple PDFs in sequence"""
        with patch.object(MainWindow, 'actionExit') as mock_exit, \
             patch.object(MainWindow, 'actionOpen') as mock_open, \
             patch.object(MainWindow, 'show_page') as mock_show_page:
            
            mock_exit.triggered = Mock()
            mock_open.triggered = Mock()
            
            window = MainWindow()
            
            # First PDF
            mock_file_dialog.return_value = ("first.pdf", "PDF files (*.pdf)")
            with patch('src.utilities.pdf_tools.pdf_view_analysis.miner.PDFMiner') as mock_miner1:
                mock_instance1 = Mock()
                mock_miner1.return_value = mock_instance1
                window.open_pdf()
                assert window.pdf_miner == mock_instance1
            
            # Second PDF (should replace first)
            mock_file_dialog.return_value = ("second.pdf", "PDF files (*.pdf)")
            with patch('src.utilities.pdf_tools.pdf_view_analysis.miner.PDFMiner') as mock_miner2:
                mock_instance2 = Mock()
                mock_miner2.return_value = mock_instance2
                window.open_pdf()
                assert window.pdf_miner == mock_instance2


class TestIntegration:
    """Integration tests combining PDFMiner and MainWindow"""
    
    @pytest.fixture(autouse=True)
    def setup_qapp(self):
        """Setup QApplication for GUI tests"""
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
        yield
    
    def setup_method(self):
        """Setup test data"""
        self.test_pdf_path = "integration_test.pdf"
    
    @patch('src.utilities.pdf_tools.pdf_view_analysis.miner.uic.loadUi')
    @patch('src.utilities.pdf_tools.pdf_view_analysis.miner.fitz.open')
    @patch('src.utilities.pdf_tools.pdf_view_analysis.miner.QFileDialog.getOpenFileName')
    def test_full_workflow_integration(self, mock_file_dialog, mock_fitz_open, mock_load_ui):
        """Test complete workflow from opening file to displaying page"""
        # Setup file dialog
        mock_file_dialog.return_value = (self.test_pdf_path, "PDF files (*.pdf)")
        
        # Setup PDF document mock
        mock_pdf_doc = Mock()
        mock_first_page = Mock()
        mock_first_page.rect.width = 800
        mock_first_page.rect.height = 600
        mock_pdf_doc.load_page.return_value = mock_first_page
        mock_pdf_doc.metadata = {'title': 'Integration Test'}
        mock_pdf_doc.page_count = 3
        mock_fitz_open.return_value = mock_pdf_doc
        
        # Setup page mock for display
        mock_page = Mock()
        mock_pixmap = Mock()
        mock_pixmap.samples = b'\x00' * 1000
        mock_pixmap.width = 400
        mock_pixmap.height = 300
        mock_pixmap.stride = 1200
        mock_page.get_pixmap.return_value = mock_pixmap
        
        def load_page_side_effect(page_num):
            if page_num == 0:
                return mock_first_page
            else:
                return mock_page
        
        mock_pdf_doc.load_page.side_effect = load_page_side_effect
        
        with patch.object(MainWindow, 'actionExit') as mock_exit, \
             patch.object(MainWindow, 'actionOpen') as mock_open, \
             patch.object(MainWindow, 'pdfView') as mock_pdf_view:
            
            mock_exit.triggered = Mock()
            mock_open.triggered = Mock()
            mock_pdf_view.setPixmap = Mock()
            
            # Create window and open PDF
            window = MainWindow()
            
            with patch('src.utilities.pdf_tools.pdf_view_analysis.miner.QImage') as mock_qimage, \
                 patch('src.utilities.pdf_tools.pdf_view_analysis.miner.QPixmap.fromImage') as mock_from_image:
                
                mock_qimage_instance = Mock()
                mock_qimage.return_value = mock_qimage_instance
                mock_pixmap_instance = Mock()
                mock_from_image.return_value = mock_pixmap_instance
                
                window.open_pdf()
                
                # Verify PDF was opened and displayed
                assert window.pdf_miner is not None
                assert isinstance(window.pdf_miner, PDFMiner)
                
                # Verify metadata access
                metadata, num_pages = window.pdf_miner.get_metadata()
                assert metadata['title'] == 'Integration Test'
                assert num_pages == 3
                
                # Verify page display was called
                mock_pdf_view.setPixmap.assert_called_once_with(mock_pixmap_instance)


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v', '--tb=short'])