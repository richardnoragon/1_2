import os
import tempfile
import shutil
from unittest import TestCase
from unittest.mock import MagicMock, patch
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from tree_map import DiskScanLogic, TreeMapWindow

from core.error_handler import error_handler


class TestDiskScanLogic(TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.scanner = DiskScanLogic()
        
    def tearDown(self):
        shutil.rmtree(self.test_dir)
        
    def create_test_files(self, structure):
        """Helper to create a test directory structure.
        structure is a dict where keys are filenames and values are sizes/subdirs"""
        for name, size in structure.items():
            path = os.path.join(self.test_dir, name)
            if isinstance(size, dict):
                os.makedirs(path)
                for subname, subsize in size.items():
                    with open(os.path.join(path, subname), 'wb') as f:
                        f.write(b'0' * subsize)
            else:
                with open(path, 'wb') as f:
                    f.write(b'0' * size)

    def test_basic_scan(self):
        # Create test files
        test_files = {
            'small.txt': 100,
            'medium.txt': 1000,
            'large.txt': 10000
        }
        self.create_test_files(test_files)
        
        # Mock signals
        progress_signal = MagicMock()
        complete_signal = MagicMock()
        self.scanner.progress_updated.connect(progress_signal)
        self.scanner.scan_complete.connect(complete_signal)
        
        # Run scan
        self.scanner.start_scan(self.test_dir)
        
        # Verify results
        complete_signal.assert_called_once()
        scan_data = complete_signal.call_args[0][0]
        self.assertEqual(len(scan_data['items']), 3)
        self.assertEqual(
            sum(item['size'] for item in scan_data['items']), 
            sum(test_files.values())
        )

    def test_nested_directory_scan(self):
        # Create nested directory structure
        structure = {
            'dir1': {
                'file1.txt': 1000,
                'file2.txt': 2000
            },
            'dir2': {
                'file3.txt': 3000
            },
            'file4.txt': 4000
        }
        self.create_test_files(structure)
        
        complete_signal = MagicMock()
        self.scanner.scan_complete.connect(complete_signal)
        
        self.scanner.start_scan(self.test_dir)
        
        scan_data = complete_signal.call_args[0][0]
        total_size = sum([1000, 2000, 3000, 4000])
        scanned_size = sum(item['size'] for item in scan_data['items'])
        self.assertEqual(scanned_size, total_size)

    def test_stop_scan(self):
        # Create large test structure
        structure = {f'file{i}.txt': 1000 for i in range(100)}
        self.create_test_files(structure)
        
        complete_signal = MagicMock()
        self.scanner.scan_complete.connect(complete_signal)
        
        # Start scan and immediately stop it
        self.scanner._is_running = True
        self.scanner.stop()
        self.scanner.start_scan(self.test_dir)
        
        # Verify scan was stopped
        self.assertFalse(self.scanner._is_running)

    def test_error_handling(self):
        error_signal = MagicMock()
        self.scanner.error_occurred.connect(error_signal)
        
        # Test with non-existent directory
        self.scanner.start_scan("/nonexistent/path")
        error_signal.assert_called_once()

class TestTreeMapWindow(TestCase):
    @classmethod
    def setUpClass(cls):
        # Create QApplication instance
        cls.app = QApplication([])
        
    def setUp(self):
        self.window = TreeMapWindow()
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        shutil.rmtree(self.test_dir)
        
    @classmethod
    def tearDownClass(cls):
        cls.app.quit()

    def test_initial_state(self):
        self.assertFalse(self.window.btnStop.isEnabled())
        self.assertEqual(self.window.progressBar.value(), 0)

    def test_draw_treemap(self):
        # Test with sample data
        test_data = {
            'path': self.test_dir,
            'items': [
                {'name': 'file1.txt', 'size': 1000, 'path': 'path1'},
                {'name': 'file2.txt', 'size': 2000, 'path': 'path2'},
                {'name': 'file3.txt', 'size': 3000, 'path': 'path3'}
            ]
        }
        
        self.window.draw_treemap(test_data)
        
        # Verify rectangles were created
        self.assertEqual(len(self.window.scene.items()), 3)

    def test_format_size(self):
        test_cases = [
            (500, "500.0 B"),
            (1024, "1.0 KB"),
            (1024 * 1024, "1.0 MB"),
            (1024 * 1024 * 1024, "1.0 GB")
        ]
        
        for size, expected in test_cases:
            self.assertEqual(self.window.format_size(size), expected)

    def test_empty_directory(self):
        test_data = {'path': self.test_dir, 'items': []}
        self.window.draw_treemap(test_data)
        self.assertEqual(len(self.window.scene.items()), 0)
        self.assertEqual(self.window.lblStatus.text(), "No items to display")

    def test_stop_scan_button(self):
        with patch('PyQt5.QtWidgets.QFileDialog.getExistingDirectory', 
                  return_value=self.test_dir):
            self.window.select_directory()
            self.assertTrue(self.window.btnStop.isEnabled())
            
            self.window.stop_scan()
            self.assertFalse(self.window.btnStop.isEnabled())
