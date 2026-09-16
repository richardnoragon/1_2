#!/usr/bin/env python3
"""
PDF Parameter Dialogs - User interface dialogs for PDF operations
Provides modern, intuitive dialogs for merge, split, and sign operations
"""
from src.rfu.localization import localized_widget as _ui_widget, bind_literal as _ui_bind
from src.rfu import font_tokens

import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from PyQt5.QtCore import QSize, Qt, QThread, QTimer, pyqtSignal
from PyQt5.QtGui import (
    QColor,
    QDragEnterEvent,
    QDropEvent,
    QFont,
    QIcon,
    QPalette,
    QPixmap,
)
from PyQt5.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSlider,
    QSpinBox,
    QSplitter,
    QTabWidget,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.gui.components.buttons import PrimaryButton, SecondaryButton
from src.gui.components.inputs import TextInput
from src.gui.themes import token

PDF_FILE_FILTER = "PDF Files (*.pdf)"
ALL_FILES_FILTER = "All Files (*)"
PDF_FILES_FILTER = f"{PDF_FILE_FILTER};;{ALL_FILES_FILTER}"

# Set up logger
logger = logging.getLogger(__name__)


class DragDropListWidget(QListWidget):
    """List widget with drag and drop support for file reordering"""

    files_reordered = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setDragDropMode(QListWidget.InternalMove)
        self.setDefaultDropAction(Qt.MoveAction)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            # Handle external file drops
            files = []
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    file_path = url.toLocalFile()
                    if file_path.lower().endswith(".pdf"):
                        files.append(file_path)

            if files:
                for file_path in files:
                    item = QListWidgetItem(os.path.basename(file_path))
                    item.setData(Qt.UserRole, file_path)
                    item.setToolTip(file_path)
                    self.addItem(item)
                self.files_reordered.emit()

            event.acceptProposedAction()
        else:
            # Handle internal reordering
            super().dropEvent(event)
            self.files_reordered.emit()


class FilePreviewWidget(QWidget):
    """Widget for previewing PDF file information"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Preview label
        self.preview_label = _ui_widget(QLabel, 'Legacy.s26bfbd5c83f90db3', 'setText')
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet(
            f"""
            QLabel {{
                border: 2px dashed {token('border_light')};
                border-radius: 8px;
                padding: 20px;
                background-color: {token('surface')};
                color: {token('text_muted')};

            }}
        """
        )
        font_tokens.bind(self.preview_label, "font.body")
        self.preview_label.setMinimumHeight(120)
        layout.addWidget(self.preview_label)

        # File info
        self.info_label = QLabel("")
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet(
            f" color: {token('text_muted')};"
        )
        font_tokens.bind(self.info_label, "font.body")
        layout.addWidget(self.info_label)

    def update_preview(self, file_path: str, page_count: int = 0, file_size: int = 0):
        """Update preview with file information"""
        if file_path:
            filename = os.path.basename(file_path)
            self.preview_label.setText(f"📄 {filename}")

            # Format file size
            if file_size > 0:
                if file_size < 1024:
                    size_str = f"{file_size} B"
                elif file_size < 1024 * 1024:
                    size_str = f"{file_size / 1024:.1f} KB"
                else:
                    size_str = f"{file_size / (1024 * 1024):.1f} MB"
            else:
                size_str = "Unknown size"

            info_text = f"Pages: {page_count}\nSize: {size_str}"
            self.info_label.setText(info_text)
        else:
            self.preview_label.setText("No file selected")
            self.info_label.setText("")


class PDFMergeDialog(QDialog):
    """Dialog for PDF merge operation parameters"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.input_files = []
        self.output_file = ""
        self.merge_options = {}

        _ui_bind(self, 'setWindowTitle', 'Legacy.sbac5b212c95d0405')
        self.setModal(True)
        self.resize(800, 600)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        splitter.addWidget(self._build_left_panel())
        splitter.addWidget(self._build_right_panel())
        splitter.setSizes([400, 400])

        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        self.cancel_btn = _ui_widget(SecondaryButton, 'Legacy.s19766ed6ccb2f4a3', 'setText')
        _ui_bind(self.cancel_btn, 'setAccessibleName', 'Legacy.sd2c4bacb083314c5')
        self.cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_btn)

        self.merge_btn = _ui_widget(PrimaryButton, 'Legacy.s43d1539b7596aa88', 'setText')
        _ui_bind(self.merge_btn, 'setAccessibleName', 'Legacy.s13ef4c4313541340')
        self.merge_btn.clicked.connect(self.accept)
        self.merge_btn.setEnabled(False)
        self.merge_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {token('button_primary')};
                color: {token('text_on_primary')};
                font-weight: bold;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {token('button_primary_hover')};
            }}
            QPushButton:disabled {{
                background-color: {token('text_disabled')};
            }}
        """
        )
        buttons_layout.addWidget(self.merge_btn)

        layout.addLayout(buttons_layout)
        self.apply_styling()

    def _build_left_panel(self) -> QWidget:
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        files_group = _ui_widget(QGroupBox, 'Legacy.sb2cd7c00fb28900d', 'setTitle')
        files_layout = QVBoxLayout(files_group)
        self.file_list = DragDropListWidget()
        self.file_list.files_reordered.connect(self.on_files_reordered)
        self.file_list.itemSelectionChanged.connect(self.on_file_selected)
        files_layout.addWidget(self.file_list)

        file_buttons_layout = QHBoxLayout()
        self.add_files_btn = _ui_widget(SecondaryButton, 'Legacy.s7e69772d579a9448', 'setText')
        _ui_bind(self.add_files_btn, 'setAccessibleName', 'Legacy.sc76572f3277f0db4')
        self.add_files_btn.clicked.connect(self.add_files)
        file_buttons_layout.addWidget(self.add_files_btn)

        self.remove_file_btn = _ui_widget(SecondaryButton, 'Legacy.sc3812fc4acb861d5', 'setText')
        _ui_bind(self.remove_file_btn, 'setAccessibleName', 'Legacy.s15a64ac455e78ba9')
        self.remove_file_btn.clicked.connect(self.remove_selected_file)
        self.remove_file_btn.setEnabled(False)
        file_buttons_layout.addWidget(self.remove_file_btn)

        self.move_up_btn = _ui_widget(SecondaryButton, 'Legacy.sd2e966bf8db85620', 'setText')
        _ui_bind(self.move_up_btn, 'setAccessibleName', 'Legacy.s00c5f50b2179d252')
        self.move_up_btn.clicked.connect(self.move_file_up)
        self.move_up_btn.setEnabled(False)
        file_buttons_layout.addWidget(self.move_up_btn)

        self.move_down_btn = _ui_widget(SecondaryButton, 'Legacy.s07a2abcd3189716d', 'setText')
        _ui_bind(self.move_down_btn, 'setAccessibleName', 'Legacy.s5e5c23786326d221')
        self.move_down_btn.clicked.connect(self.move_file_down)
        self.move_down_btn.setEnabled(False)
        file_buttons_layout.addWidget(self.move_down_btn)

        files_layout.addLayout(file_buttons_layout)
        left_layout.addWidget(files_group)

        options_group = _ui_widget(QGroupBox, 'Legacy.sbd13c923ae59829f', 'setTitle')
        options_layout = QFormLayout(options_group)
        self.preserve_bookmarks_cb = _ui_widget(QCheckBox, 'Legacy.sc20d60fcbccc76d7', 'setText')
        _ui_bind(self.preserve_bookmarks_cb, 'setAccessibleName', 'Legacy.sc20d60fcbccc76d7')
        self.preserve_bookmarks_cb.setMinimumHeight(44)
        self.preserve_bookmarks_cb.setChecked(True)
        options_layout.addRow(self.preserve_bookmarks_cb)

        self.preserve_metadata_cb = _ui_widget(QCheckBox, 'Legacy.s9d577b82b5d3ce25', 'setText')
        _ui_bind(self.preserve_metadata_cb, 'setAccessibleName', 'Legacy.s9d577b82b5d3ce25')
        self.preserve_metadata_cb.setMinimumHeight(44)
        self.preserve_metadata_cb.setChecked(True)
        options_layout.addRow(self.preserve_metadata_cb)

        self.optimize_output_cb = _ui_widget(QCheckBox, 'Legacy.s3c6477d617f72da6', 'setText')
        _ui_bind(self.optimize_output_cb, 'setAccessibleName', 'Legacy.s3c6477d617f72da6')
        self.optimize_output_cb.setMinimumHeight(44)
        options_layout.addRow(self.optimize_output_cb)

        self.custom_ranges_cb = _ui_widget(QCheckBox, 'Legacy.s2a640752e57ef36d', 'setText')
        _ui_bind(self.custom_ranges_cb, 'setAccessibleName', 'Legacy.s2a640752e57ef36d')
        self.custom_ranges_cb.setMinimumHeight(44)
        self.custom_ranges_cb.toggled.connect(self.toggle_custom_ranges)
        options_layout.addRow(self.custom_ranges_cb)
        left_layout.addWidget(options_group)

        output_group = _ui_widget(QGroupBox, 'Legacy.sb2439bcb8dee14b6', 'setTitle')
        output_layout = QFormLayout(output_group)
        output_file_layout = QHBoxLayout()
        self.output_file_edit = TextInput(
            "Merged Output File",
            "Select output file...",
            accessible_name="Merged output file",
        )
        output_file_layout.addWidget(self.output_file_edit)

        self.browse_output_btn = _ui_widget(SecondaryButton, 'Legacy.s3227aa9666253f7a', 'setText')
        _ui_bind(self.browse_output_btn, 'setAccessibleName', 'Legacy.s288a747d781539e2')
        self.browse_output_btn.clicked.connect(self.browse_output_file)
        output_file_layout.addWidget(self.browse_output_btn)

        output_layout.addRow("Output file:", output_file_layout)
        left_layout.addWidget(output_group)
        return left_panel

    def _build_right_panel(self) -> QWidget:
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        preview_group = _ui_widget(QGroupBox, 'Legacy.s324b134f57c70c72', 'setTitle')
        preview_layout = QVBoxLayout(preview_group)
        self.preview_widget = FilePreviewWidget()
        preview_layout.addWidget(self.preview_widget)

        self.details_text = QTextEdit()
        _ui_bind(self.details_text, 'setAccessibleName', 'Legacy.s1c55b4b480437b49')
        self.details_text.setMaximumHeight(100)
        self.details_text.setReadOnly(True)
        preview_layout.addWidget(self.details_text)
        right_layout.addWidget(preview_group)

        self.ranges_group = _ui_widget(QGroupBox, 'Legacy.s313beedd21da1799', 'setTitle')
        self.ranges_group.setVisible(False)
        ranges_layout = QVBoxLayout(self.ranges_group)
        ranges_help = _ui_widget(QLabel, 'Legacy.s492603ffce52e861', 'setText')
        ranges_help.setWordWrap(True)
        ranges_help.setStyleSheet(f"color: {token('text_muted')}; ")
        font_tokens.bind(ranges_help, "font.body")
        ranges_layout.addWidget(ranges_help)

        self.ranges_list = QListWidget()
        _ui_bind(self.ranges_list, 'setAccessibleName', 'Legacy.s59799a0b4e8e376c')
        ranges_layout.addWidget(self.ranges_list)
        right_layout.addWidget(self.ranges_group)
        return right_panel

    def apply_styling(self):
        """Apply modern styling to the dialog"""
        self.setStyleSheet(
            f"""
            QDialog {{
                background-color: {token('window_background')};

            }}
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {token('border_light')};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
            QPushButton {{
                padding: 6px 12px;
                border: 1px solid {token('border_light')};
                border-radius: 4px;
                background-color: {token('surface')};
            }}
            QPushButton:hover {{
                background-color: {token('color_bg_tint')};
            }}
            QListWidget {{
                border: 1px solid {token('border_light')};
                border-radius: 4px;
                background-color: {token('window_background')};
            }}
            QLineEdit {{
                padding: 6px;
                border: 1px solid {token('border_light')};
                border-radius: 4px;
            }}
        """
        )
        font_tokens.bind(self, "font.body")

    def add_files(self):
        """Add PDF files to the merge list"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select PDF Files to Merge",
            "",
            PDF_FILES_FILTER,
        )

        if files:
            for file_path in files:
                # Check if file already exists in list
                existing = False
                for i in range(self.file_list.count()):
                    item = self.file_list.item(i)
                    if item.data(Qt.UserRole) == file_path:
                        existing = True
                        break

                if not existing:
                    item = QListWidgetItem(os.path.basename(file_path))
                    item.setData(Qt.UserRole, file_path)
                    item.setToolTip(file_path)
                    self.file_list.addItem(item)

            self.update_file_list()
            self.update_ranges_list()

    def remove_selected_file(self):
        """Remove selected file from the list"""
        current_row = self.file_list.currentRow()
        if current_row >= 0:
            self.file_list.takeItem(current_row)
            self.update_file_list()
            self.update_ranges_list()

    def move_file_up(self):
        """Move selected file up in the list"""
        current_row = self.file_list.currentRow()
        if current_row > 0:
            item = self.file_list.takeItem(current_row)
            self.file_list.insertItem(current_row - 1, item)
            self.file_list.setCurrentRow(current_row - 1)
            self.update_file_list()

    def move_file_down(self):
        """Move selected file down in the list"""
        current_row = self.file_list.currentRow()
        if current_row < self.file_list.count() - 1:
            item = self.file_list.takeItem(current_row)
            self.file_list.insertItem(current_row + 1, item)
            self.file_list.setCurrentRow(current_row + 1)
            self.update_file_list()

    def on_files_reordered(self):
        """Handle file reordering"""
        self.update_file_list()
        self.update_ranges_list()

    def on_file_selected(self):
        """Handle file selection in the list"""
        current_item = self.file_list.currentItem()
        has_selection = current_item is not None

        self.remove_file_btn.setEnabled(has_selection)
        self.move_up_btn.setEnabled(has_selection and self.file_list.currentRow() > 0)
        self.move_down_btn.setEnabled(
            has_selection and self.file_list.currentRow() < self.file_list.count() - 1
        )

        if current_item:
            file_path = current_item.data(Qt.UserRole)
            try:
                # Get file info for preview
                file_size = os.path.getsize(file_path)
                # This would require PDF validation to get page count
                # For now, show basic info
                self.preview_widget.update_preview(file_path, 0, file_size)
                self.details_text.setText(f"File: {file_path}")
            except Exception as e:
                logger.warning(f"Error getting file info: {e}")
                self.preview_widget.update_preview(file_path, 0, 0)

    def update_file_list(self):
        """Update the internal file list and UI state"""
        self.input_files = []
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            file_path = item.data(Qt.UserRole)
            self.input_files.append(file_path)

        # Enable/disable merge button
        has_files = len(self.input_files) >= 2
        has_output = bool(self.output_file_edit.text().strip())
        self.merge_btn.setEnabled(has_files and has_output)

        # Update details
        if self.input_files:
            details = f"Files to merge: {len(self.input_files)}\n"
            details += "\n".join(
                [
                    f"{i+1}. {os.path.basename(f)}"
                    for i, f in enumerate(self.input_files)
                ]
            )
            self.details_text.setText(details)

    def update_ranges_list(self):
        """Update the custom ranges list"""
        self.ranges_list.clear()
        for file_path in self.input_files:
            filename = os.path.basename(file_path)
            item = QListWidgetItem(f"{filename}: ")
            item.setData(Qt.UserRole, file_path)
            self.ranges_list.addItem(item)

    def toggle_custom_ranges(self, enabled: bool):
        """Toggle custom page ranges section"""
        self.ranges_group.setVisible(enabled)

    def browse_output_file(self):
        """Browse for output file location"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Merged PDF As",
            "merged_document.pdf",
            PDF_FILES_FILTER,
        )

        if file_path:
            self.output_file_edit.setText(file_path)
            self.update_file_list()  # Update merge button state

    def get_merge_options(self) -> Dict[str, Any]:
        """Get merge options from the dialog"""
        options = {
            "preserve_bookmarks": self.preserve_bookmarks_cb.isChecked(),
            "preserve_metadata": self.preserve_metadata_cb.isChecked(),
            "optimize_output": self.optimize_output_cb.isChecked(),
            "page_ranges": {},
        }

        # Get custom page ranges if enabled
        if self.custom_ranges_cb.isChecked():
            for i in range(self.ranges_list.count()):
                item = self.ranges_list.item(i)
                file_path = item.data(Qt.UserRole)
                # This would need implementation to parse range text
                # For now, include all pages
                options["page_ranges"][file_path] = None

        return options

    def get_input_files(self) -> List[str]:
        """Get list of input files"""
        return self.input_files.copy()

    def get_output_file(self) -> str:
        """Get output file path"""
        return self.output_file_edit.text().strip()


class PDFSplitDialog(QDialog):
    """Dialog for PDF split operation parameters"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.input_file = ""
        self.output_directory = ""
        self.split_options = {}

        _ui_bind(self, 'setWindowTitle', 'Legacy.s7a49bebdd6f720a1')
        self.setModal(True)
        self.resize(700, 500)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Input file section
        input_group = _ui_widget(QGroupBox, 'Legacy.s87e183ba430af487', 'setTitle')
        input_layout = QFormLayout(input_group)

        input_file_layout = QHBoxLayout()
        self.input_file_edit = TextInput(
            "Input PDF File",
            "Select PDF file to split...",
            accessible_name="Input PDF file to split",
        )
        self.input_file_edit.textChanged.connect(self.on_input_file_changed)
        input_file_layout.addWidget(self.input_file_edit)

        self.browse_input_btn = _ui_widget(SecondaryButton, 'Legacy.s3227aa9666253f7a', 'setText')
        _ui_bind(self.browse_input_btn, 'setAccessibleName', 'Legacy.s91ae8b59118f2781')
        self.browse_input_btn.clicked.connect(self.browse_input_file)
        input_file_layout.addWidget(self.browse_input_btn)

        input_layout.addRow("PDF File:", input_file_layout)

        self.file_info_label = QLabel("")
        self.file_info_label.setStyleSheet(
            f"color: {token('text_muted')}; "
        )
        font_tokens.bind(self.file_info_label, "font.body")
        input_layout.addRow(self.file_info_label)

        layout.addWidget(input_group)

        # Split method section
        method_group = _ui_widget(QGroupBox, 'Legacy.s1b4eccc4f009a2da', 'setTitle')
        method_layout = QVBoxLayout(method_group)

        self.method_group = QButtonGroup()

        # By page count
        self.pages_radio = _ui_widget(QRadioButton, 'Legacy.s62e1c4f470a4f4b2', 'setText')
        _ui_bind(self.pages_radio, 'setAccessibleName', 'Legacy.s62a46e9cf5484ad7')
        self.pages_radio.setMinimumHeight(44)
        self.pages_radio.setChecked(True)
        self.pages_radio.toggled.connect(self.on_method_changed)
        self.method_group.addButton(self.pages_radio)
        method_layout.addWidget(self.pages_radio)

        pages_layout = QHBoxLayout()
        pages_layout.addSpacing(20)
        pages_layout.addWidget(_ui_widget(QLabel, 'Legacy.s513129314fbd6430', 'setText'))
        self.pages_spinbox = QSpinBox()
        _ui_bind(self.pages_spinbox, 'setAccessibleName', 'Legacy.s176a703e9437c937')
        self.pages_spinbox.setMinimumHeight(44)
        self.pages_spinbox.setMinimum(1)
        self.pages_spinbox.setMaximum(1000)
        self.pages_spinbox.setValue(1)
        pages_layout.addWidget(self.pages_spinbox)
        pages_layout.addStretch()
        method_layout.addLayout(pages_layout)

        # By page ranges
        self.ranges_radio = _ui_widget(QRadioButton, 'Legacy.s6f63b08cbd1514e8', 'setText')
        _ui_bind(self.ranges_radio, 'setAccessibleName', 'Legacy.s93cc2fc1a2ca3552')
        self.ranges_radio.setMinimumHeight(44)
        self.ranges_radio.toggled.connect(self.on_method_changed)
        self.method_group.addButton(self.ranges_radio)
        method_layout.addWidget(self.ranges_radio)

        ranges_layout = QHBoxLayout()
        ranges_layout.addSpacing(20)
        ranges_layout.addWidget(_ui_widget(QLabel, 'Legacy.sa4a045c02a534f52', 'setText'))
        self.ranges_edit = TextInput(
            "Page Ranges",
            "e.g., 1-10,11-20,21-30",
            accessible_name="Page ranges to split at",
        )
        self.ranges_edit.setEnabled(False)
        ranges_layout.addWidget(self.ranges_edit)
        method_layout.addLayout(ranges_layout)

        # By bookmarks
        self.bookmarks_radio = _ui_widget(QRadioButton, 'Legacy.s63eaefdbf33c3e7d', 'setText')
        _ui_bind(self.bookmarks_radio, 'setAccessibleName', 'Legacy.s1ab781a278e82dca')
        self.bookmarks_radio.setMinimumHeight(44)
        self.bookmarks_radio.toggled.connect(self.on_method_changed)
        self.method_group.addButton(self.bookmarks_radio)
        method_layout.addWidget(self.bookmarks_radio)

        # By file size
        self.size_radio = _ui_widget(QRadioButton, 'Legacy.sb02156ab99e52549', 'setText')
        _ui_bind(self.size_radio, 'setAccessibleName', 'Legacy.s65606affebc4ae70')
        self.size_radio.setMinimumHeight(44)
        self.size_radio.toggled.connect(self.on_method_changed)
        self.method_group.addButton(self.size_radio)
        method_layout.addWidget(self.size_radio)

        size_layout = QHBoxLayout()
        size_layout.addSpacing(20)
        size_layout.addWidget(_ui_widget(QLabel, 'Legacy.s48818834a3c076c3', 'setText'))
        self.size_spinbox = QSpinBox()
        _ui_bind(self.size_spinbox, 'setAccessibleName', 'Legacy.s9c5e4395126dc80c')
        self.size_spinbox.setMinimumHeight(44)
        self.size_spinbox.setMinimum(1)
        self.size_spinbox.setMaximum(100)
        self.size_spinbox.setValue(5)
        self.size_spinbox.setEnabled(False)
        size_layout.addWidget(self.size_spinbox)
        size_layout.addWidget(_ui_widget(QLabel, 'Legacy.s1d09f6fa23235881', 'setText'))
        size_layout.addStretch()
        method_layout.addLayout(size_layout)

        layout.addWidget(method_group)

        # Preview section
        preview_group = _ui_widget(QGroupBox, 'Legacy.s324b134f57c70c72', 'setTitle')
        preview_layout = QVBoxLayout(preview_group)

        self.preview_text = QTextEdit()
        _ui_bind(self.preview_text, 'setAccessibleName', 'Legacy.s8238aafad32848b1')
        self.preview_text.setMaximumHeight(100)
        self.preview_text.setReadOnly(True)
        _ui_bind(self.preview_text, 'setPlaceholderText', 'Legacy.sbf2283a271ae5718')
        preview_layout.addWidget(self.preview_text)

        layout.addWidget(preview_group)

        # Output section
        output_group = _ui_widget(QGroupBox, 'Legacy.sb2439bcb8dee14b6', 'setTitle')
        output_layout = QFormLayout(output_group)

        output_dir_layout = QHBoxLayout()
        self.output_dir_edit = TextInput(
            "Split Output Directory",
            "Select output directory...",
            accessible_name="Split output directory",
        )
        self.output_dir_edit.textChanged.connect(self.update_split_button)
        output_dir_layout.addWidget(self.output_dir_edit)

        self.browse_output_btn = _ui_widget(SecondaryButton, 'Legacy.s3227aa9666253f7a', 'setText')
        _ui_bind(self.browse_output_btn, 'setAccessibleName', 'Legacy.sc615df9b2f4f7a36')
        self.browse_output_btn.clicked.connect(self.browse_output_directory)
        output_dir_layout.addWidget(self.browse_output_btn)

        output_layout.addRow("Output Directory:", output_dir_layout)

        self.naming_edit = TextInput(
            "Naming Pattern",
            "split_{index}.pdf",
            accessible_name="Split output file naming pattern",
        )
        output_layout.addRow(self.naming_edit)

        layout.addWidget(output_group)

        # Dialog buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        self.cancel_btn = _ui_widget(SecondaryButton, 'Legacy.s19766ed6ccb2f4a3', 'setText')
        _ui_bind(self.cancel_btn, 'setAccessibleName', 'Legacy.s7428753b7bb36bfa')
        self.cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_btn)

        self.split_btn = _ui_widget(PrimaryButton, 'Legacy.s4f1b846cb144435e', 'setText')
        _ui_bind(self.split_btn, 'setAccessibleName', 'Legacy.s869441f8aa22d755')
        self.split_btn.clicked.connect(self.accept)
        self.split_btn.setEnabled(False)
        self.split_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {token('semantic_success')};
                color: {token('text_on_primary')};
                font-weight: bold;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {token('semantic_success_hover')};
            }}
            QPushButton:disabled {{
                background-color: {token('text_disabled')};
            }}
        """
        )
        buttons_layout.addWidget(self.split_btn)

        layout.addLayout(buttons_layout)

        self.apply_styling()

    def apply_styling(self):
        """Apply modern styling to the dialog"""
        self.setStyleSheet(
            f"""
            QDialog {{
                background-color: {token('window_background')};

            }}
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {token('border_light')};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
            QPushButton {{
                padding: 6px 12px;
                border: 1px solid {token('border_light')};
                border-radius: 4px;
                background-color: {token('surface')};
            }}
            QPushButton:hover {{
                background-color: {token('color_bg_tint')};
            }}
            QLineEdit {{
                padding: 6px;
                border: 1px solid {token('border_light')};
                border-radius: 4px;
            }}
            QTextEdit {{
                border: 1px solid {token('border_light')};
                border-radius: 4px;
            }}
        """
        )
        font_tokens.bind(self, "font.body")

    def browse_input_file(self):
        """Browse for input PDF file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select PDF File to Split",
            "",
            "PDF Files (*.pdf);;All Files (*)",
        )

        if file_path:
            self.input_file_edit.setText(file_path)

    def browse_output_directory(self):
        """Browse for output directory"""
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory")

        if directory:
            self.output_dir_edit.setText(directory)

    def on_input_file_changed(self):
        """Handle input file change"""
        file_path = self.input_file_edit.text().strip()
        if file_path and os.path.exists(file_path):
            try:
                # Get file info (would need PDF validation for page count)
                file_size = os.path.getsize(file_path)
                size_str = f"{file_size / (1024 * 1024):.1f} MB"
                self.file_info_label.setText(f"File size: {size_str}")

                # Update preview
                self.update_preview()
            except Exception as e:
                logger.warning(f"Error getting file info: {e}")
                self.file_info_label.setText("Error reading file")
        else:
            self.file_info_label.setText("")

        self.update_split_button()

    def on_method_changed(self):
        """Handle split method change"""
        # Enable/disable controls based on selected method
        self.ranges_edit.setEnabled(self.ranges_radio.isChecked())
        self.size_spinbox.setEnabled(self.size_radio.isChecked())

        # Update preview
        self.update_preview()

    def update_preview(self):
        """Update split preview"""
        if not self.input_file_edit.text().strip():
            self.preview_text.clear()
            return

        preview_text = ""

        if self.pages_radio.isChecked():
            pages_per_file = self.pages_spinbox.value()
            # This would need actual page count from PDF
            estimated_files = max(1, 100 // pages_per_file)  # Assume 100 pages
            preview_text = f"Estimated output: {estimated_files} files\n"
            preview_text += f"Pages per file: {pages_per_file}"

        elif self.ranges_radio.isChecked():
            ranges_text = self.ranges_edit.text().strip()
            if ranges_text:
                ranges = ranges_text.split(",")
                preview_text = f"Output files: {len(ranges)}\n"
                preview_text += f"Ranges: {ranges_text}"
            else:
                preview_text = "Enter page ranges (e.g., 1-10,11-20)"

        elif self.bookmarks_radio.isChecked():
            preview_text = "Will split by bookmarks/chapters\n"
            preview_text += "(Requires PDF with bookmarks)"

        elif self.size_radio.isChecked():
            max_size = self.size_spinbox.value()
            preview_text = f"Max size per file: {max_size} MB\n"
            preview_text += "Estimated files: (depends on content)"

        self.preview_text.setText(preview_text)

    def update_split_button(self):
        """Update split button state"""
        has_input = bool(self.input_file_edit.text().strip())
        has_output = bool(self.output_dir_edit.text().strip())
        self.split_btn.setEnabled(has_input and has_output)

    def get_split_options(self) -> Dict[str, Any]:
        """Get split options from the dialog"""
        options = {
            "naming_pattern": self.naming_edit.text().strip() or "split_{index}.pdf"
        }

        if self.pages_radio.isChecked():
            options["method"] = "pages"
            options["pages_per_file"] = self.pages_spinbox.value()
        elif self.ranges_radio.isChecked():
            options["method"] = "ranges"
            ranges_text = self.ranges_edit.text().strip()
            # Parse ranges (simplified - would need more robust parsing)
            custom_ranges = []
            if ranges_text:
                for range_str in ranges_text.split(","):
                    range_str = range_str.strip()
                    if "-" in range_str:
                        start, end = range_str.split("-", 1)
                        try:
                            start_page = int(start.strip()) - 1  # Convert to 0-based
                            end_page = int(end.strip()) - 1
                            custom_ranges.append((start_page, end_page))
                        except ValueError:
                            continue
            options["custom_ranges"] = custom_ranges
        elif self.bookmarks_radio.isChecked():
            options["method"] = "bookmarks"
        elif self.size_radio.isChecked():
            options["method"] = "size"
            options["max_size_mb"] = self.size_spinbox.value()

        return options

    def get_input_file(self) -> str:
        """Get input file path"""
        return self.input_file_edit.text().strip()

    def get_output_directory(self) -> str:
        """Get output directory path"""
        return self.output_dir_edit.text().strip()


class PDFSignDialog(QDialog):
    """Dialog for PDF sign operation parameters"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.input_file = ""
        self.signature_file = ""
        self.output_file = ""
        self.sign_options = {}

        _ui_bind(self, 'setWindowTitle', 'Legacy.s69a77e93050118ee')
        self.setModal(True)
        self.resize(600, 500)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Input files section
        files_group = _ui_widget(QGroupBox, 'Legacy.sabc7e9892806b047', 'setTitle')
        files_layout = QFormLayout(files_group)

        # PDF file
        pdf_file_layout = QHBoxLayout()
        self.pdf_file_edit = TextInput(
            "PDF File",
            "Select PDF file to sign...",
            accessible_name="PDF file to sign",
        )
        self.pdf_file_edit.textChanged.connect(self.update_sign_button)
        pdf_file_layout.addWidget(self.pdf_file_edit)

        self.browse_pdf_btn = _ui_widget(SecondaryButton, 'Legacy.s3227aa9666253f7a', 'setText')
        _ui_bind(self.browse_pdf_btn, 'setAccessibleName', 'Legacy.s1f8deb9bf96c614f')
        self.browse_pdf_btn.clicked.connect(self.browse_pdf_file)
        pdf_file_layout.addWidget(self.browse_pdf_btn)

        files_layout.addRow("PDF File:", pdf_file_layout)

        # Signature file
        sig_file_layout = QHBoxLayout()
        self.sig_file_edit = TextInput(
            "Signature File",
            "Select signature image...",
            accessible_name="Signature image file",
        )
        self.sig_file_edit.textChanged.connect(self.update_sign_button)
        sig_file_layout.addWidget(self.sig_file_edit)

        self.browse_sig_btn = _ui_widget(SecondaryButton, 'Legacy.s3227aa9666253f7a', 'setText')
        _ui_bind(self.browse_sig_btn, 'setAccessibleName', 'Legacy.saeeaa9a5c56800e7')
        self.browse_sig_btn.clicked.connect(self.browse_signature_file)
        sig_file_layout.addWidget(self.browse_sig_btn)

        files_layout.addRow("Signature:", sig_file_layout)

        layout.addWidget(files_group)

        # Create splitter for position and preview
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)

        # Left panel - Position and options
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # Position section
        position_group = _ui_widget(QGroupBox, 'Legacy.s6d031af10da7a25e', 'setTitle')
        position_layout = QGridLayout(position_group)

        self.position_group = QButtonGroup()

        positions = [
            ("Top Left", "top_left", 0, 0),
            ("Top Right", "top_right", 0, 1),
            ("Center", "center", 1, 0),
            ("Custom", "custom", 1, 1),
            ("Bottom Left", "bottom_left", 2, 0),
            ("Bottom Right", "bottom_right", 2, 1),
        ]

        for text, value, row, col in positions:
            radio = QRadioButton(text)
            radio.setAccessibleName(f"Position: {text}")
            radio.setMinimumHeight(44)
            radio.setProperty("position_value", value)
            if value == "bottom_right":
                radio.setChecked(True)
            self.position_group.addButton(radio)
            position_layout.addWidget(radio, row, col)

        # Custom coordinates
        custom_layout = QHBoxLayout()
        custom_layout.addWidget(_ui_widget(QLabel, 'Legacy.s939fc7d2410705f9', 'setText'))
        self.custom_x_spin = QSpinBox()
        _ui_bind(self.custom_x_spin, 'setAccessibleName', 'Legacy.sc832d561b54c0a4d')
        self.custom_x_spin.setMinimumHeight(44)
        self.custom_x_spin.setRange(0, 1000)
        self.custom_x_spin.setValue(100)
        self.custom_x_spin.setEnabled(False)
        custom_layout.addWidget(self.custom_x_spin)

        custom_layout.addWidget(_ui_widget(QLabel, 'Legacy.s841ceee9c2d2e386', 'setText'))
        self.custom_y_spin = QSpinBox()
        _ui_bind(self.custom_y_spin, 'setAccessibleName', 'Legacy.s3ecbf805feaa8391')
        self.custom_y_spin.setMinimumHeight(44)
        self.custom_y_spin.setRange(0, 1000)
        self.custom_y_spin.setValue(100)
        self.custom_y_spin.setEnabled(False)
        custom_layout.addWidget(self.custom_y_spin)

        position_layout.addLayout(custom_layout, 3, 0, 1, 2)

        # Connect position change
        self.position_group.buttonToggled.connect(self.on_position_changed)

        left_layout.addWidget(position_group)

        # Pages section
        pages_group = _ui_widget(QGroupBox, 'Legacy.scc7f571a2b00d8f5', 'setTitle')
        pages_layout = QVBoxLayout(pages_group)

        self.pages_group = QButtonGroup()

        self.all_pages_radio = _ui_widget(QRadioButton, 'Legacy.s903542125c003f8f', 'setText')
        _ui_bind(self.all_pages_radio, 'setAccessibleName', 'Legacy.sa293cb858ee48545')
        self.all_pages_radio.setMinimumHeight(44)
        self.all_pages_radio.setChecked(True)
        self.pages_group.addButton(self.all_pages_radio)
        pages_layout.addWidget(self.all_pages_radio)

        self.first_page_radio = _ui_widget(QRadioButton, 'Legacy.sb881647b7191c901', 'setText')
        _ui_bind(self.first_page_radio, 'setAccessibleName', 'Legacy.s5366dccd9ef0558e')
        self.first_page_radio.setMinimumHeight(44)
        self.pages_group.addButton(self.first_page_radio)
        pages_layout.addWidget(self.first_page_radio)

        self.last_page_radio = _ui_widget(QRadioButton, 'Legacy.s38133d2e747c541a', 'setText')
        _ui_bind(self.last_page_radio, 'setAccessibleName', 'Legacy.s0fab69634a890490')
        self.last_page_radio.setMinimumHeight(44)
        self.pages_group.addButton(self.last_page_radio)
        pages_layout.addWidget(self.last_page_radio)

        self.custom_pages_radio = _ui_widget(QRadioButton, 'Legacy.s06dd8a91390b2c38', 'setText')
        _ui_bind(self.custom_pages_radio, 'setAccessibleName', 'Legacy.s8b068714e4b3c056')
        self.custom_pages_radio.setMinimumHeight(44)
        self.pages_group.addButton(self.custom_pages_radio)
        pages_layout.addWidget(self.custom_pages_radio)

        custom_pages_layout = QHBoxLayout()
        custom_pages_layout.addSpacing(20)
        self.custom_pages_edit = TextInput(
            "Custom Pages",
            "e.g., 1,3,5",
            accessible_name="Custom page numbers to sign",
        )
        self.custom_pages_edit.setEnabled(False)
        custom_pages_layout.addWidget(self.custom_pages_edit)
        pages_layout.addLayout(custom_pages_layout)

        self.pages_group.buttonToggled.connect(self.on_pages_changed)

        left_layout.addWidget(pages_group)

        # Options section
        options_group = _ui_widget(QGroupBox, 'Legacy.sd0db8b5e364b6989', 'setTitle')
        options_layout = QFormLayout(options_group)

        # Size
        size_layout = QHBoxLayout()
        self.width_spin = QSpinBox()
        _ui_bind(self.width_spin, 'setAccessibleName', 'Legacy.sd53c9c874144f37c')
        self.width_spin.setMinimumHeight(44)
        self.width_spin.setRange(10, 500)
        self.width_spin.setValue(100)
        self.width_spin.setSuffix(" pt")
        size_layout.addWidget(self.width_spin)

        size_layout.addWidget(_ui_widget(QLabel, 'Legacy.s8db71ed28b0f2f14', 'setText'))

        self.height_spin = QSpinBox()
        _ui_bind(self.height_spin, 'setAccessibleName', 'Legacy.sa847d4babec4bde5')
        self.height_spin.setMinimumHeight(44)
        self.height_spin.setRange(10, 500)
        self.height_spin.setValue(50)
        self.height_spin.setSuffix(" pt")
        size_layout.addWidget(self.height_spin)

        options_layout.addRow("Size:", size_layout)

        # Transparency
        self.transparency_slider = QSlider(Qt.Horizontal)
        _ui_bind(self.transparency_slider, 'setAccessibleName', 'Legacy.s47363504883f23b0')
        self.transparency_slider.setMinimumHeight(44)
        self.transparency_slider.setRange(0, 100)
        self.transparency_slider.setValue(80)
        self.transparency_slider.valueChanged.connect(self.update_transparency_label)

        transparency_layout = QHBoxLayout()
        transparency_layout.addWidget(self.transparency_slider)
        self.transparency_label = _ui_widget(QLabel, 'Legacy.sf39dda09980ef9a6', 'setText')
        transparency_layout.addWidget(self.transparency_label)

        options_layout.addRow("Transparency:", transparency_layout)

        # Digital signature
        self.digital_sig_cb = _ui_widget(QCheckBox, 'Legacy.s166ec6598ee3d2b5', 'setText')
        _ui_bind(self.digital_sig_cb, 'setAccessibleName', 'Legacy.seffad318a98e2686')
        self.digital_sig_cb.setMinimumHeight(44)
        self.digital_sig_cb.toggled.connect(self.toggle_certificate)
        options_layout.addRow(self.digital_sig_cb)

        # Certificate file
        cert_layout = QHBoxLayout()
        self.cert_file_edit = TextInput(
            "Certificate File",
            "Select certificate file...",
            accessible_name="Certificate file for digital signature",
        )
        self.cert_file_edit.setEnabled(False)
        cert_layout.addWidget(self.cert_file_edit)

        self.browse_cert_btn = _ui_widget(SecondaryButton, 'Legacy.s3227aa9666253f7a', 'setText')
        _ui_bind(self.browse_cert_btn, 'setAccessibleName', 'Legacy.s0782eb8dbd434fda')
        self.browse_cert_btn.clicked.connect(self.browse_certificate_file)
        self.browse_cert_btn.setEnabled(False)
        cert_layout.addWidget(self.browse_cert_btn)

        options_layout.addRow("Certificate:", cert_layout)

        left_layout.addWidget(options_group)

        splitter.addWidget(left_panel)

        # Right panel - Preview
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        preview_group = _ui_widget(QGroupBox, 'Legacy.s324b134f57c70c72', 'setTitle')
        preview_layout = QVBoxLayout(preview_group)

        # Preview area (placeholder)
        self.preview_label = _ui_widget(QLabel, 'Legacy.s0a44b1414f67ff5d', 'setText')
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet(
            f"""
            QLabel {{
                border: 2px dashed {token('border_light')};
                border-radius: 8px;
                padding: 40px;
                background-color: {token('surface')};
                color: {token('text_muted')};

            }}
        """
        )
        font_tokens.bind(self.preview_label, "font.body")
        self.preview_label.setMinimumHeight(200)
        preview_layout.addWidget(self.preview_label)

        right_layout.addWidget(preview_group)

        splitter.addWidget(right_panel)
        splitter.setSizes([350, 250])

        # Output section
        output_group = _ui_widget(QGroupBox, 'Legacy.sb2439bcb8dee14b6', 'setTitle')
        output_layout = QFormLayout(output_group)

        output_file_layout = QHBoxLayout()
        self.output_file_edit = TextInput(
            "Signed Output File",
            "Output file will be auto-generated...",
            accessible_name="Signed output file",
        )
        self.output_file_edit.textChanged.connect(self.update_sign_button)
        output_file_layout.addWidget(self.output_file_edit)

        self.browse_output_btn = _ui_widget(SecondaryButton, 'Legacy.s3227aa9666253f7a', 'setText')
        _ui_bind(self.browse_output_btn, 'setAccessibleName', 'Legacy.s4c87616d148247fd')
        self.browse_output_btn.clicked.connect(self.browse_output_file)
        output_file_layout.addWidget(self.browse_output_btn)

        output_layout.addRow("Output File:", output_file_layout)

        layout.addWidget(output_group)

        # Dialog buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        self.cancel_btn = _ui_widget(SecondaryButton, 'Legacy.s19766ed6ccb2f4a3', 'setText')
        _ui_bind(self.cancel_btn, 'setAccessibleName', 'Legacy.s108c6eaa3f0db951')
        self.cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_btn)

        self.sign_btn = _ui_widget(PrimaryButton, 'Legacy.sd78d69270eb64ab4', 'setText')
        _ui_bind(self.sign_btn, 'setAccessibleName', 'Legacy.sd1a8b617a29083a7')
        self.sign_btn.clicked.connect(self.accept)
        self.sign_btn.setEnabled(False)
        self.sign_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {token('semantic_error')};
                color: {token('text_on_primary')};
                font-weight: bold;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {token('semantic_error_hover')};
            }}
            QPushButton:disabled {{
                background-color: {token('text_disabled')};
            }}
        """
        )
        buttons_layout.addWidget(self.sign_btn)

        layout.addLayout(buttons_layout)

        self.apply_styling()

    def apply_styling(self):
        """Apply modern styling to the dialog"""
        self.setStyleSheet(
            f"""
            QDialog {{
                background-color: {token('window_background')};

            }}
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {token('border_light')};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
            QPushButton {{
                padding: 6px 12px;
                border: 1px solid {token('border_light')};
                border-radius: 4px;
                background-color: {token('surface')};
            }}
            QPushButton:hover {{
                background-color: {token('color_bg_tint')};
            }}
            QLineEdit {{
                padding: 6px;
                border: 1px solid {token('border_light')};
                border-radius: 4px;
            }}
        """
        )
        font_tokens.bind(self, "font.body")

    def browse_pdf_file(self):
        """Browse for PDF file to sign"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select PDF File to Sign",
            "",
            "PDF Files (*.pdf);;All Files (*)",
        )

        if file_path:
            self.pdf_file_edit.setText(file_path)
            # Auto-generate output filename
            base_name = os.path.splitext(file_path)[0]
            output_file = f"{base_name}_signed.pdf"
            self.output_file_edit.setText(output_file)

    def browse_signature_file(self):
        """Browse for signature image file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Signature Image",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*)",
        )

        if file_path:
            self.sig_file_edit.setText(file_path)

    def browse_certificate_file(self):
        """Browse for certificate file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Certificate File",
            "",
            "Certificate Files (*.pfx *.p12 *.pem);;All Files (*)",
        )

        if file_path:
            self.cert_file_edit.setText(file_path)

    def browse_output_file(self):
        """Browse for output file location"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Signed PDF As",
            "signed_document.pdf",
            "PDF Files (*.pdf);;All Files (*)",
        )

        if file_path:
            self.output_file_edit.setText(file_path)

    def on_position_changed(self, button, checked):
        """Handle position change"""
        if checked:
            position_value = button.property("position_value")
            is_custom = position_value == "custom"
            self.custom_x_spin.setEnabled(is_custom)
            self.custom_y_spin.setEnabled(is_custom)

    def on_pages_changed(self, button, checked):
        """Handle pages selection change"""
        if checked:
            is_custom = button == self.custom_pages_radio
            self.custom_pages_edit.setEnabled(is_custom)

    def update_transparency_label(self, value):
        """Update transparency label"""
        self.transparency_label.setText(f"{value}%")

    def toggle_certificate(self, enabled):
        """Toggle certificate file controls"""
        self.cert_file_edit.setEnabled(enabled)
        self.browse_cert_btn.setEnabled(enabled)

    def update_sign_button(self):
        """Update sign button state"""
        has_pdf = bool(self.pdf_file_edit.text().strip())
        has_signature = bool(self.sig_file_edit.text().strip())
        has_output = bool(self.output_file_edit.text().strip())

        self.sign_btn.setEnabled(has_pdf and has_signature and has_output)

    def get_sign_options(self) -> Dict[str, Any]:
        """Get sign options from the dialog"""
        # Get selected position
        position = "bottom_right"  # default
        for button in self.position_group.buttons():
            if button.isChecked():
                position = button.property("position_value")
                break

        if position == "custom":
            position = (self.custom_x_spin.value(), self.custom_y_spin.value())

        # Get pages to sign
        pages = "all"  # default
        if self.first_page_radio.isChecked():
            pages = "first"
        elif self.last_page_radio.isChecked():
            pages = "last"
        elif self.custom_pages_radio.isChecked():
            pages_text = self.custom_pages_edit.text().strip()
            if pages_text:
                try:
                    # Parse custom pages (convert to 0-based)
                    pages = [
                        int(p.strip()) - 1
                        for p in pages_text.split(",")
                        if p.strip().isdigit()
                    ]
                except ValueError:
                    pages = "all"  # fallback

        options = {
            "position": position,
            "pages": pages,
            "size": (self.width_spin.value(), self.height_spin.value()),
            "transparency": self.transparency_slider.value() / 100.0,
            "digital_signature": self.digital_sig_cb.isChecked(),
            "certificate_file": (
                self.cert_file_edit.text().strip()
                if self.digital_sig_cb.isChecked()
                else None
            ),
        }

        return options

    def get_input_file(self) -> str:
        """Get input PDF file path"""
        return self.pdf_file_edit.text().strip()

    def get_signature_file(self) -> str:
        """Get signature image file path"""
        return self.sig_file_edit.text().strip()

    def get_output_file(self) -> str:
        """Get output file path"""
        return self.output_file_edit.text().strip()


if __name__ == "__main__":
    # Test the parameter dialogs
    import sys

    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # Test merge dialog
    merge_dialog = PDFMergeDialog()
    if merge_dialog.exec_() == QDialog.Accepted:
        print("Merge dialog accepted")
        print(f"Input files: {merge_dialog.get_input_files()}")
        print(f"Output file: {merge_dialog.get_output_file()}")
        print(f"Options: {merge_dialog.get_merge_options()}")

    # Test split dialog
    split_dialog = PDFSplitDialog()
    if split_dialog.exec_() == QDialog.Accepted:
        print("Split dialog accepted")
        print(f"Input file: {split_dialog.get_input_file()}")
        print(f"Output directory: {split_dialog.get_output_directory()}")
        print(f"Options: {split_dialog.get_split_options()}")

    # Test sign dialog
    sign_dialog = PDFSignDialog()
    if sign_dialog.exec_() == QDialog.Accepted:
        print("Sign dialog accepted")
        print(f"Input file: {sign_dialog.get_input_file()}")
        print(f"Signature file: {sign_dialog.get_signature_file()}")
        print(f"Output file: {sign_dialog.get_output_file()}")
        print(f"Options: {sign_dialog.get_sign_options()}")
