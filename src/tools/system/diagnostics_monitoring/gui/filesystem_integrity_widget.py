"""Filesystem integrity monitoring GUI widget."""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    from PyQt5.QtCore import Qt, QThread, QTimer, pyqtSignal
    from PyQt5.QtGui import QColor, QFont, QPalette
    from PyQt5.QtWidgets import (
        QCheckBox,
        QComboBox,
        QFileDialog,
        QFrame,
        QGridLayout,
        QGroupBox,
        QHBoxLayout,
        QHeaderView,
        QLabel,
        QMessageBox,
        QScrollArea,
        QSpinBox,
        QSplitter,
        QTableWidget,
        QTableWidgetItem,
        QTabWidget,
        QTextEdit,
        QTreeWidget,
        QTreeWidgetItem,
        QVBoxLayout,
        QWidget,
    )

    from src.gui.components.buttons import PrimaryButton, SecondaryButton
    from src.gui.components.loading_indicator import LoadingIndicator

    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

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

    class QThread:
        pass


from core.error_handler import error_handler

from ..core.platform_detector import get_platform_detector
from ..monitors.filesystem.integrity_monitor import IntegrityMonitor, ScanType


class ScanWorker(QThread):
    """Worker thread for running filesystem scans."""

    progress_updated = pyqtSignal(dict)
    scan_completed = pyqtSignal(dict)
    scan_error = pyqtSignal(str)

    def __init__(
        self, integrity_monitor: IntegrityMonitor, scan_config: Dict[str, Any]
    ):
        """Initialize scan worker.

        Args:
            integrity_monitor: Integrity monitor instance
            scan_config: Scan configuration
        """
        super().__init__()
        self.integrity_monitor = integrity_monitor
        self.scan_config = scan_config
        self.logger = logging.getLogger("RFU.DiagnosticsMonitoring.ScanWorker")

    def run(self):
        """Run the filesystem scan."""
        try:

            def progress_callback(progress_data: Dict[str, Any]) -> None:
                self.progress_updated.emit(progress_data)

            result = self.integrity_monitor.start_scan(
                scan_type=self.scan_config.get("scan_type", ScanType.QUICK),
                paths=self.scan_config.get("paths"),
                config_override=self.scan_config.get("config_override"),
                callback=progress_callback,
            )

            if result:
                # Wait for scan to complete and get results
                while self.integrity_monitor.is_scanning():
                    self.msleep(1000)  # Sleep for 1 second

                # Get final results
                scan_status = self.integrity_monitor.get_scan_status()
                if scan_status:
                    self.scan_completed.emit(scan_status)
                else:
                    self.scan_error.emit("Failed to get scan results")
            else:
                self.scan_error.emit("Failed to start scan")

        except Exception as e:
            self.logger.error(f"Error in scan worker: {e}")
            self.scan_error.emit(str(e))


class FilesystemIntegrityWidget(QWidget):
    """Filesystem integrity monitoring widget with progress visualization."""

    def __init__(self, parent=None):
        """Initialize the filesystem integrity widget.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        self.logger = logging.getLogger(
            "RFU.DiagnosticsMonitoring.FilesystemIntegrityWidget"
        )

        if not PYQT_AVAILABLE:
            self.logger.error("PyQt5 not available - GUI will not function")
            return

        # Initialize monitoring components
        self.integrity_monitor = IntegrityMonitor()
        self.platform_detector = get_platform_detector()

        # Scan state
        self.current_scan_worker: Optional[ScanWorker] = None
        self.scan_history: List[Dict[str, Any]] = []

        # Setup UI
        self.setup_ui()

        # Setup timers
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_display)
        self.update_timer.start(5000)  # Update every 5 seconds

        # Initial update
        self.update_display()

    def setup_ui(self):
        """Setup the user interface."""
        if not PYQT_AVAILABLE:
            return

        layout = QVBoxLayout(self)

        # Create main splitter
        main_splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(main_splitter)

        # Left panel - Controls and status
        left_panel = self.create_control_panel()
        main_splitter.addWidget(left_panel)

        # Right panel - Results and details
        right_panel = self.create_results_panel()
        main_splitter.addWidget(right_panel)

        # Set splitter proportions
        main_splitter.setSizes([300, 700])

        # Status bar
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)

    def create_control_panel(self) -> QWidget:
        """Create the control panel.

        Returns:
            Control panel widget
        """
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Scan configuration group
        scan_group = QGroupBox("Scan Configuration")
        scan_layout = QGridLayout(scan_group)

        # Scan type selection
        scan_layout.addWidget(QLabel("Scan Type:"), 0, 0)
        self.scan_type_combo = QComboBox()
        self.scan_type_combo.setAccessibleName("Scan type")
        self.scan_type_combo.addItems(
            ["Quick Scan", "Full Scan", "Deep Scan", "Custom Scan"]
        )
        scan_layout.addWidget(self.scan_type_combo, 0, 1)

        # Scan paths
        scan_layout.addWidget(QLabel("Scan Paths:"), 1, 0)
        self.paths_button = SecondaryButton("Select Paths...")
        self.paths_button.setAccessibleName("Select scan paths")
        self.paths_button.clicked.connect(self.select_scan_paths)
        scan_layout.addWidget(self.paths_button, 1, 1)

        # Scan options
        self.checksum_check = QCheckBox("Verify Checksums")
        self.checksum_check.setChecked(True)
        self.checksum_check.setAccessibleName("Verify checksums")
        self.checksum_check.setMinimumHeight(44)
        scan_layout.addWidget(self.checksum_check, 2, 0, 1, 2)

        self.permissions_check = QCheckBox("Check Permissions")
        self.permissions_check.setChecked(True)
        self.permissions_check.setAccessibleName("Check permissions")
        self.permissions_check.setMinimumHeight(44)
        scan_layout.addWidget(self.permissions_check, 3, 0, 1, 2)

        self.timestamps_check = QCheckBox("Verify Timestamps")
        self.timestamps_check.setChecked(True)
        self.timestamps_check.setAccessibleName("Verify timestamps")
        self.timestamps_check.setMinimumHeight(44)
        scan_layout.addWidget(self.timestamps_check, 4, 0, 1, 2)

        # Max depth
        scan_layout.addWidget(QLabel("Max Depth:"), 5, 0)
        self.max_depth_spin = QSpinBox()
        self.max_depth_spin.setAccessibleName("Maximum scan depth")
        self.max_depth_spin.setMinimumHeight(44)
        self.max_depth_spin.setRange(1, 50)
        self.max_depth_spin.setValue(10)
        scan_layout.addWidget(self.max_depth_spin, 5, 1)

        layout.addWidget(scan_group)

        # Scan controls
        controls_group = QGroupBox("Scan Controls")
        controls_layout = QVBoxLayout(controls_group)

        self.start_scan_button = PrimaryButton("Start Scan")
        self.start_scan_button.setAccessibleName("Start filesystem scan")
        self.start_scan_button.clicked.connect(self.start_scan)
        controls_layout.addWidget(self.start_scan_button)

        self.stop_scan_button = SecondaryButton("Stop Scan")
        self.stop_scan_button.setAccessibleName("Stop filesystem scan")
        self.stop_scan_button.clicked.connect(self.stop_scan)
        self.stop_scan_button.setEnabled(False)
        controls_layout.addWidget(self.stop_scan_button)

        layout.addWidget(controls_group)

        # Progress group
        progress_group = QGroupBox("Scan Progress")
        progress_layout = QVBoxLayout(progress_group)

        self.progress_bar = LoadingIndicator(parent=self, message="Scanning...")
        progress_layout.addWidget(self.progress_bar)

        self.progress_label = QLabel("No scan running")
        progress_layout.addWidget(self.progress_label)

        self.files_scanned_label = QLabel("Files scanned: 0")
        progress_layout.addWidget(self.files_scanned_label)

        self.errors_found_label = QLabel("Errors found: 0")
        progress_layout.addWidget(self.errors_found_label)

        layout.addWidget(progress_group)

        # Scheduled scans group
        schedule_group = QGroupBox("Scheduled Scans")
        schedule_layout = QVBoxLayout(schedule_group)

        self.schedule_button = SecondaryButton("Schedule Scan...")
        self.schedule_button.setAccessibleName("Schedule a scan")
        self.schedule_button.clicked.connect(self.schedule_scan)
        schedule_layout.addWidget(self.schedule_button)

        self.scheduled_scans_list = QTreeWidget()
        self.scheduled_scans_list.setAccessibleName("Scheduled scans list")
        self.scheduled_scans_list.setHeaderLabels(["Type", "Next Run", "Recurring"])
        schedule_layout.addWidget(self.scheduled_scans_list)

        layout.addWidget(schedule_group)

        # Add stretch to push everything to top
        layout.addStretch()

        return panel

    def create_results_panel(self) -> QWidget:
        """Create the results panel.

        Returns:
            Results panel widget
        """
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Create tab widget for different views
        self.results_tabs = QTabWidget()
        self.results_tabs.setAccessibleName("Scan results tabs")
        layout.addWidget(self.results_tabs)

        # Overview tab
        overview_tab = self.create_overview_tab()
        self.results_tabs.addTab(overview_tab, "Overview")

        # Scan Results tab
        results_tab = self.create_scan_results_tab()
        self.results_tabs.addTab(results_tab, "Scan Results")

        # Corruption Analysis tab
        corruption_tab = self.create_corruption_analysis_tab()
        self.results_tabs.addTab(corruption_tab, "Corruption Analysis")

        # Repair Recommendations tab
        repair_tab = self.create_repair_recommendations_tab()
        self.results_tabs.addTab(repair_tab, "Repair Recommendations")

        # History tab
        history_tab = self.create_history_tab()
        self.results_tabs.addTab(history_tab, "Scan History")

        return panel

    def create_overview_tab(self) -> QWidget:
        """Create the overview tab.

        Returns:
            Overview tab widget
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # System info group
        system_group = QGroupBox("System Information")
        system_layout = QGridLayout(system_group)

        self.platform_label = QLabel(
            f"Platform: {self.platform_detector.platform.value}"
        )
        system_layout.addWidget(self.platform_label, 0, 0, 1, 2)

        self.filesystem_count_label = QLabel("Filesystems: 0")
        system_layout.addWidget(self.filesystem_count_label, 1, 0)

        self.last_scan_label = QLabel("Last scan: Never")
        system_layout.addWidget(self.last_scan_label, 1, 1)

        layout.addWidget(system_group)

        # Health status group
        health_group = QGroupBox("Filesystem Health Status")
        health_layout = QVBoxLayout(health_group)

        self.health_status_label = QLabel("Status: Unknown")
        self.health_status_label.setFont(Typography.h3())
        health_layout.addWidget(self.health_status_label)

        self.health_details_text = QTextEdit()
        self.health_details_text.setAccessibleName("Filesystem health details")
        self.health_details_text.setMaximumHeight(100)
        self.health_details_text.setReadOnly(True)
        health_layout.addWidget(self.health_details_text)

        layout.addWidget(health_group)

        # Quick stats group
        stats_group = QGroupBox("Quick Statistics")
        stats_layout = QGridLayout(stats_group)

        self.total_scans_label = QLabel("Total scans: 0")
        stats_layout.addWidget(self.total_scans_label, 0, 0)

        self.corruptions_found_label = QLabel("Corruptions found: 0")
        stats_layout.addWidget(self.corruptions_found_label, 0, 1)

        self.repairs_suggested_label = QLabel("Repairs suggested: 0")
        stats_layout.addWidget(self.repairs_suggested_label, 1, 0)

        self.avg_scan_time_label = QLabel("Avg scan time: 0s")
        stats_layout.addWidget(self.avg_scan_time_label, 1, 1)

        layout.addWidget(stats_group)

        # Add stretch
        layout.addStretch()

        return tab

    def create_scan_results_tab(self) -> QWidget:
        """Create the scan results tab.

        Returns:
            Scan results tab widget
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Results table
        self.results_table = QTableWidget()
        self.results_table.setAccessibleName("Scan results table")
        self.results_table.setColumnCount(6)
        self.results_table.setHorizontalHeaderLabels(
            ["Path", "Type", "Size", "Status", "Issues", "Last Modified"]
        )

        # Make table sortable and resizable
        self.results_table.setSortingEnabled(True)
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setStretchLastSection(True)

        layout.addWidget(self.results_table)

        # Export button
        export_layout = QHBoxLayout()
        export_layout.addStretch()

        self.export_results_button = SecondaryButton("Export Results...")
        self.export_results_button.setAccessibleName("Export scan results")
        self.export_results_button.clicked.connect(self.export_results)
        export_layout.addWidget(self.export_results_button)

        layout.addLayout(export_layout)

        return tab

    def create_corruption_analysis_tab(self) -> QWidget:
        """Create the corruption analysis tab.

        Returns:
            Corruption analysis tab widget
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Corruption summary
        summary_group = QGroupBox("Corruption Summary")
        summary_layout = QGridLayout(summary_group)

        self.corruption_count_label = QLabel("Total corruptions: 0")
        summary_layout.addWidget(self.corruption_count_label, 0, 0)

        self.critical_count_label = QLabel("Critical: 0")
        summary_layout.addWidget(self.critical_count_label, 0, 1)

        self.high_count_label = QLabel("High: 0")
        summary_layout.addWidget(self.high_count_label, 1, 0)

        self.medium_count_label = QLabel("Medium: 0")
        summary_layout.addWidget(self.medium_count_label, 1, 1)

        layout.addWidget(summary_group)

        # Corruption details table
        self.corruption_table = QTableWidget()
        self.corruption_table.setAccessibleName("Corruption details table")
        self.corruption_table.setColumnCount(5)
        self.corruption_table.setHorizontalHeaderLabels(
            ["Path", "Type", "Severity", "Description", "Timestamp"]
        )

        header = self.corruption_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setStretchLastSection(True)

        layout.addWidget(self.corruption_table)

        return tab

    def create_repair_recommendations_tab(self) -> QWidget:
        """Create the repair recommendations tab.

        Returns:
            Repair recommendations tab widget
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Recommendations table
        self.recommendations_table = QTableWidget()
        self.recommendations_table.setAccessibleName("Repair recommendations table")
        self.recommendations_table.setColumnCount(6)
        self.recommendations_table.setHorizontalHeaderLabels(
            [
                "Priority",
                "Action",
                "Description",
                "Command",
                "Auto",
                "Time Est.",
            ]
        )

        header = self.recommendations_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setStretchLastSection(True)

        layout.addWidget(self.recommendations_table)

        # Action buttons
        action_layout = QHBoxLayout()

        self.apply_selected_button = PrimaryButton("Apply Selected")
        self.apply_selected_button.setAccessibleName("Apply selected repairs")
        self.apply_selected_button.clicked.connect(self.apply_selected_recommendations)
        action_layout.addWidget(self.apply_selected_button)

        self.generate_script_button = SecondaryButton("Generate Script...")
        self.generate_script_button.setAccessibleName("Generate repair script")
        self.generate_script_button.clicked.connect(self.generate_repair_script)
        action_layout.addWidget(self.generate_script_button)

        action_layout.addStretch()
        layout.addLayout(action_layout)

        return tab

    def create_history_tab(self) -> QWidget:
        """Create the scan history tab.

        Returns:
            History tab widget
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # History table
        self.history_table = QTableWidget()
        self.history_table.setAccessibleName("Scan history table")
        self.history_table.setColumnCount(7)
        self.history_table.setHorizontalHeaderLabels(
            [
                "Date",
                "Type",
                "Duration",
                "Files",
                "Errors",
                "Status",
                "Actions",
            ]
        )

        header = self.history_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setStretchLastSection(True)

        layout.addWidget(self.history_table)

        # History controls
        history_controls = QHBoxLayout()

        self.clear_history_button = SecondaryButton("Clear History")
        self.clear_history_button.setAccessibleName("Clear scan history")
        self.clear_history_button.clicked.connect(self.clear_scan_history)
        history_controls.addWidget(self.clear_history_button)

        self.export_history_button = SecondaryButton("Export History...")
        self.export_history_button.setAccessibleName("Export scan history")
        self.export_history_button.clicked.connect(self.export_scan_history)
        history_controls.addWidget(self.export_history_button)

        history_controls.addStretch()
        layout.addLayout(history_controls)

        return tab

    def select_scan_paths(self):
        """Open dialog to select scan paths."""
        if not PYQT_AVAILABLE:
            return

        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.Directory)
        dialog.setOption(QFileDialog.ShowDirsOnly, True)

        if dialog.exec_():
            selected_paths = dialog.selectedFiles()
            if selected_paths:
                self.scan_paths = selected_paths
                self.paths_button.setText(f"Paths: {len(selected_paths)} selected")

    def start_scan(self):
        """Start a filesystem integrity scan."""
        if not PYQT_AVAILABLE:
            return

        try:
            # Prepare scan configuration
            scan_type_map = {
                "Quick Scan": ScanType.QUICK,
                "Full Scan": ScanType.FULL,
                "Deep Scan": ScanType.DEEP,
                "Custom Scan": ScanType.CUSTOM,
            }

            scan_type = scan_type_map[self.scan_type_combo.currentText()]

            config_override = {
                "check_checksums": self.checksum_check.isChecked(),
                "verify_permissions": self.permissions_check.isChecked(),
                "verify_timestamps": self.timestamps_check.isChecked(),
                "max_depth": self.max_depth_spin.value(),
            }

            scan_config = {
                "scan_type": scan_type,
                "paths": getattr(self, "scan_paths", None),
                "config_override": config_override,
            }

            # Start scan worker
            self.current_scan_worker = ScanWorker(self.integrity_monitor, scan_config)
            self.current_scan_worker.progress_updated.connect(self.update_scan_progress)
            self.current_scan_worker.scan_completed.connect(self.scan_completed)
            self.current_scan_worker.scan_error.connect(self.scan_error)
            self.current_scan_worker.start()

            # Update UI state
            self.start_scan_button.setEnabled(False)
            self.stop_scan_button.setEnabled(True)
            self.progress_bar.start()
            self.progress_bar.set_progress(0)
            self.progress_label.setText("Starting scan...")
            self.status_label.setText("Scan in progress...")

        except Exception as e:
            self.logger.error(f"Error starting scan: {e}")
            QMessageBox.critical(self, "Error", f"Failed to start scan: {e}")

    def stop_scan(self):
        """Stop the current scan."""
        if not PYQT_AVAILABLE:
            return

        try:
            if self.current_scan_worker and self.current_scan_worker.isRunning():
                self.integrity_monitor.stop_scan()
                self.current_scan_worker.quit()
                self.current_scan_worker.wait(5000)  # Wait up to 5 seconds

            self.scan_stopped()

        except Exception as e:
            self.logger.error(f"Error stopping scan: {e}")
            QMessageBox.warning(self, "Warning", f"Error stopping scan: {e}")

    def update_scan_progress(self, progress_data: Dict[str, Any]):
        """Update scan progress display.

        Args:
            progress_data: Progress information
        """
        if not PYQT_AVAILABLE:
            return

        try:
            progress = progress_data.get("progress_percent", 0)
            files_scanned = progress_data.get("files_scanned", 0)
            errors_found = progress_data.get("errors_found", 0)
            current_path = progress_data.get("current_path", "")

            self.progress_bar.set_progress(int(progress))
            self.progress_label.setText(f"Scanning: {current_path}")
            self.files_scanned_label.setText(f"Files scanned: {files_scanned}")
            self.errors_found_label.setText(f"Errors found: {errors_found}")

        except Exception as e:
            self.logger.error(f"Error updating scan progress: {e}")

    def scan_completed(self, scan_result: Dict[str, Any]):
        """Handle scan completion.

        Args:
            scan_result: Scan result data
        """
        if not PYQT_AVAILABLE:
            return

        try:
            # Add to history
            self.scan_history.append(scan_result)

            # Update UI
            self.scan_stopped()
            self.progress_bar.set_progress(100)
            self.progress_label.setText("Scan completed")
            self.status_label.setText("Scan completed successfully")

            # Update displays
            self.update_display()
            self.populate_scan_results(scan_result)

            # Show completion message
            QMessageBox.information(
                self,
                "Scan Complete",
                "Filesystem integrity scan completed successfully.",
            )

        except Exception as e:
            self.logger.error(f"Error handling scan completion: {e}")

    def scan_error(self, error_message: str):
        """Handle scan error.

        Args:
            error_message: Error message
        """
        if not PYQT_AVAILABLE:
            return

        self.progress_bar.stop()
        self.scan_stopped()
        self.progress_label.setText(f"Scan failed: {error_message}")
        self.status_label.setText("Scan failed")

        QMessageBox.critical(self, "Scan Error", f"Scan failed: {error_message}")

    def scan_stopped(self):
        """Update UI when scan is stopped."""
        if not PYQT_AVAILABLE:
            return

        self.start_scan_button.setEnabled(True)
        self.stop_scan_button.setEnabled(False)
        self.progress_bar.stop()
        self.current_scan_worker = None

    def populate_scan_results(self, scan_result: Dict[str, Any]):
        """Populate scan results in the UI.

        Args:
            scan_result: Scan result data
        """
        if not PYQT_AVAILABLE:
            return

        try:
            # Update corruption analysis
            corruption_analysis = scan_result.get("corruption_analysis", {})
            self.populate_corruption_analysis(corruption_analysis)

            # Update repair recommendations
            repair_recommendations = scan_result.get("repair_recommendations", {})
            self.populate_repair_recommendations(repair_recommendations)

            # Update history
            self.populate_scan_history()

        except Exception as e:
            self.logger.error(f"Error populating scan results: {e}")

    def populate_corruption_analysis(self, analysis: Dict[str, Any]):
        """Populate corruption analysis tab.

        Args:
            analysis: Corruption analysis data
        """
        if not PYQT_AVAILABLE:
            return

        try:
            stats = analysis.get("statistics", {})
            corruptions = analysis.get("corruptions", [])

            # Update summary labels
            self.corruption_count_label.setText(
                f"Total corruptions: {stats.get('corruptions_found', 0)}"
            )
            self.critical_count_label.setText(
                f"Critical: {stats.get('critical_issues', 0)}"
            )
            self.high_count_label.setText(f"High: {stats.get('high_severity', 0)}")
            self.medium_count_label.setText(
                f"Medium: {stats.get('medium_severity', 0)}"
            )

            # Populate corruption table
            self.corruption_table.setRowCount(len(corruptions))

            for row, corruption in enumerate(corruptions):
                self.corruption_table.setItem(
                    row, 0, QTableWidgetItem(corruption.get("path", ""))
                )
                self.corruption_table.setItem(
                    row, 1, QTableWidgetItem(corruption.get("type", ""))
                )
                self.corruption_table.setItem(
                    row, 2, QTableWidgetItem(corruption.get("severity", ""))
                )
                self.corruption_table.setItem(
                    row, 3, QTableWidgetItem(corruption.get("description", ""))
                )
                self.corruption_table.setItem(
                    row, 4, QTableWidgetItem(corruption.get("timestamp", ""))
                )

        except Exception as e:
            self.logger.error(f"Error populating corruption analysis: {e}")

    def populate_repair_recommendations(self, recommendations: Dict[str, Any]):
        """Populate repair recommendations tab.

        Args:
            recommendations: Repair recommendations data
        """
        if not PYQT_AVAILABLE:
            return

        try:
            recs = recommendations.get("recommendations", [])

            self.recommendations_table.setRowCount(len(recs))

            for row, rec in enumerate(recs):
                self.recommendations_table.setItem(
                    row, 0, QTableWidgetItem(rec.get("priority", ""))
                )
                self.recommendations_table.setItem(
                    row, 1, QTableWidgetItem(rec.get("action", ""))
                )
                self.recommendations_table.setItem(
                    row, 2, QTableWidgetItem(rec.get("description", ""))
                )
                self.recommendations_table.setItem(
                    row, 3, QTableWidgetItem(rec.get("command", ""))
                )
                self.recommendations_table.setItem(
                    row,
                    4,
                    QTableWidgetItem(
                        "Yes" if rec.get("automation_possible", False) else "No"
                    ),
                )
                self.recommendations_table.setItem(
                    row, 5, QTableWidgetItem(rec.get("estimated_time", ""))
                )

        except Exception as e:
            self.logger.error(f"Error populating repair recommendations: {e}")

    def populate_scan_history(self):
        """Populate scan history tab."""
        if not PYQT_AVAILABLE:
            return

        try:
            self.history_table.setRowCount(len(self.scan_history))

            for row, scan in enumerate(self.scan_history):
                start_time = scan.get("start_time", "")
                if start_time:
                    try:
                        dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
                        date_str = dt.strftime("%Y-%m-%d %H:%M")
                    except:
                        date_str = start_time
                else:
                    date_str = "Unknown"

                self.history_table.setItem(row, 0, QTableWidgetItem(date_str))
                self.history_table.setItem(
                    row, 1, QTableWidgetItem(scan.get("scan_type", ""))
                )
                self.history_table.setItem(
                    row,
                    2,
                    QTableWidgetItem(f"{scan.get('duration_seconds', 0):.1f}s"),
                )

                stats = scan.get("statistics", {})
                self.history_table.setItem(
                    row,
                    3,
                    QTableWidgetItem(str(stats.get("files_scanned", 0))),
                )
                self.history_table.setItem(
                    row,
                    4,
                    QTableWidgetItem(str(stats.get("errors_encountered", 0))),
                )
                self.history_table.setItem(
                    row,
                    5,
                    QTableWidgetItem(
                        "Success" if scan.get("success", False) else "Failed"
                    ),
                )

        except Exception as e:
            self.logger.error(f"Error populating scan history: {e}")

    def update_display(self):
        """Update the display with current information."""
        if not PYQT_AVAILABLE:
            return

        try:
            # Update overview information
            metrics = self.integrity_monitor.get_scan_metrics()

            self.total_scans_label.setText(
                f"Total scans: {metrics.get('total_scans', 0)}"
            )
            self.corruptions_found_label.setText(
                f"Corruptions found: {metrics.get('corruptions_found', 0)}"
            )
            self.repairs_suggested_label.setText(
                f"Repairs suggested: {metrics.get('repairs_suggested', 0)}"
            )
            self.avg_scan_time_label.setText(
                f"Avg scan time: {metrics.get('average_scan_time', 0):.1f}s"
            )

            # Update health status
            health_status = self.integrity_monitor.get_health_status()
            status = health_status.get("status", "unknown")
            message = health_status.get("message", "No information available")

            self.health_status_label.setText(f"Status: {status.title()}")
            self.health_details_text.setText(message)

            # Set status color
            if status == "healthy":
                self.health_status_label.setStyleSheet("color: green;")
            elif status == "warning":
                self.health_status_label.setStyleSheet("color: orange;")
            elif status in ["critical", "corrupted"]:
                self.health_status_label.setStyleSheet("color: red;")
            else:
                self.health_status_label.setStyleSheet("color: gray;")

            # Update scheduled scans
            self.update_scheduled_scans_display()

        except Exception as e:
            self.logger.error(f"Error updating display: {e}")

    def update_scheduled_scans_display(self):
        """Update the scheduled scans display."""
        if not PYQT_AVAILABLE:
            return

        try:
            self.scheduled_scans_list.clear()

            scheduled_scans = self.integrity_monitor.get_scheduled_scans()
            for scan in scheduled_scans:
                item = QTreeWidgetItem(
                    [
                        scan.get("scan_type", ""),
                        scan.get("schedule_time", ""),
                        "Yes" if scan.get("recurring", False) else "No",
                    ]
                )
                self.scheduled_scans_list.addTopLevelItem(item)

        except Exception as e:
            self.logger.error(f"Error updating scheduled scans display: {e}")

    def schedule_scan(self):
        """Open dialog to schedule a scan."""
        if not PYQT_AVAILABLE:
            return

        # This would open a scheduling dialog
        QMessageBox.information(
            self,
            "Schedule Scan",
            "Scan scheduling dialog would open here.\n"
            "This feature requires additional implementation.",
        )

    def apply_selected_recommendations(self):
        """Apply selected repair recommendations."""
        if not PYQT_AVAILABLE:
            return

        selected_rows = set()
        for item in self.recommendations_table.selectedItems():
            selected_rows.add(item.row())

        if not selected_rows:
            QMessageBox.warning(self, "Warning", "No recommendations selected.")
            return

        reply = QMessageBox.question(
            self,
            "Apply Recommendations",
            f"Apply {len(selected_rows)} selected recommendations?\n"
            "This may require administrator privileges.",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            QMessageBox.information(
                self,
                "Apply Recommendations",
                "Recommendation application would be implemented here.\n"
                "This requires integration with system repair tools.",
            )

    def generate_repair_script(self):
        """Generate a repair script from recommendations."""
        if not PYQT_AVAILABLE:
            return

        dialog = QFileDialog()
        filename, _ = dialog.getSaveFileName(
            self,
            "Save Repair Script",
            "filesystem_repair_script.sh",
            "Shell Scripts (*.sh);;Batch Files (*.bat);;All Files (*)",
        )

        if filename:
            QMessageBox.information(
                self,
                "Generate Script",
                f"Repair script would be generated and saved to:\n{filename}\n\n"
                "This feature requires additional implementation.",
            )

    def export_results(self):
        """Export scan results to file."""
        if not PYQT_AVAILABLE:
            return

        dialog = QFileDialog()
        filename, _ = dialog.getSaveFileName(
            self,
            "Export Scan Results",
            "scan_results.json",
            "JSON Files (*.json);;CSV Files (*.csv);;All Files (*)",
        )

        if filename:
            QMessageBox.information(
                self,
                "Export Results",
                f"Scan results would be exported to:\n{filename}\n\n"
                "This feature requires additional implementation.",
            )

    def clear_scan_history(self):
        """Clear the scan history."""
        if not PYQT_AVAILABLE:
            return

        reply = QMessageBox.question(
            self,
            "Clear History",
            "Are you sure you want to clear all scan history?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self.scan_history.clear()
            self.populate_scan_history()
            QMessageBox.information(
                self, "History Cleared", "Scan history has been cleared."
            )

    def export_scan_history(self):
        """Export scan history to file."""
        if not PYQT_AVAILABLE:
            return

        dialog = QFileDialog()
        filename, _ = dialog.getSaveFileName(
            self,
            "Export Scan History",
            "scan_history.json",
            "JSON Files (*.json);;CSV Files (*.csv);;All Files (*)",
        )

        if filename:
            QMessageBox.information(
                self,
                "Export History",
                f"Scan history would be exported to:\n{filename}\n\n"
                "This feature requires additional implementation.",
            )

    def get_widget_info(self) -> Dict[str, Any]:
        """Get widget information for integration.

        Returns:
            Dict containing widget information
        """
        return {
            "name": "Filesystem Integrity Monitor",
            "description": "Monitor and analyze filesystem integrity",
            "version": "1.0.0",
            "requires_admin": True,
            "supported_platforms": ["windows", "macos", "linux"],
            "features": [
                "Filesystem scanning",
                "Corruption detection",
                "Repair recommendations",
                "Scheduled scans",
                "Progress visualization",
            ],
        }


# Standalone testing
if __name__ == "__main__":
    if PYQT_AVAILABLE:
        import sys

        from PyQt5.QtWidgets import QApplication

        from src.gui.themes import Typography

        app = QApplication(sys.argv)
        widget = FilesystemIntegrityWidget()
        widget.show()
        sys.exit(app.exec_())
    else:
        print("PyQt5 not available - cannot run standalone test")
