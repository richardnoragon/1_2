"""
Enhanced Configuration Manager with Qt Object Serialization

This module provides enhanced configuration management that properly handles
Qt objects and binary data serialization, preventing JSON serialization errors.

Key Features:
1. Custom JSON encoders for Qt objects
2. Fallback serialization mechanisms
3. Configuration validation and recovery
4. Safe configuration operations with error handling

Author: RFU Development Team
Version: 2.0.0 (Enhanced with Qt Object Support)
"""

import base64
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Union

try:
    from PyQt5.QtCore import (
        QByteArray,
        QPoint,
        QRect,
        QSettings,
        QSize,
        QVariant,
    )
    from PyQt5.QtGui import QColor, QFont

    QT_AVAILABLE = True
except ImportError:
    QT_AVAILABLE = False

    # Mock classes for testing
    class QByteArray:
        def data(self):
            return b""

    class QVariant:
        def value(self):
            return None

    class QRect:
        def __init__(self, *args):
            pass

    class QSize:
        def __init__(self, *args):
            pass

    class QPoint:
        def __init__(self, *args):
            pass

    class QColor:
        def __init__(self, *args):
            pass

    class QFont:
        def __init__(self, *args):
            pass


class QtObjectSerializationError(Exception):
    """Exception raised when Qt object serialization fails."""

    pass


class EnhancedJSONEncoder(json.JSONEncoder):
    """
    Enhanced JSON encoder that handles Qt objects and other complex types.

    Supported Qt Types:
    - QByteArray: Converted to base64 string
    - QRect, QSize, QPoint: Converted to coordinate dictionaries
    - QColor: Converted to RGBA values
    - QFont: Converted to font descriptor
    - QVariant: Converted to underlying value
    """

    def default(self, obj: Any) -> Any:
        """
        Convert Qt objects to JSON-serializable format.

        Args:
            obj: Object to serialize

        Returns:
            Any: JSON-serializable representation
        """
        try:
            # Handle QByteArray
            if QT_AVAILABLE and isinstance(obj, QByteArray):
                return {
                    "__qt_type__": "QByteArray",
                    "data": base64.b64encode(obj.data()).decode("utf-8"),
                }

            # Handle QRect
            if (
                QT_AVAILABLE
                and hasattr(obj, "x")
                and hasattr(obj, "y")
                and hasattr(obj, "width")
                and hasattr(obj, "height")
            ):
                return {
                    "__qt_type__": "QRect",
                    "x": obj.x(),
                    "y": obj.y(),
                    "width": obj.width(),
                    "height": obj.height(),
                }

            # Handle QSize
            if (
                QT_AVAILABLE
                and hasattr(obj, "width")
                and hasattr(obj, "height")
                and not hasattr(obj, "x")
            ):
                return {
                    "__qt_type__": "QSize",
                    "width": obj.width(),
                    "height": obj.height(),
                }

            # Handle QPoint
            if (
                QT_AVAILABLE
                and hasattr(obj, "x")
                and hasattr(obj, "y")
                and not hasattr(obj, "width")
            ):
                return {"__qt_type__": "QPoint", "x": obj.x(), "y": obj.y()}

            # Handle QColor
            if (
                QT_AVAILABLE
                and hasattr(obj, "red")
                and hasattr(obj, "green")
                and hasattr(obj, "blue")
            ):
                return {
                    "__qt_type__": "QColor",
                    "red": obj.red(),
                    "green": obj.green(),
                    "blue": obj.blue(),
                    "alpha": obj.alpha() if hasattr(obj, "alpha") else 255,
                }

            # Handle QFont
            if (
                QT_AVAILABLE
                and hasattr(obj, "family")
                and hasattr(obj, "pointSize")
            ):
                return {
                    "__qt_type__": "QFont",
                    "family": obj.family(),
                    "pointSize": obj.pointSize(),
                    "bold": obj.bold() if hasattr(obj, "bold") else False,
                    "italic": (
                        obj.italic() if hasattr(obj, "italic") else False
                    ),
                }

            # Handle QVariant
            if QT_AVAILABLE and isinstance(obj, QVariant):
                return {
                    "__qt_type__": "QVariant",
                    "value": (
                        self.default(obj.value())
                        if obj.value() is not None
                        else None
                    ),
                }

            # Handle datetime objects
            if isinstance(obj, datetime):
                return {"__datetime__": True, "isoformat": obj.isoformat()}

            # Handle bytes
            if isinstance(obj, bytes):
                return {
                    "__bytes__": True,
                    "data": base64.b64encode(obj).decode("utf-8"),
                }

            # Handle Path objects
            if isinstance(obj, Path):
                return {"__path__": True, "path": str(obj)}

            # Fallback to string representation for unknown objects
            return {
                "__unknown_type__": type(obj).__name__,
                "string_repr": str(obj),
            }

        except Exception as e:
            # Last resort: convert to string
            return f"<Serialization Error: {type(obj).__name__}: {str(e)}>"


def enhanced_json_decoder(dct: Dict[str, Any]) -> Any:
    """
    Decode JSON objects back to their original types.

    Args:
        dct: Dictionary to decode

    Returns:
        Any: Decoded object
    """
    try:
        if "__qt_type__" in dct:
            qt_type = dct["__qt_type__"]

            if qt_type == "QByteArray" and QT_AVAILABLE:
                data = base64.b64decode(dct["data"].encode("utf-8"))
                return QByteArray(data)

            elif qt_type == "QRect" and QT_AVAILABLE:
                from PyQt5.QtCore import QRect

                return QRect(dct["x"], dct["y"], dct["width"], dct["height"])

            elif qt_type == "QSize" and QT_AVAILABLE:
                from PyQt5.QtCore import QSize

                return QSize(dct["width"], dct["height"])

            elif qt_type == "QPoint" and QT_AVAILABLE:
                from PyQt5.QtCore import QPoint

                return QPoint(dct["x"], dct["y"])

            elif qt_type == "QColor" and QT_AVAILABLE:
                from PyQt5.QtGui import QColor

                return QColor(
                    dct["red"],
                    dct["green"],
                    dct["blue"],
                    dct.get("alpha", 255),
                )

            elif qt_type == "QFont" and QT_AVAILABLE:
                from PyQt5.QtGui import QFont

                font = QFont(dct["family"], dct["pointSize"])
                if dct.get("bold"):
                    font.setBold(True)
                if dct.get("italic"):
                    font.setItalic(True)
                return font

            elif qt_type == "QVariant" and QT_AVAILABLE:
                from PyQt5.QtCore import QVariant

                return QVariant(dct["value"])

        elif "__datetime__" in dct:
            return datetime.fromisoformat(dct["isoformat"])

        elif "__bytes__" in dct:
            return base64.b64decode(dct["data"].encode("utf-8"))

        elif "__path__" in dct:
            return Path(dct["path"])

        elif "__unknown_type__" in dct:
            # Return as string representation for unknown types
            return dct["string_repr"]

        return dct

    except Exception as e:
        # Return original dict if decoding fails
        return dct


class EnhancedConfigurationManager:
    """
    Enhanced configuration manager with Qt object serialization support.

    Features:
    - Safe Qt object serialization/deserialization
    - Configuration validation and recovery
    - Fallback mechanisms for serialization failures
    - Comprehensive error handling
    - Configuration backup and restore
    """

    def __init__(self, config_file: Union[str, Path] = None):
        """
        Initialize enhanced configuration manager.

        Args:
            config_file: Path to configuration file
        """
        self.logger = logging.getLogger(__name__)
        self.config_file = (
            Path(config_file)
            if config_file
            else Path("config/enhanced_config.json")
        )
        self.config_data: Dict[str, Any] = {}
        self.backup_config: Dict[str, Any] = {}
        self._load_config()

    def _load_config(self):
        """Load configuration from file with error recovery."""
        try:
            if self.config_file.exists():
                with open(self.config_file, "r", encoding="utf-8") as f:
                    self.config_data = json.load(
                        f, object_hook=enhanced_json_decoder
                    )

                # Create backup of loaded config
                self.backup_config = self.config_data.copy()
                self.logger.info(
                    f"Loaded configuration from {self.config_file}"
                )
            else:
                self.config_data = {}
                self.logger.info(
                    f"No existing configuration found, using defaults"
                )

        except json.JSONDecodeError as e:
            self.logger.error(f"JSON decode error in config file: {e}")
            self._handle_corrupt_config()

        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            self._handle_corrupt_config()

    def _handle_corrupt_config(self):
        """Handle corrupt configuration file."""
        try:
            # Try to backup corrupt file
            if self.config_file.exists():
                backup_path = self.config_file.with_suffix(".corrupt.backup")
                self.config_file.rename(backup_path)
                self.logger.warning(
                    f"Backed up corrupt config to {backup_path}"
                )

            # Initialize with defaults
            self.config_data = {}
            self.backup_config = {}

        except Exception as e:
            self.logger.error(f"Failed to handle corrupt config: {e}")

    def get_setting(self, section: str, key: str, default: Any = None) -> Any:
        """
        Get configuration setting with safe access.

        Args:
            section: Configuration section
            key: Setting key
            default: Default value if not found

        Returns:
            Any: Configuration value or default
        """
        try:
            return self.config_data.get(section, {}).get(key, default)
        except Exception as e:
            self.logger.error(f"Failed to get setting {section}.{key}: {e}")
            return default

    def set_setting(self, section: str, key: str, value: Any) -> bool:
        """
        Set configuration setting with validation.

        Args:
            section: Configuration section
            key: Setting key
            value: Value to set

        Returns:
            bool: True if setting was saved successfully
        """
        try:
            # Ensure section exists
            if section not in self.config_data:
                self.config_data[section] = {}

            # Set the value
            self.config_data[section][key] = value

            # Save configuration
            return self.save_config()

        except Exception as e:
            self.logger.error(f"Failed to set setting {section}.{key}: {e}")
            return False

    def save_config(self) -> bool:
        """
        Save configuration to file with Qt object support.

        Returns:
            bool: True if saved successfully
        """
        try:
            # Ensure directory exists
            self.config_file.parent.mkdir(parents=True, exist_ok=True)

            # Write configuration with enhanced encoder
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(
                    self.config_data,
                    f,
                    cls=EnhancedJSONEncoder,
                    indent=2,
                    ensure_ascii=False,
                )

            self.logger.debug(f"Saved configuration to {self.config_file}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
            return self._fallback_save()

    def _fallback_save(self) -> bool:
        """
        Fallback save method with simplified serialization.

        Returns:
            bool: True if fallback save succeeded
        """
        try:
            # Create a simplified version of config data
            simplified_config = self._simplify_config_data(self.config_data)

            # Try to save simplified version
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(simplified_config, f, indent=2, ensure_ascii=False)

            self.logger.warning(f"Used fallback save for configuration")
            return True

        except Exception as e:
            self.logger.error(f"Fallback save also failed: {e}")
            return False

    def _simplify_config_data(self, data: Any) -> Any:
        """
        Simplify configuration data by converting complex objects to strings.

        Args:
            data: Data to simplify

        Returns:
            Any: Simplified data
        """
        try:
            if isinstance(data, dict):
                return {
                    k: self._simplify_config_data(v) for k, v in data.items()
                }
            elif isinstance(data, list):
                return [self._simplify_config_data(item) for item in data]
            elif isinstance(data, (str, int, float, bool)) or data is None:
                return data
            else:
                # Convert complex objects to string representation
                return str(data)

        except Exception as e:
            self.logger.warning(f"Failed to simplify data: {e}")
            return str(data)

    def validate_config(self) -> Dict[str, Any]:
        """
        Validate configuration and return validation results.

        Returns:
            Dict: Validation results
        """
        validation_results = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "corrected_items": 0,
        }

        try:
            # Check for serialization issues by attempting to serialize
            test_json = json.dumps(self.config_data, cls=EnhancedJSONEncoder)

            # Try to deserialize
            json.loads(test_json, object_hook=enhanced_json_decoder)

            validation_results["is_valid"] = True

        except Exception as e:
            validation_results["is_valid"] = False
            validation_results["errors"].append(
                f"Serialization test failed: {e}"
            )

            # Attempt to fix by simplifying
            try:
                simplified = self._simplify_config_data(self.config_data)
                json.dumps(simplified)
                validation_results["warnings"].append(
                    "Configuration can be saved with simplification"
                )
                validation_results["corrected_items"] = 1
            except Exception as fix_error:
                validation_results["errors"].append(
                    f"Cannot fix configuration: {fix_error}"
                )

        return validation_results

    def restore_backup(self) -> bool:
        """
        Restore configuration from backup.

        Returns:
            bool: True if restored successfully
        """
        try:
            if not self.backup_config:
                self.logger.warning("No backup configuration available")
                return False

            self.config_data = self.backup_config.copy()
            return self.save_config()

        except Exception as e:
            self.logger.error(f"Failed to restore backup: {e}")
            return False

    def create_backup(self) -> bool:
        """
        Create backup of current configuration.

        Returns:
            bool: True if backup created successfully
        """
        try:
            backup_path = self.config_file.with_suffix(".backup")
            with open(backup_path, "w", encoding="utf-8") as f:
                json.dump(
                    self.config_data,
                    f,
                    cls=EnhancedJSONEncoder,
                    indent=2,
                    ensure_ascii=False,
                )

            self.logger.info(f"Created configuration backup at {backup_path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to create backup: {e}")
            return False

    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get entire configuration section.

        Args:
            section: Section name

        Returns:
            Dict: Section data
        """
        return self.config_data.get(section, {})

    def get_all_settings(self) -> Dict[str, Any]:
        """
        Get all configuration settings.

        Returns:
            Dict: All configuration data
        """
        return self.config_data.copy()

    def clear_section(self, section: str) -> bool:
        """
        Clear entire configuration section.

        Args:
            section: Section to clear

        Returns:
            bool: True if cleared successfully
        """
        try:
            if section in self.config_data:
                del self.config_data[section]
                return self.save_config()
            return True

        except Exception as e:
            self.logger.error(f"Failed to clear section {section}: {e}")
            return False


# Global instance for application-wide use
_global_config_manager: Optional[EnhancedConfigurationManager] = None


def get_enhanced_config_manager(
    config_file: Union[str, Path] = None,
) -> EnhancedConfigurationManager:
    """Get the global enhanced configuration manager instance."""
    global _global_config_manager
    if _global_config_manager is None:
        _global_config_manager = EnhancedConfigurationManager(config_file)
    return _global_config_manager


# Testing and validation
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    # Test enhanced configuration manager
    config_manager = EnhancedConfigurationManager("test_config.json")

    # Test Qt object serialization if available
    if QT_AVAILABLE:
        from PyQt5.QtCore import QByteArray, QRect
        from PyQt5.QtGui import QColor

        # Test saving Qt objects
        config_manager.set_setting(
            "qt_objects", "byte_array", QByteArray(b"test data")
        )
        config_manager.set_setting(
            "qt_objects", "rect", QRect(10, 20, 100, 200)
        )
        config_manager.set_setting("qt_objects", "color", QColor(255, 128, 64))

    # Test regular objects
    config_manager.set_setting("app", "window_size", [800, 600])
    config_manager.set_setting("app", "last_opened", datetime.now())

    # Validate configuration
    validation = config_manager.validate_config()
    print(f"Configuration validation: {validation}")

    # Test backup and restore
    config_manager.create_backup()

    print("Enhanced configuration manager test completed")
