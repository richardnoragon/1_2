#!/usr/bin/env python3
"""
Process Monitor Tool for Richard's File Utilities

A real-time process monitor with CPU and memory usage tracking.
"""

import sys
from datetime import datetime

import psutil

from src.gui.themes import Typography, token

try:
    from PyQt5.QtCore import Qt, QThread, QTimer, pyqtSignal
    from PyQt5.QtGui import QFont
    from PyQt5.QtWidgets import (
        QApplication,
        QHBoxLayout,
        QHeaderView,
        QLabel,
        QLineEdit,
        QMainWindow,
        QPushButton,
        QTableWidget,
        QTableWidgetItem,
        QVBoxLayout,
        QWidget,
    )
except ImportError:
    print("PyQt5 not available. Please install PyQt5.")
    sys.exit(1)


AUTO_REFRESH_LABEL = "▶️ Auto Refresh"
STOP_AUTO_LABEL = "⏹️ Stop Auto"
AUTO_REFRESH_STATUS = "Auto-refresh enabled (3 seconds)"


class ProcessMonitorWorker(QThread):
    """Worker thread for monitoring processes."""

    processes_ready = pyqtSignal(list)

    def __init__(self, sort_by="cpu"):
        super().__init__()
        self.sort_by = sort_by
        self._running = True

    def run(self):
        """Monitor processes continuously."""
        try:
            if not self._running:
                return

            processes = []
            for proc in psutil.process_iter(
                [
                    "pid",
                    "name",
                    "cpu_percent",
                    "memory_percent",
                    "status",
                    "create_time",
                ]
            ):
                if not self._running:
                    break

                try:
                    proc_info = proc.info
                    create_time = proc_info.get("create_time")
                    if create_time:
                        proc_info["create_time"] = datetime.fromtimestamp(
                            create_time
                        ).strftime("%H:%M:%S")
                    else:
                        proc_info["create_time"] = "N/A"

                    proc_info.setdefault("name", "Unknown")
                    proc_info.setdefault("status", "unknown")
                    proc_info.setdefault("cpu_percent", 0.0)
                    proc_info.setdefault("memory_percent", 0.0)
                    processes.append(proc_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            # Sort processes
            if self.sort_by == "cpu":
                processes.sort(key=lambda x: x["cpu_percent"], reverse=True)
            elif self.sort_by == "memory":
                processes.sort(key=lambda x: x["memory_percent"], reverse=True)
            elif self.sort_by == "name":
                processes.sort(key=lambda x: x["name"].lower())
            elif self.sort_by == "pid":
                processes.sort(key=lambda x: x["pid"])

            self.processes_ready.emit(processes[:100])  # Top 100 processes

        except Exception as e:
            print(f"Error monitoring processes: {e}")

    def stop(self):
        """Stop the worker thread."""
        self._running = False


class ProcessMonitorGUI(QMainWindow):
    """Process Monitor GUI."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Process Monitor - Richard's File Utilities")
        self.setMinimumSize(900, 600)
        self.resize(1000, 700)

        # Apply basic styling
        self.setStyleSheet(
            f"""
            QMainWindow {{
                background-color: {token('surface')};
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            QPushButton {{
                background-color: {token('semantic_success')};
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 14px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {token('semantic_success')};
            }}
            QPushButton:pressed {{
                background-color: {token('color_green_deep')};
            }}
            QPushButton:checked {{
                background-color: {token('semantic_error')};
            }}
            QTableWidget {{
                border: 1px solid {token('border')};
                border-radius: 4px;
                background-color: white;
                gridline-color: {token('border_light')};
            }}
            QTableWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {token('border_light')};
            }}
            QTableWidget::item:selected {{
                background-color: {token('accent')};
                color: white;
            }}
            QHeaderView::section {{
                background-color: {token('secondary')};
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }}
            QLineEdit {{
                border: 1px solid {token('border')};
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
            }}
        """
        )

        self.worker = None
        self.sort_by = "cpu"
        self._setup_ui()

        # Setup auto-refresh timer
        self.timer = QTimer()
        self.timer.timeout.connect(self._refresh_processes)

    def _setup_ui(self):
        """Setup the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Title
        title = QLabel("⚡ Process Monitor")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(Typography.h1())
        layout.addWidget(title)

        # Control panel
        control_layout = QHBoxLayout()

        # Refresh controls
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self._refresh_processes)
        control_layout.addWidget(self.refresh_btn)

        self.auto_refresh_btn = QPushButton(AUTO_REFRESH_LABEL)
        self.auto_refresh_btn.clicked.connect(self._toggle_auto_refresh)
        self.auto_refresh_btn.setCheckable(True)
        control_layout.addWidget(self.auto_refresh_btn)

        # Sorting controls
        control_layout.addWidget(QLabel("Sort by:"))

        self.sort_cpu_btn = QPushButton("CPU")
        self.sort_cpu_btn.clicked.connect(lambda: self._set_sort("cpu"))
        self.sort_cpu_btn.setCheckable(True)
        self.sort_cpu_btn.setChecked(True)
        control_layout.addWidget(self.sort_cpu_btn)

        self.sort_memory_btn = QPushButton("Memory")
        self.sort_memory_btn.clicked.connect(lambda: self._set_sort("memory"))
        self.sort_memory_btn.setCheckable(True)
        control_layout.addWidget(self.sort_memory_btn)

        self.sort_name_btn = QPushButton("Name")
        self.sort_name_btn.clicked.connect(lambda: self._set_sort("name"))
        self.sort_name_btn.setCheckable(True)
        control_layout.addWidget(self.sort_name_btn)

        self.sort_pid_btn = QPushButton("PID")
        self.sort_pid_btn.clicked.connect(lambda: self._set_sort("pid"))
        self.sort_pid_btn.setCheckable(True)
        control_layout.addWidget(self.sort_pid_btn)

        # Filter
        control_layout.addWidget(QLabel("Filter:"))
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Enter process name to filter...")
        self.filter_input.textChanged.connect(self._filter_processes)
        control_layout.addWidget(self.filter_input)

        control_layout.addStretch()
        layout.addLayout(control_layout)

        # Process table
        self.process_table = QTableWidget()
        self.process_table.setColumnCount(6)
        self.process_table.setHorizontalHeaderLabels(
            [
                "PID",
                "Process Name",
                "CPU %",
                "Memory %",
                "Status",
                "Start Time",
            ]
        )

        # Configure table
        header = self.process_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # PID
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Name
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # CPU
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Memory
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Status
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Start Time

        self.process_table.setAlternatingRowColors(True)
        self.process_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.process_table.setSortingEnabled(False)

        layout.addWidget(self.process_table)

        # Status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready - Click Refresh to load processes")

        # Store original process list for filtering
        self.all_processes = []

    def _refresh_processes(self):
        """Refresh the process list."""
        if self.worker and self.worker.isRunning():
            return

        self.status_bar.showMessage("Loading processes...")

        self.worker = ProcessMonitorWorker(self.sort_by)
        self.worker.processes_ready.connect(self._update_process_table)
        self.worker.finished.connect(self._refresh_finished)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.start()

    def _update_process_table(self, processes):
        """Update the process table with new data."""
        self.all_processes = processes
        self._filter_processes()

    def _filter_processes(self):
        """Filter processes based on the filter input."""
        filter_text = self.filter_input.text().lower()

        if filter_text:
            filtered_processes = [
                proc
                for proc in self.all_processes
                if filter_text in proc["name"].lower()
            ]
        else:
            filtered_processes = self.all_processes

        # Update table
        self.process_table.setRowCount(len(filtered_processes))

        for row, process in enumerate(filtered_processes):
            # PID
            self.process_table.setItem(row, 0, QTableWidgetItem(str(process["pid"])))

            # Name
            self.process_table.setItem(row, 1, QTableWidgetItem(process["name"]))

            # CPU %
            cpu_item = QTableWidgetItem(f"{process['cpu_percent']:.1f}%")
            if process["cpu_percent"] > 10:
                cpu_item.setBackground(Qt.red)
                cpu_item.setForeground(Qt.white)
            elif process["cpu_percent"] > 5:
                cpu_item.setBackground(Qt.yellow)
            self.process_table.setItem(row, 2, cpu_item)

            # Memory %
            memory_item = QTableWidgetItem(f"{process['memory_percent']:.1f}%")
            if process["memory_percent"] > 10:
                memory_item.setBackground(Qt.red)
                memory_item.setForeground(Qt.white)
            elif process["memory_percent"] > 5:
                memory_item.setBackground(Qt.yellow)
            self.process_table.setItem(row, 3, memory_item)

            # Status
            self.process_table.setItem(row, 4, QTableWidgetItem(process["status"]))

            # Start Time
            self.process_table.setItem(row, 5, QTableWidgetItem(process["create_time"]))

        process_count = len(filtered_processes)
        total_count = len(self.all_processes)

        if filter_text:
            self.status_bar.showMessage(
                f"Showing {process_count} of {total_count} processes " "(filtered)"
            )
        else:
            self.status_bar.showMessage(f"Showing {process_count} processes")

    def _refresh_finished(self):
        """Handle refresh completion."""
        if self.auto_refresh_btn.isChecked():
            self.status_bar.showMessage(AUTO_REFRESH_STATUS)
        else:
            self.status_bar.showMessage("Process list updated")

        self.worker = None

    def _toggle_auto_refresh(self):
        """Toggle auto-refresh timer."""
        if self.auto_refresh_btn.isChecked():
            self.timer.start(3000)  # 3 seconds
            self.auto_refresh_btn.setText(STOP_AUTO_LABEL)
            self.status_bar.showMessage(AUTO_REFRESH_STATUS)
        else:
            self.timer.stop()
            self.auto_refresh_btn.setText(AUTO_REFRESH_LABEL)
            self.status_bar.showMessage("Auto-refresh disabled")

    def _set_sort(self, sort_by):
        """Set the sorting method."""
        self.sort_by = sort_by

        # Update button states
        buttons = [
            self.sort_cpu_btn,
            self.sort_memory_btn,
            self.sort_name_btn,
            self.sort_pid_btn,
        ]
        for btn in buttons:
            btn.setChecked(False)

        if sort_by == "cpu":
            self.sort_cpu_btn.setChecked(True)
        elif sort_by == "memory":
            self.sort_memory_btn.setChecked(True)
        elif sort_by == "name":
            self.sort_name_btn.setChecked(True)
        elif sort_by == "pid":
            self.sort_pid_btn.setChecked(True)

        # Refresh with new sorting
        self._refresh_processes()

    def closeEvent(self, event):  # pragma: no cover - GUI lifecycle hook
        """Ensure background tasks stop cleanly when the window closes."""
        self.timer.stop()
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait(1000)
        self.auto_refresh_btn.setChecked(False)
        self.auto_refresh_btn.setText(AUTO_REFRESH_LABEL)
        super().closeEvent(event)


def main():
    """Main function to run the process monitor."""
    app = QApplication(sys.argv)
    window = ProcessMonitorGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
