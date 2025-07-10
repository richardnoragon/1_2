import os
import sys
from unittest import TestCase
from unittest.mock import MagicMock, patch
from PyQt5.QtWidgets import QApplication
from main import MyGUI, main, RenameWindow, CatalogWindow, OrganizeWindow

from core.error_handler import error_handler


class TestMainApplication(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication([])

    def setUp(self):
        self.gui = MyGUI()
        
    @classmethod
    def tearDownClass(cls):
        cls.app.quit()

    def test_initial_window_state(self):
        """Test initial state of the main window"""
        self.assertEqual(self.gui.windowTitle(), "My GUI")
        
        # Verify all buttons exist
        self.assertTrue(hasattr(self.gui, 'rename_button'))
        self.assertTrue(hasattr(self.gui, 'catalog_button'))
        self.assertTrue(hasattr(self.gui, 'cmsd_button'))
        self.assertTrue(hasattr(self.gui, 'organize_button'))

    @patch('subprocess.call')
    def test_open_rename_window(self, mock_subprocess):
        """Test opening rename window"""
        self.gui.open_rename_window()
        mock_subprocess.assert_called_once_with(["python", "rename.py"])

    def test_open_catalog_window(self):
        """Test opening catalog window"""
        self.gui.open_catalog_window()
        self.assertIsInstance(self.gui.catalog_window, CatalogWindow)

    def test_open_organize_window(self):
        """Test opening organize window"""
        self.gui.open_organize_window()
        self.assertIsInstance(self.gui.organize_window, OrganizeWindow)

    @patch('main.LogManager')
    @patch('main.ConfigManager')
    def test_main_function_normal_execution(self, mock_config, mock_log_manager):
        """Test normal execution path of main function"""
        # Setup mocks
        mock_logger = MagicMock()
        mock_log_manager.return_value.get_logger.return_value = mock_logger
        mock_config.return_value.get_setting.side_effect = [
            'INFO',  # logging_level
            False    # debug_enabled
        ]

        # Mock RFUHub
        with patch('main.RFUHub') as mock_rfuhub:
            mock_window = MagicMock()
            mock_rfuhub.return_value = mock_window
            
            # Run main function
            with patch.object(QApplication, 'exec_', return_value=0):
                result = main()

            # Verify execution
            self.assertEqual(result, 0)
            mock_window.show.assert_called_once()
            mock_logger.info.assert_any_call('Starting Richards Files Utilities')
            mock_logger.info.assert_any_call('Qt Application initialized')

    @patch('main.LogManager')
    @patch('main.ConfigManager')
    def test_main_function_with_debug_enabled(self, mock_config, mock_log_manager):
        """Test main function with debug logging enabled"""
        # Setup mocks
        mock_logger = MagicMock()
        mock_log_manager.return_value.get_logger.return_value = mock_logger
        mock_config.return_value.get_setting.side_effect = [
            'INFO',  # logging_level
            True     # debug_enabled
        ]

        # Run main function
        with patch('main.RFUHub'):
            with patch.object(QApplication, 'exec_', return_value=0):
                result = main()

        # Verify debug mode was set
        mock_log_manager.return_value.set_level.assert_called_with('DEBUG')
        self.assertEqual(result, 0)

    @patch('main.LogManager')
    @patch('main.ConfigManager')
    def test_main_function_error_handling(self, mock_config, mock_log_manager):
        """Test error handling in main function"""
        # Setup mocks
        mock_logger = MagicMock()
        mock_log_manager.return_value.get_logger.return_value = mock_logger
        mock_config.return_value.get_setting.side_effect = Exception("Test error")

        # Run main function
        result = main()

        # Verify error handling
        self.assertEqual(result, 1)
        mock_logger.critical.assert_called_once()
        self.assertIn("Test error", mock_logger.critical.call_args[0][0])

class TestSubWindows(TestCase):
    """Test the individual sub-window classes"""
    
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication([])

    @classmethod
    def tearDownClass(cls):
        cls.app.quit()

    def test_rename_window(self):
        window = RenameWindow()
        self.assertEqual(window.windowTitle(), "Rename Window")
        self.assertEqual(window.geometry().width(), 400)
        self.assertEqual(window.geometry().height(), 300)

    def test_catalog_window(self):
        window = CatalogWindow()
        self.assertEqual(window.windowTitle(), "Catalog Window")
        self.assertEqual(window.geometry().width(), 400)
        self.assertEqual(window.geometry().height(), 300)

    def test_organize_window(self):
        window = OrganizeWindow()
        self.assertEqual(window.windowTitle(), "Organize Window")
        self.assertEqual(window.geometry().width(), 400)
        self.assertEqual(window.geometry().height(), 300)
