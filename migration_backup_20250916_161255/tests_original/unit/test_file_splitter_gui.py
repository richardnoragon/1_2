"""
GUI Tests for File Splitter

This module provides comprehensive testing for the file splitter GUI
components with file_utilities_2 integration, including StandardWindow
integration, ThemeManager styling, and widget functionality.
"""

import unittest
import os
import tempfile
import shutil
from unittest.mock import Mock, patch
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest

from file_utilities_2.gui.file_splitter_gui import FileSplitterGUI
from file_utilities_2.gui.file_splitter_widget import FileSplitterWidget
from file_utilities_2.gui.standard_window import StandardWindow
from file_utilities_2.core.file_splitter_config import FileSplitterConfig


class TestFileSplitterGUI(unittest.TestCase):
    """Test suite for FileSplitterGUI with StandardWindow integration."""
    
    @classmethod
    def setUpClass(cls):
        """Set up QApplication for GUI testing."""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_dir = tempfile.mkdtemp()
        
        # Create test file
        self.test_file = os.path.join(self.test_dir, "gui_test.dat")
        with open(self.test_file, 'wb') as f:
            f.write(os.urandom(1024))  # 1KB test file
        
        # Mock hub connector to avoid actual hub connections
        with patch('file_utilities_2.gui.file_splitter_gui.HubConnector'):
            self.gui = FileSplitterGUI()
    
    def tearDown(self):
        """Clean up test fixtures after each test method."""
        if hasattr(self, 'gui'):
            self.gui.close()
        shutil.rmtree(self.test_dir)
    
    def test_gui_initialization(self):
        """Test GUI initialization and StandardWindow inheritance."""
        # Test inheritance
        self.assertIsInstance(self.gui, StandardWindow)
        
        # Test basic properties
        self.assertEqual(self.gui.windowTitle(), "File Splitter & Joiner")
        self.assertIsNotNone(self.gui.config)
        self.assertIsNotNone(self.gui.logger)
        self.assertIsNotNone(self.gui.logic)
        
        # Test UI components exist
        self.assertIsNotNone(self.gui.tab_widget)
        self.assertIsNotNone(self.gui.split_tab)
        self.assertIsNotNone(self.gui.join_tab)
        self.assertIsNotNone(self.gui.progress_bar)
        self.assertIsNotNone(self.gui.status_label)
    
    def test_split_tab_components(self):
        """Test split tab UI components."""
        # Test input components
        self.assertIsNotNone(self.gui.split_input_path)
        self.assertIsNotNone(self.gui.split_browse_input)
        self.assertIsNotNone(self.gui.split_output_path)
        self.assertIsNotNone(self.gui.split_browse_output)
        
        # Test split options
        self.assertIsNotNone(self.gui.split_by_size)
        self.assertIsNotNone(self.gui.split_by_parts)
        self.assertIsNotNone(self.gui.size_value)
        self.assertIsNotNone(self.gui.size_unit)
        self.assertIsNotNone(self.gui.parts_value)
        
        # Test split button
        self.assertIsNotNone(self.gui.split_button)
        
        # Test initial state
        self.assertTrue(self.gui.split_by_size.isChecked())
        self.assertFalse(self.gui.split_by_parts.isChecked())
        self.assertTrue(self.gui.size_value.isEnabled())
        self.assertFalse(self.gui.parts_value.isEnabled())
    
    def test_join_tab_components(self):
        """Test join tab UI components."""
        # Test input components
        self.assertIsNotNone(self.gui.join_input_path)
        self.assertIsNotNone(self.gui.join_browse_input)
        self.assertIsNotNone(self.gui.join_output_path)
        self.assertIsNotNone(self.gui.join_browse_output)
        
        # Test join button
        self.assertIsNotNone(self.gui.join_button)
    
    def test_split_mode_toggle(self):
        """Test split mode radio button functionality."""
        # Initially split by size should be checked
        self.assertTrue(self.gui.split_by_size.isChecked())
        self.assertTrue(self.gui.size_value.isEnabled())
        self.assertTrue(self.gui.size_unit.isEnabled())
        self.assertFalse(self.gui.parts_value.isEnabled())
        
        # Click split by parts
        self.gui.split_by_parts.setChecked(True)
        self.gui.on_split_mode_changed()
        
        # Check state changed
        self.assertFalse(self.gui.size_value.isEnabled())
        self.assertFalse(self.gui.size_unit.isEnabled())
        self.assertTrue(self.gui.parts_value.isEnabled())
        
        # Click split by size again
        self.gui.split_by_size.setChecked(True)
        self.gui.on_split_mode_changed()
        
        # Check state reverted
        self.assertTrue(self.gui.size_value.isEnabled())
        self.assertTrue(self.gui.size_unit.isEnabled())
        self.assertFalse(self.gui.parts_value.isEnabled())
    
    def test_progress_updates(self):
        """Test progress bar and status updates."""
        # Test progress update
        self.gui.update_progress(50, 100, "Test progress message")
        
        self.assertEqual(self.gui.progress_bar.value(), 50)
        self.assertEqual(self.gui.status_label.text(), "Test progress message")
        
        # Test completion
        self.gui.update_progress(100, 100, "Operation complete")
        self.assertEqual(self.gui.progress_bar.value(), 100)
    
    def test_operation_state_management(self):
        """Test operation state management."""
        # Initially buttons should be enabled
        self.assertTrue(self.gui.split_button.isEnabled())
        self.assertTrue(self.gui.join_button.isEnabled())
        self.assertFalse(self.gui.progress_bar.isVisible())
        
        # Set running state
        self.gui._set_operation_state(True)
        
        self.assertFalse(self.gui.split_button.isEnabled())
        self.assertFalse(self.gui.join_button.isEnabled())
        self.assertTrue(self.gui.progress_bar.isVisible())
        
        # Set idle state
        self.gui._set_operation_state(False)
        
        self.assertTrue(self.gui.split_button.isEnabled())
        self.assertTrue(self.gui.join_button.isEnabled())
        self.assertFalse(self.gui.progress_bar.isVisible())


class TestFileSplitterWidget(unittest.TestCase):
    """Test suite for FileSplitterWidget embeddable component."""
    
    @classmethod
    def setUpClass(cls):
        """Set up QApplication for GUI testing."""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_dir = tempfile.mkdtemp()
        self.widget = FileSplitterWidget()
    
    def tearDown(self):
        """Clean up test fixtures after each test method."""
        if hasattr(self, 'widget'):
            self.widget.close()
        shutil.rmtree(self.test_dir)
    
    def test_widget_initialization(self):
        """Test widget initialization."""
        # Test basic properties
        self.assertIsNotNone(self.widget.config)
        self.assertIsNotNone(self.widget.logger)
        self.assertIsNotNone(self.widget.logic)
        
        # Test UI components exist
        self.assertIsNotNone(self.widget.tab_widget)
        self.assertIsNotNone(self.widget.split_tab)
        self.assertIsNotNone(self.widget.join_tab)
        self.assertIsNotNone(self.widget.progress_bar)
        self.assertIsNotNone(self.widget.status_label)
    
    def test_compact_layout(self):
        """Test compact layout for embedding."""
        # Widget should be more compact than full GUI
        self.assertLessEqual(self.widget.minimumHeight(), 400)
        
        # Progress bar should be compact
        self.assertEqual(self.widget.progress_bar.maximumHeight(), 20)
        self.assertEqual(self.widget.status_label.maximumHeight(), 20)
    
    def test_widget_signals(self):
        """Test widget signals for parent communication."""
        # Test signal existence
        self.assertTrue(hasattr(self.widget, 'operation_started'))
        self.assertTrue(hasattr(self.widget, 'operation_completed'))
        self.assertTrue(hasattr(self.widget, 'operation_failed'))
    
    def test_stop_operation_method(self):
        """Test external stop operation control."""
        # Test stop operation method exists
        self.assertTrue(hasattr(self.widget, 'stop_operation'))
        
        # Test calling stop operation
        self.widget.stop_operation()  # Should not crash


if __name__ == '__main__':
    # Initialize QApplication for Qt GUI testing
    app = QApplication([])
    unittest.main()