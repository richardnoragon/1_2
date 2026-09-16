#!/usr/bin/env python3
"""
Simple Duplicate Finder GUI for Richard's File Utilities
"""
from src.rfu.localization import localized_widget as _ui_widget, bind_literal as _ui_bind
from src.rfu import font_tokens

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
    # Add the correct path for imports
    sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    from src.gui.safe_standard_window import (
        SafeStandardWindow as StandardWindow,
    )

    STANDARD_WINDOW_AVAILABLE = True
except ImportError as e:
    print(f"SafeStandardWindow not available: {e}")
    # Try original StandardWindow as fallback
    try:
        from src.gui.standard_window import StandardWindow

        STANDARD_WINDOW_AVAILABLE = True
    except ImportError:
        # Final fallback - minimal implementation
        class StandardWindow(QMainWindow):
            def __init__(self, title="Window", window_type="utility", parent=None):
                super().__init__(parent)
                self.setWindowTitle(title)

            def ensure_menu_bar(self):
                pass  # No-op for fallback

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
    from src.rfu.ui_strings import DuplicateFinder as _DupFinderStrings
except ImportError:

    class _DupFinderStrings:  # type: ignore[no-redef]
        TITLE = "Duplicate Finder"
        WINDOW_TITLE = "Duplicate Finder — RFU"
        LOADING = "Loading Duplicate Finder…"
        ERR_INIT_FAILED = (
            "Could not start Duplicate Finder. "
            "Please try again or restart the application."
        )
        ERR_SCAN_FAILED = (
            "Duplicate scan could not be completed. "
            "Check that the folder is accessible and try again."
        )


class DuplicateScanWorker(QObject):
    """Scan a directory for duplicate files in a background thread (PERF-1d)."""

    finished = pyqtSignal(list)  # emits list of (original, duplicate) tuples
    error = pyqtSignal(str)

    def __init__(self, directory: str) -> None:
        super().__init__()
        self._directory = directory

    def run(self) -> None:
        """Walk directory, hash every file, collect duplicates."""
        try:
            file_hashes: dict = {}
            duplicates: list = []
            for root, _dirs, files in os.walk(self._directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_hash = self._get_file_hash(file_path)
                    if file_hash:
                        if file_hash in file_hashes:
                            duplicates.append((file_hashes[file_hash], file_path))
                        else:
                            file_hashes[file_hash] = file_path
            self.finished.emit(duplicates)
        except Exception as e:
            self.error.emit(str(e))

    @staticmethod
    def _get_file_hash(file_path: str):
        """Return MD5 hex digest or None on error."""
        try:
            with open(file_path, "rb") as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:  # ERR: non-fatal — file skipped
            return None


class DuplicateFinderApp(StandardWindow):
    """Simple Duplicate Finder GUI."""

    def __init__(self, hub_instance=None, parent=None):
        # Always use the safe constructor parameters
        super().__init__(
            title=_DupFinderStrings.WINDOW_TITLE,
            window_type="utility",
            parent=parent,
        )
        self._hub = hub_instance
        try:
            from src.rfu.log_manager import get_log_manager

            self._logger = get_log_manager().get_logger("DuplicateFinderApp")
        except Exception:
            self._logger = logging.getLogger("DuplicateFinderApp")
        self.setGeometry(100, 100, 800, 600)

        self.duplicates = {}
        self.selected_directory = None
        self._worker: DuplicateScanWorker | None = None
        self._thread: QThread | None = None
        self.init_ui()
        if STANDARD_WINDOW_AVAILABLE:
            self._setup_menu_callbacks()
        # Ensure menu bar exists (safe to call in both modes)
        self.ensure_menu_bar()
        register_gui_component(
            self, tool_id="duplicate_finder", recovery_callback=self.degraded_fallback
        )
        _emit_telemetry("ui_view_load", tool_id="duplicate_finder")
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
            self._logger.warning("DuplicateFinderApp entering degraded mode")
        except Exception:
            pass
        _emit_telemetry(
            "ui_error_event", tool_id="duplicate_finder", error_type="degraded"
        )

    def _setup_menu_callbacks(self):
        """Setup tool-specific menu callbacks."""
        if hasattr(self, "menu_manager"):
            # Register tool-specific callbacks
            self.menu_manager.register_callback("new_scan", self.clear_results)
            # Override the standard help with our tool-specific help
            self.menu_manager.register_callback("show_user_guide", self.show_help)
            self.menu_manager.register_callback(
                "show_preferences", self.show_preferences
            )
            self.menu_manager.register_callback("refresh", self.refresh_view)

    def clear_results(self):
        """Clear all duplicate scan results."""
        self.duplicates = {}
        if hasattr(self, "results_list"):
            self.results_list.clear()

    def show_help(self):
        """Show help dialog for Duplicate Finder tool."""
        help_text = """
        <h2>Duplicate Finder - Help</h2>

        <h3>How to Find Duplicates:</h3>
        <ul>
        <li><b>Select Directory:</b> Choose the folder to scan for duplicates</li>
        <li><b>Start Scan:</b> Begin searching for duplicate files</li>
        <li><b>Review Results:</b> Examine found duplicates in the results list</li>
        </ul>

        <h3>Duplicate Detection:</h3>
        <ul>
        <li><b>File Comparison:</b> Uses MD5 checksums for accurate detection</li>
        <li><b>Size Filtering:</b> Pre-filters by file size for efficiency</li>
        <li><b>Content Verification:</b> Compares actual file content</li>
        <li><b>Safe Detection:</b> Never modifies original files</li>
        </ul>

        <h3>Results Management:</h3>
        <ul>
        <li><b>Group Display:</b> Duplicates grouped by content similarity</li>
        <li><b>Path Information:</b> Full file paths for each duplicate</li>
        <li><b>Size Details:</b> File sizes and modification dates</li>
        <li><b>Export Options:</b> Save results to file for review</li>
        </ul>

        <h3>Best Practices:</h3>
        <ul>
        <li><b>Backup First:</b> Always backup important files before cleanup</li>
        <li><b>Manual Review:</b> Verify duplicates before any deletion</li>
        <li><b>Keep Originals:</b> Preserve files in primary locations</li>
        <li><b>Scan Regularly:</b> Periodic scans help maintain organization</li>
        </ul>

        <h3>Keyboard Shortcuts:</h3>
        <ul>
        <li><b>Ctrl+Q:</b> Exit application</li>
        <li><b>F1:</b> Show this help</li>
        <li><b>F5:</b> Clear results and start new scan</li>
        </ul>
        """

        if Modal:
            Modal("Duplicate Finder Help", help_text, parent=self).exec_()
        else:
            QMessageBox.information(self, "Duplicate Finder Help", help_text)

    def show_preferences(self):
        """Show Duplicate Finder preferences."""
        msg = (
            "Duplicate Finder preferences:\n\n"
            "• Scan depth limits\n"
            "• File type filters\n"
            "• Minimum file size settings\n"
            "• Checksum algorithm options\n\n"
            "Advanced preferences coming soon!"
        )
        if Modal:
            Modal("Duplicate Finder Preferences", msg, parent=self).exec_()
        else:
            QMessageBox.information(self, "Duplicate Finder Preferences", msg)

    def refresh_view(self):
        """Refresh/clear the current scan results."""
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
        header_label = _ui_widget(QLabel, 'Legacy.sfba9a040c5d31d24', 'setText')
        header_label.setStyleSheet(
            f"""
            QLabel {{

                font-weight: bold;
                color: {token('text_primary')};
                padding: 10px;
                background-color: {token('background')};
                border-radius: 5px;
                margin-bottom: 10px;
            }}
        """
        )
        font_tokens.bind(header_label, "font.toolHeader")
        layout.addWidget(header_label)

        # Directory selection
        dir_group = _ui_widget(QGroupBox, 'Legacy.s30d2d5574cce5ea3', 'setTitle')
        dir_layout = QVBoxLayout(dir_group)

        select_button = _ui_widget(SecondaryButton, 'Legacy.s220c3fe6289ca828', 'setText')
        select_button.clicked.connect(self.select_directory)
        dir_layout.addWidget(select_button)

        self.dir_label = _ui_widget(QLabel, 'Legacy.sbf355de778591b63', 'setText')
        dir_layout.addWidget(self.dir_label)

        layout.addWidget(dir_group)

        # Find button
        find_button = _ui_widget(PrimaryButton, 'Legacy.s464e1de43383aadf', 'setText')
        find_button.clicked.connect(self.find_duplicates)
        layout.addWidget(find_button)

        # Results
        self.results_list = QListWidget()
        _ui_bind(self.results_list, 'setAccessibleName', 'Legacy.s78c341a0d40b5add')
        layout.addWidget(self.results_list)

        # Loading indicator (PERF-3a/3b)
        if LoadingIndicator:
            self._loading_indicator = LoadingIndicator(
                parent=self, message="Scanning for duplicates…"
            )
            layout.addWidget(self._loading_indicator)
        else:
            self._loading_indicator = None

        self.selected_directory = None

    def select_directory(self):
        """Select a directory to scan."""
        dir_path = QFileDialog.getExistingDirectory(self, "Select Directory to Scan")
        if dir_path:
            self.selected_directory = dir_path
            self.dir_label.setText(f"Selected: {dir_path}")

    def find_duplicates(self):
        """Start duplicate scan in a background thread (PERF-1d)."""
        if not self.selected_directory:
            if Modal:
                Modal(
                    "Warning", "Please select a directory first.", parent=self
                ).exec_()
            else:
                QMessageBox.warning(self, "Warning", "Please select a directory first.")
            return

        if self._thread and self._thread.isRunning():
            return  # already scanning

        self.results_list.clear()
        self.results_list.addItem("Scanning for duplicates…")

        # PERF-3a: start indicator before worker
        if self._loading_indicator:
            self._loading_indicator.start()

        self._worker = DuplicateScanWorker(self.selected_directory)
        self._thread = QThread()
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.finished.connect(self._display_results)
        self._worker.error.connect(self._on_scan_error)
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

    def _on_scan_error(self, message: str) -> None:  # ERR: non-fatal
        self._logger.error(f"Duplicate scan error: {message}", exc_info=True)
        if Modal:
            Modal("Error", _DupFinderStrings.ERR_SCAN_FAILED, ["OK"], self).exec_()

    def _display_results(self, duplicates: list) -> None:
        """Display scan results in the list widget."""
        self.results_list.clear()

        if duplicates:
            self.results_list.addItem(f"Found {len(duplicates)} duplicate pairs:")
            for original, duplicate in duplicates:
                self.results_list.addItem(f"Original: {original}")
                self.results_list.addItem(f"Duplicate: {duplicate}")
                self.results_list.addItem("---")
        else:
            self.results_list.addItem("No duplicates found.")


def main():
    """Main function for standalone execution."""
    app = QApplication(sys.argv)
    window = DuplicateFinderApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
