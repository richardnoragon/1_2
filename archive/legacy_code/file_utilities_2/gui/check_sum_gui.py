import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread
from file_utilities_2.core.check_sum import ChecksumLogic
from gui.common import (
    BaseWindow,
    show_error_dialog,
    show_info_dialog,
    get_open_file_name,
    get_save_file_name,
    get_existing_directory,
    ProgressWidget
)
from typing import Optional


class ChecksumGUI(BaseWindow):
    """GUI application for calculating and verifying file/directory checksums.
    
    Inherits from BaseWindow and provides functionality for:
    - Calculating checksums for files and directories
    - Verifying checksums against provided values
    - Supporting multiple hash algorithms
    - Showing progress during operations
    """
    
    def __init__(self) -> None:
        # Get the directory containing this script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_file = os.path.join(current_dir, 'check_sum.ui')
        super().__init__(ui_file)
        
        # Add progress widget to status bar
        self.progress_widget = ProgressWidget(self)
        self.statusBar().addPermanentWidget(self.progress_widget)
        self.progress_widget.hide()
        
        # Connect signals
        self.browseButton.clicked.connect(self.browse_file)
        self.calculateButton.clicked.connect(self.start_calculation)
        self.clearButton.clicked.connect(self.clear_results)
        self.saveButton.clicked.connect(self.save_results)
        self.modeCombo.currentTextChanged.connect(self.update_ui_state)
        
        # Initialize state
        self.checksum_thread: Optional[QThread] = None
        self.checksum_worker: Optional[ChecksumLogic] = None
        self.update_ui_state()
        
    def update_ui_state(self) -> None:
        """Update UI elements based on current mode"""
        mode: str = self.modeCombo.currentText()
        is_verify_mode: bool = 'Verify' in mode
        self.checksumInput.setVisible(is_verify_mode)
        self.checksumInput.setEnabled(is_verify_mode)
        
    def browse_file(self) -> None:
        """Open file dialog to select file or directory"""
        mode: str = self.modeCombo.currentText()
        if 'Directory' in mode:
            path: str = str(
                get_existing_directory(self, "Select Directory") or ""
            )
        else:
            path: str = str(get_open_file_name(self, "Select File") or "")
            
        if path:
            self.filePathInput.setText(path)
            
    def start_calculation(self) -> None:
        """Start the checksum calculation/verification process"""
        path: str = self.filePathInput.text()
        if not path:
            show_error_dialog(
                "Please select a file or directory",
                parent=self
            )
            return
            
        if not os.path.exists(path):
            show_error_dialog("Selected path does not exist", parent=self)
            return
            
        # Determine mode
        mode_text: str = self.modeCombo.currentText().lower()
        if 'directory' in mode_text:
            mode: str = (
                'calculate_dir' if 'calculate' in mode_text
                else 'verify_dir'
            )
        else:
            mode: str = (
                'calculate_file' if 'calculate' in mode_text
                else 'verify_file'
            )
            
        # Get algorithm
        algorithm: str = (
            self.algorithmCombo.currentText()
            .lower()
            .replace('-', '')
        )
            
        # Create worker in thread
        self.checksum_worker = ChecksumLogic(
            path,
            algorithm,
            self.checksumInput.text() if 'verify' in mode else None,
            self.checksumInput.text() if mode == 'verify_dir' else None,
            mode
        )
        
        self.checksum_thread = QThread()
        self.checksum_worker.moveToThread(self.checksum_thread)
        
        # Connect signals
        self.checksum_thread.started.connect(self.checksum_worker.run)
        self.checksum_worker.progress_updated.connect(self.update_progress)
        self.checksum_worker.progress_percentage.connect(self.update_percentage)
        self.checksum_worker.progress_message.connect(self.update_status_message)
        self.checksum_worker.milestone_reached.connect(self.update_milestone)
        self.checksum_worker.time_estimate.connect(self.update_time_estimate)
        self.checksum_worker.result_ready.connect(self.handle_results)
        self.checksum_worker.error_occurred.connect(self.handle_error)
        self.checksum_worker.finished.connect(self.calculation_finished)
        
        # Disable UI elements
        self.calculateButton.setEnabled(False)
        self.browseButton.setEnabled(False)
        self.clearButton.setEnabled(False)
        self.saveButton.setEnabled(False)
        
        # Start processing
        self.checksum_thread.start()
        
    def update_progress(self, current: int, total: int) -> None:
        """Update progress bar"""
        percentage: int = int((current / total) * 100) if total > 0 else 0
        self.progressBar.setValue(percentage)
        self.progress_widget.set_progress(percentage)
        self.progress_widget.set_text(f"Processing: {current}/{total}")
    
    def update_percentage(self, percentage: int) -> None:
        """Update progress bar with percentage"""
        self.progressBar.setValue(percentage)
        self.progress_widget.set_progress(percentage)
    
    def update_status_message(self, message: str) -> None:
        """Update status message"""
        self.statusBar().showMessage(message)
        self.progress_widget.set_text(message)
    
    def update_milestone(self, milestone: str, percentage: int) -> None:
        """Update milestone progress"""
        self.statusBar().showMessage(f"{milestone} ({percentage}%)")
    
    def update_time_estimate(self, estimate: str) -> None:
        """Update time estimate display"""
        self.progress_widget.set_text(f"{self.progress_widget.text()} - {estimate}")
        
    def handle_results(self, results: object) -> None:
        """Display calculation/verification results"""
        self.resultsArea.clear()
        if isinstance(results, dict):
            for path, checksum in results.items():
                self.resultsArea.append(f"{path}: {checksum}")
        else:
            self.resultsArea.append(str(results))
        show_info_dialog("Checksum calculation completed", parent=self)
            
    def handle_error(self, error_msg: str) -> None:
        """Display error message"""
        show_error_dialog("Error", error_msg, parent=self)
        
    def calculation_finished(self) -> None:
        """Clean up after calculation is complete"""
        if self.checksum_thread:
            self.checksum_thread.quit()
            self.checksum_thread.wait()
            
        # Re-enable UI elements
        self.calculateButton.setEnabled(True)
        self.browseButton.setEnabled(True)
        self.clearButton.setEnabled(True)
        self.saveButton.setEnabled(True)
        self.progressBar.setValue(0)
        self.progress_widget.hide()
        
    def clear_results(self) -> None:
        """Clear the results area"""
        self.resultsArea.clear()
        self.progressBar.setValue(0)
        
    def save_results(self) -> None:
        """Save results to a file"""
        if not self.resultsArea.toPlainText():
            show_error_dialog("No results to save", parent=self)
            return
            
        filename: str = str(get_save_file_name(
            parent=self,
            caption="Save Results",
            file_filter="Text Files (*.txt);;All Files (*.*)"
        ) or "")
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(self.resultsArea.toPlainText())
                show_info_dialog("Results saved successfully", parent=self)
            except Exception as e:
                show_error_dialog(
                    "Error",
                    f"Failed to save results: {e}",
                    parent=self
                )


if __name__ == '__main__':
    app: QApplication = QApplication(sys.argv)
    window: ChecksumGUI = ChecksumGUI()
    window.show()
    sys.exit(app.exec_())