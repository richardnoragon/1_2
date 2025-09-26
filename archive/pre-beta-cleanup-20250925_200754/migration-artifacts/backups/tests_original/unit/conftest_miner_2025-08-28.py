"""
Pytest configuration and fixtures for miner.py tests
Created: 2025-08-28
Provides shared fixtures and configuration for PDF miner testing
"""

import pytest
import sys
import os
import tempfile
import shutil
from unittest.mock import Mock, patch
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
import fitz  # PyMuPDF

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance for GUI tests"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    # Clean up is handled automatically by pytest


@pytest.fixture(scope="session")
def test_data_dir():
    """Create temporary directory for test data"""
    temp_dir = tempfile.mkdtemp(prefix="miner_tests_")
    yield temp_dir
    # Cleanup
    try:
        shutil.rmtree(temp_dir)
    except OSError:
        pass  # Directory might already be cleaned up


@pytest.fixture
def mock_pdf_document():
    """Create a mock PDF document for testing"""
    mock_doc = Mock()
    mock_doc.metadata = {
        'title': 'Test Document',
        'author': 'Test Author',
        'subject': 'Test Subject',
        'creator': 'Test Creator',
        'producer': 'Test Producer',
        'creationDate': 'D:20250828000000+00\'00\'',
        'modDate': 'D:20250828000000+00\'00\''
    }
    mock_doc.page_count = 5
    
    # Create mock pages
    mock_pages = []
    for i in range(5):
        mock_page = Mock()
        mock_page.rect.width = 800 if i == 0 else 600
        mock_page.rect.height = 600 if i == 0 else 800
        mock_page.getText.return_value = f"Sample text for page {i + 1}"
        
        # Mock pixmap for page rendering
        mock_pixmap = Mock()
        mock_pixmap.samples = b'\x00' * (800 * 600 * 3)  # RGB data
        mock_pixmap.width = 800
        mock_pixmap.height = 600
        mock_pixmap.stride = 800 * 3
        mock_page.get_pixmap.return_value = mock_pixmap
        
        mock_pages.append(mock_page)
    
    mock_doc.load_page.side_effect = lambda page_num: mock_pages[page_num] if 0 <= page_num < len(mock_pages) else None
    
    return mock_doc


@pytest.fixture
def mock_pdf_file_path(test_data_dir):
    """Create a mock PDF file path"""
    return os.path.join(test_data_dir, "test_document.pdf")


@pytest.fixture
def mock_invalid_pdf_path(test_data_dir):
    """Create a path to non-existent PDF file"""
    return os.path.join(test_data_dir, "nonexistent.pdf")


@pytest.fixture
def mock_empty_pdf_document():
    """Create a mock empty PDF document"""
    mock_doc = Mock()
    mock_doc.metadata = {}
    mock_doc.page_count = 0
    mock_doc.load_page.side_effect = IndexError("Page index out of range")
    return mock_doc


@pytest.fixture
def mock_large_pdf_document():
    """Create a mock large PDF document (100 pages)"""
    mock_doc = Mock()
    mock_doc.metadata = {
        'title': 'Large Test Document',
        'author': 'Test Author',
        'subject': 'Performance Testing'
    }
    mock_doc.page_count = 100
    
    def mock_load_page(page_num):
        if 0 <= page_num < 100:
            mock_page = Mock()
            mock_page.rect.width = 800
            mock_page.rect.height = 600
            mock_page.getText.return_value = f"Page {page_num + 1} content with some sample text"
            
            mock_pixmap = Mock()
            mock_pixmap.samples = b'\x00' * (800 * 600 * 3)
            mock_pixmap.width = 800
            mock_pixmap.height = 600
            mock_pixmap.stride = 800 * 3
            mock_page.get_pixmap.return_value = mock_pixmap
            
            return mock_page
        else:
            raise IndexError("Page index out of range")
    
    mock_doc.load_page.side_effect = mock_load_page
    return mock_doc


@pytest.fixture
def mock_corrupted_pdf_document():
    """Create a mock corrupted PDF document that raises errors"""
    mock_doc = Mock()
    mock_doc.metadata = Mock(side_effect=RuntimeError("Corrupted metadata"))
    mock_doc.page_count = Mock(side_effect=RuntimeError("Cannot read page count"))
    mock_doc.load_page.side_effect = RuntimeError("Corrupted PDF data")
    return mock_doc


@pytest.fixture
def mock_ui_file_content():
    """Mock UI file content for testing"""
    return """<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>MainWindow</class>
 <widget class="QMainWindow" name="MainWindow">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>800</width>
    <height>600</height>
   </rect>
  </property>
  <widget class="QWidget" name="centralwidget">
   <widget class="QLabel" name="pdfView">
    <property name="geometry">
     <rect>
      <x>10</x>
      <y>10</y>
      <width>780</width>
      <height>550</height>
     </rect>
    </property>
   </widget>
  </widget>
  <widget class="QMenuBar" name="menubar">
   <widget class="QMenu" name="menuFile">
    <property name="title">
     <string>File</string>
    </property>
    <addaction name="actionOpen"/>
    <addaction name="actionExit"/>
   </widget>
  </widget>
  <action name="actionOpen">
   <property name="text">
    <string>Open</string>
   </property>
  </action>
  <action name="actionExit">
   <property name="text">
    <string>Exit</string>
   </property>
  </action>
 </widget>
</ui>"""


@pytest.fixture
def sample_pdf_metadata():
    """Sample PDF metadata for testing"""
    return {
        'title': 'Sample PDF Document',
        'author': 'John Doe',
        'subject': 'Testing PDF Metadata',
        'creator': 'PDF Creator Application',
        'producer': 'PDF Producer',
        'creationDate': 'D:20250828120000+00\'00\'',
        'modDate': 'D:20250828150000+00\'00\'',
        'keywords': 'test, pdf, metadata',
        'format': 'PDF-1.4'
    }


@pytest.fixture
def performance_test_config():
    """Configuration for performance tests"""
    return {
        'max_execution_time': 5.0,  # seconds
        'max_memory_usage': 100 * 1024 * 1024,  # 100MB
        'large_pdf_pages': 1000,
        'stress_test_iterations': 50
    }


@pytest.fixture(autouse=True)
def cleanup_after_test():
    """Cleanup fixture that runs after each test"""
    yield
    # Clean up any global state or temporary files
    # This runs after each test method
    pass


def pytest_configure(config):
    """Pytest configuration hook"""
    # Add custom markers
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "unit: mark test as unit test")
    config.addinivalue_line("markers", "gui: mark test as requiring GUI")
    config.addinivalue_line("markers", "pdf: mark test as PDF-related")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically"""
    for item in items:
        # Add unit marker to all tests in unit directory
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        
        # Add GUI marker to tests that use qapp fixture
        if "qapp" in item.fixturenames:
            item.add_marker(pytest.mark.gui)
        
        # Add PDF marker to tests in miner module
        if "miner" in str(item.fspath):
            item.add_marker(pytest.mark.pdf)
        
        # Add slow marker to tests that might be slow
        if any(keyword in item.name.lower() for keyword in ['performance', 'large', 'stress', 'integration']):
            item.add_marker(pytest.mark.slow)


@pytest.fixture
def mock_qt_components():
    """Mock Qt components for testing without actual GUI"""
    mocks = {}
    
    with patch('PyQt5.QtWidgets.QMainWindow') as mock_main_window, \
         patch('PyQt5.QtWidgets.QApplication') as mock_qapp, \
         patch('PyQt5.QtWidgets.QFileDialog') as mock_file_dialog, \
         patch('PyQt5.QtGui.QPixmap') as mock_pixmap, \
         patch('PyQt5.QtGui.QImage') as mock_qimage, \
         patch('PyQt5.uic.loadUi') as mock_load_ui:
        
        mocks['main_window'] = mock_main_window
        mocks['qapp'] = mock_qapp
        mocks['file_dialog'] = mock_file_dialog
        mocks['pixmap'] = mock_pixmap
        mocks['qimage'] = mock_qimage
        mocks['load_ui'] = mock_load_ui
        
        yield mocks


@pytest.fixture
def test_execution_timer():
    """Timer fixture for measuring test execution time"""
    import time
    start_time = time.time()
    yield
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"\nTest execution time: {execution_time:.3f} seconds")


# Custom assertions for PDF testing
class PDFAssertions:
    """Custom assertions for PDF-related testing"""
    
    @staticmethod
    def assert_valid_pdf_metadata(metadata):
        """Assert that metadata is valid PDF metadata"""
        assert isinstance(metadata, dict)
        # Common PDF metadata fields
        expected_fields = ['title', 'author', 'subject', 'creator']
        for field in expected_fields:
            if field in metadata:
                assert isinstance(metadata[field], str)
    
    @staticmethod
    def assert_valid_page_count(page_count):
        """Assert that page count is valid"""
        assert isinstance(page_count, int)
        assert page_count >= 0
    
    @staticmethod
    def assert_valid_page_dimensions(width, height):
        """Assert that page dimensions are valid"""
        assert isinstance(width, (int, float))
        assert isinstance(height, (int, float))
        assert width > 0
        assert height > 0
    
    @staticmethod
    def assert_valid_zoom_factor(zoom):
        """Assert that zoom factor is valid"""
        assert isinstance(zoom, (int, float))
        assert zoom > 0
        assert zoom <= 10  # Reasonable upper limit


@pytest.fixture
def pdf_assertions():
    """Provide PDF assertion utilities"""
    return PDFAssertions()