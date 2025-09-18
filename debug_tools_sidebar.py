#!/usr/bin/env python3
"""
Debug tool sidebar display issue in multi-pane explorer
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_tools_sidebar_display():
    """Test if tools are showing up in the sidebar"""
    print("Testing Tools Sidebar Display...")
    print("=" * 50)
    
    try:
        from PyQt5.QtWidgets import QApplication
        app = QApplication(sys.argv)
        
        # Import the multi-pane explorer
        from src.file_explorer.multi_pane_explorer import MultiPaneFileExplorer
        
        print("Creating MultiPaneFileExplorer instance...")
        explorer = MultiPaneFileExplorer()
        
        # Check if tools widget exists
        print("\n1. Checking Tools Widget Creation:")
        if hasattr(explorer, 'tools_widget'):
            print("  ✓ tools_widget attribute exists")
            tools_widget = explorer.tools_widget
            
            if tools_widget is not None:
                print("  ✓ tools_widget is not None")
                
                # Check if it's a QTreeWidget with items
                if hasattr(tools_widget, 'topLevelItemCount'):
                    count = tools_widget.topLevelItemCount()
                    print(f"  ✓ Found {count} top-level categories")
                    
                    if count > 0:
                        print("\n2. Category Details:")
                        total_tools = 0
                        for i in range(count):
                            category_item = tools_widget.topLevelItem(i)
                            if category_item:
                                category_name = category_item.text(0)
                                tool_count = category_item.childCount()
                                total_tools += tool_count
                                print(f"     {category_name}: {tool_count} tools")
                        
                        print(f"\n  ✓ Total tools: {total_tools}")
                        
                        if total_tools > 0:
                            print("\n✅ TOOLS ARE BEING DISCOVERED AND LOADED!")
                        else:
                            print("\n❌ No tools found in categories")
                    else:
                        print("\n❌ No categories found in tools widget")
                else:
                    print("  ❌ tools_widget doesn't have topLevelItemCount method")
            else:
                print("  ❌ tools_widget is None")
        else:
            print("  ❌ tools_widget attribute missing")
        
        # Check if tools widget is in the left panel
        print("\n3. Checking Left Panel Integration:")
        if hasattr(explorer, 'tools_widget'):
            # Try to find the left panel
            central_widget = explorer.centralWidget()
            if central_widget:
                print("  ✓ Central widget exists")
                
                # Look for the main splitter
                main_layout = central_widget.layout()
                if main_layout:
                    print("  ✓ Main layout exists")
                    
                    # Search for widgets in the layout
                    widget_count = main_layout.count()
                    print(f"  ✓ Layout has {widget_count} widgets")
                    
                    # Try to find the left panel (QTabWidget with Tools tab)
                    for i in range(widget_count):
                        widget = main_layout.itemAt(i).widget()
                        if widget and hasattr(widget, 'count'):  # Might be a splitter
                            print(f"     Widget {i}: {type(widget).__name__}")
                            if hasattr(widget, 'widget'):  # It's a splitter
                                for j in range(widget.count()):
                                    sub_widget = widget.widget(j)
                                    print(f"       Sub-widget {j}: {type(sub_widget).__name__}")
                                    if hasattr(sub_widget, 'tabText'):  # QTabWidget
                                        tab_count = sub_widget.count()
                                        print(f"         Tab widget with {tab_count} tabs:")
                                        for k in range(tab_count):
                                            tab_text = sub_widget.tabText(k)
                                            print(f"           Tab {k}: {tab_text}")
                                            if tab_text == "Tools":
                                                print("         ✓ Found Tools tab!")
                                                tools_tab_widget = sub_widget.widget(k)
                                                if tools_tab_widget == explorer.tools_widget:
                                                    print("         ✓ Tools tab contains correct widget!")
                                                else:
                                                    print("         ❌ Tools tab widget mismatch")
        
        # Don't show the GUI
        app.quit()
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_tools_sidebar_display()