"""
src.tools.analysis.size_analyzer package
"""

import os

# Import the main class from the parent module's size_analyzer.py file
import sys

# Add parent directory to path to import the size_analyzer.py file
parent_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, parent_dir)

try:
    from size_analyzer import SizeAnalyzerGUI

    __all__ = ["SizeAnalyzerGUI"]
except ImportError:
    # Fallback import strategy
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "size_analyzer_module", os.path.join(parent_dir, "size_analyzer.py")
    )
    if spec and spec.loader:
        size_analyzer_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(size_analyzer_module)
        SizeAnalyzerGUI = size_analyzer_module.SizeAnalyzerGUI
        __all__ = ["SizeAnalyzerGUI"]
    else:
        __all__ = []
