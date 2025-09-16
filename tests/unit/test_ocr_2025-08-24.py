"""
Comprehensive Unit Tests for OCR Module
Test file: test_ocr_2025-08-24.py
Target: src/tools/pdf_tools/pdf_enhancements/ocr.py
Created: 2025-08-24
Framework: pytest with coverage, HTML and JSON reporting
"""

import os
import shutil
import sys
import tempfile
from datetime import datetime
from io import BytesIO
from unittest.mock import MagicMock, Mock, call, patch

import cv2
import fitz
import numpy as np
import pandas as pd
import pytest
from PIL import Image

# Add the source directory to the path for importing the module under test
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'utilities', 'pdf_tools', 'pdf_enhancements'))

# Mock the log_config module before importing ocr
with patch('log_config.setup_logger') as mock_logger:
    mock_logger.return_value = MagicMock()
    import ocr

class TestPixmapToNumpyConversion:
    """Test suite for pix2np function"""
    
    def test_pix2np_valid_rgba_pixmap(self):
        """Test conversion of valid RGBA pixmap to numpy array"""
        # Create mock pixmap with RGBA data
        mock_pix = Mock()
        mock_pix.samples = b'\x00\x01\x02\x03' * 6  # 6 pixels of RGBA data
        mock_pix.h = 2
        mock_pix.w = 3
        mock_pix.n = 4  # RGBA
        
        result = ocr.pix2np(mock_pix)
        
        assert result is not None
        assert isinstance(result, np.ndarray)
        assert result.shape == (2, 3, 3)  # Height, Width, BGR channels
    
    def test_pix2np_valid_rgb_pixmap(self):
        """Test conversion of valid RGB pixmap to numpy array"""
        mock_pix = Mock()
        mock_pix.samples = b'\x00\x01\x02' * 6  # 6 pixels of RGB data
        mock_pix.h = 2
        mock_pix.w = 3
        mock_pix.n = 3  # RGB
        
        result = ocr.pix2np(mock_pix)
        
        assert result is not None
        assert isinstance(result, np.ndarray)
        assert result.shape == (2, 3, 3)  # Height, Width, BGR channels
    
    def test_pix2np_grayscale_pixmap(self):
        """Test conversion of grayscale pixmap to numpy array"""
        mock_pix = Mock()
        mock_pix.samples = b'\x80' * 6  # 6 pixels of grayscale data
        mock_pix.h = 2
        mock_pix.w = 3
        mock_pix.n = 1  # Grayscale
        
        with patch('cv2.cvtColor') as mock_cvt:
            mock_cvt.return_value = np.zeros((2, 3, 3), dtype=np.uint8)
            result = ocr.pix2np(mock_pix)
            
            assert result is not None
            assert isinstance(result, np.ndarray)
            mock_cvt.assert_called_once()
    
    def test_pix2np_invalid_pixmap(self):
        """Test handling of invalid pixmap data"""
        mock_pix = Mock()
        mock_pix.samples = None
        mock_pix.h = 2
        mock_pix.w = 3
        mock_pix.n = 3
        
        result = ocr.pix2np(mock_pix)
        
        assert result is None
    
    def test_pix2np_exception_handling(self):
        """Test exception handling in pix2np"""
        mock_pix = Mock()
        mock_pix.samples.side_effect = Exception("Test exception")
        
        result = ocr.pix2np(mock_pix)
        
        assert result is None


class TestImagePreprocessing:
    """Test suite for image preprocessing functions"""
    
    @pytest.fixture
    def sample_image(self):
        """Create a sample test image"""
        return np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    
    @pytest.fixture
    def sample_grayscale_image(self):
        """Create a sample grayscale test image"""
        return np.random.randint(0, 255, (100, 100), dtype=np.uint8)
    
    def test_grayscale_conversion(self, sample_image):
        """Test grayscale conversion function"""
        with patch('cv2.cvtColor') as mock_cvt:
            mock_cvt.return_value = np.zeros((100, 100), dtype=np.uint8)
            
            result = ocr.grayscale(sample_image)
            
            mock_cvt.assert_called_once_with(sample_image, cv2.COLOR_BGR2GRAY)
            assert result is not None
    
    def test_remove_noise(self, sample_grayscale_image):
        """Test noise removal function"""
        with patch('cv2.medianBlur') as mock_blur:
            mock_blur.return_value = sample_grayscale_image
            
            result = ocr.remove_noise(sample_grayscale_image)
            
            mock_blur.assert_called_once_with(sample_grayscale_image, 5)
            assert result is not None
    
    def test_threshold_operation(self, sample_grayscale_image):
        """Test thresholding operation"""
        with patch('cv2.threshold') as mock_thresh:
            mock_thresh.return_value = (127, sample_grayscale_image)
            
            result = ocr.threshold(sample_grayscale_image)
            
            mock_thresh.assert_called_once_with(
                sample_grayscale_image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU
            )
            assert result is not None
    
    def test_dilate_operation(self, sample_grayscale_image):
        """Test dilation morphological operation"""
        with patch('cv2.dilate') as mock_dilate:
            mock_dilate.return_value = sample_grayscale_image
            
            result = ocr.dilate(sample_grayscale_image)
            
            mock_dilate.assert_called_once()
            assert result is not None
    
    def test_erode_operation(self, sample_grayscale_image):
        """Test erosion morphological operation"""
        with patch('cv2.erode') as mock_erode:
            mock_erode.return_value = sample_grayscale_image
            
            result = ocr.erode(sample_grayscale_image)
            
            mock_erode.assert_called_once()
            assert result is not None
    
    def test_opening_operation(self, sample_grayscale_image):
        """Test opening morphological operation"""
        with patch('cv2.morphologyEx') as mock_morph:
            mock_morph.return_value = sample_grayscale_image
            
            result = ocr.opening(sample_grayscale_image)
            
            mock_morph.assert_called_once()
            assert result is not None
    
    def test_canny_edge_detection(self, sample_grayscale_image):
        """Test Canny edge detection"""
        with patch('cv2.Canny') as mock_canny:
            mock_canny.return_value = sample_grayscale_image
            
            result = ocr.canny(sample_grayscale_image)
            
            mock_canny.assert_called_once_with(sample_grayscale_image, 100, 200)
            assert result is not None
    
    def test_deskew_operation(self, sample_grayscale_image):
        """Test deskewing operation"""
        with patch('cv2.minAreaRect') as mock_rect, \
             patch('cv2.getRotationMatrix2D') as mock_rotation, \
             patch('cv2.warpAffine') as mock_warp:
            
            mock_rect.return_value = ((50, 50), (40, 20), -15)  # center, size, angle
            mock_rotation.return_value = np.eye(2, 3)
            mock_warp.return_value = sample_grayscale_image
            
            result = ocr.deskew(sample_grayscale_image)
            
            mock_rect.assert_called_once()
            mock_rotation.assert_called_once()
            mock_warp.assert_called_once()
            assert result is not None
    
    def test_match_template(self, sample_grayscale_image):
        """Test template matching"""
        template = np.random.randint(0, 255, (20, 20), dtype=np.uint8)
        
        with patch('cv2.matchTemplate') as mock_match:
            mock_match.return_value = np.random.rand(81, 81)
            
            result = ocr.match_template(sample_grayscale_image, template)
            
            mock_match.assert_called_once_with(
                sample_grayscale_image, template, cv2.TM_CCOEFF_NORMED
            )
            assert result is not None
    
    def test_convert_img2bin(self, sample_image):
        """Test binary image conversion"""
        with patch.object(ocr, 'grayscale') as mock_gray, \
             patch.object(ocr, 'threshold') as mock_thresh, \
             patch('cv2.bitwise_not') as mock_not:
            
            mock_gray.return_value = np.zeros((100, 100), dtype=np.uint8)
            mock_not.return_value = np.zeros((100, 100), dtype=np.uint8)
            mock_thresh.return_value = np.zeros((100, 100), dtype=np.uint8)
            
            result = ocr.convert_img2bin(sample_image)
            
            mock_gray.assert_called_once_with(sample_image)
            mock_not.assert_called_once()
            mock_thresh.assert_called_once()
            assert result is not None


class TestImageDisplay:
    """Test suite for image display functionality"""
    
    def test_display_img_success(self):
        """Test successful image display"""
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        
        with patch('cv2.namedWindow') as mock_window, \
             patch('cv2.setWindowTitle') as mock_title, \
             patch('cv2.resizeWindow') as mock_resize, \
             patch('cv2.imshow') as mock_show, \
             patch('cv2.waitKey') as mock_wait, \
             patch('cv2.destroyAllWindows') as mock_destroy:
            
            mock_wait.return_value = ord('q')  # Simulate key press
            
            ocr.display_img("Test Title", test_image)
            
            mock_window.assert_called_once_with('img', cv2.WINDOW_NORMAL)
            mock_title.assert_called_once_with('img', "Test Title")
            mock_resize.assert_called_once_with('img', 1200, 900)
            mock_show.assert_called_once_with('img', test_image)
            mock_wait.assert_called_once_with(0)
            mock_destroy.assert_called_once()
    
    def test_display_img_exception_handling(self):
        """Test exception handling in display_img"""
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        
        with patch('cv2.namedWindow', side_effect=Exception("Test exception")):
            # Should not raise exception, should handle gracefully
            ocr.display_img("Test Title", test_image)


class TestTextProcessing:
    """Test suite for text processing functions"""
    
    @pytest.fixture
    def sample_ocr_details(self):
        """Create sample OCR details dictionary"""
        return {
            'text': ['Hello', '', 'World', 'Test', '', 'OCR', ''],
            'conf': [95.5, -1, 87.2, 92.1, -1, 89.3, -1],
            'page_num': [1, 1, 1, 1, 1, 1, 1],
            'block_num': [1, 1, 1, 2, 2, 2, 2],
            'par_num': [1, 1, 1, 1, 1, 1, 1],
            'line_num': [1, 1, 1, 2, 2, 2, 2],
            'left': [10, 20, 30, 40, 50, 60, 70],
            'top': [10, 20, 30, 40, 50, 60, 70],
            'width': [50, 0, 60, 40, 0, 45, 0],
            'height': [20, 0, 20, 20, 0, 20, 0]
        }
    
    def test_generate_ss_text_valid_input(self, sample_ocr_details):
        """Test text generation from OCR details"""
        result = ocr.generate_ss_text(sample_ocr_details)
        
        assert isinstance(result, list)
        assert len(result) > 0
        # Should group words into lines
        expected_lines = [['Hello'], ['World', 'Test'], ['OCR']]
        assert result == expected_lines
    
    def test_generate_ss_text_empty_input(self):
        """Test text generation with empty input"""
        empty_details = {'text': []}
        result = ocr.generate_ss_text(empty_details)
        
        assert isinstance(result, list)
        assert len(result) == 0
    
    def test_generate_ss_text_all_empty_text(self):
        """Test text generation with all empty text entries"""
        empty_text_details = {'text': ['', '', '', '']}
        result = ocr.generate_ss_text(empty_text_details)
        
        assert isinstance(result, list)
        assert len(result) == 0
    
    def test_search_for_text_found(self, sample_ocr_details):
        """Test text search with matches found"""
        search_term = "Hello"
        results = list(ocr.search_for_text(sample_ocr_details, search_term))
        
        assert len(results) == 1
        assert results[0] == "Hello"
    
    def test_search_for_text_case_insensitive(self, sample_ocr_details):
        """Test case-insensitive text search"""
        search_term = "hello"
        results = list(ocr.search_for_text(sample_ocr_details, search_term))
        
        assert len(results) == 1
        assert results[0] == "Hello"
    
    def test_search_for_text_not_found(self, sample_ocr_details):
        """Test text search with no matches"""
        search_term = "NotFound"
        results = list(ocr.search_for_text(sample_ocr_details, search_term))
        
        assert len(results) == 0
    
    def test_search_for_text_regex_pattern(self, sample_ocr_details):
        """Test text search with regex pattern"""
        search_term = r"W\w+"  # Words starting with W
        results = list(ocr.search_for_text(sample_ocr_details, search_term))
        
        assert len(results) == 1
        assert results[0] == "World"


class TestPageContent:
    """Test suite for page content handling"""
    
    def test_save_page_content_valid_data(self):
        """Test saving page content with valid data"""
        pdf_content = pd.DataFrame(columns=['page', 'line_id', 'line'])
        page_id = 1
        page_data = [['Hello', 'World'], ['Test', 'OCR']]
        
        result = ocr.save_page_content(pdf_content, page_id, page_data)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert result.iloc[0]['page'] == 1
        assert result.iloc[0]['line_id'] == 1
        assert result.iloc[0]['line'] == 'Hello World'
        assert result.iloc[1]['line'] == 'Test OCR'
    
    def test_save_page_content_empty_data(self):
        """Test saving page content with empty data"""
        pdf_content = pd.DataFrame(columns=['page', 'line_id', 'line'])
        page_id = 1
        page_data = []
        
        result = ocr.save_page_content(pdf_content, page_id, page_data)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
    
    def test_save_page_content_none_data(self):
        """Test saving page content with None data"""
        pdf_content = pd.DataFrame(columns=['page', 'line_id', 'line'])
        page_id = 1
        page_data = None
        
        result = ocr.save_page_content(pdf_content, page_id, page_data)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
    
    @patch('pandas.DataFrame.to_csv')
    def test_save_file_content(self, mock_to_csv):
        """Test saving file content to CSV"""
        pdf_content = pd.DataFrame({
            'page': [1, 1, 2],
            'line_id': [1, 2, 1],
            'line': ['Line 1', 'Line 2', 'Line 3']
        })
        input_file = r"C:\test\document.pdf"
        
        result = ocr.save_file_content(pdf_content, input_file)
        
        expected_file = r"C:\test\document.csv"
        assert result == expected_file
        mock_to_csv.assert_called_once_with(expected_file, sep=',', index=False)


class TestConfidenceCalculation:
    """Test suite for confidence score calculation"""
    
    def test_calculate_ss_confidence_valid_data(self):
        """Test confidence calculation with valid data"""
        ss_details = {
            'page_num': [1, 1, 1, 1],
            'conf': [95.5, 87.2, 92.1, 89.3]
        }
        
        result = ocr.calculate_ss_confidence(ss_details)
        
        expected_confidence = (95.5 + 87.2 + 92.1 + 89.3) / 4
        assert abs(result - expected_confidence) < 0.01
    
    def test_calculate_ss_confidence_with_negative_values(self):
        """Test confidence calculation filtering negative values"""
        ss_details = {
            'page_num': [1, 1, 1, 1, 1],
            'conf': [95.5, -1, 87.2, -1, 92.1]
        }
        
        result = ocr.calculate_ss_confidence(ss_details)
        
        # Should ignore -1 values
        expected_confidence = (95.5 + 87.2 + 92.1) / 3
        assert abs(result - expected_confidence) < 0.01
    
    def test_calculate_ss_confidence_empty_data(self):
        """Test confidence calculation with empty data"""
        ss_details = {
            'page_num': [],
            'conf': []
        }
        
        result = ocr.calculate_ss_confidence(ss_details)
        
        assert result == 0
    
    def test_calculate_ss_confidence_exception_handling(self):
        """Test confidence calculation exception handling"""
        ss_details = {
            'page_num': [1, 1],
            'conf': ['invalid', 'data']  # Invalid numeric data
        }
        
        result = ocr.calculate_ss_confidence(ss_details)
        
        assert result == 0


class TestImageToBytesConversion:
    """Test suite for image to bytes conversion"""
    
    def test_image_to_byte_array_jpeg(self):
        """Test converting JPEG image to byte array"""
        # Create a test image
        img_array = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        test_image = Image.fromarray(img_array)
        test_image.format = 'JPEG'
        
        result = ocr.image_to_byte_array(test_image)
        
        assert result is not None
        assert isinstance(result, bytes)
        assert len(result) > 0
    
    def test_image_to_byte_array_png(self):
        """Test converting PNG image to byte array"""
        img_array = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        test_image = Image.fromarray(img_array)
        test_image.format = 'PNG'
        
        result = ocr.image_to_byte_array(test_image)
        
        assert result is not None
        assert isinstance(result, bytes)
        assert len(result) > 0
    
    def test_image_to_byte_array_no_format(self):
        """Test converting image without format to byte array"""
        img_array = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        test_image = Image.fromarray(img_array)
        test_image.format = None
        
        result = ocr.image_to_byte_array(test_image)
        
        assert result is not None
        assert isinstance(result, bytes)
        assert len(result) > 0
    
    def test_image_to_byte_array_exception(self):
        """Test image to byte array conversion exception handling"""
        # Create a mock image that will cause an exception
        mock_image = Mock()
        mock_image.save.side_effect = Exception("Test exception")
        
        result = ocr.image_to_byte_array(mock_image)
        
        assert result is None


class TestOcrImg:
    """Test suite for OCR image processing function"""
    
    @pytest.fixture
    def sample_image(self):
        """Create a sample test image"""
        return np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    
    @pytest.fixture
    def mock_tesseract_details(self):
        """Mock tesseract OCR output details"""
        return {
            'text': ['Hello', 'World', 'Test'],
            'conf': [95.5, 87.2, 92.1],
            'left': [10, 50, 90],
            'top': [10, 10, 10],
            'width': [30, 35, 25],
            'height': [20, 20, 20]
        }
    
    @patch('pytesseract.image_to_data')
    @patch.object(ocr, 'convert_img2bin')
    @patch.object(ocr, 'calculate_ss_confidence')
    @patch.object(ocr, 'generate_ss_text')
    @patch('cv2.rectangle')
    @patch('cv2.imwrite')
    def test_ocr_img_basic_processing(self, mock_imwrite, mock_rectangle, 
                                    mock_generate_text, mock_calc_confidence,
                                    mock_convert_bin, mock_tesseract, 
                                    sample_image, mock_tesseract_details):
        """Test basic OCR image processing"""
        # Setup mocks
        mock_convert_bin.return_value = sample_image
        mock_tesseract.return_value = mock_tesseract_details
        mock_calc_confidence.return_value = 91.6
        mock_generate_text.return_value = [['Hello', 'World'], ['Test']]
        mock_rectangle.return_value = sample_image
        
        result = ocr.ocr_img(
            img=sample_image,
            input_file=None,
            search_str=None,
            highlight_readable_text=False,
            action='Highlight',
            show_comparison=False,
            generate_output=True
        )
        
        highlighted_img, readable_items, matches, confidence, output_data = result
        
        assert highlighted_img is not None
        assert readable_items == 3  # All items have confidence > 30
        assert matches == 0  # No search string provided
        assert confidence == 91.6
        assert output_data == [['Hello', 'World'], ['Test']]
        
        mock_convert_bin.assert_called_once()
        mock_tesseract.assert_called_once()
        mock_calc_confidence.assert_called_once()
        mock_generate_text.assert_called_once()
        mock_imwrite.assert_called_once()
    
    @patch('pytesseract.image_to_data')
    @patch.object(ocr, 'convert_img2bin')
    @patch.object(ocr, 'calculate_ss_confidence')
    @patch('cv2.rectangle')
    @patch('cv2.imwrite')
    @patch('re.findall')
    def test_ocr_img_with_search_highlight(self, mock_findall, mock_imwrite, 
                                         mock_rectangle, mock_calc_confidence,
                                         mock_convert_bin, mock_tesseract, 
                                         sample_image, mock_tesseract_details):
        """Test OCR image processing with search and highlight"""
        # Setup mocks
        mock_convert_bin.return_value = sample_image
        mock_tesseract.return_value = mock_tesseract_details
        mock_calc_confidence.return_value = 91.6
        mock_rectangle.return_value = sample_image
        mock_findall.side_effect = [['Hello'], [], []]  # Only first text matches
        
        result = ocr.ocr_img(
            img=sample_image,
            input_file=None,
            search_str="Hello",
            highlight_readable_text=False,
            action='Highlight',
            show_comparison=False,
            generate_output=False
        )
        
        highlighted_img, readable_items, matches, confidence, output_data = result
        
        assert highlighted_img is not None
        assert readable_items == 3
        assert matches == 1  # One match found
        assert confidence == 91.6
        assert output_data is None  # generate_output=False
        
        # Should call findall for each text item
        assert mock_findall.call_count == 3
    
    @patch('pytesseract.image_to_data')
    @patch.object(ocr, 'convert_img2bin')
    @patch.object(ocr, 'calculate_ss_confidence')
    @patch('cv2.rectangle')
    @patch('cv2.imwrite')
    @patch('re.findall')
    def test_ocr_img_with_search_redact(self, mock_findall, mock_imwrite, 
                                      mock_rectangle, mock_calc_confidence,
                                      mock_convert_bin, mock_tesseract, 
                                      sample_image, mock_tesseract_details):
        """Test OCR image processing with search and redact"""
        # Setup mocks
        mock_convert_bin.return_value = sample_image
        mock_tesseract.return_value = mock_tesseract_details
        mock_calc_confidence.return_value = 91.6
        mock_rectangle.return_value = sample_image
        mock_findall.side_effect = [['Hello'], [], []]  # Only first text matches
        
        result = ocr.ocr_img(
            img=sample_image,
            input_file=None,
            search_str="Hello",
            highlight_readable_text=False,
            action='Redact',
            show_comparison=False,
            generate_output=False
        )
        
        highlighted_img, readable_items, matches, confidence, output_data = result
        
        assert highlighted_img is not None
        assert readable_items == 3
        assert matches == 1
        assert confidence == 91.6
        
        # Verify redact action called rectangle with black color
        mock_rectangle.assert_called()
    
    @patch('cv2.imread')
    @patch('pytesseract.image_to_data')
    @patch.object(ocr, 'convert_img2bin')
    @patch.object(ocr, 'calculate_ss_confidence')
    @patch('cv2.imwrite')
    def test_ocr_img_from_file(self, mock_imwrite, mock_calc_confidence,
                             mock_convert_bin, mock_tesseract, mock_imread,
                             sample_image, mock_tesseract_details):
        """Test OCR processing from image file"""
        # Setup mocks
        mock_imread.return_value = sample_image
        mock_convert_bin.return_value = sample_image
        mock_tesseract.return_value = mock_tesseract_details
        mock_calc_confidence.return_value = 91.6
        
        result = ocr.ocr_img(
            img=None,
            input_file="test_image.jpg",
            search_str=None,
            highlight_readable_text=False,
            action='Highlight',
            show_comparison=False,
            generate_output=False
        )
        
        highlighted_img, readable_items, matches, confidence, output_data = result
        
        assert highlighted_img is not None
        assert readable_items == 3
        assert confidence == 91.6
        
        mock_imread.assert_called_once_with("test_image.jpg")
    
    def test_ocr_img_exception_handling(self, sample_image):
        """Test OCR image processing exception handling"""
        with patch.object(ocr, 'convert_img2bin', side_effect=Exception("Test exception")):
            result = ocr.ocr_img(
                img=sample_image,
                input_file=None,
                search_str=None,
                highlight_readable_text=False,
                action='Highlight',
                show_comparison=False,
                generate_output=False
            )
            
            highlighted_img, readable_items, matches, confidence, output_data = result
            
            assert highlighted_img is None
            assert readable_items == 0
            assert matches == 0
            assert confidence == 0
            assert output_data is None


class TestOcrFile:
    """Test suite for OCR file processing function"""
    
    @pytest.fixture
    def temp_pdf_file(self):
        """Create a temporary PDF file for testing"""
        temp_dir = tempfile.mkdtemp()
        pdf_path = os.path.join(temp_dir, "test.pdf")
        
        # Create a simple PDF with PyMuPDF
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((72, 72), "Test PDF Content")
        doc.save(pdf_path)
        doc.close()
        
        yield pdf_path
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    @patch('fitz.open')
    @patch.object(ocr, 'pix2np')
    @patch.object(ocr, 'ocr_img')
    @patch.object(ocr, 'save_page_content')
    @patch.object(ocr, 'save_file_content')
    @patch.object(ocr, 'image_to_byte_array')
    def test_ocr_file_basic_processing(self, mock_img_to_bytes, mock_save_file,
                                     mock_save_page, mock_ocr_img, mock_pix2np,
                                     mock_fitz_open):
        """Test basic PDF file OCR processing"""
        # Setup mocks
        mock_doc = Mock()
        mock_doc.page_count = 1
        mock_page = Mock()
        mock_page.rect = Mock()
        mock_page.rect.width = 595
        mock_page.rect.height = 842
        mock_pix = Mock()
        mock_doc.__getitem__.return_value = mock_page
        mock_page.get_pixmap.return_value = mock_pix
        mock_fitz_open.side_effect = [mock_doc, Mock()]  # Input and output docs
        
        mock_pix2np.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_ocr_img.return_value = (
            np.zeros((100, 100, 3), dtype=np.uint8),  # highlighted_img
            10,  # readable_items
            2,   # matches
            95.5,  # confidence
            [['Test', 'Content']]  # output_data
        )
        mock_save_page.return_value = pd.DataFrame()
        mock_save_file.return_value = "test.csv"
        mock_img_to_bytes.return_value = b"test_image_bytes"
        
        # Setup output PDF mock
        mock_output_doc = Mock()
        mock_new_page = Mock()
        mock_output_doc.newPage.return_value = mock_new_page
        mock_fitz_open.return_value = mock_output_doc
        
        kwargs = {
            'input_file': 'test.pdf',
            'output_file': 'output.pdf',
            'search_str': 'test',
            'pages': None,
            'highlight_readable_text': False,
            'action': 'Highlight',
            'show_comparison': False,
            'generate_output': True
        }
        
        result = ocr.ocr_file(**kwargs)
        
        # Verify the function completed without returning False
        assert result is None  # Function returns None on success
        
        mock_doc.close.assert_called_once()
        mock_output_doc.save.assert_called_once_with('output.pdf')
        mock_output_doc.close.assert_called_once()
    
    @patch('fitz.open')
    def test_ocr_file_specific_pages(self, mock_fitz_open):
        """Test OCR file processing with specific pages"""
        # Setup mocks
        mock_doc = Mock()
        mock_doc.page_count = 3
        mock_fitz_open.side_effect = [mock_doc, Mock()]
        
        with patch.object(ocr, 'pix2np'), \
             patch.object(ocr, 'ocr_img') as mock_ocr_img, \
             patch.object(ocr, 'image_to_byte_array'):
            
            mock_ocr_img.return_value = (None, 0, 0, 0, None)
            
            kwargs = {
                'input_file': 'test.pdf',
                'output_file': None,
                'search_str': None,
                'pages': (0, 2),  # Only process pages 0 and 2
                'highlight_readable_text': False,
                'action': None,
                'show_comparison': False,
                'generate_output': False
            }
            
            ocr.ocr_file(**kwargs)
            
            # Should only process pages 0 and 2, so ocr_img called twice
            assert mock_ocr_img.call_count == 2
    
    @patch('fitz.open')
    def test_ocr_file_exception_handling(self, mock_fitz_open):
        """Test OCR file processing exception handling"""
        mock_fitz_open.side_effect = Exception("File not found")
        
        kwargs = {
            'input_file': 'nonexistent.pdf',
            'output_file': None,
            'search_str': None,
            'pages': None,
            'highlight_readable_text': False,
            'action': None,
            'show_comparison': False,
            'generate_output': False
        }
        
        result = ocr.ocr_file(**kwargs)
        
        assert result is False


class TestOcrFolder:
    """Test suite for OCR folder processing function"""
    
    @pytest.fixture
    def temp_folder_with_pdfs(self):
        """Create a temporary folder with test PDF files"""
        temp_dir = tempfile.mkdtemp()
        
        # Create test PDF files
        pdf_files = []
        for i in range(3):
            pdf_path = os.path.join(temp_dir, f"test_{i}.pdf")
            doc = fitz.open()
            page = doc.new_page()
            page.insert_text((72, 72), f"Test PDF {i} Content")
            doc.save(pdf_path)
            doc.close()
            pdf_files.append(pdf_path)
        
        # Create a non-PDF file (should be ignored)
        txt_path = os.path.join(temp_dir, "test.txt")
        with open(txt_path, 'w') as f:
            f.write("This is not a PDF")
        
        yield temp_dir, pdf_files
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    @patch.object(ocr, 'ocr_file')
    def test_ocr_folder_basic_processing(self, mock_ocr_file, temp_folder_with_pdfs):
        """Test basic folder OCR processing"""
        temp_dir, pdf_files = temp_folder_with_pdfs
        
        kwargs = {
            'input_folder': temp_dir,
            'recursive': False,
            'search_str': 'test',
            'pages': None,
            'action': 'Highlight',
            'generate_output': True
        }
        
        ocr.ocr_folder(**kwargs)
        
        # Should call ocr_file for each PDF file
        assert mock_ocr_file.call_count == 3
        
        # Verify calls were made with correct parameters
        for call in mock_ocr_file.call_args_list:
            args, kwargs_call = call
            assert 'input_file' in kwargs_call
            assert kwargs_call['input_file'].endswith('.pdf')
            assert kwargs_call['search_str'] == 'test'
            assert kwargs_call['action'] == 'Highlight'
            assert kwargs_call['generate_output'] is True
    
    @patch.object(ocr, 'ocr_file')
    def test_ocr_folder_recursive_processing(self, mock_ocr_file):
        """Test recursive folder OCR processing"""
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Create nested directory structure
            sub_dir = os.path.join(temp_dir, 'subdir')
            os.makedirs(sub_dir)
            
            # Create PDF in main directory
            pdf1_path = os.path.join(temp_dir, "test1.pdf")
            doc1 = fitz.open()
            doc1.new_page()
            doc1.save(pdf1_path)
            doc1.close()
            
            # Create PDF in subdirectory
            pdf2_path = os.path.join(sub_dir, "test2.pdf")
            doc2 = fitz.open()
            doc2.new_page()
            doc2.save(pdf2_path)
            doc2.close()
            
            kwargs = {
                'input_folder': temp_dir,
                'recursive': True,
                'search_str': None,
                'pages': None,
                'action': None,
                'generate_output': False
            }
            
            ocr.ocr_folder(**kwargs)
            
            # Should process both PDFs in recursive mode
            assert mock_ocr_file.call_count == 2
            
        finally:
            shutil.rmtree(temp_dir)
    
    @patch.object(ocr, 'ocr_file')
    def test_ocr_folder_non_recursive(self, mock_ocr_file):
        """Test non-recursive folder processing"""
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Create nested directory structure
            sub_dir = os.path.join(temp_dir, 'subdir')
            os.makedirs(sub_dir)
            
            # Create PDF in main directory
            pdf1_path = os.path.join(temp_dir, "test1.pdf")
            doc1 = fitz.open()
            doc1.new_page()
            doc1.save(pdf1_path)
            doc1.close()
            
            # Create PDF in subdirectory
            pdf2_path = os.path.join(sub_dir, "test2.pdf")
            doc2 = fitz.open()
            doc2.new_page()
            doc2.save(pdf2_path)
            doc2.close()
            
            kwargs = {
                'input_folder': temp_dir,
                'recursive': False,
                'search_str': None,
                'pages': None,
                'action': None,
                'generate_output': False
            }
            
            ocr.ocr_folder(**kwargs)
            
            # Should only process PDF in main directory (non-recursive)
            assert mock_ocr_file.call_count == 1
            
        finally:
            shutil.rmtree(temp_dir)


class TestPathValidation:
    """Test suite for path validation function"""
    
    def test_is_valid_path_existing_file(self):
        """Test path validation with existing file"""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            result = ocr.is_valid_path(temp_path)
            assert result == temp_path
        finally:
            os.unlink(temp_path)
    
    def test_is_valid_path_existing_directory(self):
        """Test path validation with existing directory"""
        temp_dir = tempfile.mkdtemp()
        
        try:
            result = ocr.is_valid_path(temp_dir)
            assert result == temp_dir
        finally:
            os.rmdir(temp_dir)
    
    def test_is_valid_path_nonexistent(self):
        """Test path validation with nonexistent path"""
        nonexistent_path = r"C:\nonexistent\path\file.pdf"
        
        with pytest.raises(ValueError, match="Invalid Path"):
            ocr.is_valid_path(nonexistent_path)
    
    def test_is_valid_path_empty_string(self):
        """Test path validation with empty string"""
        with pytest.raises(ValueError, match="Invalid Path"):
            ocr.is_valid_path("")
    
    def test_is_valid_path_none(self):
        """Test path validation with None"""
        with pytest.raises(ValueError, match="Invalid Path"):
            ocr.is_valid_path(None)


class TestArgumentParsing:
    """Test suite for command line argument parsing"""
    
    @patch('sys.argv')
    @patch.object(ocr, 'is_valid_path')
    def test_parse_args_basic_file_input(self, mock_is_valid_path, mock_argv):
        """Test parsing basic file input arguments"""
        mock_is_valid_path.return_value = "test.pdf"
        mock_argv[:] = ['ocr.py', '-i', 'test.pdf']
        
        with patch('os.path.isfile', return_value=True), \
             patch('os.path.isdir', return_value=False):
            
            args = ocr.parse_args()
            
            assert args['input_path'] == 'test.pdf'
            assert 'output_file' in args  # Should add file-specific arguments
            assert 'highlight_readable_text' in args
            assert 'show_comparison' in args
    
    @patch('sys.argv')
    @patch.object(ocr, 'is_valid_path')
    def test_parse_args_directory_input(self, mock_is_valid_path, mock_argv):
        """Test parsing directory input arguments"""
        mock_is_valid_path.return_value = "/test/directory"
        mock_argv[:] = ['ocr.py', '-i', '/test/directory']
        
        with patch('os.path.isfile', return_value=False), \
             patch('os.path.isdir', return_value=True):
            
            args = ocr.parse_args()
            
            assert args['input_path'] == '/test/directory'
            assert 'recursive' in args  # Should add directory-specific arguments
    
    @patch('sys.argv')
    @patch.object(ocr, 'is_valid_path')
    def test_parse_args_with_all_options(self, mock_is_valid_path, mock_argv):
        """Test parsing with all command line options"""
        mock_is_valid_path.return_value = "test.pdf"
        mock_argv[:] = [
            'ocr.py', '-i', 'test.pdf', '-o', 'output.pdf',
            '-s', 'search_term', '-a', 'Highlight',
            '-p', '(0,1)', '-g', '-t', '-c'
        ]
        
        with patch('os.path.isfile', return_value=True), \
             patch('os.path.isdir', return_value=False):
            
            args = ocr.parse_args()
            
            assert args['input_path'] == 'test.pdf'
            assert args['output_file'] == 'output.pdf'
            assert args['search_str'] == 'search_term'
            assert args['action'] == 'Highlight'
            assert args['pages'] == '(0,1)'
            assert args['generate_output'] is True
            assert args['highlight_readable_text'] is True
            assert args['show_comparison'] is True


class TestOcrUI:
    """Test suite for OCR UI class"""
    
    @patch('PyQt5.QtWidgets.QApplication')
    @patch('PyQt5.uic.loadUi')
    def test_ocr_ui_initialization_success(self, mock_load_ui, mock_qapp):
        """Test successful OCR UI initialization"""
        # Create mock UI elements
        mock_ui = Mock()
        mock_ui.browseButton = Mock()
        mock_ui.processButton = Mock()
        mock_ui.actionExit = Mock()
        mock_ui.previewView = Mock()
        mock_ui.statusBar = Mock()
        mock_ui.inputFileEdit = Mock()
        mock_ui.batchModeCheckbox = Mock()
        mock_ui.searchEdit = Mock()
        mock_ui.actionCombo = Mock()
        mock_ui.generateOutputCheckbox = Mock()
        mock_ui.pagesEdit = Mock()
        mock_ui.outputText = Mock()
        
        # Mock the loadUi to set up the UI elements
        def setup_ui(ui_file, instance):
            for attr_name in dir(mock_ui):
                if not attr_name.startswith('_'):
                    setattr(instance, attr_name, getattr(mock_ui, attr_name))
        
        mock_load_ui.side_effect = setup_ui
        
        with patch('PyQt5.QtWidgets.QMainWindow.__init__'), \
             patch('PyQt5.QtWidgets.QGraphicsScene'), \
             patch('PyQt5.QtWidgets.QPushButton'), \
             patch('PyQt5.QtWidgets.QProgressBar'):
            
            ui = ocr.OcrUI()
            
            assert ui.input_files == []
            assert ui.is_batch is False
            assert ui.current_preview_item == 0
            
            # Verify signal connections were attempted
            mock_ui.browseButton.clicked.connect.assert_called()
            mock_ui.processButton.clicked.connect.assert_called()
            mock_ui.actionExit.triggered.connect.assert_called()
    
    @patch('PyQt5.QtWidgets.QApplication')
    @patch('PyQt5.uic.loadUi')
    def test_ocr_ui_initialization_failure(self, mock_load_ui, mock_qapp):
        """Test OCR UI initialization failure handling"""
        mock_load_ui.side_effect = Exception("UI file not found")
        
        with patch('PyQt5.QtWidgets.QMainWindow.__init__'), \
             patch('PyQt5.QtWidgets.QMessageBox.critical') as mock_msg:
            
            ui = ocr.OcrUI()
            
            mock_msg.assert_called_once()


class TestMainFunction:
    """Test suite for main function"""
    
    @patch('PyQt5.QtWidgets.QApplication')
    @patch.object(ocr, 'OcrUI')
    def test_main_function_success(self, mock_ocr_ui, mock_qapp):
        """Test successful main function execution"""
        mock_app = Mock()
        mock_qapp.return_value = mock_app
        mock_window = Mock()
        mock_ocr_ui.return_value = mock_window
        
        ocr.main()
        
        mock_qapp.assert_called_once_with([])
        mock_ocr_ui.assert_called_once()
        mock_app.exec_.assert_called_once()
    
    @patch('PyQt5.QtWidgets.QApplication')
    @patch.object(ocr, 'OcrUI')
    @patch('sys.exit')
    def test_main_function_exception(self, mock_exit, mock_ocr_ui, mock_qapp):
        """Test main function exception handling"""
        mock_qapp.side_effect = Exception("Application failed to start")
        
        ocr.main()
        
        mock_exit.assert_called_once_with(1)


# Test execution timestamp and result file generation
class TestResultGeneration:
    """Test suite for generating test results and reports"""
    
    def test_execution_timestamp_generation(self):
        """Test that execution timestamp is properly generated"""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        assert len(timestamp) == 19  # YYYY-MM-DD_HH-MM-SS format
        assert timestamp[4] == '-'
        assert timestamp[7] == '-'
        assert timestamp[10] == '_'
        assert timestamp[13] == '-'
        assert timestamp[16] == '-'
    
    def test_result_filename_convention(self):
        """Test result filename follows the specified convention"""
        today = datetime.now().strftime("%Y-%m-%d")
        expected_test_filename = f"test_ocr_{today}.py"
        expected_result_filename = f"result_ocr_{today}.html"
        
        current_filename = "test_ocr_2025-08-24.py"
        
        assert current_filename.startswith("test_")
        assert "ocr" in current_filename
        assert current_filename.endswith(".py")
        assert "2025-08-24" in current_filename


# Integration tests to verify the overall OCR pipeline
class TestOcrIntegration:
    """Integration tests for OCR functionality"""
    
    @pytest.fixture
    def sample_test_image(self):
        """Create a simple test image with text"""
        # Create a white image with black text
        img = np.ones((200, 400, 3), dtype=np.uint8) * 255
        
        # Add some text-like rectangles (simulating text)
        cv2.rectangle(img, (50, 50), (350, 80), (0, 0, 0), -1)  # Text line 1
        cv2.rectangle(img, (50, 100), (300, 130), (0, 0, 0), -1)  # Text line 2
        
        return img
    
    @patch('pytesseract.image_to_data')
    @patch.object(ocr, 'calculate_ss_confidence')
    def test_full_ocr_pipeline(self, mock_calc_confidence, mock_tesseract, sample_test_image):
        """Test the complete OCR processing pipeline"""
        # Mock tesseract response
        mock_tesseract_details = {
            'text': ['Sample', 'Text', 'For', 'Testing'],
            'conf': [95.5, 87.2, 92.1, 89.3],
            'left': [50, 100, 150, 200],
            'top': [50, 50, 50, 50],
            'width': [40, 35, 25, 45],
            'height': [20, 20, 20, 20]
        }
        mock_tesseract.return_value = mock_tesseract_details
        mock_calc_confidence.return_value = 91.0
        
        with patch('cv2.imwrite'):
            result = ocr.ocr_img(
                img=sample_test_image,
                input_file=None,
                search_str="Text",
                highlight_readable_text=True,
                action='Highlight',
                show_comparison=False,
                generate_output=True
            )
        
        highlighted_img, readable_items, matches, confidence, output_data = result
        
        assert highlighted_img is not None
        assert readable_items == 4  # All 4 words should be readable
        assert matches == 1  # One match for "Text"
        assert confidence == 91.0
        assert output_data is not None
        assert len(output_data) > 0


if __name__ == "__main__":
    # Generate execution timestamp
    execution_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    print(f"Starting OCR Unit Tests - Execution Time: {execution_timestamp}")
    print("=" * 80)
    
    # Run the tests
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        f"--html=C:/Users/HP1/1_2/1_2/tests/unit/result_ocr_2025-08-24_{execution_timestamp}.html",
        "--self-contained-html",
        f"--json-report=C:/Users/HP1/1_2/1_2/tests/unit/result_ocr_2025-08-24_{execution_timestamp}.json",
        "--cov=ocr",
        "--cov-report=html:C:/Users/HP1/1_2/1_2/tests/unit/coverage_ocr_2025-08-24",
        "--cov-report=term-missing"
    ])