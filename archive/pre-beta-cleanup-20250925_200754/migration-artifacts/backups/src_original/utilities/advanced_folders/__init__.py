"""Advanced Folders Management Package.

A comprehensive enterprise-grade folder management system with intelligent
categorization, automated organization, and advanced search capabilities.
"""

# Core backend imports
try:
    from .core import (ConfigurationManager, DateTimeRange, FileMetadata,
                       FolderConfiguration, FolderType, LogLevel,
                       SearchParameter, SearchType, SizeRange, SortBy,
                       ValidationResult)
    from .database import AdvancedFoldersDBManager, AdvancedFoldersSchema
    from .repositories import (CacheStrategy, FileMetadataRepository,
                               FolderConfigurationRepository, QueryFilter,
                               QueryOptions, Repository, RepositoryManager,
                               SearchParameterRepository, UnitOfWork)
    BACKEND_AVAILABLE = True
except ImportError:
    BACKEND_AVAILABLE = False

# GUI components imports
try:
    from .gui.config_tabs import (DisplayConfigTab, FiltersConfigTab,
                                  GeneralConfigTab, SearchConfigTab)
    from .gui.configuration_dialog import FolderConfigurationDialog
    from .gui.directory_browser import DirectoryBrowserWidget
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False

__version__ = "1.0.0"
__author__ = "RFU Development Team"

# Dynamic __all__ based on available components
__all__ = []

if BACKEND_AVAILABLE:
    __all__.extend([
        # Core Models
        'FolderConfiguration',
        'SearchParameter',
        'FileMetadata',
        'ConfigurationManager',
        'FolderType',
        'LogLevel',
        'SortBy',
        'SearchType',
        'DateTimeRange',
        'SizeRange',
        'ValidationResult',
        
        # Database Components
        'AdvancedFoldersSchema',
        'AdvancedFoldersDBManager',
        
        # Repository Pattern
        'Repository',
        'FolderConfigurationRepository',
        'SearchParameterRepository',
        'FileMetadataRepository',
        'UnitOfWork',
        'RepositoryManager',
        'CacheStrategy',
        'QueryFilter',
        'QueryOptions',
    ])

if GUI_AVAILABLE:
    __all__.extend([
        # GUI Components
        'FolderConfigurationDialog',
        'GeneralConfigTab',
        'SearchConfigTab',
        'FiltersConfigTab',
        'DisplayConfigTab',
        'DirectoryBrowserWidget',
    ])