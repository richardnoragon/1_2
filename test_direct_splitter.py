#!/usr/bin/env python3
"""
Direct test of QSplitter functionality to isolate the issue.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
project_root = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(project_root, 'src'))

try:
    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import (QApplication, QLabel, QSplitter, QVBoxLayout,
                                 QWidget)

    from src.file_explorer.ui.file_explorer_pane import FileExplorerPane
    from src.file_explorer.ui.pane_manager import (PaneConfiguration,
                                                       PaneType)
    
    def test_splitter_direct():
        print("Testing QSplitter and FileExplorerPane directly...")
        
        app = QApplication(sys.argv)
        
        # Test 1: Basic QSplitter creation
        print("\n=== Test 1: QSplitter Creation ===")
        splitter = QSplitter(Qt.Horizontal)
        print(f"Created splitter: {type(splitter).__name__}")
        print(f"Initial count: {splitter.count()}")
        
        # Test 2: Simple widget addition
        print("\n=== Test 2: Simple Widget Addition ===")
        label1 = QLabel("Test Widget 1")
        label2 = QLabel("Test Widget 2")
        
        splitter.addWidget(label1)
        splitter.addWidget(label2)
        print(f"After adding 2 labels: {splitter.count()}")
        
        # Test 3: FileExplorerPane creation
        print("\n=== Test 3: FileExplorerPane Creation ===")
        try:
            config1 = PaneConfiguration(
                pane_id="test_pane_1",
                pane_type=PaneType.FILE_EXPLORER,
                title="Test Explorer 1"
            )
            
            config2 = PaneConfiguration(
                pane_id="test_pane_2", 
                pane_type=PaneType.FILE_EXPLORER,
                title="Test Explorer 2"
            )
            
            pane1 = FileExplorerPane(config1)
            pane2 = FileExplorerPane(config2)
            
            print(f"Created FileExplorerPane 1: {type(pane1).__name__}")
            print(f"Created FileExplorerPane 2: {type(pane2).__name__}")
            print(f"Pane 1 visible: {pane1.isVisible()}")
            print(f"Pane 2 visible: {pane2.isVisible()}")
            
        except Exception as e:
            print(f"Error creating FileExplorerPanes: {e}")
            import traceback
            traceback.print_exc()
            return 1
        
        # Test 4: Add FileExplorerPanes to new splitter
        print("\n=== Test 4: FileExplorerPane Addition ===")
        pane_splitter = QSplitter(Qt.Horizontal)
        print(f"New splitter count before: {pane_splitter.count()}")
        
        # Make panes visible before adding
        pane1.show()
        pane2.show()
        print(f"Pane 1 visible after show(): {pane1.isVisible()}")
        print(f"Pane 2 visible after show(): {pane2.isVisible()}")
        
        # Add to splitter
        pane_splitter.addWidget(pane1)
        print(f"After adding pane 1: {pane_splitter.count()}")
        
        pane_splitter.addWidget(pane2)
        print(f"After adding pane 2: {pane_splitter.count()}")
        
        # Show splitter window
        pane_splitter.show()
        pane_splitter.resize(800, 600)
        pane_splitter.setWindowTitle("Direct Splitter Test")
        
        print(f"\nFinal splitter count: {pane_splitter.count()}")
        print("SUCCESS: Direct splitter test completed!")
        
        # Process events to ensure everything is rendered
        app.processEvents()
        
        return 0
    
    if __name__ == '__main__':
        sys.exit(test_splitter_direct())

except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)