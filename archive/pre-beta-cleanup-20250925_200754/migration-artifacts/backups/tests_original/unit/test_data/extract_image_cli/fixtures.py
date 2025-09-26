"""
Test fixtures and mock data for extract_image_cli tests
Generated on: 2025-08-24
"""

import io
import os
import tempfile
from unittest.mock import Mock

import pytest
from PIL import Image


class TestFixtures:
    """Collection of test fixtures for extract_image_cli testing."""
    
    @staticmethod
    def create_mock_pdf_with_images():
        """Create a comprehensive mock PDF document with various image scenarios."""
        mock_doc = Mock()
        mock_doc.__len__ = Mock(return_value=3)  # 3 pages
        
        # Page 1: Has 2 valid images
        page1 = Mock()
        page1.get_images.return_value = [
            (1, 'large_image_data'),
            (2, 'medium_image_data')
        ]
        
        # Page 2: Has 1 small image (should be filtered out)
        page2 = Mock()
        page2.get_images.return_value = [
            (3, 'small_image_data')
        ]
        
        # Page 3: No images
        page3 = Mock()
        page3.get_images.return_value = []
        
        pages = [page1, page2, page3]
        mock_doc.__getitem__ = Mock(side_effect=lambda x: pages[x])
        mock_doc.close = Mock()
        
        # Mock different image extractions
        def mock_extract_image(xref):
            image_data = {
                1: {'image': b'large_image_bytes', 'ext': 'png'},
                2: {'image': b'medium_image_bytes', 'ext': 'jpg'},
                3: {'image': b'small_image_bytes', 'ext': 'gif'}
            }
            return image_data.get(xref, {'image': b'default', 'ext': 'png'})
        
        mock_doc.extract_image = Mock(side_effect=mock_extract_image)
        return mock_doc
    
    @staticmethod
    def create_mock_pil_image(width=200, height=150):
        """Create a mock PIL Image with specified dimensions."""
        mock_image = Mock()
        mock_image.width = width
        mock_image.height = height
        mock_image.save = Mock()
        mock_image.format = 'PNG'
        return mock_image
    
    @staticmethod
    def create_test_pdf_file(temp_dir, filename="test.pdf"):
        """Create a test PDF file for testing."""
        pdf_path = os.path.join(temp_dir, filename)
        with open(pdf_path, 'wb') as f:
            # Simple PDF structure for testing
            pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
>>
endobj
xref
0 4
0000000000 65535 f 
0000000010 00000 n 
0000000053 00000 n 
0000000125 00000 n 
trailer
<<
/Size 4
/Root 1 0 R
>>
startxref
225
%%EOF"""
            f.write(pdf_content)
        return pdf_path
    
    @staticmethod
    def create_temp_image_file(temp_dir, filename="test_image.png", 
                              width=100, height=100):
        """Create a temporary image file for testing."""
        image_path = os.path.join(temp_dir, filename)
        # Create a simple test image
        image = Image.new('RGB', (width, height), color='red')
        image.save(image_path)
        return image_path


@pytest.fixture
def test_fixtures():
    """Provide access to test fixtures."""
    return TestFixtures


@pytest.fixture
def temp_test_dirs():
    """Create temporary directories for testing with cleanup."""
    temp_input = tempfile.mkdtemp(prefix="extract_test_input_")
    temp_output = tempfile.mkdtemp(prefix="extract_test_output_")
    temp_assets = tempfile.mkdtemp(prefix="extract_test_assets_")
    
    yield {
        'input': temp_input,
        'output': temp_output,
        'assets': temp_assets
    }
    
    # Cleanup
    import shutil
    for temp_dir in [temp_input, temp_output, temp_assets]:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_qt_components():
    """Provide mocked PyQt5 components for GUI testing."""
    components = {
        'QApplication': Mock(),
        'QMainWindow': Mock(),
        'QFileDialog': Mock(),
        'QMessageBox': Mock(),
        'QProgressBar': Mock(),
        'QPushButton': Mock(),
        'QLineEdit': Mock()
    }
    
    # Setup common return values
    components['QFileDialog'].getOpenFileName = Mock(
        return_value=("/test/path.pdf", "PDF Files (*.pdf)")
    )
    components['QFileDialog'].getExistingDirectory = Mock(
        return_value="/test/output"
    )
    
    return components


@pytest.fixture
def sample_pdf_data():
    """Provide sample PDF test data."""
    return {
        'valid_pdf_path': '/path/to/test.pdf',
        'output_dir': '/path/to/output',
        'image_count': 3,
        'expected_formats': ['png', 'jpg', 'gif'],
        'min_dimensions': {'width': 100, 'height': 100}
    }


@pytest.fixture
def performance_test_data():
    """Provide data for performance testing."""
    return {
        'large_pdf_pages': 100,
        'images_per_page': 5,
        'max_processing_time': 30.0,  # seconds
        'memory_limit_mb': 500
    }


class MockLogConfig:
    """Mock logging configuration for testing."""
    
    @staticmethod
    def setup_logger(name):
        """Return a mock logger."""
        mock_logger = Mock()
        mock_logger.info = Mock()
        mock_logger.debug = Mock()
        mock_logger.warning = Mock()
        mock_logger.error = Mock()
        mock_logger.critical = Mock()
        return mock_logger


@pytest.fixture
def mock_logger():
    """Provide a mock logger for testing."""
    return MockLogConfig.setup_logger("test_logger")


# Test data constants
TEST_CONSTANTS = {
    'DEFAULT_MIN_WIDTH': 100,
    'DEFAULT_MIN_HEIGHT': 100,
    'DEFAULT_FORMAT': 'png',
    'SUPPORTED_FORMATS': ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'],
    'COMMON_IMAGE_SIZES': [
        (50, 50),    # Small (should be filtered)
        (100, 100),  # Minimum size
        (200, 150),  # Medium
        (800, 600),  # Large
        (1920, 1080) # Very large
    ]
}


@pytest.fixture
def test_constants():
    """Provide test constants."""
    return TEST_CONSTANTS


# Error simulation helpers
class ErrorSimulation:
    """Helper class for simulating various error conditions."""
    
    @staticmethod
    def file_not_found_error():
        """Simulate FileNotFoundError."""
        return FileNotFoundError("Test file not found")
    
    @staticmethod
    def permission_error():
        """Simulate PermissionError."""
        return PermissionError("Test permission denied")
    
    @staticmethod
    def pdf_corruption_error():
        """Simulate PDF corruption error."""
        return Exception("PDF file is corrupted or invalid")
    
    @staticmethod
    def image_processing_error():
        """Simulate image processing error."""
        return Exception("Cannot process image data")
    
    @staticmethod
    def memory_error():
        """Simulate memory error."""
        return MemoryError("Not enough memory to process image")


@pytest.fixture
def error_simulation():
    """Provide error simulation helpers."""
    return ErrorSimulation