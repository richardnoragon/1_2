"""
Enhanced Network Tools GUI Wrapper

This module provides a comprehensive PyQt5 GUI wrapper for all network tools
using the utilities logic framework.
"""
from src.rfu.localization import localized_widget as _ui_widget, bind_literal as _ui_bind

import ipaddress
import logging
import socket
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional

from PyQt5.QtCore import QMutex, QMutexLocker, QThread, pyqtSignal
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.gui.themes import token

# Import the standard window framework
try:
    from ....gui.standard_window import StandardWindow
except ImportError:
    # Fallback for development
    StandardWindow = QWidget


# ---------------------------------------------------------------------------
# GRD-1a: Guardian registration (graceful no-op when guardian absent)
# ---------------------------------------------------------------------------
try:
    from src.core.guardian import register_gui_component
except ImportError:

    def register_gui_component(*a, **kw):
        pass  # noqa: E731


# ---------------------------------------------------------------------------
# TEL: Telemetry helpers (graceful no-op when telemetry absent)
# ---------------------------------------------------------------------------
try:
    from src.gui.telemetry import emit_telemetry

    def _emit_telemetry(event_type, **kw):
        emit_telemetry(event_type, **kw)  # noqa: E731

except ImportError:

    def _emit_telemetry(*a, **kw):
        pass  # noqa: E731


# ---------------------------------------------------------------------------
# STR: Centralised string constants with fallback (P1-C15 / STR-1)
# ---------------------------------------------------------------------------
try:
    from src.rfu.ui_strings import NetworkTools as _NetworkToolsStrings
except ImportError:

    class _NetworkToolsStrings:  # type: ignore[no-redef]
        TITLE = "Network Tools"
        WINDOW_TITLE = "Network Tools — RFU"
        LOADING = "Loading Network Tools…"
        MODAL_ERROR_TITLE = "Network Error"
        ERR_INIT_FAILED = (
            "Could not start Network Tools. "
            "Please try again or restart the application."
        )
        ERR_SCAN_FAILED = "Could not complete network scan. Please try again."
        ERR_CONNECT_FAILED = "Could not connect to target. Please check connectivity."
        ERR_PORT_INVALID = (
            "Invalid port format. "
            "Please enter comma-separated port numbers (e.g., 80, 443, 8080)."
        )
        ERR_NO_TARGET = (
            "Please enter a target hostname or IP address before starting a scan."
        )


# ---------------------------------------------------------------------------
# CP: Component Placement — PrimaryButton / SecondaryButton
# ---------------------------------------------------------------------------
try:
    from src.gui.components.buttons import PrimaryButton, SecondaryButton

    _CP_AVAILABLE = True
except ImportError:
    PrimaryButton = QPushButton  # type: ignore[misc,assignment]
    SecondaryButton = QPushButton  # type: ignore[misc,assignment]
    _CP_AVAILABLE = False

# ---------------------------------------------------------------------------
# ERR: Modal helper (graceful no-op when modal absent)
# ---------------------------------------------------------------------------
try:
    from src.gui.components.modal import Modal
except ImportError:
    Modal = None  # type: ignore[assignment,misc]


# Import network tools
try:
    from ..network_connectivity_complex.tools.bandwidth_monitor import (
        BandwidthMonitor,
    )
    from ..network_connectivity_complex.tools.lan_file_transfer import (
        LANFileTransfer,
    )
    from ..network_connectivity_complex.tools.port_scanner import PortScanner
    from ..network_connectivity_complex.tools.wifi_analyzer import WiFiAnalyzer
except ImportError:
    # Fallback imports for development
    PortScanner = None
    BandwidthMonitor = None
    WiFiAnalyzer = None
    LANFileTransfer = None


# Constants
DEFAULT_SPEED_LABEL = "0 KB/s"


@dataclass
class NetworkScanResult:
    """Network scan result data."""

    target: str
    port: int
    state: str
    service: str
    banner: str = ""
    timestamp: Optional[datetime] = None


@dataclass
class BandwidthData:
    """Bandwidth monitoring data."""

    timestamp: datetime
    download_speed: float
    upload_speed: float
    total_download: int
    total_upload: int


class NetworkWorkerThread(QThread):
    """Worker thread for network operations."""

    # Signals
    progress_updated = pyqtSignal(int, str)  # progress, status
    scan_result = pyqtSignal(dict)  # scan result data
    bandwidth_data = pyqtSignal(dict)  # bandwidth data
    operation_completed = pyqtSignal(bool, str)  # success, message
    error_occurred = pyqtSignal(str)

    def __init__(self, operation_type: str, parameters: Dict[str, Any]):
        super().__init__()
        self.operation_type = operation_type
        self.parameters = parameters
        self.is_cancelled = False
        self._mutex = QMutex()

        # Initialize tools
        self.port_scanner = PortScanner() if PortScanner else None
        self.bandwidth_monitor = BandwidthMonitor() if BandwidthMonitor else None
        self.wifi_analyzer = WiFiAnalyzer() if WiFiAnalyzer else None
        self.lan_transfer = LANFileTransfer() if LANFileTransfer else None

    def run(self):
        """Execute network operation."""
        try:
            if self.operation_type == "port_scan":
                self._run_port_scan()
            elif self.operation_type == "bandwidth_monitor":
                self._run_bandwidth_monitor()
            elif self.operation_type == "wifi_scan":
                self._run_wifi_scan()
            elif self.operation_type == "network_discovery":
                self._run_network_discovery()
            elif self.operation_type == "connectivity_test":
                self._run_connectivity_test()
            else:
                self.error_occurred.emit(f"Unknown operation: {self.operation_type}")

        except Exception as e:
            self.error_occurred.emit(f"Operation failed: {str(e)}")

    def _run_port_scan(self):
        """Run port scanning operation."""
        if not self.port_scanner:
            self.error_occurred.emit("Port scanner not available")
            return

        target = self.parameters.get("target", "")
        ports = self.parameters.get("ports", [80, 443, 22, 21, 25, 53])
        scan_type = self.parameters.get("scan_type", "tcp_connect")

        total_ports = len(ports)

        for i, port in enumerate(ports):
            with QMutexLocker(self._mutex):
                if self.is_cancelled:
                    break

            try:
                # Simulate port scan (replace with actual scanner logic)
                result = self._scan_port(target, port, scan_type)

                self.scan_result.emit(
                    {
                        "target": target,
                        "port": port,
                        "state": result["state"],
                        "service": result["service"],
                        "banner": result.get("banner", ""),
                        "timestamp": datetime.now().isoformat(),
                    }
                )

                progress = int((i + 1) / total_ports * 100)
                self.progress_updated.emit(progress, f"Scanning port {port}")

            except Exception as e:
                self.error_occurred.emit(f"Error scanning port {port}: {str(e)}")

        self.operation_completed.emit(True, "Port scan completed")

    def _run_bandwidth_monitor(self):
        """Run bandwidth monitoring."""
        duration = self.parameters.get("duration", 60)  # seconds
        interval = self.parameters.get("interval", 1)  # seconds

        for i in range(duration):
            with QMutexLocker(self._mutex):
                if self.is_cancelled:
                    break

            # Simulate bandwidth data (replace with actual monitoring)
            bandwidth_data = {
                "timestamp": datetime.now().isoformat(),
                "download_speed": 1024 * 1024 * (0.5 + i * 0.1),  # Simulated
                "upload_speed": 256 * 1024 * (0.3 + i * 0.05),  # Simulated
                "total_download": 1024 * 1024 * 1024 * i,
                "total_upload": 256 * 1024 * 1024 * i,
            }

            self.bandwidth_data.emit(bandwidth_data)

            progress = int((i + 1) / duration * 100)
            status_msg = f"Monitoring bandwidth ({i+1}/{duration}s)"
            self.progress_updated.emit(progress, status_msg)

            self.msleep(interval * 1000)  # Convert to milliseconds

        self.operation_completed.emit(True, "Bandwidth monitoring completed")

    def _run_wifi_scan(self):
        """Run WiFi network scanning."""
        self.progress_updated.emit(50, "Scanning for WiFi networks...")

        # Simulate WiFi scan results
        networks = [
            {"ssid": "Home_Network", "signal": -30, "security": "WPA2"},
            {"ssid": "Guest_WiFi", "signal": -45, "security": "Open"},
            {"ssid": "Office_5G", "signal": -60, "security": "WPA3"},
        ]

        for network in networks:
            self.scan_result.emit(network)

        self.progress_updated.emit(100, "WiFi scan completed")
        self.operation_completed.emit(True, f"Found {len(networks)} networks")

    def _run_network_discovery(self):
        """Run network discovery."""
        network = self.parameters.get("network", "192.168.1.0/24")

        try:
            net = ipaddress.IPv4Network(network, strict=False)
            hosts = list(net.hosts())[:20]  # Limit to first 20 hosts

            for i, host in enumerate(hosts):
                with QMutexLocker(self._mutex):
                    if self.is_cancelled:
                        break

                # Simulate host discovery
                is_alive = self._ping_host(str(host))

                if is_alive:
                    self.scan_result.emit(
                        {
                            "ip": str(host),
                            "hostname": f'host-{str(host).split(".")[-1]}',
                            "status": "alive",
                            "response_time": 10 + i,  # Simulated
                        }
                    )

                progress = int((i + 1) / len(hosts) * 100)
                self.progress_updated.emit(progress, f"Discovering {host}")

        except Exception as e:
            self.error_occurred.emit(f"Network discovery error: {str(e)}")

        self.operation_completed.emit(True, "Network discovery completed")

    def _run_connectivity_test(self):
        """Run connectivity test."""
        targets = self.parameters.get("targets", ["8.8.8.8", "google.com"])

        for i, target in enumerate(targets):
            with QMutexLocker(self._mutex):
                if self.is_cancelled:
                    break

            # Test connectivity
            result = self._test_connectivity(target)

            self.scan_result.emit(
                {
                    "target": target,
                    "reachable": result["reachable"],
                    "response_time": result["response_time"],
                    "error": result.get("error", ""),
                }
            )

            progress = int((i + 1) / len(targets) * 100)
            self.progress_updated.emit(progress, f"Testing {target}")

        self.operation_completed.emit(True, "Connectivity test completed")

    def _scan_port(self, target: str, port: int, scan_type: str) -> Dict[str, str]:
        """Scan a single port."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex((target, port))
            sock.close()

            if result == 0:
                return {
                    "state": "open",
                    "service": self._get_service_name(port),
                }
            else:
                return {"state": "closed", "service": ""}
        except Exception:
            return {"state": "filtered", "service": ""}

    def _ping_host(self, host: str) -> bool:
        """Ping a host to check if it's alive."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((host, 22))  # Try SSH port
            sock.close()
            return result == 0
        except Exception:
            return False

    def _test_connectivity(self, target: str) -> Dict[str, Any]:
        """Test connectivity to target."""
        try:
            start_time = datetime.now()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)

            # Test connection on port 80
            result = sock.connect_ex((target, 80))

            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds() * 1000

            sock.close()

            return {"reachable": result == 0, "response_time": response_time}
        except Exception as e:
            return {"reachable": False, "response_time": 0, "error": str(e)}

    def _get_service_name(self, port: int) -> str:
        """Get service name for port."""
        services = {
            21: "FTP",
            22: "SSH",
            23: "Telnet",
            25: "SMTP",
            53: "DNS",
            80: "HTTP",
            110: "POP3",
            143: "IMAP",
            443: "HTTPS",
            993: "IMAPS",
            995: "POP3S",
            3389: "RDP",
            5900: "VNC",
        }
        return services.get(port, "Unknown")

    def cancel(self):
        """Cancel the operation."""
        with QMutexLocker(self._mutex):
            self.is_cancelled = True


class NetworkToolsWindow(StandardWindow):
    """Enhanced Network Tools GUI with comprehensive functionality."""

    def __init__(self, hub_instance=None):
        super().__init__()
        self._hub = hub_instance
        try:
            from src.rfu.log_manager import get_log_manager

            self._logger = get_log_manager().get_logger("NetworkToolsWindow")
        except Exception:
            self._logger = logging.getLogger("NetworkToolsWindow")
        self.setWindowTitle(_NetworkToolsStrings.WINDOW_TITLE)
        self.setGeometry(100, 100, 1400, 900)

        # Initialize components
        self.worker_thread = None
        self.scan_results = []
        self.bandwidth_data = []

        self.init_ui()
        self.connect_signals()
        register_gui_component(
            self, tool_id="network_tools", recovery_callback=self.degraded_fallback
        )
        _emit_telemetry("ui_view_load", tool_id="network_tools")

    def health_check(self) -> bool:
        """Return True if core UI is functional (GRD-3a)."""
        try:
            return hasattr(self, "tab_widget") and self.tab_widget is not None
        except Exception:
            return False

    def degraded_fallback(self) -> None:
        """Enter degraded / read-only state (GRD-3b)."""
        try:
            self._logger.warning("NetworkToolsWindow entering degraded mode")
        except Exception:
            pass
        _emit_telemetry(
            "ui_error_event", tool_id="network_tools", error_type="degraded"
        )

    def init_ui(self):
        """Initialize the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)

        # Create tab widget for different tools
        self.tab_widget = QTabWidget()
        _ui_bind(self.tab_widget, 'setAccessibleName', 'Legacy.s2416e47b9515b7ab')
        main_layout.addWidget(self.tab_widget)

        # Create tabs
        self.create_port_scanner_tab()
        self.create_bandwidth_monitor_tab()
        self.create_network_discovery_tab()
        self.create_connectivity_test_tab()
        self.create_wifi_analyzer_tab()

        # Bottom panel - Progress and controls
        bottom_panel = self.create_control_panel()
        main_layout.addWidget(bottom_panel)

    def create_port_scanner_tab(self) -> QWidget:
        """Create the port scanner tab."""
        tab = QWidget()
        layout = QHBoxLayout(tab)

        # Left panel - Configuration
        config_panel = QWidget()
        config_layout = QVBoxLayout(config_panel)
        config_panel.setMaximumWidth(350)

        # Target configuration
        target_group = _ui_widget(QGroupBox, 'Legacy.sf1488e5474179293', 'setTitle')
        target_layout = QGridLayout(target_group)

        target_layout.addWidget(_ui_widget(QLabel, 'Legacy.s890d34fffcde315c', 'setText'), 0, 0)
        self.edit_target = QLineEdit()
        _ui_bind(self.edit_target, 'setAccessibleName', 'Legacy.s3e04ed907ad4dfe0')
        _ui_bind(self.edit_target, 'setPlaceholderText', 'Legacy.s35a4c86aca3e6491')
        target_layout.addWidget(self.edit_target, 0, 1)

        target_layout.addWidget(_ui_widget(QLabel, 'Legacy.s57cc3a094b97feb0', 'setText'), 1, 0)
        self.edit_ports = QLineEdit()
        _ui_bind(self.edit_ports, 'setAccessibleName', 'Legacy.se67c8404565601f0')
        _ui_bind(self.edit_ports, 'setAccessibleDescription', 'Legacy.s2a16575f9eb339ee')
        self.edit_ports.setText("22,80,443,21,25,53,110,143,993,995,3389,5900")
        target_layout.addWidget(self.edit_ports, 1, 1)

        target_layout.addWidget(_ui_widget(QLabel, 'Legacy.s7c5499f8e961102e', 'setText'), 2, 0)
        self.combo_scan_type = QComboBox()
        _ui_bind(self.combo_scan_type, 'setAccessibleName', 'Legacy.se317806114c1edbc')
        self.combo_scan_type.addItems(["TCP Connect", "TCP SYN", "UDP"])
        target_layout.addWidget(self.combo_scan_type, 2, 1)

        config_layout.addWidget(target_group)

        # Options
        options_group = _ui_widget(QGroupBox, 'Legacy.sd0db8b5e364b6989', 'setTitle')
        options_layout = QVBoxLayout(options_group)

        self.chk_service_detection = _ui_widget(QCheckBox, 'Legacy.sf55a764546dfe1a4', 'setText')
        _ui_bind(self.chk_service_detection, 'setAccessibleName', 'Legacy.s48a3d28c92e0a9a9')
        _ui_bind(self.chk_service_detection, 'setAccessibleDescription', 'Legacy.sfd649117b6e764ec')
        self.chk_service_detection.setMinimumHeight(44)
        self.chk_service_detection.setChecked(True)
        options_layout.addWidget(self.chk_service_detection)

        self.chk_banner_grab = _ui_widget(QCheckBox, 'Legacy.se9657f64691376dd', 'setText')
        _ui_bind(self.chk_banner_grab, 'setAccessibleName', 'Legacy.se8df6d4d9ac16023')
        _ui_bind(self.chk_banner_grab, 'setAccessibleDescription', 'Legacy.s90573d6da4a04145')
        self.chk_banner_grab.setMinimumHeight(44)
        options_layout.addWidget(self.chk_banner_grab)

        self.chk_stealth_mode = _ui_widget(QCheckBox, 'Legacy.s9eeec5fef8dd985b', 'setText')
        _ui_bind(self.chk_stealth_mode, 'setAccessibleName', 'Legacy.s2088f8a23433bb6b')
        _ui_bind(self.chk_stealth_mode, 'setAccessibleDescription', 'Legacy.s20c84afde6650751')
        self.chk_stealth_mode.setMinimumHeight(44)
        options_layout.addWidget(self.chk_stealth_mode)

        config_layout.addWidget(options_group)

        # Scan button
        self.btn_start_scan = _ui_widget(PrimaryButton, 'Legacy.s4ec0ceaea3c853c2', 'setText')
        config_layout.addWidget(self.btn_start_scan)

        config_layout.addStretch()
        layout.addWidget(config_panel)

        # Right panel - Results
        results_panel = QWidget()
        results_layout = QVBoxLayout(results_panel)

        results_layout.addWidget(_ui_widget(QLabel, 'Legacy.sf05abd58eb52252a', 'setText'))

        # Results table
        self.table_scan_results = QTableWidget()
        _ui_bind(self.table_scan_results, 'setAccessibleName', 'Legacy.s92d56c9b20a2fae2')
        self.table_scan_results.setColumnCount(5)
        self.table_scan_results.setHorizontalHeaderLabels(
            ["Target", "Port", "State", "Service", "Banner"]
        )

        # Configure table
        header = self.table_scan_results.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.Stretch)

        results_layout.addWidget(self.table_scan_results)

        layout.addWidget(results_panel)

        self.tab_widget.addTab(tab, "Port Scanner")
        return tab

    def create_bandwidth_monitor_tab(self) -> QWidget:
        """Create the bandwidth monitor tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Configuration panel
        config_panel = QWidget()
        config_layout = QHBoxLayout(config_panel)

        config_layout.addWidget(_ui_widget(QLabel, 'Legacy.s0e0eb5c0ebcacb31', 'setText'))
        self.spin_duration = QSpinBox()
        _ui_bind(self.spin_duration, 'setAccessibleName', 'Legacy.s8b3eb54f8c396022')
        _ui_bind(self.spin_duration, 'setAccessibleDescription', 'Legacy.se27e5e8063bc2fea')
        self.spin_duration.setMinimumHeight(44)
        self.spin_duration.setMinimum(10)
        self.spin_duration.setMaximum(3600)
        self.spin_duration.setValue(60)
        config_layout.addWidget(self.spin_duration)

        config_layout.addWidget(_ui_widget(QLabel, 'Legacy.s620c84c402244f14', 'setText'))
        self.spin_interval = QSpinBox()
        _ui_bind(self.spin_interval, 'setAccessibleName', 'Legacy.s4d141f97bfdc5afc')
        _ui_bind(self.spin_interval, 'setAccessibleDescription', 'Legacy.sd34e06b561feca2c')
        self.spin_interval.setMinimumHeight(44)
        self.spin_interval.setMinimum(1)
        self.spin_interval.setMaximum(60)
        self.spin_interval.setValue(1)
        config_layout.addWidget(self.spin_interval)

        self.btn_start_monitor = _ui_widget(PrimaryButton, 'Legacy.sa2f859806eb26f9b', 'setText')
        config_layout.addWidget(self.btn_start_monitor)

        config_layout.addStretch()
        layout.addWidget(config_panel)

        # Statistics display
        stats_panel = QWidget()
        stats_layout = QGridLayout(stats_panel)

        stats_layout.addWidget(_ui_widget(QLabel, 'Legacy.s4e3562116bb64636', 'setText'), 0, 0)
        self.lbl_download_speed = QLabel(DEFAULT_SPEED_LABEL)
        self.lbl_download_speed.setStyleSheet(
            f"font-weight: bold; color: {token('semantic_success')};"
        )
        stats_layout.addWidget(self.lbl_download_speed, 0, 1)

        stats_layout.addWidget(_ui_widget(QLabel, 'Legacy.sabed73a9b6d1f994', 'setText'), 1, 0)
        self.lbl_upload_speed = QLabel(DEFAULT_SPEED_LABEL)
        self.lbl_upload_speed.setStyleSheet(
            f"font-weight: bold; color: {token('semantic_warning')};"
        )
        stats_layout.addWidget(self.lbl_upload_speed, 1, 1)

        layout.addWidget(stats_panel)

        # Data log
        layout.addWidget(_ui_widget(QLabel, 'Legacy.sacddffcb1ad51fb3', 'setText'))
        self.text_bandwidth_log = QTextEdit()
        _ui_bind(self.text_bandwidth_log, 'setAccessibleName', 'Legacy.s5db69d2e72ac38f2')
        self.text_bandwidth_log.setMaximumHeight(200)
        self.text_bandwidth_log.setReadOnly(True)
        layout.addWidget(self.text_bandwidth_log)

        self.tab_widget.addTab(tab, "Bandwidth Monitor")
        return tab

    def create_network_discovery_tab(self) -> QWidget:
        """Create the network discovery tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Configuration
        config_panel = QWidget()
        config_layout = QHBoxLayout(config_panel)

        config_layout.addWidget(_ui_widget(QLabel, 'Legacy.s76011314cc1f2ee6', 'setText'))
        self.edit_network = QLineEdit()
        _ui_bind(self.edit_network, 'setAccessibleName', 'Legacy.sb277b34e3183fba4')
        self.edit_network.setText("192.168.1.0/24")
        _ui_bind(self.edit_network, 'setPlaceholderText', 'Legacy.sd01a825c13311b46')
        config_layout.addWidget(self.edit_network)

        self.btn_discover = _ui_widget(PrimaryButton, 'Legacy.sb272c4e5c1d1ca1d', 'setText')
        config_layout.addWidget(self.btn_discover)

        config_layout.addStretch()
        layout.addWidget(config_panel)

        # Results table
        layout.addWidget(_ui_widget(QLabel, 'Legacy.saf84e7f193ae9b65', 'setText'))
        self.table_hosts = QTableWidget()
        _ui_bind(self.table_hosts, 'setAccessibleName', 'Legacy.s325d7fc58e8ebb6f')
        self.table_hosts.setColumnCount(4)
        self.table_hosts.setHorizontalHeaderLabels(
            ["IP Address", "Hostname", "Status", "Response Time (ms)"]
        )

        # Configure table
        header = self.table_hosts.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)

        layout.addWidget(self.table_hosts)

        self.tab_widget.addTab(tab, "Network Discovery")
        return tab

    def create_connectivity_test_tab(self) -> QWidget:
        """Create the connectivity test tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Configuration
        config_panel = QWidget()
        config_layout = QVBoxLayout(config_panel)

        config_layout.addWidget(_ui_widget(QLabel, 'Legacy.sbe96f54d225b1a48', 'setText'))
        self.text_targets = QTextEdit()
        _ui_bind(self.text_targets, 'setAccessibleName', 'Legacy.sa70933e75ba37f69')
        self.text_targets.setMaximumHeight(100)
        self.text_targets.setText("8.8.8.8\ngoogle.com\nbing.com\ncloudflare.com")
        config_layout.addWidget(self.text_targets)

        self.btn_test_connectivity = _ui_widget(PrimaryButton, 'Legacy.sebf0f1e9ae77aa3e', 'setText')
        config_layout.addWidget(self.btn_test_connectivity)

        layout.addWidget(config_panel)

        # Results table
        layout.addWidget(_ui_widget(QLabel, 'Legacy.s8f801f4f84a55efe', 'setText'))
        self.table_connectivity = QTableWidget()
        _ui_bind(self.table_connectivity, 'setAccessibleName', 'Legacy.s1bb1c3cd37321068')
        self.table_connectivity.setColumnCount(4)
        self.table_connectivity.setHorizontalHeaderLabels(
            ["Target", "Reachable", "Response Time (ms)", "Error"]
        )

        # Configure table
        header = self.table_connectivity.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)

        layout.addWidget(self.table_connectivity)

        self.tab_widget.addTab(tab, "Connectivity Test")
        return tab

    def create_wifi_analyzer_tab(self) -> QWidget:
        """Create the WiFi analyzer tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Configuration
        config_panel = QWidget()
        config_layout = QHBoxLayout(config_panel)

        self.btn_scan_wifi = _ui_widget(PrimaryButton, 'Legacy.s877e25f73ba55b5e', 'setText')
        config_layout.addWidget(self.btn_scan_wifi)

        self.chk_show_hidden = _ui_widget(QCheckBox, 'Legacy.s07ff829921c4e1ae', 'setText')
        _ui_bind(self.chk_show_hidden, 'setAccessibleName', 'Legacy.s7c57e7b4627fccb1')
        self.chk_show_hidden.setMinimumHeight(44)
        config_layout.addWidget(self.chk_show_hidden)

        config_layout.addStretch()
        layout.addWidget(config_panel)

        # Results table
        layout.addWidget(_ui_widget(QLabel, 'Legacy.s98196611eb10d4ba', 'setText'))
        self.table_wifi = QTableWidget()
        _ui_bind(self.table_wifi, 'setAccessibleName', 'Legacy.s3216945bbba11765')
        self.table_wifi.setColumnCount(3)
        self.table_wifi.setHorizontalHeaderLabels(
            ["SSID", "Signal Strength", "Security"]
        )

        # Configure table
        header = self.table_wifi.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)

        layout.addWidget(self.table_wifi)

        self.tab_widget.addTab(tab, "WiFi Analyzer")
        return tab

    def create_control_panel(self) -> QWidget:
        """Create the control panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Status label
        self.lbl_status = _ui_widget(QLabel, 'Legacy.s5fa7aac5375c5815', 'setText')
        layout.addWidget(self.lbl_status)

        # Action buttons
        btn_layout = QHBoxLayout()

        self.btn_cancel = _ui_widget(SecondaryButton, 'Legacy.s8c5701a834c26f05', 'setText')
        self.btn_cancel.setEnabled(False)

        self.btn_export = _ui_widget(SecondaryButton, 'Legacy.s97df6c79050ddf07', 'setText')

        self.btn_clear = _ui_widget(SecondaryButton, 'Legacy.s6b46cb7814332a7a', 'setText')

        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_export)
        btn_layout.addWidget(self.btn_clear)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)

        return panel

    def connect_signals(self):
        """Connect signals and slots."""
        # Port scanner
        self.btn_start_scan.clicked.connect(self.start_port_scan)

        # Bandwidth monitor
        self.btn_start_monitor.clicked.connect(self.start_bandwidth_monitor)

        # Network discovery
        self.btn_discover.clicked.connect(self.start_network_discovery)

        # Connectivity test
        self.btn_test_connectivity.clicked.connect(self.start_connectivity_test)

        # WiFi analyzer
        self.btn_scan_wifi.clicked.connect(self.start_wifi_scan)

        # Control buttons
        self.btn_cancel.clicked.connect(self.cancel_operation)
        self.btn_export.clicked.connect(self.export_results)
        self.btn_clear.clicked.connect(self.clear_results)

    def start_port_scan(self):
        """Start port scanning."""
        target = self.edit_target.text().strip()
        if not target:  # ERR: non-fatal — surfaced via Modal; missing user input
            if Modal:
                Modal(
                    _NetworkToolsStrings.MODAL_ERROR_TITLE,
                    _NetworkToolsStrings.ERR_NO_TARGET,
                    ["OK"],
                    self,
                ).exec_()
            return

        ports_text = self.edit_ports.text().strip()
        try:
            ports = [int(p.strip()) for p in ports_text.split(",")]
        except ValueError:  # ERR: non-fatal — surfaced via Modal; invalid user input
            if Modal:
                Modal(
                    _NetworkToolsStrings.MODAL_ERROR_TITLE,
                    _NetworkToolsStrings.ERR_PORT_INVALID,
                    ["OK"],
                    self,
                ).exec_()
            return

        parameters = {
            "target": target,
            "ports": ports,
            "scan_type": self.combo_scan_type.currentText().lower().replace(" ", "_"),
            "service_detection": self.chk_service_detection.isChecked(),
            "banner_grab": self.chk_banner_grab.isChecked(),
            "stealth_mode": self.chk_stealth_mode.isChecked(),
        }

        self.start_operation("port_scan", parameters)

    def start_bandwidth_monitor(self):
        """Start bandwidth monitoring."""
        parameters = {
            "duration": self.spin_duration.value(),
            "interval": self.spin_interval.value(),
        }

        self.start_operation("bandwidth_monitor", parameters)

    def start_network_discovery(self):
        """Start network discovery."""
        network = self.edit_network.text().strip()
        if not network:
            if Modal:
                Modal("Warning", "Please enter a network", ["OK"], self).exec_()
            else:
                QMessageBox.warning(self, "Warning", "Please enter a network")
            return

        parameters = {"network": network}

        self.start_operation("network_discovery", parameters)

    def start_connectivity_test(self):
        """Start connectivity test."""
        targets_text = self.text_targets.toPlainText().strip()
        if not targets_text:
            if Modal:
                Modal("Warning", "Please enter test targets", ["OK"], self).exec_()
            else:
                QMessageBox.warning(self, "Warning", "Please enter test targets")
            return

        targets = [t.strip() for t in targets_text.split("\n") if t.strip()]

        parameters = {"targets": targets}

        self.start_operation("connectivity_test", parameters)

    def start_wifi_scan(self):
        """Start WiFi scanning."""
        parameters = {"show_hidden": self.chk_show_hidden.isChecked()}

        self.start_operation("wifi_scan", parameters)

    def start_operation(self, operation_type: str, parameters: Dict[str, Any]):
        """Start a network operation."""
        if self.worker_thread and self.worker_thread.isRunning():
            if Modal:
                Modal(
                    "Warning", "An operation is already running", ["OK"], self
                ).exec_()
            else:
                QMessageBox.warning(self, "Warning", "An operation is already running")
            return

        # Disable relevant buttons
        self.btn_cancel.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        # Clear previous results for this operation type
        self.clear_operation_results(operation_type)

        # Start worker thread
        self.worker_thread = NetworkWorkerThread(operation_type, parameters)

        # Connect signals
        self.worker_thread.progress_updated.connect(self.on_progress_updated)
        self.worker_thread.scan_result.connect(self.on_scan_result)
        self.worker_thread.bandwidth_data.connect(self.on_bandwidth_data)
        self.worker_thread.operation_completed.connect(self.on_operation_completed)
        self.worker_thread.error_occurred.connect(self.on_error_occurred)

        self.worker_thread.start()

    def cancel_operation(self):
        """Cancel the current operation."""
        if self.worker_thread:
            self.worker_thread.cancel()
            # PERF-2b: do not block-wait on the UI thread.
            # operation_completed signal → on_operation_completed → on_operation_finished
            # handles UI cleanup when the worker finishes.

    def on_progress_updated(self, progress: int, status: str):
        """Handle progress update."""
        self.progress_bar.setValue(progress)
        self.lbl_status.setText(status)

    def on_scan_result(self, result: Dict[str, Any]):
        """Handle scan result."""
        if "port" in result:  # Port scan result
            self.add_port_scan_result(result)
        elif "ssid" in result:  # WiFi scan result
            self.add_wifi_result(result)
        elif "ip" in result:  # Network discovery result
            self.add_host_result(result)
        elif "reachable" in result:  # Connectivity test result
            self.add_connectivity_result(result)

    def on_bandwidth_data(self, data: Dict[str, Any]):
        """Handle bandwidth data."""
        # Update statistics
        # Convert to MB/s
        download_speed = data["download_speed"] / (1024 * 1024)
        upload_speed = data["upload_speed"] / (1024 * 1024)

        self.lbl_download_speed.setText(f"{download_speed:.2f} MB/s")
        self.lbl_upload_speed.setText(f"{upload_speed:.2f} MB/s")

        # Add to log
        timestamp = datetime.fromisoformat(data["timestamp"]).strftime("%H:%M:%S")
        log_entry = (
            f"[{timestamp}] Down: {download_speed:.2f} MB/s, "
            f"Up: {upload_speed:.2f} MB/s\n"
        )
        self.text_bandwidth_log.append(log_entry)
        self.text_bandwidth_log.ensureCursorVisible()

    def on_operation_completed(self, success: bool, message: str):
        """Handle operation completion."""
        self.on_operation_finished()

        if success:
            self.lbl_status.setText(f"Completed: {message}")
        else:
            if Modal:
                Modal("Operation Failed", message, ["OK"], self).exec_()
            else:
                QMessageBox.warning(self, "Operation Failed", message)

    def on_error_occurred(self, error_message: str):
        """Handle error."""
        if Modal:
            Modal("Error", error_message, ["OK"], self).exec_()
        else:
            QMessageBox.critical(self, "Error", error_message)
        self.on_operation_finished()

    def on_operation_finished(self):
        """Handle operation finishing."""
        self.btn_cancel.setEnabled(False)
        self.progress_bar.setVisible(False)

        if self.worker_thread:
            self.worker_thread = None

    def add_port_scan_result(self, result: Dict[str, Any]):
        """Add port scan result to table."""
        table = self.table_scan_results
        row = table.rowCount()
        table.insertRow(row)

        table.setItem(row, 0, QTableWidgetItem(result["target"]))
        table.setItem(row, 1, QTableWidgetItem(str(result["port"])))

        state_item = QTableWidgetItem(result["state"])
        if result["state"] == "open":
            state_item.setBackground(QColor(76, 175, 80, 100))  # Light green
        elif result["state"] == "closed":
            state_item.setBackground(QColor(244, 67, 54, 100))  # Light red
        else:
            state_item.setBackground(QColor(255, 152, 0, 100))  # Light orange

        table.setItem(row, 2, state_item)
        table.setItem(row, 3, QTableWidgetItem(result["service"]))
        table.setItem(row, 4, QTableWidgetItem(result.get("banner", "")))

    def add_wifi_result(self, result: Dict[str, Any]):
        """Add WiFi result to table."""
        table = self.table_wifi
        row = table.rowCount()
        table.insertRow(row)

        table.setItem(row, 0, QTableWidgetItem(result["ssid"]))
        table.setItem(row, 1, QTableWidgetItem(f"{result['signal']} dBm"))
        table.setItem(row, 2, QTableWidgetItem(result["security"]))

    def add_host_result(self, result: Dict[str, Any]):
        """Add host discovery result to table."""
        table = self.table_hosts
        row = table.rowCount()
        table.insertRow(row)

        table.setItem(row, 0, QTableWidgetItem(result["ip"]))
        table.setItem(row, 1, QTableWidgetItem(result["hostname"]))

        status_item = QTableWidgetItem(result["status"])
        if result["status"] == "alive":
            status_item.setBackground(QColor(76, 175, 80, 100))  # Light green

        table.setItem(row, 2, status_item)
        table.setItem(row, 3, QTableWidgetItem(str(result["response_time"])))

    def add_connectivity_result(self, result: Dict[str, Any]):
        """Add connectivity result to table."""
        table = self.table_connectivity
        row = table.rowCount()
        table.insertRow(row)

        table.setItem(row, 0, QTableWidgetItem(result["target"]))

        reachable_item = QTableWidgetItem("Yes" if result["reachable"] else "No")
        if result["reachable"]:
            reachable_item.setBackground(QColor(76, 175, 80, 100))  # Light green
        else:
            reachable_item.setBackground(QColor(244, 67, 54, 100))  # Light red

        table.setItem(row, 1, reachable_item)
        table.setItem(row, 2, QTableWidgetItem(f"{result['response_time']:.2f}"))
        table.setItem(row, 3, QTableWidgetItem(result.get("error", "")))

    def clear_operation_results(self, operation_type: str):
        """Clear results for specific operation type."""
        if operation_type == "port_scan":
            self.table_scan_results.setRowCount(0)
        elif operation_type == "wifi_scan":
            self.table_wifi.setRowCount(0)
        elif operation_type == "network_discovery":
            self.table_hosts.setRowCount(0)
        elif operation_type == "connectivity_test":
            self.table_connectivity.setRowCount(0)
        elif operation_type == "bandwidth_monitor":
            self.text_bandwidth_log.clear()
            self.lbl_download_speed.setText(DEFAULT_SPEED_LABEL)
            self.lbl_upload_speed.setText(DEFAULT_SPEED_LABEL)

    def clear_results(self):
        """Clear all results."""
        tables = [
            self.table_scan_results,
            self.table_wifi,
            self.table_hosts,
            self.table_connectivity,
        ]

        for table in tables:
            table.setRowCount(0)

        self.text_bandwidth_log.clear()
        self.lbl_download_speed.setText(DEFAULT_SPEED_LABEL)
        self.lbl_upload_speed.setText(DEFAULT_SPEED_LABEL)

        self.lbl_status.setText("Ready")

    def export_results(self):
        """Export results to file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Results",
            "network_tools_results.txt",
            "Text Files (*.txt);;CSV Files (*.csv);;All Files (*)",
        )

        if file_path:
            try:
                with open(file_path, "w") as f:
                    f.write("Network Tools Results\n")
                    f.write("=" * 50 + "\n\n")

                    # Export each tab's data
                    self.export_table_data(
                        f, "Port Scan Results", self.table_scan_results
                    )
                    self.export_table_data(f, "WiFi Networks", self.table_wifi)
                    self.export_table_data(f, "Discovered Hosts", self.table_hosts)
                    self.export_table_data(
                        f, "Connectivity Results", self.table_connectivity
                    )

                    # Export bandwidth log
                    if self.text_bandwidth_log.toPlainText():
                        f.write("\nBandwidth Monitor Log:\n")
                        f.write("-" * 30 + "\n")
                        f.write(self.text_bandwidth_log.toPlainText())

                if Modal:
                    Modal(
                        "Export Complete",
                        f"Results exported to {file_path}",
                        ["OK"],
                        self,
                    ).exec_()
                else:
                    QMessageBox.information(
                        self, "Export Complete", f"Results exported to {file_path}"
                    )

            except Exception as e:  # ERR: non-fatal — surfaced via Modal
                self._logger.error(
                    f"Error exporting network results: {e}", exc_info=True
                )
                if Modal:
                    Modal(
                        _NetworkToolsStrings.MODAL_ERROR_TITLE,
                        _NetworkToolsStrings.ERR_EXPORT_FAILED,
                        ["OK"],
                        self,
                    ).exec_()

    def export_table_data(self, file_handle, title: str, table: QTableWidget):
        """Export table data to file."""
        if table.rowCount() == 0:
            return

        file_handle.write(f"\n{title}:\n")
        file_handle.write("-" * len(title) + "\n")

        # Write headers
        headers = []
        for col in range(table.columnCount()):
            headers.append(table.horizontalHeaderItem(col).text())
        file_handle.write(" | ".join(headers) + "\n")
        file_handle.write("-" * (len(" | ".join(headers))) + "\n")

        # Write data
        for row in range(table.rowCount()):
            row_data = []
            for col in range(table.columnCount()):
                item = table.item(row, col)
                row_data.append(item.text() if item else "")
            file_handle.write(" | ".join(row_data) + "\n")

        file_handle.write("\n")

    def closeEvent(self, event):
        """Handle window close event."""
        if self.worker_thread and self.worker_thread.isRunning():
            if Modal:
                confirmed = (
                    Modal(
                        "Confirm Close",
                        "Network operation is in progress. Cancel and close?",
                        ["Yes", "No"],
                        self,
                    ).exec_()
                    == 1
                )  # QDialog.Accepted
            else:
                reply = QMessageBox.question(
                    self,
                    "Confirm Close",
                    "Network operation is in progress. Cancel and close?",
                    QMessageBox.Yes | QMessageBox.No,
                )
                confirmed = reply == QMessageBox.Yes

            if confirmed:
                self.cancel_operation()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


def main():
    """Main function for standalone execution."""
    app = QApplication(sys.argv)
    app.setApplicationName("Network Tools")

    # Set application style
    app.setStyle("Fusion")

    window = NetworkToolsWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
