import os
import tempfile
import hashlib
from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, patch
from queue import Queue
import threading
from PyQt5.QtWidgets import QApplication
from core.error_handler import error_handler
from find_duplicate_files import (
    DuplicateFinderApp,
    get_file_id,
    get_file_md5,
    worker,
    process_file
)

class TestDuplicateFinder(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication([])

    def setUp(self):
        self.finder = DuplicateFinderApp()
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        for root, dirs, files in os.walk(self.test_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(self.test_dir)

    @classmethod
    def tearDownClass(cls):
        cls.app.quit()

    def create_test_files(self, structure):
        """Helper to create test files with specified content"""
        created_files = []
        for filename, content in structure.items():
            filepath = os.path.join(self.test_dir, filename)
            with open(filepath, 'wb') as f:
                f.write(content)
            created_files.append(Path(filepath))
        return created_files

    def test_get_file_id(self):
        test_file = Path(self.test_dir) / "test.txt"
        with open(test_file, 'w') as f:
            f.write("test content")
        
        digest = "test_digest"
        file_id = get_file_id(test_file, digest)
        
        self.assertEqual(file_id, "test.txt|test_digest")

    def test_get_file_md5_small_file(self):
        content = b"test content"
        test_file = Path(self.test_dir) / "small.txt"
        with open(test_file, 'wb') as f:
            f.write(content)
            
        md5 = hashlib.md5(content).hexdigest()
        self.assertEqual(get_file_md5(test_file, len(content)), md5)

    def test_get_file_md5_large_file(self):
        # Create file larger than CRITIC_SIZE
        content = b"x" * (1024 * 1024)  # 1MB
        test_file = Path(self.test_dir) / "large.txt"
        with open(test_file, 'wb') as f:
            f.write(content)
            
        md5 = hashlib.md5(content).hexdigest()
        self.assertEqual(get_file_md5(test_file, len(content)), md5)

    def test_worker_processing(self):
        # Create test files
        files = self.create_test_files({
            "file1.txt": b"content1",
            "file2.txt": b"content2"
        })
        
        # Setup worker components
        task_queue = Queue()
        for file in files:
            task_queue.put(file)
            
        processed_files = []
        print_lock = threading.Lock()
        abort = threading.Event()
        
        # Run worker
        worker(task_queue, print_lock, processed_files, abort)
        
        # Verify results
        self.assertEqual(len(processed_files), 2)
        self.assertEqual(processed_files[0][0], files[0])
        self.assertEqual(processed_files[1][0], files[1])

    def test_process_file(self):
        # Create test file
        content = b"test content"
        test_file = Path(self.test_dir) / "test.txt"
        with open(test_file, 'wb') as f:
            f.write(content)
            
        processed_files = []
        print_lock = threading.Lock()
        
        process_file(test_file, processed_files, print_lock)
        
        self.assertEqual(len(processed_files), 1)
        self.assertEqual(processed_files[0][0], test_file)
        self.assertEqual(
            processed_files[0][1], 
            hashlib.md5(content).hexdigest()
        )

    @patch('PyQt5.QtWidgets.QFileDialog.getExistingDirectory')
    def test_browse_folder(self, mock_dialog):
        test_path = "/test/path"
        mock_dialog.return_value = test_path
        
        self.finder.browse_folder()
        self.assertEqual(
            self.finder.central_widget.lineEditFolder.text(), 
            test_path
        )

    def test_find_duplicates_validation(self):
        # Test empty folder
        self.finder.central_widget.lineEditFolder.setText("")
        self.finder.central_widget.lineEditFile.setText("results.txt")
        
        with patch('PyQt5.QtWidgets.QMessageBox.warning') as mock_warning:
            self.finder.find_duplicates()
            mock_warning.assert_called_once()
        
        # Test empty filename
        self.finder.central_widget.lineEditFolder.setText("/test/path")
        self.finder.central_widget.lineEditFile.setText("")
        
        with patch('PyQt5.QtWidgets.QMessageBox.warning') as mock_warning:
            self.finder.find_duplicates()
            mock_warning.assert_called_once()

    def test_duplicate_detection(self):
        # Create duplicate files
        content1 = b"content1"
        content2 = b"content1"  # Duplicate content
        content3 = b"content3"  # Unique content
        
        files = self.create_test_files({
            "file1.txt": content1,
            "file2.txt": content2,
            "file3.txt": content3
        })
        
        self.finder.central_widget.lineEditFolder.setText(self.test_dir)
        self.finder.central_widget.lineEditFile.setText("results.txt")
        
        # Run duplicate search
        self.finder.find_duplicates()
        
        # Verify results
        self.assertEqual(len(self.finder.duplicate_groups), 1)  # One group of duplicates
        for file_id, group in self.finder.duplicate_groups.items():
            self.assertEqual(len(group), 2)  # Two files in the group
