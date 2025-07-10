import unittest
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
import pytest
from tests.test_utils import TestUtils

from core.error_handler import error_handler


class BaseGuiTest(unittest.TestCase):
    """Base class for GUI tests providing common functionality"""
    
    @classmethod
    def setUpClass(cls):
        """Create QApplication once for all tests in the class"""
        cls.app = TestUtils.get_test_app()
        
    def setUp(self):
        """Set up test environment"""
        self.test_dir = TestUtils.create_temp_dir()
        
    def tearDown(self):
        """Clean up test environment"""
        TestUtils.cleanup_temp_dir(self.test_dir)
        # Process pending events
        QTest.qWait(100)
    
    def wait_for(self, condition, timeout=1000, interval=50):
        """Wait for a condition to become true
        
        Args:
            condition: Function that returns True when condition is met
            timeout: Maximum time to wait in milliseconds
            interval: Check interval in milliseconds
        
        Returns:
            bool: True if condition was met, False if timeout occurred
        """
        total_waited = 0
        while not condition() and total_waited < timeout:
            QTest.qWait(interval)
            total_waited += interval
        return total_waited < timeout
    
    def click_button(self, button):
        """Safely click a button
        
        Args:
            button: QPushButton to click
        """
        if not button.isEnabled():
            raise RuntimeError(f"Button {button.text()} is not enabled")
        QTest.mouseClick(button, Qt.LeftButton)
        QTest.qWait(100)  # Wait for click to process
    
    def enter_text(self, widget, text):
        """Enter text into a widget
        
        Args:
            widget: QWidget that accepts text input
            text: Text to enter
        """
        widget.clear()
        QTest.keyClicks(widget, text)
        QTest.keyClick(widget, Qt.Key_Return)
        QTest.qWait(100)  # Wait for text to process
    
    def select_in_list(self, list_widget, text):
        """Select an item in a list widget by text
        
        Args:
            list_widget: QListWidget to select in
            text: Text of item to select
        
        Returns:
            bool: True if item was found and selected
        """
        for i in range(list_widget.count()):
            item = list_widget.item(i)
            if item.text() == text:
                list_widget.setCurrentItem(item)
                QTest.qWait(100)  # Wait for selection to process
                return True
        return False
    
    def select_in_combo(self, combo_box, text):
        """Select an item in a combo box by text
        
        Args:
            combo_box: QComboBox to select in
            text: Text to select
        
        Returns:
            bool: True if item was found and selected
        """
        index = combo_box.findText(text)
        if index >= 0:
            combo_box.setCurrentIndex(index)
            QTest.qWait(100)  # Wait for selection to process
            return True
        return False
    
    def check_widget_visibility(self, widget, expected_visible=True, timeout=1000):
        """Check if widget becomes visible/invisible within timeout
        
        Args:
            widget: Widget to check
            expected_visible: True to wait for visible, False for invisible
            timeout: Maximum time to wait in milliseconds
        
        Returns:
            bool: True if widget reached expected visibility state
        """
        return self.wait_for(
            lambda: widget.isVisible() == expected_visible,
            timeout=timeout
        )
    
    def verify_widget_enabled(self, widget, expected_enabled=True, timeout=1000):
        """Check if widget becomes enabled/disabled within timeout
        
        Args:
            widget: Widget to check
            expected_enabled: True to wait for enabled, False for disabled
            timeout: Maximum time to wait in milliseconds
        
        Returns:
            bool: True if widget reached expected enabled state
        """
        return self.wait_for(
            lambda: widget.isEnabled() == expected_enabled,
            timeout=timeout
        )
    
    def verify_widget_text(self, widget, expected_text, timeout=1000):
        """Check if widget text matches expected text within timeout
        
        Args:
            widget: Widget with text property to check
            expected_text: Text to match
            timeout: Maximum time to wait in milliseconds
        
        Returns:
            bool: True if text matched within timeout
        """
        return self.wait_for(
            lambda: widget.text() == expected_text,
            timeout=timeout
        )
    
    def verify_status_message(self, status_bar, expected_message, timeout=1000):
        """Check if status bar shows expected message within timeout
        
        Args:
            status_bar: QStatusBar to check
            expected_message: Message to look for
            timeout: Maximum time to wait in milliseconds
        
        Returns:
            bool: True if message appeared within timeout
        """
        return self.wait_for(
            lambda: expected_message in status_bar.currentMessage(),
            timeout=timeout
        )
    
    def capture_dialog(self, trigger_action, dialog_type):
        """Capture and return a dialog shown by an action
        
        Args:
            trigger_action: Function that will show the dialog
            dialog_type: Expected type of dialog
        
        Returns:
            The shown dialog if it matched the expected type
        """
        dialogs = []
        def dialog_shown(dialog):
            if isinstance(dialog, dialog_type):
                dialogs.append(dialog)
        
        # Connect to show dialog signal
        self.app.installEventFilter(lambda obj, event: 
            dialog_shown(obj) if isinstance(obj, dialog_type) else False
        )
        
        # Trigger the action
        trigger_action()
        
        # Wait for dialog
        self.wait_for(lambda: len(dialogs) > 0)
        
        return dialogs[0] if dialogs else None