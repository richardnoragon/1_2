"""Configuration templates and integration for network connectivity tools."""

from .default_settings import get_default_config, validate_config
from .tool_profiles import get_tool_profiles, create_custom_profile
from .config_integration import (
    NetworkConfigManager,
    get_network_config_manager,
    get_tool_config,
    set_tool_config,
)

__all__ = [
    "get_default_config",
    "validate_config",
    "get_tool_profiles",
    "create_custom_profile",
    "NetworkConfigManager",
    "get_network_config_manager",
    "get_tool_config",
    "set_tool_config",
]
