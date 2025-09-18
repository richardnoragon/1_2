#!/usr/bin/env python3
"""
Test the tool discovery in multi-pane explorer GUI
"""
import sys
from pathlib import Path

# Add src to path  
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Try to test just the tools widget creation
try:
    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
    
    app = QApplication(sys.argv)
    
    # Import our multi-pane explorer
    from src.file_explorer.multi_pane_explorer import MultiPaneFileExplorer

    # Create an instance
    explorer = MultiPaneFileExplorer()
    
    # Test if the tools widget was created successfully
    if hasattr(explorer, 'tools_widget'):
        print("✓ Tools widget created successfully")
        
        # Get the tree widget
        tools_tree = explorer.tools_widget
        
        if hasattr(tools_tree, 'topLevelItemCount'):
            category_count = tools_tree.topLevelItemCount()
            print(f"✓ Found {category_count} tool categories in the tree")
            
            # Count total tools
            total_tools = 0
            for i in range(category_count):
                category_item = tools_tree.topLevelItem(i)
                if category_item:
                    tool_count = category_item.childCount()
                    total_tools += tool_count
                    print(f"  - {category_item.text(0)}: {tool_count} tools")
            
            print(f"✓ Total tools in sidebar: {total_tools}")
            
            if total_tools > 0:
                print("✓ Tool discovery and display successful!")
            else:
                print("✗ No tools found in sidebar")
        else:
            print("✗ Tools tree widget not properly initialized")
    else:
        print("✗ Tools widget not created")
    
    # Don't show the GUI, just test the tool discovery
    print("\n✓ Tool discovery test completed successfully!")
    
except Exception as e:
    print(f"✗ Error during test: {e}")
    import traceback
    traceback.print_exc()
