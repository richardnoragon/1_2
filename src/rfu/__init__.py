"""
Richard's File Utilities - Main Application Package

This package contains the core RFU application including the main hub,
configuration management, and core infrastructure.
"""

__version__ = "3.0.0"
__author__ = "Richard's File Utilities Team"

# Import main components for easy access
from .main import main
from .hub import RFUHub

__all__ = [
    "__version__",
    "__author__",
    "main",
    "RFUHub",
]