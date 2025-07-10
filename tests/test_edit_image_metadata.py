import os
import tempfile
from unittest import TestCase
from unittest.mock import MagicMock, patch
from PIL import Image
import piexif
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from edit_image_metadata import ExifEditorLogic, ImageMetadataEditor, parse_exif_value, format_exif_value

from core.error_handler import error_handler


class TestExifEditorLogic(TestCase):
    def setUp(self):
        self.editor_logic = ExifEditorLogic()
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        if hasattr(self, 'test_file') and os.path.exists(self.test_file):
            os.remove(self.test_file)
        os.rmdir(self.test_dir)

    def create_test_image(self, filename="test.jpg"):
        """Helper to create a test image with EXIF data"""
        test_file = os.path.join(self.test_dir, filename)
        # Create a small test image
        img = Image.new('RGB', (100, 100), color='red')
        
        # Create sample EXIF data
        exif_dict = {
            "0th": {
                piexif.ImageIFD.Make: b"Test Camera",
                piexif.ImageIFD.Model: b"Test Model"
            },
            "Exif": {
                piexif.ExifIFD.DateTimeOriginal: b"2025:04:08 12:00:00",
                piexif.ExifIFD.ISOSpeedRatings: 100
            }
        }
        exif_bytes = piexif.dump(exif_dict)
        img.save(test_file, "JPEG", exif=exif_bytes)
        return test_file

    def test_load_exif(self):
        self.test_file = self.create_test_image()
        
        # Mock the signals
        data_loaded_signal = MagicMock()
        self.editor_logic.exif_data_loaded.connect(data_loaded_signal)
        
        # Load EXIF
        self.editor_logic.load_exif(self.test_file)
        
        # Verify signal was called with data
        data_loaded_signal.assert_called_once()
        loaded_data = data_loaded_signal.call_args[0][0]
        
        # Check if expected tags are present
        self.assertIn('0th', loaded_data)
        self.assertIn('Exif', loaded_data)
        self.assertIn(piexif.ImageIFD.Make, loaded_data['0th'])
        self.assertIn(piexif.ExifIFD.DateTimeOriginal, loaded_data['Exif'])

    def test_save_exif(self):
        self.test_file = self.create_test_image()
        
        # Load initial EXIF
        self.editor_logic.load_exif(self.test_file)
        
        # Modify some values
        modified_data = {
            "0th": {
                piexif.ImageIFD.Make: {
                    'name': 'Make',
                    'value': 'New Camera',
                    'original_value': b'Test Camera',
                    'original_type': bytes
                }
            }
        }
        
        # Mock signals
        save_result_signal = MagicMock()
        self.editor_logic.save_result.connect(save_result_signal)
        
        # Save modifications
        self.editor_logic.save_exif(self.test_file, modified_data)
        
        # Verify save was successful
        save_result_signal.assert_called_once()
        success, message = save_result_signal.call_args[0]
        self.assertTrue(success)
        
        # Verify changes by loading again
        self.editor_logic.load_exif(self.test_file)
        new_data = self.editor_logic.original_exif_dict
        self.assertEqual(new_data['0th'][piexif.ImageIFD.Make], b'New Camera')

    def test_invalid_file(self):
        # Test with non-existent file
        error_signal = MagicMock()
        self.editor_logic.error_occurred.connect(error_signal)
        
        self.editor_logic.load_exif("/nonexistent/file.jpg")
        error_signal.assert_called_once()

class TestImageMetadataEditor(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication([])

    def setUp(self):
        self.editor = ImageMetadataEditor()
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        if hasattr(self, 'test_file') and os.path.exists(self.test_file):
            os.remove(self.test_file)
        os.rmdir(self.test_dir)

    @classmethod
    def tearDownClass(cls):
        cls.app.quit()

    def create_test_image(self):
        """Create a test image with EXIF data"""
        test_file = os.path.join(self.test_dir, "test.jpg")
        img = Image.new('RGB', (100, 100), color='red')
        
        exif_dict = {
            "0th": {
                piexif.ImageIFD.Make: b"Test Camera",
                piexif.ImageIFD.Model: b"Test Model"
            }
        }
        exif_bytes = piexif.dump(exif_dict)
        img.save(test_file, "JPEG", exif=exif_bytes)
        return test_file

    @patch('PyQt5.QtWidgets.QFileDialog.getOpenFileName')
    def test_browse_file(self, mock_dialog):
        self.test_file = self.create_test_image()
        mock_dialog.return_value = (self.test_file, '')
        
        self.editor.browse_file()
        self.assertEqual(self.editor.current_file, self.test_file)
        self.assertEqual(self.editor.filePathEdit.text(), self.test_file)
        self.assertTrue(self.editor.saveButton.isEnabled())

    def test_handle_item_changed(self):
        self.test_file = self.create_test_image()
        self.editor.current_file = self.test_file
        self.editor.exif_logic.load_exif(self.test_file)
        
        # Find a tag item and simulate editing
        for i in range(self.editor.exifTreeWidget.topLevelItemCount()):
            top_item = self.editor.exifTreeWidget.topLevelItem(i)
            for j in range(top_item.childCount()):
                child = top_item.child(j)
                if child.data(1, Qt.UserRole):
                    child.setText(2, "New Value")
                    self.editor.handle_item_changed(child, 2)
                    ifd_name, tag_code = child.data(1, Qt.UserRole)
                    self.assertEqual(
                        self.editor.modified_data[ifd_name][tag_code]['value'],
                        "New Value"
                    )
                    break

class TestExifHelperFunctions(TestCase):
    def test_format_exif_value(self):
        test_cases = [
            (b"Test String", "Test String"),
            ((100, 1), "100/1"),
            (100, "100"),
            (b"\x00\x01\x02\x03", "00010203 (bytes)")
        ]
        
        for input_value, expected_output in test_cases:
            self.assertEqual(format_exif_value(input_value), expected_output)

    def test_parse_exif_value(self):
        test_cases = [
            ("Test String", str, "Test String"),
            ("100/1", (1, 1), (100, 1)),
            ("100", int, 100)
        ]
        
        for input_str, original_type, expected_output in test_cases:
            result = parse_exif_value(input_str, original_type(), None)
            self.assertEqual(result, expected_output)
