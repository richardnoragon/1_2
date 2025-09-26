"""
Enhanced PDF Tools Hub
A comprehensive, modern interface for all PDF utility tools with dynamic
discovery, categorized sections, progress tracking, and unified error handling.
"""

import os
import sys
from typing import Dict, List, Optional, Any
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QScrollArea, QGridLayout, QLabel, QPushButton,
    QProgressBar, QStatusBar, QMessageBox, QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QIcon, QColor, QPixmap, QPainter, QBrush

from pdf_tool_discovery import get_tool_discovery, ToolMetadata
from config_manager import ConfigManager
from log_config import setup_logger

logger = setup_logger(__name__)


class ModernButton(QPushButton):
    """A modern, styled button with hover effects and animations."""
    
    def __init__(self, text: str, icon_path: Optional[str] = None,
                 primary: bool = True, parent=None):
        super().__init__(text, parent)
        self.primary = primary
        self.icon_path = icon_path
        self._setup_style()
    
    def _setup_style(self):
        """Setup the button styling."""
        self.setMinimumHeight(45)
        self.setMinimumWidth(120)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        if self.primary:
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #4a90e2, stop:1 #357abd);
                    border: 1px solid #2c5aa0;
                    border-radius: 8px;
                    color: white;
                    font-weight: bold;
                    font-size: 11pt;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #5ba0f2, stop:1 #4682cd);
                    border: 1px solid #3d6bb0;
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #357abd, stop:1 #2c5aa0);
                }
                QPushButton:disabled {
                    background: #cccccc;
                    color: #666666;
                    border: 1px solid #999999;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #f8f9fa, stop:1 #e9ecef);
                    border: 1px solid #ced4da;
                    border-radius: 8px;
                    color: #495057;
                    font-size: 11pt;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #ffffff, stop:1 #f1f3f4);
                    border: 1px solid #adb5bd;
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #e9ecef, stop:1 #dee2e6);
                }
            """)
        
        if self.icon_path and os.path.exists(self.icon_path):
            self.setIcon(QIcon(self.icon_path))
            self.setIconSize(QSize(20, 20))


class ToolCard(QFrame):
    """A card widget representing a PDF tool with metadata and actions."""
    
    tool_launched = pyqtSignal(str)  # tool_name
    
    def __init__(self, tool_metadata: ToolMetadata, parent=None):
        super().__init__(parent)
        self.tool_metadata = tool_metadata
        self.is_running = False
        self._setup_ui()
        self._setup_style()
    
    def _setup_ui(self):
        """Setup the card UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        # Header with tool name and status
        header_layout = QHBoxLayout()
        
        # Tool name
        self.name_label = QLabel(self.tool_metadata.name)
        self.name_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.name_label.setStyleSheet("color: #2c3e50;")
        header_layout.addWidget(self.name_label)
        
        # Status indicator
        self.status_indicator = QLabel("●")
        self.status_indicator.setFont(QFont("Arial", 16))
        self.status_indicator.setStyleSheet("color: #27ae60;")  # Green
        self.status_indicator.setToolTip("Tool available")
        header_layout.addWidget(self.status_indicator)
        
        layout.addLayout(header_layout)
        
        # Description
        self.description_label = QLabel(self.tool_metadata.description)
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet("""
            color: #7f8c8d;
            font-size: 10pt;
            line-height: 1.4;
        """)
        layout.addWidget(self.description_label)
        
        # Features row
        features_layout = QHBoxLayout()
        
        # Batch support indicator
        if self.tool_metadata.supports_batch:
            batch_label = QLabel("📦 Batch")
            batch_label.setToolTip("Supports batch processing")
            batch_label.setStyleSheet("color: #3498db; font-size: 9pt;")
            features_layout.addWidget(batch_label)
        
        # Preview support indicator
        if self.tool_metadata.has_preview:
            preview_label = QLabel("👁 Preview")
            preview_label.setToolTip("Supports preview")
            preview_label.setStyleSheet("color: #9b59b6; font-size: 9pt;")
            features_layout.addWidget(preview_label)
        
        # Output formats
        if self.tool_metadata.output_formats:
            formats_text = ", ".join(self.tool_metadata.output_formats[:3])
            if len(self.tool_metadata.output_formats) > 3:
                formats_text += "..."
            formats_label = QLabel(f"→ {formats_text}")
            output_formats_str = ", ".join(self.tool_metadata.output_formats)
            formats_label.setToolTip(f"Output formats: {output_formats_str}")
            formats_label.setStyleSheet("color: #e67e22; font-size: 9pt;")
            features_layout.addWidget(formats_label)
        
        features_layout.addStretch()
        layout.addLayout(features_layout)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.launch_button = ModernButton("Launch", primary=True)
        self.launch_button.clicked.connect(self._launch_tool)
        button_layout.addWidget(self.launch_button)
        
        self.info_button = ModernButton("Info", primary=False)
        self.info_button.clicked.connect(self._show_info)
        button_layout.addWidget(self.info_button)
        
        layout.addLayout(button_layout)
        
        # Progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                text-align: center;
                font-size: 9pt;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3498db, stop:1 #2980b9);
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress_bar)
    
    def _setup_style(self):
        """Setup the card styling."""
        self.setFrameStyle(QFrame.Box)
        self.setStyleSheet("""
            ToolCard {
                background-color: white;
                border: 1px solid #e1e8ed;
                border-radius: 12px;
                margin: 4px;
            }
            ToolCard:hover {
                border: 1px solid #3498db;
                box-shadow: 0 2px 8px rgba(52, 152, 219, 0.2);
            }
        """)
        self.setMinimumHeight(160)
        self.setMaximumHeight(200)
    
    def _launch_tool(self):
        """Launch the PDF tool."""
        try:
            logger.info(f"Launching tool: {self.tool_metadata.name}")
            self.tool_launched.emit(self.tool_metadata.name)
            self.set_running_state(True)
        except Exception as e:
            logger.error(f"Failed to launch {self.tool_metadata.name}: {e}")
            QMessageBox.critical(
                self, "Launch Error",
                f"Failed to launch {self.tool_metadata.name}:\n{str(e)}"
            )
    
    def _show_info(self):
        """Show detailed tool information."""
        info_dialog = ToolInfoDialog(self.tool_metadata, self)
        info_dialog.exec_()
    
    def set_running_state(self, running: bool):
        """Set the running state of the tool."""
        self.is_running = running
        if running:
            self.status_indicator.setStyleSheet("color: #f39c12;")  # Orange
            self.status_indicator.setToolTip("Tool running")
            self.launch_button.setText("Running...")
            self.launch_button.setEnabled(False)
        else:
            self.status_indicator.setStyleSheet("color: #27ae60;")  # Green
            self.status_indicator.setToolTip("Tool available")
            self.launch_button.setText("Launch")
            self.launch_button.setEnabled(True)
    
    def show_progress(self, value: int, message: str = ""):
        """Show progress for the tool operation."""
        self.progress_bar.setValue(value)
        if message:
            self.progress_bar.setFormat(f"{message} - %p%")
        else:
            self.progress_bar.setFormat("%p%")
        
        if not self.progress_bar.isVisible():
            self.progress_bar.setVisible(True)
        
        if value >= 100:
            QTimer.singleShot(2000, self.hide_progress)
    
    def hide_progress(self):
        """Hide the progress bar."""
        self.progress_bar.setVisible(False)
        self.set_running_state(False)


class ToolInfoDialog(QMessageBox):
    """Dialog showing detailed information about a PDF tool."""
    
    def __init__(self, tool_metadata: ToolMetadata, parent=None):
        super().__init__(parent)
        self.tool_metadata = tool_metadata
        self._setup_dialog()
    
    def _setup_dialog(self):
        """Setup the information dialog."""
        self.setWindowTitle(f"Tool Information - {self.tool_metadata.name}")
        self.setIcon(QMessageBox.Information)
        
        batch_support = ('Yes' if self.tool_metadata.supports_batch
                         else 'No')
        preview_support = ('Yes' if self.tool_metadata.has_preview
                           else 'No')
        output_formats = (', '.join(self.tool_metadata.output_formats)
                          if self.tool_metadata.output_formats else 'N/A')
        dependencies = (', '.join(self.tool_metadata.dependencies)
                        if self.tool_metadata.dependencies else 'None')
        
        info_text = f"""
<h3>{self.tool_metadata.name}</h3>
<p><b>Description:</b> {self.tool_metadata.description}</p>
<p><b>Category:</b> {self.tool_metadata.category.replace('_', ' ').title()}</p>
<p><b>Module:</b> {self.tool_metadata.module_name}</p>
<p><b>Class:</b> {self.tool_metadata.class_name}</p>

<h4>Features:</h4>
<ul>
<li>Batch Processing: {batch_support}</li>
<li>Preview Support: {preview_support}</li>
</ul>

<h4>Supported Formats:</h4>
<p><b>Input:</b> {', '.join(self.tool_metadata.input_formats)}</p>
<p><b>Output:</b> {output_formats}</p>

<h4>Dependencies:</h4>
<p>{dependencies}</p>

<h4>File Location:</h4>
<p><small>{self.tool_metadata.file_path}</small></p>
        """
        
        self.setText(info_text)
        self.setStandardButtons(QMessageBox.Ok)


class CategoryTab(QWidget):
    """A tab widget containing tools for a specific category."""
    
    tool_launched = pyqtSignal(str)  # tool_name
    
    def __init__(self, category_id: str, category_info: Dict[str, Any],
                 tools: List[ToolMetadata], parent=None):
        super().__init__(parent)
        self.category_id = category_id
        self.category_info = category_info
        self.tools = tools
        self.tool_cards: Dict[str, ToolCard] = {}
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the category tab UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Category header
        header_layout = QHBoxLayout()
        
        title_label = QLabel(self.category_info['name'])
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50;")
        header_layout.addWidget(title_label)
        
        # Tool count
        count_label = QLabel(f"({len(self.tools)} tools)")
        count_label.setStyleSheet("color: #7f8c8d; font-size: 12pt;")
        header_layout.addWidget(count_label)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Category description
        desc_label = QLabel(self.category_info['description'])
        desc_label.setStyleSheet(
            "color: #7f8c8d; font-size: 11pt; margin-bottom: 8px;"
        )
        layout.addWidget(desc_label)
        
        # Scroll area for tool cards
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #f8f9fa;
            }
            QScrollBar:vertical {
                background-color: #e9ecef;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #ced4da;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #adb5bd;
            }
        """)
        
        # Container for tool cards
        cards_widget = QWidget()
        cards_layout = QGridLayout(cards_widget)
        cards_layout.setSpacing(12)
        cards_layout.setContentsMargins(8, 8, 8, 8)
        
        # Add tool cards in a grid
        row, col = 0, 0
        max_cols = 3
        
        for tool in self.tools:
            card = ToolCard(tool)
            card.tool_launched.connect(self.tool_launched.emit)
            self.tool_cards[tool.name] = card
            
            cards_layout.addWidget(card, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        # Add stretch to fill remaining space
        cards_layout.setRowStretch(row + 1, 1)
        cards_layout.setColumnStretch(max_cols, 1)
        
        scroll_area.setWidget(cards_widget)
        layout.addWidget(scroll_area)
    
    def get_tool_card(self, tool_name: str) -> Optional[ToolCard]:
        """Get a tool card by name."""
        return self.tool_cards.get(tool_name)
    
    def update_tool_progress(self, tool_name: str, progress: int,
                             message: str = ""):
        """Update progress for a specific tool."""
        card = self.get_tool_card(tool_name)
        if card:
            card.show_progress(progress, message)


class EnhancedPDFHub(QMainWindow):
    """
    Enhanced PDF Tools Hub with dynamic discovery, categorized interface,
    and modern UI design.
    """
    
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.tool_discovery = get_tool_discovery()
        self.discovered_tools: Dict[str, ToolMetadata] = {}
        self.category_tabs: Dict[str, CategoryTab] = {}
        self.running_tools: Dict[str, Any] = {}
        
        self._setup_ui()
        self._discover_tools()
        self._setup_connections()
        
        logger.info("Enhanced PDF Hub initialized successfully")
    
    def _setup_ui(self):
        """Setup the main UI."""
        self.setWindowTitle("PDF Tools Hub - Comprehensive PDF Utilities")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)
        
        # Set application icon
        self.setWindowIcon(self._create_app_icon())
        
        # Apply modern styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
            QTabWidget::pane {
                border: 1px solid #dee2e6;
                background-color: white;
                border-radius: 8px;
            }
            QTabWidget::tab-bar {
                alignment: center;
            }
            QTabBar::tab {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
                border: 1px solid #dee2e6;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                min-width: 120px;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom: 1px solid white;
            }
            QTabBar::tab:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f1f3f4);
            }
        """)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)
        
        # Header
        self._create_header(main_layout)
        
        # Main content area
        self._create_main_content(main_layout)
        
        # Status bar
        self._create_status_bar()
    
    def _create_app_icon(self) -> QIcon:
        """Create application icon."""
        # Create a simple PDF icon
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor(0, 0, 0, 0))  # Transparent
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw PDF icon
        painter.setBrush(QBrush(QColor("#e74c3c")))
        painter.setPen(QColor("#c0392b"))
        painter.drawRoundedRect(4, 4, 24, 24, 4, 4)
        
        painter.setPen(QColor("white"))
        painter.setFont(QFont("Arial", 8, QFont.Bold))
        painter.drawText(8, 20, "PDF")
        
        painter.end()
        
        return QIcon(pixmap)
    
    def _create_header(self, layout: QVBoxLayout):
        """Create the header section."""
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2980b9);
                border-radius: 12px;
                padding: 16px;
            }
        """)
        header_frame.setFixedHeight(80)
        
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 16, 20, 16)
        
        # Title and subtitle
        title_layout = QVBoxLayout()
        
        title_label = QLabel("PDF Tools Hub")
        title_label.setFont(QFont("Arial", 20, QFont.Bold))
        title_label.setStyleSheet("color: white;")
        title_layout.addWidget(title_label)
        
        subtitle_label = QLabel(
            "Comprehensive PDF utilities with dynamic discovery"
        )
        subtitle_label.setFont(QFont("Arial", 11))
        subtitle_label.setStyleSheet("color: #ecf0f1;")
        title_layout.addWidget(subtitle_label)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        # Header buttons
        self.refresh_button = ModernButton("🔄 Refresh", primary=False)
        self.refresh_button.clicked.connect(self._refresh_tools)
        header_layout.addWidget(self.refresh_button)
        
        self.settings_button = ModernButton("⚙️ Settings", primary=False)
        self.settings_button.clicked.connect(self._open_settings)
        header_layout.addWidget(self.settings_button)
        
        layout.addWidget(header_frame)
    
    def _create_main_content(self, layout: QVBoxLayout):
        """Create the main content area with tabs."""
        # Tab widget for categories
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)
        self.tab_widget.setMovable(False)
        
        layout.addWidget(self.tab_widget)
    
    def _create_status_bar(self):
        """Create the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Status message
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)
        
        # Progress bar for global operations
        self.global_progress = QProgressBar()
        self.global_progress.setVisible(False)
        self.global_progress.setMaximumWidth(200)
        self.status_bar.addPermanentWidget(self.global_progress)
        
        # Tool count
        self.tool_count_label = QLabel("0 tools discovered")
        self.status_bar.addPermanentWidget(self.tool_count_label)
    
    def _discover_tools(self):
        """Discover and organize PDF tools."""
        try:
            self.status_label.setText("Discovering PDF tools...")
            self.global_progress.setVisible(True)
            self.global_progress.setRange(0, 0)  # Indeterminate
            
            # Discover tools
            self.discovered_tools = self.tool_discovery.discover_tools()
            categories = self.tool_discovery.get_all_categories()
            
            # Clear existing tabs
            self.tab_widget.clear()
            self.category_tabs.clear()
            
            # Create tabs for each category with tools
            for category_id, category_info in categories.items():
                tools = self.tool_discovery.get_tools_by_category(category_id)
                if tools:  # Only create tab if there are tools
                    tab = CategoryTab(category_id, category_info, tools)
                    tab.tool_launched.connect(self._launch_tool)
                    
                    self.category_tabs[category_id] = tab
                    self.tab_widget.addTab(tab, category_info['name'])
            
            # Update status
            tool_count = len(self.discovered_tools)
            self.tool_count_label.setText(f"{tool_count} tools discovered")
            self.status_label.setText(f"Discovered {tool_count} PDF tools")
            
            self.global_progress.setVisible(False)
            
            logger.info(f"Successfully discovered {tool_count} PDF tools")
            
        except Exception as e:
            logger.error(f"Error discovering tools: {e}", exc_info=True)
            self.status_label.setText("Error discovering tools")
            self.global_progress.setVisible(False)
            QMessageBox.critical(
                self, "Discovery Error",
                f"Failed to discover PDF tools:\n{str(e)}"
            )
    
    def _setup_connections(self):
        """Setup signal connections."""
        # Timer for periodic tool discovery refresh
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self._refresh_tools)
        # Refresh every 5 minutes
        self.refresh_timer.start(300000)
    
    def _launch_tool(self, tool_name: str):
        """Launch a PDF tool."""
        try:
            tool_metadata = self.discovered_tools.get(tool_name)
            if not tool_metadata:
                raise ValueError(f"Tool '{tool_name}' not found")
            
            logger.info(f"Launching tool: {tool_name}")
            self.status_label.setText(f"Launching {tool_name}...")
            
            # Import and instantiate the tool
            module_name = tool_metadata.module_name
            class_name = tool_metadata.class_name
            
            # Dynamic import
            module = __import__(module_name)
            tool_class = getattr(module, class_name)
            
            # Create and show the tool window
            tool_instance = tool_class()
            tool_instance.show()
            
            # Track running tool
            self.running_tools[tool_name] = tool_instance
            
            self.status_label.setText(f"{tool_name} launched successfully")
            
            # Update tool card status
            for tab in self.category_tabs.values():
                card = tab.get_tool_card(tool_name)
                if card:
                    card.set_running_state(True)
                    break
            
        except Exception as e:
            logger.error(f"Failed to launch {tool_name}: {e}", exc_info=True)
            self.status_label.setText(f"Failed to launch {tool_name}")
            QMessageBox.critical(
                self, "Launch Error",
                f"Failed to launch {tool_name}:\n{str(e)}"
            )
    
    def _refresh_tools(self):
        """Refresh the tool discovery."""
        logger.info("Refreshing tool discovery...")
        self._discover_tools()
    
    def _open_settings(self):
        """Open the settings manager."""
        try:
            from settings_manager import SettingsManagerUI
            if not hasattr(self, 'settings_window'):
                self.settings_window = SettingsManagerUI()
            self.settings_window.show()
            self.settings_window.raise_()
        except ImportError as e:
            logger.error(f"Failed to import settings manager: {e}")
            QMessageBox.warning(
                self, "Settings",
                "Settings manager is not available."
            )
    
    def closeEvent(self, event):
        """Handle application close event."""
        # Close all running tools
        for tool_name, tool_instance in self.running_tools.items():
            try:
                if hasattr(tool_instance, 'close'):
                    tool_instance.close()
            except Exception as e:
                logger.warning(f"Error closing {tool_name}: {e}")
        
        # Stop refresh timer
        if hasattr(self, 'refresh_timer'):
            self.refresh_timer.stop()
        
        logger.info("Enhanced PDF Hub closing")
        super().closeEvent(event)


def main():
    """Main function to run the Enhanced PDF Hub."""
    try:
        app = QApplication(sys.argv)
        app.setApplicationName("PDF Tools Hub")
        app.setApplicationVersion("2.0")
        app.setOrganizationName("Richard's File Utilities")
        
        # Set application style
        app.setStyle('Fusion')
        
        # Create and show the main window
        window = EnhancedPDFHub()
        window.show()
        
        logger.info("Enhanced PDF Hub started successfully")
        
        return app.exec_()
        
    except Exception as e:
        logger.critical(
            f"Failed to start Enhanced PDF Hub: {e}", exc_info=True
        )
        if 'app' in locals():
            QMessageBox.critical(
                None, "Startup Error",
                f"Failed to start PDF Tools Hub:\n{str(e)}"
            )
        return 1


if __name__ == '__main__':
    sys.exit(main())