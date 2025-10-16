"""
Metadata Utilities

This package contains utilities for metadata operations including:
- Image metadata editing and analysis
- Office document metadata handling
- File timestamp modification tools
- Metadata extraction and manipulation tools
"""

# Import warnings for optional imports
import warnings

__all__: list[str] = []


def _extend_all(module) -> None:
    """Extend __all__ with exports from a module when available."""
    exported = getattr(module, "__all__", None)
    if not exported:
        return

    for name in exported:
        if name not in __all__:
            __all__.append(name)


# Core metadata utilities
try:
    from . import image_metadata as _image_metadata
    from .image_metadata import *  # noqa: F401,F403

    _extend_all(_image_metadata)
except Exception as e:
    warnings.warn(f"Could not import image_metadata: {e}")

try:
    from . import office_metadata as _office_metadata
    from .office_metadata import *  # noqa: F401,F403

    _extend_all(_office_metadata)
except Exception as e:
    warnings.warn(f"Could not import office_metadata: {e}")

try:
    from . import file_touch as _file_touch
    from .file_touch import *  # noqa: F401,F403

    _extend_all(_file_touch)
except Exception as e:
    warnings.warn(f"Could not import file_touch: {e}")
