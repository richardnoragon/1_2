"""GUI front-end for preference portability operations."""

from __future__ import annotations

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
except ImportError as exc:  # pragma: no cover - GUI dependency
    raise RuntimeError("PyQt5 is required for Preference Portability GUI") from exc

from src.core.preferences.portability import (
    AES_AVAILABLE,
    PreferencePortabilityError,
    export_preferences,
    import_preferences,
)
from src.log_manager import get_log_manager


class PreferencePortabilityGUI(QMainWindow):
    """Simple interface for exporting and importing preference payloads."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.logger = get_log_manager().get_logger("PreferencePortabilityGUI")
        self.setWindowTitle("Preference Portability")
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

    def _init_ui(self) -> None:
        central = QWidget(self)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        header = QLabel("Manage preference export/import operations from the hub.")
        header.setWordWrap(True)
        layout.addWidget(header)

        self.tabs = QTabWidget()
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
        self.export_user_edit.setPlaceholderText("User identifier (required)")
        form.addRow("User ID", self.export_user_edit)

        self.export_dest_edit = QLineEdit()
        self.export_dest_edit.setPlaceholderText("Destination directory (optional)")
        dest_button = QPushButton("Browse…")
        dest_button.clicked.connect(self._browse_export_destination)
        dest_row = self._wrap_with_row(self.export_dest_edit, dest_button)
        form.addRow("Destination", dest_row)

        self.export_categories_edit = QLineEdit()
        self.export_categories_edit.setPlaceholderText(
            "Comma separated categories (optional)"
        )
        form.addRow("Categories", self.export_categories_edit)

        self.export_skip_encrypted = QCheckBox("Skip encrypted rows")
        form.addRow("Encrypted", self.export_skip_encrypted)

        self.export_encrypt = QCheckBox("Encrypt exported payload")
        self.export_encrypt.toggled.connect(self._on_export_encrypt_toggled)
        if not AES_AVAILABLE:
            self.export_encrypt.setEnabled(False)
            self.export_encrypt.setToolTip("Install pyAesCrypt to enable encryption")
        form.addRow("Encryption", self.export_encrypt)

        self.export_passphrase_edit = QLineEdit()
        self.export_passphrase_edit.setEchoMode(QLineEdit.Password)
        self.export_passphrase_edit.setEnabled(False)
        form.addRow("Passphrase", self.export_passphrase_edit)

        tab_layout.addLayout(form)

        self.export_button = QPushButton("Export Preferences")
        self.export_button.clicked.connect(self._handle_export)
        button_row = QHBoxLayout()
        button_row.addStretch(1)
        button_row.addWidget(self.export_button)
        tab_layout.addLayout(button_row)
        tab_layout.addStretch(1)

        if not AES_AVAILABLE:
            warning = QLabel(
                "AES encryption unavailable: install pyAesCrypt to enable it."
            )
            warning.setStyleSheet("color: #b9770e;")
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
        self.import_source_edit.setPlaceholderText("Export file path (required)")
        source_button = QPushButton("Browse…")
        source_button.clicked.connect(self._browse_import_source)
        source_row = self._wrap_with_row(
            self.import_source_edit,
            source_button,
        )
        form.addRow("Source", source_row)

        self.import_target_user_edit = QLineEdit()
        self.import_target_user_edit.setPlaceholderText("Override user (optional)")
        form.addRow("Target User", self.import_target_user_edit)

        self.import_allow_overwrite = QCheckBox("Allow overwriting existing values")
        form.addRow("Overwrite", self.import_allow_overwrite)

        self.import_decrypt = QCheckBox("Decrypt payload with passphrase")
        self.import_decrypt.toggled.connect(self._on_import_decrypt_toggled)
        if not AES_AVAILABLE:
            self.import_decrypt.setEnabled(False)
            self.import_decrypt.setToolTip("Install pyAesCrypt to enable decryption")
        form.addRow("Decryption", self.import_decrypt)

        self.import_passphrase_edit = QLineEdit()
        self.import_passphrase_edit.setEchoMode(QLineEdit.Password)
        self.import_passphrase_edit.setEnabled(False)
        form.addRow("Passphrase", self.import_passphrase_edit)

        tab_layout.addLayout(form)

        self.import_button = QPushButton("Import Preferences")
        self.import_button.clicked.connect(self._handle_import)
        button_row = QHBoxLayout()
        button_row.addStretch(1)
        button_row.addWidget(self.import_button)
        tab_layout.addLayout(button_row)
        tab_layout.addStretch(1)

        if not AES_AVAILABLE:
            warning = QLabel(
                "AES decryption unavailable: install pyAesCrypt to enable it."
            )
            warning.setStyleSheet("color: #b9770e;")
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
            QMessageBox.warning(
                self,
                "Missing Information",
                "User ID is required.",
            )
            return

        destination_text = self.export_dest_edit.text().strip()
        destination = Path(destination_text) if destination_text else None

        categories = self._parse_categories(self.export_categories_edit.text())
        skip_encrypted = self.export_skip_encrypted.isChecked()

        encrypt = self.export_encrypt.isChecked()
        passphrase = self.export_passphrase_edit.text() if encrypt else None
        if encrypt and not passphrase:
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
        except PreferencePortabilityError as exc:
            QMessageBox.critical(self, "Export Failed", str(exc))
            self.logger.error("Export failed: %s", exc, exc_info=True)
            return
        except (ValueError, OSError) as exc:  # pragma: no cover - defensive
            QMessageBox.critical(self, "Export Failed", str(exc))
            self.logger.error(
                "Unexpected export failure: %s",
                exc,
                exc_info=True,
            )
            return

        status_bar = self.statusBar()
        if status_bar is not None:
            status_bar.showMessage(f"Export completed: {export_path}", 5000)
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
            QMessageBox.warning(
                self,
                "Missing Information",
                "Select an export file to import.",
            )
            return

        source_path = Path(source_text)
        if not source_path.exists():
            QMessageBox.warning(
                self,
                "Invalid Source",
                "Selected file does not exist.",
            )
            return

        target_user = self.import_target_user_edit.text().strip() or None
        allow_overwrite = self.import_allow_overwrite.isChecked()

        decrypt = self.import_decrypt.isChecked()
        passphrase = self.import_passphrase_edit.text() if decrypt else None
        if decrypt and not passphrase:
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
        except PreferencePortabilityError as exc:
            QMessageBox.critical(self, "Import Failed", str(exc))
            self.logger.error("Import failed: %s", exc, exc_info=True)
            return
        except (ValueError, OSError) as exc:  # pragma: no cover - defensive
            QMessageBox.critical(self, "Import Failed", str(exc))
            self.logger.error(
                "Unexpected import failure: %s",
                exc,
                exc_info=True,
            )
            return

        status_bar = self.statusBar()
        if status_bar is not None:
            status_bar.showMessage(
                f"Import applied {result['applied']} entries",
                5000,
            )
        QMessageBox.information(
            self,
            "Import Completed",
            (
                "Imported {applied} entries (skipped {skipped}) for " "user {user_id}."
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
