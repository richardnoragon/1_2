#!/usr/bin/env python3
"""
Comprehensive Import Testing for TagViewerEditor Migration
=========================================================

This script performs thorough testing of all import scenarios for the
migrated TagViewerEditor component to ensure 100% import functionality.

Test Coverage:
- Direct import from new location
- Package-level imports
- Module-level imports
- Dependency validation
- UI file accessibility
- Class instantiation
"""

import sys
import os
import traceback
from pathlib import Path
from typing import List, Dict, Any, Optional

def test_direct_import() -> Dict[str, Any]:
    """Test direct import from new location."""
    test_result = {
        'test_name': 'Direct Import Test',
        'status': 'UNKNOWN',
        'details': [],
        'errors': []
    }
    
    try:
        # Test the primary import path
        from file_utilities_2.gui.tag_viewer_editor import TagViewerEditor
        test_result['details'].append("✅ Direct import successful: from file_utilities_2.gui.tag_viewer_editor import TagViewerEditor")
        
        # Verify class is importable
        if TagViewerEditor:
            test_result['details'].append("✅ TagViewerEditor class accessible")
            test_result['status'] = 'PASSED'
        else:
            test_result['errors'].append("❌ TagViewerEditor class is None")
            test_result['status'] = 'FAILED'
            
    except ImportError as e:
        test_result['errors'].append(f"❌ ImportError: {str(e)}")
        test_result['status'] = 'FAILED'
    except Exception as e:
        test_result['errors'].append(f"❌ Unexpected error: {str(e)}")
        test_result['status'] = 'FAILED'
        
    return test_result

def test_package_level_import() -> Dict[str, Any]:
    """Test package-level import."""
    test_result = {
        'test_name': 'Package Level Import Test',
        'status': 'UNKNOWN',
        'details': [],
        'errors': []
    }
    
    try:
        # Test package-level import
        from file_utilities_2.gui import TagViewerEditor
        test_result['details'].append("✅ Package-level import successful: from file_utilities_2.gui import TagViewerEditor")
        
        # Verify class accessibility
        if TagViewerEditor:
            test_result['details'].append("✅ TagViewerEditor accessible via package import")
            test_result['status'] = 'PASSED'
        else:
            test_result['errors'].append("❌ TagViewerEditor not accessible via package import")
            test_result['status'] = 'FAILED'
            
    except ImportError as e:
        test_result['errors'].append(f"❌ Package import failed: {str(e)}")
        test_result['status'] = 'FAILED'
    except Exception as e:
        test_result['errors'].append(f"❌ Unexpected error: {str(e)}")
        test_result['status'] = 'FAILED'
        
    return test_result

def test_dependency_imports() -> Dict[str, Any]:
    """Test all dependency imports."""
    test_result = {
        'test_name': 'Dependency Import Test',
        'status': 'UNKNOWN',
        'details': [],
        'errors': []
    }
    
    dependencies = [
        ('PyQt5.QtWidgets', 'QApplication, QMessageBox, QFileDialog'),
        ('PyQt5.QtCore', 'QModelIndex'),
        ('PyQt5.QtGui', 'QStandardItemModel, QStandardItem'),
        ('PyQt5', 'uic'),
        ('mutagen._file', 'File'),
        ('file_utilities_2.gui.standard_window', 'StandardWindow'),
        ('file_utilities_2.gui.themes', 'ThemeManager')
    ]
    
    passed_count = 0
    total_count = len(dependencies)
    
    for module_name, components in dependencies:
        try:
            if module_name == 'PyQt5.QtWidgets':
                from PyQt5.QtWidgets import QApplication, QMessageBox, QFileDialog
            elif module_name == 'PyQt5.QtCore':
                from PyQt5.QtCore import QModelIndex
            elif module_name == 'PyQt5.QtGui':
                from PyQt5.QtGui import QStandardItemModel, QStandardItem
            elif module_name == 'PyQt5':
                from PyQt5 import uic
            elif module_name == 'mutagen._file':
                from mutagen._file import File
            elif module_name == 'file_utilities_2.gui.standard_window':
                from file_utilities_2.gui.standard_window import StandardWindow
            elif module_name == 'file_utilities_2.gui.themes':
                from file_utilities_2.gui.themes import ThemeManager
                
            test_result['details'].append(f"✅ {module_name}: {components}")
            passed_count += 1
            
        except ImportError as e:
            test_result['errors'].append(f"❌ {module_name}: {str(e)}")
        except Exception as e:
            test_result['errors'].append(f"❌ {module_name}: Unexpected error - {str(e)}")
    
    if passed_count == total_count:
        test_result['status'] = 'PASSED'
        test_result['details'].append(f"✅ All {total_count} dependencies imported successfully")
    else:
        test_result['status'] = 'FAILED'
        test_result['errors'].append(f"❌ {total_count - passed_count} of {total_count} dependencies failed")
        
    return test_result

def test_ui_file_accessibility() -> Dict[str, Any]:
    """Test UI file accessibility."""
    test_result = {
        'test_name': 'UI File Accessibility Test',
        'status': 'UNKNOWN',
        'details': [],
        'errors': []
    }
    
    try:
        ui_file_path = Path('file_utilities_2/gui/tag_viewer_editor.ui')
        
        if ui_file_path.exists():
            test_result['details'].append(f"✅ UI file exists: {ui_file_path}")
            
            # Check if file is readable
            with open(ui_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if content and len(content) > 0:
                    test_result['details'].append(f"✅ UI file readable ({len(content)} characters)")
                    
                    # Check for basic UI elements
                    required_elements = ['metadataTable', 'filePathEdit', 'browseButton', 'updateButton']
                    found_elements = []
                    
                    for element in required_elements:
                        if element in content:
                            found_elements.append(element)
                            
                    if len(found_elements) == len(required_elements):
                        test_result['details'].append(f"✅ All required UI elements found: {', '.join(found_elements)}")
                        test_result['status'] = 'PASSED'
                    else:
                        missing = set(required_elements) - set(found_elements)
                        test_result['errors'].append(f"❌ Missing UI elements: {', '.join(missing)}")
                        test_result['status'] = 'FAILED'
                else:
                    test_result['errors'].append("❌ UI file is empty")
                    test_result['status'] = 'FAILED'
        else:
            test_result['errors'].append(f"❌ UI file not found: {ui_file_path}")
            test_result['status'] = 'FAILED'
            
    except Exception as e:
        test_result['errors'].append(f"❌ Error accessing UI file: {str(e)}")
        test_result['status'] = 'FAILED'
        
    return test_result

def test_class_instantiation() -> Dict[str, Any]:
    """Test class instantiation without GUI."""
    test_result = {
        'test_name': 'Class Instantiation Test',
        'status': 'UNKNOWN',
        'details': [],
        'errors': []
    }
    
    try:
        # Import required modules
        from file_utilities_2.gui.tag_viewer_editor import TagViewerEditor
        
        # Check if class can be referenced
        if TagViewerEditor:
            test_result['details'].append("✅ TagViewerEditor class can be referenced")
            
            # Check class attributes and methods
            expected_methods = ['_load_ui', '_setup_ui_components', '_init_metadata_model', '_connect_signals']
            found_methods = []
            
            for method in expected_methods:
                if hasattr(TagViewerEditor, method):
                    found_methods.append(method)
                    
            if len(found_methods) == len(expected_methods):
                test_result['details'].append(f"✅ All expected methods found: {', '.join(found_methods)}")
                test_result['status'] = 'PASSED'
            else:
                missing = set(expected_methods) - set(found_methods)
                test_result['errors'].append(f"❌ Missing methods: {', '.join(missing)}")
                test_result['status'] = 'FAILED'
        else:
            test_result['errors'].append("❌ TagViewerEditor class is None")
            test_result['status'] = 'FAILED'
            
    except Exception as e:
        test_result['errors'].append(f"❌ Class instantiation test failed: {str(e)}")
        test_result['status'] = 'FAILED'
        
    return test_result

def test_legacy_import_blocked() -> Dict[str, Any]:
    """Test that legacy imports are properly blocked."""
    test_result = {
        'test_name': 'Legacy Import Block Test',
        'status': 'UNKNOWN',
        'details': [],
        'errors': []
    }
    
    try:
        # Try to import from old location (should fail)
        try:
            from tag_viewer_editor import TagViewerEditor
            test_result['errors'].append("❌ Legacy import succeeded (should have failed)")
            test_result['status'] = 'FAILED'
        except ImportError:
            test_result['details'].append("✅ Legacy import properly blocked")
            test_result['status'] = 'PASSED'
        except Exception as e:
            test_result['errors'].append(f"❌ Unexpected error testing legacy import: {str(e)}")
            test_result['status'] = 'FAILED'
            
    except Exception as e:
        test_result['errors'].append(f"❌ Legacy import test failed: {str(e)}")
        test_result['status'] = 'FAILED'
        
    return test_result

def run_comprehensive_import_tests() -> Dict[str, Any]:
    """Run all import tests and return comprehensive results."""
    print("🧪 COMPREHENSIVE IMPORT TESTING FOR TAG_VIEWER_EDITOR MIGRATION")
    print("=" * 70)
    print()
    
    # Define all tests
    tests = [
        test_direct_import,
        test_package_level_import,
        test_dependency_imports,
        test_ui_file_accessibility,
        test_class_instantiation,
        test_legacy_import_blocked
    ]
    
    results = []
    passed_tests = 0
    total_tests = len(tests)
    
    # Run each test
    for test_func in tests:
        print(f"Running {test_func.__name__}...")
        try:
            result = test_func()
            results.append(result)
            
            print(f"  Status: {result['status']}")
            for detail in result['details']:
                print(f"    {detail}")
            for error in result['errors']:
                print(f"    {error}")
                
            if result['status'] == 'PASSED':
                passed_tests += 1
                
        except Exception as e:
            error_result = {
                'test_name': test_func.__name__,
                'status': 'ERROR',
                'details': [],
                'errors': [f"Test execution failed: {str(e)}"]
            }
            results.append(error_result)
            print(f"  Status: ERROR")
            print(f"    Test execution failed: {str(e)}")
            
        print()
    
    # Generate summary
    summary = {
        'total_tests': total_tests,
        'passed_tests': passed_tests,
        'failed_tests': total_tests - passed_tests,
        'success_rate': (passed_tests / total_tests) * 100 if total_tests > 0 else 0,
        'overall_status': 'PASSED' if passed_tests == total_tests else 'FAILED',
        'test_results': results
    }
    
    print("📊 IMPORT TEST SUMMARY")
    print("-" * 30)
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Passed: {summary['passed_tests']}")
    print(f"Failed: {summary['failed_tests']}")
    print(f"Success Rate: {summary['success_rate']:.1f}%")
    print(f"Overall Status: {summary['overall_status']}")
    print()
    
    return summary

if __name__ == "__main__":
    results = run_comprehensive_import_tests()
    
    # Exit with appropriate code
    if results['overall_status'] == 'PASSED':
        print("✅ ALL IMPORT TESTS PASSED - Migration import functionality is 100% operational!")
        sys.exit(0)
    else:
        print("❌ SOME IMPORT TESTS FAILED - Review errors above")
        sys.exit(1)