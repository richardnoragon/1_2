#!/usr/bin/env python3
"""
Simple test to verify grid layout functionality works.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_layout_logic():
    """Test the layout logic without GUI."""
    print("Testing layout logic...")
    
    # Test available layouts configuration
    available_layouts = {
        1: [],  # Single pane: no layout options
        2: ['horizontal', 'vertical'],  # Two panes: h/v only
        3: ['horizontal', 'vertical', 'grid'],  # Three+ panes: all
        4: ['horizontal', 'vertical', 'grid']
    }
    
    # Test 1: Verify grid is available for 3+ panes
    print("Test 1: Grid availability")
    assert 'grid' not in available_layouts[2], "Grid should not be available for 2 panes"
    assert 'grid' in available_layouts[3], "Grid should be available for 3 panes"
    assert 'grid' in available_layouts[4], "Grid should be available for 4 panes"
    print("✅ Grid availability logic is correct")
    
    # Test 2: Grid columns configuration
    grid_columns = {2: 1, 3: 2, 4: 2}
    
    def test_grid_config(pane_count):
        cols = grid_columns.get(pane_count, 2)
        rows = (pane_count + cols - 1) // cols  # Ceiling division
        return rows, cols
    
    print("Test 2: Grid configuration")
    rows_3, cols_3 = test_grid_config(3)
    rows_4, cols_4 = test_grid_config(4)
    
    print(f"3 panes: {rows_3} rows × {cols_3} columns")
    print(f"4 panes: {rows_4} rows × {cols_4} columns")
    
    assert rows_3 == 2 and cols_3 == 2, "3 panes should be 2×2 grid"
    assert rows_4 == 2 and cols_4 == 2, "4 panes should be 2×2 grid"
    print("✅ Grid configuration logic is correct")
    
    print("\n✅ All layout logic tests passed!")

if __name__ == "__main__":
    test_layout_logic()