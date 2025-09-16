#!/usr/bin/env python3
"""
Direct test of the multi-pane explorer with tools pane restoration.
"""

import os
import sys

# Set up encoding for Windows
if os.name == 'nt':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add src to path
project_root = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(project_root, 'src'))

try:
    from PyQt5.QtCore import QTimer
    from PyQt5.QtWidgets import QApplication
    
    print("Testing Multi-Pane Explorer Tools Pane...")
    
    app = QApplication(sys.argv)
    
    # Import and test the multi-pane explorer directly
    from src.rfu.file_explorer.multi_pane_explorer_repaired import \
        MultiPaneFileExplorer
    
    explorer = MultiPaneFileExplorer()
    
    print("Multi-pane explorer created successfully")
    
    # Test the left panel creation
    try:
        left_panel = explorer.create_left_panel()
        print(f"Left panel created with {left_panel.count()} tabs")
        
        for i in range(left_panel.count()):
            tab_text = left_panel.tabText(i)
            print(f"  Tab {i}: {tab_text}")
            
    except Exception as e:
        print(f"Error testing left panel: {e}")
    
    explorer.show()
    print("Explorer window shown - verify tools pane is visible")
    
    # Auto-close after 5 seconds for testing
    QTimer.singleShot(5000, app.quit)
    
    app.exec_()
    print("Test completed")
    
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Test error: {e}")
    sys.exit(1)