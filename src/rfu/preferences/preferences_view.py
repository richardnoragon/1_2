"""Preferences dialog for sharing settings and exports."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

from src.core.preferences.services.share_service import ShareService
from src.log_manager import get_log_manager

LOGGER = get_log_manager().get_logger("RFU.PreferencesView")

try:  # pragma: no cover - GUI import guard
    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import (
        QCheckBox,
        QDialog,
        QGridLayout,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QPlainTextEdit,
        QPushButton,
        QVBoxLayout,
        QWidget,
    )

    PYQT5_AVAILABLE = True
except ImportError:  # pragma: no cover - GUI fallback
    PYQT5_AVAILABLE = False
    Qt = object  # type: ignore
    QDialog = object  # type: ignore
    QWidget = object  # type: ignore


def _extract_username(session: Mapping[str, Any] | Dict[str, Any]) -> str:
    username = session.get("username") if isinstance(session, Mapping) else None
    if username:
        return str(username)
    nested = session.get("session") if isinstance(session, Mapping) else None
    if isinstance(nested, Mapping):
        candidate = nested.get("username")
        if candidate:
            return str(candidate)
    return ""


if PYQT5_AVAILABLE:

    class PreferencesViewDialog(QDialog):
        """Modal dialog exposing share toggles and export helpers."""

        def __init__(
            self,
            *,
            database_path: str | Path,
            session: Mapping[str, Any] | Dict[str, Any],
            parent: Optional[QWidget] = None,
        ) -> None:
            super().__init__(parent)
            self.setWindowTitle("Preferences")
            self.database_path = Path(database_path)
            self.session = dict(session or {})
            self.username = _extract_username(self.session)
            if not self.username:
                raise ValueError("Authenticated session is required")
            self._loading_state = False

            self.share_checkbox: QCheckBox
            self.preference_id_label: QLabel
            self.status_label: QLabel
            self.purpose_input: QLineEdit
            self.payload_view: QPlainTextEdit

            self._build_ui()
            self._load_initial_state()

        def _build_ui(self) -> None:
            self.setMinimumWidth(520)

            layout = QVBoxLayout(self)
            layout.setContentsMargins(24, 24, 24, 24)
            layout.setSpacing(12)

            title = QLabel("Preference Sharing")
            title.setStyleSheet("font-size: 16px; font-weight: bold;")
            layout.addWidget(title)

            summary = QLabel(
                "Enable preference sharing to allow exports " "for support requests."
            )
            summary.setWordWrap(True)
            layout.addWidget(summary)

            grid = QGridLayout()
            grid.setHorizontalSpacing(12)
            grid.setVerticalSpacing(8)

            grid.addWidget(QLabel("Signed in as"), 0, 0)
            grid.addWidget(QLabel(self.username), 0, 1)

            grid.addWidget(QLabel("Preference ID"), 1, 0)
            self.preference_id_label = QLabel("-")
            grid.addWidget(self.preference_id_label, 1, 1)

            self.share_checkbox = QCheckBox("Allow exporting sanitized preferences")
            self.share_checkbox.stateChanged.connect(self._handle_share_toggle)
            grid.addWidget(self.share_checkbox, 2, 0, 1, 2)

            layout.addLayout(grid)

            purpose_label = QLabel("Export purpose")
            layout.addWidget(purpose_label)

            self.purpose_input = QLineEdit()
            self.purpose_input.setPlaceholderText("e.g. Troubleshooting with support")
            layout.addWidget(self.purpose_input)

            self.payload_view = QPlainTextEdit()
            self.payload_view.setReadOnly(True)
            self.payload_view.setPlaceholderText(
                "Exported JSON bundle appears here once generated"
            )
            layout.addWidget(self.payload_view)

            button_row = QHBoxLayout()
            button_row.addStretch(1)

            self.status_label = QLabel("")
            self.status_label.setStyleSheet("color: #2c3e50;")
            layout.addWidget(self.status_label)

            export_button = QPushButton("Export Preferences")
            export_button.clicked.connect(self._handle_export)
            button_row.addWidget(export_button)

            close_button = QPushButton("Close")
            close_button.clicked.connect(self.reject)
            button_row.addWidget(close_button)

            layout.addLayout(button_row)

        def _load_initial_state(self) -> None:
            row = self._fetch_user_row()
            share_enabled = bool(row.get("share_preferences")) if row else False
            preference_id = row.get("preferences_id") if row else None
            self._loading_state = True
            try:
                self.share_checkbox.setChecked(share_enabled)
            finally:
                self._loading_state = False
            self.preference_id_label.setText(preference_id or "Not linked")
            self._set_status("Sharing enabled" if share_enabled else "Sharing off")

        def _fetch_user_row(self) -> Dict[str, Any]:
            if not self.database_path.exists():
                raise FileNotFoundError("Identity database not found")
            conn = sqlite3.connect(self.database_path)
            conn.row_factory = sqlite3.Row
            try:
                row = conn.execute(
                    """
                    SELECT share_preferences,
                           preferences_id
                    FROM user_accounts
                    WHERE username = ?
                    LIMIT 1
                    """,
                    (self.username,),
                ).fetchone()
                if row is None:
                    raise ValueError(
                        f"User {self.username!r} does not exist in user_accounts"
                    )
                return dict(row)
            finally:
                conn.close()

        def _handle_share_toggle(self, state: int) -> None:
            if self._loading_state:
                return
            enabled = state == Qt.Checked
            try:
                self._update_share_flag(enabled)
            except Exception as exc:
                LOGGER.warning("Unable to toggle share flag: %s", exc)
                self._loading_state = True
                self.share_checkbox.blockSignals(True)
                self.share_checkbox.setChecked(not enabled)
                self.share_checkbox.blockSignals(False)
                self._loading_state = False
                self._set_status(str(exc), error=True)
                return
            self._set_status(
                "Preference sharing enabled"
                if enabled
                else "Preference sharing disabled"
            )

        def _update_share_flag(self, enabled: bool) -> None:
            conn = sqlite3.connect(self.database_path)
            try:
                conn.execute(
                    "UPDATE user_accounts SET share_preferences=? WHERE username=?",
                    (1 if enabled else 0, self.username),
                )
                conn.commit()
            finally:
                conn.close()

        def _handle_export(self) -> None:
            purpose = (self.purpose_input.text() or "").strip()
            if not purpose:
                self._set_status("Enter a sharing purpose before exporting", error=True)
                self.purpose_input.setFocus()
                return
            service = ShareService(
                database_path=self.database_path,
                origin_surface="gui",
            )
            try:
                bundle = service.export_preferences(
                    username=self.username,
                    purpose=purpose,
                    actor_username=self.username,
                )
            except Exception as exc:
                LOGGER.warning("Preference export failed: %s", exc)
                self._set_status(str(exc), error=True)
                return

            self.payload_view.setPlainText(json.dumps(bundle, indent=2, sort_keys=True))
            self._set_status("Preferences exported successfully")

        def _set_status(self, message: str, *, error: bool = False) -> None:
            color = "#e74c3c" if error else "#2c3e50"
            self.status_label.setStyleSheet(f"color: {color};")
            self.status_label.setText(message)

else:  # pragma: no cover - fallback definitions

    class PreferencesViewDialog:  # type: ignore[override]
        def __init__(self, *_, **__):
            raise RuntimeError("PyQt5 is required for the preferences dialog")


__all__ = ["PreferencesViewDialog"]
