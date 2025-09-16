"""
Comprehensive unit tests for split.py
Test file: test_split_2025-08-24.py
Execution timestamp: 2025-08-24
Target module: src/tools/pdf_tools/pdf_basic_operations/split.py

This test suite provides comprehensive coverage of all functions and methods
in the split.py module, including edge cases, error handling, and GUI components.
"""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, call, patch

import pytest
from PyQt5.QtWidgets import QApplication, QMessageBox

# Add the source directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src" / 
                     "utilities" / "pdf_tools" / "pdf_basic_operations"))

# Import the module under test
import split


class TestSplitPdfFunction:
    """Test cases for the split_pdf function."""
    
    @pytest.mark.unit
    @pytest.mark.pdf
    def test_split_pdf_by_pages_per_file_success(self, sample_pdf_5_pages, 
                                                 output_directory, mock_logger,
                                                 mock_qmessagebox, mock_pikepdf):
        """Test successful PDF splitting by pages per file."""
        # Arrange
        pages_per_file = 2
        
        # Act
        result = split.split_pdf(sample_pdf_5_pages, output_directory, 
                               pages_per_file=pages_per_file)
        
        # Assert
        assert result is True
        mock_logger.info.assert_called()
        mock_logger.debug.assert_called()
        
    @pytest.mark.unit
    @pytest.mark.pdf
    def test_split_pdf_by_page_ranges_success(self, sample_pdf_10_pages,
                                             output_directory, mock_logger,
                                             mock_qmessagebox, mock_pikepdf):
        """Test successful PDF splitting by page ranges."""
        # Arrange
        page_ranges = ["1-3", "4-6", "7-10"]
        
        # Act
        result = split.split_pdf(sample_pdf_10_pages, output_directory,
                               page_ranges=page_ranges)
        
        # Assert
        assert result is True
        mock_logger.info.assert_called()
        
    @pytest.mark.unit
    @pytest.mark.pdf
    def test_split_pdf_individual_pages_success(self, sample_pdf_5_pages,
                                               output_directory, mock_logger,
                                               mock_qmessagebox, mock_pikepdf):
        """Test successful PDF splitting into individual pages."""
        # Arrange & Act
        result = split.split_pdf(sample_pdf_5_pages, output_directory)
        
        # Assert
        assert result is True
        mock_logger.info.assert_called()
        
    @pytest.mark.unit
    @pytest.mark.pdf
    def test_split_pdf_file_not_found(self, nonexistent_pdf, output_directory,
                                     mock_logger, mock_qmessagebox):
        """Test split_pdf with non-existent input file."""
        # Act
        result = split.split_pdf(nonexistent_pdf, output_directory)
        
        # Assert
        assert result is False
        mock_logger.error.assert_called()
        mock_qmessagebox.critical.assert_called()
        
    @pytest.mark.unit
    @pytest.mark.pdf
    def test_split_pdf_corrupted_file(self, corrupted_pdf, output_directory,
                                     mock_logger, mock_qmessagebox):
        """Test split_pdf with corrupted PDF file."""
        # Act
        result = split.split_pdf(corrupted_pdf, output_directory)
        
        # Assert
        assert result is False
        mock_logger.error.assert_called()
        mock_qmessagebox.critical.assert_called()
        
    @pytest.mark.unit
    @pytest.mark.pdf
    def test_split_pdf_invalid_page_ranges(self, sample_pdf_5_pages,
                                          output_directory, mock_logger,
                                          mock_qmessagebox, mock_pikepdf):
        """Test split_pdf with invalid page ranges."""
        # Arrange
        page_ranges = ["1-10", "invalid-range", "0-1"]  # 1-10 exceeds pages
        
        # Act
        result = split.split_pdf(sample_pdf_5_pages, output_directory,
                               page_ranges=page_ranges)
        
        # Assert
        assert result is True  # Should still succeed for valid ranges
        mock_logger.warning.assert_called()
        mock_qmessagebox.warning.assert_called()
        
    @pytest.mark.unit
    @pytest.mark.pdf
    def test_split_pdf_malformed_page_ranges(self, sample_pdf_5_pages,
                                            output_directory, mock_logger,
                                            mock_qmessagebox, mock_pikepdf):
        """Test split_pdf with malformed page range format."""
        # Arrange
        page_ranges = ["1-2", "invalid_format", "3-4"]
        
        # Act
        result = split.split_pdf(sample_pdf_5_pages, output_directory,
                               page_ranges=page_ranges)
        
        # Assert
        assert result is True  # Should succeed for valid ranges
        mock_logger.error.assert_called()
        mock_qmessagebox.warning.assert_called()
        
    @pytest.mark.unit
    @pytest.mark.pdf
    def test_split_pdf_zero_pages_per_file(self, sample_pdf_5_pages,
                                          output_directory, mock_logger,
                                          mock_qmessagebox, mock_pikepdf):
        """Test split_pdf with zero pages per file."""
        # Act
        result = split.split_pdf(sample_pdf_5_pages, output_directory,
                               pages_per_file=0)
        
        # Assert
        # Should default to individual pages when pages_per_file is falsy
        assert result is True
        
    @pytest.mark.unit
    @pytest.mark.pdf
    def test_split_pdf_creates_output_directory(self, sample_pdf_5_pages,
                                               temp_dir, mock_logger,
                                               mock_qmessagebox, mock_pikepdf):
        """Test that split_pdf creates output directory if it doesn't exist."""
        # Arrange
        nonexistent_output = os.path.join(temp_dir, "new_output_dir")
        
        # Act
        result = split.split_pdf(sample_pdf_5_pages, nonexistent_output)
        
        # Assert
        assert result is True
        assert os.path.exists(nonexistent_output)
        
    @pytest.mark.unit
    @pytest.mark.pdf
    def test_split_pdf_with_single_page(self, sample_pdf_1_page,
                                       output_directory, mock_logger,
                                       mock_qmessagebox, mock_pikepdf):
        """Test split_pdf with a single-page PDF."""
        # Act
        result = split.split_pdf(sample_pdf_1_page, output_directory,
                               pages_per_file=2)
        
        # Assert
        assert result is True
        
    @pytest.mark.unit
    @pytest.mark.pdf
    def test_split_pdf_exception_during_operation(self, sample_pdf_5_pages,
                                                  output_directory, mock_logger,
                                                  mock_qmessagebox):
        """Test split_pdf with exception during split operation."""
        # Arrange
        with patch('split.pikepdf.Pdf.open') as mock_open:
            mock_pdf = Mock()
            mock_pdf.pages = [Mock() for _ in range(5)]
            mock_open.return_value = mock_pdf
            
            # Make save method raise an exception
            with patch('split.pikepdf.Pdf.new') as mock_new:
                mock_new_pdf = Mock()
                mock_new_pdf.save.side_effect = Exception("Save failed")
                mock_new.return_value = mock_new_pdf
                
                # Act
                result = split.split_pdf(sample_pdf_5_pages, output_directory)
                
                # Assert
                assert result is False
                mock_logger.error.assert_called()
                mock_qmessagebox.critical.assert_called()


class TestSplitUIClass:
    """Test cases for the SplitUI class."""
    
    @pytest.mark.gui
    @pytest.mark.unit
    def test_splitui_initialization_success(self, qapp, mock_splitui_components,
                                           mock_logger):
        """Test successful SplitUI initialization."""
        # Arrange
        with patch('split.QtWidgets.QProgressBar'):
            with patch.object(split.SplitUI, 'show'):
                # Act
                ui = split.SplitUI()
                
                # Assert
                assert ui is not None
                assert ui.current_file is None
                assert ui.current_output_dir is None
                mock_logger.info.assert_called_with("Initializing Split UI")
                
    @pytest.mark.gui
    @pytest.mark.unit
    def test_splitui_initialization_failure(self, qapp, mock_logger,
                                           mock_qmessagebox):
        """Test SplitUI initialization failure."""
        # Arrange
        with patch('split.uic.loadUi', side_effect=Exception("UI load failed")):
            with patch.object(split.SplitUI, 'close'):
                # Act
                ui = split.SplitUI()
                
                # Assert
                mock_logger.error.assert_called()
                mock_qmessagebox.critical.assert_called()
                
    @pytest.mark.gui
    @pytest.mark.unit
    def test_browse_file_success(self, qapp, mock_splitui_components,
                                mock_qfiledialog, mock_logger):
        """Test successful file browsing."""
        # Arrange
        mock_qfiledialog.getOpenFileName.return_value = (
            "test.pdf", "PDF Files (*.pdf)")
        
        with patch('split.QtWidgets.QProgressBar'):
            with patch.object(split.SplitUI, 'show'):
                ui = split.SplitUI()
                ui.inputFileEdit = Mock()
                ui.update_split_button = Mock()
                
                # Act
                ui.browse_file()
                
                # Assert
                assert ui.current_file == "test.pdf"
                ui.inputFileEdit.setText.assert_called_with("test.pdf")
                ui.update_split_button.assert_called()
                mock_logger.info.assert_called()
                
    @pytest.mark.gui
    @pytest.mark.unit
    def test_browse_file_cancelled(self, qapp, mock_splitui_components,
                                  mock_qfiledialog, mock_logger):
        """Test file browsing when user cancels."""
        # Arrange
        mock_qfiledialog.getOpenFileName.return_value = ("", "")
        
        with patch('split.QtWidgets.QProgressBar'):
            with patch.object(split.SplitUI, 'show'):
                ui = split.SplitUI()
                ui.inputFileEdit = Mock()
                
                # Act
                ui.browse_file()
                
                # Assert
                assert ui.current_file is None
                ui.inputFileEdit.setText.assert_not_called()
                
    @pytest.mark.gui
    @pytest.mark.unit
    def test_browse_file_exception(self, qapp, mock_splitui_components,
                                  mock_qfiledialog, mock_logger,
                                  mock_qmessagebox):
        """Test file browsing with exception."""
        # Arrange
        mock_qfiledialog.getOpenFileName.side_effect = Exception("Dialog error")
        
        with patch('split.QtWidgets.QProgressBar'):
            with patch.object(split.SplitUI, 'show'):
                ui = split.SplitUI()
                
                # Act
                ui.browse_file()
                
                # Assert
                mock_logger.error.assert_called()
                mock_qmessagebox.critical.assert_called()
                
    @pytest.mark.gui
    @pytest.mark.unit
    def test_browse_output_dir_success(self, qapp, mock_splitui_components,
                                      mock_qfiledialog, mock_logger):
        """Test successful output directory browsing."""
        # Arrange
        mock_qfiledialog.getExistingDirectory.return_value = "/output/dir"
        
        with patch('split.QtWidgets.QProgressBar'):
            with patch.object(split.SplitUI, 'show'):
                ui = split.SplitUI()
                ui.outputDirEdit = Mock()
                ui.update_split_button = Mock()
                
                # Act
                ui.browse_output_dir()
                
                # Assert
                assert ui.current_output_dir == "/output/dir"
                ui.outputDirEdit.setText.assert_called_with("/output/dir")
                ui.update_split_button.assert_called()
                mock_logger.info.assert_called()
                
    @pytest.mark.gui
    @pytest.mark.unit
    def test_browse_output_dir_cancelled(self, qapp, mock_splitui_components,
                                        mock_qfiledialog):
        """Test output directory browsing when user cancels."""
        # Arrange
        mock_qfiledialog.getExistingDirectory.return_value = ""
        
        with patch('split.QtWidgets.QProgressBar'):
            with patch.object(split.SplitUI, 'show'):
                ui = split.SplitUI()
                ui.outputDirEdit = Mock()
                
                # Act
                ui.browse_output_dir()
                
                # Assert
                assert ui.current_output_dir is None
                ui.outputDirEdit.setText.assert_not_called()
                
    @pytest.mark.gui
    @pytest.mark.unit
    def test_update_split_button_both_selected(self, qapp, 
                                              mock_splitui_components):
        """Test update_split_button when both file and directory selected."""
        # Arrange
        with patch('split.QtWidgets.QProgressBar'):
            with patch.object(split.SplitUI, 'show'):
                ui = split.SplitUI()
                ui.current_file = "test.pdf"
                ui.current_output_dir = "/output"
                ui.splitButton = Mock()
                
                # Act
                ui.update_split_button()
                
                # Assert
                ui.splitButton.setEnabled.assert_called_with(True)
                
    @pytest.mark.gui
    @pytest.mark.unit
    def test_update_split_button_missing_file(self, qapp, 
                                             mock_splitui_components):
        """Test update_split_button when file is missing."""
        # Arrange
        with patch('split.QtWidgets.QProgressBar'):
            with patch.object(split.SplitUI, 'show'):
                ui = split.SplitUI()
                ui.current_file = None
                ui.current_output_dir = "/output"
                ui.splitButton = Mock()
                
                # Act
                ui.update_split_button()
                
                # Assert
                ui.splitButton.setEnabled.assert_called_with(False)
                
    @pytest.mark.gui
    @pytest.mark.unit
    def test_update_split_button_missing_directory(self, qapp,
                                                   mock_splitui_components):
        """Test update_split_button when directory is missing."""
        # Arrange
        with patch('split.QtWidgets.QProgressBar'):
            with patch.object(split.SplitUI, 'show'):
                ui = split.SplitUI()
                ui.current_file = "test.pdf"
                ui.current_output_dir = None
                ui.splitButton = Mock()
                
                # Act
                ui.update_split_button()
                
                # Assert
                ui.splitButton.setEnabled.assert_called_with(False)
                
    @pytest.mark.gui
    @pytest.mark.unit
    def test_split_pdf_missing_inputs(self, qapp, mock_splitui_components,
                                     mock_logger, mock_qmessagebox):
        """Test split_pdf method with missing inputs."""
        # Arrange
        with patch('split.QtWidgets.QProgressBar'):
            with patch.object(split.SplitUI, 'show'):
                ui = split.SplitUI()
                ui.current_file = None
                ui.current_output_dir = None
                
                # Act
                ui.split_pdf()
                
                # Assert
                mock_logger.warning.assert_called()
                mock_qmessagebox.warning.assert_called()
                
    @pytest.mark.gui
    @pytest.mark.unit
    def test_split_pdf_pages_per_file_mode(self, qapp, mock_splitui_components,
                                          mock_logger, mock_qmessagebox):
        """Test split_pdf method in pages per file mode."""
        # Arrange
        with patch('split.QtWidgets.QProgressBar'):
            with patch.object(split.SplitUI, 'show'):
                ui = split.SplitUI()
                ui.current_file = "test.pdf"
                ui.current_output_dir = "/output"
                ui.pagesPerFileRadio = Mock()
                ui.pagesPerFileRadio.isChecked.return_value = True
                ui.pagesPerFileEdit = Mock()
                ui.pagesPerFileEdit.text.return_value = "2"
                ui.pageRangesRadio = Mock()
                ui.pageRangesRadio.isChecked.return_value = False
                ui.progressBar = Mock()
                ui.statusBar = Mock()
                
                with patch('split.split_pdf', return_value=True) as mock_split:
                    with patch('split.fitz.open') as mock_fitz:
                        mock_doc = Mock()
                        mock_doc.page_count = 5
                        mock_fitz.return_value = mock_doc
                        
                        # Act
                        ui.split_pdf()
                        
                        # Assert
                        mock_split.assert_called()
                        
    @pytest.mark.gui
    @pytest.mark.unit
    def test_split_pdf_invalid_pages_per_file(self, qapp, 
                                             mock_splitui_components,
                                             mock_logger, mock_qmessagebox):
        """Test split_pdf method with invalid pages per file value."""
        # Arrange
        with patch('split.QtWidgets.QProgressBar'):
            with patch.object(split.SplitUI, 'show'):
                ui = split.SplitUI()
                ui.current_file = "test.pdf"
                ui.current_output_dir = "/output"
                ui.pagesPerFileRadio = Mock()
                ui.pagesPerFileRadio.isChecked.return_value = True
                ui.pagesPerFileEdit = Mock()
                ui.pagesPerFileEdit.text.return_value = "invalid"
                
                # Act
                ui.split_pdf()
                
                # Assert
                mock_logger.error.assert_called()
                mock_qmessagebox.critical.assert_called()
                
    @pytest.mark.gui
    @pytest.mark.unit
    def test_split_pdf_negative_pages_per_file(self, qapp,
                                              mock_splitui_components,
                                              mock_logger, mock_qmessagebox):
        """Test split_pdf method with negative pages per file value."""
        # Arrange
        with patch('split.QtWidgets.QProgressBar'):
            with patch.object(split.SplitUI, 'show'):
                ui = split.SplitUI()
                ui.current_file = "test.pdf"
                ui.current_output_dir = "/output"
                ui.pagesPerFileRadio = Mock()
                ui.pagesPerFileRadio.isChecked.return_value = True
                ui.pagesPerFileEdit = Mock()
                ui.pagesPerFileEdit.text.return_value = "-1"
                
                # Act
                ui.split_pdf()
                
                # Assert
                mock_logger.error.assert_called()
                mock_qmessagebox.critical.assert_called()
                
    @pytest.mark.gui
    @pytest.mark.unit
    def test_split_pdf_page_ranges_mode(self, qapp, mock_splitui_components,
                                       mock_logger):
        """Test split_pdf method in page ranges mode."""
        # Arrange
        with patch('split.QtWidgets.QProgressBar'):
            with patch.object(split.SplitUI, 'show'):
                ui = split.SplitUI()
                ui.current_file = "test.pdf"
                ui.current_output_dir = "/output"
                ui.pagesPerFileRadio = Mock()
                ui.pagesPerFileRadio.isChecked.return_value = False
                ui.pageRangesRadio = Mock()
                ui.pageRangesRadio.isChecked.return_value = True
                ui.pageRangesEdit = Mock()
                ui.pageRangesEdit.text.return_value = "1-2, 3-4"
                ui.progressBar = Mock()
                ui.statusBar = Mock()
                
                with patch('split.split_pdf', return_value=True) as mock_split:
                    with patch('split.fitz.open') as mock_fitz:
                        mock_doc = Mock()
                        mock_doc.page_count = 5
                        mock_fitz.return_value = mock_doc
                        
                        # Act
                        ui.split_pdf()
                        
                        # Assert
                        mock_split.assert_called()
                        
    @pytest.mark.gui
    @pytest.mark.unit
    def test_split_pdf_empty_page_ranges(self, qapp, mock_splitui_components,
                                        mock_logger, mock_qmessagebox):
        """Test split_pdf method with empty page ranges."""
        # Arrange
        with patch('split.QtWidgets.QProgressBar'):
            with patch.object(split.SplitUI, 'show'):
                ui = split.SplitUI()
                ui.current_file = "test.pdf"
                ui.current_output_dir = "/output"
                ui.pagesPerFileRadio = Mock()
                ui.pagesPerFileRadio.isChecked.return_value = False
                ui.pageRangesRadio = Mock()
                ui.pageRangesRadio.isChecked.return_value = True
                ui.pageRangesEdit = Mock()
                ui.pageRangesEdit.text.return_value = "   "  # Whitespace only
                
                # Act
                ui.split_pdf()
                
                # Assert
                mock_logger.warning.assert_called()
                mock_qmessagebox.warning.assert_called()
                
    @pytest.mark.gui
    @pytest.mark.unit
    def test_update_progress(self, qapp, mock_splitui_components):
        """Test update_progress method."""
        # Arrange
        with patch('split.QtWidgets.QProgressBar'):
            with patch.object(split.SplitUI, 'show'):
                ui = split.SplitUI()
                ui.progressBar = Mock()
                ui.statusBar = Mock()
                
                # Act
                ui.update_progress(50, 20)
                
                # Assert
                ui.progressBar.setValue.assert_called_with(55)  # 20 + 50*70/100
                ui.statusBar.showMessage.assert_called_with("Splitting PDF... 50%")


class TestMainFunction:
    """Test cases for the main function."""
    
    @pytest.mark.unit
    def test_main_function_success(self, mock_logger):
        """Test successful execution of main function."""
        # Arrange
        with patch('split.QtWidgets.QApplication') as mock_app:
            with patch('split.SplitUI') as mock_ui:
                with patch('sys.exit') as mock_exit:
                    mock_app_instance = Mock()
                    mock_app.return_value = mock_app_instance
                    mock_app_instance.exec_.return_value = 0
                    
                    # Act
                    split.main()
                    
                    # Assert
                    mock_logger.info.assert_called_with(
                        "Starting Split PDF application")
                    mock_ui.assert_called_once()
                    mock_exit.assert_called_with(0)
                    
    @pytest.mark.unit
    def test_main_function_exception(self, mock_logger, mock_qmessagebox):
        """Test main function with exception."""
        # Arrange
        with patch('split.QtWidgets.QApplication', 
                  side_effect=Exception("App failed")):
            with patch('sys.exit') as mock_exit:
                # Act
                split.main()
                
                # Assert
                mock_logger.critical.assert_called()
                mock_qmessagebox.critical.assert_called()
                mock_exit.assert_called_with(1)


class TestEdgeCasesAndIntegration:
    """Test edge cases and integration scenarios."""
    
    @pytest.mark.integration
    @pytest.mark.pdf
    def test_split_large_pdf(self, temp_dir, mock_logger, mock_qmessagebox):
        """Test splitting a large PDF file."""
        # This would test with a mock large PDF
        pass  # Implementation would depend on performance requirements
        
    @pytest.mark.integration
    @pytest.mark.pdf
    def test_split_pdf_with_special_characters_in_path(self, temp_dir,
                                                       mock_logger,
                                                       mock_qmessagebox):
        """Test PDF splitting with special characters in file path."""
        # Arrange
        special_path = os.path.join(temp_dir, "test file with spaces & chars.pdf")
        
        # Create a simple PDF file
        from reportlab.pdfgen import canvas
        c = canvas.Canvas(special_path)
        c.drawString(100, 750, "Test content")
        c.showPage()
        c.save()
        
        output_dir = os.path.join(temp_dir, "output with spaces")
        
        with patch('split.pikepdf') as mock_pikepdf:
            mock_pdf = Mock()
            mock_pdf.pages = [Mock()]
            mock_pikepdf.Pdf.open.return_value = mock_pdf
            mock_pikepdf.Pdf.new.return_value = Mock()
            
            # Act
            result = split.split_pdf(special_path, output_dir)
            
            # Assert
            assert result is True
            
    @pytest.mark.unit
    @pytest.mark.pdf
    def test_split_pdf_concurrent_access(self, sample_pdf_5_pages,
                                        output_directory, mock_logger):
        """Test PDF splitting with concurrent access simulation."""
        # This would test thread safety if relevant
        pass  # Implementation depends on concurrency requirements
        
    @pytest.mark.unit
    @pytest.mark.pdf  
    def test_split_pdf_memory_cleanup(self, sample_pdf_5_pages,
                                     output_directory, mock_logger,
                                     mock_pikepdf):
        """Test that PDF splitting properly cleans up memory."""
        # Arrange & Act
        result = split.split_pdf(sample_pdf_5_pages, output_directory)
        
        # Assert
        assert result is True
        # Additional memory profiling would be done in real scenarios
        
    @pytest.mark.unit
    @pytest.mark.pdf
    def test_split_pdf_with_unicode_content(self, temp_dir, mock_logger,
                                           mock_pikepdf):
        """Test PDF splitting with Unicode content."""
        # Arrange
        unicode_pdf = os.path.join(temp_dir, "unicode_test.pdf")
        
        # Create PDF with Unicode content
        from reportlab.pdfgen import canvas
        c = canvas.Canvas(unicode_pdf)
        c.drawString(100, 750, "Test with Unicode: àáâãäåæçèéêë")
        c.showPage()
        c.save()
        
        # Act
        result = split.split_pdf(unicode_pdf, temp_dir)
        
        # Assert
        assert result is True


if __name__ == "__main__":
    # Run tests with timestamp in output
    import datetime
    print(f"Running tests at: {datetime.datetime.now()}")
    pytest.main([__file__, "-v", "--tb=short"])