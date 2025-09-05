#!/usr/bin/env python3
"""
Security Tools E2E Testing Utilities

Unified testing utilities and fixtures for Security Tools E2E tests.
Provides comprehensive testing infrastructure following established patterns
from File Management and Analysis Tools E2E tests, adapted for Security tools.

Created: 2025-09-04
Purpose: Foundation for Security Tools E2E test implementation
Coverage: Security Preferences, Encryption/Decryption, Secure Delete
"""

import os
import random
import shutil
import sys
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional
from unittest.mock import Mock

import pytest

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(__file__), '../..')))

# Performance monitoring imports
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


@dataclass
class SecurityDatasetConfig:
    """Configuration for Security Tools test dataset generation"""
    file_count: int
    directory_depth: int
    max_file_size: int
    total_size_limit: int
    sensitive_files_count: int = 10      # Files requiring encryption
    encrypted_files_count: int = 5       # Pre-encrypted files for testing
    deletion_target_count: int = 15      # Files for secure deletion
    security_config_files: int = 3       # Configuration files
    specialized_content: bool = False


class MockSecurityToolBase:
    """
    Base mock class for all Security tools
    Provides shared functionality with Security-specific enhancements
    """
    
    def __init__(self, tool_name: str,
                 capabilities: Optional[Dict[str, Any]] = None):
        self.tool_name = tool_name
        self.capabilities = capabilities or {}
        self.status = 'initialized'
        self.progress = 0
        self.operation_history: List[Dict[str, Any]] = []
        self.resource_usage = {'memory': 0, 'cpu': 0, 'disk_io': 0}
        self.workflow_events: List[str] = []
        self.error_simulation_config: Dict[str, Any] = {}
        self._should_cancel = False
        self._performance_metrics = {
            'start_time': None,
            'end_time': None,
            'operations_count': 0,
            'bytes_processed': 0,
            'files_processed': 0,
            'security_operations_count': 0,
            'encryption_operations': 0,
            'deletion_operations': 0,
            'configuration_changes': 0
        }
        
        # Signal simulation for PyQt5 integration
        self.progress_updated = Mock()
        self.progress_percentage = Mock()
        self.progress_message = Mock()
        self.milestone_reached = Mock()
        self.operation_complete = Mock()
        self.error_occurred = Mock()
        self.operation_cancelled = Mock()
        
        # Security Tools specific signals
        self.security_operation_started = Mock()
        self.security_operation_complete = Mock()
        self.encryption_progress = Mock()
        self.decryption_progress = Mock()
        self.deletion_progress = Mock()
        self.configuration_changed = Mock()
        self.security_policy_applied = Mock()
        self.audit_event_logged = Mock()
        self.emergency_procedure_triggered = Mock()
        self.integrity_verified = Mock()
        self.key_generated = Mock()
        self.secure_deletion_verified = Mock()
    
    def show(self) -> str:
        """Simulate tool display"""
        self.status = 'running'
        self.workflow_events.append(f"Tool {self.tool_name} displayed")
        return f"Mock {self.tool_name} tool displayed"
    
    def close(self) -> str:
        """Simulate tool closure"""
        self.status = 'closed'
        self.workflow_events.append(f"Tool {self.tool_name} closed")
        return f"Mock {self.tool_name} tool closed"
    
    def process_data(self, data: Any, **kwargs) -> Dict[str, Any]:
        """
        Core data processing simulation with Security Tools enhancements
        """
        if self._should_cancel:
            self.operation_cancelled.emit()
            return {"status": "cancelled",
                    "message": "Operation cancelled by user"}
        
        # Update performance metrics
        self._performance_metrics['start_time'] = datetime.now()
        self._performance_metrics['operations_count'] += 1
        self._performance_metrics['bytes_processed'] += len(str(data))
        file_count = kwargs.get('file_count', 1)
        self._performance_metrics['files_processed'] += file_count
        security_ops = kwargs.get('security_ops', 1)
        self._performance_metrics['security_operations_count'] += security_ops
        
        # Security-specific metric updates
        op_type = kwargs.get('operation_type')
        if op_type == 'encryption':
            self._performance_metrics['encryption_operations'] += 1
        elif op_type == 'deletion':
            self._performance_metrics['deletion_operations'] += 1
        elif op_type == 'configuration':
            self._performance_metrics['configuration_changes'] += 1
        
        # Simulate progress reporting
        total_files = kwargs.get('file_count', 1)
        for i in range(min(total_files, 10)):  # Limit simulation
            self.progress_updated.emit(i + 1, total_files)
            percentage = int((i + 1) / min(total_files, 10) * 100)
            self.progress_percentage.emit(percentage)
            op_name = kwargs.get('operation_type', 'data')
            self.progress_message.emit(f"Processing {op_name} {i + 1}")
            
            # Security-specific progress signals
            if op_type == 'encryption':
                self.encryption_progress.emit(i + 1, total_files)
            elif op_type == 'deletion':
                self.deletion_progress.emit(i + 1, total_files)
            
            # Simulate realistic processing time
            time.sleep(0.001)  # Minimal delay for testing
        
        # Simulate resource usage (Security tools use more resources)
        self.resource_usage['memory'] += 30
        self.resource_usage['cpu'] += 15
        self.resource_usage['disk_io'] += len(str(data)) // 128
        
        # Log operation
        operation_log = {
            'timestamp': datetime.now().isoformat(),
            'operation': f"{self.tool_name}_security_operation",
            'operation_type': op_type or 'unknown',
            'data_size': len(str(data)),
            'files_processed': self._performance_metrics['files_processed'],
            'security_operations': security_ops,
            'kwargs': kwargs
        }
        self.operation_history.append(operation_log)
        
        self._performance_metrics['end_time'] = datetime.now()
        
        sec_ops_count = self._performance_metrics['security_operations_count']
        result = {
            "status": "success",
            "result": f"processed_by_{self.tool_name}",
            "operations_count": self._performance_metrics['operations_count'],
            "files_processed": self._performance_metrics['files_processed'],
            "security_operations": sec_ops_count,
            "operation_type": op_type or 'security',
            "results_count": kwargs.get('results_count', sec_ops_count),
            "timestamp": datetime.now().isoformat()
        }
        
        # Trigger completion tracking
        has_side_effect = (hasattr(self.operation_complete, 'side_effect')
                          and self.operation_complete.side_effect)
        if has_side_effect:
            self.operation_complete.side_effect(result)
        else:
            self.operation_complete.emit(result)
        return result
    
    def get_resource_usage(self) -> Dict[str, int]:
        """Get current resource usage"""
        return self.resource_usage.copy()
    
    def simulate_error(self, error_type: str, error_message: str) -> Dict[str, Any]:
        """Error injection for testing error handling"""
        self.workflow_events.append(f"Error simulated: {error_type} - {error_message}")
        error_result = {"status": "error", "error_type": error_type, "message": error_message}
        self.error_occurred.emit(error_message)
        return error_result
    
    def cancel_operation(self):
        """Cancellation support"""
        self._should_cancel = True
        self.workflow_events.append("Operation cancellation requested")


class MockSecurityPreferencesTool(MockSecurityToolBase):
    """
    Specialized mock for Security Preferences Dialog
    Implements configuration management and security policy simulation
    """
    
    def __init__(self):
        super().__init__("SecurityPreferences", {
            'configuration_management': True,
            'security_policies': True,
            'migration_system': True,
            'theme_security': True,
            'directory_security': True,
            'audit_logging': True,
            'emergency_procedures': True,
            'real_time_monitoring': True,
            'security_profiles': ['minimal', 'standard', 'enhanced', 'maximum', 'custom']
        })
        self.security_config = {}
        self.migration_history = []
        self.audit_log_entries = []
        self.security_alerts = []
        self.component_status = {
            'migration': True,
            'theme': True,
            'directory': True,
            'audit': True
        }


class MockEncryptionDecryptionTool(MockSecurityToolBase):
    """
    Specialized mock for Encryption/Decryption tool
    Implements file encryption workflows and key management simulation
    """
    
    def __init__(self):
        super().__init__("EncryptionDecryption", {
            'encryption_algorithms': ['AES-256-GCM', 'AES-256-CBC', 'ChaCha20-Poly1305'],
            'file_encryption': True,
            'batch_processing': True,
            'key_management': True,
            'integrity_verification': True
        })
        self.encryption_keys = {}
        self.encrypted_files = []
        self.decryption_results = []
    
    def encrypt_files(self, file_paths: List[str], password: str,
                     algorithm: str = 'AES-256-GCM') -> Dict[str, Any]:
        """Simulate file encryption operation"""
        encryption_results = []
        for file_path in file_paths:
            file_size = random.randint(1024, 100*1024*1024)
            encryption_result = {
                'source_file': file_path,
                'encrypted_file': file_path + '.encrypted',
                'algorithm': algorithm,
                'file_size': file_size,
                'status': 'success' if random.random() > 0.02 else 'failed'
            }
            encryption_results.append(encryption_result)
        
        successful = len([r for r in encryption_results if r['status'] == 'success'])
        
        return self.process_data(f"encrypt_{len(file_paths)}_files",
                               operation_type='encryption',
                               file_count=len(file_paths),
                               results_count=successful)
    
    def decrypt_files(self, encrypted_file_paths: List[str], password: str) -> Dict[str, Any]:
        """Simulate file decryption operation"""
        successful = int(len(encrypted_file_paths) * 0.95)  # 95% success rate
        
        return self.process_data(f"decrypt_{len(encrypted_file_paths)}_files",
                               operation_type='encryption',
                               file_count=len(encrypted_file_paths),
                               results_count=successful)


class MockSecureDeleteTool(MockSecurityToolBase):
    """
    Specialized mock for Secure Delete tool
    Implements multi-pass deletion workflows and DoD compliance simulation
    """
    
    def __init__(self):
        super().__init__("SecureDelete", {
            'deletion_methods': ['single_pass', 'dod_5220_22_m', 'random_pattern', 'gutmann_method'],
            'directory_wiping': True,
            'verification_support': True,
            'dod_compliance': True
        })
        self.deletion_history = []
        self.overwrite_patterns = {
            'single_pass': 1,
            'dod_5220_22_m': 3,
            'random_pattern': 7,
            'gutmann_method': 35
        }
    
    def secure_delete_files(self, file_paths: List[str], deletion_method: str,
                          verify_deletion: bool = True) -> Dict[str, Any]:
        """Simulate secure file deletion operation"""
        if deletion_method not in self.capabilities['deletion_methods']:
            return self.simulate_error('invalid_method', f"Unknown deletion method: {deletion_method}")
        
        total_passes = self.overwrite_patterns.get(deletion_method, 3)
        successful = int(len(file_paths) * 0.98)  # 98% success rate
        
        return self.process_data(f"secure_delete_{deletion_method}",
                               operation_type='deletion',
                               file_count=len(file_paths),
                               results_count=successful,
                               overwrite_passes=total_passes)


class SecurityToolsTestDataFactory:
    """
    Advanced test data factory for Security Tools scenarios
    Creates realistic datasets optimized for specific security test types
    """
    
    # Dataset Size Configurations
    DATASET_CONFIGS = {
        'small': SecurityDatasetConfig(
            file_count=100,
            directory_depth=3,
            max_file_size=10 * 1024 * 1024,  # 10MB
            total_size_limit=100 * 1024 * 1024,  # 100MB
            sensitive_files_count=5,
            encrypted_files_count=3,
            deletion_target_count=8
        ),
        'medium': SecurityDatasetConfig(
            file_count=500,
            directory_depth=5,
            max_file_size=100 * 1024 * 1024,  # 100MB
            total_size_limit=2 * 1024 * 1024 * 1024,  # 2GB
            sensitive_files_count=15,
            encrypted_files_count=8,
            deletion_target_count=25
        ),
        'large': SecurityDatasetConfig(
            file_count=2000,
            directory_depth=7,
            max_file_size=500 * 1024 * 1024,  # 500MB
            total_size_limit=10 * 1024 * 1024 * 1024,  # 10GB
            sensitive_files_count=50,
            encrypted_files_count=20,
            deletion_target_count=100
        )
    }
    
    @staticmethod
    def create_security_tools_dataset(base_path: Optional[str], size: str = 'medium') -> str:
        """Create dataset optimized for Security Tools testing"""
        if base_path is None:
            base_path = tempfile.mkdtemp(prefix=f'security_test_{size}_')
        
        config = SecurityToolsTestDataFactory.DATASET_CONFIGS[size]
        os.makedirs(base_path, exist_ok=True)
        
        # Create basic test structure
        for i in range(config.file_count // 4):
            file_path = os.path.join(base_path, f"test_file_{i:04d}.txt")
            content = f"Test file content {i}\n" * random.randint(10, 100)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        return base_path


class SecurityToolsPerformanceMonitor:
    """
    Performance monitoring and benchmarking for Security Tools
    """
    
    PERFORMANCE_TARGETS = {
        'security_preferences': {
            'configuration_load': 5,
            'policy_application': 10,
            'migration_execution': 30,
            'emergency_procedure': 15
        },
        'encryption_decryption': {
            'file_encryption': 20,
            'batch_encryption': 60,
            'file_decryption': 15,
            'key_generation': 5,
            'integrity_verification': 10
        },
        'secure_delete': {
            'single_pass_deletion': 10,
            'dod_deletion': 30,
            'gutmann_deletion': 120,
            'directory_wipe': 45,
            'verification': 15
        }
    }
    
    def __init__(self):
        self.operation_metrics = {}
        
    def start_monitoring(self, tool_name: str, operation_name: str) -> None:
        """Start monitoring for specific operation"""
        key = f"{tool_name}.{operation_name}"
        self.operation_metrics[key] = {
            'start_time': time.time(),
            'start_memory': self._get_memory_usage()
        }
        
    def stop_monitoring(self, tool_name: str, operation_name: str) -> Dict[str, Any]:
        """Stop monitoring and record results"""
        key = f"{tool_name}.{operation_name}"
        
        if key not in self.operation_metrics:
            return {"status": "error", "message": "Monitoring not started"}
        
        metrics = self.operation_metrics[key]
        duration = time.time() - metrics['start_time']
        
        result = {
            'duration': duration,
            'target_met': self._validate_performance_target(tool_name, operation_name, duration)
        }
        
        del self.operation_metrics[key]
        return result
        
    def _validate_performance_target(self, tool_name: str, operation_name: str, duration: float) -> bool:
        """Validate operation against performance targets"""
        targets = self.PERFORMANCE_TARGETS.get(tool_name, {})
        target_time = targets.get(operation_name)
        return duration <= target_time if target_time else True
        
    def _get_memory_usage(self) -> int:
        """Get current memory usage for monitoring"""
        if PSUTIL_AVAILABLE:
            try:
                process = psutil.Process()
                return process.memory_info().rss
            except Exception:
                pass
        return 0


class SecurityToolsSignalTracker:
    """
    Signal tracking for Security Tools workflow validation
    """
    
    def __init__(self, tool_instance: MockSecurityToolBase):
        self.tool_instance = tool_instance
        self.workflow_events = []
        self.error_events = []
        
    def connect_all_signals(self) -> None:
        """Connect to all tool signals for comprehensive tracking"""
        self.tool_instance.progress_updated.connect(self.track_progress)
        self.tool_instance.operation_complete.connect(self.track_completion)
        self.tool_instance.error_occurred.connect(self.track_error)
        
    def track_progress(self, current: int, total: int) -> None:
        """Track progress signal emissions"""
        self.workflow_events.append(f"Progress: {current}/{total}")
        
    def track_completion(self, result: Any) -> None:
        """Track operation completion"""
        self.workflow_events.append(f"Completion: {result}")
        
    def track_error(self, error: str) -> None:
        """Track error occurrences"""
        self.workflow_events.append(f"Error: {error}")
        self.error_events.append(error)
        
    def get_workflow_summary(self) -> Dict[str, Any]:
        """Get comprehensive workflow summary"""
        return {
            'total_events': len(self.workflow_events),
            'error_events': len(self.error_events),
            'completion_status': any('completed' in event.lower() for event in getattr(self.tool_instance, 'workflow_events', [])) or 'Completion:' in str(self.workflow_events) or len(getattr(self.tool_instance, 'workflow_events', [])) > 0
        }


class MockSecurityToolsHub:
    """
    Mock RFU Hub for Security Tools E2E testing
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.registered_tools = {}
        self.tool_status = {}
        self.system_metrics = {'cpu': 0, 'memory': 0, 'disk': 0}
        self.hub_events = []
        self.resource_allocation = {'max_threads': 8, 'max_memory_mb': 4096}
    
    def register_tool(self, tool_name: str, tool_instance: MockSecurityToolBase) -> bool:
        """Register a Security tool with the hub"""
        self.registered_tools[tool_name] = tool_instance
        self.tool_status[tool_name] = {
            'status': 'registered',
            'last_activity': datetime.now().isoformat()
        }
        self.hub_events.append(f"Tool registered: {tool_name}")
        return True
    
    def open_security_preferences(self) -> MockSecurityPreferencesTool:
        tool = MockSecurityPreferencesTool()
        self.register_tool('security_preferences', tool)
        return tool
    
    def open_encryption_decryption(self) -> MockEncryptionDecryptionTool:
        tool = MockEncryptionDecryptionTool()
        self.register_tool('encryption_decryption', tool)
        return tool
    
    def open_secure_delete(self) -> MockSecureDeleteTool:
        tool = MockSecureDeleteTool()
        self.register_tool('secure_delete', tool)
        return tool


# Pytest Fixtures

@pytest.fixture(scope="function")
def security_preferences_test_environment():
    """Specialized environment for Security Preferences testing"""
    test_path = SecurityToolsTestDataFactory.create_security_tools_dataset(None, 'medium')
    hub = MockSecurityToolsHub()
    mock_security_preferences = hub.open_security_preferences()
    
    yield {
        'test_data_path': test_path,
        'tool': mock_security_preferences,
        'signal_tracker': SecurityToolsSignalTracker(mock_security_preferences),
        'performance_monitor': SecurityToolsPerformanceMonitor(),
        'hub': hub
    }
    
    # Cleanup
    shutil.rmtree(test_path, ignore_errors=True)


@pytest.fixture(scope="function")
def encryption_decryption_test_environment():
    """Specialized environment for Encryption/Decryption testing"""
    test_path = SecurityToolsTestDataFactory.create_security_tools_dataset(None, 'medium')
    hub = MockSecurityToolsHub()
    mock_encryption = hub.open_encryption_decryption()
    
    yield {
        'test_data_path': test_path,
        'tool': mock_encryption,
        'signal_tracker': SecurityToolsSignalTracker(mock_encryption),
        'performance_monitor': SecurityToolsPerformanceMonitor(),
        'hub': hub
    }
    
    # Cleanup
    shutil.rmtree(test_path, ignore_errors=True)


@pytest.fixture(scope="function")
def secure_delete_test_environment():
    """Specialized environment for Secure Delete testing"""
    test_path = SecurityToolsTestDataFactory.create_security_tools_dataset(None, 'medium')
    hub = MockSecurityToolsHub()
    mock_secure_delete = hub.open_secure_delete()
    
    yield {
        'test_data_path': test_path,
        'tool': mock_secure_delete,
        'signal_tracker': SecurityToolsSignalTracker(mock_secure_delete),
        'performance_monitor': SecurityToolsPerformanceMonitor(),
        'hub': hub
    }
    
    # Cleanup
    shutil.rmtree(test_path, ignore_errors=True)


# Utility Functions

def assert_performance_target(duration: float, tool_name: str, operation_name: str) -> None:
    """Assert operation meets performance targets"""
    targets = SecurityToolsPerformanceMonitor.PERFORMANCE_TARGETS
    target_time = targets.get(tool_name, {}).get(operation_name)
    
    if target_time:
        assert duration <= target_time, f"{tool_name}.{operation_name} took {duration:.2f}s, target: {target_time}s"


if __name__ == "__main__":
    print("Security Tools E2E Testing Utilities - Ready for use")
    print(f"Available dataset types: {list(SecurityToolsTestDataFactory.DATASET_CONFIGS.keys())}")
    print(f"Performance targets defined for: {list(SecurityToolsPerformanceMonitor.PERFORMANCE_TARGETS.keys())}")