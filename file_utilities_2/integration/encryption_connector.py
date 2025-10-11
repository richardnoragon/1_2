"""
Hub connector for encryption operations.

This module provides integration between the encryption tool and the main hub,
handling progress reporting, resource coordination, and communication.
"""

import time
from typing import Dict, Any, Optional, Callable
from PyQt5.QtCore import QObject, pyqtSignal

from file_utilities_2.integration.hub_connector import HubConnector


class EncryptionHubConnector(HubConnector):
    """
    Hub connector specifically for encryption operations.
    
    Extends the base HubConnector with encryption-specific functionality
    for progress reporting, resource management, and operation coordination.
    """
    
    # Encryption-specific signals
    encryption_progress = pyqtSignal(str, int, int, str)  # op_id, current, total, msg
    encryption_completed = pyqtSignal(str, dict)  # operation_id, results
    encryption_failed = pyqtSignal(str, str)  # operation_id, error
    encryption_cancelled = pyqtSignal(str, str)  # operation_id, reason
    
    def __init__(self, hub_instance=None):
        """
        Initialize encryption hub connector.
        
        Args:
            hub_instance: Main hub instance for communication
        """
        super().__init__(tool_name="encryption", hub_instance=hub_instance)
        
        # Encryption-specific state
        self.active_operations = {}
        self.operation_counter = 0
        self.resource_usage = {
            'memory_usage': 0,
            'cpu_usage': 0,
            'disk_io': 0,
            'active_files': []
        }
        
        # Performance tracking
        self.performance_metrics = {
            'total_operations': 0,
            'successful_operations': 0,
            'failed_operations': 0,
            'total_bytes_processed': 0,
            'average_speed': 0,
            'session_start_time': time.time()
        }
    
    def register_operation(self, operation_type: str, 
                          parameters: Dict[str, Any]) -> str:
        """
        Register a new encryption operation with the hub.
        
        Args:
            operation_type: Type of operation (encrypt_file, decrypt_file, etc.)
            parameters: Operation parameters
            
        Returns:
            str: Unique operation ID
        """
        self.operation_counter += 1
        operation_id = f"enc_{self.operation_counter}_{int(time.time())}"
        
        operation_info = {
            'id': operation_id,
            'type': operation_type,
            'parameters': self._sanitize_parameters(parameters),
            'start_time': time.time(),
            'status': 'starting',
            'progress': 0,
            'total': 0,
            'message': 'Initializing...'
        }
        
        self.active_operations[operation_id] = operation_info
        
        # Report to hub
        if self.hub_instance:
            self.report_operation_start(operation_id, operation_type, parameters)
        
        # Update metrics
        self.performance_metrics['total_operations'] += 1
        
        return operation_id
    
    def update_operation_progress(self, operation_id: str, current: int, 
                                 total: int, message: str = ""):
        """
        Update progress for an active operation.
        
        Args:
            operation_id: Operation identifier
            current: Current progress value
            total: Total progress value
            message: Progress message
        """
        if operation_id not in self.active_operations:
            return
        
        operation = self.active_operations[operation_id]
        operation['progress'] = current
        operation['total'] = total
        operation['message'] = message
        operation['status'] = 'in_progress'
        
        # Calculate speed and ETA
        elapsed_time = time.time() - operation['start_time']
        if elapsed_time > 0 and current > 0:
            speed = current / elapsed_time
            eta = (total - current) / speed if speed > 0 else 0
            operation['speed'] = speed
            operation['eta'] = eta
        
        # Emit signal
        self.encryption_progress.emit(operation_id, current, total, message)
        
        # Report to hub
        if self.hub_instance:
            self.report_progress(operation_id, current, total, message)
    
    def complete_operation(self, operation_id: str, results: Dict[str, Any]):
        """
        Mark operation as completed.
        
        Args:
            operation_id: Operation identifier
            results: Operation results
        """
        if operation_id not in self.active_operations:
            return
        
        operation = self.active_operations[operation_id]
        operation['status'] = 'completed'
        operation['end_time'] = time.time()
        operation['duration'] = operation['end_time'] - operation['start_time']
        operation['results'] = results
        
        # Update metrics
        self.performance_metrics['successful_operations'] += 1
        if 'bytes_processed' in results:
            self.performance_metrics['total_bytes_processed'] += results['bytes_processed']
        
        # Calculate average speed
        total_time = time.time() - self.performance_metrics['session_start_time']
        if total_time > 0:
            self.performance_metrics['average_speed'] = (
                self.performance_metrics['total_bytes_processed'] / total_time
            )
        
        # Emit signal
        self.encryption_completed.emit(operation_id, results)
        
        # Report to hub
        if self.hub_instance:
            self.report_operation_complete(operation_id, results)
        
        # Clean up
        del self.active_operations[operation_id]
    
    def fail_operation(self, operation_id: str, error: str):
        """
        Mark operation as failed.
        
        Args:
            operation_id: Operation identifier
            error: Error message
        """
        if operation_id not in self.active_operations:
            return
        
        operation = self.active_operations[operation_id]
        operation['status'] = 'failed'
        operation['end_time'] = time.time()
        operation['duration'] = operation['end_time'] - operation['start_time']
        operation['error'] = error
        
        # Update metrics
        self.performance_metrics['failed_operations'] += 1
        
        # Emit signal
        self.encryption_failed.emit(operation_id, error)
        
        # Report to hub
        if self.hub_instance:
            self.report_operation_failed(operation_id, error)
        
        # Clean up
        del self.active_operations[operation_id]
    
    def cancel_operation(self, operation_id: str, reason: str = "User cancelled"):
        """
        Cancel an active operation.
        
        Args:
            operation_id: Operation identifier
            reason: Cancellation reason
        """
        if operation_id not in self.active_operations:
            return
        
        operation = self.active_operations[operation_id]
        operation['status'] = 'cancelled'
        operation['end_time'] = time.time()
        operation['duration'] = operation['end_time'] - operation['start_time']
        operation['cancellation_reason'] = reason
        
        # Emit signal
        self.encryption_cancelled.emit(operation_id, reason)
        
        # Report to hub
        if self.hub_instance:
            self.report_operation_cancelled(operation_id, reason)
        
        # Clean up
        del self.active_operations[operation_id]
    
    def update_resource_usage(self, memory_mb: float = 0, cpu_percent: float = 0,
                             disk_io_mb: float = 0, active_files: list = None):
        """
        Update resource usage information.
        
        Args:
            memory_mb: Memory usage in MB
            cpu_percent: CPU usage percentage
            disk_io_mb: Disk I/O in MB/s
            active_files: List of currently active files
        """
        self.resource_usage.update({
            'memory_usage': memory_mb,
            'cpu_usage': cpu_percent,
            'disk_io': disk_io_mb,
            'active_files': active_files or [],
            'timestamp': time.time()
        })
        
        # Report to hub
        if self.hub_instance:
            self.report_resource_usage(self.resource_usage)
    
    def get_operation_status(self, operation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get status of a specific operation.
        
        Args:
            operation_id: Operation identifier
            
        Returns:
            Operation status dictionary or None if not found
        """
        return self.active_operations.get(operation_id)
    
    def get_all_operations(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all active operations."""
        return self.active_operations.copy()
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        metrics = self.performance_metrics.copy()
        metrics['active_operations_count'] = len(self.active_operations)
        metrics['session_duration'] = time.time() - metrics['session_start_time']
        return metrics
    
    def get_resource_usage(self) -> Dict[str, Any]:
        """Get current resource usage."""
        return self.resource_usage.copy()
    
    def request_resource_allocation(self, resource_type: str, 
                                   amount: float) -> bool:
        """
        Request resource allocation from hub.
        
        Args:
            resource_type: Type of resource (memory, cpu, disk)
            amount: Amount to allocate
            
        Returns:
            bool: True if allocation granted
        """
        if self.hub_instance and hasattr(self.hub_instance, 'allocate_resource'):
            return self.hub_instance.allocate_resource(
                'encryption', resource_type, amount
            )
        return True  # Default to allowing if no hub
    
    def release_resource_allocation(self, resource_type: str, amount: float):
        """
        Release resource allocation back to hub.
        
        Args:
            resource_type: Type of resource
            amount: Amount to release
        """
        if self.hub_instance and hasattr(self.hub_instance, 'release_resource'):
            self.hub_instance.release_resource(
                'encryption', resource_type, amount
            )
    
    def coordinate_with_other_tools(self, message: str, 
                                   data: Dict[str, Any] = None) -> bool:
        """
        Send coordination message to other tools via hub.
        
        Args:
            message: Coordination message
            data: Optional data payload
            
        Returns:
            bool: True if message sent successfully
        """
        if self.hub_instance and hasattr(self.hub_instance, 'broadcast_message'):
            return self.hub_instance.broadcast_message(
                'encryption', message, data or {}
            )
        return False
    
    def handle_hub_message(self, sender: str, message: str, 
                          data: Dict[str, Any]):
        """
        Handle incoming message from hub.
        
        Args:
            sender: Message sender tool name
            message: Message content
            data: Message data
        """
        # Handle coordination messages from other tools
        if message == "resource_constraint":
            self._handle_resource_constraint(data)
        elif message == "priority_operation":
            self._handle_priority_operation(data)
        elif message == "system_shutdown":
            self._handle_system_shutdown(data)
    
    def _handle_resource_constraint(self, data: Dict[str, Any]):
        """Handle resource constraint notification."""
        constraint_type = data.get('type', 'unknown')
        severity = data.get('severity', 'low')
        
        if severity == 'high':
            # Pause non-critical operations
            for op_id, operation in self.active_operations.items():
                if operation.get('priority', 'normal') == 'low':
                    self.update_operation_progress(
                        op_id, operation['progress'], operation['total'],
                        f"Paused due to {constraint_type} constraint"
                    )
    
    def _handle_priority_operation(self, data: Dict[str, Any]):
        """Handle priority operation notification."""
        requesting_tool = data.get('tool', 'unknown')
        priority_level = data.get('priority', 'normal')
        
        if priority_level == 'urgent':
            # Reduce resource usage for current operations
            for op_id, operation in self.active_operations.items():
                self.update_operation_progress(
                    op_id, operation['progress'], operation['total'],
                    f"Reduced priority for {requesting_tool} urgent operation"
                )
    
    def _handle_system_shutdown(self, data: Dict[str, Any]):
        """Handle system shutdown notification."""
        shutdown_timeout = data.get('timeout', 30)  # seconds
        
        # Cancel all non-critical operations
        operations_to_cancel = []
        for op_id, operation in self.active_operations.items():
            if operation.get('priority', 'normal') != 'critical':
                operations_to_cancel.append(op_id)
        
        for op_id in operations_to_cancel:
            self.cancel_operation(op_id, "System shutdown requested")
    
    def _sanitize_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize parameters for logging/reporting."""
        sanitized = {}
        sensitive_keys = ['key', 'password', 'secret']
        
        for key, value in parameters.items():
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                sanitized[key] = "[REDACTED]"
            elif isinstance(value, (str, int, float, bool)):
                sanitized[key] = value
            else:
                sanitized[key] = str(type(value))
        
        return sanitized
    
    def cleanup(self):
        """Clean up connector resources."""
        # Cancel all active operations
        for op_id in list(self.active_operations.keys()):
            self.cancel_operation(op_id, "Connector cleanup")
        
        # Call parent cleanup
        super().cleanup()