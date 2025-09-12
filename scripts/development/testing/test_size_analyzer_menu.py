#!/usr/bin/env python3
"""Test Size Analyzer menu bar specifically."""

import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from PyQt5.QtWidgets import QApplication
from utilities.analysis.size_analyzer import SizeAnalyzerGUI

def test_size_analyzer():
    """Test Size Analyzer menu bar."""
    app = QApplication(sys.argv)
    
    try:
        # Create the tool
        tool = SizeAnalyzerGUI()
        
        # Check menu bar
        menu_bar = tool.menuBar()
        if menu_bar and menu_bar.actions():
            menu_count = len(menu_bar.actions())
            menu_names = [action.text() for action in menu_bar.actions()]
            print(f"✅ Size Analyzer: Menu bar present with {menu_count} menus")
            print(f"   Menus: {', '.join(menu_names)}")
            
            # Show briefly and close
            tool.show()
            app.processEvents()
            tool.close()
            
            return True
        else:
            print("❌ Size Analyzer: Menu bar missing or empty")
            return False
            
    except Exception as e:
        print(f"❌ Size Analyzer: Error - {e}")
        return False

if __name__ == "__main__":
    success = test_size_analyzer()
    if success:
        print("\n🎉 Size Analyzer menu bar fix successful!")
    else:
        print("\n⚠️ Size Analyzer still needs menu bar fix.")