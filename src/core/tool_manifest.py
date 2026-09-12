"""Tool Manifest — declares tool identity and minimum geometry constraints.

ToolManifestEntry contains only tool-authored declarations (e.g. min_window_width,
min_window_height).  User-state fields (window_x, window_y) MUST NOT appear here
— those belong exclusively in AppearanceProfile / UAPSettings.  (I2)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


def _normalize_tool_key(value: str) -> str:
    """Normalize a tool label for manifest lookup."""

    return "".join(ch for ch in value.lower().strip() if ch.isalnum())


@dataclass
class ToolManifestEntry:
    """Metadata for a registered tool.

    Attributes:
        tool_id:           Unique kebab-case identifier, e.g. "duplicate-finder".
        display_name:      Human-readable label shown in the hub.
        module_path:       Dotted import path, e.g. "src.tools.analysis.duplicate_finder".
        class_name:        Class to instantiate, e.g. "DuplicateFinderApp".
        category:          Logical grouping key, e.g. "analysis".
        min_window_width:  Minimum width enforced by UAPService.apply().  Default 400.
        min_window_height: Minimum height enforced by UAPService.apply().  Default 300.
        tool_version:      Optional semver string.
        uap_exempt:        When True the tool is excluded from UAP apply/audit.
        headless_incompatible: When True the tool cannot be instantiated headlessly.
        headless_reason:   One-line reason why the tool is headless-incompatible.
    """

    tool_id: str
    display_name: str
    module_path: str
    class_name: str
    category: str
    min_window_width: int = 400
    min_window_height: int = 300
    tool_version: Optional[str] = None
    uap_exempt: bool = False
    headless_incompatible: bool = False
    headless_reason: Optional[str] = None


class ToolManifestRegistry:
    """Registry of all known tools.

    T041 MUST NOT seed, mutate, or add entries to this registry.
    T041 MUST fail if ``all()`` returns fewer than two entries.
    """

    _entries: Dict[str, ToolManifestEntry] = {}

    @classmethod
    def register(cls, entry: ToolManifestEntry) -> None:
        """Register a tool entry.  Overwrites an existing entry with the same tool_id."""
        cls._entries[entry.tool_id] = entry

    @classmethod
    def get(cls, tool_id: str) -> Optional[ToolManifestEntry]:
        """Return the entry for *tool_id*, or None if not found."""
        return cls._entries.get(tool_id)

    @classmethod
    def lookup(cls, tool_name: str) -> Optional[ToolManifestEntry]:
        """Find an entry by tool_id or human-readable display name."""

        normalized = _normalize_tool_key(tool_name)
        for entry in cls._entries.values():
            if normalized == _normalize_tool_key(entry.tool_id):
                return entry
            if normalized == _normalize_tool_key(entry.display_name):
                return entry
        return None

    @classmethod
    def all(cls) -> List[ToolManifestEntry]:
        """Return a snapshot list of all registered entries."""
        return list(cls._entries.values())

    @classmethod
    def clear(cls) -> None:
        """Remove all entries.  Use only in tests."""
        cls._entries.clear()


# ---------------------------------------------------------------------------
# Seed entries — canonical baseline used by T041 audit and T007 contract tests
# ---------------------------------------------------------------------------
ToolManifestRegistry.register(
    ToolManifestEntry(
        tool_id="tool.alpha",
        display_name="Alpha Tool",
        module_path="src.tools.alpha",
        class_name="AlphaGUI",
        category="analysis",
        min_window_width=480,
        min_window_height=320,
    )
)

ToolManifestRegistry.register(
    ToolManifestEntry(
        tool_id="tool.beta",
        display_name="Beta Tool",
        module_path="src.tools.beta",
        class_name="BetaGUI",
        category="analysis",
        min_window_width=600,
        min_window_height=400,
    )
)

# Real tool metadata gathered from hub launcher entry points.
ToolManifestRegistry.register(
    ToolManifestEntry(
        tool_id="size-analyzer",
        display_name="Size Analyzer",
        module_path="src.tools.analysis.size_analyzer.size_analyzer",
        class_name="SizeAnalyzerGUI",
        category="analysis",
    )
)
ToolManifestRegistry.register(
    ToolManifestEntry(
        tool_id="empty-folders-finder",
        display_name="Empty Folders Finder",
        module_path="src.tools.analysis.empty_folders.empty_folders",
        class_name="EmptyFoldersGUI",
        category="analysis",
    )
)
ToolManifestRegistry.register(
    ToolManifestEntry(
        tool_id="checksum-calculator",
        display_name="Checksum Calculator",
        module_path="src.tools.analysis.checksum.check_sum",
        class_name="ChecksumGUI",
        category="analysis",
    )
)
ToolManifestRegistry.register(
    ToolManifestEntry(
        tool_id="synchronization-backup",
        display_name="Synchronization & Backup",
        module_path="src.tools.file_management.synchronization_backup.sync",
        class_name="SyncWindow",
        category="file_management",
    )
)
ToolManifestRegistry.register(
    ToolManifestEntry(
        tool_id="advanced-folders",
        display_name="Advanced Folders",
        module_path="src.tools.file_management.advanced_folders.ui.advanced_folders_widget",
        class_name="AdvancedFoldersGUI",
        category="file_management",
    )
)
ToolManifestRegistry.register(
    ToolManifestEntry(
        tool_id="file-organizer",
        display_name="File Organizer",
        module_path="src.tools.file_management.organizer.organize",
        class_name="OrganizeWindow",
        category="file_management",
    )
)
ToolManifestRegistry.register(
    ToolManifestEntry(
        tool_id="batch-rename",
        display_name="Batch Rename",
        module_path="src.tools.file_operations.rename.rename",
        class_name="RenameWindow",
        category="file_operations",
    )
)
ToolManifestRegistry.register(
    ToolManifestEntry(
        tool_id="network-tools",
        display_name="Network Tools",
        module_path="src.tools.network.gui",
        class_name="NetworkToolsWindow",
        category="network",
    )
)
ToolManifestRegistry.register(
    ToolManifestEntry(
        tool_id="privacy-tools",
        display_name="Privacy Tools",
        module_path="src.tools.privacy.privacy_tools.gui.privacy_hub",
        class_name="PrivacyToolsHub",
        category="privacy",
    )
)
ToolManifestRegistry.register(
    ToolManifestEntry(
        tool_id="security-scanner",
        display_name="Security Scanner",
        module_path="src.tools.security.security_scanner.security_scanner",
        class_name="SimpleSecurityScannerGUI",
        category="security",
    )
)
ToolManifestRegistry.register(
    ToolManifestEntry(
        tool_id="system-information",
        display_name="System Information",
        module_path="src.tools.system.simple_system_info",
        class_name="SimpleSystemInfoGUI",
        category="system",
    )
)
ToolManifestRegistry.register(
    ToolManifestEntry(
        tool_id="process-monitor",
        display_name="Process Monitor",
        module_path="src.tools.system.process_monitor.process_monitor",
        class_name="ProcessMonitorGUI",
        category="system",
    )
)
ToolManifestRegistry.register(
    ToolManifestEntry(
        tool_id="system-cleanup",
        display_name="System Cleanup",
        module_path="src.tools.system.system_cleanup.system_cleanup_gui",
        class_name="SystemCleanupGUI",
        category="system",
    )
)
ToolManifestRegistry.register(
    ToolManifestEntry(
        tool_id="file-finder",
        display_name="File Finder",
        module_path="src.tools.file_management.finder.file_finder",
        class_name="FileFinderWindow",
        category="file_management",
    )
)
ToolManifestRegistry.register(
    ToolManifestEntry(
        tool_id="advanced-catalog-generator",
        display_name="Advanced Catalog Generator",
        module_path="src.tools.file_management.advanced_catalog.advanced_catalog_window",
        class_name="AdvancedCatalogWindow",
        category="file_management",
    )
)
ToolManifestRegistry.register(
    ToolManifestEntry(
        tool_id="system-diagnostics",
        display_name="System Diagnostics",
        module_path="src.tools.system.system_diagnostics.system_diagnostics_gui",
        class_name="SystemDiagnosticsGUI",
        category="system",
    )
)
ToolManifestRegistry.register(
    ToolManifestEntry(
        tool_id="software-maintenance",
        display_name="Software Maintenance",
        module_path="src.tools.system.software_maintenance.gui.maintenance_hub",
        class_name="SoftwareMaintenanceHub",
        category="system",
    )
)
ToolManifestRegistry.register(
    ToolManifestEntry(
        tool_id="preference-portability",
        display_name="Preference Portability",
        module_path="src.tools.preferences.portability_launcher",
        class_name="PreferencePortabilityGUI",
        category="preferences",
    )
)
ToolManifestRegistry.register(
    ToolManifestEntry(
        tool_id="file-touch",
        display_name="File Touch",
        module_path="src.tools.metadata.file_touch.file_touch",
        class_name="FileTouchWindow",
        category="metadata",
    )
)
ToolManifestRegistry.register(
    ToolManifestEntry(
        tool_id="file-splitter",
        display_name="File Splitter",
        module_path="src.tools.file_operations.file_splitter.gui",
        class_name="FileSplitJoinGUI",
        category="file_operations",
    )
)
ToolManifestRegistry.register(
    ToolManifestEntry(
        tool_id="secure-delete",
        display_name="Secure Delete",
        module_path="src.tools.file_operations.secure_delete.secure_delete",
        class_name="SecureDeleteGUI",
        category="file_operations",
    )
)
ToolManifestRegistry.register(
    ToolManifestEntry(
        tool_id="compression-tools",
        display_name="Compression Tools",
        module_path="src.tools.file_operations.compression.compress_decompress",
        class_name="CompressDecompressApp",
        category="file_operations",
    )
)
ToolManifestRegistry.register(
    ToolManifestEntry(
        tool_id="duplicate-finder",
        display_name="Duplicate Finder",
        module_path="src.tools.analysis.duplicate_finder.find_duplicate_files",
        class_name="DuplicateFinderApp",
        category="analysis",
    )
)
ToolManifestRegistry.register(
    ToolManifestEntry(
        tool_id="image-metadata-editor",
        display_name="Image Metadata Editor",
        module_path="src.tools.metadata.image_metadata.gui",
        class_name="ImageMetadataEditorGUI",
        category="metadata",
    )
)
ToolManifestRegistry.register(
    ToolManifestEntry(
        tool_id="office-metadata-tools",
        display_name="Office Metadata Tools",
        module_path="src.tools.metadata.office_metadata.office_metadata_gui",
        class_name="OfficeMetadataGUI",
        category="metadata",
    )
)
ToolManifestRegistry.register(
    ToolManifestEntry(
        tool_id="pdf-tools",
        display_name="PDF Tools",
        module_path="src.tools.pdf_tools.widgets.enhanced_pdf_tools_widget",
        class_name="EnhancedPDFToolsWidget",
        category="pdf",
    )
)
ToolManifestRegistry.register(
    ToolManifestEntry(
        tool_id="network-transfer",
        display_name="Network Transfer",
        module_path="src.tools.network.transfer.network_transfer",
        class_name="NetworkTransferGUI",
        category="network",
    )
)
ToolManifestRegistry.register(
    ToolManifestEntry(
        tool_id="network-scanner",
        display_name="Network Scanner",
        module_path="src.tools.network.scanner.network_scanner",
        class_name="NetworkScannerGUI",
        category="network",
    )
)
ToolManifestRegistry.register(
    ToolManifestEntry(
        tool_id="port-scanner",
        display_name="Port Scanner",
        module_path="src.utilities.network.port_scanner",
        class_name="PortScannerGUI",
        category="network",
    )
)
ToolManifestRegistry.register(
    ToolManifestEntry(
        tool_id="network-monitor",
        display_name="Network Monitor",
        module_path="src.utilities.network.network_monitor",
        class_name="NetworkMonitorGUI",
        category="network",
    )
)
ToolManifestRegistry.register(
    ToolManifestEntry(
        tool_id="bandwidth-test",
        display_name="Bandwidth Test",
        module_path="src.utilities.network.bandwidth_test",
        class_name="BandwidthTestGUI",
        category="network",
    )
)
ToolManifestRegistry.register(
    ToolManifestEntry(
        tool_id="wake-on-lan",
        display_name="Wake on LAN",
        module_path="src.utilities.network.wake_on_lan",
        class_name="WakeOnLANGUI",
        category="network",
    )
)
ToolManifestRegistry.register(
    ToolManifestEntry(
        tool_id="encrypt-decrypt",
        display_name="Encrypt / Decrypt",
        module_path="src.tools.security.encryption.en_and_decrypt",
        class_name="EnAndDecryptGUI",
        category="security",
    )
)
ToolManifestRegistry.register(
    ToolManifestEntry(
        tool_id="hash-calculator",
        display_name="Hash Calculator",
        module_path="src.utilities.security.hash_calculator",
        class_name="HashCalculatorGUI",
        category="security",
    )
)
ToolManifestRegistry.register(
    ToolManifestEntry(
        tool_id="password-generator",
        display_name="Password Generator",
        module_path="src.tools.security.password_generator.password_generator",
        class_name="SimplePasswordGeneratorGUI",
        category="security",
    )
)
ToolManifestRegistry.register(
    ToolManifestEntry(
        tool_id="security-preferences",
        display_name="Security Preferences",
        module_path="src.tools.security.security_preferences",
        class_name="SecurityPreferencesGUI",
        category="security",
    )
)
ToolManifestRegistry.register(
    ToolManifestEntry(
        tool_id="key-manager",
        display_name="Key Manager",
        module_path="src.utilities.security.key_manager",
        class_name="KeyManagerGUI",
        category="security",
    )
)
ToolManifestRegistry.register(
    ToolManifestEntry(
        tool_id="secure-notes",
        display_name="Secure Notes",
        module_path="src.utilities.security.secure_notes",
        class_name="SecureNotesGUI",
        category="security",
    )
)
ToolManifestRegistry.register(
    ToolManifestEntry(
        tool_id="clipboard-manager",
        display_name="Clipboard Manager",
        module_path="src.utilities.system.clipboard_manager",
        class_name="ClipboardManagerGUI",
        category="system",
    )
)
ToolManifestRegistry.register(
    ToolManifestEntry(
        tool_id="system-monitor",
        display_name="System Monitor",
        module_path="src.utilities.system.system_monitor",
        class_name="SystemMonitorGUI",
        category="system",
    )
)
ToolManifestRegistry.register(
    ToolManifestEntry(
        tool_id="registry-tools",
        display_name="Registry Tools",
        module_path="src.utilities.system.registry_tools",
        class_name="RegistryToolsGUI",
        category="system",
    )
)
ToolManifestRegistry.register(
    ToolManifestEntry(
        tool_id="disk-tools",
        display_name="Disk Tools",
        module_path="src.utilities.system.disk_tools",
        class_name="DiskToolsGUI",
        category="system",
    )
)
ToolManifestRegistry.register(
    ToolManifestEntry(
        tool_id="process-manager",
        display_name="Process Manager",
        module_path="src.utilities.system.process_manager",
        class_name="ProcessManagerGUI",
        category="system",
    )
)
ToolManifestRegistry.register(
    ToolManifestEntry(
        tool_id="service-manager",
        display_name="Service Manager",
        module_path="src.utilities.system.service_manager",
        class_name="ServiceManagerGUI",
        category="system",
    )
)
