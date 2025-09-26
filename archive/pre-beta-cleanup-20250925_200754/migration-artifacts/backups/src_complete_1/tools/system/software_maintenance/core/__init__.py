"""
Core infrastructure for Software Maintenance Toolkit

This module contains the foundational classes and utilities for software
management operations including base classes, security management,
software detection, and cross-platform compatibility.
"""

from .maintenance_base import MaintenanceToolBase
from .software_detector import SoftwareDetector
from .security_manager import SecurityManager
from .update_sources import UpdateSourceManager
from .platform_support import PlatformSupport

__all__ = [
    'MaintenanceToolBase',
    'SoftwareDetector', 
    'SecurityManager',
    'UpdateSourceManager',
    'PlatformSupport'
]