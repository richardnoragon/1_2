"""
Configuration and Resource Testing for Size Analyzer

This module contains comprehensive tests for configuration management,
resource path resolution, settings persistence, and validation.
"""

import os
import json
import tempfile
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from file_utilities_2.core.size_analyzer_config import SizeAnalyzerConfig
from file_utilities_2.core.size_analyzer_logging import (
    SizeAnalyzerLogger, get_size_analyzer_logger, cleanup_logging
)


class TestSizeAnalyzerConfig:
    """Test SizeAnalyzerConfig functionality."""
    
    def test_config_initialization(self):
        """Test configuration initialization."""
        with patch('file_utilities_2.core.size_analyzer_config.ConfigManager'):
            config = SizeAnalyzerConfig()
            
            assert config is not None
            assert config.section_name == 'size_analyzer'
            assert config.defaults is not None
            assert isinstance(config.defaults, dict)
    
    def test_default_configuration_structure(self):
        """Test default configuration structure."""
        with patch('file_utilities_2.core.size_analyzer_config.ConfigManager'):
            config = SizeAnalyzerConfig()
            
            required_sections = [
                'general', 'analysis', 'export', 'ui', 'performance',
                'resources', 'hub_integration', 'logging'
            ]
            
            for section in required_sections:
                assert section in config.defaults
                assert isinstance(config.defaults[section], dict)
    
    def test_general_configuration_defaults(self):
        """Test general configuration defaults."""
        with patch('file_utilities_2.core.size_analyzer_config.ConfigManager'):
            config = SizeAnalyzerConfig()
            
            general = config.defaults['general']
            
            assert 'module_path' in general
            assert 'class_name' in general
            assert 'last_opened_directory' in general
            assert 'recent_directories' in general
            assert 'max_recent_directories' in general
            assert 'enable_logging' in general
            
            assert general['module_path'] == 'file_utilities_2.gui.size_analyzer_gui'
            assert general['class_name'] == 'SizeAnalyzerGUI'
            assert isinstance(general['recent_directories'], list)
            assert isinstance(general['max_recent_directories'], int)
    
    def test_analysis_configuration_defaults(self):
        """Test analysis configuration defaults."""
        with patch('file_utilities_2.core.size_analyzer_config.ConfigManager'):
            config = SizeAnalyzerConfig()
            
            analysis = config.defaults['analysis']
            
            assert 'default_top_files_count' in analysis
            assert 'progress_update_interval' in analysis
            assert 'max_concurrent_operations' in analysis
            assert 'include_hidden_files' in analysis
            assert 'follow_symlinks' in analysis
            assert 'skip_system_files' in analysis
            
            assert isinstance(analysis['default_top_files_count'], int)
            assert isinstance(analysis['include_hidden_files'], bool)
            assert isinstance(analysis['follow_symlinks'], bool)
    
    def test_export_configuration_defaults(self):
        """Test export configuration defaults."""
        with patch('file_utilities_2.core.size_analyzer_config.ConfigManager'):
            config = SizeAnalyzerConfig()
            
            export = config.defaults['export']
            
            assert 'default_format' in export
            assert 'include_metadata' in export
            assert 'include_performance_metrics' in export
            assert 'export_formats' in export
            
            assert export['default_format'] == 'json'
            assert isinstance(export['include_metadata'], bool)
            assert isinstance(export['export_formats'], list)
            assert 'json' in export['export_formats']
    
    def test_ui_configuration_defaults(self):
        """Test UI configuration defaults."""
        with patch('file_utilities_2.core.size_analyzer_config.ConfigManager'):
            config = SizeAnalyzerConfig()
            
            ui = config.defaults['ui']
            
            assert 'window_geometry' in ui
            assert 'progress_visualization' in ui
            assert 'results_display' in ui
            
            geometry = ui['window_geometry']
            assert 'width' in geometry
            assert 'height' in geometry
            assert 'remember_size' in geometry
            
            assert isinstance(geometry['width'], int)
            assert isinstance(geometry['height'], int)
            assert isinstance(geometry['remember_size'], bool)
    
    def test_performance_configuration_defaults(self):
        """Test performance configuration defaults."""
        with patch('file_utilities_2.core.size_analyzer_config.ConfigManager'):
            config = SizeAnalyzerConfig()
            
            performance = config.defaults['performance']
            
            assert 'enable_performance_monitoring' in performance
            assert 'max_memory_usage_mb' in performance
            assert 'max_cpu_usage_percent' in performance
            assert 'operation_timeout_seconds' in performance
            
            assert isinstance(performance['max_memory_usage_mb'], int)
            assert isinstance(performance['max_cpu_usage_percent'], int)
            assert isinstance(performance['operation_timeout_seconds'], int)
    
    def test_resources_configuration_defaults(self):
        """Test resources configuration defaults."""
        with patch('file_utilities_2.core.size_analyzer_config.ConfigManager'):
            config = SizeAnalyzerConfig()
            
            resources = config.defaults['resources']
            
            assert 'icon_path' in resources
            assert 'ui_file' in resources
            assert 'help_file' in resources
            assert 'template_path' in resources
            assert 'cache_directory' in resources
            assert 'temp_directory' in resources
            assert 'log_directory' in resources
            
            assert resources['icon_path'].endswith('.png')
            assert resources['ui_file'].endswith('.ui')
            assert resources['help_file'].endswith('.html')
    
    def test_hub_integration_configuration_defaults(self):
        """Test hub integration configuration defaults."""
        with patch('file_utilities_2.core.size_analyzer_config.ConfigManager'):
            config = SizeAnalyzerConfig()
            
            hub = config.defaults['hub_integration']
            
            assert 'enable_hub_integration' in hub
            assert 'tool_name' in hub
            assert 'tool_category' in hub
            assert 'resource_requirements' in hub
            assert 'event_broadcasting' in hub
            assert 'coordination' in hub
            
            assert hub['tool_name'] == 'Size Analyzer'
            assert hub['tool_category'] == 'analysis'
            assert isinstance(hub['enable_hub_integration'], bool)
    
    def test_logging_configuration_defaults(self):
        """Test logging configuration defaults."""
        with patch('file_utilities_2.core.size_analyzer_config.ConfigManager'):
            config = SizeAnalyzerConfig()
            
            logging_config = config.defaults['logging']
            
            assert 'enable_tool_logging' in logging_config
            assert 'log_level' in logging_config
            assert 'log_file' in logging_config
            assert 'max_log_size_mb' in logging_config
            assert 'backup_count' in logging_config
            assert 'log_categories' in logging_config
            
            assert isinstance(logging_config['enable_tool_logging'], bool)
            assert isinstance(logging_config['log_categories'], dict)
    
    def test_setting_get_set(self):
        """Test setting get/set operations."""
        mock_config_manager = Mock()
        mock_config_manager.config = {'size_analyzer': {}}
        
        with patch('file_utilities_2.core.size_analyzer_config.ConfigManager',
                   return_value=mock_config_manager):
            config = SizeAnalyzerConfig()
            
            # Test setting a value
            result = config.set_setting('general', 'test_key', 'test_value')
            assert result is True
            
            # Test getting the value
            value = config.get_setting('general', 'test_key')
            assert value == 'test_value'
            
            # Test getting with default
            default_value = config.get_setting('general', 'nonexistent', 'default')
            assert default_value == 'default'
    
    def test_recent_directories_management(self):
        """Test recent directories management."""
        mock_config_manager = Mock()
        mock_config_manager.config = {
            'size_analyzer': {
                'general': {
                    'recent_directories': [],
                    'max_recent_directories': 5
                }
            }
        }
        
        with patch('file_utilities_2.core.size_analyzer_config.ConfigManager',
                   return_value=mock_config_manager):
            config = SizeAnalyzerConfig()
            
            # Add directories
            config.add_recent_directory('/path/1')
            config.add_recent_directory('/path/2')
            config.add_recent_directory('/path/3')
            
            recent = config.get_recent_directories()
            assert '/path/3' in recent
            assert '/path/2' in recent
            assert '/path/1' in recent
            
            # Test duplicate handling
            config.add_recent_directory('/path/2')
            recent = config.get_recent_directories()
            # Should move to front, not duplicate
            assert recent.count('/path/2') == 1
    
    def test_window_geometry_management(self):
        """Test window geometry management."""
        mock_config_manager = Mock()
        mock_config_manager.config = {'size_analyzer': {'ui': {}}}
        
        with patch('file_utilities_2.core.size_analyzer_config.ConfigManager',
                   return_value=mock_config_manager):
            config = SizeAnalyzerConfig()
            
            # Save geometry
            result = config.save_window_geometry(800, 600, 100, 50)
            assert result is True
            
            # Get geometry
            geometry = config.get_window_geometry()
            assert geometry['width'] == 800
            assert geometry['height'] == 600
    
    def test_resource_path_resolution(self):
        """Test resource path resolution."""
        mock_config_manager = Mock()
        mock_config_manager.config = {
            'size_analyzer': {
                'resources': {
                    'icon_path': 'relative/path/icon.png',
                    'absolute_path': '/absolute/path/file.txt'
                }
            }
        }
        
        with patch('file_utilities_2.core.size_analyzer_config.ConfigManager',
                   return_value=mock_config_manager):
            config = SizeAnalyzerConfig()
            
            # Test relative path resolution
            icon_path = config.get_resource_path('icon_path')
            assert os.path.isabs(icon_path)
            assert icon_path.endswith('icon.png')
            
            # Test absolute path passthrough
            abs_path = config.get_resource_path('absolute_path')
            assert abs_path == '/absolute/path/file.txt'
    
    def test_configuration_validation(self):
        """Test configuration validation."""
        mock_config_manager = Mock()
        mock_config_manager.config = {
            'size_analyzer': {
                'performance': {
                    'max_memory_usage_mb': 32,  # Very low
                    'operation_timeout_seconds': 10  # Very low
                },
                'analysis': {
                    'default_top_files_count': 150  # Very high
                },
                'resources': {
                    'nonexistent_file': '/nonexistent/path'
                }
            }
        }
        
        with patch('file_utilities_2.core.size_analyzer_config.ConfigManager',
                   return_value=mock_config_manager):
            config = SizeAnalyzerConfig()
            
            issues = config.validate_configuration()
            
            assert 'errors' in issues
            assert 'warnings' in issues
            assert 'info' in issues
            
            # Should have warnings about low values
            warnings = issues['warnings']
            assert any('Memory limit is very low' in w for w in warnings)
            assert any('Operation timeout is very low' in w for w in warnings)
            assert any('Large top files count' in w for w in warnings)
    
    def test_configuration_export_import(self, temp_dir):
        """Test configuration export/import."""
        mock_config_manager = Mock()
        test_config = {
            'general': {'test_setting': 'test_value'},
            'analysis': {'test_analysis': True}
        }
        mock_config_manager.config = {'size_analyzer': test_config}
        
        with patch('file_utilities_2.core.size_analyzer_config.ConfigManager',
                   return_value=mock_config_manager):
            config = SizeAnalyzerConfig()
            
            export_path = os.path.join(temp_dir, 'config_export.json')
            
            # Test export
            result = config.export_configuration(export_path)
            assert result is True
            assert os.path.exists(export_path)
            
            # Verify exported content
            with open(export_path, 'r') as f:
                exported_data = json.load(f)
            assert exported_data == test_config
            
            # Test import
            result = config.import_configuration(export_path)
            assert result is True
    
    def test_configuration_reset(self):
        """Test configuration reset to defaults."""
        mock_config_manager = Mock()
        mock_config_manager.config = {'size_analyzer': {'modified': 'data'}}
        
        with patch('file_utilities_2.core.size_analyzer_config.ConfigManager',
                   return_value=mock_config_manager):
            config = SizeAnalyzerConfig()
            
            result = config.reset_to_defaults()
            assert result is True
            
            # Verify config was reset
            mock_config_manager.save_config.assert_called()


class TestSizeAnalyzerLogging:
    """Test SizeAnalyzerLogger functionality."""
    
    def test_logger_initialization(self):
        """Test logger initialization."""
        with patch('file_utilities_2.core.size_analyzer_logging.LogManager'), \
             patch('file_utilities_2.core.size_analyzer_config.SizeAnalyzerConfig'):
            logger = SizeAnalyzerLogger()
            
            assert logger is not None
            assert logger.config is not None
            assert logger.loggers is not None
            assert logger.main_logger is not None
    
    def test_logger_with_config(self):
        """Test logger initialization with config."""
        mock_config = Mock()
        
        with patch('file_utilities_2.core.size_analyzer_logging.LogManager'):
            logger = SizeAnalyzerLogger(mock_config)
            
            assert logger.config == mock_config
    
    def test_log_directory_creation(self, temp_dir):
        """Test log directory creation."""
        mock_config = Mock()
        mock_config.get_resource_path.return_value = temp_dir
        mock_config.get_all_settings.return_value = {
            'logging': {'enable_tool_logging': True}
        }
        
        with patch('file_utilities_2.core.size_analyzer_logging.LogManager'):
            logger = SizeAnalyzerLogger(mock_config)
            
            log_dir = logger._ensure_log_directory()
            assert os.path.exists(log_dir)
            assert os.path.isdir(log_dir)
    
    def test_category_logger_retrieval(self):
        """Test category logger retrieval."""
        with patch('file_utilities_2.core.size_analyzer_logging.LogManager'), \
             patch('file_utilities_2.core.size_analyzer_config.SizeAnalyzerConfig'):
            logger = SizeAnalyzerLogger()
            
            # Test main logger
            main_logger = logger.get_logger('main')
            assert main_logger is not None
            
            # Test category logger
            core_logger = logger.get_logger('core_logic')
            assert core_logger is not None
            
            # Test fallback to main logger
            unknown_logger = logger.get_logger('unknown_category')
            assert unknown_logger == logger.main_logger
    
    def test_logging_methods(self):
        """Test various logging methods."""
        with patch('file_utilities_2.core.size_analyzer_logging.LogManager'), \
             patch('file_utilities_2.core.size_analyzer_config.SizeAnalyzerConfig'):
            logger = SizeAnalyzerLogger()
            
            # Mock category loggers
            mock_logger = Mock()
            logger.loggers['core_logic'] = mock_logger
            logger.loggers['gui_events'] = mock_logger
            logger.loggers['hub_integration'] = mock_logger
            logger.loggers['performance'] = mock_logger
            logger.loggers['errors'] = mock_logger
            
            # Test logging methods
            logger.log_core_logic('info', 'Test core message')
            logger.log_gui_event('debug', 'Test GUI event')
            logger.log_hub_integration('info', 'Test hub event')
            logger.log_performance('debug', 'Test performance')
            logger.log_error('Test error')
            
            # Verify calls were made
            assert mock_logger.info.called or mock_logger.debug.called
    
    def test_analysis_lifecycle_logging(self):
        """Test analysis lifecycle logging."""
        with patch('file_utilities_2.core.size_analyzer_logging.LogManager'), \
             patch('file_utilities_2.core.size_analyzer_config.SizeAnalyzerConfig'):
            logger = SizeAnalyzerLogger()
            
            # Mock loggers
            mock_core_logger = Mock()
            mock_perf_logger = Mock()
            logger.loggers['core_logic'] = mock_core_logger
            logger.loggers['performance'] = mock_perf_logger
            
            # Test analysis lifecycle
            logger.log_analysis_start('/test/dir', {'setting': 'value'})
            logger.log_analysis_progress(50, 'Halfway done')
            logger.log_analysis_complete('/test/dir', {
                'file_count': 100,
                'total_size': 1024000,
                'performance_metrics': {
                    'files_per_second': 10.5,
                    'bytes_per_second': 10240.0
                }
            })
            
            # Verify logging calls
            mock_core_logger.info.assert_called()
            mock_core_logger.debug.assert_called()
            mock_perf_logger.info.assert_called()
    
    def test_export_event_logging(self):
        """Test export event logging."""
        with patch('file_utilities_2.core.size_analyzer_logging.LogManager'), \
             patch('file_utilities_2.core.size_analyzer_config.SizeAnalyzerConfig'):
            logger = SizeAnalyzerLogger()
            
            mock_core_logger = Mock()
            mock_error_logger = Mock()
            logger.loggers['core_logic'] = mock_core_logger
            logger.loggers['errors'] = mock_error_logger
            
            # Test successful export
            logger.log_export_event('/path/export.json', 'json', True)
            mock_core_logger.info.assert_called()
            
            # Test failed export
            logger.log_export_event('/path/export.json', 'json', False)
            mock_error_logger.error.assert_called()
    
    def test_hub_event_logging(self):
        """Test hub event logging."""
        with patch('file_utilities_2.core.size_analyzer_logging.LogManager'), \
             patch('file_utilities_2.core.size_analyzer_config.SizeAnalyzerConfig'):
            logger = SizeAnalyzerLogger()
            
            mock_hub_logger = Mock()
            logger.loggers['hub_integration'] = mock_hub_logger
            
            logger.log_hub_event('tool_started', {'tool': 'Size Analyzer'})
            mock_hub_logger.info.assert_called()
    
    def test_configuration_change_logging(self):
        """Test configuration change logging."""
        with patch('file_utilities_2.core.size_analyzer_logging.LogManager'), \
             patch('file_utilities_2.core.size_analyzer_config.SizeAnalyzerConfig'):
            logger = SizeAnalyzerLogger()
            
            mock_core_logger = Mock()
            logger.loggers['core_logic'] = mock_core_logger
            
            logger.log_configuration_change('test_setting', 'old_value', 'new_value')
            mock_core_logger.info.assert_called()
    
    def test_resource_usage_logging(self):
        """Test resource usage logging."""
        with patch('file_utilities_2.core.size_analyzer_logging.LogManager'), \
             patch('file_utilities_2.core.size_analyzer_config.SizeAnalyzerConfig'):
            logger = SizeAnalyzerLogger()
            
            mock_perf_logger = Mock()
            logger.loggers['performance'] = mock_perf_logger
            
            logger.log_resource_usage(50.5, 128.0, 10.5)
            mock_perf_logger.debug.assert_called()
    
    def test_logger_cleanup(self):
        """Test logger cleanup."""
        with patch('file_utilities_2.core.size_analyzer_logging.LogManager'), \
             patch('file_utilities_2.core.size_analyzer_config.SizeAnalyzerConfig'):
            logger = SizeAnalyzerLogger()
            
            # Mock handlers
            mock_handler = Mock()
            mock_logger = Mock()
            mock_logger.handlers = [mock_handler]
            logger.loggers['test'] = mock_logger
            logger.main_logger.handlers = [mock_handler]
            
            # Test cleanup
            logger.cleanup()
            
            # Verify handlers were closed
            mock_handler.close.assert_called()


class TestGlobalLoggingFunctions:
    """Test global logging functions."""
    
    def test_get_size_analyzer_logger(self):
        """Test global logger getter."""
        with patch('file_utilities_2.core.size_analyzer_logging.SizeAnalyzerLogger') as mock_logger_class:
            mock_logger_instance = Mock()
            mock_logger_class.return_value = mock_logger_instance
            
            # First call should create logger
            logger1 = get_size_analyzer_logger()
            assert logger1 == mock_logger_instance
            mock_logger_class.assert_called_once()
            
            # Second call should return same instance
            logger2 = get_size_analyzer_logger()
            assert logger2 == mock_logger_instance
            # Should not create new instance
            assert mock_logger_class.call_count == 1
    
    def test_cleanup_logging(self):
        """Test global logging cleanup."""
        with patch('file_utilities_2.core.size_analyzer_logging.SizeAnalyzerLogger') as mock_logger_class:
            mock_logger_instance = Mock()
            mock_logger_class.return_value = mock_logger_instance
            
            # Create logger
            get_size_analyzer_logger()
            
            # Cleanup
            cleanup_logging()
            
            # Verify cleanup was called
            mock_logger_instance.cleanup.assert_called_once()
    
    def test_get_logger_with_config(self):
        """Test getting logger with custom config."""
        mock_config = Mock()
        
        with patch('file_utilities_2.core.size_analyzer_logging.SizeAnalyzerLogger') as mock_logger_class:
            mock_logger_instance = Mock()
            mock_logger_class.return_value = mock_logger_instance
            
            logger = get_size_analyzer_logger(mock_config)
            
            # Verify logger was created with config
            mock_logger_class.assert_called_with(mock_config)
            assert logger == mock_logger_instance


class TestConfigurationIntegration:
    """Test integration between configuration and logging."""
    
    def test_config_logger_integration(self):
        """Test integration between config and logger."""
        mock_config_manager = Mock()
        mock_config_manager.config = {
            'size_analyzer': {
                'logging': {
                    'enable_tool_logging': True,
                    'log_level': 'DEBUG',
                    'log_categories': {
                        'core_logic': 'INFO',
                        'gui_events': 'DEBUG'
                    }
                }
            }
        }
        
        with patch('file_utilities_2.core.size_analyzer_config.ConfigManager',
                   return_value=mock_config_manager), \
             patch('file_utilities_2.core.size_analyzer_logging.LogManager'):
            
            config = SizeAnalyzerConfig()
            logger = SizeAnalyzerLogger(config)
            
            # Verify integration
            assert logger.config == config
    
    def test_resource_path_logging_integration(self, temp_dir):
        """Test resource path integration with logging."""
        mock_config_manager = Mock()
        mock_config_manager.config = {
            'size_analyzer': {
                'resources': {
                    'log_directory': temp_dir
                },
                'logging': {
                    'enable_tool_logging': True
                }
            }
        }
        
        with patch('file_utilities_2.core.size_analyzer_config.ConfigManager',
                   return_value=mock_config_manager), \
             patch('file_utilities_2.core.size_analyzer_logging.LogManager'):
            
            config = SizeAnalyzerConfig()
            logger = SizeAnalyzerLogger(config)
            
            # Test log directory resolution
            log_dir = logger._ensure_log_directory()
            assert log_dir == temp_dir