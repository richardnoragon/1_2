# Network Connectivity Module - Integration Guide

**Document Version:** 1.0  
**Date:** 2025-07-26  
**Companion to:** network_connectivity_architecture.md

## Integration Points and Shared Components

### 1. Core Framework Integration Points

#### 1.1 Configuration System Integration

**Integration Point:** [`core/config_manager.py`](core/config_manager.py:15)

```python
# Configuration Bridge Implementation
class NetworkConfigBridge:
    """Bridge between network tools and main configuration system."""
    
    def __init__(self):
        self.main_config = ConfigManager()
        self._ensure_network_section()
    
    def _ensure_network_section(self):
        """Ensure network_connectivity section exists."""
        if 'network_connectivity' not in self.main_config.config:
            default_config = {
                "general": {
                    "default_timeout": 5000,
                    "max_concurrent_operations": 10,
                    "enable_logging": True,
                    "log_level": "INFO"
                }
            }
            self.main_config.set_setting('network_connectivity', 'general', default_config['general'])
    
    def get_tool_setting(self, tool_name: str, key: str, default=None):
        """Get setting for specific network tool."""
        return self.main_config.get_setting('network_connectivity', f'{tool_name}.{key}', default)
    
    def set_tool_setting(self, tool_name: str, key: str, value):
        """Set setting for specific network tool."""
        current_config = self.main_config.get_setting('network_connectivity', tool_name, {})
        current_config[key] = value
        self.main_config.set_setting('network_connectivity', tool_name, current_config)
```

**Shared Configuration Components:**
- **Timeout Management:** Unified timeout handling across all network tools
- **Logging Configuration:** Centralized logging level and format settings
- **Resource Limits:** Shared resource allocation and throttling settings
- **Security Settings:** Common security policies and validation rules

#### 1.2 Logging System Integration

**Integration Point:** [`core/logging_manager.py`](core/logging_manager.py:9)

```python
# Logging Bridge Implementation
def setup_network_logger(tool_name: str):
    """Set up logger for network connectivity tools."""
    logger_name = f'NetworkConnectivity.{tool_name}'
    logger = LogManager().get_logger(logger_name)
    
    # Add network-specific context
    logger.info(f"Initializing {tool_name} network tool")
    return logger

# Usage in network tools
class ConnectivityTester(NetworkToolBase):
    def __init__(self):
        super().__init__("ConnectivityTester")
        self.logger = setup_network_logger("ConnectivityTester")
```

**Shared Logging Components:**
- **Log Categories:** Hierarchical logging under NetworkConnectivity namespace
- **Context Information:** Network-specific context (IP addresses, protocols, etc.)
- **Performance Metrics:** Standardized performance logging format
- **Error Correlation:** Consistent error tracking and correlation IDs

#### 1.3 Error Handling Integration

**Integration Point:** [`core/error_handler.py`](core/error_handler.py:12)

```python
# Error Handling Bridge
class NetworkErrorHandler:
    """Network-specific error handling with RFU integration."""
    
    @staticmethod
    def handle_network_error(error: Exception, operation: str, 
                           network_context: dict = None):
        """Handle network errors with appropriate context."""
        context = {
            'module': 'network_connectivity',
            'operation': operation,
            'network_info': network_context or {}
        }
        
        # Add network-specific error details
        if hasattr(error, 'errno'):
            context['network_errno'] = error.errno
        if hasattr(error, 'strerror'):
            context['network_error'] = error.strerror
            
        return error_handler.handle_error(
            error,
            f"network connectivity {operation}",
            context=context,
            show_dialog=True
        )
```

**Shared Error Handling Components:**
- **Network Exception Types:** Standardized network error classifications
- **Recovery Strategies:** Common error recovery and retry mechanisms
- **User Notifications:** Consistent error messaging and user guidance
- **Diagnostic Information:** Network-specific diagnostic data collection

### 2. GUI Framework Integration Points

#### 2.1 Base Window Integration

**Integration Point:** [`gui/common/base_window.py`](gui/common/base_window.py:16)

```python
# Network Tools Hub Window
class NetworkConnectivityHub(BaseWindow):
    """Main hub for network connectivity tools."""
    
    def __init__(self):
        super().__init__("Network Connectivity Tools")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)
        
        # Initialize network tools
        self.tools = {
            'connectivity': ConnectivityTesterWidget(),
            'bandwidth': BandwidthMonitorWidget(),
            'port_scanner': PortScannerWidget(),
            'diagnostics': NetworkDiagnosticsWidget()
        }
        
        self._setup_ui()
        self.apply_theme()  # Inherit theme from BaseWindow
    
    def _setup_ui(self):
        """Setup the tabbed interface for network tools."""
        self.tab_widget = QTabWidget()
        
        # Add tool tabs
        for tool_name, widget in self.tools.items():
            self.tab_widget.addTab(widget, widget.get_display_name())
        
        # Set as central widget
        self.setCentralWidget(self.tab_widget)
```

**Shared GUI Components:**
- **Window Management:** Consistent window behavior and lifecycle
- **Menu Integration:** Standard menu structure and actions
- **Status Bar:** Unified status reporting across tools
- **Progress Tracking:** Common progress indication patterns

#### 2.2 Theme System Integration

**Integration Point:** [`gui/themes.py`](gui/themes.py:231)

```python
# Network-specific theme extensions
class NetworkThemeExtensions:
    """Theme extensions for network connectivity tools."""
    
    @staticmethod
    def get_network_styles():
        """Get network-specific style extensions."""
        return {
            "ConnectivityStatus": """
                QLabel[status="connected"] {
                    color: #4CAF50;
                    font-weight: bold;
                }
                QLabel[status="disconnected"] {
                    color: #f44336;
                    font-weight: bold;
                }
                QLabel[status="testing"] {
                    color: #FFC107;
                    font-weight: bold;
                }
            """,
            "BandwidthChart": """
                QWidget {
                    background-color: white;
                    border: 1px solid #dcdcdc;
                    border-radius: 4px;
                }
            """,
            "PortScanResults": """
                QTableView::item[port_status="open"] {
                    background-color: #e8f5e8;
                }
                QTableView::item[port_status="closed"] {
                    background-color: #ffeaea;
                }
            """
        }
```

**Shared Theme Components:**
- **Color Schemes:** Network status color coding (connected/disconnected/testing)
- **Icon Sets:** Standardized network-related icons
- **Chart Styling:** Consistent styling for network data visualization
- **Status Indicators:** Common visual patterns for network states

### 3. Cross-Module Communication

#### 3.1 Event System Integration

```python
# Network Event System
class NetworkEventManager(QObject):
    """Manages network-related events across the application."""
    
    # Global network events
    network_status_changed = pyqtSignal(str, bool)  # interface, connected
    bandwidth_threshold_exceeded = pyqtSignal(str, float)  # interface, usage
    security_alert = pyqtSignal(str, str)  # alert_type, message
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def emit_network_status(self, interface: str, connected: bool):
        """Emit network status change event."""
        self.network_status_changed.emit(interface, connected)
    
    def emit_bandwidth_alert(self, interface: str, usage: float):
        """Emit bandwidth threshold exceeded event."""
        self.bandwidth_threshold_exceeded.emit(interface, usage)
```

#### 3.2 Data Sharing Integration

```python
# Network Data Cache
class NetworkDataCache:
    """Shared cache for network data across tools."""
    
    def __init__(self):
        self._cache = {}
        self._cache_timeout = 30  # seconds
        self._last_update = {}
    
    def get_network_interfaces(self) -> List[dict]:
        """Get cached network interface information."""
        if self._is_cache_valid('interfaces'):
            return self._cache.get('interfaces', [])
        
        # Refresh cache
        interfaces = self._collect_network_interfaces()
        self._cache['interfaces'] = interfaces
        self._last_update['interfaces'] = time.time()
        return interfaces
    
    def get_active_connections(self) -> List[dict]:
        """Get cached active network connections."""
        if self._is_cache_valid('connections'):
            return self._cache.get('connections', [])
        
        # Refresh cache
        connections = self._collect_active_connections()
        self._cache['connections'] = connections
        self._last_update['connections'] = time.time()
        return connections
```

## Configuration Schema Definition

### Complete Configuration Schema

```json
{
  "network_connectivity": {
    "general": {
      "default_timeout": 5000,
      "max_concurrent_operations": 10,
      "enable_logging": true,
      "log_level": "INFO",
      "auto_save_results": true,
      "results_retention_days": 30,
      "enable_notifications": true,
      "notification_sound": true,
      "data_cache_timeout": 30,
      "max_history_entries": 1000
    },
    "connectivity_tester": {
      "default_ping_count": 4,
      "default_ping_size": 32,
      "default_ping_interval": 1000,
      "default_hosts": [
        "8.8.8.8",
        "1.1.1.1",
        "google.com",
        "cloudflare.com"
      ],
      "traceroute_max_hops": 30,
      "traceroute_timeout": 5000,
      "dns_servers": [
        "8.8.8.8",
        "1.1.1.1",
        "208.67.222.222"
      ],
      "http_test_urls": [
        "https://www.google.com",
        "https://www.cloudflare.com",
        "https://httpbin.org/get"
      ],
      "enable_ipv6_testing": true,
      "save_ping_history": true,
      "alert_on_failure": true,
      "failure_threshold": 3
    },
    "bandwidth_monitor": {
      "monitoring_interval": 1000,
      "data_retention_hours": 24,
      "alert_threshold_mbps": 100,
      "enable_alerts": true,
      "monitor_interfaces": "auto",
      "chart_update_interval": 2000,
      "enable_real_time_chart": true,
      "show_upload_download_separate": true,
      "data_units": "auto",
      "enable_application_monitoring": false,
      "alert_email": "",
      "peak_detection_enabled": true,
      "baseline_calculation_hours": 168
    },
    "port_scanner": {
      "default_scan_type": "tcp",
      "common_ports": [
        21, 22, 23, 25, 53, 80, 110, 135, 139, 143,
        443, 993, 995, 1723, 3306, 3389, 5432, 5900
      ],
      "scan_timeout": 3000,
      "max_threads": 50,
      "enable_service_detection": true,
      "enable_os_detection": false,
      "enable_vulnerability_scan": false,
      "scan_delay": 0,
      "randomize_scan_order": false,
      "save_scan_results": true,
      "export_formats": ["json", "csv", "xml"],
      "stealth_mode": false,
      "custom_port_ranges": [],
      "exclude_ports": [],
      "enable_banner_grabbing": true
    },
    "network_diagnostics": {
      "include_system_info": true,
      "include_network_config": true,
      "include_route_table": true,
      "include_dns_config": true,
      "include_firewall_status": true,
      "include_active_connections": true,
      "include_network_adapters": true,
      "include_wireless_info": true,
      "generate_recommendations": true,
      "auto_fix_suggestions": false,
      "detailed_analysis": true,
      "include_performance_metrics": true,
      "save_diagnostic_reports": true,
      "report_format": "html",
      "include_screenshots": false,
      "anonymize_sensitive_data": true
    },
    "security": {
      "require_admin_for_scans": false,
      "whitelist_scan_targets": [],
      "blacklist_scan_targets": [
        "127.0.0.1",
        "localhost",
        "::1"
      ],
      "max_scan_rate": 1000,
      "enable_scan_logging": true,
      "alert_on_suspicious_activity": true,
      "encrypt_stored_data": false,
      "data_retention_policy": "30_days",
      "audit_trail_enabled": true
    },
    "performance": {
      "enable_performance_monitoring": true,
      "max_memory_usage_mb": 512,
      "max_cpu_usage_percent": 25,
      "operation_timeout_multiplier": 1.0,
      "enable_background_operations": true,
      "priority_level": "normal",
      "thread_pool_size": "auto",
      "cache_size_mb": 64,
      "enable_compression": true
    }
  }
}
```

### Configuration Validation Schema

```python
# Configuration validation rules
NETWORK_CONFIG_SCHEMA = {
    "general": {
        "default_timeout": {"type": int, "min": 1000, "max": 60000},
        "max_concurrent_operations": {"type": int, "min": 1, "max": 100},
        "enable_logging": {"type": bool},
        "log_level": {"type": str, "choices": ["DEBUG", "INFO", "WARNING", "ERROR"]},
        "results_retention_days": {"type": int, "min": 1, "max": 365}
    },
    "connectivity_tester": {
        "default_ping_count": {"type": int, "min": 1, "max": 100},
        "default_ping_size": {"type": int, "min": 8, "max": 65507},
        "traceroute_max_hops": {"type": int, "min": 1, "max": 255},
        "default_hosts": {"type": list, "min_items": 1}
    },
    "bandwidth_monitor": {
        "monitoring_interval": {"type": int, "min": 100, "max": 10000},
        "alert_threshold_mbps": {"type": float, "min": 0.1, "max": 10000},
        "data_retention_hours": {"type": int, "min": 1, "max": 8760}
    },
    "port_scanner": {
        "scan_timeout": {"type": int, "min": 100, "max": 30000},
        "max_threads": {"type": int, "min": 1, "max": 1000},
        "common_ports": {"type": list, "item_type": int}
    }
}
```

## GUI Component Hierarchy and Theming

### GUI Component Structure

```
NetworkConnectivityHub (BaseWindow)
├── QTabWidget (main_tabs)
│   ├── ConnectivityTesterWidget
│   │   ├── QGroupBox (ping_group)
│   │   │   ├── QLineEdit (target_host)
│   │   │   ├── QSpinBox (ping_count)
│   │   │   └── QPushButton (start_ping)
│   │   ├── QGroupBox (traceroute_group)
│   │   │   ├── QLineEdit (trace_target)
│   │   │   └── QPushButton (start_trace)
│   │   ├── QGroupBox (dns_group)
│   │   │   ├── QLineEdit (dns_query)
│   │   │   └── QPushButton (resolve_dns)
│   │   └── QTextEdit (results_display)
│   ├── BandwidthMonitorWidget
│   │   ├── QGroupBox (monitoring_controls)
│   │   │   ├── QComboBox (interface_selector)
│   │   │   ├── QPushButton (start_monitoring)
│   │   │   └── QPushButton (stop_monitoring)
│   │   ├── QGroupBox (real_time_chart)
│   │   │   └── NetworkChartWidget (custom)
│   │   ├── QGroupBox (statistics)
│   │   │   ├── QLabel (current_download)
│   │   │   ├── QLabel (current_upload)
│   │   │   ├── QLabel (peak_download)
│   │   │   └── QLabel (peak_upload)
│   │   └── QTableView (history_table)
│   ├── PortScannerWidget
│   │   ├── QGroupBox (scan_configuration)
│   │   │   ├── QLineEdit (target_host)
│   │   │   ├── QLineEdit (port_range)
│   │   │   ├── QComboBox (scan_type)
│   │   │   └── QPushButton (start_scan)
│   │   ├── QGroupBox (scan_options)
│   │   │   ├── QCheckBox (service_detection)
│   │   │   ├── QCheckBox (os_detection)
│   │   │   └── QSpinBox (thread_count)
│   │   ├── QProgressBar (scan_progress)
│   │   └── QTableView (results_table)
│   └── NetworkDiagnosticsWidget
│       ├── QGroupBox (diagnostic_options)
│       │   ├── QCheckBox (include_system_info)
│       │   ├── QCheckBox (include_network_config)
│       │   ├── QCheckBox (include_route_table)
│       │   └── QPushButton (run_diagnostics)
│       ├── QProgressBar (diagnostic_progress)
│       ├── QTabWidget (results_tabs)
│       │   ├── QTextEdit (system_info_tab)
│       │   ├── QTextEdit (network_config_tab)
│       │   ├── QTableView (route_table_tab)
│       │   └── QTextEdit (recommendations_tab)
│       └── QPushButton (export_report)
└── QStatusBar (status_bar)
    ├── QLabel (connection_status)
    ├── QProgressBar (operation_progress)
    └── QLabel (tool_status)
```

### Theme Integration Specifications

#### Network-Specific Color Scheme

```python
# Network status colors
NETWORK_COLORS = {
    "connected": "#4CAF50",      # Green
    "disconnected": "#f44336",   # Red
    "testing": "#FFC107",        # Amber
    "unknown": "#9E9E9E",        # Gray
    "warning": "#FF9800",        # Orange
    "error": "#D32F2F",          # Dark Red
    "success": "#388E3C",        # Dark Green
    "info": "#1976D2"            # Blue
}

# Bandwidth visualization colors
BANDWIDTH_COLORS = {
    "download": "#2196F3",       # Blue
    "upload": "#4CAF50",         # Green
    "total": "#9C27B0",          # Purple
    "background": "#F5F5F5",     # Light Gray
    "grid": "#E0E0E0"            # Gray
}

# Port scan result colors
PORT_COLORS = {
    "open": "#4CAF50",           # Green
    "closed": "#f44336",         # Red
    "filtered": "#FF9800",       # Orange
    "unknown": "#9E9E9E"         # Gray
}
```

#### Custom Widget Styling

```python
# Network-specific widget styles
NETWORK_WIDGET_STYLES = {
    "NetworkStatusLabel": """
        QLabel {
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: bold;
        }
        QLabel[status="connected"] {
            background-color: #E8F5E8;
            color: #2E7D32;
            border: 1px solid #4CAF50;
        }
        QLabel[status="disconnected"] {
            background-color: #FFEBEE;
            color: #C62828;
            border: 1px solid #f44336;
        }
        QLabel[status="testing"] {
            background-color: #FFF8E1;
            color: #F57C00;
            border: 1px solid #FFC107;
        }
    """,
    
    "NetworkChartWidget": """
        QWidget {
            background-color: white;
            border: 1px solid #E0E0E0;
            border-radius: 4px;
        }
    """,
    
    "PortScanTable": """
        QTableView {
            gridline-color: #E0E0E0;
            selection-background-color: #E3F2FD;
        }
        QTableView::item[port_status="open"] {
            background-color: #E8F5E8;
        }
        QTableView::item[port_status="closed"] {
            background-color: #FFEBEE;
        }
        QTableView::item[port_status="filtered"] {
            background-color: #FFF3E0;
        }
    """,
    
    "NetworkProgressBar": """
        QProgressBar {
            border: 1px solid #E0E0E0;
            border-radius: 4px;
            text-align: center;
            background-color: #F5F5F5;
        }
        QProgressBar::chunk {
            background-color: #2196F3;
            border-radius: 3px;
        }
    """
}
```

#### Icon Integration

```python
# Network tool icons
NETWORK_ICONS = {
    "connectivity_tester": "network-test.png",
    "bandwidth_monitor": "bandwidth.png",
    "port_scanner": "port-scan.png",
    "network_diagnostics": "network-diagnostic.png",
    "connected": "connected.png",
    "disconnected": "disconnected.png",
    "testing": "testing.png",
    "scan_running": "scan-running.png",
    "scan_complete": "scan-complete.png",
    "export": "export.png",
    "settings": "settings.png",
    "refresh": "refresh.png",
    "stop": "stop.png",
    "start": "start.png"
}
```

### Responsive Design Considerations

#### Window Sizing and Layout

```python
# Responsive layout specifications
LAYOUT_SPECIFICATIONS = {
    "minimum_window_size": (1000, 700),
    "preferred_window_size": (1200, 800),
    "maximum_window_size": (1920, 1080),
    
    "tab_minimum_height": 500,
    "chart_minimum_size": (400, 200),
    "table_minimum_height": 200,
    
    "responsive_breakpoints": {
        "small": 1000,   # Compact layout
        "medium": 1200,  # Standard layout
        "large": 1600    # Expanded layout
    }
}
```

#### Adaptive UI Elements

```python
# Adaptive UI behavior
class NetworkUIAdapter:
    """Adapts UI elements based on window size and content."""
    
    def adapt_layout(self, window_width: int, window_height: int):
        """Adapt layout based on window dimensions."""
        if window_width < 1200:
            # Compact layout
            self.use_vertical_tabs()
            self.hide_secondary_panels()
        elif window_width > 1600:
            # Expanded layout
            self.show_side_panels()
            self.use_multi_column_layout()
        else:
            # Standard layout
            self.use_standard_layout()
    
    def adapt_chart_size(self, available_space: tuple):
        """Adapt chart dimensions to available space."""
        width, height = available_space
        chart_width = min(width - 40, 800)  # Leave margin
        chart_height = min(height - 100, 400)  # Leave space for controls
        return (chart_width, chart_height)
```

---

## Summary

This integration guide provides comprehensive specifications for:

1. **Integration Points:** Detailed connection points with RFU core systems
2. **Shared Components:** Reusable components across network tools
3. **Configuration Schema:** Complete configuration structure and validation
4. **GUI Hierarchy:** Detailed component structure and relationships
5. **Theme Integration:** Network-specific styling and visual elements

These specifications ensure seamless integration with the existing RFU architecture while maintaining consistency and extensibility for future enhancements.