import os
import unittest
from tests.test_utils import TestUtils
from file_utilities_1.catalog import CatalogWindow


class TestCatalog(unittest.TestCase):
    """A class that handles test catalog."""
    def setUp(self):
        """setup."""
        self.test_dir = TestUtils.create_temp_dir()
        self.catalog_gen = CatalogWindow()
        
        # Create test directory structure
        self.subdir = os.path.join(self.test_dir, "subdir")
        os.makedirs(self.subdir)
        
        # Create test files
        self.test_files = [
            TestUtils.create_test_file(self.test_dir, "test1.txt", "content1"),
            TestUtils.create_test_file(self.test_dir, "test2.txt", "content2"),
        ]
        self.test_file_subdir = os.path.join(self.subdir, "subfile.txt")
        with open(self.test_file_subdir, 'w') as f:
            f.write("subcontent")

    def tearDown(self):
        """teardown."""
        TestUtils.cleanup_temp_dir(self.test_dir)

    def test_directory_loading(self):
        """Test directory loading functionality"""
        # Set the directory and update file list
        self.catalog_gen._current_dir = self.test_dir
        self.catalog_gen._update_file_list()
        
        # Check that files were loaded into the model
        model = self.catalog_gen._list_model
        self.assertGreater(model.rowCount(), 0)

    def test_generate_html(self):
        """Test HTML catalog generation"""
        # Set up the catalog window with test directory
        self.catalog_gen._current_dir = self.test_dir
        
        # Generate catalog
        self.catalog_gen._generate_catalog()
        
        # Check that catalog file was created
        catalog_file = os.path.join(self.test_dir, "catalog.html")
        self.assertTrue(os.path.exists(catalog_file))
        
        with open(catalog_file, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("html", content.lower())
            self.assertIn("File Catalog", content)

    def test_file_size_formatting(self):
        """Test file size formatting functionality"""
        # Test the _format_size method
        self.assertEqual(self.catalog_gen._format_size(1024), "1.0 KB")
        self.assertEqual(self.catalog_gen._format_size(1048576), "1.0 MB")
        self.assertEqual(self.catalog_gen._format_size(500), "500.0 B")


if __name__ == '__main__':
    unittest.main()