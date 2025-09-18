#!/usr/bin/env python3
"""
Debug test to see what's happening with the pane layout.
"""

import logging
import os
import sys

# Add the src directory to the Python path
project_root = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(project_root, 'src'))

# Configure logging to see debug messages
logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')

try:
    from PyQt5.QtWidgets import QApplication

    from src.file_explorer.multi_pane_explorer import MultiPaneFileExplorer
    
    def main():
        print("Debug testing MultiPaneFileExplorer layout...")
        
        app = QApplication(sys.argv)
        
        try:
            # Create the multi-pane explorer
            window = MultiPaneFileExplorer()
            print("SUCCESS: Multi-pane explorer created")
            
            # Check splitter and panes
            print(f"Pane splitter type: {type(window.pane_splitter).__name__}")
            print(f"Panes list length: {len(window.panes)}")
            
            if hasattr(window.pane_splitter, 'count'):
                count_before = window.pane_splitter.count()
                print(f"Splitter widget count BEFORE manual layout: {count_before}")
                
                # Try to manually trigger layout update
                print("Manually triggering layout update...")
                window._update_pane_layout()
                
                count_after = window.pane_splitter.count()
                print(f"Splitter widget count AFTER manual layout: {count_after}")
                
                # Check if panes have proper attributes
                for i, pane in enumerate(window.panes):
                    print(f"Pane {i+1} type: {type(pane).__name__}")
                    if hasattr(pane, 'config'):
                        print(f"  Config: {pane.config.pane_id}")
                    if hasattr(pane, 'isVisible'):
                        print(f"  Visible: {pane.isVisible()}")
                    if hasattr(pane, 'parent'):
                        parent = pane.parent()
                        parent_type = type(parent).__name__ if parent else "None"
                        print(f"  Parent: {parent_type}")
            
            # Show window to see visual result
            window.show()
            app.processEvents()
            
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
    sys.exit(1)