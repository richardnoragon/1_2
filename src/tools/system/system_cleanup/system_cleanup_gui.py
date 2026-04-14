#!/usr/bin/env python3
"""
System Cleanup GUI for Richard's File Utilities

This module provides a comprehensive system cleanup interface that inherits
from SystemDiagnosticsGUI and integrates all available cleanup tools with
safety features and progress tracking.
"""

import logging
from typing import Any, Dict

try:
    from PyQt5.QtCore import QObject, QThread, pyqtSignal
    from PyQt5.QtWidgets import (
        QCheckBox,
        QDialog,
        QFileDialog,
        QFrame,
        QGridLayout,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QMainWindow,
        QMessageBox,
        QProgressBar,
        QPushButton,
        QScrollArea,
        QSpinBox,
        QTabWidget,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )

    from src.gui.components.buttons import (
        DestructiveButton,
        PrimaryButton,
        SecondaryButton,
    )
    from src.gui.components.loading_indicator import LoadingIndicator
    from src.gui.components.modal import ConfirmationModal, Modal
    from src.gui.components.toast import ToastNotification
    from src.gui.themes import ThemeManager, token

    PYQT5_AVAILABLE = True
except ImportError:
    PYQT5_AVAILABLE = False
    # Create dummy classes for when PyQt5 is not available
    QMainWindow = type("QMainWindow", (), {})
    QObject = type("QObject", (), {})
    pyqtSignal = type("pyqtSignal", (), {"__init__": lambda self, *args: None})
    QWidget = type("QWidget", (), {})
    QVBoxLayout = type("QVBoxLayout", (), {})
    QHBoxLayout = type("QHBoxLayout", (), {})
    QTabWidget = type("QTabWidget", (), {})
    QLabel = type("QLabel", (), {})
    QPushButton = type("QPushButton", (), {})
    PrimaryButton = QPushButton
    SecondaryButton = QPushButton
    DestructiveButton = QPushButton
    ConfirmationModal = None
    Modal = None
    LoadingIndicator = None
    ToastNotification = None
    QGroupBox = type("QGroupBox", (), {})
    QGridLayout = type("QGridLayout", (), {})
    QProgressBar = type("QProgressBar", (), {})
    QTextEdit = type("QTextEdit", (), {})
    QFrame = type("QFrame", (), {})
    QCheckBox = type("QCheckBox", (), {})
    QSpinBox = type("QSpinBox", (), {})
    QScrollArea = type("QScrollArea", (), {})
    QMessageBox = type("QMessageBox", (), {})
    QFileDialog = type("QFileDialog", (), {})

# Import the comprehensive SystemDiagnosticsGUI as base class
try:
    from src.tools.system.diagnostics_monitoring.system_diagnostics_gui import (  # noqa: E501
        SystemDiagnosticsGUI,
    )

    DIAGNOSTICS_GUI_AVAILABLE = True
except ImportError:
    DIAGNOSTICS_GUI_AVAILABLE = False
    SystemDiagnosticsGUI = QMainWindow

# Import cleanup tools
try:
    from src.tools.system.system_cleanup.core.cleanup_base import (
        CleanupOperationResult,
    )
    from src.tools.system.system_cleanup.core.safety_manager import (
        SafetyManager,
    )
    from src.tools.system.system_cleanup.core.windows_utils import WindowsUtils
    from src.tools.system.system_cleanup.tools.temp_cleaner import (
        TempFilesCleaner,
    )

    CLEANUP_TOOLS_AVAILABLE = True
except ImportError:
    CLEANUP_TOOLS_AVAILABLE = False
    TempFilesCleaner = None
    CleanupOperationResult = None
    SafetyManager = None
    WindowsUtils = None

try:
    from src.rfu.ui_strings import SystemCleanup as _SystemCleanupStrings
except ImportError:

    class _SystemCleanupStrings:
        TITLE = "System Cleanup"
        LOADING = "Loading System Cleanup…"
        DRY_RUN_LABEL = "Dry Run (Preview Only)"
        ESTIMATE_LABEL = "Estimate Space to Free"
        PREVIEW_LABEL = "Preview Temp Files Cleanup"
        WINDOW_TITLE = "System Cleanup - Richard's File Utilities"
        TAB_QUICK_CLEANUP = "Quick Cleanup"
        TAB_ADVANCED_TOOLS = "Advanced Tools"
        TAB_SAFETY_BACKUPS = "Safety & Backups"
        TAB_RESULTS_REPORTS = "Results & Reports"
        GROUP_QUICK_CLEANUP = "Quick Cleanup"
        GROUP_QUICK_CONTROLS = "Quick Cleanup Controls"
        GROUP_CLEANUP_ESTIMATE = "Cleanup Estimate"
        GROUP_ADDITIONAL_TOOLS = "Additional Cleanup Tools"
        GROUP_TEMP_ADVANCED = "Temporary Files - Advanced Options"
        GROUP_SAFETY_SETTINGS = "Safety Settings"
        GROUP_BACKUP_MGMT = "Backup Management"
        GROUP_SYSTEM_INFO = "System Information"
        GROUP_OP_STATUS = "Current Operation Status"
        GROUP_CLEANUP_RESULTS = "Cleanup Results"
        CHK_TEMP_FILES = "Clean Temporary Files"
        CHK_CACHE = "Clear Application Caches"
        CHK_LOGS = "Clean Windows Logs"
        CHK_TEMP_SYSTEM = "Include system temp directories"
        CHK_TEMP_BACKUP = "Create backup before deletion"
        CHK_TEMP_SECURE = "Secure deletion (overwrite data)"
        CHK_RESTORE_POINT = "Create system restore point before cleanup"
        CHK_BACKUP_FILES = "Backup important files before deletion"
        CHK_CONFIRM_OPS = "Show confirmation dialogs for destructive operations"
        BTN_RUN_QUICK_CLEANUP = "Run Quick Cleanup"
        BTN_EXECUTE_TEMP_CLEANUP = "Execute Temp Files Cleanup"
        BTN_VIEW_BACKUPS = "View Backups"
        BTN_CLEANUP_OLD_BACKUPS = "Cleanup Old Backups"
        BTN_RESTORE_ALL_BACKUPS = "Restore All Backups"
        BTN_STOP_OPERATION = "Stop Current Operation"
        BTN_EXPORT_RESULTS = "Export Results Report"
        LABEL_AGE_FILTER = "Delete files older than (days):"
        LABEL_SIZE_FILTER = "Minimum file size (MB):"
        LABEL_BACKUP_LOCATION = "Backup Location:"
        LABEL_BACKUP_NOT_INITIALIZED = "Not initialized"
        LABEL_TOOLS_UNAVAILABLE = "Advanced Tools are temporarily unavailable."
        LABEL_SAFETY_UNAVAILABLE = (
            "Safety & Backup settings are temporarily unavailable."
        )
        LABEL_NO_OPERATION = "No cleanup operation in progress"
        LABEL_ADDITIONAL_TOOLS_COMING = (
            "Additional cleanup tools will be available in future updates:"
        )
        LABEL_TOOLS_LIST = "\u2022 Registry Cleaner\n\u2022 Cache Cleaner\n\u2022 Log Files Cleaner\n\u2022 Restore Points Manager\n\u2022 Memory Dumps Cleaner"  # noqa: E501
        TEXT_ESTIMATE_PROMPT = (
            "Click 'Estimate Space to Free' to see potential cleanup results."
        )
        TEXT_NO_RESULTS = "No cleanup operations performed yet.\n\nSelect a cleanup operation from the Quick Cleanup or Advanced Tools tabs to begin."  # noqa: E501
        LOADING_INDICATOR_MSG = "Cleanup in progress..."
        STATUS_UNABLE_TO_START = "Unable to start cleanup. Please try again."
        STATUS_CLEANUP_COMPLETED = "Cleanup completed"
        STATUS_CLEANUP_FAILED = "Cleanup failed"
        STATUS_ESTIMATING = "Estimating cleanup size\u2026"
        STATUS_ESTIMATE_ERROR = "Unable to estimate cleanup size. Please try again."
        STATUS_ESTIMATE_DISPLAY_ERROR = (
            "Unable to display estimate results. Please try again."
        )
        MODAL_NO_TOOLS_TITLE = "No Tools Selected"
        MODAL_NO_TOOLS_MSG = "Please select at least one cleanup option to proceed."
        MODAL_TOOL_NA_TITLE = "Tool Not Available"
        MODAL_TOOL_NA_MSG = "Temporary files cleanup tool is not available."
        MODAL_PREVIEW_ERR_TITLE = "Preview Error"
        MODAL_PREVIEW_ERR_MSG = "Unable to generate preview. Please try again."
        MODAL_PREVIEW_DISPLAY_ERR_MSG = "Unable to display preview. Please try again."
        MODAL_QUICK_ERR_TITLE = "Quick Cleanup Error"
        MODAL_QUICK_ERR_MSG = "Quick cleanup could not be started. Please try again or check the application logs."  # noqa: E501
        MODAL_CLEANUP_ERR_TITLE = "Cleanup Error"
        MODAL_CLEANUP_ERR_MSG_START = (
            "Failed to start the cleanup operation. Please try again."
        )
        MODAL_CLEANUP_ERR_MSG_WORKER = (
            "Cleanup failed. Please try again or check the application logs."
        )
        MODAL_CLEANUP_ERR_MSG_UNABLE = "Unable to start cleanup. Please try again or check the application logs."  # noqa: E501
        MODAL_CLEANUP_COMPLETE_TITLE = "Cleanup Complete"
        MODAL_CLEANUP_WARNING_TITLE = "Cleanup Warning"
        MODAL_OP_IN_PROGRESS_TITLE = "Operation In Progress"
        MODAL_OP_IN_PROGRESS_MSG = "Another cleanup operation is currently running. Please wait for it to complete."  # noqa: E501
        MODAL_EXPORT_TITLE = "Export Results"
        MODAL_EXPORT_MSG = "Export functionality will be available in a future update.\n\nYou can select and copy the results text manually."  # noqa: E501
        MODAL_BACKUPS_NA_TITLE = "Backups Unavailable"
        MODAL_BACKUPS_NO_DIR_MSG = (
            "Safety manager is not initialised; no backup directory available."
        )
        MODAL_BACKUPS_NA_MSG = "Safety manager is not initialised."
        MODAL_BACKUPS_RESTORE_NA_MSG = (
            "Safety manager is not initialised; cannot restore backups."
        )
        MODAL_CANT_OPEN_DIR_TITLE = "Cannot Open Directory"
        MODAL_CANT_OPEN_DIR_MSG = "Unable to open the backup directory. Please check the path and try again."  # noqa: E501
        MODAL_BACKUPS_CLEANED_TITLE = "Backups Cleaned"
        MODAL_BACKUPS_CLEANED_MSG = "Old backups removed successfully."
        MODAL_BACKUPS_FAILED_TITLE = "Cleanup Failed"
        MODAL_BACKUPS_FAILED_MSG = "Failed to remove old backups."
        MODAL_RESTORE_COMPLETE_TITLE = "Restore Complete"
        MODAL_RESTORE_COMPLETE_MSG = "All backups restored successfully."
        MODAL_RESTORE_FAILED_TITLE = "Restore Failed"
        MODAL_RESTORE_FAILED_MSG = "Failed to restore all backups."
        CONFIRM_BACKUP_CLEANUP_TITLE = "Confirm Backup Cleanup"
        CONFIRM_BACKUP_CLEANUP_MSG = (
            "Delete all backups older than 7 days? This cannot be undone."
        )
        CONFIRM_BACKUP_CLEANUP_YES = "Delete Backups"
        CONFIRM_RESTORE_ALL_TITLE = "Restore All Backups"
        CONFIRM_RESTORE_ALL_MSG = "Restore ALL session backups? This will overwrite current files and cannot be undone."  # noqa: E501
        CONFIRM_RESTORE_ALL_YES = "Restore"
        CONFIRM_QUICK_CLEANUP_TITLE = "Confirm Quick Cleanup"
        CONFIRM_TEMP_CLEANUP_TITLE = "Confirm Temp Files Cleanup"
        CONFIRM_TEMP_CLEANUP_MSG = "Are you sure you want to clean temporary files?\n\nThis operation may delete files permanently."  # noqa: E501
        CONFIRM_YES = "Yes"
        CONFIRM_CANCEL = "Cancel"


# GRD-1a: ComponentGuardian registration (P1-C03/P1-C04 resolved April 2026)
try:
    from src.core.guardian import register_gui_component

    COMPONENT_GUARDIAN_AVAILABLE = True
except ImportError:
    COMPONENT_GUARDIAN_AVAILABLE = False

    def register_gui_component(widget, component_type=None, recovery_callback=None):
        """No-op stub used when ComponentGuardian is unavailable."""
        return ""


# TEL-1/2/3/4: UI telemetry (spec §9.3)
try:
    from src.gui.telemetry import emit_telemetry as _emit_telemetry

    _TELEMETRY_AVAILABLE = True
except ImportError:
    _TELEMETRY_AVAILABLE = False

    def _emit_telemetry(event_type: str, *, tool_id: str, **kwargs) -> None:
        """No-op stub used when ui_telemetry module is unavailable."""


class CleanupWorker(QObject):
    """Worker thread for running cleanup operations."""

    progress_updated = pyqtSignal(int, int, str)  # current, total, message
    operation_complete = pyqtSignal(object)  # CleanupOperationResult
    error_occurred = pyqtSignal(str)  # error message

    def __init__(
        self,
        cleanup_tool,
        operation_params,
        safety_manager=None,
        restore_point_description: str = "",
    ):
        super().__init__()
        self.cleanup_tool = cleanup_tool
        self.operation_params = operation_params
        self._safety_manager = safety_manager
        self._restore_point_description = restore_point_description
        self._should_stop = False

    def run(self):
        """Run the cleanup operation."""
        try:
            # Create restore point before cleanup if requested (PERF-1d: done in  # noqa: E501
            # worker thread so PowerShell call does not block the UI thread)
            if self._safety_manager and self._restore_point_description:
                self._safety_manager.create_restore_point(
                    self._restore_point_description
                )

            # Connect tool signals to worker signals
            if hasattr(self.cleanup_tool, "progress_updated"):
                self.cleanup_tool.progress_updated.connect(self.progress_updated)
            if hasattr(self.cleanup_tool, "error_occurred"):
                self.cleanup_tool.error_occurred.connect(self.error_occurred)

            # Execute the operation
            result = self.cleanup_tool.execute_operation(**self.operation_params)
            self.operation_complete.emit(result)

        except (
            Exception
        ) as e:  # ERR: non-fatal — propagated via error_occurred signal to on_cleanup_error  # noqa: E501
            logging.getLogger("RFU.SystemCleanup").error(
                f"Cleanup operation failed: {e}"
            )
            self.error_occurred.emit("Cleanup operation failed")

    def stop(self):
        """Request to stop the operation."""
        self._should_stop = True
        if hasattr(self.cleanup_tool, "stop_operation"):
            self.cleanup_tool.stop_operation()


class EstimateWorker(QObject):
    """Worker thread for estimating cleanup size without
    blocking the UI thread.

    PERF-1d: temp directory scan (O(n) stat() calls) moved off UI thread.
    """

    estimate_ready = pyqtSignal(int)  # total_size bytes
    error_occurred = pyqtSignal(str)

    def __init__(
        self,
        temp_tool,
        max_age_days: int = 0,
        min_size_bytes: int = 0,
        include_system_temp: bool = True,
    ):
        super().__init__()
        self._temp_tool = temp_tool
        self._max_age_days = max_age_days
        self._min_size_bytes = min_size_bytes
        self._include_system_temp = include_system_temp

    def run(self):
        """Estimate cleanup size on the worker thread."""
        try:
            size = self._temp_tool.estimate_cleanup_size(
                max_age_days=self._max_age_days,
                min_size_bytes=self._min_size_bytes,
                include_system_temp=self._include_system_temp,
            )
            self.estimate_ready.emit(size)
        except (
            Exception
        ) as e:  # ERR: non-fatal — propagated via error_occurred signal to _on_estimate_error  # noqa: E501
            logging.getLogger("RFU.SystemCleanup").error(f"Estimate worker failed: {e}")
            self.error_occurred.emit("Unable to estimate cleanup size")


class PreviewWorker(QObject):
    """Worker thread for generating cleanup preview without blocking the UI thread.  # noqa: E501

    PERF-1d: temp directory scan (O(n) stat() calls) moved off UI thread.
    """

    preview_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def __init__(self, temp_tool, params: dict):
        super().__init__()
        self._temp_tool = temp_tool
        self._params = params

    def run(self):
        """Generate cleanup preview on the worker thread."""
        try:
            preview = self._temp_tool.preview_operation(**self._params)
            self.preview_ready.emit(preview)
        except (
            Exception
        ) as e:  # ERR: non-fatal — propagated via error_occurred signal to _on_preview_error  # noqa: E501
            logging.getLogger("RFU.SystemCleanup").error(f"Preview worker failed: {e}")
            self.error_occurred.emit("Unable to generate preview")


class SystemCleanupGUI(SystemDiagnosticsGUI):
    """Comprehensive System Cleanup GUI with integrated cleanup tools.

    This class inherits from SystemDiagnosticsGUI and provides a specialized
    interface for system cleanup operations, including temporary file removal,
    cache clearing, registry cleaning, and other system optimization tasks.
    """

    # Additional signals for cleanup operations
    cleanup_started = pyqtSignal(str)  # tool_name
    cleanup_completed = pyqtSignal(str, object)  # tool_name, result
    cleanup_progress = pyqtSignal(str, int, str)  # tool_name, percentage, message

    def __init__(self, hub_instance=None, parent=None):
        """Initialize the System Cleanup GUI.

        Args:
            hub_instance: Optional hub instance for integration
            parent: Parent widget
        """
        if not PYQT5_AVAILABLE:
            raise ImportError("PyQt5 is required for the System Cleanup GUI")

        if not DIAGNOSTICS_GUI_AVAILABLE:
            raise ImportError("SystemDiagnosticsGUI is required as base class")

        # Initialize the base class
        super().__init__(hub_instance, parent)

        # Setup logging
        self.logger = logging.getLogger("RFU.SystemCleanup")

        # Cleanup-specific components
        self.cleanup_tools = {}
        self.safety_manager = None
        self.current_worker = None
        self.current_thread = None
        self._loading_indicator = None

        # Initialize cleanup tools
        self.init_cleanup_tools()

        # Override window title and customize UI
        self.setWindowTitle(_SystemCleanupStrings.WINDOW_TITLE)
        self.customize_cleanup_interface()

        # Connect cleanup-specific signals
        self.setup_cleanup_signals()

        # Register theme-change callback for live re-theming
        if PYQT5_AVAILABLE:
            ThemeManager.add_theme_changed_callback(self._on_theme_changed)
        self._toast = (
            ToastNotification(self, role="info") if ToastNotification else None
        )
        # GRD-1b/c: Register with ComponentGuardian before widget is shown
        self._guardian_component_id = register_gui_component(
            self, component_type="system_cleanup"
        )

        # TEL-1b: emit ui_view_load when the widget is initialised
        _emit_telemetry("ui_view_load", tool_id="system_cleanup")

    def _on_theme_changed(self, variant: str) -> None:
        """Re-apply token-driven stylesheets when theme variant changes."""
        for _btn in (
            "quick_cleanup_button",
            "execute_button",
            "estimate_button",
            "preview_button",
            "stop_cleanup_button",
            "view_backups_button",
            "export_button",
        ):
            btn = getattr(self, _btn, None)
            if btn is not None:
                btn._apply_style()
        if hasattr(self, "restore_backups_button"):
            self.restore_backups_button._apply_destructive_style()
        if hasattr(self, "cleanup_backups_button"):
            self.cleanup_backups_button._apply_destructive_style()

    def init_cleanup_tools(self):
        """Initialize available cleanup tools."""
        try:
            if CLEANUP_TOOLS_AVAILABLE:
                # Initialize safety manager
                if SafetyManager:
                    self.safety_manager = SafetyManager()

                # Initialize cleanup tools
                if TempFilesCleaner:
                    self.cleanup_tools["temp_files"] = TempFilesCleaner()

                # TODO: Add other cleanup tools as they become available
                # self.cleanup_tools['registry'] = RegistryCleaner()
                # self.cleanup_tools['cache'] = CacheCleaner()
                # self.cleanup_tools['logs'] = LogCleaner()

                self.logger.info(f"Initialized {len(self.cleanup_tools)} cleanup tools")
            else:
                self.logger.warning("Cleanup tools not available")

        except (
            Exception
        ) as e:  # ERR: non-fatal — tool init failure; UI still renders (degraded)  # noqa: E501
            self.logger.error(f"Error initializing cleanup tools: {e}")

    def customize_cleanup_interface(self):
        """Customize the interface for cleanup operations."""
        try:
            # Clear existing tabs and create cleanup-specific tabs
            self.tab_widget.clear()

            # Create cleanup-specific tabs
            self.create_quick_cleanup_tab()
            self.create_advanced_cleanup_tab()
            self.create_safety_backup_tab()
            self.create_cleanup_results_tab()

            # Update header section
            self.update_header_for_cleanup()

        except Exception as e:  # ERR: fatal — UI setup failed; tool cannot render
            self.logger.error(f"Error customizing cleanup interface: {e}")
            raise

    def update_header_for_cleanup(self):
        """Update the header section for cleanup operations."""
        try:
            # Find and update the header widget
            central_widget = self.centralWidget()
            if central_widget:
                layout = central_widget.layout()
                if layout and layout.count() > 0:
                    # Get the header widget (first item)
                    header_item = layout.itemAt(0)
                    if header_item:
                        header_widget = header_item.widget()
                        if isinstance(header_widget, QFrame):
                            # Update title and description
                            header_layout = header_widget.layout()
                            if header_layout:
                                title_layout = header_layout.itemAt(0)
                                if title_layout:
                                    title_widget = title_layout.itemAt(0)
                                    if title_widget:
                                        title_label = title_widget.widget()
                                        if isinstance(title_label, QLabel):
                                            title_label.setText(
                                                "System Cleanup & Optimization"
                                            )

                                    desc_widget = title_layout.itemAt(1)
                                    if desc_widget:
                                        desc_label = desc_widget.widget()
                                        if isinstance(desc_label, QLabel):
                                            desc_label.setText(
                                                "Comprehensive system cleanup and optimization tools"  # noqa: E501
                                            )
        except (
            Exception
        ) as e:  # ERR: non-fatal — cosmetic only; tool remains functional
            self.logger.error(f"Error updating header: {e}")

    def create_quick_cleanup_tab(self):
        """Create the quick cleanup tab with common operations."""
        try:
            quick_widget = QWidget()
            layout = QVBoxLayout(quick_widget)

            # Quick cleanup section
            quick_group = QGroupBox(_SystemCleanupStrings.GROUP_QUICK_CLEANUP)
            quick_layout = QVBoxLayout(quick_group)

            # Quick cleanup options
            self.quick_cleanup_options = {}

            # Temporary files cleanup
            temp_checkbox = QCheckBox(_SystemCleanupStrings.CHK_TEMP_FILES)
            temp_checkbox.setChecked(True)
            temp_checkbox.setToolTip(
                "Remove temporary files from system and user temp directories"
            )
            temp_checkbox.setAccessibleName("Clean Temporary Files")
            temp_checkbox.setAccessibleDescription(
                "Removes files from system and user temp directories"
            )
            temp_checkbox.setMinimumHeight(44)  # A11Y-8c
            self.quick_cleanup_options["temp_files"] = temp_checkbox
            quick_layout.addWidget(temp_checkbox)

            # Cache cleanup (placeholder for future implementation)
            cache_checkbox = QCheckBox(_SystemCleanupStrings.CHK_CACHE)
            cache_checkbox.setToolTip(
                "Clear application and system caches (Coming Soon)"
            )
            cache_checkbox.setEnabled(False)  # Disabled until implemented
            cache_checkbox.setAccessibleName("Clear Application Caches")
            cache_checkbox.setAccessibleDescription(
                "Clear application and system caches (Coming Soon)"
            )
            cache_checkbox.setMinimumHeight(44)  # A11Y-8c
            self.quick_cleanup_options["cache"] = cache_checkbox
            quick_layout.addWidget(cache_checkbox)

            # Windows logs cleanup (placeholder)
            logs_checkbox = QCheckBox(_SystemCleanupStrings.CHK_LOGS)
            logs_checkbox.setToolTip(
                "Remove old Windows system and application logs (Coming Soon)"
            )
            logs_checkbox.setEnabled(False)  # Disabled until implemented
            logs_checkbox.setAccessibleName("Clean Windows Logs")
            logs_checkbox.setAccessibleDescription(
                "Remove old Windows system and application logs (Coming Soon)"
            )
            logs_checkbox.setMinimumHeight(44)  # A11Y-8c
            self.quick_cleanup_options["logs"] = logs_checkbox
            quick_layout.addWidget(logs_checkbox)

            layout.addWidget(quick_group)

            # Quick cleanup controls
            controls_group = QGroupBox(_SystemCleanupStrings.GROUP_QUICK_CONTROLS)
            controls_layout = QHBoxLayout(controls_group)

            # Estimate button
            self.estimate_button = SecondaryButton(_SystemCleanupStrings.ESTIMATE_LABEL)
            self.estimate_button.clicked.connect(self.estimate_quick_cleanup)
            controls_layout.addWidget(self.estimate_button)

            # Run quick cleanup button
            self.quick_cleanup_button = PrimaryButton(
                _SystemCleanupStrings.BTN_RUN_QUICK_CLEANUP
            )
            self.quick_cleanup_button.clicked.connect(self.run_quick_cleanup)
            controls_layout.addWidget(self.quick_cleanup_button)

            layout.addWidget(controls_group)

            # Quick cleanup results
            results_group = QGroupBox(_SystemCleanupStrings.GROUP_CLEANUP_ESTIMATE)
            results_layout = QVBoxLayout(results_group)

            self.quick_results_text = QTextEdit()
            self.quick_results_text.setMaximumHeight(150)
            self.quick_results_text.setReadOnly(True)
            self.quick_results_text.setPlainText(
                _SystemCleanupStrings.TEXT_ESTIMATE_PROMPT
            )
            self.quick_results_text.setAccessibleName("Quick cleanup estimate results")
            results_layout.addWidget(self.quick_results_text)

            layout.addWidget(results_group)
            layout.addStretch()

            self.tab_widget.addTab(
                quick_widget, _SystemCleanupStrings.TAB_QUICK_CLEANUP
            )

        except Exception as e:  # ERR: fatal — primary tab missing; tool cannot function
            self.logger.error(f"Error creating quick cleanup tab: {e}")
            raise

    def create_advanced_cleanup_tab(self):
        """Create the advanced cleanup tab with detailed options."""
        try:
            advanced_widget = QWidget()
            layout = QVBoxLayout(advanced_widget)

            # Create scroll area for advanced options
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_widget = QWidget()
            scroll_layout = QVBoxLayout(scroll_widget)

            # Temporary Files Advanced Options
            if "temp_files" in self.cleanup_tools:
                temp_group = self.create_temp_files_advanced_group()
                scroll_layout.addWidget(temp_group)

            # Placeholder for other advanced tools
            placeholder_group = QGroupBox(_SystemCleanupStrings.GROUP_ADDITIONAL_TOOLS)
            placeholder_layout = QVBoxLayout(placeholder_group)
            placeholder_label = QLabel(
                _SystemCleanupStrings.LABEL_ADDITIONAL_TOOLS_COMING
            )
            placeholder_label.setStyleSheet(
                f"color: {token('text_muted')}; font-style: italic;"
            )
            placeholder_layout.addWidget(placeholder_label)

            tools_list = QLabel(_SystemCleanupStrings.LABEL_TOOLS_LIST)
            tools_list.setStyleSheet(
                f"color: {token('text_muted')}; margin-left: 20px;"
            )
            placeholder_layout.addWidget(tools_list)

            scroll_layout.addWidget(placeholder_group)
            scroll_layout.addStretch()

            scroll_area.setWidget(scroll_widget)
            layout.addWidget(scroll_area)

            self.tab_widget.addTab(
                advanced_widget, _SystemCleanupStrings.TAB_ADVANCED_TOOLS
            )

        except (
            Exception
        ) as e:  # ERR: non-fatal — secondary tab; core cleanup still available
            self.logger.error(f"Error creating advanced cleanup tab: {e}")
            _err_widget = QWidget()
            QVBoxLayout(_err_widget).addWidget(
                QLabel(_SystemCleanupStrings.LABEL_TOOLS_UNAVAILABLE)
            )
            self.tab_widget.addTab(
                _err_widget, _SystemCleanupStrings.TAB_ADVANCED_TOOLS
            )

    def create_temp_files_advanced_group(self) -> QGroupBox:
        """Create advanced options group for temporary files cleanup."""
        temp_group = QGroupBox(_SystemCleanupStrings.GROUP_TEMP_ADVANCED)
        temp_layout = QGridLayout(temp_group)

        # Age filter
        temp_layout.addWidget(QLabel(_SystemCleanupStrings.LABEL_AGE_FILTER), 0, 0)
        self.temp_age_spinbox = QSpinBox()
        self.temp_age_spinbox.setRange(0, 365)
        self.temp_age_spinbox.setValue(0)
        self.temp_age_spinbox.setToolTip(
            "0 = delete all temp files, >0 = only delete files older than specified days"  # noqa: E501
        )
        self.temp_age_spinbox.setAccessibleName(
            "Minimum age in days for temp files to delete"
        )
        self.temp_age_spinbox.setAccessibleDescription(
            "0 = delete all temp files; >0 = only delete files older than specified days"  # noqa: E501
        )
        self.temp_age_spinbox.setMinimumHeight(44)  # A11Y-8c
        temp_layout.addWidget(self.temp_age_spinbox, 0, 1)

        # Size filter
        temp_layout.addWidget(QLabel(_SystemCleanupStrings.LABEL_SIZE_FILTER), 1, 0)
        self.temp_size_spinbox = QSpinBox()
        self.temp_size_spinbox.setRange(0, 1000)
        self.temp_size_spinbox.setValue(0)
        self.temp_size_spinbox.setToolTip(
            "0 = delete all sizes, >0 = only delete files larger than specified MB"  # noqa: E501
        )
        self.temp_size_spinbox.setAccessibleName(
            "Minimum file size in megabytes for temp files to delete"
        )
        self.temp_size_spinbox.setAccessibleDescription(
            "0 = delete all file sizes; >0 = only delete files larger than specified megabytes"  # noqa: E501
        )
        self.temp_size_spinbox.setMinimumHeight(44)  # A11Y-8c
        temp_layout.addWidget(self.temp_size_spinbox, 1, 1)

        # Include system temp
        self.temp_system_checkbox = QCheckBox(_SystemCleanupStrings.CHK_TEMP_SYSTEM)
        self.temp_system_checkbox.setChecked(True)
        self.temp_system_checkbox.setToolTip(
            "Include Windows system temp directories (may require admin privileges)"  # noqa: E501
        )
        self.temp_system_checkbox.setAccessibleName("Include system temp directories")
        self.temp_system_checkbox.setAccessibleDescription(
            "May require administrator privileges to access Windows system directories"  # noqa: E501
        )
        self.temp_system_checkbox.setMinimumHeight(44)  # A11Y-8c
        temp_layout.addWidget(self.temp_system_checkbox, 2, 0, 1, 2)

        # Create backup
        self.temp_backup_checkbox = QCheckBox(_SystemCleanupStrings.CHK_TEMP_BACKUP)
        self.temp_backup_checkbox.setChecked(False)
        self.temp_backup_checkbox.setToolTip(
            "Create backup of files before deletion (uses additional disk space)"  # noqa: E501
        )
        self.temp_backup_checkbox.setAccessibleName("Create backup before deletion")
        self.temp_backup_checkbox.setAccessibleDescription(
            "Copies files to a backup location before deleting; uses additional disk space"  # noqa: E501
        )
        self.temp_backup_checkbox.setMinimumHeight(44)  # A11Y-8c
        temp_layout.addWidget(self.temp_backup_checkbox, 3, 0, 1, 2)

        # Secure delete
        self.temp_secure_checkbox = QCheckBox(_SystemCleanupStrings.CHK_TEMP_SECURE)
        self.temp_secure_checkbox.setChecked(False)
        self.temp_secure_checkbox.setToolTip(
            "Securely overwrite file data before deletion (slower but more secure)"  # noqa: E501
        )
        self.temp_secure_checkbox.setAccessibleName("Secure deletion overwrite")
        self.temp_secure_checkbox.setAccessibleDescription(
            "Overwrites file data before deletion to prevent recovery; significantly slower than standard deletion"  # noqa: E501
        )
        self.temp_secure_checkbox.setMinimumHeight(44)  # A11Y-8c
        temp_layout.addWidget(self.temp_secure_checkbox, 4, 0, 1, 2)

        # Action buttons
        button_layout = QHBoxLayout()

        self.preview_button = SecondaryButton(_SystemCleanupStrings.PREVIEW_LABEL)
        preview_button = self.preview_button
        preview_button.clicked.connect(self.preview_temp_cleanup)
        button_layout.addWidget(preview_button)

        self.execute_button = PrimaryButton(
            _SystemCleanupStrings.BTN_EXECUTE_TEMP_CLEANUP
        )
        execute_button = self.execute_button
        execute_button.clicked.connect(self.execute_temp_cleanup)
        button_layout.addWidget(execute_button)

        temp_layout.addLayout(button_layout, 5, 0, 1, 2)

        return temp_group

    def create_safety_backup_tab(self):
        """Create the safety and backup management tab."""
        try:
            safety_widget = QWidget()
            layout = QVBoxLayout(safety_widget)

            # Safety settings
            safety_group = QGroupBox(_SystemCleanupStrings.GROUP_SAFETY_SETTINGS)
            safety_layout = QVBoxLayout(safety_group)

            # Create restore point
            self.restore_point_checkbox = QCheckBox(
                _SystemCleanupStrings.CHK_RESTORE_POINT
            )
            self.restore_point_checkbox.setChecked(True)
            self.restore_point_checkbox.setToolTip(
                "Create a system restore point before performing cleanup operations"  # noqa: E501
            )
            self.restore_point_checkbox.setAccessibleName(
                "Create system restore point before cleanup"
            )
            self.restore_point_checkbox.setMinimumHeight(44)  # A11Y-8c
            safety_layout.addWidget(self.restore_point_checkbox)

            # Backup important files
            self.backup_files_checkbox = QCheckBox(
                _SystemCleanupStrings.CHK_BACKUP_FILES
            )
            self.backup_files_checkbox.setChecked(True)
            self.backup_files_checkbox.setToolTip(
                "Create backups of important files before deletion"
            )
            self.backup_files_checkbox.setAccessibleName(
                "Backup important files before deletion"
            )
            self.backup_files_checkbox.setMinimumHeight(44)  # A11Y-8c
            safety_layout.addWidget(self.backup_files_checkbox)

            # Confirmation dialogs
            self.confirm_operations_checkbox = QCheckBox(
                _SystemCleanupStrings.CHK_CONFIRM_OPS
            )
            self.confirm_operations_checkbox.setChecked(True)
            self.confirm_operations_checkbox.setToolTip(
                "Show confirmation dialogs before performing potentially destructive operations"  # noqa: E501
            )
            self.confirm_operations_checkbox.setAccessibleName(
                "Show confirmation dialogs for destructive operations"
            )
            self.confirm_operations_checkbox.setMinimumHeight(44)  # A11Y-8c
            safety_layout.addWidget(self.confirm_operations_checkbox)

            layout.addWidget(safety_group)

            # Backup management
            backup_group = QGroupBox(_SystemCleanupStrings.GROUP_BACKUP_MGMT)
            backup_layout = QVBoxLayout(backup_group)

            # Backup location
            backup_info_layout = QHBoxLayout()
            backup_info_layout.addWidget(
                QLabel(_SystemCleanupStrings.LABEL_BACKUP_LOCATION)
            )
            self.backup_location_label = QLabel(
                _SystemCleanupStrings.LABEL_BACKUP_NOT_INITIALIZED
            )
            if self.safety_manager:
                self.backup_location_label.setText(
                    str(self.safety_manager.session_backup_dir)
                )
            backup_info_layout.addWidget(self.backup_location_label)
            backup_layout.addLayout(backup_info_layout)

            # Backup actions
            backup_actions_layout = QHBoxLayout()

            self.view_backups_button = SecondaryButton(
                _SystemCleanupStrings.BTN_VIEW_BACKUPS
            )
            view_backups_button = self.view_backups_button
            view_backups_button.clicked.connect(self.view_backups)
            backup_actions_layout.addWidget(view_backups_button)

            self.cleanup_backups_button = DestructiveButton(
                _SystemCleanupStrings.BTN_CLEANUP_OLD_BACKUPS
            )
            self.cleanup_backups_button.set_confirmation_callback(
                lambda: ConfirmationModal(
                    _SystemCleanupStrings.CONFIRM_BACKUP_CLEANUP_TITLE,
                    _SystemCleanupStrings.CONFIRM_BACKUP_CLEANUP_MSG,
                    _SystemCleanupStrings.CONFIRM_BACKUP_CLEANUP_YES,
                    _SystemCleanupStrings.CONFIRM_CANCEL,
                    self,
                ).exec_()
                == QDialog.Accepted
            )
            self.cleanup_backups_button.action_confirmed.connect(
                self.cleanup_old_backups
            )
            backup_actions_layout.addWidget(self.cleanup_backups_button)

            self.restore_backups_button = DestructiveButton(
                _SystemCleanupStrings.BTN_RESTORE_ALL_BACKUPS
            )
            self.restore_backups_button.set_confirmation_callback(
                lambda: ConfirmationModal(
                    _SystemCleanupStrings.CONFIRM_RESTORE_ALL_TITLE,
                    _SystemCleanupStrings.CONFIRM_RESTORE_ALL_MSG,
                    _SystemCleanupStrings.CONFIRM_RESTORE_ALL_YES,
                    _SystemCleanupStrings.CONFIRM_CANCEL,
                    self,
                ).exec_()
                == QDialog.Accepted
            )
            self.restore_backups_button.action_confirmed.connect(
                self.restore_all_backups
            )
            backup_actions_layout.addWidget(self.restore_backups_button)

            backup_layout.addLayout(backup_actions_layout)

            layout.addWidget(backup_group)

            # System information
            system_group = QGroupBox(_SystemCleanupStrings.GROUP_SYSTEM_INFO)
            system_layout = QVBoxLayout(system_group)

            self.system_info_text = QTextEdit()
            self.system_info_text.setReadOnly(True)
            self.system_info_text.setMaximumHeight(200)
            self.system_info_text.setAccessibleName("System information")
            self.update_system_info_display()
            system_layout.addWidget(self.system_info_text)

            layout.addWidget(system_group)
            layout.addStretch()

            self.tab_widget.addTab(
                safety_widget, _SystemCleanupStrings.TAB_SAFETY_BACKUPS
            )

        except (
            Exception
        ) as e:  # ERR: non-fatal — secondary tab; core cleanup still available
            self.logger.error(f"Error creating safety backup tab: {e}")
            _err_widget = QWidget()
            QVBoxLayout(_err_widget).addWidget(
                QLabel(_SystemCleanupStrings.LABEL_SAFETY_UNAVAILABLE)
            )
            self.tab_widget.addTab(
                _err_widget, _SystemCleanupStrings.TAB_SAFETY_BACKUPS
            )

    def create_cleanup_results_tab(self):
        """Create the cleanup results and reports tab."""
        try:
            results_widget = QWidget()
            layout = QVBoxLayout(results_widget)

            # Current operation status
            status_group = QGroupBox(_SystemCleanupStrings.GROUP_OP_STATUS)
            status_layout = QVBoxLayout(status_group)

            # Progress bar
            self.cleanup_progress_bar = QProgressBar()
            self.cleanup_progress_bar.setVisible(False)
            status_layout.addWidget(self.cleanup_progress_bar)

            # Status label
            self.cleanup_status_label = QLabel(_SystemCleanupStrings.LABEL_NO_OPERATION)
            status_layout.addWidget(self.cleanup_status_label)

            # Stop button
            self.stop_cleanup_button = SecondaryButton(
                _SystemCleanupStrings.BTN_STOP_OPERATION
            )
            self.stop_cleanup_button.clicked.connect(self.stop_current_cleanup)
            self.stop_cleanup_button.setVisible(False)
            status_layout.addWidget(self.stop_cleanup_button)

            # Loading indicator (spec §8.1, CP-6b / CP-7b/c)
            if LoadingIndicator:
                self._loading_indicator = LoadingIndicator(
                    status_group,
                    cancellable=True,
                    message=_SystemCleanupStrings.LOADING_INDICATOR_MSG,
                )
                self._loading_indicator.cancelled.connect(self.stop_current_cleanup)
                status_layout.addWidget(self._loading_indicator)

            layout.addWidget(status_group)

            # Results display
            results_group = QGroupBox(_SystemCleanupStrings.GROUP_CLEANUP_RESULTS)
            results_layout = QVBoxLayout(results_group)

            self.results_text = QTextEdit()
            self.results_text.setReadOnly(True)
            self.results_text.setPlainText(_SystemCleanupStrings.TEXT_NO_RESULTS)
            self.results_text.setAccessibleName("Cleanup results report")
            results_layout.addWidget(self.results_text)

            # Export results button
            self.export_button = SecondaryButton(
                _SystemCleanupStrings.BTN_EXPORT_RESULTS
            )
            export_button = self.export_button
            export_button.clicked.connect(self.export_results_report)
            results_layout.addWidget(export_button)

            layout.addWidget(results_group)

            self.tab_widget.addTab(
                results_widget, _SystemCleanupStrings.TAB_RESULTS_REPORTS
            )

        except (
            Exception
        ) as e:  # ERR: fatal — results/progress tab missing; operation feedback unavailable  # noqa: E501
            self.logger.error(f"Error creating cleanup results tab: {e}")
            raise

    def setup_cleanup_signals(self):
        """Setup cleanup-specific signal connections."""
        try:
            # Connect cleanup signals to update UI
            self.cleanup_started.connect(self.on_cleanup_started)
            self.cleanup_completed.connect(self.on_cleanup_completed)
            self.cleanup_progress.connect(self.on_cleanup_progress)

        except (
            Exception
        ) as e:  # ERR: non-fatal — GUI event signals unused; no user impact
            self.logger.error(f"Error setting up cleanup signals: {e}")

    def estimate_quick_cleanup(self):
        """Estimate space freed by quick cleanup (async — PERF-1d).

        Runs the O(n) temp-directory scan in an EstimateWorker thread so the
        UI thread is never blocked for the duration of the filesystem walk.
        """
        # TEL-2b: KEY_ACTION 1 — Full System Scan (estimate variant)
        _emit_telemetry(
            "ui_user_action",
            tool_id="system_cleanup",
            action="estimate_quick_cleanup",
        )
        try:
            # TEL-4a: performance metric — estimate operation start
            _emit_telemetry(
                "ui_performance_metric",
                tool_id="system_cleanup",
                operation="estimate",
                phase="start",
            )
            # If temp_files is not selected / available, render static results
            # immediately without spinning up a thread.
            if (
                not self.quick_cleanup_options["temp_files"].isChecked()
                or "temp_files" not in self.cleanup_tools
            ):
                static_results = []
                if self.quick_cleanup_options["cache"].isChecked():
                    static_results.append("Application Caches: Coming Soon")
                if self.quick_cleanup_options["logs"].isChecked():
                    static_results.append("Windows Logs: Coming Soon")
                text = "Estimated space to be freed: 0 B\n\nBreakdown:\n" + "\n".join(
                    f"• {r}" for r in static_results
                )
                if not static_results:
                    text += "\n\nNo cleanup tools are currently selected or available."  # noqa: E501
                self.quick_results_text.setPlainText(text)
                return

            self.quick_results_text.setPlainText(
                _SystemCleanupStrings.STATUS_ESTIMATING
            )

            temp_tool = self.cleanup_tools["temp_files"]
            self._estimate_worker = EstimateWorker(
                temp_tool,
                max_age_days=0,
                min_size_bytes=0,
                include_system_temp=True,
            )
            self._estimate_thread = QThread()
            self._estimate_worker.moveToThread(self._estimate_thread)

            self._estimate_thread.started.connect(self._estimate_worker.run)
            self._estimate_worker.estimate_ready.connect(self._on_estimate_ready)
            self._estimate_worker.error_occurred.connect(self._on_estimate_error)
            self._estimate_worker.estimate_ready.connect(self._estimate_thread.quit)
            self._estimate_worker.error_occurred.connect(self._estimate_thread.quit)
            self._estimate_thread.finished.connect(self._cleanup_estimate_thread)

            if self._loading_indicator:
                self._estimate_thread.started.connect(self._loading_indicator.start)
                self._estimate_thread.finished.connect(self._loading_indicator.stop)

            self._estimate_thread.start()

        except Exception as e:  # ERR: non-fatal — surfaced in quick_results_text
            self.logger.error(f"Error estimating quick cleanup: {e}")
            self.quick_results_text.setPlainText(
                _SystemCleanupStrings.STATUS_ESTIMATE_ERROR
            )

    def _on_estimate_ready(self, temp_size: int) -> None:
        """Receive estimate result from EstimateWorker and update the UI."""
        # TEL-4b: performance metric — estimate operation stop
        _emit_telemetry(
            "ui_performance_metric",
            tool_id="system_cleanup",
            operation="estimate",
            phase="stop",
        )
        try:
            results = [f"Temporary Files: {self._format_size(temp_size)}"]
            if self.quick_cleanup_options["cache"].isChecked():
                results.append("Application Caches: Coming Soon")
            if self.quick_cleanup_options["logs"].isChecked():
                results.append("Windows Logs: Coming Soon")

            results_text = (
                f"Estimated space to be freed: {self._format_size(temp_size)}\n\n"  # noqa: E501
                "Breakdown:\n" + "\n".join(f"• {r}" for r in results)
            )
            if temp_size == 0:
                results_text += (
                    "\n\nNo cleanup tools are currently selected or available."
                )
            self.quick_results_text.setPlainText(results_text)
        except Exception as e:  # ERR: non-fatal — surfaced in quick_results_text
            self.logger.error(f"Error displaying estimate result: {e}")
            self.quick_results_text.setPlainText(
                _SystemCleanupStrings.STATUS_ESTIMATE_DISPLAY_ERROR
            )

    def _on_estimate_error(
        self, error_msg: str
    ) -> None:  # ERR: non-fatal — surfaced in quick_results_text
        """Handle EstimateWorker failure."""
        # TEL-3a: error event (error_code only — no stack trace per TEL-3b)
        _emit_telemetry(
            "ui_error_event",
            tool_id="system_cleanup",
            error_code="estimate_worker_error",
        )
        # TEL-4b: performance metric — estimate operation stop (via error path)
        _emit_telemetry(
            "ui_performance_metric",
            tool_id="system_cleanup",
            operation="estimate",
            phase="stop",
        )
        self.logger.error(f"Estimate worker error: {error_msg}")
        self.quick_results_text.setPlainText(
            _SystemCleanupStrings.STATUS_ESTIMATE_ERROR
        )

    def _cleanup_estimate_thread(self) -> None:
        """Release EstimateWorker and its thread after completion."""
        worker = getattr(self, "_estimate_worker", None)
        thread = getattr(self, "_estimate_thread", None)
        if worker is not None:
            worker.deleteLater()
            self._estimate_worker = None
        if thread is not None:
            thread.deleteLater()
            self._estimate_thread = None

    def run_quick_cleanup(self):
        """Run the quick cleanup operation."""
        # TEL-2b: KEY_ACTION 4 — Run Cleanup Programs
        _emit_telemetry(
            "ui_user_action",
            tool_id="system_cleanup",
            action="run_cleanup_programs",
        )
        try:
            # Check if any options are selected
            selected_tools = [
                name
                for name, checkbox in self.quick_cleanup_options.items()
                if checkbox.isChecked() and checkbox.isEnabled()
            ]

            if not selected_tools:
                Modal(
                    _SystemCleanupStrings.MODAL_NO_TOOLS_TITLE,
                    _SystemCleanupStrings.MODAL_NO_TOOLS_MSG,
                    ["OK"],
                    self,
                ).exec_()
                return

            # Confirm operation
            if self.confirm_operations_checkbox.isChecked():
                if (
                    ConfirmationModal(
                        _SystemCleanupStrings.CONFIRM_QUICK_CLEANUP_TITLE,
                        f"Are you sure you want to run quick cleanup?\n\n"
                        f"Selected tools: {', '.join(selected_tools)}\n\n"
                        f"This operation may delete files permanently.",
                        confirm_text=_SystemCleanupStrings.CONFIRM_YES,
                        cancel_text=_SystemCleanupStrings.CONFIRM_CANCEL,
                        parent=self,
                    ).exec_()
                    != QDialog.Accepted
                ):
                    return

            # Restore point created inside the worker thread (PERF-1d): pass
            # the description so CleanupWorker.run() calls it off the UI thread.  # noqa: E501
            restore_desc = (
                "RFU System Cleanup - Quick Cleanup"
                if self.restore_point_checkbox.isChecked()
                else ""
            )

            # Run temp files cleanup if selected
            if "temp_files" in selected_tools and "temp_files" in self.cleanup_tools:

                self.execute_temp_cleanup_with_defaults(
                    restore_point_description=restore_desc
                )

            # TODO: Add other quick cleanup operations as tools become available  # noqa: E501

        except Exception as e:  # ERR: non-fatal — surfaced via Modal
            self.logger.error(f"Error running quick cleanup: {e}")
            Modal(
                _SystemCleanupStrings.MODAL_QUICK_ERR_TITLE,
                _SystemCleanupStrings.MODAL_QUICK_ERR_MSG,
                ["OK"],
                self,
            ).exec_()

    def execute_temp_cleanup_with_defaults(self, restore_point_description: str = ""):
        """Execute temp files cleanup with default quick cleanup settings.

        Args:
            restore_point_description: If non-empty, create a restore point
                inside the worker thread before cleanup (PERF-1d).
        """
        try:
            if "temp_files" not in self.cleanup_tools:
                return

            temp_tool = self.cleanup_tools["temp_files"]

            # Use default settings for quick cleanup
            params = {
                "max_age_days": 0,  # Delete all temp files
                "min_size_bytes": 0,  # All sizes
                "file_extensions": [],  # All extensions
                "include_system_temp": True,
                "create_backup": self.backup_files_checkbox.isChecked(),
                "secure_delete": False,  # Fast deletion for quick cleanup
            }

            self.execute_cleanup_operation(
                temp_tool,
                params,
                "Temporary Files",
                restore_point_description=restore_point_description,
            )

        except Exception as e:  # ERR: non-fatal — surfaced via status label
            self.logger.error(f"Error executing temp cleanup with defaults: {e}")
            if hasattr(self, "status_label"):
                self.status_label.setText(_SystemCleanupStrings.STATUS_UNABLE_TO_START)

    def preview_temp_cleanup(self):
        """Preview temporary files cleanup operation (async — PERF-1d).

        Runs the O(n) temp-directory scan in a PreviewWorker thread so the
        UI thread is never blocked for the duration of the filesystem walk.
        """
        # TEL-2b: KEY_ACTION 3 — Preview Cleanup Targets
        _emit_telemetry(
            "ui_user_action",
            tool_id="system_cleanup",
            action="preview_cleanup_targets",
        )
        try:
            # TEL-4a: performance metric — preview operation start
            _emit_telemetry(
                "ui_performance_metric",
                tool_id="system_cleanup",
                operation="preview",
                phase="start",
            )
            if "temp_files" not in self.cleanup_tools:
                Modal(
                    _SystemCleanupStrings.MODAL_TOOL_NA_TITLE,
                    _SystemCleanupStrings.MODAL_TOOL_NA_MSG,
                    ["OK"],
                    self,
                ).exec_()
                return

            temp_tool = self.cleanup_tools["temp_files"]
            params = self.get_temp_cleanup_params()

            self._preview_worker = PreviewWorker(temp_tool, params)
            self._preview_thread = QThread()
            self._preview_worker.moveToThread(self._preview_thread)

            self._preview_thread.started.connect(self._preview_worker.run)
            self._preview_worker.preview_ready.connect(
                lambda preview: self._on_preview_ready(
                    "Temporary Files Cleanup", preview
                )
            )
            self._preview_worker.error_occurred.connect(self._on_preview_error)
            self._preview_worker.preview_ready.connect(self._preview_thread.quit)
            self._preview_worker.error_occurred.connect(self._preview_thread.quit)
            self._preview_thread.finished.connect(self._cleanup_preview_thread)

            if self._loading_indicator:
                self._preview_thread.started.connect(self._loading_indicator.start)
                self._preview_thread.finished.connect(self._loading_indicator.stop)

            self._preview_thread.start()

        except Exception as e:  # ERR: non-fatal — surfaced via Modal
            self.logger.error(f"Error previewing temp cleanup: {e}")
            Modal(
                _SystemCleanupStrings.MODAL_PREVIEW_ERR_TITLE,
                _SystemCleanupStrings.MODAL_PREVIEW_ERR_MSG,
                ["OK"],
                self,
            ).exec_()

    def _on_preview_ready(self, title: str, preview: dict) -> None:
        """Receive preview result from PreviewWorker and display it."""
        # TEL-4b: performance metric — preview operation stop
        _emit_telemetry(
            "ui_performance_metric",
            tool_id="system_cleanup",
            operation="preview",
            phase="stop",
        )
        self.show_cleanup_preview(title, preview)

    def _on_preview_error(
        self, error_msg: str
    ) -> None:  # ERR: non-fatal — surfaced via Modal
        """Handle PreviewWorker failure."""
        # TEL-3a: error event (error_code only — no stack trace per TEL-3b)
        _emit_telemetry(
            "ui_error_event",
            tool_id="system_cleanup",
            error_code="preview_worker_error",
        )
        # TEL-4b: performance metric — preview operation stop (via error path)
        _emit_telemetry(
            "ui_performance_metric",
            tool_id="system_cleanup",
            operation="preview",
            phase="stop",
        )
        self.logger.error(f"Preview worker error: {error_msg}")
        Modal(
            _SystemCleanupStrings.MODAL_PREVIEW_ERR_TITLE,
            _SystemCleanupStrings.MODAL_PREVIEW_ERR_MSG,
            ["OK"],
            self,
        ).exec_()

    def _cleanup_preview_thread(self) -> None:
        """Release PreviewWorker and its thread after completion."""
        worker = getattr(self, "_preview_worker", None)
        thread = getattr(self, "_preview_thread", None)
        if worker is not None:
            worker.deleteLater()
            self._preview_worker = None
        if thread is not None:
            thread.deleteLater()
            self._preview_thread = None

    def show_cleanup_preview(self, title: str, preview: dict) -> None:
        """Display a cleanup preview result in a modal dialog.

        This is a pure UI method called on the main thread after the
        PreviewWorker has finished its filesystem scan.
        """
        try:
            lines = [f"Preview: {title}", ""]
            if isinstance(preview, dict):
                estimated_files = preview.get("estimated_files", 0)
                estimated_size = preview.get("estimated_size", 0)
                directories = preview.get("temp_directories", [])
                warnings = preview.get("warnings", [])

                lines.append(f"Estimated files to remove: {estimated_files}")
                lines.append(
                    f"Estimated space to free:   {self._format_size(estimated_size)}"  # noqa: E501
                )

                if directories:
                    lines.append("\nDirectories:")
                    for d in directories:
                        accessible = "✓" if d.get("accessible") else "✗"
                        lines.append(
                            f"  {accessible} {d.get('path', '')} "
                            f"({d.get('file_count', 0)} files, "
                            f"{self._format_size(d.get('size', 0))})"
                        )

                if warnings:
                    lines.append("\nWarnings:")
                    for w in warnings:
                        lines.append(f"  ⚠ {w}")
            else:
                lines.append(str(preview))

            Modal(title, "\n".join(lines), ["OK"], self).exec_()
        except Exception as e:  # ERR: non-fatal — surfaced via Modal
            self.logger.error(f"Error showing cleanup preview: {e}")
            Modal(
                _SystemCleanupStrings.MODAL_PREVIEW_ERR_TITLE,
                _SystemCleanupStrings.MODAL_PREVIEW_DISPLAY_ERR_MSG,
                ["OK"],
                self,
            ).exec_()

    def _format_size(self, size_bytes: int) -> str:
        """Format a byte count into a human-readable string."""
        for unit in ("B", "KB", "MB", "GB", "TB"):
            if abs(size_bytes) < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"

    def execute_temp_cleanup(self):
        """Execute temporary files cleanup operation."""
        try:
            if "temp_files" not in self.cleanup_tools:
                Modal(
                    _SystemCleanupStrings.MODAL_TOOL_NA_TITLE,
                    _SystemCleanupStrings.MODAL_TOOL_NA_MSG,
                    ["OK"],
                    self,
                ).exec_()
                return

            # Confirm operation
            if self.confirm_operations_checkbox.isChecked():
                if (
                    ConfirmationModal(
                        _SystemCleanupStrings.CONFIRM_TEMP_CLEANUP_TITLE,
                        _SystemCleanupStrings.CONFIRM_TEMP_CLEANUP_MSG,
                        confirm_text=_SystemCleanupStrings.CONFIRM_YES,
                        cancel_text=_SystemCleanupStrings.CONFIRM_CANCEL,
                        parent=self,
                    ).exec_()
                    != QDialog.Accepted
                ):
                    return

            # Restore point created inside the worker thread (PERF-1d).
            restore_desc = (
                "RFU System Cleanup - Temp Files"
                if self.restore_point_checkbox.isChecked()
                else ""
            )

            temp_tool = self.cleanup_tools["temp_files"]
            params = self.get_temp_cleanup_params()

            self.execute_cleanup_operation(
                temp_tool,
                params,
                "Temporary Files",
                restore_point_description=restore_desc,
            )

        except Exception as e:  # ERR: non-fatal — surfaced via Modal
            self.logger.error(f"Error executing temp cleanup: {e}")
            Modal(
                _SystemCleanupStrings.MODAL_CLEANUP_ERR_TITLE,
                _SystemCleanupStrings.MODAL_CLEANUP_ERR_MSG_UNABLE,
                ["OK"],
                self,
            ).exec_()

    def get_temp_cleanup_params(self) -> Dict[str, Any]:
        """Get temporary files cleanup parameters from UI."""
        return {
            "max_age_days": self.temp_age_spinbox.value(),
            "min_size_bytes": self.temp_size_spinbox.value()
            * 1024
            * 1024,  # Convert MB to bytes
            "file_extensions": [],  # TODO: Add extension filter UI
            "include_system_temp": self.temp_system_checkbox.isChecked(),
            "create_backup": self.temp_backup_checkbox.isChecked(),
            "secure_delete": self.temp_secure_checkbox.isChecked(),
        }

    def execute_cleanup_operation(
        self,
        cleanup_tool,
        params,
        tool_name,
        restore_point_description: str = "",
    ):
        """Execute a cleanup operation in a worker thread.

        Args:
            cleanup_tool: The cleanup tool to execute.
            params: Parameters dict passed to the tool's execute_operation().
            tool_name: Display name shown in the status bar.
            restore_point_description: If non-empty, create a system restore
                point with this description at the start of the worker run
                (PERF-1d: keeps PowerShell call off the UI thread).
        """
        try:
            # Check if another operation is running
            if self.current_worker is not None:
                Modal(
                    _SystemCleanupStrings.MODAL_OP_IN_PROGRESS_TITLE,
                    _SystemCleanupStrings.MODAL_OP_IN_PROGRESS_MSG,
                    ["OK"],
                    self,
                ).exec_()
                return

            # Create and configure worker thread (restore point handled inside
            # the worker so the UI thread is never blocked by PowerShell)
            safety_mgr = self.safety_manager if restore_point_description else None
            self.current_worker = CleanupWorker(
                cleanup_tool,
                params,
                safety_manager=safety_mgr,
                restore_point_description=restore_point_description,
            )
            self.worker_thread = QThread()
            self.current_worker.moveToThread(self.worker_thread)

            # Connect signals
            self.worker_thread.started.connect(self.current_worker.run)
            self.current_worker.operation_complete.connect(self.on_cleanup_complete)
            self.current_worker.error_occurred.connect(self.on_cleanup_error)
            self.current_worker.operation_complete.connect(self.worker_thread.quit)
            self.current_worker.error_occurred.connect(self.worker_thread.quit)
            self.worker_thread.finished.connect(self.cleanup_worker_finished)

            # Loading indicator wiring (spec §8.1, CP-6c/d)
            if self._loading_indicator:
                self.worker_thread.started.connect(self._loading_indicator.start)
                self.worker_thread.finished.connect(self._loading_indicator.stop)

            # TEL-4a: performance metric — cleanup execution start
            _emit_telemetry(
                "ui_performance_metric",
                tool_id="system_cleanup",
                operation="execute_cleanup",
                phase="start",
            )
            # Start the thread
            self.worker_thread.start()
            self.status_label.setText(f"Running {tool_name}...")

        except Exception as e:  # ERR: non-fatal — surfaced via Modal
            self.logger.error(f"Error starting cleanup operation: {e}")
            Modal(
                _SystemCleanupStrings.MODAL_CLEANUP_ERR_TITLE,
                _SystemCleanupStrings.MODAL_CLEANUP_ERR_MSG_START,
                ["OK"],
                self,
            ).exec_()

    def on_cleanup_complete(self, result):
        """Handle cleanup operation completion."""
        # TEL-4b: performance metric — cleanup execution stop
        _emit_telemetry(
            "ui_performance_metric",
            tool_id="system_cleanup",
            operation="execute_cleanup",
            phase="stop",
        )
        try:
            if result and hasattr(result, "success") and result.success:
                message = "Cleanup completed successfully!\n\n"
                if hasattr(result, "files_removed"):
                    message += f"Files removed: {result.files_removed}\n"
                if hasattr(result, "space_freed"):
                    message += f"Space freed: {result.space_freed / (1024**2):.2f} MB\n"  # noqa: E501

                Modal(
                    _SystemCleanupStrings.MODAL_CLEANUP_COMPLETE_TITLE,
                    message,
                    ["OK"],
                    self,
                ).exec_()
            else:
                error_msg = (
                    getattr(result, "error", "Unknown error")
                    if result
                    else "No result returned"
                )
                Modal(
                    _SystemCleanupStrings.MODAL_CLEANUP_WARNING_TITLE,
                    f"Cleanup completed with issues:\n{error_msg}",
                    ["OK"],
                    self,
                ).exec_()

            if self._toast:
                self._toast.show_message(
                    _SystemCleanupStrings.STATUS_CLEANUP_COMPLETED, "success"
                )
            else:
                self.status_label.setText(
                    _SystemCleanupStrings.STATUS_CLEANUP_COMPLETED
                )

        except (
            Exception
        ) as e:  # ERR: non-fatal — completion display failure; cleanup already done  # noqa: E501
            self.logger.error(f"Error handling cleanup completion: {e}")

    def on_cleanup_error(
        self, error_msg
    ):  # ERR: non-fatal — worker error; surfaced inline
        """Handle cleanup operation error."""
        # TEL-3a: error event (error_code only — no stack trace per TEL-3b)
        _emit_telemetry(
            "ui_error_event",
            tool_id="system_cleanup",
            error_code="cleanup_worker_error",
        )
        # TEL-4b: performance metric — cleanup execution stop (via error path)
        _emit_telemetry(
            "ui_performance_metric",
            tool_id="system_cleanup",
            operation="execute_cleanup",
            phase="stop",
        )
        self.logger.error(f"Cleanup error: {error_msg}")
        Modal(
            _SystemCleanupStrings.MODAL_CLEANUP_ERR_TITLE,
            _SystemCleanupStrings.MODAL_CLEANUP_ERR_MSG_WORKER,
            ["OK"],
            self,
        ).exec_()
        if self._toast:
            self._toast.show_message(
                _SystemCleanupStrings.STATUS_CLEANUP_FAILED, "error"
            )
        else:
            self.status_label.setText(_SystemCleanupStrings.STATUS_CLEANUP_FAILED)

    def export_results_report(self):
        """Export the cleanup results report.

        TODO: Implement full file-export functionality (see FN-032).
        """
        # TEL-2b: KEY_ACTION 6 — Export Report
        _emit_telemetry(
            "ui_user_action",
            tool_id="system_cleanup",
            action="export_report",
        )
        Modal(
            _SystemCleanupStrings.MODAL_EXPORT_TITLE,
            _SystemCleanupStrings.MODAL_EXPORT_MSG,
            ["OK"],
            self,
        ).exec_()

    def on_cleanup_started(self, tool_name: str) -> None:
        """Handle cleanup_started signal."""
        if hasattr(self, "cleanup_status_label"):
            self.cleanup_status_label.setText(f"Starting {tool_name}...")

    def on_cleanup_completed(self, tool_name: str, result) -> None:
        """Handle cleanup_completed signal."""
        if hasattr(self, "cleanup_status_label"):
            self.cleanup_status_label.setText(f"{tool_name} complete")

    def on_cleanup_progress(
        self, tool_name: str, percentage: int, message: str
    ) -> None:
        """Handle cleanup_progress signal."""
        if hasattr(self, "cleanup_progress_bar"):
            self.cleanup_progress_bar.setValue(percentage)
        if hasattr(self, "cleanup_status_label"):
            self.cleanup_status_label.setText(message)

    def stop_current_cleanup(self):
        """Stop the currently running cleanup operation (CP-7)."""
        # TEL-2b: KEY_ACTION 8 — Stop / Cancel Scan
        _emit_telemetry(
            "ui_user_action",
            tool_id="system_cleanup",
            action="stop_cancel_scan",
        )
        if self.current_worker is not None:
            self.current_worker.stop()

    def cleanup_worker_finished(self):
        """Cleanup after worker thread finishes."""
        try:
            if self.worker_thread:
                self.worker_thread.deleteLater()
                self.worker_thread = None
            self.current_worker = None
        except Exception as e:  # ERR: non-fatal — teardown; operation already complete
            self.logger.error(f"Error cleaning up worker thread: {e}")

    # ------------------------------------------------------------------
    # Backup-tab delegation methods (FN-012)
    # These delegate to self.safety_manager, which is initialised in
    # init_cleanup_tools() when SafetyManager is available.
    # ------------------------------------------------------------------

    def view_backups(self):
        """Open the session backup directory in the system file explorer."""
        # TEL-2b: backup management action
        _emit_telemetry(
            "ui_user_action",
            tool_id="system_cleanup",
            action="view_backups",
        )
        if not self.safety_manager:
            Modal(
                _SystemCleanupStrings.MODAL_BACKUPS_NA_TITLE,
                _SystemCleanupStrings.MODAL_BACKUPS_NO_DIR_MSG,
                ["OK"],
                self,
            ).exec_()
            return
        backup_dir = str(self.safety_manager.session_backup_dir)
        try:
            import subprocess

            subprocess.Popen(["explorer", backup_dir])
        except Exception as exc:  # ERR: non-fatal — surfaced via Modal
            self.logger.error(f"Cannot open backup directory: {exc}")
            Modal(
                _SystemCleanupStrings.MODAL_CANT_OPEN_DIR_TITLE,
                _SystemCleanupStrings.MODAL_CANT_OPEN_DIR_MSG,
                ["OK"],
                self,
            ).exec_()

    def cleanup_old_backups(self):
        """Delete backups older than 7 days via the safety manager."""
        # TEL-2b: backup management action
        _emit_telemetry(
            "ui_user_action",
            tool_id="system_cleanup",
            action="cleanup_old_backups",
        )
        if not self.safety_manager:
            Modal(
                _SystemCleanupStrings.MODAL_BACKUPS_NA_TITLE,
                _SystemCleanupStrings.MODAL_BACKUPS_NA_MSG,
                ["OK"],
                self,
            ).exec_()
            return
        success = self.safety_manager.cleanup_old_backups(days_old=7)
        if success:
            Modal(
                _SystemCleanupStrings.MODAL_BACKUPS_CLEANED_TITLE,
                _SystemCleanupStrings.MODAL_BACKUPS_CLEANED_MSG,
                ["OK"],
                self,
            ).exec_()
        else:
            Modal(
                _SystemCleanupStrings.MODAL_BACKUPS_FAILED_TITLE,
                _SystemCleanupStrings.MODAL_BACKUPS_FAILED_MSG,
                ["OK"],
                self,
            ).exec_()

    def restore_all_backups(self):
        """Restore all session backups via the safety manager."""
        # TEL-2b: KEY_ACTION 7 — Undo Recent Cleanup
        _emit_telemetry(
            "ui_user_action",
            tool_id="system_cleanup",
            action="undo_recent_cleanup",
        )
        if not self.safety_manager:
            Modal(
                _SystemCleanupStrings.MODAL_BACKUPS_NA_TITLE,
                _SystemCleanupStrings.MODAL_BACKUPS_RESTORE_NA_MSG,
                ["OK"],
                self,
            ).exec_()
            return
        success = self.safety_manager.restore_all_backups()
        if success:
            Modal(
                _SystemCleanupStrings.MODAL_RESTORE_COMPLETE_TITLE,
                _SystemCleanupStrings.MODAL_RESTORE_COMPLETE_MSG,
                ["OK"],
                self,
            ).exec_()
        else:
            Modal(
                _SystemCleanupStrings.MODAL_RESTORE_FAILED_TITLE,
                _SystemCleanupStrings.MODAL_RESTORE_FAILED_MSG,
                ["OK"],
                self,
            ).exec_()

    # ------------------------------------------------------------------
    # ComponentGuardian protocol (GRD)
    # ------------------------------------------------------------------

    def health_check(self) -> bool:
        """Verify that this widget is fully operational.

        Called by ComponentGuardian to determine whether the component is
        healthy. Returns ``True`` when all required resources are initialised
        and no fatal internal error state is set; returns ``False`` on any
        failure so the guardian can trigger :meth:`degraded_fallback`.
        """
        try:
            if not PYQT5_AVAILABLE:
                return False
            # Confirm the UI skeleton was built (tab_widget populated)
            if not hasattr(self, "tab_widget") or self.tab_widget is None:
                return False
            if self.tab_widget.count() == 0:
                return False
            # Confirm at least one backend cleanup tool is available
            if not self.cleanup_tools:
                return False
            return True
        except Exception:
            return False

    def degraded_fallback(self) -> None:
        """Put this widget into degraded mode when a required
        resource is unavailable.

        Keeps the widget visible and disables only the functionality that
        requires the unavailable resource. Shows an inline degraded-mode
        notice to the user.

        Disabled capabilities and rationale:

        - ``quick_cleanup_button`` — requires at least one cleanup tool to be
          initialised (``self.cleanup_tools`` non-empty).
        - ``estimate_button`` — requires ``TempFilesCleaner`` to scan
          temp dirs.
        - ``preview_button`` — same dependency as ``estimate_button``.
        - ``execute_button`` — requires a cleanup tool and safety manager.
        - ``stop_cleanup_button`` — no active operation can be running if tools
          are unavailable; disabled for consistency.

        Root cause: ``CLEANUP_TOOLS_AVAILABLE`` is ``False`` or
        :meth:`health_check` returned ``False`` (``cleanup_tools`` dict empty).

        See also: ``docs/ui-ux-harmonization/system_cleanup/DEGRADED_MODE.md``
        """
        # GRD-3b-i: keep widget visible
        self.setVisible(True)

        # GRD-3b-ii: disable only the functionality that requires cleanup tools
        for _btn_name in (
            "quick_cleanup_button",
            "estimate_button",
            "preview_button",
            "execute_button",
            "stop_cleanup_button",
        ):
            _btn = getattr(self, _btn_name, None)
            if _btn is not None:
                _btn.setEnabled(False)

        # GRD-3b-iii: show inline degraded-mode notice
        _notice = (
            "Degraded mode — cleanup tools unavailable. "
            "Some features have been disabled."
        )
        if (
            hasattr(self, "cleanup_status_label")
            and self.cleanup_status_label is not None
        ):
            self.cleanup_status_label.setText(_notice)
        elif hasattr(self, "status_label") and self.status_label is not None:
            self.status_label.setText(_notice)
        elif self._toast is not None:
            self._toast.show_message(_notice)
