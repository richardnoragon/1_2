"""Compatibility wrapper for legacy file finder imports."""

from src.tools.file_management import finder

__all__ = [
    "FileFinderWindow",
    "FileFinder",
    "FileFinderLogic",
    "FileFinderGUI",
    "main",
]

FileFinderWindow = finder.FileFinderWindow
FileFinder = finder.FileFinder
FileFinderLogic = finder.FileFinderLogic
main = finder.main

# Preserve GUI alias expected by older integrations.
FileFinderGUI = FileFinderWindow
