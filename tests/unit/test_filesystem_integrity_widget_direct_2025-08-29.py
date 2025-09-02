"""
Direct unit tests for filesystem_integrity_widget.py
This version bypasses import issues by directly testing the module.

Test file: test_filesystem_integrity_widget_direct_2025-08-29.py
Target module: filesystem_integrity_widget.py
Created: 2025-08-29
Framework: pytest
"""

import importlib.util
import os
import sys
from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

import pytest


class TestFilesystemIntegrityWidgetDirect:
    """Direct tests for the filesystem integrity widget."""
    
    @pytest.fixture(scope="class")
    def widget_module(self):
        """Load the widget module directly."""
        # Mock all dependencies before importing
        mock_modules = {
            'PyQt5': Mock(),
            'PyQt5.QtWidgets': Mock(),
            'PyQt5.QtCore': Mock(),
            'PyQt5.QtGui': Mock(),
            'utilities.system.diagnostics_monitoring.monitors.filesystem.integrity_monitor': Mock(),
            'utilities.system.diagnostics_monitoring.core.platform_detector': Mock(),
            'core.error_handler': Mock()
        }
        
        # Create mock classes for PyQt components
        mock_qwidget = Mock()
        mock_qthread = Mock()
        mock_pyqt_signal = Mock()
        
        # Setup mock module attributes
        mock_modules['PyQt5.QtWidgets'].QWidget = mock_qwidget
        mock_modules['PyQt5.QtCore'].QThread = mock_qthread
        mock_modules['PyQt5.QtCore'].pyqtSignal = mock_pyqt_signal
        
        with patch.dict('sys.modules', mock_modules):
            # Load the module directly
            module_path = os.path.join(
                os.path.dirname(__file__), '..', '..', 'src',
                'utilities', 'system', 'diagnostics_monitoring', 'gui',
                'filesystem_integrity_widget.py'
            )
            
            spec = importlib.util.spec_from_file_location(
                "filesystem_integrity_widget", module_path
            )
            module = importlib.util.module_from_spec(spec)
            
            # Mock the dependencies in the module's namespace
            module.IntegrityMonitor = Mock()
            module.get_platform_detector = Mock(return_value=Mock())
            module.error_handler = Mock()
            module.ScanType = Mock()
            module.PYQT_AVAILABLE = True
            
            # Execute the module
            spec.loader.exec_module(module)
            
            return module
    
    def test_module_loaded_successfully(self, widget_module):
        """Test that the module loads successfully."""
        assert widget_module is not None
        assert hasattr(widget_module, 'FilesystemIntegrityWidget')
        assert hasattr(widget_module, 'ScanWorker')
    
    def test_scan_worker_initialization(self, widget_module):
        """Test ScanWorker initialization."""
        mock_monitor = Mock()
        scan_config = {
            'scan_type': 'QUICK',
            'paths': ['/test/path'],
            'config_override': {'max_depth': 10}
        }
        
        worker = widget_module.ScanWorker(mock_monitor, scan_config)
        
        assert worker.integrity_monitor == mock_monitor
        assert worker.scan_config == scan_config
        assert hasattr(worker, 'logger')
    
    def test_scan_worker_run_success(self, widget_module):
        """Test successful scan worker run."""
        mock_monitor = Mock()
        mock_monitor.start_scan.return_value = True
        mock_monitor.is_scanning.return_value = False
        mock_monitor.get_scan_status.return_value = {
            'success': True,
            'statistics': {'files_scanned': 100}
        }
        
        scan_config = {'scan_type': 'QUICK'}
        worker = widget_module.ScanWorker(mock_monitor, scan_config)
        
        # Mock the signals
        worker.progress_updated = Mock()
        worker.scan_completed = Mock()
        worker.scan_error = Mock()
        worker.msleep = Mock()  # Mock sleep method
        
        worker.run()
        
        # Verify scan was started
        mock_monitor.start_scan.assert_called_once()
        
        # Verify completion signal was emitted
        worker.scan_completed.emit.assert_called_once()
        
        # Verify no error signal
        worker.scan_error.emit.assert_not_called()
    
    def test_scan_worker_run_failure(self, widget_module):
        """Test scan worker run with failure."""
        mock_monitor = Mock()
        mock_monitor.start_scan.return_value = False
        
        scan_config = {'scan_type': 'QUICK'}
        worker = widget_module.ScanWorker(mock_monitor, scan_config)
        
        # Mock the signals
        worker.scan_error = Mock()
        worker.scan_completed = Mock()
        
        worker.run()
        
        # Verify error signal was emitted
        worker.scan_error.emit.assert_called_once_with("Failed to start scan")
        
        # Verify completion signal was not emitted
        worker.scan_completed.emit.assert_not_called()
    
    def test_widget_initialization(self, widget_module):
        """Test widget initialization."""
        widget = widget_module.FilesystemIntegrityWidget()
        
        assert widget is not None
        assert hasattr(widget, 'integrity_monitor')
        assert hasattr(widget, 'platform_detector')
        assert hasattr(widget, 'scan_history')
        assert hasattr(widget, 'logger')
        assert widget.current_scan_worker is None
        assert widget.scan_history == []
    
    def test_widget_get_info(self, widget_module):
        """Test widget get_widget_info method."""
        widget = widget_module.FilesystemIntegrityWidget()
        info = widget.get_widget_info()
        
        assert isinstance(info, dict)
        assert info['name'] == 'Filesystem Integrity Monitor'
        assert info['description'] == 'Monitor and analyze filesystem integrity'
        assert info['version'] == '1.0.0'
        assert info['requires_admin'] is True
        assert 'windows' in info['supported_platforms']
        assert 'features' in info
        assert len(info['features']) > 0
    
    def test_widget_update_scan_progress(self, widget_module):
        """Test scan progress update."""
        widget = widget_module.FilesystemIntegrityWidget()
        
        # Mock UI components
        widget.progress_bar = Mock()
        widget.progress_label = Mock()
        widget.files_scanned_label = Mock()
        widget.errors_found_label = Mock()
        
        progress_data = {
            'progress_percent': 75,
            'files_scanned': 500,
            'errors_found': 3,
            'current_path': '/test/current/file.txt'
        }
        
        widget.update_scan_progress(progress_data)
        
        # Verify UI was updated
        widget.progress_bar.setValue.assert_called_with(75)
        widget.progress_label.setText.assert_called_with("Scanning: /test/current/file.txt")
        widget.files_scanned_label.setText.assert_called_with("Files scanned: 500")
        widget.errors_found_label.setText.assert_called_with("Errors found: 3")
    
    def test_widget_scan_completed(self, widget_module):
        """Test scan completion handling."""
        widget = widget_module.FilesystemIntegrityWidget()
        
        # Mock UI components
        widget.progress_bar = Mock()
        widget.progress_label = Mock()
        widget.status_label = Mock()
        
        scan_result = {
            'success': True,
            'start_time': '2025-08-29T10:00:00Z',
            'statistics': {'files_scanned': 1000},
            'corruption_analysis': {'statistics': {}, 'corruptions': []},
            'repair_recommendations': {'recommendations': []}
        }
        
        # Mock the scan_stopped and other methods
        widget.scan_stopped = Mock()
        widget.update_display = Mock()
        widget.populate_scan_results = Mock()
        
        with patch.object(widget_module, 'QMessageBox'):
            widget.scan_completed(scan_result)
        
        # Verify scan result was added to history
        assert scan_result in widget.scan_history
        
        # Verify UI updates
        widget.progress_bar.setValue.assert_called_with(100)
        widget.progress_label.setText.assert_called_with("Scan completed")
        widget.status_label.setText.assert_called_with("Scan completed successfully")
    
    def test_widget_scan_error(self, widget_module):
        """Test scan error handling."""
        widget = widget_module.FilesystemIntegrityWidget()
        
        # Mock UI components
        widget.progress_label = Mock()
        widget.status_label = Mock()
        widget.scan_stopped = Mock()
        
        error_message = "Test scan error"
        
        with patch.object(widget_module, 'QMessageBox'):
            widget.scan_error(error_message)
        
        # Verify UI updates
        widget.progress_label.setText.assert_called_with(f"Scan failed: {error_message}")
        widget.status_label.setText.assert_called_with("Scan failed")
        widget.scan_stopped.assert_called_once()
    
    def test_widget_populate_corruption_analysis(self, widget_module):
        """Test corruption analysis population."""
        widget = widget_module.FilesystemIntegrityWidget()
        
        # Mock UI components
        widget.corruption_count_label = Mock()
        widget.critical_count_label = Mock()
        widget.high_count_label = Mock()
        widget.medium_count_label = Mock()
        widget.corruption_table = Mock()
        
        analysis = {
            'statistics': {
                'corruptions_found': 5,
                'critical_issues': 1,
                'high_severity': 2,
                'medium_severity': 2
            },
            'corruptions': [
                {
                    'path': '/test/file1.txt',
                    'type': 'checksum_mismatch',
                    'severity': 'high',
                    'description': 'Checksum mismatch',
                    'timestamp': '2025-08-29T10:00:00Z'
                }
            ]
        }
        
        widget.populate_corruption_analysis(analysis)
        
        # Verify summary labels were updated
        widget.corruption_count_label.setText.assert_called_with("Total corruptions: 5")
        widget.critical_count_label.setText.assert_called_with("Critical: 1")
        widget.high_count_label.setText.assert_called_with("High: 2")
        widget.medium_count_label.setText.assert_called_with("Medium: 2")
        
        # Verify table was populated
        widget.corruption_table.setRowCount.assert_called_with(1)
    
    def test_widget_update_display(self, widget_module):
        """Test display update."""
        widget = widget_module.FilesystemIntegrityWidget()
        
        # Mock UI components
        widget.total_scans_label = Mock()
        widget.corruptions_found_label = Mock()
        widget.repairs_suggested_label = Mock()
        widget.avg_scan_time_label = Mock()
        widget.health_status_label = Mock()
        widget.health_details_text = Mock()
        widget.update_scheduled_scans_display = Mock()
        
        # Mock monitor methods
        widget.integrity_monitor.get_scan_metrics.return_value = {
            'total_scans': 10,
            'corruptions_found': 3,
            'repairs_suggested': 2,
            'average_scan_time': 125.5
        }
        
        widget.integrity_monitor.get_health_status.return_value = {
            'status': 'healthy',
            'message': 'All systems operational'
        }
        
        widget.update_display()
        
        # Verify metric labels were updated
        widget.total_scans_label.setText.assert_called_with("Total scans: 10")
        widget.corruptions_found_label.setText.assert_called_with("Corruptions found: 3")
        widget.repairs_suggested_label.setText.assert_called_with("Repairs suggested: 2")
        widget.avg_scan_time_label.setText.assert_called_with("Avg scan time: 125.5s")
        
        # Verify health status was updated
        widget.health_status_label.setText.assert_called_with("Status: Healthy")
        widget.health_details_text.setText.assert_called_with("All systems operational")
    
    def test_widget_edge_cases(self, widget_module):
        """Test edge cases and error handling."""
        widget = widget_module.FilesystemIntegrityWidget()
        
        # Test with empty/None data
        widget.update_scan_progress({})
        widget.scan_completed({})
        widget.populate_corruption_analysis({})
        widget.populate_repair_recommendations({})
        
        # Should not raise exceptions
        assert True
    
    def test_pyqt_unavailable_fallback(self, widget_module):
        """Test behavior when PyQt5 is not available."""
        # Temporarily set PYQT_AVAILABLE to False
        original_pyqt = widget_module.PYQT_AVAILABLE
        widget_module.PYQT_AVAILABLE = False
        
        try:
            widget = widget_module.FilesystemIntegrityWidget()
            
            # Should not raise exception, just log error
            assert widget is not None
            
            # UI methods should return early without errors
            widget.setup_ui()
            widget.select_scan_paths()
            widget.start_scan()
            widget.stop_scan()
            
        finally:
            # Restore original value
            widget_module.PYQT_AVAILABLE = original_pyqt


def test_execution_info():
    """Test to capture execution information."""
    execution_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\nTest execution started at: {execution_time}")
    print(f"Target module: filesystem_integrity_widget.py")
    print(f"Test framework: pytest")
    print(f"Python version: {sys.version}")
    
    assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])