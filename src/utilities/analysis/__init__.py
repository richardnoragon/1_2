"""
Richard's File Utilities - Analysis Tools

This package contains file analysis utilities including:
- Size Analyzer: Disk space usage analysis
- Duplicate Finder: Find and manage duplicate files  
- Checksum Calculator: File integrity verification
"""

import sys
from pathlib import Path

# Add current directory to path for relative imports
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Import main GUI classes with error handling
try:
    from .size_analyzer import SizeAnalyzerGUI
except ImportError as e:
    print(f"Warning: Could not import SizeAnalyzerGUI: {e}")
    SizeAnalyzerGUI = None

try:
    from .find_duplicate_files import DuplicateFinderApp
except ImportError as e:
    print(f"Warning: Could not import DuplicateFinderApp: {e}")
    DuplicateFinderApp = None

try:
    from .check_sum import ChecksumGUI
except ImportError as e:
    print(f"Warning: Could not import ChecksumGUI: {e}")
    ChecksumGUI = None

# Import core logic classes with error handling
try:
    from .core.size_analyzer_logic import SizeAnalyzer, SizeAnalyzerWorker
except ImportError as e:
    print(f"Warning: Could not import core logic classes: {e}")
    SizeAnalyzer = None
    SizeAnalyzerWorker = None

# Import configuration classes with error handling
try:
    from .config.size_analyzer_config import SizeAnalyzerConfig
except ImportError as e:
    print(f"Warning: Could not import configuration classes: {e}")
    SizeAnalyzerConfig = None

# Export all available classes
__all__ = [
    'SizeAnalyzerGUI',
    'DuplicateFinderApp', 
    'ChecksumGUI',
    'SizeAnalyzer',
    'SizeAnalyzerWorker',
    'SizeAnalyzerConfig'
]

# Provide module information for debugging


def get_available_classes():
    """Return a dictionary of available classes and their status."""
    return {
        'SizeAnalyzerGUI': SizeAnalyzerGUI is not None,
        'DuplicateFinderApp': DuplicateFinderApp is not None,
        'ChecksumGUI': ChecksumGUI is not None,
        'SizeAnalyzer': SizeAnalyzer is not None,
        'SizeAnalyzerWorker': SizeAnalyzerWorker is not None,
        'SizeAnalyzerConfig': SizeAnalyzerConfig is not None
    }


def validate_imports():
    """Validate that all expected imports are available."""
    available = get_available_classes()
    missing = [name for name, status in available.items() if not status]
    
    if missing:
        print(f"Missing imports in analysis package: {missing}")
        return False
    return True
