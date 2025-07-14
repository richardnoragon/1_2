from PyQt5.QtWidgets import (
    QApplication, QWidget, QMainWindow, QPushButton, QVBoxLayout, QLabel,
    QSizePolicy, QSpacerItem, QHBoxLayout, QGridLayout, QTabWidget,
    QStatusBar
)
from PyQt5.QtGui import QIcon, QFont, QColor
from PyQt5.QtCore import Qt, QSize
import sys
import subprocess
import os
import shutil
from log_manager import LogManager
from gui.common.base_window import BaseWindow
from gui.themes import ThemeManager, Colors, Fonts
from core import error_handler
from typing import Optional, List



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


class CatalogWindow(StandardUtilityWindow):
    """Standardized catalog window."""
    
    def __init__(self) -> None:
        super().__init__("File Catalog Utility", 600, 450)
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Setup the user interface."""
        # Header
        header = self.create_header("File Catalog Utility")
        self.main_layout.addWidget(header)
        
        # Buttons
        scan_btn = StyledButton("Scan Directory", primary=True)
        generate_btn = StyledButton("Generate Catalog", primary=False)
        
        button_row = self.create_button_row([scan_btn, generate_btn])
        self.main_layout.addLayout(button_row)
        
        # Connect signals
        scan_btn.clicked.connect(self.scan_directory)
        generate_btn.clicked.connect(self.generate_catalog)
    
    def scan_directory(self) -> None:
        """Handle directory scanning."""
        self.show_status_message("Scanning directory...")
    
    def generate_catalog(self) -> None:
        """Handle catalog generation."""
        self.show_status_message("Generating catalog...")


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
    """Updated main GUI with standardized styling."""
    
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Richard's File Utilities Hub")
        self.setMinimumSize(800, 600)
        self.resize(900, 700)
        
        # Apply standard theme
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {Colors.WINDOW_BACKGROUND};
                color: {Colors.TEXT_PRIMARY};
            }}
        """)
        
        self._setup_ui()
    
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
        """Open encrypt/decrypt utility."""
        try:
            from en_and_decrypt import EnAndDecryptGUI
            self.encrypt_decrypt_window = EnAndDecryptGUI()
            self.encrypt_decrypt_window.show()
        except ImportError as e:
            print(f"Error loading encrypt/decrypt: {e}")
    
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
            from file_finder import FileFinderGUI
            self.file_finder_window = FileFinderGUI()
            self.file_finder_window.show()
        except ImportError as e:
            print(f"Error loading file finder: {e}")
    
    def open_size_analyzer(self) -> None:
        """Open size analyzer utility."""
        try:
            from size_analyzer import SizeAnalyzerWindow
            self.size_analyzer_window = SizeAnalyzerWindow()
            self.size_analyzer_window.show()
        except ImportError as e:
            print(f"Error loading size analyzer: {e}")
    
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
            from sync import SyncWindow
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
            from compress_decompress import CompressDecompressApp
            self.compress_decompress_window = CompressDecompressApp()
            self.compress_decompress_window.show()
        except ImportError as e:
            print(f"Error loading compress/decompress: {e}")
    
    def open_tag_metadata_editor(self) -> None:
        """Open tag metadata editor utility."""
        try:
            from tag_viewer_editor import TagViewerEditor
            self.tag_metadata_window = TagViewerEditor()
            self.tag_metadata_window.show()
        except ImportError as e:
            print(f"Error loading tag metadata editor: {e}")
    
    def open_checksum(self) -> None:
        """Open checksum utility."""
        try:
            from check_sum_gui import ChecksumGUI
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
            from file_touch import FileTouchGUI
            self.file_touch_window = FileTouchGUI()
            self.file_touch_window.show()
        except ImportError as e:
            print(f"Error loading file touch: {e}")
    
    def open_file_splitter(self) -> None:
        """Open file splitter utility."""
        try:
            from file_splitter_joiner import FileSplitJoinGUI
            self.file_splitter_window = FileSplitJoinGUI()
            self.file_splitter_window.show()
        except ImportError as e:
            print(f"Error loading file splitter: {e}")
    
    def open_secure_delete(self) -> None:
        """Open secure delete utility."""
        try:
            from secure_delete import SecureDeleteGUI
            self.secure_delete_window = SecureDeleteGUI()
            self.secure_delete_window.show()
        except ImportError as e:
            print(f"Error loading secure delete: {e}")
    
    def open_log_manager(self) -> None:
        """Open log manager utility."""
        try:
            from gui.log_viewer import LogViewerWindow
            self.log_manager_window = LogViewerWindow()
            self.log_manager_window.show()
        except ImportError as e:
            print(f"Error loading log manager: {e}")
    
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
