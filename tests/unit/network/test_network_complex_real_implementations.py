
"""
Network Complex Module Real Implementation Tests

This module provides comprehensive pytest-based unit tests for the actual
network complex module implementations, targeting 85%+ code coverage.

Key Difference: Tests REAL implementations instead of mocks.
Target: 2,400+ lines of advanced network infrastructure code.
"""

import sys
import os
import pytest
import threading
import time
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List

# Setup dependencies before importing network modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src_backup')))

# Import and setup dependency mocks
from mocks import setup_network_module_dependencies

# Setup dependencies
dependencies = setup_network_module_dependencies()

# Now import the real network modules
try:
    from utilities.network.network_connectivity.core.network_base import (
        NetworkOperationStatus, NetworkAlertLevel, NetworkOperationResult, NetworkToolBase
    )
    from utilities.network.network_connectivity.tools.wifi_analyzer import (
        WiFiSecurityType, WiFiStandard, ChannelBand, InterferenceType,
        AccessPoint, SignalMeasurement, ChannelInfo, InterferenceSource,
        SecurityAssessment, WiFiAlert, OUIDatabase, WiFiChannelMap, WiFiAnalyzer
    )
    from utilities.network.network_connectivity.tools.port_scanner import (
        ScanType, PortState, ScanPolicy, PortInfo, ScanTarget, ScanResult,
        VulnerabilityInfo, ServiceDetector, VulnerabilityAssessment, ScanEngine,
        PortScanner
    )
    REAL_IMPLEMENTATIONS_AVAILABLE = True
    print("✅ Real network implementations successfully imported!")
except ImportError as e:
    REAL_IMPLEMENTATIONS_AVAILABLE = False
    print(f"❌ Failed to import real implementations: {e}")


class TestNetworkOperationEnums:
    """Test network operation enums and basic structures."""
    
    def test_network_operation_status_enum(self):
        """Test NetworkOperationStatus enum values."""
        if not REAL_IMPLEMENTATIONS_AVAILABLE:
            pytest.skip("Real implementations not available")
        
        # Test all enum values exist
        assert NetworkOperationStatus.IDLE.value == "idle"
        assert NetworkOperationStatus.STARTING.value == "starting"
        assert NetworkOperationStatus.RUNNING.value == "running"
        assert NetworkOperationStatus.STOPPING.value == "stopping"
        assert NetworkOperationStatus.COMPLETED.value == "completed"
        assert NetworkOperationStatus.ERROR.value == "error"
    
    def test_network_alert_level_enum(self):
        """Test NetworkAlertLevel enum values."""
        if not REAL_IMPLEMENTATIONS_AVAILABLE:
            pytest.skip("Real implementations not available")
        
        assert NetworkAlertLevel.INFO.value == "info"
        assert NetworkAlertLevel.WARNING.value == "warning"
        assert NetworkAlertLevel.CRITICAL.value == "critical"
    
    def test_network_operation_result_dataclass(self):
        """Test NetworkOperationResult dataclass functionality."""
        if not REAL_IMPLEMENTATIONS_AVAILABLE:
            pytest.skip("Real implementations not available")
        
        # Test creation with required fields
        result = NetworkOperationResult(
            success=True,
            operation_type="test_operation",
            data={"key": "value"}
        )
        
        assert result.success is True
        assert result.operation_type == "test_operation"
        assert result.data == {"key": "value"}
        assert result.error_message is None
        assert result.timestamp is not None  # Auto-generated
        assert result.duration_ms is None


class TestWiFiSecurityEnums:
    """Test WiFi security-related enums."""
    
    def test_wifi_security_type_enum(self):
        """Test WiFiSecurityType enum completeness."""
        if not REAL_IMPLEMENTATIONS_AVAILABLE:
            pytest.skip("Real implementations not available")
        
        # Test critical security types
        assert WiFiSecurityType.OPEN.value == "Open"
        assert WiFiSecurityType.WEP.value == "WEP"
        assert WiFiSecurityType.WPA.value == "WPA"
        assert WiFiSecurityType.WPA2.value == "WPA2"
        assert WiFiSecurityType.WPA3.value == "WPA3"
        assert WiFiSecurityType.ENTERPRISE.value == "Enterprise"
    
    def test_wifi_standard_enum(self):
        """Test WiFiStandard enum for 802.11 standards."""
        if not REAL_IMPLEMENTATIONS_AVAILABLE:
            pytest.skip("Real implementations not available")
        
        # Test modern standards
        assert WiFiStandard.N.value == "802.11n"
        assert WiFiStandard.AC.value == "802.11ac" 
        assert WiFiStandard.AX.value == "802.11ax"
        assert WiFiStandard.BE.value == "802.11be"
    
    def test_channel_band_enum(self):
        """Test ChannelBand enum for frequency bands."""
        if not REAL_IMPLEMENTATIONS_AVAILABLE:
            pytest.skip("Real implementations not available")
        
        assert ChannelBand.BAND_2_4GHZ.value == "2.4GHz"
        assert ChannelBand.BAND_5GHZ.value == "5GHz"
        assert ChannelBand.BAND_6GHZ.value == "6GHz"


class TestOUIDatabase:
    """Test OUI Database functionality - SECURITY CRITICAL."""
    
    def test_oui_database_initialization(self):
        """Test OUI database initializes with vendor mappings."""
        if not REAL_IMPLEMENTATIONS_AVAILABLE:
            pytest.skip("Real implementations not available")
        
        oui_db = OUIDatabase()
        
        # Verify database is populated
        assert len(oui_db.oui_map) > 100  # Should have 200+ mappings
        assert isinstance(oui_db.oui_map, dict)
    
    def test_oui_database_intel_vendors(self):
        """Test Intel vendor identification."""
        if not REAL_IMPLEMENTATIONS_AVAILABLE:
            pytest.skip("Real implementations not available")
        
        oui_db = OUIDatabase()
        
        # Test known Intel MAC prefixes
        assert oui_db.get_vendor("00:1B:21:AA:BB:CC") == "Intel"
        assert oui_db.get_vendor("00:13:02:AA:BB:CC") == "Intel"
        assert oui_db.get_vendor("3C:A9:F4:AA:BB:CC") == "Intel"
    
    def test_oui_database_apple_vendors(self):
        """Test Apple vendor identification."""
        if not REAL_IMPLEMENTATIONS_AVAILABLE:
            pytest.skip("Real implementations not available")
        
        oui_db = OUIDatabase()
        
        # Test known Apple MAC prefixes
        assert oui_db.get_vendor("00:03:93:AA:BB:CC") == "Apple"
        assert oui_db.get_vendor("A4:C3:61:AA:BB:CC") == "Apple"
        assert oui_db.get_vendor("BC:52:B7:AA:BB:CC") == "Apple"
    
    def test_oui_database_unknown_vendor(self):
        """Test unknown vendor handling."""
        if not REAL_IMPLEMENTATIONS_AVAILABLE:
            pytest.skip("Real implementations not available")
        
        oui_db = OUIDatabase()
        
        # Test unknown MAC prefix
        assert oui_db.get_vendor("FF:FF:FF:AA:BB:CC") is None
        assert oui_db.get_vendor("99:99:99:AA:BB:CC") is None
    
    def test_oui_database_invalid_input(self):
        """Test invalid MAC address handling."""
        if not REAL_IMPLEMENTATIONS_AVAILABLE:
            pytest.skip("Real implementations not available")
        
        oui_db = OUIDatabase()
        
        # Test invalid inputs
        assert oui_db.get_vendor("") is None
        assert oui_db.get_vendor(None) is None
        assert oui_db.get_vendor("invalid") is None
        assert oui_db.get_vendor("12:34") is None  # Too short
    
    def test_oui_database_case_insensitive(self):
        """Test case insensitive MAC address lookup."""
        if not REAL_IMPLEMENTATIONS_AVAILABLE:
            pytest.skip("Real implementations not available")
        
        oui_db = OUIDatabase()
        
        # Test case variations
        assert oui_db.get_vendor("00:1b:21:aa:bb:cc") == "Intel"  # lowercase
        assert oui_db.get_vendor("00:1B:21:AA:BB:CC") == "Intel"  # uppercase
        assert oui_db.get_vendor("00:1b:21:AA:bb:CC") == "Intel"  # mixed case
    
    def test_oui_database_add_custom_vendor(self):
        """Test adding custom vendor mappings."""
        if not REAL_IMPLEMENTATIONS_AVAILABLE:
            pytest.skip("Real implementations not available")
        
        oui_db = OUIDatabase()
        
        # Add custom vendor
        oui_db.add_vendor_mapping("00:11:22", "TestVendor")
        
        # Verify custom vendor is found
        assert oui_db.get_vendor("00:11:22:AA:BB:CC") == "TestVendor"


class TestWiFiChannelMap:
    """Test WiFi Channel Mapping functionality - CORE NETWORK FEATURE."""
    
    def test_channel_frequency_2_4ghz(self):
        """Test 2.4GHz channel to frequency mapping."""
        if not REAL_IMPLEMENTATIONS_AVAILABLE:
            pytest.skip("Real implementations not available")
        
        # Test standard 2.4GHz channels
        assert WiFiChannelMap.get_frequency(1) == 2412
        assert WiFiChannelMap.get_frequency(6) == 2437
        assert WiFiChannelMap.get_frequency(11) == 2462
        assert WiFiChannelMap.get_frequency(14) == 2484  # Japan
    
    def test_channel_frequency_5ghz(self):
        """Test 5GHz channel to frequency mapping."""
        if not REAL_IMPLEMENTATIONS_AVAILABLE:
            pytest.skip("Real implementations not available")
        
        # Test common 5GHz channels
        assert WiFiChannelMap.get_frequency(36) == 5180
        assert WiFiChannelMap.get_frequency(149) == 5745
        assert WiFiChannelMap.get_frequency(165) == 5825
    
    def test_channel_frequency_6ghz(self):
        """Test 6GHz channel to frequency mapping."""
        if not REAL_IMPLEMENTATIONS_AVAILABLE:
            pytest.skip("Real implementations not available")
        
        # Test WiFi 6E channels
        assert WiFiChannelMap.get_frequency(1) == 5955  # 6GHz channel 1
        assert WiFiChannelMap.get_frequency(233) == 7115  # Upper 6GHz
    
    def test_channel_frequency_invalid(self):
        """Test invalid channel handling."""
        if not REAL_IMPLEMENTATIONS_AVAILABLE:
            pytest.skip("Real implementations not available")
        
        # Test invalid channels
        assert WiFiChannelMap.get_frequency(0) is None
        assert WiFiChannelMap.get_frequency(999) is None
        assert WiFiChannelMap.get_frequency(-1) is None
    
    def test_frequency_to_channel_conversion(self):
        """Test frequency to channel conversion."""
        if not REAL_IMPLEMENTATIONS_AVAILABLE:
            pytest.skip("Real implementations not available")
        
        # Test reverse lookup
        assert WiFiChannelMap.get_channel_from_frequency(2412) == 1
        assert WiFiChannelMap.get_channel_from_frequency(2437) == 6
        assert WiFiChannelMap.get_channel_from_frequency(5180) == 36
        assert WiFiChannelMap.get_channel_from_frequency(9999) is None
    
    def test_band_identification(self):
        """Test frequency band identification."""
        if not REAL_IMPLEMENTATIONS_AVAILABLE:
            pytest.skip("Real implementations not available")
        
        # Test band identification
        assert WiFiChannelMap.get_band(1) == ChannelBand.BAND_2_4GHZ
        assert WiFiChannelMap.get_band(6) == ChannelBand.BAND_2_4GHZ
        assert WiFiChannelMap.get_band(36) == ChannelBand.BAND_5GHZ
        assert WiFiChannelMap.get_band(149) == ChannelBand.BAND_5GHZ
        assert WiFiChannelMap.get_band(999) == ChannelBand.UNKNOWN
    
    def test_overlapping_channels_2_4ghz(self):
        """Test 2.4GHz channel overlap detection."""
        if not REAL_IMPLEMENTATIONS_AVAILABLE:
            pytest.skip("Real implementations not available")
        
        # Test channel 6 overlaps
        overlaps = WiFiChannelMap.get_overlapping_channels(6)
        expected_overlaps = [4, 5, 7, 8]  # Channels that overlap with 6
        
        for channel in expected_overlaps:
            assert channel in overlaps
    
    def test_non_overlapping_channels(self):
        """Test non-overlapping channel identification."""
        if not REAL_IMPLEMENTATIONS_AVAILABLE:
            pytest.skip("Real implementations not available")
        
        # Test 2.4GHz non-overlapping channels
        non_overlapping_2_4 = WiFiChannelMap.get_non_overlapping_channels(ChannelBand.BAND_2_4GHZ)
        assert non_overlapping_2_4 == [1, 6, 11]
        
        # Test 5GHz channels (should be most/all channels)
        non_overlapping_5 = WiFiChannelMap.get_non_overlapping_channels(ChannelBand.BAND_5GHZ)
        assert len(non_overlapping_5) > 20  # Many non-overlapping 5GHz channels


class TestPortScannerEnums:
    """Test port scanner enums and data structures."""
    
    def test_scan_type_enum(self):
        """Test ScanType enum values."""
        if not REAL_IMPLEMENTATIONS_AVAILABLE:
            pytest.skip("Real implementations not available")
        
        assert ScanType.TCP_CONNECT.value == "tcp_connect"
        assert ScanType.TCP_SYN.value == "tcp_syn"
        assert ScanType.UDP.value == "udp"
    
    def test_port_state_enum(self):
        """Test PortState enum values."""
        if not REAL_IMPLEMENTATIONS_AVAILABLE:
            pytest.skip("Real implementations not available")
        
        assert PortState.OPEN.value == "open"
        assert PortState.CLOSED.value == "closed"
        assert PortState.FILTERED.value == "filtered"
    
    def test_scan_policy_enum(self):
        """Test ScanPolicy enum values."""
        if not REAL_IMPLEMENTATIONS_AVAILABLE:
            pytest.skip("Real implementations not available")
        
        assert ScanPolicy.AGGRESSIVE.value == "aggressive"
        assert ScanPolicy.NORMAL.value == "normal"
        assert ScanPolicy.POLITE.value == "polite"
        assert ScanPolicy.STEALTH.value == "stealth"


class TestServiceDetector:
    """Test Service Detection functionality - SECURITY CRITICAL."""
    
    def test_service_detector_initialization(self):
        """Test ServiceDetector initializes with service signatures."""
        if not REAL_IMPLEMENTATIONS_AVAILABLE:
            pytest.skip("Real implementations not available")
        
        detector = ServiceDetector()
        
        # Verify service signatures are loaded
        assert len(detector.service_signatures) > 10
        assert 80 in detector.service_signatures  # HTTP
        assert 443 in detector.service_signatures  # HTTPS
        assert 22 in detector.service_signatures  # SSH
        assert 21 in detector.service_signatures  # FTP
    
    def test_service_detector_common_ports(self):
        """Test detection of common service ports."""
        if not REAL_IMPLEMENTATIONS_AVAILABLE:
            pytest.skip("Real implementations not available")
        
        detector = ServiceDetector()
        
        # Test common port mappings
        assert detector.service_signatures[80]["service"] == "http"
        assert detector.service_signatures[443]["service"] == "https"
        assert detector.service_signatures[22]["service"] == "ssh"
        assert detector.service_signatures[21]["service"] == "ftp"
        assert detector.service_signatures[25]["service"] == "smtp"
        assert detector.service_signatures[53]["service"] == "dns"
    
    def test_banner_analysis_ssh(self):
        """Test SSH banner analysis."""
        if not REAL_IMPLEMENTATIONS_AVAILABLE:
            pytest.skip("Real implementations not available")
        
        detector = ServiceDetector()
        
        # Test SSH banner analysis
        ssh_banner = "SSH-2.0-OpenSSH_7.4"
        result = detector._analyze_banner(22, ssh_banner)
        
        assert result is not None
        assert result["service"] == "ssh"
        assert "7.4" in result.get("version", "")
    
    def test_banner_analysis_http(self):
        """Test HTTP banner analysis."""
        if not REAL_IMPLEMENTATIONS_AVAILABLE:
            pytest.skip("Real implementations not available")
        
        detector = ServiceDetector()
        
        # Test HTTP server banner
        http_banner = "Server: Apache/2.4.41 (Ubuntu)"
        result = detector._analyze_banner(80, http_banner)
        
        assert result is not None
        assert "apache" in result["service"].lower()
        assert "2.4.41" in result.get("version", "")
    
    def test_banner_analysis_ftp(self):
        """Test FTP banner analysis."""
        if not REAL_IMPLEMENTATIONS_AVAILABLE:
            pytest.skip("Real implementations not available")
        
        detector = ServiceDetector()
        
        # Test FTP banner
        ftp_banner = "220 Welcome to FTP Server"
        result = detector._analyze_banner(21, ftp_banner)
        
        assert result is not None
        assert result["service"] == "ftp"
    
    def test_http_response_parsing(self):
        """Test HTTP response parsing functionality."""
        if not REAL_IMPLEMENTATIONS_AVAILABLE:
            pytest.skip("Real implementations not available")
        
        detector = ServiceDetector()
        
        # Test HTTP response parsing
        http_response = """HTTP/1.1 200 OK
Server: nginx/1.18.0
Content-Type: text/html
Connection: close

<!DOCTYPE html>
<html></html>"""
        
        result = detector._parse_http_response(http_response)
        
        assert result["service"] == "nginx"
        assert "nginx" in result["version"]
        assert result["extra"]["status_code"] == "200"
        assert result["extra"]["server"] == "nginx/1.18.0"


class TestVulnerabilityAssessment:
    """Test Vulnerability Assessment functionality - CRITICAL SECURITY."""
    
    def test_vulnerability_assessment_initialization(self):
        """Test VulnerabilityAssessment initializes with vulnerability patterns."""
        if not REAL_IMPLEMENTATIONS_AVAILABLE:
            pytest.skip("Real implementations not available")
        
        vuln_assessment = VulnerabilityAssessment()
        
        # Verify vulnerability patterns are loaded
        assert len(vuln_assessment.vulnerability_patterns) > 0
        assert "ftp" in vuln_assessment.vulnerability_patterns
        assert "ssh" in vuln_assessment.vulnerability_patterns
        assert "http" in vuln_assessment.vulnerability_patterns
    
    def test_cve_detection_vsftpd_backdoor(self):
        """Test CVE-2011-2523 vsftpd backdoor detection."""
        if not REAL_IMPLEMENTATIONS_AVAILABLE:
            pytest.skip("Real implementations not available")
        
        vuln_assessment = VulnerabilityAssessment()
        
        # Create vulnerable FTP service
        port_info = PortInfo(
            port=21,
            protocol="tcp",
            state=PortState.OPEN,
            service="ftp",
            banner="220 vsftpd 2.3.4 ready"
        )
        
        vulnerabilities = vuln_assessment._check_service_vulnerabilities(port_info)
        
        # Should detect the critical backdoor vulnerability
        assert len(vulnerabilities) > 0
        assert any("CVE-2011-2523" in vuln.cve_id for vuln in vulnerabilities)
        assert any("critical" in vuln.severity for vuln in vulnerabilities)
        assert any("backdoor" in vuln.description.lower() for vuln in vulnerabilities)
    
    def test_cve_detection_openssh(self):
        """Test OpenSSH vulnerability detection."""
        if not REAL_IMPLEMENTATIONS_AVAILABLE:
            pytest.skip("Real implementations not available")
        
        vuln_assessment = VulnerabilityAssessment()
        
        # Create vulnerable SSH service
        port_info = PortInfo(
            port=22,
            protocol="tcp",
            state=PortState.OPEN,
            service="ssh",
            banner="SSH-2.0-OpenSSH_6.0"
        )
        
        vulnerabilities = vuln_assessment._check_service_vulnerabilities(port_info)
        
        # Should detect SSH vulnerability
        assert len(vulnerabilities) > 0
        assert any("CVE-2016-0777" in vuln.cve_id for vuln in vulnerabilities)
        assert any("medium" in vuln.severity for vuln in vulnerabilities)
    
    def test_insecure_configuration_detection(self):
        """Test insecure configuration detection."""
        if not REAL_IMPLEMENTATIONS_AVAILABLE:
            pytest.skip("Real implementations not available")
        
        vuln_assessment = VulnerabilityAssessment()
        
        # Test Telnet insecure configuration
        telnet_port = PortInfo(
            port=23,
            protocol="tcp",
            state=PortState.OPEN,
            service="telnet"
        )
        
        vulnerabilities = vuln_assessment._check_insecure_configurations(telnet_port)
        
        assert len(vulnerabilities) > 0
        assert any("Unencrypted Telnet" in vuln.description for vuln in vulnerabilities)
        assert any("high" in vuln.severity for vuln in vulnerabilities)
        assert any("SSH" in vuln.recommendation for vuln in vulnerabilities)


class TestDataClassValidation:
    """Test network data class validation and functionality."""
    
    def test_access_point_dataclass(self):
        """Test AccessPoint dataclass functionality."""
        if not REAL_IMPLEMENTATIONS_AVAILABLE:
            pytest.skip("Real implementations not available")
        
        ap = AccessPoint(
            ssid="TestNetwork",
            bssid="00:11:22:33:44:55",
            signal_strength=-45,
            channel=6,
            frequency=2437,
            security=WiFiSecurityType.WPA2,
            standard=WiFiStandard.N,
            band=ChannelBand.BAND_2_4GHZ
        )
        
        assert ap.ssid == "TestNetwork"
        assert ap.signal_strength == -45
        assert ap.channel == 6
        assert ap.security == WiFiSecurityType.WPA2
        assert ap.band == ChannelBand.BAND_2_4GHZ
        assert ap.last_seen is not None  # Auto-generated
        assert ap.capabilities == []  # Default empty list
    
    def test_port_info_dataclass(self):
        """Test PortInfo dataclass functionality."""
        if not REAL_IMPLEMENTATIONS_AVAILABLE:
            pytest.skip("Real implementations not available")
        
        port_info = PortInfo(
            port=80,
            protocol="tcp",
            state=PortState.OPEN,
            service="http",
            version="Apache/2.4.41",
            banner="Server: Apache/2.4.41",
            response_time=15.5,
            confidence=0.9
        )
        
        assert port_info.port == 80
        assert port_info.protocol == "tcp"
        assert port_info.state == PortState.OPEN
        assert port_info.service == "http"
        assert port_info.response_time == 15.5
        assert port_info.confidence == 0.9
        assert port_info.extra_info == {}  # Default empty dict
    
    def test_vulnerability_info_dataclass(self):
        """Test VulnerabilityInfo dataclass functionality."""
        if not REAL_IMPLEMENTATIONS_AVAILABLE:
            pytest.skip("Real implementations not available")
        
        vuln = VulnerabilityInfo(
            cve_id="CVE-2023-12345",
            severity="high",
            description="Test vulnerability",
            service="http",
            port=80,
            recommendation="Update software"
        )
        
        assert vuln.cve_id == "CVE-2023-12345"
        assert vuln.severity == "high"
        assert vuln.service == "http"
        assert vuln.port == 80
        assert vuln.references == []  # Default empty list


class TestNetworkToolBaseIntegration:
    """Test NetworkToolBase integration - CRITICAL ARCHITECTURE."""
    
    def test_wifi_analyzer_initialization(self):
        """Test WiFiAnalyzer initialization and inheritance."""
        if not REAL_IMPLEMENTATIONS_AVAILABLE:
            pytest.skip("Real implementations not available")
        
        with patch('utilities.network.network_connectivity.core.platform_network.PlatformNetworkDetector'), \
             patch('utilities.network.network_connectivity.core.security_validator.SecurityValidator'):
            
            wifi_analyzer = WiFiAnalyzer()
            
            # Test inheritance from NetworkToolBase
            assert hasattr(wifi_analyzer, 'execute_operation')
            assert hasattr(wifi_analyzer, 'get_supported_protocols')
            assert hasattr(wifi_analyzer, 'validate_parameters')
            assert hasattr(wifi_analyzer, 'get_health_status')
            
            # Test WiFi-specific attributes
            assert hasattr(wifi_analyzer, 'oui_database')
            assert isinstance(wifi_analyzer.oui_database, OUIDatabase)
            assert wifi_analyzer.tool_name == "WiFiAnalyzer"
    
    def test_port_scanner_initialization(self):
        """Test PortScanner initialization and inheritance."""
        if not REAL_IMPLEMENTATIONS_AVAILABLE:
            pytest.skip("Real implementations not available")
        
        with patch('utilities.network.network_connectivity.core.platform_network.PlatformNetworkDetector'), \
             patch('utilities.network.network_connectivity.core.security_validator.SecurityValidator'):
            
            port_scanner = PortScanner()
            
            # Test inheritance from NetworkToolBase
            assert hasattr(port_scanner, 'execute_operation')
            assert hasattr(port_scanner, 'get_supported_protocols')
            assert hasattr(port_scanner, 'validate_parameters')
            assert hasattr(port_scanner, 'get_health_status')
            
            # Test PortScanner-specific attributes
            assert hasattr(port_scanner, 'service_detector')
            assert isinstance(port_scanner.service_detector, ServiceDetector)
            assert hasattr(port_scanner, 'vulnerability_assessment')
            assert isinstance(port_scanner.vulnerability_assessment, VulnerabilityAssessment)
            assert port_scanner.tool_name == "PortScanner"


class TestSecurityCriticalFunctions:
    """Test security-critical functions - HIGHEST PRIORITY."""
    
    def test_oui_database_security_mappings(self):
        """Test OUI database contains security-relevant vendor mappings."""
        if not REAL_IMPLEMENTATIONS_AVAILABLE:
            pytest.skip("Real implementations not available")
        
        oui_db = OUIDatabase()
        
        # Test major security vendors
        security_vendors = [
            ("00:1B:21", "Intel"),    # Common in enterprise
            ("00:03:93", "Apple"),    # iOS/macOS devices
            ("00:1A:A0", "Netgear"),  # Common routers
            ("00:0C:41", "Linksys"),  # Common routers
            ("00:07:7D", "D-Link"),   # Common routers
        ]
        
        for oui, expected_vendor in security_vendors:
            mac_address = f"{oui}:AA:BB:CC"
            detected_vendor = oui_db.get_vendor(mac_address)
            assert detected_vendor == expected_vendor, f"Failed to detect {expected_vendor} for {oui}"
    
    def test_vulnerability_cve_patterns(self):
        """Test CVE pattern matching accuracy."""
        if not REAL_IMPLEMENTATIONS_AVAILABLE:
            pytest.skip("Real implementations not available")
        
        vuln_assessment = VulnerabilityAssessment()
        
        # Test critical CVE patterns
        critical_cves = [
            ("ftp", "vsftpd 2.3.4", "CVE-2011-2523", "critical"),
            ("ssh", "OpenSSH_6.0", "CVE-2016-0777", "medium"),
            ("http", "Apache/2.2.", "CVE-2017-15710", "medium")
        ]
        
        for service, banner, expected_cve, expected_severity in critical_cves:
            port_info = PortInfo(
                port=21 if service == "ftp" else 22 if service == "ssh" else 80,
                protocol="tcp",
                state=PortState.OPEN,
                service=service,
                banner=banner
            )
            
            vulnerabilities = vuln_assessment._check_service_vulnerabilities(port_info)
            
            # Should detect the expected CVE
            matching_vulns = [v for v in vulnerabilities if expected_cve in (v.cve_id or "")]
            assert len(matching_vulns) > 0, f"Failed to detect {expected_cve} in {banner}"
            assert matching_vulns[0].severity == expected_severity


# Performance and Integration Tests
class TestPerformanceRequirements:
    """Test performance requirements and SLA compliance."""
    
    def test_oui_database_performance(self):
        """Test OUI database lookup performance."""
        if not REAL_IMPLEMENTATIONS_AVAILABLE:
            pytest.skip("Real implementations not available")
        
        oui_db = OUIDatabase()
        
        # Test multiple lookups quickly
        test_macs = [
            "00:1B:21:AA:BB:CC",
            "00:03:93:DD:EE:FF", 
            "00:1A: