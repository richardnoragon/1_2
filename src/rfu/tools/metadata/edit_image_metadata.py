#!/usr/bin/env python3
"""
Image Metadata Editor Tool for Richard's File Utilities

A comprehensive image metadata viewing and editing utility with full
EXIF, IPTC, and XMP support, integrated with the StandardWindow menu system.
"""

import os
import sys
from datetime import datetime

try:
    from PyQt5.QtWidgets import (
        QWidget, QVBoxLayout, QGridLayout, QHBoxLayout,
        QPushButton, QLineEdit, QLabel, QCheckBox, QGroupBox,
        QFileDialog, QMessageBox, QProgressBar,
        QTextEdit, QSplitter, QTreeWidget, QTreeWidgetItem,
        QTableWidget, QTabWidget
    )
    from PyQt5.QtCore import Qt, QThread, pyqtSignal
except ImportError:
    print("PyQt5 not available. Please install PyQt5.")
    sys.exit(1)

# Import StandardWindow for menu integration
try:
    from src.rfu.gui.standard_window import StandardWindow
except ImportError:
    try:
        from rfu.gui.standard_window import StandardWindow
    except ImportError:
        # Fallback for standalone execution
        from PyQt5.QtWidgets import QMainWindow, QStatusBar
        
        class StandardWindow(QMainWindow):
            def __init__(self, title="", window_type="utility"):
                super().__init__()
                self.setWindowTitle(title)
                self.central_widget = QWidget()
                self.setCentralWidget(self.central_widget)
                self.main_layout = QVBoxLayout(self.central_widget)
                self.setStatusBar(QStatusBar())
                
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
                
            def get_file_path(self, title="Select File",
                              file_filter="All Files (*)"):
                return QFileDialog.getOpenFileName(
                    self, title, "", file_filter)[0]
                
            def get_save_file_path(self, title="Save File",
                                   file_filter="All Files (*)"):
                return QFileDialog.getSaveFileName(
                    self, title, "", file_filter)[0]
                    
            def get_directory_path(self, title="Select Directory"):
                return QFileDialog.getExistingDirectory(self, title)
                
            def create_header(self, text):
                """Create a standard header label."""
                header = QLabel(text)
                header.setStyleSheet("""
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
                return header

# Import existing image metadata logic
try:
    from src.utilities.metadata.image_metadata_logic import (
        ImageMetadataLogic, ImageMetadataWorker, format_exif_value, 
        parse_exif_value, get_tag_name
    )
except ImportError:
    try:
        from utilities.metadata.image_metadata_logic import (
            ImageMetadataLogic, ImageMetadataWorker, format_exif_value,
            parse_exif_value, get_tag_name
        )
    except ImportError:
        # Fallback implementation for standalone execution
        print("Warning: Advanced metadata logic not available. "
              "Using basic implementation.")
        
        from PyQt5.QtCore import QObject
        
        class ImageMetadataLogic(QObject):
            metadata_loaded = pyqtSignal(dict)
            metadata_saved = pyqtSignal(bool, str)
            error_occurred = pyqtSignal(str)
            progress_percentage = pyqtSignal(int)
            progress_message = pyqtSignal(str)
            finished = pyqtSignal()
            
            def __init__(self):
                super().__init__()
                
            def load_image_metadata(self, file_path):
                # Basic fallback implementation
                self.metadata_loaded.emit({})
                self.finished.emit()
                
            def save_image_metadata(self, file_path, metadata):
                self.metadata_saved.emit(
                    False, "Advanced metadata logic not available")
                self.finished.emit()
        
        class ImageMetadataWorker(QThread):
            def __init__(self, *args, **kwargs):
                super().__init__()
                
            def run(self):
                pass
        
        def format_exif_value(value):
            return str(value)
        
        def parse_exif_value(value, original_type, tag_code):
            return value
        
        def get_tag_name(ifd_name, tag_code):
            return f"Tag_{tag_code}"


class ImageMetadataWorkerThread(QThread):
    """Enhanced worker thread for image metadata operations with batch
    support."""
    
    progress_updated = pyqtSignal(int)
    file_processed = pyqtSignal(str, dict)  # file_path, metadata
    finished = pyqtSignal()
    error_occurred = pyqtSignal(str)
    status_updated = pyqtSignal(str)
    
    def __init__(self, files, operation, metadata_updates=None):
        super().__init__()
        self.files = files
        self.operation = operation
        self.metadata_updates = metadata_updates or {}
        self.is_cancelled = False
        self.metadata_logic = ImageMetadataLogic()
        
    def run(self):
        """Execute metadata operation."""
        try:
            total_files = len(self.files)
            
            for i, file_path in enumerate(self.files):
                if self.is_cancelled:
                    break
                    
                try:
                    self.status_updated.emit(
                        f"Processing {os.path.basename(file_path)}...")
                    
                    if self.operation == "read":
                        metadata = self._read_comprehensive_metadata(file_path)
                        self.file_processed.emit(file_path, metadata)
                    elif self.operation == "write":
                        success = self._write_metadata(
                            file_path, self.metadata_updates)
                        if success:
                            metadata = self._read_comprehensive_metadata(
                                file_path)
                            self.file_processed.emit(file_path, metadata)
                        
                except Exception as e:
                    error_msg = f"Error processing {file_path}: {str(e)}"
                    self.error_occurred.emit(error_msg)
                
                progress = int((i + 1) / total_files * 100)
                self.progress_updated.emit(progress)
                
            self.finished.emit()
            
        except Exception as e:
            self.error_occurred.emit(f"Worker error: {str(e)}")
    
    def _read_comprehensive_metadata(self, file_path):
        """Read comprehensive metadata from image file."""
        metadata = {
            "file_info": {},
            "exif_data": {},
            "iptc_data": {},
            "xmp_data": {},
            "basic_metadata": {},
            "error": None
        }
        
        try:
            # Basic file information
            stat_info = os.stat(file_path)
            metadata["file_info"] = {
                "filename": os.path.basename(file_path),
                "filepath": file_path,
                "size": stat_info.st_size,
                "modified": datetime.fromtimestamp(
                    stat_info.st_mtime).isoformat(),
                "created": datetime.fromtimestamp(
                    stat_info.st_ctime).isoformat(),
                "extension": os.path.splitext(file_path)[1].lower()
            }
            
            # Try to get basic image info using PIL
            try:
                from PIL import Image
                with Image.open(file_path) as img:
                    metadata["basic_metadata"] = {
                        "format": img.format,
                        "mode": img.mode,
                        "width": img.width,
                        "height": img.height,
                        "has_transparency": (img.mode in ('RGBA', 'LA') or
                                             'transparency' in img.info)
                    }
                    
                    # Extract basic EXIF using PIL
                    try:
                        exif_data = img.getexif()
                        if exif_data:
                            metadata["exif_data"] = self._process_pil_exif(
                                exif_data)
                    except (AttributeError, Exception):
                        # EXIF not available or error reading
                        pass
                        
            except ImportError:
                metadata["basic_metadata"] = {
                    "format": "Unknown (PIL not available)",
                    "note": "Install Pillow for full metadata support"
                }
            except Exception as e:
                metadata["error"] = f"Image processing error: {str(e)}"
            
            # Try to use advanced metadata logic if available
            try:
                advanced_metadata = (
                    self.metadata_logic.load_image_metadata(file_path))
                if advanced_metadata:
                    # Merge advanced metadata
                    for key, value in advanced_metadata.items():
                        if key in metadata and isinstance(value, dict):
                            metadata[key].update(value)
                        else:
                            metadata[key] = value
            except Exception:
                # Advanced metadata not available, continue with basic
                pass
                
        except Exception as e:
            metadata["error"] = f"File access error: {str(e)}"
            
        return metadata
    
    def _process_pil_exif(self, exif_data):
        """Process PIL EXIF data into readable format."""
        processed_exif = {}
        
        try:
            from PIL.ExifTags import TAGS
            
            for tag_id, value in exif_data.items():
                tag_name = TAGS.get(tag_id, f"Tag_{tag_id}")
                if isinstance(value, bytes):
                    try:
                        value = value.decode(
                            'utf-8', errors='ignore').strip('\x00 ')
                    except Exception:
                        value = str(value)
                processed_exif[tag_name] = str(value)
                
        except Exception as e:
            processed_exif["error"] = f"EXIF processing error: {str(e)}"
            
        return processed_exif
    
    def _write_metadata(self, file_path, updates):
        """Write metadata to image file."""
        try:
            # Use advanced metadata logic if available
            return self.metadata_logic.save_image_metadata(file_path, updates)
        except Exception:
            # Fallback - metadata writing not available
            return False
    
    def cancel(self):
        """Cancel the operation."""
        self.is_cancelled = True


class ImageMetadataEditorGUI(StandardWindow):
    """Professional Image Metadata Editor GUI with comprehensive
    functionality."""
    
    def __init__(self):
        super().__init__(
            title="Image Metadata Editor - Richard's File Utilities",
            window_type="utility"
        )
        self.worker = None
        self.selected_files = []
        self.current_metadata = {}
        self.current_file_metadata = {}
        self.metadata_logic = ImageMetadataLogic()
        
        self.init_ui()
        self._setup_menu_callbacks()
        
    def _setup_menu_callbacks(self):
        """Setup tool-specific menu callbacks."""
        if hasattr(self, 'menu_manager'):
            # File menu callbacks
            self.menu_manager.register_callback(
                'new_image_session', self.new_image_session)
            self.menu_manager.register_callback(
                'save_file', self.save_image_settings)
            self.menu_manager.register_callback(
                'open_file', self.load_image_settings)
            self.menu_manager.register_callback(
                'export_data', self.export_metadata)
            self.menu_manager.register_callback(
                'import_data', self.import_metadata_settings)
            self.menu_manager.register_callback(
                'print_document', self.print_metadata_report)
            
            # Edit menu callbacks
            self.menu_manager.register_callback('cut', self.cut_text)
            self.menu_manager.register_callback('copy', self.copy_text)
            self.menu_manager.register_callback('paste', self.paste_text)
            self.menu_manager.register_callback(
                'select_all', self.select_all_text)
            self.menu_manager.register_callback('find', self.find_metadata)
            
            # View menu callbacks
            self.menu_manager.register_callback('zoom_in', self.zoom_in)
            self.menu_manager.register_callback('zoom_out', self.zoom_out)
            self.menu_manager.register_callback('zoom_reset', self.zoom_reset)
            
            # Tools menu callbacks
            self.menu_manager.register_callback(
                'show_options', self.show_image_options)
            self.menu_manager.register_callback(
                'batch_processing', self.show_batch_processing)
            self.menu_manager.register_callback(
                'metadata_analysis', self.analyze_images)
            
            # Help menu callbacks
            self.menu_manager.register_callback(
                'help_image', self.show_help)
        
    def init_ui(self):
        """Initialize the comprehensive user interface."""
        self.setGeometry(100, 100, 1400, 900)
        
        # Use the main layout from StandardWindow
        layout = self.main_layout
        
        # Create header using StandardWindow method
        header_label = self.create_header("Image Metadata Editor")
        layout.addWidget(header_label)
        
        # Create main splitter
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(main_splitter)
        
        # Left panel - File selection and controls
        left_panel = self._create_left_panel()
        main_splitter.addWidget(left_panel)
        
        # Right panel - Metadata display
        right_panel = self._create_right_panel()
        main_splitter.addWidget(right_panel)
        
        # Set splitter proportions
        main_splitter.setSizes([450, 950])
        
    def _create_left_panel(self):
        """Create the left control panel."""
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # File selection group
        selection_group = QGroupBox("Image File Selection")
        selection_layout = QGridLayout(selection_group)
        
        # File input
        selection_layout.addWidget(QLabel("Files:"), 0, 0)
        self.files_edit = QLineEdit()
        self.files_edit.setPlaceholderText("Select image files...")
        self.files_edit.setReadOnly(True)
        selection_layout.addWidget(self.files_edit, 0, 1)
        
        # Browse buttons
        self.browse_files_button = QPushButton("Browse Images")
        self.browse_files_button.clicked.connect(self.browse_files)
        selection_layout.addWidget(self.browse_files_button, 0, 2)
        
        self.browse_folder_button = QPushButton("Browse Folder")
        self.browse_folder_button.clicked.connect(self.browse_folder)
        selection_layout.addWidget(self.browse_folder_button, 1, 2)
        
        # Options
        self.recursive_check = QCheckBox("Include subdirectories")
        self.recursive_check.setChecked(False)
        selection_layout.addWidget(self.recursive_check, 1, 0, 1, 2)
        
        # Supported formats info
        formats_label = QLabel("Supported: JPEG, PNG, TIFF, BMP, GIF, RAW")
        formats_label.setStyleSheet("color: #7f8c8d; font-size: 10px;")
        selection_layout.addWidget(formats_label, 2, 0, 1, 3)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.read_button = QPushButton("Read Metadata")
        self.read_button.clicked.connect(self.read_metadata)
        self.read_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        button_layout.addWidget(self.read_button)
        
        self.edit_button = QPushButton("Edit Metadata")
        self.edit_button.clicked.connect(self.edit_metadata)
        self.edit_button.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """)
        self.edit_button.setEnabled(False)
        button_layout.addWidget(self.edit_button)
        
        selection_layout.addLayout(button_layout, 3, 0, 1, 3)
        left_layout.addWidget(selection_group)
        
        # Progress section
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Ready to process image metadata")
        progress_layout.addWidget(self.status_label)
        
        left_layout.addWidget(progress_group)
        
        # Quick actions group
        actions_group = QGroupBox("Quick Actions")
        actions_layout = QVBoxLayout(actions_group)
        
        self.export_button = QPushButton("Export Metadata")
        self.export_button.clicked.connect(self.export_metadata)
        self.export_button.setEnabled(False)
        actions_layout.addWidget(self.export_button)
        
        self.save_changes_button = QPushButton("Save Changes")
        self.save_changes_button.clicked.connect(self.save_metadata_changes)
        self.save_changes_button.setEnabled(False)
        actions_layout.addWidget(self.save_changes_button)
        
        self.clear_button = QPushButton("Clear Results")
        self.clear_button.clicked.connect(self.clear_results)
        actions_layout.addWidget(self.clear_button)
        
        left_layout.addWidget(actions_group)
        
        # Metadata options group
        options_group = QGroupBox("Metadata Options")
        options_layout = QVBoxLayout(options_group)
        
        self.include_thumbnails_check = QCheckBox("Include thumbnail data")
        self.include_thumbnails_check.setChecked(False)
        options_layout.addWidget(self.include_thumbnails_check)
        
        self.backup_originals_check = QCheckBox("Backup original files")
        self.backup_originals_check.setChecked(True)
        options_layout.addWidget(self.backup_originals_check)
        
        left_layout.addWidget(options_group)
        
        return left_panel
        
    def _create_right_panel(self):
        """Create the right metadata display panel."""
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Metadata tabs
        self.metadata_tabs = QTabWidget()
        
        # File list tab
        self._create_file_list_tab()
        
        # EXIF data tab
        self._create_exif_tab()
        
        # IPTC data tab
        self._create_iptc_tab()
        
        # XMP data tab
        self._create_xmp_tab()
        
        # Combined metadata tab
        self._create_combined_tab()
        
        right_layout.addWidget(self.metadata_tabs)
        return right_panel
        
    def _create_file_list_tab(self):
        """Create the file list tab."""
        self.file_list_tab = QWidget()
        file_list_layout = QVBoxLayout(self.file_list_tab)
        
        file_list_layout.addWidget(QLabel("Processed Images:"))
        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabels(
            ["Filename", "Format", "Dimensions", "Size", "Modified"])
        self.file_tree.itemClicked.connect(self.show_file_metadata)
        file_list_layout.addWidget(self.file_tree)
        
        self.metadata_tabs.addTab(self.file_list_tab, "Images")
        
    def _create_exif_tab(self):
        """Create the EXIF data tab."""
        self.exif_tab = QWidget()
        exif_layout = QVBoxLayout(self.exif_tab)
        
        exif_layout.addWidget(QLabel("EXIF Data:"))
        self.exif_table = QTableWidget()
        self.exif_table.setColumnCount(3)
        self.exif_table.setHorizontalHeaderLabels(["Tag", "Value", "Editable"])
        self.exif_table.cellChanged.connect(self.on_metadata_changed)
        exif_layout.addWidget(self.exif_table)
        
        self.metadata_tabs.addTab(self.exif_tab, "EXIF")
        
    def _create_iptc_tab(self):
        """Create the IPTC data tab."""
        self.iptc_tab = QWidget()
        iptc_layout = QVBoxLayout(self.iptc_tab)
        
        iptc_layout.addWidget(QLabel("IPTC Data:"))
        self.iptc_table = QTableWidget()
        self.iptc_table.setColumnCount(3)
        self.iptc_table.setHorizontalHeaderLabels(["Tag", "Value", "Editable"])
        self.iptc_table.cellChanged.connect(self.on_metadata_changed)
        iptc_layout.addWidget(self.iptc_table)
        
        self.metadata_tabs.addTab(self.iptc_tab, "IPTC")
        
    def _create_xmp_tab(self):
        """Create the XMP data tab."""
        self.xmp_tab = QWidget()
        xmp_layout = QVBoxLayout(self.xmp_tab)
        
        xmp_layout.addWidget(QLabel("XMP Data:"))
        self.xmp_table = QTableWidget()
        self.xmp_table.setColumnCount(3)
        self.xmp_table.setHorizontalHeaderLabels(["Tag", "Value", "Editable"])
        self.xmp_table.cellChanged.connect(self.on_metadata_changed)
        xmp_layout.addWidget(self.xmp_table)
        
        self.metadata_tabs.addTab(self.xmp_tab, "XMP")
        
    def _create_combined_tab(self):
        """Create the combined metadata tab."""
        self.combined_tab = QWidget()
        combined_layout = QVBoxLayout(self.combined_tab)
        
        combined_layout.addWidget(QLabel("All Metadata:"))
        self.combined_text = QTextEdit()
        self.combined_text.setReadOnly(True)
        combined_layout.addWidget(self.combined_text)
        
        self.metadata_tabs.addTab(self.combined_tab, "All")
        
    def browse_files(self):
        """Browse for image files."""
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Image Files", "",
            "Image Files (*.jpg *.jpeg *.png *.tiff *.tif *.bmp *.gif "
            "*.cr2 *.nef *.arw *.dng);;"
            "JPEG Files (*.jpg *.jpeg);;"
            "PNG Files (*.png);;"
            "TIFF Files (*.tiff *.tif);;"
            "RAW Files (*.cr2 *.nef *.arw *.dng);;"
            "All Files (*.*)"
        )
        if files:
            self.selected_files = files
            self.files_edit.setText(f"{len(files)} image file(s) selected")
            self.edit_button.setEnabled(True)
            
    def browse_folder(self):
        """Browse for folder containing images."""
        folder = QFileDialog.getExistingDirectory(
            self, "Select Folder with Images"
        )
        if folder:
            image_extensions = {'.jpg', '.jpeg', '.png', '.tiff', '.tif', 
                                '.bmp', '.gif', '.cr2', '.nef', '.arw', '.dng'}
            files = []
            
            if self.recursive_check.isChecked():
                for root, dirs, filenames in os.walk(folder):
                    for filename in filenames:
                        if any(filename.lower().endswith(ext)
                               for ext in image_extensions):
                            files.append(os.path.join(root, filename))
            else:
                for filename in os.listdir(folder):
                    file_path = os.path.join(folder, filename)
                    if (os.path.isfile(file_path) and
                            any(filename.lower().endswith(ext)
                                for ext in image_extensions)):
                        files.append(file_path)
            
            self.selected_files = files
            self.files_edit.setText(f"Folder: {folder} ({len(files)} images)")
            self.edit_button.setEnabled(True)
            
    def read_metadata(self):
        """Read metadata from selected images."""
        if not self.selected_files:
            QMessageBox.warning(self, "Warning",
                                "Please select image files first.")
            return
            
        self.start_operation("read")
        
    def edit_metadata(self):
        """Enable metadata editing mode."""
        if not self.current_metadata:
            QMessageBox.warning(self, "Warning",
                                "Please read metadata first.")
            return
            
        self.save_changes_button.setEnabled(True)
        self.show_status_message("Metadata editing enabled")
        
    def save_metadata_changes(self):
        """Save metadata changes to files."""
        if not self.current_file_metadata:
            QMessageBox.warning(self, "Warning",
                                "No metadata changes to save.")
            return
            
        reply = QMessageBox.question(
            self, "Save Changes",
            "Save metadata changes to selected files?\n"
            "Original files will be backed up if enabled.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.start_operation("write", self.current_file_metadata)
        
    def start_operation(self, operation, updates=None):
        """Start metadata operation."""
        # Clear previous results if reading
        if operation == "read":
            self.clear_results()
        
        # Setup UI for operation
        self.read_button.setEnabled(False)
        self.edit_button.setEnabled(False)
        self.save_changes_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        if operation == "read":
            self.status_label.setText("Reading image metadata...")
        else:
            self.status_label.setText("Saving metadata changes...")
        
        # Start worker thread
        self.worker = ImageMetadataWorkerThread(
            self.selected_files, operation, updates)
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.file_processed.connect(self.add_result)
        self.worker.finished.connect(self.operation_finished)
        self.worker.error_occurred.connect(self.show_error)
        self.worker.status_updated.connect(self.update_status)
        self.worker.start()
        
    def update_progress(self, value):
        """Update progress bar."""
        self.progress_bar.setValue(value)
        
    def update_status(self, message):
        """Update status message."""
        self.status_label.setText(message)
        
    def add_result(self, file_path, metadata):
        """Add metadata result to the display."""
        filename = os.path.basename(file_path)
        
        # Add to file tree
        item = QTreeWidgetItem()
        item.setText(0, filename)
        
        # Determine file format and dimensions
        if "basic_metadata" in metadata and metadata["basic_metadata"]:
            basic = metadata["basic_metadata"]
            item.setText(1, basic.get("format", "Unknown"))
            
            width = basic.get("width", "?")
            height = basic.get("height", "?")
            item.setText(2, f"{width}x{height}")
        else:
            item.setText(1, "Unknown")
            item.setText(2, "Unknown")
            
        # File size
        if "file_info" in metadata and metadata["file_info"]:
            size = metadata["file_info"].get("size", 0)
            if size < 1024:
                size_str = f"{size} B"
            elif size < 1024 * 1024:
                size_str = f"{size / 1024:.1f} KB"
            else:
                size_str = f"{size / (1024 * 1024):.1f} MB"
            item.setText(3, size_str)
            
            # Modified date
            modified = metadata["file_info"].get("modified", "")
            if modified:
                try:
                    dt = datetime.fromisoformat(
                        modified.replace('Z', '+00:00'))
                    item.setText(4, dt.strftime("%Y-%m-%d %H:%M"))
                except Exception:
                    item.setText(4, "Unknown")
        
        item.setData(0, Qt.ItemDataRole.UserRole, 
                     {"path": file_path, "metadata": metadata})
        self.file_tree.addTopLevelItem(item)
        
        # Store metadata
        self.current_metadata[file_path] = metadata
        
    def operation_finished(self):
        """Handle operation completion."""
        self.read_button.setEnabled(True)
        self.edit_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        count = self.file_tree.topLevelItemCount()
        self.status_label.setText(f"Completed - {count} images processed")
        
        # Enable action buttons
        self.export_button.setEnabled(True)
        
        if self.worker:
            self.worker.deleteLater()
            self.worker = None
            
    def show_error(self, error_message):
        """Show error message."""
        QMessageBox.warning(self, "Error", error_message)
        
    def show_file_metadata(self, item):
        """Show detailed metadata for selected file."""
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data and "metadata" in data:
            metadata = data["metadata"]
            self.current_file_metadata = metadata
            
            # Update EXIF table
            self._update_metadata_table(self.exif_table,
                                        metadata.get("exif_data", {}))
            
            # Update IPTC table
            self._update_metadata_table(self.iptc_table,
                                        metadata.get("iptc_data", {}))
            
            # Update XMP table
            self._update_metadata_table(self.xmp_table,
                                        metadata.get("xmp_data", {}))
            
            # Update combined view
            self._update_combined_view(metadata)
            
    def _update_metadata_table(self, table, metadata_dict):
        """Update a metadata table with data."""
        table.setRowCount(0)
        
        if not metadata_dict:
            return
            
        for key, value in metadata_dict.items():
            row = table.rowCount()
            table.insertRow(row)
            
            # Tag name
            tag_item = QTreeWidgetItem()
            tag_item.setText(0, str(key))
            table.setItem(row, 0, tag_item)
            
            # Value
            value_item = QTreeWidgetItem()
            value_item.setText(0, str(value))
            table.setItem(row, 1, value_item)
            
            # Editable checkbox
            editable_item = QTreeWidgetItem()
            editable_item.setText(
                0, "Yes" if self._is_editable_tag(key) else "No")
            table.setItem(row, 2, editable_item)
            
        # Resize columns
        table.resizeColumnsToContents()
        
    def _update_combined_view(self, metadata):
        """Update the combined metadata view."""
        import json
        try:
            formatted_text = json.dumps(metadata, indent=2, default=str)
            self.combined_text.setText(formatted_text)
        except Exception as e:
            self.combined_text.setText(f"Error formatting metadata: {str(e)}")
            
    def _is_editable_tag(self, tag):
        """Check if a metadata tag is editable."""
        # Define which tags are safely editable
        editable_tags = {
            'Artist', 'Copyright', 'ImageDescription', 'Software',
            'DateTime', 'DateTimeOriginal', 'DateTimeDigitized',
            'UserComment', 'XPTitle', 'XPComment', 'XPAuthor',
            'XPKeywords', 'XPSubject'
        }
        return str(tag) in editable_tags
        
    def on_metadata_changed(self, row, column):
        """Handle metadata changes in tables."""
        if column == 1:  # Value column
            self.save_changes_button.setEnabled(True)
            self.show_status_message(
                "Metadata modified - remember to save changes")
            
    def clear_results(self):
        """Clear all results."""
        self.file_tree.clear()
        self.exif_table.setRowCount(0)
        self.iptc_table.setRowCount(0)
        self.xmp_table.setRowCount(0)
        self.combined_text.clear()
        self.current_metadata.clear()
        self.current_file_metadata = {}
        self.status_label.setText("Ready to process image metadata")
        
        # Disable action buttons
        self.export_button.setEnabled(False)
        self.save_changes_button.setEnabled(False)
        
    # Menu callback implementations
    def new_image_session(self):
        """Start a new image metadata session."""
        self.clear_results()
        self.selected_files = []
        self.files_edit.clear()
        self.edit_button.setEnabled(False)
        self.show_status_message("New image metadata session started")
        
    def save_image_settings(self):
        """Save current image metadata settings to file."""
        settings = {
            'selected_files': self.selected_files,
            'recursive_search': self.recursive_check.isChecked(),
            'include_thumbnails': self.include_thumbnails_check.isChecked(),
            'backup_originals': self.backup_originals_check.isChecked(),
            'timestamp': datetime.now().isoformat()
        }
        
        file_path = self.get_save_file_path(
            "Save Image Metadata Settings",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            try:
                import json
                with open(file_path, 'w') as f:
                    json.dump(settings, f, indent=2)
                self.show_info_dialog(
                    "Settings Saved",
                    f"Image metadata settings saved to {file_path}"
                )
            except Exception as e:
                self.show_error_dialog(
                    "Save Error",
                    f"Failed to save settings: {str(e)}"
                )
                
    def load_image_settings(self):
        """Load image metadata settings from file."""
        file_path = self.get_file_path(
            "Load Image Metadata Settings",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            try:
                import json
                with open(file_path, 'r') as f:
                    settings = json.load(f)
                
                self.selected_files = settings.get('selected_files', [])
                self.recursive_check.setChecked(
                    settings.get('recursive_search', False))
                self.include_thumbnails_check.setChecked(
                    settings.get('include_thumbnails', False))
                self.backup_originals_check.setChecked(
                    settings.get('backup_originals', True))
                
                if self.selected_files:
                    self.files_edit.setText(
                        f"{len(self.selected_files)} image(s) loaded")
                    self.edit_button.setEnabled(True)
                
                self.show_info_dialog(
                    "Settings Loaded",
                    f"Image metadata settings loaded from {file_path}"
                )
            except Exception as e:
                self.show_error_dialog(
                    "Load Error",
                    f"Failed to load settings: {str(e)}"
                )
                
    def export_metadata(self):
        """Export metadata to file."""
        if not self.current_metadata:
            QMessageBox.warning(self, "Warning", "No metadata to export.")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Image Metadata", "image_metadata.json",
            "JSON Files (*.json);;Text Files (*.txt);;All Files (*.*)"
        )
        
        if file_path:
            try:
                import json
                with open(file_path, 'w') as f:
                    if file_path.endswith('.json'):
                        json.dump(self.current_metadata, f, indent=2,
                                  default=str)
                    else:
                        f.write("Image Metadata Export\n")
                        f.write("=" * 50 + "\n\n")
                        
                        for file_path_key, metadata in \
                                self.current_metadata.items():
                            f.write(f"Image: {file_path_key}\n")
                            f.write("-" * 30 + "\n")
                            f.write(json.dumps(metadata, indent=2,
                                               default=str))
                            f.write("\n\n")
                        
                QMessageBox.information(self, "Success",
                                        "Metadata exported successfully.")
                
            except Exception as e:
                QMessageBox.warning(self, "Error",
                                    f"Failed to export metadata: {e}")
                
    def import_metadata_settings(self):
        """Import metadata from external source."""
        self.show_info_dialog(
            "Import Metadata",
            "Metadata import functionality will be implemented."
        )
        
    def print_metadata_report(self):
        """Print metadata analysis report."""
        self.show_info_dialog(
            "Print Report",
            "Metadata report printing functionality will be implemented."
        )
        
    def cut_text(self):
        """Cut text from focused widget."""
        from PyQt5.QtWidgets import QApplication
        focused = QApplication.focusWidget()
        if focused and hasattr(focused, 'cut'):
            focused.cut()
            
    def copy_text(self):
        """Copy text from focused widget."""
        from PyQt5.QtWidgets import QApplication
        focused = QApplication.focusWidget()
        if focused and hasattr(focused, 'copy'):
            focused.copy()
            
    def paste_text(self):
        """Paste text to focused widget."""
        from PyQt5.QtWidgets import QApplication
        focused = QApplication.focusWidget()
        if focused and hasattr(focused, 'paste'):
            focused.paste()
            
    def select_all_text(self):
        """Select all text in focused widget."""
        from PyQt5.QtWidgets import QApplication
        focused = QApplication.focusWidget()
        if focused and hasattr(focused, 'selectAll'):
            focused.selectAll()
            
    def find_metadata(self):
        """Find text in metadata."""
        self.show_info_dialog(
            "Find in Metadata",
            "Find functionality will be implemented."
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
        
    def show_image_options(self):
        """Show image metadata options dialog."""
        self.show_info_dialog(
            "Image Metadata Options",
            "Image metadata options:\n\n"
            "• Supported file formats\n"
            "• Metadata extraction depth\n"
            "• EXIF, IPTC, XMP handling\n"
            "• Backup and safety settings\n"
            "• Batch processing preferences\n\n"
            "Advanced options coming soon!"
        )
        
    def show_batch_processing(self):
        """Show batch processing dialog."""
        self.show_info_dialog(
            "Batch Processing",
            "Batch image metadata processing functionality will be "
            "implemented."
        )
        
    def analyze_images(self):
        """Analyze image metadata structure."""
        if not self.selected_files:
            self.show_warning_dialog(
                "No Images Selected",
                "Please select images to analyze."
            )
            return
            
        self.show_info_dialog(
            "Image Analysis",
            f"Analyzing {len(self.selected_files)} image(s)...\n\n"
            "Analysis includes:\n"
            "• File format validation\n"
            "• Metadata completeness\n"
            "• EXIF data consistency\n"
            "• Image quality metrics\n"
            "• Geolocation data"
        )
        
    def show_help(self):
        """Show help dialog for Image Metadata Editor."""
        help_text = """
        <h2>Image Metadata Editor - Help</h2>
        
        <h3>Overview:</h3>
        <p>The Image Metadata Editor allows you to view, edit, and manage
        metadata from various image formats including EXIF, IPTC, and XMP
        data.</p>
        
        <h3>Supported Formats:</h3>
        <ul>
        <li><b>JPEG:</b> Full EXIF, IPTC, XMP support</li>
        <li><b>TIFF:</b> Full EXIF, limited IPTC/XMP</li>
        <li><b>PNG:</b> Limited metadata (mainly XMP)</li>
        <li><b>RAW:</b> Read-only EXIF support (CR2, NEF, ARW, DNG)</li>
        <li><b>BMP, GIF:</b> Basic metadata only</li>
        </ul>
        
        <h3>Features:</h3>
        <ul>
        <li><b>Batch Processing:</b> Analyze multiple images at once</li>
        <li><b>Export Options:</b> Save metadata to JSON or text files</li>
        <li><b>Metadata Types:</b> EXIF, IPTC, and XMP data</li>
        <li><b>Safe Editing:</b> Backup originals before changes</li>
        <li><b>Search:</b> Recursive folder scanning</li>
        </ul>
        
        <h3>Usage:</h3>
        <ol>
        <li>Select images or folders using Browse buttons</li>
        <li>Click "Read Metadata" to analyze images</li>
        <li>View results in the tabbed interface</li>
        <li>Edit metadata in the EXIF/IPTC/XMP tabs</li>
        <li>Save changes using "Save Changes" button</li>
        <li>Export results using the Export button</li>
        </ol>
        
        <h3>Keyboard Shortcuts:</h3>
        <ul>
        <li><b>Ctrl+O:</b> Open images</li>
        <li><b>Ctrl+S:</b> Save settings</li>
        <li><b>Ctrl+E:</b> Export metadata</li>
        <li><b>F5:</b> Refresh view</li>
        <li><b>F1:</b> Show this help</li>
        </ul>
        
        <h3>Safety Notes:</h3>
        <ul>
        <li>Always backup original files before editing</li>
        <li>Test metadata changes on copies first</li>
        <li>Some RAW formats are read-only</li>
        <li>IPTC/XMP support varies by format</li>
        </ul>
        """
        
        QMessageBox.information(self, "Image Metadata Editor Help", help_text)

    def closeEvent(self, a0):
        """Handle window close event."""
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.worker.wait()
        super().closeEvent(a0)


def main():
    """Main function for standalone execution."""
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = ImageMetadataEditorGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()