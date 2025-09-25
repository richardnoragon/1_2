"""Mock objects for network-related components."""

import random
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from unittest.mock import Mock, MagicMock

from ...core.platform_network import NetworkInterface, NetworkStats


class MockNetworkInterface:
    """Mock network interface for testing."""

    def __init__(
        self,
        name: str = "eth0",
        is_wireless: bool = False,
        is_up: bool = True,
        speed_mbps: int = 1000,
    ):
        self.name = name
        self.display_name = name.capitalize()
        self.description = f"Mock {name} Interface"
        self.mac_address = self._generate_mac_address()
        self.ip_addresses = [self._generate_ip_address()]
        self.is_up = is_up
        self.is_wireless = is_wireless
        self.speed_mbps = speed_mbps
        self.mtu = 1500

    def _generate_mac_address(self) -> str:
        """Generate a random MAC address."""
        return ":".join([f"{random.randint(0, 255):02x}" for _ in range(6)])

    def _generate_ip_address(self) -> str:
        """Generate a random IP address."""
        return f"192.168.1.{random.randint(100, 200)}"

    def to_network_interface(self) -> NetworkInterface:
        """Convert to actual NetworkInterface object."""
        return NetworkInterface(
            name=self.name,
            display_name=self.display_name,
            description=self.description,
            mac_address=self.mac_address,
            ip_addresses=self.ip_addresses,
            is_up=self.is_up,
            is_wireless=self.is_wireless,
            speed_mbps=self.speed_mbps,
            mtu=self.mtu,
        )


class MockNetworkStats:
    """Mock network statistics for testing."""

    def __init__(self, interface_name: str = "eth0"):
        self.interface_name = interface_name
        self.bytes_sent = random.randint(1000000, 10000000)
        self.bytes_received = random.randint(2000000, 20000000)
        self.packets_sent = random.randint(1000, 10000)
        self.packets_received = random.randint(2000, 20000)
        self.errors_in = random.randint(0, 10)
        self.errors_out = random.randint(0, 10)
        self.drops_in = random.randint(0, 5)
        self.drops_out = random.randint(0, 5)
        self.timestamp = datetime.now()

    def to_network_stats(self) -> NetworkStats:
        """Convert to actual NetworkStats object."""
        return NetworkStats(
            interface_name=self.interface_name,
            bytes_sent=self.bytes_sent,
            bytes_received=self.bytes_received,
            packets_sent=self.packets_sent,
            packets_received=self.packets_received,
            errors_in=self.errors_in,
            errors_out=self.errors_out,
            drops_in=self.drops_in,
            drops_out=self.drops_out,
            timestamp=self.timestamp,
        )

    def update_stats(self, time_delta: float = 1.0):
        """Update stats to simulate network activity."""
        # Simulate data transfer
        bytes_per_second = random.randint(1000, 100000)
        packets_per_second = random.randint(10, 1000)

        self.bytes_sent += int(bytes_per_second * time_delta * 0.3)
        self.bytes_received += int(bytes_per_second * time_delta)
        self.packets_sent += int(packets_per_second * time_delta * 0.3)
        self.packets_received += int(packets_per_second * time_delta)

        # Occasionally add errors/drops
        if random.random() < 0.1:
            self.errors_in += random.randint(0, 2)
            self.errors_out += random.randint(0, 2)

        if random.random() < 0.05:
            self.drops_in += random.randint(0, 1)
            self.drops_out += random.randint(0, 1)

        self.timestamp = datetime.now()


class MockPlatformDetector:
    """Mock platform network detector for testing."""

    def __init__(self):
        self.interfaces = [
            MockNetworkInterface("eth0", is_wireless=False, speed_mbps=1000),
            MockNetworkInterface("wlan0", is_wireless=True, speed_mbps=150),
            MockNetworkInterface("lo", is_wireless=False, speed_mbps=0),
        ]
        self.stats = {
            iface.name: MockNetworkStats(iface.name)
            for iface in self.interfaces
        }
        self.default_gateway = "192.168.1.1"
        self.dns_servers = ["8.8.8.8", "8.8.4.4"]

    def get_network_interfaces(self) -> List[NetworkInterface]:
        """Get list of mock network interfaces."""
        return [iface.to_network_interface() for iface in self.interfaces]

    def get_interface_stats(
        self, interface_name: str
    ) -> Optional[NetworkStats]:
        """Get mock statistics for interface."""
        if interface_name in self.stats:
            # Update stats to simulate activity
            self.stats[interface_name].update_stats()
            return self.stats[interface_name].to_network_stats()
        return None

    def is_interface_wireless(self, interface_name: str) -> bool:
        """Check if interface is wireless."""
        for iface in self.interfaces:
            if iface.name == interface_name:
                return iface.is_wireless
        return False

    def get_default_gateway(self) -> Optional[str]:
        """Get default gateway."""
        return self.default_gateway

    def get_dns_servers(self) -> List[str]:
        """Get DNS servers."""
        return self.dns_servers.copy()

    def add_interface(self, interface: MockNetworkInterface):
        """Add a mock interface."""
        self.interfaces.append(interface)
        self.stats[interface.name] = MockNetworkStats(interface.name)

    def remove_interface(self, interface_name: str):
        """Remove a mock interface."""
        self.interfaces = [
            iface for iface in self.interfaces if iface.name != interface_name
        ]
        if interface_name in self.stats:
            del self.stats[interface_name]

    def simulate_interface_down(self, interface_name: str):
        """Simulate interface going down."""
        for iface in self.interfaces:
            if iface.name == interface_name:
                iface.is_up = False
                break

    def simulate_interface_up(self, interface_name: str):
        """Simulate interface coming up."""
        for iface in self.interfaces:
            if iface.name == interface_name:
                iface.is_up = True
                break


class MockNetworkData:
    """Mock network data generator for testing."""

    @staticmethod
    def generate_bandwidth_data(
        interface_name: str = "eth0", count: int = 10, time_interval: int = 1
    ) -> List[Dict[str, Any]]:
        """Generate mock bandwidth monitoring data."""
        data = []
        base_time = datetime.now() - timedelta(seconds=count * time_interval)

        for i in range(count):
            timestamp = base_time + timedelta(seconds=i * time_interval)

            # Generate realistic bandwidth data
            upload_speed = random.uniform(10, 100)  # Mbps
            download_speed = random.uniform(50, 500)  # Mbps

            data.append(
                {
                    "timestamp": timestamp,
                    "interface_name": interface_name,
                    "bytes_sent": random.randint(1000, 10000),
                    "bytes_received": random.randint(5000, 50000),
                    "upload_speed": upload_speed,
                    "download_speed": download_speed,
                    "total_bytes_sent": random.randint(1000000, 10000000),
                    "total_bytes_received": random.randint(5000000, 50000000),
                }
            )

        return data

    @staticmethod
    def generate_port_scan_results(
        target: str = "192.168.1.1", port_range: tuple = (1, 1000)
    ) -> Dict[str, Any]:
        """Generate mock port scan results."""
        results = {
            "target": target,
            "scan_time": datetime.now(),
            "total_ports": port_range[1] - port_range[0] + 1,
            "open_ports": [],
            "closed_ports": [],
            "filtered_ports": [],
        }

        # Common open ports
        common_ports = [22, 23, 25, 53, 80, 110, 143, 443, 993, 995]

        for port in range(port_range[0], port_range[1] + 1):
            if port in common_ports and random.random() < 0.8:
                results["open_ports"].append(
                    {
                        "port": port,
                        "state": "open",
                        "service": MockNetworkData._get_service_name(port),
                        "version": f"Service {port} v1.0",
                    }
                )
            elif random.random() < 0.1:
                results["filtered_ports"].append(
                    {"port": port, "state": "filtered"}
                )
            else:
                results["closed_ports"].append(
                    {"port": port, "state": "closed"}
                )

        return results

    @staticmethod
    def generate_wifi_networks(count: int = 5) -> List[Dict[str, Any]]:
        """Generate mock WiFi network data."""
        networks = []
        ssid_prefixes = ["HomeNetwork", "OfficeWiFi", "CafeNet", "PublicWiFi"]
        security_types = ["WPA2-PSK", "WPA3-SAE", "WEP", "Open"]

        for i in range(count):
            ssid = f"{random.choice(ssid_prefixes)}_{i+1}"
            bssid = ":".join(
                [f"{random.randint(0, 255):02x}" for _ in range(6)]
            )

            networks.append(
                {
                    "ssid": ssid,
                    "bssid": bssid,
                    "channel": random.choice([1, 6, 11, 36, 40, 44, 48]),
                    "frequency": random.choice(
                        [2437, 2462, 5180, 5200, 5220, 5240]
                    ),
                    "signal_strength": random.randint(-80, -30),
                    "security": [random.choice(security_types)],
                    "encryption": random.choice(
                        ["AES", "TKIP", "WEP", "None"]
                    ),
                    "vendor": random.choice(
                        ["Cisco", "Netgear", "Linksys", "TP-Link"]
                    ),
                }
            )

        return networks

    @staticmethod
    def generate_lan_devices(count: int = 3) -> List[Dict[str, Any]]:
        """Generate mock LAN device data."""
        devices = []
        device_types = ["Computer", "Phone", "Tablet", "Printer", "Router"]
        os_types = ["Windows", "macOS", "Linux", "Android", "iOS"]

        for i in range(count):
            ip = f"192.168.1.{100 + i}"
            mac = ":".join([f"{random.randint(0, 255):02x}" for _ in range(6)])

            devices.append(
                {
                    "ip_address": ip,
                    "mac_address": mac,
                    "hostname": f"device-{i+1}",
                    "device_type": random.choice(device_types),
                    "os_type": random.choice(os_types),
                    "manufacturer": random.choice(
                        ["Apple", "Dell", "HP", "Samsung"]
                    ),
                    "last_seen": datetime.now()
                    - timedelta(minutes=random.randint(1, 60)),
                    "is_online": random.choice([True, False]),
                    "open_ports": random.sample(
                        [22, 80, 443, 8080], random.randint(0, 3)
                    ),
                }
            )

        return devices

    @staticmethod
    def _get_service_name(port: int) -> str:
        """Get service name for port."""
        service_map = {
            22: "ssh",
            23: "telnet",
            25: "smtp",
            53: "dns",
            80: "http",
            110: "pop3",
            143: "imap",
            443: "https",
            993: "imaps",
            995: "pop3s",
        }
        return service_map.get(port, f"unknown-{port}")


class MockDeviceDiscovery:
    """Mock device discovery for LAN file transfer testing."""

    def __init__(self):
        self.discovered_devices = MockNetworkData.generate_lan_devices(5)
        self.discovery_active = False

    def start_discovery(
        self, interface_name: str = "eth0", discovery_port: int = 8888
    ):
        """Start device discovery."""
        self.discovery_active = True
        return True

    def stop_discovery(self):
        """Stop device discovery."""
        self.discovery_active = False

    def get_discovered_devices(self) -> List[Dict[str, Any]]:
        """Get list of discovered devices."""
        return self.discovered_devices.copy()

    def add_device(self, device: Dict[str, Any]):
        """Add a device to discovery results."""
        self.discovered_devices.append(device)

    def remove_device(self, ip_address: str):
        """Remove a device from discovery results."""
        self.discovered_devices = [
            device
            for device in self.discovered_devices
            if device["ip_address"] != ip_address
        ]

    def simulate_device_online(self, ip_address: str):
        """Simulate device coming online."""
        for device in self.discovered_devices:
            if device["ip_address"] == ip_address:
                device["is_online"] = True
                device["last_seen"] = datetime.now()
                break

    def simulate_device_offline(self, ip_address: str):
        """Simulate device going offline."""
        for device in self.discovered_devices:
            if device["ip_address"] == ip_address:
                device["is_online"] = False
                break


class MockNetworkError:
    """Mock network error simulator."""

    ERROR_TYPES = [
        "connection_timeout",
        "connection_refused",
        "host_unreachable",
        "network_unreachable",
        "dns_resolution_failed",
        "ssl_handshake_failed",
        "permission_denied",
        "interface_not_found",
    ]

    def __init__(self, error_probability: float = 0.1):
        self.error_probability = error_probability
        self.error_counts = {error_type: 0 for error_type in self.ERROR_TYPES}

    def should_simulate_error(self) -> bool:
        """Check if an error should be simulated."""
        return random.random() < self.error_probability

    def get_random_error(self) -> str:
        """Get a random error type."""
        error_type = random.choice(self.ERROR_TYPES)
        self.error_counts[error_type] += 1
        return error_type

    def simulate_error(self, error_type: str):
        """Simulate a specific error."""
        if error_type == "connection_timeout":
            raise TimeoutError("Connection timed out")
        elif error_type == "connection_refused":
            raise ConnectionRefusedError("Connection refused")
        elif error_type == "host_unreachable":
            raise OSError("Host unreachable")
        elif error_type == "network_unreachable":
            raise OSError("Network unreachable")
        elif error_type == "dns_resolution_failed":
            raise OSError("DNS resolution failed")
        elif error_type == "ssl_handshake_failed":
            raise OSError("SSL handshake failed")
        elif error_type == "permission_denied":
            raise PermissionError("Permission denied")
        elif error_type == "interface_not_found":
            raise ValueError("Network interface not found")
        else:
            raise RuntimeError(f"Unknown error type: {error_type}")

    def get_error_statistics(self) -> Dict[str, int]:
        """Get error statistics."""
        return self.error_counts.copy()

    def reset_statistics(self):
        """Reset error statistics."""
        self.error_counts = {error_type: 0 for error_type in self.ERROR_TYPES}
