"""Advanced Folders GUI Package.

Enterprise-grade user interface components for the Advanced Folders feature.
Implements comprehensive folder management, search capabilities, and file organization tools.
"""

from .folder_tree_view import FolderTreeView
from .main_widget import AdvancedFoldersMainWidget
from .menu_manager import AdvancedFoldersMenuManager
from .search_results_table import SearchResultsTable
from .toolbar_manager import AdvancedFoldersToolbar

__version__ = "1.0.0"
__author__ = "RFU Development Team"

__all__ = [
    "AdvancedFoldersMainWidget",
    "FolderTreeView",
    "SearchResultsTable",
    "AdvancedFoldersToolbar",
    "AdvancedFoldersMenuManager",
]
