"""Battery Health Monitor - Comprehensive cross-platform battery monitoring and health analysis.

This module provides comprehensive battery health monitoring capabilities including:
- Real-time battery status monitoring
- Battery health analysis and degradation tracking
- Charge cycle tracking and lifespan analysis
- Power consumption analysis
- Charging pattern optimization
- Cross-platform battery data collection

The module supports Windows (WMI, Power Management APIs), macOS (IOKit, system_profiler, pmset),
and Linux (/sys/class/power_supply, ACPI, upower) platforms.
"""

from .battery_monitor import BatteryMonitor
from .health_analyzer import BatteryHealthAnalyzer
from .cycle_tracker import ChargeCycleTracker

__all__ = ["BatteryMonitor", "BatteryHealthAnalyzer", "ChargeCycleTracker"]

__version__ = "1.0.0"
__author__ = "Richard's File Utilities"
__description__ = "Cross-platform battery health monitoring and analysis"
