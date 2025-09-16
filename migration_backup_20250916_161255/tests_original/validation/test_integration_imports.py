#!/usr/bin/env python3
"""
Integration test script to validate file_utilities_2 imports and dependencies.
This script will systematically test all import paths and identify missing dependencies.
"""

import sys
import os
import traceback
from pathlib import Path

# Add the current directory to Python path for testing
sys.path.insert(0, os.getcwd())

def test_import(module_path, description):
    """Test importing a specific module and return results."""
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"Module: {module_path}")
    print(f"{'='*60}")
    
    try:
        # Try to import the module
        if '.' in module_path:
            # Handle nested imports
            parts = module_path.split('.')
            module = __import__(module_path, fromlist=[parts[-1]])
        else:
            module = __import__(module_path)
        
        print(f"✅ SUCCESS: {module_path} imported successfully")
        
        # Try to get some basic info about the module
        if hasattr(module, '__file__'):
            print(f"   Location: {module.__file__}")
        if hasattr(module, '__version__'):
            print(f"   Version: {module.__version__}")
        if hasattr(module, '__all__'):
            print(f"   Exports: {module.__all__}")
            
        return True, module, None
        
    except ImportError as e:
        print(f"❌ IMPORT ERROR: {e}")
        print(f"   Traceback: {traceback.format_exc()}")
        return False, None, str(e)
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
        print(f"   Traceback: {traceback.format_exc()}")
        return False, None, str(e)

def test_specific_imports(module, imports_to_test):
    """Test specific imports from a module."""
    results = {}
    for import_name in imports_to_test:
        try:
            obj = getattr(module, import_name)
            print(f"   ✅ {import_name}: {type(obj)}")
            results[import_name] = True
        except AttributeError:
            print(f"   ❌ {import_name}: Not found")
            results[import_name] = False
    return results

def main():
    """Main testing function."""
    print("FILE UTILITIES 2 - INTEGRATION IMPORT TESTING")
    print("=" * 80)
    
    test_results = {}
    
    # Test 1: Basic package import
    success, module, error = test_import('file_utilities_2', 'Main package import')
    test_results['main_package'] = success
    
    if success:
        # Test specific exports from main package
        expected_exports = ['ChecksumLogic', 'VALID_ALGORITHMS', 'ChecksumGUI', 'ChecksumWindow', 'MyGUI']
        print(f"\nTesting specific exports from main package:")
        export_results = test_specific_imports(module, expected_exports)
        test_results['main_exports'] = export_results
    
    # Test 2: Core module imports
    success, core_module, error = test_import('file_utilities_2.core', 'Core module import')
    test_results['core_module'] = success
    
    # Test 3: Core checksum import
    success, checksum_module, error = test_import('file_utilities_2.core.check_sum', 'Core checksum module')
    test_results['core_checksum'] = success
    
    if success:
        # Test specific classes and constants
        checksum_exports = ['ChecksumLogic', 'VALID_ALGORITHMS']
        print(f"\nTesting specific exports from core.check_sum:")
        checksum_export_results = test_specific_imports(checksum_module, checksum_exports)
        test_results['checksum_exports'] = checksum_export_results
    
    # Test 4: GUI module imports
    success, gui_module, error = test_import('file_utilities_2.gui', 'GUI module import')
    test_results['gui_module'] = success
    
    # Test 5: GUI checksum_gui import
    success, gui_checksum, error = test_import('file_utilities_2.gui.check_sum_gui', 'GUI checksum_gui module')
    test_results['gui_checksum_gui'] = success
    
    # Test 6: GUI standardized import
    success, gui_std, error = test_import('file_utilities_2.gui.check_sum_standardized', 'GUI standardized module')
    test_results['gui_standardized'] = success
    
    # Test 7: Test module imports
    success, test_module, error = test_import('file_utilities_2.tests', 'Tests module import')
    test_results['tests_module'] = success
    
    # Test 8: Test checksum import
    success, test_checksum, error = test_import('file_utilities_2.tests.test_checksum', 'Test checksum module')
    test_results['test_checksum'] = success
    
    # Test 9: PyQt5 compatibility test
    success, pyqt5, error = test_import('PyQt5.QtCore', 'PyQt5 QtCore import')
    test_results['pyqt5_core'] = success
    
    success, pyqt5_widgets, error = test_import('PyQt5.QtWidgets', 'PyQt5 QtWidgets import')
    test_results['pyqt5_widgets'] = success
    
    # Summary
    print(f"\n{'='*80}")
    print("IMPORT TEST SUMMARY")
    print(f"{'='*80}")
    
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results.values() if result is True or (isinstance(result, dict) and all(result.values())))
    
    for test_name, result in test_results.items():
        if isinstance(result, dict):
            # Handle export test results
            passed = sum(result.values())
            total = len(result)
            status = "✅ PASS" if passed == total else f"⚠️  PARTIAL ({passed}/{total})"
            print(f"{test_name:25} {status}")
            if passed != total:
                for export, success in result.items():
                    if not success:
                        print(f"   - Missing: {export}")
        else:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name:25} {status}")
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests < total_tests:
        print(f"\n⚠️  ISSUES DETECTED - Some imports failed")
        print("This indicates missing dependencies or incorrect import paths.")
        return False
    else:
        print(f"\n✅ ALL IMPORTS SUCCESSFUL")
        return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)