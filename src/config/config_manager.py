"""Unified configuration management for Richard's File Utilities."""

from __future__ import annotations

import copy
import json
import logging
import os
import shutil
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Any, Dict, Optional, Union

DEFAULT_CONFIG_FILENAMES = ("rfu_config.json", "configuration.json")
LEGACY_CONFIG_FILENAMES = ("config.json",)

DEFAULT_VALIDATOR_PROFILES: Dict[str, Any] = {
    "default": {
        "mode": "reject",
        "allowed_types": [
            "pdf",
            "png",
            "jpg",
            "jpeg",
            "gif",
            "bmp",
            "tiff",
            "zip",
            "doc",
            "docx",
            "xls",
            "xlsx",
            "ppt",
            "pptx",
            "txt",
            "csv",
            "json",
            "xml",
        ],
        "notify": "on-mismatch",
    },
    "network_transfer": {
        "inherit": "default",
        "mode": "reject",
        "allowed_types": [
            "pdf",
            "png",
            "jpg",
            "jpeg",
            "gif",
            "zip",
            "docx",
            "xlsx",
            "pptx",
            "txt",
            "csv",
            "json",
            "xml",
        ],
        "workflow": "network_transfer",
        "notify": "on-mismatch",
    },
    "content_indexer": {
        "inherit": "default",
        "mode": "reject",
        "workflow": "content_indexer",
        "notify": "always",
    },
}

MIGRATED_PREFERENCE_KEYS: set[tuple[str, str]] = {
    ("general", "theme"),
    ("general", "default_directory"),
    ("general", "recent_directories"),
    ("general", "show_hidden"),
}

DEFAULT_CONFIG_STRUCTURE: Dict[str, Any] = {
    "general": {
        "logging_level": "INFO",
        "enable_debug_logging": False,
        "auto_save_config": True,
        "theme": "light",
        "language": "en",
        "check_for_updates": True,
        "default_directory": "",
        "recent_directories": [],
        "max_recent_entries": 10,
        "show_hidden": False,
    },
    "gui": {
        "window_width": 900,
        "window_height": 700,
        "remember_window_position": True,
        "show_status_bar": True,
        "show_toolbar": True,
        "font_size": 12,
        "font_family": "Segoe UI",
    },
    "logging": {
        "enable_file_logging": True,
        "enable_console_logging": True,
        "log_file_max_size_mb": 10,
        "log_file_backup_count": 5,
        "enable_tool_logging": True,
        "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    },
    "identity": {
        "database_path": "",
        "enable_idle_watchdog": False,
        "idle_timeout_minutes": 10,
        "watchdog_interval_seconds": 60,
    },
    "tools": {
        "default_directory": str(Path.home()),
        "remember_last_directory": True,
        "show_hidden_files": False,
        "confirm_destructive_operations": True,
        "auto_refresh_file_lists": True,
    },
    "duplicates": {
        "default_hash_algorithm": "sha256",
        "min_file_size": 1024,
        "skip_system_files": True,
    },
    "secure_delete": {
        "default_passes": 3,
        "max_passes": 35,
    },
    "compression": {
        "default_format": "zip",
        "default_compression_level": 6,
        "use_password_protection": False,
    },
    "sync": {
        "default_mode": "two_way",
        "create_backups": True,
        "skip_newer_files": False,
    },
    "catalog": {
        "recursive_by_default": True,
        "check_duplicates": False,
        "show_file_sizes": True,
        "show_dates": True,
        "default_sort_by": "name",
        "default_sort_order": "ascending",
    },
    "organize": {
        "recursive_by_default": False,
        "create_category_folders": True,
        "move_files": True,
    },
    "network_connectivity": {
        "general": {
            "default_timeout": 5000,
            "max_concurrent_operations": 10,
            "enable_logging": True,
            "log_level": "INFO",
            "auto_save_results": True,
            "results_retention_days": 30,
            "enable_notifications": True,
            "notification_sound": True,
            "data_cache_timeout": 30,
            "max_history_entries": 1000,
        },
        "bandwidth_monitor": {
            "monitoring_interval": 1000,
            "data_retention_hours": 24,
            "alert_threshold_mbps": 100.0,
            "enable_alerts": True,
            "monitor_interfaces": "auto",
            "chart_update_interval": 2000,
            "enable_real_time_chart": True,
            "show_upload_download_separate": True,
            "data_units": "auto",
            "enable_application_monitoring": False,
            "alert_email": "",
            "peak_detection_enabled": True,
            "baseline_calculation_hours": 168,
            "export_format": "csv",
            "auto_export_enabled": False,
            "auto_export_interval_hours": 24,
        },
        "wifi_analyzer": {
            "scan_interval": 30000,
            "signal_interval": 2000,
            "enable_security_analysis": True,
            "enable_interference_detection": True,
            "enable_channel_analysis": True,
            "data_retention_hours": 24,
            "max_access_points": 1000,
            "enable_alerts": True,
            "weak_signal_threshold": -70,
            "security_alert_level": "medium",
            "scan_type": "active",
            "bands": ["2.4GHz", "5GHz"],
            "channel_width_detection": True,
            "vendor_identification": True,
            "hidden_network_detection": True,
            "beacon_analysis": True,
            "probe_request_analysis": False,
            "monitor_mode_required": False,
            "auto_channel_recommendation": True,
            "interference_threshold": 0.7,
            "security_score_threshold": 0.5,
            "signal_history_size": 1000,
            "export_format": "json",
            "include_vendor_info": True,
            "include_capabilities": True,
            "real_time_updates": True,
            "update_interval": 5000,
        },
        "lan_file_transfer": {
            "discovery_port": 8765,
            "transfer_port": 8766,
            "discovery_interval": 30,
            "max_concurrent_transfers": 3,
            "default_chunk_size": 65536,
            "encryption_enabled": True,
            "compression_enabled": False,
            "default_compression": "gzip",
            "transfer_timeout": 300,
            "connection_timeout": 30,
            "enable_device_discovery": True,
            "auto_accept_trusted": False,
            "require_authentication": True,
            "enable_resume": True,
            "max_file_size_mb": 1024,
            "allowed_file_types": [
                "*",
            ],
            "blocked_file_types": [
                ".exe",
                ".bat",
                ".cmd",
                ".scr",
            ],
            "default_download_path": "Downloads",
            "enable_bandwidth_limiting": False,
            "max_upload_speed_mbps": 0,
            "max_download_speed_mbps": 0,
            "enable_notifications": True,
            "log_transfers": True,
            "keep_transfer_history": True,
            "history_retention_days": 30,
            "enable_security_scanning": False,
            "trust_local_network": True,
            "device_name": "",
            "enable_upnp": False,
            "firewall_auto_config": False,
        },
        "port_scanner": {
            "default_scan_type": "tcp",
            "common_ports": [
                21,
                22,
                23,
                25,
                53,
                80,
                110,
                135,
                139,
                143,
                443,
                993,
                995,
                1723,
                3306,
                3389,
                5432,
                5900,
            ],
            "scan_timeout": 3000,
            "max_threads": 50,
            "enable_service_detection": True,
            "enable_os_detection": False,
            "enable_vulnerability_scan": False,
            "scan_delay": 0,
            "randomize_scan_order": False,
            "save_scan_results": True,
            "export_formats": ["json", "csv", "xml"],
            "stealth_mode": False,
            "custom_port_ranges": [],
            "exclude_ports": [],
            "enable_banner_grabbing": True,
        },
        "security": {
            "require_admin_for_scans": False,
            "whitelist_scan_targets": [],
            "blacklist_scan_targets": [
                "127.0.0.1",
                "localhost",
                "::1",
            ],
            "max_scan_rate": 1000,
            "enable_scan_logging": True,
            "alert_on_suspicious_activity": True,
            "encrypt_stored_data": False,
            "data_retention_policy": "30_days",
            "audit_trail_enabled": True,
            "security_level": "moderate",
        },
        "performance": {
            "enable_performance_monitoring": True,
            "max_memory_usage_mb": 512,
            "max_cpu_usage_percent": 25,
            "operation_timeout_multiplier": 1.0,
            "enable_background_operations": True,
            "priority_level": "normal",
            "thread_pool_size": "auto",
            "cache_size_mb": 64,
            "enable_compression": True,
        },
    },
    "pdf_tools": {},
    "privacy_tools": {},
    "software_maintenance": {},
    "validator_profiles": copy.deepcopy(DEFAULT_VALIDATOR_PROFILES),
}

TOP_LEVEL_DEFAULTS: Dict[str, Any] = {
    "profiles": {},
}

TYPE_RULES = {
    ("general", "theme"): str,
    ("general", "language"): str,
    ("general", "show_hidden"): bool,
}

REQUIRED_FIELDS = (
    ("general", "theme"),
    ("general", "language"),
)


def _deepcopy(data: Any) -> Any:
    """Return a deepcopy using ``copy.deepcopy`` for readability."""

    return copy.deepcopy(data)


def _merge_defaults(target: Dict[str, Any], defaults: Dict[str, Any]) -> None:
    """Recursively merge ``defaults`` into ``target`` without overwriting."""

    for key, default_value in defaults.items():
        if isinstance(default_value, dict):
            target.setdefault(key, {})
            if isinstance(target[key], dict):
                _merge_defaults(target[key], default_value)
            else:
                target[key] = _deepcopy(default_value)
        elif key not in target:
            target[key] = _deepcopy(default_value)


class ConfigManager:
    """Centralized configuration manager with singleton semantics."""

    _instance: Optional["ConfigManager"] = None
    _lock = Lock()

    def __new__(
        cls,
        config_file: Optional[Union[str, Path]] = None,
    ) -> "ConfigManager":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
                cls._instance._config_file_override = None
            if config_file is not None:
                cls._instance._pending_override = Path(config_file)
        return cls._instance

    def __init__(self, config_file: Optional[Union[str, Path]] = None) -> None:
        override = (
            Path(config_file).expanduser()
            if config_file is not None
            else getattr(self, "_pending_override", None)
        )
        if override is not None:
            self._config_file_override = override
            self._pending_override = None
            if getattr(self, "_initialized", False):
                self._setup_config(reinitialize=True)
                return

        if not getattr(self, "_initialized", False):
            self._setup_config()
            self._initialized = True

    # ------------------------------------------------------------------
    # Core setup
    # ------------------------------------------------------------------
    def _setup_config(self, reinitialize: bool = False) -> None:
        self.logger = logging.getLogger("RFU.ConfigManager")
        self._initialize_paths()
        self.config: Dict[str, Any] = {}
        self._migrate_legacy_config()
        self._load_config()
        self._ensure_default_structure()
        self.save_config()
        if reinitialize:
            self.logger.info(
                "ConfigManager reinitialized with custom path %s",
                self.config_file,
            )
        else:
            self.logger.info("ConfigManager initialized successfully")

    def _initialize_paths(self) -> None:
        override = getattr(self, "_config_file_override", None)
        project_root = Path(__file__).resolve().parents[2]

        if override is not None:
            config_path = override
            self.config_dir = config_path.parent
            self.config_dir.mkdir(parents=True, exist_ok=True)
            self.config_file = config_path
        else:
            env_dir = os.getenv("RFU_CONFIG_DIR")
            base_dir = (
                Path(env_dir).expanduser() if env_dir else project_root / "config"
            )
            base_dir.mkdir(parents=True, exist_ok=True)

            selected: Optional[Path] = None
            for name in DEFAULT_CONFIG_FILENAMES:
                candidate = base_dir / name
                if candidate.exists():
                    selected = candidate
                    break
            if selected is None:
                selected = base_dir / DEFAULT_CONFIG_FILENAMES[0]

            self.config_dir = base_dir
            self.config_file = selected

        legacy_root = project_root
        self.legacy_config_files = (
            [self.config_dir / name for name in LEGACY_CONFIG_FILENAMES]
            + [legacy_root / name for name in DEFAULT_CONFIG_FILENAMES]
            + [legacy_root / name for name in LEGACY_CONFIG_FILENAMES]
        )

    def _migrate_legacy_config(self) -> None:
        if self.config_file.exists():
            return

        for legacy_file in self.legacy_config_files:
            try:
                if not legacy_file.exists():
                    continue
                with open(legacy_file, "r", encoding="utf-8") as handle:
                    data = json.load(handle)
                if not isinstance(data, dict):
                    continue
                self.config_dir.mkdir(parents=True, exist_ok=True)
                with open(self.config_file, "w", encoding="utf-8") as dest:
                    json.dump(data, dest, indent=2, ensure_ascii=False)
                backup = legacy_file.with_suffix(".legacy_backup")
                try:
                    if backup.exists():
                        backup.unlink()
                    legacy_file.rename(backup)
                except Exception:
                    pass
                self.logger.info(
                    "Migrated legacy configuration from %s",
                    legacy_file,
                )
                return
            except Exception as exc:
                self.logger.error(
                    "Failed to migrate legacy configuration from %s: %s",
                    legacy_file,
                    exc,
                )

    def _load_config(self) -> None:
        try:
            if self.config_file.exists():
                with open(self.config_file, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                if isinstance(data, dict):
                    self.config = data
                else:
                    self.logger.warning(
                        "Configuration file %s is not a dictionary; " "using defaults",
                        self.config_file,
                    )
                    self.config = {}
            else:
                self.config = {}
        except Exception as exc:
            self.logger.error(
                "Error loading configuration from %s: %s",
                self.config_file,
                exc,
                exc_info=True,
            )
            self.config = {}

    def _ensure_default_structure(self, force: bool = False) -> None:
        if force:
            self.config = _deepcopy(DEFAULT_CONFIG_STRUCTURE)
        else:
            _merge_defaults(self.config, DEFAULT_CONFIG_STRUCTURE)

        for key, default_value in TOP_LEVEL_DEFAULTS.items():
            if force or key not in self.config:
                self.config[key] = _deepcopy(default_value)

    # ------------------------------------------------------------------
    # Validation helpers
    # ------------------------------------------------------------------
    def _validate_config_types(self, config_data: Dict[str, Any]) -> None:
        for (section, key), expected_type in TYPE_RULES.items():
            value: Any = None
            section_has_data = section in config_data and isinstance(
                config_data[section], dict
            )
            if section_has_data:
                value = config_data[section].get(key)
            elif key in config_data:
                value = config_data.get(key)

            if value is not None and not isinstance(value, expected_type):
                type_name = expected_type.__name__
                message = f"'{section}.{key}' must be of type {type_name}"
                raise ValueError(message)

    def _validate_required_fields(self, config_data: Dict[str, Any]) -> None:
        for section, key in REQUIRED_FIELDS:
            section_has_data = section in config_data and isinstance(
                config_data[section], dict
            )
            if section_has_data:
                if key not in config_data[section]:
                    message = f"Required field '{section}.{key}' is missing"
                    raise ValueError(message)
            elif key not in config_data:
                message = f"Required field '{section}.{key}' is missing"
                raise ValueError(message)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def get_setting(
        self, section: str, key: Optional[str] = None, default: Any = None
    ) -> Any:
        try:
            section_data = self.config.get(section, {})
            if key is None:
                return section_data if section_data else default
            value = section_data.get(key, default)
            self.logger.debug(
                "Retrieved setting %s.%s: %s",
                section,
                key,
                value,
            )
            return value
        except Exception:
            self.logger.warning(
                "Failed to get %s.%s, using default: %s", section, key, default
            )
            return default

    def set_setting(self, section: str, key: str, value: Any) -> None:
        try:
            if (section, key) in MIGRATED_PREFERENCE_KEYS:
                self.logger.warning(
                    "Skipped legacy write for migrated preference %s.%s;"
                    " PreferenceManager now owns this key",
                    section,
                    key,
                )
                return
            if section not in self.config or not isinstance(
                self.config.get(section), dict
            ):
                self.config[section] = {}
            self.config[section][key] = value
            self.save_config()
            self.logger.info(
                "Updated setting %s.%s to %s",
                section,
                key,
                value,
            )
        except Exception as exc:
            self.logger.error(
                "Error setting %s.%s: %s", section, key, exc, exc_info=True
            )

    def add_recent_directory(self, directory: str) -> None:
        if not directory:
            return

        self.logger.warning(
            "Skipped legacy recent directory write for '%s'; PreferenceManager"
            " handles persistence",
            directory,
        )

    def get_recent_directories(self) -> list[str]:
        recent = self.config.get("general", {}).get("recent_directories", [])
        return list(recent)

    def reset_section(self, section: str) -> None:
        defaults = DEFAULT_CONFIG_STRUCTURE.get(section)
        if defaults is None:
            self.config.pop(section, None)
        else:
            self.config[section] = _deepcopy(defaults)
        self.save_config()
        self.logger.info("Reset section %s to default values", section)

    def reset_to_defaults(self) -> bool:
        try:
            self._ensure_default_structure(force=True)
            self.save_config()
            self.logger.info("Configuration reset to defaults")
            return True
        except Exception as exc:
            self.logger.error("Failed to reset configuration: %s", exc)
            return False

    def save_config(
        self,
        config_data: Optional[Dict[str, Any]] = None,
        validate_required: bool = False,
    ) -> None:
        try:
            if config_data is not None:
                self._validate_config_types(config_data)
                if validate_required:
                    self._validate_required_fields(config_data)
                if config_data:
                    for key, value in config_data.items():
                        if (
                            key in self.config
                            and isinstance(self.config[key], dict)
                            and isinstance(value, dict)
                        ):
                            self.config[key].update(value)
                        else:
                            self.config[key] = value

            self._ensure_default_structure()
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, "w", encoding="utf-8") as fh:
                json.dump(self.config, fh, indent=2, ensure_ascii=False)
            self.logger.debug(
                "Configuration saved to %s",
                self.config_file,
            )
        except Exception as exc:
            self.logger.error(
                "Error saving configuration: %s",
                exc,
                exc_info=True,
            )
            raise

    def load_config(self) -> bool:
        try:
            self._load_config()
            self._ensure_default_structure()
            self.logger.info("Configuration reloaded successfully")
            return True
        except Exception as exc:
            self.logger.error("Failed to reload configuration: %s", exc)
            return False

    def get_section(self, section: str) -> Dict[str, Any]:
        data = self.config.get(section, {})
        return _deepcopy(data) if isinstance(data, dict) else {}

    def set_section(self, section: str, settings: Dict[str, Any]) -> bool:
        try:
            self.config[section] = _deepcopy(settings)
            self.save_config()
            self.logger.info("Set configuration section '%s'", section)
            return True
        except Exception as exc:
            self.logger.error("Error setting section %s: %s", section, exc)
            return False

    def remove_setting(self, section: str, key: str) -> bool:
        try:
            if section in self.config and key in self.config[section]:
                del self.config[section][key]
                self.save_config()
                self.logger.info("Removed configuration %s.%s", section, key)
                return True
            self.logger.warning(
                "Configuration %s.%s not found for removal", section, key
            )
            return False
        except Exception as exc:
            self.logger.error("Error removing %s.%s: %s", section, key, exc)
            return False

    def get_all_settings(self) -> Dict[str, Any]:
        return _deepcopy(self.config)

    def get_config(self) -> Dict[str, Any]:
        flat_config: Dict[str, Any] = {}
        general = self.config.get("general", {})
        flat_config["theme"] = general.get("theme", "light")
        flat_config["language"] = general.get("language", "en")
        flat_config["show_hidden"] = general.get("show_hidden", False)
        for key, value in self.config.items():
            if not isinstance(value, dict):
                flat_config[key] = value
        return flat_config

    def update_config(self, key: str, value: Any) -> None:
        self.config[key] = value
        self.save_config()

    def update_multiple(self, updates: Dict[str, Any]) -> None:
        self.config.update(updates)
        self.save_config()

    def create_backup(self) -> str:
        if not self.config_file.exists():
            self.save_config()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{self.config_file.stem}_backup_{timestamp}.json"
        backup_path = self.config_dir / backup_name
        shutil.copy2(self.config_file, backup_path)
        return str(backup_path)

    def restore_from_backup(self, backup_file: Union[str, Path]) -> None:
        backup_path = Path(backup_file)
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_path}")
        shutil.copy2(backup_path, self.config_file)
        self.load_config()

    def export_config(self, export_path: Union[str, Path]) -> bool:
        try:
            export_file = Path(export_path)
            export_file.parent.mkdir(parents=True, exist_ok=True)
            with open(export_file, "w", encoding="utf-8") as fh:
                json.dump(self.config, fh, indent=2, ensure_ascii=False)
            self.logger.info("Configuration exported to %s", export_file)
            return True
        except Exception as exc:
            self.logger.error("Failed to export configuration: %s", exc)
            return False

    def import_config(self, import_path: Union[str, Path]) -> bool:
        try:
            import_file = Path(import_path)
            if not import_file.exists():
                self.logger.error("Import file not found: %s", import_file)
                return False
            with open(import_file, "r", encoding="utf-8") as fh:
                imported_config = json.load(fh)
            if not isinstance(imported_config, dict):
                self.logger.error("Invalid configuration format")
                return False
            self.config.update(imported_config)
            self._ensure_default_structure()
            self.save_config()
            self.logger.info("Configuration imported from %s", import_file)
            return True
        except Exception as exc:
            self.logger.error("Failed to import configuration: %s", exc)
            return False

    def get_config_info(self) -> Dict[str, Any]:
        modified_at = None
        if self.config_file.exists():
            modified_at = datetime.fromtimestamp(
                self.config_file.stat().st_mtime
            ).isoformat()
        return {
            "config_file": str(self.config_file),
            "config_dir": str(self.config_dir),
            "sections": list(self.config.keys()),
            "total_settings": sum(
                len(value) for value in self.config.values() if isinstance(value, dict)
            ),
            "file_exists": self.config_file.exists(),
            "file_size_bytes": (
                self.config_file.stat().st_size if self.config_file.exists() else 0
            ),
            "modified_at": modified_at,
        }

    # ------------------------------------------------------------------
    # Profile management
    # ------------------------------------------------------------------
    def _ensure_profile_container(self) -> Dict[str, Dict[str, Any]]:
        profiles = self.config.setdefault("profiles", {})
        if not isinstance(profiles, dict):
            profiles = {}
            self.config["profiles"] = profiles
        return profiles

    def _migrate_legacy_profiles(self, module_name: str) -> None:
        legacy_key = f"{module_name}_profiles"
        legacy_data = self.config.get(legacy_key)
        if isinstance(legacy_data, dict) and legacy_data:
            profiles = self._ensure_profile_container()
            module_profiles = profiles.setdefault(module_name, {})
            module_profiles.update(legacy_data)
            del self.config[legacy_key]
            self.logger.info(
                "Migrated legacy profiles for module '%s'",
                module_name,
            )

    def get_profiles(self, module_name: str) -> list[str]:
        profiles = self._ensure_profile_container()
        module_profiles = profiles.get(module_name, {})
        legacy_key = f"{module_name}_profiles"
        legacy_profiles = self.config.get(legacy_key, {})

        names = set()
        if isinstance(module_profiles, dict):
            names.update(module_profiles.keys())
        if isinstance(legacy_profiles, dict):
            names.update(legacy_profiles.keys())
        return sorted(names)

    def save_profile(
        self, profile_name: str, module_name: str, settings: Dict[str, Any]
    ) -> None:
        try:
            profiles = self._ensure_profile_container()
            self._migrate_legacy_profiles(module_name)
            module_profiles = profiles.setdefault(module_name, {})
            module_profiles[profile_name] = settings
            self.save_config()
            self.logger.info(
                "Saved profile %s for module %s", profile_name, module_name
            )
        except Exception as exc:
            self.logger.error(
                "Error saving profile %s for module %s: %s",
                profile_name,
                module_name,
                exc,
                exc_info=True,
            )

    def load_profile(
        self, profile_name: str, module_name: str
    ) -> Optional[Dict[str, Any]]:
        try:
            profiles = self._ensure_profile_container()
            module_profiles = profiles.get(module_name, {})
            if profile_name in module_profiles:
                return _deepcopy(module_profiles[profile_name])
            legacy_key = f"{module_name}_profiles"
            legacy_profiles = self.config.get(legacy_key, {})
            if isinstance(legacy_profiles, dict):
                return _deepcopy(legacy_profiles.get(profile_name))
            return None
        except Exception as exc:
            self.logger.error(
                "Error loading profile %s for module %s: %s",
                profile_name,
                module_name,
                exc,
                exc_info=True,
            )
            return None

    def delete_profile(self, profile_name: str, module_name: str) -> bool:
        try:
            profiles = self._ensure_profile_container()
            module_profiles = profiles.get(module_name, {})
            removed = False
            if profile_name in module_profiles:
                del module_profiles[profile_name]
                removed = True
                if not module_profiles:
                    del profiles[module_name]

            legacy_key = f"{module_name}_profiles"
            legacy_profiles = self.config.get(legacy_key, {})
            legacy_profile_exists = (
                isinstance(legacy_profiles, dict) and profile_name in legacy_profiles
            )
            if legacy_profile_exists:
                del legacy_profiles[profile_name]
                removed = True
                if not legacy_profiles:
                    del self.config[legacy_key]

            if removed:
                self.save_config()
                self.logger.info(
                    "Deleted profile %s from module %s",
                    profile_name,
                    module_name,
                )
            return removed
        except Exception as exc:
            self.logger.error(
                "Error deleting profile %s for module %s: %s",
                profile_name,
                module_name,
                exc,
                exc_info=True,
            )
            return False


_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """Return a shared ``ConfigManager`` instance."""

    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


__all__ = ["ConfigManager", "get_config_manager"]
