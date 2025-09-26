"""
Privacy tools implementations.

This package contains the individual privacy cleaning tools.
"""

from .secure_empty_trash import SecureEmptyTrashTool
from .delete_cookies import DeleteCookiesTool
from .delete_history import DeleteHistoryTool
from .delete_file_history import DeleteFileHistoryTool
from .delete_downloads import DeleteDownloadsTool

__all__ = [
    'SecureEmptyTrashTool',
    'DeleteCookiesTool',
    'DeleteHistoryTool',
    'DeleteFileHistoryTool',
    'DeleteDownloadsTool'
]