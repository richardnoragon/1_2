"""
Pytest Configuration and Shared Fixtures for miner.py Tests
Generated: 2025-08-30
Target: test_miner_2025-08-30.py

This file contains shared fixtures, configuration, and utilities for testing miner.py
"""

import os
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path

import fitz
import pytest
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication

# Add source directory to path
sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "src",
        "utilities",
        "pdf_tools",
        "pdf_view_analysis",
    ),
)

# Global test configuration
TEST_DATE = "2025-08-30"
TARGET_MODULE = "miner"


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance for GUI tests"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])

    # Set up application for testing
    app.setQuitOnLastWindowClosed(False)

    yield app

    # Cleanup
    app.quit()


@pytest.fixture(scope="session")
def test_data_directory():
    """Create and provide temporary directory for test data"""
    temp_dir = tempfile.mkdtemp(prefix=f"test_{TARGET_MODULE}_{TEST_DATE}_")
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def temp_directory():
    """Create temporary directory for individual tests"""
    temp_dir = tempfile.mkdtemp(prefix=f"test_{TARGET_MODULE}_")
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def simple_pdf_file(temp_directory):
    """Create a simple PDF file for testing"""
    pdf_path = os.path.join(temp_directory, "simple_test.pdf")

    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Simple Test PDF\nLine 2\nLine 3", fontsize=12)
    doc.save(pdf_path)
    doc.close()

    return pdf_path


@pytest.fixture
def multi_page_pdf_file(temp_directory):
    """Create a multi-page PDF file for testing"""
    pdf_path = os.path.join(temp_directory, "multi_page_test.pdf")

    doc = fitz.open()
    for i in range(5):
        page = doc.new_page()
        page.insert_text(
            (72, 72),
            f"Page {i+1} Content\nThis is page number {i+1}\nTest content for page {i+1}",
            fontsize=12,
        )
    doc.save(pdf_path)
    doc.close()

    return pdf_path


@pytest.fixture
def complex_pdf_file(temp_directory):
    """Create a complex PDF file with various elements"""
    pdf_path = os.path.join(temp_directory, "complex_test.pdf")

    doc = fitz.open()

    # Page 1: Text with different fonts and sizes
    page1 = doc.new_page()
    page1.insert_text(
        (72, 72), "Title Text", fontsize=18, fontname="helv-bold"
    )
    page1.insert_text(
        (72, 120), "Regular paragraph text with normal font size.", fontsize=12
    )
    page1.insert_text((72, 150), "Small footnote text", fontsize=8)

    # Page 2: Text with tables/structured content
    page2 = doc.new_page()
    page2.insert_text(
        (72, 72), "Table Data", fontsize=14, fontname="helv-bold"
    )
    page2.insert_text((72, 100), "Column 1\tColumn 2\tColumn 3", fontsize=10)
    page2.insert_text((72, 120), "Data 1\tData 2\tData 3", fontsize=10)
    page2.insert_text(
        (72, 140), "Row 2 Data 1\tRow 2 Data 2\tRow 2 Data 3", fontsize=10
    )

    # Page 3: Empty page (for testing edge cases)
    doc.new_page()

    doc.save(pdf_path)
    doc.close()

    return pdf_path


@pytest.fixture
def corrupted_pdf_file(temp_directory):
    """Create a corrupted PDF file for error testing"""
    pdf_path = os.path.join(temp_directory, "corrupted_test.pdf")

    with open(pdf_path, "w") as f:
        f.write("This is not a valid PDF file content")

    return pdf_path


@pytest.fixture
def empty_pdf_file(temp_directory):
    """Create an empty PDF file for testing"""
    pdf_path = os.path.join(temp_directory, "empty_test.pdf")
    Path(pdf_path).touch()  # Create empty file
    return pdf_path


@pytest.fixture
def test_execution_context():
    """Provide test execution context information"""
    return {
        "test_date": TEST_DATE,
        "target_module": TARGET_MODULE,
        "execution_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "python_version": sys.version,
        "platform": sys.platform,
        "working_directory": str(Path.cwd()),
    }


@pytest.fixture
def mock_ui_file(temp_directory):
    """Create a mock UI file for MainWindow testing"""
    ui_path = os.path.join(temp_directory, "miner.ui")

    ui_content = """<?xml version="1.0" encoding="UTF-8"?>
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
  <property name="windowTitle">
   <string>PDF Miner</string>
  </property>
  <widget class="QWidget" name="centralwidget">
   <widget class="QLabel" name="pdfView">
    <property name="geometry">
     <rect>
      <x>10</x>
      <y>10</y>
      <width>780</width>
      <height>540</height>
     </rect>
    </property>
   </widget>
  </widget>
  <widget class="QMenuBar" name="menubar">
   <property name="geometry">
    <rect>
     <x>0</x>
     <y>0</y>
     <width>800</width>
     <height>22</height>
    </rect>
   </property>
   <widget class="QMenu" name="menuFile">
    <property name="title">
     <string>File</string>
    </property>
    <addaction name="actionOpen"/>
    <addaction name="actionExit"/>
   </widget>
   <addaction name="menuFile"/>
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
 <resources/>
 <connections/>
</ui>"""

    with open(ui_path, "w") as f:
        f.write(ui_content)

    return ui_path


@pytest.fixture(autouse=True)
def test_environment_setup(request):
    """Automatically set up test environment for each test"""
    # Set up environment variables if needed
    os.environ["PYTEST_RUNNING"] = "true"
    os.environ["TEST_DATE"] = TEST_DATE

    # Log test start
    test_name = request.node.name
    print(f"\n{'='*50}")
    print(f"Starting test: {test_name}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}")

    yield

    # Log test completion
    print(f"\n{'='*50}")
    print(f"Completed test: {test_name}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}")

    # Cleanup environment
    if "PYTEST_RUNNING" in os.environ:
        del os.environ["PYTEST_RUNNING"]


def pytest_configure(config):
    """Pytest configuration hook"""
    # Register custom markers
    config.addinivalue_line("markers", "miner: Tests for miner.py module")
    config.addinivalue_line("markers", "gui: Tests requiring GUI components")
    config.addinivalue_line(
        "markers", "pdf_tools: Tests for PDF processing tools"
    )
    config.addinivalue_line("markers", "unit_test: Unit test classification")
    config.addinivalue_line(
        "markers",
        f"date_{TEST_DATE.replace('-', '_')}: Tests created on {TEST_DATE}",
    )
    config.addinivalue_line(
        "markers", "slow: Tests that take significant time"
    )
    config.addinivalue_line("markers", "integration: Integration tests")


def pytest_runtest_setup(item):
    """Setup hook for each test item"""
    # Skip GUI tests if no display available (for CI/CD environments)
    if "gui" in [mark.name for mark in item.iter_markers()]:
        if os.environ.get("DISPLAY") is None and sys.platform.startswith(
            "linux"
        ):
            pytest.skip("GUI tests require display")


def pytest_collection_modifyitems(config, items):
    """Modify collected test items"""
    # Add markers based on test names
    for item in items:
        # Add slow marker to performance tests
        if "performance" in item.name or "concurrent" in item.name:
            item.add_marker(pytest.mark.slow)

        # Add integration marker to workflow tests
        if "workflow" in item.name or "integration" in item.name:
            item.add_marker(pytest.mark.integration)


def pytest_sessionstart(session):
    """Called before test collection"""
    print(f"\n{'*'*60}")
    print(f"Starting {TARGET_MODULE}.py Test Suite")
    print(f"Date: {TEST_DATE}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python Version: {sys.version}")
    print(f"Platform: {sys.platform}")
    print(f"Working Directory: {Path.cwd()}")
    print(f"{'*'*60}")


def pytest_sessionfinish(session, exitstatus):
    """Called after test collection and execution"""
    print(f"\n{'*'*60}")
    print(f"Completed {TARGET_MODULE}.py Test Suite")
    print(f"Exit Status: {exitstatus}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'*'*60}")


# Custom assertion helpers
def assert_valid_qimage(image):
    """Assert that an image is a valid QImage"""
    from PyQt5.QtGui import QImage

    assert isinstance(image, QImage), "Expected QImage object"
    assert not image.isNull(), "QImage should not be null"
    assert image.width() > 0, "QImage width should be positive"
    assert image.height() > 0, "QImage height should be positive"


def assert_valid_pdf_text(text, expected_content=None):
    """Assert that PDF text is valid"""
    assert isinstance(text, str), "Expected string text"
    if expected_content:
        assert (
            expected_content in text
        ), f"Expected '{expected_content}' in text"


def assert_valid_metadata(metadata, num_pages):
    """Assert that PDF metadata is valid"""
    assert isinstance(metadata, dict), "Expected dictionary metadata"
    assert isinstance(num_pages, int), "Expected integer page count"
    assert num_pages > 0, "Page count should be positive"


# Performance testing utilities
class PerformanceTimer:
    """Simple performance timer for tests"""

    def __init__(self):
        self.start_time = None
        self.end_time = None

    def start(self):
        self.start_time = datetime.now()

    def stop(self):
        self.end_time = datetime.now()

    def duration(self):
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None


@pytest.fixture
def performance_timer():
    """Provide performance timer for tests"""
    return PerformanceTimer()
