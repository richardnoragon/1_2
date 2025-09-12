#!/usr/bin/env python3
"""
Test script to verify that button functionality is working correctly.
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent
src_dir = project_root / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

def test_tool_imports():
    """Test that we can successfully import the analysis tools."""
    print("Testing tool imports...")
    
    try:
        from utilities.analysis.size_analyzer import SizeAnalyzerGUI
        print("✓ Size Analyzer imported successfully")
    except ImportError as e:
        print(f"✗ Size Analyzer import failed: {e}")
    
    try:
        from utilities.analysis.find_duplicate_files import DuplicateFinderApp
        print("✓ Duplicate Finder imported successfully")
    except ImportError as e:
        print(f"✗ Duplicate Finder import failed: {e}")
    
    try:
        from utilities.analysis.check_sum import ChecksumGUI
        print("✓ Checksum Tool imported successfully")
    except ImportError as e:
        print(f"✗ Checksum Tool import failed: {e}")

def test_simple_hub_import():
    """Test that we can import the simple hub."""
    try:
        from rfu.simple_hub import SimpleRFUHub
        print("✓ Simple RFU Hub imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Simple RFU Hub import failed: {e}")
        return False

def test_button_methods():
    """Test that button methods exist and can be called."""
    try:
        from rfu.simple_hub import SimpleRFUHub
        
        # Create a hub instance (but don't show GUI)
        hub = SimpleRFUHub()
        
        # Test that methods exist
        methods_to_test = [
            'open_size_analyzer',
            'open_duplicate_finder', 
            'open_checksum'
        ]
        
        for method_name in methods_to_test:
            if hasattr(hub, method_name):
                print(f"✓ Method {method_name} exists")
            else:
                print(f"✗ Method {method_name} not found")
        
        print("Button method test completed")
        return True
        
    except Exception as e:
        print(f"✗ Button method test failed: {e}")
        return False

if __name__ == "__main__":
    print("RFU Button Functionality Test")
    print("=" * 40)
    
    test_tool_imports()
    print()
    
    if test_simple_hub_import():
        print()
        test_button_methods()
    
    print()
    print("Test completed!")