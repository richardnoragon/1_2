"""Main performance monitoring class for comprehensive system performance tracking.

This module provides the primary interface for performance monitoring,
coordinating CPU, memory, and process analysis components.
"""

import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass

from ...core.monitor_base import MonitorBase, AlertLevel
from ...core.data_collector import get_data_collector, DataType
from ...core.platform_detector import get_platform_detector
from core.error_handler import error_handler

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None


@dataclass
class PerformanceThresholds:
    """Performance monitoring thresholds."""
    cpu_warning: float = 80.0  # CPU usage warning threshold (%)
    cpu_critical: float = 95.0  # CPU usage critical threshold (%)
    memory_warning: float = 85.0  # Memory usage warning threshold (%)
    memory_critical: float = 95.0  # Memory usage critical threshold (%)
    load_warning: float = 2.0  # Load average warning threshold
    load_critical: float = 4.0  # Load average critical threshold
    process_cpu_warning: float = 50.0  # Single process CPU warning (%)
    process_memory_warning: float = 25.0  # Single process memory warning (%)


class PerformanceMonitor(MonitorBase):
    """Main performance monitoring class.
    
    Provides comprehensive system performance monitoring including:
    - Real-time CPU usage (per-core and aggregate)
    - Memory usage (physical, virtual, swap)
    - Process-level analysis
    - Load average and system responsiveness
    - Historical trend analysis
    """
    
    def __init__(self, update_interval: float = 2.0):
        """Initialize the performance monitor.
        
        Args:
            update_interval: Update interval in seconds (default: 2.0)
        """
        super().__init__("Performance", update_interval)
        
        # Check dependencies
        if not PSUTIL_AVAILABLE:
            self.logger.warning("psutil not available, limited functionality")
        
        # Performance tracking components
        self._cpu_tracker = None
        self._memory_tracker = None
        self._process_analyzer = None
        
        # Configuration
        self.thresholds = PerformanceThresholds()
        self._enable_per_core_cpu = True
        self._enable_process_analysis = True
        self._max_processes_tracked = 10
        
        # Performance data
        self._cpu_history: List[Dict[str, Any]] = []
        self._memory_history: List[Dict[str, Any]] = []
        self._load_history: List[float] = []
        self._max_history_points = 300  # 10 minutes at 2-second intervals
        
        # Platform-specific implementation
        self._platform_impl = None
        
        # Data collector integration
        self._data_collector = get_data_collector()
        
        self.logger.info("Performance monitor initialized")
    
    def _initialize_platform_specific(self) -> None:
        """Initialize platform-specific performance monitoring."""
        try:
            # Import platform-specific implementation
            platform_detector = get_platform_detector()
            
            if platform_detector.is_windows():
                from .platform_impl.windows_perf import WindowsPerformanceImpl
                self._platform_impl = WindowsPerformanceImpl()
            elif platform_detector.is_macos():
                from .platform_impl.macos_perf import MacOSPerformanceImpl
                self._platform_impl = MacOSPerformanceImpl()
            elif platform_detector.is_linux():
                from .platform_impl.linux_perf import LinuxPerformanceImpl
                self._platform_impl = LinuxPerformanceImpl()
            else:
                self.logger.warning("No platform-specific implementation available")
                
            # Initialize component trackers
            self._initialize_trackers()
            
        except ImportError as e:
            self.logger.warning(f"Platform-specific implementation not available: {e}")
        except Exception as e:
            self.logger.error(f"Error initializing platform-specific components: {e}")
            error_handler.handle_error(e, "PerformanceMonitor._initialize_platform_specific")
    
    def _initialize_trackers(self) -> None:
        """Initialize performance tracking components."""
        try:
            from .cpu_tracker import CPUTracker
            from .memory_tracker import MemoryTracker
            from .process_analyzer import ProcessAnalyzer
            
            self._cpu_tracker = CPUTracker(
                enable_per_core=self._enable_per_core_cpu,
                platform_impl=self._platform_impl
            )
            
            self._memory_tracker = MemoryTracker(
                platform_impl=self._platform_impl
            )
            
            if self._enable_process_analysis:
                self._process_analyzer = ProcessAnalyzer(
                    max_processes=self._max_processes_tracked,
                    platform_impl=self._platform_impl
                )
                
        except Exception as e:
            self.logger.error(f"Error initializing trackers: {e}")
            error_handler.handle_error(e, "PerformanceMonitor._initialize_trackers")
    
    def _collect_data(self) -> Dict[str, Any]:
        """Collect comprehensive performance data.
        
        Returns:
            Dict containing performance metrics
        """
        data = {
            'timestamp': datetime.now().isoformat(),
            'monitor_type': 'performance'
        }
        
        try:
            # Collect CPU data
            if self._cpu_tracker:
                cpu_data = self._cpu_tracker.get_cpu_metrics()
                data.update(cpu_data)
                self._store_cpu_history(cpu_data)
            
            # Collect memory data
            if self._memory_tracker:
                memory_data = self._memory_tracker.get_memory_metrics()
                data.update(memory_data)
                self._store_memory_history(memory_data)
            
            # Collect process data
            if self._process_analyzer:
                process_data = self._process_analyzer.get_process_metrics()
                data['processes'] = process_data
            
            # Collect system load
            load_data = self._collect_system_load()
            data.update(load_data)
            
            # Add platform-specific data
            if self._platform_impl:
                platform_data = self._platform_impl.get_additional_metrics()
                data.update(platform_data)
            
            # Calculate derived metrics
            self._calculate_derived_metrics(data)
            
        except Exception as e:
            self.logger.error(f"Error collecting performance data: {e}")
            error_handler.handle_error(e, "PerformanceMonitor._collect_data")
            
        return data
    
    def _collect_system_load(self) -> Dict[str, Any]:
        """Collect system load information.
        
        Returns:
            Dict containing load metrics
        """
        load_data = {}
        
        try:
            if PSUTIL_AVAILABLE:
                # Get load average (Unix-like systems)
                if hasattr(psutil, 'getloadavg'):
                    load_avg = psutil.getloadavg()
                    load_data.update({
                        'load_1min': load_avg[0],
                        'load_5min': load_avg[1],
                        'load_15min': load_avg[2]
                    })
                    self._load_history.append(load_avg[0])
                
                # Get boot time and uptime
                boot_time = psutil.boot_time()
                uptime = time.time() - boot_time
                load_data.update({
                    'boot_time': datetime.fromtimestamp(boot_time).isoformat(),
                    'uptime_seconds': uptime,
                    'uptime_hours': uptime / 3600
                })
                
                # Get user count
                users = psutil.users()
                load_data['active_users'] = len(users)
                
        except Exception as e:
            self.logger.error(f"Error collecting system load: {e}")
            
        # Limit history size
        if len(self._load_history) > self._max_history_points:
            self._load_history = self._load_history[-self._max_history_points:]
            
        return load_data
    
    def _store_cpu_history(self, cpu_data: Dict[str, Any]) -> None:
        """Store CPU data in history.
        
        Args:
            cpu_data: CPU metrics to store
        """
        history_point = {
            'timestamp': datetime.now(),
            'cpu_percent': cpu_data.get('cpu_percent', 0),
            'cpu_user': cpu_data.get('cpu_user', 0),
            'cpu_system': cpu_data.get('cpu_system', 0),
            'cpu_idle': cpu_data.get('cpu_idle', 0)
        }
        
        if 'cpu_per_core' in cpu_data:
            history_point['cpu_per_core'] = cpu_data['cpu_per_core']
            
        self._cpu_history.append(history_point)
        
        # Limit history size
        if len(self._cpu_history) > self._max_history_points:
            self._cpu_history = self._cpu_history[-self._max_history_points:]
    
    def _store_memory_history(self, memory_data: Dict[str, Any]) -> None:
        """Store memory data in history.
        
        Args:
            memory_data: Memory metrics to store
        """
        history_point = {
            'timestamp': datetime.now(),
            'memory_percent': memory_data.get('memory_percent', 0),
            'memory_used': memory_data.get('memory_used', 0),
            'memory_available': memory_data.get('memory_available', 0),
            'swap_percent': memory_data.get('swap_percent', 0)
        }
        
        self._memory_history.append(history_point)
        
        # Limit history size
        if len(self._memory_history) > self._max_history_points:
            self._memory_history = self._memory_history[-self._max_history_points:]
    
    def _calculate_derived_metrics(self, data: Dict[str, Any]) -> None:
        """Calculate derived performance metrics.
        
        Args:
            data: Performance data to enhance
        """
        try:
            # Calculate CPU trend
            if len(self._cpu_history) >= 2:
                recent_cpu = [point['cpu_percent'] for point in self._cpu_history[-10:]]
                data['cpu_trend'] = self._calculate_trend(recent_cpu)
            
            # Calculate memory trend
            if len(self._memory_history) >= 2:
                recent_memory = [point['memory_percent'] for point in self._memory_history[-10:]]
                data['memory_trend'] = self._calculate_trend(recent_memory)
            
            # Calculate load trend
            if len(self._load_history) >= 2:
                recent_load = self._load_history[-10:]
                data['load_trend'] = self._calculate_trend(recent_load)
            
            # Calculate system responsiveness score
            data['responsiveness_score'] = self._calculate_responsiveness_score(data)
            
        except Exception as e:
            self.logger.error(f"Error calculating derived metrics: {e}")
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from a list of values.
        
        Args:
            values: List of numeric values
            
        Returns:
            Trend direction: 'increasing', 'decreasing', or 'stable'
        """
        if len(values) < 2:
            return 'stable'
            
        # Simple linear trend calculation
        n = len(values)
        x_sum = sum(range(n))
        y_sum = sum(values)
        xy_sum = sum(i * values[i] for i in range(n))
        x2_sum = sum(i * i for i in range(n))
        
        slope = (n * xy_sum - x_sum * y_sum) / (n * x2_sum - x_sum * x_sum)
        
        if slope > 0.5:
            return 'increasing'
        elif slope < -0.5:
            return 'decreasing'
        else:
            return 'stable'
    
    def _calculate_responsiveness_score(self, data: Dict[str, Any]) -> float:
        """Calculate system responsiveness score (0-100).
        
        Args:
            data: Performance data
            
        Returns:
            Responsiveness score
        """
        score = 100.0
        
        # Reduce score based on CPU usage
        cpu_percent = data.get('cpu_percent', 0)
        if cpu_percent > 80:
            score -= (cpu_percent - 80) * 2
        
        # Reduce score based on memory usage
        memory_percent = data.get('memory_percent', 0)
        if memory_percent > 85:
            score -= (memory_percent - 85) * 1.5
        
        # Reduce score based on load average
        load_1min = data.get('load_1min', 0)
        cpu_count = data.get('cpu_count', 1)
        if load_1min > cpu_count:
            score -= (load_1min - cpu_count) * 10
        
        return max(0.0, min(100.0, score))
    
    def _validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate collected performance data.
        
        Args:
            data: Data to validate
            
        Returns:
            True if data is valid, False otherwise
        """
        required_fields = ['timestamp', 'monitor_type']
        
        # Check required fields
        for field in required_fields:
            if field not in data:
                self.logger.warning(f"Missing required field: {field}")
                return False
        
        # Validate numeric ranges
        if 'cpu_percent' in data:
            if not (0 <= data['cpu_percent'] <= 100):
                self.logger.warning(f"Invalid CPU percentage: {data['cpu_percent']}")
                return False
        
        if 'memory_percent' in data:
            if not (0 <= data['memory_percent'] <= 100):
                self.logger.warning(f"Invalid memory percentage: {data['memory_percent']}")
                return False
        
        return True
    
    def _check_alerts(self, data: Dict[str, Any]) -> None:
        """Check for performance alert conditions.
        
        Args:
            data: Current performance data
        """
        try:
            # Check CPU alerts
            cpu_percent = data.get('cpu_percent', 0)
            if cpu_percent >= self.thresholds.cpu_critical:
                self._notify_alert_callbacks(
                    'cpu_usage',
                    AlertLevel.CRITICAL,
                    f"Critical CPU usage: {cpu_percent:.1f}%"
                )
            elif cpu_percent >= self.thresholds.cpu_warning:
                self._notify_alert_callbacks(
                    'cpu_usage',
                    AlertLevel.WARNING,
                    f"High CPU usage: {cpu_percent:.1f}%"
                )
            
            # Check memory alerts
            memory_percent = data.get('memory_percent', 0)
            if memory_percent >= self.thresholds.memory_critical:
                self._notify_alert_callbacks(
                    'memory_usage',
                    AlertLevel.CRITICAL,
                    f"Critical memory usage: {memory_percent:.1f}%"
                )
            elif memory_percent >= self.thresholds.memory_warning:
                self._notify_alert_callbacks(
                    'memory_usage',
                    AlertLevel.WARNING,
                    f"High memory usage: {memory_percent:.1f}%"
                )
            
            # Check load average alerts
            load_1min = data.get('load_1min')
            if load_1min is not None:
                if load_1min >= self.thresholds.load_critical:
                    self._notify_alert_callbacks(
                        'system_load',
                        AlertLevel.CRITICAL,
                        f"Critical system load: {load_1min:.2f}"
                    )
                elif load_1min >= self.thresholds.load_warning:
                    self._notify_alert_callbacks(
                        'system_load',
                        AlertLevel.WARNING,
                        f"High system load: {load_1min:.2f}"
                    )
            
            # Check process alerts
            if 'processes' in data:
                self._check_process_alerts(data['processes'])
                
        except Exception as e:
            self.logger.error(f"Error checking alerts: {e}")
    
    def _check_process_alerts(self, processes: List[Dict[str, Any]]) -> None:
        """Check for process-level alerts.
        
        Args:
            processes: List of process information
        """
        for process in processes:
            try:
                # Check process CPU usage
                cpu_percent = process.get('cpu_percent', 0)
                if cpu_percent >= self.thresholds.process_cpu_warning:
                    process_name = process.get('name', 'Unknown')
                    self._notify_alert_callbacks(
                        'process_cpu',
                        AlertLevel.WARNING,
                        f"High CPU usage by process '{process_name}': {cpu_percent:.1f}%"
                    )
                
                # Check process memory usage
                memory_percent = process.get('memory_percent', 0)
                if memory_percent >= self.thresholds.process_memory_warning:
                    process_name = process.get('name', 'Unknown')
                    self._notify_alert_callbacks(
                        'process_memory',
                        AlertLevel.WARNING,
                        f"High memory usage by process '{process_name}': {memory_percent:.1f}%"
                    )
                    
            except Exception as e:
                self.logger.error(f"Error checking process alerts: {e}")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get current performance health status.
        
        Returns:
            Dict containing health status information
        """
        current_data = self.get_current_data()
        
        status = {
            'overall_health': 'good',
            'cpu_health': 'good',
            'memory_health': 'good',
            'load_health': 'good',
            'responsiveness_score': current_data.get('responsiveness_score', 100),
            'issues': []
        }
        
        try:
            # Check CPU health
            cpu_percent = current_data.get('cpu_percent', 0)
            if cpu_percent >= self.thresholds.cpu_critical:
                status['cpu_health'] = 'critical'
                status['issues'].append(f"Critical CPU usage: {cpu_percent:.1f}%")
            elif cpu_percent >= self.thresholds.cpu_warning:
                status['cpu_health'] = 'warning'
                status['issues'].append(f"High CPU usage: {cpu_percent:.1f}%")
            
            # Check memory health
            memory_percent = current_data.get('memory_percent', 0)
            if memory_percent >= self.thresholds.memory_critical:
                status['memory_health'] = 'critical'
                status['issues'].append(f"Critical memory usage: {memory_percent:.1f}%")
            elif memory_percent >= self.thresholds.memory_warning:
                status['memory_health'] = 'warning'
                status['issues'].append(f"High memory usage: {memory_percent:.1f}%")
            
            # Check load health
            load_1min = current_data.get('load_1min')
            if load_1min is not None:
                if load_1min >= self.thresholds.load_critical:
                    status['load_health'] = 'critical'
                    status['issues'].append(f"Critical system load: {load_1min:.2f}")
                elif load_1min >= self.thresholds.load_warning:
                    status['load_health'] = 'warning'
                    status['issues'].append(f"High system load: {load_1min:.2f}")
            
            # Determine overall health
            health_levels = [status['cpu_health'], status['memory_health'], status['load_health']]
            if 'critical' in health_levels:
                status['overall_health'] = 'critical'
            elif 'warning' in health_levels:
                status['overall_health'] = 'warning'
                
        except Exception as e:
            self.logger.error(f"Error determining health status: {e}")
            status['overall_health'] = 'unknown'
            status['issues'].append("Error determining health status")
        
        return status
    
    def get_performance_summary(self, time_range: timedelta = timedelta(minutes=10)) -> Dict[str, Any]:
        """Get performance summary for the specified time range.
        
        Args:
            time_range: Time range for summary
            
        Returns:
            Dict containing performance summary
        """
        cutoff_time = datetime.now() - time_range
        
        # Filter historical data
        recent_cpu = [point for point in self._cpu_history if point['timestamp'] >= cutoff_time]
        recent_memory = [point for point in self._memory_history if point['timestamp'] >= cutoff_time]
        recent_load = [load for load in self._load_history[-60:]]  # Last 60 points
        
        summary = {
            'time_range': str(time_range),
            'data_points': len(recent_cpu),
            'cpu_summary': {},
            'memory_summary': {},
            'load_summary': {}
        }
        
        # CPU summary
        if recent_cpu:
            cpu_values = [point['cpu_percent'] for point in recent_cpu]
            summary['cpu_summary'] = {
                'min': min(cpu_values),
                'max': max(cpu_values),
                'avg': sum(cpu_values) / len(cpu_values),
                'trend': self._calculate_trend(cpu_values)
            }
        
        # Memory summary
        if recent_memory:
            memory_values = [point['memory_percent'] for point in recent_memory]
            summary['memory_summary'] = {
                'min': min(memory_values),
                'max': max(memory_values),
                'avg': sum(memory_values) / len(memory_values),
                'trend': self._calculate_trend(memory_values)
            }
        
        # Load summary
        if recent_load:
            summary['load_summary'] = {
                'min': min(recent_load),
                'max': max(recent_load),
                'avg': sum(recent_load) / len(recent_load),
                'trend': self._calculate_trend(recent_load)
            }
        
        return summary
    
    def configure_thresholds(self, **kwargs) -> None:
        """Configure performance monitoring thresholds.
        
        Args:
            **kwargs: Threshold values to update
        """
        for key, value in kwargs.items():
            if hasattr(self.thresholds, key):
                setattr(self.thresholds, key, value)
                self.logger.info(f"Updated threshold {key} to {value}")
            else:
                self.logger.warning(f"Unknown threshold: {key}")
    
    def get_cpu_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get CPU usage history.
        
        Args:
            limit: Maximum number of points to return
            
        Returns:
            List of CPU history points
        """
        history = self._cpu_history.copy()
        if limit:
            history = history[-limit:]
        return history
    
    def get_memory_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get memory usage history.
        
        Args:
            limit: Maximum number of points to return
            
        Returns:
            List of memory history points
        """
        history = self._memory_history.copy()
        if limit:
            history = history[-limit:]
        return history