#!/usr/bin/env python3
"""
Direct test of the MultiPaneFileExplorer to verify it works properly.
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
        print("Testing MultiPaneFileExplorer directly...")
        
        app = QApplication(sys.argv)
        
        try:
            # Create the multi-pane explorer
            window = MultiPaneFileExplorer()
            window.show()
            
            print("✅ Multi-pane explorer launched successfully!")
            print(f"   Window title: {window.windowTitle()}")
            print(f"   Window size: {window.size().width()}x{window.size().height()}")
            print(f"   Number of panes: {len(window.panes) if hasattr(window, 'panes') else 'Unknown'}")
            
            # Check if panes are created
            if hasattr(window, 'panes') and window.panes:
                print(f"   Panes created: {len(window.panes)}")
                for i, pane in enumerate(window.panes):
                    if pane:
                        print(f"   - Pane {i+1}: {type(pane).__name__}")
                    else:
                        print(f"   - Pane {i+1}: None")
            else:
                print("   ⚠️  No panes found or panes list empty")
            
            print("\n🎯 Multi-pane explorer is running with full features!")
            print("   Close the window to exit the test.")
            
            return app.exec_()
            
        except Exception as e:
            print(f"❌ Error creating multi-pane explorer: {e}")
            import traceback
            traceback.print_exc()
            return 1
    
    if __name__ == '__main__':
        sys.exit(main())

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure PyQt5 is installed and the project structure is correct.")
    sys.exit(1)