"""
Comprehensive Unit Tests for SecurityValidator
=============================================

Test File: test_security_validator_2025-08-30.py
Target Module: security_validator.py
Generated: 2025-08-30
Framework: pytest
Coverage: All functions and methods with edge cases

Description:
    This module provides comprehensive unit tests for the SecurityValidator class
    from the network connectivity complex module. Tests cover all security validation
    functionality including IP address validation, domain validation, port validation,
    scan target validation, and security rule management.

Requirements:
    - pytest>=7.0.0
    - pytest-html>=3.1.0
    - pytest-json-report>=1.5.0
    - pytest-cov>=4.0.0
    - pytest-mock>=3.10.0
"""

import ipaddress
import json
import logging
import os
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from unittest.mock import MagicMock, Mock, patch

import pytest

# Add the source directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

try:
    from tools.network.network_connectivity_complex.core.security_validator import (
        SecurityLevel, SecurityRule, SecurityValidator, ValidationResponse,
        ValidationResult)
except ImportError as e:
    pytest.skip(f"Could not import security_validator module: {e}", allow_module_level=True)


class TestSecurityValidatorEnums:
    """Test the enum classes used by SecurityValidator."""
    
    def test_security_level_enum_values(self):
        """Test SecurityLevel enum has correct values."""
        assert SecurityLevel.STRICT.value == "strict"
        assert SecurityLevel.MODERATE.value == "moderate"
        assert SecurityLevel.PERMISSIVE.value == "permissive"
    
    def test_validation_result_enum_values(self):
        """Test ValidationResult enum has correct values."""
        assert ValidationResult.ALLOWED.value == "allowed"
        assert ValidationResult.BLOCKED.value == "blocked"
        assert ValidationResult.WARNING.value == "warning"


class TestSecurityRule:
    """Test the SecurityRule dataclass."""
    
    def test_security_rule_creation(self):
        """Test SecurityRule can be created with all parameters."""
        rule = SecurityRule(
            rule_type="ip_range",
            pattern="192.168.1.0/24",
            action=ValidationResult.WARNING,
            description="Test rule",
            enabled=True
        )
        
        assert rule.rule_type == "ip_range"
        assert rule.pattern == "192.168.1.0/24"
        assert rule.action == ValidationResult.WARNING
        assert rule.description == "Test rule"
        assert rule.enabled is True
    
    def test_security_rule_default_enabled(self):
        """Test SecurityRule has default enabled=True."""
        rule = SecurityRule(
            rule_type="port_range",
            pattern="80",
            action=ValidationResult.ALLOWED,
            description="HTTP port"
        )
        
        assert rule.enabled is True


class TestValidationResponse:
    """Test the ValidationResponse dataclass."""
    
    def test_validation_response_creation(self):
        """Test ValidationResponse can be created with all parameters."""
        response = ValidationResponse(
            result=ValidationResult.ALLOWED,
            rule_matched="test_rule",
            message="Test message",
            details={"key": "value"}
        )
        
        assert response.result == ValidationResult.ALLOWED
        assert response.rule_matched == "test_rule"
        assert response.message == "Test message"
        assert response.details == {"key": "value"}
    
    def test_validation_response_with_none_rule(self):
        """Test ValidationResponse with None rule_matched."""
        response = ValidationResponse(
            result=ValidationResult.BLOCKED,
            rule_matched=None,
            message="No rule matched",
            details={}
        )
        
        assert response.rule_matched is None


class TestSecurityValidatorInitialization:
    """Test SecurityValidator initialization and setup."""
    
    def test_init_default_security_level(self):
        """Test SecurityValidator initializes with default MODERATE level."""
        validator = SecurityValidator()
        assert validator.security_level == SecurityLevel.MODERATE
        assert isinstance(validator.rules, list)
        assert len(validator.rules) > 0
    
    def test_init_strict_security_level(self):
        """Test SecurityValidator initializes with STRICT level."""
        validator = SecurityValidator(SecurityLevel.STRICT)
        assert validator.security_level == SecurityLevel.STRICT
        # Strict mode should have more rules
        assert len(validator.rules) >= 6
    
    def test_init_permissive_security_level(self):
        """Test SecurityValidator initializes with PERMISSIVE level."""
        validator = SecurityValidator(SecurityLevel.PERMISSIVE)
        assert validator.security_level == SecurityLevel.PERMISSIVE
        # Permissive mode should have fewer rules
        assert len(validator.rules) >= 1
    
    def test_init_sets_empty_collections(self):
        """Test SecurityValidator initializes empty whitelist/blacklist sets."""
        validator = SecurityValidator()
        assert isinstance(validator.whitelist_ips, set)
        assert isinstance(validator.blacklist_ips, set)
        assert isinstance(validator.whitelist_domains, set)
        assert isinstance(validator.blacklist_domains, set)
        assert len(validator.whitelist_ips) == 0
        assert len(validator.blacklist_ips) == 0
        assert len(validator.whitelist_domains) == 0
        assert len(validator.blacklist_domains) == 0
    
    def test_logger_initialization(self):
        """Test logger is properly initialized."""
        validator = SecurityValidator()
        assert validator.logger is not None
        assert isinstance(validator.logger, logging.Logger)
        assert 'SecurityValidator' in validator.logger.name


class TestSecurityValidatorRuleInitialization:
    """Test the rule initialization methods."""
    
    def test_strict_rules_initialization(self):
        """Test strict security rules are properly initialized."""
        validator = SecurityValidator(SecurityLevel.STRICT)
        
        # Check for specific strict rules
        rule_patterns = [rule.pattern for rule in validator.rules]
        assert "127.0.0.0/8" in rule_patterns
        assert "10.0.0.0/8" in rule_patterns
        assert "172.16.0.0/12" in rule_patterns
        assert "192.168.0.0/16" in rule_patterns
        assert "1-1023" in rule_patterns
        
        # Check for domain pattern rule
        domain_rules = [rule for rule in validator.rules if rule.rule_type == "domain_pattern"]
        assert len(domain_rules) >= 1
    
    def test_moderate_rules_initialization(self):
        """Test moderate security rules are properly initialized."""
        validator = SecurityValidator(SecurityLevel.MODERATE)
        
        rule_patterns = [rule.pattern for rule in validator.rules]
        assert "127.0.0.0/8" in rule_patterns
        assert "0.0.0.0/8" in rule_patterns
        assert "224.0.0.0/4" in rule_patterns
    
    def test_permissive_rules_initialization(self):
        """Test permissive security rules are properly initialized."""
        validator = SecurityValidator(SecurityLevel.PERMISSIVE)
        
        rule_patterns = [rule.pattern for rule in validator.rules]
        assert "0.0.0.0/8" in rule_patterns
        # Permissive should have minimal rules


class TestIPAddressValidation:
    """Test IP address validation functionality."""
    
    def test_validate_valid_ipv4_address(self):
        """Test validation of valid IPv4 addresses."""
        validator = SecurityValidator()
        
        test_ips = ["8.8.8.8", "1.1.1.1", "208.67.222.222"]
        
        for ip in test_ips:
            result = validator.validate_ip_address(ip)
            assert isinstance(result, ValidationResponse)
            assert result.result in [ValidationResult.ALLOWED, ValidationResult.WARNING]
            assert result.details["ip"] == ip
    
    def test_validate_valid_ipv6_address(self):
        """Test validation of valid IPv6 addresses."""
        validator = SecurityValidator()
        
        test_ips = ["2001:db8::1", "::1", "fe80::1"]
        
        for ip in test_ips:
            result = validator.validate_ip_address(ip)
            assert isinstance(result, ValidationResponse)
            assert result.details["ip"] == ip
    
    def test_validate_invalid_ip_address(self):
        """Test validation of invalid IP addresses."""
        validator = SecurityValidator()
        
        invalid_ips = [
            "256.256.256.256",
            "192.168.1",
            "not.an.ip.address",
            "192.168.1.1.1",
            "",
            None
        ]
        
        for ip in invalid_ips:
            if ip is not None:
                result = validator.validate_ip_address(ip)
                assert result.result == ValidationResult.BLOCKED
                assert result.rule_matched == "invalid_format"
                assert "Invalid IP address format" in result.message
    
    def test_validate_localhost_addresses(self):
        """Test validation of localhost/loopback addresses."""
        validator = SecurityValidator(SecurityLevel.STRICT)
        
        localhost_ips = ["127.0.0.1", "127.0.0.2", "127.255.255.255"]
        
        for ip in localhost_ips:
            result = validator.validate_ip_address(ip)
            assert result.result == ValidationResult.BLOCKED
            assert "Block localhost/loopback addresses" in result.message
    
    def test_validate_private_network_addresses(self):
        """Test validation of private network addresses."""
        validator = SecurityValidator(SecurityLevel.STRICT)
        
        private_ips = [
            ("10.0.0.1", "10.0.0.0/8"),
            ("172.16.0.1", "172.16.0.0/12"),
            ("192.168.1.1", "192.168.0.0/16")
        ]
        
        for ip, network in private_ips:
            result = validator.validate_ip_address(ip)
            assert result.result == ValidationResult.WARNING
            assert "Private network range" in result.message
            assert result.details["rule"] == network
    
    def test_validate_blacklisted_ip(self):
        """Test validation of blacklisted IP addresses."""
        validator = SecurityValidator()
        validator.add_blacklist_ip("192.168.1.100")
        
        result = validator.validate_ip_address("192.168.1.100")
        assert result.result == ValidationResult.BLOCKED
        assert result.rule_matched == "blacklist"
        assert "is blacklisted" in result.message
        assert result.details["type"] == "blacklist"
    
    def test_validate_whitelisted_ip(self):
        """Test validation of whitelisted IP addresses."""
        validator = SecurityValidator()
        validator.add_whitelist_ip("192.168.1.200")
        
        result = validator.validate_ip_address("192.168.1.200")
        assert result.result == ValidationResult.ALLOWED
        assert result.rule_matched == "whitelist"
        assert "is whitelisted" in result.message
        assert result.details["type"] == "whitelist"
    
    def test_whitelist_overrides_rules(self):
        """Test that whitelist takes precedence over security rules."""
        validator = SecurityValidator(SecurityLevel.STRICT)
        # Add a localhost IP to whitelist (normally blocked in strict mode)
        validator.add_whitelist_ip("127.0.0.1")
        
        result = validator.validate_ip_address("127.0.0.1")
        assert result.result == ValidationResult.ALLOWED
        assert result.rule_matched == "whitelist"
    
    def test_blacklist_overrides_whitelist(self):
        """Test that blacklist takes precedence over whitelist."""
        validator = SecurityValidator()
        test_ip = "8.8.8.8"
        validator.add_whitelist_ip(test_ip)
        validator.add_blacklist_ip(test_ip)
        
        result = validator.validate_ip_address(test_ip)
        assert result.result == ValidationResult.BLOCKED
        assert result.rule_matched == "blacklist"


class TestDomainValidation:
    """Test domain name validation functionality."""
    
    def test_validate_valid_domains(self):
        """Test validation of valid domain names."""
        validator = SecurityValidator()
        
        valid_domains = [
            "google.com",
            "www.example.org",
            "sub.domain.test.co.uk",
            "example-site.com",
            "test123.domain.edu"
        ]
        
        for domain in valid_domains:
            result = validator.validate_domain(domain)
            assert isinstance(result, ValidationResponse)
            assert result.result in [ValidationResult.ALLOWED, ValidationResult.WARNING]
            assert result.details["domain"] == domain
    
    def test_validate_invalid_domain_formats(self):
        """Test validation of invalid domain formats."""
        validator = SecurityValidator()
        
        invalid_domains = [
            "",
            ".",
            ".com",
            "domain.",
            "domain..com",
            "domain with spaces.com",
            "a" * 254,  # Too long
            "domain_with_underscore.com"
        ]
        
        for domain in invalid_domains:
            result = validator.validate_domain(domain)
            assert result.result == ValidationResult.BLOCKED
            assert result.rule_matched == "invalid_format"
            assert "Invalid domain format" in result.message
    
    def test_validate_local_domains(self):
        """Test validation of .local domains in strict mode."""
        validator = SecurityValidator(SecurityLevel.STRICT)
        
        local_domains = ["computer.local", "printer.local", "test.local"]
        
        for domain in local_domains:
            result = validator.validate_domain(domain)
            assert result.result == ValidationResult.WARNING
            assert "Local domain" in result.message
    
    def test_validate_blacklisted_domain(self):
        """Test validation of blacklisted domains."""
        validator = SecurityValidator()
        validator.add_blacklist_domain("malicious.com")
        
        result = validator.validate_domain("malicious.com")
        assert result.result == ValidationResult.BLOCKED
        assert result.rule_matched == "blacklist"
        assert "is blacklisted" in result.message
    
    def test_validate_whitelisted_domain(self):
        """Test validation of whitelisted domains."""
        validator = SecurityValidator()
        validator.add_whitelist_domain("trusted.com")
        
        result = validator.validate_domain("trusted.com")
        assert result.result == ValidationResult.ALLOWED
        assert result.rule_matched == "whitelist"
        assert "is whitelisted" in result.message
    
    def test_domain_case_insensitive(self):
        """Test that domain validation is case insensitive."""
        validator = SecurityValidator()
        validator.add_blacklist_domain("EXAMPLE.COM")
        
        result = validator.validate_domain("example.com")
        assert result.result == ValidationResult.BLOCKED
        assert result.rule_matched == "blacklist"
    
    def test_domain_format_validation_helper(self):
        """Test the _is_valid_domain_format helper method."""
        validator = SecurityValidator()
        
        # Valid domains
        assert validator._is_valid_domain_format("example.com") is True
        assert validator._is_valid_domain_format("sub.example.com") is True
        assert validator._is_valid_domain_format("test-site.org") is True
        
        # Invalid domains
        assert validator._is_valid_domain_format("") is False
        assert validator._is_valid_domain_format(".com") is False
        assert validator._is_valid_domain_format("domain.") is False
        assert validator._is_valid_domain_format("a" * 254) is False


class TestPortValidation:
    """Test port number validation functionality."""
    
    def test_validate_valid_ports(self):
        """Test validation of valid port numbers."""
        validator = SecurityValidator()
        
        valid_ports = [1, 80, 443, 8080, 65535]
        
        for port in valid_ports:
            result = validator.validate_port(port)
            assert isinstance(result, ValidationResponse)
            assert result.result in [ValidationResult.ALLOWED, ValidationResult.WARNING]
            assert result.details["port"] == port
    
    def test_validate_invalid_port_ranges(self):
        """Test validation of invalid port numbers."""
        validator = SecurityValidator()
        
        invalid_ports = [0, -1, 65536, 100000]
        
        for port in invalid_ports:
            result = validator.validate_port(port)
            assert result.result == ValidationResult.BLOCKED
            assert result.rule_matched == "invalid_range"
            assert "outside valid range" in result.message
    
    def test_validate_well_known_ports_strict(self):
        """Test validation of well-known ports in strict mode."""
        validator = SecurityValidator(SecurityLevel.STRICT)
        
        well_known_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995]
        
        for port in well_known_ports:
            result = validator.validate_port(port)
            assert result.result == ValidationResult.WARNING
            assert "Well-known ports" in result.message
            assert result.details["rule"] == "1-1023"
    
    def test_validate_high_ports(self):
        """Test validation of high-numbered ports."""
        validator = SecurityValidator()
        
        high_ports = [8080, 9000, 32768, 49152, 65534]
        
        for port in high_ports:
            result = validator.validate_port(port)
            # These should be allowed in moderate/permissive modes
            assert result.result == ValidationResult.ALLOWED
    
    def test_port_range_rule_matching(self):
        """Test port range rule matching."""
        validator = SecurityValidator()
        # Add a custom port range rule
        custom_rule = SecurityRule(
            rule_type="port_range",
            pattern="8000-9000",
            action=ValidationResult.WARNING,
            description="Development port range"
        )
        validator.add_custom_rule(custom_rule)
        
        # Test port in range
        result = validator.validate_port(8080)
        assert result.result == ValidationResult.WARNING
        assert "Development port range" in result.message
        assert result.details["rule"] == "8000-9000"
        
        # Test port outside range
        result = validator.validate_port(9001)
        assert result.result == ValidationResult.ALLOWED
    
    def test_single_port_rule_matching(self):
        """Test single port rule matching."""
        validator = SecurityValidator()
        # Add a custom single port rule
        custom_rule = SecurityRule(
            rule_type="port_range",
            pattern="3389",
            action=ValidationResult.BLOCKED,
            description="Block RDP port"
        )
        validator.add_custom_rule(custom_rule)
        
        result = validator.validate_port(3389)
        assert result.result == ValidationResult.BLOCKED
        assert "Block RDP port" in result.message


class TestScanTargetValidation:
    """Test scan target validation functionality."""
    
    def test_validate_ip_scan_target(self):
        """Test validation of IP address scan targets."""
        validator = SecurityValidator()
        
        result = validator.validate_scan_target("8.8.8.8")
        assert isinstance(result, ValidationResponse)
        assert result.details["target"] == "8.8.8.8" or "ip" in result.details
    
    def test_validate_domain_scan_target(self):
        """Test validation of domain scan targets."""
        validator = SecurityValidator()
        
        result = validator.validate_scan_target("google.com")
        assert isinstance(result, ValidationResponse)
        assert result.details["domain"] == "google.com"
    
    def test_validate_scan_target_with_ports(self):
        """Test validation of scan targets with port lists."""
        validator = SecurityValidator()
        
        result = validator.validate_scan_target("example.com", [80, 443, 8080])
        assert isinstance(result, ValidationResponse)
        # Should validate both target and ports
    
    def test_validate_scan_target_blocked_ip(self):
        """Test validation of blocked IP scan targets."""
        validator = SecurityValidator()
        validator.add_blacklist_ip("192.168.1.100")
        
        result = validator.validate_scan_target("192.168.1.100", [80])
        assert result.result == ValidationResult.BLOCKED
        assert result.rule_matched == "blacklist"
    
    def test_validate_scan_target_with_blocked_port(self):
        """Test validation with blocked ports."""
        validator = SecurityValidator()
        # Add a rule to block port 22
        custom_rule = SecurityRule(
            rule_type="port_range",
            pattern="22",
            action=ValidationResult.BLOCKED,
            description="Block SSH"
        )
        validator.add_custom_rule(custom_rule)
        
        result = validator.validate_scan_target("example.com", [80, 22, 443])
        assert result.result == ValidationResult.BLOCKED
        assert result.details["port"] == 22
        assert "Block SSH" in result.message
    
    def test_is_ip_address_helper(self):
        """Test the _is_ip_address helper method."""
        validator = SecurityValidator()
        
        # Valid IPs
        assert validator._is_ip_address("192.168.1.1") is True
        assert validator._is_ip_address("2001:db8::1") is True
        assert validator._is_ip_address("127.0.0.1") is True
        
        # Domains/invalid
        assert validator._is_ip_address("google.com") is False
        assert validator._is_ip_address("not.an.ip") is False
        assert validator._is_ip_address("256.256.256.256") is False


class TestWhitelistBlacklistManagement:
    """Test whitelist and blacklist management methods."""
    
    def test_add_whitelist_ip(self):
        """Test adding IPs to whitelist."""
        validator = SecurityValidator()
        
        validator.add_whitelist_ip("192.168.1.1")
        assert "192.168.1.1" in validator.whitelist_ips
        
        # Test adding multiple IPs
        validator.add_whitelist_ip("10.0.0.1")
        assert "10.0.0.1" in validator.whitelist_ips
        assert len(validator.whitelist_ips) == 2
    
    def test_add_blacklist_ip(self):
        """Test adding IPs to blacklist."""
        validator = SecurityValidator()
        
        validator.add_blacklist_ip("malicious.ip.com")
        assert "malicious.ip.com" in validator.blacklist_ips
    
    def test_add_whitelist_domain(self):
        """Test adding domains to whitelist."""
        validator = SecurityValidator()
        
        validator.add_whitelist_domain("TRUSTED.COM")
        # Should be stored in lowercase
        assert "trusted.com" in validator.whitelist_domains
        assert "TRUSTED.COM" not in validator.whitelist_domains
    
    def test_add_blacklist_domain(self):
        """Test adding domains to blacklist."""
        validator = SecurityValidator()
        
        validator.add_blacklist_domain("MALICIOUS.COM")
        # Should be stored in lowercase
        assert "malicious.com" in validator.blacklist_domains
    
    @patch('logging.Logger.info')
    def test_whitelist_blacklist_logging(self, mock_logger):
        """Test that whitelist/blacklist operations are logged."""
        validator = SecurityValidator()
        
        validator.add_whitelist_ip("1.1.1.1")
        validator.add_blacklist_ip("2.2.2.2")
        validator.add_whitelist_domain("good.com")
        validator.add_blacklist_domain("bad.com")
        
        # Should have called logger.info 4 times
        assert mock_logger.call_count == 4


class TestCustomRuleManagement:
    """Test custom security rule management."""
    
    def test_add_custom_rule(self):
        """Test adding custom security rules."""
        validator = SecurityValidator()
        initial_count = len(validator.rules)
        
        custom_rule = SecurityRule(
            rule_type="custom",
            pattern="test",
            action=ValidationResult.WARNING,
            description="Custom test rule"
        )
        
        validator.add_custom_rule(custom_rule)
        assert len(validator.rules) == initial_count + 1
        assert custom_rule in validator.rules
    
    def test_remove_rule(self):
        """Test removing security rules by description."""
        validator = SecurityValidator()
        
        # Add a custom rule
        custom_rule = SecurityRule(
            rule_type="test",
            pattern="test",
            action=ValidationResult.BLOCKED,
            description="Test rule to remove"
        )
        validator.add_custom_rule(custom_rule)
        
        # Remove the rule
        removed = validator.remove_rule("Test rule to remove")
        assert removed is True
        
        # Verify it's gone
        descriptions = [rule.description for rule in validator.rules]
        assert "Test rule to remove" not in descriptions
    
    def test_remove_nonexistent_rule(self):
        """Test removing a rule that doesn't exist."""
        validator = SecurityValidator()
        
        removed = validator.remove_rule("Nonexistent rule")
        assert removed is False
    
    @patch('logging.Logger.info')
    def test_custom_rule_logging(self, mock_logger):
        """Test that custom rule operations are logged."""
        validator = SecurityValidator()
        
        custom_rule = SecurityRule(
            rule_type="test",
            pattern="test",
            action=ValidationResult.WARNING,
            description="Test rule"
        )
        
        validator.add_custom_rule(custom_rule)
        validator.remove_rule("Test rule")
        
        # Should have logged add and remove operations
        assert mock_logger.call_count >= 2


class TestSecuritySummary:
    """Test security configuration summary functionality."""
    
    def test_get_security_summary_structure(self):
        """Test that security summary has expected structure."""
        validator = SecurityValidator()
        summary = validator.get_security_summary()
        
        required_keys = [
            'security_level',
            'total_rules',
            'enabled_rules',
            'whitelist_ips',
            'blacklist_ips',
            'whitelist_domains',
            'blacklist_domains',
            'rule_types'
        ]
        
        for key in required_keys:
            assert key in summary
    
    def test_get_security_summary_values(self):
        """Test security summary values are correct."""
        validator = SecurityValidator(SecurityLevel.STRICT)
        
        # Add some whitelist/blacklist entries
        validator.add_whitelist_ip("1.1.1.1")
        validator.add_blacklist_ip("2.2.2.2")
        validator.add_whitelist_domain("good.com")
        validator.add_blacklist_domain("bad.com")
        
        summary = validator.get_security_summary()
        
        assert summary['security_level'] == "strict"
        assert summary['total_rules'] >= 6  # Strict mode has multiple default rules
        assert summary['enabled_rules'] <= summary['total_rules']
        assert summary['whitelist_ips'] == 1
        assert summary['blacklist_ips'] == 1
        assert summary['whitelist_domains'] == 1
        assert summary['blacklist_domains'] == 1
        assert isinstance(summary['rule_types'], list)
        assert len(summary['rule_types']) > 0
    
    def test_get_security_summary_rule_types(self):
        """Test that rule types are correctly identified."""
        validator = SecurityValidator(SecurityLevel.STRICT)
        summary = validator.get_security_summary()
        
        expected_types = ['ip_range', 'port_range', 'domain_pattern']
        for rule_type in expected_types:
            assert rule_type in summary['rule_types']
    
    def test_disabled_rules_count(self):
        """Test that disabled rules are counted correctly."""
        validator = SecurityValidator()
        
        # Disable a rule
        if validator.rules:
            validator.rules[0].enabled = False
        
        summary = validator.get_security_summary()
        assert summary['enabled_rules'] < summary['total_rules']


class TestEdgeCasesAndErrorHandling:
    """Test edge cases and error handling."""
    
    def test_empty_string_inputs(self):
        """Test handling of empty string inputs."""
        validator = SecurityValidator()
        
        # Empty IP
        result = validator.validate_ip_address("")
        assert result.result == ValidationResult.BLOCKED
        
        # Empty domain
        result = validator.validate_domain("")
        assert result.result == ValidationResult.BLOCKED
    
    def test_none_inputs(self):
        """Test handling of None inputs."""
        validator = SecurityValidator()
        
        # None should be handled gracefully
        try:
            result = validator.validate_ip_address(None)
            # If it doesn't crash, check the result
            assert result.result == ValidationResult.BLOCKED
        except (TypeError, AttributeError):
            # This is also acceptable behavior
            pass
    
    def test_invalid_rule_patterns(self):
        """Test handling of invalid rule patterns."""
        validator = SecurityValidator()
        
        # Add rule with invalid IP pattern
        invalid_rule = SecurityRule(
            rule_type="ip_range",
            pattern="invalid.pattern",
            action=ValidationResult.BLOCKED,
            description="Invalid rule"
        )
        validator.add_custom_rule(invalid_rule)
        
        # Should still work for valid IPs
        result = validator.validate_ip_address("8.8.8.8")
        assert isinstance(result, ValidationResponse)
    
    def test_invalid_regex_patterns(self):
        """Test handling of invalid regex patterns in domain rules."""
        validator = SecurityValidator()
        
        # Add rule with invalid regex
        invalid_rule = SecurityRule(
            rule_type="domain_pattern",
            pattern="[invalid regex",
            action=ValidationResult.BLOCKED,
            description="Invalid regex rule"
        )
        validator.add_custom_rule(invalid_rule)
        
        # Should still work for valid domains
        result = validator.validate_domain("example.com")
        assert isinstance(result, ValidationResponse)
    
    def test_large_whitelist_blacklist(self):
        """Test performance with large whitelist/blacklist."""
        validator = SecurityValidator()
        
        # Add many entries
        for i in range(100):
            validator.add_whitelist_ip(f"192.168.1.{i}")
            validator.add_blacklist_ip(f"10.0.0.{i}")
        
        # Should still work efficiently
        result = validator.validate_ip_address("192.168.1.50")
        assert result.result == ValidationResult.ALLOWED
        assert result.rule_matched == "whitelist"
    
    def test_unicode_domain_handling(self):
        """Test handling of unicode domain names."""
        validator = SecurityValidator()
        
        # Test unicode domain (should be invalid per current implementation)
        unicode_domain = "xn--n3h.com"  # IDN domain
        result = validator.validate_domain(unicode_domain)
        # Current implementation should handle this appropriately
        assert isinstance(result, ValidationResponse)


class TestSecurityLevelBehaviors:
    """Test different behaviors across security levels."""
    
    def test_localhost_behavior_across_levels(self):
        """Test localhost handling across different security levels."""
        test_ip = "127.0.0.1"
        
        # Strict: should block
        strict_validator = SecurityValidator(SecurityLevel.STRICT)
        result = strict_validator.validate_ip_address(test_ip)
        assert result.result == ValidationResult.BLOCKED
        
        # Moderate: should warn
        moderate_validator = SecurityValidator(SecurityLevel.MODERATE)
        result = moderate_validator.validate_ip_address(test_ip)
        assert result.result == ValidationResult.WARNING
        
        # Permissive: should allow
        permissive_validator = SecurityValidator(SecurityLevel.PERMISSIVE)
        result = permissive_validator.validate_ip_address(test_ip)
        assert result.result == ValidationResult.ALLOWED
    
    def test_private_network_behavior_across_levels(self):
        """Test private network handling across security levels."""
        test_ip = "192.168.1.1"
        
        # Strict: should warn
        strict_validator = SecurityValidator(SecurityLevel.STRICT)
        result = strict_validator.validate_ip_address(test_ip)
        assert result.result == ValidationResult.WARNING
        
        # Moderate/Permissive: should allow (no specific rules)
        moderate_validator = SecurityValidator(SecurityLevel.MODERATE)
        result = moderate_validator.validate_ip_address(test_ip)
        assert result.result == ValidationResult.ALLOWED
    
    def test_well_known_ports_behavior(self):
        """Test well-known port handling across security levels."""
        test_port = 80
        
        # Strict: should warn
        strict_validator = SecurityValidator(SecurityLevel.STRICT)
        result = strict_validator.validate_port(test_port)
        assert result.result == ValidationResult.WARNING
        
        # Moderate/Permissive: should allow
        moderate_validator = SecurityValidator(SecurityLevel.MODERATE)
        result = moderate_validator.validate_port(test_port)
        assert result.result == ValidationResult.ALLOWED


# Test fixtures and setup
@pytest.fixture
def validator_strict():
    """Fixture for strict security validator."""
    return SecurityValidator(SecurityLevel.STRICT)


@pytest.fixture
def validator_moderate():
    """Fixture for moderate security validator."""
    return SecurityValidator(SecurityLevel.MODERATE)


@pytest.fixture
def validator_permissive():
    """Fixture for permissive security validator."""
    return SecurityValidator(SecurityLevel.PERMISSIVE)


@pytest.fixture
def sample_security_rule():
    """Fixture for sample security rule."""
    return SecurityRule(
        rule_type="test_rule",
        pattern="test_pattern",
        action=ValidationResult.WARNING,
        description="Test security rule"
    )


@pytest.fixture
def temp_log_file():
    """Fixture for temporary log file."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
        yield f.name
    os.unlink(f.name)


# Performance and integration tests
class TestPerformanceAndIntegration:
    """Test performance and integration scenarios."""
    
    def test_bulk_ip_validation_performance(self):
        """Test performance of bulk IP validation."""
        validator = SecurityValidator()
        
        # Generate test IPs
        test_ips = [f"192.168.1.{i}" for i in range(1, 101)]
        
        # Time the validation
        import time
        start_time = time.time()
        
        results = []
        for ip in test_ips:
            result = validator.validate_ip_address(ip)
            results.append(result)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete in reasonable time (less than 1 second for 100 IPs)
        assert duration < 1.0
        assert len(results) == 100
        assert all(isinstance(r, ValidationResponse) for r in results)
    
    def test_complex_scan_validation_scenario(self):
        """Test complex scan validation scenario."""
        validator = SecurityValidator(SecurityLevel.STRICT)
        
        # Add mixed whitelist/blacklist
        validator.add_whitelist_ip("8.8.8.8")
        validator.add_blacklist_domain("malicious.com")
        
        # Test multiple targets with ports
        targets = [
            ("8.8.8.8", [53, 443]),  # Whitelisted IP
            ("malicious.com", [80]),  # Blacklisted domain
            ("example.com", [22, 80, 443]),  # Regular domain with privileged ports
        ]
        
        results = []
        for target, ports in targets:
            result = validator.validate_scan_target(target, ports)
            results.append((target, result))
        
        # Verify expected results
        assert len(results) == 3
        
        # Whitelisted IP should be allowed
        whitelisted_result = next(r for t, r in results if t == "8.8.8.8")
        assert whitelisted_result.result == ValidationResult.ALLOWED
        
        # Blacklisted domain should be blocked
        blacklisted_result = next(r for t, r in results if t == "malicious.com")
        assert blacklisted_result.result == ValidationResult.BLOCKED


# Test configuration and setup
def pytest_configure(config):
    """Configure pytest for security validator tests."""
    config.addinivalue_line(
        "markers", "security: mark test as security-related"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as performance-related"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers."""
    for item in items:
        # Add security marker to all tests
        item.add_marker(pytest.mark.security)
        
        # Add performance marker to performance tests
        if "performance" in item.name.lower():
            item.add_marker(pytest.mark.performance)
        
        # Add integration marker to integration tests
        if "integration" in item.name.lower() or "complex" in item.name.lower():
            item.add_marker(pytest.mark.integration)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])