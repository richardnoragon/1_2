"""Dialog for configuring application appearance settings."""

from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)

from .settings import AppearanceSettings
from .styles import Theme


class AppearanceDialog(QDialog):
    """Dialog for configuring application appearance."""

    def __init__(self, parent=None):
        """Initialize the dialog.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._settings = AppearanceSettings()
        self.setup_ui()
        self.load_current_settings()

    def setup_ui(self):
        """Set up the dialog UI."""
        self.setWindowTitle("Appearance Settings")
        layout = QVBoxLayout()

        # Theme selection
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Theme:")
        self.theme_combo = QComboBox()
        self.theme_combo.setAccessibleName("Theme selection")
        self.theme_combo.setMinimumHeight(44)
        self.theme_combo.addItems(["Light", "Dark"])
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        layout.addLayout(theme_layout)

        # Font size selection
        font_layout = QHBoxLayout()
        font_label = QLabel("Font Size:")
        self.font_spin = QSpinBox()
        self.font_spin.setAccessibleName("Font size")
        self.font_spin.setMinimumHeight(44)
        self.font_spin.setRange(8, 24)
        font_layout.addWidget(font_label)
        font_layout.addWidget(self.font_spin)
        layout.addLayout(font_layout)

        # Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.setAccessibleName("Save appearance settings")
        save_button.setMinimumHeight(44)
        cancel_button = QPushButton("Cancel")
        cancel_button.setAccessibleName("Cancel appearance settings")
        cancel_button.setMinimumHeight(44)
        save_button.clicked.connect(self.save_settings)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def load_current_settings(self):
        """Load current settings into the UI."""
        # Set theme
        theme_index = 0 if self._settings.theme == Theme.LIGHT else 1
        self.theme_combo.setCurrentIndex(theme_index)

        # Set font size
        self.font_spin.setValue(self._settings.font_size)

    def save_settings(self):
        """Save the settings and close dialog."""
        # Update theme
        theme_idx = self.theme_combo.currentIndex()
        new_theme = Theme.LIGHT if theme_idx == 0 else Theme.DARK
        self._settings.theme = new_theme

        # Update font size
        self._settings.font_size = self.font_spin.value()

        self.accept()
