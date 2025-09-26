"""Mock objects for service components."""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from unittest.mock import Mock, MagicMock


class MockConfigService:
    """Mock configuration service for testing."""

    def __init__(self):
        self.config_data = {
            "general": {
                "default_timeout": 5000,
                "max_concurrent_operations": 10,
                "enable_logging": True,
                "log_level": "INFO",
                "enable_notifications": True,
                "notification_sound": True,
            },
            "bandwidth_monitor": {
                "update_interval": 1000,
                "history_size": 100,
                "enable_alerts": True,
                "alert_thresholds": {
                    "upload_speed": 50.0,
                    "download_speed": 100.0,
                },
            },
            "port_scanner": {
                "default_timeout": 3000,
                "max_threads": 50,
                "scan_techniques": ["tcp_connect", "tcp_syn"],
                "common_ports": [22, 23, 25, 53, 80, 110, 143, 443, 993, 995],
            },
            "wifi_analyzer": {
                "scan_interval": 5000,
                "channel_bands": ["2.4GHz", "5GHz"],
                "enable_security_analysis": True,
                "signal_threshold": -70,
            },
            "lan_file_transfer": {
                "discovery_port": 8888,
                "transfer_port_range": [9000, 9100],
                "encryption_enabled": True,
                "authentication_required": True,
                "max_file_size": 1073741824,  # 1GB
            },
        }
        self.profiles = {}
        self.active_profile = None
        self.event_callbacks = {}

    def get_configuration(self, use_cache: bool = True) -> Dict[str, Any]:
        """Get full configuration."""
        return self.config_data.copy()

    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a specific setting."""
        keys = key.split(".")
        current = self.config_data

        try:
            for k in keys:
                current = current[k]
            return current
        except (KeyError, TypeError):
            return default

    def set_setting(self, key: str, value: Any) -> bool:
        """Set a specific setting."""
        keys = key.split(".")
        current = self.config_data

        try:
            for k in keys[:-1]:
                if k not in current:
                    current[k] = {}
                current = current[k]
            current[keys[-1]] = value
            return True
        except (KeyError, TypeError):
            return False

    def update_configuration(
        self, updates: Dict[str, Any], validate: bool = True
    ) -> bool:
        """Update configuration with new values."""
        if validate and not self._validate_config(updates):
            return False

        self._deep_update(self.config_data, updates)
        return True

    def create_profile(
        self,
        name: str,
        description: str = "",
        use_case: str = "",
        settings: Dict[str, Any] = None,
    ):
        """Create a configuration profile."""
        if name in self.profiles:
            return False

        self.profiles[name] = {
            "name": name,
            "description": description,
            "use_case": use_case,
            "settings": settings or {},
            "created_at": datetime.now(),
            "modified_at": datetime.now(),
        }
        return True

    def get_profile(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a configuration profile."""
        return self.profiles.get(name)

    def get_profiles(self) -> List[Dict[str, Any]]:
        """Get all configuration profiles."""
        return list(self.profiles.values())

    def switch_profile(self, name: str) -> bool:
        """Switch to a configuration profile."""
        if name not in self.profiles:
            return False

        self.active_profile = name
        profile = self.profiles[name]
        self.update_configuration(profile["settings"], validate=False)
        return True

    def get_active_profile(self) -> Optional[Dict[str, Any]]:
        """Get the active profile."""
        if self.active_profile:
            return self.profiles.get(self.active_profile)
        return None

    def delete_profile(self, name: str) -> bool:
        """Delete a configuration profile."""
        if name in self.profiles:
            del self.profiles[name]
            if self.active_profile == name:
                self.active_profile = None
            return True
        return False

    def export_configuration(
        self, file_path: str, include_profiles: bool = False
    ) -> bool:
        """Export configuration to file."""
        try:
            export_data = {
                "configuration": self.config_data,
                "export_time": datetime.now().isoformat(),
            }

            if include_profiles:
                export_data["profiles"] = self.profiles

            with open(file_path, "w") as f:
                json.dump(export_data, f, indent=2, default=str)
            return True
        except Exception:
            return False

    def import_configuration(
        self, file_path: str, import_profiles: bool = False
    ) -> bool:
        """Import configuration from file."""
        try:
            with open(file_path, "r") as f:
                import_data = json.load(f)

            if "configuration" in import_data:
                self.config_data = import_data["configuration"]

            if import_profiles and "profiles" in import_data:
                self.profiles.update(import_data["profiles"])

            return True
        except Exception:
            return False

    def validate_configuration(self) -> List[str]:
        """Validate current configuration."""
        return self._validate_config(self.config_data)

    def add_event_callback(self, event_type: str, callback: Callable):
        """Add event callback."""
        if event_type not in self.event_callbacks:
            self.event_callbacks[event_type] = []
        self.event_callbacks[event_type].append(callback)

    def _validate_config(self, config: Dict[str, Any]) -> List[str]:
        """Validate configuration and return errors."""
        errors = []

        # Basic validation rules
        if "general" in config:
            general = config["general"]
            if "default_timeout" in general:
                if general["default_timeout"] < 1000:
                    errors.append("default_timeout must be at least 1000ms")

            if "log_level" in general:
                valid_levels = [
                    "DEBUG",
                    "INFO",
                    "WARNING",
                    "ERROR",
                    "CRITICAL",
                ]
                if general["log_level"] not in valid_levels:
                    errors.append(f"log_level must be one of {valid_levels}")

        return errors

    def _deep_update(self, target: Dict, source: Dict):
        """Deep update dictionary."""
        for key, value in source.items():
            if isinstance(value, dict) and key in target:
                self._deep_update(target[key], value)
            else:
                target[key] = value


class MockLoggingService:
    """Mock logging service for testing."""

    def __init__(self):
        self.log_entries = []
        self.loggers = {}
        self.handlers = []
        self.filters = []
        self.analytics_data = {}

    def get_logger(self, name: str):
        """Get a mock logger."""
        if name not in self.loggers:
            logger = Mock()
            logger.debug = Mock()
            logger.info = Mock()
            logger.warning = Mock()
            logger.error = Mock()
            logger.critical = Mock()
            self.loggers[name] = logger
        return self.loggers[name]

    def log_structured(
        self,
        level: str,
        tool_name: str,
        message: str,
        operation: str = None,
        context: Dict = None,
        metadata: Dict = None,
        **kwargs,
    ):
        """Log structured message."""
        entry = {
            "timestamp": datetime.now(),
            "level": level,
            "tool_name": tool_name,
            "message": message,
            "operation": operation,
            "context": context or {},
            "metadata": metadata or {},
            **kwargs,
        }
        self.log_entries.append(entry)

    def search_logs(self, log_filter: Dict = None) -> List[Dict]:
        """Search log entries."""
        if not log_filter:
            return self.log_entries.copy()

        filtered_logs = []
        for entry in self.log_entries:
            if self._matches_filter(entry, log_filter):
                filtered_logs.append(entry)

        return filtered_logs

    def get_analytics(self) -> Dict[str, Any]:
        """Get log analytics."""
        analytics = {}

        for entry in self.log_entries:
            tool_name = entry.get("tool_name", "Unknown")
            level = entry.get("level", "INFO")

            if tool_name not in analytics:
                analytics[tool_name] = {
                    "total_count": 0,
                    "DEBUG_count": 0,
                    "INFO_count": 0,
                    "WARNING_count": 0,
                    "ERROR_count": 0,
                    "CRITICAL_count": 0,
                }

            analytics[tool_name]["total_count"] += 1
            analytics[tool_name][f"{level}_count"] += 1

        return analytics

    def export_logs(
        self,
        file_path: str,
        log_filter: Dict = None,
        format_type: str = "JSON",
    ) -> bool:
        """Export logs to file."""
        try:
            logs = self.search_logs(log_filter)

            if format_type.upper() == "JSON":
                with open(file_path, "w") as f:
                    json.dump(logs, f, indent=2, default=str)
            elif format_type.upper() == "CSV":
                import csv

                with open(file_path, "w", newline="") as f:
                    if logs:
                        writer = csv.DictWriter(f, fieldnames=logs[0].keys())
                        writer.writeheader()
                        writer.writerows(logs)

            return True
        except Exception:
            return False

    def cleanup_old_logs(self, hours: int):
        """Clean up old log entries."""
        cutoff_time = datetime.now() - datetime.timedelta(hours=hours)
        self.log_entries = [
            entry
            for entry in self.log_entries
            if entry["timestamp"] > cutoff_time
        ]

    def get_log_statistics(self) -> Dict[str, Any]:
        """Get log statistics."""
        if not self.log_entries:
            return {
                "total_entries": 0,
                "level_distribution": {},
                "tool_distribution": {},
                "time_range_seconds": 0,
            }

        level_dist = {}
        tool_dist = {}

        for entry in self.log_entries:
            level = entry.get("level", "INFO")
            tool = entry.get("tool_name", "Unknown")

            level_dist[level] = level_dist.get(level, 0) + 1
            tool_dist[tool] = tool_dist.get(tool, 0) + 1

        timestamps = [entry["timestamp"] for entry in self.log_entries]
        time_range = (max(timestamps) - min(timestamps)).total_seconds()

        return {
            "total_entries": len(self.log_entries),
            "level_distribution": level_dist,
            "tool_distribution": tool_dist,
            "time_range_seconds": time_range,
        }

    def _matches_filter(self, entry: Dict, log_filter: Dict) -> bool:
        """Check if entry matches filter."""
        if "tools" in log_filter:
            if entry.get("tool_name") not in log_filter["tools"]:
                return False

        if "min_level" in log_filter:
            # Simplified level comparison
            levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
            entry_level = entry.get("level", "INFO")
            min_level = log_filter["min_level"]

            if levels.index(entry_level) < levels.index(min_level):
                return False

        if "keywords" in log_filter:
            message = entry.get("message", "")
            if not any(
                keyword in message for keyword in log_filter["keywords"]
            ):
                return False

        return True


class MockNotificationService:
    """Mock notification service for testing."""

    def __init__(self):
        self.notifications = []
        self.rules = []
        self.enabled = True
        self.sound_enabled = True

    def send_notification(
        self,
        title: str,
        message: str,
        notification_type: str = "info",
        priority: str = "normal",
    ) -> bool:
        """Send a notification."""
        if not self.enabled:
            return False

        notification = {
            "timestamp": datetime.now(),
            "title": title,
            "message": message,
            "type": notification_type,
            "priority": priority,
            "id": len(self.notifications),
        }

        self.notifications.append(notification)
        return True

    def add_rule(self, rule: Dict[str, Any]) -> bool:
        """Add notification rule."""
        self.rules.append(rule)
        return True

    def remove_rule(self, rule_id: str) -> bool:
        """Remove notification rule."""
        self.rules = [rule for rule in self.rules if rule.get("id") != rule_id]
        return True

    def get_notifications(self, limit: int = None) -> List[Dict[str, Any]]:
        """Get notifications."""
        if limit:
            return self.notifications[-limit:]
        return self.notifications.copy()

    def clear_notifications(self):
        """Clear all notifications."""
        self.notifications.clear()

    def set_enabled(self, enabled: bool):
        """Enable/disable notifications."""
        self.enabled = enabled

    def set_sound_enabled(self, enabled: bool):
        """Enable/disable notification sounds."""
        self.sound_enabled = enabled


class MockMetricsService:
    """Mock metrics service for testing."""

    def __init__(self):
        self.metrics = {}
        self.collectors = []
        self.enabled = True

    def record_metric(
        self,
        name: str,
        value: float,
        tags: Dict = None,
        timestamp: datetime = None,
    ):
        """Record a metric."""
        if not self.enabled:
            return

        if name not in self.metrics:
            self.metrics[name] = []

        metric_entry = {
            "value": value,
            "tags": tags or {},
            "timestamp": timestamp or datetime.now(),
        }

        self.metrics[name].append(metric_entry)

    def get_metrics(
        self, name: str = None, time_range: tuple = None
    ) -> Dict[str, List]:
        """Get metrics."""
        if name:
            return {name: self.metrics.get(name, [])}

        if time_range:
            start_time, end_time = time_range
            filtered_metrics = {}

            for metric_name, entries in self.metrics.items():
                filtered_entries = [
                    entry
                    for entry in entries
                    if start_time <= entry["timestamp"] <= end_time
                ]
                filtered_metrics[metric_name] = filtered_entries

            return filtered_metrics

        return self.metrics.copy()

    def get_metric_statistics(self, name: str) -> Dict[str, float]:
        """Get statistics for a metric."""
        if name not in self.metrics:
            return {}

        values = [entry["value"] for entry in self.metrics[name]]

        if not values:
            return {}

        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "sum": sum(values),
        }

    def clear_metrics(self, name: str = None):
        """Clear metrics."""
        if name:
            if name in self.metrics:
                del self.metrics[name]
        else:
            self.metrics.clear()

    def add_collector(self, collector):
        """Add metrics collector."""
        self.collectors.append(collector)

    def remove_collector(self, collector):
        """Remove metrics collector."""
        if collector in self.collectors:
            self.collectors.remove(collector)

    def set_enabled(self, enabled: bool):
        """Enable/disable metrics collection."""
        self.enabled = enabled
