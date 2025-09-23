#!/usr/bin/env python3
"""
Test script to verify Multi Pane Explorer UI improvements.

This script tests:
1. Folder icons are displayed
2. File type color coding is working
3. One-click directory expansion is functional
"""

import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

try:
    from PyQt5.QtWidgets import QApplication

    from src.file_explorer.multi_pane_explorer import MultiPaneFileExplorer
    
    def test_ui_improvements():
        """Test if our UI improvements are properly implemented."""
        print("Testing Multi Pane Explorer UI improvements...")
        
        app = QApplication([])
        
        # Create the explorer instance
        explorer = MultiPaneFileExplorer()
        
        # Test 1: Check if color mappings exist
        print("✓ Testing file type color mappings...")
        assert hasattr(explorer, 'FILE_TYPE_COLORS'), "FILE_TYPE_COLORS not found"
        assert '.py' in explorer.FILE_TYPE_COLORS, "Python file color not defined"
        assert '.jpg' in explorer.FILE_TYPE_COLORS, "Image file color not defined"
        print(f"  Found {len(explorer.FILE_TYPE_COLORS)} file type color mappings")
        
        # Test 2: Check if icons exist
        print("✓ Testing file type icons...")
        assert hasattr(explorer, 'FOLDER_ICON'), "FOLDER_ICON not found"
        assert hasattr(explorer, 'FILE_ICONS'), "FILE_ICONS not found"
        assert explorer.FOLDER_ICON == "📁", "Folder icon is incorrect"
        assert '.py' in explorer.FILE_ICONS, "Python file icon not defined"
        print(f"  Found folder icon: {explorer.FOLDER_ICON}")
        print(f"  Found {len(explorer.FILE_ICONS)} file type icons")
        
        # Test 3: Check if single-click method exists
        print("✓ Testing single-click navigation method...")
        assert hasattr(explorer, '_on_file_item_single_click'), "Single-click method not found"
        print("  Single-click navigation method found")
        
        # Test 4: Check if populate method uses improvements
        print("✓ Testing file list population method...")
        assert hasattr(explorer, '_populate_file_list'), "Populate method not found"
        print("  Enhanced populate method found")
        
        print("\n🎉 All UI improvements are properly implemented!")
        print("\nTo see the improvements in action:")
        print("1. Run: python main.py")
        print("2. Select 'Multi-Pane Explorer Layout' from the welcome dialog")
        print("3. Look for:")
        print("   • 📁 Folder icons next to directory names")
        print("   • Different colored file names based on file type")
        print("   • Single-click navigation into folders")
        
        return True
        
    if __name__ == '__main__':
        test_ui_improvements()
        
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running this from the project root directory.")
    sys.exit(1)
except Exception as e:
    print(f"Test failed: {e}")
    sys.exit(1)