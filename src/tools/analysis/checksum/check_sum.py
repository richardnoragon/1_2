#!/usr/bin/env python3
"""
Simple Checksum GUI for Richard's File Utilities
"""

import hashlib
import logging
import os
import sys

from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication,
    QFileDialog,
    QGroupBox,
    QLabel,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from src.gui.themes import ThemeManager, token

try:
    from src.gui.components.buttons import PrimaryButton, SecondaryButton
    from src.gui.components.loading_indicator import LoadingIndicator
    from src.gui.components.modal import Modal

    _COMPONENTS_AVAILABLE = True
except ImportError:
    from PyQt5.QtWidgets import QPushButton as PrimaryButton
    from PyQt5.QtWidgets import QPushButton as SecondaryButton

    LoadingIndicator = None
    Modal = None
    _COMPONENTS_AVAILABLE = False

# Import SafeStandardWindow for reliable menu integration
try:
    from src.gui.safe_standard_window import (
        SafeStandardWindow as StandardWindow,
    )

    STANDARD_WINDOW_AVAILABLE = True
except ImportError as safe_window_error:
    print(f"SafeStandardWindow not available: {safe_window_error}")
    try:
        from src.gui.standard_window import StandardWindow

        STANDARD_WINDOW_AVAILABLE = True
    except ImportError:

        class StandardWindow(QMainWindow):
            """Fallback window with minimal functionality."""

            def __init__(
                self,
                title="Window",
                window_type="utility",
                parent=None,
            ):
                super().__init__(parent)
                self.setWindowTitle(title)

            def ensure_menu_bar(self):
                # Menu bar not available in fallback mode
                pass

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
    from src.rfu.ui_strings import Checksum as _ChecksumStrings
except ImportError:

    class _ChecksumStrings:  # type: ignore[no-redef]
        TITLE = "Checksum Calculator"
        WINDOW_TITLE = "Checksum Calculator — RFU"
        LOADING = "Loading Checksum Calculator…"
        ERR_INIT_FAILED = (
            "Could not start Checksum Calculator. "
            "Please try again or restart the application."
        )
        ERR_CALCULATE_FAILED = (
            "Checksum calculation failed. "
            "Check that the file is accessible and try again."
        )


class ChecksumWorker(QObject):
    """Compute an MD5 checksum in a background thread (PERF-1d)."""

    finished = pyqtSignal(str)  # emits "MD5: <hex>"
    error = pyqtSignal(str)  # emits error message

    def __init__(self, file_path: str) -> None:
        super().__init__()
        self._file_path = file_path

    def run(self) -> None:
        """Hash the file and emit finished or error."""
        try:
            md5_hash = hashlib.md5()
            with open(self._file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    md5_hash.update(chunk)
            self.finished.emit(f"MD5: {md5_hash.hexdigest()}")
        except Exception as e:
            self.error.emit(str(e))


class ChecksumGUI(StandardWindow):
    """Simple Checksum Calculator GUI."""

    def __init__(self, hub_instance=None, parent=None):
        # Always use the safe constructor parameters
        super().__init__(
            title=_ChecksumStrings.WINDOW_TITLE,
            window_type="utility",
            parent=parent,
        )
        self._hub = hub_instance
        try:
            from src.rfu.log_manager import get_log_manager

            self._logger = get_log_manager().get_logger("ChecksumGUI")
        except Exception:
            self._logger = logging.getLogger("ChecksumGUI")
        self.setGeometry(100, 100, 800, 600)

        self._worker: ChecksumWorker | None = None
        self._thread: QThread | None = None

        self.init_ui()
        if STANDARD_WINDOW_AVAILABLE:
            self._setup_menu_callbacks()
        # Ensure menu bar exists (safe to call in both modes)
        self.ensure_menu_bar()
        register_gui_component(
            self, tool_id="checksum", recovery_callback=self.degraded_fallback
        )
        _emit_telemetry("ui_view_load", tool_id="checksum")
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
            self._logger.warning("ChecksumGUI entering degraded mode")
        except Exception:
            pass
        _emit_telemetry("ui_error_event", tool_id="checksum", error_type="degraded")

    def _setup_menu_callbacks(self):
        """Setup tool-specific menu callbacks."""
        if hasattr(self, "menu_manager"):
            # Register tool-specific callbacks
            self.menu_manager.register_callback("new_checksum", self.clear_results)
            # Override the standard help with our tool-specific help
            self.menu_manager.register_callback("show_user_guide", self.show_help)
            self.menu_manager.register_callback(
                "show_preferences", self.show_preferences
            )
            self.menu_manager.register_callback("refresh", self.refresh_view)

    def clear_results(self):
        """Clear all checksum calculation results."""
        if hasattr(self, "results_list"):
            self.results_list.clear()

    def show_help(self):
        """Show help dialog for Checksum Calculator tool."""
        help_text = """
        <h2>File Checksum Calculator - Help</h2>
        
        <h3>How to Calculate Checksums:</h3>
        <ul>
        <li><b>Select Files:</b> Choose one or more files to calculate
            checksums</li>
        <li><b>Choose Algorithm:</b> Pick MD5, SHA1, or SHA256 algorithm</li>
        <li><b>Calculate:</b> Click to generate checksums for selected files</li>
        <li><b>Copy Results:</b> Copy checksums to clipboard for
            verification</li>
        </ul>
        
        <h3>Checksum Algorithms:</h3>
        <ul>
        <li><b>MD5:</b> Fast, 128-bit hash (legacy, less secure)</li>
        <li><b>SHA1:</b> 160-bit hash (deprecated for security)</li>
        <li><b>SHA256:</b> Secure 256-bit hash (recommended)</li>
        <li><b>SHA512:</b> Most secure 512-bit hash (slower but strongest)</li>
        </ul>
        
        <h3>Use Cases:</h3>
        <ul>
        <li><b>File Integrity:</b> Verify files haven't been corrupted</li>
        <li><b>Download Verification:</b> Confirm downloaded files are
            intact</li>
        <li><b>Change Detection:</b> Detect if files have been modified</li>
        <li><b>Duplicate Detection:</b> Compare checksums to find
            duplicates</li>
        </ul>
        
        <h3>Best Practices:</h3>
        <ul>
        <li><b>Use SHA256:</b> Most balanced option for security and speed</li>
        <li><b>Save Results:</b> Keep checksum records for later
            verification</li>
        <li><b>Batch Processing:</b> Calculate multiple files at once</li>
        <li><b>Regular Checks:</b> Verify important files periodically</li>
        </ul>
        
        <h3>Keyboard Shortcuts:</h3>
        <ul>
        <li><b>Ctrl+Q:</b> Exit application</li>
        <li><b>F1:</b> Show this help</li>
        <li><b>F5:</b> Clear results and start new calculation</li>
        </ul>
        """

        if Modal:
            Modal("Checksum Calculator Help", help_text, parent=self).exec_()
        else:
            QMessageBox.information(self, "Checksum Calculator Help", help_text)

    def show_preferences(self):
        """Show Checksum Calculator preferences."""
        if Modal:
            Modal(
                "Checksum Calculator Preferences",
                "Checksum Calculator preferences:\n\n"
                "• Default checksum algorithm\n"
                "• Output format options\n"
                "• Progress display settings\n"
                "• Auto-save results location\n\n"
                "Advanced preferences coming soon!",
                parent=self,
            ).exec_()
        else:
            QMessageBox.information(
                self,
                "Checksum Calculator Preferences",
                "Checksum Calculator preferences:\n\n"
                "• Default checksum algorithm\n"
                "• Output format options\n"
                "• Progress display settings\n"
                "• Auto-save results location\n\n"
                "Advanced preferences coming soon!",
            )

    def refresh_view(self):
        """Refresh/clear the current calculation results."""
        self.clear_results()

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
        header_label = QLabel("File Checksum Calculator")
        header_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: 18px;
                font-weight: bold;
                color: {token('text_primary')};
                padding: 10px;
                background-color: {token('background')};
                border-radius: 5px;
                margin-bottom: 10px;
            }}
        """
        )
        layout.addWidget(header_label)

        # File selection
        file_group = QGroupBox("File Selection")
        file_layout = QVBoxLayout(file_group)

        select_button = SecondaryButton("Select File")
        select_button.clicked.connect(self.select_file)
        file_layout.addWidget(select_button)

        self.file_label = QLabel("No file selected")
        file_layout.addWidget(self.file_label)

        layout.addWidget(file_group)

        # Calculate button
        calc_button = PrimaryButton("Calculate MD5 Checksum")
        calc_button.clicked.connect(self.calculate_checksum)
        layout.addWidget(calc_button)

        # Results
        self.results_list = QListWidget()
        self.results_list.setAccessibleName("Checksum results")
        layout.addWidget(self.results_list)

        # Loading indicator (PERF-3a/3b)
        if LoadingIndicator:
            self._loading_indicator = LoadingIndicator(
                parent=self, message="Calculating checksum…"
            )
            layout.addWidget(self._loading_indicator)
        else:
            self._loading_indicator = None

        self.selected_file = None

    def select_file(self):
        """Select a file for checksum calculation."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File", "", "All Files (*.*)"
        )
        if file_path:
            self.selected_file = file_path
            self.file_label.setText(f"Selected: {os.path.basename(file_path)}")

    def calculate_checksum(self):
        """Start MD5 checksum calculation in a background thread (PERF-1d)."""
        if not self.selected_file:
            if Modal:
                Modal("Warning", "Please select a file first.", parent=self).exec_()
            else:
                QMessageBox.warning(self, "Warning", "Please select a file first.")
            return

        if self._thread and self._thread.isRunning():
            return  # already running

        # PERF-3a: start indicator before worker
        if self._loading_indicator:
            self._loading_indicator.start()

        self._worker = ChecksumWorker(self.selected_file)
        self._thread = QThread()
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.finished.connect(self._on_checksum_done)
        self._worker.error.connect(self._on_checksum_error)
        # PERF-4a: stop indicator on normal completion
        self._worker.finished.connect(self._stop_indicator)
        # PERF-4b: stop indicator on error path
        self._worker.error.connect(self._stop_indicator)
        self._thread.start()

    def _stop_indicator(self) -> None:
        """Stop the loading indicator and clean up the thread."""
        if self._loading_indicator:
            self._loading_indicator.stop()
        if self._thread:
            self._thread.quit()
            self._thread = None
        self._worker = None

    def _on_checksum_done(self, result: str) -> None:
        """Display the computed checksum."""
        self.results_list.addItem(result)

    def _on_checksum_error(self, message: str) -> None:  # ERR: non-fatal
        """Surface a checksum error via Modal."""
        self._logger.error(f"Checksum error for '{self.selected_file}': {message}")
        if Modal:
            Modal("Error", _ChecksumStrings.ERR_CALCULATE_FAILED, ["OK"], self).exec_()


def main():
    """Main function for standalone execution."""
    app = QApplication(sys.argv)
    window = ChecksumGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
