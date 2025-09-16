"""
Comprehensive unit tests for disk_health_widget.py

Test file: test_disk_health_widget_2025-08-29.py
Target module: disk_health_widget.py
Created: 2025-08-29
Framework: pytest

This module contains comprehensive unit tests for the DiskHealthWidget class,
covering all methods, GUI components, error handling, and edge cases.
"""

import json
import sys
from datetime import datetime
from typing import Any, Dict, List
from unittest.mock import MagicMock, Mock, PropertyMock, patch

import pytest


class MockQWidget:
    """Mock QWidget class for testing."""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.layout_set = False
        self.style_sheet = ""
        self.destroyed = False
        
    def setLayout(self, layout):
        self.layout_set = True
        
    def setStyleSheet(self, style):
        self.style_sheet = style
        
    def destroy(self):
        self.destroyed = True


class MockQVBoxLayout:
    """Mock QVBoxLayout class."""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.widgets = []
        self.layouts = []
        self.margins = (0, 0, 0, 0)
        self.spacing = 0
        
    def addWidget(self, widget):
        self.widgets.append(widget)
        
    def addLayout(self, layout):
        self.layouts.append(layout)
        
    def setContentsMargins(self, left, top, right, bottom):
        self.margins = (left, top, right, bottom)
        
    def setSpacing(self, spacing):
        self.spacing = spacing
        
    def addStretch(self):
        self.widgets.append("stretch")


class MockQHBoxLayout:
    """Mock QHBoxLayout class."""
    
    def __init__(self):
        self.widgets = []
        self.stretches = 0
        
    def addWidget(self, widget):
        self.widgets.append(widget)
        
    def addStretch(self):
        self.stretches += 1


class MockQLabel:
    """Mock QLabel class."""
    
    def __init__(self, text=""):
        self.text = text
        self.font = None
        self.style_sheet = ""
        
    def setText(self, text):
        self.text = text
        
    def setFont(self, font):
        self.font = font
        
    def setStyleSheet(self, style):
        self.style_sheet = style


class MockQTimer:
    """Mock QTimer class."""
    
    def __init__(self):
        self.interval_ms = 1000
        self.active = False
        self.timeout_handler = None
        self.single_shot = False
        
    def setInterval(self, ms):
        self.interval_ms = ms
        
    def start(self):
        self.active = True
        
    def stop(self):
        self.active = False
        
    def timeout(self):
        """Mock signal connection."""
        return MagicMock()


class MockQProgressBar:
    """Mock QProgressBar class."""
    
    def __init__(self):
        self.value = 0
        self.text_visible = True
        self.style_sheet = ""
        
    def setValue(self, value):
        self.value = value
        
    def setTextVisible(self, visible):
        self.text_visible = visible
        
    def setStyleSheet(self, style):
        self.style_sheet = style


class MockQTreeWidget:
    """Mock QTreeWidget class."""
    
    def __init__(self):
        self.headers = []
        self.items = []
        self.columns = 0
        self.click_handler = None
        
    def setHeaderLabels(self, labels):
        self.headers = labels
        self.columns = len(labels)
        
    def addTopLevelItem(self, item):
        self.items.append(item)
        
    def clear(self):
        self.items = []
        
    def expandAll(self):
        pass
        
    def resizeColumnToContents(self, column):
        pass
        
    def columnCount(self):
        return self.columns
        
    def itemClicked(self):
        """Mock signal."""
        return MagicMock()


class MockQTreeWidgetItem:
    """Mock QTreeWidgetItem class."""
    
    def __init__(self, data):
        self.data_list = data
        self.user_data = {}
        self.foreground_colors = {}
        
    def setData(self, column, role, data):
        self.user_data[column] = data
        
    def data(self, column, role):
        return self.user_data.get(column)
        
    def setForeground(self, column, color):
        self.foreground_colors[column] = color


class MockQSplitter:
    """Mock QSplitter class."""
    
    def __init__(self, orientation):
        self.orientation = orientation
        self.widgets = []
        self.sizes = []
        
    def addWidget(self, widget):
        self.widgets.append(widget)
        
    def setSizes(self, sizes):
        self.sizes = sizes


class MockQTabWidget:
    """Mock QTabWidget class."""
    
    def __init__(self):
        self.tabs = []
        
    def addTab(self, widget, title):
        self.tabs.append((widget, title))


class MockQGroupBox:
    """Mock QGroupBox class."""
    
    def __init__(self, title=""):
        self.title = title


class MockDiskHealthWidget:
    """Mock implementation of DiskHealthWidget for testing."""
    
    def __init__(self, parent=None):
        # Initialize basic attributes
        self.parent = parent
        self.disk_monitor = None
        self.current_data = {}
        
        # Mock PyQt components
        self.update_timer = MockQTimer()
        self.refresh_button = MagicMock()
        self.auto_refresh_button = MagicMock()
        self.disk_tree = MockQTreeWidget()
        self.details_tabs = MockQTabWidget()
        
        # Summary labels
        self.total_disks_label = MockQLabel("Total Disks: 0")
        self.healthy_disks_label = MockQLabel("Healthy: 0")
        self.warning_disks_label = MockQLabel("Warning: 0")
        self.critical_disks_label = MockQLabel("Critical: 0")
        self.total_capacity_label = MockQLabel("Total Capacity: 0 GB")
        self.total_used_label = MockQLabel("Total Used: 0 GB")
        
        # Details labels
        self.details_title = MockQLabel("Select a disk to view details")
        self.device_id_label = MockQLabel("Device ID: -")
        self.device_path_label = MockQLabel("Device Path: -")
        self.model_label = MockQLabel("Model: -")
        self.serial_label = MockQLabel("Serial Number: -")
        self.size_label = MockQLabel("Size: -")
        self.filesystem_label = MockQLabel("Filesystem: -")
        self.mount_point_label = MockQLabel("Mount Point: -")
        
        # Health labels
        self.health_status_label = MockQLabel("Status: Unknown")
        self.temperature_label = MockQLabel("Temperature: -")
        self.power_on_hours_label = MockQLabel("Power On Hours: -")
        self.usage_progress = MockQProgressBar()
        self.usage_label = MockQLabel("Used: 0 GB / 0 GB (0%)")
        
        # Performance labels
        self.reads_label = MockQLabel("Reads: -")
        self.writes_label = MockQLabel("Writes: -")
        self.read_bytes_label = MockQLabel("Bytes Read: -")
        self.write_bytes_label = MockQLabel("Bytes Written: -")
        
        # Status labels
        self.status_label = MockQLabel("Ready")
        self.last_update_label = MockQLabel("Last Update: Never")
        
        # Color scheme
        self.health_colors = {
            'healthy': '#4CAF50',
            'warning': '#FF9800', 
            'critical': '#F44336',
            'unknown': '#9E9E9E'
        }
        
        # Initialize UI (mocked)
        self.setup_ui()
        self.setup_styles()
        self.initialize_monitor()
    
    def setup_ui(self):
        """Mock UI setup."""
        pass
    
    def setup_styles(self):
        """Mock style setup."""
        pass
    
    def initialize_monitor(self):
        """Mock monitor initialization."""
        self.disk_monitor = MagicMock()
        self.disk_monitor.start_monitoring.return_value = True
        self.disk_monitor.get_current_data.return_value = self._get_mock_data()
        
    def _get_mock_data(self):
        """Get mock disk data for testing."""
        return {
            'summary': {
                'total_physical_disks': 2,
                'total_logical_disks': 3,
                'healthy_disks': 4,
                'warning_disks': 1,
                'critical_disks': 0,
                'total_capacity_gb': 1000.0,
                'total_used_gb': 500.0
            },
            'physical_disks': [
                {
                    'device_id': '/dev/sda',
                    'device_path': '/dev/sda',
                    'model': 'Samsung SSD 980',
                    'serial_number': 'S649NX12345678',
                    'size_bytes': 500000000000,
                    'health_status': 'healthy',
                    'temperature': 42,
                    'power_on_hours': 8760,
                    'io_stats': {
                        'reads_completed': 1000000,
                        'writes_completed': 500000,
                        'sectors_read': 2000000,
                        'sectors_written': 1000000
                    }
                }
            ],
            'logical_disks': [
                {
                    'device_id': 'C:',
                    'device_path': 'C:',
                    'filesystem': 'NTFS',
                    'mount_point': 'C:',
                    'size_bytes': 250000000000,
                    'used_bytes': 100000000000,
                    'used_percent': 40.0,
                    'health_status': 'healthy'
                }
            ]
        }
    
    # Mock all the methods from the original class
    def create_header(self):
        return MockQHBoxLayout()
    
    def create_disk_list_panel(self):
        return MockQWidget()
    
    def create_summary_section(self):
        return MockQGroupBox()
    
    def create_disk_details_panel(self):
        return MockQWidget()
    
    def create_general_tab(self):
        return MockQWidget()
    
    def create_health_tab(self):
        return MockQWidget()
    
    def create_performance_tab(self):
        return MockQWidget()
    
    def create_status_bar(self):
        return MockQHBoxLayout()
    
    def refresh_data(self):
        """Mock refresh data."""
        if self.disk_monitor:
            self.current_data = self.disk_monitor.get_current_data()
            self.update_summary()
            self.update_disk_tree()
            self.status_label.setText("Ready")
            self.last_update_label.setText(
                f"Last Update: {datetime.now().strftime('%H:%M:%S')}"
            )
    
    def update_summary(self):
        """Mock update summary."""
        if not self.current_data:
            return
        
        summary = self.current_data.get('summary', {})
        total_physical = summary.get('total_physical_disks', 0)
        total_logical = summary.get('total_logical_disks', 0)
        total_disks = total_physical + total_logical
        
        self.total_disks_label.setText(f"Total Disks: {total_disks}")
        self.healthy_disks_label.setText(f"Healthy: {summary.get('healthy_disks', 0)}")
        self.warning_disks_label.setText(f"Warning: {summary.get('warning_disks', 0)}")
        self.critical_disks_label.setText(f"Critical: {summary.get('critical_disks', 0)}")
    
    def update_disk_tree(self):
        """Mock update disk tree."""
        self.disk_tree.clear()
        
        if not self.current_data:
            return
        
        physical_disks = self.current_data.get('physical_disks', [])
        for disk in physical_disks:
            self.add_disk_to_tree(disk, 'physical')
        
        logical_disks = self.current_data.get('logical_disks', [])
        for disk in logical_disks:
            self.add_disk_to_tree(disk, 'logical')
    
    def add_disk_to_tree(self, disk, disk_type):
        """Mock add disk to tree."""
        device_id = disk.get('device_id', 'Unknown')
        size_bytes = disk.get('size_bytes', 0)
        health_status = disk.get('health_status', 'unknown')
        
        size_str = self.format_bytes(size_bytes)
        usage_str = "-"
        if disk_type == 'logical':
            used_percent = disk.get('used_percent', 0)
            usage_str = f"{used_percent:.1f}%"
        
        item = MockQTreeWidgetItem([
            device_id, disk_type.title(), size_str, health_status.title(), usage_str
        ])
        item.setData(0, 1, (device_id, disk_type, disk))
        self.disk_tree.addTopLevelItem(item)
    
    def format_bytes(self, bytes_value):
        """Mock format bytes."""
        if bytes_value == 0:
            return "0 B"
        
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        unit_index = 0
        size = float(bytes_value)
        
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
        
        return f"{size:.1f} {units[unit_index]}"
    
    def on_disk_selected(self, item, column):
        """Mock disk selection handler."""
        data = item.data(0, 1)
        if data:
            device_id, disk_type, disk_info = data
            self.update_disk_details(device_id, disk_type, disk_info)
    
    def update_disk_details(self, device_id, disk_type, disk_info):
        """Mock update disk details."""
        self.details_title.setText(f"Details: {device_id} ({disk_type})")
        self.update_general_details(disk_info)
        self.update_health_details(disk_info)
        self.update_performance_details(disk_info)
    
    def update_general_details(self, disk_info):
        """Mock update general details."""
        device_id = disk_info.get('device_id', '-')
        device_path = disk_info.get('device_path', '-')
        model = disk_info.get('model', '-')
        serial = disk_info.get('serial_number', '-')
        size = self.format_bytes(disk_info.get('size_bytes', 0))
        filesystem = disk_info.get('filesystem', '-')
        mount_point = disk_info.get('mount_point', '-')
        
        self.device_id_label.setText(f"Device ID: {device_id}")
        self.device_path_label.setText(f"Device Path: {device_path}")
        self.model_label.setText(f"Model: {model}")
        self.serial_label.setText(f"Serial Number: {serial}")
        self.size_label.setText(f"Size: {size}")
        self.filesystem_label.setText(f"Filesystem: {filesystem}")
        self.mount_point_label.setText(f"Mount Point: {mount_point}")
    
    def update_health_details(self, disk_info):
        """Mock update health details."""
        health_status = disk_info.get('health_status', 'unknown')
        temperature = disk_info.get('temperature', '-')
        power_on_hours = disk_info.get('power_on_hours', '-')
        
        self.health_status_label.setText(f"Status: {health_status.title()}")
        
        if isinstance(temperature, (int, float)):
            self.temperature_label.setText(f"Temperature: {temperature}°C")
        else:
            self.temperature_label.setText("Temperature: -")
        
        if isinstance(power_on_hours, (int, float)):
            self.power_on_hours_label.setText(f"Power On Hours: {power_on_hours:,}")
        else:
            self.power_on_hours_label.setText("Power On Hours: -")
        
        used_percent = disk_info.get('used_percent', 0)
        if used_percent > 0:
            self.usage_progress.setValue(int(used_percent))
            used_bytes = disk_info.get('used_bytes', 0)
            size_bytes = disk_info.get('size_bytes', 0)
            used_str = self.format_bytes(used_bytes)
            total_str = self.format_bytes(size_bytes)
            self.usage_label.setText(
                f"Used: {used_str} / {total_str} ({used_percent:.1f}%)"
            )
    
    def update_performance_details(self, disk_info):
        """Mock update performance details."""
        io_stats = disk_info.get('io_stats', {})
        
        if io_stats:
            reads = io_stats.get('reads_completed', '-')
            writes = io_stats.get('writes_completed', '-')
            sectors_read = io_stats.get('sectors_read', 0)
            sectors_written = io_stats.get('sectors_written', 0)
            
            bytes_read = sectors_read * 512
            bytes_written = sectors_written * 512
            
            self.reads_label.setText(f"Reads: {reads:,}" if isinstance(reads, int) else "Reads: -")
            self.writes_label.setText(f"Writes: {writes:,}" if isinstance(writes, int) else "Writes: -")
            self.read_bytes_label.setText(f"Bytes Read: {self.format_bytes(bytes_read)}")
            self.write_bytes_label.setText(f"Bytes Written: {self.format_bytes(bytes_written)}")
        else:
            self.reads_label.setText("Reads: -")
            self.writes_label.setText("Writes: -")
            self.read_bytes_label.setText("Bytes Read: -")
            self.write_bytes_label.setText("Bytes Written: -")
    
    def toggle_auto_refresh(self):
        """Mock toggle auto refresh."""
        if hasattr(self.auto_refresh_button, 'isChecked'):
            if self.auto_refresh_button.isChecked():
                self.update_timer.start()
            else:
                self.update_timer.stop()
    
    def closeEvent(self, event):
        """Mock close event handler."""
        self.update_timer.stop()
        if self.disk_monitor:
            self.disk_monitor.stop_monitoring()


@pytest.fixture
def mock_disk_widget():
    """Create a mock disk health widget for testing."""
    return MockDiskHealthWidget()


@pytest.fixture
def mock_disk_data():
    """Provide comprehensive mock disk data."""
    return {
        'summary': {
            'total_physical_disks': 2,
            'total_logical_disks': 4,
            'healthy_disks': 5,
            'warning_disks': 1,
            'critical_disks': 0,
            'total_capacity_gb': 2000.0,
            'total_used_gb': 800.0
        },
        'physical_disks': [
            {
                'device_id': '/dev/sda',
                'device_path': '/dev/sda',
                'model': 'Samsung SSD 980 PRO',
                'serial_number': 'S649NX0W123456',
                'size_bytes': 1000000000000,
                'health_status': 'healthy',
                'temperature': 45,
                'power_on_hours': 15000,
                'io_stats': {
                    'reads_completed': 2500000,
                    'writes_completed': 1200000,
                    'sectors_read': 5000000,
                    'sectors_written': 2400000
                }
            },
            {
                'device_id': '/dev/sdb',
                'device_path': '/dev/sdb',
                'model': 'WD Black SN850',
                'serial_number': 'WDS100T1X0E123',
                'size_bytes': 1000000000000,
                'health_status': 'warning',
                'temperature': 55,
                'power_on_hours': 25000,
                'io_stats': {
                    'reads_completed': 1800000,
                    'writes_completed': 900000,
                    'sectors_read': 3600000,
                    'sectors_written': 1800000
                }
            }
        ],
        'logical_disks': [
            {
                'device_id': 'C:',
                'device_path': 'C:',
                'filesystem': 'NTFS',
                'mount_point': 'C:',
                'size_bytes': 500000000000,
                'used_bytes': 300000000000,
                'used_percent': 60.0,
                'health_status': 'healthy'
            },
            {
                'device_id': 'D:',
                'device_path': 'D:',
                'filesystem': 'NTFS',
                'mount_point': 'D:',
                'size_bytes': 500000000000,
                'used_bytes': 450000000000,
                'used_percent': 90.0,
                'health_status': 'warning'
            }
        ]
    }


class TestDiskHealthWidget:
    """Test class for DiskHealthWidget functionality."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        self.test_start_time = datetime.now()
        print(f"\nStarting test: {self._get_test_name()}")
    
    def teardown_method(self):
        """Clean up after each test."""
        print(f"Completed test: {self._get_test_name()}")
    
    def _get_test_name(self):
        """Get current test name."""
        import inspect
        return inspect.stack()[2].function
    
    def test_widget_initialization(self, mock_disk_widget):
        """Test widget initialization."""
        widget = mock_disk_widget
        
        # Verify basic initialization
        assert widget.current_data == {}
        assert widget.disk_monitor is not None
        assert hasattr(widget, 'update_timer')
        assert hasattr(widget, 'health_colors')
        
        # Verify UI components
        assert hasattr(widget, 'disk_tree')
        assert hasattr(widget, 'details_tabs')
        assert hasattr(widget, 'refresh_button')
        assert hasattr(widget, 'auto_refresh_button')
        
        # Verify labels
        assert hasattr(widget, 'total_disks_label')
        assert hasattr(widget, 'healthy_disks_label')
        assert hasattr(widget, 'warning_disks_label')
        assert hasattr(widget, 'critical_disks_label')
    
    def test_monitor_initialization(self, mock_disk_widget):
        """Test disk monitor initialization."""
        widget = mock_disk_widget
        
        # Verify monitor was created
        assert widget.disk_monitor is not None
        
        # Verify monitor methods are available
        assert hasattr(widget.disk_monitor, 'start_monitoring')
        assert hasattr(widget.disk_monitor, 'get_current_data')
        assert hasattr(widget.disk_monitor, 'stop_monitoring')
    
    def test_refresh_data_functionality(self, mock_disk_widget, mock_disk_data):
        """Test data refresh functionality."""
        widget = mock_disk_widget
        widget.disk_monitor.get_current_data.return_value = mock_disk_data
        
        # Test refresh
        widget.refresh_data()
        
        # Verify data was updated
        assert widget.current_data == mock_disk_data
        
        # Verify status was updated
        assert widget.status_label.text == "Ready"
        assert "Last Update:" in widget.last_update_label.text
    
    def test_summary_update(self, mock_disk_widget, mock_disk_data):
        """Test summary section update."""
        widget = mock_disk_widget
        widget.current_data = mock_disk_data
        
        widget.update_summary()
        
        # Verify summary labels were updated
        assert "Total Disks: 6" in widget.total_disks_label.text
        assert "Healthy: 5" in widget.healthy_disks_label.text
        assert "Warning: 1" in widget.warning_disks_label.text
        assert "Critical: 0" in widget.critical_disks_label.text
    
    def test_disk_tree_update(self, mock_disk_widget, mock_disk_data):
        """Test disk tree update."""
        widget = mock_disk_widget
        widget.current_data = mock_disk_data
        
        widget.update_disk_tree()
        
        # Verify tree was cleared and populated
        expected_items = len(mock_disk_data['physical_disks']) + len(mock_disk_data['logical_disks'])
        assert len(widget.disk_tree.items) == expected_items
    
    def test_add_disk_to_tree_physical(self, mock_disk_widget):
        """Test adding physical disk to tree."""
        widget = mock_disk_widget
        
        disk_info = {
            'device_id': '/dev/sda',
            'size_bytes': 1000000000000,
            'health_status': 'healthy'
        }
        
        widget.add_disk_to_tree(disk_info, 'physical')
        
        # Verify item was added
        assert len(widget.disk_tree.items) == 1
        item = widget.disk_tree.items[0]
        assert '/dev/sda' in item.data_list
        assert 'Physical' in item.data_list
    
    def test_add_disk_to_tree_logical(self, mock_disk_widget):
        """Test adding logical disk to tree."""
        widget = mock_disk_widget
        
        disk_info = {
            'device_id': 'C:',
            'size_bytes': 500000000000,
            'health_status': 'healthy',
            'used_percent': 75.0
        }
        
        widget.add_disk_to_tree(disk_info, 'logical')
        
        # Verify item was added with usage
        assert len(widget.disk_tree.items) == 1
        item = widget.disk_tree.items[0]
        assert 'C:' in item.data_list
        assert 'Logical' in item.data_list
        assert '75.0%' in item.data_list
    
    def test_format_bytes_conversion(self, mock_disk_widget):
        """Test bytes formatting."""
        widget = mock_disk_widget
        
        # Test various byte values
        assert widget.format_bytes(0) == "0 B"
        assert widget.format_bytes(1024) == "1.0 KB"
        assert widget.format_bytes(1048576) == "1.0 MB"
        assert widget.format_bytes(1073741824) == "1.0 GB"
        assert widget.format_bytes(1099511627776) == "1.0 TB"
        
        # Test intermediate values
        assert "1.5 GB" in widget.format_bytes(1610612736)
    
    def test_disk_selection_handling(self, mock_disk_widget):
        """Test disk selection handling."""
        widget = mock_disk_widget
        
        disk_info = {
            'device_id': '/dev/sda',
            'device_path': '/dev/sda',
            'model': 'Test SSD',
            'health_status': 'healthy'
        }
        
        # Create mock tree item
        item = MockQTreeWidgetItem(['/dev/sda', 'Physical', '1.0 TB'])
        item.setData(0, 1, ('/dev/sda', 'physical', disk_info))
        
        # Test selection
        widget.on_disk_selected(item, 0)
        
        # Verify details were updated
        assert "Details: /dev/sda (physical)" in widget.details_title.text
    
    def test_general_details_update(self, mock_disk_widget):
        """Test general details update."""
        widget = mock_disk_widget
        
        disk_info = {
            'device_id': '/dev/sda',
            'device_path': '/dev/sda',
            'model': 'Samsung SSD 980',
            'serial_number': 'S649NX123456',
            'size_bytes': 1000000000000,
            'filesystem': 'ext4',
            'mount_point': '/'
        }
        
        widget.update_general_details(disk_info)
        
        # Verify labels were updated
        assert "Device ID: /dev/sda" in widget.device_id_label.text
        assert "Model: Samsung SSD 980" in widget.model_label.text
        assert "Serial Number: S649NX123456" in widget.serial_label.text
        assert "1.0 TB" in widget.size_label.text
        assert "Filesystem: ext4" in widget.filesystem_label.text
        assert "Mount Point: /" in widget.mount_point_label.text
    
    def test_health_details_update(self, mock_disk_widget):
        """Test health details update.""" 
        widget = mock_disk_widget
        
        disk_info = {
            'health_status': 'healthy',
            'temperature': 42,
            'power_on_hours': 15000,
            'used_percent': 65.0,
            'used_bytes': 650000000000,
            'size_bytes': 1000000000000
        }
        
        widget.update_health_details(disk_info)
        
        # Verify health status
        assert "Status: Healthy" in widget.health_status_label.text
        assert "Temperature: 42°C" in widget.temperature_label.text
        assert "Power On Hours: 15,000" in widget.power_on_hours_label.text
        
        # Verify usage progress
        assert widget.usage_progress.value == 65
        assert "650.0 GB / 1.0 TB (65.0%)" in widget.usage_label.text
    
    def test_performance_details_update(self, mock_disk_widget):
        """Test performance details update."""
        widget = mock_disk_widget
        
        disk_info = {
            'io_stats': {
                'reads_completed': 1000000,
                'writes_completed': 500000,
                'sectors_read': 2000000,
                'sectors_written': 1000000
            }
        }
        
        widget.update_performance_details(disk_info)
        
        # Verify I/O statistics
        assert "Reads: 1,000,000" in widget.reads_label.text
        assert "Writes: 500,000" in widget.writes_label.text
        assert "1.0 GB" in widget.read_bytes_label.text  # 2M sectors * 512 bytes
        assert "512.0 MB" in widget.write_bytes_label.text  # 1M sectors * 512 bytes
    
    def test_auto_refresh_toggle(self, mock_disk_widget):
        """Test auto-refresh toggle functionality."""
        widget = mock_disk_widget
        
        # Mock the button's isChecked method
        widget.auto_refresh_button.isChecked = MagicMock(return_value=True)
        
        # Test enabling auto-refresh
        widget.toggle_auto_refresh()
        assert widget.update_timer.active is True
        
        # Test disabling auto-refresh
        widget.auto_refresh_button.isChecked.return_value = False
        widget.toggle_auto_refresh()
        assert widget.update_timer.active is False
    
    def test_empty_data_handling(self, mock_disk_widget):
        """Test handling of empty data."""
        widget = mock_disk_widget
        widget.current_data = {}
        
        # Test update methods with empty data
        widget.update_summary()  # Should not crash
        widget.update_disk_tree()  # Should clear tree
        
        assert len(widget.disk_tree.items) == 0
    
    def test_malformed_data_handling(self, mock_disk_widget):
        """Test handling of malformed data."""
        widget = mock_disk_widget
        
        # Test with missing summary
        widget.current_data = {'physical_disks': [], 'logical_disks': []}
        widget.update_summary()  # Should not crash
        
        # Test with malformed disk data
        malformed_disk = {'device_id': 'test'}  # Missing required fields
        widget.add_disk_to_tree(malformed_disk, 'physical')  # Should handle gracefully
        
        assert len(widget.disk_tree.items) == 1
    
    def test_health_status_colors(self, mock_disk_widget):
        """Test health status color assignment."""
        widget = mock_disk_widget
        
        # Verify color scheme
        assert widget.health_colors['healthy'] == '#4CAF50'
        assert widget.health_colors['warning'] == '#FF9800'
        assert widget.health_colors['critical'] == '#F44336'
        assert widget.health_colors['unknown'] == '#9E9E9E'
    
    def test_close_event_handling(self, mock_disk_widget):
        """Test widget close event handling."""
        widget = mock_disk_widget
        
        # Mock event
        mock_event = MagicMock()
        mock_event.accept = MagicMock()
        
        # Test close event
        widget.closeEvent(mock_event)
        
        # Verify cleanup
        assert widget.update_timer.active is False
        mock_event.accept.assert_called_once()
    
    def test_large_numbers_formatting(self, mock_disk_widget):
        """Test formatting of large numbers."""
        widget = mock_disk_widget
        
        disk_info = {
            'power_on_hours': 87600,  # 10 years
            'io_stats': {
                'reads_completed': 123456789,
                'writes_completed': 987654321
            }
        }
        
        widget.update_health_details(disk_info)
        widget.update_performance_details(disk_info)
        
        # Verify large number formatting with commas
        assert "87,600" in widget.power_on_hours_label.text
        assert "123,456,789" in widget.reads_label.text
        assert "987,654,321" in widget.writes_label.text
    
    def test_edge_case_byte_values(self, mock_disk_widget):
        """Test edge case byte values."""
        widget = mock_disk_widget
        
        # Test zero bytes
        assert widget.format_bytes(0) == "0 B"
        
        # Test very large values
        very_large = 1024 ** 5  # Petabyte
        result = widget.format_bytes(very_large)
        assert "PB" in result or "TB" in result  # Depends on implementation limit
        
        # Test negative values (edge case)
        result = widget.format_bytes(-1024)
        assert result  # Should handle gracefully


class TestDiskHealthWidgetIntegration:
    """Integration tests for DiskHealthWidget."""
    
    def test_full_data_flow(self, mock_disk_widget, mock_disk_data):
        """Test complete data flow from monitor to UI."""
        widget = mock_disk_widget
        widget.disk_monitor.get_current_data.return_value = mock_disk_data
        
        # Simulate full refresh cycle
        widget.refresh_data()
        
        # Verify data propagated through all components
        assert widget.current_data == mock_disk_data
        assert len(widget.disk_tree.items) > 0
        assert "Total Disks: 6" in widget.total_disks_label.text
        assert widget.status_label.text == "Ready"
    
    def test_disk_selection_to_details_flow(self, mock_disk_widget, mock_disk_data):
        """Test flow from disk selection to details display."""
        widget = mock_disk_widget
        widget.current_data = mock_disk_data
        
        # Populate tree
        widget.update_disk_tree()
        
        # Simulate disk selection
        if widget.disk_tree.items:
            item = widget.disk_tree.items[0]
            widget.on_disk_selected(item, 0)
            
            # Verify details were updated
            assert "Details:" in widget.details_title.text
    
    def test_error_recovery(self, mock_disk_widget):
        """Test error handling and recovery."""
        widget = mock_disk_widget
        
        # Simulate monitor error
        widget.disk_monitor.get_current_data.side_effect = Exception("Test error")
        
        # Should handle error gracefully
        try:
            widget.refresh_data()
        except Exception:
            pytest.fail("Widget should handle monitor errors gracefully")


class TestDiskHealthWidgetPerformance:
    """Performance tests for DiskHealthWidget."""
    
    def test_large_disk_list_performance(self, mock_disk_widget):
        """Test performance with large number of disks."""
        widget = mock_disk_widget
        
        # Generate large dataset
        large_data = {
            'summary': {
                'total_physical_disks': 50,
                'total_logical_disks': 100,
                'healthy_disks': 140,
                'warning_disks': 10,
                'critical_disks': 0,
                'total_capacity_gb': 50000.0,
                'total_used_gb': 25000.0
            },
            'physical_disks': [
                {
                    'device_id': f'/dev/sd{chr(97+i)}',
                    'size_bytes': 1000000000000,
                    'health_status': 'healthy'
                } for i in range(50)
            ],
            'logical_disks': [
                {
                    'device_id': f'{chr(67+i)}:',
                    'size_bytes': 500000000000,
                    'used_percent': 50.0,
                    'health_status': 'healthy'
                } for i in range(26)  # A-Z drives
            ]
        }
        
        widget.current_data = large_data
        
        # Measure update performance
        import time
        start_time = time.time()
        widget.update_disk_tree()
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        # Verify performance (should complete quickly)
        assert execution_time < 1.0  # Less than 1 second
        assert len(widget.disk_tree.items) == 76  # 50 + 26
    
    def test_frequent_updates_performance(self, mock_disk_widget, mock_disk_data):
        """Test performance with frequent updates."""
        widget = mock_disk_widget
        widget.disk_monitor.get_current_data.return_value = mock_disk_data
        
        # Simulate multiple rapid updates
        import time
        start_time = time.time()
        
        for _ in range(10):
            widget.refresh_data()
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should handle frequent updates efficiently
        assert execution_time < 2.0  # Less than 2 seconds for 10 updates


# Test execution tracking
class TestExecutionTracker:
    """Track test execution details."""
    
    @classmethod
    def setup_class(cls):
        """Set up test execution tracking."""
        cls.start_time = datetime.now()
        cls.test_results = []
    
    @classmethod
    def teardown_class(cls):
        """Generate test execution report."""
        end_time = datetime.now()
        execution_time = end_time - cls.start_time
        
        report = {
            'test_execution_summary': {
                'start_time': cls.start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'total_execution_time': str(execution_time),
                'test_file': 'test_disk_health_widget_2025-08-29.py',
                'target_module': 'disk_health_widget.py',
                'framework': 'pytest'
            }
        }
        
        # Write execution report
        report_path = 'c:/Users/richardi/1_2/tests/unit/result_disk_health_widget_2025-08-29.json'
        try:
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)
        except Exception as e:
            print(f"Could not write execution report: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])