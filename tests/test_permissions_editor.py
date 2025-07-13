import os
import stat
import tempfile
from unittest import TestCase
from unittest.mock import MagicMock, patch
from PyQt5.QtCore import Qt, QMimeData, QUrl
from PyQt5.QtGui import QDragEnterEvent, QDropEvent
from PyQt5.QtWidgets import QApplication
from permissions_editor import FilePermissionsGUI

from core.error_handler import error_handler


class TestFilePermissionsGUI(TestCase):
    """A class that handles test file permissions g u i and inherits from TestCase."""
    @classmethod
    def setUpClass(cls):
        """setupclass.
        Args:
            cls (Any): Description of cls"""
        cls.app = QApplication([])

    def setUp(self):
        """setup."""
        self.editor = FilePermissionsGUI()
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """teardown."""
        for file in os.listdir(self.test_dir):
            os.chmod(os.path.join(self.test_dir, file), 0o777)  # Reset permissions
            os.remove(os.path.join(self.test_dir, file))
        os.rmdir(self.test_dir)

    @classmethod
    def tearDownClass(cls):
        """teardownclass.
        Args:
            cls (Any): Description of cls"""
        cls.app.quit()

    def create_test_file(self, filename="test.txt", permissions=0o666):
        """Helper to create a test file with specific permissions"""
        filepath = os.path.join(self.test_dir, filename)
        with open(filepath, 'w') as f:
            f.write('test content')
        os.chmod(filepath, permissions)
        return filepath

    @patch('PyQt5.QtWidgets.QFileDialog.getOpenFileNames')
    def test_select_files(self, mock_dialog):
        """testselectfiles.
        Args:
            mock_dialog (Any): Description of mock_dialog"""
        # Create test files
        test_file1 = self.create_test_file("test1.txt")
        test_file2 = self.create_test_file("test2.txt")
        mock_dialog.return_value = ([test_file1, test_file2], '')

        # Test file selection
        self.editor.select_files()

        # Verify files were added to the model
        self.assertEqual(self.editor.model.rowCount(), 2)
        self.assertEqual(self.editor.model.item(0).text(), test_file1)
        self.assertEqual(self.editor.model.item(1).text(), test_file2)

    def test_add_files(self):
        """testaddfiles."""
        # Create test file
        test_file = self.create_test_file()
        
        # Add file to the editor
        self.editor.add_files([test_file])
        
        # Verify file was added
        self.assertEqual(self.editor.model.rowCount(), 1)
        self.assertEqual(self.editor.model.item(0).text(), test_file)

    def test_update_file_permissions(self):
        """testupdatefilepermissions."""
        # Create file with read-only permissions
        test_file = self.create_test_file(permissions=0o444)
        
        # Update permissions display
        self.editor.update_file_permissions(test_file)
        
        # Verify checkboxes reflect permissions
        self.assertTrue(self.editor.read_checkBox.isChecked())
        self.assertFalse(self.editor.write_checkBox.isChecked())
        self.assertFalse(self.editor.execute_checkBox.isChecked())

    def test_set_permissions(self):
        """testsetpermissions."""
        # Create test file
        test_file = self.create_test_file(permissions=0o666)
        self.editor.add_files([test_file])
        
        # Set new permissions
        self.editor.read_checkBox.setChecked(True)
        self.editor.write_checkBox.setChecked(False)
        self.editor.execute_checkBox.setChecked(True)
        
        # Apply permissions
        with patch('PyQt5.QtWidgets.QMessageBox.information') as mock_info:
            self.editor.set_permissions()
            mock_info.assert_called_once()
        
        # Verify permissions were changed
        new_mode = os.stat(test_file).st_mode
        self.assertTrue(bool(new_mode & stat.S_IREAD))
        self.assertFalse(bool(new_mode & stat.S_IWRITE))
        self.assertTrue(bool(new_mode & stat.S_IEXEC))

    def test_set_permissions_no_files(self):
        """testsetpermissionsnofiles."""
        # Test setting permissions with no files selected
        with patch('PyQt5.QtWidgets.QMessageBox.information') as mock_info:
            self.editor.set_permissions()
            mock_info.assert_called_once()

    def test_drag_and_drop(self):
        """testdraganddrop."""
        # Create test file
        test_file = self.create_test_file()
        
        # Mock drag enter event
        drag_event = MagicMock(spec=QDragEnterEvent)
        mime_data = QMimeData()
        mime_data.setUrls([QUrl.fromLocalFile(test_file)])
        drag_event.mimeData.return_value = mime_data
        
        # Test drag enter
        self.editor.dragEnterEvent(drag_event)
        drag_event.acceptProposedAction.assert_called_once()
        
        # Mock drop event
        drop_event = MagicMock(spec=QDropEvent)
        drop_event.mimeData.return_value = mime_data
        
        # Test drop
        self.editor.dropEvent(drop_event)
        
        # Verify file was added
        self.assertEqual(self.editor.model.rowCount(), 1)
        self.assertEqual(self.editor.model.item(0).text(), test_file)

    def test_error_handling(self):
        """testerrorhandling."""
        # Test with non-existent file
        with patch('PyQt5.QtWidgets.QMessageBox.warning') as mock_warning:
            self.editor.update_file_permissions("/nonexistent/file.txt")
            mock_warning.assert_called_once()

    def test_permission_update_failure(self):
        """testpermissionupdatefailure."""
        # Create test file that will fail permission update
        test_file = self.create_test_file()
        self.editor.add_files([test_file])
        
        # Mock os.chmod to raise an exception
        with patch('os.chmod', side_effect=PermissionError("Access denied")), \
             patch('PyQt5.QtWidgets.QMessageBox.warning') as mock_warning:
            self.editor.set_permissions()
            mock_warning.assert_called_once()
