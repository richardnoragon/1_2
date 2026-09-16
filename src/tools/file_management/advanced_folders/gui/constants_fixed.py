# -*- coding: utf-8 -*-
"""
GUI Constants for Advanced Folders

This module contains all visual styling constants, color schemes,
typography definitions, and other UI constants used throughout
the Advanced Folders GUI components.

Author: RFU Development Team
Version: 1.0.0
"""
from src.rfu import font_tokens

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont


class Colors:
    """Color scheme definitions for consistent theming."""

    # Primary colors
    PRIMARY_BLUE = "#2196F3"
    PRIMARY_BLUE_HOVER = "#1976D2"
    PRIMARY_BLUE_PRESSED = "#0D47A1"

    # Secondary colors
    SECONDARY_GREY = "#607D8B"
    SECONDARY_GREY_HOVER = "#455A64"
    SECONDARY_GREY_PRESSED = "#263238"

    # Background colors
    BACKGROUND_MAIN = "#FAFAFA"
    BACKGROUND_SECONDARY = "#FFFFFF"
    BACKGROUND_PANEL = "#F5F5F5"
    BACKGROUND_HOVER = "#E3F2FD"
    BACKGROUND_SELECTED = "#BBDEFB"

    # Text colors
    TEXT_PRIMARY = "#212121"
    TEXT_SECONDARY = "#757575"
    TEXT_DISABLED = "#BDBDBD"
    TEXT_ACCENT = "#1976D2"

    # Status colors
    SUCCESS_GREEN = "#4CAF50"
    SUCCESS_GREEN_LIGHT = "#C8E6C9"
    WARNING_ORANGE = "#FF9800"
    WARNING_ORANGE_LIGHT = "#FFE0B2"
    ERROR_RED = "#F44336"
    ERROR_RED_LIGHT = "#FFCDD2"
    INFO_BLUE = "#2196F3"
    INFO_BLUE_LIGHT = "#E3F2FD"

    # Border colors
    BORDER_LIGHT = "#E0E0E0"
    BORDER_MEDIUM = "#BDBDBD"
    BORDER_DARK = "#757575"
    BORDER_ACCENT = "#2196F3"


class Fonts:
    """Typography system with consistent font definitions."""

    # Font families
    FAMILY_PRIMARY = "Segoe UI"
    FAMILY_SECONDARY = "Arial"
    FAMILY_MONOSPACE = "Consolas"

    # Font sizes (in points)
    SIZE_SMALL = 11
    SIZE_NORMAL = 14
    SIZE_MEDIUM = 14
    SIZE_LARGE = 16
    SIZE_XLARGE = 14
    SIZE_TITLE = 16
    SIZE_HEADER = 18

    # Font weights
    WEIGHT_NORMAL = QFont.Normal
    WEIGHT_BOLD = QFont.Bold

    @classmethod
    def get_font(cls, size=None, weight=None, family=None):
        """Create a QFont with specified parameters."""
        font = font_tokens.get("font.body", family=family, scale=max(1.0, (size or cls.SIZE_NORMAL) / 14))

        if weight is not None:
            font.setWeight(weight)

        return font


class Layout:
    """Layout and spacing constants for consistent positioning."""

    # Margins and padding
    MARGIN_SMALL = 4
    MARGIN_NORMAL = 8
    MARGIN_MEDIUM = 12
    MARGIN_LARGE = 16
    MARGIN_XLARGE = 24

    # Spacing between elements
    SPACING_SMALL = 4
    SPACING_NORMAL = 8
    SPACING_MEDIUM = 12
    SPACING_LARGE = 16

    # Content areas
    CONTENT_MARGIN = 16
    CONTENT_PADDING = 12
    DIALOG_MARGIN = 20

    # Widget dimensions
    BUTTON_HEIGHT = 32
    INPUT_HEIGHT = 28
    TAB_HEIGHT = 36
    HEADER_HEIGHT = 40
    STATUS_BAR_HEIGHT = 24

    # Dialog dimensions
    DIALOG_MIN_WIDTH = 600
    DIALOG_MIN_HEIGHT = 400
    DIALOG_PREFERRED_WIDTH = 800
    DIALOG_PREFERRED_HEIGHT = 600


class FileTypes:
    """File type categorizations and extensions."""

    # Document files
    DOCUMENTS = [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt"]

    # Image files
    IMAGES = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".svg"]

    # Video files
    VIDEOS = [".mp4", ".avi", ".mov", ".wmv", ".flv", ".mkv", ".webm"]

    # Audio files
    AUDIO = [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma"]

    # Archive files
    ARCHIVES = [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"]

    # Code files
    CODE = [".py", ".js", ".html", ".css", ".cpp", ".java", ".cs", ".php"]

    # Excel/Spreadsheet files
    SPREADSHEETS = [".xls", ".xlsx", ".csv", ".ods"]

    # All categories combined
    ALL_TYPES = DOCUMENTS + IMAGES + VIDEOS + AUDIO + ARCHIVES + CODE + SPREADSHEETS


class Icons:
    """Icon definitions and text representations."""

    # Action icons
    ADD = "+"
    REMOVE = "-"
    EDIT = "Edit"
    DELETE = "Delete"
    SAVE = "Save"
    CANCEL = "Cancel"

    # File operation icons
    COPY = "Copy"
    MOVE = "Move"
    SYNC = "Sync"
    SEARCH = "Search"
    REFRESH = "Refresh"
    SETTINGS = "Settings"

    # Status icons
    SUCCESS = "OK"
    ERROR = "Error"
    WARNING = "Warning"
    INFO = "Info"

    # Navigation icons
    UP = "Up"
    DOWN = "Down"
    LEFT = "Left"
    RIGHT = "Right"


class Styles:
    """CSS styling definitions for consistent appearance."""

    # Dialog styling
    DIALOG_STYLE = f"""
        QDialog {{
            background-color: {Colors.BACKGROUND_MAIN};
            color: {Colors.TEXT_PRIMARY};


        }}
    """

    # Tab widget styling
    TAB_WIDGET_STYLE = f"""
        QTabWidget::pane {{
            border: 1px solid {Colors.BORDER_LIGHT};
            background-color: {Colors.BACKGROUND_SECONDARY};
        }}

        QTabBar::tab {{
            background-color: {Colors.BACKGROUND_PANEL};
            color: {Colors.TEXT_PRIMARY};
            padding: 8px 16px;
            margin-right: 2px;
            border: 1px solid {Colors.BORDER_LIGHT};
            border-bottom: none;
        }}

        QTabBar::tab:selected {{
            background-color: {Colors.BACKGROUND_SECONDARY};
            color: {Colors.TEXT_ACCENT};
            border-bottom: 2px solid {Colors.PRIMARY_BLUE};
        }}

        QTabBar::tab:hover {{
            background-color: {Colors.BACKGROUND_HOVER};
        }}
    """

    # Button styling
    BUTTON_PRIMARY_STYLE = f"""
        QPushButton {{
            background-color: {Colors.PRIMARY_BLUE};
            color: white;
            border: none;
            padding: 8px 16px;

            font-weight: bold;
            border-radius: 4px;
        }}

        QPushButton:hover {{
            background-color: {Colors.PRIMARY_BLUE_HOVER};
        }}

        QPushButton:pressed {{
            background-color: {Colors.PRIMARY_BLUE_PRESSED};
        }}

        QPushButton:disabled {{
            background-color: {Colors.TEXT_DISABLED};
            color: {Colors.BACKGROUND_MAIN};
        }}
    """

    BUTTON_SECONDARY_STYLE = f"""
        QPushButton {{
            background-color: {Colors.BACKGROUND_SECONDARY};
            color: {Colors.TEXT_PRIMARY};
            border: 1px solid {Colors.BORDER_MEDIUM};
            padding: 8px 16px;

            border-radius: 4px;
        }}

        QPushButton:hover {{
            background-color: {Colors.BACKGROUND_HOVER};
            border-color: {Colors.BORDER_ACCENT};
        }}

        QPushButton:pressed {{
            background-color: {Colors.BACKGROUND_SELECTED};
        }}
    """

    # Input field styling
    INPUT_STYLE = f"""
        QLineEdit, QTextEdit {{
            background-color: {Colors.BACKGROUND_SECONDARY};
            color: {Colors.TEXT_PRIMARY};
            border: 1px solid {Colors.BORDER_LIGHT};
            padding: 6px;

            border-radius: 3px;
        }}

        QLineEdit:focus, QTextEdit:focus {{
            border-color: {Colors.BORDER_ACCENT};
            background-color: white;
        }}

        QLineEdit:disabled, QTextEdit:disabled {{
            background-color: {Colors.BACKGROUND_PANEL};
            color: {Colors.TEXT_DISABLED};
        }}
    """

    # Tree view styling
    TREE_VIEW_STYLE = f"""
        QTreeView {{
            background-color: {Colors.BACKGROUND_SECONDARY};
            color: {Colors.TEXT_PRIMARY};
            border: 1px solid {Colors.BORDER_LIGHT};

            selection-background-color: {Colors.BACKGROUND_SELECTED};
        }}

        QTreeView::item {{
            padding: 4px;
            border: none;
        }}

        QTreeView::item:hover {{
            background-color: {Colors.BACKGROUND_HOVER};
        }}

        QTreeView::item:selected {{
            background-color: {Colors.BACKGROUND_SELECTED};
            color: {Colors.TEXT_PRIMARY};
        }}

        QTreeView::branch:has-children:!has-siblings:closed,
        QTreeView::branch:closed:has-children:has-siblings {{
            border-image: none;
            image: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAkAAAAJCAYAAADgkQYQAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAAdgAAAHYBTnsmCAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAFXSURBVBiVY/z//z8DAwMDw38GBgYGJiYmBhaWfwwsLCwMLCwsDMxMTAwsLCwMbGxsDOzs7Ayc);
        }}

        QTreeView::branch:open:has-children:!has-siblings,
        QTreeView::branch:open:has-children:has-siblings {{
            border-image: none;
            image: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAkAAAAJCAYAAADgkQYQAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAAdgAAAHYBTnsmCAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAFXSURBVBiVY/z//z8DAwMDw38GBgYGJiYmBhaWfwwsLCwMLCwsDMxMTAwsLCwMbGxsDOzs7Ayc);
        }}
    """


class ValidationPatterns:
    """Regular expression patterns for input validation."""

    # File and directory patterns
    FILENAME_PATTERN = r'^[^<>:"/\\|?*]+$'
    DIRECTORY_PATH_PATTERN = r'^[a-zA-Z]:\\(?:[^<>:"/\\|?*]+\\)*[^<>:"/\\|?*]*$'

    # Text patterns
    NON_EMPTY_TEXT = r".+"
    ALPHANUMERIC = r"^[a-zA-Z0-9]+$"
    ALPHANUMERIC_SPACES = r"^[a-zA-Z0-9\s]+$"

    # Size patterns
    FILE_SIZE_PATTERN = r"^\d+(\.\d+)?\s*(B|KB|MB|GB|TB)$"
    NUMBER_PATTERN = r"^\d+$"
    DECIMAL_PATTERN = r"^\d+(\.\d+)?$"


class Messages:
    """User-facing message texts and templates."""

    # Success messages
    SUCCESS_SAVE = "Configuration saved successfully"
    SUCCESS_LOAD = "Configuration loaded successfully"
    SUCCESS_RESET = "Settings reset to defaults"

    # Error messages
    ERROR_SAVE = "Failed to save configuration: {error}"
    ERROR_LOAD = "Failed to load configuration: {error}"
    ERROR_INVALID_PATH = "Invalid directory path: {path}"
    ERROR_PATH_NOT_EXISTS = "Directory does not exist: {path}"
    ERROR_NO_PERMISSION = "Insufficient permissions for: {path}"

    # Warning messages
    WARNING_UNSAVED_CHANGES = "You have unsaved changes. Do you want to save them?"
    WARNING_RESET_SETTINGS = "This will reset all settings to defaults. Continue?"
    WARNING_LARGE_DIRECTORY = (
        "This directory contains many files. Processing may take time."
    )

    # Info messages
    INFO_SCANNING_DIRECTORY = "Scanning directory..."
    INFO_PROCESSING_FILES = "Processing files..."
    INFO_OPERATION_COMPLETE = "Operation completed"

    # Confirmation messages
    CONFIRM_DELETE = "Are you sure you want to delete this item?"
    CONFIRM_OVERWRITE = "File already exists. Do you want to overwrite it?"
    CONFIRM_EXIT = "Are you sure you want to exit?"


class Accessibility:
    """Accessibility and WCAG compliance constants."""

    # ARIA labels and descriptions
    ARIA_LABEL_MAIN_DIALOG = "Folder Configuration Dialog"
    ARIA_LABEL_TAB_GENERAL = "General Settings Tab"
    ARIA_LABEL_TAB_SEARCH = "Search Settings Tab"
    ARIA_LABEL_TAB_FILTERS = "Filter Settings Tab"
    ARIA_LABEL_TAB_DISPLAY = "Display Settings Tab"

    ARIA_LABEL_DIRECTORY_BROWSER = "Directory Browser"
    ARIA_LABEL_PATH_INPUT = "Directory Path Input"
    ARIA_LABEL_BROWSE_BUTTON = "Browse for Directory"

    # Keyboard shortcuts
    SHORTCUT_SAVE = "Ctrl+S"
    SHORTCUT_CANCEL = "Escape"
    SHORTCUT_HELP = "F1"
    SHORTCUT_REFRESH = "F5"

    # Focus indicators
    FOCUS_OUTLINE_COLOR = Colors.BORDER_ACCENT
    FOCUS_OUTLINE_WIDTH = "2px"
    FOCUS_OUTLINE_STYLE = "solid"


# Version and metadata
VERSION = "1.0.0"
MODULE_NAME = "Advanced Folders GUI Constants"
AUTHOR = "RFU Development Team"
