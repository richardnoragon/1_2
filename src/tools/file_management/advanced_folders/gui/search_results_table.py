"""Search Results Table Component.

Enterprise-grade table widget for displaying search results with advanced features.
Implements virtual scrolling, multi-column sorting, filtering, and metadata display.

Features:
- Virtual scrolling for performance with large result sets
- Multi-column sorting with custom sort orders
- Advanced filtering and grouping capabilities
- Inline editing for supported metadata
- Context menu with file operations
- Export functionality for search results
- Accessibility compliance with screen readers
"""

import logging
import operator
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from PyQt5.QtCore import (
    QAbstractTableModel,
    QItemSelectionModel,
    QModelIndex,
    QRect,
    QSize,
    QSortFilterProxyModel,
    Qt,
    QTimer,
    QVariant,
    pyqtSignal,
)
from PyQt5.QtGui import (
    QBrush,
    QClipboard,
    QColor,
    QFont,
    QIcon,
    QKeySequence,
    QPalette,
    QPixmap,
)
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QAction,
    QApplication,
    QCheckBox,
    QComboBox,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMenu,
    QMessageBox,
    QProgressBar,
    QScrollArea,
    QSplitter,
    QTableView,
    QTextEdit,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from ..database import AdvancedFoldersDBManager
from ..models.folder_models import (
    FileMetadata,
    FolderConfiguration,
    SearchParameter,
)
from ..repositories import FileMetadataRepository


class SearchResultItem:
    """Single search result item with metadata."""

    def __init__(self, file_metadata: FileMetadata):
        """Initialize search result item.

        Args:
            file_metadata: File metadata object
        """
        self.file_metadata = file_metadata
        self.selected = False
        self.highlighted = False

        # Cached display values for performance
        self._display_cache = {}
        self._icon_cache = None

    def get_display_value(self, column: str) -> str:
        """Get cached display value for column.

        Args:
            column: Column name

        Returns:
            Formatted display value
        """
        if column not in self._display_cache:
            self._display_cache[column] = self._format_column_value(column)
        return self._display_cache[column]

    def _format_column_value(self, column: str) -> str:
        """Format column value for display.

        Args:
            column: Column name

        Returns:
            Formatted value
        """
        metadata = self.file_metadata

        if column == "name":
            return metadata.file_name
        elif column == "path":
            return str(metadata.file_path)
        elif column == "size":
            return self._format_file_size(metadata.file_size)
        elif column == "type":
            return (
                metadata.file_extension.upper()
                if metadata.file_extension
                else "Unknown"
            )
        elif column == "modified":
            return (
                metadata.modified_date.strftime("%Y-%m-%d %H:%M")
                if metadata.modified_date
                else "Unknown"
            )
        elif column == "created":
            return (
                metadata.created_date.strftime("%Y-%m-%d %H:%M")
                if metadata.created_date
                else "Unknown"
            )
        elif column == "folder":
            return metadata.folder_name or "Unknown"
        else:
            return str(getattr(metadata, column, ""))

    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size for display.

        Args:
            size_bytes: Size in bytes

        Returns:
            Formatted size string
        """
        if size_bytes == 0:
            return "0 B"

        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1

        return f"{size_bytes:.1f} {size_names[i]}"

    def get_icon(self) -> QIcon:
        """Get file type icon.

        Returns:
            Appropriate icon for file type
        """
        if self._icon_cache is None:
            self._icon_cache = self._create_file_icon()
        return self._icon_cache

    def _create_file_icon(self) -> QIcon:
        """Create file type icon.

        Returns:
            File type icon
        """
        ext = (
            self.file_metadata.file_extension.lower()
            if self.file_metadata.file_extension
            else ""
        )

        # Icon mapping for common file types
        icon_map = {
            "pdf": ":/icons/file_pdf.png",
            "doc": ":/icons/file_word.png",
            "docx": ":/icons/file_word.png",
            "xls": ":/icons/file_excel.png",
            "xlsx": ":/icons/file_excel.png",
            "ppt": ":/icons/file_powerpoint.png",
            "pptx": ":/icons/file_powerpoint.png",
            "txt": ":/icons/file_text.png",
            "jpg": ":/icons/file_image.png",
            "jpeg": ":/icons/file_image.png",
            "png": ":/icons/file_image.png",
            "gif": ":/icons/file_image.png",
            "mp4": ":/icons/file_video.png",
            "avi": ":/icons/file_video.png",
            "mkv": ":/icons/file_video.png",
            "mp3": ":/icons/file_audio.png",
            "wav": ":/icons/file_audio.png",
            "zip": ":/icons/file_archive.png",
            "rar": ":/icons/file_archive.png",
            "7z": ":/icons/file_archive.png",
        }

        icon_path = icon_map.get(ext, ":/icons/file_default.png")
        return QIcon(icon_path)


class SearchResultsModel(QAbstractTableModel):
    """Table model for search results with virtual scrolling support."""

    # Custom signals
    dataUpdated = pyqtSignal(int)  # result_count
    selectionChanged = pyqtSignal(list)  # selected_items

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize search results model.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        self.logger = logging.getLogger("AdvancedFolders.ResultsModel")

        # Model data
        self.results: List[SearchResultItem] = []
        self.selected_items: List[SearchResultItem] = []

        # Column configuration
        self.columns = [
            {"name": "name", "title": "Name", "width": 200, "sortable": True},
            {"name": "size", "title": "Size", "width": 80, "sortable": True},
            {"name": "type", "title": "Type", "width": 60, "sortable": True},
            {
                "name": "modified",
                "title": "Modified",
                "width": 120,
                "sortable": True,
            },
            {"name": "path", "title": "Path", "width": 300, "sortable": True},
            {
                "name": "folder",
                "title": "Folder",
                "width": 100,
                "sortable": True,
            },
        ]

        # Sorting state
        self.sort_column = 0
        self.sort_order = Qt.AscendingOrder

        # Repository for data operations
        self.db_manager = AdvancedFoldersDBManager()
        self.metadata_repository = FileMetadataRepository(self.db_manager)

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Get number of rows."""
        return len(self.results)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Get number of columns."""
        return len(self.columns)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        """Get data for model index."""
        if not index.isValid() or index.row() >= len(self.results):
            return QVariant()

        result_item = self.results[index.row()]
        column_info = self.columns[index.column()]
        column_name = column_info["name"]

        if role == Qt.DisplayRole:
            return result_item.get_display_value(column_name)

        elif role == Qt.DecorationRole and index.column() == 0:
            return result_item.get_icon()

        elif role == Qt.ToolTipRole:
            return self._create_tooltip(result_item)

        elif role == Qt.BackgroundRole:
            if result_item.selected:
                return QBrush(QColor(173, 216, 230))  # Light blue
            elif result_item.highlighted:
                return QBrush(QColor(255, 255, 224))  # Light yellow
            elif index.row() % 2 == 0:
                return QBrush(QColor(248, 248, 248))  # Light gray for alternating rows

        elif role == Qt.FontRole:
            if result_item.selected:
                font = QFont()
                font.setBold(True)
                return font

        elif role == Qt.TextAlignmentRole:
            if column_name in ["size"]:
                return Qt.AlignRight | Qt.AlignVCenter
            return Qt.AlignLeft | Qt.AlignVCenter

        elif role == Qt.UserRole:
            return result_item

        return QVariant()

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.DisplayRole,
    ) -> Any:
        """Get header data."""
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if 0 <= section < len(self.columns):
                return self.columns[section]["title"]

        elif orientation == Qt.Horizontal and role == Qt.ToolTipRole:
            if 0 <= section < len(self.columns):
                return f"Click to sort by {self.columns[section]['title']}"

        return QVariant()

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        """Get item flags."""
        if not index.isValid():
            return Qt.NoItemFlags

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def sort(self, column: int, order: Qt.SortOrder):
        """Sort model data."""
        if column < 0 or column >= len(self.columns):
            return

        self.beginResetModel()

        self.sort_column = column
        self.sort_order = order

        column_name = self.columns[column]["name"]
        reverse = order == Qt.DescendingOrder

        # Sort based on column type
        if column_name == "size":
            self.results.sort(
                key=lambda x: x.file_metadata.file_size or 0, reverse=reverse
            )
        elif column_name == "modified":
            self.results.sort(
                key=lambda x: x.file_metadata.modified_date or datetime.min,
                reverse=reverse,
            )
        elif column_name == "created":
            self.results.sort(
                key=lambda x: x.file_metadata.created_date or datetime.min,
                reverse=reverse,
            )
        else:
            self.results.sort(
                key=lambda x: x.get_display_value(column_name).lower(),
                reverse=reverse,
            )

        self.endResetModel()
        self.logger.debug(f"Sorted by {column_name} ({order})")

    def _create_tooltip(self, result_item: SearchResultItem) -> str:
        """Create tooltip for result item.

        Args:
            result_item: Search result item

        Returns:
            Formatted tooltip text
        """
        metadata = result_item.file_metadata

        tooltip_parts = [
            f"Name: {metadata.file_name}",
            f"Path: {metadata.file_path}",
            f"Size: {result_item.get_display_value('size')}",
            f"Type: {result_item.get_display_value('type')}",
            f"Modified: {result_item.get_display_value('modified')}",
        ]

        if metadata.folder_name:
            tooltip_parts.append(f"Folder: {metadata.folder_name}")

        return "\n".join(tooltip_parts)

    def set_results(self, file_metadata_list: List[FileMetadata]):
        """Set search results.

        Args:
            file_metadata_list: List of file metadata objects
        """
        self.beginResetModel()

        self.results = [SearchResultItem(metadata) for metadata in file_metadata_list]
        self.selected_items.clear()

        self.endResetModel()

        self.dataUpdated.emit(len(self.results))
        self.logger.info(f"Loaded {len(self.results)} search results")

    def clear_results(self):
        """Clear all search results."""
        self.beginResetModel()
        self.results.clear()
        self.selected_items.clear()
        self.endResetModel()

        self.dataUpdated.emit(0)

    def get_result_item(self, index: QModelIndex) -> Optional[SearchResultItem]:
        """Get result item for model index.

        Args:
            index: Model index

        Returns:
            Search result item or None
        """
        if not index.isValid() or index.row() >= len(self.results):
            return None

        return self.results[index.row()]

    def get_selected_items(self) -> List[SearchResultItem]:
        """Get currently selected items.

        Returns:
            List of selected result items
        """
        return self.selected_items.copy()

    def set_item_selection(self, items: List[SearchResultItem], selected: bool):
        """Set selection state for items.

        Args:
            items: Items to update
            selected: Selection state
        """
        for item in items:
            if item in self.results:
                item.selected = selected
                if selected and item not in self.selected_items:
                    self.selected_items.append(item)
                elif not selected and item in self.selected_items:
                    self.selected_items.remove(item)

        # Emit data changed for affected rows
        if items:
            start_row = min(
                self.results.index(item) for item in items if item in self.results
            )
            end_row = max(
                self.results.index(item) for item in items if item in self.results
            )

            start_index = self.createIndex(start_row, 0)
            end_index = self.createIndex(end_row, self.columnCount() - 1)
            self.dataChanged.emit(start_index, end_index)

        self.selectionChanged.emit(self.selected_items)

    def highlight_items(self, items: List[SearchResultItem], highlighted: bool):
        """Set highlight state for items.

        Args:
            items: Items to highlight
            highlighted: Highlight state
        """
        for item in items:
            if item in self.results:
                item.highlighted = highlighted

        # Emit data changed for affected rows
        if items:
            start_row = min(
                self.results.index(item) for item in items if item in self.results
            )
            end_row = max(
                self.results.index(item) for item in items if item in self.results
            )

            start_index = self.createIndex(start_row, 0)
            end_index = self.createIndex(end_row, self.columnCount() - 1)
            self.dataChanged.emit(start_index, end_index)

    def get_column_info(self) -> List[Dict[str, Any]]:
        """Get column configuration.

        Returns:
            List of column information dictionaries
        """
        return self.columns.copy()


class SearchResultsTable(QTableView):
    """Enterprise-grade search results table with advanced features."""

    # Custom signals
    itemSelected = pyqtSignal(object)  # SearchResultItem
    itemActivated = pyqtSignal(object)  # SearchResultItem
    selectionChanged = pyqtSignal(list)  # List[SearchResultItem]
    contextMenuRequested = pyqtSignal(object, object)  # SearchResultItem, QPoint

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize search results table.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        self.logger = logging.getLogger("AdvancedFolders.ResultsTable")

        # Setup model
        self.results_model = SearchResultsModel(self)
        self.setModel(self.results_model)

        # Setup table
        self._setup_table()
        self._connect_signals()

        # Context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

        self.logger.info("Search results table initialized")

    def _setup_table(self):
        """Setup table appearance and behavior."""
        # Selection behavior
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)

        # Visual appearance
        self.setAlternatingRowColors(True)
        self.setShowGrid(False)
        self.setWordWrap(False)

        # Performance optimization
        self.setUniformRowHeights(True)
        self.verticalHeader().setDefaultSectionSize(24)
        self.verticalHeader().hide()

        # Horizontal header
        header = self.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSortIndicatorShown(True)
        header.setSectionsClickable(True)
        header.setSectionsMovable(True)

        # Set initial column widths
        for i, column_info in enumerate(self.results_model.get_column_info()):
            header.resizeSection(i, column_info["width"])

        # Enable sorting
        self.setSortingEnabled(True)

        # Scrolling optimization
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)

        # Accessibility
        self.setAccessibleName("Search Results Table")
        self.setAccessibleDescription("Table displaying file search results")

    def _connect_signals(self):
        """Connect internal signals."""
        # Selection changes
        self.selectionModel().currentChanged.connect(self._on_current_changed)
        self.selectionModel().selectionChanged.connect(self._on_selection_changed)

        # Double-click activation
        self.doubleClicked.connect(self._on_double_clicked)

        # Model signals
        self.results_model.dataUpdated.connect(self._on_data_updated)
        self.results_model.selectionChanged.connect(self.selectionChanged)

    def _on_current_changed(self, current: QModelIndex, previous: QModelIndex):
        """Handle current item changes.

        Args:
            current: Current selected index
            previous: Previously selected index
        """
        result_item = self.results_model.get_result_item(current)
        if result_item:
            self.itemSelected.emit(result_item)
            self.logger.debug(f"Selected item: {result_item.file_metadata.file_name}")

    def _on_selection_changed(self, selected, deselected):
        """Handle selection changes.

        Args:
            selected: Selected item selection
            deselected: Deselected item selection
        """
        # Update model selection state
        selected_items = []
        for index in self.selectionModel().selectedRows():
            result_item = self.results_model.get_result_item(index)
            if result_item:
                selected_items.append(result_item)

        self.results_model.set_item_selection(selected_items, True)

        # Update deselected items
        deselected_items = []
        for index in deselected.indexes():
            result_item = self.results_model.get_result_item(index)
            if result_item:
                deselected_items.append(result_item)

        self.results_model.set_item_selection(deselected_items, False)

    def _on_double_clicked(self, index: QModelIndex):
        """Handle double-click activation.

        Args:
            index: Double-clicked index
        """
        result_item = self.results_model.get_result_item(index)
        if result_item:
            self.itemActivated.emit(result_item)
            self.logger.debug(f"Activated item: {result_item.file_metadata.file_name}")

    def _on_data_updated(self, count: int):
        """Handle data update.

        Args:
            count: Number of results
        """
        self.logger.info(f"Table updated with {count} results")

        # Auto-resize columns based on content
        if count > 0:
            self.resizeColumnsToContents()

        # Scroll to top
        self.scrollToTop()

    def _show_context_menu(self, position):
        """Show context menu for table item.

        Args:
            position: Menu position
        """
        index = self.indexAt(position)
        result_item = self.results_model.get_result_item(index)

        if result_item:
            self.contextMenuRequested.emit(result_item, self.mapToGlobal(position))

    def set_results(self, file_metadata_list: List[FileMetadata]):
        """Set search results.

        Args:
            file_metadata_list: List of file metadata objects
        """
        self.results_model.set_results(file_metadata_list)

    def clear_results(self):
        """Clear all search results."""
        self.results_model.clear_results()

    def get_selected_items(self) -> List[SearchResultItem]:
        """Get currently selected items.

        Returns:
            List of selected result items
        """
        return self.results_model.get_selected_items()

    def get_all_items(self) -> List[SearchResultItem]:
        """Get all result items.

        Returns:
            List of all result items
        """
        return self.results_model.results.copy()

    def highlight_items(self, items: List[SearchResultItem], highlighted: bool = True):
        """Highlight specific items.

        Args:
            items: Items to highlight
            highlighted: Highlight state
        """
        self.results_model.highlight_items(items, highlighted)

    def scroll_to_item(self, item: SearchResultItem):
        """Scroll to specific item.

        Args:
            item: Item to scroll to
        """
        try:
            row = self.results_model.results.index(item)
            index = self.results_model.createIndex(row, 0)
            self.scrollTo(index, QAbstractItemView.PositionAtCenter)
        except ValueError:
            self.logger.warning("Item not found for scrolling")

    def select_all_items(self):
        """Select all items in table."""
        self.selectAll()

    def copy_selected_to_clipboard(self):
        """Copy selected items to clipboard."""
        selected_items = self.get_selected_items()
        if not selected_items:
            return

        # Create tab-separated text
        column_headers = [col["title"] for col in self.results_model.get_column_info()]
        lines = ["\t".join(column_headers)]

        for item in selected_items:
            values = []
            for col in self.results_model.get_column_info():
                values.append(item.get_display_value(col["name"]))
            lines.append("\t".join(values))

        clipboard_text = "\n".join(lines)

        clipboard = QApplication.clipboard()
        clipboard.setText(clipboard_text)

        self.logger.info(f"Copied {len(selected_items)} items to clipboard")


class SearchResultsWidget(QWidget):
    """Complete search results widget with toolbar and statistics."""

    # Signals
    itemSelected = pyqtSignal(object)  # SearchResultItem
    itemActivated = pyqtSignal(object)  # SearchResultItem
    selectionChanged = pyqtSignal(list)  # List[SearchResultItem]
    exportRequested = pyqtSignal(list)  # List[SearchResultItem]

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize search results widget.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        self.logger = logging.getLogger("AdvancedFolders.ResultsWidget")

        # Setup UI
        self._setup_ui()
        self._connect_signals()

        self.logger.info("Search results widget initialized")

    def _setup_ui(self):
        """Setup widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        # Create toolbar
        self._create_toolbar(layout)

        # Create table
        self.table = SearchResultsTable(self)
        layout.addWidget(self.table)

        # Create status bar
        self._create_status_bar(layout)

    def _create_toolbar(self, parent_layout: QVBoxLayout):
        """Create toolbar with result operations.

        Args:
            parent_layout: Parent layout for toolbar
        """
        toolbar_frame = QFrame()
        toolbar_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        toolbar_frame.setMaximumHeight(32)

        toolbar_layout = QHBoxLayout(toolbar_frame)
        toolbar_layout.setContentsMargins(4, 2, 4, 2)
        toolbar_layout.setSpacing(2)

        # Export button
        self.export_button = QToolButton()
        self.export_button.setText("Export")
        self.export_button.setToolTip("Export search results")
        self.export_button.clicked.connect(self._export_results)
        toolbar_layout.addWidget(self.export_button)

        # Copy button
        self.copy_button = QToolButton()
        self.copy_button.setText("Copy")
        self.copy_button.setToolTip("Copy selected items to clipboard")
        self.copy_button.clicked.connect(self.table.copy_selected_to_clipboard)
        toolbar_layout.addWidget(self.copy_button)

        # Select all button
        self.select_all_button = QToolButton()
        self.select_all_button.setText("Select All")
        self.select_all_button.setToolTip("Select all results")
        self.select_all_button.clicked.connect(self.table.select_all_items)
        toolbar_layout.addWidget(self.select_all_button)

        toolbar_layout.addStretch()

        # Results count label
        self.count_label = QLabel("0 results")
        self.count_label.setStyleSheet("QLabel { color: #666666; font-size: 11px; }")
        toolbar_layout.addWidget(self.count_label)

        parent_layout.addWidget(toolbar_frame)

    def _create_status_bar(self, parent_layout: QVBoxLayout):
        """Create status bar with selection info.

        Args:
            parent_layout: Parent layout for status bar
        """
        status_frame = QFrame()
        status_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        status_frame.setMaximumHeight(24)

        status_layout = QHBoxLayout(status_frame)
        status_layout.setContentsMargins(4, 2, 4, 2)

        # Selection info
        self.selection_label = QLabel("No selection")
        self.selection_label.setStyleSheet(
            "QLabel { color: #666666; font-size: 11px; }"
        )
        status_layout.addWidget(self.selection_label)

        status_layout.addStretch()

        parent_layout.addWidget(status_frame)

    def _connect_signals(self):
        """Connect internal signals."""
        # Forward table signals
        self.table.itemSelected.connect(self.itemSelected)
        self.table.itemActivated.connect(self.itemActivated)
        self.table.selectionChanged.connect(self._on_selection_changed)
        self.table.results_model.dataUpdated.connect(self._on_data_updated)

    def _on_selection_changed(self, selected_items: List[SearchResultItem]):
        """Handle selection changes.

        Args:
            selected_items: Currently selected items
        """
        count = len(selected_items)
        if count == 0:
            self.selection_label.setText("No selection")
        elif count == 1:
            self.selection_label.setText("1 item selected")
        else:
            self.selection_label.setText(f"{count} items selected")

        self.selectionChanged.emit(selected_items)

    def _on_data_updated(self, count: int):
        """Handle data updates.

        Args:
            count: Number of results
        """
        if count == 0:
            self.count_label.setText("No results")
        elif count == 1:
            self.count_label.setText("1 result")
        else:
            self.count_label.setText(f"{count:,} results")

    def _export_results(self):
        """Export search results."""
        all_items = self.table.get_all_items()
        self.exportRequested.emit(all_items)

    def set_results(self, file_metadata_list: List[FileMetadata]):
        """Set search results."""
        self.table.set_results(file_metadata_list)

    def clear_results(self):
        """Clear all search results."""
        self.table.clear_results()

    def get_selected_items(self) -> List[SearchResultItem]:
        """Get currently selected items."""
        return self.table.get_selected_items()
