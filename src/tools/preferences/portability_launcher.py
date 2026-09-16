"""GUI front-end for preference portability operations."""

from __future__ import annotations
from src.rfu.localization import localized_widget as _ui_widget, bind_literal as _ui_bind

import logging
from pathlib import Path
from typing import Optional, Sequence

try:
    from PyQt5.QtWidgets import (
        QCheckBox,
        QFileDialog,
        QFormLayout,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QMainWindow,
        QMessageBox,
        QPushButton,
        QTabWidget,
        QVBoxLayout,
        QWidget,
    )

    from src.gui.themes import ThemeManager, token
except ImportError as exc:  # pragma: no cover - GUI dependency
    raise RuntimeError("PyQt5 is required for Preference Portability GUI") from exc

from src.core.preferences.portability import (
    AES_AVAILABLE,
    PreferencePortabilityError,
    export_preferences,
    import_preferences,
)
from src.log_manager import get_log_manager

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
    from src.rfu.ui_strings import PreferencePortability as _PrefPortStrings
except ImportError:

    class _PrefPortStrings:  # type: ignore[no-redef]
        TITLE = "Preference Portability"
        WINDOW_TITLE = "Preference Portability — RFU"
        LOADING = "Loading Preference Portability…"
        MODAL_ERROR_TITLE = "Preference Portability"
        ERR_INIT_FAILED = (
            "Could not start Preference Portability. "
            "Please try again or restart the application."
        )
        ERR_EXPORT_FAILED = "Could not export preferences. Please try again."
        ERR_IMPORT_FAILED = "Could not import preferences. Please try again."


# ---------------------------------------------------------------------------
# ERR: Modal import (graceful no-op when modal absent)
# ---------------------------------------------------------------------------
try:
    from src.gui.components.buttons import PrimaryButton, SecondaryButton
    from src.gui.components.modal import Modal
    from src.gui.components.toast import ToastNotification

    _CP_AVAILABLE = True
except ImportError:
    Modal = None  # type: ignore[assignment,misc]
    PrimaryButton = SecondaryButton = None  # type: ignore[assignment,misc]
    ToastNotification = None
    _CP_AVAILABLE = False


class PreferencePortabilityGUI(QMainWindow):
    """Simple interface for exporting and importing preference payloads."""

    def __init__(self, hub_instance=None, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._hub = hub_instance
        self.logger = get_log_manager().get_logger("PreferencePortabilityGUI")
        self._logger = self.logger  # harmonization alias
        self.setWindowTitle(_PrefPortStrings.WINDOW_TITLE)
        self.resize(640, 520)

        # Widget references initialised for static analysis linting.
        # GUI elements initialised during tab construction.
        self.export_user_edit: QLineEdit
        self.export_dest_edit: QLineEdit
        self.export_categories_edit: QLineEdit
        self.export_skip_encrypted: QCheckBox
        self.export_encrypt: QCheckBox
        self.export_passphrase_edit: QLineEdit
        self.export_button: QPushButton
        self.import_source_edit: QLineEdit
        self.import_target_user_edit: QLineEdit
        self.import_allow_overwrite: QCheckBox
        self.import_decrypt: QCheckBox
        self.import_passphrase_edit: QLineEdit
        self.import_button: QPushButton

        self._init_ui()
        status_bar = self.statusBar()
        if status_bar is not None:
            status_bar.showMessage("Ready")
        register_gui_component(
            self,
            tool_id="preference_portability",
            recovery_callback=self.degraded_fallback,
        )
        _emit_telemetry("ui_view_load", tool_id="preference_portability")
        ThemeManager.add_theme_changed_callback(self._on_theme_changed)

    def _on_theme_changed(self, variant: str) -> None:
        """Re-apply token-based stylesheets when the active theme variant changes."""
        pass  # stylesheets applied at init; live re-apply deferred (TH-4c/4d)

    def health_check(self) -> bool:
        """Return True if core UI is functional (GRD-3a)."""
        try:
            return hasattr(self, "tabs") and self.tabs is not None
        except Exception:
            return False

    def degraded_fallback(self) -> None:
        """Enter degraded / read-only state (GRD-3b)."""
        try:
            self._logger.warning("PreferencePortabilityGUI entering degraded mode")
        except Exception:
            pass
        _emit_telemetry(
            "ui_error_event",
            tool_id="preference_portability",
            error_type="degraded",
        )

    def _init_ui(self) -> None:
        central = QWidget(self)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        header = _ui_widget(QLabel, 'Legacy.s741b066f43a3ad35', 'setText')
        header.setWordWrap(True)
        layout.addWidget(header)

        self.tabs = QTabWidget()
        _ui_bind(self.tabs, 'setAccessibleName', 'Legacy.s748a664d59760434')
        layout.addWidget(self.tabs)

        self._build_export_tab()
        self._build_import_tab()

        self.setCentralWidget(central)

    def _build_export_tab(self) -> None:
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.setSpacing(10)

        form = QFormLayout()

        self.export_user_edit = QLineEdit()
        _ui_bind(self.export_user_edit, 'setAccessibleName', 'Legacy.s034c7004f4ec44f7')
        _ui_bind(self.export_user_edit, 'setPlaceholderText', 'Legacy.sc33b8b47c4c81c61')
        form.addRow("User ID", self.export_user_edit)

        self.export_dest_edit = QLineEdit()
        _ui_bind(self.export_dest_edit, 'setAccessibleName', 'Legacy.se4423cbe8e495daf')
        _ui_bind(self.export_dest_edit, 'setPlaceholderText', 'Legacy.s7b3b565a2609e3c2')
        _SB = SecondaryButton if SecondaryButton else QPushButton
        dest_button = _SB("Browse…")
        dest_button.clicked.connect(self._browse_export_destination)
        dest_row = self._wrap_with_row(self.export_dest_edit, dest_button)
        form.addRow("Destination", dest_row)

        self.export_categories_edit = QLineEdit()
        _ui_bind(self.export_categories_edit, 'setAccessibleName', 'Legacy.s38d57fecbc138352')
        _ui_bind(self.export_categories_edit, 'setPlaceholderText', 'Legacy.sea67ae230c8318fe')
        form.addRow("Categories", self.export_categories_edit)

        self.export_skip_encrypted = _ui_widget(QCheckBox, 'Legacy.sc373c3f7d4d8fa46', 'setText')
        _ui_bind(self.export_skip_encrypted, 'setAccessibleName', 'Legacy.sc373c3f7d4d8fa46')
        _ui_bind(self.export_skip_encrypted, 'setAccessibleDescription', 'Legacy.s1823bf192cbea9e0')
        self.export_skip_encrypted.setMinimumHeight(44)
        form.addRow("Encrypted", self.export_skip_encrypted)

        self.export_encrypt = _ui_widget(QCheckBox, 'Legacy.sf0a296dfca6bb3c1', 'setText')
        _ui_bind(self.export_encrypt, 'setAccessibleName', 'Legacy.sf0a296dfca6bb3c1')
        _ui_bind(self.export_encrypt, 'setAccessibleDescription', 'Legacy.s1052038660a67c07')
        self.export_encrypt.setMinimumHeight(44)
        self.export_encrypt.toggled.connect(self._on_export_encrypt_toggled)
        if not AES_AVAILABLE:
            self.export_encrypt.setEnabled(False)
            _ui_bind(self.export_encrypt, 'setToolTip', 'Legacy.sedc0697dfc725d75')
        form.addRow("Encryption", self.export_encrypt)

        self.export_passphrase_edit = QLineEdit()
        _ui_bind(self.export_passphrase_edit, 'setAccessibleName', 'Legacy.s6a1eb28c568d938b')
        _ui_bind(self.export_passphrase_edit, 'setAccessibleDescription', 'Legacy.s8b5f86bd9a4d3b0c')
        self.export_passphrase_edit.setEchoMode(QLineEdit.Password)
        self.export_passphrase_edit.setEnabled(False)
        form.addRow("Passphrase", self.export_passphrase_edit)

        tab_layout.addLayout(form)

        _PB = PrimaryButton if PrimaryButton else QPushButton
        self.export_button = _PB("Export Preferences")
        self.export_button.clicked.connect(self._handle_export)
        button_row = QHBoxLayout()
        button_row.addStretch(1)
        button_row.addWidget(self.export_button)
        tab_layout.addLayout(button_row)
        tab_layout.addStretch(1)

        if not AES_AVAILABLE:
            warning = _ui_widget(QLabel, 'Legacy.s975556f605d060c4', 'setText')
            warning.setStyleSheet(f"color: {token('semantic_warning')};")
            warning.setWordWrap(True)
            tab_layout.addWidget(warning)

        self.tabs.addTab(tab, "Export")

    def _build_import_tab(self) -> None:
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.setSpacing(10)

        form = QFormLayout()

        self.import_source_edit = QLineEdit()
        _ui_bind(self.import_source_edit, 'setAccessibleName', 'Legacy.saedb82f10406682d')
        _ui_bind(self.import_source_edit, 'setPlaceholderText', 'Legacy.sc32207e16ea296dc')
        _SB2 = SecondaryButton if SecondaryButton else QPushButton
        source_button = _SB2("Browse…")
        source_button.clicked.connect(self._browse_import_source)
        source_row = self._wrap_with_row(
            self.import_source_edit,
            source_button,
        )
        form.addRow("Source", source_row)

        self.import_target_user_edit = QLineEdit()
        _ui_bind(self.import_target_user_edit, 'setAccessibleName', 'Legacy.s2961f1b67e487a08')
        _ui_bind(self.import_target_user_edit, 'setPlaceholderText', 'Legacy.s85a6068979d2a6e2')
        form.addRow("Target User", self.import_target_user_edit)

        self.import_allow_overwrite = _ui_widget(QCheckBox, 'Legacy.sbaa451f19f4d9007', 'setText')
        _ui_bind(self.import_allow_overwrite, 'setAccessibleName', 'Legacy.sbaa451f19f4d9007')
        _ui_bind(self.import_allow_overwrite, 'setAccessibleDescription', 'Legacy.sc882caceacea5d49')
        self.import_allow_overwrite.setMinimumHeight(44)
        form.addRow("Overwrite", self.import_allow_overwrite)

        self.import_decrypt = _ui_widget(QCheckBox, 'Legacy.s18ea3db2651726c0', 'setText')
        _ui_bind(self.import_decrypt, 'setAccessibleName', 'Legacy.s18ea3db2651726c0')
        _ui_bind(self.import_decrypt, 'setAccessibleDescription', 'Legacy.s71258f317fcc0cb7')
        self.import_decrypt.setMinimumHeight(44)
        self.import_decrypt.toggled.connect(self._on_import_decrypt_toggled)
        if not AES_AVAILABLE:
            self.import_decrypt.setEnabled(False)
            _ui_bind(self.import_decrypt, 'setToolTip', 'Legacy.s27af6bcaa6238928')
        form.addRow("Decryption", self.import_decrypt)

        self.import_passphrase_edit = QLineEdit()
        _ui_bind(self.import_passphrase_edit, 'setAccessibleName', 'Legacy.s16b0f98bfb32173d')
        _ui_bind(self.import_passphrase_edit, 'setAccessibleDescription', 'Legacy.s86a511f92d78268b')
        self.import_passphrase_edit.setEchoMode(QLineEdit.Password)
        self.import_passphrase_edit.setEnabled(False)
        form.addRow("Passphrase", self.import_passphrase_edit)

        tab_layout.addLayout(form)

        _PB2 = PrimaryButton if PrimaryButton else QPushButton
        self.import_button = _PB2("Import Preferences")
        self.import_button.clicked.connect(self._handle_import)
        button_row = QHBoxLayout()
        button_row.addStretch(1)
        button_row.addWidget(self.import_button)
        tab_layout.addLayout(button_row)
        tab_layout.addStretch(1)

        if not AES_AVAILABLE:
            warning = _ui_widget(QLabel, 'Legacy.sfb4f4e73bcb2bb43', 'setText')
            warning.setStyleSheet(f"color: {token('semantic_warning')};")
            warning.setWordWrap(True)
            tab_layout.addWidget(warning)

        self.tabs.addTab(tab, "Import")

    def _wrap_with_row(self, *widgets: QWidget) -> QWidget:
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(6)
        for widget in widgets:
            row_layout.addWidget(widget)
        return row_widget

    def _on_export_encrypt_toggled(self, checked: bool) -> None:
        if checked and not AES_AVAILABLE:
            if Modal:
                Modal(
                    "Encryption Unavailable",
                    "Install pyAesCrypt to enable encrypted exports.",
                    ["OK"],
                    self,
                ).exec_()
            else:
                QMessageBox.warning(
                    self,
                    "Encryption Unavailable",
                    "Install pyAesCrypt to enable encrypted exports.",
                )
            self.export_encrypt.setChecked(False)
            return
        self.export_passphrase_edit.setEnabled(checked)
        if not checked:
            self.export_passphrase_edit.clear()

    def _on_import_decrypt_toggled(self, checked: bool) -> None:
        if checked and not AES_AVAILABLE:
            if Modal:
                Modal(
                    "Decryption Unavailable",
                    "Install pyAesCrypt to enable encrypted imports.",
                    ["OK"],
                    self,
                ).exec_()
            else:
                QMessageBox.warning(
                    self,
                    "Decryption Unavailable",
                    "Install pyAesCrypt to enable encrypted imports.",
                )
            self.import_decrypt.setChecked(False)
            return
        self.import_passphrase_edit.setEnabled(checked)
        if not checked:
            self.import_passphrase_edit.clear()

    def _browse_export_destination(self) -> None:
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Destination",
        )
        if directory:
            self.export_dest_edit.setText(directory)

    def _browse_import_source(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Preferences Export",
            filter=("Preference Exports (*.json *.json.aes *.aes);;" "All Files (*)"),
        )
        if file_path:
            self.import_source_edit.setText(file_path)

    def _handle_export(self) -> None:
        user_id = self.export_user_edit.text().strip()
        if not user_id:
            if Modal:
                Modal(
                    "Missing Information", "User ID is required.", ["OK"], self
                ).exec_()
            else:
                QMessageBox.warning(self, "Missing Information", "User ID is required.")
            return

        destination_text = self.export_dest_edit.text().strip()
        destination = Path(destination_text) if destination_text else None

        categories = self._parse_categories(self.export_categories_edit.text())
        skip_encrypted = self.export_skip_encrypted.isChecked()

        encrypt = self.export_encrypt.isChecked()
        passphrase = self.export_passphrase_edit.text() if encrypt else None
        if encrypt and not passphrase:
            if Modal:
                Modal(
                    "Missing Passphrase",
                    "Enter a passphrase when encryption is enabled.",
                    ["OK"],
                    self,
                ).exec_()
            else:
                QMessageBox.warning(
                    self,
                    "Missing Passphrase",
                    "Enter a passphrase when encryption is enabled.",
                )
            return

        self.logger.info(
            "preference_portability_gui_export_requested user_id=%s "
            "encrypt=%s skip_encrypted=%s destination=%s categories=%s",
            user_id,
            encrypt,
            skip_encrypted,
            str(destination) if destination else "<auto>",
            categories or [],
        )

        try:
            export_path = export_preferences(
                user_id,
                destination=destination,
                categories=categories,
                include_encrypted=not skip_encrypted,
                passphrase=passphrase,
            )
        except (
            PreferencePortabilityError
        ) as exc:  # ERR: non-fatal — surfaced via Modal; export failed
            self.logger.error("Export failed: %s", exc, exc_info=True)
            if Modal:
                Modal(
                    _PrefPortStrings.MODAL_ERROR_TITLE,
                    _PrefPortStrings.ERR_EXPORT_FAILED,
                    ["OK"],
                    self,
                ).exec_()
            return
        except (
            ValueError,
            OSError,
        ) as exc:  # ERR: non-fatal — surfaced via Modal; unexpected export failure  # pragma: no cover - defensive
            self.logger.error(
                "Unexpected export failure: %s",
                exc,
                exc_info=True,
            )
            if Modal:
                Modal(
                    _PrefPortStrings.MODAL_ERROR_TITLE,
                    _PrefPortStrings.ERR_EXPORT_FAILED,
                    ["OK"],
                    self,
                ).exec_()
            return

        status_bar = self.statusBar()
        if status_bar is not None:
            status_bar.showMessage(f"Export completed: {export_path}", 5000)
        if ToastNotification:
            ToastNotification(parent=self).show_message(
                f"Preferences exported to: {export_path}", "success"
            )
        else:
            QMessageBox.information(
                self,
                "Export Completed",
                f"Preferences exported to:\n{export_path}",
            )
        self.logger.info(
            "preference_portability_gui_export_completed user_id=%s path=%s "
            "encrypt=%s skip_encrypted=%s categories=%s",
            user_id,
            export_path,
            encrypt,
            skip_encrypted,
            categories or [],
        )

    def _handle_import(self) -> None:
        source_text = self.import_source_edit.text().strip()
        if not source_text:
            if Modal:
                Modal(
                    "Missing Information",
                    "Select an export file to import.",
                    ["OK"],
                    self,
                ).exec_()
            else:
                QMessageBox.warning(
                    self, "Missing Information", "Select an export file to import."
                )
            return

        source_path = Path(source_text)
        if not source_path.exists():
            if Modal:
                Modal(
                    "Invalid Source", "Selected file does not exist.", ["OK"], self
                ).exec_()
            else:
                QMessageBox.warning(
                    self, "Invalid Source", "Selected file does not exist."
                )
            return

        target_user = self.import_target_user_edit.text().strip() or None
        allow_overwrite = self.import_allow_overwrite.isChecked()

        decrypt = self.import_decrypt.isChecked()
        passphrase = self.import_passphrase_edit.text() if decrypt else None
        if decrypt and not passphrase:
            if Modal:
                Modal(
                    "Missing Passphrase",
                    "Enter a passphrase when decryption is enabled.",
                    ["OK"],
                    self,
                ).exec_()
            else:
                QMessageBox.warning(
                    self,
                    "Missing Passphrase",
                    "Enter a passphrase when decryption is enabled.",
                )
            return

        self.logger.info(
            "preference_portability_gui_import_requested source=%s "
            "target_user=%s allow_overwrite=%s decrypt=%s",
            source_path,
            target_user or "<export-user>",
            allow_overwrite,
            decrypt,
        )

        try:
            result = import_preferences(
                source_path,
                passphrase=passphrase,
                target_user_id=target_user,
                allow_overwrite=allow_overwrite,
            )
        except (
            PreferencePortabilityError
        ) as exc:  # ERR: non-fatal — surfaced via Modal; import failed
            self.logger.error("Import failed: %s", exc, exc_info=True)
            if Modal:
                Modal(
                    _PrefPortStrings.MODAL_ERROR_TITLE,
                    _PrefPortStrings.ERR_IMPORT_FAILED,
                    ["OK"],
                    self,
                ).exec_()
            return
        except (
            ValueError,
            OSError,
        ) as exc:  # ERR: non-fatal — surfaced via Modal; unexpected import failure  # pragma: no cover - defensive
            self.logger.error(
                "Unexpected import failure: %s",
                exc,
                exc_info=True,
            )
            if Modal:
                Modal(
                    _PrefPortStrings.MODAL_ERROR_TITLE,
                    _PrefPortStrings.ERR_IMPORT_FAILED,
                    ["OK"],
                    self,
                ).exec_()
            return

        status_bar = self.statusBar()
        if status_bar is not None:
            status_bar.showMessage(
                f"Import applied {result['applied']} entries",
                5000,
            )
        if ToastNotification:
            ToastNotification(parent=self).show_message(
                "Imported {applied} entries (skipped {skipped}) for user {user_id}.".format(
                    **result
                ),
                "success",
            )
        else:
            QMessageBox.information(
                self,
                "Import Completed",
                (
                    "Imported {applied} entries (skipped {skipped}) for "
                    "user {user_id}."
                ).format(**result),
            )
        self.logger.info(
            "preference_portability_gui_import_completed source=%s user_id=%s "
            "applied=%d skipped=%d",
            source_path,
            result.get("user_id"),
            result.get("applied", 0),
            result.get("skipped", 0),
        )

    @staticmethod
    def _parse_categories(raw_value: str) -> Optional[Sequence[str]]:
        cleaned = [item.strip() for item in raw_value.split(",") if item.strip()]
        return tuple(cleaned) if cleaned else None
