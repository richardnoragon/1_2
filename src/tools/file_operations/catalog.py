"""Compatibility wrapper for legacy catalog imports.

This module exposes the catalog tool from its new location under
``src.tools.file_management`` so older import paths continue to work.
"""

from src.tools.file_management.advanced_catalog import catalog_tool

CatalogWindow = catalog_tool.CatalogWindow

__all__ = ["CatalogWindow", "CatalogGUI"]

# Maintain historical alias used by older tooling.
CatalogGUI = CatalogWindow
