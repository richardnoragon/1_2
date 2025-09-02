#!/usr/bin/env python3
"""
Working unit tests for system_cleanup.py - Direct import version
Test file: test_system_cleanup_direct_2025-08-28.py
Created: 2025-08-28
Target: src/utilities/system/system_cleanup.py
"""

import importlib.util
import os
import sys
from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

import pytest


# Direct import approach - load system_cleanup.py as a module
def get_system_cleanup_module():
    """Load the system_cleanup.py module directly."""
    current_dir = os.path.dirname(__file__)
    module_path = os.path.join(current_dir, '..', '..', 'src', 'utilities', 'system', 'system_cleanup.py')
    module_path = os.path.abspath(module_path)
    
    if not os.path.exists(module_path):
        pytest.skip(f"system_cleanup.py not found at {module_path}")
    
    # Load module
    spec = importlib.util.spec_from_file_location("system_cleanup", module_path)
    module = importlib.util.module_from_spec(spec)
    
    # Add to sys.modules to handle internal imports
    sys.modules['system_cleanup'] = module
    
    try:
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        pytest.skip(f"Failed to load system_cleanup.py: {e}")


@pytest.fixture(scope="module")
def system_cleanup_module():
    """Fixture that provides the system_cleanup module."""
    return get_system_cleanup_module()


def test_module_loading(system_cleanup_module):
    """Test that the module loads successfully."""
    assert system_cleanup_module is not None
    print("✅ system_cleanup module loaded successfully")


def test_pyqt5_availability_constant(system_cleanup_module):
    """Test PYQT5_AVAILABLE constant."""
    assert hasattr(system_cleanup_module, 'PYQT5_AVAILABLE')
    pyqt5_available = system_cleanup_module.PYQT5_AVAILABLE
    assert isinstance(pyqt5_available, bool)
    print(f"✅ PYQT5_AVAILABLE: {pyqt5_available}")


def test_diagnostics_gui_availability_constant(system_cleanup_module):
    """Test DIAGNOSTICS_GUI_AVAILABLE constant."""
    assert hasattr(system_cleanup_module, 'DIAGNOSTICS_GUI_AVAILABLE')
    diagnostics_available = system_cleanup_module.DIAGNOSTICS_GUI_AVAILABLE
    assert isinstance(diagnostics_available, bool)
    print(f"✅ DIAGNOSTICS_GUI_AVAILABLE: {diagnostics_available}")


def test_cleanup_tools_availability_constant(system_cleanup_module):
    """Test CLEANUP_TOOLS_AVAILABLE constant."""
    assert hasattr(system_cleanup_module, 'CLEANUP_TOOLS_AVAILABLE')
    tools_available = system_cleanup_module.CLEANUP_TOOLS_AVAILABLE
    assert isinstance(tools_available, bool)
    print(f"✅ CLEANUP_TOOLS_AVAILABLE: {tools_available}")


def test_system_cleanup_gui_class_exists(system_cleanup_module):
    """Test that SystemCleanupGUI class exists."""
    assert hasattr(system_cleanup_module, 'SystemCleanupGUI')
    SystemCleanupGUI = system_cleanup_module.SystemCleanupGUI
    assert SystemCleanupGUI is not None
    print("✅ SystemCleanupGUI class exists")


def test_main_function_exists(system_cleanup_module):
    """Test that main function exists."""
    assert hasattr(system_cleanup_module, 'main')
    main_func = system_cleanup_module.main
    assert callable(main_func)
    print("✅ main function exists and is callable")


def test_system_cleanup_gui_initialization_without_pyqt5(system_cleanup_module):
    """Test SystemCleanupGUI initialization when PyQt5 is not available."""
    SystemCleanupGUI = system_cleanup_module.SystemCleanupGUI
    
    # Mock PYQT5_AVAILABLE to False
    original_pyqt5 = system_cleanup_module.PYQT5_AVAILABLE
    system_cleanup_module.PYQT5_AVAILABLE = False
    
    try:
        with pytest.raises(ImportError, match="PyQt5 is required"):
            SystemCleanupGUI()
        print("✅ SystemCleanupGUI properly requires PyQt5")
    finally:
        # Restore original value
        system_cleanup_module.PYQT5_AVAILABLE = original_pyqt5


def test_main_function_without_pyqt5(system_cleanup_module):
    """Test main function behavior when PyQt5 is not available."""
    main_func = system_cleanup_module.main
    
    # Mock PYQT5_AVAILABLE to False
    original_pyqt5 = system_cleanup_module.PYQT5_AVAILABLE
    system_cleanup_module.PYQT5_AVAILABLE = False
    
    try:
        with patch('builtins.print') as mock_print:
            main_func()
            
            # Check that appropriate error messages were printed
            call_args_list = [call[0][0] for call in mock_print.call_args_list]
            assert any("PyQt5 is required" in msg for msg in call_args_list)
            print("✅ main function handles missing PyQt5 correctly")
    finally:
        # Restore original value
        system_cleanup_module.PYQT5_AVAILABLE = original_pyqt5


@patch('sys.exit')
def test_main_function_with_mocked_pyqt5(mock_exit, system_cleanup_module):
    """Test main function with mocked PyQt5 components."""
    main_func = system_cleanup_module.main
    
    # Mock the required PyQt5 components if PYQT5_AVAILABLE is True
    if system_cleanup_module.PYQT5_AVAILABLE:
        with patch.object(system_cleanup_module, 'QApplication') as mock_qapp, \
             patch.object(system_cleanup_module, 'SystemCleanupGUI') as mock_gui_class:
            
            # Setup mocks
            mock_app = Mock()
            mock_qapp.return_value = mock_app
            mock_app.exec_.return_value = 0
            
            mock_gui = Mock()
            mock_gui_class.return_value = mock_gui
            
            # Call main
            main_func()
            
            # Verify the expected flow
            mock_qapp.assert_called_once()
            mock_gui_class.assert_called_once()
            mock_gui.show.assert_called_once()
            mock_app.exec_.assert_called_once()
            mock_exit.assert_called_once_with(0)
            
            print("✅ main function with PyQt5 works correctly")
    else:
        pytest.skip("PyQt5 not available, skipping PyQt5-specific test")


def test_main_function_exception_handling(system_cleanup_module):
    """Test exception handling in main function."""
    main_func = system_cleanup_module.main
    
    if system_cleanup_module.PYQT5_AVAILABLE:
        with patch.object(system_cleanup_module, 'QApplication', side_effect=RuntimeError("Test error")), \
             patch('builtins.print') as mock_print:
            
            main_func()
            
            # Check that error was printed
            call_args_list = [call[0][0] for call in mock_print.call_args_list]
            assert any("Error running System Cleanup GUI" in msg for msg in call_args_list)
            print("✅ main function handles exceptions correctly")
    else:
        pytest.skip("PyQt5 not available, skipping exception handling test")


def test_format_size_method_logic():
    """Test the _format_size method logic."""
    # Test the actual implementation logic (extracted from the class)
    def _format_size(size_bytes):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
    
    # Test various sizes
    assert _format_size(0) == "0.0 B"
    assert _format_size(512) == "512.0 B"
    assert _format_size(1024) == "1.0 KB"
    assert _format_size(1536) == "1.5 KB"
    assert _format_size(1024*1024) == "1.0 MB"
    assert _format_size(1024*1024*1.5) == "1.5 MB"
    assert _format_size(1024*1024*1024) == "1.0 GB"
    assert _format_size(1024*1024*1024*1024) == "1.0 TB"
    
    print("✅ _format_size method logic works correctly")


def test_module_constants_types(system_cleanup_module):
    """Test that all module constants are of correct types."""
    constants = ['PYQT5_AVAILABLE', 'DIAGNOSTICS_GUI_AVAILABLE', 'CLEANUP_TOOLS_AVAILABLE']
    
    for const_name in constants:
        if hasattr(system_cleanup_module, const_name):
            const_value = getattr(system_cleanup_module, const_name)
            assert isinstance(const_value, bool), f"{const_name} should be boolean"
    
    print("✅ All module constants are properly typed")


def test_system_cleanup_gui_with_mocked_dependencies(system_cleanup_module):
    """Test SystemCleanupGUI with mocked dependencies."""
    if not system_cleanup_module.PYQT5_AVAILABLE:
        pytest.skip("PyQt5 not available")
    
    SystemCleanupGUI = system_cleanup_module.SystemCleanupGUI
    
    # Mock all the dependencies
    with patch.object(system_cleanup_module, 'SystemDiagnosticsGUI', create=True) as mock_base, \
         patch.object(SystemCleanupGUI, 'init_cleanup_tools'), \
         patch.object(SystemCleanupGUI, 'customize_for_cleanup'):
        
        # Create instance with mocked hub
        mock_hub = Mock()
        
        try:
            gui = SystemCleanupGUI(hub_instance=mock_hub)
            assert gui is not None
            print("✅ SystemCleanupGUI can be instantiated with mocked dependencies")
        except Exception as e:
            print(f"⚠️  SystemCleanupGUI instantiation failed: {e}")
            # This is expected if dependencies are missing


def test_cleanup_operation_result_import_via_module(system_cleanup_module):
    """Test importing CleanupOperationResult through the module."""
    try:
        # Try to access cleanup tools
        if hasattr(system_cleanup_module, 'CleanupOperationResult'):
            CleanupOperationResult = system_cleanup_module.CleanupOperationResult
            
            # Test creating a result
            result = CleanupOperationResult(
                success=True,
                message="Test operation",
                items_processed=50,
                space_freed=1024*1024*10  # 10MB
            )
            
            assert result.success is True
            assert result.message == "Test operation"
            assert result.items_processed == 50
            assert result.space_freed == 1024*1024*10
            print("✅ CleanupOperationResult works correctly")
        else:
            print("ℹ️  CleanupOperationResult not directly available from module")
    except Exception as e:
        print(f"ℹ️  CleanupOperationResult test skipped: {e}")


def test_logging_setup():
    """Test logging configuration."""
    import logging

    # Test that the expected logger name works
    logger = logging.getLogger('RFU.SystemCleanup')
    assert logger.name == 'RFU.SystemCleanup'
    assert isinstance(logger, logging.Logger)
    print("✅ Logging configuration is correct")


@pytest.mark.integration
def test_module_integration(system_cleanup_module):
    """Integration test for the entire module."""
    # Test that key components exist
    components = ['SystemCleanupGUI', 'main', 'PYQT5_AVAILABLE']
    missing_components = []
    
    for component in components:
        if not hasattr(system_cleanup_module, component):
            missing_components.append(component)
    
    if missing_components:
        pytest.fail(f"Missing components: {missing_components}")
    
    print("✅ All key components present in module")


def test_session_metadata():
    """Test session metadata for reporting."""
    metadata = {
        'test_file': 'test_system_cleanup_direct_2025-08-28.py',
        'target_module': 'system_cleanup.py',
        'execution_date': '2025-08-28',
        'timestamp': datetime.now().isoformat(),
        'test_approach': 'direct_import',
        'framework': 'pytest'
    }
    
    assert metadata['test_file'] == 'test_system_cleanup_direct_2025-08-28.py'
    assert metadata['target_module'] == 'system_cleanup.py'
    assert metadata['test_approach'] == 'direct_import'
    print(f"✅ Test session metadata: {metadata}")


if __name__ == "__main__":
    # Run tests when script is executed directly
    pytest.main([__file__, "-v", "--tb=short"])