"""Image metadata integration package.

Exports both the interactive GUI and the core logic module from a single
location to keep imports consistent across the codebase.
"""

from .gui import ImageMetadataEditorGUI
from .image_metadata_logic import (
    ImageMetadataLogic,
    ImageMetadataWorker,
    format_exif_value,
    get_tag_name,
    parse_exif_value,
)

__all__ = [
    "ImageMetadataEditorGUI",
    "ImageMetadataLogic",
    "ImageMetadataWorker",
    "format_exif_value",
    "get_tag_name",
    "parse_exif_value",
]
