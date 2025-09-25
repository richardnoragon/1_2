"""Security validation utilities for network connectivity tools."""

import logging
import ipaddress
import re
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
from enum import Enum


class SecurityLevel(Enum):
    """Security validation levels."""

    STRICT = "strict"
    MODERATE = "moderate"
    PERMISSIVE = "permissive"


class ValidationResult(Enum):
    """Validation result types."""

    ALLOWED = "allowed"
    BLOCKED = "blocked"
    WARNING = "warning"


@dataclass
class SecurityRule:
    """Security validation rule."""

    rule_type: str
    pattern: str
    action: ValidationResult
    description: str
    enabled: bool = True


@dataclass
class ValidationResponse:
    """Security validation response."""

    result: ValidationResult
    rule_matched: Optional[str]
    message: str
    details: Dict[str, Any]


class SecurityValidator:
    """Security validation for network operations."""

    def __init__(self, security_level: SecurityLevel = SecurityLevel.MODERATE):
        """Initialize security validator.

        Args:
            security_level: Security validation level
        """
        self.security_level = security_level
        self.logger = logging.getLogger(
            "RFU.NetworkConnectivity.SecurityValidator"
        )

        # Default security rules
        self.rules: List[SecurityRule] = []
        self._initialize_default_rules()

        # Custom whitelist and blacklist
        self.whitelist_ips: Set[str] = set()
        self.blacklist_ips: Set[str] = set()
        self.whitelist_domains: Set[str] = set()
        self.blacklist_domains: Set[str] = set()

    def _initialize_default_rules(self):
        """Initialize default security rules based on security level."""
        if self.security_level == SecurityLevel.STRICT:
            self._add_strict_rules()
        elif self.security_level == SecurityLevel.MODERATE:
            self._add_moderate_rules()
        else:  # PERMISSIVE
            self._add_permissive_rules()

    def _add_strict_rules(self):
        """Add strict security rules."""
        self.rules.extend(
            [
                SecurityRule(
                    rule_type="ip_range",
                    pattern="127.0.0.0/8",
                    action=ValidationResult.BLOCKED,
                    description="Block localhost/loopback addresses",
                ),
                SecurityRule(
                    rule_type="ip_range",
                    pattern="10.0.0.0/8",
                    action=ValidationResult.WARNING,
                    description="Private network range - use with caution",
                ),
                SecurityRule(
                    rule_type="ip_range",
                    pattern="172.16.0.0/12",
                    action=ValidationResult.WARNING,
                    description="Private network range - use with caution",
                ),
                SecurityRule(
                    rule_type="ip_range",
                    pattern="192.168.0.0/16",
                    action=ValidationResult.WARNING,
                    description="Private network range - use with caution",
                ),
                SecurityRule(
                    rule_type="port_range",
                    pattern="1-1023",
                    action=ValidationResult.WARNING,
                    description="Well-known ports - may require privileges",
                ),
                SecurityRule(
                    rule_type="domain_pattern",
                    pattern=r".*\.local$",
                    action=ValidationResult.WARNING,
                    description="Local domain - may not be accessible externally",
                ),
            ]
        )

    def _add_moderate_rules(self):
        """Add moderate security rules."""
        self.rules.extend(
            [
                SecurityRule(
                    rule_type="ip_range",
                    pattern="127.0.0.0/8",
                    action=ValidationResult.WARNING,
                    description="Localhost/loopback addresses",
                ),
                SecurityRule(
                    rule_type="ip_range",
                    pattern="0.0.0.0/8",
                    action=ValidationResult.BLOCKED,
                    description="Invalid IP range",
                ),
                SecurityRule(
                    rule_type="ip_range",
                    pattern="224.0.0.0/4",
                    action=ValidationResult.WARNING,
                    description="Multicast address range",
                ),
            ]
        )

    def _add_permissive_rules(self):
        """Add permissive security rules."""
        self.rules.extend(
            [
                SecurityRule(
                    rule_type="ip_range",
                    pattern="0.0.0.0/8",
                    action=ValidationResult.BLOCKED,
                    description="Invalid IP range",
                )
            ]
        )

    def validate_ip_address(self, ip_address: str) -> ValidationResponse:
        """Validate an IP address.

        Args:
            ip_address: IP address to validate

        Returns:
            ValidationResponse with validation result
        """
        try:
            # Parse IP address
            ip = ipaddress.ip_address(ip_address)

            # Check blacklist first
            if ip_address in self.blacklist_ips:
                return ValidationResponse(
                    result=ValidationResult.BLOCKED,
                    rule_matched="blacklist",
                    message=f"IP {ip_address} is blacklisted",
                    details={"ip": ip_address, "type": "blacklist"},
                )

            # Check whitelist
            if ip_address in self.whitelist_ips:
                return ValidationResponse(
                    result=ValidationResult.ALLOWED,
                    rule_matched="whitelist",
                    message=f"IP {ip_address} is whitelisted",
                    details={"ip": ip_address, "type": "whitelist"},
                )

            # Check against rules
            for rule in self.rules:
                if not rule.enabled or rule.rule_type != "ip_range":
                    continue

                try:
                    network = ipaddress.ip_network(rule.pattern, strict=False)
                    if ip in network:
                        return ValidationResponse(
                            result=rule.action,
                            rule_matched=rule.rule_type,
                            message=f"{rule.description}: {ip_address}",
                            details={
                                "ip": ip_address,
                                "rule": rule.pattern,
                                "description": rule.description,
                            },
                        )
                except ValueError:
                    continue

            # Default allow
            return ValidationResponse(
                result=ValidationResult.ALLOWED,
                rule_matched=None,
                message=f"IP {ip_address} validation passed",
                details={"ip": ip_address},
            )

        except ValueError as e:
            return ValidationResponse(
                result=ValidationResult.BLOCKED,
                rule_matched="invalid_format",
                message=f"Invalid IP address format: {ip_address}",
                details={"ip": ip_address, "error": str(e)},
            )

    def validate_domain(self, domain: str) -> ValidationResponse:
        """Validate a domain name.

        Args:
            domain: Domain name to validate

        Returns:
            ValidationResponse with validation result
        """
        # Basic domain format validation
        if not self._is_valid_domain_format(domain):
            return ValidationResponse(
                result=ValidationResult.BLOCKED,
                rule_matched="invalid_format",
                message=f"Invalid domain format: {domain}",
                details={"domain": domain},
            )

        # Check blacklist
        if domain in self.blacklist_domains:
            return ValidationResponse(
                result=ValidationResult.BLOCKED,
                rule_matched="blacklist",
                message=f"Domain {domain} is blacklisted",
                details={"domain": domain, "type": "blacklist"},
            )

        # Check whitelist
        if domain in self.whitelist_domains:
            return ValidationResponse(
                result=ValidationResult.ALLOWED,
                rule_matched="whitelist",
                message=f"Domain {domain} is whitelisted",
                details={"domain": domain, "type": "whitelist"},
            )

        # Check against domain pattern rules
        for rule in self.rules:
            if not rule.enabled or rule.rule_type != "domain_pattern":
                continue

            try:
                if re.match(rule.pattern, domain, re.IGNORECASE):
                    return ValidationResponse(
                        result=rule.action,
                        rule_matched=rule.rule_type,
                        message=f"{rule.description}: {domain}",
                        details={
                            "domain": domain,
                            "rule": rule.pattern,
                            "description": rule.description,
                        },
                    )
            except re.error:
                continue

        # Default allow
        return ValidationResponse(
            result=ValidationResult.ALLOWED,
            rule_matched=None,
            message=f"Domain {domain} validation passed",
            details={"domain": domain},
        )

    def validate_port(self, port: int) -> ValidationResponse:
        """Validate a port number.

        Args:
            port: Port number to validate

        Returns:
            ValidationResponse with validation result
        """
        # Basic port range validation
        if not (1 <= port <= 65535):
            return ValidationResponse(
                result=ValidationResult.BLOCKED,
                rule_matched="invalid_range",
                message=f"Port {port} is outside valid range (1-65535)",
                details={"port": port},
            )

        # Check against port range rules
        for rule in self.rules:
            if not rule.enabled or rule.rule_type != "port_range":
                continue

            try:
                if "-" in rule.pattern:
                    start, end = map(int, rule.pattern.split("-"))
                    if start <= port <= end:
                        return ValidationResponse(
                            result=rule.action,
                            rule_matched=rule.rule_type,
                            message=f"{rule.description}: port {port}",
                            details={
                                "port": port,
                                "rule": rule.pattern,
                                "description": rule.description,
                            },
                        )
                else:
                    if port == int(rule.pattern):
                        return ValidationResponse(
                            result=rule.action,
                            rule_matched=rule.rule_type,
                            message=f"{rule.description}: port {port}",
                            details={
                                "port": port,
                                "rule": rule.pattern,
                                "description": rule.description,
                            },
                        )
            except ValueError:
                continue

        # Default allow
        return ValidationResponse(
            result=ValidationResult.ALLOWED,
            rule_matched=None,
            message=f"Port {port} validation passed",
            details={"port": port},
        )

    def validate_scan_target(
        self, target: str, ports: Optional[List[int]] = None
    ) -> ValidationResponse:
        """Validate a scan target (IP or domain) and ports.

        Args:
            target: Target IP address or domain
            ports: List of ports to scan (optional)

        Returns:
            ValidationResponse with validation result
        """
        # Validate target
        if self._is_ip_address(target):
            target_result = self.validate_ip_address(target)
        else:
            target_result = self.validate_domain(target)

        # If target is blocked, return immediately
        if target_result.result == ValidationResult.BLOCKED:
            return target_result

        # Validate ports if provided
        if ports:
            for port in ports:
                port_result = self.validate_port(port)
                if port_result.result == ValidationResult.BLOCKED:
                    return ValidationResponse(
                        result=ValidationResult.BLOCKED,
                        rule_matched=port_result.rule_matched,
                        message=(
                            f"Port validation failed: "
                            f"{port_result.message}"
                        ),
                        details={
                            "target": target,
                            "port": port,
                            "port_details": port_result.details,
                        },
                    )

        # Return target validation result
        return target_result

    def _is_valid_domain_format(self, domain: str) -> bool:
        """Check if domain has valid format.

        Args:
            domain: Domain to check

        Returns:
            True if domain format is valid
        """
        if not domain or len(domain) > 253:
            return False

        # Basic domain regex
        domain_pattern = re.compile(
            r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*"
            r"[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$"
        )

        return bool(domain_pattern.match(domain))

    def _is_ip_address(self, target: str) -> bool:
        """Check if target is an IP address.

        Args:
            target: Target to check

        Returns:
            True if target is an IP address
        """
        try:
            ipaddress.ip_address(target)
            return True
        except ValueError:
            return False

    def add_whitelist_ip(self, ip_address: str):
        """Add IP to whitelist.

        Args:
            ip_address: IP address to whitelist
        """
        self.whitelist_ips.add(ip_address)
        self.logger.info(f"Added IP to whitelist: {ip_address}")

    def add_blacklist_ip(self, ip_address: str):
        """Add IP to blacklist.

        Args:
            ip_address: IP address to blacklist
        """
        self.blacklist_ips.add(ip_address)
        self.logger.info(f"Added IP to blacklist: {ip_address}")

    def add_whitelist_domain(self, domain: str):
        """Add domain to whitelist.

        Args:
            domain: Domain to whitelist
        """
        self.whitelist_domains.add(domain.lower())
        self.logger.info(f"Added domain to whitelist: {domain}")

    def add_blacklist_domain(self, domain: str):
        """Add domain to blacklist.

        Args:
            domain: Domain to blacklist
        """
        self.blacklist_domains.add(domain.lower())
        self.logger.info(f"Added domain to blacklist: {domain}")

    def add_custom_rule(self, rule: SecurityRule):
        """Add custom security rule.

        Args:
            rule: Security rule to add
        """
        self.rules.append(rule)
        self.logger.info(f"Added custom security rule: {rule.description}")

    def remove_rule(self, rule_description: str) -> bool:
        """Remove security rule by description.

        Args:
            rule_description: Description of rule to remove

        Returns:
            True if rule was removed
        """
        for i, rule in enumerate(self.rules):
            if rule.description == rule_description:
                del self.rules[i]
                self.logger.info(f"Removed security rule: {rule_description}")
                return True
        return False

    def get_security_summary(self) -> Dict[str, Any]:
        """Get security configuration summary.

        Returns:
            Dictionary with security configuration details
        """
        return {
            "security_level": self.security_level.value,
            "total_rules": len(self.rules),
            "enabled_rules": len([r for r in self.rules if r.enabled]),
            "whitelist_ips": len(self.whitelist_ips),
            "blacklist_ips": len(self.blacklist_ips),
            "whitelist_domains": len(self.whitelist_domains),
            "blacklist_domains": len(self.blacklist_domains),
            "rule_types": list(set(r.rule_type for r in self.rules)),
        }
