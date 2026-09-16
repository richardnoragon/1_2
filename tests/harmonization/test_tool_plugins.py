import json

import pytest

from src.core.tool_manifest import ToolManifestRegistry
from src.core.tool_plugins import load_manifest


@pytest.fixture(autouse=True)
def restore_registry():
    entries = ToolManifestRegistry.all()
    yield
    ToolManifestRegistry.clear()
    for entry in entries:
        ToolManifestRegistry.register(entry)


def manifest(tmp_path, rows):
    path = tmp_path / "plugin.json"
    path.write_text(json.dumps({"schema_version": 1, "tools": rows}))
    return path


def tool(tool_id="example-plugin"):
    return dict(tool_id=tool_id, display_name=tool_id, module_path="example_not_imported.gui",
                class_name="Window", category="analysis")


def test_registration_is_lazy_and_resolves_for_launcher(tmp_path):
    from src.core.tool_lifecycle import resolve_tool_launch_request
    load_manifest(manifest(tmp_path, [tool()]))
    request = resolve_tool_launch_request("Example Plugin")
    assert request.module_name == "example_not_imported.gui"
    assert request.class_name == "Window"


def test_rejects_entire_manifest_before_partial_registration(tmp_path):
    bad = tool("second-plugin")
    bad["min_window_width"] = True
    with pytest.raises(ValueError):
        load_manifest(manifest(tmp_path, [tool(), bad]))
    assert ToolManifestRegistry.get("example-plugin") is None


def test_cannot_shadow_builtin_by_display_alias(tmp_path):
    row = tool()
    row["display_name"] = "Size Analyzer"
    with pytest.raises(ValueError, match="conflicts"):
        load_manifest(manifest(tmp_path, [row]))


def test_duplicate_aliases_in_manifest_are_atomic(tmp_path):
    with pytest.raises(ValueError, match="conflicts"):
        load_manifest(manifest(tmp_path, [tool(), tool()]))
    assert ToolManifestRegistry.get("example-plugin") is None


def test_plugin_contracts_validate_before_registration(tmp_path):
    row = tool()
    row['commands'] = [{'id': 'inspect', 'label': '&Inspect', 'menu': 'Tools',
                        'shortcut': 'Ctrl+Alt+I', 'method': 'inspect'}]
    row['preferences'] = {'schema_version': 1, 'fields': {'enabled': {'type': 'boolean', 'default': True}}}
    row['telemetry'] = {'inspected': {'count': 'integer'}}
    row['preferences']['fields']['enabled']['default'] = 'true'
    with pytest.raises(ValueError):
        load_manifest(manifest(tmp_path, [row]))
    assert ToolManifestRegistry.get(row['tool_id']) is None


def test_plugin_declared_command_preferences_and_telemetry(qapp, tmp_path, monkeypatch):
    from PyQt5.QtWidgets import QMainWindow, QWidget
    from src.gui.menu_registry import MenuRegistry
    from src.core.plugin_contracts import install_contracts
    row = tool()
    row['commands'] = [{'id': 'inspect', 'label': '&Inspect', 'menu': 'Tools',
                        'shortcut': 'Ctrl+Alt+I', 'method': 'inspect'}]
    row['preferences'] = {'schema_version': 1, 'fields': {'enabled': {'type': 'boolean', 'default': True}}}
    row['telemetry'] = {'inspected': {'count': 'integer'}}
    entry = load_manifest(manifest(tmp_path, [row]))[0]
    window = QMainWindow()
    window.menu_registry = MenuRegistry(window)
    widget = QWidget()
    calls = []
    widget.inspect = lambda: calls.append('inspect')
    install_contracts(window, widget, entry)
    window.menu_registry.menus['Tools'].actions()[0].trigger()
    assert calls == ['inspect']
    services = widget.plugin_services
    assert services.load_preferences() == {'enabled': True}
    services.save_preferences({'enabled': False})
    assert services.load_preferences() == {'enabled': False}
    with pytest.raises(ValueError):
        services.save_preferences({'enabled': 0})
    with pytest.raises(ValueError):
        services.emit_event('inspected', count='1')
    events = []
    monkeypatch.setattr('src.gui.telemetry.emit_telemetry', lambda *args, **kw: events.append(kw))
    services.emit_event('inspected', count=1)
    assert events[-1]['plugin_fields'] == {'count': 1}
    assert len(ToolManifestRegistry.builtins()) == 36
    window.close()
