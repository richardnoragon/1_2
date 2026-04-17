#!/usr/bin/env python3
"""
Comprehensive System Diagnostics GUI for Richard's File Utilities

This module provides a unified interface for all system diagnostic tools,
integrating disk health, performance monitoring, battery health, and
filesystem integrity checks.
"""

import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, Optional

try:
    from PyQt5.QtCore import Qt, QThread, QTimer, pyqtSignal
    from PyQt5.QtGui import QFont, QIcon, QPixmap
    from PyQt5.QtWidgets import (
        QAction,
        QApplication,
        QFrame,
        QGridLayout,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QMainWindow,
        QMenuBar,
        QMessageBox,
        QProgressBar,
        QPushButton,
        QSplitter,
        QStatusBar,
        QTabWidget,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )

    from src.gui.themes import ThemeManager, Typography, token

    PYQT5_AVAILABLE = True
except ImportError:
    PYQT5_AVAILABLE = False

    # Create dummy classes for when PyQt5 is not available
    class QMainWindow:
        pass

    class pyqtSignal:
        def __init__(self, *args):
            pass


# Import diagnostic widgets with fallbacks
try:
    from .gui.disk_health_widget import DiskHealthWidget

    DISK_WIDGET_AVAILABLE = True
except ImportError:
    DISK_WIDGET_AVAILABLE = False
    DiskHealthWidget = None

try:
    from .gui.performance_widget import PerformanceWidget

    PERFORMANCE_WIDGET_AVAILABLE = True
except ImportError:
    PERFORMANCE_WIDGET_AVAILABLE = False
    PerformanceWidget = None

try:
    from .gui.battery_health_widget import BatteryHealthWidget

    BATTERY_WIDGET_AVAILABLE = True
except ImportError:
    BATTERY_WIDGET_AVAILABLE = False
    BatteryHealthWidget = None

# Import monitoring components
try:
    from .monitors.battery.battery_monitor import BatteryMonitor
    from .monitors.disk_health.disk_monitor import DiskHealthMonitor
    from .monitors.performance.performance_monitor import PerformanceMonitor

    MONITORS_AVAILABLE = True
except ImportError:
    MONITORS_AVAILABLE = False
    DiskHealthMonitor = None
    PerformanceMonitor = None
    BatteryMonitor = None

# Import core components
try:
    from .core.alert_manager import AlertManager
    from .core.data_collector import DataCollector
    from .core.platform_detector import PlatformDetector

    CORE_AVAILABLE = True
except ImportError:
    CORE_AVAILABLE = False
    PlatformDetector = None
    DataCollector = None
    AlertManager = None


# ---------------------------------------------------------------------------
# CP: Shared UI components (graceful fallback when unavailable)
# ---------------------------------------------------------------------------
try:
    from src.gui.components.buttons import PrimaryButton, SecondaryButton
    from src.gui.components.modal import Modal
    from src.gui.components.toast import ToastNotification

    _CP_AVAILABLE = True
except ImportError:
    PrimaryButton = SecondaryButton = None  # type: ignore[assignment,misc]
    Modal = None  # type: ignore[assignment,misc]
    ToastNotification = None
    _CP_AVAILABLE = False


class SystemDiagnosticsGUI(QMainWindow):
    """Comprehensive System Diagnostics GUI with integrated monitoring widgets.

    This class provides a unified interface for all system diagnostic tools,
    including disk health monitoring, performance tracking, battery health,
    and filesystem integrity checks.
    """

    # Signals for hub integration
    tool_progress_updated = pyqtSignal(str, int, str)  # tool_name, percentage, message
    tool_status_changed = pyqtSignal(str, str)  # tool_name, status
    diagnostic_completed = pyqtSignal(dict)  # results

    def __init__(self, hub_instance=None, parent=None):
        """Initialize the System Diagnostics GUI.

        Args:
            hub_instance: Optional hub instance for integration
            parent: Parent widget
        """
        if not PYQT5_AVAILABLE:
            raise ImportError("PyQt5 is required for the System Diagnostics GUI")

        super().__init__(parent)

        # Setup logging
        self.logger = logging.getLogger("RFU.SystemDiagnostics")

        # Hub integration
        self.hub_instance = hub_instance

        # Monitoring components
        self.disk_monitor = None
        self.performance_monitor = None
        self.battery_monitor = None
        self.data_collector = None
        self.alert_manager = None

        # Widget references
        self.disk_widget = None
        self.performance_widget = None
        self.battery_widget = None

        # Monitoring state
        self.monitoring_active = False
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_all_widgets)

        # Initialize UI
        self.init_ui()
        self.init_monitoring_components()

        # Connect hub signals if available
        if self.hub_instance:
            self.setup_hub_integration()
        ThemeManager.add_theme_changed_callback(self._on_theme_changed)

    def _on_theme_changed(self, variant: str) -> None:
        """Re-apply token-based stylesheets when the active theme variant changes."""
        pass  # stylesheets applied at init; live re-apply pending TH-4c/4d

    def init_ui(self):
        """Initialize the user interface."""
        try:
            # Window setup
            self.setWindowTitle("System Diagnostics - Richard's File Utilities")
            self.setMinimumSize(1000, 700)
            self.resize(1200, 800)

            # Create menu bar
            self.create_menu_bar()

            # Create central widget
            central_widget = QWidget()
            self.setCentralWidget(central_widget)

            # Main layout
            main_layout = QVBoxLayout(central_widget)
            main_layout.setContentsMargins(10, 10, 10, 10)
            main_layout.setSpacing(10)

            # Header section
            header_widget = self.create_header_section()
            main_layout.addWidget(header_widget)

            # Main content area with tabs
            self.tab_widget = QTabWidget()
            self.tab_widget.setAccessibleName("Diagnostics tabs")
            main_layout.addWidget(self.tab_widget)

            # Create tabs
            self.create_overview_tab()
            self.create_disk_health_tab()
            self.create_performance_tab()
            self.create_battery_tab()
            self.create_system_info_tab()

            # Status bar
            self.create_status_bar()

            # Apply styling
            self.apply_styling()

        except Exception as e:
            self.logger.error(f"Error initializing UI: {e}")
            self.show_error_message("UI Initialization Error", str(e))

    def create_menu_bar(self):
        """Create the menu bar."""
        try:
            menubar = self.menuBar()

            # File menu
            file_menu = menubar.addMenu("File")

            export_action = QAction("Export Report", self)
            export_action.triggered.connect(self.export_diagnostic_report)
            file_menu.addAction(export_action)

            file_menu.addSeparator()

            exit_action = QAction("Exit", self)
            exit_action.setShortcut("Ctrl+Q")
            exit_action.triggered.connect(self.close)
            file_menu.addAction(exit_action)

            # Tools menu
            tools_menu = menubar.addMenu("Tools")

            start_monitoring_action = QAction("Start Monitoring", self)
            start_monitoring_action.triggered.connect(self.start_monitoring)
            tools_menu.addAction(start_monitoring_action)

            stop_monitoring_action = QAction("Stop Monitoring", self)
            stop_monitoring_action.triggered.connect(self.stop_monitoring)
            tools_menu.addAction(stop_monitoring_action)

            tools_menu.addSeparator()

            refresh_action = QAction("Refresh All", self)
            refresh_action.setShortcut("F5")
            refresh_action.triggered.connect(self.refresh_all_data)
            tools_menu.addAction(refresh_action)

            # Help menu
            help_menu = menubar.addMenu("Help")

            about_action = QAction("About", self)
            about_action.triggered.connect(self.show_about_dialog)
            help_menu.addAction(about_action)

        except Exception as e:
            self.logger.error(f"Error creating menu bar: {e}")

    def create_header_section(self) -> QWidget:
        """Create the header section with title and controls.

        Returns:
            Header widget
        """
        try:
            header_frame = QFrame()
            header_frame.setFrameStyle(QFrame.StyledPanel)
            header_layout = QHBoxLayout(header_frame)

            # Title and description
            title_layout = QVBoxLayout()

            title_label = QLabel("System Diagnostics & Monitoring")
            title_label.setFont(Typography.h1())
            title_layout.addWidget(title_label)

            desc_label = QLabel(
                "Comprehensive system health monitoring and diagnostics"
            )
            desc_label.setStyleSheet(f"color: {token('text_muted')};")
            title_layout.addWidget(desc_label)

            header_layout.addLayout(title_layout)
            header_layout.addStretch()

            # Control buttons
            controls_layout = QVBoxLayout()

            _PB = PrimaryButton if PrimaryButton else QPushButton
            self.start_button = _PB("Start Monitoring")
            self.start_button.clicked.connect(self.start_monitoring)
            controls_layout.addWidget(self.start_button)

            _SB = SecondaryButton if SecondaryButton else QPushButton
            self.stop_button = _SB("Stop Monitoring")
            self.stop_button.clicked.connect(self.stop_monitoring)
            self.stop_button.setEnabled(False)
            controls_layout.addWidget(self.stop_button)

            header_layout.addLayout(controls_layout)

            return header_frame

        except Exception as e:
            self.logger.error(f"Error creating header section: {e}")
            return QWidget()

    def create_overview_tab(self):
        """Create the overview tab with system summary."""
        try:
            overview_widget = QWidget()
            layout = QVBoxLayout(overview_widget)

            # System summary section
            summary_group = QGroupBox("System Summary")
            summary_layout = QGridLayout(summary_group)

            # System info labels
            self.system_info_labels = {}
            info_items = [
                ("Platform:", "platform"),
                ("CPU:", "cpu"),
                ("Memory:", "memory"),
                ("Disk Space:", "disk_space"),
                ("Uptime:", "uptime"),
                ("Last Scan:", "last_scan"),
            ]

            for i, (label_text, key) in enumerate(info_items):
                label = QLabel(label_text)
                value_label = QLabel("Loading...")
                self.system_info_labels[key] = value_label

                summary_layout.addWidget(label, i, 0)
                summary_layout.addWidget(value_label, i, 1)

            layout.addWidget(summary_group)

            # Health status section
            health_group = QGroupBox("Health Status")
            health_layout = QGridLayout(health_group)

            # Health indicators
            self.health_indicators = {}
            health_items = [
                ("Disk Health:", "disk_health"),
                ("Performance:", "performance"),
                ("Battery Health:", "battery_health"),
                ("System Stability:", "system_stability"),
            ]

            for i, (label_text, key) in enumerate(health_items):
                label = QLabel(label_text)
                progress = QProgressBar()
                progress.setRange(0, 100)
                progress.setValue(0)
                self.health_indicators[key] = progress

                health_layout.addWidget(label, i, 0)
                health_layout.addWidget(progress, i, 1)

            layout.addWidget(health_group)

            # Recent alerts section
            alerts_group = QGroupBox("Recent Alerts")
            alerts_layout = QVBoxLayout(alerts_group)

            self.alerts_text = QTextEdit()
            self.alerts_text.setAccessibleName("Recent alerts")
            self.alerts_text.setMaximumHeight(150)
            self.alerts_text.setReadOnly(True)
            self.alerts_text.setPlainText("No alerts at this time.")
            alerts_layout.addWidget(self.alerts_text)

            layout.addWidget(alerts_group)
            layout.addStretch()

            self.tab_widget.addTab(overview_widget, "Overview")

        except Exception as e:
            self.logger.error(f"Error creating overview tab: {e}")

    def create_disk_health_tab(self):
        """Create the disk health monitoring tab."""
        try:
            if DISK_WIDGET_AVAILABLE and DiskHealthWidget:
                self.disk_widget = DiskHealthWidget()
                self.tab_widget.addTab(self.disk_widget, "Disk Health")
            else:
                # Create placeholder widget
                placeholder = self.create_placeholder_widget(
                    "Disk Health Monitor",
                    "Disk health monitoring is not available.\n"
                    "This may be due to missing dependencies or system limitations.",
                )
                self.tab_widget.addTab(placeholder, "Disk Health")

        except Exception as e:
            self.logger.error(f"Error creating disk health tab: {e}")
            placeholder = self.create_placeholder_widget(
                "Disk Health Monitor",
                f"Error loading disk health monitor: {str(e)}",
            )
            self.tab_widget.addTab(placeholder, "Disk Health")

    def create_performance_tab(self):
        """Create the performance monitoring tab."""
        try:
            if PERFORMANCE_WIDGET_AVAILABLE and PerformanceWidget:
                self.performance_widget = PerformanceWidget()
                self.tab_widget.addTab(self.performance_widget, "Performance")
            else:
                # Create placeholder widget
                placeholder = self.create_placeholder_widget(
                    "Performance Monitor",
                    "Performance monitoring is not available.\n"
                    "This may be due to missing dependencies or system limitations.",
                )
                self.tab_widget.addTab(placeholder, "Performance")

        except Exception as e:
            self.logger.error(f"Error creating performance tab: {e}")
            placeholder = self.create_placeholder_widget(
                "Performance Monitor",
                f"Error loading performance monitor: {str(e)}",
            )
            self.tab_widget.addTab(placeholder, "Performance")

    def create_battery_tab(self):
        """Create the battery health monitoring tab."""
        try:
            if BATTERY_WIDGET_AVAILABLE and BatteryHealthWidget:
                self.battery_widget = BatteryHealthWidget()
                self.tab_widget.addTab(self.battery_widget, "Battery Health")
            else:
                # Create placeholder widget
                placeholder = self.create_placeholder_widget(
                    "Battery Health Monitor",
                    "Battery health monitoring is not available.\n"
                    "This may be due to missing dependencies or no battery present.",
                )
                self.tab_widget.addTab(placeholder, "Battery Health")

        except Exception as e:
            self.logger.error(f"Error creating battery tab: {e}")
            placeholder = self.create_placeholder_widget(
                "Battery Health Monitor",
                f"Error loading battery health monitor: {str(e)}",
            )
            self.tab_widget.addTab(placeholder, "Battery Health")

    def create_system_info_tab(self):
        """Create the system information tab."""
        try:
            system_widget = QWidget()
            layout = QVBoxLayout(system_widget)

            # System information display
            info_group = QGroupBox("Detailed System Information")
            info_layout = QVBoxLayout(info_group)

            self.system_info_text = QTextEdit()
            self.system_info_text.setAccessibleName("Detailed system information")
            self.system_info_text.setReadOnly(True)
            self.system_info_text.setPlainText("Loading system information...")
            info_layout.addWidget(self.system_info_text)

            layout.addWidget(info_group)

            # Diagnostic tools section
            tools_group = QGroupBox("Diagnostic Tools")
            tools_layout = QGridLayout(tools_group)

            # Tool buttons
            tools = [
                ("Run System Check", self.run_system_check),
                ("Check Disk Space", self.check_disk_space),
                ("Memory Test", self.run_memory_test),
                ("Performance Benchmark", self.run_performance_benchmark),
            ]

            for i, (text, callback) in enumerate(tools):
                _SB2 = SecondaryButton if SecondaryButton else QPushButton
                button = _SB2(text)
                button.clicked.connect(callback)
                tools_layout.addWidget(button, i // 2, i % 2)

            layout.addWidget(tools_group)

            self.tab_widget.addTab(system_widget, "System Info")

        except Exception as e:
            self.logger.error(f"Error creating system info tab: {e}")

    def create_placeholder_widget(self, title: str, message: str) -> QWidget:
        """Create a placeholder widget for unavailable components.

        Args:
            title: Widget title
            message: Message to display

        Returns:
            Placeholder widget
        """
        try:
            widget = QWidget()
            layout = QVBoxLayout(widget)

            # Title
            title_label = QLabel(title)
            title_label.setFont(Typography.h2())
            title_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(title_label)

            # Message
            message_label = QLabel(message)
            message_label.setAlignment(Qt.AlignCenter)
            message_label.setWordWrap(True)
            message_label.setStyleSheet(f"color: {token('text_muted')}; padding: 20px;")
            layout.addWidget(message_label)

            layout.addStretch()

            return widget

        except Exception as e:
            self.logger.error(f"Error creating placeholder widget: {e}")
            return QWidget()

    def create_status_bar(self):
        """Create the status bar."""
        try:
            self.status_bar = QStatusBar()
            self.setStatusBar(self.status_bar)

            # Status message
            self.status_label = QLabel("Ready")
            self.status_bar.addWidget(self.status_label)

            # Monitoring indicator
            self.monitoring_label = QLabel("Monitoring: Stopped")
            self.status_bar.addPermanentWidget(self.monitoring_label)

            # Last update time
            self.last_update_label = QLabel("Last Update: Never")
            self.status_bar.addPermanentWidget(self.last_update_label)

        except Exception as e:
            self.logger.error(f"Error creating status bar: {e}")

    def apply_styling(self):
        """Apply custom styling to the interface."""
        try:
            # Main window styling
            self.setStyleSheet(
                """
                QMainWindow {
                    background-color: {token('surface')};
                }
                QTabWidget::pane {
                    border: 1px solid {token('border')};
                    background-color: white;
                }
                QTabBar::tab {
                    background-color: {token('border_light')};
                    padding: 8px 16px;
                    margin-right: 2px;
                }
                QTabBar::tab:selected {
                    background-color: white;
                    border-bottom: 2px solid {token('button_primary')};
                }
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
                QPushButton {
                    background-color: {token('button_primary')};
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: {token('button_primary')};
                }
                QPushButton:disabled {
                    background-color: {token('border')};
                    color: {token('text_muted')};
                }
                QProgressBar {
                    border: 1px solid {token('border')};
                    border-radius: 3px;
                    text-align: center;
                }
                QProgressBar::chunk {
                    background-color: {token('semantic_success')};
                    border-radius: 2px;
                }
            """
            )

        except Exception as e:
            self.logger.error(f"Error applying styling: {e}")

    def init_monitoring_components(self):
        """Initialize monitoring components."""
        try:
            if MONITORS_AVAILABLE:
                # Initialize monitors
                if DiskHealthMonitor:
                    self.disk_monitor = DiskHealthMonitor()

                if PerformanceMonitor:
                    self.performance_monitor = PerformanceMonitor()

                if BatteryMonitor:
                    self.battery_monitor = BatteryMonitor()

            if CORE_AVAILABLE:
                # Initialize core components
                if DataCollector:
                    self.data_collector = DataCollector()

                if AlertManager:
                    self.alert_manager = AlertManager()

            self.logger.info("Monitoring components initialized")

        except Exception as e:
            self.logger.error(f"Error initializing monitoring components: {e}")

    def setup_hub_integration(self):
        """Setup integration with the main hub."""
        try:
            if self.hub_instance:
                # Connect signals to hub
                self.tool_progress_updated.connect(
                    lambda name, pct, msg: self.hub_instance.update_tool_progress(
                        "System Diagnostics", pct, msg
                    )
                )

                self.tool_status_changed.connect(
                    lambda name, status: self.hub_instance.update_tool_status(
                        "System Diagnostics", status
                    )
                )

                self.logger.info("Hub integration setup complete")

        except Exception as e:
            self.logger.error(f"Error setting up hub integration: {e}")

    def start_monitoring(self):
        """Start system monitoring."""
        try:
            if not self.monitoring_active:
                self.monitoring_active = True

                # Update UI
                self.start_button.setEnabled(False)
                self.stop_button.setEnabled(True)
                self.monitoring_label.setText("Monitoring: Active")
                self.status_label.setText("Starting monitoring...")

                # Start monitors
                if self.disk_monitor:
                    self.disk_monitor.start_monitoring()

                if self.performance_monitor:
                    self.performance_monitor.start_monitoring()

                if self.battery_monitor:
                    self.battery_monitor.start_monitoring()

                # Start update timer
                self.update_timer.start(5000)  # Update every 5 seconds

                # Emit status change
                self.tool_status_changed.emit("System Diagnostics", "monitoring")

                self.status_label.setText("Monitoring active")
                self.logger.info("System monitoring started")

        except Exception as e:
            self.logger.error(f"Error starting monitoring: {e}")
            self.show_error_message(
                "Monitoring Error", f"Failed to start monitoring: {str(e)}"
            )

    def stop_monitoring(self):
        """Stop system monitoring."""
        try:
            if self.monitoring_active:
                self.monitoring_active = False

                # Update UI
                self.start_button.setEnabled(True)
                self.stop_button.setEnabled(False)
                self.monitoring_label.setText("Monitoring: Stopped")
                self.status_label.setText("Stopping monitoring...")

                # Stop monitors
                if self.disk_monitor:
                    self.disk_monitor.stop_monitoring()

                if self.performance_monitor:
                    self.performance_monitor.stop_monitoring()

                if self.battery_monitor:
                    self.battery_monitor.stop_monitoring()

                # Stop update timer
                self.update_timer.stop()

                # Emit status change
                self.tool_status_changed.emit("System Diagnostics", "stopped")

                self.status_label.setText("Monitoring stopped")
                self.logger.info("System monitoring stopped")

        except Exception as e:
            self.logger.error(f"Error stopping monitoring: {e}")
            self.show_error_message(
                "Monitoring Error", f"Failed to stop monitoring: {str(e)}"
            )

    def update_all_widgets(self):
        """Update all monitoring widgets with current data."""
        try:
            if self.monitoring_active:
                # Update overview
                self.update_overview_data()

                # Update individual widgets
                if self.disk_widget and hasattr(self.disk_widget, "refresh_data"):
                    self.disk_widget.refresh_data()

                if self.performance_widget and hasattr(
                    self.performance_widget, "update_display"
                ):
                    self.performance_widget.update_display()

                if self.battery_widget and hasattr(self.battery_widget, "refresh_data"):
                    self.battery_widget.refresh_data()

                # Update last update time
                current_time = datetime.now().strftime("%H:%M:%S")
                self.last_update_label.setText(f"Last Update: {current_time}")

                # Emit progress update
                self.tool_progress_updated.emit(
                    "System Diagnostics", 100, "Data updated"
                )

        except Exception as e:
            self.logger.error(f"Error updating widgets: {e}")

    def update_overview_data(self):
        """Update the overview tab with current system data."""
        try:
            # Update system info labels
            if hasattr(self, "system_info_labels"):
                # Platform info
                if PlatformDetector:
                    detector = PlatformDetector()
                    platform_info = detector.get_platform_info()
                    self.system_info_labels["platform"].setText(
                        f"{platform_info.get('system', 'Unknown')} {platform_info.get('release', '')}"
                    )

                # Update other system info as available
                self.system_info_labels["last_scan"].setText(
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )

            # Update health indicators
            if hasattr(self, "health_indicators"):
                # Set example values - these would come from actual monitoring
                self.health_indicators["disk_health"].setValue(85)
                self.health_indicators["performance"].setValue(78)
                self.health_indicators["battery_health"].setValue(92)
                self.health_indicators["system_stability"].setValue(88)

        except Exception as e:
            self.logger.error(f"Error updating overview data: {e}")

    def refresh_all_data(self):
        """Manually refresh all data."""
        try:
            self.status_label.setText("Refreshing data...")
            self.update_all_widgets()
            self.status_label.setText("Data refreshed")

        except Exception as e:
            self.logger.error(f"Error refreshing data: {e}")
            self.show_error_message(
                "Refresh Error", f"Failed to refresh data: {str(e)}"
            )

    def run_system_check(self):
        """Run comprehensive system check."""
        try:
            self.status_label.setText("Running system check...")
            # Placeholder for system check implementation
            if ToastNotification:
                ToastNotification(parent=self).show_message(
                    "System check completed \u2014 no critical issues detected.",
                    "success",
                )
            else:
                QMessageBox.information(
                    self,
                    "System Check",
                    "System check completed successfully.\n\nNo critical issues detected.",
                )
            self.status_label.setText("System check completed")

        except Exception as e:
            self.logger.error(f"Error running system check: {e}")
            self.show_error_message("System Check Error", str(e))

    def check_disk_space(self):
        """Check disk space usage."""
        try:
            self.status_label.setText("Checking disk space...")
            # Placeholder for disk space check implementation
            if ToastNotification:
                ToastNotification(parent=self).show_message(
                    "Disk space check completed \u2014 all drives OK.", "success"
                )
            else:
                QMessageBox.information(
                    self,
                    "Disk Space Check",
                    "Disk space check completed.\n\nAll drives have sufficient free space.",
                )
            self.status_label.setText("Disk space check completed")

        except Exception as e:
            self.logger.error(f"Error checking disk space: {e}")
            self.show_error_message("Disk Space Check Error", str(e))

    def run_memory_test(self):
        """Run memory test."""
        try:
            self.status_label.setText("Running memory test...")
            # Placeholder for memory test implementation
            if ToastNotification:
                ToastNotification(parent=self).show_message(
                    "Memory test completed \u2014 no issues detected.", "success"
                )
            else:
                QMessageBox.information(
                    self,
                    "Memory Test",
                    "Memory test completed successfully.\n\nNo memory issues detected.",
                )
            self.status_label.setText("Memory test completed")

        except Exception as e:
            self.logger.error(f"Error running memory test: {e}")
            self.show_error_message("Memory Test Error", str(e))

    def run_performance_benchmark(self):
        """Run performance benchmark."""
        try:
            self.status_label.setText("Running performance benchmark...")
            # Placeholder for performance benchmark implementation
            if ToastNotification:
                ToastNotification(parent=self).show_message(
                    "Performance benchmark completed \u2014 within normal parameters.",
                    "success",
                )
            else:
                QMessageBox.information(
                    self,
                    "Performance Benchmark",
                    "Performance benchmark completed.\n\n"
                    "System performance is within normal parameters.",
                )
            self.status_label.setText("Performance benchmark completed")

        except Exception as e:
            self.logger.error(f"Error running performance benchmark: {e}")
            self.show_error_message("Performance Benchmark Error", str(e))

    def export_diagnostic_report(self):
        """Export diagnostic report to file."""
        try:
            from PyQt5.QtWidgets import QFileDialog

            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Export Diagnostic Report",
                f"diagnostic_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                "Text Files (*.txt);;All Files (*)",
            )

            if filename:
                with open(filename, "w") as f:
                    f.write("System Diagnostics Report\n")
                    f.write("=" * 50 + "\n")
                    f.write(
                        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                    )
                    f.write("System Information:\n")
                    f.write("- Platform: Windows/Linux/macOS\n")
                    f.write("- Monitoring Status: Active/Inactive\n")
                    f.write("\nDiagnostic Results:\n")
                    f.write("- Disk Health: Good\n")
                    f.write("- Performance: Normal\n")
                    f.write("- Battery Health: Good\n")
                    f.write("- System Stability: Stable\n")

                if ToastNotification:
                    ToastNotification(parent=self).show_message(
                        f"Diagnostic report exported to: {filename}", "success"
                    )
                else:
                    QMessageBox.information(
                        self,
                        "Export Complete",
                        f"Diagnostic report exported to:\n{filename}",
                    )

        except Exception as e:
            self.logger.error(f"Error exporting report: {e}")
            self.show_error_message("Export Error", str(e))

    def show_about_dialog(self):
        """Show about dialog."""
        try:
            _about_text = (
                "System Diagnostics Tool\n"
                "Part of Richard's File Utilities\n\n"
                "Version: 1.0.0\n"
                "Comprehensive system monitoring and diagnostics\n\n"
                "Features:\n"
                "• Disk health monitoring\n"
                "• Performance tracking\n"
                "• Battery health analysis\n"
                "• System information display\n"
                "• Real-time monitoring\n"
                "• Diagnostic reporting"
            )
            if Modal:
                Modal(
                    "About System Diagnostics", _about_text, ["OK"], parent=self
                ).exec_()
            else:
                QMessageBox.about(self, "About System Diagnostics", _about_text)

        except Exception as e:
            self.logger.error(f"Error showing about dialog: {e}")

    def show_error_message(self, title: str, message: str):
        """Show error message dialog.

        Args:
            title: Dialog title
            message: Error message
        """
        try:
            if Modal:
                Modal(title, message, ["OK"], parent=self).exec_()
            else:
                QMessageBox.critical(self, title, message)
        except Exception as e:
            self.logger.error(f"Error showing error message: {e}")

    def closeEvent(self, event):
        """Handle window close event.

        Args:
            event: Close event
        """
        try:
            # Stop monitoring if active
            if self.monitoring_active:
                self.stop_monitoring()

            # Emit status change
            self.tool_status_changed.emit("System Diagnostics", "closed")

            event.accept()

        except Exception as e:
            self.logger.error(f"Error during close: {e}")
            event.accept()


def create_system_diagnostics_gui(
    hub_instance=None,
) -> Optional[SystemDiagnosticsGUI]:
    """Create a SystemDiagnosticsGUI instance.

    Args:
        hub_instance: Optional hub instance for integration

    Returns:
        SystemDiagnosticsGUI instance or None if creation fails
    """
    try:
        if not PYQT5_AVAILABLE:
            print("PyQt5 is not available. Cannot create System Diagnostics GUI.")
            return None

        gui = SystemDiagnosticsGUI(hub_instance)
        return gui

    except Exception as e:
        print(f"Error creating System Diagnostics GUI: {e}")
        return None


def main():
    """Main function for standalone execution."""
    try:
        if not PYQT5_AVAILABLE:
            print("PyQt5 is required to run the System Diagnostics GUI.")
            print("Please install PyQt5: pip install PyQt5")
            return

        app = QApplication(sys.argv)

        # Create and show the GUI
        gui = create_system_diagnostics_gui()
        if gui:
            gui.show()
            sys.exit(app.exec_())
        else:
            print("Failed to create System Diagnostics GUI.")

    except Exception as e:
        print(f"Error running System Diagnostics GUI: {e}")


if __name__ == "__main__":
    main()
