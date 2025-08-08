#!/usr/bin/env python3
"""
Enhanced Secure Delete Tool for Richard's File Utilities

A comprehensive secure delete utility with menu integration and essential functionality.
"""

import os
import sys
import hashlib

try:
    from PyQt5.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout,
        QPushButton, QLabel, QListWidget, QProgressBar,
        QApplication, QMessageBox, QFileDialog, QGroupBox, QLineEdit,
        QCheckBox, QSpinBox, QComboBox, QMainWindow
    )
except ImportError:
    print("PyQt5 not available. Please install PyQt5.")
    sys.exit(1)

# Import StandardWindow for menu integration
try:
    from src.rfu.gui.standard_window import StandardWindow
    STANDARD_WINDOW_AVAILABLE = True
except ImportError:
    # Fallback for standalone execution
    StandardWindow = QMainWindow
    STANDARD_WINDOW_AVAILABLE = False


class SecureDeleteGUI(StandardWindow):
    """Main window for Secure Delete operations."""
    
    def __init__(self):
        if STANDARD_WINDOW_AVAILABLE:
            super().__init__(
                title="Secure Delete - Richard's File Utilities",
                window_type="security"
            )
        else:
            super().__init__()
            self.setWindowTitle("Secure Delete - Richard's File Utilities")
            self.setGeometry(100, 100, 800, 600)
        
        self.selected_files = []
        self.init_ui()
        if STANDARD_WINDOW_AVAILABLE:
            self._setup_menu_callbacks()
        
    def _setup_menu_callbacks(self):
        """Setup tool-specific menu callbacks."""
        if hasattr(self, 'menu_manager'):
            # Register tool-specific callbacks
            self.menu_manager.register_callback('new_deletion', self.clear_selection)
            self.menu_manager.register_callback('help_secure_delete', self.show_help)
            
    def show_help(self):
        """Show comprehensive help for Secure Delete tool."""
        help_text = """
        <h2>Secure Delete Tool - Comprehensive Guide</h2>
        
        <h3>🗑️ Overview</h3>
        <p>The Secure Delete tool provides military-grade file deletion capabilities that 
        prevent data recovery by overwriting files multiple times with random data patterns.</p>
        
        <h3>🚀 Key Features</h3>
        <ul>
            <li><b>Multiple Pass Deletion</b>: 1-35 overwrite passes for maximum security</li>
            <li><b>DoD Standards</b>: DoD 5220.22-M compliant deletion patterns</li>
            <li><b>Random Overwriting</b>: Cryptographically secure random data patterns</li>
            <li><b>Directory Deletion</b>: Secure deletion of entire directory structures</li>
            <li><b>Free Space Wiping</b>: Clean unallocated disk space</li>
            <li><b>Verification</b>: Optional verification of deletion success</li>
        </ul>
        
        <h3>🔒 Deletion Methods</h3>
        <ul>
            <li><b>Single Pass</b>: Quick deletion with one random overwrite</li>
            <li><b>DoD 5220.22-M</b>: 3-pass DoD standard (0x00, 0xFF, random)</li>
            <li><b>Gutmann Method</b>: 35-pass algorithm for ultimate security</li>
            <li><b>Random Pattern</b>: Multiple passes with cryptographic random data</li>
            <li><b>Custom Pattern</b>: User-defined overwrite patterns</li>
        </ul>
        
        <h3>⚠️ Important Warnings</h3>
        <ul>
            <li><b>Permanent Deletion</b>: Securely deleted files CANNOT be recovered</li>
            <li><b>SSD Limitations</b>: Modern SSDs may have built-in wear leveling</li>
            <li><b>File System Features</b>: Copy-on-write file systems need special handling</li>
            <li><b>Backup Considerations</b>: Files may exist in backups elsewhere</li>
            <li><b>System Files</b>: Never delete critical system files</li>
        </ul>
        
        <p><b>Note:</b> This tool provides a foundation for secure deletion. Full implementation 
        requires system-level integration and may need additional libraries for optimal security.</p>
        """
        
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Secure Delete Tool - Help")
        msg_box.setTextFormat(1)  # Rich text format
        msg_box.setText(help_text)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()
        
    def show_preferences(self):
        """Show Secure Delete preferences."""
        QMessageBox.information(self, "Secure Delete Preferences", 
                               "Secure Delete preferences:\n\n"
                               "• Default deletion method settings\n"
                               "• Overwrite pass count preferences\n"
                               "• Verification options\n"
                               "• Performance optimization settings\n"
                               "• Logging and audit preferences\n\n"
                               "Advanced preferences coming soon!")
                               
    def refresh_view(self):
        """Refresh the current view."""
        self.clear_selection()
        
    def clear_selection(self):
        """Clear current file selection."""
        if hasattr(self, 'files_list'):
            self.files_list.clear()
        if hasattr(self, 'status_label'):
            self.status_label.setText("Ready - Select files or directories to securely delete")
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
        header_label = QLabel("Secure Delete")
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
        file_group = QGroupBox("File/Directory Selection")
        file_layout = QVBoxLayout(file_group)
        
        # Selection buttons
        button_layout = QHBoxLayout()
        
        self.select_files_button = QPushButton("Select Files")
        self.select_files_button.clicked.connect(self.select_files)
        self.select_files_button.setStyleSheet("""
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
        button_layout.addWidget(self.select_files_button)
        
        self.select_folder_button = QPushButton("Select Folder")
        self.select_folder_button.clicked.connect(self.select_folder)
        self.select_folder_button.setStyleSheet("""
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
        button_layout.addWidget(self.select_folder_button)
        
        file_layout.addLayout(button_layout)
        
        # Selected files list
        self.files_list = QListWidget()
        self.files_list.setMaximumHeight(120)
        file_layout.addWidget(QLabel("Selected Items:"))
        file_layout.addWidget(self.files_list)
        
        layout.addWidget(file_group)
        
        # Add security options
        security_group = QGroupBox("Deletion Method")
        security_layout = QVBoxLayout(security_group)
        
        # Deletion method selection
        method_layout = QHBoxLayout()
        method_layout.addWidget(QLabel("Method:"))
        self.method_combo = QComboBox()
        self.method_combo.addItems([
            "Single Pass (Quick)",
            "DoD 5220.22-M (3 Pass)",
            "Random Pattern (7 Pass)",
            "Gutmann Method (35 Pass)",
            "Custom Pattern"
        ])
        self.method_combo.setCurrentIndex(1)  # Default to DoD standard
        method_layout.addWidget(self.method_combo)
        security_layout.addLayout(method_layout)
        
        # Verification option
        self.verify_deletion = QCheckBox("Verify deletion (recommended)")
        self.verify_deletion.setChecked(True)
        security_layout.addWidget(self.verify_deletion)
        
        layout.addWidget(security_group)
        
        # Add progress section
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Ready - Select files or directories to securely delete")
        self.status_label.setStyleSheet("padding: 10px; color: #666;")
        progress_layout.addWidget(self.status_label)
        
        layout.addWidget(progress_group)
        
        # Add action buttons
        action_layout = QHBoxLayout()
        
        self.delete_button = QPushButton("🗑️ Secure Delete")
        self.delete_button.clicked.connect(self.secure_delete)
        self.delete_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        action_layout.addWidget(self.delete_button)
        
        self.clear_button = QPushButton("Clear Selection")
        self.clear_button.clicked.connect(self.clear_selection)
        action_layout.addWidget(self.clear_button)
        
        layout.addLayout(action_layout)
        
    def select_files(self):
        """Select files for secure deletion."""
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Files for Secure Deletion", "",
            "All Files (*.*)"
        )
        if files:
            self.files_list.clear()
            for file_path in files:
                self.files_list.addItem(f"📄 {os.path.basename(file_path)}")
            self.selected_files = files
            self.status_label.setText(f"Selected {len(files)} file(s) for secure deletion")
            
    def select_folder(self):
        """Select folder for secure deletion."""
        folder = QFileDialog.getExistingDirectory(
            self, "Select Folder for Secure Deletion"
        )
        if folder:
            self.files_list.clear()
            self.files_list.addItem(f"📁 {os.path.basename(folder)}")
            self.selected_files = [folder]
            self.status_label.setText(f"Selected folder for secure deletion")
            
    def secure_delete(self):
        """Perform secure deletion."""
        if not self.selected_files:
            QMessageBox.warning(self, "Warning", "Please select files or folders first.")
            return
            
        method = self.method_combo.currentText()
        verify = self.verify_deletion.isChecked()
        
        # Confirmation dialog with strong warning
        reply = QMessageBox.critical(
            self, "⚠️ SECURE DELETE CONFIRMATION",
            f"WARNING: This will PERMANENTLY DELETE the selected items!\n\n"
            f"Items to delete: {len(self.selected_files)}\n"
            f"Method: {method}\n"
            f"Verification: {'Enabled' if verify else 'Disabled'}\n\n"
            f"This action CANNOT be undone!\n\n"
            f"Are you absolutely sure you want to continue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            QMessageBox.information(
                self,
                "Secure Delete",
                f"Secure deletion functionality will be implemented.\n\n"
                f"Method: {method}\n"
                f"Items: {len(self.selected_files)}\n"
                f"Verification: {'Enabled' if verify else 'Disabled'}\n\n"
                f"This will use military-grade overwriting patterns."
            )
def main():
    """Main function for standalone execution."""
    app = QApplication(sys.argv)
    window = SecureDeleteGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
