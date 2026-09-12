"""Backward-compatible config manager for legacy imports.

This module preserves the historical flat-dictionary configuration API used by
older scripts and tests in this repository.
"""

from __future__ import annotations

import json
import logging
from copy import deepcopy
from pathlib import Path
from threading import Lock
from typing import Any, Dict, Optional, Union


class ConfigManager:
    """Compatibility implementation for the legacy flat-config API."""

    _instance: Optional["ConfigManager"] = None
    _lock = Lock()

    def __new__(cls, config_file: Optional[Union[str, Path]] = None):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            if config_file is not None:
                cls._instance._pending_config_file = Path(config_file)
        return cls._instance

    def __init__(self, config_file: Optional[Union[str, Path]] = None):
        if getattr(self, "_initialized", False):
            # Reinitialize when a custom config file is provided to a running
            # singleton instance.
            if config_file is not None:
                self.config_path = config_file
            return

        self.logger = logging.getLogger("RFU.LegacyConfigManager")
        self._initialized = True
        self.config: Dict[str, Any] = {}
        self.config_dir = Path("config")
        self.config_file = self.config_dir / "rfu_config.json"
        self._pending_config_file = None
        if config_file is not None:
            self.config_path = config_file
        else:
            self._ensure_default_config()
            self.load_config()

    def _default_config(self) -> Dict[str, Any]:
        return {
            "last_directory": str(Path.home()),
            "file_types": [".txt", ".doc", ".pdf"],
            "theme": "light",
            "language": "en",
            "auto_backup": True,
            "max_recent_files": 10,
            "show_hidden": False,
        }

    def _ensure_default_config(self) -> None:
        defaults = self._default_config()
        for key, value in defaults.items():
            self.config.setdefault(key, deepcopy(value))

    def _validate_config(self, config_data: Dict[str, Any]) -> None:
        if not isinstance(config_data, dict):
            raise ValueError("Configuration must be a dictionary")

        if "theme" in config_data and not isinstance(config_data["theme"], str):
            raise ValueError("Theme must be a string")
        if "language" in config_data and not isinstance(config_data["language"], str):
            raise ValueError("Language must be a string")
        if "show_hidden" in config_data and not isinstance(config_data["show_hidden"], bool):
            raise ValueError("show_hidden must be a boolean")
        if "auto_backup" in config_data and not isinstance(config_data["auto_backup"], bool):
            raise ValueError("auto_backup must be a boolean")
        if "max_recent_files" in config_data and not isinstance(config_data["max_recent_files"], int):
            raise ValueError("max_recent_files must be an integer")

    def _load_from_disk(self) -> Dict[str, Any]:
        if not self.config_file.exists():
            self.config = self._default_config()
            return deepcopy(self.config)

        try:
            with open(self.config_file, "r", encoding="utf-8") as handle:
                data = json.load(handle)
        except (json.JSONDecodeError, OSError):
            self.logger.warning("Invalid config file %s; using defaults", self.config_file)
            self.config = self._default_config()
            return deepcopy(self.config)

        if not isinstance(data, dict):
            self.config = self._default_config()
            return deepcopy(self.config)

        self.config = deepcopy(data)
        return deepcopy(self.config)

    @property
    def config_path(self):
        return self.config_file

    @config_path.setter
    def config_path(self, value):
        self.config_file = Path(value).expanduser()
        self.config_dir = self.config_file.parent
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self._load_from_disk()

    def get_value(self, key: str, default: Any = None):
        return self.config.get(key, default)

    def set_value(self, key: str, value: Any):
        self.config[key] = value
        self.save_config()
        return value

    def merge_config(self, updates: Dict[str, Any]):
        if not isinstance(updates, dict):
            raise ValueError("merge_config expects a dictionary")
        self.config.update(updates)
        self.save_config()
        return self.config.copy()

    def save_config(self, config_data: Optional[Dict[str, Any]] = None, validate_required: bool = False):
        if config_data is not None:
            self._validate_config(config_data)
            if validate_required:
                required = ["theme", "language"]
                missing = [key for key in required if key not in config_data]
                if missing:
                    raise ValueError(f"Missing required configuration field(s): {missing}")
            self.config = deepcopy(config_data)
        else:
            self._validate_config(self.config)

        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, "w", encoding="utf-8") as handle:
            json.dump(self.config, handle, indent=2, ensure_ascii=False)
        return True

    def load_config(self):
        self._load_from_disk()
        return self.config.copy()

    def get_config(self):
        self._load_from_disk()
        return self.config.copy()

    def update_config(self, key: str, value: Any):
        self.set_value(key, value)

    def update_multiple(self, updates: Dict[str, Any]):
        self.merge_config(updates)

    def reset_to_defaults(self):
        self.config = self._default_config()
        self.save_config()
        return True

    def create_backup(self) -> str:
        if not self.config_file.exists():
            self.save_config()
        timestamp = __import__("datetime").datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.config_dir / f"{self.config_file.stem}_backup_{timestamp}.json"
        with open(self.config_file, "r", encoding="utf-8") as src, open(backup_path, "w", encoding="utf-8") as dst:
            dst.write(src.read())
        return str(backup_path)

    def restore_from_backup(self, backup_file: Union[str, Path]):
        backup_path = Path(backup_file)
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_path}")
        with open(backup_path, "r", encoding="utf-8") as src, open(self.config_file, "w", encoding="utf-8") as dst:
            dst.write(src.read())
        self.load_config()

    def get_setting(self, section: str, key: Optional[str] = None, default: Any = None):
        if key is None:
            return self.config.get(section, default)
        return self.config.get(key, default)

    def set_setting(self, section: str, key: str, value: Any):
        self.config[key] = value
        return self.save_config()

    def get_section(self, section: str):
        return self.config.copy()

    def set_section(self, section: str, settings: Dict[str, Any]):
        self.config.update(settings)
        return self.save_config()

    def remove_setting(self, section: str, key: str):
        self.config.pop(key, None)
        return self.save_config()

    def get_all_settings(self):
        return self.config.copy()

    def export_config(self, export_path):
        export_file = Path(export_path)
        export_file.parent.mkdir(parents=True, exist_ok=True)
        with open(export_file, "w", encoding="utf-8") as handle:
            json.dump(self.config, handle, indent=2, ensure_ascii=False)
        return True


get_config_manager = ConfigManager

__all__ = ["ConfigManager", "get_config_manager"]
