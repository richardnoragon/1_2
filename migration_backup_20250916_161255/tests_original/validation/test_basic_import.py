#!/usr/bin/env python3
"""
Basic import test for catalog migration validation
"""

def test_basic_import():
    """Test basic import of CatalogWindow from new location"""
    try:
        from file_utilities_1.catalog import CatalogWindow
        print("✅ SUCCESS: Basic CatalogWindow import works")
        return True
    except ImportError as e:
        print(f"❌ FAIL: Import error - {e}")
        return False
    except Exception as e:
        print(f"❌ FAIL: Unexpected error - {e}")
        return False

def test_class_definition():
    """Test if CatalogWindow class is properly defined"""
    try:
        from file_utilities_1.catalog import CatalogWindow
        
        # Check if class has expected methods
        expected_methods = ['__init__', 'scan_directory', 'generate_html']
        missing_methods = []
        
        for method in expected_methods:
            if not hasattr(CatalogWindow, method):
                missing_methods.append(method)
        
        if not missing_methods:
            print("✅ SUCCESS: CatalogWindow class has expected methods")
            return True
        else:
            print(f"❌ FAIL: Missing methods: {missing_methods}")
            return False
    except Exception as e:
        print(f"❌ FAIL: Error checking class definition - {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing Basic Import Validation")
    print("=" * 40)
    
    success1 = test_basic_import()
    success2 = test_class_definition()
    
    if success1 and success2:
        print("\n🎉 Basic import validation PASSED!")
    else:
        print("\n❌ Basic import validation FAILED!")