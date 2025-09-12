"""Cross-platform network interface detection and monitoring utilities."""

import platform
import logging
import subprocess
import re
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class NetworkPlatform(Enum):
    """Supported network platforms."""
    WINDOWS = "windows"
    MACOS = "macos"
    LINUX = "linux"
    UNKNOWN = "unknown"


@dataclass
class NetworkInterface:
    """Network interface information."""
    name: str
    display_name: str
    is_active: bool
    is_wireless: bool
    mac_address: Optional[str]
    ip_addresses: List[str]
    interface_type: str
    speed_mbps: Optional[int]
    mtu: Optional[int]
    bytes_sent: Optional[int] = None
    bytes_recv: Optional[int] = None
    packets_sent: Optional[int] = None
    packets_recv: Optional[int] = None


@dataclass
class NetworkStats:
    """Network statistics for an interface."""
    interface_name: str
    bytes_sent: int
    bytes_recv: int
    packets_sent: int
    packets_recv: int
    errors_in: int
    errors_out: int
    drops_in: int
    drops_out: int
    timestamp: float


class NetworkDetectorBase(ABC):
    """Abstract base class for platform-specific network detection."""
    
    def __init__(self):
        self.logger = logging.getLogger(
            f'RFU.NetworkConnectivity.{self.__class__.__name__}'
        )
    
    @abstractmethod
    def get_network_interfaces(self) -> List[NetworkInterface]:
        """Get list of network interfaces."""
        pass
    
    @abstractmethod
    def get_interface_stats(self, interface_name: str) -> Optional[
            NetworkStats]:
        """Get statistics for a specific interface."""
        pass
    
    @abstractmethod
    def is_interface_wireless(self, interface_name: str) -> bool:
        """Check if interface is wireless."""
        pass
    
    @abstractmethod
    def get_default_gateway(self) -> Optional[str]:
        """Get the default gateway IP address."""
        pass


class WindowsNetworkDetector(NetworkDetectorBase):
    """Windows-specific network detection using WMI and system commands."""
    
    def __init__(self):
        super().__init__()
        self._wmi_available = False
        try:
            import wmi
            self._wmi = wmi.WMI()
            self._wmi_available = True
        except ImportError:
            self.logger.warning("WMI not available, using fallback methods")
    
    def get_network_interfaces(self) -> List[NetworkInterface]:
        """Get network interfaces using WMI or fallback methods."""
        interfaces = []
        
        if PSUTIL_AVAILABLE:
            interfaces.extend(self._get_interfaces_psutil())
        elif self._wmi_available:
            interfaces.extend(self._get_interfaces_wmi())
        else:
            interfaces.extend(self._get_interfaces_fallback())
        
        return interfaces
    
    def _get_interfaces_psutil(self) -> List[NetworkInterface]:
        """Get interfaces using psutil."""
        interfaces = []
        
        try:
            net_if_addrs = psutil.net_if_addrs()
            net_if_stats = psutil.net_if_stats()
            
            for name, addresses in net_if_addrs.items():
                if name in net_if_stats:
                    stats = net_if_stats[name]
                    
                    # Extract IP addresses and MAC
                    ip_addresses = []
                    mac_address = None
                    
                    for addr in addresses:
                        if addr.family == 2:  # AF_INET (IPv4)
                            ip_addresses.append(addr.address)
                        elif addr.family == 23:  # AF_LINK (MAC)
                            mac_address = addr.address
                    
                    interface = NetworkInterface(
                        name=name,
                        display_name=name,
                        is_active=stats.isup,
                        is_wireless=self.is_interface_wireless(name),
                        mac_address=mac_address,
                        ip_addresses=ip_addresses,
                        interface_type=self._get_interface_type(name),
                        speed_mbps=stats.speed if stats.speed > 0 else None,
                        mtu=stats.mtu
                    )
                    interfaces.append(interface)
        
        except Exception as e:
            self.logger.error(f"Error getting interfaces with psutil: {e}")
        
        return interfaces
    
    def _get_interfaces_wmi(self) -> List[NetworkInterface]:
        """Get interfaces using WMI."""
        interfaces = []
        
        try:
            for adapter in self._wmi.Win32_NetworkAdapter():
                if adapter.NetEnabled:
                    # Get configuration
                    config = None
                    for cfg in self._wmi.Win32_NetworkAdapterConfiguration():
                        if cfg.Index == adapter.Index:
                            config = cfg
                            break
                    
                    ip_addresses = []
                    if config and config.IPAddress:
                        ip_addresses = [
                            ip for ip in config.IPAddress
                            if not ip.startswith('fe80')
                        ]
                    
                    interface = NetworkInterface(
                        name=adapter.NetConnectionID or adapter.Name,
                        display_name=adapter.Description or adapter.Name,
                        is_active=adapter.NetEnabled,
                        is_wireless=('wireless' in adapter.Name.lower() or
                                     'wifi' in adapter.Name.lower()),
                        mac_address=adapter.MACAddress,
                        ip_addresses=ip_addresses,
                        interface_type=adapter.AdapterType or "Unknown",
                        speed_mbps=(int(adapter.Speed / 1000000)
                                    if adapter.Speed else None),
                        mtu=config.MTU if config else None
                    )
                    interfaces.append(interface)
        
        except Exception as e:
            self.logger.error(f"Error getting interfaces with WMI: {e}")
        
        return interfaces
    
    def _get_interfaces_fallback(self) -> List[NetworkInterface]:
        """Fallback method using system commands."""
        interfaces = []
        
        try:
            # Use ipconfig to get interface information
            result = subprocess.run(
                ['ipconfig', '/all'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                interfaces = self._parse_ipconfig_output(result.stdout)
        
        except Exception as e:
            self.logger.error(f"Error with fallback method: {e}")
        
        return interfaces
    
    def _parse_ipconfig_output(self, output: str) -> List[NetworkInterface]:
        """Parse ipconfig output to extract interface information."""
        interfaces = []
        current_interface = None
        
        for line in output.split('\n'):
            line = line.strip()
            
            if 'adapter' in line.lower() and ':' in line:
                # New adapter section
                if current_interface:
                    interfaces.append(current_interface)
                
                name = line.split(':')[0].strip()
                current_interface = {
                    'name': name,
                    'display_name': name,
                    'is_active': False,
                    'is_wireless': 'wireless' in name.lower(),
                    'mac_address': None,
                    'ip_addresses': [],
                    'interface_type': 'Unknown',
                    'speed_mbps': None,
                    'mtu': None
                }
            
            elif current_interface:
                if 'Physical Address' in line:
                    mac = line.split(':')[1].strip()
                    current_interface['mac_address'] = mac
                elif 'IPv4 Address' in line:
                    ip = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                    if ip:
                        current_interface['ip_addresses'].append(ip.group(1))
                        current_interface['is_active'] = True
        
        if current_interface:
            interfaces.append(current_interface)
        
        # Convert to NetworkInterface objects
        return [NetworkInterface(**iface) for iface in interfaces]
    
    def get_interface_stats(self, interface_name: str) -> Optional[
            NetworkStats]:
        """Get interface statistics."""
        if PSUTIL_AVAILABLE:
            try:
                stats = psutil.net_io_counters(pernic=True)
                if interface_name in stats:
                    stat = stats[interface_name]
                    return NetworkStats(
                        interface_name=interface_name,
                        bytes_sent=stat.bytes_sent,
                        bytes_recv=stat.bytes_recv,
                        packets_sent=stat.packets_sent,
                        packets_recv=stat.packets_recv,
                        errors_in=stat.errin,
                        errors_out=stat.errout,
                        drops_in=stat.dropin,
                        drops_out=stat.dropout,
                        timestamp=0  # psutil doesn't provide timestamp
                    )
            except Exception as e:
                self.logger.error(
                    f"Error getting stats for {interface_name}: {e}")
        
        return None
    
    def is_interface_wireless(self, interface_name: str) -> bool:
        """Check if interface is wireless."""
        wireless_keywords = ['wireless', 'wifi', 'wi-fi', '802.11', 'wlan']
        name_lower = interface_name.lower()
        return any(keyword in name_lower for keyword in wireless_keywords)
    
    def get_default_gateway(self) -> Optional[str]:
        """Get default gateway."""
        try:
            result = subprocess.run(
                ['route', 'print', '0.0.0.0'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if '0.0.0.0' in line and 'Gateway' not in line:
                        parts = line.split()
                        if len(parts) >= 3:
                            return parts[2]
        
        except Exception as e:
            self.logger.error(f"Error getting default gateway: {e}")
        
        return None
    
    def _get_interface_type(self, interface_name: str) -> str:
        """Determine interface type based on name."""
        name_lower = interface_name.lower()
        
        if any(keyword in name_lower for keyword in 
               ['ethernet', 'eth', 'lan']):
            return "Ethernet"
        elif any(keyword in name_lower for keyword in 
                 ['wireless', 'wifi', 'wlan']):
            return "Wireless"
        elif 'loopback' in name_lower:
            return "Loopback"
        elif 'tunnel' in name_lower:
            return "Tunnel"
        else:
            return "Unknown"


class LinuxNetworkDetector(NetworkDetectorBase):
    """Linux-specific network detection using /proc and system commands."""
    
    def get_network_interfaces(self) -> List[NetworkInterface]:
        """Get network interfaces using /proc and system commands."""
        interfaces = []
        
        if PSUTIL_AVAILABLE:
            interfaces.extend(self._get_interfaces_psutil())
        else:
            interfaces.extend(self._get_interfaces_proc())
        
        return interfaces
    
    def _get_interfaces_psutil(self) -> List[NetworkInterface]:
        """Get interfaces using psutil (similar to Windows implementation)."""
        interfaces = []
        
        try:
            net_if_addrs = psutil.net_if_addrs()
            net_if_stats = psutil.net_if_stats()
            
            for name, addresses in net_if_addrs.items():
                if name in net_if_stats:
                    stats = net_if_stats[name]
                    
                    ip_addresses = []
                    mac_address = None
                    
                    for addr in addresses:
                        if addr.family == 2:  # AF_INET
                            ip_addresses.append(addr.address)
                        elif addr.family == 17:  # AF_PACKET (Linux MAC)
                            mac_address = addr.address
                    
                    interface = NetworkInterface(
                        name=name,
                        display_name=name,
                        is_active=stats.isup,
                        is_wireless=self.is_interface_wireless(name),
                        mac_address=mac_address,
                        ip_addresses=ip_addresses,
                        interface_type=self._get_interface_type(name),
                        speed_mbps=stats.speed if stats.speed > 0 else None,
                        mtu=stats.mtu
                    )
                    interfaces.append(interface)
        
        except Exception as e:
            self.logger.error(f"Error getting interfaces with psutil: {e}")
        
        return interfaces
    
    def _get_interfaces_proc(self) -> List[NetworkInterface]:
        """Get interfaces using /proc filesystem."""
        interfaces = []
        
        try:
            # Read /proc/net/dev for interface names
            with open('/proc/net/dev', 'r') as f:
                lines = f.readlines()[2:]  # Skip header lines
                
                for line in lines:
                    parts = line.split(':')
                    if len(parts) >= 2:
                        name = parts[0].strip()
                        
                        interface = NetworkInterface(
                            name=name,
                            display_name=name,
                            is_active=self._is_interface_up(name),
                            is_wireless=self.is_interface_wireless(name),
                            mac_address=self._get_mac_address(name),
                            ip_addresses=self._get_ip_addresses(name),
                            interface_type=self._get_interface_type(name),
                            speed_mbps=self._get_interface_speed(name),
                            mtu=self._get_interface_mtu(name)
                        )
                        interfaces.append(interface)
        
        except Exception as e:
            self.logger.error(f"Error reading /proc/net/dev: {e}")
        
        return interfaces
    
    def _is_interface_up(self, interface_name: str) -> bool:
        """Check if interface is up."""
        try:
            with open(f'/sys/class/net/{interface_name}/operstate', 'r') as f:
                state = f.read().strip()
                return state == 'up'
        except Exception:
            return False
    
    def _get_mac_address(self, interface_name: str) -> Optional[str]:
        """Get MAC address for interface."""
        try:
            with open(f'/sys/class/net/{interface_name}/address', 'r') as f:
                return f.read().strip()
        except Exception:
            return None
    
    def _get_ip_addresses(self, interface_name: str) -> List[str]:
        """Get IP addresses for interface."""
        ip_addresses = []
        
        try:
            result = subprocess.run(
                ['ip', 'addr', 'show', interface_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'inet ' in line:
                        ip_match = re.search(
                            r'inet (\d+\.\d+\.\d+\.\d+)', line)
                        if ip_match:
                            ip_addresses.append(ip_match.group(1))
        
        except Exception as e:
            self.logger.error(f"Error getting IP addresses: {e}")
        
        return ip_addresses
    
    def _get_interface_speed(self, interface_name: str) -> Optional[int]:
        """Get interface speed in Mbps."""
        try:
            with open(f'/sys/class/net/{interface_name}/speed', 'r') as f:
                speed = int(f.read().strip())
                return speed if speed > 0 else None
        except Exception:
            return None
    
    def _get_interface_mtu(self, interface_name: str) -> Optional[int]:
        """Get interface MTU."""
        try:
            with open(f'/sys/class/net/{interface_name}/mtu', 'r') as f:
                return int(f.read().strip())
        except Exception:
            return None
    
    def get_interface_stats(self, interface_name: str) -> Optional[
            NetworkStats]:
        """Get interface statistics."""
        if PSUTIL_AVAILABLE:
            try:
                stats = psutil.net_io_counters(pernic=True)
                if interface_name in stats:
                    stat = stats[interface_name]
                    return NetworkStats(
                        interface_name=interface_name,
                        bytes_sent=stat.bytes_sent,
                        bytes_recv=stat.bytes_recv,
                        packets_sent=stat.packets_sent,
                        packets_recv=stat.packets_recv,
                        errors_in=stat.errin,
                        errors_out=stat.errout,
                        drops_in=stat.dropin,
                        drops_out=stat.dropout,
                        timestamp=0
                    )
            except Exception as e:
                self.logger.error(f"Error getting stats: {e}")
        
        return None
    
    def is_interface_wireless(self, interface_name: str) -> bool:
        """Check if interface is wireless."""
        # Check if wireless directory exists
        wireless_path = f'/sys/class/net/{interface_name}/wireless'
        try:
            import os
            return os.path.exists(wireless_path)
        except Exception:
            # Fallback to name-based detection
            wireless_keywords = ['wlan', 'wifi', 'wireless']
            return any(keyword in interface_name.lower()
                       for keyword in wireless_keywords)
    
    def get_default_gateway(self) -> Optional[str]:
        """Get default gateway."""
        try:
            result = subprocess.run(
                ['ip', 'route', 'show', 'default'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'default via' in line:
                        parts = line.split()
                        if len(parts) >= 3:
                            return parts[2]
        
        except Exception as e:
            self.logger.error(f"Error getting default gateway: {e}")
        
        return None
    
    def _get_interface_type(self, interface_name: str) -> str:
        """Determine interface type."""
        name_lower = interface_name.lower()
        
        if name_lower.startswith('eth'):
            return "Ethernet"
        elif name_lower.startswith('wlan') or name_lower.startswith('wifi'):
            return "Wireless"
        elif name_lower.startswith('lo'):
            return "Loopback"
        elif name_lower.startswith('tun') or name_lower.startswith('tap'):
            return "Tunnel"
        else:
            return "Unknown"


class MacOSNetworkDetector(NetworkDetectorBase):
    """macOS-specific network detection using system commands."""
    
    def get_network_interfaces(self) -> List[NetworkInterface]:
        """Get network interfaces using system commands."""
        interfaces = []
        
        if PSUTIL_AVAILABLE:
            interfaces.extend(self._get_interfaces_psutil())
        else:
            interfaces.extend(self._get_interfaces_ifconfig())
        
        return interfaces
    
    def _get_interfaces_psutil(self) -> List[NetworkInterface]:
        """Get interfaces using psutil."""
        interfaces = []
        
        try:
            net_if_addrs = psutil.net_if_addrs()
            net_if_stats = psutil.net_if_stats()
            
            for name, addresses in net_if_addrs.items():
                if name in net_if_stats:
                    stats = net_if_stats[name]
                    
                    ip_addresses = []
                    mac_address = None
                    
                    for addr in addresses:
                        if addr.family == 2:  # AF_INET
                            ip_addresses.append(addr.address)
                        elif addr.family == 18:  # AF_LINK (macOS)
                            mac_address = addr.address
                    
                    interface = NetworkInterface(
                        name=name,
                        display_name=name,
                        is_active=stats.isup,
                        is_wireless=self.is_interface_wireless(name),
                        mac_address=mac_address,
                        ip_addresses=ip_addresses,
                        interface_type=self._get_interface_type(name),
                        speed_mbps=stats.speed if stats.speed > 0 else None,
                        mtu=stats.mtu
                    )
                    interfaces.append(interface)
        
        except Exception as e:
            self.logger.error(f"Error getting interfaces with psutil: {e}")
        
        return interfaces
    
    def _get_interfaces_ifconfig(self) -> List[NetworkInterface]:
        """Get interfaces using ifconfig command."""
        interfaces = []
        
        try:
            result = subprocess.run(
                ['ifconfig'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                interfaces = self._parse_ifconfig_output(result.stdout)
        
        except Exception as e:
            self.logger.error(f"Error with ifconfig: {e}")
        
        return interfaces
    
    def _parse_ifconfig_output(self, output: str) -> List[NetworkInterface]:
        """Parse ifconfig output."""
        interfaces = []
        current_interface = None
        
        for line in output.split('\n'):
            if line and not line.startswith('\t') and not line.startswith(' '):
                # New interface
                if current_interface:
                    interfaces.append(NetworkInterface(**current_interface))
                
                parts = line.split(':')
                if len(parts) >= 2:
                    name = parts[0].strip()
                    current_interface = {
                        'name': name,
                        'display_name': name,
                        'is_active': 'UP' in line,
                        'is_wireless': self.is_interface_wireless(name),
                        'mac_address': None,
                        'ip_addresses': [],
                        'interface_type': self._get_interface_type(name),
                        'speed_mbps': None,
                        'mtu': None
                    }
            
            elif current_interface and line.strip():
                line = line.strip()
                
                if line.startswith('ether '):
                    current_interface['mac_address'] = line.split()[1]
                elif line.startswith('inet '):
                    ip = line.split()[1]
                    current_interface['ip_addresses'].append(ip)
                elif 'mtu' in line:
                    mtu_match = re.search(r'mtu (\d+)', line)
                    if mtu_match:
                        current_interface['mtu'] = int(mtu_match.group(1))
        
        if current_interface:
            interfaces.append(NetworkInterface(**current_interface))
        
        return interfaces
    
    def get_interface_stats(self, interface_name: str) -> Optional[
            NetworkStats]:
        """Get interface statistics."""
        if PSUTIL_AVAILABLE:
            try:
                stats = psutil.net_io_counters(pernic=True)
                if interface_name in stats:
                    stat = stats[interface_name]
                    return NetworkStats(
                        interface_name=interface_name,
                        bytes_sent=stat.bytes_sent,
                        bytes_recv=stat.bytes_recv,
                        packets_sent=stat.packets_sent,
                        packets_recv=stat.packets_recv,
                        errors_in=stat.errin,
                        errors_out=stat.errout,
                        drops_in=stat.dropin,
                        drops_out=stat.dropout,
                        timestamp=0
                    )
            except Exception as e:
                self.logger.error(f"Error getting stats: {e}")
        
        return None
    
    def is_interface_wireless(self, interface_name: str) -> bool:
        """Check if interface is wireless."""
        wireless_keywords = ['en1', 'en0']  # Common wireless interfaces
        if interface_name in wireless_keywords:
            # Check if it's actually wireless using system_profiler
            try:
                result = subprocess.run(
                    ['system_profiler', 'SPAirPortDataType'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                return interface_name in result.stdout
            except Exception:
                pass
        
        return ('wifi' in interface_name.lower() or
                'wireless' in interface_name.lower())
    
    def get_default_gateway(self) -> Optional[str]:
        """Get default gateway."""
        try:
            result = subprocess.run(
                ['route', 'get', 'default'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'gateway:' in line:
                        return line.split(':')[1].strip()
        
        except Exception as e:
            self.logger.error(f"Error getting default gateway: {e}")
        
        return None
    
    def _get_interface_type(self, interface_name: str) -> str:
        """Determine interface type."""
        name_lower = interface_name.lower()
        
        if name_lower.startswith('en'):
            return "Ethernet"  # Could be wireless too
        elif name_lower.startswith('lo'):
            return "Loopback"
        elif name_lower.startswith('utun') or name_lower.startswith('tun'):
            return "Tunnel"
        else:
            return "Unknown"


class PlatformNetworkDetector:
    """Cross-platform network interface detector."""
    
    def __init__(self):
        self.platform = self._detect_platform()
        self.detector = self._create_detector()
        self.logger = logging.getLogger(
            'RFU.NetworkConnectivity.PlatformNetworkDetector'
        )
    
    def _detect_platform(self) -> NetworkPlatform:
        """Detect the current platform."""
        system = platform.system().lower()
        
        if system == 'windows':
            return NetworkPlatform.WINDOWS
        elif system == 'darwin':
            return NetworkPlatform.MACOS
        elif system == 'linux':
            return NetworkPlatform.LINUX
        else:
            return NetworkPlatform.UNKNOWN
    
    def _create_detector(self) -> NetworkDetectorBase:
        """Create platform-specific detector."""
        if self.platform == NetworkPlatform.WINDOWS:
            return WindowsNetworkDetector()
        elif self.platform == NetworkPlatform.MACOS:
            return MacOSNetworkDetector()
        elif self.platform == NetworkPlatform.LINUX:
            return LinuxNetworkDetector()
        else:
            # Fallback to a basic detector
            return WindowsNetworkDetector()  # Most generic
    
    def get_network_interfaces(self) -> List[NetworkInterface]:
        """Get list of network interfaces."""
        try:
            return self.detector.get_network_interfaces()
        except Exception as e:
            self.logger.error(f"Error getting network interfaces: {e}")
            return []
    
    def get_interface_stats(self, interface_name: str) -> Optional[
            NetworkStats]:
        """Get statistics for a specific interface."""
        try:
            return self.detector.get_interface_stats(interface_name)
        except Exception as e:
            self.logger.error(f"Error getting stats for {interface_name}: {e}")
            return None
    
    def is_interface_wireless(self, interface_name: str) -> bool:
        """Check if interface is wireless."""
        try:
            return self.detector.is_interface_wireless(interface_name)
        except Exception as e:
            self.logger.error(f"Error checking wireless status: {e}")
            return False
    
    def get_default_gateway(self) -> Optional[str]:
        """Get the default gateway IP address."""
        try:
            return self.detector.get_default_gateway()
        except Exception as e:
            self.logger.error(f"Error getting default gateway: {e}")
            return None
    
    def get_active_interfaces(self) -> List[NetworkInterface]:
        """Get only active network interfaces."""
        all_interfaces = self.get_network_interfaces()
        return [iface for iface in all_interfaces if iface.is_active]
    
    def get_interface_by_name(self, name: str) -> Optional[NetworkInterface]:
        """Get interface by name."""
        interfaces = self.get_network_interfaces()
        for interface in interfaces:
            if interface.name == name:
                return interface
        return None
    
    def is_supported(self) -> bool:
        """Check if current platform is supported."""
        return self.platform != NetworkPlatform.UNKNOWN
    
    def get_capabilities(self) -> Dict[str, bool]:
        """Get platform capabilities."""
        return {
            'interface_detection': True,
            'statistics_collection': PSUTIL_AVAILABLE,
            'wireless_detection': True,
            'gateway_detection': True,
            'real_time_monitoring': PSUTIL_AVAILABLE,
            'platform_supported': self.is_supported()
        }