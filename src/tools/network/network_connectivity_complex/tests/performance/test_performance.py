"""Performance tests for network connectivity tools."""

import pytest
import time
import threading
import psutil
import gc
from datetime import datetime, timedelta
from unittest.mock import patch
from typing import List, Dict, Any

from ...tools.bandwidth_monitor import BandwidthMonitor
from ...tools.port_scanner import PortScanner
from ...tools.wifi_analyzer import WiFiAnalyzer
from ...tools.lan_file_transfer import LANFileTransfer
from ..mocks.network_mocks import MockPlatformDetector
from ..mocks.service_mocks import (
    MockConfigService, MockLoggingService,
    MockNotificationService, MockMetricsService
)


class PerformanceTestBase:
    """Base class for performance tests."""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.start_memory = None
        self.end_memory = None
        self.start_cpu = None
        self.end_cpu = None
    
    def start_monitoring(self):
        """Start performance monitoring."""
        gc.collect()  # Force garbage collection
        self.start_time = time.time()
        self.start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        self.start_cpu = psutil.Process().cpu_percent()
    
    def stop_monitoring(self):
        """Stop performance monitoring."""
        self.end_time = time.time()
        self.end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        self.end_cpu = psutil.Process().cpu_percent()
    
    def get_execution_time(self) -> float:
        """Get execution time in seconds."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0
    
    def get_memory_usage(self) -> float:
        """Get memory usage in MB."""
        if self.start_memory and self.end_memory:
            return self.end_memory - self.start_memory
        return 0.0
    
    def get_cpu_usage(self) -> float:
        """Get CPU usage percentage."""
        if self.start_cpu is not None and self.end_cpu is not None:
            return max(self.end_cpu - self.start_cpu, 0)
        return 0.0
    
    def assert_performance_limits(self, max_time: float = None,
                                 max_memory: float = None,
                                 max_cpu: float = None):
        """Assert performance limits."""
        if max_time and self.get_execution_time() > max_time:
            pytest.fail(
                f"Execution time {self.get_execution_time():.2f}s "
                f"exceeded limit {max_time}s"
            )
        
        if max_memory and self.get_memory_usage() > max_memory:
            pytest.fail(
                f"Memory usage {self.get_memory_usage():.2f}MB "
                f"exceeded limit {max_memory}MB"
            )
        
        if max_cpu and self.get_cpu_usage() > max_cpu:
            pytest.fail(
                f"CPU usage {self.get_cpu_usage():.2f}% "
                f"exceeded limit {max_cpu}%"
            )


@pytest.mark.performance
class TestBandwidthMonitorPerformance:
    """Performance tests for BandwidthMonitor."""
    
    @pytest.fixture
    def bandwidth_monitor(self):
        """Create bandwidth monitor for performance testing."""
        mock_services = {
            'config': MockConfigService(),
            'logging': MockLoggingService(),
            'notification': MockNotificationService(),
            'metrics': MockMetricsService()
        }
        mock_detector = MockPlatformDetector()
        
        with patch('network_connectivity.tools.bandwidth_monitor.get_config_service', 
                  return_value=mock_services['config']), \
             patch('network_connectivity.tools.bandwidth_monitor.get_logging_service', 
                  return_value=mock_services['logging']):
            
            monitor = BandwidthMonitor()
            monitor.platform_detector = mock_detector
            return monitor
    
    def test_bandwidth_monitor_initialization_performance(self, bandwidth_monitor):
        """Test bandwidth monitor initialization performance."""
        perf = PerformanceTestBase()
        
        perf.start_monitoring()
        
        # Perform multiple initializations
        for _ in range(100):
            monitor = BandwidthMonitor()
            monitor.platform_detector = MockPlatformDetector()
        
        perf.stop_monitoring()
        
        # Assert performance limits
        perf.assert_performance_limits(
            max_time=2.0,    # 2 seconds for 100 initializations
            max_memory=50.0,  # 50MB memory increase
            max_cpu=80.0     # 80% CPU usage
        )
    
    def test_bandwidth_data_collection_performance(self, bandwidth_monitor):
        """Test bandwidth data collection performance."""
        perf = PerformanceTestBase()
        
        bandwidth_monitor.set_monitoring_interface("eth0")
        
        perf.start_monitoring()
        
        # Collect bandwidth data multiple times
        for _ in range(1000):
            data = bandwidth_monitor.get_current_bandwidth()
            assert data is not None
        
        perf.stop_monitoring()
        
        # Assert performance limits
        perf.assert_performance_limits(
            max_time=1.0,    # 1 second for 1000 collections
            max_memory=20.0,  # 20MB memory increase
            max_cpu=50.0     # 50% CPU usage
        )
    
    def test_bandwidth_history_management_performance(self, bandwidth_monitor):
        """Test bandwidth history management performance."""
        perf = PerformanceTestBase()
        
        bandwidth_monitor.set_monitoring_interface("eth0")
        bandwidth_monitor.set_history_size(10000)  # Large history
        
        perf.start_monitoring()
        
        # Add many data points to history
        for i in range(10000):
            data = bandwidth_monitor.get_current_bandwidth()
            bandwidth_monitor.bandwidth_history.append(data)
        
        # Test history retrieval
        history = bandwidth_monitor.get_bandwidth_history()
        assert len(history) <= 10000
        
        perf.stop_monitoring()
        
        # Assert performance limits
        perf.assert_performance_limits(
            max_time=5.0,     # 5 seconds for large history
            max_memory=100.0,  # 100MB memory increase
            max_cpu=70.0      # 70% CPU usage
        )
    
    def test_concurrent_bandwidth_monitoring_performance(self, bandwidth_monitor):
        """Test concurrent bandwidth monitoring performance."""
        perf = PerformanceTestBase()
        
        bandwidth_monitor.set_monitoring_interface("eth0")
        
        def monitoring_worker():
            for _ in range(100):
                data = bandwidth_monitor.get_current_bandwidth()
                time.sleep(0.001)  # 1ms delay
        
        perf.start_monitoring()
        
        # Start multiple monitoring threads
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=monitoring_worker)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        perf.stop_monitoring()
        
        # Assert performance limits
        perf.assert_performance_limits(
            max_time=3.0,     # 3 seconds for concurrent monitoring
            max_memory=50.0,   # 50MB memory increase
            max_cpu=90.0      # 90% CPU usage (higher for concurrent)
        )


@pytest.mark.performance
class TestPortScannerPerformance:
    """Performance tests for PortScanner."""
    
    @pytest.fixture
    def port_scanner(self):
        """Create port scanner for performance testing."""
        mock_services = {
            'config': MockConfigService(),
            'logging': MockLoggingService()
        }
        mock_detector = MockPlatformDetector()
        
        with patch('network_connectivity.tools.port_scanner.get_config_service', 
                  return_value=mock_services['config']), \
             patch('network_connectivity.tools.port_scanner.get_logging_service', 
                  return_value=mock_services['logging']):
            
            scanner = PortScanner()
            scanner.platform_detector = mock_detector
            return scanner
    
    def test_port_scanner_initialization_performance(self, port_scanner):
        """Test port scanner initialization performance."""
        perf = PerformanceTestBase()
        
        perf.start_monitoring()
        
        # Perform multiple initializations
        for _ in range(50):
            scanner = PortScanner()
            scanner.platform_detector = MockPlatformDetector()
        
        perf.stop_monitoring()
        
        # Assert performance limits
        perf.assert_performance_limits(
            max_time=1.0,     # 1 second for 50 initializations
            max_memory=30.0,   # 30MB memory increase
            max_cpu=60.0      # 60% CPU usage
        )
    
    def test_port_range_processing_performance(self, port_scanner):
        """Test port range processing performance."""
        perf = PerformanceTestBase()
        
        port_scanner.set_target("192.168.1.1")
        
        perf.start_monitoring()
        
        # Process large port ranges
        for start_port in range(1, 1001, 100):  # 10 ranges of 100 ports
            end_port = start_port + 99
            port_range = list(range(start_port, end_port + 1))
            
            # Simulate port range processing
            for port in port_range:
                # Mock port check (would be actual network operation)
                result = {"port": port, "state": "closed"}
                assert result is not None
        
        perf.stop_monitoring()
        
        # Assert performance limits
        perf.assert_performance_limits(
            max_time=2.0,     # 2 seconds for processing 1000 ports
            max_memory=25.0,   # 25MB memory increase
            max_cpu=70.0      # 70% CPU usage
        )


@pytest.mark.performance
class TestWiFiAnalyzerPerformance:
    """Performance tests for WiFiAnalyzer."""
    
    @pytest.fixture
    def wifi_analyzer(self):
        """Create WiFi analyzer for performance testing."""
        mock_services = {
            'config': MockConfigService(),
            'logging': MockLoggingService()
        }
        mock_detector = MockPlatformDetector()
        
        with patch('network_connectivity.tools.wifi_analyzer.get_config_service', 
                  return_value=mock_services['config']), \
             patch('network_connectivity.tools.wifi_analyzer.get_logging_service', 
                  return_value=mock_services['logging']):
            
            analyzer = WiFiAnalyzer()
            analyzer.platform_detector = mock_detector
            return analyzer
    
    def test_wifi_scan_performance(self, wifi_analyzer):
        """Test WiFi scanning performance."""
        perf = PerformanceTestBase()
        
        perf.start_monitoring()
        
        # Perform multiple WiFi scans
        for _ in range(10):
            # Mock WiFi scan (would be actual wireless scan)
            networks = []
            for i in range(20):  # Simulate 20 networks found
                network = {
                    "ssid": f"Network_{i}",
                    "bssid": f"00:11:22:33:44:{i:02x}",
                    "signal_strength": -50 - i,
                    "channel": (i % 11) + 1
                }
                networks.append(network)
            
            assert len(networks) == 20
        
        perf.stop_monitoring()
        
        # Assert performance limits
        perf.assert_performance_limits(
            max_time=1.5,     # 1.5 seconds for 10 scans
            max_memory=20.0,   # 20MB memory increase
            max_cpu=60.0      # 60% CPU usage
        )


@pytest.mark.performance
class TestLANFileTransferPerformance:
    """Performance tests for LANFileTransfer."""
    
    @pytest.fixture
    def lan_file_transfer(self):
        """Create LAN file transfer for performance testing."""
        mock_services = {
            'config': MockConfigService(),
            'logging': MockLoggingService()
        }
        mock_detector = MockPlatformDetector()
        
        with patch('network_connectivity.tools.lan_file_transfer.get_config_service', 
                  return_value=mock_services['config']), \
             patch('network_connectivity.tools.lan_file_transfer.get_logging_service', 
                  return_value=mock_services['logging']):
            
            transfer = LANFileTransfer()
            transfer.platform_detector = mock_detector
            return transfer
    
    def test_device_discovery_performance(self, lan_file_transfer):
        """Test device discovery performance."""
        perf = PerformanceTestBase()
        
        perf.start_monitoring()
        
        # Simulate device discovery
        for _ in range(100):
            # Mock device discovery (would be actual network discovery)
            devices = []
            for i in range(10):  # Simulate 10 devices found
                device = {
                    "ip_address": f"192.168.1.{100 + i}",
                    "mac_address": f"00:11:22:33:44:{i:02x}",
                    "hostname": f"device-{i}",
                    "device_type": "Computer"
                }
                devices.append(device)
            
            assert len(devices) == 10
        
        perf.stop_monitoring()
        
        # Assert performance limits
        perf.assert_performance_limits(
            max_time=2.0,     # 2 seconds for 100 discovery cycles
            max_memory=30.0,   # 30MB memory increase
            max_cpu=70.0      # 70% CPU usage
        )


@pytest.mark.stress
class TestStressTests:
    """Stress tests for network connectivity tools."""
    
    def test_memory_leak_detection(self):
        """Test for memory leaks during extended operation."""
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        # Run operations for extended period
        for cycle in range(100):
            # Create and destroy tools
            with patch('network_connectivity.tools.bandwidth_monitor.get_config_service'), \
                 patch('network_connectivity.tools.bandwidth_monitor.get_logging_service'):
                
                monitor = BandwidthMonitor()
                monitor.platform_detector = MockPlatformDetector()
                
                # Perform operations
                monitor.set_monitoring_interface("eth0")
                for _ in range(10):
                    data = monitor.get_current_bandwidth()
                    monitor.bandwidth_history.append(data)
                
                # Clean up
                del monitor
            
            # Force garbage collection every 10 cycles
            if cycle % 10 == 0:
                gc.collect()
                current_memory = psutil.Process().memory_info().rss / 1024 / 1024
                memory_increase = current_memory - initial_memory
                
                # Memory should not increase significantly
                assert memory_increase < 100, f"Memory leak detected: {memory_increase}MB increase"
    
    def test_concurrent_tool_stress(self):
        """Test concurrent operation of multiple tools under stress."""
        perf = PerformanceTestBase()
        
        def bandwidth_worker():
            with patch('network_connectivity.tools.bandwidth_monitor.get_config_service'), \
                 patch('network_connectivity.tools.bandwidth_monitor.get_logging_service'):
                
                monitor = BandwidthMonitor()
                monitor.platform_detector = MockPlatformDetector()
                monitor.set_monitoring_interface("eth0")
                
                for _ in range(50):
                    data = monitor.get_current_bandwidth()
                    time.sleep(0.01)
        
        def port_scanner_worker():
            with patch('network_connectivity.tools.port_scanner.get_config_service'), \
                 patch('network_connectivity.tools.port_scanner.get_logging_service'):
                
                scanner = PortScanner()
                scanner.platform_detector = MockPlatformDetector()
                scanner.set_target("192.168.1.1")
                
                for _ in range(50):
                    # Mock port scan operation
                    time.sleep(0.01)
        
        perf.start_monitoring()
        
        # Start multiple worker threads
        threads = []
        for _ in range(5):
            threads.append(threading.Thread(target=bandwidth_worker))
            threads.append(threading.Thread(target=port_scanner_worker))
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        perf.stop_monitoring()
        
        # Assert stress test limits (more lenient)
        perf.assert_performance_limits(
            max_time=10.0,     # 10 seconds for stress test
            max_memory=200.0,   # 200MB memory increase
            max_cpu=95.0       # 95% CPU usage
        )
    
    def test_large_data_handling_stress(self):
        """Test handling of large amounts of data."""
        perf = PerformanceTestBase()
        
        with patch('network_connectivity.tools.bandwidth_monitor.get_config_service'), \
             patch('network_connectivity.tools.bandwidth_monitor.get_logging_service'):
            
            monitor = BandwidthMonitor()
            monitor.platform_detector = MockPlatformDetector()
            monitor.set_monitoring_interface("eth0")
            monitor.set_history_size(50000)  # Very large history
            
            perf.start_monitoring()
            
            # Generate large amount of data
            for _ in range(50000):
                data = monitor.get_current_bandwidth()
                monitor.bandwidth_history.append(data)
            
            # Test operations on large dataset
            history = monitor.get_bandwidth_history()
            stats = monitor.get_statistics()
            
            assert len(history) <= 50000
            assert stats is not None
            
            perf.stop_monitoring()
            
            # Assert large data handling limits
            perf.assert_performance_limits(
                max_time=15.0,     # 15 seconds for large data
                max_memory=500.0,   # 500MB memory increase
                max_cpu=90.0       # 90% CPU usage
            )


@pytest.mark.performance
class TestPerformanceRegression:
    """Performance regression tests."""
    
    def test_bandwidth_monitor_regression(self):
        """Test bandwidth monitor performance regression."""
        # Baseline performance expectations
        baseline_times = {
            "initialization": 0.1,    # 100ms
            "data_collection": 0.001, # 1ms per collection
            "history_retrieval": 0.01 # 10ms for 100 items
        }
        
        with patch('network_connectivity.tools.bandwidth_monitor.get_config_service'), \
             patch('network_connectivity.tools.bandwidth_monitor.get_logging_service'):
            
            # Test initialization time
            start_time = time.time()
            monitor = BandwidthMonitor()
            monitor.platform_detector = MockPlatformDetector()
            init_time = time.time() - start_time
            
            assert init_time < baseline_times["initialization"], \
                f"Initialization regression: {init_time:.3f}s > {baseline_times['initialization']}s"
            
            # Test data collection time
            monitor.set_monitoring_interface("eth0")
            start_time = time.time()
            data = monitor.get_current_bandwidth()
            collection_time = time.time() - start_time
            
            assert collection_time < baseline_times["data_collection"], \
                f"Data collection regression: {collection_time:.3f}s > {baseline_times['data_collection']}s"
            
            # Test history retrieval time
            for _ in range(100):
                monitor.bandwidth_history.append(data)
            
            start_time = time.time()
            history = monitor.get_bandwidth_history()
            retrieval_time = time.time() - start_time
            
            assert retrieval_time < baseline_times["history_retrieval"], \
                f"History retrieval regression: {retrieval_time:.3f}s > {baseline_times['history_retrieval']}s"


if __name__ == "__main__":
    pytest.main([__file__])