#!/usr/bin/env python3
"""
Test script to verify File Finder works correctly.
"""
import sys

from PyQt5.QtWidgets import QApplication

from src.tools.file_management.finder import FileFinderWindow

def test_file_finder():
    """Test launching File Finder."""
    try:
        print("Creating QApplication...")
        app = QApplication(sys.argv)
        
    print("Creating FileFinderWindow...")
    window = FileFinderWindow()
        
        print("✅ File Finder created successfully!")
        print("Showing window...")
        window.show()
        
        print("✅ File Finder is ready to use!")
        print("Close the window to exit this test.")
        
        return app.exec_()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(test_file_finder())
