"""T030 — UAPAppearanceWidget.

Embedded appearance settings panel used in SettingsDialog (T034) and
tabbed hub (T036).
"""

from __future__ import annotations

from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFontDatabase
from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


class UAPAppearanceWidget(QWidget):
    """Widget that exposes the full Unified Appearance Profile UI."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._svc = None  # lazy-loaded
        self._build_ui()
        self._connect_signals()
        self._load()

    def _get_svc(self):
        if self._svc is None:
            from src.core.preferences.uap.service import UAPService

            self._svc = UAPService()
        return self._svc

    def _build_ui(self) -> None:
        main = QVBoxLayout(self)

        # --- Mode ---
        mode_group = QGroupBox("Mode")
        mode_layout = QHBoxLayout(mode_group)
        self.radio_last_used = QRadioButton("Last Used")
        self.radio_predefined = QRadioButton("Predefined")
        self.radio_last_used.setChecked(True)
        self.radio_last_used.setAccessibleName("Use last used appearance profile")
        self.radio_predefined.setAccessibleName("Use predefined appearance profile")
        mode_layout.addWidget(self.radio_last_used)
        mode_layout.addWidget(self.radio_predefined)
        main.addWidget(mode_group)

        # --- Profile ---
        profile_group = QGroupBox("Profile")
        profile_layout = QHBoxLayout(profile_group)
        self.profile_combo = QComboBox()
        self.btn_new = QPushButton("New")
        self.btn_rename = QPushButton("Rename")
        self.btn_duplicate = QPushButton("Duplicate")
        self.btn_delete = QPushButton("Delete")
        self.btn_set_active = QPushButton("Set Active")
        self.profile_combo.setAccessibleName("Appearance profile selector")
        self.btn_new.setAccessibleName("Create new appearance profile")
        self.btn_rename.setAccessibleName("Rename appearance profile")
        self.btn_duplicate.setAccessibleName("Duplicate appearance profile")
        self.btn_delete.setAccessibleName("Delete appearance profile")
        self.btn_set_active.setAccessibleName("Set selected profile active")
        for w in (
            self.profile_combo,
            self.btn_new,
            self.btn_rename,
            self.btn_duplicate,
            self.btn_delete,
            self.btn_set_active,
        ):
            profile_layout.addWidget(w)
        main.addWidget(profile_group)

        # --- Geometry ---
        geom_group = QGroupBox("Window Geometry")
        geom_form = QFormLayout(geom_group)
        self.width_spin = QSpinBox()
        self.width_spin.setRange(400, 9999)
        self.width_spin.setAccessibleName("Window width")
        self.height_spin = QSpinBox()
        self.height_spin.setRange(300, 9999)
        self.height_spin.setAccessibleName("Window height")
        self.x_spin = QSpinBox()
        self.x_spin.setRange(-1, 9999)
        self.x_spin.setAccessibleName("Window X position")
        self.y_spin = QSpinBox()
        self.y_spin.setRange(-1, 9999)
        self.y_spin.setAccessibleName("Window Y position")
        self.default_placement_cb = QCheckBox("Use default placement (-1, -1)")
        self.default_placement_cb.setAccessibleName("Use default window placement")
        geom_form.addRow("Width:", self.width_spin)
        geom_form.addRow("Height:", self.height_spin)
        geom_form.addRow("X:", self.x_spin)
        geom_form.addRow("Y:", self.y_spin)
        geom_form.addRow("", self.default_placement_cb)
        main.addWidget(geom_group)

        # --- Font ---
        font_group = QGroupBox("Font")
        font_form = QFormLayout(font_group)
        self.font_family_combo = QComboBox()
        db = QFontDatabase()
        self.font_family_combo.addItems(db.families())
        self.font_family_combo.setAccessibleName("Font family selector")
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(14, 32)
        self.font_size_spin.setAccessibleName("Font size selector")
        font_form.addRow("Family:", self.font_family_combo)
        font_form.addRow("Size:", self.font_size_spin)
        main.addWidget(font_group)

        # --- Working Directory ---
        dir_group = QGroupBox("Working Directory")
        dir_layout = QHBoxLayout(dir_group)
        self.directory_edit = QLineEdit()
        self.directory_browse_btn = QPushButton("Browse…")
        self.directory_edit.setAccessibleName("Working directory path")
        self.directory_browse_btn.setAccessibleName("Browse for working directory")
        dir_layout.addWidget(self.directory_edit)
        dir_layout.addWidget(self.directory_browse_btn)
        main.addWidget(dir_group)

        # --- Apply ---
        self.apply_btn = QPushButton("Apply")
        self.apply_btn.setAccessibleName("Apply appearance settings")
        main.addWidget(self.apply_btn)
        main.addStretch()

    def _connect_signals(self) -> None:
        self.apply_btn.clicked.connect(self._on_apply)
        self.directory_browse_btn.clicked.connect(self._on_browse_directory)
        self.default_placement_cb.toggled.connect(self._on_default_placement_toggled)
        self.btn_new.clicked.connect(self._on_new_profile)
        self.btn_rename.clicked.connect(self._on_rename_profile)
        self.btn_duplicate.clicked.connect(self._on_duplicate_profile)
        self.btn_delete.clicked.connect(self._on_delete_profile)
        self.btn_set_active.clicked.connect(self._on_set_active_profile)
        self.radio_predefined.toggled.connect(self._on_mode_toggled)

    def _on_mode_toggled(self, checked: bool) -> None:
        enabled = self.radio_predefined.isChecked()
        for btn in (
            self.btn_rename,
            self.btn_duplicate,
            self.btn_delete,
            self.btn_set_active,
        ):
            btn.setEnabled(enabled)

    def _on_default_placement_toggled(self, checked: bool) -> None:
        self.x_spin.setEnabled(not checked)
        self.y_spin.setEnabled(not checked)
        if checked:
            self.x_spin.setValue(-1)
            self.y_spin.setValue(-1)

    def _on_browse_directory(self) -> None:
        current = self.directory_edit.text()
        chosen = QFileDialog.getExistingDirectory(
            self, "Select Working Directory", current or ""
        )
        if chosen:
            self.directory_edit.setText(chosen)

    def _load(self) -> None:
        try:
            svc = self._get_svc()
            s = svc._settings
            self.radio_last_used.setChecked(s.mode == "last_used")
            self.radio_predefined.setChecked(s.mode == "predefined")
            self.width_spin.setValue(s.last_used_width)
            self.height_spin.setValue(s.last_used_height)
            self.x_spin.setValue(s.last_used_x)
            self.y_spin.setValue(s.last_used_y)
            idx = self.font_family_combo.findText(s.last_used_font_family)
            if idx >= 0:
                self.font_family_combo.setCurrentIndex(idx)
            self.font_size_spin.setValue(s.last_used_font_size)
            self.directory_edit.setText(s.last_used_directory)
            self.default_placement_cb.setChecked(
                s.last_used_x == -1 and s.last_used_y == -1
            )
            self._refresh_profile_combo()
        except Exception:
            pass

    def _refresh_profile_combo(self) -> None:
        self.profile_combo.clear()
        try:
            svc = self._get_svc()
            for p in svc.list_profiles():
                self.profile_combo.addItem(p.profile_name, p.profile_id)
        except Exception:
            pass

    def _on_apply(self) -> None:
        svc = self._get_svc()
        mode = "predefined" if self.radio_predefined.isChecked() else "last_used"
        svc._settings.mode = mode
        svc.store.set(svc.user_id, "uap", "mode", mode)

        use_default = self.default_placement_cb.isChecked()
        x = -1 if use_default else self.x_spin.value()
        y = -1 if use_default else self.y_spin.value()

        family = self.font_family_combo.currentText()
        size = self.font_size_spin.value()

        svc.set_geometry(
            self.width_spin.value(),
            self.height_spin.value(),
            x,
            y,
        )
        svc.set_font(family, size)
        svc.set_directory(self.directory_edit.text())

    def _on_new_profile(self) -> None:
        from PyQt5.QtWidgets import QInputDialog

        name, ok = QInputDialog.getText(self, "New Profile", "Profile name:")
        if ok and name.strip():
            self._get_svc().create_profile(name.strip())
            self._refresh_profile_combo()

    def _on_rename_profile(self) -> None:
        from PyQt5.QtWidgets import QInputDialog

        profile_id = self.profile_combo.currentData()
        if not profile_id:
            return
        name, ok = QInputDialog.getText(self, "Rename Profile", "New name:")
        if ok and name.strip():
            self._get_svc().rename_profile(profile_id, name.strip())
            self._refresh_profile_combo()

    def _on_duplicate_profile(self) -> None:
        from PyQt5.QtWidgets import QInputDialog

        profile_id = self.profile_combo.currentData()
        if not profile_id:
            return
        name, ok = QInputDialog.getText(self, "Duplicate Profile", "New profile name:")
        if ok and name.strip():
            self._get_svc().duplicate_profile(profile_id, name.strip())
            self._refresh_profile_combo()

    def _on_delete_profile(self) -> None:
        profile_id = self.profile_combo.currentData()
        if not profile_id:
            return
        try:
            self._get_svc().delete_profile(profile_id)
        except ValueError as exc:
            QMessageBox.warning(self, "Cannot Delete Profile", str(exc))
        self._refresh_profile_combo()

    def _on_set_active_profile(self) -> None:
        profile_id = self.profile_combo.currentData()
        if not profile_id:
            return
        self._get_svc().set_active_profile(profile_id)
