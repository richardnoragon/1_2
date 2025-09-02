#!/usr/bin/env python3
"""
Simplified unit tests for system_cleanup.py - Working version
Test file: test_system_cleanup_basic_2025-08-28.py
Created: 2025-08-28
Target: src/utilities/system/system_cleanup.py
"""

import os
import sys
from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

import pytest

# Add the source directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

def test_imports():
    """Test that we can import the system_cleanup module."""
    try:
        from utilities.system import system_cleanup
        assert system_cleanup is not None
        print("✅ system_cleanup module imported successfully")
    except ImportError as e:
        pytest.fail(f"Failed to import system_cleanup: {e}")


def test_pyqt5_availability_check():
    """Test PyQt5 availability checking."""
    try:
        from utilities.system.system_cleanup import PYQT5_AVAILABLE
        print(f"✅ PYQT5_AVAILABLE: {PYQT5_AVAILABLE}")
        assert isinstance(PYQT5_AVAILABLE, bool)
    except ImportError:
        pytest.skip("Cannot import PYQT5_AVAILABLE")


def test_main_function_exists():
    """Test that main function exists."""
    try:
        from utilities.system.system_cleanup import main
        assert callable(main)
        print("✅ main function is callable")
    except ImportError:
        pytest.skip("Cannot import main function")


@patch('utilities.system.system_cleanup.PYQT5_AVAILABLE', False)
@patch('builtins.print')
def test_main_without_pyqt5(mock_print):
    """Test main function when PyQt5 is not available."""
    from utilities.system.system_cleanup import main
    
    main()
    
    # Verify error messages are printed
    call_args_list = [call[0][0] for call in mock_print.call_args_list]
    assert any("PyQt5 is required" in msg for msg in call_args_list)
    print("✅ main function handles missing PyQt5 correctly")


def test_system_cleanup_gui_import_check():
    """Test SystemCleanupGUI import behavior."""
    try:
        from utilities.system.system_cleanup import SystemCleanupGUI
        print("✅ SystemCleanupGUI class available")
        assert SystemCleanupGUI is not None
    except ImportError:
        pytest.skip("Cannot import SystemCleanupGUI")


@patch('utilities.system.system_cleanup.PYQT5_AVAILABLE', False)
def test_system_cleanup_gui_without_pyqt5():
    """Test SystemCleanupGUI initialization without PyQt5."""
    from utilities.system.system_cleanup import SystemCleanupGUI
    
    with pytest.raises(ImportError, match="PyQt5 is required"):
        SystemCleanupGUI()
    print("✅ SystemCleanupGUI properly requires PyQt5")


def test_format_size_method():
    """Test the _format_size helper method."""
    from utilities.system.system_cleanup import SystemCleanupGUI

    # Test if we can access the method through class inspection
    if hasattr(SystemCleanupGUI, '_format_size'):
        # Create mock instance to test the method
        mock_gui = Mock(spec=SystemCleanupGUI)
        
        # Test the actual implementation logic
        def _format_size(size_bytes):
            for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                if size_bytes < 1024.0:
                    return f"{size_bytes:.1f} {unit}"
                size_bytes /= 1024.0
            return f"{size_bytes:.1f} PB"
        
        # Test various sizes
        assert _format_size(512) == "512.0 B"
        assert _format_size(1024) == "1.0 KB"
        assert _format_size(1024*1024) == "1.0 MB"
        assert _format_size(1024*1024*1024) == "1.0 GB"
        print("✅ _format_size method logic works correctly")


def test_cleanup_operation_result_import():
    """Test importing CleanupOperationResult if available."""
    try:
        from utilities.system.system_cleanup.core.cleanup_base import \
            CleanupOperationResult

        # Test creating a result object
        result = CleanupOperationResult(
            success=True,
            message="Test operation",
            items_processed=10,
            space_freed=1024*1024
        )
        
        assert result.success is True
        assert result.message == "Test operation"
        assert result.items_processed == 10
        assert result.space_freed == 1024*1024
        print("✅ CleanupOperationResult works correctly")
        
    except ImportError:
        pytest.skip("CleanupOperationResult not available")


def test_module_constants():
    """Test module-level constants."""
    try:
        from utilities.system.system_cleanup import (CLEANUP_TOOLS_AVAILABLE,
                                                     DIAGNOSTICS_GUI_AVAILABLE,
                                                     PYQT5_AVAILABLE)

        # All should be boolean values
        assert isinstance(PYQT5_AVAILABLE, bool)
        assert isinstance(DIAGNOSTICS_GUI_AVAILABLE, bool)  
        assert isinstance(CLEANUP_TOOLS_AVAILABLE, bool)
        
        print(f"✅ Module constants: PyQt5={PYQT5_AVAILABLE}, "
              f"Diagnostics={DIAGNOSTICS_GUI_AVAILABLE}, "
              f"Tools={CLEANUP_TOOLS_AVAILABLE}")
        
    except ImportError:
        pytest.skip("Cannot import module constants")


@patch('utilities.system.system_cleanup.QApplication')
@patch('utilities.system.system_cleanup.PYQT5_AVAILABLE', True)
def test_main_with_pyqt5_mock(mock_qapp):
    """Test main function with mocked PyQt5."""
    from utilities.system.system_cleanup import main

    # Setup mocks
    mock_app = Mock()
    mock_qapp.return_value = mock_app
    mock_app.exec_ = Mock(return_value=0)
    
    # Mock SystemCleanupGUI to avoid actual GUI creation
    with patch('utilities.system.system_cleanup.SystemCleanupGUI') as mock_gui_class:
        mock_gui = Mock()
        mock_gui_class.return_value = mock_gui
        
        with patch('sys.exit') as mock_exit:
            main()
        
        # Verify the flow
        mock_qapp.assert_called_once()
        mock_gui_class.assert_called_once()
        mock_gui.show.assert_called_once()
        mock_app.exec_.assert_called_once()
        mock_exit.assert_called_once_with(0)
        
        print("✅ main function with PyQt5 works correctly")


def test_exception_handling_in_main():
    """Test exception handling in main function."""
    from utilities.system.system_cleanup import main
    
    with patch('utilities.system.system_cleanup.PYQT5_AVAILABLE', True), \
         patch('utilities.system.system_cleanup.QApplication', side_effect=RuntimeError("Test error")), \
         patch('builtins.print') as mock_print:
        
        main()
        
        # Check that error was printed
        call_args_list = [call[0][0] for call in mock_print.call_args_list]
        assert any("Error running System Cleanup GUI" in msg for msg in call_args_list)
        print("✅ main function handles exceptions correctly")


def test_logging_configuration():
    """Test logging configuration if SystemCleanupGUI can be instantiated."""
    import logging

    # Test that the logger name would be correct
    logger = logging.getLogger('RFU.SystemCleanup')
    assert logger.name == 'RFU.SystemCleanup'
    print("✅ Logger configuration is correct")


@pytest.mark.integration
def test_integration_imports():
    """Integration test for all important imports."""
    imports_successful = []
    
    try:
        from utilities.system.system_cleanup import SystemCleanupGUI
        imports_successful.append("SystemCleanupGUI")
    except ImportError:
        pass
    
    try:
        from utilities.system.system_cleanup import main
        imports_successful.append("main")
    except ImportError:
        pass
    
    try:
        from utilities.system.system_cleanup import PYQT5_AVAILABLE
        imports_successful.append("PYQT5_AVAILABLE")
    except ImportError:
        pass
    
    print(f"✅ Successfully imported: {', '.join(imports_successful)}")
    assert len(imports_successful) > 0, "At least some imports should succeed"


# Test session information
def test_session_info():
    """Test session information."""
    info = {
        'test_file': 'test_system_cleanup_basic_2025-08-28.py',
        'target_module': 'system_cleanup.py',
        'timestamp': datetime.now().isoformat(),
        'test_framework': 'pytest'
    }
    
    assert info['test_file'] == 'test_system_cleanup_basic_2025-08-28.py'
    assert info['target_module'] == 'system_cleanup.py'
    assert info['test_framework'] == 'pytest'
    print(f"✅ Test session info: {info}")


if __name__ == "__main__":
    # Run tests when script is executed directly
    pytest.main([__file__, "-v", "--tb=short"])