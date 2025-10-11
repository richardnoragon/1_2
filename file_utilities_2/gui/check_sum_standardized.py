"""
Standardized Checksum Utility with consistent styling.
"""

import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QLineEdit,
                             QComboBox, QTextEdit, QFileDialog, QProgressBar,
                             QGroupBox, QStatusBar, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont
from gui.themes import ThemeManager, Colors, Fonts
from file_utilities_2.core.check_sum import ChecksumLogic, VALID_ALGORITHMS


class ChecksumWindow(QMainWindow):
    """Standardized checksum utility window."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Checksum Utility")
        self.setMinimumSize(600, 500)
        self.resize(700, 600)
        
        # Apply standard theme
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {Colors.WINDOW_BACKGROUND};
                color: {Colors.TEXT_PRIMARY};
            }}
        """)
        
        self._setup_ui()
        self.checksum_thread = None
        self.cancel_button = None
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self._update_progress_display)
    
    def _setup_ui(self):
        """Setup the user interface with standardized styling."""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        central_widget.setLayout(main_layout)
        
        # Header
        header = QLabel("Checksum Utility")
        header_font = Fonts.get_font(Fonts.TITLE_SIZE, Fonts.BOLD)
        header.setFont(header_font)
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet(f"color: {Colors.PRIMARY}; margin-bottom: 10px;")
        main_layout.addWidget(header)
        
        # File selection group
        file_group = QGroupBox("File Selection")
        ThemeManager.style_group_box(file_group)
        file_layout = QVBoxLayout()
        file_layout.setSpacing(10)
        file_group.setLayout(file_layout)
        
        # File path input
        file_path_layout = QHBoxLayout()
        file_path_layout.setSpacing(10)
        
        self.file_path_input = QLineEdit()
        ThemeManager.style_input_field(self.file_path_input)
        self.file_path_input.setPlaceholderText("Select file or directory...")
        
        browse_btn = QPushButton("Browse")
        ThemeManager.style_primary_button(browse_btn)
        browse_btn.clicked.connect(self.browse_file)
        
        file_path_layout.addWidget(self.file_path_input)
        file_path_layout.addWidget(browse_btn)
        file_layout.addLayout(file_path_layout)
        
        main_layout.addWidget(file_group)
        
        # Algorithm selection group
        algo_group = QGroupBox("Algorithm")
        ThemeManager.style_group_box(algo_group)
        algo_layout = QVBoxLayout()
        algo_layout.setSpacing(10)
        algo_group.setLayout(algo_layout)
        
        self.algorithm_combo = QComboBox()
        ThemeManager.style_input_field(self.algorithm_combo)
        self.algorithm_combo.addItems(VALID_ALGORITHMS)
        self.algorithm_combo.setCurrentText("sha256")
        
        algo_layout.addWidget(QLabel("Select algorithm:"))
        algo_layout.addWidget(self.algorithm_combo)
        
        main_layout.addWidget(algo_group)
        
        # Checksum input group
        checksum_group = QGroupBox("Checksum")
        ThemeManager.style_group_box(checksum_group)
        checksum_layout = QVBoxLayout()
        checksum_layout.setSpacing(10)
        checksum_group.setLayout(checksum_layout)
        
        self.checksum_input = QLineEdit()
        ThemeManager.style_input_field(self.checksum_input)
        self.checksum_input.setPlaceholderText("Enter expected checksum (optional)...")
        
        checksum_layout.addWidget(QLabel("Expected checksum (for verification):"))
        checksum_layout.addWidget(self.checksum_input)
        
        main_layout.addWidget(checksum_group)
        
        # Results group
        results_group = QGroupBox("Results")
        ThemeManager.style_group_box(results_group)
        results_layout = QVBoxLayout()
        results_layout.setSpacing(10)
        results_group.setLayout(results_layout)
        
        self.results_text = QTextEdit()
        ThemeManager.style_input_field(self.results_text)
        self.results_text.setReadOnly(True)
        self.results_text.setMaximumHeight(150)
        
        results_layout.addWidget(QLabel("Checksum results:"))
        results_layout.addWidget(self.results_text)
        
        main_layout.addWidget(results_group)
        
        # Progress group
        progress_group = QGroupBox("Progress")
        ThemeManager.style_group_box(progress_group)
        progress_layout = QVBoxLayout()
        progress_layout.setSpacing(5)
        progress_group.setLayout(progress_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        ThemeManager.style_progress_bar(self.progress_bar)
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)
        
        # Progress message
        self.progress_message = QLabel("")
        self.progress_message.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
        self.progress_message.setVisible(False)
        progress_layout.addWidget(self.progress_message)
        
        # Time estimate
        self.time_estimate_label = QLabel("")
        self.time_estimate_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
        self.time_estimate_label.setVisible(False)
        progress_layout.addWidget(self.time_estimate_label)
        
        progress_group.setVisible(False)
        main_layout.addWidget(progress_group)
        self.progress_group = progress_group
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.calculate_btn = QPushButton("Calculate Checksum")
        ThemeManager.style_primary_button(self.calculate_btn)
        self.calculate_btn.clicked.connect(self.calculate_checksum)
        
        self.verify_btn = QPushButton("Verify Checksum")
        ThemeManager.style_secondary_button(self.verify_btn)
        self.verify_btn.clicked.connect(self.verify_checksum)
        
        self.clear_btn = QPushButton("Clear")
        ThemeManager.style_secondary_button(self.clear_btn)
        self.clear_btn.clicked.connect(self.clear_results)
        
        # Cancel button (initially hidden)
        self.cancel_button = QPushButton("Cancel")
        ThemeManager.style_secondary_button(self.cancel_button)
        self.cancel_button.clicked.connect(self.cancel_operation)
        self.cancel_button.setVisible(False)
        
        button_layout.addWidget(self.calculate_btn)
        button_layout.addWidget(self.verify_btn)
        button_layout.addWidget(self.clear_btn)
        button_layout.addWidget(self.cancel_button)
        
        main_layout.addLayout(button_layout)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def browse_file(self):
        """Browse for file or directory."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File", "", "All Files (*)"
        )
        if file_path:
            self.file_path_input.setText(file_path)
    
    def calculate_checksum(self):
        """Calculate checksum for selected file."""
        file_path = self.file_path_input.text()
        if not file_path or not os.path.exists(file_path):
            self.status_bar.showMessage("Please select a valid file", 3000)
            return
        
        algorithm = self.algorithm_combo.currentText()
        
        # Show progress UI
        self._show_progress_ui()
        self.status_bar.showMessage("Calculating checksum...")
        
        # Create and start enhanced checksum thread
        self.checksum_thread = EnhancedChecksumThread(file_path, algorithm)
        self._connect_thread_signals()
        self.checksum_thread.result_ready.connect(self.on_checksum_calculated)
        self.checksum_thread.start()
    
    def verify_checksum(self):
        """Verify checksum against expected value."""
        file_path = self.file_path_input.text()
        expected_checksum = self.checksum_input.text()
        
        if not file_path or not os.path.exists(file_path):
            self.status_bar.showMessage("Please select a valid file", 3000)
            return
        
        if not expected_checksum:
            self.status_bar.showMessage("Please enter expected checksum", 3000)
            return
        
        algorithm = self.algorithm_combo.currentText()
        
        # Show progress UI
        self._show_progress_ui()
        self.status_bar.showMessage("Verifying checksum...")
        
        # Create and start enhanced checksum thread
        self.checksum_thread = EnhancedChecksumThread(file_path, algorithm,
                                                     expected_checksum)
        self._connect_thread_signals()
        self.checksum_thread.result_ready.connect(self.on_checksum_verified)
        self.checksum_thread.start()
    
    def _show_progress_ui(self):
        """Show progress UI elements."""
        self.progress_group.setVisible(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_message.setVisible(True)
        self.time_estimate_label.setVisible(True)
        
        # Disable action buttons and show cancel
        self.calculate_btn.setEnabled(False)
        self.verify_btn.setEnabled(False)
        self.clear_btn.setEnabled(False)
        self.cancel_button.setVisible(True)
    
    def _hide_progress_ui(self):
        """Hide progress UI elements."""
        self.progress_group.setVisible(False)
        self.progress_bar.setVisible(False)
        self.progress_message.setVisible(False)
        self.time_estimate_label.setVisible(False)
        
        # Re-enable action buttons and hide cancel
        self.calculate_btn.setEnabled(True)
        self.verify_btn.setEnabled(True)
        self.clear_btn.setEnabled(True)
        self.cancel_button.setVisible(False)
    
    def _connect_thread_signals(self):
        """Connect enhanced thread signals."""
        self.checksum_thread.progress_percentage.connect(
            self.progress_bar.setValue
        )
        self.checksum_thread.progress_message.connect(
            self.progress_message.setText
        )
        self.checksum_thread.milestone_reached.connect(
            self._on_milestone_reached
        )
        self.checksum_thread.time_estimate.connect(
            self.time_estimate_label.setText
        )
        self.checksum_thread.error_occurred.connect(self.on_error)
        self.checksum_thread.finished.connect(self._on_thread_finished)
    
    def _on_milestone_reached(self, milestone, percentage):
        """Handle milestone updates."""
        self.status_bar.showMessage(f"{milestone} ({percentage}%)")
    
    def _on_thread_finished(self):
        """Handle thread completion."""
        self._hide_progress_ui()
    
    def _update_progress_display(self):
        """Update progress display periodically."""
        # This can be used for additional UI updates if needed
        pass
    
    def cancel_operation(self):
        """Cancel the current operation."""
        if self.checksum_thread and self.checksum_thread.isRunning():
            self.checksum_thread.cancel()
            self.status_bar.showMessage("Cancelling operation...", 2000)
    
    def on_checksum_calculated(self, result):
        """Handle checksum calculation result."""
        checksum = result.get('checksum', '')
        algorithm = result.get('algorithm', '')
        file_path = result.get('file_path', '')
        
        self.results_text.setPlainText(
            f"Algorithm: {algorithm}\n"
            f"File: {file_path}\n"
            f"Checksum: {checksum}"
        )
        
        self.status_bar.showMessage("Checksum calculated successfully", 3000)
    
    def on_checksum_verified(self, result):
        """Handle checksum verification result."""
        is_valid = result.get('is_valid', False)
        expected = result.get('expected', '')
        actual = result.get('actual', '')
        algorithm = result.get('algorithm', '')
        file_path = result.get('file_path', '')
        
        if is_valid:
            self.results_text.setPlainText(
                f"✅ Checksum verification PASSED\n"
                f"Algorithm: {algorithm}\n"
                f"File: {file_path}\n"
                f"Expected: {expected}\n"
                f"Actual: {actual}"
            )
        else:
            self.results_text.setPlainText(
                f"❌ Checksum verification FAILED\n"
                f"Algorithm: {algorithm}\n"
                f"File: {file_path}\n"
                f"Expected: {expected}\n"
                f"Actual: {actual}"
            )
        
        self.status_bar.showMessage("Checksum verification complete", 3000)
    
    def on_error(self, error_message):
        """Handle errors."""
        self._hide_progress_ui()
        self.status_bar.showMessage(f"Error: {error_message}", 5000)
        
        # Show error in results area
        self.results_text.setPlainText(f"❌ Error: {error_message}")
    
    def clear_results(self):
        """Clear all results and inputs."""
        self.results_text.clear()
        self.checksum_input.clear()
        self._hide_progress_ui()
        self.status_bar.showMessage("Ready")


class EnhancedChecksumThread(QThread):
    """Enhanced thread for calculating checksums with real-time progress."""
    
    result_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    progress_percentage = pyqtSignal(int)
    progress_message = pyqtSignal(str)
    milestone_reached = pyqtSignal(str, int)
    time_estimate = pyqtSignal(str)
    
    def __init__(self, file_path, algorithm, expected_checksum=None):
        super().__init__()
        self.file_path = file_path
        self.algorithm = algorithm
        self.expected_checksum = expected_checksum
        self.checksum_logic = None
        self._cancelled = False
    
    def cancel(self):
        """Cancel the current operation."""
        self._cancelled = True
        if self.checksum_logic:
            self.checksum_logic.stop()
    
    def run(self):
        """Calculate checksum using enhanced ChecksumLogic."""
        try:
            if not os.path.exists(self.file_path):
                self.error_occurred.emit("File not found")
                return
            
            # Determine mode based on expected checksum
            mode = 'verify_file' if self.expected_checksum else 'calculate_file'
            
            # Create ChecksumLogic instance
            self.checksum_logic = ChecksumLogic(
                self.file_path,
                self.algorithm,
                self.expected_checksum,
                mode=mode
            )
            
            # Connect signals
            self.checksum_logic.progress_percentage.connect(
                self.progress_percentage.emit
            )
            self.checksum_logic.progress_message.connect(
                self.progress_message.emit
            )
            self.checksum_logic.milestone_reached.connect(
                self.milestone_reached.emit
            )
            self.checksum_logic.time_estimate.connect(
                self.time_estimate.emit
            )
            self.checksum_logic.error_occurred.connect(
                self.error_occurred.emit
            )
            self.checksum_logic.result_ready.connect(
                self._handle_result
            )
            
            # Run the checksum calculation
            self.checksum_logic.run()
            
        except Exception as e:
            if not self._cancelled:
                self.error_occurred.emit(str(e))
    
    def _handle_result(self, results):
        """Handle results from ChecksumLogic and format for GUI."""
        try:
            if self._cancelled:
                return
                
            file_path = self.file_path
            
            if self.expected_checksum:
                # Verification mode
                status = results.get(file_path, "ERROR")
                is_valid = status == "OK"
                
                result = {
                    'file_path': file_path,
                    'algorithm': self.algorithm,
                    'is_valid': is_valid,
                    'expected': self.expected_checksum,
                    'actual': results.get('calculated_checksum', ''),
                    'status': status
                }
            else:
                # Calculation mode
                checksum = results.get(file_path, '')
                
                result = {
                    'file_path': file_path,
                    'algorithm': self.algorithm,
                    'checksum': checksum
                }
            
            self.result_ready.emit(result)
            
        except Exception as e:
            self.error_occurred.emit(f"Error processing results: {e}")


class MyGUI(ChecksumWindow):
    """Main GUI class for checksum utility."""
    pass


def main():
    """Main function to run the checksum utility."""
    app = QApplication(sys.argv)
    
    # Apply application-wide stylesheet
    app.setStyle('Fusion')
    app.setStyleSheet(f"""
        QApplication {{
            font-family: {Fonts.DEFAULT_FAMILY};
            font-size: {Fonts.BODY_SIZE}pt;
        }}
    """)
    
    window = MyGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()