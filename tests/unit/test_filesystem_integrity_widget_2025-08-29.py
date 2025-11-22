"""
Comprehensive unit tests for filesystem_integrity_widget.py

Test file: test_filesystem_integrity_widget_2025-08-29.py
Target module: filesystem_integrity_widget.py
Created: 2025-08-29
Framework: pytest

This module contains comprehensive unit tests for the FilesystemIntegrityWidget
class and its related components, including the ScanWorker thread class.

Tests cover:
- Widget initialization and UI setup
- Scan configuration and execution
- Progress tracking and updates
- Error handling and edge cases
- UI interactions and user actions
- Mock data and dependency injection
"""

import json
import os
import sys
from datetime import datetime
from typing import Any, Dict, List
from unittest.mock import MagicMock, Mock, call, patch

import pytest

# Add the source directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

# Test imports with mocking for PyQt5
with patch.dict('sys.modules', {
    'PyQt5': Mock(),
    'PyQt5.QtWidgets': Mock(),
    'PyQt5.QtCore': Mock(),
    'PyQt5.QtGui': Mock(),
}):
    from src.tools.system.diagnostics_monitoring.gui.filesystem_integrity_widget import (
        PYQT_AVAILABLE, FilesystemIntegrityWidget, ScanWorker)


class TestScanWorker:
    """Test cases for the ScanWorker thread class."""
    
    @pytest.fixture
    def mock_integrity_monitor(self):
        """Create a mock integrity monitor."""
        monitor = Mock()
        monitor.start_scan.return_value = True
        monitor.is_scanning.return_value = False
        monitor.get_scan_status.return_value = {
            'success': True,
            'start_time': '2025-08-29T10:00:00Z',
            'duration_seconds': 120.5,
            'statistics': {
                'files_scanned': 1000,
                'errors_encountered': 5,
                'corruptions_found': 2
            }
        }
        return monitor
    
    @pytest.fixture
    def scan_config(self):
        """Create a sample scan configuration."""
        return {
            'scan_type': 'QUICK',
            'paths': ['/test/path1', '/test/path2'],
            'config_override': {
                'check_checksums': True,
                'verify_permissions': True,
                'verify_timestamps': True,
                'max_depth': 10
            }
        }
    
    def test_scan_worker_initialization(self, mock_integrity_monitor, scan_config):
        """Test ScanWorker initialization."""
        worker = ScanWorker(mock_integrity_monitor, scan_config)
        
        assert worker.integrity_monitor == mock_integrity_monitor
        assert worker.scan_config == scan_config
        assert worker.logger is not None
        assert hasattr(worker, 'progress_updated')
        assert hasattr(worker, 'scan_completed')
        assert hasattr(worker, 'scan_error')
    
    @patch('utilities.system.diagnostics_monitoring.gui.filesystem_integrity_widget.QThread')
    def test_scan_worker_successful_run(self, mock_qthread, mock_integrity_monitor, scan_config):
        """Test successful scan execution."""
        worker = ScanWorker(mock_integrity_monitor, scan_config)
        worker.msleep = Mock()  # Mock the sleep method
        
        # Mock signals
        worker.progress_updated = Mock()
        worker.scan_completed = Mock()
        worker.scan_error = Mock()
        
        # Run the worker
        worker.run()
        
        # Verify scan was started
        mock_integrity_monitor.start_scan.assert_called_once()
        
        # Verify scan completion was emitted
        worker.scan_completed.emit.assert_called_once()
        
        # Verify no error was emitted
        worker.scan_error.emit.assert_not_called()
    
    @patch('utilities.system.diagnostics_monitoring.gui.filesystem_integrity_widget.QThread')
    def test_scan_worker_start_scan_failure(self, mock_qthread, mock_integrity_monitor, scan_config):
        """Test scan worker when start_scan fails."""
        mock_integrity_monitor.start_scan.return_value = False
        
        worker = ScanWorker(mock_integrity_monitor, scan_config)
        worker.scan_error = Mock()
        worker.scan_completed = Mock()
        
        worker.run()
        
        # Verify error was emitted
        worker.scan_error.emit.assert_called_once_with("Failed to start scan")
        worker.scan_completed.emit.assert_not_called()
    
    @patch('utilities.system.diagnostics_monitoring.gui.filesystem_integrity_widget.QThread')
    def test_scan_worker_get_status_failure(self, mock_qthread, mock_integrity_monitor, scan_config):
        """Test scan worker when get_scan_status fails."""
        mock_integrity_monitor.get_scan_status.return_value = None
        
        worker = ScanWorker(mock_integrity_monitor, scan_config)
        worker.msleep = Mock()
        worker.scan_error = Mock()
        worker.scan_completed = Mock()
        
        worker.run()
        
        # Verify error was emitted
        worker.scan_error.emit.assert_called_once_with("Failed to get scan results")
        worker.scan_completed.emit.assert_not_called()
    
    @patch('utilities.system.diagnostics_monitoring.gui.filesystem_integrity_widget.QThread')
    def test_scan_worker_exception_handling(self, mock_qthread, mock_integrity_monitor, scan_config):
        """Test scan worker exception handling."""
        mock_integrity_monitor.start_scan.side_effect = Exception("Test exception")
        
        worker = ScanWorker(mock_integrity_monitor, scan_config)
        worker.scan_error = Mock()
        
        worker.run()
        
        # Verify error was emitted with exception message
        worker.scan_error.emit.assert_called_once_with("Test exception")


class TestFilesystemIntegrityWidget:
    """Test cases for the FilesystemIntegrityWidget class."""
    
    @pytest.fixture
    def mock_pyqt_components(self):
        """Mock PyQt5 components."""
        with patch.multiple(
            'utilities.system.diagnostics_monitoring.gui.filesystem_integrity_widget',
            PYQT_AVAILABLE=True,
            QWidget=Mock,
            QVBoxLayout=Mock,
            QHBoxLayout=Mock,
            QSplitter=Mock,
            QTabWidget=Mock,
            QGroupBox=Mock,
            QGridLayout=Mock,
            QLabel=Mock,
            QProgressBar=Mock,
            QPushButton=Mock,
            QTextEdit=Mock,
            QTableWidget=Mock,
            QTableWidgetItem=Mock,
            QHeaderView=Mock,
            QComboBox=Mock,
            QCheckBox=Mock,
            QSpinBox=Mock,
            QTreeWidget=Mock,
            QTreeWidgetItem=Mock,
            QTimer=Mock,
            QMessageBox=Mock,
            QFileDialog=Mock
        ):
            yield
    
    @pytest.fixture
    def mock_dependencies(self):
        """Mock external dependencies."""
        with patch.multiple(
            'utilities.system.diagnostics_monitoring.gui.filesystem_integrity_widget',
            IntegrityMonitor=Mock,
            get_platform_detector=Mock
        ):
            yield
    
    @pytest.fixture
    def widget(self, mock_pyqt_components, mock_dependencies):
        """Create a FilesystemIntegrityWidget instance for testing."""
        widget = FilesystemIntegrityWidget()
        
        # Mock UI components that would be created
        widget.scan_type_combo = Mock()
        widget.paths_button = Mock()
        widget.checksum_check = Mock()
        widget.permissions_check = Mock()
        widget.timestamps_check = Mock()
        widget.max_depth_spin = Mock()
        widget.start_scan_button = Mock()
        widget.stop_scan_button = Mock()
        widget.progress_bar = Mock()
        widget.progress_label = Mock()
        widget.files_scanned_label = Mock()
        widget.errors_found_label = Mock()
        widget.status_label = Mock()
        widget.results_table = Mock()
        widget.corruption_table = Mock()
        widget.recommendations_table = Mock()
        widget.history_table = Mock()
        widget.scheduled_scans_list = Mock()
        widget.health_status_label = Mock()
        widget.health_details_text = Mock()
        
        # Mock labels for statistics
        widget.total_scans_label = Mock()
        widget.corruptions_found_label = Mock()
        widget.repairs_suggested_label = Mock()
        widget.avg_scan_time_label = Mock()
        widget.corruption_count_label = Mock()
        widget.critical_count_label = Mock()
        widget.high_count_label = Mock()
        widget.medium_count_label = Mock()
        widget.filesystem_count_label = Mock()
        widget.last_scan_label = Mock()
        
        return widget
    
    def test_widget_initialization(self, mock_pyqt_components, mock_dependencies):
        """Test widget initialization."""
        widget = FilesystemIntegrityWidget()
        
        assert widget.integrity_monitor is not None
        assert widget.platform_detector is not None
        assert widget.current_scan_worker is None
        assert widget.scan_history == []
        assert widget.logger is not None
    
    def test_widget_initialization_without_pyqt(self):
        """Test widget initialization when PyQt5 is not available."""
        with patch('utilities.system.diagnostics_monitoring.gui.filesystem_integrity_widget.PYQT_AVAILABLE', False):
            widget = FilesystemIntegrityWidget()
            # Should not raise an exception, just log an error
            assert widget is not None
    
    def test_setup_ui_without_pyqt(self, widget):
        """Test setup_ui when PyQt5 is not available."""
        with patch('utilities.system.diagnostics_monitoring.gui.filesystem_integrity_widget.PYQT_AVAILABLE', False):
            # Should return early without errors
            widget.setup_ui()
    
    def test_select_scan_paths(self, widget):
        """Test scan path selection."""
        # Mock QFileDialog
        mock_dialog = Mock()
        mock_dialog.exec_.return_value = True
        mock_dialog.selectedFiles.return_value = ['/test/path1', '/test/path2']
        
        with patch('utilities.system.diagnostics_monitoring.gui.filesystem_integrity_widget.QFileDialog', return_value=mock_dialog):
            widget.select_scan_paths()
            
            assert hasattr(widget, 'scan_paths')
            assert widget.scan_paths == ['/test/path1', '/test/path2']
            widget.paths_button.setText.assert_called_with("Paths: 2 selected")
    
    def test_start_scan_success(self, widget):
        """Test successful scan start."""
        # Setup mock UI components
        widget.scan_type_combo.currentText.return_value = "Quick Scan"
        widget.checksum_check.isChecked.return_value = True
        widget.permissions_check.isChecked.return_value = True
        widget.timestamps_check.isChecked.return_value = True
        widget.max_depth_spin.value.return_value = 10
        widget.scan_paths = ['/test/path']
        
        with patch('utilities.system.diagnostics_monitoring.gui.filesystem_integrity_widget.ScanWorker') as mock_worker_class:
            mock_worker = Mock()
            mock_worker_class.return_value = mock_worker
            
            widget.start_scan()
            
            # Verify worker was created and started
            mock_worker_class.assert_called_once()
            mock_worker.start.assert_called_once()
            
            # Verify UI state updates
            widget.start_scan_button.setEnabled.assert_called_with(False)
            widget.stop_scan_button.setEnabled.assert_called_with(True)
            widget.progress_bar.setValue.assert_called_with(0)
            widget.progress_label.setText.assert_called_with("Starting scan...")
            widget.status_label.setText.assert_called_with("Scan in progress...")
    
    def test_start_scan_exception(self, widget):
        """Test scan start with exception."""
        widget.scan_type_combo.currentText.side_effect = Exception("Test exception")
        
        with patch('utilities.system.diagnostics_monitoring.gui.filesystem_integrity_widget.QMessageBox') as mock_msgbox:
            widget.start_scan()
            mock_msgbox.critical.assert_called_once()
    
    def test_stop_scan(self, widget):
        """Test scan stop functionality."""
        # Setup mock worker
        mock_worker = Mock()
        mock_worker.isRunning.return_value = True
        widget.current_scan_worker = mock_worker
        
        widget.stop_scan()
        
        # Verify stop sequence
        widget.integrity_monitor.stop_scan.assert_called_once()
        mock_worker.quit.assert_called_once()
        mock_worker.wait.assert_called_once_with(5000)
        
        # Verify UI state reset
        widget.start_scan_button.setEnabled.assert_called_with(True)
        widget.stop_scan_button.setEnabled.assert_called_with(False)
        assert widget.current_scan_worker is None
    
    def test_stop_scan_exception(self, widget):
        """Test stop scan with exception."""
        widget.integrity_monitor.stop_scan.side_effect = Exception("Test exception")
        
        with patch('utilities.system.diagnostics_monitoring.gui.filesystem_integrity_widget.QMessageBox') as mock_msgbox:
            widget.stop_scan()
            mock_msgbox.warning.assert_called_once()
    
    def test_update_scan_progress(self, widget):
        """Test scan progress updates."""
        progress_data = {
            'progress_percent': 75,
            'files_scanned': 500,
            'errors_found': 3,
            'current_path': '/test/current/file.txt'
        }
        
        widget.update_scan_progress(progress_data)
        
        # Verify UI updates
        widget.progress_bar.setValue.assert_called_with(75)
        widget.progress_label.setText.assert_called_with("Scanning: /test/current/file.txt")
        widget.files_scanned_label.setText.assert_called_with("Files scanned: 500")
        widget.errors_found_label.setText.assert_called_with("Errors found: 3")
    
    def test_update_scan_progress_exception(self, widget):
        """Test scan progress update with exception."""
        widget.progress_bar.setValue.side_effect = Exception("Test exception")
        
        progress_data = {'progress_percent': 50}
        
        # Should not raise exception
        widget.update_scan_progress(progress_data)
    
    def test_scan_completed(self, widget):
        """Test scan completion handling."""
        scan_result = {
            'success': True,
            'start_time': '2025-08-29T10:00:00Z',
            'duration_seconds': 120.5,
            'statistics': {
                'files_scanned': 1000,
                'errors_encountered': 5
            },
            'corruption_analysis': {
                'statistics': {'corruptions_found': 2},
                'corruptions': []
            },
            'repair_recommendations': {
                'recommendations': []
            }
        }
        
        with patch('utilities.system.diagnostics_monitoring.gui.filesystem_integrity_widget.QMessageBox') as mock_msgbox:
            widget.scan_completed(scan_result)
            
            # Verify scan result was added to history
            assert scan_result in widget.scan_history
            
            # Verify UI updates
            widget.progress_bar.setValue.assert_called_with(100)
            widget.progress_label.setText.assert_called_with("Scan completed")
            widget.status_label.setText.assert_called_with("Scan completed successfully")
            
            # Verify completion message
            mock_msgbox.information.assert_called_once()
    
    def test_scan_error(self, widget):
        """Test scan error handling."""
        error_message = "Test scan error"
        
        with patch('utilities.system.diagnostics_monitoring.gui.filesystem_integrity_widget.QMessageBox') as mock_msgbox:
            widget.scan_error(error_message)
            
            # Verify UI updates
            widget.progress_label.setText.assert_called_with(f"Scan failed: {error_message}")
            widget.status_label.setText.assert_called_with("Scan failed")
            
            # Verify error message
            mock_msgbox.critical.assert_called_once()
    
    def test_populate_corruption_analysis(self, widget):
        """Test corruption analysis population."""
        analysis = {
            'statistics': {
                'corruptions_found': 10,
                'critical_issues': 2,
                'high_severity': 3,
                'medium_severity': 5
            },
            'corruptions': [
                {
                    'path': '/test/file1.txt',
                    'type': 'checksum_mismatch',
                    'severity': 'high',
                    'description': 'File checksum does not match',
                    'timestamp': '2025-08-29T10:00:00Z'
                },
                {
                    'path': '/test/file2.txt',
                    'type': 'permission_error',
                    'severity': 'medium',
                    'description': 'Invalid file permissions',
                    'timestamp': '2025-08-29T10:01:00Z'
                }
            ]
        }
        
        widget.populate_corruption_analysis(analysis)
        
        # Verify summary labels were updated
        widget.corruption_count_label.setText.assert_called_with("Total corruptions: 10")
        widget.critical_count_label.setText.assert_called_with("Critical: 2")
        widget.high_count_label.setText.assert_called_with("High: 3")
        widget.medium_count_label.setText.assert_called_with("Medium: 5")
        
        # Verify table was populated
        widget.corruption_table.setRowCount.assert_called_with(2)
    
    def test_populate_repair_recommendations(self, widget):
        """Test repair recommendations population."""
        recommendations = {
            'recommendations': [
                {
                    'priority': 'high',
                    'action': 'restore_from_backup',
                    'description': 'Restore corrupted file from backup',
                    'command': 'cp /backup/file.txt /original/file.txt',
                    'automation_possible': True,
                    'estimated_time': '5 minutes'
                },
                {
                    'priority': 'medium',
                    'action': 'fix_permissions',
                    'description': 'Fix file permissions',
                    'command': 'chmod 644 /test/file.txt',
                    'automation_possible': True,
                    'estimated_time': '1 minute'
                }
            ]
        }
        
        widget.populate_repair_recommendations(recommendations)
        
        # Verify table was populated
        widget.recommendations_table.setRowCount.assert_called_with(2)
    
    def test_populate_scan_history(self, widget):
        """Test scan history population."""
        widget.scan_history = [
            {
                'start_time': '2025-08-29T10:00:00Z',
                'scan_type': 'QUICK',
                'duration_seconds': 120.5,
                'success': True,
                'statistics': {
                    'files_scanned': 1000,
                    'errors_encountered': 5
                }
            },
            {
                'start_time': '2025-08-29T11:00:00Z',
                'scan_type': 'FULL',
                'duration_seconds': 300.0,
                'success': False,
                'statistics': {
                    'files_scanned': 500,
                    'errors_encountered': 10
                }
            }
        ]
        
        widget.populate_scan_history()
        
        # Verify table was populated
        widget.history_table.setRowCount.assert_called_with(2)
    
    def test_update_display(self, widget):
        """Test display update functionality."""
        # Mock monitor methods
        widget.integrity_monitor.get_scan_metrics.return_value = {
            'total_scans': 10,
            'corruptions_found': 5,
            'repairs_suggested': 3,
            'average_scan_time': 125.7
        }
        
        widget.integrity_monitor.get_health_status.return_value = {
            'status': 'healthy',
            'message': 'All systems operational'
        }
        
        widget.integrity_monitor.get_scheduled_scans.return_value = []
        
        widget.update_display()
        
        # Verify metric labels were updated
        widget.total_scans_label.setText.assert_called_with("Total scans: 10")
        widget.corruptions_found_label.setText.assert_called_with("Corruptions found: 5")
        widget.repairs_suggested_label.setText.assert_called_with("Repairs suggested: 3")
        widget.avg_scan_time_label.setText.assert_called_with("Avg scan time: 125.7s")
        
        # Verify health status was updated
        widget.health_status_label.setText.assert_called_with("Status: Healthy")
        widget.health_details_text.setText.assert_called_with("All systems operational")
    
    def test_update_display_different_health_statuses(self, widget):
        """Test display update with different health statuses."""
        test_cases = [
            ('healthy', 'color: green;'),
            ('warning', 'color: orange;'),
            ('critical', 'color: red;'),
            ('corrupted', 'color: red;'),
            ('unknown', 'color: gray;')
        ]
        
        widget.integrity_monitor.get_scan_metrics.return_value = {}
        widget.integrity_monitor.get_scheduled_scans.return_value = []
        
        for status, expected_style in test_cases:
            widget.integrity_monitor.get_health_status.return_value = {
                'status': status,
                'message': f'Status is {status}'
            }
            
            widget.update_display()
            widget.health_status_label.setStyleSheet.assert_called_with(expected_style)
    
    def test_update_scheduled_scans_display(self, widget):
        """Test scheduled scans display update."""
        scheduled_scans = [
            {
                'scan_type': 'QUICK',
                'schedule_time': '2025-08-30T10:00:00Z',
                'recurring': True
            },
            {
                'scan_type': 'FULL',
                'schedule_time': '2025-08-31T10:00:00Z',
                'recurring': False
            }
        ]
        
        widget.integrity_monitor.get_scheduled_scans.return_value = scheduled_scans
        
        widget.update_scheduled_scans_display()
        
        # Verify list was cleared and populated
        widget.scheduled_scans_list.clear.assert_called_once()
        widget.scheduled_scans_list.addTopLevelItem.assert_called()
    
    def test_schedule_scan(self, widget):
        """Test scan scheduling dialog."""
        with patch('utilities.system.diagnostics_monitoring.gui.filesystem_integrity_widget.QMessageBox') as mock_msgbox:
            widget.schedule_scan()
            mock_msgbox.information.assert_called_once()
    
    def test_apply_selected_recommendations_no_selection(self, widget):
        """Test apply recommendations with no selection."""
        widget.recommendations_table.selectedItems.return_value = []
        
        with patch('utilities.system.diagnostics_monitoring.gui.filesystem_integrity_widget.QMessageBox') as mock_msgbox:
            widget.apply_selected_recommendations()
            mock_msgbox.warning.assert_called_once()
    
    def test_apply_selected_recommendations_with_selection(self, widget):
        """Test apply recommendations with selection."""
        # Mock selected items
        mock_item1 = Mock()
        mock_item1.row.return_value = 0
        mock_item2 = Mock()
        mock_item2.row.return_value = 1
        
        widget.recommendations_table.selectedItems.return_value = [mock_item1, mock_item2]
        
        with patch('utilities.system.diagnostics_monitoring.gui.filesystem_integrity_widget.QMessageBox') as mock_msgbox:
            mock_msgbox.question.return_value = mock_msgbox.Yes
            
            widget.apply_selected_recommendations()
            
            # Verify confirmation dialog was shown
            mock_msgbox.question.assert_called_once()
            mock_msgbox.information.assert_called_once()
    
    def test_generate_repair_script(self, widget):
        """Test repair script generation."""
        mock_dialog = Mock()
        mock_dialog.getSaveFileName.return_value = ("/test/script.sh", "Shell Scripts (*.sh)")
        
        with patch('utilities.system.diagnostics_monitoring.gui.filesystem_integrity_widget.QFileDialog', return_value=mock_dialog):
            with patch('utilities.system.diagnostics_monitoring.gui.filesystem_integrity_widget.QMessageBox') as mock_msgbox:
                widget.generate_repair_script()
                mock_msgbox.information.assert_called_once()
    
    def test_export_results(self, widget):
        """Test results export."""
        mock_dialog = Mock()
        mock_dialog.getSaveFileName.return_value = ("/test/results.json", "JSON Files (*.json)")
        
        with patch('utilities.system.diagnostics_monitoring.gui.filesystem_integrity_widget.QFileDialog', return_value=mock_dialog):
            with patch('utilities.system.diagnostics_monitoring.gui.filesystem_integrity_widget.QMessageBox') as mock_msgbox:
                widget.export_results()
                mock_msgbox.information.assert_called_once()
    
    def test_clear_scan_history_confirmed(self, widget):
        """Test scan history clearing when confirmed."""
        widget.scan_history = [{'test': 'data'}]
        
        with patch('utilities.system.diagnostics_monitoring.gui.filesystem_integrity_widget.QMessageBox') as mock_msgbox:
            mock_msgbox.question.return_value = mock_msgbox.Yes
            
            widget.clear_scan_history()
            
            assert widget.scan_history == []
            mock_msgbox.information.assert_called_once()
    
    def test_clear_scan_history_cancelled(self, widget):
        """Test scan history clearing when cancelled."""
        original_history = [{'test': 'data'}]
        widget.scan_history = original_history.copy()
        
        with patch('utilities.system.diagnostics_monitoring.gui.filesystem_integrity_widget.QMessageBox') as mock_msgbox:
            mock_msgbox.question.return_value = mock_msgbox.No
            
            widget.clear_scan_history()
            
            assert widget.scan_history == original_history
            mock_msgbox.information.assert_not_called()
    
    def test_export_scan_history(self, widget):
        """Test scan history export."""
        mock_dialog = Mock()
        mock_dialog.getSaveFileName.return_value = ("/test/history.json", "JSON Files (*.json)")
        
        with patch('utilities.system.diagnostics_monitoring.gui.filesystem_integrity_widget.QFileDialog', return_value=mock_dialog):
            with patch('utilities.system.diagnostics_monitoring.gui.filesystem_integrity_widget.QMessageBox') as mock_msgbox:
                widget.export_scan_history()
                mock_msgbox.information.assert_called_once()
    
    def test_get_widget_info(self, widget):
        """Test widget information retrieval."""
        info = widget.get_widget_info()
        
        assert info['name'] == 'Filesystem Integrity Monitor'
        assert info['description'] == 'Monitor and analyze filesystem integrity'
        assert info['version'] == '1.0.0'
        assert info['requires_admin'] is True
        assert 'windows' in info['supported_platforms']
        assert 'macos' in info['supported_platforms']
        assert 'linux' in info['supported_platforms']
        assert len(info['features']) > 0
    
    def test_edge_case_empty_scan_result(self, widget):
        """Test handling of empty scan results."""
        empty_result = {}
        
        # Should not raise exception
        widget.scan_completed(empty_result)
        assert empty_result in widget.scan_history
    
    def test_edge_case_invalid_progress_data(self, widget):
        """Test handling of invalid progress data."""
        invalid_progress = {
            'progress_percent': 'invalid',
            'files_scanned': None,
            'errors_found': 'not_a_number'
        }
        
        # Should not raise exception
        widget.update_scan_progress(invalid_progress)
    
    def test_edge_case_missing_ui_components(self):
        """Test behavior when UI components are missing."""
        widget = FilesystemIntegrityWidget()
        
        # Should not raise exception when calling methods without UI setup
        widget.update_display()
        widget.scan_stopped()


class TestIntegration:
    """Integration tests for the complete widget functionality."""
    
    @pytest.fixture
    def full_widget_setup(self, mock_pyqt_components, mock_dependencies):
        """Setup a fully configured widget for integration testing."""
        widget = FilesystemIntegrityWidget()
        
        # Setup all UI components
        widget.setup_ui()
        
        return widget
    
    def test_complete_scan_workflow(self, full_widget_setup):
        """Test a complete scan workflow from start to finish."""
        widget = full_widget_setup
        
        # Mock all UI components
        widget.scan_type_combo = Mock()
        widget.scan_type_combo.currentText.return_value = "Quick Scan"
        widget.checksum_check = Mock()
        widget.checksum_check.isChecked.return_value = True
        widget.permissions_check = Mock()
        widget.permissions_check.isChecked.return_value = True
        widget.timestamps_check = Mock()
        widget.timestamps_check.isChecked.return_value = True
        widget.max_depth_spin = Mock()
        widget.max_depth_spin.value.return_value = 10
        
        widget.start_scan_button = Mock()
        widget.stop_scan_button = Mock()
        widget.progress_bar = Mock()
        widget.progress_label = Mock()
        widget.files_scanned_label = Mock()
        widget.errors_found_label = Mock()
        widget.status_label = Mock()
        
        # Start scan
        with patch('utilities.system.diagnostics_monitoring.gui.filesystem_integrity_widget.ScanWorker') as mock_worker_class:
            mock_worker = Mock()
            mock_worker_class.return_value = mock_worker
            
            widget.start_scan()
            
            # Simulate progress updates
            progress_data = {
                'progress_percent': 50,
                'files_scanned': 500,
                'errors_found': 2,
                'current_path': '/test/file.txt'
            }
            widget.update_scan_progress(progress_data)
            
            # Simulate scan completion
            scan_result = {
                'success': True,
                'start_time': '2025-08-29T10:00:00Z',
                'duration_seconds': 120.5,
                'statistics': {
                    'files_scanned': 1000,
                    'errors_encountered': 2
                },
                'corruption_analysis': {
                    'statistics': {'corruptions_found': 1},
                    'corruptions': [{
                        'path': '/test/corrupted.txt',
                        'type': 'checksum_mismatch',
                        'severity': 'high',
                        'description': 'File checksum mismatch',
                        'timestamp': '2025-08-29T10:00:00Z'
                    }]
                },
                'repair_recommendations': {
                    'recommendations': [{
                        'priority': 'high',
                        'action': 'restore_backup',
                        'description': 'Restore from backup',
                        'command': 'cp /backup/file.txt /original/file.txt',
                        'automation_possible': True,
                        'estimated_time': '2 minutes'
                    }]
                }
            }
            
            with patch('utilities.system.diagnostics_monitoring.gui.filesystem_integrity_widget.QMessageBox'):
                widget.scan_completed(scan_result)
            
            # Verify complete workflow
            assert len(widget.scan_history) == 1
            assert widget.scan_history[0] == scan_result


@pytest.fixture(scope="session")
def test_execution_timestamp():
    """Generate timestamp for test execution."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def pytest_sessionstart(session):
    """Called after the Session object has been created."""
    print(f"\n{'='*80}")
    print(f"FILESYSTEM INTEGRITY WIDGET UNIT TESTS")
    print(f"{'='*80}")
    print(f"Test execution started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target module: filesystem_integrity_widget.py")
    print(f"Test framework: pytest")
    print(f"{'='*80}\n")


def pytest_sessionfinish(session, exitstatus):
    """Called after whole test run finished."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    status = "PASSED" if exitstatus == 0 else "FAILED"
    
    print(f"\n{'='*80}")
    print(f"TEST EXECUTION COMPLETED")
    print(f"{'='*80}")
    print(f"Completion time: {timestamp}")
    print(f"Exit status: {exitstatus} ({status})")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    # Run tests with comprehensive reporting
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--strict-markers",
        "--strict-config"
    ])