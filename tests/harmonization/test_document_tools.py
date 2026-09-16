import ast
import json
from pathlib import Path
from threading import Event
import fitz
import pytest
from PyQt5.QtTest import QTest
from src.core.tool_manifest import ToolManifestRegistry
from src.core.tool_inventory import load_inventory
from src.core.workflows import WorkflowCancelled
from src.tools.pdf_tools import page_model as pdf
from src.tools.privacy.anonymizer import model as data


def wait(window):
    for _ in range(400):
        if window._job is None:
            return
        QTest.qWait(10)
    pytest.fail('Document operation did not finish')


def make_pdf(path, labels):
    with fitz.open() as document:
        for label in labels:
            document.new_page().insert_text((50, 50), label)
        document.save(path)


def test_inventory_governs_36_real_entrypoints():
    entries = ToolManifestRegistry.builtins()
    assert len(entries) == 36
    assert {e.tool_id for e in entries} == {r['id'] for r in load_inventory()['tools']}
    for entry in entries:
        path = Path(*entry.module_path.split('.')).with_suffix('.py')
        tree = ast.parse(path.read_text(encoding='utf-8-sig'))
        assert any(isinstance(node, ast.ClassDef) and node.name == entry.class_name
                   for node in tree.body), entry.tool_id
        for alias in entry.aliases:
            assert ToolManifestRegistry.lookup(alias) is entry
    assert ToolManifestRegistry.lookup('Alpha Tool') is None


def test_json_transform_preserves_structure_and_repeat_pseudonyms(tmp_path):
    path = tmp_path / 'data.json'
    original = [{'name': 'Alice', 'private': {'email': 'a@example.org'}, 'keep': 1},
                {'name': 'Alice', 'private': None, 'keep': 2}]
    path.write_text(json.dumps(original))
    dataset = data.load_dataset(path)
    rules = {'name': 'pseudonym', 'private': 'redact'}
    result = data.transform(dataset, rules, b'key')
    assert result[0]['name'] == result[1]['name']
    assert result[0]['name'] != data.transform(dataset, rules, b'other')[0]['name']
    assert result[0]['private'] == '[REDACTED]'
    assert result[0]['keep'] == 1
    assert dataset.records == original
    target = tmp_path / 'export.json'
    data.export_dataset(dataset, result, target)
    assert json.loads(target.read_text()) == result
    with pytest.raises(ValueError):
        data.export_dataset(dataset, result, path)
    assert json.loads(path.read_text()) == original


def test_csv_and_json_object_exports(tmp_path):
    path = tmp_path / 'data.csv'
    path.write_text('name,note\nAlice,=1+1\nAlice,hello\n')
    dataset = data.load_dataset(path)
    result = data.transform(dataset, {'name': 'redact'}, b'key')
    target = tmp_path / 'output.csv'
    data.export_dataset(dataset, result, target)
    assert "'=1+1" in target.read_text()
    path = tmp_path / 'object.json'
    path.write_text('{"name": "Alice", "unselected": [1, 2]}')
    dataset = data.load_dataset(path)
    result = data.transform(dataset, {'name': 'redact'}, b'key')
    target = tmp_path / 'object-out.json'
    data.export_dataset(dataset, result, target)
    assert json.loads(target.read_text()) == {'name': '[REDACTED]', 'unselected': [1, 2]}


def test_pdf_reorder_rotate_insert_extract_preserves_sources(tmp_path):
    source, inserted = tmp_path / 'source.pdf', tmp_path / 'inserted.pdf'
    make_pdf(source, ['first', 'second'])
    make_pdf(inserted, ['third'])
    before = source.read_bytes(), inserted.read_bytes()
    pages = pdf.load_pages(source)
    extra = pdf.load_pages(inserted)
    draft = [pdf.rotate(pages[1]), extra[0], pages[0]]
    output = tmp_path / 'output.pdf'
    pdf.export_pages(draft, output)
    with fitz.open(output) as result:
        assert [page.get_text().strip() for page in result] == ['second', 'third', 'first']
        assert result[0].rotation == 90
    assert pdf.preview(draft[0]).startswith(b'\x89PNG')
    pdf.export_pages([draft[1]], tmp_path / 'extract.pdf')
    with pytest.raises(ValueError):
        pdf.export_pages(draft, source)
    # Removed source pages still protect their source from being overwritten.
    with pytest.raises(ValueError):
        pdf.export_pages(extra, source, sources=[source])
    assert (source.read_bytes(), inserted.read_bytes()) == before


def test_cancel_and_aliases_leave_output_untouched(tmp_path):
    source = tmp_path / 'source.pdf'
    make_pdf(source, ['one'])
    pages = pdf.load_pages(source)
    target = tmp_path / 'existing.pdf'
    target.write_bytes(b'existing')
    cancel = Event()
    cancel.set()
    with pytest.raises(WorkflowCancelled):
        pdf.export_pages(pages, target, cancel)
    assert target.read_bytes() == b'existing'
    alias = tmp_path / 'alias.pdf'
    alias.hardlink_to(source)
    with pytest.raises(ValueError):
        pdf.export_pages(pages, alias)


def test_anonymizer_gui_preview_invalidation_and_export(qapp, tmp_path):
    from src.tools.privacy.anonymizer.data_anonymizer import DataAnonymizerGUI
    source = tmp_path / 'data.csv'
    source.write_text('name,age\nAlice,32\nAlice,33\n')
    window = DataAnonymizerGUI()
    window.load_file(source)
    wait(window)
    assert not window.save_button.isEnabled()
    window.fields.cellWidget(0, 1).setCurrentIndex(2)
    window.preview_data()
    wait(window)
    assert 'Alice' not in window.preview.toPlainText()
    assert window.save_button.isEnabled()
    output = tmp_path / 'result.csv'
    window.export_to(output)
    wait(window)
    assert 'person_' in output.read_text()
    window.fields.cellWidget(0, 1).setCurrentIndex(1)
    assert not window.save_button.isEnabled()
    assert not window.preview.toPlainText()
    window.close()


def test_pdf_gui_draft_undo_insert_and_export(qapp, tmp_path):
    from src.tools.pdf_tools.page_administration import PageAdministrationGUI
    source = tmp_path / 'source.pdf'
    inserted = tmp_path / 'inserted.pdf'
    make_pdf(source, ['first', 'second'])
    make_pdf(inserted, ['third'])
    window = PageAdministrationGUI()
    window.load_file(source)
    wait(window)
    window.rotate_selected()
    assert window.pages[0].rotation == 90
    window.undo_stack.undo()
    assert window.pages[0].rotation == 0
    window.undo_stack.redo()
    window.insert_file(inserted)
    wait(window)
    assert len(window.pages) == 3
    window.undo_stack.undo()
    assert len(window.pages) == 2
    window.undo_stack.redo()
    window.show_preview()
    wait(window)
    assert window.image.pixmap() is not None
    window.remove_selected()
    assert len(window.pages) == 2
    output = tmp_path / 'out.pdf'
    window.export_to(output)
    assert not window.undo_actions[0].isEnabled()
    wait(window)
    with fitz.open(output) as result:
        assert len(result) == 2
    window.close()


def test_catalogue_launches_both_new_tools_and_reopens(qapp):
    from PyQt5.QtWidgets import QMainWindow
    from src.gui.tool_catalogue import ToolCatalogue, launch_registered_tool
    from src.simple_menu_manager import SimpleMenuManager
    hub = QMainWindow()
    hub.menu_manager = SimpleMenuManager(hub)
    hub.menu_manager.create_menubar()
    catalogue = ToolCatalogue(hub)
    assert catalogue.tree.topLevelItemCount() == 36
    for tool_id in ['data-anonymizer', 'pdf-page-administration']:
        assert launch_registered_tool(hub, tool_id)
        window = hub._catalogue_windows[tool_id]
        assert window.isVisible()
        assert window.tool_id == tool_id
        assert window.menu_registry.menus['File'].actions()
        window.close()
        assert launch_registered_tool(hub, tool_id)
        assert hub._catalogue_windows[tool_id] is window
        window.close()
    hub.close()


def test_pdf_links_inspection_preserves_input_and_exports_explicitly(tmp_path):
    from src.tools.pdf_tools.pdf_content_extraction.extract_links import inspect_links, export_links
    source = tmp_path / 'source.pdf'
    with fitz.open() as document:
        page = document.new_page()
        page.insert_link({'kind': fitz.LINK_URI, 'from': fitz.Rect(10, 10, 80, 30),
                          'uri': 'https://example.org/path'})
        document.save(source)
    before = source.read_bytes()
    links = inspect_links(source)
    assert links == [(1, 'https://example.org/path')]
    assert source.read_bytes() == before
    assert list(tmp_path.iterdir()) == [source]
    export_links(source, links, tmp_path / 'links.csv')
    assert 'https://example.org/path' in (tmp_path / 'links.csv').read_text()
    with pytest.raises(ValueError):
        export_links(source, links, source)


def test_pdf_export_handoff_to_link_inspection(qapp, tmp_path):
    from PyQt5.QtWidgets import QMainWindow
    from src.gui.tool_catalogue import launch_registered_tool
    from src.simple_menu_manager import SimpleMenuManager
    from src.core.tool_handoffs import DocumentArtifact, handoff
    hub = QMainWindow()
    hub.menu_manager = SimpleMenuManager(hub)
    hub.menu_manager.create_menubar()
    hub.launch_tool = lambda name: launch_registered_tool(hub, name)
    source = tmp_path / 'source.pdf'
    make_pdf(source, ['first'])
    hub.launch_tool('pdf-page-administration')
    window = hub._catalogue_windows['pdf-page-administration']
    window.load_file(source)
    wait(window)
    output = tmp_path / 'saved.pdf'
    window.export_to(output)
    wait(window)
    assert window.handoff_button.isEnabled()
    window.inspect_exported_links()
    target = hub._catalogue_windows['pdf-extract-links']
    wait(target)
    assert target.source == output
    with pytest.raises(ValueError):
        handoff(hub, DocumentArtifact(output, 'application/pdf', 'test'), 'data-anonymizer')
    window.close()
    target.close()
    hub.close()


def test_document_worker_preserves_correlation_and_recovers_after_cancel(qapp, monkeypatch):
    from src.tools.privacy.anonymizer.data_anonymizer import DataAnonymizerGUI
    from src.core.operations import operation
    events = []
    monkeypatch.setattr('src.gui.telemetry.emit_telemetry', lambda *args, **kw: events.append(kw))
    window = DataAnonymizerGUI()
    window.show()
    with operation('workflow', 'start') as correlation:
        window.run_job('wait', lambda: window.cancel.wait(2), lambda _: None)
    window.close()
    wait(window)
    assert not window.isVisible()
    assert all(event.get('correlation_id') == correlation for event in events
               if event.get('operation') == 'wait')
    window.show()
    window.run_job('again', lambda: None, lambda _: None)
    wait(window)
    assert window.isVisible()
    window.close()


def test_root_main_ui_uses_governed_catalogue(qapp):
    import importlib.util
    import logging
    from PyQt5.QtWidgets import QMainWindow
    spec = importlib.util.spec_from_file_location('rfu_root_main_test', Path.cwd() / 'main.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # Exercise UI construction independently of the unchanged login gate.
    window = module.RFUMainWindow.__new__(module.RFUMainWindow)
    QMainWindow.__init__(window)
    window.logger = logging.getLogger('test.main')
    window.config_manager = None
    window.init_ui()
    assert window.tool_catalogue.tree.topLevelItemCount() == 36
    assert window.tab_widget.count() == 1
    window.close()
