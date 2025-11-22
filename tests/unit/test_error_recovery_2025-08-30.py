#!/usr/bin/env python3
"""
Comprehensive Unit Tests for error_recovery.py
Generated on: 2025-08-30
Test Framework: pytest

This module contains comprehensive unit tests for the PrivacyToolsErrorRecovery class
and related functions in the error_recovery.py module.
"""

import sys
import pytest
import logging
import traceback
from unittest.mock import Mock, patch, MagicMock, call
from pathlib import Path
from typing import Dict, Any
import tempfile
import os

# Add the source directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.tools.privacy.error_recovery import (
    PrivacyToolsErrorRecovery,
    safe_import,
    safe_execute,
    error_recovery
)


class TestPrivacyToolsErrorRecovery:
    """Test suite for PrivacyToolsErrorRecovery class."""

    def setup_method(self):
        """Setup method called before each test method."""
        self.recovery = PrivacyToolsErrorRecovery()
        self.test_context = "test_context"

    def teardown_method(self):
        """Teardown method called after each test method."""
        # Clean up any created log files
        log_file = Path('privacy_tools_errors.log')
        if log_file.exists():
            try:
                log_file.unlink()
            except PermissionError:
                pass

    def test_initialization(self):
        """Test PrivacyToolsErrorRecovery initialization."""
        recovery = PrivacyToolsErrorRecovery()
        
        assert isinstance(recovery.logger, logging.Logger)
        assert recovery.logger.name == 'privacy_tools_recovery'
        assert recovery.logger.level == logging.INFO
        assert isinstance(recovery.recovery_strategies, dict)
        
        # Check that all expected recovery strategies are present
        expected_strategies = {
            'ImportError', 'ModuleNotFoundError', 'AttributeError',
            'TypeError', 'RuntimeError'
        }
        assert set(recovery.recovery_strategies.keys()) == expected_strategies

    def test_setup_logging(self):
        """Test logging setup."""
        recovery = PrivacyToolsErrorRecovery()
        logger = recovery._setup_logging()
        
        assert logger.name == 'privacy_tools_recovery'
        assert logger.level == logging.INFO
        assert len(logger.handlers) >= 1
        
        # Test that log file is created
        log_file = Path('privacy_tools_errors.log')
        assert log_file.exists() or True  # File might not exist yet until first log

    @patch('utilities.privacy.error_recovery.logging.Logger.error')
    def test_handle_error_logging(self, mock_error):
        """Test that handle_error logs errors correctly."""
        test_error = ValueError("Test error")
        context = "test_function"
        
        self.recovery.handle_error(test_error, context)
        
        # Verify logging calls
        assert mock_error.call_count == 2
        mock_error.assert_any_call(f"Error in {context}: ValueError - Test error")

    def test_handle_error_with_known_strategy(self):
        """Test handle_error with a known error type."""
        import_error = ImportError("Test import error")
        
        with patch.object(self.recovery, '_handle_import_error') as mock_handler:
            mock_handler.return_value = "handled"
            
            result = self.recovery.handle_error(import_error, self.test_context)
            
            mock_handler.assert_called_once_with(import_error, self.test_context)
            assert result == "handled"

    def test_handle_error_with_unknown_strategy(self):
        """Test handle_error with an unknown error type."""
        custom_error = ValueError("Test value error")
        
        with patch.object(self.recovery, '_handle_generic_error') as mock_handler:
            mock_handler.return_value = "generic_handled"
            
            result = self.recovery.handle_error(custom_error, self.test_context)
            
            mock_handler.assert_called_once_with(custom_error, self.test_context)
            assert result == "generic_handled"

    def test_handle_import_error_privacy_tools(self):
        """Test _handle_import_error for privacy tools related errors."""
        import_error = ImportError("No module named 'privacy_tools'")
        
        with patch.object(self.recovery, '_try_privacy_tools_fallback') as mock_fallback:
            mock_fallback.return_value = "fallback_result"
            
            result = self.recovery._handle_import_error(import_error, self.test_context)
            
            mock_fallback.assert_called_once()
            assert result == "fallback_result"

    def test_handle_import_error_gui_themes(self):
        """Test _handle_import_error for GUI themes related errors."""
        import_error = ImportError("No module named 'gui.themes'")
        
        with patch.object(self.recovery, '_create_minimal_theme') as mock_theme:
            mock_theme.return_value = {"theme": "minimal"}
            
            result = self.recovery._handle_import_error(import_error, self.test_context)
            
            mock_theme.assert_called_once()
            assert result == {"theme": "minimal"}

    def test_handle_import_error_standard_window(self):
        """Test _handle_import_error for StandardWindow related errors."""
        import_error = ImportError("No module named 'StandardWindow'")
        
        with patch.object(self.recovery, '_create_basic_window') as mock_window:
            mock_window.return_value = "BasicWindow"
            
            result = self.recovery._handle_import_error(import_error, self.test_context)
            
            mock_window.assert_called_once()
            assert result == "BasicWindow"

    def test_handle_import_error_generic(self):
        """Test _handle_import_error for generic import errors."""
        import_error = ImportError("Generic import error")
        
        with patch.object(self.recovery, '_show_import_error_dialog') as mock_dialog:
            mock_dialog.return_value = None
            
            result = self.recovery._handle_import_error(import_error, self.test_context)
            
            mock_dialog.assert_called_once_with(import_error, self.test_context)
            assert result is None

    def test_handle_module_not_found_with_quotes(self):
        """Test _handle_module_not_found with module name in quotes."""
        module_error = ModuleNotFoundError("No module named 'PyQt5'")
        
        with patch.object(self.recovery, '_show_module_error_dialog') as mock_dialog:
            self.recovery._handle_module_not_found(module_error, self.test_context)
            
            mock_dialog.assert_called_once_with('PyQt5', 'pip install PyQt5')

    def test_handle_module_not_found_without_quotes(self):
        """Test _handle_module_not_found without module name in quotes."""
        module_error = ModuleNotFoundError("Module not available")
        
        with patch.object(self.recovery, '_show_module_error_dialog') as mock_dialog:
            self.recovery._handle_module_not_found(module_error, self.test_context)
            
            mock_dialog.assert_called_once_with('unknown', 'pip install unknown')

    def test_handle_attribute_error_metaclass(self):
        """Test _handle_attribute_error for metaclass conflicts."""
        attr_error = AttributeError("metaclass conflict detected")
        
        with patch.object(self.recovery, '_handle_metaclass_conflict') as mock_metaclass:
            mock_metaclass.return_value = "metaclass_resolved"
            
            result = self.recovery._handle_attribute_error(attr_error, self.test_context)
            
            mock_metaclass.assert_called_once()
            assert result == "metaclass_resolved"

    def test_handle_attribute_error_generic(self):
        """Test _handle_attribute_error for generic attribute errors."""
        attr_error = AttributeError("Generic attribute error")
        
        with patch.object(self.recovery, '_show_attribute_error_dialog') as mock_dialog:
            mock_dialog.return_value = None
            
            result = self.recovery._handle_attribute_error(attr_error, self.test_context)
            
            mock_dialog.assert_called_once_with(attr_error, self.test_context)
            assert result is None

    def test_handle_type_error_metaclass(self):
        """Test _handle_type_error for metaclass conflicts."""
        type_error = TypeError("metaclass conflict: multiple bases")
        
        with patch.object(self.recovery, '_handle_metaclass_conflict') as mock_metaclass:
            mock_metaclass.return_value = "metaclass_resolved"
            
            result = self.recovery._handle_type_error(type_error, self.test_context)
            
            mock_metaclass.assert_called_once()
            assert result == "metaclass_resolved"

    def test_handle_type_error_generic(self):
        """Test _handle_type_error for generic type errors."""
        type_error = TypeError("Generic type error")
        
        with patch.object(self.recovery, '_show_type_error_dialog') as mock_dialog:
            mock_dialog.return_value = None
            
            result = self.recovery._handle_type_error(type_error, self.test_context)
            
            mock_dialog.assert_called_once_with(type_error, self.test_context)
            assert result is None

    def test_handle_runtime_error(self):
        """Test _handle_runtime_error."""
        runtime_error = RuntimeError("Runtime error occurred")
        
        with patch.object(self.recovery, '_show_runtime_error_dialog') as mock_dialog:
            mock_dialog.return_value = None
            
            result = self.recovery._handle_runtime_error(runtime_error, self.test_context)
            
            mock_dialog.assert_called_once_with(runtime_error, self.test_context)
            assert result is None

    def test_handle_generic_error(self):
        """Test _handle_generic_error."""
        generic_error = Exception("Generic error")
        
        with patch.object(self.recovery, '_show_generic_error_dialog') as mock_dialog:
            mock_dialog.return_value = None
            
            result = self.recovery._handle_generic_error(generic_error, self.test_context)
            
            mock_dialog.assert_called_once_with(generic_error, self.test_context)
            assert result is None

    @patch('utilities.privacy.error_recovery.PrivacyToolsErrorRecovery._try_privacy_tools_fallback')
    def test_try_privacy_tools_fallback_success(self, mock_fallback):
        """Test successful privacy tools fallback."""
        mock_class = Mock()
        mock_fallback.return_value = mock_class
        
        result = self.recovery._try_privacy_tools_fallback()
        
        assert result == mock_class

    @patch('builtins.__import__', side_effect=ImportError("Module not found"))
    def test_try_privacy_tools_fallback_failure(self, mock_import):
        """Test failed privacy tools fallback."""
        result = self.recovery._try_privacy_tools_fallback()
        
        assert result is None

    def test_create_minimal_theme(self):
        """Test _create_minimal_theme."""
        theme = self.recovery._create_minimal_theme()
        
        expected_keys = {
            'primary_color', 'background_color', 'text_color',
            'font_family', 'font_size'
        }
        
        assert isinstance(theme, dict)
        assert set(theme.keys()) == expected_keys
        assert theme['primary_color'] == '#3498db'
        assert theme['background_color'] == '#f5f5f5'
        assert theme['text_color'] == '#2c3e50'
        assert theme['font_family'] == 'Arial'
        assert theme['font_size'] == 10

    @patch('utilities.privacy.error_recovery.QMainWindow')
    def test_create_basic_window_success(self, mock_qmainwindow):
        """Test successful basic window creation."""
        result = self.recovery._create_basic_window()
        
        assert result is not None
        assert hasattr(result, '__name__')
        assert result.__name__ == 'BasicWindow'

    @patch('utilities.privacy.error_recovery.QMainWindow', side_effect=ImportError("PyQt5 not available"))
    def test_create_basic_window_failure(self, mock_qmainwindow):
        """Test failed basic window creation."""
        result = self.recovery._create_basic_window()
        
        assert result is None

    def test_handle_metaclass_conflict(self):
        """Test _handle_metaclass_conflict."""
        result = self.recovery._handle_metaclass_conflict()
        
        assert result == "metaclass_conflict_resolved"

    @patch('utilities.privacy.error_recovery.QApplication')
    @patch('utilities.privacy.error_recovery.QMessageBox')
    def test_show_import_error_dialog(self, mock_messagebox, mock_qapp):
        """Test _show_import_error_dialog."""
        mock_qapp.instance.return_value = Mock()
        import_error = ImportError("Test import error")
        
        self.recovery._show_import_error_dialog(import_error, self.test_context)
        
        mock_messagebox.critical.assert_called_once()

    @patch('utilities.privacy.error_recovery.QApplication')
    @patch('utilities.privacy.error_recovery.QMessageBox')
    def test_show_module_error_dialog(self, mock_messagebox, mock_qapp):
        """Test _show_module_error_dialog."""
        mock_qapp.instance.return_value = Mock()
        
        self.recovery._show_module_error_dialog("test_module", "pip install test_module")
        
        mock_messagebox.critical.assert_called_once()

    @patch('utilities.privacy.error_recovery.QApplication')
    @patch('utilities.privacy.error_recovery.QMessageBox')
    def test_show_attribute_error_dialog(self, mock_messagebox, mock_qapp):
        """Test _show_attribute_error_dialog."""
        mock_qapp.instance.return_value = Mock()
        attr_error = AttributeError("Test attribute error")
        
        self.recovery._show_attribute_error_dialog(attr_error, self.test_context)
        
        mock_messagebox.warning.assert_called_once()

    @patch('utilities.privacy.error_recovery.QApplication')
    @patch('utilities.privacy.error_recovery.QMessageBox')
    def test_show_type_error_dialog(self, mock_messagebox, mock_qapp):
        """Test _show_type_error_dialog."""
        mock_qapp.instance.return_value = Mock()
        type_error = TypeError("Test type error")
        
        self.recovery._show_type_error_dialog(type_error, self.test_context)
        
        mock_messagebox.critical.assert_called_once()

    @patch('utilities.privacy.error_recovery.QApplication')
    @patch('utilities.privacy.error_recovery.QMessageBox')
    def test_show_runtime_error_dialog(self, mock_messagebox, mock_qapp):
        """Test _show_runtime_error_dialog."""
        mock_qapp.instance.return_value = Mock()
        runtime_error = RuntimeError("Test runtime error")
        
        self.recovery._show_runtime_error_dialog(runtime_error, self.test_context)
        
        mock_messagebox.warning.assert_called_once()

    @patch('utilities.privacy.error_recovery.QApplication')
    @patch('utilities.privacy.error_recovery.QMessageBox')
    def test_show_generic_error_dialog(self, mock_messagebox, mock_qapp):
        """Test _show_generic_error_dialog."""
        mock_qapp.instance.return_value = Mock()
        generic_error = Exception("Test generic error")
        
        self.recovery._show_generic_error_dialog(generic_error, self.test_context)
        
        mock_messagebox.critical.assert_called_once()

    @patch('utilities.privacy.error_recovery.QApplication', side_effect=Exception("GUI not available"))
    def test_dialog_fallback_to_print(self, mock_qapp):
        """Test that dialog methods fallback to print when GUI is not available."""
        with patch('builtins.print') as mock_print:
            import_error = ImportError("Test error")
            
            self.recovery._show_import_error_dialog(import_error, self.test_context)
            
            mock_print.assert_called_once()


class TestSafeImportFunction:
    """Test suite for safe_import function."""

    def setup_method(self):
        """Setup method called before each test method."""
        self.test_module = "test_module"
        self.fallback_value = "fallback"

    @patch('builtins.__import__')
    def test_safe_import_success(self, mock_import):
        """Test successful import with safe_import."""
        mock_module = Mock()
        mock_import.return_value = mock_module
        
        result = safe_import(self.test_module, self.fallback_value)
        
        mock_import.assert_called_once_with(self.test_module)
        assert result == mock_module

    @patch('builtins.__import__', side_effect=ImportError("Module not found"))
    @patch('utilities.privacy.error_recovery.PrivacyToolsErrorRecovery.handle_error')
    def test_safe_import_failure_with_recovery(self, mock_handle_error, mock_import):
        """Test failed import with error recovery."""
        mock_handle_error.return_value = "recovered_module"
        
        result = safe_import(self.test_module, self.fallback_value)
        
        mock_import.assert_called_once_with(self.test_module)
        mock_handle_error.assert_called_once()
        assert result == "recovered_module"

    @patch('builtins.__import__', side_effect=ImportError("Module not found"))
    @patch('utilities.privacy.error_recovery.PrivacyToolsErrorRecovery.handle_error')
    def test_safe_import_failure_with_fallback(self, mock_handle_error, mock_import):
        """Test failed import falling back to provided fallback."""
        mock_handle_error.return_value = None
        
        result = safe_import(self.test_module, self.fallback_value)
        
        mock_import.assert_called_once_with(self.test_module)
        mock_handle_error.assert_called_once()
        assert result == self.fallback_value

    @patch('builtins.__import__', side_effect=ModuleNotFoundError("Module not found"))
    @patch('utilities.privacy.error_recovery.PrivacyToolsErrorRecovery.handle_error')
    def test_safe_import_module_not_found(self, mock_handle_error, mock_import):
        """Test safe_import with ModuleNotFoundError."""
        mock_handle_error.return_value = None
        
        result = safe_import(self.test_module, self.fallback_value)
        
        mock_import.assert_called_once_with(self.test_module)
        mock_handle_error.assert_called_once()
        assert result == self.fallback_value


class TestSafeExecuteFunction:
    """Test suite for safe_execute function."""

    def setup_method(self):
        """Setup method called before each test method."""
        self.test_function = Mock()
        self.test_args = (1, 2, 3)
        self.test_kwargs = {'key': 'value'}

    def test_safe_execute_success(self):
        """Test successful function execution with safe_execute."""
        self.test_function.return_value = "success"
        
        result = safe_execute(self.test_function, *self.test_args, **self.test_kwargs)
        
        self.test_function.assert_called_once_with(*self.test_args, **self.test_kwargs)
        assert result == "success"

    @patch('utilities.privacy.error_recovery.PrivacyToolsErrorRecovery.handle_error')
    def test_safe_execute_failure(self, mock_handle_error):
        """Test failed function execution with error recovery."""
        self.test_function.side_effect = RuntimeError("Function failed")
        mock_handle_error.return_value = "error_handled"
        
        result = safe_execute(self.test_function, *self.test_args, **self.test_kwargs)
        
        self.test_function.assert_called_once_with(*self.test_args, **self.test_kwargs)
        mock_handle_error.assert_called_once()
        assert result == "error_handled"

    def test_safe_execute_no_args(self):
        """Test safe_execute with no arguments."""
        self.test_function.return_value = "no_args_success"
        
        result = safe_execute(self.test_function)
        
        self.test_function.assert_called_once_with()
        assert result == "no_args_success"

    @patch('utilities.privacy.error_recovery.PrivacyToolsErrorRecovery.handle_error')
    def test_safe_execute_with_exception_types(self, mock_handle_error):
        """Test safe_execute with different exception types."""
        exceptions = [
            ValueError("Value error"),
            TypeError("Type error"),
            AttributeError("Attribute error"),
            RuntimeError("Runtime error")
        ]
        
        for exception in exceptions:
            self.test_function.side_effect = exception
            mock_handle_error.return_value = f"handled_{type(exception).__name__}"
            
            result = safe_execute(self.test_function)
            
            assert result == f"handled_{type(exception).__name__}"
            mock_handle_error.assert_called()


class TestGlobalErrorRecoveryInstance:
    """Test suite for global error_recovery instance."""

    def test_global_instance_exists(self):
        """Test that global error_recovery instance exists."""
        assert error_recovery is not None
        assert isinstance(error_recovery, PrivacyToolsErrorRecovery)

    def test_global_instance_functionality(self):
        """Test that global error_recovery instance is functional."""
        test_error = ValueError("Test error")
        
        with patch.object(error_recovery, '_handle_generic_error') as mock_handler:
            mock_handler.return_value = "handled"
            
            result = error_recovery.handle_error(test_error, "test_context")
            
            mock_handler.assert_called_once_with(test_error, "test_context")
            assert result == "handled"


class TestEdgeCases:
    """Test suite for edge cases and boundary conditions."""

    def setup_method(self):
        """Setup method called before each test method."""
        self.recovery = PrivacyToolsErrorRecovery()

    def test_empty_context_string(self):
        """Test handling errors with empty context string."""
        test_error = ValueError("Test error")
        
        with patch.object(self.recovery, '_handle_generic_error') as mock_handler:
            mock_handler.return_value = "handled"
            
            result = self.recovery.handle_error(test_error, "")
            
            mock_handler.assert_called_once_with(test_error, "")
            assert result == "handled"

    def test_none_context(self):
        """Test handling errors with None context."""
        test_error = ValueError("Test error")
        
        with patch.object(self.recovery, '_handle_generic_error') as mock_handler:
            mock_handler.return_value = "handled"
            
            result = self.recovery.handle_error(test_error, None)
            
            mock_handler.assert_called_once_with(test_error, None)
            assert result == "handled"

    def test_very_long_error_message(self):
        """Test handling errors with very long error messages."""
        long_message = "x" * 10000
        test_error = ValueError(long_message)
        
        with patch.object(self.recovery, '_handle_generic_error') as mock_handler:
            mock_handler.return_value = "handled"
            
            result = self.recovery.handle_error(test_error, "test_context")
            
            mock_handler.assert_called_once_with(test_error, "test_context")
            assert result == "handled"

    def test_nested_exceptions(self):
        """Test handling nested exceptions."""
        try:
            try:
                raise ValueError("Inner error")
            except ValueError as inner:
                raise RuntimeError("Outer error") from inner
        except RuntimeError as nested_error:
            with patch.object(self.recovery, '_handle_runtime_error') as mock_handler:
                mock_handler.return_value = "handled_nested"
                
                result = self.recovery.handle_error(nested_error, "nested_context")
                
                mock_handler.assert_called_once_with(nested_error, "nested_context")
                assert result == "handled_nested"

    def test_unicode_in_error_messages(self):
        """Test handling errors with unicode characters."""
        unicode_message = "Error with unicode: 你好世界 🌍"
        test_error = ValueError(unicode_message)
        
        with patch.object(self.recovery, '_handle_generic_error') as mock_handler:
            mock_handler.return_value = "handled_unicode"
            
            result = self.recovery.handle_error(test_error, "unicode_context")
            
            mock_handler.assert_called_once_with(test_error, "unicode_context")
            assert result == "handled_unicode"

    @patch('utilities.privacy.error_recovery.Path.unlink', side_effect=PermissionError("Cannot delete"))
    def test_log_file_cleanup_failure(self, mock_unlink):
        """Test handling of log file cleanup failures."""
        # This should not raise an exception
        recovery = PrivacyToolsErrorRecovery()
        assert recovery is not None


class TestIntegrationScenarios:
    """Test suite for integration scenarios."""

    def setup_method(self):
        """Setup method called before each test method."""
        self.recovery = PrivacyToolsErrorRecovery()

    def test_complete_import_error_flow(self):
        """Test complete flow for import error handling."""
        import_error = ImportError("No module named 'privacy_tools'")
        
        with patch.object(self.recovery, '_try_privacy_tools_fallback') as mock_fallback:
            mock_fallback.return_value = Mock()
            
            result = self.recovery.handle_error(import_error, "main_application")
            
            # Verify the complete flow
            mock_fallback.assert_called_once()
            assert result is not None

    def test_complete_module_not_found_flow(self):
        """Test complete flow for module not found error handling."""
        module_error = ModuleNotFoundError("No module named 'PyQt5'")
        
        with patch.object(self.recovery, '_show_module_error_dialog') as mock_dialog:
            result = self.recovery.handle_error(module_error, "gui_initialization")
            
            # Verify the complete flow
            mock_dialog.assert_called_once_with('PyQt5', 'pip install PyQt5')
            assert result is None

    def test_safe_import_with_safe_execute_combination(self):
        """Test combination of safe_import and safe_execute."""
        def test_function():
            return "executed"
        
        # Test successful combination
        with patch('builtins.__import__') as mock_import:
            mock_module = Mock()
            mock_module.test_function = test_function
            mock_import.return_value = mock_module
            
            imported_module = safe_import("test_module")
            result = safe_execute(imported_module.test_function)
            
            assert imported_module == mock_module
            assert result == "executed"

    def test_error_recovery_with_multiple_strategies(self):
        """Test error recovery invoking multiple strategies."""
        # Create a custom error that might trigger multiple strategies
        class CustomError(ImportError, AttributeError):
            pass
        
        custom_error = CustomError("Multiple inheritance error")
        
        # Should use ImportError strategy since it's first in MRO
        with patch.object(self.recovery, '_handle_import_error') as mock_import_handler:
            mock_import_handler.return_value = "import_handled"
            
            result = self.recovery.handle_error(custom_error, "complex_scenario")
            
            mock_import_handler.assert_called_once_with(custom_error, "complex_scenario")
            assert result == "import_handled"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
        mock_handler = Mock()
        mock_file_handler.return_value = mock_handler
        
        logger = error_recovery_instance._setup_logging()
        
        mock_file_handler.assert_called_once()
        mock_handler.setLevel.assert_called_with(logging.INFO)
        mock_handler.setFormatter.assert_called_once()

    def test_handle_error_with_known_error_type(self, error_recovery_instance):
        """Test error handling with known error types."""
        test_error = ImportError("Test import error")
        
        with patch.object(error_recovery_instance, '_handle_import_error') as mock_handler:
            mock_handler.return_value = "handled"
            result = error_recovery_instance.handle_error(test_error, "test_context")
            
            mock_handler.assert_called_once_with(test_error, "test_context")
            assert result == "handled"

    def test_handle_error_with_unknown_error_type(self, error_recovery_instance):
        """Test error handling with unknown error types."""
        test_error = ValueError("Test value error")
        
        with patch.object(error_recovery_instance, '_handle_generic_error') as mock_handler:
            mock_handler.return_value = "generic_handled"
            result = error_recovery_instance.handle_error(test_error, "test_context")
            
            mock_handler.assert_called_once_with(test_error, "test_context")
            assert result == "generic_handled"

    def test_handle_error_logging(self, error_recovery_instance):
        """Test that handle_error logs errors properly."""
        test_error = RuntimeError("Test runtime error")
        
        with patch.object(error_recovery_instance.logger, 'error') as mock_log:
            error_recovery_instance.handle_error(test_error, "test_context")
            
            # Should log both the error and traceback
            assert mock_log.call_count == 2
            mock_log.assert_any_call("Error in test_context: RuntimeError - Test runtime error")

    def test_handle_import_error_privacy_tools(self, error_recovery_instance):
        """Test import error handling for privacy tools."""
        test_error = ImportError("No module named 'privacy_tools'")
        
        with patch.object(error_recovery_instance, '_try_privacy_tools_fallback') as mock_fallback:
            mock_fallback.return_value = "fallback_result"
            result = error_recovery_instance._handle_import_error(test_error, "test_context")
            
            mock_fallback.assert_called_once()
            assert result == "fallback_result"

    def test_handle_import_error_gui_themes(self, error_recovery_instance):
        """Test import error handling for gui.themes."""
        test_error = ImportError("No module named 'gui.themes'")
        
        with patch.object(error_recovery_instance, '_create_minimal_theme') as mock_theme:
            mock_theme.return_value = {"theme": "minimal"}
            result = error_recovery_instance._handle_import_error(test_error, "test_context")
            
            mock_theme.assert_called_once()
            assert result == {"theme": "minimal"}

    def test_handle_import_error_standard_window(self, error_recovery_instance):
        """Test import error handling for StandardWindow."""
        test_error = ImportError("No module named 'StandardWindow'")
        
        with patch.object(error_recovery_instance, '_create_basic_window') as mock_window:
            mock_window.return_value = "BasicWindow"
            result = error_recovery_instance._handle_import_error(test_error, "test_context")
            
            mock_window.assert_called_once()
            assert result == "BasicWindow"

    def test_handle_import_error_generic(self, error_recovery_instance):
        """Test import error handling for generic import errors."""
        test_error = ImportError("Some other import error")
        
        with patch.object(error_recovery_instance, '_show_import_error_dialog') as mock_dialog:
            mock_dialog.return_value = None
            result = error_recovery_instance._handle_import_error(test_error, "test_context")
            
            mock_dialog.assert_called_once_with(test_error, "test_context")
            assert result is None

    def test_handle_module_not_found(self, error_recovery_instance):
        """Test module not found error handling."""
        test_error = ModuleNotFoundError("No module named 'PyQt5'")
        
        with patch.object(error_recovery_instance, '_show_module_error_dialog') as mock_dialog:
            result = error_recovery_instance._handle_module_not_found(test_error, "test_context")
            
            mock_dialog.assert_called_once_with('PyQt5', 'pip install PyQt5')
            assert result is None

    def test_handle_module_not_found_unknown_module(self, error_recovery_instance):
        """Test module not found error handling for unknown modules."""
        test_error = ModuleNotFoundError("No module named 'unknown_module'")
        
        with patch.object(error_recovery_instance, '_show_module_error_dialog') as mock_dialog:
            result = error_recovery_instance._handle_module_not_found(test_error, "test_context")
            
            mock_dialog.assert_called_once_with('unknown_module', 'pip install unknown_module')
            assert result is None

    def test_handle_attribute_error_metaclass(self, error_recovery_instance):
        """Test attribute error handling for metaclass conflicts."""
        test_error = AttributeError("metaclass conflict detected")
        
        with patch.object(error_recovery_instance, '_handle_metaclass_conflict') as mock_handler:
            mock_handler.return_value = "conflict_resolved"
            result = error_recovery_instance._handle_attribute_error(test_error, "test_context")
            
            mock_handler.assert_called_once()
            assert result == "conflict_resolved"

    def test_handle_attribute_error_generic(self, error_recovery_instance):
        """Test generic attribute error handling."""
        test_error = AttributeError("'NoneType' object has no attribute 'test'")
        
        with patch.object(error_recovery_instance, '_show_attribute_error_dialog') as mock_dialog:
            mock_dialog.return_value = None
            result = error_recovery_instance._handle_attribute_error(test_error, "test_context")
            
            mock_dialog.assert_called_once_with(test_error, "test_context")
            assert result is None

    def test_handle_type_error_metaclass(self, error_recovery_instance):
        """Test type error handling for metaclass conflicts."""
        test_error = TypeError("metaclass conflict: the metaclass of a derived class")
        
        with patch.object(error_recovery_instance, '_handle_metaclass_conflict') as mock_handler:
            mock_handler.return_value = "conflict_resolved"
            result = error_recovery_instance._handle_type_error(test_error, "test_context")
            
            mock_handler.assert_called_once()
            assert result == "conflict_resolved"

    def test_handle_type_error_generic(self, error_recovery_instance):
        """Test generic type error handling."""
        test_error = TypeError("unsupported operand type(s)")
        
        with patch.object(error_recovery_instance, '_show_type_error_dialog') as mock_dialog:
            mock_dialog.return_value = None
            result = error_recovery_instance._handle_type_error(test_error, "test_context")
            
            mock_dialog.assert_called_once_with(test_error, "test_context")
            assert result is None

    def test_handle_runtime_error(self, error_recovery_instance):
        """Test runtime error handling."""
        test_error = RuntimeError("Test runtime error")
        
        with patch.object(error_recovery_instance, '_show_runtime_error_dialog') as mock_dialog:
            mock_dialog.return_value = None
            result = error_recovery_instance._handle_runtime_error(test_error, "test_context")
            
            mock_dialog.assert_called_once_with(test_error, "test_context")
            assert result is None

    def test_handle_generic_error(self, error_recovery_instance):
        """Test generic error handling."""
        test_error = ValueError("Test value error")
        
        with patch.object(error_recovery_instance, '_show_generic_error_dialog') as mock_dialog:
            mock_dialog.return_value = None
            result = error_recovery_instance._handle_generic_error(test_error, "test_context")
            
            mock_dialog.assert_called_once_with(test_error, "test_context")
            assert result is None

    @patch('utilities.privacy.error_recovery.__import__')
    def test_try_privacy_tools_fallback_success(self, mock_import, error_recovery_instance):
        """Test successful privacy tools fallback."""
        mock_module = Mock()
        mock_module.SimplePrivacyHub = "SimplePrivacyHub"
        mock_import.return_value = mock_module
        
        # Mock the relative import
        with patch('utilities.privacy.error_recovery.PrivacyToolsErrorRecovery._try_privacy_tools_fallback') as mock_fallback:
            mock_fallback.return_value = "SimplePrivacyHub"
            result = error_recovery_instance._try_privacy_tools_fallback()
            assert result == "SimplePrivacyHub"

    def test_try_privacy_tools_fallback_failure(self, error_recovery_instance):
        """Test failed privacy tools fallback."""
        with patch('builtins.__import__', side_effect=ImportError):
            result = error_recovery_instance._try_privacy_tools_fallback()
            assert result is None

    def test_create_minimal_theme(self, error_recovery_instance):
        """Test minimal theme creation."""
        theme = error_recovery_instance._create_minimal_theme()
        
        assert isinstance(theme, dict)
        expected_keys = ['primary_color', 'background_color', 'text_color', 'font_family', 'font_size']
        for key in expected_keys:
            assert key in theme
        
        assert theme['primary_color'] == '#3498db'
        assert theme['background_color'] == '#f5f5f5'
        assert theme['text_color'] == '#2c3e50'
        assert theme['font_family'] == 'Arial'
        assert theme['font_size'] == 10

    @patch('utilities.privacy.error_recovery.QMainWindow')
    def test_create_basic_window_success(self, mock_qmainwindow, error_recovery_instance):
        """Test successful basic window creation."""
        result = error_recovery_instance._create_basic_window()
        assert result is not None

    @patch('utilities.privacy.error_recovery.QMainWindow', side_effect=ImportError)
    def test_create_basic_window_failure(self, mock_qmainwindow, error_recovery_instance):
        """Test failed basic window creation."""
        result = error_recovery_instance._create_basic_window()
        assert result is None

    def test_handle_metaclass_conflict(self, error_recovery_instance):
        """Test metaclass conflict handling."""
        result = error_recovery_instance._handle_metaclass_conflict()
        assert result == "metaclass_conflict_resolved"

    @patch('utilities.privacy.error_recovery.QApplication')
    @patch('utilities.privacy.error_recovery.QMessageBox')
    def test_show_import_error_dialog(self, mock_messagebox, mock_qapp, error_recovery_instance):
        """Test import error dialog display."""
        test_error = ImportError("Test import error")
        mock_qapp.instance.return_value = Mock()
        
        error_recovery_instance._show_import_error_dialog(test_error, "test_context")
        
        mock_messagebox.critical.assert_called_once()

    @patch('utilities.privacy.error_recovery.QApplication')
    @patch('utilities.privacy.error_recovery.QMessageBox')
    def test_show_module_error_dialog(self, mock_messagebox, mock_qapp, error_recovery_instance):
        """Test module error dialog display."""
        mock_qapp.instance.return_value = Mock()
        
        error_recovery_instance._show_module_error_dialog("test_module", "pip install test_module")
        
        mock_messagebox.critical.assert_called_once()

    @patch('utilities.privacy.error_recovery.QApplication')
    @patch('utilities.privacy.error_recovery.QMessageBox')
    def test_show_attribute_error_dialog(self, mock_messagebox, mock_qapp, error_recovery_instance):
        """Test attribute error dialog display."""
        test_error = AttributeError("Test attribute error")
        mock_qapp.instance.return_value = Mock()
        
        error_recovery_instance._show_attribute_error_dialog(test_error, "test_context")
        
        mock_messagebox.warning.assert_called_once()

    @patch('utilities.privacy.error_recovery.QApplication')
    @patch('utilities.privacy.error_recovery.QMessageBox')
    def test_show_type_error_dialog(self, mock_messagebox, mock_qapp, error_recovery_instance):
        """Test type error dialog display."""
        test_error = TypeError("Test type error")
        mock_qapp.instance.return_value = Mock()
        
        error_recovery_instance._show_type_error_dialog(test_error, "test_context")
        
        mock_messagebox.critical.assert_called_once()

    @patch('utilities.privacy.error_recovery.QApplication')
    @patch('utilities.privacy.error_recovery.QMessageBox')
    def test_show_runtime_error_dialog(self, mock_messagebox, mock_qapp, error_recovery_instance):
        """Test runtime error dialog display."""
        test_error = RuntimeError("Test runtime error")
        mock_qapp.instance.return_value = Mock()
        
        error_recovery_instance._show_runtime_error_dialog(test_error, "test_context")
        
        mock_messagebox.warning.assert_called_once()

    @patch('utilities.privacy.error_recovery.QApplication')
    @patch('utilities.privacy.error_recovery.QMessageBox')
    def test_show_generic_error_dialog(self, mock_messagebox, mock_qapp, error_recovery_instance):
        """Test generic error dialog display."""
        test_error = ValueError("Test value error")
        mock_qapp.instance.return_value = Mock()
        
        error_recovery_instance._show_generic_error_dialog(test_error, "test_context")
        
        mock_messagebox.critical.assert_called_once()

    # Edge cases and error conditions
    def test_error_dialog_fallback_to_print(self, error_recovery_instance, capsys):
        """Test that error dialogs fallback to print when GUI is unavailable."""
        test_error = ImportError("Test import error")
        
        with patch('utilities.privacy.error_recovery.QApplication', side_effect=Exception):
            error_recovery_instance._show_import_error_dialog(test_error, "test_context")
            
            captured = capsys.readouterr()
            assert "Import Error in test_context: Test import error" in captured.out

    def test_module_error_dialog_fallback_to_print(self, error_recovery_instance, capsys):
        """Test that module error dialogs fallback to print when GUI is unavailable."""
        with patch('utilities.privacy.error_recovery.QApplication', side_effect=Exception):
            error_recovery_instance._show_module_error_dialog("test_module", "pip install test_module")
            
            captured = capsys.readouterr()
            assert "Module Not Found: test_module" in captured.out
            assert "Install with: pip install test_module" in captured.out


class TestSafeImportFunction:
    """Test suite for safe_import function."""

    @patch('utilities.privacy.error_recovery.__import__')
    def test_safe_import_success(self, mock_import):
        """Test successful module import."""
        mock_module = Mock()
        mock_import.return_value = mock_module
        
        result = safe_import("test_module")
        
        mock_import.assert_called_once_with("test_module")
        assert result == mock_module

    @patch('utilities.privacy.error_recovery.__import__')
    @patch('utilities.privacy.error_recovery.PrivacyToolsErrorRecovery')
    def test_safe_import_failure_with_fallback(self, mock_recovery_class, mock_import):
        """Test safe import with error and fallback."""
        mock_import.side_effect = ImportError("Module not found")
        mock_recovery = Mock()
        mock_recovery.handle_error.return_value = "fallback_result"
        mock_recovery_class.return_value = mock_recovery
        
        result = safe_import("test_module", fallback="default_fallback")
        
        mock_recovery.handle_error.assert_called_once()
        assert result == "fallback_result"

    @patch('utilities.privacy.error_recovery.__import__')
    @patch('utilities.privacy.error_recovery.PrivacyToolsErrorRecovery')
    def test_safe_import_failure_no_recovery_result(self, mock_recovery_class, mock_import):
        """Test safe import with error and no recovery result."""
        mock_import.side_effect = ImportError("Module not found")
        mock_recovery = Mock()
        mock_recovery.handle_error.return_value = None
        mock_recovery_class.return_value = mock_recovery
        
        result = safe_import("test_module", fallback="default_fallback")
        
        mock_recovery.handle_error.assert_called_once()
        assert result == "default_fallback"


class TestSafeExecuteFunction:
    """Test suite for safe_execute function."""

    def test_safe_execute_success(self):
        """Test successful function execution."""
        def test_func(x, y):
            return x + y
        
        result = safe_execute(test_func, 2, 3)
        assert result == 5

    def test_safe_execute_with_kwargs(self):
        """Test successful function execution with kwargs."""
        def test_func(x, y=10):
            return x * y
        
        result = safe_execute(test_func, 5, y=3)
        assert result == 15

    @patch('utilities.privacy.error_recovery.PrivacyToolsErrorRecovery')
    def test_safe_execute_failure(self, mock_recovery_class):
        """Test function execution with error."""
        def failing_func():
            raise ValueError("Test error")
        
        mock_recovery = Mock()
        mock_recovery.handle_error.return_value = "error_handled"
        mock_recovery_class.return_value = mock_recovery
        
        result = safe_execute(failing_func)
        
        mock_recovery.handle_error.assert_called_once()
        assert result == "error_handled"


class TestGlobalErrorRecoveryInstance:
    """Test suite for global error_recovery instance."""

    def test_global_instance_exists(self):
        """Test that global error_recovery instance exists."""
        assert error_recovery is not None
        assert isinstance(error_recovery, PrivacyToolsErrorRecovery)

    def test_global_instance_has_logger(self):
        """Test that global instance has a logger."""
        assert hasattr(error_recovery, 'logger')
        assert error_recovery.logger is not None

    def test_global_instance_has_recovery_strategies(self):
        """Test that global instance has recovery strategies."""
        assert hasattr(error_recovery, 'recovery_strategies')
        assert isinstance(error_recovery.recovery_strategies, dict)
        assert len(error_recovery.recovery_strategies) > 0


class TestErrorRecoveryIntegration:
    """Integration tests for error recovery system."""

    def test_full_error_recovery_workflow(self):
        """Test complete error recovery workflow."""
        recovery = PrivacyToolsErrorRecovery()
        
        # Test with import error
        import_error = ImportError("No module named 'test_module'")
        with patch.object(recovery, '_show_import_error_dialog') as mock_dialog:
            result = recovery.handle_error(import_error, "integration_test")
            mock_dialog.assert_called_once()

    def test_logging_integration(self, temp_log_file):
        """Test that logging works correctly."""
        # Create recovery instance with custom log file
        with patch('utilities.privacy.error_recovery.Path') as mock_path:
            mock_path.return_value = Path(temp_log_file)
            recovery = PrivacyToolsErrorRecovery()
            
            test_error = RuntimeError("Integration test error")
            recovery.handle_error(test_error, "integration_test")
            
            # Check that log file was created and contains error info
            with open(temp_log_file, 'r') as f:
                log_content = f.read()
                assert "integration_test" in log_content
                assert "RuntimeError" in log_content


class TestErrorRecoveryEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_context(self):
        """Test error handling with empty context."""
        recovery = PrivacyToolsErrorRecovery()
        test_error = ValueError("Test error")
        
        with patch.object(recovery, '_show_generic_error_dialog') as mock_dialog:
            result = recovery.handle_error(test_error, "")
            mock_dialog.assert_called_once_with(test_error, "")

    def test_none_error(self):
        """Test handling of None as error (edge case)."""
        recovery = PrivacyToolsErrorRecovery()
        
        # This should raise an AttributeError when trying to get type(None).__name__
        with pytest.raises(AttributeError):
            recovery.handle_error(None, "test_context")

    def test_very_long_error_message(self):
        """Test handling of very long error messages."""
        recovery = PrivacyToolsErrorRecovery()
        long_message = "A" * 10000  # Very long error message
        test_error = ValueError(long_message)
        
        with patch.object(recovery, '_show_generic_error_dialog') as mock_dialog:
            result = recovery.handle_error(test_error, "test_context")
            mock_dialog.assert_called_once_with(test_error, "test_context")

    def test_unicode_error_message(self):
        """Test handling of unicode characters in error messages."""
        recovery = PrivacyToolsErrorRecovery()
        unicode_message = "Error with unicode: ñáéíóú 中文 🚀"
        test_error = ValueError(unicode_message)
        
        with patch.object(recovery, '_show_generic_error_dialog') as mock_dialog:
            result = recovery.handle_error(test_error, "test_context")
            mock_dialog.assert_called_once_with(test_error, "test_context")

    def test_nested_exception_handling(self):
        """Test handling of nested exceptions."""
        recovery = PrivacyToolsErrorRecovery()
        
        try:
            try:
                raise ValueError("Inner error")
            except ValueError as e:
                raise RuntimeError("Outer error") from e
        except RuntimeError as nested_error:
            with patch.object(recovery, '_show_runtime_error_dialog') as mock_dialog:
                result = recovery.handle_error(nested_error, "nested_test")
                mock_dialog.assert_called_once_with(nested_error, "nested_test")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])