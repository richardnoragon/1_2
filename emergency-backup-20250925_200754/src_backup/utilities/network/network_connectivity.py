#!/usr/bin/env python3
"""
Network Connectivity GUI Wrapper for Richard's File Utilities

A simple GUI wrapper for network connectivity tools.
"""

import os
import sys
try:
    from PyQt5.QtWidgets import (
        QMainWindow, QWidget, QVBoxLayout,
        QPushButton, QLabel, QListWidget,
        QApplication, QMessageBox, QGroupBox
    )
except ImportError:
    print("PyQt5 not available. Please install PyQt5.")
    sys.exit(1)


class NetworkConnectivityGUI(QMainWindow):
    """Simple Network Connectivity GUI wrapper."""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Network Connectivity - Richard's File Utilities")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Add header
        header_label = QLabel("Network Connectivity Tools")
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
        
        # Tool buttons group
        tools_group = QGroupBox("Available Tools")
        tools_layout = QVBoxLayout(tools_group)
        
        # Network monitoring button
        monitor_button = QPushButton("Network Bandwidth Monitor")
        monitor_button.clicked.connect(self.open_bandwidth_monitor)
        tools_layout.addWidget(monitor_button)
        
        # Port scanner button
        scanner_button = QPushButton("Port Scanner")
        scanner_button.clicked.connect(self.open_port_scanner)
        tools_layout.addWidget(scanner_button)
        
        # WiFi analyzer button
        wifi_button = QPushButton("WiFi Analyzer")
        wifi_button.clicked.connect(self.open_wifi_analyzer)
        tools_layout.addWidget(wifi_button)
        
        # File transfer button
        transfer_button = QPushButton("LAN File Transfer")
        transfer_button.clicked.connect(self.open_file_transfer)
        tools_layout.addWidget(transfer_button)
        
        layout.addWidget(tools_group)
        
        # Status display
        status_group = QGroupBox("Status")
        status_layout = QVBoxLayout(status_group)
        
        self.status_list = QListWidget()
        self.status_list.addItem("Network connectivity tools ready")
        self.status_list.addItem("Click a tool button to access network features")
        status_layout.addWidget(self.status_list)
        
        layout.addWidget(status_group)
        
        # Style the buttons
        button_style = """
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """
        for button in [monitor_button, scanner_button, wifi_button, transfer_button]:
            button.setStyleSheet(button_style)
    
    def open_bandwidth_monitor(self):
        """Open bandwidth monitoring tool."""
        try:
            # Try to import and launch the actual tool
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'network_connectivity'))
            from gui.hub import NetworkConnectivityHub
            self.network_hub = NetworkConnectivityHub()
            self.network_hub._launch_tool("bandwidth_monitor")
            self.status_list.addItem("Launched bandwidth monitor")
        except Exception as e:
            QMessageBox.information(
                self, 
                "Bandwidth Monitor", 
                f"Bandwidth monitoring functionality will be implemented here.\n"
                f"This tool will provide real-time network speed monitoring.\n\n"
                f"Debug info: {str(e)}"
            )
    
    def open_port_scanner(self):
        """Open port scanner tool."""
        try:
            # Try to import and launch the actual tool
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'network_connectivity'))
            from gui.hub import NetworkConnectivityHub
            self.network_hub = NetworkConnectivityHub()
            self.network_hub._launch_tool("port_scanner")
            self.status_list.addItem("Launched port scanner")
        except Exception as e:
            QMessageBox.information(
                self, 
                "Port Scanner", 
                f"Port scanning functionality will be implemented here.\n"
                f"This tool will scan for open ports on network devices.\n\n"
                f"Debug info: {str(e)}"
            )
    
    def open_wifi_analyzer(self):
        """Open WiFi analyzer tool."""
        try:
            # Try to import and launch the actual tool
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'network_connectivity'))
            from gui.hub import NetworkConnectivityHub
            self.network_hub = NetworkConnectivityHub()
            self.network_hub._launch_tool("wifi_analyzer")
            self.status_list.addItem("Launched WiFi analyzer")
        except Exception as e:
            QMessageBox.information(
                self, 
                "WiFi Analyzer", 
                f"WiFi analysis functionality will be implemented here.\n"
                f"This tool will analyze wireless network signals and security.\n\n"
                f"Debug info: {str(e)}"
            )
    
    def open_file_transfer(self):
        """Open LAN file transfer tool."""
        try:
            # Try to import and launch the actual tool
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'network_connectivity'))
            from gui.hub import NetworkConnectivityHub
            self.network_hub = NetworkConnectivityHub()
            self.network_hub._launch_tool("lan_file_transfer")
            self.status_list.addItem("Launched LAN file transfer")
        except Exception as e:
            QMessageBox.information(
                self, 
                "LAN File Transfer", 
                f"LAN file transfer functionality will be implemented here.\n"
                f"This tool will enable secure file sharing over local network.\n\n"
                f"Debug info: {str(e)}"
            )


def main():
    """Main function for standalone execution."""
    app = QApplication(sys.argv)
    window = NetworkConnectivityGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
