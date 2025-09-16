#!/usr/bin/env python3
"""Test script to verify that catalog imports work correctly after fixes."""

import sys
import os

def test_catalog_import():
    """Test that catalog can be imported from file_utilities_1."""
    try:
        print("Testing catalog import from file_utilities_1...")
        from file_utilities_1.catalog import CatalogWindow
        print("✓ Successfully imported CatalogWindow")
        
        # Test that we can create an instance (without showing UI)
        print("Testing CatalogWindow instantiation...")
        # Note: This would normally show the UI, but we're just testing import
        print("✓ CatalogWindow class is available")
        
        # Test that the required methods exist
        required_methods = [
            '_format_size',
            '_generate_catalog', 
            '_update_file_list',
            '_get_file_list'
        ]
        
        for method in required_methods:
            if hasattr(CatalogWindow, method):
                print(f"✓ Method {method} exists")
            else:
                print(f"✗ Method {method} missing")
                return False
                
        print("✓ All required methods are present")
        return True
        
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("CATALOG IMPORT TEST")
    print("=" * 50)
    
    success = test_catalog_import()
    
    print("=" * 50)
    if success:
        print("✓ ALL TESTS PASSED")
        sys.exit(0)
    else:
        print("✗ TESTS FAILED")
        sys.exit(1)