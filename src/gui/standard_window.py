"""Standardized base window class for all GUI utilities."""

import logging
import os
from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QAction,
    QDialog,
    QFileDialog,
    QGroupBox,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QStatusBar,
    QWidget,
)

from gui.menu_manager import MenuManager
from gui.themes import Colors, Dimensions, ThemeManager

try:  # pragma: no cover - fallback for standalone execution
    from src.core.tool_interface_validator import (  # type: ignore
        ToolInterfaceError,
        validate_tool_class,
    )
except ImportError:  # pragma: no cover - optional fallback path
    try:
        from core.tool_interface_validator import (  # type: ignore
            ToolInterfaceError,
            validate_tool_class,
        )
    except ImportError:  # pragma: no cover - validation unavailable
        ToolInterfaceError = None  # type: ignore
        validate_tool_class = None  # type: ignore


class StandardWindow(QMainWindow):
    """Standardized main window for utilities."""

    def __init__(
        self,
        title="Richard's File Utilities",
        icon_path=None,
        enable_menu=True,
        window_type="utility",
    ):
        super().__init__()
        self.title = title
        self.icon_path = icon_path or self._get_default_icon()
        self.enable_menu = enable_menu
        self.window_type = window_type

        # Initialize menu manager
        if self.enable_menu:
            self.menu_manager = MenuManager(self)

        self._validate_tool_interface_contract()

        self._setup_window()
        self._create_central_widget()

        # Create menu bar if enabled
        if self.enable_menu:
            self._create_menu_bar()

        self._create_status_bar()
        self._apply_theme()
        if self.enable_menu:
            self.ensure_exit_action_reference()

    def _validate_tool_interface_contract(self) -> None:
        """Validate required interface attributes before setup."""

        if validate_tool_class is None:
            return

        try:
            validate_tool_class(self.__class__)
        except ToolInterfaceError as exc:
            logging.getLogger(__name__).error("Tool validation failed: %s", exc)
            raise

    def _setup_window(self):
        """Setup basic window properties."""
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon(self.icon_path))

        if hasattr(Dimensions, "UTILITY_WINDOW_MIN_WIDTH"):
            min_width = Dimensions.UTILITY_WINDOW_MIN_WIDTH
            min_height = Dimensions.UTILITY_WINDOW_MIN_HEIGHT
        else:
            min_width = 600
            min_height = 500

        self.setMinimumSize(min_width, min_height)
        self.resize(min_width + 200, min_height + 150)

    def _create_menu_bar(self):
        """Create the standardized menu bar."""
        if hasattr(self, "menu_manager"):
            self.menu_manager.create_standard_menubar(self.window_type)

            # Register common callbacks
            self.menu_manager.register_callback(
                "show_preferences", self.show_preferences
            )
            self.menu_manager.register_callback("show_options", self.show_options)
            self.menu_manager.register_callback("refresh", self.refresh_view)

            # Register file operations if implemented
            if hasattr(self, "save_data"):
                self.menu_manager.register_callback("save_file", self.save_data)
            if hasattr(self, "load_data"):
                self.menu_manager.register_callback("open_file", self.load_data)
            if hasattr(self, "export_data"):
                self.menu_manager.register_callback("export_data", self.export_data)
            if hasattr(self, "import_data"):
                self.menu_manager.register_callback("import_data", self.import_data)

    def show_preferences(self):
        """Show preferences dialog - can be overridden by subclasses."""
        QMessageBox.information(
            self,
            "Preferences",
            "Preferences dialog not implemented for this tool.",
        )

    def show_options(self):
        """Show options dialog - can be overridden by subclasses."""
        QMessageBox.information(
            self, "Options", "Options dialog not implemented for this tool."
        )

    def refresh_view(self):
        """Refresh the current view - can be overridden by subclasses."""
        status_bar = self.statusBar() if hasattr(self, "statusBar") else None
        if status_bar is not None:
            status_bar.showMessage("Refreshed", 2000)

    def _create_central_widget(self):
        """Create central widget with standard layout."""
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = ThemeManager.create_standard_layout(self.central_widget)
        self.central_widget.setLayout(self.main_layout)

    def ensure_menu_bar(self):
        """Ensure menu bar exists - fallback method for tools."""
        menubar = self.menuBar() if hasattr(self, "menuBar") else None
        if menubar is None or not menubar.actions():
            # Menu bar doesn't exist or is empty, create it
            if not hasattr(self, "menu_manager"):
                self.menu_manager = MenuManager(self)
            self.menu_manager.create_standard_menubar(self.window_type)

            # Register standard callbacks
            self.menu_manager.register_callback(
                "show_preferences", self.show_preferences
            )
            self.menu_manager.register_callback("show_options", self.show_options)
            self.menu_manager.register_callback("refresh", self.refresh_view)

    def _create_status_bar(self):
        """Create standard status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def _apply_theme(self):
        """Apply standard theme to the window."""
        ThemeManager.apply_utility_window_theme(self)

    def _get_default_icon(self):
        """Get default application icon."""
        return os.path.join(os.path.dirname(__file__), "..", "icons", "app_icon.png")

    def create_header(self, text):
        """Create a standard header label."""
        header = QLabel(text)
        ThemeManager.style_label(header, is_header=True)
        header.setAlignment(Qt.AlignCenter)
        return header

    def create_button(self, text, callback=None, primary=True):
        """Create a standard button."""
        button = QPushButton(text)
        if primary:
            ThemeManager.style_primary_button(button)
        else:
            ThemeManager.style_secondary_button(button)

        if callback:
            button.clicked.connect(callback)

        return button

    def create_group_box(self, title):
        """Create a standard group box."""
        group_box = QGroupBox(title)
        ThemeManager.style_group_box(group_box)
        return group_box

    def create_progress_bar(self):
        """Create a standard progress bar."""
        progress = QProgressBar()
        ThemeManager.style_progress_bar(progress)
        return progress

    def show_status_message(self, message, timeout=3000):
        """Show status message with optional timeout."""
        self.status_bar.showMessage(message, timeout)

    # ------------------------------------------------------------------
    #  Exit action helpers
    # ------------------------------------------------------------------
    def ensure_exit_action_reference(self) -> Optional[QAction]:
        """Expose both legacy (actionexit) and modern (actionExit) handles."""
        menubar = self.menuBar() if hasattr(self, "menuBar") else None
        if not menubar:
            return None

        exit_action = getattr(self, "actionExit", None)
        if exit_action is None:
            exit_action = self.findChild(QAction, "actionExit")
        if exit_action is None:
            exit_action = self.findChild(QAction, "actionexit")
        if exit_action is None:
            exit_action = self._find_exit_action_by_text(menubar)

        if exit_action is None:
            file_menu = self._resolve_file_menu(menubar)
            if file_menu is None:
                return None

            exit_action = QAction("E&xit", self)
            exit_action.setObjectName("actionExit")
            exit_action.setShortcut("Ctrl+Q")
            exit_action.setStatusTip("Exit the tool")
            exit_action.triggered.connect(self._handle_exit_trigger)
            file_menu.addAction(exit_action)

        if exit_action and not hasattr(self, "actionExit"):
            setattr(self, "actionExit", exit_action)
        if exit_action and not hasattr(self, "actionexit"):
            setattr(self, "actionexit", exit_action)

        return exit_action

    def _find_exit_action_by_text(self, menubar) -> Optional[QAction]:
        for top_action in menubar.actions():
            menu = top_action.menu()
            if menu is None:
                continue
            for action in menu.actions():
                if action.isSeparator():
                    continue
                normalized = self._normalize_action_text(action.text())
                if normalized in {"exit", "quit"}:
                    return action
        return None

    def _resolve_file_menu(self, menubar):
        for top_action in menubar.actions():
            menu = top_action.menu()
            if menu is None:
                continue
            label = self._normalize_action_text(top_action.text())
            if label in {"file", "exit"}:
                return menu
        return menubar.addMenu("&File")

    @staticmethod
    def _normalize_action_text(label: str) -> str:
        return (label or "").replace("&", "").strip().lower()

    def _handle_exit_trigger(self) -> None:
        """Close the window in response to an exit action."""
        self.close()

    def show_error_dialog(self, title, message):
        """Show error dialog with standard styling."""
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

    def show_info_dialog(self, title, message):
        """Show info dialog with standard styling."""
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

    def show_warning_dialog(self, title, message):
        """Show warning dialog with standard styling."""
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

    def get_file_path(self, title="Select File", file_filter="All Files (*)"):
        """Show file selection dialog with standard styling."""
        return QFileDialog.getOpenFileName(self, title, "", file_filter)[0]

    def get_directory_path(self, title="Select Directory"):
        """Show directory selection dialog with standard styling."""
        return QFileDialog.getExistingDirectory(self, title)

    def get_save_file_path(self, title="Save File", file_filter="All Files (*)"):
        """Show save file dialog with standard styling."""
        return QFileDialog.getSaveFileName(self, title, "", file_filter)[0]


class StandardDialog(QDialog):
    """Standardized dialog for utilities."""

    def __init__(self, title="Dialog", parent=None):
        super().__init__(parent)
        self.title = title

        self._setup_dialog()
        self._create_layout()
        self._apply_theme()

    def _setup_dialog(self):
        """Setup basic dialog properties."""
        self.setWindowTitle(self.title)
        self.setModal(True)
        self.setMinimumSize(Dimensions.DIALOG_WIDTH, Dimensions.DIALOG_HEIGHT)

    def _create_layout(self):
        """Create standard dialog layout."""
        self.main_layout = ThemeManager.create_standard_layout(self)
        self.setLayout(self.main_layout)

    def _apply_theme(self):
        """Apply standard theme to the dialog."""
        ThemeManager.apply_utility_window_theme(self)

    def create_header(self, text):
        """Create a standard header label."""
        header = QLabel(text)
        ThemeManager.style_label(header, is_header=True)
        header.setAlignment(Qt.AlignCenter)
        return header

    def create_button(self, text, callback=None, primary=True):
        """Create a standard button."""
        button = QPushButton(text)
        if primary:
            ThemeManager.style_primary_button(button)
        else:
            ThemeManager.style_secondary_button(button)

        if callback:
            button.clicked.connect(callback)

        return button

    def create_group_box(self, title):
        """Create a standard group box."""
        group_box = QGroupBox(title)
        ThemeManager.style_group_box(group_box)
        return group_box

    def show_error_dialog(self, title, message):
        """Show error dialog."""
        QMessageBox.critical(self, title, message)

    def show_info_dialog(self, title, message):
        """Show info dialog."""
        QMessageBox.information(self, title, message)


class StandardUtilityWidget(QWidget):
    """Standardized widget for embedding in other windows."""

    def __init__(self, title="Utility", parent=None):
        super().__init__(parent)
        self.title = title

        self._create_layout()
        self._apply_theme()

    def _create_layout(self):
        """Create standard widget layout."""
        self.main_layout = ThemeManager.create_standard_layout(self)
        self.setLayout(self.main_layout)

    def _apply_theme(self):
        """Apply standard theme to the widget."""
        window_bg = getattr(Colors, "WINDOW_BACKGROUND", "#2b2b2b")
        text_primary = getattr(Colors, "TEXT_PRIMARY", "#f0f0f0")
        self.setStyleSheet(
            f"""
            QWidget {{
                background-color: {window_bg};
                color: {text_primary};
            }}
        """
        )

    def create_header(self, text):
        """Create a standard header label."""
        header = QLabel(text)
        ThemeManager.style_label(header, is_header=True)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return header

    def create_button(self, text, callback=None, primary=True):
        """Create a standard button."""
        button = QPushButton(text)
        if primary:
            ThemeManager.style_primary_button(button)
        else:
            ThemeManager.style_secondary_button(button)

        if callback:
            button.clicked.connect(callback)

        return button
