"""
File Explorer Managers Module

Provides clean separation of concerns through specialized manager classes
for pane management, layout coordination, and component lifecycle.

Author: Enterprise Code Guardian Team
Version: 1.0.0
Created: September 28, 2025
"""

from .layout_manager import LayoutManager
from .pane_manager import PaneManager

__all__ = ["LayoutManager", "PaneManager"]
