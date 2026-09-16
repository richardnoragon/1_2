"""
Security Preferences GUI (lightweight fallback)

This module provides a minimal SecurityPreferencesGUI so the Dialog Hub can
launch Security Preferences without import errors, even if the full-featured
implementation isn't present. It follows the StandardWindow pattern used across
the suite and can be expanded later.
"""
from src.rfu.localization import localized_widget as _ui_widget, bind_literal as _ui_bind
from src.rfu import font_tokens

import sys

try:
    from PyQt5.QtWidgets import (
        QApplication,
        QLabel,
        QMainWindow,
        QMessageBox,
        QVBoxLayout,
        QWidget,
    )

    from src.gui.components.buttons import PrimaryButton, SecondaryButton
    from src.gui.themes import token
except ImportError:  # pragma: no cover - runtime guard
    print("PyQt5 not available. Please install PyQt5.")
    sys.exit(1)

# StandardWindow is not required for this lightweight fallback


class SecurityPreferencesGUI(QMainWindow):
    """Minimal, expandable Security Preferences window.

    Provides a friendly placeholder with a couple of common entry points so
    other tools can link to it. Replace or extend with full implementation when
    available.
    """

    def __init__(self):
        super().__init__()
        _ui_bind(self, 'setWindowTitle', 'Legacy.se060c6c6c7f0e784')
        self.setGeometry(120, 120, 800, 600)
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        header = _ui_widget(QLabel, 'Legacy.s647b47387f78391d', 'setText')
        header.setStyleSheet(
            """
            QLabel {

                font-weight: bold;
                color: {token('text_primary')};
                padding: 10px;
                background-color: {token('background')};
                border-radius: 5px;
                margin-bottom: 10px;
            }
            """
        )
        font_tokens.bind(header, "font.toolHeader")
        layout.addWidget(header)

        desc = _ui_widget(QLabel, 'Legacy.scc0e07a5304390f0', 'setText')
        desc.setWordWrap(True)
        layout.addWidget(desc)

        test_btn = _ui_widget(PrimaryButton, 'Legacy.sb1d5c733d944cf75', 'setText')
        _ui_bind(test_btn, 'setAccessibleName', 'Legacy.sa72053bbb58d1412')
        test_btn.clicked.connect(self._run_self_check)
        layout.addWidget(test_btn)

        help_btn = _ui_widget(SecondaryButton, 'Legacy.s221c1dad35dc247f', 'setText')
        _ui_bind(help_btn, 'setAccessibleName', 'Legacy.sb4a26106054defc8')
        help_btn.clicked.connect(self._show_help)
        layout.addWidget(help_btn)

        layout.addStretch()

        # If the standard window framework is present, we could register
        # callbacks here in a richer implementation.

    def _run_self_check(self):
        QMessageBox.information(
            self,
            "Security Self-Check",
            (
                "Basic security preferences panel is operational.\n\n"
                "You can replace this placeholder with a richer "
                "implementation at\n"
                "src/tools/security/security_preferences.py"
            ),
        )

    def _show_help(self):
        QMessageBox.information(
            self,
            "Security Preferences Help",
            "Configure global security settings for the application.\n\n"
            "This placeholder provides a consistent launch experience while\n"
            "the full feature set is under development.",
        )


def main():  # pragma: no cover - manual run helper
    app = QApplication(sys.argv)
    w = SecurityPreferencesGUI()
    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":  # pragma: no cover
    main()
