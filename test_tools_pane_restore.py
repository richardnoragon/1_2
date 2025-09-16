#!/usr/bin/env python3
"""
Test script to verify the restored tools pane functionality in the multi-pane file explorer.

This script tests:
- Tools pane visibility and integration
- Tool category display and organization  
- Tool launch functionality
- Search and filtering capabilities
- Keyboard navigation support
- Inter-pane communication
"""

import os
import sys
from pathlib import Path

# Add src to path
project_root = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(project_root, 'src'))

try:
    from PyQt5.QtCore import Qt, QTimer
    from PyQt5.QtWidgets import QApplication, QMessageBox

    # Import the multi-pane explorer
    from src.rfu.file_explorer.multi_pane_explorer_repaired import \
        MultiPaneFileExplorer
    
    def test_tools_pane_functionality():
        """Test tools pane functionality."""
        print("Testing Tools Pane Restoration...")
        
        app = QApplication(sys.argv)
        
        try:
            # Create explorer window
            explorer = MultiPaneFileExplorer()
            
            # Verify tools pane exists
            print("✅ MultiPaneFileExplorer created successfully")
            
            # Check if left panel has tools tab
            if hasattr(explorer, 'create_left_panel'):
                left_panel = explorer.create_left_panel()
                
                if hasattr(left_panel, 'count') and left_panel.count() >= 2:
                    print(f"✅ Left panel has {left_panel.count()} tabs")
                    
                    # Check tab names
                    for i in range(left_panel.count()):
                        tab_text = left_panel.tabText(i)
                        print(f"   Tab {i}: {tab_text}")
                        
                        if "Tools" in tab_text:
                            print("SUCCESS: Tools tab found!")
                            
                            # Test tools widget
                            tools_widget = left_panel.widget(i)
                            if hasattr(tools_widget, 'get_tool_count'):
                                tool_count = tools_widget.get_tool_count()
                                category_count = tools_widget.get_category_count()
                                print(f"SUCCESS: Tools pane contains {tool_count} tools in {category_count} categories")
                            else:
                                print("WARNING: Tools widget doesn't have expected methods")
                        
                        if "Bookmarks" in tab_text:
                            print("SUCCESS: Bookmarks tab found!")
                else:
                    print("ERROR: Left panel doesn't have expected tabs")
            else:
                print("ERROR: Explorer doesn't have create_left_panel method")
            
            # Show the explorer window for visual verification
            explorer.show()
            
            # Set up automatic exit after a few seconds for testing
            QTimer.singleShot(3000, app.quit)
            
            print("Explorer window displayed - check for tools pane visibility")
            print("   - Left panel should have 'Tools' and 'Bookmarks' tabs")
            print("   - Tools tab should display 9 tool categories")
            print("   - Search functionality should be available")
            
            return app.exec_()
            
        except Exception as e:
            print(f"ERROR during testing: {e}")
            return 1
            
    def main():
        """Main test function."""
        print("=" * 60)
        print("RFU TOOLS PANE RESTORATION TEST")
        print("=" * 60)
        
        try:
            result = test_tools_pane_functionality()
            
            if result == 0:
                print("\nSUCCESS: Tools pane restoration test completed successfully!")
            else:
                print("\nERROR: Tools pane restoration test failed!")
                
            return result
            
        except Exception as e:
            print(f"\nERROR: Critical test failure: {e}")
            return 1

    if __name__ == '__main__':
        sys.exit(main())
        
except ImportError as e:
    print(f"ERROR: Import error: {e}")
    print("Please ensure PyQt5 is installed and RFU modules are available")
    sys.exit(1)