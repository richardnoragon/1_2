"""Verify that catalog migration fixes are working correctly."""

def test_import():
    """Test that catalog can be imported without errors."""
    try:
        print("Testing catalog import...")
        from file_utilities_1.catalog import CatalogWindow
        print("✓ Successfully imported CatalogWindow")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_class_methods():
    """Test that required methods exist in CatalogWindow."""
    try:
        from file_utilities_1.catalog import CatalogWindow
        
        required_methods = [
            '_format_size',
            '_generate_catalog', 
            '_update_file_list',
            '_get_file_list',
            '_check_duplicate'
        ]
        
        print("Testing class methods...")
        for method in required_methods:
            if hasattr(CatalogWindow, method):
                print(f"✓ Method {method} exists")
            else:
                print(f"✗ Method {method} missing")
                return False
                
        print("✓ All required methods are present")
        return True
        
    except Exception as e:
        print(f"✗ Method test failed: {e}")
        return False

def test_gui_imports():
    """Test that GUI imports work correctly."""
    try:
        print("Testing GUI imports...")
        from file_utilities_1.catalog import BaseWindow, get_existing_directory, show_error_dialog
        print("✓ GUI imports successful")
        return True
    except Exception as e:
        print(f"✗ GUI import failed: {e}")
        return False

def main():
    """Run all verification tests."""
    print("=" * 60)
    print("CATALOG MIGRATION VERIFICATION")
    print("=" * 60)
    
    tests = [
        ("Import Test", test_import),
        ("Class Methods Test", test_class_methods),
        ("GUI Imports Test", test_gui_imports)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 40)
        success = test_func()
        results.append((test_name, success))
    
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for test_name, success in results:
        status = "PASS" if success else "FAIL"
        print(f"{test_name}: {status}")
        if not success:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ ALL TESTS PASSED - Catalog migration fixes are working!")
    else:
        print("✗ SOME TESTS FAILED - Issues remain")
    print("=" * 60)
    
    return all_passed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)