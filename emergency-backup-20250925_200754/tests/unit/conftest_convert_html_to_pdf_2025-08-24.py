"""
Pytest configuration and fixtures for convert_html_to_pdf tests
Created: 2025-08-24
Provides test fixtures, setup, and teardown methods
"""

import json
import os
import shutil
import sys
import tempfile
from datetime import datetime
from unittest.mock import Mock, patch

import pytest

# Test data directory
TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "test_data")


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up the test environment before all tests."""
    print(f"\n{'='*60}")
    print(
        f"CONVERT HTML TO PDF TEST SUITE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    print(f"{'='*60}")

    # Ensure test data directory exists
    os.makedirs(TEST_DATA_DIR, exist_ok=True)

    # Add the source directory to Python path for imports
    src_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "src",
        "utilities",
        "pdf_tools",
        "pdf_conversion",
    )
    if src_path not in sys.path:
        sys.path.insert(0, os.path.abspath(src_path))

    yield

    print(f"\n{'='*60}")
    print(
        f"TEST SUITE COMPLETED - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    print(f"{'='*60}")


@pytest.fixture(scope="session")
def test_data_directory():
    """Provide the test data directory path."""
    return TEST_DATA_DIR


@pytest.fixture
def temp_directory():
    """Create a temporary directory for test files."""
    temp_dir = tempfile.mkdtemp(prefix="test_convert_html_to_pdf_")
    yield temp_dir
    # Cleanup
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def temp_html_file(temp_directory):
    """Create a temporary HTML file for testing."""
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Test HTML Document</title>
    <style>
        body { font-family: Arial, sans-serif; }
        h1 { color: blue; }
        .content { margin: 20px; }
    </style>
</head>
<body>
    <h1>Test HTML to PDF Conversion</h1>
    <div class="content">
        <p>This is a test HTML document for PDF conversion testing.</p>
        <ul>
            <li>Item 1</li>
            <li>Item 2</li>
            <li>Item 3</li>
        </ul>
        <table border="1">
            <tr><th>Column 1</th><th>Column 2</th></tr>
            <tr><td>Data 1</td><td>Data 2</td></tr>
        </table>
    </div>
</body>
</html>"""

    html_path = os.path.join(temp_directory, "test_document.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    yield html_path


@pytest.fixture
def temp_output_pdf(temp_directory):
    """Create a temporary output PDF path for testing."""
    pdf_path = os.path.join(temp_directory, "output_document.pdf")
    yield pdf_path


@pytest.fixture
def sample_html_content():
    """Provide sample HTML content for testing."""
    return {
        "simple": "<html><body><h1>Simple Test</h1></body></html>",
        "complex": """<!DOCTYPE html>
<html>
<head>
    <title>Complex Test</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background-color: #f0f0f0; padding: 10px; }
        .content { margin-top: 20px; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Complex HTML Document</h1>
    </div>
    <div class="content">
        <h2>Section 1</h2>
        <p>This is a complex HTML document with various elements.</p>
        
        <h3>Subsection</h3>
        <ul>
            <li>List item 1</li>
            <li>List item 2</li>
            <li>List item 3</li>
        </ul>
        
        <h3>Data Table</h3>
        <table>
            <thead>
                <tr><th>Name</th><th>Age</th><th>City</th></tr>
            </thead>
            <tbody>
                <tr><td>John</td><td>30</td><td>New York</td></tr>
                <tr><td>Jane</td><td>25</td><td>London</td></tr>
                <tr><td>Bob</td><td>35</td><td>Paris</td></tr>
            </tbody>
        </table>
    </div>
</body>
</html>""",
        "minimal": "<html><body>Minimal content</body></html>",
        "empty": "",
        "invalid": "<html><body><h1>Invalid HTML - missing closing tags",
    }


@pytest.fixture
def sample_urls():
    """Provide sample URLs for testing."""
    return {
        "valid": [
            "https://httpbin.org/html",
            "https://example.com",
            "https://www.google.com",
        ],
        "invalid": [
            "not-a-url",
            "ftp://invalid-protocol.com",
            "https://non-existent-domain-12345.com",
        ],
        "empty": "",
        "malformed": [
            "htp://missing-t.com",
            "https:/missing-slash.com",
            "https://spaces in url.com",
        ],
    }


@pytest.fixture
def mock_qt_application():
    """Mock QApplication for GUI testing."""
    with patch("PyQt5.QtWidgets.QApplication") as mock_app:
        mock_instance = Mock()
        mock_app.return_value = mock_instance
        mock_app.instance.return_value = mock_instance
        yield mock_app


@pytest.fixture
def mock_ui_file():
    """Mock UI file loading."""
    with patch("PyQt5.uic.loadUi") as mock_load_ui:
        yield mock_load_ui


@pytest.fixture
def mock_logger():
    """Mock logger for testing."""
    with patch("convert_html_to_pdf.logger") as logger_mock:
        logger_mock.info = Mock()
        logger_mock.debug = Mock()
        logger_mock.warning = Mock()
        logger_mock.error = Mock()
        logger_mock.critical = Mock()
        yield logger_mock


@pytest.fixture
def mock_pdfkit():
    """Mock pdfkit for testing."""
    with (
        patch("pdfkit.from_url") as mock_from_url,
        patch("pdfkit.from_file") as mock_from_file,
        patch("pdfkit.from_string") as mock_from_string,
    ):

        yield {
            "from_url": mock_from_url,
            "from_file": mock_from_file,
            "from_string": mock_from_string,
        }


@pytest.fixture
def mock_file_dialogs():
    """Mock file dialogs for testing."""
    with (
        patch("PyQt5.QtWidgets.QFileDialog.getOpenFileName") as mock_open,
        patch("PyQt5.QtWidgets.QFileDialog.getSaveFileName") as mock_save,
    ):

        yield {"open": mock_open, "save": mock_save}


@pytest.fixture
def mock_message_boxes():
    """Mock message boxes for testing."""
    with (
        patch("PyQt5.QtWidgets.QMessageBox.information") as mock_info,
        patch("PyQt5.QtWidgets.QMessageBox.critical") as mock_critical,
        patch("PyQt5.QtWidgets.QMessageBox.warning") as mock_warning,
    ):

        yield {
            "information": mock_info,
            "critical": mock_critical,
            "warning": mock_warning,
        }


@pytest.fixture
def mock_ui_components():
    """Create mock UI components for testing."""
    components = {
        "urlInput": Mock(),
        "fileInput": Mock(),
        "htmlInput": Mock(),
        "statusLabel": Mock(),
        "convertUrlButton": Mock(),
        "convertFileButton": Mock(),
        "convertHtmlButton": Mock(),
        "browseButton": Mock(),
        "actionExit": Mock(),
    }

    # Set up default behaviors
    components["urlInput"].text.return_value = ""
    components["fileInput"].text.return_value = ""
    components["htmlInput"].toPlainText.return_value = ""

    return components


@pytest.fixture
def conversion_scenarios():
    """Provide various conversion scenarios for testing."""
    return {
        "url_to_pdf": {
            "input": "https://example.com",
            "output": "/path/to/output.pdf",
            "method": "from_url",
        },
        "file_to_pdf": {
            "input": "/path/to/input.html",
            "output": "/path/to/output.pdf",
            "method": "from_file",
        },
        "html_to_pdf": {
            "input": "<html><body><h1>Test</h1></body></html>",
            "output": "/path/to/output.pdf",
            "method": "from_string",
        },
    }


@pytest.fixture
def error_scenarios():
    """Provide different error scenarios for testing."""
    return {
        "pdfkit_error": Exception("PDFKit processing error"),
        "file_not_found": FileNotFoundError("HTML file not found"),
        "permission_error": PermissionError("Permission denied"),
        "network_error": Exception("Network connection error"),
        "invalid_url": Exception("Invalid URL format"),
        "ui_error": Exception("UI component error"),
        "system_error": OSError("System error occurred"),
    }


@pytest.fixture(autouse=True)
def cleanup_test_files():
    """Automatically clean up test files after each test."""
    yield
    # Cleanup any remaining test files
    for root, dirs, files in os.walk(TEST_DATA_DIR):
        for file in files:
            if file.startswith("test_") and file.endswith(".tmp"):
                try:
                    os.remove(os.path.join(root, file))
                except OSError:
                    pass


@pytest.fixture
def performance_monitor():
    """Monitor test performance and execution time."""
    start_time = datetime.now()
    yield
    end_time = datetime.now()
    execution_time = (end_time - start_time).total_seconds()
    print(f"\nTest execution time: {execution_time:.3f} seconds")


# Pytest hooks for custom behavior
def pytest_configure(config):
    """Configure pytest with custom settings."""
    # Add custom markers
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line("markers", "gui: mark test as a GUI test")
    config.addinivalue_line(
        "markers", "conversion: mark test as a conversion test"
    )
    config.addinivalue_line("markers", "slow: mark test as slow running")


def pytest_runtest_setup(item):
    """Set up before each test item."""
    # Print test name for detailed output
    if hasattr(item, "function"):
        print(f"\n🔍 Running: {item.function.__name__}")


def pytest_runtest_teardown(item, nextitem):
    """Clean up after each test item."""
    # Additional cleanup if needed
    pass


def pytest_sessionstart(session):
    """Called after the Session object has been created."""
    print(f"\n📊 Starting test session for convert_html_to_pdf")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🗂️  Test directory: {session.config.option.file_or_dir}")


def pytest_sessionfinish(session, exitstatus):
    """Called after whole test run finished."""
    print(f"\n✅ Test session completed with exit status: {exitstatus}")
    if exitstatus == 0:
        print("🎉 All tests passed successfully!")
    else:
        print(f"❌ Some tests failed (exit code: {exitstatus})")


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Add additional terminal summary."""
    if hasattr(terminalreporter, "stats"):
        passed = len(terminalreporter.stats.get("passed", []))
        failed = len(terminalreporter.stats.get("failed", []))
        skipped = len(terminalreporter.stats.get("skipped", []))
        errors = len(terminalreporter.stats.get("error", []))

        print(f"\n📈 Test Summary:")
        print(f"   ✅ Passed: {passed}")
        print(f"   ❌ Failed: {failed}")
        print(f"   ⏭️  Skipped: {skipped}")
        print(f"   🚫 Errors: {errors}")
        print(f"   📊 Total: {passed + failed + skipped + errors}")


# Test data creation helpers
def create_test_html_file(content, file_path):
    """Create a test HTML file with specified content."""
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    return file_path


def create_test_pdf_path(directory, filename="test_output.pdf"):
    """Create a test PDF file path."""
    return os.path.join(directory, filename)


def validate_html_content(content):
    """Validate HTML content for testing."""
    if not content or not isinstance(content, str):
        return False
    return "<html>" in content.lower() or "<body>" in content.lower()


def generate_sample_html(title="Test Document", content="Test content"):
    """Generate sample HTML content for testing."""
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <p>{content}</p>
    <p>Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
</body>
</html>"""
