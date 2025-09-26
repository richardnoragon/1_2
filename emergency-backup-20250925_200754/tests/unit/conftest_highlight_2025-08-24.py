"""
Pytest configuration and fixtures for highlight.py testing
Generated on August 24, 2025

This file provides comprehensive fixtures for testing the PDF highlighting tool,
including mock PDF documents, temporary files, and test data.
"""

import os
import shutil
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing"""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def temp_file():
    """Create a temporary file for testing"""
    temp_fd, temp_path = tempfile.mkstemp(suffix=".txt")
    os.close(temp_fd)
    yield temp_path
    try:
        os.unlink(temp_path)
    except OSError:
        pass


@pytest.fixture
def temp_pdf_path():
    """Create a temporary PDF file path for testing"""
    temp_fd, temp_path = tempfile.mkstemp(suffix=".pdf")
    os.close(temp_fd)
    yield temp_path
    try:
        os.unlink(temp_path)
    except OSError:
        pass


@pytest.fixture
def sample_pdf_path():
    """Provide a sample PDF path for testing"""
    return "/path/to/sample.pdf"


@pytest.fixture
def mock_pdf_document():
    """Create a mock PDF document for testing"""
    doc = Mock()
    doc.pageCount = 2
    doc.isEncrypted = False
    doc.metadata = {
        "title": "Test Document",
        "author": "Test Author",
        "subject": "Test Subject",
        "creator": "Test Creator",
    }
    doc.save = Mock()
    doc.close = Mock()
    return doc


@pytest.fixture
def mock_pdf_page():
    """Create a mock PDF page for testing"""
    page = Mock()
    page.getText = Mock(return_value="Test content with searchable text")
    page.searchFor = Mock(return_value=[Mock()])
    page.addRedactAnnot = Mock()
    page.apply_redactions = Mock()
    page.addRectAnnot = Mock()
    page.addHighlightAnnot = Mock()
    page.addSquigglyAnnot = Mock()
    page.addUnderlineAnnot = Mock()
    page.addStrikeoutAnnot = Mock()
    page.deleteAnnot = Mock()
    page.firstAnnot = None
    return page


@pytest.fixture
def mock_pdf_annotation():
    """Create a mock PDF annotation for testing"""
    annot = Mock()
    annot.set_opacity = Mock()
    annot.setColors = Mock()
    annot.update = Mock()
    annot.next = None
    return annot


@pytest.fixture
def sample_text_lines():
    """Provide sample text lines for search testing"""
    return [
        "This is the first line with test data",
        "Second line contains more test information",
        "Third line has different content",
        "Final line with test again",
    ]


@pytest.fixture
def sample_search_patterns():
    """Provide sample search patterns for testing"""
    return {
        "simple": "test",
        "case_sensitive": "Test",
        "regex": r"\b\w+@\w+\.\w+\b",
        "email": "user@example.com",
        "phone": r"\d{3}-\d{3}-\d{4}",
        "invalid_regex": "[",
    }


@pytest.fixture
def mock_qt_widgets():
    """Mock PyQt5 widgets for GUI testing"""
    with (
        patch("highlight.QApplication") as mock_app,
        patch("highlight.QMainWindow") as mock_main,
        patch("highlight.QFileDialog") as mock_dialog,
        patch("highlight.QMessageBox") as mock_msgbox,
    ):

        mock_dialog.getOpenFileName = Mock(
            return_value=("test.pdf", "PDF Files (*.pdf)")
        )
        mock_msgbox.warning = Mock()
        mock_msgbox.critical = Mock()
        mock_msgbox.information = Mock()

        yield {
            "app": mock_app,
            "main": mock_main,
            "dialog": mock_dialog,
            "msgbox": mock_msgbox,
        }


@pytest.fixture
def mock_ui_elements():
    """Mock UI elements for HighlightUI testing"""
    elements = {
        "browseButton": Mock(),
        "processButton": Mock(),
        "actionExit": Mock(),
        "actionCombo": Mock(),
        "colorCombo": Mock(),
        "opacitySlider": Mock(),
        "inputPathEdit": Mock(),
        "searchEdit": Mock(),
        "pagesEdit": Mock(),
        "statusBar": Mock(),
    }

    # Configure common return values
    elements["actionCombo"].currentText = Mock(return_value="Highlight")
    elements["colorCombo"].currentText = Mock(return_value="Yellow")
    elements["opacitySlider"].value = Mock(return_value=100)
    elements["searchEdit"].text = Mock(return_value="test")
    elements["pagesEdit"].text = Mock(return_value="")
    elements["statusBar"].return_value = Mock()

    return elements


@pytest.fixture
def sample_pdf_content():
    """Provide sample PDF content for testing"""
    return {
        "pages": [
            {
                "number": 0,
                "text": "First page content with test data\nAnother line here",
                "lines": [
                    "First page content with test data",
                    "Another line here",
                ],
            },
            {
                "number": 1,
                "text": "Second page has more test information\nFinal line of document",
                "lines": [
                    "Second page has more test information",
                    "Final line of document",
                ],
            },
        ],
        "metadata": {
            "title": "Sample PDF Document",
            "author": "Test Author",
            "subject": "Testing PDF Processing",
            "creator": "PDF Test Creator",
        },
    }


@pytest.fixture
def mock_file_system():
    """Mock file system operations for testing"""
    with (
        patch("os.path.isfile") as mock_isfile,
        patch("os.path.isdir") as mock_isdir,
        patch("os.path.exists") as mock_exists,
        patch("os.walk") as mock_walk,
    ):

        mock_isfile.return_value = True
        mock_isdir.return_value = False
        mock_exists.return_value = True
        mock_walk.return_value = [
            ("/test/dir", [], ["file1.pdf", "file2.pdf", "file3.txt"])
        ]

        yield {
            "isfile": mock_isfile,
            "isdir": mock_isdir,
            "exists": mock_exists,
            "walk": mock_walk,
        }


@pytest.fixture
def test_command_args():
    """Provide test command line arguments"""
    return {
        "file_highlight": [
            "highlight.py",
            "-i",
            "/test/file.pdf",
            "-s",
            "test",
            "-a",
            "Highlight",
        ],
        "file_redact": [
            "highlight.py",
            "-i",
            "/test/file.pdf",
            "-s",
            "sensitive",
            "-a",
            "Redact",
        ],
        "folder_recursive": [
            "highlight.py",
            "-i",
            "/test/folder",
            "-s",
            "test",
            "-r",
            "true",
        ],
        "remove_highlights": [
            "highlight.py",
            "-i",
            "/test/file.pdf",
            "-a",
            "Remove",
        ],
    }


@pytest.fixture
def mock_logger():
    """Mock logger for testing"""
    with patch("highlight.logger") as mock_log:
        mock_log.info = Mock()
        mock_log.debug = Mock()
        mock_log.warning = Mock()
        mock_log.error = Mock()
        yield mock_log


@pytest.fixture
def error_scenarios():
    """Provide various error scenarios for testing"""
    return {
        "pdf_open_error": Exception("Could not open PDF file"),
        "file_not_found": FileNotFoundError("File not found"),
        "permission_error": PermissionError("Permission denied"),
        "invalid_regex": Exception("Invalid regular expression"),
        "ui_load_error": Exception("Could not load UI file"),
        "processing_error": Exception("PDF processing failed"),
    }


@pytest.fixture
def color_test_cases():
    """Provide color test cases for highlighting"""
    return {
        "yellow": {"rgb": (1, 1, 0), "name": "yellow"},
        "red": {"rgb": (1, 0, 0), "name": "red"},
        "green": {"rgb": (0, 1, 0), "name": "green"},
        "blue": {"rgb": (0, 0, 1), "name": "blue"},
        "purple": {"rgb": (0.7, 0, 0.7), "name": "purple"},
        "unknown": {
            "rgb": (1, 1, 0),
            "name": "invalid_color",
        },  # Should default to yellow
    }


@pytest.fixture
def annotation_types():
    """Provide annotation types for testing"""
    return [
        "Highlight",
        "Squiggly",
        "Underline",
        "Strikeout",
        "Unknown",  # Should default to Highlight
    ]


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment before each test"""
    # Ensure test directory exists
    test_dir = Path(__file__).parent
    test_data_dir = test_dir / "test_data"
    test_data_dir.mkdir(exist_ok=True)

    # Setup any additional test environment requirements
    os.environ["PYTEST_RUNNING"] = "1"

    yield

    # Cleanup after test
    if "PYTEST_RUNNING" in os.environ:
        del os.environ["PYTEST_RUNNING"]


@pytest.fixture
def performance_test_data():
    """Provide data for performance testing"""
    return {
        "large_text": "test " * 1000,  # Large text with many matches
        "complex_regex": r"(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)",
        "many_pages": 100,
        "many_matches": 500,
    }


@pytest.fixture
def edge_case_data():
    """Provide edge case data for testing"""
    return {
        "empty_string": "",
        "none_value": None,
        "unicode_text": "Ţēşţ ūņĩçōđē țėxț",
        "special_chars": "!@#$%^&*()_+-=[]{}|;:,.<>?",
        "very_long_string": "x" * 10000,
        "newlines": "line1\nline2\rline3\r\nline4",
        "whitespace": "   \t\n\r   ",
        "numbers_only": "1234567890",
        "mixed_content": "Text123!@#ūņĩçōđē\n\t  ",
    }
