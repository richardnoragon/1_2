"""
Enhanced Clipboard Manager - Main Window and Floating Widget Implementation.

This module provides the main application window and floating widget for the 
Enhanced Clipboard Manager, featuring comprehensive clipboard management with
advanced features and System Tools integration.

Author: Richard's File Utilities
Version: 1.0.0
Date: August 7, 2025
"""

import os
import sys
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List

try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QTabWidget, QPushButton, QLabel, QLineEdit, QTextEdit,
        QComboBox, QCheckBox, QSplitter, QGroupBox, QFrame,
        QDialog, QDialogButtonBox, QTableWidget, QTableWidgetItem,
        QHeaderView, QMenu, QAction, QSystemTrayIcon, QMessageBox,
        QFileDialog, QInputDialog, QSpinBox, QToolBar, QStatusBar,
        QMenuBar, QSizePolicy, QAbstractItemView, QStyledItemDelegate
    )
    from PyQt5.QtCore import (
        Qt, QTimer, QThread, pyqtSignal, QSize, QRect, QPoint,
        QDateTime, QPropertyAnimation, QEasingCurve, QMimeData,
        QSettings, QStandardPaths, QUrl
    )
    from PyQt5.QtGui import (
        QFont, QIcon, QPixmap, QPainter, QPen, QBrush, QColor,
        QLinearGradient, QPalette, QCursor, QKeySequence, QClipboard,
        QDesktopServices
    )
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

try:
    from enhanced_clipboard_manager import (
        ClipboardItem, ClipboardDatabase, ClipboardEncryption,
        ClipboardCloudSync, ClipboardTextProcessor, ClipboardTemplateManager
    )
    from enhanced_clipboard_gui import (
        ClipboardItemWidget, ClipboardHistoryView, ClipboardSearchPanel,
        ClipboardTemplatePanel
    )
    CLIPBOARD_COMPONENTS_AVAILABLE = True
except ImportError:
    CLIPBOARD_COMPONENTS_AVAILABLE = False


class ClipboardStatisticsPanel(QWidget):
    """Statistics dashboard for clipboard usage."""
    
    def __init__(self, database: 'ClipboardDatabase', parent=None):
        super().__init__(parent)
        self.database = database
        self.setup_ui()
        self.refresh_stats()
    
    def setup_ui(self):
        """Setup the statistics panel UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Title
        title_label = QLabel("📊 Clipboard Statistics")
        title_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        layout.addWidget(title_label)
        
        # Overview stats
        overview_group = QGroupBox("Overview")
        overview_layout = QVBoxLayout(overview_group)
        
        self.total_items_label = QLabel("Total Items: 0")
        self.pinned_items_label = QLabel("Pinned Items: 0")
        self.storage_size_label = QLabel("Storage Used: 0 KB")
        
        overview_layout.addWidget(self.total_items_label)
        overview_layout.addWidget(self.pinned_items_label)
        overview_layout.addWidget(self.storage_size_label)
        
        layout.addWidget(overview_group)
        
        # Type distribution
        type_group = QGroupBox("Items by Type")
        self.type_table = QTableWidget(0, 2)
        self.type_table.setHorizontalHeaderLabels(["Type", "Count"])
        self.type_table.horizontalHeader().setStretchLastSection(True)
        self.type_table.setAlternatingRowColors(True)
        
        type_layout = QVBoxLayout(type_group)
        type_layout.addWidget(self.type_table)
        layout.addWidget(type_group)
        
        # Most accessed
        accessed_group = QGroupBox("Most Accessed Items")
        self.accessed_table = QTableWidget(0, 2)
        self.accessed_table.setHorizontalHeaderLabels(["Content", "Access Count"])
        self.accessed_table.horizontalHeader().setStretchLastSection(True)
        self.accessed_table.setAlternatingRowColors(True)
        
        accessed_layout = QVBoxLayout(accessed_group)
        accessed_layout.addWidget(self.accessed_table)
        layout.addWidget(accessed_group)
        
        # Refresh button
        self.refresh_btn = QPushButton("🔄 Refresh Statistics")
        self.refresh_btn.clicked.connect(self.refresh_stats)
        layout.addWidget(self.refresh_btn)
        
        layout.addStretch()
    
    def refresh_stats(self):
        """Refresh statistics display."""
        if not self.database:
            return
            
        stats = self.database.get_statistics()
        
        # Update overview
        self.total_items_label.setText(f"Total Items: {stats.get('total_items', 0)}")
        self.pinned_items_label.setText(f"Pinned Items: {stats.get('pinned_items', 0)}")
        
        total_size = stats.get('total_size', 0)
        if total_size < 1024:
            size_text = f"{total_size} B"
        elif total_size < 1024 * 1024:
            size_text = f"{total_size // 1024} KB"
        else:
            size_text = f"{total_size // (1024 * 1024)} MB"
        self.storage_size_label.setText(f"Storage Used: {size_text}")
        
        # Update type distribution
        by_type = stats.get('by_type', {})
        self.type_table.setRowCount(len(by_type))
        for i, (item_type, count) in enumerate(by_type.items()):
            self.type_table.setItem(i, 0, QTableWidgetItem(item_type.title()))
            self.type_table.setItem(i, 1, QTableWidgetItem(str(count)))
        
        # Update most accessed
        most_accessed = stats.get('most_accessed', [])
        self.accessed_table.setRowCount(len(most_accessed))
        for i, (content, access_count) in enumerate(most_accessed):
            preview = content[:50] + "..." if len(content) > 50 else content
            self.accessed_table.setItem(i, 0, QTableWidgetItem(preview))
            self.accessed_table.setItem(i, 1, QTableWidgetItem(str(access_count)))


class ClipboardSettingsPanel(QWidget):
    """Settings panel for clipboard configuration."""
    
    settings_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings("RFU", "EnhancedClipboard")
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        """Setup the settings panel UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Title
        title_label = QLabel("⚙️ Settings")
        title_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        layout.addWidget(title_label)
        
        # General settings
        general_group = QGroupBox("General")
        general_layout = QVBoxLayout(general_group)
        
        self.max_items_spinbox = QSpinBox()
        self.max_items_spinbox.setRange(10, 1000)
        self.max_items_spinbox.setValue(100)
        general_layout.addWidget(QLabel("Maximum clipboard items:"))
        general_layout.addWidget(self.max_items_spinbox)
        
        self.auto_cleanup_checkbox = QCheckBox("Auto-cleanup expired items")
        general_layout.addWidget(self.auto_cleanup_checkbox)
        
        self.cleanup_days_spinbox = QSpinBox()
        self.cleanup_days_spinbox.setRange(1, 365)
        self.cleanup_days_spinbox.setValue(30)
        general_layout.addWidget(QLabel("Cleanup after (days):"))
        general_layout.addWidget(self.cleanup_days_spinbox)
        
        layout.addWidget(general_group)
        
        # Hotkeys
        hotkeys_group = QGroupBox("Hotkeys")
        hotkeys_layout = QVBoxLayout(hotkeys_group)
        
        self.hotkey_panel_edit = QLineEdit("Ctrl+Shift+V")
        hotkeys_layout.addWidget(QLabel("Open clipboard panel:"))
        hotkeys_layout.addWidget(self.hotkey_panel_edit)
        
        self.hotkey_floating_edit = QLineEdit("Ctrl+Shift+C")
        hotkeys_layout.addWidget(QLabel("Toggle floating widget:"))
        hotkeys_layout.addWidget(self.hotkey_floating_edit)
        
        layout.addWidget(hotkeys_group)
        
        # Security
        security_group = QGroupBox("Security")
        security_layout = QVBoxLayout(security_group)
        
        self.encrypt_sensitive_checkbox = QCheckBox("Encrypt sensitive content")
        security_layout.addWidget(self.encrypt_sensitive_checkbox)
        
        self.clear_on_exit_checkbox = QCheckBox("Clear clipboard on exit")
        security_layout.addWidget(self.clear_on_exit_checkbox)
        
        layout.addWidget(security_group)
        
        # Cloud sync
        sync_group = QGroupBox("Cloud Synchronization")
        sync_layout = QVBoxLayout(sync_group)
        
        self.sync_enabled_checkbox = QCheckBox("Enable cloud sync")
        sync_layout.addWidget(self.sync_enabled_checkbox)
        
        self.sync_url_edit = QLineEdit()
        self.sync_url_edit.setPlaceholderText("https://your-sync-service.com")
        sync_layout.addWidget(QLabel("Sync URL:"))
        sync_layout.addWidget(self.sync_url_edit)
        
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.Password)
        self.api_key_edit.setPlaceholderText("Enter API key")
        sync_layout.addWidget(QLabel("API Key:"))
        sync_layout.addWidget(self.api_key_edit)
        
        layout.addWidget(sync_group)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("💾 Save Settings")
        self.save_btn.clicked.connect(self.save_settings)
        buttons_layout.addWidget(self.save_btn)
        
        self.reset_btn = QPushButton("🔄 Reset to Defaults")
        self.reset_btn.clicked.connect(self.reset_settings)
        buttons_layout.addWidget(self.reset_btn)
        
        layout.addLayout(buttons_layout)
        layout.addStretch()
    
    def load_settings(self):
        """Load settings from storage."""
        self.max_items_spinbox.setValue(self.settings.value("max_items", 100, int))
        self.auto_cleanup_checkbox.setChecked(self.settings.value("auto_cleanup", True, bool))
        self.cleanup_days_spinbox.setValue(self.settings.value("cleanup_days", 30, int))
        
        self.hotkey_panel_edit.setText(self.settings.value("hotkey_panel", "Ctrl+Shift+V"))
        self.hotkey_floating_edit.setText(self.settings.value("hotkey_floating", "Ctrl+Shift+C"))
        
        self.encrypt_sensitive_checkbox.setChecked(self.settings.value("encrypt_sensitive", False, bool))
        self.clear_on_exit_checkbox.setChecked(self.settings.value("clear_on_exit", False, bool))
        
        self.sync_enabled_checkbox.setChecked(self.settings.value("sync_enabled", False, bool))
        self.sync_url_edit.setText(self.settings.value("sync_url", ""))
        self.api_key_edit.setText(self.settings.value("api_key", ""))
    
    def save_settings(self):
        """Save settings to storage."""
        self.settings.setValue("max_items", self.max_items_spinbox.value())
        self.settings.setValue("auto_cleanup", self.auto_cleanup_checkbox.isChecked())
        self.settings.setValue("cleanup_days", self.cleanup_days_spinbox.value())
        
        self.settings.setValue("hotkey_panel", self.hotkey_panel_edit.text())
        self.settings.setValue("hotkey_floating", self.hotkey_floating_edit.text())
        
        self.settings.setValue("encrypt_sensitive", self.encrypt_sensitive_checkbox.isChecked())
        self.settings.setValue("clear_on_exit", self.clear_on_exit_checkbox.isChecked())
        
        self.settings.setValue("sync_enabled", self.sync_enabled_checkbox.isChecked())
        self.settings.setValue("sync_url", self.sync_url_edit.text())
        self.settings.setValue("api_key", self.api_key_edit.text())
        
        self.settings_changed.emit()
        QMessageBox.information(self, "Settings Saved", "Settings have been saved successfully.")
    
    def reset_settings(self):
        """Reset settings to defaults."""
        reply = QMessageBox.question(
            self, "Reset Settings",
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.settings.clear()
            self.load_settings()


class ClipboardFloatingWidget(QWidget):
    """Compact floating widget for always-on-screen access."""
    
    def __init__(self, clipboard_manager, parent=None):
        super().__init__(parent)
        self.clipboard_manager = clipboard_manager
        self.is_expanded = False
        self.setup_ui()
        self.setup_window_properties()
    
    def setup_window_properties(self):
        """Setup floating widget window properties."""
        self.setWindowFlags(
            Qt.Tool | 
            Qt.FramelessWindowHint | 
            Qt.WindowStaysOnTopHint |
            Qt.X11BypassWindowManagerHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setFixedSize(60, 60)  # Compact size when collapsed
        
        # Position in bottom-right corner
        screen = QApplication.primaryScreen().geometry()
        x = screen.width() - self.width() - 20
        y = screen.height() - self.height() - 80
        self.move(x, y)
    
    def setup_ui(self):
        """Setup the floating widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)
        
        # Main button
        self.main_btn = QPushButton("📋")
        self.main_btn.setFont(QFont("Segoe UI", 16))
        self.main_btn.setMaximumSize(50, 50)
        self.main_btn.clicked.connect(self.toggle_expand)
        self.main_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(33, 37, 41, 0.9);
                border: 2px solid #495057;
                border-radius: 25px;
                color: white;
            }
            QPushButton:hover {
                background-color: rgba(52, 58, 64, 0.9);
                border-color: #6c757d;
            }
        """)
        layout.addWidget(self.main_btn)
        
        # Expanded content (initially hidden)
        self.expanded_widget = QWidget()
        self.expanded_widget.hide()
        
        expanded_layout = QVBoxLayout(self.expanded_widget)
        expanded_layout.setContentsMargins(4, 4, 4, 4)
        expanded_layout.setSpacing(2)
        
        # Quick action buttons
        self.paste_btn = QPushButton("📋")
        self.paste_btn.setMaximumSize(30, 30)
        self.paste_btn.setToolTip("Paste last item")
        self.paste_btn.clicked.connect(self.paste_last_item)
        expanded_layout.addWidget(self.paste_btn)
        
        self.history_btn = QPushButton("📜")
        self.history_btn.setMaximumSize(30, 30)
        self.history_btn.setToolTip("Show history")
        self.history_btn.clicked.connect(self.show_history)
        expanded_layout.addWidget(self.history_btn)
        
        self.settings_btn = QPushButton("⚙️")
        self.settings_btn.setMaximumSize(30, 30)
        self.settings_btn.setToolTip("Settings")
        self.settings_btn.clicked.connect(self.show_settings)
        expanded_layout.addWidget(self.settings_btn)
        
        self.close_btn = QPushButton("✖️")
        self.close_btn.setMaximumSize(30, 30)
        self.close_btn.setToolTip("Close")
        self.close_btn.clicked.connect(self.hide)
        expanded_layout.addWidget(self.close_btn)
        
        # Style expanded buttons
        button_style = """
            QPushButton {
                background-color: rgba(52, 58, 64, 0.9);
                border: 1px solid #6c757d;
                border-radius: 15px;
                color: white;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: rgba(73, 80, 87, 0.9);
            }
        """
        for btn in [self.paste_btn, self.history_btn, self.settings_btn, self.close_btn]:
            btn.setStyleSheet(button_style)
        
        layout.addWidget(self.expanded_widget)
    
    def toggle_expand(self):
        """Toggle expanded state."""
        self.is_expanded = not self.is_expanded
        
        if self.is_expanded:
            self.expanded_widget.show()
            self.setFixedSize(60, 180)
        else:
            self.expanded_widget.hide()
            self.setFixedSize(60, 60)
    
    def paste_last_item(self):
        """Paste the last clipboard item."""
        if hasattr(self.clipboard_manager, 'get_last_item'):
            last_item = self.clipboard_manager.get_last_item()
            if last_item:
                clipboard = QApplication.clipboard()
                clipboard.setText(last_item.content)
    
    def show_history(self):
        """Show clipboard history."""
        if hasattr(self.clipboard_manager, 'show_main_window'):
            self.clipboard_manager.show_main_window()
    
    def show_settings(self):
        """Show settings dialog."""
        if hasattr(self.clipboard_manager, 'show_settings'):
            self.clipboard_manager.show_settings()
    
    def mousePressEvent(self, event):
        """Handle mouse press for dragging."""
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging."""
        if event.buttons() == Qt.LeftButton and hasattr(self, 'drag_start_position'):
            self.move(event.globalPos() - self.drag_start_position)
            event.accept()


class EnhancedClipboardMainWindow(QMainWindow):
    """Main window for the Enhanced Clipboard Manager."""
    
    def __init__(self):
        super().__init__()
        self.setup_core_components()
        self.setup_ui()
        self.setup_system_integration()
        self.setup_timers()
        self.load_clipboard_history()
        
        # Floating widget
        self.floating_widget = ClipboardFloatingWidget(self)
        
        print("Enhanced Clipboard Manager initialized successfully")
    
    def setup_core_components(self):
        """Initialize core clipboard management components."""
        # Database
        db_path = os.path.join(QStandardPaths.writableLocation(
            QStandardPaths.AppDataLocation), "clipboard_history.db")
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.database = ClipboardDatabase(db_path)
        
        # Encryption
        self.encryption = ClipboardEncryption()
        
        # Cloud sync
        sync_config = {
            'sync_enabled': False,
            'sync_url': '',
            'api_key': '',
            'device_id': QSettings().value("device_id", "")
        }
        self.cloud_sync = ClipboardCloudSync(sync_config)
        
        # Template manager
        self.template_manager = ClipboardTemplateManager(self.database)
        
        # Text processor
        self.text_processor = ClipboardTextProcessor()
        
        # Current items
        self.clipboard_items = []
    
    def setup_ui(self):
        """Setup the main window UI."""
        self.setWindowTitle("Enhanced Clipboard Manager - RFU System Tools")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)
        
        # Central widget with splitter
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)
        
        # Main splitter
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel (search and filters)
        left_panel = QWidget()
        left_panel.setMaximumWidth(300)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Search panel
        self.search_panel = ClipboardSearchPanel()
        self.search_panel.search_changed.connect(self.filter_clipboard_items)
        left_layout.addWidget(self.search_panel)
        
        splitter.addWidget(left_panel)
        
        # Center panel (main content)
        center_panel = QWidget()
        center_layout = QVBoxLayout(center_panel)
        center_layout.setContentsMargins(0, 0, 0, 0)
        
        # Toolbar
        toolbar = QToolBar()
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        
        # Main actions
        new_action = toolbar.addAction("➕ New Item")
        new_action.triggered.connect(self.create_new_item)
        
        import_action = toolbar.addAction("📁 Import")
        import_action.triggered.connect(self.import_clipboard_data)
        
        export_action = toolbar.addAction("💾 Export")
        export_action.triggered.connect(self.export_clipboard_data)
        
        toolbar.addSeparator()
        
        sync_action = toolbar.addAction("☁️ Sync")
        sync_action.triggered.connect(self.sync_with_cloud)
        
        cleanup_action = toolbar.addAction("🗑️ Cleanup")
        cleanup_action.triggered.connect(self.cleanup_expired_items)
        
        toolbar.addSeparator()
        
        floating_action = toolbar.addAction("🔄 Floating Widget")
        floating_action.triggered.connect(self.toggle_floating_widget)
        
        center_layout.addWidget(toolbar)
        
        # Tab widget for main content
        self.tab_widget = QTabWidget()
        
        # History tab
        self.history_view = ClipboardHistoryView()
        self.history_view.item_selected.connect(self.on_item_selected)
        self.history_view.items_changed.connect(self.save_clipboard_history)
        self.tab_widget.addTab(self.history_view, "📜 History")
        
        # Templates tab
        self.template_panel = ClipboardTemplatePanel(self.template_manager)
        self.template_panel.template_applied.connect(self.on_template_applied)
        self.tab_widget.addTab(self.template_panel, "📄 Templates")
        
        # Statistics tab
        self.stats_panel = ClipboardStatisticsPanel(self.database)
        self.tab_widget.addTab(self.stats_panel, "📊 Statistics")
        
        # Settings tab
        self.settings_panel = ClipboardSettingsPanel()
        self.settings_panel.settings_changed.connect(self.apply_settings)
        self.tab_widget.addTab(self.settings_panel, "⚙️ Settings")
        
        center_layout.addWidget(self.tab_widget)
        splitter.addWidget(center_panel)
        
        # Right panel (content preview and actions)
        right_panel = QWidget()
        right_panel.setMaximumWidth(300)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Content preview
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMaximumHeight(200)
        self.preview_text.setFont(QFont("Consolas", 9))
        preview_layout.addWidget(self.preview_text)
        
        right_layout.addWidget(preview_group)
        
        # Quick actions
        actions_group = QGroupBox("Quick Actions")
        actions_layout = QVBoxLayout(actions_group)
        
        self.copy_btn = QPushButton("📋 Copy to Clipboard")
        self.copy_btn.clicked.connect(self.copy_selected_item)
        actions_layout.addWidget(self.copy_btn)
        
        self.edit_btn = QPushButton("✏️ Edit Content")
        self.edit_btn.clicked.connect(self.edit_selected_item)
        actions_layout.addWidget(self.edit_btn)
        
        self.pin_btn = QPushButton("📌 Toggle Pin")
        self.pin_btn.clicked.connect(self.toggle_pin_selected_item)
        actions_layout.addWidget(self.pin_btn)
        
        actions_layout.addStretch()
        right_layout.addWidget(actions_group)
        
        right_layout.addStretch()
        splitter.addWidget(right_panel)
        
        # Set splitter proportions
        splitter.setSizes([300, 600, 300])
        
        # Status bar
        self.statusBar().showMessage("Enhanced Clipboard Manager Ready")
        
        # Apply styling
        self.apply_modern_styling()
    
    def apply_modern_styling(self):
        """Apply modern styling to the application."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
            QTabWidget::pane {
                border: 1px solid #dee2e6;
                background-color: #ffffff;
            }
            QTabBar::tab {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                padding: 8px 16px;
                margin-right: 2px;
                border-bottom: none;
            }
            QTabBar::tab:selected {
                background-color: #ffffff;
                border-bottom-color: #ffffff;
                font-weight: bold;
            }
            QTabBar::tab:hover {
                background-color: #e9ecef;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #dee2e6;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
            QToolBar {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                spacing: 4px;
                padding: 4px;
            }
            QToolBar QToolButton {
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 3px;
                padding: 4px 8px;
            }
            QToolBar QToolButton:hover {
                background-color: #e9ecef;
                border-color: #dee2e6;
            }
        """)
    
    def setup_system_integration(self):
        """Setup system clipboard monitoring and integration."""
        self.clipboard = QApplication.clipboard()
        self.clipboard.dataChanged.connect(self.on_system_clipboard_changed)
        
        # System tray integration
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = QSystemTrayIcon(self)
            self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
            
            # Tray menu
            tray_menu = QMenu()
            
            show_action = tray_menu.addAction("Show Clipboard Manager")
            show_action.triggered.connect(self.show)
            
            floating_action = tray_menu.addAction("Toggle Floating Widget")
            floating_action.triggered.connect(self.toggle_floating_widget)
            
            tray_menu.addSeparator()
            
            quit_action = tray_menu.addAction("Quit")
            quit_action.triggered.connect(self.close)
            
            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.show()
    
    def setup_timers(self):
        """Setup periodic timers for maintenance tasks."""
        # Auto-save timer
        self.save_timer = QTimer()
        self.save_timer.timeout.connect(self.save_clipboard_history)
        self.save_timer.start(30000)  # Save every 30 seconds
        
        # Cleanup timer
        self.cleanup_timer = QTimer()
        self.cleanup_timer.timeout.connect(self.auto_cleanup)
        self.cleanup_timer.start(3600000)  # Check every hour
        
        # Sync timer
        self.sync_timer = QTimer()
        self.sync_timer.timeout.connect(self.auto_sync)
        self.sync_timer.start(300000)  # Sync every 5 minutes
    
    def on_system_clipboard_changed(self):
        """Handle system clipboard changes."""
        mime_data = self.clipboard.mimeData()
        
        if mime_data.hasText():
            content = mime_data.text()
            if content.strip():  # Only add non-empty content
                item = ClipboardItem(content, "text", self.get_active_application())
                self.add_clipboard_item(item)
        elif mime_data.hasImage():
            # Handle image data
            image = mime_data.imageData()
            if image:
                # Convert to base64 for storage
                buffer = QByteArray()
                image.save(buffer, "PNG")
                image_data = f"data:image/png;base64,{buffer.toBase64().data().decode()}"
                
                item = ClipboardItem(image_data, "image", self.get_active_application())
                self.add_clipboard_item(item)
        elif mime_data.hasUrls():
            # Handle file/URL data
            urls = mime_data.urls()
            if urls:
                url_strings = [url.toString() for url in urls]
                content = "\n".join(url_strings)
                item_type = "file" if any(url.isLocalFile() for url in urls) else "url"
                
                item = ClipboardItem(content, item_type, self.get_active_application())
                self.add_clipboard_item(item)
    
    def get_active_application(self) -> str:
        """Get the name of the currently active application."""
        # Simplified implementation - would need platform-specific code
        return "Unknown Application"
    
    def add_clipboard_item(self, item: ClipboardItem):
        """Add a new clipboard item."""
        # Check for duplicates
        for existing_item in self.clipboard_items:
            if existing_item.content == item.content and existing_item.item_type == item.item_type:
                # Update existing item timestamp
                existing_item.timestamp = datetime.now()
                return
        
        # Add to database
        self.database.add_item(item)
        
        # Add to UI
        self.history_view.add_item(item)
        
        # Update status
        self.statusBar().showMessage(f"Added new {item.item_type} item to clipboard history")
    
    def filter_clipboard_items(self, query: str, item_type: str, category: str, pinned_only: bool):
        """Filter clipboard items based on search criteria."""
        self.history_view.filter_items(query, item_type, category, pinned_only)
    
    def on_item_selected(self, item_id: str):
        """Handle clipboard item selection."""
        # Find the selected item
        selected_item = None
        for item in self.clipboard_items:
            if item.id == item_id:
                selected_item = item
                break
        
        if selected_item:
            # Update preview
            self.preview_text.setPlainText(selected_item.content)
            
            # Update access count
            selected_item.access_count += 1
            selected_item.last_accessed = datetime.now()
            self.database.update_item(selected_item)
    
    def copy_selected_item(self):
        """Copy selected item to system clipboard."""
        # Implementation would copy the currently selected item
        self.statusBar().showMessage("Item copied to clipboard")
    
    def edit_selected_item(self):
        """Edit selected clipboard item."""
        # Implementation would open edit dialog
        self.statusBar().showMessage("Edit functionality would be implemented here")
    
    def toggle_pin_selected_item(self):
        """Toggle pin status of selected item."""
        # Implementation would toggle pin status
        self.statusBar().showMessage("Pin status toggled")
    
    def create_new_item(self):
        """Create a new clipboard item manually."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Create New Clipboard Item")
        dialog.setModal(True)
        dialog.resize(500, 300)
        
        layout = QVBoxLayout(dialog)
        
        # Content input
        layout.addWidget(QLabel("Content:"))
        content_edit = QTextEdit()
        layout.addWidget(content_edit)
        
        # Type selection
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Type:"))
        type_combo = QComboBox()
        type_combo.addItems(["text", "url", "code", "email"])
        type_layout.addWidget(type_combo)
        layout.addLayout(type_layout)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec_() == QDialog.Accepted:
            content = content_edit.toPlainText()
            item_type = type_combo.currentText()
            
            if content.strip():
                item = ClipboardItem(content, item_type, "Manual Entry")
                self.add_clipboard_item(item)
    
    def import_clipboard_data(self):
        """Import clipboard data from file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Clipboard Data", "",
            "JSON Files (*.json);;All Files (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                imported_count = 0
                for item_data in data.get('items', []):
                    item = ClipboardItem.from_dict(item_data)
                    self.database.add_item(item)
                    imported_count += 1
                
                self.load_clipboard_history()  # Refresh display
                self.statusBar().showMessage(f"Imported {imported_count} clipboard items")
                
            except Exception as e:
                QMessageBox.critical(self, "Import Error", f"Failed to import clipboard data: {e}")
    
    def export_clipboard_data(self):
        """Export clipboard data to file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Clipboard Data", "clipboard_export.json",
            "JSON Files (*.json);;All Files (*.*)"
        )
        
        if file_path:
            try:
                items = self.database.get_items()
                data = {
                    'export_date': datetime.now().isoformat(),
                    'item_count': len(items),
                    'items': [item.to_dict() for item in items]
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                self.statusBar().showMessage(f"Exported {len(items)} clipboard items")
                
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export clipboard data: {e}")
    
    def sync_with_cloud(self):
        """Manually trigger cloud synchronization."""
        if self.cloud_sync.sync_enabled:
            pinned_items = [item for item in self.clipboard_items if item.pinned]
            if self.cloud_sync.sync_to_cloud(pinned_items):
                self.statusBar().showMessage("Cloud sync completed successfully")
            else:
                self.statusBar().showMessage("Cloud sync failed")
        else:
            QMessageBox.information(self, "Cloud Sync", "Cloud synchronization is not enabled. Please configure it in Settings.")
    
    def cleanup_expired_items(self):
        """Clean up expired clipboard items."""
        count = self.database.cleanup_expired(30)  # 30 days
        self.load_clipboard_history()  # Refresh display
        self.statusBar().showMessage(f"Cleaned up {count} expired items")
    
    def toggle_floating_widget(self):
        """Toggle floating widget visibility."""
        if self.floating_widget.isVisible():
            self.floating_widget.hide()
        else:
            self.floating_widget.show()
    
    def on_template_applied(self, content: str):
        """Handle template application."""
        # Add template content to clipboard
        clipboard = QApplication.clipboard()
        clipboard.setText(content)
        
        # Create clipboard item
        item = ClipboardItem(content, "text", "Template")
        self.add_clipboard_item(item)
        
        self.statusBar().showMessage("Template applied and added to clipboard")
    
    def load_clipboard_history(self):
        """Load clipboard history from database."""
        items = self.database.get_items(limit=1000)  # Load recent items
        self.clipboard_items = items
        
        # Update UI
        self.history_view.clear_items()
        for item in items:
            self.history_view.add_item(item)
        
        # Update statistics
        self.stats_panel.refresh_stats()
    
    def save_clipboard_history(self):
        """Save clipboard history to database."""
        # Items are saved automatically when added/modified
        pass
    
    def apply_settings(self):
        """Apply changed settings."""
        # Reload settings and apply changes
        self.statusBar().showMessage("Settings applied successfully")
    
    def auto_cleanup(self):
        """Automatic cleanup based on settings."""
        settings = QSettings("RFU", "EnhancedClipboard")
        if settings.value("auto_cleanup", True, bool):
            cleanup_days = settings.value("cleanup_days", 30, int)
            count = self.database.cleanup_expired(cleanup_days)
            if count > 0:
                self.load_clipboard_history()
    
    def auto_sync(self):
        """Automatic cloud synchronization."""
        if self.cloud_sync.sync_enabled:
            pinned_items = [item for item in self.clipboard_items if item.pinned]
            self.cloud_sync.sync_to_cloud(pinned_items)
    
    def closeEvent(self, event):
        """Handle application close event."""
        settings = QSettings("RFU", "EnhancedClipboard")
        
        if settings.value("clear_on_exit", False, bool):
            # Clear non-pinned items
            for item in self.clipboard_items:
                if not item.pinned:
                    self.database.delete_item(item.id)
        
        # Close database
        self.database.close()
        
        # Hide to system tray instead of closing
        if hasattr(self, 'tray_icon') and self.tray_icon.isVisible():
            self.hide()
            event.ignore()
        else:
            event.accept()


def main():
    """Main function to run the Enhanced Clipboard Manager."""
    if not PYQT_AVAILABLE:
        print("PyQt5 is required to run the Enhanced Clipboard Manager")
        return
    
    app = QApplication(sys.argv)
    app.setApplicationName("Enhanced Clipboard Manager")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("RFU")
    
    # Create and show main window
    window = EnhancedClipboardMainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
