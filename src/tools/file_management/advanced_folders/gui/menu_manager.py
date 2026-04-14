"""Menu Manager for Advanced Folders.

Enterprise-grade menu system providing comprehensive navigation, context menus,
and keyboard shortcut integration with accessibility support.

Features:
- Hierarchical menu structure with proper organization
- Context-sensitive menu items and availability
- Keyboard navigation and shortcut display
- Accessibility compliance with ARIA labels
- Dynamic menu construction based on application state
- Menu customization and user preferences
"""

import logging
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Union

from PyQt5.QtCore import QObject, QSettings, Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QKeySequence, QPixmap
from PyQt5.QtWidgets import (
    QAction,
    QActionGroup,
    QApplication,
    QMenu,
    QMenuBar,
    QWidget,
)

from src.gui.themes import token


@dataclass
class MenuItemDefinition:
    """Definition for a single menu item."""

    item_id: str
    title: str
    tooltip: str = ""
    icon_path: Optional[str] = None
    shortcut: Optional[str] = None
    callback: Optional[Callable] = None
    enabled: bool = True
    checkable: bool = False
    checked: bool = False
    separator_after: bool = False
    submenu_items: Optional[List["MenuItemDefinition"]] = None


@dataclass
class MenuDefinition:
    """Definition for a top-level menu."""

    menu_id: str
    title: str
    items: List[MenuItemDefinition]
    visible: bool = True
    position: int = 0


class AdvancedFoldersMenuManager(QObject):
    """Enterprise-grade menu manager for Advanced Folders."""

    # Signals for menu events
    menuItemTriggered = pyqtSignal(str, object)  # item_id, data
    contextMenuRequested = pyqtSignal(str, object)  # context, position
    menuConfigChanged = pyqtSignal(dict)  # configuration

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize menu manager.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        self.logger = logging.getLogger("AdvancedFolders.Menu")
        self.parent_widget = parent

        # Menu configuration
        self.menu_definitions: Dict[str, MenuDefinition] = {}
        self.menu_items: Dict[str, MenuItemDefinition] = {}
        self.action_groups: Dict[str, QActionGroup] = {}

        # UI components
        self.menu_bar: Optional[QMenuBar] = None
        self.context_menus: Dict[str, QMenu] = {}

        # State management
        self.menu_visible = True
        self.customization_enabled = True

        # Initialize default menus
        self._register_default_menus()

        self.logger.info("Advanced Folders menu manager initialized")

    def _register_default_menus(self):
        """Register default menu structure."""
        # File menu
        file_menu = MenuDefinition(
            "file",
            "File",
            [
                MenuItemDefinition(
                    "new_folder",
                    "New Folder Configuration...",
                    "Create a new folder configuration",
                    ":/icons/folder_new.png",
                    "Ctrl+N",
                ),
                MenuItemDefinition(
                    "open_folder",
                    "Open Folder Configuration...",
                    "Open an existing folder configuration",
                    ":/icons/folder_open.png",
                    "Ctrl+O",
                ),
                MenuItemDefinition("separator1", "", separator_after=True),
                MenuItemDefinition(
                    "save_config",
                    "Save Configuration",
                    "Save current folder configuration",
                    ":/icons/save.png",
                    "Ctrl+S",
                ),
                MenuItemDefinition(
                    "save_config_as",
                    "Save Configuration As...",
                    "Save configuration with new name",
                    ":/icons/save_as.png",
                    "Ctrl+Shift+S",
                ),
                MenuItemDefinition("separator2", "", separator_after=True),
                MenuItemDefinition(
                    "import_config",
                    "Import Configuration...",
                    "Import folder configuration from file",
                    ":/icons/import.png",
                    "Ctrl+I",
                ),
                MenuItemDefinition(
                    "export_config",
                    "Export Configuration...",
                    "Export current configuration to file",
                    ":/icons/export.png",
                    "Ctrl+E",
                ),
                MenuItemDefinition("separator3", "", separator_after=True),
                MenuItemDefinition(
                    "recent_configs",
                    "Recent Configurations",
                    "Access recently used configurations",
                    submenu_items=[
                        MenuItemDefinition(
                            "clear_recent",
                            "Clear Recent List",
                            "Clear the recent configurations list",
                        )
                    ],
                ),
                MenuItemDefinition("separator4", "", separator_after=True),
                MenuItemDefinition(
                    "exit",
                    "Exit",
                    "Exit Advanced Folders",
                    ":/icons/exit.png",
                    "Ctrl+Q",
                ),
            ],
        )

        # Edit menu
        edit_menu = MenuDefinition(
            "edit",
            "Edit",
            [
                MenuItemDefinition(
                    "undo",
                    "Undo",
                    "Undo last action",
                    ":/icons/undo.png",
                    "Ctrl+Z",
                    enabled=False,
                ),
                MenuItemDefinition(
                    "redo",
                    "Redo",
                    "Redo last undone action",
                    ":/icons/redo.png",
                    "Ctrl+Y",
                    enabled=False,
                ),
                MenuItemDefinition("separator1", "", separator_after=True),
                MenuItemDefinition(
                    "cut",
                    "Cut",
                    "Cut selected items",
                    ":/icons/cut.png",
                    "Ctrl+X",
                    enabled=False,
                ),
                MenuItemDefinition(
                    "copy",
                    "Copy",
                    "Copy selected items",
                    ":/icons/copy.png",
                    "Ctrl+C",
                    enabled=False,
                ),
                MenuItemDefinition(
                    "paste",
                    "Paste",
                    "Paste items from clipboard",
                    ":/icons/paste.png",
                    "Ctrl+V",
                    enabled=False,
                ),
                MenuItemDefinition("separator2", "", separator_after=True),
                MenuItemDefinition(
                    "select_all",
                    "Select All",
                    "Select all items",
                    ":/icons/select_all.png",
                    "Ctrl+A",
                ),
                MenuItemDefinition(
                    "select_none",
                    "Select None",
                    "Clear selection",
                    ":/icons/select_none.png",
                    "Ctrl+D",
                ),
                MenuItemDefinition(
                    "invert_selection",
                    "Invert Selection",
                    "Invert selection",
                    ":/icons/select_invert.png",
                    "Ctrl+Shift+I",
                ),
                MenuItemDefinition("separator3", "", separator_after=True),
                MenuItemDefinition(
                    "find",
                    "Find...",
                    "Find files and folders",
                    ":/icons/find.png",
                    "Ctrl+F",
                ),
                MenuItemDefinition(
                    "find_next",
                    "Find Next",
                    "Find next match",
                    ":/icons/find_next.png",
                    "F3",
                    enabled=False,
                ),
                MenuItemDefinition(
                    "find_previous",
                    "Find Previous",
                    "Find previous match",
                    ":/icons/find_previous.png",
                    "Shift+F3",
                    enabled=False,
                ),
                MenuItemDefinition("separator4", "", separator_after=True),
                MenuItemDefinition(
                    "preferences",
                    "Preferences...",
                    "Open preferences dialog",
                    ":/icons/preferences.png",
                    "Ctrl+,",
                ),
            ],
        )

        # View menu
        view_menu = MenuDefinition(
            "view",
            "View",
            [
                MenuItemDefinition(
                    "view_mode",
                    "View Mode",
                    "Select view mode",
                    submenu_items=[
                        MenuItemDefinition(
                            "view_details",
                            "Details",
                            "Show detailed view",
                            ":/icons/view_details.png",
                            checkable=True,
                            checked=True,
                        ),
                        MenuItemDefinition(
                            "view_list",
                            "List",
                            "Show list view",
                            ":/icons/view_list.png",
                            checkable=True,
                        ),
                        MenuItemDefinition(
                            "view_icons",
                            "Icons",
                            "Show icon view",
                            ":/icons/view_icons.png",
                            checkable=True,
                        ),
                    ],
                ),
                MenuItemDefinition("separator1", "", separator_after=True),
                MenuItemDefinition(
                    "show_toolbar",
                    "Show Toolbar",
                    "Toggle toolbar visibility",
                    checkable=True,
                    checked=True,
                ),
                MenuItemDefinition(
                    "show_status_bar",
                    "Show Status Bar",
                    "Toggle status bar visibility",
                    checkable=True,
                    checked=True,
                ),
                MenuItemDefinition(
                    "show_quick_access",
                    "Show Quick Access Bar",
                    "Toggle quick access bar visibility",
                    checkable=True,
                    checked=True,
                ),
                MenuItemDefinition("separator2", "", separator_after=True),
                MenuItemDefinition(
                    "show_folder_tree",
                    "Show Folder Tree",
                    "Toggle folder tree visibility",
                    checkable=True,
                    checked=True,
                ),
                MenuItemDefinition(
                    "show_search_results",
                    "Show Search Results",
                    "Toggle search results visibility",
                    checkable=True,
                    checked=True,
                ),
                MenuItemDefinition("separator3", "", separator_after=True),
                MenuItemDefinition(
                    "refresh",
                    "Refresh",
                    "Refresh current view",
                    ":/icons/refresh.png",
                    "F5",
                ),
                MenuItemDefinition(
                    "refresh_all",
                    "Refresh All",
                    "Refresh all views",
                    ":/icons/refresh_all.png",
                    "Ctrl+F5",
                ),
                MenuItemDefinition("separator4", "", separator_after=True),
                MenuItemDefinition(
                    "zoom_in",
                    "Zoom In",
                    "Increase font size",
                    ":/icons/zoom_in.png",
                    "Ctrl++",
                ),
                MenuItemDefinition(
                    "zoom_out",
                    "Zoom Out",
                    "Decrease font size",
                    ":/icons/zoom_out.png",
                    "Ctrl+-",
                ),
                MenuItemDefinition(
                    "zoom_reset",
                    "Reset Zoom",
                    "Reset font size to default",
                    ":/icons/zoom_reset.png",
                    "Ctrl+0",
                ),
            ],
        )

        # Search menu
        search_menu = MenuDefinition(
            "search",
            "Search",
            [
                MenuItemDefinition(
                    "quick_search",
                    "Quick Search",
                    "Perform quick search",
                    ":/icons/search.png",
                    "Ctrl+F",
                ),
                MenuItemDefinition(
                    "advanced_search",
                    "Advanced Search...",
                    "Open advanced search dialog",
                    ":/icons/search_advanced.png",
                    "Ctrl+Shift+F",
                ),
                MenuItemDefinition("separator1", "", separator_after=True),
                MenuItemDefinition(
                    "search_in_folder",
                    "Search in Folder...",
                    "Search within selected folder",
                    ":/icons/search_folder.png",
                    "Ctrl+Alt+F",
                ),
                MenuItemDefinition(
                    "search_by_size",
                    "Search by Size...",
                    "Search files by size criteria",
                    ":/icons/search_size.png",
                ),
                MenuItemDefinition(
                    "search_by_date",
                    "Search by Date...",
                    "Search files by date criteria",
                    ":/icons/search_date.png",
                ),
                MenuItemDefinition(
                    "search_by_type",
                    "Search by Type...",
                    "Search files by type criteria",
                    ":/icons/search_type.png",
                ),
                MenuItemDefinition("separator2", "", separator_after=True),
                MenuItemDefinition(
                    "save_search",
                    "Save Search...",
                    "Save current search",
                    ":/icons/save_search.png",
                    "Ctrl+S",
                ),
                MenuItemDefinition(
                    "load_search",
                    "Load Search...",
                    "Load saved search",
                    ":/icons/load_search.png",
                    "Ctrl+L",
                ),
                MenuItemDefinition("separator3", "", separator_after=True),
                MenuItemDefinition(
                    "clear_search",
                    "Clear Search",
                    "Clear search results",
                    ":/icons/clear.png",
                    "Ctrl+Shift+C",
                ),
                MenuItemDefinition(
                    "search_history",
                    "Search History...",
                    "View search history",
                    ":/icons/history.png",
                    "Ctrl+H",
                ),
            ],
        )

        # Tools menu
        tools_menu = MenuDefinition(
            "tools",
            "Tools",
            [
                MenuItemDefinition(
                    "analyze_folder",
                    "Analyze Folder Size...",
                    "Analyze folder size distribution",
                    ":/icons/analyze.png",
                ),
                MenuItemDefinition(
                    "find_duplicates",
                    "Find Duplicate Files...",
                    "Find duplicate files",
                    ":/icons/duplicates.png",
                ),
                MenuItemDefinition(
                    "cleanup_empty",
                    "Clean Up Empty Folders...",
                    "Remove empty folders",
                    ":/icons/cleanup.png",
                ),
                MenuItemDefinition("separator1", "", separator_after=True),
                MenuItemDefinition(
                    "backup_config",
                    "Backup Configuration...",
                    "Create backup of current configuration",
                    ":/icons/backup.png",
                ),
                MenuItemDefinition(
                    "restore_config",
                    "Restore Configuration...",
                    "Restore configuration from backup",
                    ":/icons/restore.png",
                ),
                MenuItemDefinition("separator2", "", separator_after=True),
                MenuItemDefinition(
                    "validate_folders",
                    "Validate Folder Configurations",
                    "Validate all folder configurations",
                    ":/icons/validate.png",
                ),
                MenuItemDefinition(
                    "repair_database",
                    "Repair Database...",
                    "Repair application database",
                    ":/icons/repair.png",
                ),
                MenuItemDefinition("separator3", "", separator_after=True),
                MenuItemDefinition(
                    "customize_toolbar",
                    "Customize Toolbar...",
                    "Customize toolbar layout",
                    ":/icons/customize.png",
                ),
                MenuItemDefinition(
                    "customize_menus",
                    "Customize Menus...",
                    "Customize menu layout",
                    ":/icons/customize_menu.png",
                ),
            ],
        )

        # Help menu
        help_menu = MenuDefinition(
            "help",
            "Help",
            [
                MenuItemDefinition(
                    "help_contents",
                    "Help Contents",
                    "Show help documentation",
                    ":/icons/help.png",
                    "F1",
                ),
                MenuItemDefinition(
                    "keyboard_shortcuts",
                    "Keyboard Shortcuts",
                    "Show keyboard shortcuts reference",
                    ":/icons/keyboard.png",
                    "Ctrl+?",
                ),
                MenuItemDefinition(
                    "tips_tricks",
                    "Tips & Tricks",
                    "Show tips and tricks",
                    ":/icons/tips.png",
                ),
                MenuItemDefinition("separator1", "", separator_after=True),
                MenuItemDefinition(
                    "check_updates",
                    "Check for Updates...",
                    "Check for application updates",
                    ":/icons/update.png",
                ),
                MenuItemDefinition(
                    "report_bug",
                    "Report Bug...",
                    "Report a bug or issue",
                    ":/icons/bug.png",
                ),
                MenuItemDefinition(
                    "send_feedback",
                    "Send Feedback...",
                    "Send feedback to developers",
                    ":/icons/feedback.png",
                ),
                MenuItemDefinition("separator2", "", separator_after=True),
                MenuItemDefinition(
                    "about",
                    "About Advanced Folders...",
                    "Show about dialog",
                    ":/icons/about.png",
                ),
            ],
        )

        # Register all menus
        for menu_def in [
            file_menu,
            edit_menu,
            view_menu,
            search_menu,
            tools_menu,
            help_menu,
        ]:
            self.register_menu(menu_def)

    def register_menu(self, menu_def: MenuDefinition):
        """Register a menu definition.

        Args:
            menu_def: Menu definition to register
        """
        self.menu_definitions[menu_def.menu_id] = menu_def

        # Register all menu items
        self._register_menu_items(menu_def.items)

        self.logger.debug(f"Registered menu: {menu_def.menu_id}")

    def _register_menu_items(self, items: List[MenuItemDefinition]):
        """Register menu items recursively.

        Args:
            items: List of menu item definitions
        """
        for item in items:
            if item.item_id and not item.item_id.startswith("separator"):
                self.menu_items[item.item_id] = item

            # Register submenu items
            if item.submenu_items:
                self._register_menu_items(item.submenu_items)

    def create_menu_bar(self, parent_widget: QWidget) -> QMenuBar:
        """Create the main menu bar.

        Args:
            parent_widget: Parent widget for menu bar

        Returns:
            Created menu bar
        """
        if self.menu_bar:
            return self.menu_bar

        self.menu_bar = QMenuBar(parent_widget)
        self.menu_bar.setObjectName("AdvancedFoldersMenuBar")

        # Sort menus by position
        sorted_menus = sorted(self.menu_definitions.values(), key=lambda m: m.position)

        # Create menus
        for menu_def in sorted_menus:
            if menu_def.visible:
                menu = self._create_menu(menu_def)
                self.menu_bar.addMenu(menu)

        # Apply styling
        self._apply_menu_styling(self.menu_bar)

        self.logger.info("Menu bar created")
        return self.menu_bar

    def _create_menu(self, menu_def: MenuDefinition) -> QMenu:
        """Create a menu from definition.

        Args:
            menu_def: Menu definition

        Returns:
            Created menu
        """
        menu = QMenu(menu_def.title, self.parent_widget)
        menu.setObjectName(f"menu_{menu_def.menu_id}")

        # Build menu items
        self._build_menu_items(menu, menu_def.items)

        return menu

    def _build_menu_items(self, menu: QMenu, items: List[MenuItemDefinition]):
        """Build menu items in a menu.

        Args:
            menu: Menu to populate
            items: List of item definitions
        """
        for item in items:
            if item.item_id.startswith("separator"):
                menu.addSeparator()
            elif item.submenu_items:
                # Create submenu
                submenu = menu.addMenu(item.title)
                if item.icon_path:
                    icon = self._load_icon(item.icon_path)
                    submenu.setIcon(icon)

                self._build_menu_items(submenu, item.submenu_items)
            else:
                # Create regular action
                action = self._create_menu_action(item)
                menu.addAction(action)

            if item.separator_after:
                menu.addSeparator()

    def _create_menu_action(self, item: MenuItemDefinition) -> QAction:
        """Create menu action from item definition.

        Args:
            item: Menu item definition

        Returns:
            Created action
        """
        action = QAction(item.title, self.parent_widget)
        action.setObjectName(f"action_{item.item_id}")

        if item.tooltip:
            action.setToolTip(item.tooltip)
            action.setStatusTip(item.tooltip)

        action.setEnabled(item.enabled)
        action.setCheckable(item.checkable)
        action.setChecked(item.checked)

        # Set icon
        if item.icon_path:
            icon = self._load_icon(item.icon_path)
            action.setIcon(icon)

        # Set shortcut
        if item.shortcut:
            action.setShortcut(QKeySequence(item.shortcut))

        # Connect callback
        if item.callback:
            action.triggered.connect(item.callback)
        else:
            action.triggered.connect(
                lambda checked, item_id=item.item_id: self.menuItemTriggered.emit(
                    item_id, checked
                )
            )

        return action

    def _load_icon(self, icon_path: str) -> QIcon:
        """Load icon with fallback.

        Args:
            icon_path: Path to icon file

        Returns:
            Loaded icon or default icon
        """
        icon = QIcon(icon_path)

        # If icon is null, create a simple fallback
        if icon.isNull():
            pixmap = QPixmap(16, 16)
            pixmap.fill(Qt.gray)
            icon = QIcon(pixmap)

        return icon

    def _apply_menu_styling(self, menu_bar: QMenuBar):
        """Apply enterprise styling to menu bar.

        Args:
            menu_bar: Menu bar to style
        """
        menu_bar.setStyleSheet(
            f"""
            QMenuBar {{
                background-color: {token('dialog_background')};
                border-bottom: 1px solid {token('border_light')};
                padding: 2px 4px;
                font-size: 14px;
            }}
            
            QMenuBar::item {{
                background-color: transparent;
                padding: 6px 12px;
                margin: 2px;
                border-radius: 4px;
            }}
            
            QMenuBar::item:selected {{
                background-color: {token('border_light')};
            }}
            
            QMenuBar::item:pressed {{
                background-color: {token('border_light')};
            }}
            
            QMenu {{
                background-color: white;
                border: 1px solid {token('border_light')};
                border-radius: 6px;
                padding: 4px 0px;
            }}
            
            QMenu::item {{
                padding: 6px 24px 6px 32px;
                margin: 0px 4px;
                border-radius: 4px;
            }}
            
            QMenu::item:selected {{
                background-color: {token('dialog_background')};
                color: {token('text_primary')};
            }}
            
            QMenu::item:disabled {{
                color: {token('text_muted')};
            }}
            
            QMenu::separator {{
                height: 1px;
                background-color: {token('border_light')};
                margin: 4px 8px;
            }}
            
            QMenu::indicator {{
                width: 16px;
                height: 16px;
                left: 8px;
            }}
            
            QMenu::indicator:checked {{
                image: url(:/icons/check.png);
            }}
            
            QMenu::right-arrow {{
                image: url(:/icons/arrow_right.png);
                width: 12px;
                height: 12px;
            }}
        """
        )

    def create_context_menu(
        self, context_id: str, items: List[MenuItemDefinition]
    ) -> QMenu:
        """Create a context menu.

        Args:
            context_id: Context menu identifier
            items: List of menu items

        Returns:
            Created context menu
        """
        menu = QMenu(self.parent_widget)
        menu.setObjectName(f"context_menu_{context_id}")

        self._build_menu_items(menu, items)

        # Apply context menu styling
        menu.setStyleSheet(self.menu_bar.styleSheet() if self.menu_bar else "")

        self.context_menus[context_id] = menu

        self.logger.debug(f"Created context menu: {context_id}")
        return menu

    def show_context_menu(self, context_id: str, position):
        """Show a context menu at position.

        Args:
            context_id: Context menu identifier
            position: Position to show menu
        """
        if context_id in self.context_menus:
            menu = self.context_menus[context_id]
            menu.exec_(position)

            self.contextMenuRequested.emit(context_id, position)

    def enable_menu_item(self, item_id: str, enabled: bool = True):
        """Enable or disable a menu item.

        Args:
            item_id: Menu item identifier
            enabled: Enabled state
        """
        if item_id in self.menu_items:
            item = self.menu_items[item_id]
            item.enabled = enabled

            # Update actual action if menu bar exists
            if self.menu_bar:
                action = self.menu_bar.findChild(QAction, f"action_{item_id}")
                if action:
                    action.setEnabled(enabled)

    def set_menu_item_checked(self, item_id: str, checked: bool):
        """Set menu item checked state.

        Args:
            item_id: Menu item identifier
            checked: Checked state
        """
        if item_id in self.menu_items:
            item = self.menu_items[item_id]
            if item.checkable:
                item.checked = checked

                # Update actual action if menu bar exists
                if self.menu_bar:
                    action = self.menu_bar.findChild(QAction, f"action_{item_id}")
                    if action:
                        action.setChecked(checked)

    def trigger_menu_item(self, item_id: str):
        """Programmatically trigger a menu item.

        Args:
            item_id: Menu item identifier
        """
        if self.menu_bar:
            action = self.menu_bar.findChild(QAction, f"action_{item_id}")
            if action:
                action.trigger()
        elif item_id in self.menu_items:
            item = self.menu_items[item_id]
            if item.callback:
                item.callback()
            else:
                self.menuItemTriggered.emit(item_id, None)

    def get_menu_shortcuts(self) -> Dict[str, str]:
        """Get all menu keyboard shortcuts.

        Returns:
            Dictionary mapping item IDs to shortcuts
        """
        shortcuts = {}
        for item_id, item in self.menu_items.items():
            if item.shortcut:
                shortcuts[item_id] = item.shortcut

        return shortcuts

    def set_menu_visible(self, visible: bool):
        """Set menu bar visibility.

        Args:
            visible: Visibility state
        """
        self.menu_visible = visible

        if self.menu_bar:
            self.menu_bar.setVisible(visible)

    def save_menu_config(self):
        """Save current menu configuration."""
        settings = QSettings("RFU", "AdvancedFolders")

        # Save menu visibility
        settings.setValue("menu/visible", self.menu_visible)

        # Save menu item states
        for item_id, item in self.menu_items.items():
            settings.setValue(f"menu/item_{item_id}_enabled", item.enabled)
            if item.checkable:
                settings.setValue(f"menu/item_{item_id}_checked", item.checked)

        self.logger.debug("Menu configuration saved")

    def load_menu_config(self):
        """Load menu configuration from settings."""
        settings = QSettings("RFU", "AdvancedFolders")

        # Load menu visibility
        self.menu_visible = settings.value("menu/visible", True, type=bool)

        # Load menu item states
        for item_id, item in self.menu_items.items():
            enabled = settings.value(
                f"menu/item_{item_id}_enabled", item.enabled, type=bool
            )
            item.enabled = enabled

            if item.checkable:
                checked = settings.value(
                    f"menu/item_{item_id}_checked", item.checked, type=bool
                )
                item.checked = checked

        self.logger.debug("Menu configuration loaded")

    def cleanup(self):
        """Clean up menu resources."""
        # Save configuration
        self.save_menu_config()

        # Clear context menus
        for menu in self.context_menus.values():
            menu.setParent(None)
        self.context_menus.clear()

        # Clear menu bar
        if self.menu_bar:
            self.menu_bar.setParent(None)
            self.menu_bar = None

        self.logger.info("Menu manager cleaned up")
