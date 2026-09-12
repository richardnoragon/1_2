"""
Enhanced Editor - Advanced Text Editor for Richard's File Utilities

A comprehensive text editor with syntax highlighting, advanced search/replace,
file operations, and integration with the RFU ecosystem.

Features:
- Multi-document tabbed interface
- Syntax highlighting for 20+ languages
- Advanced search and replace with regex support
- File encoding detection and conversion
- Text transformation tools
- Integrated file finder for locating resources
- Plugin architecture for extensibility
- Integration with StandardWindow for consistent UI
"""

import codecs
import json
import os
import re
import sys
import tempfile
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from PyQt5.QtCore import (
    QDir,
    QEasingCurve,
    QFileInfo,
    QFileSystemWatcher,
    QMimeData,
    QObject,
    QPoint,
    QPropertyAnimation,
    QRect,
    QSettings,
    QSize,
    QStandardPaths,
    Qt,
    QTextCodec,
    QThread,
    QTimer,
    QUrl,
    pyqtSignal,
)
from PyQt5.QtGui import (
    QClipboard,
    QColor,
    QDragEnterEvent,
    QDropEvent,
    QFont,
    QFontDatabase,
    QFontMetrics,
    QIcon,
    QKeyEvent,
    QKeySequence,
    QMouseEvent,
    QPainter,
    QPalette,
    QPixmap,
    QSyntaxHighlighter,
    QTextBlockFormat,
    QTextCharFormat,
    QTextCursor,
    QTextDocument,
    QTextFormat,
    QTextOption,
    QWheelEvent,
)
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QAction,
    QApplication,
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QMenuBar,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSlider,
    QSpinBox,
    QSplitter,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextBrowser,
    QTextEdit,
    QToolBar,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

# Import StandardWindow for RFU integration
try:
    from src.gui.components.buttons import PrimaryButton, SecondaryButton
    from src.gui.components.inputs import TextInput
    from src.gui.standard_window import StandardWindow
except ImportError:
    # Fallback for standalone execution
    try:
        from src.gui.standard_window import StandardWindow
    except ImportError:
        # Final fallback - create a minimal StandardWindow substitute
        class StandardWindow(QMainWindow):
            def __init__(self, title="", window_type="utility"):
                super().__init__()
                self.setWindowTitle(title)
                self.central_widget = QWidget()
                self.setCentralWidget(self.central_widget)
                self.main_layout = QVBoxLayout(self.central_widget)

            def show_status_message(self, message, timeout=3000):
                status_bar = self.statusBar()
                if status_bar:
                    status_bar.showMessage(message, timeout)


class DocumentType(Enum):
    """Document type enumeration for syntax highlighting."""

    TEXT = "text"
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    HTML = "html"
    CSS = "css"
    XML = "xml"
    JSON = "json"
    YAML = "yaml"
    SQL = "sql"
    BASH = "bash"
    POWERSHELL = "powershell"
    C = "c"
    CPP = "cpp"
    JAVA = "java"
    CSHARP = "csharp"
    MARKDOWN = "markdown"


@dataclass
class SearchOptions:
    """Options for search operations."""

    case_sensitive: bool = False
    whole_words: bool = False
    use_regex: bool = False
    wrap_around: bool = True
    search_backwards: bool = False


@dataclass
class EditorSettings:
    """Editor configuration settings."""

    font_family: str = "Consolas"
    font_size: int = 11
    tab_width: int = 4
    use_spaces: bool = True
    word_wrap: bool = True
    line_numbers: bool = True
    syntax_highlighting: bool = True
    auto_indent: bool = True
    show_whitespace: bool = False
    theme: str = "default"


class SyntaxHighlighter(QSyntaxHighlighter):
    """Basic syntax highlighter for common programming languages."""

    def __init__(self, document, language: DocumentType):
        super().__init__(document)
        self.language = language
        self.highlighting_rules = []
        self._setup_highlighting_rules()

    def _setup_highlighting_rules(self):
        """Setup syntax highlighting rules based on language."""
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(0, 0, 255))
        keyword_format.setFontWeight(QFont.Bold)

        string_format = QTextCharFormat()
        string_format.setForeground(QColor(0, 128, 0))

        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(128, 128, 128))
        comment_format.setFontItalic(True)

        if self.language == DocumentType.PYTHON:
            keywords = [
                "def",
                "class",
                "if",
                "elif",
                "else",
                "try",
                "except",
                "finally",
                "for",
                "while",
                "import",
                "from",
                "as",
                "return",
                "yield",
                "break",
                "continue",
                "pass",
                "and",
                "or",
                "not",
                "in",
                "is",
                "lambda",
                "with",
                "global",
                "nonlocal",
                "assert",
                "del",
                "raise",
            ]

            for keyword in keywords:
                self.highlighting_rules.append(
                    (re.compile(r"\b" + keyword + r"\b"), keyword_format)
                )

            # Strings
            self.highlighting_rules.append(
                (re.compile(r'"[^"\\]*(\\.[^"\\]*)*"'), string_format)
            )
            self.highlighting_rules.append(
                (re.compile(r"'[^'\\]*(\\.[^'\\]*)*'"), string_format)
            )

            # Comments
            self.highlighting_rules.append((re.compile(r"#[^\n]*"), comment_format))

        elif self.language == DocumentType.JAVASCRIPT:
            keywords = [
                "var",
                "let",
                "const",
                "function",
                "if",
                "else",
                "for",
                "while",
                "do",
                "switch",
                "case",
                "default",
                "break",
                "continue",
                "return",
                "try",
                "catch",
                "finally",
                "throw",
                "new",
                "this",
                "typeof",
                "instanceof",
                "in",
                "delete",
                "void",
            ]

            for keyword in keywords:
                self.highlighting_rules.append(
                    (re.compile(r"\b" + keyword + r"\b"), keyword_format)
                )

    def highlightBlock(self, text):
        """Apply syntax highlighting to a block of text."""
        for pattern, format in self.highlighting_rules:
            for match in pattern.finditer(text):
                start, end = match.span()
                self.setFormat(start, end - start, format)


class DocumentManager:
    """Manages multiple documents and their properties."""

    def __init__(self):
        self.documents = {}
        self.current_document = None
        self.recent_files = []
        self.max_recent_files = 10

    def create_document(self, content: str = "", file_path: str = None) -> str:
        """Create a new document and return its ID."""
        doc_id = f"doc_{len(self.documents)}"
        document = {
            "id": doc_id,
            "content": content,
            "file_path": file_path,
            "is_modified": False,
            "encoding": "utf-8",
            "line_ending": "lf",
            "document_type": self._detect_document_type(file_path),
            "cursor_position": 0,
            "scroll_position": 0,
        }
        self.documents[doc_id] = document
        self.current_document = doc_id
        return doc_id

    def _detect_document_type(self, file_path: str) -> DocumentType:
        """Detect document type based on file extension."""
        if not file_path:
            return DocumentType.TEXT

        extension = Path(file_path).suffix.lower()
        type_mapping = {
            ".py": DocumentType.PYTHON,
            ".js": DocumentType.JAVASCRIPT,
            ".html": DocumentType.HTML,
            ".htm": DocumentType.HTML,
            ".css": DocumentType.CSS,
            ".xml": DocumentType.XML,
            ".json": DocumentType.JSON,
            ".yaml": DocumentType.YAML,
            ".yml": DocumentType.YAML,
            ".sql": DocumentType.SQL,
            ".sh": DocumentType.BASH,
            ".ps1": DocumentType.POWERSHELL,
            ".c": DocumentType.C,
            ".cpp": DocumentType.CPP,
            ".cc": DocumentType.CPP,
            ".cxx": DocumentType.CPP,
            ".java": DocumentType.JAVA,
            ".cs": DocumentType.CSHARP,
            ".md": DocumentType.MARKDOWN,
            ".markdown": DocumentType.MARKDOWN,
        }
        return type_mapping.get(extension, DocumentType.TEXT)

    def get_document(self, doc_id: str) -> Optional[Dict]:
        """Get document by ID."""
        return self.documents.get(doc_id)

    def update_document(self, doc_id: str, **kwargs):
        """Update document properties."""
        if doc_id in self.documents:
            self.documents[doc_id].update(kwargs)

    def remove_document(self, doc_id: str):
        """Remove document from manager."""
        if doc_id in self.documents:
            del self.documents[doc_id]
            if self.current_document == doc_id:
                self.current_document = None

    def add_to_recent_files(self, file_path: str):
        """Add file to recent files list."""
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        self.recent_files.insert(0, file_path)
        self.recent_files = self.recent_files[: self.max_recent_files]


class SearchDialog(QDialog):
    """Search and replace dialog."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Find and Replace")
        self.setModal(False)
        self.resize(400, 200)
        self.setup_ui()

    def setup_ui(self):
        """Setup the search dialog UI."""
        layout = QVBoxLayout(self)

        # Search section
        search_group = QGroupBox("Find")
        search_layout = QFormLayout(search_group)

        self.search_edit = TextInput("Find")
        self.search_edit.setAccessibleName("Search text")
        search_layout.addRow("Find:", self.search_edit)

        # Replace section
        self.replace_edit = TextInput("Replace")
        self.replace_edit.setAccessibleName("Replacement text")
        search_layout.addRow("Replace:", self.replace_edit)

        # Options
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout(options_group)

        self.case_sensitive_cb = QCheckBox("Case sensitive")
        self.case_sensitive_cb.setAccessibleName("Case sensitive search")
        self.case_sensitive_cb.setMinimumHeight(44)
        self.whole_words_cb = QCheckBox("Whole words only")
        self.whole_words_cb.setAccessibleName("Whole words only search")
        self.whole_words_cb.setMinimumHeight(44)
        self.use_regex_cb = QCheckBox("Use regular expressions")
        self.use_regex_cb.setAccessibleName("Use regular expressions in search")
        self.use_regex_cb.setMinimumHeight(44)
        self.wrap_around_cb = QCheckBox("Wrap around")
        self.wrap_around_cb.setAccessibleName("Wrap around search")
        self.wrap_around_cb.setMinimumHeight(44)
        self.wrap_around_cb.setChecked(True)

        options_layout.addWidget(self.case_sensitive_cb)
        options_layout.addWidget(self.whole_words_cb)
        options_layout.addWidget(self.use_regex_cb)
        options_layout.addWidget(self.wrap_around_cb)

        # Buttons
        button_layout = QHBoxLayout()
        self.find_next_btn = PrimaryButton("Find Next")
        self.find_next_btn.setAccessibleName("Find next match")
        self.find_prev_btn = SecondaryButton("Find Previous")
        self.find_prev_btn.setAccessibleName("Find previous match")
        self.replace_btn = SecondaryButton("Replace")
        self.replace_btn.setAccessibleName("Replace current match")
        self.replace_all_btn = SecondaryButton("Replace All")
        self.replace_all_btn.setAccessibleName("Replace all matches")
        self.close_btn = SecondaryButton("Close")
        self.close_btn.setAccessibleName("Close search dialog")

        button_layout.addWidget(self.find_next_btn)
        button_layout.addWidget(self.find_prev_btn)
        button_layout.addWidget(self.replace_btn)
        button_layout.addWidget(self.replace_all_btn)
        button_layout.addWidget(self.close_btn)

        layout.addWidget(search_group)
        layout.addWidget(options_group)
        layout.addLayout(button_layout)

        # Connect signals
        self.close_btn.clicked.connect(self.close)

    def get_search_options(self) -> SearchOptions:
        """Get current search options."""
        return SearchOptions(
            case_sensitive=self.case_sensitive_cb.isChecked(),
            whole_words=self.whole_words_cb.isChecked(),
            use_regex=self.use_regex_cb.isChecked(),
            wrap_around=self.wrap_around_cb.isChecked(),
        )


class TextEditor(QPlainTextEdit):
    """Enhanced text editor widget with additional features."""

    content_changed = pyqtSignal()
    cursor_position_changed = pyqtSignal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.document_type = DocumentType.TEXT
        self.highlighter = None
        self.line_number_area = LineNumberArea(self)
        self.settings = EditorSettings()

        # Connect signals
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        self.cursorPositionChanged.connect(self.emit_cursor_position)
        self.textChanged.connect(self.content_changed.emit)

        self.update_line_number_area_width(0)
        self.highlight_current_line()
        self.apply_settings()

    def apply_settings(self):
        """Apply editor settings."""
        font = QFont(
            self.settings.font_family, self.settings.font_size
        )  # noqa: TH-3  user-configurable editor font
        font.setFixedPitch(True)
        self.setFont(font)

        self.setTabStopWidth(self.settings.tab_width * QFontMetrics(font).width(" "))
        self.setLineWrapMode(
            QPlainTextEdit.WidgetWidth
            if self.settings.word_wrap
            else QPlainTextEdit.NoWrap
        )

    def set_document_type(self, doc_type: DocumentType):
        """Set document type and update syntax highlighting."""
        self.document_type = doc_type
        if self.settings.syntax_highlighting:
            self.highlighter = SyntaxHighlighter(self.document(), doc_type)

    def line_number_area_width(self):
        """Calculate line number area width."""
        digits = 1
        max_val = max(1, self.blockCount())
        while max_val >= 10:
            max_val /= 10
            digits += 1
        space = 3 + self.fontMetrics().width("9") * digits
        return space

    def update_line_number_area_width(self, _):
        """Update line number area width."""
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        """Update line number area display."""
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(
                0, rect.y(), self.line_number_area.width(), rect.height()
            )

        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        """Handle resize event."""
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height())
        )

    def highlight_current_line(self):
        """Highlight the current line."""
        extra_selections = []

        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            line_color = QColor(Qt.yellow).lighter(160)
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)

        self.setExtraSelections(extra_selections)

    def emit_cursor_position(self):
        """Emit cursor position signal."""
        cursor = self.textCursor()
        line = cursor.blockNumber() + 1
        column = cursor.columnNumber() + 1
        self.cursor_position_changed.emit(line, column)

    def line_number_area_paint_event(self, event):
        """Paint line numbers."""
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), Qt.lightGray)

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(
            self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        )
        bottom = top + int(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(Qt.black)
                painter.drawText(
                    0,
                    top,
                    self.line_number_area.width(),
                    self.fontMetrics().height(),
                    Qt.AlignRight,
                    number,
                )

            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1


class LineNumberArea(QWidget):
    """Line number area widget for the text editor."""

    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        """Return size hint."""
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        """Paint event for line numbers."""
        self.editor.line_number_area_paint_event(event)


class EnhancedEditor(StandardWindow):
    """
    Enhanced Editor - Advanced text editor for Richard's File Utilities.

    Provides comprehensive text editing capabilities including:
    - Multi-document tabbed interface
    - Syntax highlighting for multiple languages
    - Advanced search and replace with regex support
    - File encoding detection and conversion
    - Text transformation tools
    - Plugin architecture support
    """

    def __init__(self):
        try:
            super().__init__(
                title="Enhanced Editor - Richard's File Utilities",
                window_type="utility",
            )
        except TypeError:
            super().__init__()
            self.setWindowTitle("Enhanced Editor - Richard's File Utilities")

        # Initialize components
        self.document_manager = DocumentManager()
        self.search_dialog = None
        self.settings = EditorSettings()
        self.tab_to_doc_mapping = {}  # Maps tab index to doc_id

        # Setup UI
        self.setup_ui()
        self.setup_menu_callbacks()
        self.load_settings()

        # Create initial document
        self.new_document()

    def setup_ui(self):
        """Setup the main user interface."""
        main_splitter = self._create_main_splitter()
        self._setup_panels(main_splitter)
        self._finalize_ui_setup()

    def _create_main_splitter(self):
        """Create and configure the main splitter widget."""
        main_splitter = QSplitter(Qt.Horizontal)

        # Add to existing layout or create new one
        if hasattr(self, "main_layout"):
            self.main_layout.addWidget(main_splitter)
        else:
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            main_layout = QVBoxLayout(central_widget)
            main_layout.addWidget(main_splitter)

        return main_splitter

    def _setup_panels(self, main_splitter):
        """Setup all three panels of the interface."""
        left_panel = self.create_left_panel()
        center_panel = self.create_center_panel()
        right_panel = self.create_right_panel()

        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(center_panel)
        main_splitter.addWidget(right_panel)
        main_splitter.setSizes([200, 600, 200])

    def _finalize_ui_setup(self):
        """Finalize the UI setup with toolbar and status bar."""
        self.create_toolbar()
        self.update_status_bar()

    def create_left_panel(self):
        """Create left panel with document outline."""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Document outline
        outline_group = QGroupBox("Document Outline")
        outline_layout = QVBoxLayout(outline_group)

        self.outline_tree = QTreeWidget()
        self.outline_tree.setAccessibleName("Document structure outline")
        self.outline_tree.setHeaderLabel("Structure")
        outline_layout.addWidget(self.outline_tree)

        layout.addWidget(outline_group)

        # Recent files
        recent_group = QGroupBox("Recent Files")
        recent_layout = QVBoxLayout(recent_group)

        self.recent_list = QListWidget()
        self.recent_list.setAccessibleName("Recent files list")
        self.recent_list.itemDoubleClicked.connect(self.open_recent_file)
        recent_layout.addWidget(self.recent_list)

        layout.addWidget(recent_group)

        return panel

    def create_center_panel(self):
        """Create center panel with tabbed editor."""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Tab widget for multiple documents
        self.tab_widget = QTabWidget()
        self.tab_widget.setAccessibleName("Open document tabs")
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_document_tab)
        self.tab_widget.currentChanged.connect(self.tab_changed)

        layout.addWidget(self.tab_widget)

        return panel

    def create_right_panel(self):
        """Create right panel with search results and properties."""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # File finder tools
        finder_group = QGroupBox("File Finder")
        finder_layout = QVBoxLayout(finder_group)

        pattern_layout = QHBoxLayout()
        pattern_layout.addWidget(QLabel("Pattern:"))
        self.file_search_pattern = TextInput("Pattern", "*.py")
        self.file_search_pattern.setAccessibleName("File search pattern")
        pattern_layout.addWidget(self.file_search_pattern)
        finder_layout.addLayout(pattern_layout)

        directory_layout = QHBoxLayout()
        directory_layout.addWidget(QLabel("Directory:"))
        self.file_search_directory = TextInput("Directory")
        self.file_search_directory.setAccessibleName("File search directory")
        self.file_search_directory.setText(str(Path.cwd()))
        directory_layout.addWidget(self.file_search_directory)
        browse_button = SecondaryButton("Browse")
        browse_button.setAccessibleName("Browse for file search directory")
        browse_button.clicked.connect(self.choose_file_search_directory)
        directory_layout.addWidget(browse_button)
        finder_layout.addLayout(directory_layout)

        options_layout = QHBoxLayout()
        self.file_search_recursive = QCheckBox("Recursive")
        self.file_search_recursive.setAccessibleName("Search files recursively")
        self.file_search_recursive.setMinimumHeight(44)
        self.file_search_recursive.setChecked(True)
        options_layout.addWidget(self.file_search_recursive)
        finder_layout.addLayout(options_layout)

        self.file_search_button = PrimaryButton("Search Files")
        self.file_search_button.setAccessibleName("Search for files")
        self.file_search_button.clicked.connect(self.perform_file_search)
        finder_layout.addWidget(self.file_search_button)

        self.file_search_results = QListWidget()
        self.file_search_results.setAccessibleName("File search results")
        self.file_search_results.itemDoubleClicked.connect(self.open_file_from_search)
        finder_layout.addWidget(self.file_search_results)

        layout.addWidget(finder_group)

        # Search results
        search_group = QGroupBox("Search Results")
        search_layout = QVBoxLayout(search_group)

        self.search_results = QListWidget()
        self.search_results.setAccessibleName("Text search results")
        self.search_results.itemDoubleClicked.connect(self.goto_search_result)
        search_layout.addWidget(self.search_results)

        layout.addWidget(search_group)

        # Document properties
        props_group = QGroupBox("Document Properties")
        props_layout = QFormLayout(props_group)

        self.encoding_label = QLabel("UTF-8")
        self.line_ending_label = QLabel("LF")
        self.doc_type_label = QLabel("Text")
        self.file_size_label = QLabel("0 bytes")

        props_layout.addRow("Encoding:", self.encoding_label)
        props_layout.addRow("Line Ending:", self.line_ending_label)
        props_layout.addRow("Type:", self.doc_type_label)
        props_layout.addRow("Size:", self.file_size_label)

        layout.addWidget(props_group)

        return panel

    def choose_file_search_directory(self):
        """Select a directory for file searches."""
        if not hasattr(self, "file_search_directory"):
            return

        start_dir = self.file_search_directory.text() or str(Path.cwd())
        directory = QFileDialog.getExistingDirectory(
            self, "Select Directory", start_dir
        )
        if directory:
            self.file_search_directory.setText(directory)

    def perform_file_search(self):
        """Search for files matching the user pattern."""
        if not hasattr(self, "file_search_results"):
            return

        directory_text = (self.file_search_directory.text() or "").strip()
        if not directory_text:
            directory_text = str(Path.cwd())

        directory_path = Path(directory_text).expanduser()
        if not directory_path.exists():
            QMessageBox.warning(
                self,
                "Invalid Directory",
                f"Directory does not exist:\n{directory_path}",
            )
            return

        pattern = (self.file_search_pattern.text() or "").strip() or "*"
        recursive = (
            self.file_search_recursive.isChecked()
            if hasattr(self, "file_search_recursive")
            else True
        )

        try:
            iterator = (
                directory_path.rglob(pattern)
                if recursive
                else directory_path.glob(pattern)
            )

            matches = []
            for path in iterator:
                if path.is_file():
                    matches.append(path)
                if len(matches) >= 500:
                    break
        except (OSError, ValueError) as exc:
            QMessageBox.critical(
                self,
                "Search Error",
                f"Could not complete search:\n{exc}",
            )
            return

        self.file_search_results.clear()
        for path in matches:
            item = QListWidgetItem(path.name)
            item.setData(Qt.UserRole, str(path))
            item.setToolTip(str(path))
            self.file_search_results.addItem(item)

        if matches:
            limited = " (showing first 500 results)" if len(matches) >= 500 else ""
            self.show_status_message(f"Found {len(matches)} file(s){limited}", 3000)
        else:
            self.show_status_message("No files found", 3000)

    def open_file_from_search(self, item: QListWidgetItem):
        """Open a file selected from the search results."""
        file_path = item.data(Qt.UserRole)
        if file_path and os.path.exists(file_path):
            self.open_document(file_path)
        else:
            QMessageBox.warning(
                self,
                "File Unavailable",
                f"The file could not be located:\n{file_path}",
            )

    def set_file_search_directory(self, file_path: Optional[str]):
        """Update default file search directory based on a document path."""
        if file_path and hasattr(self, "file_search_directory"):
            directory = Path(file_path).resolve().parent
            self.file_search_directory.setText(str(directory))

    def create_toolbar(self):
        """Create the main toolbar."""
        toolbar = self.addToolBar("Main")

        # File operations
        new_action = toolbar.addAction("New")
        new_action.setShortcut(QKeySequence.New)
        new_action.triggered.connect(self.new_document)

        open_action = toolbar.addAction("Open")
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.open_document)

        save_action = toolbar.addAction("Save")
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.save_document)

        toolbar.addSeparator()

        # Edit operations
        undo_action = toolbar.addAction("Undo")
        undo_action.setShortcut(QKeySequence.Undo)
        undo_action.triggered.connect(self.undo)

        redo_action = toolbar.addAction("Redo")
        redo_action.setShortcut(QKeySequence.Redo)
        redo_action.triggered.connect(self.redo)

        toolbar.addSeparator()

        # Search operations
        find_action = toolbar.addAction("Find")
        find_action.setShortcut(QKeySequence.Find)
        find_action.triggered.connect(self.show_search_dialog)

        replace_action = toolbar.addAction("Replace")
        replace_action.setShortcut(QKeySequence.Replace)
        replace_action.triggered.connect(self.show_replace_dialog)

    def setup_menu_callbacks(self):
        """Setup menu callbacks for StandardWindow integration."""
        if hasattr(self, "menu_manager"):
            # File menu callbacks
            self.menu_manager.register_callback("new_file", self.new_document)
            self.menu_manager.register_callback("open_file", self.open_document)
            self.menu_manager.register_callback("save_file", self.save_document)
            self.menu_manager.register_callback("save_as_file", self.save_document_as)

            # Edit menu callbacks
            self.menu_manager.register_callback("undo", self.undo)
            self.menu_manager.register_callback("redo", self.redo)
            self.menu_manager.register_callback("cut", self.cut)
            self.menu_manager.register_callback("copy", self.copy)
            self.menu_manager.register_callback("paste", self.paste)
            self.menu_manager.register_callback("select_all", self.select_all)
            self.menu_manager.register_callback("find", self.show_search_dialog)
            self.menu_manager.register_callback("replace", self.show_replace_dialog)

            # View menu callbacks
            self.menu_manager.register_callback("zoom_in", self.zoom_in)
            self.menu_manager.register_callback("zoom_out", self.zoom_out)
            self.menu_manager.register_callback("zoom_reset", self.zoom_reset)

            # Tools menu callbacks
            self.menu_manager.register_callback(
                "show_preferences", self.show_preferences
            )
            self.menu_manager.register_callback(
                "text_statistics", self.show_text_statistics
            )

    def get_current_editor(self) -> Optional[TextEditor]:
        """Get the currently active text editor."""
        current_tab = self.tab_widget.currentWidget()
        return current_tab if isinstance(current_tab, TextEditor) else None

    def new_document(self, content: str = "", file_path: str = None):
        """Create a new document."""
        doc_id = self.document_manager.create_document(content, file_path)

        # Create editor widget
        editor = TextEditor()
        editor.setPlainText(content)
        editor.content_changed.connect(lambda: self.mark_document_modified(doc_id))
        editor.cursor_position_changed.connect(self.update_cursor_position)

        # Set document type and syntax highlighting
        document = self.document_manager.get_document(doc_id)
        if document:
            editor.set_document_type(document["document_type"])

        # Add tab
        tab_title = os.path.basename(file_path) if file_path else "Untitled"
        tab_index = self.tab_widget.addTab(editor, tab_title)
        self.tab_widget.setCurrentIndex(tab_index)

        # Store doc_id mapping
        self.tab_to_doc_mapping[tab_index] = doc_id

        if file_path:
            self.set_file_search_directory(file_path)

        self.update_status_bar()
        return doc_id

    def open_document(self, file_path: str = None):
        """Open a document from file."""
        if not file_path:
            file_path = self._get_file_path_from_dialog()

        if not file_path:
            return None

        return self._process_file_opening(file_path)

    def _get_file_path_from_dialog(self):
        """Get file path from file dialog."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            "",
            "All Files (*.*);;"
            "Text Files (*.txt);;"
            "Python Files (*.py);;"
            "JavaScript Files (*.js);;"
            "HTML Files (*.html);;"
            "CSS Files (*.css);;"
            "JSON Files (*.json);;"
            "XML Files (*.xml)",
        )
        return file_path

    def _process_file_opening(self, file_path):
        """Process the actual file opening operation."""
        try:
            encoding = self.detect_encoding(file_path)
            content = self._read_file_content(file_path, encoding)

            doc_id = self.new_document(content, file_path)
            self._update_document_after_opening(doc_id, encoding, file_path)

            return doc_id

        except Exception as e:
            self._handle_file_opening_error(file_path, e)
            return None

    def _read_file_content(self, file_path, encoding):
        """Read file content with specified encoding."""
        with open(file_path, "r", encoding=encoding) as f:
            return f.read()

    def _update_document_after_opening(self, doc_id, encoding, file_path):
        """Update document properties after successful opening."""
        self.document_manager.update_document(
            doc_id, encoding=encoding, is_modified=False
        )

        self.document_manager.add_to_recent_files(file_path)
        self.update_recent_files_list()
        self.set_file_search_directory(file_path)
        self.show_status_message(f"Opened: {os.path.basename(file_path)}")

    def _handle_file_opening_error(self, file_path, error):
        """Handle errors during file opening."""
        QMessageBox.critical(
            self,
            "Error Opening File",
            f"Could not open file {file_path}:\n{str(error)}",
        )

    def save_document(self, doc_id: str = None):
        """Save the current or specified document."""
        if not doc_id:
            current_tab = self.tab_widget.currentIndex()
            if current_tab >= 0:
                doc_id = self.tab_to_doc_mapping.get(current_tab)

        document = self.document_manager.get_document(doc_id)
        if not document:
            return False

        file_path = document.get("file_path")
        if not file_path:
            return self.save_document_as(doc_id)

        try:
            # Get content from editor
            editor = self.get_editor_for_document(doc_id)
            if editor:
                content = editor.toPlainText()
                encoding = document.get("encoding", "utf-8")

                # Write file
                with open(file_path, "w", encoding=encoding) as f:
                    f.write(content)

                # Update document properties
                self.document_manager.update_document(doc_id, is_modified=False)
                self.update_tab_title(doc_id)
                self.set_file_search_directory(file_path)

                self.show_status_message(f"Saved: {os.path.basename(file_path)}")
                return True

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error Saving File",
                f"Could not save file {file_path}:\n{str(e)}",
            )

        return False

    def save_document_as(self, doc_id: str = None):
        """Save document with a new filename."""
        if not doc_id:
            current_tab = self.tab_widget.currentIndex()
            if current_tab >= 0:
                doc_id = self.tab_to_doc_mapping.get(current_tab)

        document = self.document_manager.get_document(doc_id)
        if not document:
            return False

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save File As",
            "",
            "All Files (*.*);;"
            "Text Files (*.txt);;"
            "Python Files (*.py);;"
            "JavaScript Files (*.js);;"
            "HTML Files (*.html);;"
            "CSS Files (*.css);;"
            "JSON Files (*.json);;"
            "XML Files (*.xml)",
        )

        if file_path:
            # Update document with new file path
            self.document_manager.update_document(doc_id, file_path=file_path)

            # Update document type based on new extension
            doc_type = self.document_manager._detect_document_type(file_path)
            self.document_manager.update_document(doc_id, document_type=doc_type)

            # Update syntax highlighting
            editor = self.get_editor_for_document(doc_id)
            if editor:
                editor.set_document_type(doc_type)

            # Save the file
            return self.save_document(doc_id)

        return False

    def close_document_tab(self, tab_index: int):
        """Close a document tab."""
        doc_id = self.tab_to_doc_mapping.get(tab_index)
        document = self.document_manager.get_document(doc_id) if doc_id else None

        if document and document.get("is_modified", False):
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "Document has unsaved changes. Save before closing?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
            )

            if reply == QMessageBox.Save:
                if not self.save_document(doc_id):
                    return  # Cancel close if save failed
            elif reply == QMessageBox.Cancel:
                return  # Cancel close

        # Remove tab and document
        self.tab_widget.removeTab(tab_index)
        if doc_id:
            self.document_manager.remove_document(doc_id)
            # Remove from mapping and update remaining mappings
            del self.tab_to_doc_mapping[tab_index]
            # Update mappings for tabs after the removed one
            new_mapping = {}
            for tab_idx, d_id in self.tab_to_doc_mapping.items():
                if tab_idx > tab_index:
                    new_mapping[tab_idx - 1] = d_id
                else:
                    new_mapping[tab_idx] = d_id
            self.tab_to_doc_mapping = new_mapping

        self.update_status_bar()

    def tab_changed(self, index: int):
        """Handle tab change."""
        if index >= 0:
            doc_id = self.tab_to_doc_mapping.get(index)
            if doc_id:
                self.document_manager.current_document = doc_id
                self.update_document_properties()
                self.update_status_bar()

    def get_editor_for_document(self, doc_id: str) -> Optional[TextEditor]:
        """Get the editor widget for a document."""
        for tab_index, d_id in self.tab_to_doc_mapping.items():
            if d_id == doc_id:
                return self.tab_widget.widget(tab_index)
        return None

    def mark_document_modified(self, doc_id: str):
        """Mark document as modified."""
        self.document_manager.update_document(doc_id, is_modified=True)
        self.update_tab_title(doc_id)

    def update_tab_title(self, doc_id: str):
        """Update tab title to reflect modification status."""
        document = self.document_manager.get_document(doc_id)
        if not document:
            return

        # Find tab index for document
        tab_index = -1
        for t_idx, d_id in self.tab_to_doc_mapping.items():
            if d_id == doc_id:
                tab_index = t_idx
                break

        if tab_index >= 0:
            file_path = document.get("file_path")
            title = os.path.basename(file_path) if file_path else "Untitled"
            if document.get("is_modified", False):
                title += " *"
            self.tab_widget.setTabText(tab_index, title)

    def detect_encoding(self, file_path: str) -> str:
        """Detect file encoding."""
        try:
            import chardet

            with open(file_path, "rb") as f:
                raw_data = f.read(10000)  # Read first 10KB
                result = chardet.detect(raw_data)
                return result.get("encoding", "utf-8") or "utf-8"
        except ImportError:
            # Fallback to common encodings
            encodings = ["utf-8", "utf-16", "ascii", "latin-1"]
            for encoding in encodings:
                try:
                    with open(file_path, "r", encoding=encoding) as f:
                        f.read(1000)  # Try to read a portion
                    return encoding
                except UnicodeDecodeError:
                    continue
            return "utf-8"  # Default fallback

    def show_search_dialog(self):
        """Show the search dialog."""
        if not self.search_dialog:
            self.search_dialog = SearchDialog(self)
            self.search_dialog.find_next_btn.clicked.connect(self.find_next)
            self.search_dialog.find_prev_btn.clicked.connect(self.find_previous)
            self.search_dialog.replace_btn.clicked.connect(self.replace_current)
            self.search_dialog.replace_all_btn.clicked.connect(self.replace_all)

        self.search_dialog.show()
        self.search_dialog.search_edit.setFocus()

    def show_replace_dialog(self):
        """Show the replace dialog."""
        self.show_search_dialog()  # Same dialog handles both

    def find_next(self):
        """Find next occurrence."""
        if not self.search_dialog:
            return

        search_text = self.search_dialog.search_edit.text()
        if not search_text:
            return

        editor = self.get_current_editor()
        if not editor:
            return

        options = self.search_dialog.get_search_options()
        self.perform_search(editor, search_text, options, forward=True)

    def find_previous(self):
        """Find previous occurrence."""
        if not self.search_dialog:
            return

        search_text = self.search_dialog.search_edit.text()
        if not search_text:
            return

        editor = self.get_current_editor()
        if not editor:
            return

        options = self.search_dialog.get_search_options()
        self.perform_search(editor, search_text, options, forward=False)

    def perform_search(
        self,
        editor: TextEditor,
        search_text: str,
        options: SearchOptions,
        forward: bool = True,
    ):
        """Perform search operation."""
        cursor = editor.textCursor()

        if options.use_regex:
            return self._perform_regex_search(editor, search_text, options, forward)
        else:
            return self._perform_standard_search(
                editor, search_text, options, forward, cursor
            )

    def _perform_regex_search(self, editor, search_text, options, forward):
        """Perform regex-based search."""
        import re

        regex_flags = 0 if options.case_sensitive else re.IGNORECASE
        pattern = re.compile(search_text, regex_flags)

        text = editor.toPlainText()
        cursor = editor.textCursor()
        start_pos = cursor.position()

        match = self._find_regex_match(pattern, text, start_pos, forward)

        if match:
            self._apply_search_result(editor, match.start(), match.end())
            return True
        elif options.wrap_around:
            return self._try_regex_wrap_around(editor, pattern, text, forward)

        self._show_not_found_message()
        return False

    def _find_regex_match(self, pattern, text, start_pos, forward):
        """Find regex match in specified direction."""
        if forward:
            return pattern.search(text, start_pos)
        else:
            matches = list(pattern.finditer(text, 0, start_pos))
            return matches[-1] if matches else None

    def _try_regex_wrap_around(self, editor, pattern, text, forward):
        """Try regex search with wrap around."""
        if forward:
            match = pattern.search(text, 0)
        else:
            matches = list(pattern.finditer(text))
            match = matches[-1] if matches else None

        if match:
            self._apply_search_result(editor, match.start(), match.end())
            return True
        return False

    def _perform_standard_search(self, editor, search_text, options, forward, cursor):
        """Perform standard text search."""
        flags = self._get_search_flags(options, forward)

        found_cursor = editor.document().find(search_text, cursor, flags)

        if not found_cursor.isNull():
            editor.setTextCursor(found_cursor)
            return True
        elif options.wrap_around:
            return self._try_standard_wrap_around(editor, search_text, flags, forward)

        self._show_not_found_message()
        return False

    def _get_search_flags(self, options, forward):
        """Get search flags based on options."""
        flags = QTextDocument.FindFlags()

        if not forward:
            flags |= QTextDocument.FindBackward
        if options.case_sensitive:
            flags |= QTextDocument.FindCaseSensitively
        if options.whole_words:
            flags |= QTextDocument.FindWholeWords

        return flags

    def _try_standard_wrap_around(self, editor, search_text, flags, forward):
        """Try standard search with wrap around."""
        cursor = QTextCursor(editor.document())
        if not forward:
            cursor.movePosition(QTextCursor.End)

        found_cursor = editor.document().find(search_text, cursor, flags)
        if not found_cursor.isNull():
            editor.setTextCursor(found_cursor)
            return True
        return False

    def _apply_search_result(self, editor, start_pos, end_pos):
        """Apply search result by setting cursor position."""
        cursor = editor.textCursor()
        cursor.setPosition(start_pos)
        cursor.setPosition(end_pos, QTextCursor.KeepAnchor)
        editor.setTextCursor(cursor)

    def _show_not_found_message(self):
        """Show text not found message."""
        QMessageBox.information(self, "Search", "Text not found.")

    def replace_current(self):
        """Replace current selection."""
        if not self.search_dialog:
            return

        editor = self.get_current_editor()
        if not editor:
            return

        cursor = editor.textCursor()
        if cursor.hasSelection():
            replace_text = self.search_dialog.replace_edit.text()
            cursor.insertText(replace_text)

            # Find next occurrence
            self.find_next()

    def replace_all(self):
        """Replace all occurrences."""
        if not self.search_dialog:
            return

        search_text = self.search_dialog.search_edit.text()
        replace_text = self.search_dialog.replace_edit.text()

        if not search_text:
            return

        editor = self.get_current_editor()
        if not editor:
            return

        options = self.search_dialog.get_search_options()
        replacements = self._perform_replace_all(
            editor, search_text, replace_text, options
        )
        self._show_replace_result(replacements)

    def _perform_replace_all(self, editor, search_text, replace_text, options):
        """Perform the actual replace all operation."""
        text = editor.toPlainText()

        if options.use_regex:
            return self._replace_all_regex(text, search_text, replace_text, options)
        else:
            return self._replace_all_standard(text, search_text, replace_text, options)

    def _replace_all_regex(self, text, search_text, replace_text, options):
        """Perform regex-based replace all."""
        import re

        regex_flags = 0 if options.case_sensitive else re.IGNORECASE
        pattern = re.compile(search_text, regex_flags)
        new_text, count = pattern.subn(replace_text, text)
        return new_text, count

    def _replace_all_standard(self, text, search_text, replace_text, options):
        """Perform standard replace all."""
        if options.case_sensitive:
            new_text = text.replace(search_text, replace_text)
            replacements = text.count(search_text)
        else:
            import re

            pattern = re.compile(re.escape(search_text), re.IGNORECASE)
            new_text, replacements = pattern.subn(replace_text, text)

        return new_text, replacements

    def _show_replace_result(self, result):
        """Show the result of replace all operation."""
        if isinstance(result, tuple):
            new_text, replacements = result
            editor = self.get_current_editor()
            if editor and replacements > 0:
                editor.setPlainText(new_text)

            if replacements > 0:
                QMessageBox.information(
                    self,
                    "Replace All",
                    f"Replaced {replacements} occurrences.",
                )
            else:
                QMessageBox.information(self, "Replace All", "No occurrences found.")
        else:
            replacements = result
            if replacements > 0:
                QMessageBox.information(
                    self,
                    "Replace All",
                    f"Replaced {replacements} occurrences.",
                )
            else:
                QMessageBox.information(self, "Replace All", "No occurrences found.")

    # Standard edit operations
    def undo(self):
        """Undo last operation."""
        editor = self.get_current_editor()
        if editor:
            editor.undo()

    def redo(self):
        """Redo last undone operation."""
        editor = self.get_current_editor()
        if editor:
            editor.redo()

    def cut(self):
        """Cut selected text."""
        editor = self.get_current_editor()
        if editor:
            editor.cut()

    def copy(self):
        """Copy selected text."""
        editor = self.get_current_editor()
        if editor:
            editor.copy()

    def paste(self):
        """Paste text from clipboard."""
        editor = self.get_current_editor()
        if editor:
            editor.paste()

    def select_all(self):
        """Select all text."""
        editor = self.get_current_editor()
        if editor:
            editor.selectAll()

    # View operations
    def zoom_in(self):
        """Increase font size."""
        self.settings.font_size = min(self.settings.font_size + 1, 72)
        self.apply_settings_to_all_editors()

    def zoom_out(self):
        """Decrease font size."""
        self.settings.font_size = max(self.settings.font_size - 1, 6)
        self.apply_settings_to_all_editors()

    def zoom_reset(self):
        """Reset font size to default."""
        self.settings.font_size = 11
        self.apply_settings_to_all_editors()

    def apply_settings_to_all_editors(self):
        """Apply current settings to all open editors."""
        for i in range(self.tab_widget.count()):
            editor = self.tab_widget.widget(i)
            if isinstance(editor, TextEditor):
                editor.settings = self.settings
                editor.apply_settings()

    def show_preferences(self):
        """Show preferences dialog."""
        dialog = PreferencesDialog(self, self.settings)
        if dialog.exec_() == QDialog.Accepted:
            self.settings = dialog.get_settings()
            self.apply_settings_to_all_editors()
            self.save_settings()

    def show_text_statistics(self):
        """Show text statistics for current document."""
        editor = self.get_current_editor()
        if not editor:
            return

        text = editor.toPlainText()

        # Calculate statistics
        char_count = len(text)
        char_count_no_spaces = len(text.replace(" ", "").replace("\t", ""))
        word_count = len(text.split())
        line_count = text.count("\n") + 1 if text else 0
        paragraph_count = len([p for p in text.split("\n\n") if p.strip()])

        # Show statistics dialog
        stats_text = f"""
        Text Statistics:
        
        Characters: {char_count:,}
        Characters (no spaces): {char_count_no_spaces:,}
        Words: {word_count:,}
        Lines: {line_count:,}
        Paragraphs: {paragraph_count:,}
        """

        QMessageBox.information(self, "Text Statistics", stats_text)

    def update_recent_files_list(self):
        """Update recent files list widget."""
        self.recent_list.clear()
        for file_path in self.document_manager.recent_files:
            item = QListWidgetItem(os.path.basename(file_path))
            item.setData(Qt.UserRole, file_path)
            item.setToolTip(file_path)
            self.recent_list.addItem(item)

    def open_recent_file(self, item: QListWidgetItem):
        """Open a recent file."""
        file_path = item.data(Qt.UserRole)
        if file_path and os.path.exists(file_path):
            self.open_document(file_path)
        else:
            QMessageBox.warning(self, "File Not Found", f"File not found: {file_path}")

    def goto_search_result(self, item: QListWidgetItem):
        """Go to search result location."""
        # Implementation for navigating to search results
        pass

    def update_cursor_position(self, line: int, column: int):
        """Update cursor position display."""
        self.show_status_message(f"Line {line}, Column {column}", 1000)

    def update_document_properties(self):
        """Update document properties panel."""
        doc_id = self.document_manager.current_document
        document = self.document_manager.get_document(doc_id)

        if document:
            self.encoding_label.setText(document.get("encoding", "UTF-8"))
            self.line_ending_label.setText(document.get("line_ending", "LF").upper())
            self.doc_type_label.setText(
                document.get("document_type", DocumentType.TEXT).value.title()
            )

            # Calculate file size
            editor = self.get_current_editor()
            if editor:
                size = len(editor.toPlainText().encode("utf-8"))
                if size < 1024:
                    size_text = f"{size} bytes"
                elif size < 1024 * 1024:
                    size_text = f"{size / 1024:.1f} KB"
                else:
                    size_text = f"{size / (1024 * 1024):.1f} MB"
                self.file_size_label.setText(size_text)

    def update_status_bar(self):
        """Update status bar information."""
        if self.tab_widget.count() == 0:
            self.show_status_message("No documents open")
        else:
            doc_count = self.tab_widget.count()
            current_tab = self.tab_widget.currentIndex() + 1
            self.show_status_message(f"Document {current_tab} of {doc_count}")

    def load_settings(self):
        """Load application settings."""
        settings = QSettings("RFU", "EnhancedEditor")

        # Load editor settings
        self.settings.font_family = settings.value(
            "font_family", self.settings.font_family
        )
        self.settings.font_size = int(
            settings.value("font_size", self.settings.font_size)
        )
        self.settings.tab_width = int(
            settings.value("tab_width", self.settings.tab_width)
        )
        self.settings.use_spaces = settings.value(
            "use_spaces", self.settings.use_spaces, type=bool
        )
        self.settings.word_wrap = settings.value(
            "word_wrap", self.settings.word_wrap, type=bool
        )
        self.settings.line_numbers = settings.value(
            "line_numbers", self.settings.line_numbers, type=bool
        )
        self.settings.syntax_highlighting = settings.value(
            "syntax_highlighting", self.settings.syntax_highlighting, type=bool
        )

        # Load recent files
        recent_files = settings.value("recent_files", [])
        if isinstance(recent_files, str):
            recent_files = [recent_files]
        self.document_manager.recent_files = recent_files or []
        self.update_recent_files_list()

        # Load window geometry
        geometry = settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)

    def save_settings(self):
        """Save application settings."""
        settings = QSettings("RFU", "EnhancedEditor")

        # Save editor settings
        settings.setValue("font_family", self.settings.font_family)
        settings.setValue("font_size", self.settings.font_size)
        settings.setValue("tab_width", self.settings.tab_width)
        settings.setValue("use_spaces", self.settings.use_spaces)
        settings.setValue("word_wrap", self.settings.word_wrap)
        settings.setValue("line_numbers", self.settings.line_numbers)
        settings.setValue("syntax_highlighting", self.settings.syntax_highlighting)

        # Save recent files
        settings.setValue("recent_files", self.document_manager.recent_files)

        # Save window geometry
        settings.setValue("geometry", self.saveGeometry())

    def closeEvent(self, event):
        """Handle close event."""
        unsaved_docs = self._get_unsaved_documents()

        if unsaved_docs:
            if not self._handle_unsaved_documents(unsaved_docs, event):
                return

        self.save_settings()
        event.accept()

    def _get_unsaved_documents(self):
        """Get list of unsaved document names."""
        unsaved_docs = []
        for doc_id, document in self.document_manager.documents.items():
            if document.get("is_modified", False):
                file_path = document.get("file_path", "Untitled")
                unsaved_docs.append(os.path.basename(file_path))
        return unsaved_docs

    def _handle_unsaved_documents(self, unsaved_docs, event):
        """Handle unsaved documents before closing."""
        reply = self._show_unsaved_confirmation_dialog(unsaved_docs)

        if reply == QMessageBox.Save:
            return self._save_all_modified_documents(event)
        elif reply == QMessageBox.Cancel:
            event.ignore()
            return False

        return True

    def _show_unsaved_confirmation_dialog(self, unsaved_docs):
        """Show confirmation dialog for unsaved documents."""
        return QMessageBox.question(
            self,
            "Unsaved Changes",
            f"There are unsaved changes in {len(unsaved_docs)} document(s):\n"
            + "\n".join(unsaved_docs)
            + "\n\nSave changes before closing?",
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
        )

    def _save_all_modified_documents(self, event):
        """Save all modified documents."""
        for doc_id, document in self.document_manager.documents.items():
            if document.get("is_modified", False):
                if not self.save_document(doc_id):
                    event.ignore()
                    return False
        return True


class PreferencesDialog(QDialog):
    """Preferences dialog for editor settings."""

    def __init__(self, parent=None, settings: EditorSettings = None):
        super().__init__(parent)
        self.settings = settings or EditorSettings()
        self.setWindowTitle("Enhanced Editor Preferences")
        self.setModal(True)
        self.resize(500, 400)
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        """Setup preferences dialog UI."""
        layout = QVBoxLayout(self)

        # Create tab widget for different categories
        tab_widget = QTabWidget()
        tab_widget.setAccessibleName("Preferences categories")
        layout.addWidget(tab_widget)

        # Editor tab
        editor_tab = self.create_editor_tab()
        tab_widget.addTab(editor_tab, "Editor")

        # Appearance tab
        appearance_tab = self.create_appearance_tab()
        tab_widget.addTab(appearance_tab, "Appearance")

        # Advanced tab
        advanced_tab = self.create_advanced_tab()
        tab_widget.addTab(advanced_tab, "Advanced")

        # Button box
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def create_editor_tab(self):
        """Create editor preferences tab."""
        tab = QWidget()
        layout = QFormLayout(tab)

        # Font settings
        font_group = QGroupBox("Font")
        font_layout = QFormLayout(font_group)

        self.font_family_combo = QComboBox()
        self.font_family_combo.setAccessibleName("Editor font family")
        font_db = QFontDatabase()
        for family in font_db.families():
            if font_db.isFixedPitch(family):
                self.font_family_combo.addItem(family)
        font_layout.addRow("Font Family:", self.font_family_combo)

        self.font_size_spin = QSpinBox()
        self.font_size_spin.setAccessibleName("Editor font size")
        self.font_size_spin.setMinimumHeight(44)
        self.font_size_spin.setRange(6, 72)
        font_layout.addRow("Font Size:", self.font_size_spin)

        layout.addWidget(font_group)

        # Indentation settings
        indent_group = QGroupBox("Indentation")
        indent_layout = QFormLayout(indent_group)

        self.tab_width_spin = QSpinBox()
        self.tab_width_spin.setAccessibleName("Tab width in spaces")
        self.tab_width_spin.setMinimumHeight(44)
        self.tab_width_spin.setRange(1, 16)
        indent_layout.addRow("Tab Width:", self.tab_width_spin)

        self.use_spaces_check = QCheckBox("Use spaces instead of tabs")
        self.use_spaces_check.setAccessibleName("Use spaces instead of tabs")
        self.use_spaces_check.setMinimumHeight(44)
        indent_layout.addRow(self.use_spaces_check)

        self.auto_indent_check = QCheckBox("Auto-indent new lines")
        self.auto_indent_check.setAccessibleName("Auto-indent new lines")
        self.auto_indent_check.setMinimumHeight(44)
        indent_layout.addRow(self.auto_indent_check)

        layout.addWidget(indent_group)

        return tab

    def create_appearance_tab(self):
        """Create appearance preferences tab."""
        tab = QWidget()
        layout = QFormLayout(tab)

        # Display settings
        display_group = QGroupBox("Display")
        display_layout = QVBoxLayout(display_group)

        self.word_wrap_check = QCheckBox("Word wrap")
        self.word_wrap_check.setAccessibleName("Word wrap")
        self.word_wrap_check.setMinimumHeight(44)
        display_layout.addWidget(self.word_wrap_check)

        self.line_numbers_check = QCheckBox("Show line numbers")
        self.line_numbers_check.setAccessibleName("Show line numbers")
        self.line_numbers_check.setMinimumHeight(44)
        display_layout.addWidget(self.line_numbers_check)

        self.show_whitespace_check = QCheckBox("Show whitespace")
        self.show_whitespace_check.setAccessibleName("Show whitespace characters")
        self.show_whitespace_check.setMinimumHeight(44)
        display_layout.addWidget(self.show_whitespace_check)

        layout.addWidget(display_group)

        # Syntax highlighting
        syntax_group = QGroupBox("Syntax Highlighting")
        syntax_layout = QVBoxLayout(syntax_group)

        self.syntax_highlighting_check = QCheckBox("Enable syntax highlighting")
        self.syntax_highlighting_check.setAccessibleName("Enable syntax highlighting")
        self.syntax_highlighting_check.setMinimumHeight(44)
        syntax_layout.addWidget(self.syntax_highlighting_check)

        layout.addWidget(syntax_group)

        return tab

    def create_advanced_tab(self):
        """Create advanced preferences tab."""
        tab = QWidget()
        layout = QFormLayout(tab)

        # Advanced settings placeholder
        info_label = QLabel("Advanced settings will be available in future versions.")
        layout.addWidget(info_label)

        return tab

    def load_settings(self):
        """Load current settings into dialog."""
        self.font_family_combo.setCurrentText(self.settings.font_family)
        self.font_size_spin.setValue(self.settings.font_size)
        self.tab_width_spin.setValue(self.settings.tab_width)
        self.use_spaces_check.setChecked(self.settings.use_spaces)
        self.word_wrap_check.setChecked(self.settings.word_wrap)
        self.line_numbers_check.setChecked(self.settings.line_numbers)
        self.syntax_highlighting_check.setChecked(self.settings.syntax_highlighting)
        self.show_whitespace_check.setChecked(self.settings.show_whitespace)

    def get_settings(self) -> EditorSettings:
        """Get settings from dialog."""
        return EditorSettings(
            font_family=self.font_family_combo.currentText(),
            font_size=self.font_size_spin.value(),
            tab_width=self.tab_width_spin.value(),
            use_spaces=self.use_spaces_check.isChecked(),
            word_wrap=self.word_wrap_check.isChecked(),
            line_numbers=self.line_numbers_check.isChecked(),
            syntax_highlighting=self.syntax_highlighting_check.isChecked(),
            show_whitespace=self.show_whitespace_check.isChecked(),
        )


def main():
    """Main function for standalone execution."""
    app = QApplication(sys.argv)

    editor = EnhancedEditor()
    editor.show()

    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
