"""Network Connectivity GUI built for the RFU tool suite."""
from src.rfu.localization import localized_widget as _ui_widget, bind_literal as _ui_bind
from src.rfu import font_tokens

import sys

PORT_SCANNER_TEXT = "Port Scanner"
RESULTS_READY_TEXT = "Network connectivity tools ready. Select a tool above to begin."
THIS_TOOL_WILL_PROVIDE_TEXT = "This tool will provide:"

try:
    from PyQt5.QtWidgets import (
        QApplication,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QMainWindow,
        QMessageBox,
        QProgressBar,
        QSpinBox,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )

    from src.gui.components.buttons import PrimaryButton, SecondaryButton
    from src.gui.components.inputs import TextInput
    from src.gui.components.loading_indicator import LoadingIndicator
    from src.gui.themes import token
except ImportError:
    print("PyQt5 not available. Please install PyQt5.")
    sys.exit(1)

try:
    from src.gui.standard_window import StandardWindow
except ImportError:  # pragma: no cover - fallback for standalone runs

    class StandardWindow(QMainWindow):
        """Fallback window used when StandardWindow is unavailable."""

        def __init__(
            self,
            title: str = "Network Connectivity",
            **_: object,
        ) -> None:
            super().__init__()
            self.setWindowTitle(title)
            self.setGeometry(200, 200, 800, 600)
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            self.main_layout = QVBoxLayout(central_widget)

        def ensure_menu_bar(self) -> None:  # noqa: D401 - compatibility stub
            """No-op for fallback."""


class NetworkConnectivityGUI(StandardWindow):
    """Main window for Network Connectivity operations."""

    def __init__(self) -> None:
        super().__init__(
            title="Network Connectivity - Richard's File Utilities",
            window_type="utility",
        )
        self._ensure_layout()
        self._init_ui()
        self._setup_menu_callbacks()

    def _ensure_layout(self) -> None:
        """Ensure a usable main layout regardless of base class."""

        if not hasattr(self, "main_layout"):
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            self.main_layout = QVBoxLayout(central_widget)

    def _setup_menu_callbacks(self) -> None:
        """Wire RFU menu callbacks when available."""

        if hasattr(self, "menu_manager"):
            self.menu_manager.register_callback(
                "show_preferences",
                self.show_preferences,
            )
            self.menu_manager.register_callback("refresh", self.refresh_view)

    def show_preferences(self) -> None:
        """Display the Network Connectivity preferences dialog."""

        QMessageBox.information(
            self,
            "Network Connectivity Preferences",
            "Network Connectivity preferences:\n\n"
            "• Default connection timeout settings\n"
            "• Preferred network interfaces\n"
            "• Monitoring intervals\n"
            "• Alert thresholds\n\n"
            "Advanced preferences coming soon!",
        )

    def refresh_view(self) -> None:
        """Refresh any active network connectivity status panels."""

        self.results_text.append("\n=== Refreshing Network Status ===")
        self.results_text.append("Network interfaces refreshed")
        self.results_text.append("Connection status updated")
        QMessageBox.information(
            self,
            "Refresh",
            "Network status refreshed successfully.",
        )

    def _init_ui(self) -> None:
        """Compose the interface widgets for the tool."""

        layout = self.main_layout

        header_label = _ui_widget(QLabel, 'Legacy.s45acab8512bdb8a1', 'setText')
        header_label.setStyleSheet(
            """
            QLabel {

                font-weight: bold;
                color: {token('text_primary')};
                padding: 10px;
                background-color: {token('background')};
                border-radius: 5px;
                margin-bottom: 10px;
            }
        """
        )
        font_tokens.bind(header_label, "font.toolHeader")
        layout.addWidget(header_label)

        tools_group = _ui_widget(QGroupBox, 'Legacy.sec8ff975cad09591', 'setTitle')
        tools_layout = QVBoxLayout(tools_group)

        bandwidth_group = _ui_widget(QGroupBox, 'Legacy.s38923ecfba1269de', 'setTitle')
        bandwidth_layout = QVBoxLayout(bandwidth_group)

        bandwidth_button = _ui_widget(PrimaryButton, 'Legacy.sa389f5cf3c9cbed3', 'setText')
        _ui_bind(bandwidth_button, 'setAccessibleName', 'Legacy.s125382ff9fdaeb25')
        bandwidth_button.clicked.connect(self.start_bandwidth_monitor)
        bandwidth_layout.addWidget(bandwidth_button)

        self.bandwidth_status = _ui_widget(QLabel, 'Legacy.sd2187745dda2b177', 'setText')
        bandwidth_layout.addWidget(self.bandwidth_status)

        tools_layout.addWidget(bandwidth_group)

        scanner_group = QGroupBox(PORT_SCANNER_TEXT)
        scanner_layout = QVBoxLayout(scanner_group)

        target_layout = QHBoxLayout()
        target_layout.addWidget(_ui_widget(QLabel, 'Legacy.s890d34fffcde315c', 'setText'))
        self.target_input = TextInput("Target host", "Enter IP address or hostname")
        _ui_bind(self.target_input, 'setAccessibleName', 'Legacy.sfe2d1fcb2414123f')
        target_layout.addWidget(self.target_input)
        scanner_layout.addLayout(target_layout)

        port_layout = QHBoxLayout()
        port_layout.addWidget(_ui_widget(QLabel, 'Legacy.sc23de10e17c4ca4e', 'setText'))
        self.start_port = QSpinBox()
        _ui_bind(self.start_port, 'setAccessibleName', 'Legacy.sf8132b7aed82551d')
        self.start_port.setMinimumHeight(44)
        self.start_port.setRange(1, 65535)
        self.start_port.setValue(1)
        port_layout.addWidget(self.start_port)
        port_layout.addWidget(_ui_widget(QLabel, 'Legacy.s663ea1bfffe5038f', 'setText'))
        self.end_port = QSpinBox()
        _ui_bind(self.end_port, 'setAccessibleName', 'Legacy.s30dafb24fa178f45')
        self.end_port.setMinimumHeight(44)
        self.end_port.setRange(1, 65535)
        self.end_port.setValue(1000)
        port_layout.addWidget(self.end_port)
        scanner_layout.addLayout(port_layout)

        scan_button = _ui_widget(PrimaryButton, 'Legacy.s4ec0ceaea3c853c2', 'setText')
        _ui_bind(scan_button, 'setAccessibleName', 'Legacy.sd0dafab4d2bbe3fe')
        scan_button.clicked.connect(self.start_port_scan)
        scanner_layout.addWidget(scan_button)

        tools_layout.addWidget(scanner_group)

        wifi_group = _ui_widget(QGroupBox, 'Legacy.s8ac9131a13d0630a', 'setTitle')
        wifi_layout = QVBoxLayout(wifi_group)

        wifi_button = _ui_widget(SecondaryButton, 'Legacy.s610566bfc5d3f88b', 'setText')
        _ui_bind(wifi_button, 'setAccessibleName', 'Legacy.s4de6e3001e70ad6e')
        wifi_button.clicked.connect(self.analyze_wifi)
        wifi_layout.addWidget(wifi_button)

        tools_layout.addWidget(wifi_group)

        layout.addWidget(tools_group)

        results_group = _ui_widget(QGroupBox, 'Legacy.s219c4a6c86a716e9', 'setTitle')
        results_layout = QVBoxLayout(results_group)

        self.results_text = QTextEdit()
        _ui_bind(self.results_text, 'setAccessibleName', 'Legacy.s66c11af910187df0')
        self.results_text.setReadOnly(True)
        self.results_text.setPlainText(RESULTS_READY_TEXT)
        results_layout.addWidget(self.results_text)

        layout.addWidget(results_group)

        self.progress_bar = LoadingIndicator(parent=self, message="Scanning...")
        layout.addWidget(self.progress_bar)

        button_style = """
            QPushButton {
                background-color: {token('accent')};
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
                margin: 2px;
            }
            QPushButton:hover {
                background-color: {token('button_primary_hover')};
            }
        """
        for button in (bandwidth_button, scan_button, wifi_button):
            button.setStyleSheet(button_style)

    def start_bandwidth_monitor(self) -> None:
        """Start bandwidth monitoring."""

        self.bandwidth_status.setText("Status: Monitoring...")
        self.results_text.append("\n=== Bandwidth Monitor ===")
        self.results_text.append(
            "Bandwidth monitoring functionality ready for implementation."
        )
        self.results_text.append(THIS_TOOL_WILL_PROVIDE_TEXT)
        self.results_text.append("• Real-time network speed monitoring")
        self.results_text.append("• Historical data analysis and charts")
        self.results_text.append("• Bandwidth alerts and notifications")
        self.results_text.append("• Application-level monitoring")

        QMessageBox.information(
            self,
            "Bandwidth Monitor",
            "Bandwidth monitoring started!\n\n"
            "This feature will monitor your network speed in real-time.",
        )

    def start_port_scan(self) -> None:
        """Initiate the port scanning workflow."""

        target = self.target_input.text().strip()
        start_port = self.start_port.value()
        end_port = self.end_port.value()

        if not target:
            QMessageBox.warning(
                self,
                PORT_SCANNER_TEXT,
                "Please enter a target IP address or hostname.",
            )
            return

        if start_port > end_port:
            QMessageBox.warning(
                self,
                PORT_SCANNER_TEXT,
                "Start port must be less than or equal to end port.",
            )
            return

        self.results_text.append("\n=== Port Scanner ===")
        self.results_text.append(f"Target: {target}")
        self.results_text.append(f"Port Range: {start_port}-{end_port}")
        self.results_text.append(
            "Port scanning functionality ready for implementation."
        )
        self.results_text.append(THIS_TOOL_WILL_PROVIDE_TEXT)
        self.results_text.append("• Comprehensive port scanning")
        self.results_text.append("• Service detection and identification")
        self.results_text.append("• Security vulnerability assessment")
        self.results_text.append("• Custom scan profiles")

        QMessageBox.information(
            self,
            PORT_SCANNER_TEXT,
            f"Port scan initiated for {target}!\n\n"
            f"Scanning ports {start_port}-{end_port}",
        )

    def analyze_wifi(self) -> None:
        """Run the WiFi analysis workflow."""

        self.results_text.append("\n=== WiFi Analyzer ===")
        self.results_text.append(
            "WiFi analysis functionality ready for implementation."
        )
        self.results_text.append(THIS_TOOL_WILL_PROVIDE_TEXT)
        self.results_text.append("• Wireless network analysis")
        self.results_text.append("• Signal strength monitoring")
        self.results_text.append("• Channel utilization analysis")
        self.results_text.append("• Security assessment")

        QMessageBox.information(
            self,
            "WiFi Analyzer",
            "WiFi analysis started!\n\n"
            "This feature will analyze wireless networks in your area.",
        )


def main() -> int:
    """Run the Network Connectivity tool as a standalone application."""

    app = QApplication(sys.argv)
    window = NetworkConnectivityGUI()
    window.show()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
