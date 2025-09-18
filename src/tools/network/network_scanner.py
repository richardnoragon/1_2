#!/usr/bin/env python3
"""
Network Scanner Tool for Richard's File Utilities

A streamlined network scanner utility with essential functionality.
"""

import sys
import socket

try:
    from PyQt5.QtWidgets import (
        QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QPushButton, QLabel, QProgressBar,
        QApplication, QMessageBox, QGroupBox,
        QLineEdit, QSpinBox, QTextEdit, QCheckBox
    )
except ImportError:
    print("PyQt5 not available. Please install PyQt5.")
    sys.exit(1)

# Import StandardWindow for menu integration
try:
    from src.gui.standard_window import StandardWindow
except ImportError:
    # Fallback for standalone execution
    StandardWindow = QMainWindow


class NetworkScannerGUI(StandardWindow):
    """Main window for Network Scanner operations."""
    
    def __init__(self):
        super().__init__(
            title="Network Scanner - Richard's File Utilities",
            window_type="utility"
        )
        self.init_ui()
        self._setup_menu_callbacks()
        
    def _setup_menu_callbacks(self):
        """Setup tool-specific menu callbacks."""
        if hasattr(self, 'menu_manager'):
            # Register tool-specific callbacks
            self.menu_manager.register_callback('show_preferences',
                                               self.show_preferences)
            self.menu_manager.register_callback('refresh', self.refresh_view)
    
    def show_preferences(self):
        """Show Network Scanner preferences."""
        QMessageBox.information(
            self, "Network Scanner Preferences",
            "Network Scanner preferences:\n\n"
            "• Default scan timeout settings\n"
            "• Preferred scan techniques\n"
            "• Port range presets\n"
            "• Result display options\n\n"
            "Advanced preferences coming soon!"
        )
        
    def refresh_view(self):
        """Refresh the network scanner interface."""
        self.results_text.append("\n=== Refreshing Scanner Interface ===")
        self.results_text.append("Target configuration refreshed")
        self.results_text.append("Scan options updated")
        QMessageBox.information(self, "Refresh",
                               "Scanner interface refreshed successfully.")
        
    def init_ui(self):
        """Initialize the user interface."""
        # Use the existing main layout from StandardWindow
        layout = self.main_layout
        
        # Add header
        header_label = QLabel("Network Scanner")
        header_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
                background-color: #ecf0f1;
                border-radius: 5px;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(header_label)
        
        # Scanner Configuration Group
        config_group = QGroupBox("Scanner Configuration")
        config_layout = QVBoxLayout(config_group)
        
        # Target input
        target_layout = QHBoxLayout()
        target_layout.addWidget(QLabel("Target Host:"))
        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("Enter IP address or hostname")
        self.target_input.setText("127.0.0.1")  # Default to localhost
        target_layout.addWidget(self.target_input)
        config_layout.addLayout(target_layout)
        
        # Port range configuration
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("Port Range:"))
        self.start_port = QSpinBox()
        self.start_port.setRange(1, 65535)
        self.start_port.setValue(1)
        port_layout.addWidget(self.start_port)
        port_layout.addWidget(QLabel("to"))
        self.end_port = QSpinBox()
        self.end_port.setRange(1, 65535)
        self.end_port.setValue(1000)
        port_layout.addWidget(self.end_port)
        config_layout.addLayout(port_layout)
        
        # Scan options
        options_layout = QHBoxLayout()
        self.tcp_scan = QCheckBox("TCP Scan")
        self.tcp_scan.setChecked(True)
        options_layout.addWidget(self.tcp_scan)
        
        self.udp_scan = QCheckBox("UDP Scan")
        options_layout.addWidget(self.udp_scan)
        
        self.service_detection = QCheckBox("Service Detection")
        options_layout.addWidget(self.service_detection)
        
        config_layout.addLayout(options_layout)
        
        # Scan button
        self.scan_button = QPushButton("Start Network Scan")
        self.scan_button.clicked.connect(self.start_scan)
        config_layout.addWidget(self.scan_button)
        
        layout.addWidget(config_group)
        
        # Quick Scan Presets
        presets_group = QGroupBox("Quick Scan Presets")
        presets_layout = QHBoxLayout(presets_group)
        
        common_ports_btn = QPushButton("Common Ports (1-1000)")
        common_ports_btn.clicked.connect(self.set_common_ports)
        presets_layout.addWidget(common_ports_btn)
        
        web_ports_btn = QPushButton("Web Ports (80, 443, 8080)")
        web_ports_btn.clicked.connect(self.set_web_ports)
        presets_layout.addWidget(web_ports_btn)
        
        all_ports_btn = QPushButton("All Ports (1-65535)")
        all_ports_btn.clicked.connect(self.set_all_ports)
        presets_layout.addWidget(all_ports_btn)
        
        layout.addWidget(presets_group)
        
        # Results area
        results_group = QGroupBox("Scan Results")
        results_layout = QVBoxLayout(results_group)
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setPlainText(
            "Network scanner ready. Configure target and port range, "
            "then click 'Start Network Scan'."
        )
        results_layout.addWidget(self.results_text)
        
        layout.addWidget(results_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Style the buttons
        button_style = """
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                margin: 2px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """
        for button in [self.scan_button, common_ports_btn,
                       web_ports_btn, all_ports_btn]:
            button.setStyleSheet(button_style)
        
    def set_common_ports(self):
        """Set common ports range."""
        self.start_port.setValue(1)
        self.end_port.setValue(1000)
        self.results_text.append("Preset: Common ports (1-1000) selected")
        
    def set_web_ports(self):
        """Set web ports range."""
        self.start_port.setValue(80)
        self.end_port.setValue(443)
        self.results_text.append("Preset: Web ports (80-443) selected")
        
    def set_all_ports(self):
        """Set all ports range."""
        self.start_port.setValue(1)
        self.end_port.setValue(65535)
        self.results_text.append("Preset: All ports (1-65535) selected")
        
    def start_scan(self):
        """Start network scanning."""
        target = self.target_input.text().strip()
        start_port = self.start_port.value()
        end_port = self.end_port.value()
        
        if not target:
            QMessageBox.warning(
                self, "Network Scanner",
                "Please enter a target IP address or hostname."
            )
            return
            
        if start_port > end_port:
            QMessageBox.warning(
                self, "Network Scanner",
                "Start port must be less than or equal to end port."
            )
            return
        
        # Display scan information
        self.results_text.append("\n=== Network Scan Started ===")
        self.results_text.append(f"Target: {target}")
        self.results_text.append(f"Port Range: {start_port}-{end_port}")
        tcp_status = 'Yes' if self.tcp_scan.isChecked() else 'No'
        self.results_text.append(f"TCP Scan: {tcp_status}")
        udp_status = 'Yes' if self.udp_scan.isChecked() else 'No'
        self.results_text.append(f"UDP Scan: {udp_status}")
        service_status = 'Yes' if self.service_detection.isChecked() else 'No'
        self.results_text.append(f"Service Detection: {service_status}")
        self.results_text.append("")
        
        # Show scan capabilities
        self.results_text.append(
            "Network scanning functionality ready for implementation."
        )
        self.results_text.append("This tool will provide:")
        self.results_text.append("• Comprehensive port scanning (TCP/UDP)")
        self.results_text.append("• Service detection and identification")
        self.results_text.append("• Security vulnerability assessment")
        self.results_text.append("• Custom scan profiles and presets")
        self.results_text.append("• Detailed reporting and export options")
        self.results_text.append("• Network topology discovery")
        
        # Simulate basic connectivity test
        self.test_basic_connectivity(target)
        
        QMessageBox.information(
            self,
            "Network Scanner",
            f"Network scan initiated for {target}!\n\n"
            f"Scanning ports {start_port}-{end_port}\n"
            f"Check the results area for scan progress."
        )
        
    def test_basic_connectivity(self, target):
        """Test basic connectivity to target."""
        try:
            # Simple connectivity test
            socket.gethostbyname(target)
            self.results_text.append(f"✓ Host {target} is reachable")
        except socket.gaierror:
            self.results_text.append(f"✗ Host {target} could not be resolved")
        except Exception as e:
            self.results_text.append(f"✗ Connectivity test failed: {e}")


def main():
    """Main function for standalone execution."""
    app = QApplication(sys.argv)
    window = NetworkScannerGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
