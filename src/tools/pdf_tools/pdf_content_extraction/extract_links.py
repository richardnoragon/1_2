"""Read-only PDF link inspection with explicit atomic CSV export."""
import csv
from pathlib import Path
import fitz
from PyQt5.QtWidgets import QApplication, QFileDialog, QHBoxLayout, QTableWidget, QTableWidgetItem
from src.core.document_export import atomic_export, check_cancel
from src.gui.document_tool import DocumentToolWindow
from src.rfu import font_tokens
from src.rfu.localization import service, tr


def inspect_links(path, cancel=None):
    links = []
    with fitz.open(path) as document:
        if document.needs_pass:
            raise ValueError('An unencrypted PDF is required.')
        for index, page in enumerate(document):
            check_cancel(cancel)
            for link in page.get_links():
                if link.get('uri'):
                    links.append((index + 1, link['uri']))
    check_cancel(cancel)
    return links


def export_links(source, links, destination, cancel=None):
    def write(path):
        with path.open('w', encoding='utf-8', newline='') as stream:
            writer = csv.writer(stream)
            writer.writerow(['Page', 'URL'])
            for page, uri in links:
                check_cancel(cancel)
                writer.writerow([page, "'" + uri if uri.startswith(('=', '+', '-', '@', '\t', '\r')) else uri])
    atomic_export(destination, [source], write, cancel)


class ExtractLinksUI(DocumentToolWindow):
    undo_supported = False

    def __init__(self, parent=None):
        super().__init__('pdf-extract-links', 'PDFLinks.TITLE', 'PDFLinks.HELP', parent)
        self.source = None
        self.links = []
        self.table = QTableWidget(0, 2)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setHorizontalHeaderLabels(tr('PDFLinks.HEADERS').split('|'))
        service.bind(self.table, 'setAccessibleName', 'PDFLinks.TABLE')
        font_tokens.bind(self.table)
        self.layout.addWidget(self.table)
        row = QHBoxLayout()
        row.addWidget(self.button('DocumentTool.OPEN', self.choose_file))
        row.addStretch()
        self.save_button = self.button('DocumentTool.SAVE', self.save_as, primary=True)
        row.addWidget(self.save_button)
        self.layout.addLayout(row)
        self.update_controls()
        service.subscribe(self, 'retranslate')

    def retranslate(self):
        self.table.setHorizontalHeaderLabels(tr('PDFLinks.HEADERS').split('|'))

    def choose_file(self):
        path, _ = QFileDialog.getOpenFileName(self, tr('DocumentTool.OPEN'), '', 'PDF (*.pdf)')
        if path:
            self.load_file(path)

    def load_file(self, path):
        def loaded(links):
            self.source = Path(path).resolve()
            self.links = links
            self.table.setRowCount(min(len(links), 1000))
            for row, (page, uri) in enumerate(links[:1000]):
                self.table.setItem(row, 0, QTableWidgetItem(str(page)))
                self.table.setItem(row, 1, QTableWidgetItem(uri))
            self.table.resizeColumnsToContents()
            self.status.setText(tr('PDFLinks.READY').format(count=len(links)))
        self.run_job('inspect', lambda: inspect_links(path, self.cancel), loaded)

    def save_as(self):
        path, _ = QFileDialog.getSaveFileName(self, tr('DocumentTool.SAVE'), 'links.csv', 'CSV (*.csv)')
        if path:
            self.run_job('export', lambda: export_links(self.source, self.links, path, self.cancel), self.exported)

    def update_controls(self):
        self.save_button.setEnabled(self.source is not None)


def main():
    import sys
    app = QApplication.instance() or QApplication(sys.argv)
    window = ExtractLinksUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
