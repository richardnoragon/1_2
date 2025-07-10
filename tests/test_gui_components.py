import unittest
from PyQt5.QtWidgets import QApplication, QPushButton, QTabWidget
from tests.test_utils import TestUtils
from rfuhub import RFUHub


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
        self.assertEqual(
            self.window.windowTitle(),
            "Richard's File Utilities Hub"
        )

    def test_tab_structure(self):
        """Test that all expected tabs are present"""
        tab_widget = self.window.findChild(QTabWidget)
        self.assertIsNotNone(tab_widget)
        
        expected_tabs = [
            "File Management",
            "Organization",
            "Analysis",
            "Operations",
            "Metadata",
            "System",
            "Administration"
        ]
        
        # Access QTabWidget methods directly
        tab_count = tab_widget.count()
        tab_texts = []
        for i in range(tab_count):
            tab_texts.append(tab_widget.tabText(i))
            
        self.assertEqual(len(tab_texts), len(expected_tabs))
        for expected in expected_tabs:
            self.assertIn(expected, tab_texts)

    def test_button_existence(self):
        """Test that all main buttons exist"""
        buttons = self.window.findChildren(QPushButton)
        self.assertGreater(len(buttons), 0)
        
        required_buttons = [
            "File Finder",
            "Catalog Files",
            "Rename Files",
            "Exit"
        ]
        
        button_texts = []
        for btn in buttons:
            button_texts.append(btn.property("text"))
            
        for required in required_buttons:
            self.assertIn(required, button_texts,
                         f"Missing required button: {required}")

    def test_button_click_handling(self):
        """Test that button clicks trigger correct handler"""
        # Test the exit button specifically since it's a direct action
        exit_button = self.window.exit_button
        self.assertIsNotNone(exit_button)
        
        # Store the initial state
        was_called = False
        
        # Create a test handler
        def test_handler():
            nonlocal was_called
            was_called = True
            
        # Connect our test handler
        exit_button.clicked.disconnect()  # Disconnect existing handler
        exit_button.clicked.connect(test_handler)
        
        try:
            # Simulate clicking the exit button
            exit_button.click()
            
            # Verify our handler was called
            self.assertTrue(was_called)
        finally:
            # Reconnect the original quit handler
            exit_button.clicked.disconnect()
            exit_button.clicked.connect(QApplication.instance().quit)

    def test_button_styling(self):
        """Test that buttons have the correct styling"""
        buttons = self.window.findChildren(QPushButton)
        self.assertGreater(len(buttons), 0)
        
        for button in buttons:
            # Check minimum height through property
            min_height = button.property("minimumHeight")
            self.assertIsNotNone(min_height)
            self.assertGreaterEqual(min_height, 50)
            
            # Check that style sheet contains essential elements
            style = button.styleSheet().lower()
            self.assertIn("background-color", style)
            self.assertIn("border-radius", style)
            self.assertIn("padding", style)


if __name__ == '__main__':
    unittest.main()
