#!/usr/bin/env python3
"""Test script to verify File Catalog button functionality.

This script tests the File Catalog imports only.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


def test_catalog_imports():
    """Test that both catalog implementations can be imported."""
    print("Testing catalog imports...")
    
    try:
        # Test simple catalog
        from src.utilities.file_operations.catalog.catalog import CatalogWindow
        print("✓ Simple catalog import successful")
        simple_ok = True
    except ImportError as e:
        print(f"✗ Simple catalog import failed: {e}")
        simple_ok = False
    
    try:
        # Test advanced catalog
        from src.utilities.file_management.advanced_catalog.advanced_catalog_window import AdvancedCatalogWindow
        print("✓ Advanced catalog import successful")
        advanced_ok = True
    except ImportError as e:
        print(f"✗ Advanced catalog import failed: {e}")
        advanced_ok = False
    
    return simple_ok and advanced_ok


def main():
    """Run import tests."""
    print("File Catalog Button Fix - Import Test")
    print("=" * 50)
    
    # Test imports
    imports_ok = test_catalog_imports()
    
    print("\n" + "=" * 50)
    print(f"Import Test: {'PASS' if imports_ok else 'FAIL'}")
    
    if imports_ok:
        print("\n✓ All imports successful! File Catalog button should work.")
        print("\nTo test the button:")
        print("1. Run: python -m src.rfu.simple_hub")
        print("2. Go to the Analysis tab")
        print("3. Click the '🗂️ File Catalog' button")
        print("4. The File Catalog Generator window should open")
        return 0
    else:
        print("\n✗ Import test failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())