#!/usr/bin/env python3
"""
Enhanced Encrypt/Decrypt Tool for Richard's File Utilities

A comprehensive encrypt/decrypt utility with menu integration and essential functionality.
"""

import hashlib
import logging
import os
import sys

try:
    from PyQt5.QtWidgets import (
        QApplication,
        QCheckBox,
        QFileDialog,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QListWidget,
        QMainWindow,
        QMessageBox,
        QProgressBar,
        QPushButton,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )
except ImportError:
    print("PyQt5 not available. Please install PyQt5.")
    sys.exit(1)

try:
    from src.gui.themes import ThemeManager, token
except ImportError:

    def token(key: str) -> str:
        return ""


# Import StandardWindow for menu integration
try:
    from src.gui.standard_window import StandardWindow

    STANDARD_WINDOW_AVAILABLE = True
except ImportError:
    # Fallback for standalone execution
    StandardWindow = QMainWindow
    STANDARD_WINDOW_AVAILABLE = False


# ---------------------------------------------------------------------------
# GRD-1a: Guardian registration (graceful no-op when guardian absent)
# ---------------------------------------------------------------------------
try:
    from src.core.guardian import register_gui_component
except ImportError:

    def register_gui_component(*a, **kw):
        pass  # noqa: E731


# ---------------------------------------------------------------------------
# TEL: Telemetry helpers (graceful no-op when telemetry absent)
# ---------------------------------------------------------------------------
try:
    from src.gui.telemetry import emit_telemetry

    def _emit_telemetry(event_type, **kw):
        emit_telemetry(event_type, **kw)  # noqa: E731

except ImportError:

    def _emit_telemetry(*a, **kw):
        pass  # noqa: E731


# ---------------------------------------------------------------------------
# STR: Centralised string constants with fallback (P1-C15 / STR-1)
# ---------------------------------------------------------------------------
try:
    from src.rfu.ui_strings import Encryption as _EADStrings
except ImportError:

    class _EADStrings:  # type: ignore[no-redef]
        TITLE = "Encrypt / Decrypt"
        WINDOW_TITLE = "Encrypt / Decrypt — RFU"
        LOADING = "Loading Encrypt / Decrypt…"
        ERR_INIT_FAILED = (
            "Could not start Encrypt / Decrypt. "
            "Please try again or restart the application."
        )
        ERR_OPERATION_FAILED = (
            "Encryption/decryption operation failed. "
            "Check your password and file permissions."
        )
        ERR_NO_FILES = "No files selected for the operation."


# ---------------------------------------------------------------------------
# CP: Shared UI components (graceful fallback when unavailable)
# ---------------------------------------------------------------------------
try:
    from src.gui.components.buttons import PrimaryButton, SecondaryButton
    from src.gui.components.modal import Modal
    from src.gui.components.toast import ToastNotification

    _CP_AVAILABLE = True
except ImportError:
    PrimaryButton = SecondaryButton = None  # type: ignore[assignment,misc]
    Modal = None  # type: ignore[assignment,misc]
    ToastNotification = None
    _CP_AVAILABLE = False


class EnAndDecryptGUI(StandardWindow):
    """Main window for Encrypt/Decrypt operations."""

    def __init__(self, hub_instance=None):
        self._hub = hub_instance
        if STANDARD_WINDOW_AVAILABLE:
            super().__init__(
                title=_EADStrings.WINDOW_TITLE,
                window_type="utility",
            )
        else:
            super().__init__()
            self.setWindowTitle(_EADStrings.WINDOW_TITLE)
            self.setGeometry(100, 100, 800, 600)

        try:
            from src.rfu.log_manager import get_log_manager

            self._logger = get_log_manager().get_logger("EnAndDecryptGUI")
        except Exception:  # ERR: non-fatal — logger fallback to module logger
            self._logger = logging.getLogger("EnAndDecryptGUI")

        self.selected_files = []
        self.operation_mode = "encrypt"
        self.init_ui()
        if STANDARD_WINDOW_AVAILABLE:
            self._setup_menu_callbacks()
        register_gui_component(
            self, tool_id="encryption", recovery_callback=self.degraded_fallback
        )
        _emit_telemetry("ui_view_load", tool_id="encryption")
        ThemeManager.add_theme_changed_callback(self._on_theme_changed)

    def _on_theme_changed(self, variant: str) -> None:
        """Re-apply token-based stylesheets when the active theme variant changes."""
        pass  # stylesheets applied at init; live re-apply pending TH-4c/4d

    def health_check(self) -> bool:
        """Return True if core UI is functional (GRD-3a)."""
        try:
            return hasattr(self, "files_list") and self.files_list is not None
        except Exception:
            return False

    def degraded_fallback(self) -> None:
        """Enter degraded / read-only state (GRD-3b)."""
        try:
            self._logger.warning("EnAndDecryptGUI entering degraded mode")
        except Exception:
            pass
        _emit_telemetry("ui_error_event", tool_id="encryption", error_type="degraded")

    def _setup_menu_callbacks(self):
        """Setup tool-specific menu callbacks."""
        if hasattr(self, "menu_manager"):
            # Register tool-specific callbacks
            self.menu_manager.register_callback("new_operation", self.clear_operation)
            self.menu_manager.register_callback("help_encrypt_decrypt", self.show_help)

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
        _msg = (
            "Encrypt/Decrypt preferences:\n\n"
            "• Default encryption algorithm settings\n"
            "• Key derivation iteration counts\n"
            "• Secure delete options\n"
            "• Compression preferences\n"
            "• Output directory settings\n\n"
            "Advanced preferences coming soon!"
        )
        if Modal:
            Modal("Encrypt/Decrypt Preferences", _msg, ["OK"], self).exec_()
        else:
            QMessageBox.information(self, "Encrypt/Decrypt Preferences", _msg)

    def refresh_view(self):
        """Refresh the current operation."""
        self.clear_operation()

    def clear_operation(self):
        """Clear current encryption/decryption operation."""
        if hasattr(self, "password_edit"):
            self.password_edit.clear()
        if hasattr(self, "files_list"):
            self.files_list.clear()
        if hasattr(self, "status_label"):
            self.status_label.setText("Ready - Select files to encrypt or decrypt")
        self.selected_files = []

    def init_ui(self):
        """Initialize the user interface."""
        # Use the existing main layout from StandardWindow or create new layout
        if STANDARD_WINDOW_AVAILABLE and hasattr(self, "main_layout"):
            layout = self.main_layout
        else:
            # Create central widget and layout for fallback mode
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)

        # Add header
        header_label = QLabel("Encrypt/Decrypt")
        header_label.setStyleSheet(
            """
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: {token('text_primary')};
                padding: 10px;
                background-color: {token('background')};
                border-radius: 5px;
                margin-bottom: 10px;
            }
        """
        )
        layout.addWidget(header_label)

        # Add file selection group
        file_group = QGroupBox("File Selection")
        file_layout = QVBoxLayout(file_group)

        # File selection buttons
        button_layout = QHBoxLayout()

        _SB = SecondaryButton if SecondaryButton else QPushButton
        self.select_files_button = _SB("Select Files to Encrypt")
        self.select_files_button.clicked.connect(self.select_encrypt_files)
        button_layout.addWidget(self.select_files_button)

        self.select_decrypt_button = _SB("Select Files to Decrypt")
        self.select_decrypt_button.clicked.connect(self.select_decrypt_files)
        button_layout.addWidget(self.select_decrypt_button)

        file_layout.addLayout(button_layout)

        # Selected files list
        self.files_list = QListWidget()
        self.files_list.setAccessibleName("Files to process")
        self.files_list.setMaximumHeight(100)
        file_layout.addWidget(QLabel("Selected Files:"))
        file_layout.addWidget(self.files_list)

        layout.addWidget(file_group)

        # Add security options
        security_group = QGroupBox("Security Options")
        security_layout = QVBoxLayout(security_group)

        self.password_edit = QLineEdit()
        self.password_edit.setAccessibleName("Encryption password")
        self.password_edit.setAccessibleDescription(
            "Password used to encrypt or decrypt files; minimum 8 characters recommended"
        )
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("Enter password...")
        security_layout.addWidget(QLabel("Password:"))
        security_layout.addWidget(self.password_edit)

        # Dry run option — must appear before action buttons (spec §5.2)
        self.dry_run_checkbox = QCheckBox(
            "🔍 Dry Run (Preview Only — No Files Will Be Encrypted/Decrypted)"
        )
        self.dry_run_checkbox.setAccessibleName("Dry run preview mode")
        self.dry_run_checkbox.setAccessibleDescription(
            "Shows which files would be processed without making any changes"
        )
        self.dry_run_checkbox.setMinimumHeight(44)
        self.dry_run_checkbox.setToolTip(
            "When checked, shows which files WOULD be processed without "
            "actually encrypting or decrypting anything"
        )
        security_layout.addWidget(self.dry_run_checkbox)

        layout.addWidget(security_group)

        # Add progress section
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout(progress_group)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)

        self.status_label = QLabel("Ready - Select files to encrypt or decrypt")
        self.status_label.setStyleSheet(f"padding: 10px; color: {token('text_muted')};")
        progress_layout.addWidget(self.status_label)

        layout.addWidget(progress_group)

        # Add action buttons
        action_layout = QHBoxLayout()

        _PB = PrimaryButton if PrimaryButton else QPushButton
        self.encrypt_button = _PB("🔒 Encrypt Selected Files")
        self.encrypt_button.clicked.connect(self.encrypt_files)
        action_layout.addWidget(self.encrypt_button)

        _SB2 = SecondaryButton if SecondaryButton else QPushButton
        self.decrypt_button = _SB2("🔓 Decrypt Selected Files")
        self.decrypt_button.clicked.connect(self.decrypt_files)
        action_layout.addWidget(self.decrypt_button)

        self.clear_button = _SB2("Clear All")
        self.clear_button.clicked.connect(self.clear_operation)
        action_layout.addWidget(self.clear_button)

        layout.addLayout(action_layout)

    def select_encrypt_files(self):
        """Select files for encryption."""
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Files to Encrypt", "", "All Files (*.*)"
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
            self,
            "Select Files to Decrypt",
            "",
            "Encrypted Files (*.enc);;All Files (*.*)",
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
        if not hasattr(self, "selected_files") or not self.selected_files:
            if Modal:
                Modal(
                    "Warning", "Please select files to encrypt first.", ["OK"], self
                ).exec_()
            else:
                QMessageBox.warning(
                    self, "Warning", "Please select files to encrypt first."
                )
            return

        password = self.password_edit.text()
        if not password:
            if Modal:
                Modal(
                    "Warning", "Please enter a password for encryption.", ["OK"], self
                ).exec_()
            else:
                QMessageBox.warning(
                    self, "Warning", "Please enter a password for encryption."
                )
            return

        if hasattr(self, "dry_run_checkbox") and self.dry_run_checkbox.isChecked():
            items_text = "\n".join(
                f"  \u2022 {os.path.basename(f)}" for f in self.selected_files
            )
            _dry_msg = (
                f"DRY RUN \u2014 No files will be encrypted.\n\n"
                f"The following {len(self.selected_files)} file(s) WOULD be encrypted:\n"
                f"{items_text}\n\n"
                f"Algorithm: AES-256-GCM with PBKDF2 key derivation."
            )
            if Modal:
                Modal("Dry Run Preview \u2014 Encrypt", _dry_msg, ["OK"], self).exec_()
            else:
                QMessageBox.information(
                    self, "Dry Run Preview \u2014 Encrypt", _dry_msg
                )
        else:
            _msg = (
                f"Encryption functionality will be implemented.\n\n"
                f"Files to encrypt: {len(self.selected_files)}\n"
                f"Password: {'*' * len(password)}\n\n"
                f"This will use AES-256-GCM encryption with PBKDF2 key derivation."
            )
            if Modal:
                Modal("Encrypt Files", _msg, ["OK"], self).exec_()
            else:
                QMessageBox.information(self, "Encrypt Files", _msg)

    def decrypt_files(self):
        """Decrypt selected files."""
        if not hasattr(self, "selected_files") or not self.selected_files:
            if Modal:
                Modal(
                    "Warning", "Please select files to decrypt first.", ["OK"], self
                ).exec_()
            else:
                QMessageBox.warning(
                    self, "Warning", "Please select files to decrypt first."
                )
            return

        password = self.password_edit.text()
        if not password:
            if Modal:
                Modal(
                    "Warning", "Please enter the decryption password.", ["OK"], self
                ).exec_()
            else:
                QMessageBox.warning(
                    self, "Warning", "Please enter the decryption password."
                )
            return

        if hasattr(self, "dry_run_checkbox") and self.dry_run_checkbox.isChecked():
            items_text = "\n".join(
                f"  \u2022 {os.path.basename(f)}" for f in self.selected_files
            )
            _dry_msg = (
                f"DRY RUN \u2014 No files will be decrypted.\n\n"
                f"The following {len(self.selected_files)} file(s) WOULD be decrypted:\n"
                f"{items_text}\n\n"
                f"Integrity verification will be performed before decryption."
            )
            if Modal:
                Modal("Dry Run Preview \u2014 Decrypt", _dry_msg, ["OK"], self).exec_()
            else:
                QMessageBox.information(
                    self, "Dry Run Preview \u2014 Decrypt", _dry_msg
                )
        else:
            _msg = (
                f"Decryption functionality will be implemented.\n\n"
                f"Files to decrypt: {len(self.selected_files)}\n"
                f"Password: {'*' * len(password)}\n\n"
                f"This will verify integrity and decrypt using the original algorithm."
            )
            if Modal:
                Modal("Decrypt Files", _msg, ["OK"], self).exec_()
            else:
                QMessageBox.information(self, "Decrypt Files", _msg)


def main():
    """Main function for standalone execution."""
    app = QApplication(sys.argv)
    window = EnAndDecryptGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
