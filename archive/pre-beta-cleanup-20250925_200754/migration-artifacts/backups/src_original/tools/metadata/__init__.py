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
    from .image_metadata import *
except ImportError as e:
    warnings.warn(f"Could not import image_metadata: {e}")

try:
    from .image_metadata_logic import *
except ImportError as e:
    warnings.warn(f"Could not import image_metadata_logic: {e}")

__all__ = [
    # Export all imported symbols
    # This will be populated by the imported modules
]
