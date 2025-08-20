"""Advanced configuration validation system for network connectivity tools."""

import re
import ipaddress
from typing import Dict, Any, List, Optional, Union, Callable
from dataclasses import dataclass
from enum import Enum

from ..core.logging_integration import get_network_logging_manager


class ValidationSeverity(Enum):
    """Validation error severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationResult:
    """Result of a validation check."""
    path: str
    severity: ValidationSeverity
    message: str
    expected: Optional[Any] = None
    actual: Optional[Any] = None
    suggestion: Optional[str] = None


class ValidationRule:
    """Base class for validation rules."""
    
    def __init__(self, name: str, description: str, 
                 severity: ValidationSeverity = ValidationSeverity.ERROR):
        self.name = name
        self.description = description
        self.severity = severity
    
    def validate(self, value: Any, path: str = "") -> List[ValidationResult]:
        """Validate a value.
        
        Args:
            value: Value to validate
            path: Configuration path
            
        Returns:
            List of validation results
        """
        # Default implementation - subclasses should override for specific validation
        return []


class TypeValidationRule(ValidationRule):
    """Validates value types."""
    
    def __init__(self, expected_type: type, 
                 severity: ValidationSeverity = ValidationSeverity.ERROR):
        super().__init__(
            f"type_{expected_type.__name__}",
            f"Value must be of type {expected_type.__name__}",
            severity
        )
        self.expected_type = expected_type
    
    def validate(self, value: Any, path: str = "") -> List[ValidationResult]:
        if not isinstance(value, self.expected_type):
            return [ValidationResult(
                path=path,
                severity=self.severity,
                message=f"Expected {self.expected_type.__name__}, got {type(value).__name__}",
                expected=self.expected_type.__name__,
                actual=type(value).__name__,
                suggestion=f"Convert value to {self.expected_type.__name__}"
            )]
        return []


class RangeValidationRule(ValidationRule):
    """Validates numeric ranges."""
    
    def __init__(self, min_value: Union[int, float] = None, 
                 max_value: Union[int, float] = None,
                 severity: ValidationSeverity = ValidationSeverity.ERROR):
        self.min_value = min_value
        self.max_value = max_value
        
        desc_parts = []
        if min_value is not None:
            desc_parts.append(f"minimum {min_value}")
        if max_value is not None:
            desc_parts.append(f"maximum {max_value}")
        
        super().__init__(
            f"range_{min_value}_{max_value}",
            f"Value must be within range: {', '.join(desc_parts)}",
            severity
        )
    
    def validate(self, value: Any, path: str = "") -> List[ValidationResult]:
        if not isinstance(value, (int, float)):
            return []  # Type validation should catch this
        
        results = []
        
        if self.min_value is not None and value < self.min_value:
            results.append(ValidationResult(
                path=path,
                severity=self.severity,
                message=f"Value {value} is below minimum {self.min_value}",
                expected=f">= {self.min_value}",
                actual=value,
                suggestion=f"Use a value >= {self.min_value}"
            ))
        
        if self.max_value is not None and value > self.max_value:
            results.append(ValidationResult(
                path=path,
                severity=self.severity,
                message=f"Value {value} is above maximum {self.max_value}",
                expected=f"<= {self.max_value}",
                actual=value,
                suggestion=f"Use a value <= {self.max_value}"
            ))
        
        return results


class ChoiceValidationRule(ValidationRule):
    """Validates value is in allowed choices."""
    
    def __init__(self, choices: List[Any], 
                 severity: ValidationSeverity = ValidationSeverity.ERROR):
        self.choices = choices
        super().__init__(
            f"choice_{len(choices)}",
            f"Value must be one of: {', '.join(map(str, choices))}",
            severity
        )
    
    def validate(self, value: Any, path: str = "") -> List[ValidationResult]:
        if value not in self.choices:
            return [ValidationResult(
                path=path,
                severity=self.severity,
                message=f"Value '{value}' is not in allowed choices",
                expected=f"One of: {', '.join(map(str, self.choices))}",
                actual=value,
                suggestion=f"Use one of: {', '.join(map(str, self.choices[:3]))}{'...' if len(self.choices) > 3 else ''}"
            )]
        return []


class RegexValidationRule(ValidationRule):
    """Validates value matches regex pattern."""
    
    def __init__(self, pattern: str, description: str = None,
                 severity: ValidationSeverity = ValidationSeverity.ERROR):
        self.pattern = pattern
        self.regex = re.compile(pattern)
        super().__init__(
            f"regex_{pattern[:20]}",
            description or f"Value must match pattern: {pattern}",
            severity
        )
    
    def validate(self, value: Any, path: str = "") -> List[ValidationResult]:
        if not isinstance(value, str):
            return []  # Type validation should catch this
        
        if not self.regex.match(value):
            return [ValidationResult(
                path=path,
                severity=self.severity,
                message=f"Value '{value}' does not match required pattern",
                expected=f"Pattern: {self.pattern}",
                actual=value,
                suggestion="Check the format requirements"
            )]
        return []


class IPAddressValidationRule(ValidationRule):
    """Validates IP addresses."""
    
    def __init__(self, allow_ipv4: bool = True, allow_ipv6: bool = True,
                 severity: ValidationSeverity = ValidationSeverity.ERROR):
        self.allow_ipv4 = allow_ipv4
        self.allow_ipv6 = allow_ipv6
        
        types = []
        if allow_ipv4:
            types.append("IPv4")
        if allow_ipv6:
            types.append("IPv6")
        
        super().__init__(
            "ip_address",
            f"Value must be a valid {' or '.join(types)} address",
            severity
        )
    
    def validate(self, value: Any, path: str = "") -> List[ValidationResult]:
        if not isinstance(value, str):
            return []  # Type validation should catch this
        
        try:
            addr = ipaddress.ip_address(value)
            
            if isinstance(addr, ipaddress.IPv4Address) and not self.allow_ipv4:
                return [ValidationResult(
                    path=path,
                    severity=self.severity,
                    message="IPv4 addresses are not allowed",
                    expected="IPv6 address",
                    actual="IPv4 address",
                    suggestion="Use an IPv6 address instead"
                )]
            
            if isinstance(addr, ipaddress.IPv6Address) and not self.allow_ipv6:
                return [ValidationResult(
                    path=path,
                    severity=self.severity,
                    message="IPv6 addresses are not allowed",
                    expected="IPv4 address",
                    actual="IPv6 address",
                    suggestion="Use an IPv4 address instead"
                )]
            
            return []
            
        except ValueError:
            return [ValidationResult(
                path=path,
                severity=self.severity,
                message=f"'{value}' is not a valid IP address",
                expected="Valid IP address",
                actual=value,
                suggestion="Use format like '192.168.1.1' or '::1'"
            )]


class PortValidationRule(ValidationRule):
    """Validates port numbers."""
    
    def __init__(self, allow_well_known: bool = True, 
                 allow_registered: bool = True, allow_dynamic: bool = True,
                 severity: ValidationSeverity = ValidationSeverity.ERROR):
        self.allow_well_known = allow_well_known  # 1-1023
        self.allow_registered = allow_registered   # 1024-49151
        self.allow_dynamic = allow_dynamic         # 49152-65535
        
        super().__init__(
            "port_number",
            "Value must be a valid port number",
            severity
        )
    
    def validate(self, value: Any, path: str = "") -> List[ValidationResult]:
        if not isinstance(value, int):
            return []  # Type validation should catch this
        
        if not (1 <= value <= 65535):
            return [ValidationResult(
                path=path,
                severity=self.severity,
                message=f"Port {value} is outside valid range",
                expected="1-65535",
                actual=value,
                suggestion="Use a port number between 1 and 65535"
            )]
        
        results = []
        
        if 1 <= value <= 1023 and not self.allow_well_known:
            results.append(ValidationResult(
                path=path,
                severity=ValidationSeverity.WARNING,
                message=f"Port {value} is a well-known port",
                expected="Non-well-known port",
                actual=value,
                suggestion="Consider using a port > 1023"
            ))
        
        if 1024 <= value <= 49151 and not self.allow_registered:
            results.append(ValidationResult(
                path=path,
                severity=ValidationSeverity.WARNING,
                message=f"Port {value} is a registered port",
                expected="Non-registered port",
                actual=value,
                suggestion="Consider using a dynamic port (49152-65535)"
            ))
        
        if 49152 <= value <= 65535 and not self.allow_dynamic:
            results.append(ValidationResult(
                path=path,
                severity=ValidationSeverity.WARNING,
                message=f"Port {value} is a dynamic port",
                expected="Non-dynamic port",
                actual=value,
                suggestion="Consider using a registered port (1024-49151)"
            ))
        
        return results


class CustomValidationRule(ValidationRule):
    """Custom validation rule with user-defined function."""
    
    def __init__(self, name: str, description: str, 
                 validator_func: Callable[[Any], bool],
                 error_message: str = None,
                 severity: ValidationSeverity = ValidationSeverity.ERROR):
        super().__init__(name, description, severity)
        self.validator_func = validator_func
        self.error_message = error_message or f"Value failed {name} validation"
    
    def validate(self, value: Any, path: str = "") -> List[ValidationResult]:
        try:
            if not self.validator_func(value):
                return [ValidationResult(
                    path=path,
                    severity=self.severity,
                    message=self.error_message,
                    actual=value
                )]
            return []
        except Exception as e:
            return [ValidationResult(
                path=path,
                severity=ValidationSeverity.ERROR,
                message=f"Validation function error: {e}",
                actual=value
            )]


class ConfigurationValidator:
    """Advanced configuration validation system."""
    
    def __init__(self):
        self.logger = get_network_logging_manager().get_tool_logger(
            'ConfigValidator'
        )
        
        # Validation rules by configuration path
        self._rules: Dict[str, List[ValidationRule]] = {}
        
        # Setup default rules
        self._setup_default_rules()
    
    def _setup_default_rules(self):
        """Setup default validation rules for network connectivity configuration."""
        
        # General settings
        self.add_rule("general.default_timeout", [
            TypeValidationRule(int),
            RangeValidationRule(1000, 60000)
        ])
        
        self.add_rule("general.max_concurrent_operations", [
            TypeValidationRule(int),
            RangeValidationRule(1, 100)
        ])
        
        self.add_rule("general.log_level", [
            TypeValidationRule(str),
            ChoiceValidationRule(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        ])
        
        self.add_rule("general.results_retention_days", [
            TypeValidationRule(int),
            RangeValidationRule(1, 365)
        ])
        
        # Bandwidth monitor settings
        self.add_rule("bandwidth_monitor.monitoring_interval", [
            TypeValidationRule(int),
            RangeValidationRule(100, 10000)
        ])
        
        self.add_rule("bandwidth_monitor.alert_threshold_mbps", [
            TypeValidationRule((int, float)),
            RangeValidationRule(0.1, 10000.0)
        ])
        
        self.add_rule("bandwidth_monitor.data_retention_hours", [
            TypeValidationRule(int),
            RangeValidationRule(1, 8760)  # 1 year
        ])
        
        # WiFi analyzer settings
        self.add_rule("wifi_analyzer.scan_interval", [
            TypeValidationRule(int),
            RangeValidationRule(5000, 300000)  # 5 seconds to 5 minutes
        ])
        
        self.add_rule("wifi_analyzer.signal_interval", [
            TypeValidationRule(int),
            RangeValidationRule(500, 60000)  # 0.5 to 60 seconds
        ])
        
        self.add_rule("wifi_analyzer.weak_signal_threshold", [
            TypeValidationRule(int),
            RangeValidationRule(-100, -30)  # dBm range
        ])
        
        self.add_rule("wifi_analyzer.security_alert_level", [
            TypeValidationRule(str),
            ChoiceValidationRule(["low", "medium", "high"])
        ])
        
        # Port scanner settings
        self.add_rule("port_scanner.scan_timeout", [
            TypeValidationRule(int),
            RangeValidationRule(100, 30000)
        ])
        
        self.add_rule("port_scanner.max_threads", [
            TypeValidationRule(int),
            RangeValidationRule(1, 1000)
        ])
        
        self.add_rule("port_scanner.default_scan_type", [
            TypeValidationRule(str),
            ChoiceValidationRule(["tcp", "udp", "syn"])
        ])
        
        # LAN file transfer settings
        self.add_rule("lan_file_transfer.discovery_port", [
            TypeValidationRule(int),
            PortValidationRule(allow_well_known=False)
        ])
        
        self.add_rule("lan_file_transfer.transfer_port", [
            TypeValidationRule(int),
            PortValidationRule(allow_well_known=False)
        ])
        
        self.add_rule("lan_file_transfer.max_file_size_mb", [
            TypeValidationRule(int),
            RangeValidationRule(1, 10240)  # 1MB to 10GB
        ])
        
        # Security settings
        self.add_rule("security.security_level", [
            TypeValidationRule(str),
            ChoiceValidationRule(["strict", "moderate", "permissive"])
        ])
        
        self.add_rule("security.max_scan_rate", [
            TypeValidationRule(int),
            RangeValidationRule(1, 10000)
        ])
        
        # Performance settings
        self.add_rule("performance.max_memory_usage_mb", [
            TypeValidationRule(int),
            RangeValidationRule(64, 4096)
        ])
        
        self.add_rule("performance.max_cpu_usage_percent", [
            TypeValidationRule((int, float)),
            RangeValidationRule(1, 100)
        ])
        
        # Custom validation rules
        self.add_rule("general.enable_logging", [
            TypeValidationRule(bool)
        ])
        
        self.add_rule("general.auto_save_results", [
            TypeValidationRule(bool)
        ])
        
        # Complex validation rules
        self._add_complex_rules()
    
    def _add_complex_rules(self):
        """Add complex validation rules."""
        
        # Port list validation
        def validate_port_list(ports):
            if not isinstance(ports, list):
                return False
            return all(isinstance(p, int) and 1 <= p <= 65535 for p in ports)
        
        self.add_rule("port_scanner.common_ports", [
            CustomValidationRule(
                "port_list",
                "Must be a list of valid port numbers",
                validate_port_list,
                "All ports must be integers between 1 and 65535"
            )
        ])
        
        # File extension validation
        def validate_file_extensions(extensions):
            if not isinstance(extensions, list):
                return False
            return all(isinstance(ext, str) and ext.startswith('.') 
                      for ext in extensions)
        
        self.add_rule("lan_file_transfer.blocked_file_types", [
            CustomValidationRule(
                "file_extensions",
                "Must be a list of file extensions starting with '.'",
                validate_file_extensions,
                "File extensions must start with '.'"
            )
        ])
        
        # Bandwidth threshold validation
        def validate_bandwidth_threshold(threshold):
            if not isinstance(threshold, (int, float)):
                return False
            # Warn if threshold is unusually high or low
            return 0.1 <= threshold <= 10000
        
        self.add_rule("bandwidth_monitor.alert_threshold_mbps", [
            CustomValidationRule(
                "reasonable_bandwidth",
                "Bandwidth threshold should be reasonable",
                validate_bandwidth_threshold,
                "Bandwidth threshold seems unusually high or low",
                ValidationSeverity.WARNING
            )
        ])
    
    def add_rule(self, path: str, rules: List[ValidationRule]):
        """Add validation rules for a configuration path.
        
        Args:
            path: Configuration path (e.g., 'general.timeout')
            rules: List of validation rules
        """
        if path not in self._rules:
            self._rules[path] = []
        self._rules[path].extend(rules)
    
    def validate_configuration(self, config: Dict[str, Any], 
                             path_prefix: str = "") -> List[ValidationResult]:
        """Validate a configuration dictionary.
        
        Args:
            config: Configuration to validate
            path_prefix: Path prefix for nested validation
            
        Returns:
            List of validation results
        """
        results = []
        
        try:
            # Validate network_connectivity section if present
            if "network_connectivity" in config:
                nc_config = config["network_connectivity"]
                results.extend(
                    self._validate_section(nc_config, "network_connectivity")
                )
            elif not path_prefix:
                # If no network_connectivity section and no prefix, 
                # assume this is the network_connectivity section
                results.extend(self._validate_section(config, ""))
            
            # Perform cross-field validation
            results.extend(self._validate_cross_fields(config))
            
        except Exception as e:
            self.logger.error(f"Error during validation: {e}")
            results.append(ValidationResult(
                path="validation_error",
                severity=ValidationSeverity.CRITICAL,
                message=f"Validation process failed: {e}"
            ))
        
        return results
    
    def _validate_section(self, section: Dict[str, Any], 
                         section_path: str) -> List[ValidationResult]:
        """Validate a configuration section.
        
        Args:
            section: Configuration section
            section_path: Path to the section
            
        Returns:
            List of validation results
        """
        results = []
        
        for key, value in section.items():
            current_path = f"{section_path}.{key}" if section_path else key
            
            if isinstance(value, dict):
                # Recursively validate nested sections
                results.extend(self._validate_section(value, current_path))
            else:
                # Validate individual values
                results.extend(self._validate_value(value, current_path))
        
        return results
    
    def _validate_value(self, value: Any, path: str) -> List[ValidationResult]:
        """Validate an individual configuration value.
        
        Args:
            value: Value to validate
            path: Configuration path
            
        Returns:
            List of validation results
        """
        results = []
        
        # Check if we have rules for this path
        if path in self._rules:
            for rule in self._rules[path]:
                try:
                    rule_results = rule.validate(value, path)
                    results.extend(rule_results)
                except Exception as e:
                    self.logger.error(f"Error in validation rule {rule.name}: {e}")
                    results.append(ValidationResult(
                        path=path,
                        severity=ValidationSeverity.ERROR,
                        message=f"Validation rule error: {e}"
                    ))
        
        return results
    
    def _validate_cross_fields(self, config: Dict[str, Any]) -> List[ValidationResult]:
        """Validate relationships between different configuration fields.
        
        Args:
            config: Full configuration
            
        Returns:
            List of validation results
        """
        results = []
        
        try:
            nc_config = config.get("network_connectivity", config)
            
            # Validate port conflicts
            results.extend(self._validate_port_conflicts(nc_config))
            
            # Validate resource constraints
            results.extend(self._validate_resource_constraints(nc_config))
            
            # Validate logical consistency
            results.extend(self._validate_logical_consistency(nc_config))
            
        except Exception as e:
            self.logger.error(f"Error in cross-field validation: {e}")
        
        return results
    
    def _validate_port_conflicts(self, config: Dict[str, Any]) -> List[ValidationResult]:
        """Validate for port conflicts between different tools.
        
        Args:
            config: Network connectivity configuration
            
        Returns:
            List of validation results
        """
        results = []
        used_ports = {}
        
        # Check LAN file transfer ports
        lan_config = config.get("lan_file_transfer", {})
        discovery_port = lan_config.get("discovery_port")
        transfer_port = lan_config.get("transfer_port")
        
        if discovery_port:
            used_ports[discovery_port] = "lan_file_transfer.discovery_port"
        
        if transfer_port:
            if transfer_port in used_ports:
                results.append(ValidationResult(
                    path="lan_file_transfer.transfer_port",
                    severity=ValidationSeverity.ERROR,
                    message=f"Port {transfer_port} conflicts with {used_ports[transfer_port]}",
                    suggestion="Use different ports for different services"
                ))
            else:
                used_ports[transfer_port] = "lan_file_transfer.transfer_port"
        
        # Check if discovery and transfer ports are the same
        if discovery_port and transfer_port and discovery_port == transfer_port:
            results.append(ValidationResult(
                path="lan_file_transfer",
                severity=ValidationSeverity.ERROR,
                message="Discovery and transfer ports cannot be the same",
                suggestion="Use different ports for discovery and transfer"
            ))
        
        return results
    
    def _validate_resource_constraints(self, config: Dict[str, Any]) -> List[ValidationResult]:
        """Validate resource usage constraints.
        
        Args:
            config: Network connectivity configuration
            
        Returns:
            List of validation results
        """
        results = []
        
        # Check memory constraints
        perf_config = config.get("performance", {})
        max_memory = perf_config.get("max_memory_usage_mb", 512)
        
        # Check if thread counts are reasonable for memory limit
        port_scanner_config = config.get("port_scanner", {})
        max_threads = port_scanner_config.get("max_threads", 50)
        
        # Rough estimate: each thread might use ~1MB
        estimated_memory = max_threads * 1
        if estimated_memory > max_memory * 0.5:  # 50% of memory limit
            results.append(ValidationResult(
                path="port_scanner.max_threads",
                severity=ValidationSeverity.WARNING,
                message=f"High thread count ({max_threads}) may exceed memory limit",
                suggestion=f"Consider reducing threads or increasing memory limit"
            ))
        
        # Check concurrent operations vs performance settings
        general_config = config.get("general", {})
        max_concurrent = general_config.get("max_concurrent_operations", 10)
        max_cpu = perf_config.get("max_cpu_usage_percent", 50)
        
        if max_concurrent > 20 and max_cpu < 50:
            results.append(ValidationResult(
                path="general.max_concurrent_operations",
                severity=ValidationSeverity.WARNING,
                message="High concurrent operations with low CPU limit may cause performance issues",
                suggestion="Increase CPU limit or reduce concurrent operations"
            ))
        
        return results
    
    def _validate_logical_consistency(self, config: Dict[str, Any]) -> List[ValidationResult]:
        """Validate logical consistency between settings.
        
        Args:
            config: Network connectivity configuration
            
        Returns:
            List of validation results
        """
        results = []
        
        # Check bandwidth monitoring vs alert settings
        bw_config = config.get("bandwidth_monitor", {})
        enable_alerts = bw_config.get("enable_alerts", True)
        alert_threshold = bw_config.get("alert_threshold_mbps")
        
        if enable_alerts and not alert_threshold:
            results.append(ValidationResult(
                path="bandwidth_monitor.alert_threshold_mbps",
                severity=ValidationSeverity.WARNING,
                message="Alerts enabled but no threshold set",
                suggestion="Set an alert threshold or disable alerts"
            ))
        
        # Check WiFi analyzer security settings
        wifi_config = config.get("wifi_analyzer", {})
        enable_security = wifi_config.get("enable_security_analysis", True)
        security_level = wifi_config.get("security_alert_level", "medium")
        
        if not enable_security and security_level == "high":
            results.append(ValidationResult(
                path="wifi_analyzer.security_alert_level",
                severity=ValidationSeverity.INFO,
                message="High security alert level set but security analysis disabled",
                suggestion="Enable security analysis or lower alert level"
            ))
        
        # Check logging settings consistency
        general_config = config.get("general", {})
        enable_logging = general_config.get("enable_logging", True)
        log_level = general_config.get("log_level", "INFO")
        
        if not enable_logging and log_level == "DEBUG":
            results.append(ValidationResult(
                path="general.log_level",
                severity=ValidationSeverity.INFO,
                message="Debug logging level set but logging disabled",
                suggestion="Enable logging or change log level"
            ))
        
        return results
    
    def validate_value_at_path(self, config: Dict[str, Any], 
                              path: str) -> List[ValidationResult]:
        """Validate a specific value at a given path.
        
        Args:
            config: Configuration dictionary
            path: Dot-separated path to the value
            
        Returns:
            List of validation results
        """
        try:
            value = self._get_nested_value(config, path)
            return self._validate_value(value, path)
        except KeyError:
            return [ValidationResult(
                path=path,
                severity=ValidationSeverity.ERROR,
                message=f"Configuration path not found: {path}"
            )]
        except Exception as e:
            return [ValidationResult(
                path=path,
                severity=ValidationSeverity.ERROR,
                message=f"Error validating path: {e}"
            )]
    
    def _get_nested_value(self, config: Dict[str, Any], path: str) -> Any:
        """Get value from nested configuration using dot notation.
        
        Args:
            config: Configuration dictionary
            path: Dot-separated path
            
        Returns:
            Value at the path
            
        Raises:
            KeyError: If path is not found
        """
        keys = path.split('.')
        value = config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                raise KeyError(f"Path {path} not found")
        
        return value
    
    def get_validation_summary(self, results: List[ValidationResult]) -> Dict[str, Any]:
        """Get summary of validation results.
        
        Args:
            results: List of validation results
            
        Returns:
            Summary dictionary
        """
        summary = {
            "total_issues": len(results),
            "by_severity": {
                "info": 0,
                "warning": 0,
                "error": 0,
                "critical": 0
            },
            "paths_with_issues": set(),
            "most_common_issues": {},
            "is_valid": True
        }
        
        for result in results:
            severity = result.severity.value
            summary["by_severity"][severity] += 1
            summary["paths_with_issues"].add(result.path)
            
            # Count issue types
            issue_type = result.message.split(':')[0] if ':' in result.message else result.message
            summary["most_common_issues"][issue_type] = summary["most_common_issues"].get(issue_type, 0) + 1
            
            # Configuration is invalid if there are errors or critical issues
            if result.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL]:
                summary["is_valid"] = False
        
        summary["paths_with_issues"] = list(summary["paths_with_issues"])
        
        return summary


# Global instance for easy access
_config_validator = None


def get_config_validator() -> ConfigurationValidator:
    """Get global configuration validator instance.
    
    Returns:
        ConfigurationValidator instance
    """
    global _config_validator
    
    if _config_validator is None:
        _config_validator = ConfigurationValidator()
    
    return _config_validator