"""Compatibility bridge for relocated File Finder module.

The File Finder implementation now lives in
``src.tools.file_management.finder.file_finder``. This module keeps
backwards-compatible imports pointing to the consolidated implementation
without retaining the legacy codebase.
"""

from .finder.file_finder import (
    FileFinder,
    FileFinderLogic,
    FileFinderWindow,
)

__all__ = ["FileFinderWindow", "FileFinder", "FileFinderLogic"]
