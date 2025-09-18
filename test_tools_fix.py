#!/usr/bin/env python3
"""
Quick test to verify Tools tab functionality after fix.
"""

import os
import sys

# Add the project root to the Python path
project_root = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(project_root, 'src'))

try:
    from PyQt5.QtCore import QTimer
    from PyQt5.QtWidgets import QApplication

    # Import the multi-pane explorer
    from src.file_explorer.multi_pane_explorer_repaired import \
        MultiPaneFileExplorer
    
    def test_tools_tab():
        """Test the Tools tab functionality."""
        print("Testing Tools Tab After Fix...")
        
        app = QApplication(sys.argv)
        
        # Create multi-pane explorer
        explorer = MultiPaneFileExplorer()
        explorer.show()
        
        def check_tools_after_delay():
            try:
                print("Checking Tools tab content...")
                
                # Find Tools tab content
                from PyQt5.QtWidgets import QTabWidget
                tab_widgets = explorer.findChildren(QTabWidget)
                
                tools_found = False
                for tab_widget in tab_widgets:
                    for i in range(tab_widget.count()):
                        tab_text = tab_widget.tabText(i)
                        if "Tools" in tab_text:
                            tools_found = True
                            widget = tab_widget.widget(i)
                            
                            print(f"Found Tools tab: '{tab_text}'")
                            print(f"Widget type: {type(widget).__name__}")
                            
                            # Check if it's the real ToolsPaneWidget (not fallback)
                            if hasattr(widget, 'tool_categories'):
                                categories = widget.tool_categories
                                total_tools = sum(len(tools) for tools in categories.values())
                                print(f"SUCCESS: Real ToolsPaneWidget with {len(categories)} categories and {total_tools} tools!")
                                
                                # Print some categories for verification
                                print("Tool Categories:")
                                for cat_name, tools in list(categories.items())[:3]:
                                    print(f"  📁 {cat_name} ({len(tools)} tools)")
                                    for tool_name, _, _ in tools[:2]:
                                        print(f"    🔧 {tool_name}")
                                
                                return True
                            else:
                                print("ERROR: Tools tab is using fallback widget")
                                return False
                
                if not tools_found:
                    print("ERROR: Tools tab not found")
                    return False
                    
            except Exception as e:
                print(f"ERROR during test: {e}")
                return False
            finally:
                app.quit()
        
        # Check after UI loads
        QTimer.singleShot(3000, check_tools_after_delay)
        
        return app.exec_()
    
    if __name__ == '__main__':
        print("RFU TOOLS TAB FIX VERIFICATION")
        print("=" * 40)
        result = test_tools_tab()
        print(f"Test completed with result: {result}")

except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)