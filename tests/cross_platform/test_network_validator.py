#!/usr/bin/env python3
"""Test suite for CrossPlatformNetworkValidator.

This module provides comprehensive tests for the network validation
framework across Windows, Linux, and macOS platforms.
"""

import json
import os
import platform
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, Mock, call, patch

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from cross_platform.network_validator import (CrossPlatformNetworkValidator,
                                              LinuxNetworkValidator,
                                              MacOSNetworkValidator,
                                              NetworkCapability, NetworkTool,
                                              ValidationResult,
                                              WindowsNetworkValidator)


class TestNetworkCapability(unittest.TestCase):
    """Test cases for NetworkCapability dataclass."""
    
    def test_network_capability_creation(self):
        """Test NetworkCapability creation with all fields."""
        capability = NetworkCapability(
            name="ping",
            available=True,
            version="1.0",
            command="ping",
            dependencies=["socket"],
            platform_specific=True
        )
        
        self.assertEqual(capability.name, "ping")
        self.assertTrue(capability.available)
        self.assertEqual(capability.version, "1.0")
        self.assertEqual(capability.command, "ping")
        self.assertEqual(len(capability.dependencies), 1)
        self.assertTrue(capability.platform_specific)
    
    def test_network_capability_defaults(self):
        """Test NetworkCapability creation with default values."""
        capability = NetworkCapability(name="traceroute", available=False)
        
        self.assertEqual(capability.name, "traceroute")
        self.assertFalse(capability.available)
        self.assertIsNone(capability.version)
        self.assertIsNone(capability.command)
        self.assertEqual(capability.dependencies, [])
        self.assertFalse(capability.platform_specific)


class TestNetworkTool(unittest.TestCase):
    """Test cases for NetworkTool dataclass."""
    
    def test_network_tool_creation(self):
        """Test NetworkTool creation with all fields."""
        capabilities = [
            NetworkCapability("scan", True),
            NetworkCapability("monitor", True)
        ]
        
        tool = NetworkTool(
            name="PortScanner",
            description="Network port scanning tool",
            executable_path="/usr/bin/nmap",
            capabilities=capabilities,
            performance_metrics={"scan_time": 2.5},
            platform_support={"linux", "windows", "darwin"}
        )
        
        self.assertEqual(tool.name, "PortScanner")
        self.assertEqual(tool.description, "Network port scanning tool")
        self.assertEqual(tool.executable_path, "/usr/bin/nmap")
        self.assertEqual(len(tool.capabilities), 2)
        self.assertEqual(tool.performance_metrics["scan_time"], 2.5)
        self.assertEqual(len(tool.platform_support), 3)
    
    def test_network_tool_defaults(self):
        """Test NetworkTool creation with default values."""
        tool = NetworkTool(name="TestTool", description="Test tool")
        
        self.assertEqual(tool.name, "TestTool")
        self.assertEqual(tool.description, "Test tool")
        self.assertIsNone(tool.executable_path)
        self.assertEqual(tool.capabilities, [])
        self.assertEqual(tool.performance_metrics, {})
        self.assertEqual(tool.platform_support, set())


class TestValidationResult(unittest.TestCase):
    """Test cases for ValidationResult dataclass."""
    
    def test_validation_result_success(self):
        """Test successful validation result."""
        result = ValidationResult(
            tool_name="PingTest",
            platform="linux",
            success=True,
            capabilities_tested=5,
            capabilities_passed=5,
            performance_score=95.0,
            execution_time=1.2
        )
        
        self.assertEqual(result.tool_name, "PingTest")
        self.assertEqual(result.platform, "linux")
        self.assertTrue(result.success)
        self.assertEqual(result.capabilities_tested, 5)
        self.assertEqual(result.capabilities_passed, 5)
        self.assertEqual(result.performance_score, 95.0)
        self.assertEqual(result.execution_time, 1.2)
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(len(result.warnings), 0)
    
    def test_validation_result_failure(self):
        """Test failed validation result."""
        result = ValidationResult(
            tool_name="FailedTest",
            platform="windows",
            success=False,
            capabilities_tested=3,
            capabilities_passed=1,
            performance_score=25.0,
            errors=["Permission denied", "Service unavailable"],
            warnings=["Slow response time"]
        )
        
        self.assertFalse(result.success)
        self.assertEqual(len(result.errors), 2)
        self.assertEqual(len(result.warnings), 1)
        self.assertEqual(result.performance_score, 25.0)


class TestWindowsNetworkValidator(unittest.TestCase):
    """Test cases for WindowsNetworkValidator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = WindowsNetworkValidator()
    
    def test_initialization(self):
        """Test Windows validator initialization."""
        self.assertEqual(self.validator.platform_name, "Windows")
        self.assertIn('ping', self.validator.required_utilities)
        self.assertIn('netstat', self.validator.required_utilities)
        self.assertIn('ipconfig', self.validator.required_utilities)
    
    @patch('platform.version')
    @patch('subprocess.run')
    def test_validate_platform_requirements_success(self, mock_run, mock_version):
        """Test successful Windows platform requirements validation."""
        mock_version.return_value = "10.0.19041"
        mock_run.return_value = Mock(returncode=0)
        
        # Mock ctypes for admin check
        with patch('ctypes.windll.shell32.IsUserAnAdmin', return_value=True):
            requirements = self.validator.validate_platform_requirements()
        
        self.assertTrue(requirements['windows_version'])
        self.assertTrue(requirements['admin_privileges'])
        self.assertTrue(requirements['networking_stack'])
    
    @patch('subprocess.run')
    def test_get_network_utilities_success(self, mock_run):
        """Test successful network utilities detection on Windows."""
        # Mock 'where' command success
        mock_run.return_value = Mock(
            returncode=0,
            stdout="C:\\Windows\\System32\\ping.exe\n"
        )
        
        utilities = self.validator.get_network_utilities()
        
        # Should find at least the ping utility
        ping_utility = next((u for u in utilities if u.name == 'ping'), None)
        self.assertIsNotNone(ping_utility)
        self.assertTrue(ping_utility.available)
        self.assertEqual(ping_utility.command, 'ping.exe')
    
    @patch('subprocess.run')
    def test_get_network_utilities_not_found(self, mock_run):
        """Test network utilities detection when tools not found."""
        # Mock 'where' command failure
        mock_run.return_value = Mock(returncode=1)
        
        utilities = self.validator.get_network_utilities()
        
        # All utilities should be marked as unavailable
        for utility in utilities:
            if utility.name in self.validator.required_utilities:
                self.assertFalse(utility.available)
    
    @patch('socket.socket')
    def test_test_network_permissions_raw_socket_success(self, mock_socket):
        """Test raw socket permission check success."""
        mock_sock = Mock()
        mock_socket.return_value = mock_sock
        
        permissions = self.validator.test_network_permissions()
        
        self.assertTrue(permissions['raw_socket'])
        mock_sock.close.assert_called_once()
    
    @patch('socket.socket')
    def test_test_network_permissions_raw_socket_failure(self, mock_socket):
        """Test raw socket permission check failure."""
        mock_socket.side_effect = PermissionError("Access denied")
        
        permissions = self.validator.test_network_permissions()
        
        self.assertFalse(permissions['raw_socket'])
    
    @patch('subprocess.run')
    @patch('socket.gethostbyname')
    def test_benchmark_network_performance(self, mock_gethostbyname, mock_run):
        """Test network performance benchmarking on Windows."""
        # Mock DNS resolution
        mock_gethostbyname.return_value = "8.8.8.8"
        
        # Mock ping command
        mock_run.return_value = Mock(
            returncode=0,
            stdout="Average = 25ms"
        )
        
        metrics = self.validator.benchmark_network_performance()
        
        self.assertIn('dns_resolution_ms', metrics)
        self.assertIn('ping_localhost_ms', metrics)
        self.assertGreater(metrics['dns_resolution_ms'], 0)
        self.assertEqual(metrics['ping_localhost_ms'], 25.0)


class TestLinuxNetworkValidator(unittest.TestCase):
    """Test cases for LinuxNetworkValidator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = LinuxNetworkValidator()
    
    def test_initialization(self):
        """Test Linux validator initialization."""
        self.assertEqual(self.validator.platform_name, "Linux")
        self.assertIn('ping', self.validator.required_utilities)
        self.assertIn('traceroute', self.validator.required_utilities)
        self.assertIn('ip', self.validator.required_utilities)
    
    @patch('pathlib.Path.exists')
    @patch('os.geteuid')
    @patch('socket.socket')
    def test_validate_platform_requirements_success(self, mock_socket, mock_geteuid, mock_exists):
        """Test successful Linux platform requirements validation."""
        mock_exists.return_value = True
        mock_geteuid.return_value = 0  # Root user
        
        # Mock netlink socket
        mock_sock = Mock()
        mock_socket.return_value = mock_sock
        
        requirements = self.validator.validate_platform_requirements()
        
        self.assertTrue(requirements['proc_filesystem'])
        self.assertTrue(requirements['sysfs_filesystem'])
        self.assertTrue(requirements['root_privileges'])
        self.assertTrue(requirements['netlink_support'])
    
    @patch('subprocess.run')
    def test_get_network_utilities_success(self, mock_run):
        """Test successful network utilities detection on Linux."""
        # Mock 'which' command success
        mock_run.return_value = Mock(
            returncode=0,
            stdout="/bin/ping\n"
        )
        
        utilities = self.validator.get_network_utilities()
        
        # Should find at least the ping utility
        ping_utility = next((u for u in utilities if u.name == 'ping'), None)
        self.assertIsNotNone(ping_utility)
        self.assertTrue(ping_utility.available)
        self.assertEqual(ping_utility.command, 'ping')
    
    @patch('subprocess.run')
    def test_test_network_permissions_iptables_success(self, mock_run):
        """Test iptables permission check success."""
        mock_run.return_value = Mock(returncode=0)
        
        permissions = self.validator.test_network_permissions()
        
        self.assertTrue(permissions['iptables_access'])
    
    @patch('subprocess.run')
    @patch('socket.gethostbyname')
    @patch('builtins.open', create=True)
    def test_benchmark_network_performance(self, mock_open, mock_gethostbyname, mock_run):
        """Test network performance benchmarking on Linux."""
        # Mock DNS resolution
        mock_gethostbyname.return_value = "8.8.8.8"
        
        # Mock ping command
        mock_run.return_value = Mock(
            returncode=0,
            stdout="rtt min/avg/max/mdev = 10.0/15.0/20.0/5.0 ms"
        )
        
        # Mock /proc/net/dev file
        mock_open.return_value.__enter__.return_value.readlines.return_value = [
            "Inter-|   Receive                                                |  Transmit\n",
            " face |bytes    packets errs drop fifo frame compressed multicast|bytes    packets errs drop fifo colls carrier compressed\n",
            "    lo:       0       0    0    0    0     0          0         0        0       0    0    0    0     0       0          0\n",
            "  eth0:  123456     789    0    0    0     0          0         0   654321     321    0    0    0     0       0          0\n"
        ]
        
        metrics = self.validator.benchmark_network_performance()
        
        self.assertIn('dns_resolution_ms', metrics)
        self.assertIn('ping_localhost_ms', metrics)
        self.assertIn('proc_net_parse_ms', metrics)
        self.assertGreater(metrics['dns_resolution_ms'], 0)
        self.assertEqual(metrics['ping_localhost_ms'], 15.0)
        self.assertEqual(metrics['proc_net_interfaces'], 2)


class TestMacOSNetworkValidator(unittest.TestCase):
    """Test cases for MacOSNetworkValidator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = MacOSNetworkValidator()
    
    def test_initialization(self):
        """Test macOS validator initialization."""
        self.assertEqual(self.validator.platform_name, "macOS")
        self.assertIn('ping', self.validator.required_utilities)
        self.assertIn('scutil', self.validator.required_utilities)
        self.assertIn('networksetup', self.validator.required_utilities)
    
    @patch('subprocess.run')
    @patch('os.geteuid')
    def test_validate_platform_requirements_success(self, mock_geteuid, mock_run):
        """Test successful macOS platform requirements validation."""
        mock_geteuid.return_value = 0  # Root user
        
        # Mock various system commands
        mock_run.side_effect = [
            Mock(returncode=0, stdout="10.15.7"),  # sw_vers
            Mock(returncode=0),  # scutil
            Mock(returncode=0)   # pfctl
        ]
        
        requirements = self.validator.validate_platform_requirements()
        
        self.assertTrue(requirements['macos_version'])
        self.assertTrue(requirements['root_privileges'])
        self.assertTrue(requirements['system_configuration'])
        self.assertTrue(requirements['packet_filter'])
    
    @patch('subprocess.run')
    def test_get_network_utilities_success(self, mock_run):
        """Test successful network utilities detection on macOS."""
        # Mock 'which' command success
        mock_run.return_value = Mock(
            returncode=0,
            stdout="/usr/bin/ping\n"
        )
        
        utilities = self.validator.get_network_utilities()
        
        # Should find at least the ping utility
        ping_utility = next((u for u in utilities if u.name == 'ping'), None)
        self.assertIsNotNone(ping_utility)
        self.assertTrue(ping_utility.available)
        self.assertEqual(ping_utility.command, 'ping')
    
    @patch('subprocess.run')
    def test_test_network_permissions_pfctl_success(self, mock_run):
        """Test pfctl permission check success."""
        mock_run.return_value = Mock(returncode=0)
        
        permissions = self.validator.test_network_permissions()
        
        self.assertTrue(permissions['packet_filter_access'])
    
    @patch('subprocess.run')
    @patch('socket.gethostbyname')
    def test_benchmark_network_performance(self, mock_gethostbyname, mock_run):
        """Test network performance benchmarking on macOS."""
        # Mock DNS resolution
        mock_gethostbyname.return_value = "8.8.8.8"
        
        # Mock ping and scutil commands
        mock_run.side_effect = [
            Mock(returncode=0, stdout="round-trip min/avg/max/stddev = 10.0/15.0/20.0/5.0 ms"),  # ping
            Mock(returncode=0, stdout="State:/Network/Global/IPv4")  # scutil
        ]
        
        metrics = self.validator.benchmark_network_performance()
        
        self.assertIn('dns_resolution_ms', metrics)
        self.assertIn('ping_localhost_ms', metrics)
        self.assertIn('scutil_query_ms', metrics)
        self.assertGreater(metrics['dns_resolution_ms'], 0)
        self.assertEqual(metrics['ping_localhost_ms'], 15.0)
        self.assertGreater(metrics['scutil_query_ms'], 0)


class TestCrossPlatformNetworkValidator(unittest.TestCase):
    """Test cases for CrossPlatformNetworkValidator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = CrossPlatformNetworkValidator(verbose=False)
    
    @patch('platform.system')
    def test_create_platform_validator_windows(self, mock_system):
        """Test Windows platform validator creation."""
        mock_system.return_value = "Windows"
        
        validator = CrossPlatformNetworkValidator()
        
        self.assertEqual(validator.platform, "windows")
        self.assertIsInstance(validator.validator, WindowsNetworkValidator)
    
    @patch('platform.system')
    def test_create_platform_validator_linux(self, mock_system):
        """Test Linux platform validator creation."""
        mock_system.return_value = "Linux"
        
        validator = CrossPlatformNetworkValidator()
        
        self.assertEqual(validator.platform, "linux")
        self.assertIsInstance(validator.validator, LinuxNetworkValidator)
    
    @patch('platform.system')
    def test_create_platform_validator_macos(self, mock_system):
        """Test macOS platform validator creation."""
        mock_system.return_value = "Darwin"
        
        validator = CrossPlatformNetworkValidator()
        
        self.assertEqual(validator.platform, "darwin")
        self.assertIsInstance(validator.validator, MacOSNetworkValidator)
    
    @patch('platform.system')
    def test_create_platform_validator_unknown(self, mock_system):
        """Test unknown platform fallback to Linux validator."""
        mock_system.return_value = "FreeBSD"
        
        with patch('logging.Logger.warning') as mock_warning:
            validator = CrossPlatformNetworkValidator()
            
            self.assertEqual(validator.platform, "freebsd")
            self.assertIsInstance(validator.validator, LinuxNetworkValidator)
            mock_warning.assert_called_once()
    
    def test_define_network_tools(self):
        """Test network tools definition."""
        tools = self.validator._define_network_tools()
        
        self.assertGreater(len(tools), 0)
        
        # Check that all expected tools are defined
        tool_names = [tool.name for tool in tools]
        expected_tools = [
            "WiFiAnalyzer",
            "PortScanner", 
            "BandwidthMonitor",
            "LANFileTransfer",
            "NetworkDiagnostics",
            "SecurityScanner",
            "TrafficAnalyzer"
        ]
        
        for expected_tool in expected_tools:
            self.assertIn(expected_tool, tool_names)
        
        # Check platform support
        for tool in tools:
            self.assertIn("windows", tool.platform_support)
            self.assertIn("linux", tool.platform_support)
            self.assertIn("darwin", tool.platform_support)
    
    @patch.object(WindowsNetworkValidator, 'validate_platform_requirements')
    def test_validate_platform_requirements_success(self, mock_validate):
        """Test successful platform requirements validation."""
        mock_validate.return_value = {
            'windows_version': True,
            'admin_privileges': True,
            'networking_stack': True
        }
        
        with patch('platform.system', return_value="Windows"):
            validator = CrossPlatformNetworkValidator()
            result = validator.validate_platform_requirements()
        
        self.assertTrue(result.success)
        self.assertEqual(result.tool_name, "Platform Requirements")
        self.assertEqual(result.capabilities_tested, 3)
        self.assertEqual(result.capabilities_passed, 3)
        self.assertEqual(result.performance_score, 100.0)
    
    @patch.object(WindowsNetworkValidator, 'validate_platform_requirements')
    def test_validate_platform_requirements_failure(self, mock_validate):
        """Test failed platform requirements validation."""
        mock_validate.return_value = {
            'windows_version': True,
            'admin_privileges': False,  # Missing admin rights
            'networking_stack': False   # Networking issues
        }
        
        with patch('platform.system', return_value="Windows"):
            validator = CrossPlatformNetworkValidator()
            result = validator.validate_platform_requirements()
        
        self.assertFalse(result.success)
        self.assertGreater(len(result.errors), 0)
        self.assertEqual(result.capabilities_passed, 1)
        self.assertEqual(result.performance_score, 50.0)
    
    @patch.object(WindowsNetworkValidator, 'get_network_utilities')
    def test_validate_network_utilities_success(self, mock_get_utilities):
        """Test successful network utilities validation."""
        mock_utilities = [
            NetworkCapability("ping", True, "1.0", "ping"),
            NetworkCapability("netstat", True, "2.0", "netstat"),
            NetworkCapability("tracert", True, "1.5", "tracert")
        ]
        mock_get_utilities.return_value = mock_utilities
        
        with patch('platform.system', return_value="Windows"):
            validator = CrossPlatformNetworkValidator()
            result = validator.validate_network_utilities()
        
        self.assertTrue(result.success)
        self.assertEqual(result.capabilities_tested, 3)
        self.assertEqual(result.capabilities_passed, 3)
        self.assertEqual(result.performance_score, 100.0)
    
    @patch.object(WindowsNetworkValidator, 'get_network_utilities')
    def test_validate_network_utilities_missing_critical(self, mock_get_utilities):
        """Test network utilities validation with missing critical utilities."""
        mock_utilities = [
            NetworkCapability("ping", False, None, "ping"),  # Critical utility missing
            NetworkCapability("netstat", True, "2.0", "netstat"),
            NetworkCapability("tracert", False, None, "tracert")
        ]
        mock_get_utilities.return_value = mock_utilities
        
        with patch('platform.system', return_value="Windows"):
            validator = CrossPlatformNetworkValidator()
            result = validator.validate_network_utilities()
        
        self.assertFalse(result.success)
        self.assertGreater(len(result.errors), 0)
        self.assertEqual(result.capabilities_passed, 1)
        self.assertLess(result.performance_score, 100.0)
    
    def test_validate_individual_tool_success(self):
        """Test successful individual tool validation."""
        tool = NetworkTool(
            name="TestTool",
            description="Test network tool",
            platform_support={"windows", "linux", "darwin"}
        )
        
        # Mock all capability tests to succeed
        with patch.object(self.validator, '_test_tool_import', return_value=True), \
             patch.object(self.validator, '_test_tool_initialization', return_value=True), \
             patch.object(self.validator, '_test_tool_basic_functionality', return_value=True), \
             patch.object(self.validator, '_test_tool_error_handling', return_value=True), \
             patch.object(self.validator, '_test_tool_cleanup', return_value=True):
            
            result = self.validator._validate_individual_tool(tool)
        
        self.assertTrue(result.success)
        self.assertEqual(result.tool_name, "TestTool")
        self.assertEqual(result.capabilities_tested, 5)
        self.assertEqual(result.capabilities_passed, 5)
        self.assertEqual(result.performance_score, 100.0)
    
    def test_validate_individual_tool_failure(self):
        """Test failed individual tool validation."""
        tool = NetworkTool(
            name="FailedTool",
            description="Failed test tool",
            platform_support={"windows", "linux", "darwin"}
        )
        
        # Mock some capability tests to fail
        with patch.object(self.validator, '_test_tool_import', return_value=False), \
             patch.object(self.validator, '_test_tool_initialization', return_value=False), \
             patch.object(self.validator, '_test_tool_basic_functionality', return_value=True), \
             patch.object(self.validator, '_test_tool_error_handling', return_value=True), \
             patch.object(self.validator, '_test_tool_cleanup', return_value=True):
            
            result = self.validator._validate_individual_tool(tool)
        
        self.assertFalse(result.success)
        self.assertGreater(len(result.errors), 0)
        self.assertEqual(result.capabilities_passed, 3)
        self.assertEqual(result.performance_score, 60.0)
    
    def test_validate_network_tools_unsupported_platform(self):
        """Test tool validation on unsupported platform."""
        # Mock platform as something not supported by tools
        with patch('platform.system', return_value="BeOS"):
            validator = CrossPlatformNetworkValidator()
            validator.platform = "beos"  # Force unsupported platform
            
            results = validator.validate_network_tools()
        
        # All tools should fail due to unsupported platform
        for result in results:
            self.assertFalse(result.success)
            self.assertIn("not supported", result.errors[0])
    
    def test_run_comprehensive_validation(self):
        """Test comprehensive validation execution."""
        # Mock all validation methods
        with patch.object(self.validator, 'validate_platform_requirements') as mock_platform, \
             patch.object(self.validator, 'validate_network_utilities') as mock_utilities, \
             patch.object(self.validator, 'validate_network_permissions') as mock_permissions, \
             patch.object(self.validator, 'benchmark_network_performance') as mock_performance, \
             patch.object(self.validator, 'validate_network_tools') as mock_tools:
            
            # Mock return values
            mock_platform.return_value = ValidationResult("Platform", "test", True, 1, 1, 100.0)
            mock_utilities.return_value = ValidationResult("Utilities", "test", True, 1, 1, 100.0)
            mock_permissions.return_value = ValidationResult("Permissions", "test", True, 1, 1, 100.0)
            mock_performance.return_value = ValidationResult("Performance", "test", True, 1, 1, 100.0)
            mock_tools.return_value = [ValidationResult("Tool1", "test", True, 1, 1, 100.0)]
            
            results = self.validator.run_comprehensive_validation()
        
        # Should have results from all validation categories
        self.assertEqual(len(results), 5)  # 4 main categories + 1 tool
        
        # Check that all validation methods were called
        mock_platform.assert_called_once()
        mock_utilities.assert_called_once()
        mock_permissions.assert_called_once()
        mock_performance.assert_called_once()
        mock_tools.assert_called_once()
    
    def test_generate_validation_report(self):
        """Test validation report generation."""
        results = [
            ValidationResult("PlatformTest", "linux", True, 3, 3, 100.0, execution_time=1.0),
            ValidationResult("ToolTest", "linux", False, 2, 1, 50.0, 
                           errors=["Test error"], warnings=["Test warning"], execution_time=0.5)
        ]
        
        report = self.validator.generate_validation_report(results)
        
        self.assertIn("CROSS-PLATFORM NETWORK TOOL VALIDATION REPORT", report)
        self.assertIn("Platform: linux", report)
        self.assertIn("Total Tests: 2", report)
        self.assertIn("Passed Tests: 1", report)
        self.assertIn("✓ PASS PlatformTest", report)
        self.assertIn("✗ FAIL ToolTest", report)
        self.assertIn("Test error", report)
        self.assertIn("Test warning", report)
    
    def test_export_validation_results_json(self):
        """Test exporting validation results to JSON."""
        results = [
            ValidationResult("Test1", "linux", True, 1, 1, 100.0),
            ValidationResult("Test2", "linux", False, 1, 0, 0.0, errors=["Error"])
        ]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            filename = self.validator.export_validation_results(results, "json")
            
            self.assertTrue(os.path.exists(filename))
            self.assertTrue(filename.endswith('.json'))
            
            # Verify JSON content
            with open(filename, 'r') as f:
                data = json.load(f)
            
            self.assertIn("validation_date", data)
            self.assertIn("platform", data)
            self.assertEqual(len(data["results"]), 2)
            self.assertEqual(data["summary"]["total_tests"], 2)
            self.assertEqual(data["summary"]["passed_tests"], 1)


class TestNetworkValidatorIntegration(unittest.TestCase):
    """Integration tests for network validator."""
    
    def setUp(self):
        """Set up integration test fixtures."""
        self.validator = CrossPlatformNetworkValidator(verbose=True)
    
    @unittest.skipUnless(
        sys.platform.startswith('win') or sys.platform.startswith('linux') or sys.platform.startswith('darwin'),
        "Integration tests require actual platform"
    )
    def test_real_platform_detection(self):
        """Test real platform detection."""
        self.assertIn(self.validator.platform, ['windows', 'linux', 'darwin'])
        self.assertIsNotNone(self.validator.validator)
    
    def test_logging_configuration(self):
        """Test logging setup."""
        # Verify logger was created
        self.assertIsNotNone(self.validator.logger)
        
        # Test verbose logging
        verbose_validator = CrossPlatformNetworkValidator(verbose=True)
        self.assertIsNotNone(verbose_validator.logger)


class TestCommandLineInterface(unittest.TestCase):
    """Test cases for command-line interface."""
    
    @patch('sys.argv', ['network_validator.py', '--help'])
    def test_help_argument(self):
        """Test help argument display."""
        with patch('builtins.print') as mock_print:
            try:
                from cross_platform.network_validator import main
                main()
            except SystemExit:
                pass  # argparse calls sys.exit after showing help
            
            # Check that help was displayed
            print_calls = [str(call) for call in mock_print.call_args_list]
            help_displayed = any('usage:' in call.lower() for call in print_calls)
            self.assertTrue(help_displayed)
    
    @patch('sys.argv', ['network_validator.py', '--verbose', '--component', 'requirements'])
    @patch.object(CrossPlatformNetworkValidator, 'validate_platform_requirements')
    def test_requirements_validation_command(self, mock_validate):
        """Test requirements validation via command line."""
        mock_validate.return_value = ValidationResult(
            "Requirements", "test", True, 3, 3, 100.0
        )
        
        try:
            from cross_platform.network_validator import main
            main()
        except SystemExit as e:
            self.assertEqual(e.code, 0)  # Should exit successfully
        
        mock_validate.assert_called_once()


if __name__ == '__main__':
    # Configure test discovery and execution
    unittest.main(
        verbosity=2,
        buffer=True,
        failfast=False,
        warnings='ignore'
    )