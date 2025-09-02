"""
Shared test fixtures and configuration for PDF View Analysis testing.

This module provides common fixtures, mocks, and utilities for testing
the PDF View Analysis module (view.py).

Created: 2025-08-30
Target: src/utilities/pdf_tools/pdf_view_analysis/view.py
"""

import json
import os
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

# Configure test environment
TEST_TIMESTAMP = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')


@pytest.fixture(scope="session")
def test_session_info():
    """Provide session-wide test information."""
    return {
        'timestamp': TEST_TIMESTAMP,
        'module': 'pdf_view_analysis',
        'target_file': 'view.py',
        'test_runner': 'pytest',
        'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    }


@pytest.fixture(scope="session")
def mock_pyqt5():
    """Provide session-wide PyQt5 mocking."""
    # Create comprehensive PyQt5 mock
    pyqt5_mock = MagicMock()
    
    # Mock QtWidgets
    pyqt5_mock.QtWidgets = MagicMock()
    pyqt5_mock.QtWidgets.QMainWindow = MagicMock()
    pyqt5_mock.QtWidgets.QApplication = MagicMock()
    pyqt5_mock.QtWidgets.QFileDialog = MagicMock()
    pyqt5_mock.QtWidgets.QMessageBox = MagicMock()
    pyqt5_mock.QtWidgets.QGraphicsScene = MagicMock()
    
    # Mock QtGui
    pyqt5_mock.QtGui = MagicMock()
    pyqt5_mock.QtGui.QImage = MagicMock()
    pyqt5_mock.QtGui.QPixmap = MagicMock()
    
    # Mock QtCore
    pyqt5_mock.QtCore = MagicMock()
    pyqt5_mock.QtCore.Qt = MagicMock()
    pyqt5_mock.QtCore.Qt.KeepAspectRatio = 1
    
    # Mock uic
    pyqt5_mock.uic = MagicMock()
    pyqt5_mock.uic.loadUi = MagicMock()
    
    # Mock image formats
    pyqt5_mock.QtGui.QImage.Format_RGBA8888 = 1
    pyqt5_mock.QtGui.QImage.Format_RGB888 = 2
    
    # Install mocks
    sys.modules['PyQt5'] = pyqt5_mock
    sys.modules['PyQt5.QtWidgets'] = pyqt5_mock.QtWidgets
    sys.modules['PyQt5.QtGui'] = pyqt5_mock.QtGui
    sys.modules['PyQt5.QtCore'] = pyqt5_mock.QtCore
    sys.modules['PyQt5.uic'] = pyqt5_mock.uic
    
    return pyqt5_mock


@pytest.fixture(scope="session")
def mock_fitz():
    """Provide session-wide PyMuPDF (fitz) mocking."""
    fitz_mock = MagicMock()
    
    # Mock document operations
    fitz_mock.open = MagicMock()
    fitz_mock.FileDataError = Exception
    fitz_mock.Matrix = MagicMock()
    
    # Mock document class
    mock_doc = MagicMock()
    mock_doc.close = MagicMock()
    fitz_mock.open.return_value = mock_doc
    
    # Mock page operations
    mock_page = MagicMock()
    mock_pixmap = MagicMock()
    mock_pixmap.alpha = False
    mock_pixmap.samples = b'test_image_data'
    mock_pixmap.width = 100
    mock_pixmap.height = 150
    mock_pixmap.stride = 100
    mock_page.get_pixmap.return_value = mock_pixmap
    mock_doc.__getitem__.return_value = mock_page
    
    # Install mock
    sys.modules['fitz'] = fitz_mock
    
    return fitz_mock


@pytest.fixture(scope="session")
def mock_config_manager():
    """Provide session-wide ConfigManager mocking."""
    config_mock = MagicMock()
    
    # Mock ConfigManager class
    mock_config_instance = MagicMock()
    mock_config_instance.get_setting.return_value = ''
    mock_config_instance.get_module_config.return_value = {
        'zoom_factor': 1.0,
        'default_page': 1
    }
    mock_config_instance.set_setting = MagicMock()
    
    config_mock.ConfigManager.return_value = mock_config_instance
    
    # Install mock
    sys.modules['config_manager'] = config_mock
    
    return config_mock


@pytest.fixture(scope="session")
def mock_log_config():
    """Provide session-wide log_config mocking."""
    log_mock = MagicMock()
    
    # Mock logger
    mock_logger = MagicMock()
    mock_logger.info = MagicMock()
    mock_logger.warning = MagicMock()
    mock_logger.error = MagicMock()
    mock_logger.debug = MagicMock()
    mock_logger.critical = MagicMock()
    
    log_mock.setup_logger.return_value = mock_logger
    
    # Install mock
    sys.modules['log_config'] = log_mock
    
    return log_mock


@pytest.fixture
def temp_test_dir():
    """Provide a temporary directory for test files."""
    test_dir = tempfile.mkdtemp(prefix='pdf_view_test_')
    yield test_dir
    shutil.rmtree(test_dir, ignore_errors=True)


@pytest.fixture
def mock_pdf_file(temp_test_dir):
    """Create a mock PDF file for testing."""
    pdf_path = os.path.join(temp_test_dir, 'test.pdf')
    with open(pdf_path, 'wb') as f:
        # Simple PDF header
        f.write(b'%PDF-1.4\n')
        f.write(b'1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n')
        f.write(b'2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n')
        f.write(b'3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]>>endobj\n')
        f.write(b'xref\n0 4\n0000000000 65535 f \n')
        f.write(b'0000000009 00000 n \n0000000074 00000 n \n')
        f.write(b'0000000120 00000 n \ntrailer<</Size 4/Root 1 0 R>>\n')
        f.write(b'startxref\n202\n%%EOF\n')
    return pdf_path


@pytest.fixture
def mock_corrupted_pdf_file(temp_test_dir):
    """Create a corrupted PDF file for error testing."""
    pdf_path = os.path.join(temp_test_dir, 'corrupted.pdf')
    with open(pdf_path, 'wb') as f:
        f.write(b'This is not a valid PDF file')
    return pdf_path


@pytest.fixture
def mock_pdf_viewer():
    """Provide a mock PDFViewer instance."""
    viewer = MagicMock()
    
    # Mock attributes
    viewer.config = MagicMock()
    viewer.doc = None
    viewer.current_page = 0
    viewer.total_pages = 0
    viewer.zoom_factor = 1.0
    viewer.last_directory = ''
    viewer.default_page = 1
    
    # Mock UI components
    viewer.actionOpen = MagicMock()
    viewer.actionExit = MagicMock()
    viewer.previousButton = MagicMock()
    viewer.nextButton = MagicMock()
    viewer.pdfView = MagicMock()
    viewer.pageLabel = MagicMock()
    viewer.statusBar = MagicMock(return_value=MagicMock())
    
    # Mock methods
    viewer.show = MagicMock()
    viewer.close = MagicMock()
    viewer.load_settings = MagicMock()
    viewer.save_settings = MagicMock()
    viewer.open_file = MagicMock()
    viewer.show_page = MagicMock()
    viewer.previous_page = MagicMock()
    viewer.next_page = MagicMock()
    viewer.closeEvent = MagicMock()
    
    return viewer


@pytest.fixture
def test_configuration():
    """Provide test configuration settings."""
    return {
        'general': {
            'last_opened_dir': '',
            'theme': 'default'
        },
        'viewer': {
            'zoom_factor': 1.0,
            'default_page': 1,
            'auto_fit': True
        },
        'performance': {
            'cache_size': 10,
            'prefetch_pages': 2
        }
    }


@pytest.fixture
def mock_document():
    """Provide a mock PDF document."""
    doc = MagicMock()
    
    # Document properties
    doc.pageCount = 5
    doc.title = "Test Document"
    doc.author = "Test Author"
    doc.creator = "Test Creator"
    doc.producer = "Test Producer"
    doc.subject = "Test Subject"
    doc.keywords = "test, document, pdf"
    
    # Mock pages
    pages = []
    for i in range(5):
        page = MagicMock()
        page.number = i
        page.width = 612
        page.height = 792
        
        # Mock pixmap
        pixmap = MagicMock()
        pixmap.alpha = False
        pixmap.samples = f'page_{i}_data'.encode()
        pixmap.width = 612
        pixmap.height = 792
        pixmap.stride = 612
        
        page.get_pixmap.return_value = pixmap
        pages.append(page)
    
    doc.__getitem__ = lambda self, i: pages[i]
    doc.__len__ = lambda self: len(pages)
    doc.close = MagicMock()
    
    return doc


@pytest.fixture(autouse=True)
def setup_test_environment(mock_pyqt5, mock_fitz, mock_config_manager, mock_log_config):
    """Set up the test environment with all necessary mocks."""
    # This fixture automatically runs for each test
    # All mocks are already set up by the session fixtures
    pass


@pytest.fixture
def performance_monitor():
    """Monitor test performance metrics."""
    import os
    import time

    import psutil
    
    process = psutil.Process(os.getpid())
    start_time = time.time()
    start_memory = process.memory_info().rss
    
    class Monitor:
        def get_metrics(self):
            end_time = time.time()
            end_memory = process.memory_info().rss
            return {
                'execution_time': end_time - start_time,
                'memory_delta': end_memory - start_memory,
                'peak_memory': process.memory_info().peak_wss if hasattr(process.memory_info(), 'peak_wss') else end_memory
            }
    
    return Monitor()


@pytest.fixture
def test_reporter():
    """Provide test result reporting utilities."""
    results = []
    
    class Reporter:
        def add_result(self, test_name, status, duration=None, error=None):
            results.append({
                'test': test_name,
                'status': status,
                'duration': duration,
                'error': str(error) if error else None,
                'timestamp': datetime.now().isoformat()
            })
        
        def get_results(self):
            return results.copy()
        
        def save_results(self, filename):
            with open(filename, 'w') as f:
                json.dump({
                    'test_session': TEST_TIMESTAMP,
                    'results': results
                }, f, indent=2)
    
    return Reporter()


# Pytest configuration hooks
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: Unit tests for individual components"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests for component interaction"
    )
    config.addinivalue_line(
        "markers", "slow: Slow running tests"
    )
    config.addinivalue_line(
        "markers", "pdf: PDF processing related tests"
    )
    config.addinivalue_line(
        "markers", "ui: User interface related tests"
    )
    config.addinivalue_line(
        "markers", "config: Configuration management tests"
    )
    config.addinivalue_line(
        "markers", "navigation: Page navigation tests"
    )
    config.addinivalue_line(
        "markers", "error: Error handling tests"
    )


def pytest_runtest_setup(item):
    """Set up individual test runs."""
    # Mark the start of each test
    item.start_time = datetime.now()


def pytest_runtest_teardown(item):
    """Clean up after individual test runs."""
    # Calculate test duration
    if hasattr(item, 'start_time'):
        duration = (datetime.now() - item.start_time).total_seconds()
        item.duration = duration


def pytest_sessionstart(session):
    """Actions to perform at the start of the test session."""
    print(f"\n{'='*80}")
    print(f"PDF VIEW ANALYSIS TEST SESSION STARTED")
    print(f"Timestamp: {TEST_TIMESTAMP}")
    print(f"Python: {sys.version}")
    print(f"Working Directory: {os.getcwd()}")
    print(f"{'='*80}")


def pytest_sessionfinish(session, exitstatus):
    """Actions to perform at the end of the test session."""
    print(f"\n{'='*80}")
    print(f"PDF VIEW ANALYSIS TEST SESSION COMPLETED")
    print(f"Exit Status: {exitstatus}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}")
    print(f"{'='*80}")


# Custom markers for test categorization
pytestmark = [
    pytest.mark.pdf,
    pytest.mark.unit
]