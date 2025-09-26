"""
Advanced Folders Feature for Richard's File Utilities

This module provides advanced folder management capabilities including:
- Smart folder creation and configuration
- Dynamic search and filtering
- Real-time file system monitoring
- Enhanced metadata and statistics
- Cross-tool integration
- Import/export functionality
- Backup and restore system

Version: 1.0.0
Author: RFU Development Team
"""

__version__ = "1.0.0"
__author__ = "RFU Development Team"

from .core.backup_restore import (AutomaticBackupScheduler, BackupManager,
                                  BackupMetadata)
# Core imports
from .core.folder_configuration import (FolderConfiguration,
                                        FolderConfigurationManager,
                                        FolderStatistics, SearchParameters,
                                        SortCriteria)
from .core.import_export import (ConfigurationExporter, ConfigurationImporter,
                                 ConflictResolver, ImportExportManager)
from .core.search_engine import FileResult, SearchEngine, SearchProgress

# UI imports (optional, depends on PyQt5 availability)
try:
    from .ui.advanced_folders_widget import AdvancedFoldersWidget
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False

__all__ = [
    "__version__",
    "__author__",
    "FolderConfiguration",
    "FolderConfigurationManager", 
    "SearchEngine",
    "SearchParameters",
    "FolderStatistics",
    "SortCriteria",
    "FileResult",
    "SearchProgress",
    "ImportExportManager",
    "ConfigurationExporter",
    "ConfigurationImporter",
    "ConflictResolver",
    "BackupManager",
    "BackupMetadata",
    "AutomaticBackupScheduler",
    "AdvancedFoldersWidget" if GUI_AVAILABLE else None,
    "GUI_AVAILABLE"
]

# Remove None values from __all__
__all__ = [item for item in __all__ if item is not None]