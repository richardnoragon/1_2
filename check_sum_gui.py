import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from PyQt5.QtCore import QThread
from PyQt5 import uic
from check_sum import ChecksumLogic


class ChecksumGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        # Get the directory containing this script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_file = os.path.join(current_dir, 'check_sum.ui')
        uic.loadUi(ui_file, self)
        
        # Connect signals
        self.browseButton.clicked.connect(self.browse_file)
        self.calculateButton.clicked.connect(self.start_calculation)
        self.clearButton.clicked.connect(self.clear_results)
        self.saveButton.clicked.connect(self.save_results)
        self.modeCombo.currentTextChanged.connect(self.update_ui_state)
        
        # Initialize state
        self.checksum_thread = None
        self.checksum_worker = None
        self.update_ui_state()
        
    def update_ui_state(self):
        """Update UI elements based on current mode"""
        mode = self.modeCombo.currentText()
        is_verify_mode = 'Verify' in mode
        self.checksumInput.setVisible(is_verify_mode)
        self.checksumInput.setEnabled(is_verify_mode)
        
    def browse_file(self):
        """Open file dialog to select file or directory"""
        mode = self.modeCombo.currentText()
        if 'Directory' in mode:
            path = QFileDialog.getExistingDirectory(self, "Select Directory")
        else:
            path, _ = QFileDialog.getOpenFileName(self, "Select File")
            
        if path:
            self.filePathInput.setText(path)
            
    def start_calculation(self):
        """Start the checksum calculation/verification process"""
        path = self.filePathInput.text()
        if not path:
            QMessageBox.warning(
                self, 
                "Error", 
                "Please select a file or directory"
            )
            return
            
        if not os.path.exists(path):
            QMessageBox.warning(self, "Error", "Selected path does not exist")
            return
            
        # Determine mode
        mode_text = self.modeCombo.currentText().lower()
        if 'directory' in mode_text:
            mode = ('calculate_dir' if 'calculate' in mode_text 
                   else 'verify_dir')
        else:
            mode = ('calculate_file' if 'calculate' in mode_text 
                   else 'verify_file')
            
        # Get algorithm
        algorithm = self.algorithmCombo.currentText().lower().replace('-', '')
        
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
        
    def update_progress(self, current, total):
        """Update progress bar"""
        percentage = (current / total) * 100 if total > 0 else 0
        self.progressBar.setValue(int(percentage))
        
    def handle_results(self, results):
        """Display calculation/verification results"""
        self.resultsArea.clear()
        if isinstance(results, dict):
            for path, checksum in results.items():
                self.resultsArea.append(f"{path}: {checksum}")
        else:
            self.resultsArea.append(str(results))
            
    def handle_error(self, error_msg):
        """Display error message"""
        QMessageBox.warning(self, "Error", error_msg)
        
    def calculation_finished(self):
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
        
    def clear_results(self):
        """Clear the results area"""
        self.resultsArea.clear()
        self.progressBar.setValue(0)
        
    def save_results(self):
        """Save results to a file"""
        if not self.resultsArea.toPlainText():
            QMessageBox.warning(self, "Error", "No results to save")
            return
            
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Results",
            "",
            "Text Files (*.txt);;All Files (*.*)"
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(self.resultsArea.toPlainText())
                QMessageBox.information(
                    self, 
                    "Success",
                    "Results saved successfully"
                )
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Error",
                    f"Failed to save results: {e}"
                )


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ChecksumGUI()
    window.show()
    sys.exit(app.exec_())