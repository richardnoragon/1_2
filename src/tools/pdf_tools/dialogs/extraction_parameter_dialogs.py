#!/usr/bin/env python3
"""
PDF Extraction Parameter Dialogs - Phase 2.2 Implementation
User interface dialogs for PDF extraction operations following established patterns
"""
from src.rfu.localization import localized_widget as _ui_widget, bind_literal as _ui_bind
from src.rfu import font_tokens

import logging
import os
from typing import Any, Dict, List, Optional, Tuple

from PyQt5.QtCore import QSize, Qt, QThread, QTimer, pyqtSignal
from PyQt5.QtGui import QColor, QFont, QIcon, QPalette, QPixmap
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
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
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

PDF_OPEN_FILE_FILTER = "PDF Files (*.pdf);;All Files (*)"

# Set up logger
logger = logging.getLogger(__name__)


class PDFExtractionDialogBase(QDialog):
    """Base class for PDF extraction parameter dialogs"""

    def __init__(self, parent=None, extraction_type: str = ""):
        super().__init__(parent)
        self.extraction_type = extraction_type
        self.input_file = ""
        self.output_location = ""
        self.extraction_options = {}

        self.setWindowTitle(f"PDF {extraction_type.title()} Extraction")
        self.setModal(True)
        self.resize(600, 500)

        # Apply consistent styling
        self.setStyleSheet(
            """
            QDialog {
                background-color: {token('window_background')};

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
                background-color: {token('button_primary')};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: {token('button_primary')};
            }
            QPushButton:disabled {
                background-color: {token('text_muted')};
            }
        """
        )
        font_tokens.bind(self, "font.body")

        self.init_ui()
        self.setup_connections()

    def init_ui(self):
        """Initialize the UI - to be implemented by subclasses"""
        pass

    def setup_connections(self):
        """Setup signal connections - to be implemented by subclasses"""
        pass

    def get_input_file(self) -> str:
        """Get the selected input file"""
        return self.input_file

    def get_output_location(self) -> str:
        """Get the selected output location"""
        return self.output_location

    def get_extraction_options(self) -> Dict[str, Any]:
        """Get the extraction options"""
        return self.extraction_options

    def validate_parameters(self) -> bool:
        """Validate the dialog parameters"""
        if not self.input_file or not os.path.exists(self.input_file):
            QMessageBox.warning(
                self, "Invalid Input", "Please select a valid PDF file."
            )
            return False

        if not self.output_location:
            QMessageBox.warning(
                self, "Invalid Output", "Please specify an output location."
            )
            return False

        return True


class PDFTextExtractionDialog(PDFExtractionDialogBase):
    """Dialog for PDF text extraction parameters"""

    def __init__(self, parent=None):
        super().__init__(parent, "Text")

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Input file section
        input_group = _ui_widget(QGroupBox, 'Legacy.s22bc9850e3d02875', 'setTitle')
        input_layout = QHBoxLayout(input_group)

        self.input_edit = TextInput(
            "Input PDF file",
            "Select PDF file...",
            accessible_name="Input PDF file",
        )
        self.input_edit.setReadOnly(True)
        input_layout.addWidget(self.input_edit)

        self.browse_input_btn = _ui_widget(SecondaryButton, 'Legacy.sc58a6bd402efb06c', 'setText')
        _ui_bind(self.browse_input_btn, 'setAccessibleName', 'Legacy.s6a0c40ebf4735e07')
        input_layout.addWidget(self.browse_input_btn)

        layout.addWidget(input_group)

        # Output file section
        output_group = _ui_widget(QGroupBox, 'Legacy.s1f255907a60dd154', 'setTitle')
        output_layout = QHBoxLayout(output_group)

        self.output_edit = TextInput(
            "Output text file",
            "Output text file...",
            accessible_name="Output text file",
        )
        output_layout.addWidget(self.output_edit)

        self.browse_output_btn = _ui_widget(SecondaryButton, 'Legacy.sc58a6bd402efb06c', 'setText')
        _ui_bind(self.browse_output_btn, 'setAccessibleName', 'Legacy.sfc96835debadaf35')
        output_layout.addWidget(self.browse_output_btn)

        layout.addWidget(output_group)

        # Extraction options
        options_group = _ui_widget(QGroupBox, 'Legacy.s58426c87d69b9dc1', 'setTitle')
        options_layout = QFormLayout(options_group)

        # Extraction method
        self.method_combo = QComboBox()
        _ui_bind(self.method_combo, 'setAccessibleName', 'Legacy.s03d9cd38f08b1a7d')
        self.method_combo.setMinimumHeight(44)
        self.method_combo.addItems(["pdfplumber", "pymupdf"])
        self.method_combo.setCurrentText("pdfplumber")
        options_layout.addRow("Extraction Method:", self.method_combo)

        # Page range
        page_range_layout = QHBoxLayout()
        self.page_range_check = _ui_widget(QCheckBox, 'Legacy.s500277376e9ea8fc', 'setText')
        _ui_bind(self.page_range_check, 'setAccessibleName', 'Legacy.sb92076db77e8dd15')
        self.page_range_check.setMinimumHeight(44)
        page_range_layout.addWidget(self.page_range_check)

        self.start_page_spin = QSpinBox()
        _ui_bind(self.start_page_spin, 'setAccessibleName', 'Legacy.s8cefd6c52d03fe65')
        self.start_page_spin.setMinimumHeight(44)
        self.start_page_spin.setMinimum(1)
        self.start_page_spin.setMaximum(9999)
        self.start_page_spin.setEnabled(False)
        page_range_layout.addWidget(_ui_widget(QLabel, 'Legacy.sdc45d36f35e84e07', 'setText'))
        page_range_layout.addWidget(self.start_page_spin)

        self.end_page_spin = QSpinBox()
        _ui_bind(self.end_page_spin, 'setAccessibleName', 'Legacy.sf1aa36b86021c1ba')
        self.end_page_spin.setMinimumHeight(44)
        self.end_page_spin.setMinimum(1)
        self.end_page_spin.setMaximum(9999)
        self.end_page_spin.setEnabled(False)
        page_range_layout.addWidget(_ui_widget(QLabel, 'Legacy.s2b5fc5c94f64250c', 'setText'))
        page_range_layout.addWidget(self.end_page_spin)

        page_range_layout.addStretch()
        options_layout.addRow(page_range_layout)

        # Include formatting
        self.formatting_check = _ui_widget(QCheckBox, 'Legacy.s0d31c0796a39ca16', 'setText')
        _ui_bind(self.formatting_check, 'setAccessibleName', 'Legacy.s0d31c0796a39ca16')
        self.formatting_check.setMinimumHeight(44)
        options_layout.addRow("Formatting:", self.formatting_check)

        layout.addWidget(options_group)

        # Preview section
        preview_group = _ui_widget(QGroupBox, 'Legacy.s324b134f57c70c72', 'setTitle')
        preview_layout = QVBoxLayout(preview_group)

        self.preview_text = QPlainTextEdit()
        _ui_bind(self.preview_text, 'setAccessibleName', 'Legacy.s5f55425378a6910b')
        self.preview_text.setMaximumHeight(100)
        _ui_bind(self.preview_text, 'setPlaceholderText', 'Legacy.s947db4c831f3a16c')
        self.preview_text.setReadOnly(True)
        preview_layout.addWidget(self.preview_text)

        self.preview_btn = _ui_widget(SecondaryButton, 'Legacy.sd486e2c6718ba223', 'setText')
        _ui_bind(self.preview_btn, 'setAccessibleName', 'Legacy.s32387aa545e2e282')
        self.preview_btn.setEnabled(False)
        preview_layout.addWidget(self.preview_btn)

        layout.addWidget(preview_group)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancel_btn = _ui_widget(SecondaryButton, 'Legacy.s19766ed6ccb2f4a3', 'setText')
        _ui_bind(self.cancel_btn, 'setAccessibleName', 'Legacy.sd832d706f7175c10')
        button_layout.addWidget(self.cancel_btn)

        self.extract_btn = _ui_widget(PrimaryButton, 'Legacy.s9ab5926ba4cd7a39', 'setText')
        _ui_bind(self.extract_btn, 'setAccessibleName', 'Legacy.sb659675ab4773bbb')
        self.extract_btn.setEnabled(False)
        button_layout.addWidget(self.extract_btn)

        layout.addLayout(button_layout)

    def setup_connections(self):
        self.browse_input_btn.clicked.connect(self.browse_input_file)
        self.browse_output_btn.clicked.connect(self.browse_output_file)
        self.page_range_check.toggled.connect(self.toggle_page_range)
        self.preview_btn.clicked.connect(self.preview_text_extraction)
        self.cancel_btn.clicked.connect(self.reject)
        self.extract_btn.clicked.connect(self.accept)

        # Auto-generate output filename when input changes
        self.input_edit.textChanged.connect(self.auto_generate_output)

    def browse_input_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select PDF File", "", "PDF Files (*.pdf)"
        )
        if file_path:
            self.input_file = file_path
            self.input_edit.setText(file_path)
            self.preview_btn.setEnabled(True)

    def browse_output_file(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Text File As", "", "Text Files (*.txt)"
        )
        if file_path:
            self.output_location = file_path
            self.output_edit.setText(file_path)
            self.update_extract_button()

    def auto_generate_output(self):
        if self.input_file:
            base_name = os.path.splitext(self.input_file)[0]
            output_file = f"{base_name}_extracted_text.txt"
            self.output_location = output_file
            self.output_edit.setText(output_file)
            self.update_extract_button()

    def toggle_page_range(self, checked):
        self.start_page_spin.setEnabled(checked)
        self.end_page_spin.setEnabled(checked)
        if checked:
            self.start_page_spin.setValue(1)
            self.end_page_spin.setValue(1)

    def update_extract_button(self):
        has_input = bool(self.input_file)
        has_output = bool(self.output_location)
        self.extract_btn.setEnabled(has_input and has_output)

    def preview_text_extraction(self):
        if not self.input_file:
            return

        try:
            # Simple preview using first method available
            import fitz

            doc = fitz.open(self.input_file)
            if len(doc) > 0:
                first_page = doc[0]
                text = first_page.get_text()
                preview_text = text[:500] + "..." if len(text) > 500 else text
                self.preview_text.setPlainText(preview_text)
            doc.close()
        except:
            self.preview_text.setPlainText("Preview not available")

    def get_extraction_options(self) -> Dict[str, Any]:
        options = {
            "method": self.method_combo.currentText(),
            "include_formatting": self.formatting_check.isChecked(),
        }

        if self.page_range_check.isChecked():
            options["page_range"] = (
                self.start_page_spin.value() - 1,  # Convert to 0-based
                self.end_page_spin.value() - 1,
            )

        return options


class PDFImageExtractionDialog(PDFExtractionDialogBase):
    """Dialog for PDF image extraction parameters"""

    def __init__(self, parent=None):
        super().__init__(parent, "Image")

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Input file section
        input_group = _ui_widget(QGroupBox, 'Legacy.s22bc9850e3d02875', 'setTitle')
        input_layout = QHBoxLayout(input_group)

        self.input_edit = TextInput(
            "Input PDF file",
            "Select PDF file...",
            accessible_name="Input PDF file",
        )
        self.input_edit.setReadOnly(True)
        input_layout.addWidget(self.input_edit)

        self.browse_input_btn = _ui_widget(SecondaryButton, 'Legacy.sc58a6bd402efb06c', 'setText')
        _ui_bind(self.browse_input_btn, 'setAccessibleName', 'Legacy.s6a0c40ebf4735e07')
        input_layout.addWidget(self.browse_input_btn)

        layout.addWidget(input_group)

        # Output directory section
        output_group = _ui_widget(QGroupBox, 'Legacy.s2d8842920b678b49', 'setTitle')
        output_layout = QHBoxLayout(output_group)

        self.output_edit = TextInput(
            "Output directory for images",
            "Output directory...",
            accessible_name="Output directory for images",
        )
        output_layout.addWidget(self.output_edit)

        self.browse_output_btn = _ui_widget(SecondaryButton, 'Legacy.sc58a6bd402efb06c', 'setText')
        _ui_bind(self.browse_output_btn, 'setAccessibleName', 'Legacy.s9f20baa3d056c434')
        output_layout.addWidget(self.browse_output_btn)

        layout.addWidget(output_group)

        # Extraction options
        options_group = _ui_widget(QGroupBox, 'Legacy.s4983b0aa01cecd3c', 'setTitle')
        options_layout = QFormLayout(options_group)

        # Image format
        self.format_combo = QComboBox()
        _ui_bind(self.format_combo, 'setAccessibleName', 'Legacy.s5cbac26f26346506')
        self.format_combo.setMinimumHeight(44)
        self.format_combo.addItems(["png", "jpg", "bmp", "tiff"])
        self.format_combo.setCurrentText("png")
        options_layout.addRow("Image Format:", self.format_combo)

        # Minimum size filters
        size_layout = QHBoxLayout()

        self.min_width_spin = QSpinBox()
        _ui_bind(self.min_width_spin, 'setAccessibleName', 'Legacy.sdadef8ae58c13b81')
        self.min_width_spin.setMinimumHeight(44)
        self.min_width_spin.setMinimum(1)
        self.min_width_spin.setMaximum(9999)
        self.min_width_spin.setValue(100)
        size_layout.addWidget(_ui_widget(QLabel, 'Legacy.s70071bce279eb5a9', 'setText'))
        size_layout.addWidget(self.min_width_spin)

        self.min_height_spin = QSpinBox()
        _ui_bind(self.min_height_spin, 'setAccessibleName', 'Legacy.sbe3d00b05b387bd8')
        self.min_height_spin.setMinimumHeight(44)
        self.min_height_spin.setMinimum(1)
        self.min_height_spin.setMaximum(9999)
        self.min_height_spin.setValue(100)
        size_layout.addWidget(_ui_widget(QLabel, 'Legacy.s537f68695dfe0efd', 'setText'))
        size_layout.addWidget(self.min_height_spin)

        size_layout.addStretch()
        options_layout.addRow("Minimum Size (px):", size_layout)

        # Page range
        page_range_layout = QHBoxLayout()
        self.page_range_check = _ui_widget(QCheckBox, 'Legacy.s500277376e9ea8fc', 'setText')
        _ui_bind(self.page_range_check, 'setAccessibleName', 'Legacy.sb92076db77e8dd15')
        self.page_range_check.setMinimumHeight(44)
        page_range_layout.addWidget(self.page_range_check)

        self.start_page_spin = QSpinBox()
        _ui_bind(self.start_page_spin, 'setAccessibleName', 'Legacy.s8cefd6c52d03fe65')
        self.start_page_spin.setMinimumHeight(44)
        self.start_page_spin.setMinimum(1)
        self.start_page_spin.setMaximum(9999)
        self.start_page_spin.setEnabled(False)
        page_range_layout.addWidget(_ui_widget(QLabel, 'Legacy.sdc45d36f35e84e07', 'setText'))
        page_range_layout.addWidget(self.start_page_spin)

        self.end_page_spin = QSpinBox()
        _ui_bind(self.end_page_spin, 'setAccessibleName', 'Legacy.sf1aa36b86021c1ba')
        self.end_page_spin.setMinimumHeight(44)
        self.end_page_spin.setMinimum(1)
        self.end_page_spin.setMaximum(9999)
        self.end_page_spin.setEnabled(False)
        page_range_layout.addWidget(_ui_widget(QLabel, 'Legacy.s2b5fc5c94f64250c', 'setText'))
        page_range_layout.addWidget(self.end_page_spin)

        page_range_layout.addStretch()
        options_layout.addRow(page_range_layout)

        layout.addWidget(options_group)

        # Preview section
        preview_group = _ui_widget(QGroupBox, 'Legacy.sd04fb70f2c2822fd', 'setTitle')
        preview_layout = QVBoxLayout(preview_group)

        self.image_count_label = _ui_widget(QLabel, 'Legacy.sd4947438507c15a8', 'setText')
        self.image_count_label.setAlignment(Qt.AlignCenter)
        preview_layout.addWidget(self.image_count_label)

        self.scan_btn = _ui_widget(SecondaryButton, 'Legacy.sa8dd28d4c0d58b26', 'setText')
        _ui_bind(self.scan_btn, 'setAccessibleName', 'Legacy.s52d4014c70345d7e')
        self.scan_btn.setEnabled(False)
        preview_layout.addWidget(self.scan_btn)

        layout.addWidget(preview_group)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancel_btn = _ui_widget(SecondaryButton, 'Legacy.s19766ed6ccb2f4a3', 'setText')
        _ui_bind(self.cancel_btn, 'setAccessibleName', 'Legacy.s3e46bf3320176bd1')
        button_layout.addWidget(self.cancel_btn)

        self.extract_btn = _ui_widget(PrimaryButton, 'Legacy.s6a8eaf282cf29e30', 'setText')
        _ui_bind(self.extract_btn, 'setAccessibleName', 'Legacy.s6b780c804b624b10')
        self.extract_btn.setEnabled(False)
        button_layout.addWidget(self.extract_btn)

        layout.addLayout(button_layout)

    def setup_connections(self):
        self.browse_input_btn.clicked.connect(self.browse_input_file)
        self.browse_output_btn.clicked.connect(self.browse_output_dir)
        self.page_range_check.toggled.connect(self.toggle_page_range)
        self.scan_btn.clicked.connect(self.scan_for_images)
        self.cancel_btn.clicked.connect(self.reject)
        self.extract_btn.clicked.connect(self.accept)

        # Auto-generate output directory when input changes
        self.input_edit.textChanged.connect(self.auto_generate_output)

    def browse_input_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select PDF File", "", "PDF Files (*.pdf)"
        )
        if file_path:
            self.input_file = file_path
            self.input_edit.setText(file_path)
            self.scan_btn.setEnabled(True)

    def browse_output_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if dir_path:
            self.output_location = dir_path
            self.output_edit.setText(dir_path)
            self.update_extract_button()

    def auto_generate_output(self):
        if self.input_file:
            base_name = os.path.splitext(os.path.basename(self.input_file))[0]
            output_dir = os.path.join(
                os.path.dirname(self.input_file),
                f"{base_name}_extracted_images",
            )
            self.output_location = output_dir
            self.output_edit.setText(output_dir)
            self.update_extract_button()

    def toggle_page_range(self, checked):
        self.start_page_spin.setEnabled(checked)
        self.end_page_spin.setEnabled(checked)
        if checked:
            self.start_page_spin.setValue(1)
            self.end_page_spin.setValue(1)

    def update_extract_button(self):
        has_input = bool(self.input_file)
        has_output = bool(self.output_location)
        self.extract_btn.setEnabled(has_input and has_output)

    def scan_for_images(self):
        if not self.input_file:
            return

        try:
            import fitz

            doc = fitz.open(self.input_file)

            total_images = 0
            for page_num in range(len(doc)):
                page = doc[page_num]
                images = page.get_images()
                total_images += len(images)

            self.image_count_label.setText(
                f"Found {total_images} images in {len(doc)} pages"
            )
            doc.close()
        except:
            self.image_count_label.setText("Could not scan for images")

    def get_extraction_options(self) -> Dict[str, Any]:
        options = {
            "format": self.format_combo.currentText(),
            "min_width": self.min_width_spin.value(),
            "min_height": self.min_height_spin.value(),
        }

        if self.page_range_check.isChecked():
            options["page_range"] = (
                self.start_page_spin.value() - 1,  # Convert to 0-based
                self.end_page_spin.value() - 1,
            )

        return options


class PDFMetadataExtractionDialog(PDFExtractionDialogBase):
    """Dialog for PDF metadata extraction parameters"""

    def __init__(self, parent=None):
        super().__init__(parent, "Metadata")

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Input file section
        input_group = _ui_widget(QGroupBox, 'Legacy.s22bc9850e3d02875', 'setTitle')
        input_layout = QHBoxLayout(input_group)

        self.input_edit = TextInput(
            "Input PDF file",
            "Select PDF file...",
            accessible_name="Input PDF file",
        )
        self.input_edit.setReadOnly(True)
        input_layout.addWidget(self.input_edit)

        self.browse_input_btn = _ui_widget(SecondaryButton, 'Legacy.sc58a6bd402efb06c', 'setText')
        _ui_bind(self.browse_input_btn, 'setAccessibleName', 'Legacy.s6a0c40ebf4735e07')
        input_layout.addWidget(self.browse_input_btn)

        layout.addWidget(input_group)

        # Output file section
        output_group = _ui_widget(QGroupBox, 'Legacy.s2d3a2aa2191a98de', 'setTitle')
        output_layout = QHBoxLayout(output_group)

        self.output_edit = TextInput(
            "Output metadata JSON file",
            "Output JSON file...",
            accessible_name="Output metadata JSON file",
        )
        output_layout.addWidget(self.output_edit)

        self.browse_output_btn = _ui_widget(SecondaryButton, 'Legacy.sc58a6bd402efb06c', 'setText')
        _ui_bind(self.browse_output_btn, 'setAccessibleName', 'Legacy.sfc96835debadaf35')
        output_layout.addWidget(self.browse_output_btn)

        layout.addWidget(output_group)

        # Extraction options
        options_group = _ui_widget(QGroupBox, 'Legacy.s8acd4d5d395cfab8', 'setTitle')
        options_layout = QFormLayout(options_group)

        # Include extended metadata
        self.extended_check = _ui_widget(QCheckBox, 'Legacy.s1b0c8642c563509a', 'setText')
        _ui_bind(self.extended_check, 'setAccessibleName', 'Legacy.s1b0c8642c563509a')
        self.extended_check.setMinimumHeight(44)
        self.extended_check.setChecked(True)
        options_layout.addRow("Extended Info:", self.extended_check)

        layout.addWidget(options_group)

        # Preview section
        preview_group = _ui_widget(QGroupBox, 'Legacy.s3f2d7cffe4978503', 'setTitle')
        preview_layout = QVBoxLayout(preview_group)

        self.preview_text = QPlainTextEdit()
        _ui_bind(self.preview_text, 'setAccessibleName', 'Legacy.s6c071a26b022dbea')
        self.preview_text.setMaximumHeight(150)
        _ui_bind(self.preview_text, 'setPlaceholderText', 'Legacy.s491c415ecb7311f4')
        self.preview_text.setReadOnly(True)
        preview_layout.addWidget(self.preview_text)

        self.preview_btn = _ui_widget(SecondaryButton, 'Legacy.s9e297cc8f9ca7c57', 'setText')
        _ui_bind(self.preview_btn, 'setAccessibleName', 'Legacy.s491a85faff677129')
        self.preview_btn.setEnabled(False)
        preview_layout.addWidget(self.preview_btn)

        layout.addWidget(preview_group)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancel_btn = _ui_widget(SecondaryButton, 'Legacy.s19766ed6ccb2f4a3', 'setText')
        _ui_bind(self.cancel_btn, 'setAccessibleName', 'Legacy.s2f6b0e043db428eb')
        button_layout.addWidget(self.cancel_btn)

        self.extract_btn = _ui_widget(PrimaryButton, 'Legacy.s24051b380a89f902', 'setText')
        _ui_bind(self.extract_btn, 'setAccessibleName', 'Legacy.se2dda45c71a1626b')
        self.extract_btn.setEnabled(False)
        button_layout.addWidget(self.extract_btn)

        layout.addLayout(button_layout)

    def setup_connections(self):
        self.browse_input_btn.clicked.connect(self.browse_input_file)
        self.browse_output_btn.clicked.connect(self.browse_output_file)
        self.preview_btn.clicked.connect(self.preview_metadata)
        self.cancel_btn.clicked.connect(self.reject)
        self.extract_btn.clicked.connect(self.accept)

        # Auto-generate output filename when input changes
        self.input_edit.textChanged.connect(self.auto_generate_output)

    def browse_input_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select PDF File", "", "PDF Files (*.pdf)"
        )
        if file_path:
            self.input_file = file_path
            self.input_edit.setText(file_path)
            self.preview_btn.setEnabled(True)

    def browse_output_file(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Metadata File As", "", "JSON Files (*.json)"
        )
        if file_path:
            self.output_location = file_path
            self.output_edit.setText(file_path)
            self.update_extract_button()

    def auto_generate_output(self):
        if self.input_file:
            base_name = os.path.splitext(self.input_file)[0]
            output_file = f"{base_name}_metadata.json"
            self.output_location = output_file
            self.output_edit.setText(output_file)
            self.update_extract_button()

    def update_extract_button(self):
        has_input = bool(self.input_file)
        has_output = bool(self.output_location)
        self.extract_btn.setEnabled(has_input and has_output)

    def preview_metadata(self):
        if not self.input_file:
            return

        try:
            import fitz

            doc = fitz.open(self.input_file)
            metadata = doc.metadata

            preview_lines = []
            if metadata:
                for key, value in metadata.items():
                    if value:  # Only show non-empty values
                        preview_lines.append(f"{key}: {value}")

            if preview_lines:
                self.preview_text.setPlainText("\n".join(preview_lines[:10]))
            else:
                self.preview_text.setPlainText("No metadata found")

            doc.close()
        except:
            self.preview_text.setPlainText("Preview not available")

    def get_extraction_options(self) -> Dict[str, Any]:
        return {"include_extended": self.extended_check.isChecked()}


class PDFTableExtractionDialog(PDFExtractionDialogBase):
    """Dialog for PDF table extraction parameters"""

    def __init__(self, parent=None):
        super().__init__(parent, "Table")

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Input file section
        input_group = _ui_widget(QGroupBox, 'Legacy.s22bc9850e3d02875', 'setTitle')
        input_layout = QHBoxLayout(input_group)

        self.input_edit = TextInput(
            "Input PDF file",
            "Select PDF file...",
            accessible_name="Input PDF file",
        )
        self.input_edit.setReadOnly(True)
        input_layout.addWidget(self.input_edit)

        self.browse_input_btn = _ui_widget(SecondaryButton, 'Legacy.sc58a6bd402efb06c', 'setText')
        _ui_bind(self.browse_input_btn, 'setAccessibleName', 'Legacy.s6a0c40ebf4735e07')
        input_layout.addWidget(self.browse_input_btn)

        layout.addWidget(input_group)

        # Output directory section
        output_group = _ui_widget(QGroupBox, 'Legacy.s2d8842920b678b49', 'setTitle')
        output_layout = QHBoxLayout(output_group)

        self.output_edit = TextInput(
            "Output directory for tables",
            "Output directory...",
            accessible_name="Output directory for tables",
        )
        output_layout.addWidget(self.output_edit)

        self.browse_output_btn = _ui_widget(SecondaryButton, 'Legacy.sc58a6bd402efb06c', 'setText')
        _ui_bind(self.browse_output_btn, 'setAccessibleName', 'Legacy.s9f20baa3d056c434')
        output_layout.addWidget(self.browse_output_btn)

        layout.addWidget(output_group)

        # Extraction options
        options_group = _ui_widget(QGroupBox, 'Legacy.s2c51c555b216e268', 'setTitle')
        options_layout = QFormLayout(options_group)

        # Extraction method
        self.method_combo = QComboBox()
        _ui_bind(self.method_combo, 'setAccessibleName', 'Legacy.s1c016908eacba70e')
        self.method_combo.setMinimumHeight(44)
        self.method_combo.addItems(["camelot", "pdfplumber"])
        self.method_combo.setCurrentText("camelot")
        options_layout.addRow("Extraction Method:", self.method_combo)

        # Camelot-specific options
        self.camelot_group = _ui_widget(QGroupBox, 'Legacy.seebd1cae89de5001', 'setTitle')
        camelot_layout = QFormLayout(self.camelot_group)

        self.flavor_combo = QComboBox()
        _ui_bind(self.flavor_combo, 'setAccessibleName', 'Legacy.seedbbc5942c03de2')
        self.flavor_combo.setMinimumHeight(44)
        self.flavor_combo.addItems(["lattice", "stream"])
        self.flavor_combo.setCurrentText("lattice")
        camelot_layout.addRow("Table Detection:", self.flavor_combo)

        options_layout.addRow(self.camelot_group)

        # Page range
        page_range_layout = QHBoxLayout()
        self.page_range_check = _ui_widget(QCheckBox, 'Legacy.s500277376e9ea8fc', 'setText')
        _ui_bind(self.page_range_check, 'setAccessibleName', 'Legacy.sb92076db77e8dd15')
        self.page_range_check.setMinimumHeight(44)
        page_range_layout.addWidget(self.page_range_check)

        self.start_page_spin = QSpinBox()
        _ui_bind(self.start_page_spin, 'setAccessibleName', 'Legacy.s8cefd6c52d03fe65')
        self.start_page_spin.setMinimumHeight(44)
        self.start_page_spin.setMinimum(1)
        self.start_page_spin.setMaximum(9999)
        self.start_page_spin.setEnabled(False)
        page_range_layout.addWidget(_ui_widget(QLabel, 'Legacy.sdc45d36f35e84e07', 'setText'))
        page_range_layout.addWidget(self.start_page_spin)

        self.end_page_spin = QSpinBox()
        _ui_bind(self.end_page_spin, 'setAccessibleName', 'Legacy.sf1aa36b86021c1ba')
        self.end_page_spin.setMinimumHeight(44)
        self.end_page_spin.setMinimum(1)
        self.end_page_spin.setMaximum(9999)
        self.end_page_spin.setEnabled(False)
        page_range_layout.addWidget(_ui_widget(QLabel, 'Legacy.s2b5fc5c94f64250c', 'setText'))
        page_range_layout.addWidget(self.end_page_spin)

        page_range_layout.addStretch()
        options_layout.addRow(page_range_layout)

        layout.addWidget(options_group)

        # Preview section
        preview_group = _ui_widget(QGroupBox, 'Legacy.s0f9061fb517ec129', 'setTitle')
        preview_layout = QVBoxLayout(preview_group)

        self.table_count_label = _ui_widget(QLabel, 'Legacy.sb0bc4469609d6597', 'setText')
        self.table_count_label.setAlignment(Qt.AlignCenter)
        preview_layout.addWidget(self.table_count_label)

        self.scan_btn = _ui_widget(SecondaryButton, 'Legacy.s5e41742d2bfa53d8', 'setText')
        _ui_bind(self.scan_btn, 'setAccessibleName', 'Legacy.s978b949b5323d05c')
        self.scan_btn.setEnabled(False)
        preview_layout.addWidget(self.scan_btn)

        layout.addWidget(preview_group)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancel_btn = _ui_widget(SecondaryButton, 'Legacy.s19766ed6ccb2f4a3', 'setText')
        _ui_bind(self.cancel_btn, 'setAccessibleName', 'Legacy.s20808208e3832733')
        button_layout.addWidget(self.cancel_btn)

        self.extract_btn = _ui_widget(PrimaryButton, 'Legacy.se28f43c9fd4036b1', 'setText')
        _ui_bind(self.extract_btn, 'setAccessibleName', 'Legacy.sf1a569f7d44b120a')
        self.extract_btn.setEnabled(False)
        button_layout.addWidget(self.extract_btn)

        layout.addLayout(button_layout)

    def setup_connections(self):
        self.browse_input_btn.clicked.connect(self.browse_input_file)
        self.browse_output_btn.clicked.connect(self.browse_output_dir)
        self.method_combo.currentTextChanged.connect(self.update_method_options)
        self.page_range_check.toggled.connect(self.toggle_page_range)
        self.scan_btn.clicked.connect(self.scan_for_tables)
        self.cancel_btn.clicked.connect(self.reject)
        self.extract_btn.clicked.connect(self.accept)

        # Auto-generate output directory when input changes
        self.input_edit.textChanged.connect(self.auto_generate_output)

    def browse_input_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select PDF File", "", "PDF Files (*.pdf)"
        )
        if file_path:
            self.input_file = file_path
            self.input_edit.setText(file_path)
            self.scan_btn.setEnabled(True)

    def browse_output_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if dir_path:
            self.output_location = dir_path
            self.output_edit.setText(dir_path)
            self.update_extract_button()

    def auto_generate_output(self):
        if self.input_file:
            base_name = os.path.splitext(os.path.basename(self.input_file))[0]
            output_dir = os.path.join(
                os.path.dirname(self.input_file),
                f"{base_name}_extracted_tables",
            )
            self.output_location = output_dir
            self.output_edit.setText(output_dir)
            self.update_extract_button()

    def update_method_options(self, method):
        self.camelot_group.setVisible(method == "camelot")

    def toggle_page_range(self, checked):
        self.start_page_spin.setEnabled(checked)
        self.end_page_spin.setEnabled(checked)
        if checked:
            self.start_page_spin.setValue(1)
            self.end_page_spin.setValue(1)

    def update_extract_button(self):
        has_input = bool(self.input_file)
        has_output = bool(self.output_location)
        self.extract_btn.setEnabled(has_input and has_output)

    def scan_for_tables(self):
        if not self.input_file:
            return

        try:
            # Simple table count estimation
            import pdfplumber

            with pdfplumber.open(self.input_file) as pdf:
                total_tables = 0
                for page in pdf.pages[:5]:  # Check first 5 pages
                    tables = page.extract_tables()
                    if tables:
                        total_tables += len(tables)

                self.table_count_label.setText(
                    f"Estimated {total_tables} tables in first 5 pages"
                )
        except:
            self.table_count_label.setText("Could not scan for tables")

    def get_extraction_options(self) -> Dict[str, Any]:
        options = {"method": self.method_combo.currentText()}

        if self.method_combo.currentText() == "camelot":
            options["camelot_options"] = {"flavor": self.flavor_combo.currentText()}

        if self.page_range_check.isChecked():
            options["page_range"] = (
                self.start_page_spin.value() - 1,  # Convert to 0-based
                self.end_page_spin.value() - 1,
            )

        return options


class PDFLinkExtractionDialog(PDFExtractionDialogBase):
    """Dialog for PDF link extraction parameters"""

    def __init__(self, parent=None):
        super().__init__(parent, "Link")

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Input file section
        input_group = _ui_widget(QGroupBox, 'Legacy.s22bc9850e3d02875', 'setTitle')
        input_layout = QHBoxLayout(input_group)

        self.input_edit = TextInput(
            "Input PDF file",
            "Select PDF file...",
            accessible_name="Input PDF file",
        )
        self.input_edit.setReadOnly(True)
        input_layout.addWidget(self.input_edit)

        self.browse_input_btn = _ui_widget(SecondaryButton, 'Legacy.sc58a6bd402efb06c', 'setText')
        _ui_bind(self.browse_input_btn, 'setAccessibleName', 'Legacy.s6a0c40ebf4735e07')
        input_layout.addWidget(self.browse_input_btn)

        layout.addWidget(input_group)

        # Output file section
        output_group = _ui_widget(QGroupBox, 'Legacy.sdf0565b5501bb4f9', 'setTitle')
        output_layout = QHBoxLayout(output_group)

        self.output_edit = TextInput(
            "Output links JSON file",
            "Output JSON file...",
            accessible_name="Output links JSON file",
        )
        output_layout.addWidget(self.output_edit)

        self.browse_output_btn = _ui_widget(SecondaryButton, 'Legacy.sc58a6bd402efb06c', 'setText')
        _ui_bind(self.browse_output_btn, 'setAccessibleName', 'Legacy.sfc96835debadaf35')
        output_layout.addWidget(self.browse_output_btn)

        layout.addWidget(output_group)

        # Extraction options
        options_group = _ui_widget(QGroupBox, 'Legacy.sbe72fb6312430196', 'setTitle')
        options_layout = QFormLayout(options_group)

        # Include internal links
        self.internal_links_check = _ui_widget(QCheckBox, 'Legacy.s542e9eab9b7caacf', 'setText')
        _ui_bind(self.internal_links_check, 'setAccessibleName', 'Legacy.s542e9eab9b7caacf')
        self.internal_links_check.setMinimumHeight(44)
        self.internal_links_check.setChecked(True)
        options_layout.addRow("Internal Links:", self.internal_links_check)

        # Page range
        page_range_layout = QHBoxLayout()
        self.page_range_check = _ui_widget(QCheckBox, 'Legacy.s500277376e9ea8fc', 'setText')
        _ui_bind(self.page_range_check, 'setAccessibleName', 'Legacy.sb92076db77e8dd15')
        self.page_range_check.setMinimumHeight(44)
        page_range_layout.addWidget(self.page_range_check)

        self.start_page_spin = QSpinBox()
        _ui_bind(self.start_page_spin, 'setAccessibleName', 'Legacy.s8cefd6c52d03fe65')
        self.start_page_spin.setMinimumHeight(44)
        self.start_page_spin.setMinimum(1)
        self.start_page_spin.setMaximum(9999)
        self.start_page_spin.setEnabled(False)
        page_range_layout.addWidget(_ui_widget(QLabel, 'Legacy.sdc45d36f35e84e07', 'setText'))
        page_range_layout.addWidget(self.start_page_spin)

        self.end_page_spin = QSpinBox()
        _ui_bind(self.end_page_spin, 'setAccessibleName', 'Legacy.sf1aa36b86021c1ba')
        self.end_page_spin.setMinimumHeight(44)
        self.end_page_spin.setMinimum(1)
        self.end_page_spin.setMaximum(9999)
        self.end_page_spin.setEnabled(False)
        page_range_layout.addWidget(_ui_widget(QLabel, 'Legacy.s2b5fc5c94f64250c', 'setText'))
        page_range_layout.addWidget(self.end_page_spin)

        page_range_layout.addStretch()
        options_layout.addRow(page_range_layout)

        layout.addWidget(options_group)

        # Preview section
        preview_group = _ui_widget(QGroupBox, 'Legacy.s2428b7a70078e3d4', 'setTitle')
        preview_layout = QVBoxLayout(preview_group)

        self.preview_text = QPlainTextEdit()
        _ui_bind(self.preview_text, 'setAccessibleName', 'Legacy.s9c80ca9d598cefe9')
        self.preview_text.setMaximumHeight(120)
        _ui_bind(self.preview_text, 'setPlaceholderText', 'Legacy.s2de93c9798c52a70')
        self.preview_text.setReadOnly(True)
        preview_layout.addWidget(self.preview_text)

        self.preview_btn = _ui_widget(SecondaryButton, 'Legacy.s990c20eb1ae9ecc5', 'setText')
        _ui_bind(self.preview_btn, 'setAccessibleName', 'Legacy.se36acb856002f5e5')
        self.preview_btn.setEnabled(False)
        preview_layout.addWidget(self.preview_btn)

        layout.addWidget(preview_group)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancel_btn = _ui_widget(SecondaryButton, 'Legacy.s19766ed6ccb2f4a3', 'setText')
        _ui_bind(self.cancel_btn, 'setAccessibleName', 'Legacy.s838ee2ef3c7d809e')
        button_layout.addWidget(self.cancel_btn)

        self.extract_btn = _ui_widget(PrimaryButton, 'Legacy.s02bbd8b6de889b96', 'setText')
        _ui_bind(self.extract_btn, 'setAccessibleName', 'Legacy.sb8db2bd817769cd9')
        self.extract_btn.setEnabled(False)
        button_layout.addWidget(self.extract_btn)

        layout.addLayout(button_layout)

    def setup_connections(self):
        self.browse_input_btn.clicked.connect(self.browse_input_file)
        self.browse_output_btn.clicked.connect(self.browse_output_file)
        self.page_range_check.toggled.connect(self.toggle_page_range)
        self.preview_btn.clicked.connect(self.preview_links)
        self.cancel_btn.clicked.connect(self.reject)
        self.extract_btn.clicked.connect(self.accept)

        # Auto-generate output filename when input changes
        self.input_edit.textChanged.connect(self.auto_generate_output)

    def browse_input_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select PDF File", "", "PDF Files (*.pdf)"
        )
        if file_path:
            self.input_file = file_path
            self.input_edit.setText(file_path)
            self.preview_btn.setEnabled(True)

    def browse_output_file(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Links File As", "", "JSON Files (*.json)"
        )
        if file_path:
            self.output_location = file_path
            self.output_edit.setText(file_path)
            self.update_extract_button()

    def auto_generate_output(self):
        if self.input_file:
            base_name = os.path.splitext(self.input_file)[0]
            output_file = f"{base_name}_links.json"
            self.output_location = output_file
            self.output_edit.setText(output_file)
            self.update_extract_button()

    def toggle_page_range(self, checked):
        self.start_page_spin.setEnabled(checked)
        self.end_page_spin.setEnabled(checked)
        if checked:
            self.start_page_spin.setValue(1)
            self.end_page_spin.setValue(1)

    def update_extract_button(self):
        has_input = bool(self.input_file)
        has_output = bool(self.output_location)
        self.extract_btn.setEnabled(has_input and has_output)

    def preview_links(self):
        if not self.input_file:
            return

        try:
            import fitz

            doc = fitz.open(self.input_file)

            links = []
            for page_num in range(min(3, len(doc))):  # Check first 3 pages
                page = doc[page_num]
                page_links = page.get_links()

                for link in page_links:
                    if link.get("uri"):
                        links.append(f"Page {page_num + 1}: {link['uri']}")
                    elif link.get("page") is not None:
                        links.append(
                            f"Page {page_num + 1}: Internal -> Page {link['page'] + 1}"
                        )

            if links:
                preview_text = "\n".join(links[:10])
                if len(links) > 10:
                    preview_text += f"\n... and {len(links) - 10} more"
                self.preview_text.setPlainText(preview_text)
            else:
                self.preview_text.setPlainText("No links found in first 3 pages")

            doc.close()
        except:
            self.preview_text.setPlainText("Preview not available")

    def get_extraction_options(self) -> Dict[str, Any]:
        options = {"include_internal_links": self.internal_links_check.isChecked()}

        if self.page_range_check.isChecked():
            options["page_range"] = (
                self.start_page_spin.value() - 1,  # Convert to 0-based
                self.end_page_spin.value() - 1,
            )

        return options


if __name__ == "__main__":
    """Test the extraction parameter dialogs"""
    import sys

    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # Test text extraction dialog
    dialog = PDFTextExtractionDialog()
    if dialog.exec_() == QDialog.Accepted:
        print("Text extraction parameters:")
        print(f"Input: {dialog.get_input_file()}")
        print(f"Output: {dialog.get_output_location()}")
        print(f"Options: {dialog.get_extraction_options()}")

    sys.exit(app.exec_())
