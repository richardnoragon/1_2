#!/usr/bin/env python3
"""
Simple test script to verify tool launching without Unicode characters
"""

import os
import sys

# Add path for imports
project_root = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(project_root, 'src'))

def test_direct_import():
    """Test direct import of tools."""
    print("Testing direct tool imports...")
    
    try:
        from src.tools.analysis.check_sum import ChecksumGUI
        print("SUCCESS: ChecksumGUI imported")
        
        # Test instantiation
        tool = ChecksumGUI(parent=None)
        print("SUCCESS: ChecksumGUI instantiated")
        tool.close()
        
        return True
    except Exception as e:
        print(f"FAILED: ChecksumGUI - {e}")
        return False

def test_safe_window():
    """Test SafeStandardWindow."""
    try:
        from src.gui.safe_standard_window import SafeStandardWindow
        print("SUCCESS: SafeStandardWindow imported")
        return True
    except Exception as e:
        print(f"FAILED: SafeStandardWindow - {e}")
        return False

if __name__ == "__main__":
    print("Simple Tool Launch Test")
    print("=" * 40)
    
    safe_window_ok = test_safe_window()
    direct_import_ok = test_direct_import()
    
    print("\nResults:")
    print(f"SafeStandardWindow: {'OK' if safe_window_ok else 'FAILED'}")
    print(f"Direct Import: {'OK' if direct_import_ok else 'FAILED'}")
    
    if safe_window_ok and direct_import_ok:
        print("All tests passed!")
        sys.exit(0)
    else:
        print("Some tests failed!")
        sys.exit(1)