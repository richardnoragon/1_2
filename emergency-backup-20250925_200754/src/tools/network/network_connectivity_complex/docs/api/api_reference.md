# API Reference

**Version:** 1.2.0  
**Last Updated:** 2025-07-26  
**Compatibility:** Network Connectivity Toolkit v1.2.0+

## Overview

The Network Connectivity Toolkit provides a comprehensive Python API for programmatic access to all network analysis and monitoring capabilities. This reference documents all public classes, methods, and interfaces available for integration and automation.

## 📚 API Structure

### Core Modules
- **[`network_connectivity.core`](#core-api)** - Base classes and core functionality
- **[`network_connectivity.tools`](#tools-api)** - Network analysis tools
- **[`network_connectivity.config`](#configuration-api)** - Configuration management
- **[`network_connectivity.gui`](#gui-api)** - Graphical user interface components

### Service Modules
- **[`network_connectivity.services`](#services-api)** - Shared services (logging, config, etc.)
- **[`network_connectivity.integration`](#integration-api)** - System integration utilities
- **[`network_connectivity.utils`](#utilities-api)** - Utility functions and helpers

## 🔧 Core API

### NetworkToolBase

Base class for all network connectivity tools.

```python
from network_connectivity.core.network_base import NetworkToolBase, NetworkOperationStatus

class NetworkToolBase(QObject, ABC):
    """Base class for all network connectivity tools."""
    
    # Signals
    progress_updated = pyqtSignal(int, int, str)  # current, total, message
    operation_complete = pyqtSignal(object)       # NetworkOperationResult
    error_occurred = pyqtSignal(str)              # error message
    status_changed = pyqtSignal(str)              # status message
    data_updated = pyqtSignal(dict)               # real-time data updates
    alert_triggered = pyqtSignal(str, str, str)   # level, type, message
```

#### Constructor
```python
def __init__(self, tool_name: str):
    """Initialize the network tool.
    
    Args:
        tool_name: Name of the network tool
    """
```

#### Abstract Methods
```python
@abstractmethod
def execute_operation(self, **kwargs) -> NetworkOperationResult:
    """Execute the network operation."""
    
@abstractmethod
def get_supported_protocols(self) -> List[str]:
    """Get list of supported network protocols."""
    
@abstractmethod
def validate_parameters(self, **kwargs) -> bool:
    """Validate operation parameters."""
    
@abstractmethod
def get_health_status(self) -> Dict[str, Any]:
    """Get the current health status of the tool."""
```

#### Public Methods
```python
def start_operation(self, operation_type: str, **kwargs) -> bool:
    """Start a network operation."""
    
def stop_operation(self) -> bool:
    """Stop the current operation."""
    
def get_tool_config(self, key: str, default: Any = None) -> Any:
    """Get tool-specific configuration value."""
    
def set_tool_config(self, key: str, value: Any):
    """Set tool-specific configuration value."""
    
def get_current_data(self) -> Dict[str, Any]:
    """Get the current data."""
    
def get_historical_data(self, start_time: Optional[datetime] = None, 
                       end_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
    """Get historical data."""
```

#### Properties
```python
@property
def is_running(self) -> bool:
    """Check if the tool is running."""
    
@property
def is_healthy(self) -> bool:
    """Check if the tool is healthy."""
```

### NetworkOperationResult

Data class representing the result of a network operation.

```python
@dataclass
class NetworkOperationResult:
    """Result of a network operation."""
    success: bool
    operation_type: str
    data: Dict[str, Any]
    error_message: Optional[str] = None
    timestamp: Optional[datetime] = None
    duration_ms: Optional[float] = None
```

### NetworkOperationStatus

Enumeration of network operation status states.

```python
class NetworkOperationStatus(Enum):
    """Enumeration of network operation status states."""
    IDLE = "idle"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    COMPLETED = "completed"
    ERROR = "error"
```

## 🛠️ Tools API

### BandwidthMonitor

Real-time network bandwidth monitoring tool.

```python
from network_connectivity.tools.bandwidth_monitor import BandwidthMonitor

class BandwidthMonitor(NetworkToolBase):
    """Real-time network bandwidth monitoring tool."""
```

#### Constructor
```python
def __init__(self):
    """Initialize bandwidth monitor."""
```

#### Public Methods
```python
def start_monitoring(self, interface: str = "auto", interval: int = 1000) -> bool:
    """Start bandwidth monitoring.
    
    Args:
        interface: Network interface to monitor ("auto" for automatic selection)
        interval: Monitoring interval in milliseconds
        
    Returns:
        bool: True if started successfully
    """

def stop_monitoring() -> bool:
    """Stop bandwidth monitoring."""

def get_interfaces() -> List[Dict[str, Any]]:
    """Get available network interfaces."""

def get_current_speed() -> Dict[str, float]:
    """Get current upload/download speeds."""

def get_usage_statistics(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
    """Get usage statistics for time period."""

def configure_alert(self, alert_type: str, **kwargs) -> bool:
    """Configure bandwidth alerts."""

def export_data(self, start_time: datetime, end_time: datetime, 
               format: str = "csv", filename: str = None) -> str:
    """Export bandwidth data."""
```

#### Example Usage
```python
# Create and configure monitor
monitor = BandwidthMonitor()

# Start monitoring
monitor.start_monitoring(interface="eth0", interval=1000)

# Get current data
current_data = monitor.get_current_data()
print(f"Download: {current_data['download_speed']} Mbps")

# Configure alerts
monitor.configure_alert(
    alert_type="speed_threshold",
    threshold=100,  # Mbps
    direction="download"
)

# Stop monitoring
monitor.stop_monitoring()
```

### PortScanner

Comprehensive port scanning and security analysis tool.

```python
from network_connectivity.tools.port_scanner import PortScanner

class PortScanner(NetworkToolBase):
    """Comprehensive port scanning and security analysis tool."""
```

#### Constructor
```python
def __init__(self):
    """Initialize port scanner."""
```

#### Public Methods
```python
def scan(self, target: str, ports: str = "1-1000", 
         scan_type: str = "tcp_syn", **kwargs) -> Dict[str, Any]:
    """Perform port scan.
    
    Args:
        target: Target IP address, hostname, or network range
        ports: Port specification (e.g., "80", "1-1000", "80,443,8080")
        scan_type: Scan technique ("tcp_syn", "tcp_connect", "udp")
        **kwargs: Additional scan options
        
    Returns:
        Dict containing scan results
    """

def quick_scan(self, target: str) -> Dict[str, Any]:
    """Perform quick scan of common ports."""

def scan_network(self, network: str, ports: str = "22,80,443") -> Dict[str, Any]:
    """Scan multiple hosts in network range."""

def detect_services(self, target: str, ports: List[int]) -> Dict[int, Dict[str, Any]]:
    """Detect services on specified ports."""

def analyze_security(self, scan_results: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze security posture from scan results."""

def generate_report(self, results: Dict[str, Any], format: str = "html") -> str:
    """Generate scan report."""
```

#### Example Usage
```python
# Create scanner
scanner = PortScanner()

# Perform quick scan
results = scanner.quick_scan("192.168.1.1")

# Full scan with service detection
full_results = scanner.scan(
    target="192.168.1.1",
    ports="1-65535",
    scan_type="tcp_syn",
    enable_service_detection=True
)

# Security analysis
security_report = scanner.analyze_security(full_results)
print(f"Security Score: {security_report['score']}/100")

# Generate report
report = scanner.generate_report(full_results, format="html")
```

### WiFiAnalyzer

Wireless network analysis and monitoring tool.

```python
from network_connectivity.tools.wifi_analyzer import WiFiAnalyzer

class WiFiAnalyzer(NetworkToolBase):
    """Wireless network analysis and monitoring tool."""
```

#### Constructor
```python
def __init__(self):
    """Initialize Wi-Fi analyzer."""
```

#### Public Methods
```python
def start_scanning(self, scan_interval: int = 30000, **kwargs) -> bool:
    """Start Wi-Fi network scanning.
    
    Args:
        scan_interval: Scan interval in milliseconds
        **kwargs: Additional scan options
        
    Returns:
        bool: True if started successfully
    """

def stop_scanning() -> bool:
    """Stop Wi-Fi scanning."""

def get_networks() -> List[Dict[str, Any]]:
    """Get discovered Wi-Fi networks."""

def get_network_by_ssid(self, ssid: str) -> Optional[Dict[str, Any]]:
    """Get specific network by SSID."""

def analyze_channels(self, band: str = "2.4GHz") -> Dict[str, Any]:
    """Analyze channel utilization."""

def get_channel_recommendations(self, band: str = "2.4GHz") -> List[int]:
    """Get optimal channel recommendations."""

def assess_security(self, network: Dict[str, Any]) -> Dict[str, Any]:
    """Assess network security."""

def monitor_signal(self, ssid: str, duration: int = 300) -> List[Dict[str, Any]]:
    """Monitor signal strength for specific network."""
```

#### Example Usage
```python
# Create analyzer
analyzer = WiFiAnalyzer()

# Start scanning
analyzer.start_scanning(scan_interval=30000)

# Get networks
networks = analyzer.get_networks()
for network in networks:
    print(f"SSID: {network['ssid']}, Signal: {network['signal_strength']} dBm")

# Channel analysis
channel_analysis = analyzer.analyze_channels(band="5GHz")
recommendations = analyzer.get_channel_recommendations(band="5GHz")

# Security assessment
for network in networks:
    security = analyzer.assess_security(network)
    print(f"{network['ssid']}: Security Score {security['score']}/100")
```

### LANFileTransfer

Secure peer-to-peer file transfer tool.

```python
from network_connectivity.tools.lan_file_transfer import LANFileTransfer

class LANFileTransfer(NetworkToolBase):
    """Secure peer-to-peer file transfer tool."""
```

#### Constructor
```python
def __init__(self):
    """Initialize LAN file transfer."""
```

#### Public Methods
```python
def start_service(self, port: int = 8765) -> bool:
    """Start file transfer service."""

def stop_service() -> bool:
    """Stop file transfer service."""

def discover_devices(self, timeout: int = 30) -> List[Dict[str, Any]]:
    """Discover available devices on network."""

def send_file(self, device_id: str, file_path: str, **kwargs) -> str:
    """Send file to device.
    
    Returns:
        str: Transfer ID for tracking
    """

def receive_file(self, transfer_id: str, save_path: str) -> bool:
    """Accept and receive file transfer."""

def get_transfer_status(self, transfer_id: str) -> Dict[str, Any]:
    """Get transfer status and progress."""

def cancel_transfer(self, transfer_id: str) -> bool:
    """Cancel active transfer."""

def get_transfer_history(self) -> List[Dict[str, Any]]:
    """Get transfer history."""
```

#### Example Usage
```python
# Create file transfer instance
transfer = LANFileTransfer()

# Start service
transfer.start_service(port=8765)

# Discover devices
devices = transfer.discover_devices(timeout=30)
print(f"Found {len(devices)} devices")

# Send file
if devices:
    transfer_id = transfer.send_file(
        device_id=devices[0]['id'],
        file_path="/path/to/file.txt"
    )
    
    # Monitor transfer
    while True:
        status = transfer.get_transfer_status(transfer_id)
        if status['state'] == 'completed':
            break
        print(f"Progress: {status['progress']}%")
```

## ⚙️ Configuration API

### ConfigService

Advanced configuration management service.

```python
from network_connectivity.core.config_service import ConfigService

class ConfigService:
    """Advanced configuration management service."""
```

#### Public Methods
```python
def get_setting(self, section: str, key: str = None, default: Any = None) -> Any:
    """Get configuration setting."""

def set_setting(self, section: str, key: str, value: Any) -> bool:
    """Set configuration setting."""

def get_profile(self, profile_name: str) -> Dict[str, Any]:
    """Get configuration profile."""

def set_profile(self, profile_name: str, config: Dict[str, Any]) -> bool:
    """Set configuration profile."""

def switch_profile(self, profile_name: str) -> bool:
    """Switch to configuration profile."""

def export_config(self, filename: str, include_profiles: bool = True) -> bool:
    """Export configuration to file."""

def import_config(self, filename: str, merge: bool = True) -> bool:
    """Import configuration from file."""

def validate_config(self, config: Dict[str, Any]) -> List[str]:
    """Validate configuration."""

def reset_to_defaults(self, section: str = None) -> bool:
    """Reset configuration to defaults."""
```

#### Example Usage
```python
from network_connectivity.core.config_service import get_config_service

# Get service instance
config = get_config_service()

# Get/set settings
timeout = config.get_setting('network_connectivity', 'default_timeout', 5000)
config.set_setting('network_connectivity', 'default_timeout', 10000)

# Work with profiles
config.set_profile('production', {
    'network_connectivity': {
        'general': {'default_timeout': 3000},
        'bandwidth_monitor': {'monitoring_interval': 500}
    }
})
config.switch_profile('production')

# Export/import
config.export_config('backup.json')
config.import_config('backup.json')
```

## 📊 Services API

### LoggingService

Advanced logging service with aggregation and analysis.

```python
from network_connectivity.core.logging_service import LoggingService

class LoggingService:
    """Advanced logging service."""
```

#### Public Methods
```python
def get_logger(self, name: str) -> logging.Logger:
    """Get logger instance."""

def log_network_event(self, tool_name: str, event_type: str, 
                     message: str, **kwargs) -> None:
    """Log network-specific event."""

def get_log_entries(self, start_time: datetime = None, 
                   end_time: datetime = None, 
                   level: str = None) -> List[Dict[str, Any]]:
    """Get log entries."""

def analyze_logs(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
    """Analyze log patterns."""

def export_logs(self, filename: str, format: str = "json") -> bool:
    """Export logs to file."""

def configure_alerts(self, alert_config: Dict[str, Any]) -> bool:
    """Configure log-based alerts."""
```

### NotificationService

Notification and alerting service.

```python
from network_connectivity.core.notification_service import NotificationService

class NotificationService:
    """Notification and alerting service."""
```

#### Public Methods
```python
def send_notification(self, title: str, message: str, 
                     level: str = "info", **kwargs) -> bool:
    """Send notification."""

def configure_email(self, smtp_config: Dict[str, Any]) -> bool:
    """Configure email notifications."""

def add_webhook(self, name: str, url: str, **kwargs) -> bool:
    """Add webhook endpoint."""

def test_notification(self, method: str) -> bool:
    """Test notification delivery."""
```

## 🎨 GUI API

### NetworkConnectivityHub

Main GUI hub for network tools.

```python
from network_connectivity.gui.hub import NetworkConnectivityHub

class NetworkConnectivityHub(StandardWindow):
    """Main Network Connectivity Hub interface."""
```

#### Public Methods
```python
def launch_tool(self, tool_name: str) -> bool:
    """Launch a network tool."""

def close_tool(self, tool_name: str) -> bool:
    """Close a network tool."""

def get_active_tools(self) -> List[str]:
    """Get list of currently active tools."""
```

### Tool Widgets

Individual tool GUI components.

```python
# Bandwidth Monitor Widget
from network_connectivity.gui.widgets.bandwidth_monitor_widget import BandwidthMonitorWidget

# Port Scanner Widget  
from network_connectivity.gui.widgets.port_scanner_widget import PortScannerWidget

# Wi-Fi Analyzer Widget
from network_connectivity.gui.widgets.wifi_analyzer_widget import WiFiAnalyzerWidget

# LAN File Transfer Widget
from network_connectivity.gui.widgets.lan_file_transfer_widget import LANFileTransferWidget
```

## 🔧 Utilities API

### Network Utilities

Common network utility functions.

```python
from network_connectivity.utils.network_utils import (
    validate_ip_address,
    validate_port_range,
    parse_network_range,
    get_local_ip_addresses,
    check_network_connectivity
)

def validate_ip_address(ip: str) -> bool:
    """Validate IP address format."""

def validate_port_range(port_range: str) -> bool:
    """Validate port range specification."""

def parse_network_range(network: str) -> List[str]:
    """Parse network range into individual IPs."""

def get_local_ip_addresses() -> List[str]:
    """Get local IP addresses."""

def check_network_connectivity(host: str, port: int, timeout: int = 5) -> bool:
    """Check network connectivity to host:port."""
```

### Data Utilities

Data processing and export utilities.

```python
from network_connectivity.utils.data_utils import (
    export_to_csv,
    export_to_json,
    export_to_xml,
    generate_report
)

def export_to_csv(data: List[Dict[str, Any]], filename: str) -> bool:
    """Export data to CSV format."""

def export_to_json(data: Any, filename: str) -> bool:
    """Export data to JSON format."""

def export_to_xml(data: Dict[str, Any], filename: str) -> bool:
    """Export data to XML format."""

def generate_report(data: Dict[str, Any], template: str, 
                   format: str = "html") -> str:
    """Generate formatted report."""
```

## 🔗 Integration Examples

### Complete Workflow Example

```python
from network_connectivity.tools.bandwidth_monitor import BandwidthMonitor
from network_connectivity.tools.port_scanner import PortScanner
from network_connectivity.tools.wifi_analyzer import WiFiAnalyzer
from network_connectivity.core.config_service import get_config_service
from network_connectivity.core.logging_service import get_logging_service
from datetime import datetime, timedelta

# Initialize services
config = get_config_service()
logging = get_logging_service()
logger = logging.get_logger('NetworkAnalysis')

# Configure tools
config.set_setting('network_connectivity', 'default_timeout', 10000)

# Create tools
bandwidth_monitor = BandwidthMonitor()
port_scanner = PortScanner()
wifi_analyzer = WiFiAnalyzer()

try:
    # Start bandwidth monitoring
    logger.info("Starting network analysis workflow")
    bandwidth_monitor.start_monitoring(interface="auto", interval=1000)
    
    # Perform port scan
    scan_results = port_scanner.quick_scan("192.168.1.1")
    logger.info(f"Port scan completed: {len(scan_results['ports'])} ports scanned")
    
    # Analyze Wi-Fi
    wifi_analyzer.start_scanning(scan_interval=30000)
    networks = wifi_analyzer.get_networks()
    logger.info(f"Wi-Fi analysis completed: {len(networks)} networks found")
    
    # Generate comprehensive report
    report_data = {
        'bandwidth': bandwidth_monitor.get_current_data(),
        'port_scan': scan_results,
        'wifi_networks': networks,
        'timestamp': datetime.now().isoformat()
    }
    
    # Export results
    bandwidth_monitor.export_data(
        start_time=datetime.now() - timedelta(hours=1),
        end_time=datetime.now(),
        format="csv",
        filename="bandwidth_report.csv"
    )
    
    port_scanner.generate_report(scan_results, format="html")
    
finally:
    # Cleanup
    bandwidth_monitor.stop_monitoring()
    wifi_analyzer.stop_scanning()
    logger.info("Network analysis workflow completed")
```

### Error Handling

```python
from network_connectivity.core.network_base import NetworkOperationStatus
from network_connectivity.tools.bandwidth_monitor import BandwidthMonitor

monitor = BandwidthMonitor()

# Connect to signals for error handling
def handle_error(error_message):
    print(f"Error occurred: {error_message}")

def handle_status_change(status):
    print(f"Status changed: {status}")

monitor.error_occurred.connect(handle_error)
monitor.status_changed.connect(handle_status_change)

# Start monitoring with error handling
try:
    if monitor.start_monitoring():
        print("Monitoring started successfully")
    else:
        print("Failed to start monitoring")
except Exception as e:
    print(f"Exception during startup: {e}")
```

## 📋 API Conventions

### Return Values
- **Boolean methods:** Return `True` for success, `False` for failure
- **Data methods:** Return data structures or `None` for no data
- **List methods:** Return empty list `[]` if no items found
- **Dict methods:** Return empty dict `{}` if no data available

### Error Handling
- **Exceptions:** Raised for programming errors and invalid parameters
- **Signals:** Emitted for runtime errors and status changes
- **Return values:** Used for operation success/failure indication
- **Logging:** All errors logged to appropriate logger

### Threading
- **Thread-safe:** All public methods are thread-safe
- **Signals:** Emitted from worker threads, safe for GUI updates
- **Blocking operations:** Long-running operations use separate threads
- **Cancellation:** Operations support cancellation via stop methods

---

**For more examples and detailed usage:** See the **[Examples](../examples/)** and **[Tutorials](../tutorials/)** sections.