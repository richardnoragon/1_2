"""Compatibility wrapper for legacy system monitor imports.

Historically, callers imported `SystemMonitorGUI` from
`src.tools.system.system_monitor`. The active implementation lives in the
process monitor module, so this wrapper preserves the old API surface.
"""

from src.tools.system.process_monitor.process_monitor import (
    ProcessMonitorGUI as SystemMonitorGUI,
)

__all__ = ["SystemMonitorGUI"]
