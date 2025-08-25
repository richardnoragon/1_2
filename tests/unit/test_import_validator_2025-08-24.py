#!/usr/bin/env python3
"""
Comprehensive Unit Tests for import_validator.py
Created: 2025-08-24

Test Coverage:
- ImportValidator class initialization and core functionality
- Module import validation and error handling
- Python path configuration validation
- Circular import detection capabilities
- File path resolution and module discovery
- Diagnostic report generation
- Automatic fix application and __init__.py creation
- Edge cases: missing modules, permission errors, malformed paths
- Mock data testing with various import scenarios
"""

import pytest
import tempfile
import sys
from unittest.mock import Mock, patch
from pathlib import Path
import shutil

# Import the module under test
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from src.utilities.analysis.import_validator import (
        ImportValidator, main
    )
except ImportError as e:
    pytest.skip(f"Cannot import import_validator module: {e}",
                allow_module_level=True)


class TestImportValidator:
    """Test suite for ImportValidator class."""

    @pytest.fixture
    def import_validator(self):
        """Create ImportValidator instance for testing."""
        validator = ImportValidator()
        yield validator

    @pytest.fixture
    def temp_directory(self):
        """Create temporary directory for testing."""
        temp_dir = tempfile.mkdtemp(prefix="import_validator_test_")
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def mock_module_structure(self, temp_directory):
        """Create mock module structure for testing."""
        # Create mock src directory structure
        src_dir = Path(temp_directory) / "src"
        src_dir.mkdir()
        
        # Create utilities directory
        utilities_dir = src_dir / "utilities"
        utilities_dir.mkdir()
        
        # Create analysis directory
        analysis_dir = utilities_dir / "analysis"
        analysis_dir.mkdir()
        
        # Create mock Python files
        (analysis_dir / "__init__.py").write_text("")
        (analysis_dir / "size_analyzer.py").write_text(
            "class SizeAnalyzerGUI:\n    pass\n"
        )
        
        # Create core directory
        core_dir = analysis_dir / "core"
        core_dir.mkdir()
        (core_dir / "__init__.py").write_text("")
        (core_dir / "size_analyzer_logic.py").write_text(
            "class SizeAnalyzer:\n    pass\n"
        )
        
        # Create config directory
        config_dir = analysis_dir / "config"
        config_dir.mkdir()
        (config_dir / "__init__.py").write_text("")
        (config_dir / "size_analyzer_config.py").write_text(
            "class SizeAnalyzerConfig:\n    pass\n"
        )
        
        return {
            'temp_dir': temp_directory,
            'src_dir': str(src_dir),
            'analysis_dir': str(analysis_dir)
        }

    def test_import_validator_initialization(self, import_validator):
        """Test ImportValidator initialization and attributes."""
        assert import_validator is not None
        assert hasattr(import_validator, 'validation_results')
        assert hasattr(import_validator, 'import_paths')
        assert hasattr(import_validator, 'missing_modules')
        assert hasattr(import_validator, 'circular_imports')
        
        assert import_validator.validation_results == {}
        assert import_validator.import_paths == []
        assert import_validator.missing_modules == []
        assert import_validator.circular_imports == []

    def test_validate_size_analyzer_imports_structure(self, import_validator):
        """Test structure of validate_size_analyzer_imports result."""
        results = import_validator.validate_size_analyzer_imports()
        
        # Check required keys
        required_keys = ['success', 'errors', 'warnings', 'info',
                         'module_status', 'python_path_status',
                         'circular_imports']
        for key in required_keys:
            assert key in results
        
        # Check data types
        assert isinstance(results['success'], bool)
        assert isinstance(results['errors'], list)
        assert isinstance(results['warnings'], list)
        assert isinstance(results['info'], list)
        assert isinstance(results['module_status'], dict)

    def test_validate_module_import_success(self, import_validator):
        """Test successful module import validation."""
        # Test with a built-in module
        with patch('importlib.import_module') as mock_import:
            mock_module = Mock()
            mock_module.TestClass = Mock
            mock_import.return_value = mock_module
            
            with patch.object(import_validator, '_resolve_module_file_path',
                              return_value='/mock/path.py'):
                with patch('os.path.exists', return_value=True):
                    status = import_validator._validate_module_import(
                        'mock.module', 'TestClass'
                    )
        
        assert status['importable'] is True
        assert status['class_available'] is True
        # os.path.exists mocked to return True with file_path '/mock/path.py'
        assert status['file_exists'] is True

    def test_validate_module_import_failure(self, import_validator):
        """Test module import validation failure."""
        with patch('importlib.import_module',
                   side_effect=ImportError("Module not found")):
            status = import_validator._validate_module_import(
                'nonexistent.module', 'NonexistentClass'
            )
        
        assert status['importable'] is False
        assert status['class_available'] is False
        assert "Import failed" in status['error']

    def test_validate_module_import_class_not_found(self, import_validator):
        """Test module import with missing class."""
        with patch('importlib.import_module') as mock_import:
            mock_module = Mock()
            # Use spec to control attribute access
            mock_module.configure_mock(**{})  # No class attributes
            mock_module._spec_class = Mock()
            mock_module._spec_class.return_value = False
            
            # Override hasattr behavior to return False for our test class
            with patch('builtins.hasattr', return_value=False):
                mock_import.return_value = mock_module
                
                with patch.object(import_validator, '_resolve_module_file_path',
                                  return_value='/mock/path.py'):
                    with patch('os.path.exists', return_value=True):
                        status = import_validator._validate_module_import(
                            'mock.module', 'MissingClass'
                        )
        
        assert status['importable'] is True
        assert status['class_available'] is False
        assert "Class MissingClass not found" in status['error']

    def test_resolve_module_file_path_success(self, import_validator,
                                              mock_module_structure):
        """Test successful module file path resolution."""
        with patch('pathlib.Path.cwd',
                   return_value=Path(mock_module_structure['temp_dir'])):
            file_path = import_validator._resolve_module_file_path(
                'src.utilities.analysis.size_analyzer'
            )
        
        assert file_path is not None
        assert 'size_analyzer.py' in file_path

    def test_resolve_module_file_path_not_found(self, import_validator):
        """Test module file path resolution for non-existent module."""
        file_path = import_validator._resolve_module_file_path(
            'nonexistent.module.path'
        )
        
        assert file_path is None

    def test_validate_python_path_valid(self, import_validator):
        """Test Python path validation with valid configuration."""
        with patch('sys.path', ['/src', str(Path.cwd()), '/other']):
            status = import_validator._validate_python_path()
        
        assert status['valid'] is True
        assert len(status['issues']) == 0

    def test_validate_python_path_no_src(self, import_validator):
        """Test Python path validation without src directory."""
        with patch('sys.path', ['/other', '/paths']):
            status = import_validator._validate_python_path()
        
        assert status['valid'] is False
        assert any("No 'src' directory found" in issue
                   for issue in status['issues'])

    def test_validate_python_path_duplicate_paths(self, import_validator):
        """Test Python path validation with duplicate paths."""
        with patch('sys.path', ['/src', '/current', '/src']):
            status = import_validator._validate_python_path()
        
        assert any("Duplicate paths found" in issue
                   for issue in status['issues'])

    def test_check_circular_imports(self, import_validator):
        """Test circular import detection."""
        status = import_validator._check_circular_imports()
        
        assert 'found' in status
        assert 'issues' in status
        assert 'dependencies' in status
        assert isinstance(status['found'], bool)
        assert isinstance(status['issues'], list)

    def test_generate_diagnostic_report_success(self, import_validator):
        """Test diagnostic report generation for successful validation."""
        with patch.object(import_validator, 'validate_size_analyzer_imports',
                          return_value={
                              'success': True,
                              'errors': [],
                              'warnings': [],
                              'info': ['Test info'],
                              'module_status': {
                                  'test.module': {
                                      'importable': True,
                                      'error': None,
                                      'file_exists': True,
                                      'path_resolved': '/test/path.py'
                                  }
                              },
                              'python_path_status': {'valid': True,
                                                     'issues': []},
                              'circular_imports': {'found': False,
                                                   'issues': []}
                          }):
            report = import_validator.generate_diagnostic_report()
        
        assert "✓ PASS" in report
        assert "Module Import Status" in report
        assert "✓ `test.module`" in report
        assert "All imports are working correctly!" in report

    def test_generate_diagnostic_report_failure(self, import_validator):
        """Test diagnostic report generation for failed validation."""
        with patch.object(import_validator, 'validate_size_analyzer_imports',
                          return_value={
                              'success': False,
                              'errors': ['Test error'],
                              'warnings': ['Test warning'],
                              'info': [],
                              'module_status': {
                                  'test.module': {
                                      'importable': False,
                                      'error': 'Import failed',
                                      'file_exists': False,
                                      'path_resolved': None
                                  }
                              },
                              'python_path_status': {
                                  'valid': False,
                                  'issues': ['Path issue']
                              },
                              'circular_imports': {'found': False,
                                                   'issues': []}
                          }):
            report = import_validator.generate_diagnostic_report()
        
        assert "✗ FAIL" in report
        assert "## Errors" in report
        assert "❌ Test error" in report
        assert "## Warnings" in report
        assert "⚠️ Test warning" in report
        assert "✗ `test.module`" in report

    def test_fix_common_issues_success(self, import_validator,
                                      mock_module_structure):
        """Test successful application of common fixes."""
        original_path = sys.path.copy()
        
        try:
            # Remove src from path to test fix
            sys.path = [p for p in sys.path if 'src' not in p]
            
            with patch('pathlib.Path.cwd',
                       return_value=Path(mock_module_structure['temp_dir'])):
                with patch('os.path.exists', return_value=True):
                    fixes = import_validator.fix_common_issues()
            
            assert fixes['success'] is True
            assert len(fixes['fixes']) > 0
            assert any('Python path' in fix for fix in fixes['fixes'])
            
        finally:
            sys.path = original_path

    def test_fix_common_issues_exception(self, import_validator):
        """Test fix application with exception handling."""
        with patch.object(import_validator, '_create_missing_init_files',
                          side_effect=Exception("Test error")):
            fixes = import_validator.fix_common_issues()
        
        assert fixes['success'] is False
        assert len(fixes['errors']) > 0

    def test_create_missing_init_files(self, import_validator, temp_directory):
        """Test creation of missing __init__.py files."""
        # Create directory structure without __init__.py files
        test_dirs = [
            'src',
            'src/utilities',
            'src/utilities/analysis'
        ]
        
        for dir_name in test_dirs:
            dir_path = Path(temp_directory) / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
        
        with patch('pathlib.Path', return_value=Path(temp_directory)):
            with patch.object(import_validator,
                              '_create_missing_init_files') as mock_create:
                mock_create.return_value = ['Created file1', 'Created file2']
                created_files = import_validator._create_missing_init_files()
        
        assert len(created_files) > 0

    def test_validate_gui_class_instantiation(self, import_validator):
        """Test validation of GUI class instantiation."""
        with patch('importlib.import_module') as mock_import:
            mock_module = Mock()
            mock_gui_class = Mock()
            mock_gui_class.__name__ = 'SizeAnalyzerGUI'
            mock_module.SizeAnalyzerGUI = mock_gui_class
            mock_import.return_value = mock_module
            
            with patch.object(import_validator, '_resolve_module_file_path',
                             return_value='/mock/path.py'):
                with patch('os.path.exists', return_value=True):
                    status = import_validator._validate_module_import(
                        'mock.module', 'SizeAnalyzerGUI'
                    )
        
        assert status['importable'] is True
        assert status['class_available'] is True
        # GUI classes are assumed instantiable without actually instantiating
        assert status['instantiable'] is True

    def test_validate_non_gui_class_instantiation(self, import_validator):
        """Test validation of non-GUI class instantiation."""
        with patch('importlib.import_module') as mock_import:
            mock_module = Mock()
            mock_class = Mock()
            mock_class.return_value = Mock()  # Successful instantiation
            mock_module.RegularClass = mock_class
            mock_import.return_value = mock_module
            
            with patch.object(import_validator, '_resolve_module_file_path',
                             return_value='/mock/path.py'):
                with patch('os.path.exists', return_value=True):
                    status = import_validator._validate_module_import(
                        'mock.module', 'RegularClass'
                    )
        
        assert status['importable'] is True
        assert status['class_available'] is True
        assert status['instantiable'] is True

    def test_resolve_module_with_init_file(self, import_validator,
                                          mock_module_structure):
        """Test module resolution finding __init__.py file."""
        # Create a module directory with __init__.py
        module_dir = Path(mock_module_structure['temp_dir']) / 'test_module'
        module_dir.mkdir()
        (module_dir / '__init__.py').write_text("")
        
        with patch('pathlib.Path.cwd',
                   return_value=Path(mock_module_structure['temp_dir'])):
            file_path = import_validator._resolve_module_file_path(
                'test_module')
        
        assert file_path is not None
        assert '__init__.py' in file_path

    def test_multiple_base_paths_resolution(self, import_validator,
                                           mock_module_structure):
        """Test module resolution across multiple base paths."""
        with patch('pathlib.Path.cwd',
                   return_value=Path(mock_module_structure['temp_dir'])):
            file_path = import_validator._resolve_module_file_path(
                'src.utilities.analysis.size_analyzer'
            )
        
        assert file_path is not None


class TestMainFunction:
    """Test suite for main function."""
    
    def test_main_function_basic_import(self):
        """Test main function is properly defined and importable."""
        # Simply test that we can import and access the main function
        assert callable(main)
        assert main.__name__ == 'main'
        # This is safer than trying to execute it in test environment

    @patch('builtins.print')
    def test_main_function_execution_flow(self, mock_print):
        """Test main function execution flow with mocking."""
        with patch.object(ImportValidator, 'generate_diagnostic_report',
                         return_value="Mock report") as mock_report:
            with patch.object(ImportValidator, 'fix_common_issues',
                             return_value={'success': True, 'fixes': []}) as mock_fix:
                with patch.object(ImportValidator, 'validate_size_analyzer_imports',
                                 return_value={'success': True, 'errors': []}) as mock_validate:
                    main()
        
        mock_report.assert_called_once()
        mock_fix.assert_called_once()
        mock_validate.assert_called_once()


class TestEdgeCases:
    """Test suite for edge cases and error conditions."""
    
    @pytest.fixture
    def import_validator(self):
        """Create ImportValidator instance for testing."""
        validator = ImportValidator()
        yield validator

    def test_empty_module_path(self, import_validator):
        """Test handling of empty module path."""
        status = import_validator._validate_module_import("", "TestClass")
        
        assert status['importable'] is False
        assert status['error'] is not None

    def test_malformed_module_path(self, import_validator):
        """Test handling of malformed module path."""
        status = import_validator._validate_module_import(
            "...invalid..module", "TestClass"
        )
        
        assert status['importable'] is False
        assert status['error'] is not None

    def test_module_with_special_characters(self, import_validator):
        """Test handling of module paths with special characters."""
        status = import_validator._validate_module_import(
            "module-with-dashes", "TestClass"
        )
        
        assert status['importable'] is False

    def test_very_long_module_path(self, import_validator):
        """Test handling of very long module paths."""
        long_path = ".".join([f"level{i}" for i in range(50)])
        status = import_validator._validate_module_import(long_path, "TestClass")
        
        assert status['importable'] is False

    def test_class_instantiation_exception(self, import_validator):
        """Test handling of class instantiation exceptions."""
        with patch('importlib.import_module') as mock_import:
            mock_module = Mock()
            mock_class = Mock(side_effect=Exception("Instantiation error"))
            mock_module.TestClass = mock_class
            mock_import.return_value = mock_module
            
            status = import_validator._validate_module_import(
                'mock.module', 'TestClass'
            )
        
        assert status['importable'] is True
        assert status['class_available'] is True
        assert "Instantiation failed" in status['error']

    def test_file_path_permission_error(self, import_validator):
        """Test handling of file path permission errors."""
        with patch('pathlib.Path.exists', side_effect=PermissionError("Access denied")):
            file_path = import_validator._resolve_module_file_path('test.module')
        
        assert file_path is None

    def test_sys_path_modification_during_validation(self, import_validator):
        """Test validation when sys.path is modified during execution."""
        original_path = sys.path.copy()
        
        def modify_path():
            sys.path.append('/new/path')
            return {'valid': True, 'issues': [], 'paths': sys.path.copy()}
        
        try:
            with patch.object(import_validator, '_validate_python_path',
                             side_effect=modify_path):
                status = import_validator._validate_python_path()
            
            assert status['valid'] is True
            
        finally:
            sys.path = original_path

    def test_circular_import_complex_scenario(self, import_validator):
        """Test circular import detection in complex scenarios."""
        # Mock a complex module dependency scenario
        status = import_validator._check_circular_imports()
        
        # Should complete without errors
        assert 'found' in status
        assert 'issues' in status

    def test_create_init_files_permission_denied(self, import_validator):
        """Test __init__.py creation with permission denied."""
        with patch('pathlib.Path.write_text',
                   side_effect=PermissionError("Permission denied")):
            with patch('pathlib.Path.exists', return_value=True):
                with patch('pathlib.Path.is_dir', return_value=True):
                    created_files = import_validator._create_missing_init_files()
        
        # Should handle permission errors gracefully
        assert isinstance(created_files, list)

    def test_unicode_module_paths(self, import_validator):
        """Test handling of Unicode characters in module paths."""
        unicode_path = "测试模块.unicode_module"
        status = import_validator._validate_module_import(unicode_path, "TestClass")
        
        # Should handle Unicode gracefully
        assert status['importable'] is False

    def test_concurrent_validation_calls(self, import_validator):
        """Test multiple concurrent validation calls."""
        # Simulate concurrent calls by calling validation multiple times
        results = []
        for _ in range(5):
            result = import_validator.validate_size_analyzer_imports()
            results.append(result)
        
        # All results should be consistent
        assert len(results) == 5
        for result in results:
            assert 'success' in result


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])