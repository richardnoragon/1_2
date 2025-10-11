"""Advanced File Catalog Generator

A comprehensive file cataloging tool with advanced sorting, color-coding,
and multi-format export capabilities.

Features:
- Multi-criteria sorting (alphabetical, size, type, dates)
- Dynamic color-coding with accessibility support
- Real-time re-sorting capabilities
- Multi-format export (HTML, PDF, CSV, JSON, XML, Excel)
- RFU Hub integration for progress tracking
"""

from .advanced_catalog_window import AdvancedCatalogWindow
from .catalog_data_model import (
    CatalogData,
    ColorScheme,
    FileEntry,
    SortCriteria,
)
from .catalog_tool import CatalogWindow
from .color_coding_engine import ColorCodingEngine
from .sorting_engine import SortingEngine

__version__ = "1.0.0"
__author__ = "Richard's File Utilities"

__all__ = [
    "AdvancedCatalogWindow",
    "FileEntry",
    "CatalogData",
    "SortCriteria",
    "ColorScheme",
    "SortingEngine",
    "ColorCodingEngine",
    "CatalogWindow",
]
