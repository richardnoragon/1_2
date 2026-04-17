#!/usr/bin/env python3
"""
Size Analyzer Tool for Richard's File Utilities

A streamlined size analyzer utility with essential functionality.
"""

import logging
import sys

try:
    from PyQt5.QtWidgets import (
        QApplication,
        QFileDialog,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QListWidget,
        QMainWindow,
        QMessageBox,
        QPushButton,
        QVBoxLayout,
        QWidget,
    )

    from src.gui.themes import ThemeManager, token
except ImportError:
    print("PyQt5 not available. Please install PyQt5.")
    sys.exit(1)

try:
    from .size_analyzer_logic import SizeAnalyzer, SizeAnalyzerWorker
except ImportError:  # Allow running as standalone script
    from src.tools.analysis.size_analyzer.size_analyzer_logic import (
        SizeAnalyzer,
        SizeAnalyzerWorker,
    )

try:
    from ....log_manager import get_log_manager

    LOG_MANAGER_AVAILABLE = True
except ImportError:
    try:
        from src.log_manager import get_log_manager

        LOG_MANAGER_AVAILABLE = True
    except ImportError:
        get_log_manager = None
        LOG_MANAGER_AVAILABLE = False

SIZE_ANALYZER_LABEL = "Size Analyzer"

# Import SafeStandardWindow for reliable menu integration
try:
    # Add the correct path for imports
    from ....gui.safe_standard_window import (
        SafeStandardWindow as StandardWindow,
    )

    STANDARD_WINDOW_AVAILABLE = True
except ImportError:
    try:
        from src.gui.safe_standard_window import (
            SafeStandardWindow as StandardWindow,
        )

        STANDARD_WINDOW_AVAILABLE = True
    except ImportError as safe_error:
        print(f"SafeStandardWindow not available: {safe_error}")
        # Try original StandardWindow as fallback
        try:
            from ....gui.standard_window import StandardWindow

            STANDARD_WINDOW_AVAILABLE = True
        except ImportError:
            try:
                from src.gui.standard_window import StandardWindow

                STANDARD_WINDOW_AVAILABLE = True
            except ImportError:
                # Final fallback - minimal implementation
                class StandardWindow(QMainWindow):
                    def __init__(
                        self,
                        title="Window",
                        window_type="utility",
                        parent=None,
                    ):
                        super().__init__(parent)
                        self.setWindowTitle(title)
                        self.window_type = window_type

                    def ensure_menu_bar(self):
                        """Safe no-op when full menu system is unavailable."""
                        return None

                STANDARD_WINDOW_AVAILABLE = False


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
    from src.rfu.ui_strings import SizeAnalyzer as _SizeAnalyzerStrings
except ImportError:

    class _SizeAnalyzerStrings:  # type: ignore[no-redef]
        TITLE = "Size Analyzer"
        WINDOW_TITLE = "Size Analyzer — RFU"
        LOADING = "Loading Size Analyzer…"
        MODAL_ERROR_TITLE = "Size Analyzer"
        ERR_INIT_FAILED = (
            "Could not start Size Analyzer. "
            "Please try again or restart the application."
        )
        ERR_ANALYSIS_FAILED = "Could not analyze directory. Please try again."
        ERR_FILTER_INVALID = (
            "Invalid name filter. "
            "Please enter a valid file name pattern or leave the filter empty."
        )
        ERR_EXPORT_FAILED = (
            "Could not export analysis results. "
            "Check that you have write permission to the chosen location."
        )


# ---------------------------------------------------------------------------
# ERR: Modal helper (graceful no-op when modal absent)
# ---------------------------------------------------------------------------
try:
    from src.gui.components.buttons import PrimaryButton, SecondaryButton
    from src.gui.components.loading_indicator import LoadingIndicator
    from src.gui.components.modal import Modal
    from src.gui.components.toast import ToastNotification

    _CP_AVAILABLE = True
except ImportError:
    Modal = None  # type: ignore[assignment,misc]
    PrimaryButton = QPushButton
    SecondaryButton = QPushButton
    LoadingIndicator = None
    ToastNotification = None
    _CP_AVAILABLE = False


class SizeAnalyzerGUI(StandardWindow):
    """Main window for Size Analyzer operations."""

    def __init__(self, hub_instance=None, parent=None):
        # Always use the safe constructor parameters
        super().__init__(
            title=_SizeAnalyzerStrings.WINDOW_TITLE,
            window_type="utility",
            parent=parent,
        )
        self._hub = hub_instance
        self.setGeometry(100, 100, 800, 600)

        self.logger = self._init_logger()
        self._logger = self.logger  # harmonization alias
        self.analysis_results = {}
        self.analyzer = SizeAnalyzer()
        self.analyzer.operation_cancelled.connect(self._handle_analysis_cancelled)
        self.worker_thread: SizeAnalyzerWorker | None = None
        self._last_selected_path: str | None = None
        self._worker_signals_connected = False
        self._worker_signal_pairs = []
        self.init_ui()
        if STANDARD_WINDOW_AVAILABLE:
            self._setup_menu_callbacks()
        # Ensure menu bar exists (safe to call in both modes)
        self.ensure_menu_bar()
        register_gui_component(
            self, tool_id="size_analyzer", recovery_callback=self.degraded_fallback
        )
        _emit_telemetry("ui_view_load", tool_id="size_analyzer")
        ThemeManager.add_theme_changed_callback(self._on_theme_changed)

    def _on_theme_changed(self, variant: str) -> None:
        """Re-apply token-based stylesheets when the active theme variant changes."""
        pass  # stylesheets applied at init; live re-apply pending TH-4c/4d

    def health_check(self) -> bool:
        """Return True if core UI is functional (GRD-3a)."""
        try:
            return hasattr(self, "results_list") and self.results_list is not None
        except Exception:
            return False

    def degraded_fallback(self) -> None:
        """Enter degraded / read-only state (GRD-3b)."""
        try:
            self._logger.warning("SizeAnalyzerGUI entering degraded mode")
        except Exception:
            pass
        _emit_telemetry(
            "ui_error_event", tool_id="size_analyzer", error_type="degraded"
        )

    def _setup_menu_callbacks(self):
        """Setup tool-specific menu callbacks."""
        if hasattr(self, "menu_manager"):
            # Register tool-specific callbacks
            self.menu_manager.register_callback(
                "new_analysis",
                self.clear_analysis,
            )
            # Override the standard help with our tool-specific help
            self.menu_manager.register_callback(
                "show_user_guide",
                self.show_help,
            )
            self.menu_manager.register_callback(
                "show_preferences", self.show_preferences
            )
            self.menu_manager.register_callback("refresh", self.refresh_view)

    def clear_analysis(self):
        """Clear all size analysis results."""
        self.analysis_results = {}
        if hasattr(self, "results_list"):
            self.results_list.clear()

    def show_help(self):
        """Show help dialog for Size Analyzer tool."""
        help_text = """
        <h2>Size Analyzer - Help</h2>
        
        <h3>How to Analyze Directory Sizes:</h3>
        <ul>
        <li><b>Select Directory:</b> Choose the folder to analyze</li>
        <li><b>Start Analysis:</b> Begin scanning directories & files</li>
        <li><b>View Results:</b> Review folder/file size breakdown</li>
        <li><b>Export Data:</b> Save analysis results to file</li>
        </ul>
        
        <h3>Analysis Features:</h3>
        <ul>
        <li><b>Directory Tree:</b> Hierarchical view of folder sizes</li>
        <li><b>File Breakdown:</b> Individual file size listings</li>
        <li><b>Size Sorting:</b> Results sorted by size (largest first)</li>
        <li><b>Progress Tracking:</b> Real-time analysis progress</li>
        <li><b>Name Range Filter:</b> Limit scans to names between
        two values</li>
        </ul>
        
        <h3>Size Information:</h3>
        <ul>
        <li><b>Bytes Display:</b> Precise file sizes in bytes</li>
        <li><b>Human Readable:</b> Sizes shown in KB, MB, GB format</li>
        <li><b>Percentage View:</b> Relative size percentages</li>
        <li><b>File Count:</b> Number of files in each directory</li>
        </ul>
        
        <h3>Use Cases:</h3>
        <ul>
        <li><b>Disk Cleanup:</b> Find largest files consuming space</li>
        <li><b>Storage Planning:</b> Understand disk usage patterns</li>
        <li><b>Archive Planning:</b> Identify candidates for archival</li>
        <li><b>System Optimization:</b> Locate space-wasting files</li>
        </ul>
        
        <h3>Best Practices:</h3>
        <ul>
        <li><b>Regular Analysis:</b> Regular checks prevent space issues</li>
        <li><b>Focus on Large Files:</b> Target the biggest space users</li>
        <li><b>Archive Old Data:</b> Archive unused large files externally</li>
        <li><b>Monitor Growth:</b> Track how directories grow over time</li>
        </ul>
        
        <h3>Keyboard Shortcuts:</h3>
        <ul>
        <li><b>Ctrl+Q:</b> Exit application</li>
        <li><b>F1:</b> Show this help</li>
        <li><b>F5:</b> Clear analysis and start new scan</li>
        </ul>
        """

        if Modal:
            Modal("Size Analyzer Help", help_text, ["OK"], parent=self).exec_()
        else:
            QMessageBox.information(self, "Size Analyzer Help", help_text)

    def show_preferences(self):
        """Show Size Analyzer preferences."""
        _msg = (
            "Size Analyzer preferences:\n\n"
            "• Analysis depth limits\n"
            "• File type filters\n"
            "• Size display units\n"
            "• Sort and grouping options\n\n"
            "Advanced preferences coming soon!"
        )
        if Modal:
            Modal("Size Analyzer Preferences", _msg, ["OK"], parent=self).exec_()
        else:
            QMessageBox.information(self, "Size Analyzer Preferences", _msg)

    def refresh_view(self):
        """Refresh/clear the current analysis results."""
        self.clear_analysis()

    def init_ui(self):
        """Initialize the user interface."""
        # Use the existing main layout from StandardWindow or create new layout
        if STANDARD_WINDOW_AVAILABLE and hasattr(self, "main_layout"):
            layout = self.main_layout
        else:
            # Create central widget and layout for fallback mode
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)

        # Add header
        header_label = QLabel(SIZE_ANALYZER_LABEL)
        header_label.setStyleSheet(
            """
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: {token('text_primary')};
                padding: 10px;
                background-color: {token('background')};
                border-radius: 5px;
                margin-bottom: 10px;
            }
        """
        )
        layout.addWidget(header_label)

        # Add analysis area
        analysis_group = QGroupBox("Analysis Results")
        analysis_layout = QVBoxLayout(analysis_group)

        self.results_list = QListWidget()
        self.results_list.setAccessibleName("Analysis results")
        analysis_layout.addWidget(self.results_list)

        self.status_label = QLabel("Idle")
        self.status_label.setStyleSheet(
            f"color: {token('text_primary')}; padding: 4px 0;"
        )
        analysis_layout.addWidget(self.status_label)

        filter_group = QGroupBox("File Name Range Filter (Optional)")
        filter_layout = QHBoxLayout()
        filter_group.setLayout(filter_layout)

        start_label = QLabel("Start:")
        self.start_range_input = QLineEdit()
        self.start_range_input.setAccessibleName("Start of range")
        self.start_range_input.setPlaceholderText("e.g., A or 100")

        end_label = QLabel("End:")
        self.end_range_input = QLineEdit()
        self.end_range_input.setAccessibleName("End of range")
        self.end_range_input.setPlaceholderText("e.g., D or 399")

        for widget in (
            start_label,
            self.start_range_input,
            end_label,
            self.end_range_input,
        ):
            filter_layout.addWidget(widget)

        analysis_layout.addWidget(filter_group)

        self.analyze_button = PrimaryButton("Start Analysis")
        self.analyze_button.clicked.connect(self.start_analysis)
        analysis_layout.addWidget(self.analyze_button)

        self.cancel_button = SecondaryButton("Stop Analysis")
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self.stop_analysis)
        analysis_layout.addWidget(self.cancel_button)

        layout.addWidget(analysis_group)
        content_label = QLabel(
            "Use Start Analysis to scan a directory. Results appear above."
        )
        content_label.setStyleSheet(f"padding: 20px; color: {token('text_muted')};")
        layout.addWidget(content_label)

        # Loading indicator for background analysis (CP-6)
        if LoadingIndicator:
            self._loading = LoadingIndicator(
                parent=self, cancellable=True, message="Analyzing…"
            )
            self._loading.cancelled.connect(self.stop_analysis)
            layout.addWidget(self._loading)
        else:
            self._loading = None

        # Add action button
        self.action_button = SecondaryButton("Execute Action")
        self.action_button.clicked.connect(self.execute_action)
        layout.addWidget(self.action_button)

    def start_analysis(self):
        """Start the analysis process."""
        if self.worker_thread and self.worker_thread.isRunning():
            warning_text = (
                "An analysis is already running. Please wait for it to finish."
            )
            if Modal:
                Modal(SIZE_ANALYZER_LABEL, warning_text, ["OK"], parent=self).exec_()
            else:
                QMessageBox.warning(self, SIZE_ANALYZER_LABEL, warning_text)
            return

        if self._worker_signals_connected:
            if self.logger:
                self.logger.warning(
                    "Worker signals still connected from previous run;"
                    " disconnecting before restarting"
                )
            self._disconnect_worker_signals()

        try:
            start_value, end_value = self._get_name_range_filters()
        except (
            ValueError
        ) as error:  # ERR: non-fatal — surfaced via Modal; invalid filter input
            self.logger.error(f"Invalid name range filter: {error}", exc_info=True)
            if Modal:
                Modal(
                    _SizeAnalyzerStrings.MODAL_ERROR_TITLE,
                    _SizeAnalyzerStrings.ERR_FILTER_INVALID,
                    ["OK"],
                    self,
                ).exec_()
            return

        name_range = None
        if start_value or end_value:
            name_range = (start_value, end_value)

        self.results_list.clear()
        target_path = self._prompt_drive_selection()
        if not target_path:
            self.results_list.addItem("Analysis cancelled: no drive selected")
            return

        self.status_label.setText("Preparing analysis...")
        self.results_list.addItem(f"Analyzing: {target_path}")
        if name_range:
            self.results_list.addItem(self._describe_name_range())

        self.worker_thread = SizeAnalyzerWorker(
            self.analyzer,
            target_path,
            top_files_count=10,
            name_range=name_range,
        )
        self._connect_worker_signals()
        self.worker_thread.finished.connect(self._cleanup_worker)

        self._set_analysis_running(True)
        if self.logger:
            self.logger.info(
                "Worker %s launched for %s (range=%s)",
                id(self.worker_thread),
                target_path,
                name_range,
            )
        self.worker_thread.start()

    def stop_analysis(self):
        """Allow the user to cancel the running analysis."""
        if not self.worker_thread or not self.worker_thread.isRunning():
            if Modal:
                Modal(
                    SIZE_ANALYZER_LABEL,
                    "No analysis is currently running.",
                    ["OK"],
                    parent=self,
                ).exec_()
            else:
                QMessageBox.information(
                    self,
                    SIZE_ANALYZER_LABEL,
                    "No analysis is currently running.",
                )
            return

        self.status_label.setText("Cancelling analysis...")
        if self.logger:
            self.logger.info(
                "Cancellation requested for worker %s", id(self.worker_thread)
            )
        self.worker_thread.cancel()

    def execute_action(self):
        """Main action method for this tool."""
        if not self.analysis_results:
            if Modal:
                Modal(
                    SIZE_ANALYZER_LABEL,
                    "Run an analysis before exporting results.",
                    ["OK"],
                    parent=self,
                ).exec_()
            else:
                QMessageBox.information(
                    self,
                    SIZE_ANALYZER_LABEL,
                    "Run an analysis before exporting results.",
                )
            return

        export_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Analysis Results",
            "size_analysis.json",
            "JSON Files (*.json)",
        )

        if not export_path:
            return

        try:
            self.analyzer.export_analysis(
                self.analysis_results,
                export_path,
            )
            if ToastNotification:
                ToastNotification(parent=self).show_message(
                    f"Exported to {export_path}", "success"
                )
            else:
                QMessageBox.information(
                    self,
                    SIZE_ANALYZER_LABEL,
                    f"Analysis results exported to:\n{export_path}",
                )
        except OSError as exc:  # ERR: non-fatal — surfaced via Modal
            self.logger.error(f"Error exporting analysis results: {exc}", exc_info=True)
            if Modal:
                Modal(
                    _SizeAnalyzerStrings.MODAL_ERROR_TITLE,
                    _SizeAnalyzerStrings.ERR_EXPORT_FAILED,
                    ["OK"],
                    self,
                ).exec_()

    def _prompt_drive_selection(self) -> str | None:
        """Show a directory picker so the user can choose the drive/folder."""

        caption = "Select drive or folder to analyze"
        dialog_options = QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        selected = QFileDialog.getExistingDirectory(
            self,
            caption,
            self._last_selected_path or "C:/",
            options=dialog_options,
        )
        if selected:
            self._last_selected_path = selected
            return selected
        return None

    def _get_name_range_filters(self) -> tuple[str | None, str | None]:
        """Return normalized start/end tokens for name filtering."""
        if not hasattr(self, "start_range_input"):
            return None, None

        start_raw = self.start_range_input.text().strip()
        end_raw = self.end_range_input.text().strip()

        start_value = start_raw.lower() or None
        end_value = end_raw.lower() or None

        if start_value and end_value and start_value > end_value:
            raise ValueError(
                "Start value must alphabetically or numerically precede "
                "the end value."
            )

        return start_value, end_value

    def _describe_name_range(self) -> str:
        """Generate a user-facing description of the active name range."""
        start_raw = self.start_range_input.text().strip()
        end_raw = self.end_range_input.text().strip()

        if start_raw and end_raw:
            return f"Name range: '{start_raw}' through '{end_raw}'"
        if start_raw:
            return f"Name range: from '{start_raw}' onward"
        return f"Name range: up to '{end_raw}'"

    def _handle_progress_update(self, percentage: int) -> None:
        """Update UI with progress information."""
        if self.logger and percentage % 25 == 0:
            self.logger.debug("Progress update: %s%%", percentage)
        self.status_label.setText(f"Progress: {percentage}%")
        if percentage == 100:
            self.status_label.setText("Finalizing results...")

    def _handle_status_update(self, message: str) -> None:
        """Display status text so users know what phase is running."""
        if self.logger:
            self.logger.debug("Status update: %s", message)
        self.status_label.setText(message)

    def _handle_analysis_finished(self, analysis: dict) -> None:
        """Render analysis results when the worker finishes."""
        self.analysis_results = analysis or {}
        self.results_list.clear()

        if not analysis:
            self.results_list.addItem("No results returned from analysis.")
        else:
            total_size = self.analyzer.format_size(analysis.get("total_size", 0))
            directory_label = f"Directory: {analysis.get('path', 'Unknown')}"
            self.results_list.addItem(directory_label)
            self.results_list.addItem(f"Total Size: {total_size}")
            summary_line = (
                f"Files: {analysis.get('file_count', 0)} | "
                f"Folders: {analysis.get('directory_count', 0)}"
            )
            self.results_list.addItem(summary_line)

            largest_files = analysis.get("largest_files", [])
            if largest_files:
                self.results_list.addItem("Largest Files:")
                for file_info in largest_files[:5]:
                    size_label = self.analyzer.format_size(file_info.get("size", 0))
                    self.results_list.addItem(
                        f"  {file_info.get('name', 'Unknown')} - {size_label}"
                    )

        self.status_label.setText("Analysis complete.")
        self._set_analysis_running(False)
        if ToastNotification:
            ToastNotification(parent=self).show_message("Analysis complete", "success")
        if self.logger:
            self.logger.info(
                "Analysis finished: files=%s total_bytes=%s",
                analysis.get("file_count", 0),
                analysis.get("total_size", 0),
            )

    def _handle_analysis_error(self, error_message: str) -> None:
        """Show errors and restore UI state."""
        self.status_label.setText("Analysis failed.")
        self.results_list.addItem(error_message)
        if Modal:
            Modal(SIZE_ANALYZER_LABEL, error_message, ["OK"], parent=self).exec_()
        else:
            QMessageBox.critical(self, SIZE_ANALYZER_LABEL, error_message)
        self._set_analysis_running(False)
        if self.logger:
            self.logger.error("Analysis error: %s", error_message)

    def _cleanup_worker(self) -> None:
        """Disconnect worker signals and release the thread."""
        if self.logger:
            self.logger.debug(
                "Cleanup triggered for worker %s",
                id(self.worker_thread) if self.worker_thread else None,
            )
        self._disconnect_worker_signals()
        if self.worker_thread:
            try:
                self.worker_thread.deleteLater()
            except (
                RuntimeError,
                TypeError,
            ) as error:  # ERR: non-fatal — worker deletion failed; GC will clean up
                if self.logger:
                    self.logger.warning("Failed to schedule worker deletion: %s", error)
        self.worker_thread = None
        if self.logger:
            self.logger.debug("Worker cleanup complete")

    def _handle_analysis_cancelled(self) -> None:
        """Handle cancellation notifications from the analyzer."""
        self.results_list.addItem("Analysis cancelled by user.")
        self.status_label.setText("Analysis cancelled.")
        self._set_analysis_running(False)
        if self.logger:
            self.logger.info("Analysis cancelled by user")

    def _set_analysis_running(self, running: bool) -> None:
        """Toggle button availability based on analysis state."""
        if hasattr(self, "analyze_button"):
            self.analyze_button.setEnabled(not running)
        if hasattr(self, "action_button"):
            self.action_button.setEnabled(not running)
        if hasattr(self, "cancel_button"):
            self.cancel_button.setEnabled(running)
        if hasattr(self, "start_range_input"):
            self.start_range_input.setEnabled(not running)
        if hasattr(self, "end_range_input"):
            self.end_range_input.setEnabled(not running)
        if hasattr(self, "_loading") and self._loading:
            if running:
                self._loading.start()
            else:
                self._loading.stop()
        if self.logger:
            self.logger.debug("UI state updated (running=%s)", running)

    def _connect_worker_signals(self) -> None:
        """Connect worker signals while tracking for cleanup."""
        if not self.worker_thread:
            return

        connections = [
            (self.worker_thread.progress_update, self._handle_progress_update),
            (self.worker_thread.status_update, self._handle_status_update),
            (
                self.worker_thread.analysis_finished,
                self._handle_analysis_finished,
            ),
            (self.worker_thread.analysis_error, self._handle_analysis_error),
        ]

        for signal, slot in connections:
            signal.connect(slot)

        self._worker_signal_pairs = connections
        self._worker_signals_connected = True
        if self.logger:
            self.logger.debug(
                "Connected worker signals (worker_id=%s)",
                id(self.worker_thread),
            )

    def _disconnect_worker_signals(self) -> None:
        """Disconnect worker signals to avoid duplicate connections."""
        if not self._worker_signals_connected:
            return

        for signal, slot in self._worker_signal_pairs:
            try:
                signal.disconnect(slot)
            except (
                TypeError,
                RuntimeError,
            ):  # ERR: non-fatal — stale signal disconnect; loop continues
                continue

        self._worker_signal_pairs = []
        self._worker_signals_connected = False
        if self.logger:
            self.logger.debug("Worker signals disconnected")

    def _init_logger(self):
        """Initialize a logger instance for diagnostics."""
        try:
            if LOG_MANAGER_AVAILABLE and get_log_manager:
                return get_log_manager().get_logger("SizeAnalyzerGUI")
        except (AttributeError, RuntimeError, ImportError) as error:
            logging.getLogger("SizeAnalyzerGUI").debug(
                "Falling back to root logger due to: %s", error
            )

        return logging.getLogger("SizeAnalyzerGUI")


def main():
    """Main function for standalone execution."""
    app = QApplication(sys.argv)
    window = SizeAnalyzerGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
