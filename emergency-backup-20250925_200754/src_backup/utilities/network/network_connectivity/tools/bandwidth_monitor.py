"""Bandwidth Monitor tool for real-time network speed tracking and analysis."""

import time
import threading
import json
import csv
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from pathlib import Path

from ..core.network_base import (
    NetworkToolBase, NetworkOperationResult, NetworkAlertLevel
)
from ..core.platform_network import (
    PlatformNetworkDetector, NetworkInterface, NetworkStats
)


@dataclass
class SpeedMeasurement:
    """Single speed measurement data point."""
    timestamp: datetime
    interface_name: str
    download_speed_mbps: float
    upload_speed_mbps: float
    total_bytes_recv: int
    total_bytes_sent: int
    measurement_interval: float


@dataclass
class BandwidthAlert:
    """Bandwidth alert information."""
    alert_type: str
    level: NetworkAlertLevel
    message: str
    timestamp: datetime
    interface_name: str
    threshold_value: float
    current_value: float


class SpeedCalculator:
    """Real-time speed calculation engine."""
    
    def __init__(self, interface_name: str, platform_detector: 
                 PlatformNetworkDetector):
        """Initialize speed calculator.
        
        Args:
            interface_name: Network interface to monitor
            platform_detector: Platform network detector instance
        """
        self.interface_name = interface_name
        self.platform_detector = platform_detector
        self.previous_stats: Optional[NetworkStats] = None
        self.previous_time: Optional[float] = None
        
    def calculate_speed(self) -> Optional[SpeedMeasurement]:
        """Calculate current speed based on interface statistics.
        
        Returns:
            SpeedMeasurement if calculation successful, None otherwise
        """
        current_time = time.time()
        current_stats = self.platform_detector.get_interface_stats(
            self.interface_name
        )
        
        if not current_stats:
            return None
        
        # Need previous measurement for speed calculation
        if self.previous_stats is None or self.previous_time is None:
            self.previous_stats = current_stats
            self.previous_time = current_time
            return None
        
        # Calculate time difference
        time_diff = current_time - self.previous_time
        if time_diff <= 0:
            return None
        
        # Calculate byte differences
        bytes_recv_diff = (current_stats.bytes_recv -
                           self.previous_stats.bytes_recv)
        bytes_sent_diff = (current_stats.bytes_sent -
                           self.previous_stats.bytes_sent)
        
        # Handle counter rollover (unlikely but possible)
        if bytes_recv_diff < 0:
            bytes_recv_diff = current_stats.bytes_recv
        if bytes_sent_diff < 0:
            bytes_sent_diff = current_stats.bytes_sent
        
        # Calculate speeds in Mbps
        download_speed_mbps = (bytes_recv_diff * 8) / (time_diff * 1000000)
        upload_speed_mbps = (bytes_sent_diff * 8) / (time_diff * 1000000)
        
        measurement = SpeedMeasurement(
            timestamp=datetime.now(),
            interface_name=self.interface_name,
            download_speed_mbps=download_speed_mbps,
            upload_speed_mbps=upload_speed_mbps,
            total_bytes_recv=current_stats.bytes_recv,
            total_bytes_sent=current_stats.bytes_sent,
            measurement_interval=time_diff
        )
        
        # Update previous values
        self.previous_stats = current_stats
        self.previous_time = current_time
        
        return measurement
    
    def reset(self):
        """Reset calculator state."""
        self.previous_stats = None
        self.previous_time = None


class HistoricalDataManager:
    """Manages historical bandwidth data storage and retrieval."""
    
    def __init__(self, retention_hours: int = 24, max_entries: int = 10000):
        """Initialize data manager.
        
        Args:
            retention_hours: Hours to retain data
            max_entries: Maximum number of entries to keep
        """
        self.retention_hours = retention_hours
        self.max_entries = max_entries
        self.data: List[SpeedMeasurement] = []
        self._lock = threading.Lock()
    
    def add_measurement(self, measurement: SpeedMeasurement):
        """Add a new measurement to historical data.
        
        Args:
            measurement: Speed measurement to add
        """
        with self._lock:
            self.data.append(measurement)
            self._cleanup_old_data()
    
    def _cleanup_old_data(self):
        """Remove old data based on retention policy."""
        if not self.data:
            return
        
        # Remove by age
        cutoff_time = datetime.now() - timedelta(hours=self.retention_hours)
        self.data = [m for m in self.data if m.timestamp > cutoff_time]
        
        # Remove by count
        if len(self.data) > self.max_entries:
            self.data = self.data[-self.max_entries:]
    
    def get_measurements(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        interface_name: Optional[str] = None
    ) -> List[SpeedMeasurement]:
        """Get measurements within specified criteria.
        
        Args:
            start_time: Start time filter
            end_time: End time filter
            interface_name: Interface name filter
            
        Returns:
            List of matching measurements
        """
        with self._lock:
            filtered_data = self.data.copy()
        
        if start_time:
            filtered_data = [m for m in filtered_data
                             if m.timestamp >= start_time]
        
        if end_time:
            filtered_data = [m for m in filtered_data
                             if m.timestamp <= end_time]
        
        if interface_name:
            filtered_data = [m for m in filtered_data
                             if m.interface_name == interface_name]
        
        return filtered_data
    
    def get_statistics(
        self,
        interface_name: Optional[str] = None,
        hours: int = 1
    ) -> Dict[str, float]:
        """Get statistical summary of measurements.
        
        Args:
            interface_name: Interface to analyze
            hours: Hours of data to analyze
            
        Returns:
            Dictionary with statistical data
        """
        start_time = datetime.now() - timedelta(hours=hours)
        measurements = self.get_measurements(
            start_time=start_time,
            interface_name=interface_name
        )
        
        if not measurements:
            return {
                'avg_download_mbps': 0.0,
                'avg_upload_mbps': 0.0,
                'max_download_mbps': 0.0,
                'max_upload_mbps': 0.0,
                'min_download_mbps': 0.0,
                'min_upload_mbps': 0.0,
                'total_data_gb': 0.0,
                'measurement_count': 0
            }
        
        download_speeds = [m.download_speed_mbps for m in measurements]
        upload_speeds = [m.upload_speed_mbps for m in measurements]
        
        # Calculate total data transferred (approximate)
        total_bytes = 0
        if measurements:
            first_measurement = measurements[0]
            last_measurement = measurements[-1]
            total_bytes = (
                (last_measurement.total_bytes_recv - 
                 first_measurement.total_bytes_recv) +
                (last_measurement.total_bytes_sent - 
                 first_measurement.total_bytes_sent)
            )
        
        return {
            'avg_download_mbps': sum(download_speeds) / len(download_speeds),
            'avg_upload_mbps': sum(upload_speeds) / len(upload_speeds),
            'max_download_mbps': max(download_speeds),
            'max_upload_mbps': max(upload_speeds),
            'min_download_mbps': min(download_speeds),
            'min_upload_mbps': min(upload_speeds),
            'total_data_gb': total_bytes / (1024 ** 3),
            'measurement_count': len(measurements)
        }
    
    def clear_data(self):
        """Clear all historical data."""
        with self._lock:
            self.data.clear()


class AlertManager:
    """Manages bandwidth threshold monitoring and notifications."""
    
    def __init__(self):
        """Initialize alert manager."""
        self.thresholds: Dict[str, Dict[str, float]] = {}
        self.alert_callbacks: List[Callable[[BandwidthAlert], None]] = []
        self.recent_alerts: List[BandwidthAlert] = []
        self.alert_cooldown = 60  # seconds between same type alerts
        self._lock = threading.Lock()
    
    def set_threshold(
        self,
        interface_name: str,
        threshold_type: str,
        value: float
    ):
        """Set a threshold for monitoring.
        
        Args:
            interface_name: Interface to monitor
            threshold_type: Type of threshold (e.g., 'max_download', 
                          'max_upload', 'min_speed')
            value: Threshold value in Mbps
        """
        with self._lock:
            if interface_name not in self.thresholds:
                self.thresholds[interface_name] = {}
            self.thresholds[interface_name][threshold_type] = value
    
    def check_thresholds(self, measurement: SpeedMeasurement):
        """Check measurement against configured thresholds.
        
        Args:
            measurement: Speed measurement to check
        """
        interface_name = measurement.interface_name
        
        with self._lock:
            if interface_name not in self.thresholds:
                return
            
            thresholds = self.thresholds[interface_name]
        
        # Check download speed thresholds
        if 'max_download' in thresholds:
            if measurement.download_speed_mbps > thresholds['max_download']:
                self._trigger_alert(
                    'max_download_exceeded',
                    NetworkAlertLevel.WARNING,
                    f"Download speed {measurement.download_speed_mbps:.2f} "
                    f"Mbps exceeds threshold {thresholds['max_download']:.2f} "
                    f"Mbps",
                    measurement.interface_name,
                    thresholds['max_download'],
                    measurement.download_speed_mbps
                )
        
        if 'min_download' in thresholds:
            if measurement.download_speed_mbps < thresholds['min_download']:
                self._trigger_alert(
                    'min_download_not_met',
                    NetworkAlertLevel.CRITICAL,
                    f"Download speed {measurement.download_speed_mbps:.2f} "
                    f"Mbps below threshold {thresholds['min_download']:.2f} "
                    f"Mbps",
                    measurement.interface_name,
                    thresholds['min_download'],
                    measurement.download_speed_mbps
                )
        
        # Check upload speed thresholds
        if 'max_upload' in thresholds:
            if measurement.upload_speed_mbps > thresholds['max_upload']:
                self._trigger_alert(
                    'max_upload_exceeded',
                    NetworkAlertLevel.WARNING,
                    f"Upload speed {measurement.upload_speed_mbps:.2f} Mbps "
                    f"exceeds threshold {thresholds['max_upload']:.2f} Mbps",
                    measurement.interface_name,
                    thresholds['max_upload'],
                    measurement.upload_speed_mbps
                )
        
        if 'min_upload' in thresholds:
            if measurement.upload_speed_mbps < thresholds['min_upload']:
                self._trigger_alert(
                    'min_upload_not_met',
                    NetworkAlertLevel.CRITICAL,
                    f"Upload speed {measurement.upload_speed_mbps:.2f} Mbps "
                    f"below threshold {thresholds['min_upload']:.2f} Mbps",
                    measurement.interface_name,
                    thresholds['min_upload'],
                    measurement.upload_speed_mbps
                )
    
    def _trigger_alert(
        self,
        alert_type: str,
        level: NetworkAlertLevel,
        message: str,
        interface_name: str,
        threshold_value: float,
        current_value: float
    ):
        """Trigger an alert if not in cooldown period.
        
        Args:
            alert_type: Type of alert
            level: Alert level
            message: Alert message
            interface_name: Interface name
            threshold_value: Threshold that was breached
            current_value: Current measured value
        """
        # Check cooldown
        now = datetime.now()
        for recent_alert in self.recent_alerts:
            if (recent_alert.alert_type == alert_type and
                recent_alert.interface_name == interface_name and
                (now - recent_alert.timestamp).total_seconds() <
                    self.alert_cooldown):
                return  # Still in cooldown
        
        alert = BandwidthAlert(
            alert_type=alert_type,
            level=level,
            message=message,
            timestamp=now,
            interface_name=interface_name,
            threshold_value=threshold_value,
            current_value=current_value
        )
        
        with self._lock:
            self.recent_alerts.append(alert)
            # Keep only recent alerts
            cutoff_time = now - timedelta(hours=1)
            self.recent_alerts = [
                a for a in self.recent_alerts if a.timestamp > cutoff_time
            ]
        
        # Notify callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception:
                # Log error but don't fail
                pass
    
    def add_alert_callback(self, callback: Callable[[BandwidthAlert], None]):
        """Add callback for alert notifications.
        
        Args:
            callback: Function to call when alerts are triggered
        """
        self.alert_callbacks.append(callback)
    
    def get_recent_alerts(
        self,
        hours: int = 1,
        interface_name: Optional[str] = None
    ) -> List[BandwidthAlert]:
        """Get recent alerts.
        
        Args:
            hours: Hours of alerts to retrieve
            interface_name: Filter by interface name
            
        Returns:
            List of recent alerts
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        with self._lock:
            alerts = [a for a in self.recent_alerts
                      if a.timestamp > cutoff_time]
        
        if interface_name:
            alerts = [a for a in alerts if a.interface_name == interface_name]
        
        return alerts


class DataExporter:
    """Handles exporting bandwidth data to various formats."""
    
    def __init__(self, data_manager: HistoricalDataManager):
        """Initialize data exporter.
        
        Args:
            data_manager: Historical data manager instance
        """
        self.data_manager = data_manager
    
    def export_to_csv(
        self,
        file_path: Path,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        interface_name: Optional[str] = None
    ) -> bool:
        """Export data to CSV format.
        
        Args:
            file_path: Output file path
            start_time: Start time filter
            end_time: End time filter
            interface_name: Interface name filter
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            measurements = self.data_manager.get_measurements(
                start_time=start_time,
                end_time=end_time,
                interface_name=interface_name
            )
            
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'timestamp', 'interface_name', 'download_speed_mbps',
                    'upload_speed_mbps', 'total_bytes_recv',
                    'total_bytes_sent', 'measurement_interval'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for measurement in measurements:
                    row = asdict(measurement)
                    row['timestamp'] = measurement.timestamp.isoformat()
                    writer.writerow(row)
            
            return True
        
        except Exception:
            return False
    
    def export_to_json(
        self,
        file_path: Path,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        interface_name: Optional[str] = None,
        include_statistics: bool = True
    ) -> bool:
        """Export data to JSON format.
        
        Args:
            file_path: Output file path
            start_time: Start time filter
            end_time: End time filter
            interface_name: Interface name filter
            include_statistics: Whether to include statistical summary
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            measurements = self.data_manager.get_measurements(
                start_time=start_time,
                end_time=end_time,
                interface_name=interface_name
            )
            
            # Convert measurements to serializable format
            data = {
                'export_timestamp': datetime.now().isoformat(),
                'filters': {
                    'start_time': (start_time.isoformat()
                                   if start_time else None),
                    'end_time': (end_time.isoformat()
                                 if end_time else None),
                    'interface_name': interface_name
                },
                'measurements': []
            }
            
            for measurement in measurements:
                measurement_dict = asdict(measurement)
                measurement_dict['timestamp'] = (
                    measurement.timestamp.isoformat()
                )
                data['measurements'].append(measurement_dict)
            
            # Add statistics if requested
            if include_statistics and measurements:
                hours = 24  # Default to 24 hours of statistics
                if start_time and end_time:
                    hours = int((end_time - start_time).total_seconds() / 3600)
                
                data['statistics'] = self.data_manager.get_statistics(
                    interface_name=interface_name,
                    hours=hours
                )
            
            with open(file_path, 'w', encoding='utf-8') as jsonfile:
                json.dump(data, jsonfile, indent=2, ensure_ascii=False)
            
            return True
        
        except Exception:
            return False


class BandwidthMonitor(NetworkToolBase):
    """Main bandwidth monitoring tool with real-time tracking and analysis."""
    
    def __init__(self):
        """Initialize bandwidth monitor."""
        super().__init__("BandwidthMonitor")
        
        # Core components
        self.platform_detector = PlatformNetworkDetector()
        self.speed_calculators: Dict[str, SpeedCalculator] = {}
        self.data_manager = HistoricalDataManager()
        self.alert_manager = AlertManager()
        self.data_exporter = DataExporter(self.data_manager)
        
        # Monitoring state
        self.monitored_interfaces: List[str] = []
        self.monitoring_interval = 1.0  # seconds
        self._monitoring_thread: Optional[threading.Thread] = None
        self._monitoring_active = False
        
        # Load configuration
        self._load_configuration()
        
        # Set up alert callback
        self.alert_manager.add_alert_callback(self._handle_alert)
    
    def _load_configuration(self):
        """Load tool configuration."""
        # Get monitoring interval
        self.monitoring_interval = self.get_tool_config(
            'monitoring_interval', 1000
        ) / 1000.0  # Convert ms to seconds
        
        # Get data retention settings
        retention_hours = self.get_tool_config('data_retention_hours', 24)
        self.data_manager.retention_hours = retention_hours
        
        # Get alert thresholds
        alert_threshold = self.get_tool_config('alert_threshold_mbps', 100.0)
        enable_alerts = self.get_tool_config('enable_alerts', True)
        
        if enable_alerts:
            # Set default thresholds for all interfaces
            interfaces = self.platform_detector.get_active_interfaces()
            for interface in interfaces:
                self.alert_manager.set_threshold(
                    interface.name, 'max_download', alert_threshold
                )
                self.alert_manager.set_threshold(
                    interface.name, 'max_upload', alert_threshold
                )
    
    def execute_operation(self, **kwargs) -> NetworkOperationResult:
        """Execute bandwidth monitoring operation.
        
        Args:
            **kwargs: Operation parameters
                - operation_type: 'start_monitoring', 'stop_monitoring', 
                                'get_current_speeds', 'get_statistics'
                - interface_names: List of interfaces to monitor
                - duration_seconds: Duration for monitoring
                
        Returns:
            NetworkOperationResult with operation results
        """
        operation_type = kwargs.get('operation_type', 'get_current_speeds')
        
        try:
            if operation_type == 'start_monitoring':
                return self._start_monitoring_operation(**kwargs)
            elif operation_type == 'stop_monitoring':
                return self._stop_monitoring_operation()
            elif operation_type == 'get_current_speeds':
                return self._get_current_speeds_operation(**kwargs)
            elif operation_type == 'get_statistics':
                return self._get_statistics_operation(**kwargs)
            elif operation_type == 'export_data':
                return self._export_data_operation(**kwargs)
            else:
                raise ValueError(f"Unknown operation type: {operation_type}")
        
        except Exception as e:
            return NetworkOperationResult(
                success=False,
                operation_type=operation_type,
                data={},
                error_message=str(e)
            )
    
    def _start_monitoring_operation(self, **kwargs) -> NetworkOperationResult:
        """Start bandwidth monitoring."""
        interface_names = kwargs.get('interface_names', [])
        
        if not interface_names:
            # Auto-detect active interfaces
            active_interfaces = self.platform_detector.get_active_interfaces()
            interface_names = [iface.name for iface in active_interfaces]
        
        if not interface_names:
            raise ValueError("No network interfaces available for monitoring")
        
        # Validate interfaces
        available_interfaces = self.platform_detector.get_network_interfaces()
        available_names = [iface.name for iface in available_interfaces]
        
        invalid_interfaces = [name for name in interface_names
                              if name not in available_names]
        if invalid_interfaces:
            raise ValueError(
                f"Invalid interfaces: {', '.join(invalid_interfaces)}"
            )
        
        # Start monitoring
        success = self.start_monitoring(interface_names)
        
        return NetworkOperationResult(
            success=success,
            operation_type='start_monitoring',
            data={
                'monitored_interfaces': self.monitored_interfaces,
                'monitoring_interval': self.monitoring_interval,
                'is_monitoring': self._monitoring_active
            }
        )
    
    def _stop_monitoring_operation(self) -> NetworkOperationResult:
        """Stop bandwidth monitoring."""
        success = self.stop_monitoring()
        
        return NetworkOperationResult(
            success=success,
            operation_type='stop_monitoring',
            data={
                'was_monitoring': not self._monitoring_active,
                'data_points_collected': len(self.data_manager.data)
            }
        )
    
    def _get_current_speeds_operation(
            self, **kwargs) -> NetworkOperationResult:
        """Get current speeds for monitored interfaces."""
        interface_name = kwargs.get('interface_name')
        
        current_speeds = {}
        
        if interface_name:
            # Get speed for specific interface
            if interface_name in self.speed_calculators:
                measurement = self.speed_calculators[
                    interface_name].calculate_speed()
                if measurement:
                    current_speeds[interface_name] = asdict(measurement)
        else:
            # Get speeds for all monitored interfaces
            for name, calculator in self.speed_calculators.items():
                measurement = calculator.calculate_speed()
                if measurement:
                    current_speeds[name] = asdict(measurement)
        
        return NetworkOperationResult(
            success=True,
            operation_type='get_current_speeds',
            data={
                'current_speeds': current_speeds,
                'timestamp': datetime.now().isoformat()
            }
        )
    
    def _get_statistics_operation(self, **kwargs) -> NetworkOperationResult:
        """Get bandwidth statistics."""
        interface_name = kwargs.get('interface_name')
        hours = kwargs.get('hours', 1)
        
        statistics = self.data_manager.get_statistics(
            interface_name=interface_name,
            hours=hours
        )
        
        return NetworkOperationResult(
            success=True,
            operation_type='get_statistics',
            data={
                'statistics': statistics,
                'interface_name': interface_name,
                'hours_analyzed': hours
            }
        )
    
    def _export_data_operation(self, **kwargs) -> NetworkOperationResult:
        """Export bandwidth data."""
        file_path = Path(kwargs.get('file_path', 'bandwidth_data.csv'))
        export_format = kwargs.get('format', 'csv').lower()
        start_time = kwargs.get('start_time')
        end_time = kwargs.get('end_time')
        interface_name = kwargs.get('interface_name')
        
        if export_format == 'csv':
            success = self.data_exporter.export_to_csv(
                file_path, start_time, end_time, interface_name
            )
        elif export_format == 'json':
            success = self.data_exporter.export_to_json(
                file_path, start_time, end_time, interface_name
            )
        else:
            raise ValueError(f"Unsupported export format: {export_format}")
        
        return NetworkOperationResult(
            success=success,
            operation_type='export_data',
            data={
                'file_path': str(file_path),
                'format': export_format,
                'exported': success
            }
        )
    
    def start_monitoring(self, interface_names: List[str]) -> bool:
        """Start monitoring specified interfaces.
        
        Args:
            interface_names: List of interface names to monitor
            
        Returns:
            True if monitoring started successfully
        """
        if self._monitoring_active:
            self.logger.warning("Monitoring is already active")
            return False
        
        try:
            # Initialize speed calculators
            self.speed_calculators.clear()
            for interface_name in interface_names:
                self.speed_calculators[interface_name] = SpeedCalculator(
                    interface_name, self.platform_detector
                )
            
            self.monitored_interfaces = interface_names.copy()
            self._monitoring_active = True
            
            # Start monitoring thread
            self._monitoring_thread = threading.Thread(
                target=self._monitoring_loop,
                name="BandwidthMonitoringLoop",
                daemon=True
            )
            self._monitoring_thread.start()
            
            self.logger.info(
                f"Started monitoring interfaces: {', '.join(interface_names)}"
            )
            self.status_changed.emit("Monitoring started")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to start monitoring: {e}")
            self._monitoring_active = False
            return False
    
    def stop_monitoring(self) -> bool:
        """Stop bandwidth monitoring.
        
        Returns:
            True if monitoring stopped successfully
        """
        if not self._monitoring_active:
            self.logger.warning("Monitoring is not active")
            return True
        
        try:
            self._monitoring_active = False
            
            # Wait for monitoring thread to finish
            if self._monitoring_thread and self._monitoring_thread.is_alive():
                self._monitoring_thread.join(timeout=5.0)
            
            self.speed_calculators.clear()
            self.monitored_interfaces.clear()
            
            self.logger.info("Stopped bandwidth monitoring")
            self.status_changed.emit("Monitoring stopped")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to stop monitoring: {e}")
            return False
    
    def _monitoring_loop(self):
        """Main monitoring loop."""
        self.logger.debug("Starting bandwidth monitoring loop")
        
        while self._monitoring_active:
            try:
                # Collect measurements from all interfaces
                for interface_name, calculator in (
                        self.speed_calculators.items()):
                    measurement = calculator.calculate_speed()
                    
                    if measurement:
                        # Store measurement
                        self.data_manager.add_measurement(measurement)
                        
                        # Check alerts
                        self.alert_manager.check_thresholds(measurement)
                        
                        # Emit data update signal
                        measurement_dict = asdict(measurement)
                        measurement_dict['timestamp'] = (
                            measurement.timestamp.isoformat()
                        )
                        self.data_updated.emit(measurement_dict)
                        
                        # Store in base class for callbacks
                        self._store_data(measurement_dict)
                
                # Wait for next measurement
                time.sleep(self.monitoring_interval)
            
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.monitoring_interval)
        
        self.logger.debug("Bandwidth monitoring loop stopped")
    
    def _handle_alert(self, alert: BandwidthAlert):
        """Handle bandwidth alerts.
        
        Args:
            alert: Bandwidth alert to handle
        """
        self.logger.warning(f"Bandwidth alert: {alert.message}")
        
        # Emit alert signal
        self._notify_alert_callbacks(
            alert.alert_type, alert.level, alert.message
        )
    
    def get_supported_protocols(self) -> List[str]:
        """Get list of supported protocols."""
        return ["TCP", "UDP", "ICMP"]
    
    def validate_parameters(self, **kwargs) -> bool:
        """Validate operation parameters."""
        operation_type = kwargs.get('operation_type')
        
        if not operation_type:
            return False
        
        valid_operations = [
            'start_monitoring', 'stop_monitoring', 'get_current_speeds',
            'get_statistics', 'export_data'
        ]
        
        if operation_type not in valid_operations:
            return False
        
        # Validate interface names if provided
        interface_names = kwargs.get('interface_names', [])
        if interface_names:
            available_interfaces = (
                self.platform_detector.get_network_interfaces()
            )
            available_names = [iface.name for iface in available_interfaces]
            
            for name in interface_names:
                if name not in available_names:
                    return False
        
        return True
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status."""
        return {
            'is_monitoring': self._monitoring_active,
            'monitored_interfaces': self.monitored_interfaces.copy(),
            'monitoring_interval': self.monitoring_interval,
            'data_points_collected': len(self.data_manager.data),
            'platform_supported': self.platform_detector.is_supported(),
            'available_interfaces': len(
                self.platform_detector.get_network_interfaces()
            ),
            'recent_alerts': len(self.alert_manager.get_recent_alerts()),
            'capabilities': self.platform_detector.get_capabilities()
        }
    
    def get_monitored_interfaces(self) -> List[str]:
        """Get list of currently monitored interfaces.
        
        Returns:
            List of interface names being monitored
        """
        return self.monitored_interfaces.copy()
    
    def get_available_interfaces(self) -> List[NetworkInterface]:
        """Get list of available network interfaces.
        
        Returns:
            List of available network interfaces
        """
        return self.platform_detector.get_network_interfaces()
    
    def set_monitoring_interval(self, interval_seconds: float):
        """Set monitoring interval.
        
        Args:
            interval_seconds: Monitoring interval in seconds
        """
        if interval_seconds > 0:
            self.monitoring_interval = interval_seconds
            self.set_tool_config('monitoring_interval',
                                 int(interval_seconds * 1000))
    
    def set_alert_threshold(
        self,
        interface_name: str,
        threshold_type: str,
        value: float
    ):
        """Set alert threshold for an interface.
        
        Args:
            interface_name: Interface name
            threshold_type: Type of threshold
            value: Threshold value in Mbps
        """
        self.alert_manager.set_threshold(interface_name, threshold_type, value)
    
    def get_current_statistics(
        self,
        interface_name: Optional[str] = None,
        hours: int = 1
    ) -> Dict[str, float]:
        """Get current bandwidth statistics.
        
        Args:
            interface_name: Interface to analyze (None for all)
            hours: Hours of data to analyze
            
        Returns:
            Dictionary with statistical data
        """
        return self.data_manager.get_statistics(interface_name, hours)
    
    def export_data(
        self,
        file_path: str,
        format_type: str = 'csv',
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        interface_name: Optional[str] = None
    ) -> bool:
        """Export bandwidth data to file.
        
        Args:
            file_path: Output file path
            format_type: Export format ('csv' or 'json')
            start_time: Start time filter
            end_time: End time filter
            interface_name: Interface name filter
            
        Returns:
            True if export successful
        """
        path = Path(file_path)
        
        if format_type.lower() == 'csv':
            return self.data_exporter.export_to_csv(
                path, start_time, end_time, interface_name
            )
        elif format_type.lower() == 'json':
            return self.data_exporter.export_to_json(
                path, start_time, end_time, interface_name
            )
        else:
            return False