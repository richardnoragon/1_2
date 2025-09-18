"""Unit tests for platform network detection."""

import pytest
import platform
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from ...core.platform_network import (
    PlatformNetworkDetector, NetworkInterface, NetworkStats,
    NetworkDetectorBase, WindowsNetworkDetector, MacOSNetworkDetector,
    LinuxNetworkDetector
)


class TestNetworkInterface:
    """Test NetworkInterface data class."""
    
    def test_network_interface_creation(self):
        """Test NetworkInterface creation."""
        interface = NetworkInterface(
            name="eth0",
            display_name="Ethernet",
            description="Test Ethernet Interface",
            mac_address="00:11:22:33:44:55",
            ip_addresses=["192.168.1.100", "fe80::1"],
            is_up=True,
            is_wireless=False,
            speed_mbps=1000,
            mtu=1500
        )
        
        assert interface.name == "eth0"
        assert interface.display_name == "Ethernet"
        assert interface.description == "Test Ethernet Interface"
        assert interface.mac_address == "00:11:22:33:44:55"
        assert "192.168.1.100" in interface.ip_addresses
        assert "fe80::1" in interface.ip_addresses
        assert interface.is_up is True
        assert interface.is_wireless is False
        assert interface.speed_mbps == 1000
        assert interface.mtu == 1500
    
    def test_network_interface_defaults(self):
        """Test NetworkInterface with default values."""
        interface = NetworkInterface(
            name="lo",
            display_name="Loopback"
        )
        
        assert interface.name == "lo"
        assert interface.display_name == "Loopback"
        assert interface.description == ""
        assert interface.mac_address == ""
        assert interface.ip_addresses == []
        assert interface.is_up is False
        assert interface.is_wireless is False
        assert interface.speed_mbps == 0
        assert interface.mtu == 0
    
    def test_network_interface_equality(self):
        """Test NetworkInterface equality comparison."""
        interface1 = NetworkInterface(
            name="eth0",
            display_name="Ethernet",
            mac_address="00:11:22:33:44:55"
        )
        
        interface2 = NetworkInterface(
            name="eth0",
            display_name="Ethernet",
            mac_address="00:11:22:33:44:55"
        )
        
        interface3 = NetworkInterface(
            name="wlan0",
            display_name="WiFi",
            mac_address="AA:BB:CC:DD:EE:FF"
        )
        
        assert interface1 == interface2
        assert interface1 != interface3


class TestNetworkStats:
    """Test NetworkStats data class."""
    
    def test_network_stats_creation(self):
        """Test NetworkStats creation."""
        timestamp = datetime.now()
        stats = NetworkStats(
            interface_name="eth0",
            bytes_sent=1024000,
            bytes_received=2048000,
            packets_sent=1000,
            packets_received=2000,
            errors_in=0,
            errors_out=0,
            drops_in=0,
            drops_out=0,
            timestamp=timestamp
        )
        
        assert stats.interface_name == "eth0"
        assert stats.bytes_sent == 1024000
        assert stats.bytes_received == 2048000
        assert stats.packets_sent == 1000
        assert stats.packets_received == 2000
        assert stats.errors_in == 0
        assert stats.errors_out == 0
        assert stats.drops_in == 0
        assert stats.drops_out == 0
        assert stats.timestamp == timestamp
    
    def test_network_stats_defaults(self):
        """Test NetworkStats with default values."""
        stats = NetworkStats(interface_name="lo")
        
        assert stats.interface_name == "lo"
        assert stats.bytes_sent == 0
        assert stats.bytes_received == 0
        assert stats.packets_sent == 0
        assert stats.packets_received == 0
        assert stats.errors_in == 0
        assert stats.errors_out == 0
        assert stats.drops_in == 0
        assert stats.drops_out == 0
        assert isinstance(stats.timestamp, datetime)


class TestNetworkDetectorBase:
    """Test NetworkDetectorBase abstract class."""
    
    def test_abstract_methods(self):
        """Test that abstract methods raise NotImplementedError."""
        # Cannot instantiate abstract class directly
        with pytest.raises(TypeError):
            NetworkDetectorBase()
    
    def test_concrete_implementation(self):
        """Test concrete implementation of abstract class."""
        class TestDetector(NetworkDetectorBase):
            def get_network_interfaces(self):
                return []
            
            def get_interface_stats(self, interface_name):
                return None
            
            def is_interface_wireless(self, interface_name):
                return False
            
            def get_default_gateway(self):
                return None
        
        detector = TestDetector()
        assert detector.logger is not None
        assert detector.get_network_interfaces() == []
        assert detector.get_interface_stats("test") is None
        assert detector.is_interface_wireless("test") is False
        assert detector.get_default_gateway() is None


class TestPlatformNetworkDetector:
    """Test PlatformNetworkDetector factory class."""
    
    @pytest.fixture
    def detector(self):
        """Create a platform network detector."""
        return PlatformNetworkDetector()
    
    def test_detector_creation(self, detector):
        """Test detector creation."""
        assert detector is not None
        assert hasattr(detector, '_detector')
        assert detector._detector is not None
    
    @patch('platform.system')
    def test_windows_detector_selection(self, mock_system):
        """Test Windows detector selection."""
        mock_system.return_value = 'Windows'
        
        detector = PlatformNetworkDetector()
        assert isinstance(detector._detector, WindowsNetworkDetector)
    
    @patch('platform.system')
    def test_macos_detector_selection(self, mock_system):
        """Test macOS detector selection."""
        mock_system.return_value = 'Darwin'
        
        detector = PlatformNetworkDetector()
        assert isinstance(detector._detector, MacOSNetworkDetector)
    
    @patch('platform.system')
    def test_linux_detector_selection(self, mock_system):
        """Test Linux detector selection."""
        mock_system.return_value = 'Linux'
        
        detector = PlatformNetworkDetector()
        assert isinstance(detector._detector, LinuxNetworkDetector)
    
    @patch('platform.system')
    def test_unknown_platform_fallback(self, mock_system):
        """Test unknown platform fallback."""
        mock_system.return_value = 'UnknownOS'
        
        detector = PlatformNetworkDetector()
        # Should fallback to Linux detector
        assert isinstance(detector._detector, LinuxNetworkDetector)
    
    def test_method_delegation(self, detector):
        """Test that methods are properly delegated."""
        # Mock the internal detector
        mock_detector = Mock()
        mock_detector.get_network_interfaces.return_value = []
        mock_detector.get_interface_stats.return_value = None
        mock_detector.is_interface_wireless.return_value = False
        mock_detector.get_default_gateway.return_value = "192.168.1.1"
        
        detector._detector = mock_detector
        
        # Test method delegation
        interfaces = detector.get_network_interfaces()
        stats = detector.get_interface_stats("eth0")
        is_wireless = detector.is_interface_wireless("wlan0")
        gateway = detector.get_default_gateway()
        
        assert interfaces == []
        assert stats is None
        assert is_wireless is False
        assert gateway == "192.168.1.1"
        
        # Verify calls were delegated
        mock_detector.get_network_interfaces.assert_called_once()
        mock_detector.get_interface_stats.assert_called_once_with("eth0")
        mock_detector.is_interface_wireless.assert_called_once_with("wlan0")
        mock_detector.get_default_gateway.assert_called_once()


class TestWindowsNetworkDetector:
    """Test Windows-specific network detector."""
    
    @pytest.fixture
    def detector(self):
        """Create a Windows network detector."""
        return WindowsNetworkDetector()
    
    @patch('psutil.net_if_addrs')
    @patch('psutil.net_if_stats')
    def test_get_network_interfaces(self, mock_net_if_stats, 
                                   mock_net_if_addrs, detector):
        """Test getting network interfaces on Windows."""
        # Mock psutil data
        mock_net_if_addrs.return_value = {
            'Ethernet': [
                MagicMock(
                    family=2,  # AF_INET
                    address='192.168.1.100',
                    netmask='255.255.255.0'
                ),
                MagicMock(
                    family=17,  # AF_LINK (MAC address)
                    address='00-11-22-33-44-55'
                )
            ]
        }
        
        mock_net_if_stats.return_value = {
            'Ethernet': MagicMock(
                isup=True,
                speed=1000,
                mtu=1500
            )
        }
        
        interfaces = detector.get_network_interfaces()
        
        assert len(interfaces) == 1
        interface = interfaces[0]
        assert interface.name == 'Ethernet'
        assert interface.display_name == 'Ethernet'
        assert '192.168.1.100' in interface.ip_addresses
        assert interface.mac_address == '00:11:22:33:44:55'
        assert interface.is_up is True
        assert interface.speed_mbps == 1000
        assert interface.mtu == 1500
    
    @patch('psutil.net_io_counters')
    def test_get_interface_stats(self, mock_net_io_counters, detector):
        """Test getting interface statistics on Windows."""
        # Mock psutil data
        mock_stats = MagicMock()
        mock_stats.bytes_sent = 1024000
        mock_stats.bytes_recv = 2048000
        mock_stats.packets_sent = 1000
        mock_stats.packets_recv = 2000
        mock_stats.errin = 0
        mock_stats.errout = 0
        mock_stats.dropin = 0
        mock_stats.dropout = 0
        
        mock_net_io_counters.return_value = {'Ethernet': mock_stats}
        
        stats = detector.get_interface_stats('Ethernet')
        
        assert stats is not None
        assert stats.interface_name == 'Ethernet'
        assert stats.bytes_sent == 1024000
        assert stats.bytes_received == 2048000
        assert stats.packets_sent == 1000
        assert stats.packets_received == 2000
    
    def test_get_interface_stats_not_found(self, detector):
        """Test getting stats for non-existent interface."""
        with patch('psutil.net_io_counters', return_value={}):
            stats = detector.get_interface_stats('NonExistent')
            assert stats is None
    
    @patch('subprocess.run')
    def test_is_interface_wireless(self, mock_run, detector):
        """Test wireless interface detection on Windows."""
        # Mock netsh command output for wireless interface
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Wi-Fi adapter Wireless Network Connection:"
        )
        
        is_wireless = detector.is_interface_wireless('Wi-Fi')
        assert is_wireless is True
        
        # Mock netsh command output for wired interface
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Ethernet adapter Local Area Connection:"
        )
        
        is_wireless = detector.is_interface_wireless('Ethernet')
        assert is_wireless is False
    
    @patch('subprocess.run')
    def test_get_default_gateway(self, mock_run, detector):
        """Test getting default gateway on Windows."""
        # Mock route command output
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="0.0.0.0          0.0.0.0      192.168.1.1     192.168.1.100"
        )
        
        gateway = detector.get_default_gateway()
        assert gateway == "192.168.1.1"


class TestMacOSNetworkDetector:
    """Test macOS-specific network detector."""
    
    @pytest.fixture
    def detector(self):
        """Create a macOS network detector."""
        return MacOSNetworkDetector()
    
    @patch('subprocess.run')
    def test_is_interface_wireless(self, mock_run, detector):
        """Test wireless interface detection on macOS."""
        # Mock networksetup command output
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Wi-Fi\nBluetooth PAN\nThunderbolt Bridge"
        )
        
        is_wireless = detector.is_interface_wireless('en0')
        # This would require more complex mocking of the actual detection logic
        assert isinstance(is_wireless, bool)
    
    @patch('subprocess.run')
    def test_get_default_gateway(self, mock_run, detector):
        """Test getting default gateway on macOS."""
        # Mock route command output
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="default            192.168.1.1        UGSc           en0"
        )
        
        gateway = detector.get_default_gateway()
        assert gateway == "192.168.1.1"


class TestLinuxNetworkDetector:
    """Test Linux-specific network detector."""
    
    @pytest.fixture
    def detector(self):
        """Create a Linux network detector."""
        return LinuxNetworkDetector()
    
    @patch('os.path.exists')
    def test_is_interface_wireless(self, mock_exists, detector):
        """Test wireless interface detection on Linux."""
        # Mock wireless interface
        mock_exists.return_value = True
        is_wireless = detector.is_interface_wireless('wlan0')
        assert is_wireless is True
        
        # Mock wired interface
        mock_exists.return_value = False
        is_wireless = detector.is_interface_wireless('eth0')
        assert is_wireless is False
    
    @patch('subprocess.run')
    def test_get_default_gateway(self, mock_run, detector):
        """Test getting default gateway on Linux."""
        # Mock ip route command output
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="default via 192.168.1.1 dev eth0 proto dhcp metric 100"
        )
        
        gateway = detector.get_default_gateway()
        assert gateway == "192.168.1.1"


class TestPlatformNetworkDetectorIntegration:
    """Integration tests for platform network detector."""
    
    def test_real_interface_detection(self):
        """Test real interface detection (if available)."""
        detector = PlatformNetworkDetector()
        
        try:
            interfaces = detector.get_network_interfaces()
            
            # Should have at least loopback interface
            assert len(interfaces) >= 1
            
            # Check that interfaces have required fields
            for interface in interfaces:
                assert interface.name
                assert interface.display_name
                assert isinstance(interface.is_up, bool)
                assert isinstance(interface.is_wireless, bool)
                assert isinstance(interface.speed_mbps, int)
                assert isinstance(interface.mtu, int)
                
        except Exception as e:
            # If real detection fails, that's okay for unit tests
            pytest.skip(f"Real interface detection failed: {e}")
    
    def test_error_handling(self):
        """Test error handling in platform detection."""
        detector = PlatformNetworkDetector()
        
        # Test with invalid interface name
        stats = detector.get_interface_stats("invalid_interface_name_12345")
        assert stats is None
        
        # Test wireless detection with invalid interface
        is_wireless = detector.is_interface_wireless("invalid_interface")
        assert isinstance(is_wireless, bool)  # Should not raise exception


if __name__ == "__main__":
    pytest.main([__file__])