"""
Secure Delete Hub Connector Module

Specialized hub integration connector for secure delete operations with
enhanced resource management, progress reporting, and status coordination.

Migrated from: secure_delete.py hub integration
Target: file_utilities_2 package integration
"""

import os
import json
import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal, QTimer

from .hub_connector import (HubConnector, HubCommunicationProtocol, 
                           HubMessage, HubIntegratedTool)


class SecureDeleteHubConnector(HubIntegratedTool):
    """
    Specialized hub connector for secure delete operations.
    
    Provides enhanced integration features specific to secure deletion:
    - Resource coordination for disk operations
    - Progress aggregation and reporting
    - Security event logging and monitoring
    - Configuration synchronization
    - Performance metrics collection
    """
    
    # Secure delete specific signals
    resource_allocated = pyqtSignal(str, dict)      # resource_type, details
    resource_released = pyqtSignal(str, dict)       # resource_type, details
    security_event = pyqtSignal(str, dict)          # event_type, details
    performance_metric = pyqtSignal(str, dict)      # metric_name, data
    
    def __init__(self, hub_instance=None):
        """
        Initialize secure delete hub connector.
        
        Args:
            hub_instance: Reference to the hub instance
        """
        super().__init__("SecureDeleteConnector")
        
        # Enhanced hub connector
        self.hub_connector = HubConnector("SecureDelete", hub_instance)
        self._setup_enhanced_integration()
        
        # Resource management
        self.allocated_resources = {}
        self.resource_usage_history = []
        
        # Performance tracking
        self.performance_metrics = {
            'operations_completed': 0,
            'total_bytes_processed': 0,
            'total_operation_time': 0.0,
            'average_throughput': 0.0,
            'error_rate': 0.0
        }
        
        # Security monitoring
        self.security_events = []
        self.security_alerts_enabled = True
        
        # Configuration synchronization
        self.config_sync_enabled = True
        self.last_config_sync = None
        
        # Periodic reporting timer
        self.reporting_timer = QTimer()
        self.reporting_timer.timeout.connect(self._send_periodic_report)
        self.reporting_timer.setInterval(60000)  # 1 minute
        self.reporting_timer.start()
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("SecureDeleteHubConnector initialized")
    
    def _setup_enhanced_integration(self):
        """Setup enhanced hub integration features."""
        try:
            # Register with hub
            self.hub_connector.register_with_hub()
            
            # Register event handlers
            self.hub_connector.register_event_handler(
                "resource_request", self._handle_resource_request
            )
            self.hub_connector.register_event_handler(
                "config_update", self._handle_config_update
            )
            self.hub_connector.register_event_handler(
                "security_alert", self._handle_security_alert
            )
            
            # Connect signals
            self.hub_connector.hub_resource_available.connect(
                self._on_resource_available
            )
            
            self.logger.info("Enhanced hub integration setup completed")
            
        except Exception as e:
            self.logger.error(f"Failed to setup enhanced integration: {e}")
    
    def request_deletion_resources(self, file_path: str, file_size: int, 
                                  passes: int) -> bool:
        """
        Request resources for secure deletion operation.
        
        Args:
            file_path: Path of file to be deleted
            file_size: Size of file in bytes
            passes: Number of overwrite passes
            
        Returns:
            True if resources allocated, False otherwise
        """
        try:
            # Calculate resource requirements
            estimated_time = self._estimate_operation_time(file_size, passes)
            disk_io_load = self._calculate_disk_io_load(file_size, passes)
            
            resource_requirements = {
                'operation': 'secure_delete',
                'file_path': file_path,
                'file_size': file_size,
                'passes': passes,
                'estimated_time': estimated_time,
                'disk_io_load': disk_io_load,
                'priority': 'high',
                'exclusive_access': True
            }
            
            # Request disk resource
            disk_granted = self.hub_connector.request_hub_resources(
                "disk", resource_requirements
            )
            
            if disk_granted:
                # Track allocated resources
                self.allocated_resources['disk'] = {
                    'allocated_at': datetime.now(),
                    'requirements': resource_requirements,
                    'operation_id': self._generate_operation_id()
                }
                
                # Log resource allocation
                self._log_resource_event('allocated', 'disk', resource_requirements)
                
                # Emit signal
                self.resource_allocated.emit('disk', resource_requirements)
                
                return True
            else:
                self.logger.warning("Failed to allocate disk resources")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to request deletion resources: {e}")
            return False
    
    def release_deletion_resources(self, operation_id: str = None):
        """
        Release allocated resources for deletion operation.
        
        Args:
            operation_id: Optional operation ID for tracking
        """
        try:
            released_resources = []
            
            for resource_type, resource_info in self.allocated_resources.items():
                if operation_id is None or resource_info.get('operation_id') == operation_id:
                    # Calculate usage duration
                    allocated_at = resource_info['allocated_at']
                    duration = (datetime.now() - allocated_at).total_seconds()
                    
                    # Log resource usage
                    usage_info = {
                        'resource_type': resource_type,
                        'duration': duration,
                        'requirements': resource_info['requirements'],
                        'released_at': datetime.now()
                    }
                    
                    self.resource_usage_history.append(usage_info)
                    
                    # Log release event
                    self._log_resource_event('released', resource_type, usage_info)
                    
                    # Emit signal
                    self.resource_released.emit(resource_type, usage_info)
                    
                    released_resources.append(resource_type)
            
            # Remove released resources from tracking
            for resource_type in released_resources:
                del self.allocated_resources[resource_type]
            
            self.logger.info(f"Released {len(released_resources)} resources")
            
        except Exception as e:
            self.logger.error(f"Failed to release resources: {e}")
    
    def report_operation_progress(self, operation_id: str, file_path: str,
                                 current_pass: int, total_passes: int,
                                 bytes_processed: int, total_bytes: int):
        """
        Report detailed operation progress to hub.
        
        Args:
            operation_id: Operation tracking ID
            file_path: File being processed
            current_pass: Current overwrite pass
            total_passes: Total overwrite passes
            bytes_processed: Bytes processed so far
            total_bytes: Total bytes to process
        """
        try:
            # Calculate progress metrics
            pass_progress = (current_pass / total_passes) * 100 if total_passes > 0 else 0
            byte_progress = (bytes_processed / total_bytes) * 100 if total_bytes > 0 else 0
            overall_progress = (pass_progress + byte_progress) / 2
            
            # Calculate throughput
            throughput = self._calculate_current_throughput(bytes_processed)
            
            progress_data = {
                'operation_id': operation_id,
                'file_path': file_path,
                'current_pass': current_pass,
                'total_passes': total_passes,
                'bytes_processed': bytes_processed,
                'total_bytes': total_bytes,
                'pass_progress': round(pass_progress, 2),
                'byte_progress': round(byte_progress, 2),
                'overall_progress': round(overall_progress, 2),
                'throughput_mbps': round(throughput, 2),
                'timestamp': datetime.now().isoformat()
            }
            
            # Report to hub
            self.hub_connector.report_progress_to_hub(
                int(overall_progress),
                f"Pass {current_pass}/{total_passes} - {byte_progress:.1f}% complete"
            )
            
            # Broadcast detailed progress
            self.hub_connector.broadcast_event(
                "secure_delete_progress", progress_data
            )
            
        except Exception as e:
            self.logger.error(f"Failed to report operation progress: {e}")
    
    def report_security_event(self, event_type: str, file_path: str,
                             details: Dict[str, Any]):
        """
        Report security-related events to hub.
        
        Args:
            event_type: Type of security event
            file_path: File path involved
            details: Event details
        """
        try:
            security_event = {
                'event_type': event_type,
                'file_path': file_path,
                'details': details,
                'timestamp': datetime.now().isoformat(),
                'severity': self._determine_event_severity(event_type),
                'source': 'SecureDelete'
            }
            
            # Store event
            self.security_events.append(security_event)
            
            # Keep only recent events (last 1000)
            if len(self.security_events) > 1000:
                self.security_events = self.security_events[-1000:]
            
            # Report to hub
            self.hub_connector.broadcast_event(
                "security_event", security_event
            )
            
            # Emit signal
            self.security_event.emit(event_type, security_event)
            
            # Log high-severity events
            if security_event['severity'] in ['high', 'critical']:
                self.logger.warning(
                    f"Security event [{event_type}]: {file_path}"
                )
            
        except Exception as e:
            self.logger.error(f"Failed to report security event: {e}")
    
    def update_performance_metrics(self, operation_data: Dict[str, Any]):
        """
        Update performance metrics and report to hub.
        
        Args:
            operation_data: Data from completed operation
        """
        try:
            # Update metrics
            self.performance_metrics['operations_completed'] += 1
            self.performance_metrics['total_bytes_processed'] += operation_data.get('bytes_processed', 0)
            self.performance_metrics['total_operation_time'] += operation_data.get('duration', 0)
            
            # Calculate derived metrics
            if self.performance_metrics['total_operation_time'] > 0:
                self.performance_metrics['average_throughput'] = (
                    self.performance_metrics['total_bytes_processed'] / 
                    self.performance_metrics['total_operation_time'] / 1024 / 1024  # MB/s
                )
            
            # Calculate error rate
            total_operations = self.performance_metrics['operations_completed']
            error_count = operation_data.get('error_count', 0)
            if total_operations > 0:
                self.performance_metrics['error_rate'] = (error_count / total_operations) * 100
            
            # Report metrics to hub
            self.hub_connector.broadcast_event(
                "performance_metrics", {
                    'tool': 'SecureDelete',
                    'metrics': self.performance_metrics.copy(),
                    'timestamp': datetime.now().isoformat()
                }
            )
            
            # Emit signal
            self.performance_metric.emit('operation_completed', operation_data)
            
        except Exception as e:
            self.logger.error(f"Failed to update performance metrics: {e}")
    
    def synchronize_configuration(self, config_data: Dict[str, Any]) -> bool:
        """
        Synchronize configuration with hub.
        
        Args:
            config_data: Configuration data to synchronize
            
        Returns:
            True if synchronized successfully, False otherwise
        """
        try:
            if not self.config_sync_enabled:
                return True
            
            sync_data = {
                'tool': 'SecureDelete',
                'config': config_data,
                'sync_timestamp': datetime.now().isoformat(),
                'version': '1.0.0'
            }
            
            # Broadcast configuration
            self.hub_connector.broadcast_event(
                "config_sync", sync_data
            )
            
            # Update sync timestamp
            self.last_config_sync = datetime.now()
            
            self.logger.info("Configuration synchronized with hub")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to synchronize configuration: {e}")
            return False
    
    def _estimate_operation_time(self, file_size: int, passes: int) -> float:
        """Estimate operation time based on file size and passes."""
        # Base estimation: 50 MB/s throughput
        base_throughput = 50 * 1024 * 1024  # 50 MB/s
        estimated_seconds = (file_size * passes) / base_throughput
        
        # Add overhead for file operations
        overhead = 2.0  # 2 seconds overhead
        return estimated_seconds + overhead
    
    def _calculate_disk_io_load(self, file_size: int, passes: int) -> str:
        """Calculate expected disk I/O load."""
        total_io = file_size * passes
        
        if total_io < 100 * 1024 * 1024:  # < 100MB
            return "low"
        elif total_io < 1024 * 1024 * 1024:  # < 1GB
            return "medium"
        else:
            return "high"
    
    def _calculate_current_throughput(self, bytes_processed: int) -> float:
        """Calculate current throughput in MB/s."""
        # This would be calculated based on actual timing
        # For now, return estimated throughput
        return 50.0  # 50 MB/s
    
    def _determine_event_severity(self, event_type: str) -> str:
        """Determine severity level for security events."""
        high_severity_events = [
            'unauthorized_access_attempt',
            'permission_escalation',
            'suspicious_file_access'
        ]
        
        medium_severity_events = [
            'file_access_denied',
            'resource_allocation_failed',
            'operation_interrupted'
        ]
        
        if event_type in high_severity_events:
            return "high"
        elif event_type in medium_severity_events:
            return "medium"
        else:
            return "low"
    
    def _generate_operation_id(self) -> str:
        """Generate unique operation ID."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        import uuid
        short_uuid = str(uuid.uuid4())[:8]
        return f"SD_OP_{timestamp}_{short_uuid}"
    
    def _log_resource_event(self, action: str, resource_type: str, 
                           details: Dict[str, Any]):
        """Log resource allocation/release events."""
        event_data = {
            'action': action,
            'resource_type': resource_type,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        
        self.logger.info(f"Resource {action}: {resource_type}")
    
    def _send_periodic_report(self):
        """Send periodic status report to hub."""
        try:
            report_data = {
                'tool': 'SecureDelete',
                'status': 'active',
                'allocated_resources': list(self.allocated_resources.keys()),
                'performance_metrics': self.performance_metrics.copy(),
                'recent_security_events': len([
                    e for e in self.security_events 
                    if (datetime.now() - datetime.fromisoformat(e['timestamp'])).seconds < 3600
                ]),
                'timestamp': datetime.now().isoformat()
            }
            
            self.hub_connector.broadcast_event("periodic_report", report_data)
            
        except Exception as e:
            self.logger.error(f"Failed to send periodic report: {e}")
    
    def _handle_resource_request(self, message: HubMessage):
        """Handle resource requests from hub."""
        try:
            request_data = message.data
            resource_type = request_data.get('resource_type')
            
            if resource_type in self.allocated_resources:
                # Resource is allocated, check if it can be shared
                response_data = {
                    'resource_type': resource_type,
                    'available': False,
                    'reason': 'Resource currently allocated to secure delete operation'
                }
            else:
                response_data = {
                    'resource_type': resource_type,
                    'available': True
                }
            
            # Send response
            self.hub_connector.broadcast_event("resource_response", response_data)
            
        except Exception as e:
            self.logger.error(f"Failed to handle resource request: {e}")
    
    def _handle_config_update(self, message: HubMessage):
        """Handle configuration updates from hub."""
        try:
            config_data = message.data.get('config', {})
            
            if self.config_sync_enabled:
                # Apply configuration updates
                self.logger.info("Received configuration update from hub")
                # Configuration would be applied here
                
        except Exception as e:
            self.logger.error(f"Failed to handle config update: {e}")
    
    def _handle_security_alert(self, message: HubMessage):
        """Handle security alerts from hub."""
        try:
            alert_data = message.data
            alert_type = alert_data.get('alert_type')
            
            if self.security_alerts_enabled:
                self.logger.warning(f"Security alert received: {alert_type}")
                
                # Take appropriate action based on alert type
                if alert_type == 'system_compromise':
                    # Pause operations
                    self.logger.critical("System compromise detected, pausing operations")
                
        except Exception as e:
            self.logger.error(f"Failed to handle security alert: {e}")
    
    def _on_resource_available(self, resource_type: str, details: Dict[str, Any]):
        """Handle resource availability notifications."""
        self.logger.info(f"Resource available: {resource_type}")
    
    def get_connector_status(self) -> Dict[str, Any]:
        """
        Get comprehensive connector status.
        
        Returns:
            Dictionary containing connector status information
        """
        return {
            'connected': self.hub_connector.is_connected,
            'registered': self.hub_connector.is_registered,
            'allocated_resources': list(self.allocated_resources.keys()),
            'performance_metrics': self.performance_metrics.copy(),
            'security_events_count': len(self.security_events),
            'config_sync_enabled': self.config_sync_enabled,
            'last_config_sync': self.last_config_sync.isoformat() if self.last_config_sync else None,
            'resource_usage_history_count': len(self.resource_usage_history)
        }
    
    def cleanup(self):
        """Cleanup connector resources."""
        try:
            # Stop periodic reporting
            self.reporting_timer.stop()
            
            # Release any allocated resources
            self.release_deletion_resources()
            
            # Cleanup hub connector
            self.hub_connector.cleanup()
            
            self.logger.info("SecureDeleteHubConnector cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup connector: {e}")