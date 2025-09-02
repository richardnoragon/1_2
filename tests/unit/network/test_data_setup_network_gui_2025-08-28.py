"""
Test Data Setup for Network GUI Tests
Generated: 2025-08-28
Target: src/utilities/network/gui.py

This module provides test data, fixtures, and setup utilities for network GUI testing.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
from dataclasses import dataclass, asdict


@dataclass
class TestNetworkScanResult:
    """Test data for network scan results."""
    target: str
    port: int
    state: str
    service: str
    banner: str = ""
    timestamp: str = ""


@dataclass
class TestBandwidthData:
    """Test data for bandwidth monitoring."""
    timestamp: str
    download_speed: float
    upload_speed: float
    total_download: int
    total_upload: int


@dataclass
class TestWiFiNetwork:
    """Test data for WiFi networks."""
    ssid: str
    signal: int
    security: str
    frequency: int = 2400
    channel: int = 6


@dataclass
class TestHostDiscovery:
    """Test data for host discovery."""
    ip: str
    hostname: str
    status: str
    response_time: float
    mac_address: str = ""
    device_type: str = ""


@dataclass
class TestConnectivityResult:
    """Test data for connectivity tests."""
    target: str
    reachable: bool
    response_time: float
    error: str = ""
    http_status: int = 0


class NetworkGUITestData:
    """Provides comprehensive test data for network GUI testing."""
    
    def __init__(self):
        self.base_timestamp = datetime.now()
    
    def get_port_scan_results(self) -> List[TestNetworkScanResult]:
        """Generate port scan test results."""
        results = [
            TestNetworkScanResult(
                target="192.168.1.1",
                port=22,
                state="open",
                service="SSH",
                banner="OpenSSH_8.0",
                timestamp=self._get_timestamp(0)
            ),
            TestNetworkScanResult(
                target="192.168.1.1",
                port=80,
                state="open",
                service="HTTP",
                banner="Apache/2.4.41",
                timestamp=self._get_timestamp(1)
            ),
            TestNetworkScanResult(
                target="192.168.1.1",
                port=443,
                state="open",
                service="HTTPS",
                banner="nginx/1.18.0",
                timestamp=self._get_timestamp(2)
            ),
            TestNetworkScanResult(
                target="192.168.1.1",
                port=21,
                state="closed",
                service="",
                timestamp=self._get_timestamp(3)
            ),
            TestNetworkScanResult(
                target="192.168.1.1",
                port=25,
                state="filtered",
                service="",
                timestamp=self._get_timestamp(4)
            ),
            TestNetworkScanResult(
                target="10.0.0.1",
                port=3389,
                state="open",
                service="RDP",
                banner="Microsoft Terminal Services",
                timestamp=self._get_timestamp(5)
            ),
            TestNetworkScanResult(
                target="172.16.0.1",
                port=5900,
                state="open",
                service="VNC",
                banner="RealVNC 6.0",
                timestamp=self._get_timestamp(6)
            )
        ]
        return results
    
    def get_bandwidth_data(self) -> List[TestBandwidthData]:
        """Generate bandwidth monitoring test data."""
        results = []
        for i in range(30):  # 30 seconds of data
            results.append(TestBandwidthData(
                timestamp=self._get_timestamp(i),
                download_speed=1048576 + (i * 102400),  # Starting at 1MB/s, increasing
                upload_speed=524288 + (i * 51200),     # Starting at 0.5MB/s, increasing
                total_download=1073741824 * (i + 1),   # Cumulative
                total_upload=536870912 * (i + 1)       # Cumulative
            ))
        return results
    
    def get_wifi_networks(self) -> List[TestWiFiNetwork]:
        """Generate WiFi network test data."""
        results = [
            TestWiFiNetwork(
                ssid="HomeNetwork_5G",
                signal=-30,
                security="WPA3",
                frequency=5000,
                channel=36
            ),
            TestWiFiNetwork(
                ssid="HomeNetwork_2G",
                signal=-35,
                security="WPA2",
                frequency=2400,
                channel=6
            ),
            TestWiFiNetwork(
                ssid="Guest_WiFi",
                signal=-45,
                security="Open",
                frequency=2400,
                channel=11
            ),
            TestWiFiNetwork(
                ssid="Office_Secure",
                signal=-50,
                security="WPA2-Enterprise",
                frequency=5000,
                channel=149
            ),
            TestWiFiNetwork(
                ssid="Neighbor_Network",
                signal=-70,
                security="WPA2",
                frequency=2400,
                channel=1
            ),
            TestWiFiNetwork(
                ssid="",  # Hidden network
                signal=-60,
                security="WPA2",
                frequency=5000,
                channel=44
            )
        ]
        return results
    
    def get_host_discovery_results(self) -> List[TestHostDiscovery]:
        """Generate host discovery test data."""
        results = []
        
        # Generate results for 192.168.1.0/24 network
        alive_hosts = [1, 10, 15, 20, 50, 100, 150, 200, 254]
        
        for i in alive_hosts:
            results.append(TestHostDiscovery(
                ip=f"192.168.1.{i}",
                hostname=f"host-{i}" if i != 1 else "router",
                status="alive",
                response_time=10.0 + (i * 0.1),
                mac_address=f"00:11:22:33:44:{i:02x}",
                device_type="Router" if i == 1 else "Computer"
            ))
        
        return results
    
    def get_connectivity_results(self) -> List[TestConnectivityResult]:
        """Generate connectivity test results."""
        results = [
            TestConnectivityResult(
                target="8.8.8.8",
                reachable=True,
                response_time=15.5,
                http_status=200
            ),
            TestConnectivityResult(
                target="google.com",
                reachable=True,
                response_time=25.2,
                http_status=200
            ),
            TestConnectivityResult(
                target="bing.com",
                reachable=True,
                response_time=30.1,
                http_status=200
            ),
            TestConnectivityResult(
                target="cloudflare.com",
                reachable=True,
                response_time=18.7,
                http_status=200
            ),
            TestConnectivityResult(
                target="unreachable.example.invalid",
                reachable=False,
                response_time=0.0,
                error="DNS resolution failed"
            ),
            TestConnectivityResult(
                target="timeout.example.com",
                reachable=False,
                response_time=5000.0,
                error="Connection timeout"
            )
        ]
        return results
    
    def get_edge_case_data(self) -> Dict[str, Any]:
        """Generate edge case test data."""
        return {
            'empty_results': [],
            'large_port_range': list(range(1, 65536)),
            'invalid_targets': [
                "",
                "invalid..domain",
                "999.999.999.999",
                "not-a-valid-ip"
            ],
            'special_characters': [
                "测试网络.com",  # Unicode domain
                "xn--fsq.xn--0zwm56d",  # Punycode
                "192.168.1.1:8080",  # With port
                "http://example.com"  # With protocol
            ],
            'extreme_values': {
                'very_high_response_time': 99999.99,
                'negative_response_time': -1.0,
                'zero_bandwidth': 0.0,
                'extremely_high_bandwidth': 999999999999.0
            }
        }
    
    def _get_timestamp(self, offset_seconds: int = 0) -> str:
        """Get timestamp with optional offset."""
        timestamp = self.base_timestamp + timedelta(seconds=offset_seconds)
        return timestamp.isoformat()
    
    def save_test_data_to_files(self, output_dir: str = "."):
        """Save all test data to JSON files."""
        os.makedirs(output_dir, exist_ok=True)
        
        test_data = {
            'port_scan_results': [asdict(r) for r in self.get_port_scan_results()],
            'bandwidth_data': [asdict(r) for r in self.get_bandwidth_data()],
            'wifi_networks': [asdict(r) for r in self.get_wifi_networks()],
            'host_discovery': [asdict(r) for r in self.get_host_discovery_results()],
            'connectivity_results': [asdict(r) for r in self.get_connectivity_results()],
            'edge_case_data': self.get_edge_case_data()
        }
        
        # Save comprehensive test data
        test_data_file = os.path.join(output_dir, "network_gui_test_data_2025-08-28.json")
        with open(test_data_file, 'w') as f:
            json.dump(test_data, f, indent=2, default=str)
        
        # Save individual data sets
        for key, data in test_data.items():
            filename = os.path.join(output_dir, f"test_data_{key}_2025-08-28.json")
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        
        print(f"Test data saved to {output_dir}")
        print(f"Main file: {test_data_file}")


class MockNetworkOperations:
    """Mock network operations for testing."""
    
    @staticmethod
    def mock_socket_connect_success(*args, **kwargs):
        """Mock successful socket connection."""
        return 0
    
    @staticmethod
    def mock_socket_connect_failure(*args, **kwargs):
        """Mock failed socket connection."""
        return 1
    
    @staticmethod
    def mock_socket_connect_timeout(*args, **kwargs):
        """Mock connection timeout."""
        raise TimeoutError("Connection timed out")
    
    @staticmethod
    def mock_dns_resolution_failure(*args, **kwargs):
        """Mock DNS resolution failure."""
        raise OSError("Name or service not known")
    
    @staticmethod
    def get_mock_service_responses() -> Dict[int, Dict[str, str]]:
        """Get mock service banner responses."""
        return {
            22: {'banner': 'SSH-2.0-OpenSSH_8.0', 'service': 'SSH'},
            80: {'banner': 'Apache/2.4.41 (Ubuntu)', 'service': 'HTTP'},
            443: {'banner': 'nginx/1.18.0', 'service': 'HTTPS'},
            21: {'banner': 'vsftpd 3.0.3', 'service': 'FTP'},
            25: {'banner': 'Postfix smtpd', 'service': 'SMTP'},
            53: {'banner': 'BIND 9.16.1', 'service': 'DNS'},
            3389: {'banner': 'Microsoft Terminal Services', 'service': 'RDP'},
            5900: {'banner': 'RealVNC 6.0', 'service': 'VNC'}
        }


def create_test_data_files():
    """Create all test data files."""
    print("Creating test data files for Network GUI tests...")
    
    # Create test data
    test_data_generator = NetworkGUITestData()
    
    # Create data directory
    data_dir = "test_data"
    test_data_generator.save_test_data_to_files(data_dir)
    
    # Create mock configuration
    mock_config = {
        'mock_settings': {
            'enable_socket_mocking': True,
            'enable_dns_mocking': True,
            'simulate_network_delays': False,
            'default_timeout': 5.0
        },
        'network_responses': MockNetworkOperations.get_mock_service_responses(),
        'test_networks': [
            '192.168.1.0/24',
            '10.0.0.0/24',
            '172.16.0.0/24'
        ],
        'test_targets': [
            '8.8.8.8',
            'google.com',
            'bing.com',
            'cloudflare.com'
        ]
    }
    
    mock_config_file = os.path.join(data_dir, "mock_config_2025-08-28.json")
    with open(mock_config_file, 'w') as f:
        json.dump(mock_config, f, indent=2)
    
    print(f"✓ Test data files created in {data_dir}/")
    print(f"✓ Mock configuration saved to {mock_config_file}")


if __name__ == "__main__":
    create_test_data_files()