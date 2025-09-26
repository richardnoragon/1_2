"""
Logging and audit trail system for encryption operations.

This module provides comprehensive logging, audit trails, and security
monitoring for all encryption/decryption operations with hub integration.
"""

import os
import json
import time
import logging
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, List
from enum import Enum


class LogLevel(Enum):
    """Log level enumeration."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    AUDIT = "AUDIT"


class SecurityEvent(Enum):
    """Security event types for audit logging."""
    KEY_GENERATED = "key_generated"
    KEY_LOADED = "key_loaded"
    KEY_SAVED = "key_saved"
    FILE_ENCRYPTED = "file_encrypted"
    FILE_DECRYPTED = "file_decrypted"
    OPERATION_STARTED = "operation_started"
    OPERATION_COMPLETED = "operation_completed"
    OPERATION_FAILED = "operation_failed"
    OPERATION_CANCELLED = "operation_cancelled"
    CONFIG_CHANGED = "config_changed"
    SECURITY_VIOLATION = "security_violation"


class EncryptionLogger:
    """
    Comprehensive logging and audit system for encryption operations.
    
    Provides structured logging, audit trails, security monitoring,
    and integration with hub logging system.
    """
    
    def __init__(self, log_directory: str = None, hub_instance=None):
        """
        Initialize encryption logger.
        
        Args:
            log_directory: Optional custom log directory
            hub_instance: Optional hub instance for log coordination
        """
        self.hub_instance = hub_instance
        self.log_directory = log_directory or self._get_default_log_directory()
        self.session_id = self._generate_session_id()
        
        # Initialize logging components
        self._setup_logging()
        self._setup_audit_logging()
        
        # Performance tracking
        self._operation_timings = {}
        self._session_stats = {
            'start_time': time.time(),
            'operations_count': 0,
            'files_processed': 0,
            'bytes_processed': 0,
            'errors_count': 0
        }
    
    def _get_default_log_directory(self) -> str:
        """Get default log directory."""
        app_data = os.path.expanduser("~/.rfu_hub/logs")
        os.makedirs(app_data, exist_ok=True)
        return app_data
    
    def _generate_session_id(self) -> str:
        """Generate unique session identifier."""
        timestamp = str(time.time())
        return hashlib.md5(timestamp.encode()).hexdigest()[:12]
    
    def _setup_logging(self):
        """Setup standard logging configuration."""
        # Create logger
        self.logger = logging.getLogger(f'encryption_{self.session_id}')
        self.logger.setLevel(logging.DEBUG)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # File handler for general logs
        log_file = os.path.join(
            self.log_directory, 
            f"encryption_{datetime.now().strftime('%Y%m%d')}.log"
        )
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler for immediate feedback
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def _setup_audit_logging(self):
        """Setup audit trail logging."""
        self.audit_file = os.path.join(
            self.log_directory,
            f"encryption_audit_{datetime.now().strftime('%Y%m%d')}.json"
        )
        
        # Initialize audit file if it doesn't exist
        if not os.path.exists(self.audit_file):
            with open(self.audit_file, 'w', encoding='utf-8') as f:
                json.dump([], f)
    
    def log(self, level: LogLevel, message: str, 
            context: Dict[str, Any] = None):
        """
        Log a message with optional context.
        
        Args:
            level: Log level
            message: Log message
            context: Optional context data
        """
        try:
            # Prepare log entry
            log_entry = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'session_id': self.session_id,
                'level': level.value,
                'message': message,
                'context': context or {}
            }
            
            # Log to standard logger
            getattr(self.logger, level.value.lower())(
                f"[{self.session_id}] {message}"
            )
            
            # Send to hub if available
            if self.hub_instance and hasattr(self.hub_instance, 'log_event'):
                self.hub_instance.log_event('encryption', log_entry)
                
        except Exception as e:
            # Fallback logging
            print(f"Logging error: {e}")
    
    def audit(self, event: SecurityEvent, details: Dict[str, Any] = None):
        """
        Log security/audit event.
        
        Args:
            event: Security event type
            details: Event details and context
        """
        try:
            audit_entry = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'session_id': self.session_id,
                'event_type': event.value,
                'details': details or {},
                'user_context': self._get_user_context(),
                'system_context': self._get_system_context()
            }
            
            # Write to audit file
            self._write_audit_entry(audit_entry)
            
            # Log as audit level
            self.log(LogLevel.AUDIT,
                     f"Security event: {event.value}",
                     audit_entry)
            
            # Update session statistics
            self._update_session_stats(event)
            
        except Exception as e:
            self.log(LogLevel.ERROR, f"Audit logging failed: {e}")
    
    def _write_audit_entry(self, entry: Dict[str, Any]):
        """Write audit entry to file."""
        try:
            # Read existing entries
            with open(self.audit_file, 'r', encoding='utf-8') as f:
                entries = json.load(f)
            
            # Add new entry
            entries.append(entry)
            
            # Write back
            with open(self.audit_file, 'w', encoding='utf-8') as f:
                json.dump(entries, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.log(LogLevel.ERROR, f"Failed to write audit entry: {e}")
    
    def _get_user_context(self) -> Dict[str, Any]:
        """Get user context information."""
        return {
            'user': os.getenv('USERNAME', 'unknown'),
            'working_directory': os.getcwd(),
            'process_id': os.getpid()
        }
    
    def _get_system_context(self) -> Dict[str, Any]:
        """Get system context information."""
        return {
            'platform': os.name,
            'python_version': (f"{os.sys.version_info.major}."
                              f"{os.sys.version_info.minor}."
                              f"{os.sys.version_info.micro}"),
            'timestamp_utc': datetime.now(timezone.utc).isoformat()
        }
    
    def _update_session_stats(self, event: SecurityEvent):
        """Update session statistics."""
        if event in [SecurityEvent.OPERATION_STARTED]:
            self._session_stats['operations_count'] += 1
        elif event in [SecurityEvent.FILE_ENCRYPTED, 
                       SecurityEvent.FILE_DECRYPTED]:
            self._session_stats['files_processed'] += 1
        elif event in [SecurityEvent.OPERATION_FAILED, 
                       SecurityEvent.SECURITY_VIOLATION]:
            self._session_stats['errors_count'] += 1
    
    def start_operation_timing(self, operation_id: str):
        """Start timing an operation."""
        self._operation_timings[operation_id] = {
            'start_time': time.time(),
            'end_time': None,
            'duration': None
        }
    
    def end_operation_timing(self, operation_id: str) -> float:
        """
        End timing an operation.
        
        Args:
            operation_id: Operation identifier
            
        Returns:
            Operation duration in seconds
        """
        if operation_id in self._operation_timings:
            timing = self._operation_timings[operation_id]
            timing['end_time'] = time.time()
            timing['duration'] = timing['end_time'] - timing['start_time']
            return timing['duration']
        return 0.0
    
    def log_operation_start(self, operation_type: str,
                            parameters: Dict[str, Any]):
        """Log operation start."""
        operation_id = f"{operation_type}_{int(time.time())}"
        
        self.start_operation_timing(operation_id)
        
        self.audit(SecurityEvent.OPERATION_STARTED, {
            'operation_id': operation_id,
            'operation_type': operation_type,
            'parameters': self._sanitize_parameters(parameters)
        })
        
        self.log(LogLevel.INFO,
                 f"Started {operation_type} operation",
                 {'operation_id': operation_id})
        
        return operation_id
    
    def log_operation_complete(self, operation_id: str,
                               results: Dict[str, Any]):
        """Log operation completion."""
        duration = self.end_operation_timing(operation_id)
        
        self.audit(SecurityEvent.OPERATION_COMPLETED, {
            'operation_id': operation_id,
            'duration_seconds': duration,
            'results': self._sanitize_results(results)
        })
        
        self.log(LogLevel.INFO, 
                f"Completed operation {operation_id} in {duration:.2f}s",
                {'duration': duration, 'results': results})
    
    def log_operation_failed(self, operation_id: str, error: Exception):
        """Log operation failure."""
        duration = self.end_operation_timing(operation_id)
        
        self.audit(SecurityEvent.OPERATION_FAILED, {
            'operation_id': operation_id,
            'duration_seconds': duration,
            'error_type': type(error).__name__,
            'error_message': str(error)
        })
        
        self.log(LogLevel.ERROR, 
                f"Operation {operation_id} failed: {error}",
                {'error_type': type(error).__name__})
    
    def log_file_operation(self, operation: str, file_path: str, 
                          success: bool, file_size: int = None):
        """Log file operation."""
        event = (SecurityEvent.FILE_ENCRYPTED if operation == 'encrypt' 
                else SecurityEvent.FILE_DECRYPTED)
        
        details = {
            'file_path': os.path.basename(file_path),  # Don't log full paths
            'file_size': file_size,
            'success': success
        }
        
        if success:
            self.audit(event, details)
            self.log(LogLevel.INFO, 
                    f"Successfully {operation}ed file: "
                    f"{os.path.basename(file_path)}")
            
            if file_size:
                self._session_stats['bytes_processed'] += file_size
        else:
            self.log(LogLevel.ERROR, 
                    f"Failed to {operation} file: "
                    f"{os.path.basename(file_path)}")
    
    def log_key_operation(self, operation: str, key_path: str = None, 
                         success: bool = True):
        """Log key-related operation."""
        event_map = {
            'generate': SecurityEvent.KEY_GENERATED,
            'load': SecurityEvent.KEY_LOADED,
            'save': SecurityEvent.KEY_SAVED
        }
        
        event = event_map.get(operation, SecurityEvent.KEY_LOADED)
        
        details = {
            'operation': operation,
            'key_file': os.path.basename(key_path) if key_path else None,
            'success': success
        }
        
        self.audit(event, details)
        
        if success:
            self.log(LogLevel.INFO, f"Key {operation} successful")
        else:
            self.log(LogLevel.ERROR, f"Key {operation} failed")
    
    def log_security_violation(self, violation_type: str, 
                              details: Dict[str, Any]):
        """Log security violation."""
        self.audit(SecurityEvent.SECURITY_VIOLATION, {
            'violation_type': violation_type,
            'details': details
        })
        
        self.log(LogLevel.CRITICAL, 
                f"Security violation: {violation_type}",
                details)
    
    def _sanitize_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:  # noqa: E501
        """Sanitize parameters for logging (remove sensitive data)."""
        sanitized = {}
        sensitive_keys = ['key', 'password', 'secret', 'token']
        
        for key, value in parameters.items():
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                sanitized[key] = "[REDACTED]"
            elif isinstance(value, (str, int, float, bool)):
                sanitized[key] = value
            else:
                sanitized[key] = str(type(value))
        
        return sanitized
    
    def _sanitize_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize results for logging."""
        return self._sanitize_parameters(results)
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get current session statistics."""
        current_time = time.time()
        session_duration = current_time - self._session_stats['start_time']
        
        return {
            'session_id': self.session_id,
            'session_duration_seconds': session_duration,
            'operations_count': self._session_stats['operations_count'],
            'files_processed': self._session_stats['files_processed'],
            'bytes_processed': self._session_stats['bytes_processed'],
            'errors_count': self._session_stats['errors_count'],
            'average_operation_time': (
                session_duration /
                max(1, self._session_stats['operations_count'])
            )
        }
    
    def export_audit_log(self, start_date: str = None,
                         end_date: str = None) -> List[Dict[str, Any]]:
        """
        Export audit log entries for a date range.
        
        Args:
            start_date: Start date (ISO format)
            end_date: End date (ISO format)
            
        Returns:
            List of audit entries
        """
        try:
            with open(self.audit_file, 'r', encoding='utf-8') as f:
                entries = json.load(f)
            
            if start_date or end_date:
                filtered_entries = []
                for entry in entries:
                    entry_date = entry['timestamp']
                    
                    if start_date and entry_date < start_date:
                        continue
                    if end_date and entry_date > end_date:
                        continue
                    
                    filtered_entries.append(entry)
                
                return filtered_entries
            
            return entries
            
        except Exception as e:
            self.log(LogLevel.ERROR, f"Failed to export audit log: {e}")
            return []
    
    def cleanup_old_logs(self, days_to_keep: int = 30):
        """Clean up old log files."""
        try:
            cutoff_time = time.time() - (days_to_keep * 24 * 3600)
            
            for filename in os.listdir(self.log_directory):
                file_path = os.path.join(self.log_directory, filename)
                
                if (os.path.isfile(file_path) and 
                        filename.startswith('encryption_') and
                        os.path.getmtime(file_path) < cutoff_time):
                    
                    os.remove(file_path)
                    self.log(LogLevel.INFO,
                            f"Cleaned up old log file: {filename}")
                    
        except Exception as e:
            self.log(LogLevel.ERROR, f"Failed to cleanup old logs: {e}")
    
    def close(self):
        """Close logger and finalize session."""
        # Log session summary
        stats = self.get_session_stats()
        self.log(LogLevel.INFO, "Encryption session ended", stats)
        
        # Close handlers
        for handler in self.logger.handlers:
            handler.close()
            self.logger.removeHandler(handler)