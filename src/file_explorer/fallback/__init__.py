"""
Fallback Managers Module

Provides simplified implementations when full managers are not available,
ensuring graceful degradation and system stability.

Author: Enterprise Code Guardian Team
Version: 1.0.0
Created: September 28, 2025
"""

from .simple_managers import (
    SimpleLayoutManager,
    SimplePaneManager,
    SimpleToolIntegration,
)

__all__ = ["SimplePaneManager", "SimpleLayoutManager", "SimpleToolIntegration"]
