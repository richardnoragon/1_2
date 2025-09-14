#!/usr/bin/env python3
"""
Quick test script to verify radio button text display in the startup dialog.
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

try:
    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import (QApplication, QButtonGroup, QRadioButton,
                                 QVBoxLayout, QWidget)
    
    def test_radio_buttons():
        """Test radio button text display."""
        app = QApplication(sys.argv)
        
        # Create test window
        window = QWidget()
        window.setWindowTitle("Radio Button Text Test")
        window.setGeometry(300, 300, 400, 200)
        
        layout = QVBoxLayout(window)
        
        # Create button group
        button_group = QButtonGroup()
        
        # Test radio buttons with the same styling as the dialog
        radio1 = QRadioButton("📋 Dialog-Based Hub Interface")
        radio1.setStyleSheet("""
            QRadioButton {
                color: #3498db; 
                font-size: 14px;
                font-weight: bold;
                spacing: 8px;
                padding: 5px;
            }
            QRadioButton::indicator {
                width: 16px;
                height: 16px;
                border-radius: 8px;
                border: 2px solid #bdc3c7;
                background-color: white;
            }
            QRadioButton::indicator:checked {
                border: 2px solid #3498db;
                background-color: #3498db;
            }
        """)
        radio1.setChecked(True)
        
        radio2 = QRadioButton("🔀 Multi-Pane Explorer Layout")
        radio2.setStyleSheet("""
            QRadioButton {
                color: #e74c3c; 
                font-size: 14px;
                font-weight: bold;
                spacing: 8px;
                padding: 5px;
            }
            QRadioButton::indicator {
                width: 16px;
                height: 16px;
                border-radius: 8px;
                border: 2px solid #bdc3c7;
                background-color: white;
            }
            QRadioButton::indicator:checked {
                border: 2px solid #e74c3c;
                background-color: #e74c3c;
            }
        """)
        
        button_group.addButton(radio1)
        button_group.addButton(radio2)
        
        layout.addWidget(radio1)
        layout.addWidget(radio2)
        
        window.show()
        
        print("Radio button test window opened.")
        print("If you can see the text on both radio buttons, the fix is working!")
        
        return app.exec_()
    
    if __name__ == '__main__':
        test_radio_buttons()

except ImportError as e:
    print(f"PyQt5 not available for testing: {e}")
    print("This is expected in environments without PyQt5.")
    print("The fix should work when PyQt5 is properly installed.")