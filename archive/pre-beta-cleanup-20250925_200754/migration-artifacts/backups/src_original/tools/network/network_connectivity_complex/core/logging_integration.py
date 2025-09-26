"""Logging integration for network connectivity tools with main RFU logging system."""

import logging
from typing import Any, Dict, Optional


# Create a simplified logging manager for network complex modules
# to avoid dependency on the main RFU core modules
class SimpleLogManager:
    """Simplified log manager for network complex modules."""
    
    def __init__(self):
        self.logger = logging.getLogger('NetworkConnectivity')
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get a logger instance."""
        return logging.getLogger(f'NetworkConnectivity.{name}')


# Use the simplified log manager
LogManager = SimpleLogManager()


class NetworkLoggingManager:
    """Manages logging integration for network connectivity tools."""
    
    def __init__(self):
        """Initialize network logging manager."""
        self.log_manager = LogManager()
        self.network_loggers: Dict[str, logging.Logger] = {}
        self._setup_network_logging()
    
    def _setup_network_logging(self):
        """Setup network-specific logging configuration."""
        # Configure network connectivity logging namespace
        self.main_logger = self.log_manager.get_logger('NetworkConnectivity')
        
        # Set up tool-specific loggers
        tools = [
            'BandwidthMonitor',
            'PortScanner', 
            'WiFiAnalyzer',
            'LANFileTransfer',
            'ConnectionManager',
            'SecurityValidator',
            'PerformanceAnalyzer',
            'PlatformNetwork'
        ]
        
        for tool in tools:
            logger_name = f'NetworkConnectivity.{tool}'
            logger = self.log_manager.get_logger(logger_name)
            self.network_loggers[tool] = logger
    
    def get_tool_logger(self, tool_name: str) -> logging.Logger:
        """Get logger for a specific network tool.
        
        Args:
            tool_name: Name of the network tool
            
        Returns:
            Logger instance for the tool
        """
        if tool_name in self.network_loggers:
            return self.network_loggers[tool_name]
        
        # Create new logger if not exists
        logger_name = f'NetworkConnectivity.{tool_name}'
        logger = self.log_manager.get_logger(logger_name)
        self.network_loggers[tool_name] = logger
        return logger
    
    def log_network_operation(
        self,
        tool_name: str,
        operation: str,
        level: str = 'INFO',
        details: Optional[Dict[str, Any]] = None,
        error: Optional[Exception] = None
    ):
        """Log a network operation with standardized format.
        
        Args:
            tool_name: Name of the network tool
            operation: Operation being performed
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            details: Additional operation details
            error: Exception if operation failed
        """
        logger = self.get_tool_logger(tool_name)
        
        # Format message
        message = f"{operation}"
        if details:
            detail_str = ", ".join([f"{k}={v}" for k, v in details.items()])
            message += f" ({detail_str})"
        
        # Log based on level
        log_level = getattr(logging, level.upper(), logging.INFO)
        
        if error:
            logger.log(log_level, f"{message} - Error: {error}", exc_info=True)
        else:
            logger.log(log_level, message)
    
    def log_network_alert(
        self,
        tool_name: str,
        alert_type: str,
        message: str,
        level: str = 'WARNING',
        details: Optional[Dict[str, Any]] = None
    ):
        """Log a network alert with standardized format.
        
        Args:
            tool_name: Name of the network tool
            alert_type: Type of alert
            message: Alert message
            level: Log level
            details: Additional alert details
        """
        logger = self.get_tool_logger(tool_name)
        
        # Format alert message
        alert_msg = f"ALERT [{alert_type}]: {message}"
        if details:
            detail_str = ", ".join([f"{k}={v}" for k, v in details.items()])
            alert_msg += f" ({detail_str})"
        
        log_level = getattr(logging, level.upper(), logging.WARNING)
        logger.log(log_level, alert_msg)
    
    def log_network_performance(
        self,
        tool_name: str,
        metric_name: str,
        value: float,
        unit: str = '',
        threshold: Optional[float] = None
    ):
        """Log network performance metrics.
        
        Args:
            tool_name: Name of the network tool
            metric_name: Name of the performance metric
            value: Metric value
            unit: Unit of measurement
            threshold: Performance threshold if applicable
        """
        logger = self.get_tool_logger(tool_name)
        
        message = f"PERFORMANCE [{metric_name}]: {value}"
        if unit:
            message += f" {unit}"
        
        if threshold is not None:
            if value > threshold:
                message += f" (ABOVE THRESHOLD: {threshold})"
                logger.warning(message)
            else:
                message += f" (within threshold: {threshold})"
                logger.debug(message)
        else:
            logger.debug(message)
    
    def log_network_security(
        self,
        tool_name: str,
        event_type: str,
        message: str,
        level: str = 'INFO',
        source_ip: Optional[str] = None,
        target_ip: Optional[str] = None
    ):
        """Log network security events.
        
        Args:
            tool_name: Name of the network tool
            event_type: Type of security event
            message: Security event message
            level: Log level
            source_ip: Source IP address if applicable
            target_ip: Target IP address if applicable
        """
        logger = self.get_tool_logger(tool_name)
        
        # Format security message
        security_msg = f"SECURITY [{event_type}]: {message}"
        
        if source_ip or target_ip:
            ip_info = []
            if source_ip:
                ip_info.append(f"src={source_ip}")
            if target_ip:
                ip_info.append(f"dst={target_ip}")
            security_msg += f" ({', '.join(ip_info)})"
        
        log_level = getattr(logging, level.upper(), logging.INFO)
        logger.log(log_level, security_msg)
    
    def configure_tool_logging(
        self,
        tool_name: str,
        log_level: str = 'INFO',
        enable_performance_logging: bool = True,
        enable_security_logging: bool = True
    ):
        """Configure logging settings for a specific tool.
        
        Args:
            tool_name: Name of the network tool
            log_level: Logging level for the tool
            enable_performance_logging: Whether to enable performance logging
            enable_security_logging: Whether to enable security logging
        """
        logger = self.get_tool_logger(tool_name)
        
        # Set log level
        level = getattr(logging, log_level.upper(), logging.INFO)
        logger.setLevel(level)
        
        # Store configuration for tool
        config = {
            'log_level': log_level,
            'performance_logging': enable_performance_logging,
            'security_logging': enable_security_logging
        }
        
        # Store in logger for later reference
        logger.tool_config = config
        
        self.log_network_operation(
            tool_name,
            f"Logging configured: level={log_level}, "
            f"performance={enable_performance_logging}, "
            f"security={enable_security_logging}"
        )
    
    def get_tool_log_config(self, tool_name: str) -> Dict[str, Any]:
        """Get logging configuration for a tool.
        
        Args:
            tool_name: Name of the network tool
            
        Returns:
            Dictionary with tool logging configuration
        """
        logger = self.get_tool_logger(tool_name)
        
        if hasattr(logger, 'tool_config'):
            return logger.tool_config
        
        # Return default configuration
        return {
            'log_level': 'INFO',
            'performance_logging': True,
            'security_logging': True
        }
    
    def cleanup_old_network_logs(self, max_age_days: int = 30):
        """Clean up old network connectivity logs.
        
        Args:
            max_age_days: Maximum age of logs to keep in days
        """
        try:
            self.log_manager.cleanup_old_logs(max_age_days)
            self.main_logger.info(f"Cleaned up network logs older than {max_age_days} days")
        except Exception as e:
            self.main_logger.error(f"Error cleaning up network logs: {e}")


# Global instance for easy access
_network_logging_manager = None


def get_network_logging_manager() -> NetworkLoggingManager:
    """Get global network logging manager instance.
    
    Returns:
        NetworkLoggingManager instance
    """
    global _network_logging_manager
    
    if _network_logging_manager is None:
        _network_logging_manager = NetworkLoggingManager()
    
    return _network_logging_manager


def get_network_logger(tool_name: str) -> logging.Logger:
    """Convenience function to get a network tool logger.
    
    Args:
        tool_name: Name of the network tool
        
    Returns:
        Logger instance for the tool
    """
    return get_network_logging_manager().get_tool_logger(tool_name)


def log_network_operation(
    tool_name: str,
    operation: str,
    level: str = 'INFO',
    details: Optional[Dict[str, Any]] = None,
    error: Optional[Exception] = None
):
    """Convenience function to log network operations.
    
    Args:
        tool_name: Name of the network tool
        operation: Operation being performed
        level: Log level
        details: Additional operation details
        error: Exception if operation failed
    """
    get_network_logging_manager().log_network_operation(
        tool_name, operation, level, details, error
    )


def log_network_alert(
    tool_name: str,
    alert_type: str,
    message: str,
    level: str = 'WARNING',
    details: Optional[Dict[str, Any]] = None
):
    """Convenience function to log network alerts.
    
    Args:
        tool_name: Name of the network tool
        alert_type: Type of alert
        message: Alert message
        level: Log level
        details: Additional alert details
    """
    get_network_logging_manager().log_network_alert(
        tool_name, alert_type, message, level, details
    )