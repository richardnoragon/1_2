"""
Import and Compatibility Testing for Size Analyzer

This module contains comprehensive tests for import paths, module loading,
backward compatibility, package exports, and deployment scenarios.
"""

import sys
import importlib
from unittest.mock import patch, Mock


class TestSizeAnalyzerImports:
    """Test Size Analyzer import functionality."""
    
    def test_core_module_imports(self):
        """Test core module imports."""
        # Test core logic import
        try:
            from file_utilities_2.core.size_analyzer_logic import (
                SizeAnalyzer, SizeAnalyzerWorker
            )
            assert SizeAnalyzer is not None
            assert SizeAnalyzerWorker is not None
        except ImportError as e:
            assert False, f"Failed to import core logic: {e}"
        
        # Test config import
        try:
            from file_utilities_2.core.size_analyzer_config import (
                SizeAnalyzerConfig
            )
            assert SizeAnalyzerConfig is not None
        except ImportError as e:
            assert False, f"Failed to import config: {e}"
        
        # Test logging import
        try:
            from file_utilities_2.core.size_analyzer_logging import (
                SizeAnalyzerLogger, get_size_analyzer_logger
            )
            assert SizeAnalyzerLogger is not None
            assert get_size_analyzer_logger is not None
        except ImportError as e:
            assert False, f"Failed to import logging: {e}"
    
    def test_gui_module_imports(self):
        """Test GUI module imports."""
        try:
            from file_utilities_2.gui.size_analyzer_gui import SizeAnalyzerGUI
            assert SizeAnalyzerGUI is not None
        except ImportError as e:
            assert False, f"Failed to import GUI: {e}"
    
    def test_integration_module_imports(self):
        """Test integration module imports."""
        try:
            from file_utilities_2.integration.hub_connector import (
                HubConnector, HubMessage, HubCommunicationProtocol
            )
            assert HubConnector is not None
            assert HubMessage is not None
            assert HubCommunicationProtocol is not None
        except ImportError as e:
            assert False, f"Failed to import integration: {e}"
    
    def test_package_level_imports(self):
        """Test package-level imports."""
        try:
            from file_utilities_2 import (
                SizeAnalyzer, SizeAnalyzerGUI, SizeAnalyzerConfig
            )
            assert SizeAnalyzer is not None
            assert SizeAnalyzerGUI is not None
            assert SizeAnalyzerConfig is not None
        except ImportError as e:
            assert False, f"Failed to import from package level: {e}"
    
    def test_relative_imports(self):
        """Test relative imports within modules."""
        # Test that modules can import from each other
        try:
            # This tests that GUI can import from core
            from file_utilities_2.gui.size_analyzer_gui import SizeAnalyzerGUI
            gui = SizeAnalyzerGUI()
            assert hasattr(gui, 'analyzer')
            gui.close()
        except Exception as e:
            assert False, f"Relative imports failed: {e}"
    
    def test_optional_dependencies(self):
        """Test handling of optional dependencies."""
        # Test PyQt5 dependency
        try:
            from PyQt5.QtWidgets import QApplication
            from PyQt5.QtCore import QObject, pyqtSignal
            assert QApplication is not None
            assert QObject is not None
            assert pyqtSignal is not None
        except ImportError:
            assert False, "PyQt5 is required but not available"
    
    def test_import_error_handling(self):
        """Test graceful handling of import errors."""
        # Mock a missing dependency
        with patch.dict('sys.modules', {'missing_module': None}):
            try:
                # This should handle missing dependencies gracefully
                from file_utilities_2.core.size_analyzer_logic import (
                    SizeAnalyzer
                )
                assert SizeAnalyzer is not None
            except ImportError as e:
                # Should not fail due to missing optional dependencies
                if 'missing_module' not in str(e):
                    assert False, f"Unexpected import error: {e}"


class TestBackwardCompatibility:
    """Test backward compatibility with legacy imports."""
    
    def test_legacy_import_paths(self):
        """Test that legacy import paths still work."""
        # Test legacy paths if they exist
        legacy_paths = [
            'file_utilities_2.core.size_analyzer_logic',
            'file_utilities_2.gui.size_analyzer_gui',
            'file_utilities_2.integration.hub_connector'
        ]
        
        for path in legacy_paths:
            try:
                module = importlib.import_module(path)
                assert module is not None
            except ImportError as e:
                assert False, f"Legacy import path failed: {path} - {e}"
    
    def test_class_name_compatibility(self):
        """Test that class names remain consistent."""
        from file_utilities_2.core.size_analyzer_logic import SizeAnalyzer
        from file_utilities_2.gui.size_analyzer_gui import SizeAnalyzerGUI
        from file_utilities_2.core.size_analyzer_config import SizeAnalyzerConfig
        
        # Verify class names
        assert SizeAnalyzer.__name__ == 'SizeAnalyzer'
        assert SizeAnalyzerGUI.__name__ == 'SizeAnalyzerGUI'
        assert SizeAnalyzerConfig.__name__ == 'SizeAnalyzerConfig'
    
    def test_method_signature_compatibility(self):
        """Test that method signatures remain compatible."""
        from file_utilities_2.core.size_analyzer_logic import SizeAnalyzer
        
        analyzer = SizeAnalyzer()
        
        # Test that key methods exist with expected signatures
        assert hasattr(analyzer, 'analyze_directory')
        assert hasattr(analyzer, 'format_size')
        assert hasattr(analyzer, 'export_analysis')
        assert hasattr(analyzer, 'cancel_operation')
        
        # Test method signatures
        import inspect
        
        # analyze_directory should accept directory_path and optional params
        sig = inspect.signature(analyzer.analyze_directory)
        params = list(sig.parameters.keys())
        assert 'directory_path' in params
        assert 'top_files_count' in params
        assert 'include_extensions' in params
        assert 'progress_callback' in params
    
    def test_signal_compatibility(self):
        """Test that PyQt signals remain compatible."""
        from file_utilities_2.core.size_analyzer_logic import SizeAnalyzer
        from PyQt5.QtCore import pyqtSignal
        
        analyzer = SizeAnalyzer()
        
        # Test that expected signals exist
        expected_signals = [
            'progress_updated',
            'progress_percentage',
            'progress_message',
            'milestone_reached',
            'time_estimate',
            'analysis_complete',
            'error_occurred',
            'operation_cancelled'
        ]
        
        for signal_name in expected_signals:
            assert hasattr(analyzer, signal_name)
            signal = getattr(analyzer, signal_name)
            assert isinstance(signal, pyqtSignal)


class TestPackageExports:
    """Test package exports and public API."""
    
    def test_package_init_exports(self):
        """Test that package __init__.py exports expected classes."""
        import file_utilities_2
        
        # Test that main classes are available at package level
        expected_exports = [
            'SizeAnalyzer',
            'SizeAnalyzerGUI',
            'SizeAnalyzerConfig',
            'SizeAnalyzerLogger'
        ]
        
        for export in expected_exports:
            assert hasattr(file_utilities_2, export), f"Missing export: {export}"
    
    def test_subpackage_exports(self):
        """Test subpackage exports."""
        # Test core subpackage
        from file_utilities_2 import core
        assert hasattr(core, 'SizeAnalyzer')
        assert hasattr(core, 'SizeAnalyzerConfig')
        assert hasattr(core, 'SizeAnalyzerLogger')
        
        # Test gui subpackage
        from file_utilities_2 import gui
        assert hasattr(gui, 'SizeAnalyzerGUI')
        
        # Test integration subpackage
        from file_utilities_2 import integration
        assert hasattr(integration, 'HubConnector')
    
    def test_public_api_stability(self):
        """Test that public API remains stable."""
        from file_utilities_2.core.size_analyzer_logic import SizeAnalyzer
        from file_utilities_2.gui.size_analyzer_gui import SizeAnalyzerGUI
        
        # Test that public methods are available
        analyzer = SizeAnalyzer()
        public_methods = [
            'analyze_directory',
            'format_size',
            'export_analysis',
            'cancel_operation',
            'is_running',
            'set_hub_connector',
            'get_performance_metrics',
            'get_resource_usage'
        ]
        
        for method in public_methods:
            assert hasattr(analyzer, method), f"Missing public method: {method}"
            assert callable(getattr(analyzer, method))
    
    def test_version_information(self):
        """Test version information availability."""
        try:
            import file_utilities_2
            # Check if version info is available
            if hasattr(file_utilities_2, '__version__'):
                version = file_utilities_2.__version__
                assert isinstance(version, str)
                assert len(version) > 0
        except AttributeError:
            # Version info might not be implemented yet
            pass


class TestCrossModuleDependencies:
    """Test cross-module dependencies and imports."""
    
    def test_core_to_integration_imports(self):
        """Test imports from core to integration modules."""
        from file_utilities_2.core.size_analyzer_logic import SizeAnalyzer
        from file_utilities_2.integration.hub_connector import HubConnector
        
        # Test that core can work with integration
        hub_connector = HubConnector("Test")
        analyzer = SizeAnalyzer(hub_connector=hub_connector)
        
        assert analyzer._hub_connector == hub_connector
    
    def test_gui_to_core_imports(self):
        """Test imports from GUI to core modules."""
        from file_utilities_2.gui.size_analyzer_gui import SizeAnalyzerGUI
        
        # Test that GUI properly imports and uses core classes
        gui = SizeAnalyzerGUI()
        assert hasattr(gui, 'analyzer')
        assert gui.analyzer is not None
        gui.close()
    
    def test_gui_to_integration_imports(self):
        """Test imports from GUI to integration modules."""
        from file_utilities_2.gui.size_analyzer_gui import SizeAnalyzerGUI
        
        # Test that GUI properly imports and uses integration classes
        gui = SizeAnalyzerGUI()
        assert hasattr(gui, 'hub_connector')
        assert gui.hub_connector is not None
        gui.close()
    
    def test_circular_import_prevention(self):
        """Test that circular imports are prevented."""
        # Import all modules to check for circular dependencies
        modules = [
            'file_utilities_2.core.size_analyzer_logic',
            'file_utilities_2.core.size_analyzer_config',
            'file_utilities_2.core.size_analyzer_logging',
            'file_utilities_2.gui.size_analyzer_gui',
            'file_utilities_2.integration.hub_connector'
        ]
        
        for module_name in modules:
            try:
                importlib.import_module(module_name)
            except ImportError as e:
                if 'circular import' in str(e).lower():
                    assert False, f"Circular import detected in {module_name}: {e}"
                # Other import errors might be due to missing dependencies
                # which is handled elsewhere


class TestDeploymentScenarios:
    """Test various deployment scenarios."""
    
    def test_standalone_import(self):
        """Test importing as standalone module."""
        # Test that modules can be imported independently
        try:
            from file_utilities_2.core.size_analyzer_logic import SizeAnalyzer
            analyzer = SizeAnalyzer()
            assert analyzer is not None
        except Exception as e:
            assert False, f"Standalone import failed: {e}"
    
    def test_frozen_application_compatibility(self):
        """Test compatibility with frozen applications (PyInstaller, etc.)."""
        # Mock frozen environment
        original_frozen = getattr(sys, 'frozen', False)
        
        try:
            sys.frozen = True
            
            # Test imports in frozen environment
            from file_utilities_2.core.size_analyzer_logic import SizeAnalyzer
            analyzer = SizeAnalyzer()
            assert analyzer is not None
            
        finally:
            if original_frozen:
                sys.frozen = original_frozen
            else:
                delattr(sys, 'frozen')
    
    def test_namespace_package_compatibility(self):
        """Test compatibility with namespace packages."""
        # Test that the package works as a namespace package
        import file_utilities_2
        
        # Check that it's properly structured
        assert hasattr(file_utilities_2, '__path__')
        assert file_utilities_2.__path__ is not None
    
    def test_import_from_different_locations(self):
        """Test importing from different filesystem locations."""
        # Test that imports work regardless of current working directory
        import os
        original_cwd = os.getcwd()
        
        try:
            # Change to a different directory
            os.chdir(os.path.expanduser('~'))
            
            # Test imports still work
            from file_utilities_2.core.size_analyzer_logic import SizeAnalyzer
            analyzer = SizeAnalyzer()
            assert analyzer is not None
            
        finally:
            os.chdir(original_cwd)


class TestImportPerformance:
    """Test import performance and efficiency."""
    
    def test_import_time(self):
        """Test that imports complete in reasonable time."""
        import time
        
        # Test core module import time
        start_time = time.time()
        from file_utilities_2.core.size_analyzer_logic import SizeAnalyzer
        core_import_time = time.time() - start_time
        
        # Should import quickly (less than 1 second)
        assert core_import_time < 1.0, f"Core import too slow: {core_import_time}s"
        
        # Test GUI module import time
        start_time = time.time()
        from file_utilities_2.gui.size_analyzer_gui import SizeAnalyzerGUI
        gui_import_time = time.time() - start_time
        
        # GUI imports might be slower due to PyQt5, but should be reasonable
        assert gui_import_time < 5.0, f"GUI import too slow: {gui_import_time}s"
    
    def test_lazy_imports(self):
        """Test that expensive imports are lazy-loaded where possible."""
        # Test that importing the package doesn't immediately load everything
        import time
        
        start_time = time.time()
        import file_utilities_2
        package_import_time = time.time() - start_time
        
        # Package import should be fast
        assert package_import_time < 0.5, f"Package import too slow: {package_import_time}s"
    
    def test_memory_usage_during_import(self):
        """Test memory usage during imports."""
        try:
            import psutil
            process = psutil.Process()
            
            # Get initial memory usage
            initial_memory = process.memory_info().rss
            
            # Import modules
            from file_utilities_2.core.size_analyzer_logic import SizeAnalyzer
            from file_utilities_2.gui.size_analyzer_gui import SizeAnalyzerGUI
            from file_utilities_2.integration.hub_connector import HubConnector
            
            # Get final memory usage
            final_memory = process.memory_info().rss
            memory_increase = final_memory - initial_memory
            
            # Memory increase should be reasonable (less than 100MB)
            assert memory_increase < 100 * 1024 * 1024, f"Import memory usage too high: {memory_increase} bytes"
            
        except ImportError:
            # psutil not available, skip this test
            pass


class TestImportErrorRecovery:
    """Test error recovery during imports."""
    
    def test_missing_optional_dependency_handling(self):
        """Test handling of missing optional dependencies."""
        # Mock missing PyQt5
        with patch.dict('sys.modules', {'PyQt5': None}):
            try:
                # This should fail gracefully
                from file_utilities_2.gui.size_analyzer_gui import SizeAnalyzerGUI
                # If it doesn't fail, that's also acceptable
            except ImportError as e:
                # Should provide helpful error message
                assert 'PyQt5' in str(e) or 'GUI' in str(e)
    
    def test_partial_import_recovery(self):
        """Test recovery from partial import failures."""
        # Test that if one module fails, others still work
        try:
            from file_utilities_2.core.size_analyzer_logic import SizeAnalyzer
            core_works = True
        except ImportError:
            core_works = False
        
        try:
            from file_utilities_2.integration.hub_connector import HubConnector
            integration_works = True
        except ImportError:
            integration_works = False
        
        # At least core functionality should work
        assert core_works, "Core functionality should always be importable"
    
    def test_import_cleanup_on_failure(self):
        """Test that failed imports don't leave partial state."""
        # This is more of a structural test
        # If imports fail, they shouldn't leave modules in sys.modules
        # in a broken state
        
        original_modules = set(sys.modules.keys())
        
        try:
            # Try to import something that might fail
            from file_utilities_2.core.size_analyzer_logic import SizeAnalyzer
        except ImportError:
            pass
        
        # Check that we didn't leave broken modules
        current_modules = set(sys.modules.keys())
        new_modules = current_modules - original_modules
        
        # Any new modules should be properly loaded
        for module_name in new_modules:
            module = sys.modules[module_name]
            assert module is not None, f"Broken module in sys.modules: {module_name}"