"""Network interface selector component."""

from typing import List, Optional, Dict, Any
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
    QGroupBox,
)
from PyQt5.QtCore import Qt, pyqtSignal

from gui.themes import ThemeManager, Spacing

try:
    from ..core.platform_network import PlatformNetworkDetector, NetworkInterface
except ModuleNotFoundError:  # pragma: no cover - relative import fallback
    from src.tools.network.network_connectivity_complex.core.platform_network import (
        PlatformNetworkDetector,
        NetworkInterface,
    )


class NetworkInterfaceSelector(QWidget):
    """Widget for selecting network interfaces."""

    # Signals
    interface_selected = pyqtSignal(str)  # interface_name
    interface_changed = pyqtSignal(str)  # interface_name
    refresh_requested = pyqtSignal()

    def __init__(self, interface_type: str = "all", parent=None):
        """Initialize network interface selector.

        Args:
            interface_type: Type of interfaces to show
                          ('all', 'wireless', 'ethernet', 'active')
            parent: Parent widget
        """
        super().__init__(parent)
        self.interface_type = interface_type
        self.platform_detector = PlatformNetworkDetector()
        self.interfaces: List[NetworkInterface] = []

        self._setup_ui()
        self._connect_signals()
        self.refresh_interfaces()

    def _setup_ui(self):
        """Setup selector UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(Spacing.MEDIUM_SPACING)

        # Group box
        self.group_box = QGroupBox("Network Interface")
        ThemeManager.style_group_box(self.group_box)
        layout.addWidget(self.group_box)

        group_layout = QVBoxLayout(self.group_box)
        group_layout.setSpacing(Spacing.SMALL_SPACING)

        # Interface selection layout
        selection_layout = QHBoxLayout()

        # Interface combo box
        self.interface_combo = QComboBox()
        ThemeManager.style_input_field(self.interface_combo)
        self.interface_combo.setMinimumWidth(200)
        selection_layout.addWidget(self.interface_combo)

        # Refresh button
        self.refresh_button = QPushButton("Refresh")
        ThemeManager.style_secondary_button(self.refresh_button)
        self.refresh_button.setMaximumWidth(80)
        selection_layout.addWidget(self.refresh_button)

        group_layout.addLayout(selection_layout)

        # Interface details
        self.details_layout = QVBoxLayout()
        self.details_layout.setSpacing(Spacing.SMALL_SPACING)

        # Status label
        self.status_label = QLabel("No interface selected")
        ThemeManager.style_label(self.status_label)
        self.details_layout.addWidget(self.status_label)

        # IP address label
        self.ip_label = QLabel("")
        ThemeManager.style_label(self.ip_label)
        self.details_layout.addWidget(self.ip_label)

        # Type label
        self.type_label = QLabel("")
        ThemeManager.style_label(self.type_label)
        self.details_layout.addWidget(self.type_label)

        group_layout.addLayout(self.details_layout)

    def _connect_signals(self):
        """Connect widget signals."""
        self.interface_combo.currentTextChanged.connect(
            self._on_interface_changed
        )
        self.refresh_button.clicked.connect(self._on_refresh_clicked)

    def _on_interface_changed(self, interface_name: str):
        """Handle interface selection change.

        Args:
            interface_name: Selected interface name
        """
        if interface_name:
            self._update_interface_details(interface_name)
            self.interface_changed.emit(interface_name)
            self.interface_selected.emit(interface_name)

    def _on_refresh_clicked(self):
        """Handle refresh button click."""
        self.refresh_interfaces()
        self.refresh_requested.emit()

    def refresh_interfaces(self):
        """Refresh available network interfaces."""
        try:
            # Get all interfaces
            all_interfaces = self.platform_detector.get_network_interfaces()

            # Filter based on type
            filtered_interfaces = self._filter_interfaces(all_interfaces)

            # Update combo box
            current_selection = self.interface_combo.currentText()
            self.interface_combo.clear()

            self.interfaces = filtered_interfaces

            if not filtered_interfaces:
                self.interface_combo.addItem("No interfaces available")
                self.interface_combo.setEnabled(False)
                self._update_status("No interfaces available")
                return

            self.interface_combo.setEnabled(True)

            # Add interfaces to combo box
            for interface in filtered_interfaces:
                display_name = self._get_interface_display_name(interface)
                self.interface_combo.addItem(display_name, interface.name)

            # Restore selection if possible
            if current_selection:
                index = self.interface_combo.findText(current_selection)
                if index >= 0:
                    self.interface_combo.setCurrentIndex(index)
                else:
                    self.interface_combo.setCurrentIndex(0)
            else:
                self.interface_combo.setCurrentIndex(0)

            self._update_status(f"Found {len(filtered_interfaces)} interfaces")

        except Exception as e:
            self.interface_combo.clear()
            self.interface_combo.addItem("Error loading interfaces")
            self.interface_combo.setEnabled(False)
            self._update_status(f"Error: {e}")

    def _filter_interfaces(
        self, interfaces: List[NetworkInterface]
    ) -> List[NetworkInterface]:
        """Filter interfaces based on type.

        Args:
            interfaces: List of all interfaces

        Returns:
            Filtered list of interfaces
        """
        if self.interface_type == "all":
            return interfaces
        elif self.interface_type == "wireless":
            return [iface for iface in interfaces if iface.is_wireless]
        elif self.interface_type == "ethernet":
            return [iface for iface in interfaces if not iface.is_wireless]
        elif self.interface_type == "active":
            return [iface for iface in interfaces if iface.is_active]
        else:
            return interfaces

    def _get_interface_display_name(self, interface: NetworkInterface) -> str:
        """Get display name for interface.

        Args:
            interface: Network interface

        Returns:
            Display name
        """
        name = interface.name

        # Add type indicator
        if interface.is_wireless:
            name += " (Wi-Fi)"
        else:
            name += " (Ethernet)"

        # Add status indicator
        if not interface.is_active:
            name += " [Inactive]"

        return name

    def _update_interface_details(self, interface_name: str):
        """Update interface details display.

        Args:
            interface_name: Interface name
        """
        # Find interface
        interface = None
        for iface in self.interfaces:
            if iface.name == interface_name:
                interface = iface
                break

        if not interface:
            self._update_status("Interface not found")
            self.ip_label.setText("")
            self.type_label.setText("")
            return

        # Update details
        status = "Active" if interface.is_active else "Inactive"
        self.status_label.setText(f"Status: {status}")

        if interface.ip_address:
            self.ip_label.setText(f"IP: {interface.ip_address}")
        else:
            self.ip_label.setText("IP: Not assigned")

        interface_type = "Wireless" if interface.is_wireless else "Ethernet"
        self.type_label.setText(f"Type: {interface_type}")

    def _update_status(self, status: str):
        """Update status display.

        Args:
            status: Status message
        """
        self.status_label.setText(status)
        self.ip_label.setText("")
        self.type_label.setText("")

    def get_selected_interface(self) -> Optional[str]:
        """Get currently selected interface name.

        Returns:
            Interface name or None if no selection
        """
        if self.interface_combo.isEnabled():
            return self.interface_combo.currentData()
        return None

    def set_selected_interface(self, interface_name: str) -> bool:
        """Set selected interface.

        Args:
            interface_name: Interface name to select

        Returns:
            True if interface was found and selected
        """
        for i in range(self.interface_combo.count()):
            if self.interface_combo.itemData(i) == interface_name:
                self.interface_combo.setCurrentIndex(i)
                return True
        return False

    def get_interface_details(self) -> Optional[Dict[str, Any]]:
        """Get details of selected interface.

        Returns:
            Interface details dictionary or None
        """
        interface_name = self.get_selected_interface()
        if not interface_name:
            return None

        for interface in self.interfaces:
            if interface.name == interface_name:
                return {
                    "name": interface.name,
                    "display_name": interface.display_name,
                    "is_active": interface.is_active,
                    "is_wireless": interface.is_wireless,
                    "ip_address": interface.ip_address,
                    "mac_address": interface.mac_address,
                    "speed": interface.speed,
                    "mtu": interface.mtu,
                }

        return None

    def set_interface_type(self, interface_type: str):
        """Set interface type filter.

        Args:
            interface_type: Interface type filter
        """
        if interface_type != self.interface_type:
            self.interface_type = interface_type
            self.refresh_interfaces()
