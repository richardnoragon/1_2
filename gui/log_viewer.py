import os
from pathlib import Path
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QApplication, QMessageBox
from PyQt5 import uic
import sys
from core.logging_manager import LogManager
from gui.common.base_window import BaseWindow
from gui.common.dialogs import (
    show_error_dialog,
    show_info_dialog,
    get_save_file_name
)


class LogViewerWindow(BaseWindow):
    def __init__(self):
        super().__init__()
        
        # Initialize log manager first
        self.log_manager = LogManager()
        self.logger = self.log_manager.get_logger(__name__)
        self.logger.info("Initializing Log Viewer window")
        
        # Load UI
        try:
            ui_dir = Path(__file__).parent.parent
            ui_file = ui_dir / "log_manager.ui"
            self.logger.debug(f"Loading UI file from: {ui_file}")
            if not ui_file.exists():
                raise FileNotFoundError(f"UI file not found: {ui_file}")
            uic.loadUi(str(ui_file), self)
            self.logger.info("UI file loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to load UI file: {str(e)}")
            show_error_dialog(
                f"Failed to load UI file: {str(e)}",
                title="Fatal Error",
                parent=None
            )
            raise
        
        self.full_content = []
        
        # Connect signals
        self.refreshButton.clicked.connect(self.refresh_logs)
        self.exportButton.clicked.connect(self.export_log)
        self.clearButton.clicked.connect(self.clear_log)
        self.logFileComboBox.currentIndexChanged.connect(self.load_log_content)
        self.filterLevelComboBox.currentTextChanged.connect(self.apply_filters)
        self.searchEdit.textChanged.connect(self.apply_filters)
        
        # Initialize
        self.refresh_logs()
        self.show()
    
    def refresh_logs(self):
        """Refresh the list of available log files"""
        try:
            self.logger.debug("Starting log files refresh")
            self.logFileComboBox.clear()
            
            log_dir = Path(__file__).parent.parent / 'logs'
            log_dir.mkdir(exist_ok=True)
            self.logger.debug(f"Using log directory: {log_dir}")
            
            log_files = [f.name for f in log_dir.glob('*.log')]
            log_files.sort(reverse=True)  # Most recent first
            self.logger.debug(f"Found log files: {log_files}")
            
            self.logFileComboBox.addItems(log_files)
            
            if log_files:
                self.logger.debug("Loading content of first log file")
                self.load_log_content()
            else:
                self.logger.info("No log files found")
            
            self.logger.debug("Log files list refreshed")
            
        except Exception as e:
            logger = self.log_manager.get_logger(__name__)
            logger.error("Failed to refresh log files: %s", str(e))
            show_error_dialog(
                f"Failed to refresh log files: {str(e)}",
                parent=self
            )
    
    def load_log_content(self):
        """Load the content of the selected log file"""
        try:
            current_file = self.logFileComboBox.currentText()
            if not current_file:
                self.logger.debug("No file selected in combo box")
                return
            
            log_dir = Path(__file__).parent.parent / 'logs'
            file_path = log_dir / current_file
            self.logger.debug(f"Loading log file: {file_path}")
            
            if not file_path.exists():
                self.logger.error(f"Log file does not exist: {file_path}")
                raise FileNotFoundError(f"Log file not found: {file_path}")
            
            self.full_content = file_path.read_text(
                encoding='utf-8'
            ).splitlines(keepends=True)
            
            self.logger.debug(f"Loaded {len(self.full_content)} lines")
            self.apply_filters()
            self.logger.debug(f"Log file content loaded: {current_file}")
            
        except Exception as e:
            logger = self.log_manager.get_logger(__name__)
            logger.error("Failed to load log content: %s", str(e))
            show_error_dialog(
                f"Failed to load log content: {str(e)}",
                parent=self
            )
    
    def apply_filters(self):
        """Apply level and search filters to log content"""
        try:
            if not hasattr(self, 'full_content'):
                return
            
            level_filter = self.filterLevelComboBox.currentText()
            search_text = self.searchEdit.text().lower()
            
            filtered_content = []
            for line in self.full_content:
                # Apply level filter
                if level_filter != "All" and level_filter not in line:
                    continue
                
                # Apply search filter
                if search_text and search_text not in line.lower():
                    continue
                
                filtered_content.append(line)
            
            self.logTextEdit.setPlainText(''.join(filtered_content))
            
        except Exception as e:
            logger = self.log_manager.get_logger(__name__)
            logger.error("Failed to apply filters: %s", str(e))
            show_error_dialog(
                f"Failed to apply filters: {str(e)}",
                parent=self
            )
    
    def export_log(self):
        """Export the current log file"""
        try:
            current_file = self.logFileComboBox.currentText()
            if not current_file:
                show_error_dialog(
                    "No log file selected",
                    title="Warning",
                    parent=self
                )
                return
            
            file_name = get_save_file_name(
                "Export Log",
                current_file,
                "Log Files (*.log);;All Files (*)",
                parent=self
            )
            
            if file_name:
                log_dir = Path(__file__).parent.parent / 'logs'
                source_path = log_dir / current_file
                
                with open(file_name, 'w', encoding='utf-8') as target:
                    target.write(source_path.read_text(encoding='utf-8'))
                
                show_info_dialog(
                    "Log file exported successfully",
                    title="Success",
                    parent=self
                )
                
                logger = self.log_manager.get_logger(__name__)
                logger.info("Log file exported to %s", str(file_name))
            
        except Exception as e:
            logger = self.log_manager.get_logger(__name__)
            logger.error("Failed to export log: %s", str(e))
            show_error_dialog(
                f"Failed to export log: {str(e)}",
                parent=self
            )
    
    def clear_log(self):
        """Clear the current log file"""
        try:
            current_file = self.logFileComboBox.currentText()
            if not current_file:
                show_error_dialog(
                    "No log file selected",
                    title="Warning",
                    parent=self
                )
                return
            
            reply = QMessageBox.question(
                self,
                "Confirm Clear",
                f"Are you sure you want to clear {current_file}?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                log_dir = Path(__file__).parent.parent / 'logs'
                file_path = log_dir / current_file
                file_path.write_text('', encoding='utf-8')
                
                self.load_log_content()
                show_info_dialog(
                    "Log file cleared successfully",
                    title="Success",
                    parent=self
                )
                
                logger = self.log_manager.get_logger(__name__)
                logger.info("Log file cleared: %s", current_file)
            
        except Exception as e:
            logger = self.log_manager.get_logger(__name__)
            logger.error("Failed to clear log: %s", str(e))
            show_error_dialog(
                f"Failed to clear log: {str(e)}",
                parent=self
            )


def main():
    """Main entry point for the log viewer GUI."""
    logger = None
    try:
        # Initialize logging first
        log_manager = LogManager()
        logger = log_manager.get_logger(__name__)
        logger.info("Starting Log Viewer application")
        
        # Create Qt application
        app = QApplication(sys.argv)
        logger.debug("Qt Application initialized")
        
        # Create main window
        window = LogViewerWindow()
        logger.info("Log Viewer window created")
        
        # Start event loop
        sys.exit(app.exec_())
    except Exception as e:
        error_msg = f"Failed to start Log Viewer: {str(e)}"
        if logger:
            logger.critical(error_msg, exc_info=True)
        else:
            print(error_msg)
        show_error_dialog(
            error_msg,
            title="Fatal Error"
        )
        sys.exit(1)


if __name__ == '__main__':
    main()
