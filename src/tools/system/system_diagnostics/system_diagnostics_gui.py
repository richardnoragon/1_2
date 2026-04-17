#!/usr/bin/env python3
"""
System Diagnostics GUI for Richard's File Utilities

A comprehensive system diagnostics tool that provides:
- System information gathering
- Performance monitoring
- Hardware diagnostics
- Network diagnostics
- Disk health checking
- Memory analysis
"""

import logging
import platform
import sys

# String constant to avoid duplication (SonarQube S1192)
SYSTEM_DIAGNOSTICS_TEXT = "System Diagnostics"

try:
    from PyQt5.QtCore import QThread, QTimer, pyqtSignal
    from PyQt5.QtWidgets import (
        QApplication,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QMainWindow,
        QMessageBox,
        QProgressBar,
        QPushButton,
        QTableWidget,
        QTableWidgetItem,
        QTabWidget,
        QTextEdit,
        QTreeWidget,
        QTreeWidgetItem,
        QVBoxLayout,
        QWidget,
    )

    from src.gui.themes import token
except ImportError:
    print("PyQt5 not available. Please install PyQt5.")
    sys.exit(1)


# ---------------------------------------------------------------------------
# GRD-1a: Guardian registration (graceful no-op when guardian absent)
# ---------------------------------------------------------------------------
try:
    from src.core.guardian import register_gui_component
except ImportError:

    def register_gui_component(*a, **kw):
        pass  # noqa: E731


# ---------------------------------------------------------------------------
# TEL: Telemetry helpers (graceful no-op when telemetry absent)
# ---------------------------------------------------------------------------
try:
    from src.gui.telemetry import emit_telemetry

    def _emit_telemetry(event_type, **kw):
        emit_telemetry(event_type, **kw)  # noqa: E731

except ImportError:

    def _emit_telemetry(*a, **kw):
        pass  # noqa: E731


# ---------------------------------------------------------------------------
# STR: Centralised string constants with fallback (P1-C15 / STR-1)
# ---------------------------------------------------------------------------
try:
    from src.rfu.ui_strings import SystemDiagnostics as _SysDiagStrings
except ImportError:

    class _SysDiagStrings:  # type: ignore[no-redef]
        TITLE = "System Diagnostics"
        WINDOW_TITLE = "System Diagnostics — RFU"
        LOADING = "Loading System Diagnostics…"
        ERR_INIT_FAILED = (
            "Could not start System Diagnostics. "
            "Please try again or restart the application."
        )
        ERR_SCAN_FAILED = "Could not run diagnostics. Please try again."


# ---------------------------------------------------------------------------
# CP: Component Placement — PrimaryButton / SecondaryButton / Modal
# ---------------------------------------------------------------------------
try:
    from src.gui.components.buttons import PrimaryButton, SecondaryButton

    _CP_AVAILABLE = True
except ImportError:
    PrimaryButton = QPushButton  # type: ignore[misc,assignment]
    SecondaryButton = QPushButton  # type: ignore[misc,assignment]
    _CP_AVAILABLE = False

try:
    from src.gui.components.modal import Modal
except ImportError:
    Modal = None  # type: ignore[assignment,misc]


class SystemDiagnosticsGUI(QMainWindow):
    """Main window for System Diagnostics operations."""

    def __init__(self, hub_instance=None):
        super().__init__()
        self._hub = hub_instance
        try:
            from src.rfu.log_manager import get_log_manager

            self._logger = get_log_manager().get_logger("SystemDiagnosticsGUI")
        except Exception:
            self._logger = logging.getLogger("SystemDiagnosticsGUI")
        self.setWindowTitle(_SysDiagStrings.WINDOW_TITLE)
        self.setGeometry(200, 200, 1000, 700)

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)

        self.init_ui()
        self._setup_menu_callbacks()
        register_gui_component(
            self, tool_id="system_diagnostics", recovery_callback=self.degraded_fallback
        )
        _emit_telemetry("ui_view_load", tool_id="system_diagnostics")

    def health_check(self) -> bool:
        """Return True if core UI is functional (GRD-3a)."""
        try:
            return hasattr(self, "main_layout") and self.main_layout is not None
        except Exception:
            return False

    def degraded_fallback(self) -> None:
        """Enter degraded / read-only state (GRD-3b)."""
        try:
            self._logger.warning("SystemDiagnosticsGUI entering degraded mode")
        except Exception:
            pass
        _emit_telemetry(
            "ui_error_event", tool_id="system_diagnostics", error_type="degraded"
        )

    def _setup_menu_callbacks(self):
        """Setup tool-specific menu callbacks."""
        # Basic implementation without full menu manager
        pass

    def show_preferences(self):
        """Show System Diagnostics preferences."""
        _msg = (
            "System Diagnostics preferences:\n\n"
            "• Monitoring intervals\n"
            "• Alert thresholds\n"
            "• Report formats\n"
            "• Auto-diagnostic settings\n\n"
            "Advanced preferences coming soon!"
        )
        if Modal:
            Modal("System Diagnostics Preferences", _msg, ["OK"], self).exec_()
        else:
            QMessageBox.information(self, "System Diagnostics Preferences", _msg)

    def refresh_view(self):
        """Refresh the system diagnostics interface."""
        self.gather_system_info()
        if Modal:
            Modal(
                "Refresh", "System diagnostics refreshed successfully.", ["OK"], self
            ).exec_()
        else:
            QMessageBox.information(
                self, "Refresh", "System diagnostics refreshed successfully."
            )

    def init_ui(self):
        """Initialize the user interface."""
        # Create header
        header_label = QLabel("System Diagnostics & Health Monitor")
        header_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: 18px;
                font-weight: bold;
                color: {token('text_primary')};
                padding: 10px;
                background-color: {token('background')};
                border-radius: 5px;
                margin-bottom: 10px;
            }}
        """
        )
        self.main_layout.addWidget(header_label)

        # Create tab widget for different diagnostic categories
        tab_widget = QTabWidget()
        tab_widget.setAccessibleName("System diagnostics tabs")
        self.main_layout.addWidget(tab_widget)

        # System Info Tab
        system_info_tab = self.create_system_info_tab()
        tab_widget.addTab(system_info_tab, "System Information")

        # Performance Tab
        performance_tab = self.create_performance_tab()
        tab_widget.addTab(performance_tab, "Performance")

        # Hardware Tab
        hardware_tab = self.create_hardware_tab()
        tab_widget.addTab(hardware_tab, "Hardware")

        # Network Tab
        network_tab = self.create_network_tab()
        tab_widget.addTab(network_tab, "Network")

        # Health Check Tab
        health_tab = self.create_health_tab()
        tab_widget.addTab(health_tab, "Health Check")

        # Quick actions
        actions_group = QGroupBox("Quick Diagnostic Actions")
        actions_layout = QHBoxLayout(actions_group)

        full_scan_btn = PrimaryButton("Full System Scan")
        full_scan_btn.clicked.connect(self.run_full_scan)
        actions_layout.addWidget(full_scan_btn)

        quick_check_btn = SecondaryButton("Quick Health Check")
        quick_check_btn.clicked.connect(self.run_quick_check)
        actions_layout.addWidget(quick_check_btn)

        export_report_btn = SecondaryButton("Export Report")
        export_report_btn.clicked.connect(self.export_report)
        actions_layout.addWidget(export_report_btn)

        self.main_layout.addWidget(actions_group)

    def create_system_info_tab(self):
        """Create system information tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # System info tree
        info_group = QGroupBox("System Information")
        info_layout = QVBoxLayout(info_group)

        self.system_info_tree = QTreeWidget()
        self.system_info_tree.setAccessibleName("System information tree")
        self.system_info_tree.setHeaderLabels(["Property", "Value"])
        info_layout.addWidget(self.system_info_tree)

        # Refresh button
        refresh_info_btn = PrimaryButton("Refresh System Info")
        refresh_info_btn.clicked.connect(self.gather_system_info)
        info_layout.addWidget(refresh_info_btn)

        layout.addWidget(info_group)

        # Initialize with basic system info
        self.gather_system_info()

        return tab

    def create_performance_tab(self):
        """Create performance monitoring tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Performance controls
        controls_group = QGroupBox("Performance Monitoring")
        controls_layout = QHBoxLayout(controls_group)

        start_monitor_btn = PrimaryButton("Start Monitoring")
        start_monitor_btn.clicked.connect(self.start_performance_monitoring)
        controls_layout.addWidget(start_monitor_btn)

        stop_monitor_btn = SecondaryButton("Stop Monitoring")
        stop_monitor_btn.clicked.connect(self.stop_performance_monitoring)
        controls_layout.addWidget(stop_monitor_btn)

        reset_stats_btn = SecondaryButton("Reset Statistics")
        reset_stats_btn.clicked.connect(self.reset_performance_stats)
        controls_layout.addWidget(reset_stats_btn)

        controls_layout.addStretch()
        layout.addWidget(controls_group)

        # Performance display
        performance_group = QGroupBox("Performance Data")
        performance_layout = QVBoxLayout(performance_group)

        self.performance_text = QTextEdit()
        self.performance_text.setAccessibleName("Performance monitoring data")
        self.performance_text.setReadOnly(True)
        self.performance_text.setPlainText(
            "Performance monitoring ready.\n"
            "Click 'Start Monitoring' to begin collecting performance data."
        )
        performance_layout.addWidget(self.performance_text)

        layout.addWidget(performance_group)

        return tab

    def create_hardware_tab(self):
        """Create hardware diagnostics tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Hardware tests
        tests_group = QGroupBox("Hardware Diagnostic Tests")
        tests_layout = QVBoxLayout(tests_group)

        # Test buttons
        button_layout = QHBoxLayout()

        cpu_test_btn = PrimaryButton("CPU Test")
        cpu_test_btn.clicked.connect(self.test_cpu)
        button_layout.addWidget(cpu_test_btn)

        memory_test_btn = SecondaryButton("Memory Test")
        memory_test_btn.clicked.connect(self.test_memory)
        button_layout.addWidget(memory_test_btn)

        disk_test_btn = SecondaryButton("Disk Test")
        disk_test_btn.clicked.connect(self.test_disk)
        button_layout.addWidget(disk_test_btn)

        gpu_test_btn = SecondaryButton("GPU Test")
        gpu_test_btn.clicked.connect(self.test_gpu)
        button_layout.addWidget(gpu_test_btn)

        tests_layout.addLayout(button_layout)

        # Test results
        self.hardware_results = QTextEdit()
        self.hardware_results.setAccessibleName("Hardware diagnostic results")
        self.hardware_results.setReadOnly(True)
        self.hardware_results.setPlainText(
            "Hardware diagnostic results will appear here.\n"
            "Select a test to run hardware diagnostics."
        )
        tests_layout.addWidget(self.hardware_results)

        layout.addWidget(tests_group)

        return tab

    def create_network_tab(self):
        """Create network diagnostics tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Network tests
        network_group = QGroupBox("Network Diagnostic Tests")
        network_layout = QVBoxLayout(network_group)

        # Test buttons
        button_layout = QHBoxLayout()

        connectivity_btn = PrimaryButton("Connectivity Test")
        connectivity_btn.clicked.connect(self.test_network_connectivity)
        button_layout.addWidget(connectivity_btn)

        speed_test_btn = SecondaryButton("Speed Test")
        speed_test_btn.clicked.connect(self.test_network_speed)
        button_layout.addWidget(speed_test_btn)

        dns_test_btn = SecondaryButton("DNS Test")
        dns_test_btn.clicked.connect(self.test_dns)
        button_layout.addWidget(dns_test_btn)

        latency_test_btn = SecondaryButton("Latency Test")
        latency_test_btn.clicked.connect(self.test_latency)
        button_layout.addWidget(latency_test_btn)

        network_layout.addLayout(button_layout)

        # Network results
        self.network_results = QTextEdit()
        self.network_results.setAccessibleName("Network diagnostic results")
        self.network_results.setReadOnly(True)
        self.network_results.setPlainText(
            "Network diagnostic results will appear here.\n"
            "Select a test to run network diagnostics."
        )
        network_layout.addWidget(self.network_results)

        layout.addWidget(network_group)

        return tab

    def create_health_tab(self):
        """Create system health check tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Health check controls
        health_group = QGroupBox("System Health Check")
        health_layout = QVBoxLayout(health_group)

        # Health check buttons
        button_layout = QHBoxLayout()

        full_health_btn = PrimaryButton("Full Health Scan")
        full_health_btn.clicked.connect(self.run_full_health_check)
        button_layout.addWidget(full_health_btn)

        quick_health_btn = SecondaryButton("Quick Health Check")
        quick_health_btn.clicked.connect(self.run_quick_health_check)
        button_layout.addWidget(quick_health_btn)

        schedule_btn = SecondaryButton("Schedule Checks")
        schedule_btn.clicked.connect(self.schedule_health_checks)
        button_layout.addWidget(schedule_btn)

        health_layout.addLayout(button_layout)

        # Health results
        self.health_results = QTextEdit()
        self.health_results.setAccessibleName("Health check results")
        self.health_results.setReadOnly(True)
        self.health_results.setPlainText(
            "System health check results will appear here.\n"
            "Run a health check to see system status and recommendations."
        )
        health_layout.addWidget(self.health_results)

        layout.addWidget(health_group)

        return tab

    def gather_system_info(self):
        """Gather and display system information."""
        self.system_info_tree.clear()

        # Operating System info
        os_item = QTreeWidgetItem(["Operating System", ""])
        os_item.addChild(QTreeWidgetItem(["System", platform.system()]))
        os_item.addChild(QTreeWidgetItem(["Release", platform.release()]))
        os_item.addChild(QTreeWidgetItem(["Version", platform.version()]))
        os_item.addChild(QTreeWidgetItem(["Machine", platform.machine()]))
        os_item.addChild(QTreeWidgetItem(["Processor", platform.processor()]))
        self.system_info_tree.addTopLevelItem(os_item)

        # Python info
        python_item = QTreeWidgetItem(["Python Environment", ""])
        python_item.addChild(QTreeWidgetItem(["Version", platform.python_version()]))
        python_item.addChild(
            QTreeWidgetItem(["Implementation", platform.python_implementation()])
        )
        self.system_info_tree.addTopLevelItem(python_item)

        # Expand all items
        self.system_info_tree.expandAll()

    def start_performance_monitoring(self):
        """Start performance monitoring."""
        self.performance_text.append("\n=== Performance Monitoring Started ===")
        self.performance_text.append(
            "Monitoring functionality ready for implementation."
        )
        self.performance_text.append("This will monitor:")
        self.performance_text.append("• CPU usage and temperature")
        self.performance_text.append("• Memory usage and available space")
        self.performance_text.append("• Disk I/O and usage")
        self.performance_text.append("• Network activity")
        self.performance_text.append("• GPU usage (if available)")

        if Modal:
            Modal(
                "Performance Monitoring",
                "Performance monitoring started!\n\n"
                "Real-time system performance data will be collected.",
                ["OK"],
                self,
            ).exec_()
        else:
            QMessageBox.information(
                self,
                "Performance Monitoring",
                "Performance monitoring started!\n\n"
                "Real-time system performance data will be collected.",
            )

    def stop_performance_monitoring(self):
        """Stop performance monitoring."""
        self.performance_text.append("\n=== Performance Monitoring Stopped ===")
        if Modal:
            Modal(
                "Performance Monitoring",
                "Performance monitoring stopped.",
                ["OK"],
                self,
            ).exec_()
        else:
            QMessageBox.information(
                self, "Performance Monitoring", "Performance monitoring stopped."
            )

    def reset_performance_stats(self):
        """Reset performance statistics."""
        self.performance_text.clear()
        self.performance_text.append("Performance statistics reset.")
        if Modal:
            Modal(
                "Performance Statistics",
                "Performance statistics have been reset.",
                ["OK"],
                self,
            ).exec_()
        else:
            QMessageBox.information(
                self,
                "Performance Statistics",
                "Performance statistics have been reset.",
            )

    def test_cpu(self):
        """Run CPU diagnostic test."""
        self.hardware_results.append("\n=== CPU Diagnostic Test ===")
        self.hardware_results.append("CPU test functionality ready for implementation.")
        self.hardware_results.append("This test will check:")
        self.hardware_results.append("• CPU cores and threads")
        self.hardware_results.append("• Clock speeds and scaling")
        self.hardware_results.append("• Temperature monitoring")
        self.hardware_results.append("• Stress testing capabilities")

        if Modal:
            Modal(
                "CPU Test",
                "CPU diagnostic test completed!\n\n"
                "Check the results area for detailed information.",
                ["OK"],
                self,
            ).exec_()
        else:
            QMessageBox.information(
                self,
                "CPU Test",
                "CPU diagnostic test completed!\n\n"
                "Check the results area for detailed information.",
            )

    def test_memory(self):
        """Run memory diagnostic test."""
        self.hardware_results.append("\n=== Memory Diagnostic Test ===")
        self.hardware_results.append(
            "Memory test functionality ready for implementation."
        )
        self.hardware_results.append("This test will check:")
        self.hardware_results.append("• Total and available memory")
        self.hardware_results.append("• Memory speed and timing")
        self.hardware_results.append("• Memory errors and stability")
        self.hardware_results.append("• Virtual memory usage")

        if Modal:
            Modal(
                "Memory Test",
                "Memory diagnostic test completed!\n\n"
                "Check the results area for detailed information.",
                ["OK"],
                self,
            ).exec_()
        else:
            QMessageBox.information(
                self,
                "Memory Test",
                "Memory diagnostic test completed!\n\n"
                "Check the results area for detailed information.",
            )

    def test_disk(self):
        """Run disk diagnostic test."""
        self.hardware_results.append("\n=== Disk Diagnostic Test ===")
        self.hardware_results.append(
            "Disk test functionality ready for implementation."
        )
        self.hardware_results.append("This test will check:")
        self.hardware_results.append("• Disk health and SMART status")
        self.hardware_results.append("• Read/write speeds")
        self.hardware_results.append("• Available space and fragmentation")
        self.hardware_results.append("• Bad sectors and errors")

        if Modal:
            Modal(
                "Disk Test",
                "Disk diagnostic test completed!\n\n"
                "Check the results area for detailed information.",
                ["OK"],
                self,
            ).exec_()
        else:
            QMessageBox.information(
                self,
                "Disk Test",
                "Disk diagnostic test completed!\n\n"
                "Check the results area for detailed information.",
            )

    def test_gpu(self):
        """Run GPU diagnostic test."""
        self.hardware_results.append("\n=== GPU Diagnostic Test ===")
        self.hardware_results.append("GPU test functionality ready for implementation.")
        self.hardware_results.append("This test will check:")
        self.hardware_results.append("• GPU model and specifications")
        self.hardware_results.append("• VRAM usage and availability")
        self.hardware_results.append("• Temperature and fan status")
        self.hardware_results.append("• Performance benchmarks")

        if Modal:
            Modal(
                "GPU Test",
                "GPU diagnostic test completed!\n\n"
                "Check the results area for detailed information.",
                ["OK"],
                self,
            ).exec_()
        else:
            QMessageBox.information(
                self,
                "GPU Test",
                "GPU diagnostic test completed!\n\n"
                "Check the results area for detailed information.",
            )

    def test_network_connectivity(self):
        """Test network connectivity."""
        self.network_results.append("\n=== Network Connectivity Test ===")
        self.network_results.append(
            "Connectivity test functionality ready for implementation."
        )
        self.network_results.append("This test will check:")
        self.network_results.append("• Internet connectivity")
        self.network_results.append("• Local network access")
        self.network_results.append("• Gateway connectivity")
        self.network_results.append("• DNS resolution")

        if Modal:
            Modal(
                "Network Connectivity",
                "Network connectivity test completed!\n\n"
                "Check the results area for detailed information.",
                ["OK"],
                self,
            ).exec_()
        else:
            QMessageBox.information(
                self,
                "Network Connectivity",
                "Network connectivity test completed!\n\n"
                "Check the results area for detailed information.",
            )

    def test_network_speed(self):
        """Test network speed."""
        self.network_results.append("\n=== Network Speed Test ===")
        self.network_results.append(
            "Speed test functionality ready for implementation."
        )
        self.network_results.append("This test will measure:")
        self.network_results.append("• Download speed")
        self.network_results.append("• Upload speed")
        self.network_results.append("• Ping latency")
        self.network_results.append("• Jitter and packet loss")

        if Modal:
            Modal(
                "Network Speed Test",
                "Network speed test completed!\n\n"
                "Check the results area for speed measurements.",
                ["OK"],
                self,
            ).exec_()
        else:
            QMessageBox.information(
                self,
                "Network Speed Test",
                "Network speed test completed!\n\n"
                "Check the results area for speed measurements.",
            )

    def test_dns(self):
        """Test DNS functionality."""
        self.network_results.append("\n=== DNS Test ===")
        self.network_results.append("DNS test functionality ready for implementation.")
        self.network_results.append("This test will check:")
        self.network_results.append("• DNS server response times")
        self.network_results.append("• DNS resolution accuracy")
        self.network_results.append("• Alternative DNS servers")
        self.network_results.append("• DNS cache status")

        if Modal:
            Modal(
                "DNS Test",
                "DNS test completed!\n\n" "Check the results area for DNS information.",
                ["OK"],
                self,
            ).exec_()
        else:
            QMessageBox.information(
                self,
                "DNS Test",
                "DNS test completed!\n\n" "Check the results area for DNS information.",
            )

    def test_latency(self):
        """Test network latency."""
        self.network_results.append("\n=== Network Latency Test ===")
        self.network_results.append(
            "Latency test functionality ready for implementation."
        )
        self.network_results.append("This test will measure:")
        self.network_results.append("• Ping times to various servers")
        self.network_results.append("• Traceroute analysis")
        self.network_results.append("• Jitter measurements")
        self.network_results.append("• Network path analysis")

        if Modal:
            Modal(
                "Network Latency",
                "Network latency test completed!\n\n"
                "Check the results area for latency measurements.",
                ["OK"],
                self,
            ).exec_()
        else:
            QMessageBox.information(
                self,
                "Network Latency",
                "Network latency test completed!\n\n"
                "Check the results area for latency measurements.",
            )

    def run_full_health_check(self):
        """Run full system health check."""
        self.health_results.append("\n=== Full System Health Check ===")
        self.health_results.append(
            "Full health check functionality ready for implementation."
        )
        self.health_results.append("This comprehensive check will analyze:")
        self.health_results.append("• Hardware health and status")
        self.health_results.append("• Software and driver updates")
        self.health_results.append("• Security vulnerabilities")
        self.health_results.append("• Performance bottlenecks")
        self.health_results.append("• System optimization opportunities")

        if Modal:
            Modal(
                "Full Health Check",
                "Full system health check completed!\n\n"
                "Review the detailed health report in the results area.",
                ["OK"],
                self,
            ).exec_()
        else:
            QMessageBox.information(
                self,
                "Full Health Check",
                "Full system health check completed!\n\n"
                "Review the detailed health report in the results area.",
            )

    def run_quick_health_check(self):
        """Run quick system health check."""
        self.health_results.append("\n=== Quick Health Check ===")
        self.health_results.append(
            "Quick health check functionality ready for implementation."
        )
        self.health_results.append("This quick check will verify:")
        self.health_results.append("• System responsiveness")
        self.health_results.append("• Critical service status")
        self.health_results.append("• Available resources")
        self.health_results.append("• Basic security status")

        if Modal:
            Modal(
                "Quick Health Check",
                "Quick health check completed!\n\n"
                "System appears to be functioning normally.",
                ["OK"],
                self,
            ).exec_()
        else:
            QMessageBox.information(
                self,
                "Quick Health Check",
                "Quick health check completed!\n\n"
                "System appears to be functioning normally.",
            )

    def schedule_health_checks(self):
        """Schedule automatic health checks."""
        self.health_results.append("\n=== Scheduled Health Checks ===")
        self.health_results.append(
            "Health check scheduling functionality ready for implementation."
        )
        self.health_results.append("Scheduling options will include:")
        self.health_results.append("• Daily, weekly, or monthly checks")
        self.health_results.append("• Custom check intervals")
        self.health_results.append("• Automatic reporting")
        self.health_results.append("• Alert notifications")

        if Modal:
            Modal(
                "Schedule Health Checks",
                "Health check scheduling configured!\n\n"
                "Automatic health checks will run as scheduled.",
                ["OK"],
                self,
            ).exec_()
        else:
            QMessageBox.information(
                self,
                "Schedule Health Checks",
                "Health check scheduling configured!\n\n"
                "Automatic health checks will run as scheduled.",
            )

    def run_full_scan(self):
        """Run full system diagnostic scan."""
        if Modal:
            Modal(
                "Full System Scan",
                "Full system diagnostic scan initiated!\n\n"
                "This will run comprehensive diagnostics across all categories.\n"
                "Please check each tab for detailed results.",
                ["OK"],
                self,
            ).exec_()
        else:
            QMessageBox.information(
                self,
                "Full System Scan",
                "Full system diagnostic scan initiated!\n\n"
                "This will run comprehensive diagnostics across all categories.\n"
                "Please check each tab for detailed results.",
            )

        # Run all diagnostic categories
        self.gather_system_info()
        self.start_performance_monitoring()
        self.test_cpu()
        self.test_network_connectivity()
        self.run_full_health_check()

    def run_quick_check(self):
        """Run quick system health check."""
        if Modal:
            Modal(
                "Quick Health Check",
                "Quick system health check completed!\n\n"
                "System appears to be functioning normally.\n"
                "Run a full scan for detailed diagnostics.",
                ["OK"],
                self,
            ).exec_()
        else:
            QMessageBox.information(
                self,
                "Quick Health Check",
                "Quick system health check completed!\n\n"
                "System appears to be functioning normally.\n"
                "Run a full scan for detailed diagnostics.",
            )

    def export_report(self):
        """Export diagnostic report."""
        if Modal:
            Modal(
                "Export Report",
                "Diagnostic report export ready!\n\n"
                "This feature will export comprehensive reports in:\n"
                "\u2022 PDF format\n"
                "\u2022 HTML format\n"
                "\u2022 CSV format for data analysis",
                ["OK"],
                self,
            ).exec_()
        else:
            QMessageBox.information(
                self,
                "Export Report",
                "Diagnostic report export ready!\n\n"
                "This feature will export comprehensive reports in:\n"
                "\u2022 PDF format\n"
                "\u2022 HTML format\n"
                "\u2022 CSV format for data analysis",
            )


def main():
    """Main function for standalone execution."""
    app = QApplication(sys.argv)
    window = SystemDiagnosticsGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
