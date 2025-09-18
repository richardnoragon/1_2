#!/usr/bin/env python3
"""Simple test for Recent tab integration."""

import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

try:
    from PyQt5.QtWidgets import QApplication, QTabWidget

    from src.file_explorer.multi_pane_explorer_repaired import \
        MultiPaneFileExplorer
    
    print('✅ MultiPaneFileExplorer imported successfully')
    
    app = QApplication([])
    
    explorer = MultiPaneFileExplorer()
    print('✅ MultiPaneFileExplorer created successfully')
    
    # Check if Recent tab is integrated
    recent_widget_found = hasattr(explorer, 'recent_widget')
    print(f'Recent widget attribute: {recent_widget_found}')
    
    # Find tab widgets and check for Recent tab
    tab_widgets = explorer.findChildren(QTabWidget)
    print(f'Found {len(tab_widgets)} tab widgets')
    
    for i, tab_widget in enumerate(tab_widgets):
        tab_count = tab_widget.count()
        print(f'Tab widget {i}: {tab_count} tabs')
        
        for j in range(tab_count):
            tab_text = tab_widget.tabText(j)
            print(f'  Tab {j}: "{tab_text}"')
            
            if 'Recent' in tab_text:
                print(f'  ✅ Found Recent tab at index {j}!')
                
                # Get the widget
                recent_tab_widget = tab_widget.widget(j)
                print(f'  Recent tab widget type: {type(recent_tab_widget).__name__}')
    
    print('Integration test completed!')
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()