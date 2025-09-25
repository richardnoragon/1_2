"""
Test Data Setup and Configuration for SecurityValidator Tests
===========================================================

Configuration File: conftest_security_validator_2025-08-30.py
Target: test_security_validator_2025-08-30.py
Generated: 2025-08-30

This module provides pytest fixtures, test data, and configuration
for comprehensive SecurityValidator unit testing.

Features:
- Mock data generation for IP addresses, domains, and ports
- Test fixtures for different security levels
- Setup and teardown methods for test isolation
- Custom assertions and utilities
"""

import ipaddress
import json
import logging
import os
import random
import string
import sys
import tempfile
from datetime import datetime
from typing import Any, Dict, Generator, List
from unittest.mock import MagicMock, Mock, patch

import pytest

# Add source directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

# Test configuration
TEST_CONFIG = {
    "log_level": logging.DEBUG,
    "timeout": 30,
    "mock_data_size": 100,
    "performance_iterations": 1000,
}


class TestDataGenerator:
    """Generate test data for SecurityValidator tests."""

    @staticmethod
    def generate_valid_ipv4_addresses(count: int = 50) -> List[str]:
        """Generate valid IPv4 addresses for testing."""
        addresses = []

        # Add common public DNS servers
        addresses.extend(
            [
                "8.8.8.8",
                "8.8.4.4",  # Google DNS
                "1.1.1.1",
                "1.0.0.1",  # Cloudflare DNS
                "208.67.222.222",
                "208.67.220.220",  # OpenDNS
                "9.9.9.9",
                "149.112.112.112",  # Quad9 DNS
            ]
        )

        # Generate random valid IPs
        while len(addresses) < count:
            # Avoid private ranges for this set
            first = random.choice(
                [
                    1,
                    2,
                    3,
                    4,
                    5,
                    6,
                    7,
                    8,
                    9,
                    11,
                    12,
                    13,
                    14,
                    15,
                    16,
                    17,
                    18,
                    19,
                    20,
                ]
            )
            second = random.randint(0, 255)
            third = random.randint(0, 255)
            fourth = random.randint(1, 254)

            ip = f"{first}.{second}.{third}.{fourth}"
            if ip not in addresses:
                addresses.append(ip)

        return addresses[:count]

    @staticmethod
    def generate_private_ipv4_addresses(count: int = 30) -> List[str]:
        """Generate private IPv4 addresses for testing."""
        addresses = []

        # 10.0.0.0/8 range
        for _ in range(count // 3):
            ip = f"10.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
            addresses.append(ip)

        # 172.16.0.0/12 range
        for _ in range(count // 3):
            second = random.randint(16, 31)
            ip = f"172.{second}.{random.randint(0, 255)}.{random.randint(1, 254)}"
            addresses.append(ip)

        # 192.168.0.0/16 range
        for _ in range(count - len(addresses)):
            ip = f"192.168.{random.randint(0, 255)}.{random.randint(1, 254)}"
            addresses.append(ip)

        return addresses

    @staticmethod
    def generate_invalid_ip_addresses(count: int = 20) -> List[str]:
        """Generate invalid IP addresses for testing."""
        invalid_ips = [
            "256.256.256.256",
            "192.168.1",
            "192.168.1.1.1",
            "not.an.ip.address",
            "192.168.-1.1",
            "192.168.1.256",
            "",
            "...",
            "192.168..1",
            "192.168.1.",
            ".192.168.1.1",
            "192 168 1 1",
            "192.168.1.1/24",
            "http://192.168.1.1",
            "999.999.999.999",
        ]

        # Generate more random invalid IPs
        while len(invalid_ips) < count:
            # Random invalid formats
            invalid_formats = [
                f"{random.randint(256, 999)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}",
                f"{random.randint(0, 255)}.{random.randint(256, 999)}.{random.randint(0, 255)}.{random.randint(0, 255)}",
                f"{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(256, 999)}.{random.randint(0, 255)}",
                f"{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(256, 999)}",
                f"{''.join(random.choices(string.ascii_lowercase, k=10))}.com",
            ]

            invalid_ip = random.choice(invalid_formats)
            if invalid_ip not in invalid_ips:
                invalid_ips.append(invalid_ip)

        return invalid_ips[:count]

    @staticmethod
    def generate_valid_domains(count: int = 50) -> List[str]:
        """Generate valid domain names for testing."""
        domains = []

        # Add common domains
        common_domains = [
            "google.com",
            "microsoft.com",
            "amazon.com",
            "facebook.com",
            "twitter.com",
            "github.com",
            "stackoverflow.com",
            "reddit.com",
            "wikipedia.org",
            "mozilla.org",
            "w3.org",
            "ietf.org",
            "example.com",
            "example.org",
            "example.net",
            "test.com",
        ]
        domains.extend(common_domains)

        # Generate random valid domains
        tlds = [".com", ".org", ".net", ".edu", ".gov", ".mil", ".int"]
        while len(domains) < count:
            length = random.randint(3, 15)
            domain_name = "".join(
                random.choices(
                    string.ascii_lowercase + string.digits, k=length
                )
            )
            tld = random.choice(tlds)
            domain = f"{domain_name}{tld}"

            if domain not in domains:
                domains.append(domain)

        return domains[:count]

    @staticmethod
    def generate_invalid_domains(count: int = 20) -> List[str]:
        """Generate invalid domain names for testing."""
        invalid_domains = [
            "",
            ".",
            ".com",
            "domain.",
            "domain..com",
            "domain with spaces.com",
            "-domain.com",
            "domain-.com",
            "domain._invalid.com",
            "domain.c",
            "a" * 254,  # Too long
            "xn--invalid-domain",
            "domain@invalid.com",
            "domain#invalid.com",
            "domain$invalid.com",
        ]

        # Generate more random invalid domains
        while len(invalid_domains) < count:
            invalid_chars = "!@#$%^&*()+=[]{}|\\:;\"'<>?/"
            invalid_formats = [
                f"domain{random.choice(invalid_chars)}.com",
                f".{random.choice(['com', 'org', 'net'])}",
                f"domain.{random.choice(invalid_chars)}",
                f"{''.join(random.choices(string.ascii_lowercase, k=80))}.com",  # Too long
                f"domain..{random.choice(['com', 'org', 'net'])}",
            ]

            invalid_domain = random.choice(invalid_formats)
            if invalid_domain not in invalid_domains:
                invalid_domains.append(invalid_domain)

        return invalid_domains[:count]

    @staticmethod
    def generate_port_numbers() -> Dict[str, List[int]]:
        """Generate various categories of port numbers."""
        return {
            "well_known": list(range(1, 1024)),
            "registered": [
                1433,
                1521,
                3389,
                5432,
                5984,
                6379,
                8080,
                8443,
                9200,
            ],
            "dynamic": [32768, 49152, 65000, 65534, 65535],
            "invalid": [0, -1, 65536, 100000, -100],
            "common_services": [
                21,
                22,
                23,
                25,
                53,
                80,
                110,
                143,
                443,
                993,
                995,
            ],
        }


class MockLogger:
    """Mock logger for testing."""

    def __init__(self):
        self.messages = []

    def info(self, msg):
        self.messages.append(("INFO", msg))

    def warning(self, msg):
        self.messages.append(("WARNING", msg))

    def error(self, msg):
        self.messages.append(("ERROR", msg))

    def debug(self, msg):
        self.messages.append(("DEBUG", msg))

    def get_messages(self, level=None):
        if level:
            return [msg for lvl, msg in self.messages if lvl == level]
        return self.messages

    def clear(self):
        self.messages.clear()


# Pytest fixtures
@pytest.fixture
def test_data_generator():
    """Fixture providing test data generator."""
    return TestDataGenerator()


@pytest.fixture
def valid_ipv4_addresses(test_data_generator):
    """Fixture providing valid IPv4 addresses."""
    return test_data_generator.generate_valid_ipv4_addresses()


@pytest.fixture
def private_ipv4_addresses(test_data_generator):
    """Fixture providing private IPv4 addresses."""
    return test_data_generator.generate_private_ipv4_addresses()


@pytest.fixture
def invalid_ip_addresses(test_data_generator):
    """Fixture providing invalid IP addresses."""
    return test_data_generator.generate_invalid_ip_addresses()


@pytest.fixture
def valid_domains(test_data_generator):
    """Fixture providing valid domain names."""
    return test_data_generator.generate_valid_domains()


@pytest.fixture
def invalid_domains(test_data_generator):
    """Fixture providing invalid domain names."""
    return test_data_generator.generate_invalid_domains()


@pytest.fixture
def port_numbers(test_data_generator):
    """Fixture providing categorized port numbers."""
    return test_data_generator.generate_port_numbers()


@pytest.fixture
def mock_logger():
    """Fixture providing mock logger."""
    return MockLogger()


@pytest.fixture
def temp_directory():
    """Fixture providing temporary directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def test_config():
    """Fixture providing test configuration."""
    return TEST_CONFIG.copy()


@pytest.fixture(autouse=True)
def setup_logging():
    """Setup logging for tests."""
    logging.basicConfig(
        level=TEST_CONFIG["log_level"],
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


@pytest.fixture
def security_validator_mock():
    """Fixture providing mocked SecurityValidator."""
    with patch(
        "utilities.network.network_connectivity_complex.core.security_validator.SecurityValidator"
    ) as mock:
        yield mock


@pytest.fixture
def ipaddress_mock():
    """Fixture providing mocked ipaddress module."""
    with patch("ipaddress.ip_address") as mock:
        yield mock


@pytest.fixture
def ipaddress_network_mock():
    """Fixture providing mocked ipaddress.ip_network."""
    with patch("ipaddress.ip_network") as mock:
        yield mock


@pytest.fixture(scope="session")
def test_session_data():
    """Session-scoped fixture for test data that doesn't change."""
    return {
        "timestamp": datetime.now().isoformat(),
        "test_id": f"security_validator_test_{random.randint(1000, 9999)}",
        "version": "1.0.0",
    }


# Custom assertions and utilities
def assert_validation_response(
    response, expected_result=None, expected_rule=None
):
    """Custom assertion for ValidationResponse objects."""
    from tools.network.network_connectivity_complex.core.security_validator import (
        ValidationResponse,
        ValidationResult,
    )

    assert isinstance(
        response, ValidationResponse
    ), "Response must be ValidationResponse instance"
    assert hasattr(response, "result"), "Response must have result attribute"
    assert hasattr(
        response, "rule_matched"
    ), "Response must have rule_matched attribute"
    assert hasattr(response, "message"), "Response must have message attribute"
    assert hasattr(response, "details"), "Response must have details attribute"

    if expected_result:
        assert (
            response.result == expected_result
        ), f"Expected result {expected_result}, got {response.result}"

    if expected_rule:
        assert (
            response.rule_matched == expected_rule
        ), f"Expected rule {expected_rule}, got {response.rule_matched}"


def assert_security_rule(rule, expected_type=None, expected_action=None):
    """Custom assertion for SecurityRule objects."""
    from tools.network.network_connectivity_complex.core.security_validator import (
        SecurityRule,
        ValidationResult,
    )

    assert hasattr(rule, "rule_type"), "Rule must have rule_type attribute"
    assert hasattr(rule, "pattern"), "Rule must have pattern attribute"
    assert hasattr(rule, "action"), "Rule must have action attribute"
    assert hasattr(rule, "description"), "Rule must have description attribute"
    assert hasattr(rule, "enabled"), "Rule must have enabled attribute"

    if expected_type:
        assert (
            rule.rule_type == expected_type
        ), f"Expected type {expected_type}, got {rule.rule_type}"

    if expected_action:
        assert (
            rule.action == expected_action
        ), f"Expected action {expected_action}, got {rule.action}"


# Test data cleanup
@pytest.fixture(autouse=True)
def cleanup_test_data():
    """Automatically cleanup test data after each test."""
    yield
    # Cleanup code here if needed
    pass


# Performance testing utilities
@pytest.fixture
def performance_timer():
    """Fixture for timing test performance."""
    import time

    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None

        def start(self):
            self.start_time = time.time()

        def stop(self):
            self.end_time = time.time()

        def elapsed(self):
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return 0

    return Timer()


# Error injection utilities
@pytest.fixture
def error_injector():
    """Fixture for injecting errors in tests."""

    class ErrorInjector:
        def __init__(self):
            self.active_patches = []

        def inject_import_error(self, module_name):
            """Inject ImportError for specified module."""

            def mock_import(name, *args, **kwargs):
                if name == module_name:
                    raise ImportError(f"Mock import error for {module_name}")
                return __import__(name, *args, **kwargs)

            patch_obj = patch("builtins.__import__", side_effect=mock_import)
            self.active_patches.append(patch_obj)
            return patch_obj.start()

        def inject_value_error(self, target, error_msg="Mock ValueError"):
            """Inject ValueError for specified target."""
            patch_obj = patch(target, side_effect=ValueError(error_msg))
            self.active_patches.append(patch_obj)
            return patch_obj.start()

        def cleanup(self):
            """Cleanup all active patches."""
            for patch_obj in self.active_patches:
                patch_obj.stop()
            self.active_patches.clear()

    injector = ErrorInjector()
    yield injector
    injector.cleanup()


# Test markers
pytest.mark.security = pytest.mark.security
pytest.mark.performance = pytest.mark.performance
pytest.mark.integration = pytest.mark.integration
pytest.mark.unit = pytest.mark.unit
pytest.mark.edge_case = pytest.mark.edge_case
