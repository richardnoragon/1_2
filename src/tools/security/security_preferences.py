"""
Security Preferences GUI (lightweight fallback)

This module provides a minimal SecurityPreferencesGUI so the Dialog Hub can
launch Security Preferences without import errors, even if the full-featured
implementation isn't present. It follows the StandardWindow pattern used across
the suite and can be expanded later.
"""

import sys

try:
    from src.gui.themes import token
    from PyQt5.QtWidgets import (
        QApplication,
        QLabel,
        QMainWindow,
        QMessageBox,
        QPushButton,
        QVBoxLayout,
        QWidget,
    )
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
        self.setWindowTitle("Security Preferences - Richard's File Utilities")
        self.setGeometry(120, 120, 800, 600)
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        header = QLabel("Security Preferences")
        header.setStyleSheet(
            """
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: {token('text_primary')};
                padding: 10px;
                background-color: {token('background')};
                border-radius: 5px;
                margin-bottom: 10px;
            }
            """
        )
        layout.addWidget(header)

        desc = QLabel(
            "This is a lightweight Security Preferences panel.\n\n"
            "It exists to ensure the Security tab launches without errors.\n"
            "A fuller implementation can add tabs for: Encryption, Directory\n"
            "Security, Access Control, and Audit settings."
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)

        test_btn = QPushButton("Run Security Self-Check")
        test_btn.clicked.connect(self._run_self_check)
        layout.addWidget(test_btn)

        help_btn = QPushButton("Show Help")
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
