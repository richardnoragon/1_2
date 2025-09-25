"""Configuration integration for network connectivity tools with main RFU application."""

import logging
from typing import Dict, Any, Optional
from pathlib import Path

from core.config_manager import ConfigManager
from .default_settings import get_default_config, validate_config, merge_config


class NetworkConfigManager:
    """Manages network connectivity configuration integration."""

    def __init__(self):
        """Initialize network configuration manager."""
        self.config_manager = ConfigManager()
        self.logger = logging.getLogger("RFU.NetworkConnectivity.Config")
        self._ensure_network_config()

    def _ensure_network_config(self):
        """Ensure network connectivity configuration exists in main config."""
        try:
            # Check if network_connectivity section exists
            current_config = self.config_manager.config

            if "network_connectivity" not in current_config:
                self.logger.info(
                    "Adding network connectivity configuration to main config"
                )

                # Get default network config
                default_config = get_default_config()

                # Merge with current config
                merged_config = merge_config(current_config, default_config)

                # Validate the merged config
                validation_errors = validate_config(merged_config)
                if validation_errors:
                    self.logger.warning(
                        f"Configuration validation warnings: {validation_errors}"
                    )

                # Update the main configuration
                self.config_manager.config.update(merged_config)
                self.config_manager.save_config()

                self.logger.info(
                    "Network connectivity configuration added successfully"
                )

        except Exception as e:
            self.logger.error(f"Error ensuring network configuration: {e}")
            # Fall back to default configuration
            self._create_default_network_config()

    def _create_default_network_config(self):
        """Create default network configuration as fallback."""
        try:
            default_config = get_default_config()
            self.config_manager.set_setting(
                "network_connectivity",
                "general",
                default_config["network_connectivity"]["general"],
            )
            self.logger.info(
                "Created default network connectivity configuration"
            )
        except Exception as e:
            self.logger.error(f"Error creating default network config: {e}")

    def get_tool_config(
        self, tool_name: str, key: str = None, default: Any = None
    ) -> Any:
        """Get configuration for a specific network tool.

        Args:
            tool_name: Name of the network tool
            key: Specific configuration key (optional)
            default: Default value if key not found

        Returns:
            Configuration value or entire tool configuration
        """
        try:
            tool_config = self.config_manager.get_setting(
                "network_connectivity", tool_name, {}
            )

            if key is None:
                return tool_config

            return tool_config.get(key, default)

        except Exception as e:
            self.logger.error(
                f"Error getting tool config for {tool_name}: {e}"
            )
            return default

    def set_tool_config(self, tool_name: str, key: str, value: Any) -> bool:
        """Set configuration for a specific network tool.

        Args:
            tool_name: Name of the network tool
            key: Configuration key
            value: Configuration value

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get current tool config
            current_config = self.config_manager.get_setting(
                "network_connectivity", tool_name, {}
            )

            # Update the specific key
            current_config[key] = value

            # Save back to main config
            self.config_manager.set_setting(
                "network_connectivity", tool_name, current_config
            )

            self.logger.debug(f"Updated {tool_name}.{key} = {value}")
            return True

        except Exception as e:
            self.logger.error(
                f"Error setting tool config for {tool_name}: {e}"
            )
            return False

    def get_general_config(self, key: str = None, default: Any = None) -> Any:
        """Get general network connectivity configuration.

        Args:
            key: Specific configuration key (optional)
            default: Default value if key not found

        Returns:
            Configuration value or entire general configuration
        """
        return self.get_tool_config("general", key, default)

    def set_general_config(self, key: str, value: Any) -> bool:
        """Set general network connectivity configuration.

        Args:
            key: Configuration key
            value: Configuration value

        Returns:
            True if successful, False otherwise
        """
        return self.set_tool_config("general", key, value)

    def get_security_config(self, key: str = None, default: Any = None) -> Any:
        """Get security configuration for network tools.

        Args:
            key: Specific configuration key (optional)
            default: Default value if key not found

        Returns:
            Configuration value or entire security configuration
        """
        return self.get_tool_config("security", key, default)

    def get_performance_config(
        self, key: str = None, default: Any = None
    ) -> Any:
        """Get performance configuration for network tools.

        Args:
            key: Specific configuration key (optional)
            default: Default value if key not found

        Returns:
            Configuration value or entire performance configuration
        """
        return self.get_tool_config("performance", key, default)

    def validate_current_config(self) -> list:
        """Validate current network connectivity configuration.

        Returns:
            List of validation errors (empty if valid)
        """
        try:
            current_config = self.config_manager.config
            return validate_config(current_config)
        except Exception as e:
            self.logger.error(f"Error validating configuration: {e}")
            return [f"Validation error: {e}"]

    def reset_tool_config(self, tool_name: str) -> bool:
        """Reset a tool's configuration to defaults.

        Args:
            tool_name: Name of the tool to reset

        Returns:
            True if successful, False otherwise
        """
        try:
            default_config = get_default_config()
            tool_defaults = default_config["network_connectivity"].get(
                tool_name, {}
            )

            if tool_defaults:
                self.config_manager.set_setting(
                    "network_connectivity", tool_name, tool_defaults
                )
                self.logger.info(
                    f"Reset {tool_name} configuration to defaults"
                )
                return True
            else:
                self.logger.warning(
                    f"No default configuration found for {tool_name}"
                )
                return False

        except Exception as e:
            self.logger.error(
                f"Error resetting tool config for {tool_name}: {e}"
            )
            return False

    def export_network_config(self, file_path: str) -> bool:
        """Export network connectivity configuration to file.

        Args:
            file_path: Path to export file

        Returns:
            True if successful, False otherwise
        """
        try:
            import json

            network_config = self.config_manager.get_setting(
                "network_connectivity", {}
            )

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(network_config, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Exported network configuration to {file_path}")
            return True

        except Exception as e:
            self.logger.error(f"Error exporting network config: {e}")
            return False

    def import_network_config(
        self, file_path: str, validate: bool = True
    ) -> bool:
        """Import network connectivity configuration from file.

        Args:
            file_path: Path to import file
            validate: Whether to validate imported configuration

        Returns:
            True if successful, False otherwise
        """
        try:
            import json

            with open(file_path, "r", encoding="utf-8") as f:
                imported_config = json.load(f)

            # Validate if requested
            if validate:
                # Wrap in network_connectivity section for validation
                test_config = {"network_connectivity": imported_config}
                validation_errors = validate_config(test_config)

                if validation_errors:
                    self.logger.error(
                        f"Imported configuration validation failed: {validation_errors}"
                    )
                    return False

            # Import the configuration
            self.config_manager.set_setting(
                "network_connectivity", "", imported_config
            )

            self.logger.info(
                f"Imported network configuration from {file_path}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Error importing network config: {e}")
            return False

    def get_config_summary(self) -> Dict[str, Any]:
        """Get summary of current network connectivity configuration.

        Returns:
            Dictionary with configuration summary
        """
        try:
            network_config = self.config_manager.get_setting(
                "network_connectivity", {}
            )

            summary = {
                "tools_configured": list(network_config.keys()),
                "general_settings": network_config.get("general", {}),
                "security_level": network_config.get("security", {}).get(
                    "security_level", "unknown"
                ),
                "performance_monitoring": network_config.get(
                    "performance", {}
                ).get("enable_performance_monitoring", False),
                "logging_enabled": network_config.get("general", {}).get(
                    "enable_logging", False
                ),
                "config_valid": len(self.validate_current_config()) == 0,
            }

            return summary

        except Exception as e:
            self.logger.error(f"Error getting config summary: {e}")
            return {"error": str(e)}


# Global instance for easy access
_network_config_manager = None


def get_network_config_manager() -> NetworkConfigManager:
    """Get global network configuration manager instance.

    Returns:
        NetworkConfigManager instance
    """
    global _network_config_manager

    if _network_config_manager is None:
        _network_config_manager = NetworkConfigManager()

    return _network_config_manager


def get_tool_config(
    tool_name: str, key: str = None, default: Any = None
) -> Any:
    """Convenience function to get tool configuration.

    Args:
        tool_name: Name of the network tool
        key: Specific configuration key (optional)
        default: Default value if key not found

    Returns:
        Configuration value
    """
    return get_network_config_manager().get_tool_config(
        tool_name, key, default
    )


def set_tool_config(tool_name: str, key: str, value: Any) -> bool:
    """Convenience function to set tool configuration.

    Args:
        tool_name: Name of the network tool
        key: Configuration key
        value: Configuration value

    Returns:
        True if successful, False otherwise
    """
    return get_network_config_manager().set_tool_config(tool_name, key, value)
