import time
from threading import Event

from PyQt5.QtCore import QTimer
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QUndoCommand, QUndoStack

from src.gui.file_workflow_dialog import FileWorkflowDialog
from src.gui.menu_registry import MenuRegistry
from src.gui.undo_history import install_undo_history


def wait_until(qapp, condition, timeout=3):
    deadline = time.monotonic() + timeout
    while not condition() and time.monotonic() < deadline:
        QTest.qWait(10)
    assert condition()


def test_file_workflow_gui_export(qapp, tmp_path, monkeypatch):
    source = tmp_path / "input"
    source.mkdir()
    (source / "file.txt").write_text("example")
    target = tmp_path / "report.csv"
    monkeypatch.setattr(QFileDialog, "getExistingDirectory", lambda *a: str(source))
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *a: (str(target), ""))
    dialog = FileWorkflowDialog()
    dialog.show()
    dialog.choose_folder()
    assert not dialog.inspect.isEnabled()
    wait_until(qapp, lambda: dialog._job is None)
    assert dialog.export.isEnabled()
    assert dialog.records[0].path == "file.txt"
    dialog.export_results()
    wait_until(qapp, lambda: dialog._job is None)
    assert "SHA-256" in target.read_text()
    dialog.close()


def test_worker_keeps_ui_responsive_and_close_cancels(qapp):
    dialog = FileWorkflowDialog()
    dialog.show()
    heartbeats = []
    timer = QTimer()
    timer.timeout.connect(lambda: heartbeats.append(time.monotonic()))
    timer.start(10)
    started, finished = Event(), Event()
    def work():
        started.set()
        dialog._cancel.wait(5)
        finished.set()
        return []
    try:
        dialog._start(work, dialog._inspected)
        # Native window managers may coalesce timer ticks during first paint.
        # Require actual GUI events while the worker is demonstrably still active.
        wait_until(qapp, lambda: started.is_set() and len(heartbeats) >= 2)
        assert not finished.is_set() and dialog._job is not None
        dialog.close()
        assert dialog._cancel.is_set()
        wait_until(qapp, lambda: dialog._job is None)
        assert not dialog.isVisible()
    finally:
        dialog._cancel.set()
        timer.stop()
        dialog.close()


def test_undo_history_tracks_real_stack(qapp, monkeypatch):
    monkeypatch.setattr("src.gui.undo_history.emit_telemetry", lambda *a, **kw: None)
    window = QMainWindow()
    window.menu_registry = MenuRegistry(window)
    stack = QUndoStack(window)
    undo, redo, history = install_undo_history(window, stack, tool_id="test")
    value = []
    class Command(QUndoCommand):
        def redo(self):
            value.append(1)
        def undo(self):
            value.pop()
    assert not undo.isEnabled()
    stack.push(Command("Append"))
    assert value == [1]
    undo.trigger()
    assert not value
    assert redo.isEnabled()
    redo.trigger()
    assert value == [1]


def test_tool_navigation_and_editing_stay_with_tool(qapp, monkeypatch):
    from PyQt5.QtWidgets import QWidget
    from src.simple_menu_manager import SimpleMenuManager
    from src.tabbed_hub import UtilityWindow
    monkeypatch.setattr("src.gui.menu_registry.emit_telemetry", lambda *a, **kw: None)
    hub = QMainWindow()
    hub.menu_manager = SimpleMenuManager(hub)
    hub.menu_manager.create_menubar()
    calls = []
    hub.menu_manager.register_callback("undo", lambda: calls.append("hub"))
    class Tool(QWidget):
        def undo(self):
            calls.append("tool")
    window = UtilityWindow(hub, Tool(), "Example")
    window.menu_manager._handle_action("undo")
    assert calls == ["tool"]
    window.menu_manager._return_to_hub()
    assert hub.isVisible()
    hub.menu_manager._refresh_windows()
    assert any("Example" in a.text() for a in hub.menu_registry.menus["Window"].actions())
    window.close()
    hub.close()
