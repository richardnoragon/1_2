"""Performance monitoring GUI widget for real-time system performance visualization.

This module provides a comprehensive GUI interface for monitoring system
performance including CPU, memory, and process analysis with real-time charts.
"""
from src.rfu.localization import localized_widget as _ui_widget, bind_literal as _ui_bind

from src.rfu import font_tokens
import logging
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

try:
    from PyQt5.QtCore import Qt, QTimer, pyqtSignal
    from PyQt5.QtGui import QColor, QFont, QPalette
    from PyQt5.QtWidgets import (
        QCheckBox,
        QComboBox,
        QFrame,
        QGridLayout,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QProgressBar,
        QPushButton,
        QScrollArea,
        QSpinBox,
        QSplitter,
        QTableWidget,
        QTableWidgetItem,
        QTabWidget,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )

    from src.gui.themes import Typography, token

    PYQT5_AVAILABLE = True
except ImportError:
    PYQT5_AVAILABLE = False

    # Create dummy classes for when PyQt5 is not available
    class QWidget:
        def __init__(self, parent=None):
            self.parent = parent

    class pyqtSignal:
        def __init__(self, *args):
            self.connected_functions = []

        def emit(self, *args):
            """Emit signal to connected functions."""
            for func in self.connected_functions:
                try:
                    func(*args)
                except Exception as e:
                    logging.warning(f"Signal emission failed: {e}")

        def connect(self, func):
            """Connect a function to this signal."""
            if callable(func):
                self.connected_functions.append(func)


from core.error_handler import error_handler


class PerformanceWidget(QWidget):
    """Performance monitoring widget with real-time visualization.

    Provides comprehensive performance monitoring interface including:
    - Real-time CPU and memory usage charts
    - Process monitoring and analysis
    - Performance metrics and statistics
    - Configurable monitoring settings
    """

    # Signals
    refresh_requested = pyqtSignal()
    settings_changed = pyqtSignal(dict)

    def __init__(self, parent=None):
        """Initialize the performance widget.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        self.logger = logging.getLogger("RFU.DiagnosticsMonitoring.PerformanceWidget")

        # Performance monitor instance
        self.performance_monitor = None

        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_display)
        self.update_interval = 2000  # 2 seconds

        # Data storage for charts
        self.cpu_history = []
        self.memory_history = []
        self.max_history_points = 60  # 2 minutes at 2-second intervals

        # UI state
        self.auto_refresh = True
        self.show_per_core = True
        self.show_processes = True

        if PYQT5_AVAILABLE:
            self.init_ui()
            self.logger.info("Performance widget initialized")
        else:
            self.logger.warning("PyQt5 not available, GUI disabled")

    def init_ui(self):
        """Initialize the user interface."""
        try:
            _ui_bind(self, 'setWindowTitle', 'Legacy.sbb77d93db2d0da43')
            self.setMinimumSize(800, 600)

            # Main layout
            main_layout = QVBoxLayout(self)

            # Control panel
            control_panel = self.create_control_panel()
            main_layout.addWidget(control_panel)

            # Main content area
            content_splitter = QSplitter(Qt.Horizontal)
            main_layout.addWidget(content_splitter)

            # Left panel - Overview and charts
            left_panel = self.create_overview_panel()
            content_splitter.addWidget(left_panel)

            # Right panel - Detailed information
            right_panel = self.create_details_panel()
            content_splitter.addWidget(right_panel)

            # Set splitter proportions
            content_splitter.setSizes([500, 300])

            # Status bar
            status_bar = self.create_status_bar()
            main_layout.addWidget(status_bar)

            # Apply styling
            self.apply_styling()

        except Exception as e:
            self.logger.error(f"Error initializing UI: {e}")
            error_handler.handle_error(e, "PerformanceWidget.init_ui")

    def create_control_panel(self) -> QWidget:
        """Create the control panel.

        Returns:
            Control panel widget
        """
        panel = QFrame()
        panel.setFrameStyle(QFrame.StyledPanel)
        panel.setMaximumHeight(80)

        layout = QHBoxLayout(panel)

        # Auto-refresh control
        self.auto_refresh_cb = _ui_widget(QCheckBox, 'Legacy.s7b36f955808e9f74', 'setText')
        _ui_bind(self.auto_refresh_cb, 'setAccessibleName', 'Legacy.sc7c026a80acf8742')
        self.auto_refresh_cb.setMinimumHeight(44)
        self.auto_refresh_cb.setChecked(self.auto_refresh)
        self.auto_refresh_cb.toggled.connect(self.toggle_auto_refresh)
        layout.addWidget(self.auto_refresh_cb)

        # Refresh interval
        layout.addWidget(_ui_widget(QLabel, 'Legacy.sa9f4edc07cde07e4', 'setText'))
        self.interval_spin = QSpinBox()
        _ui_bind(self.interval_spin, 'setAccessibleName', 'Legacy.s29a85213c92392cc')
        self.interval_spin.setMinimumHeight(44)
        self.interval_spin.setRange(1, 60)
        self.interval_spin.setValue(self.update_interval // 1000)
        self.interval_spin.valueChanged.connect(self.change_update_interval)
        layout.addWidget(self.interval_spin)

        # Manual refresh button
        self.refresh_btn = _ui_widget(SecondaryButton, 'Legacy.sc7b4a057f059ca05', 'setText')
        _ui_bind(self.refresh_btn, 'setAccessibleName', 'Legacy.sfc36f93998b8eaa6')
        self.refresh_btn.clicked.connect(self.manual_refresh)
        layout.addWidget(self.refresh_btn)

        layout.addStretch()

        # Display options
        self.per_core_cb = _ui_widget(QCheckBox, 'Legacy.s20031c4908fdfb01', 'setText')
        _ui_bind(self.per_core_cb, 'setAccessibleName', 'Legacy.s4a007df849663160')
        self.per_core_cb.setMinimumHeight(44)
        self.per_core_cb.setChecked(self.show_per_core)
        self.per_core_cb.toggled.connect(self.toggle_per_core_display)
        layout.addWidget(self.per_core_cb)

        self.processes_cb = _ui_widget(QCheckBox, 'Legacy.scc800fb709e5ac1f', 'setText')
        _ui_bind(self.processes_cb, 'setAccessibleName', 'Legacy.s02e7e6424ed7799a')
        self.processes_cb.setMinimumHeight(44)
        self.processes_cb.setChecked(self.show_processes)
        self.processes_cb.toggled.connect(self.toggle_process_display)
        layout.addWidget(self.processes_cb)

        return panel

    def create_overview_panel(self) -> QWidget:
        """Create the overview panel with charts and metrics.

        Returns:
            Overview panel widget
        """
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Tab widget for different views
        self.overview_tabs = QTabWidget()
        _ui_bind(self.overview_tabs, 'setAccessibleName', 'Legacy.sc4f068c245dda72d')
        layout.addWidget(self.overview_tabs)

        # CPU tab
        cpu_tab = self.create_cpu_tab()
        self.overview_tabs.addTab(cpu_tab, "CPU")

        # Memory tab
        memory_tab = self.create_memory_tab()
        self.overview_tabs.addTab(memory_tab, "Memory")

        # System tab
        system_tab = self.create_system_tab()
        self.overview_tabs.addTab(system_tab, "System")

        return panel

    def create_cpu_tab(self) -> QWidget:
        """Create the CPU monitoring tab.

        Returns:
            CPU tab widget
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # CPU overview
        cpu_overview = _ui_widget(QGroupBox, 'Legacy.s422c01836fcebced', 'setTitle')
        cpu_layout = QGridLayout(cpu_overview)

        # CPU usage display
        cpu_layout.addWidget(_ui_widget(QLabel, 'Legacy.s7cb76456e82f39c0', 'setText'), 0, 0)
        self.cpu_usage_label = _ui_widget(QLabel, 'Legacy.sd9a847a1a79ab448', 'setText')
        font_tokens.bind(self.cpu_usage_label, "font.title")
        cpu_layout.addWidget(self.cpu_usage_label, 0, 1)

        self.cpu_usage_bar = QProgressBar()
        self.cpu_usage_bar.setRange(0, 100)
        self.cpu_usage_bar.setFormat("%p%")
        cpu_layout.addWidget(self.cpu_usage_bar, 0, 2)

        # CPU details
        cpu_layout.addWidget(_ui_widget(QLabel, 'Legacy.sbd63495fdc60fe64', 'setText'), 1, 0)
        self.cpu_cores_label = _ui_widget(QLabel, 'Legacy.se2f79e5b60330bba', 'setText')
        cpu_layout.addWidget(self.cpu_cores_label, 1, 1)

        cpu_layout.addWidget(_ui_widget(QLabel, 'Legacy.s318c64475f824843', 'setText'), 2, 0)
        self.cpu_freq_label = _ui_widget(QLabel, 'Legacy.se2f79e5b60330bba', 'setText')
        cpu_layout.addWidget(self.cpu_freq_label, 2, 1)

        cpu_layout.addWidget(_ui_widget(QLabel, 'Legacy.s44bd0a9d177a4c78', 'setText'), 3, 0)
        self.cpu_temp_label = _ui_widget(QLabel, 'Legacy.se2f79e5b60330bba', 'setText')
        cpu_layout.addWidget(self.cpu_temp_label, 3, 1)

        layout.addWidget(cpu_overview)

        # Per-core CPU usage
        self.per_core_group = _ui_widget(QGroupBox, 'Legacy.sd71c50d1ed1dcc8c', 'setTitle')
        self.per_core_layout = QGridLayout(self.per_core_group)
        layout.addWidget(self.per_core_group)

        # CPU history chart placeholder
        cpu_chart_group = _ui_widget(QGroupBox, 'Legacy.se4f2865c338ea9de', 'setTitle')
        cpu_chart_layout = QVBoxLayout(cpu_chart_group)

        self.cpu_chart_text = QTextEdit()
        _ui_bind(self.cpu_chart_text, 'setAccessibleName', 'Legacy.se5dcb796a3a448ba')
        self.cpu_chart_text.setMaximumHeight(150)
        self.cpu_chart_text.setReadOnly(True)
        cpu_chart_layout.addWidget(self.cpu_chart_text)

        layout.addWidget(cpu_chart_group)

        return tab

    def create_memory_tab(self) -> QWidget:
        """Create the memory monitoring tab.

        Returns:
            Memory tab widget
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Memory overview
        memory_overview = _ui_widget(QGroupBox, 'Legacy.s165bd384d170c3e6', 'setTitle')
        memory_layout = QGridLayout(memory_overview)

        # Memory usage display
        memory_layout.addWidget(_ui_widget(QLabel, 'Legacy.s931c233e518b3723', 'setText'), 0, 0)
        self.memory_usage_label = _ui_widget(QLabel, 'Legacy.sd9a847a1a79ab448', 'setText')
        font_tokens.bind(self.memory_usage_label, "font.title")
        memory_layout.addWidget(self.memory_usage_label, 0, 1)

        self.memory_usage_bar = QProgressBar()
        self.memory_usage_bar.setRange(0, 100)
        self.memory_usage_bar.setFormat("%p%")
        memory_layout.addWidget(self.memory_usage_bar, 0, 2)

        # Memory details
        memory_layout.addWidget(_ui_widget(QLabel, 'Legacy.s18e872be2359d76e', 'setText'), 1, 0)
        self.memory_total_label = _ui_widget(QLabel, 'Legacy.se2f79e5b60330bba', 'setText')
        memory_layout.addWidget(self.memory_total_label, 1, 1)

        memory_layout.addWidget(_ui_widget(QLabel, 'Legacy.s72074a8a68367e12', 'setText'), 2, 0)
        self.memory_available_label = _ui_widget(QLabel, 'Legacy.se2f79e5b60330bba', 'setText')
        memory_layout.addWidget(self.memory_available_label, 2, 1)

        memory_layout.addWidget(_ui_widget(QLabel, 'Legacy.s05b15ffb77764094', 'setText'), 3, 0)
        self.memory_used_label = _ui_widget(QLabel, 'Legacy.se2f79e5b60330bba', 'setText')
        memory_layout.addWidget(self.memory_used_label, 3, 1)

        layout.addWidget(memory_overview)

        # Swap information
        swap_group = _ui_widget(QGroupBox, 'Legacy.s304548e8f1f73d05', 'setTitle')
        swap_layout = QGridLayout(swap_group)

        swap_layout.addWidget(_ui_widget(QLabel, 'Legacy.s02e6ffeb78eee676', 'setText'), 0, 0)
        self.swap_usage_label = _ui_widget(QLabel, 'Legacy.sd9a847a1a79ab448', 'setText')
        swap_layout.addWidget(self.swap_usage_label, 0, 1)

        self.swap_usage_bar = QProgressBar()
        self.swap_usage_bar.setRange(0, 100)
        self.swap_usage_bar.setFormat("%p%")
        swap_layout.addWidget(self.swap_usage_bar, 0, 2)

        swap_layout.addWidget(_ui_widget(QLabel, 'Legacy.s18e872be2359d76e', 'setText'), 1, 0)
        self.swap_total_label = _ui_widget(QLabel, 'Legacy.se2f79e5b60330bba', 'setText')
        swap_layout.addWidget(self.swap_total_label, 1, 1)

        layout.addWidget(swap_group)

        # Memory history chart placeholder
        memory_chart_group = _ui_widget(QGroupBox, 'Legacy.s80bf83afa5adaf27', 'setTitle')
        memory_chart_layout = QVBoxLayout(memory_chart_group)

        self.memory_chart_text = QTextEdit()
        _ui_bind(self.memory_chart_text, 'setAccessibleName', 'Legacy.sf7579d9756e3865f')
        self.memory_chart_text.setMaximumHeight(150)
        self.memory_chart_text.setReadOnly(True)
        memory_chart_layout.addWidget(self.memory_chart_text)

        layout.addWidget(memory_chart_group)

        return tab

    def create_system_tab(self) -> QWidget:
        """Create the system information tab.

        Returns:
            System tab widget
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # System overview
        system_overview = _ui_widget(QGroupBox, 'Legacy.s8ad54ec1c0dcab4f', 'setTitle')
        system_layout = QGridLayout(system_overview)

        system_layout.addWidget(_ui_widget(QLabel, 'Legacy.sc07ba68bc73e53a9', 'setText'), 0, 0)
        self.load_avg_label = _ui_widget(QLabel, 'Legacy.se2f79e5b60330bba', 'setText')
        system_layout.addWidget(self.load_avg_label, 0, 1)

        system_layout.addWidget(_ui_widget(QLabel, 'Legacy.s63a0447e268ab722', 'setText'), 1, 0)
        self.uptime_label = _ui_widget(QLabel, 'Legacy.se2f79e5b60330bba', 'setText')
        system_layout.addWidget(self.uptime_label, 1, 1)

        system_layout.addWidget(_ui_widget(QLabel, 'Legacy.sf189e3d8944e8329', 'setText'), 2, 0)
        self.processes_label = _ui_widget(QLabel, 'Legacy.se2f79e5b60330bba', 'setText')
        system_layout.addWidget(self.processes_label, 2, 1)

        system_layout.addWidget(_ui_widget(QLabel, 'Legacy.s21cc6c76f4aba4be', 'setText'), 3, 0)
        self.responsiveness_label = _ui_widget(QLabel, 'Legacy.se2f79e5b60330bba', 'setText')
        system_layout.addWidget(self.responsiveness_label, 3, 1)

        layout.addWidget(system_overview)

        # Performance metrics
        metrics_group = _ui_widget(QGroupBox, 'Legacy.sf34186f67a38a598', 'setTitle')
        metrics_layout = QVBoxLayout(metrics_group)

        self.metrics_text = QTextEdit()
        _ui_bind(self.metrics_text, 'setAccessibleName', 'Legacy.s5167b9cd755c25c7')
        self.metrics_text.setReadOnly(True)
        metrics_layout.addWidget(self.metrics_text)

        layout.addWidget(metrics_group)

        return tab

    def create_details_panel(self) -> QWidget:
        """Create the details panel with process information.

        Returns:
            Details panel widget
        """
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Process information
        self.process_group = _ui_widget(QGroupBox, 'Legacy.s060a204fd1490f83', 'setTitle')
        process_layout = QVBoxLayout(self.process_group)

        # Process selection
        process_controls = QHBoxLayout()
        process_controls.addWidget(_ui_widget(QLabel, 'Legacy.s27ab0062ef43bf40', 'setText'))

        self.sort_combo = QComboBox()
        _ui_bind(self.sort_combo, 'setAccessibleName', 'Legacy.s9c23c70ee2138c27')
        self.sort_combo.addItems(["CPU", "Memory"])
        self.sort_combo.currentTextChanged.connect(self.change_process_sort)
        process_controls.addWidget(self.sort_combo)

        process_controls.addStretch()
        process_layout.addLayout(process_controls)

        # Process table
        self.process_table = QTableWidget()
        _ui_bind(self.process_table, 'setAccessibleName', 'Legacy.saf7012567ed122e2')
        self.process_table.setColumnCount(5)
        self.process_table.setHorizontalHeaderLabels(
            ["PID", "Name", "CPU %", "Memory %", "Status"]
        )
        self.process_table.setAlternatingRowColors(True)
        self.process_table.setSelectionBehavior(QTableWidget.SelectRows)
        process_layout.addWidget(self.process_table)

        layout.addWidget(self.process_group)

        return panel

    def create_status_bar(self) -> QWidget:
        """Create the status bar.

        Returns:
            Status bar widget
        """
        status_bar = QFrame()
        status_bar.setFrameStyle(QFrame.StyledPanel)
        status_bar.setMaximumHeight(30)

        layout = QHBoxLayout(status_bar)

        self.status_label = _ui_widget(QLabel, 'Legacy.s5fa7aac5375c5815', 'setText')
        layout.addWidget(self.status_label)

        layout.addStretch()

        self.last_update_label = _ui_widget(QLabel, 'Legacy.s7d988f29d384372f', 'setText')
        layout.addWidget(self.last_update_label)

        return status_bar

    def apply_styling(self):
        """Apply custom styling to the widget."""
        try:
            # Set color scheme
            palette = self.palette()

            # Progress bar styling
            for progress_bar in [
                self.cpu_usage_bar,
                self.memory_usage_bar,
                self.swap_usage_bar,
            ]:
                progress_bar.setStyleSheet(
                    """
                    QProgressBar {
                        border: 1px solid grey;
                        border-radius: 3px;
                        text-align: center;
                    }
                    QProgressBar::chunk {
                        background-color: {token('semantic_success')};
                        border-radius: 2px;
                    }
                """
                )

            # Group box styling
            group_box_style = """
                QGroupBox {
                    font-weight: bold;
                    border: 2px solid {token('border')};
                    border-radius: 5px;
                    margin-top: 1ex;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                }
            """

            for group_box in self.findChildren(QGroupBox):
                group_box.setStyleSheet(group_box_style)

        except Exception as e:
            self.logger.error(f"Error applying styling: {e}")

    def set_performance_monitor(self, monitor):
        """Set the performance monitor instance.

        Args:
            monitor: PerformanceMonitor instance
        """
        self.performance_monitor = monitor

        if self.auto_refresh:
            self.start_auto_refresh()

    def start_auto_refresh(self):
        """Start automatic refresh timer."""
        if PYQT5_AVAILABLE and self.performance_monitor:
            self.update_timer.start(self.update_interval)
            self.status_label.setText("Auto-refresh enabled")

    def stop_auto_refresh(self):
        """Stop automatic refresh timer."""
        if PYQT5_AVAILABLE:
            self.update_timer.stop()
            self.status_label.setText("Auto-refresh disabled")

    def toggle_auto_refresh(self, enabled: bool):
        """Toggle auto-refresh on/off.

        Args:
            enabled: Whether to enable auto-refresh
        """
        self.auto_refresh = enabled

        if enabled:
            self.start_auto_refresh()
        else:
            self.stop_auto_refresh()

    def change_update_interval(self, interval: int):
        """Change the update interval.

        Args:
            interval: New interval in seconds
        """
        self.update_interval = interval * 1000

        if self.auto_refresh:
            self.update_timer.setInterval(self.update_interval)

    def toggle_per_core_display(self, enabled: bool):
        """Toggle per-core CPU display.

        Args:
            enabled: Whether to show per-core CPU usage
        """
        self.show_per_core = enabled
        self.per_core_group.setVisible(enabled)

    def toggle_process_display(self, enabled: bool):
        """Toggle process display.

        Args:
            enabled: Whether to show process information
        """
        self.show_processes = enabled
        self.process_group.setVisible(enabled)

    def change_process_sort(self, sort_by: str):
        """Change process sorting method.

        Args:
            sort_by: Sort criteria ("CPU" or "Memory")
        """
        self.update_process_table()

    def manual_refresh(self):
        """Manually refresh the display."""
        self.update_display()
        self.refresh_requested.emit()

    def update_display(self):
        """Update the display with current performance data."""
        if not self.performance_monitor:
            return

        try:
            # Get current performance data
            data = self.performance_monitor.get_current_data()

            if data:
                self.update_cpu_display(data)
                self.update_memory_display(data)
                self.update_system_display(data)

                if self.show_processes:
                    self.update_process_table(data)

                # Update status
                current_time = datetime.now().strftime("%H:%M:%S")
                self.last_update_label.setText(f"Last update: {current_time}")

                # Store history for charts
                self.store_history_data(data)
                self.update_charts()

        except Exception as e:
            self.logger.error(f"Error updating display: {e}")
            self.status_label.setText(f"Update error: {str(e)[:50]}")

    def update_cpu_display(self, data: Dict[str, Any]):
        """Update CPU display elements.

        Args:
            data: Performance data
        """
        try:
            # CPU usage
            cpu_percent = data.get("cpu_percent", 0)
            self.cpu_usage_label.setText(f"{cpu_percent:.1f}%")
            self.cpu_usage_bar.setValue(int(cpu_percent))

            # CPU details
            cores = data.get("cpu_logical_cores", "N/A")
            self.cpu_cores_label.setText(str(cores))

            freq = data.get("cpu_freq_current", "N/A")
            if freq != "N/A":
                self.cpu_freq_label.setText(f"{freq:.0f} MHz")
            else:
                self.cpu_freq_label.setText("N/A")

            temp = data.get("cpu_temperature", "N/A")
            if temp != "N/A":
                self.cpu_temp_label.setText(f"{temp:.1f}°C")
            else:
                self.cpu_temp_label.setText("N/A")

            # Per-core usage
            if self.show_per_core:
                self.update_per_core_display(data)

        except Exception as e:
            self.logger.error(f"Error updating CPU display: {e}")

    def update_per_core_display(self, data: Dict[str, Any]):
        """Update per-core CPU display.

        Args:
            data: Performance data
        """
        try:
            per_core = data.get("cpu_per_core", [])

            # Clear existing widgets
            for i in reversed(range(self.per_core_layout.count())):
                self.per_core_layout.itemAt(i).widget().setParent(None)

            # Add per-core progress bars
            for i, usage in enumerate(per_core):
                label = QLabel(f"Core {i}:")
                self.per_core_layout.addWidget(label, i // 4, (i % 4) * 2)

                progress = QProgressBar()
                progress.setRange(0, 100)
                progress.setValue(int(usage))
                progress.setFormat("%p%")
                self.per_core_layout.addWidget(progress, i // 4, (i % 4) * 2 + 1)

        except Exception as e:
            self.logger.error(f"Error updating per-core display: {e}")

    def update_memory_display(self, data: Dict[str, Any]):
        """Update memory display elements.

        Args:
            data: Performance data
        """
        try:
            # Memory usage
            memory_percent = data.get("memory_percent", 0)
            self.memory_usage_label.setText(f"{memory_percent:.1f}%")
            self.memory_usage_bar.setValue(int(memory_percent))

            # Memory details
            total_gb = data.get("memory_total_gb", 0)
            available_gb = data.get("memory_available_gb", 0)
            used_gb = data.get("memory_used_gb", 0)

            self.memory_total_label.setText(f"{total_gb:.1f} GB")
            self.memory_available_label.setText(f"{available_gb:.1f} GB")
            self.memory_used_label.setText(f"{used_gb:.1f} GB")

            # Swap usage
            swap_percent = data.get("swap_percent", 0)
            self.swap_usage_label.setText(f"{swap_percent:.1f}%")
            self.swap_usage_bar.setValue(int(swap_percent))

            swap_total_gb = data.get("swap_total_gb", 0)
            self.swap_total_label.setText(f"{swap_total_gb:.1f} GB")

        except Exception as e:
            self.logger.error(f"Error updating memory display: {e}")

    def update_system_display(self, data: Dict[str, Any]):
        """Update system display elements.

        Args:
            data: Performance data
        """
        try:
            # Load average
            load_1min = data.get("load_1min", "N/A")
            if load_1min != "N/A":
                self.load_avg_label.setText(f"{load_1min:.2f}")
            else:
                self.load_avg_label.setText("N/A")

            # Uptime
            uptime_hours = data.get("uptime_hours", "N/A")
            if uptime_hours != "N/A":
                days = int(uptime_hours // 24)
                hours = int(uptime_hours % 24)
                self.uptime_label.setText(f"{days}d {hours}h")
            else:
                self.uptime_label.setText("N/A")

            # Process count
            total_processes = data.get("total_processes", "N/A")
            running_processes = data.get("running_processes", "N/A")
            if total_processes != "N/A" and running_processes != "N/A":
                self.processes_label.setText(
                    f"{total_processes} ({running_processes} running)"
                )
            else:
                self.processes_label.setText("N/A")

            # Responsiveness score
            responsiveness = data.get("responsiveness_score", "N/A")
            if responsiveness != "N/A":
                self.responsiveness_label.setText(f"{responsiveness:.0f}/100")
            else:
                self.responsiveness_label.setText("N/A")

            # Update metrics text
            self.update_metrics_text(data)

        except Exception as e:
            self.logger.error(f"Error updating system display: {e}")

    def update_metrics_text(self, data: Dict[str, Any]):
        """Update the metrics text display.

        Args:
            data: Performance data
        """
        try:
            metrics_text = []

            # CPU metrics
            cpu_trend = data.get("cpu_trend", "stable")
            metrics_text.append(f"CPU Trend: {cpu_trend}")

            cpu_user = data.get("cpu_user_percent", "N/A")
            if cpu_user != "N/A":
                metrics_text.append(f"CPU User: {cpu_user:.1f}%")

            cpu_system = data.get("cpu_system_percent", "N/A")
            if cpu_system != "N/A":
                metrics_text.append(f"CPU System: {cpu_system:.1f}%")

            # Memory metrics
            memory_trend = data.get("memory_trend", "stable")
            metrics_text.append(f"Memory Trend: {memory_trend}")

            memory_pressure = data.get("memory_pressure", "N/A")
            if memory_pressure != "N/A":
                metrics_text.append(f"Memory Pressure: {memory_pressure:.1f}")

            # System metrics
            load_trend = data.get("load_trend", "stable")
            metrics_text.append(f"Load Trend: {load_trend}")

            self.metrics_text.setPlainText("\n".join(metrics_text))

        except Exception as e:
            self.logger.error(f"Error updating metrics text: {e}")

    def update_process_table(self, data: Optional[Dict[str, Any]] = None):
        """Update the process table.

        Args:
            data: Performance data (optional)
        """
        try:
            if not data:
                return

            sort_by = self.sort_combo.currentText().lower()

            if sort_by == "cpu":
                processes = data.get("top_cpu_processes", [])
            else:
                processes = data.get("top_memory_processes", [])

            self.process_table.setRowCount(len(processes))

            for row, process in enumerate(processes):
                # PID
                pid_item = QTableWidgetItem(str(process.get("pid", "N/A")))
                self.process_table.setItem(row, 0, pid_item)

                # Name
                name_item = QTableWidgetItem(process.get("name", "N/A"))
                self.process_table.setItem(row, 1, name_item)

                # CPU %
                cpu_item = QTableWidgetItem(f"{process.get('cpu_percent', 0):.1f}%")
                self.process_table.setItem(row, 2, cpu_item)

                # Memory %
                memory_item = QTableWidgetItem(
                    f"{process.get('memory_percent', 0):.1f}%"
                )
                self.process_table.setItem(row, 3, memory_item)

                # Status
                status_item = QTableWidgetItem(process.get("status", "N/A"))
                self.process_table.setItem(row, 4, status_item)

            # Resize columns to content
            self.process_table.resizeColumnsToContents()

        except Exception as e:
            self.logger.error(f"Error updating process table: {e}")

    def store_history_data(self, data: Dict[str, Any]):
        """Store data for history charts.

        Args:
            data: Performance data
        """
        try:
            current_time = datetime.now()

            # Store CPU history
            cpu_point = {
                "time": current_time,
                "usage": data.get("cpu_percent", 0),
            }
            self.cpu_history.append(cpu_point)

            # Store memory history
            memory_point = {
                "time": current_time,
                "usage": data.get("memory_percent", 0),
            }
            self.memory_history.append(memory_point)

            # Limit history size
            if len(self.cpu_history) > self.max_history_points:
                self.cpu_history = self.cpu_history[-self.max_history_points :]

            if len(self.memory_history) > self.max_history_points:
                self.memory_history = self.memory_history[-self.max_history_points :]

        except Exception as e:
            self.logger.error(f"Error storing history data: {e}")

    def update_charts(self):
        """Update the history charts with simple text representation."""
        try:
            # Update CPU chart
            if self.cpu_history:
                cpu_text = "CPU Usage History (last 60 points):\n"
                recent_cpu = self.cpu_history[-20:]  # Show last 20 points

                for i, point in enumerate(recent_cpu):
                    time_str = point["time"].strftime("%H:%M:%S")
                    usage = point["usage"]
                    bar_length = int(usage / 5)  # Scale to 20 chars max
                    bar = "█" * bar_length + "░" * (20 - bar_length)
                    cpu_text += f"{time_str}: {bar} {usage:.1f}%\n"

                self.cpu_chart_text.setPlainText(cpu_text)

            # Update memory chart
            if self.memory_history:
                memory_text = "Memory Usage History (last 60 points):\n"
                recent_memory = self.memory_history[-20:]  # Show last 20 points

                for i, point in enumerate(recent_memory):
                    time_str = point["time"].strftime("%H:%M:%S")
                    usage = point["usage"]
                    bar_length = int(usage / 5)  # Scale to 20 chars max
                    bar = "█" * bar_length + "░" * (20 - bar_length)
                    memory_text += f"{time_str}: {bar} {usage:.1f}%\n"

                self.memory_chart_text.setPlainText(memory_text)

        except Exception as e:
            self.logger.error(f"Error updating charts: {e}")

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for export.

        Returns:
            Dict containing performance summary
        """
        if not self.performance_monitor:
            return {}

        try:
            return self.performance_monitor.get_performance_summary()
        except Exception as e:
            self.logger.error(f"Error getting performance summary: {e}")
            return {}

    def export_data(self, format_type: str = "json") -> Optional[str]:
        """Export performance data.

        Args:
            format_type: Export format ("json", "csv")

        Returns:
            Exported data as string or None
        """
        try:
            if not self.performance_monitor:
                return None

            data = self.performance_monitor.get_current_data()

            if format_type.lower() == "json":
                import json

                return json.dumps(data, indent=2, default=str)
            elif format_type.lower() == "csv":
                import csv
                import io

                output = io.StringIO()
                if data:
                    writer = csv.DictWriter(output, fieldnames=data.keys())
                    writer.writeheader()
                    writer.writerow(data)

                return output.getvalue()
            else:
                return str(data)

        except Exception as e:
            self.logger.error(f"Error exporting data: {e}")
            return None

    def closeEvent(self, event):
        """Handle widget close event."""
        try:
            self.stop_auto_refresh()
            event.accept()
        except Exception as e:
            self.logger.error(f"Error during close: {e}")
            event.accept()


def create_performance_widget(performance_monitor=None) -> PerformanceWidget:
    """Create a performance widget instance.

    Args:
        performance_monitor: PerformanceMonitor instance

    Returns:
        PerformanceWidget instance
    """
    widget = PerformanceWidget()

    if performance_monitor:
        widget.set_performance_monitor(performance_monitor)

    return widget


# Standalone testing
if __name__ == "__main__":
    if PYQT5_AVAILABLE:
        from PyQt5.QtWidgets import QApplication

        app = QApplication(sys.argv)

        # Create test widget
        widget = create_performance_widget()
        widget.show()

        sys.exit(app.exec_())
    else:
        print("PyQt5 not available for standalone testing")
