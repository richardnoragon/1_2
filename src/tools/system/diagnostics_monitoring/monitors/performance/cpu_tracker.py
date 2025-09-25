"""CPU tracking module for multi-core CPU monitoring.

This module provides detailed CPU usage tracking including:
- Per-core CPU usage monitoring
- Aggregate CPU statistics
- CPU frequency and temperature monitoring
- Load average tracking
- CPU utilization trends
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
class CPUInfo:
    """CPU information data structure."""

    physical_cores: int
    logical_cores: int
    max_frequency: Optional[float]
    min_frequency: Optional[float]
    current_frequency: Optional[float]
    architecture: Optional[str] = None
    vendor: Optional[str] = None
    brand: Optional[str] = None


@dataclass
class CPUTimes:
    """CPU time statistics data structure."""

    user: float
    system: float
    idle: float
    nice: Optional[float] = None
    iowait: Optional[float] = None
    irq: Optional[float] = None
    softirq: Optional[float] = None
    steal: Optional[float] = None
    guest: Optional[float] = None
    guest_nice: Optional[float] = None


class CPUTracker:
    """CPU usage tracking and analysis.

    Provides comprehensive CPU monitoring including per-core usage,
    frequency monitoring, temperature tracking, and load analysis.
    """

    def __init__(
        self, enable_per_core: bool = True, platform_impl: Optional[Any] = None
    ):
        """Initialize the CPU tracker.

        Args:
            enable_per_core: Enable per-core CPU monitoring
            platform_impl: Platform-specific implementation
        """
        self.enable_per_core = enable_per_core
        self.platform_impl = platform_impl

        # CPU information cache
        self._cpu_info: Optional[CPUInfo] = None
        self._last_cpu_times = None
        self._cpu_usage_history: List[Dict[str, Any]] = []
        self._frequency_history: List[Dict[str, float]] = []
        self._temperature_history: List[float] = []

        # Initialize CPU information
        self._initialize_cpu_info()

    def _initialize_cpu_info(self) -> None:
        """Initialize CPU information."""
        try:
            if PSUTIL_AVAILABLE:
                # Get CPU count information
                physical_cores = psutil.cpu_count(logical=False) or 1
                logical_cores = psutil.cpu_count(logical=True) or 1

                # Get CPU frequency information
                freq_info = None
                try:
                    freq_info = psutil.cpu_freq()
                except (AttributeError, OSError):
                    pass

                self._cpu_info = CPUInfo(
                    physical_cores=physical_cores,
                    logical_cores=logical_cores,
                    max_frequency=freq_info.max if freq_info else None,
                    min_frequency=freq_info.min if freq_info else None,
                    current_frequency=freq_info.current if freq_info else None,
                )

                # Get additional CPU information from platform implementation
                if self.platform_impl:
                    platform_info = self.platform_impl.get_cpu_info()
                    if platform_info:
                        self._cpu_info.architecture = platform_info.get(
                            "architecture"
                        )
                        self._cpu_info.vendor = platform_info.get("vendor")
                        self._cpu_info.brand = platform_info.get("brand")

        except Exception as e:
            error_handler.handle_error(e, "CPUTracker._initialize_cpu_info")

    def get_cpu_metrics(self) -> Dict[str, Any]:
        """Get comprehensive CPU metrics.

        Returns:
            Dict containing CPU usage information
        """
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "cpu_available": PSUTIL_AVAILABLE,
        }

        try:
            if PSUTIL_AVAILABLE:
                # Get overall CPU usage
                overall_usage = self._get_overall_cpu_usage()
                metrics.update(overall_usage)

                # Get per-core CPU usage if enabled
                if self.enable_per_core:
                    per_core_usage = self._get_per_core_cpu_usage()
                    metrics.update(per_core_usage)

                # Get CPU times breakdown
                cpu_times = self._get_cpu_times()
                metrics.update(cpu_times)

                # Get CPU frequency information
                frequency_info = self._get_cpu_frequency()
                metrics.update(frequency_info)

                # Get CPU temperature if available
                temperature_info = self._get_cpu_temperature()
                metrics.update(temperature_info)

                # Get load average
                load_info = self._get_load_average()
                metrics.update(load_info)

                # Add CPU information
                if self._cpu_info:
                    metrics.update(self._get_cpu_info_dict())

                # Get platform-specific CPU metrics
                if self.platform_impl:
                    platform_metrics = self.platform_impl.get_cpu_metrics()
                    metrics.update(platform_metrics)

                # Calculate derived metrics
                self._calculate_derived_metrics(metrics)

                # Store usage history
                self._store_usage_history(metrics)

            else:
                # Fallback when psutil is not available
                metrics.update(self._get_fallback_cpu_info())

        except Exception as e:
            error_handler.handle_error(e, "CPUTracker.get_cpu_metrics")
            metrics["error"] = str(e)

        return metrics

    def _get_overall_cpu_usage(self) -> Dict[str, Any]:
        """Get overall CPU usage percentage.

        Returns:
            Dict containing overall CPU usage
        """
        try:
            # Get CPU usage with a short interval for accuracy
            cpu_percent = psutil.cpu_percent(interval=0.1)

            return {
                "cpu_percent": round(cpu_percent, 2),
                "cpu_usage_level": self._categorize_cpu_usage(cpu_percent),
            }

        except Exception as e:
            error_handler.handle_error(e, "CPUTracker._get_overall_cpu_usage")
            return {}

    def _get_per_core_cpu_usage(self) -> Dict[str, Any]:
        """Get per-core CPU usage.

        Returns:
            Dict containing per-core CPU usage
        """
        try:
            # Get per-CPU usage
            per_cpu = psutil.cpu_percent(interval=0.1, percpu=True)

            per_core_info = {
                "cpu_per_core": [round(usage, 2) for usage in per_cpu],
                "cpu_core_count": len(per_cpu),
                "cpu_max_core_usage": round(max(per_cpu), 2),
                "cpu_min_core_usage": round(min(per_cpu), 2),
                "cpu_avg_core_usage": round(sum(per_cpu) / len(per_cpu), 2),
            }

            # Identify heavily loaded cores
            high_usage_cores = [
                i for i, usage in enumerate(per_cpu) if usage > 80
            ]
            per_core_info["cpu_high_usage_cores"] = high_usage_cores

            return per_core_info

        except Exception as e:
            error_handler.handle_error(e, "CPUTracker._get_per_core_cpu_usage")
            return {}

    def _get_cpu_times(self) -> Dict[str, Any]:
        """Get CPU time statistics.

        Returns:
            Dict containing CPU time breakdown
        """
        try:
            cpu_times = psutil.cpu_times()

            times_info = {
                "cpu_user": round(cpu_times.user, 2),
                "cpu_system": round(cpu_times.system, 2),
                "cpu_idle": round(cpu_times.idle, 2),
            }

            # Add optional CPU time fields if available
            if hasattr(cpu_times, "nice"):
                times_info["cpu_nice"] = round(cpu_times.nice, 2)
            if hasattr(cpu_times, "iowait"):
                times_info["cpu_iowait"] = round(cpu_times.iowait, 2)
            if hasattr(cpu_times, "irq"):
                times_info["cpu_irq"] = round(cpu_times.irq, 2)
            if hasattr(cpu_times, "softirq"):
                times_info["cpu_softirq"] = round(cpu_times.softirq, 2)
            if hasattr(cpu_times, "steal"):
                times_info["cpu_steal"] = round(cpu_times.steal, 2)
            if hasattr(cpu_times, "guest"):
                times_info["cpu_guest"] = round(cpu_times.guest, 2)
            if hasattr(cpu_times, "guest_nice"):
                times_info["cpu_guest_nice"] = round(cpu_times.guest_nice, 2)

            # Calculate CPU time percentages
            total_time = sum(
                [
                    cpu_times.user,
                    cpu_times.system,
                    cpu_times.idle,
                    getattr(cpu_times, "nice", 0),
                    getattr(cpu_times, "iowait", 0),
                    getattr(cpu_times, "irq", 0),
                    getattr(cpu_times, "softirq", 0),
                    getattr(cpu_times, "steal", 0),
                    getattr(cpu_times, "guest", 0),
                    getattr(cpu_times, "guest_nice", 0),
                ]
            )

            if total_time > 0:
                times_info["cpu_user_percent"] = round(
                    (cpu_times.user / total_time) * 100, 2
                )
                times_info["cpu_system_percent"] = round(
                    (cpu_times.system / total_time) * 100, 2
                )
                times_info["cpu_idle_percent"] = round(
                    (cpu_times.idle / total_time) * 100, 2
                )

            return times_info

        except Exception as e:
            error_handler.handle_error(e, "CPUTracker._get_cpu_times")
            return {}

    def _get_cpu_frequency(self) -> Dict[str, Any]:
        """Get CPU frequency information.

        Returns:
            Dict containing CPU frequency data
        """
        try:
            freq_info = {}

            # Get current CPU frequency
            try:
                freq = psutil.cpu_freq()
                if freq:
                    freq_info.update(
                        {
                            "cpu_freq_current": round(freq.current, 2),
                            "cpu_freq_min": (
                                round(freq.min, 2) if freq.min else None
                            ),
                            "cpu_freq_max": (
                                round(freq.max, 2) if freq.max else None
                            ),
                        }
                    )

                    # Calculate frequency utilization
                    if freq.max and freq.max > 0:
                        utilization = (freq.current / freq.max) * 100
                        freq_info["cpu_freq_utilization"] = round(
                            utilization, 2
                        )

            except (AttributeError, OSError):
                pass

            # Get per-core frequencies if available
            try:
                per_cpu_freq = psutil.cpu_freq(percpu=True)
                if per_cpu_freq:
                    freq_info["cpu_freq_per_core"] = [
                        round(freq.current, 2) for freq in per_cpu_freq
                    ]

            except (AttributeError, OSError):
                pass

            # Store frequency history
            if freq_info:
                current_time = time.time()
                self._frequency_history.append(
                    {
                        "timestamp": current_time,
                        "frequency": freq_info.get("cpu_freq_current", 0),
                    }
                )

                # Limit history size
                if len(self._frequency_history) > 100:
                    self._frequency_history = self._frequency_history[-100:]

            return freq_info

        except Exception as e:
            error_handler.handle_error(e, "CPUTracker._get_cpu_frequency")
            return {}

    def _get_cpu_temperature(self) -> Dict[str, Any]:
        """Get CPU temperature information.

        Returns:
            Dict containing CPU temperature data
        """
        temp_info = {}

        try:
            # Try to get temperature from psutil
            if hasattr(psutil, "sensors_temperatures"):
                temps = psutil.sensors_temperatures()

                # Look for CPU temperature sensors
                cpu_temps = []
                for name, entries in temps.items():
                    if any(
                        keyword in name.lower()
                        for keyword in ["cpu", "core", "processor"]
                    ):
                        for entry in entries:
                            if entry.current:
                                cpu_temps.append(entry.current)

                if cpu_temps:
                    avg_temp = sum(cpu_temps) / len(cpu_temps)
                    temp_info.update(
                        {
                            "cpu_temperature": round(avg_temp, 1),
                            "cpu_temperature_max": round(max(cpu_temps), 1),
                            "cpu_temperature_min": round(min(cpu_temps), 1),
                            "cpu_temperature_cores": [
                                round(temp, 1) for temp in cpu_temps
                            ],
                        }
                    )

                    # Store temperature history
                    self._temperature_history.append(avg_temp)
                    if len(self._temperature_history) > 100:
                        self._temperature_history = self._temperature_history[
                            -100:
                        ]

            # Try platform-specific temperature monitoring
            if self.platform_impl and not temp_info:
                platform_temp = self.platform_impl.get_cpu_temperature()
                temp_info.update(platform_temp)

        except Exception as e:
            error_handler.handle_error(e, "CPUTracker._get_cpu_temperature")

        return temp_info

    def _get_load_average(self) -> Dict[str, Any]:
        """Get system load average.

        Returns:
            Dict containing load average information
        """
        load_info = {}

        try:
            # Get load average (Unix-like systems)
            if hasattr(psutil, "getloadavg"):
                load_avg = psutil.getloadavg()
                load_info.update(
                    {
                        "load_1min": round(load_avg[0], 2),
                        "load_5min": round(load_avg[1], 2),
                        "load_15min": round(load_avg[2], 2),
                    }
                )

                # Calculate load per core
                if self._cpu_info:
                    cores = self._cpu_info.logical_cores
                    load_info.update(
                        {
                            "load_per_core_1min": round(
                                load_avg[0] / cores, 2
                            ),
                            "load_per_core_5min": round(
                                load_avg[1] / cores, 2
                            ),
                            "load_per_core_15min": round(
                                load_avg[2] / cores, 2
                            ),
                        }
                    )

                    # Categorize load level
                    load_info["load_level"] = self._categorize_load_level(
                        load_avg[0], cores
                    )

        except Exception as e:
            error_handler.handle_error(e, "CPUTracker._get_load_average")

        return load_info

    def _get_cpu_info_dict(self) -> Dict[str, Any]:
        """Get CPU information as dictionary.

        Returns:
            Dict containing CPU information
        """
        if not self._cpu_info:
            return {}

        return {
            "cpu_physical_cores": self._cpu_info.physical_cores,
            "cpu_logical_cores": self._cpu_info.logical_cores,
            "cpu_max_frequency": self._cpu_info.max_frequency,
            "cpu_min_frequency": self._cpu_info.min_frequency,
            "cpu_architecture": self._cpu_info.architecture,
            "cpu_vendor": self._cpu_info.vendor,
            "cpu_brand": self._cpu_info.brand,
        }

    def _calculate_derived_metrics(self, metrics: Dict[str, Any]) -> None:
        """Calculate derived CPU metrics.

        Args:
            metrics: CPU metrics to enhance
        """
        try:
            # Calculate CPU efficiency score
            cpu_percent = metrics.get("cpu_percent", 0)
            load_1min = metrics.get("load_1min", 0)
            cores = metrics.get("cpu_logical_cores", 1)

            # Efficiency based on CPU usage vs load
            if cores > 0:
                expected_load = (cpu_percent / 100) * cores
                if load_1min > 0:
                    efficiency = min(100, (expected_load / load_1min) * 100)
                    metrics["cpu_efficiency"] = round(efficiency, 2)

            # Calculate CPU balance (how evenly distributed load is across cores)
            if "cpu_per_core" in metrics:
                per_core = metrics["cpu_per_core"]
                if len(per_core) > 1:
                    avg_usage = sum(per_core) / len(per_core)
                    variance = sum(
                        (usage - avg_usage) ** 2 for usage in per_core
                    ) / len(per_core)
                    balance_score = max(0, 100 - (variance / 10))
                    metrics["cpu_balance_score"] = round(balance_score, 2)

            # Calculate CPU trends
            if len(self._cpu_usage_history) >= 2:
                recent_usage = [
                    point["cpu_percent"]
                    for point in self._cpu_usage_history[-10:]
                    if "cpu_percent" in point
                ]
                if recent_usage:
                    metrics["cpu_trend"] = self._calculate_trend(recent_usage)

        except Exception as e:
            error_handler.handle_error(
                e, "CPUTracker._calculate_derived_metrics"
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

    def _store_usage_history(self, metrics: Dict[str, Any]) -> None:
        """Store CPU usage in history.

        Args:
            metrics: CPU metrics to store
        """
        history_point = {
            "timestamp": datetime.now(),
            "cpu_percent": metrics.get("cpu_percent", 0),
            "load_1min": metrics.get("load_1min", 0),
        }

        if "cpu_per_core" in metrics:
            history_point["cpu_per_core"] = metrics["cpu_per_core"]

        self._cpu_usage_history.append(history_point)

        # Limit history size
        if len(self._cpu_usage_history) > 300:
            self._cpu_usage_history = self._cpu_usage_history[-300:]

    def _categorize_cpu_usage(self, cpu_percent: float) -> str:
        """Categorize CPU usage level.

        Args:
            cpu_percent: CPU usage percentage

        Returns:
            Usage level category
        """
        if cpu_percent < 25:
            return "low"
        elif cpu_percent < 50:
            return "moderate"
        elif cpu_percent < 75:
            return "high"
        else:
            return "very_high"

    def _categorize_load_level(self, load: float, cores: int) -> str:
        """Categorize system load level.

        Args:
            load: Load average value
            cores: Number of CPU cores

        Returns:
            Load level category
        """
        load_per_core = load / cores

        if load_per_core < 0.5:
            return "low"
        elif load_per_core < 0.8:
            return "moderate"
        elif load_per_core < 1.0:
            return "high"
        else:
            return "overloaded"

    def _get_fallback_cpu_info(self) -> Dict[str, Any]:
        """Get basic CPU information when psutil is not available.

        Returns:
            Dict containing basic CPU information
        """
        fallback_info = {
            "cpu_percent": 0,
            "cpu_physical_cores": 1,
            "cpu_logical_cores": 1,
            "fallback_mode": True,
        }

        try:
            # Try platform-specific fallback methods
            if self.platform_impl:
                platform_info = self.platform_impl.get_fallback_cpu_info()
                fallback_info.update(platform_info)

        except Exception as e:
            error_handler.handle_error(e, "CPUTracker._get_fallback_cpu_info")

        return fallback_info

    def get_cpu_usage_history(
        self, limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get CPU usage history.

        Args:
            limit: Maximum number of points to return

        Returns:
            List of CPU usage history points
        """
        history = self._cpu_usage_history.copy()
        if limit:
            history = history[-limit:]
        return history

    def get_temperature_history(
        self, limit: Optional[int] = None
    ) -> List[float]:
        """Get CPU temperature history.

        Args:
            limit: Maximum number of points to return

        Returns:
            List of temperature values
        """
        history = self._temperature_history.copy()
        if limit:
            history = history[-limit:]
        return history

    def get_frequency_history(
        self, limit: Optional[int] = None
    ) -> List[Dict[str, float]]:
        """Get CPU frequency history.

        Args:
            limit: Maximum number of points to return

        Returns:
            List of frequency information
        """
        history = self._frequency_history.copy()
        if limit:
            history = history[-limit:]
        return history
