"""
Shared test configuration and fixtures for split.py unit tests.
Execution timestamp: 2025-08-24
"""

import os
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pikepdf
import pytest
from PyQt5.QtWidgets import QApplication
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Add source directory to path for imports
sys.path.insert(
    0,
    str(
        Path(__file__).parent.parent.parent
        / "src"
        / "utilities"
        / "pdf_tools"
        / "pdf_basic_operations"
    ),
)


@pytest.fixture(scope="session")
def execution_timestamp():
    """Fixture providing the test execution timestamp."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@pytest.fixture(scope="session")
def test_output_dir():
    """Create and provide a temporary directory for test outputs."""
    test_dir = Path(__file__).parent / "test_outputs"
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
def sample_pdf_1_page(temp_dir):
    """Create a sample PDF with 1 page."""
    pdf_path = os.path.join(temp_dir, "sample_1_page.pdf")

    # Create PDF using reportlab
    c = canvas.Canvas(pdf_path, pagesize=letter)
    c.drawString(100, 750, "This is page 1")
    c.showPage()
    c.save()

    return pdf_path


@pytest.fixture
def sample_pdf_5_pages(temp_dir):
    """Create a sample PDF with 5 pages."""
    pdf_path = os.path.join(temp_dir, "sample_5_pages.pdf")

    # Create PDF using reportlab
    c = canvas.Canvas(pdf_path, pagesize=letter)
    for i in range(1, 6):
        c.drawString(100, 750, f"This is page {i}")
        c.showPage()
    c.save()

    return pdf_path


@pytest.fixture
def sample_pdf_10_pages(temp_dir):
    """Create a sample PDF with 10 pages."""
    pdf_path = os.path.join(temp_dir, "sample_10_pages.pdf")

    # Create PDF using reportlab
    c = canvas.Canvas(pdf_path, pagesize=letter)
    for i in range(1, 11):
        c.drawString(100, 750, f"This is page {i}")
        c.showPage()
    c.save()

    return pdf_path


@pytest.fixture
def corrupted_pdf(temp_dir):
    """Create a corrupted PDF file for error testing."""
    pdf_path = os.path.join(temp_dir, "corrupted.pdf")
    with open(pdf_path, "w") as f:
        f.write("This is not a valid PDF file")
    return pdf_path


@pytest.fixture
def nonexistent_pdf(temp_dir):
    """Provide path to a non-existent PDF file."""
    return os.path.join(temp_dir, "nonexistent.pdf")


@pytest.fixture
def output_directory(temp_dir):
    """Create an output directory for split operations."""
    output_dir = os.path.join(temp_dir, "output")
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


@pytest.fixture
def readonly_directory(temp_dir):
    """Create a read-only directory for permission testing."""
    readonly_dir = os.path.join(temp_dir, "readonly")
    os.makedirs(readonly_dir, exist_ok=True)
    # Make directory read-only (Windows compatible)
    try:
        os.chmod(readonly_dir, 0o444)
    except OSError:
        # If we can't change permissions, skip this fixture
        pytest.skip("Cannot create read-only directory on this system")

    yield readonly_dir

    # Restore permissions for cleanup
    try:
        os.chmod(readonly_dir, 0o755)
    except OSError:
        pass


@pytest.fixture
def mock_logger():
    """Mock logger for testing log operations."""
    with patch("split.logger") as mock_log:
        yield mock_log


@pytest.fixture
def mock_qmessagebox():
    """Mock QMessageBox for testing GUI operations."""
    with patch("split.QMessageBox") as mock_msg:
        mock_msg.critical = Mock()
        mock_msg.warning = Mock()
        mock_msg.information = Mock()
        yield mock_msg


@pytest.fixture
def mock_qfiledialog():
    """Mock QFileDialog for testing file dialog operations."""
    with patch("split.QFileDialog") as mock_dialog:
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
def mock_ui_file():
    """Mock the UI file loading for SplitUI tests."""
    with patch("split.uic.loadUi") as mock_loadui:
        mock_loadui.return_value = None
        yield mock_loadui


@pytest.fixture
def mock_splitui_components():
    """Mock all UI components for SplitUI testing."""
    with patch.multiple(
        "split", QtWidgets=MagicMock(), uic=MagicMock()
    ) as mocks:
        # Create mock UI components
        mock_ui = MagicMock()
        mock_ui.browseButton = MagicMock()
        mock_ui.browseOutputButton = MagicMock()
        mock_ui.splitButton = MagicMock()
        mock_ui.inputFileEdit = MagicMock()
        mock_ui.outputDirEdit = MagicMock()
        mock_ui.pagesPerFileRadio = MagicMock()
        mock_ui.pageRangesRadio = MagicMock()
        mock_ui.pagesPerFileEdit = MagicMock()
        mock_ui.pageRangesEdit = MagicMock()
        mock_ui.progressBar = MagicMock()
        mock_ui.statusBar = MagicMock()
        mock_ui.actionExit = MagicMock()

        mocks["uic"].loadUi.return_value = mock_ui
        yield mock_ui


class MockPdf:
    """Mock PDF class for testing without real PDF operations."""

    def __init__(self, num_pages=5):
        self.pages = [MockPage(i) for i in range(num_pages)]

    @classmethod
    def open(cls, filename):
        """Mock the pikepdf.Pdf.open method."""
        if "nonexistent" in filename:
            raise FileNotFoundError(f"No such file: {filename}")
        if "corrupted" in filename:
            raise pikepdf.PdfError("Invalid PDF")

        # Return different page counts based on filename
        if "1_page" in filename:
            return cls(1)
        elif "5_pages" in filename:
            return cls(5)
        elif "10_pages" in filename:
            return cls(10)
        else:
            return cls(5)  # Default

    @classmethod
    def new(cls):
        """Mock the pikepdf.Pdf.new method."""
        return cls(0)

    def save(self, filename):
        """Mock save method."""
        # Create an empty file to simulate saving
        Path(filename).touch()


class MockPage:
    """Mock PDF page class."""

    def __init__(self, page_num):
        self.page_num = page_num


@pytest.fixture
def mock_pikepdf():
    """Mock pikepdf operations."""
    with patch("split.pikepdf") as mock_pdf:
        mock_pdf.Pdf = MockPdf
        mock_pdf.PdfError = pikepdf.PdfError
        yield mock_pdf


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
    config.addinivalue_line("markers", "gui: Tests requiring GUI components")
    config.addinivalue_line("markers", "pdf: Tests working with PDF files")


def pytest_runtest_setup(item):
    """Setup hook for each test item."""
    # Log test start
    print(f"\n--- Starting test: {item.nodeid} ---")


def pytest_runtest_teardown(item, nextitem):
    """Teardown hook for each test item."""
    # Log test completion
    print(f"\n--- Completed test: {item.nodeid} ---")


def pytest_sessionstart(session):
    """Called after the Session object has been created."""
    print(
        f"\n=== Test Session Started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ==="
    )


def pytest_sessionfinish(session, exitstatus):
    """Called after whole test run finished."""
    print(
        f"\n=== Test Session Finished at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ==="
    )
    print(f"Exit status: {exitstatus}")
