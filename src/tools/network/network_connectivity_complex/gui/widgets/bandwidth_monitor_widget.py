"""Bandwidth Monitor Widget for real-time network speed monitoring."""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QGroupBox,
    QComboBox,
    QSpinBox,
    QCheckBox,
    QTabWidget,
    QSplitter,
    QFrame,
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, pyqtSlot

from gui.common.standard_window import StandardWindow
from gui.themes import ThemeManager, Colors, Spacing, Dimensions
from ..components.data_visualization import (
    RealTimeChart,
    ProgressIndicator,
    StatusIndicator,
    DataTable,
)
from ..components.network_interface_selector import NetworkInterfaceSelector
from ...tools.bandwidth_monitor import BandwidthMonitor


class BandwidthStatisticsWidget(QWidget):
    """Widget displaying bandwidth statistics."""

    def __init__(self, parent=None):
        """Initialize statistics widget."""
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Setup statistics UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            Spacing.MEDIUM_SPACING,
            Spacing.MEDIUM_SPACING,
            Spacing.MEDIUM_SPACING,
            Spacing.MEDIUM_SPACING,
        )
        layout.setSpacing(Spacing.MEDIUM_SPACING)

        # Current speeds group
        current_group = QGroupBox("Current Speeds")
        ThemeManager.style_group_box(current_group)
        layout.addWidget(current_group)

        current_layout = QVBoxLayout(current_group)
        current_layout.setSpacing(Spacing.SMALL_SPACING)

        # Download speed
        self.download_label = QLabel("Download: 0.0 Mbps")
        ThemeManager.style_label(self.download_label, is_header=True)
        current_layout.addWidget(self.download_label)

        # Upload speed
        self.upload_label = QLabel("Upload: 0.0 Mbps")
        ThemeManager.style_label(self.upload_label, is_header=True)
        current_layout.addWidget(self.upload_label)

        # Statistics group
        stats_group = QGroupBox("Statistics (Last Hour)")
        ThemeManager.style_group_box(stats_group)
        layout.addWidget(stats_group)

        stats_layout = QVBoxLayout(stats_group)
        stats_layout.setSpacing(Spacing.SMALL_SPACING)

        # Average speeds
        self.avg_download_label = QLabel("Avg Download: 0.0 Mbps")
        ThemeManager.style_label(self.avg_download_label)
        stats_layout.addWidget(self.avg_download_label)

        self.avg_upload_label = QLabel("Avg Upload: 0.0 Mbps")
        ThemeManager.style_label(self.avg_upload_label)
        stats_layout.addWidget(self.avg_upload_label)

        # Peak speeds
        self.peak_download_label = QLabel("Peak Download: 0.0 Mbps")
        ThemeManager.style_label(self.peak_download_label)
        stats_layout.addWidget(self.peak_download_label)

        self.peak_upload_label = QLabel("Peak Upload: 0.0 Mbps")
        ThemeManager.style_label(self.peak_upload_label)
        stats_layout.addWidget(self.peak_upload_label)

        # Total data
        self.total_data_label = QLabel("Total Data: 0.0 GB")
        ThemeManager.style_label(self.total_data_label)
        stats_layout.addWidget(self.total_data_label)

        layout.addStretch()

    def update_current_speeds(self, download_mbps: float, upload_mbps: float):
        """Update current speed display.

        Args:
            download_mbps: Download speed in Mbps
            upload_mbps: Upload speed in Mbps
        """
        self.download_label.setText(f"Download: {download_mbps:.2f} Mbps")
        self.upload_label.setText(f"Upload: {upload_mbps:.2f} Mbps")

    def update_statistics(self, stats: Dict[str, float]):
        """Update statistics display.

        Args:
            stats: Statistics dictionary
        """
        self.avg_download_label.setText(
            f"Avg Download: {stats.get('avg_download_mbps', 0):.2f} Mbps"
        )
        self.avg_upload_label.setText(
            f"Avg Upload: {stats.get('avg_upload_mbps', 0):.2f} Mbps"
        )
        self.peak_download_label.setText(
            f"Peak Download: {stats.get('max_download_mbps', 0):.2f} Mbps"
        )
        self.peak_upload_label.setText(
            f"Peak Upload: {stats.get('max_upload_mbps', 0):.2f} Mbps"
        )
        self.total_data_label.setText(
            f"Total Data: {stats.get('total_data_gb', 0):.2f} GB"
        )


class BandwidthControlPanel(QWidget):
    """Control panel for bandwidth monitoring."""

    # Signals
    start_monitoring = pyqtSignal(list)  # interface_names
    stop_monitoring = pyqtSignal()
    export_data = pyqtSignal(str, str)  # file_path, format
    settings_changed = pyqtSignal(dict)  # settings

    def __init__(self, parent=None):
        """Initialize control panel."""
        super().__init__(parent)
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """Setup control panel UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            Spacing.MEDIUM_SPACING,
            Spacing.MEDIUM_SPACING,
            Spacing.MEDIUM_SPACING,
            Spacing.MEDIUM_SPACING,
        )
        layout.setSpacing(Spacing.MEDIUM_SPACING)

        # Interface selection
        self.interface_selector = NetworkInterfaceSelector("active")
        layout.addWidget(self.interface_selector)

        # Monitoring controls
        controls_group = QGroupBox("Monitoring Controls")
        ThemeManager.style_group_box(controls_group)
        layout.addWidget(controls_group)

        controls_layout = QVBoxLayout(controls_group)
        controls_layout.setSpacing(Spacing.SMALL_SPACING)

        # Start/Stop buttons
        button_layout = QHBoxLayout()

        self.start_button = QPushButton("Start Monitoring")
        ThemeManager.style_primary_button(self.start_button)
        button_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Monitoring")
        ThemeManager.style_secondary_button(self.stop_button)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)

        controls_layout.addLayout(button_layout)

        # Settings group
        settings_group = QGroupBox("Settings")
        ThemeManager.style_group_box(settings_group)
        layout.addWidget(settings_group)

        settings_layout = QVBoxLayout(settings_group)
        settings_layout.setSpacing(Spacing.SMALL_SPACING)

        # Monitoring interval
        interval_layout = QHBoxLayout()
        interval_label = QLabel("Update Interval (ms):")
        ThemeManager.style_label(interval_label)
        interval_layout.addWidget(interval_label)

        self.interval_spinbox = QSpinBox()
        self.interval_spinbox.setRange(100, 10000)
        self.interval_spinbox.setValue(1000)
        self.interval_spinbox.setSuffix(" ms")
        ThemeManager.style_input_field(self.interval_spinbox)
        interval_layout.addWidget(self.interval_spinbox)

        settings_layout.addLayout(interval_layout)

        # Enable alerts
        self.alerts_checkbox = QCheckBox("Enable Speed Alerts")
        self.alerts_checkbox.setChecked(True)
        settings_layout.addWidget(self.alerts_checkbox)

        # Export controls
        export_group = QGroupBox("Data Export")
        ThemeManager.style_group_box(export_group)
        layout.addWidget(export_group)

        export_layout = QVBoxLayout(export_group)
        export_layout.setSpacing(Spacing.SMALL_SPACING)

        # Export format
        format_layout = QHBoxLayout()
        format_label = QLabel("Format:")
        ThemeManager.style_label(format_label)
        format_layout.addWidget(format_label)

        self.format_combo = QComboBox()
        self.format_combo.addItems(["CSV", "JSON"])
        ThemeManager.style_input_field(self.format_combo)
        format_layout.addWidget(self.format_combo)

        export_layout.addLayout(format_layout)

        # Export button
        self.export_button = QPushButton("Export Data")
        ThemeManager.style_secondary_button(self.export_button)
        export_layout.addWidget(self.export_button)

        layout.addStretch()

    def _connect_signals(self):
        """Connect control panel signals."""
        self.start_button.clicked.connect(self._on_start_clicked)
        self.stop_button.clicked.connect(self._on_stop_clicked)
        self.export_button.clicked.connect(self._on_export_clicked)
        self.interval_spinbox.valueChanged.connect(self._on_settings_changed)
        self.alerts_checkbox.toggled.connect(self._on_settings_changed)

    def _on_start_clicked(self):
        """Handle start monitoring button click."""
        interface_name = self.interface_selector.get_selected_interface()
        if interface_name:
            self.start_monitoring.emit([interface_name])
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)

    def _on_stop_clicked(self):
        """Handle stop monitoring button click."""
        self.stop_monitoring.emit()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def _on_export_clicked(self):
        """Handle export button click."""
        from PyQt5.QtWidgets import QFileDialog

        format_type = self.format_combo.currentText().lower()
        file_filter = (
            "CSV files (*.csv)"
            if format_type == "csv"
            else "JSON files (*.json)"
        )
        default_name = f"bandwidth_data.{format_type}"

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Bandwidth Data", default_name, file_filter
        )

        if file_path:
            self.export_data.emit(file_path, format_type)

    def _on_settings_changed(self):
        """Handle settings change."""
        settings = {
            "monitoring_interval": self.interval_spinbox.value(),
            "enable_alerts": self.alerts_checkbox.isChecked(),
        }
        self.settings_changed.emit(settings)

    def set_monitoring_state(self, is_monitoring: bool):
        """Set monitoring state.

        Args:
            is_monitoring: True if monitoring is active
        """
        self.start_button.setEnabled(not is_monitoring)
        self.stop_button.setEnabled(is_monitoring)


class BandwidthMonitorWidget(StandardWindow):
    """Main bandwidth monitor widget with real-time charts and statistics."""

    def __init__(self, parent=None):
        """Initialize bandwidth monitor widget."""
        super().__init__("Bandwidth Monitor", is_main_window=False)

        # Initialize bandwidth monitor
        self.bandwidth_monitor = BandwidthMonitor()

        # Setup UI
        self._setup_ui()
        self._connect_signals()

        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_display)
        self.update_timer.start(1000)  # Update every second

        # Show window
        self.show()

    def _setup_ui(self):
        """Setup bandwidth monitor UI."""
        # Create main splitter
        main_splitter = QSplitter(Qt.Horizontal)
        self.set_content_widget(main_splitter)

        # Left panel - Controls and statistics
        left_panel = QWidget()
        left_panel.setMaximumWidth(350)
        left_panel.setMinimumWidth(300)
        main_splitter.addWidget(left_panel)

        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(Spacing.MEDIUM_SPACING)

        # Status indicator
        self.status_indicator = StatusIndicator()
        left_layout.addWidget(self.status_indicator)

        # Control panel
        self.control_panel = BandwidthControlPanel()
        left_layout.addWidget(self.control_panel)

        # Statistics widget
        self.statistics_widget = BandwidthStatisticsWidget()
        left_layout.addWidget(self.statistics_widget)

        # Right panel - Charts and data
        right_panel = QWidget()
        main_splitter.addWidget(right_panel)

        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(Spacing.MEDIUM_SPACING)

        # Tab widget for different views
        self.tab_widget = QTabWidget()
        right_layout.addWidget(self.tab_widget)

        # Real-time chart tab
        self.chart_widget = RealTimeChart("Network Speed", max_points=60)
        self.chart_widget.add_series("Download", Colors.ACCENT)
        self.chart_widget.add_series("Upload", Colors.SUCCESS)
        self.tab_widget.addTab(self.chart_widget, "Real-time Chart")

        # Historical data tab
        self.data_table = DataTable()
        self.data_table.set_headers(
            [
                "Time",
                "Interface",
                "Download (Mbps)",
                "Upload (Mbps)",
                "Total Recv (MB)",
                "Total Sent (MB)",
            ]
        )
        self.tab_widget.addTab(self.data_table, "Historical Data")

        # Set splitter proportions
        main_splitter.setSizes([350, 650])

    def _connect_signals(self):
        """Connect widget signals."""
        # Control panel signals
        self.control_panel.start_monitoring.connect(self._start_monitoring)
        self.control_panel.stop_monitoring.connect(self._stop_monitoring)
        self.control_panel.export_data.connect(self._export_data)
        self.control_panel.settings_changed.connect(self._apply_settings)

        # Bandwidth monitor signals
        self.bandwidth_monitor.status_changed.connect(self._on_status_changed)
        self.bandwidth_monitor.data_updated.connect(self._on_data_updated)
        self.bandwidth_monitor.error_occurred.connect(self._on_error_occurred)

    @pyqtSlot(list)
    def _start_monitoring(self, interface_names: List[str]):
        """Start bandwidth monitoring.

        Args:
            interface_names: List of interface names to monitor
        """
        try:
            success = self.bandwidth_monitor.start_monitoring(interface_names)
            if success:
                self.status_indicator.set_status(
                    "running", "Monitoring active"
                )
                self.show_success_message("Bandwidth monitoring started")
            else:
                self.status_indicator.set_status("error", "Failed to start")
                self.show_error_message("Failed to start monitoring")
                self.control_panel.set_monitoring_state(False)
        except Exception as e:
            self.status_indicator.set_status("error", f"Error: {e}")
            self.show_error_message(f"Error starting monitoring: {e}")
            self.control_panel.set_monitoring_state(False)

    @pyqtSlot()
    def _stop_monitoring(self):
        """Stop bandwidth monitoring."""
        try:
            success = self.bandwidth_monitor.stop_monitoring()
            if success:
                self.status_indicator.set_status("idle", "Monitoring stopped")
                self.show_info_message("Bandwidth monitoring stopped")
            else:
                self.show_error_message("Failed to stop monitoring")
        except Exception as e:
            self.show_error_message(f"Error stopping monitoring: {e}")

    @pyqtSlot(str, str)
    def _export_data(self, file_path: str, format_type: str):
        """Export bandwidth data.

        Args:
            file_path: Export file path
            format_type: Export format ('csv' or 'json')
        """
        try:
            success = self.bandwidth_monitor.export_data(
                file_path, format_type
            )
            if success:
                self.show_success_message(f"Data exported to {file_path}")
            else:
                self.show_error_message("Failed to export data")
        except Exception as e:
            self.show_error_message(f"Export error: {e}")

    @pyqtSlot(dict)
    def _apply_settings(self, settings: Dict[str, Any]):
        """Apply settings changes.

        Args:
            settings: Settings dictionary
        """
        try:
            # Update monitoring interval
            if "monitoring_interval" in settings:
                interval_ms = settings["monitoring_interval"]
                self.bandwidth_monitor.set_monitoring_interval(
                    interval_ms / 1000.0
                )

            # Update alert settings
            if "enable_alerts" in settings:
                # Implementation would depend on alert configuration
                pass

        except Exception as e:
            self.show_error_message(f"Settings error: {e}")

    @pyqtSlot(str)
    def _on_status_changed(self, status: str):
        """Handle bandwidth monitor status change.

        Args:
            status: Status message
        """
        if "started" in status.lower():
            self.status_indicator.set_status("running", status)
        elif "stopped" in status.lower():
            self.status_indicator.set_status("idle", status)
        else:
            self.status_indicator.set_status("idle", status)

    @pyqtSlot(dict)
    def _on_data_updated(self, data: Dict[str, Any]):
        """Handle bandwidth data update.

        Args:
            data: Updated bandwidth data
        """
        # Update chart if we have speed data
        if "download_speed_mbps" in data and "upload_speed_mbps" in data:
            timestamp = datetime.now()
            self.chart_widget.add_data_point(
                "Download", data["download_speed_mbps"], timestamp
            )
            self.chart_widget.add_data_point(
                "Upload", data["upload_speed_mbps"], timestamp
            )

            # Update statistics
            self.statistics_widget.update_current_speeds(
                data["download_speed_mbps"], data["upload_speed_mbps"]
            )

        # Add to historical data table
        if "timestamp" in data:
            row_data = [
                data.get("timestamp", ""),
                data.get("interface_name", ""),
                f"{data.get('download_speed_mbps', 0):.2f}",
                f"{data.get('upload_speed_mbps', 0):.2f}",
                f"{data.get('total_bytes_recv', 0) / (1024*1024):.2f}",
                f"{data.get('total_bytes_sent', 0) / (1024*1024):.2f}",
            ]
            self.data_table.add_row(row_data)

            # Limit table size
            if self.data_table.rowCount() > 1000:
                self.data_table.removeRow(0)

    @pyqtSlot(str)
    def _on_error_occurred(self, error: str):
        """Handle bandwidth monitor error.

        Args:
            error: Error message
        """
        self.status_indicator.set_status("error", f"Error: {error}")
        self.show_error_message(error)
        self.control_panel.set_monitoring_state(False)

    def _update_display(self):
        """Update display with current statistics."""
        try:
            # Get current statistics
            stats = self.bandwidth_monitor.get_current_statistics()
            if stats:
                self.statistics_widget.update_statistics(stats)
        except Exception as e:
            # Silently handle errors to avoid spam
            pass

    def closeEvent(self, event):
        """Handle window close event."""
        # Stop monitoring if active
        if self.bandwidth_monitor.is_running:
            self.bandwidth_monitor.stop_monitoring()

        # Stop update timer
        self.update_timer.stop()

        super().closeEvent(event)
