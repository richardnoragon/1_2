"""Wi-Fi Signal Analyzer tool for comprehensive wireless network analysis."""

import time
import threading
import json
import csv
import subprocess
import re
import platform
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Set, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum
import logging

from ..core.network_base import (
    NetworkToolBase,
    NetworkOperationResult,
    NetworkAlertLevel,
)
from ..core.platform_network import (
    PlatformNetworkDetector,
    NetworkInterface,
    NetworkPlatform,
)
from ..core.security_validator import SecurityValidator, ValidationResult


class WiFiSecurityType(Enum):
    """Wi-Fi security protocol types."""

    OPEN = "Open"
    WEP = "WEP"
    WPA = "WPA"
    WPA2 = "WPA2"
    WPA3 = "WPA3"
    WPA_WPA2 = "WPA/WPA2"
    WPA2_WPA3 = "WPA2/WPA3"
    ENTERPRISE = "Enterprise"
    UNKNOWN = "Unknown"


class WiFiStandard(Enum):
    """Wi-Fi 802.11 standards."""

    LEGACY_A = "802.11a"
    LEGACY_B = "802.11b"
    LEGACY_G = "802.11g"
    N = "802.11n"
    AC = "802.11ac"
    AX = "802.11ax"
    BE = "802.11be"
    UNKNOWN = "Unknown"


class ChannelBand(Enum):
    """Wi-Fi frequency bands."""

    BAND_2_4GHZ = "2.4GHz"
    BAND_5GHZ = "5GHz"
    BAND_6GHZ = "6GHz"
    UNKNOWN = "Unknown"


class InterferenceType(Enum):
    """Types of wireless interference."""

    BLUETOOTH = "Bluetooth"
    MICROWAVE = "Microwave"
    CORDLESS_PHONE = "Cordless Phone"
    BABY_MONITOR = "Baby Monitor"
    WIRELESS_CAMERA = "Wireless Camera"
    CHANNEL_OVERLAP = "Channel Overlap"
    NON_WIFI = "Non-WiFi"
    UNKNOWN = "Unknown"


@dataclass
class AccessPoint:
    """Wi-Fi access point information."""

    ssid: str
    bssid: str
    signal_strength: int  # RSSI in dBm
    channel: int
    frequency: int  # MHz
    security: WiFiSecurityType
    standard: WiFiStandard
    band: ChannelBand
    vendor: Optional[str] = None
    capabilities: List[str] = None
    channel_width: Optional[int] = None  # MHz
    last_seen: Optional[datetime] = None
    beacon_interval: Optional[int] = None
    wps_enabled: bool = False
    hidden: bool = False

    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = []
        if self.last_seen is None:
            self.last_seen = datetime.now()


@dataclass
class SignalMeasurement:
    """Signal strength measurement data point."""

    timestamp: datetime
    interface_name: str
    connected_ssid: Optional[str]
    connected_bssid: Optional[str]
    rssi: int  # dBm
    snr: Optional[float] = None  # Signal-to-Noise Ratio
    noise_floor: Optional[int] = None  # dBm
    link_quality: Optional[float] = None  # 0.0 to 1.0
    tx_rate: Optional[float] = None  # Mbps
    rx_rate: Optional[float] = None  # Mbps
    channel: Optional[int] = None
    frequency: Optional[int] = None


@dataclass
class ChannelInfo:
    """Channel utilization and analysis information."""

    channel: int
    frequency: int
    band: ChannelBand
    utilization: float  # 0.0 to 1.0
    access_points: List[str]  # BSSIDs
    interference_level: float  # 0.0 to 1.0
    recommended: bool = False
    overlapping_channels: List[int] = None

    def __post_init__(self):
        if self.overlapping_channels is None:
            self.overlapping_channels = []


@dataclass
class InterferenceSource:
    """Detected interference source."""

    source_type: InterferenceType
    frequency: int  # MHz
    strength: float  # 0.0 to 1.0
    affected_channels: List[int]
    description: str
    timestamp: datetime
    confidence: float = 0.0  # 0.0 to 1.0


@dataclass
class SecurityAssessment:
    """Wi-Fi security assessment result."""

    ssid: str
    bssid: str
    security_score: float  # 0.0 to 1.0
    security_type: WiFiSecurityType
    vulnerabilities: List[str]
    recommendations: List[str]
    wps_vulnerable: bool = False
    encryption_strength: str = "Unknown"
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class WiFiAlert:
    """Wi-Fi specific alert information."""

    alert_type: str
    level: NetworkAlertLevel
    message: str
    timestamp: datetime
    interface_name: Optional[str] = None
    ssid: Optional[str] = None
    bssid: Optional[str] = None
    details: Dict[str, Any] = None

    def __post_init__(self):
        if self.details is None:
            self.details = {}


class OUIDatabase:
    """Organizationally Unique Identifier database for vendor lookup."""

    def __init__(self):
        """Initialize OUI database."""
        self.oui_map: Dict[str, str] = {}
        self._load_builtin_oui()

    def _load_builtin_oui(self):
        """Load built-in OUI mappings for common vendors."""
        # Common Wi-Fi equipment vendors
        self.oui_map.update(
            {
                # Intel
                "00:1B:21": "Intel",
                "00:13:02": "Intel",
                "00:15:00": "Intel",
                "00:16:EA": "Intel",
                "00:19:D1": "Intel",
                "00:1F:3A": "Intel",
                "00:21:6A": "Intel",
                "00:22:FB": "Intel",
                "00:24:D7": "Intel",
                "00:26:C6": "Intel",
                "00:27:10": "Intel",
                "04:CE:14": "Intel",
                "08:11:96": "Intel",
                "0C:8B:FD": "Intel",
                "34:13:E8": "Intel",
                "3C:A9:F4": "Intel",
                "7C:7A:91": "Intel",
                "84:3A:4B": "Intel",
                "9C:B6:D0": "Intel",
                "A0:A8:CD": "Intel",
                "B4:96:91": "Intel",
                "CC:46:D6": "Intel",
                "D0:7E:35": "Intel",
                "E0:94:67": "Intel",
                "F0:D5:BF": "Intel",
                "F4:06:69": "Intel",
                # Apple
                "00:03:93": "Apple",
                "00:0A:95": "Apple",
                "00:0D:93": "Apple",
                "00:11:24": "Apple",
                "00:14:51": "Apple",
                "00:16:CB": "Apple",
                "00:17:F2": "Apple",
                "00:19:E3": "Apple",
                "00:1B:63": "Apple",
                "00:1E:C2": "Apple",
                "00:21:E9": "Apple",
                "00:23:12": "Apple",
                "00:23:DF": "Apple",
                "00:25:00": "Apple",
                "00:25:4B": "Apple",
                "00:25:BC": "Apple",
                "00:26:08": "Apple",
                "00:26:4A": "Apple",
                "00:26:B0": "Apple",
                "00:26:BB": "Apple",
                "04:0C:CE": "Apple",
                "04:15:52": "Apple",
                "04:1E:64": "Apple",
                "04:54:53": "Apple",
                "04:69:F8": "Apple",
                "04:DB:56": "Apple",
                "04:E5:36": "Apple",
                "08:00:07": "Apple",
                "08:6D:41": "Apple",
                "0C:3E:9F": "Apple",
                "0C:4D:E9": "Apple",
                "0C:74:C2": "Apple",
                "10:40:F3": "Apple",
                "10:9A:DD": "Apple",
                "14:10:9F": "Apple",
                "14:20:5E": "Apple",
                "14:5A:05": "Apple",
                "14:7D:DA": "Apple",
                "14:BD:61": "Apple",
                "18:34:51": "Apple",
                "18:65:90": "Apple",
                "18:AF:61": "Apple",
                "18:E7:F4": "Apple",
                "1C:1A:C0": "Apple",
                "1C:36:BB": "Apple",
                "1C:AB:A7": "Apple",
                "20:78:F0": "Apple",
                "20:A2:E4": "Apple",
                "20:C9:D0": "Apple",
                "24:A0:74": "Apple",
                "24:AB:81": "Apple",
                "28:37:37": "Apple",
                "28:6A:BA": "Apple",
                "28:A0:2B": "Apple",
                "28:CF:DA": "Apple",
                "28:CF:E9": "Apple",
                "28:E0:2C": "Apple",
                "28:E7:CF": "Apple",
                "2C:1F:23": "Apple",
                "2C:36:F8": "Apple",
                "2C:B4:3A": "Apple",
                "30:90:AB": "Apple",
                "34:15:9E": "Apple",
                "34:36:3B": "Apple",
                "34:A3:95": "Apple",
                "34:C0:59": "Apple",
                "38:0F:4A": "Apple",
                "38:48:4C": "Apple",
                "38:89:DC": "Apple",
                "38:C9:86": "Apple",
                "3C:07:54": "Apple",
                "3C:15:C2": "Apple",
                "40:30:04": "Apple",
                "40:33:1A": "Apple",
                "40:A6:D9": "Apple",
                "40:B3:95": "Apple",
                "40:CB:C0": "Apple",
                "44:00:10": "Apple",
                "44:2A:60": "Apple",
                "44:4C:0C": "Apple",
                "44:D8:84": "Apple",
                "48:43:7C": "Apple",
                "48:60:BC": "Apple",
                "48:74:6E": "Apple",
                "48:A1:95": "Apple",
                "48:BF:6B": "Apple",
                "4C:32:75": "Apple",
                "4C:57:CA": "Apple",
                "4C:8D:79": "Apple",
                "4C:B1:99": "Apple",
                "50:EA:D6": "Apple",
                "54:26:96": "Apple",
                "54:72:4F": "Apple",
                "54:AE:27": "Apple",
                "54:E4:3A": "Apple",
                "58:55:CA": "Apple",
                "5C:59:48": "Apple",
                "5C:95:AE": "Apple",
                "5C:F9:38": "Apple",
                "60:03:08": "Apple",
                "60:33:4B": "Apple",
                "60:C5:47": "Apple",
                "60:F4:45": "Apple",
                "60:FA:CD": "Apple",
                "60:FB:42": "Apple",
                "64:20:9F": "Apple",
                "64:76:BA": "Apple",
                "64:A3:CB": "Apple",
                "64:B0:A6": "Apple",
                "64:E6:82": "Apple",
                "68:5B:35": "Apple",
                "68:96:7B": "Apple",
                "68:AB:1E": "Apple",
                "68:D9:3C": "Apple",
                "6C:19:8F": "Apple",
                "6C:40:08": "Apple",
                "6C:72:20": "Apple",
                "6C:94:66": "Apple",
                "6C:AD:F8": "Apple",
                "70:11:24": "Apple",
                "70:48:0F": "Apple",
                "70:56:81": "Apple",
                "70:73:CB": "Apple",
                "70:CD:60": "Apple",
                "70:DE:E2": "Apple",
                "74:E1:B6": "Apple",
                "74:E2:F5": "Apple",
                "78:31:C1": "Apple",
                "78:4F:43": "Apple",
                "78:67:D0": "Apple",
                "78:A3:E4": "Apple",
                "78:CA:39": "Apple",
                "7C:6D:62": "Apple",
                "7C:C3:A1": "Apple",
                "7C:D1:C3": "Apple",
                "7C:F0:5F": "Apple",
                "80:92:9F": "Apple",
                "80:BE:05": "Apple",
                "80:E6:50": "Apple",
                "84:38:35": "Apple",
                "84:85:06": "Apple",
                "84:FC:FE": "Apple",
                "88:1F:A1": "Apple",
                "88:53:2E": "Apple",
                "88:63:DF": "Apple",
                "88:66:5A": "Apple",
                "88:AE:1D": "Apple",
                "88:E9:FE": "Apple",
                "8C:2D:AA": "Apple",
                "8C:58:77": "Apple",
                "8C:7C:92": "Apple",
                "8C:85:90": "Apple",
                "8C:8E:F2": "Apple",
                "90:27:E4": "Apple",
                "90:72:40": "Apple",
                "90:84:0D": "Apple",
                "90:B0:ED": "Apple",
                "90:B2:1F": "Apple",
                "94:E6:F7": "Apple",
                "94:F6:A3": "Apple",
                "98:03:D8": "Apple",
                "98:5A:EB": "Apple",
                "98:B8:E3": "Apple",
                "98:FE:94": "Apple",
                "9C:04:EB": "Apple",
                "9C:20:7B": "Apple",
                "9C:29:3F": "Apple",
                "9C:84:BF": "Apple",
                "9C:F3:87": "Apple",
                "A0:99:9B": "Apple",
                "A0:D7:95": "Apple",
                "A4:5E:60": "Apple",
                "A4:83:E7": "Apple",
                "A4:B1:97": "Apple",
                "A4:C3:61": "Apple",
                "A8:20:66": "Apple",
                "A8:51:AB": "Apple",
                "A8:60:B6": "Apple",
                "A8:66:7F": "Apple",
                "A8:86:DD": "Apple",
                "A8:96:75": "Apple",
                "A8:BB:CF": "Apple",
                "A8:FA:D8": "Apple",
                "AC:1F:74": "Apple",
                "AC:29:3A": "Apple",
                "AC:3C:0B": "Apple",
                "AC:61:EA": "Apple",
                "AC:87:A3": "Apple",
                "AC:BC:32": "Apple",
                "AC:CF:85": "Apple",
                "B0:65:BD": "Apple",
                "B0:CA:68": "Apple",
                "B4:18:D1": "Apple",
                "B4:F0:AB": "Apple",
                "B4:F6:1C": "Apple",
                "B8:09:8A": "Apple",
                "B8:17:C2": "Apple",
                "B8:53:AC": "Apple",
                "B8:63:BC": "Apple",
                "B8:78:2E": "Apple",
                "B8:C7:5D": "Apple",
                "B8:E8:56": "Apple",
                "B8:F6:B1": "Apple",
                "BC:52:B7": "Apple",
                "BC:67:1C": "Apple",
                "BC:6C:21": "Apple",
                "BC:92:6B": "Apple",
                "BC:9F:EF": "Apple",
                "C0:84:7A": "Apple",
                "C0:CE:CD": "Apple",
                "C0:D0:12": "Apple",
                "C4:2C:03": "Apple",
                "C4:B3:01": "Apple",
                "C8:2A:14": "Apple",
                "C8:33:4B": "Apple",
                "C8:69:CD": "Apple",
                "C8:89:F3": "Apple",
                "C8:BC:C8": "Apple",
                "C8:E0:EB": "Apple",
                "C8:F6:50": "Apple",
                "CC:08:8D": "Apple",
                "CC:25:EF": "Apple",
                "CC:29:F5": "Apple",
                "CC:78:AB": "Apple",
                "D0:23:DB": "Apple",
                "D0:81:7A": "Apple",
                "D0:A6:37": "Apple",
                "D4:61:9D": "Apple",
                "D4:9A:20": "Apple",
                "D4:F4:6F": "Apple",
                "D8:30:62": "Apple",
                "D8:96:95": "Apple",
                "D8:A2:5E": "Apple",
                "D8:BB:2C": "Apple",
                "DC:2B:2A": "Apple",
                "DC:37:45": "Apple",
                "DC:56:E7": "Apple",
                "DC:86:D8": "Apple",
                "DC:A4:CA": "Apple",
                "DC:A9:04": "Apple",
                "DC:D3:21": "Apple",
                "E0:AC:CB": "Apple",
                "E0:B9:BA": "Apple",
                "E0:C9:7A": "Apple",
                "E0:F5:C6": "Apple",
                "E0:F8:47": "Apple",
                "E4:25:E7": "Apple",
                "E4:8B:7F": "Apple",
                "E4:B2:FB": "Apple",
                "E4:C6:3D": "Apple",
                "E4:CE:8F": "Apple",
                "E8:06:88": "Apple",
                "E8:80:2E": "Apple",
                "E8:B2:AC": "Apple",
                "EC:35:86": "Apple",
                "EC:89:14": "Apple",
                "F0:18:98": "Apple",
                "F0:2F:74": "Apple",
                "F0:99:BF": "Apple",
                "F0:B4:79": "Apple",
                "F0:C1:F1": "Apple",
                "F0:DB:E2": "Apple",
                "F0:DC:E2": "Apple",
                "F4:0F:24": "Apple",
                "F4:37:B7": "Apple",
                "F4:5C:89": "Apple",
                "F4:F1:5A": "Apple",
                "F4:F9:51": "Apple",
                "F8:0C:F3": "Apple",
                "F8:1E:DF": "Apple",
                "F8:27:93": "Apple",
                "F8:2F:A8": "Apple",
                "F8:4F:AD": "Apple",
                "F8:A9:D0": "Apple",
                "F8:FF:C2": "Apple",
                "FC:25:3F": "Apple",
                "FC:E9:98": "Apple",
                "FC:FC:48": "Apple",
                # Netgear
                "00:1A:A0": "Netgear",
                "00:09:5B": "Netgear",
                "00:0F:B5": "Netgear",
                "00:14:6C": "Netgear",
                "00:18:4D": "Netgear",
                "00:1B:2F": "Netgear",
                "00:1E:2A": "Netgear",
                "00:22:3F": "Netgear",
                "00:24:B2": "Netgear",
                "00:26:F2": "Netgear",
                "04:A1:51": "Netgear",
                "08:BD:43": "Netgear",
                "0C:80:63": "Netgear",
                "10:0D:7F": "Netgear",
                "20:4E:7F": "Netgear",
                "28:C6:8E": "Netgear",
                "2C:30:33": "Netgear",
                "30:46:9A": "Netgear",
                "32:46:9A": "Netgear",
                "44:94:FC": "Netgear",
                "4C:60:DE": "Netgear",
                "6C:B0:CE": "Netgear",
                "74:44:01": "Netgear",
                "84:1B:5E": "Netgear",
                "9C:1C:12": "Netgear",
                "A0:04:60": "Netgear",
                "A0:21:B7": "Netgear",
                "B0:7F:B9": "Netgear",
                "C0:3F:0E": "Netgear",
                "C4:04:15": "Netgear",
                "CC:40:D0": "Netgear",
                "E0:46:9A": "Netgear",
                "E0:91:F5": "Netgear",
                # Linksys
                "00:06:25": "Linksys",
                "00:0C:41": "Linksys",
                "00:0E:08": "Linksys",
                "00:12:17": "Linksys",
                "00:13:10": "Linksys",
                "00:14:BF": "Linksys",
                "00:16:B6": "Linksys",
                "00:18:39": "Linksys",
                "00:18:F8": "Linksys",
                "00:1A:70": "Linksys",
                "00:1C:10": "Linksys",
                "00:1D:7E": "Linksys",
                "00:1E:E5": "Linksys",
                "00:20:A6": "Linksys",
                "00:21:29": "Linksys",
                "00:22:6B": "Linksys",
                "00:23:69": "Linksys",
                "00:25:9C": "Linksys",
                "08:86:3B": "Linksys",
                "0C:54:A5": "Linksys",
                "10:BF:48": "Linksys",
                "14:91:82": "Linksys",
                "20:AA:4B": "Linksys",
                "24:F5:A2": "Linksys",
                "30:23:03": "Linksys",
                "48:F8:B3": "Linksys",
                "58:6D:8F": "Linksys",
                "60:38:E0": "Linksys",
                "68:7F:74": "Linksys",
                "94:10:3E": "Linksys",
                "98:01:A7": "Linksys",
                "C0:56:27": "Linksys",
                "C4:41:1E": "Linksys",
                "E4:F4:C6": "Linksys",
                # D-Link
                "00:07:7D": "D-Link",
                "00:0D:88": "D-Link",
                "00:0F:3D": "D-Link",
                "00:11:95": "D-Link",
                "00:13:46": "D-Link",
                "00:15:E9": "D-Link",
                "00:17:9A": "D-Link",
                "00:19:5B": "D-Link",
                "00:1B:11": "D-Link",
                "00:1C:F0": "D-Link",
                "00:1E:58": "D-Link",
                "00:21:91": "D-Link",
                "00:22:B0": "D-Link",
                "00:24:01": "D-Link",
                "00:26:5A": "D-Link",
                "14:D6:4D": "D-Link",
                "1C:7E:E5": "D-Link",
                "20:CF:30": "D-Link",
                "28:10:7B": "D-Link",
                "34:08:04": "D-Link",
                "40:61:86": "D-Link",
                "5C:D9:98": "D-Link",
                "78:54:2E": "D-Link",
                "84:C9:B2": "D-Link",
                "90:94:E4": "D-Link",
                "B8:A3:86": "D-Link",
                "C8:D3:A3": "D-Link",
                "CC:B2:55": "D-Link",
                "E4:6F:13": "D-Link",
                "F0:7D:68": "D-Link",
                # ASUS
                "00:1F:90": "ASUS",
                "00:22:15": "ASUS",
                "00:23:54": "ASUS",
                "00:24:8C": "ASUS",
                "00:26:18": "ASUS",
                "04:D4:C4": "ASUS",
                "08:60:6E": "ASUS",
                "0C:9D:92": "ASUS",
                "10:BF:48": "ASUS",
                "14:DD:A9": "ASUS",
                "1C:87:2C": "ASUS",
                "20:CF:30": "ASUS",
                "2C:56:DC": "ASUS",
                "30:5A:3A": "ASUS",
                "38:D5:47": "ASUS",
                "40:16:7E": "ASUS",
                "50:46:5D": "ASUS",
                "54:04:A6": "ASUS",
                "60:45:CB": "ASUS",
                "70:4D:7B": "ASUS",
                "74:D0:2B": "ASUS",
                "78:24:AF": "ASUS",
                "88:D7:F6": "ASUS",
                "9C:5C:8E": "ASUS",
                "AC:9E:17": "ASUS",
                "B0:6E:BF": "ASUS",
                "BC:EE:7B": "ASUS",
                "D0:17:C2": "ASUS",
                "E0:3F:49": "ASUS",
                "F4:6D:04": "ASUS",
                # TP-Link
                "00:90:4C": "TP-Link",
                "00:27:19": "TP-Link",
                "04:8D:38": "TP-Link",
                "0C:80:63": "TP-Link",
                "14:CC:20": "TP-Link",
                "18:A6:F7": "TP-Link",
                "1C:61:B4": "TP-Link",
                "20:F4:78": "TP-Link",
                "24:A4:3C": "TP-Link",
                "28:87:BA": "TP-Link",
                "2C:30:33": "TP-Link",
                "30:B5:C2": "TP-Link",
                "34:97:F6": "TP-Link",
                "38:BA:F8": "TP-Link",
                "3C:84:6A": "TP-Link",
                "40:ED:00": "TP-Link",
                "44:D9:E7": "TP-Link",
                "48:0E:EC": "TP-Link",
                "4C:ED:FB": "TP-Link",
                "50:C7:BF": "TP-Link",
                "54:AF:97": "TP-Link",
                "60:E3:27": "TP-Link",
                "64:70:02": "TP-Link",
                "68:FF:7B": "TP-Link",
                "6C:5A:B0": "TP-Link",
                "70:4F:57": "TP-Link",
                "74:DA:DA": "TP-Link",
                "78:8A:20": "TP-Link",
                "7C:8B:CA": "TP-Link",
                "80:EA:96": "TP-Link",
                "84:16:F9": "TP-Link",
                "88:25:2C": "TP-Link",
                "8C:A6:DF": "TP-Link",
                "90:F6:52": "TP-Link",
                "94:A6:7E": "TP-Link",
                "98:DA:C4": "TP-Link",
                "9C:A2:F4": "TP-Link",
                "A0:F3:C1": "TP-Link",
                "A4:2B:B0": "TP-Link",
                "A8:57:4E": "TP-Link",
                "AC:84:C6": "TP-Link",
                "B0:48:7A": "TP-Link",
                "B4:B0:24": "TP-Link",
                "B8:A3:86": "TP-Link",
                "BC:46:99": "TP-Link",
                "C0:25:E9": "TP-Link",
                "C4:E9:84": "TP-Link",
                "C8:0E:14": "TP-Link",
                "CC:32:E5": "TP-Link",
                "D0:76:E7": "TP-Link",
                "D4:6E:0E": "TP-Link",
                "D8:0D:17": "TP-Link",
                "DC:9F:DB": "TP-Link",
                "E0:28:6D": "TP-Link",
                "E4:95:6E": "TP-Link",
                "E8:DE:27": "TP-Link",
                "EC:08:6B": "TP-Link",
                "F0:2F:74": "TP-Link",
                "F4:28:53": "TP-Link",
                "F8:1A:67": "TP-Link",
                "FC:EC:DA": "TP-Link",
            }
        )

    def get_vendor(self, mac_address: str) -> Optional[str]:
        """Get vendor name from MAC address.

        Args:
            mac_address: MAC address in format XX:XX:XX:XX:XX:XX

            Vendor name or None if not found
        """
        if not mac_address:
            return None

        # Extract OUI (first 3 octets)
        oui = mac_address.upper()[:8]  # XX:XX:XX format
        return self.oui_map.get(oui)

    def add_vendor_mapping(self, oui: str, vendor: str):
        """Add custom vendor mapping.

        Args:
            oui: OUI in format XX:XX:XX
            vendor: Vendor name
        """
        self.oui_map[oui.upper()] = vendor


class WiFiChannelMap:
    """Wi-Fi channel to frequency mapping and utilities."""

    # 2.4GHz channels (1-14)
    CHANNELS_2_4GHZ = {
        1: 2412,
        2: 2417,
        3: 2422,
        4: 2427,
        5: 2432,
        6: 2437,
        7: 2442,
        8: 2447,
        9: 2452,
        10: 2457,
        11: 2462,
        12: 2467,
        13: 2472,
        14: 2484,
    }

    # 5GHz channels (36-165)
    CHANNELS_5GHZ = {
        36: 5180,
        40: 5200,
        44: 5220,
        48: 5240,
        52: 5260,
        56: 5280,
        60: 5300,
        64: 5320,
        100: 5500,
        104: 5520,
        108: 5540,
        112: 5560,
        116: 5580,
        120: 5600,
        124: 5620,
        128: 5640,
        132: 5660,
        136: 5680,
        140: 5700,
        144: 5720,
        149: 5745,
        153: 5765,
        157: 5785,
        161: 5805,
        165: 5825,
    }

    # 6GHz channels (1-233)
    CHANNELS_6GHZ = {
        1: 5955,
        5: 5975,
        9: 5995,
        13: 6015,
        17: 6035,
        21: 6055,
        25: 6075,
        29: 6095,
        33: 6115,
        37: 6135,
        41: 6155,
        45: 6175,
        49: 6195,
        53: 6215,
        57: 6235,
        61: 6255,
        65: 6275,
        69: 6295,
        73: 6315,
        77: 6335,
        81: 6355,
        85: 6375,
        89: 6395,
        93: 6415,
        97: 6435,
        101: 6455,
        105: 6475,
        109: 6495,
        113: 6515,
        117: 6535,
        121: 6555,
        125: 6575,
        129: 6595,
        133: 6615,
        137: 6635,
        141: 6655,
        145: 6675,
        149: 6695,
        153: 6715,
        157: 6735,
        161: 6755,
        165: 6775,
        169: 6795,
        173: 6815,
        177: 6835,
        181: 6855,
        185: 6875,
        189: 6895,
        193: 6915,
        197: 6935,
        201: 6955,
        205: 6975,
        209: 6995,
        213: 7015,
        217: 7035,
        221: 7055,
        225: 7075,
        229: 7095,
        233: 7115,
    }

    @classmethod
    def get_frequency(cls, channel: int) -> Optional[int]:
        """Get frequency for a channel.

        Args:
            channel: Channel number

        Returns:
            Frequency in MHz or None if not found
        """
        if channel in cls.CHANNELS_2_4GHZ:
            return cls.CHANNELS_2_4GHZ[channel]
        elif channel in cls.CHANNELS_5GHZ:
            return cls.CHANNELS_5GHZ[channel]
        elif channel in cls.CHANNELS_6GHZ:
            return cls.CHANNELS_6GHZ[channel]
        return None

    @classmethod
    def get_band(cls, channel: int) -> ChannelBand:
        """Get band for a channel.

        Args:
            channel: Channel number

        Returns:
            Channel band
        """
        if channel in cls.CHANNELS_2_4GHZ:
            return ChannelBand.BAND_2_4GHZ
        elif channel in cls.CHANNELS_5GHZ:
            return ChannelBand.BAND_5GHZ
        elif channel in cls.CHANNELS_6GHZ:
            return ChannelBand.BAND_6GHZ
        return ChannelBand.UNKNOWN

    @classmethod
    def get_channel_from_frequency(cls, frequency: int) -> Optional[int]:
        """Get channel number from frequency.

        Args:
            frequency: Frequency in MHz

        Returns:
            Channel number or None if not found
        """
        # Check 2.4GHz
        for channel, freq in cls.CHANNELS_2_4GHZ.items():
            if freq == frequency:
                return channel

        # Check 5GHz
        for channel, freq in cls.CHANNELS_5GHZ.items():
            if freq == frequency:
                return channel

        # Check 6GHz
        for channel, freq in cls.CHANNELS_6GHZ.items():
            if freq == frequency:
                return channel

        return None

    @classmethod
    def get_overlapping_channels(cls, channel: int) -> List[int]:
        """Get channels that overlap with the given channel.

        Args:
            channel: Channel number

        Returns:
            List of overlapping channel numbers
        """
        overlapping = []

        if channel in cls.CHANNELS_2_4GHZ:
            # 2.4GHz channels overlap significantly
            # Each channel overlaps with ±2 channels
            for ch in range(max(1, channel - 2), min(15, channel + 3)):
                if ch != channel and ch in cls.CHANNELS_2_4GHZ:
                    overlapping.append(ch)

        # 5GHz and 6GHz channels typically don't overlap
        # unless using wider channel widths

        return overlapping

    @classmethod
    def get_non_overlapping_channels(cls, band: ChannelBand) -> List[int]:
        """Get non-overlapping channels for a band.

        Args:
            band: Channel band

        Returns:
            List of non-overlapping channel numbers
        """
        if band == ChannelBand.BAND_2_4GHZ:
            # Standard non-overlapping channels in 2.4GHz
            return [1, 6, 11]
        elif band == ChannelBand.BAND_5GHZ:
            # Most 5GHz channels don't overlap with 20MHz width
            return list(cls.CHANNELS_5GHZ.keys())
        elif band == ChannelBand.BAND_6GHZ:
            # 6GHz channels don't overlap with 20MHz width
            return list(cls.CHANNELS_6GHZ.keys())

        return []


# Placeholder classes for components that will be implemented separately
class SignalMonitor:
    """Signal monitoring component placeholder."""

    def __init__(self, interface_name: str, platform_detector):
        self.interface_name = interface_name
        self.platform_detector = platform_detector
        self._monitoring_active = False

    def start_monitoring(self, interval: float) -> bool:
        self._monitoring_active = True
        return True

    def stop_monitoring(self) -> bool:
        self._monitoring_active = False
        return True

    def get_current_measurement(self) -> Optional[SignalMeasurement]:
        return None


class ChannelAnalyzer:
    """Channel analysis component placeholder."""

    def __init__(self, platform_detector):
        self.platform_detector = platform_detector

    def analyze_channels(
        self,
        access_points: List[AccessPoint],
        bands: Optional[List[ChannelBand]] = None,
    ) -> Dict[int, ChannelInfo]:
        return {}


class NetworkDiscovery:
    """Network discovery component placeholder."""

    def __init__(self, platform_detector, oui_database):
        self.platform_detector = platform_detector
        self.oui_database = oui_database

    def scan_networks(
        self,
        interface_name: str,
        scan_type: str = "active",
        bands: Optional[List[ChannelBand]] = None,
    ) -> List[AccessPoint]:
        return []


class InterferenceDetector:
    """Interference detection component placeholder."""

    def detect_interference(
        self,
        access_points: List[AccessPoint],
        channel_info: Dict[int, ChannelInfo],
    ) -> List[InterferenceSource]:
        return []


class SecurityAnalyzer:
    """Security analysis component placeholder."""

    def __init__(self, security_validator):
        self.security_validator = security_validator

    def assess_access_point(
        self, access_point: AccessPoint
    ) -> SecurityAssessment:
        return SecurityAssessment(
            ssid=access_point.ssid,
            bssid=access_point.bssid,
            security_score=0.5,
            security_type=access_point.security,
            vulnerabilities=[],
            recommendations=[],
        )


class WiFiDataManager:
    """Wi-Fi data management component placeholder."""

    def __init__(self, retention_hours: int = 24, max_entries: int = 1000):
        self.retention_hours = retention_hours
        self.max_entries = max_entries

    def add_access_point(self, access_point: AccessPoint):
        pass

    def add_security_assessment(self, assessment: SecurityAssessment):
        pass

    def add_interference_source(self, source: InterferenceSource):
        pass

    def export_data(
        self,
        file_path: str,
        format_type: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> bool:
        return True


class WiFiAnalyzer(NetworkToolBase):
    """Main Wi-Fi Signal Analyzer tool with comprehensive wireless analysis."""

    def __init__(self):
        """Initialize Wi-Fi analyzer."""
        super().__init__("WiFiAnalyzer")

        # Core components
        self.platform_detector = PlatformNetworkDetector()
        self.oui_database = OUIDatabase()
        self.security_validator = SecurityValidator()

        # Analysis components
        self.signal_monitors: Dict[str, SignalMonitor] = {}
        self.channel_analyzer: Optional[ChannelAnalyzer] = None
        self.network_discovery: Optional[NetworkDiscovery] = None
        self.interference_detector: Optional[InterferenceDetector] = None
        self.security_analyzer: Optional[SecurityAnalyzer] = None
        self.data_manager: Optional[WiFiDataManager] = None

        # Current data
        self.access_points: List[AccessPoint] = []
        self.channel_info: Dict[int, ChannelInfo] = {}
        self.interference_sources: List[InterferenceSource] = []
        self.security_assessments: List[SecurityAssessment] = []

        # Monitoring state
        self.wireless_interfaces: List[str] = []
        self._monitoring_active = False
        self._scan_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

        # Load configuration and initialize components
        self._load_configuration()
        self._initialize_components()

    def _load_configuration(self):
        """Load Wi-Fi analyzer configuration."""
        # Get scan intervals
        self.scan_interval = (
            self.get_tool_config("scan_interval", 30000) / 1000.0
        )  # Convert ms to seconds
        self.signal_interval = (
            self.get_tool_config("signal_interval", 2000) / 1000.0
        )

        # Get analysis settings
        self.enable_security_analysis = self.get_tool_config(
            "enable_security_analysis", True
        )
        self.enable_interference_detection = self.get_tool_config(
            "enable_interference_detection", True
        )
        self.enable_channel_analysis = self.get_tool_config(
            "enable_channel_analysis", True
        )

        # Get data retention settings
        self.data_retention_hours = self.get_tool_config(
            "data_retention_hours", 24
        )
        self.max_access_points = self.get_tool_config(
            "max_access_points", 1000
        )

        # Get alert settings
        self.enable_alerts = self.get_tool_config("enable_alerts", True)
        self.weak_signal_threshold = self.get_tool_config(
            "weak_signal_threshold", -70
        )
        self.security_alert_level = self.get_tool_config(
            "security_alert_level", "medium"
        )

    def _initialize_components(self):
        """Initialize analysis components."""
        try:
            # Initialize channel analyzer
            if self.enable_channel_analysis:
                self.channel_analyzer = ChannelAnalyzer(self.platform_detector)

            # Initialize network discovery
            self.network_discovery = NetworkDiscovery(
                self.platform_detector, self.oui_database
            )

            # Initialize interference detector
            if self.enable_interference_detection:
                self.interference_detector = InterferenceDetector()

            # Initialize security analyzer
            if self.enable_security_analysis:
                self.security_analyzer = SecurityAnalyzer(
                    self.security_validator
                )

            # Initialize data manager
            self.data_manager = WiFiDataManager(
                retention_hours=self.data_retention_hours,
                max_entries=self.max_access_points,
            )

            # Detect wireless interfaces
            self._detect_wireless_interfaces()

            self.logger.info(
                "Wi-Fi analyzer components initialized successfully"
            )

        except Exception as e:
            self.logger.error(
                f"Failed to initialize Wi-Fi analyzer components: {e}"
            )

    def _detect_wireless_interfaces(self):
        """Detect available wireless interfaces."""
        try:
            interfaces = self.platform_detector.get_network_interfaces()
            self.wireless_interfaces = [
                iface.name
                for iface in interfaces
                if iface.is_wireless and iface.is_active
            ]

            self.logger.info(
                f"Detected wireless interfaces: {self.wireless_interfaces}"
            )

        except Exception as e:
            self.logger.error(f"Error detecting wireless interfaces: {e}")
            self.wireless_interfaces = []

    def execute_operation(self, **kwargs) -> NetworkOperationResult:
        """Execute Wi-Fi analyzer operation.

        Args:
            **kwargs: Operation parameters
                - operation_type: 'start_analysis', 'stop_analysis', 'scan_networks',
                                'get_signal_strength', 'analyze_channels', 'assess_security'
                - interface_name: Wireless interface to use
                - scan_type: 'active', 'passive', 'both'
                - bands: List of bands to analyze

        Returns:
            NetworkOperationResult with operation results
        """
        operation_type = kwargs.get("operation_type", "scan_networks")

        try:
            if operation_type == "start_analysis":
                return self._start_analysis_operation(**kwargs)
            elif operation_type == "stop_analysis":
                return self._stop_analysis_operation()
            elif operation_type == "scan_networks":
                return self._scan_networks_operation(**kwargs)
            elif operation_type == "get_signal_strength":
                return self._get_signal_strength_operation(**kwargs)
            elif operation_type == "analyze_channels":
                return self._analyze_channels_operation(**kwargs)
            elif operation_type == "assess_security":
                return self._assess_security_operation(**kwargs)
            elif operation_type == "detect_interference":
                return self._detect_interference_operation(**kwargs)
            elif operation_type == "export_data":
                return self._export_data_operation(**kwargs)
            else:
                raise ValueError(f"Unknown operation type: {operation_type}")

        except Exception as e:
            return NetworkOperationResult(
                success=False,
                operation_type=operation_type,
                data={},
                error_message=str(e),
            )

    def _start_analysis_operation(self, **kwargs) -> NetworkOperationResult:
        """Start comprehensive Wi-Fi analysis."""
        interface_name = kwargs.get("interface_name")

        if not interface_name:
            if not self.wireless_interfaces:
                raise ValueError("No wireless interfaces available")
            interface_name = self.wireless_interfaces[0]

        if interface_name not in self.wireless_interfaces:
            raise ValueError(
                f"Interface {interface_name} is not a wireless interface"
            )

        # Start monitoring
        success = self.start_monitoring(interface_name)

        return NetworkOperationResult(
            success=success,
            operation_type="start_analysis",
            data={
                "interface_name": interface_name,
                "monitoring_active": self._monitoring_active,
                "scan_interval": self.scan_interval,
                "signal_interval": self.signal_interval,
                "components_enabled": {
                    "channel_analysis": self.enable_channel_analysis,
                    "security_analysis": self.enable_security_analysis,
                    "interference_detection": self.enable_interference_detection,
                },
            },
        )

    def _stop_analysis_operation(self) -> NetworkOperationResult:
        """Stop Wi-Fi analysis."""
        success = self.stop_monitoring()

        return NetworkOperationResult(
            success=success,
            operation_type="stop_analysis",
            data={
                "was_monitoring": not self._monitoring_active,
                "access_points_found": len(self.access_points),
                "channels_analyzed": len(self.channel_info),
                "interference_sources": len(self.interference_sources),
                "security_assessments": len(self.security_assessments),
            },
        )

    def _scan_networks_operation(self, **kwargs) -> NetworkOperationResult:
        """Scan for Wi-Fi networks."""
        interface_name = kwargs.get("interface_name")
        scan_type = kwargs.get("scan_type", "active")
        bands = kwargs.get(
            "bands", [ChannelBand.BAND_2_4GHZ, ChannelBand.BAND_5GHZ]
        )

        if not interface_name:
            if not self.wireless_interfaces:
                raise ValueError("No wireless interfaces available")
            interface_name = self.wireless_interfaces[0]

        # Perform network scan
        if self.network_discovery:
            access_points = self.network_discovery.scan_networks(
                interface_name, scan_type, bands
            )
            self.access_points = access_points

            # Store in data manager
            if self.data_manager:
                for ap in access_points:
                    self.data_manager.add_access_point(ap)
        else:
            access_points = []

        return NetworkOperationResult(
            success=True,
            operation_type="scan_networks",
            data={
                "interface_name": interface_name,
                "scan_type": scan_type,
                "bands": [band.value for band in bands],
                "access_points_found": len(access_points),
                "access_points": [asdict(ap) for ap in access_points],
                "timestamp": datetime.now().isoformat(),
            },
        )

    def _get_signal_strength_operation(
        self, **kwargs
    ) -> NetworkOperationResult:
        """Get current signal strength."""
        interface_name = kwargs.get("interface_name")

        if not interface_name:
            if not self.wireless_interfaces:
                raise ValueError("No wireless interfaces available")
            interface_name = self.wireless_interfaces[0]

        # Get signal monitor for interface
        if interface_name not in self.signal_monitors:
            self.signal_monitors[interface_name] = SignalMonitor(
                interface_name, self.platform_detector
            )

        monitor = self.signal_monitors[interface_name]
        measurement = monitor.get_current_measurement()

        return NetworkOperationResult(
            success=measurement is not None,
            operation_type="get_signal_strength",
            data={
                "interface_name": interface_name,
                "measurement": asdict(measurement) if measurement else None,
                "timestamp": datetime.now().isoformat(),
            },
        )

    def _analyze_channels_operation(self, **kwargs) -> NetworkOperationResult:
        """Analyze channel utilization."""
        bands = kwargs.get(
            "bands", [ChannelBand.BAND_2_4GHZ, ChannelBand.BAND_5GHZ]
        )

        if not self.channel_analyzer:
            raise ValueError("Channel analysis is not enabled")

        # Use current access points or scan if needed
        access_points = self.access_points
        if not access_points and self.network_discovery:
            interface_name = (
                self.wireless_interfaces[0]
                if self.wireless_interfaces
                else None
            )
            if interface_name:
                access_points = self.network_discovery.scan_networks(
                    interface_name, "active", bands
                )
                self.access_points = access_points

        # Analyze channels
        channel_info = self.channel_analyzer.analyze_channels(
            access_points, bands
        )
        self.channel_info = channel_info

        return NetworkOperationResult(
            success=True,
            operation_type="analyze_channels",
            data={
                "bands": [band.value for band in bands],
                "channels_analyzed": len(channel_info),
                "channel_info": {
                    str(ch): asdict(info) for ch, info in channel_info.items()
                },
                "recommended_channels": [
                    ch for ch, info in channel_info.items() if info.recommended
                ],
                "timestamp": datetime.now().isoformat(),
            },
        )

    def _assess_security_operation(self, **kwargs) -> NetworkOperationResult:
        """Assess Wi-Fi security."""
        if not self.security_analyzer:
            raise ValueError("Security analysis is not enabled")

        # Use current access points or scan if needed
        access_points = self.access_points
        if not access_points and self.network_discovery:
            interface_name = (
                self.wireless_interfaces[0]
                if self.wireless_interfaces
                else None
            )
            if interface_name:
                access_points = self.network_discovery.scan_networks(
                    interface_name, "active"
                )
                self.access_points = access_points

        # Assess security for each access point
        assessments = []
        for ap in access_points:
            assessment = self.security_analyzer.assess_access_point(ap)
            assessments.append(assessment)

        self.security_assessments = assessments

        # Store in data manager
        if self.data_manager:
            for assessment in assessments:
                self.data_manager.add_security_assessment(assessment)

        return NetworkOperationResult(
            success=True,
            operation_type="assess_security",
            data={
                "access_points_assessed": len(assessments),
                "security_assessments": [
                    asdict(assessment) for assessment in assessments
                ],
                "vulnerable_networks": [
                    asdict(assessment)
                    for assessment in assessments
                    if assessment.security_score < 0.5
                ],
                "timestamp": datetime.now().isoformat(),
            },
        )

    def _detect_interference_operation(
        self, **kwargs
    ) -> NetworkOperationResult:
        """Detect wireless interference."""
        if not self.interference_detector:
            raise ValueError("Interference detection is not enabled")

        # Use current access points and channel info
        access_points = self.access_points
        channel_info = self.channel_info

        # Detect interference
        interference_sources = self.interference_detector.detect_interference(
            access_points, channel_info
        )
        self.interference_sources = interference_sources

        # Store in data manager
        if self.data_manager:
            for source in interference_sources:
                self.data_manager.add_interference_source(source)

        return NetworkOperationResult(
            success=True,
            operation_type="detect_interference",
            data={
                "interference_sources_found": len(interference_sources),
                "interference_sources": [
                    asdict(source) for source in interference_sources
                ],
                "affected_channels": list(
                    set(
                        ch
                        for source in interference_sources
                        for ch in source.affected_channels
                    )
                ),
                "timestamp": datetime.now().isoformat(),
            },
        )

    def _export_data_operation(self, **kwargs) -> NetworkOperationResult:
        """Export Wi-Fi analysis data."""
        if not self.data_manager:
            raise ValueError("Data manager is not available")

        file_path = kwargs.get("file_path", "wifi_analysis.json")
        export_format = kwargs.get("format", "json").lower()
        start_time = kwargs.get("start_time")
        end_time = kwargs.get("end_time")

        # Export data
        success = self.data_manager.export_data(
            file_path, export_format, start_time, end_time
        )

        return NetworkOperationResult(
            success=success,
            operation_type="export_data",
            data={
                "file_path": file_path,
                "format": export_format,
                "exported": success,
                "timestamp": datetime.now().isoformat(),
            },
        )

    def start_monitoring(self, interface_name: str) -> bool:
        """Start comprehensive Wi-Fi monitoring.

        Args:
            interface_name: Wireless interface to monitor

        Returns:
            True if monitoring started successfully
        """
        if self._monitoring_active:
            self.logger.warning("Wi-Fi monitoring is already active")
            return False

        try:
            # Start signal monitoring
            if interface_name not in self.signal_monitors:
                self.signal_monitors[interface_name] = SignalMonitor(
                    interface_name, self.platform_detector
                )

            signal_monitor = self.signal_monitors[interface_name]
            signal_monitor.start_monitoring(self.signal_interval)

            # Start periodic scanning
            self._monitoring_active = True
            self._stop_event.clear()

            self._scan_thread = threading.Thread(
                target=self._monitoring_loop,
                args=(interface_name,),
                name="WiFiAnalyzerMonitoring",
                daemon=True,
            )
            self._scan_thread.start()

            self.logger.info(f"Started Wi-Fi monitoring on {interface_name}")
            self.status_changed.emit("Wi-Fi monitoring started")
            return True

        except Exception as e:
            self.logger.error(f"Failed to start Wi-Fi monitoring: {e}")
            self._monitoring_active = False
            return False

    def stop_monitoring(self) -> bool:
        """Stop Wi-Fi monitoring.

        Returns:
            True if monitoring stopped successfully
        """
        if not self._monitoring_active:
            return True

        try:
            self._monitoring_active = False
            self._stop_event.set()

            # Stop signal monitors
            for monitor in self.signal_monitors.values():
                monitor.stop_monitoring()

            # Wait for scan thread to finish
            if self._scan_thread and self._scan_thread.is_alive():
                self._scan_thread.join(timeout=10.0)

            self.logger.info("Stopped Wi-Fi monitoring")
            self.status_changed.emit("Wi-Fi monitoring stopped")
            return True

        except Exception as e:
            self.logger.error(f"Failed to stop Wi-Fi monitoring: {e}")
            return False

    def _monitoring_loop(self, interface_name: str):
        """Main monitoring loop.

        Args:
            interface_name: Interface to monitor
        """
        self.logger.debug("Starting Wi-Fi monitoring loop")

        while self._monitoring_active and not self._stop_event.is_set():
            try:
                # Perform network scan
                if self.network_discovery:
                    access_points = self.network_discovery.scan_networks(
                        interface_name, "active"
                    )
                    self.access_points = access_points

                    # Store access points
                    if self.data_manager:
                        for ap in access_points:
                            self.data_manager.add_access_point(ap)

                # Analyze channels
                if self.channel_analyzer and self.access_points:
                    channel_info = self.channel_analyzer.analyze_channels(
                        self.access_points
                    )
                    self.channel_info = channel_info

                # Detect interference
                if self.interference_detector and self.access_points:
                    interference_sources = (
                        self.interference_detector.detect_interference(
                            self.access_points, self.channel_info
                        )
                    )
                    self.interference_sources = interference_sources

                    # Store interference sources
                    if self.data_manager:
                        for source in interference_sources:
                            self.data_manager.add_interference_source(source)

                # Assess security
                if self.security_analyzer and self.access_points:
                    assessments = []
                    for ap in self.access_points:
                        assessment = (
                            self.security_analyzer.assess_access_point(ap)
                        )
                        assessments.append(assessment)

                    self.security_assessments = assessments

                    # Store security assessments
                    if self.data_manager:
                        for assessment in assessments:
                            self.data_manager.add_security_assessment(
                                assessment
                            )

                # Emit data update
                self._emit_analysis_update()

                # Check for alerts
                if self.enable_alerts:
                    self._check_alerts()

                # Wait for next scan
                self._stop_event.wait(self.scan_interval)

            except Exception as e:
                self.logger.error(f"Error in Wi-Fi monitoring loop: {e}")
                self._stop_event.wait(self.scan_interval)

        self.logger.debug("Wi-Fi monitoring loop stopped")

    def _emit_analysis_update(self):
        """Emit analysis data update."""
        data = {
            "access_points": len(self.access_points),
            "channels_analyzed": len(self.channel_info),
            "interference_sources": len(self.interference_sources),
            "security_assessments": len(self.security_assessments),
            "timestamp": datetime.now().isoformat(),
        }

        self.data_updated.emit(data)
        self._store_data(data)

    def _check_alerts(self):
        """Check for Wi-Fi alerts."""
        try:
            # Check for weak signals
            for interface_name, monitor in self.signal_monitors.items():
                measurement = monitor.get_current_measurement()
                if (
                    measurement
                    and measurement.rssi < self.weak_signal_threshold
                ):
                    self._trigger_alert(
                        "weak_signal",
                        NetworkAlertLevel.WARNING,
                        f"Weak signal on {interface_name}: {measurement.rssi} dBm",
                        interface_name=interface_name,
                        ssid=measurement.connected_ssid,
                    )

            # Check for security issues
            for assessment in self.security_assessments:
                if assessment.security_score < 0.3:
                    self._trigger_alert(
                        "security_risk",
                        NetworkAlertLevel.CRITICAL,
                        f"High security risk detected: {assessment.ssid}",
                        ssid=assessment.ssid,
                        bssid=assessment.bssid,
                    )
                elif assessment.security_score < 0.6:
                    self._trigger_alert(
                        "security_warning",
                        NetworkAlertLevel.WARNING,
                        f"Security warning: {assessment.ssid}",
                        ssid=assessment.ssid,
                        bssid=assessment.bssid,
                    )

            # Check for interference
            for source in self.interference_sources:
                if source.strength > 0.7:
                    self._trigger_alert(
                        "high_interference",
                        NetworkAlertLevel.WARNING,
                        f"High interference detected: {source.description}",
                        details={"source_type": source.source_type.value},
                    )

        except Exception as e:
            self.logger.error(f"Error checking Wi-Fi alerts: {e}")

    def _trigger_alert(
        self,
        alert_type: str,
        level: NetworkAlertLevel,
        message: str,
        interface_name: Optional[str] = None,
        ssid: Optional[str] = None,
        bssid: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Trigger a Wi-Fi alert.

        Args:
            alert_type: Type of alert
            level: Alert level
            message: Alert message
            interface_name: Interface name (optional)
            ssid: SSID (optional)
            bssid: BSSID (optional)
            details: Additional details (optional)
        """
        alert = WiFiAlert(
            alert_type=alert_type,
            level=level,
            message=message,
            timestamp=datetime.now(),
            interface_name=interface_name,
            ssid=ssid,
            bssid=bssid,
            details=details or {},
        )

        self.logger.warning(f"Wi-Fi alert: {alert.message}")

        # Emit alert signal
        self._notify_alert_callbacks(alert_type, level, message)

    def get_supported_protocols(self) -> List[str]:
        """Get list of supported protocols."""
        return [
            "802.11a",
            "802.11b",
            "802.11g",
            "802.11n",
            "802.11ac",
            "802.11ax",
        ]

    def validate_parameters(self, **kwargs) -> bool:
        """Validate operation parameters."""
        operation_type = kwargs.get("operation_type")

        if not operation_type:
            return False

        valid_operations = [
            "start_analysis",
            "stop_analysis",
            "scan_networks",
            "get_signal_strength",
            "analyze_channels",
            "assess_security",
            "detect_interference",
            "export_data",
        ]

        if operation_type not in valid_operations:
            return False

        # Validate interface name if provided
        interface_name = kwargs.get("interface_name")
        if interface_name and interface_name not in self.wireless_interfaces:
            return False

        return True

    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status."""
        return {
            "is_monitoring": self._monitoring_active,
            "wireless_interfaces": self.wireless_interfaces.copy(),
            "access_points_found": len(self.access_points),
            "channels_analyzed": len(self.channel_info),
            "interference_sources": len(self.interference_sources),
            "security_assessments": len(self.security_assessments),
            "platform_supported": self.platform_detector.is_supported(),
            "components_enabled": {
                "channel_analysis": self.enable_channel_analysis,
                "security_analysis": self.enable_security_analysis,
                "interference_detection": self.enable_interference_detection,
            },
            "scan_interval": self.scan_interval,
            "signal_interval": self.signal_interval,
            "capabilities": self.platform_detector.get_capabilities(),
        }

    def get_wireless_interfaces(self) -> List[str]:
        """Get list of available wireless interfaces.

        Returns:
            List of wireless interface names
        """
        return self.wireless_interfaces.copy()

    def get_access_points(
        self,
        ssid_filter: Optional[str] = None,
        security_filter: Optional[WiFiSecurityType] = None,
        band_filter: Optional[ChannelBand] = None,
    ) -> List[AccessPoint]:
        """Get detected access points with optional filtering.

        Args:
            ssid_filter: Filter by SSID (partial match)
            security_filter: Filter by security type
            band_filter: Filter by frequency band

        Returns:
            List of filtered access points
        """
        filtered_aps = self.access_points.copy()

        if ssid_filter:
            filtered_aps = [
                ap
                for ap in filtered_aps
                if ssid_filter.lower() in ap.ssid.lower()
            ]

        if security_filter:
            filtered_aps = [
                ap for ap in filtered_aps if ap.security == security_filter
            ]

        if band_filter:
            filtered_aps = [
                ap for ap in filtered_aps if ap.band == band_filter
            ]

        return filtered_aps

    def get_channel_recommendations(
        self, band: ChannelBand = ChannelBand.BAND_2_4GHZ
    ) -> List[int]:
        """Get recommended channels for a band.

        Args:
            band: Frequency band

        Returns:
            List of recommended channel numbers
        """
        if not self.channel_info:
            return WiFiChannelMap.get_non_overlapping_channels(band)

        # Get channels for the specified band
        band_channels = [
            ch for ch, info in self.channel_info.items() if info.band == band
        ]

        # Sort by utilization (lower is better)
        band_channels.sort(key=lambda ch: self.channel_info[ch].utilization)

        # Return top 3 least utilized channels
        return band_channels[:3]

    def get_security_summary(self) -> Dict[str, Any]:
        """Get security assessment summary.

        Returns:
            Dictionary with security summary
        """
        if not self.security_assessments:
            return {
                "total_networks": 0,
                "secure_networks": 0,
                "vulnerable_networks": 0,
                "open_networks": 0,
                "average_security_score": 0.0,
            }

        total = len(self.security_assessments)
        secure = len(
            [a for a in self.security_assessments if a.security_score >= 0.7]
        )
        vulnerable = len(
            [a for a in self.security_assessments if a.security_score < 0.5]
        )
        open_networks = len(
            [
                a
                for a in self.security_assessments
                if a.security_type == WiFiSecurityType.OPEN
            ]
        )

        avg_score = (
            sum(a.security_score for a in self.security_assessments) / total
        )

        return {
            "total_networks": total,
            "secure_networks": secure,
            "vulnerable_networks": vulnerable,
            "open_networks": open_networks,
            "average_security_score": avg_score,
        }

    def export_analysis_report(
        self,
        file_path: str,
        format_type: str = "json",
        include_raw_data: bool = False,
    ) -> bool:
        """Export comprehensive analysis report.

        Args:
            file_path: Output file path
            format_type: Export format ('json', 'csv', 'html')
            include_raw_data: Include raw measurement data

        Returns:
            True if export successful
        """
        try:
            report_data = {
                "timestamp": datetime.now().isoformat(),
                "wireless_interfaces": self.wireless_interfaces,
                "access_points": [asdict(ap) for ap in self.access_points],
                "channel_analysis": {
                    str(ch): asdict(info)
                    for ch, info in self.channel_info.items()
                },
                "security_summary": self.get_security_summary(),
                "interference_sources": [
                    asdict(source) for source in self.interference_sources
                ],
                "health_status": self.get_health_status(),
            }

            if include_raw_data and self.data_manager:
                # Add raw data if available
                pass  # Implementation would depend on data manager structure

            if format_type.lower() == "json":
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(report_data, f, indent=2, ensure_ascii=False)
            elif format_type.lower() == "csv":
                # Convert to CSV format
                with open(file_path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Type", "Data"])
                    writer.writerow(["Timestamp", report_data["timestamp"]])
                    writer.writerow(
                        ["Access Points", len(report_data["access_points"])]
                    )
                    writer.writerow(
                        [
                            "Channels Analyzed",
                            len(report_data["channel_analysis"]),
                        ]
                    )
                    # Add more CSV rows as needed
            else:
                return False

            return True

        except Exception as e:
            self.logger.error(f"Error exporting analysis report: {e}")
            return False
