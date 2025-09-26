"""
Core Error Handler Mock for Network Module Testing

This module provides a comprehensive mock implementation of core.error_handler
to enable real implementation testing of the Network Complex Module.

Priority: URGENT - Resolves dependency blocking for network security testing
"""

import logging
import traceback
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for classification."""
    NETWORK = "network"
    SECURITY = "security"
    CONFIGURATION = "configuration"
    VALIDATION = "validation"
    SYSTEM = "system"
    UNKNOWN = "unknown"


class MockErrorHandler:
    """Mock ErrorHandler for network module testing."""
    
    def __init__(self):
        """Initialize mock error handler."""
        self.errors = []
        self.error_count = 0
        self.logger = logging.getLogger('MockErrorHandler')
        self.enabled = True
        self.max_errors = 1000
        
        # Configure logging for error handler
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def handle_error(self, error: Exception, context: str = "", 
                    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                    category: ErrorCategory = ErrorCategory.UNKNOWN) -> bool:
        """
        Handle error with logging and tracking.
        
        Args:
            error: The error/exception to handle
            context: Context where error occurred
            severity: Error severity level
            category: Error category
            
        Returns:
            True if error handled successfully
        """
        try:
            if not self.enabled:
                return True
            
            # Create error record
            error_record = {
                'timestamp': datetime.now(),
                'error': str(error),
                'error_type': type(error).__name__,
                'context': context,
                'severity': (severity.value if isinstance(severity, 
                           ErrorSeverity) else str(severity)),
                'category': (category.value if isinstance(category, 
                           ErrorCategory) else str(category)),
                'traceback': (traceback.format_exc() if 
                            hasattr(error, '__traceback__') else None)
            }
            
            # Add to error list (with rotation)
            self.errors.append(error_record)
            if len(self.errors) > self.max_errors:
                self.errors.pop(0)
            
            self.error_count += 1
            
            # Log based on severity
            log_message = f"ERROR in {context}: {error}"
            if severity == ErrorSeverity.CRITICAL:
                self.logger.critical(log_message)
            elif severity == ErrorSeverity.HIGH:
                self.logger.error(log_message)
            elif severity == ErrorSeverity.MEDIUM:
                self.logger.warning(log_message)
            else:
                self.logger.info(log_message)
            
            return True
            
        except Exception as handler_error:
            # Error in error handler - use basic logging
            print(f"Error handler failed: {handler_error}")
            print(f"Original error: {error}")
            return False
    
    def handle_network_error(self, error: Exception, operation: str = "", 
                           target: str = "") -> bool:
        """
        Handle network-specific errors.
        
        Args:
            error: Network error
            operation: Network operation being performed
            target: Target host/address
            
        Returns:
            True if handled successfully
        """
        context = f"NetworkOperation:{operation}"
        if target:
            context += f" Target:{target}"
        
        return self.handle_error(
            error, 
            context, 
            ErrorSeverity.HIGH, 
            ErrorCategory.NETWORK
        )
    
    def handle_security_error(self, error: Exception, 
                            security_context: str = "") -> bool:
        """
        Handle security-related errors.
        
        Args:
            error: Security error
            security_context: Security operation context
            
        Returns:
            True if handled successfully
        """
        return self.handle_error(
            error,
            f"SecurityOperation:{security_context}",
            ErrorSeverity.CRITICAL,
            ErrorCategory.SECURITY
        )
    
    def handle_validation_error(self, error: Exception, 
                              validation_type: str = "") -> bool:
        """
        Handle validation errors.
        
        Args:
            error: Validation error
            validation_type: Type of validation
            
        Returns:
            True if handled successfully
        """
        return self.handle_error(
            error,
            f"Validation:{validation_type}",
            ErrorSeverity.MEDIUM,
            ErrorCategory.VALIDATION
        )
    
    def get_error_summary(self) -> Dict[str, Any]:
        """
        Get summary of handled errors.
        
        Returns:
            Error summary statistics
        """
        if not self.errors:
            return {
                'total_errors': 0,
                'by_severity': {},
                'by_category': {},
                'recent_errors': []
            }
        
        # Count by severity
        by_severity = {}
        by_category = {}
        
        for error in self.errors:
            severity = error.get('severity', 'unknown')
            category = error.get('category', 'unknown')
            
            by_severity[severity] = by_severity.get(severity, 0) + 1
            by_category[category] = by_category.get(category, 0) + 1
        
        # Get recent errors (last 10)
        recent_errors = (self.errors[-10:] if len(self.errors) > 10 
                        else self.errors)
        
        return {
            'total_errors': len(self.errors),
            'by_severity': by_severity,
            'by_category': by_category,
            'recent_errors': [
                {
                    'timestamp': err['timestamp'].isoformat(),
                    'error': err['error'],
                    'context': err['context'],
                    'severity': err['severity']
                }
                for err in recent_errors
            ]
        }
    
    def clear_errors(self) -> None:
        """Clear all stored errors."""
        self.errors.clear()
        self.error_count = 0
    
    def get_errors_by_category(self, 
                             category: ErrorCategory) -> List[Dict[str, Any]]:
        """
        Get errors by category.
        
        Args:
            category: Error category to filter by
            
        Returns:
            List of errors in category
        """
        category_str = (category.value if isinstance(category, ErrorCategory) 
                       else str(category))
        return [error for error in self.errors 
                if error.get('category') == category_str]
    
    def get_errors_by_severity(self, 
                             severity: ErrorSeverity) -> List[Dict[str, Any]]:
        """
        Get errors by severity.
        
        Args:
            severity: Error severity to filter by
            
        Returns:
            List of errors with specified severity
        """
        severity_str = (severity.value if isinstance(severity, ErrorSeverity) 
                       else str(severity))
        return [error for error in self.errors 
                if error.get('severity') == severity_str]
    
    def has_critical_errors(self) -> bool:
        """
        Check if any critical errors have occurred.
        
        Returns:
            True if critical errors exist
        """
        return any(error.get('severity') == ErrorSeverity.CRITICAL.value 
                  for error in self.errors)
    
    def enable(self) -> None:
        """Enable error handling."""
        self.enabled = True
    
    def disable(self) -> None:
        """Disable error handling."""
        self.enabled = False


# Global instance for use in mocking
error_handler = MockErrorHandler()


class ErrorHandler(MockErrorHandler):
    """Alias for MockErrorHandler to match real interface."""
    pass