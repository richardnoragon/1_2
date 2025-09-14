#!/usr/bin/env python3
"""Test the multi-pane widget creation directly."""

import os
import sys
from pathlib import Path

from PyQt5.QtWidgets import QApplication

# Add the same paths as main.py
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(project_root, 'src'))

def test_multi_pane_widget():
    """Test creating the multi-pane widget."""
    app = QApplication(sys.argv)
    
    try:
        # Import the main window class
        from main import RFUMainWindow

        # Create a main window instance
        main_window = RFUMainWindow()
        
        # Test the _create_multi_pane_widget method
        print("Testing _create_multi_pane_widget method...")
        multi_pane_widget = main_window._create_multi_pane_widget()
        
        if multi_pane_widget:
            print("✅ Multi-pane widget created successfully!")
            print(f"Widget type: {type(multi_pane_widget)}")
            
            # Show the widget to verify it displays
            multi_pane_widget.setWindowTitle("Test Multi-Pane Widget")
            multi_pane_widget.show()
            multi_pane_widget.resize(800, 600)
            
            print("Multi-pane widget is displayed. Check the window!")
            return True
        else:
            print("❌ Failed to create multi-pane widget")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        app.quit()

if __name__ == "__main__":
    test_multi_pane_widget()