import unittest
import os
from tests.test_utils import TestUtils
from catalog import CatalogGenerator  # Update this import based on actual class name

class TestCatalog(unittest.TestCase):
    def setUp(self):
        self.test_dir = TestUtils.create_temp_dir()
        self.catalog_gen = CatalogGenerator()
        
        # Create test directory structure
        self.subdir = os.path.join(self.test_dir, "subdir")
        os.makedirs(self.subdir)
        
        # Create test files
        self.test_files = [
            TestUtils.create_temp_file("content1"),
            TestUtils.create_temp_file("content2"),
        ]
        self.test_file_subdir = os.path.join(self.subdir, "subfile.txt")
        with open(self.test_file_subdir, 'w') as f:
            f.write("subcontent")

    def tearDown(self):
        TestUtils.cleanup_temp_dir(self.test_dir)
        for file in self.test_files:
            TestUtils.cleanup_temp_file(file)

    def test_scan_directory(self):
        """Test directory scanning functionality"""
        file_list = self.catalog_gen.scan_directory(self.test_dir)
        self.assertTrue(len(file_list) >= 3)  # At least 3 files
        self.assertTrue(any(f.endswith("subfile.txt") for f in file_list))

    def test_generate_html(self):
        """Test HTML catalog generation"""
        output_file = os.path.join(self.test_dir, "catalog.html")
        self.catalog_gen.generate_catalog(self.test_dir, output_file)
        
        self.assertTrue(os.path.exists(output_file))
        with open(output_file, 'r') as f:
            content = f.read()
            self.assertIn("html", content.lower())
            self.assertIn("subfile.txt", content)

    def test_file_size_calculation(self):
        """Test file size calculation in catalog"""
        sizes = self.catalog_gen.get_file_sizes(self.test_files)
        for size in sizes.values():
            self.assertGreater(size, 0)

if __name__ == '__main__':
    unittest.main()