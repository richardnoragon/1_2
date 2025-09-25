"""Alert management system for diagnostics monitoring."""

import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable, Set
from dataclasses import dataclass
from enum import Enum

from .platform_detector import get_platform_detector
from .data_collector import DataType, DataPoint
from core.error_handler import error_handler


class AlertLevel(Enum):
    """Enumeration of alert levels."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertStatus(Enum):
    """Enumeration of alert status."""

    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


@dataclass
class AlertRule:
    """Represents an alert rule."""

    rule_id: str
    name: str
    data_type: DataType
    metric_path: str  # e.g., "cpu_percent" or "disks.0.free_space_percent"
    condition: str  # e.g., ">" or "<" or "=="
    threshold_warning: Optional[float] = None
    threshold_critical: Optional[float] = None
    enabled: bool = True
    description: str = ""


@dataclass
class Alert:
    """Represents an alert instance."""

    alert_id: str
    rule_id: str
    level: AlertLevel
    status: AlertStatus
    message: str
    data_type: DataType
    monitor_name: str
    metric_value: float
    threshold_value: float
    created_time: datetime
    acknowledged_time: Optional[datetime] = None
    resolved_time: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class AlertManager:
    """Manages alert rules, generation, and delivery."""

    def __init__(self):
        """Initialize the alert manager."""
        self.logger = logging.getLogger(
            "RFU.DiagnosticsMonitoring.AlertManager"
        )
        self.platform_detector = get_platform_detector()

        # Alert storage
        self._alert_rules: Dict[str, AlertRule] = {}
        self._active_alerts: Dict[str, Alert] = {}
        self._alert_history: List[Alert] = []
        self._max_history_size = 1000
        self._lock = threading.Lock()

        # Alert handlers
        self._alert_handlers: List[Callable[[Alert], None]] = []

        # Suppression tracking
        self._suppressed_alerts: Set[str] = set()
        self._last_alert_times: Dict[str, datetime] = {}
        self._min_alert_interval = timedelta(minutes=5)

        # Load default rules
        self._load_default_rules()

        self.logger.info("Alert manager initialized")

    def add_rule(self, rule: AlertRule) -> bool:
        """Add an alert rule.

        Args:
            rule: Alert rule to add

        Returns:
            bool: True if added successfully, False otherwise
        """
        try:
            with self._lock:
                self._alert_rules[rule.rule_id] = rule

            self.logger.info(f"Added alert rule: {rule.name}")
            return True

        except Exception as e:
            self.logger.error(f"Error adding alert rule: {e}")
            error_handler.handle_error(e, "AlertManager.add_rule")
            return False

    def remove_rule(self, rule_id: str) -> bool:
        """Remove an alert rule.

        Args:
            rule_id: ID of rule to remove

        Returns:
            bool: True if removed successfully, False otherwise
        """
        try:
            with self._lock:
                if rule_id in self._alert_rules:
                    del self._alert_rules[rule_id]
                    self.logger.info(f"Removed alert rule: {rule_id}")
                    return True
                else:
                    self.logger.warning(f"Alert rule not found: {rule_id}")
                    return False

        except Exception as e:
            self.logger.error(f"Error removing alert rule: {e}")
            error_handler.handle_error(e, "AlertManager.remove_rule")
            return False

    def update_rule(self, rule: AlertRule) -> bool:
        """Update an existing alert rule.

        Args:
            rule: Updated alert rule

        Returns:
            bool: True if updated successfully, False otherwise
        """
        try:
            with self._lock:
                if rule.rule_id in self._alert_rules:
                    self._alert_rules[rule.rule_id] = rule
                    self.logger.info(f"Updated alert rule: {rule.name}")
                    return True
                else:
                    self.logger.warning(
                        f"Alert rule not found: {rule.rule_id}"
                    )
                    return False

        except Exception as e:
            self.logger.error(f"Error updating alert rule: {e}")
            error_handler.handle_error(e, "AlertManager.update_rule")
            return False

    def check_data_point(self, data_point: DataPoint) -> List[Alert]:
        """Check a data point against all applicable rules.

        Args:
            data_point: Data point to check

        Returns:
            List of generated alerts
        """
        generated_alerts = []

        try:
            with self._lock:
                rules = [
                    rule
                    for rule in self._alert_rules.values()
                    if rule.enabled and rule.data_type == data_point.data_type
                ]

            for rule in rules:
                alert = self._evaluate_rule(rule, data_point)
                if alert:
                    generated_alerts.append(alert)

        except Exception as e:
            self.logger.error(f"Error checking data point: {e}")
            error_handler.handle_error(e, "AlertManager.check_data_point")

        return generated_alerts

    def _evaluate_rule(
        self, rule: AlertRule, data_point: DataPoint
    ) -> Optional[Alert]:
        """Evaluate a single rule against a data point.

        Args:
            rule: Alert rule to evaluate
            data_point: Data point to check

        Returns:
            Alert if rule is triggered, None otherwise
        """
        try:
            # Extract metric value from data
            metric_value = self._extract_metric_value(
                data_point.data, rule.metric_path
            )

            if metric_value is None:
                return None

            # Check thresholds
            alert_level = None
            threshold_value = None

            if rule.threshold_critical is not None and self._check_condition(
                metric_value, rule.condition, rule.threshold_critical
            ):
                alert_level = AlertLevel.CRITICAL
                threshold_value = rule.threshold_critical
            elif rule.threshold_warning is not None and self._check_condition(
                metric_value, rule.condition, rule.threshold_warning
            ):
                alert_level = AlertLevel.WARNING
                threshold_value = rule.threshold_warning

            if alert_level is None:
                # Check if we need to resolve an existing alert
                self._check_alert_resolution(rule.rule_id, metric_value, rule)
                return None

            # Check if alert should be suppressed
            if self._should_suppress_alert(rule.rule_id, alert_level):
                return None

            # Generate alert
            alert_id = f"{rule.rule_id}_{datetime.now().timestamp()}"
            message = self._generate_alert_message(
                rule, metric_value, threshold_value, alert_level
            )

            alert = Alert(
                alert_id=alert_id,
                rule_id=rule.rule_id,
                level=alert_level,
                status=AlertStatus.ACTIVE,
                message=message,
                data_type=data_point.data_type,
                monitor_name=data_point.monitor_name,
                metric_value=metric_value,
                threshold_value=threshold_value,
                created_time=datetime.now(),
                metadata={
                    "rule_name": rule.name,
                    "metric_path": rule.metric_path,
                    "condition": rule.condition,
                },
            )

            # Store alert
            with self._lock:
                self._active_alerts[alert_id] = alert
                self._alert_history.append(alert)

                # Limit history size
                if len(self._alert_history) > self._max_history_size:
                    self._alert_history = self._alert_history[
                        -self._max_history_size :
                    ]

            # Update suppression tracking
            self._last_alert_times[rule.rule_id] = datetime.now()

            # Notify handlers
            self._notify_handlers(alert)

            self.logger.info(f"Generated {alert_level.value} alert: {message}")
            return alert

        except Exception as e:
            self.logger.error(f"Error evaluating rule {rule.rule_id}: {e}")
            return None

    def _extract_metric_value(
        self, data: Dict[str, Any], metric_path: str
    ) -> Optional[float]:
        """Extract a metric value from data using a path.

        Args:
            data: Data dictionary
            metric_path: Path to metric (e.g., "cpu_percent" or
                "disks.0.free_space")

        Returns:
            Metric value or None if not found
        """
        try:
            parts = metric_path.split(".")
            current = data

            for part in parts:
                if isinstance(current, dict):
                    current = current.get(part)
                elif isinstance(current, list):
                    try:
                        index = int(part)
                        current = current[index]
                    except (ValueError, IndexError):
                        return None
                else:
                    return None

                if current is None:
                    return None

            # Convert to float if possible
            if isinstance(current, (int, float)):
                return float(current)
            else:
                return None

        except Exception:
            return None

    def _check_condition(
        self, value: float, condition: str, threshold: float
    ) -> bool:
        """Check if a condition is met.

        Args:
            value: Current value
            condition: Condition operator
            threshold: Threshold value

        Returns:
            bool: True if condition is met
        """
        if condition == ">":
            return value > threshold
        elif condition == ">=":
            return value >= threshold
        elif condition == "<":
            return value < threshold
        elif condition == "<=":
            return value <= threshold
        elif condition == "==":
            return abs(value - threshold) < 0.001  # Float comparison
        elif condition == "!=":
            return abs(value - threshold) >= 0.001
        else:
            return False

    def _should_suppress_alert(self, rule_id: str, level: AlertLevel) -> bool:
        """Check if an alert should be suppressed.

        Args:
            rule_id: Rule ID
            level: Alert level

        Returns:
            bool: True if alert should be suppressed
        """
        # Check if rule is suppressed
        if rule_id in self._suppressed_alerts:
            return True

        # Check minimum interval
        last_time = self._last_alert_times.get(rule_id)
        if last_time:
            time_since_last = datetime.now() - last_time
            if time_since_last < self._min_alert_interval:
                return True

        return False

    def _check_alert_resolution(
        self, rule_id: str, current_value: float, rule: AlertRule
    ) -> None:
        """Check if any active alerts for this rule should be resolved.

        Args:
            rule_id: Rule ID
            current_value: Current metric value
            rule: Alert rule
        """
        with self._lock:
            alerts_to_resolve = []

            for alert in self._active_alerts.values():
                if (
                    alert.rule_id == rule_id
                    and alert.status == AlertStatus.ACTIVE
                ):

                    # Check if value is now within acceptable range
                    if not self._check_condition(
                        current_value, rule.condition, alert.threshold_value
                    ):
                        alerts_to_resolve.append(alert.alert_id)

            # Resolve alerts
            for alert_id in alerts_to_resolve:
                self._resolve_alert(alert_id)

    def _resolve_alert(self, alert_id: str) -> bool:
        """Resolve an active alert.

        Args:
            alert_id: Alert ID to resolve

        Returns:
            bool: True if resolved successfully
        """
        try:
            with self._lock:
                if alert_id in self._active_alerts:
                    alert = self._active_alerts[alert_id]
                    alert.status = AlertStatus.RESOLVED
                    alert.resolved_time = datetime.now()

                    # Remove from active alerts
                    del self._active_alerts[alert_id]

                    self.logger.info(f"Resolved alert: {alert.message}")
                    return True

        except Exception as e:
            self.logger.error(f"Error resolving alert {alert_id}: {e}")

        return False

    def _generate_alert_message(
        self,
        rule: AlertRule,
        value: float,
        threshold: float,
        level: AlertLevel,
    ) -> str:
        """Generate an alert message.

        Args:
            rule: Alert rule
            value: Current value
            threshold: Threshold value
            level: Alert level

        Returns:
            Alert message string
        """
        return (
            f"{level.value.upper()}: {rule.name} - "
            f"{rule.metric_path} is {value:.2f} "
            f"(threshold: {rule.condition} {threshold:.2f})"
        )

    def add_handler(self, handler: Callable[[Alert], None]) -> None:
        """Add an alert handler.

        Args:
            handler: Function to call when alerts are generated
        """
        self._alert_handlers.append(handler)
        self.logger.debug("Added alert handler")

    def _notify_handlers(self, alert: Alert) -> None:
        """Notify all alert handlers.

        Args:
            alert: Alert to send to handlers
        """
        for handler in self._alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                self.logger.error(f"Error in alert handler: {e}")

    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert.

        Args:
            alert_id: Alert ID to acknowledge

        Returns:
            bool: True if acknowledged successfully
        """
        try:
            with self._lock:
                if alert_id in self._active_alerts:
                    alert = self._active_alerts[alert_id]
                    alert.status = AlertStatus.ACKNOWLEDGED
                    alert.acknowledged_time = datetime.now()

                    self.logger.info(f"Acknowledged alert: {alert.message}")
                    return True

        except Exception as e:
            self.logger.error(f"Error acknowledging alert {alert_id}: {e}")

        return False

    def suppress_rule(
        self, rule_id: str, duration: Optional[timedelta] = None
    ) -> bool:
        """Suppress alerts for a rule.

        Args:
            rule_id: Rule ID to suppress
            duration: Duration to suppress (None for indefinite)

        Returns:
            bool: True if suppressed successfully
        """
        try:
            self._suppressed_alerts.add(rule_id)

            if duration:
                # Schedule unsuppression (simplified - in real implementation
                # you'd want a proper scheduler)
                threading.Timer(
                    duration.total_seconds(),
                    lambda: self._suppressed_alerts.discard(rule_id),
                ).start()

            self.logger.info(f"Suppressed rule: {rule_id}")
            return True

        except Exception as e:
            self.logger.error(f"Error suppressing rule {rule_id}: {e}")
            return False

    def unsuppress_rule(self, rule_id: str) -> bool:
        """Unsuppress alerts for a rule.

        Args:
            rule_id: Rule ID to unsuppress

        Returns:
            bool: True if unsuppressed successfully
        """
        try:
            self._suppressed_alerts.discard(rule_id)
            self.logger.info(f"Unsuppressed rule: {rule_id}")
            return True

        except Exception as e:
            self.logger.error(f"Error unsuppressing rule {rule_id}: {e}")
            return False

    def get_active_alerts(
        self,
        level: Optional[AlertLevel] = None,
        data_type: Optional[DataType] = None,
    ) -> List[Alert]:
        """Get active alerts with optional filtering.

        Args:
            level: Filter by alert level
            data_type: Filter by data type

        Returns:
            List of active alerts
        """
        with self._lock:
            alerts = list(self._active_alerts.values())

        # Apply filters
        if level:
            alerts = [alert for alert in alerts if alert.level == level]
        if data_type:
            alerts = [
                alert for alert in alerts if alert.data_type == data_type
            ]

        return alerts

    def get_alert_history(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> List[Alert]:
        """Get alert history with optional filtering.

        Args:
            start_time: Filter by start time
            end_time: Filter by end time
            limit: Limit number of results

        Returns:
            List of historical alerts
        """
        with self._lock:
            alerts = self._alert_history.copy()

        # Apply time filters
        if start_time or end_time:
            filtered_alerts = []
            for alert in alerts:
                if start_time and alert.created_time < start_time:
                    continue
                if end_time and alert.created_time > end_time:
                    continue
                filtered_alerts.append(alert)
            alerts = filtered_alerts

        # Apply limit
        if limit:
            alerts = alerts[-limit:]

        return alerts

    def get_rules(self) -> List[AlertRule]:
        """Get all alert rules.

        Returns:
            List of alert rules
        """
        with self._lock:
            return list(self._alert_rules.values())

    def _load_default_rules(self) -> None:
        """Load default alert rules."""
        default_rules = [
            # Disk space rules
            AlertRule(
                rule_id="disk_space_warning",
                name="Disk Space Warning",
                data_type=DataType.DISK_HEALTH,
                metric_path="free_space_percent",
                condition="<",
                threshold_warning=20.0,
                threshold_critical=10.0,
                description="Alert when disk space is low",
            ),
            # CPU usage rules
            AlertRule(
                rule_id="cpu_usage_high",
                name="High CPU Usage",
                data_type=DataType.PERFORMANCE,
                metric_path="cpu_percent",
                condition=">",
                threshold_warning=80.0,
                threshold_critical=95.0,
                description="Alert when CPU usage is high",
            ),
            # Memory usage rules
            AlertRule(
                rule_id="memory_usage_high",
                name="High Memory Usage",
                data_type=DataType.PERFORMANCE,
                metric_path="memory_percent",
                condition=">",
                threshold_warning=85.0,
                threshold_critical=95.0,
                description="Alert when memory usage is high",
            ),
            # Battery health rules
            AlertRule(
                rule_id="battery_health_low",
                name="Low Battery Health",
                data_type=DataType.BATTERY,
                metric_path="health_percent",
                condition="<",
                threshold_warning=80.0,
                threshold_critical=60.0,
                description="Alert when battery health is low",
            ),
        ]

        for rule in default_rules:
            self.add_rule(rule)

        self.logger.info(f"Loaded {len(default_rules)} default alert rules")

    def get_statistics(self) -> Dict[str, Any]:
        """Get alert manager statistics.

        Returns:
            Dict containing statistics
        """
        with self._lock:
            active_count = len(self._active_alerts)
            total_rules = len(self._alert_rules)
            enabled_rules = sum(
                1 for rule in self._alert_rules.values() if rule.enabled
            )
            suppressed_rules = len(self._suppressed_alerts)

            # Count alerts by level
            level_counts = {}
            for alert in self._active_alerts.values():
                level = alert.level.value
                level_counts[level] = level_counts.get(level, 0) + 1

        return {
            "active_alerts": active_count,
            "total_rules": total_rules,
            "enabled_rules": enabled_rules,
            "suppressed_rules": suppressed_rules,
            "alert_history_size": len(self._alert_history),
            "alerts_by_level": level_counts,
            "platform": self.platform_detector.platform.value,
        }


# Global alert manager instance
_alert_manager: Optional[AlertManager] = None


def get_alert_manager() -> AlertManager:
    """Get the global alert manager instance.

    Returns:
        AlertManager: The alert manager instance
    """
    global _alert_manager
    if _alert_manager is None:
        _alert_manager = AlertManager()
    return _alert_manager
