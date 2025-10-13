"""RFU file splitter package.

This package consolidates the legacy ``src.tools.file_operations.splitter``
module into the enhanced ``file_splitter`` toolkit. It exposes the GUI entry
point together with the primary logic, configuration, and logging utilities so
consumers can rely on a single namespace for all file split and join
operations.
"""

from .file_splitter_config import FileSplitterConfig
from .file_splitter_logging import get_file_splitter_logger
from .file_splitter_logic import (
    FileSplitterError,
    FileSplitterIOError,
    FileSplitterLogic,
    FileSplitterSecurityError,
    FileSplitterValidationError,
)
from .gui import FileSplitJoinGUI

# Transitional alias for callers that still expect the legacy class name.
FileSplitterGUI = FileSplitJoinGUI

__all__ = [
    "FileSplitJoinGUI",
    "FileSplitterGUI",
    "FileSplitterLogic",
    "FileSplitterError",
    "FileSplitterValidationError",
    "FileSplitterIOError",
    "FileSplitterSecurityError",
    "FileSplitterConfig",
    "get_file_splitter_logger",
]
