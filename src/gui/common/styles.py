"""Centralized UI style definitions for shared GUI surfaces.

This module exposes token-driven palettes and stylesheet builders used by
hub/dialog/common windows, plus accessibility checks for contrast.
"""

from __future__ import annotations

from enum import Enum
from typing import Dict, Iterable, List, Tuple


class Theme(Enum):
    """Available themes for shared GUI surfaces."""

    LIGHT = "light"
    DARK = "dark"


_THEME_TOKENS: Dict[Theme, Dict[str, str]] = {
    Theme.LIGHT: {
        "window_bg": "#F4F6F8",
        "widget_bg": "#FFFFFF",
        "surface_subtle": "#EAEFF3",
        "primary": "#0B5ED7",
        "primary_hover": "#094BB1",
        "primary_pressed": "#073C8F",
        "focus_ring": "#0A84FF",
        "success": "#1B8A5A",
        "success_hover": "#16724A",
        "warning": "#A56A00",
        "error": "#C62828",
        "text": "#1E2430",
        "text_secondary": "#4B5565",
        "text_on_primary": "#FFFFFF",
        "border": "#C6CFD9",
        "separator": "#D7DEE6",
        "disabled": "#A3AFBC",
        "highlight": "#CCE3FF",
        "selection_text": "#0F1720",
    },
    Theme.DARK: {
        "window_bg": "#1D2633",
        "widget_bg": "#233041",
        "surface_subtle": "#2B394D",
        "primary": "#5AA6FF",
        "primary_hover": "#82BBFF",
        "primary_pressed": "#3C90F5",
        "focus_ring": "#8CC4FF",
        "success": "#58C89B",
        "success_hover": "#74D4AD",
        "warning": "#FFCB6B",
        "error": "#FF8A80",
        "text": "#F3F6FA",
        "text_secondary": "#C3CDD8",
        "text_on_primary": "#0F1720",
        "border": "#475569",
        "separator": "#3B4A5E",
        "disabled": "#7B8795",
        "highlight": "#36557A",
        "selection_text": "#F3F6FA",
    },
}


def get_theme_tokens(theme: Theme = Theme.LIGHT) -> Dict[str, str]:
    """Return a copy of token values for the requested theme."""

    return dict(_THEME_TOKENS[theme])


def _clamp_scale(ui_scale: float) -> float:
    try:
        value = float(ui_scale)
    except (TypeError, ValueError):
        return 1.0
    return max(0.8, min(value, 2.0))


def _scaled(font_size: int, ui_scale: float) -> int:
    return max(8, int(round(font_size * _clamp_scale(ui_scale))))


def get_base_styles(
    theme: Theme = Theme.LIGHT,
    font_size: int = 12,
    ui_scale: float = 1.0,
) -> str:
    """Build the shared token-driven stylesheet.

    The stylesheet includes explicit keyboard focus styles and larger control
    targets to improve accessibility consistency across windows and dialogs.
    """

    colors = get_theme_tokens(theme)
    fs = _scaled(font_size, ui_scale)
    control_min_height = max(30, _scaled(30, ui_scale))
    input_padding_v = max(4, _scaled(5, ui_scale))
    input_padding_h = max(6, _scaled(8, ui_scale))

    return f"""
        QMainWindow, QDialog, QWidget {{
            background-color: {colors['window_bg']};
            color: {colors['text']};
        }}

        QLabel {{
            color: {colors['text']};
            font-size: {fs}pt;
        }}

        QPushButton {{
            background-color: {colors['primary']};
            color: {colors['text_on_primary']};
            border: 1px solid {colors['primary']};
            border-radius: 6px;
            padding: {input_padding_v}px {input_padding_h * 2}px;
            min-height: {control_min_height}px;
            font-size: {fs}pt;
            font-weight: 600;
        }}

        QPushButton:hover {{
            background-color: {colors['primary_hover']};
            border-color: {colors['primary_hover']};
        }}

        QPushButton:pressed {{
            background-color: {colors['primary_pressed']};
            border-color: {colors['primary_pressed']};
        }}

        QPushButton:disabled {{
            background-color: {colors['disabled']};
            border-color: {colors['disabled']};
            color: {colors['text_on_primary']};
        }}

        QPushButton[success="true"] {{
            background-color: {colors['success']};
            border-color: {colors['success']};
        }}

        QPushButton[success="true"]:hover {{
            background-color: {colors['success_hover']};
            border-color: {colors['success_hover']};
        }}

        QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QSpinBox,
        QDoubleSpinBox, QDateTimeEdit {{
            background-color: {colors['widget_bg']};
            color: {colors['text']};
            border: 1px solid {colors['border']};
            border-radius: 6px;
            padding: {input_padding_v}px {input_padding_h}px;
            min-height: {control_min_height}px;
            font-size: {fs}pt;
            selection-background-color: {colors['highlight']};
            selection-color: {colors['selection_text']};
        }}

        QListView, QTreeView, QTableView {{
            background-color: {colors['widget_bg']};
            color: {colors['text']};
            border: 1px solid {colors['border']};
            border-radius: 6px;
            font-size: {fs}pt;
            selection-background-color: {colors['highlight']};
            selection-color: {colors['selection_text']};
        }}

        QGroupBox {{
            background-color: {colors['widget_bg']};
            color: {colors['text']};
            border: 1px solid {colors['border']};
            border-radius: 6px;
            margin-top: 1.5ex;
            padding-top: {input_padding_v}px;
            font-size: {fs}pt;
            font-weight: 600;
        }}

        QCheckBox, QRadioButton {{
            color: {colors['text']};
            spacing: {max(6, _scaled(6, ui_scale))}px;
            font-size: {fs}pt;
        }}

        QProgressBar {{
            background-color: {colors['surface_subtle']};
            color: {colors['text']};
            border: 1px solid {colors['border']};
            border-radius: 6px;
            text-align: center;
            min-height: {max(20, _scaled(20, ui_scale))}px;
            font-size: {fs}pt;
        }}

        QProgressBar::chunk {{
            background-color: {colors['primary']};
            border-radius: 5px;
        }}

        QStatusBar {{
            background-color: {colors['window_bg']};
            color: {colors['text']};
            border-top: 1px solid {colors['separator']};
        }}

        QMenuBar {{
            background-color: {colors['window_bg']};
            color: {colors['text']};
            border-bottom: 1px solid {colors['separator']};
        }}

        QMenuBar::item:selected,
        QMenu::item:selected,
        QTabBar::tab:selected {{
            background-color: {colors['highlight']};
            color: {colors['selection_text']};
        }}

        QMenu {{
            background-color: {colors['widget_bg']};
            color: {colors['text']};
            border: 1px solid {colors['border']};
        }}

        QTabWidget::pane {{
            border: 1px solid {colors['border']};
            border-radius: 6px;
            background-color: {colors['widget_bg']};
        }}

        QTabBar::tab {{
            background-color: {colors['window_bg']};
            color: {colors['text']};
            border: 1px solid {colors['border']};
            border-bottom: none;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            padding: {input_padding_v}px {input_padding_h * 2}px;
            min-height: {control_min_height}px;
            font-size: {fs}pt;
        }}

        QScrollBar:vertical, QScrollBar:horizontal {{
            background-color: {colors['window_bg']};
        }}

        QScrollBar::handle:vertical,
        QScrollBar::handle:horizontal {{
            background-color: {colors['primary']};
            border-radius: 6px;
        }}

        /* Keyboard focus visibility across shared controls */
        QWidget:focus {{
            outline: 2px solid {colors['focus_ring']};
            outline-offset: 1px;
        }}

        QPushButton:focus,
        QLineEdit:focus,
        QTextEdit:focus,
        QPlainTextEdit:focus,
        QComboBox:focus,
        QSpinBox:focus,
        QDoubleSpinBox:focus,
        QDateTimeEdit:focus,
        QCheckBox:focus,
        QRadioButton:focus,
        QListView:focus,
        QTreeView:focus,
        QTableView:focus,
        QTabBar::tab:focus {{
            border: 2px solid {colors['focus_ring']};
        }}
    """


def get_custom_styles() -> Dict[str, str]:
    """Return component-specific style augmentations."""

    return {
        "ProgressWidget": """
            QProgressBar {
                max-height: 18px;
                border-radius: 9px;
            }
            QProgressBar::chunk {
                border-radius: 8px;
            }
        """,
        "FileOperationWindow": """
            QListView {
                min-height: 220px;
            }
            QProgressBar {
                margin: 10px 0;
            }
        """,
    }


def _hex_to_rgb(color_hex: str) -> Tuple[float, float, float]:
    hex_value = color_hex.lstrip("#")
    if len(hex_value) != 6:
        raise ValueError(f"Expected #RRGGBB color, got {color_hex!r}")
    r = int(hex_value[0:2], 16) / 255.0
    g = int(hex_value[2:4], 16) / 255.0
    b = int(hex_value[4:6], 16) / 255.0
    return r, g, b


def _luminance_channel(channel: float) -> float:
    if channel <= 0.03928:
        return channel / 12.92
    return ((channel + 0.055) / 1.055) ** 2.4


def contrast_ratio(foreground_hex: str, background_hex: str) -> float:
    """Compute WCAG contrast ratio for two hex colors."""

    fr, fg, fb = _hex_to_rgb(foreground_hex)
    br, bg, bb = _hex_to_rgb(background_hex)

    lum_foreground = (
        0.2126 * _luminance_channel(fr)
        + 0.7152 * _luminance_channel(fg)
        + 0.0722 * _luminance_channel(fb)
    )
    lum_background = (
        0.2126 * _luminance_channel(br)
        + 0.7152 * _luminance_channel(bg)
        + 0.0722 * _luminance_channel(bb)
    )

    lighter = max(lum_foreground, lum_background)
    darker = min(lum_foreground, lum_background)
    return (lighter + 0.05) / (darker + 0.05)


def validate_theme_contrast(
    theme: Theme,
    *,
    min_ratio: float = 4.5,
    pairs: Iterable[Tuple[str, str]] | None = None,
) -> List[str]:
    """Validate token pairs against the minimum contrast ratio.

    Returns a list of failures in the format:
    "token_a/token_b=3.98 < 4.50"
    """

    tokens = get_theme_tokens(theme)
    checks = list(
        pairs
        or [
            ("text", "window_bg"),
            ("text", "widget_bg"),
            ("text_secondary", "window_bg"),
            ("text_on_primary", "primary"),
            ("selection_text", "highlight"),
        ]
    )

    failures: List[str] = []
    for fg_key, bg_key in checks:
        ratio = contrast_ratio(tokens[fg_key], tokens[bg_key])
        if ratio < min_ratio:
            failures.append(f"{fg_key}/{bg_key}={ratio:.2f} < {min_ratio:.2f}")

    return failures


def is_theme_accessible(theme: Theme, *, min_ratio: float = 4.5) -> bool:
    """Return True when all required contrast checks pass."""

    return not validate_theme_contrast(theme, min_ratio=min_ratio)
