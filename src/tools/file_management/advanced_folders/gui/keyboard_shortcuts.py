"""Keyboard Shortcuts Manager.

Enterprise-grade keyboard shortcuts manager that provides comprehensive
keyboard navigation, accessibility, and customization support for the
Advanced Folders interface.

Features:
- Comprehensive keyboard shortcuts for all functionality
- Customizable keyboard bindings
- Accessibility compliance (WCAG 2.1 AA)
- Context-sensitive shortcuts
- Visual feedback and help system
- Cross-platform compatibility
"""
from src.rfu.localization import localized_widget as _ui_widget, bind_literal as _ui_bind
from src.rfu import font_tokens

import logging
from typing import Any, Callable, Dict, List, Optional, Tuple

from PyQt5.QtCore import QEvent, QObject, Qt, pyqtSignal
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.gui.components.buttons import PrimaryButton, SecondaryButton
from src.gui.components.inputs import TextInput


class ShortcutAction:
    """Represents a keyboard shortcut action."""

    def __init__(
        self,
        action_id: str,
        description: str,
        default_shortcut: str,
        callback: Callable,
        context: str = "global",
        enabled: bool = True,
    ):
        """Initialize shortcut action.

        Args:
            action_id: Unique action identifier
            description: Human-readable description
            default_shortcut: Default keyboard shortcut
            callback: Function to call when triggered
            context: Context where shortcut is active
            enabled: Whether shortcut is enabled
        """
        self.action_id = action_id
        self.description = description
        self.default_shortcut = default_shortcut
        self.current_shortcut = default_shortcut
        self.callback = callback
        self.context = context
        self.enabled = enabled
        self.qaction: Optional[QAction] = None


class KeyboardShortcutsManager(QObject):
    """Enterprise-grade keyboard shortcuts manager.

    Provides comprehensive keyboard navigation with:
    - Context-sensitive shortcuts
    - Customizable key bindings
    - Accessibility compliance
    - Visual feedback and help
    - Conflict detection and resolution
    """

    # Signals
    shortcutTriggered = pyqtSignal(str, str)  # action_id, context
    shortcutConflict = pyqtSignal(
        str, str, str
    )  # action_id, shortcut, conflicting_action
    shortcutsChanged = pyqtSignal(dict)  # all_shortcuts
    helpRequested = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize keyboard shortcuts manager.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Initialize logging
        self.logger = logging.getLogger("AdvancedFolders.KeyboardShortcuts")
        self.logger.info("Initializing Keyboard Shortcuts Manager")

        # Parent widget for shortcut registration
        self.parent_widget = parent

        # Shortcut registry
        self.shortcuts: Dict[str, ShortcutAction] = {}
        self.context_shortcuts: Dict[str, List[str]] = {}
        self.active_context = "global"

        # Shortcut conflicts tracking
        self.conflicts: Dict[str, List[str]] = {}

        # Initialize default shortcuts
        self._initialize_default_shortcuts()

        # Load custom shortcuts
        self._load_custom_shortcuts()

        # Setup shortcuts
        self._setup_shortcuts()

        self.logger.info("Keyboard Shortcuts Manager initialized successfully")

    def _initialize_default_shortcuts(self):
        """Initialize default keyboard shortcuts."""
        # File operations
        self.register_shortcut(
            "new_folder",
            "Create New Folder",
            "Ctrl+N",
            self._placeholder_callback,
            "global",
        )

        self.register_shortcut(
            "open_folder",
            "Open Folder Configuration",
            "Ctrl+O",
            self._placeholder_callback,
            "global",
        )

        self.register_shortcut(
            "save_config",
            "Save Configuration",
            "Ctrl+S",
            self._placeholder_callback,
            "global",
        )

        self.register_shortcut(
            "save_as",
            "Save Configuration As...",
            "Ctrl+Shift+S",
            self._placeholder_callback,
            "global",
        )

        self.register_shortcut(
            "close_folder",
            "Close Current Folder",
            "Ctrl+W",
            self._placeholder_callback,
            "global",
        )

        self.register_shortcut(
            "exit",
            "Exit Application",
            "Ctrl+Q",
            self._placeholder_callback,
            "global",
        )

        # Edit operations
        self.register_shortcut(
            "cut", "Cut", "Ctrl+X", self._placeholder_callback, "global"
        )

        self.register_shortcut(
            "copy", "Copy", "Ctrl+C", self._placeholder_callback, "global"
        )

        self.register_shortcut(
            "paste", "Paste", "Ctrl+V", self._placeholder_callback, "global"
        )

        self.register_shortcut(
            "select_all",
            "Select All",
            "Ctrl+A",
            self._placeholder_callback,
            "search_results",
        )

        self.register_shortcut(
            "delete",
            "Delete Selected",
            "Delete",
            self._placeholder_callback,
            "search_results",
        )

        # Search operations
        self.register_shortcut(
            "quick_search",
            "Quick Search",
            "Ctrl+F",
            self._placeholder_callback,
            "global",
        )

        self.register_shortcut(
            "advanced_search",
            "Advanced Search",
            "Ctrl+Shift+F",
            self._placeholder_callback,
            "global",
        )

        self.register_shortcut(
            "clear_search",
            "Clear Search",
            "Ctrl+Shift+C",
            self._placeholder_callback,
            "global",
        )

        self.register_shortcut(
            "next_result",
            "Next Search Result",
            "F3",
            self._placeholder_callback,
            "search_results",
        )

        self.register_shortcut(
            "prev_result",
            "Previous Search Result",
            "Shift+F3",
            self._placeholder_callback,
            "search_results",
        )

        # Navigation shortcuts
        self.register_shortcut(
            "focus_tree",
            "Focus Folder Tree",
            "Ctrl+1",
            self._placeholder_callback,
            "global",
        )

        self.register_shortcut(
            "focus_search",
            "Focus Search Results",
            "Ctrl+2",
            self._placeholder_callback,
            "global",
        )

        self.register_shortcut(
            "focus_preview",
            "Focus Preview Pane",
            "Ctrl+3",
            self._placeholder_callback,
            "global",
        )

        self.register_shortcut(
            "toggle_tree",
            "Toggle Folder Tree",
            "F9",
            self._placeholder_callback,
            "global",
        )

        self.register_shortcut(
            "toggle_preview",
            "Toggle Preview Pane",
            "F10",
            self._placeholder_callback,
            "global",
        )

        # View operations
        self.register_shortcut(
            "view_details",
            "Details View",
            "Ctrl+D",
            self._placeholder_callback,
            "global",
        )

        self.register_shortcut(
            "view_list",
            "List View",
            "Ctrl+L",
            self._placeholder_callback,
            "global",
        )

        self.register_shortcut(
            "view_icons",
            "Icons View",
            "Ctrl+I",
            self._placeholder_callback,
            "global",
        )

        self.register_shortcut(
            "refresh",
            "Refresh View",
            "F5",
            self._placeholder_callback,
            "global",
        )

        self.register_shortcut(
            "zoom_in",
            "Zoom In",
            "Ctrl++",
            self._placeholder_callback,
            "preview",
        )

        self.register_shortcut(
            "zoom_out",
            "Zoom Out",
            "Ctrl+-",
            self._placeholder_callback,
            "preview",
        )

        self.register_shortcut(
            "zoom_reset",
            "Reset Zoom",
            "Ctrl+0",
            self._placeholder_callback,
            "preview",
        )

        # Help and accessibility
        self.register_shortcut(
            "help", "Show Help", "F1", self._placeholder_callback, "global"
        )

        self.register_shortcut(
            "shortcuts_help",
            "Show Keyboard Shortcuts",
            "Ctrl+/",
            self._show_shortcuts_help,
            "global",
        )

        self.register_shortcut(
            "accessibility_mode",
            "Toggle Accessibility Mode",
            "Ctrl+Alt+A",
            self._placeholder_callback,
            "global",
        )

        # Application shortcuts
        self.register_shortcut(
            "preferences",
            "Preferences",
            "Ctrl+,",
            self._placeholder_callback,
            "global",
        )

        self.register_shortcut(
            "about", "About", "F12", self._placeholder_callback, "global"
        )

        # Context-specific shortcuts
        self.register_shortcut(
            "expand_all",
            "Expand All",
            "Ctrl+Shift+E",
            self._placeholder_callback,
            "folder_tree",
        )

        self.register_shortcut(
            "collapse_all",
            "Collapse All",
            "Ctrl+Shift+W",
            self._placeholder_callback,
            "folder_tree",
        )

        self.register_shortcut(
            "sort_name",
            "Sort by Name",
            "Ctrl+Shift+N",
            self._placeholder_callback,
            "search_results",
        )

        self.register_shortcut(
            "sort_size",
            "Sort by Size",
            "Ctrl+Shift+S",
            self._placeholder_callback,
            "search_results",
        )

        self.register_shortcut(
            "sort_date",
            "Sort by Date",
            "Ctrl+Shift+D",
            self._placeholder_callback,
            "search_results",
        )

        self.register_shortcut(
            "sort_type",
            "Sort by Type",
            "Ctrl+Shift+T",
            self._placeholder_callback,
            "search_results",
        )

    def register_shortcut(
        self,
        action_id: str,
        description: str,
        default_shortcut: str,
        callback: Callable,
        context: str = "global",
        enabled: bool = True,
    ) -> bool:
        """Register a keyboard shortcut.

        Args:
            action_id: Unique action identifier
            description: Human-readable description
            default_shortcut: Default keyboard shortcut
            callback: Function to call when triggered
            context: Context where shortcut is active
            enabled: Whether shortcut is enabled

        Returns:
            True if registration was successful
        """
        try:
            # Check for existing action
            if action_id in self.shortcuts:
                self.logger.warning(f"Shortcut action already exists: {action_id}")
                return False

            # Validate shortcut string
            if not self._validate_shortcut(default_shortcut):
                self.logger.error(f"Invalid shortcut string: {default_shortcut}")
                return False

            # Create shortcut action
            shortcut_action = ShortcutAction(
                action_id,
                description,
                default_shortcut,
                callback,
                context,
                enabled,
            )

            # Register action
            self.shortcuts[action_id] = shortcut_action

            # Add to context registry
            if context not in self.context_shortcuts:
                self.context_shortcuts[context] = []
            self.context_shortcuts[context].append(action_id)

            # Check for conflicts
            self._check_shortcut_conflicts(action_id, default_shortcut)

            self.logger.debug(f"Registered shortcut: {action_id} -> {default_shortcut}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to register shortcut {action_id}: {e}")
            return False

    def unregister_shortcut(self, action_id: str) -> bool:
        """Unregister a keyboard shortcut.

        Args:
            action_id: Action identifier to unregister

        Returns:
            True if unregistration was successful
        """
        try:
            if action_id not in self.shortcuts:
                self.logger.warning(f"Shortcut action not found: {action_id}")
                return False

            shortcut_action = self.shortcuts[action_id]

            # Remove QAction if it exists
            if shortcut_action.qaction:
                shortcut_action.qaction.deleteLater()

            # Remove from context registry
            context = shortcut_action.context
            if context in self.context_shortcuts:
                if action_id in self.context_shortcuts[context]:
                    self.context_shortcuts[context].remove(action_id)

            # Remove from shortcuts registry
            del self.shortcuts[action_id]

            self.logger.debug(f"Unregistered shortcut: {action_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to unregister shortcut {action_id}: {e}")
            return False

    def set_shortcut(self, action_id: str, new_shortcut: str) -> bool:
        """Set a new shortcut for an action.

        Args:
            action_id: Action identifier
            new_shortcut: New shortcut string

        Returns:
            True if shortcut was set successfully
        """
        try:
            if action_id not in self.shortcuts:
                self.logger.error(f"Shortcut action not found: {action_id}")
                return False

            # Validate new shortcut
            if not self._validate_shortcut(new_shortcut):
                self.logger.error(f"Invalid shortcut string: {new_shortcut}")
                return False

            # Check for conflicts
            conflicts = self._check_shortcut_conflicts(
                action_id, new_shortcut, exclude_action=action_id
            )
            if conflicts:
                self.logger.warning(f"Shortcut conflict detected: {new_shortcut}")
                self.shortcutConflict.emit(action_id, new_shortcut, conflicts[0])
                return False

            # Update shortcut
            shortcut_action = self.shortcuts[action_id]
            old_shortcut = shortcut_action.current_shortcut
            shortcut_action.current_shortcut = new_shortcut

            # Update QAction
            if shortcut_action.qaction:
                shortcut_action.qaction.setShortcut(QKeySequence(new_shortcut))

            self.logger.debug(
                f"Updated shortcut {action_id}: {old_shortcut} -> {new_shortcut}"
            )

            # Emit change signal
            self.shortcutsChanged.emit(self.get_all_shortcuts())

            return True

        except Exception as e:
            self.logger.error(f"Failed to set shortcut {action_id}: {e}")
            return False

    def reset_shortcut(self, action_id: str) -> bool:
        """Reset shortcut to default value.

        Args:
            action_id: Action identifier

        Returns:
            True if reset was successful
        """
        if action_id not in self.shortcuts:
            return False

        shortcut_action = self.shortcuts[action_id]
        return self.set_shortcut(action_id, shortcut_action.default_shortcut)

    def reset_all_shortcuts(self):
        """Reset all shortcuts to default values."""
        for action_id in self.shortcuts:
            self.reset_shortcut(action_id)

    def enable_shortcut(self, action_id: str, enabled: bool = True) -> bool:
        """Enable or disable a shortcut.

        Args:
            action_id: Action identifier
            enabled: Whether to enable the shortcut

        Returns:
            True if operation was successful
        """
        if action_id not in self.shortcuts:
            return False

        shortcut_action = self.shortcuts[action_id]
        shortcut_action.enabled = enabled

        # Update QAction
        if shortcut_action.qaction:
            shortcut_action.qaction.setEnabled(enabled)

        return True

    def set_active_context(self, context: str):
        """Set the active shortcut context.

        Args:
            context: Context name
        """
        if context != self.active_context:
            self.logger.debug(
                f"Changing shortcut context: {self.active_context} -> {context}"
            )
            self.active_context = context
            self._update_context_shortcuts()

    def get_active_context(self) -> str:
        """Get the current active context.

        Returns:
            Active context name
        """
        return self.active_context

    def get_shortcuts_for_context(self, context: str) -> List[ShortcutAction]:
        """Get all shortcuts for a specific context.

        Args:
            context: Context name

        Returns:
            List of shortcut actions
        """
        if context not in self.context_shortcuts:
            return []

        return [
            self.shortcuts[action_id]
            for action_id in self.context_shortcuts[context]
            if action_id in self.shortcuts
        ]

    def get_all_shortcuts(self) -> Dict[str, Dict[str, Any]]:
        """Get all registered shortcuts.

        Returns:
            Dictionary of all shortcuts
        """
        result = {}
        for action_id, shortcut_action in self.shortcuts.items():
            result[action_id] = {
                "description": shortcut_action.description,
                "current_shortcut": shortcut_action.current_shortcut,
                "default_shortcut": shortcut_action.default_shortcut,
                "context": shortcut_action.context,
                "enabled": shortcut_action.enabled,
            }
        return result

    def _setup_shortcuts(self):
        """Setup all registered shortcuts."""
        if not self.parent_widget:
            self.logger.warning("No parent widget provided for shortcut setup")
            return

        for action_id, shortcut_action in self.shortcuts.items():
            self._create_qaction(shortcut_action)

    def _create_qaction(self, shortcut_action: ShortcutAction):
        """Create QAction for a shortcut.

        Args:
            shortcut_action: Shortcut action to create QAction for
        """
        if not self.parent_widget:
            return

        # Create QAction
        qaction = QAction(shortcut_action.description, self.parent_widget)
        qaction.setShortcut(QKeySequence(shortcut_action.current_shortcut))
        qaction.setEnabled(shortcut_action.enabled)

        # Connect signal
        qaction.triggered.connect(
            lambda checked, aid=shortcut_action.action_id: self._handle_shortcut_triggered(
                aid
            )
        )

        # Add to parent widget
        self.parent_widget.addAction(qaction)

        # Store reference
        shortcut_action.qaction = qaction

    def _handle_shortcut_triggered(self, action_id: str):
        """Handle shortcut trigger.

        Args:
            action_id: Triggered action ID
        """
        if action_id not in self.shortcuts:
            return

        shortcut_action = self.shortcuts[action_id]

        # Check if shortcut is active in current context
        if not self._is_shortcut_active(shortcut_action):
            return

        try:
            # Call the callback
            shortcut_action.callback()

            # Emit signal
            self.shortcutTriggered.emit(action_id, shortcut_action.context)

            self.logger.debug(f"Shortcut triggered: {action_id}")

        except Exception as e:
            self.logger.error(f"Error executing shortcut {action_id}: {e}")

    def _is_shortcut_active(self, shortcut_action: ShortcutAction) -> bool:
        """Check if shortcut is active in current context.

        Args:
            shortcut_action: Shortcut action to check

        Returns:
            True if shortcut is active
        """
        # Global shortcuts are always active
        if shortcut_action.context == "global":
            return True

        # Context-specific shortcuts are active only in their context
        return shortcut_action.context == self.active_context

    def _update_context_shortcuts(self):
        """Update shortcut availability based on current context."""
        for shortcut_action in self.shortcuts.values():
            if shortcut_action.qaction:
                is_active = self._is_shortcut_active(shortcut_action)
                shortcut_action.qaction.setEnabled(
                    is_active and shortcut_action.enabled
                )

    def _validate_shortcut(self, shortcut: str) -> bool:
        """Validate shortcut string.

        Args:
            shortcut: Shortcut string to validate

        Returns:
            True if shortcut is valid
        """
        try:
            key_sequence = QKeySequence(shortcut)
            return not key_sequence.isEmpty()
        except Exception:
            return False

    def _check_shortcut_conflicts(
        self,
        action_id: str,
        shortcut: str,
        exclude_action: Optional[str] = None,
    ) -> List[str]:
        """Check for shortcut conflicts.

        Args:
            action_id: Action ID to check
            shortcut: Shortcut string to check
            exclude_action: Action ID to exclude from conflict check

        Returns:
            List of conflicting action IDs
        """
        conflicts = []

        for other_action_id, other_shortcut_action in self.shortcuts.items():
            if other_action_id == exclude_action:
                continue

            if (
                other_shortcut_action.current_shortcut == shortcut
                and other_shortcut_action.context
                == self.shortcuts.get(
                    action_id, ShortcutAction("", "", "", lambda: None)
                ).context
            ):
                conflicts.append(other_action_id)

        return conflicts

    def _load_custom_shortcuts(self):
        """Load custom shortcuts from settings."""
        # This would load from QSettings or configuration file
        # For now, use defaults
        pass

    def _save_custom_shortcuts(self):
        """Save custom shortcuts to settings."""
        # This would save to QSettings or configuration file
        pass

    def _show_shortcuts_help(self):
        """Show keyboard shortcuts help dialog."""
        self.helpRequested.emit()

        # Create and show help dialog
        help_dialog = KeyboardShortcutsHelpDialog(self.parent_widget, self)
        help_dialog.exec_()

    def _placeholder_callback(self):
        """Placeholder callback for shortcuts without implementation."""
        self.logger.debug("Placeholder shortcut callback triggered")

    def get_shortcut_conflicts(self) -> Dict[str, List[str]]:
        """Get all shortcut conflicts.

        Returns:
            Dictionary of conflicts
        """
        conflicts = {}

        for action_id, shortcut_action in self.shortcuts.items():
            conflicting_actions = self._check_shortcut_conflicts(
                action_id,
                shortcut_action.current_shortcut,
                exclude_action=action_id,
            )
            if conflicting_actions:
                conflicts[action_id] = conflicting_actions

        return conflicts

    def shutdown(self):
        """Shutdown the shortcuts manager."""
        self.logger.info("Shutting down Keyboard Shortcuts Manager")

        # Save custom shortcuts
        self._save_custom_shortcuts()

        # Clean up QActions
        for shortcut_action in self.shortcuts.values():
            if shortcut_action.qaction:
                shortcut_action.qaction.deleteLater()

        self.logger.info("Keyboard Shortcuts Manager shutdown complete")


class KeyboardShortcutsHelpDialog(QDialog):
    """Help dialog for displaying keyboard shortcuts."""

    def __init__(self, parent: QWidget, shortcuts_manager: KeyboardShortcutsManager):
        """Initialize help dialog.

        Args:
            parent: Parent widget
            shortcuts_manager: Shortcuts manager instance
        """
        super().__init__(parent)

        self.shortcuts_manager = shortcuts_manager

        _ui_bind(self, 'setWindowTitle', 'Legacy.s59cdaa26dd9dcd4c')
        self.setModal(True)
        self.resize(800, 600)

        self._setup_ui()
        self._populate_shortcuts()

        # Apply accessibility
        _ui_bind(self, 'setAccessibleName', 'Legacy.sc3de790a0e6a6529')
        _ui_bind(self, 'setAccessibleDescription', 'Legacy.s57cb8e662a5ac56e')

    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)

        # Header
        header_label = _ui_widget(QLabel, 'Legacy.s59cdaa26dd9dcd4c', 'setText')
        header_label.setStyleSheet(
            " font-weight: bold; margin-bottom: 10px;"
        )
        font_tokens.bind(header_label, "font.toolHeader")
        layout.addWidget(header_label)

        # Search box
        search_layout = QHBoxLayout()
        search_label = _ui_widget(QLabel, 'Legacy.sbd689c15b2ca8b8c', 'setText')
        self.search_box = TextInput("Search", "Type to filter shortcuts...")
        _ui_bind(self.search_box, 'setAccessibleName', 'Legacy.s9066acbf6eaa314f')
        self.search_box.textChanged.connect(self._filter_shortcuts)

        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_box)
        layout.addLayout(search_layout)

        # Shortcuts table
        self.shortcuts_table = QTableWidget()
        _ui_bind(self.shortcuts_table, 'setAccessibleName', 'Legacy.se9bef0b0f3c25e6e')
        self.shortcuts_table.setColumnCount(4)
        self.shortcuts_table.setHorizontalHeaderLabels(
            ["Action", "Shortcut", "Context", "Description"]
        )

        # Configure table
        header = self.shortcuts_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)

        self.shortcuts_table.setAlternatingRowColors(True)
        self.shortcuts_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.shortcuts_table.setSortingEnabled(True)

        layout.addWidget(self.shortcuts_table)

        # Buttons
        button_layout = QHBoxLayout()

        reset_button = _ui_widget(SecondaryButton, 'Legacy.se1c518097f23653d', 'setText')
        _ui_bind(reset_button, 'setAccessibleName', 'Legacy.s8344034b41356c05')
        reset_button.clicked.connect(self._reset_all_shortcuts)

        close_button = _ui_widget(PrimaryButton, 'Legacy.s7d9eb7acb13e2462', 'setText')
        _ui_bind(close_button, 'setAccessibleName', 'Legacy.secd2e39f1a28d6de')
        close_button.clicked.connect(self.accept)
        close_button.setDefault(True)

        button_layout.addWidget(reset_button)
        button_layout.addStretch()
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)

    def _populate_shortcuts(self):
        """Populate the shortcuts table."""
        all_shortcuts = self.shortcuts_manager.get_all_shortcuts()

        self.shortcuts_table.setRowCount(len(all_shortcuts))

        row = 0
        for action_id, shortcut_data in all_shortcuts.items():
            # Action ID
            action_item = QTableWidgetItem(action_id)
            action_item.setFlags(action_item.flags() & ~Qt.ItemIsEditable)
            self.shortcuts_table.setItem(row, 0, action_item)

            # Shortcut
            shortcut_item = QTableWidgetItem(shortcut_data["current_shortcut"])
            shortcut_item.setFlags(shortcut_item.flags() & ~Qt.ItemIsEditable)
            self.shortcuts_table.setItem(row, 1, shortcut_item)

            # Context
            context_item = QTableWidgetItem(shortcut_data["context"])
            context_item.setFlags(context_item.flags() & ~Qt.ItemIsEditable)
            self.shortcuts_table.setItem(row, 2, context_item)

            # Description
            description_item = QTableWidgetItem(shortcut_data["description"])
            description_item.setFlags(description_item.flags() & ~Qt.ItemIsEditable)
            self.shortcuts_table.setItem(row, 3, description_item)

            row += 1

        # Sort by action ID initially
        self.shortcuts_table.sortItems(0)

    def _filter_shortcuts(self, filter_text: str):
        """Filter shortcuts based on search text.

        Args:
            filter_text: Text to filter by
        """
        filter_text = filter_text.lower()

        for row in range(self.shortcuts_table.rowCount()):
            should_show = False

            # Check all columns for filter text
            for col in range(self.shortcuts_table.columnCount()):
                item = self.shortcuts_table.item(row, col)
                if item and filter_text in item.text().lower():
                    should_show = True
                    break

            self.shortcuts_table.setRowHidden(row, not should_show)

    def _reset_all_shortcuts(self):
        """Reset all shortcuts to defaults."""
        self.shortcuts_manager.reset_all_shortcuts()
        self._populate_shortcuts()  # Refresh display
