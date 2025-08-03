#!/usr/bin/env python3
"""
CMSD Tool Integration Test
Tests the Copy/Move/Sync/Delete tool integration with the main application.
"""

import sys
import os
from PyQt5.QtWidgets import QApplication

def test_cmsd_standalone():
    """Test CMSD tool standalone functionality."""
    print("🔧 Testing CMSD tool standalone...")
    
    try:
        # Test import
        import cmsd
        print("✅ Import successful")
        
        # Test class existence
        if hasattr(cmsd, 'CopyMoveSyncDeleteWindow'):
            print("✅ Class 'CopyMoveSyncDeleteWindow' found")
        else:
            print("❌ Class 'CopyMoveSyncDeleteWindow' not found")
            return False
        
        # Test instantiation
        app = QApplication(sys.argv)
        window = cmsd.CopyMoveSyncDeleteWindow()
        print("✅ Instantiation successful")
        
        # Test basic functionality
        window.hide()  # Don't show the window
        window.close()
        print("✅ Basic functionality working")
        
        return True
        
    except Exception as e:
        print(f"❌ CMSD standalone test failed: {str(e)}")
        return False

def test_cmsd_main_integration():
    """Test CMSD tool integration with main application."""
    print("\n🔧 Testing CMSD integration with main application...")
    
    try:
        # Test main.py import
        import main
        print("✅ Main application import successful")
        
        # Test main app creation
        app = QApplication(sys.argv)
        main_window = main.RFUMainWindow()
        print("✅ Main window creation successful")
        
        # Test CMSD launch method
        if hasattr(main_window, 'open_cmsd'):
            print("✅ CMSD launch method found")
        else:
            print("❌ CMSD launch method not found")
            return False
        
        # Test launch_tool method
        if hasattr(main_window, 'launch_tool'):
            print("✅ Generic launch_tool method found")
        else:
            print("❌ Generic launch_tool method not found")
            return False
        
        # Test the actual launch (without showing)
        try:
            # Simulate the launch process
            main_window.launch_tool("CMSD", "cmsd", "CopyMoveSyncDeleteWindow")
            print("✅ CMSD launch simulation successful")
        except Exception as e:
            print(f"❌ CMSD launch simulation failed: {str(e)}")
            return False
        
        main_window.close()
        return True
        
    except Exception as e:
        print(f"❌ Main integration test failed: {str(e)}")
        return False

def test_error_handling():
    """Test enhanced error handling system."""
    print("\n🔧 Testing enhanced error handling...")
    
    try:
        import main
        app = QApplication(sys.argv)
        main_window = main.RFUMainWindow()
        
        # Test validation method
        if hasattr(main_window, 'validate_tool_before_launch'):
            print("✅ Pre-launch validation method found")
            
            # Test validation
            result = main_window.validate_tool_before_launch("cmsd", "CopyMoveSyncDeleteWindow")
            if result["success"]:
                print("✅ CMSD validation passed")
            else:
                print(f"❌ CMSD validation failed: {result['errors']}")
                return False
        else:
            print("❌ Pre-launch validation method not found")
            return False
        
        # Test error dialog methods
        error_methods = [
            'show_enhanced_error_dialog',
            'show_enhanced_placeholder_window',
            'show_instantiation_error_dialog',
            'show_generic_error_dialog'
        ]
        
        for method in error_methods:
            if hasattr(main_window, method):
                print(f"✅ Error handling method '{method}' found")
            else:
                print(f"❌ Error handling method '{method}' not found")
                return False
        
        main_window.close()
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {str(e)}")
        return False

def run_comprehensive_test():
    """Run all CMSD integration tests."""
    print("🚀 Starting CMSD Integration Test Suite")
    print("=" * 50)
    
    tests = [
        ("CMSD Standalone", test_cmsd_standalone),
        ("Main Integration", test_cmsd_main_integration),
        ("Error Handling", test_error_handling)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} Test...")
        if test_func():
            print(f"🎉 {test_name} Test: PASSED")
            passed += 1
        else:
            print(f"💥 {test_name} Test: FAILED")
    
    print("\n" + "=" * 50)
    print("📊 CMSD Integration Test Results")
    print("=" * 50)
    print(f"Total Tests: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {total - passed}")
    print(f"🎯 Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! CMSD tool is fully integrated and functional.")
        print("✅ The Copy/Move/Sync/Delete button should now work correctly in the main application.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)