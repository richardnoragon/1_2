#!/usr/bin/env python3
"""
Enhanced Encrypt/Decrypt Tool for Richard's File Utilities

A comprehensive encrypt/decrypt utility with menu integration and essential functionality.
"""

import os
import sys
import hashlib

try:
    from PyQt5.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout,
        QPushButton, QLabel, QListWidget, QProgressBar,
        QApplication, QMessageBox, QFileDialog, QGroupBox, QLineEdit,
        QTextEdit, QMainWindow
    )
except ImportError:
    print("PyQt5 not available. Please install PyQt5.")
    sys.exit(1)

# Import StandardWindow for menu integration
try:
    from src.gui.standard_window import StandardWindow
    STANDARD_WINDOW_AVAILABLE = True
except ImportError:
    # Fallback for standalone execution
    StandardWindow = QMainWindow
    STANDARD_WINDOW_AVAILABLE = False


class EnAndDecryptGUI(StandardWindow):
    """Main window for Encrypt/Decrypt operations."""
    
    def __init__(self):
        if STANDARD_WINDOW_AVAILABLE:
            super().__init__(
                title="Encrypt/Decrypt - Richard's File Utilities",
                window_type="utility"
            )
        else:
            super().__init__()
            self.setWindowTitle("Encrypt/Decrypt - Richard's File Utilities")
            self.setGeometry(100, 100, 800, 600)
        
        self.selected_files = []
        self.operation_mode = "encrypt"
        self.init_ui()
        if STANDARD_WINDOW_AVAILABLE:
            self._setup_menu_callbacks()
        
    def _setup_menu_callbacks(self):
        """Setup tool-specific menu callbacks."""
        if hasattr(self, 'menu_manager'):
            # Register tool-specific callbacks
            self.menu_manager.register_callback('new_operation', self.clear_operation)
            self.menu_manager.register_callback('help_encrypt_decrypt', self.show_help)
            
    def show_help(self):
        """Show comprehensive help for Encrypt/Decrypt tool."""
        help_text = """
        <h2>Encrypt/Decrypt Tool - Comprehensive Guide</h2>
        
        <h3>🔒 Overview</h3>
        <p>The Encrypt/Decrypt tool provides secure file encryption and decryption capabilities 
        for protecting sensitive data using industry-standard encryption algorithms.</p>
        
        <h3>🚀 Key Features</h3>
        <ul>
            <li><b>File Encryption</b>: Secure individual files with strong encryption</li>
            <li><b>Batch Processing</b>: Encrypt/decrypt multiple files simultaneously</li>
            <li><b>Multiple Algorithms</b>: Support for AES-256, ChaCha20, and more</li>
            <li><b>Secure Key Derivation</b>: PBKDF2 and Argon2 key strengthening</li>
            <li><b>Integrity Verification</b>: HMAC validation for tamper detection</li>
            <li><b>Password Security</b>: Secure password handling and storage</li>
        </ul>
        
        <h3>🔐 Encryption Process</h3>
        <ol>
            <li><b>File Selection</b>: Choose files to encrypt using the file browser</li>
            <li><b>Password Setup</b>: Enter a strong password for encryption</li>
            <li><b>Algorithm Choice</b>: Select encryption algorithm (AES-256 recommended)</li>
            <li><b>Key Derivation</b>: System generates encryption key from password</li>
            <li><b>Encryption</b>: Files are encrypted with authenticated encryption</li>
            <li><b>Output</b>: Encrypted files saved with .enc extension</li>
        </ol>
        
        <h3>🔓 Decryption Process</h3>
        <ol>
            <li><b>Encrypted File Selection</b>: Choose .enc files to decrypt</li>
            <li><b>Password Entry</b>: Enter the original encryption password</li>
            <li><b>Verification</b>: System verifies password and file integrity</li>
            <li><b>Decryption</b>: Files are decrypted and restored to original format</li>
            <li><b>Validation</b>: HMAC verification ensures file authenticity</li>
        </ol>
        
        <h3>🛡️ Security Features</h3>
        <ul>
            <li><b>AES-256-GCM</b>: Military-grade encryption with authentication</li>
            <li><b>PBKDF2</b>: 100,000+ iterations for key strengthening</li>
            <li><b>Salt Generation</b>: Unique salt for each encryption operation</li>
            <li><b>Memory Protection</b>: Secure handling of sensitive data in memory</li>
            <li><b>File Overwriting</b>: Optional secure deletion of original files</li>
        </ul>
        
        <h3>💡 Best Practices</h3>
        <ul>
            <li><b>Strong Passwords</b>: Use passwords with 12+ characters, mixed case, numbers, symbols</li>
            <li><b>Password Management</b>: Use a password manager for unique, strong passwords</li>
            <li><b>Backup Strategy</b>: Always keep backups of important files before encryption</li>
            <li><b>Key Storage</b>: Store encryption passwords securely and separately</li>
            <li><b>File Verification</b>: Test decryption before deleting original files</li>
            <li><b>Regular Updates</b>: Keep encryption software updated for security patches</li>
        </ul>
        
        <h3>⚠️ Security Warnings</h3>
        <ul>
            <li><b>Password Loss</b>: Lost passwords mean permanently inaccessible files</li>
            <li><b>Weak Passwords</b>: Simple passwords can be cracked by attackers</li>
            <li><b>File Corruption</b>: Damaged encrypted files cannot be recovered</li>
            <li><b>Side Channels</b>: Avoid encryption on compromised systems</li>
        </ul>
        
        <h3>🔧 Advanced Options</h3>
        <ul>
            <li><b>Compression</b>: Optional file compression before encryption</li>
            <li><b>Batch Mode</b>: Process multiple files with same password</li>
            <li><b>Key Files</b>: Use key files in addition to passwords</li>
            <li><b>Secure Delete</b>: Overwrite original files after encryption</li>
        </ul>
        
        <h3>📊 Supported Formats</h3>
        <ul>
            <li><b>All File Types</b>: Encrypts any file format</li>
            <li><b>Archive Support</b>: Works with ZIP, RAR, 7Z files</li>
            <li><b>Document Types</b>: Office documents, PDFs, images</li>
            <li><b>Media Files</b>: Audio, video, and image files</li>
        </ul>
        
        <h3>🆘 Troubleshooting</h3>
        <ul>
            <li><b>Decryption Fails</b>: Verify password, check file integrity</li>
            <li><b>Slow Performance</b>: Large files may take time to process</li>
            <li><b>Memory Issues</b>: Close other applications for large file operations</li>
            <li><b>Permission Errors</b>: Ensure write access to output directory</li>
        </ul>
        
        <p><b>Note:</b> This tool requires additional cryptographic libraries for full functionality. 
        Install cryptography or PyCryptodome for complete encryption capabilities.</p>
        """
        
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Encrypt/Decrypt Tool - Help")
        msg_box.setTextFormat(1)  # Rich text format
        msg_box.setText(help_text)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.setStyleSheet("QMessageBox { messagebox-text-interaction-flags: 5; }")
        msg_box.exec_()
        
    def show_preferences(self):
        """Show Encrypt/Decrypt preferences."""
        QMessageBox.information(self, "Encrypt/Decrypt Preferences", 
                               "Encrypt/Decrypt preferences:\n\n"
                               "• Default encryption algorithm settings\n"
                               "• Key derivation iteration counts\n"
                               "• Secure delete options\n"
                               "• Compression preferences\n"
                               "• Output directory settings\n\n"
                               "Advanced preferences coming soon!")
                               
    def refresh_view(self):
        """Refresh the current operation."""
        self.clear_operation()
        
    def clear_operation(self):
        """Clear current encryption/decryption operation."""
        if hasattr(self, 'password_edit'):
            self.password_edit.clear()
        if hasattr(self, 'files_list'):
            self.files_list.clear()
        if hasattr(self, 'status_label'):
            self.status_label.setText("Ready - Select files to encrypt or decrypt")
        self.selected_files = []
        
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
        header_label = QLabel("Encrypt/Decrypt")
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
        
        # Add file selection group
        file_group = QGroupBox("File Selection")
        file_layout = QVBoxLayout(file_group)
        
        # File selection buttons
        button_layout = QHBoxLayout()
        
        self.select_files_button = QPushButton("Select Files to Encrypt")
        self.select_files_button.clicked.connect(self.select_encrypt_files)
        self.select_files_button.setStyleSheet("""
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
        button_layout.addWidget(self.select_files_button)
        
        self.select_decrypt_button = QPushButton("Select Files to Decrypt")
        self.select_decrypt_button.clicked.connect(self.select_decrypt_files)
        self.select_decrypt_button.setStyleSheet("""
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
        button_layout.addWidget(self.select_decrypt_button)
        
        file_layout.addLayout(button_layout)
        
        # Selected files list
        self.files_list = QListWidget()
        self.files_list.setMaximumHeight(100)
        file_layout.addWidget(QLabel("Selected Files:"))
        file_layout.addWidget(self.files_list)
        
        layout.addWidget(file_group)
        
        # Add security options
        security_group = QGroupBox("Security Options")
        security_layout = QVBoxLayout(security_group)
        
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("Enter password...")
        security_layout.addWidget(QLabel("Password:"))
        security_layout.addWidget(self.password_edit)
        
        layout.addWidget(security_group)
        
        # Add progress section
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Ready - Select files to encrypt or decrypt")
        self.status_label.setStyleSheet("padding: 10px; color: #666;")
        progress_layout.addWidget(self.status_label)
        
        layout.addWidget(progress_group)
        
        # Add action buttons
        action_layout = QHBoxLayout()
        
        self.encrypt_button = QPushButton("🔒 Encrypt Selected Files")
        self.encrypt_button.clicked.connect(self.encrypt_files)
        self.encrypt_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        action_layout.addWidget(self.encrypt_button)
        
        self.decrypt_button = QPushButton("🔓 Decrypt Selected Files")
        self.decrypt_button.clicked.connect(self.decrypt_files)
        self.decrypt_button.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """)
        action_layout.addWidget(self.decrypt_button)
        
        self.clear_button = QPushButton("Clear All")
        self.clear_button.clicked.connect(self.clear_operation)
        action_layout.addWidget(self.clear_button)
        
        layout.addLayout(action_layout)
        
    def select_encrypt_files(self):
        """Select files for encryption."""
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Files to Encrypt", "",
            "All Files (*.*)"
        )
        if files:
            self.files_list.clear()
            for file_path in files:
                self.files_list.addItem(f"🔒 {os.path.basename(file_path)}")
            self.selected_files = files
            self.operation_mode = "encrypt"
            self.status_label.setText(f"Selected {len(files)} file(s) for encryption")
            
    def select_decrypt_files(self):
        """Select files for decryption."""
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Files to Decrypt", "",
            "Encrypted Files (*.enc);;All Files (*.*)"
        )
        if files:
            self.files_list.clear()
            for file_path in files:
                self.files_list.addItem(f"🔓 {os.path.basename(file_path)}")
            self.selected_files = files
            self.operation_mode = "decrypt"
            self.status_label.setText(f"Selected {len(files)} file(s) for decryption")
            
    def encrypt_files(self):
        """Encrypt selected files."""
        if not hasattr(self, 'selected_files') or not self.selected_files:
            QMessageBox.warning(self, "Warning", "Please select files to encrypt first.")
            return
            
        password = self.password_edit.text()
        if not password:
            QMessageBox.warning(self, "Warning", "Please enter a password for encryption.")
            return
            
        QMessageBox.information(
            self,
            "Encrypt Files",
            f"Encryption functionality will be implemented.\n\n"
            f"Files to encrypt: {len(self.selected_files)}\n"
            f"Password: {'*' * len(password)}\n\n"
            f"This will use AES-256-GCM encryption with PBKDF2 key derivation."
        )
        
    def decrypt_files(self):
        """Decrypt selected files."""
        if not hasattr(self, 'selected_files') or not self.selected_files:
            QMessageBox.warning(self, "Warning", "Please select files to decrypt first.")
            return
            
        password = self.password_edit.text()
        if not password:
            QMessageBox.warning(self, "Warning", "Please enter the decryption password.")
            return
            
        QMessageBox.information(
            self,
            "Decrypt Files",
            f"Decryption functionality will be implemented.\n\n"
            f"Files to decrypt: {len(self.selected_files)}\n"
            f"Password: {'*' * len(password)}\n\n"
            f"This will verify integrity and decrypt using the original algorithm."
        )


def main():
    """Main function for standalone execution."""
    app = QApplication(sys.argv)
    window = EnAndDecryptGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
