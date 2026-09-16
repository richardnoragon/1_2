"""Main window for the Advanced File Catalog Generator.

This module provides the main GUI interface for the advanced catalog generator
with comprehensive sorting, color-coding, and export capabilities.
"""
from src.rfu.localization import localized_widget as _ui_widget, bind_literal as _ui_bind

from src.rfu import font_tokens
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from PyQt5.QtCore import Qt, QThread, QTimer, pyqtSignal
from PyQt5.QtGui import QColor, QFont, QPalette
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

# Import StandardWindow for menu integration
try:
    from src.gui.standard_window import StandardWindow
except ImportError:
    # Fallback for standalone execution
    StandardWindow = QMainWindow


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
    from src.rfu.ui_strings import AdvancedCatalog as _AdvCatalogStrings
except ImportError:

    class _AdvCatalogStrings:  # type: ignore[no-redef]
        TITLE = "Advanced Catalog Generator"
        WINDOW_TITLE = "Advanced Catalog Generator — RFU"
        LOADING = "Loading Advanced Catalog Generator…"
        ERR_INIT_FAILED = (
            "Could not start Advanced Catalog Generator. "
            "Please try again or restart the application."
        )
        ERR_SCAN_FAILED = "Could not scan directory. Please try again."
        ERR_EXPORT_FAILED = "Could not export catalog. Please try again."


# ---------------------------------------------------------------------------
# CP: Component Placement — PrimaryButton / SecondaryButton / Modal
# ---------------------------------------------------------------------------
try:
    from src.gui.components.buttons import PrimaryButton, SecondaryButton

    _CP_AVAILABLE = True
except ImportError:
    PrimaryButton = QPushButton  # type: ignore[misc,assignment]
    SecondaryButton = QPushButton  # type: ignore[misc,assignment]
    _CP_AVAILABLE = False

try:
    from src.gui.components.modal import Modal
except ImportError:
    Modal = None  # type: ignore[assignment,misc]


from .catalog_data_model import CatalogData, ColorScheme, SortCriteria
from .color_coding_engine import ColorCodingEngine
from .export_engine import CSVExporter, HTMLExporter, JSONExporter
from .sorting_engine import SortingEngine


class FileScanThread(QThread):
    """Background thread for scanning files."""

    progress_updated = pyqtSignal(int, str)
    scan_completed = pyqtSignal(object)  # CatalogData
    scan_failed = pyqtSignal(str)

    def __init__(self, directory: Path, recursive: bool = False):
        super().__init__()
        self.directory = directory
        self.recursive = recursive
        self.catalog_data = None

    def run(self):
        """Run the file scanning process."""
        try:
            self.progress_updated.emit(10, "Initializing scan...")
            self.catalog_data = CatalogData()

            self.progress_updated.emit(20, "Scanning directory...")
            self.catalog_data.scan_directory(self.directory, self.recursive)

            self.progress_updated.emit(100, "Scan completed")
            self.scan_completed.emit(self.catalog_data)

        except (
            Exception
        ) as e:  # ERR: non-fatal — surfaced via scan_failed signal; handled in _on_scan_failed
            self.scan_failed.emit(str(e))


class ExportThread(QThread):
    """Background thread for exporting catalogs."""

    progress_updated = pyqtSignal(int, str)
    export_completed = pyqtSignal(str)  # output_path
    export_failed = pyqtSignal(str)

    def __init__(self, catalog_data, exporter, output_path: Path):
        super().__init__()
        self.catalog_data = catalog_data
        self.exporter = exporter
        self.output_path = output_path

    def run(self):
        """Run the export process."""
        try:
            # Set progress callback
            self.exporter.set_progress_callback(self._progress_callback)

            success = self.exporter.export(self.catalog_data, self.output_path)

            if success:
                self.export_completed.emit(str(self.output_path))
            else:
                self.export_failed.emit("Export failed - unknown error")

        except (
            Exception
        ) as e:  # ERR: non-fatal — surfaced via export_failed signal; handled in _on_export_failed
            self.export_failed.emit(str(e))

    def _progress_callback(self, percentage: int, message: str):
        """Progress callback for the exporter."""
        self.progress_updated.emit(percentage, message)


class AdvancedCatalogWindow(StandardWindow):
    """Main window for advanced catalog generation."""

    def __init__(self, hub_instance=None):
        try:
            super().__init__(
                title=_AdvCatalogStrings.WINDOW_TITLE,
                window_type="file_operations",
            )
        except (
            TypeError
        ):  # ERR: non-fatal — QMainWindow fallback when StandardWindow constructor rejects kwargs
            # Fallback for QMainWindow
            super().__init__()
            self.setWindowTitle(_AdvCatalogStrings.WINDOW_TITLE)

        self._hub = hub_instance
        self.hub_instance = hub_instance  # legacy alias kept for compatibility
        try:
            from src.rfu.log_manager import get_log_manager

            self._logger = get_log_manager().get_logger("AdvancedCatalogWindow")
        except Exception:
            self._logger = logging.getLogger("AdvancedCatalogWindow")

        # Initialize data
        self.catalog_data = CatalogData()
        self.sorting_engine = SortingEngine()
        self.color_engine = ColorCodingEngine()
        self.current_directory = None

        # Initialize threads
        self.scan_thread = None
        self.export_thread = None

        # Setup UI
        self._setup_ui()
        self._connect_signals()
        self._setup_menu_callbacks()

        # Set initial state
        self._set_initial_state()
        register_gui_component(
            self,
            tool_id="advanced_catalog",
            recovery_callback=self.degraded_fallback,
        )
        _emit_telemetry("ui_view_load", tool_id="advanced_catalog")

    def health_check(self) -> bool:
        """Return True if core UI is functional (GRD-3a)."""
        try:
            return self.centralWidget() is not None
        except Exception:
            return False

    def degraded_fallback(self) -> None:
        """Enter degraded / read-only state (GRD-3b)."""
        try:
            self._logger.warning("AdvancedCatalogWindow entering degraded mode")
        except Exception:
            pass
        _emit_telemetry(
            "ui_error_event", tool_id="advanced_catalog", error_type="degraded"
        )

    def _setup_ui(self):
        """Setup the user interface."""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Header
        header_label = _ui_widget(QLabel, 'Legacy.s04592b544f8d18f7', 'setText')
        header_font = Typography.body()

        header_font.setBold(True)
        header_label.setFont(header_font)
        header_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header_label)

        # Directory selection
        dir_group = self._create_directory_group()
        main_layout.addWidget(dir_group)

        # Create splitter for main content
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # Left panel - Configuration
        config_widget = self._create_config_panel()
        splitter.addWidget(config_widget)

        # Right panel - Preview and Legend
        preview_widget = self._create_preview_panel()
        splitter.addWidget(preview_widget)

        # Set splitter proportions
        splitter.setSizes([400, 600])

        # Export section
        export_group = self._create_export_group()
        main_layout.addWidget(export_group)

        # Status and progress
        status_layout = QHBoxLayout()
        self.status_label = _ui_widget(QLabel, 'Legacy.s0506135a8bea582e', 'setText')
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)

        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.progress_bar)
        main_layout.addLayout(status_layout)

    def _create_directory_group(self) -> QGroupBox:
        """Create directory selection group."""
        group = _ui_widget(QGroupBox, 'Legacy.s30d2d5574cce5ea3', 'setTitle')
        layout = QHBoxLayout(group)

        self.select_dir_btn = _ui_widget(SecondaryButton, 'Legacy.s220c3fe6289ca828', 'setText')
        self.dir_label = _ui_widget(QLabel, 'Legacy.sbf355de778591b63', 'setText')
        self.dir_label.setStyleSheet(
            f"QLabel {{ border: 1px solid gray; padding: 5px; background-color: {token('surface')}; }}"
        )
        self.recursive_cb = _ui_widget(QCheckBox, 'Legacy.s73d35e999740bfc8', 'setText')
        self.recursive_cb.setChecked(True)
        _ui_bind(self.recursive_cb, 'setAccessibleName', 'Legacy.s7fe3b250ab4b4940')
        _ui_bind(self.recursive_cb, 'setAccessibleDescription', 'Legacy.sdc6b4d7e4114808d')
        self.recursive_cb.setMinimumHeight(44)

        layout.addWidget(self.select_dir_btn)
        layout.addWidget(self.dir_label, 1)
        layout.addWidget(self.recursive_cb)

        return group

    def _create_config_panel(self) -> QWidget:
        """Create configuration panel."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Sort configuration
        sort_group = _ui_widget(QGroupBox, 'Legacy.sd4bd4904fbaa4a06', 'setTitle')
        sort_layout = QVBoxLayout(sort_group)

        # Sort criteria selection
        criteria_layout = QHBoxLayout()
        criteria_layout.addWidget(_ui_widget(QLabel, 'Legacy.s27ab0062ef43bf40', 'setText'))

        self.sort_combo = QComboBox()
        _ui_bind(self.sort_combo, 'setAccessibleName', 'Legacy.s3c9b30285f90cf05')
        self.sort_combo.addItems(
            [
                "Alphabetical (A-Z)",
                "File Size",
                "File Type",
                "Creation Date",
                "Modification Date",
                "Access Date",
            ]
        )
        criteria_layout.addWidget(self.sort_combo)
        sort_layout.addLayout(criteria_layout)

        # Sort order
        order_layout = QHBoxLayout()
        self.ascending_cb = _ui_widget(QCheckBox, 'Legacy.sfa5a12e1c71f6bb9', 'setText')
        self.ascending_cb.setChecked(True)
        _ui_bind(self.ascending_cb, 'setAccessibleName', 'Legacy.s7005a161d4aa0778')
        _ui_bind(self.ascending_cb, 'setAccessibleDescription', 'Legacy.s136e6e6b129695ad')
        self.ascending_cb.setMinimumHeight(44)
        order_layout.addWidget(self.ascending_cb)
        sort_layout.addLayout(order_layout)

        # Apply sort button
        self.apply_sort_btn = _ui_widget(SecondaryButton, 'Legacy.s287604906bf25b92', 'setText')
        sort_layout.addWidget(self.apply_sort_btn)

        layout.addWidget(sort_group)

        # Color scheme configuration
        color_group = _ui_widget(QGroupBox, 'Legacy.sc52309d3f294de8f', 'setTitle')
        color_layout = QVBoxLayout(color_group)

        scheme_layout = QHBoxLayout()
        scheme_layout.addWidget(_ui_widget(QLabel, 'Legacy.sd22fb33a0d2d41fc', 'setText'))

        self.color_scheme_combo = QComboBox()
        _ui_bind(self.color_scheme_combo, 'setAccessibleName', 'Legacy.s10ee94005bb99845')
        self.color_scheme_combo.addItems(
            ["Default", "High Contrast", "Colorblind Friendly", "Monochrome"]
        )
        scheme_layout.addWidget(self.color_scheme_combo)
        color_layout.addLayout(scheme_layout)

        # Accessibility options
        self.accessibility_cb = _ui_widget(QCheckBox, 'Legacy.s76dc0d6a3f889459', 'setText')
        _ui_bind(self.accessibility_cb, 'setAccessibleName', 'Legacy.s42f20d3219f95d26')
        _ui_bind(self.accessibility_cb, 'setAccessibleDescription', 'Legacy.s1216179652e1db5d')
        self.accessibility_cb.setMinimumHeight(44)
        color_layout.addWidget(self.accessibility_cb)

        layout.addWidget(color_group)

        # Statistics
        stats_group = _ui_widget(QGroupBox, 'Legacy.sa656107e99c71dea', 'setTitle')
        stats_layout = QVBoxLayout(stats_group)

        self.stats_text = QTextEdit()
        _ui_bind(self.stats_text, 'setAccessibleName', 'Legacy.sa656107e99c71dea')
        self.stats_text.setMaximumHeight(150)
        self.stats_text.setReadOnly(True)
        stats_layout.addWidget(self.stats_text)

        layout.addWidget(stats_group)

        layout.addStretch()
        return widget

    def _create_preview_panel(self) -> QWidget:
        """Create preview and legend panel."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # File preview
        preview_group = _ui_widget(QGroupBox, 'Legacy.s07f3d730cfb74f22', 'setTitle')
        preview_layout = QVBoxLayout(preview_group)

        # File count label
        self.file_count_label = _ui_widget(QLabel, 'Legacy.sff4cfe58b8d5f546', 'setText')
        preview_layout.addWidget(self.file_count_label)

        # File list
        self.file_list = QListWidget()
        _ui_bind(self.file_list, 'setAccessibleName', 'Legacy.s66abb418a562e894')
        self.file_list.setAlternatingRowColors(True)
        preview_layout.addWidget(self.file_list)

        layout.addWidget(preview_group)

        # Color legend
        legend_group = _ui_widget(QGroupBox, 'Legacy.s481edca6e8686d1b', 'setTitle')
        legend_layout = QVBoxLayout(legend_group)

        # Legend scroll area
        self.legend_scroll = QScrollArea()
        self.legend_widget = QWidget()
        self.legend_layout = QVBoxLayout(self.legend_widget)
        self.legend_scroll.setWidget(self.legend_widget)
        self.legend_scroll.setWidgetResizable(True)
        self.legend_scroll.setMaximumHeight(200)

        legend_layout.addWidget(self.legend_scroll)
        layout.addWidget(legend_group)

        return widget

    def _create_export_group(self) -> QGroupBox:
        """Create export configuration group."""
        group = _ui_widget(QGroupBox, 'Legacy.sfa02422c2640e672', 'setTitle')
        layout = QHBoxLayout(group)

        # Format selection
        layout.addWidget(_ui_widget(QLabel, 'Legacy.s0511f25cd80edb02', 'setText'))

        self.export_format_combo = QComboBox()
        _ui_bind(self.export_format_combo, 'setAccessibleName', 'Legacy.sdf339cb8da14714c')
        self.export_format_combo.addItems(
            ["HTML (with CSS)", "CSV (with metadata)", "JSON (structured)"]
        )
        layout.addWidget(self.export_format_combo)

        # Export button
        self.export_btn = _ui_widget(PrimaryButton, 'Legacy.sa6574d527b5c1287', 'setText')
        self.export_btn.setEnabled(False)
        layout.addWidget(self.export_btn)

        # Open after export
        self.open_after_export_cb = _ui_widget(QCheckBox, 'Legacy.se16d248630cc1b61', 'setText')
        self.open_after_export_cb.setChecked(True)
        _ui_bind(self.open_after_export_cb, 'setAccessibleName', 'Legacy.se16d248630cc1b61')
        _ui_bind(self.open_after_export_cb, 'setAccessibleDescription', 'Legacy.s5bb3506732731c57')
        self.open_after_export_cb.setMinimumHeight(44)
        layout.addWidget(self.open_after_export_cb)

        layout.addStretch()

        return group

    def _connect_signals(self):
        """Connect UI signals to their handlers."""
        self.select_dir_btn.clicked.connect(self._select_directory)
        self.apply_sort_btn.clicked.connect(self._apply_sort)
        self.export_btn.clicked.connect(self._export_catalog)

        # Combo box changes
        self.sort_combo.currentTextChanged.connect(self._on_sort_criteria_changed)
        self.color_scheme_combo.currentTextChanged.connect(
            self._on_color_scheme_changed
        )
        self.accessibility_cb.toggled.connect(self._on_accessibility_toggled)

    def _setup_menu_callbacks(self):
        """Setup tool-specific menu callbacks."""
        if hasattr(self, "menu_manager"):
            self.menu_manager.register_callback("new_catalog", self._new_catalog)
            self.menu_manager.register_callback("save_operation", self._save_settings)
            self.menu_manager.register_callback("load_operation", self._load_settings)
            self.menu_manager.register_callback("export_results", self._export_catalog)

    def _set_initial_state(self):
        """Set initial UI state."""
        self.apply_sort_btn.setEnabled(False)
        self._update_stats_display()

    def _select_directory(self):
        """Handle directory selection."""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Directory to Catalog"
        )

        if directory:
            self.current_directory = Path(directory)
            self.dir_label.setText(directory)
            self._start_file_scan()

    def _start_file_scan(self):
        """Start background file scanning."""
        if not self.current_directory:
            return

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Scanning files...")

        # Create and start scan thread
        self.scan_thread = FileScanThread(
            self.current_directory, self.recursive_cb.isChecked()
        )
        self.scan_thread.progress_updated.connect(self._on_scan_progress)
        self.scan_thread.scan_completed.connect(self._on_scan_completed)
        self.scan_thread.scan_failed.connect(self._on_scan_failed)
        self.scan_thread.start()

        # Report to hub
        if self.hub_instance:
            self.hub_instance.update_tool_progress(
                "Advanced Catalog Generator", 10, "Scanning files..."
            )

    def _on_scan_progress(self, percentage: int, message: str):
        """Handle scan progress updates."""
        self.progress_bar.setValue(percentage)
        self.status_label.setText(message)

        if self.hub_instance:
            self.hub_instance.update_tool_progress(
                "Advanced Catalog Generator", percentage, message
            )

    def _on_scan_completed(self, catalog_data: CatalogData):
        """Handle scan completion."""
        self.catalog_data = catalog_data
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"Loaded {len(catalog_data.entries)} files")

        # Enable controls
        self.apply_sort_btn.setEnabled(True)
        self.export_btn.setEnabled(True)

        # Apply initial sort
        self._apply_sort()

        # Update statistics
        self._update_stats_display()

        if self.hub_instance:
            self.hub_instance.update_tool_progress(
                "Advanced Catalog Generator", 100, "Scan completed"
            )

    def _on_scan_failed(self, error_message: str):
        """Handle scan failure."""
        self.progress_bar.setVisible(False)
        self.status_label.setText("Scan failed")

        if Modal:
            Modal(
                "Scan Error",
                f"Failed to scan directory:\n{error_message}",
                ["OK"],
                self,
            ).exec_()
        else:
            QMessageBox.critical(
                self, "Scan Error", f"Failed to scan directory:\n{error_message}"
            )

        if self.hub_instance:
            self.hub_instance.update_tool_progress(
                "Advanced Catalog Generator", 0, "Scan failed"
            )

    def _apply_sort(self):
        """Apply the selected sorting criteria."""
        if not self.catalog_data.entries:
            return

        # Get sort criteria
        criteria_map = {
            "Alphabetical (A-Z)": SortCriteria.ALPHABETICAL,
            "File Size": SortCriteria.SIZE,
            "File Type": SortCriteria.TYPE,
            "Creation Date": SortCriteria.CREATED_DATE,
            "Modification Date": SortCriteria.MODIFIED_DATE,
            "Access Date": SortCriteria.ACCESSED_DATE,
        }

        criteria_text = self.sort_combo.currentText()
        criteria = criteria_map.get(criteria_text, SortCriteria.ALPHABETICAL)
        reverse = not self.ascending_cb.isChecked()

        # Apply sorting
        self.catalog_data.entries = self.sorting_engine.sort_entries(
            self.catalog_data.entries, criteria, reverse
        )
        self.catalog_data.sort_criteria = criteria

        # Apply color coding
        self._apply_color_coding()

        # Update preview
        self._update_file_preview()
        self._update_color_legend()

        self.status_label.setText(
            f"Applied {criteria_text} sort to {len(self.catalog_data.entries)} files"
        )

    def _apply_color_coding(self):
        """Apply color coding to entries."""
        # Set color scheme
        scheme_map = {
            "Default": ColorScheme.DEFAULT,
            "High Contrast": ColorScheme.HIGH_CONTRAST,
            "Colorblind Friendly": ColorScheme.COLORBLIND_FRIENDLY,
            "Monochrome": ColorScheme.MONOCHROME,
        }

        scheme_text = self.color_scheme_combo.currentText()
        scheme = scheme_map.get(scheme_text, ColorScheme.DEFAULT)

        self.color_engine.scheme = scheme
        self.color_engine.enable_accessibility_mode(self.accessibility_cb.isChecked())
        self.catalog_data.color_scheme = scheme

        # Apply colors
        self.color_engine.assign_colors(
            self.catalog_data.entries, self.catalog_data.sort_criteria
        )

        # Generate legend
        self.catalog_data.color_legend = self.color_engine.generate_legend(
            self.catalog_data.sort_criteria
        )

    def _update_file_preview(self):
        """Update the file preview list."""
        self.file_list.clear()

        for entry in self.catalog_data.entries[:100]:  # Show first 100 files
            item_text = (
                f"{entry.name} ({entry.format_size()}) - {entry.file_type.value}"
            )
            item = QListWidgetItem(item_text)

            # Apply color if available
            if entry.color_category:
                color = QColor(entry.color_category.color_hex)
                item.setBackground(color)

                # Always prepend icon as non-colour indicator (A11Y-4)
                item_text = f"{entry.color_category.icon} {item_text}"
                item.setText(item_text)

            self.file_list.addItem(item)

        # Update count
        total_files = len(self.catalog_data.entries)
        shown_files = min(100, total_files)
        self.file_count_label.setText(f"Showing {shown_files} of {total_files} files")

    def _update_color_legend(self):
        """Update the color legend display."""
        # Clear existing legend
        for i in reversed(range(self.legend_layout.count())):
            self.legend_layout.itemAt(i).widget().setParent(None)

        if not self.catalog_data.color_legend:
            return

        for (
            category_name,
            color_items,
        ) in self.catalog_data.color_legend.items():
            # Category header
            header = QLabel(category_name)
            font_tokens.bind(header, "font.body")
            self.legend_layout.addWidget(header)

            # Color items
            for color_info in color_items:
                item_widget = QWidget()
                item_layout = QHBoxLayout(item_widget)
                item_layout.setContentsMargins(10, 2, 2, 2)

                # Color sample
                color_label = QLabel()
                color_label.setFixedSize(20, 20)
                color_label.setStyleSheet(
                    f"background-color: {color_info.color_hex}; border: 1px solid black;"
                )
                item_layout.addWidget(color_label)

                # Icon (if accessibility mode)
                if self.accessibility_cb.isChecked():
                    icon_label = QLabel(color_info.icon)
                    item_layout.addWidget(icon_label)

                # Label
                text_label = QLabel(
                    f"{color_info.accessibility_label} - {color_info.category_name}"
                )
                item_layout.addWidget(text_label)
                item_layout.addStretch()

                self.legend_layout.addWidget(item_widget)

        self.legend_layout.addStretch()

    def _update_stats_display(self):
        """Update the statistics display."""
        if not self.catalog_data.entries:
            self.stats_text.setText("No files loaded")
            return

        stats = self.catalog_data.statistics
        stats_text = f"""Total Files: {stats.total_files:,}
Total Size: {self.catalog_data._format_size(stats.total_size)}

File Types:
"""

        for file_type, count in stats.file_type_counts.items():
            stats_text += f"  {file_type.value}: {count:,}\n"

        if stats.largest_file:
            stats_text += f"\nLargest File: {stats.largest_file.name} ({stats.largest_file.format_size()})"

        if stats.smallest_file:
            stats_text += f"\nSmallest File: {stats.smallest_file.name} ({stats.smallest_file.format_size()})"

        self.stats_text.setText(stats_text)

    def _on_sort_criteria_changed(self):
        """Handle sort criteria change."""
        if self.catalog_data.entries:
            self._apply_sort()

    def _on_color_scheme_changed(self):
        """Handle color scheme change."""
        if self.catalog_data.entries:
            self._apply_color_coding()
            self._update_file_preview()
            self._update_color_legend()

    def _on_accessibility_toggled(self):
        """Handle accessibility mode toggle."""
        if self.catalog_data.entries:
            self._apply_color_coding()
            self._update_file_preview()
            self._update_color_legend()

    def _export_catalog(self):
        """Export the catalog in the selected format."""
        if not self.catalog_data.entries:
            if Modal:
                Modal(
                    "No Data",
                    "No files to export. Please scan a directory first.",
                    ["OK"],
                    self,
                ).exec_()
            else:
                QMessageBox.warning(
                    self,
                    "No Data",
                    "No files to export. Please scan a directory first.",
                )
            return

        # Get export format
        format_map = {
            "HTML (with CSS)": ("html", HTMLExporter),
            "CSV (with metadata)": ("csv", CSVExporter),
            "JSON (structured)": ("json", JSONExporter),
        }

        format_text = self.export_format_combo.currentText()
        if format_text not in format_map:
            return

        extension, exporter_class = format_map[format_text]

        # Get output file
        default_name = f"catalog_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{extension}"
        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Catalog",
            default_name,
            f"{extension.upper()} Files (*.{extension});;All Files (*)",
        )

        if not output_path:
            return

        # Create exporter
        exporter = exporter_class()
        exporter.set_accessibility_mode(self.accessibility_cb.isChecked())

        # Start export thread
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Exporting catalog...")

        self.export_thread = ExportThread(
            self.catalog_data, exporter, Path(output_path)
        )
        self.export_thread.progress_updated.connect(self._on_export_progress)
        self.export_thread.export_completed.connect(self._on_export_completed)
        self.export_thread.export_failed.connect(self._on_export_failed)
        self.export_thread.start()

    def _on_export_progress(self, percentage: int, message: str):
        """Handle export progress updates."""
        self.progress_bar.setValue(percentage)
        self.status_label.setText(message)

        if self.hub_instance:
            self.hub_instance.update_tool_progress(
                "Advanced Catalog Generator", percentage, f"Export: {message}"
            )

    def _on_export_completed(self, output_path: str):
        """Handle export completion."""
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"Export completed: {output_path}")

        if Modal:
            Modal(
                "Export Complete",
                f"Catalog exported successfully to:\n{output_path}",
                ["OK"],
                self,
            ).exec_()
        else:
            QMessageBox.information(
                self,
                "Export Complete",
                f"Catalog exported successfully to:\n{output_path}",
            )

        # Open file if requested
        if self.open_after_export_cb.isChecked():
            import webbrowser

            webbrowser.open(f"file:///{output_path}")

        if self.hub_instance:
            self.hub_instance.update_tool_progress(
                "Advanced Catalog Generator", 100, "Export completed"
            )

    def _on_export_failed(self, error_message: str):
        """Handle export failure."""
        self.progress_bar.setVisible(False)
        self.status_label.setText("Export failed")

        if Modal:
            Modal(
                "Export Error",
                f"Failed to export catalog:\n{error_message}",
                ["OK"],
                self,
            ).exec_()
        else:
            QMessageBox.critical(
                self, "Export Error", f"Failed to export catalog:\n{error_message}"
            )

        if self.hub_instance:
            self.hub_instance.update_tool_progress(
                "Advanced Catalog Generator", 0, "Export failed"
            )

    def _new_catalog(self):
        """Start a new catalog."""
        self.catalog_data = CatalogData()
        self.current_directory = None
        self.dir_label.setText("No directory selected")
        self.file_list.clear()
        self.file_count_label.setText("0 files")
        self.stats_text.setText("No files loaded")
        self.apply_sort_btn.setEnabled(False)
        self.export_btn.setEnabled(False)
        self.status_label.setText("Ready - Select a directory to begin")

    def _save_settings(self):
        """Save current settings."""
        # Implementation for saving settings
        pass

    def _load_settings(self):
        """Load saved settings."""
        # Implementation for loading settings
        pass


def main():
    """Main entry point for standalone execution."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = AdvancedCatalogWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
