"""
Address Bar Component for RFU Multi-Pane File Explorer

This module provides an intelligent address bar with auto-completion,
path validation, and navigation event handling.

Author: Richard Noragon
Version: 2.0.0
"""

import logging
import os
import sys
from pathlib import Path
from typing import List, Optional, Set

from PyQt5.QtCore import QCompleter, QStringListModel, Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QKeySequence, QPalette
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QCompleter as BaseCompleter
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QPushButton,
    QToolButton,
    QWidget,
)


class NavigationEvent:
    """Represents a navigation event from the address bar."""

    def __init__(self, path: str, source: str = "address_bar"):
        """
        Initialize navigation event.

        Args:
            path: Target path for navigation
            source: Source of the navigation event
        """
        self.path = path
        self.source = source
        self.timestamp = None

    def __str__(self):
        return f"NavigationEvent(path='{self.path}', source='{self.source}')"


class PathValidator:
    """Validates and normalizes file system paths."""

    @staticmethod
    def is_valid_path(path: str) -> bool:
        """
        Check if path is valid and accessible.

        Args:
            path: Path to validate

        Returns:
            bool: True if path is valid
        """
        try:
            path_obj = Path(path).resolve()
            return path_obj.exists() and path_obj.is_dir()
        except (OSError, ValueError):
            return False

    @staticmethod
    def normalize_path(path: str) -> str:
        """
        Normalize path to standard format.

        Args:
            path: Path to normalize

        Returns:
            str: Normalized path
        """
        try:
            return str(Path(path).resolve())
        except (OSError, ValueError):
            return path

    @staticmethod
    def get_parent_path(path: str) -> Optional[str]:
        """
        Get parent directory of path.

        Args:
            path: Input path

        Returns:
            str or None: Parent path if available
        """
        try:
            parent = Path(path).parent
            if parent != Path(path):  # Avoid infinite loop at root
                return str(parent)
        except (OSError, ValueError):
            pass
        return None

    @staticmethod
    def get_available_drives() -> List[str]:
        """
        Get list of available drives/mount points.

        Returns:
            List of drive paths
        """
        drives = []

        if sys.platform == "win32":
            # Windows drives
            import string

            for letter in string.ascii_uppercase:
                drive = f"{letter}:\\"
                if os.path.exists(drive):
                    drives.append(drive)
        else:
            # Unix-like systems
            drives.append("/")
            # Add common mount points
            mount_points = ["/mnt", "/media", "/Volumes"]
            for mount in mount_points:
                if os.path.exists(mount):
                    try:
                        for item in os.listdir(mount):
                            full_path = os.path.join(mount, item)
                            if os.path.isdir(full_path):
                                drives.append(full_path)
                    except (PermissionError, OSError):
                        pass

        return sorted(drives)


class AddressBarCompleter(BaseCompleter):
    """Enhanced completer for address bar with path-aware completion."""

    def __init__(self, parent=None):
        """Initialize the completer."""
        super().__init__(parent)

        self.model = QStringListModel()
        self.setModel(self.model)
        self.setCaseSensitivity(Qt.CaseInsensitive)
        self.setCompletionMode(BaseCompleter.PopupCompletion)
        self.setFilterMode(Qt.MatchStartsWith)

        # Cache for completion items
        self.completion_cache: Set[str] = set()
        self.last_base_path = ""

        # Setup logging
        self.logger = logging.getLogger("RFU.AddressBarCompleter")

    def update_completions(self, partial_path: str) -> None:
        """
        Update completion suggestions based on partial path.

        Args:
            partial_path: Partial path being typed
        """
        try:
            # Normalize the input
            path_obj = Path(partial_path)

            # Determine base directory for completion
            if partial_path.endswith(os.sep) or path_obj.is_dir():
                base_dir = path_obj
                prefix = ""
            else:
                base_dir = path_obj.parent
                prefix = path_obj.name

            # Only update if base directory changed
            base_dir_str = str(base_dir)
            if base_dir_str == self.last_base_path:
                return

            self.last_base_path = base_dir_str

            # Get completions
            completions = self._get_directory_completions(base_dir, prefix)

            # Update model
            self.completion_cache = set(completions)
            self.model.setStringList(sorted(completions))

        except Exception as e:
            self.logger.debug(f"Completion update failed: {e}")

    def _get_directory_completions(
        self, base_dir: Path, prefix: str
    ) -> List[str]:
        """
        Get directory completions for given base directory and prefix.

        Args:
            base_dir: Base directory to scan
            prefix: Filename prefix to match

        Returns:
            List of completion strings
        """
        completions = []

        try:
            if not base_dir.exists() or not base_dir.is_dir():
                return completions

            # Scan directory
            for item in base_dir.iterdir():
                try:
                    if item.is_dir():
                        item_name = item.name
                        if not prefix or item_name.lower().startswith(
                            prefix.lower()
                        ):
                            completion = str(base_dir / item_name)
                            completions.append(completion)
                except (PermissionError, OSError):
                    # Skip inaccessible items
                    continue

            # Add special entries for root level
            if str(base_dir) in ["/", "C:\\"] or len(str(base_dir)) <= 3:
                drives = PathValidator.get_available_drives()
                for drive in drives:
                    if not prefix or drive.lower().startswith(prefix.lower()):
                        completions.append(drive)

        except (PermissionError, OSError) as e:
            self.logger.debug(f"Directory scan failed: {e}")

        return completions[:50]  # Limit completions for performance


class AddressBar(QWidget):
    """
    Intelligent address bar with path validation and auto-completion.

    Features:
    - Real-time path validation
    - Auto-completion with directory scanning
    - Navigation history integration
    - Keyboard shortcuts
    - Path bookmarking
    - Drive/mount point detection
    """

    # Signals
    navigation_requested = pyqtSignal(str)  # path
    path_changed = pyqtSignal(str)  # path
    completion_needed = pyqtSignal(str)  # partial_path
    bookmark_requested = pyqtSignal(str)  # path

    def __init__(self, parent=None):
        """Initialize the address bar."""
        super().__init__(parent)

        self.current_path = ""
        self.is_editing = False

        # Setup UI
        self.setup_ui()
        self.setup_completer()
        self.setup_actions()

        # Setup logging
        self.logger = logging.getLogger("RFU.AddressBar")

        self.logger.debug("AddressBar initialized")

    def setup_ui(self) -> None:
        """Setup the address bar user interface."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        # Path icon/indicator
        self.path_icon = QLabel()
        self.path_icon.setFixedSize(16, 16)
        self.path_icon.setStyleSheet("QLabel { margin: 2px; }")
        layout.addWidget(self.path_icon)

        # Main path input
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Enter path or start typing...")
        self.path_edit.returnPressed.connect(self.on_path_entered)
        self.path_edit.textChanged.connect(self.on_text_changed)
        self.path_edit.focusInEvent = self.on_focus_in
        self.path_edit.focusOutEvent = self.on_focus_out
        layout.addWidget(self.path_edit, 1)

        # Navigation buttons
        self.nav_button = QToolButton()
        self.nav_button.setText("⚡")
        self.nav_button.setToolTip("Navigate to path")
        self.nav_button.clicked.connect(self.navigate_to_current_path)
        layout.addWidget(self.nav_button)

        # Bookmark button
        self.bookmark_button = QToolButton()
        self.bookmark_button.setText("⭐")
        self.bookmark_button.setToolTip("Bookmark this path")
        self.bookmark_button.clicked.connect(self.bookmark_current_path)
        layout.addWidget(self.bookmark_button)

        # Options menu button
        self.options_button = QToolButton()
        self.options_button.setText("⋮")
        self.options_button.setToolTip("Address bar options")
        self.options_button.setPopupMode(QToolButton.InstantPopup)
        layout.addWidget(self.options_button)

        # Set initial appearance
        self.update_appearance()

    def setup_completer(self) -> None:
        """Setup auto-completion for the address bar."""
        self.completer = AddressBarCompleter(self)
        self.path_edit.setCompleter(self.completer)

        # Connect completer signals
        self.completer.activated.connect(self.on_completion_selected)

    def setup_actions(self) -> None:
        """Setup keyboard shortcuts and context menu actions."""
        # Keyboard shortcuts
        self.path_edit.addAction(
            QAction(
                "Go Up",
                self,
                shortcut=QKeySequence("Alt+Up"),
                triggered=self.go_up,
            )
        )

        # Context menu for options button
        options_menu = QMenu(self)

        # Copy path action
        copy_action = QAction("Copy Path", self)
        copy_action.triggered.connect(self.copy_path_to_clipboard)
        options_menu.addAction(copy_action)

        # Paste path action
        paste_action = QAction("Paste Path", self)
        paste_action.triggered.connect(self.paste_path_from_clipboard)
        options_menu.addAction(paste_action)

        options_menu.addSeparator()

        # Show hidden files toggle
        show_hidden_action = QAction("Show Hidden Files", self)
        show_hidden_action.setCheckable(True)
        options_menu.addAction(show_hidden_action)

        # Case sensitive completion toggle
        case_sensitive_action = QAction("Case Sensitive Completion", self)
        case_sensitive_action.setCheckable(True)
        case_sensitive_action.toggled.connect(self.toggle_case_sensitivity)
        options_menu.addAction(case_sensitive_action)

        self.options_button.setMenu(options_menu)

    def set_path(self, path: str) -> None:
        """
        Set the current path in the address bar.

        Args:
            path: Path to display
        """
        normalized_path = PathValidator.normalize_path(path)

        if normalized_path != self.current_path:
            self.current_path = normalized_path

            # Update UI if not currently editing
            if not self.is_editing:
                self.path_edit.setText(self.current_path)

            # Update appearance
            self.update_appearance()

            # Emit signal
            self.path_changed.emit(self.current_path)

            self.logger.debug(f"Path set to: {self.current_path}")

    def get_path(self) -> str:
        """
        Get the current path from the address bar.

        Returns:
            str: Current path
        """
        return self.current_path

    def on_text_changed(self, text: str) -> None:
        """Handle text changes in the address bar."""
        self.is_editing = True

        # Update completions if text is a potential path
        if len(text) > 1 and (os.sep in text or ":" in text):
            self.completer.update_completions(text)

        # Update appearance based on validity
        self.update_appearance()

    def on_path_entered(self) -> None:
        """Handle path entry (Return key pressed)."""
        entered_path = self.path_edit.text().strip()

        if entered_path:
            self.navigate_to_path(entered_path)

        self.is_editing = False

    def on_completion_selected(self, completion: str) -> None:
        """Handle completion selection."""
        self.path_edit.setText(completion)
        self.navigate_to_path(completion)

    def on_focus_in(self, event) -> None:
        """Handle focus in event."""
        self.is_editing = True
        # Call original focus in event
        QLineEdit.focusInEvent(self.path_edit, event)

    def on_focus_out(self, event) -> None:
        """Handle focus out event."""
        self.is_editing = False

        # Revert to current path if invalid entry
        if not PathValidator.is_valid_path(self.path_edit.text()):
            self.path_edit.setText(self.current_path)

        # Call original focus out event
        QLineEdit.focusOutEvent(self.path_edit, event)

    def navigate_to_path(self, path: str) -> None:
        """
        Navigate to the specified path.

        Args:
            path: Path to navigate to
        """
        if PathValidator.is_valid_path(path):
            normalized_path = PathValidator.normalize_path(path)
            self.set_path(normalized_path)
            self.navigation_requested.emit(normalized_path)
            self.logger.info(f"Navigation requested: {normalized_path}")
        else:
            self.logger.warning(f"Invalid path entered: {path}")
            self.show_error_state()

    def navigate_to_current_path(self) -> None:
        """Navigate to the currently entered path."""
        self.navigate_to_path(self.path_edit.text())

    def go_up(self) -> None:
        """Navigate to parent directory."""
        parent_path = PathValidator.get_parent_path(self.current_path)
        if parent_path:
            self.navigate_to_path(parent_path)

    def bookmark_current_path(self) -> None:
        """Bookmark the current path."""
        if self.current_path:
            self.bookmark_requested.emit(self.current_path)
            self.logger.info(f"Bookmark requested: {self.current_path}")

    def copy_path_to_clipboard(self) -> None:
        """Copy current path to clipboard."""
        from PyQt5.QtWidgets import QApplication

        clipboard = QApplication.clipboard()
        clipboard.setText(self.current_path)
        self.logger.debug("Path copied to clipboard")

    def paste_path_from_clipboard(self) -> None:
        """Paste path from clipboard."""
        from PyQt5.QtWidgets import QApplication

        clipboard = QApplication.clipboard()
        text = clipboard.text()

        if text and PathValidator.is_valid_path(text):
            self.navigate_to_path(text)
        else:
            self.path_edit.setText(text)

    def toggle_case_sensitivity(self, enabled: bool) -> None:
        """Toggle case sensitivity for completion."""
        if enabled:
            self.completer.setCaseSensitivity(Qt.CaseSensitive)
        else:
            self.completer.setCaseSensitivity(Qt.CaseInsensitive)

    def update_appearance(self) -> None:
        """Update visual appearance based on current state."""
        current_text = self.path_edit.text()

        # Determine state
        if self.is_editing:
            if PathValidator.is_valid_path(current_text):
                self.set_valid_state()
            else:
                self.set_invalid_state()
        else:
            self.set_normal_state()

        # Update path icon
        self.update_path_icon()

    def set_normal_state(self) -> None:
        """Set normal appearance state."""
        self.path_edit.setStyleSheet("")
        self.nav_button.setEnabled(True)
        self.bookmark_button.setEnabled(bool(self.current_path))

    def set_valid_state(self) -> None:
        """Set valid path appearance state."""
        self.path_edit.setStyleSheet(
            """
            QLineEdit {
                border: 2px solid green;
                background-color: #f0fff0;
            }
        """
        )
        self.nav_button.setEnabled(True)
        self.bookmark_button.setEnabled(True)

    def set_invalid_state(self) -> None:
        """Set invalid path appearance state."""
        self.path_edit.setStyleSheet(
            """
            QLineEdit {
                border: 2px solid red;
                background-color: #fff0f0;
            }
        """
        )
        self.nav_button.setEnabled(False)
        self.bookmark_button.setEnabled(False)

    def show_error_state(self) -> None:
        """Temporarily show error state."""
        self.set_invalid_state()

        # Reset to normal after delay
        from PyQt5.QtCore import QTimer

        QTimer.singleShot(2000, self.update_appearance)

    def update_path_icon(self) -> None:
        """Update the path icon based on path type."""
        if not self.current_path:
            self.path_icon.setText("📁")
            return

        path_obj = Path(self.current_path)

        # Set icon based on path type
        if not path_obj.exists():
            icon = "❌"
        elif path_obj.is_dir():
            # Check for special directories
            if path_obj.name.lower() in ["desktop", "documents", "downloads"]:
                icon = "📋"
            elif path_obj == path_obj.anchor:  # Root/drive
                icon = "💾"
            else:
                icon = "📁"
        else:
            icon = "📄"

        self.path_icon.setText(icon)

    def clear(self) -> None:
        """Clear the address bar."""
        self.current_path = ""
        self.path_edit.clear()
        self.is_editing = False
        self.update_appearance()
        self.logger.debug("Address bar cleared")

    def set_read_only(self, read_only: bool) -> None:
        """
        Set address bar read-only state.

        Args:
            read_only: Whether address bar should be read-only
        """
        self.path_edit.setReadOnly(read_only)
        self.nav_button.setEnabled(not read_only)
        self.bookmark_button.setEnabled(
            not read_only and bool(self.current_path)
        )

        if read_only:
            self.path_edit.setStyleSheet(
                "QLineEdit { background-color: #f5f5f5; }"
            )
        else:
            self.update_appearance()

    def get_completion_suggestions(self, partial_path: str) -> List[str]:
        """
        Get completion suggestions for partial path.

        Args:
            partial_path: Partial path to complete

        Returns:
            List of completion suggestions
        """
        self.completer.update_completions(partial_path)
        return list(self.completer.completion_cache)
