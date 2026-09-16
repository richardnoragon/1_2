import pytest

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QLabel, QMainWindow

from src.gui.menu_manager import MenuManager
from src.gui.menu_registry import MenuRegistry
from src.gui.components.toast import ToastNotification
from src.rfu import font_tokens


@pytest.fixture(autouse=True)
def telemetry(monkeypatch):
    monkeypatch.setattr("src.gui.menu_registry.emit_telemetry", lambda *a, **kw: None)


def test_menu_callback_registered_after_creation(qapp):
    window = QMainWindow()
    manager = MenuManager(window)
    manager.create_standard_menubar()
    calls = []
    manager.register_callback("open_file", lambda: calls.append("opened"))
    action = next(a for a in manager.file_menu.actions() if a.shortcut().toString() == "Ctrl+O")
    action.trigger()
    assert calls == ["opened"]
    window.close()


def test_registry_order_conflicts_conditions_and_removal(qapp):
    window = QMainWindow()
    registry = MenuRegistry(window)
    assert [a.text().replace("&", "") for a in window.menuBar().actions()] == list(registry.ORDER)
    assert not registry.menus["Reports"].menuAction().isVisible()
    calls = []
    state = {"enabled": False}
    action = registry.register(tool_id="test", menu="Reports", label="Menu.LOAD_PLUGIN",
                               accelerator="Ctrl+Shift+P", callback=lambda: calls.append(1),
                               enabled_condition=lambda: state["enabled"])
    assert registry.menus["Reports"].menuAction().isVisible()
    action.trigger()
    assert not calls
    with pytest.raises(ValueError, match="already assigned"):
        registry.register(tool_id="other", menu="Tools", label="Menu.LOAD_PLUGIN",
                          accelerator="Ctrl+Shift+P", callback=lambda: None)
    assert window.property("menuDegraded")
    assert registry.guardian.get_component_status(registry.guardian_id)["state"] in {"DEGRADED", "FAILED"}
    state["enabled"] = True
    registry.refresh()
    action.trigger()
    assert calls == [1]
    registry.deregister(tool_id="test")
    assert not registry.menus["Reports"].menuAction().isVisible()


def test_font_tokens_keep_ratios_and_update_live(qapp):
    original = QFont(qapp.font())
    label = QLabel()
    font_tokens.bind(label)
    assert label.font().pointSizeF() == 14
    assert font_tokens.get("font.caption").pointSizeF() == 12
    assert font_tokens.get("font.small").pointSizeF() == 11
    zoom = QFont(original)
    zoom.setPointSizeF(original.pointSizeF() * 2)
    try:
        qapp.setFont(zoom)
        qapp.processEvents()
        assert label.font().pointSizeF() == 28
        assert font_tokens.get("font.caption").pointSizeF() == 24
    finally:
        qapp.setFont(original)
        qapp.processEvents()


def test_toast_role_validation_and_accessibility(qapp):
    toast = ToastNotification()
    toast.show_message("Check the input", role="warning")
    assert toast.accessibleName() == "Warning notification"
    with pytest.raises(ValueError):
        toast.show_message("bad", role="unknown")
    assert toast.accessibleName() == "Warning notification"
    toast.close()


def test_appearance_profiles_preserve_font_hierarchy_and_minimums(qapp):
    window = QMainWindow()
    title = QLabel(window)
    caption = QLabel(window)
    font_tokens.bind(title, "font.toolHeader")
    font_tokens.bind(caption, "font.caption")
    font_tokens.apply_profile(window, "DejaVu Sans", 10)
    assert window.font().pointSizeF() == 14
    assert title.font().pointSizeF() == 18
    assert caption.font().pointSizeF() == 12
    font_tokens.apply_profile(window, "DejaVu Sans", 28)
    assert title.font().pointSizeF() == 36
    assert caption.font().pointSizeF() == 24


def test_hub_callback_aliases(qapp):
    from src.simple_menu_manager import SimpleMenuManager
    window = QMainWindow()
    manager = SimpleMenuManager(window)
    manager.create_menubar()
    calls = []
    manager.register_callback("show_preferences", lambda: calls.append(1))
    manager._handle_action("preferences")
    assert calls == [1]


def test_destructive_cancel_never_emits_accepted(qapp):
    from PyQt5.QtWidgets import QPushButton
    from src.gui.components.modal import ConfirmationModal
    dialog = ConfirmationModal("Delete", "Delete this file?", "Delete", "Cancel")
    accepted = []
    rejected = []
    dialog.accepted.connect(lambda: accepted.append(True))
    dialog.rejected.connect(lambda: rejected.append(True))
    cancel = next(button for button in dialog.findChildren(QPushButton) if button.text() == "Cancel")
    confirm = next(button for button in dialog.findChildren(QPushButton) if button.text() == "Delete")
    cancel.click()
    assert accepted == []
    assert rejected == [True]
    confirm.click()
    assert accepted == [True]


def test_menu_and_font_bindings_survive_window_collection(qapp):
    import gc
    for _ in range(20):
        window = QMainWindow()
        window.menu_registry = MenuRegistry(window)
        font_tokens.apply_profile(window, "DejaVu Sans", 14)
        window.close()
        del window
        gc.collect()
        qapp.processEvents()
