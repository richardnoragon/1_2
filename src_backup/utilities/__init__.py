"""
Richard's File Utilities - Utilities Package

This package contains all the file utility modules organized by category.
"""

__version__ = "3.0.0"

# Import utility categories
from . import file_operations
from . import analysis
from . import metadata
from . import security
from . import pdf_tools
from . import network
from . import privacy
from . import system

__all__ = [
    "__version__",
    "file_operations",
    "analysis", 
    "metadata",
    "security",
    "pdf_tools",
    "network",
    "privacy",
    "system",
]