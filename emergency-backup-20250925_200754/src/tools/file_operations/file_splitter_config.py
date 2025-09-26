"""
File Splitter Configuration Management

This module provides centralized configuration management for the file splitter
with file_utilities_2 integration, including user preferences, default settings,
and configuration persistence.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path


class FileSplitterConfig:
    """
    Configuration management for file splitter operations.

    Provides centralized configuration with file_utilities_2 integration,
    user preference persistence, and validation.
    """

    # Default configuration values
    DEFAULT_CONFIG = {
        # Core operation settings
        "default_chunk_size": 1024 * 1024,  # 1MB
        "default_output_dir": "",
        "max_chunks": 9999,
        "buffer_size": 1024 * 1024,  # 1MB read/write buffer
        # File handling settings
        "preserve_timestamps": True,
        "verify_integrity": True,
        "auto_cleanup_on_error": True,
        "create_metadata_file": True,
        # UI settings
        "remember_last_directories": True,
        "show_progress_details": True,
        "confirm_large_operations": True,
        "auto_open_output_directory": False,
        # Integration settings
        "enable_hub_reporting": True,
        "detailed_logging": True,
        "log_level": "INFO",
        # Performance settings
        "use_threading": True,
        "thread_priority": "normal",
        "memory_limit_mb": 512,
        # Advanced settings
        "compression_enabled": False,
        "encryption_enabled": False,
        "backup_original": False,
    }

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager.

        Args:
            config_path: Custom path to configuration file (optional)
        """
        self.config_path = config_path or self._get_default_config_path()
        self._config = self.DEFAULT_CONFIG.copy()
        self._user_config = {}
        self.logger = self._setup_logger()

        # Load existing configuration
        self._load_config()

        self.logger.info(f"FileSplitterConfig initialized: {self.config_path}")

    def _setup_logger(self) -> logging.Logger:
        """Setup logger for configuration management."""
        logger = logging.getLogger("file_splitter.config")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def _get_default_config_path(self) -> str:
        """Get default configuration file path."""
        # Use file_utilities_2 configuration directory
        config_dir = os.path.expanduser("~/.file_utilities_2")
        os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, "file_splitter_config.json")

    def _load_config(self):
        """Load configuration from file."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self._user_config = json.load(f)

                # Merge user config with defaults
                self._config.update(self._user_config)

                self.logger.info(
                    f"Configuration loaded: {len(self._user_config)} settings"
                )
            else:
                self.logger.info(
                    "No existing configuration found, using defaults"
                )

        except (json.JSONDecodeError, IOError) as e:
            self.logger.warning(f"Failed to load configuration: {e}")
            self._user_config = {}

    def save_config(self):
        """Save current configuration to file."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)

            # Save only non-default values to keep file clean
            config_to_save = {}
            for key, value in self._config.items():
                if (
                    key not in self.DEFAULT_CONFIG
                    or self.DEFAULT_CONFIG[key] != value
                ):
                    config_to_save[key] = value

            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(config_to_save, f, indent=2, ensure_ascii=False)

            self._user_config = config_to_save
            self.logger.info(
                f"Configuration saved: {len(config_to_save)} settings"
            )

        except (IOError, OSError) as e:
            self.logger.error(f"Failed to save configuration: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        return self._config.get(key, default)

    def set(self, key: str, value: Any, save: bool = True):
        """
        Set configuration value.

        Args:
            key: Configuration key
            value: Configuration value
            save: Whether to save configuration immediately
        """
        old_value = self._config.get(key)
        self._config[key] = value

        if save:
            self.save_config()

        self.logger.debug(
            f"Configuration updated: {key} = {value} (was {old_value})"
        )

    def update(self, config_dict: Dict[str, Any], save: bool = True):
        """
        Update multiple configuration values.

        Args:
            config_dict: Dictionary of configuration updates
            save: Whether to save configuration immediately
        """
        self._config.update(config_dict)

        if save:
            self.save_config()

        self.logger.info(f"Configuration updated: {len(config_dict)} settings")

    def reset_to_defaults(self, save: bool = True):
        """
        Reset configuration to default values.

        Args:
            save: Whether to save configuration immediately
        """
        self._config = self.DEFAULT_CONFIG.copy()
        self._user_config = {}

        if save:
            # Remove config file to reset to defaults
            try:
                if os.path.exists(self.config_path):
                    os.remove(self.config_path)
                self.logger.info("Configuration reset to defaults")
            except OSError as e:
                self.logger.error(f"Failed to remove config file: {e}")

    def get_chunk_size_bytes(self) -> int:
        """Get default chunk size in bytes."""
        return self.get("default_chunk_size", 1024 * 1024)

    def get_buffer_size_bytes(self) -> int:
        """Get buffer size for read/write operations."""
        return self.get("buffer_size", 1024 * 1024)

    def get_max_chunks(self) -> int:
        """Get maximum number of chunks allowed."""
        return self.get("max_chunks", 9999)

    def is_hub_reporting_enabled(self) -> bool:
        """Check if hub reporting is enabled."""
        return self.get("enable_hub_reporting", True)

    def is_integrity_verification_enabled(self) -> bool:
        """Check if integrity verification is enabled."""
        return self.get("verify_integrity", True)

    def should_preserve_timestamps(self) -> bool:
        """Check if file timestamps should be preserved."""
        return self.get("preserve_timestamps", True)

    def should_auto_cleanup_on_error(self) -> bool:
        """Check if auto cleanup on error is enabled."""
        return self.get("auto_cleanup_on_error", True)

    def should_create_metadata_file(self) -> bool:
        """Check if metadata file should be created."""
        return self.get("create_metadata_file", True)

    def get_log_level(self) -> str:
        """Get logging level."""
        return self.get("log_level", "INFO")

    def get_memory_limit_mb(self) -> int:
        """Get memory limit in MB."""
        return self.get("memory_limit_mb", 512)

    def is_threading_enabled(self) -> bool:
        """Check if threading is enabled."""
        return self.get("use_threading", True)

    def get_default_output_directory(self) -> str:
        """Get default output directory."""
        return self.get("default_output_dir", "")

    def set_default_output_directory(self, directory: str):
        """Set default output directory."""
        self.set("default_output_dir", directory)

    def should_remember_directories(self) -> bool:
        """Check if last used directories should be remembered."""
        return self.get("remember_last_directories", True)

    def should_show_progress_details(self) -> bool:
        """Check if detailed progress should be shown."""
        return self.get("show_progress_details", True)

    def should_confirm_large_operations(self) -> bool:
        """Check if large operations should be confirmed."""
        return self.get("confirm_large_operations", True)

    def should_auto_open_output_directory(self) -> bool:
        """Check if output directory should be opened automatically."""
        return self.get("auto_open_output_directory", False)

    def validate_config(self) -> Dict[str, str]:
        """
        Validate current configuration.

        Returns:
            Dictionary of validation errors (empty if valid)
        """
        errors = {}

        # Validate chunk size
        chunk_size = self.get_chunk_size_bytes()
        if chunk_size <= 0:
            errors["default_chunk_size"] = "Chunk size must be positive"
        elif chunk_size > 1024 * 1024 * 1024:  # 1GB
            errors["default_chunk_size"] = "Chunk size too large (max 1GB)"

        # Validate buffer size
        buffer_size = self.get_buffer_size_bytes()
        if buffer_size <= 0:
            errors["buffer_size"] = "Buffer size must be positive"
        elif buffer_size > chunk_size:
            errors["buffer_size"] = "Buffer size cannot exceed chunk size"

        # Validate max chunks
        max_chunks = self.get_max_chunks()
        if max_chunks <= 0:
            errors["max_chunks"] = "Max chunks must be positive"
        elif max_chunks > 99999:
            errors["max_chunks"] = "Max chunks too large (max 99999)"

        # Validate memory limit
        memory_limit = self.get_memory_limit_mb()
        if memory_limit <= 0:
            errors["memory_limit_mb"] = "Memory limit must be positive"
        elif memory_limit > 8192:  # 8GB
            errors["memory_limit_mb"] = "Memory limit too large (max 8GB)"

        # Validate log level
        log_level = self.get_log_level()
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if log_level not in valid_levels:
            errors["log_level"] = (
                f"Invalid log level (must be one of {valid_levels})"
            )

        # Validate output directory if specified
        output_dir = self.get_default_output_directory()
        if output_dir and not os.path.isdir(output_dir):
            errors["default_output_dir"] = (
                "Default output directory does not exist"
            )

        return errors

    def get_config_summary(self) -> Dict[str, Any]:
        """
        Get configuration summary for display.

        Returns:
            Dictionary with configuration summary
        """
        return {
            "config_file": self.config_path,
            "total_settings": len(self._config),
            "custom_settings": len(self._user_config),
            "chunk_size_mb": self.get_chunk_size_bytes() / (1024 * 1024),
            "buffer_size_kb": self.get_buffer_size_bytes() / 1024,
            "max_chunks": self.get_max_chunks(),
            "hub_reporting": self.is_hub_reporting_enabled(),
            "integrity_verification": self.is_integrity_verification_enabled(),
            "threading_enabled": self.is_threading_enabled(),
            "log_level": self.get_log_level(),
        }

    def export_config(self, export_path: str):
        """
        Export configuration to specified file.

        Args:
            export_path: Path to export configuration
        """
        try:
            with open(export_path, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Configuration exported to: {export_path}")
        except (IOError, OSError) as e:
            self.logger.error(f"Failed to export configuration: {e}")
            raise

    def import_config(self, import_path: str, merge: bool = True):
        """
        Import configuration from specified file.

        Args:
            import_path: Path to import configuration from
            merge: Whether to merge with existing config or replace
        """
        try:
            with open(import_path, "r", encoding="utf-8") as f:
                imported_config = json.load(f)

            if merge:
                self._config.update(imported_config)
            else:
                self._config = {**self.DEFAULT_CONFIG, **imported_config}

            self.save_config()
            self.logger.info(f"Configuration imported from: {import_path}")

        except (json.JSONDecodeError, IOError, OSError) as e:
            self.logger.error(f"Failed to import configuration: {e}")
            raise

    def __str__(self) -> str:
        """String representation of configuration."""
        summary = self.get_config_summary()
        return f"FileSplitterConfig({summary['total_settings']} settings, {summary['custom_settings']} custom)"

    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"FileSplitterConfig(config_path='{self.config_path}', settings={len(self._config)})"
