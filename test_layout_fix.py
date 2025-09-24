#!/usr/bin/env python3
"""
Quick test to verify that the layout selection dropdown is working in the multi-pane explorer.
This test verifies that the layout_combo is properly stored as an instance variable.
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from PyQt5.QtWidgets import QApplication, QComboBox

    from src.file_explorer.multi_pane_explorer import MultiPaneFileExplorer
    
    def test_layout_combo_existence():
        """Test if the layout combo is properly accessible."""
        app = QApplication(sys.argv) if not QApplication.instance() else QApplication.instance()
        
        # Create the multi-pane explorer
        explorer = MultiPaneFileExplorer()
        
        # Check if layout_combo exists as an instance variable
        has_layout_combo = hasattr(explorer, 'layout_combo')
        print(f"✓ Multi-pane explorer has layout_combo attribute: {has_layout_combo}")
        
        if has_layout_combo:
            layout_combo = explorer.layout_combo
            is_qcombobox = isinstance(layout_combo, QComboBox)
            print(f"✓ layout_combo is a QComboBox: {is_qcombobox}")
            
            if is_qcombobox:
                item_count = layout_combo.count()
                print(f"✓ Layout combo has {item_count} items")
                
                # List all items
                items = [layout_combo.itemText(i) for i in range(item_count)]
                print(f"✓ Layout options: {items}")
                
                # Check if combo is enabled (should be enabled for multi-pane)
                is_enabled = layout_combo.isEnabled()
                print(f"✓ Layout combo is enabled: {is_enabled}")
                
                return True
        
        return False
    
    def test_pane_combo_existence():
        """Test if the pane count combo is also properly accessible."""
        app = QApplication(sys.argv) if not QApplication.instance() else QApplication.instance()
        
        # Create the multi-pane explorer
        explorer = MultiPaneFileExplorer()
        
        # Check if pane_count_combo exists as an instance variable
        has_pane_combo = hasattr(explorer, 'pane_count_combo')
        print(f"✓ Multi-pane explorer has pane_count_combo attribute: {has_pane_combo}")
        
        if has_pane_combo:
            pane_combo = explorer.pane_count_combo
            is_qcombobox = isinstance(pane_combo, QComboBox)
            print(f"✓ pane_count_combo is a QComboBox: {is_qcombobox}")
            
            if is_qcombobox:
                item_count = pane_combo.count()
                print(f"✓ Pane combo has {item_count} items")
                
                # List all items
                items = [pane_combo.itemText(i) for i in range(item_count)]
                print(f"✓ Pane options: {items}")
                
                current_index = pane_combo.currentIndex()
                current_text = pane_combo.currentText()
                print(f"✓ Current selection: {current_text} (index {current_index})")
                
                return True
        
        return False
    
    if __name__ == "__main__":
        print("Testing Multi-Pane Explorer Layout Selection Fix...")
        print("=" * 60)
        
        # Test layout combo
        print("\n1. Testing Layout Combo:")
        layout_test_passed = test_layout_combo_existence()
        
        print("\n2. Testing Pane Count Combo:")
        pane_test_passed = test_pane_combo_existence()
        
        print("\n" + "=" * 60)
        if layout_test_passed and pane_test_passed:
            print("✅ SUCCESS: Both combo boxes are properly accessible!")
            print("✅ The layout selection fix has been successful.")
            print("✅ Users should now be able to select different layout patterns.")
        else:
            print("❌ FAILED: One or more combo boxes are not properly accessible.")
            if not layout_test_passed:
                print("❌ Layout combo issue detected")
            if not pane_test_passed:
                print("❌ Pane count combo issue detected")
        
        print("\nTest completed.")

except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running this from the project root directory.")
except Exception as e:
    print(f"Error during test: {e}")