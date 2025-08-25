"""
Comprehensive unit tests for highlight.py
Generated on August 24, 2025

This test suite provides complete coverage for the PDF highlighting tool,
including all functions, methods, edge cases, and error scenarios.
"""

import os
import re
import shutil
import sys
import tempfile
from io import BytesIO
from typing import Tuple
from unittest.mock import MagicMock, Mock, call, patch

import pytest

# Add the source directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'utilities', 'pdf_tools', 'pdf_enhancements'))

# Import the module under test
try:
    import highlight
    from highlight import (HighlightUI, extract_info, frame_matching_data,
                           highlight_matching_data, is_valid_path, parse_args,
                           process_data, process_file, process_folder,
                           redact_matching_data, remove_highlght,
                           search_for_text)
except ImportError as e:
    pytest.skip(f"Could not import highlight module: {e}", allow_module_level=True)


class TestExtractInfo:
    """Test cases for extract_info function"""
    
    @patch('highlight.fitz.open')
    def test_extract_info_success(self, mock_fitz_open, sample_pdf_path):
        """Test successful PDF info extraction"""
        # Mock PDF document
        mock_doc = Mock()
        mock_doc.isEncrypted = False
        mock_doc.metadata = {
            'title': 'Test Document',
            'author': 'Test Author',
            'subject': 'Test Subject'
        }
        mock_fitz_open.return_value = mock_doc
        
        result, info = extract_info(sample_pdf_path)
        
        assert result is True
        assert info['File'] == sample_pdf_path
        assert info['Encrypted'] == 'False'
        assert info['title'] == 'Test Document'
        assert info['author'] == 'Test Author'
        mock_fitz_open.assert_called_once_with(sample_pdf_path)
    
    @patch('highlight.fitz.open')
    def test_extract_info_encrypted_pdf(self, mock_fitz_open, sample_pdf_path):
        """Test info extraction from encrypted PDF"""
        mock_doc = Mock()
        mock_doc.isEncrypted = True
        mock_fitz_open.return_value = mock_doc
        
        result, info = extract_info(sample_pdf_path)
        
        assert result is True
        assert info['Encrypted'] == 'True'
        assert 'title' not in info  # Metadata not extracted for encrypted PDFs
    
    @patch('highlight.fitz.open')
    def test_extract_info_exception(self, mock_fitz_open, sample_pdf_path):
        """Test exception handling in extract_info"""
        mock_fitz_open.side_effect = Exception("PDF open error")
        
        result = extract_info(sample_pdf_path)
        
        assert result is None
    
    def test_extract_info_empty_path(self):
        """Test extract_info with empty path"""
        result = extract_info("")
        assert result is None
    
    def test_extract_info_none_path(self):
        """Test extract_info with None path"""
        result = extract_info(None)
        assert result is None


class TestSearchForText:
    """Test cases for search_for_text function"""
    
    def test_search_for_text_single_match(self):
        """Test searching for text with single match"""
        lines = ["This is a test line", "Another line here", "Test line again"]
        search_str = "test"
        
        results = list(search_for_text(lines, search_str))
        
        assert len(results) == 2
        assert "test" in results
    
    def test_search_for_text_multiple_matches_same_line(self):
        """Test searching with multiple matches in same line"""
        lines = ["test test test", "no match here"]
        search_str = "test"
        
        results = list(search_for_text(lines, search_str))
        
        assert len(results) == 3
        assert all(result == "test" for result in results)
    
    def test_search_for_text_case_insensitive(self):
        """Test case insensitive search"""
        lines = ["TEST", "Test", "test", "TeSt"]
        search_str = "test"
        
        results = list(search_for_text(lines, search_str))
        
        assert len(results) == 4
    
    def test_search_for_text_regex_pattern(self):
        """Test search with regex pattern"""
        lines = ["email@test.com", "another@example.org", "not an email"]
        search_str = r"\w+@\w+\.\w+"
        
        results = list(search_for_text(lines, search_str))
        
        assert len(results) == 2
        assert "email@test.com" in results
        assert "another@example.org" in results
    
    def test_search_for_text_no_matches(self):
        """Test search with no matches"""
        lines = ["no matches here", "nothing to find"]
        search_str = "xyz"
        
        results = list(search_for_text(lines, search_str))
        
        assert len(results) == 0
    
    def test_search_for_text_empty_lines(self):
        """Test search with empty lines"""
        lines = []
        search_str = "test"
        
        results = list(search_for_text(lines, search_str))
        
        assert len(results) == 0
    
    def test_search_for_text_exception_handling(self):
        """Test exception handling in search_for_text"""
        lines = ["test line"]
        search_str = "["  # Invalid regex
        
        results = list(search_for_text(lines, search_str))
        
        assert len(results) == 0


class TestRedactMatchingData:
    """Test cases for redact_matching_data function"""
    
    def test_redact_matching_data_success(self, mock_pdf_page):
        """Test successful redaction of matching data"""
        matched_values = ["test1", "test2"]
        mock_pdf_page.searchFor.side_effect = [
            [Mock()],  # Area for test1
            [Mock()]   # Area for test2
        ]
        
        matches_found = redact_matching_data(mock_pdf_page, matched_values)
        
        assert matches_found == 2
        assert mock_pdf_page.searchFor.call_count == 2
        assert mock_pdf_page.addRedactAnnot.call_count == 2
        mock_pdf_page.apply_redactions.assert_called_once()
    
    def test_redact_matching_data_multiple_areas(self, mock_pdf_page):
        """Test redaction with multiple areas per match"""
        matched_values = ["test"]
        mock_area1, mock_area2 = Mock(), Mock()
        mock_pdf_page.searchFor.return_value = [mock_area1, mock_area2]
        
        matches_found = redact_matching_data(mock_pdf_page, matched_values)
        
        assert matches_found == 1
        assert mock_pdf_page.addRedactAnnot.call_count == 2
    
    def test_redact_matching_data_no_matches(self, mock_pdf_page):
        """Test redaction with no matching values"""
        matched_values = []
        
        matches_found = redact_matching_data(mock_pdf_page, matched_values)
        
        assert matches_found == 0
        mock_pdf_page.apply_redactions.assert_called_once()
    
    def test_redact_matching_data_exception(self, mock_pdf_page):
        """Test exception handling in redact_matching_data"""
        matched_values = ["test"]
        mock_pdf_page.searchFor.side_effect = Exception("Search error")
        
        matches_found = redact_matching_data(mock_pdf_page, matched_values)
        
        assert matches_found == 0


class TestFrameMatchingData:
    """Test cases for frame_matching_data function"""
    
    @patch('highlight.fitz.fitz.Rect')
    def test_frame_matching_data_success(self, mock_rect, mock_pdf_page):
        """Test successful framing of matching data"""
        matched_values = ["test1", "test2"]
        mock_area = Mock()
        mock_area.__class__ = mock_rect
        mock_pdf_page.searchFor.return_value = [mock_area]
        mock_annot = Mock()
        mock_pdf_page.addRectAnnot.return_value = mock_annot
        
        matches_found = frame_matching_data(mock_pdf_page, matched_values)
        
        assert matches_found == 2
        assert mock_pdf_page.addRectAnnot.call_count == 2
        assert mock_annot.setColors.call_count == 2
        assert mock_annot.update.call_count == 2
    
    def test_frame_matching_data_no_areas(self, mock_pdf_page):
        """Test framing with no matching areas"""
        matched_values = ["test"]
        mock_pdf_page.searchFor.return_value = []
        
        matches_found = frame_matching_data(mock_pdf_page, matched_values)
        
        assert matches_found == 1
        mock_pdf_page.addRectAnnot.assert_not_called()
    
    def test_frame_matching_data_exception(self, mock_pdf_page):
        """Test exception handling in frame_matching_data"""
        matched_values = ["test"]
        mock_pdf_page.searchFor.side_effect = Exception("Frame error")
        
        matches_found = frame_matching_data(mock_pdf_page, matched_values)
        
        assert matches_found == 0


class TestHighlightMatchingData:
    """Test cases for highlight_matching_data function"""
    
    def test_highlight_matching_data_default(self, mock_pdf_page):
        """Test highlighting with default settings"""
        matched_values = ["test"]
        mock_area = Mock()
        mock_pdf_page.searchFor.return_value = [mock_area]
        mock_highlight = Mock()
        mock_pdf_page.addHighlightAnnot.return_value = mock_highlight
        
        matches_found = highlight_matching_data(
            mock_pdf_page, matched_values, 'Highlight'
        )
        
        assert matches_found == 1
        mock_pdf_page.addHighlightAnnot.assert_called_once_with([mock_area])
        mock_highlight.set_opacity.assert_called_once_with(1.0)
        mock_highlight.setColors.assert_called_once()
        mock_highlight.update.assert_called_once()
    
    def test_highlight_matching_data_custom_color_opacity(self, mock_pdf_page):
        """Test highlighting with custom color and opacity"""
        matched_values = ["test"]
        mock_area = Mock()
        mock_pdf_page.searchFor.return_value = [mock_area]
        mock_highlight = Mock()
        mock_pdf_page.addHighlightAnnot.return_value = mock_highlight
        
        matches_found = highlight_matching_data(
            mock_pdf_page, matched_values, 'Highlight', 'red', 0.5
        )
        
        assert matches_found == 1
        mock_highlight.set_opacity.assert_called_once_with(0.5)
        # Check that red color was used
        call_args = mock_highlight.setColors.call_args
        assert call_args[1]['fill'] == (1, 0, 0)  # Red RGB
    
    def test_highlight_matching_data_squiggly(self, mock_pdf_page):
        """Test squiggly annotation type"""
        matched_values = ["test"]
        mock_area = Mock()
        mock_pdf_page.searchFor.return_value = [mock_area]
        mock_squiggly = Mock()
        mock_pdf_page.addSquigglyAnnot.return_value = mock_squiggly
        
        matches_found = highlight_matching_data(
            mock_pdf_page, matched_values, 'Squiggly'
        )
        
        assert matches_found == 1
        mock_pdf_page.addSquigglyAnnot.assert_called_once()
    
    def test_highlight_matching_data_underline(self, mock_pdf_page):
        """Test underline annotation type"""
        matched_values = ["test"]
        mock_area = Mock()
        mock_pdf_page.searchFor.return_value = [mock_area]
        mock_underline = Mock()
        mock_pdf_page.addUnderlineAnnot.return_value = mock_underline
        
        matches_found = highlight_matching_data(
            mock_pdf_page, matched_values, 'Underline'
        )
        
        assert matches_found == 1
        mock_pdf_page.addUnderlineAnnot.assert_called_once()
    
    def test_highlight_matching_data_strikeout(self, mock_pdf_page):
        """Test strikeout annotation type"""
        matched_values = ["test"]
        mock_area = Mock()
        mock_pdf_page.searchFor.return_value = [mock_area]
        mock_strikeout = Mock()
        mock_pdf_page.addStrikeoutAnnot.return_value = mock_strikeout
        
        matches_found = highlight_matching_data(
            mock_pdf_page, matched_values, 'Strikeout'
        )
        
        assert matches_found == 1
        mock_pdf_page.addStrikeoutAnnot.assert_called_once()
    
    def test_highlight_matching_data_unknown_type(self, mock_pdf_page):
        """Test unknown annotation type defaults to highlight"""
        matched_values = ["test"]
        mock_area = Mock()
        mock_pdf_page.searchFor.return_value = [mock_area]
        mock_highlight = Mock()
        mock_pdf_page.addHighlightAnnot.return_value = mock_highlight
        
        matches_found = highlight_matching_data(
            mock_pdf_page, matched_values, 'Unknown'
        )
        
        assert matches_found == 1
        mock_pdf_page.addHighlightAnnot.assert_called_once()
    
    def test_highlight_matching_data_all_colors(self, mock_pdf_page):
        """Test all available colors"""
        matched_values = ["test"]
        mock_area = Mock()
        mock_pdf_page.searchFor.return_value = [mock_area]
        mock_highlight = Mock()
        mock_pdf_page.addHighlightAnnot.return_value = mock_highlight
        
        colors = {
            'yellow': (1, 1, 0),
            'red': (1, 0, 0),
            'green': (0, 1, 0),
            'blue': (0, 0, 1),
            'purple': (0.7, 0, 0.7),
            'unknown': (1, 1, 0)  # Should default to yellow
        }
        
        for color, expected_rgb in colors.items():
            mock_pdf_page.reset_mock()
            mock_highlight.reset_mock()
            mock_pdf_page.searchFor.return_value = [mock_area]
            mock_pdf_page.addHighlightAnnot.return_value = mock_highlight
            
            highlight_matching_data(mock_pdf_page, matched_values, 'Highlight', color)
            
            call_args = mock_highlight.setColors.call_args
            assert call_args[1]['fill'] == expected_rgb
    
    def test_highlight_matching_data_exception(self, mock_pdf_page):
        """Test exception handling in highlight_matching_data"""
        matched_values = ["test"]
        mock_pdf_page.searchFor.side_effect = Exception("Highlight error")
        
        matches_found = highlight_matching_data(
            mock_pdf_page, matched_values, 'Highlight'
        )
        
        assert matches_found == 0


class TestProcessData:
    """Test cases for process_data function"""
    
    @patch('highlight.fitz.open')
    @patch('highlight.search_for_text')
    @patch('highlight.highlight_matching_data')
    @patch('builtins.open', create=True)
    def test_process_data_highlight_success(self, mock_open, mock_highlight_func, 
                                          mock_search, mock_fitz_open, temp_pdf_path):
        """Test successful PDF processing with highlighting"""
        # Setup mocks
        mock_doc = Mock()
        mock_doc.pageCount = 2
        mock_page1, mock_page2 = Mock(), Mock()
        mock_doc.__getitem__.side_effect = [mock_page1, mock_page2]
        mock_fitz_open.return_value = mock_doc
        
        mock_page1.getText.return_value = "test content\nmore text"
        mock_page2.getText.return_value = "another test\nfinal line"
        
        mock_search.side_effect = [["test"], ["test"]]
        mock_highlight_func.side_effect = [1, 1]
        
        mock_buffer = BytesIO()
        mock_doc.save.return_value = None
        
        result = process_data(
            temp_pdf_path, f"{temp_pdf_path}_output.pdf", 
            "test", action="Highlight"
        )
        
        assert result is True
        mock_fitz_open.assert_called_once_with(temp_pdf_path)
        assert mock_search.call_count == 2
        assert mock_highlight_func.call_count == 2
    
    @patch('highlight.fitz.open')
    @patch('highlight.search_for_text')
    @patch('highlight.redact_matching_data')
    def test_process_data_redact_action(self, mock_redact_func, mock_search, 
                                       mock_fitz_open, temp_pdf_path):
        """Test PDF processing with redact action"""
        # Setup mocks
        mock_doc = Mock()
        mock_doc.pageCount = 1
        mock_page = Mock()
        mock_doc.__getitem__.return_value = mock_page
        mock_fitz_open.return_value = mock_doc
        
        mock_page.getText.return_value = "test content"
        mock_search.return_value = ["test"]
        mock_redact_func.return_value = 1
        
        with patch('builtins.open', create=True):
            result = process_data(
                temp_pdf_path, f"{temp_pdf_path}_output.pdf", 
                "test", action="Redact"
            )
        
        assert result is True
        mock_redact_func.assert_called_once()
    
    @patch('highlight.fitz.open')
    @patch('highlight.search_for_text')
    @patch('highlight.frame_matching_data')
    def test_process_data_frame_action(self, mock_frame_func, mock_search, 
                                      mock_fitz_open, temp_pdf_path):
        """Test PDF processing with frame action"""
        # Setup mocks
        mock_doc = Mock()
        mock_doc.pageCount = 1
        mock_page = Mock()
        mock_doc.__getitem__.return_value = mock_page
        mock_fitz_open.return_value = mock_doc
        
        mock_page.getText.return_value = "test content"
        mock_search.return_value = ["test"]
        mock_frame_func.return_value = 1
        
        with patch('builtins.open', create=True):
            result = process_data(
                temp_pdf_path, f"{temp_pdf_path}_output.pdf", 
                "test", action="Frame"
            )
        
        assert result is True
        mock_frame_func.assert_called_once()
    
    @patch('highlight.fitz.open')
    def test_process_data_specific_pages(self, mock_fitz_open, temp_pdf_path):
        """Test PDF processing with specific pages"""
        # Setup mocks
        mock_doc = Mock()
        mock_doc.pageCount = 3
        mock_page = Mock()
        mock_doc.__getitem__.return_value = mock_page
        mock_fitz_open.return_value = mock_doc
        
        mock_page.getText.return_value = "no matches"
        
        with patch('highlight.search_for_text', return_value=[]):
            with patch('builtins.open', create=True):
                result = process_data(
                    temp_pdf_path, f"{temp_pdf_path}_output.pdf", 
                    "test", pages=("1", "2")
                )
        
        assert result is True
        # Should only process pages 1 and 2 (0-indexed doesn't match our tuple)
        assert mock_doc.__getitem__.call_count == 2
    
    @patch('highlight.fitz.open')
    def test_process_data_exception(self, mock_fitz_open, temp_pdf_path):
        """Test exception handling in process_data"""
        mock_fitz_open.side_effect = Exception("PDF open error")
        
        with pytest.raises(Exception):
            process_data(temp_pdf_path, f"{temp_pdf_path}_output.pdf", "test")


class TestRemoveHighlight:
    """Test cases for remove_highlght function"""
    
    @patch('highlight.fitz.open')
    @patch('builtins.open', create=True)
    def test_remove_highlight_success(self, mock_open, mock_fitz_open, temp_pdf_path):
        """Test successful highlight removal"""
        # Setup mocks
        mock_doc = Mock()
        mock_doc.pageCount = 1
        mock_page = Mock()
        mock_doc.__getitem__.return_value = mock_page
        mock_fitz_open.return_value = mock_doc
        
        # Mock annotations
        mock_annot1 = Mock()
        mock_annot1.next = None
        mock_page.firstAnnot = mock_annot1
        
        result = remove_highlght(temp_pdf_path, f"{temp_pdf_path}_output.pdf")
        
        assert result is True
        mock_page.deleteAnnot.assert_called_once_with(mock_annot1)
    
    @patch('highlight.fitz.open')
    @patch('builtins.open', create=True)
    def test_remove_highlight_multiple_annotations(self, mock_open, mock_fitz_open, temp_pdf_path):
        """Test removal of multiple annotations"""
        # Setup mocks
        mock_doc = Mock()
        mock_doc.pageCount = 1
        mock_page = Mock()
        mock_doc.__getitem__.return_value = mock_page
        mock_fitz_open.return_value = mock_doc
        
        # Mock multiple annotations
        mock_annot1 = Mock()
        mock_annot2 = Mock()
        mock_annot1.next = mock_annot2
        mock_annot2.next = None
        mock_page.firstAnnot = mock_annot1
        
        result = remove_highlght(temp_pdf_path, f"{temp_pdf_path}_output.pdf")
        
        assert result is True
        assert mock_page.deleteAnnot.call_count == 2
    
    @patch('highlight.fitz.open')
    def test_remove_highlight_exception(self, mock_fitz_open, temp_pdf_path):
        """Test exception handling in remove_highlght"""
        mock_fitz_open.side_effect = Exception("PDF open error")
        
        result = remove_highlght(temp_pdf_path, f"{temp_pdf_path}_output.pdf")
        
        assert result is False


class TestProcessFile:
    """Test cases for process_file function"""
    
    @patch('highlight.process_data')
    def test_process_file_success(self, mock_process_data, temp_pdf_path):
        """Test successful file processing"""
        mock_process_data.return_value = True
        
        result = process_file(
            input_file=temp_pdf_path,
            output_file=f"{temp_pdf_path}_output.pdf",
            search_str="test",
            action="Highlight"
        )
        
        assert result is True
        mock_process_data.assert_called_once()
    
    @patch('highlight.remove_highlght')
    def test_process_file_remove_action(self, mock_remove, temp_pdf_path):
        """Test file processing with remove action"""
        mock_remove.return_value = True
        
        result = process_file(
            input_file=temp_pdf_path,
            action="Remove"
        )
        
        assert result is True
        mock_remove.assert_called_once()
    
    def test_process_file_default_output(self, temp_pdf_path):
        """Test file processing with default output file"""
        with patch('highlight.process_data', return_value=True) as mock_process_data:
            result = process_file(
                input_file=temp_pdf_path,
                search_str="test",
                action="Highlight"
            )
        
        assert result is True
        # Output file should default to input file
        call_args = mock_process_data.call_args
        assert call_args[1]['output_file'] == temp_pdf_path
    
    @patch('highlight.process_data')
    def test_process_file_exception(self, mock_process_data, temp_pdf_path):
        """Test exception handling in process_file"""
        mock_process_data.side_effect = Exception("Processing error")
        
        result = process_file(
            input_file=temp_pdf_path,
            search_str="test",
            action="Highlight"
        )
        
        assert result is False


class TestProcessFolder:
    """Test cases for process_folder function"""
    
    @patch('os.walk')
    @patch('highlight.process_file')
    def test_process_folder_success(self, mock_process_file, mock_walk, temp_dir):
        """Test successful folder processing"""
        mock_walk.return_value = [
            (temp_dir, [], ['file1.pdf', 'file2.pdf', 'file3.txt'])
        ]
        mock_process_file.return_value = True
        
        result = process_folder(
            input_folder=temp_dir,
            search_str="test",
            action="Highlight"
        )
        
        assert result is True
        assert mock_process_file.call_count == 2  # Only PDF files
    
    @patch('os.walk')
    @patch('highlight.process_file')
    def test_process_folder_recursive(self, mock_process_file, mock_walk, temp_dir):
        """Test recursive folder processing"""
        mock_walk.return_value = [
            (temp_dir, ['subdir'], ['file1.pdf']),
            (os.path.join(temp_dir, 'subdir'), [], ['file2.pdf'])
        ]
        mock_process_file.return_value = True
        
        result = process_folder(
            input_folder=temp_dir,
            search_str="test",
            action="Highlight",
            recursive=True
        )
        
        assert result is True
        assert mock_process_file.call_count == 2
    
    @patch('os.walk')
    @patch('highlight.process_file')
    def test_process_folder_non_recursive(self, mock_process_file, mock_walk, temp_dir):
        """Test non-recursive folder processing"""
        mock_walk.return_value = [
            (temp_dir, ['subdir'], ['file1.pdf']),
            (os.path.join(temp_dir, 'subdir'), [], ['file2.pdf'])
        ]
        mock_process_file.return_value = True
        
        result = process_folder(
            input_folder=temp_dir,
            search_str="test",
            action="Highlight",
            recursive=False
        )
        
        assert result is True
        assert mock_process_file.call_count == 1  # Only top level
    
    @patch('os.walk')
    def test_process_folder_exception(self, mock_walk, temp_dir):
        """Test exception handling in process_folder"""
        mock_walk.side_effect = Exception("Walk error")
        
        result = process_folder(
            input_folder=temp_dir,
            search_str="test",
            action="Highlight"
        )
        
        assert result is False


class TestIsValidPath:
    """Test cases for is_valid_path function"""
    
    def test_is_valid_path_file(self, temp_file):
        """Test validation of existing file path"""
        result = is_valid_path(temp_file)
        assert result == temp_file
    
    def test_is_valid_path_directory(self, temp_dir):
        """Test validation of existing directory path"""
        result = is_valid_path(temp_dir)
        assert result == temp_dir
    
    def test_is_valid_path_nonexistent(self):
        """Test validation of non-existent path"""
        with pytest.raises(ValueError, match="Invalid Path"):
            is_valid_path("/path/that/does/not/exist")
    
    def test_is_valid_path_empty(self):
        """Test validation of empty path"""
        with pytest.raises(ValueError, match="Invalid Path"):
            is_valid_path("")
    
    def test_is_valid_path_none(self):
        """Test validation of None path"""
        with pytest.raises(ValueError, match="Invalid Path"):
            is_valid_path(None)


class TestParseArgs:
    """Test cases for parse_args function"""
    
    @patch('sys.argv')
    @patch('highlight.is_valid_path')
    def test_parse_args_file_input(self, mock_is_valid_path, mock_argv, temp_file):
        """Test argument parsing for file input"""
        mock_is_valid_path.return_value = temp_file
        mock_argv.__getitem__.side_effect = [
            'highlight.py', '-i', temp_file, '-s', 'test', '-a', 'Highlight'
        ]
        
        with patch('os.path.isfile', return_value=True):
            with patch('os.path.isdir', return_value=False):
                args = parse_args()
        
        assert args['input_path'] == temp_file
        assert args['search_str'] == 'test'
        assert args['action'] == 'Highlight'
    
    @patch('sys.argv')
    @patch('highlight.is_valid_path')
    def test_parse_args_directory_input(self, mock_is_valid_path, mock_argv, temp_dir):
        """Test argument parsing for directory input"""
        mock_is_valid_path.return_value = temp_dir
        mock_argv.__getitem__.side_effect = [
            'highlight.py', '-i', temp_dir, '-s', 'test', '-r', 'true'
        ]
        
        with patch('os.path.isfile', return_value=False):
            with patch('os.path.isdir', return_value=True):
                args = parse_args()
        
        assert args['input_path'] == temp_dir
        assert args['recursive'] is True
    
    @patch('sys.argv')
    @patch('highlight.is_valid_path')
    def test_parse_args_remove_action(self, mock_is_valid_path, mock_argv, temp_file):
        """Test argument parsing for remove action"""
        mock_is_valid_path.return_value = temp_file
        mock_argv.__getitem__.side_effect = [
            'highlight.py', '-i', temp_file, '-a', 'Remove'
        ]
        
        with patch('os.path.isfile', return_value=True):
            with patch('os.path.isdir', return_value=False):
                args = parse_args()
        
        assert args['action'] == 'Remove'
        assert 'search_str' not in args


class TestHighlightUI:
    """Test cases for HighlightUI class"""
    
    @pytest.fixture
    def mock_qt_app(self):
        """Mock QApplication for testing"""
        with patch('highlight.QApplication') as mock_app:
            yield mock_app
    
    @patch('highlight.uic.loadUi')
    @patch('highlight.QMainWindow.__init__')
    def test_highlight_ui_init_success(self, mock_super_init, mock_load_ui):
        """Test successful HighlightUI initialization"""
        mock_ui = Mock()
        mock_ui.browseButton = Mock()
        mock_ui.processButton = Mock()
        mock_ui.actionExit = Mock()
        mock_ui.actionCombo = Mock()
        mock_ui.colorCombo = Mock()
        mock_ui.opacitySlider = Mock()
        mock_ui.show = Mock()
        
        with patch.object(HighlightUI, '__dict__', mock_ui.__dict__):
            ui = HighlightUI()
        
        mock_load_ui.assert_called_once_with('highlight.ui', ui)
        mock_ui.browseButton.clicked.connect.assert_called_once()
        mock_ui.processButton.clicked.connect.assert_called_once()
    
    @patch('highlight.uic.loadUi')
    def test_highlight_ui_init_exception(self, mock_load_ui):
        """Test HighlightUI initialization exception"""
        mock_load_ui.side_effect = Exception("UI load error")
        
        with pytest.raises(Exception):
            HighlightUI()
    
    def test_on_action_changed_redact(self):
        """Test on_action_changed with redact action"""
        ui = Mock()
        ui.colorCombo = Mock()
        ui.opacitySlider = Mock()
        
        HighlightUI.on_action_changed(ui, 'Redact')
        
        ui.colorCombo.setEnabled.assert_called_once_with(False)
        ui.opacitySlider.setEnabled.assert_called_once_with(False)
    
    def test_on_action_changed_remove(self):
        """Test on_action_changed with remove action"""
        ui = Mock()
        ui.colorCombo = Mock()
        ui.opacitySlider = Mock()
        
        HighlightUI.on_action_changed(ui, 'Remove')
        
        ui.colorCombo.setEnabled.assert_called_once_with(False)
        ui.opacitySlider.setEnabled.assert_called_once_with(False)
    
    def test_on_action_changed_highlight(self):
        """Test on_action_changed with highlight action"""
        ui = Mock()
        ui.colorCombo = Mock()
        ui.opacitySlider = Mock()
        
        HighlightUI.on_action_changed(ui, 'Highlight')
        
        ui.colorCombo.setEnabled.assert_called_once_with(True)
        ui.opacitySlider.setEnabled.assert_called_once_with(True)
    
    @patch('highlight.QFileDialog.getOpenFileName')
    @patch('highlight.extract_info')
    def test_browse_file_success(self, mock_extract_info, mock_file_dialog):
        """Test successful file browsing"""
        mock_file_dialog.return_value = ('/path/to/file.pdf', 'PDF Files (*.pdf)')
        mock_extract_info.return_value = (True, {})
        
        ui = Mock()
        ui.inputPathEdit = Mock()
        ui.statusBar = Mock()
        ui.statusBar.return_value = Mock()
        
        HighlightUI.browse_file(ui)
        
        ui.inputPathEdit.setText.assert_called_once_with('/path/to/file.pdf')
        assert ui.input_file == '/path/to/file.pdf'
    
    @patch('highlight.QFileDialog.getOpenFileName')
    def test_browse_file_cancelled(self, mock_file_dialog):
        """Test file browsing when cancelled"""
        mock_file_dialog.return_value = ('', '')
        
        ui = Mock()
        ui.inputPathEdit = Mock()
        
        HighlightUI.browse_file(ui)
        
        ui.inputPathEdit.setText.assert_not_called()
    
    @patch('highlight.QFileDialog.getOpenFileName')
    @patch('highlight.QMessageBox.critical')
    def test_browse_file_exception(self, mock_message_box, mock_file_dialog):
        """Test file browsing exception handling"""
        mock_file_dialog.side_effect = Exception("File dialog error")
        
        ui = Mock()
        
        HighlightUI.browse_file(ui)
        
        mock_message_box.assert_called_once()
    
    @patch('highlight.process_data')
    @patch('highlight.QMessageBox')
    def test_process_success(self, mock_message_box, mock_process_data):
        """Test successful processing"""
        ui = Mock()
        ui.input_file = '/path/to/input.pdf'
        ui.searchEdit = Mock()
        ui.searchEdit.text.return_value = 'test'
        ui.actionCombo = Mock()
        ui.actionCombo.currentText.return_value = 'Highlight'
        ui.colorCombo = Mock()
        ui.colorCombo.currentText.return_value = 'Yellow'
        ui.opacitySlider = Mock()
        ui.opacitySlider.value.return_value = 50
        ui.pagesEdit = Mock()
        ui.pagesEdit.text.return_value = ''
        
        mock_process_data.return_value = True
        
        HighlightUI.process(ui)
        
        mock_process_data.assert_called_once()
        mock_message_box.information.assert_called_once()
    
    @patch('highlight.QMessageBox.warning')
    def test_process_no_input_file(self, mock_message_box):
        """Test processing with no input file"""
        ui = Mock()
        ui.input_file = None
        
        HighlightUI.process(ui)
        
        mock_message_box.assert_called_once()
    
    @patch('highlight.QMessageBox.warning')
    def test_process_no_search_text(self, mock_message_box):
        """Test processing with no search text"""
        ui = Mock()
        ui.input_file = '/path/to/input.pdf'
        ui.searchEdit = Mock()
        ui.searchEdit.text.return_value = ''
        
        HighlightUI.process(ui)
        
        mock_message_box.assert_called_once()


if __name__ == '__main__':
    pytest.main([__file__])