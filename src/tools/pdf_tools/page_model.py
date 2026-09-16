"""Immutable PDF inputs and editable page plans; all writes use separate output."""
from dataclasses import dataclass, replace
from pathlib import Path
import fitz
from src.core.document_export import atomic_export, check_cancel


@dataclass(frozen=True)
class PDFSource:
    path: Path
    content: bytes


@dataclass(frozen=True)
class Page:
    source: PDFSource
    index: int
    rotation: int = 0


def load_pages(path, cancel=None):
    check_cancel(cancel)
    source = PDFSource(Path(path).resolve(), Path(path).read_bytes())
    with fitz.open(stream=source.content, filetype='pdf') as document:
        if document.needs_pass:
            raise ValueError('This PDF is password protected. Open an unencrypted copy.')
        pages = [Page(source, index) for index in range(len(document))]
    if not pages:
        raise ValueError('The PDF has no pages.')
    check_cancel(cancel)
    return pages


def rotate(page):
    return replace(page, rotation=(page.rotation + 90) % 360)


def preview(page, cancel=None):
    check_cancel(cancel)
    with fitz.open(stream=page.source.content, filetype='pdf') as document:
        item = document[page.index]
        item.set_rotation((item.rotation + page.rotation) % 360)
        scale = min(700 / item.rect.width, 850 / item.rect.height)
        data = item.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False).tobytes('png')
    check_cancel(cancel)
    return data


def export_pages(pages, destination, cancel=None, sources=()):
    if not pages:
        raise ValueError('Keep or select at least one page.')
    if Path(destination).suffix.lower() != '.pdf':
        raise ValueError('Choose a PDF output file.')
    def write(path):
        with fitz.open() as output:
            opened = {}
            try:
                for page in pages:
                    check_cancel(cancel)
                    key = id(page.source)
                    if key not in opened:
                        opened[key] = fitz.open(stream=page.source.content, filetype='pdf')
                    source = opened[key]
                    output.insert_pdf(source, from_page=page.index, to_page=page.index)
                    output[-1].set_rotation((source[page.index].rotation + page.rotation) % 360)
                output.save(str(path), garbage=4, deflate=True)
            finally:
                for document in opened.values():
                    document.close()
    atomic_export(destination, [p.source.path for p in pages] + list(sources), write, cancel)
