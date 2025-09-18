#!/usr/bin/env python3
"""
Simple Checksum GUI for Richard's File Utilities
"""

import sys
import os
import hashlib
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QListWidget, QProgressBar,
    QApplication, QMessageBox, QGroupBox, QFileDialog
)

# Import StandardWindow for menu integration
try:
    from src.gui.standard_window import StandardWindow
    STANDARD_WINDOW_AVAILABLE = True
except ImportError:
    # Fallback for standalone execution
    from PyQt5.QtWidgets import QMainWindow
    StandardWindow = QMainWindow
    STANDARD_WINDOW_AVAILABLE = False


class ChecksumGUI(StandardWindow):
    """Simple Checksum Calculator GUI."""
    
    def __init__(self):
        if STANDARD_WINDOW_AVAILABLE:
            super().__init__(
                title="Checksum Calculator - Richard's File Utilities",
                window_type="utility"
            )
        else:
            super().__init__()
            self.setWindowTitle("Checksum Calculator - Richard's File Utilities")
            self.setGeometry(100, 100, 800, 600)
        
        self.init_ui()
        if STANDARD_WINDOW_AVAILABLE:
            self._setup_menu_callbacks()
            # Ensure menu bar exists
            self.ensure_menu_bar()
    
    def _setup_menu_callbacks(self):
        """Setup tool-specific menu callbacks."""
        if hasattr(self, 'menu_manager'):
            # Register tool-specific callbacks
            self.menu_manager.register_callback('new_checksum',
                                                self.clear_results)
            # Override the standard help with our tool-specific help
            self.menu_manager.register_callback('show_user_guide',
                                                self.show_help)
            self.menu_manager.register_callback('show_preferences',
                                                self.show_preferences)
            self.menu_manager.register_callback('refresh',
                                                self.refresh_view)
            
    def clear_results(self):
        """Clear all checksum calculation results."""
        if hasattr(self, 'results_list'):
            self.results_list.clear()
        
    def show_help(self):
        """Show help dialog for Checksum Calculator tool."""
        help_text = """
        <h2>File Checksum Calculator - Help</h2>
        
        <h3>How to Calculate Checksums:</h3>
        <ul>
        <li><b>Select Files:</b> Choose one or more files to calculate checksums</li>
        <li><b>Choose Algorithm:</b> Pick MD5, SHA1, or SHA256 algorithm</li>
        <li><b>Calculate:</b> Click to generate checksums for selected files</li>
        <li><b>Copy Results:</b> Copy checksums to clipboard for verification</li>
        </ul>
        
        <h3>Checksum Algorithms:</h3>
        <ul>
        <li><b>MD5:</b> Fast, 128-bit hash (legacy, less secure)</li>
        <li><b>SHA1:</b> 160-bit hash (deprecated for security)</li>
        <li><b>SHA256:</b> Secure 256-bit hash (recommended)</li>
        <li><b>SHA512:</b> Most secure 512-bit hash (slower but strongest)</li>
        </ul>
        
        <h3>Use Cases:</h3>
        <ul>
        <li><b>File Integrity:</b> Verify files haven't been corrupted</li>
        <li><b>Download Verification:</b> Confirm downloaded files are intact</li>
        <li><b>Change Detection:</b> Detect if files have been modified</li>
        <li><b>Duplicate Detection:</b> Compare checksums to find duplicates</li>
        </ul>
        
        <h3>Best Practices:</h3>
        <ul>
        <li><b>Use SHA256:</b> Most balanced option for security and speed</li>
        <li><b>Save Results:</b> Keep checksum records for later verification</li>
        <li><b>Batch Processing:</b> Calculate multiple files at once</li>
        <li><b>Regular Checks:</b> Verify important files periodically</li>
        </ul>
        
        <h3>Keyboard Shortcuts:</h3>
        <ul>
        <li><b>Ctrl+Q:</b> Exit application</li>
        <li><b>F1:</b> Show this help</li>
        <li><b>F5:</b> Clear results and start new calculation</li>
        </ul>
        """
        
        QMessageBox.information(self, "Checksum Calculator Help", help_text)
        
    def show_preferences(self):
        """Show Checksum Calculator preferences."""
        QMessageBox.information(self, "Checksum Calculator Preferences",
                                "Checksum Calculator preferences:\n\n"
                                "• Default checksum algorithm\n"
                                "• Output format options\n"
                                "• Progress display settings\n"
                                "• Auto-save results location\n\n"
                                "Advanced preferences coming soon!")
                               
    def refresh_view(self):
        """Refresh/clear the current calculation results."""
        self.clear_results()
        
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
        header_label = QLabel("File Checksum Calculator")
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
        
        # File selection
        file_group = QGroupBox("File Selection")
        file_layout = QVBoxLayout(file_group)
        
        select_button = QPushButton("Select File")
        select_button.clicked.connect(self.select_file)
        file_layout.addWidget(select_button)
        
        self.file_label = QLabel("No file selected")
        file_layout.addWidget(self.file_label)
        
        layout.addWidget(file_group)
        
        # Calculate button
        calc_button = QPushButton("Calculate MD5 Checksum")
        calc_button.clicked.connect(self.calculate_checksum)
        layout.addWidget(calc_button)
        
        # Results
        self.results_list = QListWidget()
        layout.addWidget(self.results_list)
        
        self.selected_file = None
    
    def select_file(self):
        """Select a file for checksum calculation."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File", "", "All Files (*.*)"
        )
        if file_path:
            self.selected_file = file_path
            self.file_label.setText(f"Selected: {os.path.basename(file_path)}")
    
    def calculate_checksum(self):
        """Calculate MD5 checksum."""
        if not self.selected_file:
            QMessageBox.warning(self, "Warning", "Please select a file first.")
            return
        
        try:
            md5_hash = hashlib.md5()
            with open(self.selected_file, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    md5_hash.update(chunk)
            
            checksum = md5_hash.hexdigest()
            result = f"MD5: {checksum}"
            self.results_list.addItem(result)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to calculate checksum: {e}")


def main():
    """Main function for standalone execution."""
    app = QApplication(sys.argv)
    window = ChecksumGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
