"""
Centralized theme system for Richard's File Utilities.

This module provides consistent styling and appearance across all utilities.
"""

from typing import Callable, List

try:
    from PyQt5.QtCore import QObject, Qt, pyqtSignal
    from PyQt5.QtGui import QColor, QFont
except ImportError:  # pragma: no cover - headless / startup-safe fallback
    class QObject:  # type: ignore[override]
        pass

    class _FallbackSignal:
        def __init__(self):
            self._callbacks: List[Callable] = []

        def __call__(self, *args, **kwargs):
            return None

        def connect(self, callback):
            if callable(callback) and callback not in self._callbacks:
                self._callbacks.append(callback)

        def disconnect(self, callback):
            if callback in self._callbacks:
                self._callbacks.remove(callback)

        def emit(self, *args, **kwargs):
            for callback in list(self._callbacks):
                callback(*args, **kwargs)

    def pyqtSignal(*args, **kwargs):
        return _FallbackSignal()

    class Qt:
        align_center = 0
        dialog = 0
        window = 0
        window_title_hint = 0
        window_system_menu_hint = 0
        window_close_button_hint = 0
        window_minimize_button_hint = 0
        window_maximize_button_hint = 0

    class QColor:
        def __init__(self, *args, **kwargs):
            self.value = args[0] if args else "#000000"

    class QFont:
        normal = 0
        bold = 1
        demi_bold = 2

        def __init__(self, *args, **kwargs):
            self.family = args[0] if args else "Sans"
            self.point_size = kwargs.get("pointSize", 10)

        def set_point_size(self, value):
            self.point_size = value

        def set_weight(self, value):
            self.weight = value


# Color Palette
class LightColors:
    """Light theme color definitions."""

    # Primary colors
    PRIMARY = "#2C3E50"  # Dark blue-gray
    SECONDARY = "#34495E"  # Medium blue-gray
    ACCENT = "#3498DB"  # Bright blue

    # Background colors
    BACKGROUND = "#ECF0F1"  # Light gray
    WINDOW_BACKGROUND = "#FFFFFF"  # White
    DIALOG_BACKGROUND = "#F8F9FA"  # Very light gray

    # Text colors
    TEXT_PRIMARY = "#2C3E50"  # Dark blue-gray
    TEXT_SECONDARY = "#7F8C8D"  # Medium gray
    TEXT_DISABLED = "#BDC3C7"  # Light gray

    # Button colors
    BUTTON_PRIMARY = "#3498DB"  # Bright blue
    BUTTON_PRIMARY_HOVER = "#2980B9"
    BUTTON_PRIMARY_PRESSED = "#21618C"

    BUTTON_SECONDARY = "#95A5A6"  # Medium gray
    BUTTON_SECONDARY_HOVER = "#7F8C8D"
    BUTTON_SECONDARY_PRESSED = "#6C7A89"

    # Status colors
    SUCCESS = "#27AE60"  # Green
    WARNING = "#F39C12"  # Orange
    ERROR = "#E74C3C"  # Red
    INFO = "#3498DB"  # Blue


class DarkColors:
    """Dark theme color definitions."""

    # Primary colors
    PRIMARY = "#3A4A5C"  # Dark blue-gray
    SECONDARY = "#4A5A6C"  # Medium blue-gray
    ACCENT = "#5DADE2"  # Bright blue (lighter for dark backgrounds)

    # Background colors
    BACKGROUND = "#2C3E50"  # Dark blue-gray
    WINDOW_BACKGROUND = "#34495E"  # Medium blue-gray
    DIALOG_BACKGROUND = "#3A4A5C"  # Slightly lighter gray

    # Text colors
    TEXT_PRIMARY = "#ECF0F1"  # Light gray
    TEXT_SECONDARY = "#BDC3C7"  # Medium gray
    TEXT_DISABLED = "#7F8C8D"  # Darker gray

    # Button colors
    BUTTON_PRIMARY = "#5DADE2"  # Bright blue
    BUTTON_PRIMARY_HOVER = "#7FB3D3"
    BUTTON_PRIMARY_PRESSED = "#85C1E9"

    BUTTON_SECONDARY = "#5D6D7E"  # Dark gray
    BUTTON_SECONDARY_HOVER = "#6C7B7F"
    BUTTON_SECONDARY_PRESSED = "#7B8A8F"

    # Status colors
    SUCCESS = "#58D68D"  # Light green
    WARNING = "#F7DC6F"  # Light orange
    ERROR = "#F1948A"  # Light red
    INFO = "#7FB3D3"  # Light blue


# Dynamic color selection based on current theme
class Colors:
    """Dynamic color definitions that change based on current theme."""

    _current_theme = "light"  # Default theme

    # Initialize with light theme colors by default
    PRIMARY = LightColors.PRIMARY
    SECONDARY = LightColors.SECONDARY
    ACCENT = LightColors.ACCENT
    BACKGROUND = LightColors.BACKGROUND
    WINDOW_BACKGROUND = LightColors.WINDOW_BACKGROUND
    DIALOG_BACKGROUND = LightColors.DIALOG_BACKGROUND
    TEXT_PRIMARY = LightColors.TEXT_PRIMARY
    TEXT_SECONDARY = LightColors.TEXT_SECONDARY
    TEXT_DISABLED = LightColors.TEXT_DISABLED
    BUTTON_PRIMARY = LightColors.BUTTON_PRIMARY
    BUTTON_PRIMARY_HOVER = LightColors.BUTTON_PRIMARY_HOVER
    BUTTON_PRIMARY_PRESSED = LightColors.BUTTON_PRIMARY_PRESSED
    BUTTON_SECONDARY = LightColors.BUTTON_SECONDARY
    BUTTON_SECONDARY_HOVER = LightColors.BUTTON_SECONDARY_HOVER
    BUTTON_SECONDARY_PRESSED = LightColors.BUTTON_SECONDARY_PRESSED
    SUCCESS = LightColors.SUCCESS
    WARNING = LightColors.WARNING
    ERROR = LightColors.ERROR
    INFO = LightColors.INFO

    @classmethod
    def set_theme(cls, theme_name: str):
        """Set the current theme and update all color attributes."""
        cls._current_theme = theme_name.lower()
        color_class = DarkColors if cls._current_theme == "dark" else LightColors

        # Update all color attributes
        cls.PRIMARY = color_class.PRIMARY
        cls.SECONDARY = color_class.SECONDARY
        cls.ACCENT = color_class.ACCENT
        cls.BACKGROUND = color_class.BACKGROUND
        cls.WINDOW_BACKGROUND = color_class.WINDOW_BACKGROUND
        cls.DIALOG_BACKGROUND = color_class.DIALOG_BACKGROUND
        cls.TEXT_PRIMARY = color_class.TEXT_PRIMARY
        cls.TEXT_SECONDARY = color_class.TEXT_SECONDARY
        cls.TEXT_DISABLED = color_class.TEXT_DISABLED
        cls.BUTTON_PRIMARY = color_class.BUTTON_PRIMARY
        cls.BUTTON_PRIMARY_HOVER = color_class.BUTTON_PRIMARY_HOVER
        cls.BUTTON_PRIMARY_PRESSED = color_class.BUTTON_PRIMARY_PRESSED
        cls.BUTTON_SECONDARY = color_class.BUTTON_SECONDARY
        cls.BUTTON_SECONDARY_HOVER = color_class.BUTTON_SECONDARY_HOVER
        cls.BUTTON_SECONDARY_PRESSED = color_class.BUTTON_SECONDARY_PRESSED
        cls.SUCCESS = color_class.SUCCESS
        cls.WARNING = color_class.WARNING
        cls.ERROR = color_class.ERROR
        cls.INFO = color_class.INFO

    @classmethod
    def get_theme(cls) -> str:
        """Get the current theme."""
        return cls._current_theme

    @classmethod
    def _get_color_class(cls):
        """Get the appropriate color class based on current theme."""
        return DarkColors if cls._current_theme == "dark" else LightColors


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


# ---------------------------------------------------------------------------
# P1-C02 — Typography class (spec §4.2.1)
# ---------------------------------------------------------------------------


class Typography:
    """Spec-compliant typography building blocks (spec §4.2.1).

    All methods return a QFont configured with "Segoe UI" and the correct
    size / weight.  Use these instead of bare QFont() calls in tool widgets.
    ``Fonts`` is kept below for backward compatibility.
    """

    _FAMILY = "Segoe UI"

    @classmethod
    def h1(cls) -> QFont:
        """18 pt Bold — primary heading."""
        f = QFont(cls._FAMILY)
        f.setPointSize(18)
        f.setWeight(QFont.Bold)
        return f

    @classmethod
    def h2(cls) -> QFont:
        """14 pt Bold — section heading."""
        f = QFont(cls._FAMILY)
        f.setPointSize(14)
        f.setWeight(QFont.Bold)
        return f

    @classmethod
    def h3(cls) -> QFont:
        """12 pt DemiBold — sub-section heading."""
        f = QFont(cls._FAMILY)
        f.setPointSize(12)
        f.setWeight(QFont.DemiBold)
        return f

    @classmethod
    def body(cls) -> QFont:
        """10 pt Regular — body text."""
        f = QFont(cls._FAMILY)
        f.setPointSize(10)
        f.setWeight(QFont.Normal)
        return f

    @classmethod
    def caption(cls) -> QFont:
        """8 pt Regular — caption / helper text."""
        f = QFont(cls._FAMILY)
        f.setPointSize(8)
        f.setWeight(QFont.Normal)
        return f

    @classmethod
    def monospace(cls) -> QFont:
        """9 pt Regular — monospace for log viewers and code widgets."""
        f = QFont("Consolas")
        f.setPointSize(9)
        f.setWeight(QFont.Normal)
        return f


# ---------------------------------------------------------------------------
# P1-C01 — Token system (spec §4.1.2)
# ---------------------------------------------------------------------------

TOKENS: dict = {
    "light": {
        # Core palette
        "primary": LightColors.PRIMARY,
        "secondary": LightColors.SECONDARY,
        "accent": LightColors.ACCENT,
        "background": LightColors.BACKGROUND,
        "window_background": LightColors.WINDOW_BACKGROUND,
        "dialog_background": LightColors.DIALOG_BACKGROUND,
        "text_primary": LightColors.TEXT_PRIMARY,
        "text_secondary": LightColors.TEXT_SECONDARY,
        "text_disabled": LightColors.TEXT_DISABLED,
        # Buttons
        "button_primary": LightColors.BUTTON_PRIMARY,
        "button_primary_hover": LightColors.BUTTON_PRIMARY_HOVER,
        "button_primary_pressed": LightColors.BUTTON_PRIMARY_PRESSED,
        "button_secondary": LightColors.BUTTON_SECONDARY,
        "button_secondary_hover": LightColors.BUTTON_SECONDARY_HOVER,
        "button_secondary_pressed": LightColors.BUTTON_SECONDARY_PRESSED,
        # Semantic (constitutional reserved token keys)
        "semantic_success": LightColors.SUCCESS,
        "semantic_warning": LightColors.WARNING,
        "semantic_error": LightColors.ERROR,
        "semantic_info": LightColors.INFO,
        # Extended palette — Phase 3 TH tool migration tokens
        "text_muted": "#666666",
        "border": "#CCCCCC",
        "border_light": "#DEE2E6",
        "surface": "#F5F5F5",
        "surface_error": "#FFEAEA",
        "surface_warning": "#FFF2E8",
        "surface_info": "#E8F4FD",
        "text_error": "#C0392B",  # Dark red — 9.2:1 on surface_error; WCAG AA text ✓
        # Phase 3 TH — additional tool colour tokens
        "text_on_primary": "#FFFFFF",
        "color_black": "#000000",
        "color_action_blue": "#106EBE",
        "color_bg_tint": "#E9ECEF",
        "color_bg_subtle": "#F1F2F6",
        "semantic_success_hover": "#2ECC71",
        "semantic_warning_hover": "#F7A41E",
        "accent_light": "#4DA6E5",
        "color_surface_success": "#E8F5E8",
        "color_priority_high": "#F57C00",
        "color_priority_medium": "#FBC02D",
        "color_priority_low": "#388E3C",
        "color_amber": "#FFC107",
        "color_text_darkest": "#212121",
        "color_purple": "#9C27B0",
        "color_purple_dark": "#7B1FA2",
        "color_deep_orange": "#FF5722",
        "color_deep_orange_dark": "#E64A19",
        "color_blue_grey": "#607D8B",
        "color_blue_grey_dark": "#455A64",
        "color_grey_medium": "#5A6268",
        "color_navy_dark": "#004085",
        "color_orange_red": "#FF6B35",
        "color_orange_red_dark": "#E55A2B",
        "color_orange_red_darker": "#CC4F26",
        "color_green_deep": "#1E8449",
        "color_orange_badge": "#FD7E14",
        "color_warning_dark": "#D35400",
        # Hub nav — reserved; MUST NOT be used by tool UIs (spec §4.1.2)
        "hub_nav_background": "#1A252F",
        "hub_nav_foreground": "#ECF0F1",
        "hub_nav_accent": "#3498DB",
        "hub_nav_border": "#0D1B2A",
    },
    "dark": {
        # Core palette
        "primary": DarkColors.PRIMARY,
        "secondary": DarkColors.SECONDARY,
        "accent": DarkColors.ACCENT,
        "background": DarkColors.BACKGROUND,
        "window_background": DarkColors.WINDOW_BACKGROUND,
        "dialog_background": DarkColors.DIALOG_BACKGROUND,
        "text_primary": DarkColors.TEXT_PRIMARY,
        "text_secondary": DarkColors.TEXT_SECONDARY,
        "text_disabled": DarkColors.TEXT_DISABLED,
        # Buttons
        "button_primary": DarkColors.BUTTON_PRIMARY,
        "button_primary_hover": DarkColors.BUTTON_PRIMARY_HOVER,
        "button_primary_pressed": DarkColors.BUTTON_PRIMARY_PRESSED,
        "button_secondary": DarkColors.BUTTON_SECONDARY,
        "button_secondary_hover": DarkColors.BUTTON_SECONDARY_HOVER,
        "button_secondary_pressed": DarkColors.BUTTON_SECONDARY_PRESSED,
        # Semantic
        "semantic_success": DarkColors.SUCCESS,
        "semantic_warning": DarkColors.WARNING,
        "semantic_error": DarkColors.ERROR,
        "semantic_info": DarkColors.INFO,
        # Extended palette — Phase 3 TH tool migration tokens
        "text_muted": "#B5BFC8",  # A11Y-7b: was #A0A0A0, lightened to pass WCAG AA 4.5:1 on dark backgrounds
        "border": "#4A5A6C",
        "border_light": "#3A4A5C",
        "surface": "#2C3E50",
        "surface_error": "#5C2828",
        "surface_warning": "#5C4A28",
        "surface_info": "#28445C",
        "text_error": "#FFCDD2",  # Light red — 6.8:1 on dark surface_error; WCAG AA text ✓
        # Phase 3 TH — additional tool colour tokens
        "text_on_primary": "#FFFFFF",
        "color_black": "#000000",
        "color_action_blue": "#4DA6E5",
        "color_bg_tint": "#3A4A5C",
        "color_bg_subtle": "#2C3E50",
        "semantic_success_hover": "#58D68D",
        "semantic_warning_hover": "#F7DC6F",
        "accent_light": "#7FB3D3",
        "color_surface_success": "#1A3A1E",
        "color_priority_high": "#E65100",
        "color_priority_medium": "#F9A825",
        "color_priority_low": "#2E7D32",
        "color_amber": "#FFD600",
        "color_text_darkest": "#EEEEEE",
        "color_purple": "#BA68C8",
        "color_purple_dark": "#9C27B0",
        "color_deep_orange": "#FF7043",
        "color_deep_orange_dark": "#F4511E",
        "color_blue_grey": "#78909C",
        "color_blue_grey_dark": "#546E7A",
        "color_grey_medium": "#8A9299",
        "color_navy_dark": "#1A3A6A",
        "color_orange_red": "#FF8A65",
        "color_orange_red_dark": "#F4511E",
        "color_orange_red_darker": "#D84315",
        "color_green_deep": "#27AE60",
        "color_orange_badge": "#FF9800",
        "color_warning_dark": "#E65100",
        # Hub nav — reserved
        "hub_nav_background": "#0D1B2A",
        "hub_nav_foreground": "#BDC3C7",
        "hub_nav_accent": "#5DADE2",
        "hub_nav_border": "#070F18",
    },
}

# Active variant — mutated only by apply_theme()
_active_variant: str = "light"


def token(key: str) -> str:
    """Return the color value for *key* in the currently active theme variant.

    Raises ``KeyError`` if the key is not in the token registry.
    """
    return TOKENS[_active_variant][key]


def apply_theme(variant: str) -> None:
    """Switch the active theme variant and synchronise the ``Colors`` class.

    Args:
        variant: ``"light"`` or ``"dark"``
    """
    global _active_variant
    _active_variant = variant.lower()
    Colors.set_theme(_active_variant)
    # Notify registered callbacks so live widgets can re-render
    for _cb in ThemeManager._theme_changed_callbacks:
        try:
            _cb(_active_variant)
        except Exception as _e:
            print(f"Error in theme change callback: {_e}")


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
    def main_window(self):
        return self.get_main_window_style()

    # Keep legacy MAIN_WINDOW for backward compatibility
    @property
    def main_window_legacy(self):
        return self.get_main_window_style()

    @property
    def primary_button(self):
        return self.get_primary_button_style()

    # Keep legacy PRIMARY_BUTTON for backward compatibility
    @property
    def primary_button_legacy(self):
        return self.get_primary_button_style()

    @property
    def secondary_button(self):
        return self.get_secondary_button_style()

    # Keep legacy SECONDARY_BUTTON for backward compatibility
    @property
    def secondary_button_legacy(self):
        return self.get_secondary_button_style()

    @property
    def input_field(self):
        return self.get_input_field_style()

    # Keep legacy INPUT_FIELD for backward compatibility
    @property
    def input_field_legacy(self):
        return self.get_input_field_style()

    @property
    def label(self):
        return self.get_label_style()

    # Keep legacy LABEL for backward compatibility
    @property
    def label_legacy(self):
        return self.get_label_style()

    @property
    def header_label(self):
        return self.get_header_label_style()

    # Keep legacy HEADER_LABEL for backward compatibility
    @property
    def header_label_legacy(self):
        return self.get_header_label_style()

    @property
    def group_box(self):
        return self.get_group_box_style()

    # Keep legacy GROUP_BOX for backward compatibility
    @property
    def group_box_legacy(self):
        return self.get_group_box_style()

    @property
    def progress_bar(self):
        return self.get_progress_bar_style()

    # Keep legacy PROGRESS_BAR for backward compatibility
    @property
    def progress_bar_legacy(self):
        return self.get_progress_bar_style()


# Utility functions
class _ThemeManagerSignals(QObject):
    """QObject carrier for ThemeManager signals (T042)."""

    uap_font_changed = pyqtSignal(str, int)
    uap_geometry_changed = pyqtSignal(int, int, int, int)
    theme_changed = pyqtSignal(str)


class ThemeManager:
    """Manager for applying themes consistently and dynamically (T042-T043)."""

    _instance: "_ThemeManagerSignals | None" = None
    _theme_changed_callbacks: List[Callable] = []

    @classmethod
    def instance(cls) -> "_ThemeManagerSignals":
        """Return the singleton QObject signals carrier (T043)."""
        if cls._instance is None:
            cls._instance = _ThemeManagerSignals()
        return cls._instance

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
        global _active_variant
        _active_variant = theme_name.lower()
        Colors.set_theme(theme_name)

        # Notify all callbacks about theme change
        for callback in cls._theme_changed_callbacks:
            try:
                callback(theme_name)
            except Exception as e:
                print(f"Error in theme change callback: {e}")
        # Emit QObject signal (T042)
        cls.instance().theme_changed.emit(theme_name)

    @classmethod
    def get_current_theme(cls) -> str:
        """Get the current theme."""
        return Colors.get_theme()

    @staticmethod
    def apply_main_window_theme(window):
        """Apply main window theme to a QMainWindow."""
        window.setStyleSheet(Styles.get_main_window_style())
        window.setMinimumSize(
            Dimensions.MAIN_WINDOW_MIN_WIDTH, Dimensions.MAIN_WINDOW_MIN_HEIGHT
        )

    @staticmethod
    def apply_utility_window_theme(window):
        """Apply utility window theme to a QDialog or QWidget."""
        window.setStyleSheet(Styles.get_main_window_style())
        window.setMinimumSize(
            Dimensions.UTILITY_WINDOW_MIN_WIDTH,
            Dimensions.UTILITY_WINDOW_MIN_HEIGHT,
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
            if not hasattr(widget, "setStyleSheet"):
                return

            if widget_type != "default":
                ThemeManager._apply_explicit_widget_style(widget, widget_type)
            else:
                ThemeManager._apply_inferred_widget_style(widget)

        except Exception as e:
            print(f"Error applying theme to widget {widget}: {e}")

    @staticmethod
    def _apply_explicit_widget_style(widget, widget_type):
        """Apply styling based on explicit widget type."""
        widget_type_handlers = {
            "tree": ThemeManager.style_tree_widget,
            "frame": ThemeManager.style_frame,
            "combo": ThemeManager.style_combo_box,
            "input": ThemeManager.style_input_field,
            "button_primary": ThemeManager.style_primary_button,
            "button_secondary": ThemeManager.style_secondary_button,
            "label": ThemeManager.style_label,
            "group": ThemeManager.style_group_box,
            "progress": ThemeManager.style_progress_bar,
        }

        handler = widget_type_handlers.get(widget_type)
        if handler:
            handler(widget)

    @staticmethod
    def _apply_inferred_widget_style(widget):
        """Apply styling based on inferred widget class."""
        widget_class = widget.__class__.__name__

        class_handlers = {
            "TreeWidget": ThemeManager.style_tree_widget,
            "Frame": ThemeManager.style_frame,
            "ComboBox": ThemeManager.style_combo_box,
            "Button": ThemeManager.style_primary_button,
            "Label": ThemeManager.style_label,
            "GroupBox": ThemeManager.style_group_box,
            "ProgressBar": ThemeManager.style_progress_bar,
        }

        # Handle exact matches first
        handler = class_handlers.get(widget_class)
        if handler:
            handler(widget)
            return

        # Handle partial matches
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

    @staticmethod
    def apply_dialog_theme(dialog):
        """Apply consistent theme styling to a QDialog."""
        dialog.setStyleSheet(Styles.get_main_window_style())

    @staticmethod
    def create_standard_layout(parent=None):
        """Create a standard layout with consistent spacing."""
        try:
            from PyQt5.QtWidgets import QVBoxLayout

            layout = QVBoxLayout(parent)
            layout.setContentsMargins(
                Spacing.WINDOW_MARGIN,
                Spacing.WINDOW_MARGIN,
                Spacing.WINDOW_MARGIN,
                Spacing.WINDOW_MARGIN,
            )
            layout.setSpacing(Spacing.LARGE_SPACING)

            return layout
        except ImportError:
            # Return None if PyQt5 not available
            return None


# Initialize current theme from preferences if available (best effort)
try:  # pragma: no cover - optional integration
    from src.core.preferences.manager import PreferenceManager

    _pm = PreferenceManager()
    _initial_theme = _pm.get_theme(default=Colors.get_theme())
    Colors.set_theme(_initial_theme)
except Exception:
    # Prefer silent fallback to default theme on any import/DB errors
    pass
