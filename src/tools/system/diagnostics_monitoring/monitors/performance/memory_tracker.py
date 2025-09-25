"""Memory tracking module for comprehensive RAM monitoring.

This module provides detailed memory usage tracking including:
- Physical memory (RAM) usage
- Virtual memory usage
- Swap/page file usage
- Memory breakdown by type
- Memory pressure indicators
"""

import time
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None

from core.error_handler import error_handler


@dataclass
class MemoryInfo:
    """Memory information data structure."""

    total: int
    available: int
    used: int
    free: int
    percent: float
    active: Optional[int] = None
    inactive: Optional[int] = None
    buffers: Optional[int] = None
    cached: Optional[int] = None
    shared: Optional[int] = None
    slab: Optional[int] = None


@dataclass
class SwapInfo:
    """Swap memory information data structure."""

    total: int
    used: int
    free: int
    percent: float
    sin: Optional[int] = None  # Swap in
    sout: Optional[int] = None  # Swap out


class MemoryTracker:
    """Memory usage tracking and analysis.

    Provides comprehensive memory monitoring including physical memory,
    virtual memory, swap usage, and memory pressure indicators.
    """

    def __init__(self, platform_impl: Optional[Any] = None):
        """Initialize the memory tracker.

        Args:
            platform_impl: Platform-specific implementation
        """
        self.platform_impl = platform_impl
        self._last_swap_stats = None
        self._swap_rate_history: List[Dict[str, float]] = []
        self._memory_pressure_history: List[float] = []

        # Memory conversion constants
        self.BYTES_TO_MB = 1024 * 1024
        self.BYTES_TO_GB = 1024 * 1024 * 1024

    def get_memory_metrics(self) -> Dict[str, Any]:
        """Get comprehensive memory metrics.

        Returns:
            Dict containing memory usage information
        """
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "memory_available": PSUTIL_AVAILABLE,
        }

        try:
            if PSUTIL_AVAILABLE:
                # Get virtual memory information
                virtual_memory = self._get_virtual_memory()
                metrics.update(virtual_memory)

                # Get swap memory information
                swap_memory = self._get_swap_memory()
                metrics.update(swap_memory)

                # Calculate memory pressure
                pressure = self._calculate_memory_pressure(virtual_memory)
                metrics["memory_pressure"] = pressure

                # Get platform-specific memory details
                if self.platform_impl:
                    platform_metrics = self.platform_impl.get_memory_details()
                    metrics.update(platform_metrics)

                # Calculate derived metrics
                self._calculate_derived_metrics(metrics)

            else:
                # Fallback when psutil is not available
                metrics.update(self._get_fallback_memory_info())

        except Exception as e:
            error_handler.handle_error(e, "MemoryTracker.get_memory_metrics")
            metrics["error"] = str(e)

        return metrics

    def _get_virtual_memory(self) -> Dict[str, Any]:
        """Get virtual memory information.

        Returns:
            Dict containing virtual memory metrics
        """
        try:
            vmem = psutil.virtual_memory()

            memory_info = {
                "memory_total": vmem.total,
                "memory_available": vmem.available,
                "memory_used": vmem.used,
                "memory_free": vmem.free,
                "memory_percent": vmem.percent,
                "memory_total_gb": round(vmem.total / self.BYTES_TO_GB, 2),
                "memory_available_gb": round(
                    vmem.available / self.BYTES_TO_GB, 2
                ),
                "memory_used_gb": round(vmem.used / self.BYTES_TO_GB, 2),
                "memory_free_gb": round(vmem.free / self.BYTES_TO_GB, 2),
            }

            # Add platform-specific memory details
            if hasattr(vmem, "active"):
                memory_info["memory_active"] = vmem.active
                memory_info["memory_active_gb"] = round(
                    vmem.active / self.BYTES_TO_GB, 2
                )

            if hasattr(vmem, "inactive"):
                memory_info["memory_inactive"] = vmem.inactive
                memory_info["memory_inactive_gb"] = round(
                    vmem.inactive / self.BYTES_TO_GB, 2
                )

            if hasattr(vmem, "buffers"):
                memory_info["memory_buffers"] = vmem.buffers
                memory_info["memory_buffers_gb"] = round(
                    vmem.buffers / self.BYTES_TO_GB, 2
                )

            if hasattr(vmem, "cached"):
                memory_info["memory_cached"] = vmem.cached
                memory_info["memory_cached_gb"] = round(
                    vmem.cached / self.BYTES_TO_GB, 2
                )

            if hasattr(vmem, "shared"):
                memory_info["memory_shared"] = vmem.shared
                memory_info["memory_shared_gb"] = round(
                    vmem.shared / self.BYTES_TO_GB, 2
                )

            if hasattr(vmem, "slab"):
                memory_info["memory_slab"] = vmem.slab
                memory_info["memory_slab_gb"] = round(
                    vmem.slab / self.BYTES_TO_GB, 2
                )

            return memory_info

        except Exception as e:
            error_handler.handle_error(e, "MemoryTracker._get_virtual_memory")
            return {}

    def _get_swap_memory(self) -> Dict[str, Any]:
        """Get swap memory information.

        Returns:
            Dict containing swap memory metrics
        """
        try:
            swap = psutil.swap_memory()

            swap_info = {
                "swap_total": swap.total,
                "swap_used": swap.used,
                "swap_free": swap.free,
                "swap_percent": swap.percent,
                "swap_total_gb": round(swap.total / self.BYTES_TO_GB, 2),
                "swap_used_gb": round(swap.used / self.BYTES_TO_GB, 2),
                "swap_free_gb": round(swap.free / self.BYTES_TO_GB, 2),
            }

            # Calculate swap I/O rates
            if hasattr(swap, "sin") and hasattr(swap, "sout"):
                swap_info["swap_sin"] = swap.sin
                swap_info["swap_sout"] = swap.sout

                # Calculate swap rates
                current_time = time.time()
                if self._last_swap_stats:
                    time_delta = current_time - self._last_swap_stats["time"]
                    if time_delta > 0:
                        sin_rate = (
                            swap.sin - self._last_swap_stats["sin"]
                        ) / time_delta
                        sout_rate = (
                            swap.sout - self._last_swap_stats["sout"]
                        ) / time_delta

                        swap_info["swap_sin_rate"] = max(0, sin_rate)
                        swap_info["swap_sout_rate"] = max(0, sout_rate)

                        # Store swap rate history
                        self._swap_rate_history.append(
                            {
                                "timestamp": current_time,
                                "sin_rate": sin_rate,
                                "sout_rate": sout_rate,
                            }
                        )

                        # Limit history size
                        if len(self._swap_rate_history) > 100:
                            self._swap_rate_history = self._swap_rate_history[
                                -100:
                            ]

                # Update last swap stats
                self._last_swap_stats = {
                    "time": current_time,
                    "sin": swap.sin,
                    "sout": swap.sout,
                }

            return swap_info

        except Exception as e:
            error_handler.handle_error(e, "MemoryTracker._get_swap_memory")
            return {}

    def _calculate_memory_pressure(self, memory_info: Dict[str, Any]) -> float:
        """Calculate memory pressure indicator (0-100).

        Args:
            memory_info: Memory information

        Returns:
            Memory pressure score
        """
        try:
            # Base pressure from memory usage percentage
            memory_percent = memory_info.get("memory_percent", 0)
            pressure = memory_percent

            # Increase pressure if swap is being used heavily
            swap_percent = memory_info.get("swap_percent", 0)
            if swap_percent > 0:
                pressure += swap_percent * 0.5

            # Increase pressure based on swap I/O rates
            swap_sin_rate = memory_info.get("swap_sin_rate", 0)
            swap_sout_rate = memory_info.get("swap_sout_rate", 0)

            if swap_sin_rate > 0 or swap_sout_rate > 0:
                # High swap I/O indicates memory pressure
                swap_io_pressure = min(
                    20, (swap_sin_rate + swap_sout_rate) / 1024
                )
                pressure += swap_io_pressure

            # Cap at 100
            pressure = min(100, pressure)

            # Store pressure history
            self._memory_pressure_history.append(pressure)
            if len(self._memory_pressure_history) > 100:
                self._memory_pressure_history = self._memory_pressure_history[
                    -100:
                ]

            return pressure

        except Exception as e:
            error_handler.handle_error(
                e, "MemoryTracker._calculate_memory_pressure"
            )
            return 0.0

    def _calculate_derived_metrics(self, metrics: Dict[str, Any]) -> None:
        """Calculate derived memory metrics.

        Args:
            metrics: Memory metrics to enhance
        """
        try:
            # Calculate memory efficiency
            total_memory = metrics.get("memory_total", 0)
            available_memory = metrics.get("memory_available", 0)

            if total_memory > 0:
                efficiency = (available_memory / total_memory) * 100
                metrics["memory_efficiency"] = round(efficiency, 2)

            # Calculate swap usage ratio
            swap_total = metrics.get("swap_total", 0)
            swap_used = metrics.get("swap_used", 0)

            if swap_total > 0 and total_memory > 0:
                swap_ratio = (swap_used / total_memory) * 100
                metrics["swap_usage_ratio"] = round(swap_ratio, 2)

            # Calculate memory fragmentation indicator
            if "memory_free" in metrics and "memory_available" in metrics:
                free_memory = metrics["memory_free"]
                available_memory = metrics["memory_available"]

                if available_memory > 0:
                    fragmentation = (
                        (available_memory - free_memory) / available_memory
                    ) * 100
                    metrics["memory_fragmentation"] = round(
                        max(0, fragmentation), 2
                    )

            # Calculate memory trends
            if len(self._memory_pressure_history) >= 2:
                recent_pressure = self._memory_pressure_history[-10:]
                metrics["pressure_trend"] = self._calculate_trend(
                    recent_pressure
                )

        except Exception as e:
            error_handler.handle_error(
                e, "MemoryTracker._calculate_derived_metrics"
            )

    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from a list of values.

        Args:
            values: List of numeric values

        Returns:
            Trend direction: 'increasing', 'decreasing', or 'stable'
        """
        if len(values) < 2:
            return "stable"

        # Simple linear trend calculation
        n = len(values)
        x_sum = sum(range(n))
        y_sum = sum(values)
        xy_sum = sum(i * values[i] for i in range(n))
        x2_sum = sum(i * i for i in range(n))

        if n * x2_sum - x_sum * x_sum == 0:
            return "stable"

        slope = (n * xy_sum - x_sum * y_sum) / (n * x2_sum - x_sum * x_sum)

        if slope > 0.5:
            return "increasing"
        elif slope < -0.5:
            return "decreasing"
        else:
            return "stable"

    def _get_fallback_memory_info(self) -> Dict[str, Any]:
        """Get basic memory information when psutil is not available.

        Returns:
            Dict containing basic memory information
        """
        fallback_info = {
            "memory_total": 0,
            "memory_available": 0,
            "memory_used": 0,
            "memory_percent": 0,
            "swap_total": 0,
            "swap_used": 0,
            "swap_percent": 0,
            "fallback_mode": True,
        }

        try:
            # Try platform-specific fallback methods
            if self.platform_impl:
                platform_info = self.platform_impl.get_fallback_memory_info()
                fallback_info.update(platform_info)

        except Exception as e:
            error_handler.handle_error(
                e, "MemoryTracker._get_fallback_memory_info"
            )

        return fallback_info

    def get_memory_breakdown(self) -> Dict[str, Any]:
        """Get detailed memory breakdown.

        Returns:
            Dict containing detailed memory breakdown
        """
        breakdown = {}

        try:
            if PSUTIL_AVAILABLE:
                vmem = psutil.virtual_memory()

                breakdown = {
                    "physical_memory": {
                        "total": vmem.total,
                        "available": vmem.available,
                        "used": vmem.used,
                        "free": vmem.free,
                        "percent": vmem.percent,
                    }
                }

                # Add detailed breakdown if available
                if hasattr(vmem, "active"):
                    breakdown["memory_types"] = {}

                    if hasattr(vmem, "active"):
                        breakdown["memory_types"]["active"] = vmem.active
                    if hasattr(vmem, "inactive"):
                        breakdown["memory_types"]["inactive"] = vmem.inactive
                    if hasattr(vmem, "buffers"):
                        breakdown["memory_types"]["buffers"] = vmem.buffers
                    if hasattr(vmem, "cached"):
                        breakdown["memory_types"]["cached"] = vmem.cached
                    if hasattr(vmem, "shared"):
                        breakdown["memory_types"]["shared"] = vmem.shared
                    if hasattr(vmem, "slab"):
                        breakdown["memory_types"]["slab"] = vmem.slab

                # Add swap information
                swap = psutil.swap_memory()
                breakdown["swap_memory"] = {
                    "total": swap.total,
                    "used": swap.used,
                    "free": swap.free,
                    "percent": swap.percent,
                }

                if hasattr(swap, "sin"):
                    breakdown["swap_memory"]["sin"] = swap.sin
                if hasattr(swap, "sout"):
                    breakdown["swap_memory"]["sout"] = swap.sout

        except Exception as e:
            error_handler.handle_error(e, "MemoryTracker.get_memory_breakdown")
            breakdown["error"] = str(e)

        return breakdown

    def get_memory_pressure_history(
        self, limit: Optional[int] = None
    ) -> List[float]:
        """Get memory pressure history.

        Args:
            limit: Maximum number of points to return

        Returns:
            List of memory pressure values
        """
        history = self._memory_pressure_history.copy()
        if limit:
            history = history[-limit:]
        return history

    def get_swap_rate_history(
        self, limit: Optional[int] = None
    ) -> List[Dict[str, float]]:
        """Get swap I/O rate history.

        Args:
            limit: Maximum number of points to return

        Returns:
            List of swap rate information
        """
        history = self._swap_rate_history.copy()
        if limit:
            history = history[-limit:]
        return history

    def format_bytes(self, bytes_value: int, unit: str = "auto") -> str:
        """Format bytes value to human-readable string.

        Args:
            bytes_value: Value in bytes
            unit: Target unit ('auto', 'B', 'KB', 'MB', 'GB', 'TB')

        Returns:
            Formatted string
        """
        if unit == "auto":
            # Automatically choose appropriate unit
            if bytes_value >= self.BYTES_TO_GB:
                return f"{bytes_value / self.BYTES_TO_GB:.2f} GB"
            elif bytes_value >= self.BYTES_TO_MB:
                return f"{bytes_value / self.BYTES_TO_MB:.2f} MB"
            elif bytes_value >= 1024:
                return f"{bytes_value / 1024:.2f} KB"
            else:
                return f"{bytes_value} B"
        elif unit == "GB":
            return f"{bytes_value / self.BYTES_TO_GB:.2f} GB"
        elif unit == "MB":
            return f"{bytes_value / self.BYTES_TO_MB:.2f} MB"
        elif unit == "KB":
            return f"{bytes_value / 1024:.2f} KB"
        else:
            return f"{bytes_value} B"
