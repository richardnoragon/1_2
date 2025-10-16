#!/usr/bin/env python3
"""
Simple Password Generator Tool for Richard's File Utilities

A simple password generator with customizable options.
"""

import sys
import random
import string
import secrets

try:
    from PyQt5.QtWidgets import (
        QMainWindow,
        QWidget,
        QVBoxLayout,
        QHBoxLayout,
        QPushButton,
        QLabel,
        QSpinBox,
        QCheckBox,
        QApplication,
        QMessageBox,
        QGroupBox,
        QLineEdit,
        QTextEdit,
        QGridLayout,
        QSlider,
    )
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QFont, QClipboard
except ImportError:
    print("PyQt5 not available. Please install PyQt5.")
    sys.exit(1)


class SimplePasswordGeneratorGUI(QMainWindow):
    """Simple Password Generator GUI."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Password Generator - Richard's File Utilities")
        self.setMinimumSize(600, 500)
        self.resize(700, 600)

        # Apply basic styling
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #f5f5f5;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 14px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QLineEdit, QTextEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
            }
        """
        )

        self._setup_ui()

    def _setup_ui(self):
        """Setup the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Title
        title = QLabel("🔑 Password Generator")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title)

        # Options group
        options_group = QGroupBox("Password Options")
        options_layout = QGridLayout(options_group)

        # Length
        options_layout.addWidget(QLabel("Length:"), 0, 0)
        self.length_spin = QSpinBox()
        self.length_spin.setRange(4, 128)
        self.length_spin.setValue(16)
        options_layout.addWidget(self.length_spin, 0, 1)

        # Character options
        self.include_uppercase = QCheckBox("Include Uppercase (A-Z)")
        self.include_uppercase.setChecked(True)
        options_layout.addWidget(self.include_uppercase, 1, 0, 1, 2)

        self.include_lowercase = QCheckBox("Include Lowercase (a-z)")
        self.include_lowercase.setChecked(True)
        options_layout.addWidget(self.include_lowercase, 2, 0, 1, 2)

        self.include_numbers = QCheckBox("Include Numbers (0-9)")
        self.include_numbers.setChecked(True)
        options_layout.addWidget(self.include_numbers, 3, 0, 1, 2)

        self.include_symbols = QCheckBox("Include Symbols (!@#$%^&*)")
        self.include_symbols.setChecked(True)
        options_layout.addWidget(self.include_symbols, 4, 0, 1, 2)

        self.exclude_ambiguous = QCheckBox("Exclude Ambiguous (0, O, l, 1, I)")
        self.exclude_ambiguous.setChecked(True)
        options_layout.addWidget(self.exclude_ambiguous, 5, 0, 1, 2)

        layout.addWidget(options_group)

        # Generate button
        self.generate_btn = QPushButton("🎲 Generate Password")
        self.generate_btn.clicked.connect(self.generate_password)
        layout.addWidget(self.generate_btn)

        # Generated password display
        password_group = QGroupBox("Generated Password")
        password_layout = QVBoxLayout(password_group)

        self.password_display = QLineEdit()
        self.password_display.setReadOnly(True)
        self.password_display.setFont(QFont("Courier", 12))
        password_layout.addWidget(self.password_display)

        # Copy button
        self.copy_btn = QPushButton("📋 Copy to Clipboard")
        self.copy_btn.clicked.connect(self.copy_password)
        password_layout.addWidget(self.copy_btn)

        layout.addWidget(password_group)

        # Multiple passwords
        multiple_group = QGroupBox("Generate Multiple Passwords")
        multiple_layout = QVBoxLayout(multiple_group)

        count_layout = QHBoxLayout()
        count_layout.addWidget(QLabel("Count:"))
        self.count_spin = QSpinBox()
        self.count_spin.setRange(1, 50)
        self.count_spin.setValue(5)
        count_layout.addWidget(self.count_spin)
        count_layout.addStretch()
        multiple_layout.addLayout(count_layout)

        self.generate_multiple_btn = QPushButton("🎲 Generate Multiple")
        self.generate_multiple_btn.clicked.connect(
            self.generate_multiple_passwords
        )
        multiple_layout.addWidget(self.generate_multiple_btn)

        self.multiple_display = QTextEdit()
        self.multiple_display.setMaximumHeight(150)
        self.multiple_display.setFont(QFont("Courier", 10))
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
            QMessageBox.information(
                self, "Success", "Password copied to clipboard!"
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
