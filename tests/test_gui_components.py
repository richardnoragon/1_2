import unittest
import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from tests.test_utils import TestUtils
from rfuhub import RFUHub  # Update based on actual main window class name

class TestGUIComponents(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Create the application once for all tests"""
        cls.app = TestUtils.get_test_app()

    def setUp(self):
        """Create the main window for each test"""
        self.window = RFUHub()
        self.test_dir = TestUtils.create_temp_dir()

    def tearDown(self):
        """Clean up after each test"""
        self.window.close()
        TestUtils.cleanup_temp_dir(self.test_dir)

    def test_window_title(self):
        """Test that the window title is correct"""
        self.assertEqual(self.window.windowTitle(), "Richard's File Utilities Hub")

    def test_file_selection(self):
        """Test the file selection dialog"""
        # Create a test file
        test_file = os.path.join(self.test_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("test content")

        # Simulate file selection
        self.window.last_directory = self.test_dir  # Set initial directory
        
        # Here we're assuming there's a method to programmatically select files
        # without showing the dialog
        self.window.select_files([test_file])
        
        # Verify the file appears in the file list
        self.assertIn("test.txt", self.window.get_selected_files())

    def test_menu_actions(self):
        """Test that menu actions are connected"""
        # Get all actions
        actions = self.window.findChildren(QAction)
        
        # Verify essential actions exist
        action_names = [a.text() for a in actions]
        required_actions = ["Open", "Save", "Exit"]
        for required in required_actions:
            self.assertTrue(
                any(required in name for name in action_names),
                f"Missing required action: {required}"
            )

    @unittest.skipIf(os.environ.get('CI') == 'true', "Skip in CI environment")
    def test_drag_drop(self):
        """Test drag and drop functionality"""
        # Create a mock drag event
        mime_data = QMimeData()
        mime_data.setUrls([QUrl.fromLocalFile(self.test_dir)])
        
        # Create and execute the drop event
        event = QDropEvent(
            QPoint(0, 0),
            Qt.CopyAction,
            mime_data,
            Qt.LeftButton,
            Qt.NoModifier
        )
        
        # Assume there's a drop handler
        self.window.dropEvent(event)
        
        # Verify the directory was added
        self.assertIn(self.test_dir, self.window.get_directories())

    def test_progress_bar(self):
        """Test progress bar updates"""
        progress = self.window.findChild(QProgressBar)
        self.assertIsNotNone(progress)
        
        # Test progress updates
        self.window.update_progress(50)
        self.assertEqual(progress.value(), 50)
        
        self.window.update_progress(100)
        self.assertEqual(progress.value(), 100)

    def test_error_dialog(self):
        """Test error dialog display"""
        # Trigger an error
        error_msg = "Test error message"
        QTimer.singleShot(100, lambda: self.click_ok_on_error_dialog())
        self.window.show_error(error_msg)
        
        # Verify error was shown (implementation dependent)
        self.assertTrue(self.window.last_error_shown == error_msg)

    def click_ok_on_error_dialog(self):
        """Helper to click OK on error dialog"""
        dialog = QApplication.activeModalWidget()
        if dialog:
            QTest.keyClick(dialog, Qt.Key_Return)

if __name__ == '__main__':
    unittest.main()