"""Common widget utilities and custom widgets."""
from typing import Optional, List, Union, Callable
from pathlib import Path
from PyQt5.QtWidgets import (
    QProgressBar, QLabel, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QFrame, QSpacerItem, QSizePolicy,
    QLineEdit, QSpinBox, QDoubleSpinBox, QCheckBox
)
from PyQt5.QtCore import Qt, pyqtSignal


class ProgressWidget(QWidget):
    """A widget combining a progress bar with a label and optional cancel button."""
    
    cancelled = pyqtSignal()
    
    def __init__(
        self,
        parent: Optional[QWidget] = None,
        show_cancel: bool = False,
        label_text: str = ""
    ):
        """Initialize the widget.
        
        Args:
            parent: Parent widget
            show_cancel: Whether to show cancel button
            label_text: Initial label text
        """
        super().__init__(parent)
        self.show_cancel = show_cancel
        self.label_text = label_text
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.label = QLabel(self.label_text, self)
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)
        
        h_layout = QHBoxLayout()
        
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setAlignment(Qt.AlignCenter)
        h_layout.addWidget(self.progress_bar)
        
        if self.show_cancel:
            self.cancel_button = QPushButton("Cancel", self)
            self.cancel_button.clicked.connect(self.cancelled.emit)
            h_layout.addWidget(self.cancel_button)
            
        layout.addLayout(h_layout)
        self.setLayout(layout)
        
    def set_progress(self, value: int, maximum: int = 100):
        """Set the progress bar value.
        
        Args:
            value: Current progress value
            maximum: Maximum progress value
        """
        self.progress_bar.setMaximum(maximum)
        self.progress_bar.setValue(value)
        
    def set_text(self, text: str):
        """Set the label text.
        
        Args:
            text: New label text
        """
        self.label.setText(text)


class FileSelectionWidget(QWidget):
    """Widget for file/directory selection with browse button."""
    
    path_changed = pyqtSignal(Path)
    
    def __init__(
        self,
        parent: Optional[QWidget] = None,
        mode: str = "file_open",
        label_text: str = "File:",
        file_filter: str = "All Files (*.*)"
    ):
        """Initialize the widget.
        
        Args:
            parent: Parent widget
            mode: One of "file_open", "file_save", or "directory"
            label_text: Label text
            file_filter: File type filter
        """
        super().__init__(parent)
        self.mode = mode
        self.file_filter = file_filter
        self.setup_ui(label_text)
        
    def setup_ui(self, label_text: str):
        """Set up the UI components.
        
        Args:
            label_text: Label text
        """
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.label = QLabel(label_text, self)
        layout.addWidget(self.label)
        
        self.path_edit = QLineEdit(self)
        self.path_edit.textChanged.connect(self._on_path_changed)
        layout.addWidget(self.path_edit)
        
        self.browse_button = QPushButton("Browse...", self)
        self.browse_button.clicked.connect(self._browse)
        layout.addWidget(self.browse_button)
        
    def _browse(self):
        """Show file/directory selection dialog."""
        if self.mode == "directory":
            path = get_existing_directory(self, "Select Directory")
        elif self.mode == "file_save":
            path, _ = get_save_file_name(
                self, "Save File", filter=self.file_filter
            )
        else:  # file_open
            path, _ = get_open_file_name(
                self, "Open File", filter=self.file_filter
            )
            
        if path:
            self.set_path(path)
            
    def _on_path_changed(self, text: str):
        """Handle path text changes.
        
        Args:
            text: New path text
        """
        self.path_changed.emit(Path(text))
        
    def get_path(self) -> Optional[Path]:
        """Get the selected path.
        
        Returns:
            Selected path or None if empty
        """
        text = self.path_edit.text().strip()
        return Path(text) if text else None
        
    def set_path(self, path: Union[str, Path]):
        """Set the path.
        
        Args:
            path: Path to set
        """
        self.path_edit.setText(str(path))


class CollapsibleWidget(QWidget):
    """A collapsible section widget."""
    
    def __init__(
        self,
        title: str,
        parent: Optional[QWidget] = None,
        expanded: bool = False
    ):
        """Initialize the widget.
        
        Args:
            title: Section title
            parent: Parent widget
            expanded: Whether initially expanded
        """
        super().__init__(parent)
        self.expanded = expanded
        self.setup_ui(title)
        
    def setup_ui(self, title: str):
        """Set up the UI components.
        
        Args:
            title: Section title
        """
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.toggle_button = QPushButton(title, self)
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(self.expanded)
        self.toggle_button.clicked.connect(self._on_toggle)
        layout.addWidget(self.toggle_button)
        
        self.content_widget = QWidget(self)
        self.content_widget.setVisible(self.expanded)
        
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(20, 0, 0, 0)
        
        layout.addWidget(self.content_widget)
        
    def _on_toggle(self, checked: bool):
        """Handle toggle button clicks.
        
        Args:
            checked: New toggle state
        """
        self.expanded = checked
        self.content_widget.setVisible(checked)
        
    def add_widget(self, widget: QWidget):
        """Add a widget to the content area.
        
        Args:
            widget: Widget to add
        """
        self.content_layout.addWidget(widget)
        
    def add_layout(self, layout: Union[QVBoxLayout, QHBoxLayout]):
        """Add a layout to the content area.
        
        Args:
            layout: Layout to add
        """
        self.content_layout.addLayout(layout)


def set_widget_enabled(widget: QWidget, enabled: bool):
    """Enable or disable a widget and its children.
    
    Args:
        widget: Widget to enable/disable
        enabled: Whether to enable or disable
    """
    widget.setEnabled(enabled)
    for child in widget.findChildren(QWidget):
        child.setEnabled(enabled)


def clear_layout(layout: Union[QVBoxLayout, QHBoxLayout]):
    """Clear all widgets from a layout.
    
    Args:
        layout: Layout to clear
    """
    while layout.count():
        item = layout.takeAt(0)
        if item.widget():
            item.widget().deleteLater()
        elif item.layout():
            clear_layout(item.layout())
