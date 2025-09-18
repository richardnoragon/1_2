"""Centralized style definitions for the application."""
from enum import Enum
from typing import Dict


class Theme(Enum):
    """Available themes for the application."""
    LIGHT = "light"
    DARK = "dark"


class Colors:
    """Color definitions for the application."""
    # Light theme colors
    LIGHT = {
        "window_bg": "#f5f5f5",
        "widget_bg": "#ffffff",
        "primary": "#2196F3",
        "primary_hover": "#1976D2",
        "primary_pressed": "#0D47A1",
        "success": "#4CAF50",
        "success_hover": "#388E3C",
        "warning": "#FFC107",
        "error": "#f44336",
        "text": "#333333",
        "text_secondary": "#666666",
        "border": "#dcdcdc",
        "separator": "#e0e0e0",
        "disabled": "#9e9e9e",
        "highlight": "#bbdefb"
    }

    # Dark theme colors
    DARK = {
        "window_bg": "#303030",
        "widget_bg": "#424242",
        "primary": "#2196F3",
        "primary_hover": "#1976D2",
        "primary_pressed": "#0D47A1",
        "success": "#4CAF50",
        "success_hover": "#388E3C",
        "warning": "#FFC107",
        "error": "#f44336",
        "text": "#ffffff",
        "text_secondary": "#b0b0b0",
        "border": "#505050",
        "separator": "#606060",
        "disabled": "#707070",
        "highlight": "#1565C0"
    }


def get_base_styles(theme: Theme = Theme.LIGHT, font_size: int = 12) -> str:
    """Get the base stylesheet for the application.
    
    Args:
        theme: The theme to use for styling
        font_size: Base font size in points
        
    Returns:
        The complete stylesheet as a string
    """
    colors = Colors.LIGHT if theme == Theme.LIGHT else Colors.DARK
    
    return f"""
        QMainWindow, QDialog {{
            background-color: {colors['window_bg']};
        }}
        
        /* Labels */
        QLabel {{
            color: {colors['text']};
            font-size: {font_size}pt;
        }}
        
        /* Push Buttons */
        QPushButton {{
            background-color: {colors['primary']};
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            min-height: 32px;
            font-size: {font_size}pt;
        }}
        
        QPushButton:hover {{
            background-color: {colors['primary_hover']};
        }}
        
        QPushButton:pressed {{
            background-color: {colors['primary_pressed']};
        }}
        
        QPushButton:disabled {{
            background-color: {colors['disabled']};
        }}
        
        /* Success buttons */
        QPushButton[success="true"] {{
            background-color: {colors['success']};
        }}
        
        QPushButton[success="true"]:hover {{
            background-color: {colors['success_hover']};
        }}
        
        /* Line Edits */
        QLineEdit {{
            background-color: {colors['widget_bg']};
            color: {colors['text']};
            border: 1px solid {colors['border']};
            border-radius: 4px;
            padding: 6px;
            font-size: {font_size}pt;
        }}
        
        QLineEdit:focus {{
            border-color: {colors['primary']};
        }}
        
        /* Combo Boxes */
        QComboBox {{
            background-color: {colors['widget_bg']};
            color: {colors['text']};
            border: 1px solid {colors['border']};
            border-radius: 4px;
            padding: 6px;
            min-height: 32px;
            font-size: {font_size}pt;
        }}
        
        QComboBox:hover {{
            border-color: {colors['primary']};
        }}
        
        /* List and Tree Views */
        QListView, QTreeView, QTableView {{
            background-color: {colors['widget_bg']};
            color: {colors['text']};
            border: 1px solid {colors['border']};
            border-radius: 4px;
            font-size: {font_size}pt;
        }}
        
        QListView::item:selected, QTreeView::item:selected, QTableView::item:selected {{
            background-color: {colors['highlight']};
        }}
        
        /* Group Boxes */
        QGroupBox {{
            background-color: {colors['widget_bg']};
            border: 1px solid {colors['border']};
            border-radius: 4px;
            margin-top: 1.5ex;
            font-size: {font_size}pt;
        }}
        
        QGroupBox::title {{
            color: {colors['text']};
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 0 5px;
        }}
        
        /* Check Boxes and Radio Buttons */
        QCheckBox, QRadioButton {{
            color: {colors['text']};
            spacing: 8px;
            font-size: {font_size}pt;
        }}
        
        /* Progress Bars */
        QProgressBar {{
            background-color: {colors['widget_bg']};
            border: 1px solid {colors['border']};
            border-radius: 4px;
            text-align: center;
            font-size: {font_size}pt;
        }}
        
        QProgressBar::chunk {{
            background-color: {colors['primary']};
            border-radius: 3px;
        }}
        
        /* Status Bar */
        QStatusBar {{
            background-color: {colors['window_bg']};
            color: {colors['text']};
            border-top: 1px solid {colors['border']};
        }}
        
        /* Menu Bar */
        QMenuBar {{
            background-color: {colors['window_bg']};
            color: {colors['text']};
            border-bottom: 1px solid {colors['border']};
        }}
        
        QMenuBar::item:selected {{
            background-color: {colors['highlight']};
        }}
        
        /* Menu */
        QMenu {{
            background-color: {colors['widget_bg']};
            color: {colors['text']};
            border: 1px solid {colors['border']};
        }}
        
        QMenu::item:selected {{
            background-color: {colors['highlight']};
        }}
        
        /* Scroll Bars */
        QScrollBar:vertical {{
            background-color: {colors['widget_bg']};
            width: 12px;
            margin: 0;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {colors['primary']};
            border-radius: 6px;
            min-height: 20px;
        }}
        
        QScrollBar:horizontal {{
            background-color: {colors['widget_bg']};
            height: 12px;
            margin: 0;
        }}
        
        QScrollBar::handle:horizontal {{
            background-color: {colors['primary']};
            border-radius: 6px;
            min-width: 20px;
        }}
        
        /* Tabs */
        QTabWidget::pane {{
            border: 1px solid {colors['border']};
            border-radius: 4px;
            background-color: {colors['widget_bg']};
        }}
        
        QTabBar::tab {{
            background-color: {colors['window_bg']};
            color: {colors['text']};
            padding: 8px 16px;
            border: 1px solid {colors['border']};
            border-bottom: none;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            font-size: {font_size}pt;
        }}
        
        QTabBar::tab:selected {{
            background-color: {colors['widget_bg']};
            border-bottom: none;
        }}
        
        /* Spinboxes and Date/Time edits */
        QSpinBox, QDoubleSpinBox, QDateTimeEdit {{
            background-color: {colors['widget_bg']};
            color: {colors['text']};
            border: 1px solid {colors['border']};
            border-radius: 4px;
            padding: 6px;
            font-size: {font_size}pt;
        }}
    """


def get_custom_styles() -> Dict[str, str]:
    """Get custom styles for specific widgets or windows.
    
    Returns:
        A dictionary of custom style overrides
    """
    return {
        "ProgressWidget": """
            QProgressBar {
                max-height: 16px;
                border-radius: 8px;
            }
            QProgressBar::chunk {
                border-radius: 7px;
            }
        """,
        "FileOperationWindow": """
            QListView {
                min-height: 200px;
            }
            QProgressBar {
                margin: 10px 0;
            }
        """
    }
