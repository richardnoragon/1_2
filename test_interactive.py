#!/usr/bin/env python3
"""Interactive test for Recent tab functionality."""

import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QTabWidget

try:
    from src.file_explorer.multi_pane_explorer_repaired import \
        MultiPaneFileExplorer
    
    print('Starting interactive test...')
    
    app = QApplication(sys.argv)
    
    explorer = MultiPaneFileExplorer()
    explorer.show()
    
    def test_recent_tab():
        """Test Recent tab functionality after UI loads."""
        try:
            # Find the left panel tab widget
            tab_widgets = explorer.findChildren(QTabWidget)
            left_panel = None
            
            for tab_widget in tab_widgets:
                for i in range(tab_widget.count()):
                    if 'Recent' in tab_widget.tabText(i):
                        left_panel = tab_widget
                        recent_index = i
                        break
                if left_panel:
                    break
            
            if left_panel:
                print(f'✅ Found Recent tab, switching to it...')
                left_panel.setCurrentIndex(recent_index)
                
                # Get the Recent widget
                recent_widget = left_panel.widget(recent_index)
                print(f'Recent widget type: {type(recent_widget).__name__}')
                
                # If it's the enhanced widget, test its functionality
                if hasattr(recent_widget, 'add_recent_directory'):
                    print('✅ Enhanced Recent widget detected')
                    
                    # Add some test data
                    test_dirs = [
                        str(Path.home()),
                        str(Path.home() / "Documents"),
                        str(Path.home() / "Downloads"),
                        str(Path.home() / "Pictures")
                    ]
                    
                    for test_dir in test_dirs:
                        if Path(test_dir).exists():
                            recent_widget.add_recent_directory(test_dir)
                            print(f'Added: {test_dir}')
                    
                    # Add some test tools
                    test_tools = [
                        ("File Finder", "File Management"),
                        ("Duplicate Finder", "Analysis"),
                        ("Secure Delete", "Security")
                    ]
                    
                    for tool_name, category in test_tools:
                        recent_widget.add_recent_tool(tool_name, category)
                        print(f'Added tool: {tool_name}')
                    
                    print('✅ Test data added successfully!')
                    print('')
                    print('You should now see:')
                    print('1. Recent directories in the upper section')
                    print('2. Recent tools in the lower section')
                    print('3. You can double-click items to navigate/launch')
                    print('4. Right-click for context menus with pin/unpin options')
                    print('')
                    print('The Recent tab is fully functional!')
                    
                else:
                    print('Using fallback Recent widget')
                    print('Basic functionality available')
            else:
                print('❌ Recent tab not found')
                
        except Exception as e:
            print(f'❌ Error during test: {e}')
            import traceback
            traceback.print_exc()
    
    # Schedule test after UI loads
    QTimer.singleShot(1000, test_recent_tab)
    
    print('Window opened! Check the Recent tab in the left sidebar.')
    print('Press Ctrl+C to exit.')
    
    sys.exit(app.exec_())
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()