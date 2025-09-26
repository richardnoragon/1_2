"""
Comprehensive test configuration and fixtures for watermark.py testing
Generated on: 2025-08-24
Target: src/utilities/pdf_tools/pdf_enhancements/watermark.py
"""

import json
import os
import shutil
import sys
import tempfile
from datetime import datetime
from unittest.mock import Mock, patch

import pytest

# Add src path to allow imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

# PyQt5 imports with error handling
try:
    from PyQt5 import QtCore, QtTest, QtWidgets
    from PyQt5.QtWidgets import QApplication
    QT_AVAILABLE = True
except ImportError:
    QT_AVAILABLE = False
    QtWidgets = None
    QtCore = None
    QtTest = None
    QApplication = None

# Mock fitz if not available
try:
    import fitz
    FITZ_AVAILABLE = True
except ImportError:
    FITZ_AVAILABLE = False
    fitz = None


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance for GUI tests."""
    if not QT_AVAILABLE:
        pytest.skip("PyQt5 not available")
    
    app = None
    if QApplication:
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
    yield app


@pytest.fixture
def temp_dir():
    """Create temporary directory for test files."""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def sample_pdf_content():
    """Sample PDF content for testing."""
    content = (
        b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R "
        b"/MediaBox [0 0 612 792] >>\nendobj\n"
        b"xref\n0 4\n0000000000 65535 f \n0000000010 00000 n \n"
        b"0000000079 00000 n \n0000000173 00000 n \ntrailer\n"
        b"<< /Size 4 /Root 1 0 R >>\nstartxref\n253\n%%EOF"
    )
    return content


@pytest.fixture
def sample_pdf_file(temp_dir, sample_pdf_content):
    """Create a sample PDF file for testing."""
    pdf_path = os.path.join(temp_dir, "sample.pdf")
    with open(pdf_path, "wb") as f:
        f.write(sample_pdf_content)
    return pdf_path


@pytest.fixture
def mock_pdf_document():
    """Mock PyMuPDF document for testing."""
    mock_doc = Mock()
    mock_doc.__len__ = Mock(return_value=3)
    
    # Create mock pages
    mock_pages = []
    for i in range(3):
        mock_page = Mock()
        mock_page.rect = Mock()
        mock_page.rect.width = 595
        mock_page.rect.height = 842
        mock_page.insert_text = Mock()
        mock_pages.append(mock_page)
    
    mock_doc.__getitem__ = Mock(side_effect=lambda x: mock_pages[x])
    mock_doc.save = Mock()
    mock_doc.close = Mock()
    
    return mock_doc


@pytest.fixture
def mock_fitz(mock_pdf_document):
    """Mock the fitz module."""
    with patch('fitz.open', return_value=mock_pdf_document):
        with patch('fitz.get_text_length', return_value=100):
            yield fitz


@pytest.fixture
def mock_logger():
    """Mock logger for testing."""
    logger_mock = Mock()
    logger_mock.info = Mock()
    logger_mock.debug = Mock()
    logger_mock.warning = Mock()
    logger_mock.error = Mock()
    logger_mock.critical = Mock()
    return logger_mock


@pytest.fixture
def mock_config():
    """Mock configuration dictionary."""
    return {
        'opacity': 0.5,
        'watermark_text': 'Test Watermark',
        'last_directory': '/tmp/test'
    }


@pytest.fixture
def mock_ui_file(temp_dir):
    """Create a mock UI file for testing."""
    ui_content = '''<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>MainWindow</class>
 <widget class="QMainWindow" name="MainWindow">
  <widget class="QWidget" name="centralwidget">
   <widget class="QPushButton" name="browseButton"/>
   <widget class="QPushButton" name="watermarkButton"/>
   <widget class="QLineEdit" name="inputFileEdit"/>
   <widget class="QLineEdit" name="watermarkEdit"/>
   <widget class="QSpinBox" name="opacitySpinBox"/>
   <widget class="QLineEdit" name="pagesEdit"/>
  </widget>
  <widget class="QMenuBar" name="menuBar">
   <widget class="QMenu" name="menuFile">
    <addaction name="actionExit"/>
   </widget>
  </widget>
  <widget class="QStatusBar" name="statusBar"/>
  <action name="actionExit"/>
 </widget>
</ui>'''
    
    ui_path = os.path.join(temp_dir, "watermark.ui")
    with open(ui_path, "w") as f:
        f.write(ui_content)
    return ui_path


@pytest.fixture
def test_execution_timestamp():
    """Provide test execution timestamp."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@pytest.fixture
def test_results_logger():
    """Logger for test results and execution details."""
    class TestResultsLogger:
        def __init__(self):
            self.results = []
            self.start_time = datetime.now()
        
        def log_test_start(self, test_name):
            self.results.append({
                'test_name': test_name,
                'start_time': datetime.now().isoformat(),
                'status': 'running'
            })
        
        def log_test_result(self, test_name, status, duration=None,
                            error=None):
            for result in self.results:
                if result['test_name'] == test_name:
                    result['status'] = status
                    result['end_time'] = datetime.now().isoformat()
                    result['duration'] = duration
                    if error:
                        result['error'] = str(error)
                    break
        
        def get_summary(self):
            total_tests = len(self.results)
            passed = len([r for r in self.results if r['status'] == 'passed'])
            failed = len([r for r in self.results if r['status'] == 'failed'])
            
            return {
                'execution_timestamp': self.start_time.isoformat(),
                'total_tests': total_tests,
                'passed': passed,
                'failed': failed,
                'success_rate': ((passed / total_tests * 100)
                                 if total_tests > 0 else 0),
                'results': self.results
            }
    
    return TestResultsLogger()


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Set up test environment and cleanup."""
    original_cwd = os.getcwd()
    logs_dir = os.path.join(os.path.dirname(__file__), 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    yield
    os.chdir(original_cwd)


def create_test_pdf(filepath, num_pages=3):
    """Create a test PDF file with specified number of pages."""
    if FITZ_AVAILABLE and fitz:
        try:
            doc = fitz.open()
            for i in range(num_pages):
                page = doc.new_page()
                page.insert_text((100, 100), f"Page {i+1}")
            doc.save(filepath)
            doc.close()
        except Exception:
            pass
    else:
        with open(filepath, "w") as f:
            f.write(f"Mock PDF with {num_pages} pages")


def generate_test_summary(results, output_path):
    """Generate a comprehensive test execution summary."""
    summary = {
        'execution_timestamp': datetime.now().isoformat(),
        'test_file': 'test_watermark_2025-08-24.py',
        'target_module': 'watermark.py',
        'results': results
    }
    
    with open(output_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    return summary