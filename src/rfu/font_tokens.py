"""Point-based typography tokens with live application-font scaling."""

from __future__ import annotations

import sys
import weakref
import math

from PyQt5.QtGui import QFont, QFontDatabase
from PyQt5.QtWidgets import QApplication

TOKENS = {
    "font.body": (14, QFont.Normal),
    "font.bodyBold": (14, QFont.Bold),
    "font.mono": (13, QFont.Normal),
    "font.caption": (12, QFont.Normal),
    "font.captionBold": (12, QFont.Bold),
    "font.title": (16, QFont.DemiBold),
    "font.toolHeader": (18, QFont.Bold),
    "font.small": (11, QFont.Normal),
}
FALLBACKS = {
    "win32": ("Segoe UI", "Arial"),
    "darwin": ("SF Pro Text", "Helvetica Neue", "Arial"),
    "linux": ("Noto Sans", "DejaVu Sans", "Liberation Sans"),
}
MONO_FALLBACKS = ("Cascadia Mono", "Consolas", "Menlo", "DejaVu Sans Mono")
_bindings = weakref.WeakKeyDictionary()
_observer = None
_base_size = None
_base_family = None


def _observe():
    global _observer, _base_size, _base_family
    app = QApplication.instance()
    if app is not None and (_observer is None or _observer() is not app):
        _base_size = app.font().pointSizeF()
        _base_family = app.font().family()
        _observer = weakref.ref(app)
        app.fontChanged.connect(reload)
    return app


def get(token_name: str, *, family=None, scale=1.0) -> QFont:
    """Return a fresh font; never shrink below the token's legibility floor."""
    size, weight = TOKENS[token_name]
    if not isinstance(scale, (int, float)) or not math.isfinite(scale) or scale <= 0:
        raise ValueError("Font scale must be positive and finite")
    profile_scale = max(1.0, scale)
    app = _observe()
    font = QFont()
    scale = 1.0
    if app is not None:
        available = set(QFontDatabase().families())
        candidates = MONO_FALLBACKS if token_name == "font.mono" else FALLBACKS.get(sys.platform, FALLBACKS["linux"])
        if token_name != "font.mono" and family:
            candidates = (family, *candidates)
        elif token_name != "font.mono" and app.font().family() != _base_family:
            candidates = (app.font().family(), *candidates)
        family = next((name for name in candidates if name in available), None)
        if family:
            font.setFamily(family)
        elif token_name == "font.mono":
            font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        else:
            font = QFont(app.font())
        if _base_size and _base_size > 0:
            scale = max(1.0, app.font().pointSizeF() / _base_size)
    font.setPointSizeF(size * scale * profile_scale)
    font.setWeight(weight)
    return font


def bind(widget, token_name="font.body"):
    """Apply a token and refresh this widget when accessibility font changes."""
    widget.setFont(_resolve_for_widget(widget, token_name))
    widget.setProperty("fontToken", token_name)
    _bindings[widget] = token_name


def _resolve_for_widget(widget, token_name):
    scope = widget
    while scope is not None:
        scale = scope.property("rfuFontScale")
        if scale is not None:
            return get(token_name, family=scope.property("rfuFontFamily"), scale=scale)
        scope = scope.parent()
    return get(token_name)


def apply_profile(window, family, body_size):
    """Apply UAP preferences while retaining token hierarchy and minimums."""
    from PyQt5.QtWidgets import QWidget
    window.setProperty("rfuFontScale", max(1.0, body_size / TOKENS["font.body"][0]))
    window.setProperty("rfuFontFamily", family)
    for widget in [window, *window.findChildren(QWidget)]:
        bind(widget, widget.property("fontToken") or "font.body")


def reload(*_):
    """Re-resolve live bindings following a theme or application-font change."""
    for widget, name in list(_bindings.items()):
        try:
            widget.setFont(_resolve_for_widget(widget, name))
        except RuntimeError:
            _bindings.pop(widget, None)
