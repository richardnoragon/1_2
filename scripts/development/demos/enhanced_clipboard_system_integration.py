"""
Enhanced Clipboard System Tools Integration

This module provides the integration layer between the Enhanced Clipboard Manager
and the RFU System Tools tab, following established patterns from other tools.

Author: Richard's File Utilities  
Version: 1.0.0
Date: August 7, 2025
"""

import os
import sys
from typing import Optional

try:
    from PyQt5.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
        QFrame, QGroupBox, QTextEdit, QMessageBox, QApplication
    )
    from PyQt5.QtCore import Qt, pyqtSignal, QTimer
    from PyQt5.QtGui import QFont, QIcon, QPixmap
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

try:
    from enhanced_clipboard_main_window import EnhancedClipboardMainWindow
    CLIPBOARD_MAIN_AVAILABLE = True
except ImportError:
    CLIPBOARD_MAIN_AVAILABLE = False

try:
    from enhanced_clipboard_manager import ClipboardDatabase
    CLIPBOARD_CORE_AVAILABLE = True
except ImportError:
    CLIPBOARD_CORE_AVAILABLE = False


class EnhancedClipboardSystemWidget(QWidget):
    """
    Enhanced Clipboard widget for System Tools tab integration.
    
    This widget provides a comprehensive clipboard management interface
    that integrates seamlessly with the RFU System Tools tab while
    offering advanced clipboard functionality.
    """
    
    # Signals for RFU integration
    operation_started = pyqtSignal(str, str)  # operation_name, description
    operation_completed = pyqtSignal(str, bool, str)  # operation_name, success, message
    status_update = pyqtSignal(str)  # status_message
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.clipboard_window = None
        self.clipboard_database = None
        self.setup_ui()
        self.setup_clipboard_integration()
        self.setup_system_monitoring()
        
    def setup_ui(self):
        """Setup the System Tools integration UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header section
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.StyledPanel)
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        header_layout = QVBoxLayout(header_frame)
        
        # Title
        title_label = QLabel("📋 Enhanced Clipboard Manager")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel(
            "Comprehensive clipboard management system with multi-panel interface,\\n"
            "searchable database, cloud sync, templates, and advanced features."
        )
        desc_label.setFont(QFont("Segoe UI", 10))
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setStyleSheet("color: #6c757d;")
        header_layout.addWidget(desc_label)
        
        layout.addWidget(header_frame)
        
        # Main features section
        features_group = QGroupBox("🚀 Key Features")
        features_group.setFont(QFont("Segoe UI", 12, QFont.Bold))
        features_layout = QVBoxLayout(features_group)
        
        # Feature highlights
        features = [
            "📜 Multi-panel history view with timestamped entries",
            "🔍 Searchable database with advanced filtering",
            "⭐ Favorites system with ratings and categories", 
            "📄 Template manager with variable substitution",
            "☁️ Cloud synchronization across devices",
            "🔧 Advanced text processing and formatting",
            "🎛️ Customizable hotkeys and shortcuts",
            "🔄 Floating widget for always-on access",
            "🔐 Data encryption for sensitive content",
            "📊 Usage statistics and analytics",
            "🗑️ Intelligent cleanup and duplicate detection",
            "📁 Import/export with multiple formats"
        ]
        
        for feature in features:
            feature_label = QLabel(feature)
            feature_label.setFont(QFont("Segoe UI", 9))
            feature_label.setStyleSheet("color: #495057; margin: 2px 0;")
            features_layout.addWidget(feature_label)
        
        layout.addWidget(features_group)
        
        # Action buttons section
        actions_group = QGroupBox("🎯 Quick Actions")
        actions_group.setFont(QFont("Segoe UI", 12, QFont.Bold))
        actions_layout = QVBoxLayout(actions_group)
        
        # Main action buttons
        buttons_layout = QHBoxLayout()
        
        self.launch_btn = QPushButton("🚀 Launch Clipboard Manager")
        self.launch_btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.launch_btn.setMinimumHeight(45)
        self.launch_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
        """)
        self.launch_btn.clicked.connect(self.launch_clipboard_manager)
        buttons_layout.addWidget(self.launch_btn)
        
        self.floating_btn = QPushButton("🔄 Floating Widget")
        self.floating_btn.setFont(QFont("Segoe UI", 10))
        self.floating_btn.setMinimumHeight(45)
        self.floating_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #1e7e34;
            }
            QPushButton:pressed {
                background-color: #155724;
            }
        """)
        self.floating_btn.clicked.connect(self.toggle_floating_widget)
        buttons_layout.addWidget(self.floating_btn)
        
        actions_layout.addLayout(buttons_layout)
        
        # Secondary action buttons
        secondary_layout = QHBoxLayout()
        
        self.history_btn = QPushButton("📜 View History")
        self.history_btn.clicked.connect(self.show_clipboard_history)
        secondary_layout.addWidget(self.history_btn)
        
        self.templates_btn = QPushButton("📄 Templates")
        self.templates_btn.clicked.connect(self.show_templates)
        secondary_layout.addWidget(self.templates_btn)
        
        self.stats_btn = QPushButton("📊 Statistics")
        self.stats_btn.clicked.connect(self.show_statistics)
        secondary_layout.addWidget(self.stats_btn)
        
        self.settings_btn = QPushButton("⚙️ Settings")
        self.settings_btn.clicked.connect(self.show_settings)
        secondary_layout.addWidget(self.settings_btn)
        
        # Style secondary buttons
        for btn in [self.history_btn, self.templates_btn, self.stats_btn, self.settings_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #6c757d;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 6px 12px;
                    margin: 2px;
                }
                QPushButton:hover {
                    background-color: #545b62;
                }
                QPushButton:pressed {
                    background-color: #3d4043;
                }
            """)
        
        actions_layout.addLayout(secondary_layout)
        layout.addWidget(actions_group)
        
        # Status section
        status_group = QGroupBox("📈 Current Status")
        status_group.setFont(QFont("Segoe UI", 12, QFont.Bold))
        status_layout = QVBoxLayout(status_group)
        
        self.status_text = QTextEdit()
        self.status_text.setMaximumHeight(120)
        self.status_text.setReadOnly(True)
        self.status_text.setFont(QFont("Consolas", 9))
        self.status_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        status_layout.addWidget(self.status_text)
        
        layout.addWidget(status_group)
        
        # Utility buttons
        utility_layout = QHBoxLayout()
        
        self.clear_clipboard_btn = QPushButton("🗑️ Clear System Clipboard")
        self.clear_clipboard_btn.clicked.connect(self.clear_system_clipboard)
        utility_layout.addWidget(self.clear_clipboard_btn)
        
        self.backup_btn = QPushButton("💾 Backup Clipboard Data")
        self.backup_btn.clicked.connect(self.backup_clipboard_data)
        utility_layout.addWidget(self.backup_btn)
        
        self.restore_btn = QPushButton("📁 Restore Clipboard Data")
        self.restore_btn.clicked.connect(self.restore_clipboard_data)
        utility_layout.addWidget(self.restore_btn)
        
        # Style utility buttons
        for btn in [self.clear_clipboard_btn, self.backup_btn, self.restore_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #dc3545;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 6px 12px;
                    margin: 2px;
                }
                QPushButton:hover {
                    background-color: #c82333;
                }
                QPushButton:pressed {
                    background-color: #bd2130;
                }
            """)
        
        layout.addLayout(utility_layout)
        layout.addStretch()
        
        # Initialize status
        self.update_status("Enhanced Clipboard Manager ready - System Tools integration active")
    
    def setup_clipboard_integration(self):
        """Setup clipboard monitoring and integration."""
        try:
            # Initialize clipboard database for monitoring
            from PyQt5.QtCore import QStandardPaths
            db_path = os.path.join(
                QStandardPaths.writableLocation(QStandardPaths.AppDataLocation),
                "clipboard_history.db"
            )
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            
            if CLIPBOARD_CORE_AVAILABLE:
                self.clipboard_database = ClipboardDatabase(db_path)
                self.update_status("Clipboard database initialized successfully")
            else:
                self.update_status("Warning: Clipboard core components not available")
                
        except Exception as e:
            self.update_status(f"Error initializing clipboard integration: {e}")
    
    def setup_system_monitoring(self):
        """Setup system clipboard monitoring."""
        try:
            # Monitor system clipboard
            self.clipboard = QApplication.clipboard()
            self.clipboard.dataChanged.connect(self.on_clipboard_changed)
            
            # Status update timer
            self.status_timer = QTimer()
            self.status_timer.timeout.connect(self.update_clipboard_stats)
            self.status_timer.start(5000)  # Update every 5 seconds
            
            self.update_status("System clipboard monitoring active")
            
        except Exception as e:
            self.update_status(f"Error setting up system monitoring: {e}")
    
    def update_status(self, message: str):
        """Update status display."""
        timestamp = "[" + str(QTimer().isActive()).replace("True", "Active").replace("False", "Inactive") + "]"
        current_time = "⏰ " + QTimer().objectName() if hasattr(QTimer(), 'objectName') else "⏰"
        
        status_line = f"{current_time} {message}"
        
        # Add to status text (keep last 10 lines)
        current_text = self.status_text.toPlainText()
        lines = current_text.split('\\n')
        if len(lines) >= 10:
            lines = lines[-9:]  # Keep last 9 lines
        
        lines.append(status_line)
        self.status_text.setPlainText('\\n'.join(lines))
        
        # Scroll to bottom
        cursor = self.status_text.textCursor()
        cursor.movePosition(cursor.End)
        self.status_text.setTextCursor(cursor)
        
        # Emit status signal for RFU integration
        self.status_update.emit(message)
    
    def launch_clipboard_manager(self):
        """Launch the main Enhanced Clipboard Manager window."""
        self.operation_started.emit("Launch Clipboard Manager", "Opening comprehensive clipboard management interface")
        
        try:
            if not CLIPBOARD_MAIN_AVAILABLE:
                QMessageBox.warning(
                    self, "Feature Unavailable",
                    "The Enhanced Clipboard Manager components are not available.\\n"
                    "Please ensure all required modules are installed."
                )
                self.operation_completed.emit("Launch Clipboard Manager", False, "Required components not available")
                return
            
            # Create or show existing window
            if self.clipboard_window is None:
                self.clipboard_window = EnhancedClipboardMainWindow()
                self.clipboard_window.setAttribute(Qt.WA_DeleteOnClose, False)
            
            self.clipboard_window.show()
            self.clipboard_window.raise_()
            self.clipboard_window.activateWindow()
            
            self.update_status("Enhanced Clipboard Manager window opened successfully")
            self.operation_completed.emit("Launch Clipboard Manager", True, "Clipboard manager launched successfully")
            
        except Exception as e:
            error_msg = f"Failed to launch clipboard manager: {e}"
            self.update_status(error_msg)
            QMessageBox.critical(self, "Launch Error", error_msg)
            self.operation_completed.emit("Launch Clipboard Manager", False, error_msg)
    
    def toggle_floating_widget(self):
        """Toggle the floating clipboard widget."""
        self.operation_started.emit("Toggle Floating Widget", "Toggling floating clipboard widget visibility")
        
        try:
            if self.clipboard_window is None:
                # Create window first if it doesn't exist
                self.launch_clipboard_manager()
                return
            
            # Toggle floating widget
            if hasattr(self.clipboard_window, 'toggle_floating_widget'):
                self.clipboard_window.toggle_floating_widget()
                self.update_status("Floating widget toggled")
                self.operation_completed.emit("Toggle Floating Widget", True, "Floating widget toggled successfully")
            else:
                self.update_status("Floating widget not available")
                self.operation_completed.emit("Toggle Floating Widget", False, "Floating widget not available")
                
        except Exception as e:
            error_msg = f"Failed to toggle floating widget: {e}"
            self.update_status(error_msg)
            self.operation_completed.emit("Toggle Floating Widget", False, error_msg)
    
    def show_clipboard_history(self):
        """Show clipboard history view."""
        self.operation_started.emit("Show History", "Opening clipboard history view")
        
        try:
            # Launch main window and switch to history tab
            if self.clipboard_window is None:
                self.launch_clipboard_manager()
            else:
                self.clipboard_window.show()
                self.clipboard_window.raise_()
                
                # Switch to history tab if available
                if hasattr(self.clipboard_window, 'tab_widget'):
                    self.clipboard_window.tab_widget.setCurrentIndex(0)  # History tab
            
            self.update_status("Clipboard history view displayed")
            self.operation_completed.emit("Show History", True, "History view opened")
            
        except Exception as e:
            error_msg = f"Failed to show history: {e}"
            self.update_status(error_msg)
            self.operation_completed.emit("Show History", False, error_msg)
    
    def show_templates(self):
        """Show clipboard templates."""
        self.operation_started.emit("Show Templates", "Opening clipboard templates manager")
        
        try:
            # Launch main window and switch to templates tab
            if self.clipboard_window is None:
                self.launch_clipboard_manager()
            else:
                self.clipboard_window.show()
                self.clipboard_window.raise_()
                
                # Switch to templates tab if available
                if hasattr(self.clipboard_window, 'tab_widget'):
                    self.clipboard_window.tab_widget.setCurrentIndex(1)  # Templates tab
            
            self.update_status("Clipboard templates manager displayed")
            self.operation_completed.emit("Show Templates", True, "Templates manager opened")
            
        except Exception as e:
            error_msg = f"Failed to show templates: {e}"
            self.update_status(error_msg)
            self.operation_completed.emit("Show Templates", False, error_msg)
    
    def show_statistics(self):
        """Show clipboard statistics."""
        self.operation_started.emit("Show Statistics", "Opening clipboard usage statistics")
        
        try:
            # Launch main window and switch to statistics tab
            if self.clipboard_window is None:
                self.launch_clipboard_manager()
            else:
                self.clipboard_window.show()
                self.clipboard_window.raise_()
                
                # Switch to statistics tab if available
                if hasattr(self.clipboard_window, 'tab_widget'):
                    self.clipboard_window.tab_widget.setCurrentIndex(2)  # Statistics tab
            
            self.update_status("Clipboard statistics dashboard displayed")
            self.operation_completed.emit("Show Statistics", True, "Statistics dashboard opened")
            
        except Exception as e:
            error_msg = f"Failed to show statistics: {e}"
            self.update_status(error_msg)
            self.operation_completed.emit("Show Statistics", False, error_msg)
    
    def show_settings(self):
        """Show clipboard settings."""
        self.operation_started.emit("Show Settings", "Opening clipboard settings configuration")
        
        try:
            # Launch main window and switch to settings tab
            if self.clipboard_window is None:
                self.launch_clipboard_manager()
            else:
                self.clipboard_window.show()
                self.clipboard_window.raise_()
                
                # Switch to settings tab if available
                if hasattr(self.clipboard_window, 'tab_widget'):
                    self.clipboard_window.tab_widget.setCurrentIndex(3)  # Settings tab
            
            self.update_status("Clipboard settings configuration displayed")
            self.operation_completed.emit("Show Settings", True, "Settings configuration opened")
            
        except Exception as e:
            error_msg = f"Failed to show settings: {e}"
            self.update_status(error_msg)
            self.operation_completed.emit("Show Settings", False, error_msg)
    
    def clear_system_clipboard(self):
        """Clear the system clipboard."""
        self.operation_started.emit("Clear Clipboard", "Clearing system clipboard content")
        
        try:
            clipboard = QApplication.clipboard()
            clipboard.clear()
            
            self.update_status("System clipboard cleared successfully")
            self.operation_completed.emit("Clear Clipboard", True, "System clipboard cleared")
            
        except Exception as e:
            error_msg = f"Failed to clear clipboard: {e}"
            self.update_status(error_msg)
            self.operation_completed.emit("Clear Clipboard", False, error_msg)
    
    def backup_clipboard_data(self):
        """Backup clipboard data to file."""
        self.operation_started.emit("Backup Data", "Creating clipboard data backup")
        
        try:
            from PyQt5.QtWidgets import QFileDialog
            import json
            from datetime import datetime
            
            # Get save location
            default_name = f"clipboard_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Clipboard Backup", default_name,
                "JSON Files (*.json);;All Files (*.*)"
            )
            
            if file_path and self.clipboard_database:
                # Export clipboard data
                items = self.clipboard_database.get_items()
                backup_data = {
                    'backup_date': datetime.now().isoformat(),
                    'version': '1.0.0',
                    'item_count': len(items),
                    'items': [item.to_dict() for item in items]
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(backup_data, f, indent=2, ensure_ascii=False)
                
                self.update_status(f"Clipboard data backed up to {file_path}")
                self.operation_completed.emit("Backup Data", True, f"Backup created: {file_path}")
            else:
                self.operation_completed.emit("Backup Data", False, "Backup cancelled or database unavailable")
                
        except Exception as e:
            error_msg = f"Failed to backup clipboard data: {e}"
            self.update_status(error_msg)
            self.operation_completed.emit("Backup Data", False, error_msg)
    
    def restore_clipboard_data(self):
        """Restore clipboard data from backup file."""
        self.operation_started.emit("Restore Data", "Restoring clipboard data from backup")
        
        try:
            from PyQt5.QtWidgets import QFileDialog
            import json
            
            # Get restore file
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Select Clipboard Backup", "",
                "JSON Files (*.json);;All Files (*.*)"
            )
            
            if file_path and self.clipboard_database:
                with open(file_path, 'r', encoding='utf-8') as f:
                    backup_data = json.load(f)
                
                # Restore items
                items_data = backup_data.get('items', [])
                restored_count = 0
                
                for item_data in items_data:
                    try:
                        from enhanced_clipboard_manager import ClipboardItem
                        item = ClipboardItem.from_dict(item_data)
                        self.clipboard_database.add_item(item)
                        restored_count += 1
                    except Exception as item_error:
                        self.update_status(f"Failed to restore item: {item_error}")
                
                self.update_status(f"Restored {restored_count} clipboard items from backup")
                self.operation_completed.emit("Restore Data", True, f"Restored {restored_count} items")
            else:
                self.operation_completed.emit("Restore Data", False, "Restore cancelled or database unavailable")
                
        except Exception as e:
            error_msg = f"Failed to restore clipboard data: {e}"
            self.update_status(error_msg)
            self.operation_completed.emit("Restore Data", False, error_msg)
    
    def on_clipboard_changed(self):
        """Handle system clipboard changes."""
        try:
            clipboard = QApplication.clipboard()
            text = clipboard.text()
            
            if text and len(text.strip()) > 0:
                # Log clipboard activity
                preview = text[:50] + "..." if len(text) > 50 else text
                self.update_status(f"Clipboard updated: {preview}")
                
                # Add to database if available
                if self.clipboard_database and CLIPBOARD_CORE_AVAILABLE:
                    from enhanced_clipboard_manager import ClipboardItem
                    item = ClipboardItem(text, "text", "System Monitor")
                    self.clipboard_database.add_item(item)
                    
        except Exception as e:
            self.update_status(f"Error processing clipboard change: {e}")
    
    def update_clipboard_stats(self):
        """Update clipboard statistics in status."""
        try:
            if self.clipboard_database:
                stats = self.clipboard_database.get_statistics()
                total_items = stats.get('total_items', 0)
                pinned_items = stats.get('pinned_items', 0)
                
                self.update_status(f"Stats: {total_items} total items, {pinned_items} pinned")
                
        except Exception as e:
            # Don't spam with error messages for stats updates
            pass
    
    def closeEvent(self, event):
        """Handle widget close event."""
        # Clean up resources
        if self.clipboard_database:
            self.clipboard_database.close()
        
        # Close clipboard window if it exists
        if self.clipboard_window:
            self.clipboard_window.close()
        
        event.accept()


def create_enhanced_clipboard_widget(parent=None):
    """Factory function to create Enhanced Clipboard widget for System Tools integration."""
    return EnhancedClipboardSystemWidget(parent)


# RFU System Tools Integration Point
class EnhancedClipboardGUI:
    """Main class for RFU System Tools integration."""
    
    def __init__(self):
        self.widget = None
    
    def show(self):
        """Show the Enhanced Clipboard interface."""
        if not PYQT_AVAILABLE:
            print("PyQt5 is required to run the Enhanced Clipboard Manager")
            return
        
        if self.widget is None:
            self.widget = EnhancedClipboardSystemWidget()
        
        self.widget.show()
        return self.widget


if __name__ == "__main__":
    # Test the integration widget
    if PYQT_AVAILABLE:
        app = QApplication(sys.argv)
        widget = EnhancedClipboardSystemWidget()
        widget.show()
        sys.exit(app.exec_())
    else:
        print("PyQt5 not available - Enhanced Clipboard integration test skipped")
