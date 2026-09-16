import json
import time
import zipfile
from pathlib import Path
from threading import Event
from types import SimpleNamespace
import pytest
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLineEdit
from PyQt5.QtTest import QTest
from src.core.archive_operations import plan_compression, execute_compression, plan_extraction, execute_extraction
from src.core.workflows import WorkflowCancelled
from src.core.preferences.legacy_json import LegacyJSONPreferences


@pytest.mark.parametrize('format,suffix', [('ZIP','.zip'),('TAR.GZ','.tar.gz'),('TAR.BZ2','.tar.bz2')])
def test_archive_plan_apply_and_extract_preserve_input(tmp_path, format, suffix):
    source = tmp_path / 'source'
    source.mkdir()
    (source / 'empty').mkdir()
    (source / 'file.txt').write_text('sample content')
    output = tmp_path / ('archive' + suffix)
    plan = plan_compression(source, output, format)
    assert not output.exists()
    assert len(plan.members) == 2
    execute_compression(plan)
    destination = tmp_path / 'extracted'
    extract = plan_extraction(output, destination)
    assert not destination.exists()
    execute_extraction(extract)
    assert (destination / 'file.txt').read_text() == 'sample content'
    assert (destination / 'empty').is_dir()
    assert (source / 'file.txt').read_text() == 'sample content'
    with pytest.raises(FileExistsError):
        plan_extraction(output, destination)


@pytest.mark.parametrize('name', ['../outside', '/absolute', 'a\\..\\outside', 'C:/outside'])
def test_archive_rejects_unsafe_members_before_writes(tmp_path, name):
    archive = tmp_path / 'bad.zip'
    with zipfile.ZipFile(archive, 'w') as stream:
        stream.writestr(name, 'data')
    target = tmp_path / 'target'
    with pytest.raises(ValueError):
        plan_extraction(archive, target)
    assert not target.exists()


def test_archive_password_cancellation_and_changed_source(tmp_path):
    source = tmp_path / 'source'
    source.mkdir()
    file = source / 'file.txt'
    file.write_text('original')
    destination = tmp_path / 'archive.zip'
    with pytest.raises(ValueError, match='Password'):
        plan_compression(source, destination, password='secret')
    plan = plan_compression(source, destination)
    cancel = Event()
    cancel.set()
    with pytest.raises(WorkflowCancelled):
        execute_compression(plan, cancel)
    assert not destination.exists()
    file.write_text('changed content')
    with pytest.raises(OSError):
        execute_compression(plan)
    assert not destination.exists()


def test_legacy_json_import_is_atomic_and_native_file_is_retained(tmp_path):
    class Manager:
        def __init__(self): self.values = {}
        def get(self, c, k, default=None): return self.values.get((c,k),default)
        def set(self, c, k, v): self.values[c,k] = v
    path = tmp_path / 'settings.json'
    path.write_text(json.dumps({'security': {'confirm': False, 'passes': 5}}))
    before = path.read_bytes()
    manager = Manager()
    prefs = LegacyJSONPreferences('tool', {'security': {'confirm': True, 'passes': 3}}, manager=manager)
    values = prefs.load(path)
    assert values['security']['passes'] == 5
    with pytest.raises(ValueError):
        prefs.save({'security': {'confirm': 'false', 'passes': 5}})
    assert prefs.load(path) == values
    assert path.read_bytes() == before
    path.write_text('{}')
    assert prefs.load(path) == values  # Migration is one-way and only happens once.


def test_active_dispatch_preserves_tool_callbacks_and_focus(qapp):
    from src.gui.command_dispatch import CommandDispatcher
    from src.gui.menu_registry import MenuRegistry
    window = QMainWindow()
    owner = QWidget()
    layout = QVBoxLayout(owner)
    field = QLineEdit('example')
    layout.addWidget(field)
    window.setCentralWidget(owner)
    window.menu_registry = MenuRegistry(window)
    calls = []
    owner.menu_manager = SimpleNamespace(callbacks={'save_as_file': lambda: calls.append('save')})
    dispatcher = CommandDispatcher(window, owner, 'test')
    window.show()
    window.activateWindow()
    field.setFocus()
    QTest.qWait(20)
    field.selectAll()
    assert dispatcher.invoke('copy')
    assert qapp.clipboard().text() == 'example'
    assert dispatcher.invoke('save_as')
    assert calls == ['save']
    owner._job = object()
    assert not dispatcher.invoke('save_as')
    assert calls == ['save']
    window.close()


def test_guardian_fallback_retains_data_and_validates_recovery(qapp):
    from src.gui.tool_runtime import ToolRuntime
    from src.gui.menu_registry import MenuRegistry
    window, hub = QMainWindow(), QMainWindow()
    owner = QWidget()
    layout = QVBoxLayout(owner)
    field = QLineEdit('unsaved work')
    layout.addWidget(field)
    window.setCentralWidget(owner)
    window.menu_registry = MenuRegistry(window)
    state = {'healthy': True}
    owner.health_check = lambda: state['healthy']
    runtime = ToolRuntime(window, owner, SimpleNamespace(tool_id='test', display_name='Test'), hub)
    state['healthy'] = False
    assert not runtime.check_health()
    assert not owner.isEnabled()
    assert field.text() == 'unsaved work'
    runtime.retry()
    assert window.property('toolDegraded')
    state['healthy'] = True
    runtime.retry()
    assert not window.property('toolDegraded')
    assert owner.isEnabled()
    assert field.text() == 'unsaved work'
    state['healthy'] = False
    runtime.check_health()
    assert window.property('toolDegraded')
    window.close()
    hub.close()


def test_event_loop_budget_detects_blocking_callback(qapp):
    from src.gui.tool_runtime import UIThreadBudget
    window = QMainWindow()
    budget = UIThreadBudget(window, 'test')
    violations = []
    budget.exceeded.connect(violations.append)
    window.show()
    QTest.qWait(60)
    time.sleep(.13)
    QTest.qWait(30)
    assert violations and max(violations) >= 100
    window.close()


def test_permission_preview_preserves_other_bits_and_undo_detects_changes(tmp_path):
    import os
    import stat
    from src.core.permission_operations import plan_permissions, apply_permissions
    if os.name == 'nt':
        pytest.skip('POSIX mode semantics; Windows only supports the read-only flag')
    target = tmp_path / 'document'
    target.write_text('unchanged')
    target.chmod(0o654)
    plan = plan_permissions(target, 0o400)
    assert plan.after == 0o454
    assert stat.S_IMODE(target.stat().st_mode) == 0o654
    reverse = apply_permissions(plan)
    assert stat.S_IMODE(target.stat().st_mode) == 0o454
    apply_permissions(reverse)
    assert stat.S_IMODE(target.stat().st_mode) == 0o654
    target.chmod(0o644)
    with pytest.raises(OSError, match='changed'):
        apply_permissions(plan)
    assert target.read_text() == 'unchanged'
    no_access = plan_permissions(target, 0)
    restore = apply_permissions(no_access)
    apply_permissions(restore)
    assert stat.S_IMODE(target.stat().st_mode) == 0o644


def test_secure_delete_preview_and_cancel_never_execute(qapp, tmp_path, monkeypatch):
    from src.tools.file_operations.secure_delete.secure_delete import SecureDeleteGUI
    from src.gui.components import ConfirmationModal
    from PyQt5.QtWidgets import QMessageBox, QDialog
    target = tmp_path / 'keep.txt'
    target.write_text('keep')
    window = SecureDeleteGUI()
    window.selected_files = [str(target)]
    calls = []
    monkeypatch.setattr(window, '_execute_secure_delete', lambda: calls.append('execute'))
    monkeypatch.setattr(QMessageBox, 'information', lambda *a, **k: QMessageBox.Ok)
    assert window.dry_run_checkbox.isChecked()
    window.secure_delete()
    assert not calls
    window.dry_run_checkbox.setChecked(False)
    monkeypatch.setattr(ConfirmationModal, 'exec_', lambda self: QDialog.Rejected)
    window.secure_delete()
    assert not calls
    assert target.read_text() == 'keep'
    monkeypatch.setattr(ConfirmationModal, 'exec_', lambda self: QDialog.Accepted)
    window.secure_delete()
    assert calls == ['execute']
    window.close()


def test_background_cancel_keeps_ui_responsive_and_restores_disabled_controls(qapp):
    from src.gui.background_task import BackgroundTask
    from src.core.workflows import WorkflowCancelled
    from PyQt5.QtCore import QTimer
    from PyQt5.QtWidgets import QPushButton
    from threading import Event
    window = QMainWindow()
    body = QWidget()
    layout = QVBoxLayout(body)
    window.setCentralWidget(body)
    enabled, disabled = QPushButton('enabled'), QPushButton('disabled')
    layout.addWidget(enabled)
    layout.addWidget(disabled)
    disabled.setEnabled(False)
    task = BackgroundTask(window, 'test', layout, [enabled, disabled])
    started = Event()
    results, ticks = [], []
    def work():
        started.set()
        if task.cancel.wait(3):
            raise WorkflowCancelled()
        return 'unexpected'
    timer = QTimer(window)
    timer.timeout.connect(lambda: ticks.append(1))
    timer.start(5)
    window.show()
    task.start('cancel-test', work, results.append)
    deadline = time.monotonic() + 3
    while not started.is_set() and time.monotonic() < deadline:
        QTest.qWait(10)
    QTest.qWait(40)
    assert ticks and not enabled.isEnabled()
    task.request_cancel()
    while task.job is not None and time.monotonic() < deadline:
        QTest.qWait(10)
    assert task.job is None and not results
    assert enabled.isEnabled() and not disabled.isEnabled()
    assert 'cancel' in window.statusBar().currentMessage().lower()
    window.close()


def test_legacy_and_designer_locale_bindings_preserve_user_input(qapp):
    from PyQt5.QtWidgets import QLabel
    from src.rfu.localization import localized_widget, bind_designer_strings, service, catalogue
    key = next(key for key, value in catalogue().items() if key.startswith('Legacy.') and value == 'Delete Selected')
    parent = QWidget()
    label = localized_widget(QLabel, key, 'setText', parent)
    designer = QLabel('Delete Selected', parent)
    designer.setProperty('rfuLocale_setText', key)
    user_input = QLineEdit('My user-entered text', parent)
    bind_designer_strings(parent)
    old_locale, old_packs, old_preferences = service.locale, dict(service.packs), service._preferences
    service._preferences = None
    try:
        service.load_data({'schema_version': 1, 'locale': 'zz', 'strings': {key: 'Translated label'}})
        service.switch('zz')
        assert label.text() == designer.text() == 'Translated label'
        assert label.accessibleName() == 'Translated label'
        assert user_input.text() == 'My user-entered text'
    finally:
        service.packs = old_packs
        service.switch(old_locale)
        service._preferences = old_preferences
        parent.close()


def test_rename_preview_exclusive_destination_partial_cancel_and_undo(tmp_path):
    from src.core.rename_operations import plan_renames, execute_renames
    original = tmp_path / 'original.txt'
    original.write_text('content')
    plan = plan_renames(tmp_path, [('original.txt', 'new.txt')])
    assert original.exists() and not (tmp_path / 'new.txt').exists()
    cancel = Event()
    cancel.set()
    assert execute_renames(plan, cancel) == ((), ())
    reverse, errors = execute_renames(plan)
    assert not errors and not original.exists()
    assert (tmp_path / 'new.txt').read_text() == 'content'
    assert not execute_renames(reverse)[1]
    assert original.read_text() == 'content'
    (tmp_path / 'new.txt').write_text('someone else')
    reverse, errors = execute_renames(plan)
    assert not reverse and errors
    assert original.read_text() == 'content'
    assert (tmp_path / 'new.txt').read_text() == 'someone else'
    with pytest.raises(ValueError):
        plan_renames(tmp_path, [('original.txt', '../escape.txt')])


@pytest.mark.parametrize('legacy,canonical', [('open_files','open_file'), ('save_metadata','save_file'), ('export_results','export_data'), ('help_sync','user_guide'), ('new_deletion','new_project')])
def test_legacy_callbacks_dispatch_to_owner_and_block_while_busy(qapp, legacy, canonical):
    from src.gui.command_dispatch import CommandDispatcher
    window = QMainWindow()
    owner = QWidget()
    window.setCentralWidget(owner)
    calls = []
    owner.menu_manager = SimpleNamespace(callbacks={legacy: lambda: calls.append(legacy)})
    dispatcher = CommandDispatcher(window, owner, 'legacy-tool')
    assert dispatcher.invoke(canonical)
    assert calls == [legacy]
    owner._job = object()
    assert dispatcher.resolve('save_file') is None
    window.setProperty('toolDegraded', True)
    assert dispatcher.resolve('open_file') is None
    window.close()


def wait_for_task(task):
    deadline = time.monotonic() + 5
    while task.job is not None and time.monotonic() < deadline:
        QTest.qWait(10)
    assert task.job is None


def test_permissions_gui_preview_apply_and_restore(qapp, tmp_path, monkeypatch):
    import os
    import stat
    from src.tools.system.permissions.permissions_editor import PermissionsEditorGUI
    from src.gui.components import ConfirmationModal
    from PyQt5.QtWidgets import QDialog
    if os.name == 'nt':
        pytest.skip('POSIX mode restoration; Windows has read-only flag semantics')
    target = tmp_path / 'file'
    target.write_text('original')
    target.chmod(0o654)
    window = PermissionsEditorGUI()
    window.selected_path = str(target)
    window.read_check.setChecked(True)
    window.write_check.setChecked(False)
    window.execute_check.setChecked(False)
    window.apply_permissions()
    wait_for_task(window._permission_task)
    assert stat.S_IMODE(target.stat().st_mode) == 0o654
    window.preview_only.setChecked(False)
    monkeypatch.setattr(ConfirmationModal, 'exec_', lambda self: QDialog.Rejected)
    window.apply_permissions()
    wait_for_task(window._permission_task)
    assert stat.S_IMODE(target.stat().st_mode) == 0o654
    monkeypatch.setattr(ConfirmationModal, 'exec_', lambda self: QDialog.Accepted)
    window.apply_permissions()
    wait_for_task(window._permission_task)
    assert stat.S_IMODE(target.stat().st_mode) == 0o454
    assert window.can_undo()
    window.undo()
    wait_for_task(window._permission_task)
    assert stat.S_IMODE(target.stat().st_mode) == 0o654
    window.close()


def test_rename_gui_confirmation_and_undo(qapp, tmp_path, monkeypatch):
    from src.tools.file_operations.rename.rename import RenameWindow
    from src.gui.components import ConfirmationModal
    from PyQt5.QtWidgets import QDialog
    source = tmp_path / 'original.txt'
    source.write_text('preserved')
    window = RenameWindow()
    window.current_directory = str(tmp_path)
    window.selected_files = ['original.txt']
    monkeypatch.setattr(window, 'get_new_filename', lambda name, index: 'renamed.txt')
    monkeypatch.setattr(ConfirmationModal, 'exec_', lambda self: QDialog.Rejected)
    window.apply_rename()
    wait_for_task(window._rename_task())
    assert source.exists()
    monkeypatch.setattr(ConfirmationModal, 'exec_', lambda self: QDialog.Accepted)
    window.apply_rename()
    wait_for_task(window._rename_task())
    assert not source.exists() and (tmp_path / 'renamed.txt').read_text() == 'preserved'
    window.undo()
    wait_for_task(window._rename_task())
    assert source.read_text() == 'preserved' and not (tmp_path / 'renamed.txt').exists()
    window.close()
