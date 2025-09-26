# Diagnostics Monitoring System

## Overview

The Diagnostics Monitoring System is a comprehensive cross-platform system monitoring solution integrated into Richard's File Utilities. It provides real-time monitoring, historical analysis, and configurable alerting for four essential system monitoring tools.

## Features

### 🖥️ System Monitoring Tools

1. **Disk Health Monitor**
   - SMART data analysis and monitoring
   - Real-time disk space tracking
   - Predictive failure detection
   - Cross-platform disk enumeration

2. **RAM & CPU Usage Tracker**
   - Real-time performance metrics
   - Historical data visualization
   - Process-level analysis
   - Multi-core CPU monitoring

3. **File System Integrity Check**
   - Automated scanning capabilities
   - Corruption detection algorithms
   - Repair recommendations
   - Scheduled integrity checks

4. **Battery Health Monitor**
   - Charge cycle tracking
   - Health status reporting
   - Power consumption analysis
   - Battery lifespan predictions

### 📊 Dashboard & Visualization

- **Unified Dashboard**: Real-time overview of all system metrics
- **Historical Charts**: Trend analysis and historical data visualization
- **Alert Management**: Configurable thresholds and notification system
- **Export Functionality**: Data export in multiple formats (JSON, CSV, PDF, HTML)

### 🔔 Alert System

- **Configurable Thresholds**: User-defined warning and critical levels
- **Multi-level Alerts**: Info, Warning, and Critical alert levels
- **Multiple Notification Methods**: GUI notifications, system notifications, email alerts
- **Alert History**: Complete alert tracking and management

### 🌐 Cross-Platform Support

- **Windows**: WMI queries, Performance Counters, Windows APIs
- **macOS**: IOKit framework, system_profiler, Activity Monitor APIs
- **Linux**: proc filesystem, sysfs, system utilities integration

## Installation

### Prerequisites

```bash
# Core dependencies (already in RFU requirements.txt)
PyQt5>=5.15.11
psutil>=7.0.0

# Additional dependencies for diagnostics monitoring
smartmontools  # For SMART data (cross-platform)
sqlite3        # For data storage (built-in Python)
```

### Platform-Specific Requirements

#### Windows
- WMI (Windows Management Instrumentation) - Built-in
- Performance Counters - Built-in
- Administrator privileges for some disk operations

#### macOS
- Xcode Command Line Tools
- IOKit framework access
- Administrator privileges for some system operations

#### Linux
- smartmontools package
- sysfs filesystem access
- Root privileges for some hardware operations

## Quick Start

### 1. Access Diagnostics Monitoring

From the main RFU Hub interface:
1. Click the **"Diagnostics"** button in the main toolbar
2. The Diagnostics Dashboard will open showing real-time system status

### 2. Configure Monitoring

1. **Set Thresholds**: Go to Settings → Threshold Configuration
   - Disk space warning/critical levels
   - CPU usage thresholds
   - Memory usage limits
   - Battery health thresholds

2. **Configure Alerts**: Go to Settings → Alert Configuration
   - Enable/disable notification types
   - Set alert escalation rules
   - Configure email notifications (if desired)

3. **Customize Dashboard**: Right-click on dashboard panels
   - Rearrange monitoring widgets
   - Show/hide specific metrics
   - Adjust update intervals

### 3. Monitor System Health

#### Real-time Monitoring
- **Dashboard Overview**: See all system metrics at a glance
- **Individual Monitors**: Click on specific monitoring tools for detailed views
- **Alert Notifications**: Receive immediate notifications for threshold breaches

#### Historical Analysis
- **Trend Charts**: View historical data trends for all monitored metrics
- **Performance Reports**: Generate detailed performance reports
- **Data Export**: Export monitoring data for external analysis

## Configuration

### Threshold Configuration

```json
{
  "disk_health": {
    "space_warning_percent": 80,
    "space_critical_percent": 90,
    "smart_temperature_warning": 50,
    "smart_temperature_critical": 60
  },
  "performance": {
    "cpu_warning_percent": 80,
    "cpu_critical_percent": 95,
    "memory_warning_percent": 85,
    "memory_critical_percent": 95
  },
  "filesystem": {
    "scan_interval_hours": 24,
    "auto_scan_enabled": true
  },
  "battery": {
    "health_warning_percent": 80,
    "cycle_count_warning": 1000
  }
}
```

### Alert Configuration

```json
{
  "notifications": {
    "gui_enabled": true,
    "system_enabled": true,
    "email_enabled": false,
    "log_enabled": true
  },
  "escalation": {
    "warning_repeat_minutes": 30,
    "critical_repeat_minutes": 5,
    "max_escalations": 3
  }
}
```

## Usage Examples

### Monitoring Disk Health

```python
# Example: Check disk health status
from diagnostics_monitoring.monitors.disk_health import DiskMonitor

disk_monitor = DiskMonitor()
health_status = disk_monitor.get_health_status()

for disk in health_status:
    print(f"Disk {disk['device']}: {disk['health_status']}")
    print(f"  Temperature: {disk['temperature']}°C")
    print(f"  Free Space: {disk['free_space_percent']}%")
```

### Performance Monitoring

```python
# Example: Get current performance metrics
from diagnostics_monitoring.monitors.performance import PerformanceMonitor

perf_monitor = PerformanceMonitor()
metrics = perf_monitor.get_current_metrics()

print(f"CPU Usage: {metrics['cpu_percent']}%")
print(f"Memory Usage: {metrics['memory_percent']}%")
print(f"Load Average: {metrics['load_average']}")
```

### Setting Up Alerts

```python
# Example: Configure custom alert thresholds
from diagnostics_monitoring.core.alert_manager import AlertManager

alert_manager = AlertManager()

# Set custom CPU threshold
alert_manager.set_threshold(
    monitor_type="performance",
    metric="cpu_percent",
    warning_level=75,
    critical_level=90
)

# Enable email notifications
alert_manager.configure_notifications(
    email_enabled=True,
    email_address="admin@example.com"
)
```

## Data Export

### Export Formats

1. **JSON Export**: Raw data in JSON format for programmatic access
2. **CSV Export**: Tabular data for spreadsheet analysis
3. **PDF Reports**: Formatted reports with charts and analysis
4. **HTML Reports**: Web-friendly reports with interactive charts

### Export Examples

```python
# Export last 24 hours of performance data
from diagnostics_monitoring.data.exporters import CSVExporter

exporter = CSVExporter()
exporter.export_performance_data(
    start_time=datetime.now() - timedelta(hours=24),
    end_time=datetime.now(),
    output_file="performance_report.csv"
)

# Generate PDF report
from diagnostics_monitoring.data.exporters import PDFExporter

pdf_exporter = PDFExporter()
pdf_exporter.generate_system_report(
    output_file="system_health_report.pdf",
    include_charts=True,
    time_range="last_week"
)
```

## Troubleshooting

### Common Issues

#### 1. Permission Errors
**Problem**: Cannot access system information
**Solution**: 
- Windows: Run as Administrator
- macOS/Linux: Use sudo for system-level operations
- Check user permissions for hardware access

#### 2. Missing Dependencies
**Problem**: Import errors for platform-specific modules
**Solution**:
```bash
# Windows
pip install wmi pywin32

# macOS
pip install pyobjc-framework-IOKit

# Linux
sudo apt-get install smartmontools
pip install python-dbus
```

#### 3. High CPU Usage
**Problem**: Monitoring causing high system load
**Solution**:
- Increase monitoring intervals in settings
- Disable unnecessary monitoring features
- Check for background processes conflicts

#### 4. Database Errors
**Problem**: Cannot save historical data
**Solution**:
- Check disk space for database storage
- Verify write permissions for data directory
- Reset database if corrupted

### Performance Optimization

1. **Adjust Monitoring Intervals**
   - Increase update intervals for less critical metrics
   - Use adaptive intervals based on system load

2. **Selective Monitoring**
   - Disable monitoring for unused features
   - Focus on critical system components

3. **Data Retention**
   - Configure appropriate data retention policies
   - Archive old data to external storage

## Integration with RFU Hub

### Theme Integration
The Diagnostics Monitoring System automatically inherits the current RFU theme:
- Light/Dark theme support
- Custom color schemes
- Font size preferences
- Window styling consistency

### Configuration Integration
All settings are stored in the main RFU configuration system:
- Centralized configuration management
- Profile support for different monitoring setups
- Backup and restore capabilities

### Error Handling Integration
Uses RFU's centralized error handling:
- Consistent error reporting
- Automatic error logging
- User-friendly error messages

## API Reference

### Core Classes

- `MonitorBase`: Base class for all monitoring tools
- `DataCollector`: Handles data collection and processing
- `AlertManager`: Manages alert generation and delivery
- `ThresholdManager`: Configurable threshold management

### Monitor Classes

- `DiskMonitor`: Disk health and space monitoring
- `PerformanceMonitor`: CPU and memory monitoring
- `FilesystemMonitor`: Filesystem integrity checking
- `BatteryMonitor`: Battery health monitoring

### GUI Classes

- `DiagnosticsHub`: Main diagnostics interface
- `MainDashboard`: Real-time monitoring dashboard
- `AlertPanel`: Alert management interface

For detailed API documentation, see [API Reference](docs/api_reference.md).

## Contributing

### Development Setup

1. Clone the RFU repository
2. Install development dependencies
3. Set up pre-commit hooks
4. Run the test suite

### Testing

```bash
# Run all diagnostics tests
python -m pytest diagnostics_monitoring/tests/

# Run specific test categories
python -m pytest diagnostics_monitoring/tests/test_monitors/
python -m pytest diagnostics_monitoring/tests/test_gui/

# Run with coverage
python -m pytest --cov=diagnostics_monitoring
```

### Code Style

Follow the existing RFU code style:
- PEP 8 compliance
- Type hints for all functions
- Comprehensive docstrings
- Error handling best practices

## License

This module is part of Richard's File Utilities and follows the same licensing terms.

## Support

For support and bug reports:
1. Check the troubleshooting section above
2. Review the [platform-specific notes](docs/platform_notes.md)
3. Submit issues through the RFU issue tracker
4. Consult the [user guide](docs/user_guide.md) for detailed usage instructions