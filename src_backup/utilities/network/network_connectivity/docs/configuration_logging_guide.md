# Network Connectivity Configuration and Logging Guide

**Version:** 1.2.0  
**Date:** 2025-07-26  
**Author:** Network Connectivity Development Team

## Table of Contents

1. [Overview](#overview)
2. [Configuration Management](#configuration-management)
3. [Logging Framework](#logging-framework)
4. [Shared Services](#shared-services)
5. [Configuration Profiles](#configuration-profiles)
6. [Advanced Features](#advanced-features)
7. [GUI Components](#gui-components)
8. [API Reference](#api-reference)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)

## Overview

The Network Connectivity toolkit includes comprehensive shared configuration and logging systems designed to provide:

- **Unified Configuration Management**: Centralized configuration with profiles, validation, and migration
- **Advanced Logging Framework**: Structured logging with aggregation, analysis, and real-time monitoring
- **Shared Services**: Configuration, logging, notification, and metrics services
- **Production-Ready Features**: Backup/restore, import/export, validation, and GUI management

### Key Features

- ✅ **Configuration Profiles**: Pre-built profiles for different use cases (home, enterprise, security audit)
- ✅ **Real-time Validation**: Comprehensive validation with detailed error reporting
- ✅ **Configuration Migration**: Automatic migration between configuration versions
- ✅ **Backup & Restore**: Configuration backup with versioning and restore points
- ✅ **Structured Logging**: JSON-formatted logs with metadata and context
- ✅ **Log Aggregation**: Centralized logging from all network tools
- ✅ **Performance Monitoring**: Built-in performance metrics and alerting
- ✅ **Security Auditing**: Security event logging and analysis
- ✅ **GUI Management**: User-friendly configuration management interface

## Configuration Management

### Configuration Service

The `ConfigurationService` provides centralized configuration management for all network connectivity tools.

```python
from network_connectivity.core.config_service import get_config_service

# Get the configuration service
config_service = get_config_service()

# Get current configuration
config = config_service.get_configuration()

# Update configuration
updates = {
    "general": {
        "default_timeout": 10000,
        "log_level": "DEBUG"
    }
}
success = config_service.update_configuration(updates, validate=True)
```

### Configuration Structure

The configuration is organized hierarchically:

```json
{
  "network_connectivity": {
    "general": {
      "default_timeout": 5000,
      "max_concurrent_operations": 10,
      "enable_logging": true,
      "log_level": "INFO",
      "auto_save_results": true,
      "results_retention_days": 30
    },
    "bandwidth_monitor": {
      "monitoring_interval": 1000,
      "data_retention_hours": 24,
      "alert_threshold_mbps": 100.0,
      "enable_alerts": true
    },
    "wifi_analyzer": {
      "scan_interval": 30000,
      "signal_interval": 2000,
      "enable_security_analysis": true,
      "max_access_points": 1000
    },
    "port_scanner": {
      "default_scan_type": "tcp",
      "scan_timeout": 3000,
      "max_threads": 50,
      "enable_service_detection": true
    },
    "security": {
      "security_level": "moderate",
      "enable_scan_logging": true,
      "alert_on_suspicious_activity": true
    },
    "performance": {
      "enable_performance_monitoring": true,
      "max_memory_usage_mb": 512,
      "max_cpu_usage_percent": 25
    }
  }
}
```

### Configuration Validation

The system includes comprehensive validation:

```python
from network_connectivity.config.config_validator import get_config_validator

validator = get_config_validator()

# Validate configuration
errors = validator.validate_configuration(config)

if errors:
    for error in errors:
        print(f"Error at {error.path}: {error.message}")
        if error.suggestion:
            print(f"Suggestion: {error.suggestion}")
```

### Configuration Profiles

Profiles provide pre-configured settings for different use cases:

```python
from network_connectivity.config.config_profiles import get_profile_manager

profile_manager = get_profile_manager()

# Get available templates
templates = profile_manager.get_templates()

# Create profile from template
success = profile_manager.create_profile_from_template(
    "enterprise", "My Enterprise Profile"
)

# Switch to profile
config_service.switch_profile("My Enterprise Profile")
```

#### Available Profile Templates

1. **Home User Profile**
   - Optimized for home users with basic monitoring needs
   - Moderate resource usage
   - Essential security features

2. **Enterprise Profile**
   - Comprehensive monitoring for enterprise environments
   - Advanced security analysis
   - Detailed logging and reporting

3. **Security Audit Profile**
   - Intensive security scanning and monitoring
   - Maximum logging detail
   - Strict security policies

4. **Development Profile**
   - Lightweight configuration for development work
   - Minimal logging
   - Fast scan intervals

### Backup and Restore

```python
# Create backup
backup_id = config_service.create_backup(
    "Pre-upgrade backup",
    "Backup before system upgrade"
)

# List backups
backups = config_service.get_backups()

# Restore backup
success = config_service.restore_backup(backup_id)
```

### Import and Export

```python
# Export configuration
success = config_service.export_configuration(
    "my_config.json",
    include_profiles=True,
    include_backups=False
)

# Import configuration
success = config_service.import_configuration(
    "my_config.json",
    import_profiles=True,
    validate=True
)
```

## Logging Framework

### Logging Service

The `LoggingService` provides advanced logging capabilities:

```python
from network_connectivity.core.logging_service import (
    get_logging_service, LogLevel, log_info, log_error
)

# Get the logging service
logging_service = get_logging_service()

# Structured logging
logging_service.log_structured(
    level=LogLevel.INFO,
    tool_name="BandwidthMonitor",
    message="Monitoring started",
    operation="start_monitoring",
    context={"interface": "eth0"},
    metadata={"version": "1.2.0"},
    correlation_id="mon-123",
    performance_data={"startup_time_ms": 150}
)

# Convenience functions
log_info("BandwidthMonitor", "Monitoring started")
log_error("PortScanner", "Scan failed", error_data={"code": 500})
```

### Log Levels

The system supports enhanced log levels:

- `TRACE`: Detailed trace information
- `DEBUG`: Debug information
- `INFO`: General information
- `WARNING`: Warning messages
- `ERROR`: Error messages
- `CRITICAL`: Critical errors
- `SECURITY`: Security events
- `PERFORMANCE`: Performance metrics
- `AUDIT`: Audit trail events

### Log Collectors

Specialized collectors process different types of logs:

#### Performance Log Collector

```python
# Automatically collects performance metrics
log_performance(
    "BandwidthMonitor",
    "Bandwidth measurement completed",
    performance_data={
        "response_time_ms": 250,
        "memory_usage_mb": 64,
        "cpu_usage_percent": 15
    }
)
```

#### Security Log Collector

```python
# Automatically analyzes security events
log_security(
    "PortScanner",
    "Suspicious scan detected",
    metadata={
        "source_ip": "192.168.1.100",
        "target_ports": [22, 80, 443]
    }
)
```

#### Error Log Collector

```python
# Automatically correlates related errors
log_error(
    "WiFiAnalyzer",
    "Scan timeout",
    correlation_id="scan-456",
    error_data={
        "timeout_ms": 30000,
        "interface": "wlan0"
    }
)
```

### Log Search and Analysis

```python
from network_connectivity.core.logging_service import LogFilter

# Create search filter
log_filter = LogFilter(
    min_level=LogLevel.WARNING,
    tools=["BandwidthMonitor", "PortScanner"],
    start_time=datetime.now() - timedelta(hours=1),
    keywords=["error", "timeout"]
)

# Search logs
results = logging_service.search_logs(log_filter, limit=100)

# Get analytics
analytics = logging_service.get_analytics("BandwidthMonitor")
print(f"Total logs: {analytics['total_count']}")
print(f"Error count: {analytics['ERROR_count']}")
```

### Log Export

```python
from network_connectivity.core.logging_service import LogFormat

# Export logs to JSON
success = logging_service.export_logs(
    "network_logs.jsonl",
    log_filter,
    LogFormat.JSON
)

# Export logs to CSV
success = logging_service.export_logs(
    "network_logs.csv",
    log_filter,
    LogFormat.CSV
)
```

## Shared Services

### Notification Service

The notification service provides real-time alerts and notifications:

```python
from network_connectivity.core.notification_service import (
    get_notification_service, NotificationType, NotificationPriority
)

notification_service = get_notification_service()

# Send notification
notification_id = notification_service.send_notification(
    type=NotificationType.WARNING,
    title="High Bandwidth Usage",
    message="Bandwidth usage exceeded 90% of threshold",
    source="BandwidthMonitor",
    priority=NotificationPriority.HIGH,
    data={"current_usage": 450, "threshold": 500}
)

# Add notification rule
notification_service.add_rule(
    name="bandwidth_alert",
    condition=lambda data: data.get('bandwidth_usage', 0) > 400,
    notification_template={
        'type': 'warning',
        'title': 'Bandwidth Alert',
        'message': 'High bandwidth usage: {bandwidth_usage} Mbps'
    }
)
```

### Metrics Service

The metrics service collects and analyzes performance metrics:

```python
from network_connectivity.core.metrics_service import (
    get_metrics_service, MetricType, MetricUnit, record_gauge
)

metrics_service = get_metrics_service()

# Create metric
metrics_service.create_metric(
    "bandwidth_usage",
    MetricType.GAUGE,
    MetricUnit.MBPS,
    "Current bandwidth usage"
)

# Record metric value
metrics_service.record_value("bandwidth_usage", 125.5)

# Convenience function
record_gauge("cpu_usage_percent", 45.2)

# Get metric summary
summary = metrics_service.get_metrics_summary()

# Add metric alert
metrics_service.add_alert(
    "bandwidth_usage",
    "gt",  # greater than
    400.0,  # threshold
    duration_seconds=60
)
```

## Advanced Features

### Real-time Configuration Updates

The system supports real-time configuration updates without restart:

```python
# Listen for configuration events
def on_config_updated(event_data):
    print(f"Configuration updated: {event_data['updates']}")

config_service.add_event_callback(
    ConfigurationEvent.CONFIG_UPDATED,
    on_config_updated
)

# Updates are automatically applied
config_service.update_configuration({
    "general": {"log_level": "DEBUG"}
})
```

### Configuration Migration

Automatic migration between configuration versions:

```python
# Migrate configuration
success = config_service.migrate_configuration("1.0.0", "1.2.0")

if success:
    print("Configuration migrated successfully")
else:
    print("Migration failed")
```

### Cross-field Validation

The validator performs cross-field validation:

```python
# Example: Port conflict detection
config = {
    "lan_file_transfer": {
        "discovery_port": 8080,
        "transfer_port": 8080  # Conflict!
    }
}

errors = validator.validate_configuration(config)
# Will report port conflict error
```

## GUI Components

### Configuration Manager Dialog

The GUI provides a comprehensive configuration management interface:

```python
from network_connectivity.gui.dialogs.config_manager_dialog import (
    ConfigurationManagerDialog
)

# Open configuration manager
dialog = ConfigurationManagerDialog()
dialog.exec_()
```

#### Features:

- **Profile Management**: Create, switch, and delete configuration profiles
- **Configuration Tree**: Hierarchical view of all settings with inline editing
- **Real-time Validation**: Immediate feedback on configuration changes
- **Import/Export**: Easy configuration sharing and backup
- **Search and Filter**: Find specific settings quickly

### Profile Creation Dialog

```python
from network_connectivity.gui.dialogs.profile_creation_dialog import (
    ProfileCreationDialog
)

dialog = ProfileCreationDialog()
if dialog.exec_() == QDialog.Accepted:
    print(f"Created profile: {dialog.profile_name}")
```

## API Reference

### Configuration Service API

```python
class ConfigurationService:
    def get_configuration(self, use_cache: bool = True) -> Dict[str, Any]
    def update_configuration(self, updates: Dict[str, Any], validate: bool = True) -> bool
    def create_profile(self, name: str, description: str, use_case: str, settings: Dict[str, Any]) -> bool
    def switch_profile(self, name: str) -> bool
    def delete_profile(self, name: str) -> bool
    def create_backup(self, name: str, description: str = "") -> str
    def restore_backup(self, backup_id: str) -> bool
    def export_configuration(self, file_path: str, include_profiles: bool = True) -> bool
    def import_configuration(self, file_path: str, import_profiles: bool = True) -> bool
    def validate_configuration(self, config: Dict[str, Any] = None) -> List[str]
```

### Logging Service API

```python
class LoggingService:
    def log_structured(self, level: LogLevel, tool_name: str, message: str, **kwargs)
    def search_logs(self, log_filter: LogFilter, limit: int = 1000) -> List[LogEntry]
    def get_analytics(self, tool_name: str = None) -> Dict[str, Any]
    def export_logs(self, file_path: str, log_filter: LogFilter, format_type: LogFormat) -> bool
    def get_log_statistics(self) -> Dict[str, Any]
    def cleanup_old_logs(self, max_age_hours: int = 24)
```

### Notification Service API

```python
class NotificationService:
    def send_notification(self, type: NotificationType, title: str, message: str, **kwargs) -> str
    def acknowledge_notification(self, notification_id: str, acknowledged_by: str = None) -> bool
    def get_notifications(self, include_acknowledged: bool = False) -> List[Notification]
    def add_rule(self, name: str, condition: Callable, notification_template: Dict[str, Any])
    def trigger_rules(self, event_data: Dict[str, Any])
```

### Metrics Service API

```python
class MetricsService:
    def create_metric(self, name: str, metric_type: MetricType, unit: MetricUnit, description: str) -> bool
    def record_value(self, metric_name: str, value: Union[int, float], **kwargs) -> bool
    def get_metric_value(self, name: str, aggregation: str = "latest") -> Optional[float]
    def get_metrics_summary(self) -> Dict[str, Any]
    def add_alert(self, metric_name: str, condition: str, threshold: Union[int, float]) -> bool
    def export_metrics(self, file_path: str, format_type: str = "json") -> bool
```

## Best Practices

### Configuration Management

1. **Use Profiles**: Create profiles for different environments (dev, test, prod)
2. **Validate Changes**: Always validate configuration before applying
3. **Backup Before Changes**: Create backups before major configuration changes
4. **Version Control**: Export configurations to version control systems
5. **Document Changes**: Use descriptive names and comments for profiles

### Logging

1. **Use Structured Logging**: Include context and metadata in log entries
2. **Correlation IDs**: Use correlation IDs to track related operations
3. **Appropriate Levels**: Use appropriate log levels for different types of events
4. **Performance Logging**: Log performance metrics for monitoring
5. **Security Logging**: Log security-related events for audit trails

### Performance

1. **Log Rotation**: Configure appropriate log rotation policies
2. **Metric Retention**: Set reasonable metric retention periods
3. **Resource Limits**: Configure memory and CPU limits appropriately
4. **Cleanup Policies**: Implement regular cleanup of old data

### Security

1. **Sensitive Data**: Avoid logging sensitive information
2. **Access Control**: Implement proper access control for configuration
3. **Audit Trails**: Enable audit logging for configuration changes
4. **Encryption**: Consider encrypting stored configuration data

## Troubleshooting

### Common Issues

#### Configuration Not Loading

```python
# Check configuration file permissions
config_path = Path("configuration.json")
if not config_path.exists():
    print("Configuration file not found")
elif not config_path.is_readable():
    print("Configuration file not readable")

# Check configuration syntax
try:
    with open(config_path) as f:
        json.load(f)
    print("Configuration syntax is valid")
except json.JSONDecodeError as e:
    print(f"Configuration syntax error: {e}")
```

#### Validation Errors

```python
# Get detailed validation results
validator = get_config_validator()
errors = validator.validate_configuration(config)

for error in errors:
    print(f"Path: {error.path}")
    print(f"Error: {error.message}")
    if error.suggestion:
        print(f"Suggestion: {error.suggestion}")
    print("---")
```

#### Logging Issues

```python
# Check logging service status
logging_service = get_logging_service()
stats = logging_service.get_log_statistics()

print(f"Total log entries: {stats['total_entries']}")
print(f"Active collectors: {stats['active_collectors']}")
print(f"Active handlers: {stats['active_handlers']}")

# Check log file permissions
log_files = Path("logs/network_connectivity").glob("*.log")
for log_file in log_files:
    if not log_file.is_writable():
        print(f"Log file not writable: {log_file}")
```

#### Performance Issues

```python
# Check metrics service status
metrics_service = get_metrics_service()
stats = metrics_service.get_statistics()

print(f"Total metrics: {stats['total_metrics']}")
print(f"Memory usage: {stats['memory_usage_values']} entries")

# Check resource usage
import psutil
print(f"CPU usage: {psutil.cpu_percent()}%")
print(f"Memory usage: {psutil.virtual_memory().percent}%")
```

### Debug Mode

Enable debug mode for detailed troubleshooting:

```python
# Enable debug logging
config_service.update_configuration({
    "general": {"log_level": "DEBUG"}
})

# Enable performance monitoring
config_service.update_configuration({
    "performance": {"enable_performance_monitoring": True}
})
```

### Support and Documentation

For additional support:

1. Check the [Network Connectivity Architecture Guide](network_connectivity_architecture.md)
2. Review the [Integration Guide](network_connectivity_integration_guide.md)
3. Examine the test files for usage examples
4. Enable debug logging for detailed troubleshooting information

---

**Last Updated:** 2025-07-26  
**Version:** 1.2.0  
**Compatibility:** Network Connectivity Toolkit v1.2.0+