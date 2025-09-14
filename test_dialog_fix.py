#!/usr/bin/env python3
"""
Quick test to verify the startup dialog displays correctly.
"""

import logging
import sys

from PyQt5.QtWidgets import (QApplication, QDialog, QLabel, QPushButton,
                             QVBoxLayout)

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('DialogTest')

def test_simple_dialog():
    """Test a simple dialog to ensure PyQt5 is working"""
    app = QApplication(sys.argv)
    
    dialog = QDialog()
    dialog.setWindowTitle("Dialog Test")
    dialog.setFixedSize(300, 200)
    
    layout = QVBoxLayout(dialog)
    
    label = QLabel("This is a test dialog")
    layout.addWidget(label)
    
    button = QPushButton("OK")
    button.setText("OK")  # Explicitly set text
    button.setMinimumSize(100, 35)
    button.clicked.connect(dialog.accept)
    layout.addWidget(button)
    
    # Force proper sizing
    dialog.adjustSize()
    dialog.setFixedSize(300, 200)
    dialog.updateGeometry()
    dialog.update()
    dialog.repaint()
    
    # Process events for proper rendering
    QApplication.processEvents()
    
    logger.info("Showing test dialog")
    result = dialog.exec_()
    logger.info(f"Dialog result: {result}")
    
    return result

def test_startup_dialog():
    """Test the actual startup dialog"""
    app = QApplication(sys.argv)
    
    # Import the actual dialog class
    sys.path.insert(0, r'c:\Users\HP1\1_2')
    
    try:
        from main import InterfaceMode, InterfaceSelectionDialog
        
        logger.info("Creating InterfaceSelectionDialog")
        dialog = InterfaceSelectionDialog(None)
        
        logger.info("Showing selection dialog")
        result = dialog.show_selection_dialog()
        
        logger.info(f"Dialog completed with result: {result}")
        logger.info(f"Selected mode: {dialog.selected_mode}")
        logger.info(f"Remember choice: {dialog.remember_choice}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error testing startup dialog: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("Testing simple dialog...")
    test_simple_dialog()
    
    print("\nTesting startup dialog...")
    test_startup_dialog()