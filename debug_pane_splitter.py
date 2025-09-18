#!/usr/bin/env python3
"""
Debug pane splitter creation issue
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def debug_pane_splitter():
    """Debug the pane splitter creation issue"""
    print("Debugging Pane Splitter Creation...")
    print("=" * 50)
    
    try:
        from PyQt5.QtCore import Qt
        from PyQt5.QtWidgets import QApplication, QSplitter
        
        app = QApplication(sys.argv)
        
        print("✓ PyQt5 imports successful")
        
        # Test basic QSplitter creation
        test_splitter = QSplitter(Qt.Horizontal)
        print(f"✓ Basic QSplitter creation: {type(test_splitter).__name__}")
        
        # Now test the multi-pane explorer
        from src.file_explorer.multi_pane_explorer import MultiPaneFileExplorer
        
        print("\nTesting MultiPaneFileExplorer...")
        
        # Create instance but capture the exact error
        explorer = MultiPaneFileExplorer()
        
        print(f"✓ Explorer created: {type(explorer).__name__}")
        
        # Check pane_splitter specifically
        if hasattr(explorer, 'pane_splitter'):
            pane_splitter = explorer.pane_splitter
            print(f"✓ pane_splitter attribute exists: {pane_splitter}")
            
            if pane_splitter is not None:
                print(f"✓ pane_splitter is not None: {type(pane_splitter).__name__}")
            else:
                print("❌ pane_splitter is None - this is the problem!")
                
                # Let's debug the setup process
                print("\nDebugging setup process...")
                print("Checking if setup_main_content_area was called...")
                
                # Check central widget
                central_widget = explorer.centralWidget()
                if central_widget:
                    print("✓ Central widget exists")
                    layout = central_widget.layout()
                    if layout:
                        print("✓ Main layout exists")
                        print(f"  Layout has {layout.count()} items")
                        
                        # Look for main splitter
                        for i in range(layout.count()):
                            item = layout.itemAt(i)
                            if item and item.widget():
                                widget = item.widget()
                                print(f"  Item {i}: {type(widget).__name__}")
                                if isinstance(widget, QSplitter):
                                    print(f"    Found splitter with {widget.count()} widgets")
                                    for j in range(widget.count()):
                                        sub_widget = widget.widget(j)
                                        print(f"      Widget {j}: {type(sub_widget).__name__}")
                                        if isinstance(sub_widget, QSplitter):
                                            print(f"        This might be the pane_splitter: {sub_widget}")
                                            if sub_widget == explorer.pane_splitter:
                                                print("        ✓ This IS the pane_splitter!")
                                            else:
                                                print("        ❌ This is NOT the pane_splitter!")
                    else:
                        print("❌ Main layout is None")
                else:
                    print("❌ Central widget is None")
        else:
            print("❌ pane_splitter attribute missing")
        
        app.quit()
        
    except Exception as e:
        print(f"❌ Error during debug: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_pane_splitter()