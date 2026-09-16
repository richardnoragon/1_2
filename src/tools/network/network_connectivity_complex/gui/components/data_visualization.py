"""Data visualization components for network connectivity tools."""
from src.rfu.localization import localized_widget as _ui_widget, bind_literal as _ui_bind
from src.rfu import font_tokens

import time
from collections import deque
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from PyQt5.QtCore import Qt, QThread, QTimer, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QBrush, QColor, QFont, QPainter, QPen
from PyQt5.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from gui.themes import Colors, Fonts, Spacing, ThemeManager


class RealTimeChart(QWidget):
    """Real-time line chart widget for displaying network data."""

    def __init__(self, title: str = "", max_points: int = 100, parent=None):
        """Initialize real-time chart.

        Args:
            title: Chart title
            max_points: Maximum data points to display
            parent: Parent widget
        """
        super().__init__(parent)
        self.title = title
        self.max_points = max_points

        # Data storage
        self.data_series: Dict[str, deque] = {}
        self.colors: Dict[str, QColor] = {}
        self.time_points = deque(maxlen=max_points)

        # Chart properties
        self.margin = 40
        self.grid_enabled = True
        self.legend_enabled = True
        self.auto_scale = True
        self.y_min = 0
        self.y_max = 100

        # Setup UI
        self._setup_ui()

        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update)
        self.update_timer.start(1000)  # Update every second

    def _setup_ui(self):
        """Setup chart UI."""
        self.setMinimumSize(400, 300)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Apply theme
        self.setStyleSheet(
            f"""
            QWidget {{
                background-color: {Colors.WINDOW_BACKGROUND};
                border: 1px solid {Colors.TEXT_DISABLED};
                border-radius: 4px;
            }}
        """
        )

    def add_series(self, name: str, color: QColor = None):
        """Add a data series to the chart.

        Args:
            name: Series name
            color: Series color (auto-assigned if None)
        """
        if name not in self.data_series:
            self.data_series[name] = deque(maxlen=self.max_points)

            if color is None:
                # Auto-assign colors
                colors = [
                    QColor(Colors.ACCENT),
                    QColor(Colors.SUCCESS),
                    QColor(Colors.WARNING),
                    QColor(Colors.ERROR),
                    QColor(Colors.BUTTON_PRIMARY),
                    QColor(Colors.BUTTON_SECONDARY),
                ]
                color = colors[len(self.data_series) % len(colors)]

            self.colors[name] = color

    def add_data_point(
        self, series_name: str, value: float, timestamp: datetime = None
    ):
        """Add a data point to a series.

        Args:
            series_name: Name of the series
            value: Data value
            timestamp: Data timestamp (current time if None)
        """
        if series_name not in self.data_series:
            self.add_series(series_name)

        if timestamp is None:
            timestamp = datetime.now()

        self.data_series[series_name].append(value)

        # Update time points (only once per timestamp)
        if not self.time_points or self.time_points[-1] != timestamp:
            self.time_points.append(timestamp)

        # Auto-scale if enabled
        if self.auto_scale:
            self._update_scale()

        self.update()

    def _update_scale(self):
        """Update Y-axis scale based on data."""
        if not self.data_series:
            return

        all_values = []
        for series in self.data_series.values():
            all_values.extend(series)

        if all_values:
            self.y_min = min(all_values) * 0.9
            self.y_max = max(all_values) * 1.1

    def clear_data(self):
        """Clear all chart data."""
        for series in self.data_series.values():
            series.clear()
        self.time_points.clear()
        self.update()

    def paintEvent(self, event):
        """Paint the chart."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Get drawing area
        rect = self.rect()
        chart_rect = rect.adjusted(self.margin, self.margin, -self.margin, -self.margin)

        # Draw background
        painter.fillRect(rect, QBrush(QColor(Colors.WINDOW_BACKGROUND)))

        # Draw title
        if self.title:
            painter.setPen(QPen(QColor(Colors.TEXT_PRIMARY)))
            painter.setFont(
                font_tokens.get("font.toolHeader")  # noqa: TH-3  uses Fonts class (theme-aware family)
            )
            title_rect = rect.adjusted(0, 0, 0, -rect.height() + 30)
            painter.drawText(title_rect, Qt.AlignCenter, self.title)

        # Draw grid
        if self.grid_enabled:
            self._draw_grid(painter, chart_rect)

        # Draw axes
        self._draw_axes(painter, chart_rect)

        # Draw data series
        self._draw_series(painter, chart_rect)

        # Draw legend
        if self.legend_enabled and self.data_series:
            self._draw_legend(painter, rect)

    def _draw_grid(self, painter: QPainter, rect):
        """Draw chart grid."""
        painter.setPen(QPen(QColor(Colors.TEXT_DISABLED), 1, Qt.DotLine))

        # Vertical grid lines
        for i in range(1, 10):
            x = rect.left() + (rect.width() * i / 10)
            painter.drawLine(x, rect.top(), x, rect.bottom())

        # Horizontal grid lines
        for i in range(1, 5):
            y = rect.top() + (rect.height() * i / 5)
            painter.drawLine(rect.left(), y, rect.right(), y)

    def _draw_axes(self, painter: QPainter, rect):
        """Draw chart axes."""
        painter.setPen(QPen(QColor(Colors.TEXT_PRIMARY), 2))

        # X-axis
        painter.drawLine(rect.bottomLeft(), rect.bottomRight())

        # Y-axis
        painter.drawLine(rect.bottomLeft(), rect.topLeft())

        # Y-axis labels
        painter.setFont(
            font_tokens.get("font.caption")
        )  # noqa: TH-3  uses Fonts class (theme-aware family)
        for i in range(6):
            y = rect.bottom() - (rect.height() * i / 5)
            value = self.y_min + (self.y_max - self.y_min) * i / 5
            label = f"{value:.1f}"
            painter.drawText(rect.left() - 35, y + 5, label)

    def _draw_series(self, painter: QPainter, rect):
        """Draw data series."""
        if not self.data_series or not self.time_points:
            return

        for series_name, data in self.data_series.items():
            if len(data) < 2:
                continue

            color = self.colors.get(series_name, QColor(Colors.ACCENT))
            painter.setPen(QPen(color, 2))

            # Calculate points
            points = []
            for i, value in enumerate(data):
                if i >= len(self.time_points):
                    break

                x = rect.left() + (rect.width() * i / max(1, len(data) - 1))
                y_ratio = (value - self.y_min) / max(1, self.y_max - self.y_min)
                y = rect.bottom() - (rect.height() * y_ratio)
                points.append((x, y))

            # Draw lines
            for i in range(len(points) - 1):
                painter.drawLine(
                    points[i][0],
                    points[i][1],
                    points[i + 1][0],
                    points[i + 1][1],
                )

    def _draw_legend(self, painter: QPainter, rect):
        """Draw chart legend."""
        legend_x = rect.right() - 150
        legend_y = rect.top() + 50

        painter.setFont(
            font_tokens.get("font.caption")
        )  # noqa: TH-3  uses Fonts class (theme-aware family)

        for i, (series_name, color) in enumerate(self.colors.items()):
            y = legend_y + (i * 20)

            # Draw color box
            painter.fillRect(legend_x, y - 5, 10, 10, QBrush(color))

            # Draw text
            painter.setPen(QPen(QColor(Colors.TEXT_PRIMARY)))
            painter.drawText(legend_x + 15, y + 5, series_name)


class ProgressIndicator(QWidget):
    """Enhanced progress indicator with status and ETA."""

    def __init__(self, title: str = "", parent=None):
        """Initialize progress indicator.

        Args:
            title: Progress title
            parent: Parent widget
        """
        super().__init__(parent)
        self.title = title
        self._setup_ui()

    def _setup_ui(self):
        """Setup progress indicator UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            Spacing.MEDIUM_SPACING,
            Spacing.MEDIUM_SPACING,
            Spacing.MEDIUM_SPACING,
            Spacing.MEDIUM_SPACING,
        )
        layout.setSpacing(Spacing.SMALL_SPACING)

        # Title label
        if self.title:
            self.title_label = QLabel(self.title)
            ThemeManager.style_label(self.title_label, is_header=True)
            layout.addWidget(self.title_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        ThemeManager.style_progress_bar(self.progress_bar)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        layout.addWidget(self.progress_bar)

        # Status layout
        status_layout = QHBoxLayout()

        # Status label
        self.status_label = _ui_widget(QLabel, 'Legacy.s5fa7aac5375c5815', 'setText')
        ThemeManager.style_label(self.status_label)
        status_layout.addWidget(self.status_label)

        status_layout.addStretch()

        # ETA label
        self.eta_label = QLabel("")
        ThemeManager.style_label(self.eta_label)
        status_layout.addWidget(self.eta_label)

        layout.addLayout(status_layout)

        # Details layout
        details_layout = QHBoxLayout()

        # Speed label
        self.speed_label = QLabel("")
        ThemeManager.style_label(self.speed_label)
        details_layout.addWidget(self.speed_label)

        details_layout.addStretch()

        # Percentage label
        self.percentage_label = _ui_widget(QLabel, 'Legacy.sd9a847a1a79ab448', 'setText')
        ThemeManager.style_label(self.percentage_label)
        details_layout.addWidget(self.percentage_label)

        layout.addLayout(details_layout)

    def set_progress(self, value: int, maximum: int = 100):
        """Set progress value.

        Args:
            value: Current progress value
            maximum: Maximum progress value
        """
        self.progress_bar.setMaximum(maximum)
        self.progress_bar.setValue(value)

        percentage = (value / maximum * 100) if maximum > 0 else 0
        self.percentage_label.setText(f"{percentage:.1f}%")

    def set_status(self, status: str):
        """Set status message.

        Args:
            status: Status message
        """
        self.status_label.setText(status)

    def set_eta(self, eta_seconds: Optional[float]):
        """Set estimated time remaining.

        Args:
            eta_seconds: ETA in seconds (None to hide)
        """
        if eta_seconds is None:
            self.eta_label.setText("")
        else:
            if eta_seconds < 60:
                eta_text = f"{eta_seconds:.0f}s"
            elif eta_seconds < 3600:
                eta_text = f"{eta_seconds/60:.1f}m"
            else:
                eta_text = f"{eta_seconds/3600:.1f}h"
            self.eta_label.setText(f"ETA: {eta_text}")

    def set_speed(self, speed: Optional[float], unit: str = "MB/s"):
        """Set transfer speed.

        Args:
            speed: Speed value (None to hide)
            unit: Speed unit
        """
        if speed is None:
            self.speed_label.setText("")
        else:
            self.speed_label.setText(f"{speed:.1f} {unit}")


class StatusIndicator(QWidget):
    """Status indicator with color-coded states."""

    def __init__(self, parent=None):
        """Initialize status indicator."""
        super().__init__(parent)
        self._setup_ui()
        self.set_status("idle", "Ready")

    def _setup_ui(self):
        """Setup status indicator UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(
            Spacing.SMALL_SPACING,
            Spacing.SMALL_SPACING,
            Spacing.SMALL_SPACING,
            Spacing.SMALL_SPACING,
        )
        layout.setSpacing(Spacing.SMALL_SPACING)

        # Status dot
        self.status_dot = _ui_widget(QLabel, 'Legacy.s5f9e6a3696c4a7c2', 'setText')
        self.status_dot.setFont(
            font_tokens.get("font.title")
        )  # noqa: TH-3  uses Fonts family; size 16 not in Typography scale
        layout.addWidget(self.status_dot)

        # Status text
        self.status_text = _ui_widget(QLabel, 'Legacy.s5fa7aac5375c5815', 'setText')
        ThemeManager.style_label(self.status_text)
        layout.addWidget(self.status_text)

        layout.addStretch()

    def set_status(self, status: str, message: str = ""):
        """Set status indicator state.

        Args:
            status: Status type ('idle', 'running', 'success', 'warning', 'error')
            message: Status message
        """
        status_colors = {
            "idle": Colors.TEXT_SECONDARY,
            "running": Colors.INFO,
            "success": Colors.SUCCESS,
            "warning": Colors.WARNING,
            "error": Colors.ERROR,
        }

        color = status_colors.get(status, Colors.TEXT_SECONDARY)
        self.status_dot.setStyleSheet(f"color: {color};")

        if message:
            self.status_text.setText(message)
        else:
            self.status_text.setText(status.title())


class DataTable(QTableWidget):
    """Enhanced data table with sorting and filtering."""

    # Signals
    row_selected = pyqtSignal(int)
    row_double_clicked = pyqtSignal(int)

    def __init__(self, parent=None):
        """Initialize data table."""
        super().__init__(parent)
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """Setup data table UI."""
        # Table properties
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setSelectionMode(QTableWidget.SingleSelection)
        self.setSortingEnabled(True)

        # Header properties
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.verticalHeader().setVisible(False)

        # Apply theme
        self.setStyleSheet(
            f"""
            QTableWidget {{
                background-color: {Colors.WINDOW_BACKGROUND};
                alternate-background-color: {Colors.DIALOG_BACKGROUND};
                selection-background-color: {Colors.ACCENT};
                selection-color: white;
                gridline-color: {Colors.TEXT_DISABLED};
                border: 1px solid {Colors.TEXT_DISABLED};
            }}
            QHeaderView::section {{
                background-color: {Colors.SECONDARY};
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }}
        """
        )

    def _connect_signals(self):
        """Connect table signals."""
        self.itemSelectionChanged.connect(self._on_selection_changed)
        self.itemDoubleClicked.connect(self._on_double_clicked)

    def _on_selection_changed(self):
        """Handle selection change."""
        current_row = self.currentRow()
        if current_row >= 0:
            self.row_selected.emit(current_row)

    def _on_double_clicked(self, item):
        """Handle double click."""
        if item:
            self.row_double_clicked.emit(item.row())

    def set_headers(self, headers: List[str]):
        """Set table headers.

        Args:
            headers: List of header names
        """
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)

    def add_row(self, data: List[str]) -> int:
        """Add a row to the table.

        Args:
            data: Row data

        Returns:
            Row index
        """
        row = self.rowCount()
        self.insertRow(row)

        for col, value in enumerate(data):
            if col < self.columnCount():
                item = QTableWidgetItem(str(value))
                self.setItem(row, col, item)

        return row

    def update_row(self, row: int, data: List[str]):
        """Update a table row.

        Args:
            row: Row index
            data: New row data
        """
        if 0 <= row < self.rowCount():
            for col, value in enumerate(data):
                if col < self.columnCount():
                    item = self.item(row, col)
                    if item:
                        item.setText(str(value))
                    else:
                        item = QTableWidgetItem(str(value))
                        self.setItem(row, col, item)

    def clear_data(self):
        """Clear all table data."""
        self.setRowCount(0)

    def get_selected_row_data(self) -> Optional[List[str]]:
        """Get data from selected row.

        Returns:
            List of cell values or None if no selection
        """
        current_row = self.currentRow()
        if current_row < 0:
            return None

        data = []
        for col in range(self.columnCount()):
            item = self.item(current_row, col)
            data.append(item.text() if item else "")

        return data

    def filter_rows(self, column: int, filter_text: str):
        """Filter table rows by column value.

        Args:
            column: Column index to filter
            filter_text: Filter text (empty to show all)
        """
        for row in range(self.rowCount()):
            item = self.item(row, column)
            if item and filter_text:
                visible = filter_text.lower() in item.text().lower()
                self.setRowHidden(row, not visible)
            else:
                self.setRowHidden(row, False)
