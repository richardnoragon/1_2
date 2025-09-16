"""Preview Pane Component.

Enterprise-grade file preview component that provides rich preview capabilities
for various file types with performance optimization and accessibility features.

Features:
- Multi-format file preview support
- Lazy loading and caching
- Metadata display integration
- Accessibility compliance
- Performance optimization
- Error handling and fallbacks
"""

import logging
import mimetypes
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from PyQt5.QtCore import (QMutex, QObject, QPropertyAnimation, QRect, QSize,
                          Qt, QThread, QTimer, pyqtSignal)
from PyQt5.QtGui import (QFont, QFontMetrics, QIcon, QMovie, QPainter,
                         QPalette, QPixmap, QTextCharFormat, QTextDocument)
from PyQt5.QtWidgets import (QApplication, QFrame, QGraphicsDropShadowEffect,
                             QHBoxLayout, QLabel, QPlainTextEdit, QScrollArea,
                             QSizePolicy, QSplitter, QTabWidget, QTextEdit,
                             QVBoxLayout, QWidget)

from src.utilities.advanced_folders.models.folder_models import FileMetadata


class PreviewContentLoader(QThread):
    """Background thread for loading preview content."""
    
    contentLoaded = pyqtSignal(str, dict)  # file_path, content_data
    loadingFailed = pyqtSignal(str, str)  # file_path, error_message
    loadingProgress = pyqtSignal(str, int)  # file_path, progress_percent
    
    def __init__(self, parent: Optional[QObject] = None):
        """Initialize content loader.
        
        Args:
            parent: Parent QObject
        """
        super().__init__(parent)
        self.file_queue: List[str] = []
        self.mutex = QMutex()
        self.should_stop = False
        
        # Preview cache
        self.content_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_max_size = 50  # Maximum cached previews
    
    def queue_file_for_preview(self, file_path: str):
        """Queue a file for preview loading.
        
        Args:
            file_path: Path to file to preview
        """
        with QMutex():
            if file_path not in self.file_queue:
                self.file_queue.append(file_path)
    
    def clear_queue(self):
        """Clear the preview queue."""
        with QMutex():
            self.file_queue.clear()
    
    def run(self):
        """Main thread execution loop."""
        while not self.should_stop:
            file_path = None
            
            # Get next file from queue
            with QMutex():
                if self.file_queue:
                    file_path = self.file_queue.pop(0)
            
            if file_path:
                self._load_file_preview(file_path)
            else:
                self.msleep(100)  # Wait for new files
    
    def _load_file_preview(self, file_path: str):
        """Load preview content for a file.
        
        Args:
            file_path: Path to file
        """
        try:
            # Check cache first
            if file_path in self.content_cache:
                self.contentLoaded.emit(file_path, self.content_cache[file_path])
                return
            
            self.loadingProgress.emit(file_path, 10)
            
            # Determine file type and load appropriate preview
            content_data = self._determine_and_load_content(file_path)
            
            self.loadingProgress.emit(file_path, 90)
            
            # Cache content (with size limit)
            self._cache_content(file_path, content_data)
            
            self.loadingProgress.emit(file_path, 100)
            self.contentLoaded.emit(file_path, content_data)
            
        except Exception as e:
            self.loadingFailed.emit(file_path, str(e))
    
    def _determine_and_load_content(self, file_path: str) -> Dict[str, Any]:
        """Determine file type and load appropriate content.
        
        Args:
            file_path: Path to file
            
        Returns:
            Content data dictionary
        """
        file_path_obj = Path(file_path)
        
        if not file_path_obj.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Get file info
        file_stats = file_path_obj.stat()
        mime_type, _ = mimetypes.guess_type(file_path)
        
        content_data = {
            'file_path': file_path,
            'file_name': file_path_obj.name,
            'file_size': file_stats.st_size,
            'mime_type': mime_type,
            'modified_time': file_stats.st_mtime,
            'preview_type': 'unsupported',
            'content': None,
            'metadata': {},
            'error': None
        }
        
        # Load content based on file type
        if mime_type:
            if mime_type.startswith('text/'):
                content_data.update(self._load_text_content(file_path))
            elif mime_type.startswith('image/'):
                content_data.update(self._load_image_content(file_path))
            elif mime_type == 'application/pdf':
                content_data.update(self._load_pdf_content(file_path))
            elif mime_type.startswith('audio/'):
                content_data.update(self._load_audio_metadata(file_path))
            elif mime_type.startswith('video/'):
                content_data.update(self._load_video_metadata(file_path))
        
        return content_data
    
    def _load_text_content(self, file_path: str) -> Dict[str, Any]:
        """Load text file content.
        
        Args:
            file_path: Path to text file
            
        Returns:
            Text content data
        """
        try:
            # Try different encodings
            encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252']
            content = None
            encoding_used = None
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        # Read first 64KB for preview
                        content = f.read(65536)
                        encoding_used = encoding
                        break
                except UnicodeDecodeError:
                    continue
            
            if content is None:
                raise ValueError("Unable to decode text file")
            
            # Count lines and characters
            lines = content.split('\n')
            
            return {
                'preview_type': 'text',
                'content': content,
                'metadata': {
                    'encoding': encoding_used,
                    'line_count': len(lines),
                    'char_count': len(content),
                    'truncated': len(content) == 65536
                }
            }
            
        except Exception as e:
            return {
                'preview_type': 'error',
                'error': f"Failed to load text content: {e}"
            }
    
    def _load_image_content(self, file_path: str) -> Dict[str, Any]:
        """Load image file content.
        
        Args:
            file_path: Path to image file
            
        Returns:
            Image content data
        """
        try:
            pixmap = QPixmap(file_path)
            
            if pixmap.isNull():
                raise ValueError("Failed to load image")
            
            # Scale for preview if too large
            max_size = 800
            if pixmap.width() > max_size or pixmap.height() > max_size:
                pixmap = pixmap.scaled(
                    max_size, max_size,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
            
            return {
                'preview_type': 'image',
                'content': pixmap,
                'metadata': {
                    'width': pixmap.width(),
                    'height': pixmap.height(),
                    'depth': pixmap.depth(),
                    'has_alpha': pixmap.hasAlpha()
                }
            }
            
        except Exception as e:
            return {
                'preview_type': 'error',
                'error': f"Failed to load image: {e}"
            }
    
    def _load_pdf_content(self, file_path: str) -> Dict[str, Any]:
        """Load PDF file metadata and first page preview.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            PDF content data
        """
        try:
            # This would require a PDF library like PyMuPDF
            # For now, return metadata only
            return {
                'preview_type': 'pdf',
                'content': f"PDF file: {Path(file_path).name}",
                'metadata': {
                    'pages': 'Unknown',
                    'title': 'Unknown',
                    'author': 'Unknown',
                    'subject': 'Unknown'
                }
            }
            
        except Exception as e:
            return {
                'preview_type': 'error',
                'error': f"Failed to load PDF: {e}"
            }
    
    def _load_audio_metadata(self, file_path: str) -> Dict[str, Any]:
        """Load audio file metadata.
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Audio metadata
        """
        try:
            # This would require an audio library like mutagen
            # For now, return basic info
            return {
                'preview_type': 'audio',
                'content': f"Audio file: {Path(file_path).name}",
                'metadata': {
                    'duration': 'Unknown',
                    'bitrate': 'Unknown',
                    'title': 'Unknown',
                    'artist': 'Unknown',
                    'album': 'Unknown'
                }
            }
            
        except Exception as e:
            return {
                'preview_type': 'error',
                'error': f"Failed to load audio metadata: {e}"
            }
    
    def _load_video_metadata(self, file_path: str) -> Dict[str, Any]:
        """Load video file metadata.
        
        Args:
            file_path: Path to video file
            
        Returns:
            Video metadata
        """
        try:
            # This would require a video library like opencv or ffmpeg
            # For now, return basic info
            return {
                'preview_type': 'video',
                'content': f"Video file: {Path(file_path).name}",
                'metadata': {
                    'duration': 'Unknown',
                    'resolution': 'Unknown',
                    'codec': 'Unknown',
                    'fps': 'Unknown'
                }
            }
            
        except Exception as e:
            return {
                'preview_type': 'error',
                'error': f"Failed to load video metadata: {e}"
            }
    
    def _cache_content(self, file_path: str, content_data: Dict[str, Any]):
        """Cache content data.
        
        Args:
            file_path: File path
            content_data: Content data to cache
        """
        # Implement LRU cache
        if len(self.content_cache) >= self.cache_max_size:
            # Remove oldest item
            oldest_key = next(iter(self.content_cache))
            del self.content_cache[oldest_key]
        
        self.content_cache[file_path] = content_data
    
    def stop(self):
        """Stop the content loader thread."""
        self.should_stop = True
        self.quit()
        self.wait()


class PreviewPaneWidget(QWidget):
    """Enterprise-grade preview pane widget.
    
    Features:
    - Multi-format file preview
    - Tabbed interface for preview and metadata
    - Performance optimization with lazy loading
    - Accessibility compliance
    - Error handling and fallbacks
    """
    
    # Signals
    previewRequested = pyqtSignal(str)  # file_path
    previewLoaded = pyqtSignal(str, dict)  # file_path, content_data
    previewError = pyqtSignal(str, str)  # file_path, error_message
    
    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize preview pane widget.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Initialize logging
        self.logger = logging.getLogger('AdvancedFolders.PreviewPane')
        self.logger.info("Initializing Preview Pane Widget")
        
        # Current preview state
        self.current_file_path = ""
        self.current_content_data: Dict[str, Any] = {}
        
        # Initialize content loader
        self.content_loader = PreviewContentLoader(self)
        self.content_loader.contentLoaded.connect(self._handle_content_loaded)
        self.content_loader.loadingFailed.connect(self._handle_loading_failed)
        self.content_loader.loadingProgress.connect(self._handle_loading_progress)
        self.content_loader.start()
        
        # Setup UI
        self._setup_ui()
        self._apply_styling()
        self._setup_accessibility()
        
        self.logger.info("Preview Pane Widget initialized successfully")
    
    def _setup_ui(self):
        """Setup the user interface."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)
        
        # Create header
        self._create_header(main_layout)
        
        # Create tabbed content area
        self._create_content_tabs(main_layout)
        
        # Create status area
        self._create_status_area(main_layout)
    
    def _create_header(self, parent_layout: QVBoxLayout):
        """Create preview header.
        
        Args:
            parent_layout: Parent layout
        """
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        header_frame.setMaximumHeight(40)
        
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(8, 4, 8, 4)
        
        # File name label
        self.file_name_label = QLabel("No file selected")
        self.file_name_label.setStyleSheet("font-weight: bold; color: #333333;")
        
        # File size label
        self.file_size_label = QLabel("")
        self.file_size_label.setStyleSheet("color: #666666;")
        
        header_layout.addWidget(self.file_name_label)
        header_layout.addStretch()
        header_layout.addWidget(self.file_size_label)
        
        parent_layout.addWidget(header_frame)
    
    def _create_content_tabs(self, parent_layout: QVBoxLayout):
        """Create content tabs.
        
        Args:
            parent_layout: Parent layout
        """
        self.content_tabs = QTabWidget()
        self.content_tabs.setTabPosition(QTabWidget.North)
        
        # Preview tab
        self._create_preview_tab()
        
        # Metadata tab
        self._create_metadata_tab()
        
        # Properties tab
        self._create_properties_tab()
        
        parent_layout.addWidget(self.content_tabs)
    
    def _create_preview_tab(self):
        """Create the preview tab."""
        # Preview container
        self.preview_widget = QWidget()
        preview_layout = QVBoxLayout(self.preview_widget)
        preview_layout.setContentsMargins(4, 4, 4, 4)
        
        # Scroll area for preview content
        self.preview_scroll = QScrollArea()
        self.preview_scroll.setWidgetResizable(True)
        self.preview_scroll.setAlignment(Qt.AlignCenter)
        
        # Preview content widget
        self.preview_content = QLabel("Select a file to preview")
        self.preview_content.setAlignment(Qt.AlignCenter)
        self.preview_content.setStyleSheet("""
            QLabel {
                color: #666666;
                font-style: italic;
                padding: 40px;
                border: 2px dashed #cccccc;
                background-color: #f8f8f8;
                border-radius: 8px;
            }
        """)
        
        self.preview_scroll.setWidget(self.preview_content)
        preview_layout.addWidget(self.preview_scroll)
        
        self.content_tabs.addTab(self.preview_widget, "Preview")
    
    def _create_metadata_tab(self):
        """Create the metadata tab."""
        # Metadata container
        self.metadata_widget = QWidget()
        metadata_layout = QVBoxLayout(self.metadata_widget)
        metadata_layout.setContentsMargins(4, 4, 4, 4)
        
        # Metadata text area
        self.metadata_text = QTextEdit()
        self.metadata_text.setReadOnly(True)
        self.metadata_text.setPlainText("No metadata available")
        
        metadata_layout.addWidget(self.metadata_text)
        
        self.content_tabs.addTab(self.metadata_widget, "Metadata")
    
    def _create_properties_tab(self):
        """Create the properties tab."""
        # Properties container
        self.properties_widget = QWidget()
        properties_layout = QVBoxLayout(self.properties_widget)
        properties_layout.setContentsMargins(4, 4, 4, 4)
        
        # Properties text area
        self.properties_text = QTextEdit()
        self.properties_text.setReadOnly(True)
        self.properties_text.setPlainText("No properties available")
        
        properties_layout.addWidget(self.properties_text)
        
        self.content_tabs.addTab(self.properties_widget, "Properties")
    
    def _create_status_area(self, parent_layout: QVBoxLayout):
        """Create status area.
        
        Args:
            parent_layout: Parent layout
        """
        status_frame = QFrame()
        status_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        status_frame.setMaximumHeight(30)
        
        status_layout = QHBoxLayout(status_frame)
        status_layout.setContentsMargins(8, 4, 8, 4)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #333333;")
        
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        
        parent_layout.addWidget(status_frame)
    
    def _apply_styling(self):
        """Apply styling to the widget."""
        self.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background-color: white;
                border-radius: 4px;
            }
            
            QTabBar::tab {
                background-color: #e0e0e0;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                min-width: 80px;
            }
            
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #0078d4;
                color: #0078d4;
                font-weight: bold;
            }
            
            QTabBar::tab:hover {
                background-color: #f0f0f0;
            }
            
            QScrollArea {
                border: none;
                background-color: white;
            }
            
            QTextEdit {
                border: 1px solid #cccccc;
                background-color: white;
                font-family: 'Courier New', monospace;
                font-size: 10pt;
            }
        """)
    
    def _setup_accessibility(self):
        """Setup accessibility features."""
        # Set accessible names
        self.setAccessibleName("File Preview Pane")
        self.setAccessibleDescription("Displays preview and metadata for selected files")
        
        # Set tab accessible names
        self.content_tabs.setAccessibleName("Preview Content Tabs")
        self.preview_widget.setAccessibleName("File Preview")
        self.metadata_widget.setAccessibleName("File Metadata")
        self.properties_widget.setAccessibleName("File Properties")
        
        # Set keyboard focus policy
        self.setFocusPolicy(Qt.StrongFocus)
        self.content_tabs.setFocusPolicy(Qt.StrongFocus)
    
    def preview_file(self, file_path: str):
        """Preview a file.
        
        Args:
            file_path: Path to file to preview
        """
        if not file_path or file_path == self.current_file_path:
            return
        
        self.logger.debug(f"Previewing file: {file_path}")
        
        # Update current file
        self.current_file_path = file_path
        
        # Update header
        file_name = Path(file_path).name
        self.file_name_label.setText(file_name)
        
        # Show loading state
        self.status_label.setText("Loading preview...")
        self.preview_content.setText("Loading preview...")
        
        # Queue file for loading
        self.content_loader.queue_file_for_preview(file_path)
        
        # Emit signal
        self.previewRequested.emit(file_path)
    
    def _handle_content_loaded(self, file_path: str, content_data: Dict[str, Any]):
        """Handle content loaded from background thread.
        
        Args:
            file_path: File path
            content_data: Loaded content data
        """
        if file_path != self.current_file_path:
            return  # Ignore if not current file
        
        self.current_content_data = content_data
        
        # Update header
        file_size = content_data.get('file_size', 0)
        self.file_size_label.setText(self._format_file_size(file_size))
        
        # Update preview based on content type
        preview_type = content_data.get('preview_type', 'unsupported')
        
        if preview_type == 'text':
            self._display_text_preview(content_data)
        elif preview_type == 'image':
            self._display_image_preview(content_data)
        elif preview_type == 'pdf':
            self._display_pdf_preview(content_data)
        elif preview_type == 'audio':
            self._display_audio_preview(content_data)
        elif preview_type == 'video':
            self._display_video_preview(content_data)
        elif preview_type == 'error':
            self._display_error_preview(content_data)
        else:
            self._display_unsupported_preview(content_data)
        
        # Update metadata
        self._update_metadata_display(content_data)
        
        # Update properties
        self._update_properties_display(content_data)
        
        # Update status
        self.status_label.setText("Preview loaded")
        
        # Emit signal
        self.previewLoaded.emit(file_path, content_data)
    
    def _handle_loading_failed(self, file_path: str, error_message: str):
        """Handle loading failure.
        
        Args:
            file_path: File path
            error_message: Error message
        """
        if file_path != self.current_file_path:
            return
        
        self.logger.error(f"Failed to load preview for {file_path}: {error_message}")
        
        # Display error
        self.preview_content.setText(f"Failed to load preview:\n{error_message}")
        self.preview_content.setStyleSheet("""
            QLabel {
                color: #d32f2f;
                font-style: italic;
                padding: 40px;
                border: 2px dashed #d32f2f;
                background-color: #ffeaea;
                border-radius: 8px;
            }
        """)
        
        # Update status
        self.status_label.setText(f"Error: {error_message}")
        
        # Emit signal
        self.previewError.emit(file_path, error_message)
    
    def _handle_loading_progress(self, file_path: str, progress_percent: int):
        """Handle loading progress.
        
        Args:
            file_path: File path
            progress_percent: Progress percentage
        """
        if file_path != self.current_file_path:
            return
        
        self.status_label.setText(f"Loading preview... {progress_percent}%")
    
    def _display_text_preview(self, content_data: Dict[str, Any]):
        """Display text file preview.
        
        Args:
            content_data: Content data
        """
        content = content_data.get('content', '')
        
        # Create text edit for better text display
        if not isinstance(self.preview_content, QTextEdit):
            self.preview_content.deleteLater()
            self.preview_content = QTextEdit()
            self.preview_content.setReadOnly(True)
            self.preview_scroll.setWidget(self.preview_content)
        
        self.preview_content.setPlainText(content)
        
        # Truncation warning
        metadata = content_data.get('metadata', {})
        if metadata.get('truncated', False):
            self.status_label.setText("Preview truncated (showing first 64KB)")
    
    def _display_image_preview(self, content_data: Dict[str, Any]):
        """Display image preview.
        
        Args:
            content_data: Content data
        """
        pixmap = content_data.get('content')
        
        if isinstance(pixmap, QPixmap) and not pixmap.isNull():
            # Create label for image display
            if not isinstance(self.preview_content, QLabel):
                self.preview_content.deleteLater()
                self.preview_content = QLabel()
                self.preview_content.setAlignment(Qt.AlignCenter)
                self.preview_scroll.setWidget(self.preview_content)
            
            self.preview_content.setPixmap(pixmap)
            self.preview_content.setStyleSheet("border: none; background-color: white;")
            
            # Update status with image info
            metadata = content_data.get('metadata', {})
            width = metadata.get('width', 0)
            height = metadata.get('height', 0)
            self.status_label.setText(f"Image: {width}x{height} pixels")
        else:
            self._display_error_preview({'error': 'Failed to load image'})
    
    def _display_pdf_preview(self, content_data: Dict[str, Any]):
        """Display PDF preview.
        
        Args:
            content_data: Content data
        """
        # For now, just show PDF info
        self._display_info_preview("PDF Document", content_data)
    
    def _display_audio_preview(self, content_data: Dict[str, Any]):
        """Display audio file preview.
        
        Args:
            content_data: Content data
        """
        self._display_info_preview("Audio File", content_data)
    
    def _display_video_preview(self, content_data: Dict[str, Any]):
        """Display video file preview.
        
        Args:
            content_data: Content data
        """
        self._display_info_preview("Video File", content_data)
    
    def _display_info_preview(self, file_type: str, content_data: Dict[str, Any]):
        """Display info-based preview.
        
        Args:
            file_type: Type of file
            content_data: Content data
        """
        # Create label for info display
        if not isinstance(self.preview_content, QLabel):
            self.preview_content.deleteLater()
            self.preview_content = QLabel()
            self.preview_content.setAlignment(Qt.AlignCenter)
            self.preview_scroll.setWidget(self.preview_content)
        
        file_name = content_data.get('file_name', 'Unknown')
        mime_type = content_data.get('mime_type', 'Unknown')
        
        info_text = f"""
        <div style="text-align: center; font-family: Arial, sans-serif;">
            <h2 style="color: #333333; margin-bottom: 20px;">{file_type}</h2>
            <p style="color: #666666; font-size: 14px; margin: 10px;">
                <strong>File:</strong> {file_name}
            </p>
            <p style="color: #666666; font-size: 14px; margin: 10px;">
                <strong>Type:</strong> {mime_type}
            </p>
            <p style="color: #999999; font-size: 12px; margin-top: 20px;">
                Preview not available for this file type
            </p>
        </div>
        """
        
        self.preview_content.setText(info_text)
        self.preview_content.setStyleSheet("""
            QLabel {
                color: #333333;
                padding: 40px;
                border: 1px solid #cccccc;
                background-color: white;
                border-radius: 8px;
            }
        """)
    
    def _display_error_preview(self, content_data: Dict[str, Any]):
        """Display error preview.
        
        Args:
            content_data: Content data with error
        """
        # Create label for error display
        if not isinstance(self.preview_content, QLabel):
            self.preview_content.deleteLater()
            self.preview_content = QLabel()
            self.preview_content.setAlignment(Qt.AlignCenter)
            self.preview_scroll.setWidget(self.preview_content)
        
        error = content_data.get('error', 'Unknown error')
        self.preview_content.setText(f"Preview Error:\n{error}")
        self.preview_content.setStyleSheet("""
            QLabel {
                color: #d32f2f;
                padding: 40px;
                border: 2px dashed #d32f2f;
                background-color: #ffeaea;
                border-radius: 8px;
            }
        """)
    
    def _display_unsupported_preview(self, content_data: Dict[str, Any]):
        """Display unsupported file preview.
        
        Args:
            content_data: Content data
        """
        self._display_info_preview("Unsupported File Type", content_data)
    
    def _update_metadata_display(self, content_data: Dict[str, Any]):
        """Update metadata display.
        
        Args:
            content_data: Content data
        """
        metadata = content_data.get('metadata', {})
        
        metadata_text = "File Metadata:\n\n"
        
        # Basic file info
        metadata_text += f"File Name: {content_data.get('file_name', 'Unknown')}\n"
        metadata_text += f"File Size: {self._format_file_size(content_data.get('file_size', 0))}\n"
        metadata_text += f"MIME Type: {content_data.get('mime_type', 'Unknown')}\n"
        metadata_text += f"Modified: {self._format_timestamp(content_data.get('modified_time', 0))}\n"
        
        # Type-specific metadata
        if metadata:
            metadata_text += "\nType-specific Metadata:\n"
            for key, value in metadata.items():
                metadata_text += f"{key.replace('_', ' ').title()}: {value}\n"
        
        self.metadata_text.setPlainText(metadata_text)
    
    def _update_properties_display(self, content_data: Dict[str, Any]):
        """Update properties display.
        
        Args:
            content_data: Content data
        """
        properties_text = "File Properties:\n\n"
        
        # All available properties
        for key, value in content_data.items():
            if key not in ['content']:  # Skip binary content
                properties_text += f"{key.replace('_', ' ').title()}: {value}\n"
        
        self.properties_text.setPlainText(properties_text)
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format.
        
        Args:
            size_bytes: Size in bytes
            
        Returns:
            Formatted size string
        """
        if size_bytes == 0:
            return "0 B"
        
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        unit_index = 0
        size = float(size_bytes)
        
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
        
        return f"{size:.1f} {units[unit_index]}"
    
    def _format_timestamp(self, timestamp: float) -> str:
        """Format timestamp in readable format.
        
        Args:
            timestamp: Unix timestamp
            
        Returns:
            Formatted timestamp string
        """
        if timestamp == 0:
            return "Unknown"
        
        from datetime import datetime
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    
    def clear_preview(self):
        """Clear the current preview."""
        self.current_file_path = ""
        self.current_content_data.clear()
        
        # Reset UI
        self.file_name_label.setText("No file selected")
        self.file_size_label.setText("")
        
        # Reset preview content
        if not isinstance(self.preview_content, QLabel):
            self.preview_content.deleteLater()
            self.preview_content = QLabel("Select a file to preview")
            self.preview_content.setAlignment(Qt.AlignCenter)
            self.preview_scroll.setWidget(self.preview_content)
        
        self.preview_content.setText("Select a file to preview")
        self.preview_content.setStyleSheet("""
            QLabel {
                color: #666666;
                font-style: italic;
                padding: 40px;
                border: 2px dashed #cccccc;
                background-color: #f8f8f8;
                border-radius: 8px;
            }
        """)
        
        # Clear metadata and properties
        self.metadata_text.setPlainText("No metadata available")
        self.properties_text.setPlainText("No properties available")
        
        # Reset status
        self.status_label.setText("Ready")
    
    def get_current_file_path(self) -> str:
        """Get current file path.
        
        Returns:
            Current file path
        """
        return self.current_file_path
    
    def get_current_content_data(self) -> Dict[str, Any]:
        """Get current content data.
        
        Returns:
            Current content data
        """
        return self.current_content_data.copy()
    
    def closeEvent(self, event):
        """Handle widget close event."""
        self.logger.info("Preview Pane Widget closing")
        
        # Stop content loader
        if hasattr(self, 'content_loader'):
            self.content_loader.stop()
        
        event.accept()