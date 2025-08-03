from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QDragEnterEvent, QDropEvent
from PyQt5 import uic
from gui.common.base_window import BaseWindow
from gui.common.dialogs import (
    show_error_dialog, show_info_dialog, get_existing_directory,
    get_open_file_name, get_save_file_name
)
import zipfile
import os
import py7zr
import tarfile
from typing import Dict
from pathlib import Path


# Archive format constants
FORMAT_ZIP = "ZIP"
FORMAT_7Z = "7Z"
FORMAT_TAR_GZ = "TAR.GZ"
FORMAT_TAR_BZ2 = "TAR.BZ2"


class CompressDecompressWindow(BaseWindow):
    """Handles compression and decompression with various archive formats."""
    def __init__(self) -> None:
        """Initialize the compression/decompression window."""
        super().__init__()
        
        # Load UI file with proper path resolution
        ui_file = Path(__file__).parent / "compress_decompress.ui"
        uic.loadUi(str(ui_file), self)
        
        # Setup icons
        self._setup_icons()

        # Enable drag and drop
        self.setAcceptDrops(True)
        self.lineEditFolder.setAcceptDrops(True)
        self.lineEditOutput.setAcceptDrops(True)
        self.lineEditDecompress.setAcceptDrops(True)

        # Connect buttons to their respective methods
        self.buttonBrowseFolder.clicked.connect(self.browse_folder)
        self.buttonBrowseOutput.clicked.connect(self.browse_output)
        self.buttonCompress.clicked.connect(self.compress_files)
        self.buttonBrowseDecompress.clicked.connect(self.browse_decompress)
        self.buttonDecompress.clicked.connect(self.decompress_files)
        self.actionExit.triggered.connect(self.close)

        # Set up file filters based on format
        self.format_filters: Dict[str, str] = {
            FORMAT_ZIP: "Zip Files (*.zip)",
            FORMAT_7Z: "7-Zip Files (*.7z)",
            FORMAT_TAR_GZ: "Gzip Tar Files (*.tar.gz)",
            FORMAT_TAR_BZ2: "Bzip2 Tar Files (*.tar.bz2)"
        }

        # Connect format combo box to update file extension
        self.comboFormat.currentTextChanged.connect(
            self.update_output_extension
        )

    def _setup_icons(self) -> None:
        """Setup icons for the compress/decompress window."""
        # Note: Icons can be added here when available
        # Example: self.setWindowIcon(QIcon(str(
        #     Path(__file__).parent / "icons" / "compress.png")))
        pass

    def update_output_extension(self) -> None:
        """Update the output file extension based on selected format."""
        current_path: str = self.lineEditOutput.text()
        if current_path:
            base_path: str = os.path.splitext(current_path)[0]
            if self.comboFormat.currentText() == FORMAT_ZIP:
                self.lineEditOutput.setText(base_path + ".zip")
            elif self.comboFormat.currentText() == FORMAT_7Z:
                self.lineEditOutput.setText(base_path + ".7z")
            elif self.comboFormat.currentText() == FORMAT_TAR_GZ:
                self.lineEditOutput.setText(base_path + ".tar.gz")
            elif self.comboFormat.currentText() == FORMAT_TAR_BZ2:
                self.lineEditOutput.setText(base_path + ".tar.bz2")

    def browse_folder(self) -> None:
        """Browse for a folder to compress."""
        folder: str = str(get_existing_directory(self, "Select Folder") or "")
        if folder:
            self.lineEditFolder.setText(folder)

    def browse_output(self) -> None:
        """Browse for output archive file location."""
        format_filter: str = self.format_filters[
            self.comboFormat.currentText()
        ]
        output_file: str = str(
            get_save_file_name(
                caption="Select Output File",
                parent=self,
                file_filter=format_filter
            ) or ""
        )
        if output_file:
            self.lineEditOutput.setText(output_file)

    def compress_files(self) -> None:
        """Compress files using the selected format and settings."""
        folder_path: str = self.lineEditFolder.text().strip()
        output_path: str = self.lineEditOutput.text().strip()
        password: str = self.lineEditPassword.text()
        compression_level: int = self.sliderCompLevel.value()
        format_type: str = self.comboFormat.currentText()

        if not folder_path or not output_path:
            show_error_dialog(
                title="Error",
                message="Please specify both folder and output file.",
                parent=self
            )
            return

        try:
            if format_type == "ZIP":
                self._compress_zip(
                    folder_path, output_path, password, compression_level
                )
            elif format_type == "7Z":
                self._compress_7z(
                    folder_path, output_path, password, compression_level
                )
            elif format_type == "TAR.GZ":
                self._compress_targz(
                    folder_path, output_path, compression_level
                )
            elif format_type == "TAR.BZ2":
                self._compress_tarbz2(
                    folder_path, output_path, compression_level
                )

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

    def _compress_zip(
        self,
        folder_path: str,
        output_path: str,
        password: str,
        compression_level: int
    ) -> None:
        """Compress files into a ZIP archive.

        Args:
            folder_path: Path to the folder to compress
            output_path: Path where the ZIP file will be saved
            password: Optional password for encryption
            compression_level: Level of compression to use
        """
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

    def _compress_7z(
        self,
        folder_path: str,
        output_path: str,
        password: str,
        compression_level: int
    ) -> None:
        """Compress files into a 7z archive.

        Args:
            folder_path: Path to the folder to compress
            output_path: Path where the 7z file will be saved
            password: Optional password for encryption
            compression_level: Level of compression to use
        """
        filters = [{"id": py7zr.FILTER_LZMA2, "preset": compression_level}]
        with py7zr.SevenZipFile(
            output_path, 'w',
            password=password, filters=filters
        ) as archive:
            archive.writeall(folder_path, ".")

    def _compress_targz(
        self,
        folder_path: str,
        output_path: str,
        compression_level: int
    ) -> None:
        """Compress files into a tar.gz archive.

        Args:
            folder_path: Path to the folder to compress
            output_path: Path where the tar.gz file will be saved
            compression_level: Level of compression to use
        """
        with tarfile.open(
            output_path, "w:gz",
            compresslevel=compression_level
        ) as tar:
            tar.add(folder_path, arcname=".")

    def _compress_tarbz2(
        self,
        folder_path: str,
        output_path: str,
        compression_level: int
    ) -> None:
        """Compress files into a tar.bz2 archive.

        Args:
            folder_path: Path to the folder to compress
            output_path: Path where the tar.bz2 file will be saved
            compression_level: Level of compression to use
        """
        with tarfile.open(
            output_path, "w:bz2",
            compresslevel=compression_level
        ) as tar:
            tar.add(folder_path, arcname=".")

    def browse_decompress(self) -> None:
        """Browse for archive file to decompress."""
        formats: str = ";;".join(self.format_filters.values())
        zip_file: str = str(
            get_open_file_name(
                caption="Select Archive File",
                parent=self,
                file_filter=formats
            ) or ""
        )
        if zip_file:
            self.lineEditDecompress.setText(zip_file)

    def decompress_files(self) -> None:
        """Decompress files from the selected archive."""
        archive_path: str = self.lineEditDecompress.text().strip()
        output_folder: str = str(
            get_existing_directory(self, "Select Output Folder") or ""
        )
        password: str = self.lineEditPassword.text()

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
            elif archive_path.endswith('.7z'):
                self._decompress_7z(archive_path, output_folder, password)
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

    def _decompress_zip(
        self,
        archive_path: str,
        output_folder: str,
        password: str
    ) -> None:
        """Decompress files from a ZIP archive.

        Args:
            archive_path: Path to the ZIP archive to decompress
            output_folder: Path to extract the files to
            password: Optional password for encrypted archives
        """
        with zipfile.ZipFile(archive_path, 'r') as zipf:
            if password:
                zipf.setpassword(password.encode())
            zipf.extractall(output_folder)

    def _decompress_7z(
        self,
        archive_path: str,
        output_folder: str,
        password: str
    ) -> None:
        """Decompress files from a 7z archive.

        Args:
            archive_path: Path to the 7z archive to decompress
            output_folder: Path to extract the files to
            password: Optional password for encrypted archives
        """
        with py7zr.SevenZipFile(
            archive_path, mode='r',
            password=password
        ) as archive:
            archive.extractall(output_folder)

    def _decompress_targz(
        self,
        archive_path: str,
        output_folder: str
    ) -> None:
        """Decompress files from a tar.gz archive.

        Args:
            archive_path: Path to the tar.gz archive to decompress
            output_folder: Path to extract the files to
        """
        with tarfile.open(archive_path, "r:gz") as tar:
            tar.extractall(output_folder)

    def _decompress_tarbz2(
        self,
        archive_path: str,
        output_folder: str
    ) -> None:
        """Decompress files from a tar.bz2 archive.

        Args:
            archive_path: Path to the tar.bz2 archive to decompress
            output_folder: Path to extract the files to
        """
        with tarfile.open(archive_path, "r:bz2") as tar:
            tar.extractall(output_folder)

    def dragEnterEvent(self, a0: QDragEnterEvent) -> None:
        """Handle drag enter event for drag and drop operation.

        Args:
            a0: The drag enter event object
        """
        if a0.mimeData().hasUrls():
            a0.acceptProposedAction()

    def dropEvent(self, a0: QDropEvent) -> None:
        """Handle drop event for drag and drop operation.

        Args:
            a0: The drop event object
        """
        urls = a0.mimeData().urls()
        if not urls:
            return
            
        path: str = urls[0].toLocalFile()
        focused_widget = QApplication.focusWidget()
        
        if focused_widget == self.lineEditFolder:
            if os.path.isdir(path):
                self.lineEditFolder.setText(path)
            else:
                show_error_dialog(
                    title="Error",
                    message="Please drop a folder to compress",
                    parent=self)
                
        elif focused_widget == self.lineEditOutput:
            if os.path.isdir(os.path.dirname(path)):
                self.lineEditOutput.setText(path)
        elif focused_widget == self.lineEditDecompress:
            is_archive: bool = any(
                path.lower().endswith(ext)
                for ext in ['.zip', '.7z', '.tar.gz', '.tar.bz2']
            )
            if os.path.isfile(path) and is_archive:
                self.lineEditDecompress.setText(path)
            else:
                show_error_dialog(
                    title="Error",
                    message="Please drop a supported archive file",
                    parent=self)
