"""
Enhanced Image Metadata Editor with Menu Integration

This enhanced version provides comprehensive image metadata viewing and editing
with standardized menu integration following the File Finder template pattern.
"""

import os
import sys
import json
from datetime import datetime

# Add the src directory to the Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Try to import StandardWindow, fall back to QMainWindow if not available
STANDARD_WINDOW_AVAILABLE = False
try:
    from src.rfu.gui.standard_window import StandardWindow
    STANDARD_WINDOW_AVAILABLE = True
except ImportError:
    print("StandardWindow not available, using fallback mode")
    from PyQt5.QtWidgets import QMainWindow as StandardWindow

try:
    from PyQt5.QtWidgets import (
        QWidget, QVBoxLayout, QGridLayout,
        QPushButton, QLineEdit, QLabel, QCheckBox, QGroupBox,
        QFileDialog, QMessageBox, QProgressBar, QApplication,
        QTextEdit, QSplitter, QTreeWidget, QTreeWidgetItem,
        QTableWidget, QTableWidgetItem, QTabWidget, QHBoxLayout
    )
    from PyQt5.QtCore import Qt, QThread, pyqtSignal
    from PyQt5.QtGui import QFont
    
    class MetadataWorker(QThread):
        """Worker thread for metadata operations."""
        
        progress_updated = pyqtSignal(int)
        file_processed = pyqtSignal(str, dict)  # file_path, metadata
        finished = pyqtSignal()
        error_occurred = pyqtSignal(str)
        
        def __init__(self, files, operation, metadata_updates=None):
            super().__init__()
            self.files = files
            self.operation = operation
            self.metadata_updates = metadata_updates or {}
            self.is_cancelled = False
            
        def run(self):
            """Execute metadata operation."""
            try:
                total_files = len(self.files)
                
                for i, file_path in enumerate(self.files):
                    if self.is_cancelled:
                        break
                        
                    try:
                        if self.operation == "read":
                            metadata = self.read_metadata(file_path)
                            self.file_processed.emit(file_path, metadata)
                        elif self.operation == "write":
                            self.write_metadata(file_path, self.metadata_updates)
                            metadata = self.read_metadata(file_path)
                            self.file_processed.emit(file_path, metadata)
                            
                    except Exception as e:
                        error_msg = f"Error processing {file_path}: {str(e)}"
                        self.error_occurred.emit(error_msg)
                    
                    progress = int((i + 1) / total_files * 100)
                    self.progress_updated.emit(progress)
                    
                self.finished.emit()
                
            except Exception as e:
                self.error_occurred.emit(f"Worker error: {str(e)}")
        
        def read_metadata(self, file_path):
            """Read metadata from image file."""
            metadata = {
                "file_info": {},
                "basic_metadata": {},
                "exif_data": {},
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
                        stat_info.st_ctime).isoformat()
                }
                
                # Try to get image dimensions and basic info
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
                        
                        # Try to extract EXIF data
                        if hasattr(img, '_getexif') and img._getexif():
                            exif_data = img._getexif()
                            metadata["exif_data"] = self.parse_exif_data(exif_data)
                        elif hasattr(img, 'getexif'):
                            exif_data = img.getexif()
                            metadata["exif_data"] = self.parse_exif_data(exif_data)
                            
                except ImportError:
                    # Fallback without PIL
                    metadata["basic_metadata"] = {
                        "format": "Unknown (PIL not available)",
                        "note": "Install Pillow for full metadata support"
                    }
                except Exception as e:
                    metadata["error"] = f"Image processing error: {str(e)}"
                    
            except Exception as e:
                metadata["error"] = f"File access error: {str(e)}"
                
            return metadata
        
        def parse_exif_data(self, exif_data):
            """Parse EXIF data into readable format."""
            parsed_exif = {}
            
            # Common EXIF tags
            exif_tags = {
                256: "ImageWidth",
                257: "ImageLength", 
                272: "Make",
                273: "StripOffsets",
                274: "Orientation",
                282: "XResolution",
                283: "YResolution",
                296: "ResolutionUnit",
                306: "DateTime",
                315: "Artist",
                33432: "Copyright",
                36867: "DateTimeOriginal",
                36868: "DateTimeDigitized"
            }
            
            try:
                for tag_id, value in exif_data.items():
                    tag_name = exif_tags.get(tag_id, f"Tag_{tag_id}")
                    if isinstance(value, bytes):
                        try:
                            value = value.decode('utf-8', errors='ignore')
                        except Exception:
                            value = str(value)
                    parsed_exif[tag_name] = str(value)
            except Exception as e:
                parsed_exif["error"] = f"EXIF parsing error: {str(e)}"
                
            return parsed_exif
        
        def write_metadata(self, file_path, updates):
            """Write metadata to image file."""
            # This is a placeholder for metadata writing functionality
            # Full implementation would require specialized libraries
            raise NotImplementedError(
                "Metadata writing requires additional libraries")
        
        def cancel(self):
            """Cancel the operation."""
            self.is_cancelled = True


    class EnhancedImageMetadataEditorGUI(StandardWindow):
        """Enhanced Image Metadata Editor GUI with menu integration."""
        
        def __init__(self):
            if STANDARD_WINDOW_AVAILABLE:
                super().__init__(
                    title="Image Metadata Editor - Richard's File Utilities",
                    window_type="metadata"
                )
            else:
                super().__init__()
                self.setWindowTitle("Image Metadata Editor - Richard's File Utilities")
                self.setGeometry(100, 100, 1200, 800)
            
            self.worker = None
            self.selected_files = []
            self.current_metadata = {}
            
            self.init_ui()
            if STANDARD_WINDOW_AVAILABLE:
                self._setup_menu_callbacks()
            
        def _setup_menu_callbacks(self):
            """Setup tool-specific menu callbacks."""
            if hasattr(self, 'menu_manager'):
                # Register tool-specific callbacks
                self.menu_manager.register_callback('new_metadata_session', self.clear_results)
                self.menu_manager.register_callback('export_metadata', self.export_metadata)
                self.menu_manager.register_callback('help_image_metadata', self.show_help)
                
        def show_help(self):
            """Show comprehensive help for Image Metadata Editor."""
            help_text = """
            <h2>Image Metadata Editor - Comprehensive Guide</h2>
            
            <h3>📸 Overview</h3>
            <p>The Image Metadata Editor provides comprehensive image metadata viewing 
            and analysis capabilities for various image formats, including EXIF data 
            extraction and file information analysis.</p>
            
            <h3>🚀 Key Features</h3>
            <ul>
                <li><b>Multi-Format Support</b>: JPEG, PNG, TIFF, BMP, GIF images</li>
                <li><b>EXIF Data Extraction</b>: Camera settings, timestamps, GPS data</li>
                <li><b>Batch Processing</b>: Process multiple images simultaneously</li>
                <li><b>File Information</b>: Size, dimensions, creation dates</li>
                <li><b>Data Export</b>: Export metadata to JSON or text formats</li>
                <li><b>Folder Scanning</b>: Recursive directory processing</li>
            </ul>
            
            <h3>📊 Supported Image Formats</h3>
            <ul>
                <li><b>JPEG/JPG</b>: Full EXIF support, camera metadata</li>
                <li><b>PNG</b>: Basic metadata and transparency info</li>
                <li><b>TIFF</b>: Professional image metadata</li>
                <li><b>BMP</b>: Basic bitmap information</li>
                <li><b>GIF</b>: Animation and palette information</li>
            </ul>
            
            <h3>🔧 EXIF Data Categories</h3>
            <ul>
                <li><b>Camera Information</b>: Make, model, lens details</li>
                <li><b>Image Settings</b>: Resolution, color space, orientation</li>
                <li><b>Shooting Conditions</b>: ISO, aperture, shutter speed</li>
                <li><b>Timestamps</b>: Creation, modification, digitization dates</li>
                <li><b>GPS Data</b>: Location coordinates (if available)</li>
                <li><b>Copyright Information</b>: Artist, copyright notices</li>
            </ul>
            
            <h3>📁 File Selection Options</h3>
            <ul>
                <li><b>Browse Images</b>: Select individual image files</li>
                <li><b>Browse Folder</b>: Process all images in a directory</li>
                <li><b>Recursive Processing</b>: Include subdirectories</li>
                <li><b>Format Filtering</b>: Automatic image format detection</li>
            </ul>
            
            <h3>📈 Metadata Display</h3>
            <ul>
                <li><b>Files Tab</b>: Overview of processed images with basic info</li>
                <li><b>Details Tab</b>: Comprehensive property-value pairs</li>
                <li><b>EXIF Tab</b>: Raw EXIF data in structured format</li>
                <li><b>Interactive Selection</b>: Click files to view detailed metadata</li>
            </ul>
            
            <h3>💾 Export Options</h3>
            <ul>
                <li><b>JSON Format</b>: Structured data for programming use</li>
                <li><b>Text Format</b>: Human-readable metadata reports</li>
                <li><b>Batch Export</b>: Export all processed image metadata</li>
                <li><b>Selective Export</b>: Export specific image metadata</li>
            </ul>
            
            <h3>🛠️ Advanced Features</h3>
            <ul>
                <li><b>Background Processing</b>: Non-blocking metadata extraction</li>
                <li><b>Progress Monitoring</b>: Real-time processing status</li>
                <li><b>Error Handling</b>: Graceful handling of corrupted files</li>
                <li><b>Memory Efficient</b>: Optimized for large image collections</li>
            </ul>
            
            <h3>📋 Common EXIF Tags</h3>
            <ul>
                <li><b>Make/Model</b>: Camera manufacturer and model</li>
                <li><b>DateTime</b>: Image creation timestamp</li>
                <li><b>Orientation</b>: Image rotation information</li>
                <li><b>XResolution/YResolution</b>: Image resolution settings</li>
                <li><b>Artist</b>: Photographer or creator name</li>
                <li><b>Copyright</b>: Copyright information</li>
            </ul>
            
            <h3>⚠️ Usage Guidelines</h3>
            <ul>
                <li><b>Large Collections</b>: Process images in smaller batches for better performance</li>
                <li><b>Privacy Awareness</b>: EXIF data may contain sensitive location information</li>
                <li><b>Format Limitations</b>: Some formats have limited metadata support</li>
                <li><b>Backup Important Files</b>: Always backup before metadata editing</li>
            </ul>
            
            <h3>🔧 Dependencies</h3>
            <ul>
                <li><b>PIL/Pillow</b>: Required for full image metadata support</li>
                <li><b>PyQt5</b>: GUI framework for the application interface</li>
                <li><b>JSON Support</b>: Built-in Python library for data export</li>
            </ul>
            
            <h3>🚀 Getting Started</h3>
            <ol>
                <li>Click 'Browse Images' to select individual files or 'Browse Folder' for batch processing</li>
                <li>Enable 'Include subdirectories' for recursive folder scanning</li>
                <li>Click 'Read Metadata' to start the extraction process</li>
                <li>Browse the results in the Files, Details, and EXIF tabs</li>
                <li>Export metadata using the 'Export Metadata' button</li>
            </ol>
            
            <p><b>Note:</b> For full functionality, ensure PIL/Pillow is installed. 
            Some advanced EXIF features may require additional libraries.</p>
            """
            
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Image Metadata Editor - Help")
            msg_box.setTextFormat(1)  # Rich text format
            msg_box.setText(help_text)
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.resize(800, 600)
            msg_box.exec_()
            
        def show_preferences(self):
            """Show Image Metadata Editor preferences."""
            QMessageBox.information(self, "Image Metadata Editor Preferences", 
                                   "Image Metadata Editor preferences:\n\n"
                                   "• Supported image formats\n"
                                   "• EXIF data extraction settings\n"
                                   "• Export format preferences\n"
                                   "• Batch processing options\n"
                                   "• Privacy and security settings\n\n"
                                   "Advanced preferences coming soon!")
                                   
        def refresh_view(self):
            """Refresh the current metadata view."""
            if self.current_metadata:
                # Refresh the display of current metadata
                count = len(self.current_metadata)
                self.status_label.setText(f"Refreshed - {count} images loaded")
            else:
                self.clear_results()
                
        def new_metadata_session(self):
            """Start a new metadata session."""
            self.clear_results()
            self.selected_files = []
            self.files_edit.clear()
            self.edit_button.setEnabled(False)
        
        def init_ui(self):
            """Initialize the user interface."""
            # Use the existing main layout from StandardWindow or create new layout
            if STANDARD_WINDOW_AVAILABLE and hasattr(self, 'main_layout'):
                layout = self.main_layout
            else:
                # Create central widget and layout for fallback mode
                central_widget = QWidget()
                self.setCentralWidget(central_widget)
                layout = QVBoxLayout(central_widget)
            
            # Add header
            header_label = QLabel("Image Metadata Editor")
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
            
            # Create main splitter
            main_splitter = QSplitter(Qt.Orientation.Horizontal)
            layout.addWidget(main_splitter)
            
            # Left panel - File selection and controls
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
            self.browse_files_button.setStyleSheet("""
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
            selection_layout.addWidget(self.browse_files_button, 0, 2)
            
            self.browse_folder_button = QPushButton("Browse Folder")
            self.browse_folder_button.clicked.connect(self.browse_folder)
            self.browse_folder_button.setStyleSheet("""
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
            selection_layout.addWidget(self.browse_folder_button, 0, 3)
            
            # Options
            self.recursive_check = QCheckBox("Include subdirectories")
            self.recursive_check.setChecked(False)
            selection_layout.addWidget(self.recursive_check, 1, 0, 1, 2)
            
            # Supported formats info
            formats_label = QLabel("Supported: JPEG, PNG, TIFF, BMP, GIF")
            formats_label.setStyleSheet("color: #7f8c8d; font-size: 10px;")
            selection_layout.addWidget(formats_label, 1, 2, 1, 2)
            
            # Action buttons
            self.read_button = QPushButton("Read Metadata")
            self.read_button.clicked.connect(self.read_metadata)
            self.read_button.setStyleSheet("""
                QPushButton {
                    background-color: #27ae60;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #229954;
                }
            """)
            selection_layout.addWidget(self.read_button, 2, 0, 1, 2)
            
            self.edit_button = QPushButton("Edit Metadata")
            self.edit_button.clicked.connect(self.edit_metadata)
            self.edit_button.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            self.edit_button.setEnabled(False)
            selection_layout.addWidget(self.edit_button, 2, 2, 1, 2)
            
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
            
            self.clear_button = QPushButton("Clear Results")
            self.clear_button.clicked.connect(self.clear_results)
            actions_layout.addWidget(self.clear_button)
            
            left_layout.addWidget(actions_group)
            
            main_splitter.addWidget(left_panel)
            
            # Right panel - Metadata display
            right_panel = QWidget()
            right_layout = QVBoxLayout(right_panel)
            
            # Metadata tabs
            self.metadata_tabs = QTabWidget()
            
            # File list tab
            self.file_list_tab = QWidget()
            file_list_layout = QVBoxLayout(self.file_list_tab)
            
            file_list_layout.addWidget(QLabel("Processed Files:"))
            self.file_tree = QTreeWidget()
            self.file_tree.setHeaderLabels(
                ["Filename", "Format", "Dimensions", "Size"])
            self.file_tree.itemClicked.connect(self.show_file_metadata)
            file_list_layout.addWidget(self.file_tree)
            
            self.metadata_tabs.addTab(self.file_list_tab, "Files")
            
            # Metadata details tab
            self.details_tab = QWidget()
            details_layout = QVBoxLayout(self.details_tab)
            
            details_layout.addWidget(QLabel("Metadata Details:"))
            self.metadata_table = QTableWidget()
            self.metadata_table.setColumnCount(2)
            self.metadata_table.setHorizontalHeaderLabels(["Property", "Value"])
            details_layout.addWidget(self.metadata_table)
            
            self.metadata_tabs.addTab(self.details_tab, "Details")
            
            # EXIF data tab
            self.exif_tab = QWidget()
            exif_layout = QVBoxLayout(self.exif_tab)
            
            exif_layout.addWidget(QLabel("EXIF Data:"))
            self.exif_text = QTextEdit()
            self.exif_text.setReadOnly(True)
            exif_layout.addWidget(self.exif_text)
            
            self.metadata_tabs.addTab(self.exif_tab, "EXIF")
            
            right_layout.addWidget(self.metadata_tabs)
            main_splitter.addWidget(right_panel)
            
            # Set splitter proportions
            main_splitter.setSizes([400, 800])
            
        def browse_files(self):
            """Browse for image files."""
            files, _ = QFileDialog.getOpenFileNames(
                self, "Select Image Files", "",
                "Image Files (*.jpg *.jpeg *.png *.tiff *.tif *.bmp *.gif);;"
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
                image_extensions = {'.jpg', '.jpeg', '.png', '.tiff',
                                  '.tif', '.bmp', '.gif'}
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
            """Edit metadata for selected images."""
            QMessageBox.information(
                self, "Edit Metadata",
                "Metadata editing functionality requires additional libraries "
                "(piexif, exifread) for full EXIF manipulation. This feature "
                "provides a foundation for metadata editing implementation."
            )
            
        def start_operation(self, operation, updates=None):
            """Start metadata operation."""
            # Clear previous results
            self.clear_results()
            
            # Setup UI for operation
            self.read_button.setEnabled(False)
            self.edit_button.setEnabled(False)
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            
            if operation == "read":
                self.status_label.setText("Reading image metadata...")
            else:
                self.status_label.setText("Updating image metadata...")
            
            # Start worker thread
            self.worker = MetadataWorker(self.selected_files, operation, updates)
            self.worker.progress_updated.connect(self.update_progress)
            self.worker.file_processed.connect(self.add_result)
            self.worker.finished.connect(self.operation_finished)
            self.worker.error_occurred.connect(self.show_error)
            self.worker.start()
            
        def update_progress(self, value):
            """Update progress bar."""
            self.progress_bar.setValue(value)
            
        def add_result(self, file_path, metadata):
            """Add metadata result to the display."""
            filename = os.path.basename(file_path)
            
            # Add to file tree
            item = QTreeWidgetItem()
            item.setText(0, filename)
            
            if "basic_metadata" in metadata and metadata["basic_metadata"]:
                basic = metadata["basic_metadata"]
                item.setText(1, basic.get("format", "Unknown"))
                
                width = basic.get("width", "?")
                height = basic.get("height", "?")
                item.setText(2, f"{width}x{height}")
            else:
                item.setText(1, "Unknown")
                item.setText(2, "Unknown")
                
            if "file_info" in metadata and metadata["file_info"]:
                size = metadata["file_info"].get("size", 0)
                if size < 1024:
                    size_str = f"{size} B"
                elif size < 1024 * 1024:
                    size_str = f"{size / 1024:.1f} KB"
                else:
                    size_str = f"{size / (1024 * 1024):.1f} MB"
                item.setText(3, size_str)
            
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
                
                # Update metadata table
                self.metadata_table.setRowCount(0)
                
                # Add file info
                if "file_info" in metadata:
                    for key, value in metadata["file_info"].items():
                        row = self.metadata_table.rowCount()
                        self.metadata_table.insertRow(row)
                        self.metadata_table.setItem(row, 0,
                                                   QTableWidgetItem(f"File.{key}"))
                        self.metadata_table.setItem(row, 1,
                                                   QTableWidgetItem(str(value)))
                
                # Add basic metadata
                if "basic_metadata" in metadata:
                    for key, value in metadata["basic_metadata"].items():
                        row = self.metadata_table.rowCount()
                        self.metadata_table.insertRow(row)
                        self.metadata_table.setItem(row, 0,
                                                   QTableWidgetItem(f"Image.{key}"))
                        self.metadata_table.setItem(row, 1,
                                                   QTableWidgetItem(str(value)))
                
                # Update EXIF display
                exif_text = ""
                if "exif_data" in metadata and metadata["exif_data"]:
                    exif_text = json.dumps(metadata["exif_data"], indent=2)
                else:
                    exif_text = "No EXIF data available"
                    
                if "error" in metadata and metadata["error"]:
                    exif_text += f"\n\nError: {metadata['error']}"
                    
                self.exif_text.setText(exif_text)
                
                # Resize table columns
                self.metadata_table.resizeColumnsToContents()
                
        def export_metadata(self):
            """Export metadata to file."""
            if not self.current_metadata:
                QMessageBox.warning(self, "Warning", "No metadata to export.")
                return
                
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Metadata", "image_metadata.json",
                "JSON Files (*.json);;Text Files (*.txt);;All Files (*.*)"
            )
            
            if file_path:
                try:
                    with open(file_path, 'w') as f:
                        if file_path.endswith('.json'):
                            json.dump(self.current_metadata, f, indent=2,
                                     default=str)
                        else:
                            f.write("Image Metadata Export\n")
                            f.write("=" * 50 + "\n\n")
                            
                            for file_path, metadata in \
                                    self.current_metadata.items():
                                f.write(f"File: {file_path}\n")
                                f.write("-" * 30 + "\n")
                                f.write(json.dumps(metadata, indent=2,
                                                 default=str))
                                f.write("\n\n")
                            
                    QMessageBox.information(self, "Success",
                                            "Metadata exported successfully.")
                    
                except Exception as e:
                    QMessageBox.warning(self, "Error",
                                        f"Failed to export metadata: {e}")
                    
        def clear_results(self):
            """Clear all results."""
            self.file_tree.clear()
            self.metadata_table.setRowCount(0)
            self.exif_text.clear()
            self.current_metadata.clear()
            self.status_label.setText("Ready to process image metadata")
            
            # Disable action buttons
            self.export_button.setEnabled(False)
            
        def closeEvent(self, event):
            """Handle window close event."""
            if self.worker and self.worker.isRunning():
                self.worker.cancel()
                self.worker.wait()
            super().closeEvent(event)


    def main():
        """Main function to run the Enhanced Image Metadata Editor."""
        app = QApplication(sys.argv)
        
        # Set application style
        app.setStyle('Fusion')
        
        # Create and show the main window
        window = EnhancedImageMetadataEditorGUI()
        window.show()
        
        sys.exit(app.exec_())


    if __name__ == "__main__":
        main()

except ImportError as e:
    print(f"Error importing PyQt5 modules: {e}")
    print("Please ensure PyQt5 is properly installed.")
    
    def main():
        print("Enhanced Image Metadata Editor requires PyQt5 to be installed.")
        print("Please install PyQt5 using: pip install PyQt5")

    if __name__ == "__main__":
        main()
