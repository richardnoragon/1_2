#!/usr/bin/env python3
"""
Size Analyzer Tool for Richard's File Utilities

A streamlined size analyzer utility with essential functionality.
"""

import os
import sys

try:
    from PyQt5.QtWidgets import (
        QApplication,
        QFileDialog,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QListWidget,
        QMainWindow,
        QMessageBox,
        QProgressBar,
        QPushButton,
        QVBoxLayout,
        QWidget,
    )
except ImportError:
    print("PyQt5 not available. Please install PyQt5.")
    sys.exit(1)

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


class SizeAnalyzerGUI(StandardWindow):
    """Main window for Size Analyzer operations."""

    def __init__(self, parent=None):
        # Always use the safe constructor parameters
        super().__init__(
            title="Size Analyzer - Richard's File Utilities",
            window_type="utility",
            parent=parent,
        )
        self.setGeometry(100, 100, 800, 600)

        self.analysis_results = {}
        self.init_ui()
        if STANDARD_WINDOW_AVAILABLE:
            self._setup_menu_callbacks()
        # Ensure menu bar exists (safe to call in both modes)
        self.ensure_menu_bar()

    def _setup_menu_callbacks(self):
        """Setup tool-specific menu callbacks."""
        if hasattr(self, "menu_manager"):
            # Register tool-specific callbacks
            self.menu_manager.register_callback(
                "new_analysis", self.clear_analysis
            )
            # Override the standard help with our tool-specific help
            self.menu_manager.register_callback(
                "show_user_guide", self.show_help
            )
            self.menu_manager.register_callback(
                "show_preferences", self.show_preferences
            )
            self.menu_manager.register_callback("refresh", self.refresh_view)

    def clear_analysis(self):
        """Clear all size analysis results."""
        self.analysis_results = {}
        if hasattr(self, "results_list"):
            self.results_list.clear()

    def show_help(self):
        """Show help dialog for Size Analyzer tool."""
        help_text = """
        <h2>Size Analyzer - Help</h2>
        
        <h3>How to Analyze Directory Sizes:</h3>
        <ul>
        <li><b>Select Directory:</b> Choose the folder to analyze</li>
        <li><b>Start Analysis:</b> Begin calculating directory and file sizes</li>
        <li><b>View Results:</b> Browse size breakdown by folders and files</li>
        <li><b>Export Data:</b> Save analysis results to file</li>
        </ul>
        
        <h3>Analysis Features:</h3>
        <ul>
        <li><b>Directory Tree:</b> Hierarchical view of folder sizes</li>
        <li><b>File Breakdown:</b> Individual file size listings</li>
        <li><b>Size Sorting:</b> Results sorted by size (largest first)</li>
        <li><b>Progress Tracking:</b> Real-time analysis progress</li>
        </ul>
        
        <h3>Size Information:</h3>
        <ul>
        <li><b>Bytes Display:</b> Precise file sizes in bytes</li>
        <li><b>Human Readable:</b> Sizes shown in KB, MB, GB format</li>
        <li><b>Percentage View:</b> Relative size percentages</li>
        <li><b>File Count:</b> Number of files in each directory</li>
        </ul>
        
        <h3>Use Cases:</h3>
        <ul>
        <li><b>Disk Cleanup:</b> Find largest files consuming space</li>
        <li><b>Storage Planning:</b> Understand disk usage patterns</li>
        <li><b>Archive Planning:</b> Identify candidates for archival</li>
        <li><b>System Optimization:</b> Locate space-wasting files</li>
        </ul>
        
        <h3>Best Practices:</h3>
        <ul>
        <li><b>Regular Analysis:</b> Periodic size checks prevent space issues</li>
        <li><b>Focus on Large Files:</b> Start cleanup with biggest space users</li>
        <li><b>Archive Old Data:</b> Move unused large files to external storage</li>
        <li><b>Monitor Growth:</b> Track how directories grow over time</li>
        </ul>
        
        <h3>Keyboard Shortcuts:</h3>
        <ul>
        <li><b>Ctrl+Q:</b> Exit application</li>
        <li><b>F1:</b> Show this help</li>
        <li><b>F5:</b> Clear analysis and start new scan</li>
        </ul>
        """

        QMessageBox.information(self, "Size Analyzer Help", help_text)

    def show_preferences(self):
        """Show Size Analyzer preferences."""
        QMessageBox.information(
            self,
            "Size Analyzer Preferences",
            "Size Analyzer preferences:\n\n"
            "• Analysis depth limits\n"
            "• File type filters\n"
            "• Size display units\n"
            "• Sort and grouping options\n\n"
            "Advanced preferences coming soon!",
        )

    def refresh_view(self):
        """Refresh/clear the current analysis results."""
        self.clear_analysis()

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
        header_label = QLabel("Size Analyzer")
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

        # Add analysis area
        analysis_group = QGroupBox("Analysis Results")
        analysis_layout = QVBoxLayout(analysis_group)

        self.results_list = QListWidget()
        analysis_layout.addWidget(self.results_list)

        analyze_button = QPushButton("Start Analysis")
        analyze_button.clicked.connect(self.start_analysis)
        analysis_layout.addWidget(analyze_button)

        layout.addWidget(analysis_group)
        content_label = QLabel("Tool functionality will be implemented here.")
        content_label.setStyleSheet("padding: 20px; color: #666;")
        layout.addWidget(content_label)

        # Add action button
        action_button = QPushButton("Execute Action")
        action_button.clicked.connect(self.execute_action)
        action_button.setStyleSheet(
            """
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
        """
        )
        layout.addWidget(action_button)

    def start_analysis(self):
        """Start the analysis process."""
        self.results_list.clear()
        self.results_list.addItem(
            "Analysis functionality ready for implementation"
        )

    def execute_action(self):
        """Main action method for this tool."""
        QMessageBox.information(
            self,
            "Size Analyzer",
            "Tool functionality is ready for implementation.",
        )


def main():
    """Main function for standalone execution."""
    app = QApplication(sys.argv)
    window = SizeAnalyzerGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
