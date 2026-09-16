"""Evidence-oriented hub view of declared tool capabilities and health."""

import json
from pathlib import Path

from PyQt5.QtWidgets import QDialog, QLabel, QTreeWidget, QTreeWidgetItem, QVBoxLayout

from src.core.tool_manifest import ToolManifestRegistry
from src.rfu import font_tokens
from src.rfu.localization import service, tr
from src.gui.components import SecondaryButton


class CapabilityDialog(QDialog):
    def __init__(self, hub):
        super().__init__(hub)
        self.hub = hub
        service.bind(self, "setWindowTitle", "Capabilities.TITLE")
        service.bind(self, "setAccessibleName", "Capabilities.TITLE")
        self.resize(980, 520)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        intro = QLabel()
        service.bind(intro, "setText", "Capabilities.DESCRIPTION")
        intro.setWordWrap(True)
        font_tokens.bind(intro)
        layout.addWidget(intro)
        self.table = QTreeWidget()
        service.bind(self.table, "setAccessibleName", "Capabilities.TABLE")
        font_tokens.bind(self.table)
        layout.addWidget(self.table)
        refresh = SecondaryButton(tr("Capabilities.REFRESH"))
        service.bind(refresh, "setText", "Capabilities.REFRESH")
        refresh.clicked.connect(self.refresh)
        layout.addWidget(refresh)
        self.refresh()
        service.subscribe(self, "refresh")

    def refresh(self):
        self.table.setHeaderLabels(tr("Capabilities.HEADERS").split("|"))
        root = Path(__file__).resolve().parents[2]
        try:
            matrix = json.loads((root / "docs/tool-capability-matrix.json").read_text())
            # Match actual entry points rather than inconsistent historical IDs.
            by_entry = {(row["module_path"], row["class_name"]): row for row in matrix["tools"]}
        except (OSError, ValueError, KeyError):
            by_entry = {}
        manager = getattr(self.hub, "menu_manager", None)
        windows = list(getattr(manager, "_tool_windows", {}).values())
        tracker = getattr(self.hub, "tool_lifecycle", None)
        self.table.clear()
        for entry in ToolManifestRegistry.builtins():
            declaration = by_entry.get((entry.module_path, entry.class_name), {})
            evidence = declaration.get("compliance", {}) if declaration.get("last_reviewed") else {}
            badges = [tr("Capabilities.VERIFIED") if evidence.get(code) is True else tr("Capabilities.NOT_APPLICABLE") if code in evidence and evidence[code] is None else tr("Capabilities.UNVERIFIED")
                      for code in ("DR", "CE", "A11Y", "PERF")]
            module = root.joinpath(*entry.module_path.split("."))
            exists = module.with_suffix(".py").is_file() or (module / "__init__.py").is_file()
            health = tr("Capabilities.UNKNOWN")
            for window in windows:
                if getattr(window, "tool_id", None) == entry.tool_id:
                    registry = getattr(window, "menu_registry", None)
                    if registry is not None:
                        status = registry.guardian.get_component_status(getattr(window, "tool_guardian_id", registry.guardian_id))
                        health = status.get("state", tr("Capabilities.UNKNOWN"))
            runtime = tracker.snapshot(entry.display_name) if tracker is not None else None
            undo = tr("Capabilities.UNVERIFIED") if entry.undo_supported is None else tr("Capabilities.SUPPORTED") if entry.undo_supported else tr("Capabilities.UNSUPPORTED")
            self.table.addTopLevelItem(QTreeWidgetItem([
                entry.display_name, tr("Capabilities.PRESENT") if exists else tr("Capabilities.MISSING"), *badges,
                undo, health, runtime.get("last_activity", "—") if runtime else "—"]))
        for index in range(self.table.columnCount()):
            self.table.resizeColumnToContents(index)
