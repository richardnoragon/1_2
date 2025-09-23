#!/usr/bin/env python3
"""
Test script for multi-pane explorer grid layout functionality.
This script tests the reported issues with 3-pane grid layout.
"""

import logging
import sys
import time
from pathlib import Path

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.file_explorer.multi_pane_explorer import MultiPaneFileExplorer


def setup_logging():
    """Setup logging for test output."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def test_grid_layout_scenarios(explorer):
    """Test various grid layout scenarios."""
    print("\n=== Testing Grid Layout Scenarios ===")
    
    # Test 1: Start with 2 panes, try to select grid (should not be available)
    print("\nTest 1: Grid availability with 2 panes")
    explorer.set_pane_count(2)
    time.sleep(0.1)
    
    # Check if grid is available in combo box
    if hasattr(explorer, 'layout_combo') and explorer.layout_combo:
        combo_items = [explorer.layout_combo.itemText(i) 
                      for i in range(explorer.layout_combo.count())]
        print(f"Available layouts for 2 panes: {combo_items}")
        grid_available = "Grid" in combo_items
        print(f"Grid available for 2 panes: {grid_available}")
        assert not grid_available, "Grid should not be available for 2 panes"
    
    # Test 2: Switch to 3 panes and verify grid becomes available
    print("\nTest 2: Grid availability with 3 panes")
    explorer.set_pane_count(3)
    time.sleep(0.2)
    
    if hasattr(explorer, 'layout_combo') and explorer.layout_combo:
        combo_items = [explorer.layout_combo.itemText(i) 
                      for i in range(explorer.layout_combo.count())]
        print(f"Available layouts for 3 panes: {combo_items}")
        grid_available = "Grid" in combo_items
        print(f"Grid available for 3 panes: {grid_available}")
        assert grid_available, "Grid should be available for 3 panes"
    
    # Test 3: Select grid layout for 3 panes
    print("\nTest 3: Selecting grid layout for 3 panes")
    if hasattr(explorer, 'layout_combo') and explorer.layout_combo:
        grid_index = explorer.layout_combo.findText("Grid")
        if grid_index >= 0:
            explorer.layout_combo.setCurrentIndex(grid_index)
            time.sleep(0.3)
            print(f"Selected grid layout, current mode: {explorer.layout_mode}")
            print(f"Pane splitter widget count: {explorer.pane_splitter.count()}")
            assert explorer.layout_mode == 'grid', "Layout mode should be 'grid'"
        else:
            print("ERROR: Grid option not found in combo box!")
    
    # Test 4: Switch to 4 panes and verify grid works
    print("\nTest 4: Grid layout with 4 panes")
    explorer.set_pane_count(4)
    time.sleep(0.2)
    
    if hasattr(explorer, 'layout_combo') and explorer.layout_combo:
        grid_index = explorer.layout_combo.findText("Grid")
        if grid_index >= 0:
            explorer.layout_combo.setCurrentIndex(grid_index)
            time.sleep(0.3)
            print(f"4-pane grid layout, current mode: {explorer.layout_mode}")
            print(f"Pane splitter widget count: {explorer.pane_splitter.count()}")
            assert explorer.layout_mode == 'grid', "Layout mode should be 'grid'"
        else:
            print("ERROR: Grid option not found for 4 panes!")
    
    # Test 5: Rapid layout switching (robustness test)
    print("\nTest 5: Rapid layout switching test")
    layouts_to_test = ["Horizontal", "Vertical", "Grid", "Horizontal", "Grid", "Vertical"]
    
    for i, layout in enumerate(layouts_to_test):
        print(f"  Switching to {layout} (iteration {i+1})")
        if hasattr(explorer, 'layout_combo') and explorer.layout_combo:
            layout_index = explorer.layout_combo.findText(layout)
            if layout_index >= 0:
                explorer.layout_combo.setCurrentIndex(layout_index)
                time.sleep(0.1)  # Short delay between switches
                print(f"    Current mode: {explorer.layout_mode}")
                print(f"    Splitter count: {explorer.pane_splitter.count()}")
                
                # Verify layout was applied correctly
                expected_mode = layout.lower()
                if explorer.layout_mode != expected_mode:
                    print(f"    WARNING: Expected {expected_mode}, got {explorer.layout_mode}")
            else:
                print(f"    ERROR: {layout} not found in combo box!")
    
    # Test 6: Switch back to 3 panes from 4 panes with grid
    print("\nTest 6: Switching from 4 to 3 panes with grid")
    explorer.set_pane_count(4)
    time.sleep(0.1)
    
    # Set to grid
    if hasattr(explorer, 'layout_combo') and explorer.layout_combo:
        grid_index = explorer.layout_combo.findText("Grid")
        if grid_index >= 0:
            explorer.layout_combo.setCurrentIndex(grid_index)
            time.sleep(0.1)
    
    # Now switch to 3 panes
    explorer.set_pane_count(3)
    time.sleep(0.2)
    print(f"After switching to 3 panes: mode={explorer.layout_mode}")
    print(f"Pane count: {len(explorer.panes)}")
    print(f"Splitter count: {explorer.pane_splitter.count()}")
    
    print("\n=== Grid Layout Tests Completed ===")

def main():
    """Main test function."""
    setup_logging()
    
    app = QApplication(sys.argv)
    
    print("Creating MultiPaneFileExplorer...")
    explorer = MultiPaneFileExplorer()
    explorer.show()
    
    # Wait for initialization
    def run_tests():
        try:
            test_grid_layout_scenarios(explorer)
            print("\n✅ All grid layout tests completed successfully!")
        except Exception as e:
            print(f"\n❌ Test failed with error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Close the application after a short delay
            QTimer.singleShot(2000, app.quit)
    
    # Run tests after a short delay to allow UI initialization
    QTimer.singleShot(1000, run_tests)
    
    # Start the event loop
    app.exec_()

if __name__ == "__main__":
    main()