"""CSV/JSON field redaction and session-scoped pseudonymization."""
import json
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QTableWidget,
                            QTableWidgetItem, QComboBox, QPlainTextEdit)
from src.gui.document_tool import DocumentToolWindow
from src.rfu import font_tokens
from src.rfu.localization import service, tr
from .model import load_dataset, transform, export_dataset, new_key


class DataAnonymizerGUI(DocumentToolWindow):
    undo_supported = False

    def __init__(self, parent=None):
        super().__init__('data-anonymizer', 'DocumentTool.ANON_TITLE', 'DocumentTool.ANON_HELP', parent)
        self.dataset = None
        self.transformed = None
        self.key = new_key()
        self.fields = QTableWidget(0, 2)
        self.fields.setHorizontalHeaderLabels(tr('DocumentTool.HEADERS').split('|'))
        service.bind(self.fields, 'setAccessibleName', 'DocumentTool.FIELDS')
        font_tokens.bind(self.fields)
        self.layout.addWidget(self.fields, 1)
        self.preview = QPlainTextEdit()
        self.preview.setReadOnly(True)
        service.bind(self.preview, 'setAccessibleName', 'DocumentTool.DATA_PREVIEW')
        font_tokens.bind(self.preview)
        self.layout.addWidget(self.preview, 2)
        row = QHBoxLayout()
        row.addWidget(self.button('DocumentTool.OPEN', self.choose_file))
        row.addStretch()
        self.preview_button = self.button('DocumentTool.PREVIEW_DATA', self.preview_data)
        self.save_button = self.button('DocumentTool.SAVE', self.save_as, primary=True)
        row.addWidget(self.preview_button)
        row.addWidget(self.save_button)
        self.layout.addLayout(row)
        self.controls.append(self.fields)
        self.update_controls()
        service.subscribe(self, 'retranslate')

    def retranslate(self):
        self.fields.setHorizontalHeaderLabels(tr('DocumentTool.HEADERS').split('|'))
        for index in range(self.fields.rowCount()):
            combo = self.fields.cellWidget(index, 1)
            for position, key in enumerate(['KEEP', 'REDACT', 'PSEUDONYM']):
                combo.setItemText(position, tr('DocumentTool.' + key))

    def choose_file(self):
        path, _ = QFileDialog.getOpenFileName(self, tr('DocumentTool.OPEN'), '', 'Data (*.csv *.json)')
        if path:
            self.load_file(path)

    def load_file(self, path):
        self.run_job('load', lambda: load_dataset(path, self.cancel), self._loaded)

    def _loaded(self, dataset):
        self.dataset = dataset
        self.key = new_key()
        self.invalidate()
        self.fields.setRowCount(len(dataset.fields))
        for index, field in enumerate(dataset.fields):
            item = QTableWidgetItem(field)
            from PyQt5.QtCore import Qt
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self.fields.setItem(index, 0, item)
            combo = QComboBox()
            font_tokens.bind(combo)
            combo.setAccessibleName(field)
            for key, mode in [('KEEP', 'keep'), ('REDACT', 'redact'), ('PSEUDONYM', 'pseudonym')]:
                combo.addItem(tr('DocumentTool.' + key), mode)
            combo.currentIndexChanged.connect(self.invalidate)
            self.fields.setCellWidget(index, 1, combo)
        self.fields.resizeColumnsToContents()
        self.status.setText(tr('DocumentTool.SELECT_RULE'))

    def invalidate(self, *_):
        self.transformed = None
        self.preview.clear()
        self.save_button.setEnabled(False)

    def preview_data(self):
        rules = {field: self.fields.cellWidget(index, 1).currentData()
                 for index, field in enumerate(self.dataset.fields)
                 if self.fields.cellWidget(index, 1).currentData() != 'keep'}
        if not rules:
            self.status.setText(tr('DocumentTool.SELECT_RULE'))
            return
        def work():
            records = transform(self.dataset, rules, self.key, self.cancel)
            preview = json.dumps(records[:100], ensure_ascii=False, indent=2)
            return records, preview[:65536]
        self.run_job('preview', work, self._previewed)

    def _previewed(self, result):
        records, preview = result
        self.transformed = records
        self.preview.setPlainText(preview)
        self.status.setText(tr('DocumentTool.PREVIEW_READY').format(count=len(records)))

    def save_as(self):
        suffix = self.dataset.format
        path, _ = QFileDialog.getSaveFileName(self, tr('DocumentTool.SAVE'),
                    'anonymized.' + suffix, suffix.upper() + ' (*.' + suffix + ')')
        if path:
            self.export_to(path)

    def export_to(self, path):
        if self.transformed is None:
            return
        self.run_job('export', lambda: export_dataset(self.dataset, self.transformed, path, self.cancel), self.exported)

    def update_controls(self):
        self.preview_button.setEnabled(self.dataset is not None)
        self.save_button.setEnabled(self.transformed is not None)


def main():
    import sys
    app = QApplication.instance() or QApplication(sys.argv)
    window = DataAnonymizerGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
