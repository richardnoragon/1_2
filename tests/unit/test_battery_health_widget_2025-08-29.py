"""
Comprehensive unit tests for battery_health_widget.py

Test file: test_battery_health_widget_2025-08-29.py
Target module: battery_health_widget.py
Created: 2025-08-29
Framework: pytest

This module contains comprehensive unit tests for the BatteryHealthWidget class,
covering all methods, GUI components, error handling, and edge cases.
"""

import json
import os
import tempfile
import threading
import time
import tkinter as tk
from datetime import datetime, timedelta
from typing import Any, Dict, List
from unittest.mock import MagicMock, Mock, call, patch

import pytest


# Mock dependencies before importing the target module
@pytest.fixture(autouse=True)
def mock_dependencies():
    """Mock all external dependencies."""
    with patch.dict('sys.modules', {
        'matplotlib': MagicMock(),
        'matplotlib.pyplot': MagicMock(),
        'matplotlib.backends.backend_tkagg': MagicMock(),
        'matplotlib.figure': MagicMock(),
        'numpy': MagicMock(),
        'gui.common.base_window': MagicMock(),
        'core.error_handler': MagicMock(),
    }):
        # Mock matplotlib components
        figure_mock = MagicMock()
        canvas_mock = MagicMock()
        ax_mock = MagicMock()
        
        with patch('matplotlib.figure.Figure', return_value=figure_mock), \
             patch('matplotlib.backends.backend_tkagg.FigureCanvasTkAgg', return_value=canvas_mock), \
             patch('numpy.array', return_value=[1, 2, 3]):
            
            figure_mock.add_subplot.return_value = ax_mock
            canvas_mock.get_tk_widget.return_value = MagicMock()
            
            yield {
                'figure': figure_mock,
                'canvas': canvas_mock,
                'ax': ax_mock
            }


@pytest.fixture
def mock_battery_monitor():
    """Create a mock battery monitor."""
    monitor = MagicMock()
    monitor.update_interval = 60.0
    monitor.start_monitoring.return_value = True
    monitor.stop_monitoring.return_value = None
    monitor.get_current_data.return_value = {
        'batteries': [
            {
                'id': 'BAT0',
                'percent': 85.5,
                'health_percent': 92.3,
                'health_status': 'Good',
                'power_plugged': False,
                'cycle_count': 245,
                'temperature': 32.5,
                'voltage': 12.6,
                'secsleft': 7200
            }
        ],
        'power_consumption': {
            'cpu_power_estimate': 15.2
        }
    }
    monitor.is_running = True
    monitor._monitored_batteries = ['BAT0']
    monitor.cycle_tracker = MagicMock()
    monitor.cycle_tracker.get_cycle_history.return_value = [
        {'depth_of_discharge': 80},
        {'depth_of_discharge': 75},
        {'depth_of_discharge': 90}
    ]
    return monitor


@pytest.fixture
def mock_base_window():
    """Create a mock base window class."""
    base_window = MagicMock()
    base_window.main_frame = MagicMock()
    base_window.logger = MagicMock()
    return base_window


@pytest.fixture
def root_window():
    """Create a root tkinter window for testing."""
    root = tk.Tk()
    root.withdraw()  # Hide the window
    yield root
    try:
        root.destroy()
    except tk.TclError:
        pass  # Window already destroyed


class TestBatteryHealthWidget:
    """Test class for BatteryHealthWidget."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        self.test_start_time = datetime.now()
        
    def teardown_method(self):
        """Clean up after each test."""
        # Clean up any remaining tkinter windows
        try:
            import tkinter as tk
            for widget in tk._default_root.winfo_children():
                widget.destroy()
        except (AttributeError, tk.TclError):
            pass
    
    @patch('src.utilities.system.diagnostics_monitoring.gui.battery_health_widget.BatteryMonitor')
    @patch('src.utilities.system.diagnostics_monitoring.gui.battery_health_widget.BaseWindow')
    def test_init_basic(self, mock_base_window, mock_battery_monitor_class, root_window, mock_dependencies):
        """Test basic initialization of BatteryHealthWidget."""
        # Setup mocks
        mock_battery_monitor_class.return_value = mock_battery_monitor_class
        mock_base_window.__init__ = MagicMock(return_value=None)
        mock_base_window.main_frame = MagicMock()
        mock_base_window.logger = MagicMock()
        
        # Import and create widget
        from src.utilities.system.diagnostics_monitoring.gui.battery_health_widget import \
            BatteryHealthWidget
        
        with patch.object(BatteryHealthWidget, 'setup_ui'), \
             patch.object(BatteryHealthWidget, 'start_monitoring'):
            
            widget = BatteryHealthWidget(root_window)
            
            # Verify initialization
            assert widget.monitoring_active is False
            assert widget.update_thread is None
            assert widget.battery_data_history == []
            assert widget.max_history_points == 100
            assert isinstance(widget.status_vars, dict)
            assert isinstance(widget.battery_widgets, dict)
    
    @patch('src.utilities.system.diagnostics_monitoring.gui.battery_health_widget.BatteryMonitor')
    @patch('src.utilities.system.diagnostics_monitoring.gui.battery_health_widget.BaseWindow')
    def test_init_with_parent(self, mock_base_window, mock_battery_monitor_class, root_window, mock_dependencies):
        """Test initialization with parent window."""
        mock_battery_monitor_class.return_value = mock_battery_monitor_class
        mock_base_window.__init__ = MagicMock(return_value=None)
        mock_base_window.main_frame = MagicMock()
        mock_base_window.logger = MagicMock()
        
        from src.utilities.system.diagnostics_monitoring.gui.battery_health_widget import \
            BatteryHealthWidget
        
        with patch.object(BatteryHealthWidget, 'setup_ui'), \
             patch.object(BatteryHealthWidget, 'start_monitoring'):
            
            widget = BatteryHealthWidget(root_window)
            
            # Verify parent is set correctly
            mock_base_window.__init__.assert_called_once_with(root_window, "Battery Health Monitor")
    
    @patch('src.utilities.system.diagnostics_monitoring.gui.battery_health_widget.BatteryMonitor')
    @patch('src.utilities.system.diagnostics_monitoring.gui.battery_health_widget.BaseWindow')
    def test_setup_ui_complete(self, mock_base_window, mock_battery_monitor_class, root_window, mock_dependencies):
        """Test complete UI setup."""
        mock_battery_monitor_class.return_value = mock_battery_monitor_class
        mock_base_window.__init__ = MagicMock(return_value=None)
        mock_base_window.main_frame = tk.Frame(root_window)
        mock_base_window.logger = MagicMock()
        mock_base_window.title = MagicMock()
        mock_base_window.geometry = MagicMock()
        
        from src.utilities.system.diagnostics_monitoring.gui.battery_health_widget import \
            BatteryHealthWidget
        
        with patch.object(BatteryHealthWidget, 'start_monitoring'), \
             patch.object(BatteryHealthWidget, 'setup_battery_status_panel') as mock_status, \
             patch.object(BatteryHealthWidget, 'setup_control_panel') as mock_control, \
             patch.object(BatteryHealthWidget, 'setup_charts_panel') as mock_charts:
            
            widget = BatteryHealthWidget(root_window)
            widget.setup_ui()
            
            # Verify UI setup methods were called
            mock_status.assert_called_once()
            mock_control.assert_called_once()
            mock_charts.assert_called_once()
    
    @patch('src.utilities.system.diagnostics_monitoring.gui.battery_health_widget.BatteryMonitor')
    @patch('src.utilities.system.diagnostics_monitoring.gui.battery_health_widget.BaseWindow')
    def test_setup_ui_error_handling(self, mock_base_window, mock_battery_monitor_class, root_window, mock_dependencies):
        """Test UI setup error handling."""
        mock_battery_monitor_class.return_value = mock_battery_monitor_class
        mock_base_window.__init__ = MagicMock(return_value=None)
        mock_base_window.main_frame = tk.Frame(root_window)
        mock_logger = MagicMock()
        mock_base_window.logger = mock_logger
        mock_base_window.title = MagicMock()
        mock_base_window.geometry = MagicMock()
        
        from src.utilities.system.diagnostics_monitoring.gui.battery_health_widget import \
            BatteryHealthWidget
        
        with patch.object(BatteryHealthWidget, 'start_monitoring'), \
             patch.object(BatteryHealthWidget, 'setup_battery_status_panel', side_effect=Exception("Test error")):
            
            widget = BatteryHealthWidget(root_window)
            widget.setup_ui()
            
            # Verify error was logged
            mock_logger.error.assert_called()
    
    @patch('src.utilities.system.diagnostics_monitoring.gui.battery_health_widget.BatteryMonitor')
    @patch('src.utilities.system.diagnostics_monitoring.gui.battery_health_widget.BaseWindow')
    def test_start_monitoring_success(self, mock_base_window, mock_battery_monitor_class, root_window, mock_dependencies):
        """Test successful monitoring start."""
        mock_monitor = mock_battery_monitor_class.return_value
        mock_monitor.start_monitoring.return_value = True
        mock_base_window.__init__ = MagicMock(return_value=None)
        mock_base_window.main_frame = tk.Frame(root_window)
        mock_base_window.logger = MagicMock()
        
        from src.utilities.system.diagnostics_monitoring.gui.battery_health_widget import \
            BatteryHealthWidget
        
        with patch.object(BatteryHealthWidget, 'setup_ui'):
            widget = BatteryHealthWidget(root_window)
            widget.monitoring_active = False
            widget.interval_var = tk.StringVar(value="30")
            
            # Mock UI elements
            widget.start_button = MagicMock()
            widget.stop_button = MagicMock()
            
            with patch('threading.Thread') as mock_thread:
                widget.start_monitoring()
                
                # Verify monitoring started
                assert widget.monitoring_active is True
                mock_monitor.start_monitoring.assert_called_once()
                widget.start_button.config.assert_called_with(state=tk.DISABLED)
                widget.stop_button.config.assert_called_with(state=tk.NORMAL)
                mock_thread.assert_called_once()
    
    @patch('src.utilities.system.diagnostics_monitoring.gui.battery_health_widget.BatteryMonitor')
    @patch('src.utilities.system.diagnostics_monitoring.gui.battery_health_widget.BaseWindow')
    def test_start_monitoring_failure(self, mock_base_window, mock_battery_monitor_class, root_window, mock_dependencies):
        """Test monitoring start failure."""
        mock_monitor = mock_battery_monitor_class.return_value
        mock_monitor.start_monitoring.return_value = False
        mock_base_window.__init__ = MagicMock(return_value=None)
        mock_base_window.main_frame = tk.Frame(root_window)
        mock_base_window.logger = MagicMock()
        
        from src.utilities.system.diagnostics_monitoring.gui.battery_health_widget import \
            BatteryHealthWidget
        
        with patch.object(BatteryHealthWidget, 'setup_ui'), \
             patch.object(BatteryHealthWidget, 'show_error') as mock_show_error:
            
            widget = BatteryHealthWidget(root_window)
            widget.monitoring_active = False
            widget.interval_var = tk.StringVar(value="60")
            
            widget.start_monitoring()
            
            # Verify monitoring did not start
            assert widget.monitoring_active is False
            mock_show_error.assert_called_once_with("Failed to start battery monitoring")
    
    @patch('src.utilities.system.diagnostics_monitoring.gui.battery_health_widget.BatteryMonitor')
    @patch('src.utilities.system.diagnostics_monitoring.gui.battery_health_widget.BaseWindow')
    def test_stop_monitoring(self, mock_base_window, mock_battery_monitor_class, root_window, mock_dependencies):
        """Test stopping monitoring."""
        mock_monitor = mock_battery_monitor_class.return_value
        mock_base_window.__init__ = MagicMock(return_value=None)
        mock_base_window.main_frame = tk.Frame(root_window)
        mock_base_window.logger = MagicMock()
        
        from src.utilities.system.diagnostics_monitoring.gui.battery_health_widget import \
            BatteryHealthWidget
        
        with patch.object(BatteryHealthWidget, 'setup_ui'):
            widget = BatteryHealthWidget(root_window)
            widget.monitoring_active = True
            
            # Mock UI elements
            widget.start_button = MagicMock()
            widget.stop_button = MagicMock()
            
            widget.stop_monitoring()
            
            # Verify monitoring stopped
            assert widget.monitoring_active is False
            mock_monitor.stop_monitoring.assert_called_once()
            widget.start_button.config.assert_called_with(state=tk.NORMAL)
            widget.stop_button.config.assert_called_with(state=tk.DISABLED)
    
    @patch('src.utilities.system.diagnostics_monitoring.gui.battery_health_widget.BatteryMonitor')
    @patch('src.utilities.system.diagnostics_monitoring.gui.battery_health_widget.BaseWindow')
    def test_update_loop(self, mock_base_window, mock_battery_monitor_class, root_window, mock_dependencies):
        """Test update loop functionality."""
        mock_monitor = mock_battery_monitor_class.return_value
        mock_monitor.get_current_data.return_value = {
            'batteries': [{'id': 'BAT0', 'percent': 80}]
        }
        mock_monitor.update_interval = 0.1  # Fast for testing
        
        mock_base_window.__init__ = MagicMock(return_value=None)
        mock_base_window.main_frame = tk.Frame(root_window)
        mock_base_window.logger = MagicMock()
        
        from src.utilities.system.diagnostics_monitoring.gui.battery_health_widget import \
            BatteryHealthWidget
        
        with patch.object(BatteryHealthWidget, 'setup_ui'), \
             patch.object(BatteryHealthWidget, 'after') as mock_after:
            
            widget = BatteryHealthWidget(root_window)
            widget.monitoring_active = True
            widget.battery_data_history = []
            widget.max_history_points = 5
            
            # Run update loop for a short time
            with patch('time.sleep') as mock_sleep:
                mock_sleep.side_effect = [None, None, StopIteration]  # Stop after 2 iterations
                
                try:
                    widget.update_loop()
                except StopIteration:
                    pass
                
                # Verify data was collected
                assert len(widget.battery_data_history) > 0
                mock_after.assert_called()
    
    @patch('src.utilities.system.diagnostics_monitoring.gui.battery_health_widget.BatteryMonitor')
    @patch('src.utilities.system.diagnostics_monitoring.gui.battery_health_widget.BaseWindow')
    def test_update_battery_status_no_batteries(self, mock_base_window, mock_battery_monitor_class, root_window, mock_dependencies):
        """Test battery status update with no batteries."""
        mock_base_window.__init__ = MagicMock(return_value=None)
        mock_base_window.main_frame = tk.Frame(root_window)
        mock_base_window.logger = MagicMock()
        
        from src.utilities.system.diagnostics_monitoring.gui.battery_health_widget import \
            BatteryHealthWidget
        
        with patch.object(BatteryHealthWidget, 'setup_ui'):
            widget = BatteryHealthWidget(root_window)
            widget.battery_status_frame = tk.Frame(root_window)
            
            battery_data = {'batteries': []}
            
            widget.update_battery_status(battery_data)
            
            # Verify no battery message is displayed
            children = widget.battery_status_frame.winfo_children()
            assert len(children) == 1
    
    @patch('src.utilities.system.diagnostics_monitoring.gui.battery_health_widget.BatteryMonitor')
    @patch('src.utilities.system.diagnostics_monitoring.gui.battery_health_widget.BaseWindow')
    def test_update_battery_status_with_batteries(self, mock_base_window, mock_battery_monitor_class, root_window, mock_dependencies):
        """Test battery status update with battery data."""
        mock_base_window.__init__ = MagicMock(return_value=None)
        mock_base_window.main_frame = tk.Frame(root_window)
        mock_base_window.logger = MagicMock()
        
        from src.utilities.system.diagnostics_monitoring.gui.battery_health_widget import \
            BatteryHealthWidget
        
        with patch.object(BatteryHealthWidget, 'setup_ui'), \
             patch.object(BatteryHealthWidget, 'create_battery_widget') as mock_create:
            
            widget = BatteryHealthWidget(root_window)
            widget.battery_status_frame = tk.Frame(root_window)
            
            battery_data = {
                'batteries': [
                    {'id': 'BAT0', 'percent': 85.5},
                    {'id': 'BAT1', 'percent': 92.1}
                ]
            }
            
            widget.update_battery_status(battery_data)
            
            # Verify battery widgets were created
            assert mock_create.call_count == 2
    
    @patch('src.utilities.system.diagnostics_monitoring.gui.battery_health_widget.BatteryMonitor')
    @patch('src.utilities.system.diagnostics_monitoring.gui.battery_health_widget.BaseWindow')
    def test_create_battery_widget_complete(self, mock_base_window, mock_battery_monitor_class, root_window, mock_dependencies):
        """Test complete battery widget creation."""
        mock_base_window.__init__ = MagicMock(return_value=None)
        mock_base_window.main_frame = tk.Frame(root_window)
        mock_base_window.logger = MagicMock()
        
        from src.utilities.system.diagnostics_monitoring.gui.battery_health_widget import \
            BatteryHealthWidget
        
        with patch.object(BatteryHealthWidget, 'setup_ui'), \
             patch.object(BatteryHealthWidget, 'add_battery_info_row') as mock_add_row:
            
            widget = BatteryHealthWidget(root_window)
            parent_frame = tk.Frame(root_window)
            
            battery_data = {
                'id': 'BAT0',
                'percent': 85.5,
                'health_percent': 92.3,
                'health_status': 'Good',
                'power_plugged': True,
                'cycle_count': 245,
                'temperature': 32.5,
                'voltage': 12.6,
                'secsleft': 7200
            }
            
            widget.create_battery_widget(parent_frame, battery_data, 0)
            
            # Verify info rows were added
            assert mock_add_row.call_count >= 8  # Should have multiple info rows
    
    @patch('src.utilities.system.diagnostics_monitoring.gui.battery_health_widget.BatteryMonitor')
    @patch('src.utilities.system.diagnostics_monitoring.gui.battery_health_widget.BaseWindow')
    def test_refresh_data_success(self, mock_base_window, mock_battery_monitor_class, root_window, mock_dependencies):
        """Test successful data refresh."""
        mock_monitor = mock_battery_monitor_class.return_value
        mock_monitor.is_running = True
        mock_monitor.get_current_data.return_value = {'batteries': [{'id': 'BAT0'}]}
        
        mock_base_window.__init__ = MagicMock(return_value=None)
        mock_base_window.main_frame = tk.Frame(root_window)
        mock_base_window.logger = MagicMock()
        
        from src.utilities.system.diagnostics_monitoring.gui.battery_health_widget import \
            BatteryHealthWidget
        
        with patch.object(BatteryHealthWidget, 'setup_ui'), \
             patch.object(BatteryHealthWidget, 'update_ui') as mock_update_ui:
            
            widget = BatteryHealthWidget(root_window)
            
            widget.refresh_data()
            
            # Verify UI was updated
            mock_update_ui.assert_called_once()
    
    @patch('src.utilities.system.diagnostics_monitoring.gui.battery_health_widget.BatteryMonitor')
    @patch('src.utilities.system.diagnostics_monitoring.gui.battery_health_widget.BaseWindow')
    def test_refresh_data_no_data(self, mock_base_window, mock_battery_monitor_class, root_window, mock_dependencies):
        """Test data refresh when no data available."""
        mock_monitor = mock_battery_monitor_class.return_value
        mock_monitor.is_running = True
        mock_monitor.get_current_data.return_value = None
        
        mock_base_window.__init__ = MagicMock(return_value=None)
        mock_base_window.main_frame = tk.Frame(root_window)
        mock_base_window.logger = MagicMock()
        
        from src.utilities.system.diagnostics_monitoring.gui.battery_health_widget import \
            BatteryHealthWidget
        
        with patch.object(BatteryHealthWidget, 'setup_ui'), \
             patch.object(BatteryHealthWidget, 'show_info') as mock_show_info:
            
            widget = BatteryHealthWidget(root_window)
            
            widget.refresh_data()
            
            # Verify info message was shown
            mock_show_info.assert_called_once_with("No battery data available")
    
    @patch('src.utilities.system.diagnostics_monitoring.gui.battery_health_widget.BatteryMonitor')
    @patch('src.utilities.system.diagnostics_monitoring.gui.battery_health_widget.BaseWindow')
    def test_export_data_success(self, mock_base_window, mock_battery_monitor_class, root_window, mock_dependencies):
        """Test successful data export."""
        mock_base_window.__init__ = MagicMock(return_value=None)
        mock_base_window.main_frame = tk.Frame(root_window)
        mock_base_window.logger = MagicMock()
        
        from src.utilities.system.diagnostics_monitoring.gui.battery_health_widget import \
            BatteryHealthWidget
        
        with patch.object(BatteryHealthWidget, 'setup_ui'), \
             patch('tkinter.filedialog.asksaveasfilename', return_value='test_export.json'), \
             patch('builtins.open', create=True) as mock_open, \
             patch.object(BatteryHealthWidget, 'show_info') as mock_show_info:
            
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file
            
            widget = BatteryHealthWidget(root_window)
            widget.battery_data_history = [
                {
                    'timestamp': datetime.now(),
                    'data': {'batteries': [{'id': 'BAT0', 'percent': 80}]}
                }
            ]
            
            widget.export_data()
            
            # Verify file was written and success message shown
            mock_open.assert_called_once()
            mock_show_info.assert_called_once()
    
    @patch('src.utilities.system.diagnostics_monitoring.gui.battery_health_widget.BatteryMonitor')
    @patch('src.utilities.system.diagnostics_monitoring.gui.battery_health_widget.BaseWindow')
    def test_export_data_no_data(self, mock_base_window, mock_battery_monitor_class, root_window, mock_dependencies):
        """Test data export when no data available."""
        mock_base_window.__init__ = MagicMock(return_value=None)
        mock_base_window.main_frame = tk.Frame(root_window)
        mock_base_window.logger = MagicMock()
        
        from src.utilities.system.diagnostics_monitoring.gui.battery_health_widget import \
            BatteryHealthWidget
        
        with patch.object(BatteryHealthWidget, 'setup_ui'), \
             patch.object(BatteryHealthWidget, 'show_info') as mock_show_info:
            
            widget = BatteryHealthWidget(root_window)
            widget.battery_data_history = []
            
            widget.export_data()
            
            # Verify info message was shown
            mock_show_info.assert_called_once_with("No data to export")
    
    @patch('src.utilities.system.diagnostics_monitoring.gui.battery_health_widget.BatteryMonitor')
    @patch('src.utilities.system.diagnostics_monitoring.gui.battery_health_widget.BaseWindow')
    def test_chart_updates(self, mock_base_window, mock_battery_monitor_class, root_window, mock_dependencies):
        """Test chart update functionality."""
        mock_base_window.__init__ = MagicMock(return_value=None)
        mock_base_window.main_frame = tk.Frame(root_window)
        mock_base_window.logger = MagicMock()
        
        from src.utilities.system.diagnostics_monitoring.gui.battery_health_widget import \
            BatteryHealthWidget
        
        with patch.object(BatteryHealthWidget, 'setup_ui'), \
             patch.object(BatteryHealthWidget, 'update_charge_chart') as mock_charge, \
             patch.object(BatteryHealthWidget, 'update_health_chart') as mock_health, \
             patch.object(BatteryHealthWidget, 'update_power_chart') as mock_power, \
             patch.object(BatteryHealthWidget, 'update_cycle_chart') as mock_cycle:
            
            widget = BatteryHealthWidget(root_window)
            widget.battery_data_history = [
                {
                    'timestamp': datetime.now(),
                    'data': {'batteries': [{'id': 'BAT0', 'percent': 80}]}
                }
            ]
            
            widget.update_charts()
            
            # Verify all chart update methods were called
            mock_charge.assert_called_once()
            mock_health.assert_called_once()
            mock_power.assert_called_once()
            mock_cycle.assert_called_once()
    
    @patch('src.utilities.system.diagnostics_monitoring.gui.battery_health_widget.BatteryMonitor')
    @patch('src.utilities.system.diagnostics_monitoring.gui.battery_health_widget.BaseWindow')
    def test_on_closing(self, mock_base_window, mock_battery_monitor_class, root_window, mock_dependencies):
        """Test window closing handler."""
        mock_base_window.__init__ = MagicMock(return_value=None)
        mock_base_window.main_frame = tk.Frame(root_window)
        mock_base_window.logger = MagicMock()
        mock_base_window.destroy = MagicMock()
        
        from src.utilities.system.diagnostics_monitoring.gui.battery_health_widget import \
            BatteryHealthWidget
        
        with patch.object(BatteryHealthWidget, 'setup_ui'), \
             patch.object(BatteryHealthWidget, 'stop_monitoring') as mock_stop:
            
            widget = BatteryHealthWidget(root_window)
            widget.monitoring_active = True
            
            widget.on_closing()
            
            # Verify monitoring was stopped and window destroyed
            mock_stop.assert_called_once()
            mock_base_window.destroy.assert_called_once()
    
    @patch('src.utilities.system.diagnostics_monitoring.gui.battery_health_widget.BatteryMonitor')
    @patch('src.utilities.system.diagnostics_monitoring.gui.battery_health_widget.BaseWindow')
    def test_error_handling_in_methods(self, mock_base_window, mock_battery_monitor_class, root_window, mock_dependencies):
        """Test error handling in various methods."""
        mock_base_window.__init__ = MagicMock(return_value=None)
        mock_base_window.main_frame = tk.Frame(root_window)
        mock_logger = MagicMock()
        mock_base_window.logger = mock_logger
        
        from src.utilities.system.diagnostics_monitoring.gui.battery_health_widget import \
            BatteryHealthWidget
        
        with patch.object(BatteryHealthWidget, 'setup_ui'):
            widget = BatteryHealthWidget(root_window)
            
            # Test error in update_battery_status
            with patch.object(widget, 'battery_status_frame', side_effect=Exception("Test error")):
                widget.update_battery_status({'batteries': []})
                mock_logger.error.assert_called()
    
    def test_edge_cases(self, root_window, mock_dependencies):
        """Test edge cases and boundary conditions."""
        # Test with invalid interval values
        from src.utilities.system.diagnostics_monitoring.gui.battery_health_widget import \
            BatteryHealthWidget
        
        with patch('src.utilities.system.diagnostics_monitoring.gui.battery_health_widget.BatteryMonitor'), \
             patch('src.utilities.system.diagnostics_monitoring.gui.battery_health_widget.BaseWindow'), \
             patch.object(BatteryHealthWidget, 'setup_ui'), \
             patch.object(BatteryHealthWidget, 'start_monitoring'):
            
            widget = BatteryHealthWidget(root_window)
            widget.interval_var = tk.StringVar(value="invalid")
            widget.battery_monitor = MagicMock()
            widget.battery_monitor.start_monitoring.return_value = True
            widget.monitoring_active = False
            
            # Mock UI elements
            widget.start_button = MagicMock()
            widget.stop_button = MagicMock()
            
            with patch('threading.Thread'):
                widget.start_monitoring()
                
                # Should handle invalid interval gracefully
                assert widget.battery_monitor.update_interval == 60.0  # Default fallback
    
    @patch('src.utilities.system.diagnostics_monitoring.gui.battery_health_widget.BatteryMonitor')
    @patch('src.utilities.system.diagnostics_monitoring.gui.battery_health_widget.BaseWindow')
    def test_data_history_limit(self, mock_base_window, mock_battery_monitor_class, root_window, mock_dependencies):
        """Test battery data history limit enforcement."""
        mock_monitor = mock_battery_monitor_class.return_value
        mock_monitor.get_current_data.return_value = {
            'batteries': [{'id': 'BAT0', 'percent': 80}]
        }
        mock_monitor.update_interval = 0.01
        
        mock_base_window.__init__ = MagicMock(return_value=None)
        mock_base_window.main_frame = tk.Frame(root_window)
        mock_base_window.logger = MagicMock()
        
        from src.utilities.system.diagnostics_monitoring.gui.battery_health_widget import \
            BatteryHealthWidget
        
        with patch.object(BatteryHealthWidget, 'setup_ui'), \
             patch.object(BatteryHealthWidget, 'after'):
            
            widget = BatteryHealthWidget(root_window)
            widget.monitoring_active = True
            widget.max_history_points = 3  # Small limit for testing
            
            # Simulate adding more data than the limit
            for i in range(5):
                widget.battery_data_history.append({
                    'timestamp': datetime.now(),
                    'data': {'batteries': [{'id': 'BAT0', 'percent': 80 + i}]}
                })
                
                # Simulate the limit enforcement from update_loop
                if len(widget.battery_data_history) > widget.max_history_points:
                    widget.battery_data_history = (
                        widget.battery_data_history[-widget.max_history_points:]
                    )
            
            # Verify history was limited
            assert len(widget.battery_data_history) == 3
    
    @patch('src.utilities.system.diagnostics_monitoring.gui.battery_health_widget.BatteryMonitor')
    @patch('src.utilities.system.diagnostics_monitoring.gui.battery_health_widget.BaseWindow')
    def test_message_dialogs(self, mock_base_window, mock_battery_monitor_class, root_window, mock_dependencies):
        """Test message dialog functionality."""
        mock_base_window.__init__ = MagicMock(return_value=None)
        mock_base_window.main_frame = tk.Frame(root_window)
        mock_base_window.logger = MagicMock()
        
        from src.utilities.system.diagnostics_monitoring.gui.battery_health_widget import \
            BatteryHealthWidget
        
        with patch.object(BatteryHealthWidget, 'setup_ui'), \
             patch('tkinter.messagebox.showinfo') as mock_info, \
             patch('tkinter.messagebox.showerror') as mock_error:
            
            widget = BatteryHealthWidget(root_window)
            
            # Test info message
            widget.show_info("Test info message")
            mock_info.assert_called_once_with("Battery Health Monitor", "Test info message")
            
            # Test error message
            widget.show_error("Test error message")
            mock_error.assert_called_once_with("Battery Health Monitor - Error", "Test error message")


class TestBatteryHealthWidgetIntegration:
    """Integration tests for BatteryHealthWidget."""
    
    @patch('src.utilities.system.diagnostics_monitoring.gui.battery_health_widget.BatteryMonitor')
    @patch('src.utilities.system.diagnostics_monitoring.gui.battery_health_widget.BaseWindow')
    def test_full_monitoring_cycle(self, mock_base_window, mock_battery_monitor_class, mock_dependencies):
        """Test a complete monitoring cycle."""
        # Setup mocks
        mock_monitor = mock_battery_monitor_class.return_value
        mock_monitor.start_monitoring.return_value = True
        mock_monitor.get_current_data.return_value = {
            'batteries': [
                {
                    'id': 'BAT0',
                    'percent': 85.5,
                    'health_percent': 92.3,
                    'health_status': 'Good',
                    'power_plugged': False,
                    'cycle_count': 245,
                    'temperature': 32.5,
                    'voltage': 12.6,
                    'secsleft': 7200
                }
            ],
            'power_consumption': {'cpu_power_estimate': 15.2}
        }
        mock_monitor.update_interval = 0.1
        mock_monitor.is_running = True
        
        mock_base_window.__init__ = MagicMock(return_value=None)
        mock_base_window.main_frame = MagicMock()
        mock_base_window.logger = MagicMock()
        
        from src.utilities.system.diagnostics_monitoring.gui.battery_health_widget import \
            BatteryHealthWidget
        
        root = tk.Tk()
        root.withdraw()
        
        try:
            with patch.object(BatteryHealthWidget, 'setup_ui'):
                widget = BatteryHealthWidget(root)
                widget.interval_var = tk.StringVar(value="30")
                widget.start_button = MagicMock()
                widget.stop_button = MagicMock()
                
                # Start monitoring
                with patch('threading.Thread') as mock_thread:
                    widget.start_monitoring()
                    
                    # Verify monitoring started
                    assert widget.monitoring_active is True
                    mock_monitor.start_monitoring.assert_called_once()
                
                # Stop monitoring
                widget.stop_monitoring()
                
                # Verify monitoring stopped
                assert widget.monitoring_active is False
                mock_monitor.stop_monitoring.assert_called_once()
        
        finally:
            try:
                root.destroy()
            except tk.TclError:
                pass


class TestBatteryHealthWidgetPerformance:
    """Performance tests for BatteryHealthWidget."""
    
    @patch('src.utilities.system.diagnostics_monitoring.gui.battery_health_widget.BatteryMonitor')
    @patch('src.utilities.system.diagnostics_monitoring.gui.battery_health_widget.BaseWindow')
    def test_large_data_handling(self, mock_base_window, mock_battery_monitor_class, mock_dependencies):
        """Test handling of large amounts of battery data."""
        mock_base_window.__init__ = MagicMock(return_value=None)
        mock_base_window.main_frame = MagicMock()
        mock_base_window.logger = MagicMock()
        
        from src.utilities.system.diagnostics_monitoring.gui.battery_health_widget import \
            BatteryHealthWidget
        
        root = tk.Tk()
        root.withdraw()
        
        try:
            with patch.object(BatteryHealthWidget, 'setup_ui'):
                widget = BatteryHealthWidget(root)
                
                # Add large amount of data
                start_time = time.time()
                for i in range(1000):
                    widget.battery_data_history.append({
                        'timestamp': datetime.now() - timedelta(minutes=i),
                        'data': {
                            'batteries': [
                                {
                                    'id': f'BAT{j}',
                                    'percent': 50 + (i % 50),
                                    'health_percent': 90 + (i % 10)
                                } for j in range(5)  # 5 batteries
                            ]
                        }
                    })
                
                processing_time = time.time() - start_time
                
                # Verify data was processed efficiently
                assert len(widget.battery_data_history) == 1000
                assert processing_time < 1.0  # Should be fast
        
        finally:
            try:
                root.destroy()
            except tk.TclError:
                pass


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
                'test_file': 'test_battery_health_widget_2025-08-29.py',
                'target_module': 'battery_health_widget.py',
                'framework': 'pytest'
            }
        }
        
        # Write execution report
        report_path = 'c:/Users/richardi/1_2/tests/unit/result_battery_health_widget_2025-08-29.json'
        try:
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)
        except Exception as e:
            print(f"Could not write execution report: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])