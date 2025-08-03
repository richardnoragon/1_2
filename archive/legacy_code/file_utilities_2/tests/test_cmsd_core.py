"""
Test module for CMSD core logic functionality.
"""

import unittest
import tempfile
import os
import shutil
from pathlib import Path

from file_utilities_2.core.cmsd_logic import CMSDLogic, DirectoryComparison, OperationResult


class TestCMSDLogic(unittest.TestCase):
    """Test CMSD core logic functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.cmsd = CMSDLogic()
        self.test_dir_left = tempfile.mkdtemp()
        self.test_dir_right = tempfile.mkdtemp()
        
        # Create test files in left directory
        for i in range(3):
            test_file = Path(self.test_dir_left) / f"file_{i}.txt"
            test_file.write_text(f"Content {i}")
        
        # Create test files in right directory (some overlap)
        for i in range(2, 5):
            test_file = Path(self.test_dir_right) / f"file_{i}.txt"
            test_file.write_text(f"Content {i}")
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir_left, ignore_errors=True)
        shutil.rmtree(self.test_dir_right, ignore_errors=True)
    
    def test_directory_loading(self):
        """Test directory content loading."""
        files = self.cmsd.load_directory_contents(self.test_dir_left)
        self.assertEqual(len(files), 3)
        
        # Test with non-existent directory
        files = self.cmsd.load_directory_contents("/non/existent/path")
        self.assertEqual(len(files), 0)
    
    def test_directory_comparison(self):
        """Test directory comparison functionality."""
        self.cmsd.left_directory = self.test_dir_left
        self.cmsd.right_directory = self.test_dir_right
        
        comparison = self.cmsd.compare_directories()
        
        # Check comparison results
        self.assertIsInstance(comparison, DirectoryComparison)
        self.assertEqual(len(comparison.only_left), 2)  # file_0, file_1
        self.assertEqual(len(comparison.only_right), 2)  # file_3, file_4
        self.assertEqual(len(comparison.common), 1)  # file_2
        self.assertEqual(comparison.total_left, 3)
        self.assertEqual(comparison.total_right, 3)
    
    def test_file_selection(self):
        """Test file selection functionality."""
        test_file = os.path.join(self.test_dir_left, "file_0.txt")
        
        # Test adding to selection
        self.cmsd.add_to_selection(test_file)
        selected = self.cmsd.get_selected_files()
        self.assertIn(test_file, selected)
        
        # Test removing from selection
        self.cmsd.remove_from_selection(test_file)
        selected = self.cmsd.get_selected_files()
        self.assertNotIn(test_file, selected)
        
        # Test clearing selection
        self.cmsd.add_to_selection(test_file)
        self.cmsd.clear_selection()
        selected = self.cmsd.get_selected_files()
        self.assertEqual(len(selected), 0)
    
    def test_file_copy_operation(self):
        """Test file copy operations."""
        source_file = os.path.join(self.test_dir_left, "file_0.txt")
        
        result = self.cmsd.copy_files([source_file], self.test_dir_right)
        
        self.assertIsInstance(result, OperationResult)
        self.assertTrue(result.success)
        self.assertEqual(len(result.processed_files), 1)
        self.assertEqual(len(result.failed_files), 0)
        
        # Verify file was copied
        copied_file = os.path.join(self.test_dir_right, "file_0.txt")
        self.assertTrue(os.path.exists(copied_file))
    
    def test_file_copy_error_handling(self):
        """Test file copy error handling."""
        # Test with non-existent source file
        result = self.cmsd.copy_files(["/non/existent/file.txt"], self.test_dir_right)
        
        self.assertFalse(result.success)
        self.assertEqual(len(result.processed_files), 0)
        self.assertEqual(len(result.failed_files), 1)
        
        # Test with non-existent destination directory
        source_file = os.path.join(self.test_dir_left, "file_0.txt")
        result = self.cmsd.copy_files([source_file], "/non/existent/dir")
        
        self.assertFalse(result.success)
    
    def test_file_delete_operation(self):
        """Test file delete operations."""
        test_file = os.path.join(self.test_dir_left, "file_0.txt")
        
        # Verify file exists
        self.assertTrue(os.path.exists(test_file))
        
        result = self.cmsd.delete_files([test_file])
        
        self.assertIsInstance(result, OperationResult)
        self.assertTrue(result.success)
        self.assertEqual(len(result.processed_files), 1)
        self.assertEqual(len(result.failed_files), 0)
        
        # Verify file was deleted
        self.assertFalse(os.path.exists(test_file))


if __name__ == '__main__':
    unittest.main()