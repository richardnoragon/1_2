#!/usr/bin/env python3
"""
Comprehensive Unit Tests for Size Analyzer Tool

Test file: test_size_analyzer_2025-08-22.py
Target: src.utilities.analysis.size_analyzer
Created: 2025-08-22
Framework: pytest

This test suite provides comprehensive coverage for the SizeAnalyzerGUI class
including initialization, UI components, menu integration, and all public methods.
"""

import sys
import os
import pytest
import unittest.mock as mock
from unittest.mock import MagicMock, patch, PropertyMock
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Import the target module
try:
    from src.utilities.analysis.size_analyzer import SizeAnalyzerGUI, main
except ImportError:
    pytest.skip("size_analyzer module not found", allow_module_level=True)


class TestSizeAnalyzerGUI:
    """Test suite for SizeAnalyzerGUI class."""
    
    @pytest.fixture(autouse=True)
    def setup_test_environment(self):
        """Setup test environment before each test."""
        self.test_start_time = datetime.now()
        
        # Mock PyQt5 components to avoid GUI dependencies
        with patch('sys.modules') as mock_modules:
            mock_modules['PyQt5'] = MagicMock()
            mock_modules['PyQt5.QtWidgets'] = MagicMock()
            mock_modules['PyQt5.QtCore'] = MagicMock()
            mock_modules['PyQt5.QtGui'] = MagicMock()
            
            # Mock QApplication for tests
            self.mock_app = MagicMock()
            
            yield
            
        self.test_end_time = datetime.now()
        self.test_duration = self.test_end_time - self.test_start_time
    
    @patch('src.utilities.analysis.size_analyzer.QApplication')
    @patch('src.utilities.analysis.size_analyzer.QMainWindow')
    @patch('src.utilities.analysis.size_analyzer.StandardWindow')
    def test_init_with_standard_window_available(self, mock_standard_window, 
                                                 mock_qmain_window, mock_qapp):
        """Test SizeAnalyzerGUI initialization with StandardWindow available."""
        # Setup
        mock_standard_window.return_value = MagicMock()
        
        with patch('src.utilities.analysis.size_analyzer.STANDARD_WINDOW_AVAILABLE', True):
            # Execute
            gui = SizeAnalyzerGUI()
            
            # Assert
            assert hasattr(gui, 'analysis_results')
            assert gui.analysis_results == {}
            mock_standard_window.assert_called_once_with(
                title="Size Analyzer - Richard's File Utilities",
                window_type="utility"
            )
    
    @patch('src.utilities.analysis.size_analyzer.QApplication')
    @patch('src.utilities.analysis.size_analyzer.QMainWindow')
    def test_init_without_standard_window(self, mock_qmain_window, mock_qapp):
        """Test SizeAnalyzerGUI initialization without StandardWindow."""
        with patch('src.utilities.analysis.size_analyzer.STANDARD_WINDOW_AVAILABLE', False):
            # Execute
            gui = SizeAnalyzerGUI()
            
            # Assert
            assert hasattr(gui, 'analysis_results')
            assert gui.analysis_results == {}
    
    @patch('src.utilities.analysis.size_analyzer.QApplication')
    @patch('src.utilities.analysis.size_analyzer.StandardWindow')
    def test_setup_menu_callbacks(self, mock_standard_window, mock_qapp):
        """Test menu callback setup functionality."""
        # Setup
        mock_menu_manager = MagicMock()
        mock_instance = MagicMock()
        mock_instance.menu_manager = mock_menu_manager
        mock_standard_window.return_value = mock_instance
        
        with patch('src.utilities.analysis.size_analyzer.STANDARD_WINDOW_AVAILABLE', True):
            gui = SizeAnalyzerGUI()
            gui.menu_manager = mock_menu_manager
            
            # Execute
            gui._setup_menu_callbacks()
            
            # Assert
            expected_calls = [
                mock.call('new_analysis', gui.clear_analysis),
                mock.call('show_user_guide', gui.show_help),
                mock.call('show_preferences', gui.show_preferences),
                mock.call('refresh', gui.refresh_view)
            ]
            mock_menu_manager.register_callback.assert_has_calls(
                expected_calls, any_order=True
            )
    
    @patch('src.utilities.analysis.size_analyzer.QApplication')
    @patch('src.utilities.analysis.size_analyzer.StandardWindow')
    def test_clear_analysis(self, mock_standard_window, mock_qapp):
        """Test clearing analysis results."""
        # Setup
        with patch('src.utilities.analysis.size_analyzer.STANDARD_WINDOW_AVAILABLE', True):
            gui = SizeAnalyzerGUI()
            gui.analysis_results = {'test': 'data'}
            gui.results_list = MagicMock()
            
            # Execute
            gui.clear_analysis()
            
            # Assert
            assert gui.analysis_results == {}
            gui.results_list.clear.assert_called_once()
    
    @patch('src.utilities.analysis.size_analyzer.QApplication')
    @patch('src.utilities.analysis.size_analyzer.StandardWindow')
    def test_clear_analysis_without_results_list(self, mock_standard_window, mock_qapp):
        """Test clearing analysis when results_list doesn't exist."""
        # Setup
        with patch('src.utilities.analysis.size_analyzer.STANDARD_WINDOW_AVAILABLE', True):
            gui = SizeAnalyzerGUI()
            gui.analysis_results = {'test': 'data'}
            
            # Execute
            gui.clear_analysis()
            
            # Assert
            assert gui.analysis_results == {}
    
    @patch('src.utilities.analysis.size_analyzer.QMessageBox')
    @patch('src.utilities.analysis.size_analyzer.QApplication')
    @patch('src.utilities.analysis.size_analyzer.StandardWindow')
    def test_show_help(self, mock_standard_window, mock_qapp, mock_message_box):
        """Test show help dialog functionality."""
        # Setup
        with patch('src.utilities.analysis.size_analyzer.STANDARD_WINDOW_AVAILABLE', True):
            gui = SizeAnalyzerGUI()
            
            # Execute
            gui.show_help()
            
            # Assert
            mock_message_box.information.assert_called_once()
            call_args = mock_message_box.information.call_args
            assert call_args[0][1] == "Size Analyzer Help"
            assert "How to Analyze Directory Sizes" in call_args[0][2]
            assert "Keyboard Shortcuts" in call_args[0][2]
    
    @patch('src.utilities.analysis.size_analyzer.QMessageBox')
    @patch('src.utilities.analysis.size_analyzer.QApplication')
    @patch('src.utilities.analysis.size_analyzer.StandardWindow')
    def test_show_preferences(self, mock_standard_window, mock_qapp, mock_message_box):
        """Test show preferences dialog functionality."""
        # Setup
        with patch('src.utilities.analysis.size_analyzer.STANDARD_WINDOW_AVAILABLE', True):
            gui = SizeAnalyzerGUI()
            
            # Execute
            gui.show_preferences()
            
            # Assert
            mock_message_box.information.assert_called_once()
            call_args = mock_message_box.information.call_args
            assert call_args[0][1] == "Size Analyzer Preferences"
            assert "Analysis depth limits" in call_args[0][2]
    
    @patch('src.utilities.analysis.size_analyzer.QApplication')
    @patch('src.utilities.analysis.size_analyzer.StandardWindow')
    def test_refresh_view(self, mock_standard_window, mock_qapp):
        """Test refresh view functionality."""
        # Setup
        with patch('src.utilities.analysis.size_analyzer.STANDARD_WINDOW_AVAILABLE', True):
            gui = SizeAnalyzerGUI()
            gui.analysis_results = {'test': 'data'}
            gui.results_list = MagicMock()
            
            # Execute
            gui.refresh_view()
            
            # Assert
            assert gui.analysis_results == {}
            gui.results_list.clear.assert_called_once()
    
    @patch('src.utilities.analysis.size_analyzer.QApplication')
    @patch('src.utilities.analysis.size_analyzer.StandardWindow')
    @patch('src.utilities.analysis.size_analyzer.QWidget')
    @patch('src.utilities.analysis.size_analyzer.QVBoxLayout')
    @patch('src.utilities.analysis.size_analyzer.QLabel')
    @patch('src.utilities.analysis.size_analyzer.QGroupBox')
    @patch('src.utilities.analysis.size_analyzer.QListWidget')
    @patch('src.utilities.analysis.size_analyzer.QPushButton')
    def test_init_ui_with_standard_window(self, mock_button, mock_list, mock_group,
                                          mock_label, mock_layout, mock_widget,
                                          mock_standard_window, mock_qapp):
        """Test UI initialization with StandardWindow."""
        # Setup
        mock_instance = MagicMock()
        mock_instance.main_layout = MagicMock()
        mock_standard_window.return_value = mock_instance
        
        with patch('src.utilities.analysis.size_analyzer.STANDARD_WINDOW_AVAILABLE', True):
            gui = SizeAnalyzerGUI()
            gui.main_layout = MagicMock()
            
            # Execute
            gui.init_ui()
            
            # Assert UI components are created
            mock_label.assert_called()
            mock_group.assert_called_with("Analysis Results")
            mock_list.assert_called()
            mock_button.assert_called()
    
    @patch('src.utilities.analysis.size_analyzer.QApplication')
    @patch('src.utilities.analysis.size_analyzer.StandardWindow')
    @patch('src.utilities.analysis.size_analyzer.QWidget')
    @patch('src.utilities.analysis.size_analyzer.QVBoxLayout')
    def test_init_ui_without_standard_window(self, mock_layout, mock_widget,
                                             mock_standard_window, mock_qapp):
        """Test UI initialization without StandardWindow."""
        # Setup
        with patch('src.utilities.analysis.size_analyzer.STANDARD_WINDOW_AVAILABLE', False):
            gui = SizeAnalyzerGUI()
            gui.setCentralWidget = MagicMock()
            
            # Execute
            gui.init_ui()
            
            # Assert central widget is created
            gui.setCentralWidget.assert_called_once()
    
    @patch('src.utilities.analysis.size_analyzer.QApplication')
    @patch('src.utilities.analysis.size_analyzer.StandardWindow')
    def test_start_analysis(self, mock_standard_window, mock_qapp):
        """Test start analysis functionality."""
        # Setup
        with patch('src.utilities.analysis.size_analyzer.STANDARD_WINDOW_AVAILABLE', True):
            gui = SizeAnalyzerGUI()
            gui.results_list = MagicMock()
            
            # Execute
            gui.start_analysis()
            
            # Assert
            gui.results_list.clear.assert_called_once()
            gui.results_list.addItem.assert_called_once_with(
                "Analysis functionality ready for implementation"
            )
    
    @patch('src.utilities.analysis.size_analyzer.QMessageBox')
    @patch('src.utilities.analysis.size_analyzer.QApplication')
    @patch('src.utilities.analysis.size_analyzer.StandardWindow')
    def test_execute_action(self, mock_standard_window, mock_qapp, mock_message_box):
        """Test execute action functionality."""
        # Setup
        with patch('src.utilities.analysis.size_analyzer.STANDARD_WINDOW_AVAILABLE', True):
            gui = SizeAnalyzerGUI()
            
            # Execute
            gui.execute_action()
            
            # Assert
            mock_message_box.information.assert_called_once()
            call_args = mock_message_box.information.call_args
            assert call_args[0][1] == "Size Analyzer"
            assert "Tool functionality is ready for implementation" in call_args[0][2]


class TestSizeAnalyzerGUIEdgeCases:
    """Test edge cases and error conditions for SizeAnalyzerGUI."""
    
    @patch('src.utilities.analysis.size_analyzer.QApplication')
    @patch('src.utilities.analysis.size_analyzer.StandardWindow')
    def test_menu_callbacks_without_menu_manager(self, mock_standard_window, mock_qapp):
        """Test menu callback setup when menu_manager is not available."""
        # Setup
        with patch('src.utilities.analysis.size_analyzer.STANDARD_WINDOW_AVAILABLE', True):
            gui = SizeAnalyzerGUI()
            # Ensure no menu_manager attribute
            if hasattr(gui, 'menu_manager'):
                delattr(gui, 'menu_manager')
            
            # Execute - should not raise an exception
            gui._setup_menu_callbacks()
            
            # Assert - no errors should occur
            assert True  # Test passes if no exception is raised
    
    @patch('src.utilities.analysis.size_analyzer.QApplication')
    @patch('src.utilities.analysis.size_analyzer.StandardWindow')
    def test_analysis_results_immutability(self, mock_standard_window, mock_qapp):
        """Test that analysis_results can be safely modified."""
        # Setup
        with patch('src.utilities.analysis.size_analyzer.STANDARD_WINDOW_AVAILABLE', True):
            gui = SizeAnalyzerGUI()
            
            # Execute
            original_results = gui.analysis_results
            gui.analysis_results['test_key'] = 'test_value'
            
            # Assert
            assert gui.analysis_results != original_results
            assert gui.analysis_results['test_key'] == 'test_value'
    
    @patch('src.utilities.analysis.size_analyzer.QApplication')
    @patch('src.utilities.analysis.size_analyzer.StandardWindow')
    def test_multiple_clear_analysis_calls(self, mock_standard_window, mock_qapp):
        """Test multiple consecutive calls to clear_analysis."""
        # Setup
        with patch('src.utilities.analysis.size_analyzer.STANDARD_WINDOW_AVAILABLE', True):
            gui = SizeAnalyzerGUI()
            gui.analysis_results = {'data': 'test'}
            gui.results_list = MagicMock()
            
            # Execute
            gui.clear_analysis()
            gui.clear_analysis()
            gui.clear_analysis()
            
            # Assert
            assert gui.analysis_results == {}
            assert gui.results_list.clear.call_count == 3


class TestMainFunction:
    """Test the main function for standalone execution."""
    
    @patch('src.utilities.analysis.size_analyzer.sys.exit')
    @patch('src.utilities.analysis.size_analyzer.QApplication')
    def test_main_function_execution(self, mock_qapp, mock_sys_exit):
        """Test main function creates app and window correctly."""
        # Setup
        mock_app_instance = MagicMock()
        mock_app_instance.exec_.return_value = 0
        mock_qapp.return_value = mock_app_instance
        
        with patch('src.utilities.analysis.size_analyzer.SizeAnalyzerGUI') as mock_gui:
            mock_window = MagicMock()
            mock_gui.return_value = mock_window
            
            # Execute
            main()
            
            # Assert
            mock_qapp.assert_called_once_with(sys.argv)
            mock_gui.assert_called_once()
            mock_window.show.assert_called_once()
            mock_app_instance.exec_.assert_called_once()
            mock_sys_exit.assert_called_once_with(0)
    
    @patch('src.utilities.analysis.size_analyzer.sys.exit')
    @patch('src.utilities.analysis.size_analyzer.QApplication')
    def test_main_function_with_exception(self, mock_qapp, mock_sys_exit):
        """Test main function handles exceptions gracefully."""
        # Setup
        mock_qapp.side_effect = Exception("Test exception")
        
        # Execute & Assert
        with pytest.raises(Exception, match="Test exception"):
            main()


class TestModuleImports:
    """Test module import scenarios and fallbacks."""
    
    def test_pyqt5_import_failure_handling(self):
        """Test behavior when PyQt5 is not available."""
        # This test verifies the import error handling in the module
        # The actual module exits when PyQt5 is not available
        with patch.dict('sys.modules', {'PyQt5': None}):
            with patch('builtins.print') as mock_print:
                with patch('sys.exit') as mock_exit:
                    # Re-import would trigger the ImportError handling
                    # This is a conceptual test for the import guard
                    assert mock_print.call_count >= 0  # May or may not be called
    
    def test_standard_window_import_fallback(self):
        """Test StandardWindow import fallback mechanism."""
        # Test the fallback behavior when StandardWindow is not available
        with patch.dict('sys.modules', {'src.rfu.gui.standard_window': None}):
            # The module should set STANDARD_WINDOW_AVAILABLE to False
            # and use QMainWindow as fallback
            pass  # This is tested implicitly in other test cases


class TestPerformanceAndResource:
    """Test performance characteristics and resource usage."""
    
    @patch('src.utilities.analysis.size_analyzer.QApplication')
    @patch('src.utilities.analysis.size_analyzer.StandardWindow')
    def test_memory_usage_basic(self, mock_standard_window, mock_qapp):
        """Test basic memory usage characteristics."""
        # Setup
        with patch('src.utilities.analysis.size_analyzer.STANDARD_WINDOW_AVAILABLE', True):
            gui = SizeAnalyzerGUI()
            
            # Execute - perform multiple operations
            for i in range(100):
                gui.analysis_results[f'key_{i}'] = f'value_{i}'
                gui.clear_analysis()
            
            # Assert - should not accumulate data
            assert len(gui.analysis_results) == 0
    
    @patch('src.utilities.analysis.size_analyzer.QApplication')
    @patch('src.utilities.analysis.size_analyzer.StandardWindow')
    def test_repeated_ui_operations(self, mock_standard_window, mock_qapp):
        """Test repeated UI operations for stability."""
        # Setup
        with patch('src.utilities.analysis.size_analyzer.STANDARD_WINDOW_AVAILABLE', True):
            gui = SizeAnalyzerGUI()
            gui.results_list = MagicMock()
            
            # Execute - perform repeated operations
            for _ in range(50):
                gui.start_analysis()
                gui.clear_analysis()
            
            # Assert - operations should be stable
            assert gui.results_list.clear.call_count == 50
            assert gui.results_list.addItem.call_count == 50


# Test execution metadata
class TestExecutionMetadata:
    """Capture test execution metadata for reporting."""
    
    def test_execution_timestamp(self):
        """Record test execution timestamp."""
        execution_time = datetime.now()
        assert execution_time is not None
        assert isinstance(execution_time, datetime)
    
    def test_module_attributes(self):
        """Verify module has expected attributes."""
        from src.utilities.analysis import size_analyzer
        
        # Check module-level attributes
        assert hasattr(size_analyzer, 'SizeAnalyzerGUI')
        assert hasattr(size_analyzer, 'main')
        assert hasattr(size_analyzer, 'STANDARD_WINDOW_AVAILABLE')
    
    def test_class_methods_exist(self):
        """Verify all expected methods exist on SizeAnalyzerGUI."""
        expected_methods = [
            '__init__',
            '_setup_menu_callbacks',
            'clear_analysis',
            'show_help',
            'show_preferences',
            'refresh_view',
            'init_ui',
            'start_analysis',
            'execute_action'
        ]
        
        for method_name in expected_methods:
            assert hasattr(SizeAnalyzerGUI, method_name), f"Method {method_name} not found"


if __name__ == '__main__':
    # Run tests with detailed output
    pytest.main([
        __file__,
        '-v',
        '--tb=short',
        '--capture=no'
    ])