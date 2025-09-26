# Configuration Reference

**Version:** 1.2.0  
**Last Updated:** 2025-07-26  
**Compatibility:** Network Connectivity Toolkit v1.2.0+

## Overview

This document provides a comprehensive reference for all configuration options available in the Network Connectivity Toolkit. Configuration is managed through YAML files and can be modified via the GUI, API, or direct file editing.

## 📁 Configuration File Locations

### Default Locations
- **Windows:** `%APPDATA%\NetworkConnectivity\config.yaml`
- **macOS:** `~/Library/Application Support/NetworkConnectivity/config.yaml`
- **Linux:** `~/.config/NetworkConnectivity/config.yaml`

### Alternative Locations
- **Environment Variable:** Set `NETWORK_CONNECTIVITY_CONFIG` to specify custom location
- **Command Line:** Use `--config` parameter to specify configuration file
- **Working Directory:** `./network_connectivity_config.yaml` (if exists)

## 🏗️ Configuration Structure

### Root Configuration Schema
```yaml
network_connectivity:
  general: {}           # General toolkit settings
  bandwidth_monitor: {} # Bandwidth monitoring configuration
  port_scanner: {}      # Port scanning configuration
  wifi_analyzer: {}     # Wi-Fi analysis configuration
  lan_file_transfer: {} # LAN file transfer configuration
  connectivity_tester: {} # Connectivity testing configuration
  network_diagnostics: {} # Network diagnostics configuration
  security: {}          # Security settings
  performance: {}       # Performance tuning
  logging: {}           # Logging configuration
  notifications: {}     # Notification settings
```

## ⚙️ General Settings

### `network_connectivity.general`

Core toolkit configuration options.

```yaml
network_connectivity:
  general:
    default_timeout: 5000              # Default operation timeout (ms)
    max_concurrent_operations: 10      # Maximum concurrent operations
    enable_logging: true               # Enable logging system
    log_level: "INFO"                  # Logging level
    auto_save_results: true            # Automatically save results
    results_retention_days: 30         # Data retention period
    enable_notifications: true         # Enable notification system
    notification_sound: true           # Play notification sounds
    data_cache_timeout: 30             # Data cache timeout (seconds)
    max_history_entries: 1000          # Maximum historical data entries
    config_auto_backup: true           # Automatically backup configuration
    backup_retention_count: 5          # Number of config backups to keep
    theme: "auto"                      # UI theme (auto, light, dark)
    language: "en"                     # Interface language
    update_check_enabled: true         # Check for updates
    telemetry_enabled: false           # Send anonymous usage data
```

#### Parameter Details

| Parameter | Type | Default | Range/Options | Description |
|-----------|------|---------|---------------|-------------|
| `default_timeout` | integer | 5000 | 1000-60000 | Default timeout for network operations in milliseconds |
| `max_concurrent_operations` | integer | 10 | 1-100 | Maximum number of simultaneous operations |
| `enable_logging` | boolean | true | true/false | Enable or disable logging system |
| `log_level` | string | "INFO" | DEBUG, INFO, WARNING, ERROR, CRITICAL | Minimum logging level |
| `auto_save_results` | boolean | true | true/false | Automatically save operation results |
| `results_retention_days` | integer | 30 | 1-365 | Number of days to retain historical data |
| `enable_notifications` | boolean | true | true/false | Enable notification system |
| `notification_sound` | boolean | true | true/false | Play sounds for notifications |
| `data_cache_timeout` | integer | 30 | 1-3600 | Cache timeout in seconds |
| `max_history_entries` | integer | 1000 | 100-10000 | Maximum entries in history |

## 📊 Bandwidth Monitor Configuration

### `network_connectivity.bandwidth_monitor`

Configuration for bandwidth monitoring functionality.

```yaml
network_connectivity:
  bandwidth_monitor:
    # Basic Settings
    monitoring_interval: 1000          # Data collection interval (ms)
    data_retention_hours: 24           # Data retention period (hours)
    alert_threshold_mbps: 100.0        # Speed alert threshold (Mbps)
    enable_alerts: true                # Enable bandwidth alerts
    monitor_interfaces: "auto"         # Interfaces to monitor
    
    # Display Settings
    chart_update_interval: 2000        # Chart refresh rate (ms)
    enable_real_time_chart: true       # Show real-time charts
    show_upload_download_separate: true # Separate upload/download display
    data_units: "auto"                 # Data units (auto, bytes, bits)
    chart_time_range: 3600             # Chart time range (seconds)
    
    # Advanced Features
    enable_application_monitoring: false # Monitor per-application usage
    peak_detection_enabled: true       # Detect usage peaks
    baseline_calculation_hours: 168    # Baseline calculation period (hours)
    anomaly_detection_enabled: false   # Detect usage anomalies
    traffic_shaping_detection: true    # Detect traffic shaping
    
    # Export Settings
    export_format: "csv"               # Default export format
    auto_export_enabled: false         # Enable automatic exports
    auto_export_interval_hours: 24     # Auto export interval
    export_include_metadata: true      # Include metadata in exports
    
    # Alert Configuration
    alert_email: ""                    # Email for alerts
    alert_webhook_url: ""              # Webhook URL for alerts
    alert_cooldown_minutes: 15         # Minimum time between alerts
    speed_degradation_threshold: 0.5   # Speed degradation alert threshold
    usage_quota_enabled: false         # Enable usage quota alerts
    daily_quota_gb: 0                  # Daily usage quota (0 = disabled)
    monthly_quota_gb: 0                # Monthly usage quota (0 = disabled)
```

#### Bandwidth Monitor Parameters

| Parameter | Type | Default | Range/Options | Description |
|-----------|------|---------|---------------|-------------|
| `monitoring_interval` | integer | 1000 | 100-10000 | Data collection interval in milliseconds |
| `data_retention_hours` | integer | 24 | 1-8760 | Hours to retain bandwidth data |
| `alert_threshold_mbps` | float | 100.0 | 0.1-10000.0 | Speed threshold for alerts in Mbps |
| `enable_alerts` | boolean | true | true/false | Enable bandwidth alerting |
| `monitor_interfaces` | string | "auto" | auto, interface_name, "all" | Network interfaces to monitor |
| `chart_update_interval` | integer | 2000 | 500-10000 | Chart refresh interval in milliseconds |
| `data_units` | string | "auto" | auto, bytes, bits, mbps, gbps | Display units for data |

## 🔍 Port Scanner Configuration

### `network_connectivity.port_scanner`

Configuration for port scanning functionality.

```yaml
network_connectivity:
  port_scanner:
    # Basic Scan Settings
    default_scan_type: "tcp_syn"       # Default scan technique
    common_ports: [21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 993, 995, 1723, 3306, 3389, 5432, 5900]
    scan_timeout: 3000                 # Connection timeout (ms)
    max_threads: 50                    # Maximum concurrent threads
    
    # Detection Features
    enable_service_detection: true     # Enable service detection
    enable_os_detection: false         # Enable OS fingerprinting
    enable_vulnerability_scan: false   # Enable vulnerability scanning
    enable_banner_grabbing: true       # Enable banner grabbing
    
    # Scan Behavior
    scan_delay: 0                      # Delay between scans (ms)
    randomize_scan_order: false        # Randomize port scan order
    adaptive_timing: true              # Adapt timing based on responses
    max_retries: 3                     # Maximum retry attempts
    
    # Stealth Options
    stealth_mode: false                # Enable stealth scanning
    source_port_randomization: false   # Randomize source ports
    decoy_scanning: false              # Use decoy IP addresses
    fragment_packets: false            # Fragment scan packets
    
    # Output Settings
    save_scan_results: true            # Save scan results
    export_formats: ["json", "csv", "xml"] # Available export formats
    include_closed_ports: false        # Include closed ports in results
    include_filtered_ports: true       # Include filtered ports in results
    
    # Custom Port Sets
    custom_port_ranges: []             # Custom port ranges
    exclude_ports: []                  # Ports to exclude from scans
    web_ports: [80, 443, 8080, 8443, 8000, 8888]
    database_ports: [1433, 1521, 3306, 5432, 27017]
    remote_access_ports: [22, 23, 3389, 5900, 5901]
```

#### Port Scanner Parameters

| Parameter | Type | Default | Range/Options | Description |
|-----------|------|---------|---------------|-------------|
| `default_scan_type` | string | "tcp_syn" | tcp_syn, tcp_connect, udp, tcp_ack | Default scanning technique |
| `scan_timeout` | integer | 3000 | 100-30000 | Connection timeout in milliseconds |
| `max_threads` | integer | 50 | 1-1000 | Maximum concurrent scanning threads |
| `enable_service_detection` | boolean | true | true/false | Enable service detection |
| `enable_os_detection` | boolean | false | true/false | Enable OS fingerprinting |
| `scan_delay` | integer | 0 | 0-10000 | Delay between scans in milliseconds |
| `stealth_mode` | boolean | false | true/false | Enable stealth scanning options |

## 📡 Wi-Fi Analyzer Configuration

### `network_connectivity.wifi_analyzer`

Configuration for Wi-Fi analysis functionality.

```yaml
network_connectivity:
  wifi_analyzer:
    # Scanning Settings
    scan_interval: 30000               # Network scan interval (ms)
    signal_interval: 2000              # Signal monitoring interval (ms)
    scan_type: "active"                # Scan type (active/passive)
    bands: ["2.4GHz", "5GHz"]          # Frequency bands to scan
    
    # Analysis Features
    enable_security_analysis: true     # Enable security analysis
    enable_interference_detection: true # Enable interference detection
    enable_channel_analysis: true      # Enable channel analysis
    channel_width_detection: true      # Detect channel widths
    vendor_identification: true        # Identify AP vendors
    hidden_network_detection: true     # Detect hidden networks
    
    # Data Management
    data_retention_hours: 24           # Data retention period
    max_access_points: 1000            # Maximum APs to track
    signal_history_size: 1000          # Signal history entries
    
    # Alert Settings
    enable_alerts: true                # Enable Wi-Fi alerts
    weak_signal_threshold: -70         # Weak signal threshold (dBm)
    security_alert_level: "medium"     # Security alert sensitivity
    interference_threshold: 0.7        # Interference alert threshold
    security_score_threshold: 0.5      # Security score alert threshold
    
    # Advanced Analysis
    beacon_analysis: true              # Analyze beacon frames
    probe_request_analysis: false      # Analyze probe requests
    monitor_mode_required: false       # Require monitor mode
    auto_channel_recommendation: true  # Auto channel recommendations
    
    # Export Settings
    export_format: "json"              # Default export format
    include_vendor_info: true          # Include vendor information
    include_capabilities: true         # Include AP capabilities
    real_time_updates: true            # Enable real-time updates
    update_interval: 5000              # Update interval (ms)
```

#### Wi-Fi Analyzer Parameters

| Parameter | Type | Default | Range/Options | Description |
|-----------|------|---------|---------------|-------------|
| `scan_interval` | integer | 30000 | 5000-300000 | Network scan interval in milliseconds |
| `signal_interval` | integer | 2000 | 500-10000 | Signal monitoring interval in milliseconds |
| `scan_type` | string | "active" | active, passive | Type of Wi-Fi scanning |
| `bands` | array | ["2.4GHz", "5GHz"] | 2.4GHz, 5GHz, 6GHz | Frequency bands to analyze |
| `weak_signal_threshold` | integer | -70 | -100 to -30 | Weak signal threshold in dBm |
| `security_alert_level` | string | "medium" | low, medium, high | Security alert sensitivity |

## 📁 LAN File Transfer Configuration

### `network_connectivity.lan_file_transfer`

Configuration for LAN file transfer functionality.

```yaml
network_connectivity:
  lan_file_transfer:
    # Network Settings
    discovery_port: 8765               # Device discovery port
    transfer_port: 8766                # File transfer port
    discovery_interval: 30             # Discovery broadcast interval (seconds)
    connection_timeout: 30             # Connection timeout (seconds)
    transfer_timeout: 300              # Transfer timeout (seconds)
    
    # Transfer Settings
    max_concurrent_transfers: 3        # Maximum simultaneous transfers
    default_chunk_size: 65536          # Transfer chunk size (bytes)
    enable_resume: true                # Enable transfer resume
    max_file_size_mb: 1024             # Maximum file size (MB)
    
    # Security Settings
    encryption_enabled: true           # Enable file encryption
    require_authentication: true       # Require device authentication
    auto_accept_trusted: false         # Auto-accept from trusted devices
    trust_local_network: true          # Trust local network devices
    enable_security_scanning: false    # Scan files for security
    
    # Compression Settings
    compression_enabled: false         # Enable file compression
    default_compression: "gzip"        # Default compression algorithm
    compression_level: 6               # Compression level (1-9)
    
    # File Management
    allowed_file_types: []             # Allowed file extensions (empty = all)
    blocked_file_types: [".exe", ".bat", ".cmd", ".scr"] # Blocked extensions
    default_download_path: "Downloads" # Default download directory
    keep_transfer_history: true        # Keep transfer history
    history_retention_days: 30         # History retention period
    
    # Performance Settings
    enable_bandwidth_limiting: false   # Enable bandwidth limiting
    max_upload_speed_mbps: 0           # Max upload speed (0 = unlimited)
    max_download_speed_mbps: 0         # Max download speed (0 = unlimited)
    
    # Device Settings
    device_name: ""                    # Custom device name (empty = auto)
    enable_device_discovery: true      # Enable device discovery
    enable_upnp: false                 # Enable UPnP port mapping
    firewall_auto_config: false        # Auto-configure firewall
    
    # Notification Settings
    enable_notifications: true         # Enable transfer notifications
    log_transfers: true                # Log all transfers
```

#### LAN File Transfer Parameters

| Parameter | Type | Default | Range/Options | Description |
|-----------|------|---------|---------------|-------------|
| `discovery_port` | integer | 8765 | 1024-65535 | Port for device discovery |
| `transfer_port` | integer | 8766 | 1024-65535 | Port for file transfers |
| `max_concurrent_transfers` | integer | 3 | 1-10 | Maximum simultaneous transfers |
| `default_chunk_size` | integer | 65536 | 1024-1048576 | Transfer chunk size in bytes |
| `encryption_enabled` | boolean | true | true/false | Enable file encryption |
| `compression_enabled` | boolean | false | true/false | Enable file compression |
| `max_file_size_mb` | integer | 1024 | 1-10240 | Maximum file size in MB |

## 🔒 Security Configuration

### `network_connectivity.security`

Security-related configuration options.

```yaml
network_connectivity:
  security:
    # Access Control
    require_admin_for_scans: false     # Require admin privileges for scans
    whitelist_scan_targets: []         # Allowed scan targets
    blacklist_scan_targets: ["127.0.0.1", "localhost", "::1"] # Blocked targets
    
    # Rate Limiting
    max_scan_rate: 1000                # Maximum scan rate (packets/second)
    enable_scan_logging: true          # Log all scan activities
    alert_on_suspicious_activity: true # Alert on suspicious behavior
    
    # Data Protection
    encrypt_stored_data: false         # Encrypt stored data
    data_retention_policy: "30_days"   # Data retention policy
    audit_trail_enabled: true          # Enable audit trail
    secure_delete_enabled: false       # Secure delete temporary files
    
    # Security Level
    security_level: "moderate"         # Overall security level
    enforce_https: false               # Enforce HTTPS for web interfaces
    certificate_validation: true       # Validate SSL certificates
    
    # Authentication
    enable_api_authentication: false   # Require API authentication
    api_key_required: false            # Require API key
    session_timeout_minutes: 60        # Session timeout
    
    # Compliance
    gdpr_compliance: false             # GDPR compliance mode
    hipaa_compliance: false            # HIPAA compliance mode
    anonymize_logs: false              # Anonymize log data
```

#### Security Parameters

| Parameter | Type | Default | Range/Options | Description |
|-----------|------|---------|---------------|-------------|
| `security_level` | string | "moderate" | strict, moderate, permissive | Overall security level |
| `max_scan_rate` | integer | 1000 | 1-10000 | Maximum scan rate in packets per second |
| `data_retention_policy` | string | "30_days" | 7_days, 30_days, 90_days, 1_year | Data retention policy |
| `session_timeout_minutes` | integer | 60 | 5-1440 | Session timeout in minutes |

## 🚀 Performance Configuration

### `network_connectivity.performance`

Performance tuning options.

```yaml
network_connectivity:
  performance:
    # Resource Limits
    enable_performance_monitoring: true # Monitor performance metrics
    max_memory_usage_mb: 512           # Maximum memory usage (MB)
    max_cpu_usage_percent: 25          # Maximum CPU usage (%)
    
    # Threading
    thread_pool_size: "auto"           # Thread pool size
    enable_background_operations: true # Enable background processing
    priority_level: "normal"           # Process priority level
    
    # Caching
    cache_size_mb: 64                  # Cache size (MB)
    enable_compression: true           # Enable data compression
    cache_cleanup_interval: 3600       # Cache cleanup interval (seconds)
    
    # Optimization
    operation_timeout_multiplier: 1.0  # Timeout multiplier
    adaptive_performance: true         # Adapt performance based on system
    low_power_mode: false              # Enable low power mode
    
    # Database
    database_cache_size_mb: 32         # Database cache size
    database_checkpoint_interval: 300  # Database checkpoint interval (seconds)
    vacuum_database_on_startup: false  # Vacuum database on startup
```

#### Performance Parameters

| Parameter | Type | Default | Range/Options | Description |
|-----------|------|---------|---------------|-------------|
| `max_memory_usage_mb` | integer | 512 | 64-4096 | Maximum memory usage in MB |
| `max_cpu_usage_percent` | integer | 25 | 1-100 | Maximum CPU usage percentage |
| `thread_pool_size` | string/integer | "auto" | auto, 1-100 | Thread pool size |
| `cache_size_mb` | integer | 64 | 16-1024 | Cache size in MB |
| `priority_level` | string | "normal" | low, normal, high | Process priority level |

## 📝 Logging Configuration

### `network_connectivity.logging`

Logging system configuration.

```yaml
network_connectivity:
  logging:
    # Basic Settings
    enable_logging: true               # Enable logging system
    log_level: "INFO"                  # Minimum log level
    log_to_file: true                  # Write logs to file
    log_to_console: false              # Write logs to console
    
    # File Settings
    log_file_path: "logs/network_connectivity.log" # Log file path
    max_log_file_size_mb: 10           # Maximum log file size
    log_file_rotation_count: 5         # Number of rotated log files
    
    # Advanced Logging
    enable_structured_logging: true    # Use structured logging format
    include_timestamps: true           # Include timestamps in logs
    include_thread_info: false         # Include thread information
    include_process_info: false        # Include process information
    
    # Log Categories
    network_operations: "INFO"         # Network operation logs
    security_events: "WARNING"         # Security event logs
    performance_metrics: "DEBUG"       # Performance metric logs
    error_tracking: "ERROR"            # Error tracking logs
    
    # External Logging
    syslog_enabled: false              # Enable syslog integration
    syslog_server: ""                  # Syslog server address
    remote_logging_enabled: false      # Enable remote logging
    log_aggregation_url: ""            # Log aggregation service URL
```

## 🔔 Notification Configuration

### `network_connectivity.notifications`

Notification system configuration.

```yaml
network_connectivity:
  notifications:
    # Basic Settings
    enable_notifications: true         # Enable notification system
    notification_sound: true           # Play notification sounds
    show_desktop_notifications: true   # Show desktop notifications
    
    # Email Notifications
    email_enabled: false               # Enable email notifications
    smtp_server: ""                    # SMTP server address
    smtp_port: 587                     # SMTP server port
    smtp_username: ""                  # SMTP username
    smtp_password: ""                  # SMTP password
    smtp_use_tls: true                 # Use TLS encryption
    from_address: ""                   # From email address
    to_addresses: []                   # Recipient email addresses
    
    # Webhook Notifications
    webhook_enabled: false             # Enable webhook notifications
    webhook_url: ""                    # Webhook URL
    webhook_timeout: 10                # Webhook timeout (seconds)
    webhook_retry_count: 3             # Webhook retry attempts
    
    # Notification Filtering
    min_severity_level: "INFO"         # Minimum severity for notifications
    rate_limiting_enabled: true        # Enable notification rate limiting
    max_notifications_per_hour: 60     # Maximum notifications per hour
    
    # Custom Notifications
    custom_notification_script: ""     # Custom notification script path
    notification_templates: {}         # Custom notification templates
```

## 🔧 Configuration Management

### Configuration Profiles

Create and manage multiple configuration profiles for different environments.

```yaml
# Example profile configuration
profiles:
  development:
    network_connectivity:
      general:
        log_level: "DEBUG"
        enable_notifications: false
      port_scanner:
        max_threads: 10
        stealth_mode: false
  
  production:
    network_connectivity:
      general:
        log_level: "WARNING"
        enable_notifications: true
      port_scanner:
        max_threads: 25
        stealth_mode: true
      security:
        security_level: "strict"
  
  testing:
    network_connectivity:
      general:
        log_level: "INFO"
        auto_save_results: false
      performance:
        max_memory_usage_mb: 256
```

### Environment Variables

Override configuration using environment variables:

```bash
# General settings
export NC_DEFAULT_TIMEOUT=10000
export NC_LOG_LEVEL=DEBUG
export NC_ENABLE_LOGGING=true

# Tool-specific settings
export NC_BANDWIDTH_MONITOR_INTERVAL=500
export NC_PORT_SCANNER_MAX_THREADS=100
export NC_WIFI_ANALYZER_SCAN_INTERVAL=15000

# Security settings
export NC_SECURITY_LEVEL=strict
export NC_REQUIRE_ADMIN_FOR_SCANS=true
```

### Configuration Validation

The toolkit automatically validates configuration on startup:

```python
# Example validation errors
validation_errors = [
    "bandwidth_monitor.monitoring_interval must be between 100 and 10000",
    "port_scanner.max_threads must be between 1 and 1000",
    "security.security_level must be one of: strict, moderate, permissive"
]
```

### Configuration Migration

Automatic migration between configuration versions:

```yaml
# Migration example from v1.1 to v1.2
migration:
  from_version: "1.1.0"
  to_version: "1.2.0"
  changes:
    - action: "rename"
      from: "bandwidth_monitor.update_interval"
      to: "bandwidth_monitor.chart_update_interval"
    - action: "add"
      key: "wifi_analyzer.enable_channel_analysis"
      default: true
    - action: "remove"
      key: "deprecated_setting"
```

## 📋 Configuration Examples

### Minimal Configuration
```yaml
network_connectivity:
  general:
    default_timeout: 5000
    enable_logging: true
  bandwidth_monitor:
    monitoring_interval: 1000
  port_scanner:
    default_scan_type: "tcp_connect"
```

### High-Performance Configuration
```yaml
network_connectivity:
  general:
    max_concurrent_operations: 50
  bandwidth_monitor:
    monitoring_interval: 500
    enable_real_time_chart: true
  port_scanner:
    max_threads: 100
    adaptive_timing: true
  performance:
    max_memory_usage_mb: 1024
    thread_pool_size: 20
```

### Security-Focused Configuration
```yaml
network_connectivity:
  security:
    security_level: "strict"
    require_admin_for_scans: true
    encrypt_stored_data: true
    audit_trail_enabled: true
  port_scanner:
    stealth_mode: true
    enable_vulnerability_scan: true
  lan_file_transfer:
    encryption_enabled: true
    require_authentication: true
    enable_security_scanning: true
```

---

**For more configuration examples:** See the **[Configuration Guide](../user_guide/configuration_guide.md)** and **[Examples](../examples/configuration_examples.md)**.