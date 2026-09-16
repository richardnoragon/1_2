"""PDF page plans with preview, insertion, undo, extraction and Save As."""
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QFileDialog, QHBoxLayout, QGridLayout, QListWidget, QAbstractItemView,
                            QLabel, QSplitter, QUndoCommand, QUndoStack)
from src.gui.document_tool import DocumentToolWindow
from src.gui.menu_registry import MenuRegistry
from src.gui.undo_history import install_undo_history
from src.rfu import font_tokens
from src.rfu.localization import service, tr
from .page_model import load_pages, rotate, preview, export_pages


class EditPages(QUndoCommand):
    def __init__(self, window, pages):
        super().__init__(tr('DocumentTool.DRAFT_EDIT'))
        self.window, self.before, self.after = window, list(window.pages), list(pages)

    def redo(self):
        self.window.set_pages(self.after)

    def undo(self):
        self.window.set_pages(self.before)


class PageAdministrationGUI(DocumentToolWindow):
    undo_supported = True

    def __init__(self, parent=None):
        super().__init__('pdf-page-administration', 'DocumentTool.PDF_TITLE', 'DocumentTool.PDF_HELP', parent)
        self.pages = []
        self.sources = set()
        self.exported_path = None
        self.undo_stack = QUndoStack(self)
        self.menu_registry = MenuRegistry(self)
        self.undo_actions = install_undo_history(self, self.undo_stack, tool_id=self.tool_id)
        splitter = QSplitter()
        self.page_list = QListWidget()
        self.page_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        service.bind(self.page_list, 'setAccessibleName', 'DocumentTool.PAGES')
        font_tokens.bind(self.page_list)
        self.page_list.itemSelectionChanged.connect(self.update_controls)
        self.page_list.itemActivated.connect(lambda _: self.show_preview())
        self.image = QLabel()
        self.image.setMinimumWidth(260)
        self.image.setAlignment(Qt.AlignCenter)
        service.bind(self.image, 'setAccessibleName', 'DocumentTool.PREVIEW')
        font_tokens.bind(self.image)
        splitter.addWidget(self.page_list)
        splitter.addWidget(self.image)
        self.layout.addWidget(splitter, 1)
        row = QHBoxLayout()
        row.addWidget(self.button('DocumentTool.OPEN', self.choose_file))
        self.insert_button = self.button('DocumentTool.INSERT', self.choose_insert)
        row.addWidget(self.insert_button)
        row.addStretch()
        self.layout.addLayout(row)
        edits = QGridLayout()
        self.edit_buttons = []
        for token, callback in [('UP', lambda: self.move(-1)), ('DOWN', lambda: self.move(1)),
                                ('ROTATE', self.rotate_selected), ('DELETE', self.remove_selected),
                                ('PREVIEW', self.show_preview)]:
            button = self.button('DocumentTool.' + token, callback)
            self.edit_buttons.append(button)
            position = len(self.edit_buttons) - 1
            edits.addWidget(button, position // 3, position % 3)
        self.layout.addLayout(edits)
        footer = QHBoxLayout()
        self.handoff_button = self.button('DocumentTool.INSPECT_LINKS', self.inspect_exported_links)
        footer.addWidget(self.handoff_button)
        footer.addStretch()
        self.extract_button = self.button('DocumentTool.EXTRACT', lambda: self.save_as(True))
        self.save_button = self.button('DocumentTool.SAVE', self.save_as, primary=True)
        footer.addWidget(self.extract_button)
        footer.addWidget(self.save_button)
        self.layout.addLayout(footer)
        self.controls.append(self.page_list)
        self.update_controls()

    def selected(self):
        return sorted(self.page_list.row(item) for item in self.page_list.selectedItems())

    def choose_file(self):
        path, _ = QFileDialog.getOpenFileName(self, tr('DocumentTool.OPEN'), '', 'PDF (*.pdf)')
        if path:
            self.load_file(path)

    def load_file(self, path):
        self.run_job('load', lambda: load_pages(path, self.cancel), self._loaded)

    def _loaded(self, pages):
        self.undo_stack.clear()
        self.sources = {p.source.path for p in pages}
        self.set_pages(pages)
        self.status.setText(tr('DocumentTool.READY'))

    def set_pages(self, pages):
        self.exported_path = None
        self.pages = list(pages)
        self.page_list.blockSignals(True)
        self.page_list.clear()
        for position, page in enumerate(pages):
            self.page_list.addItem(tr('DocumentTool.PAGE').format(position=position + 1,
                file=page.source.path.name, page=page.index + 1, rotation=page.rotation))
        if pages:
            self.page_list.setCurrentRow(0)
        self.page_list.blockSignals(False)
        self.image.clear()
        self.update_controls()

    def choose_insert(self):
        path, _ = QFileDialog.getOpenFileName(self, tr('DocumentTool.INSERT'), '', 'PDF (*.pdf)')
        if path:
            self.insert_file(path)

    def insert_file(self, path):
        selected = self.selected()
        position = selected[-1] + 1 if selected else len(self.pages)
        def inserted(pages):
            self.sources.update(p.source.path for p in pages)
            self.undo_stack.push(EditPages(self, self.pages[:position] + pages + self.pages[position:]))
            self.status.setText(tr('DocumentTool.READY'))
        self.run_job('insert', lambda: load_pages(path, self.cancel), inserted)

    def move(self, direction):
        selected = set(self.selected())
        pages = list(self.pages)
        indices = sorted(selected, reverse=direction > 0)
        for index in indices:
            target = index + direction
            if 0 <= target < len(pages) and target not in selected:
                pages[index], pages[target] = pages[target], pages[index]
                selected.remove(index)
                selected.add(target)
        if pages != self.pages:
            self.undo_stack.push(EditPages(self, pages))
            self.page_list.clearSelection()
            for index in selected:
                self.page_list.item(index).setSelected(True)

    def rotate_selected(self):
        selected = set(self.selected())
        if selected:
            self.undo_stack.push(EditPages(self, [rotate(p) if i in selected else p for i, p in enumerate(self.pages)]))

    def remove_selected(self):
        selected = set(self.selected())
        if selected:
            self.undo_stack.push(EditPages(self, [p for i, p in enumerate(self.pages) if i not in selected]))

    def show_preview(self):
        selected = self.selected()
        if selected:
            page = self.pages[selected[0]]
            self.run_job('preview', lambda: preview(page, self.cancel), self._previewed)

    def _previewed(self, data):
        pixmap = QPixmap()
        pixmap.loadFromData(data, 'PNG')
        self.image.setPixmap(pixmap.scaled(600, 650, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.status.setText(tr('DocumentTool.READY'))

    def save_as(self, selected=False):
        pages = [self.pages[i] for i in self.selected()] if selected else list(self.pages)
        path, _ = QFileDialog.getSaveFileName(self, tr('DocumentTool.SAVE'), 'pages.pdf', 'PDF (*.pdf)')
        if path:
            self.export_to(path, pages)

    def export_to(self, path, pages=None):
        snapshot = list(self.pages if pages is None else pages)
        def exported(result):
            from pathlib import Path
            self.exported_path = Path(path).resolve()
            self.exported(result)
        self.run_job('export', lambda: export_pages(snapshot, path, self.cancel, self.sources), exported)

    def inspect_exported_links(self):
        from src.core.tool_handoffs import DocumentArtifact, handoff
        try:
            handoff(self.parent_hub, DocumentArtifact(self.exported_path, 'application/pdf', self.tool_id), 'pdf-extract-links')
        except (ValueError, OSError, RuntimeError):
            self.status.setText(tr('DocumentTool.HANDOFF_FAILED'))

    def update_controls(self):
        if self._job is not None:
            for action in self.undo_actions:
                action.setEnabled(False)
            return
        self.handoff_button.setEnabled(self.exported_path is not None and hasattr(self, "parent_hub"))
        selected = bool(self.selected())
        for button in self.edit_buttons:
            button.setEnabled(selected)
        self.extract_button.setEnabled(selected)
        self.save_button.setEnabled(bool(self.pages))
        self.undo_actions[0].setEnabled(self.undo_stack.canUndo())
        self.undo_actions[1].setEnabled(self.undo_stack.canRedo())
        self.undo_actions[2].setEnabled(True)

    def run_job(self, name, work, completed):
        started = super().run_job(name, work, completed)
        self.update_controls()
        return started
