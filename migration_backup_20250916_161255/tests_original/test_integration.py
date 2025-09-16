import unittest
import os
import time
from PyQt5.QtWidgets import QApplication
from tests.test_utils import TestUtils
from rfuhub import RFUHub
# MIGRATION UPDATE: Updated import for file finder migration to file_utilities_1
# Changed from: from file_finder import FileFinderGUI
# Changed to: from file_utilities_1 import FileFinderWindow
# Reason: FileFinderGUI has been migrated to file_utilities_1 as FileFinderWindow
from file_utilities_1 import FileFinderWindow
from en_and_decrypt import en_and_decryptGUI
from file_splitter_joiner import FileSplitJoinGUI
from rfuhub import OrganizeWindow
# MIGRATION UPDATE: Import from new file_utilities_2 package location
# Changed from: from size_analyzer import SizeAnalyzerWindow
# Changed to: from file_utilities_2.gui.size_analyzer_gui import SizeAnalyzerGUI
# Reason: size_analyzer has been migrated to file_utilities_2 package
from file_utilities_2.gui.size_analyzer_gui import SizeAnalyzerGUI

from core.error_handler import error_handler


class TestIntegration(unittest.TestCase):
    """A class that handles test integration."""
    @classmethod
    def setUpClass(cls):
        """Create the application once for all tests"""
        cls.app = TestUtils.get_test_app()

    def setUp(self):
        """setup."""
        self.test_dir = TestUtils.create_temp_dir()
        self.hub = RFUHub()
        self.create_test_environment()

    def tearDown(self):
        """teardown."""
        TestUtils.cleanup_temp_dir(self.test_dir)
        self.hub.close()

    def create_test_environment(self):
        """Create a complex test environment with various file types"""
        # Create subdirectories
        self.subdirs = {
            'docs': os.path.join(self.test_dir, "documents"),
            'media': os.path.join(self.test_dir, "media"),
            'data': os.path.join(self.test_dir, "data")
        }
        for dir_path in self.subdirs.values():
            os.makedirs(dir_path)

        # Create document files
        self.create_test_documents()
        # Create media files
        self.create_test_media()
        # Create data files
        self.create_test_data()

    def create_test_documents(self):
        """Create test document files"""
        for i in range(3):
            path = os.path.join(self.subdirs['docs'], f"doc_{i}.txt")
            with open(path, 'w') as f:
                f.write(f"Document {i} content\n" * 100)

    def create_test_media(self):
        """Create simulated media files"""
        sizes = {
            'video.mp4': 1024 * 1024 * 5,  # 5MB
            'audio.mp3': 1024 * 512,       # 512KB
            'image.jpg': 1024 * 100        # 100KB
        }
        for name, size in sizes.items():
            path = os.path.join(self.subdirs['media'], name)
            with open(path, 'wb') as f:
                f.write(os.urandom(size))

    def create_test_data(self):
        """Create test data files"""
        for i in range(2):
            path = os.path.join(self.subdirs['data'], f"data_{i}.dat")
            with open(path, 'wb') as f:
                f.write(os.urandom(1024 * 100))  # 100KB each

    def test_find_and_encrypt(self):
        """Test finding and encrypting files"""
        # Find all text files
        finder = FileFinder()
        encryptor = Encryptor()
        
        text_files = finder.find_files(
            self.test_dir,
            patterns=["*.txt"],
            recursive=True
        )
        
        # Encrypt found files
        password = "test_password123"
        encrypted_files = []
        for file_path in text_files:
            enc_path = file_path + '.encrypted'
            encryptor.encrypt_file(file_path, enc_path, password)
            encrypted_files.append(enc_path)
        
        # Verify encryption
        self.assertEqual(len(encrypted_files), len(text_files))
        for enc_file in encrypted_files:
            self.assertTrue(os.path.exists(enc_file))
            self.assertGreater(os.path.getsize(enc_file), 0)

    def test_split_and_organize(self):
        """Test splitting files and organizing the chunks"""
        # Split a large file
        splitter = FileSplitter()
        organizer = FileOrganizer()
        
        # Create a large test file
        large_file = os.path.join(self.test_dir, "large_file.dat")
        with open(large_file, 'wb') as f:
            f.write(os.urandom(1024 * 1024 * 10))  # 10MB
        
        # Split the file
        chunks = splitter.split_file(
            large_file,
            self.test_dir,
            chunk_size=1024 * 1024  # 1MB chunks
        )
        
        # Organize chunks into a dedicated directory
        chunk_dir = os.path.join(self.test_dir, "chunks")
        os.makedirs(chunk_dir)
        organizer.organize_by_extension(
            self.test_dir,
            target_dir=chunk_dir,
            file_types=[".part"]
        )
        
        # Verify organization
        self.assertTrue(all(
            os.path.exists(os.path.join(chunk_dir, os.path.basename(chunk)))
            for chunk in chunks
        ))

    def test_analyze_and_cleanup(self):
        """Test analyzing directory and cleaning up based on results"""
        analyzer = SizeAnalyzer()
        finder = FileFinder()
        
        # Analyze directory
        analysis = analyzer.analyze_directory(self.test_dir)
        
        # Find large files (>1MB)
        large_files = [
            info['path'] for info in analysis['files']
            if info['size'] > 1024 * 1024
        ]
        
        # Move large files to a separate directory
        large_dir = os.path.join(self.test_dir, "large_files")
        os.makedirs(large_dir)
        
        for file_path in large_files:
            target_path = os.path.join(
                large_dir,
                os.path.basename(file_path)
            )
            os.rename(file_path, target_path)
        
        # Verify move
        self.assertEqual(
            len(os.listdir(large_dir)),
            len(large_files)
        )

    def test_gui_operations(self):
        """Test GUI-based operations"""
        # Set working directory
        self.hub.set_working_directory(self.test_dir)
        
        # Refresh file list
        self.hub.refresh_file_list()
        
        # Verify file list population
        file_list = self.hub.get_file_list()
        self.assertGreater(len(file_list), 0)
        
        # Test file selection
        self.hub.select_files([file_list[0]])
        selected = self.hub.get_selected_files()
        self.assertEqual(len(selected), 1)
        
        # Test basic operation
        self.hub.perform_operation('analyze_size')
        
        # Verify operation results
        # (Specific verification depends on the operation implementation)
        self.assertTrue(hasattr(self.hub, 'last_operation_result'))

    def test_concurrent_operations(self):
        """Test running multiple operations concurrently"""
        # Start multiple operations
        results = []
        
        # Size analysis operation
        analyzer = SizeAnalyzer()
        analysis_result = analyzer.analyze_directory_async(
            self.test_dir,
            lambda result: results.append(('analysis', result))
        )
        
        # File finding operation
        finder = FileFinder()
        finder_result = finder.find_files_async(
            self.test_dir,
            patterns=["*.txt"],
            callback=lambda files: results.append(('find', files))
        )
        
        # Wait for completion
        while len(results) < 2:
            QApplication.processEvents()
            time.sleep(0.1)
        
        # Verify results
        self.assertEqual(len(results), 2)
        self.assertTrue(any(r[0] == 'analysis' for r in results))
        self.assertTrue(any(r[0] == 'find' for r in results))

    def test_error_recovery(self):
        """Test error recovery in integrated operations"""
        # Create a problematic file (read-only)
        readonly_file = os.path.join(self.test_dir, "readonly.txt")
        with open(readonly_file, 'w') as f:
            f.write("Read-only content")
        if os.name == 'posix':
            os.chmod(readonly_file, 0o444)
        
        # Attempt operations that should handle the error gracefully
        organizer = FileOrganizer()
        result = organizer.organize_by_extension(
            self.test_dir,
            skip_errors=True
        )
        
        # Verify other operations succeeded
        self.assertTrue(result['success'])
        self.assertIn('skipped_files', result)
        self.assertIn(readonly_file, result['skipped_files'])

if __name__ == '__main__':
    unittest.main()