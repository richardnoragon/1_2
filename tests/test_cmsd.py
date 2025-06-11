import os
import tempfile
from unittest import TestCase
from unittest.mock import MagicMock, patch
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QStandardItem
from cmsd import MyGUI

class TestCMSD(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication([])

    def setUp(self):
        self.gui = MyGUI()
        self.test_dir = tempfile.mkdtemp()
        self.create_test_files()
        
    def tearDown(self):
        for f in os.listdir(self.test_dir):
            try:
                os.remove(os.path.join(self.test_dir, f))
            except:
                pass
        os.rmdir(self.test_dir)

    @classmethod
    def tearDownClass(cls):
        cls.app.quit()

    def create_test_files(self):
        """Create test files in the temporary directory"""
        test_files = ['test1.txt', 'test2.txt', 'test3.txt']
        for filename in test_files:
            with open(os.path.join(self.test_dir, filename), 'w') as f:
                f.write('test content')

    @patch('PyQt5.QtWidgets.QFileDialog.getExistingDirectory')
    def test_load_directory_left(self, mock_dialog):
        # Mock directory selection
        mock_dialog.return_value = self.test_dir
        
        # Test loading left directory
        self.gui.load_directory_left()
        
        # Verify files were loaded into model
        self.assertEqual(self.gui.listModel.rowCount(), 3)
        filenames = [self.gui.listModel.item(i).text() 
                    for i in range(self.gui.listModel.rowCount())]
        self.assertIn('test1.txt', filenames)
        self.assertIn('test2.txt', filenames)
        self.assertIn('test3.txt', filenames)

    @patch('PyQt5.QtWidgets.QFileDialog.getExistingDirectory')
    def test_load_directory_right(self, mock_dialog):
        # Mock directory selection
        mock_dialog.return_value = self.test_dir
        
        # Test loading right directory
        self.gui.load_directory_right()
        
        # Verify files were loaded into model
        self.assertEqual(self.gui.listModel.rowCount(), 3)
        filenames = [self.gui.listModel.item(i).text() 
                    for i in range(self.gui.listModel.rowCount())]
        self.assertIn('test1.txt', filenames)
        self.assertIn('test2.txt', filenames)
        self.assertIn('test3.txt', filenames)

    def test_initial_state(self):
        # Test initial state of the GUI
        self.assertEqual(self.gui.directory, ".")
        self.assertEqual(self.gui.listModel.rowCount(), 0)
        self.assertEqual(self.gui.selectModel.rowCount(), 0)
        self.assertEqual(len(self.gui.selected), 0)

    @patch('PyQt5.QtWidgets.QFileDialog.getExistingDirectory')
    def test_load_empty_directory(self, mock_dialog):
        # Create empty directory
        empty_dir = os.path.join(self.test_dir, 'empty')
        os.makedirs(empty_dir)
        mock_dialog.return_value = empty_dir
        
        # Test loading empty directory
        self.gui.load_directory_left()
        self.assertEqual(self.gui.listModel.rowCount(), 0)

    @patch('PyQt5.QtWidgets.QFileDialog.getExistingDirectory')
    def test_load_directory_with_subdirs(self, mock_dialog):
        # Create directory with both files and subdirectories
        subdir = os.path.join(self.test_dir, 'subdir')
        os.makedirs(subdir)
        with open(os.path.join(subdir, 'subfile.txt'), 'w') as f:
            f.write('test')
            
        mock_dialog.return_value = self.test_dir
        
        # Test loading directory
        self.gui.load_directory_left()
        
        # Verify only files (not directories) were loaded
        filenames = [self.gui.listModel.item(i).text() 
                    for i in range(self.gui.listModel.rowCount())]
        self.assertNotIn('subdir', filenames)
