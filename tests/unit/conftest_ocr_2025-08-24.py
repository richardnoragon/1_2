"""
OCR-specific test fixtures and configuration
conftest_ocr_2025-08-24.py - OCR pytest configuration and fixtures
Created: 2025-08-24
"""

import os
import shutil
import tempfile
from unittest.mock import Mock, patch

import fitz
import numpy as np
import pytest
from PIL import Image


@pytest.fixture(scope="session")
def ocr_temp_test_dir():
    """Create a temporary directory for OCR test files"""
    temp_dir = tempfile.mkdtemp(prefix="ocr_test_")
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_image_rgb():
    """Create a sample RGB image for testing"""
    return np.random.randint(0, 255, (200, 300, 3), dtype=np.uint8)


@pytest.fixture
def sample_image_grayscale():
    """Create a sample grayscale image for testing"""
    return np.random.randint(0, 255, (200, 300), dtype=np.uint8)


@pytest.fixture
def sample_binary_image():
    """Create a sample binary image for testing"""
    img = np.zeros((200, 300), dtype=np.uint8)
    img[50:150, 50:250] = 255  # White rectangle on black background
    return img


@pytest.fixture
def text_image():
    """Create an image with text-like patterns"""
    img = np.ones((200, 400, 3), dtype=np.uint8) * 255  # White background

    # Add black rectangles to simulate text
    img[50:70, 50:150] = 0  # Text line 1
    img[50:70, 160:200] = 0  # Text line 1 continued
    img[80:100, 50:200] = 0  # Text line 2
    img[110:130, 50:120] = 0  # Text line 3

    return img


@pytest.fixture
def sample_pdf_file(ocr_temp_test_dir):
    """Create a sample PDF file for testing"""
    pdf_path = os.path.join(ocr_temp_test_dir, "test_sample.pdf")

    # Create a simple PDF
    doc = fitz.open()
    page = doc.new_page()

    # Add some text content
    text_content = [
        "This is a test PDF document",
        "Created for unit testing purposes",
        "It contains multiple lines of text",
        "For testing OCR functionality",
    ]

    y_position = 72  # Start from top margin
    for line in text_content:
        page.insert_text((72, y_position), line, fontsize=12)
        y_position += 20

    doc.save(pdf_path)
    doc.close()

    return pdf_path


@pytest.fixture
def sample_image_file(ocr_temp_test_dir):
    """Create a sample image file for testing"""
    img_path = os.path.join(ocr_temp_test_dir, "test_sample.png")

    # Create an image with text-like content
    img_array = np.ones((300, 500, 3), dtype=np.uint8) * 255

    # Add some black rectangles to simulate text
    img_array[50:80, 50:200] = 0  # Header
    img_array[100:130, 50:300] = 0  # Body text line 1
    img_array[140:170, 50:250] = 0  # Body text line 2
    img_array[180:210, 50:180] = 0  # Body text line 3

    # Save as PNG
    img_pil = Image.fromarray(img_array)
    img_pil.save(img_path)

    return img_path


@pytest.fixture
def mock_tesseract_output():
    """Provide mock tesseract OCR output data"""
    return {
        "text": ["Sample", "OCR", "Text", "Output", "", "More", "Text"],
        "conf": [95.5, 87.2, 92.1, 89.3, -1, 85.7, 90.1],
        "page_num": [1, 1, 1, 1, 1, 1, 1],
        "block_num": [1, 1, 1, 1, 1, 2, 2],
        "par_num": [1, 1, 1, 1, 1, 1, 1],
        "line_num": [1, 1, 1, 1, 1, 2, 2],
        "word_num": [1, 2, 3, 4, 5, 1, 2],
        "left": [10, 50, 90, 130, 170, 10, 50],
        "top": [10, 10, 10, 10, 10, 50, 50],
        "width": [35, 30, 35, 40, 0, 35, 30],
        "height": [20, 20, 20, 20, 0, 20, 20],
    }


@pytest.fixture
def mock_pdf_document():
    """Create a mock PDF document for testing"""
    mock_doc = Mock()
    mock_doc.page_count = 3

    # Create mock pages
    mock_pages = []
    for i in range(3):
        mock_page = Mock()
        mock_page.rect = Mock()
        mock_page.rect.width = 595
        mock_page.rect.height = 842

        # Mock pixmap
        mock_pix = Mock()
        mock_pix.samples = b"\x00\x01\x02" * (200 * 300)  # RGB data
        mock_pix.h = 200
        mock_pix.w = 300
        mock_pix.n = 3
        mock_page.get_pixmap.return_value = mock_pix

        mock_pages.append(mock_page)

    mock_doc.__getitem__ = lambda self, idx: mock_pages[idx]
    return mock_doc


@pytest.fixture
def mock_ocr_logger():
    """Provide a mock logger for OCR testing"""
    with patch("log_config.setup_logger") as mock_setup:
        logger_mock = Mock()
        mock_setup.return_value = logger_mock
        yield logger_mock


@pytest.fixture
def confidence_test_data():
    """Provide test data for confidence calculations"""
    return [
        # Test case 1: All positive confidence values
        {
            "input": {
                "page_num": [1, 1, 1, 1],
                "conf": [95.5, 87.2, 92.1, 89.3],
            },
            "expected": 91.025,
        },
        # Test case 2: Mixed positive and negative values
        {
            "input": {
                "page_num": [1, 1, 1, 1, 1],
                "conf": [95.5, -1, 87.2, -1, 92.1],
            },
            "expected": 91.6,
        },
        # Test case 3: All negative values
        {
            "input": {"page_num": [1, 1, 1], "conf": [-1, -1, -1]},
            "expected": 0,
        },
    ]


@pytest.fixture
def text_generation_test_data():
    """Provide test data for text generation functions"""
    return [
        # Test case 1: Normal text with empty entries
        {
            "input": {"text": ["Hello", "", "World", "Test", "", "OCR", ""]},
            "expected": [["Hello"], ["World", "Test"], ["OCR"]],
        },
        # Test case 2: All empty text
        {"input": {"text": ["", "", "", ""]}, "expected": []},
        # Test case 3: Single word
        {"input": {"text": ["SingleWord"]}, "expected": [["SingleWord"]]},
        # Test case 4: Multiple consecutive words
        {
            "input": {"text": ["Word1", "Word2", "Word3", "Word4"]},
            "expected": [["Word1", "Word2", "Word3", "Word4"]],
        },
    ]


@pytest.fixture(autouse=True)
def setup_ocr_test_environment(monkeypatch):
    """Set up test environment variables and paths for OCR tests"""
    # Mock external dependencies
    monkeypatch.setenv("TEST_MODE", "1")

    # Mock tesseract path to avoid dependency issues
    with patch("ocr.TESSERACT_PATH", "/mock/tesseract/path"):
        with patch(
            "pytesseract.pytesseract.tesseract_cmd", "/mock/tesseract/path"
        ):
            yield


# Test data generators
def generate_test_images(count=5):
    """Generate multiple test images for batch testing"""
    images = []
    for i in range(count):
        # Create varied test images
        height, width = 100 + i * 50, 150 + i * 50
        img = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
        images.append(img)
    return images


def generate_mock_ocr_results(count=3):
    """Generate mock OCR results for testing"""
    results = []
    for i in range(count):
        result = {
            "text": [f"Word{j}" for j in range(i + 1, i + 5)],
            "conf": [90 + j for j in range(4)],
            "left": [j * 40 for j in range(4)],
            "top": [10] * 4,
            "width": [35] * 4,
            "height": [20] * 4,
        }
        results.append(result)
    return results
