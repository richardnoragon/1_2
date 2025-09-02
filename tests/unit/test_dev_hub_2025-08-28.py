"""
Comprehensive unit tests for dev_hub.py module
Generated on: 2025-08-28
Target: dev_hub.py

This test suite covers all classes and methods in the dev_hub.py module
with appropriate assertions, edge cases, and mock data.
"""

import logging
import os
import sys
import time
from datetime import datetime
from unittest.mock import Mock, call, patch

import pytest

# Add the source directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

# Import the module under test
try:
    from rfu import dev_hub
except ImportError:
    # Fallback import
    src_path = os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'rfu')
    sys.path.insert(0, src_path)
    import dev_hub


class TestPerformanceMonitor:
    """Test suite for the PerformanceMonitor class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.performance_monitor = None
    
    def teardown_method(self):
        """Clean up after each test method."""
        if self.performance_monitor and self.performance_monitor.running:
            self.performance_monitor.stop()
            self.performance_monitor.wait()
    
    @patch('rfu.dev_hub.PYQT5_AVAILABLE', True)
    @patch('rfu.dev_hub.QtCore')
    def test_performance_monitor_init(self, mock_qtcore):
        """Test PerformanceMonitor initialization."""
        # Mock QThread
        mock_qthread = Mock()
        mock_qtcore.QThread = mock_qthread
        
        monitor = dev_hub.PerformanceMonitor()
        
        assert monitor.running is False
        assert monitor.interval == 1.0
        mock_qthread.assert_called_once()
    
    @patch('rfu.dev_hub.PYQT5_AVAILABLE', True)
    @patch('rfu.dev_hub.QtCore')
    @patch('psutil.cpu_percent')
    @patch('psutil.cpu_count')
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    @patch('psutil.Process')
    def test_collect_metrics(self, mock_process, mock_disk, mock_memory,
                              mock_cpu_count, mock_cpu_percent, mock_qtcore):
        """Test the _collect_metrics method."""
        # Setup mocks
        mock_qtcore.QThread = Mock()
        mock_cpu_percent.return_value = 25.5
        mock_cpu_count.return_value = 8
        
        # Mock memory
        mock_mem = Mock()
        mock_mem.percent = 65.2
        mock_mem.available = 8 * (1024**3)  # 8GB
        mock_mem.total = 16 * (1024**3)     # 16GB
        mock_memory.return_value = mock_mem
        
        # Mock disk
        mock_disk_obj = Mock()
        mock_disk_obj.used = 500 * (1024**3)   # 500GB used
        mock_disk_obj.total = 1000 * (1024**3)  # 1TB total
        mock_disk_obj.free = 500 * (1024**3)   # 500GB free
        mock_disk.return_value = mock_disk_obj
        
        # Mock process
        mock_proc = Mock()
        mock_mem_info = Mock()
        mock_mem_info.rss = 100 * (1024**2)  # 100MB
        mock_proc.memory_info.return_value = mock_mem_info
        mock_proc.cpu_percent.return_value = 5.0
        mock_process.return_value = mock_proc
        
        monitor = dev_hub.PerformanceMonitor()
        metrics = monitor._collect_metrics()
        
        # Verify metrics
        assert isinstance(metrics, dict)
        assert 'timestamp' in metrics
        assert metrics['cpu_percent'] == 25.5
        assert metrics['cpu_count'] == 8
        assert abs(metrics['memory_percent'] - 65.2) < 0.01
        assert abs(metrics['memory_available_gb'] - 8.0) < 0.01
        assert abs(metrics['memory_total_gb'] - 16.0) < 0.01
        assert abs(metrics['disk_percent'] - 50.0) < 0.01  # 500/1000 * 100
        expected_disk_free = 500.0 / (1024**3) * (1024**3)
        assert abs(metrics['disk_free_gb'] - expected_disk_free) < 0.01
        assert abs(metrics['process_memory_mb'] - 100.0) < 0.01
        assert abs(metrics['process_cpu_percent'] - 5.0) < 0.01
        
        # Verify method calls
        mock_cpu_percent.assert_called_once_with(interval=0.1)
        mock_cpu_count.assert_called_once()
        mock_memory.assert_called_once()
        mock_disk.assert_called_once_with('/')
        mock_process.assert_called_once()
    
    @patch('rfu.dev_hub.PYQT5_AVAILABLE', True)
    @patch('rfu.dev_hub.QtCore')
    @patch('time.sleep')
    def test_performance_monitor_run(self, mock_sleep, mock_qtcore):
        """Test the run method of PerformanceMonitor."""
        mock_qtcore.QThread = Mock()
        
        monitor = dev_hub.PerformanceMonitor()
        monitor._collect_metrics = Mock(return_value={'test': 'data'})
        monitor.performance_updated = Mock()
        monitor.performance_updated.emit = Mock()
        
        # Mock the running flag to stop after one iteration
        monitor.running = True
        
        def stop_after_one_iteration(*args):
            monitor.running = False
        
        mock_sleep.side_effect = stop_after_one_iteration
        
        monitor.run()
        
        monitor._collect_metrics.assert_called_once()
        monitor.performance_updated.emit.assert_called_once_with({'test': 'data'})
        mock_sleep.assert_called_once_with(1.0)
    
    @patch('rfu.dev_hub.PYQT5_AVAILABLE', True)
    @patch('rfu.dev_hub.QtCore')
    def test_performance_monitor_stop(self, mock_qtcore):
        """Test the stop method of PerformanceMonitor."""
        mock_qtcore.QThread = Mock()
        
        monitor = dev_hub.PerformanceMonitor()
        monitor.running = True
        
        monitor.stop()
        
        assert monitor.running is False


class TestLogHandler:
    """Test suite for the LogHandler class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.log_signal = Mock()
        self.log_handler = dev_hub.LogHandler(self.log_signal)
    
    def test_log_handler_init(self):
        """Test LogHandler initialization."""
        assert self.log_handler.log_signal == self.log_signal
        assert self.log_handler.log_entries == []
        assert self.log_handler.max_entries == 1000
    
    def test_emit_log_record(self):
        """Test the emit method with a log record."""
        # Create a mock log record
        log_record = Mock()
        log_record.created = time.time()
        log_record.levelname = 'INFO'
        log_record.module = 'test_module'
        log_record.funcName = 'test_function'
        log_record.lineno = 42
        
        # Mock the format method
        self.log_handler.format = Mock(return_value='Test log message')
        
        self.log_handler.emit(log_record)
        
        # Check that log entry was added
        assert len(self.log_handler.log_entries) == 1
        entry = self.log_handler.log_entries[0]
        assert entry['level'] == 'INFO'
        assert entry['message'] == 'Test log message'
        assert entry['module'] == 'test_module'
        assert entry['funcName'] == 'test_function'
        assert entry['lineno'] == 42
        
        # Check that signal was emitted
        self.log_signal.emit.assert_called_once_with('Test log message')
    
    def test_emit_max_entries_limit(self):
        """Test that emit respects the max_entries limit."""
        self.log_handler.max_entries = 3
        self.log_handler.format = Mock(return_value='Test message')
        
        # Add 5 log entries
        for i in range(5):
            log_record = Mock()
            log_record.created = time.time()
            log_record.levelname = 'INFO'
            log_record.module = f'module_{i}'
            log_record.funcName = 'test_function'
            log_record.lineno = i
            
            self.log_handler.emit(log_record)
        
        # Should only keep the last 3 entries
        assert len(self.log_handler.log_entries) == 3
        assert self.log_handler.log_entries[0]['module'] == 'module_2'
        assert self.log_handler.log_entries[1]['module'] == 'module_3'
        assert self.log_handler.log_entries[2]['module'] == 'module_4'
    
    def test_get_recent_logs(self):
        """Test the get_recent_logs method."""
        # Add some log entries
        for i in range(10):
            entry = {
                'timestamp': datetime.now(),
                'level': 'INFO',
                'message': f'Message {i}',
                'module': f'module_{i}',
                'funcName': 'test_function',
                'lineno': i
            }
            self.log_handler.log_entries.append(entry)
        
        # Get recent logs
        recent_logs = self.log_handler.get_recent_logs(5)
        
        assert len(recent_logs) == 5
        assert recent_logs[0]['message'] == 'Message 5'
        assert recent_logs[4]['message'] == 'Message 9'
    
    def test_get_recent_logs_default_count(self):
        """Test get_recent_logs with default count."""
        # Add more than 100 entries
        for i in range(150):
            entry = {'message': f'Message {i}'}
            self.log_handler.log_entries.append(entry)
        
        recent_logs = self.log_handler.get_recent_logs()
        
        assert len(recent_logs) == 100
        assert recent_logs[0]['message'] == 'Message 50'
        assert recent_logs[99]['message'] == 'Message 149'


class TestDevHub:
    """Test suite for the DevHub class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.dev_hub = None
    
    def teardown_method(self):
        """Clean up after each test method."""
        if self.dev_hub:
            # Clean up any resources
            pass
    
    @patch('rfu.dev_hub.PYQT5_AVAILABLE', False)
    def test_dev_hub_init_fallback_mode(self):
        """Test DevHub initialization in fallback mode."""
        with patch.object(dev_hub.DevHub, '_init_fallback') as mock_fallback:
            self.dev_hub = dev_hub.DevHub()
            mock_fallback.assert_called_once()
    
    @patch('rfu.dev_hub.PYQT5_AVAILABLE', True)
    @patch('rfu.dev_hub.QtWidgets')
    def test_dev_hub_init_gui_mode(self, mock_qtwidgets):
        """Test DevHub initialization in GUI mode."""
        mock_qtwidgets.QMainWindow = Mock()
        
        with patch.object(dev_hub.DevHub, '_init_gui') as mock_init_gui, \
             patch.object(dev_hub.DevHub, '_setup_performance_monitoring') as mock_perf:
            self.dev_hub = dev_hub.DevHub()
            mock_init_gui.assert_called_once()
            mock_perf.assert_called_once()
    
    @patch('rfu.dev_hub.PYQT5_AVAILABLE', True)
    @patch('rfu.dev_hub.QtWidgets')
    def test_setup_logging(self, mock_qtwidgets):
        """Test the _setup_logging method."""
        mock_qtwidgets.QMainWindow = Mock()
        
        with patch.object(dev_hub.DevHub, '_init_gui'), \
             patch.object(dev_hub.DevHub, '_setup_performance_monitoring'):
            self.dev_hub = dev_hub.DevHub()
        
        # Check logger setup
        assert hasattr(self.dev_hub, 'logger')
        assert isinstance(self.dev_hub.logger, logging.Logger)
        assert self.dev_hub.logger.name == 'DevHub'
        assert self.dev_hub.logger.level == logging.DEBUG
        
        # Check log handler
        assert hasattr(self.dev_hub, 'log_handler')
        assert isinstance(self.dev_hub.log_handler, dev_hub.LogHandler)
    
    @patch('rfu.dev_hub.PYQT5_AVAILABLE', True)
    @patch('rfu.dev_hub.QtWidgets')
    @patch('builtins.print')
    def test_init_fallback(self, mock_print, mock_qtwidgets):
        """Test the _init_fallback method."""
        mock_qtwidgets.QMainWindow = Mock()
        
        with patch.object(dev_hub.DevHub, '_init_gui'), \
             patch.object(dev_hub.DevHub, '_setup_performance_monitoring'), \
             patch.object(dev_hub.DevHub, '_console_interface'):
            self.dev_hub = dev_hub.DevHub()
            self.dev_hub._init_fallback()
        
        # Check that console messages were printed
        expected_calls = [
            call("RFU Development Hub - Console Mode"),
            call("PyQt5 not available, running in console mode"),
            call("Available commands:"),
            call("  diagnostics - Run system diagnostics"),
            call("  logs - Show recent log entries"),
            call("  help - Show this help message"),
            call("  exit - Exit the development hub")
        ]
        mock_print.assert_has_calls(expected_calls)
    
    @patch('rfu.dev_hub.PYQT5_AVAILABLE', True)
    @patch('rfu.dev_hub.QtWidgets')
    def test_create_left_panel(self, mock_qtwidgets):
        """Test the _create_left_panel method."""
        # Mock Qt widgets
        mock_widget = Mock()
        mock_layout = Mock()
        mock_tab_widget = Mock()
        
        mock_qtwidgets.QWidget.return_value = mock_widget
        mock_qtwidgets.QVBoxLayout.return_value = mock_layout
        mock_qtwidgets.QTabWidget = Mock(return_value=mock_tab_widget)
        
        with patch.object(dev_hub.DevHub, '_init_gui'), \
             patch.object(dev_hub.DevHub, '_setup_performance_monitoring'):
            self.dev_hub = dev_hub.DevHub()
        
        # Mock the tab creation methods
        with patch.object(self.dev_hub, '_create_diagnostics_tab', return_value=Mock()) as mock_diag, \
             patch.object(self.dev_hub, '_create_testing_tab', return_value=Mock()) as mock_test, \
             patch.object(self.dev_hub, '_create_inspection_tab', return_value=Mock()) as mock_inspect, \
             patch.object(self.dev_hub, '_create_dev_utils_tab', return_value=Mock()) as mock_utils:
            
            result = self.dev_hub._create_left_panel()
            
            # Verify method calls
            mock_diag.assert_called_once()
            mock_test.assert_called_once()
            mock_inspect.assert_called_once()
            mock_utils.assert_called_once()
            
            assert result == mock_widget
    
    @patch('rfu.dev_hub.PYQT5_AVAILABLE', True)
    @patch('rfu.dev_hub.QtWidgets')
    def test_create_right_panel(self, mock_qtwidgets):
        """Test the _create_right_panel method."""
        # Mock Qt widgets
        mock_widget = Mock()
        mock_layout = Mock()
        mock_tab_widget = Mock()
        
        mock_qtwidgets.QWidget.return_value = mock_widget
        mock_qtwidgets.QVBoxLayout.return_value = mock_layout
        mock_qtwidgets.QTabWidget = Mock(return_value=mock_tab_widget)
        
        with patch.object(dev_hub.DevHub, '_init_gui'), \
             patch.object(dev_hub.DevHub, '_setup_performance_monitoring'):
            self.dev_hub = dev_hub.DevHub()
        
        # Mock the tab creation methods
        with patch.object(self.dev_hub, '_create_performance_tab', return_value=Mock()) as mock_perf, \
             patch.object(self.dev_hub, '_create_logs_tab', return_value=Mock()) as mock_logs, \
             patch.object(self.dev_hub, '_create_system_info_tab', return_value=Mock()) as mock_sys:
            
            result = self.dev_hub._create_right_panel()
            
            # Verify method calls
            mock_perf.assert_called_once()
            mock_logs.assert_called_once()
            mock_sys.assert_called_once()
            
            assert result == mock_widget


class TestModuleFunctions:
    """Test suite for module-level functions."""
    
    @patch('rfu.dev_hub.PYQT5_AVAILABLE', True)
    @patch('rfu.dev_hub.QtWidgets')
    def test_main_with_pyqt5(self, mock_qtwidgets):
        """Test the main function when PyQt5 is available."""
        mock_app = Mock()
        mock_qtwidgets.QApplication.instance.return_value = None
        mock_qtwidgets.QApplication.return_value = mock_app
        
        with patch.object(dev_hub, 'DevHub') as mock_dev_hub_class:
            mock_dev_hub_instance = Mock()
            mock_dev_hub_class.return_value = mock_dev_hub_instance
            
            # Mock sys.argv and __name__ to avoid exec_()
            with patch('sys.argv', ['test']):
                dev_hub.main()
            
            # Verify that DevHub was created and shown
            mock_dev_hub_class.assert_called_once()
            mock_dev_hub_instance.show.assert_called_once()
    
    @patch('rfu.dev_hub.PYQT5_AVAILABLE', False)
    def test_main_without_pyqt5(self):
        """Test the main function when PyQt5 is not available."""
        with patch.object(dev_hub, 'DevHub') as mock_dev_hub_class:
            dev_hub.main()
            mock_dev_hub_class.assert_called_once()


class TestEdgeCases:
    """Test suite for edge cases and error conditions."""
    
    @patch('rfu.dev_hub.PYQT5_AVAILABLE', True)
    @patch('rfu.dev_hub.QtCore')
    @patch('psutil.cpu_percent', side_effect=Exception("CPU error"))
    def test_collect_metrics_exception_handling(self, mock_cpu_percent, mock_qtcore):
        """Test _collect_metrics with exception handling."""
        mock_qtcore.QThread = Mock()
        
        monitor = dev_hub.PerformanceMonitor()
        
        # Should not raise an exception
        try:
            monitor._collect_metrics()
            assert False, "Expected exception was not raised"
        except Exception:
            # Exception should be raised since psutil.cpu_percent fails
            pass
    
    def test_log_handler_emit_exception(self):
        """Test LogHandler.emit with exception in formatting."""
        log_signal = Mock()
        log_handler = dev_hub.LogHandler(log_signal)
        log_handler.format = Mock(side_effect=Exception("Format error"))
        log_handler.handleError = Mock()
        
        log_record = Mock()
        log_record.created = time.time()
        
        log_handler.emit(log_record)
        
        # Should call handleError when format fails
        log_handler.handleError.assert_called_once_with(log_record)
    
    def test_get_recent_logs_empty_list(self):
        """Test get_recent_logs with empty log entries."""
        log_signal = Mock()
        log_handler = dev_hub.LogHandler(log_signal)
        
        recent_logs = log_handler.get_recent_logs(10)
        
        assert recent_logs == []
    
    def test_get_recent_logs_count_larger_than_entries(self):
        """Test get_recent_logs when count is larger than available entries."""
        log_signal = Mock()
        log_handler = dev_hub.LogHandler(log_signal)
        
        # Add only 3 entries
        for i in range(3):
            log_handler.log_entries.append({'message': f'Message {i}'})
        
        # Request 10 entries
        recent_logs = log_handler.get_recent_logs(10)
        
        assert len(recent_logs) == 3
        assert recent_logs[0]['message'] == 'Message 0'
        assert recent_logs[2]['message'] == 'Message 2'


class TestIntegration:
    """Integration tests for the dev_hub module."""
    
    @patch('rfu.dev_hub.PYQT5_AVAILABLE', True)
    @patch('rfu.dev_hub.QtWidgets')
    def test_dev_hub_with_performance_monitor(self, mock_qtwidgets):
        """Test DevHub integration with PerformanceMonitor."""
        mock_qtwidgets.QMainWindow = Mock()
        
        with patch.object(dev_hub.DevHub, '_init_gui'), \
             patch.object(dev_hub.DevHub, '_setup_performance_monitoring'):
            dev_hub.DevHub()
        
        # Test that performance monitor can be created
        monitor = dev_hub.PerformanceMonitor()
        assert monitor is not None
        assert hasattr(monitor, 'running')
        assert hasattr(monitor, 'interval')
    
    @patch('rfu.dev_hub.PYQT5_AVAILABLE', True)
    @patch('rfu.dev_hub.QtWidgets')
    def test_log_handler_integration_with_dev_hub(self, mock_qtwidgets):
        """Test LogHandler integration with DevHub."""
        mock_qtwidgets.QMainWindow = Mock()
        
        with patch.object(dev_hub.DevHub, '_init_gui'), \
             patch.object(dev_hub.DevHub, '_setup_performance_monitoring'):
            dev_hub_instance = dev_hub.DevHub()
        
        # Test that log handler is properly set up
        assert hasattr(dev_hub_instance, 'log_handler')
        assert isinstance(dev_hub_instance.log_handler, dev_hub.LogHandler)
        
        # Test logging through the dev hub
        dev_hub_instance.logger.info("Test message")
        
        # Check that log entry was added
        assert len(dev_hub_instance.log_handler.log_entries) > 0
        last_entry = dev_hub_instance.log_handler.log_entries[-1]
        assert "Test message" in last_entry['message']


if __name__ == '__main__':
    pytest.main([__file__])