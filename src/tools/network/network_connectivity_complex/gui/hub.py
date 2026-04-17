"""Network Connectivity Hub - Main interface for all network tools."""

from typing import Any, Dict, List, Optional

from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import (
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSplitter,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from gui.common.standard_window import StandardWindow
from gui.themes import Colors, Spacing, ThemeManager

from .components.data_visualization import StatusIndicator

# ---------------------------------------------------------------------------
# CP: Component replacement imports (CP-1)
# ---------------------------------------------------------------------------
try:
    from src.gui.components.buttons import PrimaryButton

    _CP_AVAILABLE = True
except ImportError:
    from PyQt5.QtWidgets import QPushButton as PrimaryButton

    _CP_AVAILABLE = False

from .widgets.bandwidth_monitor_widget import BandwidthMonitorWidget
from .widgets.lan_file_transfer_widget import LANFileTransferWidget
from .widgets.port_scanner_widget import PortScannerWidget
from .widgets.wifi_analyzer_widget import WiFiAnalyzerWidget


class NetworkToolCard(QWidget):
    """Card widget for network tool selection."""

    # Signals
    tool_selected = pyqtSignal(str)  # tool_name

    def __init__(
        self,
        tool_name: str,
        title: str,
        description: str,
        icon_path: str = None,
        parent=None,
    ):
        """Initialize tool card.

        Args:
            tool_name: Internal tool name
            title: Display title
            description: Tool description
            icon_path: Path to tool icon
            parent: Parent widget
        """
        super().__init__(parent)
        self.tool_name = tool_name
        self.title = title
        self.description = description
        self.icon_path = icon_path

        self._setup_ui()
        self._connect_signals()
        ThemeManager.add_theme_changed_callback(self._on_theme_changed)

    def _on_theme_changed(self, variant: str) -> None:
        """Re-apply token-based stylesheets when the active theme variant changes."""
        pass  # stylesheets applied at init; live re-apply pending TH-4c/4d

    def _setup_ui(self):
        """Setup card UI."""
        self.setFixedSize(280, 120)
        self.setStyleSheet(
            f"""
            QWidget {{
                background-color: {Colors.WINDOW_BACKGROUND};
                border: 2px solid {Colors.TEXT_DISABLED};
                border-radius: 8px;
                padding: {Spacing.MEDIUM_SPACING}px;
            }}
            QWidget:hover {{
                border-color: {Colors.ACCENT};
                background-color: {Colors.DIALOG_BACKGROUND};
            }}
        """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            Spacing.MEDIUM_SPACING,
            Spacing.MEDIUM_SPACING,
            Spacing.MEDIUM_SPACING,
            Spacing.MEDIUM_SPACING,
        )
        layout.setSpacing(Spacing.SMALL_SPACING)

        # Header with icon and title
        header_layout = QHBoxLayout()

        # Icon (placeholder for now)
        if self.icon_path:
            icon_label = QLabel()
            # icon_label.setPixmap(QPixmap(self.icon_path).scaled(32, 32))
            icon_label.setText("🔧")  # Placeholder emoji
            icon_label.setStyleSheet("font-size: 24px;")
            header_layout.addWidget(icon_label)

        # Title
        title_label = QLabel(self.title)
        ThemeManager.style_label(title_label, is_header=True)
        header_layout.addWidget(title_label)

        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Description
        desc_label = QLabel(self.description)
        desc_label.setWordWrap(True)
        ThemeManager.style_label(desc_label)
        layout.addWidget(desc_label)

        layout.addStretch()

        # Launch button
        self.launch_button = PrimaryButton("Launch")
        self.launch_button.setMaximumWidth(100)
        layout.addWidget(self.launch_button, alignment=Qt.AlignRight)

    def _connect_signals(self):
        """Connect card signals."""
        self.launch_button.clicked.connect(self._on_launch_clicked)

    def _on_launch_clicked(self):
        """Handle launch button click."""
        self.tool_selected.emit(self.tool_name)

    def mousePressEvent(self, event):
        """Handle mouse press for card selection."""
        if event.button() == Qt.LeftButton:
            self.tool_selected.emit(self.tool_name)
        super().mousePressEvent(event)


class NetworkToolsOverview(QWidget):
    """Overview widget showing all available network tools."""

    # Signals
    tool_launched = pyqtSignal(str)  # tool_name

    def __init__(self, parent=None):
        """Initialize tools overview."""
        super().__init__(parent)
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """Setup overview UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            Spacing.LARGE_SPACING,
            Spacing.LARGE_SPACING,
            Spacing.LARGE_SPACING,
            Spacing.LARGE_SPACING,
        )
        layout.setSpacing(Spacing.LARGE_SPACING)

        # Title
        title_label = QLabel("Network Connectivity Tools")
        title_label.setStyleSheet(
            f"""
            QLabel {{
                color: {Colors.TEXT_PRIMARY};
                font-size: 24px;
                font-weight: bold;
                margin-bottom: {Spacing.MEDIUM_SPACING}px;
            }}
        """
        )
        layout.addWidget(title_label, alignment=Qt.AlignCenter)

        # Description
        desc_label = QLabel(
            "Comprehensive network analysis and monitoring tools for "
            "bandwidth monitoring, port scanning, Wi-Fi analysis, "
            "and LAN file transfer."
        )
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignCenter)
        ThemeManager.style_label(desc_label)
        layout.addWidget(desc_label)

        # Tools grid
        tools_frame = QFrame()
        tools_layout = QVBoxLayout(tools_frame)
        tools_layout.setSpacing(Spacing.LARGE_SPACING)

        # First row
        row1_layout = QHBoxLayout()
        row1_layout.setSpacing(Spacing.LARGE_SPACING)

        # Bandwidth Monitor card
        self.bandwidth_card = NetworkToolCard(
            "bandwidth_monitor",
            "Bandwidth Monitor",
            "Real-time network speed monitoring with charts, "
            "alerts, and historical data analysis.",
        )
        row1_layout.addWidget(self.bandwidth_card)

        # Port Scanner card
        self.port_scanner_card = NetworkToolCard(
            "port_scanner",
            "Port Scanner",
            "Comprehensive port scanning with service detection, "
            "vulnerability assessment, and reporting.",
        )
        row1_layout.addWidget(self.port_scanner_card)

        row1_layout.addStretch()
        tools_layout.addLayout(row1_layout)

        # Second row
        row2_layout = QHBoxLayout()
        row2_layout.setSpacing(Spacing.LARGE_SPACING)

        # Wi-Fi Analyzer card
        self.wifi_card = NetworkToolCard(
            "wifi_analyzer",
            "Wi-Fi Analyzer",
            "Wireless network analysis with signal strength monitoring, "
            "channel utilization, and security assessment.",
        )
        row2_layout.addWidget(self.wifi_card)

        # LAN File Transfer card
        self.lan_transfer_card = NetworkToolCard(
            "lan_file_transfer",
            "LAN File Transfer",
            "Secure peer-to-peer file sharing with device discovery, "
            "encryption, and transfer management.",
        )
        row2_layout.addWidget(self.lan_transfer_card)

        row2_layout.addStretch()
        tools_layout.addLayout(row2_layout)

        tools_layout.addStretch()
        layout.addWidget(tools_frame)

        layout.addStretch()

    def _connect_signals(self):
        """Connect overview signals."""
        self.bandwidth_card.tool_selected.connect(self.tool_launched.emit)
        self.port_scanner_card.tool_selected.connect(self.tool_launched.emit)
        self.wifi_card.tool_selected.connect(self.tool_launched.emit)
        self.lan_transfer_card.tool_selected.connect(self.tool_launched.emit)


class NetworkConnectivityHub(StandardWindow):
    """Main Network Connectivity Hub interface."""

    def __init__(self, parent=None):
        """Initialize Network Connectivity Hub."""
        super().__init__("Network Connectivity Hub", is_main_window=True)

        # Tool instances
        self.tool_widgets: Dict[str, QWidget] = {}
        self.active_tools: Dict[str, QWidget] = {}

        # Setup UI
        self._setup_ui()
        self._connect_signals()

        # Show window
        self.show()

    def _setup_ui(self):
        """Setup hub UI."""
        # Create main tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setAccessibleName("Network connectivity tool tabs")
        self.tab_widget.setTabPosition(QTabWidget.North)
        self.tab_widget.setMovable(True)
        self.tab_widget.setTabsClosable(True)
        self.set_content_widget(self.tab_widget)

        # Apply tab styling
        self.tab_widget.setStyleSheet(
            f"""
            QTabWidget::pane {{
                border: 1px solid {Colors.TEXT_DISABLED};
                background-color: {Colors.WINDOW_BACKGROUND};
            }}
            QTabBar::tab {{
                background-color: {Colors.DIALOG_BACKGROUND};
                color: {Colors.TEXT_PRIMARY};
                padding: 8px 16px;
                margin-right: 2px;
                border: 1px solid {Colors.TEXT_DISABLED};
                border-bottom: none;
            }}
            QTabBar::tab:selected {{
                background-color: {Colors.WINDOW_BACKGROUND};
                border-bottom: 1px solid {Colors.WINDOW_BACKGROUND};
            }}
            QTabBar::tab:hover {{
                background-color: {Colors.ACCENT};
                color: white;
            }}
        """
        )

        # Overview tab (always present)
        self.overview_widget = NetworkToolsOverview()
        self.tab_widget.addTab(self.overview_widget, "Overview")

        # Status bar with tool status indicators
        self._setup_status_indicators()

    def _setup_status_indicators(self):
        """Setup status indicators in status bar."""
        # Create status widget
        status_widget = QWidget()
        status_layout = QHBoxLayout(status_widget)
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setSpacing(Spacing.MEDIUM_SPACING)

        # Tool status indicators
        self.status_indicators: Dict[str, StatusIndicator] = {}

        tool_names = [
            ("bandwidth_monitor", "Bandwidth"),
            ("port_scanner", "Port Scanner"),
            ("wifi_analyzer", "Wi-Fi"),
            ("lan_file_transfer", "File Transfer"),
        ]

        for tool_name, display_name in tool_names:
            indicator = StatusIndicator()
            indicator.set_status("idle", f"{display_name}: Ready")
            self.status_indicators[tool_name] = indicator
            status_layout.addWidget(indicator)

        status_layout.addStretch()

        # Add to status bar
        self.status_bar.addPermanentWidget(status_widget)

    def _connect_signals(self):
        """Connect hub signals."""
        # Overview signals
        self.overview_widget.tool_launched.connect(self._launch_tool)

        # Tab widget signals
        self.tab_widget.tabCloseRequested.connect(self._close_tool_tab)

    @pyqtSlot(str)
    def _launch_tool(self, tool_name: str):
        """Launch a network tool.

        Args:
            tool_name: Name of tool to launch
        """
        try:
            # Check if tool is already open
            if tool_name in self.active_tools:
                # Switch to existing tab
                widget = self.active_tools[tool_name]
                index = self.tab_widget.indexOf(widget)
                if index >= 0:
                    self.tab_widget.setCurrentIndex(index)
                    return

            # Create new tool widget
            tool_widget = self._create_tool_widget(tool_name)
            if tool_widget:
                # Add to tab widget
                tool_title = self._get_tool_title(tool_name)
                tab_index = self.tab_widget.addTab(tool_widget, tool_title)
                self.tab_widget.setCurrentIndex(tab_index)

                # Track active tool
                self.active_tools[tool_name] = tool_widget

                # Update status
                if tool_name in self.status_indicators:
                    self.status_indicators[tool_name].set_status(
                        "running", f"{tool_title}: Active"
                    )

                self.show_success_message(f"Launched {tool_title}")
            else:
                self.show_error_message(f"Failed to launch {tool_name}")

        except Exception as e:
            self.show_error_message(f"Error launching {tool_name}: {e}")

    def _create_tool_widget(self, tool_name: str) -> Optional[QWidget]:
        """Create widget for specified tool.

        Args:
            tool_name: Name of tool to create

        Returns:
            Tool widget or None if creation failed
        """
        try:
            if tool_name == "bandwidth_monitor":
                return BandwidthMonitorWidget(self)
            elif tool_name == "port_scanner":
                return PortScannerWidget(self)
            elif tool_name == "wifi_analyzer":
                return WiFiAnalyzerWidget(self)
            elif tool_name == "lan_file_transfer":
                return LANFileTransferWidget(self)
            else:
                return None

        except Exception as e:
            self.show_error_message(f"Error creating {tool_name} widget: {e}")
            return None

    def _get_tool_title(self, tool_name: str) -> str:
        """Get display title for tool.

        Args:
            tool_name: Tool name

        Returns:
            Display title
        """
        titles = {
            "bandwidth_monitor": "Bandwidth Monitor",
            "port_scanner": "Port Scanner",
            "wifi_analyzer": "Wi-Fi Analyzer",
            "lan_file_transfer": "LAN File Transfer",
        }
        return titles.get(tool_name, tool_name.replace("_", " ").title())

    @pyqtSlot(int)
    def _close_tool_tab(self, tab_index: int):
        """Close a tool tab.

        Args:
            tab_index: Index of tab to close
        """
        # Don't close overview tab
        if tab_index == 0:
            return

        try:
            # Get widget and tool name
            widget = self.tab_widget.widget(tab_index)
            tool_name = None

            # Find tool name
            for name, active_widget in self.active_tools.items():
                if active_widget == widget:
                    tool_name = name
                    break

            # Remove tab
            self.tab_widget.removeTab(tab_index)

            # Clean up tool
            if tool_name:
                # Remove from active tools
                if tool_name in self.active_tools:
                    del self.active_tools[tool_name]

                # Update status
                if tool_name in self.status_indicators:
                    tool_title = self._get_tool_title(tool_name)
                    self.status_indicators[tool_name].set_status(
                        "idle", f"{tool_title}: Ready"
                    )

                # Close widget properly
                if hasattr(widget, "close"):
                    widget.close()

                self.show_info_message(f"Closed {self._get_tool_title(tool_name)}")

        except Exception as e:
            self.show_error_message(f"Error closing tool tab: {e}")

    def get_active_tools(self) -> List[str]:
        """Get list of currently active tools.

        Returns:
            List of active tool names
        """
        return list(self.active_tools.keys())

    def close_all_tools(self):
        """Close all active tool tabs."""
        # Close tabs from right to left (except overview)
        for i in range(self.tab_widget.count() - 1, 0, -1):
            self._close_tool_tab(i)

    def closeEvent(self, event):
        """Handle window close event."""
        # Close all tools first
        self.close_all_tools()

        # Accept close event
        super().closeEvent(event)
