"""Battery health monitoring GUI widget with charge visualization."""

import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import threading
import time

from ..monitors.battery.battery_monitor import BatteryMonitor
from gui.common.base_window import BaseWindow
from core.error_handler import error_handler


class BatteryHealthWidget(BaseWindow):
    """GUI widget for battery health monitoring and visualization."""

    def __init__(self, parent=None):
        """Initialize the battery health widget.

        Args:
            parent: Parent widget
        """
        super().__init__(parent, "Battery Health Monitor")

        # Battery monitor
        self.battery_monitor = BatteryMonitor()
        self.monitoring_active = False
        self.update_thread = None

        # Data storage for visualization
        self.battery_data_history = []
        self.max_history_points = 100

        # GUI components
        self.battery_frame = None
        self.chart_frame = None
        self.control_frame = None

        # Charts
        self.charge_figure = None
        self.health_figure = None
        self.charge_canvas = None
        self.health_canvas = None

        # Status variables
        self.status_vars = {}
        self.battery_widgets = {}

        self.setup_ui()
        self.start_monitoring()

    def setup_ui(self) -> None:
        """Set up the user interface."""
        try:
            # Configure main window
            self.title("Battery Health Monitor")
            self.geometry("1200x800")

            # Create main container
            main_container = ttk.Frame(self.main_frame)
            main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # Create paned window for layout
            paned_window = ttk.PanedWindow(
                main_container, orient=tk.HORIZONTAL
            )
            paned_window.pack(fill=tk.BOTH, expand=True)

            # Left panel - Battery status and controls
            left_panel = ttk.Frame(paned_window)
            paned_window.add(left_panel, weight=1)

            # Right panel - Charts and visualizations
            right_panel = ttk.Frame(paned_window)
            paned_window.add(right_panel, weight=2)

            # Setup left panel
            self.setup_battery_status_panel(left_panel)
            self.setup_control_panel(left_panel)

            # Setup right panel
            self.setup_charts_panel(right_panel)

        except Exception as e:
            self.logger.error(f"Error setting up battery health UI: {e}")
            error_handler.handle_error(e, "BatteryHealthWidget.setup_ui")

    def setup_battery_status_panel(self, parent: ttk.Frame) -> None:
        """Set up the battery status panel.

        Args:
            parent: Parent frame
        """
        try:
            # Battery status frame
            self.battery_frame = ttk.LabelFrame(
                parent, text="Battery Status", padding=10
            )
            self.battery_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

            # Create scrollable frame for multiple batteries
            canvas = tk.Canvas(self.battery_frame)
            scrollbar = ttk.Scrollbar(
                self.battery_frame, orient="vertical", command=canvas.yview
            )
            scrollable_frame = ttk.Frame(canvas)

            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
            )

            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            # Store reference to scrollable frame
            self.battery_status_frame = scrollable_frame

            # Initial message
            no_battery_label = ttk.Label(
                scrollable_frame,
                text="No battery data available\nStarting monitoring...",
                justify=tk.CENTER,
            )
            no_battery_label.pack(pady=20)

        except Exception as e:
            self.logger.error(f"Error setting up battery status panel: {e}")

    def setup_control_panel(self, parent: ttk.Frame) -> None:
        """Set up the control panel.

        Args:
            parent: Parent frame
        """
        try:
            # Control frame
            self.control_frame = ttk.LabelFrame(
                parent, text="Controls", padding=10
            )
            self.control_frame.pack(fill=tk.X, pady=(0, 10))

            # Monitoring controls
            control_buttons_frame = ttk.Frame(self.control_frame)
            control_buttons_frame.pack(fill=tk.X, pady=(0, 10))

            self.start_button = ttk.Button(
                control_buttons_frame,
                text="Start Monitoring",
                command=self.start_monitoring,
            )
            self.start_button.pack(side=tk.LEFT, padx=(0, 5))

            self.stop_button = ttk.Button(
                control_buttons_frame,
                text="Stop Monitoring",
                command=self.stop_monitoring,
                state=tk.DISABLED,
            )
            self.stop_button.pack(side=tk.LEFT, padx=(0, 5))

            self.refresh_button = ttk.Button(
                control_buttons_frame,
                text="Refresh",
                command=self.refresh_data,
            )
            self.refresh_button.pack(side=tk.LEFT)

            # Settings frame
            settings_frame = ttk.Frame(self.control_frame)
            settings_frame.pack(fill=tk.X, pady=(10, 0))

            # Update interval setting
            ttk.Label(settings_frame, text="Update Interval (seconds):").pack(
                anchor=tk.W
            )
            self.interval_var = tk.StringVar(value="60")
            interval_spinbox = ttk.Spinbox(
                settings_frame,
                from_=10,
                to=300,
                textvariable=self.interval_var,
                width=10,
            )
            interval_spinbox.pack(anchor=tk.W, pady=(2, 10))

            # Export button
            export_button = ttk.Button(
                settings_frame, text="Export Data", command=self.export_data
            )
            export_button.pack(anchor=tk.W)

        except Exception as e:
            self.logger.error(f"Error setting up control panel: {e}")

    def setup_charts_panel(self, parent: ttk.Frame) -> None:
        """Set up the charts panel.

        Args:
            parent: Parent frame
        """
        try:
            # Charts frame
            self.chart_frame = ttk.LabelFrame(
                parent, text="Battery Visualization", padding=10
            )
            self.chart_frame.pack(fill=tk.BOTH, expand=True)

            # Create notebook for different chart views
            chart_notebook = ttk.Notebook(self.chart_frame)
            chart_notebook.pack(fill=tk.BOTH, expand=True)

            # Charge level chart
            charge_frame = ttk.Frame(chart_notebook)
            chart_notebook.add(charge_frame, text="Charge Level")
            self.setup_charge_chart(charge_frame)

            # Health trend chart
            health_frame = ttk.Frame(chart_notebook)
            chart_notebook.add(health_frame, text="Health Trend")
            self.setup_health_chart(health_frame)

            # Power consumption chart
            power_frame = ttk.Frame(chart_notebook)
            chart_notebook.add(power_frame, text="Power Consumption")
            self.setup_power_chart(power_frame)

            # Cycle analysis chart
            cycle_frame = ttk.Frame(chart_notebook)
            chart_notebook.add(cycle_frame, text="Cycle Analysis")
            self.setup_cycle_chart(cycle_frame)

        except Exception as e:
            self.logger.error(f"Error setting up charts panel: {e}")

    def setup_charge_chart(self, parent: ttk.Frame) -> None:
        """Set up the charge level chart.

        Args:
            parent: Parent frame
        """
        try:
            # Create matplotlib figure
            self.charge_figure = Figure(figsize=(8, 6), dpi=100)
            self.charge_ax = self.charge_figure.add_subplot(111)

            # Create canvas
            self.charge_canvas = FigureCanvasTkAgg(self.charge_figure, parent)
            self.charge_canvas.draw()
            self.charge_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

            # Initial empty chart
            self.charge_ax.set_title("Battery Charge Level Over Time")
            self.charge_ax.set_xlabel("Time")
            self.charge_ax.set_ylabel("Charge Level (%)")
            self.charge_ax.grid(True, alpha=0.3)
            self.charge_ax.set_ylim(0, 100)

        except Exception as e:
            self.logger.error(f"Error setting up charge chart: {e}")

    def setup_health_chart(self, parent: ttk.Frame) -> None:
        """Set up the health trend chart.

        Args:
            parent: Parent frame
        """
        try:
            # Create matplotlib figure
            self.health_figure = Figure(figsize=(8, 6), dpi=100)
            self.health_ax = self.health_figure.add_subplot(111)

            # Create canvas
            self.health_canvas = FigureCanvasTkAgg(self.health_figure, parent)
            self.health_canvas.draw()
            self.health_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

            # Initial empty chart
            self.health_ax.set_title("Battery Health Trend")
            self.health_ax.set_xlabel("Time")
            self.health_ax.set_ylabel("Health (%)")
            self.health_ax.grid(True, alpha=0.3)
            self.health_ax.set_ylim(0, 100)

        except Exception as e:
            self.logger.error(f"Error setting up health chart: {e}")

    def setup_power_chart(self, parent: ttk.Frame) -> None:
        """Set up the power consumption chart.

        Args:
            parent: Parent frame
        """
        try:
            # Create matplotlib figure
            self.power_figure = Figure(figsize=(8, 6), dpi=100)
            self.power_ax = self.power_figure.add_subplot(111)

            # Create canvas
            self.power_canvas = FigureCanvasTkAgg(self.power_figure, parent)
            self.power_canvas.draw()
            self.power_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

            # Initial empty chart
            self.power_ax.set_title("Power Consumption")
            self.power_ax.set_xlabel("Time")
            self.power_ax.set_ylabel("Power (W)")
            self.power_ax.grid(True, alpha=0.3)

        except Exception as e:
            self.logger.error(f"Error setting up power chart: {e}")

    def setup_cycle_chart(self, parent: ttk.Frame) -> None:
        """Set up the cycle analysis chart.

        Args:
            parent: Parent frame
        """
        try:
            # Create matplotlib figure
            self.cycle_figure = Figure(figsize=(8, 6), dpi=100)
            self.cycle_ax = self.cycle_figure.add_subplot(111)

            # Create canvas
            self.cycle_canvas = FigureCanvasTkAgg(self.cycle_figure, parent)
            self.cycle_canvas.draw()
            self.cycle_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

            # Initial empty chart
            self.cycle_ax.set_title("Charge Cycle Analysis")
            self.cycle_ax.set_xlabel("Cycle Number")
            self.cycle_ax.set_ylabel("Depth of Discharge (%)")
            self.cycle_ax.grid(True, alpha=0.3)

        except Exception as e:
            self.logger.error(f"Error setting up cycle chart: {e}")

    def start_monitoring(self) -> None:
        """Start battery monitoring."""
        try:
            if not self.monitoring_active:
                # Update interval
                try:
                    interval = float(self.interval_var.get())
                    self.battery_monitor.update_interval = interval
                except ValueError:
                    interval = 60.0

                # Start monitor
                if self.battery_monitor.start_monitoring():
                    self.monitoring_active = True

                    # Update button states
                    self.start_button.config(state=tk.DISABLED)
                    self.stop_button.config(state=tk.NORMAL)

                    # Start update thread
                    self.update_thread = threading.Thread(
                        target=self.update_loop, daemon=True
                    )
                    self.update_thread.start()

                    self.logger.info("Battery monitoring started")
                else:
                    self.show_error("Failed to start battery monitoring")

        except Exception as e:
            self.logger.error(f"Error starting monitoring: {e}")
            self.show_error(f"Error starting monitoring: {str(e)}")

    def stop_monitoring(self) -> None:
        """Stop battery monitoring."""
        try:
            if self.monitoring_active:
                self.monitoring_active = False

                # Stop monitor
                self.battery_monitor.stop_monitoring()

                # Update button states
                self.start_button.config(state=tk.NORMAL)
                self.stop_button.config(state=tk.DISABLED)

                self.logger.info("Battery monitoring stopped")

        except Exception as e:
            self.logger.error(f"Error stopping monitoring: {e}")
            self.show_error(f"Error stopping monitoring: {str(e)}")

    def update_loop(self) -> None:
        """Main update loop for monitoring data."""
        while self.monitoring_active:
            try:
                # Get current battery data
                current_data = self.battery_monitor.get_current_data()

                if current_data:
                    # Store data for history
                    self.battery_data_history.append(
                        {"timestamp": datetime.now(), "data": current_data}
                    )

                    # Limit history size
                    if (
                        len(self.battery_data_history)
                        > self.max_history_points
                    ):
                        self.battery_data_history = self.battery_data_history[
                            -self.max_history_points :
                        ]

                    # Update UI in main thread
                    self.after(0, self.update_ui, current_data)

                # Wait for next update
                time.sleep(self.battery_monitor.update_interval)

            except Exception as e:
                self.logger.error(f"Error in update loop: {e}")
                time.sleep(5)  # Wait before retrying

    def update_ui(self, battery_data: Dict[str, Any]) -> None:
        """Update the UI with new battery data.

        Args:
            battery_data: Current battery data
        """
        try:
            # Update battery status display
            self.update_battery_status(battery_data)

            # Update charts
            self.update_charts()

        except Exception as e:
            self.logger.error(f"Error updating UI: {e}")

    def update_battery_status(self, battery_data: Dict[str, Any]) -> None:
        """Update the battery status display.

        Args:
            battery_data: Current battery data
        """
        try:
            # Clear existing widgets
            for widget in self.battery_status_frame.winfo_children():
                widget.destroy()

            batteries = battery_data.get("batteries", [])

            if not batteries:
                no_battery_label = ttk.Label(
                    self.battery_status_frame,
                    text="No batteries detected",
                    justify=tk.CENTER,
                )
                no_battery_label.pack(pady=20)
                return

            # Create battery widgets
            for i, battery in enumerate(batteries):
                self.create_battery_widget(
                    self.battery_status_frame, battery, i
                )

        except Exception as e:
            self.logger.error(f"Error updating battery status: {e}")

    def create_battery_widget(
        self, parent: ttk.Frame, battery: Dict[str, Any], index: int
    ) -> None:
        """Create a widget for displaying battery information.

        Args:
            parent: Parent frame
            battery: Battery data
            index: Battery index
        """
        try:
            battery_id = battery.get("id", f"Battery {index + 1}")

            # Battery frame
            battery_frame = ttk.LabelFrame(
                parent, text=f"Battery {index + 1}: {battery_id}", padding=10
            )
            battery_frame.pack(fill=tk.X, pady=(0, 10))

            # Create two columns
            left_column = ttk.Frame(battery_frame)
            left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            right_column = ttk.Frame(battery_frame)
            right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

            # Left column - Basic info
            self.add_battery_info_row(
                left_column,
                "Charge Level:",
                f"{battery.get('percent', 0):.1f}%",
            )

            self.add_battery_info_row(
                left_column,
                "Health:",
                f"{battery.get('health_percent', 100):.1f}%",
            )

            self.add_battery_info_row(
                left_column, "Status:", battery.get("health_status", "Unknown")
            )

            self.add_battery_info_row(
                left_column,
                "Charging:",
                "Yes" if battery.get("power_plugged", False) else "No",
            )

            # Right column - Detailed info
            cycle_count = battery.get("cycle_count", 0)
            self.add_battery_info_row(
                right_column,
                "Cycle Count:",
                str(cycle_count) if cycle_count else "Unknown",
            )

            temperature = battery.get("temperature")
            temp_text = f"{temperature:.1f}°C" if temperature else "Unknown"
            self.add_battery_info_row(right_column, "Temperature:", temp_text)

            voltage = battery.get("voltage")
            voltage_text = f"{voltage:.2f}V" if voltage else "Unknown"
            self.add_battery_info_row(right_column, "Voltage:", voltage_text)

            # Time remaining
            secsleft = battery.get("secsleft")
            if secsleft and secsleft > 0:
                hours = secsleft // 3600
                minutes = (secsleft % 3600) // 60
                time_text = f"{hours}h {minutes}m"
            else:
                time_text = "Unknown"
            self.add_battery_info_row(
                right_column, "Time Remaining:", time_text
            )

            # Progress bar for charge level
            progress_frame = ttk.Frame(battery_frame)
            progress_frame.pack(fill=tk.X, pady=(10, 0))

            ttk.Label(progress_frame, text="Charge Level:").pack(anchor=tk.W)

            charge_progress = ttk.Progressbar(
                progress_frame, length=300, mode="determinate"
            )
            charge_progress.pack(fill=tk.X, pady=(2, 0))
            charge_progress["value"] = battery.get("percent", 0)

            # Health progress bar
            ttk.Label(progress_frame, text="Battery Health:").pack(
                anchor=tk.W, pady=(10, 0)
            )

            health_progress = ttk.Progressbar(
                progress_frame, length=300, mode="determinate"
            )
            health_progress.pack(fill=tk.X, pady=(2, 0))
            health_progress["value"] = battery.get("health_percent", 100)

        except Exception as e:
            self.logger.error(f"Error creating battery widget: {e}")

    def add_battery_info_row(
        self, parent: ttk.Frame, label: str, value: str
    ) -> None:
        """Add a battery information row.

        Args:
            parent: Parent frame
            label: Label text
            value: Value text
        """
        try:
            row_frame = ttk.Frame(parent)
            row_frame.pack(fill=tk.X, pady=2)

            ttk.Label(row_frame, text=label, width=15).pack(side=tk.LEFT)
            ttk.Label(
                row_frame, text=value, font=("TkDefaultFont", 9, "bold")
            ).pack(side=tk.LEFT)

        except Exception as e:
            self.logger.error(f"Error adding battery info row: {e}")

    def update_charts(self) -> None:
        """Update all charts with current data."""
        try:
            if not self.battery_data_history:
                return

            # Update charge chart
            self.update_charge_chart()

            # Update health chart
            self.update_health_chart()

            # Update power chart
            self.update_power_chart()

            # Update cycle chart
            self.update_cycle_chart()

        except Exception as e:
            self.logger.error(f"Error updating charts: {e}")

    def update_charge_chart(self) -> None:
        """Update the charge level chart."""
        try:
            if not hasattr(self, "charge_ax"):
                return

            self.charge_ax.clear()

            # Extract data for plotting
            timestamps = []
            charge_levels = {}

            for entry in self.battery_data_history[-50:]:  # Last 50 points
                timestamp = entry["timestamp"]
                batteries = entry["data"].get("batteries", [])

                timestamps.append(timestamp)

                for battery in batteries:
                    battery_id = battery.get("id", "Battery")
                    charge_percent = battery.get("percent", 0)

                    if battery_id not in charge_levels:
                        charge_levels[battery_id] = []
                    charge_levels[battery_id].append(charge_percent)

            # Plot charge levels
            for battery_id, levels in charge_levels.items():
                if len(levels) == len(timestamps):
                    self.charge_ax.plot(
                        timestamps,
                        levels,
                        label=battery_id,
                        marker="o",
                        markersize=3,
                    )

            self.charge_ax.set_title("Battery Charge Level Over Time")
            self.charge_ax.set_xlabel("Time")
            self.charge_ax.set_ylabel("Charge Level (%)")
            self.charge_ax.grid(True, alpha=0.3)
            self.charge_ax.set_ylim(0, 100)

            if charge_levels:
                self.charge_ax.legend()

            # Format x-axis
            if timestamps:
                self.charge_ax.tick_params(axis="x", rotation=45)

            self.charge_figure.tight_layout()
            self.charge_canvas.draw()

        except Exception as e:
            self.logger.error(f"Error updating charge chart: {e}")

    def update_health_chart(self) -> None:
        """Update the health trend chart."""
        try:
            if not hasattr(self, "health_ax"):
                return

            self.health_ax.clear()

            # Extract health data
            timestamps = []
            health_levels = {}

            for entry in self.battery_data_history[-50:]:
                timestamp = entry["timestamp"]
                batteries = entry["data"].get("batteries", [])

                timestamps.append(timestamp)

                for battery in batteries:
                    battery_id = battery.get("id", "Battery")
                    health_percent = battery.get("health_percent", 100)

                    if battery_id not in health_levels:
                        health_levels[battery_id] = []
                    health_levels[battery_id].append(health_percent)

            # Plot health trends
            for battery_id, levels in health_levels.items():
                if len(levels) == len(timestamps):
                    self.health_ax.plot(
                        timestamps,
                        levels,
                        label=battery_id,
                        marker="s",
                        markersize=3,
                    )

            self.health_ax.set_title("Battery Health Trend")
            self.health_ax.set_xlabel("Time")
            self.health_ax.set_ylabel("Health (%)")
            self.health_ax.grid(True, alpha=0.3)
            self.health_ax.set_ylim(0, 100)

            if health_levels:
                self.health_ax.legend()

            # Format x-axis
            if timestamps:
                self.health_ax.tick_params(axis="x", rotation=45)

            self.health_figure.tight_layout()
            self.health_canvas.draw()

        except Exception as e:
            self.logger.error(f"Error updating health chart: {e}")

    def update_power_chart(self) -> None:
        """Update the power consumption chart."""
        try:
            if not hasattr(self, "power_ax"):
                return

            self.power_ax.clear()

            # Extract power data
            timestamps = []
            power_data = []

            for entry in self.battery_data_history[-50:]:
                timestamp = entry["timestamp"]
                power_consumption = entry["data"].get("power_consumption", {})

                timestamps.append(timestamp)

                # Get estimated power consumption
                cpu_power = power_consumption.get("cpu_power_estimate", 0)
                power_data.append(cpu_power)

            # Plot power consumption
            if timestamps and power_data:
                self.power_ax.plot(
                    timestamps,
                    power_data,
                    "r-",
                    label="CPU Power",
                    marker="d",
                    markersize=3,
                )

            self.power_ax.set_title("Power Consumption")
            self.power_ax.set_xlabel("Time")
            self.power_ax.set_ylabel("Power (W)")
            self.power_ax.grid(True, alpha=0.3)

            if power_data:
                self.power_ax.legend()

            # Format x-axis
            if timestamps:
                self.power_ax.tick_params(axis="x", rotation=45)

            self.power_figure.tight_layout()
            self.power_canvas.draw()

        except Exception as e:
            self.logger.error(f"Error updating power chart: {e}")

    def update_cycle_chart(self) -> None:
        """Update the cycle analysis chart."""
        try:
            if not hasattr(self, "cycle_ax"):
                return

            self.cycle_ax.clear()

            # Get cycle data from battery monitor
            if hasattr(self.battery_monitor, "_monitored_batteries"):
                for battery_id in self.battery_monitor._monitored_batteries:
                    cycle_history = (
                        self.battery_monitor.cycle_tracker.get_cycle_history(
                            battery_id, days=30
                        )
                    )

                    if cycle_history:
                        cycle_numbers = list(range(1, len(cycle_history) + 1))
                        depths = [
                            cycle.get("depth_of_discharge", 0)
                            for cycle in cycle_history
                        ]

                        self.cycle_ax.plot(
                            cycle_numbers,
                            depths,
                            label=battery_id,
                            marker="o",
                            markersize=4,
                        )

            self.cycle_ax.set_title("Charge Cycle Analysis (Last 30 Days)")
            self.cycle_ax.set_xlabel("Cycle Number")
            self.cycle_ax.set_ylabel("Depth of Discharge (%)")
            self.cycle_ax.grid(True, alpha=0.3)

            # Add legend if there's data
            handles, labels = self.cycle_ax.get_legend_handles_labels()
            if handles:
                self.cycle_ax.legend()

            self.cycle_figure.tight_layout()
            self.cycle_canvas.draw()

        except Exception as e:
            self.logger.error(f"Error updating cycle chart: {e}")

    def refresh_data(self) -> None:
        """Refresh battery data manually."""
        try:
            if self.battery_monitor.is_running:
                current_data = self.battery_monitor.get_current_data()
                if current_data:
                    self.update_ui(current_data)
                else:
                    self.show_info("No battery data available")
            else:
                self.show_info("Monitoring is not active")

        except Exception as e:
            self.logger.error(f"Error refreshing data: {e}")
            self.show_error(f"Error refreshing data: {str(e)}")

    def export_data(self) -> None:
        """Export battery data to file."""
        try:
            from tkinter import filedialog
            import json

            if not self.battery_data_history:
                self.show_info("No data to export")
                return

            # Ask user for file location
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Export Battery Data",
            )

            if filename:
                # Prepare data for export
                export_data = {
                    "export_timestamp": datetime.now().isoformat(),
                    "data_points": len(self.battery_data_history),
                    "battery_data": [],
                }

                for entry in self.battery_data_history:
                    export_entry = {
                        "timestamp": entry["timestamp"].isoformat(),
                        "data": entry["data"],
                    }
                    export_data["battery_data"].append(export_entry)

                # Write to file
                with open(filename, "w") as f:
                    json.dump(export_data, f, indent=2)

                self.show_info(f"Data exported to {filename}")

        except Exception as e:
            self.logger.error(f"Error exporting data: {e}")
            self.show_error(f"Error exporting data: {str(e)}")

    def on_closing(self) -> None:
        """Handle window closing event."""
        try:
            # Stop monitoring
            if self.monitoring_active:
                self.stop_monitoring()

            # Close window
            self.destroy()

        except Exception as e:
            self.logger.error(f"Error during window closing: {e}")

    def show_info(self, message: str) -> None:
        """Show information message.

        Args:
            message: Message to display
        """
        try:
            from tkinter import messagebox

            messagebox.showinfo("Battery Health Monitor", message)
        except Exception as e:
            self.logger.error(f"Error showing info message: {e}")

    def show_error(self, message: str) -> None:
        """Show error message.

        Args:
            message: Error message to display
        """
        try:
            from tkinter import messagebox

            messagebox.showerror("Battery Health Monitor - Error", message)
        except Exception as e:
            self.logger.error(f"Error showing error message: {e}")


def main():
    """Main function for testing the battery health widget."""
    try:
        root = tk.Tk()
        app = BatteryHealthWidget(root)

        # Set up window closing handler
        root.protocol("WM_DELETE_WINDOW", app.on_closing)

        root.mainloop()

    except Exception as e:
        print(f"Error running battery health widget: {e}")


if __name__ == "__main__":
    main()
