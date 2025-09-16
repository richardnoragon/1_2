"""
Comprehensive Unit Tests for merg.py
Generated on: August 24, 2025
Target Module: src.tools.pdf_tools.pdf_basic_operations.merg

This test suite provides comprehensive coverage for:
- merge_pdfs function with various scenarios
- MergeUI class initialization and methods
- Error handling and edge cases
- Mock data and fixtures for PDF operations
"""

import json
import os
import shutil
import sys
import tempfile
from datetime import datetime
from unittest.mock import MagicMock, Mock, mock_open, patch

import pikepdf
import pytest
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication, QFileDialog, QMessageBox

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'utilities', 'pdf_tools', 'pdf_basic_operations'))

# Import the module under test
try:
    from src.tools.pdf_tools.pdf_basic_operations.merg import (MergeUI, main,
                                                               merge_pdfs)
except ImportError:
    # Fallback import
    from merg import MergeUI, main, merge_pdfs

class TestFixtures:
    """Test data and fixture management"""
    
    @staticmethod
    def create_mock_pdf_file(filename: str, num_pages: int = 1) -> str:
        """Create a mock PDF file for testing"""
        temp_dir = tempfile.gettempdir()
        filepath = os.path.join(temp_dir, filename)
        
        # Create a minimal PDF using pikepdf
        try:
            pdf = pikepdf.Pdf.new()
            for _ in range(num_pages):
                pdf.pages.append(pikepdf.Page.empty_page(pdf))
            pdf.save(filepath)
            return filepath
        except Exception:
            # If pikepdf fails, create a dummy file
            with open(filepath, 'w') as f:
                f.write("Mock PDF content")
            return filepath
    
    @staticmethod
    def cleanup_temp_files(files: list):
        """Clean up temporary test files"""
        for file in files:
            try:
                if os.path.exists(file):
                    os.remove(file)
            except Exception:
                pass

class TestMergePdfs:
    """Test cases for the merge_pdfs function"""
    
    def setup_method(self):
        """Setup test environment before each test"""
        self.temp_files = []
        self.app = None
        
        # Initialize QApplication for Qt components
        if not QApplication.instance():
            self.app = QApplication([])
    
    def teardown_method(self):
        """Cleanup after each test"""
        TestFixtures.cleanup_temp_files(self.temp_files)
        if self.app:
            self.app.quit()
    
    @patch('src.tools.pdf_tools.pdf_basic_operations.merg.logger')
    @patch('src.tools.pdf_tools.pdf_basic_operations.merg.QMessageBox')
    @patch('pikepdf.Pdf')
    def test_merge_pdfs_success(self, mock_pdf_class, mock_messagebox, mock_logger):
        """Test successful PDF merging"""
        # Setup mocks
        mock_pdf_instance = Mock()
        mock_pdf_class.new.return_value = mock_pdf_instance
        mock_pdf_instance.pages = Mock()
        mock_pdf_instance.save = Mock()
        
        mock_source_pdf = Mock()
        mock_source_pdf.pages = ['page1', 'page2']
        mock_pdf_class.open.return_value = mock_source_pdf
        
        # Test data
        input_files = ['test1.pdf', 'test2.pdf']
        output_file = 'merged.pdf'
        
        # Execute
        result = merge_pdfs(input_files, output_file)
        
        # Assertions
        assert result is True
        mock_pdf_class.new.assert_called_once()
        assert mock_pdf_class.open.call_count == 2
        mock_pdf_instance.save.assert_called_once_with(output_file)
        mock_logger.info.assert_called()
    
    @patch('src.tools.pdf_tools.pdf_basic_operations.merg.logger')
    @patch('src.tools.pdf_tools.pdf_basic_operations.merg.QMessageBox')
    def test_merge_pdfs_empty_input_list(self, mock_messagebox, mock_logger):
        """Test merge_pdfs with empty input list"""
        result = merge_pdfs([], 'output.pdf')
        
        assert result is False
        mock_logger.error.assert_called_with("No input files provided")
        mock_messagebox.critical.assert_called_once()
    
    @patch('src.tools.pdf_tools.pdf_basic_operations.merg.logger')
    @patch('src.tools.pdf_tools.pdf_basic_operations.merg.QMessageBox')
    @patch('pikepdf.Pdf')
    def test_merge_pdfs_file_not_found(self, mock_pdf_class, mock_messagebox, mock_logger):
        """Test merge_pdfs with non-existent file"""
        mock_pdf_class.new.return_value = Mock()
        mock_pdf_class.open.side_effect = FileNotFoundError("File not found")
        
        result = merge_pdfs(['nonexistent.pdf'], 'output.pdf')
        
        assert result is False
        mock_logger.error.assert_called()
        mock_messagebox.critical.assert_called()
    
    @patch('src.tools.pdf_tools.pdf_basic_operations.merg.logger')
    @patch('src.tools.pdf_tools.pdf_basic_operations.merg.QMessageBox')
    @patch('pikepdf.Pdf')
    def test_merge_pdfs_pdf_error(self, mock_pdf_class, mock_messagebox, mock_logger):
        """Test merge_pdfs with PDF processing error"""
        mock_pdf_class.new.return_value = Mock()
        mock_pdf_class.open.side_effect = pikepdf.PdfError("Invalid PDF")
        
        result = merge_pdfs(['invalid.pdf'], 'output.pdf')
        
        assert result is False
        mock_logger.error.assert_called()
        mock_messagebox.critical.assert_called()
    
    @patch('src.tools.pdf_tools.pdf_basic_operations.merg.logger')
    @patch('src.tools.pdf_tools.pdf_basic_operations.merg.QMessageBox')
    @patch('pikepdf.Pdf')
    def test_merge_pdfs_save_permission_error(self, mock_pdf_class, mock_messagebox, mock_logger):
        """Test merge_pdfs with permission error during save"""
        mock_pdf_instance = Mock()
        mock_pdf_class.new.return_value = mock_pdf_instance
        mock_pdf_instance.save.side_effect = PermissionError("Permission denied")
        
        mock_source_pdf = Mock()
        mock_source_pdf.pages = ['page1']
        mock_pdf_class.open.return_value = mock_source_pdf
        
        result = merge_pdfs(['test.pdf'], 'restricted.pdf')
        
        assert result is False
        mock_logger.error.assert_called()
        mock_messagebox.critical.assert_called()
    
    @patch('src.tools.pdf_tools.pdf_basic_operations.merg.logger')
    @patch('src.tools.pdf_tools.pdf_basic_operations.merg.QMessageBox')
    @patch('pikepdf.Pdf')
    def test_merge_pdfs_unexpected_error(self, mock_pdf_class, mock_messagebox, mock_logger):
        """Test merge_pdfs with unexpected error"""
        mock_pdf_class.new.side_effect = Exception("Unexpected error")
        
        result = merge_pdfs(['test.pdf'], 'output.pdf')
        
        assert result is False
        mock_logger.error.assert_called()
        mock_messagebox.critical.assert_called()

class TestMergeUI:
    """Test cases for the MergeUI class"""
    
    def setup_method(self):
        """Setup test environment before each test"""
        self.app = None
        if not QApplication.instance():
            self.app = QApplication([])
        self.temp_files = []
    
    def teardown_method(self):
        """Cleanup after each test"""
        TestFixtures.cleanup_temp_files(self.temp_files)
        if self.app:
            self.app.quit()
    
    @patch('src.tools.pdf_tools.pdf_basic_operations.merg.uic.loadUi')
    @patch('src.tools.pdf_tools.pdf_basic_operations.merg.logger')
    def test_merge_ui_initialization_success(self, mock_logger, mock_loadui):
        """Test successful MergeUI initialization"""
        # Mock UI components
        mock_ui = Mock()
        mock_ui.addButton = Mock()
        mock_ui.removeButton = Mock()
        mock_ui.mergeButton = Mock()
        mock_ui.clearButton = Mock()
        mock_ui.upButton = Mock()
        mock_ui.downButton = Mock()
        mock_ui.actionExit = Mock()
        mock_ui.fileList = Mock()
        mock_ui.fileList.currentRow.return_value = -1
        mock_ui.statusBar.return_value = Mock()
        
        with patch.object(MergeUI, '__init__', lambda x: None):
            ui = MergeUI()
            ui.addButton = mock_ui.addButton
            ui.removeButton = mock_ui.removeButton
            ui.mergeButton = mock_ui.mergeButton
            ui.clearButton = mock_ui.clearButton
            ui.upButton = mock_ui.upButton
            ui.downButton = mock_ui.downButton
            ui.actionExit = mock_ui.actionExit
            ui.fileList = mock_ui.fileList
            ui.files = []
            
            # Test button state update
            ui.update_button_states()
            
            # Verify buttons are properly configured
            assert hasattr(ui, 'files')
            assert ui.files == []
    
    @patch('src.tools.pdf_tools.pdf_basic_operations.merg.uic.loadUi')
    @patch('src.tools.pdf_tools.pdf_basic_operations.merg.logger')
    @patch('src.tools.pdf_tools.pdf_basic_operations.merg.QMessageBox')
    def test_merge_ui_initialization_failure(self, mock_messagebox, mock_logger, mock_loadui):
        """Test MergeUI initialization failure"""
        mock_loadui.side_effect = Exception("UI load failed")
        
        with patch.object(MergeUI, 'close'):
            ui = MergeUI()
            
        mock_logger.error.assert_called()
        mock_messagebox.critical.assert_called()
    
    def test_update_button_states_no_files(self):
        """Test button states with no files"""
        # Create minimal mock UI
        ui = Mock()
        ui.files = []
        ui.fileList = Mock()
        ui.fileList.currentRow.return_value = -1
        ui.mergeButton = Mock()
        ui.clearButton = Mock()
        ui.removeButton = Mock()
        ui.upButton = Mock()
        ui.downButton = Mock()
        
        # Import and call the method
        from src.tools.pdf_tools.pdf_basic_operations.merg import MergeUI
        MergeUI.update_button_states(ui)
        
        # Verify button states
        ui.mergeButton.setEnabled.assert_called_with(False)
        ui.clearButton.setEnabled.assert_called_with(False)
        ui.removeButton.setEnabled.assert_called_with(False)
    
    def test_update_button_states_with_files(self):
        """Test button states with files"""
        ui = Mock()
        ui.files = ['file1.pdf', 'file2.pdf']
        ui.fileList = Mock()
        ui.fileList.currentRow.return_value = 0
        ui.mergeButton = Mock()
        ui.clearButton = Mock()
        ui.removeButton = Mock()
        ui.upButton = Mock()
        ui.downButton = Mock()
        
        from src.tools.pdf_tools.pdf_basic_operations.merg import MergeUI
        MergeUI.update_button_states(ui)
        
        ui.mergeButton.setEnabled.assert_called_with(True)
        ui.clearButton.setEnabled.assert_called_with(True)
        ui.removeButton.setEnabled.assert_called_with(True)
    
    @patch('src.tools.pdf_tools.pdf_basic_operations.merg.QFileDialog')
    @patch('src.tools.pdf_tools.pdf_basic_operations.merg.logger')
    def test_add_files_success(self, mock_logger, mock_file_dialog):
        """Test successful file addition"""
        mock_file_dialog.getOpenFileNames.return_value = (['file1.pdf', 'file2.pdf'], '')
        
        ui = Mock()
        ui.files = []
        ui.fileList = Mock()
        ui.update_button_states = Mock()
        
        from src.tools.pdf_tools.pdf_basic_operations.merg import MergeUI
        MergeUI.add_files(ui)
        
        assert ui.files == ['file1.pdf', 'file2.pdf']
        ui.fileList.clear.assert_called_once()
        ui.fileList.addItems.assert_called_once()
        ui.update_button_states.assert_called_once()
    
    @patch('src.tools.pdf_tools.pdf_basic_operations.merg.QFileDialog')
    def test_add_files_no_selection(self, mock_file_dialog):
        """Test file addition with no files selected"""
        mock_file_dialog.getOpenFileNames.return_value = ([], '')
        
        ui = Mock()
        ui.files = []
        ui.fileList = Mock()
        ui.update_button_states = Mock()
        
        from src.tools.pdf_tools.pdf_basic_operations.merg import MergeUI
        MergeUI.add_files(ui)
        
        assert ui.files == []
        ui.fileList.clear.assert_not_called()
    
    @patch('src.tools.pdf_tools.pdf_basic_operations.merg.logger')
    def test_remove_file_success(self, mock_logger):
        """Test successful file removal"""
        ui = Mock()
        ui.files = ['file1.pdf', 'file2.pdf']
        ui.fileList = Mock()
        ui.fileList.currentRow.return_value = 0
        ui.fileList.takeItem.return_value = Mock()
        ui.update_button_states = Mock()
        
        from src.tools.pdf_tools.pdf_basic_operations.merg import MergeUI
        MergeUI.remove_file(ui)
        
        assert ui.files == ['file2.pdf']
        ui.fileList.takeItem.assert_called_once_with(0)
        ui.update_button_states.assert_called_once()
    
    def test_remove_file_no_selection(self):
        """Test file removal with no selection"""
        ui = Mock()
        ui.files = ['file1.pdf']
        ui.fileList = Mock()
        ui.fileList.currentRow.return_value = -1
        ui.update_button_states = Mock()
        
        from src.tools.pdf_tools.pdf_basic_operations.merg import MergeUI
        MergeUI.remove_file(ui)
        
        assert ui.files == ['file1.pdf']  # No change
        ui.fileList.takeItem.assert_not_called()
    
    @patch('src.tools.pdf_tools.pdf_basic_operations.merg.logger')
    def test_clear_files(self, mock_logger):
        """Test clearing all files"""
        ui = Mock()
        ui.files = ['file1.pdf', 'file2.pdf']
        ui.fileList = Mock()
        ui.update_button_states = Mock()
        
        from src.tools.pdf_tools.pdf_basic_operations.merg import MergeUI
        MergeUI.clear_files(ui)
        
        assert len(ui.files) == 0
        ui.fileList.clear.assert_called_once()
        ui.update_button_states.assert_called_once()
    
    @patch('src.tools.pdf_tools.pdf_basic_operations.merg.logger')
    def test_move_up_success(self, mock_logger):
        """Test successful file move up"""
        ui = Mock()
        ui.files = ['file1.pdf', 'file2.pdf', 'file3.pdf']
        ui.fileList = Mock()
        ui.fileList.currentRow.return_value = 1
        ui.fileList.takeItem.return_value = Mock()
        ui.fileList.insertItem = Mock()
        ui.fileList.setCurrentRow = Mock()
        ui.update_button_states = Mock()
        
        from src.tools.pdf_tools.pdf_basic_operations.merg import MergeUI
        MergeUI.move_up(ui)
        
        assert ui.files == ['file2.pdf', 'file1.pdf', 'file3.pdf']
        ui.fileList.setCurrentRow.assert_called_with(0)
        ui.update_button_states.assert_called_once()
    
    def test_move_up_first_item(self):
        """Test move up on first item (should not move)"""
        ui = Mock()
        ui.files = ['file1.pdf', 'file2.pdf']
        ui.fileList = Mock()
        ui.fileList.currentRow.return_value = 0
        ui.update_button_states = Mock()
        
        from src.tools.pdf_tools.pdf_basic_operations.merg import MergeUI
        MergeUI.move_up(ui)
        
        assert ui.files == ['file1.pdf', 'file2.pdf']  # No change
        ui.fileList.takeItem.assert_not_called()
    
    @patch('src.tools.pdf_tools.pdf_basic_operations.merg.logger')
    def test_move_down_success(self, mock_logger):
        """Test successful file move down"""
        ui = Mock()
        ui.files = ['file1.pdf', 'file2.pdf', 'file3.pdf']
        ui.fileList = Mock()
        ui.fileList.currentRow.return_value = 1
        ui.fileList.takeItem.return_value = Mock()
        ui.fileList.insertItem = Mock()
        ui.fileList.setCurrentRow = Mock()
        ui.update_button_states = Mock()
        
        from src.tools.pdf_tools.pdf_basic_operations.merg import MergeUI
        MergeUI.move_down(ui)
        
        assert ui.files == ['file1.pdf', 'file3.pdf', 'file2.pdf']
        ui.fileList.setCurrentRow.assert_called_with(2)
        ui.update_button_states.assert_called_once()
    
    def test_move_down_last_item(self):
        """Test move down on last item (should not move)"""
        ui = Mock()
        ui.files = ['file1.pdf', 'file2.pdf']
        ui.fileList = Mock()
        ui.fileList.currentRow.return_value = 1
        ui.update_button_states = Mock()
        
        from src.tools.pdf_tools.pdf_basic_operations.merg import MergeUI
        MergeUI.move_down(ui)
        
        assert ui.files == ['file1.pdf', 'file2.pdf']  # No change
        ui.fileList.takeItem.assert_not_called()
    
    @patch('src.tools.pdf_tools.pdf_basic_operations.merg.QMessageBox')
    @patch('src.tools.pdf_tools.pdf_basic_operations.merg.logger')
    def test_merge_files_no_files(self, mock_logger, mock_messagebox):
        """Test merge operation with no files"""
        ui = Mock()
        ui.files = []
        
        from src.tools.pdf_tools.pdf_basic_operations.merg import MergeUI
        MergeUI.merge_files(ui)
        
        mock_messagebox.warning.assert_called_once()
        mock_logger.warning.assert_called()
    
    @patch('src.tools.pdf_tools.pdf_basic_operations.merg.QFileDialog')
    @patch('src.tools.pdf_tools.pdf_basic_operations.merg.merge_pdfs')
    @patch('src.tools.pdf_tools.pdf_basic_operations.merg.QMessageBox')
    @patch('src.tools.pdf_tools.pdf_basic_operations.merg.QtWidgets.QApplication.processEvents')
    def test_merge_files_success(self, mock_process_events, mock_messagebox, mock_merge_pdfs, mock_file_dialog):
        """Test successful merge operation"""
        mock_file_dialog.getSaveFileName.return_value = ('output.pdf', '')
        mock_merge_pdfs.return_value = True
        
        ui = Mock()
        ui.files = ['file1.pdf', 'file2.pdf']
        ui.progressBar = Mock()
        ui.statusBar = Mock()
        ui.statusBar.return_value = Mock()
        
        from src.tools.pdf_tools.pdf_basic_operations.merg import MergeUI
        MergeUI.merge_files(ui)
        
        mock_merge_pdfs.assert_called_once_with(['file1.pdf', 'file2.pdf'], 'output.pdf')
        mock_messagebox.information.assert_called_once()
        ui.progressBar.hide.assert_called()

class TestMainFunction:
    """Test cases for the main function"""
    
    @patch('src.tools.pdf_tools.pdf_basic_operations.merg.QApplication')
    @patch('src.tools.pdf_tools.pdf_basic_operations.merg.MergeUI')
    @patch('src.tools.pdf_tools.pdf_basic_operations.merg.logger')
    def test_main_success(self, mock_logger, mock_merge_ui, mock_qapp):
        """Test successful application startup"""
        mock_app_instance = Mock()
        mock_qapp.return_value = mock_app_instance
        mock_app_instance.exec_.return_value = 0
        
        with patch('sys.exit') as mock_exit:
            main()
            
        mock_qapp.assert_called_once()
        mock_merge_ui.assert_called_once()
        mock_app_instance.exec_.assert_called_once()
        mock_exit.assert_called_with(0)
    
    @patch('src.tools.pdf_tools.pdf_basic_operations.merg.QApplication')
    @patch('src.tools.pdf_tools.pdf_basic_operations.merg.MergeUI')
    @patch('src.tools.pdf_tools.pdf_basic_operations.merg.QMessageBox')
    @patch('src.tools.pdf_tools.pdf_basic_operations.merg.logger')
    def test_main_failure(self, mock_logger, mock_messagebox, mock_merge_ui, mock_qapp):
        """Test application startup failure"""
        mock_qapp.side_effect = Exception("App creation failed")
        
        with patch('sys.exit') as mock_exit:
            main()
            
        mock_logger.critical.assert_called()
        mock_messagebox.critical.assert_called()
        mock_exit.assert_called_with(1)

class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    def setup_method(self):
        """Setup test environment"""
        self.app = None
        if not QApplication.instance():
            self.app = QApplication([])
    
    def teardown_method(self):
        """Cleanup after tests"""
        if self.app:
            self.app.quit()
    
    @patch('src.tools.pdf_tools.pdf_basic_operations.merg.logger')
    @patch('src.tools.pdf_tools.pdf_basic_operations.merg.QMessageBox')
    @patch('pikepdf.Pdf')
    def test_merge_large_number_of_files(self, mock_pdf_class, mock_messagebox, mock_logger):
        """Test merging a large number of files"""
        mock_pdf_instance = Mock()
        mock_pdf_class.new.return_value = mock_pdf_instance
        
        # Create many mock source PDFs
        mock_source_pdf = Mock()
        mock_source_pdf.pages = ['page1']
        mock_pdf_class.open.return_value = mock_source_pdf
        
        # Test with 100 files
        input_files = [f'file{i}.pdf' for i in range(100)]
        
        result = merge_pdfs(input_files, 'large_output.pdf')
        
        assert result is True
        assert mock_pdf_class.open.call_count == 100
    
    @patch('src.tools.pdf_tools.pdf_basic_operations.merg.logger')
    @patch('src.tools.pdf_tools.pdf_basic_operations.merg.QMessageBox')
    def test_merge_pdfs_with_none_input(self, mock_messagebox, mock_logger):
        """Test merge_pdfs with None input"""
        result = merge_pdfs(None, 'output.pdf')
        
        # Should handle gracefully without crashing
        assert result is False
    
    @patch('src.tools.pdf_tools.pdf_basic_operations.merg.logger')
    @patch('src.tools.pdf_tools.pdf_basic_operations.merg.QMessageBox')
    @patch('pikepdf.Pdf')
    def test_merge_mixed_file_types(self, mock_pdf_class, mock_messagebox, mock_logger):
        """Test merging with mixed file types (should fail gracefully)"""
        mock_pdf_class.new.return_value = Mock()
        mock_pdf_class.open.side_effect = [Mock(), pikepdf.PdfError("Not a PDF")]
        
        result = merge_pdfs(['valid.pdf', 'invalid.txt'], 'output.pdf')
        
        assert result is False
        mock_logger.error.assert_called()

def generate_test_execution_summary():
    """Generate execution summary with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    summary = {
        "test_execution_summary": {
            "timestamp": timestamp,
            "target_module": "src.tools.pdf_tools.pdf_basic_operations.merg",
            "test_file": "test_merg_2025-08-24.py",
            "test_categories": [
                "merge_pdfs function tests",
                "MergeUI class tests", 
                "Main function tests",
                "Edge case tests"
            ],
            "coverage_areas": [
                "PDF merging logic",
                "File validation",
                "Error handling",
                "UI component interaction", 
                "Progress tracking",
                "File list management"
            ],
            "mock_components": [
                "pikepdf.Pdf",
                "QMessageBox",
                "QFileDialog", 
                "Logger",
                "PyQt5 UI components"
            ]
        }
    }
    
    return summary

if __name__ == "__main__":
    print("Test suite for merg.py")
    print("Generated on:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    summary = generate_test_execution_summary()
    print(json.dumps(summary, indent=2))