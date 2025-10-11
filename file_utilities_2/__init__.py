"""
File Utilities 2 - Enhanced File Management Tools

This package provides a comprehensive suite of file management utilities
with improved architecture, error handling, and user interface.

Version: 2.0.0
Author: File Utilities Team
"""

__version__ = "2.0.0"
__author__ = "File Utilities Team"

# Import core checksum functionality
from .core.check_sum import ChecksumLogic, VALID_ALGORITHMS

# Import tree map functionality
from .core.tree_map_logic import TreeMapLogic

# Import size analyzer functionality
from .core.size_analyzer_logic import SizeAnalyzer, SizeAnalyzerWorker

# Import image metadata functionality
from .core.image_metadata_logic import ImageMetadataLogic

# Import secure delete functionality
from .core.secure_delete_logic import SecureDeleteLogic
from .core.secure_delete_config import SecureDeleteConfig, get_config as get_secure_delete_config
from .core.secure_delete_logging import SecureDeleteLogger, get_logger as get_secure_delete_logger

# Import CMSD functionality
from .core.cmsd_logic import CMSDLogic
from .gui.cmsd_gui import CMSDWindow
from .integration.cmsd_connector import CMSDHubConnector

# Import encryption functionality
from .core.encryption_logic import EncryptionLogic
from .core.encryption_config import EncryptionConfig
from .core.encryption_logging import EncryptionLogger
from .gui.encryption_gui import EncryptionGUI
from .integration.encryption_connector import EncryptionHubConnector

# Import GUI components
from .gui.check_sum_gui import ChecksumGUI
from .gui.check_sum_standardized import ChecksumWindow, MyGUI
from .gui.tree_map_gui import TreeMapGUI, TreeMapView
from .gui.size_analyzer_gui import SizeAnalyzerGUI
from .gui.image_metadata_gui import ImageMetadataEditor
from .gui.secure_delete_gui import SecureDeleteGUI

# Import integration components
from .integration.secure_delete_connector import SecureDeleteHubConnector

# Package metadata
__all__ = [
    "__version__",
    "__author__",
    # Core checksum functionality
    "ChecksumLogic",
    "VALID_ALGORITHMS",
    # Core tree map functionality
    "TreeMapLogic",
    # Core size analyzer functionality
    "SizeAnalyzer",
    "SizeAnalyzerWorker",
    # Core image metadata functionality
    "ImageMetadataLogic",
    # Core secure delete functionality
    "SecureDeleteLogic",
    "SecureDeleteConfig",
    "get_secure_delete_config",
    "SecureDeleteLogger",
    "get_secure_delete_logger",
    # GUI components
    "ChecksumGUI",
    "ChecksumWindow",
    "MyGUI",
    "TreeMapGUI",
    "TreeMapView",
    "SizeAnalyzerGUI",
    "ImageMetadataEditor",
    "SecureDeleteGUI",
    # CMSD functionality
    "CMSDLogic",
    "CMSDWindow",
    "CMSDHubConnector",
    # Encryption functionality
    "EncryptionLogic",
    "EncryptionConfig",
    "EncryptionLogger",
    "EncryptionGUI",
    "EncryptionHubConnector",
    # Integration components
    "SecureDeleteHubConnector",
]