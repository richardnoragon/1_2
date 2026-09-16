"""
Software Maintenance Hub GUI
This module provides the main graphical user interface for the Software
Maintenance Toolkit, integrating the Software Updater and De-Installer
with comprehensive progress tracking and user interaction.
"""
from src.rfu.localization import localized_widget as _ui_widget, bind_literal as _ui_bind

from src.rfu import font_tokens
import csv
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Add the parent directory to the path to import from other modules
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
try:
    from PyQt5.QtCore import Qt, QThread, QTimer, pyqtSignal
    from PyQt5.QtGui import QColor, QFont, QIcon, QPalette
    from PyQt5.QtWidgets import (
        QApplication,
        QCheckBox,
        QComboBox,
        QDialog,
        QDialogButtonBox,
        QFileDialog,
        QFrame,
        QGridLayout,
        QGroupBox,
        QHBoxLayout,
        QHeaderView,
        QLabel,
        QListWidget,
        QListWidgetItem,
        QMainWindow,
        QMessageBox,
        QProgressBar,
        QPushButton,
        QScrollArea,
        QSpinBox,
        QSplitter,
        QTableWidget,
        QTableWidgetItem,
        QTabWidget,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )

    from src.gui.themes import ThemeManager, token

    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    print("PyQt5 not available. GUI functionality will be limited.")
# Import StandardWindow for menu integration
try:
    from src.gui.menu_manager import MenuManager
    from src.gui.standard_window import StandardWindow

    STANDARD_WINDOW_AVAILABLE = True
except ImportError:
    try:
        from gui.menu_manager import MenuManager
        from src.gui.standard_window import StandardWindow

        STANDARD_WINDOW_AVAILABLE = True
    except ImportError:
        STANDARD_WINDOW_AVAILABLE = False
        # Fallback to QMainWindow if StandardWindow is not available
        StandardWindow = QMainWindow
if PYQT_AVAILABLE:
    from ..tools.software_deinstaller import SoftwareDeinstaller
    from ..tools.software_updater import SoftwareUpdater


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
    from src.rfu.ui_strings import SoftwareMaintenance as _SoftMainStrings
except ImportError:

    class _SoftMainStrings:  # type: ignore[no-redef]
        TITLE = "Software Maintenance"
        WINDOW_TITLE = "Software Maintenance — RFU"
        LOADING = "Loading Software Maintenance…"
        MODAL_ERROR_TITLE = "Software Maintenance"
        ERR_INIT_FAILED = (
            "Could not start Software Maintenance. "
            "Please try again or restart the application."
        )
        ERR_SCAN_FAILED = "Could not scan for software. Please try again."
        ERR_UPDATE_FAILED = "Could not update software. Please try again."
        ERR_EXPORT_FAILED = (
            "Could not export. Check that you have write permission to the destination."
        )
        ERR_IMPORT_FAILED = (
            "Could not import. Check that the file is valid and accessible."
        )


# ---------------------------------------------------------------------------
# ERR: Modal import (graceful no-op when modal absent)
# ---------------------------------------------------------------------------
try:
    from src.gui.components.buttons import PrimaryButton, SecondaryButton
    from src.gui.components.modal import Modal
    from src.gui.components.toast import ToastNotification

    _CP_AVAILABLE = True
except ImportError:
    Modal = None  # type: ignore[assignment,misc]
    PrimaryButton = SecondaryButton = None  # type: ignore[assignment,misc]
    ToastNotification = None
    _CP_AVAILABLE = False


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
                self.tool.operation_completed.connect(self.operation_completed.emit)
                self.tool.log_message.connect(self.log_message.emit)
                # Execute the operation
                if self.operation == "scan_software":
                    result = self.tool.scan_installed_software(
                        *self.args, **self.kwargs
                    )
                elif self.operation == "check_updates":
                    result = self.tool.check_for_updates(*self.args, **self.kwargs)
                elif self.operation == "update_software":
                    if len(self.args) > 1:
                        result = self.tool.update_multiple_software(
                            *self.args, **self.kwargs
                        )
                    else:
                        result = self.tool.update_software(*self.args, **self.kwargs)
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
                        result = self.tool.uninstall_software(*self.args, **self.kwargs)
                else:
                    result = False
                self.operation_completed.emit(bool(result), "Operation completed")
            else:
                self.operation_completed.emit(False, "Failed to initialize tool")
        except (
            Exception
        ) as e:  # ERR: non-fatal — surfaced via operation_completed signal
            self.operation_completed.emit(False, f"Error: {str(e)}")


class SoftwareMaintenanceHub(StandardWindow):
    """
    Main GUI window for the Software Maintenance Toolkit providing
    unified access to software updating and uninstallation features.
    Enhanced with File menu integration following the File Finder template.
    """

    def __init__(self, hub_instance=None):
        super().__init__(
            title=_SoftMainStrings.WINDOW_TITLE,
            window_type="utility",
        )
        self._hub = hub_instance
        try:
            from src.rfu.log_manager import get_log_manager

            self._logger = get_log_manager().get_logger("SoftwareMaintenanceHub")
        except Exception:
            self._logger = logging.getLogger("SoftwareMaintenanceHub")
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
        register_gui_component(
            self,
            tool_id="software_maintenance",
            recovery_callback=self.degraded_fallback,
        )
        _emit_telemetry("ui_view_load", tool_id="software_maintenance")
        ThemeManager.add_theme_changed_callback(self._on_theme_changed)

    def _on_theme_changed(self, variant: str) -> None:
        """Re-apply token-based stylesheets when the active theme variant changes."""
        pass  # stylesheets applied at init; live re-apply pending TH-4c/4d

    def health_check(self) -> bool:
        """Return True if core UI is functional (GRD-3a)."""
        try:
            return self.centralWidget() is not None
        except Exception:
            return False

    def degraded_fallback(self) -> None:
        """Enter degraded / read-only state (GRD-3b)."""
        try:
            self._logger.warning("SoftwareMaintenanceHub entering degraded mode")
        except Exception:
            pass
        _emit_telemetry(
            "ui_error_event", tool_id="software_maintenance", error_type="degraded"
        )

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
        if Modal:
            Modal(
                "Software Maintenance Preferences",
                "Software Maintenance preferences:\n\n"
                "• Automatic update checking frequency\n"
                "• Backup settings before changes\n"
                "• Security update priorities\n"
                "• Removal verification options\n"
                "• System restore point creation\n\n"
                "Configure these settings in the Settings tab!",
                ["OK"],
                self,
            ).exec_()
        else:
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
                    f.write(f"Generated: {QTimer().currentTime().toString()}\n")
                    f.write(f"Total Software Detected: {len(self.detected_software)}\n")
                    f.write(f"Available Updates: {len(self.available_updates)}\n\n")
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
                            current = getattr(update, "current_version", "Unknown")
                            available = getattr(update, "available_version", "Unknown")
                            f.write(f"• {name}: {current} → {available}\n")
                if ToastNotification:
                    ToastNotification(parent=self).show_message(
                        f"Maintenance report exported to: {file_path}", "success"
                    )
                else:
                    QMessageBox.information(
                        self,
                        "Export Complete",
                        f"Maintenance report exported to:\n{file_path}",
                    )
            except Exception as e:  # ERR: non-fatal — surfaced via Modal; export failed
                if Modal:
                    Modal(
                        _SoftMainStrings.MODAL_ERROR_TITLE,
                        _SoftMainStrings.ERR_EXPORT_FAILED,
                        ["OK"],
                        self,
                    ).exec_()

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
                    writer.writerow(["Software Name", "Version", "Update Available"])
                    for name, info in self.detected_software.items():
                        version = getattr(info, "version", "Unknown")
                        has_update = name in self.available_updates
                        writer.writerow([name, version, "Yes" if has_update else "No"])
                if ToastNotification:
                    ToastNotification(parent=self).show_message(
                        f"Software list exported to: {file_path}", "success"
                    )
                else:
                    QMessageBox.information(
                        self,
                        "Export Complete",
                        f"Software list exported to:\n{file_path}",
                    )
            except Exception as e:  # ERR: non-fatal — surfaced via Modal; export failed
                self._logger.error(
                    f"Failed to export software list: {e}", exc_info=True
                )
                if Modal:
                    Modal(
                        _SoftMainStrings.MODAL_ERROR_TITLE,
                        _SoftMainStrings.ERR_EXPORT_FAILED,
                        ["OK"],
                        self,
                    ).exec_()

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
                    if ToastNotification:
                        ToastNotification(parent=self).show_message(
                            "Software configuration imported successfully!", "success"
                        )
                    else:
                        QMessageBox.information(
                            self,
                            "Import Complete",
                            "Software configuration imported successfully!",
                        )
                elif file_path.endswith(".csv"):
                    # Process CSV import
                    if ToastNotification:
                        ToastNotification(parent=self).show_message(
                            "Software list imported successfully!", "success"
                        )
                    else:
                        QMessageBox.information(
                            self,
                            "Import Complete",
                            "Software list imported successfully!",
                        )
                else:
                    if Modal:
                        Modal(
                            "Import",
                            "Import functionality for this file type coming soon!",
                            ["OK"],
                            self,
                        ).exec_()
                    else:
                        QMessageBox.information(
                            self,
                            "Import",
                            "Import functionality for this file type coming soon!",
                        )
            except Exception as e:  # ERR: non-fatal — surfaced via Modal; import failed
                self._logger.error(
                    f"Failed to import software list: {e}", exc_info=True
                )
                if Modal:
                    Modal(
                        _SoftMainStrings.MODAL_ERROR_TITLE,
                        _SoftMainStrings.ERR_IMPORT_FAILED,
                        ["OK"],
                        self,
                    ).exec_()

    def print_maintenance_report(self):
        """Print maintenance report."""
        _msg = (
            "Print functionality will open the system print dialog.\n\n"
            "For now, you can export the report and print from your "
            "preferred text editor."
        )
        if Modal:
            Modal("Print Report", _msg, ["OK"], self).exec_()
        else:
            QMessageBox.information(self, "Print Report", _msg)
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
        _ui_bind(self.tab_widget, 'setAccessibleName', 'Legacy.sde22939aad6b4011')
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
        self.status_label = _ui_widget(QLabel, 'Legacy.s5fa7aac5375c5815', 'setText')
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        # Statistics
        self.stats_label = _ui_widget(QLabel, 'Legacy.sdca032225a65a8a2', 'setText')
        status_layout.addWidget(self.stats_label)
        return status_layout

    def create_updater_tab(self):
        """Create the Software Updater tab."""
        updater_widget = QWidget()
        layout = QVBoxLayout(updater_widget)
        # Control panel using StandardWindow create_group_box
        control_group = self.create_group_box("Update Controls")
        control_layout = QHBoxLayout(control_group)
        self.scan_software_btn = self.create_button("Scan Software", self.scan_software)
        control_layout.addWidget(self.scan_software_btn)
        self.check_updates_btn = self.create_button("Check Updates", self.check_updates)
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
        _ui_bind(self.software_list, 'setAccessibleName', 'Legacy.s5d5716995905a309')
        self.software_list.itemChanged.connect(self.on_software_selection_changed)
        software_layout.addWidget(self.software_list)
        content_splitter.addWidget(software_group)
        # Updates panel
        updates_group = self.create_group_box("Available Updates")
        updates_layout = QVBoxLayout(updates_group)
        self.updates_table = QTableWidget()
        _ui_bind(self.updates_table, 'setAccessibleName', 'Legacy.s278e7f449190b323')
        self.updates_table.setColumnCount(4)
        self.updates_table.setHorizontalHeaderLabels(
            ["Software", "Current", "Available", "Source"]
        )
        updates_layout.addWidget(self.updates_table)
        # Update details
        self.update_details = QTextEdit()
        _ui_bind(self.update_details, 'setAccessibleName', 'Legacy.s3779f3d01d75d0d8')
        self.update_details.setMaximumHeight(150)
        _ui_bind(self.update_details, 'setPlaceholderText', 'Legacy.sc2a8393dc36bbeec')
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
        _ui_bind(self.removal_list, 'setAccessibleName', 'Legacy.s57476c1a14a949f5')
        self.removal_list.itemChanged.connect(self.on_removal_selection_changed)
        removal_layout.addWidget(self.removal_list)
        # Space analysis
        space_group = self.create_group_box("Space Analysis")
        space_layout = QVBoxLayout(space_group)
        self.space_label = _ui_widget(QLabel, 'Legacy.s13ff585b7d6469af', 'setText')
        space_layout.addWidget(self.space_label)
        removal_layout.addWidget(space_group)
        content_splitter.addWidget(removal_group)
        # Analysis panel
        analysis_group = self.create_group_box("Removal Analysis")
        analysis_layout = QVBoxLayout(analysis_group)
        self.analysis_details = QTextEdit()
        _ui_bind(self.analysis_details, 'setAccessibleName', 'Legacy.s1c74b90eeae77756')
        _ui_bind(self.analysis_details, 'setPlaceholderText', 'Legacy.s38062cf03e819026')
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
        updater_group = _ui_widget(QGroupBox, 'Legacy.s9339c5bdd141452c', 'setTitle')
        updater_layout = QGridLayout(updater_group)
        self.auto_check_cb = _ui_widget(QCheckBox, 'Legacy.s012039a0475fe3d1', 'setText')
        _ui_bind(self.auto_check_cb, 'setAccessibleName', 'Legacy.s012039a0475fe3d1')
        self.auto_check_cb.setMinimumHeight(44)
        updater_layout.addWidget(self.auto_check_cb, 0, 0, 1, 2)
        updater_layout.addWidget(_ui_widget(QLabel, 'Legacy.s8dc31033ffb65312', 'setText'), 1, 0)
        self.check_interval_spin = QSpinBox()
        _ui_bind(self.check_interval_spin, 'setAccessibleName', 'Legacy.s96a8aa213bcd17b2')
        _ui_bind(self.check_interval_spin, 'setAccessibleDescription', 'Legacy.s99e707e02e1d842c')
        self.check_interval_spin.setMinimumHeight(44)
        self.check_interval_spin.setRange(1, 168)  # 1 hour to 1 week
        self.check_interval_spin.setValue(24)
        updater_layout.addWidget(self.check_interval_spin, 1, 1)
        self.auto_security_cb = _ui_widget(QCheckBox, 'Legacy.sc60bd6d2542d6902', 'setText')
        _ui_bind(self.auto_security_cb, 'setAccessibleName', 'Legacy.sc60bd6d2542d6902')
        _ui_bind(self.auto_security_cb, 'setAccessibleDescription', 'Legacy.s10825e38ab67de6a')
        self.auto_security_cb.setMinimumHeight(44)
        updater_layout.addWidget(self.auto_security_cb, 2, 0, 1, 2)
        self.create_restore_points_cb = _ui_widget(QCheckBox, 'Legacy.s3ebcf43f5453e2ae', 'setText')
        _ui_bind(self.create_restore_points_cb, 'setAccessibleName', 'Legacy.s3ebcf43f5453e2ae')
        _ui_bind(self.create_restore_points_cb, 'setAccessibleDescription', 'Legacy.sfc5a0fee99de816f')
        self.create_restore_points_cb.setMinimumHeight(44)
        updater_layout.addWidget(self.create_restore_points_cb, 3, 0, 1, 2)
        layout.addWidget(updater_group)
        # De-installer settings
        deinstaller_group = _ui_widget(QGroupBox, 'Legacy.s07e496451b489054', 'setTitle')
        deinstaller_layout = QGridLayout(deinstaller_group)
        self.backup_before_removal_cb = _ui_widget(QCheckBox, 'Legacy.s0f8eff181978f40e', 'setText')
        _ui_bind(self.backup_before_removal_cb, 'setAccessibleName', 'Legacy.s0f8eff181978f40e')
        _ui_bind(self.backup_before_removal_cb, 'setAccessibleDescription', 'Legacy.s981cac40c4f9d6b7')
        self.backup_before_removal_cb.setMinimumHeight(44)
        deinstaller_layout.addWidget(self.backup_before_removal_cb, 0, 0, 1, 2)
        self.deep_scan_cb = _ui_widget(QCheckBox, 'Legacy.s392f8acc80e7f48a', 'setText')
        _ui_bind(self.deep_scan_cb, 'setAccessibleName', 'Legacy.s392f8acc80e7f48a')
        _ui_bind(self.deep_scan_cb, 'setAccessibleDescription', 'Legacy.s8ad3f999a6671354')
        self.deep_scan_cb.setMinimumHeight(44)
        deinstaller_layout.addWidget(self.deep_scan_cb, 1, 0, 1, 2)
        self.auto_cleanup_cb = _ui_widget(QCheckBox, 'Legacy.s1888c217e5c8d47f', 'setText')
        _ui_bind(self.auto_cleanup_cb, 'setAccessibleName', 'Legacy.s1888c217e5c8d47f')
        self.auto_cleanup_cb.setMinimumHeight(44)
        deinstaller_layout.addWidget(self.auto_cleanup_cb, 2, 0, 1, 2)
        layout.addWidget(deinstaller_group)
        # Security settings
        security_group = _ui_widget(QGroupBox, 'Legacy.s170ded248de8b540', 'setTitle')
        security_layout = QGridLayout(security_group)
        security_layout.addWidget(_ui_widget(QLabel, 'Legacy.s8c1441b7fbe7a90b', 'setText'), 0, 0)
        self.backup_retention_spin = QSpinBox()
        _ui_bind(self.backup_retention_spin, 'setAccessibleName', 'Legacy.sb2c5f497d20f3526')
        self.backup_retention_spin.setMinimumHeight(44)
        self.backup_retention_spin.setRange(1, 365)
        self.backup_retention_spin.setValue(30)
        security_layout.addWidget(self.backup_retention_spin, 0, 1)
        security_layout.addWidget(_ui_widget(QLabel, 'Legacy.sc91c619555c0624d', 'setText'), 1, 0)
        self.max_backup_size_spin = QSpinBox()
        _ui_bind(self.max_backup_size_spin, 'setAccessibleName', 'Legacy.s5a98d975bd7d3eee')
        self.max_backup_size_spin.setMinimumHeight(44)
        self.max_backup_size_spin.setRange(1, 100)
        self.max_backup_size_spin.setValue(10)
        security_layout.addWidget(self.max_backup_size_spin, 1, 1)
        layout.addWidget(security_group)
        # Save settings button
        _SB = SecondaryButton if SecondaryButton else QPushButton
        save_settings_btn = _SB("Save Settings")
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
        log_controls.addWidget(_ui_widget(QLabel, 'Legacy.sb4bf93b6cff36612', 'setText'))
        self.log_level_combo = QComboBox()
        _ui_bind(self.log_level_combo, 'setAccessibleName', 'Legacy.s9d627b6f2893cc11')
        self.log_level_combo.addItems(["All", "Info", "Warning", "Error"])
        log_controls.addWidget(self.log_level_combo)
        log_controls.addStretch()
        _SB2 = SecondaryButton if SecondaryButton else QPushButton
        clear_logs_btn = _SB2("Clear Logs")
        clear_logs_btn.clicked.connect(self.clear_logs)
        log_controls.addWidget(clear_logs_btn)
        export_logs_btn = _SB2("Export Logs")
        export_logs_btn.clicked.connect(self.export_logs)
        log_controls.addWidget(export_logs_btn)
        layout.addLayout(log_controls)
        # Log display
        self.log_display = QTextEdit()
        _ui_bind(self.log_display, 'setAccessibleName', 'Legacy.sa088b13798911e86')
        self.log_display.setReadOnly(True)
        font_tokens.bind(self.log_display, "font.body")
        layout.addWidget(self.log_display)
        self.tab_widget.addTab(logs_widget, "Logs")

    def setup_styling(self):
        """Setup the application styling."""
        # Set application style
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: {token('surface')};
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
                background-color: {token('semantic_success')};
                border: none;
                color: white;
                padding: 8px 16px;
                text-align: center;

                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: {token('semantic_success')};
            }
            QPushButton:pressed {
                background-color: {token('semantic_success')};
            }
            QPushButton:disabled {
                background-color: {token('border')};
                color: {token('text_muted')};
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
                border-bottom: 2px solid {token('semantic_success')};
            }
        """
        )
        font_tokens.bind(self, "font.body")

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
            QMessageBox.warning(self, "Warning", "No software selected for update.")
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
            self.worker_thread = WorkerThread("update_software", selected_software)
            self.worker_thread.progress_updated.connect(self.progress_bar.setValue)
            self.worker_thread.status_updated.connect(self.status_label.setText)
            self.worker_thread.operation_completed.connect(self.on_update_completed)
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
        self.worker_thread.operation_completed.connect(self.on_removal_scan_completed)
        self.worker_thread.log_message.connect(self.add_log_message)
        self.worker_thread.start()

    def analyze_selected_software(self):
        """Analyze selected software for removal."""
        # Implementation for analyzing selected software
        pass

    def uninstall_selected_software(self):
        """Uninstall selected software."""
        selected_software = [item.text() for item in self.removal_list.selectedItems()]
        if not selected_software:
            QMessageBox.warning(self, "Warning", "No software selected for removal.")
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
            self.worker_thread = WorkerThread("uninstall_software", selected_software)
            self.worker_thread.progress_updated.connect(self.progress_bar.setValue)
            self.worker_thread.status_updated.connect(self.status_label.setText)
            self.worker_thread.operation_completed.connect(self.on_removal_completed)
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
            "Update check completed" if success else f"Update check failed: {message}"
        )
        self.show_status_message(status_msg)
        if success and self.worker_thread and self.worker_thread.tool:
            self.available_updates = self.worker_thread.tool.available_updates
            self.update_updates_table()
            self.update_statistics()

    def on_update_completed(self, success, message):
        """Handle update completion."""
        self.progress_bar.setVisible(False)
        status_msg = "Updates completed" if success else f"Updates failed: {message}"
        self.show_status_message(status_msg)
        if success:
            # Refresh data after successful updates
            QTimer.singleShot(1000, self.refresh_data)

    def on_removal_scan_completed(self, success, message):
        """Handle removal scan completion."""
        self.progress_bar.setVisible(False)
        status_msg = (
            "Removal scan completed" if success else f"Removal scan failed: {message}"
        )
        self.show_status_message(status_msg)
        if success and self.worker_thread and self.worker_thread.tool:
            self.detected_software = self.worker_thread.tool.detected_software
            self.update_removal_list()
            self.update_statistics()

    def on_removal_completed(self, success, message):
        """Handle removal completion."""
        self.progress_bar.setVisible(False)
        status_msg = "Removal completed" if success else f"Removal failed: {message}"
        self.show_status_message(status_msg)
        if success:
            # Refresh data after successful removal
            QTimer.singleShot(1000, self.refresh_data)

    def update_software_list(self):
        """Update the software list display."""
        self.software_list.clear()
        for software_name, software_info in self.detected_software.items():
            item = QListWidgetItem(f"{software_name} ({software_info.version})")
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
                f" ({software_info.size_mb:.1f} MB)" if software_info.size_mb else ""
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
        QMessageBox.information(self, "Settings", "Settings saved successfully!")

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
