"""Process analyzer module for process-level performance analysis.

This module provides detailed process monitoring including:
- Top CPU and memory consuming processes
- Process resource usage tracking
- Process lifecycle monitoring
- Resource usage trends per process
- Process performance alerts
"""

import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass
from collections import defaultdict

try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None

from core.error_handler import error_handler


@dataclass
class ProcessInfo:
    """Process information data structure."""

    pid: int
    name: str
    cpu_percent: float
    memory_percent: float
    memory_rss: int
    memory_vms: int
    status: str
    create_time: float
    num_threads: int
    username: Optional[str] = None
    cmdline: Optional[List[str]] = None


class ProcessAnalyzer:
    """Process-level performance analysis.

    Provides comprehensive process monitoring including resource usage
    tracking, top consumers identification, and process lifecycle analysis.
    """

    def __init__(
        self, max_processes: int = 10, platform_impl: Optional[Any] = None
    ):
        """Initialize the process analyzer.

        Args:
            max_processes: Maximum number of top processes to track
            platform_impl: Platform-specific implementation
        """
        self.max_processes = max_processes
        self.platform_impl = platform_impl

        # Process tracking
        self._process_history: Dict[int, List[Dict[str, Any]]] = defaultdict(
            list
        )
        self._process_cache: Dict[int, ProcessInfo] = {}
        self._last_update_time = 0
        self._cache_duration = 1.0  # Cache for 1 second

        # Process statistics
        self._total_processes = 0
        self._running_processes = 0
        self._sleeping_processes = 0
        self._zombie_processes = 0

        # Resource tracking
        self._cpu_intensive_processes: Set[int] = set()
        self._memory_intensive_processes: Set[int] = set()

        # Conversion constants
        self.BYTES_TO_MB = 1024 * 1024
        self.BYTES_TO_GB = 1024 * 1024 * 1024

    def get_process_metrics(self) -> Dict[str, Any]:
        """Get comprehensive process metrics.

        Returns:
            Dict containing process analysis information
        """
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "process_analysis_available": PSUTIL_AVAILABLE,
        }

        try:
            if PSUTIL_AVAILABLE:
                # Get process statistics
                process_stats = self._get_process_statistics()
                metrics.update(process_stats)

                # Get top processes by CPU usage
                top_cpu_processes = self._get_top_cpu_processes()
                metrics["top_cpu_processes"] = top_cpu_processes

                # Get top processes by memory usage
                top_memory_processes = self._get_top_memory_processes()
                metrics["top_memory_processes"] = top_memory_processes

                # Get process resource summary
                resource_summary = self._get_resource_summary()
                metrics.update(resource_summary)

                # Get platform-specific process metrics
                if self.platform_impl:
                    platform_metrics = self.platform_impl.get_process_metrics()
                    metrics.update(platform_metrics)

                # Calculate derived metrics
                self._calculate_derived_metrics(metrics)

            else:
                # Fallback when psutil is not available
                metrics.update(self._get_fallback_process_info())

        except Exception as e:
            error_handler.handle_error(
                e, "ProcessAnalyzer.get_process_metrics"
            )
            metrics["error"] = str(e)

        return metrics

    def _get_process_statistics(self) -> Dict[str, Any]:
        """Get overall process statistics.

        Returns:
            Dict containing process statistics
        """
        try:
            # Get all processes
            processes = list(psutil.process_iter(["pid", "status"]))

            # Count processes by status
            status_counts = defaultdict(int)
            for proc in processes:
                try:
                    status = proc.info["status"]
                    status_counts[status] += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            self._total_processes = len(processes)
            self._running_processes = status_counts.get(
                psutil.STATUS_RUNNING, 0
            )
            self._sleeping_processes = status_counts.get(
                psutil.STATUS_SLEEPING, 0
            )
            self._zombie_processes = status_counts.get(psutil.STATUS_ZOMBIE, 0)

            return {
                "total_processes": self._total_processes,
                "running_processes": self._running_processes,
                "sleeping_processes": self._sleeping_processes,
                "zombie_processes": self._zombie_processes,
                "process_status_breakdown": dict(status_counts),
            }

        except Exception as e:
            error_handler.handle_error(
                e, "ProcessAnalyzer._get_process_statistics"
            )
            return {}

    def _get_top_cpu_processes(self) -> List[Dict[str, Any]]:
        """Get top CPU consuming processes.

        Returns:
            List of top CPU processes
        """
        try:
            processes = []

            # Get all processes with CPU usage
            for proc in psutil.process_iter(["pid", "name", "cpu_percent"]):
                try:
                    proc_info = proc.info
                    if proc_info["cpu_percent"] > 0:
                        # Get additional process information
                        process_data = self._get_detailed_process_info(proc)
                        if process_data:
                            processes.append(process_data)

                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # Sort by CPU usage and return top processes
            processes.sort(key=lambda x: x["cpu_percent"], reverse=True)
            top_processes = processes[: self.max_processes]

            # Track CPU intensive processes
            self._cpu_intensive_processes.update(
                proc["pid"]
                for proc in top_processes
                if proc["cpu_percent"] > 50
            )

            return top_processes

        except Exception as e:
            error_handler.handle_error(
                e, "ProcessAnalyzer._get_top_cpu_processes"
            )
            return []

    def _get_top_memory_processes(self) -> List[Dict[str, Any]]:
        """Get top memory consuming processes.

        Returns:
            List of top memory processes
        """
        try:
            processes = []

            # Get all processes with memory usage
            for proc in psutil.process_iter(["pid", "name", "memory_percent"]):
                try:
                    proc_info = proc.info
                    if proc_info["memory_percent"] > 0:
                        # Get additional process information
                        process_data = self._get_detailed_process_info(proc)
                        if process_data:
                            processes.append(process_data)

                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # Sort by memory usage and return top processes
            processes.sort(key=lambda x: x["memory_percent"], reverse=True)
            top_processes = processes[: self.max_processes]

            # Track memory intensive processes
            self._memory_intensive_processes.update(
                proc["pid"]
                for proc in top_processes
                if proc["memory_percent"] > 25
            )

            return top_processes

        except Exception as e:
            error_handler.handle_error(
                e, "ProcessAnalyzer._get_top_memory_processes"
            )
            return []

    def _get_detailed_process_info(
        self, proc: Any
    ) -> Optional[Dict[str, Any]]:
        """Get detailed information for a process.

        Args:
            proc: psutil Process object

        Returns:
            Dict containing detailed process information
        """
        try:
            # Check cache first
            current_time = time.time()
            if (
                current_time - self._last_update_time < self._cache_duration
                and proc.pid in self._process_cache
            ):
                cached_info = self._process_cache[proc.pid]
                return self._process_info_to_dict(cached_info)

            # Get process information
            with proc.oneshot():
                memory_info = proc.memory_info()

                process_data = {
                    "pid": proc.pid,
                    "name": proc.name(),
                    "cpu_percent": round(proc.cpu_percent(), 2),
                    "memory_percent": round(proc.memory_percent(), 2),
                    "memory_rss": memory_info.rss,
                    "memory_vms": memory_info.vms,
                    "memory_rss_mb": round(
                        memory_info.rss / self.BYTES_TO_MB, 2
                    ),
                    "memory_vms_mb": round(
                        memory_info.vms / self.BYTES_TO_MB, 2
                    ),
                    "status": proc.status(),
                    "create_time": proc.create_time(),
                    "num_threads": proc.num_threads(),
                }

                # Add optional information
                try:
                    process_data["username"] = proc.username()
                except (psutil.AccessDenied, AttributeError):
                    process_data["username"] = None

                try:
                    cmdline = proc.cmdline()
                    process_data["cmdline"] = cmdline[:3] if cmdline else None
                except (psutil.AccessDenied, AttributeError):
                    process_data["cmdline"] = None

                # Calculate process age
                age_seconds = current_time - process_data["create_time"]
                process_data["age_seconds"] = round(age_seconds, 2)
                process_data["age_hours"] = round(age_seconds / 3600, 2)

                # Store in cache
                process_info = ProcessInfo(
                    pid=process_data["pid"],
                    name=process_data["name"],
                    cpu_percent=process_data["cpu_percent"],
                    memory_percent=process_data["memory_percent"],
                    memory_rss=process_data["memory_rss"],
                    memory_vms=process_data["memory_vms"],
                    status=process_data["status"],
                    create_time=process_data["create_time"],
                    num_threads=process_data["num_threads"],
                    username=process_data["username"],
                    cmdline=process_data["cmdline"],
                )
                self._process_cache[proc.pid] = process_info

                # Store in history
                self._store_process_history(proc.pid, process_data)

                return process_data

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess,
        ):
            return None
        except Exception as e:
            error_handler.handle_error(
                e, "ProcessAnalyzer._get_detailed_process_info"
            )
            return None

    def _process_info_to_dict(
        self, process_info: ProcessInfo
    ) -> Dict[str, Any]:
        """Convert ProcessInfo to dictionary.

        Args:
            process_info: ProcessInfo object

        Returns:
            Dict representation of process info
        """
        current_time = time.time()
        age_seconds = current_time - process_info.create_time

        return {
            "pid": process_info.pid,
            "name": process_info.name,
            "cpu_percent": process_info.cpu_percent,
            "memory_percent": process_info.memory_percent,
            "memory_rss": process_info.memory_rss,
            "memory_vms": process_info.memory_vms,
            "memory_rss_mb": round(
                process_info.memory_rss / self.BYTES_TO_MB, 2
            ),
            "memory_vms_mb": round(
                process_info.memory_vms / self.BYTES_TO_MB, 2
            ),
            "status": process_info.status,
            "create_time": process_info.create_time,
            "num_threads": process_info.num_threads,
            "username": process_info.username,
            "cmdline": process_info.cmdline,
            "age_seconds": round(age_seconds, 2),
            "age_hours": round(age_seconds / 3600, 2),
        }

    def _store_process_history(
        self, pid: int, process_data: Dict[str, Any]
    ) -> None:
        """Store process data in history.

        Args:
            pid: Process ID
            process_data: Process information to store
        """
        history_point = {
            "timestamp": datetime.now(),
            "cpu_percent": process_data["cpu_percent"],
            "memory_percent": process_data["memory_percent"],
            "memory_rss": process_data["memory_rss"],
            "num_threads": process_data["num_threads"],
        }

        self._process_history[pid].append(history_point)

        # Limit history size per process
        if len(self._process_history[pid]) > 100:
            self._process_history[pid] = self._process_history[pid][-100:]

    def _get_resource_summary(self) -> Dict[str, Any]:
        """Get resource usage summary across all processes.

        Returns:
            Dict containing resource summary
        """
        try:
            total_cpu = 0
            total_memory_rss = 0
            total_memory_vms = 0
            total_threads = 0
            process_count = 0

            for proc in psutil.process_iter(
                ["cpu_percent", "memory_info", "num_threads"]
            ):
                try:
                    proc_info = proc.info
                    total_cpu += proc_info["cpu_percent"] or 0

                    if proc_info["memory_info"]:
                        total_memory_rss += proc_info["memory_info"].rss
                        total_memory_vms += proc_info["memory_info"].vms

                    total_threads += proc_info["num_threads"] or 0
                    process_count += 1

                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            return {
                "total_cpu_usage": round(total_cpu, 2),
                "total_memory_rss": total_memory_rss,
                "total_memory_vms": total_memory_vms,
                "total_memory_rss_gb": round(
                    total_memory_rss / self.BYTES_TO_GB, 2
                ),
                "total_memory_vms_gb": round(
                    total_memory_vms / self.BYTES_TO_GB, 2
                ),
                "total_threads": total_threads,
                "avg_threads_per_process": round(
                    total_threads / max(process_count, 1), 2
                ),
                "cpu_intensive_processes": len(self._cpu_intensive_processes),
                "memory_intensive_processes": len(
                    self._memory_intensive_processes
                ),
            }

        except Exception as e:
            error_handler.handle_error(
                e, "ProcessAnalyzer._get_resource_summary"
            )
            return {}

    def _calculate_derived_metrics(self, metrics: Dict[str, Any]) -> None:
        """Calculate derived process metrics.

        Args:
            metrics: Process metrics to enhance
        """
        try:
            # Calculate process efficiency metrics
            total_processes = metrics.get("total_processes", 0)
            running_processes = metrics.get("running_processes", 0)

            if total_processes > 0:
                efficiency = (running_processes / total_processes) * 100
                metrics["process_efficiency"] = round(efficiency, 2)

            # Calculate resource concentration
            top_cpu = metrics.get("top_cpu_processes", [])
            if top_cpu:
                top_5_cpu = sum(proc["cpu_percent"] for proc in top_cpu[:5])
                metrics["cpu_concentration_top5"] = round(top_5_cpu, 2)

            top_memory = metrics.get("top_memory_processes", [])
            if top_memory:
                top_5_memory = sum(
                    proc["memory_percent"] for proc in top_memory[:5]
                )
                metrics["memory_concentration_top5"] = round(top_5_memory, 2)

            # Calculate process stability (based on zombie processes)
            zombie_processes = metrics.get("zombie_processes", 0)
            if total_processes > 0:
                stability = (
                    (total_processes - zombie_processes) / total_processes
                ) * 100
                metrics["process_stability"] = round(stability, 2)

        except Exception as e:
            error_handler.handle_error(
                e, "ProcessAnalyzer._calculate_derived_metrics"
            )

    def _get_fallback_process_info(self) -> Dict[str, Any]:
        """Get basic process information when psutil is not available.

        Returns:
            Dict containing basic process information
        """
        fallback_info = {
            "total_processes": 0,
            "running_processes": 0,
            "top_cpu_processes": [],
            "top_memory_processes": [],
            "fallback_mode": True,
        }

        try:
            # Try platform-specific fallback methods
            if self.platform_impl:
                platform_info = self.platform_impl.get_fallback_process_info()
                fallback_info.update(platform_info)

        except Exception as e:
            error_handler.handle_error(
                e, "ProcessAnalyzer._get_fallback_process_info"
            )

        return fallback_info

    def get_process_history(
        self, pid: int, limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get history for a specific process.

        Args:
            pid: Process ID
            limit: Maximum number of points to return

        Returns:
            List of process history points
        """
        if pid not in self._process_history:
            return []

        history = self._process_history[pid].copy()
        if limit:
            history = history[-limit:]
        return history

    def get_process_trends(self, pid: int) -> Dict[str, str]:
        """Get trends for a specific process.

        Args:
            pid: Process ID

        Returns:
            Dict containing trend information
        """
        history = self.get_process_history(pid, limit=10)
        if len(history) < 2:
            return {"cpu_trend": "stable", "memory_trend": "stable"}

        cpu_values = [point["cpu_percent"] for point in history]
        memory_values = [point["memory_percent"] for point in history]

        return {
            "cpu_trend": self._calculate_trend(cpu_values),
            "memory_trend": self._calculate_trend(memory_values),
        }

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

    def cleanup_old_history(
        self, max_age: timedelta = timedelta(hours=1)
    ) -> int:
        """Clean up old process history data.

        Args:
            max_age: Maximum age of history to keep

        Returns:
            Number of history points removed
        """
        cutoff_time = datetime.now() - max_age
        removed_count = 0

        for pid in list(self._process_history.keys()):
            original_count = len(self._process_history[pid])
            self._process_history[pid] = [
                point
                for point in self._process_history[pid]
                if point["timestamp"] >= cutoff_time
            ]
            removed_count += original_count - len(self._process_history[pid])

            # Remove empty histories
            if not self._process_history[pid]:
                del self._process_history[pid]

        return removed_count

    def get_intensive_processes(self) -> Dict[str, List[int]]:
        """Get lists of resource-intensive processes.

        Returns:
            Dict containing lists of intensive process PIDs
        """
        return {
            "cpu_intensive": list(self._cpu_intensive_processes),
            "memory_intensive": list(self._memory_intensive_processes),
        }
