#!/usr/bin/env python3
"""
System Tools GUI Wrapper for Richard's File Utilities

A simple GUI wrapper for system diagnostics and maintenance tools.
"""

import os
import sys

try:
    from PyQt5.QtWidgets import (
        QMainWindow,
        QWidget,
        QVBoxLayout,
        QPushButton,
        QLabel,
        QListWidget,
        QApplication,
        QMessageBox,
        QGroupBox,
    )
except ImportError:
    print("PyQt5 not available. Please install PyQt5.")
    sys.exit(1)


class SystemDiagnosticsGUI(QMainWindow):
    """Simple System Diagnostics GUI wrapper."""

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("System Diagnostics - Richard's File Utilities")
        self.setGeometry(100, 100, 800, 600)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Add header
        header_label = QLabel("System Diagnostics & Maintenance")
        header_label.setStyleSheet(
            """
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
                background-color: #ecf0f1;
                border-radius: 5px;
                margin-bottom: 10px;
            }
        """
        )
        layout.addWidget(header_label)

        # Tool buttons group
        tools_group = QGroupBox("System Tools")
        tools_layout = QVBoxLayout(tools_group)

        # System diagnostics button
        diagnostics_button = QPushButton("System Diagnostics")
        diagnostics_button.clicked.connect(self.run_diagnostics)
        tools_layout.addWidget(diagnostics_button)

        # System cleanup button
        cleanup_button = QPushButton("System Cleanup")
        cleanup_button.clicked.connect(self.run_cleanup)
        tools_layout.addWidget(cleanup_button)

        # Software maintenance button
        maintenance_button = QPushButton("Software Maintenance")
        maintenance_button.clicked.connect(self.run_maintenance)
        tools_layout.addWidget(maintenance_button)

        # Performance monitor button
        performance_button = QPushButton("Performance Monitor")
        performance_button.clicked.connect(self.monitor_performance)
        tools_layout.addWidget(performance_button)

        layout.addWidget(tools_group)

        # Status display
        status_group = QGroupBox("Status")
        status_layout = QVBoxLayout(status_group)

        self.status_list = QListWidget()
        self.status_list.addItem("System tools ready")
        self.status_list.addItem("Select a tool to maintain your system")
        status_layout.addWidget(self.status_list)

        layout.addWidget(status_group)

        # Style the buttons
        button_style = """
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #d68910;
            }
        """
        buttons = [
            diagnostics_button,
            cleanup_button,
            maintenance_button,
            performance_button,
        ]
        for button in buttons:
            button.setStyleSheet(button_style)

    def run_diagnostics(self):
        """Run system diagnostics."""
        try:
            # Try to import and launch the actual tool
            diagnostics_path = os.path.join(
                os.path.dirname(__file__), "diagnostics_monitoring"
            )
            sys.path.insert(0, diagnostics_path)
            QMessageBox.information(
                self,
                "System Diagnostics",
                "System diagnostics functionality will be implemented here.\n"
                "This tool will check system health, disk space, memory usage, "
                "and identify potential issues.",
            )
        except Exception as e:
            QMessageBox.information(
                self,
                "System Diagnostics",
                f"System diagnostics functionality will be implemented here.\n"
                f"Debug info: {str(e)}",
            )
        self.status_list.addItem("System diagnostics tool accessed")

    def run_cleanup(self):
        """Run system cleanup."""
        try:
            # Try to import and launch the actual tool
            cleanup_path = os.path.join(
                os.path.dirname(__file__), "system_cleanup"
            )
            sys.path.insert(0, cleanup_path)
            QMessageBox.information(
                self,
                "System Cleanup",
                "System cleanup functionality will be implemented here.\n"
                "This tool will clean temporary files, cache, logs, "
                "and other unnecessary data.",
            )
        except Exception as e:
            QMessageBox.information(
                self,
                "System Cleanup",
                f"System cleanup functionality will be implemented here.\n"
                f"Debug info: {str(e)}",
            )
        self.status_list.addItem("System cleanup tool accessed")

    def run_maintenance(self):
        """Run software maintenance."""
        try:
            # Try to import and launch the actual tool
            maintenance_path = os.path.join(
                os.path.dirname(__file__), "software_maintenance"
            )
            sys.path.insert(0, maintenance_path)
            QMessageBox.information(
                self,
                "Software Maintenance",
                "Software maintenance functionality will be implemented here.\n"
                "This tool will check for software updates, verify "
                "installations, and optimize system performance.",
            )
        except Exception as e:
            QMessageBox.information(
                self,
                "Software Maintenance",
                f"Software maintenance functionality will be implemented here.\n"
                f"Debug info: {str(e)}",
            )
        self.status_list.addItem("Software maintenance tool accessed")

    def monitor_performance(self):
        """Monitor system performance."""
        QMessageBox.information(
            self,
            "Performance Monitor",
            "Performance monitoring functionality will be implemented here.\n"
            "This tool will display real-time CPU, memory, disk, "
            "and network usage statistics.",
        )
        self.status_list.addItem("Performance monitor tool accessed")


def main():
    """Main function for standalone execution."""
    app = QApplication(sys.argv)
    window = SystemDiagnosticsGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
