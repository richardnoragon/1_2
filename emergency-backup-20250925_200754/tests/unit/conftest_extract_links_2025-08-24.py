#!/usr/bin/env python3
"""
Test configuration and fixtures for extract_links.py testing
Configuration file: conftest_extract_links_2025-08-24.py
Created: 2025-08-24
Target: Shared test fixtures and configuration for extract_links.py tests
"""

import os
import shutil
import sys
import tempfile
from unittest.mock import Mock, patch

import pikepdf
import pytest
from PyQt5.QtWidgets import QApplication


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance for testing"""
    if not QApplication.instance():
        app = QApplication([])
    else:
        app = QApplication.instance()
    yield app


@pytest.fixture
def temp_test_dir():
    """Create temporary directory for testing"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_ui_components():
    """Mock UI components for testing"""
    components = {
        "browseButton": Mock(),
        "extractButton": Mock(),
        "actionExit": Mock(),
        "inputFileEdit": Mock(),
        "outputText": Mock(),
    }
    return components


@pytest.fixture
def sample_pdf_with_links(temp_test_dir):
    """Create a sample PDF with links for testing"""
    pdf_path = os.path.join(temp_test_dir, "test_with_links.pdf")

    try:
        pdf = pikepdf.Pdf.new()
        page = pikepdf.Page.new(pdf)

        # Create annotation with link
        annot = pikepdf.Dictionary(
            {
                "/Type": pikepdf.Name("/Annot"),
                "/Subtype": pikepdf.Name("/Link"),
                "/A": pikepdf.Dictionary(
                    {
                        "/Type": pikepdf.Name("/Action"),
                        "/S": pikepdf.Name("/URI"),
                        "/URI": "https://example.com",
                    }
                ),
            }
        )

        page["/Annots"] = pikepdf.Array([annot])
        pdf.pages.append(page)
        pdf.save(pdf_path)
        pdf.close()

    except Exception:
        # If PDF creation fails, create empty file
        with open(pdf_path, "w") as f:
            f.write("")

    return pdf_path


@pytest.fixture
def sample_pdf_no_links(temp_test_dir):
    """Create a sample PDF without links for testing"""
    pdf_path = os.path.join(temp_test_dir, "test_no_links.pdf")

    try:
        pdf = pikepdf.Pdf.new()
        page = pikepdf.Page.new(pdf)
        pdf.pages.append(page)
        pdf.save(pdf_path)
        pdf.close()

    except Exception:
        # If PDF creation fails, create empty file
        with open(pdf_path, "w") as f:
            f.write("")

    return pdf_path


@pytest.fixture
def mock_logger():
    """Mock logger for testing"""
    logger = Mock()
    return logger


@pytest.fixture(autouse=True)
def setup_test_paths():
    """Setup test paths"""
    # Add source paths to sys.path for imports
    test_dir = os.path.dirname(__file__)
    base_dir = os.path.join(test_dir, "..", "..")

    extraction_path = os.path.join(
        base_dir, "src", "utilities", "pdf_tools", "pdf_content_extraction"
    )
    operations_path = os.path.join(
        base_dir, "src", "utilities", "pdf_tools", "pdf_basic_operations"
    )

    # Add paths if they exist and not already in sys.path
    for path in [extraction_path, operations_path]:
        abs_path = os.path.abspath(path)
        if os.path.exists(abs_path) and abs_path not in sys.path:
            sys.path.insert(0, abs_path)

    yield

    # Cleanup - remove added paths
    for path in [extraction_path, operations_path]:
        abs_path = os.path.abspath(path)
        if abs_path in sys.path:
            sys.path.remove(abs_path)


# Configure pytest settings
def pytest_configure(config):
    """Configure pytest settings"""
    # Disable Qt warnings for cleaner output
    os.environ["QT_LOGGING_RULES"] = "*.debug=false"

    # Set test markers
    config.addinivalue_line(
        "markers", "unit: Unit tests for individual functions"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests for multiple components"
    )
    config.addinivalue_line("markers", "ui: User interface tests")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers"""
    for item in items:
        # Add unit marker to all tests by default
        if not any(item.iter_markers()):
            item.add_marker(pytest.mark.unit)

        # Add UI marker to UI-related tests
        if "ui" in item.name.lower() or "gui" in item.name.lower():
            item.add_marker(pytest.mark.ui)
