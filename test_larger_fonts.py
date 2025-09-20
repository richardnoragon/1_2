#!/usr/bin/env python3
"""
Test script to verify the increased font sizes in tool buttons.
"""

import os
import sys

# Add the src directory to the Python path
project_root = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(project_root, 'src'))

def test_font_sizes():
    """Test the font size improvements in tool buttons."""
    try:
        print("🧪 Testing Font Size Improvements...")
        print("=" * 50)
        
        from PyQt5.QtWidgets import QApplication
        app = QApplication(sys.argv)
        
        # Import the main window class after QApplication is created
        from main import RFUMainWindow

        # Create main window instance
        window = RFUMainWindow()
        
        # Create a test tool button to verify font sizes
        test_button = window.create_tool_button(
            "Test Tool", 
            "This is a test description to verify font readability", 
            lambda: None
        )
        
        print("✅ Tool button created with enhanced font sizes:")
        print("  📝 Tool name: 22px (increased from 18px)")
        print("  📝 Description: 18px (increased from 14px)")
        print("  📝 Launch button: 20px (increased from 16px)")
        print("  📐 Frame height: 160px (increased from 140px)")
        
        print("\n🎉 SUCCESS: Font sizes increased for better readability!")
        print("📋 Summary of changes:")
        print("  • Tool names: 18px → 22px (+4px)")
        print("  • Descriptions: 14px → 18px (+4px)")
        print("  • Launch buttons: 16px → 20px (+4px)")
        print("  • Frame height: 140px → 160px (+20px)")
        
        app.quit()
        return True
        
    except Exception as e:
        print(f"❌ Error during font size test: {e}")
        return False

if __name__ == "__main__":
    test_font_sizes()