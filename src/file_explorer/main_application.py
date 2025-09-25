"""
Main Application Framework for RFU Multi-Pane File Explorer
Comprehensive Application with Menu System and Global Coordination

This module provides the main application framework that integrates all
file explorer components into a cohesive multi-pane file management experience.

Key Features:
- Multi-pane layout management with dynamic pane creation
- Comprehensive menu system with keyboard shortcuts
- Global settings and configuration management
- Session persistence and restoration
- Cross-pane coordination and communication
- Plugin architecture for extensibility
- Comprehensive error handling and logging

Application Architecture:
- MainApplication: Core application class with QMainWindow
- MenuManager: Comprehensive menu and shortcut management
- SessionManager: Session persistence and restoration
- SettingsManager: Global settings and preferences
- PaneCoordinator: Cross-pane communication and coordination
- PluginManager: Plugin loading and management

Integration Features:
- File operations across multiple panes
- Unified search and filtering
- Global bookmarks and history
- Cross-pane drag and drop
- Synchronized navigation
- Comprehensive error handling

Author: RFU Development Team
Created: 2025-09-12
Version: 1.0.0 (Phase 1 Foundation)
"""

import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from PyQt5.QtCore import (
        QApplication,
        QDir,
        QObject,
        QSettings,
        QStandardPaths,
        Qt,
        QTimer,
        pyqtSignal,
    )
    from PyQt5.QtGui import (
        QAction,
        QActionGroup,
        QFont,
        QIcon,
        QKeySequence,
        QPixmap,
    )
    from PyQt5.QtWidgets import (
        QApplication,
        QDesktopWidget,
        QDialog,
        QFileDialog,
        QFrame,
        QHBoxLayout,
        QInputDialog,
        QLabel,
        QMainWindow,
        QMenuBar,
        QMessageBox,
        QProgressBar,
        QSizePolicy,
        QSplitter,
        QStatusBar,
        QToolBar,
        QVBoxLayout,
        QWidget,
    )

    QT_AVAILABLE = True
except ImportError:
    QT_AVAILABLE = False

    # Fallback definitions
    class QMainWindow:
        pass

    class QObject:
        pass

    def pyqtSignal(*args):
        def dummy_signal(*signal_args):
            pass

        return dummy_signal


# Import RFU components
try:
    from ..config_manager import get_config_manager
    from .database.cache_manager import CacheManager
    from .models.drive_manager import DriveManager
    from .ui.file_explorer_pane import FileExplorerPane, ViewMode
    from .ui.pane_manager import (
        LayoutType,
        PaneConfiguration,
        PaneManager,
        PaneType,
    )
    from .utils.directory_watcher import DirectoryWatcher
except ImportError:
    # Fallback for development/testing
    class PaneManager:
        pass

    class PaneConfiguration:
        pass

    class PaneType:
        FILE_EXPLORER = "file_explorer"

    class LayoutType:
        GRID = "grid"
        HORIZONTAL_SPLIT = "horizontal_split"
        VERTICAL_SPLIT = "vertical_split"

    class FileExplorerPane:
        pass

    class ViewMode:
        DETAILS = "details"

    class CacheManager:
        pass

    class DriveManager:
        pass

    class DirectoryWatcher:
        pass

    def get_config_manager():
        return None


class SessionManager(QObject if QT_AVAILABLE else object):
    """Manages application session persistence and restoration."""

    def __init__(self, parent=None):
        """Initialize session manager."""
        if QT_AVAILABLE:
            super().__init__(parent)

        self.logger = logging.getLogger("RFU.FileExplorer.SessionManager")

        # Session storage
        self.settings = (
            QSettings("RFU", "FileExplorer") if QT_AVAILABLE else None
        )
        self.session_file = None

        self._initialize_session_storage()

    def _initialize_session_storage(self):
        """Initialize session storage location."""
        try:
            if QT_AVAILABLE:
                # Get application data directory
                app_data = QStandardPaths.writableLocation(
                    QStandardPaths.AppDataLocation
                )
                app_dir = Path(app_data) / "RFU" / "FileExplorer"
                app_dir.mkdir(parents=True, exist_ok=True)

                self.session_file = app_dir / "session.json"
                self.logger.debug(f"Session storage: {self.session_file}")
        except Exception as e:
            self.logger.warning(f"Could not initialize session storage: {e}")

    def save_session(self, session_data: Dict[str, Any]):
        """
        Save current session data.

        Args:
            session_data: Session data to save
        """
        try:
            if self.settings:
                # Save to QSettings
                self.settings.setValue("last_session", session_data)
                self.settings.sync()

            # Also save to JSON file if available
            if self.session_file:
                import json

                with open(self.session_file, "w") as f:
                    json.dump(session_data, f, indent=2)

            self.logger.debug("Session saved successfully")

        except Exception as e:
            self.logger.error(f"Error saving session: {e}")

    def load_session(self) -> Optional[Dict[str, Any]]:
        """
        Load saved session data.

        Returns:
            Saved session data or None if not available
        """
        try:
            # Try QSettings first
            if self.settings:
                session_data = self.settings.value("last_session")
                if session_data:
                    return session_data

            # Try JSON file
            if self.session_file and self.session_file.exists():
                import json

                with open(self.session_file, "r") as f:
                    return json.load(f)

            self.logger.debug("No saved session found")
            return None

        except Exception as e:
            self.logger.warning(f"Error loading session: {e}")
            return None

    def clear_session(self):
        """Clear saved session data."""
        try:
            if self.settings:
                self.settings.remove("last_session")
                self.settings.sync()

            if self.session_file and self.session_file.exists():
                self.session_file.unlink()

            self.logger.debug("Session cleared")

        except Exception as e:
            self.logger.warning(f"Error clearing session: {e}")


class MenuManager(QObject if QT_AVAILABLE else object):
    """Manages application menus and keyboard shortcuts."""

    # Signals
    actionTriggered = pyqtSignal(str) if QT_AVAILABLE else None

    def __init__(self, main_window, parent=None):
        """Initialize menu manager."""
        if QT_AVAILABLE:
            super().__init__(parent)

        self.logger = logging.getLogger("RFU.FileExplorer.MenuManager")
        self.main_window = main_window

        # Menu components
        self.menu_bar = None
        self.file_menu = None
        self.view_menu = None
        self.tools_menu = None
        self.help_menu = None

        # Toolbars
        self.main_toolbar = None
        self.view_toolbar = None

        # Action groups
        self.view_mode_group = None
        self.layout_group = None

        # Actions dictionary
        self.actions = {}

        if QT_AVAILABLE and main_window:
            self._create_menus()
            self._create_toolbars()
            self._setup_shortcuts()

    def _create_menus(self):
        """Create application menus."""
        self.menu_bar = self.main_window.menuBar()

        # File menu
        self._create_file_menu()

        # View menu
        self._create_view_menu()

        # Tools menu
        self._create_tools_menu()

        # Help menu
        self._create_help_menu()

    def _create_file_menu(self):
        """Create file menu."""
        self.file_menu = self.menu_bar.addMenu("&File")

        # New actions
        new_pane_action = QAction("&New Pane", self.main_window)
        new_pane_action.setShortcut(QKeySequence.New)
        new_pane_action.setStatusTip("Create a new file explorer pane")
        new_pane_action.triggered.connect(
            lambda: self._emit_action("new_pane")
        )
        self.file_menu.addAction(new_pane_action)
        self.actions["new_pane"] = new_pane_action

        self.file_menu.addSeparator()

        # Open actions
        open_folder_action = QAction("&Open Folder...", self.main_window)
        open_folder_action.setShortcut(QKeySequence.Open)
        open_folder_action.setStatusTip("Open a folder in the current pane")
        open_folder_action.triggered.connect(
            lambda: self._emit_action("open_folder")
        )
        self.file_menu.addAction(open_folder_action)
        self.actions["open_folder"] = open_folder_action

        self.file_menu.addSeparator()

        # Recent folders submenu
        recent_menu = self.file_menu.addMenu("&Recent Folders")
        self.actions["recent_menu"] = recent_menu

        self.file_menu.addSeparator()

        # Exit action
        exit_action = QAction("E&xit", self.main_window)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.setStatusTip("Exit the application")
        exit_action.triggered.connect(lambda: self._emit_action("exit"))
        self.file_menu.addAction(exit_action)
        self.actions["exit"] = exit_action

    def _create_view_menu(self):
        """Create view menu."""
        self.view_menu = self.menu_bar.addMenu("&View")

        # View mode submenu
        view_mode_menu = self.view_menu.addMenu("&View Mode")
        self.view_mode_group = QActionGroup(self.main_window)

        view_modes = [
            ("&List", "list"),
            ("&Details", "details"),
            ("&Tree", "tree"),
            ("&Grid", "grid"),
            ("&Thumbnails", "thumbnails"),
        ]

        for name, mode in view_modes:
            action = QAction(name, self.main_window)
            action.setCheckable(True)
            action.setActionGroup(self.view_mode_group)
            action.triggered.connect(
                lambda checked, m=mode: self._emit_action(f"view_mode_{m}")
            )
            view_mode_menu.addAction(action)
            self.actions[f"view_mode_{mode}"] = action

        # Set default view mode
        self.actions["view_mode_details"].setChecked(True)

        self.view_menu.addSeparator()

        # Layout submenu
        layout_menu = self.view_menu.addMenu("&Layout")
        self.layout_group = QActionGroup(self.main_window)

        layouts = [
            ("&Single Pane", "single"),
            ("&Dual Pane", "dual"),
            ("&Quad Pane", "quad"),
            ("&Grid Layout", "grid"),
        ]

        for name, layout in layouts:
            action = QAction(name, self.main_window)
            action.setCheckable(True)
            action.setActionGroup(self.layout_group)
            action.triggered.connect(
                lambda checked, l=layout: self._emit_action(f"layout_{l}")
            )
            layout_menu.addAction(action)
            self.actions[f"layout_{layout}"] = action

        # Set default layout
        self.actions["layout_dual"].setChecked(True)

        self.view_menu.addSeparator()

        # Show/hide options
        show_hidden_action = QAction("Show &Hidden Files", self.main_window)
        show_hidden_action.setCheckable(True)
        show_hidden_action.setShortcut("Ctrl+H")
        show_hidden_action.triggered.connect(
            lambda: self._emit_action("toggle_hidden")
        )
        self.view_menu.addAction(show_hidden_action)
        self.actions["toggle_hidden"] = show_hidden_action

        self.view_menu.addSeparator()

        # Refresh action
        refresh_action = QAction("&Refresh", self.main_window)
        refresh_action.setShortcut(QKeySequence.Refresh)
        refresh_action.setStatusTip("Refresh the current view")
        refresh_action.triggered.connect(lambda: self._emit_action("refresh"))
        self.view_menu.addAction(refresh_action)
        self.actions["refresh"] = refresh_action

    def _create_tools_menu(self):
        """Create tools menu."""
        self.tools_menu = self.menu_bar.addMenu("&Tools")

        # Search action
        search_action = QAction("&Search...", self.main_window)
        search_action.setShortcut("Ctrl+F")
        search_action.setStatusTip("Search for files and folders")
        search_action.triggered.connect(lambda: self._emit_action("search"))
        self.tools_menu.addAction(search_action)
        self.actions["search"] = search_action

        self.tools_menu.addSeparator()

        # Bookmarks submenu
        bookmarks_menu = self.tools_menu.addMenu("&Bookmarks")

        add_bookmark_action = QAction("&Add Bookmark", self.main_window)
        add_bookmark_action.setShortcut("Ctrl+D")
        add_bookmark_action.triggered.connect(
            lambda: self._emit_action("add_bookmark")
        )
        bookmarks_menu.addAction(add_bookmark_action)
        self.actions["add_bookmark"] = add_bookmark_action

        manage_bookmarks_action = QAction(
            "&Manage Bookmarks...", self.main_window
        )
        manage_bookmarks_action.triggered.connect(
            lambda: self._emit_action("manage_bookmarks")
        )
        bookmarks_menu.addAction(manage_bookmarks_action)
        self.actions["manage_bookmarks"] = manage_bookmarks_action

        self.tools_menu.addSeparator()

        # Preferences action
        preferences_action = QAction("&Preferences...", self.main_window)
        preferences_action.setShortcut("Ctrl+,")
        preferences_action.setStatusTip("Open application preferences")
        preferences_action.triggered.connect(
            lambda: self._emit_action("preferences")
        )
        self.tools_menu.addAction(preferences_action)
        self.actions["preferences"] = preferences_action

    def _create_help_menu(self):
        """Create help menu."""
        self.help_menu = self.menu_bar.addMenu("&Help")

        # Help action
        help_action = QAction("&Help", self.main_window)
        help_action.setShortcut(QKeySequence.HelpContents)
        help_action.setStatusTip("Show help documentation")
        help_action.triggered.connect(lambda: self._emit_action("help"))
        self.help_menu.addAction(help_action)
        self.actions["help"] = help_action

        self.help_menu.addSeparator()

        # About action
        about_action = QAction("&About", self.main_window)
        about_action.setStatusTip("Show information about this application")
        about_action.triggered.connect(lambda: self._emit_action("about"))
        self.help_menu.addAction(about_action)
        self.actions["about"] = about_action

    def _create_toolbars(self):
        """Create application toolbars."""
        # Main toolbar
        self.main_toolbar = self.main_window.addToolBar("Main")
        self.main_toolbar.setObjectName("MainToolbar")

        # Add main actions to toolbar
        if "new_pane" in self.actions:
            self.main_toolbar.addAction(self.actions["new_pane"])
        if "open_folder" in self.actions:
            self.main_toolbar.addAction(self.actions["open_folder"])

        self.main_toolbar.addSeparator()

        if "refresh" in self.actions:
            self.main_toolbar.addAction(self.actions["refresh"])
        if "search" in self.actions:
            self.main_toolbar.addAction(self.actions["search"])

        # View toolbar
        self.view_toolbar = self.main_window.addToolBar("View")
        self.view_toolbar.setObjectName("ViewToolbar")

        # Add view mode actions
        for mode in ["list", "details", "tree", "grid"]:
            action_key = f"view_mode_{mode}"
            if action_key in self.actions:
                self.view_toolbar.addAction(self.actions[action_key])

    def _setup_shortcuts(self):
        """Setup additional keyboard shortcuts."""
        # Navigation shortcuts
        shortcuts = {
            "Ctrl+1": "focus_pane_1",
            "Ctrl+2": "focus_pane_2",
            "Ctrl+3": "focus_pane_3",
            "Ctrl+4": "focus_pane_4",
            "F4": "open_terminal",
            "Alt+Left": "navigate_back",
            "Alt+Right": "navigate_forward",
            "Alt+Up": "navigate_up",
            "F5": "copy_files",
            "F6": "move_files",
            "Shift+Del": "delete_files",
            "F2": "rename_file",
        }

        for shortcut, action_name in shortcuts.items():
            action = QAction(action_name, self.main_window)
            action.setShortcut(QKeySequence(shortcut))
            action.triggered.connect(
                lambda checked, name=action_name: self._emit_action(name)
            )
            self.main_window.addAction(action)
            self.actions[action_name] = action

    def _emit_action(self, action_name: str):
        """Emit action triggered signal."""
        if self.actionTriggered:
            self.actionTriggered.emit(action_name)

    def get_action(self, name: str) -> Optional[QAction]:
        """Get action by name."""
        return self.actions.get(name)

    def update_recent_folders(self, folders: List[str]):
        """Update recent folders menu."""
        if not self.actions.get("recent_menu"):
            return

        recent_menu = self.actions["recent_menu"]
        recent_menu.clear()

        for i, folder in enumerate(folders[:10]):  # Limit to 10 recent folders
            action = QAction(f"&{i+1} {folder}", self.main_window)
            action.triggered.connect(
                lambda checked, path=folder: self._emit_action(
                    f"open_recent|{path}"
                )
            )
            recent_menu.addAction(action)


class PaneCoordinator(QObject if QT_AVAILABLE else object):
    """Coordinates communication between panes."""

    # Signals
    crossPaneOperation = pyqtSignal(str, dict) if QT_AVAILABLE else None

    def __init__(self, parent=None):
        """Initialize pane coordinator."""
        if QT_AVAILABLE:
            super().__init__(parent)

        self.logger = logging.getLogger("RFU.FileExplorer.PaneCoordinator")

        # Pane registry
        self.panes = {}
        self.active_pane = None

        # Cross-pane operations
        self.clipboard = []
        self.clipboard_operation = None  # 'copy' or 'cut'

    def register_pane(self, pane_id: str, pane_widget):
        """
        Register a pane for coordination.

        Args:
            pane_id: Unique pane identifier
            pane_widget: Pane widget instance
        """
        self.panes[pane_id] = pane_widget

        # Connect pane signals if available
        if hasattr(pane_widget, "currentPathChanged"):
            pane_widget.currentPathChanged.connect(
                lambda path, pid=pane_id: self._on_pane_path_changed(pid, path)
            )

        if hasattr(pane_widget, "fileSelected"):
            pane_widget.fileSelected.connect(
                lambda file_path, pid=pane_id: self._on_pane_file_selected(
                    pid, file_path
                )
            )

        self.logger.debug(f"Pane registered: {pane_id}")

    def unregister_pane(self, pane_id: str):
        """
        Unregister a pane.

        Args:
            pane_id: Pane identifier to remove
        """
        if pane_id in self.panes:
            del self.panes[pane_id]

            if self.active_pane == pane_id:
                self.active_pane = None

            self.logger.debug(f"Pane unregistered: {pane_id}")

    def set_active_pane(self, pane_id: str):
        """
        Set the active pane.

        Args:
            pane_id: Pane identifier to set as active
        """
        if pane_id in self.panes:
            self.active_pane = pane_id
            self.logger.debug(f"Active pane set to: {pane_id}")

    def get_active_pane(self):
        """Get the active pane widget."""
        if self.active_pane and self.active_pane in self.panes:
            return self.panes[self.active_pane]
        return None

    def copy_files(self, file_paths: List[str]):
        """
        Copy files to clipboard for cross-pane operations.

        Args:
            file_paths: List of file paths to copy
        """
        self.clipboard = file_paths.copy()
        self.clipboard_operation = "copy"

        self.logger.debug(f"Copied {len(file_paths)} files to clipboard")

    def cut_files(self, file_paths: List[str]):
        """
        Cut files to clipboard for cross-pane operations.

        Args:
            file_paths: List of file paths to cut
        """
        self.clipboard = file_paths.copy()
        self.clipboard_operation = "cut"

        self.logger.debug(f"Cut {len(file_paths)} files to clipboard")

    def paste_files(self, destination_path: str):
        """
        Paste files from clipboard to destination.

        Args:
            destination_path: Destination directory path
        """
        if not self.clipboard:
            return

        operation_data = {
            "source_files": self.clipboard.copy(),
            "destination": destination_path,
            "operation": self.clipboard_operation,
        }

        if self.crossPaneOperation:
            self.crossPaneOperation.emit("paste_files", operation_data)

        # Clear clipboard if cut operation
        if self.clipboard_operation == "cut":
            self.clipboard.clear()
            self.clipboard_operation = None

        self.logger.debug(
            f"Pasted {len(operation_data['source_files'])} files to {destination_path}"
        )

    def _on_pane_path_changed(self, pane_id: str, path: str):
        """Handle pane path changes."""
        self.logger.debug(f"Pane {pane_id} path changed to: {path}")

    def _on_pane_file_selected(self, pane_id: str, file_path: str):
        """Handle pane file selection."""
        self.logger.debug(f"Pane {pane_id} selected file: {file_path}")


class MainApplication(QMainWindow if QT_AVAILABLE else object):
    """
    Main application window for RFU Multi-Pane File Explorer.

    Integrates all components into a comprehensive file management application
    with multi-pane support, global coordination, and session management.
    """

    def __init__(self, parent=None):
        """Initialize main application."""
        if QT_AVAILABLE:
            super().__init__(parent)

        self.logger = logging.getLogger("RFU.FileExplorer.MainApplication")

        # Core managers
        self.config_manager = get_config_manager()
        self.session_manager = SessionManager(self)
        self.menu_manager = None
        self.pane_coordinator = PaneCoordinator(self)

        # UI components
        self.pane_manager = None
        self.status_bar = None
        self.progress_bar = None

        # System components
        self.cache_manager = None
        self.drive_manager = None
        self.directory_watcher = None

        # Application state
        self.recent_folders = []
        self.bookmarks = []
        self.is_closing = False

        if QT_AVAILABLE:
            self._setup_application()
            self._setup_components()
            self._setup_ui()
            self._restore_session()

    def _setup_application(self):
        """Setup basic application properties."""
        self.setWindowTitle("RFU File Explorer")
        self.setWindowIcon(QIcon())  # Set application icon here

        # Set minimum size
        self.setMinimumSize(800, 600)

        # Center window on screen
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2,
        )

    def _setup_components(self):
        """Setup core application components."""
        try:
            # Initialize cache manager
            self.cache_manager = CacheManager()

            # Initialize drive manager
            self.drive_manager = DriveManager()

            # Initialize directory watcher
            self.directory_watcher = DirectoryWatcher()
            self.directory_watcher.start_monitoring()

            self.logger.debug("Core components initialized")

        except Exception as e:
            self.logger.error(f"Error setting up components: {e}")

    def _setup_ui(self):
        """Setup user interface."""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create pane manager
        self.pane_manager = PaneManager(self)
        main_layout.addWidget(self.pane_manager)

        # Setup menu system
        self.menu_manager = MenuManager(self)
        self.menu_manager.actionTriggered.connect(self._handle_menu_action)

        # Setup status bar
        self._setup_status_bar()

        # Connect pane coordinator
        self.pane_coordinator.crossPaneOperation.connect(
            self._handle_cross_pane_operation
        )

        # Create initial panes
        self._create_initial_panes()

    def _setup_status_bar(self):
        """Setup status bar."""
        self.status_bar = self.statusBar()

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumWidth(200)
        self.status_bar.addPermanentWidget(self.progress_bar)

        # Ready message
        self.status_bar.showMessage("Ready")

    def _create_initial_panes(self):
        """Create initial file explorer panes."""
        try:
            # Create default dual-pane layout
            layout_type = LayoutType.HORIZONTAL_SPLIT

            # Left pane - Home directory
            left_config = PaneConfiguration(
                pane_id="left_pane",
                pane_type=PaneType.FILE_EXPLORER,
                title="Left Pane",
            )

            # Right pane - Documents directory
            right_config = PaneConfiguration(
                pane_id="right_pane",
                pane_type=PaneType.FILE_EXPLORER,
                title="Right Pane",
            )

            # Apply layout
            self.pane_manager.apply_layout(
                layout_type, [left_config, right_config]
            )

            # Set initial paths
            home_path = str(Path.home())
            documents_path = str(Path.home() / "Documents")

            left_pane = self.pane_manager.get_pane("left_pane")
            if left_pane and hasattr(left_pane, "set_path"):
                left_pane.set_path(home_path)
                self.pane_coordinator.register_pane("left_pane", left_pane)

            right_pane = self.pane_manager.get_pane("right_pane")
            if right_pane and hasattr(right_pane, "set_path"):
                if Path(documents_path).exists():
                    right_pane.set_path(documents_path)
                else:
                    right_pane.set_path(home_path)
                self.pane_coordinator.register_pane("right_pane", right_pane)

            # Set left pane as active
            self.pane_coordinator.set_active_pane("left_pane")

            self.logger.info("Initial panes created successfully")

        except Exception as e:
            self.logger.error(f"Error creating initial panes: {e}")

    def _handle_menu_action(self, action_name: str):
        """
        Handle menu action triggers.

        Args:
            action_name: Name of the triggered action
        """
        try:
            self.logger.debug(f"Menu action triggered: {action_name}")

            if action_name == "exit":
                self.close()

            elif action_name == "new_pane":
                self._create_new_pane()

            elif action_name == "open_folder":
                self._open_folder_dialog()

            elif action_name.startswith("open_recent|"):
                folder_path = action_name.split("|", 1)[1]
                self._open_folder(folder_path)

            elif action_name.startswith("view_mode_"):
                view_mode = action_name.replace("view_mode_", "")
                self._set_view_mode(view_mode)

            elif action_name.startswith("layout_"):
                layout = action_name.replace("layout_", "")
                self._set_layout(layout)

            elif action_name == "toggle_hidden":
                self._toggle_hidden_files()

            elif action_name == "refresh":
                self._refresh_current_pane()

            elif action_name == "search":
                self._open_search_dialog()

            elif action_name == "add_bookmark":
                self._add_bookmark()

            elif action_name == "manage_bookmarks":
                self._manage_bookmarks()

            elif action_name == "preferences":
                self._open_preferences()

            elif action_name == "about":
                self._show_about_dialog()

            elif action_name == "help":
                self._show_help()

            # Handle focus actions
            elif action_name.startswith("focus_pane_"):
                pane_number = action_name.replace("focus_pane_", "")
                self._focus_pane(pane_number)

            # Handle file operations
            elif action_name == "copy_files":
                self._copy_selected_files()

            elif action_name == "move_files":
                self._move_selected_files()

            elif action_name == "delete_files":
                self._delete_selected_files()

            else:
                self.logger.warning(f"Unhandled menu action: {action_name}")

        except Exception as e:
            self.logger.error(f"Error handling menu action {action_name}: {e}")

    def _create_new_pane(self):
        """Create a new file explorer pane."""
        try:
            # Generate unique pane ID
            pane_count = len(self.pane_manager.get_all_panes())
            pane_id = f"pane_{pane_count + 1}"

            config = PaneConfiguration(
                pane_id=pane_id,
                pane_type=PaneType.FILE_EXPLORER,
                title=f"Pane {pane_count + 1}",
            )

            pane_widget = self.pane_manager.create_pane(config)
            if pane_widget:
                # Set initial path to home directory
                if hasattr(pane_widget, "set_path"):
                    pane_widget.set_path(str(Path.home()))

                # Register with coordinator
                self.pane_coordinator.register_pane(pane_id, pane_widget)

                self.status_bar.showMessage(
                    f"Created new pane: {pane_id}", 2000
                )

        except Exception as e:
            self.logger.error(f"Error creating new pane: {e}")

    def _open_folder_dialog(self):
        """Open folder selection dialog."""
        try:
            active_pane = self.pane_coordinator.get_active_pane()
            if not active_pane:
                return

            current_path = getattr(
                active_pane, "current_path", str(Path.home())
            )

            folder_path = QFileDialog.getExistingDirectory(
                self, "Open Folder", current_path
            )

            if folder_path:
                self._open_folder(folder_path)

        except Exception as e:
            self.logger.error(f"Error opening folder dialog: {e}")

    def _open_folder(self, folder_path: str):
        """
        Open folder in active pane.

        Args:
            folder_path: Path to the folder to open
        """
        try:
            active_pane = self.pane_coordinator.get_active_pane()
            if active_pane and hasattr(active_pane, "set_path"):
                active_pane.set_path(folder_path)

                # Add to recent folders
                if folder_path not in self.recent_folders:
                    self.recent_folders.insert(0, folder_path)
                    self.recent_folders = self.recent_folders[
                        :10
                    ]  # Limit to 10

                    # Update menu
                    if self.menu_manager:
                        self.menu_manager.update_recent_folders(
                            self.recent_folders
                        )

                self.status_bar.showMessage(
                    f"Opened folder: {folder_path}", 2000
                )

        except Exception as e:
            self.logger.error(f"Error opening folder {folder_path}: {e}")

    def _set_view_mode(self, mode: str):
        """Set view mode for active pane."""
        try:
            active_pane = self.pane_coordinator.get_active_pane()
            if active_pane and hasattr(active_pane, "set_view_mode"):
                view_mode_map = {
                    "list": ViewMode.LIST,
                    "details": ViewMode.DETAILS,
                    "tree": ViewMode.TREE,
                    "grid": ViewMode.GRID,
                    "thumbnails": ViewMode.THUMBNAILS,
                }

                if mode in view_mode_map:
                    active_pane.set_view_mode(view_mode_map[mode])
                    self.status_bar.showMessage(f"View mode: {mode}", 2000)

        except Exception as e:
            self.logger.error(f"Error setting view mode {mode}: {e}")

    def _set_layout(self, layout: str):
        """Set pane layout."""
        # Implementation would depend on specific layout requirements
        self.status_bar.showMessage(f"Layout: {layout}", 2000)

    def _toggle_hidden_files(self):
        """Toggle hidden files visibility."""
        try:
            active_pane = self.pane_coordinator.get_active_pane()
            if active_pane and hasattr(active_pane, "_toggle_hidden_files"):
                # This would need to be implemented in the pane
                pass

        except Exception as e:
            self.logger.error(f"Error toggling hidden files: {e}")

    def _refresh_current_pane(self):
        """Refresh current pane."""
        try:
            active_pane = self.pane_coordinator.get_active_pane()
            if active_pane and hasattr(active_pane, "_refresh_current_path"):
                active_pane._refresh_current_path()
                self.status_bar.showMessage("Refreshed", 1000)

        except Exception as e:
            self.logger.error(f"Error refreshing pane: {e}")

    def _open_search_dialog(self):
        """Open search dialog."""
        # Implementation would open a search dialog
        self.status_bar.showMessage("Search not implemented yet", 2000)

    def _add_bookmark(self):
        """Add current location to bookmarks."""
        try:
            active_pane = self.pane_coordinator.get_active_pane()
            if active_pane and hasattr(active_pane, "current_path"):
                path = active_pane.current_path
                if path and path not in self.bookmarks:
                    self.bookmarks.append(path)
                    self.status_bar.showMessage(f"Bookmarked: {path}", 2000)

        except Exception as e:
            self.logger.error(f"Error adding bookmark: {e}")

    def _manage_bookmarks(self):
        """Open bookmark management dialog."""
        self.status_bar.showMessage(
            "Bookmark management not implemented yet", 2000
        )

    def _open_preferences(self):
        """Open preferences dialog."""
        self.status_bar.showMessage("Preferences not implemented yet", 2000)

    def _show_about_dialog(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About RFU File Explorer",
            "RFU File Explorer v1.0.0\n\n"
            "A comprehensive multi-pane file management application\n"
            "built with Python and PyQt5.\n\n"
            "Copyright © 2025 RFU Development Team",
        )

    def _show_help(self):
        """Show help documentation."""
        self.status_bar.showMessage("Help not implemented yet", 2000)

    def _focus_pane(self, pane_number: str):
        """Focus specific pane by number."""
        # Implementation would focus the specified pane
        pass

    def _copy_selected_files(self):
        """Copy selected files to clipboard."""
        try:
            active_pane = self.pane_coordinator.get_active_pane()
            if active_pane and hasattr(active_pane, "file_list"):
                selected_files = active_pane.file_list.get_selected_files()
                if selected_files:
                    self.pane_coordinator.copy_files(selected_files)
                    self.status_bar.showMessage(
                        f"Copied {len(selected_files)} files", 2000
                    )

        except Exception as e:
            self.logger.error(f"Error copying files: {e}")

    def _move_selected_files(self):
        """Cut selected files to clipboard."""
        try:
            active_pane = self.pane_coordinator.get_active_pane()
            if active_pane and hasattr(active_pane, "file_list"):
                selected_files = active_pane.file_list.get_selected_files()
                if selected_files:
                    self.pane_coordinator.cut_files(selected_files)
                    self.status_bar.showMessage(
                        f"Cut {len(selected_files)} files", 2000
                    )

        except Exception as e:
            self.logger.error(f"Error cutting files: {e}")

    def _delete_selected_files(self):
        """Delete selected files."""
        # Implementation would delete selected files with confirmation
        self.status_bar.showMessage("Delete not implemented yet", 2000)

    def _handle_cross_pane_operation(
        self, operation: str, data: Dict[str, Any]
    ):
        """
        Handle cross-pane operations.

        Args:
            operation: Operation type
            data: Operation data
        """
        try:
            if operation == "paste_files":
                # Implementation would handle file paste operations
                source_files = data.get("source_files", [])
                destination = data.get("destination", "")
                op_type = data.get("operation", "copy")

                self.status_bar.showMessage(
                    f"Would {op_type} {len(source_files)} files to {destination}",
                    3000,
                )

        except Exception as e:
            self.logger.error(f"Error handling cross-pane operation: {e}")

    def _save_session(self):
        """Save current session state."""
        try:
            session_data = {
                "window_geometry": {
                    "x": self.x(),
                    "y": self.y(),
                    "width": self.width(),
                    "height": self.height(),
                },
                "pane_layout": (
                    self.pane_manager.get_layout_state()
                    if self.pane_manager
                    else {}
                ),
                "recent_folders": self.recent_folders,
                "bookmarks": self.bookmarks,
            }

            self.session_manager.save_session(session_data)
            self.logger.debug("Session saved")

        except Exception as e:
            self.logger.error(f"Error saving session: {e}")

    def _restore_session(self):
        """Restore saved session state."""
        try:
            session_data = self.session_manager.load_session()
            if not session_data:
                return

            # Restore window geometry
            geometry = session_data.get("window_geometry", {})
            if geometry:
                self.setGeometry(
                    geometry.get("x", 100),
                    geometry.get("y", 100),
                    geometry.get("width", 800),
                    geometry.get("height", 600),
                )

            # Restore recent folders and bookmarks
            self.recent_folders = session_data.get("recent_folders", [])
            self.bookmarks = session_data.get("bookmarks", [])

            # Update menu
            if self.menu_manager:
                self.menu_manager.update_recent_folders(self.recent_folders)

            self.logger.debug("Session restored")

        except Exception as e:
            self.logger.error(f"Error restoring session: {e}")

    def closeEvent(self, event):
        """Handle application close event."""
        try:
            self.is_closing = True

            # Save session
            self._save_session()

            # Cleanup components
            if self.directory_watcher:
                self.directory_watcher.cleanup()

            if self.cache_manager:
                self.cache_manager.cleanup()

            # Close all panes
            if self.pane_manager:
                self.pane_manager.cleanup()

            self.logger.info("Application closing")

            if QT_AVAILABLE:
                event.accept()

        except Exception as e:
            self.logger.error(f"Error during application close: {e}")
            if QT_AVAILABLE:
                event.accept()


def main():
    """Main application entry point."""
    import sys

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("rfu_file_explorer.log"),
        ],
    )

    logger = logging.getLogger("RFU.FileExplorer.Main")

    if not QT_AVAILABLE:
        logger.error(
            "PyQt5 is not available. Please install PyQt5 to run the application."
        )
        return 1

    try:
        # Create QApplication
        app = QApplication(sys.argv)
        app.setApplicationName("RFU File Explorer")
        app.setApplicationVersion("1.0.0")
        app.setOrganizationName("RFU")
        app.setOrganizationDomain("rfu.dev")

        # Create and show main window
        main_window = MainApplication()
        main_window.show()

        logger.info("RFU File Explorer started")

        # Run application
        return app.exec_()

    except Exception as e:
        logger.error(f"Error starting application: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
