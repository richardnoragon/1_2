"""Notification service for network connectivity tools."""

import threading
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import queue
import json
from pathlib import Path

from .logging_integration import get_network_logging_manager


class NotificationType(Enum):
    """Notification types."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    SUCCESS = "success"
    PERFORMANCE = "performance"
    SECURITY = "security"
    CONFIGURATION = "configuration"


class NotificationPriority(Enum):
    """Notification priorities."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


class NotificationChannel(Enum):
    """Notification delivery channels."""
    GUI = "gui"
    EMAIL = "email"
    LOG = "log"
    SOUND = "sound"
    SYSTEM = "system"
    WEBHOOK = "webhook"


@dataclass
class Notification:
    """Notification data structure."""
    id: str
    type: NotificationType
    priority: NotificationPriority
    title: str
    message: str
    source: str
    timestamp: datetime
    channels: List[NotificationChannel]
    data: Dict[str, Any] = None
    expires_at: Optional[datetime] = None
    acknowledged: bool = False
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    
    def __post_init__(self):
        if self.data is None:
            self.data = {}


class NotificationRule:
    """Rule for automatic notification generation."""
    
    def __init__(self, name: str, condition: Callable[[Dict[str, Any]], bool],
                 notification_template: Dict[str, Any]):
        self.name = name
        self.condition = condition
        self.notification_template = notification_template
        self.enabled = True
        self.last_triggered = None
        self.cooldown_seconds = 60  # Prevent spam
    
    def should_trigger(self, event_data: Dict[str, Any]) -> bool:
        """Check if rule should trigger for given event data."""
        if not self.enabled:
            return False
        
        # Check cooldown
        if (self.last_triggered and 
            (datetime.now() - self.last_triggered).total_seconds() < 
            self.cooldown_seconds):
            return False
        
        return self.condition(event_data)
    
    def create_notification(self, event_data: Dict[str, Any]) -> Notification:
        """Create notification from template and event data."""
        template = self.notification_template.copy()
        
        # Replace placeholders in template
        for key, value in template.items():
            if isinstance(value, str):
                template[key] = value.format(**event_data)
        
        # Create notification
        notification = Notification(
            id=f"{self.name}_{int(time.time())}",
            type=NotificationType(template.get('type', 'info')),
            priority=NotificationPriority(template.get('priority', 2)),
            title=template.get('title', 'Network Notification'),
            message=template.get('message', ''),
            source=template.get('source', 'NetworkConnectivity'),
            timestamp=datetime.now(),
            channels=[NotificationChannel(ch) for ch in 
                     template.get('channels', ['gui'])],
            data=event_data.copy()
        )
        
        self.last_triggered = datetime.now()
        return notification


class NotificationHandler:
    """Base class for notification handlers."""
    
    def __init__(self, name: str, channels: List[NotificationChannel]):
        self.name = name
        self.channels = channels
        self.enabled = True
        self.logger = get_network_logging_manager().get_tool_logger(
            f'NotificationHandler.{name}'
        )
    
    def can_handle(self, notification: Notification) -> bool:
        """Check if this handler can process the notification."""
        return (self.enabled and 
                any(channel in self.channels for channel in notification.channels))
    
    def handle(self, notification: Notification):
        """Handle the notification (override in subclasses)."""
        pass


class GUINotificationHandler(NotificationHandler):
    """GUI notification handler."""
    
    def __init__(self):
        super().__init__("GUI", [NotificationChannel.GUI])
        self._gui_callbacks: List[Callable[[Notification], None]] = []
    
    def add_gui_callback(self, callback: Callable[[Notification], None]):
        """Add GUI callback for notifications."""
        self._gui_callbacks.append(callback)
    
    def remove_gui_callback(self, callback: Callable[[Notification], None]):
        """Remove GUI callback."""
        try:
            self._gui_callbacks.remove(callback)
        except ValueError:
            pass
    
    def handle(self, notification: Notification):
        """Handle GUI notification."""
        for callback in self._gui_callbacks:
            try:
                callback(notification)
            except Exception as e:
                self.logger.error(f"Error in GUI callback: {e}")


class LogNotificationHandler(NotificationHandler):
    """Log-based notification handler."""
    
    def __init__(self):
        super().__init__("Log", [NotificationChannel.LOG])
    
    def handle(self, notification: Notification):
        """Handle log notification."""
        log_level = {
            NotificationType.INFO: 'INFO',
            NotificationType.WARNING: 'WARNING',
            NotificationType.ERROR: 'ERROR',
            NotificationType.CRITICAL: 'CRITICAL',
            NotificationType.SUCCESS: 'INFO',
            NotificationType.PERFORMANCE: 'INFO',
            NotificationType.SECURITY: 'WARNING',
            NotificationType.CONFIGURATION: 'INFO'
        }.get(notification.type, 'INFO')
        
        message = f"NOTIFICATION [{notification.type.value.upper()}]: {notification.title} - {notification.message}"
        
        logger = get_network_logging_manager().get_tool_logger(notification.source)
        getattr(logger, log_level.lower())(message)


class SoundNotificationHandler(NotificationHandler):
    """Sound notification handler."""
    
    def __init__(self):
        super().__init__("Sound", [NotificationChannel.SOUND])
        self._sound_enabled = True
        self._sound_files = {
            NotificationType.INFO: "info.wav",
            NotificationType.WARNING: "warning.wav",
            NotificationType.ERROR: "error.wav",
            NotificationType.CRITICAL: "critical.wav",
            NotificationType.SUCCESS: "success.wav"
        }
    
    def handle(self, notification: Notification):
        """Handle sound notification."""
        if not self._sound_enabled:
            return
        
        try:
            # Platform-specific sound playing would go here
            # For now, just log the sound event
            sound_file = self._sound_files.get(notification.type, "default.wav")
            self.logger.debug(f"Playing notification sound: {sound_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to play notification sound: {e}")


class SystemNotificationHandler(NotificationHandler):
    """System notification handler (OS notifications)."""
    
    def __init__(self):
        super().__init__("System", [NotificationChannel.SYSTEM])
    
    def handle(self, notification: Notification):
        """Handle system notification."""
        try:
            # Platform-specific system notifications would go here
            # For now, just log the system notification
            self.logger.info(
                f"System notification: {notification.title} - {notification.message}"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to send system notification: {e}")


class EmailNotificationHandler(NotificationHandler):
    """Email notification handler."""
    
    def __init__(self, smtp_config: Dict[str, Any] = None):
        super().__init__("Email", [NotificationChannel.EMAIL])
        self.smtp_config = smtp_config or {}
        self._email_enabled = bool(smtp_config)
    
    def handle(self, notification: Notification):
        """Handle email notification."""
        if not self._email_enabled:
            return
        
        try:
            # Email sending implementation would go here
            # For now, just log the email notification
            self.logger.info(
                f"Email notification: {notification.title} - {notification.message}"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to send email notification: {e}")


class WebhookNotificationHandler(NotificationHandler):
    """Webhook notification handler."""
    
    def __init__(self, webhook_urls: List[str] = None):
        super().__init__("Webhook", [NotificationChannel.WEBHOOK])
        self.webhook_urls = webhook_urls or []
    
    def handle(self, notification: Notification):
        """Handle webhook notification."""
        if not self.webhook_urls:
            return
        
        try:
            # Webhook sending implementation would go here
            # For now, just log the webhook notification
            self.logger.info(
                f"Webhook notification: {notification.title} - {notification.message}"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to send webhook notification: {e}")


class NotificationService:
    """Notification service for network connectivity tools."""
    
    def __init__(self):
        self.logger = get_network_logging_manager().get_tool_logger(
            'NotificationService'
        )
        
        # Threading
        self._lock = threading.RLock()
        self._notification_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._notification_queue = queue.Queue()
        
        # Storage
        self._notifications: Dict[str, Notification] = {}
        self._notification_history: List[Notification] = []
        self._max_history_size = 1000
        
        # Rules and handlers
        self._rules: Dict[str, NotificationRule] = {}
        self._handlers: Dict[str, NotificationHandler] = {}
        
        # Configuration
        self._config = {
            'max_notifications': 100,
            'default_expiry_hours': 24,
            'enable_sound': True,
            'enable_system_notifications': True,
            'notification_cooldown_seconds': 5
        }
        
        # Statistics
        self._stats = {
            'total_sent': 0,
            'sent_by_type': {},
            'sent_by_priority': {},
            'acknowledged_count': 0
        }
        
        # Initialize
        self._initialize()
    
    def _initialize(self):
        """Initialize the notification service."""
        try:
            # Create default handlers
            self._handlers['gui'] = GUINotificationHandler()
            self._handlers['log'] = LogNotificationHandler()
            self._handlers['sound'] = SoundNotificationHandler()
            self._handlers['system'] = SystemNotificationHandler()
            
            # Create default rules
            self._create_default_rules()
            
            # Start notification processing thread
            self._start_processing_thread()
            
            self.logger.info("Notification service initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize notification service: {e}")
            raise
    
    def _create_default_rules(self):
        """Create default notification rules."""
        # Error notification rule
        self.add_rule(
            name="error_notification",
            condition=lambda data: data.get('level') == 'ERROR',
            notification_template={
                'type': 'error',
                'priority': 3,
                'title': 'Network Error',
                'message': 'Error in {tool_name}: {message}',
                'source': '{tool_name}',
                'channels': ['gui', 'log']
            }
        )
        
        # Performance alert rule
        self.add_rule(
            name="performance_alert",
            condition=lambda data: (
                data.get('type') == 'performance' and
                data.get('threshold_exceeded', False)
            ),
            notification_template={
                'type': 'performance',
                'priority': 2,
                'title': 'Performance Alert',
                'message': 'Performance threshold exceeded: {metric} = {value}',
                'source': '{tool_name}',
                'channels': ['gui', 'log']
            }
        )
        
        # Security alert rule
        self.add_rule(
            name="security_alert",
            condition=lambda data: data.get('level') == 'SECURITY',
            notification_template={
                'type': 'security',
                'priority': 4,
                'title': 'Security Alert',
                'message': 'Security event: {message}',
                'source': '{tool_name}',
                'channels': ['gui', 'log', 'sound', 'system']
            }
        )
        
        # Configuration change rule
        self.add_rule(
            name="config_change",
            condition=lambda data: data.get('type') == 'config_updated',
            notification_template={
                'type': 'configuration',
                'priority': 1,
                'title': 'Configuration Updated',
                'message': 'Configuration updated: {updates}',
                'source': 'ConfigurationService',
                'channels': ['gui', 'log']
            }
        )
    
    def _start_processing_thread(self):
        """Start the notification processing thread."""
        self._stop_event.clear()
        self._notification_thread = threading.Thread(
            target=self._processing_loop,
            name="NotificationProcessor",
            daemon=True
        )
        self._notification_thread.start()
    
    def _processing_loop(self):
        """Main notification processing loop."""
        while not self._stop_event.is_set():
            try:
                # Process queued notifications
                while not self._notification_queue.empty():
                    try:
                        notification = self._notification_queue.get_nowait()
                        self._process_notification(notification)
                    except queue.Empty:
                        break
                
                # Clean up expired notifications
                self._cleanup_expired_notifications()
                
                # Sleep briefly to avoid busy waiting
                time.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"Error in notification processing loop: {e}")
    
    def _process_notification(self, notification: Notification):
        """Process a notification through all handlers."""
        with self._lock:
            try:
                # Store notification
                self._notifications[notification.id] = notification
                self._notification_history.append(notification)
                
                # Limit history size
                if len(self._notification_history) > self._max_history_size:
                    self._notification_history = self._notification_history[
                        -self._max_history_size:
                    ]
                
                # Send to handlers
                for handler in self._handlers.values():
                    if handler.can_handle(notification):
                        try:
                            handler.handle(notification)
                        except Exception as e:
                            self.logger.error(
                                f"Error in handler {handler.name}: {e}"
                            )
                
                # Update statistics
                self._update_stats(notification)
                
                self.logger.debug(f"Processed notification: {notification.id}")
                
            except Exception as e:
                self.logger.error(f"Failed to process notification: {e}")
    
    def _update_stats(self, notification: Notification):
        """Update notification statistics."""
        self._stats['total_sent'] += 1
        
        # Count by type
        type_key = notification.type.value
        self._stats['sent_by_type'][type_key] = (
            self._stats['sent_by_type'].get(type_key, 0) + 1
        )
        
        # Count by priority
        priority_key = notification.priority.name
        self._stats['sent_by_priority'][priority_key] = (
            self._stats['sent_by_priority'].get(priority_key, 0) + 1
        )
    
    def _cleanup_expired_notifications(self):
        """Clean up expired notifications."""
        with self._lock:
            now = datetime.now()
            expired_ids = []
            
            for notification_id, notification in self._notifications.items():
                if (notification.expires_at and 
                    now > notification.expires_at):
                    expired_ids.append(notification_id)
            
            for notification_id in expired_ids:
                del self._notifications[notification_id]
            
            if expired_ids:
                self.logger.debug(f"Cleaned up {len(expired_ids)} expired notifications")
    
    def send_notification(self, type: NotificationType, title: str, 
                         message: str, source: str = "NetworkConnectivity",
                         priority: NotificationPriority = NotificationPriority.NORMAL,
                         channels: List[NotificationChannel] = None,
                         data: Dict[str, Any] = None,
                         expires_in_hours: int = None) -> str:
        """Send a notification.
        
        Args:
            type: Notification type
            title: Notification title
            message: Notification message
            source: Source of the notification
            priority: Notification priority
            channels: Delivery channels
            data: Additional data
            expires_in_hours: Expiry time in hours
            
        Returns:
            Notification ID
        """
        try:
            # Generate notification ID
            notification_id = f"{source}_{int(time.time())}_{id(self)}"
            
            # Set default channels
            if channels is None:
                channels = [NotificationChannel.GUI, NotificationChannel.LOG]
            
            # Calculate expiry time
            expires_at = None
            if expires_in_hours:
                expires_at = datetime.now() + timedelta(hours=expires_in_hours)
            elif self._config['default_expiry_hours']:
                expires_at = datetime.now() + timedelta(
                    hours=self._config['default_expiry_hours']
                )
            
            # Create notification
            notification = Notification(
                id=notification_id,
                type=type,
                priority=priority,
                title=title,
                message=message,
                source=source,
                timestamp=datetime.now(),
                channels=channels,
                data=data or {},
                expires_at=expires_at
            )
            
            # Queue for processing
            self._notification_queue.put(notification)
            
            return notification_id
            
        except Exception as e:
            self.logger.error(f"Failed to send notification: {e}")
            return ""
    
    def acknowledge_notification(self, notification_id: str, 
                               acknowledged_by: str = None) -> bool:
        """Acknowledge a notification.
        
        Args:
            notification_id: Notification ID
            acknowledged_by: User who acknowledged
            
        Returns:
            True if acknowledged successfully
        """
        with self._lock:
            try:
                if notification_id in self._notifications:
                    notification = self._notifications[notification_id]
                    notification.acknowledged = True
                    notification.acknowledged_at = datetime.now()
                    notification.acknowledged_by = acknowledged_by
                    
                    self._stats['acknowledged_count'] += 1
                    
                    self.logger.debug(f"Acknowledged notification: {notification_id}")
                    return True
                else:
                    self.logger.warning(f"Notification not found: {notification_id}")
                    return False
                    
            except Exception as e:
                self.logger.error(f"Failed to acknowledge notification: {e}")
                return False
    
    def get_notifications(self, include_acknowledged: bool = False,
                         type_filter: NotificationType = None,
                         priority_filter: NotificationPriority = None) -> List[Notification]:
        """Get notifications with filtering.
        
        Args:
            include_acknowledged: Whether to include acknowledged notifications
            type_filter: Filter by notification type
            priority_filter: Filter by priority
            
        Returns:
            List of notifications
        """
        with self._lock:
            notifications = []
            
            for notification in self._notifications.values():
                # Filter acknowledged
                if not include_acknowledged and notification.acknowledged:
                    continue
                
                # Filter by type
                if type_filter and notification.type != type_filter:
                    continue
                
                # Filter by priority
                if priority_filter and notification.priority != priority_filter:
                    continue
                
                notifications.append(notification)
            
            # Sort by timestamp (newest first)
            notifications.sort(key=lambda n: n.timestamp, reverse=True)
            
            return notifications
    
    def add_rule(self, name: str, condition: Callable[[Dict[str, Any]], bool],
                notification_template: Dict[str, Any]):
        """Add a notification rule.
        
        Args:
            name: Rule name
            condition: Condition function
            notification_template: Notification template
        """
        with self._lock:
            rule = NotificationRule(name, condition, notification_template)
            self._rules[name] = rule
            self.logger.info(f"Added notification rule: {name}")
    
    def remove_rule(self, name: str):
        """Remove a notification rule.
        
        Args:
            name: Rule name
        """
        with self._lock:
            if name in self._rules:
                del self._rules[name]
                self.logger.info(f"Removed notification rule: {name}")
    
    def trigger_rules(self, event_data: Dict[str, Any]):
        """Trigger notification rules based on event data.
        
        Args:
            event_data: Event data to evaluate
        """
        for rule in self._rules.values():
            try:
                if rule.should_trigger(event_data):
                    notification = rule.create_notification(event_data)
                    self._notification_queue.put(notification)
                    
            except Exception as e:
                self.logger.error(f"Error in rule {rule.name}: {e}")
    
    def add_handler(self, name: str, handler: NotificationHandler):
        """Add a notification handler.
        
        Args:
            name: Handler name
            handler: Handler instance
        """
        with self._lock:
            self._handlers[name] = handler
            self.logger.info(f"Added notification handler: {name}")
    
    def remove_handler(self, name: str):
        """Remove a notification handler.
        
        Args:
            name: Handler name
        """
        with self._lock:
            if name in self._handlers:
                del self._handlers[name]
                self.logger.info(f"Removed notification handler: {name}")
    
    def get_gui_handler(self) -> Optional[GUINotificationHandler]:
        """Get the GUI notification handler.
        
        Returns:
            GUI handler instance or None
        """
        return self._handlers.get('gui')
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get notification statistics.
        
        Returns:
            Statistics dictionary
        """
        with self._lock:
            return {
                'total_notifications': len(self._notifications),
                'unacknowledged_notifications': len([
                    n for n in self._notifications.values() 
                    if not n.acknowledged
                ]),
                'total_sent': self._stats['total_sent'],
                'acknowledged_count': self._stats['acknowledged_count'],
                'sent_by_type': dict(self._stats['sent_by_type']),
                'sent_by_priority': dict(self._stats['sent_by_priority']),
                'active_rules': len(self._rules),
                'active_handlers': len(self._handlers)
            }
    
    def clear_notifications(self, acknowledged_only: bool = True):
        """Clear notifications.
        
        Args:
            acknowledged_only: Whether to clear only acknowledged notifications
        """
        with self._lock:
            if acknowledged_only:
                to_remove = [
                    nid for nid, notification in self._notifications.items()
                    if notification.acknowledged
                ]
                for nid in to_remove:
                    del self._notifications[nid]
                
                self.logger.info(f"Cleared {len(to_remove)} acknowledged notifications")
            else:
                count = len(self._notifications)
                self._notifications.clear()
                self.logger.info(f"Cleared all {count} notifications")
    
    def shutdown(self):
        """Shutdown the notification service."""
        with self._lock:
            # Stop processing thread
            self._stop_event.set()
            
            if self._notification_thread and self._notification_thread.is_alive():
                self._notification_thread.join(timeout=5.0)
            
            self.logger.info("Notification service shutdown complete")


# Global instance for easy access
_notification_service = None


def get_notification_service() -> NotificationService:
    """Get global notification service instance.
    
    Returns:
        NotificationService instance
    """
    global _notification_service
    
    if _notification_service is None:
        _notification_service = NotificationService()
    
    return _notification_service


# Convenience functions for sending notifications
def notify_info(title: str, message: str, source: str = "NetworkConnectivity",
               **kwargs):
    """Send info notification."""
    get_notification_service().send_notification(
        NotificationType.INFO, title, message, source, **kwargs
    )


def notify_warning(title: str, message: str, source: str = "NetworkConnectivity",
                  **kwargs):
    """Send warning notification."""
    get_notification_service().send_notification(
        NotificationType.WARNING, title, message, source, **kwargs
    )


def notify_error(title: str, message: str, source: str = "NetworkConnectivity",
                **kwargs):
    """Send error notification."""
    get_notification_service().send_notification(
        NotificationType.ERROR, title, message, source, **kwargs
    )


def notify_critical(title: str, message: str, source: str = "NetworkConnectivity",
                   **kwargs):
    """Send critical notification."""
    get_notification_service().send_notification(
        NotificationType.CRITICAL, title, message, source, **kwargs
    )


def notify_success(title: str, message: str, source: str = "NetworkConnectivity",
                  **kwargs):
    """Send success notification."""
    get_notification_service().send_notification(
        NotificationType.SUCCESS, title, message, source, **kwargs
    )