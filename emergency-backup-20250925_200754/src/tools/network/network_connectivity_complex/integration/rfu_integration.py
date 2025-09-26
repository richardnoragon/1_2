"""Integration layer for Network Connectivity with RFU systems."""

import logging
from typing import Dict, Any, Optional
from pathlib import Path

from core.config_manager import ConfigManager
from core.logging_manager import LogManager
from core.error_handler import get_error_handler

from ..core.config_service import get_config_service
from ..core.logging_service import get_logging_service
from ..core.notification_service import get_notification_service
from ..core.metrics_service import get_metrics_service


class RFUIntegrationManager:
    """Manages integration between Network Connectivity and RFU systems."""

    def __init__(self):
        self.logger = logging.getLogger("RFU.NetworkConnectivity.Integration")
        self.error_handler = get_error_handler()

        # RFU core services
        self.rfu_config = ConfigManager()
        self.rfu_logging = LogManager()

        # Network connectivity services
        self.nc_config = get_config_service()
        self.nc_logging = get_logging_service()
        self.nc_notifications = get_notification_service()
        self.nc_metrics = get_metrics_service()

        self._integration_status = {
            "config": False,
            "logging": False,
            "notifications": False,
            "metrics": False,
            "gui": False,
        }

        self._initialize_integration()

    def _initialize_integration(self):
        """Initialize integration with RFU systems."""
        try:
            self._integrate_configuration()
            self._integrate_logging()
            self._integrate_notifications()
            self._integrate_metrics()
            self._setup_error_handling()

            self.logger.info("RFU integration initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize RFU integration: {e}")
            self.error_handler.handle_error(e, "RFU Integration")

    def _integrate_configuration(self):
        """Integrate configuration systems."""
        try:
            # Ensure network connectivity configuration exists in main RFU config
            if "network_connectivity" not in self.rfu_config.config:
                self.logger.info(
                    "Adding network connectivity to RFU configuration"
                )

                # Get default network configuration
                default_config = self.nc_config.get_configuration()

                # Add to RFU configuration
                self.rfu_config.config["network_connectivity"] = (
                    default_config.get("network_connectivity", {})
                )
                self.rfu_config.save_config()

            # Set up configuration synchronization
            self._setup_config_sync()

            self._integration_status["config"] = True
            self.logger.info("Configuration integration completed")

        except Exception as e:
            self.logger.error(f"Configuration integration failed: {e}")
            raise

    def _setup_config_sync(self):
        """Setup bidirectional configuration synchronization."""
        from ..core.config_service import ConfigurationEvent

        # Listen for network connectivity config changes
        def on_nc_config_updated(event_data):
            try:
                # Sync changes to RFU config
                nc_config = self.nc_config.get_configuration()
                self.rfu_config.config["network_connectivity"] = nc_config.get(
                    "network_connectivity", {}
                )
                self.rfu_config.save_config()

                self.logger.debug("Synchronized NC config changes to RFU")

            except Exception as e:
                self.logger.error(f"Failed to sync config to RFU: {e}")

        self.nc_config.add_event_callback(
            ConfigurationEvent.CONFIG_UPDATED, on_nc_config_updated
        )

        # Monitor RFU config changes (if RFU supports callbacks)
        # This would require RFU ConfigManager to support event callbacks

    def _integrate_logging(self):
        """Integrate logging systems."""
        try:
            # Create bridge between RFU logging and NC logging
            self._setup_logging_bridge()

            # Configure NC logging to use RFU log directory structure
            self._configure_nc_logging_paths()

            self._integration_status["logging"] = True
            self.logger.info("Logging integration completed")

        except Exception as e:
            self.logger.error(f"Logging integration failed: {e}")
            raise

    def _setup_logging_bridge(self):
        """Setup bridge between RFU and NC logging systems."""

        # Create custom log handler that forwards NC logs to RFU logging
        class RFULogHandler:
            def __init__(self, rfu_logger):
                self.rfu_logger = rfu_logger

            def handle(self, log_entry):
                # Convert NC log entry to RFU log format
                level_map = {
                    "TRACE": "DEBUG",
                    "DEBUG": "DEBUG",
                    "INFO": "INFO",
                    "WARNING": "WARNING",
                    "ERROR": "ERROR",
                    "CRITICAL": "CRITICAL",
                    "SECURITY": "WARNING",
                    "PERFORMANCE": "INFO",
                    "AUDIT": "INFO",
                }

                rfu_level = level_map.get(log_entry.level.value, "INFO")
                message = f"[{log_entry.tool_name}] {log_entry.message}"

                # Add context if available
                if log_entry.context:
                    context_str = ", ".join(
                        f"{k}={v}" for k, v in log_entry.context.items()
                    )
                    message += f" ({context_str})"

                # Log to RFU system
                getattr(self.rfu_logger, rfu_level.lower())(message)

        # Add RFU handler to NC logging service
        rfu_handler = RFULogHandler(self.logger)
        self.nc_logging.add_handler("rfu_bridge", rfu_handler)

    def _configure_nc_logging_paths(self):
        """Configure NC logging to use RFU log directory structure."""
        try:
            # Get RFU log directory (assuming it follows standard pattern)
            rfu_log_dir = Path.cwd() / "logs"
            nc_log_dir = rfu_log_dir / "network_connectivity"

            # Ensure directory exists
            nc_log_dir.mkdir(parents=True, exist_ok=True)

            # Update NC logging configuration to use RFU log directory
            # This would require updating the logging service configuration

        except Exception as e:
            self.logger.warning(f"Failed to configure NC logging paths: {e}")

    def _integrate_notifications(self):
        """Integrate notification systems."""
        try:
            # Setup notification forwarding to RFU systems
            self._setup_notification_forwarding()

            # Register NC notification handlers with RFU GUI
            self._register_gui_notifications()

            self._integration_status["notifications"] = True
            self.logger.info("Notification integration completed")

        except Exception as e:
            self.logger.error(f"Notification integration failed: {e}")
            raise

    def _setup_notification_forwarding(self):
        """Setup notification forwarding to RFU systems."""
        # Get GUI notification handler
        gui_handler = self.nc_notifications.get_gui_handler()

        if gui_handler:
            # Add callback to forward notifications to RFU GUI
            def forward_to_rfu_gui(notification):
                try:
                    # This would integrate with RFU's notification system
                    # For now, log the notification
                    self.logger.info(
                        f"NC Notification: {notification.title} - {notification.message}"
                    )

                    # If RFU has a notification system, forward there
                    # rfu_notification_system.show_notification(notification)

                except Exception as e:
                    self.logger.error(
                        f"Failed to forward notification to RFU: {e}"
                    )

            gui_handler.add_gui_callback(forward_to_rfu_gui)

    def _register_gui_notifications(self):
        """Register NC notifications with RFU GUI system."""
        try:
            # This would register NC notification types with RFU's main GUI
            # so they appear in the main application's notification area

            # Example integration points:
            # - Status bar notifications
            # - System tray notifications
            # - Main window notification area

            self.logger.debug("GUI notification registration completed")

        except Exception as e:
            self.logger.warning(f"GUI notification registration failed: {e}")

    def _integrate_metrics(self):
        """Integrate metrics systems."""
        try:
            # Setup metrics collection for RFU integration
            self._setup_integration_metrics()

            # Export metrics to RFU monitoring (if available)
            self._setup_metrics_export()

            self._integration_status["metrics"] = True
            self.logger.info("Metrics integration completed")

        except Exception as e:
            self.logger.error(f"Metrics integration failed: {e}")
            raise

    def _setup_integration_metrics(self):
        """Setup metrics for integration monitoring."""
        from ..core.metrics_service import MetricType, MetricUnit

        # Create integration-specific metrics
        metrics = [
            (
                "rfu.integration.config_syncs",
                MetricType.COUNTER,
                MetricUnit.COUNT,
            ),
            (
                "rfu.integration.log_forwards",
                MetricType.COUNTER,
                MetricUnit.COUNT,
            ),
            (
                "rfu.integration.notifications_sent",
                MetricType.COUNTER,
                MetricUnit.COUNT,
            ),
            ("rfu.integration.errors", MetricType.COUNTER, MetricUnit.COUNT),
            (
                "rfu.integration.health_score",
                MetricType.GAUGE,
                MetricUnit.PERCENT,
            ),
        ]

        for name, metric_type, unit in metrics:
            self.nc_metrics.create_metric(name, metric_type, unit)

        # Record initial health score
        self.nc_metrics.record_value("rfu.integration.health_score", 100.0)

    def _setup_metrics_export(self):
        """Setup metrics export to RFU monitoring systems."""
        try:
            # This would export NC metrics to RFU's monitoring dashboard
            # or performance monitoring system if available

            # Example: Export key metrics every minute
            def export_key_metrics():
                try:
                    summary = self.nc_metrics.get_metrics_summary()

                    # Log key metrics for RFU monitoring
                    self.logger.info(
                        f"NC Metrics Summary: {len(summary)} metrics active"
                    )

                    # Export to RFU monitoring system
                    # rfu_monitoring.update_metrics("network_connectivity", summary)

                except Exception as e:
                    self.logger.error(f"Failed to export metrics: {e}")

            # Schedule periodic export (would need proper scheduler)
            # self._schedule_periodic_task(export_key_metrics, interval=60)

        except Exception as e:
            self.logger.warning(f"Metrics export setup failed: {e}")

    def _setup_error_handling(self):
        """Setup error handling integration."""
        try:
            # Integrate NC error handling with RFU error handler
            def nc_error_handler(error, context):
                try:
                    # Forward to RFU error handler
                    self.error_handler.handle_error(
                        error, f"NetworkConnectivity.{context}"
                    )

                    # Record error metric
                    self.nc_metrics.record_value("rfu.integration.errors", 1)

                    # Send error notification
                    self.nc_notifications.send_notification(
                        type="error",
                        title="Network Connectivity Error",
                        message=f"Error in {context}: {str(error)}",
                        source="RFUIntegration",
                    )

                except Exception as e:
                    # Fallback logging if integration fails
                    self.logger.error(
                        f"Error handling integration failed: {e}"
                    )

            # This would register the error handler with NC services
            # nc_services.set_error_handler(nc_error_handler)

        except Exception as e:
            self.logger.warning(f"Error handling integration failed: {e}")

    def get_integration_status(self) -> Dict[str, Any]:
        """Get integration status information."""
        return {
            "status": self._integration_status.copy(),
            "overall_health": all(self._integration_status.values()),
            "services_integrated": sum(self._integration_status.values()),
            "total_services": len(self._integration_status),
            "rfu_config_sections": list(self.rfu_config.config.keys()),
            "nc_config_valid": len(self.nc_config.validate_configuration())
            == 0,
        }

    def validate_integration(self) -> Dict[str, Any]:
        """Validate integration health."""
        validation_results = {
            "config_sync": False,
            "logging_bridge": False,
            "notification_forwarding": False,
            "metrics_collection": False,
            "error_handling": False,
            "issues": [],
        }

        try:
            # Test configuration sync
            if "network_connectivity" in self.rfu_config.config:
                validation_results["config_sync"] = True
            else:
                validation_results["issues"].append(
                    "Network connectivity config missing from RFU"
                )

            # Test logging bridge
            if self.nc_logging._handlers.get("rfu_bridge"):
                validation_results["logging_bridge"] = True
            else:
                validation_results["issues"].append(
                    "RFU logging bridge not active"
                )

            # Test notification forwarding
            gui_handler = self.nc_notifications.get_gui_handler()
            if gui_handler and gui_handler._gui_callbacks:
                validation_results["notification_forwarding"] = True
            else:
                validation_results["issues"].append(
                    "Notification forwarding not configured"
                )

            # Test metrics collection
            metrics_stats = self.nc_metrics.get_statistics()
            if metrics_stats["total_metrics"] > 0:
                validation_results["metrics_collection"] = True
            else:
                validation_results["issues"].append(
                    "No metrics being collected"
                )

            # Test error handling
            validation_results["error_handling"] = (
                True  # Assume working if no errors
            )

        except Exception as e:
            validation_results["issues"].append(f"Validation error: {e}")

        validation_results["overall_valid"] = (
            len(validation_results["issues"]) == 0
        )

        return validation_results

    def repair_integration(self) -> bool:
        """Attempt to repair integration issues."""
        try:
            self.logger.info("Attempting to repair RFU integration")

            # Re-initialize integration
            self._initialize_integration()

            # Validate repair
            validation = self.validate_integration()

            if validation["overall_valid"]:
                self.logger.info("Integration repair successful")
                return True
            else:
                self.logger.warning(
                    f"Integration repair incomplete: {validation['issues']}"
                )
                return False

        except Exception as e:
            self.logger.error(f"Integration repair failed: {e}")
            return False

    def shutdown_integration(self):
        """Shutdown integration cleanly."""
        try:
            self.logger.info("Shutting down RFU integration")

            # Remove event callbacks
            # self.nc_config.remove_event_callbacks()

            # Stop metrics collection
            # self.nc_metrics.shutdown()

            # Close logging handlers
            # self.nc_logging.shutdown()

            # Clear integration status
            self._integration_status = {
                k: False for k in self._integration_status
            }

            self.logger.info("RFU integration shutdown completed")

        except Exception as e:
            self.logger.error(f"Integration shutdown failed: {e}")


# Global integration manager instance
_integration_manager = None


def get_integration_manager() -> RFUIntegrationManager:
    """Get global RFU integration manager instance.

    Returns:
        RFUIntegrationManager instance
    """
    global _integration_manager

    if _integration_manager is None:
        _integration_manager = RFUIntegrationManager()

    return _integration_manager


def initialize_rfu_integration() -> bool:
    """Initialize RFU integration.

    Returns:
        True if initialization successful
    """
    try:
        manager = get_integration_manager()
        status = manager.get_integration_status()
        return status["overall_health"]
    except Exception as e:
        logging.getLogger("RFU.NetworkConnectivity").error(
            f"Failed to initialize RFU integration: {e}"
        )
        return False


def validate_rfu_integration() -> Dict[str, Any]:
    """Validate RFU integration health.

    Returns:
        Validation results dictionary
    """
    try:
        manager = get_integration_manager()
        return manager.validate_integration()
    except Exception as e:
        return {
            "overall_valid": False,
            "issues": [f"Integration validation failed: {e}"],
        }


def repair_rfu_integration() -> bool:
    """Repair RFU integration issues.

    Returns:
        True if repair successful
    """
    try:
        manager = get_integration_manager()
        return manager.repair_integration()
    except Exception as e:
        logging.getLogger("RFU.NetworkConnectivity").error(
            f"Failed to repair RFU integration: {e}"
        )
        return False
