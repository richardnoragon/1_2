"""Example usage of the LAN File Transfer tool."""

import sys
import os
import time
from pathlib import Path

# Add the parent directory to the path to import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from network_connectivity.tools.lan_file_transfer import (
    LANFileTransfer,
    TransferStatus,
    DeviceStatus,
)


def main():
    """Demonstrate LAN File Transfer functionality."""
    print("LAN File Transfer Tool Example")
    print("=" * 40)

    # Initialize the LAN File Transfer tool
    lan_transfer = LANFileTransfer()

    # Check if encryption is available
    if lan_transfer.encryption_handler.is_available():
        print("✓ Encryption support available")
    else:
        print("⚠ Encryption not available (install cryptography package)")

    # Check platform support
    health_status = lan_transfer.get_health_status()
    if health_status["platform_supported"]:
        print("✓ Platform supported")
    else:
        print("⚠ Platform may have limited support")

    print("\n1. Starting LAN File Transfer Service")
    print("-" * 35)

    # Start the service
    result = lan_transfer.execute_operation(operation_type="start_service")
    if result.success:
        print("✓ Service started successfully")
        print(f"  - Discovery active: {result.data['discovery_active']}")
        print(f"  - Queue active: {result.data['queue_active']}")
    else:
        print(f"✗ Failed to start service: {result.error_message}")
        return

    print("\n2. Device Discovery")
    print("-" * 18)

    # Wait a moment for device discovery
    print("Waiting for device discovery...")
    time.sleep(5)

    # Get discovered devices
    result = lan_transfer.execute_operation(operation_type="discover_devices")
    if result.success:
        devices = result.data["devices"]
        print(f"✓ Found {len(devices)} devices:")
        for device in devices:
            print(f"  - {device['name']} ({device['ip_address']})")
            print(f"    ID: {device['device_id']}")
            print(f"    Status: {device['status']}")
            print(f"    Capabilities: {', '.join(device['capabilities'])}")
    else:
        print(f"✗ Failed to discover devices: {result.error_message}")

    print("\n3. Service Status")
    print("-" * 15)

    # Get service status
    result = lan_transfer.execute_operation(operation_type="get_status")
    if result.success:
        status = result.data
        print("✓ Service Status:")
        print(f"  - Service running: {status['service_running']}")
        print(f"  - Discovery active: {status['discovery_active']}")
        print(f"  - Encryption available: {status['encryption_available']}")
        print(f"  - Discovered devices: {status['discovered_devices']}")
        print(f"  - Queue status: {status['queue_status']}")

    print("\n4. Device Management")
    print("-" * 18)

    # Example of adding a trusted device (if any devices were found)
    if "devices" in locals() and devices:
        first_device = devices[0]
        device_id = first_device["device_id"]

        # Add device to trusted list
        result = lan_transfer.execute_operation(
            operation_type="add_trusted_device", device_id=device_id
        )
        if result.success:
            print(f"✓ Added device {device_id} to trusted list")
        else:
            print(f"✗ Failed to add trusted device: {result.error_message}")

    print("\n5. File Transfer Example")
    print("-" * 23)

    # Create a test file for transfer
    test_file = Path("test_transfer_file.txt")
    test_content = "This is a test file for LAN transfer demonstration."

    try:
        with open(test_file, "w") as f:
            f.write(test_content)
        print(f"✓ Created test file: {test_file}")

        # Example file transfer (if devices available)
        if "devices" in locals() and devices:
            target_device = devices[0]["device_id"]

            result = lan_transfer.execute_operation(
                operation_type="send_file",
                source_path=str(test_file),
                target_device_id=target_device,
            )

            if result.success:
                print("✓ File transfer initiated:")
                print(f"  - Job ID: {result.data['job_id']}")
                print(f"  - Source: {result.data['source_path']}")
                print(f"  - Target: {result.data['target_device']}")
                print(f"  - File size: {result.data['file_size']} bytes")
            else:
                print(f"✗ Failed to initiate transfer: {result.error_message}")
        else:
            print("⚠ No devices available for transfer demonstration")

    except Exception as e:
        print(f"✗ Error creating test file: {e}")

    finally:
        # Clean up test file
        if test_file.exists():
            test_file.unlink()
            print(f"✓ Cleaned up test file: {test_file}")

    print("\n6. Advanced Features")
    print("-" * 19)

    # Demonstrate configuration access
    print("Configuration examples:")
    discovery_port = lan_transfer.get_tool_config("discovery_port", 8765)
    max_concurrent = lan_transfer.get_tool_config(
        "max_concurrent_transfers", 3
    )
    encryption_enabled = lan_transfer.get_tool_config(
        "encryption_enabled", True
    )

    print(f"  - Discovery port: {discovery_port}")
    print(f"  - Max concurrent transfers: {max_concurrent}")
    print(f"  - Encryption enabled: {encryption_enabled}")

    # Show supported protocols
    protocols = lan_transfer.get_supported_protocols()
    print(f"  - Supported protocols: {', '.join(protocols)}")

    print("\n7. Stopping Service")
    print("-" * 17)

    # Stop the service
    result = lan_transfer.execute_operation(operation_type="stop_service")
    if result.success:
        print("✓ Service stopped successfully")
    else:
        print(f"✗ Failed to stop service: {result.error_message}")

    print("\nLAN File Transfer demonstration completed!")


def demonstrate_callbacks():
    """Demonstrate callback functionality."""
    print("\nCallback Demonstration")
    print("=" * 22)

    lan_transfer = LANFileTransfer()

    # Define callback functions
    def on_device_discovered(device):
        print(f"📱 Device discovered: {device.name} ({device.ip_address})")

    def on_progress_update(progress):
        print(
            f"📊 Transfer progress: {progress.percentage_complete:.1f}% "
            f"({progress.transfer_speed / 1024:.1f} KB/s)"
        )

    def on_data_update(data):
        print(f"📡 Data update: {data}")

    # Add callbacks
    lan_transfer.device_discovery.add_device_callback(on_device_discovered)
    lan_transfer.progress_tracker.add_progress_callback(on_progress_update)
    lan_transfer.add_data_callback(on_data_update)

    print("✓ Callbacks registered")
    print("Start the service to see callback demonstrations...")


if __name__ == "__main__":
    try:
        main()
        print("\n" + "=" * 50)
        demonstrate_callbacks()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        print(f"\nError during demonstration: {e}")
        import traceback

        traceback.print_exc()
