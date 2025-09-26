"""Main filesystem integrity monitoring class."""

import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from enum import Enum

from ...core.monitor_base import MonitorBase, AlertLevel
from ...core.data_collector import get_data_collector, DataType
from ...core.platform_detector import get_platform_detector
from core.error_handler import error_handler

from .scanner_engine import ScannerEngine
from .corruption_detector import CorruptionDetector
from .repair_advisor import RepairAdvisor


class IntegrityStatus(Enum):
    """Filesystem integrity status levels."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CORRUPTED = "corrupted"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class ScanType(Enum):
    """Types of filesystem scans."""
    QUICK = "quick"
    FULL = "full"
    DEEP = "deep"
    CUSTOM = "custom"


class IntegrityMonitor(MonitorBase):
    """Main filesystem integrity monitoring class.
    
    Provides comprehensive filesystem integrity checking with:
    - Automated scanning with configurable intervals
    - Corruption detection and analysis
    - Repair recommendations
    - Cross-platform filesystem support
    - Real-time monitoring and alerting
    """
    
    def __init__(self, update_interval: float = 3600.0):  # Default 1 hour
        """Initialize the integrity monitor.
        
        Args:
            update_interval: Update interval in seconds (default 1 hour)
        """
        super().__init__("FilesystemIntegrity", update_interval)
        
        # Initialize components
        self.scanner_engine = ScannerEngine()
        self.corruption_detector = CorruptionDetector()
        self.repair_advisor = RepairAdvisor()
        
        # Data collector integration
        self.data_collector = get_data_collector()
        
        # Scan configuration
        self.scan_config = {
            'scan_type': ScanType.QUICK,
            'scan_paths': [],
            'max_scan_depth': 10,
            'file_filters': ['*'],
            'exclude_patterns': [
                '*.tmp', '*.temp', '*.log', 
                'System Volume Information',
                '$RECYCLE.BIN', '.Trash*'
            ],
            'check_checksums': True,
            'check_permissions': True,
            'check_timestamps': True,
            'parallel_scans': True,
            'max_workers': 4
        }
        
        # Scan state
        self._current_scan: Optional[Dict[str, Any]] = None
        self._scan_history: List[Dict[str, Any]] = []
        self._max_scan_history = 100
        self._scan_lock = threading.Lock()
        
        # Scheduled scans
        self._scheduled_scans: List[Dict[str, Any]] = []
        self._next_scheduled_scan: Optional[datetime] = None
        
        # Alert thresholds
        self.alert_thresholds = {
            'corruption_count': 5,
            'critical_errors': 1,
            'scan_failure_rate': 0.2,
            'scan_duration_minutes': 60
        }
        
        # Performance metrics
        self._scan_metrics = {
            'total_scans': 0,
            'successful_scans': 0,
            'failed_scans': 0,
            'files_scanned': 0,
            'corruptions_found': 0,
            'repairs_suggested': 0,
            'average_scan_time': 0.0
        }
        
        self.logger.info("Filesystem integrity monitor initialized")
    
    def _collect_data(self) -> Dict[str, Any]:
        """Collect filesystem integrity data.
        
        Returns:
            Dict containing integrity monitoring data
        """
        try:
            # Check if it's time for a scheduled scan
            if self._should_run_scheduled_scan():
                self._run_scheduled_scan()
            
            # Get current integrity status
            integrity_status = self._get_current_integrity_status()
            
            # Get scan progress if running
            scan_progress = self._get_scan_progress()
            
            # Get recent scan results
            recent_scans = self._get_recent_scan_results()
            
            # Get filesystem information
            filesystem_info = self._get_filesystem_info()
            
            # Compile data
            data = {
                'integrity_status': integrity_status,
                'scan_progress': scan_progress,
                'recent_scans': recent_scans,
                'filesystem_info': filesystem_info,
                'scan_metrics': self._scan_metrics.copy(),
                'scheduled_scans': len(self._scheduled_scans),
                'next_scan': (
                    self._next_scheduled_scan.isoformat() 
                    if self._next_scheduled_scan else None
                ),
                'alert_thresholds': self.alert_thresholds.copy(),
                'scan_config': self.scan_config.copy()
            }
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error collecting integrity data: {e}")
            error_handler.handle_error(e, "IntegrityMonitor._collect_data")
            return {
                'error': str(e),
                'integrity_status': IntegrityStatus.UNKNOWN.value,
                'scan_progress': None
            }
    
    def _validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate collected integrity data.
        
        Args:
            data: Data to validate
            
        Returns:
            bool: True if data is valid, False otherwise
        """
        required_fields = ['integrity_status', 'scan_metrics']
        
        for field in required_fields:
            if field not in data:
                self.logger.warning(f"Missing required field: {field}")
                return False
        
        # Validate integrity status
        valid_statuses = [status.value for status in IntegrityStatus]
        if data['integrity_status'] not in valid_statuses:
            self.logger.warning(
                f"Invalid integrity status: {data['integrity_status']}"
            )
            return False
        
        return True
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get the current filesystem health status.
        
        Returns:
            Dict containing health status information
        """
        current_data = self.get_current_data()
        
        if not current_data:
            return {
                'status': IntegrityStatus.UNKNOWN.value,
                'message': 'No data available',
                'details': {}
            }
        
        integrity_status = current_data.get(
            'integrity_status', IntegrityStatus.UNKNOWN.value
        )
        scan_metrics = current_data.get('scan_metrics', {})
        
        # Determine overall health
        if integrity_status == IntegrityStatus.CRITICAL.value:
            status = 'critical'
            message = 'Critical filesystem corruption detected'
        elif integrity_status == IntegrityStatus.CORRUPTED.value:
            status = 'warning'
            message = 'Filesystem corruption detected'
        elif integrity_status == IntegrityStatus.WARNING.value:
            status = 'warning'
            message = 'Potential filesystem issues detected'
        elif integrity_status == IntegrityStatus.HEALTHY.value:
            status = 'healthy'
            message = 'Filesystem integrity is good'
        else:
            status = 'unknown'
            message = 'Filesystem integrity status unknown'
        
        return {
            'status': status,
            'message': message,
            'details': {
                'integrity_status': integrity_status,
                'total_scans': scan_metrics.get('total_scans', 0),
                'corruptions_found': scan_metrics.get('corruptions_found', 0),
                'last_scan': (
                    current_data.get('recent_scans', [{}])[0].get('timestamp')
                    if current_data.get('recent_scans') else None
                )
            }
        }
    
    def start_scan(
        self,
        scan_type: ScanType = ScanType.QUICK,
        paths: Optional[List[str]] = None,
        config_override: Optional[Dict[str, Any]] = None,
        callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> bool:
        """Start a filesystem integrity scan.
        
        Args:
            scan_type: Type of scan to perform
            paths: Specific paths to scan (None for default)
            config_override: Override scan configuration
            callback: Progress callback function
            
        Returns:
            bool: True if scan started successfully, False otherwise
        """
        try:
            with self._scan_lock:
                current_status = (
                    self._current_scan.get('status') if self._current_scan else None
                )
                if self._current_scan and current_status == 'running':
                    self.logger.warning("Scan already in progress")
                    return False
                
                # Prepare scan configuration
                scan_config = self.scan_config.copy()
                if config_override:
                    scan_config.update(config_override)
                
                scan_config['scan_type'] = scan_type
                if paths:
                    scan_config['scan_paths'] = paths
                
                # Initialize scan
                scan_id = f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                self._current_scan = {
                    'scan_id': scan_id,
                    'scan_type': scan_type.value,
                    'status': 'starting',
                    'start_time': datetime.now(),
                    'progress': 0.0,
                    'files_scanned': 0,
                    'errors_found': 0,
                    'config': scan_config,
                    'callback': callback
                }
                
                # Start scan in background thread
                scan_thread = threading.Thread(
                    target=self._run_scan,
                    args=(scan_id, scan_config),
                    name=f"FilesystemScan_{scan_id}",
                    daemon=True
                )
                scan_thread.start()
                
                self.logger.info(f"Started filesystem scan: {scan_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Error starting scan: {e}")
            error_handler.handle_error(e, "IntegrityMonitor.start_scan")
            return False
    
    def stop_scan(self) -> bool:
        """Stop the current scan.
        
        Returns:
            bool: True if scan stopped successfully, False otherwise
        """
        try:
            with self._scan_lock:
                current_status = (
                    self._current_scan.get('status') if self._current_scan else None
                )
                if not self._current_scan or current_status != 'running':
                    self.logger.warning("No scan currently running")
                    return False
                
                # Signal scan to stop
                self._current_scan['status'] = 'stopping'
                self.scanner_engine.stop_scan()
                
                self.logger.info("Stopping filesystem scan")
                return True
                
        except Exception as e:
            self.logger.error(f"Error stopping scan: {e}")
            error_handler.handle_error(e, "IntegrityMonitor.stop_scan")
            return False
    
    def get_scan_status(self) -> Optional[Dict[str, Any]]:
        """Get the current scan status.
        
        Returns:
            Dict containing scan status or None if no scan
        """
        with self._scan_lock:
            if self._current_scan:
                return self._current_scan.copy()
            return None
    
    def schedule_scan(
        self,
        scan_type: ScanType,
        schedule_time: datetime,
        paths: Optional[List[str]] = None,
        config_override: Optional[Dict[str, Any]] = None,
        recurring: bool = False,
        interval: Optional[timedelta] = None
    ) -> str:
        """Schedule a filesystem scan.
        
        Args:
            scan_type: Type of scan to schedule
            schedule_time: When to run the scan
            paths: Specific paths to scan
            config_override: Override scan configuration
            recurring: Whether scan should repeat
            interval: Interval for recurring scans
            
        Returns:
            str: Schedule ID
        """
        schedule_id = f"schedule_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        scheduled_scan = {
            'schedule_id': schedule_id,
            'scan_type': scan_type,
            'schedule_time': schedule_time,
            'paths': paths,
            'config_override': config_override,
            'recurring': recurring,
            'interval': interval,
            'created': datetime.now(),
            'last_run': None,
            'run_count': 0
        }
        
        self._scheduled_scans.append(scheduled_scan)
        self._update_next_scheduled_scan()
        
        self.logger.info(f"Scheduled scan: {schedule_id} for {schedule_time}")
        return schedule_id
    
    def _run_scan(self, scan_id: str, config: Dict[str, Any]) -> None:
        """Run a filesystem scan.
        
        Args:
            scan_id: Unique scan identifier
            config: Scan configuration
        """
        try:
            with self._scan_lock:
                if (self._current_scan and
                        self._current_scan['scan_id'] == scan_id):
                    self._current_scan['status'] = 'running'
                    callback = self._current_scan.get('callback')
            
            start_time = datetime.now()
            
            # Progress callback
            def progress_callback(progress_data: Dict[str, Any]) -> None:
                with self._scan_lock:
                    if self._current_scan and self._current_scan['scan_id'] == scan_id:
                        self._current_scan.update(progress_data)
                        if callback:
                            callback(progress_data)
            
            # Run the scan
            scan_result = self.scanner_engine.run_scan(
                config=config,
                progress_callback=progress_callback
            )
            
            # Analyze results for corruption
            corruption_analysis = self.corruption_detector.analyze_scan_results(
                scan_result
            )
            
            # Get repair recommendations
            repair_recommendations = self.repair_advisor.analyze_issues(
                scan_result, corruption_analysis
            )
            
            # Finalize scan
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            final_result = {
                'scan_id': scan_id,
                'status': 'completed',
                'start_time': start_time,
                'end_time': end_time,
                'duration_seconds': duration,
                'scan_result': scan_result,
                'corruption_analysis': corruption_analysis,
                'repair_recommendations': repair_recommendations,
                'config': config
            }
            
            # Update scan history
            with self._scan_lock:
                self._scan_history.append(final_result)
                if len(self._scan_history) > self._max_scan_history:
                    self._scan_history = self._scan_history[-self._max_scan_history:]
                
                # Update metrics
                self._scan_metrics['total_scans'] += 1
                self._scan_metrics['successful_scans'] += 1
                self._scan_metrics['files_scanned'] += scan_result.get(
                    'files_scanned', 0
                )
                corruptions = corruption_analysis.get('corruptions', [])
                self._scan_metrics['corruptions_found'] += len(corruptions)
                recommendations = repair_recommendations.get('recommendations', [])
                self._scan_metrics['repairs_suggested'] += len(recommendations)
                
                # Update average scan time
                prev_avg = self._scan_metrics['average_scan_time']
                prev_count = self._scan_metrics['successful_scans'] - 1
                total_time = (prev_avg * prev_count) + duration
                self._scan_metrics['average_scan_time'] = (
                    total_time / self._scan_metrics['successful_scans']
                )
                
                # Clear current scan
                self._current_scan = None
            
            # Check for alerts
            self._check_scan_alerts(final_result)
            
            # Store data
            self.data_collector.add_data_point(
                DataType.FILESYSTEM,
                self.monitor_name,
                final_result
            )
            
            self.logger.info(f"Completed filesystem scan: {scan_id}")
            
        except Exception as e:
            self.logger.error(f"Error running scan {scan_id}: {e}")
            error_handler.handle_error(
                e, f"IntegrityMonitor._run_scan({scan_id})"
            )
            
            # Update failed scan metrics
            with self._scan_lock:
                self._scan_metrics['total_scans'] += 1
                self._scan_metrics['failed_scans'] += 1
                
                if self._current_scan and self._current_scan['scan_id'] == scan_id:
                    self._current_scan['status'] = 'failed'
                    self._current_scan['error'] = str(e)
    
    def _should_run_scheduled_scan(self) -> bool:
        """Check if a scheduled scan should run.
        
        Returns:
            bool: True if a scan should run now
        """
        if not self._next_scheduled_scan:
            return False
            
        return datetime.now() >= self._next_scheduled_scan
    
    def _run_scheduled_scan(self) -> None:
        """Run the next scheduled scan."""
        try:
            # Find the next scan to run
            now = datetime.now()
            for scheduled_scan in self._scheduled_scans:
                if scheduled_scan['schedule_time'] <= now:
                    # Run this scan
                    self.start_scan(
                        scan_type=scheduled_scan['scan_type'],
                        paths=scheduled_scan['paths'],
                        config_override=scheduled_scan['config_override']
                    )
                    
                    # Update schedule
                    scheduled_scan['last_run'] = now
                    scheduled_scan['run_count'] += 1
                    
                    # Handle recurring scans
                    if scheduled_scan['recurring'] and scheduled_scan['interval']:
                        scheduled_scan['schedule_time'] = now + scheduled_scan['interval']
                    else:
                        # Remove one-time scan
                        self._scheduled_scans.remove(scheduled_scan)
                    
                    break
            
            self._update_next_scheduled_scan()
            
        except Exception as e:
            self.logger.error(f"Error running scheduled scan: {e}")
            error_handler.handle_error(e, "IntegrityMonitor._run_scheduled_scan")
    
    def _update_next_scheduled_scan(self) -> None:
        """Update the next scheduled scan time."""
        if not self._scheduled_scans:
            self._next_scheduled_scan = None
            return
        
        next_times = [scan['schedule_time'] for scan in self._scheduled_scans]
        self._next_scheduled_scan = min(next_times)
    
    def _get_current_integrity_status(self) -> str:
        """Get the current integrity status.
        
        Returns:
            str: Current integrity status
        """
        # Check recent scan results
        if not self._scan_history:
            return IntegrityStatus.UNKNOWN.value
        
        recent_scan = self._scan_history[-1]
        corruption_analysis = recent_scan.get('corruption_analysis', {})
        corruptions = corruption_analysis.get('corruptions', [])
        
        if not corruptions:
            return IntegrityStatus.HEALTHY.value
        
        # Categorize by severity
        critical_count = sum(1 for c in corruptions if c.get('severity') == 'critical')
        high_count = sum(1 for c in corruptions if c.get('severity') == 'high')
        
        if critical_count > 0:
            return IntegrityStatus.CRITICAL.value
        elif high_count > 0:
            return IntegrityStatus.CORRUPTED.value
        elif len(corruptions) > 0:
            return IntegrityStatus.WARNING.value
        else:
            return IntegrityStatus.HEALTHY.value
    
    def _get_scan_progress(self) -> Optional[Dict[str, Any]]:
        """Get current scan progress.
        
        Returns:
            Dict containing scan progress or None
        """
        with self._scan_lock:
            if self._current_scan:
                return {
                    'scan_id': self._current_scan['scan_id'],
                    'status': self._current_scan['status'],
                    'progress': self._current_scan.get('progress', 0.0),
                    'files_scanned': self._current_scan.get('files_scanned', 0),
                    'errors_found': self._current_scan.get('errors_found', 0),
                    'current_path': self._current_scan.get('current_path', ''),
                    'elapsed_time': (
                        datetime.now() - self._current_scan['start_time']
                    ).total_seconds()
                }
            return None
    
    def _get_recent_scan_results(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent scan results.
        
        Args:
            limit: Maximum number of results to return
            
        Returns:
            List of recent scan results
        """
        with self._scan_lock:
            return self._scan_history[-limit:] if self._scan_history else []
    
    def _get_filesystem_info(self) -> Dict[str, Any]:
        """Get filesystem information.
        
        Returns:
            Dict containing filesystem details
        """
        try:
            # Get platform-specific filesystem info
            platform_detector = get_platform_detector()
            
            filesystem_info = {
                'platform': platform_detector.platform.value,
                'filesystems': []
            }
            
            # This would be expanded with platform-specific implementations
            # For now, return basic info
            return filesystem_info
            
        except Exception as e:
            self.logger.error(f"Error getting filesystem info: {e}")
            return {'error': str(e)}
    
    def _check_scan_alerts(self, scan_result: Dict[str, Any]) -> None:
        """Check scan results for alert conditions.
        
        Args:
            scan_result: Completed scan result
        """
        try:
            corruption_analysis = scan_result.get('corruption_analysis', {})
            corruptions = corruption_analysis.get('corruptions', [])
            
            # Check corruption count threshold
            if len(corruptions) >= self.alert_thresholds['corruption_count']:
                self._notify_alert_callbacks(
                    'corruption_threshold',
                    AlertLevel.WARNING,
                    f"Found {len(corruptions)} corruptions (threshold: {self.alert_thresholds['corruption_count']})"
                )
            
            # Check for critical errors
            critical_corruptions = [c for c in corruptions if c.get('severity') == 'critical']
            if len(critical_corruptions) >= self.alert_thresholds['critical_errors']:
                self._notify_alert_callbacks(
                    'critical_corruption',
                    AlertLevel.CRITICAL,
                    f"Found {len(critical_corruptions)} critical filesystem corruptions"
                )
            
            # Check scan duration
            duration_minutes = scan_result.get('duration_seconds', 0) / 60
            if duration_minutes > self.alert_thresholds['scan_duration_minutes']:
                self._notify_alert_callbacks(
                    'long_scan_duration',
                    AlertLevel.INFO,
                    f"Scan took {duration_minutes:.1f} minutes (threshold: {self.alert_thresholds['scan_duration_minutes']})"
                )
            
        except Exception as e:
            self.logger.error(f"Error checking scan alerts: {e}")
            error_handler.handle_error(e, "IntegrityMonitor._check_scan_alerts")
    
    def update_scan_config(self, config_updates: Dict[str, Any]) -> None:
        """Update scan configuration.
        
        Args:
            config_updates: Configuration updates to apply
        """
        self.scan_config.update(config_updates)
        self.logger.info("Updated scan configuration")
    
    def update_alert_thresholds(self, threshold_updates: Dict[str, Any]) -> None:
        """Update alert thresholds.
        
        Args:
            threshold_updates: Threshold updates to apply
        """
        self.alert_thresholds.update(threshold_updates)
        self.logger.info("Updated alert thresholds")
    
    def get_scan_metrics(self) -> Dict[str, Any]:
        """Get scan performance metrics.
        
        Returns:
            Dict containing scan metrics
        """
        return self._scan_metrics.copy()
    
    def get_scheduled_scans(self) -> List[Dict[str, Any]]:
        """Get list of scheduled scans.
        
        Returns:
            List of scheduled scan information
        """
        return [
            {
                'schedule_id': scan['schedule_id'],
                'scan_type': scan['scan_type'].value,
                'schedule_time': scan['schedule_time'].isoformat(),
                'recurring': scan['recurring'],
                'interval': str(scan['interval']) if scan['interval'] else None,
                'run_count': scan['run_count'],
                'last_run': scan['last_run'].isoformat() if scan['last_run'] else None
            }
            for scan in self._scheduled_scans
        ]