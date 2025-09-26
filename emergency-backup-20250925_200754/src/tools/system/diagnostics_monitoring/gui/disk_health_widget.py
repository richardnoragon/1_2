"""Disk health visualization widget for diagnostics monitoring."""

import sys
from typing import Dict, Any, List, Optional
from datetime import datetime

try:
    from PyQt5.QtWidgets import (
        QWidget,
        QVBoxLayout,
        QHBoxLayout,
        QLabel,
        QProgressBar,
        QTreeWidget,
        QTreeWidgetItem,
        QTabWidget,
        QGroupBox,
        QScrollArea,
        QFrame,
        QPushButton,
        QMessageBox,
        QSplitter,
    )
    from PyQt5.QtCore import Qt, QTimer, pyqtSignal
    from PyQt5.QtGui import QFont, QPalette, QColor, QPixmap, QPainter

    PYQT5_AVAILABLE = True
except ImportError:
    PYQT5_AVAILABLE = False

    # Create dummy classes for when PyQt5 is not available
    class QWidget:
        pass

    class pyqtSignal:
        def __init__(self, *args):
            pass


from ..monitors.disk_health.disk_monitor import DiskHealthMonitor
from core.error_handler import error_handler


class DiskHealthWidget(QWidget):
    """Widget for displaying disk health information."""

    # Signals
    refresh_requested = pyqtSignal()
    disk_selected = pyqtSignal(str, str)  # device_id, disk_type

    def __init__(self, parent=None):
        """Initialize disk health widget.

        Args:
            parent: Parent widget
        """
        if not PYQT5_AVAILABLE:
            raise ImportError("PyQt5 is required for GUI components")

        super().__init__(parent)

        # Initialize disk monitor
        self.disk_monitor = None
        self.current_data = {}

        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.refresh_data)
        self.update_timer.setInterval(30000)  # 30 seconds

        # Setup UI
        self.setup_ui()
        self.setup_styles()

        # Initialize data
        self.initialize_monitor()

    def setup_ui(self):
        """Setup the user interface."""
        try:
            # Main layout
            main_layout = QVBoxLayout(self)
            main_layout.setContentsMargins(10, 10, 10, 10)
            main_layout.setSpacing(10)

            # Header
            header_layout = self.create_header()
            main_layout.addLayout(header_layout)

            # Main content splitter
            splitter = QSplitter(Qt.Horizontal)
            main_layout.addWidget(splitter)

            # Left panel - Disk list
            left_panel = self.create_disk_list_panel()
            splitter.addWidget(left_panel)

            # Right panel - Disk details
            right_panel = self.create_disk_details_panel()
            splitter.addWidget(right_panel)

            # Set splitter proportions
            splitter.setSizes([300, 500])

            # Status bar
            status_layout = self.create_status_bar()
            main_layout.addLayout(status_layout)

        except Exception as e:
            error_handler.handle_error(e, "DiskHealthWidget.setup_ui")

    def create_header(self) -> QHBoxLayout:
        """Create header with title and controls.

        Returns:
            QHBoxLayout: Header layout
        """
        try:
            header_layout = QHBoxLayout()

            # Title
            title_label = QLabel("Disk Health Monitor")
            title_font = QFont()
            title_font.setPointSize(16)
            title_font.setBold(True)
            title_label.setFont(title_font)
            header_layout.addWidget(title_label)

            # Spacer
            header_layout.addStretch()

            # Refresh button
            self.refresh_button = QPushButton("Refresh")
            self.refresh_button.clicked.connect(self.refresh_data)
            header_layout.addWidget(self.refresh_button)

            # Auto-refresh toggle
            self.auto_refresh_button = QPushButton("Auto-Refresh: ON")
            self.auto_refresh_button.setCheckable(True)
            self.auto_refresh_button.setChecked(True)
            self.auto_refresh_button.clicked.connect(self.toggle_auto_refresh)
            header_layout.addWidget(self.auto_refresh_button)

            return header_layout

        except Exception as e:
            error_handler.handle_error(e, "DiskHealthWidget.create_header")
            return QHBoxLayout()

    def create_disk_list_panel(self) -> QWidget:
        """Create disk list panel.

        Returns:
            QWidget: Disk list panel
        """
        try:
            panel = QWidget()
            layout = QVBoxLayout(panel)

            # Panel title
            title_label = QLabel("Disk Overview")
            title_font = QFont()
            title_font.setPointSize(12)
            title_font.setBold(True)
            title_label.setFont(title_font)
            layout.addWidget(title_label)

            # Summary section
            self.summary_group = self.create_summary_section()
            layout.addWidget(self.summary_group)

            # Disk tree
            self.disk_tree = QTreeWidget()
            self.disk_tree.setHeaderLabels(
                ["Device", "Type", "Size", "Health", "Usage"]
            )
            self.disk_tree.itemClicked.connect(self.on_disk_selected)
            layout.addWidget(self.disk_tree)

            return panel

        except Exception as e:
            error_handler.handle_error(
                e, "DiskHealthWidget.create_disk_list_panel"
            )
            return QWidget()

    def create_summary_section(self) -> QGroupBox:
        """Create summary section.

        Returns:
            QGroupBox: Summary group box
        """
        try:
            group = QGroupBox("Summary")
            layout = QVBoxLayout(group)

            # Summary labels
            self.total_disks_label = QLabel("Total Disks: 0")
            self.healthy_disks_label = QLabel("Healthy: 0")
            self.warning_disks_label = QLabel("Warning: 0")
            self.critical_disks_label = QLabel("Critical: 0")
            self.total_capacity_label = QLabel("Total Capacity: 0 GB")
            self.total_used_label = QLabel("Total Used: 0 GB")

            layout.addWidget(self.total_disks_label)
            layout.addWidget(self.healthy_disks_label)
            layout.addWidget(self.warning_disks_label)
            layout.addWidget(self.critical_disks_label)
            layout.addWidget(self.total_capacity_label)
            layout.addWidget(self.total_used_label)

            return group

        except Exception as e:
            error_handler.handle_error(
                e, "DiskHealthWidget.create_summary_section"
            )
            return QGroupBox()

    def create_disk_details_panel(self) -> QWidget:
        """Create disk details panel.

        Returns:
            QWidget: Disk details panel
        """
        try:
            panel = QWidget()
            layout = QVBoxLayout(panel)

            # Panel title
            self.details_title = QLabel("Select a disk to view details")
            title_font = QFont()
            title_font.setPointSize(12)
            title_font.setBold(True)
            self.details_title.setFont(title_font)
            layout.addWidget(self.details_title)

            # Details tabs
            self.details_tabs = QTabWidget()
            layout.addWidget(self.details_tabs)

            # General tab
            self.general_tab = self.create_general_tab()
            self.details_tabs.addTab(self.general_tab, "General")

            # Health tab
            self.health_tab = self.create_health_tab()
            self.details_tabs.addTab(self.health_tab, "Health")

            # Performance tab
            self.performance_tab = self.create_performance_tab()
            self.details_tabs.addTab(self.performance_tab, "Performance")

            return panel

        except Exception as e:
            error_handler.handle_error(
                e, "DiskHealthWidget.create_disk_details_panel"
            )
            return QWidget()

    def create_general_tab(self) -> QWidget:
        """Create general information tab.

        Returns:
            QWidget: General tab widget
        """
        try:
            tab = QWidget()
            layout = QVBoxLayout(tab)

            # Scroll area for details
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)

            # Content widget
            content = QWidget()
            content_layout = QVBoxLayout(content)

            # General information labels
            self.device_id_label = QLabel("Device ID: -")
            self.device_path_label = QLabel("Device Path: -")
            self.model_label = QLabel("Model: -")
            self.serial_label = QLabel("Serial Number: -")
            self.size_label = QLabel("Size: -")
            self.filesystem_label = QLabel("Filesystem: -")
            self.mount_point_label = QLabel("Mount Point: -")

            content_layout.addWidget(self.device_id_label)
            content_layout.addWidget(self.device_path_label)
            content_layout.addWidget(self.model_label)
            content_layout.addWidget(self.serial_label)
            content_layout.addWidget(self.size_label)
            content_layout.addWidget(self.filesystem_label)
            content_layout.addWidget(self.mount_point_label)
            content_layout.addStretch()

            scroll.setWidget(content)
            layout.addWidget(scroll)

            return tab

        except Exception as e:
            error_handler.handle_error(
                e, "DiskHealthWidget.create_general_tab"
            )
            return QWidget()

    def create_health_tab(self) -> QWidget:
        """Create health information tab.

        Returns:
            QWidget: Health tab widget
        """
        try:
            tab = QWidget()
            layout = QVBoxLayout(tab)

            # Health status
            health_group = QGroupBox("Health Status")
            health_layout = QVBoxLayout(health_group)

            self.health_status_label = QLabel("Status: Unknown")
            self.temperature_label = QLabel("Temperature: -")
            self.power_on_hours_label = QLabel("Power On Hours: -")

            health_layout.addWidget(self.health_status_label)
            health_layout.addWidget(self.temperature_label)
            health_layout.addWidget(self.power_on_hours_label)

            layout.addWidget(health_group)

            # Space usage (for logical disks)
            usage_group = QGroupBox("Space Usage")
            usage_layout = QVBoxLayout(usage_group)

            self.usage_progress = QProgressBar()
            self.usage_progress.setTextVisible(True)
            self.usage_label = QLabel("Used: 0 GB / 0 GB (0%)")

            usage_layout.addWidget(self.usage_progress)
            usage_layout.addWidget(self.usage_label)

            layout.addWidget(usage_group)
            layout.addStretch()

            return tab

        except Exception as e:
            error_handler.handle_error(e, "DiskHealthWidget.create_health_tab")
            return QWidget()

    def create_performance_tab(self) -> QWidget:
        """Create performance information tab.

        Returns:
            QWidget: Performance tab widget
        """
        try:
            tab = QWidget()
            layout = QVBoxLayout(tab)

            # I/O Statistics
            io_group = QGroupBox("I/O Statistics")
            io_layout = QVBoxLayout(io_group)

            self.reads_label = QLabel("Reads: -")
            self.writes_label = QLabel("Writes: -")
            self.read_bytes_label = QLabel("Bytes Read: -")
            self.write_bytes_label = QLabel("Bytes Written: -")

            io_layout.addWidget(self.reads_label)
            io_layout.addWidget(self.writes_label)
            io_layout.addWidget(self.read_bytes_label)
            io_layout.addWidget(self.write_bytes_label)

            layout.addWidget(io_group)
            layout.addStretch()

            return tab

        except Exception as e:
            error_handler.handle_error(
                e, "DiskHealthWidget.create_performance_tab"
            )
            return QWidget()

    def create_status_bar(self) -> QHBoxLayout:
        """Create status bar.

        Returns:
            QHBoxLayout: Status bar layout
        """
        try:
            status_layout = QHBoxLayout()

            # Status label
            self.status_label = QLabel("Ready")
            status_layout.addWidget(self.status_label)

            # Spacer
            status_layout.addStretch()

            # Last update label
            self.last_update_label = QLabel("Last Update: Never")
            status_layout.addWidget(self.last_update_label)

            return status_layout

        except Exception as e:
            error_handler.handle_error(e, "DiskHealthWidget.create_status_bar")
            return QHBoxLayout()

    def setup_styles(self):
        """Setup widget styles."""
        try:
            # Health status colors
            self.health_colors = {
                "healthy": "#4CAF50",  # Green
                "warning": "#FF9800",  # Orange
                "critical": "#F44336",  # Red
                "unknown": "#9E9E9E",  # Gray
            }

            # Apply styles to progress bars
            self.usage_progress.setStyleSheet(
                """
                QProgressBar {
                    border: 2px solid grey;
                    border-radius: 5px;
                    text-align: center;
                }
                QProgressBar::chunk {
                    background-color: #4CAF50;
                    border-radius: 3px;
                }
            """
            )

        except Exception as e:
            error_handler.handle_error(e, "DiskHealthWidget.setup_styles")

    def initialize_monitor(self):
        """Initialize disk monitor."""
        try:
            self.disk_monitor = DiskHealthMonitor()
            self.disk_monitor.start_monitoring()

            # Start auto-refresh
            self.update_timer.start()

            # Initial data load
            self.refresh_data()

        except Exception as e:
            error_handler.handle_error(
                e, "DiskHealthWidget.initialize_monitor"
            )
            self.status_label.setText(
                "Error: Failed to initialize disk monitor"
            )

    def refresh_data(self):
        """Refresh disk data."""
        try:
            if not self.disk_monitor:
                return

            self.status_label.setText("Refreshing...")

            # Get current data
            self.current_data = self.disk_monitor.get_current_data()

            # Update UI
            self.update_summary()
            self.update_disk_tree()

            # Update status
            self.status_label.setText("Ready")
            self.last_update_label.setText(
                f"Last Update: {datetime.now().strftime('%H:%M:%S')}"
            )

        except Exception as e:
            error_handler.handle_error(e, "DiskHealthWidget.refresh_data")
            self.status_label.setText("Error: Failed to refresh data")

    def update_summary(self):
        """Update summary section."""
        try:
            if not self.current_data:
                return

            summary = self.current_data.get("summary", {})

            total_physical = summary.get("total_physical_disks", 0)
            total_logical = summary.get("total_logical_disks", 0)
            total_disks = total_physical + total_logical

            healthy = summary.get("healthy_disks", 0)
            warning = summary.get("warning_disks", 0)
            critical = summary.get("critical_disks", 0)

            capacity_gb = summary.get("total_capacity_gb", 0)
            used_gb = summary.get("total_used_gb", 0)

            # Update labels
            self.total_disks_label.setText(f"Total Disks: {total_disks}")
            self.healthy_disks_label.setText(f"Healthy: {healthy}")
            self.warning_disks_label.setText(f"Warning: {warning}")
            self.critical_disks_label.setText(f"Critical: {critical}")
            self.total_capacity_label.setText(
                f"Total Capacity: {capacity_gb:.1f} GB"
            )
            self.total_used_label.setText(f"Total Used: {used_gb:.1f} GB")

            # Apply colors
            self.healthy_disks_label.setStyleSheet(
                f"color: {self.health_colors['healthy']}"
            )
            self.warning_disks_label.setStyleSheet(
                f"color: {self.health_colors['warning']}"
            )
            self.critical_disks_label.setStyleSheet(
                f"color: {self.health_colors['critical']}"
            )

        except Exception as e:
            error_handler.handle_error(e, "DiskHealthWidget.update_summary")

    def update_disk_tree(self):
        """Update disk tree."""
        try:
            self.disk_tree.clear()

            if not self.current_data:
                return

            # Add physical disks
            physical_disks = self.current_data.get("physical_disks", [])
            for disk in physical_disks:
                self.add_disk_to_tree(disk, "physical")

            # Add logical disks
            logical_disks = self.current_data.get("logical_disks", [])
            for disk in logical_disks:
                self.add_disk_to_tree(disk, "logical")

            # Expand all items
            self.disk_tree.expandAll()

            # Resize columns
            for i in range(self.disk_tree.columnCount()):
                self.disk_tree.resizeColumnToContents(i)

        except Exception as e:
            error_handler.handle_error(e, "DiskHealthWidget.update_disk_tree")

    def add_disk_to_tree(self, disk: Dict[str, Any], disk_type: str):
        """Add a disk to the tree.

        Args:
            disk: Disk information
            disk_type: Type of disk ('physical' or 'logical')
        """
        try:
            device_id = disk.get("device_id", "Unknown")
            size_bytes = disk.get("size_bytes", 0)
            health_status = disk.get("health_status", "unknown")

            # Format size
            size_str = self.format_bytes(size_bytes)

            # Format usage
            usage_str = "-"
            if disk_type == "logical":
                used_percent = disk.get("used_percent", 0)
                usage_str = f"{used_percent:.1f}%"

            # Create tree item
            item = QTreeWidgetItem(
                [
                    device_id,
                    disk_type.title(),
                    size_str,
                    health_status.title(),
                    usage_str,
                ]
            )

            # Store disk data
            item.setData(0, Qt.UserRole, (device_id, disk_type, disk))

            # Apply health color
            health_color = QColor(
                self.health_colors.get(health_status, "#9E9E9E")
            )
            item.setForeground(3, health_color)

            self.disk_tree.addTopLevelItem(item)

        except Exception as e:
            error_handler.handle_error(e, "DiskHealthWidget.add_disk_to_tree")

    def format_bytes(self, bytes_value: int) -> str:
        """Format bytes to human readable string.

        Args:
            bytes_value: Bytes value

        Returns:
            Formatted string
        """
        try:
            if bytes_value == 0:
                return "0 B"

            units = ["B", "KB", "MB", "GB", "TB", "PB"]
            unit_index = 0
            size = float(bytes_value)

            while size >= 1024 and unit_index < len(units) - 1:
                size /= 1024
                unit_index += 1

            return f"{size:.1f} {units[unit_index]}"

        except Exception as e:
            error_handler.handle_error(e, "DiskHealthWidget.format_bytes")
            return "Unknown"

    def on_disk_selected(self, item: QTreeWidgetItem, column: int):
        """Handle disk selection.

        Args:
            item: Selected tree item
            column: Selected column
        """
        try:
            data = item.data(0, Qt.UserRole)
            if data:
                device_id, disk_type, disk_info = data
                self.update_disk_details(device_id, disk_type, disk_info)
                self.disk_selected.emit(device_id, disk_type)

        except Exception as e:
            error_handler.handle_error(e, "DiskHealthWidget.on_disk_selected")

    def update_disk_details(
        self, device_id: str, disk_type: str, disk_info: Dict[str, Any]
    ):
        """Update disk details panel.

        Args:
            device_id: Device identifier
            disk_type: Type of disk
            disk_info: Disk information
        """
        try:
            # Update title
            self.details_title.setText(f"Details: {device_id} ({disk_type})")

            # Update general tab
            self.update_general_details(disk_info)

            # Update health tab
            self.update_health_details(disk_info)

            # Update performance tab
            self.update_performance_details(disk_info)

        except Exception as e:
            error_handler.handle_error(
                e, "DiskHealthWidget.update_disk_details"
            )

    def update_general_details(self, disk_info: Dict[str, Any]):
        """Update general details.

        Args:
            disk_info: Disk information
        """
        try:
            device_id = disk_info.get("device_id", "-")
            device_path = disk_info.get("device_path", "-")
            model = disk_info.get("model", "-")
            serial = disk_info.get("serial_number", "-")
            size = self.format_bytes(disk_info.get("size_bytes", 0))
            filesystem = disk_info.get("filesystem", "-")
            mount_point = disk_info.get("mount_point", "-")

            self.device_id_label.setText(f"Device ID: {device_id}")
            self.device_path_label.setText(f"Device Path: {device_path}")
            self.model_label.setText(f"Model: {model}")
            self.serial_label.setText(f"Serial Number: {serial}")
            self.size_label.setText(f"Size: {size}")
            self.filesystem_label.setText(f"Filesystem: {filesystem}")
            self.mount_point_label.setText(f"Mount Point: {mount_point}")

        except Exception as e:
            error_handler.handle_error(
                e, "DiskHealthWidget.update_general_details"
            )

    def update_health_details(self, disk_info: Dict[str, Any]):
        """Update health details.

        Args:
            disk_info: Disk information
        """
        try:
            health_status = disk_info.get("health_status", "unknown")
            temperature = disk_info.get("temperature", "-")
            power_on_hours = disk_info.get("power_on_hours", "-")

            # Update health status with color
            health_color = self.health_colors.get(health_status, "#9E9E9E")
            self.health_status_label.setText(
                f"Status: {health_status.title()}"
            )
            self.health_status_label.setStyleSheet(f"color: {health_color}")

            # Update temperature
            if isinstance(temperature, (int, float)):
                self.temperature_label.setText(f"Temperature: {temperature}°C")
            else:
                self.temperature_label.setText("Temperature: -")

            # Update power on hours
            if isinstance(power_on_hours, (int, float)):
                self.power_on_hours_label.setText(
                    f"Power On Hours: {power_on_hours:,}"
                )
            else:
                self.power_on_hours_label.setText("Power On Hours: -")

            # Update usage progress bar
            used_percent = disk_info.get("used_percent", 0)
            used_bytes = disk_info.get("used_bytes", 0)
            size_bytes = disk_info.get("size_bytes", 0)

            if size_bytes > 0:
                self.usage_progress.setValue(int(used_percent))
                used_str = self.format_bytes(used_bytes)
                total_str = self.format_bytes(size_bytes)
                self.usage_label.setText(
                    f"Used: {used_str} / {total_str} ({used_percent:.1f}%)"
                )

                # Update progress bar color based on usage
                if used_percent >= 90:
                    color = self.health_colors["critical"]
                elif used_percent >= 75:
                    color = self.health_colors["warning"]
                else:
                    color = self.health_colors["healthy"]

                self.usage_progress.setStyleSheet(
                    f"""
                    QProgressBar {{
                        border: 2px solid grey;
                        border-radius: 5px;
                        text-align: center;
                    }}
                    QProgressBar::chunk {{
                        background-color: {color};
                        border-radius: 3px;
                    }}
                """
                )
            else:
                self.usage_progress.setValue(0)
                self.usage_label.setText("Used: - / - (-%)")

        except Exception as e:
            error_handler.handle_error(
                e, "DiskHealthWidget.update_health_details"
            )

    def update_performance_details(self, disk_info: Dict[str, Any]):
        """Update performance details.

        Args:
            disk_info: Disk information
        """
        try:
            io_stats = disk_info.get("io_stats", {})

            if io_stats:
                reads = io_stats.get("reads_completed", "-")
                writes = io_stats.get("writes_completed", "-")
                sectors_read = io_stats.get("sectors_read", 0)
                sectors_written = io_stats.get("sectors_written", 0)

                # Convert sectors to bytes (assuming 512 bytes per sector)
                bytes_read = sectors_read * 512
                bytes_written = sectors_written * 512

                self.reads_label.setText(
                    f"Reads: {reads:,}"
                    if isinstance(reads, int)
                    else "Reads: -"
                )
                self.writes_label.setText(
                    f"Writes: {writes:,}"
                    if isinstance(writes, int)
                    else "Writes: -"
                )
                self.read_bytes_label.setText(
                    f"Bytes Read: {self.format_bytes(bytes_read)}"
                )
                self.write_bytes_label.setText(
                    f"Bytes Written: {self.format_bytes(bytes_written)}"
                )
            else:
                self.reads_label.setText("Reads: -")
                self.writes_label.setText("Writes: -")
                self.read_bytes_label.setText("Bytes Read: -")
                self.write_bytes_label.setText("Bytes Written: -")

        except Exception as e:
            error_handler.handle_error(
                e, "DiskHealthWidget.update_performance_details"
            )

    def toggle_auto_refresh(self):
        """Toggle auto-refresh."""
        try:
            if self.auto_refresh_button.isChecked():
                self.update_timer.start()
                self.auto_refresh_button.setText("Auto-Refresh: ON")
            else:
                self.update_timer.stop()
                self.auto_refresh_button.setText("Auto-Refresh: OFF")

        except Exception as e:
            error_handler.handle_error(
                e, "DiskHealthWidget.toggle_auto_refresh"
            )

    def closeEvent(self, event):
        """Handle widget close event.

        Args:
            event: Close event
        """
        try:
            # Stop timer
            self.update_timer.stop()

            # Stop monitor
            if self.disk_monitor:
                self.disk_monitor.stop_monitoring()

            event.accept()

        except Exception as e:
            error_handler.handle_error(e, "DiskHealthWidget.closeEvent")
            event.accept()


# Standalone application for testing
if __name__ == "__main__":
    if PYQT5_AVAILABLE:
        from PyQt5.QtWidgets import QApplication

        app = QApplication(sys.argv)
        widget = DiskHealthWidget()
        widget.show()
        sys.exit(app.exec_())
    else:
        print("PyQt5 is required to run the disk health widget")
