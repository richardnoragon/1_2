"""
Metadata Utilities

This package contains utilities for metadata operations including:
- Image metadata editing and analysis
- Office document metadata handling
- Metadata extraction and manipulation tools
"""

# Import warnings for optional imports
import warnings

# Core metadata utilities
try:
    from . import image_metadata as _image_metadata
    from .image_metadata import *  # noqa: F401,F403
except ImportError as e:
    warnings.warn(f"Could not import image_metadata: {e}")
    __all__ = []
else:
    __all__ = getattr(_image_metadata, "__all__", [])
