#!/usr/bin/env python3
"""
Simple test to verify pane creation works without Unicode issues.
"""

import os
import sys

# Add the src directory to the Python path
project_root = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(project_root, 'src'))

try:
    from PyQt5.QtWidgets import QApplication

    from src.rfu.file_explorer.multi_pane_explorer import MultiPaneFileExplorer
    
    def main():
        print("Testing MultiPaneFileExplorer...")
        
        app = QApplication(sys.argv)
        
        try:
            # Create the multi-pane explorer
            window = MultiPaneFileExplorer()
            print("SUCCESS: Multi-pane explorer created")
            print(f"Window title: {window.windowTitle()}")
            print(f"Window size: {window.size().width()}x{window.size().height()}")
            
            # Check splitter type
            if hasattr(window, 'pane_splitter'):
                splitter_type = type(window.pane_splitter).__name__
                print(f"Pane splitter type: {splitter_type}")
                
                if hasattr(window.pane_splitter, 'count'):
                    print(f"Splitter widget count: {window.pane_splitter.count()}")
                else:
                    print("Splitter does not have count method")
            
            # Check panes
            if hasattr(window, 'panes') and window.panes:
                print(f"Panes created: {len(window.panes)}")
                for i, pane in enumerate(window.panes):
                    if pane:
                        pane_type = type(pane).__name__
                        print(f"  - Pane {i+1}: {pane_type}")
                        if hasattr(pane, 'config'):
                            print(f"    Config: {pane.config.pane_id}")
                    else:
                        print(f"  - Pane {i+1}: None")
            else:
                print("WARNING: No panes found or panes list empty")
            
            print("SUCCESS: Multi-pane explorer is functional!")
            
            # Show the window briefly
            window.show()
            app.processEvents()  # Process pending events
            
            return 0
            
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
            return 1
    
    if __name__ == '__main__':
        sys.exit(main())

except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure PyQt5 is installed and the project structure is correct.")
    sys.exit(1)