"""Shared construction for context menus and legacy tool submenus."""
from PyQt5.QtWidgets import QMenu, QMenuBar
from src.rfu import font_tokens
from src.rfu.localization import bind_text


def menu(*args, **kwargs):
    result = QMenu(*args, **kwargs)
    font_tokens.bind(result)
    if args and isinstance(args[0], str):
        bind_text(result, 'setTitle', args[0])
    return result


def menu_bar(*args, **kwargs):
    result = QMenuBar(*args, **kwargs)
    font_tokens.bind(result)
    return result


def add_menu(parent, *args):
    result = parent.addMenu(*args)
    # Qt returns QAction when an already constructed QMenu is supplied.
    target = result.menu() if hasattr(result, 'menu') else result
    if target is not None:
        font_tokens.bind(target)
        if args and isinstance(args[0], str):
            bind_text(target, 'setTitle', args[0])
    return result
