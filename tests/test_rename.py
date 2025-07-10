import os
import shutil
import tempfile
from datetime import datetime
from unittest import TestCase
from unittest.mock import MagicMock, patch
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel
from rename import MyGUI

from core.error_handler import error_handler


class TestRename(TestCase):
    def setUp(self):
        self.app = MagicMock()
        self.gui = MyGUI()
        self.test_dir = tempfile.mkdtemp()
        self.gui.directory = self.test_dir
        
        # Create some test files
        self.test_files = ['test1.txt', 'test2.jpg', 'test3.mp3']
        for file in self.test_files:
            with open(os.path.join(self.test_dir, file), 'w') as f:
                f.write('test content')

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_load_directory(self):
        with patch('PyQt5.QtWidgets.QFileDialog.getExistingDirectory', return_value=self.test_dir):
            self.gui.load_directory()
            self.assertEqual(self.gui.listModel.rowCount(), len(self.test_files))

    def test_filter_list(self):
        self.gui.filterEdit.setText('test1')
        self.gui.filter_list()
        self.assertEqual(self.gui.listModel.rowCount(), 1)

    def test_choose_selection(self):
        self.gui.listModel = QStandardItemModel()
        for file in self.test_files:
            self.gui.listModel.appendRow(QStandardItemModel().itemFromIndex(file))
        
        # Mock selection
        self.gui.listView.selectedIndexes = MagicMock(return_value=[self.gui.listModel.index(0, 0)])
        self.gui.choose_selection()
        self.assertEqual(len(self.gui.selected), 1)
        self.assertEqual(self.gui.selectModel.rowCount(), 1)

    def test_rename_files_prefix(self):
        # Test prefix addition
        self.gui.selected = ['test1.txt']
        self.gui.nameEdit.setText('prefix_')
        self.gui.addPrefixRadio.setChecked(True)
        self.gui.rename_files()
        
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, 'prefix_test1.txt')))

    def test_rename_files_suffix(self):
        # Test suffix addition
        self.gui.selected = ['test1.txt']
        self.gui.nameEdit.setText('_suffix')
        self.gui.addSuffixRadio.setChecked(True)
        self.gui.rename_files()
        
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, 'test1_suffix.txt')))

    def test_rename_files_case_changes(self):
        # Create a mixed-case test file
        test_file = 'TestCase.txt'
        with open(os.path.join(self.test_dir, test_file), 'w') as f:
            f.write('test content')
            
        self.gui.selected = [test_file]
        
        # Test lowercase conversion
        self.gui.lowerCaseRadio.setChecked(True)
        self.gui.rename_files()
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, 'testcase.txt')))

    def test_metadata_date_formatting(self):
        test_date = datetime(2025, 4, 8, 12, 30, 45)
        
        # Test different date formats
        formats = {
            "YYYY-MM-DD_HHMMSS": "2025-04-08_123045",
            "YYYYMMDD_HHMMSS": "20250408_123045",
            "DD-MM-YYYY_HHMMSS": "08-04-2025_123045",
            "YYYY-MM-DD": "2025-04-08",
            "YYYYMMDD": "20250408"
        }
        
        for format_str, expected in formats.items():
            result = self.gui.format_date(test_date, format_str)
            self.assertEqual(result, expected)

    def test_get_file_metadata_date(self):
        # Test fallback to file modification time for regular files
        test_file = os.path.join(self.test_dir, 'test1.txt')
        result = self.gui.get_file_metadata_date(test_file)
        self.assertIsInstance(result, datetime)
