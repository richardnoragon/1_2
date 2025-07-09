from PyQt5.QtWidgets import (
    QApplication, QWidget, QMainWindow, QPushButton, QVBoxLayout, QLabel,
    QSizePolicy, QSpacerItem, QHBoxLayout, QGridLayout, QTabWidget
)
from PyQt5.QtGui import QIcon, QFont, QColor
from PyQt5.QtCore import Qt, QSize
import sys
import subprocess
import os
from log_manager import LogManager
from gui.common.base_window import BaseWindow


class RenameWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rename Window")
        self.setGeometry(100, 100, 400, 300)
        self.show()


class CatalogWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Catalog Window")
        self.setGeometry(100, 100, 400, 300)
        self.show()


class CopyMoveSyncDeleteWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Copy/Move/Sync/Delete Window")
        self.setGeometry(100, 100, 400, 300)
        self.show()


class OrganizeWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Organize Window")
        self.setGeometry(100, 100, 400, 300)
        self.show()


class StyledButton(QPushButton):
    def __init__(self, text, icon_name=None, color="#D3D3D3"):
        super().__init__(text)
        # Set minimum size for buttons
        self.setMinimumHeight(50)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # Set font
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.setFont(font)
        
        # Set style
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border-radius: 10px;
                padding: 10px;
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: {self._darken_color(color)};
            }}
            QPushButton:pressed {{
                background-color: {self._darken_color(color, factor=30)};
            }}
        """)
        
        # Set icon if provided
        if icon_name:
            icon_path = self._get_icon_path(icon_name)
            if icon_path:
                self.setIcon(QIcon(icon_path))
                self.setIconSize(QSize(24, 24))
    
    def _darken_color(self, hex_color, factor=20):
        """Darken a hex color by a percentage factor"""
        color = QColor(hex_color)
        h, s, v, a = color.getHsv()
        v = max(0, int(v - factor * 255 / 100))
        color.setHsv(h, s, v, a)
        return color.name()
    
    def _get_icon_path(self, icon_name):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "icons", f"{icon_name}.png")
        return icon_path if os.path.exists(icon_path) else None


class MyGUI(BaseWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Richard's File Utilities Hub")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon(self._get_icon_path("app_icon")))
        
        # Set application style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QLabel {
                color: #333333;
                font-size: 14px;
                font-weight: bold;
                margin-bottom: 10px;
            }
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background: #ffffff;
            }
            QTabWidget::tab-bar {
                left: 5px;
            }
            QTabBar::tab {
                background: #e0e0e0;
                border: 1px solid #c4c4c4;
                padding: 5px 10px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #ffffff;
            }
        """)

        # Create main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Add header
        header = QLabel("Richard's File Utilities Hub")
        header.setAlignment(Qt.AlignCenter)
        header_font = QFont()
        header_font.setPointSize(16)
        header_font.setBold(True)
        header.setFont(header_font)
        header.setStyleSheet("color: #333333; margin-bottom: 20px;")
        main_layout.addWidget(header)

        # Create tab widget
        tab_widget = QTabWidget()

        # Create tabs for different categories
        file_mgmt_tab = QWidget()
        org_tab = QWidget()
        analysis_tab = QWidget()
        operations_tab = QWidget()
        metadata_tab = QWidget()
        system_tab = QWidget()
        admin_tab = QWidget()  # New Administration tab

        # Create layouts for each tab
        file_mgmt_layout = QGridLayout(file_mgmt_tab)
        org_layout = QGridLayout(org_tab)
        analysis_layout = QGridLayout(analysis_tab)
        operations_layout = QGridLayout(operations_tab)
        metadata_layout = QGridLayout(metadata_tab)
        system_layout = QGridLayout(system_tab)
        admin_layout = QGridLayout(admin_tab)  # New Administration layout

        # Create styled buttons
        grey = "#D3D3D3"  # Light Grey

        # File Management Tools
        self.file_finder_button = StyledButton("File Finder", "search", grey)
        self.catalog_button = StyledButton("Catalog Files", "catalog", grey)
        self.rename_button = StyledButton("Rename Files", "rename", grey)
        
        # Organization Tools
        self.organize_button = StyledButton("Organize Files", "organize", grey)
        self.cmsd_button = StyledButton("Copy/Move/Sync/Delete", "transfer", grey)
        self.sync_button = StyledButton("Synchronize", "sync", grey)
        self.empty_folders_button = StyledButton("Find Empty Folders", "folder", grey)
        
        # Analysis Tools
        self.size_analyzer_button = StyledButton("Analyze Size", "disk", grey)
        self.duplicate_finder_button = StyledButton("Duplicate Finder", "duplicate", grey)
        self.tree_map_button = StyledButton("Disk Space Analyzer", "disk", grey)
        self.checksum_button = StyledButton("File Checksum", "checksum", grey)
        
        # File Operations
        self.encrypt_decrypt_button = StyledButton("Encrypt/Decrypt", "lock", grey)
        self.compress_decompress_button = StyledButton("Compress/Decompress", "compress", grey)
        self.file_splitter_button = StyledButton("Split/Join Files", "split", grey)
        self.file_touch_button = StyledButton("File Timestamps", "clock", grey)
        self.secure_delete_button = StyledButton("Secure Delete", "shred", grey)
        
        # Metadata Tools
        self.office_metadata_button = StyledButton("Office Metadata", "file", grey)
        self.tag_metadata_button = StyledButton("Media Tags", "tag", grey)
        
        # System Tools
        self.permissions_button = StyledButton("File Permissions", "lock", grey)

        # Administration Tools
        self.log_manager_button = StyledButton("Log Manager", "log", grey)
        self.settings_button = StyledButton("Settings", "settings", grey)

        # Add buttons to layouts
        # File Management
        file_mgmt_layout.addWidget(self.file_finder_button, 0, 0)
        file_mgmt_layout.addWidget(self.catalog_button, 0, 1)
        file_mgmt_layout.addWidget(self.rename_button, 1, 0)

        # Organization
        org_layout.addWidget(self.organize_button, 0, 0)
        org_layout.addWidget(self.cmsd_button, 0, 1)
        org_layout.addWidget(self.sync_button, 1, 0)
        org_layout.addWidget(self.empty_folders_button, 1, 1)

        # Analysis
        analysis_layout.addWidget(self.size_analyzer_button, 0, 0)
        analysis_layout.addWidget(self.duplicate_finder_button, 0, 1)
        analysis_layout.addWidget(self.tree_map_button, 1, 0)
        analysis_layout.addWidget(self.checksum_button, 1, 1)

        # Operations
        operations_layout.addWidget(self.encrypt_decrypt_button, 0, 0)
        operations_layout.addWidget(self.compress_decompress_button, 0, 1)
        operations_layout.addWidget(self.file_splitter_button, 1, 0)
        operations_layout.addWidget(self.file_touch_button, 1, 1)
        operations_layout.addWidget(self.secure_delete_button, 2, 0)

        # Metadata
        metadata_layout.addWidget(self.office_metadata_button, 0, 0)
        metadata_layout.addWidget(self.tag_metadata_button, 0, 1)

        # System
        system_layout.addWidget(self.permissions_button, 0, 0)

        # Administration
        admin_layout.addWidget(self.log_manager_button, 0, 0)
        admin_layout.addWidget(self.settings_button, 0, 1)

        # Add tabs to tab widget
        tab_widget.addTab(file_mgmt_tab, "File Management")
        tab_widget.addTab(org_tab, "Organization")
        tab_widget.addTab(analysis_tab, "Analysis")
        tab_widget.addTab(operations_tab, "Operations")
        tab_widget.addTab(metadata_tab, "Metadata")
        tab_widget.addTab(system_tab, "System")
        tab_widget.addTab(admin_tab, "Administration")

        # Add tab widget to main layout
        main_layout.addWidget(tab_widget)

        # Add exit button at bottom
        self.exit_button = StyledButton("Exit", "exit", grey)
        exit_layout = QHBoxLayout()
        exit_layout.addStretch()
        exit_layout.addWidget(self.exit_button)
        exit_layout.addStretch()
        main_layout.addLayout(exit_layout)

        # Connect buttons to their handlers
        self.connect_button_handlers()

        # Set the central widget
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def connect_button_handlers(self):
        # File Management
        self.file_finder_button.clicked.connect(self.open_file_finder)
        self.catalog_button.clicked.connect(self.open_catalog_window)
        self.rename_button.clicked.connect(self.open_rename_window)
        
        # Organization
        self.organize_button.clicked.connect(self.open_organize_window)
        self.cmsd_button.clicked.connect(self.open_cmsd_window)
        self.sync_button.clicked.connect(self.open_sync)
        self.empty_folders_button.clicked.connect(self.open_empty_folders)
        
        # Analysis
        self.size_analyzer_button.clicked.connect(self.open_size_analyzer)
        self.duplicate_finder_button.clicked.connect(self.open_duplicate_finder)
        self.tree_map_button.clicked.connect(self.open_tree_map)
        self.checksum_button.clicked.connect(self.open_checksum)
        
        # Operations
        self.encrypt_decrypt_button.clicked.connect(self.open_encrypt_decrypt)
        self.compress_decompress_button.clicked.connect(self.open_compress_decompress)
        self.file_splitter_button.clicked.connect(self.open_file_splitter)
        self.file_touch_button.clicked.connect(self.open_file_touch)
        self.secure_delete_button.clicked.connect(self.open_secure_delete)
        
        # Metadata
        self.office_metadata_button.clicked.connect(self.open_office_metadata_editor)
        self.tag_metadata_button.clicked.connect(self.open_tag_metadata_editor)
        
        # System
        self.permissions_button.clicked.connect(self.open_permissions_editor)
        
        # Administration
        self.log_manager_button.clicked.connect(self.open_log_manager)
        self.settings_button.clicked.connect(self.open_settings_dialog)
        
        # Exit
        self.exit_button.clicked.connect(QApplication.instance().quit)

    def _get_icon_path(self, icon_name):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "icons", f"{icon_name}.png")
        return icon_path if os.path.exists(icon_path) else None

    def open_encrypt_decrypt(self):
        subprocess.call(["python", "en_and_decrypt.py"])

    def open_rename_window(self):
        subprocess.call(["python", "rename.py"])

    def open_catalog_window(self):
        subprocess.call(["python", "catalog.py"])

    def open_cmsd_window(self):
        subprocess.call(["python", "cmsd.py"])

    def open_organize_window(self):
        subprocess.call(["python", "organize.py"])
        
    def open_file_finder(self):
        subprocess.call(["python", "file_finder.py"])

    def open_size_analyzer(self):
        subprocess.call(["python", "size_analyzer.py"])

    def open_permissions_editor(self):
        subprocess.call(["python", "permissions_editor.py"])

    def open_sync(self):
        subprocess.call(["python", "sync.py"])

    def open_office_metadata_editor(self):
        subprocess.call(["python", "office_meta_data_editor.py"])

    def open_duplicate_finder(self):
        subprocess.call(["python", "find_duplicate_files.py"])

    def open_compress_decompress(self):
        subprocess.call(["python", "compress_decompress.py"])

    def open_tag_metadata_editor(self):
        subprocess.call(["python", "tag_viewer_editor.py"])

    def open_checksum(self):
        subprocess.call(["python", "check_sum.py"])

    def open_tree_map(self):
        subprocess.call(["python", "tree_map.py"])

    def open_empty_folders(self):
        subprocess.call(["python", "empty_folders.py"])

    def open_file_touch(self):
        subprocess.call(["python", "file_touch.py"])

    def open_file_splitter(self):
        subprocess.call(["python", "file_splitter_joiner.py"])

    def open_secure_delete(self):
        subprocess.call(["python", "secure_delete.py"])

    def open_log_manager(self):
        subprocess.call(["python", "log_manager.py"])

    def open_settings_dialog(self):
        subprocess.call(["python", "settings_dialog.py"])


class RFUHub(MyGUI):
    def __init__(self):
        self.logger = LogManager().get_logger('RFUHub')
        self.logger.info('Initializing RFU Hub')
        super().__init__()  # Initialize the MyGUI parent class


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = RFUHub()
    window.show()
    sys.exit(app.exec_())
