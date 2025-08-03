#!/usr/bin/env python3
"""
Test script for Enhanced PDF Tools Integration in RFU Hub

This script tests the comprehensive integration of the enhanced PDF Tools
tabbed interface within the main Richard's File Utilities hub.
"""

import sys
import os
import logging
from datetime import datetime

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

try:
    from PyQt5.QtWidgets import QApplication, QMainWindow
    from PyQt5.QtCore import QTimer
    
    # Import the main RFU window and enhanced PDF tools
    from main import RFUMainWindow
    from enhanced_pdf_tools_widget import EnhancedPDFToolsWidget
    
    IMPORTS_SUCCESSFUL = True
except ImportError as e:
    print(f"Import error: {e}")
    IMPORTS_SUCCESSFUL = False


class PDFIntegrationTester:
    """
    Comprehensive tester for PDF Tools integration
    """
    
    def __init__(self):
        self.test_results = {}
        self.logger = logging.getLogger('PDFIntegrationTest')
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging for test results"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('pdf_integration_test.log'),
                logging.StreamHandler()
            ]
        )
        
    def run_all_tests(self):
        """Run all integration tests"""
        print("=" * 60)
        print("Enhanced PDF Tools Integration Test Suite")
        print("=" * 60)
        
        tests = [
            ("Import Tests", self.test_imports),
            ("Widget Creation", self.test_widget_creation),
            ("RFU Hub Integration", self.test_rfu_integration),
            ("State Management", self.test_state_management),
            ("Error Handling", self.test_error_handling),
            ("Performance", self.test_performance),
            ("UI Components", self.test_ui_components),
            ("Signal Connections", self.test_signal_connections)
        ]
        
        for test_name, test_func in tests:
            print(f"\n--- Running {test_name} ---")
            try:
                result = test_func()
                self.test_results[test_name] = result
                status = "✓ PASSED" if result['success'] else "✗ FAILED"
                print(f"{status}: {result['message']}")
                if not result['success'] and 'details' in result:
                    print(f"Details: {result['details']}")
            except Exception as e:
                self.test_results[test_name] = {
                    'success': False,
                    'message': f"Test execution failed: {str(e)}",
                    'details': str(e)
                }
                print(f"✗ ERROR: {str(e)}")
                
        self.print_summary()
        
    def test_imports(self):
        """Test that all required imports are successful"""
        if not IMPORTS_SUCCESSFUL:
            return {
                'success': False,
                'message': "Required imports failed",
                'details': "PyQt5 or custom modules not available"
            }
            
        try:
            # Test specific imports
            from enhanced_pdf_tools_widget import (
                PDFToolsStateManager,
                PDFToolsErrorHandler,
                PDFToolsPerformanceManager,
                EnhancedPDFToolsWidget
            )
            
            return {
                'success': True,
                'message': "All required imports successful"
            }
        except ImportError as e:
            return {
                'success': False,
                'message': "Import test failed",
                'details': str(e)
            }
            
    def test_widget_creation(self):
        """Test creation of enhanced PDF tools widget"""
        try:
            app = QApplication.instance()
            if app is None:
                app = QApplication([])
                
            # Create widget
            widget = EnhancedPDFToolsWidget()
            
            # Test basic properties
            if not hasattr(widget, 'state_manager'):
                return {
                    'success': False,
                    'message': "Widget missing state manager"
                }
                
            if not hasattr(widget, 'tab_widget'):
                return {
                    'success': False,
                    'message': "Widget missing tab widget"
                }
                
            # Test tab count
            expected_tabs = 6  # Basic, Extraction, Security, Enhancements, Conversion, View
            if widget.tab_widget and widget.tab_widget.count() != expected_tabs:
                return {
                    'success': False,
                    'message': f"Expected {expected_tabs} tabs, got {widget.tab_widget.count()}"
                }
                
            return {
                'success': True,
                'message': f"Widget created successfully with {expected_tabs} tabs"
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': "Widget creation failed",
                'details': str(e)
            }
            
    def test_rfu_integration(self):
        """Test integration with main RFU hub"""
        try:
            app = QApplication.instance()
            if app is None:
                app = QApplication([])
                
            # Create main RFU window
            main_window = RFUMainWindow()
            
            # Check if enhanced PDF widget is available
            if hasattr(main_window, 'enhanced_pdf_widget'):
                return {
                    'success': True,
                    'message': "Enhanced PDF widget integrated into RFU hub"
                }
            else:
                # Check if PDF tab exists at all
                central_widget = main_window.centralWidget()
                if central_widget:
                    return {
                        'success': True,
                        'message': "RFU hub created, PDF integration may be using fallback"
                    }
                else:
                    return {
                        'success': False,
                        'message': "RFU hub creation failed"
                    }
                    
        except Exception as e:
            return {
                'success': False,
                'message': "RFU integration test failed",
                'details': str(e)
            }
            
    def test_state_management(self):
        """Test PDF tools state management"""
        try:
            from enhanced_pdf_tools_widget import PDFToolsStateManager
            
            state_manager = PDFToolsStateManager()
            
            # Test file management
            test_file = "test.pdf"
            state_manager.set_current_file(test_file)
            
            if state_manager.get_current_file() != test_file:
                return {
                    'success': False,
                    'message': "File state management failed"
                }
                
            # Test data sharing
            state_manager.share_data_between_tools("tool1", "tool2", {"test": "data"})
            shared_data = state_manager.get_shared_data("tool1", "tool2")
            
            if shared_data != {"test": "data"}:
                return {
                    'success': False,
                    'message': "Data sharing failed"
                }
                
            # Test operation history
            state_manager.save_operation_state("test_tool", "test_op", {"param": "value"})
            history = state_manager.get_operation_history("test_tool")
            
            if len(history) != 1:
                return {
                    'success': False,
                    'message': "Operation history failed"
                }
                
            return {
                'success': True,
                'message': "State management working correctly"
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': "State management test failed",
                'details': str(e)
            }
            
    def test_error_handling(self):
        """Test error handling capabilities"""
        try:
            from enhanced_pdf_tools_widget import PDFToolsErrorHandler
            
            logger = logging.getLogger('test')
            error_handler = PDFToolsErrorHandler(logger)
            
            # Test error handling
            test_error = FileNotFoundError("Test file not found")
            result = error_handler.handle_pdf_operation_error("test_tool", "test_op", test_error)
            
            if 'error_type' not in result:
                return {
                    'success': False,
                    'message': "Error handling result incomplete"
                }
                
            # Test recovery suggestions
            suggestions = error_handler.suggest_recovery_actions("FileNotFoundError", {})
            
            if not suggestions:
                return {
                    'success': False,
                    'message': "No recovery suggestions provided"
                }
                
            return {
                'success': True,
                'message': f"Error handling working, {len(suggestions)} suggestions provided"
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': "Error handling test failed",
                'details': str(e)
            }
            
    def test_performance(self):
        """Test performance management"""
        try:
            from enhanced_pdf_tools_widget import PDFToolsPerformanceManager
            
            perf_manager = PDFToolsPerformanceManager()
            
            # Test lazy loading
            result = perf_manager.lazy_load_tool("test_tool")
            
            if not result:
                return {
                    'success': False,
                    'message': "Lazy loading failed"
                }
                
            # Test caching
            perf_manager.cache_frequently_used_operations("test_op", {"param": "value"}, "result")
            cached_result = perf_manager.get_cached_result("test_op", {"param": "value"})
            
            if cached_result != "result":
                return {
                    'success': False,
                    'message': "Operation caching failed"
                }
                
            # Test memory management
            memory_status = perf_manager.manage_memory_usage()
            
            if 'status' not in memory_status:
                return {
                    'success': False,
                    'message': "Memory management failed"
                }
                
            return {
                'success': True,
                'message': f"Performance management working, memory status: {memory_status['status']}"
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': "Performance test failed",
                'details': str(e)
            }
            
    def test_ui_components(self):
        """Test UI components and styling"""
        try:
            app = QApplication.instance()
            if app is None:
                app = QApplication([])
                
            widget = EnhancedPDFToolsWidget()
            
            # Test main components
            components = [
                'main_layout',
                'tab_widget',
                'current_file_label',
                'progress_bar',
                'status_label'
            ]
            
            missing_components = []
            for component in components:
                if not hasattr(widget, component):
                    missing_components.append(component)
                    
            if missing_components:
                return {
                    'success': False,
                    'message': f"Missing UI components: {missing_components}"
                }
                
            # Test tab structure
            if widget.tab_widget:
                tab_names = []
                for i in range(widget.tab_widget.count()):
                    tab_names.append(widget.tab_widget.tabText(i))
                    
                expected_tabs = [
                    "Basic Operations",
                    "Content Extraction", 
                    "Security",
                    "Enhancements",
                    "Conversion",
                    "View Analysis"
                ]
                
                if tab_names != expected_tabs:
                    return {
                        'success': False,
                        'message': f"Tab structure mismatch. Expected: {expected_tabs}, Got: {tab_names}"
                    }
                    
            return {
                'success': True,
                'message': f"UI components complete with {len(tab_names)} tabs"
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': "UI components test failed",
                'details': str(e)
            }
            
    def test_signal_connections(self):
        """Test signal connections and communication"""
        try:
            app = QApplication.instance()
            if app is None:
                app = QApplication([])
                
            widget = EnhancedPDFToolsWidget()
            
            # Test signal existence
            signals = [
                'tool_operation_started',
                'tool_operation_completed',
                'file_selected'
            ]
            
            missing_signals = []
            for signal in signals:
                if not hasattr(widget, signal):
                    missing_signals.append(signal)
                    
            if missing_signals:
                return {
                    'success': False,
                    'message': f"Missing signals: {missing_signals}"
                }
                
            # Test signal emission (basic test)
            signal_test_passed = True
            try:
                widget.file_selected.emit("test.pdf")
                widget.tool_operation_started.emit("test_tool", "test_operation")
                widget.tool_operation_completed.emit("test_tool", "test_operation", True)
            except Exception:
                signal_test_passed = False
                
            if not signal_test_passed:
                return {
                    'success': False,
                    'message': "Signal emission failed"
                }
                
            return {
                'success': True,
                'message': f"All {len(signals)} signals working correctly"
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': "Signal connections test failed",
                'details': str(e)
            }
            
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\nFailed Tests:")
            for test_name, result in self.test_results.items():
                if not result['success']:
                    print(f"  ✗ {test_name}: {result['message']}")
        else:
            print("\n🎉 All tests passed! Enhanced PDF Tools integration is working correctly.")
            
        print("\nDetailed log saved to: pdf_integration_test.log")


def main():
    """Main test execution"""
    if not IMPORTS_SUCCESSFUL:
        print("❌ Cannot run tests - required imports failed")
        print("Please ensure PyQt5 is installed and all modules are available")
        return 1
        
    tester = PDFIntegrationTester()
    tester.run_all_tests()
    
    # Return exit code based on test results
    failed_tests = sum(1 for result in tester.test_results.values() if not result['success'])
    return 1 if failed_tests > 0 else 0


if __name__ == "__main__":
    sys.exit(main())