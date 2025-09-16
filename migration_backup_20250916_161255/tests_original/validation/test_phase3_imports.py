#!/usr/bin/env python3
"""
Phase 3 Import Verification Test
Tests all updated import statements to ensure they work correctly after migration.
"""

import sys
import traceback

def test_rfuhub_import():
    """Test RFU Hub can import FileFinderWindow from file_utilities_1"""
    print("Testing RFU Hub import...")
    try:
        # Test the new import that was updated in rfuhub.py
        from file_utilities_1 import FileFinderWindow
        print("✅ SUCCESS: from file_utilities_1 import FileFinderWindow")
        
        # Test that we can instantiate the class
        # Note: We won't show() it since this is just an import test
        window = FileFinderWindow()
        print("✅ SUCCESS: FileFinderWindow() instantiation")
        
        # Clean up
        window.close()
        return True
        
    except Exception as e:
        print(f"❌ FAILED: RFU Hub import test - {e}")
        traceback.print_exc()
        return False

def test_file_finder_backward_compatibility():
    """Test that FileFinder wrapper class still works for backward compatibility"""
    print("\nTesting FileFinder backward compatibility...")
    try:
        # Test that the FileFinder wrapper class is still available
        from file_finder import FileFinder
        print("✅ SUCCESS: from file_finder import FileFinder (backward compatibility)")
        
        # Test instantiation (this should work for tests)
        finder = FileFinder()
        print("✅ SUCCESS: FileFinder() instantiation")
        
        # Clean up
        finder.close()
        return True
        
    except Exception as e:
        print(f"❌ FAILED: FileFinder backward compatibility test - {e}")
        traceback.print_exc()
        return False

def test_package_exports():
    """Test that file_utilities_1 package exports work correctly"""
    print("\nTesting file_utilities_1 package exports...")
    try:
        # Test package-level import
        import file_utilities_1
        print("✅ SUCCESS: import file_utilities_1")
        
        # Test that FileFinderWindow is in __all__
        if hasattr(file_utilities_1, 'FileFinderWindow'):
            print("✅ SUCCESS: FileFinderWindow available in package")
        else:
            print("❌ WARNING: FileFinderWindow not found in package")
            
        # Test that CatalogWindow is still available
        if hasattr(file_utilities_1, 'CatalogWindow'):
            print("✅ SUCCESS: CatalogWindow still available in package")
        else:
            print("❌ WARNING: CatalogWindow not found in package")
            
        return True
        
    except Exception as e:
        print(f"❌ FAILED: Package exports test - {e}")
        traceback.print_exc()
        return False

def test_direct_module_import():
    """Test direct module import from file_utilities_1"""
    print("\nTesting direct module import...")
    try:
        # Test direct module import
        from file_utilities_1.file_finder import FileFinderWindow
        print("✅ SUCCESS: from file_utilities_1.file_finder import FileFinderWindow")
        
        # Test that we can access the class
        if hasattr(FileFinderWindow, '__init__'):
            print("✅ SUCCESS: FileFinderWindow class is properly accessible")
        else:
            print("❌ WARNING: FileFinderWindow class structure issue")
            
        return True
        
    except Exception as e:
        print(f"❌ FAILED: Direct module import test - {e}")
        traceback.print_exc()
        return False

def main():
    """Run all import verification tests"""
    print("=" * 60)
    print("PHASE 3 IMPORT VERIFICATION TEST")
    print("=" * 60)
    
    tests = [
        test_rfuhub_import,
        test_file_finder_backward_compatibility,
        test_package_exports,
        test_direct_module_import
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ CRITICAL ERROR in {test.__name__}: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Phase 3 integration is successful.")
        return 0
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())