"""File rename operations package."""

from .gui import (
    EnhancedRenameWindow,
    FileRenameWindow,
)
from .rename import RenameWindow as _SimpleRenameWindow
from .rename import main as _simple_main
from .rename_logic import FileRenamer, RenameOperation

RenameWindow = _SimpleRenameWindow
main = _simple_main

__all__ = [
    "FileRenamer",
    "RenameOperation",
    "FileRenameWindow",
    "EnhancedRenameWindow",
    "RenameWindow",
    "main",
]
