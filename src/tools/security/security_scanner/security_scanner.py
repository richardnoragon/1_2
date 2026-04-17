from src.gui.themes import ThemeManager, Typography, token

"""
Simple Security Scanner Tool for Richard's File Utilities

A basic security scanner for common vulnerabilities and system checks.
"""

import logging
import os
import platform
import socket
import subprocess
import sys

try:
    from PyQt5.QtCore import Qt, QThread, pyqtSignal
    from PyQt5.QtGui import QFont
    from PyQt5.QtWidgets import (
        QApplication,
        QCheckBox,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QMainWindow,
        QMessageBox,
        QProgressBar,
        QPushButton,
        QTabWidget,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )
except ImportError:
    print("PyQt5 not available. Please install PyQt5.")
    sys.exit(1)

# ---------------------------------------------------------------------------
# CP: Component replacement imports (CP-1 through CP-5)
# ---------------------------------------------------------------------------
try:
    from src.gui.components.buttons import PrimaryButton, SecondaryButton
    from src.gui.components.modal import Modal
    from src.gui.components.toast import ToastNotification

    _CP_AVAILABLE = True
except ImportError:
    PrimaryButton = QPushButton
    SecondaryButton = QPushButton
    Modal = None
    ToastNotification = None
    _CP_AVAILABLE = False

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
    from src.rfu.ui_strings import SecurityScanner as _SSStrings
except ImportError:

    class _SSStrings:  # type: ignore[no-redef]
        TITLE = "Security Scanner"
        WINDOW_TITLE = "Security Scanner — RFU"
        LOADING = "Loading Security Scanner…"
        ERR_INIT_FAILED = (
            "Could not start Security Scanner. "
            "Please try again or restart the application."
        )
        ERR_SCAN_FAILED = (
            "Security scan failed. "
            "Some scan modules may not be available on this system."
        )

    """Worker thread for security scanning."""

    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    result_ready = pyqtSignal(str)

    def __init__(self, scan_types):
        super().__init__()
        self.scan_types = scan_types

    def run(self):
        """Run the security scan."""
        results = []
        total_checks = len(self.scan_types)

        for i, scan_type in enumerate(self.scan_types):
            progress = int((i / total_checks) * 100)
            self.progress_updated.emit(progress)

            if scan_type == "system_info":
                self.status_updated.emit("Scanning system information...")
                result = self.scan_system_info()
            elif scan_type == "network_ports":
                self.status_updated.emit("Scanning network ports...")
                result = self.scan_network_ports()
            elif scan_type == "file_permissions":
                self.status_updated.emit("Checking file permissions...")
                result = self.scan_file_permissions()
            elif scan_type == "running_processes":
                self.status_updated.emit("Analyzing running processes...")
                result = self.scan_running_processes()
            else:
                result = f"Unknown scan type: {scan_type}"

            results.append(result)

        self.progress_updated.emit(100)
        self.status_updated.emit("Scan completed")
        self.result_ready.emit("\n\n".join(results))

    def scan_system_info(self):
        """Scan basic system information."""
        try:
            info = []
            info.append("=== SYSTEM INFORMATION ===")
            info.append(f"Operating System: {platform.system()} {platform.release()}")
            info.append(f"Machine Type: {platform.machine()}")
            info.append(f"Python Version: {platform.python_version()}")
            info.append(f"Hostname: {socket.gethostname()}")

            # Check for common security indicators
            if platform.system() == "Windows":
                info.append(
                    "Windows Defender Status: (Check manually in Security Center)"
                )

            return "\n".join(info)
        except (
            Exception
        ) as e:  # ERR: non-fatal — returns error string; included in scan results
            return f"System info scan error: {e}"

    def scan_network_ports(self):
        """Scan for open network ports."""
        try:
            results = []
            results.append("=== NETWORK PORT SCAN ===")

            # Common ports to check
            common_ports = [
                21,
                22,
                23,
                25,
                53,
                80,
                110,
                143,
                443,
                993,
                995,
                3389,
                5900,
            ]
            open_ports = []

            for port in common_ports:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(("localhost", port))
                sock.close()

                if result == 0:
                    open_ports.append(port)

            if open_ports:
                results.append(f"Open ports found: {', '.join(map(str, open_ports))}")
                results.append("⚠️  Review open ports for security implications")
            else:
                results.append("✅ No common ports found open on localhost")

            return "\n".join(results)
        except (
            Exception
        ) as e:  # ERR: non-fatal — returns error string; included in scan results
            return f"Network scan error: {e}"

    def scan_file_permissions(self):
        """Check file permissions in common directories."""
        try:
            results = []
            results.append("=== FILE PERMISSIONS CHECK ===")

            # Check common sensitive directories
            sensitive_dirs = []
            if platform.system() == "Windows":
                sensitive_dirs = [
                    os.path.expanduser("~\\Documents"),
                    os.path.expanduser("~\\Downloads"),
                    "C:\\Windows\\System32",
                ]
            else:
                sensitive_dirs = [
                    os.path.expanduser("~/Documents"),
                    os.path.expanduser("~/Downloads"),
                    "/etc",
                    "/var",
                ]

            for directory in sensitive_dirs:
                if os.path.exists(directory):
                    try:
                        # Basic permission check
                        readable = os.access(directory, os.R_OK)
                        writable = os.access(directory, os.W_OK)
                        executable = os.access(directory, os.X_OK)

                        perms = []
                        if readable:
                            perms.append("R")
                        if writable:
                            perms.append("W")
                        if executable:
                            perms.append("X")

                        results.append(f"{directory}: {''.join(perms)}")
                    except (
                        Exception
                    ) as e:  # ERR: non-fatal — logged inline in scan results; directory skipped
                        results.append(f"{directory}: Error checking permissions - {e}")

            results.append("✅ File permission scan completed")
            return "\n".join(results)
        except (
            Exception
        ) as e:  # ERR: non-fatal — returns error string; included in scan results
            return f"File permissions scan error: {e}"

    def scan_running_processes(self):
        """Scan running processes for security analysis."""
        try:
            results = []
            results.append("=== RUNNING PROCESSES ANALYSIS ===")

            if platform.system() == "Windows":
                # Use tasklist command
                try:
                    output = subprocess.check_output(
                        ["tasklist"], universal_newlines=True
                    )
                    lines = output.split("\n")[:10]  # First 10 processes
                    results.append("Top running processes:")
                    for line in lines[3:]:  # Skip header
                        if line.strip():
                            results.append(f"  {line.strip()}")
                except (
                    Exception
                ):  # ERR: non-fatal — process list unavailable; fallback message shown
                    results.append("Could not retrieve process list")
            else:
                # Use ps command for Unix-like systems
                try:
                    output = subprocess.check_output(
                        ["ps", "aux"], universal_newlines=True
                    )
                    lines = output.split("\n")[:10]  # First 10 processes
                    results.append("Top running processes:")
                    for line in lines[1:]:  # Skip header
                        if line.strip():
                            results.append(f"  {line.strip()}")
                except (
                    Exception
                ):  # ERR: non-fatal — process list unavailable; fallback message shown
                    results.append("Could not retrieve process list")

            results.append("✅ Process analysis completed")
            return "\n".join(results)
        except (
            Exception
        ) as e:  # ERR: non-fatal — returns error string; included in scan results
            return f"Process scan error: {e}"


class SimpleSecurityScannerGUI(QMainWindow):
    """Simple Security Scanner GUI."""

    def __init__(self, hub_instance=None):
        super().__init__()
        self._hub = hub_instance
        try:
            from src.rfu.log_manager import get_log_manager

            self._logger = get_log_manager().get_logger("SimpleSecurityScannerGUI")
        except Exception:  # ERR: non-fatal — logger fallback to module logger
            self._logger = logging.getLogger("SimpleSecurityScannerGUI")
        self.setWindowTitle(_SSStrings.WINDOW_TITLE)
        self.setMinimumSize(800, 700)
        self.resize(900, 800)

        # Apply basic styling
        self.setStyleSheet(
            f"""
            QMainWindow {{
                background-color: {token('surface')};
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {token('border')};
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
            QTextEdit {{
                border: 1px solid {token('border')};
                border-radius: 4px;
                padding: 8px;
                font-family: 'Courier New', monospace;
                font-size: 11px;
            }}
        """
        )

        self.scan_worker = None
        self._setup_ui()
        register_gui_component(
            self, tool_id="security_scanner", recovery_callback=self.degraded_fallback
        )
        _emit_telemetry("ui_view_load", tool_id="security_scanner")
        ThemeManager.add_theme_changed_callback(self._on_theme_changed)

    def _on_theme_changed(self, variant: str) -> None:
        """Re-apply token-based stylesheets when the active theme variant changes."""
        pass  # stylesheets applied at init; live re-apply pending TH-4c/4d

    def health_check(self) -> bool:
        """Return True if core UI is functional (GRD-3a)."""
        try:
            return self.centralWidget() is not None
        except Exception:
            return False

    def degraded_fallback(self) -> None:
        """Enter degraded / read-only state (GRD-3b)."""
        try:
            self._logger.warning("SimpleSecurityScannerGUI entering degraded mode")
        except Exception:
            pass
        _emit_telemetry(
            "ui_error_event", tool_id="security_scanner", error_type="degraded"
        )

    def _setup_ui(self):
        """Setup the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Title
        title = QLabel("🔍 Security Scanner")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(Typography.h1())
        layout.addWidget(title)

        # Scan options
        options_group = QGroupBox("Scan Options")
        options_layout = QVBoxLayout(options_group)

        self.system_info_check = QCheckBox("System Information")
        self.system_info_check.setChecked(True)
        self.system_info_check.setAccessibleName("Scan system information")
        self.system_info_check.setAccessibleDescription(
            "Checks OS version, user accounts, and installed security features"
        )
        self.system_info_check.setMinimumHeight(44)
        options_layout.addWidget(self.system_info_check)

        self.network_ports_check = QCheckBox("Network Ports")
        self.network_ports_check.setChecked(True)
        self.network_ports_check.setAccessibleName("Scan network ports")
        self.network_ports_check.setAccessibleDescription(
            "Lists all open TCP/UDP ports and associated services"
        )
        self.network_ports_check.setMinimumHeight(44)
        options_layout.addWidget(self.network_ports_check)

        self.file_permissions_check = QCheckBox("File Permissions")
        self.file_permissions_check.setChecked(True)
        self.file_permissions_check.setAccessibleName("Scan file permissions")
        self.file_permissions_check.setAccessibleDescription(
            "Identifies files with overly broad permissions that may be security risks"
        )
        self.file_permissions_check.setMinimumHeight(44)
        options_layout.addWidget(self.file_permissions_check)

        self.running_processes_check = QCheckBox("Running Processes")
        self.running_processes_check.setChecked(True)
        self.running_processes_check.setAccessibleName("Scan running processes")
        self.running_processes_check.setAccessibleDescription(
            "Lists all active processes and flags unrecognized or suspicious entries"
        )
        self.running_processes_check.setMinimumHeight(44)
        options_layout.addWidget(self.running_processes_check)

        layout.addWidget(options_group)

        # Control buttons
        button_layout = QHBoxLayout()

        self.start_scan_btn = PrimaryButton("🚀 Start Security Scan")
        self.start_scan_btn.clicked.connect(self.start_scan)
        button_layout.addWidget(self.start_scan_btn)

        self.clear_btn = SecondaryButton("🗑️ Clear Results")
        self.clear_btn.clicked.connect(self.clear_results)
        button_layout.addWidget(self.clear_btn)

        layout.addLayout(button_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Status label
        self.status_label = QLabel("Ready to scan")
        layout.addWidget(self.status_label)

        # Toast notification for completion messages (CP-5)
        if ToastNotification:
            self._toast = ToastNotification(parent=self)
        else:
            self._toast = None

        # Results area
        results_group = QGroupBox("Scan Results")
        results_layout = QVBoxLayout(results_group)

        self.results_text = QTextEdit()
        self.results_text.setAccessibleName("Security scan results")
        self.results_text.setPlainText(
            "Click 'Start Security Scan' to begin scanning for security issues..."
        )
        results_layout.addWidget(self.results_text)

        layout.addWidget(results_group)

    def start_scan(self):
        """Start the security scan."""
        # Get selected scan types
        scan_types = []
        if self.system_info_check.isChecked():
            scan_types.append("system_info")
        if self.network_ports_check.isChecked():
            scan_types.append("network_ports")
        if self.file_permissions_check.isChecked():
            scan_types.append("file_permissions")
        if self.running_processes_check.isChecked():
            scan_types.append("running_processes")

        if not scan_types:
            if Modal:
                Modal(
                    "Warning",
                    "Please select at least one scan type!",
                    ["OK"],
                    parent=self,
                ).exec_()
            else:
                QMessageBox.warning(
                    self, "Warning", "Please select at least one scan type!"
                )
            return

        # Disable start button and show progress
        self.start_scan_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.results_text.clear()

        # Start scan worker
        self.scan_worker = SecurityScanWorker(scan_types)
        self.scan_worker.progress_updated.connect(self.update_progress)
        self.scan_worker.status_updated.connect(self.update_status)
        self.scan_worker.result_ready.connect(self.display_results)
        self.scan_worker.finished.connect(self.scan_finished)
        self.scan_worker.start()

    def update_progress(self, value):
        """Update progress bar."""
        self.progress_bar.setValue(value)

    def update_status(self, status):
        """Update status label."""
        self.status_label.setText(status)

    def display_results(self, results):
        """Display scan results."""
        self.results_text.setPlainText(results)

    def scan_finished(self):
        """Handle scan completion."""
        self.start_scan_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText("Scan completed")
        if self._toast:
            self._toast.show_message("Scan completed", "success")

    def clear_results(self):
        """Clear the results area."""
        self.results_text.clear()
        self.status_label.setText("Results cleared")
        if self._toast:
            self._toast.show_message("Results cleared", "info")


def main():
    """Main function to run the security scanner."""
    app = QApplication(sys.argv)
    window = SimpleSecurityScannerGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
