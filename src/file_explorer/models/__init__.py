"""Data models for the file explorer."""

# Existing models
# New multi-pane explorer models
from .bookmark import Bookmark, BookmarkType
from .center_pane import CenterPane
from .drive_manager import DriveInfo, DriveManager
from .enhanced_file_model import (
    EnhancedFileSystemModel,
    EnhancedSortFilterProxyModel,
    FileTypeClassifier,
    PerformanceMonitor,
)
from .hub_interface_mode import HubInterfaceMode
from .left_pane_tab import LeftPaneTab
from .pane_configuration import LayoutType, PaneConfiguration
from .recent_item import RecentItem, RecentItemType
from .right_pane_tab import RightPaneTab
from .tool import Tool
from .user_preferences import UserPreferences

__all__ = [
    # Existing models
    "EnhancedFileSystemModel",
    "EnhancedSortFilterProxyModel",
    "FileTypeClassifier",
    "PerformanceMonitor",
    "DriveManager",
    "DriveInfo",
    # Multi-pane explorer models
    "Bookmark",
    "BookmarkType",
    "CenterPane",
    "HubInterfaceMode",
    "LeftPaneTab",
    "LayoutType",
    "PaneConfiguration",
    "RecentItem",
    "RecentItemType",
    "RightPaneTab",
    "Tool",
    "UserPreferences",
]
