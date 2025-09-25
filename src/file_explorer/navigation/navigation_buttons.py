"""
Navigation Buttons Component for RFU Multi-Pane File Explorer

This module provides back/forward/up navigation buttons with state management
and history integration.

Author: Richard Noragon
Version: 2.0.0
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from PyQt5.QtCore import QObject, Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QButtonGroup,
    QHBoxLayout,
    QMenu,
    QToolButton,
    QToolTip,
    QWidget,
)


@dataclass
class NavigationState:
    """Represents navigation button states."""

    can_go_back: bool = False
    can_go_forward: bool = False
    can_go_up: bool = False
    current_path: str = ""

    def __post_init__(self):
        """Post-initialization validation."""
        if self.current_path:
            self.can_go_up = bool(
                Path(self.current_path).parent != Path(self.current_path)
            )


class NavigationButtonGroup(QObject):
    """
    Group of navigation buttons with coordinated state management.

    Provides back, forward, up, home, and refresh navigation buttons
    with intelligent state management and keyboard shortcuts.
    """

    # Signals
    back_requested = pyqtSignal()
    forward_requested = pyqtSignal()
    up_requested = pyqtSignal()
    home_requested = pyqtSignal()
    refresh_requested = pyqtSignal()
    navigate_to_path = pyqtSignal(str)  # path
    button_state_changed = pyqtSignal(str, bool)  # button_name, enabled

    def __init__(self, parent=None):
        """Initialize navigation button group."""
        super().__init__(parent)

        # State tracking
        self.current_state = NavigationState()
        self.home_path: Optional[str] = None
        self.button_widgets: Dict[str, QToolButton] = {}

        # Tooltip management
        self.tooltip_timer = QTimer()
        self.tooltip_timer.setSingleShot(True)
        self.tooltip_timer.timeout.connect(self._update_tooltips)

        # Setup logging
        self.logger = logging.getLogger("RFU.NavigationButtonGroup")

        self.logger.debug("NavigationButtonGroup initialized")

    def create_button_widget(self, parent_widget: QWidget) -> QWidget:
        """
        Create the navigation button widget.

        Args:
            parent_widget: Parent widget for the buttons

        Returns:
            QWidget containing all navigation buttons
        """
        container = QWidget(parent_widget)
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(1)

        # Create buttons
        self._create_back_button(container, layout)
        self._create_forward_button(container, layout)
        self._create_up_button(container, layout)
        self._create_separator(layout)
        self._create_home_button(container, layout)
        self._create_refresh_button(container, layout)

        # Initial state update
        self.update_button_states(self.current_state)

        return container

    def _create_back_button(
        self, parent: QWidget, layout: QHBoxLayout
    ) -> None:
        """Create the back navigation button."""
        button = QToolButton(parent)
        button.setText("◀")
        button.setToolTip("Go back to previous location (Alt+Left)")
        button.setEnabled(False)
        button.setAutoRaise(True)
        button.clicked.connect(self.back_requested.emit)

        # Keyboard shortcut
        back_action = QAction("Go Back", parent)
        back_action.setShortcut(QKeySequence("Alt+Left"))
        back_action.triggered.connect(self.back_requested.emit)
        parent.addAction(back_action)

        # Context menu
        self._setup_back_button_menu(button)

        self.button_widgets["back"] = button
        layout.addWidget(button)

    def _create_forward_button(
        self, parent: QWidget, layout: QHBoxLayout
    ) -> None:
        """Create the forward navigation button."""
        button = QToolButton(parent)
        button.setText("▶")
        button.setToolTip("Go forward to next location (Alt+Right)")
        button.setEnabled(False)
        button.setAutoRaise(True)
        button.clicked.connect(self.forward_requested.emit)

        # Keyboard shortcut
        forward_action = QAction("Go Forward", parent)
        forward_action.setShortcut(QKeySequence("Alt+Right"))
        forward_action.triggered.connect(self.forward_requested.emit)
        parent.addAction(forward_action)

        # Context menu
        self._setup_forward_button_menu(button)

        self.button_widgets["forward"] = button
        layout.addWidget(button)

    def _create_up_button(self, parent: QWidget, layout: QHBoxLayout) -> None:
        """Create the up navigation button."""
        button = QToolButton(parent)
        button.setText("⬆")
        button.setToolTip("Go to parent directory (Alt+Up)")
        button.setEnabled(False)
        button.setAutoRaise(True)
        button.clicked.connect(self.up_requested.emit)

        # Keyboard shortcut
        up_action = QAction("Go Up", parent)
        up_action.setShortcut(QKeySequence("Alt+Up"))
        up_action.triggered.connect(self.up_requested.emit)
        parent.addAction(up_action)

        # Context menu
        self._setup_up_button_menu(button)

        self.button_widgets["up"] = button
        layout.addWidget(button)

    def _create_separator(self, layout: QHBoxLayout) -> None:
        """Create visual separator between button groups."""
        separator = QWidget()
        separator.setFixedWidth(8)
        layout.addWidget(separator)

    def _create_home_button(
        self, parent: QWidget, layout: QHBoxLayout
    ) -> None:
        """Create the home navigation button."""
        button = QToolButton(parent)
        button.setText("🏠")
        button.setToolTip("Go to home directory (Alt+Home)")
        button.setAutoRaise(True)
        button.clicked.connect(self.home_requested.emit)

        # Keyboard shortcut
        home_action = QAction("Go Home", parent)
        home_action.setShortcut(QKeySequence("Alt+Home"))
        home_action.triggered.connect(self.home_requested.emit)
        parent.addAction(home_action)

        # Context menu
        self._setup_home_button_menu(button)

        self.button_widgets["home"] = button
        layout.addWidget(button)

    def _create_refresh_button(
        self, parent: QWidget, layout: QHBoxLayout
    ) -> None:
        """Create the refresh button."""
        button = QToolButton(parent)
        button.setText("🔄")
        button.setToolTip("Refresh current directory (F5)")
        button.setAutoRaise(True)
        button.clicked.connect(self.refresh_requested.emit)

        # Keyboard shortcut
        refresh_action = QAction("Refresh", parent)
        refresh_action.setShortcut(QKeySequence("F5"))
        refresh_action.triggered.connect(self.refresh_requested.emit)
        parent.addAction(refresh_action)

        self.button_widgets["refresh"] = button
        layout.addWidget(button)

    def _setup_back_button_menu(self, button: QToolButton) -> None:
        """Setup context menu for back button."""
        menu = QMenu(button)

        # Recent back locations (would be populated by history manager)
        recent_action = QAction("Recent Locations", menu)
        recent_action.setEnabled(False)
        menu.addAction(recent_action)

        menu.addSeparator()

        # Clear back history
        clear_action = QAction("Clear Back History", menu)
        clear_action.triggered.connect(lambda: self._clear_history("back"))
        menu.addAction(clear_action)

        button.setContextMenuPolicy(Qt.CustomContextMenu)
        button.customContextMenuRequested.connect(
            lambda pos: menu.exec_(button.mapToGlobal(pos))
        )

    def _setup_forward_button_menu(self, button: QToolButton) -> None:
        """Setup context menu for forward button."""
        menu = QMenu(button)

        # Recent forward locations
        recent_action = QAction("Recent Locations", menu)
        recent_action.setEnabled(False)
        menu.addAction(recent_action)

        menu.addSeparator()

        # Clear forward history
        clear_action = QAction("Clear Forward History", menu)
        clear_action.triggered.connect(lambda: self._clear_history("forward"))
        menu.addAction(clear_action)

        button.setContextMenuPolicy(Qt.CustomContextMenu)
        button.customContextMenuRequested.connect(
            lambda pos: menu.exec_(button.mapToGlobal(pos))
        )

    def _setup_up_button_menu(self, button: QToolButton) -> None:
        """Setup context menu for up button."""
        menu = QMenu(button)

        # Show parent directories hierarchy
        hierarchy_action = QAction("Directory Hierarchy", menu)
        hierarchy_action.setEnabled(False)
        menu.addAction(hierarchy_action)

        # Populate with parent directories
        if self.current_state.current_path:
            self._populate_hierarchy_menu(menu)

        button.setContextMenuPolicy(Qt.CustomContextMenu)
        button.customContextMenuRequested.connect(
            lambda pos: menu.exec_(button.mapToGlobal(pos))
        )

    def _setup_home_button_menu(self, button: QToolButton) -> None:
        """Setup context menu for home button."""
        menu = QMenu(button)

        # Set home directory
        set_home_action = QAction("Set as Home Directory", menu)
        set_home_action.triggered.connect(self._set_current_as_home)
        menu.addAction(set_home_action)

        # Common directories
        menu.addSeparator()

        # User home
        user_home_action = QAction("User Home", menu)
        user_home_action.triggered.connect(
            lambda: self._navigate_to_special_dir("home")
        )
        menu.addAction(user_home_action)

        # Desktop
        desktop_action = QAction("Desktop", menu)
        desktop_action.triggered.connect(
            lambda: self._navigate_to_special_dir("desktop")
        )
        menu.addAction(desktop_action)

        # Documents
        documents_action = QAction("Documents", menu)
        documents_action.triggered.connect(
            lambda: self._navigate_to_special_dir("documents")
        )
        menu.addAction(documents_action)

        button.setContextMenuPolicy(Qt.CustomContextMenu)
        button.customContextMenuRequested.connect(
            lambda pos: menu.exec_(button.mapToGlobal(pos))
        )

    def _populate_hierarchy_menu(self, menu: QMenu) -> None:
        """Populate menu with parent directory hierarchy."""
        if not self.current_state.current_path:
            return

        path = Path(self.current_state.current_path)
        parents = []

        # Collect parent directories
        current = path.parent
        while current != current.parent:  # Stop at root
            parents.append(current)
            current = current.parent
            if len(parents) > 10:  # Limit depth
                break

        # Add root
        if parents:
            parents.append(current)

        # Create menu items
        for parent_path in parents:
            action = QAction(str(parent_path), menu)
            action.triggered.connect(
                lambda checked, p=str(parent_path): self.navigate_to_path.emit(
                    p
                )
            )
            menu.addAction(action)

    def _clear_history(self, direction: str) -> None:
        """Clear navigation history for specified direction."""
        # This would integrate with history manager
        self.logger.info(f"Clear {direction} history requested")

    def _set_current_as_home(self) -> None:
        """Set current directory as home directory."""
        if self.current_state.current_path:
            self.home_path = self.current_state.current_path
            self.logger.info(f"Home directory set to: {self.home_path}")

    def _navigate_to_special_dir(self, dir_type: str) -> None:
        """Navigate to special directory."""
        import os
        from pathlib import Path

        special_dirs = {
            "home": Path.home(),
            "desktop": Path.home() / "Desktop",
            "documents": Path.home() / "Documents",
        }

        if dir_type in special_dirs:
            target_path = special_dirs[dir_type]
            if target_path.exists():
                self.navigate_to_path.emit(str(target_path))
            else:
                self.logger.warning(
                    f"Special directory not found: {target_path}"
                )

    def update_button_states(self, state: NavigationState) -> None:
        """
        Update button states based on navigation state.

        Args:
            state: Current navigation state
        """
        self.current_state = state

        # Update button enabled states
        buttons_state = {
            "back": state.can_go_back,
            "forward": state.can_go_forward,
            "up": state.can_go_up,
            "home": True,  # Always enabled
            "refresh": True,  # Always enabled
        }

        for button_name, enabled in buttons_state.items():
            if button_name in self.button_widgets:
                button = self.button_widgets[button_name]
                button.setEnabled(enabled)

                # Update visual style
                if enabled:
                    button.setStyleSheet("")
                else:
                    button.setStyleSheet("QToolButton { color: #cccccc; }")

                # Emit state change signal
                self.button_state_changed.emit(button_name, enabled)

        # Schedule tooltip update
        self.tooltip_timer.start(100)

        self.logger.debug(f"Button states updated: {buttons_state}")

    def _update_tooltips(self) -> None:
        """Update button tooltips with context information."""
        # Update back button tooltip
        if "back" in self.button_widgets:
            back_button = self.button_widgets["back"]
            if self.current_state.can_go_back:
                tooltip = "Go back to previous location (Alt+Left)"
            else:
                tooltip = "No previous location to go back to"
            back_button.setToolTip(tooltip)

        # Update forward button tooltip
        if "forward" in self.button_widgets:
            forward_button = self.button_widgets["forward"]
            if self.current_state.can_go_forward:
                tooltip = "Go forward to next location (Alt+Right)"
            else:
                tooltip = "No next location to go forward to"
            forward_button.setToolTip(tooltip)

        # Update up button tooltip
        if "up" in self.button_widgets:
            up_button = self.button_widgets["up"]
            if self.current_state.can_go_up:
                parent_path = Path(self.current_state.current_path).parent
                tooltip = f"Go to parent directory: {parent_path} (Alt+Up)"
            else:
                tooltip = "Already at root directory"
            up_button.setToolTip(tooltip)

        # Update home button tooltip
        if "home" in self.button_widgets:
            home_button = self.button_widgets["home"]
            if self.home_path:
                tooltip = f"Go to home directory: {self.home_path} (Alt+Home)"
            else:
                tooltip = "Go to home directory (Alt+Home)"
            home_button.setToolTip(tooltip)

    def set_current_path(self, path: str) -> None:
        """
        Set current path for button state calculation.

        Args:
            path: Current directory path
        """
        self.current_state.current_path = path
        self.current_state.can_go_up = bool(Path(path).parent != Path(path))

        # Update only the up button state
        if "up" in self.button_widgets:
            self.button_widgets["up"].setEnabled(self.current_state.can_go_up)

        self._update_tooltips()

    def set_home_path(self, path: str) -> None:
        """
        Set home directory path.

        Args:
            path: Home directory path
        """
        self.home_path = path
        self._update_tooltips()
        self.logger.info(f"Home path set to: {self.home_path}")

    def get_home_path(self) -> Optional[str]:
        """
        Get current home directory path.

        Returns:
            str or None: Home directory path if set
        """
        return self.home_path

    def enable_button(self, button_name: str, enabled: bool = True) -> None:
        """
        Enable or disable a specific button.

        Args:
            button_name: Name of button to control
            enabled: Whether button should be enabled
        """
        if button_name in self.button_widgets:
            self.button_widgets[button_name].setEnabled(enabled)
            self.button_state_changed.emit(button_name, enabled)
            self.logger.debug(
                f"Button {button_name} {'enabled' if enabled else 'disabled'}"
            )

    def get_button_state(self, button_name: str) -> bool:
        """
        Get enabled state of a specific button.

        Args:
            button_name: Name of button to query

        Returns:
            bool: True if button is enabled
        """
        if button_name in self.button_widgets:
            return self.button_widgets[button_name].isEnabled()
        return False

    def trigger_button(self, button_name: str) -> None:
        """
        Programmatically trigger a button action.

        Args:
            button_name: Name of button to trigger
        """
        if button_name in self.button_widgets and self.get_button_state(
            button_name
        ):
            button = self.button_widgets[button_name]
            button.click()
            self.logger.debug(
                f"Button {button_name} triggered programmatically"
            )

    def set_button_style(self, button_name: str, style: str) -> None:
        """
        Set custom style for a specific button.

        Args:
            button_name: Name of button to style
            style: CSS style string
        """
        if button_name in self.button_widgets:
            self.button_widgets[button_name].setStyleSheet(style)

    def get_all_button_states(self) -> Dict[str, bool]:
        """
        Get enabled states of all buttons.

        Returns:
            Dict mapping button names to enabled states
        """
        return {
            name: button.isEnabled()
            for name, button in self.button_widgets.items()
        }

    def reset_to_defaults(self) -> None:
        """Reset all buttons to default states."""
        default_state = NavigationState()
        self.update_button_states(default_state)
        self.home_path = None
        self.logger.debug("Navigation buttons reset to defaults")
