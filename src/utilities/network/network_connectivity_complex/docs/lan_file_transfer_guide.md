# LAN File Transfer Tool Guide

## Overview

The LAN File Transfer Tool provides secure, peer-to-peer file sharing capabilities within local area networks. It features automatic device discovery, AES-256 encryption, transfer progress monitoring, and comprehensive device management.

## Key Features

### 🔍 **Device Discovery**
- **UDP Broadcast Discovery**: Automatically discovers devices on the local network
- **Service Announcement**: Advertises device capabilities and availability
- **Real-time Updates**: Maintains current device status and availability
- **Cross-platform Support**: Works on Windows, macOS, and Linux

### 🔒 **Security & Encryption**
- **AES-256 Encryption**: Strong encryption for sensitive file transfers
- **Device Authentication**: Certificate-based or password-based authentication
- **Trusted Device Management**: Whitelist/blacklist device management
- **Transfer Validation**: Digital signatures and integrity verification
- **Access Control**: Permission-based file sharing and device authorization

### 📊 **Transfer Management**
- **Queue System**: Multiple concurrent transfers with priority management
- **Progress Tracking**: Real-time progress, speed, ETA, and completion status
- **Resume Support**: Continuation of interrupted transfers
- **Bandwidth Control**: Transfer rate limiting and QoS management
- **Integrity Verification**: Checksum validation and corruption detection

### 🌐 **Network Protocols**
- **P2P Protocol**: Custom protocol for direct device-to-device transfers
- **Discovery Protocol**: Broadcast-based device discovery
- **Transfer Protocol**: Chunked file transfer with integrity verification
- **Compression Support**: Optional file compression to reduce transfer time

## Quick Start

### Basic Usage

```python
from network_connectivity.tools.lan_file_transfer import LANFileTransfer

# Initialize the tool
lan_transfer = LANFileTransfer()

# Start the service
result = lan_transfer.execute_operation(operation_type='start_service')
if result.success:
    print("Service started successfully")

# Discover devices
result = lan_transfer.execute_operation(operation_type='discover_devices')
devices = result.data['devices']

# Send a file
result = lan_transfer.execute_operation(
    operation_type='send_file',
    source_path='/path/to/file.txt',
    target_device_id='device_id_here'
)

# Stop the service
lan_transfer.execute_operation(operation_type='stop_service')
```

### Configuration

```python
# Configure discovery settings
lan_transfer.set_tool_config('discovery_port', 8765)
lan_transfer.set_tool_config('discovery_interval', 30)

# Configure transfer settings
lan_transfer.set_tool_config('max_concurrent_transfers', 5)
lan_transfer.set_tool_config('encryption_enabled', True)
lan_transfer.set_tool_config('default_chunk_size', 65536)
```

## API Reference

### Core Operations

#### `start_service()`
Starts the LAN file transfer service including device discovery and transfer queue.

**Returns**: `bool` - True if started successfully

#### `stop_service()`
Stops the LAN file transfer service and all active operations.

**Returns**: `bool` - True if stopped successfully

#### `execute_operation(**kwargs)`
Main operation execution method.

**Parameters**:
- `operation_type`: Operation to execute
- Additional parameters based on operation type

**Returns**: `NetworkOperationResult`

### Operation Types

#### `start_service`
Starts the file transfer service.

```python
result = lan_transfer.execute_operation(operation_type='start_service')
```

#### `stop_service`
Stops the file transfer service.

```python
result = lan_transfer.execute_operation(operation_type='stop_service')
```

#### `send_file`
Initiates a file transfer to a target device.

```python
result = lan_transfer.execute_operation(
    operation_type='send_file',
    source_path='/path/to/file.txt',
    target_device_id='target_device_id'
)
```

**Parameters**:
- `source_path`: Path to the file to send
- `target_device_id`: ID of the target device

#### `discover_devices`
Gets list of discovered devices on the network.

```python
result = lan_transfer.execute_operation(operation_type='discover_devices')
devices = result.data['devices']
```

#### `get_status`
Gets current service status and statistics.

```python
result = lan_transfer.execute_operation(operation_type='get_status')
status = result.data
```

#### `add_trusted_device`
Adds a device to the trusted devices list.

```python
result = lan_transfer.execute_operation(
    operation_type='add_trusted_device',
    device_id='device_id_here'
)
```

#### `block_device`
Blocks a device from file transfers.

```python
result = lan_transfer.execute_operation(
    operation_type='block_device',
    device_id='device_id_here'
)
```

## Device Management

### Device Discovery

The tool automatically discovers devices on the local network using UDP broadcasts:

```python
# Get discovered devices
result = lan_transfer.execute_operation(operation_type='discover_devices')
for device in result.data['devices']:
    print(f"Device: {device['name']} ({device['ip_address']})")
    print(f"  ID: {device['device_id']}")
    print(f"  Status: {device['status']}")
    print(f"  Capabilities: {device['capabilities']}")
```

### Trust Management

```python
# Add trusted device
lan_transfer.auth_manager.add_trusted_device('device_id')

# Block device
lan_transfer.auth_manager.block_device('device_id')

# Check if device is trusted
is_trusted = lan_transfer.auth_manager.is_device_trusted('device_id')
```

## Security Features

### Encryption

The tool supports AES-256 encryption for secure file transfers:

```python
# Check if encryption is available
if lan_transfer.encryption_handler.is_available():
    print("Encryption supported")

# Generate encryption key
context = lan_transfer.encryption_handler.generate_key()

# Encrypt data
encrypted_data = lan_transfer.encryption_handler.encrypt_data(data, context)
```

### Authentication

Device authentication ensures only authorized devices can participate in transfers:

```python
# Authenticate device
is_authenticated = lan_transfer.auth_manager.authenticate_device(
    device_id, challenge_response
)

# Generate auth token
token = lan_transfer.auth_manager.generate_auth_token(device_id)

# Validate auth token
is_valid = lan_transfer.auth_manager.validate_auth_token(device_id, token)
```

## Transfer Management

### Progress Tracking

Monitor transfer progress in real-time:

```python
def on_progress_update(progress):
    print(f"Transfer {progress.job_id}: {progress.percentage_complete:.1f}%")
    print(f"Speed: {progress.transfer_speed / 1024:.1f} KB/s")
    print(f"ETA: {progress.estimated_time_remaining:.0f} seconds")

lan_transfer.progress_tracker.add_progress_callback(on_progress_update)
```

### Queue Management

```python
# Get queue status
queue_status = lan_transfer.transfer_queue.get_queue_status()
print(f"Pending: {queue_status['pending_count']}")
print(f"Active: {queue_status['active_count']}")
print(f"Completed: {queue_status['completed_count']}")

# Cancel transfer
success = lan_transfer.transfer_queue.cancel_transfer('job_id')
```

## Configuration Options

### Default Settings

```python
{
    "discovery_port": 8765,
    "transfer_port": 8766,
    "discovery_interval": 30,
    "max_concurrent_transfers": 3,
    "default_chunk_size": 65536,
    "encryption_enabled": True,
    "compression_enabled": False,
    "transfer_timeout": 300,
    "connection_timeout": 30,
    "enable_device_discovery": True,
    "auto_accept_trusted": False,
    "require_authentication": True,
    "enable_resume": True,
    "max_file_size_mb": 1024,
    "allowed_file_types": [],
    "blocked_file_types": [".exe", ".bat", ".cmd", ".scr"],
    "default_download_path": "Downloads",
    "enable_bandwidth_limiting": False,
    "max_upload_speed_mbps": 0,
    "max_download_speed_mbps": 0,
    "enable_notifications": True,
    "log_transfers": True,
    "keep_transfer_history": True,
    "history_retention_days": 30
}
```

### Custom Configuration

```python
# Set custom configuration
lan_transfer.set_tool_config('discovery_port', 9000)
lan_transfer.set_tool_config('max_concurrent_transfers', 5)
lan_transfer.set_tool_config('encryption_enabled', True)

# Get configuration
port = lan_transfer.get_tool_config('discovery_port', 8765)
```

## Error Handling

### Common Errors

```python
try:
    result = lan_transfer.execute_operation(
        operation_type='send_file',
        source_path='/nonexistent/file.txt',
        target_device_id='invalid_device'
    )
    if not result.success:
        print(f"Transfer failed: {result.error_message}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Health Monitoring

```python
# Check tool health
health = lan_transfer.get_health_status()
if not health['service_running']:
    print("Service is not running")
if not health['encryption_available']:
    print("Encryption not available")
if not health['platform_supported']:
    print("Platform may have limited support")
```

## Advanced Features

### Callbacks and Events

```python
# Device discovery callback
def on_device_discovered(device):
    print(f"New device: {device.name}")

lan_transfer.device_discovery.add_device_callback(on_device_discovered)

# Progress callback
def on_progress(progress):
    print(f"Progress: {progress.percentage_complete:.1f}%")

lan_transfer.progress_tracker.add_progress_callback(on_progress)

# Data update callback
def on_data_update(data):
    print(f"Data update: {data}")

lan_transfer.add_data_callback(on_data_update)
```

### Custom Transfer Jobs

```python
from network_connectivity.tools.lan_file_transfer import (
    TransferJob, TransferDirection, TransferStatus, CompressionType
)

# Create custom transfer job
job = TransferJob(
    job_id="custom_job_001",
    source_path="/path/to/file.txt",
    destination_path="received_file.txt",
    file_size=1024000,
    direction=TransferDirection.SEND,
    device_id="target_device",
    status=TransferStatus.PENDING,
    created_time=datetime.now(),
    compression=CompressionType.GZIP,
    encryption_enabled=True,
    priority=8,
    chunk_size=32768
)

# Add to queue
lan_transfer.transfer_queue.add_transfer(job)
```

## Troubleshooting

### Common Issues

1. **Service won't start**
   - Check if ports are available
   - Verify network permissions
   - Check firewall settings

2. **No devices discovered**
   - Ensure devices are on the same network
   - Check UDP broadcast permissions
   - Verify discovery port is not blocked

3. **Transfer failures**
   - Check device authentication
   - Verify file permissions
   - Ensure sufficient disk space

4. **Encryption errors**
   - Install cryptography package: `pip install cryptography`
   - Check encryption configuration

### Logging

```python
import logging

# Enable debug logging
logging.getLogger('RFU.NetworkConnectivity.LANFileTransfer').setLevel(
    logging.DEBUG
)

# Check logs for detailed error information
```

## Security Considerations

1. **Network Security**: Only use on trusted networks
2. **File Validation**: Validate received files before opening
3. **Access Control**: Use device authentication and trusted lists
4. **Encryption**: Enable encryption for sensitive data
5. **Firewall**: Configure firewall rules appropriately

## Performance Tips

1. **Chunk Size**: Adjust chunk size based on network conditions
2. **Concurrent Transfers**: Limit concurrent transfers to avoid congestion
3. **Compression**: Enable compression for large text files
4. **Bandwidth Limiting**: Use bandwidth controls on busy networks
5. **Network Quality**: Monitor network quality for optimal performance

## Integration Examples

### With GUI Applications

```python
from PyQt5.QtCore import QObject, pyqtSignal

class FileTransferWidget(QObject):
    progress_updated = pyqtSignal(str, float)  # job_id, percentage
    
    def __init__(self):
        super().__init__()
        self.lan_transfer = LANFileTransfer()
        self.lan_transfer.progress_tracker.add_progress_callback(
            self.on_progress_update
        )
    
    def on_progress_update(self, progress):
        self.progress_updated.emit(
            progress.job_id, 
            progress.percentage_complete
        )
```

### With Web Applications

```python
from flask import Flask, jsonify, request

app = Flask(__name__)
lan_transfer = LANFileTransfer()

@app.route('/api/devices')
def get_devices():
    result = lan_transfer.execute_operation(operation_type='discover_devices')
    return jsonify(result.data)

@app.route('/api/transfer', methods=['POST'])
def start_transfer():
    data = request.json
    result = lan_transfer.execute_operation(
        operation_type='send_file',
        source_path=data['source_path'],
        target_device_id=data['target_device_id']
    )
    return jsonify({'success': result.success, 'data': result.data})
```

## Conclusion

The LAN File Transfer Tool provides a comprehensive solution for secure, efficient file sharing within local networks. With its robust feature set including encryption, device management, and progress tracking, it's suitable for both simple file transfers and complex enterprise scenarios.

For additional support and examples, refer to the example files in the `examples/` directory.