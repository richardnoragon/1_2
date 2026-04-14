#!/usr/bin/env python3
"""
PDF Parameter Dialogs - User interface dialogs for PDF operations
Provides modern, intuitive dialogs for merge, split, and sign operations
"""

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

from src.gui.themes import token

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
        self.preview_label = QLabel("No file selected")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet(
            """
            QLabel {
                border: 2px dashed {token('border')};
                border-radius: 8px;
                padding: 20px;
                background-color: {token('surface')};
                color: {token('text_muted')};
                font-size: 12pt;
            }
        """
        )
        self.preview_label.setMinimumHeight(120)
        layout.addWidget(self.preview_label)

        # File info
        self.info_label = QLabel("")
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet(f"font-size: 10pt; color: {token('text_muted')};")
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

        self.setWindowTitle("Merge PDF Files")
        self.setModal(True)
        self.resize(800, 600)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Create splitter for main content
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)

        # Left panel - File list
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # Input files section
        files_group = QGroupBox("Input Files")
        files_layout = QVBoxLayout(files_group)

        # File list with drag-drop support
        self.file_list = DragDropListWidget()
        self.file_list.files_reordered.connect(self.on_files_reordered)
        self.file_list.itemSelectionChanged.connect(self.on_file_selected)
        files_layout.addWidget(self.file_list)

        # File control buttons
        file_buttons_layout = QHBoxLayout()

        self.add_files_btn = QPushButton("Add Files")
        self.add_files_btn.clicked.connect(self.add_files)
        file_buttons_layout.addWidget(self.add_files_btn)

        self.remove_file_btn = QPushButton("Remove")
        self.remove_file_btn.clicked.connect(self.remove_selected_file)
        self.remove_file_btn.setEnabled(False)
        file_buttons_layout.addWidget(self.remove_file_btn)

        self.move_up_btn = QPushButton("↑")
        self.move_up_btn.clicked.connect(self.move_file_up)
        self.move_up_btn.setEnabled(False)
        file_buttons_layout.addWidget(self.move_up_btn)

        self.move_down_btn = QPushButton("↓")
        self.move_down_btn.clicked.connect(self.move_file_down)
        self.move_down_btn.setEnabled(False)
        file_buttons_layout.addWidget(self.move_down_btn)

        files_layout.addLayout(file_buttons_layout)
        left_layout.addWidget(files_group)

        # Options section
        options_group = QGroupBox("Merge Options")
        options_layout = QFormLayout(options_group)

        self.preserve_bookmarks_cb = QCheckBox("Preserve bookmarks")
        self.preserve_bookmarks_cb.setChecked(True)
        options_layout.addRow(self.preserve_bookmarks_cb)

        self.preserve_metadata_cb = QCheckBox("Preserve metadata")
        self.preserve_metadata_cb.setChecked(True)
        options_layout.addRow(self.preserve_metadata_cb)

        self.optimize_output_cb = QCheckBox("Optimize output file")
        options_layout.addRow(self.optimize_output_cb)

        self.custom_ranges_cb = QCheckBox("Use custom page ranges")
        self.custom_ranges_cb.toggled.connect(self.toggle_custom_ranges)
        options_layout.addRow(self.custom_ranges_cb)

        left_layout.addWidget(options_group)

        # Output section
        output_group = QGroupBox("Output")
        output_layout = QFormLayout(output_group)

        output_file_layout = QHBoxLayout()
        self.output_file_edit = QLineEdit()
        self.output_file_edit.setPlaceholderText("Select output file...")
        output_file_layout.addWidget(self.output_file_edit)

        self.browse_output_btn = QPushButton("Browse")
        self.browse_output_btn.clicked.connect(self.browse_output_file)
        output_file_layout.addWidget(self.browse_output_btn)

        output_layout.addRow("Output file:", output_file_layout)
        left_layout.addWidget(output_group)

        splitter.addWidget(left_panel)

        # Right panel - Preview
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout(preview_group)

        self.preview_widget = FilePreviewWidget()
        preview_layout.addWidget(self.preview_widget)

        # File details
        self.details_text = QTextEdit()
        self.details_text.setMaximumHeight(100)
        self.details_text.setReadOnly(True)
        preview_layout.addWidget(self.details_text)

        right_layout.addWidget(preview_group)

        # Custom ranges section (initially hidden)
        self.ranges_group = QGroupBox("Custom Page Ranges")
        self.ranges_group.setVisible(False)
        ranges_layout = QVBoxLayout(self.ranges_group)

        ranges_help = QLabel(
            "Specify page ranges for each file (e.g., 1-5,10-15).\n"
            "Leave empty to include all pages."
        )
        ranges_help.setWordWrap(True)
        ranges_help.setStyleSheet(f"color: {token('text_muted')}; font-size: 9pt;")
        ranges_layout.addWidget(ranges_help)

        self.ranges_list = QListWidget()
        ranges_layout.addWidget(self.ranges_list)

        right_layout.addWidget(self.ranges_group)

        splitter.addWidget(right_panel)
        splitter.setSizes([400, 400])

        # Dialog buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_btn)

        self.merge_btn = QPushButton("Merge PDFs")
        self.merge_btn.clicked.connect(self.accept)
        self.merge_btn.setEnabled(False)
        self.merge_btn.setStyleSheet(
            """
            QPushButton {
                background-color: {token('button_primary')};
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: {token('button_primary')};
            }
            QPushButton:disabled {
                background-color: {token('border')};
            }
        """
        )
        buttons_layout.addWidget(self.merge_btn)

        layout.addLayout(buttons_layout)

        self.apply_styling()

    def apply_styling(self):
        """Apply modern styling to the dialog"""
        self.setStyleSheet(
            """
            QDialog {
                background-color: {token('window_background')};
                font-family: "Segoe UI", Arial, sans-serif;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid {token('border_light')};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                padding: 6px 12px;
                border: 1px solid {token('border')};
                border-radius: 4px;
                background-color: {token('dialog_background')};
            }
            QPushButton:hover {
                background-color: {token('border_light')};
            }
            QListWidget {
                border: 1px solid {token('border_light')};
                border-radius: 4px;
                background-color: {token('window_background')};
            }
            QLineEdit {
                padding: 6px;
                border: 1px solid {token('border_light')};
                border-radius: 4px;
            }
        """
        )

    def add_files(self):
        """Add PDF files to the merge list"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select PDF Files to Merge",
            "",
            "PDF Files (*.pdf);;All Files (*)",
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
            "PDF Files (*.pdf);;All Files (*)",
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

        self.setWindowTitle("Split PDF File")
        self.setModal(True)
        self.resize(700, 500)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Input file section
        input_group = QGroupBox("Input File")
        input_layout = QFormLayout(input_group)

        input_file_layout = QHBoxLayout()
        self.input_file_edit = QLineEdit()
        self.input_file_edit.setPlaceholderText("Select PDF file to split...")
        self.input_file_edit.textChanged.connect(self.on_input_file_changed)
        input_file_layout.addWidget(self.input_file_edit)

        self.browse_input_btn = QPushButton("Browse")
        self.browse_input_btn.clicked.connect(self.browse_input_file)
        input_file_layout.addWidget(self.browse_input_btn)

        input_layout.addRow("PDF File:", input_file_layout)

        self.file_info_label = QLabel("")
        self.file_info_label.setStyleSheet(
            f"color: {token('text_muted')}; font-size: 10pt;"
        )
        input_layout.addRow(self.file_info_label)

        layout.addWidget(input_group)

        # Split method section
        method_group = QGroupBox("Split Method")
        method_layout = QVBoxLayout(method_group)

        self.method_group = QButtonGroup()

        # By page count
        self.pages_radio = QRadioButton("Split by page count")
        self.pages_radio.setChecked(True)
        self.pages_radio.toggled.connect(self.on_method_changed)
        self.method_group.addButton(self.pages_radio)
        method_layout.addWidget(self.pages_radio)

        pages_layout = QHBoxLayout()
        pages_layout.addSpacing(20)
        pages_layout.addWidget(QLabel("Pages per file:"))
        self.pages_spinbox = QSpinBox()
        self.pages_spinbox.setMinimum(1)
        self.pages_spinbox.setMaximum(1000)
        self.pages_spinbox.setValue(1)
        pages_layout.addWidget(self.pages_spinbox)
        pages_layout.addStretch()
        method_layout.addLayout(pages_layout)

        # By page ranges
        self.ranges_radio = QRadioButton("Split by page ranges")
        self.ranges_radio.toggled.connect(self.on_method_changed)
        self.method_group.addButton(self.ranges_radio)
        method_layout.addWidget(self.ranges_radio)

        ranges_layout = QHBoxLayout()
        ranges_layout.addSpacing(20)
        ranges_layout.addWidget(QLabel("Page ranges:"))
        self.ranges_edit = QLineEdit()
        self.ranges_edit.setPlaceholderText("e.g., 1-10,11-20,21-30")
        self.ranges_edit.setEnabled(False)
        ranges_layout.addWidget(self.ranges_edit)
        method_layout.addLayout(ranges_layout)

        # By bookmarks
        self.bookmarks_radio = QRadioButton("Split by bookmarks (chapter-based)")
        self.bookmarks_radio.toggled.connect(self.on_method_changed)
        self.method_group.addButton(self.bookmarks_radio)
        method_layout.addWidget(self.bookmarks_radio)

        # By file size
        self.size_radio = QRadioButton("Split by file size")
        self.size_radio.toggled.connect(self.on_method_changed)
        self.method_group.addButton(self.size_radio)
        method_layout.addWidget(self.size_radio)

        size_layout = QHBoxLayout()
        size_layout.addSpacing(20)
        size_layout.addWidget(QLabel("Max size per file:"))
        self.size_spinbox = QSpinBox()
        self.size_spinbox.setMinimum(1)
        self.size_spinbox.setMaximum(100)
        self.size_spinbox.setValue(5)
        self.size_spinbox.setEnabled(False)
        size_layout.addWidget(self.size_spinbox)
        size_layout.addWidget(QLabel("MB"))
        size_layout.addStretch()
        method_layout.addLayout(size_layout)

        layout.addWidget(method_group)

        # Preview section
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout(preview_group)

        self.preview_text = QTextEdit()
        self.preview_text.setMaximumHeight(100)
        self.preview_text.setReadOnly(True)
        self.preview_text.setPlaceholderText("Split preview will appear here...")
        preview_layout.addWidget(self.preview_text)

        layout.addWidget(preview_group)

        # Output section
        output_group = QGroupBox("Output")
        output_layout = QFormLayout(output_group)

        output_dir_layout = QHBoxLayout()
        self.output_dir_edit = QLineEdit()
        self.output_dir_edit.setPlaceholderText("Select output directory...")
        self.output_dir_edit.textChanged.connect(self.update_split_button)
        output_dir_layout.addWidget(self.output_dir_edit)

        self.browse_output_btn = QPushButton("Browse")
        self.browse_output_btn.clicked.connect(self.browse_output_directory)
        output_dir_layout.addWidget(self.browse_output_btn)

        output_layout.addRow("Output Directory:", output_dir_layout)

        self.naming_edit = QLineEdit("split_{index}.pdf")
        output_layout.addRow("Naming Pattern:", self.naming_edit)

        layout.addWidget(output_group)

        # Dialog buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_btn)

        self.split_btn = QPushButton("Split PDF")
        self.split_btn.clicked.connect(self.accept)
        self.split_btn.setEnabled(False)
        self.split_btn.setStyleSheet(
            """
            QPushButton {
                background-color: {token('semantic_success')};
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: {token('semantic_success')};
            }
            QPushButton:disabled {
                background-color: {token('border')};
            }
        """
        )
        buttons_layout.addWidget(self.split_btn)

        layout.addLayout(buttons_layout)

        self.apply_styling()

    def apply_styling(self):
        """Apply modern styling to the dialog"""
        self.setStyleSheet(
            """
            QDialog {
                background-color: {token('window_background')};
                font-family: "Segoe UI", Arial, sans-serif;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid {token('border_light')};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                padding: 6px 12px;
                border: 1px solid {token('border')};
                border-radius: 4px;
                background-color: {token('dialog_background')};
            }
            QPushButton:hover {
                background-color: {token('border_light')};
            }
            QLineEdit {
                padding: 6px;
                border: 1px solid {token('border_light')};
                border-radius: 4px;
            }
            QTextEdit {
                border: 1px solid {token('border_light')};
                border-radius: 4px;
            }
        """
        )

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

        self.setWindowTitle("Sign PDF Document")
        self.setModal(True)
        self.resize(600, 500)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Input files section
        files_group = QGroupBox("Files")
        files_layout = QFormLayout(files_group)

        # PDF file
        pdf_file_layout = QHBoxLayout()
        self.pdf_file_edit = QLineEdit()
        self.pdf_file_edit.setPlaceholderText("Select PDF file to sign...")
        self.pdf_file_edit.textChanged.connect(self.update_sign_button)
        pdf_file_layout.addWidget(self.pdf_file_edit)

        self.browse_pdf_btn = QPushButton("Browse")
        self.browse_pdf_btn.clicked.connect(self.browse_pdf_file)
        pdf_file_layout.addWidget(self.browse_pdf_btn)

        files_layout.addRow("PDF File:", pdf_file_layout)

        # Signature file
        sig_file_layout = QHBoxLayout()
        self.sig_file_edit = QLineEdit()
        self.sig_file_edit.setPlaceholderText("Select signature image...")
        self.sig_file_edit.textChanged.connect(self.update_sign_button)
        sig_file_layout.addWidget(self.sig_file_edit)

        self.browse_sig_btn = QPushButton("Browse")
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
        position_group = QGroupBox("Position")
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
            radio.setProperty("position_value", value)
            if value == "bottom_right":
                radio.setChecked(True)
            self.position_group.addButton(radio)
            position_layout.addWidget(radio, row, col)

        # Custom coordinates
        custom_layout = QHBoxLayout()
        custom_layout.addWidget(QLabel("X:"))
        self.custom_x_spin = QSpinBox()
        self.custom_x_spin.setRange(0, 1000)
        self.custom_x_spin.setValue(100)
        self.custom_x_spin.setEnabled(False)
        custom_layout.addWidget(self.custom_x_spin)

        custom_layout.addWidget(QLabel("Y:"))
        self.custom_y_spin = QSpinBox()
        self.custom_y_spin.setRange(0, 1000)
        self.custom_y_spin.setValue(100)
        self.custom_y_spin.setEnabled(False)
        custom_layout.addWidget(self.custom_y_spin)

        position_layout.addLayout(custom_layout, 3, 0, 1, 2)

        # Connect position change
        self.position_group.buttonToggled.connect(self.on_position_changed)

        left_layout.addWidget(position_group)

        # Pages section
        pages_group = QGroupBox("Pages to Sign")
        pages_layout = QVBoxLayout(pages_group)

        self.pages_group = QButtonGroup()

        self.all_pages_radio = QRadioButton("All pages")
        self.all_pages_radio.setChecked(True)
        self.pages_group.addButton(self.all_pages_radio)
        pages_layout.addWidget(self.all_pages_radio)

        self.first_page_radio = QRadioButton("First page only")
        self.pages_group.addButton(self.first_page_radio)
        pages_layout.addWidget(self.first_page_radio)

        self.last_page_radio = QRadioButton("Last page only")
        self.pages_group.addButton(self.last_page_radio)
        pages_layout.addWidget(self.last_page_radio)

        self.custom_pages_radio = QRadioButton("Custom pages:")
        self.pages_group.addButton(self.custom_pages_radio)
        pages_layout.addWidget(self.custom_pages_radio)

        custom_pages_layout = QHBoxLayout()
        custom_pages_layout.addSpacing(20)
        self.custom_pages_edit = QLineEdit()
        self.custom_pages_edit.setPlaceholderText("e.g., 1,3,5")
        self.custom_pages_edit.setEnabled(False)
        custom_pages_layout.addWidget(self.custom_pages_edit)
        pages_layout.addLayout(custom_pages_layout)

        self.pages_group.buttonToggled.connect(self.on_pages_changed)

        left_layout.addWidget(pages_group)

        # Options section
        options_group = QGroupBox("Options")
        options_layout = QFormLayout(options_group)

        # Size
        size_layout = QHBoxLayout()
        self.width_spin = QSpinBox()
        self.width_spin.setRange(10, 500)
        self.width_spin.setValue(100)
        self.width_spin.setSuffix(" pt")
        size_layout.addWidget(self.width_spin)

        size_layout.addWidget(QLabel("×"))

        self.height_spin = QSpinBox()
        self.height_spin.setRange(10, 500)
        self.height_spin.setValue(50)
        self.height_spin.setSuffix(" pt")
        size_layout.addWidget(self.height_spin)

        options_layout.addRow("Size:", size_layout)

        # Transparency
        self.transparency_slider = QSlider(Qt.Horizontal)
        self.transparency_slider.setRange(0, 100)
        self.transparency_slider.setValue(80)
        self.transparency_slider.valueChanged.connect(self.update_transparency_label)

        transparency_layout = QHBoxLayout()
        transparency_layout.addWidget(self.transparency_slider)
        self.transparency_label = QLabel("80%")
        transparency_layout.addWidget(self.transparency_label)

        options_layout.addRow("Transparency:", transparency_layout)

        # Digital signature
        self.digital_sig_cb = QCheckBox("Add digital signature (requires certificate)")
        self.digital_sig_cb.toggled.connect(self.toggle_certificate)
        options_layout.addRow(self.digital_sig_cb)

        # Certificate file
        cert_layout = QHBoxLayout()
        self.cert_file_edit = QLineEdit()
        self.cert_file_edit.setPlaceholderText("Select certificate file...")
        self.cert_file_edit.setEnabled(False)
        cert_layout.addWidget(self.cert_file_edit)

        self.browse_cert_btn = QPushButton("Browse")
        self.browse_cert_btn.clicked.connect(self.browse_certificate_file)
        self.browse_cert_btn.setEnabled(False)
        cert_layout.addWidget(self.browse_cert_btn)

        options_layout.addRow("Certificate:", cert_layout)

        left_layout.addWidget(options_group)

        splitter.addWidget(left_panel)

        # Right panel - Preview
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout(preview_group)

        # Preview area (placeholder)
        self.preview_label = QLabel("Preview will appear here")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet(
            """
            QLabel {
                border: 2px dashed {token('border')};
                border-radius: 8px;
                padding: 40px;
                background-color: {token('surface')};
                color: {token('text_muted')};
                font-size: 12pt;
            }
        """
        )
        self.preview_label.setMinimumHeight(200)
        preview_layout.addWidget(self.preview_label)

        right_layout.addWidget(preview_group)

        splitter.addWidget(right_panel)
        splitter.setSizes([350, 250])

        # Output section
        output_group = QGroupBox("Output")
        output_layout = QFormLayout(output_group)

        output_file_layout = QHBoxLayout()
        self.output_file_edit = QLineEdit()
        self.output_file_edit.setPlaceholderText(
            "Output file will be auto-generated..."
        )
        self.output_file_edit.textChanged.connect(self.update_sign_button)
        output_file_layout.addWidget(self.output_file_edit)

        self.browse_output_btn = QPushButton("Browse")
        self.browse_output_btn.clicked.connect(self.browse_output_file)
        output_file_layout.addWidget(self.browse_output_btn)

        output_layout.addRow("Output File:", output_file_layout)

        layout.addWidget(output_group)

        # Dialog buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_btn)

        self.sign_btn = QPushButton("Sign Document")
        self.sign_btn.clicked.connect(self.accept)
        self.sign_btn.setEnabled(False)
        self.sign_btn.setStyleSheet(
            """
            QPushButton {
                background-color: {token('semantic_error')};
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: {token('semantic_error')};
            }
            QPushButton:disabled {
                background-color: {token('border')};
            }
        """
        )
        buttons_layout.addWidget(self.sign_btn)

        layout.addLayout(buttons_layout)

        self.apply_styling()

    def apply_styling(self):
        """Apply modern styling to the dialog"""
        self.setStyleSheet(
            """
            QDialog {
                background-color: {token('window_background')};
                font-family: "Segoe UI", Arial, sans-serif;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid {token('border_light')};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                padding: 6px 12px;
                border: 1px solid {token('border')};
                border-radius: 4px;
                background-color: {token('dialog_background')};
            }
            QPushButton:hover {
                background-color: {token('border_light')};
            }
            QLineEdit {
                padding: 6px;
                border: 1px solid {token('border_light')};
                border-radius: 4px;
            }
        """
        )

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
