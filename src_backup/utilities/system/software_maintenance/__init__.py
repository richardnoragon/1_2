"""
Software Maintenance Toolkit for Richard's File Utilities

This module provides comprehensive software management capabilities including
an intelligent Software Updater and powerful De-Installer with advanced
automation, safety features, and seamless integration with the main system hub.

Features:
- Intelligent Software Updater with multi-source scanning
- Powerful De-Installer with deep system scanning
- Comprehensive backup and restore capabilities
- Administrative privilege management
- Real-time progress tracking and status reporting
- Seamless integration with RFU Hub
"""

__version__ = "1.0.0"
__author__ = "Richard's File Utilities"

from .core.maintenance_base import MaintenanceToolBase
from .core.software_detector import SoftwareDetector
from .core.security_manager import SecurityManager

__all__ = [
    'MaintenanceToolBase',
    'SoftwareDetector',
    'SecurityManager'
]