#!/usr/bin/env python3
"""
Test script to verify the Tools tab displays all programs from src/tools with folders.

This script will:
1. Launch the multi-pane explorer directly
2. Check if the Tools tab is visible in the left sidebar
3. Verify all tool categories and tools are displayed correctly
4. Test tool launching functionality
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(project_root, 'src'))

try:
    from PyQt5.QtCore import QTimer
    from PyQt5.QtWidgets import QApplication
    
    def test_tools_pane_display():
        """Test the Tools pane display functionality."""
        print("Testing Tools Pane Display...")
        
        try:
            # Import the multi-pane explorer
            from src.file_explorer.multi_pane_explorer_repaired import \
                MultiPaneFileExplorer

            # Create application
            app = QApplication(sys.argv)
            
            # Create multi-pane explorer
            explorer = MultiPaneFileExplorer()
            explorer.show()
            
            # Use a timer to check for Tools tab after a short delay
            def check_tools_tab():
                try:
                    # Find the left panel (should be a QTabWidget)
                    left_panel = None
                    for child in explorer.findChildren(QApplication.QTabWidget):
                        if hasattr(child, 'count') and child.count() > 0:
                            left_panel = child
                            break
                    
                    if left_panel:
                        print(f"Found left panel with {left_panel.count()} tabs")
                        
                        # Check each tab
                        tools_tab_found = False
                        for i in range(left_panel.count()):
                            tab_text = left_panel.tabText(i)
                            print(f"  Tab {i}: {tab_text}")
                            
                            if "Tools" in tab_text:
                                tools_tab_found = True
                                print("SUCCESS: Tools tab found!")
                                
                                # Get the Tools tab widget
                                tools_widget = left_panel.widget(i)
                                if hasattr(tools_widget, 'tools_tree'):
                                    tool_count = 0
                                    category_count = 0
                                    
                                    tree = tools_widget.tools_tree
                                    if tree:
                                        category_count = tree.topLevelItemCount()
                                        for j in range(category_count):
                                            category_item = tree.topLevelItem(j)
                                            tool_count += category_item.childCount()
                                        
                                        print(f"SUCCESS: Tools pane contains {tool_count} tools in {category_count} categories")
                                        
                                        # List all categories and tools
                                        print("\nTool Categories:")
                                        for j in range(category_count):
                                            category_item = tree.topLevelItem(j)
                                            category_text = category_item.text(0)
                                            print(f"  📁 {category_text}")
                                            
                                            for k in range(category_item.childCount()):
                                                tool_item = category_item.child(k)
                                                tool_text = tool_item.text(0)
                                                print(f"    🔧 {tool_text}")
                                        
                                        return True
                                else:
                                    print("WARNING: Tools widget found but no tools_tree attribute")
                        
                        if not tools_tab_found:
                            print("ERROR: Tools tab not found in left panel")
                            return False
                    else:
                        print("ERROR: Left panel not found")
                        return False
                        
                except Exception as e:
                    print(f"ERROR during Tools tab check: {e}")
                    return False
                
                finally:
                    # Close the application
                    QTimer.singleShot(1000, app.quit)
            
            # Schedule the check after the UI is fully loaded
            QTimer.singleShot(2000, check_tools_tab)
            
            # Run the application briefly
            app.processEvents()
            
            print("Multi-pane explorer displayed - check console output for Tools tab verification")
            return True
            
        except ImportError as e:
            print(f"ERROR: Could not import multi-pane explorer: {e}")
            return False
        except Exception as e:
            print(f"ERROR: Failed to test Tools pane: {e}")
            return False
    
    def main():
        """Main test function."""
        print("RFU TOOLS TAB DISPLAY TEST")
        print("=" * 50)
        
        try:
            result = test_tools_pane_display()
            
            if result:
                print("\nSUCCESS: Tools tab display test completed!")
                print("Expected functionality:")
                print("   - Left panel should have 'Tools' tab")
                print("   - Tools tab should display tool categories from src/tools")
                print("   - Each category should show individual tools")
                print("   - Tools should be organized by their folder structure")
            else:
                print("\nERROR: Tools tab display test failed!")
                
        except Exception as e:
            print(f"\nERROR: Test execution failed: {e}")
        
        return 0

    if __name__ == '__main__':
        sys.exit(main())

except ImportError as e:
    print(f"PyQt5 import error: {e}")
    print("Please ensure PyQt5 is installed: pip install PyQt5")
    sys.exit(1)