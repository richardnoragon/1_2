"""
Comprehensive Unit Tests for size_analyzer_config.py

Test module for the SizeAnalyzerConfig class and related functions.
Created: 2025-08-29
Author: GitHub Copilot
"""

import json
import logging
import os
import shutil
# Add the source directory to the path
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional
from unittest.mock import MagicMock, Mock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

try:
    from src.utilities.analysis.config.size_analyzer_config import (
        SizeAnalyzerConfig, get_config_manager, get_log_manager)
except ImportError:
    # Fallback import path
    try:
        from utilities.analysis.config.size_analyzer_config import (
            SizeAnalyzerConfig, get_config_manager, get_log_manager)
    except ImportError:
        # Direct import for testing
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "size_analyzer_config", 
            os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'utilities', 'analysis', 'config', 'size_analyzer_config.py')
        )
        size_analyzer_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(size_analyzer_config)
        
        SizeAnalyzerConfig = size_analyzer_config.SizeAnalyzerConfig
        get_config_manager = size_analyzer_config.get_config_manager
        get_log_manager = size_analyzer_config.get_log_manager


class TestHelperFunctions:
    """Test helper functions in the module."""
    
    def test_get_config_manager_with_valid_import(self):
        """Test get_config_manager with successful import."""
        with patch('builtins.__import__') as mock_import:
            mock_module = Mock()
            mock_module.ConfigManager = Mock()
            mock_import.return_value = mock_module
            
            result = get_config_manager()
            assert result is not None
            assert result == mock_module.ConfigManager
    
    def test_get_config_manager_import_error(self):
        """Test get_config_manager when import fails."""
        with patch('builtins.__import__', side_effect=ImportError("Module not found")):
            result = get_config_manager()
            assert result is None
    
    def test_get_config_manager_attribute_error(self):
        """Test get_config_manager when attribute doesn't exist."""
        with patch('builtins.__import__') as mock_import:
            mock_module = Mock()
            del mock_module.ConfigManager  # Remove the attribute
            mock_import.return_value = mock_module
            
            result = get_config_manager()
            assert result is None
    
    def test_get_log_manager_with_valid_import(self):
        """Test get_log_manager with successful import."""
        with patch('builtins.__import__') as mock_import:
            mock_module = Mock()
            mock_module.LogManager = Mock()
            mock_import.return_value = mock_module
            
            result = get_log_manager()
            assert result is not None
            assert result == mock_module.LogManager
    
    def test_get_log_manager_import_error(self):
        """Test get_log_manager fallback to basic logging."""
        with patch('builtins.__import__', side_effect=ImportError("Module not found")):
            result = get_log_manager()
            assert result == logging
    
    def test_get_log_manager_exception_fallback(self):
        """Test get_log_manager exception fallback."""
        with patch('builtins.__import__', side_effect=Exception("General error")):
            result = get_log_manager()
            assert result == logging


class TestSizeAnalyzerConfig:
    """Comprehensive tests for the SizeAnalyzerConfig class."""
    
    @pytest.fixture
    def mock_config_manager(self):
        """Create a mock config manager for testing."""
        mock_cm = Mock()
        mock_cm.config = {}
        mock_cm.save_config = Mock()
        return mock_cm
    
    @pytest.fixture
    def mock_logger(self):
        """Create a mock logger for testing."""
        return Mock(spec=logging.Logger)
    
    @pytest.fixture
    def size_analyzer_config(self, mock_config_manager, mock_logger):
        """Create a SizeAnalyzerConfig instance for testing."""
        with patch('src.utilities.analysis.config.size_analyzer_config.get_config_manager', return_value=lambda: mock_config_manager):
            with patch('src.utilities.analysis.config.size_analyzer_config.get_log_manager') as mock_log_manager:
                mock_log_manager.return_value.get_logger.return_value = mock_logger
                config = SizeAnalyzerConfig(config_manager=mock_config_manager)
                config.logger = mock_logger
                return config
    
    @pytest.fixture
    def temp_directory(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_initialization_with_config_manager(self, mock_config_manager):
        """Test initialization with provided config manager."""
        config = SizeAnalyzerConfig(config_manager=mock_config_manager)
        assert config.config_manager == mock_config_manager
        assert config.section_name == 'size_analyzer'
    
    def test_initialization_without_config_manager(self):
        """Test initialization without config manager (fallback)."""
        with patch('src.utilities.analysis.config.size_analyzer_config.get_config_manager', return_value=None):
            config = SizeAnalyzerConfig()
            assert config.config_manager is not None
            assert hasattr(config.config_manager, 'config')
            assert hasattr(config.config_manager, 'save_config')
    
    def test_defaults_structure(self, size_analyzer_config):
        """Test that defaults have the expected structure."""
        defaults = size_analyzer_config.defaults
        
        # Check main sections exist
        expected_sections = [
            'general', 'analysis', 'export', 'ui', 'performance',
            'resources', 'hub_integration', 'logging'
        ]
        for section in expected_sections:
            assert section in defaults
            assert isinstance(defaults[section], dict)
        
        # Check specific key structures
        assert 'window_geometry' in defaults['ui']
        assert 'progress_visualization' in defaults['ui']
        assert 'results_display' in defaults['ui']
        
        assert 'resource_requirements' in defaults['hub_integration']
        assert 'event_broadcasting' in defaults['hub_integration']
        assert 'coordination' in defaults['hub_integration']
    
    def test_ensure_configuration_exists_new_config(self, size_analyzer_config):
        """Test _ensure_configuration_exists with new configuration."""
        size_analyzer_config.config_manager.config = {}
        
        size_analyzer_config._ensure_configuration_exists()
        
        assert 'size_analyzer' in size_analyzer_config.config_manager.config
        assert size_analyzer_config.config_manager.config['size_analyzer'] == size_analyzer_config.defaults
        size_analyzer_config.config_manager.save_config.assert_called_once()
    
    def test_ensure_configuration_exists_existing_config(self, size_analyzer_config):
        """Test _ensure_configuration_exists with existing configuration."""
        existing_config = {'general': {'module_path': 'custom_path'}}
        size_analyzer_config.config_manager.config = {'size_analyzer': existing_config}
        
        with patch.object(size_analyzer_config, '_merge_with_defaults') as mock_merge:
            size_analyzer_config._ensure_configuration_exists()
            mock_merge.assert_called_once_with(existing_config)
    
    def test_ensure_configuration_exists_exception_handling(self, size_analyzer_config):
        """Test _ensure_configuration_exists exception handling."""
        size_analyzer_config.config_manager.config = None  # This will cause an error
        
        with patch.object(size_analyzer_config.config_manager, 'save_config', side_effect=Exception("Save error")):
            size_analyzer_config._ensure_configuration_exists()
            # Should fall back to defaults without raising
            assert size_analyzer_config.config_manager.config['size_analyzer'] == size_analyzer_config.defaults
    
    def test_merge_with_defaults_nested_dicts(self, size_analyzer_config):
        """Test _merge_with_defaults with nested dictionaries."""
        existing_config = {
            'general': {
                'module_path': 'custom_path',
                'new_key': 'new_value'
            },
            'ui': {
                'window_geometry': {
                    'width': 1024,
                    'custom_property': True
                }
            }
        }
        
        size_analyzer_config._merge_with_defaults(existing_config)
        
        merged = size_analyzer_config.config_manager.config['size_analyzer']
        
        # Check that custom values are preserved
        assert merged['general']['module_path'] == 'custom_path'
        assert merged['general']['new_key'] == 'new_value'
        assert merged['ui']['window_geometry']['width'] == 1024
        assert merged['ui']['window_geometry']['custom_property'] is True
        
        # Check that default values are still present
        assert 'last_opened_directory' in merged['general']
        assert merged['ui']['window_geometry']['height'] == 600  # default value
    
    def test_get_setting_existing_value(self, size_analyzer_config):
        """Test get_setting with existing value."""
        size_analyzer_config.config_manager.config = {
            'size_analyzer': {
                'general': {
                    'module_path': 'test_path'
                }
            }
        }
        
        result = size_analyzer_config.get_setting('general', 'module_path')
        assert result == 'test_path'
    
    def test_get_setting_fallback_to_default(self, size_analyzer_config):
        """Test get_setting fallback to default values."""
        size_analyzer_config.config_manager.config = {'size_analyzer': {}}
        
        result = size_analyzer_config.get_setting('general', 'module_path')
        assert result == size_analyzer_config.defaults['general']['module_path']
    
    def test_get_setting_with_custom_default(self, size_analyzer_config):
        """Test get_setting with custom default value."""
        size_analyzer_config.config_manager.config = {'size_analyzer': {}}
        
        result = size_analyzer_config.get_setting('general', 'nonexistent_key', 'custom_default')
        assert result == 'custom_default'
    
    def test_get_setting_exception_handling(self, size_analyzer_config):
        """Test get_setting exception handling."""
        size_analyzer_config.config_manager.config = None  # This will cause an error
        
        result = size_analyzer_config.get_setting('general', 'module_path', 'fallback')
        assert result == 'fallback'
    
    def test_set_setting_new_subsection(self, size_analyzer_config):
        """Test set_setting creating new subsection."""
        size_analyzer_config.config_manager.config = {}
        
        result = size_analyzer_config.set_setting('new_section', 'new_key', 'new_value')
        
        assert result is True
        assert size_analyzer_config.config_manager.config['size_analyzer']['new_section']['new_key'] == 'new_value'
        size_analyzer_config.config_manager.save_config.assert_called()
    
    def test_set_setting_existing_subsection(self, size_analyzer_config):
        """Test set_setting with existing subsection."""
        size_analyzer_config.config_manager.config = {
            'size_analyzer': {
                'general': {}
            }
        }
        
        result = size_analyzer_config.set_setting('general', 'test_key', 'test_value')
        
        assert result is True
        assert size_analyzer_config.config_manager.config['size_analyzer']['general']['test_key'] == 'test_value'
    
    def test_set_setting_exception_handling(self, size_analyzer_config):
        """Test set_setting exception handling."""
        with patch.object(size_analyzer_config.config_manager, 'save_config', side_effect=Exception("Save error")):
            result = size_analyzer_config.set_setting('general', 'test_key', 'test_value')
            assert result is False
    
    def test_get_all_settings(self, size_analyzer_config):
        """Test get_all_settings method."""
        test_config = {'general': {'test_key': 'test_value'}}
        size_analyzer_config.config_manager.config = {'size_analyzer': test_config}
        
        result = size_analyzer_config.get_all_settings()
        assert result == test_config
    
    def test_get_all_settings_fallback_to_defaults(self, size_analyzer_config):
        """Test get_all_settings fallback to defaults."""
        size_analyzer_config.config_manager.config = {}
        
        result = size_analyzer_config.get_all_settings()
        assert result == size_analyzer_config.defaults
    
    def test_reset_to_defaults_success(self, size_analyzer_config):
        """Test reset_to_defaults successful operation."""
        size_analyzer_config.config_manager.config = {
            'size_analyzer': {'custom': 'config'}
        }
        
        result = size_analyzer_config.reset_to_defaults()
        
        assert result is True
        assert size_analyzer_config.config_manager.config['size_analyzer'] == size_analyzer_config.defaults
        size_analyzer_config.config_manager.save_config.assert_called()
    
    def test_reset_to_defaults_exception(self, size_analyzer_config):
        """Test reset_to_defaults exception handling."""
        with patch.object(size_analyzer_config.config_manager, 'save_config', side_effect=Exception("Save error")):
            result = size_analyzer_config.reset_to_defaults()
            assert result is False
    
    def test_add_recent_directory_new_directory(self, size_analyzer_config):
        """Test add_recent_directory with new directory."""
        size_analyzer_config.config_manager.config = {
            'size_analyzer': {
                'general': {
                    'recent_directories': ['/path1', '/path2'],
                    'max_recent_directories': 10
                }
            }
        }
        
        result = size_analyzer_config.add_recent_directory('/new/path')
        
        assert result is True
        recent_dirs = size_analyzer_config.get_setting('general', 'recent_directories')
        assert recent_dirs[0] == '/new/path'
        assert len(recent_dirs) == 3
    
    def test_add_recent_directory_existing_directory(self, size_analyzer_config):
        """Test add_recent_directory with existing directory."""
        size_analyzer_config.config_manager.config = {
            'size_analyzer': {
                'general': {
                    'recent_directories': ['/path1', '/path2', '/path3'],
                    'max_recent_directories': 10
                }
            }
        }
        
        result = size_analyzer_config.add_recent_directory('/path2')
        
        assert result is True
        recent_dirs = size_analyzer_config.get_setting('general', 'recent_directories')
        assert recent_dirs[0] == '/path2'
        assert recent_dirs.count('/path2') == 1  # Should not duplicate
        assert len(recent_dirs) == 3
    
    def test_add_recent_directory_max_limit(self, size_analyzer_config):
        """Test add_recent_directory respecting maximum limit."""
        existing_dirs = [f'/path{i}' for i in range(5)]
        size_analyzer_config.config_manager.config = {
            'size_analyzer': {
                'general': {
                    'recent_directories': existing_dirs,
                    'max_recent_directories': 3
                }
            }
        }
        
        result = size_analyzer_config.add_recent_directory('/new/path')
        
        assert result is True
        recent_dirs = size_analyzer_config.get_setting('general', 'recent_directories')
        assert len(recent_dirs) == 3
        assert recent_dirs[0] == '/new/path'
    
    def test_add_recent_directory_exception(self, size_analyzer_config):
        """Test add_recent_directory exception handling."""
        with patch.object(size_analyzer_config, 'get_setting', side_effect=Exception("Get error")):
            result = size_analyzer_config.add_recent_directory('/test/path')
            assert result is False
    
    def test_get_recent_directories(self, size_analyzer_config):
        """Test get_recent_directories method."""
        test_dirs = ['/path1', '/path2', '/path3']
        size_analyzer_config.config_manager.config = {
            'size_analyzer': {
                'general': {
                    'recent_directories': test_dirs
                }
            }
        }
        
        result = size_analyzer_config.get_recent_directories()
        assert result == test_dirs
    
    def test_save_window_geometry_full_parameters(self, size_analyzer_config):
        """Test save_window_geometry with all parameters."""
        size_analyzer_config.config_manager.config = {
            'size_analyzer': {
                'ui': {
                    'window_geometry': {'remember_size': True}
                }
            }
        }
        
        result = size_analyzer_config.save_window_geometry(1024, 768, 100, 200)
        
        assert result is True
        geometry = size_analyzer_config.get_setting('ui', 'window_geometry')
        assert geometry['width'] == 1024
        assert geometry['height'] == 768
        assert geometry['x'] == 100
        assert geometry['y'] == 200
        assert geometry['remember_size'] is True  # Existing value preserved
    
    def test_save_window_geometry_size_only(self, size_analyzer_config):
        """Test save_window_geometry with size only."""
        result = size_analyzer_config.save_window_geometry(800, 600)
        
        assert result is True
        geometry = size_analyzer_config.get_setting('ui', 'window_geometry')
        assert geometry['width'] == 800
        assert geometry['height'] == 600
        assert 'x' not in geometry
        assert 'y' not in geometry
    
    def test_save_window_geometry_exception(self, size_analyzer_config):
        """Test save_window_geometry exception handling."""
        with patch.object(size_analyzer_config, 'set_setting', side_effect=Exception("Set error")):
            result = size_analyzer_config.save_window_geometry(800, 600)
            assert result is False
    
    def test_get_window_geometry(self, size_analyzer_config):
        """Test get_window_geometry method."""
        custom_geometry = {
            'width': 1200,
            'height': 800,
            'x': 50,
            'y': 50,
            'remember_size': False
        }
        size_analyzer_config.config_manager.config = {
            'size_analyzer': {
                'ui': {
                    'window_geometry': custom_geometry
                }
            }
        }
        
        result = size_analyzer_config.get_window_geometry()
        assert result == custom_geometry
    
    def test_get_window_geometry_defaults(self, size_analyzer_config):
        """Test get_window_geometry with default values."""
        size_analyzer_config.config_manager.config = {'size_analyzer': {}}
        
        result = size_analyzer_config.get_window_geometry()
        
        assert result['width'] == 800
        assert result['height'] == 600
        assert result['remember_size'] is True
        assert result['remember_position'] is True
        assert result['center_on_screen'] is True
    
    def test_get_resource_path_absolute_path(self, size_analyzer_config):
        """Test get_resource_path with absolute path."""
        absolute_path = os.path.abspath('/absolute/path/to/resource')
        size_analyzer_config.config_manager.config = {
            'size_analyzer': {
                'resources': {
                    'test_resource': absolute_path
                }
            }
        }
        
        result = size_analyzer_config.get_resource_path('test_resource')
        assert result == absolute_path
    
    def test_get_resource_path_relative_path(self, size_analyzer_config):
        """Test get_resource_path with relative path."""
        relative_path = 'relative/path/to/resource'
        size_analyzer_config.config_manager.config = {
            'size_analyzer': {
                'resources': {
                    'test_resource': relative_path
                }
            }
        }
        
        result = size_analyzer_config.get_resource_path('test_resource')
        
        # Should convert to absolute path
        assert os.path.isabs(result)
        assert result.endswith(relative_path.replace('/', os.sep))
    
    def test_get_resource_path_empty_path(self, size_analyzer_config):
        """Test get_resource_path with empty path."""
        size_analyzer_config.config_manager.config = {
            'size_analyzer': {
                'resources': {
                    'test_resource': ''
                }
            }
        }
        
        result = size_analyzer_config.get_resource_path('test_resource')
        assert result == ''
    
    def test_validate_configuration_success(self, size_analyzer_config, temp_directory):
        """Test validate_configuration with valid configuration."""
        # Create test resources
        test_file = os.path.join(temp_directory, 'test_file.txt')
        with open(test_file, 'w') as f:
            f.write('test')
        
        size_analyzer_config.config_manager.config = {
            'size_analyzer': {
                'resources': {
                    'test_file': test_file,
                    'cache_directory': os.path.join(temp_directory, 'cache'),
                    'temp_directory': os.path.join(temp_directory, 'temp'),
                    'log_directory': os.path.join(temp_directory, 'logs')
                },
                'performance': {
                    'max_memory_usage_mb': 256,
                    'operation_timeout_seconds': 300
                },
                'analysis': {
                    'default_top_files_count': 20
                }
            }
        }
        
        issues = size_analyzer_config.validate_configuration()
        
        assert isinstance(issues, dict)
        assert 'errors' in issues
        assert 'warnings' in issues
        assert 'info' in issues
        
        # Should have created directories
        assert len(issues['info']) >= 3  # At least 3 directories created
    
    def test_validate_configuration_missing_resources(self, size_analyzer_config):
        """Test validate_configuration with missing resources."""
        size_analyzer_config.config_manager.config = {
            'size_analyzer': {
                'resources': {
                    'missing_file': '/nonexistent/path/file.txt'
                },
                'performance': {
                    'max_memory_usage_mb': 32,  # Low memory
                    'operation_timeout_seconds': 10  # Low timeout
                },
                'analysis': {
                    'default_top_files_count': 200  # High count
                }
            }
        }
        
        issues = size_analyzer_config.validate_configuration()
        
        # Should have warnings for missing resources and low limits
        assert len(issues['warnings']) >= 3
        assert any('Resource not found' in warning for warning in issues['warnings'])
        assert any('Memory limit is very low' in warning for warning in issues['warnings'])
        assert any('Operation timeout is very low' in warning for warning in issues['warnings'])
        assert any('Large top files count' in warning for warning in issues['warnings'])
    
    def test_validate_configuration_exception(self, size_analyzer_config):
        """Test validate_configuration exception handling."""
        with patch.object(size_analyzer_config, 'get_all_settings', side_effect=Exception("Get error")):
            issues = size_analyzer_config.validate_configuration()
            
            assert len(issues['errors']) >= 1
            assert any('Configuration validation error' in error for error in issues['errors'])
    
    def test_export_configuration_success(self, size_analyzer_config, temp_directory):
        """Test export_configuration successful operation."""
        test_config = {
            'general': {'test_key': 'test_value'},
            'analysis': {'another_key': 123}
        }
        size_analyzer_config.config_manager.config = {'size_analyzer': test_config}
        
        export_file = os.path.join(temp_directory, 'exported_config.json')
        result = size_analyzer_config.export_configuration(export_file)
        
        assert result is True
        assert os.path.exists(export_file)
        
        # Verify exported content
        with open(export_file, 'r', encoding='utf-8') as f:
            exported_data = json.load(f)
        assert exported_data == test_config
    
    def test_export_configuration_exception(self, size_analyzer_config):
        """Test export_configuration exception handling."""
        result = size_analyzer_config.export_configuration('/invalid/path/config.json')
        assert result is False
    
    def test_import_configuration_success(self, size_analyzer_config, temp_directory):
        """Test import_configuration successful operation."""
        test_config = {
            'general': {'imported_key': 'imported_value'},
            'analysis': {'imported_number': 456}
        }
        
        import_file = os.path.join(temp_directory, 'import_config.json')
        with open(import_file, 'w', encoding='utf-8') as f:
            json.dump(test_config, f)
        
        result = size_analyzer_config.import_configuration(import_file)
        
        assert result is True
        assert size_analyzer_config.config_manager.config['size_analyzer'] == test_config
        size_analyzer_config.config_manager.save_config.assert_called()
    
    def test_import_configuration_invalid_format(self, size_analyzer_config, temp_directory):
        """Test import_configuration with invalid format."""
        import_file = os.path.join(temp_directory, 'invalid_config.json')
        with open(import_file, 'w', encoding='utf-8') as f:
            f.write('invalid json content')
        
        result = size_analyzer_config.import_configuration(import_file)
        assert result is False
    
    def test_import_configuration_invalid_structure(self, size_analyzer_config, temp_directory):
        """Test import_configuration with invalid structure."""
        import_file = os.path.join(temp_directory, 'invalid_structure.json')
        with open(import_file, 'w', encoding='utf-8') as f:
            json.dump("not a dict", f)  # Should be a dict
        
        result = size_analyzer_config.import_configuration(import_file)
        assert result is False
    
    def test_import_configuration_missing_file(self, size_analyzer_config):
        """Test import_configuration with missing file."""
        result = size_analyzer_config.import_configuration('/nonexistent/file.json')
        assert result is False
    
    def test_create_fallback_config_manager(self, size_analyzer_config):
        """Test _create_fallback_config_manager method."""
        fallback_cm = size_analyzer_config._create_fallback_config_manager()
        
        assert hasattr(fallback_cm, 'config')
        assert hasattr(fallback_cm, 'save_config')
        assert hasattr(fallback_cm, 'get')
        assert isinstance(fallback_cm.config, dict)
        
        # Test the get method
        fallback_cm.config['test_key'] = 'test_value'
        assert fallback_cm.get('test_key') == 'test_value'
        assert fallback_cm.get('missing_key', 'default') == 'default'
        
        # Test save_config doesn't raise an error
        fallback_cm.save_config()


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_empty_configuration(self):
        """Test behavior with completely empty configuration."""
        mock_cm = Mock()
        mock_cm.config = {}
        mock_cm.save_config = Mock()
        
        config = SizeAnalyzerConfig(config_manager=mock_cm)
        
        # Should create defaults
        assert 'size_analyzer' in mock_cm.config
        assert mock_cm.config['size_analyzer'] == config.defaults
    
    def test_corrupted_configuration(self):
        """Test behavior with corrupted configuration data."""
        mock_cm = Mock()
        mock_cm.config = {'size_analyzer': 'not_a_dict'}  # Invalid structure
        mock_cm.save_config = Mock()
        
        with patch('src.utilities.analysis.config.size_analyzer_config.get_config_manager', return_value=lambda: mock_cm):
            config = SizeAnalyzerConfig(config_manager=mock_cm)
            
            # Should handle gracefully
            result = config.get_setting('general', 'module_path', 'fallback')
            assert result == 'fallback'
    
    def test_none_values_handling(self, mock_config_manager):
        """Test handling of None values in configuration."""
        mock_config_manager.config = {
            'size_analyzer': {
                'general': {
                    'module_path': None,
                    'last_opened_directory': None
                }
            }
        }
        
        config = SizeAnalyzerConfig(config_manager=mock_config_manager)
        
        # Should fall back to defaults for None values
        result = config.get_setting('general', 'module_path')
        assert result == config.defaults['general']['module_path']
    
    def test_unicode_handling(self, mock_config_manager):
        """Test handling of Unicode characters in configuration."""
        unicode_path = '/path/with/unicode/测试/файл'
        
        config = SizeAnalyzerConfig(config_manager=mock_config_manager)
        
        # Test setting and getting Unicode values
        result = config.set_setting('general', 'unicode_path', unicode_path)
        assert result is True
        
        retrieved = config.get_setting('general', 'unicode_path')
        assert retrieved == unicode_path
    
    def test_very_large_values(self, mock_config_manager):
        """Test handling of very large values."""
        large_list = list(range(10000))
        
        config = SizeAnalyzerConfig(config_manager=mock_config_manager)
        
        result = config.set_setting('general', 'large_list', large_list)
        assert result is True
        
        retrieved = config.get_setting('general', 'large_list')
        assert retrieved == large_list


class TestIntegration:
    """Integration tests combining multiple operations."""
    
    def test_full_workflow(self, temp_directory):
        """Test a complete workflow scenario."""
        mock_cm = Mock()
        mock_cm.config = {}
        mock_cm.save_config = Mock()
        
        config = SizeAnalyzerConfig(config_manager=mock_cm)
        
        # Set some configuration values
        assert config.set_setting('general', 'last_opened_directory', temp_directory)
        assert config.set_setting('analysis', 'default_top_files_count', 50)
        
        # Add recent directories
        for i in range(5):
            test_dir = os.path.join(temp_directory, f'dir_{i}')
            assert config.add_recent_directory(test_dir)
        
        # Save window geometry
        assert config.save_window_geometry(1200, 800, 100, 100)
        
        # Export configuration
        export_file = os.path.join(temp_directory, 'workflow_config.json')
        assert config.export_configuration(export_file)
        
        # Reset to defaults
        assert config.reset_to_defaults()
        
        # Import configuration back
        assert config.import_configuration(export_file)
        
        # Verify values were restored
        assert config.get_setting('general', 'last_opened_directory') == temp_directory
        assert config.get_setting('analysis', 'default_top_files_count') == 50
        
        recent_dirs = config.get_recent_directories()
        assert len(recent_dirs) == 5
        
        geometry = config.get_window_geometry()
        assert geometry['width'] == 1200
        assert geometry['height'] == 800
    
    def test_configuration_validation_workflow(self, temp_directory):
        """Test configuration validation with real file operations."""
        mock_cm = Mock()
        mock_cm.config = {
            'size_analyzer': {
                'resources': {
                    'cache_directory': os.path.join(temp_directory, 'cache'),
                    'temp_directory': os.path.join(temp_directory, 'temp'),
                    'log_directory': os.path.join(temp_directory, 'logs'),
                    'existing_file': __file__,  # This file should exist
                    'missing_file': os.path.join(temp_directory, 'missing.txt')
                },
                'performance': {
                    'max_memory_usage_mb': 128,
                    'operation_timeout_seconds': 60
                },
                'analysis': {
                    'default_top_files_count': 30
                }
            }
        }
        mock_cm.save_config = Mock()
        
        config = SizeAnalyzerConfig(config_manager=mock_cm)
        
        # Run validation
        issues = config.validate_configuration()
        
        # Should have created directories
        assert os.path.exists(os.path.join(temp_directory, 'cache'))
        assert os.path.exists(os.path.join(temp_directory, 'temp'))
        assert os.path.exists(os.path.join(temp_directory, 'logs'))
        
        # Should have warnings for missing file
        assert any('Resource not found' in warning for warning in issues['warnings'])
        
        # Should have info messages for created directories
        assert len(issues['info']) >= 3


if __name__ == '__main__':
    # Run tests when executed directly
    pytest.main([__file__, '-v', '--tb=short'])