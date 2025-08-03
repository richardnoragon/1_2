from PyQt5.QtWidgets import (
    QApplication, QWidget, QMainWindow, QPushButton, QVBoxLayout, QLabel,
    QSizePolicy, QSpacerItem, QHBoxLayout, QGridLayout, QTabWidget,
    QStatusBar, QProgressBar, QTextEdit
)
from PyQt5.QtGui import QIcon, QFont, QColor
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QTimer
import sys
import subprocess
import os
import shutil
from datetime import datetime
from typing import Optional, List, Dict, Any
from .log_manager import LogManager
from .gui.common.base_window import BaseWindow
from .gui.themes import ThemeManager, Colors, Fonts
from .core import error_handler
from ..legacy.file_utilities_1.catalog import CatalogWindow



class StyledButton(QPushButton):
    """A standardized button class with consistent styling."""
    
    def __init__(
        self, 
        text: str, 
        icon_name: Optional[str] = None, 
        primary: bool = True
    ) -> None:
        super().__init__(text)
        self.setMinimumHeight(50)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        if primary:
            ThemeManager.style_primary_button(self)
        else:
            ThemeManager.style_secondary_button(self)
        
        if icon_name:
            icon_path = self._get_icon_path(icon_name)
            if os.path.exists(icon_path):
                self.setIcon(QIcon(icon_path))
                self.setIconSize(QSize(24, 24))
    
    def _get_icon_path(self, icon_name: str) -> str:
        """Get icon path from icon name."""
        icons_dir = os.path.join(os.path.dirname(__file__), 'icons')
        return os.path.join(icons_dir, f"{icon_name}.png")


class StandardUtilityWindow(QMainWindow):
    """Standardized window for utility applications."""
    
    def __init__(self, title: str, width: int = 500, height: int = 400) -> None:
        super().__init__()
        self.setWindowTitle(title)
        self.setMinimumSize(400, 300)
        self.resize(width, height)
        
        # Apply theme
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {Colors.WINDOW_BACKGROUND};
                color: {Colors.TEXT_PRIMARY};
            }}
        """)
        
        # Create central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)
        self.central_widget.setLayout(self.main_layout)
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def create_header(self, text: str) -> QLabel:
        """Create a standardized header."""
        header = QLabel(text)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = Fonts.get_font(Fonts.HEADER_SIZE, Fonts.BOLD)
        header.setFont(font)
        header.setStyleSheet(f"color: {Colors.PRIMARY};")
        return header
    
    def create_button_row(self, buttons: List[QPushButton]) -> QHBoxLayout:
        """Create a standardized button row."""
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        for button in buttons:
            button_layout.addWidget(button)
        
        return button_layout
    
    def show_status_message(self, message: str, timeout: int = 3000) -> None:
        """Show status message."""
        self.status_bar.showMessage(message, timeout)


class RenameWindow(StandardUtilityWindow):
    """Standardized rename window."""
    
    def __init__(self) -> None:
        super().__init__("File Rename Utility", 500, 400)
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Setup the user interface."""
        # Header
        header = self.create_header("File Rename Utility")
        self.main_layout.addWidget(header)
        
        # Buttons
        select_btn = StyledButton("Select Files", primary=True)
        rename_btn = StyledButton("Rename Files", primary=False)
        
        button_row = self.create_button_row([select_btn, rename_btn])
        self.main_layout.addLayout(button_row)
        
        # Connect signals
        select_btn.clicked.connect(self.select_files)
        rename_btn.clicked.connect(self.rename_files)
    
    def select_files(self) -> None:
        """Handle file selection."""
        self.show_status_message("Select files to rename...")
    
    def rename_files(self) -> None:
        """Handle file renaming."""
        self.show_status_message("Renaming files...")


class CopyMoveSyncDeleteWindow(StandardUtilityWindow):
    """Standardized copy/move/sync/delete window."""
    
    def __init__(self) -> None:
        super().__init__("File Operations Utility", 600, 500)
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Setup the user interface."""
        # Header
        header = self.create_header("File Operations Utility")
        self.main_layout.addWidget(header)
        
        # Operation buttons
        copy_btn = StyledButton("Copy Files", primary=True)
        move_btn = StyledButton("Move Files", primary=True)
        sync_btn = StyledButton("Sync Directories", primary=True)
        delete_btn = StyledButton("Delete Files", primary=False)
        
        # Create grid layout for operations
        grid_layout = QGridLayout()
        grid_layout.setSpacing(10)
        grid_layout.addWidget(copy_btn, 0, 0)
        grid_layout.addWidget(move_btn, 0, 1)
        grid_layout.addWidget(sync_btn, 1, 0)
        grid_layout.addWidget(delete_btn, 1, 1)
        
        self.main_layout.addLayout(grid_layout)
        
        # Connect signals
        copy_btn.clicked.connect(self.copy_files)
        move_btn.clicked.connect(self.move_files)
        sync_btn.clicked.connect(self.sync_directories)
        delete_btn.clicked.connect(self.delete_files)
    
    def copy_files(self) -> None:
        """Handle file copying."""
        self.show_status_message("Copying files...")
    
    def move_files(self) -> None:
        """Handle file moving."""
        self.show_status_message("Moving files...")
    
    def sync_directories(self) -> None:
        """Handle directory synchronization."""
        self.show_status_message("Synchronizing directories...")
    
    def delete_files(self) -> None:
        """Handle file deletion."""
        self.show_status_message("Deleting files...")


class OrganizeWindow(StandardUtilityWindow):
    """Standardized organize window."""
    
    def __init__(self) -> None:
        super().__init__("File Organization Utility", 600, 450)
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Setup the user interface."""
        # Header
        header = self.create_header("File Organization Utility")
        self.main_layout.addWidget(header)
        
        # Buttons
        organize_btn = StyledButton("Organize Files", primary=True)
        rules_btn = StyledButton("Manage Rules", primary=False)
        
        button_row = self.create_button_row([organize_btn, rules_btn])
        self.main_layout.addLayout(button_row)
        
        # Connect signals
        organize_btn.clicked.connect(self.organize_files)
        rules_btn.clicked.connect(self.manage_rules)
    
    def organize_files(self) -> None:
        """Handle file organization."""
        self.show_status_message("Organizing files...")
    
    def manage_rules(self) -> None:
        """Handle rule management."""
        self.show_status_message("Managing organization rules...")


class MyGUI(BaseWindow):
    """Updated main GUI with standardized styling and hub integration."""
    
    # Hub integration signals
    tool_registered = pyqtSignal(str, object)       # tool_name, tool_instance
    tool_unregistered = pyqtSignal(str)             # tool_name
    tool_progress_updated = pyqtSignal(str, int, str)  # tool_name, percentage, message
    tool_status_changed = pyqtSignal(str, str)      # tool_name, status
    hub_event_broadcast = pyqtSignal(str, str, dict)  # sender, event_type, data
    
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Richard's File Utilities Hub")
        self.setMinimumSize(800, 600)
        self.resize(900, 700)
        
        # Hub integration components
        self.registered_tools = {}  # tool_name -> tool_instance
        self.tool_status = {}       # tool_name -> status_info
        self.message_queue = []     # Hub message queue
        self.resource_manager = {   # Resource management
            'cpu': {'available': True, 'allocated_to': None},
            'memory': {'available': True, 'allocated_to': None},
            'disk': {'available': True, 'allocated_to': None}
        }
        
        # Apply standard theme
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {Colors.WINDOW_BACKGROUND};
                color: {Colors.TEXT_PRIMARY};
            }}
        """)
        
        self._setup_ui()
        self._setup_hub_integration()
    
    def _setup_hub_integration(self):
        """Setup hub integration components."""
        # Connect internal signals
        self.tool_registered.connect(self._on_tool_registered)
        self.tool_unregistered.connect(self._on_tool_unregistered)
        self.tool_progress_updated.connect(self._on_tool_progress_updated)
        self.tool_status_changed.connect(self._on_tool_status_changed)
        self.hub_event_broadcast.connect(self._on_hub_event_broadcast)
    
    def register_tool(self, tool_name: str, tool_instance) -> bool:
        """Register a tool with the hub."""
        try:
            if tool_name in self.registered_tools:
                # Tool already registered, update instance
                self.registered_tools[tool_name] = tool_instance
            else:
                self.registered_tools[tool_name] = tool_instance
                self.tool_status[tool_name] = {
                    'status': 'registered',
                    'last_activity': datetime.now(),
                    'progress': 0,
                    'current_operation': None
                }
            
            self.tool_registered.emit(tool_name, tool_instance)
            self._update_status_bar(f"Tool registered: {tool_name}")
            return True
            
        except Exception as e:
            self._update_status_bar(f"Failed to register tool {tool_name}: {e}")
            return False
    
    def unregister_tool(self, tool_name: str) -> bool:
        """Unregister a tool from the hub."""
        try:
            if tool_name in self.registered_tools:
                del self.registered_tools[tool_name]
                if tool_name in self.tool_status:
                    del self.tool_status[tool_name]
                
                # Release any resources allocated to this tool
                self._release_tool_resources(tool_name)
                
                self.tool_unregistered.emit(tool_name)
                self._update_status_bar(f"Tool unregistered: {tool_name}")
                return True
            return False
            
        except Exception as e:
            self._update_status_bar(f"Failed to unregister tool {tool_name}: {e}")
            return False
    
    def receive_message(self, message):
        """Receive message from a tool."""
        try:
            # Process hub message
            tool_name = message.tool_name
            message_type = message.message_type
            data = message.data
            
            if message_type == "tool_progress":
                percentage = data.get('percentage', 0)
                msg = data.get('message', '')
                self.update_tool_progress(tool_name, percentage, msg)
                
            elif message_type == "tool_status":
                status = data.get('status', 'unknown')
                self.update_tool_status(tool_name, status, data.get('details', {}))
                
            elif message_type == "tool_error":
                error_msg = data.get('error_message', 'Unknown error')
                self._handle_tool_error(tool_name, error_msg, data)
                
            elif message_type == "tool_heartbeat":
                self._update_tool_heartbeat(tool_name, data)
            
            # Add message to queue for processing
            self.message_queue.append(message)
            
        except Exception as e:
            self._update_status_bar(f"Error processing message: {e}")
    
    def update_tool_progress(self, tool_name: str, percentage: int, message: str = ""):
        """Update tool progress in hub."""
        if tool_name in self.tool_status:
            self.tool_status[tool_name].update({
                'progress': percentage,
                'current_operation': message,
                'last_activity': datetime.now()
            })
            
            self.tool_progress_updated.emit(tool_name, percentage, message)
            
            # Update status bar with current operation
            if percentage < 100:
                self._update_status_bar(f"{tool_name}: {message} ({percentage}%)")
            else:
                self._update_status_bar(f"{tool_name}: Completed")
    
    def update_tool_status(self, tool_name: str, status: str, details: Dict = None):
        """Update tool status in hub."""
        if tool_name in self.tool_status:
            self.tool_status[tool_name].update({
                'status': status,
                'last_activity': datetime.now()
            })
            
            if details:
                self.tool_status[tool_name].update(details)
            
            self.tool_status_changed.emit(tool_name, status)
    
    def request_resource(self, tool_name: str, resource_type: str, requirements: Dict = None) -> bool:
        """Handle resource request from tool."""
        try:
            if resource_type in self.resource_manager:
                resource_info = self.resource_manager[resource_type]
                
                if resource_info['available']:
                    # Allocate resource to tool
                    resource_info['available'] = False
                    resource_info['allocated_to'] = tool_name
                    resource_info['allocated_at'] = datetime.now()
                    
                    self._update_status_bar(f"Resource {resource_type} allocated to {tool_name}")
                    return True
                else:
                    # Resource already allocated
                    allocated_to = resource_info.get('allocated_to', 'unknown')
                    self._update_status_bar(f"Resource {resource_type} busy (allocated to {allocated_to})")
                    return False
            
            return False
            
        except Exception as e:
            self._update_status_bar(f"Error handling resource request: {e}")
            return False
    
    def broadcast_event(self, sender: str, event_type: str, event_data: Dict):
        """Broadcast event to all registered tools."""
        try:
            self.hub_event_broadcast.emit(sender, event_type, event_data)
            
            # Forward event to all registered tools except sender
            for tool_name, tool_instance in self.registered_tools.items():
                if tool_name != sender and hasattr(tool_instance, 'hub_connector'):
                    try:
                        # Create hub message for the event
                        from file_utilities_2.integration.hub_connector import HubMessage
                        message = HubMessage(event_type, sender, event_data)
                        tool_instance.hub_connector.handle_hub_message(message)
                    except Exception as e:
                        self._update_status_bar(f"Error forwarding event to {tool_name}: {e}")
                        
        except Exception as e:
            self._update_status_bar(f"Error broadcasting event: {e}")
    
    def _release_tool_resources(self, tool_name: str):
        """Release all resources allocated to a tool."""
        for resource_type, resource_info in self.resource_manager.items():
            if resource_info.get('allocated_to') == tool_name:
                resource_info['available'] = True
                resource_info['allocated_to'] = None
                resource_info.pop('allocated_at', None)
    
    def _handle_tool_error(self, tool_name: str, error_message: str, error_data: Dict):
        """Handle tool error reports."""
        self._update_status_bar(f"Error in {tool_name}: {error_message}")
        
        # Update tool status
        if tool_name in self.tool_status:
            self.tool_status[tool_name].update({
                'status': 'error',
                'last_error': error_message,
                'error_time': datetime.now()
            })
    
    def _update_tool_heartbeat(self, tool_name: str, heartbeat_data: Dict):
        """Update tool heartbeat information."""
        if tool_name in self.tool_status:
            self.tool_status[tool_name].update({
                'last_heartbeat': datetime.now(),
                'heartbeat_data': heartbeat_data
            })
    
    def _on_tool_registered(self, tool_name: str, tool_instance):
        """Handle tool registration event."""
        pass  # Additional processing if needed
    
    def _on_tool_unregistered(self, tool_name: str):
        """Handle tool unregistration event."""
        pass  # Additional processing if needed
    
    def _on_tool_progress_updated(self, tool_name: str, percentage: int, message: str):
        """Handle tool progress update event."""
        pass  # Additional processing if needed
    
    def _on_tool_status_changed(self, tool_name: str, status: str):
        """Handle tool status change event."""
        pass  # Additional processing if needed
    
    def _on_hub_event_broadcast(self, sender: str, event_type: str, data: Dict):
        """Handle hub event broadcast."""
        pass  # Additional processing if needed
    
    def _update_status_bar(self, message: str):
        """Update the status bar with a message."""
        if hasattr(self, 'status_bar'):
            self.status_bar.showMessage(message, 5000)
    
    def _setup_ui(self) -> None:
        """Setup the user interface with standardized styling."""
        # Create menu bar
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')
        
        # Add Exit action to File menu
        exit_action = file_menu.addAction('Exit')
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        central_widget.setLayout(main_layout)
        
        # Header
        header = QLabel("Richard's File Utilities Hub")
        header_font = Fonts.get_font(Fonts.TITLE_SIZE, Fonts.BOLD)
        header.setFont(header_font)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet(
            f"color: {Colors.PRIMARY}; margin-bottom: 20px;"
        )
        main_layout.addWidget(header)
        
        # Create grid for utility buttons
        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)
        
        # Utility buttons with consistent styling
        utilities = [
            ("Encrypt/Decrypt", self.open_encrypt_decrypt, True),
            ("Rename Files", self.open_rename_window, True),
            ("File Catalog", self.open_catalog_window, True),
            ("Copy/Move/Sync/Delete", self.open_cmsd_window, True),
            ("Organize Files", self.open_organize_window, True),
            ("PDF Tools", self.open_pdf_tools, True),
            ("Privacy Tools", self.open_privacy_tools, True),
            ("System Diagnostics", self.open_system_diagnostics, True),
            ("System Cleanup", self.open_system_cleanup, True),
            ("Software Maintenance", self.open_software_maintenance, True),
            ("Network Connectivity", self.open_network_connectivity, True),
            ("Network Scanner", self.open_network_scanner, True),
            ("Find Files", self.open_file_finder, False),
            ("Size Analyzer", self.open_size_analyzer, False),
            ("Permissions Editor", self.open_permissions_editor, False),
            ("Sync Directories", self.open_sync, False),
            ("Office Metadata", self.open_office_metadata_editor, False),
            ("Duplicate Finder", self.open_duplicate_finder, False),
            ("Compress/Decompress", self.open_compress_decompress, False),
            ("Tag Metadata", self.open_tag_metadata_editor, False),
            ("Checksum Tool", self.open_checksum, False),
            ("Tree Map", self.open_tree_map, False),
            ("Empty Folders", self.open_empty_folders, False),
            ("File Touch", self.open_file_touch, False),
            ("File Splitter", self.open_file_splitter, False),
            ("Secure Delete", self.open_secure_delete, False),
            ("Log Manager", self.open_log_manager, False),
            ("Settings", self.open_settings_dialog, False),
        ]
        
        row, col = 0, 0
        for text, callback, primary in utilities:
            btn = StyledButton(text, primary=primary)
            btn.clicked.connect(callback)
            grid_layout.addWidget(btn, row, col)
            
            col += 1
            if col > 2:  # 3 columns
                col = 0
                row += 1
        
        main_layout.addLayout(grid_layout)
        
        # Add Exit button at the bottom
        exit_btn = StyledButton("Exit Application", primary=False)
        exit_btn.clicked.connect(self.close)
        exit_btn.setMinimumHeight(40)
        main_layout.addWidget(exit_btn)
        
        # Footer
        footer = QLabel("Select a utility to get started")
        footer_font = Fonts.get_font(Fonts.BODY_SIZE)
        footer.setFont(footer_font)
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; margin-top: 20px;"
        )
        main_layout.addWidget(footer)
    
    def open_encrypt_decrypt(self) -> None:
        """Open encrypt/decrypt utility with hub integration."""
        try:
            # MIGRATION UPDATE: Import from new file_utilities_2 package location
            # Changed from: from en_and_decrypt import EnAndDecryptGUI
            # Changed to: from file_utilities_2.gui.encryption_gui import EncryptionGUI
            # Reason: en_and_decrypt has been migrated to file_utilities_2 package
            # and enhanced with hub integration and StandardWindow base class
            from file_utilities_2.gui.encryption_gui import EncryptionGUI
            
            # MIGRATION UPDATE: Updated instantiation to use hub integration
            # Changed from: EnAndDecryptGUI() to EncryptionGUI(hub_instance=self)
            # This enables full hub integration with progress reporting and resource management
            self.encrypt_decrypt_window = EncryptionGUI(hub_instance=self)
            self.encrypt_decrypt_window.show()
            
            # Register the tool with the hub
            self.register_tool("Encryption/Decryption", self.encrypt_decrypt_window)
            
        except ImportError as e:
            print(f"Error loading encrypt/decrypt: {e}")
            self._update_status_bar(f"Failed to load Encryption/Decryption: {e}")
        except Exception as e:
            print(f"Error opening encrypt/decrypt: {e}")
            self._update_status_bar(f"Error opening Encryption/Decryption: {e}")
    
    def open_rename_window(self) -> None:
        """Open rename utility."""
        try:
            rename_window = RenameWindow()
            rename_window.show()
        except Exception as e:
            print(f"Error opening rename window: {e}")
    
    def open_catalog_window(self) -> None:
        """Open catalog utility."""
        try:
            catalog_window = CatalogWindow()
            catalog_window.show()
        except Exception as e:
            print(f"Error opening catalog window: {e}")
    
    def open_cmsd_window(self) -> None:
        """Open copy/move/sync/delete utility."""
        try:
            cmsd_window = CopyMoveSyncDeleteWindow()
            cmsd_window.show()
        except Exception as e:
            print(f"Error opening CMSD window: {e}")
    
    def open_organize_window(self) -> None:
        """Open organize utility."""
        try:
            organize_window = OrganizeWindow()
            organize_window.show()
        except Exception as e:
            print(f"Error opening organize window: {e}")
    
    def open_file_finder(self) -> None:
        """Open file finder utility."""
        try:
            # MIGRATION UPDATE: Import from new file_utilities_1 package location
            # Changed from: from file_finder import FileFinderGUI
            # Changed to: from file_utilities_1 import FileFinderWindow
            # Reason: file_finder.py has been migrated to file_utilities_1 package
            # and class renamed from FileFinderGUI to FileFinderWindow for consistency
            from file_utilities_1 import FileFinderWindow
            
            # MIGRATION UPDATE: Updated instantiation to use new class name
            # Changed from: FileFinderGUI() to FileFinderWindow()
            # This maintains all existing functionality while using the migrated class
            self.file_finder_window = FileFinderWindow()
            self.file_finder_window.show()
        except ImportError as e:
            print(f"Error loading file finder: {e}")
    
    def open_size_analyzer(self) -> None:
        """Open size analyzer utility with hub integration."""
        try:
            # MIGRATION UPDATE: Import from new file_utilities_2 package location
            # Changed from: from size_analyzer import SizeAnalyzerWindow
            # Changed to: from file_utilities_2.gui.size_analyzer_gui import SizeAnalyzerGUI
            # Reason: size_analyzer has been migrated to file_utilities_2 package
            # and class renamed from SizeAnalyzerWindow to SizeAnalyzerGUI for consistency
            from file_utilities_2.gui.size_analyzer_gui import SizeAnalyzerGUI
            
            # MIGRATION UPDATE: Updated instantiation to use new class name with hub integration
            # Changed from: SizeAnalyzerWindow() to SizeAnalyzerGUI(hub_instance=self)
            # This maintains all existing functionality while adding hub integration
            self.size_analyzer_window = SizeAnalyzerGUI(hub_instance=self)
            self.size_analyzer_window.show()
            
            # Register the tool with the hub
            self.register_tool("Size Analyzer", self.size_analyzer_window)
            
        except ImportError as e:
            print(f"Error loading size analyzer: {e}")
            self._update_status_bar(f"Failed to load Size Analyzer: {e}")
        except Exception as e:
            print(f"Error opening size analyzer: {e}")
            self._update_status_bar(f"Error opening Size Analyzer: {e}")
    
    def open_permissions_editor(self) -> None:
        """Open permissions editor utility."""
        try:
            from permissions_editor import PermissionsEditorGUI
            self.permissions_editor_window = PermissionsEditorGUI()
            self.permissions_editor_window.show()
        except ImportError as e:
            print(f"Error loading permissions editor: {e}")
    
    def open_sync(self) -> None:
        """Open sync utility."""
        try:
            from synchronization_backup.sync import SyncWindow
            self.sync_window = SyncWindow()
            self.sync_window.show()
        except ImportError as e:
            print(f"Error loading sync: {e}")
    
    def open_office_metadata_editor(self) -> None:
        """Open office metadata editor utility."""
        try:
            from office_meta_data_editor import OfficeMetaDataEditorGUI
            self.office_metadata_window = OfficeMetaDataEditorGUI()
            self.office_metadata_window.show()
        except ImportError as e:
            print(f"Error loading office metadata editor: {e}")
    
    def open_duplicate_finder(self) -> None:
        """Open duplicate finder utility."""
        try:
            from find_duplicate_files import DuplicateFinderApp
            self.duplicate_finder_window = DuplicateFinderApp()
            self.duplicate_finder_window.show()
        except ImportError as e:
            print(f"Error loading duplicate finder: {e}")
    
    def open_compress_decompress(self) -> None:
        """Open compress/decompress utility."""
        try:
            # MIGRATION UPDATE: Import from new file_utilities_1 package location
            # Changed from: from compress_decompress import CompressDecompressApp
            # Changed to: from file_utilities_1 import CompressDecompressWindow
            # Reason: compress_decompress has been migrated to file_utilities_1 package
            # and class renamed from CompressDecompressApp to CompressDecompressWindow for consistency
            from file_utilities_1 import CompressDecompressWindow
            
            # MIGRATION UPDATE: Updated instantiation to use new class name
            # Changed from: CompressDecompressApp() to CompressDecompressWindow()
            # This maintains all existing functionality while using the migrated class
            self.compress_decompress_window = CompressDecompressWindow()
            self.compress_decompress_window.show()
        except ImportError as e:
            print(f"Error loading compress/decompress: {e}")
    
    def open_tag_metadata_editor(self) -> None:
        """Open tag metadata editor utility."""
        try:
            # MIGRATION UPDATE: Import from new file_utilities_2 package location
            # Changed from: from tag_viewer_editor import TagViewerEditor
            # Changed to: from file_utilities_2.gui.tag_viewer_editor import TagViewerEditor
            # Reason: tag_viewer_editor has been migrated to file_utilities_2 package
            # and moved to gui subdirectory for better organization
            from file_utilities_2.gui.tag_viewer_editor import TagViewerEditor
            self.tag_metadata_window = TagViewerEditor()
            self.tag_metadata_window.show()
        except ImportError as e:
            print(f"Error loading tag metadata editor: {e}")
    
    def open_checksum(self) -> None:
        """Open checksum utility."""
        try:
            from file_utilities_2.gui.check_sum_gui import ChecksumGUI
            self.checksum_window = ChecksumGUI()
            self.checksum_window.show()
        except ImportError as e:
            print(f"Error loading checksum: {e}")
    
    def open_tree_map(self) -> None:
        """Open tree map utility."""
        try:
            from tree_map import TreeMapGUI
            self.tree_map_window = TreeMapGUI()
            self.tree_map_window.show()
        except ImportError as e:
            print(f"Error loading tree map: {e}")
    
    def open_empty_folders(self) -> None:
        """Open empty folders utility."""
        try:
            from empty_folders import EmptyFoldersGUI
            self.empty_folders_window = EmptyFoldersGUI()
            self.empty_folders_window.show()
        except ImportError as e:
            print(f"Error loading empty folders: {e}")
    
    def open_file_touch(self) -> None:
        """Open file touch utility."""
        try:
            # MIGRATION UPDATE: Import from new file_utilities_1 package location
            # Changed from: from file_touch import FileTouchGUI
            # Changed to: from file_utilities_1 import FileTouchWindow
            # Reason: file_touch has been migrated to file_utilities_1 package
            # and class renamed from FileTouchGUI to FileTouchWindow for consistency
            from file_utilities_1 import FileTouchWindow
            
            # MIGRATION UPDATE: Updated instantiation to use new class name
            # Changed from: FileTouchGUI() to FileTouchWindow()
            # This maintains all existing functionality while using the migrated class
            self.file_touch_window = FileTouchWindow()
            self.file_touch_window.show()
        except ImportError as e:
            print(f"Error loading file touch: {e}")
            self._update_status_bar(f"Failed to load File Touch: {e}")
        except Exception as e:
            print(f"Error opening file touch: {e}")
            self._update_status_bar(f"Error opening File Touch: {e}")
    
    def open_file_splitter(self) -> None:
        """Open file splitter utility."""
        try:
            from file_splitter_joiner import FileSplitJoinGUI
            self.file_splitter_window = FileSplitJoinGUI()
            self.file_splitter_window.show()
        except ImportError as e:
            print(f"Error loading file splitter: {e}")
    
    def open_secure_delete(self) -> None:
        """Open secure delete utility with hub integration."""
        try:
            # MIGRATION UPDATE: Import from new file_utilities_2 package location
            # Changed from: from secure_delete import SecureDeleteGUI
            # Changed to: from file_utilities_2.gui.secure_delete_gui import SecureDeleteGUI
            # Reason: secure_delete has been migrated to file_utilities_2 package
            # and enhanced with hub integration and StandardWindow base class
            from file_utilities_2.gui.secure_delete_gui import SecureDeleteGUI
            
            # MIGRATION UPDATE: Updated instantiation to use hub integration
            # Changed from: SecureDeleteGUI() to SecureDeleteGUI(hub_instance=self)
            # This enables full hub integration with progress reporting and resource management
            self.secure_delete_window = SecureDeleteGUI(hub_instance=self)
            self.secure_delete_window.show()
            
            # Register the tool with the hub
            self.register_tool("Secure Delete", self.secure_delete_window)
            
        except ImportError as e:
            print(f"Error loading secure delete: {e}")
            self._update_status_bar(f"Failed to load Secure Delete: {e}")
        except Exception as e:
            print(f"Error opening secure delete: {e}")
            self._update_status_bar(f"Error opening Secure Delete: {e}")
    
    def open_log_manager(self) -> None:
        """Open log manager utility."""
        try:
            from gui.log_viewer import LogViewerWindow
            self.log_manager_window = LogViewerWindow()
            self.log_manager_window.show()
        except ImportError as e:
            print(f"Error loading log manager: {e}")
    
    def open_pdf_tools(self) -> None:
        """Open PDF Tools hub."""
        try:
            import sys
            from pathlib import Path
            
            # Add pdf_utilities directory to path for PDF utilities
            pdf_tools_path = Path(__file__).parent / 'pdf_utilities'
            if str(pdf_tools_path) not in sys.path:
                sys.path.insert(0, str(pdf_tools_path))
            
            from main import MainWindow as PDFMainWindow
            self.pdf_tools_window = PDFMainWindow()
            self.pdf_tools_window.show()
        except ImportError as e:
            print(f"Error loading PDF Tools: {e}")
            # Fallback: show message about PDF tools integration
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(
                self,
                "PDF Tools",
                "PDF Tools are being integrated. Please check back soon!\n\n"
                "Available PDF utilities:\n"
                "• Text Extraction\n"
                "• PDF Split/Merge\n"
                "• Page Administration\n"
                "• OCR Processing\n"
                "• And many more..."
            )
        except Exception as e:
            print(f"Error opening PDF Tools: {e}")
    
    def open_privacy_tools(self) -> None:
        """Open Privacy Tools hub."""
        try:
            from privacy_tools.gui.privacy_hub import PrivacyToolsHub
            self.privacy_tools_window = PrivacyToolsHub()
            self.privacy_tools_window.show()
        except ImportError as e:
            print(f"Error loading Privacy Tools: {e}")
            # Fallback: show message about privacy tools
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(
                self,
                "Privacy Tools",
                "Privacy Tools are available!\n\n"
                "Available privacy utilities:\n"
                "• Secure Empty Trash\n"
                "• Delete Browser Cookies\n"
                "• Delete Internet History\n"
                "• Delete File History\n"
                "• Delete Browser Downloads\n\n"
                "Please ensure all dependencies are installed."
            )
        except Exception as e:
            print(f"Error opening Privacy Tools: {e}")
    
    def open_software_maintenance(self) -> None:
        """Open Software Maintenance Toolkit."""
        try:
            from software_maintenance.gui.maintenance_hub import SoftwareMaintenanceHub
            self.software_maintenance_window = SoftwareMaintenanceHub()
            self.software_maintenance_window.show()
        except ImportError as e:
            print(f"Error loading Software Maintenance Toolkit: {e}")
            # Fallback: show message about software maintenance tools
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(
                self,
                "Software Maintenance Toolkit",
                "Software Maintenance Toolkit is available!\n\n"
                "Available maintenance utilities:\n"
                "• Intelligent Software Updater\n"
                "  - Automatic scanning and detection\n"
                "  - Multi-source update checking\n"
                "  - Changelog retrieval and display\n"
                "  - Selective updating with rollback\n"
                "  - Scheduling and automation\n"
                "  - Update history logging\n\n"
                "• Powerful Software De-Installer\n"
                "  - Deep system scanning\n"
                "  - Complete removal with leftover cleanup\n"
                "  - Batch uninstallation capabilities\n"
                "  - Restore points and rollback\n"
                "  - Disk space analysis and recovery\n"
                "  - Uninstallation history tracking\n\n"
                "Please ensure all dependencies are installed."
            )
        except Exception as e:
            print(f"Error opening Software Maintenance Toolkit: {e}")
    
    def open_network_connectivity(self) -> None:
        """Open Network Connectivity tool."""
        try:
            from ..utilities.network.network_connectivity import NetworkConnectivityGUI
            self.network_connectivity_window = NetworkConnectivityGUI()
            self.network_connectivity_window.show()
        except ImportError as e:
            print(f"Error loading Network Connectivity: {e}")
            self._update_status_bar(f"Failed to load Network Connectivity: {e}")
        except Exception as e:
            print(f"Error opening Network Connectivity: {e}")
            self._update_status_bar(f"Error opening Network Connectivity: {e}")
    
    def open_network_scanner(self) -> None:
        """Open Network Scanner tool."""
        try:
            from ..utilities.network.network_scanner import NetworkScannerGUI
            self.network_scanner_window = NetworkScannerGUI()
            self.network_scanner_window.show()
        except ImportError as e:
            print(f"Error loading Network Scanner: {e}")
            self._update_status_bar(f"Failed to load Network Scanner: {e}")
        except Exception as e:
            print(f"Error opening Network Scanner: {e}")
            self._update_status_bar(f"Error opening Network Scanner: {e}")
    
    def open_system_diagnostics(self) -> None:
        """Open System Diagnostics tool."""
        try:
            from ..utilities.system.diagnostics_monitoring import (
                SystemDiagnosticsGUI,
                create_system_diagnostics_gui,
                MAIN_GUI_AVAILABLE
            )
            
            if MAIN_GUI_AVAILABLE and SystemDiagnosticsGUI:
                # Create diagnostics GUI with hub integration
                self.system_diagnostics_window = create_system_diagnostics_gui(
                    hub_instance=self
                )
                
                if self.system_diagnostics_window:
                    self.system_diagnostics_window.show()
                    
                    # Register the tool with the hub
                    self.register_tool("System Diagnostics", self.system_diagnostics_window)
                    
                    self._update_status_bar("System Diagnostics opened successfully")
                else:
                    self._show_diagnostics_fallback_message()
            else:
                self._show_diagnostics_fallback_message()
                
        except ImportError as e:
            print(f"Error loading System Diagnostics: {e}")
            self._update_status_bar(f"Failed to load System Diagnostics: {e}")
            self._show_diagnostics_fallback_message()
        except Exception as e:
            print(f"Error opening System Diagnostics: {e}")
            self._update_status_bar(f"Error opening System Diagnostics: {e}")
            self._show_diagnostics_fallback_message()
    
    def _show_diagnostics_fallback_message(self) -> None:
        """Show fallback message for System Diagnostics."""
        try:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(
                self,
                "System Diagnostics",
                "System Diagnostics Tool\n\n"
                "The comprehensive system diagnostics tool provides:\n\n"
                "• Real-time system monitoring\n"
                "• Disk health analysis\n"
                "• Performance tracking\n"
                "• Battery health monitoring\n"
                "• System information display\n"
                "• Diagnostic reporting\n\n"
                "Note: Some features may require additional dependencies.\n"
                "Please ensure PyQt5 and system monitoring libraries are installed."
            )
        except Exception as e:
            print(f"Error showing diagnostics fallback message: {e}")
    
    def open_system_cleanup(self) -> None:
        """Open System Cleanup tool."""
        try:
            from ..utilities.system.system_cleanup import SystemCleanupGUI
            
            # Create cleanup GUI with hub integration
            self.system_cleanup_window = SystemCleanupGUI(hub_instance=self)
            self.system_cleanup_window.show()
            
            # Register the tool with the hub
            self.register_tool("System Cleanup", self.system_cleanup_window)
            
            self._update_status_bar("System Cleanup opened successfully")
                
        except ImportError as e:
            print(f"Error loading System Cleanup: {e}")
            self._update_status_bar(f"Failed to load System Cleanup: {e}")
            self._show_cleanup_fallback_message()
        except Exception as e:
            print(f"Error opening System Cleanup: {e}")
            self._update_status_bar(f"Error opening System Cleanup: {e}")
            self._show_cleanup_fallback_message()
    
    def _show_cleanup_fallback_message(self) -> None:
        """Show fallback message for System Cleanup."""
        try:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(
                self,
                "System Cleanup",
                "System Cleanup Tool\n\n"
                "The comprehensive system cleanup tool provides:\n\n"
                "• Temporary files cleanup\n"
                "• Cache clearing\n"
                "• Registry cleaning\n"
                "• System optimization\n"
                "• Disk space recovery\n"
                "• Performance enhancement\n\n"
                "Note: Some features may require additional dependencies.\n"
                "Please ensure PyQt5 and cleanup libraries are installed."
            )
        except Exception as e:
            print(f"Error showing cleanup fallback message: {e}")
    
    def open_settings_dialog(self) -> None:
        """Open settings dialog."""
        try:
            from settings_dialog import SettingsDialog
            self.settings_dialog_window = SettingsDialog()
            self.settings_dialog_window.show()
        except ImportError as e:
            print(f"Error loading settings dialog: {e}")


class RFUHub(MyGUI):
    """Richard's File Utilities Hub - Main application class."""
    
    def __init__(self) -> None:
        super().__init__()


def main() -> None:
    """Main function to run the RFU Hub application."""
    app = QApplication(sys.argv)
    
    # Apply application-wide stylesheet
    app.setStyle('Fusion')
    app.setStyleSheet(f"""
        QApplication {{
            font-family: {Fonts.DEFAULT_FAMILY};
            font-size: {Fonts.BODY_SIZE}pt;
        }}
    """)
    
    window = RFUHub()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
