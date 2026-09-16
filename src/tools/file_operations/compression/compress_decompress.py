"""
Compress/Decompress Tool for Richard's File Utilities
Handles compression and decompression with various archive formats.
"""
from src.rfu.localization import localized_widget as _ui_widget, bind_literal as _ui_bind
from src.rfu import font_tokens

import json
import os
import tarfile
import zipfile
from typing import Dict

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QCheckBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSlider,
)

from src.gui.components.buttons import PrimaryButton, SecondaryButton
from src.gui.components.inputs import TextInput
from src.gui.themes import token

# Import StandardWindow for menu integration
try:
    from src.gui.standard_window import StandardWindow
except ImportError:
    # Fallback for standalone execution
    try:
        from src.gui.standard_window import StandardWindow
    except ImportError:
        # Final fallback - create a minimal StandardWindow substitute
        from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget

        class StandardWindow(QMainWindow):
            def __init__(self, title="", window_type="utility"):
                super().__init__()
                self.setWindowTitle(title)
                self.central_widget = QWidget()
                self.setCentralWidget(self.central_widget)
                self.main_layout = QVBoxLayout(self.central_widget)

            def show_status_message(self, message, timeout=3000):
                status_bar = self.statusBar()
                if status_bar:
                    status_bar.showMessage(message, timeout)

            def show_error_dialog(self, title, message):
                QMessageBox.critical(self, title, message)

            def show_info_dialog(self, title, message):
                QMessageBox.information(self, title, message)

            def show_warning_dialog(self, title, message):
                QMessageBox.warning(self, title, message)

            def get_file_path(self, title="Select File", file_filter="All Files (*)"):
                return QFileDialog.getOpenFileName(self, title, "", file_filter)[0]

            def get_save_file_path(
                self, title="Save File", file_filter="All Files (*)"
            ):
                return QFileDialog.getSaveFileName(self, title, "", file_filter)[0]


# Archive format constants
FORMAT_ZIP = "ZIP"
FORMAT_7Z = "7Z"
FORMAT_TAR_GZ = "TAR.GZ"
FORMAT_TAR_BZ2 = "TAR.BZ2"
ARCHIVE_EXT_ZIP = ".zip"
ARCHIVE_EXT_7Z = ".7z"
ARCHIVE_EXT_TAR_GZ = ".tar.gz"
ARCHIVE_EXT_TAR_BZ2 = ".tar.bz2"


def show_error_dialog(title, message, parent=None):
    """Show error dialog."""
    QMessageBox.critical(parent, title, message)


def show_info_dialog(title, message, parent=None):
    """Show info dialog."""
    QMessageBox.information(parent, title, message)


def get_existing_directory(parent, caption):
    """Get existing directory."""
    return QFileDialog.getExistingDirectory(parent, caption)


def get_open_file_name(caption, parent, file_filter):
    """Get open file name."""
    return QFileDialog.getOpenFileName(parent, caption, "", file_filter)[0]


def get_save_file_name(caption, parent, file_filter):
    """Get save file name."""
    return QFileDialog.getSaveFileName(parent, caption, "", file_filter)[0]


class CompressDecompressApp(StandardWindow):
    """Handles compression and decompression with various archive formats."""

    def __init__(self):
        """Initialize the compression/decompression window."""
        try:
            super().__init__(
                title="Compress/Decompress Files - Richard's File Utilities",
                window_type="utility",
            )
        except TypeError:
            super().__init__()
            title = "Compress/Decompress Files - Richard's File Utilities"
            self.setWindowTitle(title)

        self.init_ui()
        self._setup_menu_callbacks()

    def _setup_menu_callbacks(self):
        """Setup tool-specific menu callbacks."""
        if hasattr(self, "menu_manager"):
            # File menu callbacks
            self.menu_manager.register_callback(
                "new_compression", self.new_compression_session
            )
            self.menu_manager.register_callback(
                "save_file", self.save_compression_settings
            )
            self.menu_manager.register_callback(
                "open_file", self.load_compression_settings
            )
            self.menu_manager.register_callback("export_data", self.export_archive_list)
            self.menu_manager.register_callback("import_data", self.import_archive_list)
            self.menu_manager.register_callback(
                "print_document", self.print_compression_report
            )

            # Edit menu callbacks
            self.menu_manager.register_callback("cut", self.cut_text)
            self.menu_manager.register_callback("copy", self.copy_text)
            self.menu_manager.register_callback("paste", self.paste_text)
            self.menu_manager.register_callback("select_all", self.select_all_text)
            self.menu_manager.register_callback("find", self.find_in_paths)

            # View menu callbacks
            self.menu_manager.register_callback("zoom_in", self.zoom_in)
            self.menu_manager.register_callback("zoom_out", self.zoom_out)
            self.menu_manager.register_callback("zoom_reset", self.zoom_reset)

            # Tools menu callbacks
            self.menu_manager.register_callback(
                "show_options", self.show_compression_options
            )
            self.menu_manager.register_callback("verify_archive", self.verify_archive)
            self.menu_manager.register_callback(
                "batch_operations", self.show_batch_operations
            )

            # Help menu callbacks
            self.menu_manager.register_callback("help_compression", self.show_help)

    def new_compression_session(self):
        """Start a new compression session."""
        self.clear_fields()
        self.show_status_message("New compression session started")

    def clear_fields(self):
        """Clear all input fields for a new compression task."""
        self.lineEditFolder.clear()
        self.lineEditOutput.clear()
        self.lineEditDecompress.clear()
        self.lineEditPassword.clear()
        self.comboFormat.setCurrentIndex(0)
        self.sliderCompLevel.setValue(6)

    def save_compression_settings(self):
        """Save current compression settings to file."""
        settings = {
            "folder_path": self.lineEditFolder.text(),
            "output_path": self.lineEditOutput.text(),
            "format": self.comboFormat.currentText(),
            "compression_level": self.sliderCompLevel.value(),
            "has_password": bool(self.lineEditPassword.text()),
        }

        file_path = self.get_save_file_path(
            "Save Compression Settings", "JSON Files (*.json);;All Files (*)"
        )

        if file_path:
            try:
                with open(file_path, "w") as f:
                    json.dump(settings, f, indent=2)
                self.show_info_dialog(
                    "Settings Saved",
                    f"Compression settings saved to {file_path}",
                )
            except Exception as e:
                self.show_error_dialog(
                    "Save Error", f"Failed to save settings: {str(e)}"
                )

    def load_compression_settings(self):
        """Load compression settings from file."""
        file_path = self.get_file_path(
            "Load Compression Settings", "JSON Files (*.json);;All Files (*)"
        )

        if file_path:
            try:
                with open(file_path, "r") as f:
                    settings = json.load(f)

                self.lineEditFolder.setText(settings.get("folder_path", ""))
                self.lineEditOutput.setText(settings.get("output_path", ""))

                format_text = settings.get("format", "ZIP")
                index = self.comboFormat.findText(format_text)
                if index >= 0:
                    self.comboFormat.setCurrentIndex(index)

                self.sliderCompLevel.setValue(settings.get("compression_level", 6))

                self.show_info_dialog(
                    "Settings Loaded",
                    f"Compression settings loaded from {file_path}",
                )
            except Exception as e:
                self.show_error_dialog(
                    "Load Error", f"Failed to load settings: {str(e)}"
                )

    def export_archive_list(self):
        """Export list of processed archives."""
        self.show_info_dialog(
            "Export Archive List",
            "Archive list export functionality will be implemented.",
        )

    def import_archive_list(self):
        """Import list of archives to process."""
        self.show_info_dialog(
            "Import Archive List",
            "Archive list import functionality will be implemented.",
        )

    def print_compression_report(self):
        """Print compression operation report."""
        self.show_info_dialog(
            "Print Report",
            "Compression report printing functionality will be implemented.",
        )

    def cut_text(self):
        """Cut text from focused widget."""
        focused = QApplication.focusWidget()
        if focused and hasattr(focused, "cut"):
            focused.cut()

    def copy_text(self):
        """Copy text from focused widget."""
        focused = QApplication.focusWidget()
        if focused and hasattr(focused, "copy"):
            focused.copy()

    def paste_text(self):
        """Paste text to focused widget."""
        focused = QApplication.focusWidget()
        if focused and hasattr(focused, "paste"):
            focused.paste()

    def select_all_text(self):
        """Select all text in focused widget."""
        focused = QApplication.focusWidget()
        if focused and hasattr(focused, "selectAll"):
            focused.selectAll()

    def find_in_paths(self):
        """Find text in file paths."""
        self.show_info_dialog(
            "Find in Paths", "Find functionality will be implemented."
        )

    def zoom_in(self):
        """Increase interface zoom level."""
        self.show_status_message("Zoom in functionality not applicable")

    def zoom_out(self):
        """Decrease interface zoom level."""
        self.show_status_message("Zoom out functionality not applicable")

    def zoom_reset(self):
        """Reset interface zoom level."""
        self.show_status_message("Zoom reset functionality not applicable")

    def show_compression_options(self):
        """Show compression-specific options dialog."""
        self.show_preferences()

    def verify_archive(self):
        """Verify integrity of selected archive."""
        archive_path = self.lineEditDecompress.text().strip()
        if not archive_path:
            self.show_warning_dialog(
                "No Archive Selected",
                "Please select an archive file to verify.",
            )
            return

        if not os.path.exists(archive_path):
            self.show_error_dialog(
                "File Not Found", f"Archive file not found: {archive_path}"
            )
            return

        try:
            if archive_path.endswith(ARCHIVE_EXT_ZIP):
                with zipfile.ZipFile(archive_path, "r") as zf:
                    bad_file = zf.testzip()
                    if bad_file:
                        self.show_error_dialog(
                            "Archive Corrupted",
                            f"Corrupted file found: {bad_file}",
                        )
                    else:
                        self.show_info_dialog(
                            "Archive Verified",
                            "Archive integrity verified successfully.",
                        )
            elif archive_path.endswith(ARCHIVE_EXT_TAR_GZ) or archive_path.endswith(ARCHIVE_EXT_TAR_BZ2):
                with tarfile.open(archive_path, "r") as tf:
                    # Basic verification - try to list contents
                    tf.getnames()
                    self.show_info_dialog(
                        "Archive Verified",
                        "Archive integrity verified successfully.",
                    )
            else:
                self.show_warning_dialog(
                    "Unsupported Format",
                    "Verification not supported for this archive format.",
                )
        except Exception as e:
            self.show_error_dialog(
                "Verification Failed", f"Archive verification failed: {str(e)}"
            )

    def show_batch_operations(self):
        """Show batch operations dialog."""
        self.show_info_dialog(
            "Batch Operations",
            "Batch operations functionality will be implemented.",
        )

    def show_help(self):
        """Show help dialog for Compress/Decompress tool."""
        help_text = """
        <h2>Compress/Decompress Files - Help</h2>

        <h3>Compression:</h3>
        <ul>
        <li><b>Browse Folder:</b> Select the folder you want to compress</li>
        <li><b>Browse Output:</b> Choose where to save the compressed archive</li>
        <li><b>Format:</b> Select compression format (ZIP, TAR.GZ, TAR.BZ2)</li>
        <li><b>Password:</b> Optional password protection (ZIP only)</li>
        <li><b>Compression Level:</b> Higher levels = smaller files but slower compression</li>
        </ul>

        <h3>Decompression:</h3>
        <ul>
        <li><b>Browse Archive:</b> Select the archive file to decompress</li>
        <li>Files will be extracted to the same directory as the archive</li>
        </ul>

        <h3>Supported Formats:</h3>
        <ul>
        <li>ZIP (.zip) - with password support</li>
        <li>TAR.GZ ({ARCHIVE_EXT_TAR_GZ}) - GNU zip compression</li>
        <li>TAR.BZ2 ({ARCHIVE_EXT_TAR_BZ2}) - Bzip2 compression</li>
        </ul>

        <h3>Keyboard Shortcuts:</h3>
        <ul>
        <li><b>Ctrl+Q:</b> Exit application</li>
        <li><b>F1:</b> Show this help</li>
        <li><b>F5:</b> Clear all fields</li>
        </ul>
        """

        QMessageBox.information(self, "Compress/Decompress Help", help_text)

    def show_preferences(self):
        """Show Compress/Decompress preferences."""
        QMessageBox.information(
            self,
            "Compress/Decompress Preferences",
            "Compress/Decompress preferences:\n\n"
            "• Default compression format\n"
            "• Default compression level\n"
            "• Output directory settings\n"
            "• Archive verification options\n\n"
            "Advanced preferences coming soon!",
        )

    def refresh_view(self):
        """Refresh/clear the current operation."""
        self.clear_fields()

    def init_ui(self):
        """Initialize the user interface."""
        # Use the existing main layout from StandardWindow or create our own
        if hasattr(self, "main_layout"):
            layout = self.main_layout
        else:
            # Create central widget and layout for QMainWindow fallback
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)

        # Create header
        header_label = _ui_widget(QLabel, 'Legacy.s9cb55614120321e9', 'setText')
        header_label.setStyleSheet(
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
        font_tokens.bind(header_label, "font.toolHeader")
        layout.addWidget(header_label)

        # Compression section
        layout.addWidget(_ui_widget(QLabel, 'Legacy.sb67c3682d03a7c51', 'setText'))

        # Folder selection
        folder_layout = QHBoxLayout()
        self.lineEditFolder = TextInput("Folder", "Select folder to compress...")
        _ui_bind(self.lineEditFolder, 'setAccessibleName', 'Legacy.s8594047f827bc6f1')
        folder_layout.addWidget(self.lineEditFolder)
        self.buttonBrowseFolder = _ui_widget(SecondaryButton, 'Legacy.s28bbf5e4e8dc04d6', 'setText')
        _ui_bind(self.buttonBrowseFolder, 'setAccessibleName', 'Legacy.saaafca4775ee5372')
        self.buttonBrowseFolder.clicked.connect(self.browse_folder)
        folder_layout.addWidget(self.buttonBrowseFolder)
        layout.addLayout(folder_layout)

        # Output file selection
        output_layout = QHBoxLayout()
        self.lineEditOutput = TextInput("Output archive", "Select output archive file...")
        _ui_bind(self.lineEditOutput, 'setAccessibleName', 'Legacy.s62f202846411176b')
        output_layout.addWidget(self.lineEditOutput)
        self.buttonBrowseOutput = _ui_widget(SecondaryButton, 'Legacy.s11d127bc1cd471cb', 'setText')
        _ui_bind(self.buttonBrowseOutput, 'setAccessibleName', 'Legacy.se389efd17aba1b1b')
        self.buttonBrowseOutput.clicked.connect(self.browse_output)
        output_layout.addWidget(self.buttonBrowseOutput)
        layout.addLayout(output_layout)

        # Format selection
        format_layout = QHBoxLayout()
        format_layout.addWidget(_ui_widget(QLabel, 'Legacy.s9a5649a42cb2fcef', 'setText'))
        self.comboFormat = QComboBox()
        _ui_bind(self.comboFormat, 'setAccessibleName', 'Legacy.s0efb90fed246e07c')
        self.comboFormat.addItems([FORMAT_ZIP, FORMAT_TAR_GZ, FORMAT_TAR_BZ2])
        self.comboFormat.currentTextChanged.connect(self.update_output_extension)
        format_layout.addWidget(self.comboFormat)
        layout.addLayout(format_layout)

        # Password field
        password_layout = QHBoxLayout()
        password_layout.addWidget(_ui_widget(QLabel, 'Legacy.sa1741e8b125b993c', 'setText'))
        self.lineEditPassword = TextInput("Password", "Optional archive password")
        _ui_bind(self.lineEditPassword, 'setAccessibleName', 'Legacy.s3c652b7e4a5f7621')
        self.lineEditPassword.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(self.lineEditPassword)
        layout.addLayout(password_layout)

        # Compression level
        level_layout = QHBoxLayout()
        level_layout.addWidget(_ui_widget(QLabel, 'Legacy.s56c9a55dce644508', 'setText'))
        self.sliderCompLevel = QSlider(Qt.Orientation.Horizontal)
        _ui_bind(self.sliderCompLevel, 'setAccessibleName', 'Legacy.s9889378e7ac0e5b0')
        self.sliderCompLevel.setMinimumHeight(44)
        self.sliderCompLevel.setRange(1, 9)
        self.sliderCompLevel.setValue(6)
        level_layout.addWidget(self.sliderCompLevel)
        layout.addLayout(level_layout)

        # Compress button
        self.buttonCompress = _ui_widget(PrimaryButton, 'Legacy.s033fc0445b90d3a7', 'setText')
        _ui_bind(self.buttonCompress, 'setAccessibleName', 'Legacy.s972025296c52c195')
        self.buttonCompress.clicked.connect(self.compress_files)
        layout.addWidget(self.buttonCompress)

        # Decompression section
        layout.addWidget(_ui_widget(QLabel, 'Legacy.seef49abec6492b6c', 'setText'))

        # Archive file selection
        decomp_layout = QHBoxLayout()
        self.lineEditDecompress = TextInput("Archive", "Select archive to decompress...")
        _ui_bind(self.lineEditDecompress, 'setAccessibleName', 'Legacy.s2e69eddcb5867c13')
        self.buttonBrowseDecompress = _ui_widget(SecondaryButton, 'Legacy.s70bcd8e3dce2464e', 'setText')
        _ui_bind(self.buttonBrowseDecompress, 'setAccessibleName', 'Legacy.sd14ac859f462708b')
        self.buttonBrowseDecompress.clicked.connect(self.browse_decompress)
        decomp_layout.addWidget(self.lineEditDecompress)
        decomp_layout.addWidget(self.buttonBrowseDecompress)
        layout.addLayout(decomp_layout)

        # Decompress button
        self.buttonDecompress = _ui_widget(PrimaryButton, 'Legacy.sba208c4d49178dcb', 'setText')
        _ui_bind(self.buttonDecompress, 'setAccessibleName', 'Legacy.s9621206a6af2c7d9')
        self.buttonDecompress.clicked.connect(self.decompress_files)
        layout.addWidget(self.buttonDecompress)

        from src.gui.background_task import BackgroundTask
        self.dry_run_checkbox = _ui_widget(QCheckBox, 'Legacy.s27e7300155f3b95e', 'setText')
        self.dry_run_checkbox.setChecked(True)
        _ui_bind(self.dry_run_checkbox, 'setAccessibleName', 'Legacy.s8b592c362e53af20')
        layout.addWidget(self.dry_run_checkbox)
        self.archive_task = BackgroundTask(self, "compress-decompress", layout,
            [self.buttonCompress, self.buttonDecompress, self.dry_run_checkbox,
             self.lineEditFolder, self.lineEditOutput, self.lineEditDecompress,
             self.lineEditPassword, self.comboFormat, self.sliderCompLevel])
        self.undo_supported = False

        # Set up file filters based on format
        self.format_filters: Dict[str, str] = {
            FORMAT_ZIP: "Zip Files (*.zip)",
            FORMAT_TAR_GZ: f"Gzip Tar Files (*{ARCHIVE_EXT_TAR_GZ})",
            FORMAT_TAR_BZ2: f"Bzip2 Tar Files (*{ARCHIVE_EXT_TAR_BZ2})",
        }

        # Note: Drag and drop functionality can be added later if needed
            # Note: Drag and drop functionality can be added later if needed

    def update_output_extension(self):
        """Update the output file extension based on selected format."""
        current_path = self.lineEditOutput.text()
        if current_path:
            base_path = os.path.splitext(current_path)[0]
            if self.comboFormat.currentText() == FORMAT_ZIP:
                self.lineEditOutput.setText(base_path + ARCHIVE_EXT_ZIP)
            elif self.comboFormat.currentText() == FORMAT_TAR_GZ:
                self.lineEditOutput.setText(base_path + ARCHIVE_EXT_TAR_GZ)
            elif self.comboFormat.currentText() == FORMAT_TAR_BZ2:
                self.lineEditOutput.setText(base_path + ARCHIVE_EXT_TAR_BZ2)

    def browse_folder(self):
        """Browse for a folder to compress."""
        folder = get_existing_directory(self, "Select Folder")
        if folder:
            self.lineEditFolder.setText(folder)

    def browse_output(self):
        """Browse for output archive file location."""
        format_filter = self.format_filters[self.comboFormat.currentText()]
        output_file = get_save_file_name(
            caption="Select Output File",
            parent=self,
            file_filter=format_filter,
        )
        if output_file:
            self.lineEditOutput.setText(output_file)

    def compress_files(self):
        from src.core.archive_operations import plan_compression
        source, target = self.lineEditFolder.text().strip(), self.lineEditOutput.text().strip()
        password = self.lineEditPassword.text()
        if password:
            show_error_dialog("Unsupported password", "Password-protected archive creation is not supported. No archive was written.", self)
            return
        if not source or not target:
            return
        format, level = self.comboFormat.currentText(), self.sliderCompLevel.value()
        self.archive_task.start("preview-compression", lambda: plan_compression(
            source, target, format, level, cancel=self.archive_task.cancel), self._archive_planned)

    def _archive_planned(self, plan):
        from src.core.archive_operations import execute_compression, execute_extraction
        from src.gui.components.modal import ConfirmationModal
        from PyQt5.QtWidgets import QDialog
        summary = f"{len(plan.members)} entries\nOutput: {plan.destination}\n" + "\n".join(item[0] for item in plan.members[:30])
        if self.dry_run_checkbox.isChecked():
            show_info_dialog("Archive preview — no files changed", summary, self)
            return
        if ConfirmationModal("Apply archive operation", summary + "\nExisting archive output may be replaced. Export has no undo.", parent=self).exec_() != QDialog.Accepted:
            return
        password = self.lineEditPassword.text()
        work = (lambda: execute_compression(plan, self.archive_task.cancel)) if plan.mode == "compress" else (
            lambda: execute_extraction(plan, password, self.archive_task.cancel))
        self.archive_task.start("apply-archive", work,
            lambda _: self.statusBar().showMessage("Archive operation complete. Source files preserved.", 8000))

    def _compress_7z(self, folder_path, output_path, password="", compression_level=6):
        """Compress files into a 7Z archive."""
        try:
            import py7zr
        except ImportError as exc:  # pragma: no cover - dependency guard
            raise ImportError("py7zr is required for 7Z compression support") from exc

        with py7zr.SevenZipFile(output_path, 'w', password=password) as z:
            z.writeall(folder_path, arcname='')

    def _decompress_7z(self, archive_path, output_dir, password=""):
        """Decompress a 7Z archive."""
        try:
            import py7zr
        except ImportError as exc:  # pragma: no cover - dependency guard
            raise ImportError("py7zr is required for 7Z decompression support") from exc

        with py7zr.SevenZipFile(archive_path, 'r', password=password) as z:
            z.extractall(path=output_dir)

    def _compress_zip(self, folder_path, output_path, password, compression_level):
        """Compress files into a ZIP archive."""
        if password:
            raise ValueError("Password-protected ZIP creation is unsupported")
        compression = zipfile.ZIP_DEFLATED
        with zipfile.ZipFile(
            output_path,
            "w",
            compression=compression,
            compresslevel=compression_level,
        ) as zipf:
            if password:
                zipf.setpassword(password.encode())
            for root, _, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, folder_path)
                    zipf.write(file_path, arcname)

    def _compress_targz(self, folder_path, output_path, compression_level):
        """Compress files into a tar.gz archive."""
        with tarfile.open(output_path, "w:gz", compresslevel=compression_level) as tar:
            tar.add(folder_path, arcname=".")

    def _compress_tarbz2(self, folder_path, output_path, compression_level):
        """Compress files into a tar.bz2 archive."""
        with tarfile.open(output_path, "w:bz2", compresslevel=compression_level) as tar:
            tar.add(folder_path, arcname=".")

    def browse_decompress(self):
        """Browse for archive file to decompress."""
        formats = ";;".join(self.format_filters.values())
        archive_file = get_open_file_name(
            caption="Select Archive File", parent=self, file_filter=formats
        )
        if archive_file:
            self.lineEditDecompress.setText(archive_file)

    def decompress_files(self):
        from pathlib import Path
        from src.core.archive_operations import plan_extraction
        source = self.lineEditDecompress.text().strip()
        parent = get_existing_directory(self, "Select parent for a new extracted folder")
        if not source or not parent:
            return
        destination = Path(parent) / (Path(source).name + "_extracted")
        self.archive_task.start("preview-extraction", lambda: plan_extraction(
            source, destination, self.archive_task.cancel), self._archive_planned)

    def _decompress_zip(self, archive_path, output_folder, password):
        from src.core.archive_operations import plan_extraction, execute_extraction
        execute_extraction(plan_extraction(archive_path, output_folder), password)

    def _decompress_targz(self, archive_path, output_folder):
        self._decompress_zip(archive_path, output_folder, "")

    def _decompress_tarbz2(self, archive_path, output_folder):
        self._decompress_zip(archive_path, output_folder, "")

    # Drag and drop functionality removed for simplicity
    # Can be added back later if needed


def main():
    """Main function to run the application."""
    import sys

    app = QApplication(sys.argv)
    window = CompressDecompressApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
