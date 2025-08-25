"""
Shared test configuration and fixtures for convert_to_docx.py unit tests.
Execution timestamp: 2025-08-24
"""

import os
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
from PyQt5.QtWidgets import QApplication

# Add source directory to path for imports
source_path = str(Path(__file__).parent.parent.parent / "src" /
                  "utilities" / "pdf_tools" / "pdf_conversion")
sys.path.insert(0, source_path)


@pytest.fixture(scope="session")
def execution_timestamp():
    """Fixture providing the test execution timestamp."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@pytest.fixture(scope="session")
def test_output_dir():
    """Create and provide a temporary directory for test outputs."""
    test_dir = Path(__file__).parent / "test_outputs_convert_to_docx"
    test_dir.mkdir(exist_ok=True)
    yield str(test_dir)
    # Cleanup after all tests
    if test_dir.exists():
        shutil.rmtree(test_dir)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for each test."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield tmp_dir


@pytest.fixture
def sample_pdf_file(temp_dir):
    """Create a sample PDF file for testing."""
    pdf_path = os.path.join(temp_dir, "sample.pdf")
    
    # Create a simple mock PDF file
    with open(pdf_path, 'w') as f:
        f.write("%PDF-1.4\\n")
        f.write("1 0 obj\\n")
        f.write("<<\\n")
        f.write("/Type /Catalog\\n")
        f.write("/Pages 2 0 R\\n")
        f.write(">>\\n")
        f.write("endobj\\n")
        f.write("Mock PDF content for testing")
    
    return pdf_path


@pytest.fixture
def sample_docx_file(temp_dir):
    """Create a sample DOCX file for testing."""
    docx_path = os.path.join(temp_dir, "sample.docx")
    
    # Create a simple mock DOCX file
    with open(docx_path, 'w') as f:
        f.write("Mock DOCX content for testing")
    
    return docx_path


@pytest.fixture
def nonexistent_file(temp_dir):
    """Provide path to a non-existent file."""
    return os.path.join(temp_dir, "nonexistent.pdf")


@pytest.fixture
def test_folder(temp_dir):
    """Create a test folder for move operations."""
    folder_path = os.path.join(temp_dir, "test_folder")
    os.makedirs(folder_path, exist_ok=True)
    return folder_path


@pytest.fixture
def mock_logger():
    """Mock logger for testing log operations."""
    with patch('convert_to_docx.logger') as mock_log:
        yield mock_log


@pytest.fixture
def mock_pdf2docx_parse():
    """Mock the pdf2docx.parse function."""
    with patch('convert_to_docx.parse') as mock_parse:
        yield mock_parse


@pytest.fixture
def mock_qmessagebox():
    """Mock QMessageBox for testing GUI operations."""
    with patch('convert_to_docx.QMessageBox') as mock_msg:
        mock_msg.critical = Mock()
        mock_msg.warning = Mock()
        mock_msg.information = Mock()
        yield mock_msg


@pytest.fixture
def mock_qfiledialog():
    """Mock QFileDialog for testing file dialog operations."""
    with patch('convert_to_docx.QFileDialog') as mock_dialog:
        mock_dialog.getOpenFileName = Mock()
        mock_dialog.getExistingDirectory = Mock()
        yield mock_dialog


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance for GUI tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    # Don't quit the app as it might be used by other tests


@pytest.fixture
def mock_os_operations():
    """Mock OS operations for testing error conditions."""
    with patch('convert_to_docx.os') as mock_os:
        # Keep the real os.path and other needed functions
        mock_os.path = os.path
        mock_os.makedirs = Mock()
        mock_os.exists = Mock()
        yield mock_os


@pytest.fixture
def mock_shutil_operations():
    """Mock shutil operations for testing file moves."""
    with patch('convert_to_docx.shutil') as mock_shutil:
        mock_shutil.move = Mock()
        yield mock_shutil


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Automatically set up test environment for each test."""
    # Ensure clean state before each test
    yield
    # Cleanup after each test if needed


def pytest_configure(config):
    """Configure pytest with custom markers and settings."""
    config.addinivalue_line(
        "markers", "unit: Unit tests for individual functions"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests for component interaction"
    )
    config.addinivalue_line(
        "markers", "gui: Tests requiring GUI components"
    )
    config.addinivalue_line(
        "markers", "slow: Tests that take a long time to run"
    )


def pytest_runtest_setup(item):
    """Setup hook for each test item."""
    # Log test start
    print(f"\\n--- Starting test: {item.nodeid} ---")


def pytest_runtest_teardown(item, nextitem):
    """Teardown hook for each test item."""
    # Log test completion
    print(f"\\n--- Completed test: {item.nodeid} ---")


def pytest_sessionstart(session):
    """Called after the Session object has been created."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"\\n=== Test Session Started at {timestamp} ===")


def pytest_sessionfinish(session, exitstatus):
    """Called after whole test run finished."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"\\n=== Test Session Finished at {timestamp} ===")
    print(f"Exit status: {exitstatus}")


class MockConvertWindow:
    """Mock ConvertWindow class for testing without GUI dependencies."""
    
    def __init__(self):
        self.windowTitle_value = 'PDF to DOCX Converter'
        self.geometry_value = MockGeometry()
        self.status_label = MockLabel()
        self.progress_label = MockLabel()
        self.menuBar_value = MockMenuBar()
        self.centralWidget_value = MockWidget()
    
    def windowTitle(self):
        return self.windowTitle_value
    
    def geometry(self):
        return self.geometry_value
    
    def menuBar(self):
        return self.menuBar_value
    
    def centralWidget(self):
        return self.centralWidget_value
    
    def select_pdf(self):
        pass


class MockGeometry:
    """Mock geometry class."""
    
    def width(self):
        return 600
    
    def height(self):
        return 400


class MockLabel:
    """Mock label class."""
    
    def __init__(self):
        self._text = "Select a PDF file to convert"
    
    def text(self):
        return self._text
    
    def setText(self, text):
        self._text = text


class MockWidget:
    """Mock widget class."""
    pass


class MockMenuBar:
    """Mock menu bar class."""
    
    def actions(self):
        return [MockAction()]


class MockAction:
    """Mock action class."""
    
    def menu(self):
        return MockMenu()


class MockMenu:
    """Mock menu class."""
    
    def title(self):
        return 'File'


@pytest.fixture
def mock_convert_window():
    """Provide a mock ConvertWindow for testing."""
    return MockConvertWindow()