"""Shared Undo/Redo actions and history view for tools using QUndoStack."""

from PyQt5.QtWidgets import QAction, QDialog, QUndoStack, QUndoView, QVBoxLayout

from src.gui.telemetry import emit_telemetry
from src.rfu.localization import service, tr


def install_undo_history(window, stack, *, tool_id):
    """Attach an existing tool's undo stack; do not invent reversibility."""
    if not isinstance(stack, QUndoStack):
        raise TypeError("Tools supporting undo must expose a QUndoStack")
    menu = window.menu_registry.menus["Edit"]
    for action in list(menu.actions()):
        if action.shortcut().toString() in {"Ctrl+Z", "Ctrl+Y", "Ctrl+Shift+Z"}:
            menu.removeAction(action)
            action.setShortcut("")
    undo = stack.createUndoAction(window, tr("Menu.EDIT_UNDO"))
    undo.setShortcut("Ctrl+Z")
    redo = stack.createRedoAction(window, tr("Menu.EDIT_REDO"))
    redo.setShortcut("Ctrl+Shift+Z")
    menu.insertAction(menu.actions()[0] if menu.actions() else None, redo)
    menu.insertAction(redo, undo)
    history = QAction(tr("Undo.HISTORY"), window)
    service.bind(history, "setText", "Undo.HISTORY")
    menu.addAction(history)

    def show_history():
        dialog = QDialog(window)
        service.bind(dialog, "setWindowTitle", "Undo.TITLE")
        layout = QVBoxLayout(dialog)
        view = QUndoView(stack, dialog)
        service.bind(view, "setAccessibleName", "Undo.TITLE")
        layout.addWidget(view)
        dialog.resize(450, 300)
        dialog.exec_()

    history.triggered.connect(show_history)
    def record_change(index):
        try:
            count = stack.count()
        except RuntimeError:  # QUndoStack can emit indexChanged while destructing.
            return
        emit_telemetry("ui_user_action", tool_id=tool_id, action="undo_stack_changed",
                       index=index, count=count, undo_supported=True)
    stack.indexChanged.connect(record_change)
    window.setProperty("undoSupported", True)
    return undo, redo, history
