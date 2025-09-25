"""
src.tools.analysis.empty_folders package
"""

import os

# Import the main class from the parent module's empty_folders.py file
import sys

# Add parent directory to path to import the empty_folders.py file
parent_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, parent_dir)

try:
    from empty_folders import EmptyFoldersGUI

    __all__ = ["EmptyFoldersGUI"]
except ImportError:
    # Fallback import strategy
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "empty_folders_module", os.path.join(parent_dir, "empty_folders.py")
    )
    if spec and spec.loader:
        empty_folders_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(empty_folders_module)
        EmptyFoldersGUI = empty_folders_module.EmptyFoldersGUI
        __all__ = ["EmptyFoldersGUI"]
    else:
        __all__ = []
