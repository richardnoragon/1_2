"""
Privacy Tools Hub GUI

Main interface for accessing all privacy cleaning tools.
Provides a unified interface with tabs for each tool category.
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QLabel, QPushButton, QGroupBox, QCheckBox, QComboBox,
    QSpinBox, QLineEdit, QTextEdit, QProgressBar, QMessageBox,
    QListWidget, QListWidgetItem, QSplitter, QFrame
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon

# Import the main project's GUI components
sys.path.append(str(Path(__file__).parent.parent.parent))
from gui.standard_window import StandardWindow
from gui.themes import ThemeManager, Colors, Fonts

# Import privacy tools
from ..tools.secure_empty_trash import SecureEmptyTrashTool
from ..tools.delete_cookies import DeleteCookiesTool
from ..core.browser_detector import BrowserDetector
from ..core.platform_utils import PlatformUtils


class PrivacyToolsHub(StandardWindow):
    """Main hub for privacy cleaning tools."""
    
    def __init__(self):
        super().__init__("Privacy Tools - Richard's File Utilities")
        self.setMinimumSize(900, 700)
        self.resize(1000, 800)
        
        # Initialize tools
        self.tools = {
            'trash': SecureEmptyTrashTool(),
            'cookies': DeleteCookiesTool()
        }
        
        # Initialize browser detector
        self.browser_detector = BrowserDetector()
        
        # Current operation thread
        self.current_thread = None
        
        self._setup_ui()
        self._connect_signals()
        self._refresh_browser_info()
    
    def _setup_ui(self):
        """Setup the user interface."""
        # Create main tab widget
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        
        # Create tabs for each tool category
        self._create_trash_tab()
        self._create_cookies_tab()
        self._create_history_tab()
        self._create_file_history_tab()
        self._create_downloads_tab()
        self._create_overview_tab()
    
    def _create_overview_tab(self):
        """Create overview tab showing system status."""
        overview_widget = QWidget()
        layout = QVBoxLayout(overview_widget)
        
        # Header
        header = self.create_header("Privacy Tools Overview")
        layout.addWidget(header)
        
        # System info group
        system_group = self.create_group_box("System Information")
        system_layout = QVBoxLayout()
        
        platform_label = QLabel(f"Platform: {PlatformUtils.get_platform().title()}")
        ThemeManager.style_label(platform_label)
        system_layout.addWidget(platform_label)
        
        admin_status = "Administrator" if PlatformUtils.is_admin() else "Standard User"
        admin_label = QLabel(f"Privileges: {admin_status}")
        ThemeManager.style_label(admin_label)
        system_layout.addWidget(admin_label)
        
        system_group.setLayout(system_layout)
        layout.addWidget(system_group)
        
        # Browser info group
        browser_group = self.create_group_box("Detected Browsers")
        browser_layout = QVBoxLayout()
        
        self.browser_list = QListWidget()
        browser_layout.addWidget(self.browser_list)
        
        refresh_btn = self.create_button("Refresh Browser Info", 
                                       self._refresh_browser_info)
        browser_layout.addWidget(refresh_btn)
        
        browser_group.setLayout(browser_layout)
        layout.addWidget(browser_group)
        
        # Quick actions group
        actions_group = self.create_group_box("Quick Actions")
        actions_layout = QVBoxLayout()
        
        quick_clean_btn = self.create_button("Quick Clean All", 
                                           self._quick_clean_all, primary=True)
        actions_layout.addWidget(quick_clean_btn)
        
        actions_group.setLayout(actions_layout)
        layout.addWidget(actions_group)
        
        self.tab_widget.addTab(overview_widget, "Overview")
    
    def _create_trash_tab(self):
        """Create secure empty trash tab."""
        trash_widget = QWidget()
        layout = QVBoxLayout(trash_widget)
        
        # Header
        header = self.create_header("Secure Empty Trash")
        layout.addWidget(header)
        
        # Options group
        options_group = self.create_group_box("Options")
        options_layout = QVBoxLayout()
        
        self.trash_secure_check = QCheckBox("Secure deletion (overwrite files)")
        self.trash_backup_check = QCheckBox("Create backup before deletion")
        
        options_layout.addWidget(self.trash_secure_check)
        options_layout.addWidget(self.trash_backup_check)
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Preview group
        preview_group = self.create_group_box("Preview")
        preview_layout = QVBoxLayout()
        
        self.trash_preview_text = QTextEdit()
        self.trash_preview_text.setMaximumHeight(150)
        preview_layout.addWidget(self.trash_preview_text)
        
        preview_btn = self.create_button("Preview Operation", 
                                       self._preview_trash_operation)
        preview_layout.addWidget(preview_btn)
        
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        empty_trash_btn = self.create_button("Empty Trash", 
                                           self._execute_trash_operation, 
                                           primary=True)
        button_layout.addWidget(empty_trash_btn)
        layout.addLayout(button_layout)
        
        # Progress
        self.trash_progress = self.create_progress_bar()
        self.trash_progress.setVisible(False)
        layout.addWidget(self.trash_progress)
        
        self.tab_widget.addTab(trash_widget, "Empty Trash")
    
    def _create_cookies_tab(self):
        """Create delete cookies tab."""
        cookies_widget = QWidget()
        layout = QVBoxLayout(cookies_widget)
        
        # Header
        header = self.create_header("Delete Browser Cookies")
        layout.addWidget(header)
        
        # Browser selection group
        browser_group = self.create_group_box("Browser Selection")
        browser_layout = QVBoxLayout()
        
        self.browser_checkboxes = {}
        for browser in ['chrome', 'firefox', 'edge', 'safari']:
            checkbox = QCheckBox(browser.title())
            checkbox.setChecked(True)
            self.browser_checkboxes[browser] = checkbox
            browser_layout.addWidget(checkbox)
        
        browser_group.setLayout(browser_layout)
        layout.addWidget(browser_group)
        
        # Filter options group
        filter_group = self.create_group_box("Filter Options")
        filter_layout = QVBoxLayout()
        
        # Domain filter
        domain_layout = QHBoxLayout()
        domain_layout.addWidget(QLabel("Domain filter:"))
        self.domain_filter_edit = QLineEdit()
        self.domain_filter_edit.setPlaceholderText("e.g., google.com (optional)")
        domain_layout.addWidget(self.domain_filter_edit)
        filter_layout.addLayout(domain_layout)
        
        # Age filter
        age_layout = QHBoxLayout()
        age_layout.addWidget(QLabel("Delete cookies older than:"))
        self.age_spinbox = QSpinBox()
        self.age_spinbox.setRange(0, 365)
        self.age_spinbox.setValue(0)
        self.age_spinbox.setSuffix(" days (0 = all)")
        age_layout.addWidget(self.age_spinbox)
        filter_layout.addLayout(age_layout)
        
        # Backup option
        self.cookies_backup_check = QCheckBox("Create backup before deletion")
        filter_layout.addWidget(self.cookies_backup_check)
        
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)
        
        # Preview group
        preview_group = self.create_group_box("Preview")
        preview_layout = QVBoxLayout()
        
        self.cookies_preview_text = QTextEdit()
        self.cookies_preview_text.setMaximumHeight(150)
        preview_layout.addWidget(self.cookies_preview_text)
        
        preview_btn = self.create_button("Preview Operation", 
                                       self._preview_cookies_operation)
        preview_layout.addWidget(preview_btn)
        
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        delete_cookies_btn = self.create_button("Delete Cookies", 
                                              self._execute_cookies_operation, 
                                              primary=True)
        button_layout.addWidget(delete_cookies_btn)
        layout.addLayout(button_layout)
        
        # Progress
        self.cookies_progress = self.create_progress_bar()
        self.cookies_progress.setVisible(False)
        layout.addWidget(self.cookies_progress)
        
        self.tab_widget.addTab(cookies_widget, "Delete Cookies")
    
    def _create_history_tab(self):
        """Create delete history tab (placeholder)."""
        history_widget = QWidget()
        layout = QVBoxLayout(history_widget)
        
        header = self.create_header("Delete Browser History")
        layout.addWidget(header)
        
        info_label = QLabel("Browser history deletion tool will be implemented here.")
        ThemeManager.style_label(info_label)
        layout.addWidget(info_label)
        
        self.tab_widget.addTab(history_widget, "Delete History")
    
    def _create_file_history_tab(self):
        """Create delete file history tab (placeholder)."""
        file_history_widget = QWidget()
        layout = QVBoxLayout(file_history_widget)
        
        header = self.create_header("Delete File History")
        layout.addWidget(header)
        
        info_label = QLabel("File history deletion tool will be implemented here.")
        ThemeManager.style_label(info_label)
        layout.addWidget(info_label)
        
        self.tab_widget.addTab(file_history_widget, "Delete File History")
    
    def _create_downloads_tab(self):
        """Create delete downloads tab (placeholder)."""
        downloads_widget = QWidget()
        layout = QVBoxLayout(downloads_widget)
        
        header = self.create_header("Delete Browser Downloads")
        layout.addWidget(header)
        
        info_label = QLabel("Browser downloads deletion tool will be implemented here.")
        ThemeManager.style_label(info_label)
        layout.addWidget(info_label)
        
        self.tab_widget.addTab(downloads_widget, "Delete Downloads")
    
    def _connect_signals(self):
        """Connect tool signals to GUI updates."""
        for tool in self.tools.values():
            tool.progress_updated.connect(self._update_progress)
            tool.operation_complete.connect(self._operation_complete)
            tool.error_occurred.connect(self._show_error)
            tool.status_changed.connect(self._update_status)
    
    def _refresh_browser_info(self):
        """Refresh browser detection information."""
        self.browser_list.clear()
        
        detected_browsers = self.browser_detector.detect_installed_browsers()
        running_browsers = self.browser_detector.get_running_browsers()
        
        for browser in detected_browsers:
            status = "Running" if browser in running_browsers else "Closed"
            item_text = f"{browser.title()} - {status}"
            
            item = QListWidgetItem(item_text)
            if browser in running_browsers:
                item.setForeground(Colors.WARNING)
            else:
                item.setForeground(Colors.SUCCESS)
            
            self.browser_list.addItem(item)
        
        if not detected_browsers:
            item = QListWidgetItem("No supported browsers detected")
            item.setForeground(Colors.TEXT_DISABLED)
            self.browser_list.addItem(item)
    
    def _preview_trash_operation(self):
        """Preview trash emptying operation."""
        secure_delete = self.trash_secure_check.isChecked()
        
        try:
            preview = self.tools['trash'].preview_operation(secure_delete=secure_delete)
            
            preview_text = f"Platform: {preview['platform'].title()}\n"
            preview_text += f"Secure deletion: {'Yes' if secure_delete else 'No'}\n"
            preview_text += f"Items to delete: {len(preview['trash_items'])}\n"
            
            if preview['trash_items']:
                preview_text += "\nItems:\n"
                for item in preview['trash_items'][:10]:  # Show first 10 items
                    preview_text += f"  - {item}\n"
                if len(preview['trash_items']) > 10:
                    preview_text += f"  ... and {len(preview['trash_items']) - 10} more\n"
            
            if preview['warnings']:
                preview_text += "\nWarnings:\n"
                for warning in preview['warnings']:
                    preview_text += f"  ! {warning}\n"
            
            self.trash_preview_text.setPlainText(preview_text)
            
        except Exception as e:
            self.show_error_dialog("Preview Error", f"Failed to preview operation: {str(e)}")
    
    def _preview_cookies_operation(self):
        """Preview cookies deletion operation."""
        selected_browsers = [browser for browser, checkbox in self.browser_checkboxes.items() 
                           if checkbox.isChecked()]
        
        domain_filter = self.domain_filter_edit.text().strip() or None
        days_old = self.age_spinbox.value() if self.age_spinbox.value() > 0 else None
        
        try:
            preview = self.tools['cookies'].preview_operation(
                browsers=selected_browsers,
                domain_filter=domain_filter,
                days_old=days_old
            )
            
            preview_text = f"Selected browsers: {', '.join(b.title() for b in selected_browsers)}\n"
            if domain_filter:
                preview_text += f"Domain filter: {domain_filter}\n"
            if days_old:
                preview_text += f"Age filter: older than {days_old} days\n"
            
            preview_text += "\nEstimated cookies to delete:\n"
            total_cookies = 0
            for browser, count in preview['estimated_cookies'].items():
                preview_text += f"  {browser.title()}: {count} cookies\n"
                total_cookies += count
            
            preview_text += f"\nTotal: {total_cookies} cookies\n"
            
            if preview['warnings']:
                preview_text += "\nWarnings:\n"
                for warning in preview['warnings']:
                    preview_text += f"  ! {warning}\n"
            
            self.cookies_preview_text.setPlainText(preview_text)
            
        except Exception as e:
            self.show_error_dialog("Preview Error", f"Failed to preview operation: {str(e)}")
    
    def _execute_trash_operation(self):
        """Execute trash emptying operation."""
        secure_delete = self.trash_secure_check.isChecked()
        create_backup = self.trash_backup_check.isChecked()
        
        self.trash_progress.setVisible(True)
        self.trash_progress.setRange(0, 0)  # Indeterminate progress
        
        def execute():
            return self.tools['trash'].execute_operation(
                secure_delete=secure_delete,
                create_backup=create_backup
            )
        
        self.current_thread = self.tools['trash'].run_in_thread(execute)
    
    def _execute_cookies_operation(self):
        """Execute cookies deletion operation."""
        selected_browsers = [browser for browser, checkbox in self.browser_checkboxes.items() 
                           if checkbox.isChecked()]
        
        if not selected_browsers:
            self.show_error_dialog("No Browsers Selected", 
                                 "Please select at least one browser.")
            return
        
        domain_filter = self.domain_filter_edit.text().strip() or None
        days_old = self.age_spinbox.value() if self.age_spinbox.value() > 0 else None
        create_backup = self.cookies_backup_check.isChecked()
        
        self.cookies_progress.setVisible(True)
        self.cookies_progress.setRange(0, len(selected_browsers))
        
        def execute():
            return self.tools['cookies'].execute_operation(
                browsers=selected_browsers,
                domain_filter=domain_filter,
                days_old=days_old,
                create_backup=create_backup
            )
        
        self.current_thread = self.tools['cookies'].run_in_thread(execute)
    
    def _quick_clean_all(self):
        """Execute quick clean of all privacy data."""
        reply = QMessageBox.question(
            self, "Quick Clean All",
            "This will delete cookies from all browsers and empty the trash.\n"
            "Are you sure you want to continue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Set all browser checkboxes
            for checkbox in self.browser_checkboxes.values():
                checkbox.setChecked(True)
            
            # Execute cookies operation first, then trash
            self._execute_cookies_operation()
    
    def _update_progress(self, current, total, message):
        """Update progress bars."""
        # Determine which progress bar to update based on current tab
        current_tab = self.tab_widget.currentIndex()
        
        if current_tab == 1:  # Trash tab
            if total > 0:
                self.trash_progress.setRange(0, total)
                self.trash_progress.setValue(current)
            self.show_status_message(message)
        elif current_tab == 2:  # Cookies tab
            if total > 0:
                self.cookies_progress.setRange(0, total)
                self.cookies_progress.setValue(current)
            self.show_status_message(message)
    
    def _operation_complete(self, result):
        """Handle operation completion."""
        # Hide progress bars
        self.trash_progress.setVisible(False)
        self.cookies_progress.setVisible(False)
        
        if result.success:
            self.show_info_dialog("Operation Complete", result.message)
        else:
            error_details = "\n".join(result.errors) if result.errors else "Unknown error"
            self.show_error_dialog("Operation Failed", 
                                 f"{result.message}\n\nDetails:\n{error_details}")
        
        # Refresh browser info
        self._refresh_browser_info()
    
    def _show_error(self, message):
        """Show error message."""
        self.show_error_dialog("Error", message)
    
    def _update_status(self, message):
        """Update status message."""
        self.show_status_message(message)
    
    def closeEvent(self, event):
        """Handle window close event."""
        if self.current_thread and self.current_thread.isRunning():
            reply = QMessageBox.question(
                self, "Operation in Progress",
                "An operation is currently running. Do you want to stop it and exit?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # Stop all tools
                for tool in self.tools.values():
                    tool.stop_operation()
                
                # Wait for threads to finish
                if self.current_thread:
                    self.current_thread.quit()
                    self.current_thread.wait(3000)  # Wait up to 3 seconds
                
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


def main():
    """Main function for standalone execution."""
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    window = PrivacyToolsHub()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()