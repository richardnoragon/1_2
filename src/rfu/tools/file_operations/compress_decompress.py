"""
Compress/Decompress Tool for Richard's File Utilities
Handles compression and decompression with various archive formats.
"""

from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
                             QPushButton, QLineEdit, QLabel, QComboBox,
                             QSlider, QFileDialog, QMessageBox, QApplication)
from PyQt5.QtCore import Qt
import zipfile
import os
import tarfile
import sys
from typing import Dict

# Import StandardWindow for menu integration
try:
    from src.rfu.gui.standard_window import StandardWindow
except ImportError:
    # Fallback for standalone execution
    from PyQt5.QtWidgets import QMainWindow
    StandardWindow = QMainWindow


# Archive format constants
FORMAT_ZIP = "ZIP"
FORMAT_TAR_GZ = "TAR.GZ"
FORMAT_TAR_BZ2 = "TAR.BZ2"


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
        super().__init__(
            title="Compress/Decompress Files - Richard's File Utilities",
            window_type="utility"
        )
        self.init_ui()
        self._setup_menu_callbacks()
    
    def _setup_menu_callbacks(self):
        """Setup tool-specific menu callbacks."""
        if hasattr(self, 'menu_manager'):
            # Register tool-specific callbacks
            self.menu_manager.register_callback('new_compression', self.clear_fields)
            self.menu_manager.register_callback('help_compression', self.show_help)
            
    def clear_fields(self):
        """Clear all input fields for a new compression task."""
        self.lineEditFolder.clear()
        self.lineEditOutput.clear()
        self.lineEditDecompress.clear()
        self.lineEditPassword.clear()
        self.comboFormat.setCurrentIndex(0)
        self.sliderCompLevel.setValue(6)
        
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
        <li>TAR.GZ (.tar.gz) - GNU zip compression</li>
        <li>TAR.BZ2 (.tar.bz2) - Bzip2 compression</li>
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
        QMessageBox.information(self, "Compress/Decompress Preferences", 
                               "Compress/Decompress preferences:\n\n"
                               "• Default compression format\n"
                               "• Default compression level\n"
                               "• Output directory settings\n"
                               "• Archive verification options\n\n"
                               "Advanced preferences coming soon!")
                               
    def refresh_view(self):
        """Refresh/clear the current operation."""
        self.clear_fields()
        
    def init_ui(self):
        """Initialize the user interface."""
        # Use the existing main layout from StandardWindow
        layout = self.main_layout
        
        # Create header
        header_label = QLabel("Compress/Decompress Files")
        header_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
                background-color: #ecf0f1;
                border-radius: 5px;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(header_label)
        
        # Compression section
        layout.addWidget(QLabel("Compression:"))
        
        # Folder selection
        folder_layout = QHBoxLayout()
        self.lineEditFolder = QLineEdit()
        self.lineEditFolder.setPlaceholderText("Select folder to compress...")
        self.buttonBrowseFolder = QPushButton("Browse Folder")
        self.buttonBrowseFolder.clicked.connect(self.browse_folder)
        folder_layout.addWidget(self.lineEditFolder)
        folder_layout.addWidget(self.buttonBrowseFolder)
        layout.addLayout(folder_layout)
        
        # Output file selection
        output_layout = QHBoxLayout()
        self.lineEditOutput = QLineEdit()
        self.lineEditOutput.setPlaceholderText("Select output archive file...")
        self.buttonBrowseOutput = QPushButton("Browse Output")
        self.buttonBrowseOutput.clicked.connect(self.browse_output)
        output_layout.addWidget(self.lineEditOutput)
        output_layout.addWidget(self.buttonBrowseOutput)
        layout.addLayout(output_layout)
        
        # Format selection
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Format:"))
        self.comboFormat = QComboBox()
        self.comboFormat.addItems([FORMAT_ZIP, FORMAT_TAR_GZ, FORMAT_TAR_BZ2])
        self.comboFormat.currentTextChanged.connect(
            self.update_output_extension)
        format_layout.addWidget(self.comboFormat)
        layout.addLayout(format_layout)
        
        # Password field
        password_layout = QHBoxLayout()
        password_layout.addWidget(QLabel("Password (optional):"))
        self.lineEditPassword = QLineEdit()
        self.lineEditPassword.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(self.lineEditPassword)
        layout.addLayout(password_layout)
        
        # Compression level
        level_layout = QHBoxLayout()
        level_layout.addWidget(QLabel("Compression Level:"))
        self.sliderCompLevel = QSlider(Qt.Orientation.Horizontal)
        self.sliderCompLevel.setRange(1, 9)
        self.sliderCompLevel.setValue(6)
        level_layout.addWidget(self.sliderCompLevel)
        layout.addLayout(level_layout)
        
        # Compress button
        self.buttonCompress = QPushButton("Compress")
        self.buttonCompress.clicked.connect(self.compress_files)
        layout.addWidget(self.buttonCompress)
        
        # Decompression section
        layout.addWidget(QLabel("\nDecompression:"))
        
        # Archive file selection
        decomp_layout = QHBoxLayout()
        self.lineEditDecompress = QLineEdit()
        self.lineEditDecompress.setPlaceholderText(
            "Select archive to decompress...")
        self.buttonBrowseDecompress = QPushButton("Browse Archive")
        self.buttonBrowseDecompress.clicked.connect(self.browse_decompress)
        decomp_layout.addWidget(self.lineEditDecompress)
        decomp_layout.addWidget(self.buttonBrowseDecompress)
        layout.addLayout(decomp_layout)
        
        # Decompress button
        self.buttonDecompress = QPushButton("Decompress")
        self.buttonDecompress.clicked.connect(self.decompress_files)
        layout.addWidget(self.buttonDecompress)
        
        # Set up file filters based on format
        self.format_filters: Dict[str, str] = {
            FORMAT_ZIP: "Zip Files (*.zip)",
            FORMAT_TAR_GZ: "Gzip Tar Files (*.tar.gz)",
            FORMAT_TAR_BZ2: "Bzip2 Tar Files (*.tar.bz2)"
        }
        
        # Note: Drag and drop functionality can be added later if needed
        pass

    def update_output_extension(self):
        """Update the output file extension based on selected format."""
        current_path = self.lineEditOutput.text()
        if current_path:
            base_path = os.path.splitext(current_path)[0]
            if self.comboFormat.currentText() == FORMAT_ZIP:
                self.lineEditOutput.setText(base_path + ".zip")
            elif self.comboFormat.currentText() == FORMAT_TAR_GZ:
                self.lineEditOutput.setText(base_path + ".tar.gz")
            elif self.comboFormat.currentText() == FORMAT_TAR_BZ2:
                self.lineEditOutput.setText(base_path + ".tar.bz2")

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
            file_filter=format_filter
        )
        if output_file:
            self.lineEditOutput.setText(output_file)

    def compress_files(self):
        """Compress files using the selected format and settings."""
        folder_path = self.lineEditFolder.text().strip()
        output_path = self.lineEditOutput.text().strip()
        password = self.lineEditPassword.text()
        compression_level = self.sliderCompLevel.value()
        format_type = self.comboFormat.currentText()

        if not folder_path or not output_path:
            show_error_dialog(
                title="Error",
                message="Please specify both folder and output file.",
                parent=self
            )
            return

        try:
            if format_type == FORMAT_ZIP:
                self._compress_zip(folder_path, output_path, password,
                                   compression_level)
            elif format_type == FORMAT_TAR_GZ:
                self._compress_targz(folder_path, output_path,
                                     compression_level)
            elif format_type == FORMAT_TAR_BZ2:
                self._compress_tarbz2(folder_path, output_path,
                                      compression_level)

            show_info_dialog(
                title="Success",
                message=f"Files compressed successfully to {output_path}",
                parent=self
            )
            
        except Exception as e:
            show_error_dialog(
                title="Error",
                message=f"An error occurred: {str(e)}",
                parent=self
            )

    def _compress_zip(self, folder_path, output_path, password,
                      compression_level):
        """Compress files into a ZIP archive."""
        compression = zipfile.ZIP_DEFLATED
        with zipfile.ZipFile(
            output_path, 'w',
            compression=compression,
            compresslevel=compression_level
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
        with tarfile.open(
            output_path, "w:gz",
            compresslevel=compression_level
        ) as tar:
            tar.add(folder_path, arcname=".")

    def _compress_tarbz2(self, folder_path, output_path, compression_level):
        """Compress files into a tar.bz2 archive."""
        with tarfile.open(
            output_path, "w:bz2",
            compresslevel=compression_level
        ) as tar:
            tar.add(folder_path, arcname=".")

    def browse_decompress(self):
        """Browse for archive file to decompress."""
        formats = ";;".join(self.format_filters.values())
        archive_file = get_open_file_name(
            caption="Select Archive File",
            parent=self,
            file_filter=formats
        )
        if archive_file:
            self.lineEditDecompress.setText(archive_file)

    def decompress_files(self):
        """Decompress files from the selected archive."""
        archive_path = self.lineEditDecompress.text().strip()
        output_folder = get_existing_directory(self, "Select Output Folder")
        password = self.lineEditPassword.text()

        if not archive_path or not output_folder:
            show_error_dialog(
                title="Error",
                message="Please specify both archive file and output folder.",
                parent=self
            )
            return

        try:
            if archive_path.endswith('.zip'):
                self._decompress_zip(archive_path, output_folder, password)
            elif archive_path.endswith('.tar.gz'):
                self._decompress_targz(archive_path, output_folder)
            elif archive_path.endswith('.tar.bz2'):
                self._decompress_tarbz2(archive_path, output_folder)
            else:
                raise ValueError("Unsupported archive format")

            show_info_dialog(
                title="Success",
                message=f"Files decompressed successfully to {output_folder}",
                parent=self
            )
            
        except Exception as e:
            show_error_dialog(
                title="Error",
                message=f"An error occurred: {str(e)}",
                parent=self
            )

    def _decompress_zip(self, archive_path, output_folder, password):
        """Decompress files from a ZIP archive."""
        with zipfile.ZipFile(archive_path, 'r') as zipf:
            if password:
                zipf.setpassword(password.encode())
            zipf.extractall(output_folder)

    def _decompress_targz(self, archive_path, output_folder):
        """Decompress files from a tar.gz archive."""
        with tarfile.open(archive_path, "r:gz") as tar:
            tar.extractall(output_folder)

    def _decompress_tarbz2(self, archive_path, output_folder):
        """Decompress files from a tar.bz2 archive."""
        with tarfile.open(archive_path, "r:bz2") as tar:
            tar.extractall(output_folder)

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
