#!/usr/bin/env python3
"""
Test script for the Recent tab functionality in the multi-pane file explorer.

This script tests the integration of the Recent tab widget into the main explorer
and verifies that all features work correctly.
"""

import sys
import time
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication


def test_recent_tab_integration():
    """Test the Recent tab integration with the multi-pane explorer."""
    
    app = QApplication(sys.argv)
    
    try:
        # Import the enhanced explorer
        from src.file_explorer.multi_pane_explorer_repaired import \
            MultiPaneFileExplorer
        
        print("Creating MultiPaneFileExplorer...")
        explorer = MultiPaneFileExplorer()
        
        # Show the explorer
        explorer.show()
        
        # Test Recent tab functionality after a brief delay
        def test_recent_functionality():
            try:
                print("Testing Recent tab functionality...")
                
                # Check if Recent tab was created
                if hasattr(explorer, 'recent_widget') and explorer.recent_widget:
                    print("✅ Recent widget found and accessible")
                    
                    # Test adding recent directories
                    test_dirs = [
                        str(Path.home()),
                        str(Path.home() / "Documents"),
                        str(Path.home() / "Downloads")
                    ]
                    
                    for test_dir in test_dirs:
                        explorer.recent_widget.add_recent_directory(test_dir)
                        print(f"✅ Added recent directory: {test_dir}")
                    
                    # Test adding recent tools
                    test_tools = [
                        ("File Finder", "File Management", "src.tools.file_management.file_finder"),
                        ("Duplicate Finder", "Analysis", "src.tools.analysis.duplicate_finder"),
                        ("Secure Delete", "Security", "src.tools.security.secure_delete")
                    ]
                    
                    for tool_name, category, module_path in test_tools:
                        explorer.recent_widget.add_recent_tool(tool_name, category, module_path)
                        print(f"✅ Added recent tool: {tool_name}")
                    
                    print("✅ Recent tab functionality test completed successfully!")
                    
                else:
                    print("❌ Recent widget not found - check integration")
                
                # Test tab visibility
                left_panel = None
                for child in explorer.findChildren(QTabWidget):
                    if child.count() >= 3:  # Should have Tools, Bookmarks, Recent
                        left_panel = child
                        break
                
                if left_panel:
                    tab_names = []
                    for i in range(left_panel.count()):
                        tab_names.append(left_panel.tabText(i))
                    
                    print(f"✅ Found tabs: {tab_names}")
                    
                    if "⏱️ Recent" in tab_names:
                        print("✅ Recent tab is properly integrated!")
                        
                        # Switch to Recent tab
                        recent_index = tab_names.index("⏱️ Recent")
                        left_panel.setCurrentIndex(recent_index)
                        print("✅ Switched to Recent tab")
                    else:
                        print("❌ Recent tab not found in tab list")
                else:
                    print("❌ Left panel with tabs not found")
                
            except Exception as e:
                print(f"❌ Error during testing: {e}")
                import traceback
                traceback.print_exc()
        
        # Schedule the test to run after UI is fully loaded
        QTimer.singleShot(1000, test_recent_functionality)
        
        # Run for a few seconds to allow testing
        QTimer.singleShot(5000, app.quit)
        
        print("MultiPaneFileExplorer created successfully!")
        print("Window should be visible with Recent tab...")
        
        return app.exec_()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return 1
    except Exception as e:
        print(f"❌ Error creating explorer: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    # Add necessary imports
    from PyQt5.QtWidgets import QTabWidget
    
    result = test_recent_tab_integration()
    print(f"Test completed with result: {result}")
    sys.exit(result)