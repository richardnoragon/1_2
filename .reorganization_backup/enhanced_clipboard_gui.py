"""
Enhanced Clipboard Manager GUI - Main user interface for comprehensive clipboard management.

Features:
- Multi-panel interface with history view
- Searchable database with filtering
- Context-sensitive menus
- Favorites system with ratings
- Template manager
- Cloud synchronization
- Text processing tools
- Floating widget mode
- Data encryption
- Statistics dashboard

Author: Richard's File Utilities
Version: 1.0.0
Date: August 7, 2025
"""

import os
import sys
import json
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional

try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QGridLayout, QTabWidget, QListWidget, QListWidgetItem, QTreeWidget,
        QTreeWidgetItem, QPushButton, QLabel, QLineEdit, QTextEdit,
        QComboBox, QCheckBox, QSlider, QProgressBar, QSplitter,
        QGroupBox, QFrame, QScrollArea, QDialog, QDialogButtonBox,
        QTableWidget, QTableWidgetItem, QHeaderView, QMenu, QAction,
        QSystemTrayIcon, QMessageBox, QFileDialog, QInputDialog,
        QSpinBox, QDoubleSpinBox, QDateTimeEdit, QCalendarWidget,
        QToolBar, QToolButton, QStatusBar, QMenuBar, QSizePolicy,
        QStyledItemDelegate, QStyle, QAbstractItemView, QContextMenuEvent
    )
    from PyQt5.QtCore import (
        Qt, QTimer, QThread, pyqtSignal, QSize, QRect, QPoint,
        QDateTime, QDate, QTime, QPropertyAnimation, QEasingCurve,
        QParallelAnimationGroup, QSequentialAnimationGroup, QMimeData,
        QByteArray, QDataStream, QIODevice, QSettings, QStandardPaths
    )
    from PyQt5.QtGui import (
        QFont, QIcon, QPixmap, QPainter, QPen, QBrush, QColor,
        QLinearGradient, QRadialGradient, QPalette, QCursor,
        QKeySequence, QClipboard, QDrag, QMovie, QTextCursor,
        QTextCharFormat, QTextDocument, QTextOption, QValidator,
        QRegExpValidator, QDoubleValidator, QIntValidator
    )
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    # Create dummy classes for testing
    class QWidget:
        def __init__(self, parent=None):
            pass
        def setLayout(self, layout):
            pass
        def layout(self):
            return None
    
    class QMainWindow(QWidget):
        pass
    
    class QVBoxLayout:
        def __init__(self, parent=None):
            pass
        def addWidget(self, widget):
            pass
        def addLayout(self, layout):
            pass
        def setContentsMargins(self, *args):
            pass
        def setSpacing(self, spacing):
            pass
    def pyqtSignal(*args, **kwargs):
        """Dummy pyqtSignal for testing"""
        return None

try:
    from enhanced_clipboard_manager import (
        ClipboardItem, ClipboardDatabase, ClipboardEncryption,
        ClipboardCloudSync, ClipboardTextProcessor, ClipboardTemplateManager
    )
    CLIPBOARD_CORE_AVAILABLE = True
except ImportError:
    CLIPBOARD_CORE_AVAILABLE = False


class ClipboardItemWidget(QWidget):
    """Custom widget for displaying clipboard items."""
    
    item_selected = pyqtSignal(str)  # item_id
    item_deleted = pyqtSignal(str)   # item_id
    item_pinned = pyqtSignal(str, bool)  # item_id, pinned
    
    def __init__(self, item: ClipboardItem, parent=None):
        super().__init__(parent)
        self.item = item
        self.setup_ui()
        self.setup_animations()
    
    def setup_ui(self):
        """Setup the item widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        # Header with timestamp and actions
        header_layout = QHBoxLayout()
        
        # Type icon and timestamp
        self.type_label = QLabel(self.get_type_icon())
        self.type_label.setFont(QFont("Segoe UI", 12))
        header_layout.addWidget(self.type_label)
        
        self.timestamp_label = QLabel(self.format_timestamp())
        self.timestamp_label.setFont(QFont("Segoe UI", 8))
        self.timestamp_label.setStyleSheet("color: #666666;")
        header_layout.addWidget(self.timestamp_label)
        
        header_layout.addStretch()
        
        # Action buttons
        self.pin_button = QPushButton("📌" if self.item.pinned else "📍")
        self.pin_button.setMaximumSize(24, 24)
        self.pin_button.setFlat(True)
        self.pin_button.clicked.connect(self.toggle_pin)
        header_layout.addWidget(self.pin_button)
        
        self.delete_button = QPushButton("🗑️")
        self.delete_button.setMaximumSize(24, 24)
        self.delete_button.setFlat(True)
        self.delete_button.clicked.connect(self.delete_item)
        header_layout.addWidget(self.delete_button)
        
        layout.addLayout(header_layout)
        
        # Content preview
        self.content_label = QLabel(self.item.preview)
        self.content_label.setWordWrap(True)
        self.content_label.setMaximumHeight(60)
        self.content_label.setFont(QFont("Consolas", 9))
        self.content_label.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                padding: 4px;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.content_label)
        
        # Metadata
        metadata_layout = QHBoxLayout()
        
        # Source app
        if self.item.source_app:
            source_label = QLabel(f"📱 {self.item.source_app}")
            source_label.setFont(QFont("Segoe UI", 8))
            source_label.setStyleSheet("color: #495057;")
            metadata_layout.addWidget(source_label)
        
        # Size
        size_label = QLabel(f"💾 {self.format_size(self.item.size)}")
        size_label.setFont(QFont("Segoe UI", 8))
        size_label.setStyleSheet("color: #495057;")
        metadata_layout.addWidget(size_label)
        
        # Tags
        if self.item.tags:
            tags_label = QLabel(f"🏷️ {', '.join(self.item.tags[:3])}")
            tags_label.setFont(QFont("Segoe UI", 8))
            tags_label.setStyleSheet("color: #495057;")
            metadata_layout.addWidget(tags_label)
        
        metadata_layout.addStretch()
        
        # Rating stars
        if self.item.rating > 0:
            rating_label = QLabel("⭐" * self.item.rating)
            rating_label.setFont(QFont("Segoe UI", 8))
            metadata_layout.addWidget(rating_label)
        
        layout.addLayout(metadata_layout)
        
        # Apply item styling
        self.setStyleSheet(self.get_item_style())
        self.setCursor(QCursor(Qt.PointingHandCursor))
    
    def setup_animations(self):
        """Setup hover animations."""
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(150)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
    
    def get_type_icon(self) -> str:
        """Get icon for item type."""
        icons = {
            'text': '📄',
            'image': '🖼️',
            'file': '📁',
            'url': '🔗',
            'html': '🌐',
            'code': '💻',
            'email': '✉️'
        }
        return icons.get(self.item.item_type, '📄')
    
    def format_timestamp(self) -> str:
        """Format timestamp for display."""
        now = datetime.now()
        diff = now - self.item.timestamp
        
        if diff.days > 0:
            return f"{diff.days}d ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours}h ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes}m ago"
        else:
            return "Just now"
    
    def format_size(self, size_bytes: int) -> str:
        """Format file size for display."""
        if size_bytes < 1024:
            return f"{size_bytes}B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes // 1024}KB"
        else:
            return f"{size_bytes // (1024 * 1024)}MB"
    
    def get_item_style(self) -> str:
        """Get CSS style for item widget."""
        base_color = "#ffffff"
        border_color = "#dee2e6"
        
        if self.item.pinned:
            base_color = "#fff3cd"
            border_color = "#ffeaa7"
        
        return f"""
            ClipboardItemWidget {{
                background-color: {base_color};
                border: 1px solid {border_color};
                border-radius: 6px;
                margin: 2px;
                padding: 4px;
            }}
            ClipboardItemWidget:hover {{
                background-color: #f8f9fa;
                border-color: #6c757d;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
        """
    
    def toggle_pin(self):
        """Toggle pin status."""
        self.item.pinned = not self.item.pinned
        self.pin_button.setText("📌" if self.item.pinned else "📍")
        self.setStyleSheet(self.get_item_style())
        self.item_pinned.emit(self.item.id, self.item.pinned)
    
    def delete_item(self):
        """Delete this item."""
        reply = QMessageBox.question(
            self, "Delete Item",
            "Are you sure you want to delete this clipboard item?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.item_deleted.emit(self.item.id)
    
    def mousePressEvent(self, event):
        """Handle mouse press events."""
        if event.button() == Qt.LeftButton:
            self.item_selected.emit(self.item.id)
        super().mousePressEvent(event)
    
    def contextMenuEvent(self, event):
        """Show context menu."""
        menu = QMenu(self)
        
        # Copy actions
        copy_action = menu.addAction("📋 Copy to Clipboard")
        copy_action.triggered.connect(lambda: self.copy_to_clipboard())
        
        copy_plain_action = menu.addAction("📄 Copy as Plain Text")
        copy_plain_action.triggered.connect(lambda: self.copy_to_clipboard(plain=True))
        
        menu.addSeparator()
        
        # Edit actions
        edit_action = menu.addAction("✏️ Edit Content")
        edit_action.triggered.connect(self.edit_content)
        
        tags_action = menu.addAction("🏷️ Edit Tags")
        tags_action.triggered.connect(self.edit_tags)
        
        menu.addSeparator()
        
        # Organization
        pin_text = "📌 Unpin" if self.item.pinned else "📍 Pin"
        pin_action = menu.addAction(pin_text)
        pin_action.triggered.connect(self.toggle_pin)
        
        category_action = menu.addAction("📂 Change Category")
        category_action.triggered.connect(self.change_category)
        
        menu.addSeparator()
        
        # Rating
        rating_menu = menu.addMenu("⭐ Rating")
        for i in range(6):
            if i == 0:
                rating_action = rating_menu.addAction("Remove Rating")
            else:
                rating_action = rating_menu.addAction("⭐" * i)
            rating_action.triggered.connect(lambda checked, r=i: self.set_rating(r))
        
        menu.addSeparator()
        
        # Advanced
        if self.item.item_type == "text":
            process_menu = menu.addMenu("🔧 Text Processing")
            
            case_menu = process_menu.addMenu("🔤 Change Case")
            cases = [("UPPERCASE", "upper"), ("lowercase", "lower"), 
                    ("Title Case", "title"), ("camelCase", "camel"),
                    ("PascalCase", "pascal"), ("snake_case", "snake")]
            for case_name, case_type in cases:
                case_action = case_menu.addAction(case_name)
                case_action.triggered.connect(lambda checked, ct=case_type: self.process_text_case(ct))
        
        delete_action = menu.addAction("🗑️ Delete")
        delete_action.triggered.connect(self.delete_item)
        
        menu.exec_(event.globalPos())
    
    def copy_to_clipboard(self, plain=False):
        """Copy item content to system clipboard."""
        clipboard = QApplication.clipboard()
        if plain or self.item.item_type != "html":
            clipboard.setText(self.item.content)
        else:
            mime_data = QMimeData()
            mime_data.setHtml(self.item.content)
            mime_data.setText(self.item.content)  # Fallback
            clipboard.setMimeData(mime_data)
        
        # Update access count
        self.item.access_count += 1
        self.item.last_accessed = datetime.now()
    
    def edit_content(self):
        """Edit item content."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Clipboard Content")
        dialog.setModal(True)
        dialog.resize(500, 300)
        
        layout = QVBoxLayout(dialog)
        
        # Content editor
        content_edit = QTextEdit()
        content_edit.setPlainText(self.item.content)
        content_edit.setFont(QFont("Consolas", 10))
        layout.addWidget(content_edit)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec_() == QDialog.Accepted:
            self.item.content = content_edit.toPlainText()
            self.item.preview = self.item._generate_preview(self.item.content, self.item.item_type)
            self.content_label.setText(self.item.preview)
    
    def edit_tags(self):
        """Edit item tags."""
        current_tags = ", ".join(self.item.tags)
        tags_text, ok = QInputDialog.getText(
            self, "Edit Tags", "Tags (comma-separated):", 
            QLineEdit.Normal, current_tags
        )
        
        if ok:
            if tags_text.strip():
                self.item.tags = [tag.strip() for tag in tags_text.split(",") if tag.strip()]
            else:
                self.item.tags = []
            self.setup_ui()  # Refresh display
    
    def change_category(self):
        """Change item category."""
        categories = ["General", "Work", "Personal", "Code", "URLs", "Images", "Documents"]
        category, ok = QInputDialog.getItem(
            self, "Change Category", "Select category:", 
            categories, categories.index(self.item.category) if self.item.category in categories else 0
        )
        
        if ok:
            self.item.category = category
    
    def set_rating(self, rating: int):
        """Set item rating."""
        self.item.rating = rating
        self.setup_ui()  # Refresh display
    
    def process_text_case(self, case_type: str):
        """Process text case transformation."""
        if self.item.item_type == "text":
            processor = ClipboardTextProcessor()
            self.item.content = processor.convert_case(self.item.content, case_type)
            self.item.preview = self.item._generate_preview(self.item.content, self.item.item_type)
            self.content_label.setText(self.item.preview)


class ClipboardHistoryView(QScrollArea):
    """Scrollable view for clipboard history items."""
    
    item_selected = pyqtSignal(str)
    items_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.items = []
        self.filtered_items = []
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the history view."""
        self.setWidgetResizable(True)
        self.setFrameStyle(QFrame.NoFrame)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Container widget
        self.container = QWidget()
        self.layout = QVBoxLayout(self.container)
        self.layout.setContentsMargins(8, 8, 8, 8)
        self.layout.setSpacing(4)
        self.layout.addStretch()
        
        self.setWidget(self.container)
        
        # Empty state
        self.empty_label = QLabel("No clipboard items found")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font-size: 14px;
                padding: 20px;
            }
        """)
        self.layout.addWidget(self.empty_label)
    
    def add_item(self, item: ClipboardItem):
        """Add a clipboard item to the view."""
        # Remove empty label if present
        if self.empty_label in self.layout.children():
            self.layout.removeWidget(self.empty_label)
            self.empty_label.hide()
        
        # Create item widget
        item_widget = ClipboardItemWidget(item)
        item_widget.item_selected.connect(self.item_selected.emit)
        item_widget.item_deleted.connect(self.remove_item)
        item_widget.item_pinned.connect(self.on_item_pinned)
        
        # Insert at top (most recent first)
        self.layout.insertWidget(0, item_widget)
        self.items.append(item)
        self.items_changed.emit()
    
    def remove_item(self, item_id: str):
        """Remove item by ID."""
        for i, item in enumerate(self.items):
            if item.id == item_id:
                # Remove from layout
                widget = self.layout.itemAt(i).widget()
                self.layout.removeWidget(widget)
                widget.deleteLater()
                
                # Remove from items
                self.items.pop(i)
                break
        
        # Show empty state if no items
        if not self.items:
            self.empty_label.show()
            self.layout.addWidget(self.empty_label)
        
        self.items_changed.emit()
    
    def on_item_pinned(self, item_id: str, pinned: bool):
        """Handle item pin state change."""
        for item in self.items:
            if item.id == item_id:
                item.pinned = pinned
                break
        self.items_changed.emit()
    
    def clear_items(self):
        """Clear all items."""
        # Remove all item widgets
        for i in reversed(range(self.layout.count())):
            widget = self.layout.itemAt(i).widget()
            if widget and isinstance(widget, ClipboardItemWidget):
                self.layout.removeWidget(widget)
                widget.deleteLater()
        
        self.items.clear()
        self.empty_label.show()
        self.layout.addWidget(self.empty_label)
        self.items_changed.emit()
    
    def filter_items(self, query: str = "", item_type: str = "", category: str = "", pinned_only: bool = False):
        """Filter displayed items."""
        # Hide all widgets first
        for i in range(self.layout.count()):
            widget = self.layout.itemAt(i).widget()
            if widget and isinstance(widget, ClipboardItemWidget):
                widget.hide()
        
        visible_count = 0
        
        for i in range(self.layout.count()):
            widget = self.layout.itemAt(i).widget()
            if not widget or not isinstance(widget, ClipboardItemWidget):
                continue
            
            item = widget.item
            
            # Apply filters
            if query and query.lower() not in item.content.lower() and query.lower() not in item.preview.lower():
                continue
            
            if item_type and item.item_type != item_type:
                continue
            
            if category and item.category != category:
                continue
            
            if pinned_only and not item.pinned:
                continue
            
            # Show matching widget
            widget.show()
            visible_count += 1
        
        # Show/hide empty state
        if visible_count == 0:
            self.empty_label.show()
        else:
            self.empty_label.hide()


class ClipboardSearchPanel(QWidget):
    """Search and filter panel for clipboard items."""
    
    search_changed = pyqtSignal(str, str, str, bool)  # query, type, category, pinned_only
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the search panel."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Title
        title_label = QLabel("🔍 Search & Filter")
        title_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        layout.addWidget(title_label)
        
        # Search box
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search clipboard content...")
        self.search_edit.textChanged.connect(self.emit_search_changed)
        search_layout.addWidget(self.search_edit)
        
        layout.addLayout(search_layout)
        
        # Filters
        filters_group = QGroupBox("Filters")
        filters_layout = QVBoxLayout(filters_group)
        
        # Type filter
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Type:"))
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(["All Types", "Text", "Image", "File", "URL", "HTML", "Code", "Email"])
        self.type_combo.currentTextChanged.connect(self.emit_search_changed)
        type_layout.addWidget(self.type_combo)
        
        filters_layout.addLayout(type_layout)
        
        # Category filter
        category_layout = QHBoxLayout()
        category_layout.addWidget(QLabel("Category:"))
        
        self.category_combo = QComboBox()
        self.category_combo.addItems(["All Categories", "General", "Work", "Personal", "Code", "URLs", "Images", "Documents"])
        self.category_combo.currentTextChanged.connect(self.emit_search_changed)
        category_layout.addWidget(self.category_combo)
        
        filters_layout.addLayout(category_layout)
        
        # Pinned filter
        self.pinned_checkbox = QCheckBox("Show only pinned items")
        self.pinned_checkbox.toggled.connect(self.emit_search_changed)
        filters_layout.addWidget(self.pinned_checkbox)
        
        layout.addWidget(filters_group)
        
        # Quick actions
        actions_group = QGroupBox("Quick Actions")
        actions_layout = QVBoxLayout(actions_group)
        
        self.clear_search_btn = QPushButton("🗑️ Clear Filters")
        self.clear_search_btn.clicked.connect(self.clear_filters)
        actions_layout.addWidget(self.clear_search_btn)
        
        self.refresh_btn = QPushButton("🔄 Refresh")
        actions_layout.addWidget(self.refresh_btn)
        
        layout.addWidget(actions_group)
        
        layout.addStretch()
    
    def emit_search_changed(self):
        """Emit search changed signal with current filter values."""
        query = self.search_edit.text()
        item_type = self.type_combo.currentText()
        if item_type == "All Types":
            item_type = ""
        else:
            item_type = item_type.lower()
        
        category = self.category_combo.currentText()
        if category == "All Categories":
            category = ""
        
        pinned_only = self.pinned_checkbox.isChecked()
        
        self.search_changed.emit(query, item_type, category, pinned_only)
    
    def clear_filters(self):
        """Clear all filters."""
        self.search_edit.clear()
        self.type_combo.setCurrentIndex(0)
        self.category_combo.setCurrentIndex(0)
        self.pinned_checkbox.setChecked(False)


class ClipboardTemplatePanel(QWidget):
    """Panel for managing clipboard templates."""
    
    template_applied = pyqtSignal(str)  # template content
    
    def __init__(self, template_manager: ClipboardTemplateManager, parent=None):
        super().__init__(parent)
        self.template_manager = template_manager
        self.setup_ui()
        self.load_templates()
    
    def setup_ui(self):
        """Setup the template panel."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Title
        title_label = QLabel("📄 Templates")
        title_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        layout.addWidget(title_label)
        
        # Template list
        self.template_list = QListWidget()
        self.template_list.itemDoubleClicked.connect(self.apply_template)
        layout.addWidget(self.template_list)
        
        # Template actions
        actions_layout = QHBoxLayout()
        
        self.new_template_btn = QPushButton("➕ New")
        self.new_template_btn.clicked.connect(self.create_template)
        actions_layout.addWidget(self.new_template_btn)
        
        self.edit_template_btn = QPushButton("✏️ Edit")
        self.edit_template_btn.clicked.connect(self.edit_template)
        actions_layout.addWidget(self.edit_template_btn)
        
        self.delete_template_btn = QPushButton("🗑️ Delete")
        self.delete_template_btn.clicked.connect(self.delete_template)
        actions_layout.addWidget(self.delete_template_btn)
        
        layout.addLayout(actions_layout)
    
    def load_templates(self):
        """Load templates into the list."""
        self.template_list.clear()
        for template_id, template in self.template_manager.templates.items():
            item = QListWidgetItem(f"{template['name']} ({template['category']})")
            item.setData(Qt.UserRole, template_id)
            self.template_list.addItem(item)
    
    def create_template(self):
        """Create a new template."""
        dialog = TemplateEditDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            name, content, category = dialog.get_data()
            variables = self.template_manager.get_template_variables(content)
            self.template_manager.add_template(name, content, variables, category)
            self.load_templates()
    
    def edit_template(self):
        """Edit selected template."""
        current_item = self.template_list.currentItem()
        if not current_item:
            return
        
        template_id = current_item.data(Qt.UserRole)
        template = self.template_manager.templates[template_id]
        
        dialog = TemplateEditDialog(self)
        dialog.set_data(template['name'], template['content'], template['category'])
        
        if dialog.exec_() == QDialog.Accepted:
            name, content, category = dialog.get_data()
            # Update template (simplified - would need database update in real implementation)
            self.load_templates()
    
    def delete_template(self):
        """Delete selected template."""
        current_item = self.template_list.currentItem()
        if not current_item:
            return
        
        reply = QMessageBox.question(
            self, "Delete Template",
            "Are you sure you want to delete this template?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Delete template (simplified - would need database deletion in real implementation)
            self.load_templates()
    
    def apply_template(self, item):
        """Apply selected template."""
        template_id = item.data(Qt.UserRole)
        template = self.template_manager.templates[template_id]
        
        # Check if template has variables
        variables = template.get('variables', [])
        if variables:
            dialog = TemplateVariableDialog(variables, self)
            if dialog.exec_() == QDialog.Accepted:
                variable_values = dialog.get_values()
                content = self.template_manager.expand_template(template_id, variable_values)
            else:
                return
        else:
            content = template['content']
        
        self.template_applied.emit(content)


class TemplateEditDialog(QDialog):
    """Dialog for editing templates."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Template Editor")
        self.setModal(True)
        self.resize(500, 400)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the dialog UI."""
        layout = QVBoxLayout(self)
        
        # Name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name:"))
        self.name_edit = QLineEdit()
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)
        
        # Category
        category_layout = QHBoxLayout()
        category_layout.addWidget(QLabel("Category:"))
        self.category_combo = QComboBox()
        self.category_combo.addItems(["General", "Work", "Personal", "Code", "Email", "Documents"])
        self.category_combo.setEditable(True)
        category_layout.addWidget(self.category_combo)
        layout.addLayout(category_layout)
        
        # Content
        layout.addWidget(QLabel("Content (use {variable_name} for variables):"))
        self.content_edit = QTextEdit()
        self.content_edit.setFont(QFont("Consolas", 10))
        layout.addWidget(self.content_edit)
        
        # Variables info
        info_label = QLabel("Variables will be automatically detected from {variable_name} patterns")
        info_label.setStyleSheet("color: #6c757d; font-style: italic;")
        layout.addWidget(info_label)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def set_data(self, name: str, content: str, category: str):
        """Set dialog data."""
        self.name_edit.setText(name)
        self.content_edit.setPlainText(content)
        index = self.category_combo.findText(category)
        if index >= 0:
            self.category_combo.setCurrentIndex(index)
        else:
            self.category_combo.setEditText(category)
    
    def get_data(self) -> tuple:
        """Get dialog data."""
        return (
            self.name_edit.text(),
            self.content_edit.toPlainText(),
            self.category_combo.currentText()
        )


class TemplateVariableDialog(QDialog):
    """Dialog for entering template variables."""
    
    def __init__(self, variables: List[str], parent=None):
        super().__init__(parent)
        self.variables = variables
        self.variable_edits = {}
        self.setWindowTitle("Template Variables")
        self.setModal(True)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the dialog UI."""
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("Enter values for template variables:"))
        
        # Variable inputs
        for variable in self.variables:
            var_layout = QHBoxLayout()
            var_layout.addWidget(QLabel(f"{variable}:"))
            
            var_edit = QLineEdit()
            self.variable_edits[variable] = var_edit
            var_layout.addWidget(var_edit)
            
            layout.addLayout(var_layout)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_values(self) -> Dict[str, str]:
        """Get variable values."""
        return {var: edit.text() for var, edit in self.variable_edits.items()}


if __name__ == "__main__":
    print("Enhanced Clipboard GUI components loaded successfully")
