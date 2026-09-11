#!/usr/bin/env python3
"""
Simple Password Generator Tool for Richard's File Utilities
A simple password generator with customizable options.
"""
import logging
import random
import secrets
import string
import sys

try:
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QClipboard
    from PyQt5.QtWidgets import (
        QApplication,
        QCheckBox,
        QGridLayout,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QMainWindow,
        QMessageBox,
        QSlider,
        QSpinBox,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )

    from src.gui.components.inputs import TextInput
    from src.gui.themes import ThemeManager, Typography, token
except ImportError:
    print("PyQt5 not available. Please install PyQt5.")
    sys.exit(1)

# ---------------------------------------------------------------------------
# CP: Component replacement imports (CP-1 through CP-5)
# ---------------------------------------------------------------------------
try:
    from src.gui.components.buttons import PrimaryButton, SecondaryButton
    from src.gui.components.modal import Modal
    from src.gui.components.toast import ToastNotification

    _CP_AVAILABLE = True
except ImportError:
    PrimaryButton = QPushButton
    SecondaryButton = QPushButton
    Modal = None
    ToastNotification = None
    _CP_AVAILABLE = False


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
    from src.rfu.ui_strings import PasswordGenerator as _PGStrings
except ImportError:

    class _PGStrings:  # type: ignore[no-redef]
        TITLE = "Password Generator"
        WINDOW_TITLE = "Password Generator — RFU"
        LOADING = "Loading Password Generator…"
        ERR_INIT_FAILED = (
            "Could not start Password Generator. "
            "Please try again or restart the application."
        )


class SimplePasswordGeneratorGUI(QMainWindow):
    """Simple Password Generator GUI."""

    def __init__(self, hub_instance=None):
        super().__init__()
        self._hub = hub_instance
        try:
            from src.rfu.log_manager import get_log_manager

            self._logger = get_log_manager().get_logger("SimplePasswordGeneratorGUI")
        except Exception:  # ERR: non-fatal — logger fallback to module logger
            self._logger = logging.getLogger("SimplePasswordGeneratorGUI")
        self.setWindowTitle(_PGStrings.WINDOW_TITLE)
        self.setMinimumSize(600, 500)
        self.resize(700, 600)
        # Apply basic styling
        self._apply_stylesheet()

        self._setup_ui()
        register_gui_component(
            self, tool_id="password_generator", recovery_callback=self.degraded_fallback
        )
        _emit_telemetry("ui_view_load", tool_id="password_generator")
        ThemeManager.add_theme_changed_callback(self._on_theme_changed)

    def _apply_stylesheet(self) -> None:
        """Build and apply the token-driven stylesheet (TH-1c)."""
        self.setStyleSheet(
            f"""
            QMainWindow {{
                background-color: {token('surface')};
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {token('border')};
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
            QPushButton {{
                background-color: {token('semantic_success')};
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 14px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {token('semantic_success')};
            }}
            QPushButton:pressed {{
                background-color: {token('semantic_success')};
            }}
            QLineEdit, QTextEdit {{
                border: 1px solid {token('border')};
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
            }}
        """
        )

    def _on_theme_changed(self, variant: str) -> None:
        """Re-apply token-based stylesheets when the active theme variant changes."""
        self._apply_stylesheet()

    def health_check(self) -> bool:
        """Return True if core UI is functional (GRD-3a)."""
        try:
            return self.centralWidget() is not None
        except Exception:
            return False

    def degraded_fallback(self) -> None:
        """Enter degraded / read-only state (GRD-3b)."""
        try:
            self._logger.warning("SimplePasswordGeneratorGUI entering degraded mode")
        except Exception:
            pass
        _emit_telemetry(
            "ui_error_event", tool_id="password_generator", error_type="degraded"
        )

    def _setup_ui(self):
        """Setup the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        # Title
        title = QLabel("🔑 Password Generator")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(Typography.h1())
        layout.addWidget(title)
        # Options group
        options_group = QGroupBox("Password Options")
        options_layout = QGridLayout(options_group)
        # Length
        options_layout.addWidget(QLabel("Length:"), 0, 0)
        self.length_spin = QSpinBox()
        self.length_spin.setAccessibleName("Password length")
        self.length_spin.setAccessibleDescription(
            "Number of characters in each generated password, 4 to 128"
        )
        self.length_spin.setMinimumHeight(44)
        self.length_spin.setRange(4, 128)
        self.length_spin.setValue(16)
        options_layout.addWidget(self.length_spin, 0, 1)
        # Character options
        self.include_uppercase = QCheckBox("Include Uppercase (A-Z)")
        self.include_uppercase.setChecked(True)
        self.include_uppercase.setAccessibleName("Include uppercase letters")
        self.include_uppercase.setMinimumHeight(44)
        options_layout.addWidget(self.include_uppercase, 1, 0, 1, 2)
        self.include_lowercase = QCheckBox("Include Lowercase (a-z)")
        self.include_lowercase.setChecked(True)
        self.include_lowercase.setAccessibleName("Include lowercase letters")
        self.include_lowercase.setMinimumHeight(44)
        options_layout.addWidget(self.include_lowercase, 2, 0, 1, 2)
        self.include_numbers = QCheckBox("Include Numbers (0-9)")
        self.include_numbers.setChecked(True)
        self.include_numbers.setAccessibleName("Include numbers")
        self.include_numbers.setMinimumHeight(44)
        options_layout.addWidget(self.include_numbers, 3, 0, 1, 2)
        self.include_symbols = QCheckBox("Include Symbols (!@#$%^&*)")
        self.include_symbols.setChecked(True)
        self.include_symbols.setAccessibleName("Include symbols")
        self.include_symbols.setMinimumHeight(44)
        options_layout.addWidget(self.include_symbols, 4, 0, 1, 2)
        self.exclude_ambiguous = QCheckBox("Exclude Ambiguous (0, O, l, 1, I)")
        self.exclude_ambiguous.setChecked(True)
        self.exclude_ambiguous.setAccessibleName("Exclude ambiguous characters")
        self.exclude_ambiguous.setAccessibleDescription(
            "Removes characters that look similar in some fonts: 0, O, l, 1, I"
        )
        self.exclude_ambiguous.setMinimumHeight(44)
        options_layout.addWidget(self.exclude_ambiguous, 5, 0, 1, 2)
        layout.addWidget(options_group)
        # Generate button
        self.generate_btn = PrimaryButton("🎲 Generate Password")
        self.generate_btn.clicked.connect(self.generate_password)
        layout.addWidget(self.generate_btn)
        # Generated password display
        password_group = QGroupBox("Generated Password")
        password_layout = QVBoxLayout(password_group)
        self.password_display = TextInput("Generated password")
        self.password_display.setAccessibleName("Generated password")
        self.password_display.setReadOnly(True)
        self.password_display.setFont(Typography.h3())
        password_layout.addWidget(self.password_display)
        # Copy button
        self.copy_btn = SecondaryButton("📋 Copy to Clipboard")
        self.copy_btn.clicked.connect(self.copy_password)
        password_layout.addWidget(self.copy_btn)
        layout.addWidget(password_group)
        # Multiple passwords
        multiple_group = QGroupBox("Generate Multiple Passwords")
        multiple_layout = QVBoxLayout(multiple_group)
        count_layout = QHBoxLayout()
        count_layout.addWidget(QLabel("Count:"))
        self.count_spin = QSpinBox()
        self.count_spin.setAccessibleName("Number of passwords to generate")
        self.count_spin.setAccessibleDescription(
            "How many separate passwords to generate at once, 1 to 50"
        )
        self.count_spin.setMinimumHeight(44)
        self.count_spin.setRange(1, 50)
        self.count_spin.setValue(5)
        count_layout.addWidget(self.count_spin)
        count_layout.addStretch()
        multiple_layout.addLayout(count_layout)
        self.generate_multiple_btn = SecondaryButton("🎲 Generate Multiple")
        self.generate_multiple_btn.clicked.connect(self.generate_multiple_passwords)
        multiple_layout.addWidget(self.generate_multiple_btn)
        self.multiple_display = QTextEdit()
        self.multiple_display.setAccessibleName("Multiple generated passwords")
        self.multiple_display.setMaximumHeight(150)
        self.multiple_display.setFont(Typography.body())
        multiple_layout.addWidget(self.multiple_display)
        layout.addWidget(multiple_group)
        # Generate initial password
        self.generate_password()

    def get_character_set(self):
        """Get the character set based on options."""
        chars = ""
        if self.include_uppercase.isChecked():
            chars += string.ascii_uppercase
        if self.include_lowercase.isChecked():
            chars += string.ascii_lowercase
        if self.include_numbers.isChecked():
            chars += string.digits
        if self.include_symbols.isChecked():
            chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if self.exclude_ambiguous.isChecked():
            # Remove ambiguous characters
            ambiguous = "0Ol1I"
            chars = "".join(c for c in chars if c not in ambiguous)
        return chars

    def generate_password(self):
        """Generate a single password."""
        chars = self.get_character_set()
        if not chars:
            if Modal:
                Modal(
                    "Warning",
                    "Please select at least one character type!",
                    ["OK"],
                    parent=self,
                ).exec_()
            else:
                QMessageBox.warning(
                    self, "Warning", "Please select at least one character type!"
                )
            return
        length = self.length_spin.value()
        # Use secrets module for cryptographically secure generation
        password = "".join(secrets.choice(chars) for _ in range(length))
        self.password_display.setText(password)

    def generate_multiple_passwords(self):
        """Generate multiple passwords."""
        chars = self.get_character_set()
        if not chars:
            if Modal:
                Modal(
                    "Warning",
                    "Please select at least one character type!",
                    ["OK"],
                    parent=self,
                ).exec_()
            else:
                QMessageBox.warning(
                    self, "Warning", "Please select at least one character type!"
                )
            return
        length = self.length_spin.value()
        count = self.count_spin.value()
        passwords = []
        for _ in range(count):
            password = "".join(secrets.choice(chars) for _ in range(length))
            passwords.append(password)
        self.multiple_display.setText("\n".join(passwords))

    def copy_password(self):
        """Copy the current password to clipboard."""
        password = self.password_display.text()
        if password:
            clipboard = QApplication.clipboard()
            clipboard.setText(password)
            if ToastNotification:
                ToastNotification(parent=self).show_message(
                    "Password copied to clipboard!", "success"
                )
            else:
                QMessageBox.information(
                    self, "Success", "Password copied to clipboard!"
                )
        else:
            if ToastNotification:
                ToastNotification(parent=self).show_message(
                    "No password to copy!", "warning"
                )
            else:
                QMessageBox.warning(self, "Warning", "No password to copy!")


def main():
    """Main function to run the password generator."""
    app = QApplication(sys.argv)
    window = SimplePasswordGeneratorGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
