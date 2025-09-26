#!/usr/bin/env python3
"""
Tree Map Migration Validation Script - Phase 2 Testing

This script validates the tree_map migration to file_utilities_2 structure
by testing imports, syntax, and basic functionality.

Author: Tree Map Migration Team
Date: 2025-01-27
Version: 1.0
"""

import sys
import os
import traceback
from datetime import datetime

def test_imports():
    """Test 1: Import and Syntax Validation."""
    print("📦 Testing Import and Syntax Validation...")
    results = []
    
    # Test 1.1: Core module imports
    try:
        from file_utilities_2.core.tree_map_logic import TreeMapLogic
        print("  ✅ TreeMapLogic imported successfully")
        
        # Verify class has required methods
        required_methods = ['__init__', 'stop', 'start_scan', '_get_dir_size']
        for method in required_methods:
            if hasattr(TreeMapLogic, method):
                print(f"    ✅ Method {method} found")
            else:
                print(f"    ❌ Method {method} missing")
                results.append(f"Missing method: {method}")
        
        # Test signals
        instance = TreeMapLogic()
        required_signals = ['progress_updated', 'scan_complete', 'error_occurred', 'finished']
        for signal in required_signals:
            if hasattr(instance, signal):
                print(f"    ✅ Signal {signal} found")
            else:
                print(f"    ❌ Signal {signal} missing")
                results.append(f"Missing signal: {signal}")
                
    except Exception as e:
        error_msg = f"TreeMapLogic import failed: {str(e)}"
        print(f"  ❌ {error_msg}")
        results.append(error_msg)
    
    # Test 1.2: GUI module imports
    try:
        from file_utilities_2.gui.tree_map_gui import TreeMapGUI, TreeMapView
        print("  ✅ TreeMapGUI and TreeMapView imported successfully")
        
        from file_utilities_2.gui.standard_window import StandardWindow
        print("  ✅ StandardWindow imported successfully")
        
        from file_utilities_2.gui.themes import ThemeManager, Colors
        print("  ✅ ThemeManager and Colors imported successfully")
        
        # Verify inheritance
        if issubclass(TreeMapGUI, StandardWindow):
            print("    ✅ TreeMapGUI inherits from StandardWindow")
        else:
            error_msg = "TreeMapGUI does not inherit from StandardWindow"
            print(f"    ❌ {error_msg}")
            results.append(error_msg)
            
    except Exception as e:
        error_msg = f"GUI imports failed: {str(e)}"
        print(f"  ❌ {error_msg}")
        results.append(error_msg)
    
    # Test 1.3: PyQt5 dependencies
    try:
        from PyQt5.QtWidgets import QApplication, QMainWindow
        from PyQt5.QtCore import QThread, pyqtSignal
        from PyQt5.QtGui import QPainter, QColor
        print("  ✅ PyQt5 dependencies imported successfully")
    except Exception as e:
        error_msg = f"PyQt5 dependencies failed: {str(e)}"
        print(f"  ❌ {error_msg}")
        results.append(error_msg)
    
    return results

def test_file_structure():
    """Test 2: File Structure Validation."""
    print("\n📁 Testing File Structure...")
    results = []
    
    required_files = [
        'file_utilities_2/core/tree_map_logic.py',
        'file_utilities_2/gui/tree_map_gui.py',
        'file_utilities_2/gui/standard_window.py',
        'file_utilities_2/gui/themes.py',
        'file_utilities_2/gui/tree_map.ui'
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path} exists")
        else:
            error_msg = f"Missing file: {file_path}"
            print(f"  ❌ {error_msg}")
            results.append(error_msg)
    
    return results

def test_syntax_validation():
    """Test 3: Syntax Validation."""
    print("\n🔍 Testing Syntax Validation...")
    results = []
    
    import ast
    
    files_to_check = [
        'file_utilities_2/core/tree_map_logic.py',
        'file_utilities_2/gui/tree_map_gui.py',
        'file_utilities_2/gui/standard_window.py',
        'file_utilities_2/gui/themes.py'
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    ast.parse(f.read())
                print(f"  ✅ {file_path} syntax valid")
            except SyntaxError as e:
                error_msg = f"Syntax error in {file_path}: {str(e)}"
                print(f"  ❌ {error_msg}")
                results.append(error_msg)
        else:
            error_msg = f"File not found for syntax check: {file_path}"
            print(f"  ❌ {error_msg}")
            results.append(error_msg)
    
    return results

def test_ui_file():
    """Test 4: UI File Validation."""
    print("\n🖥️ Testing UI File...")
    results = []
    
    ui_file_path = "file_utilities_2/gui/tree_map.ui"
    
    if os.path.exists(ui_file_path):
        try:
            import xml.etree.ElementTree as ET
            tree = ET.parse(ui_file_path)
            root = tree.getroot()
            
            if root.tag == "ui":
                print(f"  ✅ {ui_file_path} is valid XML with 'ui' root")
            else:
                error_msg = f"Invalid UI file format, expected 'ui' root tag, got '{root.tag}'"
                print(f"  ❌ {error_msg}")
                results.append(error_msg)
                
            # Check for required elements
            if root.find(".//class") is not None:
                print("    ✅ UI class definition found")
            else:
                error_msg = "Missing class definition in UI file"
                print(f"    ❌ {error_msg}")
                results.append(error_msg)
                
        except Exception as e:
            error_msg = f"UI file parsing failed: {str(e)}"
            print(f"  ❌ {error_msg}")
            results.append(error_msg)
    else:
        error_msg = f"UI file not found: {ui_file_path}"
        print(f"  ❌ {error_msg}")
        results.append(error_msg)
    
    return results

def test_basic_functionality():
    """Test 5: Basic Functionality."""
    print("\n⚙️ Testing Basic Functionality...")
    results = []
    
    try:
        # Test TreeMapLogic instantiation
        from file_utilities_2.core.tree_map_logic import TreeMapLogic
        logic = TreeMapLogic()
        
        # Test initial state
        if not logic._is_running:
            print("  ✅ TreeMapLogic initial state correct")
        else:
            error_msg = "TreeMapLogic should not be running initially"
            print(f"  ❌ {error_msg}")
            results.append(error_msg)
        
        # Test stop method
        logic.stop()
        if not logic._is_running:
            print("  ✅ TreeMapLogic stop method works")
        else:
            error_msg = "TreeMapLogic stop method failed"
            print(f"  ❌ {error_msg}")
            results.append(error_msg)
            
    except Exception as e:
        error_msg = f"TreeMapLogic functionality test failed: {str(e)}"
        print(f"  ❌ {error_msg}")
        results.append(error_msg)
    
    try:
        # Test GUI instantiation (without showing)
        from file_utilities_2.gui.tree_map_gui import TreeMapGUI
        from PyQt5.QtWidgets import QApplication
        
        # Create QApplication if it doesn't exist
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        gui = TreeMapGUI()
        
        # Test required attributes
        required_attrs = ['scan_thread', 'tree_map_logic', 'scan_data', 'directory_path']
        for attr in required_attrs:
            if hasattr(gui, attr):
                print(f"    ✅ GUI attribute {attr} found")
            else:
                error_msg = f"Missing GUI attribute: {attr}"
                print(f"    ❌ {error_msg}")
                results.append(error_msg)
        
        print("  ✅ TreeMapGUI instantiation successful")
        
    except Exception as e:
        error_msg = f"TreeMapGUI functionality test failed: {str(e)}"
        print(f"  ❌ {error_msg}")
        results.append(error_msg)
    
    return results

def main():
    """Main validation function."""
    print("🚀 Tree Map Migration Validation - Phase 2")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 50)
    
    all_results = []
    
    # Run all tests
    all_results.extend(test_imports())
    all_results.extend(test_file_structure())
    all_results.extend(test_syntax_validation())
    all_results.extend(test_ui_file())
    all_results.extend(test_basic_functionality())
    
    # Summary
    print("\n📊 VALIDATION SUMMARY")
    print("=" * 50)
    
    if not all_results:
        print("✅ ALL TESTS PASSED!")
        print("🎉 Tree Map Migration Phase 2 validation successful!")
        print("\nMigration Status: PHASE_2_COMPLETED")
        print("Overall Progress: 95% Complete")
        print("Next Phase: Final Integration Testing")
        return 0
    else:
        print(f"❌ {len(all_results)} ISSUES FOUND:")
        for i, result in enumerate(all_results, 1):
            print(f"  {i}. {result}")
        print("\n🔧 Issues need to be resolved before proceeding to Phase 3")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n💥 Validation script error: {str(e)}")
        traceback.print_exc()
        sys.exit(1)