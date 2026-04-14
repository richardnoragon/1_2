"""Toolbar Manager for Advanced Folders.

Enterprise-grade toolbar management system providing comprehensive action controls,
keyboard shortcuts, and contextual tool organization.

Features:
- Dynamic toolbar construction based on context
- Keyboard shortcut management and display
- Icon and theme support with high-DPI scaling
- Accessibility compliance with ARIA labels
- Context-sensitive tool availability
- Performance optimized with lazy loading
"""

import logging
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from PyQt5.QtCore import QObject, QSettings, QSize, Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QKeySequence, QPainter, QPixmap
from PyQt5.QtWidgets import (
    QAction,
    QActionGroup,
    QApplication,
    QButtonGroup,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QPushButton,
    QToolBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from src.gui.themes import token


class ToolbarAction:
    """Single toolbar action with metadata and behavior."""

    def __init__(
        self,
        action_id: str,
        title: str,
        tooltip: str,
        icon_path: Optional[str] = None,
        shortcut: Optional[str] = None,
        callback: Optional[Callable] = None,
        enabled: bool = True,
        checkable: bool = False,
        checked: bool = False,
        group: Optional[str] = None,
    ):
        """Initialize toolbar action.

        Args:
            action_id: Unique action identifier
            title: Action display title
            tooltip: Tooltip text
            icon_path: Path to action icon
            shortcut: Keyboard shortcut
            callback: Action callback function
            enabled: Initial enabled state
            checkable: Whether action is checkable
            checked: Initial checked state
            group: Action group for mutual exclusion
        """
        self.action_id = action_id
        self.title = title
        self.tooltip = tooltip
        self.icon_path = icon_path
        self.shortcut = shortcut
        self.callback = callback
        self.enabled = enabled
        self.checkable = checkable
        self.checked = checked
        self.group = group

        # Runtime properties
        self.qaction: Optional[QAction] = None
        self.visible = True
        self.priority = 0


class ToolbarSection:
    """Logical section of toolbar with related actions."""

    def __init__(self, section_id: str, title: str, actions: List[ToolbarAction]):
        """Initialize toolbar section.

        Args:
            section_id: Unique section identifier
            title: Section display title
            actions: List of actions in section
        """
        self.section_id = section_id
        self.title = title
        self.actions = actions
        self.visible = True
        self.collapsible = True


class AdvancedFoldersToolbar(QObject):
    """Enterprise-grade toolbar manager for Advanced Folders."""

    # Signals for action events
    actionTriggered = pyqtSignal(str, object)  # action_id, data
    contextChanged = pyqtSignal(str)  # context_name
    toolbarConfigChanged = pyqtSignal(dict)  # configuration

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize toolbar manager.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        self.logger = logging.getLogger("AdvancedFolders.Toolbar")
        self.parent_widget = parent

        # Toolbar configuration
        self.toolbar_sections: Dict[str, ToolbarSection] = {}
        self.action_registry: Dict[str, ToolbarAction] = {}
        self.action_groups: Dict[str, QActionGroup] = {}

        # UI components
        self.main_toolbar: Optional[QToolBar] = None
        self.context_toolbars: Dict[str, QToolBar] = {}
        self.quick_access_bar: Optional[QFrame] = None

        # State management
        self.current_context = "default"
        self.toolbar_visible = True
        self.customization_enabled = True

        # Initialize default actions
        self._register_default_actions()
        self._create_default_sections()

        self.logger.info("Advanced Folders toolbar manager initialized")

    def _register_default_actions(self):
        """Register default toolbar actions."""
        default_actions = [
            # File operations
            ToolbarAction(
                "new_folder",
                "New Folder",
                "Create new folder configuration",
                ":/icons/folder_new.png",
                "Ctrl+N",
                group="file_ops",
            ),
            ToolbarAction(
                "edit_folder",
                "Edit Folder",
                "Edit selected folder configuration",
                ":/icons/folder_edit.png",
                "Ctrl+E",
                group="file_ops",
            ),
            ToolbarAction(
                "delete_folder",
                "Delete Folder",
                "Delete selected folder configuration",
                ":/icons/folder_delete.png",
                "Delete",
                group="file_ops",
            ),
            ToolbarAction(
                "refresh_folders",
                "Refresh",
                "Refresh folder list",
                ":/icons/refresh.png",
                "F5",
                group="file_ops",
            ),
            # Search operations
            ToolbarAction(
                "quick_search",
                "Quick Search",
                "Perform quick search",
                ":/icons/search.png",
                "Ctrl+F",
                group="search_ops",
            ),
            ToolbarAction(
                "advanced_search",
                "Advanced Search",
                "Open advanced search dialog",
                ":/icons/search_advanced.png",
                "Ctrl+Shift+F",
                group="search_ops",
            ),
            ToolbarAction(
                "clear_search",
                "Clear Search",
                "Clear search results",
                ":/icons/clear.png",
                "Ctrl+Shift+C",
                group="search_ops",
            ),
            ToolbarAction(
                "save_search",
                "Save Search",
                "Save current search parameters",
                ":/icons/save_search.png",
                "Ctrl+S",
                group="search_ops",
            ),
            # View operations
            ToolbarAction(
                "view_details",
                "Details View",
                "Show detailed file information",
                ":/icons/view_details.png",
                checkable=True,
                checked=True,
                group="view_mode",
            ),
            ToolbarAction(
                "view_list",
                "List View",
                "Show simple file list",
                ":/icons/view_list.png",
                checkable=True,
                group="view_mode",
            ),
            ToolbarAction(
                "view_icons",
                "Icons View",
                "Show files as icons",
                ":/icons/view_icons.png",
                checkable=True,
                group="view_mode",
            ),
            # Tools and utilities
            ToolbarAction(
                "export_results",
                "Export Results",
                "Export search results",
                ":/icons/export.png",
                "Ctrl+Alt+E",
                group="tools",
            ),
            ToolbarAction(
                "import_config",
                "Import Config",
                "Import folder configurations",
                ":/icons/import.png",
                "Ctrl+Alt+I",
                group="tools",
            ),
            ToolbarAction(
                "preferences",
                "Preferences",
                "Open preferences dialog",
                ":/icons/preferences.png",
                "Ctrl+,",
                group="tools",
            ),
            ToolbarAction(
                "help",
                "Help",
                "Show help documentation",
                ":/icons/help.png",
                "F1",
                group="tools",
            ),
            # Selection operations
            ToolbarAction(
                "select_all",
                "Select All",
                "Select all search results",
                ":/icons/select_all.png",
                "Ctrl+A",
                group="selection",
            ),
            ToolbarAction(
                "select_none",
                "Select None",
                "Clear selection",
                ":/icons/select_none.png",
                "Ctrl+D",
                group="selection",
            ),
            ToolbarAction(
                "invert_selection",
                "Invert Selection",
                "Invert current selection",
                ":/icons/select_invert.png",
                "Ctrl+I",
                group="selection",
            ),
        ]

        # Register actions
        for action in default_actions:
            self.register_action(action)

    def _create_default_sections(self):
        """Create default toolbar sections."""
        sections = [
            ToolbarSection(
                "file_operations",
                "File Operations",
                [
                    self.action_registry[aid]
                    for aid in [
                        "new_folder",
                        "edit_folder",
                        "delete_folder",
                        "refresh_folders",
                    ]
                ],
            ),
            ToolbarSection(
                "search_operations",
                "Search Operations",
                [
                    self.action_registry[aid]
                    for aid in [
                        "quick_search",
                        "advanced_search",
                        "clear_search",
                        "save_search",
                    ]
                ],
            ),
            ToolbarSection(
                "view_modes",
                "View Modes",
                [
                    self.action_registry[aid]
                    for aid in ["view_details", "view_list", "view_icons"]
                ],
            ),
            ToolbarSection(
                "tools_utilities",
                "Tools & Utilities",
                [
                    self.action_registry[aid]
                    for aid in [
                        "export_results",
                        "import_config",
                        "preferences",
                        "help",
                    ]
                ],
            ),
        ]

        for section in sections:
            self.register_section(section)

    def register_action(self, action: ToolbarAction):
        """Register a new toolbar action.

        Args:
            action: Toolbar action to register
        """
        self.action_registry[action.action_id] = action
        self.logger.debug(f"Registered action: {action.action_id}")

    def register_section(self, section: ToolbarSection):
        """Register a new toolbar section.

        Args:
            section: Toolbar section to register
        """
        self.toolbar_sections[section.section_id] = section
        self.logger.debug(f"Registered section: {section.section_id}")

    def create_main_toolbar(self, parent_widget: QWidget) -> QToolBar:
        """Create the main toolbar.

        Args:
            parent_widget: Parent widget for toolbar

        Returns:
            Created main toolbar
        """
        if self.main_toolbar:
            return self.main_toolbar

        self.main_toolbar = QToolBar("Main Toolbar", parent_widget)
        self.main_toolbar.setObjectName("AdvancedFoldersMainToolbar")
        self.main_toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.main_toolbar.setIconSize(QSize(24, 24))
        self.main_toolbar.setMovable(True)
        self.main_toolbar.setFloatable(False)
        self.main_toolbar.setMinimumHeight(
            44
        )  # A11Y-8c: WCAG minimum interaction target

        # Build toolbar content
        self._build_toolbar_content(self.main_toolbar)

        # Apply styling
        self._apply_toolbar_styling(self.main_toolbar)

        self.logger.info("Main toolbar created")
        return self.main_toolbar

    def create_quick_access_bar(self, parent_widget: QWidget) -> QFrame:
        """Create quick access toolbar.

        Args:
            parent_widget: Parent widget for quick access bar

        Returns:
            Created quick access bar
        """
        if self.quick_access_bar:
            return self.quick_access_bar

        self.quick_access_bar = QFrame(parent_widget)
        self.quick_access_bar.setObjectName("QuickAccessBar")
        self.quick_access_bar.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.quick_access_bar.setMinimumHeight(
            52
        )  # A11Y-8c: 44px buttons + 8px vertical margins

        layout = QHBoxLayout(self.quick_access_bar)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(4)

        # Add quick access actions
        quick_actions = [
            "new_folder",
            "refresh_folders",
            "quick_search",
            "preferences",
        ]

        for action_id in quick_actions:
            if action_id in self.action_registry:
                action_def = self.action_registry[action_id]
                button = self._create_toolbar_button(action_def, icon_only=True)
                layout.addWidget(button)

        layout.addStretch()

        # Add context indicator
        self.context_label = QLabel("Default Context")
        self.context_label.setStyleSheet(
            f"QLabel { color: {token('text_muted')}; font-size: 11px; }"
        )
        layout.addWidget(self.context_label)

        self.logger.info("Quick access bar created")
        return self.quick_access_bar

    def _build_toolbar_content(self, toolbar: QToolBar):
        """Build toolbar content from registered sections.

        Args:
            toolbar: Toolbar to populate
        """
        toolbar.clear()

        for section_id, section in self.toolbar_sections.items():
            if not section.visible:
                continue

            # Add section separator if not first section
            if toolbar.actions():
                toolbar.addSeparator()

            # Add section actions
            for action_def in section.actions:
                if not action_def.visible:
                    continue

                qaction = self._create_qaction(action_def)
                toolbar.addAction(qaction)
                action_def.qaction = qaction

        # Add customization action at the end
        toolbar.addSeparator()
        customize_action = QAction("Customize...", toolbar)
        customize_action.setToolTip("Customize toolbar")
        customize_action.triggered.connect(self._show_customization_dialog)
        toolbar.addAction(customize_action)

    def _create_qaction(self, action_def: ToolbarAction) -> QAction:
        """Create QAction from toolbar action definition.

        Args:
            action_def: Toolbar action definition

        Returns:
            Created QAction
        """
        qaction = QAction(action_def.title, self.parent_widget)
        qaction.setToolTip(action_def.tooltip)
        qaction.setEnabled(action_def.enabled)
        qaction.setCheckable(action_def.checkable)
        qaction.setChecked(action_def.checked)

        # Set icon if available
        if action_def.icon_path:
            icon = self._load_icon(action_def.icon_path)
            qaction.setIcon(icon)

        # Set keyboard shortcut
        if action_def.shortcut:
            qaction.setShortcut(QKeySequence(action_def.shortcut))

        # Connect callback
        if action_def.callback:
            qaction.triggered.connect(action_def.callback)
        else:
            qaction.triggered.connect(
                lambda checked, aid=action_def.action_id: self.actionTriggered.emit(
                    aid, checked
                )
            )

        # Handle action groups
        if action_def.group:
            if action_def.group not in self.action_groups:
                self.action_groups[action_def.group] = QActionGroup(self)
                self.action_groups[action_def.group].setExclusive(action_def.checkable)

            self.action_groups[action_def.group].addAction(qaction)

        return qaction

    def _create_toolbar_button(
        self, action_def: ToolbarAction, icon_only: bool = False
    ) -> QToolButton:
        """Create toolbar button for action.

        Args:
            action_def: Action definition
            icon_only: Whether to show icon only

        Returns:
            Created toolbar button
        """
        button = QToolButton()
        button.setObjectName(f"toolbar_btn_{action_def.action_id}")
        button.setAccessibleName(action_def.title)
        if (
            action_def.tooltip
            and action_def.tooltip.strip() != action_def.title.strip()
        ):
            button.setAccessibleDescription(action_def.tooltip)

        if not icon_only:
            button.setText(action_def.title)
            button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        else:
            button.setToolButtonStyle(Qt.ToolButtonIconOnly)

        button.setToolTip(action_def.tooltip)
        button.setEnabled(action_def.enabled)
        button.setCheckable(action_def.checkable)
        button.setChecked(action_def.checked)

        # Set icon
        if action_def.icon_path:
            icon = self._load_icon(action_def.icon_path)
            button.setIcon(icon)

        # Connect callback
        if action_def.callback:
            button.clicked.connect(action_def.callback)
        else:
            button.clicked.connect(
                lambda checked, aid=action_def.action_id: self.actionTriggered.emit(
                    aid, checked
                )
            )

        button.setMinimumSize(44, 44)  # A11Y-8c: WCAG minimum interaction target
        return button

    def _load_icon(self, icon_path: str) -> QIcon:
        """Load icon from path with fallback.

        Args:
            icon_path: Path to icon file

        Returns:
            Loaded icon or default icon
        """
        icon = QIcon(icon_path)

        # If icon is null, create a simple colored rectangle as fallback
        if icon.isNull():
            pixmap = QPixmap(24, 24)
            pixmap.fill(Qt.gray)
            icon = QIcon(pixmap)

        return icon

    def _apply_toolbar_styling(self, toolbar: QToolBar):
        """Apply enterprise styling to toolbar.

        Args:
            toolbar: Toolbar to style
        """
        toolbar.setStyleSheet(
            f"""
            QToolBar {{
                background-color: {token('surface')};
                border: 1px solid {token('border')};
                border-radius: 4px;
                padding: 2px;
                spacing: 3px;
            }}
            
            QToolBar::separator {{
                background-color: {token('border')};
                width: 1px;
                margin: 2px 4px;
            }}
            
            QToolButton {{
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 3px;
                padding: 4px 8px;
                margin: 1px;
            }}
            
            QToolButton:hover {{
                background-color: {token('border_light')};
                border: 1px solid {token('text_muted')};
            }}
            
            QToolButton:pressed {{
                background-color: {token('border_light')};
                border: 1px solid {token('text_muted')};
            }}
            
            QToolButton:checked {{
                background-color: {token('accent')};
                border: 1px solid {token('button_primary')};
            }}
            
            QToolButton:disabled {{
                color: {token('text_muted')};
                background-color: transparent;
            }}
        """
        )

    def _show_customization_dialog(self):
        """Show toolbar customization dialog."""
        # Implementation would show a dialog for toolbar customization
        self.logger.info("Toolbar customization requested")
        # For now, just emit a signal
        self.toolbarConfigChanged.emit({"action": "customize"})

    def set_context(self, context_name: str):
        """Set current toolbar context.

        Args:
            context_name: Name of context to activate
        """
        if context_name != self.current_context:
            self.current_context = context_name

            # Update context label if quick access bar exists
            if self.quick_access_bar and hasattr(self, "context_label"):
                self.context_label.setText(f"{context_name.title()} Context")

            # Rebuild toolbar for new context
            if self.main_toolbar:
                self._update_toolbar_for_context(context_name)

            self.contextChanged.emit(context_name)
            self.logger.info(f"Toolbar context changed to: {context_name}")

    def _update_toolbar_for_context(self, context_name: str):
        """Update toolbar actions based on context.

        Args:
            context_name: Current context name
        """
        # Context-specific action visibility rules
        context_rules = {
            "default": {
                "visible": [
                    "new_folder",
                    "edit_folder",
                    "delete_folder",
                    "refresh_folders",
                    "quick_search",
                    "advanced_search",
                    "preferences",
                    "help",
                ],
                "enabled": [
                    "new_folder",
                    "refresh_folders",
                    "quick_search",
                    "advanced_search",
                    "preferences",
                    "help",
                ],
            },
            "search_results": {
                "visible": [
                    "clear_search",
                    "save_search",
                    "export_results",
                    "select_all",
                    "select_none",
                    "view_details",
                    "view_list",
                ],
                "enabled": [
                    "clear_search",
                    "save_search",
                    "export_results",
                    "select_all",
                    "select_none",
                    "view_details",
                    "view_list",
                ],
            },
            "folder_selected": {
                "visible": [
                    "edit_folder",
                    "delete_folder",
                    "quick_search",
                    "advanced_search",
                    "refresh_folders",
                ],
                "enabled": [
                    "edit_folder",
                    "delete_folder",
                    "quick_search",
                    "advanced_search",
                    "refresh_folders",
                ],
            },
        }

        if context_name in context_rules:
            rules = context_rules[context_name]

            # Update action visibility and enabled state
            for action_id, action_def in self.action_registry.items():
                if action_def.qaction:
                    action_def.qaction.setVisible(action_id in rules.get("visible", []))
                    action_def.qaction.setEnabled(action_id in rules.get("enabled", []))

    def enable_action(self, action_id: str, enabled: bool = True):
        """Enable or disable specific action.

        Args:
            action_id: Action identifier
            enabled: Enabled state
        """
        if action_id in self.action_registry:
            action_def = self.action_registry[action_id]
            action_def.enabled = enabled

            if action_def.qaction:
                action_def.qaction.setEnabled(enabled)

    def set_action_visible(self, action_id: str, visible: bool = True):
        """Set action visibility.

        Args:
            action_id: Action identifier
            visible: Visibility state
        """
        if action_id in self.action_registry:
            action_def = self.action_registry[action_id]
            action_def.visible = visible

            if action_def.qaction:
                action_def.qaction.setVisible(visible)

    def trigger_action(self, action_id: str):
        """Programmatically trigger an action.

        Args:
            action_id: Action identifier
        """
        if action_id in self.action_registry:
            action_def = self.action_registry[action_id]

            if action_def.qaction:
                action_def.qaction.trigger()
            elif action_def.callback:
                action_def.callback()
            else:
                self.actionTriggered.emit(action_id, None)

    def get_action_shortcuts(self) -> Dict[str, str]:
        """Get all action keyboard shortcuts.

        Returns:
            Dictionary mapping action IDs to shortcuts
        """
        shortcuts = {}
        for action_id, action_def in self.action_registry.items():
            if action_def.shortcut:
                shortcuts[action_id] = action_def.shortcut

        return shortcuts

    def save_toolbar_config(self):
        """Save current toolbar configuration."""
        settings = QSettings("RFU", "AdvancedFolders")

        # Save toolbar visibility
        settings.setValue("toolbar/main_visible", self.toolbar_visible)

        # Save action visibility states
        for action_id, action_def in self.action_registry.items():
            settings.setValue(f"toolbar/action_{action_id}_visible", action_def.visible)

        # Save section visibility states
        for section_id, section in self.toolbar_sections.items():
            settings.setValue(f"toolbar/section_{section_id}_visible", section.visible)

        self.logger.debug("Toolbar configuration saved")

    def load_toolbar_config(self):
        """Load toolbar configuration from settings."""
        settings = QSettings("RFU", "AdvancedFolders")

        # Load toolbar visibility
        self.toolbar_visible = settings.value("toolbar/main_visible", True, type=bool)

        # Load action visibility states
        for action_id, action_def in self.action_registry.items():
            visible = settings.value(
                f"toolbar/action_{action_id}_visible", True, type=bool
            )
            action_def.visible = visible

        # Load section visibility states
        for section_id, section in self.toolbar_sections.items():
            visible = settings.value(
                f"toolbar/section_{section_id}_visible", True, type=bool
            )
            section.visible = visible

        self.logger.debug("Toolbar configuration loaded")

    def get_toolbar_sections(self) -> Dict[str, ToolbarSection]:
        """Get all toolbar sections.

        Returns:
            Dictionary of toolbar sections
        """
        return self.toolbar_sections.copy()

    def get_action_registry(self) -> Dict[str, ToolbarAction]:
        """Get all registered actions.

        Returns:
            Dictionary of registered actions
        """
        return self.action_registry.copy()

    def set_toolbar_visible(self, visible: bool):
        """Set toolbar visibility.

        Args:
            visible: Visibility state
        """
        self.toolbar_visible = visible

        if self.main_toolbar:
            self.main_toolbar.setVisible(visible)

        if self.quick_access_bar:
            self.quick_access_bar.setVisible(visible)

    def cleanup(self):
        """Clean up toolbar resources."""
        # Save configuration
        self.save_toolbar_config()

        # Clear action groups
        for group in self.action_groups.values():
            group.setParent(None)
        self.action_groups.clear()

        # Clear toolbars
        if self.main_toolbar:
            self.main_toolbar.setParent(None)
            self.main_toolbar = None

        if self.quick_access_bar:
            self.quick_access_bar.setParent(None)
            self.quick_access_bar = None

        self.logger.info("Toolbar manager cleaned up")
