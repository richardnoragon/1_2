#!/usr/bin/env python3
"""
Additional test to verify that the layout combo gets properly populated when pane count changes.
"""

import os
import sys

# Add project root to path  
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from PyQt5.QtWidgets import QApplication

    from src.file_explorer.multi_pane_explorer import MultiPaneFileExplorer
    
    def test_layout_options_with_pane_changes():
        """Test if layout options change correctly when pane count changes."""
        app = QApplication(sys.argv) if not QApplication.instance() else QApplication.instance()
        
        # Create the multi-pane explorer
        explorer = MultiPaneFileExplorer()
        
        print("Testing Layout Options with Pane Count Changes:")
        print("=" * 50)
        
        # Test different pane counts
        for pane_count in [1, 2, 3, 4]:
            print(f"\nTesting with {pane_count} pane(s):")
            
            # Set pane count (this should trigger layout combo update)
            explorer.set_pane_count(pane_count)
            
            # Check layout combo
            if hasattr(explorer, 'layout_combo') and explorer.layout_combo:
                item_count = explorer.layout_combo.count()
                items = [explorer.layout_combo.itemText(i) for i in range(item_count)]
                is_enabled = explorer.layout_combo.isEnabled()
                
                print(f"  Layout combo items: {items}")
                print(f"  Layout combo enabled: {is_enabled}")
                print(f"  Current layout mode: {explorer.layout_mode}")
                
                # Check available layouts for this pane count
                available = explorer.available_layouts.get(pane_count, [])
                print(f"  Available layouts: {available}")
                
            else:
                print("  Layout combo not accessible!")
                
        return True
    
    if __name__ == "__main__":
        print("Testing Layout Combo Population...")
        test_layout_options_with_pane_changes()
        print("\nTest completed.")

except ImportError as e:
    print(f"Import error: {e}")
except Exception as e:
    print(f"Error during test: {e}")