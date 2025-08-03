"""
CMSD Hub Connector

Integration module for connecting CMSD with the RFU Hub system.
Provides menu registration and utility launch capabilities.
"""

from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from file_utilities_2.gui.cmsd_gui import CMSDWindow


class CMSDHubConnector:
    """Hub integration connector for CMSD utility."""
    
    @staticmethod
    def get_menu_info() -> Dict[str, str]:
        """Get menu information for RFU Hub registration.
        
        Returns:
            Dictionary containing menu configuration
        """
        return {
            'name': 'Content Management System Directory',
            'description': 'Compare and manage files between two directories',
            'category': 'File Management',
            'icon': 'cmsd.png',
            'shortcut': 'Ctrl+Shift+C',
            'tooltip': 'Launch CMSD for directory comparison and management',
            'version': '2.0.0'
        }
    
    @staticmethod
    def launch_utility(parent=None) -> 'CMSDWindow':
        """Launch CMSD utility from hub.
        
        Args:
            parent: Parent window (optional)
            
        Returns:
            CMSDWindow instance
        """
        from file_utilities_2.gui.cmsd_gui import CMSDWindow
        
        window = CMSDWindow()
        if parent:
            window.setParent(parent)
        
        window.show()
        return window
    
    @staticmethod
    def get_utility_info() -> Dict[str, any]:
        """Get detailed utility information.
        
        Returns:
            Dictionary containing utility details
        """
        return {
            'id': 'cmsd',
            'name': 'Content Management System Directory',
            'version': '2.0.0',
            'author': 'File Utilities Team',
            'last_updated': '2025-07-28',
            'description': 'A dual-pane directory comparison tool',
            'features': [
                'Dual directory comparison',
                'File selection and management',
                'Batch file operations',
                'Directory synchronization tools',
                'Modern PyQt5 interface',
                'Integrated with RFU Hub'
            ],
            'requirements': [
                'PyQt5',
                'Python 3.7+'
            ],
            'category': 'File Management',
            'tags': ['directory', 'comparison', 'files', 'management', 'sync']
        }
    
    @staticmethod
    def is_available() -> bool:
        """Check if CMSD utility is available.
        
        Returns:
            True if utility can be launched
        """
        try:
            # Test imports to verify availability
            import file_utilities_2.gui.cmsd_gui  # noqa: F401
            import file_utilities_2.core.cmsd_logic  # noqa: F401
            return True
        except ImportError:
            return False
    
    @staticmethod
    def get_status() -> Dict[str, any]:
        """Get current utility status.
        
        Returns:
            Dictionary containing status information
        """
        return {
            'available': CMSDHubConnector.is_available(),
            'version': '2.0.0',
            'last_check': None,  # Could be implemented for health checks
            'dependencies_ok': True,
            'config_valid': True
        }