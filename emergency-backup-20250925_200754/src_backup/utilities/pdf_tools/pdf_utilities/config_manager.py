"""
Configuration Manager Bridge for PDF Utilities
This module provides a bridge between PDF utilities and the main project's
configuration system. Created during Phase 2.1 of PDF utilities integration.
"""

import sys
from pathlib import Path

# Add parent directory to path to import main project modules
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from core.config_manager import ConfigManager as MainConfigManager
except ImportError:
    # Fallback for development/testing
    print("Warning: Could not import main ConfigManager, using fallback")
    MainConfigManager = None


class ConfigManager:
    """
    Bridge class for PDF utilities to use main configuration system.
    
    This class provides backward compatibility for PDF utilities while
    integrating with the main project's configuration system.
    """
    
    def __init__(self):
        """Initialize the configuration bridge."""
        if MainConfigManager:
            self._main_config = MainConfigManager()
            self._ensure_pdf_section()
        else:
            # Fallback configuration for testing
            self._main_config = None
            self._fallback_config = {
                'pdf_tools': {
                    'general': {
                        'last_opened_directory': '',
                        'default_output_directory': ''
                    },
                    'viewer': {
                        'zoom_factor': 1.0,
                        'default_page': 1
                    },
                    'watermark': {
                        'opacity': 0.5,
                        'watermark_text': '',
                        'last_directory': ''
                    }
                }
            }
    
    def _ensure_pdf_section(self):
        """Ensure PDF tools section exists in main config."""
        if not self._main_config:
            return
            
        if 'pdf_tools' not in self._main_config.config:
            self._main_config.config['pdf_tools'] = {
                'general': {
                    'last_opened_directory': '',
                    'default_output_directory': '',
                    'recent_files': [],
                    'max_recent_files': 10
                },
                'viewer': {
                    'zoom_factor': 1.0,
                    'default_page': 1,
                    'fit_to_window': True
                },
                'watermark': {
                    'opacity': 0.5,
                    'watermark_text': '',
                    'last_directory': '',
                    'font_size': 36,
                    'color': '#808080'
                },
                'extract_text': {
                    'default_format': 'txt',
                    'include_page_numbers': True,
                    'preserve_layout': False
                },
                'split': {
                    'default_mode': 'single_pages',
                    'preserve_bookmarks': False
                },
                'merge': {
                    'preserve_bookmarks': True,
                    'optimize_output': True
                }
            }
            self._main_config.save_config()
    
    def get_setting(self, section, key, default=None):
        """
        Get setting from PDF tools section.
        
        Args:
            section: Configuration section name
            key: Setting key
            default: Default value if setting not found
            
        Returns:
            Setting value or default
        """
        if self._main_config:
            setting_key = f'{section}.{key}'
            return self._main_config.get_setting('pdf_tools', setting_key,
                                                 default)
        else:
            # Fallback mode
            pdf_tools = self._fallback_config.get('pdf_tools', {})
            section_config = pdf_tools.get(section, {})
            return section_config.get(key, default)
    
    def set_setting(self, section, key, value):
        """
        Set setting in PDF tools section.
        
        Args:
            section: Configuration section name
            key: Setting key
            value: Setting value
        """
        if self._main_config:
            # Create nested structure if needed
            if 'pdf_tools' not in self._main_config.config:
                self._main_config.config['pdf_tools'] = {}
            if section not in self._main_config.config['pdf_tools']:
                self._main_config.config['pdf_tools'][section] = {}
            
            self._main_config.config['pdf_tools'][section][key] = value
            self._main_config.save_config()
        else:
            # Fallback mode
            if section not in self._fallback_config['pdf_tools']:
                self._fallback_config['pdf_tools'][section] = {}
            self._fallback_config['pdf_tools'][section][key] = value
    
    def get_module_config(self, module_name):
        """
        Get module-specific configuration.
        
        Args:
            module_name: Name of the module
            
        Returns:
            Dictionary of module configuration
        """
        if self._main_config:
            return self._main_config.get_setting('pdf_tools', module_name, {})
        else:
            pdf_tools = self._fallback_config.get('pdf_tools', {})
            return pdf_tools.get(module_name, {})
    
    def set_module_config(self, module_name, config):
        """
        Set module-specific configuration.
        
        Args:
            module_name: Name of the module
            config: Configuration dictionary
        """
        if self._main_config:
            if 'pdf_tools' not in self._main_config.config:
                self._main_config.config['pdf_tools'] = {}
            self._main_config.config['pdf_tools'][module_name] = config
            self._main_config.save_config()
        else:
            self._fallback_config['pdf_tools'][module_name] = config
    
    def add_recent_file(self, file_path):
        """
        Add a file to recent files list.
        
        Args:
            file_path: Path to the file
        """
        recent_files = self.get_setting('general', 'recent_files', [])
        max_recent = self.get_setting('general', 'max_recent_files', 10)
        
        # Remove if already exists
        if file_path in recent_files:
            recent_files.remove(file_path)
        
        # Add to front
        recent_files.insert(0, file_path)
        
        # Keep only max_recent files
        recent_files = recent_files[:max_recent]
        
        self.set_setting('general', 'recent_files', recent_files)
    
    def get_recent_files(self):
        """
        Get list of recent files.
        
        Returns:
            List of recent file paths
        """
        return self.get_setting('general', 'recent_files', [])
    
    def save_config(self):
        """Save configuration to file."""
        if self._main_config:
            self._main_config.save_config()
    
    @property
    def config(self):
        """Get the configuration dictionary for backward compatibility."""
        if self._main_config:
            return self._main_config.config.get('pdf_tools', {})
        else:
            return self._fallback_config.get('pdf_tools', {})


# For backward compatibility with existing code
def get_config_manager():
    """Get a ConfigManager instance."""
    return ConfigManager()


if __name__ == '__main__':
    # Test the configuration bridge
    config = ConfigManager()
    
    # Test setting and getting values
    config.set_setting('general', 'last_opened_directory', '/test/path')
    last_dir = config.get_setting('general', 'last_opened_directory')
    print(f"Last opened directory: {last_dir}")
    
    # Test module config
    viewer_config = {
        'zoom_factor': 1.5,
        'default_page': 2
    }
    config.set_module_config('viewer', viewer_config)
    print(f"Viewer config: {config.get_module_config('viewer')}")
    
    # Test recent files
    config.add_recent_file('/test/file1.pdf')
    config.add_recent_file('/test/file2.pdf')
    print(f"Recent files: {config.get_recent_files()}")
    
    print("Configuration bridge test completed successfully!")