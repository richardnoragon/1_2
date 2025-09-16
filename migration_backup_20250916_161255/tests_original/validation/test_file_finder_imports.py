#!/usr/bin/env python3
"""
Comprehensive Import Testing for FileFinderWindow Migration
Phase 4, Task 12: Test all import statements and verify no circular dependencies

This script tests:
1. All import statements work correctly
2. No circular import dependencies exist
3. FileFinderWindow can be instantiated without errors
4. UI file loads correctly with the new relative path
5. Backward compatibility with FileFinder wrapper class
"""

import sys
import traceback
from pathlib import Path

def test_basic_imports():
    """Test basic import statements for FileFinderWindow."""
    print("=" * 60)
    print("TASK 12: COMPREHENSIVE IMPORT TESTING")
    print("=" * 60)
    
    results = {}
    
    # Test 1: Import from file_utilities_1 package
    print("\n1. Testing: from file_utilities_1 import FileFinderWindow")
    try:
        from file_utilities_1 import FileFinderWindow
        print("✅ SUCCESS: FileFinderWindow imported from file_utilities_1")
        results['import_from_package'] = True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        results['import_from_package'] = False
    
    # Test 2: Import from file_utilities_1.file_finder module
    print("\n2. Testing: from file_utilities_1.file_finder import FileFinderWindow")
    try:
        from file_utilities_1.file_finder import FileFinderWindow as FFW
        print("✅ SUCCESS: FileFinderWindow imported from file_utilities_1.file_finder")
        results['import_from_module'] = True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        results['import_from_module'] = False
    
    # Test 3: Backward compatibility - FileFinder wrapper
    print("\n3. Testing: from file_finder import FileFinder (backward compatibility)")
    try:
        from file_finder import FileFinder
        print("✅ SUCCESS: FileFinder imported for backward compatibility")
        results['backward_compatibility'] = True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        results['backward_compatibility'] = False
    
    return results

def test_instantiation():
    """Test FileFinderWindow instantiation."""
    print("\n" + "=" * 60)
    print("INSTANTIATION TESTING")
    print("=" * 60)
    
    results = {}
    
    # Test 4: Basic instantiation
    print("\n4. Testing: FileFinderWindow instantiation")
    try:
        from file_utilities_1 import FileFinderWindow
        window = FileFinderWindow()
        print("✅ SUCCESS: FileFinderWindow instantiated successfully")
        results['instantiation'] = True
        
        # Test if window has expected attributes
        expected_attrs = ['finder', 'config_manager', 'search_thread']
        missing_attrs = []
        for attr in expected_attrs:
            if not hasattr(window, attr):
                missing_attrs.append(attr)
        
        if missing_attrs:
            print(f"⚠️  WARNING: Missing expected attributes: {missing_attrs}")
            results['attributes'] = False
        else:
            print("✅ SUCCESS: All expected attributes present")
            results['attributes'] = True
            
    except Exception as e:
        print(f"❌ FAILED: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        results['instantiation'] = False
        results['attributes'] = False
    
    return results

def test_ui_loading():
    """Test UI file loading with new relative path."""
    print("\n" + "=" * 60)
    print("UI LOADING TESTING")
    print("=" * 60)
    
    results = {}
    
    # Test 5: UI file existence
    print("\n5. Testing: UI file existence at new location")
    ui_file_path = Path("file_utilities_1/file_finder.ui")
    if ui_file_path.exists():
        print(f"✅ SUCCESS: UI file found at {ui_file_path}")
        results['ui_file_exists'] = True
    else:
        print(f"❌ FAILED: UI file not found at {ui_file_path}")
        results['ui_file_exists'] = False
    
    # Test 6: UI loading mechanism
    print("\n6. Testing: UI loading with relative path")
    try:
        from file_utilities_1 import FileFinderWindow
        window = FileFinderWindow()
        
        # Check if UI elements are accessible
        ui_elements = ['directoryLineEdit', 'searchButton', 'resultsTable']
        missing_elements = []
        for element in ui_elements:
            if not hasattr(window, element):
                missing_elements.append(element)
        
        if missing_elements:
            print(f"⚠️  WARNING: Missing UI elements: {missing_elements}")
            results['ui_elements'] = False
        else:
            print("✅ SUCCESS: UI elements accessible")
            results['ui_elements'] = True
            
        results['ui_loading'] = True
        
    except Exception as e:
        print(f"❌ FAILED: UI loading error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        results['ui_loading'] = False
        results['ui_elements'] = False
    
    return results

def test_circular_dependencies():
    """Test for circular import dependencies."""
    print("\n" + "=" * 60)
    print("CIRCULAR DEPENDENCY TESTING")
    print("=" * 60)
    
    results = {}
    
    # Test 7: Check for circular dependencies
    print("\n7. Testing: Circular import dependencies")
    try:
        import sys
        initial_modules = set(sys.modules.keys())
        
        # Import the module
        from file_utilities_1.file_finder import FileFinderWindow
        
        # Check if any unexpected modules were loaded
        final_modules = set(sys.modules.keys())
        new_modules = final_modules - initial_modules
        
        # Filter out expected modules
        expected_new_modules = {
            'file_utilities_1', 'file_utilities_1.file_finder',
            'PyQt5.uic', 'pathlib'  # Expected imports
        }
        
        unexpected_modules = new_modules - expected_new_modules
        unexpected_modules = {m for m in unexpected_modules if m.startswith('file_utilities_1')}
        
        if unexpected_modules:
            print(f"⚠️  WARNING: Unexpected modules loaded: {unexpected_modules}")
            results['circular_deps'] = False
        else:
            print("✅ SUCCESS: No circular dependencies detected")
            results['circular_deps'] = True
            
    except Exception as e:
        print(f"❌ FAILED: Error checking circular dependencies: {e}")
        results['circular_deps'] = False
    
    return results

def test_icon_loading():
    """Test icon file loading."""
    print("\n" + "=" * 60)
    print("ICON LOADING TESTING")
    print("=" * 60)
    
    results = {}
    
    # Test 8: Icon file existence
    print("\n8. Testing: Icon files existence")
    icon_files = ['folder.png', 'search.png']
    missing_icons = []
    
    for icon in icon_files:
        icon_path = Path(f"file_utilities_1/icons/{icon}")
        if icon_path.exists():
            print(f"✅ SUCCESS: {icon} found at {icon_path}")
        else:
            print(f"❌ FAILED: {icon} not found at {icon_path}")
            missing_icons.append(icon)
    
    if missing_icons:
        results['icon_files'] = False
        print(f"⚠️  WARNING: Missing icon files: {missing_icons}")
    else:
        results['icon_files'] = True
        print("✅ SUCCESS: All required icon files present")
    
    return results

def generate_test_report(all_results):
    """Generate comprehensive test report."""
    print("\n" + "=" * 60)
    print("COMPREHENSIVE TEST REPORT - TASK 12")
    print("=" * 60)
    
    total_tests = 0
    passed_tests = 0
    
    for category, results in all_results.items():
        print(f"\n{category.upper()} RESULTS:")
        for test_name, result in results.items():
            total_tests += 1
            if result:
                passed_tests += 1
                print(f"  ✅ {test_name}: PASS")
            else:
                print(f"  ❌ {test_name}: FAIL")
    
    print(f"\n" + "=" * 60)
    print(f"OVERALL RESULTS: {passed_tests}/{total_tests} tests passed")
    print(f"SUCCESS RATE: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED - TASK 12 COMPLETED SUCCESSFULLY")
        return True
    else:
        print("⚠️  SOME TESTS FAILED - ISSUES NEED RESOLUTION")
        return False

def main():
    """Main test execution function."""
    print("Starting Comprehensive Import Testing for FileFinderWindow Migration")
    print("Phase 4, Task 12: Import Testing and Validation")
    
    all_results = {}
    
    # Run all test categories
    all_results['basic_imports'] = test_basic_imports()
    all_results['instantiation'] = test_instantiation()
    all_results['ui_loading'] = test_ui_loading()
    all_results['circular_deps'] = test_circular_dependencies()
    all_results['icon_loading'] = test_icon_loading()
    
    # Generate final report
    success = generate_test_report(all_results)
    
    return success, all_results

if __name__ == "__main__":
    success, results = main()
    sys.exit(0 if success else 1)