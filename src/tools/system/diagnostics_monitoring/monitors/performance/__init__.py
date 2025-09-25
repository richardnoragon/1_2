"""Performance monitoring module for RAM & CPU usage tracking.

This module provides comprehensive cross-platform performance monitoring
capabilities including:
- Real-time CPU usage monitoring (per-core and aggregate)
- Memory usage tracking (physical, virtual, swap)
- Process-level performance analysis
- Historical performance trends
- Configurable performance thresholds

The module integrates with the diagnostics monitoring framework and
provides platform-specific optimizations for Windows, macOS, and Linux.
"""

from .performance_monitor import PerformanceMonitor
from .memory_tracker import MemoryTracker
from .cpu_tracker import CPUTracker
from .process_analyzer import ProcessAnalyzer

__all__ = [
    "PerformanceMonitor",
    "MemoryTracker",
    "CPUTracker",
    "ProcessAnalyzer",
]

__version__ = "1.0.0"
