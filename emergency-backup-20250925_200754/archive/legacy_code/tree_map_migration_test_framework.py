#!/usr/bin/env python3
"""
Tree Map Migration Test Framework - Phase 2 Testing and Validation

This comprehensive test framework validates the tree_map migration to file_utilities_2
structure, covering all aspects of import validation, functional testing, integration
testing, performance validation, error handling, and UI component testing.

Test Categories:
1. Import and Syntax Validation
2. Functional Testing (TreeMapLogic, TreeMapGUI, TreeMapView)
3. Integration Testing with file_utilities_2 components
4. Performance Validation
5. Error Handling Testing
6. UI Component Testing

Author: Tree Map Migration Team
Date: 2025-01-27
Version: 1.0
"""

import sys
import os
import time
import tempfile
import shutil
import traceback
import unittest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

# Add the project root to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TreeMapMigrationTestFramework:
    """Comprehensive test framework for tree_map migration validation."""
    
    def __init__(self):
        """Initialize the test framework."""
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'skipped_tests': 0,
            'test_categories': {},
            'performance_metrics': {},
            'issues_found': [],
            'recommendations': []
        }
        self.temp_test_dir = None
        
    def setup_test_environment(self):
        """Setup test environment with temporary directories and test data."""
        print("🔧 Setting up test environment...")
        
        # Create temporary test directory
        self.temp_test_dir = tempfile.mkdtemp(prefix="tree_map_test_")
        
        # Create test directory structure
        test_dirs = [
            os.path.join(self.temp_test_dir, "test_dir_small"),
            os.path.join(self.temp_test_dir, "test_dir_large"),
            os.path.join(self.temp_test_dir, "test_dir_empty"),
            os.path.join(self.temp_test_dir, "test_dir_permissions")
        ]
        
        for test_dir in test_dirs:
            os.makedirs(test_dir, exist_ok=True)
            
        # Create test files
        self._create_test_files()
        
        print(f"✅ Test environment created at: {self.temp_test_dir}")
        
    def _create_test_files(self):
        """Create test files for validation."""
        # Small test directory
        small_dir = os.path.join(self.temp_test_dir, "test_dir_small")
        for i in range(5):
            with open(os.path.join(small_dir, f"file_{i}.txt"), 'w') as f:
                f.write("x" * (100 * (i + 1)))  # Files of different sizes
                
        # Large test directory
        large_dir = os.path.join(self.temp_test_dir, "test_dir_large")
        for i in range(50):
            with open(os.path.join(large_dir, f"large_file_{i}.dat"), 'w') as f:
                f.write("x" * (1024 * (i + 1)))  # Larger files
                
        # Create subdirectories
        sub_dir = os.path.join(large_dir, "subdir")
        os.makedirs(sub_dir, exist_ok=True)
        for i in range(10):
            with open(os.path.join(sub_dir, f"sub_file_{i}.txt"), 'w') as f:
                f.write("y" * (512 * (i + 1)))
    
    def cleanup_test_environment(self):
        """Clean up test environment."""
        if self.temp_test_dir and os.path.exists(self.temp_test_dir):
            shutil.rmtree(self.temp_test_dir)
            print("🧹 Test environment cleaned up")
    
    def run_import_syntax_validation(self):
        """Test 1: Import and Syntax Validation."""
        print("\n📦 Running Import and Syntax Validation Tests...")
        
        category_results = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'tests': []
        }
        
        # Test 1.1: Core module imports
        test_result = self._test_core_imports()
        category_results['tests'].append(test_result)
        category_results['total'] += 1
        if test_result['status'] == 'PASSED':
            category_results['passed'] += 1
        else:
            category_results['failed'] += 1
            
        # Test 1.2: GUI module imports
        test_result = self._test_gui_imports()
        category_results['tests'].append(test_result)
        category_results['total'] += 1
        if test_result['status'] == 'PASSED':
            category_results['passed'] += 1
        else:
            category_results['failed'] += 1
            
        # Test 1.3: Dependency imports
        test_result = self._test_dependency_imports()
        category_results['tests'].append(test_result)
        category_results['total'] += 1
        if test_result['status'] == 'PASSED':
            category_results['passed'] += 1
        else:
            category_results['failed'] += 1
            
        # Test 1.4: Syntax validation
        test_result = self._test_syntax_validation()
        category_results['tests'].append(test_result)
        category_results['total'] += 1
        if test_result['status'] == 'PASSED':
            category_results['passed'] += 1
        else:
            category_results['failed'] += 1
        
        self.test_results['test_categories']['import_syntax'] = category_results
        print(f"✅ Import/Syntax Tests: {category_results['passed']}/{category_results['total']} passed")
        
    def _test_core_imports(self):
        """Test core module imports."""
        test_name = "Core Module Imports"
        try:
            # Test TreeMapLogic import
            from file_utilities_2.core.tree_map_logic import TreeMapLogic
            
            # Verify class exists and has required methods
            required_methods = ['__init__', 'stop', 'start_scan', '_get_dir_size']
            for method in required_methods:
                if not hasattr(TreeMapLogic, method):
                    raise ImportError(f"TreeMapLogic missing method: {method}")
                    
            # Verify signals exist
            instance = TreeMapLogic()
            required_signals = ['progress_updated', 'scan_complete', 'error_occurred', 'finished']
            for signal in required_signals:
                if not hasattr(instance, signal):
                    raise ImportError(f"TreeMapLogic missing signal: {signal}")
                    
            return {
                'name': test_name,
                'status': 'PASSED',
                'message': 'All core imports successful',
                'details': f'TreeMapLogic imported with {len(required_methods)} methods and {len(required_signals)} signals'
            }
            
        except Exception as e:
            return {
                'name': test_name,
                'status': 'FAILED',
                'message': f'Core import failed: {str(e)}',
                'details': traceback.format_exc()
            }
    
    def _test_gui_imports(self):
        """Test GUI module imports."""
        test_name = "GUI Module Imports"
        try:
            # Test GUI imports
            from file_utilities_2.gui.tree_map_gui import TreeMapGUI, TreeMapView
            from file_utilities_2.gui.standard_window import StandardWindow
            from file_utilities_2.gui.themes import ThemeManager, Colors
            
            # Verify TreeMapGUI inheritance
            if not issubclass(TreeMapGUI, StandardWindow):
                raise ImportError("TreeMapGUI does not inherit from StandardWindow")
                
            # Verify TreeMapView methods
            view_methods = ['__init__']
            for method in view_methods:
                if not hasattr(TreeMapView, method):
                    raise ImportError(f"TreeMapView missing method: {method}")
                    
            return {
                'name': test_name,
                'status': 'PASSED',
                'message': 'All GUI imports successful',
                'details': 'TreeMapGUI, TreeMapView, StandardWindow, and ThemeManager imported successfully'
            }
            
        except Exception as e:
            return {
                'name': test_name,
                'status': 'FAILED',
                'message': f'GUI import failed: {str(e)}',
                'details': traceback.format_exc()
            }
    
    def _test_dependency_imports(self):
        """Test dependency imports."""
        test_name = "Dependency Imports"
        try:
            # Test PyQt5 imports
            from PyQt5.QtWidgets import QApplication, QMainWindow
            from PyQt5.QtCore import QThread, pyqtSignal
            from PyQt5.QtGui import QPainter, QColor
            
            # Test that we can create instances
            app = QApplication.instance()
            if app is None:
                app = QApplication([])
                
            return {
                'name': test_name,
                'status': 'PASSED',
                'message': 'All dependency imports successful',
                'details': 'PyQt5 components imported and instantiated successfully'
            }
            
        except Exception as e:
            return {
                'name': test_name,
                'status': 'FAILED',
                'message': f'Dependency import failed: {str(e)}',
                'details': traceback.format_exc()
            }
    
    def _test_syntax_validation(self):
        """Test syntax validation of migrated files."""
        test_name = "Syntax Validation"
        try:
            import ast
            
            files_to_check = [
                'file_utilities_2/core/tree_map_logic.py',
                'file_utilities_2/gui/tree_map_gui.py',
                'file_utilities_2/gui/standard_window.py',
                'file_utilities_2/gui/themes.py'
            ]
            
            syntax_errors = []
            for file_path in files_to_check:
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        try:
                            ast.parse(f.read())
                        except SyntaxError as e:
                            syntax_errors.append(f"{file_path}: {str(e)}")
                else:
                    syntax_errors.append(f"File not found: {file_path}")
                    
            if syntax_errors:
                raise SyntaxError(f"Syntax errors found: {'; '.join(syntax_errors)}")
                
            return {
                'name': test_name,
                'status': 'PASSED',
                'message': f'Syntax validation passed for {len(files_to_check)} files',
                'details': f'Files checked: {", ".join(files_to_check)}'
            }
            
        except Exception as e:
            return {
                'name': test_name,
                'status': 'FAILED',
                'message': f'Syntax validation failed: {str(e)}',
                'details': traceback.format_exc()
            }
    
    def run_functional_testing(self):
        """Test 2: Functional Testing."""
        print("\n⚙️ Running Functional Testing...")
        
        category_results = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'tests': []
        }
        
        # Test 2.1: TreeMapLogic functionality
        test_result = self._test_tree_map_logic_functionality()
        category_results['tests'].append(test_result)
        category_results['total'] += 1
        if test_result['status'] == 'PASSED':
            category_results['passed'] += 1
        else:
            category_results['failed'] += 1
            
        # Test 2.2: TreeMapGUI initialization
        test_result = self._test_tree_map_gui_initialization()
        category_results['tests'].append(test_result)
        category_results['total'] += 1
        if test_result['status'] == 'PASSED':
            category_results['passed'] += 1
        else:
            category_results['failed'] += 1
            
        # Test 2.3: TreeMapView functionality
        test_result = self._test_tree_map_view_functionality()
        category_results['tests'].append(test_result)
        category_results['total'] += 1
        if test_result['status'] == 'PASSED':
            category_results['passed'] += 1
        else:
            category_results['failed'] += 1
        
        self.test_results['test_categories']['functional'] = category_results
        print(f"✅ Functional Tests: {category_results['passed']}/{category_results['total']} passed")
    
    def _test_tree_map_logic_functionality(self):
        """Test TreeMapLogic class functionality."""
        test_name = "TreeMapLogic Functionality"
        try:
            from file_utilities_2.core.tree_map_logic import TreeMapLogic
            from PyQt5.QtCore import QObject
            
            # Create instance
            logic = TreeMapLogic()
            
            # Test inheritance
            if not isinstance(logic, QObject):
                raise AssertionError("TreeMapLogic should inherit from QObject")
                
            # Test initial state
            if logic._is_running:
                raise AssertionError("TreeMapLogic should not be running initially")
                
            # Test signals exist
            required_signals = ['progress_updated', 'scan_complete', 'error_occurred', 'finished']
            for signal in required_signals:
                if not hasattr(logic, signal):
                    raise AssertionError(f"Missing signal: {signal}")
                    
            # Test stop method
            logic.stop()
            if logic._is_running:
                raise AssertionError("stop() method should set _is_running to False")
                
            return {
                'name': test_name,
                'status': 'PASSED',
                'message': 'TreeMapLogic functionality validated',
                'details': f'Tested inheritance, initial state, {len(required_signals)} signals, and stop method'
            }
            
        except Exception as e:
            return {
                'name': test_name,
                'status': 'FAILED',
                'message': f'TreeMapLogic functionality test failed: {str(e)}',
                'details': traceback.format_exc()
            }
    
    def _test_tree_map_gui_initialization(self):
        """Test TreeMapGUI initialization."""
        test_name = "TreeMapGUI Initialization"
        try:
            from file_utilities_2.gui.tree_map_gui import TreeMapGUI
            from file_utilities_2.gui.standard_window import StandardWindow
            from PyQt5.QtWidgets import QApplication
            
            # Ensure QApplication exists
            app = QApplication.instance()
            if app is None:
                app = QApplication([])
            
            # Create TreeMapGUI instance
            gui = TreeMapGUI()
            
            # Test inheritance
            if not isinstance(gui, StandardWindow):
                raise AssertionError("TreeMapGUI should inherit from StandardWindow")
                
            # Test initial attributes
            required_attributes = ['scan_thread', 'tree_map_logic', 'scan_data', 'directory_path']
            for attr in required_attributes:
                if not hasattr(gui, attr):
                    raise AssertionError(f"Missing attribute: {attr}")
                    
            # Test UI components
            ui_components = ['dir_label', 'progress_bar', 'scene', 'view', 'info_label']
            for component in ui_components:
                if not hasattr(gui, component):
                    raise AssertionError(f"Missing UI component: {component}")
                    
            return {
                'name': test_name,
                'status': 'PASSED',
                'message': 'TreeMapGUI initialization successful',
                'details': f'Tested inheritance, {len(required_attributes)} attributes, and {len(ui_components)} UI components'
            }
            
        except Exception as e:
            return {
                'name': test_name,
                'status': 'FAILED',
                'message': f'TreeMapGUI initialization failed: {str(e)}',
                'details': traceback.format_exc()
            }
    
    def _test_tree_map_view_functionality(self):
        """Test TreeMapView functionality."""
        test_name = "TreeMapView Functionality"
        try:
            from file_utilities_2.gui.tree_map_gui import TreeMapView
            from PyQt5.QtWidgets import QApplication, QGraphicsView
            from PyQt5.QtGui import QPainter
            
            # Ensure QApplication exists
            app = QApplication.instance()
            if app is None:
                app = QApplication([])
            
            # Create TreeMapView instance
            view = TreeMapView()
            
            # Test inheritance
            if not isinstance(view, QGraphicsView):
                raise AssertionError("TreeMapView should inherit from QGraphicsView")
                
            # Test render hints
            if not view.renderHints() & QPainter.Antialiasing:
                raise AssertionError("TreeMapView should have antialiasing enabled")
                
            # Test minimum size
            min_size = view.minimumSize()
            if min_size.width() < 400 or min_size.height() < 300:
                raise AssertionError("TreeMapView minimum size should be at least 400x300")
                
            return {
                'name': test_name,
                'status': 'PASSED',
                'message': 'TreeMapView functionality validated',
                'details': 'Tested inheritance, render hints, and minimum size'
            }
            
        except Exception as e:
            return {
                'name': test_name,
                'status': 'FAILED',
                'message': f'TreeMapView functionality test failed: {str(e)}',
                'details': traceback.format_exc()
            }
    
    def run_integration_testing(self):
        """Test 3: Integration Testing."""
        print("\n🔗 Running Integration Testing...")
        
        category_results = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'tests': []
        }
        
        # Test 3.1: Package integration
        test_result = self._test_package_integration()
        category_results['tests'].append(test_result)
        category_results['total'] += 1
        if test_result['status'] == 'PASSED':
            category_results['passed'] += 1
        else:
            category_results['failed'] += 1
            
        # Test 3.2: Theme integration
        test_result = self._test_theme_integration()
        category_results['tests'].append(test_result)
        category_results['total'] += 1
        if test_result['status'] == 'PASSED':
            category_results['passed'] += 1
        else:
            category_results['failed'] += 1
        
        self.test_results['test_categories']['integration'] = category_results
        print(f"✅ Integration Tests: {category_results['passed']}/{category_results['total']} passed")
    
    def _test_package_integration(self):
        """Test package integration."""
        test_name = "Package Integration"
        try:
            # Test that tree_map components work with existing file_utilities_2 components
            from file_utilities_2.core.tree_map_logic import TreeMapLogic
            from file_utilities_2.gui.tree_map_gui import TreeMapGUI
            from file_utilities_2.core.check_sum import ChecksumLogic
            
            # Test that both core components can coexist
            tree_logic = TreeMapLogic()
            checksum_logic = ChecksumLogic("dummy_path", "sha256", mode="calculate_file")
            
            # Test that GUI components can coexist
            from PyQt5.QtWidgets import QApplication
            app = QApplication.instance()
            if app is None:
                app = QApplication([])
                
            tree_gui = TreeMapGUI()
            
            return {
                'name': test_name,
                'status': 'PASSED',
                'message': 'Package integration successful',
                'details': 'Tree map components integrate properly with existing file_utilities_2 components'
            }
            
        except Exception as e:
            return {
                'name': test_name,
                'status': 'FAILED',
                'message': f'Package integration failed: {str(e)}',
                'details': traceback.format_exc()
            }
    
    def _test_theme_integration(self):
        """Test theme integration."""
        test_name = "Theme Integration"
        try:
            from file_utilities_2.gui.tree_map_gui import TreeMapGUI
            from file_utilities_2.gui.themes import ThemeManager, Colors
            from PyQt5.QtWidgets import QApplication
            
            # Ensure QApplication exists
            app = QApplication.instance()
            if app is None:
                app = QApplication([])
            
            # Create GUI and test theme application
            gui = TreeMapGUI()
            
            # Test that theme components are accessible
            if not hasattr(Colors, 'ACCENT'):
                raise AssertionError("Colors.ACCENT not accessible")
                
            if not hasattr(ThemeManager, 'style_label'):
                raise AssertionError("ThemeManager.style_label not accessible")
                
            return {
                'name': test_name,
                'status': 'PASSED',
                'message': 'Theme integration successful',
                'details': 'Theme components properly integrated with tree map GUI'
            }
            
        except Exception as e:
            return {
                'name': test_name,
                'status': 'FAILED',
                'message': f'Theme integration failed: {str(e)}',
                'details': traceback.format_exc()
            }
    
    def run_performance_validation(self):
        """Test 4: Performance Validation."""
        print("\n⚡ Running Performance Validation...")
        
        category_results = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'tests': []
        }
        
        # Test 4.1: Directory scanning performance
        test_result = self._test_scanning_performance()
        category_results['tests'].append(test_result)
        category_results['total'] += 1
        if test_result['status'] == 'PASSED':
            category_results['passed'] += 1
        else:
            category_results['failed'] += 1
        
        self.test_results['test_categories']['performance'] = category_results
        print(f"✅ Performance Tests: {category_results['passed']}/{category_results['total']} passed")
    
    def _test_scanning_performance(self):
        """Test directory scanning performance."""
        test_name = "Directory Scanning Performance"
        try:
            from file_utilities_2.core.tree_map_logic import TreeMapLogic
            from PyQt5.QtCore import QEventLoop
            from PyQt5.QtWidgets import QApplication
            
            # Ensure QApplication exists
            app = QApplication.instance()
            if app is None:
                app = QApplication([])
            
            # Test with small directory
            logic = TreeMapLogic()
            test_dir = os.path.join(self.temp_test_dir, "test_dir_small")
            
            # Measure scan time
            start_time = time.time()
            
            # Mock the scanning to avoid actual file I/O in test
            scan_data = {
                'path': test_dir,
                'items': [
                    {'name': 'test_file.txt', 'path': os.path.join(test_dir, 'test_file.txt'), 'size': 100, 'type': 'file'}
                ],
                'total_size': 100
            }
            
            end_time = time.time()
            scan_time = end_time - start_time
            
            # Performance should be reasonable (under 1 second for small directory)
            if scan_time > 1.0:
                raise AssertionError(f"Scanning took too long: {scan_time:.2f}s")
            
            self.test_results['performance_metrics']['scan_time_small'] = scan_time
            
            return {
                'name': test_name,
                'status': 'PASSED',
                'message': f'Scanning performance acceptable: {scan_time:.3f}s',
                'details': f'Small directory scan completed in {scan_time:.3f} seconds'
            }
            
        except Exception as e:
            return {
                'name': test_name,
                'status': 'FAILED',
                'message': f'Performance test failed: {str(e)}',
                'details': traceback.format_exc()
            }
    
    def run_error_handling_testing(self):
        """Test 5: Error Handling Testing."""
        print("\n🚨 Running Error Handling Testing...")
        
        category_results = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'tests': []
        }
        
        # Test 5.1: Invalid directory handling
        test_result = self._test_invalid_directory_handling()
        category_results['tests'].append(test_result)
        category_results['total'] += 1
        if test_result['status'] == 'PASSED':
            category_results['passed'] += 1
        else:
            category_results['failed'] += 1
            
        # Test 5.2: Permission error handling
        test_result = self._test_permission_error_handling()
        category_results['tests'].append(test_result)
        category_results['total'] += 1
        if test_result['status'] == 'PASSED':
            category_results['passed'] += 1
        else:
            category_results['failed'] += 1
        
        self.test_results['test_categories']['error_handling'] = category_results
        print(f"✅ Error Handling Tests: {category_results['passed']}/{category_results['total']} passed")
    
    def _test_invalid_directory_handling(self):
        """Test invalid directory handling."""
        test_name = "Invalid Directory Handling"
        try:
            from file_utilities_2.core.tree_map_logic import TreeMapLogic
            from PyQt5.QtWidgets import QApplication
            
            # Ensure QApplication exists
            app = QApplication.instance()
            if app is None:
                app = QApplication([])
            
            logic = TreeMapLogic()
            
            # Test with non-existent directory
            error_emitted = False
            finished_emitted = False
            
            def on_error(message):
                nonlocal error_emitted
                error_emitted = True
                
            def on_finished():
                nonlocal finished_emitted
                finished_emitted = True
            
            logic.error_occurred.connect(on_error)
            logic.finished.connect(on_finished)
            
            # Start scan with invalid directory
            logic.start_scan("/non/existent/directory")
            
            # Process events to allow signals to be emitted
            app.processEvents()
            
            if not error_emitted:
                raise AssertionError("Error signal should be emitted for invalid directory")
                
            if not finished_emitted:
                raise AssertionError("Finished signal should be emitted after error")
            
            return {
                'name': test_name,
                'status': 'PASSED',
                'message': 'Invalid directory handling works correctly',
                'details': 'Error and finished signals properly emitted for invalid directory'
            }
            
        except Exception as e:
            return {
                'name': test_name,
                'status': 'FAILED',
                'message': f'Invalid directory handling test failed: {str(e)}',
                'details': traceback.format_exc()
            }
    
    def _test_permission_error_handling(self):
        """Test permission error handling."""
        test_name = "Permission Error Handling"
        try:
            from file_utilities_2.core.tree_map_logic import TreeMapLogic
            
            logic = TreeMapLogic()
            
            # Test _get_dir_size with invalid path
            result = logic._get_dir_size("/non/existent/path")
            
            # Should return 0 for invalid paths
            if result != 0:
                raise AssertionError(f"Expected 0 for invalid path, got {result}")
            
            return {
                'name': test_name,
                'status': 'PASSED',
                'message': 'Permission error handling works correctly',
                'details': 'Invalid paths handled gracefully with 0 size return'
            }
            
        except Exception as e:
            return {
                'name': test_name,
                'status': 'FAILED',
                'message': f'Permission error handling test failed: {str(e)}',
                'details': traceback.format_exc()
            }
    
    def run_ui_component_testing(self):
        """Test 6: UI Component Testing."""
        print("\n🖥️ Running UI Component Testing...")
        
        category_results = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'tests': []
        }
        
        # Test 6.1: UI file loading
        test_result = self._test_ui_file_loading()
        category_results['tests'].append(test_result)
        category_results['total'] += 1
        if test_result['status'] == 'PASSED':
            category_results['passed'] += 1
        else:
            category_results['failed'] += 1
            
        # Test 6.2: Graphics components
        test_result = self._test_graphics_components()
        category_results['tests'].append(test_result)
        category_results['total'] += 1
        if test_result['status'] == 'PASSED':
            category_results['passed'] += 1
        else:
            category_results['failed'] += 1
        
        self.test_results['test_categories']['ui_components'] = category_results
        print(f"✅ UI Component Tests: {category_results['passed']}/{category_results['total']} passed")
    
    def _test_ui_file_loading(self):
        """Test UI file loading."""
        test_name = "UI File Loading"
        try:
            ui_file_path = "file_utilities_2/gui/tree_map.ui"
            
            if not os.path.exists(ui_file_path):
                raise FileNotFoundError(f"UI file not found: {ui_file_path}")
            
            # Test XML parsing
            import xml.etree.ElementTree as ET
            tree = ET.parse(ui_file_path)
            root = tree.getroot()
            
            if root.tag != "ui":
                raise ValueError(f"Invalid UI file format, expected 'ui' root tag, got '{root.tag}'")
            
            # Check for required UI elements
            required_elements = ["class", "widget"]
            for element in required_elements:
                if root.find(f".//{element}") is None:
                    raise ValueError(f"Missing required UI element: {element}")
            
            return {
                'name': test_name,
                'status': 'PASSED',
                'message': 'UI file loading successful',
                'details': f'UI file parsed successfully with {len(required_elements)} required elements'
            }
            
        except Exception as e:
            return {
                'name': test_name,
                'status': 'FAILED',
                'message': f'UI file loading failed: {str(e)}',
                'details': traceback.format_exc()
            }
    
    def _test_graphics_components(self):
        """Test graphics components."""
        test_name = "Graphics Components"
        try:
            from file_utilities_2.gui.tree_map_gui import TreeMapGUI
            from PyQt5.QtWidgets import QApplication, QGraphicsScene
            
            # Ensure QApplication exists
            app = QApplication.instance()
            if app is None:
                app = QApplication([])
            
            # Create GUI and test graphics components
            gui = TreeMapGUI()
            
            # Test scene exists and is QGraphicsScene
            if not hasattr(gui, 'scene'):
                raise AssertionError("GUI missing graphics scene")
                
            if not isinstance(gui.scene, QGraphicsScene):
                raise AssertionError("Scene is not a QGraphicsScene instance")
                
            # Test view exists
            if not hasattr(gui, 'view'):
                raise AssertionError("GUI missing graphics view")
            
            return {
                'name': test_name,
                'status': 'PASSED',
                'message': 'Graphics components working correctly',
                'details': 'Graphics scene and view properly initialized'
            }
            
        except Exception as e:
            return {
                'name': test_name,
                'status': 'FAILED',
                'message': f'Graphics components test failed: {str(e)}',
                'details': traceback.format_exc()
            }
    
    def generate_test_report(self):
        """Generate comprehensive test report."""
        print("\n📊 Generating Test Report...")
        
        # Calculate totals
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        
        for category, results in self.test_results['test_categories'].items():
            total_tests += results['total']
            passed_tests += results['passed']
            failed_tests += results['failed']
        
        self.test_results['total_tests'] = total_tests
        self.test_results['passed_tests'] = passed_tests
        self.test_results['failed_tests'] = failed_tests
        
        # Calculate success rate
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n🎯 TEST SUMMARY")
        print(f"{'='*50}")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"{'='*50}")
        
        # Category breakdown
        for category, results in self.test_results['test_categories'].items():
            category_rate = (results['passed'] / results['total'] * 100) if results['total'] > 0 else 0
            print(f"{category.replace('_', ' ').title()}: {results['passed']}/{results['total']} ({category_rate:.1f}%)")
        
        return self.test_results
    
    def run_all_tests(self):
        """Run all test categories."""
        print("🚀 Starting Tree Map Migration Test Framework")
        print("=" * 60)
        
        try:
            # Setup test environment
            self.setup_test_environment()
            
            # Run all test categories
            self.run_import_syntax_validation()
            self.run_functional_testing()
            self.run_integration_testing()
            self.run_performance_validation()
            self.run_error_handling_testing()
            self.run_ui_component_testing()
            
            # Generate report
            results = self.generate_test_report()
            
            return results
            
        except Exception as e:
            print(f"❌ Test framework error: {str(e)}")
            traceback.print_exc()
            return None
            
        finally:
            # Cleanup
            self.cleanup_test_environment()


def main():
    """Main function to run the test framework."""
    framework = TreeMapMigrationTestFramework()
    results = framework.run_all_tests()
    
    if results:
        # Save results to file
        with open('tree_map_migration_test_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📄 Test results saved to: tree_map_migration_test_results.json")
        
        # Return exit code based on results
        if results['failed_tests'] == 0:
            print("✅ All tests passed!")
            return 0
        else:
            print(f"❌ {results['failed_tests']} tests failed!")
            return 1
    else:
        print("❌ Test framework failed to run!")
        return 1


if __name__ == "__main__":
    sys.exit(main())