"""
GUI Theme Management for Richard's File Utilities

This module provides comprehensive theming support for all GUI components,
including colors, fonts, spacing, and styling utilities.
"""

from PyQt5.QtWidgets import (
    QWidget, QMainWindow, QDialog, QPushButton, QLabel, QLineEdit,
    QTextEdit, QListWidget, QTreeWidget, QTableWidget, QGroupBox,
    QProgressBar, QVBoxLayout, QHBoxLayout, QGridLayout, QApplication
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QColor, QPalette
from enum import Enum
from typing import Optional, Dict, Any


class ThemeType(Enum):
    """Available theme types."""
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"


class Colors:
    """Color constants for the application."""
    
    # Primary colors
    PRIMARY = QColor("#3498db")
    PRIMARY_HOVER = QColor("#2980b9")
    PRIMARY_PRESSED = QColor("#21618c")
    
    # Secondary colors
    SECONDARY = QColor("#95a5a6")
    SECONDARY_HOVER = QColor("#7f8c8d")
    
    # Status colors
    SUCCESS = QColor("#27ae60")
    SUCCESS_HOVER = QColor("#229954")
    WARNING = QColor("#f39c12")
    WARNING_HOVER = QColor("#e67e22")
    ERROR = QColor("#e74c3c")
    ERROR_HOVER = QColor("#c0392b")
    
    # Text colors
    TEXT_PRIMARY = QColor("#2c3e50")
    TEXT_SECONDARY = QColor("#7f8c8d")
    TEXT_DISABLED = QColor("#bdc3c7")
    TEXT_LIGHT = QColor("#ffffff")
    
    # Background colors
    BACKGROUND_LIGHT = QColor("#ffffff")
    BACKGROUND_DARK = QColor("#2c3e50")
    BACKGROUND_SECONDARY = QColor("#ecf0f1")
    BACKGROUND_HOVER = QColor("#f8f9fa")
    
    # Border colors
    BORDER_LIGHT = QColor("#dee2e6")
    BORDER_DARK = QColor("#495057")
    BORDER_FOCUS = QColor("#3498db")


class Fonts:
    """Font constants for the application."""
    
    # Font families
    PRIMARY_FAMILY = "Segoe UI"
    SECONDARY_FAMILY = "Arial"
    MONOSPACE_FAMILY = "Consolas"
    
    # Font sizes
    SMALL_SIZE = 9
    NORMAL_SIZE = 10
    MEDIUM_SIZE = 12
    LARGE_SIZE = 14
    HEADER_SIZE = 16
    TITLE_SIZE = 18
    
    @classmethod
    def get_font(cls, size: int = NORMAL_SIZE, bold: bool = False, 
                 family: str = PRIMARY_FAMILY) -> QFont:
        """Get a configured font."""
        font = QFont(family, size)
        font.setBold(bold)
        return font
    
    @classmethod
    def get_header_font(cls) -> QFont:
        """Get header font."""
        return cls.get_font(cls.HEADER_SIZE, bold=True)
    
    @classmethod
    def get_title_font(cls) -> QFont:
        """Get title font."""
        return cls.get_font(cls.TITLE_SIZE, bold=True)
    
    @classmethod
    def get_monospace_font(cls, size: int = NORMAL_SIZE) -> QFont:
        """Get monospace font."""
        return cls.get_font(size, family=cls.MONOSPACE_FAMILY)


class Spacing:
    """Spacing constants for layouts."""
    
    TINY_SPACING = 2
    SMALL_SPACING = 5
    MEDIUM_SPACING = 10
    LARGE_SPACING = 15
    EXTRA_LARGE_SPACING = 20
    
    TINY_MARGIN = 3
    SMALL_MARGIN = 6
    MEDIUM_MARGIN = 12
    LARGE_MARGIN = 18
    EXTRA_LARGE_MARGIN = 24


class Dimensions:
    """Size constants for widgets."""
    
    # Button sizes
    BUTTON_HEIGHT = 32
    SMALL_BUTTON_HEIGHT = 24
    LARGE_BUTTON_HEIGHT = 40
    
    # Window sizes
    DIALOG_WIDTH = 400
    DIALOG_HEIGHT = 300
    UTILITY_WIDTH = 600
    UTILITY_HEIGHT = 500
    MAIN_WIDTH = 900
    MAIN_HEIGHT = 700
    
    # Widget sizes
    ICON_SIZE = QSize(16, 16)
    LARGE_ICON_SIZE = QSize(24, 24)
    TOOLBAR_ICON_SIZE = QSize(20, 20)


class ThemeManager:
    """Central theme management class."""
    
    _current_theme = ThemeType.LIGHT
    _custom_styles: Dict[str, str] = {}
    
    @classmethod
    def set_theme(cls, theme: ThemeType):
        """Set the current theme."""
        cls._current_theme = theme
        cls._apply_global_theme()
    
    @classmethod
    def get_current_theme(cls) -> ThemeType:
        """Get the current theme."""
        return cls._current_theme
    
    @classmethod
    def _apply_global_theme(cls):
        """Apply theme to the entire application."""
        app = QApplication.instance()
        if app:
            app.setStyleSheet(cls._get_global_stylesheet())
    
    @classmethod
    def _get_global_stylesheet(cls) -> str:
        """Get the global stylesheet for the current theme."""
        if cls._current_theme == ThemeType.DARK:
            return cls._get_dark_stylesheet()
        else:
            return cls._get_light_stylesheet()
    
    @classmethod
    def _get_light_stylesheet(cls) -> str:
        """Get light theme stylesheet."""
        return f"""
            QMainWindow, QDialog {{
                background-color: {Colors.BACKGROUND_LIGHT.name()};
                color: {Colors.TEXT_PRIMARY.name()};
                font-family: {Fonts.PRIMARY_FAMILY};
                font-size: {Fonts.NORMAL_SIZE}pt;
            }}
            
            QPushButton {{
                background-color: {Colors.PRIMARY.name()};
                color: {Colors.TEXT_LIGHT.name()};
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                min-height: {Dimensions.BUTTON_HEIGHT - 16}px;
                font-weight: bold;
            }}
            
            QPushButton:hover {{
                background-color: {Colors.PRIMARY_HOVER.name()};
            }}
            
            QPushButton:pressed {{
                background-color: {Colors.PRIMARY_PRESSED.name()};
            }}
            
            QPushButton:disabled {{
                background-color: {Colors.TEXT_DISABLED.name()};
            }}
            
            QLineEdit, QTextEdit {{
                background-color: {Colors.BACKGROUND_LIGHT.name()};
                border: 1px solid {Colors.BORDER_LIGHT.name()};
                border-radius: 4px;
                padding: 6px;
                selection-background-color: {Colors.PRIMARY.name()};
            }}
            
            QLineEdit:focus, QTextEdit:focus {{
                border-color: {Colors.BORDER_FOCUS.name()};
            }}
            
            QGroupBox {{
                font-weight: bold;
                border: 1px solid {Colors.BORDER_LIGHT.name()};
                border-radius: 4px;
                margin-top: 1ex;
                padding-top: 10px;
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
                background-color: {Colors.BACKGROUND_LIGHT.name()};
            }}
            
            QListWidget, QTreeWidget, QTableWidget {{
                background-color: {Colors.BACKGROUND_LIGHT.name()};
                border: 1px solid {Colors.BORDER_LIGHT.name()};
                border-radius: 4px;
                selection-background-color: {Colors.PRIMARY.name()};
            }}
            
            QProgressBar {{
                border: 1px solid {Colors.BORDER_LIGHT.name()};
                border-radius: 4px;
                text-align: center;
                background-color: {Colors.BACKGROUND_SECONDARY.name()};
            }}
            
            QProgressBar::chunk {{
                background-color: {Colors.PRIMARY.name()};
                border-radius: 3px;
            }}
        """
    
    @classmethod
    def _get_dark_stylesheet(cls) -> str:
        """Get dark theme stylesheet."""
        return f"""
            QMainWindow, QDialog {{
                background-color: {Colors.BACKGROUND_DARK.name()};
                color: {Colors.TEXT_LIGHT.name()};
                font-family: {Fonts.PRIMARY_FAMILY};
                font-size: {Fonts.NORMAL_SIZE}pt;
            }}
            
            QPushButton {{
                background-color: {Colors.PRIMARY.name()};
                color: {Colors.TEXT_LIGHT.name()};
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                min-height: {Dimensions.BUTTON_HEIGHT - 16}px;
                font-weight: bold;
            }}
            
            QPushButton:hover {{
                background-color: {Colors.PRIMARY_HOVER.name()};
            }}
            
            QPushButton:pressed {{
                background-color: {Colors.PRIMARY_PRESSED.name()};
            }}
            
            QLineEdit, QTextEdit {{
                background-color: {Colors.BACKGROUND_DARK.name()};
                border: 1px solid {Colors.BORDER_DARK.name()};
                border-radius: 4px;
                padding: 6px;
                color: {Colors.TEXT_LIGHT.name()};
            }}
            
            QLineEdit:focus, QTextEdit:focus {{
                border-color: {Colors.BORDER_FOCUS.name()};
            }}
            
            QGroupBox {{
                font-weight: bold;
                border: 1px solid {Colors.BORDER_DARK.name()};
                border-radius: 4px;
                margin-top: 1ex;
                padding-top: 10px;
                color: {Colors.TEXT_LIGHT.name()};
            }}
            
            QListWidget, QTreeWidget, QTableWidget {{
                background-color: {Colors.BACKGROUND_DARK.name()};
                border: 1px solid {Colors.BORDER_DARK.name()};
                border-radius: 4px;
                color: {Colors.TEXT_LIGHT.name()};
            }}
        """
    
    @classmethod
    def apply_main_window_theme(cls, window: QMainWindow):
        """Apply theme to a main window."""
        window.setMinimumSize(Dimensions.MAIN_WIDTH, Dimensions.MAIN_HEIGHT)
        cls._apply_widget_theme(window)
    
    @classmethod
    def apply_utility_window_theme(cls, window: QMainWindow):
        """Apply theme to a utility window."""
        window.setMinimumSize(Dimensions.UTILITY_WIDTH, Dimensions.UTILITY_HEIGHT)
        cls._apply_widget_theme(window)
    
    @classmethod
    def apply_dialog_theme(cls, dialog: QDialog):
        """Apply theme to a dialog."""
        dialog.setMinimumSize(Dimensions.DIALOG_WIDTH, Dimensions.DIALOG_HEIGHT)
        cls._apply_widget_theme(dialog)
    
    @classmethod
    def _apply_widget_theme(cls, widget: QWidget):
        """Apply theme to any widget."""
        widget.setFont(Fonts.get_font())
        if hasattr(widget, 'setStyleSheet'):
            widget.setStyleSheet(cls._get_global_stylesheet())
    
    @classmethod
    def style_primary_button(cls, button: QPushButton):
        """Style a button as primary."""
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.PRIMARY.name()};
                color: {Colors.TEXT_LIGHT.name()};
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                min-height: {Dimensions.BUTTON_HEIGHT - 16}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {Colors.PRIMARY_HOVER.name()};
            }}
            QPushButton:pressed {{
                background-color: {Colors.PRIMARY_PRESSED.name()};
            }}
        """)
    
    @classmethod
    def style_secondary_button(cls, button: QPushButton):
        """Style a button as secondary."""
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.SECONDARY.name()};
                color: {Colors.TEXT_LIGHT.name()};
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                min-height: {Dimensions.BUTTON_HEIGHT - 16}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {Colors.SECONDARY_HOVER.name()};
            }}
        """)
    
    @classmethod
    def style_success_button(cls, button: QPushButton):
        """Style a button as success."""
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.SUCCESS.name()};
                color: {Colors.TEXT_LIGHT.name()};
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                min-height: {Dimensions.BUTTON_HEIGHT - 16}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {Colors.SUCCESS_HOVER.name()};
            }}
        """)
    
    @classmethod
    def style_warning_button(cls, button: QPushButton):
        """Style a button as warning."""
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.WARNING.name()};
                color: {Colors.TEXT_LIGHT.name()};
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                min-height: {Dimensions.BUTTON_HEIGHT - 16}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {Colors.WARNING_HOVER.name()};
            }}
        """)
    
    @classmethod
    def style_error_button(cls, button: QPushButton):
        """Style a button as error."""
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.ERROR.name()};
                color: {Colors.TEXT_LIGHT.name()};
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                min-height: {Dimensions.BUTTON_HEIGHT - 16}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {Colors.ERROR_HOVER.name()};
            }}
        """)
    
    @classmethod
    def style_label(cls, label: QLabel, is_header: bool = False):
        """Style a label."""
        if is_header:
            label.setFont(Fonts.get_header_font())
            label.setStyleSheet(f"""
                QLabel {{
                    color: {Colors.TEXT_PRIMARY.name()};
                    font-weight: bold;
                    padding: {Spacing.MEDIUM_SPACING}px;
                }}
            """)
        else:
            label.setFont(Fonts.get_font())
            label.setStyleSheet(f"""
                QLabel {{
                    color: {Colors.TEXT_PRIMARY.name()};
                }}
            """)
    
    @classmethod
    def create_standard_layout(cls, parent: QWidget) -> QVBoxLayout:
        """Create a standard layout with proper spacing."""
        layout = QVBoxLayout(parent)
        layout.setContentsMargins(
            Spacing.MEDIUM_MARGIN, Spacing.MEDIUM_MARGIN,
            Spacing.MEDIUM_MARGIN, Spacing.MEDIUM_MARGIN
        )
        layout.setSpacing(Spacing.MEDIUM_SPACING)
        return layout
    
    @classmethod
    def create_horizontal_layout(cls, spacing: int = Spacing.MEDIUM_SPACING) -> QHBoxLayout:
        """Create a horizontal layout with proper spacing."""
        layout = QHBoxLayout()
        layout.setSpacing(spacing)
        return layout
    
    @classmethod
    def create_grid_layout(cls, spacing: int = Spacing.MEDIUM_SPACING) -> QGridLayout:
        """Create a grid layout with proper spacing."""
        layout = QGridLayout()
        layout.setSpacing(spacing)
        return layout


# Convenience functions for backward compatibility
def apply_theme(widget: QWidget, theme: ThemeType = ThemeType.LIGHT):
    """Apply theme to a widget."""
    ThemeManager.set_theme(theme)
    ThemeManager._apply_widget_theme(widget)


def get_primary_color() -> QColor:
    """Get the primary color."""
    return Colors.PRIMARY


def get_font(size: int = Fonts.NORMAL_SIZE, bold: bool = False) -> QFont:
    """Get a font with specified properties."""
    return Fonts.get_font(size, bold)


# Initialize theme manager
ThemeManager.set_theme(ThemeType.LIGHT)