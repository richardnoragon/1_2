"""
Image Metadata Editor GUI Wrapper

This module provides a comprehensive GUI wrapper for image metadata operations,
using the enhanced utilities logic while maintaining compatibility with the
existing tools interface.
"""
from src.rfu.localization import localized_widget as _ui_widget, bind_literal as _ui_bind
from src.rfu import font_tokens

import logging
import os
import sys
from typing import Any, Dict, List, Optional

try:
    from PyQt5.QtCore import Qt, QThread, pyqtSignal
    from PyQt5.QtGui import QFont
    from PyQt5.QtWidgets import (
        QApplication,
        QFileDialog,
        QGridLayout,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QMainWindow,
        QMessageBox,
        QProgressBar,
        QPushButton,
        QSplitter,
        QTabWidget,
        QTextEdit,
        QTreeWidget,
        QTreeWidgetItem,
        QVBoxLayout,
        QWidget,
    )

    from src.gui.themes import ThemeManager, token
except ImportError:
    print("PyQt5 not available. Please install PyQt5.")
    sys.exit(1)

# Add parent directories to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import GUI framework
try:
    from src.gui.standard_window import StandardWindow

    HAS_STANDARD_WINDOW = True
except ImportError:
    # Fallback for standalone execution
    StandardWindow = QMainWindow
    HAS_STANDARD_WINDOW = False

from src.gui.themes import Typography

# Import enhanced image metadata logic
from .image_metadata_logic import (  # noqa: E402
    ImageMetadataLogic,
    format_exif_value,
)

try:
    from src.log_manager import get_log_manager as _get_log_manager
except ImportError:
    _get_log_manager = None

try:
    from src.rfu.ui_strings import ImageMetadata as _IMStrings
except ImportError:

    class _IMStrings:
        """Fallback string constants — mirrors src/rfu/ui_strings.ImageMetadata."""

        TITLE = "Image Metadata Editor"
        WINDOW_TITLE = "Image Metadata Editor — RFU"
        LOADING = "Loading Image Metadata Editor…"
        MODAL_ERROR_TITLE = "Image Metadata Editor"
        ERR_INIT_FAILED = (
            "Could not start Image Metadata Editor. "
            "Please try again or restart the application."
        )
        ERR_LOAD_FAILED = (
            "Failed to load image metadata. "
            "Check that the file is a supported image format."
        )
        ERR_SAVE_FAILED = (
            "Failed to save image metadata. "
            "Check that you have write permission to the file."
        )


# ---------------------------------------------------------------------------
# CP: Shared UI components (graceful fallback when unavailable)
# ---------------------------------------------------------------------------
try:
    from src.gui.components.buttons import PrimaryButton, SecondaryButton
    from src.gui.components.modal import ConfirmationModal, Modal
    from src.gui.components.toast import ToastNotification

    _CP_AVAILABLE = True
except ImportError:
    PrimaryButton = SecondaryButton = None  # type: ignore[assignment,misc]
    Modal = ConfirmationModal = None  # type: ignore[assignment,misc]
    ToastNotification = None
    _CP_AVAILABLE = False


class ImageMetadataWorkerThread(QThread):
    """Enhanced worker thread for image metadata operations with batch
    support."""

    progress_updated = pyqtSignal(int)
    file_processed = pyqtSignal(str, dict)  # file_path, metadata
    operation_completed = pyqtSignal(bool, str)  # success, message
    batch_progress = pyqtSignal(int, int)  # current, total

    def __init__(
        self,
        files: List[str],
        operation: str,
        metadata_updates: Optional[Dict] = None,
    ):
        """Initialize worker thread.

        Args:
            files: List of file paths to process
            operation: Operation type ('load', 'save', 'batch_edit')
            metadata_updates: Metadata updates for save operations
        """
        super().__init__()
        self.files = files
        self.operation = operation
        self.metadata_updates = metadata_updates or {}
        self.logic = ImageMetadataLogic()
        self._should_stop = False

    def run(self):
        """Execute the metadata operation in background thread."""
        try:
            total_files = len(self.files)
            processed = 0

            for i, file_path in enumerate(self.files):
                if self._should_stop:
                    break

                self.batch_progress.emit(i + 1, total_files)

                if self.operation == "load":
                    metadata = self.logic.load_image_metadata(file_path)
                    self.file_processed.emit(file_path, metadata)

                elif self.operation == "save":
                    success = self.logic.save_image_metadata(
                        file_path, self.metadata_updates
                    )
                    if success:
                        processed += 1

                progress = int((i + 1) / total_files * 100)
                self.progress_updated.emit(progress)

            message = f"Processed {processed} of {total_files} files"
            self.operation_completed.emit(True, message)

        except (
            Exception
        ) as e:  # ERR: non-fatal — surfaced via operation_completed signal
            self.operation_completed.emit(False, f"Error: {str(e)}")

    def stop(self):
        """Stop the worker thread."""
        self._should_stop = True


class ImageMetadataEditorGUI(StandardWindow):
    """Professional Image Metadata Editor GUI with comprehensive
    functionality."""

    def __init__(self, hub_instance=None):
        # Initialize with proper window title based on available base class
        if HAS_STANDARD_WINDOW:
            super().__init__(title=_IMStrings.WINDOW_TITLE)
        else:
            super().__init__()
            self.setWindowTitle(_IMStrings.WINDOW_TITLE)

        self._hub = hub_instance
        if _get_log_manager is not None:
            try:
                self._logger = _get_log_manager().get_logger("ImageMetadataEditorGUI")
            except Exception:  # ERR: non-fatal — logger fallback to module logger
                self._logger = logging.getLogger("ImageMetadataEditorGUI")
        else:
            self._logger = logging.getLogger("ImageMetadataEditorGUI")

        # Initialize instance variables
        self.worker: Optional[ImageMetadataWorkerThread] = None
        self.selected_files: List[str] = []
        self.current_metadata: Dict[str, Any] = {}
        self.current_file_metadata: Dict[str, Any] = {}
        self.metadata_logic = ImageMetadataLogic()

        # Setup UI after parent initialization is complete
        self.init_ui()
        self._setup_menu_callbacks()
        self._connect_signals()

        self.register_gui_component(
            tool_id="image_metadata",
            recovery_callback=self.degraded_fallback,
        )
        self._emit_telemetry("ui_view_load", tool_id="image_metadata")
        ThemeManager.add_theme_changed_callback(self._on_theme_changed)

    def _on_theme_changed(self, variant: str) -> None:
        """Re-apply token-based stylesheets when the active theme variant changes."""
        pass  # stylesheets applied at init; live re-apply deferred (TH-4c/4d)

    # ── GRD : ComponentGuardian integration ──────────────────────────
    def register_gui_component(self, tool_id: str, recovery_callback=None) -> None:
        """Register this widget with ComponentGuardian (no-op if unavailable)."""
        try:
            from src.core.guardian.component_guardian import ComponentGuardian

            ComponentGuardian.instance().register(
                tool_id, self, recovery_callback=recovery_callback
            )
        except Exception:
            pass

    # ── TEL : telemetry stub ──────────────────────────────────────────
    def _emit_telemetry(self, event_type: str, **kwargs) -> None:
        """Emit a telemetry event (no-op stub until TEL infrastructure lands)."""
        try:
            from src.core.telemetry import emit_telemetry

            emit_telemetry(event_type, **kwargs)
        except Exception:
            pass

    def health_check(self) -> bool:
        """Return True if core widgets are present and functional."""
        return hasattr(self, "metadata_tabs") and self.metadata_tabs is not None

    def degraded_fallback(self) -> None:
        """Disable editing immediately without blocking Guardian recovery."""
        self.statusBar().showMessage(_IMStrings.ERR_INIT_FAILED)
        body = self.centralWidget()
        if body is not None:
            body.setEnabled(False)

    def _setup_menu_callbacks(self):
        """Setup tool-specific menu callbacks."""
        if hasattr(self, "menu_manager"):
            # Register tool-specific callbacks
            self.menu_manager.register_callback("open_files", self.browse_files)
            self.menu_manager.register_callback(
                "save_metadata", self.save_current_metadata
            )
            self.menu_manager.register_callback("show_help", self.show_help)

    def _connect_signals(self):
        """Connect metadata logic signals."""
        self.metadata_logic.metadata_loaded.connect(self._on_metadata_loaded)
        self.metadata_logic.metadata_saved.connect(self._on_metadata_saved)
        self.metadata_logic.error_occurred.connect(self._on_error)
        self.metadata_logic.progress_percentage.connect(self._on_progress_update)

    def init_ui(self):
        """Initialize the user interface."""
        # Create main layout based on available base class
        if HAS_STANDARD_WINDOW:
            # Use the existing main layout from StandardWindow
            layout = self.main_layout
        else:
            # Create our own layout for QMainWindow fallback
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)
            central_widget.setLayout(layout)

        # Create header
        header_label = self.create_header("Image Metadata Editor")
        layout.addWidget(header_label)

        # Create main content area
        content_splitter = QSplitter(Qt.Horizontal)

        # Left panel - File selection and navigation
        left_panel = self._create_file_panel()
        content_splitter.addWidget(left_panel)

        # Right panel - Metadata viewing and editing
        right_panel = self._create_metadata_panel()
        content_splitter.addWidget(right_panel)

        # Set splitter proportions
        content_splitter.setSizes([300, 700])
        layout.addWidget(content_splitter)

        # Create progress section
        self._create_progress_section(layout)

        # Create button section
        self._create_button_section(layout)

    def _create_file_panel(self):
        """Create the file selection panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # File selection group
        file_group = _ui_widget(QGroupBox, 'Legacy.s1eef7fd26962e3d2', 'setTitle')
        file_layout = QVBoxLayout(file_group)

        # Browse button
        _SB = SecondaryButton if SecondaryButton else QPushButton
        self.browse_button = _SB("Browse for Images")
        self.browse_button.clicked.connect(self.browse_files)
        file_layout.addWidget(self.browse_button)

        # File list
        self.file_list = QTreeWidget()
        _ui_bind(self.file_list, 'setAccessibleName', 'Legacy.s83a04e214a1c917a')
        self.file_list.setHeaderLabels(["Files", "Status"])
        self.file_list.itemClicked.connect(self._on_file_selected)
        file_layout.addWidget(self.file_list)

        # File info
        self.file_info_label = _ui_widget(QLabel, 'Legacy.s26bfbd5c83f90db3', 'setText')
        self.file_info_label.setWordWrap(True)
        file_layout.addWidget(self.file_info_label)

        layout.addWidget(file_group)

        # Quick actions group
        actions_group = _ui_widget(QGroupBox, 'Legacy.s2cc2b6f7f200e65c', 'setTitle')
        actions_layout = QVBoxLayout(actions_group)

        _SB2 = SecondaryButton if SecondaryButton else QPushButton
        self.load_metadata_button = _SB2("Load Metadata")
        self.load_metadata_button.clicked.connect(self.load_current_metadata)
        self.load_metadata_button.setEnabled(False)
        actions_layout.addWidget(self.load_metadata_button)

        self.batch_process_button = _SB2("Batch Process")
        self.batch_process_button.clicked.connect(self.batch_process_files)
        self.batch_process_button.setEnabled(False)
        actions_layout.addWidget(self.batch_process_button)

        layout.addWidget(actions_group)
        return panel

    def _create_metadata_panel(self):
        """Create the metadata viewing and editing panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Create tab widget for different metadata types
        self.metadata_tabs = QTabWidget()
        _ui_bind(self.metadata_tabs, 'setAccessibleName', 'Legacy.s841b0a5c37417183')

        # EXIF tab
        self.exif_tab = self._create_exif_tab()
        self.metadata_tabs.addTab(self.exif_tab, "EXIF Data")

        # Basic info tab
        self.basic_tab = self._create_basic_info_tab()
        self.metadata_tabs.addTab(self.basic_tab, "Basic Info")

        # Raw data tab
        self.raw_tab = self._create_raw_data_tab()
        self.metadata_tabs.addTab(self.raw_tab, "Raw Data")

        layout.addWidget(self.metadata_tabs)
        return panel

    def _create_exif_tab(self):
        """Create the EXIF editing tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Common EXIF fields
        exif_group = _ui_widget(QGroupBox, 'Legacy.s3af0d2112ea2148c', 'setTitle')
        exif_layout = QGridLayout(exif_group)

        # Create editable fields for common EXIF data
        self.exif_fields = {}

        common_fields = [
            ("Make", "Camera Make"),
            ("Model", "Camera Model"),
            ("DateTime", "Date/Time"),
            ("Artist", "Artist/Author"),
            ("Copyright", "Copyright"),
            ("ImageDescription", "Description"),
            ("Software", "Software"),
            ("Orientation", "Orientation"),
        ]

        for i, (field, label) in enumerate(common_fields):
            label_widget = QLabel(f"{label}:")
            edit_widget = QLineEdit()
            edit_widget.setAccessibleName(label)
            edit_widget.setPlaceholderText(f"Enter {label.lower()}")

            self.exif_fields[field] = edit_widget

            exif_layout.addWidget(label_widget, i, 0)
            exif_layout.addWidget(edit_widget, i, 1)

        layout.addWidget(exif_group)

        # GPS data group
        gps_group = _ui_widget(QGroupBox, 'Legacy.s8fc0fcd2dc9e511c', 'setTitle')
        gps_layout = QGridLayout(gps_group)

        # GPS fields
        self.gps_fields = {}
        gps_field_names = [
            ("Latitude", "Latitude"),
            ("Longitude", "Longitude"),
            ("Altitude", "Altitude"),
            ("GPSDateStamp", "GPS Date"),
        ]

        for i, (field, label) in enumerate(gps_field_names):
            label_widget = QLabel(f"{label}:")
            edit_widget = QLineEdit()
            edit_widget.setAccessibleName(label)
            edit_widget.setPlaceholderText(f"Enter {label.lower()}")

            self.gps_fields[field] = edit_widget

            gps_layout.addWidget(label_widget, i, 0)
            gps_layout.addWidget(edit_widget, i, 1)

        layout.addWidget(gps_group)
        return tab

    def _create_basic_info_tab(self):
        """Create the basic image information tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Basic image properties
        info_group = _ui_widget(QGroupBox, 'Legacy.sc6ef3f7b1e38a6ee', 'setTitle')
        info_layout = QGridLayout(info_group)

        self.info_labels = {}
        info_fields = [
            ("filename", "Filename"),
            ("filesize", "File Size"),
            ("format", "Format"),
            ("mode", "Mode"),
            ("width", "Width"),
            ("height", "Height"),
            ("has_exif", "Has EXIF"),
        ]

        for i, (field, label) in enumerate(info_fields):
            label_widget = QLabel(f"{label}:")
            value_widget = _ui_widget(QLabel, 'Legacy.se2f79e5b60330bba', 'setText')
            value_widget.setStyleSheet(f"QLabel {{ color: {token('text_primary')}; }}")

            self.info_labels[field] = value_widget

            info_layout.addWidget(label_widget, i, 0)
            info_layout.addWidget(value_widget, i, 1)

        layout.addWidget(info_group)

        # Add spacer
        layout.addStretch()
        return tab

    def _create_raw_data_tab(self):
        """Create the raw metadata display tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Raw data display
        self.raw_data_text = QTextEdit()
        _ui_bind(self.raw_data_text, 'setAccessibleName', 'Legacy.saea3f538492eea6c')
        self.raw_data_text.setReadOnly(True)
        self.raw_data_text.setFont(self._get_monospace_font())
        layout.addWidget(self.raw_data_text)

        return tab

    def _create_progress_section(self, parent_layout):
        """Create the progress monitoring section."""
        progress_group = _ui_widget(QGroupBox, 'Legacy.s9ece66e0d30cdbcc', 'setTitle')
        progress_layout = QVBoxLayout(progress_group)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)

        # Status label
        self.status_label = _ui_widget(QLabel, 'Legacy.s5fa7aac5375c5815', 'setText')
        self.status_label.setStyleSheet(
            f"QLabel {{ color: {token('semantic_success')}; }}"
        )
        progress_layout.addWidget(self.status_label)

        parent_layout.addWidget(progress_group)

    def _create_button_section(self, parent_layout):
        """Create the action buttons section."""
        button_layout = QHBoxLayout()

        # Save button
        _PB = PrimaryButton if PrimaryButton else QPushButton
        self.save_button = _PB("Save Metadata")
        self.save_button.clicked.connect(self.save_current_metadata)
        self.save_button.setEnabled(False)
        button_layout.addWidget(self.save_button)

        _SB3 = SecondaryButton if SecondaryButton else QPushButton
        self.clear_button = _SB3("Clear Fields")
        self.clear_button.clicked.connect(self.clear_metadata_fields)
        button_layout.addWidget(self.clear_button)

        self.refresh_button = _SB3("Refresh")
        self.refresh_button.clicked.connect(self.load_current_metadata)
        self.refresh_button.setEnabled(False)
        button_layout.addWidget(self.refresh_button)

        button_layout.addStretch()

        self.cancel_button = _SB3("Cancel Operation")
        self.cancel_button.clicked.connect(self.cancel_operation)
        self.cancel_button.setVisible(False)
        button_layout.addWidget(self.cancel_button)

        parent_layout.addLayout(button_layout)

    def create_header(self, text: str) -> QLabel:
        """Create a standard header label."""
        header = QLabel(text)
        if HAS_STANDARD_WINDOW:
            # Use StandardWindow styling if available
            header.setStyleSheet(
                """
                QLabel {

                    font-weight: bold;
                    color: {token('text_primary')};
                    padding: 10px;
                    background-color: {token('background')};
                    border-radius: 5px;
                    margin-bottom: 10px;
                }
            """
            )
            font_tokens.bind(header, "font.toolHeader")
        else:
            # Basic styling for fallback
            header.setStyleSheet(
                """
                QLabel {

                    font-weight: bold;
                    padding: 10px;
                    margin-bottom: 10px;
                }
            """
            )
            font_tokens.bind(header, "font.toolHeader")
        return header

    def _get_monospace_font(self):
        """Get a monospace font for raw data display."""
        font = Typography.body()
        font.setFixedPitch(True)
        return font

    # Event handlers
    def browse_files(self):
        """Browse for image files."""
        file_dialog = QFileDialog()
        file_paths, _ = file_dialog.getOpenFileNames(
            self,
            "Select Image Files",
            "",
            "Image Files (*.jpg *.jpeg *.png *.tiff *.tif *.bmp);;" "All Files (*)",
        )

        if file_paths:
            self.selected_files = file_paths
            self._populate_file_list()
            self.batch_process_button.setEnabled(len(file_paths) > 1)

    def _populate_file_list(self):
        """Populate the file list widget."""
        self.file_list.clear()

        for file_path in self.selected_files:
            item = QTreeWidgetItem([os.path.basename(file_path), "Ready"])
            item.setData(0, Qt.UserRole, file_path)
            self.file_list.addTopLevelItem(item)

    def _on_file_selected(self, item):
        """Handle file selection."""
        file_path = item.data(0, Qt.UserRole)
        if file_path:
            self.current_file_path = file_path
            self._update_file_info(file_path)
            self.load_metadata_button.setEnabled(True)
            self.refresh_button.setEnabled(True)
            # Auto-load metadata
            self.load_current_metadata()

    def _update_file_info(self, file_path: str):
        """Update file information display."""
        try:
            file_stat = os.stat(file_path)
            file_size = self._format_file_size(file_stat.st_size)

            info = f"File: {os.path.basename(file_path)}\n"
            info += f"Size: {file_size}\n"
            info += f"Path: {file_path}"

            self.file_info_label.setText(info)
        except Exception as e:  # ERR: non-fatal — surfaced via file_info_label
            self._logger.error(f"Error reading file info: {e}", exc_info=True)
            self.file_info_label.setText(_IMStrings.ERR_LOAD_FAILED)

    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format."""
        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

    def load_current_metadata(self):
        """Load metadata for the currently selected file."""
        if not hasattr(self, "current_file_path"):
            if Modal:
                Modal("Warning", "No file selected.", ["OK"], self).exec_()
            else:
                QMessageBox.warning(self, "Warning", "No file selected.")
            return

        self._set_ui_enabled(False)
        self.status_label.setText("Loading metadata...")

        # Load metadata using the logic
        try:
            metadata = self.metadata_logic.load_image_metadata(self.current_file_path)
            self._on_metadata_loaded(metadata)
        except Exception as e:  # ERR: non-fatal — surfaced via _on_error dialog
            self._logger.error(f"Failed to load metadata: {e}", exc_info=True)
            self._on_error(_IMStrings.ERR_LOAD_FAILED)

    def _on_metadata_loaded(self, metadata: Dict[str, Any]):
        """Handle metadata loaded signal."""
        self.current_metadata = metadata
        self._populate_metadata_fields(metadata)
        self._set_ui_enabled(True)
        self.save_button.setEnabled(True)
        self.status_label.setText("Metadata loaded successfully")

    def _populate_metadata_fields(self, metadata: Dict[str, Any]):
        """Populate the metadata editing fields."""
        # Clear existing data
        self.clear_metadata_fields()

        # Populate EXIF fields
        exif_data = metadata.get("exif", {})
        for field, widget in self.exif_fields.items():
            if field in exif_data:
                value = format_exif_value(exif_data[field])
                widget.setText(str(value))

        # Populate GPS fields
        gps_data = metadata.get("gps", {})
        for field, widget in self.gps_fields.items():
            if field in gps_data:
                value = format_exif_value(gps_data[field])
                widget.setText(str(value))

        # Populate basic info
        basic_info = metadata.get("basic", {})
        for field, label in self.info_labels.items():
            if field in basic_info:
                label.setText(str(basic_info[field]))

        # Populate raw data
        self._populate_raw_data(metadata)

    def _populate_raw_data(self, metadata: Dict[str, Any]):
        """Populate the raw metadata display."""
        raw_text = "=== IMAGE METADATA ===\n\n"

        for category, data in metadata.items():
            raw_text += f"=== {category.upper()} ===\n"
            if isinstance(data, dict):
                for key, value in data.items():
                    raw_text += f"{key}: {value}\n"
            else:
                raw_text += f"{data}\n"
            raw_text += "\n"

        self.raw_data_text.setPlainText(raw_text)

    def save_current_metadata(self):
        """Save the current metadata modifications."""
        if not hasattr(self, "current_file_path"):
            if Modal:
                Modal("Warning", "No file selected.", ["OK"], self).exec_()
            else:
                QMessageBox.warning(self, "Warning", "No file selected.")
            return

        # Collect modified metadata
        modified_data = self._collect_metadata_updates()

        if not modified_data:
            if Modal:
                Modal("Information", "No changes to save.", ["OK"], self).exec_()
            else:
                QMessageBox.information(self, "Information", "No changes to save.")
            return

        self._set_ui_enabled(False)
        self.status_label.setText("Saving metadata...")

        try:
            success = self.metadata_logic.save_image_metadata(
                self.current_file_path, modified_data
            )
            self._on_metadata_saved(success, "Metadata saved successfully")
        except Exception as e:  # ERR: non-fatal — surfaced via _on_error dialog
            self._logger.error(f"Failed to save metadata: {e}", exc_info=True)
            self._on_error(_IMStrings.ERR_SAVE_FAILED)

    def _collect_metadata_updates(self) -> Dict[str, Any]:
        """Collect metadata updates from the form fields."""
        updates = {}

        # Collect EXIF updates
        exif_updates = {}
        for field, widget in self.exif_fields.items():
            text = widget.text().strip()
            if text:
                exif_updates[field] = text

        if exif_updates:
            updates["exif"] = exif_updates

        # Collect GPS updates
        gps_updates = {}
        for field, widget in self.gps_fields.items():
            text = widget.text().strip()
            if text:
                gps_updates[field] = text

        if gps_updates:
            updates["gps"] = gps_updates

        return updates

    def _on_metadata_saved(self, success: bool, message: str):
        """Handle metadata saved signal."""
        self._set_ui_enabled(True)

        if success:
            self.status_label.setText("Metadata saved successfully")
            if ToastNotification:
                ToastNotification(parent=self).show_message(message, "success")
            else:
                QMessageBox.information(self, "Success", message)
            # Reload to show saved changes
            self.load_current_metadata()
        else:
            self.status_label.setText("Failed to save metadata")
            if Modal:
                Modal("Error", message, ["OK"], self).exec_()
            else:
                QMessageBox.warning(self, "Error", message)

    def _on_error(self, error_message: str):
        """Handle error signal."""
        self._set_ui_enabled(True)
        self.status_label.setText("Error occurred")
        if Modal:
            Modal("Error", error_message, ["OK"], self).exec_()
        else:
            QMessageBox.critical(self, "Error", error_message)

    def _on_progress_update(self, percentage: int):
        """Handle progress update signal."""
        self.progress_bar.setValue(percentage)

    def clear_metadata_fields(self):
        """Clear all metadata editing fields."""
        # Clear EXIF fields
        for widget in self.exif_fields.values():
            widget.clear()

        # Clear GPS fields
        for widget in self.gps_fields.values():
            widget.clear()

        # Clear info labels
        for label in self.info_labels.values():
            label.setText("N/A")

        # Clear raw data
        self.raw_data_text.clear()

    def batch_process_files(self):
        """Process multiple files in batch."""
        if not self.selected_files:
            if Modal:
                Modal("Warning", "No files selected.", ["OK"], self).exec_()
            else:
                QMessageBox.warning(self, "Warning", "No files selected.")
            return

        # Get metadata updates
        updates = self._collect_metadata_updates()
        if not updates:
            if Modal:
                Modal(
                    "Information",
                    "No metadata changes to apply in batch.",
                    ["OK"],
                    self,
                ).exec_()
            else:
                QMessageBox.information(
                    self, "Information", "No metadata changes to apply in batch."
                )
            return

        # Confirm batch operation
        if ConfirmationModal:
            dlg = ConfirmationModal(
                "Confirm Batch Operation",
                f"Apply metadata changes to {len(self.selected_files)} files?",
                confirm_text="Apply",
                cancel_text="Cancel",
                parent=self,
            )
            if not dlg.exec_():
                return
        else:
            reply = QMessageBox.question(
                self,
                "Confirm Batch Operation",
                f"Apply metadata changes to {len(self.selected_files)} files?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply != QMessageBox.Yes:
                return

        # Start batch processing
        self._start_batch_operation(self.selected_files, "save", updates)

    def _start_batch_operation(
        self,
        files: List[str],
        operation: str,
        metadata_updates: Optional[Dict] = None,
    ):
        """Start a batch operation."""
        self._set_ui_enabled(False)
        self.progress_bar.setVisible(True)
        self.cancel_button.setVisible(True)

        self.worker = ImageMetadataWorkerThread(files, operation, metadata_updates)
        self.worker.progress_updated.connect(self.progress_bar.setValue)
        self.worker.file_processed.connect(self._on_file_processed)
        self.worker.operation_completed.connect(self._on_batch_completed)
        self.worker.batch_progress.connect(self._on_batch_progress)

        self.worker.start()

    def _on_file_processed(self, file_path: str, metadata: Dict[str, Any]):
        """Handle individual file processed in batch."""
        # Update file list status
        for i in range(self.file_list.topLevelItemCount()):
            item = self.file_list.topLevelItem(i)
            if item.data(0, Qt.UserRole) == file_path:
                item.setText(1, "Processed")
                break

    def _on_batch_progress(self, current: int, total: int):
        """Handle batch progress update."""
        self.status_label.setText(f"Processing {current} of {total} files...")

    def _on_batch_completed(self, success: bool, message: str):
        """Handle batch operation completion."""
        self._cleanup_operation()

        if success:
            if ToastNotification:
                ToastNotification(parent=self).show_message(message, "success")
            else:
                QMessageBox.information(self, "Batch Complete", message)
        else:
            if Modal:
                Modal("Batch Error", message, ["OK"], self).exec_()
            else:
                QMessageBox.warning(self, "Batch Error", message)

    def cancel_operation(self):
        """Cancel the current operation."""
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            # PERF-2b: do not block-wait or terminate on the UI thread.
            # operation_completed signal → _on_batch_completed → _cleanup_operation
            # handles UI cleanup when the worker finishes.
            self.status_label.setText("Cancelling…")
        else:
            self._cleanup_operation()
            self.status_label.setText("Operation cancelled")

    def _cleanup_operation(self):
        """Cleanup after operation completion or cancellation."""
        self._set_ui_enabled(True)
        self.progress_bar.setVisible(False)
        self.cancel_button.setVisible(False)

        if self.worker:
            self.worker.deleteLater()
            self.worker = None

    def _set_ui_enabled(self, enabled: bool):
        """Enable/disable UI controls during operations."""
        self.browse_button.setEnabled(enabled)
        self.load_metadata_button.setEnabled(enabled)
        self.save_button.setEnabled(enabled and hasattr(self, "current_file_path"))
        self.clear_button.setEnabled(enabled)
        self.refresh_button.setEnabled(enabled and hasattr(self, "current_file_path"))
        self.batch_process_button.setEnabled(enabled and len(self.selected_files) > 1)

        # Enable/disable metadata fields
        for widget in self.exif_fields.values():
            widget.setEnabled(enabled)
        for widget in self.gps_fields.values():
            widget.setEnabled(enabled)

    def show_help(self):
        """Show help information."""
        help_text = """
Image Metadata Editor Help

GETTING STARTED:
1. Click 'Browse for Images' to select image files
2. Click on a file in the list to select it
3. Metadata will load automatically
4. Edit the fields as needed
5. Click 'Save Metadata' to apply changes

FEATURES:
- View and edit EXIF data
- GPS information editing
- Batch processing multiple files
- Raw metadata display
- Progress tracking for operations

SUPPORTED FORMATS:
- JPEG (.jpg, .jpeg)
- PNG (.png)
- TIFF (.tif, .tiff)
- BMP (.bmp)

TIPS:
- Use batch processing for applying the same changes to multiple files
- Check the Raw Data tab to see all available metadata
- GPS coordinates should be in decimal format
- Date/time should be in YYYY:MM:DD HH:MM:SS format

ERROR HANDLING:
- The tool will show detailed error messages
- Failed operations can be retried
- Batch operations will continue even if individual files fail
        """
        QMessageBox.information(self, "Help", help_text.strip())


def main():
    """Main entry point for standalone execution."""
    app = QApplication(sys.argv)
    window = ImageMetadataEditorGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
