"""
Centralized theme system for Richard's File Utilities.

This module provides consistent styling and appearance across all GUI utilities.
"""

from PyQt5.QtGui import QColor, QFont
from PyQt5.QtCore import Qt

# Color Palette
class Colors:
    """Standard color definitions."""
    
    # Primary colors
    PRIMARY = "#2C3E50"           # Dark blue-gray
    SECONDARY = "#34495E"        # Medium blue-gray
    ACCENT = "#3498DB"           # Bright blue
    
    # Background colors
    BACKGROUND = "#ECF0F1"       # Light gray
    WINDOW_BACKGROUND = "#FFFFFF"  # White
    DIALOG_BACKGROUND = "#F8F9FA"  # Very light gray
    
    # Text colors
    TEXT_PRIMARY = "#2C3E50"     # Dark blue-gray
    TEXT_SECONDARY = "#7F8C8D"   # Medium gray
    TEXT_DISABLED = "#BDC3C7"    # Light gray
    
    # Button colors
    BUTTON_PRIMARY = "#3498DB"   # Bright blue
    BUTTON_PRIMARY_HOVER = "#2980B9"
    BUTTON_PRIMARY_PRESSED = "#21618C"
    
    BUTTON_SECONDARY = "#95A5A6" # Medium gray
    BUTTON_SECONDARY_HOVER = "#7F8C8D"
    BUTTON_SECONDARY_PRESSED = "#6C7A89"
    
    # Status colors
    SUCCESS = "#27AE60"          # Green
    WARNING = "#F39C12"          # Orange
    ERROR = "#E74C3C"            # Red
    INFO = "#3498DB"             # Blue

# Typography
class Fonts:
    """Standard font definitions."""
    
    # Font families
    DEFAULT_FAMILY = "Segoe UI"
    MONOSPACE_FAMILY = "Consolas"
    
    # Font sizes
    TITLE_SIZE = 16
    HEADER_SIZE = 14
    BODY_SIZE = 12
    SMALL_SIZE = 10
    
    # Font weights
    NORMAL = QFont.Normal
    BOLD = QFont.Bold
    
    @classmethod
    def get_font(cls, size=BODY_SIZE, weight=NORMAL, family=DEFAULT_FAMILY):
        """Get a standardized font."""
        font = QFont(family)
        font.setPointSize(size)
        font.setWeight(weight)
        return font

# Spacing
class Spacing:
    """Standard spacing values."""
    
    # Margins
    WINDOW_MARGIN = 20
    DIALOG_MARGIN = 15
    
    # Padding
    BUTTON_PADDING = "12px 24px"
    INPUT_PADDING = "8px 12px"
    
    # Spacing between elements
    SMALL_SPACING = 5
    MEDIUM_SPACING = 10
    LARGE_SPACING = 15
    XLARGE_SPACING = 20

# Dimensions
class Dimensions:
    """Standard dimensions."""
    
    # Window sizes
    MAIN_WINDOW_MIN_WIDTH = 800
    MAIN_WINDOW_MIN_HEIGHT = 600
    UTILITY_WINDOW_MIN_WIDTH = 400
    UTILITY_WINDOW_MIN_HEIGHT = 300
    DIALOG_WIDTH = 450
    DIALOG_HEIGHT = 300
    
    # Button sizes
    BUTTON_MIN_WIDTH = 120
    BUTTON_MIN_HEIGHT = 40
    
    # Input sizes
    INPUT_MIN_WIDTH = 200
    INPUT_MIN_HEIGHT = 30

# Stylesheets
class Styles:
    """Standard stylesheet definitions."""
    
    # Main window stylesheet
    MAIN_WINDOW = f"""
        QMainWindow {{
            background-color: {Colors.WINDOW_BACKGROUND};
            color: {Colors.TEXT_PRIMARY};
        }}
    """
    
    # Button stylesheets
    PRIMARY_BUTTON = f"""
        QPushButton {{
            background-color: {Colors.BUTTON_PRIMARY};
            color: white;
            border: none;
            border-radius: 8px;
            padding: {Spacing.BUTTON_PADDING};
            font-size: 12px;
            font-weight: bold;
            min-width: {Dimensions.BUTTON_MIN_WIDTH}px;
            min-height: {Dimensions.BUTTON_MIN_HEIGHT}px;
        }}
        QPushButton:hover {{
            background-color: {Colors.BUTTON_PRIMARY_HOVER};
        }}
        QPushButton:pressed {{
            background-color: {Colors.BUTTON_PRIMARY_PRESSED};
        }}
        QPushButton:disabled {{
            background-color: {Colors.TEXT_DISABLED};
            color: white;
        }}
    """
    
    SECONDARY_BUTTON = f"""
        QPushButton {{
            background-color: {Colors.BUTTON_SECONDARY};
            color: white;
            border: none;
            border-radius: 8px;
            padding: {Spacing.BUTTON_PADDING};
            font-size: 12px;
            font-weight: bold;
            min-width: {Dimensions.BUTTON_MIN_WIDTH}px;
            min-height: {Dimensions.BUTTON_MIN_HEIGHT}px;
        }}
        QPushButton:hover {{
            background-color: {Colors.BUTTON_SECONDARY_HOVER};
        }}
        QPushButton:pressed {{
            background-color: {Colors.BUTTON_SECONDARY_PRESSED};
        }}
    """
    
    # Input field stylesheet
    INPUT_FIELD = f"""
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {Colors.WINDOW_BACKGROUND};
            border: 1px solid {Colors.TEXT_DISABLED};
            border-radius: 4px;
            padding: {Spacing.INPUT_PADDING};
            color: {Colors.TEXT_PRIMARY};
            font-size: 12px;
        }}
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border: 2px solid {Colors.ACCENT};
        }}
        QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {{
            background-color: {Colors.DIALOG_BACKGROUND};
            color: {Colors.TEXT_DISABLED};
        }}
    """
    
    # Label stylesheet
    LABEL = f"""
        QLabel {{
            color: {Colors.TEXT_PRIMARY};
            font-size: 12px;
        }}
    """
    
    HEADER_LABEL = f"""
        QLabel {{
            color: {Colors.TEXT_PRIMARY};
            font-size: 14px;
            font-weight: bold;
        }}
    """
    
    # Group box stylesheet
    GROUP_BOX = f"""
        QGroupBox {{
            font-weight: bold;
            border: 2px solid {Colors.SECONDARY};
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 10px;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }}
    """
    
    # Progress bar stylesheet
    PROGRESS_BAR = f"""
        QProgressBar {{
            border: 1px solid {Colors.TEXT_DISABLED};
            border-radius: 4px;
            text-align: center;
            background-color: {Colors.DIALOG_BACKGROUND};
        }}
        QProgressBar::chunk {{
            background-color: {Colors.ACCENT};
            border-radius: 3px;
        }}
    """

# Utility functions
class ThemeManager:
    """Manager for applying themes consistently."""
    
    @staticmethod
    def apply_main_window_theme(window):
        """Apply main window theme to a QMainWindow."""
        window.setStyleSheet(Styles.MAIN_WINDOW)
        window.setMinimumSize(
            Dimensions.MAIN_WINDOW_MIN_WIDTH,
            Dimensions.MAIN_WINDOW_MIN_HEIGHT
        )
    
    @staticmethod
    def apply_utility_window_theme(window):
        """Apply utility window theme to a QDialog or QWidget."""
        window.setMinimumSize(
            Dimensions.UTILITY_WINDOW_MIN_WIDTH,
            Dimensions.UTILITY_WINDOW_MIN_HEIGHT
        )
    
    @staticmethod
    def style_primary_button(button):
        """Apply primary button styling."""
        button.setStyleSheet(Styles.PRIMARY_BUTTON)
        button.setFont(Fonts.get_font(Fonts.BODY_SIZE, Fonts.BOLD))
    
    @staticmethod
    def style_secondary_button(button):
        """Apply secondary button styling."""
        button.setStyleSheet(Styles.SECONDARY_BUTTON)
        button.setFont(Fonts.get_font(Fonts.BODY_SIZE, Fonts.BOLD))
    
    @staticmethod
    def style_input_field(widget):
        """Apply input field styling."""
        widget.setStyleSheet(Styles.INPUT_FIELD)
        widget.setFont(Fonts.get_font())
    
    @staticmethod
    def style_label(label, is_header=False):
        """Apply label styling."""
        if is_header:
            label.setStyleSheet(Styles.HEADER_LABEL)
            label.setFont(Fonts.get_font(Fonts.HEADER_SIZE, Fonts.BOLD))
        else:
            label.setStyleSheet(Styles.LABEL)
            label.setFont(Fonts.get_font())
    
    @staticmethod
    def style_group_box(group_box):
        """Apply group box styling."""
        group_box.setStyleSheet(Styles.GROUP_BOX)
        group_box.setFont(Fonts.get_font(Fonts.BODY_SIZE, Fonts.BOLD))
    
    @staticmethod
    def style_progress_bar(progress_bar):
        """Apply progress bar styling."""
        progress_bar.setStyleSheet(Styles.PROGRESS_BAR)
    
    @staticmethod
    def create_standard_layout(widget):
        """Create a standard layout with consistent spacing."""
        from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout
        
        layout = QVBoxLayout()
        layout.setContentsMargins(
            Spacing.WINDOW_MARGIN,
            Spacing.WINDOW_MARGIN,
            Spacing.WINDOW_MARGIN,
            Spacing.WINDOW_MARGIN
        )
        layout.setSpacing(Spacing.LARGE_SPACING)
        
        return layout
