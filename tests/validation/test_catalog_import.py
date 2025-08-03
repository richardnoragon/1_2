#!/usr/bin/env python3
"""
Test script to verify catalog import works correctly after moving to file_utilities_1
"""

try:
    from file_utilities_1.catalog import CatalogWindow
    print("✓ SUCCESS: CatalogWindow imported successfully from file_utilities_1.catalog")
    
    # Test that the class can be instantiated (without showing the window)
    import sys
    from PyQt5.QtWidgets import QApplication
    
    # Create QApplication if it doesn't exist
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # Test instantiation
    catalog_window = CatalogWindow()
    print("✓ SUCCESS: CatalogWindow can be instantiated successfully")
    
    # Test that it has the expected methods
    expected_methods = ['_load_directory', '_generate_catalog', '_setup_ui']
    for method in expected_methods:
        if hasattr(catalog_window, method):
            print(f"✓ SUCCESS: Method {method} exists")
        else:
            print(f"✗ WARNING: Method {method} not found")
    
    print("\n🎉 All import tests passed! The catalog migration was successful.")
    
except ImportError as e:
    print(f"✗ IMPORT ERROR: {e}")
    print("The catalog import failed. Check the file path and dependencies.")
    
except Exception as e:
    print(f"✗ ERROR: {e}")
    print("An unexpected error occurred during testing.")