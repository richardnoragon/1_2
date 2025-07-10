import unittest
import os
import shutil
from datetime import datetime
from tests.test_utils import TestUtils
from organize import FileOrganizer  # Update based on actual class name
from rename import FileRenamer     # Update based on actual class name

from core.error_handler import error_handler


class TestFileOperations(unittest.TestCase):
    def setUp(self):
        self.test_dir = TestUtils.create_temp_dir()
        self.organizer = FileOrganizer()
        self.renamer = FileRenamer()
        
        # Create test files with different extensions
        self.files = {
            'doc': os.path.join(self.test_dir, "document.doc"),
            'pdf': os.path.join(self.test_dir, "document.pdf"),
            'jpg': os.path.join(self.test_dir, "photo.jpg"),
            'mp3': os.path.join(self.test_dir, "song.mp3")
        }
        
        for file_path in self.files.values():
            with open(file_path, 'w') as f:
                f.write("test content")

    def tearDown(self):
        TestUtils.cleanup_temp_dir(self.test_dir)

    def test_organize_by_extension(self):
        """Test organizing files by extension"""
        # Organize files
        self.organizer.organize_by_extension(self.test_dir)
        
        # Check that directories were created and files moved
        for ext in ['doc', 'pdf', 'jpg', 'mp3']:
            ext_dir = os.path.join(self.test_dir, ext.upper())
            self.assertTrue(os.path.exists(ext_dir))
            file_path = self.files[ext]
            new_path = os.path.join(ext_dir, os.path.basename(file_path))
            self.assertTrue(os.path.exists(new_path))

    def test_organize_by_date(self):
        """Test organizing files by date"""
        # Organize files
        self.organizer.organize_by_date(self.test_dir)
        
        # Get current date info
        now = datetime.now()
        year_month = now.strftime("%Y-%m")
        
        # Check that date directory was created and files moved
        date_dir = os.path.join(self.test_dir, year_month)
        self.assertTrue(os.path.exists(date_dir))
        
        # All files should be in the date directory
        for file_path in self.files.values():
            new_path = os.path.join(date_dir, os.path.basename(file_path))
            self.assertTrue(os.path.exists(new_path))

    def test_rename_prefix(self):
        """Test adding prefix to filenames"""
        prefix = "TEST_"
        self.renamer.add_prefix(self.files.values(), prefix)
        
        for old_path in self.files.values():
            dir_path = os.path.dirname(old_path)
            base_name = os.path.basename(old_path)
            new_path = os.path.join(dir_path, prefix + base_name)
            self.assertTrue(os.path.exists(new_path))
            self.assertFalse(os.path.exists(old_path))

    def test_rename_pattern(self):
        """Test renaming using patterns"""
        pattern = "file_{num}"
        self.renamer.rename_pattern(self.files.values(), pattern)
        
        # Check that files were renamed according to pattern
        for i, old_path in enumerate(self.files.values(), 1):
            dir_path = os.path.dirname(old_path)
            ext = os.path.splitext(old_path)[1]
            new_name = f"file_{i}{ext}"
            new_path = os.path.join(dir_path, new_name)
            self.assertTrue(os.path.exists(new_path))
            self.assertFalse(os.path.exists(old_path))

    def test_rename_case(self):
        """Test case conversion in filenames"""
        # Test uppercase conversion
        self.renamer.to_uppercase(self.files.values())
        for old_path in self.files.values():
            upper_path = os.path.join(
                os.path.dirname(old_path),
                os.path.basename(old_path).upper()
            )
            self.assertTrue(os.path.exists(upper_path))
            self.assertFalse(os.path.exists(old_path))

    def test_rename_date(self):
        """Test adding date to filenames"""
        date_format = "%Y%m%d_"
        self.renamer.add_date(self.files.values(), date_format)
        
        today = datetime.now().strftime(date_format)
        for old_path in self.files.values():
            dir_path = os.path.dirname(old_path)
            base_name = os.path.basename(old_path)
            new_path = os.path.join(dir_path, today + base_name)
            self.assertTrue(os.path.exists(new_path))
            self.assertFalse(os.path.exists(old_path))

if __name__ == '__main__':
    unittest.main()