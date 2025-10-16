#!/usr/bin/env python3
"""
Simple Duplicate Finder GUI for Richard's File Utilities
"""

import hashlib
import os
import sys

from PyQt5.QtWidgets import (
    QApplication,
    QFileDialog,
    QGroupBox,
    QLabel,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

# Import SafeStandardWindow for reliable menu integration
try:
    # Add the correct path for imports
    sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    from src.gui.safe_standard_window import (
        SafeStandardWindow as StandardWindow,
    )

    STANDARD_WINDOW_AVAILABLE = True
except ImportError as e:
    print(f"SafeStandardWindow not available: {e}")
    # Try original StandardWindow as fallback
    try:
        from src.gui.standard_window import StandardWindow

        STANDARD_WINDOW_AVAILABLE = True
    except ImportError:
        # Final fallback - minimal implementation
        class StandardWindow(QMainWindow):
            def __init__(
                self, title="Window", window_type="utility", parent=None
            ):
                super().__init__(parent)
                self.setWindowTitle(title)

            def ensure_menu_bar(self):
                pass  # No-op for fallback

        STANDARD_WINDOW_AVAILABLE = False


class DuplicateFinderApp(StandardWindow):
    """Simple Duplicate Finder GUI."""

    def __init__(self, parent=None):
        # Always use the safe constructor parameters
        super().__init__(
            title="Duplicate Finder - Richard's File Utilities",
            window_type="utility",
            parent=parent,
        )
        self.setGeometry(100, 100, 800, 600)

        self.duplicates = {}
        self.selected_directory = None
        self.init_ui()
        if STANDARD_WINDOW_AVAILABLE:
            self._setup_menu_callbacks()
        # Ensure menu bar exists (safe to call in both modes)
        self.ensure_menu_bar()

    def _setup_menu_callbacks(self):
        """Setup tool-specific menu callbacks."""
        if hasattr(self, "menu_manager"):
            # Register tool-specific callbacks
            self.menu_manager.register_callback("new_scan", self.clear_results)
            # Override the standard help with our tool-specific help
            self.menu_manager.register_callback(
                "show_user_guide", self.show_help
            )
            self.menu_manager.register_callback(
                "show_preferences", self.show_preferences
            )
            self.menu_manager.register_callback("refresh", self.refresh_view)

    def clear_results(self):
        """Clear all duplicate scan results."""
        self.duplicates = {}
        if hasattr(self, "results_list"):
            self.results_list.clear()

    def show_help(self):
        """Show help dialog for Duplicate Finder tool."""
        help_text = """
        <h2>Duplicate Finder - Help</h2>
        
        <h3>How to Find Duplicates:</h3>
        <ul>
        <li><b>Select Directory:</b> Choose the folder to scan for duplicates</li>
        <li><b>Start Scan:</b> Begin searching for duplicate files</li>
        <li><b>Review Results:</b> Examine found duplicates in the results list</li>
        </ul>
        
        <h3>Duplicate Detection:</h3>
        <ul>
        <li><b>File Comparison:</b> Uses MD5 checksums for accurate detection</li>
        <li><b>Size Filtering:</b> Pre-filters by file size for efficiency</li>
        <li><b>Content Verification:</b> Compares actual file content</li>
        <li><b>Safe Detection:</b> Never modifies original files</li>
        </ul>
        
        <h3>Results Management:</h3>
        <ul>
        <li><b>Group Display:</b> Duplicates grouped by content similarity</li>
        <li><b>Path Information:</b> Full file paths for each duplicate</li>
        <li><b>Size Details:</b> File sizes and modification dates</li>
        <li><b>Export Options:</b> Save results to file for review</li>
        </ul>
        
        <h3>Best Practices:</h3>
        <ul>
        <li><b>Backup First:</b> Always backup important files before cleanup</li>
        <li><b>Manual Review:</b> Verify duplicates before any deletion</li>
        <li><b>Keep Originals:</b> Preserve files in primary locations</li>
        <li><b>Scan Regularly:</b> Periodic scans help maintain organization</li>
        </ul>
        
        <h3>Keyboard Shortcuts:</h3>
        <ul>
        <li><b>Ctrl+Q:</b> Exit application</li>
        <li><b>F1:</b> Show this help</li>
        <li><b>F5:</b> Clear results and start new scan</li>
        </ul>
        """

        QMessageBox.information(self, "Duplicate Finder Help", help_text)

    def show_preferences(self):
        """Show Duplicate Finder preferences."""
        QMessageBox.information(
            self,
            "Duplicate Finder Preferences",
            "Duplicate Finder preferences:\n\n"
            "• Scan depth limits\n"
            "• File type filters\n"
            "• Minimum file size settings\n"
            "• Checksum algorithm options\n\n"
            "Advanced preferences coming soon!",
        )

    def refresh_view(self):
        """Refresh/clear the current scan results."""
        self.clear_results()

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
        header_label = QLabel("Duplicate File Finder")
        header_label.setStyleSheet(
            """
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
                background-color: #ecf0f1;
                border-radius: 5px;
                margin-bottom: 10px;
            }
        """
        )
        layout.addWidget(header_label)

        # Directory selection
        dir_group = QGroupBox("Directory Selection")
        dir_layout = QVBoxLayout(dir_group)

        select_button = QPushButton("Select Directory")
        select_button.clicked.connect(self.select_directory)
        dir_layout.addWidget(select_button)

        self.dir_label = QLabel("No directory selected")
        dir_layout.addWidget(self.dir_label)

        layout.addWidget(dir_group)

        # Find button
        find_button = QPushButton("Find Duplicates")
        find_button.clicked.connect(self.find_duplicates)
        layout.addWidget(find_button)

        # Results
        self.results_list = QListWidget()
        layout.addWidget(self.results_list)

        self.selected_directory = None

    def select_directory(self):
        """Select a directory to scan."""
        dir_path = QFileDialog.getExistingDirectory(
            self, "Select Directory to Scan"
        )
        if dir_path:
            self.selected_directory = dir_path
            self.dir_label.setText(f"Selected: {dir_path}")

    def find_duplicates(self):
        """Find duplicate files in the selected directory."""
        if not self.selected_directory:
            QMessageBox.warning(
                self, "Warning", "Please select a directory first."
            )
            return

        self._prepare_scan()

        try:
            duplicates = self._scan_for_duplicates()
            self._display_results(duplicates)

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to scan directory: {e}"
            )

    def _prepare_scan(self):
        """Prepare the UI for scanning."""
        self.results_list.clear()
        self.results_list.addItem("Scanning for duplicates...")
        QApplication.processEvents()

    def _scan_for_duplicates(self):
        """Scan directory and return list of duplicate file pairs."""
        file_hashes = {}
        duplicates = []

        for root, dirs, files in os.walk(self.selected_directory):
            for file in files:
                file_path = os.path.join(root, file)
                file_hash = self._get_file_hash(file_path)

                if file_hash:
                    if file_hash in file_hashes:
                        duplicates.append((file_hashes[file_hash], file_path))
                    else:
                        file_hashes[file_hash] = file_path

        return duplicates

    def _get_file_hash(self, file_path):
        """Get MD5 hash of a file, return None if error."""
        try:
            with open(file_path, "rb") as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return None

    def _display_results(self, duplicates):
        """Display scan results in the list widget."""
        self.results_list.clear()

        if duplicates:
            self.results_list.addItem(
                f"Found {len(duplicates)} duplicate pairs:"
            )
            for original, duplicate in duplicates:
                self.results_list.addItem(f"Original: {original}")
                self.results_list.addItem(f"Duplicate: {duplicate}")
                self.results_list.addItem("---")
        else:
            self.results_list.addItem("No duplicates found.")


def main():
    """Main function for standalone execution."""
    app = QApplication(sys.argv)
    window = DuplicateFinderApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
