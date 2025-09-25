#!/usr/bin/env python3
"""
Simple System Information Tool for Richard's File Utilities

A comprehensive system information viewer with hardware and software details.
"""

import sys
import os
import platform
import psutil
from datetime import datetime, timedelta

try:
    from PyQt5.QtWidgets import (
        QMainWindow,
        QWidget,
        QVBoxLayout,
        QHBoxLayout,
        QPushButton,
        QLabel,
        QTextEdit,
        QApplication,
        QMessageBox,
        QGroupBox,
        QTabWidget,
        QGridLayout,
        QProgressBar,
    )
    from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
    from PyQt5.QtGui import QFont
except ImportError:
    print("PyQt5 not available. Please install PyQt5.")
    sys.exit(1)


class SystemInfoWorker(QThread):
    """Worker thread for collecting system information."""

    info_ready = pyqtSignal(dict)

    def run(self):
        """Collect comprehensive system information."""
        info = {}

        try:
            # Basic system information
            info["system"] = {
                "OS": platform.system(),
                "OS Version": platform.version(),
                "OS Release": platform.release(),
                "Architecture": platform.architecture()[0],
                "Machine": platform.machine(),
                "Processor": platform.processor(),
                "Hostname": platform.node(),
                "Python Version": platform.python_version(),
                "Boot Time": datetime.fromtimestamp(
                    psutil.boot_time()
                ).strftime("%Y-%m-%d %H:%M:%S"),
                "Uptime": str(
                    timedelta(
                        seconds=int(
                            (
                                datetime.now()
                                - datetime.fromtimestamp(psutil.boot_time())
                            ).total_seconds()
                        )
                    )
                ),
            }

            # CPU information
            cpu_freq = psutil.cpu_freq()
            info["cpu"] = {
                "Physical Cores": psutil.cpu_count(logical=False),
                "Logical Cores": psutil.cpu_count(logical=True),
                "Max Frequency": (
                    f"{cpu_freq.max:.2f} MHz" if cpu_freq else "N/A"
                ),
                "Current Frequency": (
                    f"{cpu_freq.current:.2f} MHz" if cpu_freq else "N/A"
                ),
                "CPU Usage": f"{psutil.cpu_percent(interval=1):.1f}%",
            }

            # Memory information
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            info["memory"] = {
                "Total RAM": f"{memory.total / (1024**3):.2f} GB",
                "Available RAM": f"{memory.available / (1024**3):.2f} GB",
                "Used RAM": f"{memory.used / (1024**3):.2f} GB",
                "RAM Usage": f"{memory.percent:.1f}%",
                "Total Swap": f"{swap.total / (1024**3):.2f} GB",
                "Used Swap": f"{swap.used / (1024**3):.2f} GB",
                "Swap Usage": f"{swap.percent:.1f}%",
            }

            # Disk information
            disk_info = {}
            disk_partitions = psutil.disk_partitions()
            for partition in disk_partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_info[f"{partition.device}"] = {
                        "Mountpoint": partition.mountpoint,
                        "File System": partition.fstype,
                        "Total": f"{usage.total / (1024**3):.2f} GB",
                        "Used": f"{usage.used / (1024**3):.2f} GB",
                        "Free": f"{usage.free / (1024**3):.2f} GB",
                        "Usage": f"{(usage.used / usage.total) * 100:.1f}%",
                    }
                except PermissionError:
                    disk_info[f"{partition.device}"] = {
                        "Error": "Permission denied"
                    }
            info["disks"] = disk_info

            # Network information
            network_info = {}
            network_interfaces = psutil.net_if_addrs()
            for interface, addresses in network_interfaces.items():
                addr_info = []
                for addr in addresses:
                    if addr.family == 2:  # IPv4
                        addr_info.append(f"IPv4: {addr.address}")
                    elif addr.family == 23:  # IPv6 on Windows
                        addr_info.append(f"IPv6: {addr.address}")
                    elif addr.family == 17:  # MAC address
                        addr_info.append(f"MAC: {addr.address}")
                network_info[interface] = addr_info
            info["network"] = network_info

            # Process information
            processes = []
            for proc in psutil.process_iter(
                ["pid", "name", "cpu_percent", "memory_percent"]
            ):
                try:
                    proc_info = proc.info
                    if (
                        proc_info["cpu_percent"] > 0
                        or proc_info["memory_percent"] > 0
                    ):
                        processes.append(proc_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            # Sort by CPU usage and get top 10
            processes.sort(key=lambda x: x["cpu_percent"], reverse=True)
            info["processes"] = processes[:10]

        except Exception as e:
            info["error"] = str(e)

        self.info_ready.emit(info)


class SimpleSystemInfoGUI(QMainWindow):
    """Simple System Information GUI."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("System Information - Richard's File Utilities")
        self.setMinimumSize(900, 700)
        self.resize(1000, 800)

        # Apply basic styling
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #f5f5f5;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
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
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 14px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Courier New', monospace;
                font-size: 11px;
                background-color: white;
            }
            QTabWidget::pane {
                border: 1px solid #cccccc;
                border-radius: 4px;
            }
            QTabBar::tab {
                background-color: #ecf0f1;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
                color: white;
            }
        """
        )

        self.worker = None
        self._setup_ui()
        self._load_system_info()

        # Setup auto-refresh timer
        self.timer = QTimer()
        self.timer.timeout.connect(self._load_system_info)

    def _setup_ui(self):
        """Setup the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Title
        title = QLabel("💻 System Information")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title)

        # Control buttons
        button_layout = QHBoxLayout()

        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self._load_system_info)
        button_layout.addWidget(self.refresh_btn)

        self.auto_refresh_btn = QPushButton("⏱️ Auto Refresh (5s)")
        self.auto_refresh_btn.clicked.connect(self._toggle_auto_refresh)
        self.auto_refresh_btn.setCheckable(True)
        button_layout.addWidget(self.auto_refresh_btn)

        self.export_btn = QPushButton("💾 Export Info")
        self.export_btn.clicked.connect(self._export_info)
        button_layout.addWidget(self.export_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Tab widget for different information categories
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # System tab
        self.system_text = QTextEdit()
        self.system_text.setReadOnly(True)
        self.tab_widget.addTab(self.system_text, "System")

        # Hardware tab
        self.hardware_text = QTextEdit()
        self.hardware_text.setReadOnly(True)
        self.tab_widget.addTab(self.hardware_text, "Hardware")

        # Storage tab
        self.storage_text = QTextEdit()
        self.storage_text.setReadOnly(True)
        self.tab_widget.addTab(self.storage_text, "Storage")

        # Network tab
        self.network_text = QTextEdit()
        self.network_text.setReadOnly(True)
        self.tab_widget.addTab(self.network_text, "Network")

        # Processes tab
        self.processes_text = QTextEdit()
        self.processes_text.setReadOnly(True)
        self.tab_widget.addTab(self.processes_text, "Top Processes")

        # Status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")

    def _load_system_info(self):
        """Load system information in background thread."""
        if self.worker and self.worker.isRunning():
            return

        self.refresh_btn.setEnabled(False)
        self.status_bar.showMessage("Loading system information...")

        self.worker = SystemInfoWorker()
        self.worker.info_ready.connect(self._display_info)
        self.worker.finished.connect(self._load_finished)
        self.worker.start()

    def _display_info(self, info):
        """Display collected system information."""
        if "error" in info:
            QMessageBox.warning(
                self,
                "Error",
                f"Failed to collect system info: {info['error']}",
            )
            return

        # System information
        if "system" in info:
            system_text = "=== SYSTEM INFORMATION ===\n\n"
            for key, value in info["system"].items():
                system_text += f"{key:20}: {value}\n"
            self.system_text.setPlainText(system_text)

        # Hardware information
        if "cpu" in info and "memory" in info:
            hardware_text = "=== CPU INFORMATION ===\n\n"
            for key, value in info["cpu"].items():
                hardware_text += f"{key:20}: {value}\n"

            hardware_text += "\n\n=== MEMORY INFORMATION ===\n\n"
            for key, value in info["memory"].items():
                hardware_text += f"{key:20}: {value}\n"
            self.hardware_text.setPlainText(hardware_text)

        # Storage information
        if "disks" in info:
            storage_text = "=== DISK INFORMATION ===\n\n"
            for disk, details in info["disks"].items():
                storage_text += f"Drive: {disk}\n"
                for key, value in details.items():
                    storage_text += f"  {key:15}: {value}\n"
                storage_text += "\n"
            self.storage_text.setPlainText(storage_text)

        # Network information
        if "network" in info:
            network_text = "=== NETWORK INTERFACES ===\n\n"
            for interface, addresses in info["network"].items():
                network_text += f"Interface: {interface}\n"
                for addr in addresses:
                    network_text += f"  {addr}\n"
                network_text += "\n"
            self.network_text.setPlainText(network_text)

        # Process information
        if "processes" in info:
            processes_text = "=== TOP PROCESSES (CPU Usage) ===\n\n"
            processes_text += (
                f"{'PID':<8} {'Name':<25} {'CPU%':<8} {'Memory%':<8}\n"
            )
            processes_text += "-" * 55 + "\n"
            for proc in info["processes"]:
                processes_text += f"{proc['pid']:<8} {proc['name'][:24]:<25} {proc['cpu_percent']:<8.1f} {proc['memory_percent']:<8.1f}\n"
            self.processes_text.setPlainText(processes_text)

    def _load_finished(self):
        """Handle load completion."""
        self.refresh_btn.setEnabled(True)
        self.status_bar.showMessage("System information updated")

    def _toggle_auto_refresh(self):
        """Toggle auto-refresh timer."""
        if self.auto_refresh_btn.isChecked():
            self.timer.start(5000)  # 5 seconds
            self.auto_refresh_btn.setText("⏹️ Stop Auto Refresh")
            self.status_bar.showMessage("Auto-refresh enabled (5 seconds)")
        else:
            self.timer.stop()
            self.auto_refresh_btn.setText("⏱️ Auto Refresh (5s)")
            self.status_bar.showMessage("Auto-refresh disabled")

    def _export_info(self):
        """Export system information to text file."""
        try:
            filename = (
                f"system_info_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            )
            filepath = os.path.join(
                os.path.expanduser("~"), "Desktop", filename
            )

            with open(filepath, "w") as f:
                f.write("SYSTEM INFORMATION REPORT\n")
                f.write("=" * 50 + "\n")
                f.write(
                    f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                )

                # Write all tab contents
                tabs = [
                    ("SYSTEM", self.system_text.toPlainText()),
                    ("HARDWARE", self.hardware_text.toPlainText()),
                    ("STORAGE", self.storage_text.toPlainText()),
                    ("NETWORK", self.network_text.toPlainText()),
                    ("PROCESSES", self.processes_text.toPlainText()),
                ]

                for tab_name, content in tabs:
                    f.write(f"\n{tab_name} INFORMATION\n")
                    f.write("-" * 30 + "\n")
                    f.write(content)
                    f.write("\n\n")

            QMessageBox.information(
                self,
                "Export Successful",
                f"System information exported to:\n{filepath}",
            )
        except Exception as e:
            QMessageBox.warning(
                self,
                "Export Failed",
                f"Failed to export system information:\n{str(e)}",
            )


def main():
    """Main function to run the system information tool."""
    app = QApplication(sys.argv)
    window = SimpleSystemInfoGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
