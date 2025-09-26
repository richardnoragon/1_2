"""
Size Analyzer Configuration Manager

This module provides configuration management specifically for the Size Analyzer tool,
integrating with the main configuration system and providing settings persistence.
"""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path


def get_config_manager():
    """Dynamically import config manager to avoid circular imports."""
    try:
        # Try multiple import paths
        import_paths = [
            'src.rfu.core.config_manager',
            'rfu.core.config_manager',
            'src.rfu.config_manager',
            'rfu.config_manager'
        ]
        
        for path in import_paths:
            try:
                module = __import__(path, fromlist=['ConfigManager'])
                return getattr(module, 'ConfigManager', None)
            except ImportError:
                continue
        
        # Fallback to basic configuration
        return None
    except Exception:
        return None


def get_log_manager():
    """Dynamically import log manager to avoid circular imports."""
    try:
        # Try multiple import paths
        import_paths = [
            'src.rfu.core.logging_manager',
            'rfu.core.logging_manager',
            'src.rfu.log_manager',
            'rfu.log_manager'
        ]
        
        for path in import_paths:
            try:
                module = __import__(path, fromlist=['LogManager'])
                return getattr(module, 'LogManager', None)
            except ImportError:
                continue
        
        # Fallback to basic logging
        import logging
        return logging
    except Exception:
        import logging
        return logging


class SizeAnalyzerConfig:
    """
    Configuration manager for Size Analyzer with settings persistence and validation.
    """
    
    def __init__(self, config_manager=None):
        """Initialize the Size Analyzer configuration manager."""
        # Dynamic import to avoid circular dependencies
        ConfigManagerClass = get_config_manager()
        LogManagerClass = get_log_manager()
        
        if config_manager:
            self.config_manager = config_manager
        elif ConfigManagerClass:
            self.config_manager = ConfigManagerClass()
        else:
            # Fallback configuration manager
            self.config_manager = self._create_fallback_config_manager()
        
        if LogManagerClass and hasattr(LogManagerClass, 'get_logger'):
            self.logger = LogManagerClass.get_logger('SizeAnalyzer.Config')
        else:
            # Fallback to basic logging
            import logging
            self.logger = logging.getLogger('SizeAnalyzer.Config')
        self.section_name = 'size_analyzer'
        
        # Default configuration values
        self.defaults = {
            'general': {
                'module_path': 'file_utilities_2.gui.size_analyzer_gui',
                'class_name': 'SizeAnalyzerGUI',
                'last_opened_directory': '',
                'default_output_directory': '',
                'recent_directories': [],
                'max_recent_directories': 10,
                'enable_logging': True,
                'log_level': 'INFO',
                'auto_save_results': True,
                'results_retention_days': 30
            },
            'analysis': {
                'default_top_files_count': 20,
                'progress_update_interval': 100,
                'max_concurrent_operations': 1,
                'include_hidden_files': False,
                'follow_symlinks': False,
                'skip_system_files': True,
                'file_size_threshold': 0,
                'enable_file_type_analysis': True,
                'enable_directory_tree': True,
                'enable_performance_metrics': True
            },
            'export': {
                'default_format': 'json',
                'include_metadata': True,
                'include_performance_metrics': True,
                'include_file_list': True,
                'include_directory_tree': False,
                'compress_exports': False,
                'auto_timestamp_exports': True,
                'export_formats': ['json', 'csv', 'txt']
            },
            'ui': {
                'window_geometry': {
                    'width': 800,
                    'height': 600,
                    'remember_size': True,
                    'remember_position': True,
                    'center_on_screen': True
                },
                'progress_visualization': {
                    'show_progress_bar': True,
                    'show_progress_details': True,
                    'show_time_estimates': True,
                    'update_frequency': 500
                },
                'results_display': {
                    'show_file_types': True,
                    'show_largest_files': True,
                    'show_directory_tree': False,
                    'auto_expand_results': True,
                    'results_font_family': 'Consolas',
                    'results_font_size': 10
                }
            },
            'performance': {
                'enable_performance_monitoring': True,
                'max_memory_usage_mb': 256,
                'max_cpu_usage_percent': 50,
                'operation_timeout_seconds': 300,
                'enable_background_operations': True,
                'priority_level': 'normal',
                'thread_pool_size': 1,
                'cache_size_mb': 32,
                'enable_progress_caching': True
            },
            'resources': {
                'icon_path': 'file_utilities_2/gui/icons/size_analyzer.png',
                'ui_file': 'file_utilities_2/gui/size_analyzer.ui',
                'help_file': 'file_utilities_2/docs/size_analyzer_help.html',
                'template_path': 'file_utilities_2/templates/size_analyzer',
                'cache_directory': 'cache/size_analyzer',
                'temp_directory': 'temp/size_analyzer',
                'log_directory': 'logs/size_analyzer'
            },
            'hub_integration': {
                'enable_hub_integration': True,
                'tool_name': 'Size Analyzer',
                'tool_category': 'analysis',
                'resource_requirements': {
                    'cpu_priority': 'normal',
                    'memory_limit_mb': 256,
                    'disk_io_priority': 'normal'
                },
                'event_broadcasting': {
                    'broadcast_start': True,
                    'broadcast_progress': True,
                    'broadcast_completion': True,
                    'broadcast_errors': True
                },
                'coordination': {
                    'allow_resource_sharing': True,
                    'coordinate_with_tools': ['tree_map', 'checksum'],
                    'exclusive_mode': False
                }
            },
            'logging': {
                'enable_tool_logging': True,
                'log_level': 'INFO',
                'log_file': 'logs/size_analyzer/size_analyzer.log',
                'max_log_size_mb': 10,
                'backup_count': 5,
                'log_format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'log_categories': {
                    'core_logic': 'INFO',
                    'gui_events': 'INFO',
                    'hub_integration': 'INFO',
                    'performance': 'DEBUG',
                    'errors': 'ERROR'
                }
            }
        }
        
        # Initialize configuration if not exists
        self._ensure_configuration_exists()
    
    def _ensure_configuration_exists(self):
        """Ensure the size analyzer configuration section exists."""
        try:
            # Check if size_analyzer section exists in configuration
            existing_config = self.config_manager.config.get(self.section_name, {})
            
            if not existing_config:
                # Create the section with defaults
                self.config_manager.config[self.section_name] = self.defaults.copy()
                self.config_manager.save_config()
                self.logger.info("Created default size analyzer configuration")
            else:
                # Merge with defaults to ensure all keys exist
                self._merge_with_defaults(existing_config)
                
        except Exception as e:
            self.logger.error(f"Error ensuring configuration exists: {e}")
            # Fall back to defaults
            self.config_manager.config[self.section_name] = self.defaults.copy()
    
    def _merge_with_defaults(self, existing_config: Dict[str, Any]):
        """Merge existing configuration with defaults to ensure all keys exist."""
        def merge_dicts(default: Dict[str, Any], existing: Dict[str, Any]) -> Dict[str, Any]:
            """Recursively merge dictionaries."""
            result = default.copy()
            for key, value in existing.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = merge_dicts(result[key], value)
                else:
                    result[key] = value
            return result
        
        merged_config = merge_dicts(self.defaults, existing_config)
        self.config_manager.config[self.section_name] = merged_config
        self.config_manager.save_config()
    
    def get_setting(self, subsection: str, key: str, default: Any = None) -> Any:
        """Get a specific setting value."""
        try:
            section_config = self.config_manager.config.get(self.section_name, {})
            subsection_config = section_config.get(subsection, {})
            value = subsection_config.get(key, default)
            
            # Fall back to defaults if not found
            if value is None and subsection in self.defaults:
                value = self.defaults[subsection].get(key, default)
            
            self.logger.debug(f"Retrieved setting {subsection}.{key}: {value}")
            return value
            
        except Exception as e:
            self.logger.warning(f"Error getting setting {subsection}.{key}: {e}")
            return default
    
    def set_setting(self, subsection: str, key: str, value: Any) -> bool:
        """Set a specific setting value."""
        try:
            if self.section_name not in self.config_manager.config:
                self.config_manager.config[self.section_name] = {}
            
            if subsection not in self.config_manager.config[self.section_name]:
                self.config_manager.config[self.section_name][subsection] = {}
            
            self.config_manager.config[self.section_name][subsection][key] = value
            self.config_manager.save_config()
            
            self.logger.info(f"Updated setting {subsection}.{key} to {value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting {subsection}.{key}: {e}")
            return False
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Get all size analyzer settings."""
        return self.config_manager.config.get(self.section_name, self.defaults.copy())
    
    def reset_to_defaults(self) -> bool:
        """Reset all settings to default values."""
        try:
            self.config_manager.config[self.section_name] = self.defaults.copy()
            self.config_manager.save_config()
            self.logger.info("Reset size analyzer configuration to defaults")
            return True
        except Exception as e:
            self.logger.error(f"Error resetting to defaults: {e}")
            return False
    
    def add_recent_directory(self, directory: str) -> bool:
        """Add a directory to the recent directories list."""
        try:
            recent_dirs = self.get_setting('general', 'recent_directories', [])
            max_recent = self.get_setting('general', 'max_recent_directories', 10)
            
            # Remove if already exists
            if directory in recent_dirs:
                recent_dirs.remove(directory)
            
            # Add to front
            recent_dirs.insert(0, directory)
            
            # Limit to max entries
            recent_dirs = recent_dirs[:max_recent]
            
            return self.set_setting('general', 'recent_directories', recent_dirs)
            
        except Exception as e:
            self.logger.error(f"Error adding recent directory: {e}")
            return False
    
    def get_recent_directories(self) -> list:
        """Get the list of recent directories."""
        return self.get_setting('general', 'recent_directories', [])
    
    def save_window_geometry(self, width: int, height: int, x: int = None, y: int = None) -> bool:
        """Save window geometry settings."""
        try:
            geometry = {
                'width': width,
                'height': height
            }
            
            if x is not None and y is not None:
                geometry.update({'x': x, 'y': y})
            
            current_geometry = self.get_setting('ui', 'window_geometry', {})
            current_geometry.update(geometry)
            
            return self.set_setting('ui', 'window_geometry', current_geometry)
            
        except Exception as e:
            self.logger.error(f"Error saving window geometry: {e}")
            return False
    
    def get_window_geometry(self) -> Dict[str, int]:
        """Get window geometry settings."""
        return self.get_setting('ui', 'window_geometry', {
            'width': 800,
            'height': 600,
            'remember_size': True,
            'remember_position': True,
            'center_on_screen': True
        })
    
    def get_resource_path(self, resource_name: str) -> str:
        """Get the path for a specific resource."""
        resource_path = self.get_setting('resources', resource_name, '')
        
        # Convert to absolute path if relative
        if resource_path and not os.path.isabs(resource_path):
            base_dir = Path(__file__).parent.parent.parent
            resource_path = str(base_dir / resource_path)
        
        return resource_path
    
    def validate_configuration(self) -> Dict[str, list]:
        """Validate the current configuration and return any issues."""
        issues = {
            'errors': [],
            'warnings': [],
            'info': []
        }
        
        try:
            config = self.get_all_settings()
            
            # Validate resource paths
            resources = config.get('resources', {})
            for resource_name, path in resources.items():
                if resource_name.endswith('_path') or resource_name.endswith('_file'):
                    if path and not os.path.exists(self.get_resource_path(resource_name)):
                        issues['warnings'].append(f"Resource not found: {resource_name} -> {path}")
            
            # Validate directories
            for dir_name in ['cache_directory', 'temp_directory', 'log_directory']:
                dir_path = self.get_resource_path(dir_name)
                if dir_path and not os.path.exists(dir_path):
                    try:
                        os.makedirs(dir_path, exist_ok=True)
                        issues['info'].append(f"Created directory: {dir_path}")
                    except Exception as e:
                        issues['errors'].append(f"Cannot create directory {dir_path}: {e}")
            
            # Validate numeric settings
            performance = config.get('performance', {})
            if performance.get('max_memory_usage_mb', 0) < 64:
                issues['warnings'].append("Memory limit is very low, may affect performance")
            
            if performance.get('operation_timeout_seconds', 0) < 30:
                issues['warnings'].append("Operation timeout is very low, may cause premature cancellations")
            
            # Validate analysis settings
            analysis = config.get('analysis', {})
            if analysis.get('default_top_files_count', 0) > 100:
                issues['warnings'].append("Large top files count may impact performance")
            
        except Exception as e:
            issues['errors'].append(f"Configuration validation error: {e}")
        
        return issues
    
    def export_configuration(self, file_path: str) -> bool:
        """Export current configuration to a file."""
        try:
            config = self.get_all_settings()
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Configuration exported to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting configuration: {e}")
            return False
    
    def import_configuration(self, file_path: str) -> bool:
        """Import configuration from a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
            
            # Validate imported configuration
            if not isinstance(imported_config, dict):
                raise ValueError("Invalid configuration format")
            
            # Merge with current configuration
            self.config_manager.config[self.section_name] = imported_config
            self.config_manager.save_config()
            
            self.logger.info(f"Configuration imported from {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error importing configuration: {e}")
            return False
    
    def _create_fallback_config_manager(self):
        """Create a fallback configuration manager."""
        class FallbackConfigManager:
            def __init__(self):
                self.config = {}
            
            def save_config(self):
                pass
            
            def get(self, key, default=None):
                return self.config.get(key, default)
        
        return FallbackConfigManager()