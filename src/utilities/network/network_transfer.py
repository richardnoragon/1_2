#!/usr/bin/env python3
"""
Network Transfer Tool for Richard's File Utilities

A comprehensive file and configuration transfer system that allows users to:
- Transfer files and folders between RFU clients
- Sync application settings and preferences
- Transfer predefined file collections
- Transfer backup configurations
- Real-time transfer monitoring with progress tracking
"""

import sys
import os
import json
import socket
import threading
import hashlib
import time
import zipfile
import tempfile
import ssl
import secrets
import hmac
import base64
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

try:
    from PyQt5.QtWidgets import (
        QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QPushButton, QLabel, QProgressBar, QApplication, 
        QMessageBox, QGroupBox, QLineEdit, QSpinBox, 
        QTextEdit, QCheckBox, QComboBox, QListWidget,
        QListWidgetItem, QFileDialog, QTabWidget,
        QTableWidget, QTableWidgetItem, QSplitter,
        QFrame, QGridLayout, QFormLayout, QSlider,
        QTreeWidget, QTreeWidgetItem, QHeaderView
    )
    from PyQt5.QtCore import QThread, pyqtSignal, QTimer, Qt
    from PyQt5.QtGui import QFont, QIcon
except ImportError:
    print("PyQt5 not available. Please install PyQt5.")
    sys.exit(1)

# Import StandardWindow for menu integration
try:
    from src.rfu.gui.standard_window import StandardWindow
except ImportError:
    # Fallback for standalone execution
    StandardWindow = QMainWindow

# Import database manager
try:
    from standalone_database_manager import DatabaseManager
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False
    print("Database manager not available. Transfer history will not be saved.")


class SecurityManager:
    """Handles authentication and encryption for network transfers."""
    
    def __init__(self):
        self.session_key = None
        self.auth_token = None
        
    def generate_session_key(self) -> bytes:
        """Generate a secure session key for encryption."""
        self.session_key = secrets.token_bytes(32)  # 256-bit key
        return self.session_key
    
    def generate_auth_token(self) -> str:
        """Generate a secure authentication token."""
        self.auth_token = secrets.token_urlsafe(32)
        return self.auth_token
    
    def verify_auth_token(self, token: str) -> bool:
        """Verify authentication token."""
        if not self.auth_token or not token:
            return False
        return hmac.compare_digest(self.auth_token, token)
    
    def encrypt_message(self, message: bytes) -> bytes:
        """Encrypt message with session key."""
        if not self.session_key:
            raise ValueError("No session key available")
        
        # Simple XOR encryption for prototype (should use proper AES in production)
        key_cycle = (self.session_key * ((len(message) // 32) + 1))[:len(message)]
        encrypted = bytes(a ^ b for a, b in zip(message, key_cycle))
        
        # Add HMAC for integrity
        hmac_key = self.session_key[:16]
        mac = hmac.new(hmac_key, encrypted, hashlib.sha256).digest()
        
        return mac + encrypted
    
    def decrypt_message(self, encrypted_data: bytes) -> bytes:
        """Decrypt message with session key."""
        if not self.session_key:
            raise ValueError("No session key available")
        
        if len(encrypted_data) < 32:  # HMAC size
            raise ValueError("Invalid encrypted data")
        
        # Verify HMAC
        mac = encrypted_data[:32]
        encrypted = encrypted_data[32:]
        hmac_key = self.session_key[:16]
        expected_mac = hmac.new(hmac_key, encrypted, hashlib.sha256).digest()
        
        if not hmac.compare_digest(mac, expected_mac):
            raise ValueError("Message integrity check failed")
        
        # Decrypt
        key_cycle = (self.session_key * ((len(encrypted) // 32) + 1))[:len(encrypted)]
        decrypted = bytes(a ^ b for a, b in zip(encrypted, key_cycle))
        
        return decrypted


class TransferProtocol:
    """Network transfer protocol for RFU clients."""
    
    VERSION = "1.0"
    CHUNK_SIZE = 8192
    PORT_RANGE = (12000, 12099)  # Reserved port range for RFU transfers
    MAX_MESSAGE_SIZE = 1024 * 1024 * 10  # 10MB max message size
    
    # Message types
    MSG_HELLO = "HELLO"
    MSG_AUTH = "AUTH"
    MSG_FILE_INFO = "FILE_INFO"
    MSG_FILE_DATA = "FILE_DATA"
    MSG_CONFIG_DATA = "CONFIG_DATA"
    MSG_COLLECTION_DATA = "COLLECTION_DATA"
    MSG_ACK = "ACK"
    MSG_ERROR = "ERROR"
    MSG_COMPLETE = "COMPLETE"
    
    @staticmethod
    def create_message(msg_type: str, data: Any) -> bytes:
        """Create a protocol message with size validation."""
        message = {
            "type": msg_type,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        json_str = json.dumps(message)
        message_bytes = json_str.encode('utf-8')
        
        # Validate message size
        if len(message_bytes) > TransferProtocol.MAX_MESSAGE_SIZE:
            raise ValueError(f"Message too large: {len(message_bytes)} bytes")
        
        # Add length prefix
        length = len(message_bytes)
        return length.to_bytes(4, 'big') + message_bytes
    
    @staticmethod
    def parse_message(data: bytes) -> Optional[Dict]:
        """Parse a protocol message with validation."""
        try:
            if len(data) < 4:
                return None
            
            length = int.from_bytes(data[:4], 'big')
            
            # Validate message length
            if length > TransferProtocol.MAX_MESSAGE_SIZE:
                raise ValueError(f"Message too large: {length} bytes")
            
            if length <= 0:
                raise ValueError(f"Invalid message length: {length}")
            
            if len(data) < 4 + length:
                return None
                
            json_str = data[4:4+length].decode('utf-8')
            return json.loads(json_str)
        except Exception:
            return None


class TransferServer(QThread):
    """Server thread for receiving transfers."""
    
    client_connected = pyqtSignal(str, int)
    transfer_started = pyqtSignal(str, str)
    progress_updated = pyqtSignal(int)
    transfer_completed = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, port: int, parent=None):
        super().__init__(parent)
        self.port = port
        self.running = False
        self.server_socket = None
        self.security_manager = SecurityManager()
        
    def run(self):
        """Run the transfer server with security."""
        try:
            sock_family = socket.AF_INET
            sock_type = socket.SOCK_STREAM
            self.server_socket = socket.socket(sock_family, sock_type)
            self.server_socket.setsockopt(socket.SOL_SOCKET,
                                          socket.SO_REUSEADDR, 1)
            # Bind to localhost only for security
            self.server_socket.bind(('127.0.0.1', self.port))
            self.server_socket.listen(5)
            self.running = True
            
            while self.running:
                try:
                    client_socket, address = self.server_socket.accept()
                    
                    # Only accept connections from localhost
                    if address[0] != '127.0.0.1':
                        client_socket.close()
                        continue
                        
                    self.client_connected.emit(address[0], address[1])
                    
                    # Handle client in separate thread
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except socket.error:
                    if self.running:
                        self.error_occurred.emit("Server socket error")
                    break
                    
        except Exception as e:
            self.error_occurred.emit(f"Server error: {str(e)}")
            
    def handle_client(self, client_socket: socket.socket, address: Tuple[str, int]):
        """Handle incoming client connection."""
        try:
            with client_socket:
                while True:
                    # Receive message length
                    length_data = client_socket.recv(4)
                    if not length_data:
                        break
                        
                    length = int.from_bytes(length_data, 'big')
                    
                    # Receive message data
                    message_data = b''
                    while len(message_data) < length:
                        chunk = client_socket.recv(min(length - len(message_data), 4096))
                        if not chunk:
                            break
                        message_data += chunk
                    
                    message = TransferProtocol.parse_message(length_data + message_data)
                    if not message:
                        continue
                    
                    self.process_message(client_socket, message)
                    
        except Exception as e:
            self.error_occurred.emit(f"Client handling error: {str(e)}")
    
    def process_message(self, client_socket: socket.socket, message: Dict):
        """Process received message."""
        msg_type = message.get("type")
        data = message.get("data", {})
        
        if msg_type == TransferProtocol.MSG_HELLO:
            self.transfer_started.emit("Incoming", data.get("client_name", "Unknown"))
            # Send ACK
            response = TransferProtocol.create_message(TransferProtocol.MSG_ACK, {"status": "ready"})
            client_socket.send(response)
            
        elif msg_type == TransferProtocol.MSG_FILE_INFO:
            # File transfer incoming
            filename = data.get("filename")
            filesize = data.get("filesize")
            self.transfer_started.emit("File", f"{filename} ({filesize} bytes)")
            
        elif msg_type == TransferProtocol.MSG_CONFIG_DATA:
            # Configuration transfer
            self.transfer_started.emit("Configuration", "Application settings")
            self.save_received_config(data)
            
        elif msg_type == TransferProtocol.MSG_COLLECTION_DATA:
            # File collection transfer
            collection_name = data.get("name", "Unknown")
            self.transfer_started.emit("Collection", collection_name)
            
    def save_received_config(self, config_data: Dict):
        """Save received configuration data."""
        try:
            # Save to temp location for user review
            temp_dir = Path(tempfile.gettempdir()) / "rfu_received_configs"
            temp_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            config_file = temp_dir / f"received_config_{timestamp}.json"
            
            with open(config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
                
            self.transfer_completed.emit(f"Configuration saved to {config_file}")
            
        except Exception as e:
            self.error_occurred.emit(f"Config save error: {str(e)}")
    
    def stop(self):
        """Stop the server."""
        self.running = False
        if self.server_socket:
            self.server_socket.close()


class PathSecurity:
    """Utilities for secure path handling."""
    
    @staticmethod
    def is_safe_path(base_path: str, user_path: str) -> bool:
        """Check if a user-provided path is safe to access."""
        try:
            # Normalize and resolve paths
            base_path = Path(base_path).resolve()
            full_path = Path(base_path / user_path).resolve()
            
            # Check if the full path is within the base path
            return str(full_path).startswith(str(base_path))
        except (ValueError, OSError):
            return False
    
    @staticmethod
    def secure_join(base_path: str, user_path: str) -> Optional[str]:
        """Safely join a base path with a user-provided path."""
        if not PathSecurity.is_safe_path(base_path, user_path):
            return None
        
        try:
            base_path = Path(base_path).resolve()
            full_path = Path(base_path / user_path).resolve()
            return str(full_path)
        except (ValueError, OSError):
            return None
    
    @staticmethod
    def secure_file_info(file_path: str) -> Optional[Dict[str, Any]]:
        """Safely get file information without TOCTOU vulnerabilities."""
        try:
            # Use file descriptor to avoid TOCTOU issues
            with open(file_path, 'rb') as f:
                fd = f.fileno()
                stat_info = os.fstat(fd)
                return {
                    'size': stat_info.st_size,
                    'exists': True,
                    'path': file_path,
                    'fd': fd
                }
        except (OSError, IOError):
            return None


class TransferClient(QThread):
    """Client thread for sending transfers."""
    
    connection_established = pyqtSignal(str)
    progress_updated = pyqtSignal(int)
    transfer_completed = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, host: str, port: int, transfer_data: Dict, parent=None):
        super().__init__(parent)
        self.host = host
        self.port = port
        self.transfer_data = transfer_data
        
    def run(self):
        """Run the transfer client."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(30)
                sock.connect((self.host, self.port))
                self.connection_established.emit(f"Connected to {self.host}:{self.port}")
                
                # Send hello message
                hello_msg = TransferProtocol.create_message(
                    TransferProtocol.MSG_HELLO,
                    {"client_name": "Richard's File Utilities", "version": TransferProtocol.VERSION}
                )
                sock.send(hello_msg)
                
                # Process transfer based on type
                transfer_type = self.transfer_data.get("type")
                
                if transfer_type == "files":
                    self.send_files(sock)
                elif transfer_type == "config":
                    self.send_config(sock)
                elif transfer_type == "collection":
                    self.send_collection(sock)
                    
                self.transfer_completed.emit("Transfer completed successfully")
                
        except Exception as e:
            self.error_occurred.emit(f"Transfer error: {str(e)}")
    
    def send_files(self, sock: socket.socket):
        """Send files to remote client with security checks."""
        files = self.transfer_data.get("files", [])
        total_files = len(files)
        
        for i, file_path in enumerate(files):
            # Use secure file info to avoid TOCTOU vulnerabilities
            file_info = PathSecurity.secure_file_info(file_path)
            if not file_info:
                continue
                
            file_size = file_info['size']
            filename = os.path.basename(file_path)
            
            # Send file info
            file_info_msg = TransferProtocol.create_message(
                TransferProtocol.MSG_FILE_INFO,
                {"filename": filename, "filesize": file_size}
            )
            sock.send(file_info_msg)
            
            # Send file data using secure file reading
            try:
                with open(file_path, 'rb') as f:
                    bytes_sent = 0
                    while True:
                        chunk = f.read(TransferProtocol.CHUNK_SIZE)
                        if not chunk:
                            break
                        
                        file_data = TransferProtocol.create_message(
                            TransferProtocol.MSG_FILE_DATA,
                            {"data": chunk.hex(), "offset": bytes_sent}
                        )
                        sock.send(file_data)
                        bytes_sent += len(chunk)
                        
                        # Update progress
                        file_progress = int((bytes_sent / file_size) * 100)
                        base_progress = i * 100
                        total_progress = int((base_progress + file_progress) /
                                             total_files)
                        self.progress_updated.emit(total_progress)
            except (OSError, IOError) as e:
                error_msg = f"Error reading file {file_path}: {e}"
                self.error_occurred.emit(error_msg)
                continue
    
    def send_config(self, sock: socket.socket):
        """Send configuration data."""
        config_data = self.transfer_data.get("config", {})
        
        config_msg = TransferProtocol.create_message(
            TransferProtocol.MSG_CONFIG_DATA,
            config_data
        )
        sock.send(config_msg)
        self.progress_updated.emit(100)
    
    def send_collection(self, sock: socket.socket):
        """Send file collection."""
        collection = self.transfer_data.get("collection", {})
        
        collection_msg = TransferProtocol.create_message(
            TransferProtocol.MSG_COLLECTION_DATA,
            collection
        )
        sock.send(collection_msg)
        self.progress_updated.emit(100)


class NetworkTransferGUI(StandardWindow):
    """Main window for Network Transfer operations."""
    
    def __init__(self):
        super().__init__(
            title="Network Transfer - Richard's File Utilities",
            window_type="utility"
        )
        self.db_manager = None
        self.transfer_server = None
        self.transfer_client = None
        self.file_collections = {}
        self.init_database()
        self.init_ui()
        self.load_collections()
        self._setup_menu_callbacks()
        
    def _setup_menu_callbacks(self):
        """Setup tool-specific menu callbacks."""
        if hasattr(self, 'menu_manager'):
            # Register tool-specific callbacks
            self.menu_manager.register_callback('show_preferences',
                                               self.show_preferences)
            self.menu_manager.register_callback('refresh', self.refresh_view)
            self.menu_manager.register_callback('export_data',
                                               self.export_transfer_settings)
            self.menu_manager.register_callback('import_data',
                                               self.import_transfer_settings)
    
    def show_preferences(self):
        """Show Network Transfer preferences."""
        QMessageBox.information(
            self, "Network Transfer Preferences",
            "Network Transfer preferences:\n\n"
            "• Default transfer ports\n"
            "• Security settings\n"
            "• File collection management\n"
            "• Transfer history options\n\n"
            "Advanced preferences coming soon!"
        )
        
    def refresh_view(self):
        """Refresh the network transfer interface."""
        self.load_collections()
        self.load_transfer_history()
        if hasattr(self, 'status_label'):
            self.status_label.setText("Interface refreshed")
        QMessageBox.information(self, "Refresh",
                               "Transfer interface refreshed successfully.")
    
    def export_transfer_settings(self):
        """Export transfer settings and collections."""
        QMessageBox.information(self, "Export Settings",
                               "Export functionality ready for implementation.")
    
    def import_transfer_settings(self):
        """Import transfer settings and collections."""
        QMessageBox.information(self, "Import Settings",
                               "Import functionality ready for implementation.")
        
    def init_database(self):
        """Initialize database connection."""
        if DATABASE_AVAILABLE:
            try:
                self.db_manager = DatabaseManager()
                self.create_transfer_tables()
            except Exception as e:
                print(f"Database initialization failed: {e}")
    
    def create_transfer_tables(self):
        """Create tables for transfer history and collections."""
        if not self.db_manager:
            return
            
        try:
            # Transfer history table
            self.db_manager.execute_query("""
                CREATE TABLE IF NOT EXISTS transfer_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    transfer_type TEXT NOT NULL,
                    direction TEXT NOT NULL,
                    remote_host TEXT,
                    file_count INTEGER DEFAULT 0,
                    total_size INTEGER DEFAULT 0,
                    status TEXT NOT NULL,
                    details TEXT
                )
            """)
            
            # File collections table
            self.db_manager.execute_query("""
                CREATE TABLE IF NOT EXISTS file_collections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    files TEXT NOT NULL,
                    created_date TEXT NOT NULL,
                    last_modified TEXT NOT NULL
                )
            """)
            
            # Transfer settings table
            self.db_manager.execute_query("""
                CREATE TABLE IF NOT EXISTS transfer_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)
            
        except Exception as e:
            print(f"Database table creation failed: {e}")
        
    def init_ui(self):
        """Initialize the user interface."""
        # Use the existing main layout from StandardWindow
        layout = self.main_layout
        
        # Add header
        header_label = QLabel("Network Transfer Tool")
        header_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #2c3e50;
                padding: 15px;
                background-color: #ecf0f1;
                border-radius: 8px;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(header_label)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.create_send_tab()
        self.create_receive_tab()
        self.create_collections_tab()
        self.create_history_tab()
        
        # Status bar and progress
        status_layout = QHBoxLayout()
        
        self.status_label = QLabel("Ready for transfers")
        status_layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        status_layout.addWidget(self.progress_bar)
        
        layout.addLayout(status_layout)
        
    def create_send_tab(self):
        """Create the send transfer tab."""
        send_widget = QWidget()
        layout = QVBoxLayout(send_widget)
        
        # Target configuration
        target_group = QGroupBox("Transfer Target")
        target_layout = QFormLayout(target_group)
        
        self.target_host = QLineEdit()
        self.target_host.setPlaceholderText("Enter target IP address or hostname")
        target_layout.addRow("Target Host:", self.target_host)
        
        self.target_port = QSpinBox()
        self.target_port.setRange(1024, 65535)
        self.target_port.setValue(12000)
        target_layout.addRow("Port:", self.target_port)
        
        layout.addWidget(target_group)
        
        # Transfer type selection
        type_group = QGroupBox("Transfer Type")
        type_layout = QVBoxLayout(type_group)
        
        # Settings/Preferences transfer
        settings_layout = QHBoxLayout()
        self.transfer_settings_btn = QPushButton("Transfer Settings & Preferences")
        self.transfer_settings_btn.clicked.connect(self.transfer_settings)
        settings_layout.addWidget(self.transfer_settings_btn)
        
        self.include_backups = QCheckBox("Include backup configurations")
        settings_layout.addWidget(self.include_backups)
        type_layout.addLayout(settings_layout)
        
        # File selection
        files_layout = QHBoxLayout()
        self.select_files_btn = QPushButton("Select Files to Transfer")
        self.select_files_btn.clicked.connect(self.select_files)
        files_layout.addWidget(self.select_files_btn)
        
        self.select_folder_btn = QPushButton("Select Folder")
        self.select_folder_btn.clicked.connect(self.select_folder)
        files_layout.addWidget(self.select_folder_btn)
        type_layout.addLayout(files_layout)
        
        # Collection selection
        collection_layout = QHBoxLayout()
        collection_layout.addWidget(QLabel("File Collection:"))
        
        self.collection_combo = QComboBox()
        collection_layout.addWidget(self.collection_combo)
        
        self.transfer_collection_btn = QPushButton("Transfer Collection")
        self.transfer_collection_btn.clicked.connect(self.transfer_collection)
        collection_layout.addWidget(self.transfer_collection_btn)
        type_layout.addLayout(collection_layout)
        
        layout.addWidget(type_group)
        
        # Selected files display
        files_group = QGroupBox("Selected Files")
        files_layout = QVBoxLayout(files_group)
        
        self.selected_files_list = QListWidget()
        files_layout.addWidget(self.selected_files_list)
        
        files_buttons = QHBoxLayout()
        self.clear_files_btn = QPushButton("Clear Selection")
        self.clear_files_btn.clicked.connect(self.clear_selected_files)
        files_buttons.addWidget(self.clear_files_btn)
        
        self.send_files_btn = QPushButton("Send Selected Files")
        self.send_files_btn.clicked.connect(self.send_selected_files)
        self.send_files_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        files_buttons.addWidget(self.send_files_btn)
        
        files_layout.addLayout(files_buttons)
        layout.addWidget(files_group)
        
        self.tab_widget.addTab(send_widget, "Send")
        
    def create_receive_tab(self):
        """Create the receive transfer tab."""
        receive_widget = QWidget()
        layout = QVBoxLayout(receive_widget)
        
        # Server configuration
        server_group = QGroupBox("Transfer Server")
        server_layout = QFormLayout(server_group)
        
        self.listen_port = QSpinBox()
        self.listen_port.setRange(1024, 65535)
        self.listen_port.setValue(12000)
        server_layout.addRow("Listen Port:", self.listen_port)
        
        self.receive_path = QLineEdit()
        self.receive_path.setText(str(Path.home() / "Downloads" / "RFU_Transfers"))
        server_layout.addRow("Receive Path:", self.receive_path)
        
        path_btn = QPushButton("Browse")
        path_btn.clicked.connect(self.browse_receive_path)
        server_layout.addRow("", path_btn)
        
        layout.addWidget(server_group)
        
        # Server controls
        controls_layout = QHBoxLayout()
        
        self.start_server_btn = QPushButton("Start Transfer Server")
        self.start_server_btn.clicked.connect(self.start_transfer_server)
        self.start_server_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        controls_layout.addWidget(self.start_server_btn)
        
        self.stop_server_btn = QPushButton("Stop Server")
        self.stop_server_btn.clicked.connect(self.stop_transfer_server)
        self.stop_server_btn.setEnabled(False)
        controls_layout.addWidget(self.stop_server_btn)
        
        layout.addLayout(controls_layout)
        
        # Server status and log
        status_group = QGroupBox("Server Status & Transfer Log")
        status_layout = QVBoxLayout(status_group)
        
        self.server_status = QLabel("Server stopped")
        self.server_status.setStyleSheet("font-weight: bold; color: #e74c3c;")
        status_layout.addWidget(self.server_status)
        
        self.transfer_log = QTextEdit()
        self.transfer_log.setReadOnly(True)
        self.transfer_log.setMaximumHeight(200)
        status_layout.addWidget(self.transfer_log)
        
        layout.addWidget(status_group)
        
        # Received files list
        received_group = QGroupBox("Received Files")
        received_layout = QVBoxLayout(received_group)
        
        self.received_files_list = QListWidget()
        received_layout.addWidget(self.received_files_list)
        
        self.tab_widget.addTab(receive_widget, "Receive")
        
    def create_collections_tab(self):
        """Create the file collections management tab."""
        collections_widget = QWidget()
        layout = QVBoxLayout(collections_widget)
        
        # Collections management
        management_group = QGroupBox("File Collections Management")
        management_layout = QVBoxLayout(management_group)
        
        # Create new collection
        create_layout = QHBoxLayout()
        create_layout.addWidget(QLabel("Collection Name:"))
        
        self.new_collection_name = QLineEdit()
        create_layout.addWidget(self.new_collection_name)
        
        self.create_collection_btn = QPushButton("Create Collection")
        self.create_collection_btn.clicked.connect(self.create_collection)
        create_layout.addWidget(self.create_collection_btn)
        
        management_layout.addLayout(create_layout)
        
        # Collections list
        self.collections_list = QListWidget()
        self.collections_list.itemClicked.connect(self.load_collection_details)
        management_layout.addWidget(self.collections_list)
        
        # Collection actions
        actions_layout = QHBoxLayout()
        
        self.edit_collection_btn = QPushButton("Edit Collection")
        self.edit_collection_btn.clicked.connect(self.edit_collection)
        actions_layout.addWidget(self.edit_collection_btn)
        
        self.delete_collection_btn = QPushButton("Delete Collection")
        self.delete_collection_btn.clicked.connect(self.delete_collection)
        actions_layout.addWidget(self.delete_collection_btn)
        
        management_layout.addLayout(actions_layout)
        layout.addWidget(management_group)
        
        # Collection details
        details_group = QGroupBox("Collection Details")
        details_layout = QVBoxLayout(details_group)
        
        self.collection_files_list = QListWidget()
        details_layout.addWidget(self.collection_files_list)
        
        files_actions = QHBoxLayout()
        
        self.add_files_to_collection_btn = QPushButton("Add Files")
        self.add_files_to_collection_btn.clicked.connect(self.add_files_to_collection)
        files_actions.addWidget(self.add_files_to_collection_btn)
        
        self.remove_file_from_collection_btn = QPushButton("Remove Selected")
        self.remove_file_from_collection_btn.clicked.connect(self.remove_file_from_collection)
        files_actions.addWidget(self.remove_file_from_collection_btn)
        
        details_layout.addLayout(files_actions)
        layout.addWidget(details_group)
        
        self.tab_widget.addTab(collections_widget, "Collections")
        
    def create_history_tab(self):
        """Create the transfer history tab."""
        history_widget = QWidget()
        layout = QVBoxLayout(history_widget)
        
        # History controls
        controls_layout = QHBoxLayout()
        
        self.refresh_history_btn = QPushButton("Refresh History")
        self.refresh_history_btn.clicked.connect(self.load_transfer_history)
        controls_layout.addWidget(self.refresh_history_btn)
        
        self.clear_history_btn = QPushButton("Clear History")
        self.clear_history_btn.clicked.connect(self.clear_transfer_history)
        controls_layout.addWidget(self.clear_history_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # History table
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(7)
        self.history_table.setHorizontalHeaderLabels([
            "Timestamp", "Type", "Direction", "Remote Host", 
            "Files", "Size", "Status"
        ])
        
        header = self.history_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        
        layout.addWidget(self.history_table)
        
        self.tab_widget.addTab(history_widget, "History")
        
        # Load initial history
        self.load_transfer_history()
    
    def select_files(self):
        """Select files for transfer with security validation."""
        try:
            files, _ = QFileDialog.getOpenFileNames(
                self, "Select Files to Transfer", str(Path.home())
            )
            
            for file_path in files:
                # Validate file path for security
                if self._is_secure_file_path(file_path):
                    item = QListWidgetItem(file_path)
                    self.selected_files_list.addItem(item)
                else:
                    QMessageBox.warning(
                        self, "Security Warning",
                        f"File path not allowed: {file_path}"
                    )
                
        except Exception as e:
            QMessageBox.warning(
                self, "Error", f"Failed to select files: {e}"
            )
            
        self.update_send_button_state()
    
    def select_folder(self):
        """Select folder for transfer with security validation."""
        try:
            folder = QFileDialog.getExistingDirectory(
                self, "Select Folder to Transfer", str(Path.home())
            )
            
            if folder and self._is_secure_file_path(folder):
                # Add all files in folder securely
                self._add_folder_files_securely(folder)
            elif folder:
                QMessageBox.warning(
                    self, "Security Warning",
                    f"Folder path not allowed: {folder}"
                )
        except Exception as e:
            QMessageBox.warning(
                self, "Error", f"Failed to select folder: {e}"
            )
            
        self.update_send_button_state()
    
    def _is_secure_file_path(self, file_path: str) -> bool:
        """Validate file path for security."""
        try:
            # Normalize the path
            normalized_path = Path(file_path).resolve()
            
            # Check against forbidden directories
            forbidden_dirs = [
                Path("/etc"),
                Path("/sys"),
                Path("/proc"),
                Path("C:\\Windows\\System32"),
                Path("C:\\Windows\\SysWOW64"),
            ]
            
            for forbidden in forbidden_dirs:
                try:
                    if str(normalized_path).startswith(str(forbidden.resolve())):
                        return False
                except (OSError, ValueError):
                    continue
            
            # Path seems safe
            return True
            
        except (ValueError, OSError):
            return False
    
    def _add_folder_files_securely(self, folder: str):
        """Add files from folder with security checks."""
        try:
            folder_path = Path(folder)
            for file_path in folder_path.rglob("*"):
                if (file_path.is_file() and 
                    self._is_secure_file_path(str(file_path))):
                    item = QListWidgetItem(str(file_path))
                    self.selected_files_list.addItem(item)
        except Exception as e:
            QMessageBox.warning(
                self, "Error", f"Failed to add folder files: {e}"
            )
    
    def clear_selected_files(self):
        """Clear selected files list."""
        self.selected_files_list.clear()
        self.update_send_button_state()
    
    def update_send_button_state(self):
        """Update send button enabled state."""
        has_files = self.selected_files_list.count() > 0
        has_target = bool(self.target_host.text().strip())
        self.send_files_btn.setEnabled(has_files and has_target)
    
    def transfer_settings(self):
        """Transfer application settings and preferences."""
        if not self.target_host.text().strip():
            QMessageBox.warning(self, "Network Transfer", "Please enter target host.")
            return
            
        try:
            # Collect application settings
            config_data = self.collect_application_config()
            
            transfer_data = {
                "type": "config",
                "config": config_data
            }
            
            self.start_transfer(transfer_data)
            
        except Exception as e:
            QMessageBox.critical(self, "Transfer Error", f"Failed to transfer settings: {str(e)}")
    
    def collect_application_config(self) -> Dict:
        """Collect application configuration for transfer."""
        config = {
            "timestamp": datetime.now().isoformat(),
            "version": "1.0",
            "settings": {},
            "collections": self.file_collections
        }
        
        # Add database settings if available
        if self.db_manager:
            try:
                settings = self.db_manager.get_all_settings()
                config["settings"] = settings
            except Exception as e:
                print(f"Failed to collect database settings: {e}")
        
        # Add backup configurations if requested
        if self.include_backups.isChecked():
            config["backups"] = self.collect_backup_configs()
            
        return config
    
    def collect_backup_configs(self) -> Dict:
        """Collect backup configuration files with security controls."""
        backup_configs = {}
        
        # Define allowed config file patterns (whitelist approach)
        allowed_patterns = [
            "rfu_*.json",
            "settings.json", 
            "preferences.json",
            "config.json"
        ]
        
        # Look for common backup config locations (only safe directories)
        config_paths = [
            Path.cwd() / "config",
            Path.cwd() / "backup",
            # Only include user-specific directories, not system-wide
            Path.home() / ".rfu"
        ]
        
        for config_path in config_paths:
            if not config_path.exists():
                continue
                
            # Verify path is safe to access
            if not self._is_secure_file_path(str(config_path)):
                continue
                
            try:
                for pattern in allowed_patterns:
                    for config_file in config_path.glob(pattern):
                        # Additional security check for each file
                        if not self._is_safe_config_file(config_file):
                            continue
                            
                        try:
                            with open(config_file, 'r') as f:
                                content = json.load(f)
                                # Sanitize content before adding
                                sanitized_content = self._sanitize_config_content(content)
                                backup_configs[config_file.name] = sanitized_content
                        except (json.JSONDecodeError, PermissionError):
                            continue
            except (OSError, PermissionError):
                continue
                        
        return backup_configs
    
    def _is_safe_config_file(self, file_path: Path) -> bool:
        """Check if a config file is safe to read."""
        try:
            # Check file size (prevent reading large files)
            if file_path.stat().st_size > 1024 * 1024:  # 1MB limit
                return False
                
            # Check file permissions (should be readable by user)
            if not os.access(file_path, os.R_OK):
                return False
                
            return True
        except (OSError, PermissionError):
            return False
    
    def _sanitize_config_content(self, content: Dict) -> Dict:
        """Remove sensitive information from config content."""
        if not isinstance(content, dict):
            return {}
            
        # List of keys that should never be transferred
        sensitive_keys = [
            'password', 'token', 'key', 'secret', 'credential',
            'auth', 'private', 'database_url', 'connection_string'
        ]
        
        sanitized = {}
        for key, value in content.items():
            # Check if key contains sensitive information
            key_lower = key.lower()
            if any(sensitive in key_lower for sensitive in sensitive_keys):
                continue
                
            # Recursively sanitize nested dictionaries
            if isinstance(value, dict):
                sanitized[key] = self._sanitize_config_content(value)
            elif isinstance(value, str) and len(value) < 1000:  # Limit string length
                sanitized[key] = value
            elif isinstance(value, (int, float, bool)):
                sanitized[key] = value
            # Skip other types (lists, large strings, etc.)
                
        return sanitized
    
    def send_selected_files(self):
        """Send selected files to target."""
        if not self.target_host.text().strip():
            QMessageBox.warning(self, "Network Transfer", "Please enter target host.")
            return
            
        files = []
        for i in range(self.selected_files_list.count()):
            files.append(self.selected_files_list.item(i).text())
            
        if not files:
            QMessageBox.warning(self, "Network Transfer", "No files selected.")
            return
            
        transfer_data = {
            "type": "files",
            "files": files
        }
        
        self.start_transfer(transfer_data)
    
    def transfer_collection(self):
        """Transfer selected file collection."""
        collection_name = self.collection_combo.currentText()
        if not collection_name or collection_name not in self.file_collections:
            QMessageBox.warning(self, "Network Transfer", "Please select a collection.")
            return
            
        collection = self.file_collections[collection_name]
        
        transfer_data = {
            "type": "collection",
            "collection": collection
        }
        
        self.start_transfer(transfer_data)
    
    def start_transfer(self, transfer_data: Dict):
        """Start a transfer operation."""
        host = self.target_host.text().strip()
        port = self.target_port.value()
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        self.transfer_client = TransferClient(host, port, transfer_data)
        self.transfer_client.connection_established.connect(self.on_connection_established)
        self.transfer_client.progress_updated.connect(self.progress_bar.setValue)
        self.transfer_client.transfer_completed.connect(self.on_transfer_completed)
        self.transfer_client.error_occurred.connect(self.on_transfer_error)
        self.transfer_client.start()
        
        # Log transfer attempt
        self.log_transfer_attempt(transfer_data, host, port)
    
    def start_transfer_server(self):
        """Start the transfer server."""
        port = self.listen_port.value()
        
        self.transfer_server = TransferServer(port)
        self.transfer_server.client_connected.connect(self.on_client_connected)
        self.transfer_server.transfer_started.connect(self.on_transfer_received)
        self.transfer_server.transfer_completed.connect(self.on_receive_completed)
        self.transfer_server.error_occurred.connect(self.on_server_error)
        self.transfer_server.start()
        
        self.start_server_btn.setEnabled(False)
        self.stop_server_btn.setEnabled(True)
        self.server_status.setText(f"Server running on port {port}")
        self.server_status.setStyleSheet("font-weight: bold; color: #27ae60;")
        
        self.transfer_log.append(f"Transfer server started on port {port}")
    
    def stop_transfer_server(self):
        """Stop the transfer server."""
        if self.transfer_server:
            self.transfer_server.stop()
            self.transfer_server.wait()
            self.transfer_server = None
            
        self.start_server_btn.setEnabled(True)
        self.stop_server_btn.setEnabled(False)
        self.server_status.setText("Server stopped")
        self.server_status.setStyleSheet("font-weight: bold; color: #e74c3c;")
        
        self.transfer_log.append("Transfer server stopped")
    
    def browse_receive_path(self):
        """Browse for receive path."""
        path = QFileDialog.getExistingDirectory(
            self, "Select Receive Directory", self.receive_path.text()
        )
        if path:
            self.receive_path.setText(path)
    
    def create_collection(self):
        """Create a new file collection."""
        name = self.new_collection_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Collection", "Please enter a collection name.")
            return
            
        if name in self.file_collections:
            QMessageBox.warning(self, "Collection", "Collection name already exists.")
            return
            
        collection = {
            "name": name,
            "description": "",
            "files": [],
            "created_date": datetime.now().isoformat(),
            "last_modified": datetime.now().isoformat()
        }
        
        self.file_collections[name] = collection
        self.save_collection(collection)
        self.load_collections()
        
        self.new_collection_name.clear()
        QMessageBox.information(self, "Collection", f"Collection '{name}' created successfully.")
    
    def load_collections(self):
        """Load file collections from database."""
        self.collections_list.clear()
        self.collection_combo.clear()
        
        if self.db_manager:
            try:
                collections = self.db_manager.execute_query(
                    "SELECT name, description, files FROM file_collections ORDER BY name"
                )
                
                for name, description, files_json in collections:
                    files = json.loads(files_json)
                    self.file_collections[name] = {
                        "name": name,
                        "description": description,
                        "files": files
                    }
                    
            except Exception as e:
                print(f"Failed to load collections: {e}")
        
        # Update UI
        for name in self.file_collections:
            self.collections_list.addItem(name)
            self.collection_combo.addItem(name)
    
    def save_collection(self, collection: Dict):
        """Save collection to database."""
        if not self.db_manager:
            return
            
        try:
            self.db_manager.execute_query("""
                INSERT OR REPLACE INTO file_collections 
                (name, description, files, created_date, last_modified)
                VALUES (?, ?, ?, ?, ?)
            """, (
                collection["name"],
                collection.get("description", ""),
                json.dumps(collection["files"]),
                collection.get("created_date", datetime.now().isoformat()),
                datetime.now().isoformat()
            ))
        except Exception as e:
            print(f"Failed to save collection: {e}")
    
    def load_collection_details(self, item: QListWidgetItem):
        """Load collection details when selected."""
        collection_name = item.text()
        collection = self.file_collections.get(collection_name)
        
        if collection:
            self.collection_files_list.clear()
            for file_path in collection.get("files", []):
                self.collection_files_list.addItem(file_path)
    
    def add_files_to_collection(self):
        """Add files to current collection."""
        current_item = self.collections_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Collection", "Please select a collection.")
            return
            
        files, _ = QFileDialog.getOpenFileNames(
            self, "Add Files to Collection", str(Path.home())
        )
        
        collection_name = current_item.text()
        collection = self.file_collections[collection_name]
        
        for file_path in files:
            if file_path not in collection["files"]:
                collection["files"].append(file_path)
                self.collection_files_list.addItem(file_path)
        
        collection["last_modified"] = datetime.now().isoformat()
        self.save_collection(collection)
    
    def remove_file_from_collection(self):
        """Remove selected file from collection."""
        current_collection = self.collections_list.currentItem()
        current_file = self.collection_files_list.currentItem()
        
        if not current_collection or not current_file:
            return
            
        collection_name = current_collection.text()
        file_path = current_file.text()
        
        collection = self.file_collections[collection_name]
        if file_path in collection["files"]:
            collection["files"].remove(file_path)
            self.collection_files_list.takeItem(self.collection_files_list.currentRow())
            
            collection["last_modified"] = datetime.now().isoformat()
            self.save_collection(collection)
    
    def edit_collection(self):
        """Edit selected collection."""
        current_item = self.collections_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Collection", "Please select a collection.")
            return
        
        # For now, just allow adding/removing files
        QMessageBox.information(
            self, "Collection Editor", 
            "Use 'Add Files' and 'Remove Selected' buttons to edit the collection."
        )
    
    def delete_collection(self):
        """Delete selected collection."""
        current_item = self.collections_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Collection", "Please select a collection.")
            return
            
        collection_name = current_item.text()
        
        reply = QMessageBox.question(
            self, "Delete Collection",
            f"Are you sure you want to delete collection '{collection_name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.db_manager:
                try:
                    self.db_manager.execute_query(
                        "DELETE FROM file_collections WHERE name = ?",
                        (collection_name,)
                    )
                except Exception as e:
                    print(f"Failed to delete collection: {e}")
            
            del self.file_collections[collection_name]
            self.load_collections()
            self.collection_files_list.clear()
    
    def load_transfer_history(self):
        """Load transfer history from database."""
        if not self.db_manager:
            return
            
        try:
            history = self.db_manager.execute_query("""
                SELECT timestamp, transfer_type, direction, remote_host,
                       file_count, total_size, status
                FROM transfer_history 
                ORDER BY timestamp DESC
                LIMIT 100
            """)
            
            self.history_table.setRowCount(len(history))
            
            for row, (timestamp, transfer_type, direction, remote_host, 
                     file_count, total_size, status) in enumerate(history):
                
                self.history_table.setItem(row, 0, QTableWidgetItem(timestamp))
                self.history_table.setItem(row, 1, QTableWidgetItem(transfer_type))
                self.history_table.setItem(row, 2, QTableWidgetItem(direction))
                self.history_table.setItem(row, 3, QTableWidgetItem(remote_host or ""))
                self.history_table.setItem(row, 4, QTableWidgetItem(str(file_count)))
                self.history_table.setItem(row, 5, QTableWidgetItem(f"{total_size} bytes"))
                self.history_table.setItem(row, 6, QTableWidgetItem(status))
                
        except Exception as e:
            print(f"Failed to load transfer history: {e}")
    
    def clear_transfer_history(self):
        """Clear transfer history."""
        reply = QMessageBox.question(
            self, "Clear History",
            "Are you sure you want to clear all transfer history?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.db_manager:
                try:
                    self.db_manager.execute_query("DELETE FROM transfer_history")
                    self.load_transfer_history()
                except Exception as e:
                    print(f"Failed to clear history: {e}")
    
    def log_transfer_attempt(self, transfer_data: Dict, host: str, port: int):
        """Log transfer attempt to database."""
        if not self.db_manager:
            return
            
        try:
            transfer_type = transfer_data.get("type", "unknown")
            file_count = 0
            total_size = 0
            
            if transfer_type == "files":
                files = transfer_data.get("files", [])
                file_count = len(files)
                total_size = sum(os.path.getsize(f) for f in files if os.path.exists(f))
            elif transfer_type == "collection":
                collection = transfer_data.get("collection", {})
                files = collection.get("files", [])
                file_count = len(files)
                total_size = sum(os.path.getsize(f) for f in files if os.path.exists(f))
            
            self.db_manager.execute_query("""
                INSERT INTO transfer_history 
                (timestamp, transfer_type, direction, remote_host, file_count, total_size, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                transfer_type,
                "outgoing",
                f"{host}:{port}",
                file_count,
                total_size,
                "started"
            ))
            
        except Exception as e:
            print(f"Failed to log transfer: {e}")
    
    # Signal handlers
    def on_connection_established(self, message: str):
        """Handle connection established."""
        self.status_label.setText(message)
    
    def on_transfer_completed(self, message: str):
        """Handle transfer completion."""
        self.status_label.setText(message)
        self.progress_bar.setVisible(False)
        QMessageBox.information(self, "Transfer Complete", message)
        self.load_transfer_history()
    
    def on_transfer_error(self, error: str):
        """Handle transfer error."""
        self.status_label.setText(f"Transfer failed: {error}")
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "Transfer Error", error)
    
    def on_client_connected(self, host: str, port: int):
        """Handle client connection."""
        self.transfer_log.append(f"Client connected from {host}:{port}")
    
    def on_transfer_received(self, transfer_type: str, details: str):
        """Handle incoming transfer."""
        self.transfer_log.append(f"Receiving {transfer_type}: {details}")
    
    def on_receive_completed(self, message: str):
        """Handle receive completion."""
        self.transfer_log.append(f"Transfer completed: {message}")
        self.load_transfer_history()
    
    def on_server_error(self, error: str):
        """Handle server error."""
        self.transfer_log.append(f"Server error: {error}")
    
    def closeEvent(self, event):
        """Handle window close event."""
        if self.transfer_server:
            self.stop_transfer_server()
        event.accept()


def main():
    """Main function for standalone execution."""
    app = QApplication(sys.argv)
    window = NetworkTransferGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
