#!/usr/bin/env python3
"""
Test script to verify the conditional grid layout interface implementation.
This script tests the dynamic behavior of layout options based on pane count.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import logging

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_layout_interface():
    """Test the conditional layout interface functionality."""
    
    app = QApplication(sys.argv)
    
    try:
        # Import the main file explorer class
        from src.rfu.file_explorer.multi_pane_explorer import \
            MultiPaneFileExplorer
        
        logger.info("Creating MultiPaneFileExplorer instance...")
        explorer = MultiPaneFileExplorer()
        
        # Test the layout combo box options for different pane counts
        logger.info("Testing layout options for different pane counts...")
        
        # Test 1 pane configuration
        logger.info("Testing 1-pane configuration...")
        explorer.set_pane_count(1)
        options_1_pane = [explorer.layout_combo.itemText(i) for i in range(explorer.layout_combo.count())]
        logger.info(f"1-pane options: {options_1_pane}")
        
        # Test 2 pane configuration
        logger.info("Testing 2-pane configuration...")
        explorer.set_pane_count(2)
        options_2_pane = [explorer.layout_combo.itemText(i) for i in range(explorer.layout_combo.count())]
        logger.info(f"2-pane options: {options_2_pane}")
        
        # Test 3 pane configuration
        logger.info("Testing 3-pane configuration...")
        explorer.set_pane_count(3)
        options_3_pane = [explorer.layout_combo.itemText(i) for i in range(explorer.layout_combo.count())]
        logger.info(f"3-pane options: {options_3_pane}")
        
        # Test 4 pane configuration  
        logger.info("Testing 4-pane configuration...")
        explorer.set_pane_count(4)
        options_4_pane = [explorer.layout_combo.itemText(i) for i in range(explorer.layout_combo.count())]
        logger.info(f"4-pane options: {options_4_pane}")
        
        # Verify expected behavior
        logger.info("Verifying expected behavior...")
        
        # Check that Grid is not available for 2 panes
        assert 'Grid' not in options_2_pane, "Grid option should not be available for 2 panes"
        logger.info("✓ Grid option correctly hidden for 2-pane configuration")
        
        # Check that Grid is available for 3+ panes
        assert 'Grid' in options_3_pane, "Grid option should be available for 3 panes"
        assert 'Grid' in options_4_pane, "Grid option should be available for 4 panes"
        logger.info("✓ Grid option correctly shown for 3+ pane configurations")
        
        # Check that Horizontal and Vertical are always available for multi-pane
        for options, count in [(options_2_pane, 2), (options_3_pane, 3), (options_4_pane, 4)]:
            assert 'Horizontal' in options, f"Horizontal should be available for {count} panes"
            assert 'Vertical' in options, f"Vertical should be available for {count} panes"
        logger.info("✓ Horizontal and Vertical options correctly available for all multi-pane configurations")
        
        # Test validation method
        logger.info("Testing layout validation...")
        
        # Set to 2 panes and test grid validation
        explorer.set_pane_count(2)
        assert not explorer._validate_layout_mode('grid'), "Grid should not be valid for 2 panes"
        assert explorer._validate_layout_mode('horizontal'), "Horizontal should be valid for 2 panes"
        assert explorer._validate_layout_mode('vertical'), "Vertical should be valid for 2 panes"
        logger.info("✓ Layout validation works correctly for 2-pane configuration")
        
        # Set to 3 panes and test all validations
        explorer.set_pane_count(3)
        assert explorer._validate_layout_mode('grid'), "Grid should be valid for 3 panes"
        assert explorer._validate_layout_mode('horizontal'), "Horizontal should be valid for 3 panes"
        assert explorer._validate_layout_mode('vertical'), "Vertical should be valid for 3 panes"
        logger.info("✓ Layout validation works correctly for 3+ pane configuration")
        
        logger.info("All tests passed! ✓")
        logger.info("Implementation successfully provides conditional grid interface")
        
        # Show the explorer briefly to verify UI
        explorer.show()
        
        # Close after a short delay
        QTimer.singleShot(2000, app.quit)
        
        return app.exec_()
        
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(test_layout_interface())