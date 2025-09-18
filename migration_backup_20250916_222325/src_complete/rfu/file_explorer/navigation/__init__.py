"""
Navigation System for RFU Multi-Pane File Explorer

This module provides comprehensive navigation capabilities including:
- Editable address bar with auto-completion
- Back/forward/up buttons with state management
- Persistent navigation history with favorites
- Interactive breadcrumb navigation

Author: Richard Noragon
Version: 2.0.0
"""

import logging

# Setup module logging
logger = logging.getLogger('RFU.Navigation')

try:
    # Address bar components
    from .address_bar import (AddressBar, AddressBarCompleter, NavigationEvent,
                              PathValidator)
    # Breadcrumb navigation components
    from .breadcrumb_widget import (BreadcrumbDropdown, BreadcrumbSegment,
                                    BreadcrumbSeparator, BreadcrumbWidget,
                                    ClickableLabel)
    # History management components
    from .history_manager import HistoryDatabase, HistoryEntry, HistoryManager
    # Navigation buttons components
    from .navigation_buttons import NavigationButtonGroup, NavigationState
    
    logger.debug("Navigation system components loaded successfully")
    
except ImportError as e:
    logger.error(f"Failed to import navigation components: {e}")
    # Provide fallback None values for graceful degradation
    AddressBar = None
    AddressBarCompleter = None
    PathValidator = None
    NavigationEvent = None
    NavigationButtonGroup = None
    NavigationState = None
    HistoryManager = None
    HistoryEntry = None
    HistoryDatabase = None
    BreadcrumbWidget = None
    BreadcrumbSegment = None
    ClickableLabel = None
    BreadcrumbDropdown = None
    BreadcrumbSeparator = None

__all__ = [
    # Address bar
    'AddressBar',
    'AddressBarCompleter', 
    'PathValidator',
    'NavigationEvent',
    
    # Navigation buttons
    'NavigationButtonGroup',
    'NavigationState',
    
    # History management
    'HistoryManager',
    'HistoryEntry',
    'HistoryDatabase',
    
    # Breadcrumb navigation
    'BreadcrumbWidget',
    'BreadcrumbSegment',
    'ClickableLabel',
    'BreadcrumbDropdown',
    'BreadcrumbSeparator'
]

# Version information
__version__ = "2.0.0"
__author__ = "Richard Noragon"
__maintainer__ = "RFU Development Team"