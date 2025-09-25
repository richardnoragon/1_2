"""Connection state management for network connectivity tools."""

import logging
import threading
import time
from typing import Dict, List, Optional, Set
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from .platform_network import PlatformNetworkDetector, NetworkInterface


class ConnectionState(Enum):
    """Network connection states."""

    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    UNKNOWN = "unknown"


@dataclass
class ConnectionInfo:
    """Information about a network connection."""

    interface_name: str
    state: ConnectionState
    ip_address: Optional[str]
    gateway: Optional[str]
    dns_servers: List[str]
    last_updated: datetime
    connection_quality: float  # 0.0 to 1.0


class ConnectionManager:
    """Manages network connection state and monitoring."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """Singleton pattern implementation."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize the connection manager."""
        self.logger = logging.getLogger(
            "RFU.NetworkConnectivity.ConnectionManager"
        )
        self.platform_detector = PlatformNetworkDetector()

        # Connection tracking
        self.connections: Dict[str, ConnectionInfo] = {}
        self.monitored_interfaces: Set[str] = set()
        self._monitoring_active = False
        self._monitoring_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

        # Connection callbacks
        self.connection_callbacks: List = []

        self.logger.info("Connection manager initialized")

    def start_monitoring(self, interfaces: Optional[List[str]] = None) -> bool:
        """Start monitoring network connections.

        Args:
            interfaces: List of interfaces to monitor (None for all active)

        Returns:
            True if monitoring started successfully
        """
        if self._monitoring_active:
            self.logger.warning("Connection monitoring already active")
            return True

        try:
            # Determine interfaces to monitor
            if interfaces is None:
                active_interfaces = (
                    self.platform_detector.get_active_interfaces()
                )
                interfaces = [iface.name for iface in active_interfaces]

            self.monitored_interfaces = set(interfaces)
            self._stop_event.clear()

            # Start monitoring thread
            self._monitoring_thread = threading.Thread(
                target=self._monitoring_loop,
                name="ConnectionMonitoring",
                daemon=True,
            )
            self._monitoring_thread.start()

            self._monitoring_active = True
            self.logger.info(
                f"Started connection monitoring for: {', '.join(interfaces)}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Failed to start connection monitoring: {e}")
            return False

    def stop_monitoring(self) -> bool:
        """Stop connection monitoring.

        Returns:
            True if monitoring stopped successfully
        """
        if not self._monitoring_active:
            return True

        try:
            self._stop_event.set()
            self._monitoring_active = False

            if self._monitoring_thread and self._monitoring_thread.is_alive():
                self._monitoring_thread.join(timeout=5.0)

            self.logger.info("Stopped connection monitoring")
            return True

        except Exception as e:
            self.logger.error(f"Failed to stop connection monitoring: {e}")
            return False

    def _monitoring_loop(self):
        """Main connection monitoring loop."""
        self.logger.debug("Starting connection monitoring loop")

        while not self._stop_event.is_set():
            try:
                self._update_connections()
                time.sleep(5.0)  # Check every 5 seconds
            except Exception as e:
                self.logger.error(f"Error in connection monitoring: {e}")
                time.sleep(5.0)

        self.logger.debug("Connection monitoring loop stopped")

    def _update_connections(self):
        """Update connection information for monitored interfaces."""
        current_interfaces = self.platform_detector.get_network_interfaces()
        interface_map = {iface.name: iface for iface in current_interfaces}

        for interface_name in self.monitored_interfaces:
            if interface_name in interface_map:
                interface = interface_map[interface_name]
                self._update_interface_connection(interface)
            else:
                # Interface no longer exists
                self._mark_interface_disconnected(interface_name)

    def _update_interface_connection(self, interface: NetworkInterface):
        """Update connection info for a specific interface.

        Args:
            interface: Network interface to update
        """
        interface_name = interface.name

        # Determine connection state
        if interface.is_active and interface.ip_addresses:
            state = ConnectionState.CONNECTED
            ip_address = (
                interface.ip_addresses[0] if interface.ip_addresses else None
            )
        else:
            state = ConnectionState.DISCONNECTED
            ip_address = None

        # Get gateway information
        gateway = None
        if state == ConnectionState.CONNECTED:
            gateway = self.platform_detector.get_default_gateway()

        # Create or update connection info
        connection_info = ConnectionInfo(
            interface_name=interface_name,
            state=state,
            ip_address=ip_address,
            gateway=gateway,
            dns_servers=self._detect_dns_servers(interface),
            last_updated=datetime.now(),
            connection_quality=self._calculate_connection_quality(interface),
        )

        # Check if state changed
        previous_info = self.connections.get(interface_name)
        state_changed = (
            previous_info is None
            or previous_info.state != connection_info.state
        )

        self.connections[interface_name] = connection_info

        if state_changed:
            self._notify_connection_change(interface_name, connection_info)

    def _mark_interface_disconnected(self, interface_name: str):
        """Mark an interface as disconnected.

        Args:
            interface_name: Name of the interface
        """
        if interface_name in self.connections:
            connection_info = self.connections[interface_name]
            if connection_info.state != ConnectionState.DISCONNECTED:
                connection_info.state = ConnectionState.DISCONNECTED
                connection_info.ip_address = None
                connection_info.gateway = None
                connection_info.last_updated = datetime.now()
                connection_info.connection_quality = 0.0

                self._notify_connection_change(interface_name, connection_info)

    def _calculate_connection_quality(
        self, interface: NetworkInterface
    ) -> float:
        """Calculate connection quality score.

        Args:
            interface: Network interface

        Returns:
            Quality score from 0.0 to 1.0
        """
        if not interface.is_active:
            return 0.0

        quality = 0.5  # Base score for active interface

        # Add points for having IP address
        if interface.ip_addresses:
            quality += 0.3

        # Add points for having speed information
        if interface.speed_mbps and interface.speed_mbps > 0:
            quality += 0.2

        return min(quality, 1.0)

    def _notify_connection_change(
        self, interface_name: str, connection_info: ConnectionInfo
    ):
        """Notify callbacks about connection state changes.

        Args:
            interface_name: Name of the interface
            connection_info: Updated connection information
        """
        self.logger.info(
            f"Connection state changed for {interface_name}: "
            f"{connection_info.state.value}"
        )

        for callback in self.connection_callbacks:
            try:
                callback(interface_name, connection_info)
            except Exception as e:
                self.logger.error(f"Error in connection callback: {e}")

    def get_connection_info(
        self, interface_name: str
    ) -> Optional[ConnectionInfo]:
        """Get connection information for an interface.

        Args:
            interface_name: Name of the interface

        Returns:
            Connection information or None if not found
        """
        return self.connections.get(interface_name)

    def get_all_connections(self) -> Dict[str, ConnectionInfo]:
        """Get connection information for all monitored interfaces.

        Returns:
            Dictionary mapping interface names to connection info
        """
        return self.connections.copy()

    def get_connected_interfaces(self) -> List[str]:
        """Get list of currently connected interfaces.

        Returns:
            List of connected interface names
        """
        return [
            name
            for name, info in self.connections.items()
            if info.state == ConnectionState.CONNECTED
        ]

    def is_interface_connected(self, interface_name: str) -> bool:
        """Check if an interface is connected.

        Args:
            interface_name: Name of the interface

        Returns:
            True if interface is connected
        """
        connection_info = self.connections.get(interface_name)
        return (
            connection_info is not None
            and connection_info.state == ConnectionState.CONNECTED
        )

    def add_connection_callback(self, callback):
        """Add callback for connection state changes.

        Args:
            callback: Function to call when connection state changes
                     Signature: callback(interface_name: str,
                                       connection_info: ConnectionInfo)
        """
        self.connection_callbacks.append(callback)

    def remove_connection_callback(self, callback):
        """Remove connection callback.

        Args:
            callback: Callback function to remove
        """
        if callback in self.connection_callbacks:
            self.connection_callbacks.remove(callback)

    def refresh_connections(self):
        """Manually refresh connection information."""
        if self._monitoring_active:
            self._update_connections()
        else:
            # One-time update
            self._update_connections()

    def get_connection_summary(self) -> Dict[str, any]:
        """Get summary of connection status.

        Returns:
            Dictionary with connection summary
        """
        connected_count = len(self.get_connected_interfaces())
        total_count = len(self.connections)

        avg_quality = 0.0
        if self.connections:
            avg_quality = sum(
                info.connection_quality for info in self.connections.values()
            ) / len(self.connections)

        return {
            "total_interfaces": total_count,
            "connected_interfaces": connected_count,
            "disconnected_interfaces": total_count - connected_count,
            "average_quality": avg_quality,
            "monitoring_active": self._monitoring_active,
            "last_update": max(
                (info.last_updated for info in self.connections.values()),
                default=datetime.now(),
            ).isoformat(),
        }

    def _detect_dns_servers(self, interface) -> List[str]:
        """Detect DNS servers for the given interface.

        Args:
            interface: Network interface object

        Returns:
            List of DNS server IP addresses
        """
        dns_servers = []

        try:
            import subprocess
            import sys

            if sys.platform.startswith("win"):
                # Windows: Use nslookup to get DNS servers
                result = subprocess.run(
                    ["nslookup", "google.com"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )

                if result.returncode == 0:
                    lines = result.stdout.split("\n")
                    for line in lines:
                        if "Server:" in line:
                            # Extract DNS server IP
                            parts = line.split()
                            if len(parts) >= 2:
                                dns_ip = parts[1].strip()
                                if self._is_valid_ip(dns_ip):
                                    dns_servers.append(dns_ip)

            else:
                # Unix-like systems: Read /etc/resolv.conf
                try:
                    with open("/etc/resolv.conf", "r") as f:
                        for line in f:
                            line = line.strip()
                            if line.startswith("nameserver"):
                                parts = line.split()
                                if len(parts) >= 2:
                                    dns_ip = parts[1]
                                    if self._is_valid_ip(dns_ip):
                                        dns_servers.append(dns_ip)
                except FileNotFoundError:
                    pass

            # Fallback: Common public DNS servers
            if not dns_servers:
                dns_servers = ["8.8.8.8", "8.8.4.4"]  # Google DNS

        except Exception as e:
            self.logger.warning(f"Failed to detect DNS servers: {e}")
            dns_servers = ["8.8.8.8", "8.8.4.4"]  # Fallback to Google DNS

        return dns_servers

    def _is_valid_ip(self, ip_string: str) -> bool:
        """Check if string is a valid IP address.

        Args:
            ip_string: String to check

        Returns:
            True if valid IP address
        """
        try:
            import ipaddress

            ipaddress.ip_address(ip_string)
            return True
        except ValueError:
            return False
