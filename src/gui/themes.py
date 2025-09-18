"""
Centralized theme system for Richard's File Utilities.

This module provides consistent styling and appearance across all GUI utilities.
"""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont


# Color Palette
class LightColors:
    """Light theme color definitions."""
    
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


class DarkColors:
    """Dark theme color definitions."""
    
    # Primary colors
    PRIMARY = "#3A4A5C"          # Dark blue-gray
    SECONDARY = "#4A5A6C"        # Medium blue-gray
    ACCENT = "#5DADE2"           # Bright blue (lighter for dark backgrounds)
    
    # Background colors
    BACKGROUND = "#2C3E50"       # Dark blue-gray
    WINDOW_BACKGROUND = "#34495E"  # Medium blue-gray
    DIALOG_BACKGROUND = "#3A4A5C"  # Slightly lighter gray
    
    # Text colors
    TEXT_PRIMARY = "#ECF0F1"     # Light gray
    TEXT_SECONDARY = "#BDC3C7"   # Medium gray
    TEXT_DISABLED = "#7F8C8D"    # Darker gray
    
    # Button colors
    BUTTON_PRIMARY = "#5DADE2"   # Bright blue
    BUTTON_PRIMARY_HOVER = "#7FB3D3"
    BUTTON_PRIMARY_PRESSED = "#85C1E9"
    
    BUTTON_SECONDARY = "#5D6D7E"  # Dark gray
    BUTTON_SECONDARY_HOVER = "#6C7B7F"
    BUTTON_SECONDARY_PRESSED = "#7B8A8F"
    
    # Status colors
    SUCCESS = "#58D68D"          # Light green
    WARNING = "#F7DC6F"          # Light orange
    ERROR = "#F1948A"            # Light red
    INFO = "#7FB3D3"             # Light blue


# Dynamic color selection based on current theme
class Colors:
    """Dynamic color definitions that change based on current theme."""
    
    _current_theme = "light"  # Default theme
    
    @classmethod
    def set_theme(cls, theme_name: str):
        """Set the current theme."""
        cls._current_theme = theme_name.lower()
    
    @classmethod
    def get_theme(cls) -> str:
        """Get the current theme."""
        return cls._current_theme
    
    @classmethod
    def _get_color_class(cls):
        """Get the appropriate color class based on current theme."""
        return DarkColors if cls._current_theme == "dark" else LightColors
    
    @classmethod
    @property
    def PRIMARY(cls):
        return cls._get_color_class().PRIMARY
    
    @classmethod
    @property
    def SECONDARY(cls):
        return cls._get_color_class().SECONDARY
    
    @classmethod
    @property
    def ACCENT(cls):
        return cls._get_color_class().ACCENT
    
    @classmethod
    @property
    def BACKGROUND(cls):
        return cls._get_color_class().BACKGROUND
    
    @classmethod
    @property
    def WINDOW_BACKGROUND(cls):
        return cls._get_color_class().WINDOW_BACKGROUND
    
    @classmethod
    @property
    def DIALOG_BACKGROUND(cls):
        return cls._get_color_class().DIALOG_BACKGROUND
    
    @classmethod
    @property
    def TEXT_PRIMARY(cls):
        return cls._get_color_class().TEXT_PRIMARY
    
    @classmethod
    @property
    def TEXT_SECONDARY(cls):
        return cls._get_color_class().TEXT_SECONDARY
    
    @classmethod
    @property
    def TEXT_DISABLED(cls):
        return cls._get_color_class().TEXT_DISABLED
    
    @classmethod
    @property
    def BUTTON_PRIMARY(cls):
        return cls._get_color_class().BUTTON_PRIMARY
    
    @classmethod
    @property
    def BUTTON_PRIMARY_HOVER(cls):
        return cls._get_color_class().BUTTON_PRIMARY_HOVER
    
    @classmethod
    @property
    def BUTTON_PRIMARY_PRESSED(cls):
        return cls._get_color_class().BUTTON_PRIMARY_PRESSED
    
    @classmethod
    @property
    def BUTTON_SECONDARY(cls):
        return cls._get_color_class().BUTTON_SECONDARY
    
    @classmethod
    @property
    def BUTTON_SECONDARY_HOVER(cls):
        return cls._get_color_class().BUTTON_SECONDARY_HOVER
    
    @classmethod
    @property
    def BUTTON_SECONDARY_PRESSED(cls):
        return cls._get_color_class().BUTTON_SECONDARY_PRESSED
    
    @classmethod
    @property
    def SUCCESS(cls):
        return cls._get_color_class().SUCCESS
    
    @classmethod
    @property
    def WARNING(cls):
        return cls._get_color_class().WARNING
    
    @classmethod
    @property
    def ERROR(cls):
        return cls._get_color_class().ERROR
    
    @classmethod
    @property
    def INFO(cls):
        return cls._get_color_class().INFO

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
    """Dynamic stylesheet definitions that change based on current theme."""
    
    @classmethod
    def get_main_window_style(cls):
        """Get main window stylesheet."""
        return f"""
            QMainWindow {{
                background-color: {Colors.WINDOW_BACKGROUND};
                color: {Colors.TEXT_PRIMARY};
            }}
        """
    
    @classmethod
    def get_primary_button_style(cls):
        """Get primary button stylesheet."""
        return f"""
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
    
    @classmethod
    def get_secondary_button_style(cls):
        """Get secondary button stylesheet."""
        return f"""
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
    
    @classmethod
    def get_input_field_style(cls):
        """Get input field stylesheet."""
        return f"""
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
    
    @classmethod
    def get_label_style(cls):
        """Get label stylesheet."""
        return f"""
            QLabel {{
                color: {Colors.TEXT_PRIMARY};
                font-size: 12px;
            }}
        """
    
    @classmethod
    def get_header_label_style(cls):
        """Get header label stylesheet."""
        return f"""
            QLabel {{
                color: {Colors.TEXT_PRIMARY};
                font-size: 14px;
                font-weight: bold;
            }}
        """
    
    @classmethod
    def get_group_box_style(cls):
        """Get group box stylesheet."""
        return f"""
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {Colors.SECONDARY};
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                color: {Colors.TEXT_PRIMARY};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
        """
    
    @classmethod
    def get_progress_bar_style(cls):
        """Get progress bar stylesheet."""
        return f"""
            QProgressBar {{
                border: 1px solid {Colors.TEXT_DISABLED};
                border-radius: 4px;
                text-align: center;
                background-color: {Colors.DIALOG_BACKGROUND};
                color: {Colors.TEXT_PRIMARY};
            }}
            QProgressBar::chunk {{
                background-color: {Colors.ACCENT};
                border-radius: 3px;
            }}
        """
    
    @classmethod
    def get_tree_widget_style(cls):
        """Get tree widget stylesheet for file lists."""
        return f"""
            QTreeWidget {{
                background-color: {Colors.WINDOW_BACKGROUND};
                border: 1px solid {Colors.TEXT_DISABLED};
                color: {Colors.TEXT_PRIMARY};
                selection-background-color: {Colors.ACCENT};
                selection-color: white;
            }}
            QTreeWidget::item {{
                padding: 4px;
                border: none;
            }}
            QTreeWidget::item:selected {{
                background-color: {Colors.ACCENT};
                color: white;
            }}
            QTreeWidget::item:hover {{
                background-color: {Colors.BACKGROUND};
            }}
            QHeaderView::section {{
                background-color: {Colors.DIALOG_BACKGROUND};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.TEXT_DISABLED};
                padding: 6px;
            }}
        """
    
    @classmethod
    def get_frame_style(cls):
        """Get frame stylesheet."""
        return f"""
            QFrame {{
                background-color: {Colors.WINDOW_BACKGROUND};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.TEXT_DISABLED};
            }}
        """
    
    @classmethod
    def get_combo_box_style(cls):
        """Get combo box stylesheet."""
        return f"""
            QComboBox {{
                background-color: {Colors.WINDOW_BACKGROUND};
                border: 1px solid {Colors.TEXT_DISABLED};
                border-radius: 4px;
                padding: 4px 8px;
                color: {Colors.TEXT_PRIMARY};
                min-width: 80px;
            }}
            QComboBox:hover {{
                border: 2px solid {Colors.ACCENT};
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid {Colors.TEXT_DISABLED};
            }}
            QComboBox::down-arrow {{
                color: {Colors.TEXT_PRIMARY};
            }}
            QComboBox QAbstractItemView {{
                background-color: {Colors.WINDOW_BACKGROUND};
                border: 1px solid {Colors.TEXT_DISABLED};
                color: {Colors.TEXT_PRIMARY};
                selection-background-color: {Colors.ACCENT};
            }}
        """
    
    # Legacy static properties for backward compatibility
    @property
    def MAIN_WINDOW(self):
        return self.get_main_window_style()
    
    @property
    def PRIMARY_BUTTON(self):
        return self.get_primary_button_style()
    
    @property
    def SECONDARY_BUTTON(self):
        return self.get_secondary_button_style()
    
    @property
    def INPUT_FIELD(self):
        return self.get_input_field_style()
    
    @property
    def LABEL(self):
        return self.get_label_style()
    
    @property
    def HEADER_LABEL(self):
        return self.get_header_label_style()
    
    @property
    def GROUP_BOX(self):
        return self.get_group_box_style()
    
    @property
    def PROGRESS_BAR(self):
        return self.get_progress_bar_style()


# Utility functions
class ThemeManager:
    """Manager for applying themes consistently and dynamically."""
    
    _theme_changed_callbacks = []
    
    @classmethod
    def add_theme_changed_callback(cls, callback):
        """Add a callback to be called when theme changes."""
        cls._theme_changed_callbacks.append(callback)
    
    @classmethod
    def remove_theme_changed_callback(cls, callback):
        """Remove a theme change callback."""
        if callback in cls._theme_changed_callbacks:
            cls._theme_changed_callbacks.remove(callback)
    
    @classmethod
    def set_theme(cls, theme_name: str):
        """Set the current theme and notify all callbacks."""
        Colors.set_theme(theme_name)
        
        # Notify all callbacks about theme change
        for callback in cls._theme_changed_callbacks:
            try:
                callback(theme_name)
            except Exception as e:
                print(f"Error in theme change callback: {e}")
    
    @classmethod
    def get_current_theme(cls) -> str:
        """Get the current theme."""
        return Colors.get_theme()
    
    @staticmethod
    def apply_main_window_theme(window):
        """Apply main window theme to a QMainWindow."""
        window.setStyleSheet(Styles.get_main_window_style())
        window.setMinimumSize(
            Dimensions.MAIN_WINDOW_MIN_WIDTH,
            Dimensions.MAIN_WINDOW_MIN_HEIGHT
        )
    
    @staticmethod
    def apply_utility_window_theme(window):
        """Apply utility window theme to a QDialog or QWidget."""
        window.setStyleSheet(Styles.get_main_window_style())
        window.setMinimumSize(
            Dimensions.UTILITY_WINDOW_MIN_WIDTH,
            Dimensions.UTILITY_WINDOW_MIN_HEIGHT
        )
    
    @staticmethod
    def style_primary_button(button):
        """Apply primary button styling."""
        button.setStyleSheet(Styles.get_primary_button_style())
        button.setFont(Fonts.get_font(Fonts.BODY_SIZE, Fonts.BOLD))
    
    @staticmethod
    def style_secondary_button(button):
        """Apply secondary button styling."""
        button.setStyleSheet(Styles.get_secondary_button_style())
        button.setFont(Fonts.get_font(Fonts.BODY_SIZE, Fonts.BOLD))
    
    @staticmethod
    def style_input_field(widget):
        """Apply input field styling."""
        widget.setStyleSheet(Styles.get_input_field_style())
        widget.setFont(Fonts.get_font())
    
    @staticmethod
    def style_label(label, is_header=False):
        """Apply label styling."""
        if is_header:
            label.setStyleSheet(Styles.get_header_label_style())
            label.setFont(Fonts.get_font(Fonts.HEADER_SIZE, Fonts.BOLD))
        else:
            label.setStyleSheet(Styles.get_label_style())
            label.setFont(Fonts.get_font())
    
    @staticmethod
    def style_group_box(group_box):
        """Apply group box styling."""
        group_box.setStyleSheet(Styles.get_group_box_style())
        group_box.setFont(Fonts.get_font(Fonts.BODY_SIZE, Fonts.BOLD))
    
    @staticmethod
    def style_progress_bar(progress_bar):
        """Apply progress bar styling."""
        progress_bar.setStyleSheet(Styles.get_progress_bar_style())
    
    @staticmethod
    def style_tree_widget(tree_widget):
        """Apply tree widget styling."""
        tree_widget.setStyleSheet(Styles.get_tree_widget_style())
    
    @staticmethod
    def style_frame(frame):
        """Apply frame styling."""
        frame.setStyleSheet(Styles.get_frame_style())
    
    @staticmethod
    def style_combo_box(combo_box):
        """Apply combo box styling."""
        combo_box.setStyleSheet(Styles.get_combo_box_style())
    
    @staticmethod
    def apply_theme_to_widget(widget, widget_type="default"):
        """Apply theme to a widget based on its type."""
        try:
            if hasattr(widget, 'setStyleSheet'):
                if widget_type == "tree":
                    ThemeManager.style_tree_widget(widget)
                elif widget_type == "frame":
                    ThemeManager.style_frame(widget)
                elif widget_type == "combo":
                    ThemeManager.style_combo_box(widget)
                elif widget_type == "input":
                    ThemeManager.style_input_field(widget)
                elif widget_type == "button_primary":
                    ThemeManager.style_primary_button(widget)
                elif widget_type == "button_secondary":
                    ThemeManager.style_secondary_button(widget)
                elif widget_type == "label":
                    ThemeManager.style_label(widget)
                elif widget_type == "group":
                    ThemeManager.style_group_box(widget)
                elif widget_type == "progress":
                    ThemeManager.style_progress_bar(widget)
                else:
                    # Apply general styling based on widget class
                    widget_class = widget.__class__.__name__
                    if "TreeWidget" in widget_class:
                        ThemeManager.style_tree_widget(widget)
                    elif "Frame" in widget_class:
                        ThemeManager.style_frame(widget)
                    elif "ComboBox" in widget_class:
                        ThemeManager.style_combo_box(widget)
                    elif "LineEdit" in widget_class or "TextEdit" in widget_class:
                        ThemeManager.style_input_field(widget)
                    elif "Button" in widget_class:
                        ThemeManager.style_primary_button(widget)
                    elif "Label" in widget_class:
                        ThemeManager.style_label(widget)
                    elif "GroupBox" in widget_class:
                        ThemeManager.style_group_box(widget)
                    elif "ProgressBar" in widget_class:
                        ThemeManager.style_progress_bar(widget)
        except Exception as e:
            print(f"Error applying theme to widget {widget}: {e}")
    
    @staticmethod
    def create_standard_layout():
        """Create a standard layout with consistent spacing."""
        from PyQt5.QtWidgets import QVBoxLayout
        
        layout = QVBoxLayout()
        layout.setContentsMargins(
            Spacing.WINDOW_MARGIN,
            Spacing.WINDOW_MARGIN,
            Spacing.WINDOW_MARGIN,
            Spacing.WINDOW_MARGIN
        )
        layout.setSpacing(Spacing.LARGE_SPACING)
        
        return layout
