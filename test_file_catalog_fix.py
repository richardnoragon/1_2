#!/usr/bin/env python3
"""Test script to verify File Catalog button functionality.

This script tests the File Catalog button in the Analysis tab to ensure
it launches the correct program when clicked.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_catalog_imports():
    """Test that both catalog implementations can be imported."""
    print("Testing catalog imports...")
    
    try:
        # Test simple catalog
        from src.utilities.file_operations.catalog.catalog import CatalogWindow
        print("✓ Simple catalog import successful")
    except ImportError as e:
        print(f"✗ Simple catalog import failed: {e}")
        return False
    
    try:
        # Test advanced catalog
        from src.utilities.file_management.advanced_catalog.advanced_catalog_window import AdvancedCatalogWindow
        print("✓ Advanced catalog import successful")
    except ImportError as e:
        print(f"✗ Advanced catalog import failed: {e}")
        return False
    
    return True

def test_hub_integration():
    """Test that the hub can create catalog windows."""
    print("\nTesting hub integration...")
    
    try:
        from PyQt5.QtWidgets import QApplication
        app = QApplication(sys.argv)
        
        # Import the hub
        from src.rfu.simple_hub import SimpleRFUHub
        hub = SimpleRFUHub()
        
        print("✓ Hub created successfully")
        
        # Test the file catalog method
        try:
            hub.open_file_catalog()
            print("✓ File catalog method executed without errors")
            
            # Check if catalog window was created
            if hasattr(hub, 'file_catalog_window') and hub.file_catalog_window is not None:
                print("✓ File catalog window created successfully")
                print(f"  Window type: {type(hub.file_catalog_window).__name__}")
                return True
            else:
                print("✗ File catalog window was not created")
                return False
                
        except Exception as e:
            print(f"✗ File catalog method failed: {e}")
            return False
            
    except Exception as e:
        print(f"✗ Hub integration test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("File Catalog Button Fix - Test Suite")
    print("=" * 50)
    
    # Test imports
    imports_ok = test_catalog_imports()
    
    # Test hub integration
    integration_ok = test_hub_integration()
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"Imports: {'PASS' if imports_ok else 'FAIL'}")
    print(f"Integration: {'PASS' if integration_ok else 'FAIL'}")
    
    if imports_ok and integration_ok:
        print("\n✓ All tests passed! File Catalog button should work correctly.")
        print("\nInstructions:")
        print("1. Run the RFU Hub: python -m src.rfu.simple_hub")
        print("2. Go to the Analysis tab")
        print("3. Click the '🗂️ File Catalog' button")
        print("4. The File Catalog Generator window should open")
        return 0
    else:
        print("\n✗ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())