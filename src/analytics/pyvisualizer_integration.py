#!/usr/bin/env python3
"""
RFU PyVisualizer Integration Module
==================================

This module provides PyVisualizer integration for Richard's File Utilities.
It can be easily integrated into the existing RFU architecture.

Author: GitHub Copilot
Date: September 29, 2025
"""

import json
import os
from datetime import datetime
from pathlib import Path

import pandas as pd
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

try:
    from PyVisualizer.Visualizer import Visualizer

    PYVISUALIZER_AVAILABLE = True
except ImportError:
    PYVISUALIZER_AVAILABLE = False


class RFUVisualizerWidget(QWidget):
    """PyVisualizer integration widget for RFU."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("RFU Analytics & Visualizations")
        self.setGeometry(100, 100, 600, 400)

        # Data storage
        self.data_dir = Path("data/analytics")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir = Path("reports")
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        self.setup_ui()

        if not PYVISUALIZER_AVAILABLE:
            self.show_pyvisualizer_not_available()

    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout()

        # Title
        title = QLabel("RFU Analytics Dashboard")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)

        # Status
        self.status_label = QLabel("Ready to generate analytics")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        # Buttons
        button_layout = QHBoxLayout()

        self.generate_sample_btn = QPushButton("Generate Sample Data")
        self.generate_sample_btn.clicked.connect(self.generate_sample_data)
        button_layout.addWidget(self.generate_sample_btn)

        self.create_charts_btn = QPushButton("Create Visualizations")
        self.create_charts_btn.clicked.connect(self.create_visualizations)
        button_layout.addWidget(self.create_charts_btn)

        self.open_reports_btn = QPushButton("Open Reports Folder")
        self.open_reports_btn.clicked.connect(self.open_reports_folder)
        button_layout.addWidget(self.open_reports_btn)

        layout.addLayout(button_layout)

        # Analytics info
        self.info_label = QLabel(
            "Click 'Generate Sample Data' to create demo analytics data"
        )
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet(
            "margin: 20px; padding: 10px; background-color: #f0f0f0; border-radius: 5px;"
        )
        layout.addWidget(self.info_label)

        self.setLayout(layout)

    def show_pyvisualizer_not_available(self):
        """Show message when PyVisualizer is not available."""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("PyVisualizer Not Available")
        msg.setText(
            "PyVisualizer is not installed or not available in the Python path."
        )
        msg.setInformativeText(
            "To install PyVisualizer, run:\npip install pyvisualizer"
        )
        msg.setStandardButtons(QMessageBox.Ok)
        msg.show()

        # Disable visualization buttons
        self.create_charts_btn.setEnabled(False)

    def generate_sample_data(self):
        """Generate sample analytics data."""
        self.status_label.setText("Generating sample data...")

        try:
            # Sample RFU operations data
            import numpy as np

            np.random.seed(42)

            data = []
            for i in range(90):  # 90 days of data
                date = datetime.now().timestamp() - (90 - i) * 24 * 3600

                # Sample operations
                operations = [
                    {
                        "timestamp": int(date),
                        "operation": "file_copy",
                        "count": np.random.randint(10, 100),
                        "size_mb": np.random.randint(100, 2000),
                        "average_sales": np.random.randint(1000, 5000),
                    },
                    {
                        "timestamp": int(date),
                        "operation": "file_move",
                        "count": np.random.randint(5, 50),
                        "size_mb": np.random.randint(50, 1000),
                        "average_sales": np.random.randint(500, 2500),
                    },
                    {
                        "timestamp": int(date),
                        "operation": "duplicate_scan",
                        "count": np.random.randint(1, 20),
                        "size_mb": np.random.randint(10, 500),
                        "average_sales": np.random.randint(200, 1500),
                    },
                ]

                data.extend(operations)

            # Save to JSON
            data_file = self.data_dir / "rfu_operations.json"
            with open(data_file, "w") as f:
                json.dump(data, f, indent=2)

            self.status_label.setText(f"✅ Generated {len(data)} sample records")
            self.info_label.setText(
                f"Sample data created with {len(data)} records.\nData saved to: {data_file}"
            )

        except Exception as e:
            self.status_label.setText(f"❌ Error generating data: {e}")

    def create_visualizations(self):
        """Create visualizations using PyVisualizer."""
        if not PYVISUALIZER_AVAILABLE:
            QMessageBox.warning(self, "Error", "PyVisualizer is not available")
            return

        self.status_label.setText("Creating visualizations...")

        try:
            # Load data
            data_file = self.data_dir / "rfu_operations.json"
            if not data_file.exists():
                QMessageBox.information(
                    self, "Info", "No data available. Generate sample data first."
                )
                return

            with open(data_file, "r") as f:
                data = json.load(f)

            df = pd.DataFrame(data)

            # Initialize visualizer
            visualizer = Visualizer()

            # Change to reports directory
            original_dir = os.getcwd()
            os.chdir(self.reports_dir)

            try:
                # Create yearly chart
                visualizer.barPlotSalesByYear(
                    pandasDataframe=df,
                    xColName="timestamp",
                    yColName="average_sales",
                    sSaveWithFileName="rfu_analytics_yearly.png",
                )

                # Create monthly chart
                visualizer.barPlotSalesByMonth(
                    pandasDataframe=df,
                    xColName="timestamp",
                    yColName="average_sales",
                    sSaveWithFileName="rfu_analytics_monthly.png",
                )

                self.status_label.setText("✅ Visualizations created successfully")
                self.info_label.setText(
                    f"Charts saved to: {self.reports_dir.absolute()}"
                )

            finally:
                os.chdir(original_dir)

        except Exception as e:
            self.status_label.setText(f"❌ Error creating visualizations: {e}")
            QMessageBox.critical(
                self, "Error", f"Failed to create visualizations:\n{str(e)}"
            )

    def open_reports_folder(self):
        """Open the reports folder in file explorer."""
        try:
            import subprocess

            subprocess.run(f'explorer "{self.reports_dir.absolute()}"', shell=True)
        except Exception as e:
            QMessageBox.warning(
                self, "Error", f"Could not open reports folder:\n{str(e)}"
            )


class RFUAnalyticsLogger:
    """Logger for RFU operations to be used throughout the application."""

    def __init__(self):
        self.data_dir = Path("data/analytics")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.data_dir / "operations_log.json"

    def log_operation(
        self,
        tool_name: str,
        operation: str,
        file_count: int = 0,
        size_mb: float = 0,
        duration_seconds: float = 0,
        success: bool = True,
    ):
        """
        Log an RFU operation for analytics.

        Usage in RFU tools:
        logger = RFUAnalyticsLogger()
        logger.log_operation(
            "FileFinderWindow", "search", file_count=150, success=True
        )
        """

        log_entry = {
            "timestamp": int(datetime.now().timestamp()),
            "tool_name": tool_name,
            "operation": operation,
            "file_count": file_count,
            "size_mb": size_mb,
            "duration_seconds": duration_seconds,
            "success": success,
            "average_sales": file_count * 10,  # Mock data for PyVisualizer
        }

        # Load existing log
        logs = []
        if self.log_file.exists():
            try:
                with open(self.log_file, "r") as f:
                    logs = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                logs = []

        # Add new entry
        logs.append(log_entry)

        # Keep only last 1000 entries to prevent file from growing too large
        if len(logs) > 1000:
            logs = logs[-1000:]

        # Save updated log
        with open(self.log_file, "w") as f:
            json.dump(logs, f, indent=2)


def integrate_with_main_hub(main_window):
    """
    Function to integrate PyVisualizer with the main RFU hub.

    Call this from your main.py file:
    from src.analytics.pyvisualizer_integration import integrate_with_main_hub
    integrate_with_main_hub(self)  # where self is your main window
    """

    def open_analytics():
        """Open the analytics widget."""
        if not hasattr(main_window, "_analytics_widget"):
            main_window._analytics_widget = RFUVisualizerWidget()

        main_window._analytics_widget.show()
        main_window._analytics_widget.raise_()
        main_window._analytics_widget.activateWindow()

    # Add menu item (you would customize this based on your menu structure)
    try:
        # This is pseudocode - adapt to your actual menu structure
        if hasattr(main_window, "menuBar"):
            tools_menu = main_window.menuBar().addMenu("Analytics")
            analytics_action = tools_menu.addAction("Open Analytics Dashboard")
            analytics_action.triggered.connect(open_analytics)
    except Exception as e:
        print(f"Could not add analytics menu: {e}")

    return open_analytics


# Example usage for testing
if __name__ == "__main__":
    import sys

    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # Test the widget
    widget = RFUVisualizerWidget()
    widget.show()

    # Test the logger
    logger = RFUAnalyticsLogger()
    logger.log_operation("TestTool", "test_operation", file_count=42, success=True)
    print("✅ Test log entry created")

    sys.exit(app.exec_())
