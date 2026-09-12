"""Legacy compatibility shim for the consolidated configuration manager."""

from src.config.config_manager import ConfigManager, get_config_manager

__all__ = ["ConfigManager", "get_config_manager"]
