#!/usr/bin/env python3
"""
Comprehensive unit tests for system_cleanup.py

Test file: test_system_cleanup_2025-08-28.py
Created: 2025-08-28
Target: src/utilities/system/system_cleanup.py

This module contains comprehensive unit tests for the SystemCleanupGUI class
using pytest framework with mocking and edge case testing.
"""

import logging
import os
import shutil
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, Mock, call, patch

import pytest

# Add the source directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

# Import the module under test
try:
    from src.utilities.system.system_cleanup import (CLEANUP_TOOLS_AVAILABLE,
                                                     DIAGNOSTICS_GUI_AVAILABLE,
                                                     PYQT5_AVAILABLE,
                                                     SystemCleanupGUI, main)
    IMPORT_SUCCESS = True
except ImportError:
    try:
        # Try alternative import path
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
        from src.utilities.system.system_cleanup import (
            CLEANUP_TOOLS_AVAILABLE, DIAGNOSTICS_GUI_AVAILABLE,
            PYQT5_AVAILABLE, SystemCleanupGUI, main)
        IMPORT_SUCCESS = True
    except ImportError as e:
        print(f"Import failed: {e}")
        IMPORT_SUCCESS = False
        # Create dummy classes for testing
        class SystemCleanupGUI:
            pass
        def main():
            pass
        PYQT5_AVAILABLE = False
        DIAGNOSTICS_GUI_AVAILABLE = False
        CLEANUP_TOOLS_AVAILABLE = False


class TestSystemCleanupGUIInitialization:
    """Test cases for SystemCleanupGUI initialization."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.mock_app = Mock()
        self.mock_hub = Mock()
        self.test_temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        """Clean up test fixtures after each test method."""
        if os.path.exists(self.test_temp_dir):
            shutil.rmtree(self.test_temp_dir, ignore_errors=True)
    
    @patch('utilities.system.system_cleanup.PYQT5_AVAILABLE', True)
    @patch('utilities.system.system_cleanup.SystemDiagnosticsGUI')
    def test_init_with_pyqt5_available(self, mock_base_class):
        """Test initialization when PyQt5 is available."""
        # Setup
        mock_instance = Mock()
        mock_base_class.return_value = mock_instance
        
        # Execute
        with patch.object(SystemCleanupGUI, 'init_cleanup_tools'), \
             patch.object(SystemCleanupGUI, 'customize_for_cleanup'):
            gui = SystemCleanupGUI(hub_instance=self.mock_hub)
        
        # Verify
        assert gui.cleanup_tools == {}
        assert gui.safety_manager is None
        assert isinstance(gui.logger, logging.Logger)
        assert gui.logger.name == 'RFU.SystemCleanup'
    
    @patch('utilities.system.system_cleanup.PYQT5_AVAILABLE', False)
    def test_init_without_pyqt5_raises_error(self):
        """Test that initialization raises ImportError when PyQt5 is not available."""
        with pytest.raises(ImportError, match="PyQt5 is required"):
            SystemCleanupGUI()
    
    @patch('utilities.system.system_cleanup.PYQT5_AVAILABLE', True)
    @patch('utilities.system.system_cleanup.SystemDiagnosticsGUI')
    def test_init_cleanup_tools_with_available_tools(self, mock_base_class):
        """Test initialization of cleanup tools when they are available."""
        with patch('utilities.system.system_cleanup.CLEANUP_TOOLS_AVAILABLE', True), \
             patch('utilities.system.system_cleanup.SafetyManager') as mock_safety, \
             patch('utilities.system.system_cleanup.TempFilesCleaner') as mock_temp:
            
            mock_safety_instance = Mock()
            mock_temp_instance = Mock()
            mock_safety.return_value = mock_safety_instance
            mock_temp.return_value = mock_temp_instance
            
            with patch.object(SystemCleanupGUI, 'customize_for_cleanup'):
                gui = SystemCleanupGUI()
            
            assert gui.safety_manager == mock_safety_instance
            assert 'temp_files' in gui.cleanup_tools
            assert gui.cleanup_tools['temp_files'] == mock_temp_instance
    
    @patch('utilities.system.system_cleanup.PYQT5_AVAILABLE', True)
    @patch('utilities.system.system_cleanup.SystemDiagnosticsGUI')
    def test_init_cleanup_tools_without_available_tools(self, mock_base_class):
        """Test initialization when cleanup tools are not available."""
        with patch('utilities.system.system_cleanup.CLEANUP_TOOLS_AVAILABLE', False), \
             patch.object(SystemCleanupGUI, 'customize_for_cleanup'):
            gui = SystemCleanupGUI()
            
            assert gui.cleanup_tools == {}
            assert gui.safety_manager is None
    
    @patch('utilities.system.system_cleanup.PYQT5_AVAILABLE', True)
    @patch('utilities.system.system_cleanup.SystemDiagnosticsGUI')
    def test_init_cleanup_tools_with_exception(self, mock_base_class):
        """Test handling of exceptions during cleanup tools initialization."""
        with patch('utilities.system.system_cleanup.CLEANUP_TOOLS_AVAILABLE', True), \
             patch('utilities.system.system_cleanup.SafetyManager', side_effect=Exception("Test error")), \
             patch.object(SystemCleanupGUI, 'customize_for_cleanup'):
            
            gui = SystemCleanupGUI()
            
            # Should not raise exception, but tools should remain empty
            assert gui.cleanup_tools == {}
            assert gui.safety_manager is None


class TestSystemCleanupGUICustomization:
    """Test cases for GUI customization methods."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.mock_tab_widget = Mock()
    
    @patch('utilities.system.system_cleanup.PYQT5_AVAILABLE', True)
    @patch('utilities.system.system_cleanup.SystemDiagnosticsGUI')
    def test_customize_for_cleanup_with_tab_widget(self, mock_base_class):
        """Test customization when tab widget is available."""
        with patch.object(SystemCleanupGUI, 'init_cleanup_tools'), \
             patch.object(SystemCleanupGUI, 'add_cleanup_tab') as mock_add_tab:
            
            gui = SystemCleanupGUI()
            gui.tab_widget = self.mock_tab_widget
            gui.setWindowTitle = Mock()
            
            gui.customize_for_cleanup()
            
            gui.setWindowTitle.assert_called_once_with(
                "System Cleanup - Richard's File Utilities"
            )
            mock_add_tab.assert_called_once()
    
    @patch('utilities.system.system_cleanup.PYQT5_AVAILABLE', True)
    @patch('utilities.system.system_cleanup.SystemDiagnosticsGUI')
    def test_customize_for_cleanup_without_tab_widget(self, mock_base_class):
        """Test customization when tab widget is not available."""
        with patch.object(SystemCleanupGUI, 'init_cleanup_tools'), \
             patch.object(SystemCleanupGUI, 'add_cleanup_tab') as mock_add_tab:
            
            gui = SystemCleanupGUI()
            gui.tab_widget = None
            gui.setWindowTitle = Mock()
            
            gui.customize_for_cleanup()
            
            gui.setWindowTitle.assert_called_once()
            mock_add_tab.assert_not_called()
    
    @patch('utilities.system.system_cleanup.PYQT5_AVAILABLE', True)
    @patch('utilities.system.system_cleanup.SystemDiagnosticsGUI')
    @patch('utilities.system.system_cleanup.QWidget')
    @patch('utilities.system.system_cleanup.QVBoxLayout')
    @patch('utilities.system.system_cleanup.QLabel')
    @patch('utilities.system.system_cleanup.QGroupBox')
    @patch('utilities.system.system_cleanup.QPushButton')
    @patch('utilities.system.system_cleanup.QTextEdit')
    def test_add_cleanup_tab_with_temp_tool(self, mock_text_edit, mock_button, 
                                          mock_group_box, mock_label, mock_layout,
                                          mock_widget, mock_base_class):
        """Test adding cleanup tab when temp tool is available."""
        with patch.object(SystemCleanupGUI, 'init_cleanup_tools'), \
             patch.object(SystemCleanupGUI, 'customize_for_cleanup'):
            
            gui = SystemCleanupGUI()
            gui.tab_widget = Mock()
            gui.cleanup_tools = {'temp_files': Mock()}
            
            # Mock Qt objects
            mock_cleanup_widget = Mock()
            mock_widget.return_value = mock_cleanup_widget
            mock_layout_instance = Mock()
            mock_layout.return_value = mock_layout_instance
            mock_button_instance = Mock()
            mock_button.return_value = mock_button_instance
            mock_text_edit_instance = Mock()
            mock_text_edit.return_value = mock_text_edit_instance
            
            gui.add_cleanup_tab()
            
            # Verify widget creation and configuration
            mock_widget.assert_called()
            mock_layout.assert_called()
            mock_button_instance.clicked.connect.assert_called_once()
            gui.tab_widget.addTab.assert_called_once()
    
    @patch('utilities.system.system_cleanup.PYQT5_AVAILABLE', True)
    @patch('utilities.system.system_cleanup.SystemDiagnosticsGUI')
    def test_add_cleanup_tab_with_exception(self, mock_base_class):
        """Test handling of exceptions during tab addition."""
        with patch.object(SystemCleanupGUI, 'init_cleanup_tools'), \
             patch.object(SystemCleanupGUI, 'customize_for_cleanup'):
            
            gui = SystemCleanupGUI()
            gui.tab_widget = Mock()
            gui.cleanup_tools = {}
            
            # Mock exception during widget creation
            with patch('utilities.system.system_cleanup.QWidget', 
                      side_effect=Exception("Widget creation error")):
                # Should not raise exception
                gui.add_cleanup_tab()


class TestSystemCleanupGUITempCleanup:
    """Test cases for temporary files cleanup functionality."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.mock_temp_tool = Mock()
        self.mock_message_box = Mock()
    
    @patch('utilities.system.system_cleanup.PYQT5_AVAILABLE', True)
    @patch('utilities.system.system_cleanup.SystemDiagnosticsGUI')
    @patch('utilities.system.system_cleanup.QMessageBox')
    def test_run_temp_cleanup_tool_not_available(self, mock_qmsg, mock_base_class):
        """Test temp cleanup when tool is not available."""
        with patch.object(SystemCleanupGUI, 'init_cleanup_tools'), \
             patch.object(SystemCleanupGUI, 'customize_for_cleanup'):
            
            gui = SystemCleanupGUI()
            gui.cleanup_tools = {}
            
            gui.run_temp_cleanup()
            
            mock_qmsg.warning.assert_called_once()
    
    @patch('utilities.system.system_cleanup.PYQT5_AVAILABLE', True)
    @patch('utilities.system.system_cleanup.SystemDiagnosticsGUI')
    @patch('utilities.system.system_cleanup.QMessageBox')
    def test_run_temp_cleanup_user_cancels(self, mock_qmsg, mock_base_class):
        """Test temp cleanup when user cancels operation."""
        with patch.object(SystemCleanupGUI, 'init_cleanup_tools'), \
             patch.object(SystemCleanupGUI, 'customize_for_cleanup'):
            
            gui = SystemCleanupGUI()
            gui.cleanup_tools = {'temp_files': self.mock_temp_tool}
            
            # Mock user clicking "No"
            mock_qmsg.question.return_value = mock_qmsg.No
            
            gui.run_temp_cleanup()
            
            # Should not execute cleanup
            self.mock_temp_tool.execute_operation.assert_not_called()
    
    @patch('utilities.system.system_cleanup.PYQT5_AVAILABLE', True)
    @patch('utilities.system.system_cleanup.SystemDiagnosticsGUI')
    @patch('utilities.system.system_cleanup.QMessageBox')
    def test_run_temp_cleanup_successful_operation(self, mock_qmsg, mock_base_class):
        """Test successful temp cleanup operation."""
        # Import CleanupOperationResult for testing
        from utilities.system.system_cleanup.core.cleanup_base import \
            CleanupOperationResult
        
        with patch.object(SystemCleanupGUI, 'init_cleanup_tools'), \
             patch.object(SystemCleanupGUI, 'customize_for_cleanup'):
            
            gui = SystemCleanupGUI()
            gui.cleanup_tools = {'temp_files': self.mock_temp_tool}
            gui.results_text = Mock()
            
            # Mock user clicking "Yes"
            mock_qmsg.question.return_value = mock_qmsg.Yes
            
            # Mock successful operation result
            success_result = CleanupOperationResult(
                success=True,
                message="Cleanup completed successfully",
                items_processed=150,
                space_freed=1024*1024*100,  # 100 MB
                errors=[]
            )
            self.mock_temp_tool.execute_operation.return_value = success_result
            
            gui.run_temp_cleanup()
            
            # Verify operation execution
            self.mock_temp_tool.execute_operation.assert_called_once_with(
                max_age_days=0,
                min_size_bytes=0,
                include_system_temp=True,
                create_backup=False,
                secure_delete=False
            )
            
            # Verify results display
            gui.results_text.setPlainText.assert_called()
            mock_qmsg.information.assert_called_once()
    
    @patch('utilities.system.system_cleanup.PYQT5_AVAILABLE', True)
    @patch('utilities.system.system_cleanup.SystemDiagnosticsGUI')
    @patch('utilities.system.system_cleanup.QMessageBox')
    def test_run_temp_cleanup_with_errors(self, mock_qmsg, mock_base_class):
        """Test temp cleanup operation with errors."""
        from utilities.system.system_cleanup.core.cleanup_base import \
            CleanupOperationResult
        
        with patch.object(SystemCleanupGUI, 'init_cleanup_tools'), \
             patch.object(SystemCleanupGUI, 'customize_for_cleanup'):
            
            gui = SystemCleanupGUI()
            gui.cleanup_tools = {'temp_files': self.mock_temp_tool}
            gui.results_text = Mock()
            
            # Mock user clicking "Yes"
            mock_qmsg.question.return_value = mock_qmsg.Yes
            
            # Mock operation result with errors
            error_result = CleanupOperationResult(
                success=True,
                message="Cleanup completed with warnings",
                items_processed=100,
                space_freed=1024*1024*50,  # 50 MB
                errors=["Cannot delete file1.tmp", "Access denied for file2.tmp"]
            )
            self.mock_temp_tool.execute_operation.return_value = error_result
            
            gui.run_temp_cleanup()
            
            # Verify results text contains error information
            call_args = gui.results_text.setPlainText.call_args[0][0]
            assert "Warnings/Errors:" in call_args
            assert "Cannot delete file1.tmp" in call_args
            assert "Access denied for file2.tmp" in call_args
    
    @patch('utilities.system.system_cleanup.PYQT5_AVAILABLE', True)
    @patch('utilities.system.system_cleanup.SystemDiagnosticsGUI')
    @patch('utilities.system.system_cleanup.QMessageBox')
    def test_run_temp_cleanup_failed_operation(self, mock_qmsg, mock_base_class):
        """Test failed temp cleanup operation."""
        from utilities.system.system_cleanup.core.cleanup_base import \
            CleanupOperationResult
        
        with patch.object(SystemCleanupGUI, 'init_cleanup_tools'), \
             patch.object(SystemCleanupGUI, 'customize_for_cleanup'):
            
            gui = SystemCleanupGUI()
            gui.cleanup_tools = {'temp_files': self.mock_temp_tool}
            gui.results_text = Mock()
            
            # Mock user clicking "Yes"
            mock_qmsg.question.return_value = mock_qmsg.Yes
            
            # Mock failed operation result
            failed_result = CleanupOperationResult(
                success=False,
                message="Operation failed due to insufficient permissions",
                items_processed=0,
                space_freed=0,
                errors=["Access denied", "Cannot create backup"]
            )
            self.mock_temp_tool.execute_operation.return_value = failed_result
            
            gui.run_temp_cleanup()
            
            # Verify error handling
            call_args = gui.results_text.setPlainText.call_args[0][0]
            assert "cleanup failed" in call_args
            assert "Access denied" in call_args
            mock_qmsg.critical.assert_not_called()  # Since it's a controlled failure
    
    @patch('utilities.system.system_cleanup.PYQT5_AVAILABLE', True)
    @patch('utilities.system.system_cleanup.SystemDiagnosticsGUI')
    @patch('utilities.system.system_cleanup.QMessageBox')
    def test_run_temp_cleanup_with_exception(self, mock_qmsg, mock_base_class):
        """Test temp cleanup when an exception occurs."""
        with patch.object(SystemCleanupGUI, 'init_cleanup_tools'), \
             patch.object(SystemCleanupGUI, 'customize_for_cleanup'):
            
            gui = SystemCleanupGUI()
            gui.cleanup_tools = {'temp_files': self.mock_temp_tool}
            gui.results_text = Mock()
            
            # Mock user clicking "Yes"
            mock_qmsg.question.return_value = mock_qmsg.Yes
            
            # Mock exception during operation
            self.mock_temp_tool.execute_operation.side_effect = RuntimeError("Test exception")
            
            gui.run_temp_cleanup()
            
            # Verify exception handling
            call_args = gui.results_text.setPlainText.call_args[0][0]
            assert "Error during temporary files cleanup" in call_args
            assert "Test exception" in call_args
            mock_qmsg.critical.assert_called_once()


class TestSystemCleanupGUIHelperMethods:
    """Test cases for helper methods in SystemCleanupGUI."""
    
    @patch('utilities.system.system_cleanup.PYQT5_AVAILABLE', True)
    @patch('utilities.system.system_cleanup.SystemDiagnosticsGUI')
    def test_format_size_bytes(self, mock_base_class):
        """Test size formatting for bytes."""
        with patch.object(SystemCleanupGUI, 'init_cleanup_tools'), \
             patch.object(SystemCleanupGUI, 'customize_for_cleanup'):
            
            gui = SystemCleanupGUI()
            
            # Test various sizes
            assert gui._format_size(512) == "512.0 B"
            assert gui._format_size(0) == "0.0 B"
    
    @patch('utilities.system.system_cleanup.PYQT5_AVAILABLE', True)
    @patch('utilities.system.system_cleanup.SystemDiagnosticsGUI')
    def test_format_size_kilobytes(self, mock_base_class):
        """Test size formatting for kilobytes."""
        with patch.object(SystemCleanupGUI, 'init_cleanup_tools'), \
             patch.object(SystemCleanupGUI, 'customize_for_cleanup'):
            
            gui = SystemCleanupGUI()
            
            # Test KB sizes
            assert gui._format_size(1024) == "1.0 KB"
            assert gui._format_size(1536) == "1.5 KB"
            assert gui._format_size(2048) == "2.0 KB"
    
    @patch('utilities.system.system_cleanup.PYQT5_AVAILABLE', True)
    @patch('utilities.system.system_cleanup.SystemDiagnosticsGUI')
    def test_format_size_megabytes(self, mock_base_class):
        """Test size formatting for megabytes."""
        with patch.object(SystemCleanupGUI, 'init_cleanup_tools'), \
             patch.object(SystemCleanupGUI, 'customize_for_cleanup'):
            
            gui = SystemCleanupGUI()
            
            # Test MB sizes
            assert gui._format_size(1024*1024) == "1.0 MB"
            assert gui._format_size(1024*1024*5) == "5.0 MB"
            assert gui._format_size(1024*1024*100) == "100.0 MB"
    
    @patch('utilities.system.system_cleanup.PYQT5_AVAILABLE', True)
    @patch('utilities.system.system_cleanup.SystemDiagnosticsGUI')
    def test_format_size_gigabytes(self, mock_base_class):
        """Test size formatting for gigabytes."""
        with patch.object(SystemCleanupGUI, 'init_cleanup_tools'), \
             patch.object(SystemCleanupGUI, 'customize_for_cleanup'):
            
            gui = SystemCleanupGUI()
            
            # Test GB sizes
            assert gui._format_size(1024*1024*1024) == "1.0 GB"
            assert gui._format_size(1024*1024*1024*2) == "2.0 GB"
    
    @patch('utilities.system.system_cleanup.PYQT5_AVAILABLE', True)
    @patch('utilities.system.system_cleanup.SystemDiagnosticsGUI')
    def test_format_size_large_values(self, mock_base_class):
        """Test size formatting for very large values."""
        with patch.object(SystemCleanupGUI, 'init_cleanup_tools'), \
             patch.object(SystemCleanupGUI, 'customize_for_cleanup'):
            
            gui = SystemCleanupGUI()
            
            # Test TB and PB sizes
            tb_size = 1024*1024*1024*1024
            assert gui._format_size(tb_size) == "1.0 TB"
            
            pb_size = tb_size * 1024
            assert gui._format_size(pb_size) == "1.0 PB"


class TestMainFunction:
    """Test cases for the main function."""
    
    @patch('utilities.system.system_cleanup.PYQT5_AVAILABLE', True)
    @patch('utilities.system.system_cleanup.QApplication')
    @patch('utilities.system.system_cleanup.SystemCleanupGUI')
    def test_main_with_pyqt5_available(self, mock_gui_class, mock_qapp_class):
        """Test main function when PyQt5 is available."""
        # Setup mocks
        mock_app = Mock()
        mock_qapp_class.return_value = mock_app
        mock_gui = Mock()
        mock_gui_class.return_value = mock_gui
        mock_app.exec_.return_value = 0
        
        # Mock sys.exit to prevent actual exit
        with patch('sys.exit') as mock_exit:
            main()
        
        # Verify application creation and execution
        mock_qapp_class.assert_called_once()
        mock_gui_class.assert_called_once()
        mock_gui.show.assert_called_once()
        mock_app.exec_.assert_called_once()
        mock_exit.assert_called_once_with(0)
    
    @patch('utilities.system.system_cleanup.PYQT5_AVAILABLE', False)
    @patch('builtins.print')
    def test_main_without_pyqt5(self, mock_print):
        """Test main function when PyQt5 is not available."""
        main()
        
        # Verify error messages are printed
        mock_print.assert_any_call("PyQt5 is required to run the System Cleanup GUI.")
        mock_print.assert_any_call("Please install PyQt5: pip install PyQt5")
    
    @patch('utilities.system.system_cleanup.PYQT5_AVAILABLE', True)
    @patch('utilities.system.system_cleanup.QApplication')
    @patch('utilities.system.system_cleanup.SystemCleanupGUI')
    @patch('builtins.print')
    def test_main_with_exception(self, mock_print, mock_gui_class, mock_qapp_class):
        """Test main function when an exception occurs."""
        # Setup mocks to raise exception
        mock_qapp_class.side_effect = RuntimeError("Test exception")
        
        main()
        
        # Verify error handling
        mock_print.assert_called_with("Error running System Cleanup GUI: Test exception")


class TestEdgeCasesAndErrorHandling:
    """Test cases for edge cases and error handling scenarios."""
    
    @patch('utilities.system.system_cleanup.PYQT5_AVAILABLE', True)
    @patch('utilities.system.system_cleanup.SystemDiagnosticsGUI')
    def test_missing_attributes_handling(self, mock_base_class):
        """Test handling of missing attributes."""
        with patch.object(SystemCleanupGUI, 'init_cleanup_tools'), \
             patch.object(SystemCleanupGUI, 'customize_for_cleanup'):
            
            gui = SystemCleanupGUI()
            
            # Test with missing results_text
            if not hasattr(gui, 'results_text'):
                gui.results_text = None
            
            # Should not raise exception when results_text is None
            try:
                gui.run_temp_cleanup()
            except AttributeError:
                pytest.fail("Should handle missing results_text gracefully")
    
    @patch('utilities.system.system_cleanup.PYQT5_AVAILABLE', True)
    @patch('utilities.system.system_cleanup.SystemDiagnosticsGUI')
    def test_logger_configuration(self, mock_base_class):
        """Test logger configuration and usage."""
        with patch.object(SystemCleanupGUI, 'init_cleanup_tools'), \
             patch.object(SystemCleanupGUI, 'customize_for_cleanup'):
            
            gui = SystemCleanupGUI()
            
            # Verify logger is properly configured
            assert gui.logger is not None
            assert gui.logger.name == 'RFU.SystemCleanup'
            assert isinstance(gui.logger, logging.Logger)
    
    @patch('utilities.system.system_cleanup.PYQT5_AVAILABLE', True)
    @patch('utilities.system.system_cleanup.SystemDiagnosticsGUI')
    def test_signals_availability(self, mock_base_class):
        """Test signal availability when PyQt5 is present."""
        with patch.object(SystemCleanupGUI, 'init_cleanup_tools'), \
             patch.object(SystemCleanupGUI, 'customize_for_cleanup'):
            
            gui = SystemCleanupGUI()
            
            # Verify signals are available
            assert hasattr(gui, 'cleanup_started')
            assert hasattr(gui, 'cleanup_completed')
            assert gui.cleanup_started is not None
            assert gui.cleanup_completed is not None


@pytest.fixture(scope="session")
def test_session_info():
    """Provide test session information."""
    return {
        'test_file': 'test_system_cleanup_2025-08-28.py',
        'target_module': 'system_cleanup.py',
        'timestamp': datetime.now().isoformat(),
        'test_framework': 'pytest'
    }


# Configuration for pytest
def pytest_configure(config):
    """Configure pytest with custom settings."""
    # Add custom markers
    config.addinivalue_line(
        "markers",
        "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", 
        "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers",
        "slow: marks tests as slow running"
    )


# Custom pytest hooks for enhanced reporting
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add custom markers."""
    for item in items:
        # Mark all tests in this file as unit tests
        item.add_marker(pytest.mark.unit)
        
        # Mark slow tests
        if "slow" in item.name or "comprehensive" in item.name:
            item.add_marker(pytest.mark.slow)


def pytest_sessionstart(session):
    """Called after the Session object has been created."""
    print(f"\n{'='*80}")
    print(f"System Cleanup Unit Tests - Started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target Module: system_cleanup.py")
    print(f"Test File: test_system_cleanup_2025-08-28.py")
    print(f"{'='*80}")


def pytest_sessionfinish(session, exitstatus):
    """Called after whole test run finished."""
    print(f"\n{'='*80}")
    print(f"System Cleanup Unit Tests - Completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Exit Status: {exitstatus}")
    print(f"{'='*80}")


if __name__ == "__main__":
    # Run tests when script is executed directly
    pytest.main([__file__, "-v", "--tb=short"])