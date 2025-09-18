"""Theme and appearance settings management."""
import json
from pathlib import Path
from typing import Optional
from .styles import Theme


class AppearanceSettings:
    """Manages theme and appearance settings."""

    _instance: Optional['AppearanceSettings'] = None
    _settings_file = Path('config/appearance.json')

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize appearance settings."""
        if not hasattr(self, '_initialized'):
            self._theme = Theme.LIGHT
            self._font_size = 12
            self._initialized = True
            self.load_settings()

    def load_settings(self) -> None:
        """Load settings from file."""
        try:
            if self._settings_file.exists():
                with open(self._settings_file, 'r') as f:
                    settings = json.load(f)
                    self._theme = Theme(settings.get('theme', 'light'))
                    self._font_size = settings.get('font_size', 12)
        except Exception as e:
            print(f"Error loading appearance settings: {e}")

    def save_settings(self) -> None:
        """Save settings to file."""
        try:
            self._settings_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self._settings_file, 'w') as f:
                json.dump({
                    'theme': self._theme.value,
                    'font_size': self._font_size
                }, f, indent=4)
        except Exception as e:
            print(f"Error saving appearance settings: {e}")

    @property
    def theme(self) -> Theme:
        """Get current theme."""
        return self._theme

    @theme.setter
    def theme(self, value: Theme) -> None:
        """Set current theme.
        
        Args:
            value: The theme to set
        """
        self._theme = value
        self.save_settings()

    @property
    def font_size(self) -> int:
        """Get current font size."""
        return self._font_size

    @font_size.setter
    def font_size(self, value: int) -> None:
        """Set font size.
        
        Args:
            value: The font size to set
        """
        self._font_size = max(8, min(value, 24))  # Clamp between 8 and 24
        self.save_settings()
