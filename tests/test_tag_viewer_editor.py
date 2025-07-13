import os
import tempfile
from unittest import TestCase
from unittest.mock import MagicMock, patch
import mutagen
from PyQt5.QtWidgets import QApplication
from tag_viewer_editor import TagViewerEditor

from core.error_handler import error_handler


class TestTagViewerEditor(TestCase):
    """A class that handles test tag viewer editor and inherits from TestCase."""
    @classmethod
    def setUpClass(cls):
        """setupclass.
        Args:
            cls (Any): Description of cls"""
        cls.app = QApplication([])

    def setUp(self):
        """setup."""
        self.viewer = TagViewerEditor()
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """teardown."""
        if hasattr(self, 'test_file') and os.path.exists(self.test_file):
            os.remove(self.test_file)
        os.rmdir(self.test_dir)

    @classmethod
    def tearDownClass(cls):
        """teardownclass.
        Args:
            cls (Any): Description of cls"""
        cls.app.quit()

    def create_test_mp3(self, filename="test.mp3"):
        """Helper method to create a test MP3 file with tags"""
        test_file = os.path.join(self.test_dir, filename)
        with open(test_file, 'wb') as f:
            f.write(b'ID3' + b'\x03\x00\x00\x00\x00\x00\x00' + b'\x00' * 128)
        return test_file

    def test_initial_state(self):
        """testinitialstate."""
        self.assertIsNone(self.viewer.current_file)
        self.assertIsNone(self.viewer.current_tags)
        self.assertEqual(self.viewer.model.rowCount(), 0)

    @patch('PyQt5.QtWidgets.QFileDialog.getOpenFileName')
    def test_browse_file(self, mock_dialog):
        """testbrowsefile.
        Args:
            mock_dialog (Any): Description of mock_dialog"""
        # Create a test MP3 file
        self.test_file = self.create_test_mp3()
        mock_dialog.return_value = (self.test_file, '')

        # Test file browsing
        self.viewer.browse_file()
        self.assertEqual(self.viewer.current_file, self.test_file)
        self.assertEqual(self.viewer.filePathEdit.text(), self.test_file)

    def test_load_metadata(self):
        """testloadmetadata."""
        # Create a test MP3 file with some metadata
        self.test_file = self.create_test_mp3()
        tags = mutagen.File(self.test_file, easy=True)
        tags['title'] = ['Test Title']
        tags['artist'] = ['Test Artist']
        tags.save()

        # Load the file
        self.viewer.current_file = self.test_file
        self.viewer.load_metadata()

        # Check if metadata was loaded correctly
        self.assertIsNotNone(self.viewer.current_tags)
        self.assertGreater(self.viewer.model.rowCount(), 0)

    def test_update_tag(self):
        """testupdatetag."""
        # Create a test MP3 file
        self.test_file = self.create_test_mp3()
        self.viewer.current_file = self.test_file
        self.viewer.current_tags = mutagen.File(self.test_file, easy=True)

        # Update a tag
        self.viewer.keyEdit.setText('title')
        self.viewer.valueEdit.setText('New Title')
        self.viewer.update_tag()

        # Verify the tag was updated
        tags = mutagen.File(self.test_file, easy=True)
        self.assertEqual(tags['title'][0], 'New Title')

    def test_on_table_click(self):
        """testontableclick."""
        # Create a test MP3 file with metadata
        self.test_file = self.create_test_mp3()
        tags = mutagen.File(self.test_file, easy=True)
        tags['title'] = ['Test Title']
        tags.save()

        # Load the metadata
        self.viewer.current_file = self.test_file
        self.viewer.load_metadata()

        # Simulate clicking on the first row
        index = self.viewer.model.index(0, 0)
        self.viewer.on_table_click(index)

        # Verify the edit fields were updated
        self.assertEqual(self.viewer.keyEdit.text(), 'title')
        self.assertEqual(self.viewer.valueEdit.text(), "['Test Title']")

    def test_invalid_file(self):
        """testinvalidfile."""
        # Test with non-existent file
        self.viewer.current_file = "/nonexistent/file.mp3"
        with patch('PyQt5.QtWidgets.QMessageBox.warning') as mock_warning:
            self.viewer.load_metadata()
            mock_warning.assert_called_once()

    def test_empty_tag_update(self):
        """testemptytagupdate."""
        # Try to update tags without loading a file
        with patch('PyQt5.QtWidgets.QMessageBox.warning') as mock_warning:
            self.viewer.update_tag()
            mock_warning.assert_called_once()

    def test_empty_tag_fields(self):
        """testemptytagfields."""
        # Create and load a test file
        self.test_file = self.create_test_mp3()
        self.viewer.current_file = self.test_file
        self.viewer.current_tags = mutagen.File(self.test_file, easy=True)

        # Try to update with empty fields
        self.viewer.keyEdit.setText('')
        self.viewer.valueEdit.setText('')
        with patch('PyQt5.QtWidgets.QMessageBox.warning') as mock_warning:
            self.viewer.update_tag()
            mock_warning.assert_called_once()
