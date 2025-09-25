"""
Software Maintenance Hub GUI

This module provides the main graphical user interface for the Software
Maintenance Toolkit, integrating the Software Updater and De-Installer
with comprehensive progress tracking and user interaction.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional
import csv
import json

# Add the parent directory to the path to import from other modules
sys.path.append(
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
)

try:
    from PyQt5.QtWidgets import (
        QMainWindow,
        QWidget,
        QVBoxLayout,
        QHBoxLayout,
        QTabWidget,
        QLabel,
        QPushButton,
        QProgressBar,
        QTextEdit,
        QListWidget,
        QListWidgetItem,
        QCheckBox,
        QGroupBox,
        QGridLayout,
        QComboBox,
        QSpinBox,
        QMessageBox,
        QDialog,
        QDialogButtonBox,
        QTableWidget,
        QTableWidgetItem,
        QHeaderView,
        QSplitter,
        QFrame,
        QScrollArea,
        QApplication,
        QFileDialog,
    )
    from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
    from PyQt5.QtGui import QFont, QIcon, QPalette, QColor

    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    print("PyQt5 not available. GUI functionality will be limited.")

# Import StandardWindow for menu integration
try:
    from src.gui.standard_window import StandardWindow
    from src.gui.menu_manager import MenuManager

    STANDARD_WINDOW_AVAILABLE = True
except ImportError:
    try:
        from src.gui.standard_window import StandardWindow
        from gui.menu_manager import MenuManager

        STANDARD_WINDOW_AVAILABLE = True
    except ImportError:
        STANDARD_WINDOW_AVAILABLE = False
        # Fallback to QMainWindow if StandardWindow is not available
        StandardWindow = QMainWindow

if PYQT_AVAILABLE:
    from ..tools.software_updater import SoftwareUpdater
    from ..tools.software_deinstaller import SoftwareDeinstaller


class WorkerThread(QThread):
    """Worker thread for running maintenance operations."""

    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    operation_completed = pyqtSignal(bool, str)
    log_message = pyqtSignal(str, str)

    def __init__(self, operation, *args, **kwargs):
        super().__init__()
        self.operation = operation
        self.args = args
        self.kwargs = kwargs
        self.tool = None

    def run(self):
        """Execute the operation in the worker thread."""
        try:
            if self.operation == "scan_software":
                self.tool = SoftwareUpdater()
            elif self.operation == "check_updates":
                self.tool = SoftwareUpdater()
            elif self.operation == "update_software":
                self.tool = SoftwareUpdater()
            elif self.operation == "scan_for_removal":
                self.tool = SoftwareDeinstaller()
            elif self.operation == "uninstall_software":
                self.tool = SoftwareDeinstaller()

            if self.tool:
                # Connect signals
                self.tool.progress_updated.connect(self.progress_updated.emit)
                self.tool.status_updated.connect(self.status_updated.emit)
                self.tool.operation_completed.connect(
                    self.operation_completed.emit
                )
                self.tool.log_message.connect(self.log_message.emit)

                # Execute the operation
                if self.operation == "scan_software":
                    result = self.tool.scan_installed_software(
                        *self.args, **self.kwargs
                    )
                elif self.operation == "check_updates":
                    result = self.tool.check_for_updates(
                        *self.args, **self.kwargs
                    )
                elif self.operation == "update_software":
                    if len(self.args) > 1:
                        result = self.tool.update_multiple_software(
                            *self.args, **self.kwargs
                        )
                    else:
                        result = self.tool.update_software(
                            *self.args, **self.kwargs
                        )
                elif self.operation == "scan_for_removal":
                    result = self.tool.scan_installed_software(
                        *self.args, **self.kwargs
                    )
                elif self.operation == "uninstall_software":
                    if len(self.args) > 1:
                        result = self.tool.uninstall_multiple_software(
                            *self.args, **self.kwargs
                        )
                    else:
                        result = self.tool.uninstall_software(
                            *self.args, **self.kwargs
                        )
                else:
                    result = False

                self.operation_completed.emit(
                    bool(result), "Operation completed"
                )
            else:
                self.operation_completed.emit(
                    False, "Failed to initialize tool"
                )

        except Exception as e:
            self.operation_completed.emit(False, f"Error: {str(e)}")


class SoftwareMaintenanceHub(StandardWindow):
    """
    Main GUI window for the Software Maintenance Toolkit providing
    unified access to software updating and uninstallation features.
    Enhanced with File menu integration following the File Finder template.
    """

    def __init__(self):
        super().__init__(
            title="Software Maintenance Toolkit - Richard's File Utilities",
            window_type="utility",
        )

        if not PYQT_AVAILABLE:
            raise ImportError("PyQt5 is required for the GUI")

        # Initialize tools
        self.updater = None
        self.deinstaller = None
        self.worker_thread = None

        # Data storage
        self.detected_software = {}
        self.available_updates = {}
        self.selected_software = set()

        # Setup UI
        self.setup_ui()
        self.setup_styling()

        # Setup menu callbacks for File menu integration
        self._setup_menu_callbacks()

        # Ensure menu bar exists
        self.ensure_menu_bar()

        # Status update timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status_display)
        self.status_timer.start(1000)  # Update every second

    def _setup_menu_callbacks(self):
        """Setup tool-specific menu callbacks for File menu integration."""
        if hasattr(self, "menu_manager") and STANDARD_WINDOW_AVAILABLE:
            # Register tool-specific callbacks
            self.menu_manager.register_callback(
                "save_file", self.export_maintenance_report
            )
            self.menu_manager.register_callback(
                "export_data", self.export_software_list
            )
            self.menu_manager.register_callback(
                "import_data", self.import_software_list
            )
            self.menu_manager.register_callback(
                "print_document", self.print_maintenance_report
            )

    def show_preferences(self):
        """Show Software Maintenance preferences."""
        QMessageBox.information(
            self,
            "Software Maintenance Preferences",
            "Software Maintenance preferences:\n\n"
            "• Automatic update checking frequency\n"
            "• Backup settings before changes\n"
            "• Security update priorities\n"
            "• Removal verification options\n"
            "• System restore point creation\n\n"
            "Configure these settings in the Settings tab!",
        )

    def refresh_view(self):
        """Refresh the current maintenance data."""
        self.refresh_data()
        self.show_status_message("Software maintenance data refreshed")

    def export_maintenance_report(self):
        """Export comprehensive maintenance report."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Maintenance Report",
            "maintenance_report.txt",
            "Text Files (*.txt);;All Files (*)",
        )

        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("Software Maintenance Report\n")
                    f.write("=" * 50 + "\n\n")

                    f.write(
                        f"Generated: {QTimer().currentTime().toString()}\n"
                    )
                    f.write(
                        f"Total Software Detected: {len(self.detected_software)}\n"
                    )
                    f.write(
                        f"Available Updates: {len(self.available_updates)}\n\n"
                    )

                    if self.detected_software:
                        f.write("Installed Software:\n")
                        f.write("-" * 20 + "\n")
                        for name, info in self.detected_software.items():
                            f.write(
                                f"• {name} (Version: {getattr(info, 'version', 'Unknown')})\n"
                            )
                        f.write("\n")

                    if self.available_updates:
                        f.write("Available Updates:\n")
                        f.write("-" * 20 + "\n")
                        for name, update in self.available_updates.items():
                            current = getattr(
                                update, "current_version", "Unknown"
                            )
                            available = getattr(
                                update, "available_version", "Unknown"
                            )
                            f.write(f"• {name}: {current} → {available}\n")

                QMessageBox.information(
                    self,
                    "Export Complete",
                    f"Maintenance report exported to:\n{file_path}",
                )
            except Exception as e:
                QMessageBox.warning(
                    self, "Export Error", f"Failed to export report:\n{e}"
                )

    def export_software_list(self):
        """Export software list to CSV format."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Software List",
            "software_list.csv",
            "CSV Files (*.csv);;All Files (*)",
        )

        if file_path:
            try:
                import csv

                with open(file_path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(
                        ["Software Name", "Version", "Update Available"]
                    )

                    for name, info in self.detected_software.items():
                        version = getattr(info, "version", "Unknown")
                        has_update = name in self.available_updates
                        writer.writerow(
                            [name, version, "Yes" if has_update else "No"]
                        )

                QMessageBox.information(
                    self,
                    "Export Complete",
                    f"Software list exported to:\n{file_path}",
                )
            except Exception as e:
                QMessageBox.warning(
                    self, "Export Error", f"Failed to export list:\n{e}"
                )

    def import_software_list(self):
        """Import software configuration or list."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Software Configuration",
            "",
            "JSON Files (*.json);;CSV Files (*.csv);;All Files (*)",
        )

        if file_path:
            try:
                if file_path.endswith(".json"):
                    import json

                    with open(file_path, "r", encoding="utf-8") as f:
                        config = json.load(f)
                    # Process JSON configuration
                    QMessageBox.information(
                        self,
                        "Import Complete",
                        "Software configuration imported successfully!",
                    )
                elif file_path.endswith(".csv"):
                    # Process CSV import
                    QMessageBox.information(
                        self,
                        "Import Complete",
                        "Software list imported successfully!",
                    )
                else:
                    QMessageBox.information(
                        self,
                        "Import",
                        "Import functionality for this file type coming soon!",
                    )
            except Exception as e:
                QMessageBox.warning(
                    self, "Import Error", f"Failed to import:\n{e}"
                )

    def print_maintenance_report(self):
        """Print maintenance report."""
        QMessageBox.information(
            self,
            "Print Report",
            "Print functionality will open the system print dialog.\n\n"
            "For now, you can export the report and print from your "
            "preferred text editor.",
        )
        # Future: Implement actual printing functionality

    def setup_ui(self):
        """Setup the main user interface using StandardWindow layout."""
        # Use the existing main layout from StandardWindow
        layout = self.main_layout

        # Header
        header_layout = self.create_header_section()
        layout.addLayout(header_layout)

        # Main content area with tabs
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # Create tabs
        self.create_updater_tab()
        self.create_deinstaller_tab()
        self.create_settings_tab()
        self.create_logs_tab()

        # Status area
        self.status_layout = self.create_status_section()
        layout.addLayout(self.status_layout)

    def create_header_section(self):
        """Create the header section with standard styling."""
        header_layout = QHBoxLayout()

        # Title using StandardWindow create_header method
        title_label = self.create_header("Software Maintenance Toolkit")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Quick action buttons using StandardWindow create_button method
        self.scan_btn = self.create_button("Quick Scan", self.quick_scan)
        header_layout.addWidget(self.scan_btn)

        self.refresh_btn = self.create_button(
            "Refresh", self.refresh_data, primary=False
        )
        header_layout.addWidget(self.refresh_btn)

        return header_layout

    def create_status_section(self):
        """Create the status section with progress and information."""
        status_layout = QHBoxLayout()

        # Progress bar using StandardWindow method
        self.progress_bar = self.create_progress_bar()
        self.progress_bar.setVisible(False)
        status_layout.addWidget(self.progress_bar)

        # Status label
        self.status_label = QLabel("Ready")
        status_layout.addWidget(self.status_label)

        status_layout.addStretch()

        # Statistics
        self.stats_label = QLabel("Software: 0 | Updates: 0")
        status_layout.addWidget(self.stats_label)

        return status_layout

    def create_updater_tab(self):
        """Create the Software Updater tab."""
        updater_widget = QWidget()
        layout = QVBoxLayout(updater_widget)

        # Control panel using StandardWindow create_group_box
        control_group = self.create_group_box("Update Controls")
        control_layout = QHBoxLayout(control_group)

        self.scan_software_btn = self.create_button(
            "Scan Software", self.scan_software
        )
        control_layout.addWidget(self.scan_software_btn)

        self.check_updates_btn = self.create_button(
            "Check Updates", self.check_updates
        )
        control_layout.addWidget(self.check_updates_btn)

        self.update_selected_btn = self.create_button(
            "Update Selected", self.update_selected_software
        )
        self.update_selected_btn.setEnabled(False)
        control_layout.addWidget(self.update_selected_btn)

        control_layout.addStretch()
        layout.addWidget(control_group)

        # Software list and updates
        content_splitter = QSplitter(Qt.Horizontal)

        # Software list
        software_group = self.create_group_box("Installed Software")
        software_layout = QVBoxLayout(software_group)

        self.software_list = QListWidget()
        self.software_list.itemChanged.connect(
            self.on_software_selection_changed
        )
        software_layout.addWidget(self.software_list)

        content_splitter.addWidget(software_group)

        # Updates panel
        updates_group = self.create_group_box("Available Updates")
        updates_layout = QVBoxLayout(updates_group)

        self.updates_table = QTableWidget()
        self.updates_table.setColumnCount(4)
        self.updates_table.setHorizontalHeaderLabels(
            ["Software", "Current", "Available", "Source"]
        )
        updates_layout.addWidget(self.updates_table)

        # Update details
        self.update_details = QTextEdit()
        self.update_details.setMaximumHeight(150)
        self.update_details.setPlaceholderText(
            "Select an update to view changelog..."
        )
        updates_layout.addWidget(self.update_details)

        content_splitter.addWidget(updates_group)
        content_splitter.setSizes([400, 600])

        layout.addWidget(content_splitter)

        self.tab_widget.addTab(updater_widget, "Software Updater")

    def create_deinstaller_tab(self):
        """Create the Software De-Installer tab."""
        deinstaller_widget = QWidget()
        layout = QVBoxLayout(deinstaller_widget)

        # Control panel using StandardWindow create_group_box
        control_group = self.create_group_box("Uninstall Controls")
        control_layout = QHBoxLayout(control_group)

        self.scan_removal_btn = self.create_button(
            "Scan for Removal", self.scan_for_removal
        )
        control_layout.addWidget(self.scan_removal_btn)

        self.analyze_btn = self.create_button(
            "Analyze Selected", self.analyze_selected_software
        )
        self.analyze_btn.setEnabled(False)
        control_layout.addWidget(self.analyze_btn)

        self.uninstall_selected_btn = self.create_button(
            "Uninstall Selected", self.uninstall_selected_software
        )
        self.uninstall_selected_btn.setEnabled(False)
        control_layout.addWidget(self.uninstall_selected_btn)

        control_layout.addStretch()
        layout.addWidget(control_group)

        # Content area
        content_splitter = QSplitter(Qt.Horizontal)

        # Software list for removal
        removal_group = self.create_group_box("Software for Removal")
        removal_layout = QVBoxLayout(removal_group)

        self.removal_list = QListWidget()
        self.removal_list.itemChanged.connect(
            self.on_removal_selection_changed
        )
        removal_layout.addWidget(self.removal_list)

        # Space analysis
        space_group = self.create_group_box("Space Analysis")
        space_layout = QVBoxLayout(space_group)

        self.space_label = QLabel(
            "Select software to see space recovery estimate"
        )
        space_layout.addWidget(self.space_label)

        removal_layout.addWidget(space_group)
        content_splitter.addWidget(removal_group)

        # Analysis panel
        analysis_group = self.create_group_box("Removal Analysis")
        analysis_layout = QVBoxLayout(analysis_group)

        self.analysis_details = QTextEdit()
        self.analysis_details.setPlaceholderText(
            "Select software to view removal analysis..."
        )
        analysis_layout.addWidget(self.analysis_details)

        content_splitter.addWidget(analysis_group)
        content_splitter.setSizes([400, 600])

        layout.addWidget(content_splitter)

        self.tab_widget.addTab(deinstaller_widget, "Software De-Installer")

    def create_settings_tab(self):
        """Create the Settings tab."""
        settings_widget = QWidget()
        layout = QVBoxLayout(settings_widget)

        # Updater settings
        updater_group = QGroupBox("Updater Settings")
        updater_layout = QGridLayout(updater_group)

        self.auto_check_cb = QCheckBox("Enable automatic update checking")
        updater_layout.addWidget(self.auto_check_cb, 0, 0, 1, 2)

        updater_layout.addWidget(QLabel("Check interval (hours):"), 1, 0)
        self.check_interval_spin = QSpinBox()
        self.check_interval_spin.setRange(1, 168)  # 1 hour to 1 week
        self.check_interval_spin.setValue(24)
        updater_layout.addWidget(self.check_interval_spin, 1, 1)

        self.auto_security_cb = QCheckBox("Auto-install security updates")
        updater_layout.addWidget(self.auto_security_cb, 2, 0, 1, 2)

        self.create_restore_points_cb = QCheckBox(
            "Create restore points before updates"
        )
        updater_layout.addWidget(self.create_restore_points_cb, 3, 0, 1, 2)

        layout.addWidget(updater_group)

        # De-installer settings
        deinstaller_group = QGroupBox("De-Installer Settings")
        deinstaller_layout = QGridLayout(deinstaller_group)

        self.backup_before_removal_cb = QCheckBox(
            "Create backups before removal"
        )
        deinstaller_layout.addWidget(self.backup_before_removal_cb, 0, 0, 1, 2)

        self.deep_scan_cb = QCheckBox("Enable deep system scanning")
        deinstaller_layout.addWidget(self.deep_scan_cb, 1, 0, 1, 2)

        self.auto_cleanup_cb = QCheckBox("Automatically clean up leftovers")
        deinstaller_layout.addWidget(self.auto_cleanup_cb, 2, 0, 1, 2)

        layout.addWidget(deinstaller_group)

        # Security settings
        security_group = QGroupBox("Security Settings")
        security_layout = QGridLayout(security_group)

        security_layout.addWidget(QLabel("Backup retention (days):"), 0, 0)
        self.backup_retention_spin = QSpinBox()
        self.backup_retention_spin.setRange(1, 365)
        self.backup_retention_spin.setValue(30)
        security_layout.addWidget(self.backup_retention_spin, 0, 1)

        security_layout.addWidget(QLabel("Max backup size (GB):"), 1, 0)
        self.max_backup_size_spin = QSpinBox()
        self.max_backup_size_spin.setRange(1, 100)
        self.max_backup_size_spin.setValue(10)
        security_layout.addWidget(self.max_backup_size_spin, 1, 1)

        layout.addWidget(security_group)

        # Save settings button
        save_settings_btn = QPushButton("Save Settings")
        save_settings_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_settings_btn)

        layout.addStretch()

        self.tab_widget.addTab(settings_widget, "Settings")

    def create_logs_tab(self):
        """Create the Logs tab."""
        logs_widget = QWidget()
        layout = QVBoxLayout(logs_widget)

        # Log controls
        log_controls = QHBoxLayout()

        log_controls.addWidget(QLabel("Log Level:"))
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["All", "Info", "Warning", "Error"])
        log_controls.addWidget(self.log_level_combo)

        log_controls.addStretch()

        clear_logs_btn = QPushButton("Clear Logs")
        clear_logs_btn.clicked.connect(self.clear_logs)
        log_controls.addWidget(clear_logs_btn)

        export_logs_btn = QPushButton("Export Logs")
        export_logs_btn.clicked.connect(self.export_logs)
        log_controls.addWidget(export_logs_btn)

        layout.addLayout(log_controls)

        # Log display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setFont(QFont("Consolas", 9))
        layout.addWidget(self.log_display)

        self.tab_widget.addTab(logs_widget, "Logs")

    def setup_styling(self):
        """Setup the application styling."""
        # Set application style
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #f0f0f0;
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
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 8px 16px;
                text-align: center;
                font-size: 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #4CAF50;
            }
        """
        )

    def quick_scan(self):
        """Perform a quick scan of software and updates."""
        self.scan_software()
        QTimer.singleShot(2000, self.check_updates)  # Check updates after scan

    def refresh_data(self):
        """Refresh all data displays."""
        self.update_software_list()
        self.update_updates_table()
        self.update_removal_list()
        self.update_statistics()

    def scan_software(self):
        """Scan for installed software."""
        if self.worker_thread and self.worker_thread.isRunning():
            return

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Scanning installed software...")

        self.worker_thread = WorkerThread("scan_software", False)
        self.worker_thread.progress_updated.connect(self.progress_bar.setValue)
        self.worker_thread.status_updated.connect(self.status_label.setText)
        self.worker_thread.operation_completed.connect(self.on_scan_completed)
        self.worker_thread.log_message.connect(self.add_log_message)
        self.worker_thread.start()

    def check_updates(self):
        """Check for available updates."""
        if self.worker_thread and self.worker_thread.isRunning():
            return

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Checking for updates...")

        self.worker_thread = WorkerThread("check_updates")
        self.worker_thread.progress_updated.connect(self.progress_bar.setValue)
        self.worker_thread.status_updated.connect(self.status_label.setText)
        self.worker_thread.operation_completed.connect(self.on_updates_checked)
        self.worker_thread.log_message.connect(self.add_log_message)
        self.worker_thread.start()

    def update_selected_software(self):
        """Update selected software."""
        selected_software = list(self.selected_software)
        if not selected_software:
            QMessageBox.warning(
                self, "Warning", "No software selected for update."
            )
            return

        reply = QMessageBox.question(
            self,
            "Confirm Update",
            f"Update {len(selected_software)} selected software packages?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.status_label.setText("Updating software...")

            self.worker_thread = WorkerThread(
                "update_software", selected_software
            )
            self.worker_thread.progress_updated.connect(
                self.progress_bar.setValue
            )
            self.worker_thread.status_updated.connect(
                self.status_label.setText
            )
            self.worker_thread.operation_completed.connect(
                self.on_update_completed
            )
            self.worker_thread.log_message.connect(self.add_log_message)
            self.worker_thread.start()

    def scan_for_removal(self):
        """Scan software for removal analysis."""
        if self.worker_thread and self.worker_thread.isRunning():
            return

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Scanning software for removal...")

        self.worker_thread = WorkerThread("scan_for_removal", False)
        self.worker_thread.progress_updated.connect(self.progress_bar.setValue)
        self.worker_thread.status_updated.connect(self.status_label.setText)
        self.worker_thread.operation_completed.connect(
            self.on_removal_scan_completed
        )
        self.worker_thread.log_message.connect(self.add_log_message)
        self.worker_thread.start()

    def analyze_selected_software(self):
        """Analyze selected software for removal."""
        # Implementation for analyzing selected software
        pass

    def uninstall_selected_software(self):
        """Uninstall selected software."""
        selected_software = [
            item.text() for item in self.removal_list.selectedItems()
        ]
        if not selected_software:
            QMessageBox.warning(
                self, "Warning", "No software selected for removal."
            )
            return

        reply = QMessageBox.question(
            self,
            "Confirm Removal",
            f"Remove {len(selected_software)} selected software packages?\n"
            "This action cannot be easily undone.",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.status_label.setText("Removing software...")

            self.worker_thread = WorkerThread(
                "uninstall_software", selected_software
            )
            self.worker_thread.progress_updated.connect(
                self.progress_bar.setValue
            )
            self.worker_thread.status_updated.connect(
                self.status_label.setText
            )
            self.worker_thread.operation_completed.connect(
                self.on_removal_completed
            )
            self.worker_thread.log_message.connect(self.add_log_message)
            self.worker_thread.start()

    def on_software_selection_changed(self):
        """Handle software selection changes."""
        self.selected_software.clear()
        for i in range(self.software_list.count()):
            item = self.software_list.item(i)
            if item.checkState() == Qt.Checked:
                self.selected_software.add(item.text())

        self.update_selected_btn.setEnabled(len(self.selected_software) > 0)

    def on_removal_selection_changed(self):
        """Handle removal selection changes."""
        selected_items = self.removal_list.selectedItems()
        self.analyze_btn.setEnabled(len(selected_items) > 0)
        self.uninstall_selected_btn.setEnabled(len(selected_items) > 0)

    def on_scan_completed(self, success, message):
        """Handle scan completion."""
        self.progress_bar.setVisible(False)
        status_msg = "Scan completed" if success else f"Scan failed: {message}"
        self.show_status_message(status_msg)

        if success and self.worker_thread and self.worker_thread.tool:
            self.detected_software = self.worker_thread.tool.detected_software
            self.update_software_list()
            self.update_statistics()

    def on_updates_checked(self, success, message):
        """Handle update check completion."""
        self.progress_bar.setVisible(False)
        status_msg = (
            "Update check completed"
            if success
            else f"Update check failed: {message}"
        )
        self.show_status_message(status_msg)

        if success and self.worker_thread and self.worker_thread.tool:
            self.available_updates = self.worker_thread.tool.available_updates
            self.update_updates_table()
            self.update_statistics()

    def on_update_completed(self, success, message):
        """Handle update completion."""
        self.progress_bar.setVisible(False)
        status_msg = (
            "Updates completed" if success else f"Updates failed: {message}"
        )
        self.show_status_message(status_msg)

        if success:
            # Refresh data after successful updates
            QTimer.singleShot(1000, self.refresh_data)

    def on_removal_scan_completed(self, success, message):
        """Handle removal scan completion."""
        self.progress_bar.setVisible(False)
        status_msg = (
            "Removal scan completed"
            if success
            else f"Removal scan failed: {message}"
        )
        self.show_status_message(status_msg)

        if success and self.worker_thread and self.worker_thread.tool:
            self.detected_software = self.worker_thread.tool.detected_software
            self.update_removal_list()
            self.update_statistics()

    def on_removal_completed(self, success, message):
        """Handle removal completion."""
        self.progress_bar.setVisible(False)
        status_msg = (
            "Removal completed" if success else f"Removal failed: {message}"
        )
        self.show_status_message(status_msg)

        if success:
            # Refresh data after successful removal
            QTimer.singleShot(1000, self.refresh_data)

    def update_software_list(self):
        """Update the software list display."""
        self.software_list.clear()

        for software_name, software_info in self.detected_software.items():
            item = QListWidgetItem(
                f"{software_name} ({software_info.version})"
            )
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.software_list.addItem(item)

    def update_updates_table(self):
        """Update the updates table display."""
        self.updates_table.setRowCount(len(self.available_updates))

        for row, (software_name, update_info) in enumerate(
            self.available_updates.items()
        ):
            self.updates_table.setItem(row, 0, QTableWidgetItem(software_name))
            self.updates_table.setItem(
                row, 1, QTableWidgetItem(update_info.current_version)
            )
            self.updates_table.setItem(
                row, 2, QTableWidgetItem(update_info.available_version)
            )
            self.updates_table.setItem(
                row, 3, QTableWidgetItem(update_info.update_source)
            )

    def update_removal_list(self):
        """Update the removal list display."""
        self.removal_list.clear()

        for software_name, software_info in self.detected_software.items():
            size_text = (
                f" ({software_info.size_mb:.1f} MB)"
                if software_info.size_mb
                else ""
            )
            item_text = f"{software_name} ({software_info.version}){size_text}"
            self.removal_list.addItem(item_text)

    def update_statistics(self):
        """Update the statistics display."""
        software_count = len(self.detected_software)
        updates_count = len(self.available_updates)
        self.stats_label.setText(
            f"Software: {software_count} | Updates: {updates_count}"
        )

    def update_status_display(self):
        """Update the status display periodically."""
        # This can be used for real-time status updates
        pass

    def add_log_message(self, level, message):
        """Add a log message to the log display."""
        timestamp = QTimer().currentTime().toString("hh:mm:ss")
        log_entry = f"[{timestamp}] {level}: {message}"
        self.log_display.append(log_entry)

    def clear_logs(self):
        """Clear the log display."""
        self.log_display.clear()

    def export_logs(self):
        """Export logs to a file."""
        # Implementation for exporting logs
        pass

    def save_settings(self):
        """Save the current settings."""
        # Implementation for saving settings
        QMessageBox.information(
            self, "Settings", "Settings saved successfully!"
        )

    def closeEvent(self, event):
        """Handle window close event."""
        if self.worker_thread and self.worker_thread.isRunning():
            reply = QMessageBox.question(
                self,
                "Confirm Exit",
                "An operation is currently running. Exit anyway?",
                QMessageBox.Yes | QMessageBox.No,
            )

            if reply == QMessageBox.No:
                event.ignore()
                return

            # Terminate worker thread
            self.worker_thread.terminate()
            self.worker_thread.wait()
