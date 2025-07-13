import unittest
import os
import unittest
from tests.test_utils import TestUtils
from empty_folders import EmptyFolderLogic, EmptyFolderCleaner

from core.error_handler import error_handler


class TestEmptyFolderCleaner(unittest.TestCase):
    """Test suite for the EmptyFolderCleaner class.
    
    Tests the functionality for:
    - Finding empty folders recursively
    - Cleaning up empty folders
    - Handling hidden files
    - Applying ignore patterns
    - Dry run operations
    - Age-based filtering
    - Error handling
    """
    
    def setUp(self):
        """Set up test environment before each test.
        
        Creates:
        - A temporary test directory
        - An EmptyFolderCleaner instance
        - A test directory structure with various folder types
        """
        self.test_dir = TestUtils.create_temp_dir()
        self.cleaner = EmptyFolderCleaner()
        
        # Create test directory structure
        self.create_test_structure()

    def tearDown(self):
        """Clean up test environment after each test.
        
        Removes the temporary test directory and all its contents.
        """
        TestUtils.cleanup_temp_dir(self.test_dir)

    def create_test_structure(self):
        """Create a test directory structure with empty and non-empty folders"""
        # Create empty folders
        self.empty_dirs = [
            os.path.join(self.test_dir, "empty1"),
            os.path.join(self.test_dir, "empty2"),
            os.path.join(self.test_dir, "parent", "empty3"),
            os.path.join(self.test_dir, "parent", "child", "empty4")
        ]
        for dir_path in self.empty_dirs:
            os.makedirs(dir_path)
        
        # Create non-empty folders
        self.nonempty_dir = os.path.join(self.test_dir, "nonempty")
        os.makedirs(self.nonempty_dir)
        with open(os.path.join(self.nonempty_dir, "file.txt"), 'w') as f:
            f.write("Content")
        
        # Create folder with hidden files
        self.hidden_dir = os.path.join(self.test_dir, "hidden")
        os.makedirs(self.hidden_dir)
        with open(os.path.join(self.hidden_dir, ".hidden"), 'w') as f:
            f.write("Hidden content")

    def test_find_empty_folders(self):
        """Test finding empty folders"""
        empty_folders = self.cleaner.find_empty_folders(self.test_dir)
        
        # Verify all empty folders were found
        for empty_dir in self.empty_dirs:
            self.assertIn(empty_dir, empty_folders)
        
        # Verify non-empty folders were not included
        self.assertNotIn(self.nonempty_dir, empty_folders)

    def test_recursive_empty_detection(self):
        """Test detection of recursively empty folders"""
        # Create a chain of empty folders
        chain_root = os.path.join(self.test_dir, "chain")
        chain_folders = [chain_root]
        current = chain_root
        
        for i in range(3):
            current = os.path.join(current, f"subfolder_{i}")
            chain_folders.append(current)
            os.makedirs(current)
        
        # Find empty folders with recursive check
        empty_folders = self.cleaner.find_empty_folders(
            self.test_dir,
            recursive=True
        )
        
        # Verify all chain folders were found
        for folder in chain_folders:
            self.assertIn(folder, empty_folders)

    def test_cleanup_empty_folders(self):
        """Test cleaning up empty folders"""
        # Clean up empty folders
        removed = self.cleaner.cleanup_empty_folders(self.test_dir)
        
        # Verify empty folders were removed
        for empty_dir in self.empty_dirs:
            self.assertFalse(os.path.exists(empty_dir))
            self.assertIn(empty_dir, removed)
        
        # Verify non-empty folders were preserved
        self.assertTrue(os.path.exists(self.nonempty_dir))
        self.assertNotIn(self.nonempty_dir, removed)

    def test_ignore_patterns(self):
        """Test ignoring specific folders"""
        # Create an empty folder that should be ignored
        ignore_dir = os.path.join(self.test_dir, "ignore_me")
        os.makedirs(ignore_dir)
        
        # Find empty folders with ignore pattern
        empty_folders = self.cleaner.find_empty_folders(
            self.test_dir,
            ignore_patterns=["ignore_*"]
        )
        
        # Verify ignored folder was not included
        self.assertNotIn(ignore_dir, empty_folders)

    def test_consider_hidden_files(self):
        """Test handling of hidden files"""
        # Find empty folders with different hidden file settings
        include_hidden = self.cleaner.find_empty_folders(
            self.test_dir,
            include_hidden=True
        )
        exclude_hidden = self.cleaner.find_empty_folders(
            self.test_dir,
            include_hidden=False
        )
        
        # Verify behavior with hidden files
        self.assertNotIn(self.hidden_dir, include_hidden)
        self.assertIn(self.hidden_dir, exclude_hidden)

    def test_dry_run(self):
        """Test dry run functionality"""
        # Perform dry run
        to_be_removed = self.cleaner.cleanup_empty_folders(
            self.test_dir,
            dry_run=True
        )
        
        # Verify folders were identified but not removed
        self.assertTrue(len(to_be_removed) > 0)
        for empty_dir in self.empty_dirs:
            self.assertTrue(os.path.exists(empty_dir))
            self.assertIn(empty_dir, to_be_removed)

    def test_min_age(self):
        """Test minimum age filter"""
        import time
        
        # Create a new empty folder
        new_empty = os.path.join(self.test_dir, "new_empty")
        os.makedirs(new_empty)
        
        # Find empty folders with age restriction
        empty_folders = self.cleaner.find_empty_folders(
            self.test_dir,
            min_age_hours=1
        )
        
        # Verify new folder was not included
        self.assertNotIn(new_empty, empty_folders)

    def test_error_handling(self):
        """Test error handling"""
        # Test non-existent directory
        with self.assertRaises(FileNotFoundError):
            self.cleaner.find_empty_folders("nonexistent")
        
        # Test permission error
        if os.name == 'posix':
            restricted_dir = os.path.join(self.test_dir, "restricted")
            os.makedirs(restricted_dir)
            os.chmod(restricted_dir, 0o000)
            
            with self.assertRaises(PermissionError):
                self.cleaner.cleanup_empty_folders(restricted_dir)

if __name__ == '__main__':
    unittest.main()