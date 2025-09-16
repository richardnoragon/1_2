"""Test error handling and GUI functionality."""
import pytest
from PyQt5.QtWidgets import QApplication, QWidget
from core.error_handler import get_error_handler

def test_error_handler_instance():
    """Test that error handler singleton works correctly."""
    error_handler1 = get_error_handler()
    error_handler2 = get_error_handler()
    assert error_handler1 is error_handler2, "Error handler should be a singleton"

def test_error_handling():
    """Test basic error handling functionality."""
    error_handler = get_error_handler()
    
    # Test handling a simple error
    result = error_handler.handle_error(
        Exception("Test error"),
        "test operation",
        show_dialog=False  # Don't show dialog for test
    )
    assert result is False, "Error handler should return False on error"

@pytest.mark.gui
def test_gui_creation(qtbot):
    """Test basic GUI widget creation."""
    widget = QWidget()
    qtbot.addWidget(widget)
    assert widget is not None, "Widget should be created"
    assert not widget.isVisible(), "Widget should not be visible by default"
